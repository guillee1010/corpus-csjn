#!/usr/bin/env python3
"""
kappa_confiabilidad.py - Cohen's kappa (parser <-> gold humano) con IC bootstrap, por variable.

Mide la concordancia corregida por azar entre la prediccion del parser y el gold codificado a mano.
NO es kappa de doble codificacion (esa valida la reproducibilidad del codebook, requiere 2da codificacion).

Uso (PowerShell):
  python scripts\\diagnostico\\kappa_confiabilidad.py `
    --gold .\\ruta\\planilla_M20_LIMPIA_n300__rebuild.xlsx `
    --recursos .\\output\\parser\\csjn_casos_recursos.csv `
    --out .\\output\\confiabilidad\\kappa_resultados.csv

Requiere: pandas, numpy, openpyxl (si el gold es .xlsx).
"""
import argparse, re
import numpy as np
import pandas as pd

# (nombre, columna_gold, fuente_pred, columna_pred)
# 'recursos' = csjn_casos_recursos.csv. Para sumar cf/dictamen/materia, agregar la fuente
# en SOURCES (abajo, en main) y descomentar la fila correspondiente.
VARIABLES = [
    ("es_revision_fondo", "cod_es_revision_fondo", "recursos", "es_revision_fondo"),
    ("via_recurso",       "cod_via_recurso",       "recursos", "via_recurso"),
    ("disposicion",       "cod_disposicion",       "recursos", "disposicion"),
    ("parte_ganadora",    "cod_parte_ganadora",    "recursos", "parte_ganadora"),
    ("reenvia",           "cod_reenvia",           "recursos", "reenvia"),
    # ("cuestion_federal", "cod_cf_norm",       "cf",       "<col_pred>"),
    # ("dictamen",         "cod_dictamen_norm", "dictamen", "<col_pred>"),
    # ("materia",          "cod_materia",       "materia",  "materia"),
]

NA = {"", "-", "revisar"}
def norm(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return None
    x = str(x).strip().lower()
    if x in NA or re.fullmatch(r"\d+", x): return None
    return x

def kappa(y1, y2):
    cats = sorted(set(y1) | set(y2)); idx = {c: i for i, c in enumerate(cats)}; n = len(y1)
    m = np.zeros((len(cats), len(cats)))
    for a, b in zip(y1, y2): m[idx[a], idx[b]] += 1
    po = np.trace(m) / n
    pe = ((m.sum(1) / n) * (m.sum(0) / n)).sum()
    return (None if pe >= 1 else (po - pe) / (1 - pe)), po

def boot_ci(y1, y2, B=5000, seed=42):
    rng = np.random.default_rng(seed)
    y1 = np.array(y1); y2 = np.array(y2); n = len(y1); ks = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        k, _ = kappa(list(y1[i]), list(y2[i]))
        if k is not None: ks.append(k)
    lo, hi = np.percentile(ks, [2.5, 97.5])
    return lo, hi, 1 - len(ks) / B

def landis_koch(k):
    return ("casi perfecto" if k >= .8 else "sustancial" if k >= .6 else
            "moderado" if k >= .4 else "aceptable-bajo" if k >= .2 else "pobre")

def load_table(path):
    return (pd.read_excel(path, dtype=str) if path.lower().endswith((".xlsx", ".xlsm"))
            else pd.read_csv(path, dtype=str))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--recursos", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--boot", type=int, default=5000)
    args = ap.parse_args()

    gold = load_table(args.gold)
    gold = gold[gold["caso_id_canonico"].notna()].set_index("caso_id_canonico")
    SOURCES = {"recursos": load_table(args.recursos).set_index("caso_id_canonico")}

    rows = []
    for name, gcol, skey, pcol in VARIABLES:
        if skey not in SOURCES or gcol not in gold.columns: continue
        src = SOURCES[skey]
        g = gold[gcol].map(norm)
        p = gold.index.to_series().map(src[pcol]).map(norm)
        df = pd.DataFrame({"g": g, "p": p}).dropna()
        if len(df) == 0: continue
        k, po = kappa(list(df.g), list(df.p))
        lo, hi, deg = boot_ci(list(df.g), list(df.p), B=args.boot)
        rows.append({"variable": name, "n": len(df), "acuerdo": round(po, 3),
                     "kappa": round(k, 3), "ic95_lo": round(lo, 3), "ic95_hi": round(hi, 3),
                     "lectura": landis_koch(k), "deg_pct": round(deg * 100, 1)})
    res = pd.DataFrame(rows)
    pd.set_option("display.width", 140)
    print(res.to_string(index=False))
    if args.out:
        res.to_csv(args.out, index=False, encoding="utf-8")
        print(f"\n-> {args.out}")

if __name__ == "__main__":
    main()
