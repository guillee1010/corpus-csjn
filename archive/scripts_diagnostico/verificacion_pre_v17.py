# verificacion_pre_v17.py
# Dos verificaciones empíricas antes de implementar v17:
# 1. ¿El fallo anterior a cada uno de los 4 casos verificados tiene firma propia?
# 2. ¿Hay bloques del corpus con 2 o más matches del patrón sumario-con-link?

import re
import pandas as pd
from pathlib import Path

# --- Config ---
CSV_CASOS = Path("paginas/csjn_casos_v16_fix1.csv")
CSV_LOCALIZADOS = Path("paginas/fallos_localizados_fix1.csv")
CORPUS_DIR = Path("markdowns_v2")

RE_SUMARIO_LINK = re.compile(
    r"^\(\*\)\s+Sentencia del .+? Ver (en https://sj\.csjn\.gov\.ar|fallo)",
    re.IGNORECASE
)

CASOS_VERIFICADOS = ["345_p1100", "346_p192", "347_p1378", "348_p1533"]

# --- Carga ---
casos = pd.read_csv(CSV_CASOS)
localizados = pd.read_csv(CSV_LOCALIZADOS)

print("=" * 70)
print("VERIFICACION 1: firma del fallo anterior a cada sumario-con-link")
print("=" * 70)

for caso_id in CASOS_VERIFICADOS:
    fila = casos[casos["caso_id_canonico"] == caso_id]
    if fila.empty:
        print(f"\n{caso_id}: NO ENCONTRADO en CSV")
        continue

    tomo = fila.iloc[0]["tomo"]
    # Extraer numero de pagina del id (formato: TOMO_pNUMERO)
    pag_actual = int(caso_id.split("_p")[1])

    # Buscar el caso anterior en el mismo tomo (mayor pagina < pag_actual)
    mismo_tomo = casos[casos["tomo"] == tomo].copy()
    mismo_tomo["pag_num"] = mismo_tomo["caso_id_canonico"].str.extract(r"_p(\d+)").astype(int)
    anteriores = mismo_tomo[mismo_tomo["pag_num"] < pag_actual].sort_values("pag_num", ascending=False)

    if anteriores.empty:
        print(f"\n{caso_id}: no hay caso anterior en el tomo")
        continue

    anterior = anteriores.iloc[0]
    print(f"\n{caso_id} (pag {pag_actual}, tomo {tomo})")
    print(f"  caso anterior: {anterior['caso_id_canonico']} (pag {anterior['pag_num']})")
    print(f"  voting_pattern anterior: {anterior['voting_pattern']}")
    print(f"  outcome anterior: {anterior['outcome']}")
    print(f"  case_name anterior: {anterior['case_name_indice'][:80]}")

print("\n" + "=" * 70)
print("VERIFICACION 2: bloques con 2+ matches del patron sumario-con-link")
print("=" * 70)

# Recorrer cada caso, reconstruir su bloque, contar matches
multi_match = []
total_con_patron = 0

for _, fila in localizados.iterrows():
    caso_id = fila["caso_id_canonico"]
    source_file = fila["source_file"]
    linea_inicio = int(fila["linea_inicio"])
    linea_fin = int(fila["linea_fin_real"])

    md_path = CORPUS_DIR / source_file
    if not md_path.exists():
        continue

    with open(md_path, encoding="utf-8") as f:
        lineas = f.readlines()

    bloque = lineas[linea_inicio - 1:linea_fin]
    matches = sum(1 for ln in bloque if RE_SUMARIO_LINK.match(ln.strip()))

    if matches >= 1:
        total_con_patron += 1
    if matches >= 2:
        multi_match.append((caso_id, source_file, linea_inicio, linea_fin, matches))

print(f"\nTotal bloques con al menos 1 match: {total_con_patron}")
print(f"Bloques con 2+ matches: {len(multi_match)}")
if multi_match:
    print("\nDetalle:")
    for caso_id, sf, li, lf, n in multi_match:
        print(f"  {caso_id} en {sf} (lineas {li}-{lf}): {n} matches")
