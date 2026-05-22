"""
poc_b076.py — PoC B076: suprimir firma_linea en sumario.

Uso (desde raiz del repo):
    python scripts/auditoria/poc_b076.py
"""
import sys, csv
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "pipeline"))

import parser as P

ZONAS_BASELINE = REPO / "output" / "parser" / "csjn_casos_zonas.csv"
LOC_CSV = REPO / "output" / "localizacion" / "fallos_localizados.csv"
CORPUS_DIR = REPO / "corpus"
OUT_DIR = REPO / "output" / "auditoria"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DIFF_CSV = OUT_DIR / "b076_diff.csv"


def cargar_baseline():
    casos = defaultdict(list)
    with open(ZONAS_BASELINE, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            casos[row["caso_id_canonico"]].append(row)
    return casos


def detectar_sospechosos(baseline):
    sosp = set()
    for cid, segs in baseline.items():
        for i, seg in enumerate(segs):
            if seg["zona"] != "firma":
                continue
            prev_z = next((segs[j]["zona"] for j in range(i-1, -1, -1)
                           if segs[j]["zona"] != "header_pagina"), None)
            next_z = next((segs[j]["zona"] for j in range(i+1, len(segs))
                           if segs[j]["zona"] != "header_pagina"), None)
            if prev_z == "sumario" and next_z in ("sumario", None):
                sosp.add(cid)
    return sosp


def cargar_localizados():
    idx = {}
    with open(LOC_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            idx[row["caso_id_canonico"]] = row
    return idx


_md_cache = {}

def cargar_md(archivo):
    if archivo not in _md_cache:
        ruta = CORPUS_DIR / archivo
        if not ruta.exists():
            _md_cache[archivo] = None
        else:
            _md_cache[archivo] = ruta.read_text(encoding="utf-8").split("\n")
    return _md_cache[archivo]


def reparsear(cid, loc_row):
    archivo = loc_row.get("archivo", "")
    if not archivo:
        return None
    lines = cargar_md(archivo)
    if lines is None:
        return None
    li = loc_row.get("linea_inicio", "")
    lf = loc_row.get("linea_fin", "")
    if not li:
        return None
    bloque = P.construir_bloque_desde_localizacion(lines, li, lf)
    if not bloque:
        return None
    zonas, _anclas = P.zonificar_bloque(bloque)
    return P.extraer_segmentos(zonas, bloque)


def wc_by_zona(segs):
    c = Counter()
    for s in segs:
        c[s["zona"]] += int(s.get("wc", 0))
    return c


def main():
    print("=" * 60)
    print("PoC B076 — firma espuria en sumario")
    print("=" * 60)

    baseline = cargar_baseline()
    print(f"Baseline: {len(baseline)} casos, {sum(len(v) for v in baseline.values())} segmentos.")

    sospechosos = detectar_sospechosos(baseline)
    print(f"Sospechosos: {len(sospechosos)} casos.")

    loc = cargar_localizados()
    print(f"Localizados: {len(loc)} filas.\n")

    diffs = []
    ok = 0
    errores = 0
    delta_global = Counter()

    for cid in sorted(sospechosos):
        if cid not in loc:
            errores += 1
            continue
        try:
            new_segs = reparsear(cid, loc[cid])
        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"  ERROR {cid}: {e}")
            continue
        if new_segs is None:
            errores += 1
            continue

        bl_wc = wc_by_zona(baseline[cid])
        nw_wc = wc_by_zona(new_segs)
        zonas_all = set(bl_wc) | set(nw_wc)
        for z in zonas_all:
            d = nw_wc.get(z, 0) - bl_wc.get(z, 0)
            if d != 0:
                delta_global[z] += d
                diffs.append({"caso": cid, "zona": z,
                              "wc_pre": bl_wc.get(z, 0),
                              "wc_post": nw_wc.get(z, 0),
                              "delta_wc": d})
        ok += 1

    print(f"Procesados: {ok}.  Errores/skip: {errores}.\n")

    print("DELTA WC POR ZONA (global):")
    for z in sorted(delta_global):
        d = delta_global[z]
        print(f"  {z:<28} {'+' if d>0 else ''}{d}")

    regr = [r for r in diffs if r["zona"] in ("cuerpo", "dispositivo", "voto_separado") and r["delta_wc"] != 0]
    print(f"\nREGRESIONES (cuerpo/disp/voto): {len(regr)}")
    for r in regr[:15]:
        print(f"  {r['caso']}: {r['zona']} {r['delta_wc']:+d}")

    if diffs:
        with open(DIFF_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["caso","zona","wc_pre","wc_post","delta_wc"])
            w.writeheader()
            w.writerows(diffs)
        print(f"\nDiff CSV: {DIFF_CSV}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
