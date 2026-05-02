#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cruzar_catalogo_y_mapa.py

Cruza catalogo_v14.csv (fallos según el índice editorial) con
mapa_paginas.csv (headers de página detectados en los .md del corpus)
para producir un CSV donde cada fallo del catálogo queda localizado
físicamente: archivo .md, línea de inicio, línea de fin.

Uso (PowerShell o cualquier shell):
    python cruzar_catalogo_y_mapa.py <catalogo_csv> <mapa_csv> [<carpeta_corpus>] [<salida_csv>] [<secciones_indices_csv>]

Ejemplo:
    python cruzar_catalogo_y_mapa.py catalogo_v14.csv mapa_paginas.csv ..\\markdowns_v2 fallos_localizados.csv ..\\secciones_indices_v14.csv

La carpeta del corpus es opcional pero recomendada: se usa para conocer
la cantidad total de líneas de cada .md y así poder calcular linea_fin
para los últimos fallos del tomo (los que tienen pagina_fin vacía en
el catálogo). Si no se pasa, esos fallos quedan con linea_fin vacía y
status='ultimo_del_tomo_sin_fin'.

El CSV de secciones de índices es opcional pero recomendado: si se pasa,
para los últimos fallos del tomo se usa la línea de inicio del índice
de nombres como tope del bloque, evitando que el bloque del último
fallo arrastre el aparato editorial de índices (nombres, materias,
sumario, legislación, general). Si no se pasa, se mantiene el
comportamiento anterior (linea_fin = última línea del .md).

Status posibles:
  ok                          — cruce limpio
  ok_cortado_en_indice        — último fallo del tomo, linea_fin = inicio del índice de nombres - 1
  pagina_no_en_mapa           — pagina_inicio del catálogo no está en el mapa
  ultimo_del_tomo             — último fallo del tomo, linea_fin = última línea del .md (fallback)
  ultimo_del_tomo_sin_fin     — último fallo pero sin acceso al corpus → linea_fin vacía
  pagina_fin_no_en_mapa       — pagina_fin+1 no aparece como header (fallback)
  fallo_cruza_archivos        — fallo cuyo cuerpo abarca dos archivos físicos
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Carga y resolución de mapa
# ---------------------------------------------------------------------------

def cargar_catalogo(ruta):
    """Devuelve lista de dicts con las filas del catálogo."""
    filas = []
    with open(ruta, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['tomo'] = int(row['tomo'])
            row['pagina_inicio'] = int(row['pagina_inicio'])
            row['pagina_fin'] = (
                int(row['pagina_fin']) if row['pagina_fin'] not in ('', None) else None
            )
            row['n_nombres'] = int(row['n_nombres'])
            row['n_archivos_indice'] = int(row['n_archivos_indice'])
            filas.append(row)
    return filas


def cargar_mapa(ruta):
    """
    Devuelve un dict {(tomo, pagina): (archivo, linea_header)} con resolución
    de duplicados: cuando una (tomo, pagina) aparece en dos archivos, se
    queda la entrada con la línea más baja (más cuerpo después).

    También devuelve un dict {(tomo, archivo): [(linea, pagina), ...]}
    con todas las entradas por archivo, ordenadas por línea — útil para
    operaciones internas.
    """
    todas = []
    with open(ruta, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            todas.append({
                'tomo': int(row['tomo']),
                'archivo': row['archivo'],
                'linea_header': int(row['linea_header']),
                'pagina': int(row['pagina']),
            })

    # Resolver duplicados (tomo, pagina): quedarse con la línea más baja
    por_clave = defaultdict(list)  # (tomo, pagina) -> lista de entradas
    for r in todas:
        por_clave[(r['tomo'], r['pagina'])].append(r)

    mapa_pagina = {}
    duplicados_resueltos = []
    for clave, entradas in por_clave.items():
        if len(entradas) == 1:
            e = entradas[0]
            mapa_pagina[clave] = (e['archivo'], e['linea_header'])
        else:
            # Quedarse con la entrada de línea más baja (más cuerpo después)
            elegida = min(entradas, key=lambda e: e['linea_header'])
            mapa_pagina[clave] = (elegida['archivo'], elegida['linea_header'])
            duplicados_resueltos.append({
                'tomo': clave[0], 'pagina': clave[1],
                'elegido': elegida['archivo'],
                'descartados': [e['archivo'] for e in entradas if e is not elegida],
            })

    # Diccionario por archivo, ordenado
    por_archivo = defaultdict(list)
    for r in todas:
        por_archivo[(r['tomo'], r['archivo'])].append((r['linea_header'], r['pagina']))
    for k in por_archivo:
        por_archivo[k].sort()

    return mapa_pagina, dict(por_archivo), duplicados_resueltos


def cargar_lineas_de_archivos(carpeta_corpus):
    """
    Para cada .md en la carpeta, devuelve {filename: n_lineas}.
    Si carpeta es None, devuelve {}.
    """
    if carpeta_corpus is None:
        return {}
    carpeta = Path(carpeta_corpus)
    if not carpeta.exists():
        print(f"AVISO: carpeta {carpeta} no existe — los últimos fallos del tomo no tendrán linea_fin")
        return {}
    out = {}
    for p in carpeta.glob('*.md'):
        with open(p, encoding='utf-8') as f:
            out[p.name] = sum(1 for _ in f)
    return out


def cargar_indices_nombres(ruta):
    """
    Devuelve dict {archivo: linea_inicio_indice_nombres}.

    Lee secciones_indices_v14.csv y para cada archivo retorna la línea
    de inicio del índice de nombres. Esa línea marca el fin de la zona
    de fallos del archivo: todo lo que está después es aparato editorial
    (índices de nombres, materias, sumario, legislación, general).

    Si ruta es None, no se pasa, o no existe, devuelve dict vacío y el
    script cae al comportamiento anterior (linea_fin = última línea
    del .md para últimos del tomo).
    """
    if ruta is None:
        return {}
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        print(f"AVISO: archivo de secciones de índices {ruta_path} no existe — "
              f"se usará última línea del .md para últimos del tomo")
        return {}
    indices = {}
    with open(ruta_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('tipo_indice') != 'nombres':
                continue
            archivo = row['archivo']
            linea_inicio = int(row['linea_inicio'])
            indices[archivo] = linea_inicio
    return indices


# ---------------------------------------------------------------------------
# Cruce
# ---------------------------------------------------------------------------

def cruzar(catalogo, mapa_pagina, n_lineas_por_archivo, indices_nombres_por_archivo=None):
    """
    Para cada fila del catálogo, calcula archivo, linea_inicio, linea_fin
    y status. Devuelve lista de dicts.

    indices_nombres_por_archivo: dict {archivo: linea_inicio_indice_nombres}.
    Si se provee y el archivo del fallo está en el dict, los últimos
    fallos del tomo se cortan en linea_inicio_indice - 1 (status
    'ok_cortado_en_indice'). Si no, fallback a última línea del .md
    (status 'ultimo_del_tomo').
    """
    if indices_nombres_por_archivo is None:
        indices_nombres_por_archivo = {}

    resultados = []
    for fila in catalogo:
        tomo = fila['tomo']
        pg_ini = fila['pagina_inicio']
        pg_fin = fila['pagina_fin']

        out = {
            'caso_id_canonico': fila['caso_id_canonico'],
            'tomo': tomo,
            'archivo': '',
            'pagina_inicio': pg_ini,
            'pagina_fin': pg_fin if pg_fin is not None else '',
            'linea_inicio': '',
            'linea_fin': '',
            'nombres_indice': fila['nombres_indice'],
            'n_nombres': fila['n_nombres'],
            'status': '',
        }

        # Buscar linea_inicio
        clave_ini = (tomo, pg_ini)
        if clave_ini not in mapa_pagina:
            out['status'] = 'pagina_no_en_mapa'
            resultados.append(out)
            continue

        archivo_ini, linea_ini = mapa_pagina[clave_ini]
        out['archivo'] = archivo_ini
        out['linea_inicio'] = linea_ini

        # Buscar linea_fin
        if pg_fin is None:
            # Último fallo del tomo
            if archivo_ini in indices_nombres_por_archivo:
                # Cortar antes del aparato de índices del .md
                out['linea_fin'] = indices_nombres_por_archivo[archivo_ini] - 1
                out['status'] = 'ok_cortado_en_indice'
            elif archivo_ini in n_lineas_por_archivo:
                # Fallback: última línea del .md (incluye índices, ruidoso)
                out['linea_fin'] = n_lineas_por_archivo[archivo_ini] - 1
                out['status'] = 'ultimo_del_tomo'
            else:
                out['linea_fin'] = ''
                out['status'] = 'ultimo_del_tomo_sin_fin'
            resultados.append(out)
            continue

        # Buscar header de la página siguiente (pg_fin + 1)
        clave_fin = (tomo, pg_fin + 1)
        if clave_fin in mapa_pagina:
            archivo_fin, linea_fin_header = mapa_pagina[clave_fin]
            if archivo_fin == archivo_ini:
                # Caso normal: el siguiente fallo está en el mismo archivo
                out['linea_fin'] = linea_fin_header - 1
                out['status'] = 'ok'
            else:
                # El fallo cruza archivos: termina con el último header del archivo de inicio
                # y el siguiente fallo arranca en otro archivo
                out['linea_fin'] = (
                    n_lineas_por_archivo[archivo_ini] - 1
                    if archivo_ini in n_lineas_por_archivo else ''
                )
                out['status'] = 'fallo_cruza_archivos'
        else:
            # pagina_fin + 1 no es header detectado — fallback
            # Buscar el último header del archivo
            ult_linea = (
                n_lineas_por_archivo[archivo_ini] - 1
                if archivo_ini in n_lineas_por_archivo else ''
            )
            out['linea_fin'] = ult_linea
            out['status'] = 'pagina_fin_no_en_mapa'

        resultados.append(out)

    return resultados


# ---------------------------------------------------------------------------
# Resumen y reporte
# ---------------------------------------------------------------------------

def resumir(resultados):
    """Devuelve dict con métricas globales y por tomo."""
    por_tomo = defaultdict(lambda: Counter())
    total = Counter()
    for r in resultados:
        por_tomo[r['tomo']][r['status']] += 1
        por_tomo[r['tomo']]['total'] += 1
        total[r['status']] += 1
        total['total'] += 1
    return total, dict(por_tomo)


# ---------------------------------------------------------------------------
# Procesamiento principal
# ---------------------------------------------------------------------------

def procesar(ruta_catalogo, ruta_mapa, carpeta_corpus, salida_csv, ruta_secciones_indices=None):
    salida_csv_path = Path(salida_csv)
    log_path = salida_csv_path.with_name(salida_csv_path.stem + '_log.txt')
    log_lines = []

    def emit(s=""):
        print(s)
        log_lines.append(s)

    emit(f"Catálogo: {ruta_catalogo}")
    emit(f"Mapa:     {ruta_mapa}")
    emit(f"Corpus:   {carpeta_corpus or '(no provisto)'}")
    emit(f"Secciones índices: {ruta_secciones_indices or '(no provisto)'}")
    emit()

    catalogo = cargar_catalogo(ruta_catalogo)
    emit(f"Filas en catálogo: {len(catalogo)}")

    mapa_pagina, mapa_por_archivo, duplicados_resueltos = cargar_mapa(ruta_mapa)
    emit(f"Páginas únicas en mapa: {len(mapa_pagina)}")
    if duplicados_resueltos:
        emit(f"Duplicados (tomo,pagina) resueltos: {len(duplicados_resueltos)}")
        for d in duplicados_resueltos:
            emit(f"  Tomo {d['tomo']} pag {d['pagina']}: usado {d['elegido']}, descartado(s) {', '.join(d['descartados'])}")

    n_lineas_por_archivo = cargar_lineas_de_archivos(carpeta_corpus)
    if n_lineas_por_archivo:
        emit(f"Archivos con n_lineas: {len(n_lineas_por_archivo)}")

    indices_nombres_por_archivo = cargar_indices_nombres(ruta_secciones_indices)
    if indices_nombres_por_archivo:
        emit(f"Archivos con índice de nombres detectado: {len(indices_nombres_por_archivo)}")
    emit()

    # Cruce
    resultados = cruzar(catalogo, mapa_pagina, n_lineas_por_archivo, indices_nombres_por_archivo)

    # Resumen
    total, por_tomo = resumir(resultados)
    emit("=" * 70)
    emit("Resumen del cruce")
    emit("=" * 70)
    emit(f"Total de fallos:                 {total['total']}")
    for status in ['ok', 'ok_cortado_en_indice', 'pagina_no_en_mapa',
                   'ultimo_del_tomo', 'ultimo_del_tomo_sin_fin',
                   'pagina_fin_no_en_mapa', 'fallo_cruza_archivos']:
        n = total.get(status, 0)
        if n > 0:
            pct = 100.0 * n / total['total']
            emit(f"  {status:<28} {n:>5}  ({pct:.1f}%)")

    emit()
    emit("Por tomo:")
    emit(f"  {'tomo':>5}  {'total':>6}  {'ok':>6}  {'sin_mapa':>9}  {'ult_tomo':>9}  {'pg_fin_nm':>10}  {'cruza_arch':>11}")
    for tomo in sorted(por_tomo):
        c = por_tomo[tomo]
        emit(f"  {tomo:>5}  {c['total']:>6}  {c.get('ok', 0):>6}  "
             f"{c.get('pagina_no_en_mapa', 0):>9}  "
             f"{c.get('ultimo_del_tomo', 0) + c.get('ultimo_del_tomo_sin_fin', 0):>9}  "
             f"{c.get('pagina_fin_no_en_mapa', 0):>10}  "
             f"{c.get('fallo_cruza_archivos', 0):>11}")
    emit("=" * 70)

    # Escribir CSV principal
    columnas = ['caso_id_canonico', 'tomo', 'archivo',
                'pagina_inicio', 'pagina_fin',
                'linea_inicio', 'linea_fin',
                'nombres_indice', 'n_nombres', 'status']
    with open(salida_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(resultados)
    emit(f"\nCSV principal: {salida_csv_path}  ({len(resultados)} filas)")

    # CSV de resumen por tomo
    resumen_path = salida_csv_path.with_name(salida_csv_path.stem + '_resumen.csv')
    with open(resumen_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'tomo', 'total', 'ok', 'ok_cortado_en_indice', 'pagina_no_en_mapa',
            'ultimo_del_tomo', 'ultimo_del_tomo_sin_fin',
            'pagina_fin_no_en_mapa', 'fallo_cruza_archivos'])
        writer.writeheader()
        for tomo in sorted(por_tomo):
            c = por_tomo[tomo]
            writer.writerow({
                'tomo': tomo,
                'total': c['total'],
                'ok': c.get('ok', 0),
                'ok_cortado_en_indice': c.get('ok_cortado_en_indice', 0),
                'pagina_no_en_mapa': c.get('pagina_no_en_mapa', 0),
                'ultimo_del_tomo': c.get('ultimo_del_tomo', 0),
                'ultimo_del_tomo_sin_fin': c.get('ultimo_del_tomo_sin_fin', 0),
                'pagina_fin_no_en_mapa': c.get('pagina_fin_no_en_mapa', 0),
                'fallo_cruza_archivos': c.get('fallo_cruza_archivos', 0),
            })
    emit(f"Resumen por tomo: {resumen_path}  ({len(por_tomo)} filas)")

    # CSV de huérfanos: solo los que no tienen status='ok' ni 'ok_cortado_en_indice'
    huerfanos_path = salida_csv_path.with_name(salida_csv_path.stem + '_huerfanos.csv')
    huerfanos = [r for r in resultados if r['status'] not in ('ok', 'ok_cortado_en_indice')]
    with open(huerfanos_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(huerfanos)
    emit(f"Huérfanos (status != ok): {huerfanos_path}  ({len(huerfanos)} filas)")

    # Log a archivo
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines))
    print(f"Log: {log_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 3:
        print(__doc__)
        sys.exit(1)
    ruta_catalogo = argv[1]
    ruta_mapa = argv[2]
    carpeta_corpus = argv[3] if len(argv) >= 4 else None
    salida_csv = argv[4] if len(argv) >= 5 else 'fallos_localizados.csv'
    ruta_secciones_indices = argv[5] if len(argv) >= 6 else None
    procesar(ruta_catalogo, ruta_mapa, carpeta_corpus, salida_csv, ruta_secciones_indices)


if __name__ == '__main__':
    main(sys.argv)
