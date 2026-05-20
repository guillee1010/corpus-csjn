# H042 - Paso 0: Re-cuantificar B055 contra CSV actual (post-H041).
# B055 = firma_raw no vacio pero truncado (sin punto final).
# El universo de 345 casos es de H033 (pre-fix B013). Necesitamos
# saber cuantos quedan despues de 6 sesiones de fixes.

import csv
from pathlib import Path
from collections import Counter

CSV_CASOS = Path("output/parser/csjn_casos.csv")

with open(CSV_CASOS, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total filas en CSV: {len(rows)}")

# --- Universo B055: firma_raw no vacio, no termina en punto ---
b055 = []
for r in rows:
    firma = r.get("firma_raw", "").strip()
    if not firma:
        continue
    if not firma.rstrip().endswith("."):
        b055.append(r)

print(f"\nB055 (firma_raw no vacio, sin punto final): {len(b055)}")

if not b055:
    print("B055 resuelto de facto. Cerrar bug.")
    raise SystemExit(0)

# --- Distribucion por n_jueces ---
dist_jueces = Counter(int(r.get("n_jueces", 0)) for r in b055)
print(f"\nDistribucion n_jueces en B055:")
for k in sorted(dist_jueces):
    print(f"  n_jueces={k}: {dist_jueces[k]}")

# --- Distribucion por tomo ---
dist_tomo = Counter(r.get("tomo", "?") for r in b055)
print(f"\nDistribucion por tomo (top 10):")
for tomo, cnt in dist_tomo.most_common(10):
    print(f"  tomo {tomo}: {cnt}")

# --- Muestra de 10 casos con firma truncada ---
print(f"\n--- Muestra (primeros 10) ---")
for r in b055[:10]:
    caso = r.get("caso_id_canonico", r.get("caso_id", "?"))
    firma = r.get("firma_raw", "")
    nj = r.get("n_jueces", "?")
    vp = r.get("voting_pattern", "?")
    tail = firma[-80:] if len(firma) > 80 else firma
    print(f"  {caso} | n_jueces={nj} | vp={vp}")
    print(f"    firma_tail: ...{tail}")
    print()

# --- Cuantos tienen por_ello_text? ---
con_disp = sum(1 for r in b055 if r.get("por_ello_text", "").strip())
sin_disp = len(b055) - con_disp
print(f"Con por_ello_text: {con_disp}")
print(f"Sin por_ello_text: {sin_disp}")

# --- Ultimos 3 caracteres de firma_raw ---
print(f"\n--- Ultimos 3 caracteres de firma_raw ---")
terminaciones = Counter(r.get("firma_raw", "").strip()[-3:] for r in b055)
for term, cnt in terminaciones.most_common(15):
    print(f"  '{term}': {cnt}")
