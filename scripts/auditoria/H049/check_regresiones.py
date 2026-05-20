import csv

with open("output/auditoria/H049/csjn_casos_b072.csv", encoding="utf-8") as f:
    rows = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

for caso in ["329_p2037", "346_p610"]:
    r = rows[caso]
    print(f"=== {caso} ===")
    print(f"  n_jueces: {r['n_jueces']}")
    print(f"  vp: {r['voting_pattern']}")
    print(f"  firma_raw: {r['firma_raw'][:400]}")
    print(f"  jueces: {r['jueces']}")
    print()
