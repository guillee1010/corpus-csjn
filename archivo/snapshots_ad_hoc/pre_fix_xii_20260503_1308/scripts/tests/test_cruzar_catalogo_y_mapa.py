#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cruzar_catalogo_y_mapa.py

Tests sintéticos del cruce. No requiere los CSVs reales.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from cruzar_catalogo_y_mapa import cruzar, resumir


def _cat_row(tomo, pg_ini, pg_fin, caso_id="caso", nombres="X", n_nombres=1, n_arch=1):
    """Helper: arma una fila de catálogo."""
    return {
        'tomo': tomo,
        'pagina_inicio': pg_ini,
        'pagina_fin': pg_fin,
        'caso_id_canonico': caso_id,
        'nombres_indice': nombres,
        'n_nombres': n_nombres,
        'n_archivos_indice': n_arch,
    }


# ---------------------------------------------------------------------------
# Casos básicos
# ---------------------------------------------------------------------------

def test_cruce_ok_simple():
    """Caso típico: dos fallos consecutivos en el mismo archivo."""
    cat = [
        _cat_row(329, 5, 8, "329_p5"),
        _cat_row(329, 9, 11, "329_p9"),
    ]
    mapa = {
        (329, 5): ('a.md', 39),
        (329, 9): ('a.md', 175),
        (329, 12): ('a.md', 244),  # header de la página siguiente al fallo 9-11
    }
    n_lineas = {'a.md': 1000}
    res = cruzar(cat, mapa, n_lineas)
    assert len(res) == 2
    # Primer fallo: termina antes del header de página 9 (no de 8+1=9, sí)
    # pagina_fin=8, pagina_fin+1=9, header en línea 175 → linea_fin=174
    assert res[0]['linea_inicio'] == 39
    assert res[0]['linea_fin'] == 174
    assert res[0]['status'] == 'ok'
    assert res[0]['archivo'] == 'a.md'
    # Segundo: pagina_fin=11, header de 12 en línea 244 → linea_fin=243
    assert res[1]['linea_inicio'] == 175
    assert res[1]['linea_fin'] == 243
    assert res[1]['status'] == 'ok'
    print("OK test_cruce_ok_simple")


def test_pagina_no_en_mapa():
    """Fallo del catálogo cuya pagina_inicio no está en el mapa."""
    cat = [_cat_row(329, 5001, 5004, "329_p5001")]
    mapa = {}  # vacío
    res = cruzar(cat, mapa, {})
    assert len(res) == 1
    assert res[0]['status'] == 'pagina_no_en_mapa'
    assert res[0]['archivo'] == ''
    assert res[0]['linea_inicio'] == ''
    assert res[0]['linea_fin'] == ''
    print("OK test_pagina_no_en_mapa")


def test_ultimo_del_tomo_con_corpus():
    """Último fallo del tomo (pagina_fin None): linea_fin = última del archivo."""
    cat = [_cat_row(329, 4900, None, "329_p4900")]
    mapa = {(329, 4900): ('z.md', 50000)}
    n_lineas = {'z.md': 60000}
    res = cruzar(cat, mapa, n_lineas)
    assert res[0]['status'] == 'ultimo_del_tomo'
    assert res[0]['linea_inicio'] == 50000
    assert res[0]['linea_fin'] == 59999
    print("OK test_ultimo_del_tomo_con_corpus")


def test_ultimo_del_tomo_sin_corpus():
    """Último fallo pero sin corpus disponible: linea_fin queda vacía."""
    cat = [_cat_row(329, 4900, None, "329_p4900")]
    mapa = {(329, 4900): ('z.md', 50000)}
    res = cruzar(cat, mapa, {})  # n_lineas vacío
    assert res[0]['status'] == 'ultimo_del_tomo_sin_fin'
    assert res[0]['linea_inicio'] == 50000
    assert res[0]['linea_fin'] == ''
    print("OK test_ultimo_del_tomo_sin_corpus")


def test_pagina_fin_no_en_mapa():
    """pagina_fin+1 no aparece como header (caso de OCR sucio o gap)."""
    cat = [_cat_row(329, 100, 105, "329_p100")]
    mapa = {(329, 100): ('a.md', 5000)}
    # No hay header de página 106, ni siguiente
    n_lineas = {'a.md': 7000}
    res = cruzar(cat, mapa, n_lineas)
    assert res[0]['status'] == 'pagina_fin_no_en_mapa'
    assert res[0]['linea_fin'] == 6999  # última línea del archivo como fallback
    print("OK test_pagina_fin_no_en_mapa")


def test_fallo_cruza_archivos():
    """Fallo cuya pagina_inicio está en un archivo y pagina_fin+1 en otro."""
    cat = [_cat_row(343, 1455, 1456, "343_p1455")]
    mapa = {
        (343, 1455): ('343-2.md', 29900),
        (343, 1457): ('343-3.md', 60),  # siguiente fallo está en otro archivo
    }
    n_lineas = {'343-2.md': 30000, '343-3.md': 25000}
    res = cruzar(cat, mapa, n_lineas)
    assert res[0]['status'] == 'fallo_cruza_archivos'
    assert res[0]['archivo'] == '343-2.md'
    assert res[0]['linea_inicio'] == 29900
    # Termina con la última línea del archivo de inicio
    assert res[0]['linea_fin'] == 29999
    print("OK test_fallo_cruza_archivos")


# ---------------------------------------------------------------------------
# Resumir
# ---------------------------------------------------------------------------

def test_resumir_estructura():
    resultados = [
        {'tomo': 329, 'status': 'ok'},
        {'tomo': 329, 'status': 'ok'},
        {'tomo': 329, 'status': 'pagina_no_en_mapa'},
        {'tomo': 330, 'status': 'ok'},
        {'tomo': 330, 'status': 'ultimo_del_tomo'},
    ]
    total, por_tomo = resumir(resultados)
    assert total['total'] == 5
    assert total['ok'] == 3
    assert total['pagina_no_en_mapa'] == 1
    assert total['ultimo_del_tomo'] == 1
    assert por_tomo[329]['total'] == 3
    assert por_tomo[329]['ok'] == 2
    assert por_tomo[330]['total'] == 2
    print("OK test_resumir_estructura")


# ---------------------------------------------------------------------------
# Casos compuestos
# ---------------------------------------------------------------------------

def test_pipeline_mixto():
    """Catálogo con fallos en varios estados, todos en el mismo run."""
    cat = [
        _cat_row(329, 5, 8, "329_p5"),               # ok
        _cat_row(329, 9, None, "329_p9"),            # último del tomo
        _cat_row(329, 5001, 5004, "329_p5001"),      # huérfano
    ]
    mapa = {
        (329, 5): ('a.md', 39),
        (329, 9): ('a.md', 175),
    }
    n_lineas = {'a.md': 1000}
    res = cruzar(cat, mapa, n_lineas)
    assert res[0]['status'] == 'ok'
    assert res[1]['status'] == 'ultimo_del_tomo'
    assert res[2]['status'] == 'pagina_no_en_mapa'
    # nombres_indice se preserva
    assert res[0]['nombres_indice'] == 'X'
    print("OK test_pipeline_mixto")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    tests = [
        test_cruce_ok_simple,
        test_pagina_no_en_mapa,
        test_ultimo_del_tomo_con_corpus,
        test_ultimo_del_tomo_sin_corpus,
        test_pagina_fin_no_en_mapa,
        test_fallo_cruza_archivos,
        test_resumir_estructura,
        test_pipeline_mixto,
    ]
    fallidos = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"FALLO {t.__name__}: {e}")
            fallidos += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            fallidos += 1
    print(f"\n{len(tests) - fallidos}/{len(tests)} tests pasaron")
    sys.exit(0 if fallidos == 0 else 1)
