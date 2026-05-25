"""
extraer_280_ac4.py — H065: extrae bloques fuente del corpus para casos
inadmisible_280 e inadmisible_acordada_4.

Genera:
  output/diag/corpus_inadmisible_280.md
  output/diag/corpus_inadmisible_acordada_4.md

Cada caso incluye: caso_id, tomo, carátula, wc_considerando,
voting_pattern, y el bloque fuente completo del .md.

Uso:
  cd corpus-csjn
  python scripts/auditoria/H065/extraer_280_ac4.py
"""

import pandas as pd
from pathlib import Path

REPO       = Path.cwd()
CASOS_CSV  = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUT_DIR    = REPO / "output" / "diag"


def cargar_fuente(source_file: str) -> list[str] | None:
    path = CORPUS_DIR / source_file
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").splitlines()


def extraer_bloque(lines: list[str], li: int, lf: int) -> str:
    bloque = lines[int(li):int(lf) + 1]
    return "\n".join(bloque)


def generar_md(df: pd.DataFrame, outcome: str, out_path: Path):
    casos = df[df["outcome"] == outcome].sort_values(["tomo", "caso_id_canonico"])
    
    partes = []
    partes.append(f"# Corpus — {outcome} ({len(casos)} casos)\n")
    partes.append(f"Extraído de los .md fuente. Para revisar en el explorador,")
    partes.append(f"buscar por tomo + página.\n")

    archivos_cache = {}
    n_ok = 0
    n_fail = 0

    for _, r in casos.iterrows():
        cid = r["caso_id_canonico"]
        sf = r.get("source_file", "")
        li = r.get("linea_inicio")
        lf = r.get("linea_fin_real")
        caratula = r.get("case_name_indice", "")
        wc = r.get("wc_considerando", "")
        vp = r.get("voting_pattern", "")
        tomo = r.get("tomo", "")

        partes.append(f"---\n")
        partes.append(f"## {cid}\n")
        partes.append(f"- **Tomo:** {tomo} | **wc_cons:** {wc} | **pattern:** {vp}")
        partes.append(f"- **Carátula:** {caratula}\n")

        if pd.isna(li) or pd.isna(lf) or not sf:
            partes.append(f"*Sin datos de localización.*\n")
            n_fail += 1
            continue

        if sf not in archivos_cache:
            archivos_cache[sf] = cargar_fuente(sf)

        lines = archivos_cache[sf]
        if lines is None:
            partes.append(f"*Archivo no encontrado: {sf}*\n")
            n_fail += 1
            continue

        bloque = extraer_bloque(lines, li, lf)
        partes.append(f"```")
        partes.append(bloque)
        partes.append(f"```\n")
        n_ok += 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(partes), encoding="utf-8")
    print(f"  {out_path.name}: {n_ok} bloques extraídos, {n_fail} sin datos")


def main():
    df = pd.read_csv(CASOS_CSV, low_memory=False, dtype=str)
    for col in ["tomo", "linea_inicio", "linea_fin_real", "wc_considerando"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"Casos: {len(df)}")
    print(f"  inadmisible_280: {(df['outcome'] == 'inadmisible_280').sum()}")
    print(f"  inadmisible_acordada_4: {(df['outcome'] == 'inadmisible_acordada_4').sum()}")
    print()

    generar_md(df, "inadmisible_280", OUT_DIR / "corpus_inadmisible_280.md")
    generar_md(df, "inadmisible_acordada_4", OUT_DIR / "corpus_inadmisible_acordada_4.md")

    print("\nListo.")


if __name__ == "__main__":
    main()
