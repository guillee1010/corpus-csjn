import csv

def load(path):
    with open(path, encoding="utf-8-sig") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

pre = load("csjn_casos_PRE.csv")
post = load("output/parser/csjn_casos.csv")

campos = ["n_jueces", "firma_raw", "voting_pattern", "outcome",
          "status_localizacion", "n_votos_svoto", "n_disidencias"]

cambios = 0
casos_changed = set()
lines = []

for cid in sorted(pre.keys()):
    for c in campos:
        vp = pre[cid].get(c, "")
        vn = post[cid].get(c, "")
        if vp != vn:
            cambios += 1
            casos_changed.add(cid)
            if c == "firma_raw":
                vp = (vp[:50] or "(vacio)")
                vn = (vn[:50] or "(vacio)")
            lines.append(f"{cid}.{c}:  {vp}  ->  {vn}")

summary = f"Total cambios: {cambios}\nCasos afectados: {len(casos_changed)}\n"
with open("diff_b089_resultado.txt", "w", encoding="utf-8") as f:
    f.write(summary + "\n")
    f.write("\n".join(lines))

print(summary)
print(f"Detalle guardado en diff_b089_resultado.txt")
