"""
CSJN Análisis Estadístico v2 (revisado)
========================================
Script consolidado de análisis empírico para la tesis de maestría sobre
formación de mayorías en la Corte Suprema argentina.

Cambios respecto a la versión inicial:
  1. composicion: derivada de la fecha (no de la firma)
  2. n_titulares: eliminada de los modelos por colinealidad con composicion
  3. Modelo a nivel voto (multinomial logit) reemplaza el modelo de
     concurrencia a nivel caso, que tenía R²=0,009
  4. Análisis de robustez del efecto del dictamen (4 pruebas)
  5. Co-disidencia condicional al banco institucional
  6. Sensibilidad temporal del banco de 3 (sub-períodos García Mansilla)
  7. Errores estándar clusterizados por trimestre (logit) y por caso (mlogit)
  8. Validación cruzada de 5 folds para los modelos logísticos

Uso:
  python csjn_analisis_v2.py \
      --casos csjn_casos_v9.csv \
      --votos csjn_casos_v9_votos.csv \
      --output-dir resultados_v2/

Estructura de outputs:
  resultados_v2/
    csjn_resultados_v2.xlsx              — todas las tablas
    corpus_limpio_v2.csv                 — corpus modelable
    fig_dissent_forest.png               — forest plot logit disidencia
    fig_voto_mlogit_forest.png           — forest plot multinomial
    fig_codisidencia_b4.png              — heatmap banco 4
    fig_codisidencia_b5.png              — heatmap banco 5
    fig_zinb_obs_vs_pred.png             — densidad observada vs predicha
"""

import argparse
import json
import re
import warnings
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
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
HIGHTON_OUT = pd.Timestamp(2021, 11, 1)   # renuncia Highton
MAQUEDA_OUT = pd.Timestamp(2024, 12, 28)  # vencimiento Maqueda
GARCIA_IN   = pd.Timestamp(2025, 2, 28)   # asunción García Mansilla (comisión)
GARCIA_OUT  = pd.Timestamp(2025, 4, 9)    # salida García Mansilla

TITULARES_HIST = ["Rosatti", "Rosenkrantz", "Lorenzetti", "Maqueda",
                  "Highton de Nolasco", "García Mansilla"]
TITULARES_BANCO_4 = ["Rosatti", "Rosenkrantz", "Lorenzetti", "Maqueda"]
TITULARES_BANCO_5 = ["Rosatti", "Rosenkrantz", "Lorenzetti", "Maqueda",
                     "Highton de Nolasco"]

MESES_ES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}

# ── Utilidades ────────────────────────────────────────────────────────────────

def asteriscos(p):
    if pd.isna(p): return ""
    if p < 0.001: return "***"
    if p < 0.01:  return "**"
    if p < 0.05:  return "*"
    if p < 0.1:   return "†"
    return ""

def parse_fecha_es(s):
    """Parsea fecha en castellano: '3 de junio de 2021' → Timestamp."""
    if not isinstance(s, str): return pd.NaT
    m = re.match(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", s.lower().strip())
    if not m: return pd.NaT
    day, mes, year = m.group(1), m.group(2), m.group(3)
    if mes not in MESES_ES: return pd.NaT
    try:
        return pd.Timestamp(int(year), MESES_ES[mes], int(day))
    except ValueError:
        return pd.NaT

def composicion_por_fecha(d):
    """Asigna composición institucional según fecha de la sentencia."""
    if pd.isna(d): return np.nan
    if d <= HIGHTON_OUT: return "5_jueces"
    if d <  MAQUEDA_OUT: return "4_jueces"
    return "3_jueces"

def sub_periodo_b3(d):
    """Sub-períodos del banco de 3 para análisis de sensibilidad."""
    if d < GARCIA_IN:   return "A_pre_garcia"
    if d <= GARCIA_OUT: return "B_con_garcia"
    return "C_post_garcia"

# ── 1. Carga y preparación ────────────────────────────────────────────────────

def cargar_y_preparar(casos_path, votos_path):
    """Carga ambos CSV y construye variables derivadas."""
    casos = pd.read_csv(casos_path, encoding="utf-8", low_memory=False)
    votos = pd.read_csv(votos_path, encoding="utf-8", low_memory=False)

    # Fecha
    casos["date_dt"] = casos["date"].apply(parse_fecha_es)

    # Excluir el outlier (1 caso de 2014 por error de parser)
    n_pre = len(casos)
    casos = casos[casos["date_dt"].dt.year >= 2021].copy()
    n_excl = n_pre - len(casos)
    if n_excl > 0:
        print(f"  [INFO] Excluidos {n_excl} caso(s) con fecha pre-2021 (parseo erróneo del parser)")

    # Composición institucional por fecha (no por firma)
    casos["composicion"] = casos["date_dt"].apply(composicion_por_fecha)

    # Posiciones como dict
    casos["posiciones_dict"] = casos["posiciones"].apply(
        lambda x: json.loads(x) if isinstance(x, str) and x.strip().startswith("{") else {}
    )

    # Tipos numéricos
    for col in ["n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
                "word_count", "wc_mayoria", "wc_votos", "line_apertura"]:
        casos[col] = pd.to_numeric(casos[col], errors="coerce")

    for col in ["is_originaria", "is_full_bench", "is_merit_decision",
                "dictamen_presente"]:
        casos[col] = casos[col].astype(str).str.lower().isin(["1", "true"]).astype(int)

    # Variables dependientes derivadas
    casos["is_dissent"]     = casos["voting_pattern"].isin(["disidencia", "mixed"]).astype(int)
    casos["is_concurrence"] = (casos["voting_pattern"] == "segun_su_voto").astype(int)
    casos["is_fragmented"]  = casos["voting_pattern"].isin(
        ["disidencia", "segun_su_voto", "mixed"]
    ).astype(int)

    # Control: log de wc_mayoria
    casos["log_wc_mayoria"] = np.log1p(casos["wc_mayoria"])

    # Trimestre para clustering
    casos["quarter"] = casos["date_dt"].dt.to_period("Q").astype(str)

    return casos, votos

def corpus_limpio(casos):
    """Filtra el corpus modelable: excluye sin_firma e originaria."""
    return casos[
        (casos["voting_pattern"] != "sin_firma")
        & (casos["is_originaria"] == 0)
        & (casos["composicion"].notna())
    ].copy()

# ── 2. Diagnóstico previo ─────────────────────────────────────────────────────

def diagnostico_corpus(casos, df_l, output_dir):
    """Tablas descriptivas del corpus completo y limpio."""
    rows = []

    # Tabla 1: corpus por composición
    for comp in ["5_jueces", "4_jueces", "3_jueces"]:
        sub = casos[casos["composicion"] == comp]
        rows.append({
            "ámbito": "corpus_completo",
            "composicion": comp,
            "n_casos": len(sub),
            "tasa_unanime":   round((sub["voting_pattern"] == "unanime").mean(), 3),
            "tasa_dissent":   round(sub["is_dissent"].mean(), 3),
            "tasa_concurr":   round(sub["is_concurrence"].mean(), 3),
            "tasa_dictamen":  round(sub["dictamen_presente"].mean(), 3),
        })
    for comp in ["5_jueces", "4_jueces", "3_jueces"]:
        sub = df_l[df_l["composicion"] == comp]
        rows.append({
            "ámbito": "corpus_limpio",
            "composicion": comp,
            "n_casos": len(sub),
            "tasa_unanime":   round((sub["voting_pattern"] == "unanime").mean(), 3),
            "tasa_dissent":   round(sub["is_dissent"].mean(), 3),
            "tasa_concurr":   round(sub["is_concurrence"].mean(), 3),
            "tasa_dictamen":  round(sub["dictamen_presente"].mean(), 3),
        })
    return pd.DataFrame(rows)

def vif_table(df, predictoras):
    """VIF para detectar multicolinealidad."""
    X = df[predictoras].copy()
    X = sm.add_constant(X)
    rows = []
    for i, col in enumerate(X.columns):
        if col == "const":
            continue
        try:
            v = variance_inflation_factor(X.values, i)
        except Exception:
            v = np.nan
        rows.append({"variable": col, "VIF": round(v, 2) if not np.isnan(v) else "n/a"})
    return pd.DataFrame(rows)

# ── 3. Logística con SE clusterizados + cross-validation ──────────────────────

PREDICTORAS_LOGIT = ["is_merit_decision", "dictamen_presente", "log_wc_mayoria"]

def fit_logit_robust(df, dep_var, output_dir, label):
    """
    Logística con composición + predictoras.
    Reporta tres versiones: SE estándar, SE clusterizados, AUC out-of-fold.
    """
    formula = (f"{dep_var} ~ " + " + ".join(PREDICTORAS_LOGIT)
               + " + C(composicion, Treatment(reference='5_jueces'))")
    sub = df.dropna(subset=PREDICTORAS_LOGIT + [dep_var, "composicion", "quarter"]).copy()

    # Modelo con SE clusterizados por trimestre
    m_clu = smf.logit(formula, data=sub).fit(
        disp=0, maxiter=200,
        cov_type="cluster", cov_kwds={"groups": sub["quarter"]},
    )

    # Tabla de coeficientes (con SE clusterizados)
    params = m_clu.params
    se = m_clu.bse
    pvals = m_clu.pvalues
    conf = m_clu.conf_int()
    or_ = np.exp(params)
    or_ci_low  = np.exp(conf[0])
    or_ci_high = np.exp(conf[1])

    tabla = pd.DataFrame({
        "variable":   params.index,
        "coef":       params.round(4).values,
        "SE_clu":     se.round(4).values,
        "z":          (params / se).round(3).values,
        "p_clu":      pvals.round(4).values,
        "sig":        [asteriscos(p) for p in pvals.values],
        "OR":         or_.round(3).values,
        "OR_IC_low":  or_ci_low.round(3).values,
        "OR_IC_high": or_ci_high.round(3).values,
    })

    # Hosmer-Lemeshow (10 deciles)
    try:
        pred = m_clu.predict(sub)
        df_hl = pd.DataFrame({"y": sub[dep_var].values, "p": pred.values})
        df_hl["decile"] = pd.qcut(df_hl["p"], 10, duplicates="drop")
        obs = df_hl.groupby("decile", observed=True)["y"].sum()
        exp = df_hl.groupby("decile", observed=True)["p"].sum()
        n_per = df_hl.groupby("decile", observed=True)["y"].count()
        hl_stat = ((obs - exp) ** 2 / (exp * (1 - exp / n_per))).sum()
        hl_p = 1 - stats.chi2.cdf(hl_stat, df=8)
    except Exception:
        hl_stat, hl_p = np.nan, np.nan

    # AUC in-sample
    auc_in = roc_auc_score(sub[dep_var], pred)

    # AUC out-of-fold (5 folds estratificado)
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

    # Forest plot
    forest_plot(tabla, f"Forest plot — {dep_var} (OR con IC 95%, SE cluster por trimestre)",
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

# ── 4. Modelo a nivel voto (multinomial logit) ────────────────────────────────

def fit_multinomial_voto(votos, casos, output_dir):
    """
    Multinomial logit con efectos fijos por juez.
    Categoría base: mayoría. Ecuaciones: vs concurrencia, vs disidencia.
    SE clusterizados por caso_id.
    """
    # Merge con caso-level
    cols_caso = ["caso_id", "composicion", "log_wc_mayoria",
                 "voting_pattern", "is_merit_decision", "dictamen_presente",
                 "is_originaria"]
    v = votos.merge(casos[cols_caso], on="caso_id", how="left",
                    suffixes=("", "_caso"))

    # Filtros: corpus limpio + solo titulares activos (no conjueces)
    # is_originaria viene de la tabla votos (ya está en su CSV original);
    # voting_pattern viene del merge con casos (sufijo _caso)
    v = v[v["voting_pattern_caso"] != "sin_firma"]
    v = v[v["is_originaria"] == 0]
    v = v[v["es_conocido"] == 1]
    v = v[~v["juez"].astype(str).str.contains("conjuez", na=False)]
    v = v.dropna(subset=["composicion", "log_wc_mayoria"])
    v = v[v["juez"].isin(TITULARES_BANCO_5)].copy()  # excluir García Mansilla por N=1

    # Recodificar 'por su voto' como 'según su voto' (sinónimos)
    v["posicion_clean"] = v["posicion"].replace({"por su voto": "según su voto"})

    # Codificar dependiente: 0=mayoría (ref), 1=concurrencia, 2=disidencia
    y_map = {"mayoria": 0, "según su voto": 1, "en disidencia": 2}
    v["y"] = v["posicion_clean"].map(y_map)
    v = v.dropna(subset=["y"]).copy()
    v["y"] = v["y"].astype(int)

    # Predictores
    v["c_4"] = (v["composicion"] == "4_jueces").astype(float)
    v["c_3"] = (v["composicion"] == "3_jueces").astype(float)
    # Dummies de juez (Lorenzetti = referencia: el juez que menos disiente
    # relativo a su volumen de votos)
    v["j_Rosatti"]     = (v["juez"] == "Rosatti").astype(float)
    v["j_Rosenkrantz"] = (v["juez"] == "Rosenkrantz").astype(float)
    v["j_Maqueda"]     = (v["juez"] == "Maqueda").astype(float)
    v["j_Highton"]     = (v["juez"] == "Highton de Nolasco").astype(float)

    X_cols = ["c_4", "c_3", "is_merit_decision", "dictamen_presente",
              "log_wc_mayoria", "j_Rosatti", "j_Rosenkrantz", "j_Maqueda",
              "j_Highton"]
    X = sm.add_constant(v[X_cols].astype(float))
    y = v["y"].values

    m = MNLogit(y, X).fit(
        disp=0, maxiter=300,
        cov_type="cluster", cov_kwds={"groups": v["caso_id"].values}
    )

    # Tablas separadas para cada ecuación
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

    # Forest plot combinado
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

# ── 5. ZINB sobre wc_votos ────────────────────────────────────────────────────

def fit_zinb(df_l, output_dir):
    """
    Zero-Inflated Negative Binomial.
    Usa lbfgs (más estable que bfgs para este problema).
    """
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
        "exp_coef":   np.exp(params).round(3).values,  # IRR para count, OR para inflate
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

    # Plot: distribución observada vs predicha (excluyendo ceros)
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

# ── 6. Robustez del efecto del dictamen ───────────────────────────────────────

def robustez_dictamen(df_l, output_dir):
    """
    Cuatro pruebas:
      (i) Univariado (sin controles)
      (ii) Distribución por outcome (dictamen no es exógeno)
      (iii) Sub-corpus de recursos extraordinarios "puros"
      (iv) Modelo con interacción dictamen × composicion
    """
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
        {"métrica": "tasa disidencia | sin dictamen", "valor": round(sin_d["is_dissent"].mean(), 3)},
        {"métrica": "tasa disidencia | con dictamen", "valor": round(con_d["is_dissent"].mean(), 3)},
        {"métrica": "Fisher OR (disidencia ~ dictamen)", "valor": round(or_, 3)},
        {"métrica": "Fisher p", "valor": round(p_fisher, 4)},
        {"métrica": "tasa wc_votos>0 | sin dictamen", "valor": round((sin_d["wc_votos"]>0).mean(), 3)},
        {"métrica": "tasa wc_votos>0 | con dictamen", "valor": round((con_d["wc_votos"]>0).mean(), 3)},
        {"métrica": "mediana wc_votos | sin d, votos>0", "valor": round(sin_v.median(), 0) if len(sin_v) else np.nan},
        {"métrica": "mediana wc_votos | con d, votos>0", "valor": round(con_v.median(), 0) if len(con_v) else np.nan},
        {"métrica": "Mann-Whitney p (longitud votos)", "valor": round(p_mw, 4) if not np.isnan(p_mw) else "n/a"},
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

    # Re-fit logit en sub-corpus
    formula = ("is_dissent ~ is_merit_decision + dictamen_presente + log_wc_mayoria"
               " + C(composicion, Treatment(reference='5_jueces'))")
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

    # (iv) Modelo con interacción dictamen × composicion (en ZINB)
    sub_int = df_l.dropna(subset=PREDICTORAS_LOGIT + ["composicion", "wc_votos"]).copy()
    X = pd.get_dummies(sub_int[["composicion"]], drop_first=True, dtype=float)
    for col in PREDICTORAS_LOGIT:
        X[col] = sub_int[col].astype(float).values
    X["dict_x_4"] = X["composicion_4_jueces"] * X["dictamen_presente"]
    X["dict_x_5"] = X["composicion_5_jueces"] * X["dictamen_presente"]
    X = sm.add_constant(X)
    Z = X.copy()
    y = sub_int["wc_votos"].astype(int).values

    try:
        m_int = ZeroInflatedNegativeBinomialP(
            y, X.astype(float), exog_infl=Z.astype(float), inflation="logit"
        ).fit(disp=0, maxiter=500, method="lbfgs")
        resultados["robustez_interaccion"] = pd.DataFrame({
            "parametro":   m_int.params.index,
            "coef":        m_int.params.round(4).values,
            "p":           m_int.pvalues.round(4).values,
            "exp_coef":    np.exp(m_int.params).round(3).values,
            "AIC":         round(m_int.aic, 2),
        })
    except Exception as e:
        print(f"  [WARN] ZINB con interacciones no convergió: {e}")
        resultados["robustez_interaccion"] = pd.DataFrame()

    return resultados

# ── 7. Sensibilidad temporal del banco de 3 ───────────────────────────────────

def sensibilidad_b3(df_l):
    """Compara tasas de fragmentación en sub-períodos del banco de 3."""
    b3 = df_l[df_l["composicion"] == "3_jueces"].copy()
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
        })

    # chi² test de homogeneidad
    if len(b3["sub_periodo"].unique()) > 1:
        tab = pd.crosstab(b3["sub_periodo"], b3["is_dissent"])
        chi2, p, dof, _ = stats.chi2_contingency(tab)
        rows.append({
            "sub_periodo": "TEST_chi²_disidencia",
            "N": int(tab.values.sum()),
            "fecha_min": "—", "fecha_max": "—",
            "tasa_dissent": f"chi²={chi2:.2f}, p={p:.4f}, df={dof}",
            "tasa_concurr": "",
        })
        tab2 = pd.crosstab(b3["sub_periodo"], b3["is_concurrence"])
        chi2, p, dof, _ = stats.chi2_contingency(tab2)
        rows.append({
            "sub_periodo": "TEST_chi²_concurrencia",
            "N": int(tab2.values.sum()),
            "fecha_min": "—", "fecha_max": "—",
            "tasa_dissent": "",
            "tasa_concurr": f"chi²={chi2:.2f}, p={p:.4f}, df={dof}",
        })

    return pd.DataFrame(rows)

# ── 8. Co-ocurrencias condicionales al banco institucional ────────────────────

def matriz_codisidencia_condicional(df_l, jueces, comp_label, output_dir):
    """
    Calcula phi de co-disidencia entre todos los pares de jueces, condicionado
    a una composición específica. Reporta N, eventos conjuntos, phi, IC95
    bootstrap y heatmap.
    """
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
            phi, p, ic_low, ic_high = 0.0, 1.0, np.nan, np.nan
        else:
            try:
                phi, p = stats.pearsonr(a_dis, b_dis)
            except Exception:
                phi, p = np.nan, np.nan
            # Bootstrap IC95
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

    # Heatmap (matriz_phi a float, copia escribible)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    matriz_plot = matriz_phi.astype(float).copy()
    for j in matriz_plot.index:
        matriz_plot.loc[j, j] = np.nan
    sns.heatmap(matriz_plot, annot=True, fmt=".2f",
                cmap="RdBu_r", center=0,
                vmin=-0.3, vmax=0.7,
                ax=ax, square=True, cbar_kws={"label": "φ"})
    ax.set_title(f"Co-disidencia φ — banco institucional {comp_label}",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    out_path = output_dir / f"fig_codisidencia_{comp_label}.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()

    return df_out, out_path

# ── Export Excel ──────────────────────────────────────────────────────────────

def export_excel(tablas, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for nombre, df in tablas.items():
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                continue
            sheet = nombre[:31]  # Excel tope
            df.to_excel(writer, sheet_name=sheet, index=False)
    print(f"\n  [OK] Excel guardado: {output_path}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="CSJN Análisis Estadístico v2")
    ap.add_argument("--casos",      required=True)
    ap.add_argument("--votos",      required=True)
    ap.add_argument("--output-dir", default="resultados_v2")
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    print("CSJN Análisis Estadístico v2")
    print("=" * 60)
    print("Cargando datos...")
    casos, votos = cargar_y_preparar(args.casos, args.votos)
    print(f"  Casos: {len(casos)}")
    print(f"  Votos: {len(votos)}")
    print(f"  Composición por fecha:")
    for k, v in casos["composicion"].value_counts().items():
        print(f"    {k}: {v}")

    df_l = corpus_limpio(casos)
    print(f"\nCorpus limpio (no sin_firma, no originaria): N = {len(df_l)}")

    # Guardar corpus limpio
    cols_export = [
        "caso_id", "tomo", "date", "date_dt", "composicion",
        "outcome", "voting_pattern", "n_titulares",
        "is_merit_decision", "dictamen_presente",
        "wc_mayoria", "wc_votos", "log_wc_mayoria",
        "is_fragmented", "is_dissent", "is_concurrence",
        "jueces_conocidos", "tribunal_origen", "quarter",
    ]
    df_l[cols_export].to_csv(output_dir / "corpus_limpio_v2.csv",
                              index=False, encoding="utf-8")
    print(f"  CSV guardado: {output_dir / 'corpus_limpio_v2.csv'}")

    tablas = {}

    # ── Diagnóstico descriptivo ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("0. DIAGNÓSTICO DESCRIPTIVO")
    print("=" * 60)
    diag = diagnostico_corpus(casos, df_l, output_dir)
    print(diag.to_string(index=False))
    tablas["00_diag_descriptivo"] = diag

    # VIF
    print("\nVIF (multicolinealidad sin n_titulares):")
    df_v = df_l.copy()
    df_v["c_3"] = (df_v["composicion"] == "3_jueces").astype(int)
    df_v["c_4"] = (df_v["composicion"] == "4_jueces").astype(int)
    vif = vif_table(df_v, PREDICTORAS_LOGIT + ["c_3", "c_4"])
    print(vif.to_string(index=False))
    tablas["01_vif"] = vif

    # ── Logit principal: is_dissent ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("1. LOGIT — is_dissent (composición por fecha, sin n_titulares)")
    print("=" * 60)
    m_dis, t_dis, met_dis = fit_logit_robust(df_l, "is_dissent", output_dir, "dissent")
    print("\nCoeficientes (SE clusterizados):")
    print(t_dis.to_string(index=False))
    print("\nMétricas:")
    print(met_dis.to_string(index=False))
    tablas["1_logit_dissent_coef"]   = t_dis
    tablas["1_logit_dissent_metric"] = met_dis

    # ── Logit secundario: is_fragmented (modelo agregado) ─────────────────────
    print("\n" + "=" * 60)
    print("2. LOGIT — is_fragmented (modelo agregado)")
    print("=" * 60)
    m_fra, t_fra, met_fra = fit_logit_robust(df_l, "is_fragmented", output_dir, "fragmented")
    print(t_fra.to_string(index=False))
    print(met_fra.to_string(index=False))
    tablas["2_logit_fragmented_coef"]   = t_fra
    tablas["2_logit_fragmented_metric"] = met_fra

    # ── Modelo a nivel voto (multinomial) ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("3. MULTINOMIAL LOGIT a nivel voto")
    print("=" * 60)
    m_mn, t_mn, met_mn = fit_multinomial_voto(votos, casos, output_dir)
    print(t_mn.to_string(index=False))
    print(met_mn.to_string(index=False))
    tablas["3_mlogit_voto_coef"]   = t_mn
    tablas["3_mlogit_voto_metric"] = met_mn

    # ── ZINB ──────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("4. ZINB sobre wc_votos")
    print("=" * 60)
    t_zinb, met_zinb = fit_zinb(df_l, output_dir)
    if t_zinb is not None:
        print(t_zinb.to_string(index=False))
        print(met_zinb.to_string(index=False))
        tablas["4_zinb_coef"]   = t_zinb
        tablas["4_zinb_metric"] = met_zinb

    # ── Robustez del dictamen ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("5. ROBUSTEZ del efecto del dictamen")
    print("=" * 60)
    res_rob = robustez_dictamen(df_l, output_dir)
    for k, v in res_rob.items():
        print(f"\n--- {k} ---")
        print(v.to_string(index=False) if isinstance(v, pd.DataFrame) and not v.empty else "(vacío)")
        tablas[f"5_dictamen_{k}"] = v

    # ── Sensibilidad temporal del banco de 3 ──────────────────────────────────
    print("\n" + "=" * 60)
    print("6. SENSIBILIDAD del banco de 3 (sub-períodos García Mansilla)")
    print("=" * 60)
    sens = sensibilidad_b3(df_l)
    print(sens.to_string(index=False))
    tablas["6_sensibilidad_b3"] = sens

    # ── Co-disidencia condicional ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("7. CO-DISIDENCIA condicional al banco institucional")
    print("=" * 60)

    df_b4, _ = matriz_codisidencia_condicional(df_l, TITULARES_BANCO_4,
                                                "4_jueces", output_dir)
    print("\n--- Banco de 4 ---")
    print(df_b4.to_string(index=False) if not df_b4.empty else "(sin pares válidos)")
    tablas["7_codis_banco_4"] = df_b4

    df_b5, _ = matriz_codisidencia_condicional(df_l, TITULARES_BANCO_5,
                                                "5_jueces", output_dir)
    print("\n--- Banco de 5 ---")
    print(df_b5.to_string(index=False) if not df_b5.empty else "(sin pares válidos)")
    tablas["7_codis_banco_5"] = df_b5

    # ── Export ────────────────────────────────────────────────────────────────
    export_excel(tablas, output_dir / "csjn_resultados_v2.xlsx")

    print("\n" + "=" * 60)
    print(f"FINALIZADO. Resultados en: {output_dir.resolve()}")
    print("=" * 60)
    print("\nArchivos generados:")
    for f in sorted(output_dir.glob("*")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
