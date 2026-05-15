"""
CSJN — Detector de Templates Doctrinales
=========================================
Post-procesa el CSV de votos producido por csjnv10.py para detectar
los dos templates anti-doctrinales identificados:

  1. LORENZETTI + VIDAL: voto técnico (según su voto) en mayorías 280
     que agrega un párrafo doctrinal citando "Vidal" (Fallos 344:3156 o
     339:1077) sobre el efecto no-doctrinal del 280.
     Función textual: ADICIONAR metacomentario doctrinal.

  2. ROSENKRANTZ + NO-LEVINAS: voto técnico (según su voto) en mayorías
     que rechazan citando Levinas (Fallos 347:2286). Rosenkrantz se
     remite a los considerandos previos y agrega que "torna inoficioso
     expedirse" sobre los restantes requisitos. Función textual:
     SUSTRAER fuerza al considerando que cita Levinas.

Uso:
  python detector_templates.py \
    --casos csjn_casos_v10.csv \
    --votos csjn_casos_v10_votos.csv \
    --output-dir resultados_templates/

Salidas:
  templates_resultado.csv     — un registro por caso con flags template
  templates_serie_temporal.csv — serie temporal por mes/tomo
  fig_templates_serie.png     — gráfico de la serie temporal
  templates_resumen.xlsx      — resumen consolidado
"""

import argparse
import re
import json
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

# ── Patrones de detección ─────────────────────────────────────────────────────

# Patrones de detección — versión robusta a OCR distorsionado

# Helper para "limpiar" texto OCR: junta guiones de fin de línea
def limpiar_ocr(s):
    """Junta palabras partidas por guion al final de línea: 'inoficio- so' → 'inoficioso'"""
    if not isinstance(s, str): return ""
    # Patrón típico: '<letra>- <letra>' o '<letra>­ <letra>' (soft hyphen)
    s = re.sub(r"([a-záéíóúñ])[\-­]\s+([a-záéíóúñ])", r"\1\2", s)
    # Normalizar espacios múltiples
    s = re.sub(r"\s+", " ", s)
    return s

# Template Lorenzetti + Vidal:
RE_VIDAL_FRASE = re.compile(
    r"cabe\s+poner\s+de\s+relieve.{0,200}?"
    r"(alcance\s+de\s+los\s+fallos|interpretaciones\s+err[óo]neas)"
    r".{0,300}?(desestimaci[óo]n.{0,80}?(recurso\s+extraordinario|aplicaci[óo]n\s+de\s+dicha\s+norma))"
    r".{0,200}?no\s+importa\s+confirmar",
    re.I | re.DOTALL
)
RE_VIDAL_CITA = re.compile(
    r"Vidal.{0,80}?Fallos:?\s*(344:3156|339:1077)",
    re.I | re.DOTALL
)

# Template Rosenkrantz + no-Levinas:
RE_INOFICIOSO = re.compile(
    r"torna\s+inoficios[oa]\s+expedirse\s+acerca\s+de\s+los\s+"
    r"(requisitos\s+propios|restantes\s+requisitos)",
    re.I
)
RE_LEVINAS = re.compile(
    r"(Ferrari.{0,40}?Levinas|Levinas.{0,40}?Ferrari|Fallos:?\s*347:2286)",
    re.I | re.DOTALL
)

# ── Carga de datos ────────────────────────────────────────────────────────────

def cargar(casos_path, votos_path):
    casos = pd.read_csv(casos_path, low_memory=False)
    votos = pd.read_csv(votos_path, low_memory=False)
    # Asegurar que texto_voto y considerando_text estén como string
    if "texto_voto" in votos.columns:
        votos["texto_voto"] = votos["texto_voto"].fillna("").astype(str)
    if "considerando_text" in casos.columns:
        casos["considerando_text"] = casos["considerando_text"].fillna("").astype(str)
    return casos, votos

# ── Detector ──────────────────────────────────────────────────────────────────

def detectar_templates(casos, votos):
    """
    Para cada caso, evalúa la presencia de los dos templates.
    """
    rows = []

    # Pre-computar: para cada caso, ¿el caso menciona Levinas?
    # Buscar en: considerando_text, por_ello_text, case_name (sumario suele estar pegado).
    # También en el texto del voto de mayoría, que viene como contexto adicional.
    def _cita_lev(c):
        fuentes = []
        for col in ("considerando_text", "por_ello_text", "case_name"):
            if col in c.index and pd.notna(c[col]):
                fuentes.append(limpiar_ocr(str(c[col])))
        texto = " ".join(fuentes)
        return bool(RE_LEVINAS.search(texto))

    casos["_cita_levinas"] = casos.apply(_cita_lev, axis=1)

    # También vamos a verificar la cita Levinas dentro del texto del voto de Rosenkrantz
    # (a veces queda allí porque el sumario está embebido en el voto OCR)
    votos_idx = votos.set_index(["caso_id", "juez"])

    for _, c in casos.iterrows():
        cid = c["caso_id"]

        # Template 1: Lorenzetti + Vidal
        t_lor_vidal = False
        ev_lor_vidal = ""
        try:
            voto_lor = votos_idx.loc[(cid, "Lorenzetti")]
            if isinstance(voto_lor, pd.DataFrame):
                voto_lor = voto_lor.iloc[0]
            posicion_lor = voto_lor["posicion"]
            texto_lor    = limpiar_ocr(voto_lor.get("texto_voto", ""))
            if posicion_lor in ("según su voto", "por su voto") and texto_lor:
                tiene_frase = bool(RE_VIDAL_FRASE.search(texto_lor))
                tiene_cita  = bool(RE_VIDAL_CITA.search(texto_lor))
                if tiene_frase and tiene_cita:
                    t_lor_vidal = True
                    ev_lor_vidal = "frase+cita"
                elif tiene_frase:
                    t_lor_vidal = True
                    ev_lor_vidal = "solo_frase"
                elif tiene_cita:
                    t_lor_vidal = True
                    ev_lor_vidal = "solo_cita"
        except KeyError:
            pass

        # Template 2: Rosenkrantz + no-Levinas
        t_ros_nolev = False
        ev_ros_nolev = ""
        try:
            voto_ros = votos_idx.loc[(cid, "Rosenkrantz")]
            if isinstance(voto_ros, pd.DataFrame):
                voto_ros = voto_ros.iloc[0]
            posicion_ros = voto_ros["posicion"]
            texto_ros    = limpiar_ocr(voto_ros.get("texto_voto", ""))
            if posicion_ros in ("según su voto", "por su voto") and texto_ros:
                tiene_inoficioso = bool(RE_INOFICIOSO.search(texto_ros))
                cita_levinas_caso = bool(c["_cita_levinas"])
                # El voto de Rosenkrantz puede contener Levinas si el sumario
                # está embebido en su texto (caso del MPM)
                cita_lev_en_voto = bool(RE_LEVINAS.search(texto_ros))
                hay_levinas = cita_levinas_caso or cita_lev_en_voto
                if tiene_inoficioso and hay_levinas:
                    t_ros_nolev = True
                    ev_ros_nolev = "inoficioso+levinas"
                elif tiene_inoficioso:
                    t_ros_nolev = True
                    ev_ros_nolev = "solo_inoficioso"
        except KeyError:
            pass

        rows.append({
            "caso_id":                      cid,
            "tomo":                         c["tomo"],
            "date":                         c["date"],
            "outcome":                      c["outcome"],
            "voting_pattern":               c["voting_pattern"],
            "cita_levinas_en_caso":         bool(c["_cita_levinas"]),
            "template_lorenzetti_vidal":    t_lor_vidal,
            "ev_lor_vidal":                 ev_lor_vidal,
            "template_rosenkrantz_no_lev":  t_ros_nolev,
            "ev_ros_nolev":                 ev_ros_nolev,
        })

    return pd.DataFrame(rows)

# ── Análisis temporal ─────────────────────────────────────────────────────────

MESES_ES = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
            "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,
            "diciembre":12}

def parse_fecha(s):
    if not isinstance(s, str): return pd.NaT
    m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", s.lower().strip())
    if not m: return pd.NaT
    d, mes, y = m.group(1), m.group(2), m.group(3)
    if mes not in MESES_ES: return pd.NaT
    try:
        return pd.Timestamp(int(y), MESES_ES[mes], int(d))
    except ValueError:
        return pd.NaT

def serie_temporal(df_templates):
    df = df_templates.copy()
    df["date_dt"] = df["date"].apply(parse_fecha)
    df["año_mes"] = df["date_dt"].dt.to_period("M").astype(str)
    df["año"]     = df["date_dt"].dt.year

    serie_mes = df.groupby("año_mes").agg(
        n_casos=("caso_id", "count"),
        n_lor_vidal=("template_lorenzetti_vidal", "sum"),
        n_ros_nolev=("template_rosenkrantz_no_lev", "sum"),
    ).reset_index()
    serie_mes["tasa_lor_vidal"] = serie_mes["n_lor_vidal"] / serie_mes["n_casos"]
    serie_mes["tasa_ros_nolev"] = serie_mes["n_ros_nolev"] / serie_mes["n_casos"]

    serie_anual = df.groupby("año").agg(
        n_casos=("caso_id", "count"),
        n_lor_vidal=("template_lorenzetti_vidal", "sum"),
        n_ros_nolev=("template_rosenkrantz_no_lev", "sum"),
    ).reset_index()
    serie_anual["tasa_lor_vidal"] = serie_anual["n_lor_vidal"] / serie_anual["n_casos"]
    serie_anual["tasa_ros_nolev"] = serie_anual["n_ros_nolev"] / serie_anual["n_casos"]

    return serie_mes, serie_anual

def grafico_serie(serie_mes, output_path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 5))
    x = pd.to_datetime(serie_mes["año_mes"] + "-01")
    ax.plot(x, serie_mes["n_lor_vidal"], marker="o",
            label="Template Lorenzetti+Vidal", color="#2E5C8A", linewidth=2)
    ax.plot(x, serie_mes["n_ros_nolev"], marker="s",
            label="Template Rosenkrantz+no-Levinas", color="#C0392B", linewidth=2)
    ax.set_xlabel("Mes")
    ax.set_ylabel("Casos con template (frecuencia absoluta)")
    ax.set_title("Aparición temporal de los templates anti-doctrinales",
                 fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

# ── Resúmenes ─────────────────────────────────────────────────────────────────

def resumen_general(df_templates, casos):
    rows = []

    rows.append({
        "métrica": "N total de casos",
        "valor": len(df_templates),
    })
    rows.append({
        "métrica": "Casos con outcome inadmisible_280",
        "valor": int((casos["outcome"] == "inadmisible_280").sum()),
    })
    rows.append({
        "métrica": "Casos con outcome mal_concedido",
        "valor": int((casos["outcome"] == "mal_concedido").sum()),
    })
    rows.append({
        "métrica": "Casos con outcome inadmisible_acordada_4",
        "valor": int((casos["outcome"] == "inadmisible_acordada_4").sum()),
    })
    rows.append({
        "métrica": "Casos donde se cita Levinas (Ferrari)",
        "valor": int(df_templates["cita_levinas_en_caso"].sum()),
    })
    rows.append({
        "métrica": "Casos con template Lorenzetti+Vidal",
        "valor": int(df_templates["template_lorenzetti_vidal"].sum()),
    })
    rows.append({
        "métrica": "Casos con template Rosenkrantz+no-Levinas",
        "valor": int(df_templates["template_rosenkrantz_no_lev"].sum()),
    })

    # Tasa template / total concurrencias por juez
    n_concurr_lor = int((casos["voting_pattern"] == "segun_su_voto").sum())  # estimado grueso
    if n_concurr_lor > 0:
        tasa_lor = df_templates["template_lorenzetti_vidal"].sum() / n_concurr_lor
        rows.append({
            "métrica": "Tasa template Lor+Vidal sobre concurrencias del corpus",
            "valor": round(tasa_lor, 3),
        })

    return pd.DataFrame(rows)

def detalle_por_outcome(df_templates):
    """Cruce template × outcome para ver dónde aparecen."""
    return pd.crosstab(
        df_templates["outcome"],
        df_templates["template_lorenzetti_vidal"],
        margins=True,
    ).rename(columns={False: "sin_template_lor_vidal", True: "con_template_lor_vidal"})

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Detector de templates CSJN")
    ap.add_argument("--casos", required=True,
                    help="CSV de casos (output de csjnv10.py)")
    ap.add_argument("--votos", required=True,
                    help="CSV de votos (output de csjnv10.py)")
    ap.add_argument("--output-dir", default="resultados_templates")
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    print("Detector de templates CSJN")
    print("=" * 60)
    print(f"Casos: {args.casos}")
    print(f"Votos: {args.votos}")

    casos, votos = cargar(args.casos, args.votos)
    print(f"\n  Casos cargados: {len(casos)}")
    print(f"  Votos cargados: {len(votos)}")

    if "texto_voto" not in votos.columns:
        print("\n  [ERROR] El CSV de votos no contiene la columna 'texto_voto'.")
        print("          Re-correr el parser con csjnv10.py para obtener esa columna.")
        return

    # Detección
    df_t = detectar_templates(casos, votos)
    print(f"\n  Templates detectados:")
    print(f"    Lorenzetti+Vidal:        {int(df_t['template_lorenzetti_vidal'].sum())}")
    print(f"    Rosenkrantz+no-Levinas:  {int(df_t['template_rosenkrantz_no_lev'].sum())}")
    print(f"    Casos que citan Levinas: {int(df_t['cita_levinas_en_caso'].sum())}")

    # Output principal
    df_t.to_csv(output_dir / "templates_resultado.csv",
                index=False, encoding="utf-8")

    # Series temporales
    serie_mes, serie_anual = serie_temporal(df_t)
    serie_mes.to_csv(output_dir / "templates_serie_mensual.csv",
                     index=False, encoding="utf-8")
    serie_anual.to_csv(output_dir / "templates_serie_anual.csv",
                       index=False, encoding="utf-8")

    # Gráfico
    if not serie_mes.empty:
        try:
            grafico_serie(serie_mes, output_dir / "fig_templates_serie.png")
            print(f"\n  Gráfico: {output_dir / 'fig_templates_serie.png'}")
        except Exception as e:
            print(f"  [WARN] No pude generar gráfico: {e}")

    # Resumen
    resumen = resumen_general(df_t, casos)
    resumen.to_csv(output_dir / "templates_resumen.csv",
                   index=False, encoding="utf-8")
    print(f"\n── Resumen ──")
    print(resumen.to_string(index=False))

    # Cruce con outcome
    detalle = detalle_por_outcome(df_t)
    print(f"\n── Distribución template Lorenzetti+Vidal × outcome ──")
    print(detalle.to_string())

    # Excel consolidado
    try:
        with pd.ExcelWriter(output_dir / "templates_consolidado.xlsx",
                            engine="openpyxl") as w:
            df_t.to_excel(w, sheet_name="resultados", index=False)
            serie_mes.to_excel(w, sheet_name="serie_mensual", index=False)
            serie_anual.to_excel(w, sheet_name="serie_anual", index=False)
            resumen.to_excel(w, sheet_name="resumen", index=False)
            detalle.reset_index().to_excel(w, sheet_name="cruce_outcome", index=False)
        print(f"\n[OK] Excel: {output_dir / 'templates_consolidado.xlsx'}")
    except Exception as e:
        print(f"  [WARN] No pude crear Excel: {e}")

    print(f"\n[OK] Resultados en: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
