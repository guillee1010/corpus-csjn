# ── Refactor sub-bloques (v18) ────────────────────────────────────────────────
# Funciones nuevas agregadas en Tanda 1 del refactor de sub-bloques.
# Aún no integradas al loop principal: solo definidas. La integración se hace
# en Tanda 2.
#
# Diseño: el bloque crudo de un caso se divide en dos sub-bloques:
#   - pre_fallo: líneas antes de "FALLO DE LA CORTE SUPREMA" real
#                (contiene carátula, sumarios, dictamen, y -en Tipo 1- residuo
#                 del caso anterior).
#   - fallo:     líneas desde "FALLO DE LA CORTE SUPREMA" real en adelante
#                (vistos, considerandos, dispositivo, firma, votos disidentes).
#
# Esto resuelve por construcción:
#   - Bug XII: el "Por ello" del dictamen queda en pre_fallo, fuera de alcance.
#   - Bug case_name_cuerpo: la carátula se busca en pre_fallo (no retrocediendo
#     desde apertura_idx) o en fallo via "Vistos los autos:" (V1).
#   - Bug XII enmascarado (Tipo 1): el primer FALLO espurio del caso anterior
#     se descarta por reglas explícitas.

# Marcador estricto de apertura, idéntico al RE_APERTURA original pero
# acotado a "FALLO DE LA CORTE SUPREMA" (sin la variante "SENTENCIA").
# Usamos uno separado porque la lógica de sub-bloques se basa empíricamente
# en este marcador exacto (Bloque B confirmó que cubre 99.9% del corpus
# combinado con V1/V4/V5).
RE_FALLO_APERTURA = re.compile(r"^\s*FALLO DE LA CORTE SUPREMA\s*$")

# Cierre canónico del bloque (para detección de Tipo 1 en pre_fallo).
RE_TRIB_ORIGEN_LINEA = re.compile(r"Tribunal de origen:", re.I)

# Buenos Aires + fecha en línea siguiente al FALLO (para regla C de
# desambiguación entre múltiples FALLOs).
RE_BUENOS_AIRES_FECHA = re.compile(r"^\s*Buenos Aires[,]?\s+", re.I)

# Marcador de nota al pie editorial: "(*)" al inicio de línea.
RE_NOTA_AL_PIE = re.compile(r"\(\*\)")

# Ruido aceptable entre "FALLO DE LA CORTE SUPREMA" y "Buenos Aires," cuando
# el fallo arranca al final de una página y la fecha cae al inicio de la
# siguiente. Líneas vacías + headers de página + números de página son ruido.
# Cualquier otra cosa (dispositivo, firma, texto sustantivo) NO es ruido y
# la regla C debe rechazar el FALLO como espurio.
RE_PAGE_NOISE = re.compile(
    r"^\s*(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N|\d{1,6})\s*$",
    re.I,
)

# Apertura V1 del fallo: "Vistos los autos:" + comilla.
# Cubre comillas tipográficas (« » " ') y rectas.
COMILLAS_APERTURA = "\u201C\u201D\u00AB\u00BB\"\u2018\u2019'"
RE_VISTOS_LOS_AUTOS = re.compile(
    r'^\s*Vistos los autos:\s*([' + COMILLAS_APERTURA + r'])',
    re.I
)

# Apertura V4/V5 (fallback cuando no hay FALLO ni Vistos los autos).
# Cubre "Autos y Vistos;" y "Autos y Vistos:".
RE_AUTOS_Y_VISTOS = re.compile(r'^\s*Autos y Vistos\s*[;:]', re.I)

# Carátula estructural por patrón "X c/ Y s/ Z" en MAYÚSCULAS o
# línea entera en MAYÚSCULAS.
# Lista negra de líneas en MAYÚSCULAS que no son carátulas.
LISTA_NEGRA_CARATULA = {
    "FALLOS DE LA CORTE SUPREMA",
    "DE JUSTICIA DE LA NACION",
    "DE JUSTICIA DE LA NACIÓN",
    "FALLO DE LA CORTE SUPREMA",
    "SENTENCIA DE LA CORTE SUPREMA",
    "DICTAMEN DE LA PROCURACION GENERAL",
    "DICTAMEN DE LA PROCURACIÓN GENERAL",
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
}


def _normalizar(s):
    """Normaliza para comparación de carátulas: lower, sin acentos, c/ → contra,
    sin puntuación, espacios colapsados."""
    if not s:
        return ""
    s = s.lower()
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'\b(bs\.?\s*as\.?|prov\.?\s*de\s*bs\.?\s*as\.?)\b',
               'buenos aires', s)
    s = re.sub(r'\bc/\b', 'contra', s)
    s = re.sub(r'\bs/\b', 'sobre', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _son_equivalentes(a, b):
    """Substring containment del normalizado más corto en el más largo, con
    fallback por similitud de palabras clave (>=75% de palabras del corto en
    el largo). Decisión P2 = C del Bloque C."""
    if not a or not b:
        return False
    a_norm = _normalizar(a)
    b_norm = _normalizar(b)
    if not a_norm or not b_norm:
        return False
    corto, largo = sorted([a_norm, b_norm], key=len)
    if corto in largo:
        return True
    palabras_corto = set(corto.split())
    palabras_largo = set(largo.split())
    if not palabras_corto:
        return False
    palabras_comunes = palabras_corto & palabras_largo
    return len(palabras_comunes) / len(palabras_corto) >= 0.75


def _split_nombres_indice(nombres_indice_str):
    """Acepta el string de fallos_localizados.csv (separado por ' | ') o una
    lista. Devuelve lista de nombres limpios."""
    if not nombres_indice_str:
        return []
    if isinstance(nombres_indice_str, list):
        return [n.strip() for n in nombres_indice_str if n and n.strip()]
    return [n.strip() for n in nombres_indice_str.split(' | ') if n and n.strip()]


def _matching_contra_indice(pre_fallo, nombres_indice_str):
    """Estrategia 1: busca en pre_fallo alguna línea equivalente a alguno de
    los nombres del catálogo (nombres_indice). Devuelve el nombre del catálogo
    que tuvo match, no el de la línea."""
    nombres = _split_nombres_indice(nombres_indice_str)
    if not nombres:
        return None
    pre_fallo_texto = " ".join(pre_fallo)
    for nombre in nombres:
        if _son_equivalentes(nombre, pre_fallo_texto):
            return nombre
    return None


def _detectar_caratula_estructural(pre_fallo):
    """Estrategia 2: busca de abajo hacia arriba la última línea con patrón
    'X c/ Y s/ Z' (carátula completa) o línea entera en MAYÚSCULAS razonablemente
    larga, descartando entradas de la lista negra (headers de sección, meses,
    marcadores institucionales)."""
    for linea in reversed(pre_fallo):
        s = linea.strip()
        if not s:
            continue
        if s.upper() in LISTA_NEGRA_CARATULA:
            continue
        # Patrón A: X c/ Y s/ Z en MAYÚSCULAS (ej: "JUAREZ c/ PROVINCIA s/ DAÑOS")
        if re.match(r'^[A-ZÁÉÍÓÚÑ\s,\.\-–—]+\s+c/\s+.+\s+s/\s+.+$', s):
            return s
        # Patrón B: línea entera en MAYÚSCULAS, longitud razonable
        if s.isupper() and 10 < len(s) < 200:
            return s
    return None


def extraer_caratula_de_vistos(fallo, max_lineas=8):
    """Estrategia 3 (V1): busca 'Vistos los autos:' seguido de comilla de
    apertura, reconstruye la carátula concatenando líneas hasta cierre.
    Maneja comillas tipográficas y wrap por silabación (- o soft hyphen)."""
    if not fallo:
        return None
    COMILLAS_TODAS = COMILLAS_APERTURA  # mismo conjunto sirve para apertura y cierre
    for i, linea in enumerate(fallo):
        m = RE_VISTOS_LOS_AUTOS.match(linea)
        if not m:
            continue
        comilla_apert = m.group(1)
        try:
            pos_apertura = linea.index(comilla_apert, m.start())
        except ValueError:
            continue
        acumulado = linea[pos_apertura + 1:].rstrip()
        # Cierre en la misma línea
        m_cierre = re.search(f'[{re.escape(COMILLAS_TODAS)}]', acumulado)
        if m_cierre:
            return acumulado[:m_cierre.start()].strip()
        # Cierre en líneas siguientes
        for j in range(i + 1, min(i + max_lineas, len(fallo))):
            sig = fallo[j].rstrip()
            if acumulado.endswith('\u00AD') or acumulado.endswith('-'):
                acumulado = acumulado.rstrip('\u00AD-') + sig.lstrip()
            else:
                acumulado = acumulado + ' ' + sig.lstrip()
            m_cierre = re.search(f'[{re.escape(COMILLAS_TODAS)}]', sig)
            if m_cierre:
                # Encontrar la última comilla en acumulado
                pos_cierre = max(
                    (acumulado.rfind(c) for c in COMILLAS_TODAS if c in acumulado),
                    default=-1
                )
                if pos_cierre > 0:
                    return acumulado[:pos_cierre].strip()
        # Si no encuentra cierre pero acumuló algo, devolver lo que tiene
        return acumulado.strip() if acumulado.strip() else None
    return None


def _decidir_caratula(candidatos, flags_division):
    """Lógica de coincidencia:
       - 3 candidatos: si las 3 son equivalentes → matching_indice + alta_triple.
                       Si no → matching_indice + media_desacuerdo + discrepancias.
       - 2 candidatos: prioridad matching > estructural > V1 → media_dos_estrategias.
       - 1 candidato: ese + baja_una_estrategia.
       - 0 candidatos: None + patologico.
    """
    if not candidatos:
        return None, {"confianza": "patologico"}
    if len(candidatos) == 3:
        valores = list(candidatos.values())
        if all(_son_equivalentes(v, valores[0]) for v in valores):
            return candidatos["matching_indice"], {"confianza": "alta_triple"}
        return candidatos["matching_indice"], {
            "confianza": "media_desacuerdo",
            "discrepancias": dict(candidatos),
        }
    if len(candidatos) == 2:
        for clave in ("matching_indice", "estructural", "vistos_los_autos"):
            if clave in candidatos:
                return candidatos[clave], {"confianza": "media_dos_estrategias"}
    if len(candidatos) == 1:
        clave = list(candidatos.keys())[0]
        return candidatos[clave], {"confianza": "baja_una_estrategia"}
    return None, {"confianza": "patologico"}


def detectar_caratula(pre_fallo, fallo, nombres_indice_str, flags_division=None):
    """Orquestador: aplica las 3 estrategias y delega la decisión a
    _decidir_caratula. Devuelve (caratula:str|None, meta:dict).

    nombres_indice_str: string del CSV (separado por ' | ') o lista.
    flags_division: dict de flags de dividir_bloque_en_sub_bloques (opcional,
                    se pasa a _decidir_caratula por si se requiere para
                    decisiones futuras; hoy no se usa).
    """
    candidatos = {}

    cand_1 = _matching_contra_indice(pre_fallo, nombres_indice_str)
    if cand_1:
        candidatos["matching_indice"] = cand_1

    cand_2 = _detectar_caratula_estructural(pre_fallo)
    if cand_2:
        candidatos["estructural"] = cand_2

    cand_3 = extraer_caratula_de_vistos(fallo)
    if cand_3:
        candidatos["vistos_los_autos"] = cand_3

    return _decidir_caratula(candidatos, flags_division or {})


def _es_ruido_entre_fallo_y_buenos_aires(linea):
    """Una línea entre 'FALLO DE LA CORTE SUPREMA' y 'Buenos Aires,' es ruido
    aceptable si está vacía o es un header de página / número de página."""
    s = linea.strip()
    if not s:
        return True
    if RE_PAGE_NOISE.match(linea):
        return True
    return False


def _cumple_regla_c(bloque, idx_fallo, max_lineas=8):
    """Regla C refinada: 'FALLO DE LA CORTE SUPREMA' es candidato a real si
    en las próximas max_lineas líneas aparece 'Buenos Aires,' Y todas las
    líneas intermedias son ruido (vacías / headers / números de página).

    Esto cubre el caso típico de paginación PDF→MD donde entre el FALLO y
    'Buenos Aires,' hay headers de página intermedios. Rechaza FALLOs
    espurios del caso anterior (Tipo 1) porque entre ellos y el próximo
    'Buenos Aires,' hay texto sustantivo (dispositivo, firma, carátula).
    """
    for j in range(idx_fallo + 1, min(idx_fallo + 1 + max_lineas, len(bloque))):
        if RE_BUENOS_AIRES_FECHA.match(bloque[j]):
            for k in range(idx_fallo + 1, j):
                if not _es_ruido_entre_fallo_y_buenos_aires(bloque[k]):
                    return False
            return True
    return False


def _elegir_fallo_real(bloque, indices_fallo, flags):
    """Reglas para elegir el FALLO real cuando hay múltiples:
       A) Descartar FALLOs en notas al pie (precedidos por 'Dicha sentencia
          dice así' o por línea con '(*)').
       B) Si queda 1 candidato, ese.
       C) Si quedan varios, el primer FALLO seguido por 'Buenos Aires,' en
          las próximas 8 líneas con solo ruido intermedio (vacío / header de
          página / número de página). Si TODOS los candidatos cumplen C,
          desempata regla D (caso típico: bug catalográfico, bloque que
          abarca dos casos legítimos).
       D) Fallback: el último candidato. Empíricamente (Bloque A, sesión XV),
          cuando hay múltiples FALLOs no editoriales el último suele ser el
          real. NOTA: si el bloque contiene dos casos completos, esto es un
          bug de catalogación (cruce catálogo↔mapa), no del parser. La
          regla D solo elige uno de los dos de manera consistente; la
          solución real está en el pendiente de auditoría catalográfica.
    """
    candidatos = []
    for idx in indices_fallo:
        # Regla A1: precedido por "Dicha sentencia dice así" en ventana de 5 líneas
        ventana_arriba = "\n".join(bloque[max(0, idx - 5):idx])
        if "Dicha sentencia dice así" in ventana_arriba:
            flags["tiene_nota_al_pie"] = True
            continue
        # Regla A2: línea inmediatamente anterior contiene "(*)"
        if idx > 0 and RE_NOTA_AL_PIE.search(bloque[idx - 1]):
            flags["tiene_nota_al_pie"] = True
            continue
        candidatos.append(idx)

    if not candidatos:
        # Todos espurios: devolvemos el último FALLO original (mejor que nada).
        return indices_fallo[-1]
    if len(candidatos) == 1:
        return candidatos[0]

    # Regla C: separar candidatos según si cumplen el patrón "FALLO seguido
    # de Buenos Aires, en las próximas 8 líneas con solo ruido intermedio".
    cumplen_c = [idx for idx in candidatos if _cumple_regla_c(bloque, idx)]

    if cumplen_c and len(cumplen_c) < len(candidatos):
        # Algunos cumplen, otros no: gana el primero que cumple. Esto cubre
        # el caso típico donde el FALLO real está separado de "Buenos Aires,"
        # solo por paginación, pero el espurio tiene texto sustantivo en medio.
        return cumplen_c[0]

    # Regla D: si todos cumplen (bug catalográfico) o ninguno cumple (caso
    # patológico), devolver el último candidato. La asunción empírica es que
    # cuando hay múltiples FALLOs no editoriales en un mismo bloque, el real
    # está al final.
    return candidatos[-1]


def _fallback_sin_fallo(bloque, pagina_inicio, flags):
    """Sin FALLO detectable: buscar 'Autos y Vistos;' o 'Autos y Vistos:' como
    proxy de inicio del fallo (V4/V5 del Bloque B)."""
    for i, linea in enumerate(bloque):
        if RE_AUTOS_Y_VISTOS.match(linea):
            flags["fallo_idx_elegido"] = i
            flags["estrategia_usada"] = "fallback_autos_y_vistos"
            return bloque[:i], bloque[i:], flags
    flags["estrategia_usada"] = "fallback_sin_apertura"
    return bloque, [], flags


def dividir_bloque_en_sub_bloques(bloque_lineas, pagina_inicio, nombres_indice_str):
    """Divide el bloque en (pre_fallo, fallo, flags).

    pre_fallo: líneas antes del FALLO real.
    fallo:     líneas desde el FALLO real en adelante.
    flags:     dict con metadatos de la división:
               - n_fallos_detectados: int
               - fallo_idx_elegido: int|None (índice 0-based en bloque_lineas)
               - estrategia_usada: str
               - tiene_nota_al_pie: bool
               - pagina_compartida: bool (Tipo 1: hay 'Tribunal de origen:'
                                          en pre_fallo)
    """
    flags = {
        "n_fallos_detectados": 0,
        "fallo_idx_elegido": None,
        "estrategia_usada": None,
        "tiene_nota_al_pie": False,
        "pagina_compartida": False,
    }

    # Paso 1: encontrar todos los marcadores FALLO DE LA CORTE SUPREMA
    indices_fallo = [
        i for i, linea in enumerate(bloque_lineas)
        if RE_FALLO_APERTURA.match(linea)
    ]
    flags["n_fallos_detectados"] = len(indices_fallo)

    # Paso 2: elegir el FALLO real
    if len(indices_fallo) == 0:
        return _fallback_sin_fallo(bloque_lineas, pagina_inicio, flags)
    elif len(indices_fallo) == 1:
        flags["fallo_idx_elegido"] = indices_fallo[0]
        flags["estrategia_usada"] = "fallo_unico"
    else:
        idx_real = _elegir_fallo_real(bloque_lineas, indices_fallo, flags)
        flags["fallo_idx_elegido"] = idx_real
        flags["estrategia_usada"] = "fallo_multiple_resuelto"

    # Paso 3: dividir
    idx = flags["fallo_idx_elegido"]
    pre_fallo = bloque_lineas[:idx]
    fallo = bloque_lineas[idx:]

    # Paso 4: detectar página compartida (Tipo 1)
    if any(RE_TRIB_ORIGEN_LINEA.search(l) for l in pre_fallo):
        flags["pagina_compartida"] = True

    return pre_fallo, fallo, flags


def detectar_dispositivo(fallo):
    """Encuentra los 'Por ello' del sub-bloque fallo.

    Bug XII resuelto por construcción: el 'Por ello' del dictamen está en
    pre_fallo, no en fallo, y por tanto no es accesible desde acá.

    Devuelve (info:dict|None, meta:dict):
      info = {
        "primer_por_ello":  int,  # índice en `fallo`
        "todos_por_ello":   list[int],
        "ultimo_por_ello":  int,
      }
      meta = {"strategy": "por_ello_simple"|"por_ello_multiple"|"ninguno"}
    """
    indices_por_ello = []
    for i, linea in enumerate(fallo):
        # Mismo patrón que el RE_POR_ELLO original: "Por ello" + opcional [,.] + espacio
        if re.match(r'^\s*Por\s+ello[,.]?\s+', linea, re.I):
            indices_por_ello.append(i)
    if not indices_por_ello:
        return None, {"strategy": "ninguno"}
    return (
        {
            "primer_por_ello": indices_por_ello[0],
            "todos_por_ello": indices_por_ello,
            "ultimo_por_ello": indices_por_ello[-1],
        },
        {"strategy": "por_ello_multiple" if len(indices_por_ello) > 1
                     else "por_ello_simple"},
    )

# ── Fin refactor sub-bloques (v18) ────────────────────────────────────────────
