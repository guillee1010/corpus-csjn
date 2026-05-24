"""
H061 — Extracción y crosscheck de entries del INDICE POR NOMBRES DE LAS PARTES.

Parsea las entries de todas las secciones indice_partes y cruza contra
csjn_casos.csv para detectar:
  - Entries del índice sin caso correspondiente en el parser (MISS)
  - Casos del parser sin entry correspondiente en el índice (EXTRA)

Genera:
  - output/parser/csjn_editorial_indice_partes.csv (entries parseadas)
  - Reporte de crosscheck a stdout

Correr: python scripts/auditoria/H061/crosscheck_indice_partes.py
"""
import re
import sys
import pandas as pd
from pathlib import Path

# Resolver repo root
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
while REPO_ROOT != REPO_ROOT.parent:
    if (REPO_ROOT / "corpus").is_dir() and (REPO_ROOT / "output").is_dir():
        break
    REPO_ROOT = REPO_ROOT.parent
else:
    print("ERROR: no encontré la raíz del repo")
    sys.exit(1)

# Agregar scripts/pipeline al path para importar parser_editorial
sys.path.insert(0, str(REPO_ROOT / "scripts" / "pipeline"))
from parser_editorial import parsear_indice_partes

CORPUS = REPO_ROOT / "corpus"
EDITORIAL_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos_editorial.csv"
CASOS_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "parser" / "csjn_editorial_indice_partes.csv"


def main():
    df_ed = pd.read_csv(EDITORIAL_CSV)
    df_ip = df_ed[df_ed["subtipo"] == "indice_partes"].copy()
    print(f"Secciones indice_partes: {len(df_ip)}")

    # ── Parsear entries ───────────────────────────────────────────────
    todas = []
    for _, row in df_ip.iterrows():
        sf = row["source_file"]
        fp = CORPUS / sf
        if not fp.exists():
            print(f"  SKIP {sf} (no encontrado)")
            continue

        lines = fp.read_text(encoding="utf-8").splitlines()
        li = int(row["linea_ini"])
        lf = min(int(row["linea_fin"]), len(lines) - 1)
        tomo = int(row["tomo"])

        entries = parsear_indice_partes(lines, li, lf, tomo, sf)
        todas.extend(entries)

        n_ok = sum(1 for e in entries if e["paginas"])
        n_inc = sum(1 for e in entries if not e["paginas"])
        print(f"  T{tomo:3d} {sf:30s}  {n_ok:4d} entries"
              + (f"  ({n_inc} incompletas)" if n_inc else ""))

    df_entries = pd.DataFrame(todas)
    print(f"\nTotal entries parseadas: {len(df_entries)}")
    if df_entries.empty:
        print("No hay entries — abortando.")
        return

    n_inc = (df_entries["n_paginas"] == 0).sum()
    if n_inc:
        print(f"  ⚠ {n_inc} entries sin página (incompletas)")

    # ── Guardar CSV ───────────────────────────────────────────────────
    df_entries.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"\nCSV guardado: {OUTPUT_CSV}")

    # ── Estadísticas ──────────────────────────────────────────────────
    print(f"\n{'='*72}")
    print("ESTADÍSTICAS")
    print(f"  Entries por tomo:")
    for tomo, cnt in df_entries.groupby("tomo").size().items():
        print(f"    T{tomo}: {cnt}")

    # Entries con múltiples páginas (mismo caso citado varias veces)
    multi = df_entries[df_entries["n_paginas"] > 1]
    print(f"\n  Entries con múltiples páginas: {len(multi)}")

    # ── Crosscheck contra csjn_casos.csv ──────────────────────────────
    print(f"\n{'='*72}")
    print("CROSSCHECK vs csjn_casos.csv")

    df_casos = pd.read_csv(CASOS_CSV, usecols=[
        "caso_id_canonico", "tomo", "case_name_indice",
        "source_file", "linea_inicio",
    ])
    # Solo fallos (no sumarios editoriales sin nombre)
    df_casos = df_casos[df_casos["case_name_indice"].notna()].copy()

    print(f"  Casos en parser: {len(df_casos)}")
    print(f"  Entries en índice: {len(df_entries)}")

    # Páginas del índice por tomo
    idx_pages = set()
    for _, e in df_entries.iterrows():
        if e["paginas"]:
            for p in str(e["paginas"]).split(","):
                idx_pages.add((int(e["tomo"]), int(p.strip())))

    # Páginas de los casos por tomo (linea_inicio → buscar en localizados
    # sería más preciso, pero caso_id_canonico tiene tomo_pPAGINA)
    parser_pages = set()
    for _, c in df_casos.iterrows():
        cid = str(c["caso_id_canonico"])
        # caso_id_canonico format: "329_p537" → tomo 329, page 537
        m = re.match(r"(\d+)_p(\d+)", cid)
        if m:
            parser_pages.add((int(m.group(1)), int(m.group(2))))

    # Cruce
    en_indice_no_parser = idx_pages - parser_pages
    en_parser_no_indice = parser_pages - idx_pages

    print(f"\n  Páginas en índice: {len(idx_pages)}")
    print(f"  Páginas en parser: {len(parser_pages)}")
    print(f"  En índice pero NO en parser (MISS): {len(en_indice_no_parser)}")
    print(f"  En parser pero NO en índice (EXTRA): {len(en_parser_no_indice)}")

    if en_indice_no_parser:
        print(f"\n  MISS (en índice, no en parser) — primeros 20:")
        for tomo, pag in sorted(en_indice_no_parser)[:20]:
            # Buscar entry correspondiente
            match = df_entries[
                (df_entries["tomo"] == tomo) &
                (df_entries["paginas"].str.contains(str(pag), na=False))
            ]
            if not match.empty:
                name = match.iloc[0]["case_name_indice"][:60]
            else:
                name = "?"
            print(f"    T{tomo} p.{pag}: {name}")

    if en_parser_no_indice:
        print(f"\n  EXTRA (en parser, no en índice) — primeros 20:")
        for tomo, pag in sorted(en_parser_no_indice)[:20]:
            match = df_casos[
                df_casos["caso_id_canonico"].str.startswith(f"{tomo}_p{pag}")
            ]
            if not match.empty:
                name = str(match.iloc[0]["case_name_indice"])[:60]
            else:
                name = "?"
            print(f"    T{tomo} p.{pag}: {name}")


if __name__ == "__main__":
    main()
