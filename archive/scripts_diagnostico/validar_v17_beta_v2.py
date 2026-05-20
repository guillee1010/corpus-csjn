# validar_v17_beta_v2.py
# Validacion de csjn_casos_v17_beta_v2.csv.
# Output EXCLUSIVO a archivo de texto, no a consola.

import pandas as pd
from pathlib import Path

CSV = Path("paginas/csjn_casos_v17_beta_v2.csv")
OUTPUT = Path("validacion_v17_beta_v2.txt")

df = pd.read_csv(CSV, low_memory=False)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("=" * 70 + "\n")
    f.write(f"VALIDACION: {CSV}\n")
    f.write("=" * 70 + "\n")
    f.write(f"Total casos: {len(df)}\n\n")

    f.write("-- voting_pattern --\n")
    for k, v in df["voting_pattern"].value_counts(dropna=False).items():
        f.write(f"  {k}: {v}\n")
    f.write("\n")

    f.write("-- tipo_entrada --\n")
    for k, v in df["tipo_entrada"].value_counts(dropna=False).items():
        f.write(f"  {k}: {v}\n")
    f.write("\n")

    n_dictamen = (df["dictamen_presente"] == 1).sum()
    f.write(f"Casos con dictamen detectado: {n_dictamen}\n")

    if n_dictamen > 0:
        s = df[df["wc_dictamen"] > 0]["wc_dictamen"]
        f.write(f"  wc_dictamen mediana: {s.median()}\n")
        f.write(f"  wc_dictamen p25: {s.quantile(0.25)}\n")
        f.write(f"  wc_dictamen p75: {s.quantile(0.75)}\n")
        f.write(f"  wc_dictamen max: {s.max()}\n")

    fallos = df[df["tipo_entrada"] == "fallo"]
    f.write(f"\nTotal fallos: {len(fallos)}\n")
    f.write(f"  word_count mediana: {fallos['word_count'].median()}\n")
    f.write(f"  wc_fallo_neto mediana: {fallos['wc_fallo_neto'].median()}\n")

    n_dict_come_todo = (df["wc_dictamen"] >= df["word_count"]).sum()
    f.write(f"\nCasos donde wc_dictamen >= word_count (dictamen comio todo): {n_dict_come_todo}\n")
    n_dict_come_casi_todo = ((df["wc_dictamen"] > 0) & (df["wc_dictamen"] / df["word_count"].replace(0, 1) > 0.9)).sum()
    f.write(f"Casos donde dictamen es >90% del bloque: {n_dict_come_casi_todo}\n")

    f.write("\n-- Comparacion con baseline v17 beta v1 --\n")
    f.write("v17 beta v1: 312 sin_firma, mediana wc_dictamen 1219\n")
    sf = (df["voting_pattern"] == "sin_firma").sum()
    f.write(f"v17 beta v2: {sf} sin_firma\n")
    delta = sf - 312
    signo = "+" if delta >= 0 else ""
    f.write(f"Delta sin_firma: {signo}{delta} (esperado: cercano a 0 o negativo)\n")
