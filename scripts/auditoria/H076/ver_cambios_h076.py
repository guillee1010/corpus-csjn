import csv

pre = {r['caso_id_canonico']: r for r in csv.DictReader(open('archivo/data/csjn_casos_pre_h076.csv', encoding='utf-8'))}
post = {r['caso_id_canonico']: r for r in csv.DictReader(open('output/parser/csjn_casos.csv', encoding='utf-8'))}

cols = ['status_localizacion', 'linea_inicio', 'word_count', 'outcome', 'voting_pattern', 'case_name_indice']

changed = []
for cid in pre:
    if pre[cid]['status_localizacion'] != post[cid]['status_localizacion']:
        changed.append(cid)

print(f"Casos cambiados: {len(changed)}\n")

for cid in changed:
    p, q = pre[cid], post[cid]
    print(f"{'='*80}")
    print(f"  {cid}  —  {p['case_name_indice'][:60]}")
    print(f"{'='*80}")
    for c in cols:
        v_pre = p.get(c, '')
        v_post = q.get(c, '')
        if v_pre != v_post:
            if c == 'linea_inicio':
                delta = int(v_post) - int(v_pre)
                print(f"  {c:<25} {v_pre:>8} -> {v_post:>8}  (trim {delta} lineas)")
            elif c == 'word_count':
                delta = int(v_post) - int(v_pre)
                print(f"  {c:<25} {v_pre:>8} -> {v_post:>8}  ({delta:+d} words)")
            else:
                print(f"  {c:<25} {v_pre[:40]:>40} -> {v_post[:40]}")
    print()
