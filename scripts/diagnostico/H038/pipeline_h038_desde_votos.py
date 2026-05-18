#!/usr/bin/env python3
"""
pipeline_h038_desde_votos.py — Búsqueda reversa DESDE inicio_votos_indiv

Lógica:
  - Si hay votos detectados (inicio_votos_indiv != None, post-apertura):
    buscar dispositivo desde inicio_votos_indiv-1 hacia apertura_rel.
    El dispositivo de mayoría está justo antes de los votos individuales.
  - Si no hay votos: forward desde apertura_rel (comportamiento actual).

Correr sobre los 5702 fallos y comparar contra CSV productivo.

Ubicación: scripts/diagnostico/H038/
Correr:
  $env:PYTHONIOENCODING = "utf-8"
  python scripts/diagnostico/H038/pipeline_h038_desde_votos.py
"""

import sys
import csv
import re
from pathlib import Path
from collections import Counter

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from pipeline.parser import (
    RE_APERTURA,
    RE_FECHA_LINEA,
    RE_DICT_HDR,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    RE_280_CONSIDERANDO,
    RE_280_LIBRE,
    RE_ACORDADA_4_CONSIDERANDO,
    detectar_apertura_dispositivo,
    detectar_apertura_en_bloque,
    collect_firma_lines,
    parse_firma,
    classify_outcome,
    extraer_considerando,
)

CSV_PATH = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = _REPO_ROOT / "corpus"
OUTPUT_DIR = _REPO_ROOT / "output" / "diagnostico" / "H038"


def reconstruir_estructura(bloque):
    apertura_tipo, apertura_rel = detectar_apertura_en_bloque(bloque)
    lineas_dictamen = set()
    en_dictamen = False
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
        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            if inicio_votos_indiv is None:
                inicio_votos_indiv = k
            continue

    return apertura_rel, lineas_dictamen, inicio_votos_indiv


def extraer_por_ello_text(bloque, k):
    """Extrae el texto del dispositivo desde la línea k."""
    chunk = []
    for m2 in range(k, min(k + 6, len(bloque))):
        chunk.append(bloque[m2])
        if bloque[m2].strip().endswith("."):
            break
    return " ".join(chunk).strip()


def buscar_dispositivo_desde_votos(bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv):
    """
    Estrategia híbrida:
    - Con votos post-apertura: REVERSA desde inicio_votos_indiv hacia apertura_rel
    - Sin votos: FORWARD desde apertura_rel (= comportamiento actual)
    """
    # Calcular ventana como el parser
    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio = apertura_rel
    elif dictamen_end is not None:
        inicio = dictamen_end + 1
    else:
        inicio = 0

    votos_post_apertura = (
        inicio_votos_indiv is not None
        and (apertura_rel is None or inicio_votos_indiv > apertura_rel)
    )

    if votos_post_apertura:
        # ── REVERSA desde votos ──
        for k in range(inicio_votos_indiv - 1, inicio - 1, -1):
            if k in lineas_dictamen:
                continue
            stripped = bloque[k].strip()
            if not stripped:
                continue
            es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
            if es_disp:
                return k, tipo_disp, extraer_por_ello_text(bloque, k), "reversa_desde_votos"
        return None, None, "", "reversa_sin_match"
    else:
        # ── FORWARD (comportamiento actual) ──
        fin = len(bloque)
        for k in range(inicio, fin):
            if k in lineas_dictamen:
                continue
            stripped = bloque[k].strip()
            if not stripped:
                continue
            es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
            if es_disp:
                return k, tipo_disp, extraer_por_ello_text(bloque, k), "forward_sin_votos"
        return None, None, "", "forward_sin_match"


def main():
    print("Leyendo CSV productivo...")
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"  Total filas: {len(rows)}")

    fallos = [r for r in rows if r.get("tipo_entrada", "fallo") == "fallo"]
    print(f"  Fallos a procesar: {len(fallos)}")

    por_archivo = {}
    for r in fallos:
        por_archivo.setdefault(r["source_file"], []).append(r)

    cambios = []
    stats = Counter()
    metodo_stats = Counter()
    errores = []
    procesados = 0

    for source_file, casos in sorted(por_archivo.items()):
        archivo_path = CORPUS_DIR / source_file
        if not archivo_path.exists():
            errores.append(f"No encontrado: {archivo_path}")
            continue

        text = archivo_path.read_text(encoding="utf-8")
        lines = text.split("\n")

        for caso in casos:
            caso_id = caso["caso_id_canonico"]
            linea_inicio = int(caso["linea_inicio"])
            linea_fin_raw = caso.get("linea_fin_real", caso.get("linea_fin", ""))
            if linea_fin_raw and str(linea_fin_raw).strip():
                linea_fin = int(linea_fin_raw)
            else:
                linea_fin = len(lines) - 1

            li = max(0, linea_inicio)
            lf = min(len(lines) - 1, linea_fin)
            if li > lf:
                errores.append(f"{caso_id}: li > lf")
                continue
            bloque = lines[li:lf + 1]
            if not bloque:
                continue

            procesados += 1
            apertura_rel, lineas_dict, votos_ini = reconstruir_estructura(bloque)

            new_idx, new_tipo, new_pet, metodo = buscar_dispositivo_desde_votos(
                bloque, apertura_rel, lineas_dict, votos_ini
            )
            metodo_stats[metodo] += 1

            # Outcome
            if new_pet:
                new_cons = extraer_considerando(bloque, new_idx, lineas_dict)
                new_outcome = classify_outcome(new_pet, new_cons)
            else:
                new_cons = ""
                new_outcome = "sin_dispositivo"
            if new_outcome == "sin_dispositivo" and new_cons:
                if RE_280_CONSIDERANDO.search(new_cons) or RE_280_LIBRE.search(new_cons):
                    new_outcome = "inadmisible_280"
                elif RE_ACORDADA_4_CONSIDERANDO.search(new_cons):
                    new_outcome = "inadmisible_acordada_4"

            # Firma
            new_firma_raw = ""
            new_fp = {"jueces": [], "voting_pattern": "sin_firma", "desconocidos": []}
            if new_idx is not None:
                new_firma_raw = collect_firma_lines(bloque, new_idx + 1)
                if new_firma_raw:
                    new_fp = parse_firma(new_firma_raw)

            old_vp = caso["voting_pattern"]
            old_n = int(caso["n_jueces"])
            old_outcome = caso["outcome"]
            new_vp = new_fp["voting_pattern"]
            new_n = len(new_fp["jueces"])

            if old_vp == new_vp and old_n == new_n and old_outcome == new_outcome:
                stats["identico"] += 1
                continue

            if old_vp == "sin_firma" and new_vp != "sin_firma":
                tipo_cambio = "mejora_gano_firma"
            elif old_vp != "sin_firma" and new_vp == "sin_firma":
                tipo_cambio = "REGRESION_perdio_firma"
            elif old_vp != "sin_firma" and new_vp != "sin_firma" and old_n > new_n:
                tipo_cambio = "REGRESION_menos_jueces"
            elif old_vp != "sin_firma" and new_vp != "sin_firma" and old_n < new_n:
                tipo_cambio = "mejora_mas_jueces"
            elif old_outcome != new_outcome:
                tipo_cambio = "cambio_outcome"
            elif old_vp != new_vp:
                tipo_cambio = "cambio_vp"
            else:
                tipo_cambio = "cambio_n_jueces"

            stats[tipo_cambio] += 1
            cambios.append({
                "caso_id": caso_id,
                "tomo": caso["tomo"],
                "tipo_cambio": tipo_cambio,
                "metodo": metodo,
                "old_outcome": old_outcome,
                "new_outcome": new_outcome,
                "old_vp": old_vp,
                "new_vp": new_vp,
                "old_n": old_n,
                "new_n": new_n,
                "old_pet": caso["por_ello_text"][:60],
                "new_pet": new_pet[:60],
                "new_firma": new_firma_raw[:80],
            })

    # ── Output ────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "desde_votos_cambios.csv"
    if cambios:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cambios[0].keys())
            writer.writeheader()
            writer.writerows(cambios)

    resumen_path = OUTPUT_DIR / "desde_votos_resumen.txt"
    with open(resumen_path, "w", encoding="utf-8") as f:
        def w(s=""):
            print(s)
            f.write(s + "\n")

        w("=" * 70)
        w("H038 — Reversa desde inicio_votos_indiv, forward sin votos")
        w(f"Procesados: {procesados}  Errores: {len(errores)}")
        w("=" * 70)

        w(f"\n── Método usado ──")
        for k, v in metodo_stats.most_common():
            w(f"  {k}: {v}")

        w(f"\n── Resultado global ──")
        w(f"  Idénticos: {stats['identico']}")
        total_c = sum(v for k, v in stats.items() if k != "identico")
        w(f"  Con cambio: {total_c}")

        w(f"\n── Detalle ──")
        for k, v in stats.most_common():
            if k == "identico":
                continue
            marker = "  ⚠️" if "REGRESION" in k else "  "
            w(f"{marker} {k}: {v}")

        regs = [c for c in cambios if "REGRESION" in c["tipo_cambio"]]
        if regs:
            w(f"\n── ⚠️  REGRESIONES ({len(regs)}) ──")
            for r in regs[:20]:
                w(f"  {r['caso_id']}: {r['tipo_cambio']} ({r['metodo']})")
                w(f"    vp: {r['old_vp']}→{r['new_vp']}, n: {r['old_n']}→{r['new_n']}")
                w(f"    old: {r['old_pet']}")
                w(f"    new: {r['new_pet']}")
        else:
            w(f"\n  ✓ 0 regresiones")

        mejoras = [c for c in cambios if "mejora" in c["tipo_cambio"]]
        w(f"\n── Mejoras: {len(mejoras)} ──")
        for k, v in Counter(c["tipo_cambio"] for c in mejoras).most_common():
            w(f"  {k}: {v}")

    print(f"\nResumen: {resumen_path}")


if __name__ == "__main__":
    main()
