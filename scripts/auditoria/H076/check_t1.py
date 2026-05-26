import csv
r = list(csv.DictReader(open('output/parser/csjn_casos.csv', encoding='utf-8')))
targets = ['329_p472','329_p2063','329_p2218','329_p4769',
           '331_p1468','345_p154','345_p296','345_p378',
           '345_p599','346_p1086','348_p60','348_p259','348_p473']
for cid in targets:
    matches = [x for x in r if x['caso_id_canonico'] == cid]
    if not matches:
        print(f"{cid:<14} NO ENCONTRADO")
        continue
    c = matches[0]
    print(f"{c['caso_id_canonico']:<14} li={c['linea_inicio']:>5} lf={c['linea_fin']:>5} lfr={c['linea_fin_real']:>5} st={c['status_localizacion'][:40]}")
