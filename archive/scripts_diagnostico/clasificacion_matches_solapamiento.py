# clasificacion_matches_solapamiento.py
# Para cada match del patron sumario-con-link, determina si la linea cae en
# zona de solapamiento con el bloque anterior/siguiente o es exclusiva.
# Output a archivo.

import re
import pandas as pd
from pathlib import Path

CSV_LOCALIZADOS = Path("paginas/fallos_localizados_fix1.csv")
CORPUS_DIR = Path("markdowns_v2")
OUTPUT = Path("clasificacion_matches_output.txt")

RE_SUMARIO_LINK = re.compile(
    r"^\(\*\)\s+Sentencia del .+? Ver (en https://sj\.csjn\.gov\.ar|fallo)",
    re.IGNORECASE
)

localizados = pd.read_csv(CSV_LOCALIZADOS)

# Filas validas
mask_validos = (
    localizados["linea_inicio"].notna()
    & localizados["linea_fin"].notna()
    & localizados["archivo"].notna()
)
validos = localizados[mask_validos].copy()
validos["linea_inicio"] = validos["linea_inicio"].astype(int)
validos["linea_fin"] = validos["linea_fin"].astype(int)

# Indexar bloques por archivo y ordenar por linea_inicio para construir vecinos
validos = validos.sort_values(["archivo", "linea_inicio"]).reset_index(drop=True)

# Para cada fila, calcular linea_inicio del siguiente bloque (mismo archivo) y linea_fin del anterior
validos["next_inicio"] = validos.groupby("archivo")["linea_inicio"].shift(-1)
validos["prev_fin"] = validos.groupby("archivo")["linea_fin"].shift(1)

# Cache de archivos
cache_archivos = {}

def get_lineas(archivo):
    if archivo not in cache_archivos:
        md_path = CORPUS_DIR / archivo
        if not md_path.exists():
            cache_archivos[archivo] = None
        else:
            with open(md_path, encoding="utf-8") as f:
                cache_archivos[archivo] = f.readlines()
    return cache_archivos[archivo]

# Para cada bloque, encontrar matches y clasificar cada uno
# Categorias:
#   - exclusivo: la linea pertenece solo a este bloque
#   - solap_con_anterior: la linea tambien esta dentro del bloque anterior
#   - solap_con_siguiente: la linea tambien esta dentro del bloque siguiente

resultados_por_bloque = []  # uno por bloque con al menos 1 match

for _, fila in validos.iterrows():
    caso_id = fila["caso_id_canonico"]
    archivo = fila["archivo"]
    li = fila["linea_inicio"]
    lf = fila["linea_fin"]
    next_inicio = fila["next_inicio"]
    prev_fin = fila["prev_fin"]

    lineas = get_lineas(archivo)
    if lineas is None:
        continue

    # Iterar lineas del bloque, detectar matches
    matches_info = []
    for offset, ln in enumerate(lineas[li - 1:lf]):
        if RE_SUMARIO_LINK.match(ln.strip()):
            n_linea = li + offset
            # Clasificar
            categorias = []
            if pd.notna(prev_fin) and n_linea <= prev_fin:
                categorias.append("solap_con_anterior")
            if pd.notna(next_inicio) and n_linea >= next_inicio:
                categorias.append("solap_con_siguiente")
            if not categorias:
                categorias.append("exclusivo")
            matches_info.append((n_linea, "+".join(categorias)))

    if matches_info:
        resultados_por_bloque.append({
            "caso_id": caso_id,
            "archivo": archivo,
            "li": li,
            "lf": lf,
            "prev_fin": prev_fin,
            "next_inicio": next_inicio,
            "n_matches": len(matches_info),
            "matches": matches_info,
        })

# Estadisticas
total_bloques_con_match = len(resultados_por_bloque)
bloques_2plus = [r for r in resultados_por_bloque if r["n_matches"] >= 2]

# Para los bloques con 2+: ¿cuantos tienen al menos un match exclusivo?
bloques_2plus_con_exclusivo = 0
bloques_2plus_solo_solap = 0
for r in bloques_2plus:
    cats = [c for _, c in r["matches"]]
    tiene_exclusivo = any("exclusivo" in c for c in cats)
    if tiene_exclusivo:
        bloques_2plus_con_exclusivo += 1
    else:
        bloques_2plus_solo_solap += 1

# Para los 254 totales: contar matches por categoria
total_matches = 0
matches_exclusivos = 0
matches_solap_anterior = 0
matches_solap_siguiente = 0
matches_solap_ambos = 0

for r in resultados_por_bloque:
    for _, cat in r["matches"]:
        total_matches += 1
        if cat == "exclusivo":
            matches_exclusivos += 1
        elif cat == "solap_con_anterior":
            matches_solap_anterior += 1
        elif cat == "solap_con_siguiente":
            matches_solap_siguiente += 1
        else:
            matches_solap_ambos += 1

# Output
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("CLASIFICACION DE MATCHES POR SOLAPAMIENTO\n")
    f.write("=" * 70 + "\n\n")

    f.write("RESUMEN\n")
    f.write("-" * 70 + "\n")
    f.write(f"Bloques con al menos 1 match: {total_bloques_con_match}\n")
    f.write(f"Bloques con 2+ matches: {len(bloques_2plus)}\n")
    f.write(f"  - con al menos 1 match exclusivo: {bloques_2plus_con_exclusivo}\n")
    f.write(f"  - todos los matches en solapamiento: {bloques_2plus_solo_solap}\n\n")

    f.write(f"Total de matches contados: {total_matches}\n")
    f.write(f"  - exclusivos (solo en este bloque): {matches_exclusivos}\n")
    f.write(f"  - en solapamiento con anterior: {matches_solap_anterior}\n")
    f.write(f"  - en solapamiento con siguiente: {matches_solap_siguiente}\n")
    f.write(f"  - en solapamiento con ambos: {matches_solap_ambos}\n\n")

    # Detalle de los 2+ que NO tienen ningun exclusivo (los mas raros)
    if bloques_2plus_solo_solap > 0:
        f.write("BLOQUES 2+ DONDE TODOS LOS MATCHES SON DE SOLAPAMIENTO\n")
        f.write("(estos son los menos preocupantes: los matches caen en zonas que comparten con vecinos)\n")
        f.write("-" * 70 + "\n")
        for r in bloques_2plus:
            cats = [c for _, c in r["matches"]]
            if not any("exclusivo" in c for c in cats):
                f.write(f"  {r['caso_id']} ({r['archivo']}, lineas {r['li']}-{r['lf']})\n")
                for n_l, cat in r["matches"]:
                    f.write(f"    linea {n_l}: {cat}\n")
        f.write("\n")

    # Detalle de los 2+ que SI tienen al menos un exclusivo (los preocupantes)
    if bloques_2plus_con_exclusivo > 0:
        f.write("BLOQUES 2+ CON AL MENOS UN MATCH EXCLUSIVO\n")
        f.write("(estos son los preocupantes: hay un patron sumario-con-link que pertenece UNICAMENTE a este bloque, ademas de otros)\n")
        f.write("-" * 70 + "\n")
        for r in bloques_2plus:
            cats = [c for _, c in r["matches"]]
            if any("exclusivo" in c for c in cats):
                f.write(f"  {r['caso_id']} ({r['archivo']}, lineas {r['li']}-{r['lf']})\n")
                for n_l, cat in r["matches"]:
                    f.write(f"    linea {n_l}: {cat}\n")

print(f"Output escrito en: {OUTPUT}")
