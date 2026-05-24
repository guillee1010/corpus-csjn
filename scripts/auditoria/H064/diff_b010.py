# diff_b010.py
import csv

pre = {}
for r in csv.DictReader(open("output/parser/csjn_casos_pre_b010.csv", encoding="utf-8")):
    if r["wc_considerando"]:
        pre[r["caso_id_canonico"]] = int(r["wc_considerando"])

post = {}
for r in csv.DictReader(open("output/parser/csjn_casos.csv", encoding="utf-8")):
    if r["wc_considerando"]:
        post[r["caso_id_canonico"]] = int(r["wc_considerando"])

cambios = [(k, pre.get(k, 0), post.get(k, 0)) for k in post if post.get(k, 0) != pre.get(k, 0)]
red = sorted([c for c in cambios if c[2] < c[1]], key=lambda x: x[1] - x[2], reverse=True)
aum = [c for c in cambios if c[2] > c[1]]
a0 = [c for c in cambios if c[2] == 0]

print(f"Casos con cambio: {len(cambios)}")
print(f"Reducciones: {len(red)}")
print(f"Aumentos: {len(aum)}")
print(f"Casos que van a 0: {len(a0)}")
if a0:
    for c in a0[:5]:
        print(f"  {c}")

print(f"\nTop 5 reducciones:")
for c in red[:5]:
    print(f"  {c[0]}: {c[1]} -> {c[2]}")

print(f"\nCasos auditados:")
print(f"  339_p444: {pre.get('339_p444', '?')} -> {post.get('339_p444', '?')}")
print(f"  341_p929: {pre.get('341_p929', '?')} -> {post.get('341_p929', '?')}")
