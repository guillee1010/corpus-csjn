"""Verificación B082 v3: muestra por_ello_text y considerando viejo/nuevo
para los 19 casos con outcome cambiado."""

import pandas as pd

old = pd.read_csv("output/parser/csjn_casos_pre_b082.csv")
new = pd.read_csv("output/parser/csjn_casos.csv")

key = "caso_id_canonico"
fo = old[old["tipo_entrada"] == "fallo"].set_index(key)
fn = new[new["tipo_entrada"] == "fallo"].set_index(key)

changed = []
for cid in fo.index.intersection(fn.index):
    if fo.loc[cid, "outcome"] != fn.loc[cid, "outcome"]:
        changed.append(cid)

print(f"Casos con outcome cambiado: {len(changed)}\n")

for cid in changed:
    print(f"{'='*70}")
    print(f"CASO: {cid}")
    print(f"  outcome: {fo.loc[cid, 'outcome']} → {fn.loc[cid, 'outcome']}")
    print(f"  voting_pattern: {fn.loc[cid, 'voting_pattern']}")
    print(f"  wc_cons: {fo.loc[cid, 'wc_considerando']} → {fn.loc[cid, 'wc_considerando']}")
    print(f"  por_ello_text: {str(fn.loc[cid, 'por_ello_text'])[:200]}")
    print(f"  cons VIEJO (últimos 300 chars):")
    ct_old = str(fo.loc[cid, "considerando_text"])
    print(f"    ...{ct_old[-300:]}")
    print(f"  cons NUEVO (últimos 300 chars):")
    ct_new = str(fn.loc[cid, "considerando_text"])
    print(f"    ...{ct_new[-300:]}")
    print()
