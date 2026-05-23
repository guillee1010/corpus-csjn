"""
Patch para exploradorv5.py — Vista editorial (B077)
====================================================

Agrega al explorador la capacidad de visualizar las secciones
editoriales (acordadas, índices, discursos) al final de cada
archivo .md del tomo.

Integración: copiar las funciones y constantes marcadas con
# B077 al explorador existente, y agregar la llamada a
render_editorial() en main().

Uso standalone (para PoC):
    streamlit run patch_explorador_editorial.py
"""

import re
import streamlit as st
import pandas as pd
from pathlib import Path

# -- Config ------------------------------------------------------------------

st.set_page_config(
    page_title="Corpus CSJN — Editorial Viewer",
    page_icon="📇",
    layout="wide",
)

REPO_ROOT  = Path.cwd()
CASOS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# ═══════════════════════════════════════════════════════════════════════════
# B077: Regex editoriales (mismos del PoC)
# ═══════════════════════════════════════════════════════════════════════════

RE_EDITORIAL_ACORDADA = re.compile(
    r"^(?:A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s+Y\s+RESOLUCIONES\s*$"
    r"|ACORDADAS\s*$)", re.I
)
RE_EDITORIAL_DISCURSO = re.compile(r"^DISCURSOS\b", re.I)
RE_EDITORIAL_INDICE = re.compile(
    r"^(?:"
    r"INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)
RE_EDITORIAL_ANY = re.compile(
    r"^(?:"
    r"A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s+Y\s+RESOLUCIONES\s*$"
    r"|ACORDADAS\s*$"
    r"|DISCURSOS\b"
    r"|INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)


def tipo_zona_editorial(linea):
    s = linea.strip()
    if not s:
        return None
    if RE_EDITORIAL_ACORDADA.match(s):
        return "acordada"
    if RE_EDITORIAL_DISCURSO.match(s):
        return "discurso"
    if RE_EDITORIAL_INDICE.match(s):
        return "indice"
    return None


# ═══════════════════════════════════════════════════════════════════════════
# B077: Paleta editorial (agregar a ZONA_STYLE del explorador)
# ═══════════════════════════════════════════════════════════════════════════

ZONA_STYLE_EDITORIAL = {
    "acordada":    ("📋", "#2a1a00", "#ffaa33", "Acordada"),
    "indice":      ("📇", "#001a2a", "#33aaff", "Índice"),
    "discurso":    ("🎤", "#2a0a2a", "#cc66ff", "Discurso"),
    "pre_editorial": ("",  "#1a1a1a", "#666666", "Pre-editorial"),
    "header_pagina": ("",  "#0e1117", "#444444", "Header página"),
}

RE_PAGE_HEADER = re.compile(
    r"^(?:\d{1,5}\s*$"               # solo número de página
    r"|DE JUSTICIA DE LA NACI[OÓ]N"  # header superior
    r"|FALLOS DE LA CORTE SUPREMA"    # header inferior
    r"|\d{3}\s*$"                     # número de tomo (3 dígitos solo)
    r")", re.I
)


# ═══════════════════════════════════════════════════════════════════════════
# B077: Funciones de detección y rendering editorial
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_casos():
    df = pd.read_csv(CASOS_CSV, encoding="utf-8", dtype=str)
    for col in ["tomo", "linea_inicio", "linea_fin_real"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_data
def load_source_file(source_file: str):
    filepath = CORPUS_DIR / source_file
    if not filepath.exists():
        return None
    return filepath.read_text(encoding="utf-8").split("\n")


@st.cache_data
def detectar_editorial_en_archivo(source_file: str, linea_post_ultimo_caso: int):
    """
    Detecta secciones editoriales en un archivo .md.
    
    Retorna:
        primer_editorial: int | None — línea absoluta del primer marcador
        secciones: list[dict] — secciones con tipo, linea_ini, linea_fin, wc
        zonas_por_linea: dict[int, str] — mapa línea_absoluta → zona
    """
    lines = load_source_file(source_file)
    if lines is None:
        return None, [], {}

    n = len(lines)
    
    # Buscar primer marcador editorial desde después del último caso
    primer_editorial = None
    for k in range(max(0, linea_post_ultimo_caso), n):
        s = lines[k].strip()
        if s and RE_EDITORIAL_ANY.match(s):
            primer_editorial = k
            break

    if primer_editorial is None:
        return None, [], {}

    # Zonificar
    zonas_por_linea = {}
    zona_activa = "pre_editorial"
    secciones = []
    ini_seccion = primer_editorial

    for k in range(primer_editorial, n):
        s = lines[k].strip()

        # Page headers
        if s and RE_PAGE_HEADER.match(s):
            zonas_por_linea[k] = "header_pagina"
            continue

        nueva = tipo_zona_editorial(lines[k])
        if nueva and nueva != zona_activa:
            # Cerrar sección anterior
            if zona_activa not in ("pre_editorial",) and ini_seccion < k:
                wc = sum(len(lines[j].split()) for j in range(ini_seccion, k))
                secciones.append({
                    "seccion": zona_activa,
                    "linea_ini": ini_seccion,
                    "linea_fin": k - 1,
                    "n_lineas": k - ini_seccion,
                    "wc": wc,
                })
            zona_activa = nueva
            ini_seccion = k

        zonas_por_linea[k] = zona_activa

    # Cerrar última sección
    if zona_activa not in ("pre_editorial",):
        wc = sum(len(lines[j].split()) for j in range(ini_seccion, n))
        secciones.append({
            "seccion": zona_activa,
            "linea_ini": ini_seccion,
            "linea_fin": n - 1,
            "n_lineas": n - ini_seccion,
            "wc": wc,
        })

    return primer_editorial, secciones, zonas_por_linea


def render_editorial():
    """Vista editorial: muestra acordadas/índices/discursos post-fallos."""
    
    df = load_casos()

    st.title("📇 Contenido Editorial por Tomo")
    st.caption(
        "Acordadas, índices por partes, índices por materias y discursos "
        "al final de cada archivo del corpus."
    )

    # Encontrar archivos con sus últimos casos
    archivos = (
        df.groupby("source_file")
        .agg(
            tomo=("tomo", "first"),
            n_casos=("caso_id_canonico", "count"),
            ultimo_caso=("caso_id_canonico", "last"),
            linea_fin_max=("linea_fin_real", "max"),
        )
        .reset_index()
        .sort_values(["tomo", "source_file"])
    )

    # Sidebar: selección de archivo
    st.sidebar.header("📇 Editorial Viewer")

    tomos_disponibles = sorted(archivos["tomo"].unique())
    tomo_sel = st.sidebar.selectbox(
        "Tomo", tomos_disponibles,
        format_func=lambda t: f"Tomo {int(t)}"
    )

    archivos_tomo = archivos[archivos["tomo"] == tomo_sel]
    archivo_sel = st.sidebar.selectbox(
        "Archivo", archivos_tomo["source_file"].values,
    )

    if archivo_sel is None:
        return

    row = archivos_tomo[archivos_tomo["source_file"] == archivo_sel].iloc[0]
    linea_post = int(row["linea_fin_max"]) + 1

    # Detectar editorial
    primer_ed, secciones, zonas = detectar_editorial_en_archivo(
        archivo_sel, linea_post
    )

    if primer_ed is None:
        st.info(f"No se detectó contenido editorial en {archivo_sel}")
        return

    lines = load_source_file(archivo_sel)
    n_total = len(lines) if lines else 0

    # Stats
    col1, col2, col3 = st.columns(3)
    total_wc = sum(s["wc"] for s in secciones)
    with col1:
        st.metric("Secciones", len(secciones))
    with col2:
        st.metric("Líneas editoriales", n_total - primer_ed)
    with col3:
        st.metric("Word count editorial", f"{total_wc:,}")

    # Desglose por tipo
    st.markdown("### Secciones detectadas")
    for s in secciones:
        style = ZONA_STYLE_EDITORIAL.get(s["seccion"], ("", "", "", s["seccion"]))
        icon, bg, fg, label = style
        st.markdown(
            f'<div style="background:{bg}; color:{fg}; padding:4px 8px; '
            f'border-radius:4px; margin:2px 0; font-size:0.85rem;">'
            f'{icon} <b>{label}</b> — '
            f'L{s["linea_ini"]+1}–L{s["linea_fin"]+1} · '
            f'{s["n_lineas"]} líneas · {s["wc"]:,} wc'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Rango a visualizar
    st.markdown("### Bloque fuente")

    rango_opciones = ["Todo"] + [
        f'{ZONA_STYLE_EDITORIAL.get(s["seccion"], ("","","",s["seccion"]))[3]} '
        f'(L{s["linea_ini"]+1}–L{s["linea_fin"]+1})'
        for s in secciones
    ]
    rango_sel = st.selectbox("Sección a visualizar", rango_opciones)

    if rango_sel == "Todo":
        view_start = primer_ed
        view_end = n_total
    else:
        idx = rango_opciones.index(rango_sel) - 1
        sec = secciones[idx]
        view_start = sec["linea_ini"]
        view_end = sec["linea_fin"] + 1

    # Limitar visualización a 2000 líneas
    max_display = 2000
    if view_end - view_start > max_display:
        st.warning(
            f"Sección de {view_end - view_start} líneas. "
            f"Mostrando primeras {max_display}."
        )
        view_end = view_start + max_display

    # Leyenda
    zonas_presentes = set(s["seccion"] for s in secciones)
    leyenda_html = '<div style="display:flex; gap:8px; margin-bottom:8px;">'
    for zona, (icon, bg, fg, label) in ZONA_STYLE_EDITORIAL.items():
        if zona not in zonas_presentes and zona != "header_pagina":
            continue
        leyenda_html += (
            f'<span style="background:{bg}; color:{fg}; padding:2px 6px; '
            f'border-radius:3px; font-size:0.75rem;">{icon} {label}</span>'
        )
    leyenda_html += '</div>'
    st.markdown(leyenda_html, unsafe_allow_html=True)

    # Generar CSS
    css_rules = []
    for zona, (_, bg, fg, _) in ZONA_STYLE_EDITORIAL.items():
        css_rules.append(
            f".ze-{zona} {{ background-color: {bg}; color: {fg}; }}"
        )
    css = f"""<style>
    .ed-block {{
        font-family: 'Courier New', monospace;
        font-size: 0.78rem;
        line-height: 1.5;
        background-color: #0e1117;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
        max-height: 70vh;
        overflow-y: auto;
    }}
    .ed-line {{
        white-space: pre-wrap;
        word-wrap: break-word;
    }}
    .ed-linenum {{
        color: #555;
        display: inline-block;
        width: 5em;
        text-align: right;
        margin-right: 1em;
        user-select: none;
    }}
    .ed-sep {{
        border-top: 1px dashed #555;
        margin: 4px 0 2px 0;
        padding-top: 2px;
        font-size: 0.65rem;
        color: #999;
        font-family: sans-serif;
    }}
    {chr(10).join(css_rules)}
    </style>"""
    st.markdown(css, unsafe_allow_html=True)

    # Renderizar bloque
    html_lines = []
    prev_zona = None

    for k in range(view_start, view_end):
        zona = zonas.get(k, "pre_editorial")
        cls = f"ze-{zona}"

        # Separador de zona
        if zona != prev_zona and zona != "header_pagina":
            style = ZONA_STYLE_EDITORIAL.get(zona, ("", "", "", zona))
            icon, _, _, label = style
            html_lines.append(
                f'<div class="ed-sep">{icon} {label}</div>'
            )

        escaped = (
            lines[k].rstrip("\n\r")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html_lines.append(
            f'<div class="ed-line {cls}">'
            f'<span class="ed-linenum">{k+1}</span>{escaped}'
            f'</div>'
        )

        if zona != "header_pagina":
            prev_zona = zona

    html = f'<div class="ed-block">{"".join(html_lines)}</div>'
    st.markdown(html, unsafe_allow_html=True)


if __name__ == "__main__":
    render_editorial()
