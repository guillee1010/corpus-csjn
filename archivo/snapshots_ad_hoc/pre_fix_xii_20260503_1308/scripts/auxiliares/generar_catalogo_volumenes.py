"""
Genera catalogo_volumenes.csv a partir de mapa_paginas.csv.
Para cada combinación (tomo, archivo), calcula la página mínima y máxima.

Uso (desde paginas\):
    python ..\generar_catalogo_volumenes.py
"""
import csv
from collections import defaultdict

INPUT = "mapa_paginas.csv"
OUTPUT = "catalogo_volumenes.csv"

paginas_por_archivo = defaultdict(list)
with open(INPUT, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        clave = (row["tomo"], row["archivo"])
        paginas_por_archivo[clave].append(int(row["pagina"]))

filas = []
for (tomo, archivo), paginas in paginas_por_archivo.items():
    filas.append({
        "tomo": int(tomo),
        "archivo": archivo,
        "pagina_min": min(paginas),
        "pagina_max": max(paginas),
        "n_paginas": len(paginas),
    })

filas.sort(key=lambda r: (r["tomo"], r["archivo"]))

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["tomo", "archivo", "pagina_min", "pagina_max", "n_paginas"])
    writer.writeheader()
    writer.writerows(filas)

print(f"Catálogo escrito: {OUTPUT} ({len(filas)} filas)")
print()
print(f"{'tomo':>5} {'archivo':<25} {'min':>6} {'max':>6} {'n_pag':>6}")
print("-" * 55)
for r in filas:
    print(f'{r["tomo"]:>5} {r["archivo"]:<25} {r["pagina_min"]:>6} {r["pagina_max"]:>6} {r["n_paginas"]:>6}')

print()
print("=== Verificación de solapamientos ===")
por_tomo = defaultdict(list)
for r in filas:
    por_tomo[r["tomo"]].append(r)

solapamientos = []
for tomo, archivos in por_tomo.items():
    if len(archivos) < 2:
        continue
    archivos_sorted = sorted(archivos, key=lambda r: r["pagina_min"])
    for i in range(len(archivos_sorted) - 1):
        a = archivos_sorted[i]
        b = archivos_sorted[i + 1]
        if a["pagina_max"] >= b["pagina_min"]:
            solapamientos.append((tomo, a, b))

if solapamientos:
    print(f"Detectados {len(solapamientos)} solapamiento(s):")
    for tomo, a, b in solapamientos:
        print(f'  Tomo {tomo}: {a["archivo"]} llega a {a["pagina_max"]}, {b["archivo"]} empieza en {b["pagina_min"]}')
else:
    print("Sin solapamientos. Esquema A confirmado.")