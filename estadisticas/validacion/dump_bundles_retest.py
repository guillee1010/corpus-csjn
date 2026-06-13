# -*- coding: utf-8 -*-
r"""
dump_bundles_retest.py — Arma los bundles ciegos de los 60 casos del retest.
corpus-csjn — Guillermo Rubinetti.

Para cada caso de retest_blank.csv, corta el texto del fallo del corpus usando
SOLO las columnas de localizacion de csjn_casos.csv (source_file, linea_inicio,
linea_fin_real). NO lee ninguna columna de clasificacion (outcome, es_queja,
etc.), asi que no rompe la ceguera: produce el mismo texto que vio el parser,
sin su veredicto.

Escribe un .md por caso en OUT_DIR, con header "# <caso_id>", que es lo que
indexa codificar_retest.py.

Corré esto UNA vez, desde la RAIZ del repo:
    python estadisticas\validacion\dump_bundles_retest.py
"""

from pathlib import Path
import sys
import pandas as pd

# ===================== CONFIG (rutas relativas a la raiz del repo) =====================
RETEST  = Path("estadisticas/validacion/retest_blank.csv")
CASOS   = Path("output/parser/csjn_casos.csv")
CORPUS  = Path("corpus")
OUT_DIR = Path("estadisticas/validacion/bundles")
COL_ID  = "caso_id_canonico"
# ======================================================================================


def main():
    for p in (RETEST, CASOS, CORPUS):
        if not p.exists():
            sys.exit(f"No encuentro {p}. Corré desde la raíz del repo o ajustá CONFIG.")

    ids = pd.read_csv(RETEST, dtype=str)[COL_ID].tolist()

    # Solo columnas de localizacion. usecols deja afuera, a proposito, los campos cod_/parser.
    loc = pd.read_csv(
        CASOS, dtype=str,
        usecols=[COL_ID, "source_file", "linea_inicio", "linea_fin", "linea_fin_real"],
    ).set_index(COL_ID)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = {}  # source_file -> list[str] (lineas), para leer cada .md una sola vez
    hechos, faltan = 0, []

    for cid in ids:
        if cid not in loc.index:
            faltan.append((cid, "no está en csjn_casos.csv"))
            continue
        r = loc.loc[cid]
        src = (r["source_file"] or "").strip()
        f = CORPUS / src
        if not src or not f.exists():
            faltan.append((cid, f"source_file '{src}' no existe en corpus/"))
            continue

        if src not in cache:
            cache[src] = f.read_text(encoding="utf-8", errors="replace").splitlines()
        lineas = cache[src]

        ini = int(float(r["linea_inicio"]))
        fin_raw = r["linea_fin_real"] if str(r["linea_fin_real"]).strip() else r["linea_fin"]
        fin = int(float(fin_raw))
        # linea_inicio es 0-indexed; corte inclusivo del fin.
        bloque = "\n".join(lineas[ini:fin + 1]).strip()

        (OUT_DIR / f"{cid}.md").write_text(
            f"# {cid}\n\n{bloque}\n", encoding="utf-8"
        )
        hechos += 1

    print(f"escritos {hechos}/{len(ids)} bundles en {OUT_DIR}")
    if faltan:
        print(f"faltan {len(faltan)}:")
        for cid, motivo in faltan:
            print(f"  {cid}: {motivo}")
    # chequeo rapido: preview del primero
    primeros = sorted(OUT_DIR.glob("*.md"))
    if primeros:
        txt = primeros[0].read_text(encoding="utf-8").splitlines()
        print(f"\npreview {primeros[0].name} ({len(txt)} lineas):")
        for l in txt[:4]:
            print("  | " + l)
        print("  ...")
        for l in txt[-3:]:
            print("  | " + l)


if __name__ == "__main__":
    main()
