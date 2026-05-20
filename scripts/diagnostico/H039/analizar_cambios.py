"""Analiza los 72 cambios de outcome entre productivo y H039."""
import csv
from collections import Counter

with open("output/parser/csjn_casos.csv", encoding="utf-8") as f:
    prod = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}
with open("output/diagnostico/H039/csjn_casos_h039.csv", encoding="utf-8") as f:
    nuevo = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

cambios = []
for cid in sorted(prod):
    if cid not in nuevo:
        continue
    p, nu = prod[cid], nuevo[cid]
    if p["tipo_entrada"] != "fallo":
        continue
    if p["outcome"] != nu["outcome"]:
        pet_nuevo = nu["por_ello_text"][:90]
        pet_viejo = p["por_ello_text"][:90]
        cambios.append({
            "cid": cid,
            "out_antes": p["outcome"],
            "out_despues": nu["outcome"],
            "vp_antes": p["voting_pattern"],
            "vp_despues": nu["voting_pattern"],
            "pet_nuevo": pet_nuevo,
            "pet_viejo": pet_viejo,
        })

print(f"Total cambios outcome: {len(cambios)}")
print()

# Agrupar por inicio del por_ello_text nuevo (para ver qué variante matcheó)
starts = Counter()
for c in cambios:
    words = c["pet_nuevo"].split()[:3]
    starts[" ".join(words)] += 1

print("por_ello_text nuevo empieza con:")
for k, v in starts.most_common():
    print(f"  '{k}': {v}")
print()

# Desglose: regressions (outcome specific→otro) vs upgrades (sin_dispositivo→algo)
regr = [c for c in cambios if c["out_antes"] != "sin_dispositivo" and c["out_antes"] != "otro"]
upgr = [c for c in cambios if c["out_antes"] == "sin_dispositivo"]
neutro = [c for c in cambios if c["out_antes"] == "otro"]

print(f"Outcome regression (specific→otro): {len(regr)}")
for c in regr[:15]:
    print(f"  {c['cid']}: {c['out_antes']}=>{c['out_despues']} | nuevo: {c['pet_nuevo'][:70]}")
    print(f"    viejo: {c['pet_viejo'][:70]}")
print()

print(f"Upgrade (sin_dispositivo→algo): {len(upgr)}")
for c in upgr[:10]:
    print(f"  {c['cid']}: {c['out_antes']}=>{c['out_despues']} vp={c['vp_despues']} | {c['pet_nuevo'][:70]}")
print()

print(f"Neutro (otro→otro_distinto): {len(neutro)}")
for c in neutro[:5]:
    print(f"  {c['cid']}: {c['out_antes']}=>{c['out_despues']} | {c['pet_nuevo'][:70]}")
