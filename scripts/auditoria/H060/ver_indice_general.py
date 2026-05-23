"""
H060 — Contenido completo del INDICE GENERAL por archivo.

Extrae todas las líneas desde el primer 'INDICE GENERAL' hasta
el fin del bloque editorial. Objetivo: ver si el formato es
estable y qué información contiene en cada era.

Correr: python scripts/auditoria/H060/ver_indice_general.py
"""
import pandas as pd
from pathlib import Path
import re

CORPUS = Path("corpus")
CSV = Path("output/parser/csjn_casos_editorial.csv")

df = pd.read_csv(CSV)

# Representativos: uno de cada era + casos especiales
# Era 1: 329.1 (estándar), 329.4 (gigante), 330.3 (discursos), 330.4 (anomalía)
# Era 2: 337.1 (simplificado), 344-1 (duplicado), 341.2 (acordadas), 348 (mínimo)
TARGETS = [
    "LibroVol329.1.md", "LibroVol329.4.md",
    "LibroVol330.3.md", "LibroVol330.4.md",
    "LibroVol331.1.md",
    "LibroVol337.1.md", "LibroVol337.2.md",
    "LibroVol340.1.md",
    "LibroVol341.2.md",
    "LibroVol344-1.md", "LibroVol344-2.md",
    "LibroVol348-1.md",
    "LibroVol349-1.md",
]

RE_INDICE_GENERAL = re.compile(r"^INDICE GENERAL\s*$", re.I)

archivos = df.groupby("source_file").agg(
    tomo=("tomo", "first"),
    linea_min=("linea_ini", "min"),
    linea_max=("linea_fin", "max"),
).reset_index()

for sf in TARGETS:
    row = archivos[archivos["source_file"] == sf]
    if row.empty:
        print(f"\n{'='*72}")
        print(f"NO ENCONTRADO: {sf}")
        continue
    row = row.iloc[0]
    fp = CORPUS / sf
    if not fp.exists():
        continue
    lines = fp.read_text(encoding="utf-8").splitlines()
    li = int(row["linea_min"])
    lf = min(int(row["linea_max"]), len(lines) - 1)

    # Buscar primer INDICE GENERAL
    ig_start = None
    for i in range(li, lf + 1):
        if RE_INDICE_GENERAL.match(lines[i].strip()):
            ig_start = i
            break

    print(f"\n{'='*72}")
    print(f"TOMO {row['tomo']} | {sf} | editorial: {li}–{lf}")
    if ig_start is None:
        print("  (No se encontró INDICE GENERAL)")
        continue

    print(f"  INDICE GENERAL empieza en L{ig_start} ({lf - ig_start + 1} líneas hasta EOF)")
    print(f"  --- Contenido completo ---")
    for i in range(ig_start, min(lf + 1, len(lines))):
        print(f"  {i:6d}  {lines[i].rstrip()}")
