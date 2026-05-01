# verificacion_2_v17.py
# Verifica si hay bloques con 2+ matches del patron sumario-con-link.
# Output a archivo (no a consola) para evitar truncado.

import re
import pandas as pd
from pathlib import Path

CSV_LOCALIZADOS = Path("paginas/fallos_localizados_fix1.csv")
CORPUS_DIR = Path("markdowns_v2")
OUTPUT = Path("verificacion_2_v17_output.txt")

RE_SUMARIO_LINK = re.compile(
    r"^\(\*\)\s+Sentencia del .+? Ver (en https://sj\.csjn\.gov\.ar|fallo)",
    re.IGNORECASE
)

localizados = pd.read_csv(CSV_LOCALIZADOS)

# Filtrar filas con datos de localizacion validos
mask_validos = (
    localizados["linea_inicio"].notna()
    & localizados["linea_fin"].notna()
    & localizados["archivo"].notna()
)
validos = localizados[mask_validos].copy()
descartados = len(localizados) - len(validos)

# Cache de archivos para no releer
cache_archivos = {}

multi_match = []
total_con_patron = 0
procesados = 0
saltados_archivo_inexistente = 0

for _, fila in validos.iterrows():
    caso_id = fila["caso_id_canonico"]
    archivo = fila["archivo"]
    linea_inicio = int(fila["linea_inicio"])
    linea_fin = int(fila["linea_fin"])

    if archivo not in cache_archivos:
        md_path = CORPUS_DIR / archivo
        if not md_path.exists():
            cache_archivos[archivo] = None
        else:
            with open(md_path, encoding="utf-8") as f:
                cache_archivos[archivo] = f.readlines()

    lineas = cache_archivos[archivo]
    if lineas is None:
        saltados_archivo_inexistente += 1
        continue

    bloque = lineas[linea_inicio - 1:linea_fin]
    matches = sum(1 for ln in bloque if RE_SUMARIO_LINK.match(ln.strip()))

    if matches >= 1:
        total_con_patron += 1
    if matches >= 2:
        multi_match.append((caso_id, archivo, linea_inicio, linea_fin, matches))

    procesados += 1

# Escribir output
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("VERIFICACION 2: bloques con 2+ matches del patron sumario-con-link\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Filas totales en localizados: {len(localizados)}\n")
    f.write(f"Filas validas (con linea_inicio/linea_fin/archivo): {len(validos)}\n")
    f.write(f"Filas descartadas por NaN: {descartados}\n")
    f.write(f"Filas saltadas por archivo inexistente: {saltados_archivo_inexistente}\n")
    f.write(f"Filas procesadas: {procesados}\n\n")
    f.write(f"Bloques con al menos 1 match: {total_con_patron}\n")
    f.write(f"Bloques con 2+ matches: {len(multi_match)}\n\n")

    if multi_match:
        f.write("Detalle de bloques con 2+ matches:\n")
        f.write("-" * 70 + "\n")
        for caso_id, sf, li, lf, n in multi_match:
            f.write(f"  {caso_id} en {sf} (lineas {li}-{lf}): {n} matches\n")

print(f"Output escrito en: {OUTPUT}")
