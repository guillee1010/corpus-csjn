#!/usr/bin/env python3
"""
H048 — Contexto alrededor del corte para los 57 sin_firma_post_fallo.

Muestra: últimas 10 líneas del bloque + 20 líneas DESPUÉS de linea_fin_real.
Objetivo: ver si la firma está justo después del corte.

Genera: output/auditoria/H048/contexto_corte_57.md

Uso:
  python scripts/auditoria/H048/contexto_corte_57.py
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
CSV_PATH = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUTPUT_DIR = REPO / "output" / "auditoria" / "H048"

sys.path.insert(0, str(REPO / "scripts" / "pipeline"))
from parser import JUECES_CONOCIDOS, linea_es_firma_de_juez

import pandas as pd

df = pd.read_csv(CSV_PATH)
sf = df[df["voting_pattern"] == "sin_firma"].copy()
sf["span"] = sf["linea_fin_real"] - sf["linea_inicio"]
ga = sf[(sf["span"] >= 20) & (sf["apertura_tipo"] == "fallo")].copy()

print(f"Grupo A: {len(ga)} casos")

_file_cache = {}
def cargar_archivo(source_file):
    if source_file not in _file_cache:
        path = CORPUS_DIR / source_file
        if not path.exists():
            _file_cache[source_file] = []
        else:
            with open(path, "r", encoding="utf-8") as f:
                _file_cache[source_file] = f.readlines()
    return _file_cache[source_file]


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUTPUT_DIR / "contexto_corte_57.md"

# Counters
firma_post_corte = 0
firma_en_bloque = 0
sin_firma_real = 0

with open(out_path, "w", encoding="utf-8") as out:
    out.write("# H048 — Contexto alrededor del corte (57 sin_firma_post_fallo)\n\n")
    out.write("Para cada caso: últimas 10 líneas del bloque + 20 líneas post-corte.\n")
    out.write("La línea `>>> CORTE (linea_fin_real) <<<` marca dónde termina el bloque.\n\n")
    out.write("---\n\n")

    for _, row in ga.sort_values("caso_id_canonico").iterrows():
        caso_id = row["caso_id_canonico"]
        src = row["source_file"]
        li = int(row["linea_inicio"])
        lfr = int(row["linea_fin_real"])
        lf = int(row["linea_fin"])

        lines = cargar_archivo(src)
        if not lines:
            out.write(f"### {caso_id} — ARCHIVO NO ENCONTRADO\n\n---\n\n")
            continue

        # Últimas 10 del bloque
        pre_start = max(li, lfr - 9)
        pre_lines = lines[pre_start:lfr + 1]

        # 20 líneas post-corte
        post_start = lfr + 1
        post_end = min(len(lines), post_start + 20)
        post_lines = lines[post_start:post_end]

        # Check: is there a firma in the post-corte zone?
        firma_encontrada_post = False
        firma_linea_post = None
        for k, line in enumerate(post_lines):
            if linea_es_firma_de_juez(line):
                firma_encontrada_post = True
                firma_linea_post = k
                break

        # Also check: any JUECES_CONOCIDOS match in post zone?
        juez_match_post = []
        for k, line in enumerate(post_lines):
            s = line.strip()
            for pat, nombre in JUECES_CONOCIDOS:
                if pat.search(s):
                    juez_match_post.append((k, nombre, s[:80]))
                    break

        if firma_encontrada_post:
            firma_post_corte += 1
            tag = "✅ FIRMA POST-CORTE"
        elif juez_match_post:
            firma_en_bloque += 1
            tag = "⚠️ JUEZ POST-CORTE (no pasa linea_es_firma)"
        else:
            sin_firma_real += 1
            tag = "❌ SIN FIRMA"

        out.write(f"### {caso_id} — {tag}\n\n")
        out.write(f"- source: `{src}` L{li}–{lfr} (lf={lf})\n")
        out.write(f"- case_name: {row['case_name_indice']}\n")
        out.write(f"- span: {lfr - li} líneas\n")
        if juez_match_post:
            for k, nombre, texto in juez_match_post:
                out.write(f"- juez post-corte: **{nombre}** en línea +{k}: `{texto}`\n")

        out.write(f"\n```\n")
        # Pre-corte
        for k, line in enumerate(pre_lines):
            lineno = pre_start + k
            out.write(f"L{lineno:6d}  {line.rstrip()}\n")

        out.write(f"\n{'='*60}\n")
        out.write(f">>> CORTE (linea_fin_real = {lfr}) <<<\n")
        out.write(f"{'='*60}\n\n")

        # Post-corte
        for k, line in enumerate(post_lines):
            lineno = post_start + k
            marker = " <<<FIRMA" if firma_encontrada_post and k == firma_linea_post else ""
            out.write(f"L{lineno:6d}  {line.rstrip()}{marker}\n")

        out.write(f"```\n\n---\n\n")

    # Resumen
    out.write(f"## Resumen\n\n")
    out.write(f"| Categoría | Casos |\n|-----------|------:|\n")
    out.write(f"| ✅ Firma detectada post-corte | {firma_post_corte} |\n")
    out.write(f"| ⚠️ Juez post-corte (no pasa linea_es_firma) | {firma_en_bloque} |\n")
    out.write(f"| ❌ Sin firma real | {sin_firma_real} |\n")
    out.write(f"| **Total** | **{firma_post_corte + firma_en_bloque + sin_firma_real}** |\n")

print(f"\nGenerado: {out_path}")
print(f"\n=== RESUMEN ===")
print(f"✅ Firma detectada post-corte: {firma_post_corte}")
print(f"⚠️ Juez post-corte (no pasa linea_es_firma): {firma_en_bloque}")
print(f"❌ Sin firma real: {sin_firma_real}")
print(f"Total: {firma_post_corte + firma_en_bloque + sin_firma_real}")
