#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B124 · PASO 2 — Cruce de las variantes contra el gold M20 (n300).

NO toca parser.py ni outputs. Sobre los 300 casos del gold reconstruye el bloque
(igual que el parser), corre las 4 reglas (actual/A1/A2/B) y compara la EXTRACCION
del por_ello, usando el gold como ground truth de DONDE estaba la fuente buena/mala.

El gold M20 codifica DISPOSICION de fondo (cod_disposicion), no el outcome de acceso,
asi que NO se cruza outcome 1:1. Lo que SI tiene y sirve directo para B124:
  - por_ello_text : el dispositivo que vos codificaste.
  - flag_revisar_fuente : 12 casos donde marcaste la fuente como MALA  <-- banco B124.
  - cod_disposicion / cod_es_revision_fondo : para chequear precision en los de fondo.

Test nucleo (robusto al caveat de version del gold): se compara por_ello(variante)
contra por_ello(ACTUAL) — los dos con el parser de hoy — y se clasifica el cambio con
flag_revisar_fuente del gold:
  - cambio en caso de FUENTE OK   (flag vacio) -> el actual estaba bien -> probable REGRESION.
  - cambio en caso de FUENTE MALA (flag=1)     -> el actual estaba mal  -> probable CORRECCION.
La regla buena: ~0 cambios en fuente-OK, y maximo de correcciones en los 12 de fuente-mala.

Ademas reporta el caveat de version (actual vs gold por_ello) y, en los de fondo con
cod_disposicion comparable {revoca,confirma,deja_sin_efecto,nulidad}, si el outcome de
la variante coincide (secundario: mezcla capas acceso/disposicion, leer con cuidado).

Uso:
  python cruce_gold_variantes.py --gold ruta\\planilla_M20_LIMPIA_n300__rebuild.xlsx
"""
import sys
import argparse
import pathlib
import re

HERE     = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
REPO     = HERE.parents[3]
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
OUTCOMES_NO_VERBO = {"otro", "sin_dispositivo"}
DISPOSICIONES = {"revoca", "confirma", "deja_sin_efecto", "nulidad"}  # comparables outcome<->cod
# H129: clítico opcional entre "se" y el verbo (se lo/la/los/las/le/les + verbo).
# Sin él, el holding de la mayoría "se lo desestima" (346_p931) no matcheaba y P
# se metía en el dispositivo de la disidencia. El grupo de captura sigue siendo el
# verbo (group 1); el código solo usa .search() booleano, así que es inocuo.
RE_PERF = re.compile(
    r"\bse\s+(?:(?:lo|la|los|las|le|les)\s+)?"
    r"(resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
    r"hace[n]?\s+lugar|deja[n]?\s+sin\s+efecto|rechaza[n]?|desestima[n]?|"
    r"tiene[n]?\s+por|admite[n]?|anula[n]?|hace\s+saber|intima)\b",
    re.IGNORECASE)
TIERS = [
    (P._cand_estructural, "base",      True,  True),
    (P._cand_t2,          "base",      True,  False),
    (P._cand_estructural, "base_full", True,  True),
    (P._cand_t3b,         "zero_full", False, False),
    (P._cand_t4,          "base_full", True,  False),
]


def hacer_cache_lines(corpus_dir):
    cache = {}

    def get(sf):
        if sf not in cache:
            p = pathlib.Path(sf)
            if not p.is_absolute():
                p = corpus_dir / sf
            cache[sf] = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
        return cache[sf]

    return get


def _barrer_modo(bloque, rango, lineas_dictamen, *, excluye_dictamen, es_candidato,
                 permite_fallback, modo):
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
            ln = bloque[m2]; m2 += 1; ss = ln.strip()
            if not ss:
                continue
            chunk.append(ln); nlin += 1
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
                fb_idx, fb_text = k, txt
            if firma:
                last_idx, last_text = k, txt
        elif modo == "A2":
            last_idx, last_text = k, txt
        elif modo == "B":
            if P.classify_outcome(txt, "") not in OUTCOMES_NO_VERBO:
                last_idx, last_text = k, txt
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
        return (fb_idx, fb_text) if (permite_fallback and fb_idx is not None) else (None, "")
    if modo in ("A1", "P"):
        if last_idx is not None:
            return last_idx, last_text
        return (fb_idx, fb_text) if (permite_fallback and fb_idx is not None) else (None, "")
    return (last_idx, last_text) if last_idx is not None else (None, "")


def resolver_variante(bloque, apertura_rel, lineas_dictamen, ivi, modo):
    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    inicio = apertura_rel if apertura_rel is not None else (
        dictamen_end + 1 if dictamen_end is not None else 0)
    fin = ivi if (ivi is not None and (apertura_rel is None or ivi > apertura_rel)) else len(bloque)
    rangos = {"base": (inicio, fin), "base_full": (inicio, len(bloque)), "zero_full": (0, len(bloque))}
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
    return lineas_dictamen, apertura_rel, ivi, no_cons


def outcome_de(bloque, idx, txt, no_cons):
    if idx is None:
        return "sin_dispositivo"
    return P.classify_outcome(txt, P.extraer_considerando(bloque, idx, no_cons))


def _norm(s):
    return " ".join(str(s or "").split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default=str(REPO / "estadisticas" / "validacion" /
                                          "planilla_M20_LIMPIA_n300__rebuild.xlsx"))
    ap.add_argument("--corpus", default=str(REPO / "corpus"))
    ap.add_argument("--ejemplos", type=int, default=15)
    args = ap.parse_args()

    import pandas as pd
    g = pd.read_excel(args.gold)
    get_lines = hacer_cache_lines(pathlib.Path(args.corpus))
    MODOS = ["A1", "A2", "B", "C", "P"]

    n = 0
    no_rec = []
    # caveat de version
    actual_vs_gold_match = 0
    # extraccion variante vs actual, partida por flag
    cambios_fuente_ok = {m: [] for m in MODOS}     # (cid, por_ello_actual, por_ello_var)  <- probable regresion
    cambios_fuente_mala = {m: [] for m in MODOS}   # idem  <- probable correccion
    # precision disposicion (secundaria) en fondo comparable
    disp_total = 0
    disp_acierto = {m: 0 for m in MODOS}
    disp_acierto_actual = 0
    # detalle de los 12 de fuente mala
    detalle_12 = []

    for _, r in g.iterrows():
        cid = str(r["caso_id_canonico"])
        sf = str(r["source_file"])
        try:
            li = int(r["linea_inicio"]); lfr = int(r["linea_fin_real"])
        except (ValueError, TypeError):
            no_rec.append(f"{cid} (li/lfr)"); continue
        lines = get_lines(sf)
        if lines is None:
            no_rec.append(f"{cid} (source {sf})"); continue
        bloque = P.construir_bloque_desde_localizacion(lines, li, lfr)
        if not bloque:
            no_rec.append(f"{cid} (bloque vacio)"); continue
        n += 1

        ld, ar, ivi, no_cons = reproducir_full(bloque)
        ia, ta = P.resolver_dispositivo(bloque, ar, ld, ivi)
        oc_a = outcome_de(bloque, ia, ta, no_cons)

        gold_pe = _norm(r["por_ello_text"])
        fuente_mala = (str(r["flag_revisar_fuente"]) not in ("nan", "", "None"))
        if _norm(ta) == gold_pe:
            actual_vs_gold_match += 1

        picks = {}
        for m in MODOS:
            im, tm = resolver_variante(bloque, ar, ld, ivi, m)
            picks[m] = (im, tm, outcome_de(bloque, im, tm, no_cons))
            if _norm(tm) != _norm(ta):  # la variante cambia la extraccion respecto del actual
                (cambios_fuente_mala if fuente_mala else cambios_fuente_ok)[m].append(
                    (cid, _norm(ta)[:90], _norm(tm)[:90]))

        # precision disposicion (secundaria): fondo + cod_disposicion comparable
        cod_disp = str(r["cod_disposicion"]).strip()
        es_fondo = str(r["cod_es_revision_fondo"]).strip().lower() == "si"
        if es_fondo and cod_disp in DISPOSICIONES:
            disp_total += 1
            if oc_a == cod_disp:
                disp_acierto_actual += 1
            for m in MODOS:
                if picks[m][2] == cod_disp:
                    disp_acierto[m] += 1

        if fuente_mala:
            detalle_12.append((cid, cod_disp, str(r["cod_es_revision_fondo"]),
                               gold_pe[:110], _norm(ta)[:110],
                               {m: (_norm(picks[m][1])[:110], picks[m][2]) for m in MODOS},
                               oc_a))

    # ===== REPORTE =====
    K = args.ejemplos
    pct = lambda x, b: f"{100.0*x/b:.1f}%" if b else "n/a"
    print("=" * 78)
    print(f"B124 PASO 2 — CRUCE CON GOLD M20  ·  parser v{P.__version__}")
    print("=" * 78)
    print(f"casos gold reconstruidos: {n}/300   no reconstruidos: {len(no_rec)}")
    for x in no_rec[:K]:
        print(f"      - {x}")

    print(f"\n--- caveat de version: por_ello(actual v19.0) == por_ello(gold): "
          f"{actual_vs_gold_match}/{n}  ({pct(actual_vs_gold_match, n)}) ---")
    print("    (si es alto, el gold esta en la misma version y comparar contra gold seria limpio;")
    print("     igual el test de abajo compara variante-vs-ACTUAL, que no depende de esto.)")

    print("\n--- TEST NUCLEO · la variante CAMBIA la extraccion respecto del actual ---")
    print("  [A] en casos de FUENTE OK (gold no marco problema) = probable REGRESION (peor cuanto mas alto):")
    for m in MODOS:
        print(f"      {m}: {len(cambios_fuente_ok[m])}")
    for m in MODOS:
        if cambios_fuente_ok[m]:
            print(f"\n    --- {m} · cambios en fuente-OK (cid | actual -> variante), {min(K,len(cambios_fuente_ok[m]))} de {len(cambios_fuente_ok[m])} ---")
            for cid, a, b in cambios_fuente_ok[m][:K]:
                print(f"        [{cid}]")
                print(f"           actual : {a}")
                print(f"           {m:<6}: {b}")
    print("\n  [B] en casos de FUENTE MALA (los 12 que marcaste) = CORRECCION (mejor cuanto mas alto):")
    for m in MODOS:
        print(f"      {m}: {len(cambios_fuente_mala[m])} de 12")

    print("\n--- DETALLE de los 12 de FUENTE MALA (para leer si la correccion es buena) ---")
    for cid, cd, ef, gpe, ape_act, varsd, oca in detalle_12[:12]:
        print(f"\n  [{cid}]  cod_disposicion={cd}  es_fondo={ef}")
        print(f"     gold por_ello: {gpe}")
        print(f"     actual ({oca}): {ape_act}")
        for m in MODOS:
            tv, ov = varsd[m]
            print(f"     {m} ({ov}): {tv}")

    print("\n--- (secundario) precision disposicion en fondo comparable "
          f"(n={disp_total}, mezcla capas, leer con cuidado) ---")
    print(f"      actual: {disp_acierto_actual}/{disp_total}  ({pct(disp_acierto_actual, disp_total)})")
    for m in MODOS:
        print(f"      {m:<6}: {disp_acierto[m]}/{disp_total}  ({pct(disp_acierto[m], disp_total)})")

    print("\n" + "=" * 78)
    print("LECTURA: la regla buena no toca los de fuente-OK (≈0 en [A]) y corrige los 12 de")
    print("fuente-mala (alto en [B], con por_ello correcto en el detalle). Los rotos del corpus")
    print("completo NO los cubre el gold (solape ~5%): esos van por lectura con extraer_caso.")
    print("=" * 78)


if __name__ == "__main__":
    main()
