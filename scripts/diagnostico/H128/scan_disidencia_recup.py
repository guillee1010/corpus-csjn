#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_disidencia_recup.py — control de calidad de las RECUPERACIONES de P (otro->real).

Sobre los 5890, toma SOLO los casos que P recupera (actual=otro -> P=outcome real) y, para
cada uno, chequea si el pick de P cae DESPUES de un encabezado de voto/disidencia separado
(la firma de la regresion 346_p931: P se mete en el dispositivo del voto perdedor). Para los
sospechosos imprime el pick de P + el encabezado + los candidatos-con-firma ANTES del
encabezado (= el dispositivo de la mayoria que P salteo), para leerlos a ojo.

NO toca nada. Mismo schema/logica que impacto_P_clitico (RE_PERF con clitico H129).

Uso:
  python scan_disidencia_recup.py
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
NO_UTIL = {"otro", "sin_dispositivo"}
RE_PERF = re.compile(
    r"\bse\s+(?:(?:lo|la|los|las|le|les)\s+)?"
    r"(resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
    r"hace[n]?\s+lugar|deja[n]?\s+sin\s+efecto|rechaza[n]?|desestima[n]?|"
    r"tiene[n]?\s+por|admite[n]?|anula[n]?|hace\s+saber|intima)\b",
    re.IGNORECASE)
# Encabezado de voto/disidencia SEPARADO (a principio de linea). NO matchea la anotacion
# de firma "(en disidencia)" (esa va inline, no a principio de linea).
RE_VOTO_HEAD = re.compile(
    r"^\s*(disidencia\b|voto\s+(?:del?\b|de\s+l[ao]s?\b|conjunto\b|concurrente\b|en\s+disidencia\b))",
    re.I)
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


def es_cand(s):
    return (P._cand_estructural(s) or P._cand_t2(s) or P._cand_t3b(s) or P._cand_t4(s))


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

    n_recup = 0
    sospechosos = []   # (cid, oc_p, pick_idx, head_idx, ivi, head_txt, pick_txt, cands_antes)

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

        ld, ar, ivi, nc = reproducir_full(bloque)
        ia, ta = P.resolver_dispositivo(bloque, ar, ld, ivi)
        if _norm(ta) != _norm(pe_csv.get(cid, "")):
            continue
        oc_a = outcome_de(bloque, ia, ta, nc)
        if oc_a != "otro":
            continue
        ip, tp = resolver_P(bloque, ar, ld, ivi)
        oc_p = outcome_de(bloque, ip, tp, nc)
        if oc_p in NO_UTIL or ip is None:
            continue
        # es una RECUPERACION (otro -> real)
        n_recup += 1

        de = max(ld) if ld else None
        inicio = ar if ar is not None else (de + 1 if de is not None else 0)
        heads = [k for k in range(inicio, ip) if RE_VOTO_HEAD.search(bloque[k].strip())]
        if not heads:
            continue
        h0 = heads[0]
        # candidatos-con-firma ANTES del encabezado = dispositivo de la mayoria que P salteo
        cands_antes = []
        for k in range(inicio, h0):
            s = bloque[k].strip()
            if s and es_cand(s) and tiene_firma(bloque, k):
                txt = chunk_de(bloque, k)
                perf = "perf" if RE_PERF.search(txt) else "no-perf"
                cands_antes.append((k, perf, txt[:90]))
        sospechosos.append((cid, oc_p, ip, h0, ivi,
                            _norm(bloque[h0])[:80], _norm(tp)[:100], cands_antes))

    print("=" * 96)
    print(f"SCAN DISIDENCIA · recuperaciones de P (otro->real)  ·  parser v{P.__version__}")
    print("=" * 96)
    print(f"recuperaciones totales (otro->real): {n_recup}")
    print(f"SOSPECHOSAS (pick de P despues de un encabezado voto/disidencia): {len(sospechosos)}")
    print(f"LIMPIAS: {n_recup - len(sospechosos)}")
    if not sospechosos:
        print("\n>> 0 sospechosas: ninguna recuperacion cae en zona de voto/disidencia separado.")
        print("   Las 119 recuperaciones no tocan votos perdedores -> P queda airtight.")
    for cid, oc_p, ip, h0, ivi, head_txt, pick_txt, cands in sospechosos:
        print("\n" + "-" * 90)
        print(f"### {cid}   otro -> {oc_p}   pick_P=idx {ip}   encabezado_voto=idx {h0}   ivi={ivi}")
        print(f"    encabezado: {head_txt}")
        print(f"    pick P    : {pick_txt}")
        if cands:
            print("    candidatos-con-firma ANTES del encabezado (= mayoria que P salteo):")
            for k, perf, t in cands:
                print(f"       idx {k:>5} [{perf:<7}] {t}")
        else:
            print("    (sin candidatos-con-firma antes del encabezado)")


if __name__ == "__main__":
    main()
