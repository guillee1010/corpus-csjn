"""
poc_b085.py — PoC de validación para B085 (Tier 3b).

Objetivo: verificar que el fix Tier 3b (búsqueda sin exclusión de
dictamen ni restricción de rango) rescata 7 sin_dispositivo sin
regresiones en los demás fallos.

Uso:
    python scripts/auditoria/poc_b085.py

Compara el parser actual (pre-fix) con el parser parcheado (post-fix).
Para eso, corre la lógica de detección de dispositivo dos veces:
una con la cascada Tier 1/2/3/4, otra agregando Tier 3b.

El script NO modifica ningún archivo — solo reporta diferencias.
"""

import csv
import re
import sys
from pathlib import Path
from collections import Counter

# ── Imports del parser ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from parser import (
    detectar_apertura_dispositivo,
    linea_es_firma_de_juez,
    zonificar_bloque,
    classify_outcome,
    _unhyphenate,
    extraer_considerando,
    RE_APERTURA,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    POR_ELLO_ARGUMENTAL,
)

# ── Config ────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent.parent
CASOS_CSV = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"

B085_TARGETS = {
    "331_p1013", "332_p2418", "334_p1033", "334_p109",
    "337_p166", "339_p662", "344_p1952",
}


def load_casos():
    """Cargar CSV y filtrar solo tipo_entrada='fallo'."""
    rows = []
    with open(CASOS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("tipo_entrada") == "fallo":
                rows.append(r)
    return rows


def load_bloque(source_file, linea_inicio, linea_fin):
    """Cargar bloque de líneas desde un archivo .md del corpus."""
    p = CORPUS_DIR / source_file
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        all_lines = f.readlines()
    start = int(linea_inicio) - 1
    end = int(linea_fin)
    return [l.rstrip("\n") for l in all_lines[start:end]]


def detect_dispositivo_baseline(bloque, zonas):
    """Cascada Tier 1/2/3/4 (SIN Tier 3b) — lógica actual del parser."""
    n = len(bloque)
    _ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
    lineas_excluir = {k for k, z in enumerate(zonas) if z not in _ZONAS_FALLO}
    lineas_dictamen = {k for k, z in enumerate(zonas) if z == "dictamen"}

    apertura_rel = None
    for k in range(n):
        if RE_APERTURA.match(bloque[k].strip()):
            apertura_rel = k
            break

    inicio_votos_indiv = None
    for k in range(n):
        if k in lineas_excluir:
            continue
        s = bloque[k].strip()
        if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
            if inicio_votos_indiv is None:
                inicio_votos_indiv = k

    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    elif dictamen_end is not None:
        inicio_busqueda = dictamen_end + 1
    else:
        inicio_busqueda = 0

    if (inicio_votos_indiv is not None
            and (apertura_rel is None or inicio_votos_indiv > apertura_rel)):
        fin_busqueda = inicio_votos_indiv
    else:
        fin_busqueda = n

    # --- Tier 1 ---
    por_ello_idx = None
    por_ello_text = ""
    _fb_idx = None
    _fb_text = ""
    for k in range(inicio_busqueda, fin_busqueda):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, _ = detectar_apertura_dispositivo(stripped)
        if es_disp:
            chunk = []
            for m2 in range(k, min(k + 6, n)):
                chunk.append(bloque[m2])
                if bloque[m2].strip().endswith("."):
                    break
            ct = " ".join(chunk).strip()
            if _fb_idx is None:
                _fb_idx = k
                _fb_text = ct
            if any(linea_es_firma_de_juez(bloque[j])
                   for j in range(k + 1, min(k + 41, n))):
                por_ello_idx = k
                por_ello_text = ct
                break
    if por_ello_idx is None and _fb_idx is not None:
        por_ello_idx = _fb_idx
        por_ello_text = _fb_text

    if por_ello_idx is not None:
        return por_ello_idx, por_ello_text, "T1"

    # --- Tier 2 (simplified — just check if it finds anything) ---
    _t2_pats = [
        re.compile(r"Por ello[,.]?\s", re.I),
        re.compile(r"Por lo expuesto\b", re.I),
        re.compile(r"Por las razones\b", re.I),
        re.compile(r"Por lo expresado\b", re.I),
        re.compile(r"Por las consideraciones\b", re.I),
        re.compile(r"Que[,]?\s+por\s+ello\b", re.I),
        re.compile(r"O[íi]dos?\s+(el|la|los|las)\b", re.I),
    ]
    for k in range(inicio_busqueda, fin_busqueda):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        for _t2_pat in _t2_pats:
            _t2_m = _t2_pat.search(stripped)
            if _t2_m and _t2_m.start() > 0:
                _t2_pre = stripped[:_t2_m.start()].rstrip()
                if not (_t2_pre.endswith(".") or _t2_pre.endswith(")")
                        or stripped.lstrip().startswith("Que")):
                    continue
                _t2_rest = stripped[_t2_m.end():].strip()
                _t2_fw = _t2_rest.split()[0].lower().rstrip(",;") if _t2_rest.split() else ""
                if _t2_fw in POR_ELLO_ARGUMENTAL:
                    continue
                if any(linea_es_firma_de_juez(bloque[j])
                       for j in range(k + 1, min(k + 41, n))):
                    chunk = []
                    for m2 in range(k, min(k + 6, n)):
                        chunk.append(bloque[m2])
                        if bloque[m2].strip().endswith("."):
                            break
                    return k, " ".join(chunk).strip(), "T2"

    # --- Tier 3 ---
    _t3_fb_idx = None
    _t3_fb_text = ""
    for k in range(inicio_busqueda, n):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, _ = detectar_apertura_dispositivo(stripped)
        if es_disp:
            chunk = []
            for m2 in range(k, min(k + 6, n)):
                chunk.append(bloque[m2])
                if bloque[m2].strip().endswith("."):
                    break
            ct = " ".join(chunk).strip()
            if _t3_fb_idx is None:
                _t3_fb_idx = k
                _t3_fb_text = ct
            if any(linea_es_firma_de_juez(bloque[j])
                   for j in range(k + 1, min(k + 41, n))):
                return k, ct, "T3"
    if _t3_fb_idx is not None:
        return _t3_fb_idx, _t3_fb_text, "T3fb"

    # --- Tier 4 ---
    _re_asi = re.compile(r"[Aa]sí se resuelve", re.I)
    for k in range(inicio_busqueda, n):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if _re_asi.search(stripped):
            if any(linea_es_firma_de_juez(bloque[j])
                   for j in range(k + 1, min(k + 41, n))):
                chunk = []
                for m2 in range(k, min(k + 6, n)):
                    chunk.append(bloque[m2])
                    if bloque[m2].strip().endswith("."):
                        break
                return k, " ".join(chunk).strip(), "T4"

    return None, "", "none"


def detect_dispositivo_with_t3b(bloque, zonas):
    """Cascada Tier 1/2/3/3b/4 — con el fix B085."""
    idx, text, tier = detect_dispositivo_baseline(bloque, zonas)
    if idx is not None:
        return idx, text, tier

    # --- Tier 3b (B085): sin exclusión dictamen, rango completo,
    #     firma obligatoria sin fallback ---
    for k in range(len(bloque)):
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, _ = detectar_apertura_dispositivo(stripped)
        if es_disp:
            chunk = []
            for m2 in range(k, min(k + 6, len(bloque))):
                chunk.append(bloque[m2])
                if bloque[m2].strip().endswith("."):
                    break
            ct = " ".join(chunk).strip()
            if any(linea_es_firma_de_juez(bloque[j])
                   for j in range(k + 1, min(k + 41, len(bloque)))):
                return k, ct, "T3b"

    return None, "", "none"


def main():
    casos = load_casos()
    print(f"Fallos cargados: {len(casos)}")

    mejorados = []
    regresiones = []
    errores = []
    n_procesados = 0

    for row in casos:
        caso_id = row["caso_id_canonico"]
        source = row.get("source_file", "")
        li = row.get("linea_inicio", "0")
        lf = row.get("linea_fin", "0")

        bloque = load_bloque(source, li, lf)
        if bloque is None:
            errores.append(caso_id)
            continue

        n_procesados += 1
        zonas, _ = zonificar_bloque(bloque)

        # Baseline (sin Tier 3b)
        base_idx, base_text, base_tier = detect_dispositivo_baseline(bloque, zonas)
        base_outcome = classify_outcome(base_text) if base_text else "sin_dispositivo"

        # Con Tier 3b
        fix_idx, fix_text, fix_tier = detect_dispositivo_with_t3b(bloque, zonas)
        fix_outcome = classify_outcome(fix_text) if fix_text else "sin_dispositivo"

        if base_idx != fix_idx:
            is_target = caso_id in B085_TARGETS
            if base_idx is None and fix_idx is not None:
                mejorados.append({
                    "caso_id": caso_id,
                    "target": is_target,
                    "tier": fix_tier,
                    "outcome": fix_outcome,
                    "idx": fix_idx,
                    "text": fix_text[:100],
                })
            else:
                regresiones.append({
                    "caso_id": caso_id,
                    "base_idx": base_idx,
                    "base_outcome": base_outcome,
                    "fix_idx": fix_idx,
                    "fix_outcome": fix_outcome,
                })

    print(f"Procesados: {n_procesados} | Errores carga: {len(errores)}")
    print(f"\n{'='*70}")
    print(f"MEJORADOS: {len(mejorados)}")
    for m in mejorados:
        tag = "★ B085" if m["target"] else "  nuevo"
        print(f"  {tag} {m['caso_id']:15s} [{m['tier']}] outcome={m['outcome']:20s} | {m['text'][:70]}")

    print(f"\nREGRESIONES: {len(regresiones)}")
    for r in regresiones:
        print(f"  !! {r['caso_id']:15s} base={r['base_outcome']} → fix={r['fix_outcome']}")

    # Resumen
    print(f"\n{'='*70}")
    n_target = sum(1 for m in mejorados if m["target"])
    n_extra = sum(1 for m in mejorados if not m["target"])
    print(f"B085 targets rescatados: {n_target}/7")
    print(f"Mejoras adicionales: {n_extra}")
    print(f"Regresiones: {len(regresiones)}")


if __name__ == "__main__":
    main()
