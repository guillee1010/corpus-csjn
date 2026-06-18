#!/usr/bin/env python3
"""
derivar_recursos.py — capa de recursos/disposición sobre el corpus (corpus-csjn).
=================================================================================
Lee los outputs canónicos del parser y deriva la disposición de fondo y la vía
recursiva, keyed por caso. NO toca parser.py: capa aparte (patrón derivar_materia).
La lógica se importa de módulos fuente-única (mismos que validan en build_m20):
  - clasificador_disposicion.py  -> disposicion, reenvia, parte_ganadora
  - clasificador_via.py          -> via_recurso, multi_recurso

Salida: output/parser/csjn_casos_recursos.csv (1 fila por caso).

v0.3 — M26 rewiring del gate: es_revision_fondo deja de ser la copia perezosa de
       is_merit_decision (parser) y pasa a derivarse de caseDisposition + guards
       (es_revision_fondo() de clasificador_disposicion v1.08). Cierra el gate-gap del
       de-interleave (gate κ 0,933→0,946) y absorbe B129. is_merit corpus 2870→2816.
v0.2 — agrega la VÍA recursiva (via_recurso + multi_recurso) vía clasificador_via
       (fuente única, primacía del ordinario). Lee considerando además del dispositivo
       (la vía a veces vive en los fundamentos). Hereda el norm() v1.01 (\xad-aware),
       que recupera disposición/vía/parte partidas por el soft-hyphen del OCR.
       Métricas en disco vs gold: vía 0,956 · disposición 0,930 · parte 0,862.
v0.1 — núcleo blind-validado: disposicion (0,857) + reenvia (0,773) + parte_ganadora
       (0,794). Campos aún pendientes (v0.3): eje queja/concedido, admisión, tipo de
       cuestión federal (regla de primacía de la arbitrariedad).
"""
import argparse, csv, sys
from pathlib import Path
import pandas as pd
csv.field_size_limit(10**7)

HERE = Path(__file__).resolve().parent       # scripts/pipeline/
ROOT = HERE.parents[1]                        # raiz del repo
sys.path.insert(0, str(HERE))
from clasificador_disposicion import disposicion, parte_ganadora_regla, es_revision_fondo, __version__ as CLF_VER
from clasificador_via import via_recurso, __version__ as VIA_VER

__version__ = "0.3"

CASOS  = ROOT / "output" / "parser" / "csjn_casos.csv"
TEXTOS = ROOT / "output" / "parser" / "csjn_casos_textos.csv"
OUT    = ROOT / "output" / "parser" / "csjn_casos_recursos.csv"

def derivar(casos_path=CASOS, textos_path=TEXTOS, out_path=OUT):
    casos = pd.read_csv(casos_path, dtype=str, keep_default_na=False)
    textos = pd.read_csv(textos_path, dtype=str, keep_default_na=False)[
        ["caso_id_canonico", "por_ello_text", "considerando_text"]]
    df = casos.merge(textos, on="caso_id_canonico", how="left")
    df["por_ello_text"] = df["por_ello_text"].fillna("")
    df["considerando_text"] = df["considerando_text"].fillna("")

    res = df["por_ello_text"].map(disposicion)
    out = pd.DataFrame({
        "caso_id_canonico": df["caso_id_canonico"],
        "disposicion": res.map(lambda r: r[0]),
        "reenvia": res.map(lambda r: "si" if r[1] else "no"),
    })
    out["parte_ganadora"] = out["disposicion"].map(parte_ganadora_regla)

    # vía recursiva (v0.2): dispositivo + considerando, primacía del ordinario
    v = df.apply(lambda r: via_recurso(r["por_ello_text"], r["considerando_text"]), axis=1)
    out["via_recurso"]   = v.map(lambda t: t[0])
    out["multi_recurso"] = v.map(lambda t: "si" if t[1] else "no")

    # es_revision_fondo (M26 rewiring v0.3): GATE derivado de caseDisposition + guards
    # (clasificador_disposicion.es_revision_fondo), ya NO la copia perezosa de is_merit_decision.
    out["es_revision_fondo"] = [es_revision_fondo(d, pe, o == "1")
        for d, pe, o in zip(out["disposicion"], df["por_ello_text"], df["is_originaria"])]
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
    print(f"[derivar_recursos v{__version__} / disp v{CLF_VER} / via v{VIA_VER}]  {len(out)} filas -> {dest.name}")
    DISPVALS = {"revoca","deja_sin_efecto","confirma","nulidad","modifica"}
    es_disp = out.disposicion.isin(DISPVALS)
    print(f"  disposición de fondo leída: {es_disp.sum()}  ({100*es_disp.mean():.1f}%)")
    print("  dist disposicion:"); print(out.disposicion.value_counts().to_string())
    print("  dist via_recurso:");  print(out.via_recurso.value_counts().to_string())
    print(f"  multi_recurso=si: {(out.multi_recurso=='si').sum()}")

if __name__ == "__main__":
    main()
