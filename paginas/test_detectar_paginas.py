#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_detectar_paginas.py

Tests sobre fixtures sintéticos basados en patrones reales observados en
los tomos 329 (2006), 343 (2021) y 348 (2024).

No requiere el corpus.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from detectar_paginas import (
    detectar_en_lineas,
    diagnosticar,
    filtrar_duplicados_consecutivos,
    filtrar_outliers,
    limpiar_detecciones,
    _es_numero,
    _norm,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lineas(*items):
    """Convierte items en líneas (cada uno con \\n al final, como readlines)."""
    return [item + "\n" for item in items]


# ---------------------------------------------------------------------------
# Tests de utilidades
# ---------------------------------------------------------------------------

def test_norm_strip_y_nbsp():
    assert _norm("  329  ") == "329"
    assert _norm("\xa0329\xa0") == "329"
    assert _norm("329\xa0") == "329"
    print("OK test_norm_strip_y_nbsp")


def test_es_numero():
    assert _es_numero("5")
    assert _es_numero("4187")
    assert _es_numero("5001")   # ahora válido (era el bug del detector)
    assert _es_numero("9999")   # límite alto
    assert not _es_numero("0")     # debajo del rango
    assert not _es_numero("10001") # sobre el rango (5 dígitos largos)
    assert not _es_numero("hola")
    assert not _es_numero("")
    assert not _es_numero("12a")
    print("OK test_es_numero")


# ---------------------------------------------------------------------------
# Patrones reales
# ---------------------------------------------------------------------------

def test_patron_A_tomo_329_pagina_impar():
    """Patrón observado en tomo 329 (impar): página, header, tomo."""
    fixture = _lineas(
        "",
        "5",
        "DE JUSTICIA DE LA NACION",
        "329",
        "FALLOS DE LA CORTE SUPREMA",
        "FEBRERO",
        "YACIMIENTOS PETROLIFEROS FISCALES S.A.",
    )
    dets = detectar_en_lineas(fixture, 329)
    assert dets == [(3, 5)], f"Esperaba [(3, 5)], salio {dets}"
    print("OK test_patron_A_tomo_329_pagina_impar")


def test_patron_B_tomo_329_pagina_par():
    """Patrón observado en tomo 329 (par): página, header, tomo, distinto texto."""
    fixture = _lineas(
        "",
        "6",
        "FALLOS DE LA CORTE SUPREMA",
        "329",
    )
    dets = detectar_en_lineas(fixture, 329)
    assert dets == [(3, 6)], f"Esperaba [(3, 6)], salio {dets}"
    print("OK test_patron_B_tomo_329_pagina_par")


def test_patron_C_tomo_pagina_sin_texto():
    """Patrón observado en 348: tomo seguido directo de página, sin texto institucional."""
    fixture = _lineas(
        "ultimo parrafo del fallo anterior.",
        "",
        "348",
        "2",
        "siguiente texto del cuerpo",
    )
    dets = detectar_en_lineas(fixture, 348)
    assert dets == [(2, 2)], f"Esperaba [(2, 2)], salio {dets}"
    print("OK test_patron_C_tomo_pagina_sin_texto")


def test_tomo_con_tilde_no_afecta():
    """En 343/348 el header dice 'NACIÓN' con tilde; el detector no
    depende del texto del header, solo del par tomo+número-cercano."""
    fixture = _lineas(
        "",
        "681",
        "DE JUSTICIA DE LA NACIÓN",
        "343",
    )
    dets = detectar_en_lineas(fixture, 343)
    assert dets == [(3, 681)], f"Esperaba [(3, 681)], salio {dets}"
    print("OK test_tomo_con_tilde_no_afecta")


def test_pagina_con_nbsp_alrededor_del_tomo():
    """Tolerar NBSP en cualquier lado de las líneas relevantes."""
    fixture = _lineas(
        "",
        "\xa0681\xa0",
        "DE JUSTICIA DE LA NACION",
        "\xa0343\xa0",
    )
    dets = detectar_en_lineas(fixture, 343)
    assert dets == [(3, 681)], f"Esperaba [(3, 681)], salio {dets}"
    print("OK test_pagina_con_nbsp_alrededor_del_tomo")


# ---------------------------------------------------------------------------
# Casos negativos: el detector no debe inventar headers
# ---------------------------------------------------------------------------

def test_negativo_tomo_solo_sin_pagina_cerca():
    """Si el número del tomo aparece como línea sola sin número plausible
    dentro de la ventana, NO contar como header.
    Caso típico: una cita de jurisprudencia mal partida en el PDF→md."""
    fixture = _lineas(
        "Vease el caso citado en Fallos:",
        "329",
        ":1234, considerando 5to.",
    )
    dets = detectar_en_lineas(fixture, 329)
    assert dets == [], f"Esperaba [], salio {dets}"
    print("OK test_negativo_tomo_solo_sin_pagina_cerca")


def test_negativo_numero_aislado_sin_tomo():
    """Una línea con un número plausible aparece sola pero sin el tomo
    en la vecindad: no es un header, no se cuenta."""
    fixture = _lineas(
        "primer parrafo",
        "12",
        "segundo parrafo",
        "tercer parrafo",
    )
    dets = detectar_en_lineas(fixture, 329)
    assert dets == [], f"Esperaba [], salio {dets}"
    print("OK test_negativo_numero_aislado_sin_tomo")


def test_negativo_tomo_distinto_no_cuenta():
    """En un archivo del tomo 329, una línea con '343' no es header.
    Cubre el caso de las preliminares editoriales con número de tomo
    de un volumen anterior."""
    fixture = _lineas(
        "",
        "5",
        "DE JUSTICIA DE LA NACION",
        "343",  # tomo distinto al del archivo
    )
    dets = detectar_en_lineas(fixture, 329)
    assert dets == [], f"Esperaba [], salio {dets}"
    print("OK test_negativo_tomo_distinto_no_cuenta")


# ---------------------------------------------------------------------------
# Comportamiento sobre múltiples páginas / orden / cercanía
# ---------------------------------------------------------------------------

def test_secuencia_de_paginas_en_orden():
    """Varios headers consecutivos: detecciones en orden de aparición."""
    fixture = _lineas(
        "5",
        "DE JUSTICIA DE LA NACION",
        "329",
        "...cuerpo del fallo...",
        "...mas cuerpo...",
        "6",
        "FALLOS DE LA CORTE SUPREMA",
        "329",
        "7",
        "DE JUSTICIA DE LA NACION",
        "329",
    )
    dets = detectar_en_lineas(fixture, 329)
    paginas = [p for _, p in dets]
    assert paginas == [5, 6, 7], f"Esperaba [5, 6, 7], salio {paginas}"
    # Verificar que también la línea_header está en orden creciente
    lineas_h = [ln for ln, _ in dets]
    assert lineas_h == sorted(lineas_h)
    print("OK test_secuencia_de_paginas_en_orden")


def test_prefiere_pagina_antes_del_tomo():
    """Cuando hay un número plausible antes del tomo (offset negativo) Y
    otro después (offset positivo), gana el de antes — refleja el patrón
    editorial real página → header → tomo."""
    fixture = _lineas(
        "",
        "5",    # offset -2: candidata antes
        "DE JUSTICIA DE LA NACION",  # offset -1: no es número
        "329",  # tomo
        "200",  # offset +1: candidata después, MÁS cercana pero del lado equivocado
    )
    dets = detectar_en_lineas(fixture, 329)
    assert len(dets) == 1
    assert dets[0][1] == 5, f"Esperaba pagina 5 (la de antes), salio {dets[0][1]}"
    print("OK test_prefiere_pagina_antes_del_tomo")


def test_usa_pagina_despues_si_no_hay_antes():
    """Si solo hay candidata después del tomo (caso del patrón C raro:
    tomo seguido directamente de página), se usa esa."""
    fixture = _lineas(
        "ultimo parrafo del fallo anterior",
        "",
        "348",  # tomo, sin número antes en la ventana
        "2",    # offset +1: única candidata
    )
    dets = detectar_en_lineas(fixture, 348)
    assert dets == [(2, 2)], f"Esperaba [(2, 2)], salio {dets}"
    print("OK test_usa_pagina_despues_si_no_hay_antes")


def test_ventana_no_alcanza_pagina_lejana():
    """Si el número plausible está demasiado lejos del tomo (fuera de
    ventana 3 atrás / 2 adelante), no se cuenta."""
    fixture = _lineas(
        "5",                          # offset -5 desde el tomo (fuera de ventana)
        "linea cuerpo 1",
        "linea cuerpo 2",
        "linea cuerpo 3",
        "linea cuerpo 4",
        "329",
    )
    dets = detectar_en_lineas(fixture, 329)
    assert dets == [], f"Esperaba [], salio {dets}"
    print("OK test_ventana_no_alcanza_pagina_lejana")


# ---------------------------------------------------------------------------
# Diagnóstico
# ---------------------------------------------------------------------------

def test_diagnosticar_archivo_perfecto():
    detecciones = [(10, 5), (20, 6), (30, 7), (40, 8)]
    diag = diagnosticar(detecciones, "test.md", 329)
    assert diag['n_headers'] == 4
    assert diag['pagina_min'] == 5
    assert diag['pagina_max'] == 8
    assert diag['monotonia_pct'] == 100.0
    assert diag['gaps_grandes'] == []
    assert diag['paginas_duplicadas'] == {}
    assert diag['anomalias'] == []
    print("OK test_diagnosticar_archivo_perfecto")


def test_diagnosticar_detecta_gap_grande():
    """Salto de más de GAP_FLAG (3) páginas se reporta."""
    detecciones = [(10, 5), (20, 6), (30, 15)]  # gap 6→15 es de 9 páginas
    diag = diagnosticar(detecciones, "test.md", 329)
    assert len(diag['gaps_grandes']) == 1
    a, b, d = diag['gaps_grandes'][0]
    assert (a, b, d) == (6, 15, 9)
    assert any('gap' in s for s in diag['anomalias'])
    print("OK test_diagnosticar_detecta_gap_grande")


def test_diagnosticar_no_reporta_gap_de_1():
    """Salto de 1 página (típica página en blanco) NO se reporta como anomalía."""
    detecciones = [(10, 5), (20, 7)]  # gap de 1 (5→7, salto 2 — está bajo el umbral 3)
    diag = diagnosticar(detecciones, "test.md", 329)
    assert diag['gaps_grandes'] == []
    assert diag['anomalias'] == []
    print("OK test_diagnosticar_no_reporta_gap_de_1")


def test_diagnosticar_detecta_pagina_duplicada():
    detecciones = [(10, 5), (20, 5), (30, 6)]
    diag = diagnosticar(detecciones, "test.md", 329)
    assert diag['paginas_duplicadas'] == {5: 2}
    assert any('duplicada' in s for s in diag['anomalias'])
    print("OK test_diagnosticar_detecta_pagina_duplicada")


def test_diagnosticar_detecta_fuera_de_orden():
    detecciones = [(10, 100), (20, 50), (30, 200)]  # 100→50 está fuera de orden
    diag = diagnosticar(detecciones, "test.md", 329)
    assert len(diag['fuera_de_orden']) == 1
    assert diag['monotonia_pct'] == 50.0
    assert any('fuera de orden' in s for s in diag['anomalias'])
    print("OK test_diagnosticar_detecta_fuera_de_orden")


def test_diagnosticar_archivo_sin_detecciones():
    diag = diagnosticar([], "test.md", 329)
    assert diag['n_headers'] == 0
    assert diag['pagina_min'] is None
    assert diag['anomalias'] == ['sin headers detectados']
    print("OK test_diagnosticar_archivo_sin_detecciones")


# ---------------------------------------------------------------------------
# Post-procesamiento: filtrar duplicados consecutivos
# ---------------------------------------------------------------------------

def test_filtrar_duplicado_consecutivo_misma_pagina():
    """Caso real visto en tomo 329: misma página detectada dos veces a 2 líneas."""
    detecciones = [
        (12224, 327),
        (12259, 328),
        (12287, 329),  # legítima
        (12289, 329),  # duplicado a 2 líneas
        (12326, 330),
    ]
    out, n = filtrar_duplicados_consecutivos(detecciones)
    assert n == 1
    assert out == [(12224, 327), (12259, 328), (12287, 329), (12326, 330)]
    print("OK test_filtrar_duplicado_consecutivo_misma_pagina")


def test_filtrar_no_toca_duplicado_lejano():
    """Si la página se repite pero a > umbral líneas, no es duplicado del header
    sino otra cosa: no se filtra."""
    detecciones = [
        (100, 50),
        (200, 50),  # mismo nº pero 100 líneas después
    ]
    out, n = filtrar_duplicados_consecutivos(detecciones)
    assert n == 0
    assert out == detecciones
    print("OK test_filtrar_no_toca_duplicado_lejano")


def test_filtrar_no_toca_paginas_distintas():
    """Si las páginas son distintas, no se filtra aunque estén cerca."""
    detecciones = [
        (100, 50),
        (102, 51),  # cercana pero distinta página
    ]
    out, n = filtrar_duplicados_consecutivos(detecciones)
    assert n == 0
    assert out == detecciones
    print("OK test_filtrar_no_toca_paginas_distintas")


def test_filtrar_duplicados_lista_vacia():
    out, n = filtrar_duplicados_consecutivos([])
    assert out == []
    assert n == 0
    print("OK test_filtrar_duplicados_lista_vacia")


# ---------------------------------------------------------------------------
# Post-procesamiento: filtrar outliers
# ---------------------------------------------------------------------------

def test_filtrar_outlier_descendente():
    """Caso real visto en tomo 338.2: 1591, 338, 1593 → 338 es outlier."""
    detecciones = [
        (35117, 1590),
        (35123, 1591),
        (35125, 338),   # outlier
        (35131, 1593),
        (35145, 1594),
    ]
    out, n = filtrar_outliers(detecciones)
    assert n == 1
    paginas = [p for _, p in out]
    assert paginas == [1590, 1591, 1593, 1594]
    print("OK test_filtrar_outlier_descendente")


def test_filtrar_outlier_ascendente():
    """Caso real visto en tomo 339.1: 19, 339, 21 → 339 es outlier (rebote ascendente)."""
    detecciones = [
        (608, 18),
        (622, 19),
        (624, 339),  # outlier ascendente
        (630, 21),
        (662, 22),
    ]
    out, n = filtrar_outliers(detecciones)
    assert n == 1
    paginas = [p for _, p in out]
    assert paginas == [18, 19, 21, 22]
    print("OK test_filtrar_outlier_ascendente")


def test_no_filtra_salto_pequeno():
    """Salto de 1-2 páginas (página en blanco) NO es outlier."""
    detecciones = [
        (10, 5),
        (20, 7),  # salto chico, página en blanco probable
        (30, 8),
    ]
    out, n = filtrar_outliers(detecciones)
    assert n == 0
    assert out == detecciones
    print("OK test_no_filtra_salto_pequeno")


def test_no_filtra_secuencia_normal():
    """Secuencia normal monótona creciente: nada se filtra."""
    detecciones = [(10, i) for i in range(1, 20)]
    out, n = filtrar_outliers(detecciones)
    assert n == 0
    assert len(out) == len(detecciones)
    print("OK test_no_filtra_secuencia_normal")


def test_filtrar_outlier_no_toca_extremos():
    """La función NO filtra primera ni última (no tienen ambas vecinas)."""
    detecciones = [
        (10, 999),  # primera, no se evalúa
        (20, 5),
        (30, 6),
        (40, 7),
        (50, 999),  # última, no se evalúa
    ]
    out, n = filtrar_outliers(detecciones)
    assert n == 0
    assert out == detecciones
    print("OK test_filtrar_outlier_no_toca_extremos")


def test_filtrar_outliers_lista_corta():
    """Listas con < 3 elementos no se procesan."""
    out, n = filtrar_outliers([(10, 5), (20, 6)])
    assert n == 0
    print("OK test_filtrar_outliers_lista_corta")


def test_limpiar_aplica_ambas_reglas():
    """limpiar_detecciones aplica primero duplicados, después outliers."""
    detecciones = [
        (100, 327),
        (110, 328),
        (120, 329),
        (122, 329),    # duplicado de la anterior
        (130, 50),     # outlier descendente respecto a 329 y la siguiente
        (140, 330),
        (150, 331),
    ]
    out, conteos = limpiar_detecciones(detecciones)
    assert conteos['duplicados_consecutivos'] == 1
    assert conteos['outliers'] == 1
    paginas = [p for _, p in out]
    assert paginas == [327, 328, 329, 330, 331]
    print("OK test_limpiar_aplica_ambas_reglas")




if __name__ == '__main__':
    tests = [
        test_norm_strip_y_nbsp,
        test_es_numero,
        test_patron_A_tomo_329_pagina_impar,
        test_patron_B_tomo_329_pagina_par,
        test_patron_C_tomo_pagina_sin_texto,
        test_tomo_con_tilde_no_afecta,
        test_pagina_con_nbsp_alrededor_del_tomo,
        test_negativo_tomo_solo_sin_pagina_cerca,
        test_negativo_numero_aislado_sin_tomo,
        test_negativo_tomo_distinto_no_cuenta,
        test_secuencia_de_paginas_en_orden,
        test_prefiere_pagina_antes_del_tomo,
        test_usa_pagina_despues_si_no_hay_antes,
        test_ventana_no_alcanza_pagina_lejana,
        test_diagnosticar_archivo_perfecto,
        test_diagnosticar_detecta_gap_grande,
        test_diagnosticar_no_reporta_gap_de_1,
        test_diagnosticar_detecta_pagina_duplicada,
        test_diagnosticar_detecta_fuera_de_orden,
        test_diagnosticar_archivo_sin_detecciones,
        test_filtrar_duplicado_consecutivo_misma_pagina,
        test_filtrar_no_toca_duplicado_lejano,
        test_filtrar_no_toca_paginas_distintas,
        test_filtrar_duplicados_lista_vacia,
        test_filtrar_outlier_descendente,
        test_filtrar_outlier_ascendente,
        test_no_filtra_salto_pequeno,
        test_no_filtra_secuencia_normal,
        test_filtrar_outlier_no_toca_extremos,
        test_filtrar_outliers_lista_corta,
        test_limpiar_aplica_ambas_reglas,
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
