"""Compara zonas pre vs post B076."""
import csv
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PRE  = REPO / "output" / "parser" / "csjn_casos_zonas_pre_b076.csv"
POST = REPO / "output" / "parser" / "csjn_casos_zonas.csv"

def cargar(ruta):
    d = {}
    with open(ruta, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cid = r["caso_id_canonico"]
            d.setdefault(cid, Counter())
            d[cid][r["zona"]] += int(r["wc"])
    return d

pre = cargar(PRE)
post = cargar(POST)

delta_global = Counter()
regresiones = []

for cid in pre:
    zonas_all = set(list(pre[cid]) + list(post.get(cid, {})))
    for z in zonas_all:
        d = post.get(cid, {}).get(z, 0) - pre[cid].get(z, 0)
        if d != 0:
            delta_global[z] += d
            if z in ("cuerpo", "dispositivo", "voto_separado") and d != 0:
                regresiones.append((cid, z, d))

print("DELTA WC POR ZONA (global):")
for z in sorted(delta_global):
    d = delta_global[z]
    print(f"  {z:<28} {'+' if d > 0 else ''}{d}")

# Segmentos totales
def contar_segs(ruta):
    with open(ruta, encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))

print(f"\nSegmentos: {contar_segs(PRE)} -> {contar_segs(POST)}")

print(f"\nREGRESIONES (cuerpo/disp/voto): {len(regresiones)}")
for cid, z, d in regresiones[:20]:
    print(f"  {cid}: {z} {d:+d}")
