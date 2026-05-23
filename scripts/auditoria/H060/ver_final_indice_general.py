"""
H060 — ¿Qué hay al final de cada INDICE GENERAL?

Muestra las últimas 15 líneas del bloque desde INDICE GENERAL hasta EOF
para cada archivo. Objetivo: ver qué se pierde/gana con cualquier
lógica de truncado, sin asumir nada.

Correr: python scripts/auditoria/H060/ver_final_indice_general.py
"""
import re
import sys
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
while REPO_ROOT != REPO_ROOT.parent:
    if (REPO_ROOT / "corpus").is_dir():
        break
    REPO_ROOT = REPO_ROOT.parent

CORPUS = REPO_ROOT / "corpus"
CSV = REPO_ROOT / "output" / "parser" / "csjn_casos_editorial.csv"

RE_IG = re.compile(r"^INDICE GENERAL\s*$", re.I)

df = pd.read_csv(CSV)

archivos = df.groupby("source_file").agg(
    tomo=("tomo", "first"),
    linea_max=("linea_fin", "max"),
).reset_index().sort_values(["tomo", "source_file"])

TAIL = 15  # líneas a mostrar

for _, row in archivos.iterrows():
    sf = row["source_file"]
    fp = CORPUS / sf
    if not fp.exists():
        continue
    lines = fp.read_text(encoding="utf-8").splitlines()
    lf = min(int(row["linea_max"]), len(lines) - 1)

    # Buscar INDICE GENERAL
    ig = None
    for i in range(int(row["linea_max"]), -1, -1):
        if i < len(lines) and RE_IG.match(lines[i].strip()):
            ig = i
            break
    if ig is None:
        continue

    n_total = lf - ig + 1
    desde = max(ig, lf - TAIL + 1)

    print(f"\n{'='*72}")
    print(f"T{row['tomo']} {sf} | INDICE GENERAL L{ig}–L{lf} ({n_total} líneas)")

    # Para bloques grandes (330.4), mostrar también la zona de transición
    if n_total > 200:
        TRANS = 100
        print(f"--- BLOQUE GRANDE: primeras {TRANS} líneas (TOC → transición) ---")
        for i in range(ig, min(ig + TRANS, lf + 1)):
            print(f"  {i:6d}  {lines[i].rstrip()}")
        print(f"  ... ({n_total - TRANS - TAIL} líneas omitidas) ...")

    print(f"--- Últimas {min(TAIL, lf - ig + 1)} líneas ---")
    for i in range(desde, lf + 1):
        print(f"  {i:6d}  {lines[i].rstrip()}")
