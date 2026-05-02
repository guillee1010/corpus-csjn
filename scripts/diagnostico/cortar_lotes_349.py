"""
cortar_lotes_349.py

Corta el LibroVol349-1.md en 5 lotes para benchmark con Gemini.
Lee csjn_casos_v17beta_fix349.csv, filtra los 45 fallos del Tomo 349,
los ordena por linea_inicio, y los agrupa en 5 lotes de 9 fallos cada uno.

Para cada lote escribe:
  - benchmark_gemini/lote_{N}.md  : el fragmento del .md correspondiente
  - benchmark_gemini/lotes_manifest.csv : trazabilidad (qué fallos están en cada lote)

Diseño:
  - El lote arranca en la linea_inicio del primer fallo y termina en la
    linea_fin_real del último.
  - Los solapamientos entre fallos consecutivos en el catálogo son
    tolerados (el catálogo así los marca).
  - El fallo Y.P.F. (no detectado por el parser, pero presente en el .md
    en línea 1601) queda físicamente embebido en el lote que contiene a
    Décima — esto es deliberado, para validar el rol de Gemini como
    auditor independiente del corpus.

Uso:
    python cortar_lotes_349.py

Salida esperada:
    benchmark_gemini/lote_1.md ... lote_5.md
    benchmark_gemini/lotes_manifest.csv
"""

import csv
import os
from pathlib import Path

# ============================================================
# Configuración
# ============================================================

PROJ_ROOT = Path(r"C:\Users\guill\Proyectos\corpus-csjn")
CSV_INPUT = PROJ_ROOT / "csjn_casos_v17beta_fix349.csv"
MD_INPUT = PROJ_ROOT / "markdowns_v2" / "LibroVol349-1.md"
OUT_DIR = PROJ_ROOT / "benchmark_gemini"
TOMO_OBJETIVO = 349
N_LOTES = 5

# ============================================================
# 1. Leer y filtrar el CSV
# ============================================================

print(f"Leyendo {CSV_INPUT}...")
fallos = []
with open(CSV_INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row["tomo"]) == TOMO_OBJETIVO:
            fallos.append({
                "caso_id": row["caso_id_canonico"],
                "case_name": row.get("case_name_indice", "") or row.get("case_name_cuerpo", ""),
                "source_file": row["source_file"],
                "linea_inicio": int(row["linea_inicio"]),
                "linea_fin_real": int(row["linea_fin_real"]),
            })

print(f"Encontrados {len(fallos)} fallos del Tomo {TOMO_OBJETIVO}.")

# Verificar que todos vengan del mismo .md
source_files = set(f["source_file"] for f in fallos)
if len(source_files) > 1:
    print(f"WARNING: múltiples source_files en el Tomo {TOMO_OBJETIVO}: {source_files}")
else:
    print(f"Todos los fallos provienen de: {list(source_files)[0]}")

# Ordenar por linea_inicio
fallos.sort(key=lambda f: f["linea_inicio"])

# ============================================================
# 2. Distribuir en N_LOTES
# ============================================================

# División entera con resto distribuido en los primeros lotes
n_total = len(fallos)
base = n_total // N_LOTES
resto = n_total % N_LOTES

lotes = []
idx = 0
for i in range(N_LOTES):
    tamaño = base + (1 if i < resto else 0)
    lotes.append(fallos[idx:idx + tamaño])
    idx += tamaño

print(f"\nDistribución de fallos por lote:")
for i, lote in enumerate(lotes, 1):
    print(f"  Lote {i}: {len(lote)} fallos | "
          f"líneas {lote[0]['linea_inicio']}-{lote[-1]['linea_fin_real']} | "
          f"{lote[0]['caso_id']} → {lote[-1]['caso_id']}")

# ============================================================
# 3. Leer el .md
# ============================================================

print(f"\nLeyendo {MD_INPUT}...")
with open(MD_INPUT, encoding="utf-8") as f:
    md_lines = f.readlines()
print(f"Total líneas del .md: {len(md_lines)}")

# ============================================================
# 4. Escribir los lotes y el manifiesto
# ============================================================

OUT_DIR.mkdir(exist_ok=True)
print(f"\nEscribiendo lotes en {OUT_DIR}/")

manifest_rows = []

for i, lote in enumerate(lotes, 1):
    primera_linea = lote[0]["linea_inicio"]
    ultima_linea = lote[-1]["linea_fin_real"]

    # Las líneas del CSV son 1-based; en Python usamos 0-based
    # md_lines[primera_linea - 1 : ultima_linea] es inclusivo en ambos extremos
    fragmento = md_lines[primera_linea - 1: ultima_linea]

    out_path = OUT_DIR / f"lote_{i}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(fragmento)

    print(f"  Lote {i}: {out_path.name} "
          f"({len(fragmento)} líneas, "
          f"~{sum(len(l) for l in fragmento) // 1000} KB)")

    for fallo in lote:
        manifest_rows.append({
            "lote": i,
            "caso_id_canonico": fallo["caso_id"],
            "case_name": fallo["case_name"],
            "linea_inicio": fallo["linea_inicio"],
            "linea_fin_real": fallo["linea_fin_real"],
        })

# Escribir manifiesto
manifest_path = OUT_DIR / "lotes_manifest.csv"
with open(manifest_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["lote", "caso_id_canonico", "case_name",
                                            "linea_inicio", "linea_fin_real"])
    writer.writeheader()
    writer.writerows(manifest_rows)

print(f"\nManifiesto: {manifest_path.name} ({len(manifest_rows)} filas)")
print(f"\nListo. Pasale lote_1.md ... lote_{N_LOTES}.md a Gemini, uno por uno,")
print(f"con el prompt de prompt_gemini_v2_lotes.md.")
