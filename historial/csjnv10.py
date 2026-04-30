"""
CSJN Fallos Parser v10
======================
Cambios respecto a v9:
  1. classify_outcome ahora recibe TANTO el dispositivo (por_ello_text) COMO
     el considerando (texto del cuerpo del fallo) para detectar inadmisible_280.
     El art. 280 figura en el considerando, no en el dispositivo.
  2. Nuevo outcome: inadmisible_acordada_4 (rechazos por art. 1 acordada 4/2007,
     formalismo del recurso de queja).
  3. CSV de votos enriquecido: nueva columna `texto_voto` con el texto íntegro
     del voto individual de cada juez. Permite análisis textual posterior
     (detección de templates, citas, etc.).
  4. Nueva columna `considerando_texto` en el CSV de casos: primeras N líneas
     después de "Considerando:" hasta "Por ello,". Necesaria para análisis
     léxico de fundamentos.

Uso:
  python csjnv10.py --input-dir . --output csjn_casos_v10.csv
  python csjnv10.py --files LibroVol344-2.md LibroVol349-1.md --output ...

Compatibilidad: produce los mismos campos que v9 más los nuevos. Reemplazable
en pipelines que esperaban v9.
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

RE_TRIB_ORIG = re.compile(r"^Tribunal\s+de\s+origen\s*:\s*(.*)$", re.I)

def find_tribunal_origen(lines, idx_inicio, idx_fin):
    for k in range(idx_inicio, min(idx_fin, len(lines))):
        m = RE_TRIB_ORIG.match(lines[k].strip())
        if m:
            tribunal = m.group(1).strip().rstrip(".")
            # Si la línea siguiente es una continuación natural, concatenar
            if k + 1 < len(lines):
                next_line = lines[k + 1].strip()
                if (next_line and not next_line.startswith("Tribunal")
                    and not RE_PAGE_HEADER.match(next_line)
                    and len(next_line) < 100
                    and not next_line.endswith(".")
                    and next_line[0].islower()):
                    tribunal += " " + next_line.rstrip(".")
            return tribunal
    return "SIN_TRIBUNAL_ORIGEN"

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

            # 3. Por ello — distinguir dispositivo de argumental
            if por_ello_idx is None and RE_POR_ELLO.match(stripped):
                rest    = re.sub(r"^Por ello[,.]\s*", "", stripped, flags=re.I)
                first_w = rest.split()[0].lower().rstrip(",;") if rest.split() else ""
                if first_w in POR_ELLO_ARGUMENTAL:
                    continue  # es argumental, ignorar
                por_ello_idx = k
                chunk = []
                for m2 in range(k, min(k + 6, len(bloque))):
                    chunk.append(bloque[m2])
                    if bloque[m2].strip().endswith("."):
                        break
                por_ello_text = " ".join(chunk).strip()

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
        is_originaria = int(
            tribunal_str == "SIN_TRIBUNAL_ORIGEN" or outcome == "originaria"
        )
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
            }
            votos_out.append(voto)

    return casos_out, votos_out, desconocidos_global

# ── Orquestación ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="CSJN Fallos Parser v10")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--input-dir", help="Directorio con archivos LibroVol*.md")
    g.add_argument("--files", nargs="+", help="Archivos .md específicos")
    ap.add_argument("--output", default="csjn_casos_v10.csv",
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
            "posiciones", "tribunal_origen", "por_ello_text",
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

    if desconocidos_global:
        print("\n── Top desconocidos en firma (auditar) ──")
        for k, v in desconocidos_global.most_common(20):
            print(f"  {k!r:<60} {v:>3}")


if __name__ == "__main__":
    main()
