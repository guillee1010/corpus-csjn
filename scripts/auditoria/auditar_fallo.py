"""
auditar_fallo.py — Auditoría manual de bloques del corpus CSJN
================================================================

Herramienta de inspección humana sobre cómo el parser segmenta el bloque de
un fallo. Para cada caso, particiona el bloque en spans tipados (carátula,
sumarios, dictamen, cuerpo de mayoría, votos, disidencias, firma, headers
de página, sumario_con_link) y emite un catch-all explícito con todo lo
que la heurística del parser no logra clasificar.

Doble propósito:
  1. Output legible (Markdown) para inspección caso por caso.
  2. API canónica `auditar_fallo(tomo, pagina) -> dict` para uso
     programático en análisis estadísticos futuros.

CRÍTICO — relación con parser.py:
  Este script REUSA por importación los regex y helpers de parser.py.
  No reimplementa heurísticas. Si una heurística está rota en parser.py,
  acá va a estar igual de rota — y el catch-all lo va a delatar. Esa es
  precisamente la función de la auditoría.

CLI:
  python auditar_fallo.py --tomo 349 --pagina 309
  python auditar_fallo.py --tomo 349 --pagina 306,309,1066
  python auditar_fallo.py --random 5 [--tomo 344] [--status ok_cortado_en_indice]

Output:
  Default → archivo en scripts/auditoria/output/auditoria_<timestamp>.md
  --stdout → imprime a terminal
  --output <ruta> → fuerza ruta específica

Convenciones:
  - linea_inicio / linea_fin son 0-indexed (igual que parser.py).
  - Los spans son disjuntos excepto header_pagina, que es transversal.
  - Invariante de cobertura: toda línea del rango [linea_inicio, linea_fin_real]
    pertenece a al menos un span (eventualmente catch_all).
"""

import argparse
import csv
import json
import random
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# ── Importar parser.py (fuente única de verdad para heurísticas) ──────────────

# El script vive en scripts/auditoria/, parser.py vive en scripts/pipeline/.
# Agregamos scripts/ al sys.path para poder importar pipeline.parser.
_AUDITORIA_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _AUDITORIA_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from pipeline.parser import (  # noqa: E402
    RE_APERTURA,
    RE_FECHA_LINEA,
    RE_CONSIDERANDO,
    RE_DICT_HDR,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    RE_SUMARIO_LINK,
    RE_PAGE_HEADER,
    RE_TOMO,
    RE_VISTOS_LOS_AUTOS,
    detectar_apertura_dispositivo,
    detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion,
    detectar_fin_real,
    cargar_proximos_headers,
    cargar_localizados,
    proximo_header_despues_de,
    primer_token_de_caratula,
    linea_es_header_sumario,
    linea_es_firma_de_juez,
    JUECES_CONOCIDOS,
)

# ── Rutas default (relativas al repo) ─────────────────────────────────────────
# Asumiendo layout: <repo>/scripts/auditoria/auditar_fallo.py
# Si el layout cambia, override con --corpus / --localizados / --mapa.

_REPO_ROOT = _SCRIPTS_DIR.parent
DEFAULT_CORPUS = _REPO_ROOT / "corpus"
DEFAULT_LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
DEFAULT_MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output" / "auditoria" / "auditar_fallo"

# ── Tipos de span (10) ────────────────────────────────────────────────────────
# Orden no semántico: solo para documentación.

TIPO_CARATULA = "caratula"
TIPO_SUMARIO = "sumario"
TIPO_DICTAMEN = "dictamen"
TIPO_CUERPO_MAYORIA = "cuerpo_mayoria"
TIPO_VOTO = "voto"
TIPO_DISIDENCIA = "disidencia"
TIPO_FIRMA = "firma"
TIPO_SUMARIO_CON_LINK = "sumario_con_link"
TIPO_HEADER_PAGINA = "header_pagina"
TIPO_CATCH_ALL = "catch_all"

TIPOS_SEMANTICOS = {  # disjuntos entre sí, excluyen TIPO_HEADER_PAGINA y TIPO_CATCH_ALL
    TIPO_CARATULA, TIPO_SUMARIO, TIPO_DICTAMEN, TIPO_CUERPO_MAYORIA,
    TIPO_VOTO, TIPO_DISIDENCIA, TIPO_FIRMA, TIPO_SUMARIO_CON_LINK,
}

# ── Detector borde_inferior (transición fin_real → próximo caso) ──────────────
#
# Inspecciona la franja entre `linea_fin_real` (lo que el parser declara como
# fin del fallo X) y `linea_inicio` del fallo siguiente, según el catálogo.
# Su trabajo es detectar residuo del fallo X que el parser dejó "del otro
# lado" del corte: típicamente continuaciones de firma multilínea (caso
# paradigmático 339_p1648), pero también votos/disidencias huérfanos o
# carátulas adelantadas. Es una herramienta DE AUDITORÍA: no corrige el
# parser, solo expone lo que el parser está tirando al residuo del próximo
# caso.
#
# Diseñado en BITACORA H018 (sesión 2026-05-09). Implementado en sesión
# 2026-05-10. Ver H018 para la discusión completa de criterios.

# Apellidos canónicos de ministros titulares CSJN (Tomos 344-349 + retroactivo).
# Se usa para detectar continuaciones de firma multilínea que cayeron del
# lado de "después de fin_real". Capturado en MAYÚSCULAS para match
# case-insensitive contra cualquier formato (Title Case, ALL CAPS).
APELLIDOS_FIRMA_TITULARES = {
    "ROSATTI", "ROSENKRANTZ", "LORENZETTI", "MAQUEDA",
    "HIGHTON", "NOLASCO", "MANSILLA",
    "ZAFFARONI", "PETRACCHI", "ARGIBAY", "FAYT",
    "BOGGIANO", "BELLUSCIO", "LÓPEZ", "LOPEZ",
    "VÁZQUEZ", "VAZQUEZ", "NAZARENO",
}

# Umbral para distinguir gap de transición editorial normal (header_normal)
# de gap_grande_solo_headers (anomalía estructural: hueco grande lleno solo
# de headers, sugiere tomo con espacios "decorativos"). Ver H018.
UMBRAL_GAP_RESIDUO = 4

# Clasificaciones posibles de líneas del gap (orden de prioridad en
# _clasificar_linea_gap).
CLAS_VACIA = "vacia"
CLAS_HEADER_PAGINA = "header_pagina"
CLAS_APERTURA_PROXIMO = "apertura_proximo_caso"
CLAS_VOTO_DISID_INDIV = "voto_disidencia_individual"
CLAS_FIRMA_ARRASTRADA = "firma_arrastrada"
CLAS_NO_CLASIFICABLE = "no_clasificable"

# Estados del borde inferior.
EST_CONTINUO = "continuo"
EST_HEADER_NORMAL = "header_normal"
EST_GAP_RESIDUO = "gap_con_residuo"
EST_GAP_SOLO_HEADERS = "gap_grande_solo_headers"
EST_SOLAPADO = "solapado_con_proximo"
EST_FIN_ARCHIVO = "fin_archivo"


def linea_es_continuacion_firma(linea):
    """
    Detecta si una línea suelta es una continuación de firma multilínea
    (cola de un bloque de firma cuya cabecera quedó del lado del fallo X
    y cuya cola cayó después de `linea_fin_real`).

    Caso paradigmático (339_p1648, línea 26599):
        "Carlos Maqueda."

    Criterio (H018):
      (1) Hay al menos un apellido del set APELLIDOS_FIRMA_TITULARES
          presente en la línea (match case-insensitive sobre la palabra
          completa).
      (2) Compatibilidad discursiva: cumple ALGUNA de —
            (a) ratio de mayúsculas ≥ 70% sobre las letras de la línea
                (firma en formato ALL CAPS, ej. "JUAN CARLOS MAQUEDA"),
            (b) longitud ≤ 80 caracteres y termina en punto o em-dash o
                guión largo,
            (c) contiene em-dash (\u2013) o m-dash (\u2014) que es el
                separador típico entre firmantes en el formato Fallos.

    Devuelve bool.
    """
    s = linea.strip()
    if not s:
        return False

    # (1) Presencia de apellido titular (case-insensitive, palabra completa).
    s_upper = s.upper()
    apellido_presente = False
    for ap in APELLIDOS_FIRMA_TITULARES:
        # \b sobre Unicode mayúsculas funciona bien con re.UNICODE (default
        # en Python 3 para str). Evitamos subcadenas accidentales.
        if re.search(r"\b" + re.escape(ap) + r"\b", s_upper):
            apellido_presente = True
            break
    if not apellido_presente:
        return False

    # (2) Compatibilidad discursiva — basta con una.
    letras = [c for c in s if c.isalpha()]
    if letras:
        n_mayus = sum(1 for c in letras if c.isupper())
        ratio_mayus = n_mayus / len(letras)
    else:
        ratio_mayus = 0.0

    cumple_a = ratio_mayus >= 0.70
    cumple_b = len(s) <= 80 and (s.endswith(".") or s.endswith("\u2013")
                                 or s.endswith("\u2014") or s.endswith("-"))
    cumple_c = ("\u2013" in s) or ("\u2014" in s)

    return cumple_a or cumple_b or cumple_c


def _clasificar_linea_gap(linea, primer_token_siguiente):
    """
    Clasifica una línea del gap entre `linea_fin_real` y `linea_inicio` del
    próximo caso. El orden de las pruebas implementa la prioridad fijada en
    H018:

      1. vacia              (línea en blanco o solo whitespace)
      2. header_pagina      (RE_PAGE_HEADER del parser)
      3. apertura_proximo_caso  (RE_VISTOS_LOS_AUTOS o primer_token_siguiente)
      4. voto_disidencia_individual  (RE_VOTO_HDR / RE_DISID_HDR)
      5. firma_arrastrada   (linea_es_continuacion_firma)
      6. no_clasificable    (catch-all; suele ser texto en cuerpo de
                             dispositivo/párrafo final que el parser cortó
                             antes de tiempo)

    Notar el orden: header_pagina ANTES que firma, porque "339" como línea
    sola es header de página, no firma. apertura_proximo_caso ANTES que
    firma porque la carátula del próximo caso a veces contiene apellidos
    del set (ej. "MAQUEDA" en una causa donde es parte). voto/disid ANTES
    que firma porque un header de voto puede contener "Maqueda" en el
    encabezado ("Voto del señor ministro doctor don Juan Carlos Maqueda").

    `primer_token_siguiente` puede ser "" si no se pudo calcular; en ese
    caso solo se usa RE_VISTOS_LOS_AUTOS para detectar apertura.
    """
    s = linea.strip()
    if not s:
        return CLAS_VACIA
    if RE_PAGE_HEADER.match(s):
        return CLAS_HEADER_PAGINA
    if RE_VISTOS_LOS_AUTOS.match(s):
        return CLAS_APERTURA_PROXIMO
    if primer_token_siguiente and len(primer_token_siguiente) >= 5:
        if re.search(r"\b" + re.escape(primer_token_siguiente) + r"\b", s, re.I):
            return CLAS_APERTURA_PROXIMO
    if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
        return CLAS_VOTO_DISID_INDIV
    if linea_es_continuacion_firma(s):
        return CLAS_FIRMA_ARRASTRADA
    return CLAS_NO_CLASIFICABLE


def detectar_borde_inferior(lines, linea_fin_real, linea_inicio_proximo_caso,
                            primer_token_siguiente):
    """
    Inspecciona la franja entre `linea_fin_real` (inclusive) y
    `linea_inicio_proximo_caso` (exclusivo) y produce un diagnóstico
    estructurado. Ver el bloque de comentario al inicio de esta sección
    para el contexto.

    Parámetros:
      lines: lista global de líneas del archivo .md (0-indexed).
      linea_fin_real: índice 0-based de la última línea declarada como
                      contenido del fallo X.
      linea_inicio_proximo_caso: índice 0-based del inicio del bloque del
                                 fallo X+1 según el catálogo de localización.
                                 None si X es el último caso del archivo.
      primer_token_siguiente: string ya calculado vía
                              primer_token_de_caratula(); puede ser "".

    Devuelve dict con la estructura definida en H018:
      {
        "linea_fin_real": int,
        "linea_inicio_proximo_caso": int | None,
        "delta": int,
        "estado": str (uno de EST_*),
        "lineas_gap": list[dict],
        "alertas": list[str],
      }

    Nota sobre `linea_abs` en lineas_gap: se reporta como índice 0-based
    del archivo, consistente con linea_fin_real y linea_inicio (otros
    campos del catálogo). El renderer suma offset si corresponde.
    """
    alertas = []

    # Caso terminal: fallo X es el último del archivo. No hay próximo caso
    # contra el cual medir gap.
    if linea_inicio_proximo_caso is None:
        return {
            "linea_fin_real": linea_fin_real,
            "linea_inicio_proximo_caso": None,
            "delta": 0,
            "estado": EST_FIN_ARCHIVO,
            "lineas_gap": [],
            "alertas": alertas,
        }

    delta = linea_inicio_proximo_caso - linea_fin_real - 1

    # Caso solapado: el catálogo del próximo caso empieza ANTES o EN la
    # línea declarada como fin del fallo X. Es una inconsistencia del
    # catálogo o del detector_fin_real (F011). Alerta crítica.
    if delta < 0:
        alertas.append("solapado_con_proximo")
        return {
            "linea_fin_real": linea_fin_real,
            "linea_inicio_proximo_caso": linea_inicio_proximo_caso,
            "delta": delta,
            "estado": EST_SOLAPADO,
            "lineas_gap": [],
            "alertas": alertas,
        }

    # Caso continuo: pegado, sin franja de transición.
    if delta == 0:
        return {
            "linea_fin_real": linea_fin_real,
            "linea_inicio_proximo_caso": linea_inicio_proximo_caso,
            "delta": 0,
            "estado": EST_CONTINUO,
            "lineas_gap": [],
            "alertas": alertas,
        }

    # delta > 0: hay franja entre fin_real y inicio del próximo. Clasificar
    # cada línea por contenido y decidir estado por composición.
    lineas_gap = []
    for ln_abs in range(linea_fin_real + 1, linea_inicio_proximo_caso):
        if 0 <= ln_abs < len(lines):
            texto = lines[ln_abs].rstrip("\r\n")
        else:
            texto = ""
        clas = _clasificar_linea_gap(texto, primer_token_siguiente)
        lineas_gap.append({
            "linea_abs": ln_abs,
            "clasificacion": clas,
            "texto": texto,
        })

    # Las "benignas" son las que NO indican residuo del fallo X.
    BENIGNAS = {CLAS_VACIA, CLAS_HEADER_PAGINA}

    no_benignas = [g for g in lineas_gap if g["clasificacion"] not in BENIGNAS]

    if no_benignas:
        estado = EST_GAP_RESIDUO

        # Alerta: firma multilínea partida por fin_real.
        # Si la primera línea no-vacía del gap es firma_arrastrada, hay
        # alta probabilidad de que detectar_fin_real haya cortado en medio
        # de un bloque de firma (F010).
        primera_no_vacia = next(
            (g for g in lineas_gap if g["clasificacion"] != CLAS_VACIA),
            None,
        )
        if primera_no_vacia and primera_no_vacia["clasificacion"] == CLAS_FIRMA_ARRASTRADA:
            alertas.append("firma_multilinea_partida_por_fin_real")

        # Alerta: apellido repetido en firma arrastrada.
        # Dentro de spans contiguos de firma_arrastrada, contar apariciones
        # de cada apellido titular. Si alguno aparece ≥2 veces, es señal
        # de que el detector concatenó dos firmas separadas (raro pero
        # diagnóstico).
        spans_firma = []
        actual = []
        for g in lineas_gap:
            if g["clasificacion"] == CLAS_FIRMA_ARRASTRADA:
                actual.append(g)
            else:
                if actual:
                    spans_firma.append(actual)
                    actual = []
        if actual:
            spans_firma.append(actual)

        for span in spans_firma:
            counter_apellidos = Counter()
            for g in span:
                s_up = g["texto"].upper()
                for ap in APELLIDOS_FIRMA_TITULARES:
                    if re.search(r"\b" + re.escape(ap) + r"\b", s_up):
                        counter_apellidos[ap] += 1
            if any(v >= 2 for v in counter_apellidos.values()):
                alertas.append("apellido_repetido_en_firma_arrastrada")
                break

        # Alerta: voto/disidencia individual en gap.
        if any(g["clasificacion"] == CLAS_VOTO_DISID_INDIV for g in lineas_gap):
            alertas.append("voto_disidencia_individual_en_gap")

        # Alerta: carátula del próximo caso adelantada al gap.
        if any(g["clasificacion"] == CLAS_APERTURA_PROXIMO for g in lineas_gap):
            alertas.append("caratula_siguiente_en_gap")

    else:
        # Todas las líneas del gap son benignas (vacia o header_pagina).
        if delta <= UMBRAL_GAP_RESIDUO:
            estado = EST_HEADER_NORMAL
        else:
            estado = EST_GAP_SOLO_HEADERS
            alertas.append("gap_grande_sin_residuo_aparente")

    return {
        "linea_fin_real": linea_fin_real,
        "linea_inicio_proximo_caso": linea_inicio_proximo_caso,
        "delta": delta,
        "estado": estado,
        "lineas_gap": lineas_gap,
        "alertas": alertas,
    }


# ── Versión robusta documentada (NO IMPLEMENTADA — reserva para iteración) ───
#
# La implementación actual de detectar_borde_inferior() asume que
# `linea_fin_real` proveniente de detectar_fin_real() es razonablemente
# correcta y solo audita la franja "más allá" del corte. Esto deja
# vulnerabilidades a bugs heredados del parser: si detectar_fin_real()
# devuelve una línea claramente prematura (ej. corta en medio del cuerpo
# del fallo X, no en la firma), el detector la va a tomar al pie de la
# letra y reportar falsos positivos de tipo "firma_multilinea_partida".
#
# La VERSIÓN ROBUSTA, no implementada acá, agregaría una ventana de
# búsqueda de cierre estructural alrededor de linea_fin_real:
#
#   1. Buscar en [linea_fin_real - W, linea_fin_real + W] (W~10) la línea
#      que más probable cierra el fallo (firma completa, dispositivo
#      cerrado con punto final, "Hágase saber.", etc.).
#   2. Reportar dos cierres: el del parser y el "estructuralmente probable",
#      con su delta entre sí.
#   3. Si difieren en > UMBRAL_DESVIO_PARSER (ej. 5 líneas), emitir
#      alerta `desvio_estructural_significativo` y elevar la criticidad
#      del span de borde.
#
# Criterio para activar: si la corrida `--random 50` con el detector
# actual muestra > 10% de falsos positivos en `firma_multilinea_partida_por_fin_real`
# (verificado por inspección humana), implementar la versión robusta.
# Hasta entonces, la versión simple es preferible: menos código que
# debuggear y sus falsos positivos son interpretables (siempre apuntan a
# F010 o F011).

# ── Detección de span "header de página" (transversal) ────────────────────────

# RE_PAGE_HEADER ya está importado del parser. Lo extendemos con el patrón de
# 1-3 dígitos como línea sola (que también es header en el formato de Fallos).
# Los headers típicos de Fallos tienen 3 líneas consecutivas:
#   <numero pagina>
#   FALLOS DE LA CORTE SUPREMA  ó  DE JUSTICIA DE LA NACIÓN
#   <numero tomo>
# (en cualquier orden). RE_PAGE_HEADER del parser cubre las tres formas.

def detectar_headers_pagina(bloque, headers_archivo, linea_inicio_abs):
    """
    Devuelve set de índices RELATIVOS al bloque que son headers de página.

    Estrategia: primero cruzar con headers_archivo (autoridad) — si la línea
    está en el mapa, es header de página. Después scanear el bloque para
    detectar líneas que matcheen RE_PAGE_HEADER y tomen el patrón de "número
    suelto" (1-4 dígitos). Esto recupera headers que no están en el mapa
    (raro, pero pasa cuando el mapa quedó incompleto).
    """
    indices = set()

    # 1. Autoridad: mapa_paginas.csv
    for ln_abs, _pg in headers_archivo:
        ln_rel = ln_abs - linea_inicio_abs
        if 0 <= ln_rel < len(bloque):
            indices.add(ln_rel)
            # El "header" típico ocupa 3 líneas: número de página, frase
            # institucional, número de tomo. Marcamos la línea del mapa Y
            # las dos adyacentes si matchean el patrón.
            for offset in (-1, 1, 2):
                k = ln_rel + offset
                if 0 <= k < len(bloque):
                    s = bloque[k].strip()
                    if RE_PAGE_HEADER.match(s):
                        indices.add(k)

    # 2. Barrido auxiliar: cualquier línea que sea solo dígitos (1-4) o que
    #    matchee RE_PAGE_HEADER y esté rodeada de líneas que también lo son.
    for k, ln in enumerate(bloque):
        s = ln.strip()
        if RE_PAGE_HEADER.match(s):
            # Confirmar que no es una mención casual: chequear si línea
            # adyacente también matchea, lo cual es señal de header real.
            if (k > 0 and RE_PAGE_HEADER.match(bloque[k - 1].strip())) or \
               (k + 1 < len(bloque) and RE_PAGE_HEADER.match(bloque[k + 1].strip())):
                indices.add(k)

    return indices


# ── Detección de carátula ─────────────────────────────────────────────────────

def detectar_caratula(bloque, headers_pagina, dictamen_inicio, apertura_rel):
    """
    Heurística para identificar la línea de carátula DENTRO del bloque.

    Casos cubiertos:
      - Sivaslian: "Sivaslian, Rosa s/ sucesión" (mayúsculas+minúsculas).
      - Cerboni: "ALEJANDRO CERBONI" (todo mayúsculas, formato viejo).
      - Universidad: "ESTADO NACIONAL – MINISTERIO de CULTURA y EDUCACION
        c/ UNIVERSIDAD de GENERAL SARMIENTO".

    Estrategia: la carátula es la primera línea no-trivial DESPUÉS de la
    metadata editorial inicial (recurrente, tribunal de origen del fallo
    previo) y ANTES de los sumarios / dictamen / apertura.

    Anclaje robusto: usar dictamen_inicio o apertura_rel como tope superior
    (ambos son detectables sin ambigüedad). La carátula está en la zona
    [0, tope). En esa zona, la carátula es la línea que aparece JUSTO
    DESPUÉS de la última línea de metadata editorial del fallo previo.

    Heurística pragmática:
      - Si hay sumarios reales detectables vía formato B (`MAYUS:` + texto),
        la carátula está justo antes del primer header con `:`.
      - Si todos los headers son formato A (sin `:`), la carátula puede
        ser indistinguible de un header. Fallback: la primera línea
        no-vacía no-header-pagina cuya siguiente línea no-vacía sea
        un header de sumario (línea seguida de sumario → carátula).

    Devuelve índice relativo, o None si no se puede determinar.
    """
    if dictamen_inicio is not None:
        tope = dictamen_inicio
    elif apertura_rel is not None:
        tope = apertura_rel
    else:
        tope = len(bloque)

    # Estrategia 1: buscar primer header con ":" (formato B). Si lo
    # encuentro, la carátula es la línea anterior no-vacía no-header-pagina.
    primer_hdr_conColon = None
    for k in range(tope):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        if ":" in s and es_header_sumario_auditoria(s):
            primer_hdr_conColon = k
            break

    if primer_hdr_conColon is not None:
        for k in range(primer_hdr_conColon - 1, -1, -1):
            if k in headers_pagina:
                continue
            s = bloque[k].strip()
            if not s:
                continue
            # ── Fix B049 Var-A: detectar carátula partida ──────────────
            if 'c/' not in s and 's/' not in s and ' | ' not in s and not s.endswith('.'):
                for k2 in range(k - 1, -1, -1):
                    if k2 in headers_pagina:
                        continue
                    s2 = bloque[k2].strip()
                    if not s2:
                        continue
                    # Guardia: s2 debe parecer primera mitad de carátula
                    if s2.upper() in {'ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'}:
                        break
                    if s2.startswith('V. ') or s2.startswith('v. '):
                        break
                    if s2.endswith('.') or (s2 and s2[0].islower()):
                        break
                    # Concatenar con manejo de silabación
                    if s2.endswith('­') or s2.endswith('-'):
                        bloque[k] = s2.rstrip('­-') + s + '\n'
                    else:
                        bloque[k] = s2 + ' ' + s + '\n'
                    break
            # ── Fin fix B049 ───────────────────────────────────────────
            return k
        return None

    # Estrategia 2: no hay headers con ":". Usar el patrón "línea seguida
    # de header de sumario sin :". Buscar pares (X, Y) consecutivos donde
    # Y es header de sumario y X no lo es. La X es candidata a carátula.
    prev_no_header = None
    for k in range(tope):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        if es_header_sumario_auditoria(s):
            # Si hay una línea anterior no-header registrada, es candidata
            if prev_no_header is not None:
                # ── Fix B049 Var-A: detectar carátula partida ──────────────
                s_cand = bloque[prev_no_header].strip()
                if 'c/' not in s_cand and 's/' not in s_cand and ' | ' not in s_cand and not s_cand.endswith('.'):
                    for k2 in range(prev_no_header - 1, -1, -1):
                        if k2 in headers_pagina:
                            continue
                        s2 = bloque[k2].strip()
                        if not s2:
                            continue
                        # Guardia: s2 debe parecer primera mitad de carátula
                        if s2.upper() in {'ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'}:
                            break
                        if s2.startswith('V. ') or s2.startswith('v. '):
                            break
                        if s2.endswith('.') or (s2 and s2[0].islower()):
                            break
                        # Concatenar con manejo de silabación
                        if s2.endswith('­') or s2.endswith('-'):
                            bloque[prev_no_header] = s2.rstrip('­-') + s_cand + '\n'
                        else:
                            bloque[prev_no_header] = s2 + ' ' + s_cand + '\n'
                        break
                # ── Fin fix B049 ───────────────────────────────────────────
                return prev_no_header
            # Si no hay anterior, este header podría ser la propia
            # carátula (caso límite: bloque empieza con carátula+sumarios
            # sin metadata editorial previa). No probable; devolver None.
            return None
        else:
            prev_no_header = k

    # Sin sumarios detectados: carátula es la última línea no-trivial
    # antes del tope.
    for k in range(tope - 1, -1, -1):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        return k

    return None


# ── Detección de sumarios editoriales ─────────────────────────────────────────

# Atribución típica al final del sumario: "-Del dictamen...-" o "(Voto de...)".
# La detectamos para poder exponerla en el span, pero no la usamos como
# requisito de cierre del sumario.
RE_ATRIBUCION_GUION = re.compile(
    r"^\s*[\-–]\s*(Del\s+dictamen|Del\s+precedente|Del\s+voto)\b.+?[\-–\.]\s*$",
    re.I,
)
RE_ATRIBUCION_PARENTESIS = re.compile(
    r"^\s*\(\s*(Voto|Disidencia)\b.+?\)\s*\.?\s*$",
    re.I,
)


def es_header_sumario_auditoria(linea):
    """
    Detector de header de sumario PROPIO de la auditoría, más permisivo
    que linea_es_header_sumario() del parser.

    Cubre dos formatos empíricos del corpus:

      Formato A (Sivaslian, tomo 349): header en MAYÚSCULAS sola,
        sin puntuación final.
        Ej: "RECURSOS LOCALES"
            "BENEFICIO DE LITIGAR SIN GASTOS"

      Formato B (Cerboni, tomo 331): título en MAYÚSCULAS + ":" +
        subtítulo en oración normal terminado en ".".
        Ej: "EXTRADICION: Extradición con países extranjeros. Trámite."
            "RECURSO EXTRAORDINARIO: Resolución. Límites del pronunciamiento."

    Reglas:
      - Línea no vacía, length entre 5 y 200 chars.
      - Primera palabra ≥ 5 letras todas en MAYÚSCULAS.
      - Si tiene ":", el prefijo antes del ":" debe ser todo mayúsculas
        (con tolerancia a espacios y dígitos romanos).
      - Si NO tiene ":", la línea entera debe ser mayoritariamente
        mayúsculas (más mayúsculas que minúsculas).

    Diferencia clave con el parser: NO requiere `.` ni `:` al final.
    """
    s = linea.strip()
    if not s:
        return False
    if len(s) < 5 or len(s) > 200:
        return False

    # Primera palabra ≥ 5 letras y toda en mayúsculas
    pp = re.match(r"^[A-ZÁÉÍÓÚÑ]+", s)
    if not pp or len(pp.group(0)) < 5:
        return False

    # Caso B: tiene ":" → el prefijo (parte antes del primer ":") es el
    # título en mayúsculas. Aceptamos si el prefijo es todo mayúsculas
    # (con espacios y dígitos romanos toleráreos) y tiene ≥ 5 letras.
    if ":" in s:
        prefijo = s.split(":", 1)[0].strip()
        # Prefijo debe ser todo mayúsculas + espacios (sin minúsculas)
        if any(c.islower() for c in prefijo):
            return False
        # Y tener al menos 5 letras alfabéticas
        n_letras_pref = sum(1 for c in prefijo if c.isalpha())
        if n_letras_pref < 5:
            return False
        return True

    # Caso A: sin ":" → la línea entera debe ser mayoritariamente
    # MAYÚSCULAS. Tolera hasta cierto número de minúsculas (conectores
    # cortos como "de", "en", "y") pero requiere mayoría mayúsculas.
    n_mayus = sum(1 for c in s if c.isupper())
    n_minus = sum(1 for c in s if c.islower())
    if n_mayus < n_minus:
        return False

    return True


def detectar_sumarios(bloque, headers_pagina, caratula_rel, fin_busqueda):
    """
    Detecta spans de sumarios editoriales entre carátula y fin_busqueda
    (típicamente apertura_rel o inicio del dictamen).

    Cada sumario empieza con un header en MAYÚSCULAS (linea_es_header_sumario
    del parser) y termina cuando empieza el siguiente sumario, o cuando
    aparece un dictamen, o cuando aparece el marcador de apertura, o cuando
    se alcanza fin_busqueda.

    Devuelve lista de dicts:
      {linea_ini, linea_fin, header, atribucion (o None), indice}
    """
    sumarios = []
    if caratula_rel is None:
        inicio = 0
    else:
        inicio = caratula_rel + 1

    fin = min(fin_busqueda, len(bloque))

    # 1. Encontrar todos los inicios de sumario
    inicios = []
    for k in range(inicio, fin):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        if es_header_sumario_auditoria(s):
            inicios.append(k)

    if not inicios:
        return sumarios

    # 2. Cada sumario va de inicios[i] a inicios[i+1]-1, o hasta fin.
    for idx, k_ini in enumerate(inicios):
        if idx + 1 < len(inicios):
            k_fin = inicios[idx + 1] - 1
        else:
            k_fin = fin - 1

        # Recortar trailing: si hay líneas vacías al final, omitirlas
        while k_fin > k_ini and not bloque[k_fin].strip():
            k_fin -= 1

        # Detectar atribución en las últimas 2 líneas no-vacías
        atribucion = None
        for kk in range(k_fin, max(k_ini, k_fin - 3) - 1, -1):
            if kk in headers_pagina:
                continue
            s = bloque[kk].strip()
            if not s:
                continue
            if RE_ATRIBUCION_GUION.match(s) or RE_ATRIBUCION_PARENTESIS.match(s):
                atribucion = s
                break

        sumarios.append({
            "linea_ini": k_ini,
            "linea_fin": k_fin,
            "header": bloque[k_ini].strip(),
            "atribucion": atribucion,
            "indice": idx + 1,
        })

    return sumarios


# ── Detección de dictamen ─────────────────────────────────────────────────────

def detectar_dictamen(bloque, headers_pagina):
    """
    Detecta el span del dictamen. Replica la lógica del parser pero devuelve
    rango de líneas en vez de set de índices.

    El dictamen empieza en RE_DICT_HDR ("Dictamen de la Procuración...") y
    termina cuando aparece una fecha "Buenos Aires" en una línea precedida
    de una línea corta (heurística del parser, líneas 1518-1529).

    AJUSTE DE AUDITORÍA: si el "fin" cae sobre la línea del FALLO DE LA
    CORTE SUPREMA (porque la heurística del parser confunde la fecha del
    fallo con el cierre del dictamen), retrocedo dos líneas para no
    pisar el cuerpo de la mayoría. Esto NO altera la heurística del
    parser; solo mejora el rendering de la auditoría. El fenómeno
    queda registrado en el span del dictamen igual: si linea_fin del
    dictamen es justo antes del FALLO, es señal de que el dictamen
    no termina con "Buenos Aires, fecha" en su última línea (formato
    no estándar) y el parser podría estar cortando mal.

    Devuelve (linea_ini, linea_fin) o None.
    """
    inicio = None
    for k, ln in enumerate(bloque):
        s = ln.strip()
        if RE_DICT_HDR.match(s):
            inicio = k
            break

    if inicio is None:
        return None

    fin = len(bloque) - 1
    for k in range(inicio + 1, len(bloque)):
        s = bloque[k].strip()
        if RE_FECHA_LINEA.match(s) and k > inicio + 5:
            prev = bloque[k - 1].strip() if k > 0 else ""
            if prev and len(prev) < 80:
                # Si la línea previa es el marcador de apertura del FALLO,
                # retroceder: el dictamen termina antes
                if RE_APERTURA.match(prev):
                    fin = k - 2  # línea antes del FALLO DE LA CORTE
                else:
                    fin = k
                break

    return (inicio, fin)


# ── Detección de votos y disidencias ──────────────────────────────────────────

def detectar_votos_y_disidencias(bloque, headers_pagina):
    """
    Detecta spans de votos separados y disidencias.

    Cada span empieza en una línea que matchee RE_VOTO_HDR o RE_DISID_HDR y
    termina al inicio del siguiente voto/disidencia, o al final del bloque.

    Devuelve lista ordenada de dicts con linea_ini, linea_fin, tipo
    ("voto" o "disidencia"), es_parcial, header.
    """
    inicios = []
    for k, ln in enumerate(bloque):
        if k in headers_pagina:
            continue
        s = ln.strip()
        m_voto = RE_VOTO_HDR.match(s)
        m_disid = RE_DISID_HDR.match(s)
        if m_voto or m_disid:
            tipo = TIPO_VOTO if m_voto else TIPO_DISIDENCIA
            es_parcial = bool(m_disid and "parcial" in s.lower())
            inicios.append((k, tipo, es_parcial, s))

    if not inicios:
        return []

    spans = []
    for i, (k_ini, tipo, es_parcial, header) in enumerate(inicios):
        if i + 1 < len(inicios):
            k_fin = inicios[i + 1][0] - 1
        else:
            k_fin = len(bloque) - 1
        spans.append({
            "linea_ini": k_ini,
            "linea_fin": k_fin,
            "tipo": tipo,
            "es_parcial": es_parcial,
            "header": header,
        })

    return spans


# ── Detección de firma de la mayoría ──────────────────────────────────────────

def detectar_firma_mayoria(bloque, headers_pagina, por_ello_idx, votos_inicio):
    """
    Detecta el span de la firma de la mayoría.

    La firma típicamente está después del "Por ello" de la mayoría y antes
    del primer voto separado (si lo hay) o antes de los metadatos
    editoriales finales.

    Heurística:
      - Buscar desde por_ello_idx hacia adelante.
      - Una línea es candidata a firma si linea_es_firma_de_juez(linea).
      - El span agrupa líneas consecutivas (con tolerancia a 1 vacía
        intercalada) que sean firma o continuación.
      - Termina al inicio del primer voto separado, o al primer header
        de página, o cuando se rompe la secuencia.

    Devuelve (linea_ini, linea_fin) o None.
    """
    if por_ello_idx is None:
        return None

    limite = votos_inicio if votos_inicio is not None else len(bloque)

    # Buscar primera línea que sea firma de juez
    inicio_firma = None
    for k in range(por_ello_idx, limite):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        if linea_es_firma_de_juez(s):
            inicio_firma = k
            break

    if inicio_firma is None:
        return None

    # Extender hacia adelante mientras siga siendo firma o línea de continuación
    fin_firma = inicio_firma
    huecos_consecutivos = 0
    for k in range(inicio_firma + 1, limite):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            huecos_consecutivos += 1
            if huecos_consecutivos >= 2:
                break
            continue
        huecos_consecutivos = 0
        if linea_es_firma_de_juez(s):
            fin_firma = k
            continue
        # Línea de continuación: si es corta y contiene apellido conocido
        if len(s) <= 100 and any(p.search(s) for p, _ in JUECES_CONOCIDOS):
            fin_firma = k
            continue
        break

    return (inicio_firma, fin_firma)


# ── Detección de "Por ello" (límite mayoría/firma) ───────────────────────────

def detectar_por_ello_mayoria(bloque, headers_pagina, dictamen_span, apertura_mayoria, votos_inicio):
    """
    Encuentra el índice del "Por ello" (o variante de dispositivo) de la
    MAYORÍA, no de un voto separado. Empieza la búsqueda DESDE apertura_mayoria
    para evitar matchear "Por ello" de fallos arrastrados al inicio del bloque
    (residuo del fallo previo) o del dictamen embebido.
    """
    if apertura_mayoria is not None:
        inicio_busqueda = apertura_mayoria
    elif dictamen_span is not None:
        inicio_busqueda = dictamen_span[1] + 1
    else:
        inicio_busqueda = 0

    fin_busqueda = votos_inicio if votos_inicio is not None else len(bloque)

    for k in range(inicio_busqueda, fin_busqueda):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        es_disp, _tipo = detectar_apertura_dispositivo(s)
        if es_disp:
            return k

    return None


# ── Detección de FALLO/SENTENCIA DE LA CORTE (apertura del cuerpo mayoría) ───

def detectar_apertura_mayoria(bloque, headers_pagina, dictamen_span):
    """
    Encuentra el índice del marcador "FALLO DE LA CORTE SUPREMA" o
    "SENTENCIA DE LA CORTE SUPREMA" que abre el cuerpo de la mayoría,
    saltando el dictamen si lo hay.
    """
    inicio_busqueda = 0
    if dictamen_span is not None:
        inicio_busqueda = dictamen_span[1] + 1

    for k in range(inicio_busqueda, len(bloque)):
        if k in headers_pagina:
            continue
        s = bloque[k].strip()
        if RE_APERTURA.match(s):
            return k
    return None


# ── Detección de sumario_con_link ─────────────────────────────────────────────

def detectar_sumario_con_link(bloque, headers_pagina):
    """
    Detecta si el bloque ES un sumario_con_link. Si lo es, devuelve span
    (linea_ini, linea_fin) que cubre TODO el bloque. Si no, devuelve None.

    Por construcción, sumario_con_link es un bloque entero, no una sección.
    """
    for k, ln in enumerate(bloque):
        if RE_SUMARIO_LINK.match(ln.strip()):
            return (0, len(bloque) - 1)
    return None


# ── Función principal: segmentar_bloque ───────────────────────────────────────

def segmentar_bloque(bloque, headers_archivo_relevantes, linea_inicio_abs):
    """
    Segmenta el bloque en spans tipados. Devuelve lista ordenada de dicts.

    Cada span tiene como mínimo: tipo, linea_ini_rel, linea_fin_rel, texto.
    Algunos tipos llevan campos extra (sumario.atribucion, voto.es_parcial, etc).

    INVARIANTES:
      - Spans semánticos (TIPOS_SEMANTICOS) son disjuntos entre sí.
      - header_pagina es transversal: puede caer adentro de cualquier span
        semántico. Se emite como span propio, no se excluye de los demás.
      - Cobertura: toda línea del bloque pertenece a ≥1 span (catch_all si
        nada más matchea).

    Los índices son RELATIVOS al bloque (0 = primera línea del bloque).
    """
    n = len(bloque)
    spans = []

    # PASO 0: detectar headers de página (transversal)
    headers_pagina = detectar_headers_pagina(
        bloque, headers_archivo_relevantes, linea_inicio_abs
    )

    # PASO 1: ¿es sumario_con_link? Si sí, todo el bloque es ese span.
    scl = detectar_sumario_con_link(bloque, headers_pagina)
    if scl is not None:
        spans.append({
            "tipo": TIPO_SUMARIO_CON_LINK,
            "linea_ini": scl[0],
            "linea_fin": scl[1],
            "texto": "\n".join(bloque[scl[0]:scl[1] + 1]),
        })
        # Headers de página siguen siendo transversales
        for k in sorted(headers_pagina):
            spans.append({
                "tipo": TIPO_HEADER_PAGINA,
                "linea_ini": k,
                "linea_fin": k,
                "texto": bloque[k],
            })
        return _ordenar_y_validar(spans, n)

    # PASO 2: detectar dictamen (si lo hay)
    dictamen_span = detectar_dictamen(bloque, headers_pagina)

    # PASO 3: detectar apertura mayoría (FALLO DE LA CORTE...)
    apertura_mayoria = detectar_apertura_mayoria(bloque, headers_pagina, dictamen_span)

    # PASO 4: detectar votos y disidencias
    votos_disid = detectar_votos_y_disidencias(bloque, headers_pagina)
    votos_inicio = votos_disid[0]["linea_ini"] if votos_disid else None

    # PASO 5: detectar "Por ello" de la mayoría
    por_ello_idx = detectar_por_ello_mayoria(
        bloque, headers_pagina, dictamen_span, apertura_mayoria, votos_inicio
    )

    # PASO 6: detectar firma de la mayoría
    firma_span = detectar_firma_mayoria(
        bloque, headers_pagina, por_ello_idx, votos_inicio
    )

    # PASO 7: detectar carátula
    dictamen_inicio = dictamen_span[0] if dictamen_span is not None else None
    caratula_rel = detectar_caratula(bloque, headers_pagina, dictamen_inicio, apertura_mayoria)

    # PASO 8: detectar sumarios editoriales
    fin_sumarios = (
        dictamen_span[0] if dictamen_span is not None
        else (apertura_mayoria if apertura_mayoria is not None else n)
    )
    sumarios = detectar_sumarios(
        bloque, headers_pagina, caratula_rel, fin_sumarios
    )

    # ── Emitir spans ─────────────────────────────────────────────────────────

    # Carátula
    if caratula_rel is not None:
        spans.append({
            "tipo": TIPO_CARATULA,
            "linea_ini": caratula_rel,
            "linea_fin": caratula_rel,
            "texto": bloque[caratula_rel],
        })

    # Sumarios (uno por sumario)
    for sm in sumarios:
        spans.append({
            "tipo": TIPO_SUMARIO,
            "linea_ini": sm["linea_ini"],
            "linea_fin": sm["linea_fin"],
            "texto": "\n".join(bloque[sm["linea_ini"]:sm["linea_fin"] + 1]),
            "indice": sm["indice"],
            "header": sm["header"],
            "atribucion": sm["atribucion"],
        })

    # Dictamen
    if dictamen_span is not None:
        spans.append({
            "tipo": TIPO_DICTAMEN,
            "linea_ini": dictamen_span[0],
            "linea_fin": dictamen_span[1],
            "texto": "\n".join(bloque[dictamen_span[0]:dictamen_span[1] + 1]),
        })

    # Cuerpo mayoría: desde apertura_mayoria (o desde fin del dictamen) hasta
    # justo antes de la firma_mayoria, o hasta votos_inicio si no hay firma.
    if apertura_mayoria is not None:
        cuerpo_ini = apertura_mayoria
        if firma_span is not None:
            cuerpo_fin = firma_span[0] - 1
        elif votos_inicio is not None:
            cuerpo_fin = votos_inicio - 1
        else:
            cuerpo_fin = n - 1
        # Recortar headers_pagina del fin si hay
        while cuerpo_fin > cuerpo_ini and cuerpo_fin in headers_pagina:
            cuerpo_fin -= 1
        if cuerpo_fin >= cuerpo_ini:
            spans.append({
                "tipo": TIPO_CUERPO_MAYORIA,
                "linea_ini": cuerpo_ini,
                "linea_fin": cuerpo_fin,
                "texto": "\n".join(bloque[cuerpo_ini:cuerpo_fin + 1]),
            })

    # Firma mayoría
    if firma_span is not None:
        spans.append({
            "tipo": TIPO_FIRMA,
            "linea_ini": firma_span[0],
            "linea_fin": firma_span[1],
            "texto": "\n".join(bloque[firma_span[0]:firma_span[1] + 1]),
        })

    # Votos y disidencias
    for vd in votos_disid:
        spans.append({
            "tipo": vd["tipo"],
            "linea_ini": vd["linea_ini"],
            "linea_fin": vd["linea_fin"],
            "texto": "\n".join(bloque[vd["linea_ini"]:vd["linea_fin"] + 1]),
            "es_parcial": vd["es_parcial"],
            "header": vd["header"],
        })

    # Headers de página (transversales)
    for k in sorted(headers_pagina):
        spans.append({
            "tipo": TIPO_HEADER_PAGINA,
            "linea_ini": k,
            "linea_fin": k,
            "texto": bloque[k],
        })

    # PASO 9: catch-all
    # Calcular cobertura semántica (sin contar header_pagina) y emitir
    # spans catch_all sobre los huecos.
    spans = _agregar_catch_all(spans, n)

    return _ordenar_y_validar(spans, n)


def _agregar_catch_all(spans, n):
    """
    Calcula líneas no cubiertas por spans semánticos y emite catch_all
    para cada hueco contiguo. Headers de página NO se cuentan como
    cobertura (son transversales).
    """
    cubierto = [False] * n
    for sp in spans:
        if sp["tipo"] in TIPOS_SEMANTICOS:
            for k in range(sp["linea_ini"], sp["linea_fin"] + 1):
                if 0 <= k < n:
                    cubierto[k] = True
        elif sp["tipo"] == TIPO_HEADER_PAGINA:
            # Los headers de página también cuentan como cobertura
            # (porque son rotulados, no residuo)
            for k in range(sp["linea_ini"], sp["linea_fin"] + 1):
                if 0 <= k < n:
                    cubierto[k] = True

    # Detectar huecos contiguos
    catch_alls = []
    k = 0
    while k < n:
        if not cubierto[k]:
            ini = k
            while k < n and not cubierto[k]:
                k += 1
            fin = k - 1
            catch_alls.append((ini, fin))
        else:
            k += 1

    return spans + [
        {
            "tipo": TIPO_CATCH_ALL,
            "linea_ini": ini,
            "linea_fin": fin,
            "texto": None,  # llenar al final
        }
        for ini, fin in catch_alls
    ]


def _ordenar_y_validar(spans, n):
    """
    Ordena por linea_ini y valida invariantes.
    """
    # Llenar texto en catch_alls (no lo teníamos al armarlos)
    # (esto se hace afuera de esta función, en auditar_fallo)
    spans.sort(key=lambda s: (s["linea_ini"], 0 if s["tipo"] != TIPO_HEADER_PAGINA else 1))
    return spans


# ── API canónica: auditar_fallo(tomo, pagina) -> dict ─────────────────────────

def _resolver_caso(tomo, pagina, filas_loc):
    """
    Resuelve (tomo, pagina) a la fila del catálogo correspondiente.

    Reglas (Decisión D):
      1. Match exacto: pagina_inicio <= P <= pagina_fin.
      2. Si pagina_fin vacío: tope = pagina_inicio del siguiente caso del
         mismo tomo menos 1. Si es el último, tope = pagina_inicio + 50
         (heurística defensiva: los casos no abarcan más de 50 páginas
         razonablemente; evita que cualquier P > pagina_inicio matchee al
         último caso del tomo).
      3. Sin match: devuelve None y lista de cercanos.
    """
    # Filtrar filas del tomo
    filas_tomo = [r for r in filas_loc if int(r["tomo"]) == int(tomo)]
    filas_tomo.sort(key=lambda r: int(r["pagina_inicio"]))

    for i, r in enumerate(filas_tomo):
        p_ini = int(r["pagina_inicio"])
        p_fin_raw = r.get("pagina_fin", "")
        if p_fin_raw and p_fin_raw.strip():
            p_fin = int(p_fin_raw)
        else:
            # Tope = pagina_inicio del siguiente caso menos 1
            if i + 1 < len(filas_tomo):
                p_fin = int(filas_tomo[i + 1]["pagina_inicio"]) - 1
            else:
                # Último del tomo: tope defensivo de 50 páginas
                p_fin = p_ini + 50

        if p_ini <= int(pagina) <= p_fin:
            return r, None

    # Sin match: devolver los 3 más cercanos del tomo
    cercanos = sorted(
        filas_tomo,
        key=lambda r: abs(int(r["pagina_inicio"]) - int(pagina))
    )[:3]
    return None, cercanos


def auditar_fallo(tomo, pagina, *,
                  corpus_dir=None, localizados_path=None, mapa_path=None,
                  _cache=None):
    """
    Audita un fallo. Devuelve dict con metadata + spans.

    _cache es uso interno para lotes (evita recargar CSVs en cada llamada).
    """
    corpus_dir = Path(corpus_dir) if corpus_dir else DEFAULT_CORPUS
    localizados_path = Path(localizados_path) if localizados_path else DEFAULT_LOCALIZADOS
    mapa_path = Path(mapa_path) if mapa_path else DEFAULT_MAPA

    # Cache de CSVs
    if _cache is None:
        _cache = {}
    if "filas_loc" not in _cache:
        _cache["filas_loc"], _ = cargar_localizados(str(localizados_path))
    if "headers_por_archivo" not in _cache:
        _cache["headers_por_archivo"] = cargar_proximos_headers(str(mapa_path))

    filas_loc = _cache["filas_loc"]
    headers_por_archivo = _cache["headers_por_archivo"]

    # Resolver el caso
    fila, cercanos = _resolver_caso(tomo, pagina, filas_loc)
    if fila is None:
        return {
            "error": "sin_match",
            "tomo": tomo,
            "pagina": pagina,
            "cercanos": [
                {
                    "caso_id_canonico": r["caso_id_canonico"],
                    "pagina_inicio": int(r["pagina_inicio"]),
                    "pagina_fin": int(r["pagina_fin"]) if r.get("pagina_fin", "").strip() else None,
                    "nombres_indice": r.get("nombres_indice", ""),
                }
                for r in cercanos
            ],
        }

    # Cargar el archivo .md
    archivo_path = corpus_dir / fila["archivo"]
    if not archivo_path.exists():
        return {
            "error": "archivo_no_encontrado",
            "ruta": str(archivo_path),
            "fila": dict(fila),
        }

    text = archivo_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    linea_inicio = int(fila["linea_inicio"])
    linea_fin_catalogo_raw = fila.get("linea_fin", "")
    if linea_fin_catalogo_raw and linea_fin_catalogo_raw.strip():
        linea_fin_catalogo = int(linea_fin_catalogo_raw)
    else:
        linea_fin_catalogo = len(lines) - 1

    # Calcular siguiente_caso para detectar_fin_real
    cat_por_tomo = {}
    for row in filas_loc:
        cat_por_tomo.setdefault(int(row["tomo"]), []).append({
            "caso_id_canonico": row["caso_id_canonico"],
            "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
            "nombres_indice": row.get("nombres_indice", ""),
        })
    for t in cat_por_tomo:
        cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])

    primer_token_siguiente = ""
    tomo_int = int(fila["tomo"])
    for i, c in enumerate(cat_por_tomo.get(tomo_int, [])):
        if c["caso_id_canonico"] == fila["caso_id_canonico"]:
            if i + 1 < len(cat_por_tomo[tomo_int]):
                siguiente = cat_por_tomo[tomo_int][i + 1]
                primer_token_siguiente = primer_token_de_caratula(siguiente["nombres_indice"])
            break

    # ── Calcular linea_inicio del próximo caso DEL MISMO ARCHIVO (no solo
    # del mismo tomo). Necesario para detectar_borde_inferior — filtrar por
    # tomo solo no alcanza porque un tomo puede dividirse en varios .md
    # (ej. LibroVol339.1.md, LibroVol339.2.md), y el "siguiente caso" del
    # último caso de un .md sería el primero del .md siguiente, generando
    # delta nonsense de líneas entre archivos distintos.
    archivo_actual = fila["archivo"]
    filas_mismo_archivo = [
        r for r in filas_loc
        if r["archivo"] == archivo_actual and r.get("linea_inicio", "").strip()
    ]
    filas_mismo_archivo.sort(key=lambda r: int(r["linea_inicio"]))
    linea_inicio_proximo_caso = None
    for i, r in enumerate(filas_mismo_archivo):
        if r["caso_id_canonico"] == fila["caso_id_canonico"]:
            if i + 1 < len(filas_mismo_archivo):
                linea_inicio_proximo_caso = int(filas_mismo_archivo[i + 1]["linea_inicio"])
            break

    # Headers del archivo (mismo tomo)
    headers_archivo = headers_por_archivo.get((tomo_int, fila["archivo"]), [])
    headers_archivo = sorted(headers_archivo)

    # Detectar fin real (igual que parser.py)
    prox_header = proximo_header_despues_de(headers_archivo, linea_fin_catalogo)
    linea_fin_real, status_fin, pista_fin = detectar_fin_real(
        lines, linea_inicio, linea_fin_catalogo, prox_header, primer_token_siguiente
    )

    # Construir bloque
    bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin_real)

    # Headers de página relevantes para este bloque
    headers_relevantes = [
        (ln, pg) for (ln, pg) in headers_archivo
        if linea_inicio <= ln <= linea_fin_real
    ]

    # Segmentar
    spans = segmentar_bloque(bloque, headers_relevantes, linea_inicio)

    # Llenar texto en catch_alls
    for sp in spans:
        if sp["tipo"] == TIPO_CATCH_ALL and sp.get("texto") is None:
            sp["texto"] = "\n".join(bloque[sp["linea_ini"]:sp["linea_fin"] + 1])

    # Calcular invariantes
    n = len(bloque)
    cobertura = [False] * n
    for sp in spans:
        for k in range(sp["linea_ini"], sp["linea_fin"] + 1):
            if 0 <= k < n:
                cobertura[k] = True
    invariante_cobertura = all(cobertura)

    # Disjunción: spans semánticos no se solapan entre sí
    invariante_disjuncion = True
    semanticos = [sp for sp in spans if sp["tipo"] in TIPOS_SEMANTICOS]
    for i, a in enumerate(semanticos):
        for b in semanticos[i + 1:]:
            if not (a["linea_fin"] < b["linea_ini"] or b["linea_fin"] < a["linea_ini"]):
                invariante_disjuncion = False
                break

    # Líneas en catch_all
    lineas_residuo = sum(
        sp["linea_fin"] - sp["linea_ini"] + 1
        for sp in spans if sp["tipo"] == TIPO_CATCH_ALL
    )

    # ── Auditar borde inferior (transición fin_real → próximo caso) ─────────
    # Esto NO afecta la segmentación ni los spans del bloque del fallo X;
    # es un diagnóstico transversal que mira "del otro lado" del corte.
    borde_inferior = detectar_borde_inferior(
        lines, linea_fin_real, linea_inicio_proximo_caso, primer_token_siguiente
    )

    return {
        "caso_id_canonico": fila["caso_id_canonico"],
        "tomo": tomo_int,
        "pagina_consultada": int(pagina),
        "pagina_inicio": int(fila["pagina_inicio"]),
        "pagina_fin": int(fila["pagina_fin"]) if fila.get("pagina_fin", "").strip() else None,
        "archivo": fila["archivo"],
        "linea_inicio": linea_inicio,
        "linea_fin_catalogo": linea_fin_catalogo,
        "linea_fin_real": linea_fin_real,
        "status_localizacion": fila.get("status", ""),
        "status_fin": status_fin,
        "pista_fin": pista_fin,
        "nombres_indice": fila.get("nombres_indice", ""),
        "spans": spans,
        "n_lineas_bloque": n,
        "lineas_residuo": lineas_residuo,
        "porcentaje_residuo": round(100 * lineas_residuo / n, 2) if n > 0 else 0.0,
        "invariante_cobertura": invariante_cobertura,
        "invariante_disjuncion": invariante_disjuncion,
        "borde_inferior": borde_inferior,
    }


# ── Renderer Markdown ─────────────────────────────────────────────────────────

def _render_caso(resultado, abs_offset_lines=True):
    """
    Renderiza un resultado de auditar_fallo a Markdown.
    Si abs_offset_lines, los rangos se imprimen como líneas absolutas
    del archivo (linea_inicio + linea_ini_rel).
    """
    if "error" in resultado:
        if resultado["error"] == "sin_match":
            out = [f"## ERROR: sin caso para tomo {resultado['tomo']} página {resultado['pagina']}"]
            out.append("\nCasos cercanos en el catálogo:")
            for c in resultado["cercanos"]:
                out.append(f"- `{c['caso_id_canonico']}` (pp. {c['pagina_inicio']}–{c['pagina_fin'] or '?'}): {c['nombres_indice'][:80]}")
            return "\n".join(out)
        elif resultado["error"] == "archivo_no_encontrado":
            return f"## ERROR: archivo no encontrado: `{resultado['ruta']}`"
        else:
            return f"## ERROR: {resultado['error']}"

    r = resultado
    offset = r["linea_inicio"] if abs_offset_lines else 0

    out = []
    titulo = f"## {r['caso_id_canonico']} — {r['nombres_indice'][:120]}"
    out.append(titulo)
    out.append("")
    out.append("**Localización**")
    out.append(f"- Archivo: `{r['archivo']}`")
    pf_str = str(r["pagina_fin"]) if r["pagina_fin"] else "(vacío)"
    out.append(f"- Páginas catálogo: {r['pagina_inicio']}–{pf_str} | Página consultada: {r['pagina_consultada']}")
    out.append(f"- Líneas catálogo: {r['linea_inicio']}–{r['linea_fin_catalogo']} | Línea fin real: {r['linea_fin_real']} (status_fin=`{r['status_fin']}`, pista=`{r['pista_fin']}`)")
    out.append(f"- Status localización: `{r['status_localizacion']}`")
    out.append("")

    # Tabla resumen
    out.append("**Resumen de spans**")
    out.append("")
    out.append("| # | Tipo | Líneas (abs) | Líneas |")
    out.append("|---|------|--------------|-------:|")
    for i, sp in enumerate(r["spans"], 1):
        ln_ini = sp["linea_ini"] + offset
        ln_fin = sp["linea_fin"] + offset
        n_lineas = sp["linea_fin"] - sp["linea_ini"] + 1
        tipo_label = sp["tipo"]
        if sp["tipo"] == TIPO_SUMARIO and "indice" in sp:
            tipo_label = f"sumario [{sp['indice']}]"
        if sp["tipo"] in (TIPO_VOTO, TIPO_DISIDENCIA) and sp.get("es_parcial"):
            tipo_label = sp["tipo"] + " (parcial)"
        out.append(f"| {i} | {tipo_label} | {ln_ini}–{ln_fin} | {n_lineas} |")
    out.append("")

    # Invariantes
    cob_str = "OK" if r["invariante_cobertura"] else "FALLA"
    dis_str = "OK" if r["invariante_disjuncion"] else "FALLA"
    out.append(
        f"**Invariantes**: cobertura={cob_str}, disjunción={dis_str}, "
        f"líneas_residuo={r['lineas_residuo']} "
        f"({r['porcentaje_residuo']}% del bloque, n={r['n_lineas_bloque']})"
    )
    out.append("")
    out.append("---")
    out.append("")

    # Spans en detalle
    for i, sp in enumerate(r["spans"], 1):
        ln_ini = sp["linea_ini"] + offset
        ln_fin = sp["linea_fin"] + offset
        tipo_label = sp["tipo"]
        if sp["tipo"] == TIPO_SUMARIO and "indice" in sp:
            tipo_label = f"sumario [{sp['indice']}]"
        out.append(f"### [span {i}] {tipo_label} ({ln_ini}–{ln_fin})")

        # Metadata extra
        if sp["tipo"] == TIPO_SUMARIO:
            out.append(f"**Header**: {sp.get('header', '')}")
            atrib = sp.get("atribucion") or "(sin atribución detectada)"
            out.append(f"**Atribución**: {atrib}")
        elif sp["tipo"] in (TIPO_VOTO, TIPO_DISIDENCIA):
            out.append(f"**Header**: {sp.get('header', '')}")
            if sp.get("es_parcial"):
                out.append(f"**Parcial**: sí")

        out.append("```")
        out.append(sp.get("texto", "") or "")
        out.append("```")
        out.append("")

    # ── Sección Borde inferior (render condicional) ────────────────────────
    # Solo se imprime si hay algo digno de mirar: residuo, solapado, gap
    # grande de solo headers, o cualquier alerta. En estados continuo /
    # header_normal / fin_archivo se omite para no inundar el reporte.
    bi = r.get("borde_inferior")
    if bi is not None:
        ESTADOS_VISIBLES = {EST_GAP_RESIDUO, EST_SOLAPADO, EST_GAP_SOLO_HEADERS}
        if bi["estado"] in ESTADOS_VISIBLES or bi["alertas"]:
            out.append("### Borde inferior (transición al próximo caso)")
            lipc = bi["linea_inicio_proximo_caso"]
            lipc_str = str(lipc) if lipc is not None else "(fin_archivo)"
            out.append(
                f"**Estado**: `{bi['estado']}` | "
                f"linea_fin_real={bi['linea_fin_real']} | "
                f"linea_inicio_proximo_caso={lipc_str} | "
                f"delta={bi['delta']}"
            )
            if bi["alertas"]:
                out.append("**Alertas**: " + ", ".join(f"`{a}`" for a in bi["alertas"]))
            if bi["lineas_gap"]:
                out.append("")
                out.append("| Línea | Clasificación | Texto |")
                out.append("|------:|---------------|-------|")
                for g in bi["lineas_gap"]:
                    # Escapar pipes en el texto para no romper la tabla MD
                    txt = (g["texto"] or "").replace("|", "\\|")
                    # Truncar muy largas para no romper la tabla visualmente
                    if len(txt) > 120:
                        txt = txt[:117] + "..."
                    out.append(f"| {g['linea_abs']} | `{g['clasificacion']}` | {txt} |")
            out.append("")

    return "\n".join(out)


def _render_doc_completo(resultados, comando_args):
    """Renderiza la cabecera del MD + todos los casos separados por ---."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    n_casos = len([r for r in resultados if "error" not in r])
    n_errores = len([r for r in resultados if "error" in r])

    # Resumen global de estados de borde inferior
    estados_borde = Counter()
    n_alertas = 0
    for r in resultados:
        if "error" in r:
            continue
        bi = r.get("borde_inferior")
        if bi is not None:
            estados_borde[bi["estado"]] += 1
            n_alertas += len(bi.get("alertas", []))

    out = [
        "# Auditoría de fallos",
        f"Generado: {ts}",
        f"Comando: `{comando_args}`",
        f"Casos auditados: {n_casos}" + (f" (errores: {n_errores})" if n_errores else ""),
    ]
    if estados_borde:
        # Orden estable: primero los más críticos, después los benignos
        orden = [
            EST_SOLAPADO, EST_GAP_RESIDUO, EST_GAP_SOLO_HEADERS,
            EST_HEADER_NORMAL, EST_CONTINUO, EST_FIN_ARCHIVO,
        ]
        partes = [f"{e}={estados_borde[e]}" for e in orden if estados_borde.get(e)]
        # Cualquier estado no esperado (defensivo)
        for e, v in estados_borde.items():
            if e not in orden:
                partes.append(f"{e}={v}")
        resumen_borde = "Borde inferior: " + ", ".join(partes)
        if n_alertas:
            resumen_borde += f" | alertas totales: {n_alertas}"
        out.append(resumen_borde)
    out.extend([
        "",
        "---",
        "",
    ])
    for r in resultados:
        out.append(_render_caso(r))
        out.append("")
        out.append("---")
        out.append("")
    return "\n".join(out)


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_paginas(s):
    """'306' → [306]. '306,309,1066' → [306, 309, 1066]."""
    return [int(p.strip()) for p in s.split(",") if p.strip()]


def _seleccionar_random(filas_loc, n, tomo=None, status=None, rng=None):
    if rng is None:
        rng = random
    candidatos = filas_loc
    if tomo is not None:
        candidatos = [r for r in candidatos if int(r["tomo"]) == int(tomo)]
    if status is not None:
        candidatos = [r for r in candidatos if r.get("status", "") == status]
    if not candidatos:
        return []
    n = min(n, len(candidatos))
    return rng.sample(candidatos, n)


def main():
    ap = argparse.ArgumentParser(
        description="Auditoría manual de bloques del corpus CSJN"
    )
    ap.add_argument("--tomo", type=int, help="Tomo (ej: 349)")
    ap.add_argument("--pagina", type=str, help="Página o lista coma-separada (ej: 306 o 306,309)")
    ap.add_argument("--random", type=int, help="Seleccionar N casos al azar")
    ap.add_argument("--seed", type=int, default=None,
                    help="Seed para --random (reproducibilidad). Sin esto, cada corrida da una muestra distinta.")
    ap.add_argument("--status", type=str, help="Filtrar --random por status (ej: ok_cortado_en_indice)")
    ap.add_argument("--corpus", type=str, default=str(DEFAULT_CORPUS),
                    help=f"Directorio del corpus (default: {DEFAULT_CORPUS})")
    ap.add_argument("--localizados", type=str, default=str(DEFAULT_LOCALIZADOS),
                    help=f"Ruta a fallos_localizados.csv (default: {DEFAULT_LOCALIZADOS})")
    ap.add_argument("--mapa", type=str, default=str(DEFAULT_MAPA),
                    help=f"Ruta a mapa_paginas.csv (default: {DEFAULT_MAPA})")
    ap.add_argument("--output", type=str, default=None,
                    help="Ruta de salida MD (default: scripts/auditoria/output/auditoria_<ts>.md)")
    ap.add_argument("--stdout", action="store_true",
                    help="Imprimir a stdout en vez de archivo")
    args = ap.parse_args()

    # Validar paths
    for label, p in (("corpus", args.corpus), ("localizados", args.localizados), ("mapa", args.mapa)):
        if not Path(p).exists():
            print(f"ERROR: no encontré '{label}' en `{p}`. "
                  f"Si moviste el repo, pasame --{label} <ruta>", file=sys.stderr)
            sys.exit(2)

    # Validar combinación de flags
    if args.random is None and (args.tomo is None or args.pagina is None):
        print("ERROR: usar --tomo X --pagina Y, o --random N [--tomo X] [--status Y]", file=sys.stderr)
        sys.exit(2)

    # Cargar CSVs una sola vez (cache compartido)
    cache = {}
    cache["filas_loc"], _ = cargar_localizados(args.localizados)
    cache["headers_por_archivo"] = cargar_proximos_headers(args.mapa)

    # Construir lista de (tomo, pagina) a auditar
    pares = []  # lista de (tomo, pagina)
    if args.random:
        rng = random.Random(args.seed) if args.seed is not None else None
        seleccion = _seleccionar_random(
            cache["filas_loc"], args.random,
            tomo=args.tomo, status=args.status, rng=rng,
        )
        for r in seleccion:
            pares.append((int(r["tomo"]), int(r["pagina_inicio"])))
    else:
        paginas = _parse_paginas(args.pagina)
        for p in paginas:
            pares.append((args.tomo, p))

    # Deduplicar manteniendo orden
    vistos = set()
    pares_dedup = []
    for par in pares:
        if par not in vistos:
            vistos.add(par)
            pares_dedup.append(par)

    if not pares_dedup:
        print("ERROR: no hay casos que auditar (filtros vacíos?)", file=sys.stderr)
        sys.exit(2)

    # Auditar
    resultados = []
    for tomo, pagina in pares_dedup:
        r = auditar_fallo(
            tomo, pagina,
            corpus_dir=args.corpus,
            localizados_path=args.localizados,
            mapa_path=args.mapa,
            _cache=cache,
        )
        # También deduplicar por caso_id_canonico (si dos páginas resuelven al mismo caso)
        if "error" not in r:
            cid = r["caso_id_canonico"]
            if any(rr.get("caso_id_canonico") == cid for rr in resultados):
                continue
        resultados.append(r)

    # Renderizar
    cmd_str = " ".join(sys.argv[1:])
    md = _render_doc_completo(resultados, cmd_str)

    # Output
    if args.stdout:
        print(md)
    else:
        if args.output:
            out_path = Path(args.output)
        else:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            out_path = DEFAULT_OUTPUT_DIR / f"auditoria_{ts}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")

        # Resumen a stdout
        n_ok = len([r for r in resultados if "error" not in r])
        n_err = len([r for r in resultados if "error" in r])
        total_residuo = sum(r.get("lineas_residuo", 0) for r in resultados if "error" not in r)
        total_lineas = sum(r.get("n_lineas_bloque", 0) for r in resultados if "error" not in r)
        pct_global = round(100 * total_residuo / total_lineas, 2) if total_lineas else 0.0
        print(f"[OK] {out_path}")
        print(f"     {n_ok} casos auditados" + (f" ({n_err} errores)" if n_err else ""))
        print(f"     líneas residuo total: {total_residuo} / {total_lineas} ({pct_global}%)")
        # Top 3 casos con más residuo (si hay >1 caso)
        if n_ok > 1:
            top = sorted(
                [r for r in resultados if "error" not in r],
                key=lambda r: r.get("porcentaje_residuo", 0),
                reverse=True,
            )[:3]
            if top and top[0].get("porcentaje_residuo", 0) > 5:
                print(f"     top residuo:")
                for r in top:
                    if r.get("porcentaje_residuo", 0) > 5:
                        print(f"       {r['caso_id_canonico']}: {r['porcentaje_residuo']}% ({r['lineas_residuo']} líneas)")


if __name__ == "__main__":
    main()
