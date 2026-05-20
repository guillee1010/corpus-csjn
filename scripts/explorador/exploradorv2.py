"""
Visor del Corpus CSJN — Vista 1: Explorador de casos
=====================================================
Streamlit app para explorar los fallos parseados del corpus CSJN.

Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    streamlit run scripts/explorador/explorador.py
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


# ── Regex de secciones (tomados del parser) ──────────────────────────

# Apertura del fallo
RE_APERTURA = re.compile(
    r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I
)

# Fecha
RE_FECHA_LINEA = re.compile(
    r"^Buenos Aires[,]?\s+\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4}", re.I
)

# Considerando
RE_CONSIDERANDO = re.compile(r"^Considerando\s*[:.]?\s*$", re.I)

# Dictamen del Procurador
RE_DICT_HDR = re.compile(
    r"^Dictamen\s+de(l)?\s+(la\s+)?Procura", re.I
)

# Dispositivo — las 15+ variantes del parser
RE_POR_ELLO = re.compile(r"^Por ello[,.]?\s*", re.I)
POR_ELLO_ARGUMENTAL = {
    "concluyó", "concluyo", "estimo", "estimó", "considera",
    "considero", "consideró", "entiende", "entendió",
    "afirma", "afirmó", "sostiene", "sostuvo",
}
DISPOSITIVO_ALT = [
    re.compile(r"^Por los fundamentos\s+y\s+conc[lu]+siones", re.I),
    re.compile(r"^Por los fundamentos\b", re.I),
    re.compile(r"^De conformidad con\b", re.I),
    re.compile(r"^Por todo lo expuesto\b", re.I),
    re.compile(r"^Por todo ello\b", re.I),
    re.compile(r"^Por lo expuesto\b", re.I),
    re.compile(r"^Por estas razones\b", re.I),
    re.compile(r"^En m[ée]rito\s+a\s+lo\b", re.I),
    re.compile(r"^En su m[ée]rito\b", re.I),
    re.compile(r"^En consecuencia\s*,?\s*\b", re.I),
    re.compile(r"^Atento\s+(a\s+)?(que|lo|el)\b", re.I),
    re.compile(r"^Por lo expresado\b", re.I),
    re.compile(r"^Por las razones\b", re.I),
    re.compile(r"^Por las consideraciones\b", re.I),
    re.compile(r"^O[íi]dos?\s+(el|la|los|las)\b", re.I),
    re.compile(r"^Que[,]?\s+por\s+ello\b", re.I),
]

# Votos y disidencias — regex del parser
RE_VOTO_HDR = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I,
)
RE_DISID_HDR = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I,
)

# Page headers y números de página
RE_PAGE_HEADER = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACIÓN|"
    r"DE JUSTICIA DE LA NACION|\d{2,6})\s*$", re.I,
)

# Firma — patrón nombre — nombre (title case o ALL CAPS)
RE_FIRMA = re.compile(
    r"^(?:[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜa-záéíóúñü.\s()]+)"
    r"(?:\s*(?:—|–)\s*(?:\n\s*)?[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜa-záéíóúñü.\s()]+)+"
)

# Sumario editorial — headers en MAYÚSCULAS cortos (antes de apertura)
RE_SUMARIO_HEADER = re.compile(r"^[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ\s:.,\-]{4,}$")


def detectar_dispositivo(stripped):
    """Detecta apertura de dispositivo con la lógica del parser."""
    if RE_POR_ELLO.match(stripped):
        rest = RE_POR_ELLO.sub("", stripped).strip()
        first_w = rest.split()[0].lower().rstrip(",.;:") if rest.split() else ""
        if first_w in POR_ELLO_ARGUMENTAL:
            return False
        return True
    for rx in DISPOSITIVO_ALT:
        if rx.match(stripped):
            return True
    return False


# ── Clasificador de líneas por sección ───────────────────────────────

# Secciones en orden de prioridad de detección
SECTION_COLORS = {
    "apertura":     ("🔶", "#3a2a00", "#ffd700", "Apertura"),
    "fecha":        ("📅", "#2a2a1a", "#e0c060", "Fecha"),
    "considerando": ("📋", "#1a2a2a", "#60c0c0", "Considerando"),
    "dictamen":     ("📜", "#2a1a2a", "#c060c0", "Dictamen"),
    "dispositivo":  ("⚖️", "#1a3a1a", "#7fff7f", "Dispositivo"),
    "firma":        ("✒️", "#1a1a3a", "#7f7fff", "Firma"),
    "voto":         ("🗳️", "#3a2a1a", "#ffbf7f", "Voto/Disidencia"),
    "page":         ("",   "#1a1a1a", "#555",    "Encabezado pág."),
    "sumario_hdr":  ("📑", "#2a2a1a", "#c0a050", "Header sumario"),
}


def classify_line(line: str, seen_apertura: bool) -> str:
    """Clasifica una línea del bloque fuente. Retorna clave de sección."""
    stripped = line.strip()
    if not stripped:
        return ""

    # Page headers y números de página (siempre, en cualquier posición)
    if RE_PAGE_HEADER.match(stripped):
        return "page"

    # Apertura del fallo
    if RE_APERTURA.match(stripped):
        return "apertura"

    # Fecha
    if RE_FECHA_LINEA.match(stripped):
        return "fecha"

    # Considerando
    if RE_CONSIDERANDO.match(stripped):
        return "considerando"

    # Dictamen
    if RE_DICT_HDR.match(stripped):
        return "dictamen"

    # Dispositivo (con filtro argumental)
    if detectar_dispositivo(stripped):
        return "dispositivo"

    # Voto / Disidencia
    if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
        return "voto"

    # Firma (solo post-apertura — evita falsos positivos con carátulas)
    if seen_apertura and RE_FIRMA.match(stripped):
        return "firma"

    # Header de sumario (solo antes de la apertura)
    if not seen_apertura and RE_SUMARIO_HEADER.match(stripped) and len(stripped) < 100:
        return "sumario_hdr"

    return ""


def classify_block(lines: list[str]) -> list[str]:
    """Clasifica todas las líneas de un bloque. Retorna lista de claves."""
    result = []
    seen_apertura = False
    for line in lines:
        cls = classify_line(line, seen_apertura)
        if cls == "apertura":
            seen_apertura = True
        result.append(cls)
    return result


# ── Carga de datos (cacheada) ────────────────────────────────────────

@st.cache_data
def load_casos():
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    for col in ["tomo", "linea_inicio", "linea_fin", "linea_fin_real",
                 "n_jueces", "n_votos_svoto", "n_disidencias", "word_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Extraer página del caso_id_canonico (ej: "329_p5" → 5)
    df["pagina"] = df["caso_id_canonico"].str.extract(r"_p(\d+)$").astype(float)
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
    start = max(0, linea_inicio - 1)
    end = min(len(lines), linea_fin_real)
    return lines[start:end], filepath


# ── CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
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

/* Colores por sección */
.hl-apertura     { background-color: #3a2a00; color: #ffd700; font-weight: bold; }
.hl-fecha        { background-color: #2a2a1a; color: #e0c060; }
.hl-considerando { background-color: #1a2a2a; color: #60c0c0; font-weight: bold; }
.hl-dictamen     { background-color: #2a1a2a; color: #c060c0; font-weight: bold; }
.hl-dispositivo  { background-color: #1a3a1a; color: #7fff7f; }
.hl-firma        { background-color: #1a1a3a; color: #7f7fff; }
.hl-voto         { background-color: #3a2a1a; color: #ffbf7f; font-weight: bold; }
.hl-page         { color: #555; font-style: italic; }
.hl-sumario_hdr  { background-color: #2a2a1a; color: #c0a050; }

/* Separador de sección */
.section-sep {
    border-top: 1px dashed #444;
    margin: 4px 0 2px 0;
    padding-top: 2px;
    font-size: 0.65rem;
    color: #888;
    font-family: sans-serif;
}

/* Badge */
.vp-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.vp-unanime       { background: #1a3a1a; color: #7fff7f; }
.vp-disidencia    { background: #3a1a1a; color: #ff7f7f; }
.vp-segun_su_voto { background: #3a2a1a; color: #ffbf7f; }
.vp-mixed         { background: #2a2a3a; color: #bf7fff; }
.vp-sin_firma     { background: #333;    color: #999; }

/* Leyenda compacta */
.leyenda { font-size: 0.7rem; margin-bottom: 0.5rem; display: flex; flex-wrap: wrap; gap: 4px; }
.leyenda span { padding: 1px 6px; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar: filtros ─────────────────────────────────────────────────

def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("⚖️ Corpus CSJN")
    st.sidebar.caption(f"{len(df):,} casos · {df['tomo'].nunique()} tomos")

    # Solo fallos
    solo_fallos = st.sidebar.checkbox("Solo fallos", value=True)
    if solo_fallos:
        df = df[df["tipo_entrada"] == "fallo"]

    st.sidebar.markdown("---")
    st.sidebar.subheader("Buscar caso")

    # Tomo + página (búsqueda directa)
    col_t, col_p = st.sidebar.columns(2)
    with col_t:
        tomo_input = st.text_input("Tomo", placeholder="ej: 329")
    with col_p:
        pag_input = st.text_input("Página", placeholder="ej: 2024")

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

    # Búsqueda libre (carátula + dispositivo + firma)
    busqueda = st.sidebar.text_input(
        "🔎 Texto libre",
        placeholder="busca en carátula, dispositivo, firma…",
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

    # Voting pattern
    vp_options = sorted(df["voting_pattern"].dropna().unique())
    vp_sel = st.sidebar.multiselect("Voting pattern", vp_options)
    if vp_sel:
        df = df[df["voting_pattern"].isin(vp_sel)]

    # Solo sin firma
    sin_firma = st.sidebar.checkbox("Solo sin firma")
    if sin_firma:
        df = df[df["voting_pattern"] == "sin_firma"]

    # Outcome
    outcomes = sorted(df["outcome"].dropna().unique())
    if outcomes:
        outcome_sel = st.sidebar.multiselect("Outcome", outcomes)
        if outcome_sel:
            df = df[df["outcome"].isin(outcome_sel)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Mostrando {len(df):,} casos")

    return df


# ── Vista: tabla ─────────────────────────────────────────────────────

def render_table(df: pd.DataFrame):
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
    if "Carátula" in df_display.columns:
        df_display["Carátula"] = df_display["Carátula"].str[:80]
    return df_display


# ── Vista: detalle ───────────────────────────────────────────────────

def render_detail(caso: pd.Series, votos_df: pd.DataFrame):
    caso_id = caso["caso_id_canonico"]

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
            ("Página", caso.get("pagina")),
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
            st.text(txt[:500] + "…" if len(txt) > 500 else txt)

        # Firma
        firma = caso.get("firma_raw", "")
        if pd.notna(firma) and firma:
            st.markdown("---")
            st.markdown("**Firma**")
            st.text(str(firma))

    # ── Panel derecho: bloque fuente con secciones ──
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

        # Clasificar líneas
        classifications = classify_block(block)

        # Leyenda
        leyenda_html = '<div class="leyenda">'
        for key, (icon, _bg, color, label) in SECTION_COLORS.items():
            if key == "page":
                continue
            leyenda_html += (
                f'<span class="hl-{key}">{icon} {label}</span>'
            )
        leyenda_html += '</div>'
        st.markdown(leyenda_html, unsafe_allow_html=True)

        # Renderizar bloque con separadores de sección
        html_lines = []
        base_num = int(linea_inicio)
        prev_cls = ""

        for i, (line, cls) in enumerate(zip(block, classifications)):
            line_num = base_num + i

            # Separador cuando cambia la sección (solo secciones significativas)
            if cls and cls != prev_cls and cls != "page":
                info = SECTION_COLORS.get(cls)
                if info:
                    icon, _, _, label = info
                    html_lines.append(
                        f'<div class="section-sep">'
                        f'{icon} {label}</div>'
                    )

            escaped = (
                line.rstrip("\n\r")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            cls_attr = f' class="source-line hl-{cls}"' if cls else ' class="source-line"'
            html_lines.append(
                f'<div{cls_attr}>'
                f'<span class="line-num">{line_num}</span>{escaped}'
                f'</div>'
            )

            if cls and cls != "page":
                prev_cls = cls

        html = f'<div class="source-block">{"".join(html_lines)}</div>'
        st.markdown(html, unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────

def main():
    if not CASOS_CSV.exists():
        st.error(f"No se encontró: {CASOS_CSV}")
        st.info(
            "Ejecutá el visor desde la raíz del repo:\n\n"
            "```\ncd C:\\Users\\guill\\Proyectos\\corpus-csjn\n"
            "streamlit run scripts/explorador/explorador.py\n```"
        )
        return

    df = load_casos()
    votos_df = load_votos()

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
        render_detail(filtered.loc[idx], votos_df)

    else:
        st.title("⚖️ Explorador del Corpus CSJN")

        df_display = render_table(filtered)

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
