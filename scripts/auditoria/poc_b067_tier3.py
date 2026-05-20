"""
PoC B067 — Tier 3: retry sin techo cuando Tier 1+2 no encuentran nada
======================================================================
Sesión H044 · corpus-csjn

Fix puramente aditivo: si Tier 1 + Tier 2 (con techo de votos) no
encuentran dispositivo, repetir Tier 1 sin techo. Solo se activa
para casos que hoy producen sin_dispositivo.

Métricas:
  - Casos que pasan de sin_dispositivo a dispositivo detectado (mejoras)
  - Casos donde el dispositivo existente cambia (regresiones, debe ser 0)
  - Validación de los 17 TECHO_CORTA identificados

Uso:
  python poc_b067_tier3.py
  python poc_b067_tier3.py --random 500 --seed 42

Ubicación: scripts/auditoria/poc_b067_tier3.py
"""

import argparse
import csv
import random
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
for _c in [_SCRIPT_DIR.parent, _SCRIPT_DIR.parent.parent / "scripts",
           _SCRIPT_DIR / "scripts", _SCRIPT_DIR]:
    if (_c / "pipeline" / "parser.py").exists():
        sys.path.insert(0, str(_c))
        break

from pipeline.parser import (  # noqa: E402
    RE_APERTURA, RE_FECHA_LINEA, RE_CONSIDERANDO, RE_DICT_HDR,
    RE_VOTO_HDR, RE_DISID_HDR,
    detectar_apertura_dispositivo, detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion, detectar_fin_real,
    cargar_proximos_headers, cargar_localizados,
    proximo_header_despues_de, primer_token_de_caratula,
    linea_es_firma_de_juez, collect_firma_lines, parse_firma,
    POR_ELLO_ARGUMENTAL, refinar_inicio_por_titulo,
)

_REPO_ROOT = None
for _c in [_SCRIPT_DIR.parent.parent, _SCRIPT_DIR.parent, _SCRIPT_DIR]:
    if (_c / "corpus").exists() and (_c / "output").exists():
        _REPO_ROOT = _c
        break
if _REPO_ROOT is None:
    _REPO_ROOT = _SCRIPT_DIR

DEFAULT_CORPUS = _REPO_ROOT / "corpus"
DEFAULT_LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
DEFAULT_MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
DEFAULT_CASOS = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output" / "auditoria" / "poc_b067"

# Los 17 TECHO_CORTA conocidos
TECHO_CORTA = {
    "329_p2218", "329_p2827", "330_p399", "330_p3141", "330_p3801",
    "331_p1013", "332_p5", "332_p2237", "340_p204",
    "341_p424", "343_p300", "343_p1024", "343_p1758",
    "344_p575", "344_p757", "347_p1084", "347_p1353",
}


def procesar_fallo_b067(bloque, apertura_rel):
    """
    Replica parser completo para dispositivo + agrega Tier 3.
    Devuelve dict con resultado baseline y resultado B067.
    """
    # ── Loop: dictamen + votos narrow (idéntico a parser) ─────────────
    en_dictamen = False
    lineas_dictamen = set()
    inicio_votos_indiv = None

    for k, bl in enumerate(bloque):
        stripped = bl.strip()
        if not stripped:
            continue
        if RE_DICT_HDR.match(stripped):
            en_dictamen = True
            lineas_dictamen.add(k)
            continue
        elif en_dictamen:
            if RE_APERTURA.match(stripped):
                en_dictamen = False
            else:
                lineas_dictamen.add(k)
                if RE_FECHA_LINEA.match(stripped) and k > 5:
                    prev = bloque[k - 1].strip() if k > 0 else ""
                    if prev and len(prev) < 80:
                        en_dictamen = False
                continue
        if inicio_votos_indiv is None:
            if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
                inicio_votos_indiv = k

    # ── Dispositivo: Tier 1 con techo (idéntico a parser) ─────────────
    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    elif dictamen_end is not None:
        inicio_busqueda = dictamen_end + 1
    else:
        inicio_busqueda = 0

    if (inicio_votos_indiv is not None
            and (apertura_rel is None
                 or inicio_votos_indiv > (apertura_rel or 0))):
        fin_busqueda_con_techo = inicio_votos_indiv
    else:
        fin_busqueda_con_techo = len(bloque)

    def tier1(fin_busqueda):
        por_ello_idx = None
        por_ello_text = ""
        fb_idx = None
        fb_text = ""
        for k in range(inicio_busqueda, fin_busqueda):
            if k in lineas_dictamen:
                continue
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
                if fb_idx is None:
                    fb_idx = k
                    fb_text = ct
                if any(linea_es_firma_de_juez(bloque[j])
                       for j in range(k + 1, min(k + 41, len(bloque)))):
                    return (k, ct, "tier1_validado")
        if fb_idx is not None:
            return (fb_idx, fb_text, "tier1_fallback")
        return (None, "", None)

    def tier2(fin_busqueda):
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
                    _t2_fw = (_t2_rest.split()[0].lower().rstrip(",;")
                              if _t2_rest.split() else "")
                    if _t2_fw in POR_ELLO_ARGUMENTAL:
                        continue
                    if any(linea_es_firma_de_juez(bloque[j])
                           for j in range(k + 1, min(k + 41, len(bloque)))):
                        chunk = []
                        for m2 in range(k, min(k + 6, len(bloque))):
                            chunk.append(bloque[m2])
                            if bloque[m2].strip().endswith("."):
                                break
                        return (k, " ".join(chunk).strip(), "tier2")
        return (None, "", None)

    # ── Baseline: Tier 1 + Tier 2 con techo ───────────────────────────
    pe_idx_bl, pe_text_bl, pe_tier_bl = tier1(fin_busqueda_con_techo)
    if pe_idx_bl is None:
        pe_idx_bl, pe_text_bl, pe_tier_bl = tier2(fin_busqueda_con_techo)

    # ── B067: si baseline no encontró nada, Tier 3 (sin techo) ────────
    pe_idx_b067 = pe_idx_bl
    pe_text_b067 = pe_text_bl
    pe_tier_b067 = pe_tier_bl
    tier3_fired = False

    if pe_idx_bl is None:
        tier3_fired = True
        # Tier 3 = Tier 1 sin techo (solo validado, sin fallback)
        pe3, pt3, _ = tier1(len(bloque))
        if pe3 is not None:
            # Extra: verificar que tiene firma (B059)
            # tier1 ya lo hace internamente para "tier1_validado"
            pe_idx_b067 = pe3
            pe_text_b067 = pt3
            pe_tier_b067 = "tier3"

    # ── Firma (con el dispositivo que haya ganado) ────────────────────
    firma_bl = ""
    vp_bl = "sin_firma"
    if pe_idx_bl is not None:
        firma_bl = collect_firma_lines(bloque, pe_idx_bl + 1)
        if firma_bl:
            vp_bl = parse_firma(firma_bl)["voting_pattern"]

    firma_b067 = ""
    vp_b067 = "sin_firma"
    if pe_idx_b067 is not None:
        firma_b067 = collect_firma_lines(bloque, pe_idx_b067 + 1)
        if firma_b067:
            vp_b067 = parse_firma(firma_b067)["voting_pattern"]

    return {
        "pe_idx_bl": pe_idx_bl,
        "pe_tier_bl": pe_tier_bl,
        "pe_text_bl": pe_text_bl[:100] if pe_text_bl else "",
        "vp_bl": vp_bl,
        "pe_idx_b067": pe_idx_b067,
        "pe_tier_b067": pe_tier_b067,
        "pe_text_b067": pe_text_b067[:100] if pe_text_b067 else "",
        "vp_b067": vp_b067,
        "tier3_fired": tier3_fired,
        "inicio_votos_indiv": inicio_votos_indiv,
        "inicio_busqueda": inicio_busqueda,
        "fin_busqueda_con_techo": fin_busqueda_con_techo,
    }


def main():
    ap = argparse.ArgumentParser(description="PoC B067 — Tier 3")
    ap.add_argument("--random", type=int, default=None)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tomo", type=int, default=None)
    ap.add_argument("--corpus", type=str, default=str(DEFAULT_CORPUS))
    ap.add_argument("--localizados", type=str, default=str(DEFAULT_LOCALIZADOS))
    ap.add_argument("--mapa", type=str, default=str(DEFAULT_MAPA))
    ap.add_argument("--casos", type=str, default=str(DEFAULT_CASOS))
    ap.add_argument("--output", type=str, default=None)
    args = ap.parse_args()

    for label, p in [("corpus", args.corpus), ("localizados", args.localizados),
                     ("mapa", args.mapa)]:
        if not Path(p).exists():
            print(f"ERROR: no encontré '{label}' en `{p}`.", file=sys.stderr)
            sys.exit(2)

    print("Cargando datos...")
    filas_loc, _ = cargar_localizados(args.localizados)
    hpa = cargar_proximos_headers(args.mapa)

    baseline = {}
    if Path(args.casos).exists():
        with open(args.casos, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                baseline[row["caso_id_canonico"]] = row

    candidatos = filas_loc
    if args.tomo is not None:
        candidatos = [r for r in candidatos if int(r["tomo"]) == args.tomo]
    candidatos = [
        r for r in candidatos
        if baseline.get(r["caso_id_canonico"], {}).get("tipo_entrada", "fallo") == "fallo"
    ]

    if args.random is not None:
        rng = random.Random(args.seed)
        candidatos = rng.sample(candidatos, min(args.random, len(candidatos)))

    print(f"Procesando {len(candidatos)} fallos...")

    cat = {}
    for r in filas_loc:
        cat.setdefault(int(r["tomo"]), []).append(r)
    for t in cat:
        cat[t].sort(key=lambda r: int(r["pagina_inicio"]))
    sig_caso = {}
    ptk = {}
    for t, lst in cat.items():
        for i, c in enumerate(lst[:-1]):
            sig_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]
        for c in lst:
            ptk[c["caso_id_canonico"]] = primer_token_de_caratula(
                c.get("nombres_indice", ""))

    resultados = []
    errores = 0
    corpus_dir = Path(args.corpus)

    for fm in candidatos:
        cid = fm["caso_id_canonico"]
        tomo = int(fm["tomo"])
        li = int(fm["linea_inicio"])
        lf_raw = fm.get("linea_fin", "")
        ni = fm.get("nombres_indice", "")
        archivo = fm["archivo"]
        fp = corpus_dir / archivo
        if not fp.exists():
            errores += 1
            continue
        try:
            lines = fp.read_text(encoding="utf-8").split("\n")
            lf = int(lf_raw) if lf_raw.strip() else len(lines) - 1
            s = sig_caso.get(cid)
            pt = ptk.get(s, "") if s else ""
            ha = sorted(hpa.get((tomo, archivo), []))
            ph = proximo_header_despues_de(ha, lf)
            lfr, _, _ = detectar_fin_real(lines, li, lf, ph, pt)
            bloque = construir_bloque_desde_localizacion(lines, li, lfr)
            if not bloque:
                errores += 1
                continue
            off, _ = refinar_inicio_por_titulo(bloque, ni)
            if off > 0:
                bloque = bloque[off:]
            _, ap = detectar_apertura_en_bloque(bloque)

            r = procesar_fallo_b067(bloque, ap)
            r["caso_id_canonico"] = cid
            r["tomo"] = tomo
            r["n_lineas"] = len(bloque)
            r["es_techo_corta"] = cid in TECHO_CORTA

            bl = baseline.get(cid, {})
            r["bl_outcome"] = bl.get("outcome", "")
            r["bl_vp"] = bl.get("voting_pattern", "")
            r["bl_sin_firma"] = r["bl_vp"] == "sin_firma"

            resultados.append(r)
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"  ERROR {cid}: {e}", file=sys.stderr)

    n = len(resultados)
    print(f"\nProcesados: {n} | Errores: {errores}")
    print("=" * 70)

    # ── Paridad: donde baseline encontraba dispositivo, B067 no cambia ──
    regresiones = [r for r in resultados
                   if r["pe_idx_bl"] is not None
                   and r["pe_idx_b067"] != r["pe_idx_bl"]]
    print(f"\n── Paridad (regresiones = 0 esperado) ──")
    print(f"  Regresiones (dispositivo cambió): {len(regresiones)}")
    for r in regresiones[:5]:
        print(f"    {r['caso_id_canonico']}: bl={r['pe_idx_bl']} b067={r['pe_idx_b067']}")

    # ── Tier 3 activaciones ───────────────────────────────────────────────
    t3_fired = [r for r in resultados if r["tier3_fired"]]
    t3_found = [r for r in t3_fired if r["pe_idx_b067"] is not None]
    t3_nada = [r for r in t3_fired if r["pe_idx_b067"] is None]
    print(f"\n── Tier 3 ──")
    print(f"  Tier 3 se activó: {len(t3_fired)} casos")
    print(f"  Tier 3 encontró dispositivo: {len(t3_found)}")
    print(f"  Tier 3 no encontró nada: {len(t3_nada)}")

    # ── Mejoras: sin_dispositivo → dispositivo ────────────────────────────
    mejoras = [r for r in resultados
               if r["pe_idx_bl"] is None and r["pe_idx_b067"] is not None]
    print(f"\n══ RESULTADO CLAVE: Mejoras ══")
    print(f"  Casos que pasan de sin_dispositivo a dispositivo: {len(mejoras)}")

    # De esas mejoras, ¿cuántas también recuperan firma?
    mejoras_con_firma = [r for r in mejoras if r["vp_b067"] != "sin_firma"]
    print(f"  De esas, con firma recuperada: {len(mejoras_con_firma)}")
    print(f"  De esas, sin firma: {len(mejoras) - len(mejoras_con_firma)}")

    if mejoras:
        print(f"\n  Detalle de mejoras:")
        for r in sorted(mejoras, key=lambda x: (x["tomo"], x["caso_id_canonico"])):
            tc = " [TECHO_CORTA]" if r["es_techo_corta"] else ""
            print(f"    {r['caso_id_canonico']}: "
                  f"pe={r['pe_idx_b067']} tier={r['pe_tier_b067']} "
                  f"vp={r['vp_b067']}{tc}")
            print(f"      texto: {r['pe_text_b067'][:90]}")

    # ── Impacto en sin_firma ──────────────────────────────────────────────
    sf_antes = sum(1 for r in resultados if r["bl_sin_firma"])
    sf_despues = sum(1 for r in resultados
                     if r["vp_b067"] == "sin_firma"
                     and r["bl_sin_firma"])
    sf_recuperados = sf_antes - sf_despues
    # Casos nuevos sin_firma (regresión)
    sf_nuevos = sum(1 for r in resultados
                    if r["vp_b067"] == "sin_firma"
                    and not r["bl_sin_firma"])
    print(f"\n── Impacto en sin_firma ──")
    print(f"  sin_firma antes: {sf_antes}")
    print(f"  sin_firma recuperados por B067: {sf_recuperados}")
    print(f"  sin_firma nuevos (regresión): {sf_nuevos}")

    # ── CSV ────────────────────────────────────────────────────────────────
    if args.output:
        out_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DEFAULT_OUTPUT_DIR / f"poc_b067_{ts}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fns = [
        "caso_id_canonico", "tomo", "n_lineas", "es_techo_corta",
        "pe_idx_bl", "pe_tier_bl", "vp_bl", "bl_outcome",
        "pe_idx_b067", "pe_tier_b067", "vp_b067",
        "tier3_fired", "inicio_votos_indiv",
        "inicio_busqueda", "fin_busqueda_con_techo",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fns, extrasaction="ignore")
        w.writeheader()
        for r in resultados:
            w.writerow(r)
    print(f"\n[OK] CSV: {out_path}")


if __name__ == "__main__":
    main()
