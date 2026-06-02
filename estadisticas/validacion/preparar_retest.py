#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
preparar_retest.py -- M19, submuestra para test-retest (kappa intra-codificador).

Sortea n casos de la planilla codificada y emite una planilla EN BLANCO
(solo caso_id_canonico + columnas cod_* vacias), en orden barajado, para
recodificar A CIEGO sin ver los codigos originales ni la clave del parser.

La recodificacion se hace mirando el fallo (el .md / texto), NO csjn_casos.csv.
Despues:
    python analizar_validacion.py --planilla <original> --clave <original> \
        --planilla2 <recodificada> --label m19_kappa
"""
import argparse, csv, random

# Campos semanticos a recodificar (sin estructurales: no entran en kappa).
COD_COLS = ["cod_es_queja", "cod_outcome", "cod_queja_resultado",
            "cod_tipo_cuestion_federal", "cod_causa_inadmisibilidad"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--planilla", required=True)
    ap.add_argument("--id-col", default="caso_id_canonico")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20260601)
    ap.add_argument("--out", default="retest_blank.csv")
    args = ap.parse_args()

    with open(args.planilla, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    ids = [r[args.id_col] for r in filas]

    random.seed(args.seed)
    muestra = random.sample(ids, min(args.n, len(ids)))
    random.shuffle(muestra)  # orden distinto al original, baja el efecto memoria

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([args.id_col] + COD_COLS)
        for cid in muestra:
            w.writerow([cid] + [""] * len(COD_COLS))

    print("sorteo n=%d de %d (seed %d) -> %s"
          % (len(muestra), len(ids), args.seed, args.out))
    print("recodifica a ciego (solo el fallo a la vista), despues corre kappa.")

if __name__ == "__main__":
    main()
