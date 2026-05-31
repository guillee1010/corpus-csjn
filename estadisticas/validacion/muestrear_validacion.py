#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
muestrear_validacion.py  --  M19, muestra para validacion contra ground truth.

Genera la muestra de CASOS y la de VOTOS para codificar a mano contra el .md y
medir exactitud del dataset (no regresion). Semilla fija; dos marcos por tabla:

  Marco A  -- aleatorio simple (insesgado -> exactitud global + IC Wilson).
  Marco B  -- oversample por valor: min(N_OBJETIVO, N_valor) por cada valor de
              cada columna de clasificacion. Los valores chicos quedan censados.
              Habilita precision/recall POR VALOR.

La muestra de VOTOS se ancla a los CASOS de la muestra de casos: se leen los
mismos .md una sola vez. Solo se agregan casos extra para cubrir los valores
raros de las columnas de votos. El codificador valida el bloque de votos completo
de cada caso, asi puede marcar jueces faltantes/sobrantes (recall de deteccion).

Salidas (sufijo = --golden):
  muestra_clave_<ver>.csv               LLAVE casos (valores del parser; NO al codificador)
  planilla_codificacion_<ver>.csv       CIEGA casos
  muestra_clave_votos_<ver>.csv         LLAVE votos
  planilla_codificacion_votos_<ver>.csv CIEGA votos

Regla M15: codificar contra el .md completo (extraer_caso.py), no el snippet del CSV.
"""
import argparse, csv, random
from collections import Counter, OrderedDict

__version__ = "1.1"   # H098: + muestra de votos anclada al caso

COLS_CASOS = ["outcome", "causa_inadmisibilidad", "es_queja",
              "queja_resultado", "tipo_cuestion_federal"]
COLS_VOTOS = ["posicion", "tipo_voto_sep", "fragmenta_ratio", "punto_divergencia"]

ID = "caso_id_canonico"
N_MARCO_A = 300
N_OBJETIVO_B = 20
N_DOBLE = 50
N_ESTRUCTURAL = 50


def cargar(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def oversample(rows, id_of, cols, ya_incluidos, rng, objetivo=N_OBJETIVO_B):
    """OrderedDict id->[etiquetas] que hay que SUMAR para llegar a min(objetivo,
    N_valor) por cada valor de cada col. `ya_incluidos`=ids que ya cuentan (Marco A)."""
    extra = OrderedDict()
    for col in cols:
        porval = {}
        for r in rows:
            porval.setdefault(r[col], []).append(r)
        for val, grp in porval.items():
            obj = min(objetivo, len(grp))
            ids_grp = [id_of(r) for r in grp]
            ya = [i for i in ids_grp if i in ya_incluidos or i in extra]
            etiqueta = "%s=%s" % (col, val if val != "" else "VACIO")
            for i in ya:
                if i in extra:
                    extra[i].append(etiqueta)
            faltan = obj - len(ya)
            if faltan > 0:
                disp = [r for r in grp if id_of(r) not in ya_incluidos
                        and id_of(r) not in extra]
                for r in rng.sample(disp, min(faltan, len(disp))):
                    extra.setdefault(id_of(r), []).append(etiqueta)
    return extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", default="csjn_casos.csv")
    ap.add_argument("--votos", default="csjn_casos_votos.csv")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--seed", type=int, default=20260531)
    ap.add_argument("--golden", default="v18.15")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    ver = args.golden

    casos = cargar(args.casos)
    by_id = {r[ID]: r for r in casos}
    todos = [r[ID] for r in casos]

    # ---------- CASOS ----------
    marco_a = set(rng.sample(todos, N_MARCO_A))
    extra_b = oversample(casos, lambda r: r[ID], COLS_CASOS, marco_a, rng)
    marco_b = set(extra_b)
    union = sorted(marco_a | marco_b)
    doble = set(rng.sample(union, min(N_DOBLE, len(union))))
    estruct = set(rng.sample(sorted(marco_a), min(N_ESTRUCTURAL, len(marco_a))))

    cp = "%s/muestra_clave_%s.csv" % (args.outdir, ver)
    with open(cp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([ID, "marco", "origen_b", "doble_cod", "spotcheck_estruct",
                    "source_file", "linea_inicio", "linea_fin_real"]
                   + ["parser_%s" % c for c in COLS_CASOS])
        for cid in union:
            r = by_id[cid]
            marco = ("A" if cid in marco_a else "") + ("B" if cid in marco_b else "")
            w.writerow([cid, marco, "|".join(extra_b.get(cid, [])),
                        int(cid in doble), int(cid in estruct),
                        r["source_file"], r["linea_inicio"], r["linea_fin_real"]]
                       + [r[c] for c in COLS_CASOS])

    pp = "%s/planilla_codificacion_%s.csv" % (args.outdir, ver)
    with open(pp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([ID, "tomo", "date", "case_name_cuerpo", "source_file",
                    "linea_inicio", "linea_fin_real", "doble_cod", "spotcheck_estruct"]
                   + ["cod_%s" % c for c in COLS_CASOS]
                   + ["cod_caratula_ok", "cod_fecha_ok", "notas"])
        for cid in union:
            r = by_id[cid]
            w.writerow([cid, r["tomo"], r["date"], r["case_name_cuerpo"],
                        r["source_file"], r["linea_inicio"], r["linea_fin_real"],
                        int(cid in doble), int(cid in estruct)]
                       + ["" for _ in COLS_CASOS] + ["", "", ""])

    # ---------- VOTOS (anclado al caso) ----------
    votos = cargar(args.votos)
    seq = Counter()
    for r in votos:
        c = r[ID]
        r["_vid"] = "%s::%d" % (c, seq[c]); seq[c] += 1
    votos_por_caso = OrderedDict()
    for r in votos:
        votos_por_caso.setdefault(r[ID], []).append(r)

    casos_a_v = set(c for c in union if c in votos_por_caso)
    extra_bv = oversample(votos, lambda r: r["_vid"], COLS_VOTOS, set(), rng)
    casos_extra_v = set(vid.split("::")[0] for vid in extra_bv) - casos_a_v
    casos_votos = sorted(casos_a_v | casos_extra_v)
    filas_votos = [r for c in casos_votos for r in votos_por_caso[c]]
    doble_v = set(rng.sample([r["_vid"] for r in filas_votos],
                             min(N_DOBLE, len(filas_votos))))

    cpv = "%s/muestra_clave_votos_%s.csv" % (args.outdir, ver)
    with open(cpv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["voto_id", ID, "juez", "marco", "origen_b", "doble_cod"]
                   + ["parser_%s" % c for c in COLS_VOTOS])
        for r in filas_votos:
            cid = r[ID]
            marco = ("A" if cid in casos_a_v else "") + ("B" if cid in casos_extra_v else "")
            w.writerow([r["_vid"], cid, r["juez"], marco,
                        "|".join(extra_bv.get(r["_vid"], [])), int(r["_vid"] in doble_v)]
                       + [r[c] for c in COLS_VOTOS])

    ppv = "%s/planilla_codificacion_votos_%s.csv" % (args.outdir, ver)
    with open(ppv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["voto_id", ID, "tomo", "date", "juez", "source_file",
                    "linea_inicio", "linea_fin_real", "primera_del_caso", "doble_cod",
                    "cod_juez_ok"] + ["cod_%s" % c for c in COLS_VOTOS]
                   + ["cod_completitud_caso", "notas"])
        for c in casos_votos:
            base = by_id.get(c, {})
            for j, r in enumerate(votos_por_caso[c]):
                w.writerow([r["_vid"], c, r["tomo"], r["date"], r["juez"],
                            base.get("source_file", ""), base.get("linea_inicio", ""),
                            base.get("linea_fin_real", ""), int(j == 0),
                            int(r["_vid"] in doble_v), ""]
                           + ["" for _ in COLS_VOTOS] + ["", ""])

    # ---------- reporte ----------
    print("muestrear_validacion.py v%s  seed=%d  golden=%s" % (__version__, args.seed, ver))
    print("\n[CASOS] poblacion %d | Marco A %d | Marco B %d | UNICOS %d"
          % (len(todos), len(marco_a), len(marco_b), len(union)))
    print("        doble %d | spot-check estructural %d" % (len(doble), len(estruct)))
    print("\n[VOTOS] poblacion %d votos en %d casos" % (len(votos), len(votos_por_caso)))
    print("        casos de la muestra de casos con votos: %d (Marco A)" % len(casos_a_v))
    print("        casos extra por valores raros:          %d (Marco B)" % len(casos_extra_v))
    print("        TOTAL casos a leer para votos:          %d" % len(casos_votos))
    print("        votos a codificar:                      %d" % len(filas_votos))
    print("        doble %d" % len(doble_v))
    total_md = sorted(set(union) | set(casos_votos))
    print("\n[.md A LEER EN TOTAL (casos+votos comparten lectura)]: %d" % len(total_md))
    print("\nCobertura por valor en votos (n muestra / N poblacion):")
    for col in COLS_VOTOS:
        pob = Counter(r[col] for r in votos)
        mue = Counter(r[col] for r in filas_votos)
        print("  [%s]" % col)
        for val, n in pob.most_common():
            print("      %-22s %4d / %5d" % ("VACIO" if val == "" else val,
                                             mue.get(val, 0), n))
    print("\nSalidas:\n  %s\n  %s\n  %s\n  %s" % (cp, pp, cpv, ppv))


if __name__ == "__main__":
    main()
