"""
H060 — ¿Qué líneas tienen puntos consecutivos en los bloques de INDICE GENERAL?

Muestra todas las líneas con 4+ puntos en cada bloque INDICE GENERAL,
con el conteo de puntos. Objetivo: ver el rango real de puntos en
entries legítimas del TOC vs artefactos.

También muestra L52377 de 330.4 para ver qué matcheó.
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
RE_DOTS = re.compile(r"\.{4,}")

df = pd.read_csv(CSV)
archivos = df.groupby("source_file").agg(
    tomo=("tomo", "first"),
    linea_max=("linea_fin", "max"),
).reset_index().sort_values(["tomo", "source_file"])

# Recopilar todas las líneas con puntos y su conteo
all_dots = []  # (source_file, linea, n_dots, texto)

for _, row in archivos.iterrows():
    sf = row["source_file"]
    fp = CORPUS / sf
    if not fp.exists():
        continue
    lines = fp.read_text(encoding="utf-8").splitlines()
    lf = min(int(row["linea_max"]), len(lines) - 1)

    # Buscar INDICE GENERAL
    ig = None
    for i in range(lf, -1, -1):
        if i < len(lines) and RE_IG.match(lines[i].strip()):
            ig = i
            break
    if ig is None:
        continue

    for i in range(ig, lf + 1):
        s = lines[i].strip()
        m = RE_DOTS.search(s)
        if m:
            n_dots = len(m.group())
            all_dots.append((sf, i, n_dots, s[:80]))

# Reportar
print("=" * 90)
print(f"TOTAL líneas con .{{4,}} en bloques INDICE GENERAL: {len(all_dots)}")
print()

# Distribución de conteo de puntos
from collections import Counter
dist = Counter(d[2] for d in all_dots)
print("Distribución de cantidad de puntos consecutivos:")
for n in sorted(dist):
    print(f"  {n:3d} puntos: {dist[n]:3d} líneas")
print()

# Líneas con MENOS de 20 puntos (potenciales conflictos)
short = [d for d in all_dots if d[2] < 20]
if short:
    print("=" * 90)
    print(f"LÍNEAS CON < 20 PUNTOS ({len(short)}):")
    for sf, linea, n, texto in short:
        print(f"  {sf:<25s} L{linea:6d}  ({n:2d} dots)  {texto}")
else:
    print("Todas las líneas con puntos tienen 20+ → umbral .{20,} sería seguro")

# Líneas con MÁS de 20 puntos (TOC legítimo)
long = [d for d in all_dots if d[2] >= 20]
print()
print("=" * 90)
print(f"MUESTRA de líneas con >= 20 puntos (primeras 10):")
for sf, linea, n, texto in long[:10]:
    print(f"  {sf:<25s} L{linea:6d}  ({n:2d} dots)  {texto}")
