"""
CSJN Análisis Estadístico v4 (corpus completo tomos 329-349)
=============================================================
Adaptación de v3 al esquema del parser v18.01. Cambios:

  1. Paths de input actualizados a output/parser/csjn_casos.csv, etc.
  2. Filtro tipo_entrada == 'fallo' (excluye sumario_con_link y sumario_editorial).
  3. dictamen_presente: normalización robusta (valores: 'True', 'False', '0').
  4. caso_id_canonico en lugar de caso_id.
  5. Integra csjn_casos_zonas.csv para word count por zona (H2, H5).
  6. Integra tipo_voto_sep (clasificación A-E de votos separados, H3).
  7. N=5669 fallos, 27463 votos, 140956 zonas.

Módulos:
  0.  Carga y preparación (filtro tipo_entrada, parse fecha, composición)
  1.  Diagnóstico descriptivo
  2.  VIF
  3.  Logit is_dissent (SE clusterizados, CV)
  4.  Logit is_fragmented
  5.  Multinomial logit a nivel voto (efectos fijos por juez)
  6.  ZINB sobre wc_votos
  7.  Robustez del efecto dictamen
  8.  Sensibilidad temporal banco de 3
  9.  Co-disidencia condicional
  10. Word count por zona (H2, H5) — NUEVO
  11. Tipo de voto separado (H3) — NUEVO

Uso:
  python csjn_analisis_v4.py \\
    --casos output/parser/csjn_casos.csv \\
    --votos output/parser/csjn_casos_votos.csv \\
    --zonas output/parser/csjn_casos_zonas.csv \\
    --output-dir output/analisis/

  # Solo núcleo
  python csjn_analisis_v4.py \\
    --casos output/parser/csjn_casos.csv \\
    --votos output/parser/csjn_casos_votos.csv \\
    --zonas output/parser/csjn_casos_zonas.csv \\
    --tipo-caso nucleo \\
    --output-dir output/analisis_nucleo/
"""

__version__ = "4.0"

import argparse
import json
import re
import warnings
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP
from statsmodels.discrete.discrete_model import MNLogit
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")
sns.set_style("whitegrid")

# ── Constantes institucionales ────────────────────────────────────────────────

ARGIBAY_OUT     = pd.Timestamp(2014, 5, 10)
PETRACCHI_OUT   = pd.Timestamp(2014, 10, 12)
ZAFFARONI_OUT   = pd.Timestamp(2014, 12, 31)
FAYT_OUT        = pd.Timestamp(2015, 12, 11)
ROSATTI_IN      = pd.Timestamp(2016, 6, 29)
ROSENKRANTZ_IN  = pd.Timestamp(2016, 8, 22)
HIGHTON_OUT     = pd.Timestamp(2021, 11, 1)
MAQUEDA_OUT     = pd.Timestamp(2024, 12, 29)
GARCIA_IN       = pd.Timestamp(2025, 2, 27)
GARCIA_OUT      = pd.Timestamp(2025, 4, 7)

TITULARES_BANCO_7 = ["Lorenzetti", "Highton de Nolasco", "Fayt", "Petracchi",
                     "Maqueda", "Zaffaroni", "Argibay"]
TITULARES_BANCO_5 = ["Rosatti", "Rosenkrantz", "Lorenzetti", "Maqueda",
                     "Highton de Nolasco"]
TITULARES_BANCO_4 = ["Rosatti", "Rosenkrantz", "Lorenzetti", "Maqueda"]
TITULARES_BANCO_3 = ["Rosatti", "Rosenkrantz", "Lorenzetti"]
TITULARES_HIST    = sorted(set(TITULARES_BANCO_7 + TITULARES_BANCO_5 +
                                TITULARES_BANCO_4 + ["García Mansilla"]))

MESES_ES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}

REGIMENES = ["banco_de_7", "transicion", "banco_de_5", "banco_de_4", "banco_de_3"]

# ── Utilidades ────────────────────────────────────────────────────────────────

def asteriscos(p):
    if pd.isna(p): return ""
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "†"
    return ""

def parse_fecha_es(s):
    """Parsea fecha en castellano con variantes:
    '3 de junio de 2021', '23 de mayo 2006', '19 diciembre de 2006'."""
    if not isinstance(s, str): return pd.NaT
    s = s.lower().strip()
    # Variante canónica: "D de MES de AAAA"
    m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", s)
    if not m:
        # Variante sin segundo "de": "D de MES AAAA"
        m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+(\d{4})", s)
    if not m:
        # Variante sin primer "de": "D MES de AAAA"
        m = re.match(r"(\d{1,2})\s+(\w+)\s+de\s+(\d{4})", s)
    if not m: return pd.NaT
    day, mes, year = m.group(1), m.group(2), m.group(3)
    if mes not in MESES_ES: return pd.NaT
    try:
        return pd.Timestamp(int(year), MESES_ES[mes], int(day))
    except ValueError:
        return pd.NaT

def composicion_por_fecha(d):
    """Composición institucional según fecha de sentencia (5 regímenes)."""
    if pd.isna(d): return np.nan
    if d <  ARGIBAY_OUT:    return "banco_de_7"
    if d <  ROSENKRANTZ_IN: return "transicion"
    if d <= HIGHTON_OUT:    return "banco_de_5"
    if d <= MAQUEDA_OUT:    return "banco_de_4"
    return "banco_de_3"

def sub_periodo_b3(d):
    """Sub-períodos del banco de 3 para sensibilidad García Mansilla."""
    if d < GARCIA_IN:   return "A_pre_garcia"
    if d <= GARCIA_OUT: return "B_con_garcia"
    return "C_post_garcia"

# ── 0. Carga y preparación ───────────────────────────────────────────────────

def cargar_y_preparar(casos_path, votos_path, zonas_path=None):
    """Carga CSVs y construye variables derivadas.

    Cambios v4 respecto a v3:
      - Filtra tipo_entrada == 'fallo'
      - caso_id_canonico como ID canónico
      - dictamen_presente: normaliza de str a int robusto
      - Incorpora zonas (word count por zona) si se provee
    """
    casos = pd.read_csv(casos_path, encoding="utf-8", low_memory=False)
    votos = pd.read_csv(votos_path, encoding="utf-8", low_memory=False)

    # ── Filtro tipo_entrada ──
    n_pre = len(casos)
    if "tipo_entrada" in casos.columns:
        casos = casos[casos["tipo_entrada"] == "fallo"].copy()
        n_filt = n_pre - len(casos)
        if n_filt > 0:
            print(f"  [INFO] Filtro tipo_entrada=fallo: {n_pre} → {len(casos)} "
                  f"(excluidos {n_filt}: sumario_con_link + sumario_editorial)")
    else:
        print("  [WARN] Columna tipo_entrada no encontrada; sin filtrar.")

    # ── Alias de ID ──
    # v4 usa caso_id_canonico; creamos alias para compatibilidad interna
    if "caso_id_canonico" in casos.columns and "caso_id" not in casos.columns:
        casos["caso_id"] = casos["caso_id_canonico"]
    if "caso_id_canonico" in votos.columns and "caso_id" not in votos.columns:
        votos["caso_id"] = votos["caso_id_canonico"]

    # Filtrar votos a casos que sobrevivieron el filtro tipo_entrada
    votos = votos[votos["caso_id"].isin(casos["caso_id"])].copy()

    # ── Fecha ──
    casos["date_dt"] = casos["date"].apply(parse_fecha_es)
    n_pre2 = len(casos)
    fechas_validas = (
        casos["date_dt"].notna()
        & (casos["date_dt"].dt.year >= 2003)
        & (casos["date_dt"].dt.year <= 2030)
    )
    casos = casos[fechas_validas].copy()
    n_excl = n_pre2 - len(casos)
    if n_excl > 0:
        print(f"  [INFO] Excluidos {n_excl} caso(s) por fecha fuera de rango")

    # ── Composición institucional ──
    casos["composicion"] = casos["date_dt"].apply(composicion_por_fecha)

    # ── Posiciones como dict ──
    casos["posiciones_dict"] = casos["posiciones"].apply(
        lambda x: json.loads(x) if isinstance(x, str) and x.strip().startswith("{") else {}
    )

    # ── Tipos numéricos ──
    for col in ["n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
                "word_count", "wc_mayoria", "wc_votos", "wc_considerando",
                "wc_dictamen", "linea_inicio"]:
        if col in casos.columns:
            casos[col] = pd.to_numeric(casos[col], errors="coerce")

    # ── Booleanos ──
    for col in ["is_originaria", "is_full_bench", "is_merit_decision"]:
        if col in casos.columns:
            casos[col] = casos[col].astype(str).str.lower().isin(["1", "true"]).astype(int)

    # ── dictamen_presente: normalización robusta ──
    # Valores posibles en el parser v18.01: 'True', 'False', '0'
    # '0' corresponde a sumarios sin datos → ya filtrados, pero por si acaso
    casos["dictamen_presente"] = (
        casos["dictamen_presente"].astype(str).str.lower()
        .isin(["1", "true"]).astype(int)
    )

    # ── Variables dependientes derivadas ──
    casos["is_dissent"]     = casos["voting_pattern"].isin(["disidencia", "mixed"]).astype(int)
    casos["is_concurrence"] = (casos["voting_pattern"] == "segun_su_voto").astype(int)
    casos["is_fragmented"]  = casos["voting_pattern"].isin(
        ["disidencia", "segun_su_voto", "mixed"]
    ).astype(int)

    # ── Control: log de wc_mayoria ──
    casos["log_wc_mayoria"] = np.log1p(casos["wc_mayoria"])

    # ── Trimestre para clustering ──
    casos["quarter"] = casos["date_dt"].dt.to_period("Q").astype(str)

    # ── Zonas: word count por zona para cada caso ──
    zonas = None
    if zonas_path is not None:
        zonas = pd.read_csv(zonas_path, encoding="utf-8", low_memory=False)
        if "caso_id_canonico" in zonas.columns and "caso_id" not in zonas.columns:
            zonas["caso_id"] = zonas["caso_id_canonico"]
        zonas = zonas[zonas["caso_id"].isin(casos["caso_id"])].copy()

        # Pivotar: wc por zona para cada caso
        wc_por_zona = (zonas.groupby(["caso_id", "zona"])["wc"]
                       .sum().unstack(fill_value=0))
        # Prefijo z_ para evitar colisiones
        wc_por_zona.columns = [f"z_wc_{c}" for c in wc_por_zona.columns]
        wc_por_zona = wc_por_zona.reset_index()
        casos = casos.merge(wc_por_zona, on="caso_id", how="left")

        # Rellenar con 0 las zonas faltantes
        z_cols = [c for c in casos.columns if c.startswith("z_wc_")]
        casos[z_cols] = casos[z_cols].fillna(0)

        # Variables derivadas de zonas
        casos["z_wc_voto_separado"] = casos.get("z_wc_voto_separado", 0)
        casos["z_wc_cuerpo"]        = casos.get("z_wc_cuerpo", 0)
        casos["z_wc_dictamen"]      = casos.get("z_wc_dictamen", 0)
        # Ratio esfuerzo argumentativo: voto_separado / (cuerpo + voto_separado)
        total_arg = casos["z_wc_cuerpo"] + casos["z_wc_voto_separado"]
        casos["ratio_voto_vs_cuerpo"] = np.where(
            total_arg > 0,
            casos["z_wc_voto_separado"] / total_arg,
            0
        )
        print(f"  [INFO] Zonas integradas: {len(zonas)} filas, "
              f"{len(z_cols)} columnas z_wc_*")

    return casos, votos, zonas

def corpus_limpio(casos):
    """Corpus modelable: excluye sin_firma e originaria."""
    return casos[
        (casos["voting_pattern"] != "sin_firma")
        & (casos["is_originaria"] == 0)
        & (casos["composicion"].notna())
    ].copy()

# ── 1. Diagnóstico descriptivo ───────────────────────────────────────────────

def diagnostico_corpus(casos, df_l, output_dir):
    """Tablas descriptivas del corpus completo y limpio."""
    rows = []
    for ambito, df in [("corpus_completo", casos), ("corpus_limpio", df_l)]:
        for comp in REGIMENES:
            sub = df[df["composicion"] == comp]
            if len(sub) == 0: continue
            rows.append({
                "ámbito":         ambito,
                "composicion":    comp,
                "n_casos":        len(sub),
                "tasa_unanime":   round((sub["voting_pattern"] == "unanime").mean(), 3),
                "tasa_dissent":   round(sub["is_dissent"].mean(), 3),
                "tasa_concurr":   round(sub["is_concurrence"].mean(), 3),
                "tasa_fragm":     round(sub["is_fragmented"].mean(), 3),
                "tasa_dictamen":  round(sub["dictamen_presente"].mean(), 3),
                "wc_mayoria_med": round(sub["wc_mayoria"].median(), 0),
                "wc_votos_med":   round(sub["wc_votos"].median(), 0),
            })
    return pd.DataFrame(rows)

def vif_table(df, predictoras):
    """VIF para multicolinealidad."""
    X = df[predictoras].copy().dropna()
    X = sm.add_constant(X)
    rows = []
    for i, col in enumerate(X.columns):
        if col == "const": continue
        try:
            v = variance_inflation_factor(X.values, i)
        except Exception:
            v = np.nan
        rows.append({"variable": col, "VIF": round(v, 2) if not np.isnan(v) else "n/a"})
    return pd.DataFrame(rows)

# ── 2. Logística con SE clusterizados + CV ───────────────────────────────────

PREDICTORAS_LOGIT = ["is_merit_decision", "dictamen_presente", "log_wc_mayoria"]

def fit_logit_robust(df, dep_var, output_dir, label):
    """Logística con composición + predictoras. SE clusterizados por trimestre."""
    formula = (f"{dep_var} ~ " + " + ".join(PREDICTORAS_LOGIT)
               + " + C(composicion, Treatment(reference='banco_de_5'))")
    sub = df.dropna(subset=PREDICTORAS_LOGIT + [dep_var, "composicion", "quarter"]).copy()

    if sub[dep_var].nunique() < 2:
        print(f"  [WARN] {dep_var} sin varianza — modelo omitido.")
        return None, pd.DataFrame(), pd.DataFrame()

    m_clu = smf.logit(formula, data=sub).fit(
        disp=0, maxiter=200,
        cov_type="cluster", cov_kwds={"groups": sub["quarter"]},
    )

    params = m_clu.params
    se = m_clu.bse
    pvals = m_clu.pvalues
    conf = m_clu.conf_int()
    or_ = np.exp(params)

    tabla = pd.DataFrame({
        "variable":   params.index,
        "coef":       params.round(4).values,
        "SE_clu":     se.round(4).values,
        "z":          (params / se).round(3).values,
        "p_clu":      pvals.round(4).values,
        "sig":        [asteriscos(p) for p in pvals.values],
        "OR":         or_.round(3).values,
        "OR_IC_low":  np.exp(conf[0]).round(3).values,
        "OR_IC_high": np.exp(conf[1]).round(3).values,
    })

    # Hosmer-Lemeshow
    try:
        pred = m_clu.predict(sub)
        df_hl = pd.DataFrame({"y": sub[dep_var].values, "p": pred.values})
        df_hl["decile"] = pd.qcut(df_hl["p"], 10, duplicates="drop")
        obs = df_hl.groupby("decile", observed=True)["y"].sum()
        exp_ = df_hl.groupby("decile", observed=True)["p"].sum()
        n_per = df_hl.groupby("decile", observed=True)["y"].count()
        hl_stat = ((obs - exp_) ** 2 / (exp_ * (1 - exp_ / n_per))).sum()
        hl_p = 1 - stats.chi2.cdf(hl_stat, df=8)
    except Exception:
        hl_stat, hl_p = np.nan, np.nan

    # AUC in-sample
    pred = m_clu.predict(sub)
    auc_in = roc_auc_score(sub[dep_var], pred)

    # AUC out-of-fold (5-fold stratified)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs = []
    for tr, te in skf.split(sub, sub[dep_var]):
        try:
            m_cv = smf.logit(formula, data=sub.iloc[tr]).fit(disp=0, maxiter=200)
            pred_cv = m_cv.predict(sub.iloc[te])
            aucs.append(roc_auc_score(sub.iloc[te][dep_var], pred_cv))
        except Exception:
            pass
    auc_oof = np.mean(aucs) if aucs else np.nan
    auc_oof_sd = np.std(aucs) if aucs else np.nan

    metricas = pd.DataFrame([{
        "n":                int(m_clu.nobs),
        "log_likelihood":   round(m_clu.llf, 2),
        "McFadden_R2":      round(m_clu.prsquared, 4),
        "AIC":              round(m_clu.aic, 2),
        "BIC":              round(m_clu.bic, 2),
        "Hosmer_Lemeshow":  round(hl_stat, 3) if not np.isnan(hl_stat) else "n/a",
        "HL_p":             round(hl_p, 4) if not np.isnan(hl_p) else "n/a",
        "AUC_in_sample":    round(auc_in, 3),
        "AUC_out_of_fold":  round(auc_oof, 3) if not np.isnan(auc_oof) else "n/a",
        "AUC_oof_sd":       round(auc_oof_sd, 3) if not np.isnan(auc_oof_sd) else "n/a",
        "n_clusters":       sub["quarter"].nunique(),
    }])

    forest_plot(tabla, f"Forest plot — {dep_var} (OR, IC 95%, SE cluster por trimestre)",
                output_dir / f"fig_{label}_forest.png")

    return m_clu, tabla, metricas

def forest_plot(tabla, titulo, output_path):
    """Forest plot de odds ratios con IC 95%."""
    df = tabla[tabla["variable"] != "Intercept"].copy()
    df = df.iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, max(4, 0.5 * len(df))))
    y = np.arange(len(df))
    ax.errorbar(
        df["OR"], y,
        xerr=[df["OR"] - df["OR_IC_low"], df["OR_IC_high"] - df["OR"]],
        fmt="o", markersize=8, capsize=4, color="#2E5C8A", ecolor="#2E5C8A",
    )
    ax.axvline(x=1, color="gray", linestyle="--", alpha=0.6, label="OR = 1")
    ax.set_yticks(y)
    ax.set_yticklabels(df["variable"])
    ax.set_xscale("log")
    ax.set_xlabel("Odds Ratio (escala logarítmica, IC 95%)")
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

# ── 3. Multinomial logit a nivel voto ────────────────────────────────────────

def fit_multinomial_voto(votos, casos, output_dir):
    """
    Multinomial logit con efectos fijos por juez.
    Categoría base: mayoría. Ecuaciones: vs concurrencia, vs disidencia.
    SE clusterizados por caso_id.
    Lorenzetti = referencia (presente en los 5 regímenes).
    """
    cols_caso = ["caso_id", "composicion", "log_wc_mayoria",
                 "voting_pattern", "is_merit_decision", "dictamen_presente",
                 "is_originaria"]
    v = votos.merge(casos[cols_caso], on="caso_id", how="left",
                    suffixes=("", "_caso"))

    # Filtros
    vp_col = "voting_pattern_caso" if "voting_pattern_caso" in v.columns else "voting_pattern"
    v = v[v[vp_col] != "sin_firma"]
    orig_col = "is_originaria_caso" if "is_originaria_caso" in v.columns else "is_originaria"
    v = v[v[orig_col] == 0]
    v = v[v["es_conocido"] == 1]
    v = v[~v["juez"].astype(str).str.contains("conjuez", na=False)]
    v = v.dropna(subset=["composicion", "log_wc_mayoria"])

    JUECES_MODELO = TITULARES_BANCO_7 + ["Rosatti", "Rosenkrantz"]
    v = v[v["juez"].isin(JUECES_MODELO)].copy()

    # Recodificar posiciones
    v["posicion_clean"] = v["posicion"].replace({
        "por su voto": "según su voto",
    })

    y_map = {"mayoria": 0, "según su voto": 1, "en disidencia": 2}
    v["y"] = v["posicion_clean"].map(y_map)
    v = v.dropna(subset=["y"]).copy()
    v["y"] = v["y"].astype(int)

    # Dummies de composición (banco_de_5 = referencia)
    v["c_7"]     = (v["composicion"] == "banco_de_7").astype(float)
    v["c_trans"] = (v["composicion"] == "transicion").astype(float)
    v["c_4"]     = (v["composicion"] == "banco_de_4").astype(float)
    v["c_3"]     = (v["composicion"] == "banco_de_3").astype(float)

    # Dummies de juez (Lorenzetti = referencia)
    juez_dummies = []
    for juez in JUECES_MODELO:
        if juez == "Lorenzetti": continue
        n_juez = (v["juez"] == juez).sum()
        if n_juez < 30:
            print(f"    [INFO] Excluido del modelo: {juez} (N={n_juez} < 30)")
            continue
        col = f"j_{juez.replace(' ', '_').replace('é','e').replace('í','i')}"
        v[col] = (v["juez"] == juez).astype(float)
        juez_dummies.append(col)

    comp_dummies = []
    for comp_col, comp_label in [("c_7","banco_de_7"), ("c_trans","transicion"),
                                   ("c_4","banco_de_4"), ("c_3","banco_de_3")]:
        n_comp = (v["composicion"] == comp_label).sum()
        if n_comp < 30:
            print(f"    [INFO] Excluido del modelo: {comp_label} (N={n_comp} < 30)")
            continue
        comp_dummies.append(comp_col)

    X_cols = comp_dummies + ["is_merit_decision", "dictamen_presente",
                             "log_wc_mayoria"] + juez_dummies
    X = sm.add_constant(v[X_cols].astype(float))
    y = v["y"].values

    m = MNLogit(y, X).fit(
        disp=0, maxiter=300,
        cov_type="cluster", cov_kwds={"groups": v["caso_id"].values}
    )

    var_names = ["Intercept"] + X_cols

    def construir_tabla(eq_idx, eq_label):
        params = m.params[eq_idx]
        bse    = m.bse[eq_idx]
        pvals  = m.pvalues[eq_idx]
        return pd.DataFrame({
            "ecuacion":  eq_label,
            "variable":  var_names,
            "coef":      params.round(4).values,
            "SE_clu":    bse.round(4).values,
            "z":         (params / bse).round(3).values,
            "p":         pvals.round(4).values,
            "sig":       [asteriscos(p) for p in pvals.values],
            "OR_rel":    np.exp(params).round(3).values,
        })

    tabla_conc = construir_tabla(0, "Concurrencia_vs_Mayoria")
    tabla_diss = construir_tabla(1, "Disidencia_vs_Mayoria")
    tabla_full = pd.concat([tabla_conc, tabla_diss], ignore_index=True)

    metricas = pd.DataFrame([{
        "n_votos":          int(m.nobs),
        "n_casos":          v["caso_id"].nunique(),
        "log_likelihood":   round(m.llf, 2),
        "McFadden_R2":      round(m.prsquared, 4),
        "AIC":              round(m.aic, 2),
        "n_mayoria":        int((y == 0).sum()),
        "n_concurrencia":   int((y == 1).sum()),
        "n_disidencia":     int((y == 2).sum()),
    }])

    forest_plot_mlogit(tabla_full, output_dir / "fig_voto_mlogit_forest.png")

    return m, tabla_full, metricas

def forest_plot_mlogit(tabla_full, output_path):
    """Forest plot lado-a-lado: concurrencia | disidencia."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    for ax, (eq, eq_lbl) in zip(axes, [
        ("Concurrencia_vs_Mayoria", "Concurrencia vs Mayoría"),
        ("Disidencia_vs_Mayoria",   "Disidencia vs Mayoría"),
    ]):
        df = tabla_full[(tabla_full["ecuacion"] == eq)
                        & (tabla_full["variable"] != "Intercept")].copy()
        df = df.iloc[::-1]
        df["OR_low"]  = np.exp(df["coef"] - 1.96 * df["SE_clu"]).values
        df["OR_high"] = np.exp(df["coef"] + 1.96 * df["SE_clu"]).values
        y = np.arange(len(df))
        ax.errorbar(
            df["OR_rel"], y,
            xerr=[df["OR_rel"] - df["OR_low"], df["OR_high"] - df["OR_rel"]],
            fmt="o", markersize=7, capsize=3,
            color="#2E5C8A", ecolor="#2E5C8A",
        )
        ax.axvline(x=1, color="gray", linestyle="--", alpha=0.6)
        ax.set_yticks(y)
        ax.set_yticklabels(df["variable"])
        ax.set_xscale("log")
        ax.set_xlabel("OR (escala log, IC 95%)")
        ax.set_title(eq_lbl, fontsize=11, fontweight="bold")
    plt.suptitle("Multinomial logit a nivel voto (SE cluster por caso_id)",
                 fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

# ── 4. ZINB sobre wc_votos ──────────────────────────────────────────────────

def fit_zinb(df_l, output_dir):
    """Zero-Inflated Negative Binomial (método lbfgs)."""
    sub = df_l.dropna(subset=PREDICTORAS_LOGIT + ["wc_votos", "composicion"]).copy()
    sub["wc_votos"] = sub["wc_votos"].astype(int)

    X = pd.get_dummies(sub[["composicion"]], drop_first=True, dtype=float)
    for col in PREDICTORAS_LOGIT:
        X[col] = sub[col].astype(float).values
    X = sm.add_constant(X)
    Z = X.copy()
    y = sub["wc_votos"].values

    try:
        m = ZeroInflatedNegativeBinomialP(
            y, X.astype(float), exog_infl=Z.astype(float), inflation="logit"
        ).fit(disp=0, maxiter=500, method="lbfgs")
    except Exception as e:
        print(f"  [ERROR] ZINB no convergió: {e}")
        return None, None

    params = m.params
    se = m.bse
    pvals = m.pvalues

    tabla = pd.DataFrame({
        "parametro":  params.index,
        "coef":       params.round(4).values,
        "SE":         se.round(4).values,
        "z":          (params / se).round(3).values,
        "p":          pvals.round(4).values,
        "sig":        [asteriscos(p) for p in pvals.values],
        "exp_coef":   np.exp(params).round(3).values,
    })

    metricas = pd.DataFrame([{
        "n":          int(m.nobs),
        "log_lik":    round(m.llf, 2),
        "AIC":        round(m.aic, 2),
        "BIC":        round(m.bic, 2),
        "alpha_NB":   round(m.params.get("alpha", np.nan), 3),
        "p_ceros_obs":round((y == 0).mean(), 3),
        "n_ceros":    int((y == 0).sum()),
    }])

    # Plot distribución observada vs predicha
    pred = m.predict(X.astype(float))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(y[y > 0], bins=50, alpha=0.55, label="Observado (wc_votos > 0)",
            color="#2E5C8A")
    ax.hist(pred[pred > 0], bins=50, alpha=0.55, label="Predicho ZINB",
            color="#D2691E")
    ax.set_xlabel("wc_votos")
    ax.set_ylabel("Frecuencia")
    ax.set_title("ZINB: distribución observada vs predicha (excluye ceros)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "fig_zinb_obs_vs_pred.png", dpi=150, bbox_inches="tight")
    plt.close()

    return tabla, metricas

# ── 5. Robustez del efecto dictamen ──────────────────────────────────────────

def robustez_dictamen(df_l, output_dir):
    """Cuatro pruebas de robustez del efecto del dictamen."""
    resultados = {}

    # (i) Univariado
    sin_d = df_l[df_l["dictamen_presente"] == 0]
    con_d = df_l[df_l["dictamen_presente"] == 1]

    tab_dis = pd.crosstab(df_l["dictamen_presente"], df_l["is_dissent"])
    or_, p_fisher = stats.fisher_exact(tab_dis.values)

    sin_v = df_l[(df_l["dictamen_presente"] == 0) & (df_l["wc_votos"] > 0)]["wc_votos"]
    con_v = df_l[(df_l["dictamen_presente"] == 1) & (df_l["wc_votos"] > 0)]["wc_votos"]
    if len(con_v) > 0 and len(sin_v) > 0:
        u, p_mw = stats.mannwhitneyu(sin_v, con_v)
    else:
        u, p_mw = np.nan, np.nan

    resultados["univariado"] = pd.DataFrame([
        {"métrica": "N sin dictamen", "valor": len(sin_d)},
        {"métrica": "N con dictamen", "valor": len(con_d)},
        {"métrica": "tasa disidencia | sin dictamen",
         "valor": round(sin_d["is_dissent"].mean(), 3) if len(sin_d) else "n/a"},
        {"métrica": "tasa disidencia | con dictamen",
         "valor": round(con_d["is_dissent"].mean(), 3) if len(con_d) else "n/a"},
        {"métrica": "Fisher OR (disidencia ~ dictamen)", "valor": round(or_, 3)},
        {"métrica": "Fisher p", "valor": round(p_fisher, 4)},
        {"métrica": "tasa wc_votos>0 | sin dictamen",
         "valor": round((sin_d["wc_votos"]>0).mean(), 3) if len(sin_d) else "n/a"},
        {"métrica": "tasa wc_votos>0 | con dictamen",
         "valor": round((con_d["wc_votos"]>0).mean(), 3) if len(con_d) else "n/a"},
        {"métrica": "mediana wc_votos | sin d, votos>0",
         "valor": round(sin_v.median(), 0) if len(sin_v) else np.nan},
        {"métrica": "mediana wc_votos | con d, votos>0",
         "valor": round(con_v.median(), 0) if len(con_v) else np.nan},
        {"métrica": "Mann-Whitney p (longitud votos)",
         "valor": round(p_mw, 4) if not np.isnan(p_mw) else "n/a"},
    ])

    # (ii) Distribución del dictamen por outcome
    resultados["distribucion_dictamen"] = (
        pd.crosstab(df_l["outcome"], df_l["dictamen_presente"], margins=True)
        .reset_index()
        .rename(columns={0: "sin_dictamen", 1: "con_dictamen", "All": "total"})
    )

    # (iii) Sub-corpus de recursos extraordinarios "puros"
    OUTCOMES_REX = {"hace_lugar", "desestima", "procedente", "inadmisible_280",
                    "revoca", "confirma", "abstracto", "desistimiento"}
    sub_rex = df_l[df_l["outcome"].isin(OUTCOMES_REX)].copy()

    formula = ("is_dissent ~ is_merit_decision + dictamen_presente + log_wc_mayoria"
               " + C(composicion, Treatment(reference='banco_de_5'))")
    try:
        m_rex = smf.logit(formula, data=sub_rex).fit(
            disp=0, cov_type="cluster", cov_kwds={"groups": sub_rex["quarter"]}
        )
        params = m_rex.params
        se = m_rex.bse
        pvals = m_rex.pvalues
        conf = m_rex.conf_int()
        resultados["robustez_rex"] = pd.DataFrame({
            "variable":   params.index,
            "coef":       params.round(4).values,
            "SE_clu":     se.round(4).values,
            "p_clu":      pvals.round(4).values,
            "OR":         np.exp(params).round(3).values,
            "OR_IC_low":  np.exp(conf[0]).round(3).values,
            "OR_IC_high": np.exp(conf[1]).round(3).values,
            "N":          int(m_rex.nobs),
        })
    except Exception as e:
        print(f"  [WARN] Logit en sub-corpus REX no convergió: {e}")
        resultados["robustez_rex"] = pd.DataFrame()

    # (iv) Interacción dictamen × composición (ZINB)
    # Inflate model uses only main effects (simpler → better convergence);
    # count model includes interactions.
    sub_int = df_l.dropna(subset=PREDICTORAS_LOGIT + ["composicion", "wc_votos"]).copy()
    X_base = pd.get_dummies(sub_int[["composicion"]], drop_first=True, dtype=float)
    for col in PREDICTORAS_LOGIT:
        X_base[col] = sub_int[col].astype(float).values

    # Z = inflate model (main effects only)
    Z = sm.add_constant(X_base.copy())

    # X = count model (main effects + interactions)
    X = X_base.copy()
    for c in list(X.columns):
        if c.startswith("composicion_banco_de_") or c.startswith("composicion_transicion"):
            X[f"dict_x_{c.replace('composicion_', '')}"] = (
                X[c] * X["dictamen_presente"]
            )
    X = sm.add_constant(X)
    y = sub_int["wc_votos"].astype(int).values

    m_int = None
    for method in ["lbfgs", "bfgs", "nm"]:
        try:
            m_int = ZeroInflatedNegativeBinomialP(
                y, X.astype(float), exog_infl=Z.astype(float), inflation="logit"
            ).fit(disp=0, maxiter=500, method=method)
            # Check for NaN p-values (sign of non-convergence)
            if m_int.pvalues.isna().all():
                print(f"  [INFO] ZINB interacción (method={method}): "
                      f"p-values NaN, reintentando...")
                m_int = None
                continue
            break
        except Exception:
            m_int = None
            continue

    if m_int is not None:
        has_nan_p = m_int.pvalues.isna().any()
        resultados["robustez_interaccion"] = pd.DataFrame({
            "parametro":   m_int.params.index,
            "coef":        m_int.params.round(4).values,
            "SE":          m_int.bse.round(4).values,
            "p":           m_int.pvalues.round(4).values,
            "sig":         [asteriscos(p) for p in m_int.pvalues.values],
            "exp_coef":    np.exp(m_int.params).round(3).values,
            "AIC":         round(m_int.aic, 2),
        })
        if has_nan_p:
            print("  [WARN] ZINB interacción: convergencia parcial (algunos p NaN)")
    else:
        print("  [WARN] ZINB con interacciones no convergió en ningún método.")
        resultados["robustez_interaccion"] = pd.DataFrame()

    return resultados

# ── 6. Sensibilidad temporal del banco de 3 ──────────────────────────────────

def sensibilidad_b3(df_l):
    """Compara tasas de fragmentación en sub-períodos del banco de 3."""
    b3 = df_l[df_l["composicion"] == "banco_de_3"].copy()
    if len(b3) == 0:
        return pd.DataFrame()
    b3["sub_periodo"] = b3["date_dt"].apply(sub_periodo_b3)

    rows = []
    for sp in ["A_pre_garcia", "B_con_garcia", "C_post_garcia"]:
        sub = b3[b3["sub_periodo"] == sp]
        if len(sub) == 0: continue
        rows.append({
            "sub_periodo":     sp,
            "N":               len(sub),
            "fecha_min":       str(sub["date_dt"].min().date()),
            "fecha_max":       str(sub["date_dt"].max().date()),
            "tasa_dissent":    round(sub["is_dissent"].mean(), 3),
            "tasa_concurr":    round(sub["is_concurrence"].mean(), 3),
            "tasa_fragm":      round(sub["is_fragmented"].mean(), 3),
        })

    if len(b3["sub_periodo"].unique()) > 1:
        for var, var_label in [("is_dissent", "disidencia"),
                                ("is_concurrence", "concurrencia")]:
            tab = pd.crosstab(b3["sub_periodo"], b3[var])
            if tab.shape[1] < 2: continue
            chi2, p, dof, _ = stats.chi2_contingency(tab)
            rows.append({
                "sub_periodo": f"TEST_chi²_{var_label}",
                "N": int(tab.values.sum()),
                "fecha_min": "—", "fecha_max": "—",
                "tasa_dissent": f"chi²={chi2:.2f}, p={p:.4f}, df={dof}" if var == "is_dissent" else "",
                "tasa_concurr": f"chi²={chi2:.2f}, p={p:.4f}, df={dof}" if var == "is_concurrence" else "",
                "tasa_fragm": "",
            })

    return pd.DataFrame(rows)

# ── 7. Co-disidencia condicional ─────────────────────────────────────────────

def matriz_codisidencia_condicional(df_l, jueces, comp_label, output_dir):
    """Co-disidencia φ entre pares de jueces, condicionada a composición."""
    sub = df_l[df_l["composicion"] == comp_label].copy()
    if len(sub) < 30:
        return pd.DataFrame(), None

    rows = []
    matriz_phi = pd.DataFrame(np.nan, index=jueces, columns=jueces)
    rng = np.random.default_rng(42)

    for a, b in combinations(jueces, 2):
        presente = sub["posiciones_dict"].apply(
            lambda d: a in d and b in d if isinstance(d, dict) else False
        )
        s = sub[presente]
        if len(s) < 30:
            continue

        a_dis = s["posiciones_dict"].apply(
            lambda d: 1 if d.get(a) == "en disidencia" else 0
        ).values
        b_dis = s["posiciones_dict"].apply(
            lambda d: 1 if d.get(b) == "en disidencia" else 0
        ).values

        if a_dis.sum() == 0 or b_dis.sum() == 0:
            phi, p = 0.0, 1.0
            ic_low, ic_high = np.nan, np.nan
        else:
            try:
                phi, p = stats.pearsonr(a_dis, b_dis)
            except Exception:
                phi, p = np.nan, np.nan
            n = len(a_dis)
            phis_boot = []
            for _ in range(2000):
                idx = rng.integers(0, n, n)
                ai, bi = a_dis[idx], b_dis[idx]
                if ai.sum() == 0 or bi.sum() == 0 or ai.sum() == n or bi.sum() == n:
                    continue
                try:
                    pb = np.corrcoef(ai, bi)[0, 1]
                    if not np.isnan(pb):
                        phis_boot.append(pb)
                except Exception:
                    continue
            ic_low  = np.percentile(phis_boot, 2.5) if phis_boot else np.nan
            ic_high = np.percentile(phis_boot, 97.5) if phis_boot else np.nan

        rows.append({
            "juez_a":       a,
            "juez_b":       b,
            "n_copres":     len(s),
            "n_a_dis":      int(a_dis.sum()),
            "n_b_dis":      int(b_dis.sum()),
            "n_codis":      int((a_dis * b_dis).sum()),
            "phi":          round(phi, 3) if not np.isnan(phi) else np.nan,
            "p":            round(p, 4) if not np.isnan(p) else np.nan,
            "sig":          asteriscos(p) if not np.isnan(p) else "",
            "IC95_low":     round(ic_low, 3) if not np.isnan(ic_low) else np.nan,
            "IC95_high":    round(ic_high, 3) if not np.isnan(ic_high) else np.nan,
        })
        matriz_phi.loc[a, b] = phi
        matriz_phi.loc[b, a] = phi

    if not rows:
        return pd.DataFrame(), None

    df_out = pd.DataFrame(rows).sort_values("phi", ascending=False, na_position="last")

    # Heatmap
    fig, ax = plt.subplots(figsize=(8, 6.5))
    matriz_plot = matriz_phi.astype(float).copy()
    for j in matriz_plot.index:
        matriz_plot.loc[j, j] = np.nan
    sns.heatmap(matriz_plot, annot=True, fmt=".2f",
                cmap="RdBu_r", center=0,
                vmin=-0.3, vmax=0.7,
                ax=ax, square=True, cbar_kws={"label": "φ"})
    ax.set_title(f"Co-disidencia φ — {comp_label}",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    out_path = output_dir / f"fig_codisidencia_{comp_label}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()

    return df_out, out_path

# ── 8. Word count por zona (H2, H5) — NUEVO ─────────────────────────────────

def analisis_zonas(df_l, output_dir):
    """
    Análisis de esfuerzo argumentativo por zona.
    Usa columnas z_wc_* generadas al integrar csjn_casos_zonas.csv.

    H2: ¿El dictamen reduce el esfuerzo argumentativo en el cuerpo?
    H5: ¿Los votos separados tienen extensión autónoma respecto del cuerpo?
    """
    z_cols = [c for c in df_l.columns if c.startswith("z_wc_")]
    if not z_cols:
        print("  [WARN] No hay columnas z_wc_* — omitiendo análisis de zonas.")
        return {}

    resultados = {}

    # (a) Descriptivo: mediana de wc por zona y composición
    zonas_interes = ["z_wc_cuerpo", "z_wc_dictamen", "z_wc_voto_separado",
                     "z_wc_firma", "z_wc_dispositivo"]
    zonas_interes = [z for z in zonas_interes if z in df_l.columns]

    rows = []
    for comp in REGIMENES:
        sub = df_l[df_l["composicion"] == comp]
        if len(sub) == 0: continue
        row = {"composicion": comp, "n": len(sub)}
        for z in zonas_interes:
            row[f"med_{z.replace('z_wc_', '')}"] = round(sub[z].median(), 0)
            row[f"mean_{z.replace('z_wc_', '')}"] = round(sub[z].mean(), 0)
        rows.append(row)
    resultados["zonas_descriptivo"] = pd.DataFrame(rows)

    # (b) Dictamen y esfuerzo: ¿el dictamen reduce wc del cuerpo?
    if "z_wc_cuerpo" in df_l.columns:
        sin_d = df_l[df_l["dictamen_presente"] == 0]["z_wc_cuerpo"]
        con_d = df_l[df_l["dictamen_presente"] == 1]["z_wc_cuerpo"]
        if len(sin_d) > 0 and len(con_d) > 0:
            u, p_mw = stats.mannwhitneyu(sin_d, con_d, alternative="two-sided")
            resultados["dictamen_vs_cuerpo"] = pd.DataFrame([{
                "grupo":           "sin dictamen",
                "n":               len(sin_d),
                "mediana_cuerpo":  round(sin_d.median(), 0),
                "mean_cuerpo":     round(sin_d.mean(), 0),
            }, {
                "grupo":           "con dictamen",
                "n":               len(con_d),
                "mediana_cuerpo":  round(con_d.median(), 0),
                "mean_cuerpo":     round(con_d.mean(), 0),
            }, {
                "grupo":           "Mann-Whitney",
                "n":               "",
                "mediana_cuerpo":  f"U={u:.0f}",
                "mean_cuerpo":     f"p={p_mw:.4f}",
            }])

    # (c) Ratio voto_separado / (cuerpo + voto_separado) por composición
    if "ratio_voto_vs_cuerpo" in df_l.columns:
        # Solo casos con votos separados (ratio > 0)
        con_voto = df_l[df_l["ratio_voto_vs_cuerpo"] > 0]
        rows_r = []
        for comp in REGIMENES:
            sub = con_voto[con_voto["composicion"] == comp]
            if len(sub) < 5: continue
            rows_r.append({
                "composicion":       comp,
                "n_con_voto_sep":    len(sub),
                "ratio_mediana":     round(sub["ratio_voto_vs_cuerpo"].median(), 3),
                "ratio_mean":        round(sub["ratio_voto_vs_cuerpo"].mean(), 3),
                "wc_voto_sep_med":   round(sub["z_wc_voto_separado"].median(), 0),
            })
        resultados["ratio_esfuerzo"] = pd.DataFrame(rows_r)

    # (d) Plot: boxplot de z_wc_cuerpo por composición y dictamen
    if "z_wc_cuerpo" in df_l.columns:
        fig, ax = plt.subplots(figsize=(10, 5))
        plot_data = df_l[["composicion", "dictamen_presente", "z_wc_cuerpo"]].copy()
        plot_data["dictamen"] = plot_data["dictamen_presente"].map(
            {0: "Sin dictamen", 1: "Con dictamen"}
        )
        order = [c for c in REGIMENES if c in plot_data["composicion"].unique()]
        sns.boxplot(data=plot_data, x="composicion", y="z_wc_cuerpo",
                    hue="dictamen", order=order, ax=ax,
                    showfliers=False, palette=["#D2691E", "#2E5C8A"])
        ax.set_ylabel("Word count del cuerpo")
        ax.set_xlabel("Composición institucional")
        ax.set_title("WC cuerpo por composición y presencia de dictamen (H2)")
        plt.tight_layout()
        plt.savefig(output_dir / "fig_zonas_cuerpo_x_dictamen.png",
                    dpi=150, bbox_inches="tight")
        plt.close()

    return resultados

# ── 9. Tipo de voto separado (H3) — NUEVO ───────────────────────────────────

def analisis_tipo_voto_sep(votos, casos, output_dir):
    """
    Distribución de tipo_voto_sep (A-E) por composición.

    Tipos:
      A = voto separado con fundamentos propios completos
      B = se remite a considerandos ajenos + agrega/modifica
      C = se remite íntegramente a otro voto
      D = disidencia pura
      E = indeterminado / inclasificable
    (Referencia: parser v18.01)

    H3: ausencia de incentivos para opinión unificada → proliferación de
    concurrencias (especialmente A y B vs C).
    """
    if "tipo_voto_sep" not in votos.columns:
        print("  [WARN] tipo_voto_sep no disponible — omitiendo módulo.")
        return {}

    cols_caso = ["caso_id", "composicion"]
    v = votos.merge(casos[cols_caso], on="caso_id", how="left")
    v = v[v["tipo_voto_sep"].notna()].copy()

    if len(v) == 0:
        print("  [WARN] Sin votos con tipo_voto_sep clasificado.")
        return {}

    resultados = {}

    # (a) Distribución global
    resultados["tipo_voto_sep_global"] = (
        v["tipo_voto_sep"].value_counts()
        .reset_index()
        .rename(columns={"index": "tipo", "count": "n"})
    )

    # (b) Cruce tipo_voto_sep × composición
    ct = pd.crosstab(v["tipo_voto_sep"], v["composicion"], margins=True)
    resultados["tipo_voto_sep_x_comp"] = ct.reset_index()

    # (c) Cruce tipo_voto_sep × posicion
    ct2 = pd.crosstab(v["tipo_voto_sep"], v["posicion"], margins=True)
    resultados["tipo_voto_sep_x_posicion"] = ct2.reset_index()

    # (d) Extensión (wc_voto) por tipo_voto_sep
    if "wc_voto" in v.columns:
        rows = []
        for tipo in sorted(v["tipo_voto_sep"].unique()):
            sub = v[v["tipo_voto_sep"] == tipo]
            wc = sub["wc_voto"].dropna()
            rows.append({
                "tipo_voto_sep": tipo,
                "n":             len(sub),
                "wc_mediana":    round(wc.median(), 0) if len(wc) else np.nan,
                "wc_mean":       round(wc.mean(), 0) if len(wc) else np.nan,
                "wc_p25":        round(wc.quantile(0.25), 0) if len(wc) else np.nan,
                "wc_p75":        round(wc.quantile(0.75), 0) if len(wc) else np.nan,
            })
        resultados["tipo_voto_sep_wc"] = pd.DataFrame(rows)

    # (e) Plot: stacked bar de tipo_voto_sep por composición
    ct_plot = pd.crosstab(v["composicion"], v["tipo_voto_sep"], normalize="index")
    order = [c for c in REGIMENES if c in ct_plot.index]
    if order:
        ct_plot = ct_plot.loc[order]
        fig, ax = plt.subplots(figsize=(10, 5))
        ct_plot.plot(kind="bar", stacked=True, ax=ax,
                     colormap="Set2", edgecolor="white")
        ax.set_ylabel("Proporción")
        ax.set_xlabel("Composición institucional")
        ax.set_title("Tipo de voto separado por composición (H3)")
        ax.legend(title="Tipo", bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.tight_layout()
        plt.savefig(output_dir / "fig_tipo_voto_sep_x_comp.png",
                    dpi=150, bbox_inches="tight")
        plt.close()

    return resultados

# ── Export Excel ─────────────────────────────────────────────────────────────

def export_excel(tablas, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for nombre, df in tablas.items():
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                continue
            sheet = nombre[:31]
            df.to_excel(writer, sheet_name=sheet, index=False)
    print(f"\n  [OK] Excel guardado: {output_path}")

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="CSJN Análisis Estadístico v4")
    ap.add_argument("--casos",  default="output/parser/csjn_casos.csv")
    ap.add_argument("--votos",  default="output/parser/csjn_casos_votos.csv")
    ap.add_argument("--zonas",  default=None,
                    help="Path a csjn_casos_zonas.csv (opcional, habilita módulo zonas)")
    ap.add_argument("--output-dir", default="output/analisis")
    ap.add_argument("--tipo-caso", default="all",
                    choices=["all", "nucleo", "admisibilidad", "originaria"])
    ap.add_argument("--templates", default=None,
                    help="Path a templates_resultado.csv")
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"CSJN Análisis Estadístico v{__version__}")
    print("=" * 60)
    print("Cargando datos...")

    casos, votos, zonas = cargar_y_preparar(args.casos, args.votos, args.zonas)
    print(f"  Casos (fallos): {len(casos)}")
    print(f"  Votos: {len(votos)}")
    print(f"  Composición por fecha:")
    for k, v_ in casos["composicion"].value_counts().items():
        print(f"    {k}: {v_}")

    # ── Filtro tipo_caso ──
    if args.tipo_caso != "all":
        n_pre = len(casos)
        if "tipo_caso_grupo" not in casos.columns:
            print(f"\n  [INFO] Computando tipo_caso_grupo on-the-fly...")
            from clasificador_tipo_caso import asignar_tipo_caso, GRUPO_MAP
            casos["tipo_caso"]       = casos.apply(asignar_tipo_caso, axis=1)
            casos["tipo_caso_grupo"] = casos["tipo_caso"].map(GRUPO_MAP)
        casos = casos[casos["tipo_caso_grupo"] == args.tipo_caso].copy()
        votos = votos[votos["caso_id"].isin(casos["caso_id"])].copy()
        print(f"\n  Filtro tipo_caso={args.tipo_caso}: {n_pre} → {len(casos)} casos")

    # ── Templates opcionales ──
    if args.templates:
        try:
            df_t = pd.read_csv(args.templates, low_memory=False)
            cols_t = ["caso_id", "template_lorenzetti_vidal",
                      "template_rosenkrantz_no_lev", "cita_levinas_en_caso"]
            cols_disponibles = [c for c in cols_t if c in df_t.columns]
            if "caso_id_canonico" in df_t.columns and "caso_id" not in df_t.columns:
                df_t["caso_id"] = df_t["caso_id_canonico"]
            casos = casos.merge(df_t[cols_disponibles], on="caso_id", how="left")
            n_lor = casos.get("template_lorenzetti_vidal", pd.Series(dtype=bool)).fillna(False).sum()
            n_ros = casos.get("template_rosenkrantz_no_lev", pd.Series(dtype=bool)).fillna(False).sum()
            print(f"\n  Templates integrados: Lor+Vidal={int(n_lor)}, Ros+noLev={int(n_ros)}")
        except Exception as e:
            print(f"\n  [WARN] No pude integrar templates: {e}")

    df_l = corpus_limpio(casos)
    print(f"\nCorpus limpio (no sin_firma, no originaria): N = {len(df_l)}")

    # ── Guardar corpus limpio ──
    cols_export = [
        "caso_id", "tomo", "date", "date_dt", "composicion",
        "outcome", "voting_pattern", "n_titulares",
        "is_merit_decision", "dictamen_presente",
        "wc_mayoria", "wc_votos", "log_wc_mayoria",
        "is_fragmented", "is_dissent", "is_concurrence",
        "jueces_conocidos", "tribunal_origen", "quarter",
    ]
    # Columnas opcionales
    for col in ["tipo_caso", "tipo_caso_grupo", "template_lorenzetti_vidal",
                "template_rosenkrantz_no_lev", "cita_levinas_en_caso",
                "z_wc_cuerpo", "z_wc_dictamen", "z_wc_voto_separado",
                "ratio_voto_vs_cuerpo"]:
        if col in df_l.columns:
            cols_export.append(col)

    cols_export = [c for c in cols_export if c in df_l.columns]
    df_l[cols_export].to_csv(output_dir / "corpus_limpio_v4.csv",
                              index=False, encoding="utf-8")
    print(f"  CSV guardado: {output_dir / 'corpus_limpio_v4.csv'}")

    tablas = {}

    # ══════════════════════════════════════════════════════════════════════════
    # 0. DIAGNÓSTICO DESCRIPTIVO
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("0. DIAGNÓSTICO DESCRIPTIVO")
    print("=" * 60)
    diag = diagnostico_corpus(casos, df_l, output_dir)
    print(diag.to_string(index=False))
    tablas["00_diag_descriptivo"] = diag

    # VIF
    print("\nVIF (multicolinealidad):")
    df_v = df_l.copy()
    df_v["c_3"] = (df_v["composicion"] == "banco_de_3").astype(int)
    df_v["c_4"] = (df_v["composicion"] == "banco_de_4").astype(int)
    vif = vif_table(df_v, PREDICTORAS_LOGIT + ["c_3", "c_4"])
    print(vif.to_string(index=False))
    tablas["01_vif"] = vif

    # ══════════════════════════════════════════════════════════════════════════
    # 1. LOGIT — is_dissent
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("1. LOGIT — is_dissent")
    print("=" * 60)
    m_dis, t_dis, met_dis = fit_logit_robust(df_l, "is_dissent", output_dir, "dissent")
    if not t_dis.empty:
        print(t_dis.to_string(index=False))
        print(met_dis.to_string(index=False))
    tablas["1_logit_dissent_coef"]   = t_dis
    tablas["1_logit_dissent_metric"] = met_dis

    # ══════════════════════════════════════════════════════════════════════════
    # 2. LOGIT — is_fragmented
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("2. LOGIT — is_fragmented")
    print("=" * 60)
    m_fra, t_fra, met_fra = fit_logit_robust(df_l, "is_fragmented", output_dir, "fragmented")
    if not t_fra.empty:
        print(t_fra.to_string(index=False))
        print(met_fra.to_string(index=False))
    tablas["2_logit_fragmented_coef"]   = t_fra
    tablas["2_logit_fragmented_metric"] = met_fra

    # ══════════════════════════════════════════════════════════════════════════
    # 3. MULTINOMIAL LOGIT a nivel voto
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("3. MULTINOMIAL LOGIT a nivel voto")
    print("=" * 60)
    m_mn, t_mn, met_mn = fit_multinomial_voto(votos, casos, output_dir)
    print(t_mn.to_string(index=False))
    print(met_mn.to_string(index=False))
    tablas["3_mlogit_voto_coef"]   = t_mn
    tablas["3_mlogit_voto_metric"] = met_mn

    # ══════════════════════════════════════════════════════════════════════════
    # 4. ZINB sobre wc_votos
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("4. ZINB sobre wc_votos")
    print("=" * 60)
    t_zinb, met_zinb = fit_zinb(df_l, output_dir)
    if t_zinb is not None:
        print(t_zinb.to_string(index=False))
        print(met_zinb.to_string(index=False))
        tablas["4_zinb_coef"]   = t_zinb
        tablas["4_zinb_metric"] = met_zinb

    # ══════════════════════════════════════════════════════════════════════════
    # 5. ROBUSTEZ del dictamen
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("5. ROBUSTEZ del efecto del dictamen")
    print("=" * 60)
    res_rob = robustez_dictamen(df_l, output_dir)
    for k, v_ in res_rob.items():
        print(f"\n--- {k} ---")
        print(v_.to_string(index=False) if isinstance(v_, pd.DataFrame) and not v_.empty else "(vacío)")
        tablas[f"5_dictamen_{k}"] = v_

    # ══════════════════════════════════════════════════════════════════════════
    # 6. SENSIBILIDAD banco de 3
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("6. SENSIBILIDAD del banco de 3 (sub-períodos García Mansilla)")
    print("=" * 60)
    sens = sensibilidad_b3(df_l)
    if not sens.empty:
        print(sens.to_string(index=False))
    else:
        print("  (sin datos para banco_de_3)")
    tablas["6_sensibilidad_b3"] = sens

    # ══════════════════════════════════════════════════════════════════════════
    # 7. CO-DISIDENCIA condicional
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("7. CO-DISIDENCIA condicional al banco institucional")
    print("=" * 60)
    for jueces, label in [(TITULARES_BANCO_7, "banco_de_7"),
                           (TITULARES_BANCO_5, "banco_de_5"),
                           (TITULARES_BANCO_4, "banco_de_4"),
                           (TITULARES_BANCO_3, "banco_de_3")]:
        df_cd, _ = matriz_codisidencia_condicional(df_l, jueces, label, output_dir)
        print(f"\n--- {label} ---")
        print(df_cd.to_string(index=False) if not df_cd.empty else "(sin pares válidos)")
        tablas[f"7_codis_{label}"] = df_cd

    # ══════════════════════════════════════════════════════════════════════════
    # 8. WORD COUNT POR ZONA (H2, H5)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("8. WORD COUNT POR ZONA (H2, H5)")
    print("=" * 60)
    res_zonas = analisis_zonas(df_l, output_dir)
    for k, v_ in res_zonas.items():
        print(f"\n--- {k} ---")
        print(v_.to_string(index=False) if isinstance(v_, pd.DataFrame) and not v_.empty else "(vacío)")
        tablas[f"8_zonas_{k}"] = v_

    # ══════════════════════════════════════════════════════════════════════════
    # 9. TIPO DE VOTO SEPARADO (H3)
    # ══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("9. TIPO DE VOTO SEPARADO (H3)")
    print("=" * 60)
    res_tvs = analisis_tipo_voto_sep(votos, casos, output_dir)
    for k, v_ in res_tvs.items():
        print(f"\n--- {k} ---")
        print(v_.to_string(index=False) if isinstance(v_, pd.DataFrame) and not v_.empty else "(vacío)")
        tablas[f"9_tvs_{k}"] = v_

    # ══════════════════════════════════════════════════════════════════════════
    # EXPORT
    # ══════════════════════════════════════════════════════════════════════════
    export_excel(tablas, output_dir / "csjn_resultados_v4.xlsx")

    print("\n" + "=" * 60)
    print(f"FINALIZADO. Resultados en: {output_dir.resolve()}")
    print("=" * 60)
    print("\nArchivos generados:")
    for f in sorted(output_dir.glob("*")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
