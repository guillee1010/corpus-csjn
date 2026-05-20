"""
CSJN Fallos Parser v17 (beta)
=============================
Cambios respecto a v16:

  1. Detector de sumarios-con-link (categoría editorial nueva).
     A partir del tomo 345, la CSJN publica algunos casos solo como sumario
     editorial con un link al fallo online, sin reproducir el fallo completo.
     Estos bloques tienen estructura: nombre de la causa, tema en mayúsculas,
     texto corto, y una nota al pie con el patrón "(*) Sentencia del [fecha].
     Ver en https://sj.csjn.gov.ar/" o "Ver fallo." (variantes por tomo).

     v17 detecta estos bloques con RE_SUMARIO_LINK y les asigna
     tipo_entrada = "sumario_con_link". Los campos analíticos (firma, outcome,
     considerando, wc_*) quedan vacíos porque el bloque no contiene un fallo
     parseable. La metadata estructural (linea_inicio, linea_fin, etc.) se
     conserva para permitir auditoría posterior.

     Motivación: en v16 estos casos quedaban como sin_firma + sin_dispositivo
     (76 casos) o, peor, heredaban firma del fallo anterior por solapamiento
     de páginas (28 casos). Ambos patrones contaminaban el análisis.

  2. Nueva columna tipo_entrada con valores "fallo" (default) o
     "sumario_con_link". Permite filtrar sumarios del análisis principal.

  3. Nueva columna wc_dictamen que exporta el word count del dictamen del
     Procurador detectado por la lógica ya existente (lineas_dictamen).
     Permite separar el aporte del dictamen del word count del fallo en sí
     para análisis estadístico. NOTA: la detección de dictamen no fue
     validada exhaustivamente; tratar wc_dictamen como aproximación hasta
     ronda de validación.

  Toda la lógica analítica restante es idéntica a v16. Solo se agregan
  el detector de sumarios y la exportación de wc_dictamen.

Uso:
  python csjnv17_beta.py --localizados fallos_localizados.csv \
                          --mapa mapa_paginas.csv \
                          --corpus ../../corpus \
                          --output ../../output/parser/csjn_casos.csv

Compatibilidad: schema extendido respecto a v16 (agrega tipo_entrada y
wc_dictamen al final). El resto de las columnas mantienen su orden y
semántica.
"""

import re
import csv
import json
import argparse
from pathlib import Path
from collections import Counter
from itertools import combinations

# ── Marcadores estructurales ──────────────────────────────────────────────────

RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I)
RE_FECHA_LINEA   = re.compile(r"^Buenos Aires[,]?\s+\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4}", re.I)
RE_FECHA_EXTRACT = re.compile(r"Buenos Aires[,]?\s+(\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4})", re.I)

# Por ello — dispositivo institucional. v8/v9 distingue entre usos como dispositivo
# vs como cláusula subordinada (argumental).
RE_POR_ELLO          = re.compile(r"^Por ello[,.]?\s*", re.I)
POR_ELLO_ARGUMENTAL  = {"concluyó", "concluyo", "estimo", "estimó", "considera",
                       "considero", "consideró", "entiende", "entendió",
                       "afirma", "afirmó", "sostiene", "sostuvo"}

# v11: detector AMPLIADO del dispositivo. En tomos viejos (329-340) un ~25% de
# los fallos no usan "Por ello" sino una de estas aperturas alternativas.
# Empíricamente verificadas en LibroVol329_3.md sobre 79 fallos sin "Por ello":
#   - "Por los fundamentos [y conclusiones del dictamen del señor Procurador]"  41/79
#   - "De conformidad con [lo dictaminado por el señor Procurador]"             27/79
#   - Residuales: "Por todo lo expuesto", "Por lo expuesto", "Atento a",
#     "En consecuencia"
# El typo "concusiones" (por "conclusiones") aparece en OCR de tomos 329-336.
# Cada regex es .match() sobre línea ya stripeada (sin anchor de fin).
RE_DISPOSITIVO_VARIANTES = [
    # nombre              # regex
    ("por_los_fund",      re.compile(r"^Por los fundamentos\s+y\s+conc[lu]+siones", re.I)),
    ("por_los_fund_simple", re.compile(r"^Por los fundamentos\b", re.I)),
    ("de_conformidad",    re.compile(r"^De conformidad con\b", re.I)),
    ("por_todo_lo_exp",   re.compile(r"^Por todo lo expuesto\b", re.I)),
    ("por_todo_ello",     re.compile(r"^Por todo ello\b", re.I)),
    ("por_lo_expuesto",   re.compile(r"^Por lo expuesto\b", re.I)),
    ("por_estas_razones", re.compile(r"^Por estas razones\b", re.I)),
    ("en_merito",         re.compile(r"^En m[ée]rito\s+a\s+lo\b", re.I)),
    ("en_su_merito",      re.compile(r"^En su m[ée]rito\b", re.I)),
    ("en_consecuencia",   re.compile(r"^En consecuencia\s*,?\s*\b", re.I)),
    ("atento_a",          re.compile(r"^Atento\s+(a\s+)?(que|lo|el)\b", re.I)),
    # ── H039: variantes confirmadas empíricamente (24 mejoras, 0 regresiones) ──
    ("por_lo_expresado",        re.compile(r"^Por lo expresado\b", re.I)),
    ("por_las_razones",         re.compile(r"^Por las razones\b", re.I)),
    ("por_las_consideraciones", re.compile(r"^Por las consideraciones\b", re.I)),
    ("oido_el",                 re.compile(r"^O[íi]dos?\s+(el|la|los|las)\b", re.I)),
    ("que_por_ello",            re.compile(r"^Que[,]?\s+por\s+ello\b", re.I)),
]

def detectar_apertura_dispositivo(stripped_line):
    """
    v11: devuelve (es_dispositivo: bool, tipo: str | None).

    es_dispositivo=True si la línea inicia el dispositivo del fallo. tipo
    identifica qué variante (para diagnóstico).

    Regla 'Por ello': solo cuenta como dispositivo si la palabra siguiente NO
    está en POR_ELLO_ARGUMENTAL (caso 'Por ello concluyó que...' es argumental,
    no dispositivo).

    v11 bugfix: el re.sub usa [,.]? (opcional) en vez de [,.] obligatorio,
    para que "Por ello concluyó..." (sin coma) sí entre por la rama
    argumental. v10 tenía esto roto: el regex de detección aceptaba "Por ello"
    sin coma pero el re.sub posterior no la limpiaba, dejando first_w='por' y
    saltándose la regla argumental.
    """
    if RE_POR_ELLO.match(stripped_line):
        rest = re.sub(r"^Por ello[,.]?\s*", "", stripped_line, flags=re.I)
        first_w = rest.split()[0].lower().rstrip(",;") if rest.split() else ""
        if first_w in POR_ELLO_ARGUMENTAL:
            return (False, None)
        return (True, "por_ello")
    for nombre, pat in RE_DISPOSITIVO_VARIANTES:
        if pat.match(stripped_line):
            return (True, nombre)
    return (False, None)

# Considerando — apertura del cuerpo argumental
RE_CONSIDERANDO  = re.compile(r"^Considerando\s*[:.]?\s*$", re.I)

# Dictamen del Procurador (a excluir del wc principal)
RE_DICT_HDR      = re.compile(
    r"^Dictamen\s+de(l)?\s+(la\s+)?Procura", re.I
)

# v17: sumario editorial con link al fallo online (no contiene fallo parseable).
# Variantes detectadas:
#   - Tomos 345-346: "(*) Sentencia del [fecha]. Ver en https://sj.csjn.gov.ar/..."
#   - Tomos 347-349: "(*) Sentencia del [fecha]. Ver fallo."
# La regex matchea ambas variantes en una sola línea stripeada.
RE_SUMARIO_LINK  = re.compile(
    r"^\(\*\)\s+Sentencia del .+? Ver (en https://sj\.csjn\.gov\.ar|fallo)",
    re.I
)

# Votos y disidencias — regex mejorado cubre todas las variantes:
# v10: agregar 'Vicepresidente', 'Presidente', tolerar OCR con
# capitalización mezclada (ej: 'caRLos FERnando RosEnkRantz' por OCR de
# tipografía decorativa). El regex original solo buscaba 'Señor[es]/Señora[s]'.
RE_VOTO_HDR  = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)
RE_DISID_HDR = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)

# Page headers a ignorar en búsqueda de case_name
RE_PAGE_HEADER   = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACIÓN|"
    r"DE JUSTICIA DE LA NACION|\d{2,6})\s*$", re.I)

# v18: Fix 1 — V1 como fuente primaria de case_name_cuerpo.
# Auditoría B (sesión XV) midió 3.859 hits = 67.3% del corpus con captura
# limpia. Reemplaza a find_case_name como fuente primaria. La búsqueda
# arranca desde apertura_rel hacia adelante para evitar el dictamen previo
# (donde están las citas doctrinales que rompían find_case_name viejo).

RE_VISTOS_LOS_AUTOS = re.compile(
    r'^\s*Vistos los autos:\s*([\u201C\u201D"\u2018\u2019\'])',
    re.IGNORECASE
)
COMILLAS_CIERRE = '\u201C\u201D"\u2018\u2019\''

def extraer_caratula_v1(bloque, apertura_rel, max_lineas=8):
    """
    v18: extrae la carátula desde el patrón V1 (`Vistos los autos: "X"`).
    Itera el bloque desde apertura_rel hacia adelante. En cuanto encuentra
    el marcador, reconstruye la carátula concatenando líneas hasta cerrar
    la comilla, manejando wrap por silabación. Devuelve la carátula sin
    las comillas, o "" si no hay V1.
    """
    inicio = apertura_rel if apertura_rel is not None else 0
    for i in range(inicio, len(bloque)):
        linea = bloque[i]
        m = RE_VISTOS_LOS_AUTOS.match(linea)
        if not m:
            continue
        comilla_apert = m.group(1)
        pos_apertura = linea.index(comilla_apert)
        acumulado = linea[pos_apertura + 1:].rstrip()
        m_cierre = re.search(f'[{COMILLAS_CIERRE}]', acumulado)
        if m_cierre:
            return acumulado[:m_cierre.start()]
        for j in range(i + 1, min(i + max_lineas, len(bloque))):
            sig = bloque[j].rstrip()
            if acumulado.endswith('\u00AD') or acumulado.endswith('-'):
                acumulado = acumulado.rstrip('\u00AD-') + sig.lstrip()
            else:
                acumulado = acumulado + ' ' + sig.lstrip()
            if re.search(f'[{COMILLAS_CIERRE}]', sig):
                pos_cierre = max(acumulado.rfind(c) for c in COMILLAS_CIERRE)
                return acumulado[:pos_cierre]
        return acumulado
    return ""

# Tomo desde nombre de archivo
RE_TOMO          = re.compile(r"LibroVol(\d+)")

# ── Outcomes ──────────────────────────────────────────────────────────────────

# v10: dos detectores, uno para considerando (1) y otro para dispositivo (2).
# La gran diferencia con v9: art. 280 y "acordada 4/2007" se detectan
# ANTES de mirar el dispositivo, porque ese es el patrón institucional real.

# Versión flexibilizada: tolera más variaciones del texto histórico
# (variantes "es inadmisible", "resulta inadmisible", "se declara inadmisible")
# y mayor distancia entre la palabra "inadmisible" y la mención al art. 280.
RE_280_CONSIDERANDO = re.compile(
    r"recurso\s+extraordinario.{0,150}?"
    r"(es|resulta|se\s+declara)\s+inadmisible"
    r".{0,150}?art[íi]?culo?\s*280\s+del\s+C[óo]digo\s+Procesal",
    re.I | re.DOTALL
)

# Variante alternativa: sólo busca "art. 280 CPCCN" en el considerando,
# sin requerir el contexto previo. Útil para captar variaciones que el
# patrón anterior no detecta.
RE_280_LIBRE = re.compile(
    r"\(\s*art[íi]?culo?\s*280\s+del\s+C[óo]digo\s+Procesal\s+Civil\s+y\s+Comercial",
    re.I
)

RE_ACORDADA_4_CONSIDERANDO = re.compile(
    r"art[íi]?culo?\s*1\s*°?\s*del\s+reglamento.{0,80}?acordada\s*4(/|\s+de\s+)2007",
    re.I | re.DOTALL
)

OUTCOME_PATTERNS_DISPOSITIVO = [
    # Ordenados por frecuencia empírica para short-circuit
    ("hace_lugar",      re.compile(r"\bse hace lugar\b", re.I)),
    ("desestima",       re.compile(r"\bse (lo |los )?desestiman?\b", re.I)),
    ("procedente",      re.compile(r"\bse declara procedente\b", re.I)),
    ("revoca",          re.compile(r"\bse revoca\b", re.I)),
    ("confirma",        re.compile(r"\bse confirma\b", re.I)),
    ("competencia",     re.compile(
        r"\bse declara (que (debe|resulta|deberá)|la competencia|incompetente)\b|"
        r"\bdeberá entender\b|\bresulta competente\b|\bdeclara su (in)?competencia\b",
        re.I)),
    ("originaria",      re.compile(
        r"^Por ello,.*se resuelve:\s*(I\.|1°|Primero)", re.I)),
    ("abstracto",       re.compile(
        r"\binoficioso\b|\babstracto\b|\bse declara abstracta?\b", re.I)),
    ("nulidad",         re.compile(r"\bse declara la nulidad\b", re.I)),
    ("desistimiento",   re.compile(r"\bse tiene por desistid[ao]\b", re.I)),
    ("mal_concedido",   re.compile(r"\bse (lo )?declara mal concedid[ao]\b", re.I)),
    # catch-all
    ("otro",            re.compile(r".*")),
]

def classify_outcome(por_ello_text: str, considerando_text: str = "") -> str:
    """
    v10: prioridad de outcomes:
      1. inadmisible_280 si está en considerando (regex estricto + libre)
      2. inadmisible_acordada_4 si está en considerando
      3. patrones de dispositivo (lo de v9)

    Esto es importante porque en CSJN el patrón institucional real del 280
    está en el considerando, no en el dispositivo. Sin esto, los 280 quedan
    clasificados como 'desestima' genérico.
    """
    if considerando_text:
        # Intentar primero el patrón estricto, después el libre como fallback
        if RE_280_CONSIDERANDO.search(considerando_text):
            return "inadmisible_280"
        if RE_280_LIBRE.search(considerando_text):
            return "inadmisible_280"
        if RE_ACORDADA_4_CONSIDERANDO.search(considerando_text):
            return "inadmisible_acordada_4"
    for label, pat in OUTCOME_PATTERNS_DISPOSITIVO:
        if pat.search(por_ello_text):
            return label
    return "otro"

# ── Jueces conocidos ──────────────────────────────────────────────────────────
# (idéntico a v9, copiado tal cual)

JUECES_CONOCIDOS = [
    # ── Banco actual / reciente ───────────────────────────────────────────────
    (re.compile(r"horacio\s+(daniel\s+)?rosatti", re.I),                     "Rosatti"),
    (re.compile(r"carlos\s+fernando\s+rosenkrantz", re.I),                   "Rosenkrantz"),
    (re.compile(r"ricardo\s+(luis\s+)?lorenzetti", re.I),                    "Lorenzetti"),
    (re.compile(r"juan\s+carlos\s+maqueda", re.I),                           "Maqueda"),
    (re.compile(r"elena\s+(i\.|inés)\s*(highton)?(?:\s+de\s+nolasco)?", re.I),"Highton de Nolasco"),
    (re.compile(r"manuel\s+jos[eé]?\s+garc[íi]a[\-\s]+mansilla", re.I),       "García Mansilla"),
    # ── Banco de 7 (2006-2014/2015) — titulares ──────────────────────────────
    # Estos son TITULARES, no conjueces. Para corpus pre-2016.
    # Los regex son tolerantes a mayúsculas/minúsculas (mayúsculas en libros viejos).
    (re.compile(r"e\.?\s*ra[úu]l\s+zaffaroni|eugenio\s+ra[úu]l\s+zaffaroni", re.I), "Zaffaroni"),
    (re.compile(r"enrique\s+santiago\s+petracchi|enrique\s+s\.?\s+petracchi", re.I), "Petracchi"),
    (re.compile(r"carmen\s+m\.?\s*argibay|carmen\s+mar[íi]a\s+argibay", re.I),"Argibay"),
    (re.compile(r"carlos\s+s\.?\s*fayt|carlos\s+santiago\s+fayt", re.I),      "Fayt"),
    # ── Jueces previos al banco de 7 (apariciones marginales pre-2006/aclaratorias) ─
    (re.compile(r"antonio\s+boggiano|^boggiano\b|—\s*boggiano\s*—", re.I),    "Boggiano"),
    (re.compile(r"augusto\s+c[ée]sar\s+belluscio", re.I),                     "Belluscio"),
    (re.compile(r"guillermo\s+a\.?\s*f\.?\s*l[óo]pez", re.I),                 "López"),
    (re.compile(r"adolfo\s+roberto\s+v[áa]zquez", re.I),                      "Vázquez"),
    (re.compile(r"juli[oa]\s+s\.?\s*nazareno", re.I),                         "Nazareno"),
    # ── Conjueces históricos frecuentes (corpus 2006+) ───────────────────────
    (re.compile(r"juan\s+carlos\s+rodr[íi]guez\s+basavilbaso", re.I),         "Rodríguez Basavilbaso (conjuez)"),
    (re.compile(r"luis\s+c[ée]sar\s+otero", re.I),                            "Otero (conjuez)"),
    (re.compile(r"gabriel\s+(rub[ée]n|r\.?)\s+cavallo", re.I),                "Cavallo (conjuez)"),
    # ── Conjueces frecuentes (heredados v9) ──────────────────────────────────
    (re.compile(r"mariano\s+borinsky", re.I),                                "Borinsky (conjuez)"),
    (re.compile(r"alejandro\s+s\.?\s*catania", re.I),                        "Catania (conjuez)"),
    (re.compile(r"juan\s+carlos\s+gemignani", re.I),                         "Gemignani (conjuez)"),
    (re.compile(r"daniel\s+a\.?\s*petrone", re.I),                           "Petrone (conjuez)"),
    (re.compile(r"angela\s+e\.?\s*ledesma", re.I),                           "Ledesma (conjuez)"),
    (re.compile(r"diego\s+g\.?\s*barroetave[ñn]a", re.I),                    "Barroetaveña (conjuez)"),
    (re.compile(r"gustavo\s+m\.?\s*hornos", re.I),                           "Hornos (conjuez)"),
    (re.compile(r"javier\s+leal\s+de\s+ibarra", re.I),                       "Leal de Ibarra (conjuez)"),
    (re.compile(r"liliana\s+(catucci|cattucci)", re.I),                      "Catucci (conjuez)"),
    (re.compile(r"eduardo\s+r\.?\s*riggi", re.I),                            "Riggi (conjuez)"),
    (re.compile(r"guillermo\s+yacobucci", re.I),                             "Yacobucci (conjuez)"),
    (re.compile(r"ana\s+mar[íi]a\s+figueroa", re.I),                         "Figueroa (conjuez)"),
    (re.compile(r"carlos\s+a\.?\s*mahiques", re.I),                          "Mahiques (conjuez)"),
    # ── Conjueces B063 (H043) ───────────────────────────────────────────────
    (re.compile(r"mar[íi]a\s+susana\s+najurieta", re.I),                    "Najurieta (conjuez)"),
    (re.compile(r"roc[íi]o\s+alcal[áa]", re.I),                            "Alcalá (conjuez)"),
    (re.compile(r"jorge\s+eduardo\s+mor[áa]n\.?", re.I),                   "Morán (conjuez)"),
    (re.compile(r"mirta\s+(d\.?|delia)\s+tyden(?:\s+de\s+skanata)?", re.I), "Tyden de Skanata (conjuez)"),
    (re.compile(r"juan\s+carlos\s+poclava\s+lafuente", re.I),              "Poclava Lafuente (conjuez)"),
    (re.compile(r"carlos\s+(m\.?|mart[íi]n)\s+pereyra\s+gonz[áa]lez", re.I), "Pereyra González (conjuez)"),
    (re.compile(r"jorge\s+ferro", re.I),                                    "Ferro (conjuez)"),
    (re.compile(r"antonio\s+pacilio", re.I),                                "Pacilio (conjuez)"),
    (re.compile(r"[áa]ngel\s+a\.?\s*arga[ñn]araz", re.I),                  "Argañaraz (conjuez)"),
    (re.compile(r"rita\s+(mill|m\.?)\s+de\s+pereyra", re.I),               "Mill de Pereyra (conjuez)"),
]

# Ruido OCR (segmentos que no son nombres). Incluimos apellidos de jueces
# para que no se cuenten como "desconocidos" cuando aparecen en otros contextos.
RUIDO_FIRMA = {
    "buenos aires", "vistos", "considerando", "por ello", "notifíquese",
    "archívese", "fdo", "ante mí", "ante mi", "rosenkrantz —",
    "lorenzetti", "rosatti", "maqueda", "highton",
    "petracchi", "zaffaroni", "argibay", "fayt", "boggiano",
    "belluscio", "lópez", "vázquez", "nazareno",
}

# ── Calificadores ─────────────────────────────────────────────────────────────

RE_CALIFICADOR = re.compile(
    r"\(\s*(en\s+disidencia|seg[úu]n\s+su\s+voto|por\s+su\s+voto)"
    r"(\s+parcial)?\s*\)",
    re.I
)

# ── Búsqueda de case_name ─────────────────────────────────────────────────────

def find_case_name(lines, apertura_idx, max_back=15, max_back_fallback=60):
    for d in range(1, max_back + 1):
        idx = apertura_idx - d
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if not candidate or RE_PAGE_HEADER.match(candidate):
            continue
        if "c/" in candidate:
            return candidate
    for d in range(1, max_back_fallback + 1):
        idx = apertura_idx - d
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if not candidate or RE_PAGE_HEADER.match(candidate):
            continue
        if "c/" in candidate or "s/" in candidate:
            return candidate
    return ""

# ── Tribunal de origen ────────────────────────────────────────────────────────

# v11: ampliar marcadores. "Tribunal de origen" es el único frecuente en el
# corpus auditado (tomo 329 = 156 ocurrencias), pero los otros tres se agregan
# preventivamente para tomos donde el formato pueda variar.
# "Tribunales que intervinieron con anterioridad" NO se incluye como marcador
# de tribunal de origen porque introduce instancias INFERIORES intermedias,
# no la instancia recurrida; pero su presencia se usa en la detección
# positiva de is_originaria como señal de NO-originario.
RE_TRIB_ORIG = re.compile(
    r"^(?:Tribunal|Juzgado|C[áa]mara)\s+de\s+origen\s*:\s*(.*)$",
    re.I,
)
RE_TRIB_INTERVINIENTE = re.compile(
    r"^Tribunales?\s+que\s+intervin",
    re.I,
)

def find_tribunal_origen(lines, idx_inicio, idx_fin):
    """
    v11: además de la línea con 'Tribunal de origen:', si la línea no tiene
    contenido después del ':' (marcador suelto, contenido en la línea
    siguiente), tomar la siguiente línea como tribunal.
    """
    for k in range(idx_inicio, min(idx_fin, len(lines))):
        m = RE_TRIB_ORIG.match(lines[k].strip())
        if m:
            tribunal = m.group(1).strip().rstrip(".")
            # v11: si el marcador está vacío (ej: 'Tribunal de origen:' sin
            # contenido en la misma línea), tomar la línea siguiente entera.
            if not tribunal and k + 1 < len(lines):
                next_line = lines[k + 1].strip()
                if next_line and not RE_PAGE_HEADER.match(next_line):
                    tribunal = next_line.rstrip(".")
                    return tribunal
            # Comportamiento original: continuación natural en línea siguiente
            if k + 1 < len(lines):
                next_line = lines[k + 1].strip()
                if (next_line and not next_line.startswith("Tribunal")
                    and not next_line.startswith("Juzgado")
                    and not next_line.startswith("Cámara")
                    and not RE_PAGE_HEADER.match(next_line)
                    and len(next_line) < 100
                    and not next_line.endswith(".")
                    and next_line[0].islower()):
                    tribunal += " " + next_line.rstrip(".")
            return tribunal
    return "SIN_TRIBUNAL_ORIGEN"

def hay_tribunal_interviniente(lines, idx_inicio, idx_fin):
    """v11: señal auxiliar — el caso vino de instancias inferiores."""
    for k in range(idx_inicio, min(idx_fin, len(lines))):
        if RE_TRIB_INTERVINIENTE.match(lines[k].strip()):
            return True
    return False

# ── Firma: collect_firma_lines + parse_firma ──────────────────────────────────

_RE_FIRMA_COMPLETA = re.compile(
    r"(?:rosatti|rosenkrantz|lorenzetti|maqueda|highton(?:\s+de\s+nolasco)?|nolasco|garc.a.mansilla|mansilla|zaffaroni|petracchi|argibay|fayt|boggiano|belluscio|l.pez|v.zquez|nazareno|rodr.guez\s+basavilbaso|basavilbaso|otero|cavallo|borinsky|catania|gemignani|petrone|ledesma|barroetave.a|hornos|leal\s+de\s+ibarra|catucci|cattucci|riggi|yacobucci|figueroa|mahiques|najurieta|alcal.a?|mor[áa]n|tyden(?:\s+de\s+skanata)?|skanata|poclava\s+lafuente|lafuente|pereyra\s+gonz.lez|ferro|pacilio|arga.araz|mill\s+de\s+pereyra)"
    r"(?:\s*\((?:en\s+disidencia|seg[uú]n\s+su\s+voto)(?:\s+parcial)?\))?\s*\.\s*$",
    re.I
)

def collect_firma_lines(bloque, idx_start, max_lines=None):
    """Junta lineas de firma. H042 fix B055 v3.

    - Techo = len(bloque) (bloque acotado por catalogo/mapa).
    - Guarda: cuando texto acumulado termina en apellido conocido
      + calificador opcional + punto -> firma podria estar completa
      -> aplicar guarda estricta. Si no -> seguir con breaks.
    - Tolera 1 linea vacia intercalada si la siguiente parece firma.
    """
    techo = len(bloque) if max_lines is None else min(idx_start + max_lines, len(bloque))
    firma_lines = []
    started = False

    def es_continuacion_firma(s):
        if any(p.search(s) for p, _ in JUECES_CONOCIDOS):
            return True
        if "—" in s or " - " in s or "–" in s:
            return True
        if RE_CALIFICADOR.search(s):
            return True
        return False

    for k in range(idx_start, techo):
        line = bloque[k].strip()
        if not line:
            if started:
                next_firma = False
                for j in range(k + 1, min(k + 3, techo)):
                    nxt = bloque[j].strip()
                    if not nxt:
                        continue
                    if es_continuacion_firma(nxt):
                        next_firma = True
                    break
                if next_firma:
                    continue
                break
            continue
        if not started:
            if any(p.search(line) for p, _ in JUECES_CONOCIDOS):
                started = True
                firma_lines.append(line)
            continue
        # Breaks estructurales
        if RE_PAGE_HEADER.match(line) or line.startswith("Recurso de"):
            break
        if RE_VOTO_HDR.match(line) or RE_DISID_HDR.match(line):
            break
        if line.startswith("Tribunal de origen") or line.startswith("Tribunal que"):
            break
        # Guarda: texto acumulado termina en apellido conocido + punto?
        firma_so_far = " ".join(firma_lines)
        if _RE_FIRMA_COMPLETA.search(firma_so_far):
            if not es_continuacion_firma(line):
                break
        firma_lines.append(line)
    return " ".join(firma_lines)

def parse_firma(firma_raw):
    """Parsea firma multi-línea: detecta jueces conocidos y calificadores.

    v10 fix: la asignación de calificador busca el calificador entre
    el nombre del juez y el siguiente nombre/separador, no en una ventana
    fija de 80 caracteres. Esto evita asignar mal el calificador cuando
    aparece junto a un juez intermedio en una firma como
    'Rosatti — Rosenkrantz (según su voto) — Lorenzetti'.
    """
    jueces_out = []
    desconocidos = []
    voting_pattern = "unanime"
    has_voto    = False
    has_disid   = False

    # 1. Encontrar todas las ocurrencias de jueces y sus posiciones
    matches = []
    for pat, nombre in JUECES_CONOCIDOS:
        for m in pat.finditer(firma_raw):
            matches.append((m.start(), m.end(), nombre))
    # Ordenar por posición y eliminar overlaps (preferir el primer match)
    matches.sort()
    matches_dedup = []
    last_end = -1
    for ini, fin, nombre in matches:
        if ini < last_end:
            continue
        matches_dedup.append((ini, fin, nombre))
        last_end = fin

    # 2. Para cada juez, buscar calificador SOLO entre su fin y el siguiente inicio
    for i, (ini, fin, nombre) in enumerate(matches_dedup):
        if i + 1 < len(matches_dedup):
            limite_busqueda = matches_dedup[i + 1][0]
        else:
            limite_busqueda = len(firma_raw)
        ventana = firma_raw[fin:limite_busqueda]
        cm = RE_CALIFICADOR.search(ventana)
        calificador = None
        if cm:
            cal_text = cm.group(1).lower()
            if "disidencia" in cal_text:
                calificador = "en disidencia"
                has_disid   = True
            elif "seg" in cal_text:
                calificador = "según su voto"
                has_voto    = True
            elif "por" in cal_text:
                calificador = "por su voto"
                has_voto    = True
        jueces_out.append({
            "nombre":      nombre,
            "calificador": calificador,
            "conocido":    True,
        })

    # 3. Ruido / desconocidos: segmentos que parecen nombres pero no matchearon
    nombres_jueces = {j["nombre"].split(" (")[0].lower() for j in jueces_out}
    for token in re.findall(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\.\-]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\.\-]+){1,3}", firma_raw):
        token_l = token.lower()
        if any(r in token_l for r in RUIDO_FIRMA):
            continue
        if any(j in token_l for j in nombres_jueces):
            continue
        if len(token) < 6:
            continue
        desconocidos.append(token)

    if has_voto and has_disid:
        voting_pattern = "mixed"
    elif has_voto:
        voting_pattern = "segun_su_voto"
    elif has_disid:
        voting_pattern = "disidencia"
    elif jueces_out:
        voting_pattern = "unanime"
    else:
        voting_pattern = "sin_firma"

    return {
        "jueces":         jueces_out,
        "voting_pattern": voting_pattern,
        "desconocidos":   desconocidos,
    }

# ── NUEVO v10: extraer texto del considerando + texto de cada voto individual ─

def extraer_considerando(bloque, por_ello_idx, lineas_dictamen):
    """
    Extrae el texto del considerando: desde 'Considerando' hasta 'Por ello'.
    Excluye líneas que forman parte del dictamen embebido.
    Returns: string con texto unificado.
    """
    inicio_cons = None
    for k, ln in enumerate(bloque):
        if k in lineas_dictamen:
            continue
        if RE_CONSIDERANDO.match(ln.strip()):
            inicio_cons = k
            break
    if inicio_cons is None:
        # Fallback: a veces no hay marcador "Considerando:" explícito,
        # pero el considerando empieza igual. Tomamos desde apertura hasta
        # por_ello_idx como aproximación.
        inicio_cons = 0
    fin_cons = por_ello_idx if por_ello_idx is not None else len(bloque)
    lineas = [bloque[k].strip() for k in range(inicio_cons, fin_cons)
              if k not in lineas_dictamen]
    return " ".join([ln for ln in lineas if ln])

def extraer_textos_votos(bloque, posiciones_marcadores):
    """
    Para cada voto/disidencia individual, extrae el texto del bloque.
    posiciones_marcadores: lista de (k_inicio, juez_nombre, tipo)
        donde tipo ∈ {'voto', 'disidencia'}
    Returns: dict {juez_nombre: texto_voto}
    """
    resultado = {}
    if not posiciones_marcadores:
        return resultado
    # Ordenar por línea de inicio
    marcadores = sorted(posiciones_marcadores, key=lambda x: x[0])
    for i, (k_ini, juez, tipo) in enumerate(marcadores):
        # Fin: línea de inicio del próximo marcador, o fin del bloque
        if i + 1 < len(marcadores):
            k_fin = marcadores[i + 1][0]
        else:
            k_fin = len(bloque)
        # Extraer texto entre k_ini+1 y k_fin (el k_ini es el header del voto)
        texto = " ".join([bloque[k].strip() for k in range(k_ini, k_fin)
                          if bloque[k].strip()])
        resultado[juez] = texto
    return resultado

def detectar_juez_en_voto_header(linea):
    """
    Dado un header como 'Voto del Señor Ministro Doctor Don Ricardo Luis
    Lorenzetti', detecta cuál juez es. Devuelve None si no matchea.
    """
    for pat, nombre in JUECES_CONOCIDOS:
        if pat.search(linea):
            return nombre
    return None

# ── NUEVO v11: detección positiva de competencia originaria ──────────────────

# Señales internas en el cuerpo del fallo
RE_COMPETENCIA_ORIGINARIA = re.compile(
    r"competencia\s+originaria\s+(de\s+(esta\s+)?Corte|del\s+Tribunal|de\s+la\s+Corte\s+Suprema)",
    re.I,
)
RE_ART_117_CN = re.compile(
    r"art[íi]?culo?s?\s*117\s+(de\s+la\s+)?Constituci[óo]n\s+Nacional",
    re.I,
)
# "en forma originaria", "instancia originaria", "originariamente"
RE_FORMA_ORIGINARIA = re.compile(
    r"\b(en\s+forma\s+originaria|instancia\s+originaria|originariamente\s+ante)\b",
    re.I,
)

# Señales en case_name
# - "Originario" con O mayúscula (encabezados tipo "M. 466. XXIV. Originario")
RE_CN_ORIGINARIO = re.compile(r"\bOriginario\b")
# - patrón de demanda contra provincia o Estado Nacional (heurística amplia)
RE_CN_DEMANDA_ESTADO = re.compile(
    r"c/\s+(?:la\s+)?Provincia\s+de\s+|"
    r"c/\s+Estado\s+Nacional|"
    r",\s*Provincia\s+de\s+\w+,?\s+c/|"  # "Buenos Aires, Provincia de, c/"
    r"Provincia\s+de\s+\w+\s+c/",
    re.I,
)

def es_originaria(case_name, considerando_text, por_ello_text):
    """
    v11: detección positiva de competencia originaria.

    Criterio AMPLIO: incluye fallos donde la Corte declina la competencia
    originaria (porque el caso fue presentado como originario, aunque la Corte
    rechace). Decisión metodológica del usuario.

    Retorna True si CUALQUIERA de estas señales aparece:
      1. "competencia originaria de esta Corte" en el texto del fallo
      2. Referencia al art. 117 CN en el texto
      3. "Originario" como marcador en el case_name
      4. Patrón de demanda contra Provincia o Estado Nacional en case_name
         CON al menos una mención adicional de competencia o art. 117

    El criterio (4) requiere doble señal porque el case_name por sí solo
    no garantiza originaria: hay quejas contra provincias que llegan en
    apelación y NO son originarios.
    """
    cuerpo = (considerando_text or "") + " " + (por_ello_text or "")

    # Señal fuerte 1: competencia originaria mencionada explícitamente
    if RE_COMPETENCIA_ORIGINARIA.search(cuerpo):
        return True
    # Señal fuerte 2: art. 117 CN
    if RE_ART_117_CN.search(cuerpo):
        return True
    # Señal fuerte 3: "Originario" en case_name (encabezado oficial del expediente)
    if case_name and RE_CN_ORIGINARIO.search(case_name):
        return True
    # Señal fuerte 4: forma originaria mencionada
    if RE_FORMA_ORIGINARIA.search(cuerpo):
        return True
    # Señal compuesta: provincia/Estado en case_name + corroboración en cuerpo
    # (deliberadamente NO se usa case_name solo como señal — demasiados falsos
    # positivos, p.ej. quejas contra el fisco provincial que vienen en apelación)
    return False

# ── NUEVO v12: clasificación de votos individuales ────────────────────────
# ── Tipo B: art. 280 CPCCN ────────────────────────────────────────────────────
# Señal definitoria: mención al art. 280 como base del rechazo. La regex
# original del parser (RE_280_LIBRE) requiere la apertura de paréntesis,
# pero en algunos votos individuales falta; ampliamos para tolerar las dos
# formas. El umbral de wc_voto se calibra desde los ejemplos 1 y 2 (89 y 55
# palabras): empíricamente los rechazos formulaicos están por debajo de 200
# palabras. El requisito is_merit_decision=0 es informativo, no duro: en
# fallos donde la mayoría rechaza por 280 pero algún ministro firma por su
# voto sin más, is_merit del caso será 0.

RE_TIPO_B_280 = re.compile(
    r"(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal",
    re.I,
)

# Variantes residuales: "art. 280", "art. 280 CPCCN" sin "del Código Procesal"
RE_TIPO_B_280_ABREV = re.compile(
    r"\b(?:art\.?|art[íi]culo)\s*280\b(?!\s+del\s+r[ée]gimen)",
    re.I,
)

# ── Tipo C: adhesión parcial con divergencia desde considerando N ────────────
# Señales arquetípicas extraídas del Ejemplo 5 (Lorenzetti, "coincide con el
# del voto de la mayoría con exclusión del considerando 4°") y del Ejemplo 6
# (Argibay, "coincide con los considerandos 1° y 2° del voto de la mayoría.
# 3°) Que..."). Dos patrones complementarios:
#
#   (a) "exclusión del considerando N"  / "excepción del considerando N"
#       Modelo: voto coincide con TODO menos un considerando explícito.
#       El considerando N se redacta a continuación de manera divergente.
#
#   (b) "coincide con los considerandos N1 y N2"  (sin "exclusión")
#       Modelo: voto adhiere hasta cierto punto y de ahí en más redacta
#       considerandos propios. El primer considerando NO citado es el
#       punto de divergencia. En el Ejemplo 6 cita "1° y 2°" y la
#       divergencia empieza en el 3°.

# Patrón (a) — exclusión / excepción explícita
RE_TIPO_C_EXCLUSION = re.compile(
    r"(coincide|comparte|adhiere|concuerda)\b"
    r".{0,80}?"
    r"(con\s+(?:la\s+)?(?:exclusi[óo]n|excepci[óo]n)\s+del?\s+"
    r"considerando\s+(\d+)\s*[°ºª]?)",
    re.I | re.DOTALL,
)

# Patrón (b) — adhesión hasta considerando N (inclusivo)
# Captura "coincide con los considerandos 1°, 2° y 3°" o "1° y 2°".
# El número capturado es el ÚLTIMO considerando adherido; la divergencia
# empieza en N+1. Construido para tolerar enumeraciones cortas.
RE_TIPO_C_HASTA = re.compile(
    r"(coincide|comparte|adhiere|concuerda)\b"
    r".{0,40}?"
    r"con\s+(?:los\s+)?considerandos?\s+"
    r"((?:\d+\s*[°ºª]?\s*[,y]?\s*)+)",
    re.I | re.DOTALL,
)

# Patrón (c) — variante "adhiere hasta el considerando N"
RE_TIPO_C_ADHIERE_HASTA = re.compile(
    r"(adhiere|coincide|comparte)\b"
    r".{0,40}?"
    r"hasta\s+el\s+considerando\s+(\d+)\s*[°ºª]?",
    re.I | re.DOTALL,
)

# ── Tipo A: remisión al dictamen del Procurador ──────────────────────────────
# Variantes empíricas, ordenadas por frecuencia esperada. Construidas para
# distinguir A puro (la remisión es el único o el principal fundamento) de
# A mixto (remisión al dictamen sobre algunos puntos + argumentos propios
# sobre otros). El Ejemplo 4 (Lorenzetti+Argibay) es A mixto: remite al
# dictamen para reseñar las cuestiones (acápites I, II y III) y luego
# argumenta sobre el fondo apoyándose en un precedente. Para nuestro
# clasificador AMBOS son tipo A — la subcategoría puro/mixto se puede
# inferir post-hoc desde wc_voto y desde la presencia de "Fallos:" pero no
# afecta la clasificación principal.

# Patrón principal: remisión explícita al dictamen como fundamento
RE_TIPO_A_REMISION_DICTAMEN = re.compile(
    r"(?:"
        # "por los fundamentos [y conclusiones] del dictamen"
        r"por\s+los\s+fundamentos\s+(?:y\s+conc[lu]+siones\s+)?"
            r"(?:expuestos\s+en\s+el\s+|del\s+)?dictamen"
        r"|"
        # "de conformidad con lo dictaminado"
        r"de\s+conformidad\s+con\s+lo\s+dictamin"
        r"|"
        # "se remite al dictamen" / "cabe remitirse al dictamen"
        r"(?:se\s+remite|cabe\s+remitirse|corresponde\s+remitir(?:se)?)\s+"
            r"(?:a\s+(?:los\s+)?(?:fundamentos\s+(?:y\s+conclusiones\s+)?"
            r"(?:expuestos\s+(?:en\s+el\s+)?|del\s+)?)?dictamen|al\s+dictamen)"
        r"|"
        # "comparte / comparten los fundamentos [y conclusiones] del dictamen"
        r"comparte[ns]?\s+(?:los\s+)?fundamentos\s+"
            r"(?:y\s+conc[lu]+siones\s+)?(?:expuestos\s+(?:en\s+el\s+)?|del\s+)?dictamen"
        r"|"
        # "concuerda / concuerdan con el dictamen"
        r"concuerd[ao]n?\s+(?:sustancialmente\s+)?con\s+(?:lo\s+expuesto\s+en\s+)?"
            r"(?:el\s+)?dictamen"
        r"|"
        # "al [que/cual] cabe remitir(se)" — referencia anafórica al dictamen
        # Sólo válida si "dictamen" aparece en una ventana corta previa,
        # condición que se chequea en el código.
        r"al\s+(?:que|cual)\s+cabe\s+remitir(?:se)?"
    r")",
    re.I | re.DOTALL,
)

# Para detectar A "anafórico" (Ejemplo 4: "...reseñados apropiadamente en
# el dictamen del señor Procurador Fiscal subrogante (acápites I, II y III),
# al que cabe remitirse..."), validamos que la palabra "dictamen" aparezca
# en una ventana de 200 caracteres previa al match anafórico.
RE_DICTAMEN_MENCION = re.compile(r"\bdictamen\b", re.I)

# ── Tipo E: remisión a voto propio anterior o a precedente ──────────────────
# Señales: cita de "Fallos: NNN:NNN" como fundamento principal, o frases
# del tipo "resulta aplicable lo resuelto en la causa", "remite a los
# fundamentos de su voto en", "criterio sostenido en". El Ejemplo 3 (Fayt)
# es el arquetipo: "Que al caso resulta aplicable, en lo pertinente, lo
# resuelto por el Tribunal en la causa 'Verbitsky' (Fallos: 328:1146,
# disidencia parcial del juez Fayt) a cuyos fundamentos y conclusiones
# corresponde remitir en razón de brevedad."
#
# Atención: la cita de "Fallos:" sola NO basta para Tipo E. Casi todos los
# fallos citan precedentes. Lo característico de E es que la cita es el
# fundamento PRINCIPAL del voto: aparece en los primeros considerandos,
# acompañada de fórmulas de remisión ("a cuyos fundamentos corresponde
# remitir", "resulta aplicable lo resuelto"). Distinguimos E "fuerte" (con
# fórmula de remisión + cita) de E "débil" (sólo cita), y sólo el primero
# califica como Tipo E. El segundo cae en otra categoría.

RE_TIPO_E_REMISION_PRECEDENTE = re.compile(
    r"(?:"
        # "resulta aplicable lo resuelto en"
        r"resulta(?:n)?\s+aplicables?\s+(?:al\s+caso\s+)?(?:en\s+lo\s+pertinente,?\s+)?"
            r"(?:lo\s+resuelto|los?\s+(?:argumentos|fundamentos|criterios?))"
        r"|"
        # "a cuyos fundamentos [y conclusiones] corresponde remitir(se)"
        r"a\s+cuyos\s+fundamentos\s+(?:y\s+conclusiones\s+)?"
            r"(?:corresponde|cabe)\s+remitir(?:se)?"
        r"|"
        # "remite a los fundamentos de su voto en"
        r"(?:se\s+)?remite\s+a\s+(?:los\s+fundamentos\s+(?:de\s+su\s+voto|"
            r"expuestos)\s+en|lo\s+resuelto\s+en)"
        r"|"
        # "criterio sostenido en" / "doctrina sentada en"
        r"(?:criterio\s+sostenido|doctrina\s+sentada|conforme\s+lo\s+resuelto)\s+en\s+(?:la\s+)?(?:causa|los\s+autos|Fallos)"
    r")",
    re.I | re.DOTALL,
)

# Cita de "Fallos: NNN:NNN" — se usa como señal corroborante para E
RE_FALLOS_CITA = re.compile(r"\bFallos\s*:\s*\d{2,3}\s*:\s*\d+", re.I)

# ── Tipo D: concurrencia sustantiva independiente ────────────────────────────
# Por descarte: NO matchea ninguna fórmula de adhesión / remisión y exhibe
# la estructura de un voto autónomo (considerandos numerados desde 1°,
# desarrollo extenso). El umbral de 1500 palabras se calibra desde los
# ejemplos 7 (6.026 palabras) y 8 (6.666 palabras) más la asimetría con C
# (los ejemplos 5 y 6 de C tienen 1.398 y 153 palabras). 1500 separa
# razonablemente C de D pero el discriminante real es la presencia/ausencia
# de fórmulas de adhesión, no el wc.

# Detección de "Considerando: 1°)" como inicio de redacción autónoma. Si el
# voto empieza así (o en esa ventana inicial aparece "1°)") es señal de
# estructura D. Tolerante al header del voto que precede.
RE_CONSIDERANDO_NUMERADO_1 = re.compile(
    r"Considerando\s*:\s*1\s*[°ºª]\s*\)",
    re.I,
)

# ── Función principal ─────────────────────────────────────────────────────────

def clasificar_tipo_voto(texto_voto, wc_voto, is_merit_decision):
    """
    Clasifica un voto individual ("según su voto" / "por su voto" /
    disidencia parcial) en uno de los cinco tipos definidos en el marco
    teórico de la tesis.

    Parámetros
    ----------
    texto_voto : str
        Texto del voto tal como lo extrae `extraer_textos_votos` en
        csjnv11.py: una sola línea con el header del voto seguido del
        cuerpo, sin saltos de línea internos.
    wc_voto : int
        Word count del voto (calculado en el loop principal con la regex
        \\b\\w+\\b).
    is_merit_decision : int | bool
        Flag del CASO (1 si outcome ∈ MERIT_OUTCOMES). Señal auxiliar.

    Returns
    -------
    dict con tres claves:
        tipo_voto_sep : str    "A" | "B" | "C" | "D" | "E" | "indeterminado"
        fragmenta_ratio : bool | str   True | False | "parcial"
        punto_divergencia : str | None  "considerando N" | "dispositivo" | None
    """
    if not texto_voto or not texto_voto.strip():
        return {
            "tipo_voto_sep":      "indeterminado",
            "fragmenta_ratio":    False,
            "punto_divergencia":  None,
        }

    # Trabajamos sobre los primeros 4000 caracteres para los matchers de
    # adhesión / remisión: las fórmulas características aparecen siempre al
    # inicio del considerando del voto separado. Para Tipo D (estructura
    # completa) sí necesitamos mirar más atrás, pero la decisión D se toma
    # por descarte y se basa en señales globales (wc, ausencia de fórmulas).
    cabeza = texto_voto[:4000]

    # ─ Tipo B — art. 280 ─────────────────────────────────────────────────────
    # Discriminante fuerte: mención al art. 280 como base del rechazo. El
    # umbral de wc <= 250 es generoso (el más largo de los ejemplos B es 89
    # palabras pero el corpus completo puede tener variantes con un párrafo
    # adicional). is_merit_decision=0 es corroborante pero no requerido:
    # ocasionalmente la mayoría decide el fondo y un ministro firma con voto
    # 280 en disidencia parcial.
    if RE_TIPO_B_280.search(cabeza):
        if wc_voto <= 250:
            return {
                "tipo_voto_sep":      "B",
                "fragmenta_ratio":    False,
                "punto_divergencia":  None,
            }
        # Si menciona 280 pero wc es alto, probablemente sea un voto de
        # fondo que cita 280 en otro contexto (raro pero posible). Cae a
        # los siguientes detectores.

    # ─ Tipo C — adhesión parcial con considerando explícito ────────────────
    # Patrón (a): "exclusión / excepción del considerando N"
    m_exc = RE_TIPO_C_EXCLUSION.search(cabeza)
    if m_exc:
        n = m_exc.group(3)
        return {
            "tipo_voto_sep":      "C",
            "fragmenta_ratio":    "parcial",
            "punto_divergencia":  f"considerando {n}",
        }

    # Patrón (c): "adhiere hasta el considerando N" — divergencia en N+1
    m_hasta = RE_TIPO_C_ADHIERE_HASTA.search(cabeza)
    if m_hasta:
        n = int(m_hasta.group(2))
        return {
            "tipo_voto_sep":      "C",
            "fragmenta_ratio":    "parcial",
            "punto_divergencia":  f"considerando {n + 1}",
        }

    # Patrón (b): "coincide con los considerandos N1 y N2..." — divergencia
    # en el primer considerando NO mencionado. Extraemos el último número
    # de la lista citada y la divergencia empieza en último+1.
    m_lista = RE_TIPO_C_HASTA.search(cabeza)
    if m_lista:
        lista_str = m_lista.group(2)
        nums = [int(x) for x in re.findall(r"\d+", lista_str)]
        if nums:
            ultimo = max(nums)
            return {
                "tipo_voto_sep":      "C",
                "fragmenta_ratio":    "parcial",
                "punto_divergencia":  f"considerando {ultimo + 1}",
            }

    # ─ Tipo A — remisión al dictamen ────────────────────────────────────────
    # Match principal: cualquier fórmula de remisión. La rama anafórica ("al
    # que cabe remitirse") se valida adicionalmente: requiere que la palabra
    # "dictamen" aparezca en una ventana de 250 caracteres previa al match,
    # para evitar falsos positivos donde "al que cabe remitirse" se refiere
    # a un precedente y no al dictamen.
    m_a = RE_TIPO_A_REMISION_DICTAMEN.search(cabeza)
    if m_a:
        es_anaforico = m_a.group(0).lower().startswith("al ")
        if es_anaforico:
            inicio = max(0, m_a.start() - 250)
            ventana_previa = cabeza[inicio:m_a.start()]
            if RE_DICTAMEN_MENCION.search(ventana_previa):
                return {
                    "tipo_voto_sep":      "A",
                    "fragmenta_ratio":    False,
                    "punto_divergencia":  None,
                }
            # Sin "dictamen" en la ventana previa: probablemente es remisión
            # a un precedente. Cae a Tipo E.
        else:
            return {
                "tipo_voto_sep":      "A",
                "fragmenta_ratio":    False,
                "punto_divergencia":  None,
            }

    # ─ Tipo E — remisión a voto propio anterior o a precedente ─────────────
    # Requiere una fórmula de remisión Y la presencia de una cita "Fallos:"
    # (o de la palabra "causa" en la ventana). La cita "Fallos:" sola es
    # demasiado común — todos los fallos citan precedentes —, y la fórmula
    # sola sin cita podría ser una remisión interna al propio considerando.
    # Pedir ambas condiciones reduce falsos positivos.
    m_e = RE_TIPO_E_REMISION_PRECEDENTE.search(cabeza)
    if m_e:
        # Verificamos que haya una cita de Fallos en una ventana razonable
        # alrededor del match (no necesariamente posterior: el patrón "a
        # cuyos fundamentos corresponde remitir" suele venir DESPUÉS de la
        # cita).
        ventana = cabeza[max(0, m_e.start() - 300):m_e.end() + 300]
        if RE_FALLOS_CITA.search(ventana):
            # Si la ratio del precedente es identificable (siempre lo es
            # cuando hay cita explícita de Fallos), fragmentación parcial.
            return {
                "tipo_voto_sep":      "E",
                "fragmenta_ratio":    "parcial",
                "punto_divergencia":  "dispositivo",
            }
        # Fórmula de remisión sin cita de Fallos: ambiguo. Cae a
        # indeterminado o a D según wc.

    # ─ Tipo D — concurrencia sustantiva independiente ──────────────────────
    # Por descarte: no matchea fórmulas de adhesión ni de remisión. Señales
    # de D:
    #   - wc_voto alto (>= 1500). Calibración: ejemplos 7 y 8 tienen 6026 y
    #     6666 palabras. Umbral conservador para no robarle votos a C y E
    #     que pueden ser largos (Ejemplo 5 de C: 1398 palabras).
    #   - is_merit_decision=1 sube la prior pero no es requisito (puede
    #     haber concurrencias sustantivas en casos no-de-fondo si el voto
    #     desarrolla una doctrina de admisibilidad alternativa).
    #   - "Considerando: 1°)" en la ventana inicial: estructura autónoma.
    es_estructura_autonoma = bool(RE_CONSIDERANDO_NUMERADO_1.search(cabeza))

    if wc_voto >= 1500 and es_estructura_autonoma:
        return {
            "tipo_voto_sep":      "D",
            "fragmenta_ratio":    True,
            "punto_divergencia":  "dispositivo",
        }

    # Caso límite: wc alto pero sin "1°)" detectable — puede ser OCR roto o
    # voto que arranca con un considerando no numerado. Si is_merit_decision=1
    # y wc >= 2500, lo consideramos D igual.
    if is_merit_decision and wc_voto >= 2500:
        return {
            "tipo_voto_sep":      "D",
            "fragmenta_ratio":    True,
            "punto_divergencia":  "dispositivo",
        }

    # ─ Fallback: indeterminado ──────────────────────────────────────────────
    return {
        "tipo_voto_sep":      "indeterminado",
        "fragmenta_ratio":    False,
        "punto_divergencia":  None,
    }

# ── Bloque de un caso ─────────────────────────────────────────────────────────

def construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin):
    """
    v14: dado el archivo (lines) y los límites del fallo (linea_inicio,
    linea_fin) tomados de fallos_localizados.csv, devuelve el bloque
    correspondiente.

    linea_inicio y linea_fin son 0-indexados (igual que en mapa_paginas.csv).
    El bloque incluye linea_fin.
    """
    if linea_fin is None or linea_fin == "":
        linea_fin = len(lines) - 1
    linea_inicio = max(0, int(linea_inicio))
    linea_fin = min(len(lines) - 1, int(linea_fin))
    if linea_inicio > linea_fin:
        return []
    return lines[linea_inicio : linea_fin + 1]


def detectar_apertura_en_bloque(bloque):
    """
    v14: busca el marcador clásico FALLO/SENTENCIA DE LA CORTE SUPREMA dentro
    del bloque. Devuelve (apertura_tipo, apertura_idx_relativo) donde
    apertura_idx_relativo es 0-indexado dentro del bloque, o (None, None) si
    no encuentra marcador.

    El marcador puede estar lejos del inicio del bloque cuando el fallo arranca
    con un dictamen largo del Procurador. Por eso buscamos en todo el bloque.
    RE_APERTURA es estricto (línea exacta = "FALLO DE LA CORTE SUPREMA"), por
    lo que no hay riesgo de matchear menciones del fallo en cuerpo de texto
    o en sumarios editoriales.
    """
    for k, ln in enumerate(bloque):
        m = RE_APERTURA.match(ln.strip())
        if m:
            return (m.group(1).lower(), k)
    return (None, None)


# ── NUEVO v15: detección de fin real del fallo ────────────────────────────────
# Lógica: buscar la frontera con el fallo siguiente usando pistas en cascada
# (carátula del siguiente, header de sumario nuevo, marcador de apertura, firma
# del actual) y búsqueda BIDIRECCIONAL alrededor del linea_fin del catálogo.
# Esto permite detectar correctamente el fin del contenido decisorio cuando:
#   (a) el catálogo extendió demás (bloque cubre múltiples fallos físicos)
#   (b) el catálogo cortó corto (la firma del fallo X cae en la página
#       compartida con el fallo siguiente)

# Header de sumario: línea en MAYÚSCULAS, corta, terminada en : o .
# Ejemplos: "RECURSO EXTRAORDINARIO: Principios generales.", "TRANSPORTE AEREO."
def linea_es_header_sumario(linea):
    s = linea.strip()
    if not s:
        return False
    if len(s) > 150:
        return False
    if not (s.endswith(".") or s.endswith(":") or ":" in s[:80]):
        return False
    primeros_chars = []
    for c in s:
        if c.isalpha():
            primeros_chars.append(c)
            if len(primeros_chars) >= 5:
                break
    if len(primeros_chars) < 5:
        return False
    if not all(c.isupper() for c in primeros_chars):
        return False
    primera_palabra_match = re.match(r"^[A-ZÁÉÍÓÚÑ]+", s)
    primera_palabra = primera_palabra_match.group(0) if primera_palabra_match else ""
    if len(primera_palabra) < 5:
        return False
    return True


# Headers de voto/disidencia que mencionan al juez como inicio (no como firma).
RE_HEADER_VOTO_DISIDENCIA = re.compile(
    r"^\s*(disidencia|voto)\b|"
    r"^\s*(don|do[ñn]a|del\s+(se[ñn]or|se[ñn]ora))\b|"
    r"^\s*(se[ñn]or(es)?|se[ñn]ora(s)?)\s+(ministr|president|vicepresidente|juez|jueza)|"
    r"^\s*la\s+se[ñn]ora\s+|"
    r"^\s*el\s+se[ñn]or\s+",
    re.I
)


def linea_es_firma_de_juez(linea):
    """
    Una línea es firma de juez si contiene un apellido de JUECES_CONOCIDOS y
    tiene señales típicas de firma (raya, corta, termina en punto), descartando
    headers de voto/disidencia y menciones del juez en cuerpo de texto.
    """
    s = linea.strip()
    if not s or len(s) > 200:
        return False
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False
    primera_palabra = s.split()[0].lower() if s.split() else ""
    palabras_cuerpo = {
        "siguiendo", "como", "según", "segun", "que", "el", "la", "los", "las",
        "ya", "esta", "este", "ese", "esa", "ello", "por", "pero", "para",
        "tal", "incluso", "asimismo", "tambien", "también", "no", "si",
        "cuando", "mientras", "aunque", "luego", "después", "despues",
        "afirma", "sostiene", "entiende", "considera", "indicó", "indico",
        "destacó", "destaco", "señaló", "señalo", "concluyó", "concluyo",
    }
    if primera_palabra.rstrip(",;:") in palabras_cuerpo:
        return False
    encontrado = False
    for pat, _nombre in JUECES_CONOCIDOS:
        if pat.search(s):
            encontrado = True
            break
    if not encontrado:
        return False
    tiene_raya = "—" in s or " - " in s or "–" in s
    es_corta = len(s) <= 80
    termina_con_punto = s.rstrip().endswith(".")
    if tiene_raya or es_corta or (termina_con_punto and len(s) <= 120):
        return True
    return False


# ── A001: búsqueda inversa de firma (fallback post-dispositivo) ───────────────
#
# Cuando el parser no detecta dispositivo (por_ello_idx=None) o detecta
# dispositivo pero collect_firma_lines no encuentra firma, esta función
# busca desde el final del bloque hacia atrás. Guardas: zona de fallo
# obligatoria (post-apertura/considerando), span mínimo, filtro de zona
# post-firma, límite de retroceso.
# Validado: PoC H045 (poc_firma_independiente_v2.py), 34 recuperados,
# 0 falsos positivos sobre 148 sin_firma (corpus post-B069).

RE_DATOS_PARTES = re.compile(
    r"^(Recurso|Nombre del|Tribunal de origen|Tribunal que intervino|"
    r"Causa|Profesionales|Ministerio|Parte actora|Parte demandada)",
    re.I,
)

_SPAN_MINIMO_FIRMA_INVERSA = 20


def _encontrar_zona_fallo(bloque):
    """
    Encuentra el inicio de la zona del fallo propiamente dicho,
    excluyendo sumarios y dictamen del Procurador.

    Busca la ÚLTIMA ocurrencia de (en orden de prioridad):
    1. Apertura: "FALLO DE LA CORTE SUPREMA"
    2. Fecha: "Buenos Aires, ..."
    3. Considerando: "Considerando:"
    4. Vistos: "Vistos los autos:"

    Retorna el índice relativo al bloque, o None.
    """
    ultima_apertura = None
    ultima_fecha = None
    ultimo_cons = None
    ultimo_vistos = None
    for k in range(len(bloque)):
        s = bloque[k].strip()
        if RE_APERTURA.match(s):
            ultima_apertura = k
        if RE_FECHA_LINEA.match(s):
            ultima_fecha = k
        if RE_CONSIDERANDO.match(s):
            ultimo_cons = k
        if s.lower().startswith("vistos los autos"):
            ultimo_vistos = k
    if ultima_apertura is not None:
        return ultima_apertura
    if ultima_fecha is not None:
        return ultima_fecha
    if ultimo_cons is not None:
        return ultimo_cons
    if ultimo_vistos is not None:
        return ultimo_vistos
    return None


def buscar_firma_inversa(bloque, max_retroceso=80):
    """
    Busca firma desde el final del bloque hacia atrás.

    Retorna (firma_idx, firma_raw, motivo) donde motivo es:
      'ok'                   — firma encontrada
      'span_corto'           — bloque menor a _SPAN_MINIMO_FIRMA_INVERSA
      'sin_zona_fallo'       — no se encontró apertura/fecha/considerando
      'sin_firma_post_fallo' — zona de fallo encontrada pero sin firma
    """
    n = len(bloque)
    if n < _SPAN_MINIMO_FIRMA_INVERSA:
        return None, "", "span_corto"

    zona_fallo = _encontrar_zona_fallo(bloque)
    if zona_fallo is None:
        return None, "", "sin_zona_fallo"

    limite = max(zona_fallo, n - max_retroceso)

    firma_encontrada = None
    for k in range(n - 1, limite - 1, -1):
        s = bloque[k].strip()
        if not s:
            continue
        if RE_PAGE_HEADER.match(s):
            continue
        if RE_DATOS_PARTES.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_encontrada = k
            break

    if firma_encontrada is None:
        return None, "", "sin_firma_post_fallo"

    # Subir para encontrar el inicio de la firma (puede ser multi-línea)
    firma_inicio = firma_encontrada
    for k in range(firma_encontrada - 1, max(limite, firma_encontrada - 5) - 1, -1):
        s = bloque[k].strip()
        if not s:
            break
        if RE_PAGE_HEADER.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_inicio = k
        else:
            if any(p.search(s) for p, _ in JUECES_CONOCIDOS) and len(s) < 80:
                firma_inicio = k
            else:
                break

    firma_raw = collect_firma_lines(bloque, firma_inicio)
    return firma_inicio, firma_raw, "ok"


# ── H040: wrapper con guardas para Pista 2 de detectar_fin_real ──────────────
#
# linea_es_header_sumario matchea falsos positivos en la zona de firma:
# líneas como "ARGIBAY (en disidencia)." pasan porque empiezan con ≥5
# mayúsculas y terminan en punto. Las guardas excluyen firmas, calificadores,
# headers de página y marcadores de apertura antes de aceptar el match.

def linea_es_header_sumario_guardado(linea):
    """linea_es_header_sumario + guardas de exclusión para Pista 2."""
    if not linea_es_header_sumario(linea):
        return False
    s = linea.strip()
    if linea_es_firma_de_juez(linea):
        return False
    if RE_CALIFICADOR.search(s):
        return False
    if RE_PAGE_HEADER.match(s):
        return False
    if RE_APERTURA.match(s):
        return False
    if RE_DICT_HDR.match(s):
        return False
    if s.upper().startswith("DICTAMEN"):
        return False
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False
    return True


def primer_token_de_caratula(nombres_indice):
    """Extrae el primer apellido/nombre principal de nombres_indice."""
    if not nombres_indice:
        return ""
    primera = nombres_indice.split("|")[0].strip()
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", primera)
    for t in tokens:
        if len(t) >= 4 and t.lower() not in (
            "otro", "otros", "sociedad", "sucesion", "sucesión",
            "empresa", "compania", "compañia", "compañía"
        ):
            return t
    return tokens[0] if tokens else ""


# ── v18 Fase F: refinador de linea_inicio por título ─────────────────────────
#
# El localizador ancla linea_inicio en el header de página del .md, que
# frecuentemente cae en medio de la página anterior e incluye residuo del
# fallo previo (firma arrastrada, metadata editorial, representación letrada).
# Este refinador recorta ese residuo buscando el título del caso como ancla
# más precisa.
#
# Señal primaria : primer_token_de_caratula(nombres_indice) — token del título.
# Señal secundaria: "Vistos los autos" — emite warning en status_localizacion.
# Fallback final  : linea_inicio del catálogo sin cambios — emite warning.
#
# La búsqueda se restringe a las primeras MAX_LINEAS_BUSQUEDA_TITULO líneas
# del bloque para no matchear citas del caso en el cuerpo del fallo.

MAX_LINEAS_BUSQUEDA_TITULO = 50


def refinar_inicio_por_titulo(bloque, nombres_indice):
    """
    Intenta refinar linea_inicio recortando residuo pre-título.

    Devuelve (offset_recorte, ancla_usada) donde:
      offset_recorte : int — líneas a recortar del inicio del bloque.
                       0 si no hay refinamiento o título está en línea 0.
      ancla_usada    : str — 'titulo' | 'vistos' | 'catalogo'

    El llamador aplica:
        linea_inicio += offset_recorte
        bloque = bloque[offset_recorte:]
    """
    # ── Señal primaria: token del título ──────────────────────────────────────
    token = primer_token_de_caratula(nombres_indice)
    if token and len(token) >= 4:
        pat = re.compile(r'\b' + re.escape(token) + r'\b', re.I)
        for k, ln in enumerate(bloque[:MAX_LINEAS_BUSQUEDA_TITULO]):
            if pat.search(ln):
                return (k, 'titulo')

    # ── Señal secundaria: "Vistos los autos" ─────────────────────────────────
    for k, ln in enumerate(bloque[:MAX_LINEAS_BUSQUEDA_TITULO]):
        if RE_VISTOS_LOS_AUTOS.match(ln):
            return (k, 'vistos')

    # ── Fallback: sin refinamiento ────────────────────────────────────────────
    return (0, 'catalogo')


def detectar_fin_real(lines, linea_inicio, linea_fin_catalogo,
                      proximo_header_pagina, primer_token_siguiente):
    """
    v15: detecta dónde realmente termina el contenido decisorio del fallo.
    Devuelve (linea_fin_real, status_fin, pista).

    status_fin: 'fin_dentro_bloque' / 'fin_extendido_pag_compartida' /
                'fin_por_firma_actual' / 'fin_no_detectado'
    pista: 'caratula_siguiente' / 'sumario_siguiente' /
           'marcador_apertura_siguiente' / 'firma_actual' / 'fallback_catalogo'
    """
    n = len(lines)
    li = max(0, int(linea_inicio))
    lfc = min(n - 1, int(linea_fin_catalogo))

    # Determinar límite hacia adelante. proximo_header_pagina es la línea de
    # inicio del bloque del fallo siguiente; la firma del fallo X puede caer
    # en las primeras líneas de ese bloque (página compartida), por eso
    # extendemos ~50 líneas más allá.
    if proximo_header_pagina is not None and proximo_header_pagina > lfc:
        limite_adelante = min(proximo_header_pagina + 50, n - 1)
    else:
        limite_adelante = min(lfc + 200, n - 1)

    def buscar_atras(check, desde, hasta):
        for k in range(desde, hasta - 1, -1):
            if check(lines[k]):
                return k
        return None

    def buscar_adelante(check, desde, hasta):
        for k in range(desde, hasta + 1):
            if check(lines[k]):
                return k
        return None

    # Pista 1: carátula del fallo siguiente
    if primer_token_siguiente and len(primer_token_siguiente) >= 5:
        pat = re.compile(r"\b" + re.escape(primer_token_siguiente) + r"\b", re.I)
        def es_caratula(linea):
            return bool(pat.search(linea))
        # B069: búsqueda atrás de Pista 1 ELIMINADA. El token del caso
        # siguiente matcheaba en cuerpo argumentativo, Vistos los autos y
        # firmas de jueces, cortando centenares de líneas. La búsqueda
        # hacia adelante (abajo) cubre página compartida correctamente.
        # Adelante hasta limite_adelante
        k = buscar_adelante(es_caratula, lfc + 1, limite_adelante)
        if k is not None:
            return (k - 1, "fin_extendido_pag_compartida", "caratula_siguiente")

    # Pista 2: header de sumario nuevo. Búsqueda atrás solo en mitad inferior
    # del bloque para no confundir con sumarios del propio fallo X.
    # H040: usa wrapper con guardas para excluir firmas, calificadores,
    # headers de página y marcadores de apertura.
    mitad_bloque = li + (lfc - li) // 2
    k = buscar_atras(linea_es_header_sumario_guardado, lfc, mitad_bloque)
    if k is not None:
        return (k - 1, "fin_dentro_bloque", "sumario_siguiente")
    k = buscar_adelante(linea_es_header_sumario_guardado, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "sumario_siguiente")

    # Pista 3: DICTAMEN o FALLO DE LA CORTE del fallo siguiente. Solo adelante
    # (atrás siempre hay marcadores del propio fallo).
    def es_marcador_apertura(linea):
        s = linea.strip()
        return (RE_APERTURA.match(s) is not None
                or RE_DICT_HDR.match(s) is not None
                or s.upper().startswith("DICTAMEN"))
    k = buscar_adelante(es_marcador_apertura, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "marcador_apertura_siguiente")

    # Fallback: firma del fallo actual
    k = buscar_atras(linea_es_firma_de_juez, lfc, li)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")
    k = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")

    # Sin detectar: usar el catálogo como está
    return (lfc, "fin_no_detectado", "fallback_catalogo")


def cargar_proximos_headers(ruta_mapa):
    """Devuelve dict {(tomo, archivo): [(linea_header, pagina), ...]} ordenado."""
    por_archivo = {}
    with open(ruta_mapa, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["tomo"]), row["archivo"])
            por_archivo.setdefault(key, []).append(
                (int(row["linea_header"]), int(row["pagina"]))
            )
    for k in por_archivo:
        por_archivo[k].sort()
    return por_archivo


def proximo_header_despues_de(headers_archivo, linea):
    """Devuelve la próxima línea-header > linea, o None."""
    for ln, _pg in headers_archivo:
        if ln > linea:
            return ln
    return None


# ── v17: helper para casos identificados como sumario-con-link ────────────────

def construir_caso_sumario_link(caso_id_canonico, tomo, nombres_indice,
                                 source_file, linea_inicio, linea_fin,
                                 linea_fin_real, status_loc_final,
                                 status_fin, pista_fin):
    """
    v17: construye el dict de un caso identificado como sumario-con-link.

    El bloque no contiene un fallo parseable (es una nota editorial con link
    al fallo online), por lo que todos los campos analíticos (firma, outcome,
    voting_pattern, considerando, jueces, wc_*, etc.) quedan vacíos o en cero.

    La metadata estructural (linea_inicio, linea_fin, source_file, nombres,
    status) se conserva intacta para permitir auditoría posterior y
    cruzamiento con otras fuentes (sentencias online, índice editorial).

    El schema es idéntico al de un caso normal — solo cambian los valores —
    para mantener consistencia del CSV y permitir filtrado simple por
    tipo_entrada.
    """
    return {
        "caso_id_canonico":       caso_id_canonico,
        "tomo":                   tomo,
        "case_name_indice":       nombres_indice,
        "case_name_cuerpo":       "",
        "case_name_cuerpo_legacy": "",
        "date":                   "",
        "apertura_tipo":          "",
        "outcome":                "",
        "voting_pattern":         "",
        "n_jueces":               0,
        "n_titulares":            0,
        "n_votos_svoto":          0,
        "n_disidencias":          0,
        "dictamen_presente":      0,
        "is_originaria":          0,
        "is_full_bench":          0,
        "is_merit_decision":      0,
        "word_count":             0,
        "wc_mayoria":             0,
        "wc_votos":               0,
        "wc_considerando":        0,
        "wc_dictamen":            0,
        "firma_raw":              "",
        "jueces":                 "",
        "jueces_conocidos":       "",
        "jueces_desconocidos":    "",
        "posiciones":             "{}",
        "tribunal_origen":        "",
        "tribunal_origen_status": "",
        "por_ello_text":          "",
        "considerando_text":      "",
        "source_file":            source_file,
        "linea_inicio":           int(linea_inicio),
        "linea_fin":              int(linea_fin) if linea_fin not in ("", None) else "",
        "linea_fin_real":         linea_fin_real,
        "status_localizacion":    status_loc_final,
        "status_fin":             status_fin,
        "pista_fin":              pista_fin,
        "tipo_entrada":           "sumario_con_link",
    }


# ── Procesamiento de un archivo ───────────────────────────────────────────────

def procesar_archivo(filepath, fallos_del_archivo, headers_archivo, primer_token_por_caso, siguiente_caso):
    """
    v15: procesa un archivo .md y devuelve dos listas (casos, votos).

    fallos_del_archivo: lista de dicts con las filas de fallos_localizados.csv
    correspondientes a este archivo. Cada fila tiene al menos:
      caso_id_canonico, tomo, pagina_inicio, pagina_fin (puede ser ''),
      linea_inicio, linea_fin (puede ser ''), nombres_indice, status.

    headers_archivo: lista [(linea_header, pagina), ...] ordenada, del mapa.
    primer_token_por_caso: dict {caso_id_canonico: primer_token}.
    siguiente_caso: dict {caso_id_canonico: caso_id_canonico_siguiente}.

    Cada fallo se procesa con su bloque del catálogo, y dentro del bloque se
    detecta la frontera real con el fallo siguiente (linea_fin_real). Los
    conteos de palabras y el texto de los votos se calculan hasta linea_fin_real,
    no hasta el final del bloque.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Tomo (lo seguimos sacando del filename para tener un fallback, aunque
    # también está en cada fila del catálogo)
    tomo_match = RE_TOMO.search(filepath.name)
    tomo_filename = int(tomo_match.group(1)) if tomo_match else 0

    casos_out  = []
    votos_out  = []
    desconocidos_global = Counter()

    for fallo_meta in fallos_del_archivo:
        linea_inicio = fallo_meta["linea_inicio"]
        linea_fin    = fallo_meta["linea_fin"]
        caso_id_canonico = fallo_meta["caso_id_canonico"]
        tomo = int(fallo_meta["tomo"]) if fallo_meta["tomo"] else tomo_filename
        nombres_indice = fallo_meta.get("nombres_indice", "")
        status_loc = fallo_meta.get("status", "")

        # Extraer el bloque del fallo
        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin)
        if not bloque:
            continue  # bloque vacío (linea_inicio inválida); saltear

        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────
        # Buscar la frontera con el fallo siguiente (carátula/sumario/marcador)
        # para detectar dónde termina realmente el contenido decisorio.
        siguiente = siguiente_caso.get(caso_id_canonico)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""
        prox_header = proximo_header_despues_de(headers_archivo, int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1)
        linea_fin_real, status_fin, pista_fin = detectar_fin_real(
            lines,
            int(linea_inicio),
            int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1,
            prox_header,
            primer_token_siguiente
        )

        # Reconstruir el bloque hasta linea_fin_real (puede extender el bloque
        # original si la firma cae más allá del linea_fin del catálogo).
        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin_real)
        if not bloque:
            continue

        # ── v18 Fase F: refinar linea_inicio por título ──────────────────────
        # Recorta residuo del fallo anterior incluido por el localizador
        # (arranca desde header de página compartida). Señal primaria: token
        # del título en nombres_indice. Secundaria: "Vistos los autos".
        # Fallback: linea_inicio del catálogo sin cambios.
        # ancla_inicio se propaga a status_localizacion para auditoría.
        offset_titulo, ancla_inicio = refinar_inicio_por_titulo(
            bloque, nombres_indice
        )
        if offset_titulo > 0:
            linea_inicio = int(linea_inicio) + offset_titulo
            bloque = bloque[offset_titulo:]
            if not bloque:
                continue

        # Detectar apertura clásica dentro del bloque (para apertura_tipo y
        # como referencia para find_case_name del cuerpo)
        apertura_tipo, apertura_rel = detectar_apertura_en_bloque(bloque)
        # apertura_idx absoluto (en `lines`) cuando hay marcador, para
        # compatibilidad con find_case_name y find_tribunal_origen que
        # esperan índice global
        if apertura_rel is not None:
            apertura_idx = int(linea_inicio) + apertura_rel
        else:
            apertura_idx = int(linea_inicio)
            apertura_tipo = ""

        # ── status_localizacion: refinamiento ────────────────────────────────
        status_loc_final = status_loc
        if apertura_rel is None:
            # Bloque procesado pero sin marcador clásico de apertura
            if status_loc == "ok":
                status_loc_final = "ok_sin_marcador_apertura"
            else:
                status_loc_final = status_loc + "_sin_marcador"
        # v18 Fase F: registrar ancla de inicio para auditoría posterior.
        # 'titulo'  → ancló por token del título (caso limpio, no modifica status)
        # 'vistos'  → ancló por "Vistos los autos" (título no detectado en bloque)
        # 'catalogo'→ sin refinamiento, usa linea_inicio del catálogo
        if ancla_inicio == 'vistos':
            if status_loc_final in ("ok", "ok_sin_marcador_apertura"):
                status_loc_final = status_loc_final + "_ancla_vistos"
            else:
                status_loc_final = status_loc_final + "_ancla_vistos"
        elif ancla_inicio == 'catalogo':
            if status_loc_final in ("ok", "ok_sin_marcador_apertura"):
                status_loc_final = status_loc_final + "_ancla_catalogo"
            else:
                status_loc_final = status_loc_final + "_ancla_catalogo"
        # ancla_inicio == 'titulo': status_loc_final no cambia (caso limpio)

        # ── v17: detector de sumarios-con-link ───────────────────────────────
        # Si el bloque contiene el patrón "(*) Sentencia del ... Ver ...",
        # es una nota editorial sin fallo parseable. Se carga como tipo_entrada
        # = "sumario_con_link" con campos analíticos vacíos y se salta el
        # resto del procesamiento.
        #
        # IMPORTANTE: la detección no depende de si el parser detectaría
        # firma o no. En casos de solapamiento de páginas (típico cuando un
        # fallo termina y un sumario empieza en la misma página), el bloque
        # del sumario arrastra firma del fallo anterior. La presencia del
        # patrón sumario-con-link es señal suficiente: las firmas que pueda
        # haber en el bloque pertenecen al fallo previo, no a este caso.
        es_sumario_con_link = any(
            RE_SUMARIO_LINK.match(ln.strip()) for ln in bloque
        )
        if es_sumario_con_link:
            casos_out.append(construir_caso_sumario_link(
                caso_id_canonico=caso_id_canonico,
                tomo=tomo,
                nombres_indice=nombres_indice,
                source_file=filepath.name,
                linea_inicio=linea_inicio,
                linea_fin=linea_fin,
                linea_fin_real=linea_fin_real,
                status_loc_final=status_loc_final,
                status_fin=status_fin,
                pista_fin=pista_fin,
            ))
            continue

        # Fecha del fallo. v16: cambio respecto a v15.
        # v15 buscaba en las primeras 8 líneas del bloque, pero el bloque
        # arranca con sumarios y dictamen, no con el fallo. La fecha del
        # fallo está cerca del marcador FALLO DE LA CORTE SUPREMA o, si no
        # hay marcador detectado, es la última fecha "Buenos Aires" del
        # bloque (la del dictamen suele estar antes).
        # NOTA: lineas_dictamen aún no está calculado a esta altura, así
        # que la heurística (b) sin marcador puede capturar la fecha del
        # dictamen como fallback. Es lo mejor que podemos hacer sin
        # reordenar el código entero.
        fecha_str = ""
        if apertura_rel is not None:
            # Caso (a): hay marcador clásico. Buscar fecha en las 10 líneas
            # siguientes al marcador.
            for k in range(apertura_rel + 1, min(apertura_rel + 11, len(bloque))):
                m = RE_FECHA_EXTRACT.search(bloque[k])
                if m:
                    fecha_str = m.group(1)
                    break
        else:
            # Caso (b): sin marcador. Buscar la ÚLTIMA fecha del bloque.
            # La última fecha "Buenos Aires" suele ser la del fallo, ya que
            # la del dictamen del Procurador viene antes en el texto.
            for k in range(len(bloque) - 1, -1, -1):
                m = RE_FECHA_EXTRACT.search(bloque[k])
                if m:
                    fecha_str = m.group(1)
                    break

        # Fallback: si no encontró nada con la lógica nueva, usar la primera
        # fecha del bloque (comportamiento v15).
        if not fecha_str:
            for k, ln in enumerate(bloque[:30]):
                m = RE_FECHA_EXTRACT.search(ln)
                if m:
                    fecha_str = m.group(1)
                    break

        # case_name del cuerpo. v18: Fix 1 — V1 como fuente primaria.
        #
        # Estrategia primaria: extraer_caratula_v1 busca 'Vistos los autos:
        # "X"' desde apertura_rel hacia adelante. Cobertura medida: 67%
        # del corpus (Auditoría B, sesión XV). Captura limpia, sin las
        # citas doctrinales del dictamen que rompían find_case_name viejo.
        #
        # Fallback: find_case_name (heurística v12) cuando V1 no encuentra.
        # Si tampoco hay apertura_rel, queda vacío.
        #
        # Columna shadow case_name_cuerpo_legacy guarda lo que hubiera
        # devuelto find_case_name siempre, para auditar el diff post-fix.
        # Eliminable en una corrida posterior cuando el fix esté validado.
        if apertura_rel is not None:
            case_name_cuerpo_legacy = find_case_name(lines, apertura_idx)
            case_name_cuerpo_v1 = extraer_caratula_v1(bloque, apertura_rel)
            case_name_cuerpo = case_name_cuerpo_v1 or case_name_cuerpo_legacy
        else:
            case_name_cuerpo_legacy = ""
            case_name_cuerpo = ""

        # Tribunal de origen
        tribunal_str = find_tribunal_origen(lines, apertura_idx, apertura_idx + len(bloque))

        # Procesar bloque línea por línea (lógica idéntica a v12)
        en_dictamen        = False
        dictamen_presente  = False
        lineas_dictamen    = set()
        por_ello_idx       = None
        por_ello_text      = ""
        n_votos_svoto      = 0
        n_disidencias      = 0
        inicio_votos_indiv = None
        marcadores_votos   = []

        for k, bl in enumerate(bloque):
            stripped = bl.strip()
            if not stripped:
                continue

            if RE_DICT_HDR.match(stripped):
                en_dictamen       = True
                dictamen_presente = True
                lineas_dictamen.add(k)
                continue
            elif en_dictamen:
                # Backstop: "FALLO/SENTENCIA DE LA CORTE SUPREMA" cierra
                # el dictamen sin consumir la línea. Resuelve dictámenes
                # largos donde len(prev) >= 80 impide el cierre por fecha.
                if RE_APERTURA.match(stripped):
                    en_dictamen = False
                    # No agregar a lineas_dictamen, no continue:
                    # la línea es la apertura del fallo, no del dictamen.
                else:
                    lineas_dictamen.add(k)
                    if RE_FECHA_LINEA.match(stripped) and k > 5:
                        prev = bloque[k - 1].strip() if k > 0 else ""
                        if prev and len(prev) < 80:
                            en_dictamen = False
                    continue

            if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
                tipo = "voto" if RE_VOTO_HDR.match(stripped) else "disidencia"
                if tipo == "voto":
                    n_votos_svoto += 1
                else:
                    n_disidencias += 1
                if inicio_votos_indiv is None:
                    inicio_votos_indiv = k
                header_completo = stripped
                for offset in range(1, 4):
                    juez = detectar_juez_en_voto_header(header_completo)
                    if juez:
                        marcadores_votos.append((k, juez, tipo))
                        break
                    if k + offset < len(bloque):
                        sig = bloque[k + offset].strip()
                        if not sig:
                            continue
                        if RE_CONSIDERANDO.match(sig):
                            break
                        header_completo += " " + sig
                continue

            pass  # dispositivo detection moved to anchored search below

        # ── Dispositivo: búsqueda anclada (emula auditor) ─────────────
        # Cascada de inicio: apertura_rel → dictamen_end+1 → 0.
        # Techo: inicio_votos_indiv (no buscar dentro de votos separados).
        # Motivación: evita matchear dispositivos prematuros en residuo del
        # fallo anterior o en el dictamen embebido (B013, 302 casos).
        dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
        if apertura_rel is not None:
            inicio_busqueda = apertura_rel
        elif dictamen_end is not None:
            inicio_busqueda = dictamen_end + 1
        else:
            inicio_busqueda = 0
        # Techo: solo usar inicio_votos_indiv si los votos están después
        # de la apertura (= son del fallo actual, no de residuo previo).
        if (inicio_votos_indiv is not None
                and (apertura_rel is None or inicio_votos_indiv > apertura_rel)):
            fin_busqueda = inicio_votos_indiv
        else:
            fin_busqueda = len(bloque)

        # ── Fix B059: forward con validación de firma ─────────────
        # Busca el primer dispositivo que tenga firma de juez en las
        # 40 líneas siguientes. Si ninguno tiene firma, usa el primero
        # como fallback (= comportamiento pre-fix, sin regresión).
        # Motivación: variantes como "en consecuencia", "de conformidad"
        # matchean texto argumental antes del dispositivo real. El
        # dispositivo real siempre tiene firma después.
        por_ello_idx = None
        por_ello_text = ""
        _fallback_idx = None
        _fallback_text = ""
        for k in range(inicio_busqueda, fin_busqueda):
            if k in lineas_dictamen:
                continue
            stripped = bloque[k].strip()
            if not stripped:
                continue
            es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
            if es_disp:
                chunk = []
                for m2 in range(k, min(k + 6, len(bloque))):
                    chunk.append(bloque[m2])
                    if bloque[m2].strip().endswith("."):
                        break
                candidate_text = " ".join(chunk).strip()
                if _fallback_idx is None:
                    _fallback_idx = k
                    _fallback_text = candidate_text
                if any(linea_es_firma_de_juez(bloque[j])
                       for j in range(k + 1, min(k + 41, len(bloque)))):
                    por_ello_idx = k
                    por_ello_text = candidate_text
                    break
        if por_ello_idx is None and _fallback_idx is not None:
            por_ello_idx = _fallback_idx
            por_ello_text = _fallback_text

        # -- H041 Tier 2: .search() mid-line para patrones seguros -----
        # Solo se activa si Tier 1 no encontro NADA (ni validado ni fallback).
        # Guardas: (a) patrones seguros, (b) fin de oracion antes del match,
        #          (c) filtro argumental, (d) firma validada sin fallback.
        if por_ello_idx is None:
            _t2_pats = [
                re.compile(r"Por ello[,.]?\s", re.I),
                re.compile(r"Por lo expuesto\b", re.I),
                re.compile(r"Por las razones\b", re.I),
                re.compile(r"Por lo expresado\b", re.I),
                re.compile(r"Por las consideraciones\b", re.I),
                re.compile(r"Que[,]?\s+por\s+ello\b", re.I),
                re.compile(r"O[íi]dos?\s+(el|la|los|las)\b", re.I),
            ]
            for k in range(inicio_busqueda, fin_busqueda):
                if k in lineas_dictamen:
                    continue
                stripped = bloque[k].strip()
                if not stripped:
                    continue
                _t2_hit = False
                for _t2_pat in _t2_pats:
                    _t2_m = _t2_pat.search(stripped)
                    if _t2_m and _t2_m.start() > 0:
                        # Guarda: fin de oracion antes del match
                        _t2_pre = stripped[:_t2_m.start()].rstrip()
                        if not (_t2_pre.endswith(".") or _t2_pre.endswith(")")
                                or stripped.lstrip().startswith("Que")):
                            continue
                        # Guarda argumental
                        _t2_rest = stripped[_t2_m.end():].strip()
                        _t2_fw = _t2_rest.split()[0].lower().rstrip(",;") if _t2_rest.split() else ""
                        if _t2_fw in POR_ELLO_ARGUMENTAL:
                            continue
                        # Firma validada obligatoria
                        if any(linea_es_firma_de_juez(bloque[j])
                               for j in range(k + 1, min(k + 41, len(bloque)))):
                            chunk = []
                            for m2 in range(k, min(k + 6, len(bloque))):
                                chunk.append(bloque[m2])
                                if bloque[m2].strip().endswith("."):
                                    break
                            por_ello_idx = k
                            por_ello_text = " ".join(chunk).strip()
                            _t2_hit = True
                            break
                if _t2_hit:
                    break

        # ── Tier 3: retry sin techo (B067) ─────────────────────────────
        # Si Tier 1+2 con techo no encontraron NADA, repetir sin techo.
        # Solo se activa para casos que producirían sin_dispositivo.
        # Motivación: 17 casos donde inicio_votos_indiv cae antes del
        # dispositivo real (votos-antes-de-dispositivo o residuo no
        # recortado). El techo deja el rango de búsqueda vacío.
        # Validado: PoC B067, 0 regresiones, 17 mejoras, 16 sin_firma
        # recuperados (422 → 406).
        if por_ello_idx is None:
            _t3_fb_idx = None
            _t3_fb_text = ""
            for k in range(inicio_busqueda, len(bloque)):
                if k in lineas_dictamen:
                    continue
                stripped = bloque[k].strip()
                if not stripped:
                    continue
                es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
                if es_disp:
                    chunk = []
                    for m2 in range(k, min(k + 6, len(bloque))):
                        chunk.append(bloque[m2])
                        if bloque[m2].strip().endswith("."):
                            break
                    candidate_text = " ".join(chunk).strip()
                    if _t3_fb_idx is None:
                        _t3_fb_idx = k
                        _t3_fb_text = candidate_text
                    if any(linea_es_firma_de_juez(bloque[j])
                           for j in range(k + 1, min(k + 41, len(bloque)))):
                        por_ello_idx = k
                        por_ello_text = candidate_text
                        break
            if por_ello_idx is None and _t3_fb_idx is not None:
                por_ello_idx = _t3_fb_idx
                por_ello_text = _t3_fb_text

        considerando_text = extraer_considerando(bloque, por_ello_idx, lineas_dictamen)

        outcome = classify_outcome(por_ello_text, considerando_text) if por_ello_text else "sin_dispositivo"
        if outcome == "sin_dispositivo" and considerando_text:
            if RE_280_CONSIDERANDO.search(considerando_text) or RE_280_LIBRE.search(considerando_text):
                outcome = "inadmisible_280"
            elif RE_ACORDADA_4_CONSIDERANDO.search(considerando_text):
                outcome = "inadmisible_acordada_4"

        firma_raw    = ""
        firma_parsed = {"jueces": [], "voting_pattern": "sin_firma", "desconocidos": []}

        if por_ello_idx is not None:
            firma_raw = collect_firma_lines(bloque, por_ello_idx + 1)
            if firma_raw:
                firma_parsed = parse_firma(firma_raw)
                for d in firma_parsed["desconocidos"]:
                    desconocidos_global[d] += 1

        # ── A001: fallback firma inversa ──────────────────────────────
        # Si el flujo normal no encontró firma (por_ello_idx=None o
        # collect_firma_lines vacío), buscar desde el final del bloque
        # hacia atrás con guardas de zona de fallo y span mínimo.
        if firma_parsed["voting_pattern"] == "sin_firma":
            _fi_idx, _fi_raw, _fi_motivo = buscar_firma_inversa(bloque)
            if _fi_raw:
                _fi_parsed = parse_firma(_fi_raw)
                if _fi_parsed["jueces"]:
                    firma_raw = _fi_raw
                    firma_parsed = _fi_parsed
                    for d in firma_parsed["desconocidos"]:
                        desconocidos_global[d] += 1

        if inicio_votos_indiv is not None:
            lineas_mayoria = [bloque[k] for k in range(len(bloque))
                              if k not in lineas_dictamen and k < inicio_votos_indiv]
            lineas_votos   = [bloque[k] for k in range(inicio_votos_indiv, len(bloque))]
        else:
            lineas_mayoria = [bloque[k] for k in range(len(bloque))
                              if k not in lineas_dictamen]
            lineas_votos   = []

        wc_mayoria = len(re.findall(r'\b\w+\b', " ".join(lineas_mayoria)))
        wc_votos   = len(re.findall(r'\b\w+\b', " ".join(lineas_votos)))
        word_count = wc_mayoria + wc_votos

        is_originaria = int(es_originaria(case_name_cuerpo, considerando_text, por_ello_text))

        if is_originaria:
            tribunal_origen_status = "originaria"
        elif tribunal_str != "SIN_TRIBUNAL_ORIGEN":
            tribunal_origen_status = "apelado_detectado"
        elif hay_tribunal_interviniente(lines, apertura_idx, apertura_idx + len(bloque)):
            tribunal_origen_status = "apelado_detectado"
        else:
            tribunal_origen_status = "sin_marcador"

        n_titulares = sum(1 for j in firma_parsed["jueces"] if j["conocido"]
                          and "(conjuez)" not in j["nombre"])
        is_full_bench = int(n_titulares == 5)

        MERIT_OUTCOMES    = {"hace_lugar", "procedente", "revoca", "nulidad", "confirma"}
        GATEKEEP_OUTCOMES = {"desestima", "inadmisible_280", "inadmisible_acordada_4",
                             "abstracto", "desistimiento", "mal_concedido"}
        is_merit = int(outcome in MERIT_OUTCOMES)

        jueces_nombres     = [j["nombre"] for j in firma_parsed["jueces"]]
        jueces_conocidos_l = [j["nombre"] for j in firma_parsed["jueces"] if j["conocido"]]
        jueces_descon_l    = [j["nombre"] for j in firma_parsed["jueces"] if not j["conocido"]]

        posiciones = {}
        for j in firma_parsed["jueces"]:
            posiciones[j["nombre"]] = j["calificador"] or "mayoria"

        textos_votos = extraer_textos_votos(bloque, marcadores_votos)

        # v17: word count del dictamen del Procurador.
        # Reutiliza lineas_dictamen (set de índices ya detectados por la
        # lógica heredada de v16). Aproximación: la detección no fue
        # validada exhaustivamente, tratar como dato auxiliar.
        wc_dictamen = sum(
            len(re.findall(r'\b\w+\b', bloque[k]))
            for k in lineas_dictamen
            if 0 <= k < len(bloque)
        )

        caso = {
            "caso_id_canonico":       caso_id_canonico,
            "tomo":                   tomo,
            "case_name_indice":       nombres_indice,
            "case_name_cuerpo":       case_name_cuerpo,
            "case_name_cuerpo_legacy": case_name_cuerpo_legacy,
            "date":                   fecha_str,
            "apertura_tipo":          apertura_tipo,
            "outcome":                outcome,
            "voting_pattern":         firma_parsed["voting_pattern"],
            "n_jueces":               len(firma_parsed["jueces"]),
            "n_titulares":            n_titulares,
            "n_votos_svoto":          n_votos_svoto,
            "n_disidencias":          n_disidencias,
            "dictamen_presente":      dictamen_presente,
            "is_originaria":          is_originaria,
            "is_full_bench":          is_full_bench,
            "is_merit_decision":      is_merit,
            "word_count":             word_count,
            "wc_mayoria":             wc_mayoria,
            "wc_votos":               wc_votos,
            "wc_considerando":       len(re.findall(r'\b\w+\b', considerando_text)),
            "wc_dictamen":            wc_dictamen,
            "firma_raw":              firma_raw,
            "jueces":                 " | ".join(jueces_nombres),
            "jueces_conocidos":       " | ".join(jueces_conocidos_l),
            "jueces_desconocidos":    " | ".join(jueces_descon_l),
            "posiciones":             json.dumps(posiciones, ensure_ascii=False),
            "tribunal_origen":        tribunal_str,
            "tribunal_origen_status": tribunal_origen_status,
            "por_ello_text":          por_ello_text[:300],
            "considerando_text":      considerando_text[:2000],
            "source_file":            filepath.name,
            "linea_inicio":           int(linea_inicio),
            "linea_fin":              int(linea_fin) if linea_fin not in ("", None) else "",
            "linea_fin_real":         linea_fin_real,
            "status_localizacion":    status_loc_final,
            "status_fin":             status_fin,
            "pista_fin":              pista_fin,
            "tipo_entrada":           "fallo",
        }
        casos_out.append(caso)

        for j in firma_parsed["jueces"]:
            if not j["conocido"]:
                continue
            juez_nombre = j["nombre"]
            posicion    = j["calificador"] or "mayoria"
            texto_voto = textos_votos.get(juez_nombre, "")
            wc_voto    = len(re.findall(r'\b\w+\b', texto_voto))
            if texto_voto:
                clasif = clasificar_tipo_voto(
                    texto_voto, wc_voto, caso["is_merit_decision"]
                )
                tipo_voto_sep     = clasif["tipo_voto_sep"]
                fragmenta_ratio   = clasif["fragmenta_ratio"]
                punto_divergencia = clasif["punto_divergencia"] or ""
            else:
                tipo_voto_sep     = ""
                fragmenta_ratio   = ""
                punto_divergencia = ""
            voto = {
                "caso_id_canonico":   caso_id_canonico,
                "tomo":               tomo,
                "date":               fecha_str,
                "juez":               juez_nombre,
                "posicion":           posicion,
                "es_conocido":        1,
                "outcome":            caso["outcome"],
                "voting_pattern":     caso["voting_pattern"],
                "is_originaria":      caso["is_originaria"],
                "is_full_bench":      caso["is_full_bench"],
                "is_merit_decision":  caso["is_merit_decision"],
                "wc_mayoria":         caso["wc_mayoria"],
                "wc_votos":           caso["wc_votos"],
                "dictamen_presente":  caso["dictamen_presente"],
                "texto_voto":         texto_voto[:5000],
                "wc_voto":            wc_voto,
                "tipo_voto_sep":      tipo_voto_sep,
                "fragmenta_ratio":    fragmenta_ratio,
                "punto_divergencia":  punto_divergencia,
            }
            votos_out.append(voto)

    return casos_out, votos_out, desconocidos_global

# ── Orquestación ──────────────────────────────────────────────────────────────

def cargar_localizados(ruta):
    """
    Carga fallos_localizados.csv. Devuelve lista de dicts.

    v18 Fase F: los fallos con status='pagina_no_en_mapa' ya no se descartan
    automáticamente. Se intenta inferir su archivo .md y una linea_inicio
    estimada desde los vecinos del mismo tomo. El refinador de título en
    procesar_archivo corrige la linea_inicio en runtime buscando el título
    del caso en el bloque estimado.

    Si no hay ningún vecino con archivo conocido en el mismo tomo, el fallo
    se descarta igual (sin archivo no hay bloque posible).
    """
    filas = []
    descartadas_sin_localizacion = 0
    todas = []
    with open(ruta, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            todas.append(row)

    # Índice de vecinos con archivo y linea_inicio conocidos, por tomo.
    # Cada entrada: (pagina_inicio_int, archivo, linea_inicio_int)
    vecinos_por_tomo = {}
    for row in todas:
        if row.get("archivo") and row.get("linea_inicio"):
            t = row["tomo"]
            try:
                p  = int(row["pagina_inicio"])
                li = int(row["linea_inicio"])
            except (ValueError, TypeError):
                continue
            vecinos_por_tomo.setdefault(t, []).append((p, row["archivo"], li))
    for t in vecinos_por_tomo:
        vecinos_por_tomo[t].sort()

    for row in todas:
        if row["status"] == "pagina_no_en_mapa":
            # Inferir archivo y linea_inicio estimada desde vecinos del tomo
            t = row["tomo"]
            try:
                p = int(row["pagina_inicio"])
            except (ValueError, TypeError):
                descartadas_sin_localizacion += 1
                continue
            vecinos = vecinos_por_tomo.get(t, [])
            # Vecino siguiente: primer vecino con pagina > p
            sig_arch = None
            sig_li   = None
            for vp, va, vli in vecinos:
                if vp > p:
                    sig_arch = va
                    sig_li   = vli
                    break
            # Si no hay siguiente, usar el anterior más cercano
            if sig_arch is None:
                for vp, va, vli in reversed(vecinos):
                    if vp < p:
                        sig_arch = va
                        sig_li   = vli
                        break
            if sig_arch is None:
                # Sin vecinos: imposible inferir archivo
                descartadas_sin_localizacion += 1
                continue
            row = dict(row)  # no mutar el original
            row["archivo"]      = sig_arch
            # linea_inicio estimada: ventana de 200 líneas antes del vecino
            # siguiente. El refinador de título la corrige en runtime.
            row["linea_inicio"] = str(max(0, sig_li - 200))
            row["linea_fin"]    = str(sig_li - 1)
            filas.append(row)
            continue

        # Casos normales: validar que tengan linea_inicio
        if not row.get("linea_inicio"):
            descartadas_sin_localizacion += 1
            continue
        filas.append(row)

    return filas, descartadas_sin_localizacion


def agrupar_por_archivo(filas, carpeta_corpus):
    """
    Devuelve dict {Path(.md): [filas]} ordenado de manera estable.
    Las filas dentro de cada archivo se ordenan por linea_inicio.
    """
    carpeta = Path(carpeta_corpus)
    grupos = {}
    for row in filas:
        archivo_nombre = row["archivo"]
        if not archivo_nombre:
            continue
        clave = carpeta / archivo_nombre
        grupos.setdefault(clave, []).append(row)
    for clave in grupos:
        grupos[clave].sort(key=lambda r: int(r["linea_inicio"]))
    return grupos


def main():
    ap = argparse.ArgumentParser(description="CSJN Fallos Parser v16 (con mapa + fin real + fix fechas)")
    ap.add_argument("--localizados", required=True,
                    help="CSV con fallos localizados (output del cruce catalogo+mapa)")
    ap.add_argument("--mapa", required=True,
                    help="CSV con mapa de páginas (mapa_paginas.csv)")
    ap.add_argument("--corpus", required=True,
                    help="Directorio con los archivos LibroVol*.md")
    ap.add_argument("--output", default="../../output/parser/csjn_casos.csv",
                    help="CSV de salida (case-centered)")
    ap.add_argument("--output-votos", default=None,
                    help="CSV de salida (vote-centered). Default: <output>_votos.csv")
    args = ap.parse_args()

    # Cargar fallos del catálogo + cruce
    filas_loc, n_sin_loc = cargar_localizados(args.localizados)
    print(f"Fallos cargados desde {args.localizados}: {len(filas_loc)}")
    if n_sin_loc:
        print(f"  ({n_sin_loc} fallos descartados por status='pagina_no_en_mapa')")

    # Cargar mapa de páginas
    headers_por_archivo = cargar_proximos_headers(args.mapa)
    print(f"Archivos con headers en mapa: {len(headers_por_archivo)}")

    # Calcular primer_token_por_caso (para detección de carátula del siguiente)
    primer_token_por_caso = {
        row["caso_id_canonico"]: primer_token_de_caratula(row.get("nombres_indice", ""))
        for row in filas_loc
    }

    # Calcular siguiente_caso (cuál fallo del catálogo viene después en el
    # mismo tomo, ordenado por pagina_inicio)
    cat_por_tomo = {}
    for row in filas_loc:
        cat_por_tomo.setdefault(int(row["tomo"]), []).append({
            "caso_id_canonico": row["caso_id_canonico"],
            "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
        })
    for t in cat_por_tomo:
        cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
    siguiente_caso = {}
    for t, lst in cat_por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]

    # Agrupar por archivo
    grupos = agrupar_por_archivo(filas_loc, args.corpus)
    print(f"Archivos a procesar: {len(grupos)}")
    print()

    all_casos = []
    all_votos = []
    desconocidos_global = Counter()

    for filepath in sorted(grupos.keys(), key=lambda p: p.name):
        if not filepath.exists():
            print(f"  {filepath.name}... ARCHIVO NO ENCONTRADO en corpus, salteado")
            continue
        try:
            tamaño = filepath.stat().st_size
        except Exception:
            tamaño = 0
        if tamaño < 200:
            print(f"  {filepath.name}... [VACÍO/incompleto, salteado: {tamaño} bytes]")
            continue

        fallos_arch = grupos[filepath]
        # Headers del archivo (los del mismo tomo que las filas que vamos a procesar)
        # Si hay múltiples tomos en un archivo (raro), tomamos los headers de todos
        tomos_archivo = set(int(r["tomo"]) for r in fallos_arch)
        headers_archivo = []
        for t in tomos_archivo:
            headers_archivo.extend(headers_por_archivo.get((t, filepath.name), []))
        headers_archivo.sort()

        print(f"  {filepath.name}... {len(fallos_arch)} fallos →", end=" ", flush=True)
        try:
            casos, votos, descon = procesar_archivo(
                filepath, fallos_arch, headers_archivo,
                primer_token_por_caso, siguiente_caso
            )
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue
        all_casos.extend(casos)
        all_votos.extend(votos)
        desconocidos_global.update(descon)
        print(f"{len(casos)} procesados, {len(votos)} votos")

    # ── Output: caso-centered ─────────────────────────────────────────────────
    output_path = Path(args.output)
    if all_casos:
        fieldnames = [
            "caso_id_canonico", "tomo",
            "case_name_indice", "case_name_cuerpo", "case_name_cuerpo_legacy",
            "date", "apertura_tipo",
            "outcome", "voting_pattern",
            "n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
            "dictamen_presente", "is_originaria", "is_full_bench",
            "is_merit_decision",
            "word_count", "wc_mayoria", "wc_votos", "wc_considerando",
            "wc_dictamen",
            "firma_raw", "jueces", "jueces_conocidos", "jueces_desconocidos",
            "posiciones", "tribunal_origen", "tribunal_origen_status",
            "por_ello_text", "considerando_text",
            "source_file", "linea_inicio", "linea_fin", "linea_fin_real",
            "status_localizacion", "status_fin", "pista_fin",
            "tipo_entrada",
        ]
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in all_casos:
                writer.writerow(c)
        print(f"\n[OK] {output_path}: {len(all_casos)} casos")

    # ── Output: vote-centered ─────────────────────────────────────────────────
    output_votos_path = (Path(args.output_votos) if args.output_votos
                         else output_path.parent /
                              (output_path.stem + "_votos" + output_path.suffix))
    if all_votos:
        fieldnames_v = [
            "caso_id_canonico", "tomo", "date",
            "juez", "posicion", "es_conocido",
            "outcome", "voting_pattern", "is_originaria", "is_full_bench",
            "is_merit_decision", "wc_mayoria", "wc_votos",
            "dictamen_presente",
            "texto_voto", "wc_voto",
            "tipo_voto_sep", "fragmenta_ratio", "punto_divergencia",
        ]
        with output_votos_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_v)
            writer.writeheader()
            for v in all_votos:
                writer.writerow(v)
        print(f"[OK] {output_votos_path}: {len(all_votos)} filas (votos)")

    # ── Diagnóstico ───────────────────────────────────────────────────────────
    if all_casos:
        outcomes  = Counter(c["outcome"]        for c in all_casos)
        patterns  = Counter(c["voting_pattern"] for c in all_casos)
        statuses  = Counter(c["status_localizacion"] for c in all_casos)
        print("\n── Status de localización ──")
        for k, v in statuses.most_common():
            print(f"  {k:<35} {v:>5}")
        print("\n── Outcomes ──")
        for k, v in outcomes.most_common():
            print(f"  {k:<30} {v:>5}")
        print("\n── Voting patterns ──")
        for k, v in patterns.most_common():
            print(f"  {k:<30} {v:>5}")
        n_280 = outcomes.get("inadmisible_280", 0)
        n_a4  = outcomes.get("inadmisible_acordada_4", 0)
        n_des = outcomes.get("desestima", 0)
        print(f"\n── Gatekeeping ──")
        print(f"  inadmisible_280:           {n_280}")
        print(f"  inadmisible_acordada_4:    {n_a4}")
        print(f"  desestima (residual):      {n_des}")
        if n_280 + n_a4 > 0:
            total_gatekeep = n_280 + n_a4 + n_des
            print(f"  Tasa de gatekeeping ident: {100*(n_280+n_a4)/total_gatekeep:.1f}%")
        trib_status = Counter(c["tribunal_origen_status"] for c in all_casos)
        n_orig = sum(1 for c in all_casos if c["is_originaria"])
        n_sin_disp = outcomes.get("sin_dispositivo", 0)
        print(f"\n── Originaria + dispositivo ──")
        print(f"  is_originaria=1:           {n_orig}")
        print(f"  sin_dispositivo (residual):{n_sin_disp}")
        print(f"  tribunal_origen_status:")
        for k, v in trib_status.most_common():
            print(f"    {k:<22}      {v:>5}")

    if desconocidos_global:
        print("\n── Top desconocidos en firma (auditar) ──")
        for k, v in desconocidos_global.most_common(20):
            print(f"  {k!r:<60} {v:>3}")


if __name__ == "__main__":
    main()
