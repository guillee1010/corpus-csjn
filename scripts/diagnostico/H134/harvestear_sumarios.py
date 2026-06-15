#!/usr/bin/env python3
# scripts/diagnostico/H134/harvestear_sumarios.py   (diagnostico, no produccion)
# -----------------------------------------------------------------------------
# Harvest del SUMARIO EDITORIAL (voces de la Secretaria de Jurisprudencia) y,
# opcional, del DICTAMEN del Procurador, para los casos arbitrariedad/mixto.
#
# Motivo (H134): tipo_cuestion_federal=mixto sobre-dispara (677 vs 1 humano) y la
# causal de arbitrariedad NO vive en el considerando -que en los casos de remision
# es solo "comparte y hace suyos el dictamen"- sino en (a) el LEAF del sumario
# editorial = vocabulario controlado de la Secretaria, y (b) el dictamen. El
# parser arma sumario_text = bloque[:apertura_rel] (parser.py:3535-3543) y lo usa
# en classify_cuestion_federal, pero NO lo persiste. Esto lo recupera a escala.
#
# REE: NO reimplementa la zonificacion. Reusa del parser, fuente unica:
#   - construir_bloque_desde_localizacion  -> mismo bloque que arma el parser
#   - detectar_apertura_en_bloque          -> mismo apertura_rel (= "FALLO DE LA
#                                             CORTE SUPREMA"; el dictamen va antes)
#   - _unhyphenate                         -> misma normalizacion base
# El split sumario_editorial | dictamen es por el header "Dictamen de la
# Procuracion". OJO normalizacion: este dump usa _unhyphenate (como extraer_caso),
# que NO limpia el soft-hyphen sin espacio; el analisis aguas abajo re-normaliza
# con clasificador_disposicion.norm para igualar lo que ve el detector.
#
# Solo LEE el corpus y vuelca un CSV. No toca el golden ni el manifest.
#
# Uso (desde la raiz del repo o cualquier subdir):
#   python scripts/diagnostico/H134/harvestear_sumarios.py
#   python scripts/diagnostico/H134/harvestear_sumarios.py --limit 50      # prueba
#   python scripts/diagnostico/H134/harvestear_sumarios.py --con-dictamen  # +dictamen (CSV grande)
#   python scripts/diagnostico/H134/harvestear_sumarios.py --todos          # los 5890
#   python scripts/diagnostico/H134/harvestear_sumarios.py --out ruta.csv
# -----------------------------------------------------------------------------

__version__ = "0.1"

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

csv.field_size_limit(10 ** 7)


def _find_root(start: Path) -> Path:
    """Sube hasta la raiz del repo (marcador: scripts/pipeline/parser.py)."""
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start.parents[2] if len(start.parents) >= 3 else start


ROOT = _find_root(Path(__file__).resolve().parent)
PIPELINE_DIR = ROOT / "scripts" / "pipeline"
CSV_CANONICO = ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = ROOT / "corpus"
OUT_DEFAULT = ROOT / "diagnostico" / "H134" / "sumarios_arbitrariedad.csv"

# Header del dictamen -> split sumario editorial | dictamen.
RE_DICTAMEN = re.compile(r"dictamen\s+de(?:l)?\s+(?:la\s+)?procuraci[oó]n", re.I)

# Preview de voces-causal de la Secretaria (subcategorias de "Sentencias
# arbitrarias"). NO es el clasificador final: es para ver la taxonomia emerger a
# escala. La lista definitiva se deriva de la columna sumario_editorial del CSV.
VOCES_PREVIEW = {
    "exceso_ritual":              r"exceso\s+ritual|excesivo\s+(?:rigor|ritualismo)|injustificado\s+rigor\s+formal",
    "excesos_u_omisiones":        r"excesos?\s+u?\s*omisiones?\s+en\s+el\s+pronunciamiento",
    "defectos_fundam_normativa":  r"defectos?\s+en\s+la\s+fundamentaci[oó]n\s+normativa",
    "defectos_extremos_conduc":   r"defectos?\s+en\s+la\s+consideraci[oó]n\s+de\s+(?:los\s+)?extremos\s+conducentes",
    "valoracion_prueba":          r"valoraci[oó]n\s+de\s+la\s+prueba|arbitraria\s+valoraci[oó]n",
    "apartam_constancias":        r"apartamiento\s+de\s+(?:las\s+)?constancias|constancias\s+(?:comprobadas\s+)?de\s+la\s+causa",
    "apartam_norma":              r"apartamiento\s+de\s+la\s+soluci[oó]n\s+normativa|prescind\w+\s+del\s+texto\s+legal",
    "fundam_aparente":            r"fundament\w*\s+(?:s[oó]lo\s+)?aparent|aparent\w+\s+fundament|derivaci[oó]n\s+razonad",
    "afirm_dogmaticas":           r"afirmaci\w+\s+dogm[aá]tic",
    "sola_voluntad":              r"sola\s+voluntad\s+de\s+los\s+jueces",
    "arbitrariedad_sorpresiva":   r"arbitrariedad\s+sorpresiva",
    "gravedad_institucional":     r"gravedad\s+institucional",   # ortogonal -> flag aparte
}
VOCES_PREVIEW = {k: re.compile(v, re.I) for k, v in VOCES_PREVIEW.items()}


def cargar_parser():
    if str(PIPELINE_DIR) not in sys.path:
        sys.path.insert(0, str(PIPELINE_DIR))
    import parser as p  # resuelve al scripts/pipeline/parser.py local
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(CSV_CANONICO))
    ap.add_argument("--corpus-dir", default=str(CORPUS_DIR))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--limit", type=int, default=0, help="solo N casos (prueba)")
    ap.add_argument("--todos", action="store_true",
                    help="los 5890, no solo arbitrariedad/mixto")
    ap.add_argument("--con-dictamen", action="store_true",
                    help="incluye la columna dictamen_text (CSV mucho mas grande)")
    args = ap.parse_args()

    P = cargar_parser()

    def norm(t):
        return re.sub(r"\s+", " ", P._unhyphenate(t or "")).strip()

    # ── filas objetivo ───────────────────────────────────────────────────────
    filas = []
    with open(args.csv, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("tipo_entrada") != "fallo":
                continue
            tcf = r.get("tipo_cuestion_federal", "")
            if args.todos or tcf in ("arbitrariedad", "mixto"):
                filas.append(r)
    if args.limit:
        filas = filas[: args.limit]
    print(f"[harvest v{__version__}]  raiz={ROOT}")
    print(f"  casos objetivo: {len(filas)}  ({'todos' if args.todos else 'arbitrariedad+mixto'})")

    # ── cache de .md por source_file ─────────────────────────────────────────
    cache = {}

    def lines_de(sf):
        if sf not in cache:
            mf = Path(args.corpus_dir) / sf
            cache[sf] = mf.read_text(encoding="utf-8").splitlines() if mf.exists() else None
        return cache[sf]

    out_rows = []
    sin_md = sin_apertura = sin_dictamen = 0
    voz_count = Counter()

    for r in filas:
        cid = r["caso_id_canonico"]
        sf = (r.get("source_file") or "").strip()
        li = (r.get("linea_inicio") or "").strip()
        lfr = (r.get("linea_fin_real") or r.get("linea_fin") or "").strip()

        lines = lines_de(sf)
        if lines is None or not li or not lfr:
            sin_md += 1
            continue

        bloque = list(P.construir_bloque_desde_localizacion(lines, int(li), int(lfr)))
        _, apertura_rel = P.detectar_apertura_en_bloque(bloque)
        if apertura_rel is None:
            sin_apertura += 1
            pre = bloque               # sin marcador: todo el bloque (espejo del parser)
        else:
            pre = bloque[:apertura_rel]

        # split sumario editorial | dictamen
        dic_idx = next((i for i, ln in enumerate(pre) if RE_DICTAMEN.search(ln)), None)
        if dic_idx is None:
            sin_dictamen += 1
            sumario = norm(" ".join(pre))
            dictamen = ""
        else:
            sumario = norm(" ".join(pre[:dic_idx]))
            dictamen = norm(" ".join(pre[dic_idx:]))

        for k, rx in VOCES_PREVIEW.items():
            if rx.search(sumario):
                voz_count[k] += 1

        row = {
            "caso_id_canonico": cid,
            "tipo_cuestion_federal": r.get("tipo_cuestion_federal", ""),
            "source_file": sf,
            "tiene_apertura": "no" if apertura_rel is None else "si",
            "tiene_dictamen": "no" if dic_idx is None else "si",
            "sumario_editorial": sumario,
        }
        if args.con_dictamen:
            row["dictamen_text"] = dictamen
        out_rows.append(row)

    if not out_rows:
        sys.exit("[FATAL] 0 filas extraidas; revisa --corpus-dir y el CSV.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    print(f"[escrito] {out}  ({len(out_rows)} filas)")
    print(f"  sin .md: {sin_md}  | sin marcador FALLO: {sin_apertura}  | sin dictamen: {sin_dictamen}")
    print("  preview voces-causal de la Secretaria en el sumario editorial:")
    for k, n in voz_count.most_common():
        print(f"    {n:>5}  {k}")
    no_arb = len(out_rows) - sum(1 for _ in out_rows
                                 if any(rx.search(_['sumario_editorial']) for rx in VOCES_PREVIEW.values()))
    print(f"  sin ninguna voz-causal del preview: {no_arb}  (candidatos a ampliar diccionario)")


if __name__ == "__main__":
    main()
