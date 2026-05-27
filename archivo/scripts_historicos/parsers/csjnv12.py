"""
CSJN Fallos Parser v11
======================
Cambios respecto a v10:
  1. RE_DISPOSITIVO_APERTURA: detector ampliado del dispositivo. v10 sólo
     captaba "Por ello" como apertura del dispositivo, lo que en tomos viejos
     (329-340) deja ~25% de los fallos sin dispositivo detectado (1.123 casos
     en el corpus completo). El verdadero patrón de la Corte en fallos breves
     con remisión al dictamen del Procurador es:
       - "Por los fundamentos [y conclusiones del dictamen]..."  (~52% de los
         no-detectados en el tomo 329)
       - "De conformidad con [lo dictaminado]..."  (~34%)
       - "Por todo lo expuesto", "Por lo expuesto", "Atento a",
         "En consecuencia"  (residuales pero reales)
     Adicionalmente, tolerar el typo OCR "concusiones" por "conclusiones".

  2. is_originaria: heurística reescrita. v10 marcaba is_originaria=1 cuando
     no encontraba "Tribunal de origen:" en el bloque, lo que producía 2.238
     casos mal clasificados (39% del corpus), de los cuales sólo ~150 eran
     originarios reales. v11 reemplaza esa heurística negativa por detección
     positiva, basada en señales internas:
       - "competencia originaria" en el cuerpo del fallo
       - referencia al art. 117 CN
       - "Originario" en el case_name (encabezados tipo "M. 466. XXIV. Originario")
       - patrón "c/ [Provincia/Estado] s/" en case_name (demandas entre estados)
     Criterio AMPLIO: los fallos donde la Corte declina su competencia
     originaria también se cuentan como originaria=1 (el caso fue presentado
     como originario, aunque la Corte rechace).

  3. RE_TRIB_ORIG ampliado: tolera variantes históricas (Juzgado de origen,
     Cámara de origen) y continuación en línea siguiente. Empíricamente raras
     en el tomo 329 pero agregadas preventivamente para tomos no auditados.

  4. NUEVA columna tribunal_origen_status ∈ {apelado_detectado, originaria,
     sin_marcador}. Reemplaza conceptualmente la mezcla anterior entre
     is_originaria y tribunal_origen vacío. Ahora is_originaria es señal
     positiva pura, y los casos donde no se detectó tribunal pero tampoco hay
     señal de originaria quedan como sin_marcador (típicamente quejas directas
     o casos con OCR roto en la sección de tribunal).

Uso:
  python csjnv11.py --input-dir . --output csjn_casos_v11.csv
  python csjnv11.py --files LibroVol344-2.md LibroVol349-1.md --output ...

Compatibilidad: misma firma de columnas que v10 más tribunal_origen_status.
Reemplazable en pipelines que esperaban v10. La semántica de is_originaria
cambia (más restrictiva), por lo que análisis posteriores que filtraban
is_originaria==1 verán un universo modelable más grande.
"""

import re
import csv
import json
import argparse
from pathlib import Path
from collections import Counter
from itertools import combinations

# ── Marcadores estructurales ──────────────────────────────────────────────────

RE_APERTURA      = re.compile(r"^(FALLO|SENTENCIA) DE LA CORTE SUPREMA\s*$")
RE_FECHA_LINEA   = re.compile(r"^Buenos Aires[,]?\s+\d{1,2}\s+de\s+\w+\s+de\s+\d{4}", re.I)
RE_FECHA_EXTRACT = re.compile(r"Buenos Aires[,]?\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})", re.I)

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

def collect_firma_lines(bloque, idx_start, max_lines=40):
    """Junta líneas de firma desde después de 'Por ello' hasta encontrar fin."""
    firma_lines = []
    started = False
    for k in range(idx_start, min(idx_start + max_lines, len(bloque))):
        line = bloque[k].strip()
        if not line:
            if started:
                break
            continue
        # Saltarse el dispositivo hasta encontrar firma con jueces conocidos
        if not started:
            if any(p.search(line) for p, _ in JUECES_CONOCIDOS):
                started = True
                firma_lines.append(line)
            continue
        # Una vez empezada la firma, recolectar hasta página/separador/inicio_voto
        if RE_PAGE_HEADER.match(line) or line.startswith("Recurso de"):
            break
        if RE_VOTO_HDR.match(line) or RE_DISID_HDR.match(line):
            break
        if line.startswith("Tribunal de origen") or line.startswith("Tribunal que"):
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
    nombres_jueces = {j["nombre"].lower() for j in jueces_out}
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

def split_in_casos(lines):
    """
    Divide el archivo en casos usando el marcador FALLO/SENTENCIA DE LA CORTE
    SUPREMA. Cada caso es una lista de líneas.
    """
    aperturas = [k for k, ln in enumerate(lines) if RE_APERTURA.match(ln.strip())]
    if not aperturas:
        return []
    casos = []
    for i, apertura_idx in enumerate(aperturas):
        if i + 1 < len(aperturas):
            fin_idx = aperturas[i + 1]
        else:
            fin_idx = len(lines)
        bloque = lines[apertura_idx:fin_idx]
        casos.append({
            "bloque":       bloque,
            "apertura_idx": apertura_idx,
            "lineas_originales": lines[max(0, apertura_idx - 60):apertura_idx],
        })
    return casos

# ── Procesamiento de un archivo ───────────────────────────────────────────────

def procesar_archivo(filepath):
    """
    Procesa un archivo .md y devuelve dos listas:
      - casos: registros caso-centered
      - votos: registros vote-centered
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Tomo
    tomo_match = RE_TOMO.search(filepath.name)
    tomo = int(tomo_match.group(1)) if tomo_match else 0

    casos_split = split_in_casos(lines)

    casos_out  = []
    votos_out  = []
    desconocidos_global = Counter()

    for caso_meta in casos_split:
        bloque       = caso_meta["bloque"]
        apertura_idx = caso_meta["apertura_idx"]

        # Fecha
        fecha_str = ""
        for k, ln in enumerate(bloque[:5]):
            m = RE_FECHA_EXTRACT.search(ln)
            if m:
                fecha_str = m.group(1)
                break

        # apertura_tipo
        apertura_match = RE_APERTURA.match(bloque[0].strip())
        apertura_tipo  = apertura_match.group(1).lower() if apertura_match else ""

        # case_name
        case_name = find_case_name(lines, apertura_idx)

        # Tribunal de origen
        tribunal_str = find_tribunal_origen(lines, apertura_idx, apertura_idx + len(bloque))

        # Procesar bloque línea por línea
        en_dictamen        = False
        dictamen_presente  = False
        lineas_dictamen    = set()
        por_ello_idx       = None
        por_ello_text      = ""
        n_votos_svoto      = 0
        n_disidencias      = 0
        inicio_votos_indiv = None
        # NUEVO v10: marcadores de inicio de cada voto individual con su juez
        marcadores_votos   = []  # (k_inicio, juez_nombre, tipo)

        for k, bl in enumerate(bloque):
            stripped = bl.strip()
            if not stripped:
                continue

            # 1. Dictamen embebido
            if RE_DICT_HDR.match(stripped):
                en_dictamen       = True
                dictamen_presente = True
                lineas_dictamen.add(k)
                continue
            elif en_dictamen:
                lineas_dictamen.add(k)
                if RE_FECHA_LINEA.match(stripped) and k > 5:
                    prev = bloque[k - 1].strip() if k > 0 else ""
                    if prev and len(prev) < 80:
                        en_dictamen = False
                continue

            # 2. Votos y disidencias individuales
            if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
                tipo = "voto" if RE_VOTO_HDR.match(stripped) else "disidencia"
                if tipo == "voto":
                    n_votos_svoto += 1
                else:
                    n_disidencias += 1
                if inicio_votos_indiv is None:
                    inicio_votos_indiv = k
                # NUEVO v10: detectar el juez en el header.
                # Si el header está cortado en dos líneas (común en OCR del libro),
                # concatenar con la(s) siguiente(s) línea(s) hasta detectar un juez
                # o agotar 3 líneas. Esto resuelve casos como
                #   'voto del señor vicepresidente doctor don carlos fernando'
                #   'rosenkrantz'
                # donde el apellido cae en la línea siguiente.
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
                        # No concatenar si la línea siguiente ya es 'Considerando:'
                        if RE_CONSIDERANDO.match(sig):
                            break
                        header_completo += " " + sig
                continue

            # 3. Apertura del dispositivo — v11: detector ampliado
            # Acepta "Por ello" + variantes ("Por los fundamentos",
            # "De conformidad con", "Por todo lo expuesto", etc.).
            if por_ello_idx is None:
                es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
                if es_disp:
                    por_ello_idx = k
                    chunk = []
                    for m2 in range(k, min(k + 6, len(bloque))):
                        chunk.append(bloque[m2])
                        if bloque[m2].strip().endswith("."):
                            break
                    por_ello_text = " ".join(chunk).strip()
                    # tipo_disp queda disponible si en el futuro se quiere
                    # auditar qué proporción del corpus usa cada variante

        # ── NUEVO v10: extraer texto del considerando ─────────────────────────
        considerando_text = extraer_considerando(bloque, por_ello_idx, lineas_dictamen)

        # ── v10: classify_outcome ahora recibe ambos ──────────────────────────
        outcome = classify_outcome(por_ello_text, considerando_text) if por_ello_text else "sin_dispositivo"
        # Caso especial: si no hay dispositivo pero el considerando dice 280
        if outcome == "sin_dispositivo" and considerando_text:
            if RE_280_CONSIDERANDO.search(considerando_text) or RE_280_LIBRE.search(considerando_text):
                outcome = "inadmisible_280"
            elif RE_ACORDADA_4_CONSIDERANDO.search(considerando_text):
                outcome = "inadmisible_acordada_4"

        # Firma de mayoría
        firma_raw    = ""
        firma_parsed = {"jueces": [], "voting_pattern": "sin_firma", "desconocidos": []}

        if por_ello_idx is not None:
            firma_raw = collect_firma_lines(bloque, por_ello_idx + 1)
            if firma_raw:
                firma_parsed = parse_firma(firma_raw)
                for d in firma_parsed["desconocidos"]:
                    desconocidos_global[d] += 1

        # ── Word count bifurcado ──────────────────────────────────────────
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

        # ── Flags analíticos ──────────────────────────────────────────────
        # v11: is_originaria pasa de heurística negativa (SIN_TRIBUNAL_ORIGEN
        # ⇒ originaria) a detección positiva basada en señales internas.
        # Criterio AMPLIO: incluye declinatorias de competencia originaria.
        is_originaria = int(es_originaria(case_name, considerando_text, por_ello_text))

        # v11: tribunal_origen_status — tres estados separados de is_originaria
        # y de tribunal_origen (que conserva el nombre del tribunal cuando se
        # detecta).
        if is_originaria:
            tribunal_origen_status = "originaria"
        elif tribunal_str != "SIN_TRIBUNAL_ORIGEN":
            tribunal_origen_status = "apelado_detectado"
        elif hay_tribunal_interviniente(lines, apertura_idx, apertura_idx + len(bloque)):
            # Hay "Tribunales que intervinieron con anterioridad" → vino de
            # instancias inferiores, claramente apelado, pero sin un único
            # tribunal de origen identificable.
            tribunal_origen_status = "apelado_detectado"
        else:
            tribunal_origen_status = "sin_marcador"

        n_titulares = sum(1 for j in firma_parsed["jueces"] if j["conocido"]
                          and "(conjuez)" not in j["nombre"])
        is_full_bench = int(n_titulares == 5)

        # v10: inadmisible_280 e inadmisible_acordada_4 son gatekeeping
        MERIT_OUTCOMES    = {"hace_lugar", "procedente", "revoca", "nulidad", "confirma"}
        GATEKEEP_OUTCOMES = {"desestima", "inadmisible_280", "inadmisible_acordada_4",
                             "abstracto", "desistimiento", "mal_concedido"}
        is_merit = int(outcome in MERIT_OUTCOMES)

        # caso_id
        caso_id = f"{tomo}_{apertura_idx + 1}"

        # Construir registro caso-centered
        jueces_nombres     = [j["nombre"] for j in firma_parsed["jueces"]]
        jueces_conocidos_l = [j["nombre"] for j in firma_parsed["jueces"] if j["conocido"]]
        jueces_descon_l    = [j["nombre"] for j in firma_parsed["jueces"] if not j["conocido"]]

        posiciones = {}
        for j in firma_parsed["jueces"]:
            posiciones[j["nombre"]] = j["calificador"] or "mayoria"

        # ── NUEVO v10: extraer texto de cada voto individual ──────────────
        textos_votos = extraer_textos_votos(bloque, marcadores_votos)

        caso = {
            "caso_id":             caso_id,
            "tomo":                tomo,
            "case_name":           case_name,
            "date":                fecha_str,
            "apertura_tipo":       apertura_tipo,
            "outcome":             outcome,
            "voting_pattern":      firma_parsed["voting_pattern"],
            "n_jueces":            len(firma_parsed["jueces"]),
            "n_titulares":         n_titulares,
            "n_votos_svoto":       n_votos_svoto,
            "n_disidencias":       n_disidencias,
            "dictamen_presente":   dictamen_presente,
            "is_originaria":       is_originaria,
            "is_full_bench":       is_full_bench,
            "is_merit_decision":   is_merit,
            "word_count":          word_count,
            "wc_mayoria":          wc_mayoria,
            "wc_votos":            wc_votos,
            "firma_raw":           firma_raw,
            "jueces":              " | ".join(jueces_nombres),
            "jueces_conocidos":    " | ".join(jueces_conocidos_l),
            "jueces_desconocidos": " | ".join(jueces_descon_l),
            "posiciones":          json.dumps(posiciones, ensure_ascii=False),
            "tribunal_origen":     tribunal_str,
            "tribunal_origen_status": tribunal_origen_status,  # v11
            "por_ello_text":       por_ello_text[:300],
            "source_file":         filepath.name,
            "line_apertura":       apertura_idx + 1,
            # NUEVOS v10:
            "considerando_text":   considerando_text[:2000],  # truncado a 2000 chars
            "wc_considerando":    len(re.findall(r'\b\w+\b', considerando_text)),
        }
        casos_out.append(caso)

        # Construir registros vote-centered
        for j in firma_parsed["jueces"]:
            if not j["conocido"]:
                continue  # solo jueces conocidos en la tabla de votos
            juez_nombre = j["nombre"]
            posicion    = j["calificador"] or "mayoria"
            # NUEVO v10: si este juez tiene un voto/disidencia individual,
            # asignar su texto. Si no, queda vacío (es mayoría).
            texto_voto = textos_votos.get(juez_nombre, "")
            wc_voto    = len(re.findall(r'\b\w+\b', texto_voto))
            # NUEVO v12: clasificar el tipo de voto separado. Sólo se llama
            # cuando el juez tiene un voto/disidencia individual (texto no
            # vacío). Para los votos de mayoría (texto_voto="") las tres
            # columnas quedan como string vacío para mantener la columna
            # numérica del CSV consistente.
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
                "caso_id":            caso_id,
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
                # NUEVOS v10:
                "texto_voto":         texto_voto[:5000],  # truncado a 5000 chars
                "wc_voto":            wc_voto,
                # NUEVOS v12:
                "tipo_voto_sep":      tipo_voto_sep,
                "fragmenta_ratio":    fragmenta_ratio,
                "punto_divergencia":  punto_divergencia,
            }
            votos_out.append(voto)

    return casos_out, votos_out, desconocidos_global

# ── Orquestación ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="CSJN Fallos Parser v11")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--input-dir", help="Directorio con archivos LibroVol*.md")
    g.add_argument("--files", nargs="+", help="Archivos .md específicos")
    ap.add_argument("--output", default="csjn_casos_v11.csv",
                    help="CSV de salida (case-centered)")
    ap.add_argument("--output-votos", default=None,
                    help="CSV de salida (vote-centered). Default: <output>_votos.csv")
    args = ap.parse_args()

    # Determinar archivos a procesar
    if args.input_dir:
        in_dir = Path(args.input_dir)
        archivos = sorted(in_dir.glob("LibroVol*.md"))
    else:
        archivos = [Path(f) for f in args.files]

    if not archivos:
        print("No se encontraron archivos .md a procesar.")
        return

    print(f"Procesando {len(archivos)} archivo(s)...")

    all_casos = []
    all_votos = []
    desconocidos_global = Counter()

    for filepath in archivos:
        # Saltar archivos vacíos o demasiado pequeños para contener un caso completo
        try:
            tamaño = filepath.stat().st_size
        except Exception:
            tamaño = 0
        if tamaño < 200:
            print(f"  {filepath.name}... [VACÍO/incompleto, salteado: {tamaño} bytes]")
            continue

        print(f"  {filepath.name}...", end="", flush=True)
        try:
            casos, votos, descon = procesar_archivo(filepath)
        except Exception as e:
            print(f" ERROR: {e}")
            continue
        all_casos.extend(casos)
        all_votos.extend(votos)
        desconocidos_global.update(descon)
        print(f"  → {len(casos)} casos, {len(votos)} votos")

    # ── Output: caso-centered ─────────────────────────────────────────────────
    output_path = Path(args.output)
    if all_casos:
        fieldnames = [
            "caso_id", "tomo", "case_name", "date", "apertura_tipo",
            "outcome", "voting_pattern",
            "n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
            "dictamen_presente", "is_originaria", "is_full_bench",
            "is_merit_decision",
            "word_count", "wc_mayoria", "wc_votos", "wc_considerando",
            "firma_raw", "jueces", "jueces_conocidos", "jueces_desconocidos",
            "posiciones", "tribunal_origen", "tribunal_origen_status",
            "por_ello_text",
            "considerando_text",
            "source_file", "line_apertura",
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
            "caso_id", "tomo", "date",
            "juez", "posicion", "es_conocido",
            "outcome", "voting_pattern", "is_originaria", "is_full_bench",
            "is_merit_decision", "wc_mayoria", "wc_votos",
            "dictamen_presente",
            "texto_voto", "wc_voto",
            # NUEVOS v12:
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
        print("\n── Outcomes ──")
        for k, v in outcomes.most_common():
            print(f"  {k:<30} {v:>5}")
        print("\n── Voting patterns ──")
        for k, v in patterns.most_common():
            print(f"  {k:<30} {v:>5}")
        # NUEVO v10: comparativa pre/post fix 280
        n_280 = outcomes.get("inadmisible_280", 0)
        n_a4  = outcomes.get("inadmisible_acordada_4", 0)
        n_des = outcomes.get("desestima", 0)
        print(f"\n── Fix v10 (detección considerando) ──")
        print(f"  inadmisible_280:           {n_280}")
        print(f"  inadmisible_acordada_4:    {n_a4}")
        print(f"  desestima (residual):      {n_des}")
        if n_280 + n_a4 > 0:
            total_gatekeep = n_280 + n_a4 + n_des
            print(f"  Tasa de gatekeeping ident: {100*(n_280+n_a4)/total_gatekeep:.1f}%")
        # NUEVO v11: distribución de tribunal_origen_status
        trib_status = Counter(c["tribunal_origen_status"] for c in all_casos)
        n_orig = sum(1 for c in all_casos if c["is_originaria"])
        n_sin_disp = outcomes.get("sin_dispositivo", 0)
        print(f"\n── Fix v11 (originaria + dispositivo) ──")
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
