"""
diag_sin_firma.py
=================
Diagnóstico del reparto R1 / R2 / R3 de los casos con voting_pattern='sin_firma'
en csjn_casos_v16.csv.

R1: el parser no detectó dispositivo. firma_raw vacío + outcome='sin_dispositivo'
    o rescatado a 'inadmisible_280' / 'inadmisible_acordada_4'.
R2: detectó dispositivo pero collect_firma_lines no encontró ningún juez en las
    40 líneas siguientes. firma_raw vacío + outcome real.
R3: collect_firma_lines acumuló texto pero parse_firma no extrajo ningún juez.
    firma_raw NO vacío + voting_pattern=sin_firma.

Uso:
    python diag_sin_firma.py csjn_casos_v16.csv
"""

import csv
import sys
from collections import Counter
from pathlib import Path

COL_VOTING_PATTERN = "voting_pattern"
COL_OUTCOME        = "outcome"
COL_TOMO           = "tomo"
COL_CASO_ID        = "caso_id_canonico"
COL_WC_MAYORIA     = "wc_mayoria"
COL_FIRMA_RAW      = "firma_raw"

OUTCOMES_RESCATADOS = {"inadmisible_280", "inadmisible_acordada_4"}


def main(ruta_csv):
    path = Path(ruta_csv)
    if not path.exists():
        print(f"No existe: {path}")
        sys.exit(1)

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        filas = list(reader)

    total = len(filas)
    sin_firma = [r for r in filas if r[COL_VOTING_PATTERN] == "sin_firma"]
    n_sf = len(sin_firma)

    print(f"Total casos: {total}")
    print(f"voting_pattern='sin_firma': {n_sf} ({n_sf/total*100:.1f}%)")
    print()

    def firma_vacia(r):
        return not (r[COL_FIRMA_RAW] or "").strip()

    def es_r1(r):
        return firma_vacia(r) and (
            r[COL_OUTCOME] == "sin_dispositivo"
            or r[COL_OUTCOME] in OUTCOMES_RESCATADOS
        )

    def es_r2(r):
        return firma_vacia(r) and not es_r1(r)

    def es_r3(r):
        return not firma_vacia(r)

    r1 = [r for r in sin_firma if es_r1(r)]
    r2 = [r for r in sin_firma if es_r2(r)]
    r3 = [r for r in sin_firma if es_r3(r)]

    print("-" * 60)
    print("REPARTO R1 / R2 / R3")
    print("-" * 60)
    print(f"R1: no detectó dispositivo                 {len(r1):4d} ({len(r1)/n_sf*100:4.1f}%)")
    print(f"R2: dispositivo OK, ningún juez en ventana {len(r2):4d} ({len(r2)/n_sf*100:4.1f}%)")
    print(f"R3: firma_raw acumulado, parse_firma falló {len(r3):4d} ({len(r3)/n_sf*100:4.1f}%)")
    print(f"Suma de control: {len(r1)+len(r2)+len(r3)} (debe ser {n_sf})")
    print()

    print("-" * 60)
    print("R2: distribución de outcomes")
    print("(tienen dispositivo OK pero firma quedó vacía)")
    print("-" * 60)
    for outcome, n in Counter(r[COL_OUTCOME] for r in r2).most_common():
        print(f"  {outcome:30s} {n:4d}")
    print()

    if r3:
        print("-" * 60)
        print("R3: distribución de outcomes")
        print("-" * 60)
        for outcome, n in Counter(r[COL_OUTCOME] for r in r3).most_common():
            print(f"  {outcome:30s} {n:4d}")
        print()

    print("-" * 60)
    print("Concentración por tomo")
    print("-" * 60)
    tomos_total = Counter(r[COL_TOMO] for r in filas)
    tomos_sf    = Counter(r[COL_TOMO] for r in sin_firma)
    tomos_r1    = Counter(r[COL_TOMO] for r in r1)
    tomos_r2    = Counter(r[COL_TOMO] for r in r2)
    tomos_r3    = Counter(r[COL_TOMO] for r in r3)

    print(f"{'tomo':6s} {'total':>6s} {'sf':>5s} {'%':>5s} {'R1':>5s} {'R2':>5s} {'R3':>5s}")
    for tomo in sorted(tomos_total):
        t   = tomos_total[tomo]
        sf  = tomos_sf[tomo]
        pct = sf / t * 100 if t else 0
        print(f"{tomo:6s} {t:6d} {sf:5d} {pct:4.1f}% "
              f"{tomos_r1[tomo]:5d} {tomos_r2[tomo]:5d} {tomos_r3[tomo]:5d}")
    print()

    def muestra(grupo, nombre, n=10):
        if not grupo:
            return
        print("-" * 60)
        print(f"Muestra {nombre} (primeros {min(n,len(grupo))})")
        print("-" * 60)
        print(f"  {'caso_id':18s} {'tomo':5s} {'outcome':22s} {'wc_may':>7s}  firma_raw[:60]")
        for r in grupo[:n]:
            firma_preview = (r[COL_FIRMA_RAW] or "")[:60].replace("\n", " ")
            print(f"  {r[COL_CASO_ID]:18s} {r[COL_TOMO]:5s} "
                  f"{r[COL_OUTCOME]:22s} {r[COL_WC_MAYORIA]:>7s}  {firma_preview}")
        print()

    muestra(r2, "R2 (dispositivo OK, firma vacía)", 15)
    muestra(r3, "R3 (firma_raw no vacío, parse falló)", 10)

    print("-" * 60)
    print("Lectura del resultado")
    print("-" * 60)
    mayor = max([("R1", len(r1)), ("R2", len(r2)), ("R3", len(r3))],
                key=lambda x: x[1])
    print(f"Predomina {mayor[0]} con {mayor[1]} casos.")
    if mayor[0] == "R1":
        print("Foco para v17: detectar_apertura_dispositivo (faltan variantes).")
    elif mayor[0] == "R2":
        print("Foco para v17: ampliar JUECES_CONOCIDOS o ventana de 40 líneas")
        print("en collect_firma_lines.")
    else:
        print("Foco para v17: revisar parse_firma o el matching de regex de jueces.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python diag_sin_firma.py csjn_casos_v16.csv")
        sys.exit(1)
    main(sys.argv[1])
