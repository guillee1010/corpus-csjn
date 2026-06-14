#!/usr/bin/env python3
"""
Diagnóstico H125 — ¿el FIX completa el por_ello?
================================================
Dumpea, por caso, el por_ello bajo 3 configs: baseline / +masking / +masking+skip.
Lectura: con +masking+skip el por_ello debería SUMAR el texto que está después del
banner (p.ej. "...corresponde a la competencia originaria de la Corte") y el
outcome flipear a competencia. Si +masking corta igual que baseline y solo
+masking+skip completa → confirma que el fix son las DOS mitades.

Uso:
    python scripts\\diagnostico\\h125\\diag_textos.py --corpus corpus \\
      --casos output\\parser\\csjn_casos.csv --mapa output\\mapa\\mapa_paginas.csv \\
      --pipeline scripts\\pipeline 329_p1917 348_p1576 329_p551
"""
import argparse
import poc_normalizar as H
import normalizar_bloque as N


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--casos", required=True)
    ap.add_argument("--mapa", required=True)
    ap.add_argument("--pipeline", required=True)
    ap.add_argument("cids", nargs="+")
    ap.add_argument("--chars", type=int, default=500)
    a = ap.parse_args()

    P = H._import_parser(a.pipeline)
    skip_fn = H.make_barrer_skip(P)
    casos = H.cargar_casos_index(a.casos)
    mapa = H.cargar_mapa(a.mapa)
    cache = {}
    C = a.chars

    cfgs = {
        "baseline":      dict(headers=False, guion=False, skip=False),
        "+masking":      dict(headers=True,  guion=False, skip=False),
        "+masking+skip": dict(headers=True,  guion=False, skip=True),
    }

    for cid in a.cids:
        m = casos.get(cid)
        print("=" * 76)
        if not m:
            print(f"### {cid}: NO está en el índice"); continue
        bloque = H.reconstruir_bloque(P, a.corpus, m["source_file"],
                                      m["linea_inicio"], m["linea_fin_real"], cache)
        if not bloque:
            print(f"### {cid}: bloque no reconstruible"); continue
        offs = N.offsets_relativos(mapa.get(m["source_file"], []),
                                   m["linea_inicio"], m["linea_fin_real"])
        case_name = H._case_name_crudo(P, bloque)
        out = {}
        for name, cfg in cfgs.items():
            d = {}
            r = H.extraer_bajo_config(P, bloque, offs, cfg, d, skip_fn)
            r["ternas"] = d.get("ternas", 0)
            r["es_originaria"] = bool(
                P.es_originaria(case_name, r["considerando_text"], r["por_ello_text"]))
            out[name] = r

        print(f"### {cid}  ({m['source_file']})  ternas(+masking)={out['+masking']['ternas']}")
        for name in cfgs:
            r = out[name]
            print(f"  {name:14}  outcome={r['outcome']!r:16}  "
                  f"es_originaria={r['es_originaria']}  dictamen={r['dictamen_presente']}")
        for name in cfgs:
            print(f"\n  POR_ELLO [{name}]:\n    {out[name]['por_ello_text'][:C]}")
        print()


if __name__ == "__main__":
    main()
