#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B124 · PASO 1 — Medicion de las 4 reglas de seleccion del dispositivo, sobre 5890.

NO toca parser.py ni outputs. Solo MIDE. Reconstruye el bloque EXACTO (igual que
el paso 0 y que procesar_archivo) y compara CUATRO reglas de "cual 'Por ello' es el
dispositivo", reusando la cascada y los detectores reales del parser (Gate 3):

  actual : primer candidato CON firma  (= parser.resolver_dispositivo, v19.0)
  A1     : ULTIMO candidato CON firma   (depende de firma confiable)
  A2     : ULTIMO candidato (sin mirar firma) (depende del techo de votos)  <-- tu propuesta
  B      : ULTIMO candidato CON VERBO   (classify_outcome(txt) not in {otro,sin_dispositivo})

Solo cambia la REGLA DE SELECCION dentro de _barrer; la cascada Tier1->4, los rangos,
los _cand_* y el armado del chunk son identicos al parser (copiados de resolver_dispositivo
L3134-3179 y _barrer L3099-3118).

GATES de fidelidad (si no pasan, las columnas A1/A2/B no son confiables):
  G1 reconstruccion : por_ello(actual) == csjn_casos_textos.por_ello_text  (esperado ~99.4%, 37 de t345)
  G2 replica cascada: mi modo "R" (= primer-con-firma reimplementado) == parser.resolver_dispositivo
                      (esperado 100%: prueba que mi cascada/chunk reproduce al parser)
  G3 outcome actual : classify_outcome(mi actual) == csjn_casos.outcome  (sanity)

Los 37 casos con G1 mismatch (bloque posiblemente desalineado) se EXCLUYEN de recuperados/
rotos y se vuelcan aparte con por_ello reproducido vs CSV para diagnosticar el cluster t345.

Uso:
  python variantes_dispositivo.py
  python variantes_dispositivo.py --ejemplos 20 --dump-345 t345.csv --dump-diff diff_A1A2.csv
"""
import sys
import csv
import argparse
import pathlib
import re
from collections import Counter

HERE     = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
REPO     = HERE.parents[3]
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402

csv.field_size_limit(10 * 1024 * 1024)

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
OUTCOMES_NO_VERBO = {"otro", "sin_dispositivo"}  # B: candidato sin verbo de disposicion

# P: marca ESTRUCTURAL del dispositivo de la CSJN ("se <verbo>"), no semantica.
# El argumental usa formas no-performativas ("corresponde/cabe/habra de", "no discutida").
RE_PERF = re.compile(
    r"\bse\s+(resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
    r"hace[n]?\s+lugar|deja[n]?\s+sin\s+efecto|rechaza[n]?|desestima[n]?|"
    r"tiene[n]?\s+por|admite[n]?|anula[n]?|hace\s+saber|intima)\b",
    re.IGNORECASE)

# Cascada identica a resolver_dispositivo (L3148-3179):
#   (detector, tipo_de_rango, excluye_dictamen, permite_fallback)
TIERS = [
    (P._cand_estructural, "base",      True,  True),   # Tier 1
    (P._cand_t2,          "base",      True,  False),  # Tier 2
    (P._cand_estructural, "base_full", True,  True),   # Tier 3
    (P._cand_t3b,         "zero_full", False, False),  # Tier 3b
    (P._cand_t4,          "base_full", True,  False),  # Tier 4
]


def hacer_cache_lines(corpus_dir):
    cache = {}

    def get(source_file):
        if source_file not in cache:
            p = pathlib.Path(source_file)
            if not p.is_absolute():
                p = corpus_dir / source_file
            cache[source_file] = (
                p.read_text(encoding="utf-8").split("\n") if p.exists() else None
            )
        return cache[source_file]

    return get


def _barrer_modo(bloque, rango, lineas_dictamen, *,
                 excluye_dictamen, es_candidato, permite_fallback, modo):
    """
    Identico a parser._barrer salvo la REGLA DE SELECCION:
      R  -> primer con firma (fallback primer sin firma)  [reproduce el parser]
      A1 -> ultimo con firma (fallback ultimo candidato)
      A2 -> ultimo candidato (sin firma)
      B  -> ultimo con verbo (classify_outcome del chunk not in OUTCOMES_NO_VERBO)
    Armado del chunk identico al parser (skip de vacias M21/B122, tope 6 o primer '.').
    """
    inicio, fin = rango
    fb_idx, fb_text = None, None
    last_idx, last_text = None, None
    for k in range(inicio, fin):
        if excluye_dictamen and k in lineas_dictamen:
            continue
        s = bloque[k].strip()
        if not s or not es_candidato(s):
            continue
        chunk, nlin, m2 = [], 0, k
        while nlin < 6 and m2 < len(bloque):
            ln = bloque[m2]
            m2 += 1
            ss = ln.strip()
            if not ss:
                continue
            chunk.append(ln)
            nlin += 1
            if ss.endswith("."):
                break
        txt = " ".join(chunk).strip()
        firma = any(P.linea_es_firma_de_juez(bloque[j])
                    for j in range(k + 1, min(k + 41, len(bloque))))
        if modo == "R":
            if permite_fallback and fb_idx is None:
                fb_idx, fb_text = k, txt
            if firma:
                return k, txt
        elif modo == "A1":
            if permite_fallback:
                fb_idx, fb_text = k, txt           # ultimo candidato visto
            if firma:
                last_idx, last_text = k, txt        # ultimo con firma
        elif modo == "A2":
            last_idx, last_text = k, txt            # ultimo candidato, sin firma
        elif modo == "B":
            if P.classify_outcome(txt, "") not in OUTCOMES_NO_VERBO:
                last_idx, last_text = k, txt        # ultimo con verbo
        elif modo == "C":
            if P.classify_outcome(txt, "") not in OUTCOMES_NO_VERBO:
                return k, txt                       # PRIMER con verbo (return inmediato)
        elif modo == "P":
            if firma:
                if RE_PERF.search(txt):
                    return k, txt                   # PRIMER performativo CON firma
                if last_idx is None:
                    last_idx, last_text = k, txt     # fallback1: primer con firma (= actual)
            elif permite_fallback and fb_idx is None:
                fb_idx, fb_text = k, txt             # fallback2: primer sin firma
    if modo == "R":
        if permite_fallback and fb_idx is not None:
            return fb_idx, fb_text
        return None, ""
    if modo == "A1":
        if last_idx is not None:
            return last_idx, last_text
        if permite_fallback and fb_idx is not None:
            return fb_idx, fb_text
        return None, ""
    if modo == "P":
        if last_idx is not None:                     # primer con firma (no performativo)
            return last_idx, last_text
        if permite_fallback and fb_idx is not None:
            return fb_idx, fb_text                   # primer sin firma
        return None, ""
    # A2, B, C
    if last_idx is not None:
        return last_idx, last_text
    return None, ""


def resolver_variante(bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv, modo):
    """Cascada Tier1->4 identica a resolver_dispositivo, con _barrer_modo(modo)."""
    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio = apertura_rel
    elif dictamen_end is not None:
        inicio = dictamen_end + 1
    else:
        inicio = 0
    if (inicio_votos_indiv is not None
            and (apertura_rel is None or inicio_votos_indiv > apertura_rel)):
        fin = inicio_votos_indiv
    else:
        fin = len(bloque)
    rangos = {"base": (inicio, fin),
              "base_full": (inicio, len(bloque)),
              "zero_full": (0, len(bloque))}
    for cand, rtipo, exd, fb in TIERS:
        idx, txt = _barrer_modo(bloque, rangos[rtipo], lineas_dictamen,
                                excluye_dictamen=exd, es_candidato=cand,
                                permite_fallback=fb, modo=modo)
        if idx is not None:
            return idx, txt
    return None, ""


def reproducir_full(bloque):
    zonas, _ = P.zonificar_bloque(bloque)
    lineas_dictamen = {k for k, z in enumerate(zonas) if z == "dictamen"}
    lineas_residuo = {k for k, z in enumerate(zonas) if z == "residuo_caso_anterior"}
    lineas_excluir = {k for k, z in enumerate(zonas) if z not in ZONAS_FALLO}
    _, apertura_rel = P.detectar_apertura_en_bloque(bloque)
    _, _, ivi, _ = P.detectar_votos_disidencias(bloque, lineas_excluir)
    no_cons = set(lineas_dictamen) | lineas_residuo
    if ivi is not None:
        no_cons |= set(range(ivi, len(bloque)))
    return zonas, lineas_dictamen, apertura_rel, ivi, no_cons


def outcome_de(bloque, idx, txt, no_cons):
    cons = P.extraer_considerando(bloque, idx, no_cons)
    return P.classify_outcome(txt, cons)


def _norm(s):
    return " ".join((s or "").split())


def listar(titulo, items, k):
    print(f"  {titulo}: {len(items)}")
    for x in items[:k]:
        print(f"      - {x}")
    if len(items) > k:
        print(f"      ... (+{len(items) - k} mas)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos",  default=str(REPO / "output" / "parser" / "csjn_casos.csv"))
    ap.add_argument("--textos", default=str(REPO / "output" / "parser" / "csjn_casos_textos.csv"))
    ap.add_argument("--corpus", default=str(REPO / "corpus"))
    ap.add_argument("--ejemplos", type=int, default=15)
    ap.add_argument("--dump-345", default="")
    ap.add_argument("--dump-diff", default="", help="CSV con todos los casos donde A1 != A2 (outcome)")
    args = ap.parse_args()

    get_lines = hacer_cache_lines(pathlib.Path(args.corpus))

    por_ello_csv, outcome_csv = {}, {}
    with open(args.textos, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            por_ello_csv[r["caso_id_canonico"]] = r.get("por_ello_text", "")
    with open(args.casos, encoding="utf-8") as f:
        casos = list(csv.DictReader(f))
    for r in casos:
        outcome_csv[r["caso_id_canonico"]] = r.get("outcome", "")

    n_total = len(casos)
    MODOS = ["A1", "A2", "B", "C", "P"]

    # gates
    g1_mismatch = []          # reconstruccion (por_ello actual vs CSV)
    g1_mismatch_345 = []      # idem, con textos para diagnostico
    g2_replica_fail = []      # mi "R" != parser.resolver_dispositivo
    g3_outcome_fail = []      # outcome actual recomputado != CSV
    n_ok = 0                  # casos con G1 ok (entran a recuperados/rotos)

    recup = {m: [] for m in MODOS}           # otro -> outcome
    recup_dist = {m: Counter() for m in MODOS}
    roto = {m: [] for m in MODOS}            # no-otro -> cambia
    pick_difiere = {m: 0 for m in MODOS}     # idx distinto del actual

    # cross-variante
    iguales_4 = 0
    A1_vs_A2 = []   # (cid, oc_a1, oc_a2) outcome distinto -> donde la firma cambia el pick
    A2_vs_B = []

    for c in casos:
        cid = c["caso_id_canonico"]
        sf, li, lfr = c.get("source_file", ""), c.get("linea_inicio", ""), c.get("linea_fin_real", "")
        lines = get_lines(sf) if sf else None
        if lines is None:
            continue
        try:
            li_i = int(li); lfr_i = int(lfr) if str(lfr) != "" else None
        except (ValueError, TypeError):
            continue
        bloque = P.construir_bloque_desde_localizacion(lines, li_i, lfr_i)
        if not bloque:
            continue

        zonas, lineas_dictamen, apertura_rel, ivi, no_cons = reproducir_full(bloque)

        # actual = parser real
        idx_a, txt_a = P.resolver_dispositivo(bloque, apertura_rel, lineas_dictamen, ivi)
        oc_a = outcome_de(bloque, idx_a, txt_a, no_cons)

        # G1 reconstruccion
        ref = por_ello_csv.get(cid, "")
        g1_ok = (txt_a == ref) or (_norm(txt_a) == _norm(ref))
        if not g1_ok:
            g1_mismatch.append(cid)
            if cid.startswith("345_"):
                g1_mismatch_345.append((cid, _norm(txt_a)[:90], _norm(ref)[:90]))

        # G2 replica de la cascada
        idx_r, txt_r = resolver_variante(bloque, apertura_rel, lineas_dictamen, ivi, "R")
        if (idx_r, _norm(txt_r)) != (idx_a, _norm(txt_a)):
            g2_replica_fail.append(cid)

        # G3 outcome sanity
        if g1_ok and oc_a != outcome_csv.get(cid, ""):
            g3_outcome_fail.append((cid, oc_a, outcome_csv.get(cid, "")))

        # variantes
        picks = {"actual": (idx_a, oc_a)}
        for m in MODOS:
            idx_m, txt_m = resolver_variante(bloque, apertura_rel, lineas_dictamen, ivi, m)
            oc_m = outcome_de(bloque, idx_m, txt_m, no_cons) if idx_m is not None else "sin_dispositivo"
            picks[m] = (idx_m, oc_m)

        # solo los G1-ok cuentan para recuperados/rotos
        if not g1_ok:
            continue
        n_ok += 1

        for m in MODOS:
            idx_m, oc_m = picks[m]
            if idx_m != idx_a:
                pick_difiere[m] += 1
            if oc_a == "otro" and oc_m != "otro":
                recup[m].append(cid)
                recup_dist[m][oc_m] += 1
            elif oc_a != "otro" and oc_m != oc_a:
                roto[m].append((cid, oc_a, oc_m))

        ocs = {picks[k][1] for k in ("actual", "A1", "A2", "B")}
        if len(ocs) == 1:
            iguales_4 += 1
        if picks["A1"][1] != picks["A2"][1]:
            A1_vs_A2.append((cid, picks["A1"][1], picks["A2"][1]))
        if picks["A2"][1] != picks["B"][1]:
            A2_vs_B.append((cid, picks["A2"][1], picks["B"][1]))

    # ================= REPORTE =================
    K = args.ejemplos
    pct = lambda x, b: f"{100.0 * x / b:.1f}%" if b else "n/a"
    print("=" * 78)
    print(f"B124 PASO 1 — VARIANTES DEL DISPOSITIVO  ·  parser v{P.__version__}")
    print("=" * 78)
    print(f"casos: {n_total}   ·   G1-ok evaluados para recup/rotos: {n_ok}")

    print("\n--- GATES de fidelidad ---")
    print(f"  G1 reconstruccion  mismatch: {len(g1_mismatch)}  ({pct(n_total - len(g1_mismatch), n_total)} ok)")
    print(f"  G2 replica cascada FAIL    : {len(g2_replica_fail)}   (debe ser 0; si >0, mi cascada no reproduce al parser)")
    listar("     G2 ejemplos", g2_replica_fail, K)
    print(f"  G3 outcome actual != CSV   : {len(g3_outcome_fail)}   (sanity)")
    for cid, a, b in g3_outcome_fail[:K]:
        print(f"      - {cid}: mio={a} csv={b}")

    print("\n--- RECUPERADOS (outcome actual = 'otro'  ->  variante != 'otro') ---")
    for m in MODOS:
        print(f"  {m:>2}: {len(recup[m])}   dist: " +
              ", ".join(f"{k}={v}" for k, v in recup_dist[m].most_common()))

    print("\n--- ROTOS (outcome actual != 'otro'  ->  variante cambia el outcome) = REGRESION ---")
    for m in MODOS:
        print(f"  {m:>2}: {len(roto[m])}")
    print(f"\n  NETO (recuperados - rotos):  " +
          "   ".join(f"{m}={len(recup[m]) - len(roto[m]):+d}" for m in MODOS))
    print("  pick (idx) distinto del actual: " +
          "   ".join(f"{m}={pick_difiere[m]}" for m in MODOS))

    for m in MODOS:
        print(f"\n  --- {m} · rotos (cid, actual -> {m}), {min(K, len(roto[m]))} de {len(roto[m])} ---")
        for cid, a, b in roto[m][:K]:
            print(f"      [{cid}] {a} -> {b}")

    print("\n--- DIFF entre variantes (donde discrepan en outcome) ---")
    print(f"  las 4 reglas coinciden en outcome: {iguales_4}/{n_ok}  ({pct(iguales_4, n_ok)})")
    print(f"  A1 != A2 (la FIRMA cambia el resultado = tu punto ciego del techo): {len(A1_vs_A2)}")
    for cid, a1, a2 in A1_vs_A2[:K]:
        print(f"      [{cid}] A1={a1}  A2={a2}")
    print(f"  A2 != B  (el VERBO/OCR cambia el resultado): {len(A2_vs_B)}")
    for cid, a2, b in A2_vs_B[:K]:
        print(f"      [{cid}] A2={a2}  B={b}")

    print("\n--- TOMO 345 · los G1-mismatch (por_ello reproducido vs CSV) ---")
    print(f"  total 345 en mismatch: {len(g1_mismatch_345)} (de {len(g1_mismatch)} mismatch totales)")
    for cid, rep, ref in g1_mismatch_345[:K]:
        print(f"      [{cid}]")
        print(f"         repro: {rep}")
        print(f"         csv  : {ref}")

    print("\n" + "=" * 78)
    print("LECTURA: la regla buena es la de NETO alto con ROTOS bajos y auditables.")
    print("Si A1==A2 casi siempre, la firma es redundante y A2 gana por simple (tu tesis).")
    print("A1!=A2 son los casos donde mirar: ahi la firma salvo o estorbo. A2!=B = costo del OCR del verbo.")
    print("=" * 78)

    if args.dump_345 and g1_mismatch_345:
        with open(args.dump_345, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["caso_id", "por_ello_repro", "por_ello_csv"])
            w.writerows(g1_mismatch_345)
        print(f"[dump] t345 -> {args.dump_345}")
    if args.dump_diff and A1_vs_A2:
        with open(args.dump_diff, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f); w.writerow(["caso_id", "outcome_A1", "outcome_A2"])
            w.writerows(A1_vs_A2)
        print(f"[dump] A1!=A2 -> {args.dump_diff}")


if __name__ == "__main__":
    main()
