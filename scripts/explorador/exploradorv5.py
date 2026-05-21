"""
Visor del Corpus CSJN v4 — Explorador con zonas del parser
===========================================================
Streamlit app para explorar los fallos parseados del corpus CSJN.
Usa las zonas reales del parser (csjn_casos_zonas.csv) para colorear
el bloque fuente, en vez de reimplementar la deteccion de secciones.

Uso:
    cd corpus-csjn
    streamlit run scripts/explorador/exploradorv4.py
"""

import re
import streamlit as st
import pandas as pd
from pathlib import Path

# -- Config ------------------------------------------------------------------

st.set_page_config(
    page_title="Corpus CSJN — Explorador v4",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ROOT  = Path.cwd()
CASOS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
VOTOS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos_votos.csv"
ZONAS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos_zonas.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

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
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# -- Carga de datos ----------------------------------------------------------

@st.cache_data
def load_casos():
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    for col in ["tomo", "linea_inicio", "linea_fin", "linea_fin_real",
                 "n_jueces", "n_votos_svoto", "n_disidencias", "word_count",
                 "wc_mayoria", "wc_votos", "wc_dictamen"]:
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
def load_source_file(source_file: str):
    filepath = CORPUS_DIR / source_file
    if not filepath.exists():
        return None
    return filepath.read_text(encoding="utf-8").split("\n")


# -- Sidebar: filtros --------------------------------------------------------

def render_sidebar(df: pd.DataFrame):
    st.sidebar.header("⚖️ Corpus CSJN v4")
    st.sidebar.caption(f"{len(df):,} casos · {df['tomo'].nunique()} tomos")

    solo_fallos = st.sidebar.checkbox("Solo fallos", value=True)
    if solo_fallos:
        df = df[df["tipo_entrada"] == "fallo"]

    st.sidebar.markdown("---")
    st.sidebar.subheader("Buscar caso")

    col_t, col_p = st.sidebar.columns(2)
    with col_t:
        tomo_input = st.text_input("Tomo", placeholder="ej: 329")
    with col_p:
        pag_input = st.text_input("Pagina", placeholder="ej: 2024")

    if tomo_input:
        try:
            tomo_num = int(tomo_input)
            df = df[df["tomo"] == tomo_num]
        except ValueError:
            pass

    if pag_input:
        try:
            pag_num = int(pag_input)
            df = df[df["pagina"] == pag_num]
        except ValueError:
            pass

    busqueda = st.sidebar.text_input(
        "🔎 Texto libre",
        placeholder="busca en caratula, dispositivo, firma...",
    )
    if busqueda:
        busq_lower = busqueda.lower()
        mask = (
            df["case_name_indice"].str.lower().str.contains(busq_lower, na=False)
            | df["case_name_cuerpo"].str.lower().str.contains(busq_lower, na=False)
            | df["por_ello_text"].str.lower().str.contains(busq_lower, na=False)
            | df["firma_raw"].str.lower().str.contains(busq_lower, na=False)
            | df["jueces"].str.lower().str.contains(busq_lower, na=False)
        )
        df = df[mask]

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros")

    vp_options = sorted(df["voting_pattern"].dropna().unique())
    vp_sel = st.sidebar.multiselect("Voting pattern", vp_options)
    if vp_sel:
        df = df[df["voting_pattern"].isin(vp_sel)]

    sin_firma = st.sidebar.checkbox("Solo sin firma")
    if sin_firma:
        df = df[df["voting_pattern"] == "sin_firma"]

    # Outlier filters (epilogo/residuo)
    outlier_epi = st.sidebar.checkbox("⚠ Epilogo > 500 wc")
    outlier_res = st.sidebar.checkbox("⚠ Residuo > 300 wc")
    if outlier_epi or outlier_res:
        zona_wc = compute_zona_wc(load_zonas())
        df = df.join(zona_wc, on="caso_id_canonico", rsuffix="_z")
        if outlier_epi:
            df = df[df.get("wc_epilogo", pd.Series(0)) > 500]
        if outlier_res:
            df = df[df.get("wc_residuo", pd.Series(0)) > 300]

    outcomes = sorted(df["outcome"].dropna().unique())
    if outcomes:
        outcome_sel = st.sidebar.multiselect("Outcome", outcomes)
        if outcome_sel:
            df = df[df["outcome"].isin(outcome_sel)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Mostrando {len(df):,} casos")

    return df


# -- Zona toggles -----------------------------------------------------------

def render_zone_toggles():
    """Renderiza checkboxes para mostrar/ocultar zonas. Retorna set de zonas visibles."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Zonas visibles")

    zonas_visibles = set()

    # Defaults: todo visible excepto header_pagina
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

    # Presets rapidos
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔍 Todas"):
            for z in defaults:
                st.session_state[f"zona_{z}"] = True
    with col2:
        if st.button("🎯 Solo fallo"):
            for z in defaults:
                st.session_state[f"zona_{z}"] = z in (
                    "apertura", "cuerpo", "dispositivo", "firma",
                    "voto_separado"
                )

    # Presets de inspección por zona
    col3, col4, col5 = st.sidebar.columns(3)
    with col3:
        if st.button("📎 Epilogo"):
            for z in defaults:
                st.session_state[f"zona_{z}"] = z == "epilogo"
    with col4:
        if st.button("🗑️ Residuo"):
            for z in defaults:
                st.session_state[f"zona_{z}"] = z == "residuo_caso_anterior"
    with col5:
        if st.button("✒️ Firma"):
            for z in defaults:
                st.session_state[f"zona_{z}"] = z == "firma"

    for zona, default in defaults.items():
        style = ZONA_STYLE.get(zona, ("", "", "", zona))
        icon, _, fg, label = style
        key = f"zona_{zona}"
        if key not in st.session_state:
            st.session_state[key] = default
        checked = st.sidebar.checkbox(
            f"{icon} {label}" if icon else label,
            value=st.session_state[key],
            key=key,
        )
        if checked:
            zonas_visibles.add(zona)

    return zonas_visibles


# -- Vista: tabla ------------------------------------------------------------

def render_table(df: pd.DataFrame):
    display_cols = [
        "caso_id_canonico", "tomo", "case_name_indice",
        "voting_pattern", "outcome", "n_jueces", "word_count",
        "tipo_entrada",
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    df_display = df[display_cols].copy()

    # Agregar wc de epilogo/residuo desde zonas
    zona_wc = compute_zona_wc(load_zonas())
    df_display = df_display.join(zona_wc, on="caso_id_canonico")
    df_display["wc_epilogo"] = df_display["wc_epilogo"].fillna(0).astype(int)
    df_display["wc_residuo"] = df_display["wc_residuo"].fillna(0).astype(int)

    # Flag outliers
    df_display["⚠"] = ""
    mask_epi = df_display["wc_epilogo"] > 500
    mask_res = df_display["wc_residuo"] > 300
    df_display.loc[mask_epi, "⚠"] += "E"
    df_display.loc[mask_res, "⚠"] += "R"

    df_display = df_display.rename(columns={
        "caso_id_canonico": "ID",
        "tomo": "Tomo",
        "case_name_indice": "Caratula",
        "voting_pattern": "Patron",
        "outcome": "Resultado",
        "n_jueces": "Jueces",
        "word_count": "WC",
        "tipo_entrada": "Tipo",
        "wc_epilogo": "Epi",
        "wc_residuo": "Res",
    })
    if "Caratula" in df_display.columns:
        df_display["Caratula"] = df_display["Caratula"].str[:80]
    return df_display


# -- Vista: detalle ---------------------------------------------------------

def render_detail(caso: pd.Series, votos_df: pd.DataFrame,
                  zonas_df: pd.DataFrame, zonas_visibles: set):
    caso_id = caso["caso_id_canonico"]

    st.markdown(f"### {caso_id}")
    caratula = caso.get("case_name_indice", "") or caso.get("case_name_cuerpo", "")
    st.caption(caratula)

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

        info_pairs = [
            ("Tomo", caso.get("tomo")),
            ("Pagina", caso.get("pagina")),
            ("Resultado", caso.get("outcome")),
            ("Jueces", caso.get("n_jueces")),
            ("Disidencias", caso.get("n_disidencias")),
            ("Tipo", caso.get("tipo_entrada")),
            ("Fecha", caso.get("date")),
            ("Originaria", caso.get("is_originaria")),
            ("Dictamen", caso.get("dictamen_presente")),
            ("Word count", caso.get("word_count")),
            ("WC mayoria", caso.get("wc_mayoria")),
            ("WC votos", caso.get("wc_votos")),
            ("WC dictamen", caso.get("wc_dictamen")),
            ("Status fin", caso.get("status_fin")),
            ("Pista fin", caso.get("pista_fin")),
            ("Archivo", caso.get("source_file")),
            ("Lineas", f'{caso.get("linea_inicio")}–{caso.get("linea_fin_real")}'),
        ]
        for label, val in info_pairs:
            if pd.notna(val) and val != "":
                st.markdown(f"**{label}:** {val}")

        # Zonas del caso (resumen)
        caso_zonas = zonas_df[zonas_df["caso_id_canonico"] == caso_id]
        if not caso_zonas.empty:
            st.markdown("---")
            st.markdown("**Zonas**")
            zona_summary = caso_zonas.groupby("zona").agg(
                segs=("segmento", "count"),
                wc=("wc", "sum"),
            ).sort_values("wc", ascending=False)
            for zona, row in zona_summary.iterrows():
                style = ZONA_STYLE.get(zona, ("", "", "", zona))
                icon = style[0]
                fg = style[2]
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

        # Construir mapa linea_relativa -> zona desde zonas CSV
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
            vis = "visible" if zona in zonas_visibles else "oculta"
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

            # Separador cuando cambia la zona
            if (zona != prev_zona and visible
                    and zona not in ("header_pagina",)):
                style = ZONA_STYLE.get(zona, ("", "", "", zona))
                icon, _, _, label = style
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
            "streamlit run scripts/explorador/exploradorv4.py\n```"
        )
        return

    df = load_casos()
    votos_df = load_votos()
    zonas_df = load_zonas()

    filtered = render_sidebar(df)
    zonas_visibles = render_zone_toggles()

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
        render_detail(filtered.loc[idx], votos_df, zonas_df, zonas_visibles)

    else:
        st.title("⚖️ Explorador del Corpus CSJN v4")

        df_display = render_table(filtered)

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


if __name__ == "__main__":
    main()
