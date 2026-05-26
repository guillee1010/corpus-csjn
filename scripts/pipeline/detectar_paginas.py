#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detectar_paginas.py

Detecta los headers de página dentro de los .md del corpus CSJN.

Heurística:
  - Para cada archivo, recorre línea por línea.
  - Cuando una línea (después de strip y reemplazo de NBSP) es exactamente
    el número del tomo, mira las vecinas i-3..i-1, i+1..i+2.
  - Si alguna vecina es un entero plausible (1..5000), la considera el
    número de página y registra la detección.
  - Si hay más de una vecina candidata, se queda con la más cercana al
    número del tomo.
  - Las apariciones del número del tomo en medio del cuerpo del texto, sin
    número plausible cerca, no se cuentan.

Uso (PowerShell o cualquier shell):
    python detectar_paginas.py <carpeta_corpus> [<salida_csv>] [<ruta_catalogo>]

Ejemplo:
    python detectar_paginas.py "G:\\Mi unidad\\corpus_csjn" "G:\\Mi unidad\\mapa_paginas.csv"

Si no se pasa salida_csv, escribe mapa_paginas.csv en el directorio actual.
Si no se pasa ruta_catalogo, intenta catalogo_v14.csv en el directorio actual
(la validación cruzada es opcional: si el catálogo no está, se omite).

Asume que construir_catalogo.py está en la misma carpeta que este script
(usa su función extraer_tomo_de_filename).
"""

__version__ = "1.0"  # H076


import csv
import sys
from collections import Counter
from pathlib import Path

# Importar la lógica de filename → tomo desde construir_catalogo.py
# para no duplicar parsers.
sys.path.insert(0, str(Path(__file__).parent))
from construir_catalogo import extraer_tomo_de_filename


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

GAP_FLAG = 3  # Saltos > 3 páginas se reportan como sospechosos


def _es_numero(s, lo=1, hi=10000):
    """¿La cadena `s` (ya strip + sin NBSP) es un entero entre lo y hi?"""
    if not s.isdigit():
        return False
    n = int(s)
    return lo <= n <= hi


def _norm(linea):
    """Strip + reemplazo de NBSP por espacio + strip de nuevo."""
    return linea.replace('\xa0', ' ').strip()


def detectar_paginas_en_md(ruta_md, tomo, ventana=(3, 2), limpiar=True):
    """
    Detecta headers de página en un .md.

    Parámetros
    ----------
    ruta_md : str o Path
    tomo    : int — número del tomo del archivo
    ventana : tuple (atras, adelante) — cuántas líneas mirar a cada lado
              cuando se ve la línea-tomo. Default: 3 atrás, 2 adelante.
    limpiar : bool — si True (default) aplica post-procesamiento para
              filtrar duplicados consecutivos y outliers.

    Devuelve
    --------
    Si limpiar=True (default):
        tuple (detecciones, conteos_filtrado)
        - detecciones: list de (linea_header, pagina), 0-indexada
        - conteos_filtrado: dict con n filas filtradas por regla
    Si limpiar=False:
        list de tuplas (linea_header, pagina), sin filtrar.
    """
    with open(ruta_md, encoding='utf-8') as f:
        lineas = f.readlines()
    raw = detectar_en_lineas(lineas, tomo, ventana)
    if not limpiar:
        return raw
    return limpiar_detecciones(raw)


def detectar_en_lineas(lineas, tomo, ventana=(3, 2)):
    """Versión testeable: recibe lista de líneas en lugar de ruta."""
    tomo_str = str(tomo)
    atras, adelante = ventana

    detecciones = []
    for i, l in enumerate(lineas):
        if _norm(l) != tomo_str:
            continue
        # Buscar candidatas. El patrón editorial real tiene la página ANTES
        # del tomo (offset negativo), así que priorizamos negativas sobre
        # positivas. Dentro de cada signo, la más cercana gana.
        cand_atras = []   # offsets negativos: (distancia, pagina)
        cand_adelante = []  # offsets positivos
        for offset in range(-atras, adelante + 1):
            if offset == 0:
                continue
            j = i + offset
            if j < 0 or j >= len(lineas):
                continue
            s = _norm(lineas[j])
            if _es_numero(s):
                if offset < 0:
                    cand_atras.append((abs(offset), int(s)))
                else:
                    cand_adelante.append((abs(offset), int(s)))
        if cand_atras:
            cand_atras.sort()
            _, pagina = cand_atras[0]
        elif cand_adelante:
            cand_adelante.sort()
            _, pagina = cand_adelante[0]
        else:
            continue
        detecciones.append((i, pagina))

    return detecciones


# ---------------------------------------------------------------------------
# Post-procesamiento: limpieza de falsos positivos
# ---------------------------------------------------------------------------

# Si dos detecciones tienen la misma página y están a menos de N líneas, la
# segunda es un duplicado del header (típicamente cuando la página coincide
# numéricamente con el tomo y ambas líneas matchean como "línea-tomo").
DUP_LINEAS_UMBRAL = 5

# Si una página rompe monotonía y se aleja más de M páginas de ambas vecinas,
# es un outlier (típicamente apariciones del número del tomo en cuerpo de
# texto que coinciden por azar con un número plausible cerca).
OUTLIER_PAGINAS_UMBRAL = 10


def filtrar_duplicados_consecutivos(detecciones, umbral_lineas=DUP_LINEAS_UMBRAL):
    """
    Elimina detecciones que tienen la misma página que la inmediata anterior
    y están a ≤ umbral_lineas líneas. Devuelve (lista_filtrada, n_filtradas).
    """
    if not detecciones:
        return detecciones, 0
    out = [detecciones[0]]
    n_filtradas = 0
    for ln, pg in detecciones[1:]:
        ln_prev, pg_prev = out[-1]
        if pg == pg_prev and (ln - ln_prev) <= umbral_lineas:
            n_filtradas += 1
            continue
        out.append((ln, pg))
    return out, n_filtradas


def filtrar_outliers(detecciones, umbral_paginas=OUTLIER_PAGINAS_UMBRAL):
    """
    Elimina detecciones cuya página difiere de ambas vecinas (anterior y
    siguiente en la misma lista) en más de umbral_paginas, mientras que
    las dos vecinas están razonablemente cerca entre sí.

    Captura tanto outliers descendentes (1591 → 338 → 1593) como
    ascendentes (19 → 339 → 21).

    Solo aplica a detecciones que tienen vecinas a ambos lados (no toca
    primera ni última).

    Devuelve (lista_filtrada, n_filtradas).
    """
    if len(detecciones) < 3:
        return detecciones, 0
    out = [detecciones[0]]
    n_filtradas = 0
    for k in range(1, len(detecciones) - 1):
        pg_prev = detecciones[k - 1][1]
        pg_curr = detecciones[k][1]
        pg_next = detecciones[k + 1][1]
        # Outlier: página actual lejos de ambas vecinas, mientras que las
        # vecinas están cerca entre sí (la secuencia continúa sin la actual).
        lejos_de_prev = abs(pg_curr - pg_prev) > umbral_paginas
        lejos_de_next = abs(pg_curr - pg_next) > umbral_paginas
        vecinas_cercanas = abs(pg_next - pg_prev) <= umbral_paginas
        if lejos_de_prev and lejos_de_next and vecinas_cercanas:
            n_filtradas += 1
            continue
        out.append(detecciones[k])
    out.append(detecciones[-1])
    return out, n_filtradas


def limpiar_detecciones(detecciones):
    """
    Aplica las dos reglas de post-procesamiento.
    Devuelve (detecciones_limpias, dict con conteos por regla).
    """
    d1, n_dup = filtrar_duplicados_consecutivos(detecciones)
    d2, n_out = filtrar_outliers(d1)
    return d2, {'duplicados_consecutivos': n_dup, 'outliers': n_out}


# ---------------------------------------------------------------------------
# Reporte por archivo
# ---------------------------------------------------------------------------

def diagnosticar(detecciones, archivo, tomo):
    """
    Devuelve un dict con métricas + lista de anomalías para reportar.
    No imprime nada por sí mismo.
    """
    n = len(detecciones)
    if n == 0:
        return {
            'archivo': archivo,
            'tomo': tomo,
            'n_headers': 0,
            'pagina_min': None,
            'pagina_max': None,
            'monotonia_pct': None,
            'gaps_grandes': [],
            'paginas_duplicadas': {},
            'fuera_de_orden': [],
            'anomalias': ['sin headers detectados'],
        }

    paginas = [p for _, p in detecciones]
    pagina_min = min(paginas)
    pagina_max = max(paginas)

    fuera_de_orden = []
    gaps_grandes = []
    for k in range(len(paginas) - 1):
        a, b = paginas[k], paginas[k + 1]
        if b < a:
            fuera_de_orden.append((detecciones[k], detecciones[k + 1]))
        elif b - a > GAP_FLAG:
            gaps_grandes.append((a, b, b - a))

    pares_ok = (n - 1) - len(fuera_de_orden)
    monotonia_pct = 100.0 * pares_ok / max(1, n - 1)

    repetidas = {p: c for p, c in Counter(paginas).items() if c > 1}

    anomalias = []
    if fuera_de_orden:
        anomalias.append(f"{len(fuera_de_orden)} pares fuera de orden")
    if gaps_grandes:
        gaps_orden = sorted(gaps_grandes, key=lambda x: -x[2])
        top = gaps_orden[:3]
        anomalias.append(
            f"{len(gaps_grandes)} gap(s) > {GAP_FLAG}p (mayores: " +
            ", ".join(f"{a}->{b} (d{d})" for a, b, d in top) + ")"
        )
    if repetidas:
        anomalias.append(f"{len(repetidas)} pagina(s) duplicada(s)")

    return {
        'archivo': archivo,
        'tomo': tomo,
        'n_headers': n,
        'pagina_min': pagina_min,
        'pagina_max': pagina_max,
        'monotonia_pct': monotonia_pct,
        'gaps_grandes': gaps_grandes,
        'paginas_duplicadas': repetidas,
        'fuera_de_orden': fuera_de_orden,
        'anomalias': anomalias,
    }


def resumen_linea(diag):
    """Una línea por archivo para el log de consola."""
    if diag['n_headers'] == 0:
        return f"  {diag['archivo']:<28}  0 headers   ! sin deteccion"
    base = (
        f"  {diag['archivo']:<28}  "
        f"{diag['n_headers']:>5} headers, "
        f"p.{diag['pagina_min']}-{diag['pagina_max']}, "
        f"monot.{diag['monotonia_pct']:>5.1f}%"
    )
    if diag.get('filtrado'):
        base += f"   [{diag['filtrado']}]"
    if diag['anomalias']:
        base += "   ! " + " | ".join(diag['anomalias'])
    return base


# ---------------------------------------------------------------------------
# Validación cruzada: rango detectado vs. rango del catálogo
# ---------------------------------------------------------------------------

def cargar_rangos_catalogo(ruta_catalogo):
    """
    Devuelve {tomo: (pagina_min, pagina_max)} a partir del catálogo.
    Si el catálogo no existe, devuelve {}.
    """
    p = Path(ruta_catalogo)
    if not p.exists():
        return {}
    rangos = {}
    with open(p, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = int(row['tomo'])
            pg = int(row['pagina_inicio'])
            if t not in rangos:
                rangos[t] = [pg, pg]
            else:
                rangos[t][0] = min(rangos[t][0], pg)
                rangos[t][1] = max(rangos[t][1], pg)
    return {t: tuple(v) for t, v in rangos.items()}


def chequear_coherencia_tomo(diag, rango_catalogo_tomo):
    """
    Si el rango detectado en este archivo está totalmente fuera del rango
    del catálogo, o lo excede notablemente, devolver mensaje de aviso.
    """
    if rango_catalogo_tomo is None:
        return None
    cat_min, cat_max = rango_catalogo_tomo
    det_min, det_max = diag['pagina_min'], diag['pagina_max']
    if det_min is None:
        return None
    if det_max < cat_min or det_min > cat_max:
        return (f"rango detectado {det_min}-{det_max} "
                f"fuera del rango del catalogo ({cat_min}-{cat_max})")
    if det_min < cat_min - 5 or det_max > cat_max + 5:
        return (f"rango detectado {det_min}-{det_max} "
                f"excede el del catalogo ({cat_min}-{cat_max})")
    return None


# ---------------------------------------------------------------------------
# Recorrido del corpus + escritura del CSV
# ---------------------------------------------------------------------------

def descubrir_archivos(carpeta):
    """
    Devuelve lista de (Path, tomo) ordenada por (tomo, nombre).
    Filtra .md cuyo filename no permite extraer tomo, y los tomos 335 y 336.
    """
    carpeta = Path(carpeta)
    archivos = []
    descartados = []
    for p in sorted(carpeta.glob('*.md')):
        t = extraer_tomo_de_filename(p.name)
        if t is None:
            descartados.append((p.name, "no se pudo extraer tomo del nombre"))
            continue
        if t in (335, 336):
            descartados.append((p.name, f"tomo {t} excluido (problemas conocidos)"))
            continue
        archivos.append((p, t))
    archivos.sort(key=lambda x: (x[1], x[0].name))
    return archivos, descartados


def procesar_corpus(carpeta_corpus, salida_csv, ruta_catalogo=None):
    archivos, descartados = descubrir_archivos(carpeta_corpus)

    # Preparar archivo de log paralelo a la consola
    salida_csv_path = Path(salida_csv)
    log_path = salida_csv_path.with_name(salida_csv_path.stem + '_log.txt')
    log_lines = []

    def emit(s=""):
        """Imprime y acumula para el log."""
        print(s)
        log_lines.append(s)

    emit(f"Carpeta corpus: {carpeta_corpus}")
    emit(f"Archivos a procesar: {len(archivos)}")
    if descartados:
        emit(f"Archivos descartados ({len(descartados)}):")
        for nombre, motivo in descartados:
            emit(f"  {nombre}: {motivo}")
    emit()

    rangos_catalogo = cargar_rangos_catalogo(ruta_catalogo) if ruta_catalogo else {}
    if rangos_catalogo:
        emit(f"Catalogo cargado: rangos para {len(rangos_catalogo)} tomos")
    else:
        emit("(catalogo no disponible: sin validacion cruzada)")
    emit()

    filas_csv = []
    filas_filtradas = []  # registro de detecciones eliminadas en post-procesamiento
    diagnosticos = []
    archivos_con_anomalias = []
    total_dup = 0
    total_out = 0

    for ruta, tomo in archivos:
        # Detectar crudas y filtrar para tener visibilidad de qué se descartó
        with open(ruta, encoding='utf-8') as f:
            lineas = f.readlines()
        raw = detectar_en_lineas(lineas, tomo)
        # Aplicar filtros uno por uno para registrar qué quedó afuera
        d_sin_dup, n_dup = filtrar_duplicados_consecutivos(raw)
        descartadas_dup = _descartadas(raw, d_sin_dup)
        for ln, pg in descartadas_dup:
            filas_filtradas.append({
                'tomo': tomo, 'archivo': ruta.name,
                'linea_header': ln, 'pagina': pg,
                'motivo': 'duplicado_consecutivo',
            })

        d_sin_out, n_out = filtrar_outliers(d_sin_dup)
        descartadas_out = _descartadas(d_sin_dup, d_sin_out)
        for ln, pg in descartadas_out:
            filas_filtradas.append({
                'tomo': tomo, 'archivo': ruta.name,
                'linea_header': ln, 'pagina': pg,
                'motivo': 'outlier',
            })

        detecciones = d_sin_out
        total_dup += n_dup
        total_out += n_out

        diag = diagnosticar(detecciones, ruta.name, tomo)

        if n_dup or n_out:
            partes = []
            if n_dup:
                partes.append(f"{n_dup} dup")
            if n_out:
                partes.append(f"{n_out} outlier(s)")
            diag['filtrado'] = " + ".join(partes) + " filtrado"
        else:
            diag['filtrado'] = ""

        coherencia = chequear_coherencia_tomo(diag, rangos_catalogo.get(tomo))
        if coherencia:
            diag['anomalias'].append(coherencia)

        diagnosticos.append(diag)
        if diag['anomalias']:
            archivos_con_anomalias.append(diag['archivo'])

        for linea_header, pagina in detecciones:
            filas_csv.append({
                'tomo': tomo,
                'archivo': ruta.name,
                'linea_header': linea_header,
                'pagina': pagina,
            })

        emit(resumen_linea(diag))

    total_headers = sum(d['n_headers'] for d in diagnosticos)
    emit()
    emit("=" * 70)
    emit(f"Total: {len(archivos)} archivos, {total_headers} headers detectados")
    emit(f"Filtrados en post-procesamiento: {total_dup} duplicados, {total_out} outliers")
    if archivos_con_anomalias:
        emit(f"Archivos con anomalias ({len(archivos_con_anomalias)}):")
        for a in archivos_con_anomalias:
            emit(f"  - {a}")
    else:
        emit("Sin anomalias reportadas.")
    emit("=" * 70)

    # Escribir mapa principal
    with open(salida_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f, fieldnames=['tomo', 'archivo', 'linea_header', 'pagina'])
        writer.writeheader()
        writer.writerows(filas_csv)
    emit(f"\nCSV escrito: {salida_csv_path}  ({len(filas_csv)} filas)")

    # Escribir resumen por archivo
    resumen_path = salida_csv_path.with_name(salida_csv_path.stem + '_resumen.csv')
    with open(resumen_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'tomo', 'archivo', 'n_headers', 'pagina_min', 'pagina_max',
            'monotonia_pct', 'dup_filtrados', 'outliers_filtrados',
            'n_gaps_grandes', 'n_paginas_duplicadas_postfiltro',
            'n_pares_fuera_de_orden', 'anomalias',
        ])
        writer.writeheader()
        for d, (ruta, tomo) in zip(diagnosticos, archivos):
            # n_dup y n_out por archivo: hay que mirar filas_filtradas
            n_dup_arch = sum(1 for r in filas_filtradas
                             if r['archivo'] == d['archivo'] and r['motivo'] == 'duplicado_consecutivo')
            n_out_arch = sum(1 for r in filas_filtradas
                             if r['archivo'] == d['archivo'] and r['motivo'] == 'outlier')
            writer.writerow({
                'tomo': d['tomo'],
                'archivo': d['archivo'],
                'n_headers': d['n_headers'],
                'pagina_min': d['pagina_min'] if d['pagina_min'] is not None else '',
                'pagina_max': d['pagina_max'] if d['pagina_max'] is not None else '',
                'monotonia_pct': f"{d['monotonia_pct']:.2f}" if d['monotonia_pct'] is not None else '',
                'dup_filtrados': n_dup_arch,
                'outliers_filtrados': n_out_arch,
                'n_gaps_grandes': len(d.get('gaps_grandes', [])),
                'n_paginas_duplicadas_postfiltro': len(d.get('paginas_duplicadas', {})),
                'n_pares_fuera_de_orden': len(d.get('fuera_de_orden', [])),
                'anomalias': ' | '.join(d['anomalias']) if d['anomalias'] else '',
            })
    emit(f"Resumen escrito: {resumen_path}  ({len(diagnosticos)} filas)")

    # Escribir filtradas
    filtradas_path = salida_csv_path.with_name(salida_csv_path.stem + '_filtradas.csv')
    with open(filtradas_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'tomo', 'archivo', 'linea_header', 'pagina', 'motivo'])
        writer.writeheader()
        writer.writerows(filas_filtradas)
    emit(f"Filtradas escritas: {filtradas_path}  ({len(filas_filtradas)} filas)")

    # Escribir log
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    print(f"Log escrito: {log_path}")


def _descartadas(antes, despues):
    """Devuelve la lista de tuplas (linea, pagina) que están en `antes` pero
    no en `despues`. Asume que `despues` es subconjunto ordenado de `antes`."""
    set_despues = set(despues)
    return [t for t in antes if t not in set_despues]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    carpeta_corpus = argv[1]
    salida_csv = argv[2] if len(argv) >= 3 else 'mapa_paginas.csv'
    ruta_catalogo = argv[3] if len(argv) >= 4 else '../../output/catalogo/catalogo.csv'
    procesar_corpus(carpeta_corpus, salida_csv, ruta_catalogo)


if __name__ == '__main__':
    main(sys.argv)
