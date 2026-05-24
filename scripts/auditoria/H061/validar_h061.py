"""H061 — Validación post-refactoring. Correr desde la raíz del repo."""
import pandas as pd
from pathlib import Path

OUT = Path("output/parser")

# 1. Casos y votos: deben ser idénticos al snapshot
for name, expected in [("csjn_casos.csv", 5862), ("csjn_casos_votos.csv", 27336)]:
    df = pd.read_csv(OUT / name)
    status = "OK" if len(df) == expected else f"DIFF ({len(df)} vs {expected})"
    print(f"  {name}: {len(df)} filas — {status}")

# 2. Zonas
df_z = pd.read_csv(OUT / "csjn_casos_zonas.csv")
print(f"  csjn_casos_zonas.csv: {len(df_z)} filas — {'OK' if len(df_z) == 141970 else 'DIFF'}")

# 3. Editorial: nueva estructura
df_e = pd.read_csv(OUT / "csjn_casos_editorial.csv")
print(f"\n  csjn_casos_editorial.csv: {len(df_e)} filas (esperado: 135)")
print(f"  Columnas: {list(df_e.columns)}")
print(f"\n  Subtipos:")
for sub, cnt in df_e["subtipo"].value_counts().items():
    print(f"    {sub:25s}  {cnt}")

# 4. Chequeo: 0 desconocido
n_desc = (df_e["subtipo"] == "desconocido").sum()
if n_desc:
    print(f"\n  ⚠ {n_desc} secciones 'desconocido':")
    print(df_e[df_e["subtipo"] == "desconocido"][["tomo","source_file","linea_ini","linea_fin"]])
else:
    print(f"\n  ✓ 0 desconocido")
