import csv

pre = {r['caso_id_canonico']: r for r in csv.DictReader(open('output/parser/csjn_casos_pre_h076.csv', encoding='utf-8'))}
post = {r['caso_id_canonico']: r for r in csv.DictReader(open('output/parser/csjn_casos.csv', encoding='utf-8'))}

cambios = 0
for cid in pre:
    s_pre = pre[cid]['status_localizacion']
    s_post = post[cid]['status_localizacion']
    if s_pre != s_post:
        print(cid.ljust(18), s_pre[:40].rjust(42), "->", s_post[:40])
        cambios += 1

print()
print("Total cambios status_loc:", cambios)
pre_ancla = sum(1 for r in pre.values() if 'ancla_catalogo' in r['status_localizacion'])
post_ancla = sum(1 for r in post.values() if 'ancla_catalogo' in r['status_localizacion'])
print("ancla_catalogo:", pre_ancla, "->", post_ancla)

# Diff de otras columnas afectadas
cols = ['linea_inicio', 'word_count', 'outcome', 'voting_pattern', 'firma_raw']
n_other = 0
for cid in pre:
    diffs = []
    for c in cols:
        if pre[cid].get(c, '') != post[cid].get(c, ''):
            diffs.append(c)
    if diffs:
        n_other += 1
print("Casos con cambios en otras columnas:", n_other)

# Zonas
pre_z = sum(1 for _ in csv.DictReader(open('output/parser/csjn_casos_zonas.csv', encoding='utf-8')))
print("Zonas pre: 141055 -> post:", pre_z)
