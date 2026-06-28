#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_recuperados_H109.py  --  lee los 28 casos recuperados por B115
directo del golden canónico (output/parser/csjn_casos.csv) y muestra,
por caso: carátula, fecha, outcome, es_queja, ubicación física
(source_file + líneas) y el `por_ello` (dispositivo).

No lee el corpus: usa las columnas de texto que ya trae el CSV. Para el
considerando completo (sin truncar) de un caso puntual, usar la herramienta
canónica `scripts/diagnostico/extraer_caso.py` con el source_file + rango
que este script imprime.

Uso (desde la raíz del repo):
    python extraer_recuperados_H109.py
    python extraer_recuperados_H109.py --cons   # incluye snippet del considerando
"""

import csv
import sys

CASOS = "output/parser/csjn_casos.csv"

# Los 28 recuperados por B115 (tomos 331-334), del QA de H109.
RECUPERADOS = [
    "331_p28", "331_p58", "331_p230", "331_p427", "331_p472", "331_p769",
    "331_p858", "331_p1869", "331_p2249", "331_p2331", "331_p2799", "331_p2833",
    "332_p238", "332_p330", "332_p818", "332_p908", "332_p1143", "332_p1365",
    "332_p1445", "332_p1963",
    "333_p394", "333_p1735",
    "334_p38", "334_p965", "334_p1027", "334_p1063", "334_p1458", "334_p1703",
]


def main():
    con_cons = "--cons" in sys.argv
    casos = {}
    with open(CASOS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            casos[r["caso_id_canonico"]] = r

    faltan = [c for c in RECUPERADOS if c not in casos]
    print("=" * 80)
    print(f"CASOS RECUPERADOS POR B115 — extracción del golden ({len(RECUPERADOS)})")
    if faltan:
        print(f"AUSENTES del golden (revisar): {faltan}")
    print("=" * 80)

    for cid in RECUPERADOS:
        r = casos.get(cid)
        if not r:
            print(f"\n### {cid}  — AUSENTE del golden")
            continue
        nombre = r["case_name_cuerpo"] or r["case_name_indice"] or "(sin carátula)"
        print(f"\n{'─'*80}")
        print(f"### {cid}   {r['date']}   outcome={r['outcome']}   "
              f"es_queja={r['es_queja']}/{r['queja_resultado']}   vp={r['voting_pattern']}")
        print(f"    carátula: {nombre}")
        print(f"    índice:   {r['case_name_indice']}")
        print(f"    ubicación: {r['source_file']}  L{r['linea_inicio']}–{r['linea_fin_real'] or r['linea_fin']}  "
              f"(status {r['status_localizacion']})")
        por_ello = (r["por_ello_text"] or "").strip()
        print(f"    POR ELLO: {por_ello if por_ello else '(vacío)'}")
        if con_cons:
            cons = (r["considerando_text"] or "").strip()
            snippet = cons[:600] + ("…" if len(cons) > 600 else "")
            print(f"    CONSIDERANDO (snippet): {snippet}")


if __name__ == "__main__":
    main()
