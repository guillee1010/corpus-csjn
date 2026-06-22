#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_epilogos.py — Vuelca el texto CRUDO de la zona `epilogo` de cada fallo a
un sidecar (insumo de la capa de partes, M29).

Arquitectura (REE): determinístico, NO muta nada, y **emite el universo COMPLETO
de fallos** (1:1 con casos.csv, tipo_entrada=fallo) — NO solo los que tienen
zona epilogo. Los fallos sin epílogo se emiten con `epilogo_status` explícito
(`sin_zona` / `archivo_no_encontrado`), nunca se omiten en silencio: así la
ausencia es AUDITABLE (¿el fallo no tiene epílogo, o el detector de zonas no se
lo marcó?), no una muerte silenciosa.

Lee los spans `epilogo` de csjn_casos_zonas.csv (líneas RELATIVAS al caso:
offset = linea_inicio del caso, verbatim del flujo H055) y el corpus crudo.
Mismo patrón sidecar que csjn_casos_textos.csv. El derivador de partes lee ESTE
csv, NO el .md → reproducible para Dataverse.

Se guarda el texto CRUDO (con saltos de línea): los marcadores del epílogo
(`Recurso ... interpuesto por`, `Tribunal de origen:`) están anclados a inicio
de línea. La des-hifenación y el parseo viven en `derivar_partes.py`.

NOTA offset: replica el cálculo de H055 (`linea_ini + linea_inicio`, 0-based
sobre `.split("\\n")`). No se validó en sandbox por falta del corpus crudo; si
hubiera corrimiento, es lo primero a revisar.
"""
from __future__ import annotations
import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

__version__ = "0.2"  # H154: emite los 5697 fallos con epilogo_status (no solo los 4345 con zona). // 0.1: solo casos con zona (muerte silenciosa de los sin-epilogo) -- corregido.

csv.field_size_limit(10 ** 7)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent.parent
DEFAULT_ZONAS  = REPO_ROOT / "output" / "parser" / "csjn_casos_zonas.csv"
DEFAULT_CASOS  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_CORPUS = REPO_ROOT / "corpus"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "parser" / "csjn_casos_epilogo.csv"

REQUIRED_ZONAS = ("caso_id_canonico", "zona", "linea_ini", "linea_fin")
REQUIRED_CASOS = ("caso_id_canonico", "tomo", "source_file", "linea_inicio",
                  "tipo_entrada")

OUT_COLS = ["caso_id_canonico", "tomo", "source_file", "epilogo_status",
            "n_seg", "wc", "epilogo_text"]


def _abrir_required(path: Path, required: tuple):
    if not path.exists():
        sys.exit(f"[FATAL] no existe: {path}")
    fh = path.open(encoding="utf-8", newline="")
    rd = csv.DictReader(fh)
    faltan = [c for c in required if c not in (rd.fieldnames or [])]
    if faltan:
        sys.exit(f"[FATAL] faltan columnas en {path}: {faltan}")
    return rd, fh


def derivar(zonas_path: Path, casos_path: Path, corpus_dir: Path,
            output_path: Path) -> dict:
    # spans `epilogo` por caso
    rd, fh = _abrir_required(zonas_path, REQUIRED_ZONAS)
    spans = defaultdict(list)
    with fh:
        for r in rd:
            if r["zona"] == "epilogo":
                spans[r["caso_id_canonico"]].append(
                    (int(r["linea_ini"]), int(r["linea_fin"])))

    # cache del corpus
    cache: dict[str, list | None] = {}
    def get_lines(sf: str):
        if sf not in cache:
            p = corpus_dir / sf
            cache[sf] = (p.read_text(encoding="utf-8").split("\n")
                         if p.exists() else None)
        return cache[sf]

    # universo: TODOS los fallos de casos.csv (1:1)
    rd, fh = _abrir_required(casos_path, REQUIRED_CASOS)
    salida = []
    st = Counter()
    sin_archivo = Counter()
    with fh:
        for r in rd:
            if r.get("tipo_entrada") != "fallo":
                continue
            cid = r["caso_id_canonico"]
            sf = r["source_file"]
            li_caso = int(r["linea_inicio"]) if r["linea_inicio"] else 0
            segs = spans.get(cid, [])
            status, texto, wc = "sin_zona", "", 0
            if segs:
                lines = get_lines(sf)
                if lines is None:
                    status = "archivo_no_encontrado"
                    sin_archivo[sf] += 1
                else:
                    bloques = []
                    for (li, lf) in sorted(segs):
                        ini = li + li_caso
                        fin = lf + li_caso
                        bloques.append("\n".join(lines[ini:min(fin + 1, len(lines))]))
                    texto = "\n".join(bloques).strip("\n")
                    wc = len(texto.split())
                    status = "ok"
            salida.append({
                "caso_id_canonico": cid, "tomo": r["tomo"], "source_file": sf,
                "epilogo_status": status, "n_seg": len(segs), "wc": wc,
                "epilogo_text": texto,
            })
            st[status] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(salida)

    return {"n": len(salida), "status": st, "sin_archivo": dict(sin_archivo)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Extrae el texto crudo de la zona epilogo (universo de fallos).")
    ap.add_argument("--zonas", type=Path, default=DEFAULT_ZONAS)
    ap.add_argument("--casos", type=Path, default=DEFAULT_CASOS)
    ap.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args(argv)

    s = derivar(args.zonas, args.casos, args.corpus_dir, args.output)
    st = s["status"]
    print(f"\n  extraer_epilogos v{__version__}")
    print(f"  fallos emitidos (1:1): {s['n']}")
    for k in ("ok", "sin_zona", "archivo_no_encontrado"):
        v = st.get(k, 0)
        pct = f"({100*v/s['n']:5.1f}%)" if s["n"] else ""
        print(f"    {k:22s} {v:5d}  {pct}")
    if s["sin_archivo"]:
        print(f"  [WARN] source_file no encontrado en corpus-dir:")
        for sf, n in s["sin_archivo"].items():
            print(f"    {sf}: {n}")
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
