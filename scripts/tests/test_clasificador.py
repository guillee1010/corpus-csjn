"""
Tests de la función `clasificar_tipo_voto` sobre los 8 ejemplos del
ground truth definidos en el prompt.

Asserts sobre `tipo_voto_sep` (los 8) y sobre `fragmenta_ratio` (los 8).
Para `punto_divergencia` se chequea coherencia general donde el ground
truth lo especifica (Ejemplos 5 y 6: considerando 4 y 3 respectivamente).
"""

from csjnv11 import clasificar_tipo_voto


# ── Textos del ground truth ──────────────────────────────────────────────────

EJ1_HIGHTON_280 = (
    "VOTO DE LAS SEÑORA VICEPRESIDENTA DOCTORA DOÑA ELENA I. HIGHTON DE "
    "NOLASCO Y DE LA SEÑORA MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY "
    "Considerando: Que el recurso extraordinario, cuya denegación originó "
    "esta queja, es inadmisible (art. 280 del Código Procesal Civil y "
    "Comercial de la Nación). Por ello, y oído el señor Procurador General "
    "se desestima la queja. Declárase perdido el depósito de fs. 79. "
    "Notifíquese y, previa devolución de los autos principales, archívese. "
    "ELENA I. HIGHTON DE NOLASCO — CARMEN M. ARGIBAY."
)

EJ2_ARGIBAY_280 = (
    "VOTO DE LA SEÑORA MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY "
    "Considerando: Que el recurso extraordinario, concedido a fs. 79/80 "
    "vta. es inadmisible (art. 280 del Código Procesal Civil y Comercial "
    "de la Nación). Por ello, oído el señor Procurador Fiscal, se lo "
    "declara mal concedido. Hágase saber y devuélvase. CARMEN M. ARGIBAY."
)

EJ3_FAYT_VERBITSKY = (
    "VOTO DEL SEÑOR MINISTRO DOCTOR DON CARLOS S. FAYT Considerando: Que "
    "al caso resulta aplicable, en lo pertinente, lo resuelto por el "
    "Tribunal en la causa \"Verbitsky\" (Fallos: 328:1146, disidencia parcial "
    "del juez Fayt) a cuyos fundamentos y conclusiones corresponde remitir "
    "en razón de brevedad. Por ello, en concordancia con lo dictaminado "
    "por el señor Procurador Fiscal, se hace lugar a la queja, se declara "
    "procedente el recurso extraordinario y se deja sin efecto la sentencia "
    "apelada. Vuelvan los autos al tribunal de origen a fin de que, por "
    "quien corresponda, se dicte un nuevo pronunciamiento con arreglo al "
    "presente. Devuélvase el depósito de fs. 1 en los términos en que se "
    "ha solicitado a fs. 91. Notifíquese y remítase. CARLOS S. FAYT."
)

EJ4_LORENZETTI_PROCURADOR = (
    "VOTO DE LOS SEÑORES MINISTROS DOCTORES DON RICARDO LUIS LORENZETTI "
    "Y DOÑA CARMEN M. ARGIBAY Considerando: 1°) Que las cuestiones "
    "debatidas, la forma en que fueron resultas por el juez a quo y los "
    "agravios desarrollados por la Administración Nacional de Medicamentos, "
    "Alimentos y Tecnología Médica en su recurso extraordinario, han sido "
    "reseñados apropiadamente en el dictamen del señor Procurador Fiscal "
    "subrogante (acápites I, II y III), al que cabe remitirse a fin de "
    "evitar repeticiones innecesarias. 2°) Que en lo atinente a la "
    "interpretación del art. 3° de la ley 16.463, resultan aplicables los "
    "argumentos expuestos, del 5 de septiembre de 2006, en la causa "
    "\"Distribuidora Norte S.R.L. y Piacenza\" (Fallos: 329:3660), dada la "
    "sustancial analogía que ella guarda con el caso sub examine."
)

EJ5_LORENZETTI_EXCLUSION = (
    "VOTO DEL SEÑOR MINISTRO DOCTOR DON RICARDO LUIS LORENZETTI "
    "Considerando: Que el infrascripto coincide con el del voto de la "
    "mayoría con exclusión del considerando 4°, el que se redacta en los "
    "siguientes términos. 4°) Que este Tribunal ha decidido que la "
    "indemnización por la privación de la libertad durante el proceso no "
    "debe ser reconocida automáticamente a consecuencia de la absolución "
    "sino sólo cuando el auto de prisión preventiva se revela como "
    "incuestionablemente infundado o arbitrario, mas no cuando elementos "
    "objetivos hubieran llevado a los juzgadores al convencimiento — "
    "relativo, obviamente, dada la etapa del proceso en que aquél se dicta— "
    "de que medió un delito y de que existía probabilidad cierta de que el "
    "imputado era su autor (Fallos: ...)"
)

EJ6_ARGIBAY_HASTA_2 = (
    "VOTO DE LA SEÑORA MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY "
    "Considerando: Que la infrascripta coincide con los considerandos 1° "
    "y 2° del voto de la mayoría. 3°) Que, al respecto es menester señalar "
    "que la ley 25.790, prorrogada por la ley 25.792, establece que las "
    "decisiones adoptadas por el Poder Ejecutivo Nacional en los procesos "
    "de renegociación no se hallarán condicionadas o limitadas por las "
    "estipulaciones contenidas en los marcos regulatorios que rigen los "
    "respectivos contratos de concesión. En tales condiciones, es decir, "
    "ante la modificación sustancial del marco fáctico y normativo vigente "
    "al tiempo de trabarse la litis, resulta inoficioso emitir un "
    "pronunciamiento en la causa."
)

EJ7_MAQUEDA_AUTONOMO = (
    "VOTO DE LA SEÑORA VICEPRESIDENTE MINISTRO DOCTOR DON JUAN CARLOS "
    "MAQUEDA Considerando: 1°) Que la actora, Evelyn Patrizia Gottschau, "
    "promovió acción de amparo contra la Ciudad Autónoma de Buenos Aires "
    "(Poder Judicial — Consejo de la Magistratura de la Ciudad de Buenos "
    "Aires) con el objeto de que se revocara la resolución 214/99, del "
    "plenario del mencionado Consejo, que desestimó la impugnación que "
    "Gottschau formuló contra el acta 24/99..."
)

EJ8_FAYT_AUTONOMO = (
    "VOTO DEL SEÑOR MINISTRO DOCTOR DON CARLOS S. FAYT Considerando: 1°) "
    "Que la Sala K de la Cámara Nacional de Apelaciones en lo Civil, al "
    "desestimar el recurso deducido por la peticionaria, confirmó la "
    "resolución de la Inspección General de Justicia 1142/03 que denegó a "
    "la Asociación Lucha por la Identidad Travesti-Transexual (\"ALITT\") la "
    "autorización para funcionar como persona jurídica, en el marco del "
    "art. 33, segunda parte, ap. 1°, del Código Civil..."
)

# ── Casos de prueba ──────────────────────────────────────────────────────────
# (texto, wc_voto, is_merit_decision, tipo_esperado, fragmenta_esperado,
#  divergencia_esperada_substring_o_None, etiqueta)

CASOS = [
    (EJ1_HIGHTON_280,        89,    0, "B", False,     None,            "Ej1 Highton 280"),
    (EJ2_ARGIBAY_280,        55,    0, "B", False,     None,            "Ej2 Argibay 280"),
    (EJ3_FAYT_VERBITSKY,    133,    1, "E", "parcial", "dispositivo",   "Ej3 Fayt Verbitsky"),
    (EJ4_LORENZETTI_PROCURADOR, 482, 1, "A", False,     None,            "Ej4 Lorenzetti procurador"),
    (EJ5_LORENZETTI_EXCLUSION, 1398, 0, "C", "parcial", "considerando 4", "Ej5 Lorenzetti exclusión"),
    (EJ6_ARGIBAY_HASTA_2,    153,    0, "C", "parcial", "considerando 3", "Ej6 Argibay hasta 2°"),
    (EJ7_MAQUEDA_AUTONOMO,  6026,    1, "D", True,      "dispositivo",   "Ej7 Maqueda autónomo"),
    (EJ8_FAYT_AUTONOMO,     6666,    1, "D", True,      "dispositivo",   "Ej8 Fayt autónomo"),
]


def main():
    n_ok = 0
    n_fail = 0
    for texto, wc, is_merit, tipo_esp, frag_esp, div_esp, etq in CASOS:
        r = clasificar_tipo_voto(texto, wc, is_merit)
        ok_tipo = r["tipo_voto_sep"] == tipo_esp
        ok_frag = r["fragmenta_ratio"] == frag_esp
        if div_esp is None:
            ok_div = r["punto_divergencia"] is None
        else:
            ok_div = (r["punto_divergencia"] is not None
                      and div_esp in r["punto_divergencia"])
        ok_all = ok_tipo and ok_frag and ok_div

        marker = "OK" if ok_all else "FAIL"
        print(f"[{marker}] {etq}")
        print(f"        esperado:  tipo={tipo_esp!r}  frag={frag_esp!r}  div~={div_esp!r}")
        print(f"        obtenido:  tipo={r['tipo_voto_sep']!r}  "
              f"frag={r['fragmenta_ratio']!r}  div={r['punto_divergencia']!r}")
        if ok_all:
            n_ok += 1
        else:
            n_fail += 1
    print(f"\n{n_ok}/{len(CASOS)} OK, {n_fail} FAIL")
    return n_fail


if __name__ == "__main__":
    import sys
    sys.exit(main())
