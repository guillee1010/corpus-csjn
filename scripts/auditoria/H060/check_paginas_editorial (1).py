"""
H060 — ¿El mapa de páginas cubre la zona editorial?

Para cada archivo, compara:
- última página mapeada (de fallos_localizados o mapa_paginas)
- línea de inicio del editorial (de csjn_casos_editorial.csv)
- página del INDICE GENERAL donde dice que arrancan acordadas/índice

Correr: python scripts/auditoria/H060/check_paginas_editorial.py
"""
import pandas as pd
from pathlib import Path

# Ajustar rutas si es necesario
EDITORIAL_CSV = Path("output/parser/csjn_casos_editorial.csv")
# Probar distintas fuentes del mapa de páginas
MAPA_CANDIDATES = [
    Path("output/localizacion/fallos_localizados.csv"),
    Path("output/paginas/mapa_paginas.csv"),
]

df_ed = pd.read_csv(EDITORIAL_CSV)

# Encontrar el mapa de páginas
mapa_path = None
for p in MAPA_CANDIDATES:
    if p.exists():
        mapa_path = p
        break

if mapa_path is None:
    print("ERROR: no encontré archivo de mapa de páginas")
    print("Candidatos probados:", [str(p) for p in MAPA_CANDIDATES])
    exit(1)

print(f"Usando mapa: {mapa_path}")
df_mapa = pd.read_csv(mapa_path)
print(f"Columnas del mapa: {list(df_mapa.columns)}")
print(f"Filas: {len(df_mapa)}")
print()

# Mostrar las primeras filas para entender la estructura
print("Primeras 3 filas del mapa:")
print(df_mapa.head(3).to_string())
print()

# Para cada source_file del editorial, buscar la última página mapeada
# y la primera línea editorial
ed_por_archivo = df_ed.groupby("source_file").agg(
    tomo=("tomo", "first"),
    linea_ini_editorial=("linea_ini", "min"),
).reset_index()

# Detectar columna de source_file en el mapa
sf_col = None
for c in ["source_file", "archivo", "file", "source"]:
    if c in df_mapa.columns:
        sf_col = c
        break

linea_col = None
for c in ["linea", "line", "linea_inicio", "linea_ini"]:
    if c in df_mapa.columns:
        linea_col = c
        break

pagina_col = None
for c in ["pagina", "page", "pagina_num", "num_pagina"]:
    if c in df_mapa.columns:
        pagina_col = c
        break

print(f"Columnas detectadas: sf={sf_col}, linea={linea_col}, pagina={pagina_col}")
print()

if sf_col and linea_col:
    print("=" * 72)
    print(f"{'ARCHIVO':<25} {'TOMO':>4} {'ULT_PAG_MAPA':>12} {'ULT_LINEA_MAPA':>15} {'INI_EDITORIAL':>14} {'CUBIER?':>8}")
    print("-" * 72)

    for _, row in ed_por_archivo.sort_values(["tomo", "source_file"]).iterrows():
        sf = row["source_file"]
        mapa_sf = df_mapa[df_mapa[sf_col] == sf]
        if mapa_sf.empty:
            print(f"{sf:<25} {row['tomo']:>4} {'(sin mapa)':>12} {'':>15} {row['linea_ini_editorial']:>14}")
            continue

        ult_linea = int(mapa_sf[linea_col].max())
        ini_ed = int(row["linea_ini_editorial"])
        cubierto = "SI" if ult_linea >= ini_ed else f"NO (-{ini_ed - ult_linea})"

        if pagina_col:
            ult_pag = mapa_sf.loc[mapa_sf[linea_col].idxmax(), pagina_col]
            print(f"{sf:<25} {row['tomo']:>4} {str(ult_pag):>12} {ult_linea:>15} {ini_ed:>14} {cubierto:>8}")
        else:
            print(f"{sf:<25} {row['tomo']:>4} {'':>12} {ult_linea:>15} {ini_ed:>14} {cubierto:>8}")
else:
    print("No pude detectar las columnas necesarias.")
    print("Columnas disponibles:", list(df_mapa.columns))
