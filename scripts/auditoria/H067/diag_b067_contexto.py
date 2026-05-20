"""
Diagnóstico B067 — Contexto real de las 17 mejoras
====================================================
Muestra para cada caso mejorado:
  - El header de voto que causó el techo (first_voto)
  - El dispositivo encontrado por Tier 3
  - La firma detectada
  - ±3 líneas de contexto alrededor de cada uno
"""

import re, sys, csv
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
for _c in [_SCRIPT_DIR.parent, _SCRIPT_DIR.parent.parent / "scripts",
           _SCRIPT_DIR / "scripts", _SCRIPT_DIR]:
    if (_c / "pipeline" / "parser.py").exists():
        sys.path.insert(0, str(_c))
        break

from pipeline.parser import (
    RE_APERTURA, RE_FECHA_LINEA, RE_DICT_HDR, RE_VOTO_HDR, RE_DISID_HDR,
    detectar_apertura_dispositivo, detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion, detectar_fin_real,
    cargar_proximos_headers, cargar_localizados,
    proximo_header_despues_de, primer_token_de_caratula,
    linea_es_firma_de_juez, collect_firma_lines, parse_firma,
    refinar_inicio_por_titulo, POR_ELLO_ARGUMENTAL,
)

_REPO_ROOT = None
for _c in [_SCRIPT_DIR.parent.parent, _SCRIPT_DIR.parent, _SCRIPT_DIR]:
    if (_c / "corpus").exists() and (_c / "output").exists():
        _REPO_ROOT = _c; break
if _REPO_ROOT is None:
    _REPO_ROOT = _SCRIPT_DIR

TARGETS = [
    "329_p2218", "329_p2827", "330_p3141", "330_p3801", "330_p399",
    "331_p1013", "332_p2237", "332_p5", "340_p204",
    "341_p424", "343_p1024", "343_p1758", "343_p300",
    "344_p575", "344_p757",
    "347_p1084", "347_p1353", "347_p2160", "348_p728",
]

CTX = 3


def show_context(bloque, k, label, ctx=CTX):
    ini = max(0, k - ctx)
    fin = min(len(bloque) - 1, k + ctx)
    print(f"  ┌─ {label} (k={k}) ─")
    for j in range(ini, fin + 1):
        prefix = "▶" if j == k else " "
        ln = bloque[j].rstrip()
        if len(ln) > 110:
            ln = ln[:107] + "..."
        print(f"  {prefix} {j:>5} │ {ln}")
    print(f"  └─")


def main():
    filas_loc, _ = cargar_localizados(
        str(_REPO_ROOT / "output/localizacion/fallos_localizados.csv"))
    hpa = cargar_proximos_headers(
        str(_REPO_ROOT / "output/mapa/mapa_paginas.csv"))
    loc = {r["caso_id_canonico"]: r for r in filas_loc}

    cat = {}
    for r in filas_loc:
        cat.setdefault(int(r["tomo"]), []).append(r)
    for t in cat:
        cat[t].sort(key=lambda r: int(r["pagina_inicio"]))
    sig = {}
    ptk = {}
    for t, lst in cat.items():
        for i, c in enumerate(lst[:-1]):
            sig[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]
        for c in lst:
            ptk[c["caso_id_canonico"]] = primer_token_de_caratula(
                c.get("nombres_indice", ""))

    corpus = _REPO_ROOT / "corpus"

    for cid in TARGETS:
        f = loc.get(cid)
        if not f:
            continue
        tomo = int(f["tomo"])
        fp = corpus / f["archivo"]
        if not fp.exists():
            continue
        lines = fp.read_text(encoding="utf-8").split("\n")
        li = int(f["linea_inicio"])
        lf_raw = f.get("linea_fin", "")
        lf = int(lf_raw) if lf_raw.strip() else len(lines) - 1
        s = sig.get(cid)
        pt = ptk.get(s, "") if s else ""
        ha = sorted(hpa.get((tomo, f["archivo"]), []))
        ph = proximo_header_despues_de(ha, lf)
        lfr, _, _ = detectar_fin_real(lines, li, lf, ph, pt)
        bloque = construir_bloque_desde_localizacion(lines, li, lfr)
        if not bloque:
            continue
        off, _ = refinar_inicio_por_titulo(bloque, f.get("nombres_indice", ""))
        if off > 0:
            bloque = bloque[off:]

        _, ap = detectar_apertura_en_bloque(bloque)

        # Find first voto/disid (el que causa el techo)
        first_voto = None
        first_voto_text = ""
        for k, bl in enumerate(bloque):
            s2 = bl.strip()
            if RE_VOTO_HDR.match(s2) or RE_DISID_HDR.match(s2):
                first_voto = k
                first_voto_text = s2[:100]
                break

        # Find dispositivo post-voto (lo que Tier 3 encuentra)
        disp_k = None
        disp_text = ""
        en_dictamen = False
        lineas_dict = set()
        for k, bl in enumerate(bloque):
            s2 = bl.strip()
            if not s2:
                continue
            if RE_DICT_HDR.match(s2):
                en_dictamen = True
                lineas_dict.add(k)
                continue
            elif en_dictamen:
                if RE_APERTURA.match(s2):
                    en_dictamen = False
                else:
                    lineas_dict.add(k)
                    if RE_FECHA_LINEA.match(s2) and k > 5:
                        prev = bloque[k-1].strip() if k > 0 else ""
                        if prev and len(prev) < 80:
                            en_dictamen = False
                    continue

        inicio_b = ap if ap is not None else (
            max(lineas_dict) + 1 if lineas_dict else 0)
        for k in range(inicio_b, len(bloque)):
            if k in lineas_dict:
                continue
            s2 = bloque[k].strip()
            if not s2:
                continue
            es, _ = detectar_apertura_dispositivo(s2)
            if es:
                if any(linea_es_firma_de_juez(bloque[j])
                       for j in range(k+1, min(k+41, len(bloque)))):
                    disp_k = k
                    disp_text = s2[:100]
                    break

        # Firma
        firma_raw = ""
        firma_jueces = ""
        vp = "sin_firma"
        if disp_k is not None:
            firma_raw = collect_firma_lines(bloque, disp_k + 1)
            if firma_raw:
                fp2 = parse_firma(firma_raw)
                vp = fp2["voting_pattern"]
                firma_jueces = " | ".join(j["nombre"] for j in fp2["jueces"])

        # Find firma start line for context
        firma_start_k = None
        if disp_k is not None:
            for k in range(disp_k + 1, min(disp_k + 30, len(bloque))):
                if linea_es_firma_de_juez(bloque[k].strip()):
                    firma_start_k = k
                    break

        # Output
        ni = f.get("nombres_indice", "")[:80]
        print(f"\n{'='*75}")
        print(f"{cid} — {ni}")
        print(f"Bloque: {len(bloque)} líneas | apertura={ap} | "
              f"first_voto={first_voto} | disp={disp_k} | vp={vp}")
        print(f"Jueces: {firma_jueces or '(sin firma)'}")

        if first_voto is not None:
            print()
            show_context(bloque, first_voto, "VOTO/DISID que causó el techo")

        if disp_k is not None:
            print()
            show_context(bloque, disp_k, "DISPOSITIVO (Tier 3)")

        if firma_start_k is not None:
            print()
            show_context(bloque, firma_start_k, "FIRMA")

        if first_voto is not None and disp_k is not None:
            gap = disp_k - first_voto
            print(f"\n  Distancia voto→dispositivo: {gap} líneas")

    print(f"\n{'='*75}")
    print("Fin del diagnóstico")


if __name__ == "__main__":
    main()
