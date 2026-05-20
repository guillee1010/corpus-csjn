# H042 - comparar_b055_fix.py
# Compara CSV productivo vs parcheado campo por campo.
# Foco en firma_raw, n_jueces, voting_pattern.
# Correr desde raiz del repo.

import csv
from pathlib import Path
from collections import Counter

CSV_PROD = Path("output/parser/csjn_casos.csv")
CSV_FIX = Path("output/diagnostico/B055/csjn_casos_b055_fix.csv")

if not CSV_FIX.exists():
    # Intentar path alternativo
    CSV_FIX = Path("scripts/diagnostico/H055/csjn_casos_b055_fix.csv")
    if not CSV_FIX.exists():
        print("No encuentro CSV del fix. Verificar que el parser parcheado")
        print("escriba su output en output/diagnostico/B055/ o ajustar path.")
        raise SystemExit(1)

def load(path):
    with open(path, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

prod = load(CSV_PROD)
fix = load(CSV_FIX)

CAMPOS = ["firma_raw", "n_jueces", "voting_pattern",
          "jueces_mayoria", "jueces_disidencia", "jueces_voto"]

mejoras = []
regresiones = []
otros = []

for caso_id in sorted(prod):
    rp = prod[caso_id]
    rf = fix.get(caso_id)
    if rf is None:
        continue
    cambios = {}
    for c in CAMPOS:
        vp = rp.get(c, "")
        vf = rf.get(c, "")
        if vp != vf:
            cambios[c] = (vp, vf)
    if not cambios:
        continue
    # Clasificar: mejora si n_jueces sube o firma_raw gana punto final
    firma_prod = rp.get("firma_raw", "").strip()
    firma_fix = rf.get("firma_raw", "").strip()
    nj_prod = int(rp.get("n_jueces", 0))
    nj_fix = int(rf.get("n_jueces", 0))

    if nj_fix > nj_prod:
        cat = "mejora_mas_jueces"
    elif nj_fix < nj_prod:
        cat = "regresion_menos_jueces"
    elif firma_fix.endswith(".") and not firma_prod.endswith("."):
        cat = "mejora_firma_limpia"
    elif firma_prod.endswith(".") and not firma_fix.endswith("."):
        cat = "regresion_firma_sucia"
    elif len(firma_fix) < len(firma_prod):
        cat = "mejora_firma_mas_corta"
    elif len(firma_fix) > len(firma_prod):
        cat = "otro_firma_mas_larga"
    else:
        cat = "otro_cambio"

    entry = {"caso_id": caso_id, "cat": cat, "cambios": cambios,
             "nj_prod": nj_prod, "nj_fix": nj_fix}
    if cat.startswith("mejora"):
        mejoras.append(entry)
    elif cat.startswith("regresion"):
        regresiones.append(entry)
    else:
        otros.append(entry)

print(f"Casos en productivo: {len(prod)}")
print(f"Casos en fix: {len(fix)}")
print(f"\nMejoras: {len(mejoras)}")
print(f"Regresiones: {len(regresiones)}")
print(f"Otros cambios: {len(otros)}")

# Desglose por categoria
cats = Counter()
for e in mejoras + regresiones + otros:
    cats[e["cat"]] += 1
print(f"\nDesglose:")
for cat, cnt in cats.most_common():
    print(f"  {cat}: {cnt}")

# Muestra de mejoras (10)
if mejoras:
    print(f"\n--- Muestra mejoras (max 10) ---")
    for e in mejoras[:10]:
        print(f"  {e['caso_id']} [{e['cat']}] nj: {e['nj_prod']} -> {e['nj_fix']}")
        for c, (vp, vf) in e["cambios"].items():
            if c == "firma_raw":
                tp = vp[-60:] if len(vp) > 60 else vp
                tf = vf[-60:] if len(vf) > 60 else vf
                print(f"    {c}: ...{tp}")
                print(f"        -> ...{tf}")
            else:
                print(f"    {c}: {vp} -> {vf}")
        print()

# Muestra de regresiones (todas)
if regresiones:
    print(f"\n--- REGRESIONES (todas) ---")
    for e in regresiones:
        print(f"  {e['caso_id']} [{e['cat']}] nj: {e['nj_prod']} -> {e['nj_fix']}")
        for c, (vp, vf) in e["cambios"].items():
            if c == "firma_raw":
                tp = vp[-60:] if len(vp) > 60 else vp
                tf = vf[-60:] if len(vf) > 60 else vf
                print(f"    {c}: ...{tp}")
                print(f"        -> ...{tf}")
            else:
                print(f"    {c}: {vp} -> {vf}")
        print()
