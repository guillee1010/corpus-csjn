"""
H060 — Mapa estructural editorial por archivo.

Para cada archivo, muestra la secuencia de títulos y page headers
en orden de aparición. Objetivo: ver el orden canónico de secciones
y cómo detectar transiciones donde no hay título único.

Correr desde raíz del repo:
  python scripts/auditoria/H060/mapa_estructura_editorial.py
"""
import pandas as pd
from pathlib import Path
import re

CORPUS = Path("corpus")
CSV = Path("output/parser/csjn_casos_editorial.csv")

df = pd.read_csv(CSV)

# Títulos y headers conocidos (de inventario_titulos_editorial.py).
# Orden: primero los más específicos para evitar matches parciales.
MARKERS = [
    # Títulos de sección (aparecen ~1x por archivo)
    ("TITULO_PARTES",       re.compile(r"^INDICE POR LOS NOMBRES DE LAS PARTES\s*$", re.I)),
    ("TITULO_MATERIAS",     re.compile(r"^INDICE ALFAB[EÉ]TICO POR MATERIAS\s*$", re.I)),
    ("TITULO_LEG_ASTERISCO", re.compile(r"^INDICE DE LEGISLACI[OÓ]N\s*\(\*\)\s*$", re.I)),
    ("TITULO_ACORDADAS_CSJN", re.compile(r"^ACORDADAS DE LA CSJN\s*$", re.I)),
    ("TITULO_DISCURSOS",    re.compile(r"^DISCURSOS\s*$", re.I)),
    ("TITULO_DISC_APERTURA", re.compile(r"^Discurso de apertura del año judicial", re.I)),
    # Page headers (aparecen muchas veces)
    ("HDR_PARTES",          re.compile(r"^NOMBRES DE LAS PARTES\s*$", re.I)),
    ("HDR_LEG",             re.compile(r"^INDICE DE LEGISLACI[OÓ]N\s*$", re.I)),
    ("HDR_GENERAL",         re.compile(r"^INDICE GENERAL\s*$", re.I)),
    ("HDR_SUMARIO",         re.compile(r"^INDICE SUMARIO\s*$", re.I)),
    ("HDR_LEG_NAC",         re.compile(r"^LEGISLACI[OÓ]N NACIONAL\s*$", re.I)),
    ("HDR_LEG_PROV",        re.compile(r"^LEGISLACI[OÓ]N PROVINCIAL\s*$", re.I)),
    ("HDR_LEG_INTL",        re.compile(r"^LEGISLACI[OÓ]N? INTERNACIONAL\s*$", re.I)),
    ("HDR_DISC_ASUNTOS",    re.compile(r"^DISCURSOS\s*[–-]\s*ASUNTOS", re.I)),
    ("HDR_ACORDADAS_Y_RES", re.compile(r"^ACORDADAS Y RESOLUCIONES\s*$", re.I)),
    ("HDR_ACORDADAS",       re.compile(r"^ACORDADAS\s*$", re.I)),
    ("HDR_ACORD_Y_RES_MC",  re.compile(r"^Acordadas y Resoluciones\s*$")),  # mixed case
    ("HDR_ACORD_MC",        re.compile(r"^Acordadas\s*$")),                 # mixed case
    ("HDR_DISCURSOS_MC",    re.compile(r"^Discursos\s*$")),                 # mixed case
    ("HDR_IND_PARTES_MC",   re.compile(r"^Indice por los nombres de las partes")),
    ("TOC_ENTRY",           re.compile(r"^.+\.{5,}")),  # línea con puntos suspensivos = TOC
]

archivos = df.groupby("source_file").agg(
    tomo=("tomo", "first"),
    linea_min=("linea_ini", "min"),
    linea_max=("linea_fin", "max"),
).reset_index().sort_values(["tomo", "source_file"])

for _, row in archivos.iterrows():
    sf = row["source_file"]
    fp = CORPUS / sf
    if not fp.exists():
        continue
    lines = fp.read_text(encoding="utf-8").splitlines()
    li = int(row["linea_min"])
    lf = min(int(row["linea_max"]), len(lines) - 1)

    # Encontrar PRIMERA ocurrencia de cada marker
    first_hits = {}  # marker_name -> (line_num, text)
    for i in range(li, lf + 1):
        s = lines[i].strip()
        if not s:
            continue
        for name, rx in MARKERS:
            if name not in first_hits and rx.match(s):
                first_hits[name] = (i, s)
                break  # solo el primer marker que matchea

    # Mostrar solo los que aparecen, ordenados por línea
    if not first_hits:
        continue
    hits_sorted = sorted(first_hits.items(), key=lambda x: x[1][0])

    print(f"\n{'='*72}")
    print(f"TOMO {row['tomo']} | {sf} | editorial: {li}–{lf}")
    for name, (lineno, text) in hits_sorted:
        # Solo mostrar TITULO_* y la primera aparición de cada HDR_*
        tag = "TITULO" if name.startswith("TITULO") else "header"
        print(f"  L{lineno:6d}  [{tag:7s}]  {name:25s}  {text[:70]}")
