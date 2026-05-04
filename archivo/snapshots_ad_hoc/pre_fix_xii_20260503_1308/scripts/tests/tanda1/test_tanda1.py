"""
Mini-test sintético para validar Tanda 1.

Cómo correrlo (desde el repo, en Windows):
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn\\scripts\\pipeline
    python -c "import test_tanda1; test_tanda1.run_all()"

O simplemente:
    python test_tanda1.py

(El archivo test_tanda1.py debe estar en el mismo directorio que parser.py.)
"""
import sys
from pathlib import Path

# Permitir que test_tanda1.py se ejecute desde cualquier directorio,
# siempre que parser.py esté en el mismo directorio.
sys.path.insert(0, str(Path(__file__).parent))

import parser  # noqa: E402


def caso_1_fallo_unico():
    """Caso sano: 1 FALLO, 1 Vistos los autos, dispositivo claro."""
    bloque = [
        "RECURSO EXTRAORDINARIO: Procedencia.",
        "",
        "Pérez, Juan c/ ANSeS s/ jubilación",
        "",
        "FALLO DE LA CORTE SUPREMA",
        "",
        "Buenos Aires, 15 de marzo de 2018.",
        "",
        'Vistos los autos: "Pérez, Juan c/ ANSeS s/ jubilación".',
        "Considerando:",
        "1°) Que la cuestión planteada...",
        "Por ello, se hace lugar al recurso. Notifíquese.",
        "Horacio Daniel Rosatti — Carlos Fernando Rosenkrantz — Ricardo Lorenzetti.",
        "Tribunal de origen: Cámara Federal de Apelaciones.",
    ]
    nombres_indice = "Pérez, Juan c/ ANSeS s/ jubilación | ANSeS (Pérez, Juan c/)"

    pre, fallo, flags = parser.dividir_bloque_en_sub_bloques(bloque, 100, nombres_indice)
    assert flags["n_fallos_detectados"] == 1, f"esperaba 1 FALLO, hubo {flags['n_fallos_detectados']}"
    assert flags["estrategia_usada"] == "fallo_unico"
    assert flags["fallo_idx_elegido"] == 4
    assert flags["pagina_compartida"] is False
    assert flags["tiene_nota_al_pie"] is False
    assert len(pre) == 4
    assert fallo[0].strip() == "FALLO DE LA CORTE SUPREMA"

    caratula, meta_car = parser.detectar_caratula(pre, fallo, nombres_indice)
    assert caratula is not None, f"no detectó carátula. meta={meta_car}"
    # Debería ser triple match (catálogo + estructural + V1)
    # NOTA: el matching del catálogo encuentra alguno de los 2 nombres del índice,
    # no necesariamente uno específico.
    print(f"  caratula='{caratula}' confianza={meta_car.get('confianza')}")

    info_disp, meta_disp = parser.detectar_dispositivo(fallo)
    assert info_disp is not None, "no detectó Por ello"
    assert meta_disp["strategy"] == "por_ello_simple"
    print(f"  primer_por_ello={info_disp['primer_por_ello']} (relativo a fallo)")
    print("CASO 1 OK")


def caso_2_tipo_1_dos_fallos():
    """Tipo 1 con bloque mal catalogado (dos FALLOs reales). El primero es del
    caso anterior, el segundo es el real. Ambos cumplen regla C (Buenos Aires
    adyacente), así que la regla D (último candidato) debe elegir el real."""
    bloque = [
        "FALLO DE LA CORTE SUPREMA",
        "",
        "Buenos Aires, 5 de mayo de 2010.",
        "",
        "Por ello, se desestima el recurso. Notifíquese.",
        "Lorenzetti — Highton de Nolasco — Maqueda.",
        "Tribunal de origen: Cámara Civil.",
        "",
        # ── frontera ──
        "RECURSO EXTRAORDINARIO: Improcedencia.",
        "",
        "García, María c/ Provincia de Buenos Aires",
        "",
        "FALLO DE LA CORTE SUPREMA",
        "",
        "Buenos Aires, 12 de mayo de 2010.",
        "",
        'Vistos los autos: "García, María c/ Provincia de Buenos Aires".',
        "Considerando:",
        "Por ello, se hace lugar. Notifíquese.",
        "Rosatti — Rosenkrantz.",
        "Tribunal de origen: Suprema Corte de Buenos Aires.",
    ]
    nombres_indice = "García, María c/ Provincia de Buenos Aires | Provincia de Buenos Aires (García, María c/)"

    pre, fallo, flags = parser.dividir_bloque_en_sub_bloques(bloque, 200, nombres_indice)
    print(f"  fallo_idx_elegido={flags['fallo_idx_elegido']} (esperado: 12)")
    print(f"  pagina_compartida={flags['pagina_compartida']} (esperado: True)")
    assert flags["n_fallos_detectados"] == 2, f"esperaba 2 FALLOs, hubo {flags['n_fallos_detectados']}"
    assert flags["fallo_idx_elegido"] == 12, (
        f"regla D debería elegir idx=12 (último candidato), eligió {flags['fallo_idx_elegido']}"
    )
    assert flags["pagina_compartida"] is True, "debería detectar Tribunal de origen en pre_fallo"
    print("CASO 2 OK")


def caso_3_nota_al_pie():
    """Bloque con 2 FALLOs: uno real, otro en nota al pie (precedido por '(*)').
    La regla A2 debería descartar el espurio."""
    bloque = [
        "RECURSO EXTRAORDINARIO: Procedencia.",
        "",
        "García c/ Provincia",
        "",
        "FALLO DE LA CORTE SUPREMA",
        "Buenos Aires, 12 de mayo de 2010.",
        'Vistos los autos: "García c/ Provincia".',
        "Considerando: 1°) Que...",
        "Por ello, se hace lugar. Notifíquese.",
        "Lorenzetti — Highton.",
        "Tribunal de origen: Cámara Civil.",
        "",
        "(*) Sentencia que dice así:",
        "FALLO DE LA CORTE SUPREMA",
        "Buenos Aires, 1 de junio de 2005.",
        "Sentencia confirmada.",
    ]
    nombres_indice = "García c/ Provincia"

    pre, fallo, flags = parser.dividir_bloque_en_sub_bloques(bloque, 4804, nombres_indice)
    print(f"  n_fallos_detectados={flags['n_fallos_detectados']} tiene_nota_al_pie={flags['tiene_nota_al_pie']}")
    print(f"  fallo_idx_elegido={flags['fallo_idx_elegido']} estrategia={flags['estrategia_usada']}")
    assert flags["n_fallos_detectados"] == 2, f"esperaba 2 FALLOs, hubo {flags['n_fallos_detectados']}"
    assert flags["tiene_nota_al_pie"] is True, "debería detectar nota al pie"
    assert flags["fallo_idx_elegido"] == 4, f"esperaba elegir el FALLO real (idx=4), eligió {flags['fallo_idx_elegido']}"
    print("CASO 3 OK")


def caso_4_sin_fallo_con_vistos():
    """Sin marcador FALLO, pero con 'Autos y Vistos;' (V4)."""
    bloque = [
        "RECURSO DE QUEJA: Improcedencia.",
        "",
        "López c/ Pérez",
        "",
        "Buenos Aires, 1 de abril de 2015.",
        "",
        "Autos y Vistos; Considerando:",
        "1°) Que la queja es improcedente.",
        "Por ello, se desestima.",
        "Rosatti — Lorenzetti.",
    ]
    nombres_indice = "López c/ Pérez"

    pre, fallo, flags = parser.dividir_bloque_en_sub_bloques(bloque, 500, nombres_indice)
    assert flags["n_fallos_detectados"] == 0
    assert flags["estrategia_usada"] == "fallback_autos_y_vistos"
    print(f"  fallo_idx_elegido={flags['fallo_idx_elegido']} estrategia={flags['estrategia_usada']}")

    info_disp, meta_disp = parser.detectar_dispositivo(fallo)
    assert info_disp is not None, "debería detectar Por ello"
    print(f"  por_ello detectado: {meta_disp['strategy']}")
    print("CASO 4 OK")


def caso_5_extraer_caratula_de_vistos():
    """V1 puro: 'Vistos los autos:' con comilla tipográfica y wrap."""
    fallo = [
        "FALLO DE LA CORTE SUPREMA",
        "Buenos Aires, 1 de enero de 2020.",
        'Vistos los autos: \u201CSosa, María Elena c/ Provincia de Buenos Aires y',
        "otros s/ daños y perjuicios\u201D.",
        "Considerando:",
    ]
    res = parser.extraer_caratula_de_vistos(fallo)
    assert res is not None, "V1 falló en encontrar la carátula"
    assert "Sosa" in res and "Buenos Aires" in res
    print(f"  V1 capturó: '{res}'")
    print("CASO 5 OK")


def caso_6_son_equivalentes():
    """Tests de _son_equivalentes (substring containment + fallback)."""
    # Substring containment exacto
    assert parser._son_equivalentes(
        "Pérez c/ ANSeS",
        "RECURSO EXTRAORDINARIO. Pérez c/ ANSeS s/ jubilación. Considerando..."
    )
    # Caso recurso de queja: orden invertido (debería capturar por containment del corto)
    a = "Pérez c/ ANSeS"
    b = "Pérez c/ ANSeS s/ jubilación"
    assert parser._son_equivalentes(a, b), f"esperaba equivalentes: {a!r} vs {b!r}"
    # No equivalentes
    assert not parser._son_equivalentes("Juan Pérez", "María González")
    # Vacíos
    assert not parser._son_equivalentes("", "Algo")
    assert not parser._son_equivalentes("Algo", "")
    print("CASO 6 OK (son_equivalentes)")


def caso_7_split_nombres_indice():
    """Tests de _split_nombres_indice."""
    # String separado por ' | '
    res = parser._split_nombres_indice("A c/ B | B (A c/) | A c/ B s/ daños")
    assert res == ["A c/ B", "B (A c/)", "A c/ B s/ daños"], f"got {res}"
    # String simple sin separador
    res = parser._split_nombres_indice("Solo un nombre")
    assert res == ["Solo un nombre"], f"got {res}"
    # Vacío
    assert parser._split_nombres_indice("") == []
    assert parser._split_nombres_indice(None) == []
    # Lista (compatibilidad)
    assert parser._split_nombres_indice(["a", "b"]) == ["a", "b"]
    print("CASO 7 OK (split_nombres_indice)")


def caso_8_regla_c_discrimina():
    """El espurio (idx=0) tiene texto sustantivo entre FALLO y Buenos Aires
    (no cumple regla C). El real (idx=10) tiene solo paginación entre FALLO
    y Buenos Aires (sí cumple regla C). Regla C debe elegir el real."""
    bloque = [
        "FALLO DE LA CORTE SUPREMA",                 # idx 0 — espurio
        "",
        "Por ello, se desestima.",                    # texto sustantivo → no es ruido
        "Lorenzetti — Highton.",
        "Tribunal de origen: Cámara Civil.",
        "",
        "RECURSO EXTRAORDINARIO.",
        "",
        "García c/ Provincia",
        "",
        "FALLO DE LA CORTE SUPREMA",                 # idx 10 — real
        "",
        "FALLOS DE LA CORTE SUPREMA",                # header de página → ruido
        "1234",                                       # número de página → ruido
        "",
        "Buenos Aires, 12 de mayo de 2010.",
    ]
    nombres_indice = "García c/ Provincia"

    pre, fallo, flags = parser.dividir_bloque_en_sub_bloques(bloque, 300, nombres_indice)
    print(f"  fallo_idx_elegido={flags['fallo_idx_elegido']} (esperado: 10)")
    assert flags["n_fallos_detectados"] == 2
    assert flags["fallo_idx_elegido"] == 10, (
        f"regla C debería elegir idx=10 (único que cumple), eligió {flags['fallo_idx_elegido']}"
    )
    print("CASO 8 OK (regla C discrimina paginación vs texto sustantivo)")


def run_all():
    print("=" * 60)
    print("TANDA 1 — VALIDACIÓN")
    print("=" * 60)
    print()
    print("CASO 1 — FALLO único + Vistos los autos:")
    caso_1_fallo_unico()
    print()
    print("CASO 2 — Tipo 1 (2 FALLOs):")
    caso_2_tipo_1_dos_fallos()
    print()
    print("CASO 3 — FALLO en nota al pie:")
    caso_3_nota_al_pie()
    print()
    print("CASO 4 — Sin FALLO, fallback Autos y Vistos:")
    caso_4_sin_fallo_con_vistos()
    print()
    print("CASO 5 — extraer_caratula_de_vistos con wrap:")
    caso_5_extraer_caratula_de_vistos()
    print()
    print("CASO 6 — son_equivalentes:")
    caso_6_son_equivalentes()
    print()
    print("CASO 7 — split_nombres_indice:")
    caso_7_split_nombres_indice()
    print()
    print("CASO 8 — regla C discrimina paginación vs texto:")
    caso_8_regla_c_discrimina()
    print()
    print("=" * 60)
    print("TANDA 1 VALIDADA")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
