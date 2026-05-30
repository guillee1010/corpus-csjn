r"""
extraer_por_outcome.py  (H090, diagnóstico)

Extrae casos del CSV canónico para ojeo manual. NO reimplementa heurísticas:
lee output/parser/csjn_casos.csv (fuente única) y filtra.

Filtros (combinables; al menos uno requerido):
    --outcome LBL[,LBL...]        outcome en lista (match exacto)
    --exclude-outcome LBL[,LBL]   outcome fuera de lista
    --considerando-regex REGEX    considerando_text matchea REGEX (re.I)

Ejemplos (desde la raiz del repo):
    # los 280 limpios
    python scripts/diagnostico/H090/extraer_por_outcome.py --outcome inadmisible_280 --out-dir scripts/diagnostico/H090
    # la frontera: 280 mencionado en considerando pero NO clasificado 280/ac4
    python scripts/diagnostico/H090/extraer_por_outcome.py ^
        --considerando-regex "art\.?\s*280|art[ii]culo\s*280" ^
        --exclude-outcome inadmisible_280,inadmisible_acordada_4 ^
        --name frontera_280 --out-dir scripts/diagnostico/H090

Salida: <out-dir>/casos_<name>.csv  (UTF-8)
"""
import argparse
import csv
import re
import sys
from pathlib import Path
from collections import Counter

# (el docstring del módulo contiene un regex con \. — ver __doc__ via -h)
COLS_SALIDA = [
    "caso_id_canonico", "tomo", "case_name_cuerpo", "outcome",
    "voting_pattern", "n_jueces", "n_disidencias", "n_votos_svoto",
    "tribunal_origen", "tribunal_origen_status",
    "por_ello_text", "considerando_text",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outcome", default=None,
                    help="Lista (coma) de outcomes a incluir (match exacto).")
    ap.add_argument("--exclude-outcome", default=None,
                    help="Lista (coma) de outcomes a excluir.")
    ap.add_argument("--considerando-regex", default=None,
                    help="Regex (re.I) que debe matchear considerando_text.")
    ap.add_argument("--name", default=None,
                    help="Nombre del archivo de salida (casos_<name>.csv).")
    ap.add_argument("--csv", default="output/parser/csjn_casos.csv")
    ap.add_argument("--out-dir", default="output/diagnostico/H090")
    args = ap.parse_args()

    if not (args.outcome or args.exclude_outcome or args.considerando_regex):
        sys.exit("[ERROR] Especifica al menos un filtro "
                 "(--outcome / --exclude-outcome / --considerando-regex).")

    incl = set(args.outcome.split(",")) if args.outcome else None
    excl = set(args.exclude_outcome.split(",")) if args.exclude_outcome else set()
    cons_re = re.compile(args.considerando_regex, re.I) if args.considerando_regex else None

    name = args.name or (args.outcome if args.outcome and "," not in args.outcome else None)
    if not name:
        sys.exit("[ERROR] Con filtro compuesto, pasa --name para el archivo de salida.")

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"[ERROR] No existe el CSV de entrada: {csv_path}")
    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    faltan = [c for c in COLS_SALIDA if c not in rows[0]]
    if faltan:
        sys.exit(f"[ERROR] Faltan columnas en el CSV: {faltan}")

    sel = []
    for r in rows:
        if incl is not None and r["outcome"] not in incl:
            continue
        if r["outcome"] in excl:
            continue
        if cons_re is not None and not cons_re.search(r["considerando_text"]):
            continue
        sel.append(r)

    if not sel:
        sys.exit("[AVISO] 0 casos con esos filtros.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"casos_{name}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS_SALIDA, extrasaction="ignore")
        w.writeheader()
        w.writerows(sel)

    con_disid = sum(1 for r in sel if r["n_disidencias"].strip() not in ("", "0"))
    print(f"filtros -> {len(sel)} casos")
    print(f"  con disidencias (n_disidencias>0): {con_disid}")
    print(f"  desglose por outcome:")
    for k, v in Counter(r["outcome"] for r in sel).most_common():
        print(f"    {v:4d}  {k}")
    print(f"  -> escrito: {out_path}")


if __name__ == "__main__":
    main()
