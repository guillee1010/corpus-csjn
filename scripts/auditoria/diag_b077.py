import csv
with open('output/parser/csjn_casos.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
sf = [r['caso_id_canonico'] for r in rows if r['voting_pattern']=='sin_firma']
ed = [r for r in rows if r['pista_fin']=='editorial_siguiente']
print(f'sin_firma: {len(sf)}')
print(f'editorial_siguiente: {len(ed)}')
for r in ed:
    cid = r['caso_id_canonico']
    wc = r['word_count']
    vp = r['voting_pattern']
    li = r['linea_inicio']
    print(f'  {cid}: wc={wc}, vp={vp}, li={li}')
