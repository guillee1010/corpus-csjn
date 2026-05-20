"""
Visor del Corpus CSJN — Vista 1: Explorador de casos
=====================================================
Streamlit app para explorar los fallos parseados del corpus CSJN.

Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    streamlit run scripts/visor/visor.py
"""

import re
import streamlit as st
import pandas as pd
from pathlib import Path

# ── Configuración de página ──────────────────────────────────────────

st.set_page_config(
    page_title="Corpus CSJN — Explorador",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Rutas (relativas a la raíz del repo) ────────────────────────────

REPO_ROOT = Path.cwd()
CASOS_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
VOTOS_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos_votos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"


# ── Carga de datos (cacheada) ────────────────────────────────────────

@st.cache_data
def load_casos():
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    # Convertir columnas numéricas
    for col in ["tomo", "linea_inicio", "linea_fin", "linea_fin_real",
                 "n_jueces", "n_votos_svoto", "n_disidencias", "word_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_votos():
    return pd.read_csv(VOTOS_CSV, encoding="utf-8", dtype=str)


@st.cache_data
def load_source_block(source_file: str, linea_inicio: int, linea_fin_real: int):
    """Carga un bloque de líneas del .md fuente."""
    filepath = CORPUS_DIR / source_file
    if not filepath.exists():
        return None, filepath
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # linea_inicio y linea_fin_real son 1-indexed
    start = max(0, linea_inicio - 1)
    end = min(len(lines), linea_fin_real)
    block = lines[start:end]
    return block, filepath


# ── Funciones de resaltado ───────────────────────────────────────────

# Patrones para resaltar líneas en el bloque fuente
RE_POR_ELLO = re.compile(r"^\s*Por ello", re.IGNORECASE)
RE_FIRMA = re.compile(
    # Nombre — Nombre (title case o ALL CAPS), permite (según su voto) etc.
    r"^(?:[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜa-záéíóúñü.\s()]+)"
    r"(?:\s*(?:—|–)\s*(?:\n\s*)?[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜa-záéíóúñü.\s()]+)+"
)
RE_VOTO_HEADER = re.compile(
    r"(?:VOTO|DISIDENCIA|AMPLIACIÓN|SEGÚN SU VOTO|EN DISIDENCIA)",
    re.IGNORECASE,
)
RE_PAGE_HEADER = re.compile(
    r"^(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACION|DE JUSTICIA DE LA NACIÓN)\s*$",
    re.IGNORECASE,
)
RE_PAGE_NUMBER = re.compile(r"^\d{1,4}\s*$")


def classify_line(line: str) -> str:
    """Clasifica una línea para resaltado. Retorna clase CSS."""
    stripped = line.strip()
    if not stripped:
        return ""
    if RE_POR_ELLO.match(stripped):
        return "hl-dispositivo"
    if RE_FIRMA.match(stripped):
        return "hl-firma"
    if RE_VOTO_HEADER.search(stripped) and len(stripped) < 120:
        return "hl-voto"
    if RE_PAGE_HEADER.match(stripped) or RE_PAGE_NUMBER.match(stripped):
        return "hl-page"
    return ""


# ── CSS personalizado ────────────────────────────────────────────────

st.markdown("""
<style>
/* Tabla de casos */
.caso-table { font-size: 0.85rem; }

/* Resaltado del bloque fuente */
.source-block {
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    line-height: 1.5;
    background-color: #0e1117;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    max-height: 70vh;
    overflow-y: auto;
}
.source-line {
    white-space: pre-wrap;
    word-wrap: break-word;
}
.line-num {
    color: #555;
    display: inline-block;
    width: 4em;
    text-align: right;
    margin-right: 1em;
    user-select: none;
}
.hl-dispositivo { background-color: #1a3a1a; color: #7fff7f; }
.hl-firma { background-color: #1a1a3a; color: #7f7fff; }
.hl-voto { background-color: #3a2a1a; color: #ffbf7f; }
.hl-page { color: #666; font-style: italic; }

/* Leyenda */
.leyenda { font-size: 0.75rem; margin-bottom: 0.5rem; }
.leyenda span { padding: 2px 6px; margin-right: 8px; border-radius: 3px; }

/* Detalle del caso */
.caso-meta { font-size: 0.85rem; }
.caso-meta dt { font-weight: bold; color: #aaa; }
.caso-meta dd { margin-bottom: 0.3rem; margin-left: 0; }

/* Badge voting pattern */
.vp-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.vp-unanime { background: #1a3a1a; color: #7fff7f; }
.vp-disidencia { background: #3a1a1a; color: #ff7f7f; }
.vp-segun_su_voto { background: #3a2a1a; color: #ffbf7f; }
.vp-mixed { background: #2a2a3a; color: #bf7fff; }
.vp-sin_firma { background: #333; color: #999; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar: filtros ─────────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza filtros en el sidebar y retorna el DataFrame filtrado."""
    st.sidebar.header("⚖️ Corpus CSJN")
    st.sidebar.caption(f"{len(df):,} casos · {df['tomo'].nunique()} tomos")

    # Filtro: tipo_entrada (solo fallos por defecto)
    solo_fallos = st.sidebar.checkbox("Solo fallos", value=True)
    if solo_fallos:
        df = df[df["tipo_entrada"] == "fallo"]

    # Filtro: tomo
    tomos = sorted(df["tomo"].dropna().unique())
    tomo_sel = st.sidebar.selectbox(
        "Tomo", ["Todos"] + [str(t) for t in tomos]
    )
    if tomo_sel != "Todos":
        df = df[df["tomo"] == int(tomo_sel)]

    # Filtro: voting_pattern
    vp_options = sorted(df["voting_pattern"].dropna().unique())
    vp_sel = st.sidebar.multiselect("Voting pattern", vp_options)
    if vp_sel:
        df = df[df["voting_pattern"].isin(vp_sel)]

    # Filtro: sin_firma
    sin_firma = st.sidebar.checkbox("Solo sin firma")
    if sin_firma:
        df = df[df["voting_pattern"] == "sin_firma"]

    # Filtro: búsqueda por carátula
    busqueda = st.sidebar.text_input("🔎 Buscar en carátula")
    if busqueda:
        mask = df["case_name_indice"].str.contains(
            busqueda, case=False, na=False
        ) | df["case_name_cuerpo"].str.contains(
            busqueda, case=False, na=False
        )
        df = df[mask]

    # Filtro: outcome
    outcomes = sorted(df["outcome"].dropna().unique())
    if outcomes:
        outcome_sel = st.sidebar.multiselect("Outcome", outcomes)
        if outcome_sel:
            df = df[df["outcome"].isin(outcome_sel)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Mostrando {len(df):,} casos")

    return df


# ── Vista: tabla de casos ────────────────────────────────────────────

def render_table(df: pd.DataFrame):
    """Renderiza la tabla de casos con selección."""

    # Preparar columnas para mostrar
    display_cols = [
        "caso_id_canonico", "tomo", "case_name_indice",
        "voting_pattern", "outcome", "n_jueces", "tipo_entrada",
    ]
    display_cols = [c for c in display_cols if c in df.columns]

    df_display = df[display_cols].copy()
    df_display = df_display.rename(columns={
        "caso_id_canonico": "ID",
        "tomo": "Tomo",
        "case_name_indice": "Carátula",
        "voting_pattern": "Patrón",
        "outcome": "Resultado",
        "n_jueces": "Jueces",
        "tipo_entrada": "Tipo",
    })

    # Truncar carátula para la tabla
    if "Carátula" in df_display.columns:
        df_display["Carátula"] = df_display["Carátula"].str[:80]

    return df_display


# ── Vista: detalle de caso ───────────────────────────────────────────

def render_detail(caso: pd.Series, votos_df: pd.DataFrame):
    """Renderiza la vista de detalle de un caso."""

    caso_id = caso["caso_id_canonico"]

    # ── Encabezado ──
    st.markdown(f"### {caso_id}")
    caratula = caso.get("case_name_indice", "") or caso.get("case_name_cuerpo", "")
    st.caption(caratula)

    col_meta, col_source = st.columns([1, 2])

    # ── Panel izquierdo: metadatos ──
    with col_meta:
        st.markdown("**Datos del caso**")

        vp = caso.get("voting_pattern", "")
        vp_class = f"vp-{vp}" if vp else ""
        st.markdown(
            f'Patrón: <span class="vp-badge {vp_class}">{vp}</span>',
            unsafe_allow_html=True,
        )

        info_pairs = [
            ("Tomo", caso.get("tomo")),
            ("Resultado", caso.get("outcome")),
            ("Jueces", caso.get("n_jueces")),
            ("Disidencias", caso.get("n_disidencias")),
            ("Tipo", caso.get("tipo_entrada")),
            ("Fecha", caso.get("date")),
            ("Originaria", caso.get("is_originaria")),
            ("Dictamen", caso.get("dictamen_presente")),
            ("Word count", caso.get("word_count")),
            ("Status fin", caso.get("status_fin")),
            ("Pista fin", caso.get("pista_fin")),
            ("Archivo", caso.get("source_file")),
            ("Líneas", f'{caso.get("linea_inicio")}–{caso.get("linea_fin_real")}'),
        ]
        for label, val in info_pairs:
            if pd.notna(val) and val != "":
                st.markdown(f"**{label}:** {val}")

        # ── Votos ──
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

        # ── Dispositivo ──
        por_ello = caso.get("por_ello_text", "")
        if pd.notna(por_ello) and por_ello:
            st.markdown("---")
            st.markdown("**Dispositivo**")
            # Truncar si es muy largo
            if len(str(por_ello)) > 500:
                st.text(str(por_ello)[:500] + "…")
            else:
                st.text(str(por_ello))

        # ── Firma ──
        firma = caso.get("firma_raw", "")
        if pd.notna(firma) and firma:
            st.markdown("---")
            st.markdown("**Firma**")
            st.text(str(firma))

    # ── Panel derecho: bloque fuente ──
    with col_source:
        st.markdown("**Bloque fuente (.md)**")

        source_file = caso.get("source_file", "")
        linea_inicio = caso.get("linea_inicio")
        linea_fin_real = caso.get("linea_fin_real")

        if pd.isna(linea_inicio) or pd.isna(linea_fin_real) or not source_file:
            st.warning("Sin datos de localización para este caso.")
            return

        block, filepath = load_source_block(
            source_file, int(linea_inicio), int(linea_fin_real)
        )

        if block is None:
            st.error(f"Archivo no encontrado: {filepath}")
            st.info(
                "El visor busca los .md en la carpeta corpus/ "
                "relativa al directorio donde se ejecuta streamlit."
            )
            return

        # Leyenda
        st.markdown(
            '<div class="leyenda">'
            '<span class="hl-dispositivo">Dispositivo</span>'
            '<span class="hl-firma">Firma</span>'
            '<span class="hl-voto">Voto/Disidencia</span>'
            '<span class="hl-page">Encabezado pág.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Renderizar bloque con resaltado
        html_lines = []
        base_num = int(linea_inicio)
        for i, line in enumerate(block):
            line_num = base_num + i
            cls = classify_line(line)
            escaped = (
                line.rstrip("\n\r")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            cls_attr = f' class="source-line {cls}"' if cls else ' class="source-line"'
            html_lines.append(
                f'<div{cls_attr}>'
                f'<span class="line-num">{line_num}</span>{escaped}'
                f'</div>'
            )

        html = f'<div class="source-block">{"".join(html_lines)}</div>'
        st.markdown(html, unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    # Verificar que existen los CSV
    if not CASOS_CSV.exists():
        st.error(f"No se encontró: {CASOS_CSV}")
        st.info(
            "Ejecutá el visor desde la raíz del repo:\n\n"
            "```\ncd C:\\Users\\guill\\Proyectos\\corpus-csjn\n"
            "streamlit run scripts/visor/visor.py\n```"
        )
        return

    # Cargar datos
    df = load_casos()
    votos_df = load_votos()

    # Sidebar con filtros
    filtered = render_sidebar(df)

    # ── Estado de sesión ──
    if "selected_idx" not in st.session_state:
        st.session_state.selected_idx = None

    # ── Layout principal ──
    if st.session_state.selected_idx is not None:
        # Vista de detalle
        idx = st.session_state.selected_idx

        # Navegación
        indices = filtered.index.tolist()
        if idx in indices:
            pos = indices.index(idx)
        else:
            # El caso seleccionado fue filtrado — volver a tabla
            st.session_state.selected_idx = None
            st.rerun()
            return

        nav_cols = st.columns([1, 1, 1, 4])
        with nav_cols[0]:
            if st.button("← Volver a tabla"):
                st.session_state.selected_idx = None
                st.rerun()
        with nav_cols[1]:
            if pos > 0:
                if st.button("◀ Anterior"):
                    st.session_state.selected_idx = indices[pos - 1]
                    st.rerun()
        with nav_cols[2]:
            if pos < len(indices) - 1:
                if st.button("Siguiente ▶"):
                    st.session_state.selected_idx = indices[pos + 1]
                    st.rerun()
        with nav_cols[3]:
            st.caption(f"Caso {pos + 1} de {len(indices)}")

        st.markdown("---")
        render_detail(filtered.loc[idx], votos_df)

    else:
        # Vista de tabla
        st.title("⚖️ Explorador del Corpus CSJN")

        df_display = render_table(filtered)

        # Paginación
        page_size = 50
        n_pages = max(1, (len(df_display) + page_size - 1) // page_size)
        page = st.number_input(
            "Página", min_value=1, max_value=n_pages, value=1, step=1
        )
        start = (page - 1) * page_size
        end = start + page_size

        st.caption(
            f"Página {page}/{n_pages} · "
            f"Filas {start + 1}–{min(end, len(df_display))} de {len(df_display)}"
        )

        # Mostrar tabla
        page_df = df_display.iloc[start:end]
        page_indices = filtered.index[start:end]

        # Usar st.dataframe con selección de fila
        event = st.dataframe(
            page_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        # Detectar selección
        if event and event.selection and event.selection.rows:
            selected_row = event.selection.rows[0]
            if selected_row < len(page_indices):
                st.session_state.selected_idx = page_indices[selected_row]
                st.rerun()


if __name__ == "__main__":
    main()
