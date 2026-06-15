#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B124 · AUTOPSIA DE LOS ROTOS DE P (corpus) — leer si son correcciones o regresiones.

NO toca nada. Corre P sobre los 5890, autodetecta los casos donde el ACTUAL daba un
outcome != 'otro' y P lo cambia (= los "rotos" de P, ~31), y para cada uno imprime el
PAISAJE de candidatos (idx | zona | firma | perf | outcome | texto) + el pick de actual
y de P. Asi se lee a ojo si P corrige (el actual capturaba mal) o regresiona (hueco de RE_PERF).

Solo audita casos con reconstruccion fiel (por_ello actual == CSV); excluye los 37 de t345.

Uso:
  python autopsia_rotos_P.py
"""
import sys
import re
import csv
import argparse
import pathlib

HERE = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
REPO = HERE.parents[3]
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402

csv.field_size_limit(10 * 1024 * 1024)

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
OUTCOMES_NO_VERBO = {"otro", "sin_dispositivo"}
RE_PERF = re.compile(
    r"\bse\s+(resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
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


def chunk_de(bloque, k):
    chunk, n, m = [], 0, k
    while n < 6 and m < len(bloque):
        ln = bloque[m]; m += 1; s = ln.strip()
        if not s:
            continue
        chunk.append(ln); n += 1
        if s.endswith("."):
            break
    return " ".join(chunk).strip()


def tiene_firma(bloque, k):
    return any(P.linea_es_firma_de_juez(bloque[j]) for j in range(k + 1, min(k + 41, len(bloque))))


def es_cand(s):
    d = []
    if P._cand_estructural(s): d.append("E")
    if P._cand_t2(s): d.append("t2")
    if P._cand_t3b(s): d.append("t3b")
    if P._cand_t4(s): d.append("t4")
    return d


def reproducir_full(bloque):
    zonas, _ = P.zonificar_bloque(bloque)
    ld = {k for k, z in enumerate(zonas) if z == "dictamen"}
    lr = {k for k, z in enumerate(zonas) if z == "residuo_caso_anterior"}
    lex = {k for k, z in enumerate(zonas) if z not in ZONAS_FALLO}
    _, ar = P.detectar_apertura_en_bloque(bloque)
    _, _, ivi, _ = P.detectar_votos_disidencias(bloque, lex)
    nc = set(ld) | lr
    if ivi is not None:
        nc |= set(range(ivi, len(bloque)))
    return zonas, ld, ar, ivi, nc


def _barrer_P(bloque, rango, ld, *, exd, cand, fb):
    inicio, fin = rango
    fbi = fbt = li = lt = None
    for k in range(inicio, fin):
        if exd and k in ld:
            continue
        s = bloque[k].strip()
        if not s or not cand(s):
            continue
        txt = chunk_de(bloque, k)
        f = tiene_firma(bloque, k)
        if f:
            if RE_PERF.search(txt):
                return k, txt
            if li is None:
                li, lt = k, txt
        elif fb and fbi is None:
            fbi, fbt = k, txt
    if li is not None:
        return li, lt
    return (fbi, fbt) if (fb and fbi is not None) else (None, None)


def resolver_P(bloque, ar, ld, ivi):
    de = max(ld) if ld else None
    inicio = ar if ar is not None else (de + 1 if de is not None else 0)
    fin = ivi if (ivi is not None and (ar is None or ivi > ar)) else len(bloque)
    Rg = {"base": (inicio, fin), "base_full": (inicio, len(bloque)), "zero_full": (0, len(bloque))}
    for cand, rt, exd, fb in TIERS:
        i, t = _barrer_P(bloque, Rg[rt], ld, exd=exd, cand=cand, fb=fb)
        if i is not None:
            return i, t
    return None, None


def outcome_de(bloque, idx, txt, nc):
    if idx is None:
        return "sin_dispositivo"
    return P.classify_outcome(txt, P.extraer_considerando(bloque, idx, nc))


def _norm(s):
    return " ".join(str(s or "").split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos",  default=str(REPO / "output" / "parser" / "csjn_casos.csv"))
    ap.add_argument("--textos", default=str(REPO / "output" / "parser" / "csjn_casos_textos.csv"))
    ap.add_argument("--corpus", default=str(REPO / "corpus"))
    args = ap.parse_args()

    corpus = pathlib.Path(args.corpus)
    cache = {}

    def lines_de(sf):
        if sf not in cache:
            p = pathlib.Path(sf)
            if not p.is_absolute():
                p = corpus / sf
            cache[sf] = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
        return cache[sf]

    pe_csv = {}
    with open(args.textos, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pe_csv[r["caso_id_canonico"]] = r.get("por_ello_text", "")
    with open(args.casos, encoding="utf-8") as f:
        casos = list(csv.DictReader(f))

    rotos = []
    for c in casos:
        cid = c["caso_id_canonico"]
        sf, li, lfr = c.get("source_file", ""), c.get("linea_inicio", ""), c.get("linea_fin_real", "")
        lines = lines_de(sf) if sf else None
        if lines is None:
            continue
        try:
            li_i = int(li); lfr_i = int(lfr) if str(lfr) != "" else None
        except (ValueError, TypeError):
            continue
        bloque = P.construir_bloque_desde_localizacion(lines, li_i, lfr_i)
        if not bloque:
            continue
        zonas, ld, ar, ivi, nc = reproducir_full(bloque)
        ia, ta = P.resolver_dispositivo(bloque, ar, ld, ivi)
        if _norm(ta) != _norm(pe_csv.get(cid, "")):   # gate: reconstruccion fiel
            continue
        oc_a = outcome_de(bloque, ia, ta, nc)
        ip, tp = resolver_P(bloque, ar, ld, ivi)
        oc_p = outcome_de(bloque, ip, tp, nc)
        if oc_a != "otro" and oc_p != oc_a:           # roto de P
            rotos.append((cid, bloque, zonas, ar, ivi, ia, oc_a, ip, oc_p))

    print("=" * 100)
    print(f"AUTOPSIA ROTOS DE P  ·  parser v{P.__version__}  ·  total rotos: {len(rotos)}")
    print("=" * 100)
    for cid, bloque, zonas, ar, ivi, ia, oc_a, ip, oc_p in rotos:
        de = max((k for k, z in enumerate(zonas) if z == "dictamen"), default=None)
        inicio = ar if ar is not None else (de + 1 if de is not None else 0)
        fin = ivi if (ivi is not None and (ar is None or ivi > ar)) else len(bloque)
        print(f"\n### {cid}   actual={oc_a} (idx {ia})  ->  P={oc_p} (idx {ip})   rango=[{inicio},{fin}) len={len(bloque)}")
        lo, hi = max(0, inicio - 2), min(len(bloque), fin + 4)
        for k in range(lo, hi):
            s = bloque[k].strip()
            if not s or not es_cand(s):
                continue
            txt = chunk_de(bloque, k)
            f = "si" if tiene_firma(bloque, k) else "."
            pf = "si" if RE_PERF.search(txt) else "."
            mark = " <-actual" if k == ia else (" <-P" if k == ip else "")
            z = zonas[k] if k < len(zonas) else "?"
            print(f"    {k:>4} {z:<12} f={f:<3} perf={pf:<3} {P.classify_outcome(txt, ''):<14} {txt[:78]}{mark}")


if __name__ == "__main__":
    main()
