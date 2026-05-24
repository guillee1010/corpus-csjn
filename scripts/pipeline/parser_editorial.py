"""
parser_editorial.py — Clasificador editorial por subtipos (H061)
================================================================

Módulo separado para detectar y clasificar las secciones editoriales
de cada tomo de Fallos CSJN: índices (partes, materias, legislación,
general), acordadas y discursos.

Migrado de la PoC validada en H060 (poc_subtipos_editorial.py).
Reemplaza `extraer_secciones_editoriales()` de parser.py.

Uso desde parser.py:
    from parser_editorial import clasificar_editorial

NOTA: el parseo de entries individuales del índice de partes lo hace
`construir_catalogo.py` (fuente canónica: output/catalogo/catalogo.csv).
Este módulo solo clasifica secciones por subtipo, no parsea entries.

Subtipos detectados:
    indice_partes       INDICE POR LOS NOMBRES DE LAS PARTES
    indice_materias     INDICE ALFABETICO POR MATERIAS
    indice_legislacion  INDICE DE LEGISLACION (*)
    indice_general      INDICE GENERAL (tabla de contenidos)
    acordadas           ACORDADAS DE LA CSJN / A C O R D A D A S...
    discurso            DISCURSOS

Detección:
    - Títulos-mojón: primera aparición de cada título conocido marca
      el inicio de la sección correspondiente.
    - Openers: determinan el subtipo del bloque inicial cuando no hay
      título-mojón previo (ej: letras espaciadas por OCR).
    - INDICE GENERAL truncado por puntos trailing: la última línea con
      `\\.{4,}\\s*$` + su número de página = fin del TOC. Sin puntos
      (Era 2, TOC degradado) → no trunca. Descarta boilerplate
      post-TOC y el acumulativo de 330.4.

Decisiones de diseño (H060):
    - Procesamiento per-archivo: no se toman índices acumulativos
      cross-volumen.
    - HOJA COMPLEMENTARIA descartada como marcador (aparece en cuerpo).
    - 330.4 anomalía documentada: único archivo con índice acumulativo.
"""

import re

# ── Títulos-mojón ─────────────────────────────────────────────────────
# Cada uno aparece ~1 vez por archivo y marca el INICIO de una sección.
# Orden: más específico primero (evitar match parcial).

TITLE_MARKERS = [
    ("indice_partes",      re.compile(
        r"^INDICE POR LOS NOMBRES DE LAS PARTES\s*$", re.I)),
    ("indice_materias",    re.compile(
        r"^INDICE ALFAB[EÉ]TICO POR MATERIAS", re.I)),
    ("indice_legislacion", re.compile(
        r"^INDICE DE LEGISLACI[OÓ]N\s*\(\*\)", re.I)),
    ("acordadas",          re.compile(
        r"^ACORDADAS DE LA CSJN\s*$", re.I)),
    ("discurso",           re.compile(
        r"^DISCURSOS\s*$", re.I)),
    ("indice_general",     re.compile(
        r"^INDICE GENERAL\s*$", re.I)),
]

# ── Openers: determinan el subtipo inicial del bloque ─────────────────
# Se chequean contra las primeras líneas no vacías.

OPENER_MARKERS = [
    ("discurso",           re.compile(r"^DISCURSOS\b", re.I)),
    ("acordadas",          re.compile(
        r"^A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S", re.I)),
    ("acordadas",          re.compile(
        r"^ACORDADAS\s+Y\s+RESOLUCIONES\s*$", re.I)),
    ("acordadas",          re.compile(
        r"^ACORDADAS DE LA CSJN\s*$", re.I)),
    ("indice_legislacion", re.compile(
        r"^INDICE DE LEGISLACI[OÓ]N", re.I)),
    ("indice_partes",      re.compile(
        r"^NOMBRES DE LAS PARTES\s*$", re.I)),
    ("indice_partes",      re.compile(
        r"^INDICE POR LOS NOMBRES", re.I)),
]

# ── Detección de fin del TOC (INDICE GENERAL) ────────────────────────
RE_TOC_DOTS = re.compile(r"\.{4,}\s*$")
RE_TOC_PAGE = re.compile(r"^\(?(?:\d+|[IVXLCDM]+)\)?\s*$")


# ── Funciones internas ───────────────────────────────────────────────

def _detectar_subtipo_inicial(lines, li, lf):
    """Subtipo de la primera sección, basado en las primeras líneas."""
    for i in range(li, min(li + 10, lf + 1)):
        s = lines[i].strip()
        if not s:
            continue
        for subtipo, rx in OPENER_MARKERS:
            if rx.match(s):
                return subtipo
        break  # solo la primera línea no vacía
    return "desconocido"


def _encontrar_mojones(lines, li, lf):
    """Primera aparición de cada título-mojón en el bloque."""
    found = {}  # subtipo -> linea
    for i in range(li, lf + 1):
        s = lines[i].strip()
        if not s:
            continue
        for subtipo, rx in TITLE_MARKERS:
            if subtipo not in found and rx.match(s):
                found[subtipo] = i
                break
    return found


def _detectar_fin_toc(lines, pos_ig, linea_fin):
    """
    Encuentra la última línea del TOC dentro de INDICE GENERAL.

    Regla: el TOC está compuesto por entries de la forma:
        Nombre de sección ......................
        (página_inicio)
    La última entry con puntos + su página = fin del TOC.
    Si no hay líneas con puntos (Era 2, TOC degradado), no trunca.
    """
    ultima_dots = None
    for i in range(pos_ig, min(linea_fin + 1, len(lines))):
        s = lines[i].strip()
        if s and RE_TOC_DOTS.search(s):
            ultima_dots = i

    if ultima_dots is None:
        return linea_fin

    fin = ultima_dots
    for i in range(ultima_dots + 1, min(linea_fin + 1, len(lines))):
        s = lines[i].strip()
        if not s or RE_TOC_PAGE.match(s):
            fin = i
        else:
            break

    return fin


# ── API pública ──────────────────────────────────────────────────────

def clasificar_editorial(lines, tomo, source_file, linea_inicio_editorial):
    """
    Clasifica el bloque editorial de un archivo en secciones con subtipos.

    Interfaz compatible con el antiguo `extraer_secciones_editoriales()`.

    Parámetros:
        lines: list[str] — todas las líneas del archivo.
        tomo: int — número de tomo.
        source_file: str — nombre del archivo (ej: LibroVol330.4.md).
        linea_inicio_editorial: int — primera línea a escanear
            (= linea_fin_real + 1 del último caso procesado).

    Retorna:
        list[dict] con columnas:
            tomo, source_file, subtipo, linea_ini, linea_fin, n_lineas, wc
    """
    n = len(lines)
    if linea_inicio_editorial >= n:
        return []

    # Guard: buscar primer marcador editorial (título-mojón u opener).
    # Compatibilidad con extraer_secciones_editoriales() que buscaba
    # primer_editorial antes de procesar. Salta texto residual post-caso.
    _all_rx = [rx for _, rx in TITLE_MARKERS] + [rx for _, rx in OPENER_MARKERS]
    linea_ini = None
    for k in range(linea_inicio_editorial, n):
        s = lines[k].strip()
        if s and any(rx.match(s) for rx in _all_rx):
            linea_ini = k
            break
    if linea_ini is None:
        return []

    linea_fin = n - 1

    # 1. Subtipo inicial (primeras líneas no vacías)
    tipo_ini = _detectar_subtipo_inicial(lines, linea_ini, linea_fin)

    # 2. Mojones (primera aparición de cada título conocido)
    mojones = _encontrar_mojones(lines, linea_ini, linea_fin)

    # 3. Posición de INDICE GENERAL (si existe)
    pos_ig = mojones.get("indice_general")

    # 4. Filtrar mojones espurios: títulos dentro del indice_general
    #    (ej: "Indice por los nombres de las partes" como entrada del TOC,
    #     a < 30 líneas del INDICE GENERAL).
    if pos_ig is not None:
        mojones_filtrados = {}
        for sub, pos in mojones.items():
            if sub == "indice_general":
                mojones_filtrados[sub] = pos
            elif pos < pos_ig:
                if (pos_ig - pos) > 30:
                    mojones_filtrados[sub] = pos
                # else: muy cerca de INDICE GENERAL → probable entrada del TOC
            # Títulos DESPUÉS de INDICE GENERAL: ignorar
        mojones = mojones_filtrados

    # 5. Construir boundaries ordenadas
    boundaries = []

    for sub, pos in sorted(mojones.items(), key=lambda x: x[1]):
        if pos <= linea_ini + 5 and sub == tipo_ini:
            continue  # ya cubierto por el tipo inicial
        if not boundaries and pos > linea_ini + 5:
            boundaries.append((linea_ini, tipo_ini))
        boundaries.append((pos, sub))

    if not boundaries:
        boundaries = [(linea_ini, tipo_ini)]
    elif boundaries[0][0] > linea_ini:
        boundaries.insert(0, (linea_ini, tipo_ini))

    # 6. Generar secciones
    secciones = []
    for idx, (li, subtipo) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            lf = boundaries[idx + 1][0] - 1
        else:
            lf = linea_fin

        # Truncar indice_general al último marcador fuerte de TOC
        if subtipo == "indice_general":
            lf_toc = _detectar_fin_toc(lines, li, lf)
            if lf_toc < lf:
                lf = lf_toc

        nn = lf - li + 1
        wc = sum(len(lines[j].split()) for j in range(li, min(lf + 1, n)))

        secciones.append({
            "tomo": tomo,
            "source_file": source_file,
            "subtipo": subtipo,
            "linea_ini": li,
            "linea_fin": lf,
            "n_lineas": nn,
            "wc": wc,
        })

    return secciones

