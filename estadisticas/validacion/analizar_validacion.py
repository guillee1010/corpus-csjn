#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analizar_validacion.py  --  M19, metricas de exactitud contra ground truth.

Toma una planilla codificada a mano (columnas cod_*) y la llave del parser
(columnas parser_*), las cruza por id, y para cada par (cod_X, parser_X) calcula:

  - exactitud (acuerdo) global con IC de Wilson 95%
  - precision y recall POR VALOR (matriz cod x parser)
  - tasa de falso-residual para valores residuales ('', 'otro', 'indeterminado')
  - kappa de Cohen entre dos codificaciones (si se pasa --planilla2)
  - spot-check estructural (cod_caratula_ok/cod_fecha_ok) con regla de tres si 0 errores
  - completitud de votos (cod_completitud_caso) si esta presente

Es agnostico de tabla: descubre los pares cod_/parser_ solos. Sirve para casos y
para votos. Si la planilla todavia no tiene filas codificadas, lo informa y corta.

AMBIGUO: una celda cod_* con valor 'AMBIGUO' es indeterminacion del .md (OCR), no
error del parser; se cuenta aparte, fuera del denominador de exactitud.
"""
import argparse, csv, math
from collections import Counter, defaultdict

__version__ = "1.1"

RESIDUALES = {"", "otro", "indeterminado"}
AMB = "AMBIGUO"


def cargar(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    medio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, centro - medio), min(1.0, centro + medio)


def kappa(pares):
    """Cohen's kappa sobre lista de (a, b)."""
    n = len(pares)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pares if a == b) / n
    ca, cb = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    cats = set(ca) | set(cb)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    return (po - pe) / (1 - pe) if pe != 1 else float("nan")


def pares_columnas(planilla_row, clave_row):
    cod = {c[4:] for c in planilla_row if c.startswith("cod_")}
    par = {c[7:] for c in clave_row if c.startswith("parser_")}
    return sorted(cod & par)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--planilla", required=True)
    ap.add_argument("--clave", required=True)
    ap.add_argument("--planilla2", help="segunda codificacion (kappa)")
    ap.add_argument("--id-col", default="caso_id_canonico")
    ap.add_argument("--label", default="validacion")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    plan = cargar(args.planilla)
    clave = cargar(args.clave)
    idc = args.id_col
    clave_by = {r[idc]: r for r in clave}
    cols = pares_columnas(plan[0], clave[0])

    out = []
    def w(s=""): out.append(s); print(s)

    w("analizar_validacion.py v%s  |  %s" % (__version__, args.label))
    w("planilla %d filas | clave %d filas | columnas: %s"
      % (len(plan), len(clave), ", ".join(cols)))

    total_cod = sum(1 for r in plan for c in cols if r.get("cod_" + c, "").strip())
    if total_cod == 0:
        w("\n>> Sin filas codificadas todavia. Estructura OK, esperando codificacion.")
        _guardar(out, args)
        return

    for col in cols:
        ck, pk = "cod_" + col, "parser_" + col
        filas = [(r.get(ck, "").strip(), clave_by[r[idc]][pk])
                 for r in plan if r[idc] in clave_by and r.get(ck, "").strip()]
        if not filas:
            continue
        amb = [x for x in filas if x[0] == AMB]
        evals = [x for x in filas if x[0] != AMB]
        aciertos = sum(1 for cod, par in evals if cod == par)
        p, lo, hi = wilson(aciertos, len(evals))
        w("\n=== %s ===" % col)
        w("  codificadas %d (ambiguas %d, evaluables %d)" % (len(filas), len(amb), len(evals)))
        w("  exactitud %.1f%%  IC95 Wilson [%.1f, %.1f]"
          % (100 * p, 100 * lo, 100 * hi))
        cod_c = Counter(c for c, _ in evals)
        par_c = Counter(pp for _, pp in evals)
        ok = Counter()
        for c, pp in evals:
            if c == pp:
                ok[c] += 1
        valores = sorted(set(cod_c) | set(par_c), key=lambda v: -par_c.get(v, 0))
        w("  valor                      n_parser  precision   recall")
        for v in valores:
            prec = ok[v] / par_c[v] if par_c.get(v) else float("nan")
            rec = ok[v] / cod_c[v] if cod_c.get(v) else float("nan")
            w("    %-24s %6d   %s   %s"
              % ("VACIO" if v == "" else v, par_c.get(v, 0),
                 "%6.1f%%" % (100 * prec) if par_c.get(v) else "    -- ",
                 "%6.1f%%" % (100 * rec) if cod_c.get(v) else "    -- "))
        for resid in (RESIDUALES & set(par_c)):
            base = par_c[resid]
            fuga = sum(1 for c, pp in evals if pp == resid and c not in RESIDUALES)
            w("  falso-residual [%s]: %d/%d (%.1f%%) que el humano asigno a categoria definida"
              % ("VACIO" if resid == "" else resid, fuga, base, 100 * fuga / base))

    if args.planilla2:
        plan2 = {r[idc]: r for r in cargar(args.planilla2)}
        w("\n=== acuerdo inter/intra-codificador (kappa de Cohen) ===")
        for col in cols:
            ck = "cod_" + col
            pares = [(r.get(ck, "").strip(), plan2[r[idc]].get(ck, "").strip())
                     for r in plan if r[idc] in plan2
                     and r.get(ck, "").strip() and plan2[r[idc]].get(ck, "").strip()]
            if pares:
                w("  %-24s kappa %.3f  (n=%d)" % (col, kappa(pares), len(pares)))

    for ec, etiq in (("cod_caratula_ok", "caratula"), ("cod_fecha_ok", "fecha")):
        if ec in plan[0]:
            vals = [r[ec].strip().upper() for r in plan
                    if r[ec].strip() and r[ec].strip().upper() != AMB]
            if vals:
                err = sum(1 for v in vals if v in ("N", "NO", "0"))
                w("\n  estructural [%s]: %d revisadas, %d errores" % (etiq, len(vals), err))
                if err == 0:
                    w("    regla de tres: cota superior del error ~%.1f%% (95%%)"
                      % (100 * 3 / len(vals)))

    if "cod_completitud_caso" in plan[0]:
        vals = [r["cod_completitud_caso"].strip() for r in plan
                if r["cod_completitud_caso"].strip()]
        if vals:
            okc = sum(1 for v in vals if v.upper() == "OK")
            w("\n  completitud de votos por caso: %d/%d OK; %d con falta/sobra"
              % (okc, len(vals), len(vals) - okc))

    _guardar(out, args)


def _guardar(out, args):
    path = "%s/metricas_%s.txt" % (args.outdir, args.label)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n-> %s" % path)


if __name__ == "__main__":
    main()
