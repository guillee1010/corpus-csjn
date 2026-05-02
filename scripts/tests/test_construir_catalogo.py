#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_construir_catalogo.py

Tests unitarios sobre fragmentos hardcodeados, basados en patrones reales
observados en los tomos 329 (2006), 334 (2011) y 348 (2024).

No requiere el corpus. Las tres décadas se cubren con fixtures.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from construir_catalogo import (
    parsear_indice_nombres,
    detectar_secciones,
    encontrar_indice_nombres,
    construir_filas_catalogo,
    limpiar_caratula,
    extraer_tomo_de_filename,
)


def test_filename_a_tomo():
    assert extraer_tomo_de_filename("LibroVol329.md") == 329
    assert extraer_tomo_de_filename("LibroVol329.1.md") == 329
    assert extraer_tomo_de_filename("LibroVol329_1.md") == 329
    assert extraer_tomo_de_filename("LibroVol329-1.md") == 329
    assert extraer_tomo_de_filename("LibroVol349-1.md") == 349
    assert extraer_tomo_de_filename("otracosa.md") is None
    print("OK test_filename_a_tomo")


def test_limpiar_caratula():
    # NBSP → espacio
    assert limpiar_caratula("Hola\xa0mundo") == "Hola mundo"
    # Guion de continuación de palabra
    assert limpiar_caratula("Fede- ral de Ingresos") == "Federal de Ingresos"
    # Espacios múltiples
    assert limpiar_caratula("Hola    mundo") == "Hola mundo"
    # Combinación
    assert limpiar_caratula("Im-  puesto\xa0al") == "Impuesto al"
    print("OK test_limpiar_caratula")


def test_entrada_simple_tomo_viejo():
    """Tomo 329: una página, formato `: p. NNN.` con punto final."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Arbumasa S.A. c/ Provincia del Chubut: p. 537.",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 2)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "Arbumasa S.A. c/ Provincia del Chubut"
    assert paginas == [537]
    print("OK test_entrada_simple_tomo_viejo")


def test_entrada_simple_tomo_nuevo_sin_punto_final():
    """Tomo 348: formato `: p. NNN` SIN punto final."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Austral Construcciones S.A. s/ quiebra s/",
        "incidente de competencia: p. 1032",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 3)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "Austral Construcciones S.A. s/ quiebra s/ incidente de competencia"
    assert paginas == [1032]
    print("OK test_entrada_simple_tomo_nuevo_sin_punto_final")


def test_entrada_multilinea_con_guion():
    """Tomo 329: entrada de varias líneas con guión de continuación de palabra."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Bagalio, Hugo Jorge y otros c/ Caja de Retiros,",
        "Jubilaciones y Pensiones de la Policía Fede-",
        "ral: p. 182.",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 4)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "Bagalio, Hugo Jorge y otros c/ Caja de Retiros, Jubilaciones y Pensiones de la Policía Federal"
    assert paginas == [182]
    print("OK test_entrada_multilinea_con_guion")


def test_paginas_multiples_separador_coma():
    """Tomo 329: `: ps. 243, 244, 297.` — separador coma."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Astíz, Alfredo y otros: ps. 243, 244, 297.",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 2)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "Astíz, Alfredo y otros"
    assert paginas == [243, 244, 297]
    print("OK test_paginas_multiples_separador_coma")


def test_paginas_multiples_separador_y():
    """Tomo 348: `: ps. 1316 y 1334` — separador 'y'."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Asociación Civil por la Igualdad y la Justicia c/",
        "EN - AFIP s/ amparo ley 16.986: ps. 1316 ",
        "y 1334",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 4)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "Asociación Civil por la Igualdad y la Justicia c/ EN - AFIP s/ amparo ley 16.986"
    assert paginas == [1316, 1334]
    print("OK test_paginas_multiples_separador_y")


def test_pagina_con_nbsp():
    """Tomo 334: `: p.\\xa0681.` — NBSP entre 'p.' y el número."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Direct TV Argentina S.A.: p.\xa0681.",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 2)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "Direct TV Argentina S.A."
    assert paginas == [681]
    print("OK test_pagina_con_nbsp")


def test_entrada_cruzada_estilo_parentesis():
    """Tomo 329: entrada cruzada con `c/` dentro de paréntesis."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "A.F.I.P. (Aguas de la Costa S.A. c/): p. 4187.",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 2)
    assert len(entradas) == 1
    caratula, paginas = entradas[0]
    assert caratula == "A.F.I.P. (Aguas de la Costa S.A. c/)"
    assert paginas == [4187]
    print("OK test_entrada_cruzada_estilo_parentesis")


def test_filtros_cabecera_alfa_y_romanos():
    """Las cabeceras alfabéticas y romanos en paréntesis no deben generar entradas."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "B",  # cabecera alfabética
        "NOMBRES DE LAS PARTES",  # cabecera de página
        "(VIII)",  # romano en paréntesis (tomo 348)
        "Y",  # cabecera alfabética
        "YPF SA c/ GASNEA SA s/ recurso directo",
        "organismo externo: p. 1546",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 7)
    assert len(entradas) == 1, f"Esperaba 1 entrada, salió {len(entradas)}"
    caratula, paginas = entradas[0]
    assert caratula == "YPF SA c/ GASNEA SA s/ recurso directo organismo externo"
    assert paginas == [1546]
    print("OK test_filtros_cabecera_alfa_y_romanos")


def test_anclas_a_mitad_de_linea():
    """Cuando dos entradas se concatenan en una línea (PDF→md sucio), el
    parser debe cortar por ancla, no por línea."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        # Las dos entradas siguientes están concatenadas en una sola línea
        "Argencard S.A. c/ Provincia del Chubut y otro: p. 755. Arriola, Mónica Beatriz (Apecechea, Jorge Ramón c/): p. 988.",
    ]
    entradas = parsear_indice_nombres(fixture, 1, 2)
    assert len(entradas) == 2, f"Esperaba 2 entradas, salió {len(entradas)}"
    assert entradas[0][0] == "Argencard S.A. c/ Provincia del Chubut y otro"
    assert entradas[0][1] == [755]
    assert entradas[1][0] == "Arriola, Mónica Beatriz (Apecechea, Jorge Ramón c/)"
    assert entradas[1][1] == [988]
    print("OK test_anclas_a_mitad_de_linea")


def test_construir_filas_dedupe_por_pagina():
    """Cuando dos entradas distintas comparten página, deben colapsar a una
    sola fila del catálogo con ambos nombres en nombres_indice."""
    entradas_por_archivo = {
        (329, "LibroVol329.1.md"): [
            ("Aguas de la Costa S.A. c/ AFIP", [4187]),
            ("A.F.I.P. (Aguas de la Costa S.A. c/)", [4187]),
        ],
    }
    filas = construir_filas_catalogo(entradas_por_archivo)
    assert len(filas) == 1
    f = filas[0]
    assert f['tomo'] == 329
    assert f['pagina_inicio'] == 4187
    assert f['n_nombres'] == 2
    # Conservar orden de aparición
    assert f['nombres_indice'] == "Aguas de la Costa S.A. c/ AFIP | A.F.I.P. (Aguas de la Costa S.A. c/)"
    assert f['n_archivos_indice'] == 1
    print("OK test_construir_filas_dedupe_por_pagina")


def test_construir_filas_pagina_fin_global_por_tomo():
    """pagina_fin = página del siguiente fallo del mismo tomo - 1.
    Última del tomo: pagina_fin queda vacía."""
    entradas_por_archivo = {
        (329, "archivoA.md"): [("Caso A", [10])],
        (329, "archivoB.md"): [("Caso B", [50]), ("Caso C", [100])],
    }
    filas = construir_filas_catalogo(entradas_por_archivo)
    assert len(filas) == 3
    # Ordenadas por (tomo, pagina_inicio)
    assert filas[0]['pagina_inicio'] == 10 and filas[0]['pagina_fin'] == 49
    assert filas[1]['pagina_inicio'] == 50 and filas[1]['pagina_fin'] == 99
    assert filas[2]['pagina_inicio'] == 100 and filas[2]['pagina_fin'] == ''
    print("OK test_construir_filas_pagina_fin_global_por_tomo")


def test_construir_filas_paginas_multiples():
    """Una entrada con páginas múltiples genera una fila por página."""
    entradas_por_archivo = {
        (348, "LibroVol348-1.md"): [
            ("Caso AAA", [1316, 1334]),
            ("Caso BBB", [1500]),
        ],
    }
    filas = construir_filas_catalogo(entradas_por_archivo)
    assert len(filas) == 3
    assert filas[0]['pagina_inicio'] == 1316
    assert filas[0]['nombres_indice'] == "Caso AAA"
    assert filas[1]['pagina_inicio'] == 1334
    assert filas[1]['nombres_indice'] == "Caso AAA"
    assert filas[2]['pagina_inicio'] == 1500
    assert filas[2]['nombres_indice'] == "Caso BBB"
    print("OK test_construir_filas_paginas_multiples")


def test_n_archivos_indice_consolidado():
    """Tomos modernos (343+) tienen el mismo índice repetido en cada volumen.
    n_archivos_indice debe reflejar cuántos archivos contribuyeron la misma
    entrada."""
    # Simular tomo 343 con tres volúmenes que listan la misma entrada
    entradas_por_archivo = {
        (343, "LibroVol343-1.md"): [("Mismo fallo c/ Otro", [500])],
        (343, "LibroVol343-2.md"): [("Mismo fallo c/ Otro", [500])],
        (343, "LibroVol343-3.md"): [("Mismo fallo c/ Otro", [500])],
    }
    filas = construir_filas_catalogo(entradas_por_archivo)
    assert len(filas) == 1
    assert filas[0]['n_archivos_indice'] == 3
    assert filas[0]['n_nombres'] == 1
    print("OK test_n_archivos_indice_consolidado")


def test_detectar_secciones_colapsa_repetidas():
    """Las cabeceras de página repetidas dentro de una sección no deben
    contar como secciones nuevas."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Caso uno: p. 5.",
        "INDICE ALFABETICO POR MATERIAS",
        "blabla",
        "INDICE ALFABETICO POR MATERIAS",  # cabecera de página repetida
        "blabla",
        "INDICE DE LEGISLACION",
        "INDICE DE LEGISLACION",  # cabecera repetida
        "INDICE DE LEGISLACION (*)",  # variante
        "INDICE GENERAL",
    ]
    secciones = detectar_secciones(fixture)
    tipos = [s[0] for s in secciones]
    # Esperamos: nombres, materias (una sola), legislacion (una sola), general
    assert tipos == ['nombres', 'materias', 'legislacion', 'general'], \
        f"Tipos detectados: {tipos}"
    print("OK test_detectar_secciones_colapsa_repetidas")


def test_estructura_tomo_348_sin_intermedias():
    """Tomo 348: nombres → general directo, sin materias ni legislación."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Caso uno: p. 5",
        "INDICE GENERAL",
    ]
    secciones = detectar_secciones(fixture)
    tipos = [s[0] for s in secciones]
    assert tipos == ['nombres', 'general']
    rango = encontrar_indice_nombres(secciones)
    assert rango == (1, 2)  # nombres ocupa líneas 1-2 (header + entrada)
    print("OK test_estructura_tomo_348_sin_intermedias")


def test_no_confundir_indice_general_minusculas():
    """`indice por los nombres de las partes ........` (minúsculas, puntos
    suspensivos) NO es un header de sección. Es una entrada del INDICE
    GENERAL al final del libro."""
    fixture = [
        "INDICE POR LOS NOMBRES DE LAS PARTES",
        "Caso uno: p. 5",
        "INDICE GENERAL",
        "Indice por los nombres de las partes ......................................",
    ]
    secciones = detectar_secciones(fixture)
    tipos = [s[0] for s in secciones]
    # La línea minúsculas no debe contar como sección nombres
    assert tipos == ['nombres', 'general'], f"Tipos: {tipos}"
    print("OK test_no_confundir_indice_general_minusculas")


def test_pagina_fin_inferida_a_traves_de_archivos():
    """Si un tomo está en varios archivos, pagina_fin se calcula globalmente
    para que el último fallo de un archivo se cierre contra el primero del
    siguiente."""
    entradas_por_archivo = {
        (329, "LibroVol329.1.md"): [
            ("Caso primer archivo", [10]),
            ("Caso último primer archivo", [100]),
        ],
        (329, "LibroVol329.2.md"): [
            ("Caso primero segundo archivo", [105]),
            ("Caso último segundo archivo", [200]),
        ],
    }
    filas = construir_filas_catalogo(entradas_por_archivo)
    # Buscar el caso de página 100 (último del primer archivo)
    f100 = next(f for f in filas if f['pagina_inicio'] == 100)
    # Su pagina_fin debería ser 104, no '' (porque el siguiente fallo del tomo
    # está en el otro archivo, página 105)
    assert f100['pagina_fin'] == 104, f"pagina_fin de 100: {f100['pagina_fin']}"
    # El último del tomo (página 200) sí queda con pagina_fin vacía
    f200 = next(f for f in filas if f['pagina_inicio'] == 200)
    assert f200['pagina_fin'] == ''
    print("OK test_pagina_fin_inferida_a_traves_de_archivos")


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    tests = [
        test_filename_a_tomo,
        test_limpiar_caratula,
        test_entrada_simple_tomo_viejo,
        test_entrada_simple_tomo_nuevo_sin_punto_final,
        test_entrada_multilinea_con_guion,
        test_paginas_multiples_separador_coma,
        test_paginas_multiples_separador_y,
        test_pagina_con_nbsp,
        test_entrada_cruzada_estilo_parentesis,
        test_filtros_cabecera_alfa_y_romanos,
        test_anclas_a_mitad_de_linea,
        test_construir_filas_dedupe_por_pagina,
        test_construir_filas_pagina_fin_global_por_tomo,
        test_construir_filas_paginas_multiples,
        test_n_archivos_indice_consolidado,
        test_detectar_secciones_colapsa_repetidas,
        test_estructura_tomo_348_sin_intermedias,
        test_no_confundir_indice_general_minusculas,
        test_pagina_fin_inferida_a_traves_de_archivos,
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
