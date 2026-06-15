#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
impacto_P_clitico.py — A/B corpus-wide: regla P (RE_PERF con clitico H129) vs parser ACTUAL.

Recorre los 5890 y clasifica CADA cambio de outcome (actual -> P) en CORRIGE / ROMPE,
con matriz de transicion y listado explicito de los que rompe para leerlos a ojo.
Solo casos con reconstruccion fiel (por_ello actual == csjn_casos_textos). NO toca nada.

Categorias:
  CORRIGE:
    - recupera : actual=otro            -> P=outcome real
    - reubica  : actual=real            -> P=real distinto   (los rotos auditados)
    - desvacio : actual=sin_dispositivo -> P=real
  ROMPE:
    - real -> {otro, sin_dispositivo}
  NEUTRO/borde:
    - otro <-> sin_dispositivo

Uso:
  python impacto_P_clitico.py
  (mismo schema de paths que autopsia_rotos_P: dejar en scripts/diagnostico/H12X/)
"""
import sys
import re
import csv
import argparse
import pathlib
from collections import Counter

HERE = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
REPO = HERE.parents[3]
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402

csv.field_size_limit(10 * 1024 * 1024)

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
NO_UTIL = {"otro", "sin_dispositivo"}
# RE_PERF H129: clitico opcional entre "se" y el verbo (igual que en la autopsia/cruce parcheados).
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
    return any(P.linea_es_firma_de_juez(bloque[j])
               for j in range(k + 1, min(k + 41, len(bloque))))


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
    return ld, ar, ivi, nc


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

    n_total = len(casos)
    n_eval = 0
    n_no_fiel = 0
    n_no_reco = 0
    sin_cambio = 0
    recupera = []     # otro -> real            (CORRIGE)
    reubica = []      # real -> real distinto   (CORRIGE, = rotos auditados)
    desvacio = []     # sin_dispositivo -> real (CORRIGE)
    rompe = []        # real -> {otro, sin_dispositivo}
    neutro = []       # otro <-> sin_dispositivo / bordes
    matriz = Counter()

    for c in casos:
        cid = c["caso_id_canonico"]
        sf, li, lfr = c.get("source_file", ""), c.get("linea_inicio", ""), c.get("linea_fin_real", "")
        lines = lines_de(sf) if sf else None
        if lines is None:
            n_no_reco += 1; continue
        try:
            li_i = int(li); lfr_i = int(lfr) if str(lfr) != "" else None
        except (ValueError, TypeError):
            n_no_reco += 1; continue
        bloque = P.construir_bloque_desde_localizacion(lines, li_i, lfr_i)
        if not bloque:
            n_no_reco += 1; continue

        ld, ar, ivi, nc = reproducir_full(bloque)
        ia, ta = P.resolver_dispositivo(bloque, ar, ld, ivi)
        if _norm(ta) != _norm(pe_csv.get(cid, "")):
            n_no_fiel += 1; continue
        n_eval += 1

        oc_a = outcome_de(bloque, ia, ta, nc)
        ip, tp = resolver_P(bloque, ar, ld, ivi)
        oc_p = outcome_de(bloque, ip, tp, nc)

        if oc_a == oc_p:
            sin_cambio += 1; continue
        matriz[(oc_a, oc_p)] += 1
        a_util = oc_a not in NO_UTIL
        p_util = oc_p not in NO_UTIL
        if not a_util and p_util:
            (recupera if oc_a == "otro" else desvacio).append((cid, oc_a, oc_p))
        elif a_util and p_util:
            reubica.append((cid, oc_a, oc_p))
        elif a_util and not p_util:
            rompe.append((cid, oc_a, oc_p))
        else:
            neutro.append((cid, oc_a, oc_p))

    corrige_total = len(recupera) + len(reubica) + len(desvacio)
    rompe_total = len(rompe)

    print("=" * 92)
    print(f"IMPACTO REGLA P (clitico H129) vs ACTUAL  ·  parser v{P.__version__}")
    print("=" * 92)
    print(f"casos en csjn_casos        : {n_total}")
    print(f"evaluados (reconstr. fiel) : {n_eval}")
    print(f"  descartados no-fiel      : {n_no_fiel}   (gate por_ello actual != CSV; t345 etc.)")
    print(f"  no reconstruibles        : {n_no_reco}")
    print(f"  sin cambio actual==P     : {sin_cambio}")
    print()
    print(f"==> CORRIGE : {corrige_total}")
    print(f"      recupera (otro -> real)             : {len(recupera)}")
    print(f"      reubica  (real -> real distinto)    : {len(reubica)}   <- los rotos auditados")
    print(f"      recupera desde sin_dispositivo      : {len(desvacio)}")
    print(f"==> ROMPE   : {rompe_total}")
    print(f"      real -> otro / sin_dispositivo      : {len(rompe)}")
    print(f"    NEUTRO/borde (otro<->sin_dispositivo) : {len(neutro)}")
    print()
    print(f"==> NETO (corrige - rompe) : {corrige_total - rompe_total}")
    print()

    if rompe:
        print("--- ROMPE (real -> otro/vacio) — LEER uno por uno ---")
        for cid, a, p in sorted(rompe):
            print(f"    [{cid}]  {a} -> {p}")
    else:
        print("--- ROMPE: 0 casos (ningun real -> otro/sin_dispositivo) ---")

    if neutro:
        print("\n--- NEUTRO/borde (otro<->sin_dispositivo), hasta 40 ---")
        for cid, a, p in sorted(neutro)[:40]:
            print(f"    [{cid}]  {a} -> {p}")

    print("\n--- matriz de transicion (actual -> P), top 30 ---")
    for (a, p), n in matriz.most_common(30):
        print(f"    {a:>22} -> {p:<22} {n}")


if __name__ == "__main__":
    main()
