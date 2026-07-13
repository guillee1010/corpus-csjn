#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_m55_quorum.py — Invariante de quórum M55 (read-only).

Regla (DEUDA M55, sellada H201): en tipo_entrada=fallo, n_jueces ∈ {0} ∪ [3, ∞).
Un fallo con n_jueces ∈ {1, 2} es jurídicamente imposible (art. 23 decreto-ley
1285/58: mayoría absoluta; mínimo de mínimos sobre las composiciones del corpus
= 3) → SIEMPRE defecto del pipeline (firma truncada B158, conjuez fuera de tabla
B153/B154/B154-bis, letrado contado B155, bleed, miss del colector).
n_jueces=0 queda FUERA del invariante (sin_firma legítimo, tablero propio).

Salida: CSV diffeable ordenado por caso_id_canonico = baseline del gate de
no-regresión (la población no puede crecer respecto del baseline sellado).
Subclase automática: voting_pattern=unanime ∧ n_jueces<3 (columna subclase_unanime).

Uso (PowerShell, desde la raíz del repo):
  python <ruta>\\check_m55_quorum.py `
    --casos output\\parser\\csjn_casos.csv `
    --out   <ruta>\\m55_pool.csv

Regla --out (skill H201): las corridas de regresión usan --out propio y
diffean contra el baseline sellado; nunca pisarlo.

read-only sobre los insumos; no toca el pipeline. v0.1 (H202).
"""

import argparse
import csv
import sys
from collections import Counter

__version__ = "0.1"

# Columnas que viajan al CSV de salida (subset de csjn_casos.csv, en este orden,
# + subclase_unanime calculada). Elegidas para adjudicar sin reabrir casos.csv.
COLS_SALIDA = [
    "caso_id_canonico", "tomo", "date", "n_jueces", "n_titulares",
    "voting_pattern", "jueces", "jueces_conocidos", "jueces_desconocidos",
    "posiciones", "outcome", "status_fin", "pista_fin", "source_file",
    "linea_inicio", "linea_fin_real",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Invariante de quórum M55 (read-only)")
    ap.add_argument("--casos", required=True, help="ruta a csjn_casos.csv")
    ap.add_argument("--out", required=True, help="CSV de salida (pool ordenado)")
    ap.add_argument("--esperar-filas", type=int, default=None,
                    help="candado opcional: abortar si el total de filas del CSV difiere")
    args = ap.parse_args()

    csv.field_size_limit(10 ** 7)  # campos largos (jueces/posiciones) no abortan

    with open(args.casos, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltantes = [c for c in COLS_SALIDA if c not in (rd.fieldnames or [])]
        if faltantes:
            print(f"[ABORT] columnas ausentes en {args.casos}: {faltantes}")
            return 2
        filas = list(rd)

    total = len(filas)
    if args.esperar_filas is not None and total != args.esperar_filas:
        print(f"[ABORT] filas={total}, esperadas {args.esperar_filas}")
        return 2

    fallos = [f for f in filas if f.get("tipo_entrada") == "fallo"]

    pool = []
    n_invalid = 0
    for f in fallos:
        raw = (f.get("n_jueces") or "").strip()
        try:
            nj = int(float(raw)) if raw else 0
        except ValueError:
            n_invalid += 1
            continue  # no adivinar: se reporta y queda fuera del pool
        if 0 < nj < 3:
            fila = {c: f.get(c, "") for c in COLS_SALIDA}
            fila["subclase_unanime"] = (
                "1" if (f.get("voting_pattern") == "unanime" and nj < 3) else "0"
            )
            pool.append(fila)

    pool.sort(key=lambda r: r["caso_id_canonico"])

    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=COLS_SALIDA + ["subclase_unanime"],
                            lineterminator="\n")  # LF determinístico (patrón H111)
        wr.writeheader()
        wr.writerows(pool)

    # ---- Resumen (medición de población) ----
    por_nj = Counter(r["n_jueces"] for r in pool)
    por_tomo = Counter(r["tomo"] for r in pool)
    subcl = sum(1 for r in pool if r["subclase_unanime"] == "1")
    print(f"check_m55_quorum v{__version__}")
    print(f"  filas casos.csv          : {total}")
    print(f"  tipo_entrada=fallo       : {len(fallos)}")
    print(f"  POOL 0<n_jueces<3        : {len(pool)}")
    print(f"    n_jueces=1             : {por_nj.get('1', 0)}")
    print(f"    n_jueces=2             : {por_nj.get('2', 0)}")
    print(f"  subclase unanime∧nj<3    : {subcl}")
    if n_invalid:
        print(f"  [WARN] n_jueces no numérico (fuera del pool): {n_invalid}")
    print(f"  por tomo: {dict(sorted(por_tomo.items()))}")
    print(f"  salida: {args.out} ({len(pool)} filas, orden caso_id_canonico)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
