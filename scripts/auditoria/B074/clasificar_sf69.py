"""
Reclasificación de los sin_firma post-B074v5.
Reproduce la clasificación H049 sobre el CSV actualizado.

Categorías:
  - bloque_vacío: span ≤ 4
  - bloque_corto: span < 20
  - sin_zona_fallo: sin apertura, sin fecha, sin considerando en el bloque
  - firma_no_detectada: tiene apertura o fecha pero firma no encontrada

Uso:
  python clasificar_sf69.py --casos <csjn_casos.csv>
"""
import csv, argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--casos', required=True)
    a = p.parse_args()

    sf = []
    with open(a.casos, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('tipo_entrada','fallo') != 'fallo':
                continue
            if row['voting_pattern'] != 'sin_firma':
                continue
            li = int(row['linea_inicio'])
            lfr = int(row['linea_fin_real'])
            span = lfr - li
            sf.append({
                'caso_id': row['caso_id_canonico'],
                'tomo': int(row['tomo']),
                'span': span,
                'pista_fin': row['pista_fin'],
                'apertura_tipo': row['apertura_tipo'],
                'status_loc': row['status_localizacion'],
                'li': li, 'lfr': lfr,
                'lf': int(row['linea_fin']) if row['linea_fin'] else 0,
            })

    # Clasificar
    vacios, cortos, sin_zona, firma_no_det = [], [], [], []
    for c in sf:
        if c['span'] <= 4:
            c['cat'] = 'bloque_vacío'
            vacios.append(c)
        elif c['span'] < 20:
            c['cat'] = 'bloque_corto'
            cortos.append(c)
        elif c['apertura_tipo'] == '' and 'ancla_catalogo' in c['status_loc']:
            c['cat'] = 'sin_zona_fallo'
            sin_zona.append(c)
        else:
            c['cat'] = 'firma_no_detectada'
            firma_no_det.append(c)

    print(f"=== Clasificación sin_firma post-B074v5 ({len(sf)} casos) ===\n")
    print(f"  firma_no_detectada: {len(firma_no_det)}")
    print(f"  sin_zona_fallo:    {len(sin_zona)}")
    print(f"  bloque_corto:      {len(cortos)}")
    print(f"  bloque_vacío:      {len(vacios)}")
    print(f"\n  Piso irrecuperables: ~{len(vacios) + len(cortos) + len([s for s in sin_zona if s['span'] < 30])}")

    # Detalle por categoría
    for cat_name, cat_list in [('firma_no_detectada', firma_no_det),
                                ('sin_zona_fallo', sin_zona),
                                ('bloque_corto', cortos),
                                ('bloque_vacío', vacios)]:
        if not cat_list:
            continue
        print(f"\n── {cat_name} ({len(cat_list)}) ──")
        for c in sorted(cat_list, key=lambda x: (x['tomo'], x['caso_id'])):
            print(f"  {c['caso_id']:15s} span={c['span']:4d}  pista={c['pista_fin']:25s}  status={c['status_loc']}")

    # Distribución por tomo
    print(f"\n── Distribución por tomo ──")
    tomos = {}
    for c in sf:
        tomos.setdefault(c['tomo'], []).append(c)
    for t in sorted(tomos):
        cats = {}
        for c in tomos[t]:
            cats[c['cat']] = cats.get(c['cat'], 0) + 1
        desc = ', '.join(f"{v} {k}" for k, v in sorted(cats.items()))
        print(f"  {t}: {len(tomos[t]):2d} ({desc})")

if __name__ == '__main__':
    main()
