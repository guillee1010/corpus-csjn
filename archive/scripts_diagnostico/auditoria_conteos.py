"""
auditoria_conteos.py

Audita la coincidencia entre el catálogo v15 y el output del parser v17beta
para todos los tomos del corpus.

Para cada tomo:
  - Cuenta entradas del catálogo
  - Cuenta entradas del parser
  - Calcula delta (parser - catálogo)
  - Lista los archivos .md del tomo y cuántas entradas hay en cada uno

Salida:
  - Tabla por consola
  - CSV: scripts/diagnosticos/auditoria_conteos.csv

Uso:
    python scripts/diagnosticos/auditoria_conteos.py
"""

import csv
from pathlib import Path
from collections import defaultdict

PROJ_ROOT = Path(r"C:\Users\guill\Proyectos\corpus-csjn")
CATALOGO = PROJ_ROOT / "catalogo_v15.csv"
PARSER = PROJ_ROOT / "csjn_casos_v17beta_fix349.csv"
OUT_CSV = PROJ_ROOT / "scripts" / "diagnosticos" / "auditoria_conteos.csv"

# ============================================================
# Cargar conteos por tomo y por archivo
# ============================================================

def cargar_conteos(path):
    """Devuelve dos diccionarios: por tomo, y por (tomo, source_file)."""
    por_tomo = defaultdict(int)
    por_tomo_archivo = defaultdict(int)

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                tomo = int(row["tomo"])
            except (ValueError, KeyError):
                continue
            por_tomo[tomo] += 1
            sf = row.get("source_file", "(sin source_file)")
            por_tomo_archivo[(tomo, sf)] += 1

    return por_tomo, por_tomo_archivo


print(f"Cargando catalogo v15: {CATALOGO.name}")
cat_tomo, cat_tomo_arch = cargar_conteos(CATALOGO)
print(f"  Tomos en catalogo: {len(cat_tomo)}, total entradas: {sum(cat_tomo.values())}")

print(f"\nCargando parser v17beta: {PARSER.name}")
par_tomo, par_tomo_arch = cargar_conteos(PARSER)
print(f"  Tomos en parser: {len(par_tomo)}, total entradas: {sum(par_tomo.values())}")

# ============================================================
# Comparar por tomo
# ============================================================

print(f"\n{'='*60}")
print(f"COMPARACIÓN POR TOMO")
print(f"{'='*60}\n")

todos_los_tomos = sorted(set(cat_tomo.keys()) | set(par_tomo.keys()))

print(f"{'Tomo':>6} | {'Catalogo':>9} | {'Parser':>7} | {'Delta':>7} | Estado")
print("-" * 60)

filas_audit = []
total_delta_no_cero = 0

for tomo in todos_los_tomos:
    n_cat = cat_tomo.get(tomo, 0)
    n_par = par_tomo.get(tomo, 0)
    delta = n_par - n_cat

    if delta == 0:
        estado = "OK"
    elif delta < 0:
        estado = f"PARSER PIERDE {-delta}"
        total_delta_no_cero += 1
    else:
        estado = f"PARSER DUPLICA {delta}"
        total_delta_no_cero += 1

    print(f"{tomo:>6} | {n_cat:>9} | {n_par:>7} | {delta:>+7} | {estado}")
    filas_audit.append({
        "tomo": tomo,
        "n_catalogo": n_cat,
        "n_parser": n_par,
        "delta": delta,
        "estado": estado,
    })

print("-" * 60)
print(f"Total entradas catalogo: {sum(cat_tomo.values())}")
print(f"Total entradas parser:   {sum(par_tomo.values())}")
print(f"Tomos con delta != 0:    {total_delta_no_cero}")

# ============================================================
# Distribución por archivo .md (para los tomos con delta != 0
# o para todos si no hay desacuerdo)
# ============================================================

print(f"\n{'='*60}")
print(f"DISTRIBUCIÓN POR ARCHIVO .md (catálogo)")
print(f"{'='*60}\n")

print(f"{'Tomo':>6} | {'Archivo':<30} | {'N':>6}")
print("-" * 50)

archivos_por_tomo = defaultdict(list)
for (tomo, sf), n in cat_tomo_arch.items():
    archivos_por_tomo[tomo].append((sf, n))

for tomo in todos_los_tomos:
    archivos = sorted(archivos_por_tomo.get(tomo, []))
    for sf, n in archivos:
        print(f"{tomo:>6} | {sf:<30} | {n:>6}")
    if len(archivos) > 1:
        total = sum(n for _, n in archivos)
        print(f"{'':>6} | {'(total)':<30} | {total:>6}")
        print()

# ============================================================
# Guardar CSV
# ============================================================

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["tomo", "n_catalogo", "n_parser", "delta", "estado"])
    writer.writeheader()
    writer.writerows(filas_audit)

print(f"\nGuardado: {OUT_CSV}")
print(f"\n=== Listo ===")
