"""
diag-dictamen.py
================
Cruza dictamen_presente con voting_pattern y otros indicadores para ver
cuán sistémico es el problema "el bloque arranca con sumario+dictamen y
el parser asume que arranca con el fallo".

Imprime:
  1. Cuántos fallos tienen dictamen_presente=True en total.
  2. Cuántos sin_firma tienen dictamen_presente.
  3. Distribución cruzada dictamen x voting_pattern.
  4. Distribución cruzada dictamen x outcome (top 10 outcomes).
  5. Promedio de wc_mayoria por dictamen_presente (por si hay sesgo de tamaño).

Uso:
    python diag-dictamen.py csjn_casos_v16.csv
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


def main(ruta_csv):
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    with open(ruta_csv, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        filas = list(reader)

    if "dictamen_presente" not in cols:
        print("ERROR: no existe columna 'dictamen_presente'")
        print(f"Columnas: {cols}")
        sys.exit(1)

    total = len(filas)

    # Normalizar dictamen_presente (puede venir como "True"/"False" string)
    def es_dict(r):
        v = (r["dictamen_presente"] or "").strip().lower()
        return v in ("true", "1", "yes", "si", "sí")

    con_dict = [r for r in filas if es_dict(r)]
    sin_dict = [r for r in filas if not es_dict(r)]

    print("=" * 60)
    print("DICTAMEN PRESENTE EN EL CORPUS")
    print("=" * 60)
    print(f"Total fallos:            {total}")
    print(f"Con dictamen_presente:   {len(con_dict)} ({len(con_dict)/total*100:.1f}%)")
    print(f"Sin dictamen_presente:   {len(sin_dict)} ({len(sin_dict)/total*100:.1f}%)")
    print()

    # Cruce con voting_pattern
    print("=" * 60)
    print("DICTAMEN x VOTING_PATTERN")
    print("=" * 60)
    patterns = sorted(set(r["voting_pattern"] for r in filas))
    print(f"{'voting_pattern':20s} {'con_dict':>10s} {'sin_dict':>10s} {'%con_dict':>10s}")
    for p in patterns:
        con = sum(1 for r in con_dict if r["voting_pattern"] == p)
        sin = sum(1 for r in sin_dict if r["voting_pattern"] == p)
        tot_p = con + sin
        pct = con / tot_p * 100 if tot_p else 0
        print(f"{p:20s} {con:>10d} {sin:>10d} {pct:>9.1f}%")
    print()

    # Cruce con outcome
    print("=" * 60)
    print("DICTAMEN x OUTCOME (top 10)")
    print("=" * 60)
    outcomes_total = Counter(r["outcome"] for r in filas).most_common(10)
    print(f"{'outcome':30s} {'con_dict':>10s} {'sin_dict':>10s} {'%con_dict':>10s}")
    for outcome, _ in outcomes_total:
        con = sum(1 for r in con_dict if r["outcome"] == outcome)
        sin = sum(1 for r in sin_dict if r["outcome"] == outcome)
        tot_o = con + sin
        pct = con / tot_o * 100 if tot_o else 0
        print(f"{outcome:30s} {con:>10d} {sin:>10d} {pct:>9.1f}%")
    print()

    # Promedio wc_mayoria
    def to_int(v):
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    wc_con = [to_int(r["wc_mayoria"]) for r in con_dict]
    wc_sin = [to_int(r["wc_mayoria"]) for r in sin_dict]

    print("=" * 60)
    print("WC_MAYORIA por dictamen_presente")
    print("=" * 60)
    if wc_con:
        prom_con = sum(wc_con) / len(wc_con)
        med_con = sorted(wc_con)[len(wc_con) // 2]
    else:
        prom_con = med_con = 0
    if wc_sin:
        prom_sin = sum(wc_sin) / len(wc_sin)
        med_sin = sorted(wc_sin)[len(wc_sin) // 2]
    else:
        prom_sin = med_sin = 0
    print(f"con_dict: promedio={prom_con:.0f}  mediana={med_con}")
    print(f"sin_dict: promedio={prom_sin:.0f}  mediana={med_sin}")
    print()

    # Caso clave: fallos con dictamen + outcome="otro" + voting_pattern="sin_firma"
    # Estos son los más sospechosos de parseo desde el lugar equivocado
    sospechosos = [r for r in con_dict
                   if r["voting_pattern"] == "sin_firma"
                   and r["outcome"] == "otro"]
    print("=" * 60)
    print("SOSPECHOSOS: con_dict + sin_firma + outcome='otro'")
    print("=" * 60)
    print(f"Total: {len(sospechosos)}")
    print()

    # Distribucion por tomo de los sospechosos
    print("Distribucion por tomo de sospechosos:")
    sospechosos_por_tomo = Counter(r["tomo"] for r in sospechosos)
    for tomo in sorted(sospechosos_por_tomo):
        print(f"  tomo {tomo}: {sospechosos_por_tomo[tomo]}")
    print()

    # Lectura del resultado
    print("=" * 60)
    print("LECTURA")
    print("=" * 60)
    pct_con_dict = len(con_dict) / total * 100
    if pct_con_dict > 50:
        print(f"El {pct_con_dict:.0f}% del corpus tiene dictamen previo.")
        print("Si la hipotesis es correcta, el problema afecta a la mayoria")
        print("del corpus, no solo a los 573 sin_firma.")
    else:
        print(f"Solo el {pct_con_dict:.0f}% del corpus tiene dictamen previo.")
        print("El problema afecta una porcion menor del corpus.")
    print()
    sf_con_dict = sum(1 for r in con_dict if r["voting_pattern"] == "sin_firma")
    sf_sin_dict = sum(1 for r in sin_dict if r["voting_pattern"] == "sin_firma")
    if sf_con_dict + sf_sin_dict > 0:
        ratio = sf_con_dict / (sf_con_dict + sf_sin_dict) * 100
        print(f"De los sin_firma, el {ratio:.0f}% tiene dictamen previo.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python diag-dictamen.py csjn_casos_v16.csv")
        sys.exit(1)
    main(sys.argv[1])
