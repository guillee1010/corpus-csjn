# -*- coding: utf-8 -*-
"""
codificar_retest.py — Codificador CIEGO para el retest de M19 (kappa de Cohen).
corpus-csjn — Guillermo Rubinetti.

    streamlit run codificar_retest.py

QUE HACE
  - Lee retest_blank.csv (60 casos: caso_id_canonico + las 5 cod_*).
  - Para cada caso muestra SOLO el texto del fallo (de los bundles ciegos) +
    la definicion del CODEBOOK de cada campo y de cada valor. NUNCA abre
    csjn_casos.csv, ni la planilla original, ni la clave del parser, ni tu
    codificacion previa. Esa es la ceguera.
  - Guarda la recodificacion INCREMENTAL en un archivo aparte
    (retest_recodificado.csv). Nunca toca retest_blank.csv.
  - Marca cada caso como hecho al guardarlo; podes cerrar y retomar.

QUE NO HACE
  - No calcula el kappa. Cuando termines, lo corre analizar_validacion.py:
      python analizar_validacion.py \
          --planilla planilla_consolidada_MARCO_A_v18_15_n300.csv \
          --clave    planilla_consolidada_MARCO_A_v18_15_n300.csv \
          --planilla2 retest_recodificado.csv --label m19_kappa

REGLAS DE CODIFICACION (las mismas de la pasada original; CODEBOOK como esta
publicado, sin criterio mejorado):
  - (en blanco) = no aplica / null. Sale del kappa (no se compara).
  - AMBIGUO     = el OCR/texto no permite decidir. Sale del denominador.
  - queja_resultado: solo si es_queja = 1; si no, en blanco.
  - tipo_cuestion_federal: solo en REX y queja; si no, en blanco.
  - causa_inadmisibilidad: solo en desestimaciones; exige leer el considerando.
  - outcome: ante dispositivo con varios verbos, cascada first-match-wins como
    desempate; si haces un override semantico, anotalo en la nota.
"""

__version__ = "1.0.0"

from pathlib import Path
import re
import pandas as pd
import streamlit as st

# ============================ CONFIG ============================
# Rutas relativas a donde corras streamlit (parate en estadisticas\validacion,
# o poné rutas absolutas).
PLANILLA_RETEST = Path("retest_blank.csv")          # ENTRADA (no se modifica)
SALIDA          = Path("retest_recodificado.csv")    # SALIDA incremental
COL_ID          = "caso_id_canonico"

# Carpeta con los bundles ciegos (los .md que usaste para codificar Marco A,
# con headers tipo "# 329_p1399"). El script indexa TODOS los .md de la carpeta.
# Poné ahí los marco_A_lote_0*.md y el bundle de los 8 suplementarios.
BUNDLE_DIR  = Path("bundles")
RE_HEADER   = re.compile(r"^#\s+(\d+_p\d+)\s*$")     # encabezado de caso en el bundle

BLANK = "(en blanco / no aplica)"
AMB   = "AMBIGUO"
# ================================================================


# -------- taxonomia y definiciones (CODEBOOK v1.3) --------
DEF_CAMPO = {
    "es_queja": "¿El caso surge de un recurso de queja (por REX denegado)?",
    "outcome": "Disposición del fallo, tomada de la cláusula «por ello».",
    "queja_resultado": "Resultado de la queja. SOLO si es_queja=1; si no, en blanco.",
    "tipo_cuestion_federal": "Tipo de cuestión federal del REX. SOLO en REX y queja.",
    "causa_inadmisibilidad": "Causal específica de inadmisibilidad/desestimación. "
                             "SOLO en desestimaciones; exige leer el considerando.",
}

VALORES = {
    "es_queja": {
        "1": "Surge de un recurso de queja (REX denegado).",
        "0": "No es queja.",
    },
    "outcome": {
        "hace_lugar": "Recurso o queja concedido (hace lugar al recurso).",
        "competencia": "Resuelve competencia (declárase competente / asigna competencia).",
        "desestima": "Desestima el recurso/queja. Incluye rechazos por art. 280 o "
                     "Ac. 4/2007 cuando el resultado operativo es desestimar.",
        "procedente": "REX admisible y procedente sobre el fondo.",
        "revoca": "Revoca la sentencia del inferior.",
        "confirma": "Confirma la sentencia del inferior.",
        "rechaza": "Rechaza la petición/recurso.",
        "abstracto": "Cuestión devenida abstracta.",
        "deja_sin_efecto": "Deja sin efecto la decisión anterior.",
        "nulidad": "Anula la sentencia del inferior.",
        "mal_concedido": "Recurso mal concedido por el inferior.",
        "inadmisible_280": "Art. 280 como disposición DOMINANTE (raro; suele ir a desestima).",
        "inadmisible": "Inadmisible por causal distinta de art. 280 / Ac. 4.",
        "inadmisible_acordada_4": "Ac. 4/2007 como disposición DOMINANTE (raro).",
        "improcedente": "Recurso improcedente.",
        "desierto": "Recurso desierto (no fundado).",
        "caducidad": "Caducidad de instancia.",
        "desistimiento": "Desistimiento.",
        "sin_dispositivo": "No hay cláusula dispositiva extraíble.",
        "otro": "No clasificable en las anteriores.",
    },
    "queja_resultado": {
        "hace_lugar": "Queja concedida.",
        "desestima": "Queja desestimada.",
        "procedente": "Queja admisible y procedente.",
        "admisible": "Queja admitida.",
        "agreguese": "Orden «agréguese» (al expediente principal).",
        "rechaza": "Queja rechazada.",
        "abstracta": "Queja devenida abstracta.",
        "suspendida": "Trámite suspendido.",
        "desistida": "Queja desistida.",
        "inadmisible": "Queja inadmisible.",
        "nula": "Queja anulada.",
    },
    "tipo_cuestion_federal": {
        "cuestion_federal": "Cuestión federal en sentido estricto.",
        "arbitrariedad": "Arbitrariedad de sentencia.",
        "mixto": "Cuestión federal + arbitrariedad.",
    },
    "causa_inadmisibilidad": {
        "INADMISIBLE_SIN_CAUSAL_EXPLICITA": "Inadmisible sin causal explícita en el «por ello».",
        "ART_280": "Rechazado por art. 280 CPCCN (certiorari discrecional).",
        "INADMISIBLE_REMITE_DICTAMEN": "Inadmisibilidad resuelta por remisión al dictamen del PG.",
        "CUESTION_ABSTRACTA": "Rechazado por cuestión devenida abstracta.",
        "ACORDADA_4_2007": "Rechazado por incumplir requisitos formales de la Ac. 4/2007.",
        "FALTA_SENTENCIA_DEFINITIVA": "Falta sentencia definitiva (recaudo del REX).",
        "RESOLUCION_NO_RECURRIBLE": "La resolución impugnada no es recurrible.",
        "FALTA_FUNDAMENTACION_AUTONOMA": "Falta fundamentación autónoma.",
        "CADUCIDAD_INSTANCIA": "Caducidad de instancia.",
        "DESISTIMIENTO": "Desistimiento.",
        "FUERA_DE_TERMINO": "Recurso presentado fuera de término.",
        "DEPOSITO_PREVIO": "Vinculado al recaudo de depósito previo.",
    },
}


st.set_page_config(page_title="Retest M19 — codificación ciega", layout="wide")


@st.cache_data
def cargar_planilla(path_str: str) -> pd.DataFrame:
    return pd.read_csv(path_str, dtype=str).fillna("")


@st.cache_data
def indexar_bundles(dir_str: str) -> dict:
    """Mapea caso_id -> texto del fallo leyendo todos los .md de la carpeta."""
    idx, d = {}, Path(dir_str)
    if not d.exists():
        return idx
    for md in sorted(d.glob("*.md")):
        cid, buf = None, []
        for line in md.read_text(encoding="utf-8", errors="replace").splitlines():
            m = RE_HEADER.match(line.strip())
            if m:
                if cid is not None:
                    idx[cid] = "\n".join(buf).strip()
                cid, buf = m.group(1), []
            elif cid is not None:
                buf.append(line)
        if cid is not None:
            idx[cid] = "\n".join(buf).strip()
    return idx


def cod_cols(df: pd.DataFrame) -> list:
    return [c for c in df.columns if c.startswith("cod_")]


def cargar_salida(path: Path, col_id: str, cods: list) -> dict:
    if not path.exists():
        return {}
    prev = pd.read_csv(path, dtype=str).fillna("")
    out = {}
    for _, row in prev.iterrows():
        cid = row.get(col_id, "")
        if not cid:
            continue
        out[cid] = {c: row.get(c, "") for c in cods}
        out[cid]["nota"] = row.get("nota", "")
        out[cid]["_done"] = row.get("_done", "")
    return out


def guardar_salida(path: Path, col_id: str, cods: list, datos: dict) -> None:
    filas = []
    for cid, v in datos.items():
        fila = {col_id: cid}
        for c in cods:
            fila[c] = v.get(c, "")
        fila["nota"] = v.get("nota", "")
        fila["_done"] = v.get("_done", "")
        filas.append(fila)
    pd.DataFrame(filas, columns=[col_id] + cods + ["nota", "_done"]).to_csv(
        path, index=False, encoding="utf-8"
    )


# ----------------- arranque / guardas -----------------
if SALIDA.resolve() == PLANILLA_RETEST.resolve():
    st.error("SALIDA no puede ser la misma que PLANILLA_RETEST. Ajustá CONFIG.")
    st.stop()
if not PLANILLA_RETEST.exists():
    st.error(f"No encuentro `{PLANILLA_RETEST}`. Ajustá PLANILLA_RETEST en CONFIG.")
    st.stop()

df = cargar_planilla(str(PLANILLA_RETEST))
if COL_ID not in df.columns:
    st.error(f"La planilla no tiene `{COL_ID}`. Columnas: {list(df.columns)}")
    st.stop()

cods = cod_cols(df)
ids = df[COL_ID].tolist()
textos = indexar_bundles(str(BUNDLE_DIR))

if "datos" not in st.session_state:
    st.session_state.datos = cargar_salida(SALIDA, COL_ID, cods)
if "idx" not in st.session_state:
    hechos = {cid for cid, v in st.session_state.datos.items() if v.get("_done") == "1"}
    st.session_state.idx = next((i for i, c in enumerate(ids) if c not in hechos), 0)

datos = st.session_state.datos


# ----------------- sidebar -----------------
def esta_hecho(cid):
    return datos.get(cid, {}).get("_done") == "1"

n_hechos = sum(1 for c in ids if esta_hecho(c))
st.sidebar.metric("Progreso", f"{n_hechos} / {len(ids)}")
st.sidebar.progress(n_hechos / len(ids) if ids else 0.0)
st.sidebar.caption(f"codificar_retest v{__version__}")
if not textos:
    st.sidebar.warning(f"No indexé ningún .md en `{BUNDLE_DIR}`. Revisá BUNDLE_DIR.")
else:
    st.sidebar.caption(f"{len(textos)} casos indexados en bundles")

salto = st.sidebar.selectbox(
    "Ir a caso", options=list(range(len(ids))), index=st.session_state.idx,
    format_func=lambda i: f"{i+1}. {ids[i]}" + ("  ✓" if esta_hecho(ids[i]) else ""),
)
if salto != st.session_state.idx:
    st.session_state.idx = salto
    st.rerun()

with st.sidebar.expander("Reglas (CODEBOOK)"):
    st.caption(
        "(en blanco) = no aplica/null, sale del kappa.\n\n"
        "AMBIGUO = el OCR no deja decidir, sale del denominador.\n\n"
        "queja_resultado solo si es_queja=1. tipo_cuestion_federal solo en "
        "REX/queja. causa_inadmisibilidad solo en desestimaciones.\n\n"
        "Codificá con el CODEBOOK como está, sin criterio mejorado. "
        "Las fronteras difusas son subespecificación, no las 'arregles'."
    )


# ----------------- caso actual -----------------
i = st.session_state.idx
cid = ids[i]
prev = datos.get(cid, {})

st.subheader(f"Caso {i+1}/{len(ids)} — `{cid}`" + ("  ✓" if esta_hecho(cid) else ""))

col_txt, col_cod = st.columns([3, 2])

with col_txt:
    texto = textos.get(cid)
    if texto is None:
        st.warning(
            f"No encontré el texto de `{cid}` en los bundles. Agregá a "
            f"`{BUNDLE_DIR}` el .md que lo contiene (header `# {cid}`)."
        )
    else:
        st.text_area("Texto del fallo", texto, height=640, key=f"txt_{cid}")

with col_cod:
    st.markdown("#### Codificación")
    seleccion = {}
    for c in cods:
        campo = c[len("cod_"):]
        st.markdown(f"**{campo}**")
        st.caption(DEF_CAMPO.get(campo, ""))
        opciones = [BLANK] + list(VALORES.get(campo, {}).keys()) + [AMB]
        guardado = prev.get(c, "")
        actual = guardado if guardado else BLANK
        idx_prev = opciones.index(actual) if actual in opciones else 0
        seleccion[c] = st.selectbox(
            campo, opciones, index=idx_prev, key=f"{c}__{cid}",
            label_visibility="collapsed",
        )
        with st.expander("valores"):
            for v, d in VALORES.get(campo, {}).items():
                st.markdown(f"`{v}` — {d}")

    nota = st.text_area("Nota (override semántico, duda, etc.)",
                        prev.get("nota", ""), height=70, key=f"nota_{cid}")

    c1, c2, c3 = st.columns(3)
    anterior = c1.button("←", disabled=(i == 0), use_container_width=True)
    guardar = c2.button("Guardar", use_container_width=True)
    guardar_sig = c3.button("Guardar →", type="primary", use_container_width=True)

    if guardar or guardar_sig:
        reg = {c: ("" if seleccion[c] == BLANK else seleccion[c]) for c in cods}
        reg["nota"] = nota
        reg["_done"] = "1"
        datos[cid] = reg
        guardar_salida(SALIDA, COL_ID, cods, datos)
        st.session_state.datos = datos
        if guardar_sig and i < len(ids) - 1:
            st.session_state.idx = i + 1
        st.rerun()

    if anterior:
        st.session_state.idx = max(0, i - 1)
        st.rerun()

st.divider()
st.caption(
    "Ceguera: este codificador no abre csjn_casos.csv, ni la planilla original, "
    f"ni la clave. Solo lee {PLANILLA_RETEST} (ids) y los bundles (texto). "
    f"Escribe en {SALIDA}."
)
