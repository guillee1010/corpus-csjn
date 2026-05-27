"""
extraer_muestra_sf.py
=====================
Extrae una muestra estratificada de casos sin_firma para auditar a mano.

Genera dos CSVs chicos:
  - muestra_R1.csv: 10 casos R1 (no detectó dispositivo).
                    Estratificado: 5 del tomo 345 (donde más se concentran),
                    5 distribuidos en otros tomos recientes (347, 348, 346).
  - muestra_R2.csv: 8 casos R2 con outcome='otro' (mayor concentración).
                    Distribuidos por tomo.

Cada fila tiene caso_id, tomo, source_file, linea_inicio, linea_fin_real,
outcome, wc_mayoria, case_name_indice, case_name_cuerpo. Con eso se puede
abrir el markdown correspondiente y leer el bloque exacto.

Uso:
    python extraer_muestra_sf.py csjn_casos_v16.csv
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path


def main(ruta_csv):
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    with open(ruta_csv, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        filas = list(reader)

    sin_firma = [r for r in filas if r["voting_pattern"] == "sin_firma"]

    def firma_vacia(r):
        return not (r["firma_raw"] or "").strip()

    rescatados = {"inadmisible_280", "inadmisible_acordada_4"}

    r1 = [r for r in sin_firma
          if firma_vacia(r) and (r["outcome"] == "sin_dispositivo"
                                  or r["outcome"] in rescatados)]
    r2 = [r for r in sin_firma
          if firma_vacia(r) and r["outcome"] != "sin_dispositivo"
          and r["outcome"] not in rescatados]

    # Agrupar por tomo
    r1_por_tomo = defaultdict(list)
    for r in r1:
        r1_por_tomo[r["tomo"]].append(r)

    # Muestra R1: 5 del tomo 345, después tomar de los más concentrados
    muestra_r1 = []
    if "345" in r1_por_tomo:
        muestra_r1.extend(r1_por_tomo["345"][:5])
    for tomo in ("348", "347", "346", "344"):
        if tomo in r1_por_tomo and len(muestra_r1) < 10:
            muestra_r1.extend(r1_por_tomo[tomo][:2])
    muestra_r1 = muestra_r1[:10]

    # Muestra R2: filtrar outcome='otro' y tomar de tomos distintos
    r2_otro = [r for r in r2 if r["outcome"] == "otro"]
    r2_por_tomo = defaultdict(list)
    for r in r2_otro:
        r2_por_tomo[r["tomo"]].append(r)

    muestra_r2 = []
    for tomo in ("345", "347", "348", "337", "344", "329", "330", "338"):
        if tomo in r2_por_tomo and len(muestra_r2) < 8:
            muestra_r2.extend(r2_por_tomo[tomo][:1])
    muestra_r2 = muestra_r2[:8]

    cols = ["caso_id_canonico", "tomo", "source_file",
            "linea_inicio", "linea_fin_real",
            "outcome", "wc_mayoria",
            "case_name_indice", "case_name_cuerpo"]

    def escribir(path, filas_muestra):
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in filas_muestra:
                w.writerow({c: r.get(c, "") for c in cols})

    escribir("muestra_R1.csv", muestra_r1)
    escribir("muestra_R2.csv", muestra_r2)

    print(f"muestra_R1.csv: {len(muestra_r1)} casos R1 (no detecto dispositivo)")
    for r in muestra_r1:
        print(f"  {r['caso_id_canonico']:14s} tomo {r['tomo']}  "
              f"lineas {r['linea_inicio']}-{r['linea_fin_real']}  "
              f"caratula: {(r.get('case_name_indice') or '')[:50]}")
    print()
    print(f"muestra_R2.csv: {len(muestra_r2)} casos R2 con outcome='otro'")
    for r in muestra_r2:
        print(f"  {r['caso_id_canonico']:14s} tomo {r['tomo']}  "
              f"lineas {r['linea_inicio']}-{r['linea_fin_real']}  "
              f"wc {r['wc_mayoria']:>6s}  "
              f"caratula: {(r.get('case_name_indice') or '')[:50]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python extraer_muestra_sf.py csjn_casos_v16.csv")
        sys.exit(1)
    main(sys.argv[1])
