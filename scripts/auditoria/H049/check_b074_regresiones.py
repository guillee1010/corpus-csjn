import csv

base_path = "output/parser/csjn_casos.csv"
nuevo_path = "output/auditoria/H049/csjn_casos_b074.csv"

with open(base_path, encoding="utf-8") as f:
    base = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}
with open(nuevo_path, encoding="utf-8") as f:
    nuevo = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

regresiones = [
    "331_p1468", "343_p1388", "343_p2243",
    "344_p220", "344_p2835", "347_p818",
]

for caso in regresiones:
    b = base[caso]
    n = nuevo[caso]
    print(f"=== {caso} ===")
    print(f"  BASE: vp={b['voting_pattern']} n_j={b['n_jueces']} lfr={b['linea_fin_real']} pista={b['pista_fin']}")
    print(f"  NUEVO: vp={n['voting_pattern']} n_j={n['n_jueces']} lfr={n['linea_fin_real']} pista={n['pista_fin']}")
    print(f"  li={b['linea_inicio']} lf={b['linea_fin']}")
    print(f"  apertura={b.get('apertura_tipo','')}")
    print(f"  BASE firma: {b['firma_raw'][:150]}")
    print(f"  NUEVO firma: {n['firma_raw'][:150]}")
    print()
