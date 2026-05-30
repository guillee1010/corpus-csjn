#!/usr/bin/env python3
# scripts/diagnostico/H092/check_columna.py
# Verifica que csjn_casos.csv (nuevo) sea identico al golden SALVO la columna
# causa_inadmisibilidad. Diagnostico, no escribe nada.
#   python scripts\diagnostico\H092\check_columna.py
#   (overrides: --golden RUTA  --new RUTA)
import argparse, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DEF_GOLDEN = ROOT / "scripts" / "tests" / "golden" / "csjn_casos.csv"
DEF_NEW    = ROOT / "output" / "parser" / "csjn_casos.csv"
NUEVA = "causa_inadmisibilidad"

ap = argparse.ArgumentParser()
ap.add_argument("--golden", default=str(DEF_GOLDEN))
ap.add_argument("--new",    default=str(DEF_NEW))
a = ap.parse_args()
g, n = Path(a.golden), Path(a.new)

for label, p in (("golden", g), ("new", n)):
    if not p.exists():
        print(f"[FALTA] {label}: {p}")
        print("csjn_casos.csv encontrados bajo el repo:")
        for h in ROOT.rglob("csjn_casos.csv"):
            print("   ", h)
        print("Pasá la ruta correcta con --golden / --new.")
        sys.exit(1)

old = pd.read_csv(g, dtype=str, keep_default_na=False)
new = pd.read_csv(n, dtype=str, keep_default_na=False)
nuevas = [c for c in new.columns if c not in old.columns]
faltan = [c for c in old.columns if c not in new.columns]
print("columnas nuevas:   ", nuevas)
print("columnas faltantes:", faltan)
print("filas golden / new:", len(old), "/", len(new))
if nuevas == [NUEVA] and not faltan:
    igual = new.drop(columns=[NUEVA]).equals(old)
    print("resto identico:", igual)
    if igual:
        print(">>> LIMPIO: lo unico que cambio es la columna", NUEVA)
    sys.exit(0 if igual else 2)
print("[OJO] el set de columnas cambio mas alla de la esperada (", NUEVA, ")")
sys.exit(2)
