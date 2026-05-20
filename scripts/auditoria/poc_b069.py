# PoC B069 — simular fix de rango en Pista 1 (buscar_atras)
#
# Cambio simulado:
#   buscar_atras(es_caratula, lfc, li + 5)
#   ->
#   buscar_atras(es_caratula, lfc, max(lfc - MAX_RETROCESO, li + 5))
#
# Mide:
#   - Mejoras: sin_firma donde retroceso > MAX_RETROCESO (Pista 1 no cortaria)
#   - Regresiones: con_firma donde retroceso > MAX_RETROCESO (Pista 1 dejaria de cortar)
#
# Uso: python scripts/auditoria/poc_b069.py
# Desde: raiz del proyecto

import csv
from collections import Counter

MAX_RETROCESO = 100


def main():
    with open("output/parser/csjn_casos.csv", encoding="utf-8") as f:
        todos = list(csv.DictReader(f))

    # Filtrar: fallos con pista_fin == caratula_siguiente, status_fin == fin_dentro_bloque
    p1_atras = [
        r for r in todos
        if r["tipo_entrada"] == "fallo"
        and r["pista_fin"] == "caratula_siguiente"
        and r["status_fin"] == "fin_dentro_bloque"
    ]

    print(f"Casos totales: {len(todos)}")
    print(f"Fallos con Pista 1 atras (caratula_siguiente + fin_dentro_bloque): {len(p1_atras)}")
    print(f"MAX_RETROCESO simulado: {MAX_RETROCESO}")
    print()

    mejoras = []
    regresiones = []
    sin_cambio = []

    for r in p1_atras:
        li = int(r["linea_inicio"])
        lf = int(r["linea_fin"])
        lfr = int(r["linea_fin_real"])
        retroceso = lf - lfr
        tiene_firma = bool(r["firma_raw"].strip())

        if retroceso > MAX_RETROCESO:
            # El fix evitaria este corte
            if not tiene_firma:
                mejoras.append(r)
            else:
                regresiones.append(r)
        else:
            sin_cambio.append(r)

    print(f"=== RESULTADOS ===")
    print(f"Mejoras (sin_firma, retroceso > {MAX_RETROCESO}): {len(mejoras)}")
    print(f"Regresiones potenciales (con_firma, retroceso > {MAX_RETROCESO}): {len(regresiones)}")
    print(f"Sin cambio (retroceso <= {MAX_RETROCESO}): {len(sin_cambio)}")
    print()

    # Desglose sin_cambio
    sc_sin_firma = sum(1 for r in sin_cambio if not r["firma_raw"].strip())
    sc_con_firma = sum(1 for r in sin_cambio if r["firma_raw"].strip())
    print(f"Sin cambio desglose:")
    print(f"  con firma (OK, Pista 1 funciono bien): {sc_con_firma}")
    print(f"  sin firma (no resueltos por este fix): {sc_sin_firma}")
    print()

    if regresiones:
        print(f"=== REGRESIONES POTENCIALES (investigar) ===")
        for r in regresiones[:20]:
            li = int(r["linea_inicio"])
            lf = int(r["linea_fin"])
            lfr = int(r["linea_fin_real"])
            print(f"  {r['caso_id_canonico']:<15} retroceso={lf-lfr:<5} firma={r['firma_raw'][:60]}")
        if len(regresiones) > 20:
            print(f"  ... y {len(regresiones) - 20} mas")
    else:
        print("=== 0 REGRESIONES ===")

    print()
    print(f"=== RESUMEN ===")
    total_sin_firma_p1 = len(mejoras) + sc_sin_firma
    print(f"Sin firma por Pista 1 atras (total): {total_sin_firma_p1}")
    print(f"  Resueltos por fix: {len(mejoras)} ({100*len(mejoras)/total_sin_firma_p1:.1f}%)")
    print(f"  Pendientes: {sc_sin_firma} ({100*sc_sin_firma/total_sin_firma_p1:.1f}%)")
    print(f"Regresiones: {len(regresiones)}")


if __name__ == "__main__":
    main()
