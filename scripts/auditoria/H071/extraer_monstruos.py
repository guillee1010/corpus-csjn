"""
extraer_monstruos.py — H071
Extrae spans de casos anómalos del corpus .md a un solo archivo para inspección.
Trunca casos > MAX_LINES a primeras/últimas TRUNC líneas.

Uso:
    python scripts/auditoria/H071/extraer_monstruos.py

Ubicación: scripts/auditoria/H071/
Requiere: csjn_casos.csv en output/parser/, corpus .md en corpus/
Salida:   output/diagnostico/monstruos_h071.md
"""

import csv
from pathlib import Path
from collections import defaultdict

# ── Config ──────────────────────────────────────────────────────────────
MAX_LINES = 800     # si el span supera esto, truncar
TRUNC = 200         # cuántas líneas mostrar al inicio y al final del truncado

REPO = Path(__file__).resolve().parent.parent.parent.parent  # scripts/auditoria/H071 → repo root
CSV_PATH = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUT_DIR = REPO / "output" / "diagnostico"
OUT_FILE = OUT_DIR / "monstruos_h071.md"

# Casos a extraer, agrupados por categoría
TARGETS = {
    "MONSTRUO (wc extremo o inconsistente)": [
        "330_p2849",   # 110k wc, 13k líneas
        "333_p1474",   # wcD=56k, wc=1249
        "342_p1827",   # wcD=7k, wc=442
    ],
    "wcM=1 + unanime (posible segun_su_voto no detectado)": [
        "329_p2218",
        "329_p2433",
        "329_p2680",
        "329_p6032",
    ],
    "wcC > wcM sin dictamen (considerando fuera del span)": [
        "333_p280",
        "329_p85",
        "329_p4403",
        "329_p3928",
        "329_p5683",
    ],
    "sin_dispositivo + firma presente": [
        "329_p317",
        "334_p109",
        "337_p166",
        "344_p2779",
    ],
}

# ── Leer CSV ────────────────────────────────────────────────────────────
all_ids = set()
for ids in TARGETS.values():
    all_ids.update(ids)

cases = {}
with open(CSV_PATH, encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        cid = row["caso_id_canonico"]
        if cid in all_ids:
            cases[cid] = row

missing = all_ids - set(cases.keys())
if missing:
    print(f"⚠ Casos no encontrados en CSV: {missing}")

# ── Agrupar por source_file ─────────────────────────────────────────────
by_file = defaultdict(list)
for cid, row in cases.items():
    by_file[row["source_file"]].append((cid, row))

# ── Extraer ──────────────────────────────────────────────────────────────
OUT_DIR.mkdir(parents=True, exist_ok=True)
extracts = {}  # cid -> (metadata_str, lines_list)

for src_file, entries in sorted(by_file.items()):
    fpath = CORPUS_DIR / src_file
    if not fpath.exists():
        print(f"⚠ Archivo no encontrado: {fpath}")
        for cid, _ in entries:
            extracts[cid] = (f"ARCHIVO NO ENCONTRADO: {src_file}", [])
        continue

    print(f"Leyendo {src_file}...")
    with open(fpath, encoding="utf-8") as fh:
        all_lines = fh.readlines()

    for cid, row in entries:
        li = int(row["linea_inicio"]) - 1   # 0-based
        lf = int(row["linea_fin_real"])       # exclusive
        span = all_lines[li:lf]
        n_span = len(span)

        meta = (
            f"caso_id: {cid} | source: {src_file} | "
            f"líneas {row['linea_inicio']}–{row['linea_fin_real']} ({n_span} líneas)\n"
            f"wc={row['word_count']} wcM={row['wc_mayoria']} wcC={row['wc_considerando']} "
            f"wcD={row['wc_dictamen']} wcV={row['wc_votos']}\n"
            f"outcome={row['outcome']} vp={row['voting_pattern']} n_jueces={row['n_jueces']}\n"
            f"firma: {row['firma_raw'][:100]}\n"
            f"case_name: {row['case_name_cuerpo'][:120] if row['case_name_cuerpo'] else 'N/A'}"
        )

        if n_span > MAX_LINES:
            head = span[:TRUNC]
            tail = span[-TRUNC:]
            omitted = n_span - 2 * TRUNC
            truncated = (
                head
                + [f"\n[... {omitted} líneas omitidas ...]\n\n"]
                + tail
            )
            meta += f"\n⚠ TRUNCADO: mostrando primeras/últimas {TRUNC} de {n_span} líneas"
            extracts[cid] = (meta, truncated)
        else:
            extracts[cid] = (meta, span)

# ── Escribir archivo de salida ───────────────────────────────────────────
with open(OUT_FILE, "w", encoding="utf-8") as out:
    out.write("# Monstruos H071 — Extracto de casos anómalos\n\n")
    out.write(f"Generado por extraer_monstruos.py\n")
    out.write(f"Total casos: {len(all_ids)}\n\n")
    out.write("---\n\n")

    for category, ids in TARGETS.items():
        out.write(f"## {category}\n\n")
        for cid in ids:
            if cid not in extracts:
                out.write(f"### {cid} — NO ENCONTRADO\n\n")
                continue
            meta, lines = extracts[cid]
            out.write(f"### {cid}\n\n")
            out.write(f"```\n{meta}\n```\n\n")
            if lines:
                out.write("```\n")
                for line in lines:
                    out.write(line)
                if not lines[-1].endswith("\n"):
                    out.write("\n")
                out.write("```\n\n")
            else:
                out.write("*(sin contenido)*\n\n")
            out.write("---\n\n")

n_extracted = sum(1 for m, l in extracts.values() if l)
total_lines = sum(len(l) for _, l in extracts.values())
print(f"\n✓ {n_extracted}/{len(all_ids)} casos extraídos")
print(f"  {total_lines} líneas totales")
print(f"  Salida: {OUT_FILE}")
