#!/usr/bin/env python3
"""
build_m20.py — generador de la clave del parser para validación M20 (corpus-csjn).
Regenera M20_clave_parser_n300.csv (answer key del parser, comparada ciega vs gold).

El clasificador de disposición se IMPORTA de scripts/pipeline/clasificador_disposicion.py
(fuente única; mismo módulo que usa derivar_recursos.py en producción). Garantía:
--verify <clave_ref> asserta reproducción 300/300 (disposicion/reenvia/parte_ganadora).

Ubicación: scripts/diagnostico/H120/build_m20.py
Uso:  python build_m20.py [--verify clave_ref.csv]
"""
import argparse, csv, sys
from pathlib import Path
import pandas as pd
csv.field_size_limit(10**7)

HERE = Path(__file__).resolve().parent          # scripts/diagnostico/H120/
ROOT = HERE.parents[2]                            # raiz del repo
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))
from clasificador_disposicion import disposicion, parte_ganadora_regla, __version__ as CLF_VER

CASOS  = ROOT / "output" / "parser" / "csjn_casos.csv"
TEXTOS = ROOT / "output" / "parser" / "csjn_casos_textos.csv"
FRAME  = HERE / "planilla_M20_codificar-56xlsx.xlsx"   # frame n300 (ids + orden M19)
OUT    = HERE / "M20_clave_parser_n300.csv"

def construir_clave(casos_p=CASOS, textos_p=TEXTOS, frame_p=FRAME):
    casos = pd.read_csv(casos_p, dtype=str, keep_default_na=False)
    textos = pd.read_csv(textos_p, dtype=str, keep_default_na=False)[["caso_id_canonico", "por_ello_text"]]
    frame = pd.read_excel(frame_p, dtype=str).fillna("")
    ids = [i for i in frame["caso_id_canonico"].tolist() if i.strip()]
    base = casos.set_index("caso_id_canonico").loc[ids].reset_index().merge(textos, on="caso_id_canonico", how="left")
    base["por_ello_text"] = base["por_ello_text"].fillna("")
    res = base["por_ello_text"].map(disposicion)
    clave = pd.DataFrame({
        "caso_id_canonico": base["caso_id_canonico"],
        "parser_es_revision_fondo": base["is_merit_decision"].map(lambda x: "si" if x == "1" else "no"),
        "parser_disposicion": res.map(lambda r: r[0]),
        "parser_reenvia": res.map(lambda r: "si" if r[1] else "no"),
    })
    clave["parser_parte_ganadora"] = clave["parser_disposicion"].map(parte_ganadora_regla)
    clave["_ctx_outcome_m19"] = base["outcome"]
    clave["_ctx_is_merit"] = base["is_merit_decision"]
    return clave

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", metavar="CLAVE_REF")
    ap.add_argument("--casos"); ap.add_argument("--textos"); ap.add_argument("--frame"); ap.add_argument("--out")
    a = ap.parse_args()
    clave = construir_clave(Path(a.casos) if a.casos else CASOS,
                            Path(a.textos) if a.textos else TEXTOS,
                            Path(a.frame) if a.frame else FRAME)
    dest = Path(a.out) if a.out else OUT
    clave.to_csv(dest, index=False, lineterminator="\n")
    print(f"[build_m20 / clf v{CLF_VER}]  {len(clave)} filas -> {dest.name}")
    if a.verify:
        ref = pd.read_csv(a.verify, dtype=str, keep_default_na=False)
        m = ref.merge(clave, on="caso_id_canonico", suffixes=("_ref", "_new"))
        bad = sum((m[f"{c}_ref"] != m[f"{c}_new"]).sum() for c in ("parser_disposicion","parser_reenvia","parser_parte_ganadora"))
        for c in ("parser_disposicion","parser_reenvia","parser_parte_ganadora"):
            d=(m[f"{c}_ref"]!=m[f"{c}_new"]).sum(); print(f"  [verify] {c}: {len(m)-d}/{len(m)}")
        print("[CLEAN] reproduce la clave de referencia exacto" if not bad else "[FAIL] NO sellar"); sys.exit(0 if not bad else 1)

if __name__ == "__main__":
    main()
