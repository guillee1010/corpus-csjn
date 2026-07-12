"""
poc_b159_superficie.py — v0.1 (H195)
====================================

PoC READ-ONLY de superficie para B159: dump corpus-wide de todos los
matches de RE_DICT_HDR (el ancla dictamen_inicio del zonificador) con
clasificacion por forma, para calibrar el discriminador FP-narrativo
vs. header genuino ANTES de tocar el parser.

Hallazgo H195 (lectura de los 7 .md): 6/7 casos B159 son FP de
RE_DICT_HDR — prosa del cuerpo cuyo wrap del OCR deja "dictamen de
la/del Procura..." a inicio de linea, y re.I la matchea. 1/7
(332_p2418) es dictamen genuino como nota al pie "(*) Dicho dictamen
dice asi:" intercalado (clase aparte).

No modifica nada: lee corpus/*.md y opcionalmente cruza contra
output/parser/csjn_casos.csv para mapear cada match a su caso.

Ejes MEDIDOS por match (ninguno decidido como discriminador todavia):
  minuscula     'd' inicial (el header genuino se espera 'D'; espejo H139)
  forma_titulo  la linea entera es SOLO el titulo (variantes conocidas),
                sin cola de prosa
  prev_abierta  la linea sustantiva anterior (salteando vacias y banners
                RE_PAGE_HEADER, verbatim del parser) NO cierra en
                puntuacion fuerte -> candidata a continuacion de wrap
                (espejo _es_continuacion_wrap / H190-b)

Ademas cuenta el marcador de nota al pie "(*) Dicho dictamen dice asi"
para dimensionar la clase A corpus-wide.

Uso (raiz del repo):
  python scripts/diagnostico/H195/poc_b159_superficie.py
  python scripts/diagnostico/H195/poc_b159_superficie.py --corpus corpus \
         --casos output/parser/csjn_casos.csv \
         --out scripts/diagnostico/H195/poc_b159_superficie.csv
"""

import re
import csv
import argparse
import sys
from pathlib import Path

__version__ = "0.1"

# ── Regex del parser, VERBATIM (parser.py v30.0) ─────────────────────
# Gate 3: no se reinventa la deteccion — el PoC replica exactamente lo
# que el zonificador ve.
RE_DICT_HDR = re.compile(
    r"^Dictamen\s+de(l)?\s+(la\s+)?Procura", re.I
)  # parser.py L188

RE_PAGE_HEADER = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACIÓN|"
    r"DE JUSTICIA DE LA NACION|\d{2,6})\s*$", re.I
)  # parser.py (skip de banners para buscar la linea anterior sustantiva)

# ── Instrumentos de medicion propios del PoC (NO son el fix) ─────────

# Forma-titulo: la linea es SOLO el titulo del dictamen, en sus
# variantes observadas, sin cola de prosa. Proxy medible; los misfits
# quedan a la vista en el dump.
RE_FORMA_TITULO = re.compile(
    r"^Dictamen\s+de(?:l)?\s+(?:la\s+)?Procura(?:ci[oó]n|dor)"
    r"(?:\s+General)?(?:\s+de\s+la\s+Naci[oó]n)?"
    r"(?:\s+\(\*?\)?)?\s*[.:]?\s*$",
    re.I,
)

# Puntuacion que CIERRA una linea (para prev_abierta). El guion de
# corte de palabra ("extradi-") cuenta como ABIERTA.
RE_CIERRE_FUERTE = re.compile(r"[.:;!?\u2026]\s*$|[.:;!?]\u2013?\s*$")

# Clase A: nota al pie que introduce un dictamen de otra causa.
RE_NOTA_DICTAMEN = re.compile(
    r"^\(\*\)\s*Dicho dictamen dice as[ií]", re.I
)


def linea_prev_sustantiva(lines, i):
    """Ultima linea no vacia y no-banner antes de i. Retorna (idx, texto)
    o (None, '')."""
    j = i - 1
    while j >= 0:
        s = lines[j].strip()
        if s and not RE_PAGE_HEADER.match(s):
            return j, s
        j -= 1
    return None, ""


def cargar_indice_casos(path_casos):
    """Indice source_file -> [(li, lf, caso_id)] desde csjn_casos.csv.

    Fail-soft: si el CSV no tiene las columnas esperadas, imprime el
    header real y devuelve None (el dump sale igual, sin caso_id).
    """
    esperadas = {"caso_id_canonico", "source_file", "linea_inicio",
                 "linea_fin_real"}
    idx = {}
    with open(path_casos, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        campos = set(reader.fieldnames or [])
        if not esperadas.issubset(campos):
            print(f"[WARN] {path_casos}: no encuentro columnas "
                  f"{sorted(esperadas - campos)}.")
            print(f"       Header real: {reader.fieldnames}")
            print("       Sigo sin el cruce a caso_id (dump igual sale).")
            return None
        for r in reader:
            try:
                li = int(r["linea_inicio"])
                lf = int(r["linea_fin_real"])
            except (ValueError, TypeError):
                continue
            idx.setdefault(r["source_file"], []).append(
                (li, lf, r["caso_id_canonico"]))
    for v in idx.values():
        v.sort()
    return idx


def caso_de(idx, source_file, linea):
    if not idx:
        return ""
    for li, lf, cid in idx.get(source_file, []):
        if li <= linea <= lf:
            return cid
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus",
                    help="directorio con los .md fuente (default: corpus)")
    ap.add_argument("--casos", default="output/parser/csjn_casos.csv",
                    help="csjn_casos.csv para mapear match -> caso_id "
                         "(opcional; fail-soft si no esta o difiere)")
    ap.add_argument("--out",
                    default="scripts/diagnostico/H195/poc_b159_superficie.csv")
    args = ap.parse_args()

    corpus = Path(args.corpus)
    archivos = sorted(corpus.glob("*.md"))
    if not archivos:
        sys.exit(f"[FATAL] no hay .md en {corpus.resolve()}")

    idx_casos = None
    if args.casos and Path(args.casos).exists():
        idx_casos = cargar_indice_casos(args.casos)
    else:
        print(f"[WARN] no encuentro {args.casos}; dump sin caso_id.")

    filas = []
    n_notas = 0
    for f in archivos:
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, raw in enumerate(lines):
            s = raw.strip()
            if not s:
                continue
            if RE_NOTA_DICTAMEN.match(s):
                n_notas += 1
                filas.append({
                    "source_file": f.name, "linea": i,
                    "tipo": "nota_al_pie",
                    "minuscula": 0, "forma_titulo": 0, "prev_abierta": "",
                    "caso_id": caso_de(idx_casos, f.name, i),
                    "linea_prev": "", "texto": s[:120],
                })
                continue
            if not RE_DICT_HDR.match(s):
                continue
            _, prev = linea_prev_sustantiva(lines, i)
            filas.append({
                "source_file": f.name, "linea": i,
                "tipo": "match_dict_hdr",
                "minuscula": int(s[0].islower()),
                "forma_titulo": int(bool(RE_FORMA_TITULO.match(s))),
                "prev_abierta": int(not RE_CIERRE_FUERTE.search(prev))
                                if prev else "",
                "caso_id": caso_de(idx_casos, f.name, i),
                "linea_prev": prev[:120],
                "texto": s[:120],
            })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    campos = ["source_file", "linea", "tipo", "minuscula", "forma_titulo",
              "prev_abierta", "caso_id", "linea_prev", "texto"]
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)

    # ── Resumen ──────────────────────────────────────────────────────
    matches = [r for r in filas if r["tipo"] == "match_dict_hdr"]
    print(f"\npoc_b159_superficie v{__version__}")
    print(f"  archivos escaneados : {len(archivos)}")
    print(f"  matches RE_DICT_HDR : {len(matches)}")
    print(f"  notas al pie '(*)'  : {n_notas}")
    print("\n  minuscula x forma_titulo x prev_abierta:")
    combos = {}
    for r in matches:
        k = (r["minuscula"], r["forma_titulo"], r["prev_abierta"])
        combos[k] = combos.get(k, 0) + 1
    for k in sorted(combos, key=lambda x: -combos[x]):
        print(f"    min={k[0]} titulo={k[1]} prev_abierta={k[2]}: "
              f"{combos[k]}")

    testigos = {"332_p2418", "334_p109", "337_p1006", "337_p166",
                "339_p662", "344_p1952", "344_p2123"}
    en_testigos = [r for r in matches if r["caso_id"] in testigos]
    if idx_casos:
        print(f"\n  matches dentro de los 7 testigos B159: "
              f"{len(en_testigos)}")
        for r in en_testigos:
            print(f"    {r['caso_id']:<11} {r['source_file']} "
                  f"L{r['linea']} min={r['minuscula']} "
                  f"titulo={r['forma_titulo']} | {r['texto'][:60]}")
    print(f"\n[OK] {out}: {len(filas)} filas")


if __name__ == "__main__":
    main()
