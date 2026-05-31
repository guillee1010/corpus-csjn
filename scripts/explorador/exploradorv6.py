"""
Visor del Corpus CSJN v6 — Explorador con zonas del parser
===========================================================
Streamlit app para explorar los fallos parseados del corpus CSJN.

Cambios v6 respecto de v5:
  - Filtros nuevos: causa_inadmisibilidad, es_queja / queja_resultado,
    tipo_cuestion_federal, apertura_tipo, tribunal_origen_status,
    is_originaria / is_full_bench / is_merit_decision / dictamen_presente,
    filtro por juez, y rangos numericos (n_jueces, n_disidencias, word_count).
  - Sidebar reorganizado en grupos colapsables (expanders) + contador de
    seleccion y boton "limpiar filtros".
  - Vista principal con tabs: Tabla / Resumen (distribuciones de la seleccion).
  - Descarga del subconjunto filtrado a CSV.
  - Toggles de zonas movidos al panel de fuente del detalle (donde aplican).

Todos los filtros categoricos se autopoblan del CSV (sin listas hardcodeadas),
de modo que el explorador sigue funcionando si cambian los valores del parser.

Uso:
    cd corpus-csjn
    streamlit run scripts/explorador/exploradorv6.py
"""

import re
import streamlit as st
import pandas as pd
from pathlib import Path

# -- Config ------------------------------------------------------------------

st.set_page_config(
    page_title="Corpus CSJN — Explorador v6",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ROOT  = Path.cwd()
CASOS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
VOTOS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos_votos.csv"
ZONAS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos_zonas.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# Prefijos de claves de widgets de filtro (para "limpiar filtros")
FILTER_KEY_PREFIXES = ("f_", "tri_")

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
    max-height: 75vh;
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
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# -- Carga de datos ----------------------------------------------------------

@st.cache_data
def load_casos():
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    for col in ["tomo", "linea_inicio", "linea_fin", "linea_fin_real",
                 "n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
                 "word_count", "wc_mayoria", "wc_votos", "wc_considerando",
                 "wc_dictamen"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["pagina"] = df["caso_id_canonico"].str.extract(r"_p(\d+)$").astype(float)
    return df


@st.cache_data
def load_votos():
    return pd.read_csv(VOTOS_CSV, encoding="utf-8", dtype=str)


@st.cache_data
def load_zonas():
    df = pd.read_csv(ZONAS_CSV, encoding="utf-8", dtype=str)
    for col in ["linea_ini", "linea_fin", "n_lineas", "wc"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def compute_zona_wc(zonas_df):
    """Calcula wc por zona para cada caso (para outlier indicators)."""
    agg = zonas_df.groupby(["caso_id_canonico", "zona"])["wc"].sum().unstack(fill_value=0)
    result = pd.DataFrame(index=agg.index)
    result["wc_epilogo"] = agg.get("epilogo", 0)
    result["wc_residuo"] = agg.get("residuo_caso_anterior", 0)
    return result


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

    sb.header("⚖️ Corpus CSJN v6")
    placeholder_count = sb.empty()

    if sb.button("🧹 Limpiar filtros", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith(FILTER_KEY_PREFIXES):
                del st.session_state[k]
        st.rerun()

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
            placeholder="carátula, dispositivo, firma, considerando...",
            key="f_busqueda",
        )
        if busqueda:
            q = busqueda.lower()
            campos = ["case_name_indice", "case_name_cuerpo", "por_ello_text",
                      "considerando_text", "firma_raw", "jueces"]
            mask = pd.Series(False, index=df.index)
            for c in campos:
                if c in df.columns:
                    mask |= df[c].str.lower().str.contains(q, na=False, regex=False)
            df = df[mask]

    # --- Clasificacion ------------------------------------------------------
    with sb.expander("⚖️ Clasificación", expanded=True):
        df = _multiselect(st, df, "tipo_entrada", "Tipo de entrada", "f_tipo_entrada")
        df = _multiselect(st, df, "outcome", "Outcome", "f_outcome")
        df = _multiselect(st, df, "voting_pattern", "Voting pattern", "f_vp")

        if st.checkbox("Solo con causal de inadmisibilidad", key="f_inadm_only"):
            df = df[df["causa_inadmisibilidad"].notna()
                    & (df["causa_inadmisibilidad"].astype(str) != "")]
        df = _multiselect(st, df, "causa_inadmisibilidad",
                          "Causa de inadmisibilidad", "f_inadm")

    # --- Proceso / jurisdiccion --------------------------------------------
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

    # --- Panel / decision ---------------------------------------------------
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
        df = _tri_state(st, df, "is_merit_decision", "Decisión sobre el fondo",
                        {"1", "1.0"}, "tri_merit")
        df = _tri_state(st, df, "dictamen_presente", "Con dictamen",
                        {"True", "1", "1.0"}, "tri_dictamen")

        df = _range_slider(st, df_full, df, "n_jueces", "N° de jueces", "f_njueces")
        df = _range_slider(st, df_full, df, "n_disidencias", "N° de disidencias",
                           "f_ndisid")

    # --- Metricas / calidad -------------------------------------------------
    with sb.expander("📐 Métricas / calidad", expanded=False):
        df = _range_slider(st, df_full, df, "word_count", "Word count",
                           "f_wc")

        outlier_epi = st.checkbox("⚠ Epílogo > 500 wc", key="f_out_epi")
        outlier_res = st.checkbox("⚠ Residuo > 300 wc", key="f_out_res")
        if outlier_epi or outlier_res:
            zona_wc = compute_zona_wc(load_zonas())
            df = df.join(zona_wc, on="caso_id_canonico", rsuffix="_z")
            if outlier_epi:
                df = df[df.get("wc_epilogo", pd.Series(0)) > 500]
            if outlier_res:
                df = df[df.get("wc_residuo", pd.Series(0)) > 300]

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

def render_table(df: pd.DataFrame):
    display_cols = [
        "caso_id_canonico", "tomo", "case_name_indice",
        "voting_pattern", "outcome", "causa_inadmisibilidad",
        "es_queja", "tipo_cuestion_federal",
        "n_jueces", "word_count", "tipo_entrada",
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    df_display = df[display_cols].copy()

    zona_wc = compute_zona_wc(load_zonas())
    df_display = df_display.join(zona_wc, on="caso_id_canonico")
    df_display["wc_epilogo"] = df_display["wc_epilogo"].fillna(0).astype(int)
    df_display["wc_residuo"] = df_display["wc_residuo"].fillna(0).astype(int)

    df_display["⚠"] = ""
    df_display.loc[df_display["wc_epilogo"] > 500, "⚠"] += "E"
    df_display.loc[df_display["wc_residuo"] > 300, "⚠"] += "R"

    df_display = df_display.rename(columns={
        "caso_id_canonico": "ID",
        "tomo": "Tomo",
        "case_name_indice": "Caratula",
        "voting_pattern": "Patron",
        "outcome": "Resultado",
        "causa_inadmisibilidad": "Inadm.",
        "es_queja": "Queja",
        "tipo_cuestion_federal": "C.Federal",
        "n_jueces": "Jueces",
        "word_count": "WC",
        "tipo_entrada": "Tipo",
        "wc_epilogo": "Epi",
        "wc_residuo": "Res",
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
        _barras("outcome", "Outcome")
        _barras("causa_inadmisibilidad", "Causa de inadmisibilidad")
        _barras("tipo_cuestion_federal", "Cuestión federal")
    with c2:
        _barras("voting_pattern", "Voting pattern")
        _barras("queja_resultado", "Resultado de queja")
        _barras("apertura_tipo", "Tipo de apertura")

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
        cols[2].metric("Sobre el fondo", v, p)
    if "causa_inadmisibilidad" in df.columns:
        v, p = _pct(df["causa_inadmisibilidad"].notna()
                    & (df["causa_inadmisibilidad"].astype(str) != ""))
        cols[3].metric("Con causal inadm.", v, p)


# -- Vista: detalle ---------------------------------------------------------

def render_detail(caso: pd.Series, votos_df: pd.DataFrame, zonas_df: pd.DataFrame):
    caso_id = caso["caso_id_canonico"]

    st.markdown(f"### {caso_id}")
    caratula = caso.get("case_name_indice", "") or caso.get("case_name_cuerpo", "")
    st.caption(caratula)

    caso_zonas = zonas_df[zonas_df["caso_id_canonico"] == caso_id]

    col_meta, col_source = st.columns([1, 2])

    # -- Panel izquierdo: metadatos --
    with col_meta:
        st.markdown("**Datos del caso**")

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

        info_pairs = [
            ("Tomo", caso.get("tomo")),
            ("Pagina", caso.get("pagina")),
            ("Fecha", caso.get("date")),
            ("Resultado", caso.get("outcome")),
            ("Cuestion federal", caso.get("tipo_cuestion_federal")),
            ("Es queja", caso.get("es_queja")),
            ("Resultado queja", caso.get("queja_resultado")),
            ("Originaria", caso.get("is_originaria")),
            ("Pleno", caso.get("is_full_bench")),
            ("Sobre el fondo", caso.get("is_merit_decision")),
            ("Jueces", caso.get("n_jueces")),
            ("Titulares", caso.get("n_titulares")),
            ("Disidencias", caso.get("n_disidencias")),
            ("Segun su voto", caso.get("n_votos_svoto")),
            ("Dictamen", caso.get("dictamen_presente")),
            ("Tribunal origen", caso.get("tribunal_origen")),
            ("Tipo", caso.get("tipo_entrada")),
            ("Word count", caso.get("word_count")),
            ("WC mayoria", caso.get("wc_mayoria")),
            ("WC votos", caso.get("wc_votos")),
            ("WC considerando", caso.get("wc_considerando")),
            ("WC dictamen", caso.get("wc_dictamen")),
            ("Status loc.", caso.get("status_localizacion")),
            ("Status fin", caso.get("status_fin")),
            ("Pista fin", caso.get("pista_fin")),
            ("Archivo", caso.get("source_file")),
            ("Lineas", f'{caso.get("linea_inicio")}–{caso.get("linea_fin_real")}'),
        ]
        for label, val in info_pairs:
            if pd.notna(val) and val != "":
                st.markdown(f"**{label}:** {val}")

        # Zonas del caso (resumen)
        if not caso_zonas.empty:
            st.markdown("---")
            st.markdown("**Zonas**")
            zona_summary = caso_zonas.groupby("zona").agg(
                segs=("segmento", "count"),
                wc=("wc", "sum"),
            ).sort_values("wc", ascending=False)
            for zona, row in zona_summary.iterrows():
                icon = ZONA_STYLE.get(zona, ("", "", "", zona))[0]
                fg = ZONA_STYLE.get(zona, ("", "", "", zona))[2]
                st.markdown(
                    f'<span style="color:{fg}">{icon} {zona}: '
                    f'{int(row["segs"])} seg, {int(row["wc"])} wc</span>',
                    unsafe_allow_html=True,
                )

        # Votos
        st.markdown("---")
        st.markdown("**Votos**")
        caso_votos = votos_df[votos_df["caso_id_canonico"] == caso_id]
        if not caso_votos.empty:
            for _, v in caso_votos.iterrows():
                juez = v.get("juez", "?")
                posicion = v.get("posicion", "?")
                tipo_sep = v.get("tipo_voto_sep", "")
                extra = f" ({tipo_sep})" if pd.notna(tipo_sep) and tipo_sep else ""
                st.markdown(f"- {juez}: **{posicion}**{extra}")
        else:
            st.caption("Sin votos individuales registrados")

        # Dispositivo
        por_ello = caso.get("por_ello_text", "")
        if pd.notna(por_ello) and por_ello:
            st.markdown("---")
            st.markdown("**Dispositivo**")
            txt = str(por_ello)
            st.text(txt[:500] + "..." if len(txt) > 500 else txt)

        # Firma
        firma = caso.get("firma_raw", "")
        if pd.notna(firma) and firma:
            st.markdown("---")
            st.markdown("**Firma**")
            st.text(str(firma))

    # -- Panel derecho: bloque fuente con zonas del parser --
    with col_source:
        st.markdown("**Bloque fuente (.md) — zonas del parser**")

        with st.expander("⚙️ Zonas visibles", expanded=False):
            zonas_visibles = render_zone_toggles(st)

        source_file = caso.get("source_file", "")
        linea_inicio = caso.get("linea_inicio")
        linea_fin_real = caso.get("linea_fin_real")

        if pd.isna(linea_inicio) or pd.isna(linea_fin_real) or not source_file:
            st.warning("Sin datos de localizacion para este caso.")
            return

        lines = load_source_file(source_file)
        if lines is None:
            st.error(f"Archivo no encontrado: {CORPUS_DIR / source_file}")
            return

        li = int(linea_inicio)
        lf = int(linea_fin_real)
        block = lines[li:lf + 1]

        if not block:
            st.warning("Bloque vacio.")
            return

        # Mapa linea_relativa -> zona desde zonas CSV
        zona_por_linea = {}
        for _, seg in caso_zonas.iterrows():
            z = seg["zona"]
            for k in range(int(seg["linea_ini"]), int(seg["linea_fin"]) + 1):
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

        # Renderizar bloque
        html_lines = []
        prev_zona = None

        for i, line in enumerate(block):
            abs_num = li + i
            zona = zona_por_linea.get(i, "intersticio")

            visible = zona in zonas_visibles
            cls = f"z-{zona}" if visible else "z-hidden"

            if (zona != prev_zona and visible
                    and zona not in ("header_pagina",)):
                icon, _, _, label = ZONA_STYLE.get(zona, ("", "", "", zona))
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


# -- Main --------------------------------------------------------------------

def main():
    if not CASOS_CSV.exists():
        st.error(f"No se encontro: {CASOS_CSV}")
        st.info(
            "Ejecuta el visor desde la raiz del repo:\n\n"
            "```\ncd corpus-csjn\n"
            "streamlit run scripts/explorador/exploradorv6.py\n```"
        )
        return

    df = load_casos()
    votos_df = load_votos()
    zonas_df = load_zonas()

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
        render_detail(filtered.loc[idx], votos_df, zonas_df)
        return

    st.title("⚖️ Explorador del Corpus CSJN v6")

    tab_tabla, tab_resumen = st.tabs(["📋 Tabla", "📊 Resumen"])

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
            f"Filas {start + 1}–{min(end, len(df_display))} de {len(df_display)}"
        )

        page_df = df_display.iloc[start:end]
        page_indices = filtered.index[start:end]

        event = st.dataframe(
            page_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        if event and event.selection and event.selection.rows:
            selected_row = event.selection.rows[0]
            if selected_row < len(page_indices):
                st.session_state.selected_idx = page_indices[selected_row]
                st.rerun()

    with tab_resumen:
        render_resumen(filtered)


if __name__ == "__main__":
    main()
