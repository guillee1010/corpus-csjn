import csv

casos_ver = ['330_p120','329_p432','329_p440','329_p1307','329_p4811']
campos = ['firma_raw','outcome','voting_pattern','n_jueces','wc_mayoria','wc_votos','word_count','posiciones','pista_fin','linea_fin_real']

vivo, nuevo = {}, {}
with open('output\\parser\\csjn_casos.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f): vivo[r['caso_id_canonico']] = {c: r.get(c,'') for c in campos}
with open('output\\diagnostico\\H040\\csjn_casos.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f): nuevo[r['caso_id_canonico']] = {c: r.get(c,'') for c in campos}

for caso in casos_ver:
    v, n = vivo.get(caso,{}), nuevo.get(caso,{})
    print(f'=== {caso} ===')
    for c in campos:
        val_v = (v.get(c,'') or '')[:80]
        val_n = (n.get(c,'') or '')[:80]
        if val_v != val_n:
            print(f'  {c:<18} VIVO: {val_v}')
            print(f'  {"":18} H040: {val_n} <<')
        else:
            print(f'  {c:<18} {val_v}')
    print()
