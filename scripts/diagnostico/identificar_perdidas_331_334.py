"""
identificar_perdidas_331_334.py  (v2)

Identifica las entradas del catálogo v15 que NO están en el output del parser
v17beta para los tomos 331, 332, 333, 334.

Columnas reales del catálogo v15:
  caso_id_canonico, nombres_indice, n_archivos_indice, n_nombres,
  pagina_fin, pagina_inicio, tomo

Salida:
  - Tabla por consola con tomo, pagina_inicio, pagina_fin, nombres_indice
  - CSV: scripts/diagnosticos/perdidas_331_334.csv
"""

import csv
from pathlib import Path

PROJ_ROOT = Path(r"C:\Users\guill\Proyectos\corpus-csjn")
CATALOGO = PROJ_ROOT / "catalogo_v15.csv"
PARSER = PROJ_ROOT / "csjn_casos_v17beta_fix349.csv"
OUT_CSV = PROJ_ROOT / "scripts" / "diagnosticos" / "perdidas_331_334.csv"

TOMOS_OBJETIVO = [331, 332, 333, 334]

# ============================================================
# 1. Cargar IDs por tomo de cada CSV
# ============================================================

def cargar_ids_por_tomo(path):
    por_tomo = {t: set() for t in TOMOS_OBJETIVO}
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tomo = int(row["tomo"])
            except (ValueError, KeyError):
                continue
            if tomo in TOMOS_OBJETIVO:
                por_tomo[tomo].add(row["caso_id_canonico"])
    return por_tomo

print("Cargando IDs del catalogo v15...")
ids_cat = cargar_ids_por_tomo(CATALOGO)

print("Cargando IDs del parser v17beta...")
ids_par = cargar_ids_por_tomo(PARSER)

# ============================================================
# 2. Calcular pérdidas (en catálogo y NO en parser)
# ============================================================

ids_perdidos = set()
print(f"\n{'='*70}")
print(f"CONTEO DE PERDIDAS")
print(f"{'='*70}")

for tomo in TOMOS_OBJETIVO:
    perdidas = ids_cat[tomo] - ids_par[tomo]
    print(f"  Tomo {tomo}: {len(perdidas)} perdidas")
    for cid in perdidas:
        ids_perdidos.add((str(tomo), cid))

print(f"  TOTAL: {len(ids_perdidos)} entradas perdidas")

# ============================================================
# 3. Re-leer el catálogo y traer las filas completas de las pérdidas
# ============================================================

print(f"\nBuscando metadata completa en el catalogo...")
filas_perdidas = []
with open(CATALOGO, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        clave = (row["tomo"], row["caso_id_canonico"])
        if clave in ids_perdidos:
            filas_perdidas.append(row)

# Ordenar por tomo y página
def safe_int(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return 0

filas_perdidas.sort(key=lambda r: (safe_int(r.get("tomo")), safe_int(r.get("pagina_inicio"))))

# ============================================================
# 4. Imprimir tabla resumida
# ============================================================

print(f"\n{'='*70}")
print(f"DETALLE DE LAS PERDIDAS")
print(f"{'='*70}\n")

print(f"{'Tomo':>5} | {'p.ini':>6} | {'p.fin':>6} | {'caso_id':<14} | nombres_indice")
print("-" * 110)

for row in filas_perdidas:
    tomo = row.get("tomo", "")
    pini = row.get("pagina_inicio", "")
    pfin = row.get("pagina_fin", "")
    cid = row.get("caso_id_canonico", "")
    nombres = row.get("nombres_indice", "")
    # Truncar nombres muy largos
    if len(nombres) > 70:
        nombres = nombres[:67] + "..."
    print(f"{tomo:>5} | {pini:>6} | {pfin:>6} | {cid:<14} | {nombres}")

# ============================================================
# 5. Guardar CSV
# ============================================================

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
if filas_perdidas:
    fieldnames = list(filas_perdidas[0].keys())
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filas_perdidas)
    print(f"\nGuardado: {OUT_CSV}")
else:
    print(f"\nNo se encontraron filas para guardar.")

print(f"\n=== Listo ===")
