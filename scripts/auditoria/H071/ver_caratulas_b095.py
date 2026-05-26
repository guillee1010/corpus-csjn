"""
ver_caratulas_b095.py — Muestra las carátulas reales en el .md fuente
para los 51 casos ancla_catalogo con token corto.

Uso:
    python scripts/auditoria/H075/ver_caratulas_b095.py
"""

import csv
import re
from pathlib import Path

_script_dir = Path(__file__).resolve().parent
if (_script_dir / "output" / "parser" / "csjn_casos.csv").exists():
    REPO_ROOT = _script_dir
elif (_script_dir.parent.parent.parent / "output" / "parser" / "csjn_casos.csv").exists():
    REPO_ROOT = _script_dir.parent.parent.parent
else:
    REPO_ROOT = Path.cwd()

CSV_PATH = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"
WINDOW = 25

_SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
         "empresa", "compania", "compañia", "compañía"}
_GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
              "afip", "buenos", "nacional", "administracion",
              "federal", "direccion", "instituto"}

def primer_token(nombres_indice):
    if not nombres_indice:
        return ""
    variantes = nombres_indice.split("|")
    for v in variantes:
        tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", v.strip())
        for t in tokens:
            if len(t) >= 4 and t.lower() not in _SKIP and t.lower() not in _GENERICOS:
                return t
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", variantes[0].strip())
    for t in tokens:
        if len(t) >= 4 and t.lower() not in _SKIP:
            return t
    return tokens[0] if tokens else ""

def main():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    target = []
    for r in rows:
        if "ancla_catalogo" not in r["status_localizacion"]:
            continue
        tok = primer_token(r["case_name_indice"])
        if len(tok) < 4:
            target.append((r, tok))

    md_cache = {}

    for i, (r, tok) in enumerate(target):
        source = r["source_file"]
        li = int(r["linea_inicio"])

        md_path = CORPUS_DIR / source
        if source not in md_cache:
            if not md_path.exists():
                print(f"[{i+1:02d}] {r['caso_id_canonico']} — {md_path} no existe")
                continue
            md_cache[source] = md_path.read_text(encoding="utf-8").splitlines()
        lines = md_cache[source]

        bloque = lines[li:li + WINDOW]

        print(f"══ [{i+1:02d}/51] {r['caso_id_canonico']} — índice: {r['case_name_indice'].split('|')[0].strip()} ══")
        for k, ln in enumerate(bloque):
            print(f"  +{k:02d}  {ln.rstrip()[:90]}")
        print()

if __name__ == "__main__":
    main()
