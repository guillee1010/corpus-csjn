import csv

# Load old (need the pre-H058 backup)
# For now, compare against what we know changed
with open('output/parser/csjn_casos.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

# Cases with pista_fin = editorial_siguiente
ed = [r for r in rows if r['pista_fin'] == 'editorial_siguiente']
print(f'Casos con pista editorial_siguiente: {len(ed)}')
for r in ed:
    print(f'  {r["caso_id_canonico"]}: wc={r["word_count"]}, vp={r["voting_pattern"]}, sd={r["outcome"]}')

print()
# Cases that are now sin_dispositivo
sd = [r for r in rows if r['outcome'] == 'sin_dispositivo']
print(f'sin_dispositivo: {len(sd)}')

# Cases that are blank voting_pattern
blank = [r for r in rows if r['voting_pattern'] == '']
print(f'voting_pattern vacio: {len(blank)}')
