#!/usr/bin/env python3
"""
derivar_recursos.py — capa de recursos/disposición sobre el corpus (corpus-csjn).
=================================================================================
Lee los outputs canónicos del parser y deriva la disposición de fondo, keyed por
caso. NO toca parser.py: capa aparte (patrón derivar_materia). El clasificador se
importa de clasificador_disposicion.py (fuente única; mismo que valida build_m20).

v0.1 — núcleo blind-validado: disposicion (0,857) + reenvia (0,773) + parte_ganadora
       (0,794). Campos pendientes (v0.2, requieren semilla gold propia): via_recurso
       ordinario/extraordinario, eje queja/concedido (cruce con es_queja), admisión,
       tipo de cuestión.

Salida: output/parser/csjn_casos_recursos.csv (1 fila por caso).
"""
import argparse, csv, sys
from pathlib import Path
import pandas as pd
csv.field_size_limit(10**7)

HERE = Path(__file__).resolve().parent       # scripts/pipeline/
ROOT = HERE.parents[1]                        # raiz del repo
sys.path.insert(0, str(HERE))
from clasificador_disposicion import disposicion, parte_ganadora_regla, __version__ as CLF_VER

__version__ = "0.1"

CASOS  = ROOT / "output" / "parser" / "csjn_casos.csv"
TEXTOS = ROOT / "output" / "parser" / "csjn_casos_textos.csv"
OUT    = ROOT / "output" / "parser" / "csjn_casos_recursos.csv"

def derivar(casos_path=CASOS, textos_path=TEXTOS, out_path=OUT):
    casos = pd.read_csv(casos_path, dtype=str, keep_default_na=False)
    textos = pd.read_csv(textos_path, dtype=str, keep_default_na=False)[["caso_id_canonico", "por_ello_text"]]
    df = casos.merge(textos, on="caso_id_canonico", how="left")
    df["por_ello_text"] = df["por_ello_text"].fillna("")

    res = df["por_ello_text"].map(disposicion)
    out = pd.DataFrame({
        "caso_id_canonico": df["caso_id_canonico"],
        "disposicion": res.map(lambda r: r[0]),
        "reenvia": res.map(lambda r: "si" if r[1] else "no"),
    })
    out["parte_ganadora"] = out["disposicion"].map(parte_ganadora_regla)
    # contexto para análisis (no es derivación nueva, viene del parser)
    out["es_revision_fondo"] = df["is_merit_decision"].map(lambda x: "si" if x == "1" else "no")
    out["es_queja"] = df.get("es_queja", "")
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos"); ap.add_argument("--textos"); ap.add_argument("--out")
    a = ap.parse_args()
    out = derivar(Path(a.casos) if a.casos else CASOS,
                  Path(a.textos) if a.textos else TEXTOS,
                  Path(a.out) if a.out else OUT)
    dest = Path(a.out) if a.out else OUT
    out.to_csv(dest, index=False, lineterminator="\n")
    print(f"[derivar_recursos v{__version__} / clf v{CLF_VER}]  {len(out)} filas -> {dest.name}")
    DISPVALS = {"revoca","deja_sin_efecto","confirma","nulidad","modifica"}
    es_disp = out.disposicion.isin(DISPVALS)
    print(f"  disposición de fondo leída: {es_disp.sum()}  ({100*es_disp.mean():.1f}%)")
    print("  dist disposicion:"); print(out.disposicion.value_counts().to_string())

if __name__ == "__main__":
    main()
