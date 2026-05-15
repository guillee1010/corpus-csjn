"""
CSJN — Clasificador de tipo_caso
==================================
Post-procesa el CSV de casos producido por csjnv10.py para asignar
una variable categórica `tipo_caso` que distingue:

  - admisibilidad_280:        outcome 'inadmisible_280'
  - admisibilidad_formal:     outcome 'inadmisible_acordada_4' o 'mal_concedido'
                              (rechazos por formalismos del recurso)
  - admisibilidad_otros:      'desestima' sin merit + 'desistimiento' + 'abstracto'
  - originaria:               competencia originaria de la Corte (excluida del
                              corpus modelable por estructura procesal distinta)
  - nucleo:                   merit decisions (hace_lugar, procedente, revoca,
                              nulidad, confirma) + competencia + otros sustantivos

NOTA: este es un primer paso. Las versiones futuras deberán agregar:
  - detección de remisiones (citas a fallos previos como única fundamentación)
  - detección de ANSES masivo (tribunal previsional + Badaro/Elliff/Blanco)

Uso:
  python clasificador_tipo_caso.py \
    --casos csjn_casos_v10.csv \
    --output csjn_casos_v10_clasificado.csv

Salida:
  CSV idéntico al input + 2 columnas: tipo_caso, tipo_caso_grupo

Donde:
  tipo_caso_grupo ∈ {admisibilidad, originaria, nucleo}  ← variable resumen
  tipo_caso       ∈ {admisibilidad_280, admisibilidad_formal,
                     admisibilidad_otros, originaria, nucleo}  ← variable detalle
"""

import argparse
from pathlib import Path
import pandas as pd

# ── Mapping ───────────────────────────────────────────────────────────────────

OUTCOMES_ADMIS_280     = {"inadmisible_280"}
OUTCOMES_ADMIS_FORMAL  = {"inadmisible_acordada_4", "mal_concedido"}
OUTCOMES_ADMIS_OTROS   = {"desestima", "desistimiento", "abstracto",
                          "sin_dispositivo"}
OUTCOMES_NUCLEO        = {"hace_lugar", "procedente", "revoca", "nulidad",
                          "confirma", "competencia", "otro"}

def asignar_tipo_caso(row):
    """Asigna tipo_caso usando outcome + is_originaria como criterios."""
    if row.get("is_originaria", 0) == 1:
        return "originaria"
    outcome = row.get("outcome", "")
    if outcome in OUTCOMES_ADMIS_280:
        return "admisibilidad_280"
    if outcome in OUTCOMES_ADMIS_FORMAL:
        return "admisibilidad_formal"
    if outcome in OUTCOMES_ADMIS_OTROS:
        return "admisibilidad_otros"
    if outcome in OUTCOMES_NUCLEO:
        return "nucleo"
    return "otro"

GRUPO_MAP = {
    "admisibilidad_280":      "admisibilidad",
    "admisibilidad_formal":   "admisibilidad",
    "admisibilidad_otros":    "admisibilidad",
    "originaria":             "originaria",
    "nucleo":                 "nucleo",
    "otro":                   "nucleo",  # conservador: agrupar "otro" con nucleo
}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Clasificador de tipo_caso CSJN")
    ap.add_argument("--casos", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    df = pd.read_csv(args.casos, low_memory=False)
    print(f"Cargados: {len(df)} casos desde {args.casos}")

    df["tipo_caso"]       = df.apply(asignar_tipo_caso, axis=1)
    df["tipo_caso_grupo"] = df["tipo_caso"].map(GRUPO_MAP)

    # Guardar
    df.to_csv(args.output, index=False, encoding="utf-8")
    print(f"\n[OK] Guardado: {args.output}")

    # Resumen
    print("\n── tipo_caso (detalle) ──")
    print(df["tipo_caso"].value_counts().to_string())

    print("\n── tipo_caso_grupo (resumen) ──")
    print(df["tipo_caso_grupo"].value_counts().to_string())

    print("\n── Cruce tipo_caso × voting_pattern ──")
    print(pd.crosstab(df["tipo_caso"], df["voting_pattern"], margins=True).to_string())

    # Si existe el flag is_originaria, mostrar consistencia
    if "is_originaria" in df.columns:
        n_orig_flag = (df["is_originaria"] == 1).sum()
        n_orig_clas = (df["tipo_caso"] == "originaria").sum()
        print(f"\nConsistencia originaria: flag={n_orig_flag}, clasificación={n_orig_clas}")


if __name__ == "__main__":
    main()
