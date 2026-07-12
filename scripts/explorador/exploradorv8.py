"""
Explorador del Corpus CSJN v8 — auditoría de zonificación y sidecars del deriver
================================================================================
Streamlit app para explorar los fallos parseados del corpus CSJN.

Cambios v8 respecto de v7 (diseño H186, cierra pendiente M16):\n  - v8.1 (misma sesion): tabla con MULTI-seleccion (los ticks eligen, no\n    abren; boton «Abrir caso» con 1 tickeado), export de casos crudos .md\n    (anclaje canonico source_file+lineas, leccion B102) y generador de\n    reporte de auditoria .md (filtros + banderas + muestra + marcas +\n    crudos) como insumo directo de la sesion H siguiente.
  - Capa de datos: left-join graceful de TODOS los sidecars del deriver
    (recursos, partes, epilogo, materia) sobre csjn_casos.csv. Schema
    verificado contra parser v26.1 (39 cols, sin causa_inadmisibilidad:
    esa columna vive en el deriver desde H148/M26 paso 3).
  - wc y n_segmentos por TODAS las zonas (pivot de zonas.csv), no solo
    epilogo/residuo. Sliders dinamicos por zona. Namespace wcz_*/nseg_*
    para no colisionar con las columnas wc_* del parser (fix post-smoke:
    wc_dictamen existia en ambas fuentes).
  - Gramatica de zonas (instrumento NUEVO, sin antecedente en DEUDA):
    secuencia colapsada por caso + flags de violacion. Modela los votos
    (dispositivo>firma>voto_separado>cuerpo>dispositivo>firma es legitimo).
  - Flags estructurales calibrados sobre datos reales (H186):
    sin firma (20 casos), sin dispositivo (49), firma fragmentada >=4 seg
    (453), wc_firma > 200 (142, p95=71), cuerpo con wc 0, cobertura baja.
  - Tab Auditoria (M16: modo auditoria-de-precision separado del masivo):
    panel de banderas con conteo y click-para-filtrar, muestreo aleatorio
    reproducible (seed visible), marcado TP/FP/dudoso con nota y export CSV.
  - Detalle en tabs (Fuente / Metadatos / Votos y zonas): la fuente usa el
    ancho completo. Panel inline de considerando/por_ello completos desde
    csjn_casos_textos.csv (pendiente M16, habilitado por split H113).
  - Filtros nuevos del deriver: disposicion, admisibilidad,
    causa_inadmisibilidad (recuperada del deriver), es_revision_fondo,
    via_recurso, reenvia, parte_ganadora, multi_recurso, partes_capa,
    roles de partes, materia_fuente, epilogo_status, y los diagnosticos
    status_localizacion / status_fin / pista_fin.

Leccion H045 vigente: el explorador NO recomputa logica del parser (los
regex del visor divergian). Todo se lee de los CSVs canonicos; el .md del
corpus solo se renderiza pintado por zonas.csv.

Todos los filtros categoricos se autopoblan del CSV (sin listas
hardcodeadas), de modo que el explorador sigue funcionando si cambian los
valores del parser/deriver.

Uso:
    cd corpus-csjn
    streamlit run scripts/explorador/exploradorv8.py
"""

import datetime
import streamlit as st
import pandas as pd
from pathlib import Path

# -- Config ------------------------------------------------------------------

st.set_page_config(
    page_title="Corpus CSJN — Explorador v8",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ROOT    = Path.cwd()
PARSER_DIR   = REPO_ROOT / "output" / "parser"
CASOS_CSV    = PARSER_DIR / "csjn_casos.csv"
TEXTOS_CSV   = PARSER_DIR / "csjn_casos_textos.csv"
VOTOS_CSV    = PARSER_DIR / "csjn_casos_votos.csv"
ZONAS_CSV    = PARSER_DIR / "csjn_casos_zonas.csv"
MATERIA_CSV  = PARSER_DIR / "csjn_casos_materia.csv"
RECURSOS_CSV = PARSER_DIR / "csjn_casos_recursos.csv"
PARTES_CSV   = PARSER_DIR / "csjn_casos_partes.csv"
EPILOGO_CSV  = PARSER_DIR / "csjn_casos_epilogo.csv"
CORPUS_DIR   = REPO_ROOT / "corpus"

# Prefijos de claves de widgets de filtro (para "limpiar filtros")
FILTER_KEY_PREFIXES = ("f_", "tri_")

# Universo de zonas de zonas.csv (verificado H186) + intersticio (computado
# solo al renderizar la fuente: lineas del bloque sin zona asignada).
ZONAS_UNIVERSO = [
    "residuo_caso_anterior", "sumario", "dictamen", "apertura", "cuerpo",
    "dispositivo", "firma", "voto_separado", "epilogo",
]

# Umbrales calibrados sobre el corpus real (H186):
#   wc firma p50=20 p95=71 max=18353; nseg firma 1-3 cubre ~92%.
UMBRAL_WC_FIRMA        = 200   # 142 casos por encima
UMBRAL_NSEG_FIRMA      = 4     # 453 casos con >=4 segmentos
UMBRAL_WC_EPILOGO      = 500   # historico v7 / validador B117 (H179)
UMBRAL_WC_RESIDUO      = 300   # historico v7
UMBRAL_COBERTURA_BAJA  = 0.85  # proporcion de lineas del bloque zonificadas

# -- Paleta de colores por zona ----------------------------------------------

ZONA_STYLE = {
    # zona:             (icono, bg,        fg,        label)
    "residuo_caso_anterior": ("🗑️", "#3a1a1a", "#ff6666", "Residuo caso ant."),
    "sumario":          ("📑", "#1a2a3a", "#5cb8ff", "Sumario"),
    "dictamen":         ("📜", "#2a1a2a", "#c060c0", "Dictamen"),
    "apertura":         ("🔶", "#3a2a00", "#ffd700", "Apertura"),
    "cuerpo":           ("📋", "#1a2a2a", "#60c0c0", "Cuerpo"),
    "dispositivo":      ("⚖️", "#1a3a1a", "#7fff7f", "Dispositivo"),
    "firma":            ("✒️", "#1a1a3a", "#7f7fff", "Firma"),
    "voto_separado":    ("🗳️", "#3a2a1a", "#ffbf7f", "Voto separado"),
    "epilogo":          ("📎", "#2a2a1a", "#c0a060", "Epilogo"),
    "intersticio":      ("",   "#1a1a1a", "#888888", "Intersticio"),
    "header_pagina":    ("",   "#0e1117", "#444444", "Header pagina"),
}

# Definicion de banderas de auditoria: clave -> (etiqueta, descripcion corta)
FLAGS_DEF = {
    "flag_sin_firma":            ("Sin zona firma",
                                  "fallo zonificado sin ningun segmento firma"),
    "flag_sin_dispositivo":      ("Sin dispositivo",
                                  "fallo zonificado sin segmento dispositivo"),
    "flag_sin_cuerpo":           ("Sin cuerpo",
                                  "fallo zonificado sin segmento cuerpo"),
    "flag_sin_apertura":         ("Sin apertura",
                                  "fallo zonificado sin segmento apertura"),
    "flag_firma_fragmentada":    (f"Firma en ≥{UMBRAL_NSEG_FIRMA} segmentos",
                                  "firma muy partida (banner/OCR/falso corte)"),
    "flag_wc_firma_outlier":     (f"Firma > {UMBRAL_WC_FIRMA} wc",
                                  "firma que probablemente se comio otra zona"),
    "flag_cuerpo_cero":          ("Cuerpo con wc 0",
                                  "clase B117: cuerpo flipeado entero a otra zona"),
    "flag_epilogo_no_terminal":  ("Epilogo no terminal",
                                  "hay zonas despues del epilogo (gramatica)"),
    "flag_residuo_tardio":       ("Residuo no inicial",
                                  "residuo_caso_anterior fuera de la posicion 0"),
    "flag_apertura_multiple":    ("Apertura multiple",
                                  "mas de un tramo de apertura (colapsado)"),
    "flag_sumario_dictamen_tardio": ("Sumario/dictamen tardio",
                                  "sumario o dictamen despues de la apertura"),
    "flag_firma_antes_dispositivo": ("Firma antes del dispositivo",
                                  "primera firma precede al primer dispositivo"),
    "flag_cobertura_baja":       (f"Cobertura < {int(UMBRAL_COBERTURA_BAJA*100)}%",
                                  "muchas lineas del bloque sin zona (intersticio)"),
    "flag_wc_epilogo_outlier":   (f"Epilogo > {UMBRAL_WC_EPILOGO} wc",
                                  "validador historico B117/H179"),
    "flag_wc_residuo_outlier":   (f"Residuo > {UMBRAL_WC_RESIDUO} wc",
                                  "residuo sobredimensionado (familia B089/B096)"),
}

# Generar CSS dinamicamente
def genera_css():
    rules = []
    for zona, (_, bg, fg, _) in ZONA_STYLE.items():
        cls = zona.replace(" ", "_")
        bold = "font-weight: bold;" if zona in (
            "apertura", "dictamen", "dispositivo", "firma",
            "voto_separado", "residuo_caso_anterior"
        ) else ""
        rules.append(f".z-{cls} {{ background-color: {bg}; color: {fg}; {bold} }}")
    return "\n".join(rules)

CSS = f"""
<style>
.source-block {{
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    line-height: 1.5;
    background-color: #0e1117;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    max-height: 78vh;
    overflow-y: auto;
}}
.source-line {{
    white-space: pre-wrap;
    word-wrap: break-word;
}}
.line-num {{
    color: #555;
    display: inline-block;
    width: 4em;
    text-align: right;
    margin-right: 1em;
    user-select: none;
}}
.section-sep {{
    border-top: 1px dashed #444;
    margin: 4px 0 2px 0;
    padding-top: 2px;
    font-size: 0.65rem;
    color: #888;
    font-family: sans-serif;
}}
.z-hidden {{ display: none; }}
{genera_css()}

.vp-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.75rem; font-weight: bold;
}}
.vp-unanime       {{ background: #1a3a1a; color: #7fff7f; }}
.vp-disidencia    {{ background: #3a1a1a; color: #ff7f7f; }}
.vp-segun_su_voto {{ background: #3a2a1a; color: #ffbf7f; }}
.vp-mixed         {{ background: #2a2a3a; color: #bf7fff; }}
.vp-sin_firma     {{ background: #333;    color: #999; }}

.leyenda {{
    font-size: 0.7rem; margin-bottom: 0.5rem;
    display: flex; flex-wrap: wrap; gap: 4px;
}}
.leyenda span {{ padding: 1px 6px; border-radius: 3px; }}

.inadm-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.75rem; font-weight: bold;
    background: #3a1a1a; color: #ff9b6b;
}}
.flag-badge {{
    display: inline-block; padding: 2px 8px; border-radius: 12px;
    font-size: 0.72rem; font-weight: bold; margin: 1px 2px;
    background: #3a2a00; color: #ffd27f;
}}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# -- Carga de datos ----------------------------------------------------------

@st.cache_data
def load_zonas():
    df = pd.read_csv(ZONAS_CSV, encoding="utf-8", dtype=str)
    for col in ["linea_ini", "linea_fin", "n_lineas", "wc"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def compute_zona_metrics():
    """wc_/nseg_ por zona + secuencia colapsada + flags de gramatica.

    Instrumento nuevo (sin antecedente en DEUDA, verificado por grep H186).
    La gramatica modela los votos: despues de la firma de mayoria pueden
    repetirse bloques voto_separado/cuerpo/dispositivo/firma; las reglas de
    violacion son solo las que sobreviven a ese patron (calibrado sobre las
    secuencias reales del corpus).
    """
    zonas = load_zonas()

    # Cobertura: lineas asignadas a CUALQUIER zona (incluye header_pagina)
    nl_total = zonas.groupby("caso_id_canonico")["n_lineas"].sum()

    z = zonas[zonas["zona"] != "header_pagina"].copy()
    z = z.sort_values(["caso_id_canonico", "linea_ini"])

    wc = z.groupby(["caso_id_canonico", "zona"])["wc"].sum().unstack(fill_value=0)
    ns = z.groupby(["caso_id_canonico", "zona"]).size().unstack(fill_value=0)

    m = pd.DataFrame(index=wc.index)
    for zona in ZONAS_UNIVERSO:
        m[f"wcz_{zona}"] = wc.get(zona, 0)
        m[f"nseg_{zona}"] = ns.get(zona, 0)
    m["n_lineas_zonificadas"] = nl_total

    # Secuencia colapsada (segmentos contiguos de la misma zona = 1 tramo)
    def _collapse(serie):
        out = []
        for x in serie:
            if not out or out[-1] != x:
                out.append(x)
        return out

    seqs = z.groupby("caso_id_canonico")["zona"].apply(_collapse)
    m["secuencia_zonas"] = seqs.map(lambda s: ">".join(s))

    # Flags de gramatica sobre la secuencia colapsada
    def _flags(s):
        first = {}
        for i, x in enumerate(s):
            first.setdefault(x, i)
        f = {}
        f["flag_epilogo_no_terminal"] = (
            "epilogo" in first
            and any(x != "epilogo" for x in s[first["epilogo"] + 1:])
        )
        f["flag_residuo_tardio"] = (
            "residuo_caso_anterior" in first
            and first["residuo_caso_anterior"] > 0
        )
        f["flag_apertura_multiple"] = s.count("apertura") > 1
        i_ap = first.get("apertura")
        f["flag_sumario_dictamen_tardio"] = (
            i_ap is not None
            and any(x in ("sumario", "dictamen") for x in s[i_ap + 1:])
        )
        f["flag_firma_antes_dispositivo"] = (
            "firma" in first and "dispositivo" in first
            and first["firma"] < first["dispositivo"]
        )
        return f

    m = m.join(seqs.map(_flags).apply(pd.Series))

    # Flags estructurales / de outlier
    m["flag_sin_firma"]         = m["nseg_firma"] == 0
    m["flag_sin_dispositivo"]   = m["nseg_dispositivo"] == 0
    m["flag_sin_cuerpo"]        = m["nseg_cuerpo"] == 0
    m["flag_sin_apertura"]      = m["nseg_apertura"] == 0
    m["flag_firma_fragmentada"] = m["nseg_firma"] >= UMBRAL_NSEG_FIRMA
    m["flag_wc_firma_outlier"]  = m["wcz_firma"] > UMBRAL_WC_FIRMA
    m["flag_cuerpo_cero"]       = (m["nseg_cuerpo"] > 0) & (m["wcz_cuerpo"] == 0)
    m["flag_wc_epilogo_outlier"] = m["wcz_epilogo"] > UMBRAL_WC_EPILOGO
    m["flag_wc_residuo_outlier"] = m["wcz_residuo_caso_anterior"] > UMBRAL_WC_RESIDUO
    return m


@st.cache_data
def load_casos():
    """csjn_casos.csv + left-joins graceful de sidecars + metricas de zona.

    Patron graceful (H112): si un sidecar no existe, el explorador sigue
    andando sin sus columnas. Ningun join altera el n de filas (todos 1:1
    por caso_id_canonico; epilogo cubre solo fallos, el resto queda NaN).
    """
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    for col in ["tomo", "linea_inicio", "linea_fin", "linea_fin_real",
                "n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
                "word_count", "wc_mayoria", "wc_votos", "wc_considerando",
                "wc_dictamen"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["pagina"] = df["caso_id_canonico"].str.extract(r"_p(\d+)$").astype(float)

    # materia (sidecar H112)
    if MATERIA_CSV.exists():
        mat = pd.read_csv(MATERIA_CSV, encoding="utf-8", dtype=str)
        cols = [c for c in ["caso_id_canonico", "materia", "materia_capa",
                            "materia_fuente"] if c in mat.columns]
        df = df.merge(mat[cols], on="caso_id_canonico", how="left")

    # recursos (deriver M26/M39): trae causa_inadmisibilidad, que desde
    # H148 NO vive en casos.csv. Se dropea su es_queja (colisiona con el
    # es_queja del parser; fuente canonica del flag = casos.csv).
    if RECURSOS_CSV.exists():
        rec = pd.read_csv(RECURSOS_CSV, encoding="utf-8", dtype=str)
        rec = rec.drop(columns=[c for c in ["es_queja"] if c in rec.columns])
        df = df.merge(rec, on="caso_id_canonico", how="left")

    # partes (deriver M29/M32)
    if PARTES_CSV.exists():
        par = pd.read_csv(PARTES_CSV, encoding="utf-8", dtype=str)
        df = df.merge(par, on="caso_id_canonico", how="left")

    # epilogo (sidecar extraer_epilogos; 5697 filas = solo fallos).
    # Se renombra para no colisionar (wc, n_seg) y NO se carga epilogo_text
    # (pesado; el texto se ve pintado en el visor de fuente).
    if EPILOGO_CSV.exists():
        epi = pd.read_csv(
            EPILOGO_CSV, encoding="utf-8", dtype=str,
            usecols=["caso_id_canonico", "epilogo_status", "n_seg", "wc"],
        )
        epi = epi.rename(columns={"n_seg": "epilogo_n_seg",
                                  "wc": "epilogo_wc_sidecar"})
        df = df.merge(epi, on="caso_id_canonico", how="left")

    # metricas de zona + gramatica
    if ZONAS_CSV.exists():
        zm = compute_zona_metrics()
        df = df.join(zm, on="caso_id_canonico")
        span = df["linea_fin_real"] - df["linea_inicio"] + 1
        df["pct_cobertura"] = (df["n_lineas_zonificadas"] / span).clip(upper=1.0)
        df["flag_cobertura_baja"] = df["pct_cobertura"] < UMBRAL_COBERTURA_BAJA
        # Flags solo aplican a casos zonificados; el resto queda False para
        # que los checkboxes no arrastren sumarios/entradas sin zonas.
        for fcol in FLAGS_DEF:
            if fcol in df.columns:
                df[fcol] = df[fcol].fillna(False).astype(bool)

    return df


@st.cache_data
def load_votos():
    return pd.read_csv(VOTOS_CSV, encoding="utf-8", dtype=str)


@st.cache_data
def load_textos():
    """csjn_casos_textos.csv (H113): considerando/por_ello/firma completos.

    Graceful: None si no existe. Pesado (~considerandos completos); se carga
    una sola vez cacheado y se consulta por caso en el detalle (cierra el
    pendiente M16 'panel inline del considerando+por_ello completos').
    """
    if not TEXTOS_CSV.exists():
        return None
    return pd.read_csv(TEXTOS_CSV, encoding="utf-8", dtype=str
                       ).set_index("caso_id_canonico")


@st.cache_data
def universo_jueces(df: pd.DataFrame):
    """Conjunto ordenado de jueces conocidos a partir de jueces_conocidos."""
    nombres = set()
    if "jueces_conocidos" in df.columns:
        for celda in df["jueces_conocidos"].dropna():
            for j in str(celda).split("|"):
                j = j.strip()
                if j:
                    nombres.add(j)
    return sorted(nombres)


@st.cache_data
def load_source_file(source_file: str):
    filepath = CORPUS_DIR / source_file
    if not filepath.exists():
        return None
    return filepath.read_text(encoding="utf-8").split("\n")


# -- Helpers de filtro -------------------------------------------------------

def _opts(df: pd.DataFrame, col: str):
    """Valores distintos no nulos de una columna, ordenados."""
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).unique())


def _multiselect(container, df, col, label, key):
    """Multiselect autopoblado; devuelve df filtrado."""
    opts = _opts(df, col)
    if not opts:
        return df
    sel = container.multiselect(label, opts, key=key)
    if sel:
        df = df[df[col].astype(str).isin(sel)]
    return df


def _tri_state(container, df, col, label, truthy, key):
    """Selector Todos / Si / No para columnas booleanas (0/1 o True/False)."""
    if col not in df.columns:
        return df
    choice = container.selectbox(label, ["—", "Sí", "No"], key=key)
    if choice == "Sí":
        return df[df[col].astype(str).isin(truthy)]
    if choice == "No":
        return df[~df[col].astype(str).isin(truthy)]
    return df


def _range_slider(container, df_full, df, col, label, key):
    """Slider de rango sobre una columna numerica. Usa bounds del df completo."""
    if col not in df_full.columns:
        return df
    serie = pd.to_numeric(df_full[col], errors="coerce").dropna()
    if serie.empty:
        return df
    lo, hi = int(serie.min()), int(serie.max())
    if lo >= hi:
        return df
    sel = container.slider(label, lo, hi, (lo, hi), key=key)
    if sel != (lo, hi):
        vals = pd.to_numeric(df[col], errors="coerce")
        df = df[(vals >= sel[0]) & (vals <= sel[1])]
    return df


# -- Sidebar: filtros --------------------------------------------------------

def render_sidebar(df_full: pd.DataFrame):
    df = df_full
    sb = st.sidebar

    sb.header("⚖️ Corpus CSJN v8")
    placeholder_count = sb.empty()

    if sb.button("🧹 Limpiar filtros", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith(FILTER_KEY_PREFIXES):
                del st.session_state[k]
        st.session_state.pop("muestra_ids", None)
        st.rerun()

    # --- Muestreo activo (se setea desde el tab Auditoria) ------------------
    muestra = st.session_state.get("muestra_ids")
    if muestra:
        seed = st.session_state.get("muestra_seed", "?")
        sb.info(f"🎲 Muestra activa: {len(muestra)} casos (seed {seed})")
        if sb.button("Quitar muestra", use_container_width=True):
            st.session_state.pop("muestra_ids", None)
            st.rerun()
        df = df[df["caso_id_canonico"].isin(muestra)]

    # --- Busqueda -----------------------------------------------------------
    with sb.expander("🔎 Búsqueda", expanded=True):
        solo_fallos = st.checkbox("Solo fallos", value=True, key="f_solo_fallos")
        if solo_fallos:
            df = df[df["tipo_entrada"] == "fallo"]

        col_t, col_p = st.columns(2)
        tomo_input = col_t.text_input("Tomo", placeholder="329", key="f_tomo")
        pag_input  = col_p.text_input("Página", placeholder="2024", key="f_pag")

        if tomo_input:
            try:
                df = df[df["tomo"] == int(tomo_input)]
            except ValueError:
                pass
        if pag_input:
            try:
                df = df[df["pagina"] == int(pag_input)]
            except ValueError:
                pass

        busqueda = st.text_input(
            "Texto libre",
            placeholder="carátula, recurrente, firma, tribunal...",
            key="f_busqueda",
        )
        if busqueda:
            q = busqueda.lower()
            campos = ["case_name_indice", "case_name_cuerpo", "jueces",
                      "tribunal_origen", "recurrente", "recurrido",
                      "secuencia_zonas"]
            mask = pd.Series(False, index=df.index)
            for c in campos:
                if c in df.columns:
                    mask |= df[c].astype(str).str.lower().str.contains(
                        q, na=False, regex=False)
            df = df[mask]

    # --- Clasificacion (ejes del parser) -------------------------------------
    with sb.expander("⚖️ Clasificación", expanded=False):
        df = _multiselect(st, df, "tipo_entrada", "Tipo de entrada", "f_tipo_entrada")
        df = _multiselect(st, df, "outcome", "Outcome (eje legacy)", "f_outcome")
        df = _multiselect(st, df, "voting_pattern", "Voting pattern", "f_vp")
        df = _tri_state(st, df, "is_merit_decision",
                        "Decisión sobre el fondo (is_merit = gate, H178)",
                        {"1", "1.0"}, "tri_merit")

    # --- Recurso y admisibilidad (deriver M26/M39) ---------------------------
    with sb.expander("📨 Recurso / admisibilidad (deriver)", expanded=False):
        df = _multiselect(st, df, "disposicion", "Disposición", "f_disp")
        df = _multiselect(st, df, "admisibilidad", "Admisibilidad", "f_adm")
        if st.checkbox("Solo con causal de inadmisibilidad", key="f_inadm_only"):
            if "causa_inadmisibilidad" in df.columns:
                df = df[df["causa_inadmisibilidad"].notna()
                        & (df["causa_inadmisibilidad"].astype(str) != "")]
        df = _multiselect(st, df, "causa_inadmisibilidad",
                          "Causa de inadmisibilidad", "f_inadm")
        df = _multiselect(st, df, "es_revision_fondo",
                          "Revisión de fondo (gate)", "f_revfondo")
        df = _multiselect(st, df, "via_recurso", "Vía del recurso", "f_via")
        df = _multiselect(st, df, "parte_ganadora", "Parte ganadora", "f_ganadora")
        df = _tri_state(st, df, "reenvia", "¿Reenvía?", {"si"}, "tri_reenvia")
        df = _tri_state(st, df, "multi_recurso", "¿Multi-recurso?",
                        {"si"}, "tri_multirec")

    # --- Proceso / jurisdiccion ----------------------------------------------
    with sb.expander("🏛️ Proceso / jurisdicción", expanded=False):
        df = _tri_state(st, df, "es_queja", "¿Es queja?", {"1", "1.0"}, "tri_queja")
        df = _multiselect(st, df, "queja_resultado", "Resultado de queja",
                          "f_queja_res")
        df = _tri_state(st, df, "is_originaria", "Competencia originaria",
                        {"1", "1.0"}, "tri_originaria")
        df = _multiselect(st, df, "tipo_cuestion_federal", "Cuestión federal",
                          "f_cf")
        df = _multiselect(st, df, "apertura_tipo", "Tipo de apertura",
                          "f_apertura")
        df = _multiselect(st, df, "tribunal_origen_status",
                          "Status tribunal de origen", "f_trib_status")

    # --- Materia y partes -----------------------------------------------------
    with sb.expander("📚 Materia y partes", expanded=False):
        df = _multiselect(st, df, "materia", "Materia", "f_materia")
        df = _multiselect(st, df, "materia_capa", "Capa de materia",
                          "f_materia_capa")
        df = _multiselect(st, df, "materia_fuente", "Fuente de materia",
                          "f_materia_fuente")
        df = _multiselect(st, df, "partes_capa", "Capa de partes",
                          "f_partes_capa")
        df = _multiselect(st, df, "recurrente_rol", "Rol del recurrente",
                          "f_rec_rol")
        df = _multiselect(st, df, "recurrido_rol", "Rol del recurrido",
                          "f_reco_rol")
        df = _tri_state(st, df, "multi_recurrente", "¿Multi-recurrente?",
                        {"si", "1", "True"}, "tri_multirecu")

    # --- Panel / decision ------------------------------------------------------
    with sb.expander("👥 Panel / decisión", expanded=False):
        jueces = universo_jueces(df_full)
        if jueces:
            sel_jueces = st.multiselect("Juez interviniente", jueces, key="f_jueces")
            if sel_jueces:
                objetivo = set(sel_jueces)
                def _tiene(celda):
                    if not isinstance(celda, str):
                        return False
                    return bool(objetivo & {x.strip() for x in celda.split("|")})
                df = df[df["jueces_conocidos"].apply(_tiene)]

        df = _tri_state(st, df, "is_full_bench", "Tribunal en pleno",
                        {"1", "1.0"}, "tri_full_bench")
        df = _tri_state(st, df, "dictamen_presente", "Con dictamen",
                        {"True", "1", "1.0"}, "tri_dictamen")

        df = _range_slider(st, df_full, df, "n_jueces", "N° de jueces", "f_njueces")
        df = _range_slider(st, df_full, df, "n_disidencias", "N° de disidencias",
                           "f_ndisid")

    # --- Zonas: wc / segmentos -------------------------------------------------
    with sb.expander("📐 Zonas: wc y segmentos", expanded=False):
        df = _range_slider(st, df_full, df, "word_count", "Word count (total)",
                           "f_wc")

        zonas_wc = st.multiselect(
            "Zonas a filtrar por wc", ZONAS_UNIVERSO, key="f_zonas_wc_sel",
            help="Aparece un slider de rango por cada zona elegida.",
        )
        for zona in zonas_wc:
            df = _range_slider(st, df_full, df, f"wcz_{zona}",
                               f"wc {zona}", f"f_wcz_{zona}")

        zonas_ns = st.multiselect(
            "Zonas a filtrar por n° de segmentos", ZONAS_UNIVERSO,
            key="f_zonas_ns_sel",
        )
        for zona in zonas_ns:
            df = _range_slider(st, df_full, df, f"nseg_{zona}",
                               f"segmentos {zona}", f"f_nsz_{zona}")

        if "pct_cobertura" in df_full.columns:
            cob = st.slider("Cobertura de zonificación (%)", 0, 100, (0, 100),
                            key="f_cobertura")
            if cob != (0, 100):
                vals = df["pct_cobertura"] * 100
                df = df[(vals >= cob[0]) & (vals <= cob[1])]

    # --- Banderas de auditoria ---------------------------------------------------
    with sb.expander("🚩 Banderas de auditoría", expanded=False):
        st.caption("Se combinan con OR. Detalle y conteos en el tab Auditoría.")
        activas = []
        for fcol, (label, _) in FLAGS_DEF.items():
            if fcol in df.columns and st.checkbox(label, key=f"f_{fcol}"):
                activas.append(fcol)
        if activas:
            mask = pd.Series(False, index=df.index)
            for fcol in activas:
                mask |= df[fcol]
            df = df[mask]

    # --- Diagnostico del parser ---------------------------------------------------
    with sb.expander("🩺 Diagnóstico del parser", expanded=False):
        df = _multiselect(st, df, "status_localizacion", "Status localización",
                          "f_status_loc")
        df = _multiselect(st, df, "status_fin", "Status fin", "f_status_fin")
        df = _multiselect(st, df, "pista_fin", "Pista fin", "f_pista_fin")
        df = _multiselect(st, df, "epilogo_status", "Status epílogo (sidecar)",
                          "f_epi_status")

    placeholder_count.caption(
        f"**{len(df):,}** de {len(df_full):,} casos · {df['tomo'].nunique()} tomos"
    )

    return df


# -- Zona toggles (en el detalle) -------------------------------------------

def render_zone_toggles(container):
    """Checkboxes para mostrar/ocultar zonas. Retorna set de zonas visibles."""
    zonas_visibles = set()

    defaults = {
        "residuo_caso_anterior": False,
        "sumario": True,
        "dictamen": True,
        "apertura": True,
        "cuerpo": True,
        "dispositivo": True,
        "firma": True,
        "voto_separado": True,
        "epilogo": True,
        "intersticio": True,
        "header_pagina": False,
    }

    col1, col2 = container.columns(2)
    if col1.button("🔍 Todas", key="zt_todas"):
        for z in defaults:
            st.session_state[f"zona_{z}"] = True
    if col2.button("🎯 Solo fallo", key="zt_fallo"):
        for z in defaults:
            st.session_state[f"zona_{z}"] = z in (
                "apertura", "cuerpo", "dispositivo", "firma", "voto_separado"
            )

    col3, col4, col5 = container.columns(3)
    if col3.button("📎 Epílogo", key="zt_epi"):
        for z in defaults:
            st.session_state[f"zona_{z}"] = z == "epilogo"
    if col4.button("🗑️ Residuo", key="zt_res"):
        for z in defaults:
            st.session_state[f"zona_{z}"] = z == "residuo_caso_anterior"
    if col5.button("✒️ Firma", key="zt_firma"):
        for z in defaults:
            st.session_state[f"zona_{z}"] = z == "firma"

    for zona, default in defaults.items():
        icon, _, fg, label = ZONA_STYLE.get(zona, ("", "", "", zona))
        key = f"zona_{zona}"
        if key not in st.session_state:
            st.session_state[key] = default
        if container.checkbox(f"{icon} {label}" if icon else label,
                              value=st.session_state[key], key=key):
            zonas_visibles.add(zona)

    return zonas_visibles


# -- Vista: tabla ------------------------------------------------------------

# Codigos cortos para la columna de banderas de la tabla
FLAG_CODES = {
    "flag_sin_firma": "F0",
    "flag_sin_dispositivo": "D0",
    "flag_sin_cuerpo": "C0",
    "flag_firma_fragmentada": "Ff",
    "flag_wc_firma_outlier": "Fw",
    "flag_cuerpo_cero": "Cw",
    "flag_epilogo_no_terminal": "Gt",
    "flag_residuo_tardio": "Gr",
    "flag_apertura_multiple": "Ga",
    "flag_sumario_dictamen_tardio": "Gs",
    "flag_firma_antes_dispositivo": "Gf",
    "flag_cobertura_baja": "Cb",
    "flag_wc_epilogo_outlier": "E",
    "flag_wc_residuo_outlier": "R",
}


def render_table(df: pd.DataFrame):
    display_cols = [
        "caso_id_canonico", "tomo", "case_name_indice",
        "voting_pattern", "outcome", "disposicion", "admisibilidad",
        "causa_inadmisibilidad", "es_revision_fondo", "es_queja",
        "n_jueces", "word_count", "wcz_firma", "nseg_firma", "tipo_entrada",
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    df_display = df[display_cols].copy()

    # Columna de banderas: codigos cortos concatenados
    flags_presentes = [f for f in FLAG_CODES if f in df.columns]
    if flags_presentes:
        def _codes(row):
            return " ".join(FLAG_CODES[f] for f in flags_presentes if row[f])
        df_display["🚩"] = df[flags_presentes].apply(_codes, axis=1)

    df_display = df_display.rename(columns={
        "caso_id_canonico": "ID",
        "tomo": "Tomo",
        "case_name_indice": "Caratula",
        "voting_pattern": "Patron",
        "outcome": "Outcome",
        "disposicion": "Disposicion",
        "admisibilidad": "Adm.",
        "causa_inadmisibilidad": "Causa inadm.",
        "es_revision_fondo": "Fondo",
        "es_queja": "Queja",
        "n_jueces": "Jueces",
        "word_count": "WC",
        "wcz_firma": "WCfirma",
        "nseg_firma": "SegF",
        "tipo_entrada": "Tipo",
    })
    if "Caratula" in df_display.columns:
        df_display["Caratula"] = df_display["Caratula"].str[:80]
    return df_display


# -- Vista: resumen ----------------------------------------------------------

def render_resumen(df: pd.DataFrame):
    st.markdown("#### Distribuciones de la selección")
    st.caption(f"{len(df):,} casos filtrados")

    if df.empty:
        st.info("Sin casos en la selección actual.")
        return

    def _barras(col, titulo):
        if col not in df.columns:
            return
        vc = df[col].fillna("(vacío)").value_counts()
        if vc.empty:
            return
        st.markdown(f"**{titulo}**")
        st.bar_chart(vc)

    c1, c2 = st.columns(2)
    with c1:
        _barras("disposicion", "Disposición (deriver)")
        _barras("causa_inadmisibilidad", "Causa de inadmisibilidad")
        _barras("outcome", "Outcome (eje legacy)")
        _barras("materia", "Materia")
        _barras("tipo_cuestion_federal", "Cuestión federal")
    with c2:
        _barras("admisibilidad", "Admisibilidad (gate)")
        _barras("voting_pattern", "Voting pattern")
        _barras("via_recurso", "Vía del recurso")
        _barras("materia_capa", "Capa de materia")
        _barras("parte_ganadora", "Parte ganadora")

    st.markdown("**Casos por tomo**")
    if "tomo" in df.columns:
        por_tomo = df["tomo"].dropna().astype(int).value_counts().sort_index()
        st.bar_chart(por_tomo)

    # Indicadores rapidos
    st.markdown("**Indicadores**")
    cols = st.columns(4)
    total = len(df)
    def _pct(mask):
        n = int(mask.sum())
        return f"{n:,}", (f"{100*n/total:.1f}%" if total else "—")
    if "es_queja" in df.columns:
        v, p = _pct(df["es_queja"].astype(str).isin({"1", "1.0"}))
        cols[0].metric("Quejas", v, p)
    if "is_originaria" in df.columns:
        v, p = _pct(df["is_originaria"].astype(str).isin({"1", "1.0"}))
        cols[1].metric("Originaria", v, p)
    if "is_merit_decision" in df.columns:
        v, p = _pct(df["is_merit_decision"].astype(str).isin({"1", "1.0"}))
        cols[2].metric("Sobre el fondo (gate)", v, p)
    if "admisibilidad" in df.columns:
        v, p = _pct(df["admisibilidad"].astype(str) == "inadmite")
        cols[3].metric("Inadmite", v, p)


# -- Vista: auditoria ---------------------------------------------------------

def render_auditoria(df: pd.DataFrame, df_full: pd.DataFrame):
    """Tab Auditoria (cierra pendiente M16: modo auditoria-de-precision).

    Panel de banderas con conteo y click-para-filtrar + muestreo aleatorio
    reproducible + estado del marcado TP/FP/dudoso.
    """
    st.markdown("#### 🚩 Banderas sobre la selección actual")
    st.caption(
        f"{len(df):,} casos en la selección. Umbrales calibrados sobre el "
        f"corpus (H186): wc firma p95=71, nseg firma 1–3 ≈ 92% de los fallos."
    )

    flags_presentes = [f for f in FLAGS_DEF if f in df.columns]
    if not flags_presentes:
        st.warning("No hay columnas de banderas (¿falta csjn_casos_zonas.csv?).")
        return

    rows = []
    for fcol in flags_presentes:
        label, desc = FLAGS_DEF[fcol]
        n_sel = int(df[fcol].sum())
        n_tot = int(df_full[fcol].sum())
        rows.append((fcol, label, desc, n_sel, n_tot))

    for fcol, label, desc, n_sel, n_tot in rows:
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.markdown(f"**{label}** · {desc}")
        c2.markdown(f"`{n_sel:,}` sel / `{n_tot:,}` corpus")
        if n_sel and c3.button("Filtrar", key=f"aud_{fcol}"):
            st.session_state[f"f_{fcol}"] = True
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🎲 Muestreo aleatorio (adjudicación por lectura)")
    st.caption(
        "Muestra reproducible de la selección actual: mismo seed + misma "
        "selección = misma muestra. La muestra se aplica como filtro global."
    )
    c1, c2, c3 = st.columns([1, 1, 2])
    n_muestra = c1.number_input("N", min_value=1, max_value=500, value=30)
    seed = c2.number_input("Seed", min_value=0, max_value=99999, value=420)
    if c3.button("Muestrear de la selección actual"):
        base = df["caso_id_canonico"].dropna()
        n = min(int(n_muestra), len(base))
        muestra = base.sample(n=n, random_state=int(seed)).tolist()
        st.session_state["muestra_ids"] = muestra
        st.session_state["muestra_seed"] = int(seed)
        st.rerun()

    st.markdown("---")
    st.markdown("#### ✅ Marcado TP / FP / dudoso")
    marcas = st.session_state.get("marcas", {})
    if marcas:
        mdf = pd.DataFrame(
            [{"caso_id_canonico": k, **v} for k, v in marcas.items()]
        )
        vc = mdf["veredicto"].value_counts().to_dict()
        st.caption(
            f"{len(mdf)} casos marcados en esta sesión — " +
            " · ".join(f"{k}: {v}" for k, v in vc.items())
        )
        st.dataframe(mdf, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Descargar marcas (CSV)",
            data=mdf.to_csv(index=False).encode("utf-8"),
            file_name="csjn_marcas_auditoria.csv",
            mime="text/csv",
        )
        if st.button("🗑️ Borrar todas las marcas"):
            st.session_state["marcas"] = {}
            st.rerun()
    else:
        st.caption(
            "Sin marcas aún. Se marca desde el detalle de cada caso "
            "(botonera TP/FP/dudoso). Las marcas viven en la sesión del "
            "navegador: descargá el CSV antes de cerrar."
        )


# -- Vista: detalle ---------------------------------------------------------

def _pintar_flags(caso: pd.Series):
    """Badges de las banderas activas del caso."""
    activos = [FLAGS_DEF[f][0] for f in FLAGS_DEF
               if f in caso.index and bool(caso.get(f))]
    if activos:
        html = "".join(f'<span class="flag-badge">🚩 {a}</span>' for a in activos)
        st.markdown(html, unsafe_allow_html=True)


def _panel_marcado(caso_id: str):
    """Botonera TP/FP/dudoso + nota (tab Auditoria consume las marcas)."""
    marcas = st.session_state.setdefault("marcas", {})
    actual = marcas.get(caso_id, {})
    if actual:
        st.caption(f"Marca actual: **{actual.get('veredicto')}** — "
                   f"{actual.get('nota') or 'sin nota'}")
    nota = st.text_input("Nota", value=actual.get("nota", ""),
                         key=f"nota_{caso_id}")
    c1, c2, c3, c4 = st.columns(4)
    for col, veredicto in ((c1, "TP"), (c2, "FP"), (c3, "dudoso")):
        if col.button(veredicto, key=f"mk_{veredicto}_{caso_id}"):
            marcas[caso_id] = {
                "veredicto": veredicto,
                "nota": nota,
                "ts": datetime.datetime.now().isoformat(timespec="seconds"),
            }
            st.rerun()
    if actual and c4.button("Quitar", key=f"mk_del_{caso_id}"):
        marcas.pop(caso_id, None)
        st.rerun()


def render_detail(caso: pd.Series, votos_df: pd.DataFrame,
                  zonas_df: pd.DataFrame, textos_df):
    caso_id = caso["caso_id_canonico"]

    st.markdown(f"### {caso_id}")
    caratula = caso.get("case_name_indice", "") or caso.get("case_name_cuerpo", "")
    st.caption(caratula)
    _pintar_flags(caso)

    # Linea rapida de campos clave (siempre visible, arriba de los tabs)
    quick = []
    for label, col in (("Patrón", "voting_pattern"), ("Outcome", "outcome"),
                       ("Disp.", "disposicion"), ("Adm.", "admisibilidad"),
                       ("Fondo", "es_revision_fondo"),
                       ("Materia", "materia"), ("Jueces", "n_jueces")):
        v = caso.get(col)
        if pd.notna(v) and v != "":
            quick.append(f"**{label}:** {v}")
    if quick:
        st.markdown(" · ".join(quick))

    caso_zonas = zonas_df[zonas_df["caso_id_canonico"] == caso_id]

    tab_fuente, tab_meta, tab_votos = st.tabs(
        ["📄 Fuente", "🗂️ Metadatos", "🗳️ Votos y zonas"]
    )

    # -- Tab Fuente: bloque .md a ancho completo ------------------------------
    with tab_fuente:
        c_tog, c_mark = st.columns([2, 1])
        with c_tog.expander("⚙️ Zonas visibles", expanded=False):
            zonas_visibles = render_zone_toggles(st)
        with c_mark.expander("✅ Marcar caso (auditoría)", expanded=False):
            _panel_marcado(caso_id)

        source_file = caso.get("source_file", "")
        linea_inicio = caso.get("linea_inicio")
        linea_fin_real = caso.get("linea_fin_real")

        if pd.isna(linea_inicio) or pd.isna(linea_fin_real) or not source_file:
            st.warning("Sin datos de localizacion para este caso.")
        else:
            lines = load_source_file(source_file)
            if lines is None:
                st.error(f"Archivo no encontrado: {CORPUS_DIR / source_file}")
            else:
                li = int(linea_inicio)
                lf = int(linea_fin_real)
                block = lines[li:lf + 1]

                if not block:
                    st.warning("Bloque vacio.")
                else:
                    # Mapa linea_relativa -> zona desde zonas CSV
                    zona_por_linea = {}
                    for _, seg in caso_zonas.iterrows():
                        z = seg["zona"]
                        for k in range(int(seg["linea_ini"]),
                                       int(seg["linea_fin"]) + 1):
                            zona_por_linea[k] = z

                    # Leyenda (solo zonas presentes en este caso)
                    zonas_presentes = set(zona_por_linea.values())
                    leyenda_html = '<div class="leyenda">'
                    for zona in ZONA_STYLE:
                        if zona not in zonas_presentes:
                            continue
                        icon, bg, fg, label = ZONA_STYLE[zona]
                        leyenda_html += (
                            f'<span class="z-{zona}" style="opacity: '
                            f'{"1" if zona in zonas_visibles else "0.3"}">'
                            f'{icon} {label}</span>'
                        )
                    leyenda_html += '</div>'
                    st.markdown(leyenda_html, unsafe_allow_html=True)

                    html_lines = []
                    prev_zona = None
                    for i, line in enumerate(block):
                        abs_num = li + i
                        zona = zona_por_linea.get(i, "intersticio")
                        visible = zona in zonas_visibles
                        cls = f"z-{zona}" if visible else "z-hidden"

                        if (zona != prev_zona and visible
                                and zona not in ("header_pagina",)):
                            icon, _, _, label = ZONA_STYLE.get(
                                zona, ("", "", "", zona))
                            html_lines.append(
                                f'<div class="section-sep">{icon} {label}</div>'
                            )

                        escaped = (
                            line.rstrip("\n\r")
                            .replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                        )
                        html_lines.append(
                            f'<div class="source-line {cls}">'
                            f'<span class="line-num">{abs_num}</span>{escaped}'
                            f'</div>'
                        )
                        if zona not in ("header_pagina",):
                            prev_zona = zona

                    html = f'<div class="source-block">{"".join(html_lines)}</div>'
                    st.markdown(html, unsafe_allow_html=True)

    # -- Tab Metadatos ----------------------------------------------------------
    with tab_meta:
        col_a, col_b = st.columns(2)

        with col_a:
            vp = caso.get("voting_pattern", "")
            vp_class = f"vp-{vp}" if vp else ""
            st.markdown(
                f'Patron: <span class="vp-badge {vp_class}">{vp}</span>',
                unsafe_allow_html=True,
            )
            inadm = caso.get("causa_inadmisibilidad", "")
            if pd.notna(inadm) and inadm:
                st.markdown(
                    f'Inadmisibilidad: <span class="inadm-badge">{inadm}</span>',
                    unsafe_allow_html=True,
                )

            st.markdown("**Caso**")
            for label, col in (
                ("Tomo", "tomo"), ("Pagina", "pagina"), ("Fecha", "date"),
                ("Tipo", "tipo_entrada"), ("Apertura", "apertura_tipo"),
                ("Outcome (legacy)", "outcome"),
                ("Cuestion federal", "tipo_cuestion_federal"),
                ("Es queja", "es_queja"), ("Resultado queja", "queja_resultado"),
                ("Originaria", "is_originaria"), ("Pleno", "is_full_bench"),
                ("Sobre el fondo (gate)", "is_merit_decision"),
                ("Dictamen", "dictamen_presente"),
                ("Tribunal origen", "tribunal_origen"),
                ("Status trib. origen", "tribunal_origen_status"),
            ):
                v = caso.get(col)
                if pd.notna(v) and v != "":
                    st.markdown(f"**{label}:** {v}")

            st.markdown("**Recurso (deriver)**")
            for label, col in (
                ("Disposicion", "disposicion"), ("Admisibilidad", "admisibilidad"),
                ("Causa inadm.", "causa_inadmisibilidad"),
                ("Revision de fondo", "es_revision_fondo"),
                ("Via", "via_recurso"), ("Reenvia", "reenvia"),
                ("Parte ganadora", "parte_ganadora"),
                ("Multi-recurso", "multi_recurso"),
            ):
                v = caso.get(col)
                if pd.notna(v) and v != "":
                    st.markdown(f"**{label}:** {v}")

        with col_b:
            st.markdown("**Partes / materia (deriver)**")
            for label, col in (
                ("Recurrente", "recurrente"), ("Rol recurrente", "recurrente_rol"),
                ("Recurrido", "recurrido"), ("Rol recurrido", "recurrido_rol"),
                ("Multi-recurrente", "multi_recurrente"),
                ("Capa partes", "partes_capa"), ("Fuente partes", "partes_fuente"),
                ("Materia", "materia"), ("Capa materia", "materia_capa"),
                ("Fuente materia", "materia_fuente"),
                ("Status epilogo", "epilogo_status"),
            ):
                v = caso.get(col)
                if pd.notna(v) and v != "":
                    st.markdown(f"**{label}:** {v}")

            st.markdown("**Metricas y diagnostico**")
            for label, col in (
                ("Word count", "word_count"), ("WC mayoria", "wc_mayoria"),
                ("WC votos", "wc_votos"), ("WC considerando", "wc_considerando"),
                ("WC dictamen", "wc_dictamen"),
                ("Cobertura zonif.", "pct_cobertura"),
                ("Jueces", "n_jueces"), ("Titulares", "n_titulares"),
                ("Disidencias", "n_disidencias"),
                ("Segun su voto", "n_votos_svoto"),
                ("Status loc.", "status_localizacion"),
                ("Status fin", "status_fin"), ("Pista fin", "pista_fin"),
                ("Archivo", "source_file"),
            ):
                v = caso.get(col)
                if pd.notna(v) and v != "":
                    if col == "pct_cobertura":
                        v = f"{float(v)*100:.1f}%"
                    st.markdown(f"**{label}:** {v}")
            st.markdown(
                f'**Lineas:** {caso.get("linea_inicio")}–'
                f'{caso.get("linea_fin_real")}'
            )
            sec = caso.get("secuencia_zonas")
            if pd.notna(sec) and sec:
                st.markdown("**Secuencia de zonas:**")
                st.code(str(sec), language=None)

        # Panel inline de textos completos (pendiente M16, split H113)
        if textos_df is not None and caso_id in textos_df.index:
            trow = textos_df.loc[caso_id]
            st.markdown("---")
            for label, col in (("Considerando (completo)", "considerando_text"),
                               ("Dispositivo — por ello (completo)",
                                "por_ello_text"),
                               ("Firma (raw)", "firma_raw")):
                v = trow.get(col)
                if pd.notna(v) and v:
                    with st.expander(f"📃 {label} — {len(str(v)):,} chars",
                                     expanded=False):
                        st.text(str(v))

    # -- Tab Votos y zonas --------------------------------------------------------
    with tab_votos:
        col_v, col_z = st.columns(2)

        with col_v:
            st.markdown("**Votos**")
            caso_votos = votos_df[votos_df["caso_id_canonico"] == caso_id]
            if not caso_votos.empty:
                for _, v in caso_votos.iterrows():
                    juez = v.get("juez", "?")
                    posicion = v.get("posicion", "?")
                    tipo_sep = v.get("tipo_voto_sep", "")
                    extra = (f" ({tipo_sep})"
                             if pd.notna(tipo_sep) and tipo_sep else "")
                    st.markdown(f"- {juez}: **{posicion}**{extra}")
            else:
                st.caption("Sin votos individuales registrados")

        with col_z:
            st.markdown("**Zonas (resumen)**")
            if not caso_zonas.empty:
                zona_summary = caso_zonas.groupby("zona").agg(
                    segs=("segmento", "count"),
                    wc=("wc", "sum"),
                    lineas=("n_lineas", "sum"),
                ).sort_values("wc", ascending=False)
                for zona, row in zona_summary.iterrows():
                    icon = ZONA_STYLE.get(zona, ("", "", "", zona))[0]
                    fg = ZONA_STYLE.get(zona, ("", "", "", zona))[2]
                    st.markdown(
                        f'<span style="color:{fg}">{icon} {zona}: '
                        f'{int(row["segs"])} seg, {int(row["wc"])} wc, '
                        f'{int(row["lineas"])} lin</span>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Sin zonas registradas para este caso.")

        st.markdown("**Segmentos (orden por linea)**")
        if not caso_zonas.empty:
            segs = caso_zonas.sort_values("linea_ini")[
                ["zona", "segmento", "linea_ini", "linea_fin", "n_lineas", "wc"]
            ]
            st.dataframe(segs, use_container_width=True, hide_index=True)



# -- Exportes: casos crudos y reporte de auditoria ---------------------------

def _bloque_crudo(caso: pd.Series) -> str:
    """Texto crudo del caso con encabezado de metadatos.

    Anclaje canonico: source_file + linea_inicio/linea_fin_real del CSV —
    el mismo que extraer_caso.py v2.0 (leccion B102: nunca resolver el
    volumen por glob). No recomputa nada del parser (leccion H045).
    """
    sf = caso.get("source_file", "")
    li, lf = caso.get("linea_inicio"), caso.get("linea_fin_real")
    header = [f"# {caso['caso_id_canonico']}"]
    car = caso.get("case_name_indice") or caso.get("case_name_cuerpo") or ""
    if pd.notna(car) and car:
        header.append(f"Caratula: {car}")
    meta = []
    for lbl, col in (("outcome", "outcome"), ("disposicion", "disposicion"),
                     ("adm", "admisibilidad"), ("fondo", "es_revision_fondo"),
                     ("patron", "voting_pattern"), ("materia", "materia")):
        v = caso.get(col)
        if pd.notna(v) and v != "":
            meta.append(f"{lbl}={v}")
    if meta:
        header.append(" · ".join(meta))
    flags = [FLAGS_DEF[f][0] for f in FLAGS_DEF
             if f in caso.index and bool(caso.get(f))]
    if flags:
        header.append("Banderas: " + " | ".join(flags))
    sec = caso.get("secuencia_zonas")
    if pd.notna(sec) and sec:
        header.append(f"Secuencia: {sec}")
    header.append(f"Fuente: {sf} · lineas {li}\u2013{lf}")
    head = "\n".join(header)

    if pd.isna(li) or pd.isna(lf) or not sf:
        return head + "\n\n[SIN LOCALIZACION]\n"
    lines = load_source_file(sf)
    if lines is None:
        return head + "\n\n[ARCHIVO NO ENCONTRADO: " + str(sf) + "]\n"
    body = "\n".join(lines[int(li):int(lf) + 1])
    return head + "\n\n```\n" + body + "\n```\n"


def _filtros_activos() -> list:
    """Snapshot de los widgets de filtro con valor. Nota: los sliders en
    rango completo aparecen pero no filtran."""
    out = []
    for k in sorted(st.session_state.keys()):
        if not k.startswith(FILTER_KEY_PREFIXES):
            continue
        v = st.session_state[k]
        if v in (None, "", False, "\u2014") or v == []:
            continue
        out.append(f"- `{k}` = {v}")
    return out


def _generar_reporte(filtered: pd.DataFrame, seleccion: list) -> str:
    """Reporte de auditoria .md: filtros, conteos, banderas, muestra,
    marcas de la sesion y bloques crudos de los casos tickeados.
    Pensado como insumo directo de la sesion H siguiente."""
    hoy = datetime.date.today().isoformat()
    L = [f"# Reporte de auditoria — explorador v8 ({hoy})", ""]

    L.append(f"**Seleccion:** {len(filtered):,} casos filtrados.")
    muestra = st.session_state.get("muestra_ids")
    if muestra:
        L.append(f"**Muestra activa:** {len(muestra)} casos, "
                 f"seed {st.session_state.get('muestra_seed', '?')} "
                 f"(reproducible sobre la misma seleccion).")
    L.append("")

    fa = _filtros_activos()
    L.append("## Filtros activos")
    L.extend(fa if fa else ["- (ninguno)"])
    L.append("")

    L.append("## Banderas sobre la seleccion")
    for fcol, (label, _) in FLAGS_DEF.items():
        if fcol in filtered.columns:
            n = int(filtered[fcol].sum())
            if n:
                L.append(f"- {label}: **{n:,}**")
    L.append("")

    marcas = st.session_state.get("marcas", {})
    L.append(f"## Marcas de la sesion ({len(marcas)})")
    for cid, m in marcas.items():
        nota = m.get("nota") or ""
        L.append(f"- `{cid}` — **{m.get('veredicto')}**"
                 + (f": {nota}" if nota else ""))
    if not marcas:
        L.append("- (sin marcas)")
    L.append("")

    if seleccion:
        L.append(f"## Casos crudos seleccionados ({len(seleccion)})")
        L.append("")
        for caso in seleccion:
            L.append(_bloque_crudo(caso))
            L.append("\n---\n")
    return "\n".join(L)


# -- Main --------------------------------------------------------------------

def main():
    if not CASOS_CSV.exists():
        st.error(f"No se encontro: {CASOS_CSV}")
        st.info(
            "Ejecuta el visor desde la raiz del repo:\n\n"
            "```\ncd corpus-csjn\n"
            "streamlit run scripts/explorador/exploradorv8.py\n```"
        )
        return

    df = load_casos()
    votos_df = load_votos()
    zonas_df = load_zonas()
    textos_df = load_textos()

    filtered = render_sidebar(df)

    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = None

    if st.session_state.selected_idx is not None:
        idx = st.session_state.selected_idx
        indices = filtered.index.tolist()

        if idx not in indices:
            st.session_state.selected_idx = None
            st.rerun()
            return

        pos = indices.index(idx)

        nav_cols = st.columns([1, 1, 1, 4])
        with nav_cols[0]:
            if st.button("← Volver"):
                st.session_state.selected_idx = None
                st.rerun()
        with nav_cols[1]:
            if pos > 0 and st.button("◀ Anterior"):
                st.session_state.selected_idx = indices[pos - 1]
                st.rerun()
        with nav_cols[2]:
            if pos < len(indices) - 1 and st.button("Siguiente ▶"):
                st.session_state.selected_idx = indices[pos + 1]
                st.rerun()
        with nav_cols[3]:
            st.caption(f"Caso {pos + 1} de {len(indices)}")

        st.markdown("---")
        render_detail(filtered.loc[idx], votos_df, zonas_df, textos_df)
        return

    st.title("⚖️ Explorador del Corpus CSJN v8")

    tab_tabla, tab_resumen, tab_audit = st.tabs(
        ["📋 Tabla", "📊 Resumen", "🚩 Auditoría"]
    )

    with tab_tabla:
        df_display = render_table(filtered)

        st.download_button(
            "⬇️ Descargar selección (CSV)",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="csjn_seleccion.csv",
            mime="text/csv",
        )

        page_size = 50
        n_pages = max(1, (len(df_display) + page_size - 1) // page_size)
        page = st.number_input(
            "Pagina", min_value=1, max_value=n_pages, value=1, step=1
        )
        start = (page - 1) * page_size
        end = start + page_size

        st.caption(
            f"Pagina {page}/{n_pages} · "
            f"Filas {start + 1}–{min(end, len(df_display))} de {len(df_display)} · "
            f"🚩 codigos: F0 sin firma · D0 sin dispositivo · C0 sin cuerpo · "
            f"Ff firma fragm. · Fw firma wc · Cw cuerpo wc0 · G* gramatica · "
            f"Cb cobertura · E epilogo · R residuo"
        )

        page_df = df_display.iloc[start:end]
        page_indices = filtered.index[start:end]

        event = st.dataframe(
            page_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="multi-row",
        )

        # Los ticks SELECCIONAN (no abren): multi-seleccion para acciones.
        # La seleccion es por pagina (solo filas visibles).
        sel_rows = (event.selection.rows
                    if event and event.selection else [])
        sel_indices = [page_indices[r] for r in sel_rows
                       if r < len(page_indices)]
        sel_casos = [filtered.loc[i] for i in sel_indices]

        c_open, c_crudos, c_rep, c_info = st.columns([1, 1.3, 1.3, 2.4])
        if c_open.button("🔍 Abrir caso",
                         disabled=len(sel_indices) != 1,
                         help="Habilitado con exactamente 1 caso tickeado"):
            st.session_state.selected_idx = sel_indices[0]
            st.rerun()
        if sel_casos:
            crudos = "\n\n---\n\n".join(_bloque_crudo(c) for c in sel_casos)
            c_crudos.download_button(
                f"⬇️ Crudos ({len(sel_casos)}) .md",
                data=crudos.encode("utf-8"),
                file_name="csjn_casos_crudos.md",
                mime="text/markdown",
            )
        c_rep.download_button(
            "📋 Reporte auditoría .md",
            data=_generar_reporte(filtered, sel_casos).encode("utf-8"),
            file_name="csjn_reporte_auditoria.md",
            mime="text/markdown",
            help="Filtros + banderas + muestra + marcas + crudos tickeados",
        )
        c_info.caption(
            f"{len(sel_indices)} tickeados · los ticks seleccionan; "
            f"«Abrir caso» entra al detalle con 1 tickeado"
        )

    with tab_resumen:
        render_resumen(filtered)

    with tab_audit:
        render_auditoria(filtered, df)


if __name__ == "__main__":
    main()
