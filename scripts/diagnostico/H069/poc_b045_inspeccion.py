"""
Inspección spot-check de CAMBIO_REVISAR del POC bidireccional.

Muestra ±5 líneas alrededor de k_back y k_fwd para verificar
si el forward es un voto real del caso actual o ruido.

Uso:
    python poc_b045_inspeccion.py
"""

import csv
import re
from pathlib import Path

ROOT       = Path(".")
CSV_CASOS  = ROOT / "output" / "parser" / "csjn_casos.csv"
CSV_MAPA   = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS_DIR = ROOT / "corpus"

# Casos a inspeccionar (elegidos por diversidad de vp y magnitud de cambio)
TARGETS = [
    # caso_id,       k_back, k_fwd  — datos del POC
    ("342_p1426",     5023,   5029),   # disidencia, delta=6 (mínimo)
    ("341_p878",       586,    732),   # segun_su_voto, delta=146
    ("344_p603",     24469,  25170),   # mixed, delta=701 (grande)
]

CONTEXT = 8  # líneas de contexto arriba/abajo


def mostrar_contexto(lines, centro, label, caso_id, lf, li, next_li):
    """Muestra ±CONTEXT líneas alrededor de centro."""
    n = len(lines)
    desde = max(0, centro - CONTEXT)
    hasta = min(n - 1, centro + CONTEXT)
    print(f"\n  ── {label} (línea {centro}) ──")
    for k in range(desde, hasta + 1):
        marker = ">>>" if k == centro else "   "
        # Annotate special lines
        annot = ""
        if k == lf:
            annot = "  ◄── linea_fin (catálogo)"
        if k == li:
            annot = "  ◄── linea_inicio"
        if next_li is not None and k == next_li:
            annot = "  ◄── next case linea_inicio"
        print(f"  {marker} {k:6d} │ {lines[k].rstrip()[:90]}{annot}")


def main():
    # Cargar CSV para metadata
    with open(CSV_CASOS, encoding="utf-8") as f:
        rows = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

    # Build next-case map
    by_file = {}
    for r in rows.values():
        if r["source_file"] and r["linea_inicio"]:
            by_file.setdefault(r["source_file"], []).append(r)
    for k in by_file:
        by_file[k].sort(key=lambda x: int(x["linea_inicio"]))

    # Cache de archivos
    cache = {}

    for caso_id, k_back, k_fwd in TARGETS:
        r = rows[caso_id]
        sf = r["source_file"]
        li = int(r["linea_inicio"])
        lf = int(r["linea_fin"])
        lfr = int(r["linea_fin_real"])
        vp = r["voting_pattern"]

        # Next case
        cases_in_file = by_file.get(sf, [])
        next_c = None
        for c in cases_in_file:
            if int(c["linea_inicio"]) > li:
                next_c = c
                break
        next_li = int(next_c["linea_inicio"]) if next_c else None
        next_id = next_c["caso_id_canonico"] if next_c else "?"

        if sf not in cache:
            path = CORPUS_DIR / sf
            cache[sf] = path.read_text(encoding="utf-8").split("\n")
        lines = cache[sf]

        print()
        print("=" * 100)
        print(f"  {caso_id}  │  vp={vp}  │  li={li}  lf={lf}  lfr_actual={lfr}")
        print(f"  archivo: {sf}")
        print(f"  next: {next_id} (li={next_li})")
        print(f"  firma_raw actual: {r['firma_raw'][:80]}")
        print(f"  case_name: {r['case_name_indice'][:80]}")
        print(f"  k_back={k_back} (ext={lfr-lf:+d})  │  k_fwd={k_fwd} (ext_new={k_fwd-lf:+d})")
        print("=" * 100)

        mostrar_contexto(lines, k_back, "BACKWARD (actual)", caso_id, lf, li, next_li)
        mostrar_contexto(lines, k_fwd, "FORWARD (bidireccional)", caso_id, lf, li, next_li)

        # También mostrar qué hay en linea_fin (catálogo) para orientar
        print(f"\n  ── linea_fin catálogo ({lf}) ──")
        desde_lf = max(0, lf - 3)
        hasta_lf = min(len(lines) - 1, lf + 3)
        for k in range(desde_lf, hasta_lf + 1):
            marker = ">>>" if k == lf else "   "
            print(f"  {marker} {k:6d} │ {lines[k].rstrip()[:90]}")

    print()


if __name__ == "__main__":
    main()
