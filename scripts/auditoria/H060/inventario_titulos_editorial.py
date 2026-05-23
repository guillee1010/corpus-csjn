"""
H060 — Inventario de títulos editoriales.

Escanea todas las secciones editoriales del corpus y lista
las líneas en MAYÚSCULAS que podrían ser títulos de sección.
Objetivo: ver qué títulos canónicos existen antes de decidir regex.

Correr desde raíz del repo:
  python scripts/auditoria/H060/inventario_titulos_editorial.py
"""
import pandas as pd
from pathlib import Path
from collections import Counter

CORPUS = Path("corpus")
CSV = Path("output/parser/csjn_casos_editorial.csv")

df = pd.read_csv(CSV)

# Agrupar por archivo (cada archivo tiene un bloque editorial contiguo)
archivos = df.groupby("source_file").agg(
    tomo=("tomo", "first"),
    linea_min=("linea_ini", "min"),
    linea_max=("linea_fin", "max"),
).reset_index()

# Recolectar líneas candidatas a título:
# - En mayúsculas (o casi)
# - Más de 3 palabras (descartar page numbers sueltos)
# - No es puro número/puntuación
titulos = []        # (source_file, linea, texto)
titulos_counter = Counter()

for _, row in archivos.iterrows():
    sf = row["source_file"]
    fp = CORPUS / sf
    if not fp.exists():
        continue
    lines = fp.read_text(encoding="utf-8").splitlines()
    li = int(row["linea_min"])
    lf = min(int(row["linea_max"]), len(lines) - 1)

    for i in range(li, lf + 1):
        s = lines[i].strip()
        if not s:
            continue
        # Filtro: línea que empieza con "INDICE" o "NOMBRES" o "DISCURSO"
        # o "ACORDADA" o "LEGISLACION" — las candidatas a título
        upper = s.upper()
        is_candidate = False
        for kw in ["INDICE", "NOMBRES DE LAS PARTES",
                    "DISCURSO", "ACORDADA", "LEGISLACION",
                    "POR MATERIAS", "POR LOS NOMBRES"]:
            if kw in upper:
                is_candidate = True
                break
        if not is_candidate:
            continue

        # Descartar si es una entry del índice (contiene ": p." o "c/" o "p. ")
        if ": p." in s or "c/" in s.lower():
            continue

        # Descartar si tiene patrón TOC (puntos suspensivos)
        if "....." in s:
            continue

        titulos.append((row["tomo"], sf, i, s))
        titulos_counter[s] += 1

# Reportar
print("=" * 72)
print(f"TOTAL líneas candidatas a título: {len(titulos)}")
print()

print("=" * 72)
print("TEXTOS ÚNICOS (ordenados por frecuencia):")
print()
for texto, n in titulos_counter.most_common():
    print(f"  {n:4d}x  {texto!r}")

print()
print("=" * 72)
print("TEXTOS QUE APARECEN 1-3 VECES (probables títulos reales):")
print()
for texto, n in sorted(titulos_counter.items(), key=lambda x: x[1]):
    if n <= 3:
        # Mostrar en qué archivos aparecen
        locs = [(t, sf, li) for t, sf, li, tx in titulos if tx == texto]
        locs_str = "; ".join(f"T{t}/{sf}:L{li}" for t, sf, li in locs[:5])
        print(f"  {n}x  {texto!r}")
        print(f"      -> {locs_str}")

print()
print("=" * 72)
print("TEXTOS QUE APARECEN 10+ VECES (probables page headers):")
print()
for texto, n in titulos_counter.most_common():
    if n >= 10:
        print(f"  {n:4d}x  {texto!r}")
