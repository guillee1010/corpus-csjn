#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B124 · AUTOPSIA — paisaje de candidatos por caso, para leer los .md reales.

NO toca nada. Para una lista de casos (default: las 5 regresiones de A + las mejoras
+ el argumental-con-verbo de C), reconstruye el bloque e imprime TODOS los candidatos
del rango de busqueda con sus features, para ver en concreto si el dispositivo de fondo
es siempre el primer candidato PERFORMATIVO ("se revoca/se resuelve/se hace lugar...")
y si los estorbos (argumental anterior / accesorio posterior) son separables.

Por cada candidato:  idx | zona | firma? | perf? | outcome(classify) | texto
Luego: que toma cada regla (actual/A1/A2/B/C) y el por_ello del gold.

Uso:
  python autopsia_candidatos.py --gold ...\\planilla_M20_LIMPIA_n300__rebuild.xlsx
  python autopsia_candidatos.py --casos 331_p2913 339_p1530 --gold ...
"""
import sys
import re
import argparse
import pathlib

HERE = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
OUTCOMES_NO_VERBO = {"otro", "sin_dispositivo"}
TIERS = [
    (P._cand_estructural, "base",      True,  True),
    (P._cand_t2,          "base",      True,  False),
    (P._cand_estructural, "base_full", True,  True),
    (P._cand_t3b,         "zero_full", False, False),
    (P._cand_t4,          "base_full", True,  False),
]
# hipotesis: el dispositivo es PERFORMATIVO ("se <verbo>"), el argumental no.
RE_PERF = re.compile(
    r"\bse\s+(resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
    r"hace[n]?\s+lugar|deja[n]?\s+sin\s+efecto|rechaza[n]?|desestima[n]?|"
    r"tiene[n]?\s+por|admite[n]?|anula[n]?|hace\s+saber|intima)\b",
    re.IGNORECASE)

CASOS_DEFAULT = [
    "331_p2913", "332_p979", "332_p1280", "339_p1530", "340_p1554",  # regresiones A (accesorio?)
    "334_p941", "345_p583", "346_p44",                               # mejoras (argumental?)
    "329_p1862",                                                     # argumental-con-verbo (C)
    "329_p3956", "329_p4178",                                        # ambiguos (competencia originaria)
]


def chunk_de(bloque, k):
    chunk, nlin, m2 = [], 0, k
    while nlin < 6 and m2 < len(bloque):
        ln = bloque[m2]; m2 += 1; s = ln.strip()
        if not s:
            continue
        chunk.append(ln); nlin += 1
        if s.endswith("."):
            break
    return " ".join(chunk).strip()


def tiene_firma(bloque, k):
    return any(P.linea_es_firma_de_juez(bloque[j]) for j in range(k + 1, min(k + 41, len(bloque))))


def es_candidato_algun(stripped):
    det = []
    if P._cand_estructural(stripped):
        det.append("E")
    if P._cand_t2(stripped):
        det.append("t2")
    if P._cand_t3b(stripped):
        det.append("t3b")
    if P._cand_t4(stripped):
        det.append("t4")
    return det


def reproducir_full(bloque):
    zonas, _ = P.zonificar_bloque(bloque)
    ld = {k for k, z in enumerate(zonas) if z == "dictamen"}
    lex = {k for k, z in enumerate(zonas) if z not in ZONAS_FALLO}
    _, ar = P.detectar_apertura_en_bloque(bloque)
    _, _, ivi, _ = P.detectar_votos_disidencias(bloque, lex)
    return zonas, ld, ar, ivi


def _barrer_modo(bloque, rango, ld, *, exd, cand, fb, modo):
    inicio, fin = rango
    fbi, fbt, li, lt = None, None, None, None
    for k in range(inicio, fin):
        if exd and k in ld:
            continue
        s = bloque[k].strip()
        if not s or not cand(s):
            continue
        txt = chunk_de(bloque, k)
        f = tiene_firma(bloque, k)
        if modo == "actual":
            if fb and fbi is None:
                fbi, fbt = k, txt
            if f:
                return k, txt
        elif modo == "A1":
            if fb:
                fbi, fbt = k, txt
            if f:
                li, lt = k, txt
        elif modo == "A2":
            li, lt = k, txt
        elif modo == "B":
            if P.classify_outcome(txt, "") not in OUTCOMES_NO_VERBO:
                li, lt = k, txt
        elif modo == "C":
            if P.classify_outcome(txt, "") not in OUTCOMES_NO_VERBO:
                return k, txt
        elif modo == "P":
            if f:
                if RE_PERF.search(txt):
                    return k, txt                   # primer performativo con firma
                if li is None:
                    li, lt = k, txt                  # fallback1: primer con firma
            elif fb and fbi is None:
                fbi, fbt = k, txt                    # fallback2: primer sin firma
    if modo == "actual":
        return (fbi, fbt) if (fb and fbi is not None) else (None, None)
    if modo in ("A1", "P"):
        if li is not None:
            return li, lt
        return (fbi, fbt) if (fb and fbi is not None) else (None, None)
    return (li, lt) if li is not None else (None, None)


def resolver(bloque, ar, ld, ivi, modo):
    de = max(ld) if ld else None
    inicio = ar if ar is not None else (de + 1 if de is not None else 0)
    fin = ivi if (ivi is not None and (ar is None or ivi > ar)) else len(bloque)
    R = {"base": (inicio, fin), "base_full": (inicio, len(bloque)), "zero_full": (0, len(bloque))}
    for cand, rt, exd, fb in TIERS:
        i, t = _barrer_modo(bloque, R[rt], ld, exd=exd, cand=cand, fb=fb, modo=modo)
        if i is not None:
            return i, t
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--corpus", default=str(HERE.parents[3] / "corpus"))
    ap.add_argument("--casos", nargs="*", default=CASOS_DEFAULT)
    args = ap.parse_args()

    import pandas as pd
    g = pd.read_excel(args.gold).set_index("caso_id_canonico")
    corpus = pathlib.Path(args.corpus)

    for cid in args.casos:
        if cid not in g.index:
            print(f"\n### {cid}: NO esta en el gold"); continue
        r = g.loc[cid]
        sf = str(r["source_file"]); li = int(r["linea_inicio"]); lfr = int(r["linea_fin_real"])
        p = pathlib.Path(sf)
        if not p.is_absolute():
            p = corpus / sf
        lines = p.read_text(encoding="utf-8").split("\n")
        bloque = P.construir_bloque_desde_localizacion(lines, li, lfr)
        zonas, ld, ar, ivi = reproducir_full(bloque)
        de = max(ld) if ld else None
        inicio = ar if ar is not None else (de + 1 if de is not None else 0)
        fin = ivi if (ivi is not None and (ar is None or ivi > ar)) else len(bloque)

        print("\n" + "=" * 100)
        print(f"### {cid}   apertura_rel={ar}  inicio_votos={ivi}  rango_busqueda=[{inicio},{fin})  len={len(bloque)}")
        print(f"    cod_disposicion={r['cod_disposicion']}  es_fondo={r['cod_es_revision_fondo']}")
        print(f"    gold por_ello: {' '.join(str(r['por_ello_text']).split())[:160]}")
        print("    " + "-" * 92)
        print(f"    {'idx':>4} {'zona':<13} {'det':<10} {'firma':<5} {'perf':<4} {'outcome':<14} texto")
        # listar candidatos en un margen alrededor del rango de busqueda
        lo = max(0, inicio - 2)
        hi = min(len(bloque), fin + 4)
        for k in range(lo, hi):
            s = bloque[k].strip()
            if not s:
                continue
            det = es_candidato_algun(s)
            if not det:
                continue
            txt = chunk_de(bloque, k)
            f = "si" if tiene_firma(bloque, k) else "."
            perf = "si" if RE_PERF.search(txt) else "."
            oc = P.classify_outcome(txt, "")
            z = zonas[k] if k < len(zonas) else "?"
            print(f"    {k:>4} {z:<13} {','.join(det):<10} {f:<5} {perf:<4} {oc:<14} {txt[:90]}")
        print("    " + "-" * 92)
        for m in ["actual", "A1", "A2", "B", "C", "P"]:
            i, t = resolver(bloque, ar, ld, ivi, m)
            oc = P.classify_outcome(t, "") if t else "sin_dispositivo"
            print(f"    {m:<7} idx={i}  outcome={oc}  | {('' if t is None else t)[:80]}")


if __name__ == "__main__":
    main()
