"""debug_h036.py — Debug de casos sin_firma con pipeline real."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from pipeline.parser import (
    RE_DICT_HDR, RE_FECHA_LINEA, RE_APERTURA,
    cargar_localizados, cargar_proximos_headers,
    construir_bloque_desde_localizacion, detectar_fin_real,
    refinar_inicio_por_titulo, detectar_apertura_en_bloque,
    detectar_apertura_dispositivo, primer_token_de_caratula,
    proximo_header_despues_de,
)

loc_rows, _ = cargar_localizados(str(REPO / "output/localizacion/fallos_localizados.csv"))
headers_map = cargar_proximos_headers(str(REPO / "output/mapa/mapa_paginas.csv"))

cat_por_tomo = {}
for row in loc_rows:
    cat_por_tomo.setdefault(int(row["tomo"]), []).append({
        "caso_id_canonico": row["caso_id_canonico"],
        "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
    })
for t in cat_por_tomo:
    cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])

siguiente_caso = {}
primer_token_por_caso = {}
for t, lst in cat_por_tomo.items():
    for i, c in enumerate(lst[:-1]):
        siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]
for row in loc_rows:
    primer_token_por_caso[row["caso_id_canonico"]] = primer_token_de_caratula(
        row.get("nombres_indice", "")
    )

test_ids = ["329_p6064", "340_p812", "330_p1305", "348_p1569"]

for cid in test_ids:
    fallo = [r for r in loc_rows if r["caso_id_canonico"] == cid]
    if not fallo:
        print(f"{cid}: NO ENCONTRADO")
        continue
    fallo = fallo[0]
    tomo = int(fallo["tomo"])
    archivo = fallo["archivo"]
    fp = REPO / "corpus" / archivo
    if not fp.exists():
        print(f"{cid}: archivo {archivo} no encontrado")
        continue
    lines = fp.read_text(encoding="utf-8").split("\n")
    li = int(fallo["linea_inicio"])
    lf_cat = int(fallo["linea_fin"]) if fallo["linea_fin"] else len(lines) - 1

    sig = siguiente_caso.get(cid)
    pt_sig = primer_token_por_caso.get(sig, "") if sig else ""
    ha = list(headers_map.get((tomo, archivo), []))
    ha.sort()
    prox_h = proximo_header_despues_de(ha, lf_cat)
    lfr, sf, pf = detectar_fin_real(lines, li, lf_cat, prox_h, pt_sig)

    bloque = construir_bloque_desde_localizacion(lines, li, lfr)
    offset, ancla = refinar_inicio_por_titulo(bloque, fallo.get("nombres_indice", ""))
    bloque = bloque[offset:]
    li_eff = li + offset

    at, ar = detectar_apertura_en_bloque(bloque)

    en_dict = False
    dict_lines = set()
    for k, bl in enumerate(bloque):
        s = bl.strip()
        if not s:
            continue
        if RE_DICT_HDR.match(s):
            en_dict = True
            dict_lines.add(k)
            continue
        elif en_dict:
            dict_lines.add(k)
            if RE_FECHA_LINEA.match(s) and k > 5:
                prev = bloque[k - 1].strip() if k > 0 else ""
                if prev and len(prev) < 80:
                    en_dict = False
            continue

    dictamen_end = max(dict_lines) if dict_lines else None
    if ar is not None:
        ib = ar
    elif dictamen_end is not None:
        ib = dictamen_end + 1
    else:
        ib = 0
    fb = len(bloque)
    pe_idx = None
    for k in range(ib, fb):
        if k in dict_lines:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        es, tipo = detectar_apertura_dispositivo(s)
        if es:
            pe_idx = k
            break

    print(f"=== {cid} ===")
    print(f"  linea_inicio={li} fin_cat={lf_cat} fin_real={lfr} ({sf}/{pf})")
    print(f"  offset={offset} ancla={ancla} bloque={len(bloque)}")
    print(f"  apertura: tipo={at} rel={ar}")
    print(f"  dictamen: {len(dict_lines)} lines, en_dict_final={en_dict}")
    if en_dict:
        last_d = max(dict_lines)
        print(f"  !! DICTAMEN NO CERRADO - ultima linea dict k={last_d} abs={li_eff+last_d}")
        print(f"     contenido: {bloque[last_d].strip()[:80]}")
    if pe_idx is not None:
        print(f"  dispositivo: idx={pe_idx} -> {bloque[pe_idx].strip()[:80]}")
    else:
        print(f"  dispositivo: NO ENCONTRADO")
        print(f"  ultimas 8 lineas:")
        for k in range(max(0, len(bloque) - 8), len(bloque)):
            ind = k in dict_lines
            print(f"    k={k} dict={ind}: {bloque[k].strip()[:70]}")
    print()
