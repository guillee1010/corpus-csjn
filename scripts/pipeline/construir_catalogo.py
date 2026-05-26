#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construir_catalogo.py

Construye un catálogo heurístico de fallos de la Corte Suprema de Justicia
de la Nación (CSJN) a partir de los índices oficiales presentes al final
de cada archivo .md del corpus.

ENFOQUE
-------
El catálogo NO es un ground truth absoluto. Es un mapa heurístico construido
a partir de los índices editoriales oficiales. Sirve para:

  1) Localizar fallos en el corpus (tomo, página inicio, página fin estimada).
  2) Indexar los nombres bajo los cuales el editor catalogó cada fallo.
  3) Validar contra otros métodos de detección (parser de cuerpo) cruzando
     listas y mirando las disonancias.

ROBUSTEZ ANTE VARIANTES EDITORIALES
-----------------------------------
El formato del índice cambió a lo largo de los 18 años cubiertos (tomos
329-349, 2006-2024). Variantes detectadas y manejadas:

  - Punto final tras la página: presente en tomos viejos, ausente en tomos
    nuevos. Regex con punto opcional.
  - Espacio post "p.": espacio normal o NBSP (\\xa0). Regex acepta ambos.
  - Separador en páginas múltiples: coma (",") en tomos viejos, "y" en
    tomos nuevos. Regex acepta ambos.
  - Anclas a mitad de línea: cuando dos entradas del PDF se concatenaron en
    una sola línea durante la conversión. Parser corta por ancla, no por
    línea.
  - Continuación multi-línea de páginas múltiples ("ps. 1316 \\n y 1334"):
    el join de líneas previo al match las une.
  - Cabeceras intermedias del índice: "NOMBRES DE LAS PARTES", letras
    alfabéticas solas (A, B, C), números romanos en paréntesis ((I), (II)).
    Filtradas antes de joinear.

DEDUPLICACIÓN
-------------
NO se aplica dedupe forzado por dirección/cruzada. En cambio, se agrupan
todas las entradas del índice por (tomo, página) y se conservan TODOS los
nombres asociados separados por " | " en la columna `nombres_indice`.

Razón: el formato editorial cambia entre tomos. En 329 las entradas cruzadas
tienen marca sintáctica ("paréntesis envolviendo c/"), en 334 son entradas
planas sin marca, en 348 prácticamente no hay cruzadas. Una regla de dedupe
única para los tres tomos forzaría inventar carátulas o descartar información.
Conservar todos los nombres asociados a cada página es más fiel al índice
original y sirve mejor para búsqueda.

ENTREGABLES
-----------
catalogo_v14.csv: una fila por (tomo, página_inicio). Columnas:
  - tomo: entero (329-349)
  - pagina_inicio: entero, página donde empieza el fallo
  - pagina_fin: entero o vacío, inferido como (página del siguiente fallo - 1)
  - caso_id_canonico: f"{tomo}_p{pagina_inicio}"
  - nombres_indice: nombres del índice asociados a esta página, separados
    por " | ". Si solo hay uno, es ese; si hay varios, son todas las formas
    en que el editor catalogó el fallo (actor, demandado, etc.)
  - n_nombres: cantidad de nombres distintos asociados (1 = entrada única;
    >1 = el fallo aparece bajo múltiples nombres en el índice)
  - n_archivos_indice: en cuántos archivos del corpus aparece esta entrada
    en el índice. Para tomos modernos (343+) suele ser igual al número de
    volúmenes (índice consolidado repetido); para tomos viejos suele ser 1.

NOTA: no se incluye archivo_origen porque en tomos con índice consolidado
multi-volumen (343+) la columna sería engañosa (apuntaría siempre al primer
volumen aunque el cuerpo físicamente esté en otro). Para localizar el cuerpo
de un fallo concreto, usar grep sobre los .md del tomo correspondiente.

secciones_indices_v14.csv: registro de qué secciones de índice hay en cada
archivo. Columnas:
  - tomo, archivo, tipo_indice, linea_inicio, linea_fin
  - tipo_indice: 'nombres', 'materias', 'sumario', 'legislacion', 'general'

USO
---
  python3 construir_catalogo.py --input-dir ../../corpus/

  python3 construir_catalogo.py \\
      --input-dir ../../corpus/ \\
      --output-catalogo ../../output/catalogo/catalogo.csv \\
      --output-secciones ../../output/catalogo/secciones_indices.csv \\
      --verbose
"""

__version__ = "1.0"  # H076


import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# ============================================================================
# REGEX DEL PARSER (todas validadas contra tomos 329, 334, 348)
# ============================================================================

# Header del índice de nombres. Mayúsculas exactas, sin puntos suspensivos.
# Distingue del header de "INDICE GENERAL" que aparece en minúsculas con
# puntos suspensivos al final del libro.
RE_HEADER_INDICE_NOMBRES = re.compile(
    r'^INDICE POR LOS NOMBRES DE LAS PARTES\s*$'
)

# Headers de las otras secciones de índice. Detectados para registro
# en secciones_indices_v14.csv y para delimitar el fin del bloque de nombres.
RE_HEADERS_SECCION = {
    'nombres':     re.compile(r'^INDICE POR LOS NOMBRES DE LAS PARTES\s*$'),
    'materias':    re.compile(r'^INDICE ALFAB[EÉ]TICO POR MATERIAS\s*$'),
    'sumario':     re.compile(r'^INDICE SUMARIO\s*$'),
    'legislacion': re.compile(r'^INDICE DE LEGISLACI[OÓ]N\s*(\(\*\))?\s*$'),
    'general':     re.compile(r'^INDICE GENERAL\s*$'),
}

# Cabecera alfabética dentro del índice de nombres: una o dos letras solas.
RE_CABECERA_ALFA = re.compile(r'^[A-ZÑÁÉÍÓÚ]{1,2}$')

# Header de página dentro del índice: "NOMBRES DE LAS PARTES" (sin "INDICE
# POR LOS"). Aparece como cabecera repetida en cada página del índice impreso.
RE_NOMBRES_PARTES_HDR = re.compile(r'^NOMBRES DE LAS PARTES')

# Número romano en paréntesis: "(VIII)", "(I)", etc. Aparece como complemento
# del header "NOMBRES DE LAS PARTES" en algunos tomos (ej. 348), en línea
# separada.
RE_ROMANO_PARENT = re.compile(r'^\([IVXLCDM]+\)$')

# Filename → tomo. El filename matchea LibroVol{tomo}{sufijo}.md donde sufijo
# puede ser ".1", "-1", "_1", o vacío.
RE_FILENAME_TOMO = re.compile(r'LibroVol(\d{3})')

# Ancla de cierre de entrada en el índice de nombres.
# Patrón general: ":" + " p." o " ps." + número(s) separados por "," o "y" + "."?
# Tolerancias:
#   - whitespace o NBSP (\xa0) entre "p." y el número
#   - separadores ",", "y", o "y" después de coma — todos válidos
#   - punto final opcional (presente en tomos viejos, ausente en nuevos)
#   - NO requiere "$" final (ancla puede estar a mitad de línea cuando la
#     conversión PDF→md concatenó dos entradas)
RE_ANCLA = re.compile(
    r':\s*(ps?\.)\s*[\xa0\s]*'              # ": p." o ": ps." con espacio o NBSP
    r'(\d+(?:\s*[,y]\s*\d+)*)'              # números: "537" o "243, 244, 297" o "1316 y 1334"
    r'\s*\.?',                              # punto final opcional
    re.UNICODE
)

# Detección de cruzada estilo paréntesis (tomos viejos: "AFIP (Aguas... c/)").
# No se usa para dedupe forzado, pero se exporta como columna informativa.
RE_CRUZADA_PARENT = re.compile(r'\([^)]*\bc/[^)]*\)')


# ============================================================================
# DETECCIÓN DE SECCIONES DE ÍNDICE
# ============================================================================

def detectar_secciones(lines):
    """
    Detecta las secciones de índice (nombres, materias, sumario, legislación,
    general) en un archivo .md. Retorna lista de tuplas:
        (tipo_indice, linea_inicio, linea_fin)
    Líneas son 1-indexed, inclusivas en ambos extremos.

    Las secciones de índice (sobre todo legislación y sumario) repiten su
    header como cabecera de página dentro de la propia sección. Para evitar
    contar cada cabecera como una sección nueva, colapsamos matches
    consecutivos del mismo tipo: cuando aparece un match del tipo X y el
    siguiente match (sin otro tipo intermedio) también es de tipo X, los
    fusionamos en una sola sección.
    """
    matches = []  # lista de (tipo, linea_idx_0)
    for i, line in enumerate(lines):
        l = line.strip()
        for tipo, regex in RE_HEADERS_SECCION.items():
            if regex.match(l):
                matches.append((tipo, i))
                break  # una línea solo matchea un tipo

    # Colapsar consecutivos del mismo tipo: el segundo y siguientes son
    # cabeceras de página repetidas dentro de la misma sección.
    matches_colapsados = []
    for tipo, linea in matches:
        if matches_colapsados and matches_colapsados[-1][0] == tipo:
            continue  # mismo tipo que el anterior, descartar (es cabecera repetida)
        matches_colapsados.append((tipo, linea))

    # Calcular linea_fin de cada sección: línea anterior al próximo header
    secciones = []
    for idx, (tipo, linea_inicio_0) in enumerate(matches_colapsados):
        if idx + 1 < len(matches_colapsados):
            linea_fin_0 = matches_colapsados[idx + 1][1] - 1
        else:
            linea_fin_0 = len(lines) - 1
        # Convertir a 1-indexed
        secciones.append((tipo, linea_inicio_0 + 1, linea_fin_0 + 1))

    return secciones


def encontrar_indice_nombres(secciones):
    """
    Dado el listado de secciones detectadas, retorna (linea_inicio, linea_fin)
    del índice de nombres (1-indexed), o None si no se encuentra.

    Si hay múltiples 'nombres' detectados (raro), toma el primero.
    El fin del bloque de nombres es la línea ANTES del siguiente header de
    sección, no el linea_fin calculado por detectar_secciones (que asume
    contigüidad). Acá lo importa es: ¿dónde termina el contenido parseable?
    """
    nombres = [s for s in secciones if s[0] == 'nombres']
    if not nombres:
        return None
    return (nombres[0][1], nombres[0][2])


def extender_inicio_indice_nombres(lines, linea_inicio_1, linea_fin_1,
                                    min_anclas_requeridas=3):
    """
    Fix v15 para tomos modernos (337-349) donde el reflow PDF→md ubica la
    portadilla 'INDICE POR LOS NOMBRES DE LAS PARTES' DESPUÉS de las primeras
    entradas alfabéticas del listado, en lugar de ANTES.

    Estrategia (en orden):
      1. Look-back desde linea_inicio_1 buscando una cabecera alfabética 'A'
         aislada (línea con solo 'A', precedida por línea vacía).
      2. Si se encuentra, verificar que entre 'A' y linea_inicio_1 haya al
         menos `min_anclas_requeridas` líneas con ancla ': p. N'. Esto
         confirma que estamos extendiendo a un listado real, no a una 'A'
         que aparece por otro motivo (cabecera espuria, OCR raro, etc.).
      3. Si la validación pasa, extender el inicio hasta la línea de 'A'.

    Topes de seguridad:
      - Si en el look-back se choca con otro header de sección
        (RE_HEADERS_SECCION), abortar sin extender.
      - Si la línea anterior a 'A' no es vacía, abortar (no es cabecera
        aislada de listado).
      - Si no hay suficientes anclas entre 'A' y el header, abortar.
      - Cota máxima: 200 líneas hacia atrás.

    Retorna (nuevo_inicio_1, linea_fin_1). Si no extiende, retorna el inicio
    original.
    """
    # 0-indexed para iterar
    inicio_0 = linea_inicio_1 - 1
    # Cota: no retroceder más de 200 líneas (un índice alfabético cabe holgado)
    minimo_0 = max(0, inicio_0 - 200)

    candidato_a = None  # índice 0-indexed de la línea con "A"
    for i in range(inicio_0 - 1, minimo_0 - 1, -1):
        l = lines[i].strip()
        # Si encontramos otro header de sección, abortar — no es seguro extender
        if any(rx.match(l) for rx in RE_HEADERS_SECCION.values()):
            return (linea_inicio_1, linea_fin_1)
        # Cabecera alfa de una sola letra "A" — candidata a inicio del listado
        if l == 'A':
            candidato_a = i
            break

    if candidato_a is None:
        return (linea_inicio_1, linea_fin_1)

    # Validación 1: la línea anterior a "A" debería ser vacía (separación
    # visual entre fin de fallo y arranque del índice). Si no, abortar.
    if candidato_a > 0 and lines[candidato_a - 1].strip() != '':
        return (linea_inicio_1, linea_fin_1)

    # Validación 2: contar anclas ": p. N" entre la "A" (exclusive) y
    # linea_inicio_1 (exclusive — es el header). Si hay al menos N, es un
    # listado real.
    n_anclas = 0
    for i in range(candidato_a + 1, inicio_0):
        if RE_ANCLA.search(lines[i]):
            n_anclas += 1
            if n_anclas >= min_anclas_requeridas:
                break

    if n_anclas < min_anclas_requeridas:
        return (linea_inicio_1, linea_fin_1)

    # Extender: nuevo inicio = línea de la "A" (1-indexed)
    nuevo_inicio_1 = candidato_a + 1
    return (nuevo_inicio_1, linea_fin_1)


# ============================================================================
# PARSER DEL ÍNDICE DE NOMBRES
# ============================================================================

def parsear_indice_nombres(lines, linea_inicio_1, linea_fin_1):
    """
    Parsea el bloque del índice de nombres. Retorna lista de tuplas:
        (caratula_normalizada, [paginas])

    Estrategia:
      1. Tomar las líneas del bloque (excluyendo el header).
      2. Filtrar líneas no-entrada: vacías, cabeceras alfa, "NOMBRES DE LAS
         PARTES", romanos en paréntesis.
      3. Joinear todas las líneas restantes en un solo string. Esto hace que
         entradas multi-línea queden contiguas.
      4. Cortar el string por anclas (RE_ANCLA). Cada ancla cierra una entrada.
         El texto desde el final del ancla anterior hasta el inicio de la
         actual es la carátula de la entrada actual.
      5. Limpiar la carátula: quitar guiones de continuación de palabra
         ("Fede- ral" → "Federal"), normalizar espacios.
      6. Extraer páginas del grupo de captura del ancla.
    """
    # Línea inicio en 1-indexed → índice 0-indexed = linea_inicio_1 - 1.
    # Saltar el header (la línea linea_inicio_1) → empezar en linea_inicio_1.
    # Línea fin en 1-indexed → índice exclusive = linea_fin_1.
    bloque = lines[linea_inicio_1:linea_fin_1]

    lineas_utiles = []
    for raw in bloque:
        l = raw.strip()
        if not l:
            continue
        if RE_CABECERA_ALFA.match(l):
            continue
        if RE_NOMBRES_PARTES_HDR.match(l):
            continue
        if RE_ROMANO_PARENT.match(l):
            continue
        # Otra defensa: si por error agarramos un header de sección, lo saltamos
        if any(rx.match(l) for rx in RE_HEADERS_SECCION.values()):
            continue
        lineas_utiles.append(l)

    texto = ' '.join(lineas_utiles)

    entradas = []
    pos = 0
    for m in RE_ANCLA.finditer(texto):
        caratula_raw = texto[pos:m.start()].strip()
        caratula = limpiar_caratula(caratula_raw)
        paginas_str = m.group(2)
        paginas = [int(n) for n in re.findall(r'\d+', paginas_str)]

        # Filtrar entradas vacías o degeneradas (puede pasar al inicio del
        # bloque si hay basura previa al primer ancla)
        if caratula and paginas:
            entradas.append((caratula, paginas))
        pos = m.end()

    return entradas


def limpiar_caratula(s):
    """
    Limpieza mínima de la carátula:
      - Une guiones de continuación de palabra ("Fede- ral" → "Federal")
      - Normaliza espacios múltiples y NBSP
      - Quita whitespace en bordes
    NO hace correcciones agresivas (no toca caracteres OCR raros como "¿",
    no decide entre may/min). Conservar fidelidad al original.
    """
    # NBSP → espacio normal
    s = s.replace('\xa0', ' ')
    # Guion de continuación: letra-espacio-letra → unir
    s = re.sub(r'(\w)-\s+(\w)', r'\1\2', s)
    # Espacios múltiples
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


# ============================================================================
# CONSTRUCCIÓN DEL CATÁLOGO
# ============================================================================

def construir_filas_catalogo(entradas_por_archivo):
    """
    Dado un dict {(tomo, archivo): [(caratula, [paginas])]}, construye la
    lista de filas del catálogo.

    Pasos:
      1. Expandir entradas con páginas múltiples a una entrada por página.
      2. Agrupar por (tomo, página) — todas las entradas que apuntan a la
         misma página son referencias al mismo fallo.
      3. Construir nombres_indice como join de las carátulas únicas (orden
         de aparición preservado).
      4. Calcular pagina_fin por inferencia global por tomo: ordenar las
         páginas del tomo, pagina_fin de cada una = página de la siguiente - 1.
         Última página del tomo: pagina_fin queda vacío.
      5. archivo_origen: el archivo donde apareció la entrada por primera vez
         para esa página. Si la misma página aparece en múltiples archivos
         (no debería pasar dentro de un mismo tomo, pero es defensivo), se
         registra el primero.
    """
    # Paso 1+2: agrupar por (tomo, página)
    grupos = defaultdict(lambda: {'nombres': [], 'archivos': []})
    for (tomo, archivo), entradas in entradas_por_archivo.items():
        for caratula, paginas in entradas:
            for pag in paginas:
                clave = (tomo, pag)
                if caratula not in grupos[clave]['nombres']:
                    grupos[clave]['nombres'].append(caratula)
                if archivo not in grupos[clave]['archivos']:
                    grupos[clave]['archivos'].append(archivo)

    # Paso 4: agrupar por tomo para calcular pagina_fin
    paginas_por_tomo = defaultdict(list)
    for (tomo, pag) in grupos.keys():
        paginas_por_tomo[tomo].append(pag)
    for tomo in paginas_por_tomo:
        paginas_por_tomo[tomo].sort()

    pagina_fin_map = {}
    for tomo, pags_ordenadas in paginas_por_tomo.items():
        for i, pag in enumerate(pags_ordenadas):
            if i + 1 < len(pags_ordenadas):
                pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]
            else:
                pagina_fin_map[(tomo, pag)] = None  # último del tomo

    # Construir filas
    filas = []
    for (tomo, pag), info in sorted(grupos.items()):
        nombres = info['nombres']
        n_archivos = len(info['archivos'])
        nombres_indice = ' | '.join(nombres)
        n_nombres = len(nombres)
        pagina_fin = pagina_fin_map[(tomo, pag)]
        caso_id = f"{tomo}_p{pag}"
        filas.append({
            'tomo': tomo,
            'pagina_inicio': pag,
            'pagina_fin': pagina_fin if pagina_fin is not None else '',
            'caso_id_canonico': caso_id,
            'nombres_indice': nombres_indice,
            'n_nombres': n_nombres,
            'n_archivos_indice': n_archivos,
        })

    return filas


# ============================================================================
# IO
# ============================================================================

def extraer_tomo_de_filename(filename):
    """LibroVol329.1.md → 329. Retorna None si no matchea."""
    m = RE_FILENAME_TOMO.search(filename)
    if not m:
        return None
    return int(m.group(1))


def leer_md(path):
    """Lee un archivo .md tolerando CRLF/LF. Retorna lista de líneas sin
    line terminator."""
    with open(path, encoding='utf-8') as f:
        contenido = f.read()
    # splitlines maneja CRLF, LF, CR
    return contenido.splitlines()


def procesar_archivo(path, verbose=False):
    """
    Procesa un .md. Retorna:
      (tomo, lista_secciones, lista_entradas_indice_nombres)
    o None si el archivo no es procesable.
    """
    filename = path.name
    tomo = extraer_tomo_de_filename(filename)
    if tomo is None:
        if verbose:
            print(f"  [SKIP] {filename}: no se pudo extraer tomo del nombre", file=sys.stderr)
        return None

    lines = leer_md(path)

    secciones = detectar_secciones(lines)
    if verbose:
        print(f"  Secciones detectadas en {filename}:", file=sys.stderr)
        for tipo, ini, fin in secciones:
            print(f"    {tipo}: líneas {ini}-{fin}", file=sys.stderr)

    rango_nombres = encontrar_indice_nombres(secciones)
    if rango_nombres is None:
        if verbose:
            print(f"  [WARN] {filename}: no se encontró 'INDICE POR LOS NOMBRES'", file=sys.stderr)
        return (tomo, secciones, [])

    linea_inicio, linea_fin = rango_nombres
    # Fix v15: si la portadilla del índice quedó intercalada por reflow del
    # PDF→md, extender el inicio hacia atrás hasta la cabecera "A" del listado.
    linea_inicio_ext, linea_fin = extender_inicio_indice_nombres(
        lines, linea_inicio, linea_fin
    )
    if verbose and linea_inicio_ext != linea_inicio:
        print(f"  [FIX-v15] {filename}: inicio del índice extendido "
              f"de L{linea_inicio} a L{linea_inicio_ext}", file=sys.stderr)
    linea_inicio = linea_inicio_ext
    entradas = parsear_indice_nombres(lines, linea_inicio, linea_fin)
    if verbose:
        print(f"  → {len(entradas)} entradas detectadas en el índice de nombres", file=sys.stderr)

    return (tomo, secciones, entradas)


def escribir_catalogo(filas, output_path):
    fieldnames = [
        'tomo', 'pagina_inicio', 'pagina_fin', 'caso_id_canonico',
        'nombres_indice', 'n_nombres', 'n_archivos_indice',
    ]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)


def escribir_secciones(secciones_por_archivo, output_path):
    fieldnames = ['tomo', 'archivo', 'tipo_indice', 'linea_inicio', 'linea_fin']
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (tomo, archivo), secciones in sorted(secciones_por_archivo.items()):
            for tipo, ini, fin in secciones:
                writer.writerow({
                    'tomo': tomo,
                    'archivo': archivo,
                    'tipo_indice': tipo,
                    'linea_inicio': ini,
                    'linea_fin': fin,
                })


# ============================================================================
# REPORTE
# ============================================================================

def imprimir_reporte(estadisticas_por_archivo, filas_catalogo):
    print("\n" + "=" * 70)
    print("REPORTE DE CONSTRUCCIÓN DEL CATÁLOGO")
    print("=" * 70)

    # Estadísticas por archivo
    print(f"\n{'Archivo':<35} {'Tomo':<6} {'Entradas':<10} {'Páginas únicas':<15}")
    print("-" * 70)
    for archivo, stats in sorted(estadisticas_por_archivo.items()):
        print(f"{archivo:<35} {stats['tomo']:<6} "
              f"{stats['n_entradas']:<10} {stats['n_paginas_unicas']:<15}")

    # Estadísticas globales del catálogo
    print("\n" + "-" * 70)
    print("GLOBAL")
    print(f"  Archivos procesados: {len(estadisticas_por_archivo)}")
    print(f"  Filas del catálogo: {len(filas_catalogo)}")

    # Agrupar por tomo
    por_tomo = defaultdict(int)
    multi_nombres = defaultdict(int)
    for f in filas_catalogo:
        por_tomo[f['tomo']] += 1
        if f['n_nombres'] > 1:
            multi_nombres[f['tomo']] += 1

    print(f"\n{'Tomo':<8} {'Fallos':<10} {'Multi-nombre':<15} {'% multi':<10}")
    for tomo in sorted(por_tomo.keys()):
        n = por_tomo[tomo]
        m = multi_nombres[tomo]
        pct = (m / n * 100) if n else 0
        print(f"{tomo:<8} {n:<10} {m:<15} {pct:.1f}%")
    print("=" * 70)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Construye un catálogo heurístico de fallos CSJN desde "
                    "los índices oficiales de los .md."
    )
    parser.add_argument(
        '--input-dir', type=Path, default=Path('../../corpus'),
        help='Directorio con los archivos .md (default: ../../corpus)'
    )
    parser.add_argument(
        '--output-catalogo', type=Path, default=Path('../../output/catalogo/catalogo.csv'),
        help='Ruta del CSV del catálogo (default: ../../output/catalogo/catalogo.csv)'
    )
    parser.add_argument(
        '--output-secciones', type=Path, default=Path('../../output/catalogo/secciones_indices.csv'),
        help='Ruta del CSV de secciones (default: ../../output/catalogo/secciones_indices.csv)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Reporte detallado por archivo procesado'
    )
    parser.add_argument(
        '--pattern', default='LibroVol*.md',
        help='Glob pattern para los .md (default: LibroVol*.md)'
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        print(f"ERROR: el directorio {args.input_dir} no existe", file=sys.stderr)
        sys.exit(1)

    archivos_md = sorted(args.input_dir.glob(args.pattern))
    if not archivos_md:
        print(f"ERROR: no se encontraron archivos {args.pattern} en {args.input_dir}",
              file=sys.stderr)
        sys.exit(1)

    print(f"Procesando {len(archivos_md)} archivos de {args.input_dir}...",
          file=sys.stderr)

    entradas_por_archivo = {}      # (tomo, archivo) → [(caratula, [paginas])]
    secciones_por_archivo = {}     # (tomo, archivo) → [(tipo, ini, fin)]
    estadisticas = {}              # archivo → stats

    for path in archivos_md:
        if args.verbose:
            print(f"\n{path.name}:", file=sys.stderr)
        resultado = procesar_archivo(path, verbose=args.verbose)
        if resultado is None:
            continue
        tomo, secciones, entradas = resultado
        clave = (tomo, path.name)
        entradas_por_archivo[clave] = entradas
        secciones_por_archivo[clave] = secciones

        # Stats: páginas únicas en este archivo
        paginas_unicas = set()
        for _, pags in entradas:
            paginas_unicas.update(pags)
        estadisticas[path.name] = {
            'tomo': tomo,
            'n_entradas': len(entradas),
            'n_paginas_unicas': len(paginas_unicas),
        }

    filas_catalogo = construir_filas_catalogo(entradas_por_archivo)

    escribir_catalogo(filas_catalogo, args.output_catalogo)
    escribir_secciones(secciones_por_archivo, args.output_secciones)

    print(f"\nCatálogo escrito: {args.output_catalogo} ({len(filas_catalogo)} filas)",
          file=sys.stderr)
    print(f"Secciones escritas: {args.output_secciones}", file=sys.stderr)

    imprimir_reporte(estadisticas, filas_catalogo)


if __name__ == '__main__':
    main()
