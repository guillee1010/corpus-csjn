"""
extraer_sin_disp.py — H071
Extrae los 27 sin_dispositivo + firma restantes.

Uso: python scripts/auditoria/H071/extraer_sin_disp.py
Salida: output/diagnostico/sin_disp_h071.md
"""
import csv
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent.parent.parent.parent
CSV_PATH = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUT_FILE = REPO / "output" / "diagnostico" / "sin_disp_h071.md"

TARGETS = [
    "329_p317", "329_p3444", "329_p4590", "329_p991",
    "330_p1172", "330_p1971", "330_p22", "330_p4590",
    "331_p1013", "331_p2363", "332_p2418",
    "333_p1140", "333_p1784",
    "334_p1033", "334_p109", "334_p362",
    "337_p1006",
    "339_p662", "339_p676",
    "340_p1392",
    "343_p473", "343_p720",
    "344_p1952", "344_p776", "344_p997",
    "346_p1068",
    "348_p532",
]

all_ids = set(TARGETS)
cases = {}
with open(CSV_PATH, encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        if row["caso_id_canonico"] in all_ids:
            cases[row["caso_id_canonico"]] = row

by_file = defaultdict(list)
for cid, row in cases.items():
    by_file[row["source_file"]].append((cid, row))

extracts = {}
for src_file, entries in sorted(by_file.items()):
    fpath = CORPUS_DIR / src_file
    if not fpath.exists():
        print(f"⚠ {fpath}")
        for cid, _ in entries:
            extracts[cid] = ("NO ENCONTRADO", [])
        continue
    print(f"Leyendo {src_file}...")
    with open(fpath, encoding="utf-8") as fh:
        all_lines = fh.readlines()
    for cid, row in entries:
        li = int(row["linea_inicio"]) - 1
        lf = int(row["linea_fin_real"])
        span = all_lines[li:lf]
        meta = (
            f"caso_id: {cid} | source: {src_file} | "
            f"líneas {row['linea_inicio']}–{row['linea_fin_real']} ({len(span)} líneas)\n"
            f"wc={row['word_count']} wcM={row['wc_mayoria']} wcC={row['wc_considerando']} "
            f"wcD={row['wc_dictamen']} wcV={row['wc_votos']}\n"
            f"outcome={row['outcome']} vp={row['voting_pattern']} n_jueces={row['n_jueces']}\n"
            f"firma: {row['firma_raw'][:100]}\n"
            f"case_name: {row['case_name_cuerpo'][:120] if row['case_name_cuerpo'] else 'N/A'}"
        )
        extracts[cid] = (meta, span)

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as out:
    out.write("# sin_dispositivo + firma — 27 casos restantes (H071)\n\n---\n\n")
    for cid in TARGETS:
        meta, lines = extracts.get(cid, ("NO ENCONTRADO", []))
        out.write(f"### {cid}\n\n```\n{meta}\n```\n\n")
        if lines:
            out.write("```\n")
            for line in lines:
                out.write(line)
            if lines and not lines[-1].endswith("\n"):
                out.write("\n")
            out.write("```\n\n---\n\n")

print(f"\n✓ {len(extracts)} casos → {OUT_FILE}")
