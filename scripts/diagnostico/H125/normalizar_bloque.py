#!/usr/bin/env python3
"""
M21 — pre-pasada de normalización del bloque  ·  arco `normalizar_bloque`
=========================================================================

REESCRITO desde cero (no se confía en el PoC de H124). Diferencia central:

    La DETECCIÓN del running-head NO se hace por regex que escanea el texto
    (eso podía divergir del pipeline y enmascaraba parcial). Se hace por el
    OUTPUT CANÓNICO `mapa_paginas.csv` (producido por detectar_paginas.py):
    el caller pasa los offsets de las líneas-header que caen en el bloque, y
    este módulo enmascara la TERNA completa anclada en cada uno.

    RE_RUNNING_HEAD se usa SOLO para identificar cuál de las líneas adyacentes
    al ancla es la frase (dar forma a la terna), nunca para buscar headers.

Hechos verificados (no de memoria) que fundan el diseño:
  - mapa_paginas.csv: columnas (tomo, archivo, linea_header, pagina).
    `linea_header` = índice 0-indexado de la LÍNEA-TOMO (el número de tomo
    pelado), no la frase ni la página. detectar_paginas.detectar_en_lineas
    ancla en `_norm(l) == tomo_str` y emite `(i, pagina)` con i = esa línea
    (detectar_paginas.py L104-132).
  - Mismo sistema 0-indexado que el bloque: construir_bloque_desde_localizacion
    devuelve lines[linea_inicio:linea_fin+1] y su docstring dice "linea_inicio y
    linea_fin son 0-indexados (igual que en mapa_paginas.csv)" (parser.py L1822).
    ⇒ offset_relativo = linea_header − linea_inicio, válido en [li, lf].
  - Forma de la terna (3 renglones consecutivos en línea propia): la página va
    ANTES del tomo en el pliego (offset negativo prioritario, detectar_paginas
    L107-109). Layout típico:  [página] / [frase] / [tomo=ancla].
    La frase es "DE JUSTICIA DE LA NACION/NACIÓN" o "FALLOS DE LA CORTE SUPREMA".
  - Headers interpolados B116 (apertura de sección): su `linea_header` apunta al
    BANNER DE MES (OCTUBRE…), no a un número de tomo (DEUDA B116). El guard de
    abajo (ancla debe ser número pelado) los SALTEA solo → no blanquea banners.

Invariantes:
  - len(salida) == len(entrada)   (índices y ventana de firma k+1..k+41 intactos)
  - running-heads → ""  (enmascarados IN-PLACE, NO eliminados)
  - marcadores editoriales (RE_EDITORIAL_ANY) NUNCA se enmascaran
    (son señal de corte de detectar_fin_real, parser ~2591)
  - la entrada no se muta (se devuelve una copia)
  - NUNCA blanquear una línea de texto real ante drift: si el ancla del mapa no
    parece componente de terna (número pelado), se saltea y se cuenta.

⚠️  El masking a "" NO libera por sí solo el presupuesto de 6 líneas del chunk de
    `_barrer` (parser L3092-3095, que cuenta líneas y no contenido). Para el
    camino `por_ello` hace falta un companion change en `_barrer` que saltee las
    líneas enmascaradas en el conteo. Esa decisión es POSTERIOR al test C (banco):
    este módulo NO toca `_barrer`. Para `extraer_considerando` (L1299-1301, sin
    presupuesto y ya filtra vacías) el masking a "" sí basta.
"""
import re

# ── DETECCIÓN: ninguna. Se usa mapa_paginas (canónico). ──────────────────────

# Frase del running-head, SOLA en su línea (^...$). Se usa únicamente para
# identificar la línea-frase adyacente a un ancla ya conocido por el mapa.
# La frase legítima "Corte Suprema de Justicia de la Nación" embebida en una
# oración NO matchea (no está sola en su línea).
RE_RUNNING_HEAD_FRASE = re.compile(
    r"^\s*(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s*$",
    re.I,
)

# Número pelado (1-4 dígitos) en línea propia: componente número de la terna
# (tomo o página).
RE_NUM_PELADO = re.compile(r"^\s*\d{1,4}\s*$")

# RE_EDITORIAL_ANY: ESPEJO EXACTO de parser.py L180 (B077). Preservar SIEMPRE.
# Al integrar a parser.py se deduplica (importar de allá).
RE_EDITORIAL_ANY = re.compile(
    r"^(?:"
    r"A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s+Y\s+RESOLUCIONES\s*$"
    r"|DISCURSOS\b"
    r"|INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I,
)


def _es_marcador_editorial(linea: str) -> bool:
    s = linea.strip()
    return bool(s and RE_EDITORIAL_ANY.match(s))


def _unhyphenate(text: str) -> str:
    """ESPEJO EXACTO de parser.py L418 (B056/H066): une el quiebre tipográfico
    'deses- tima' → 'desestima' (guión o soft-hyphen + whitespace + \\w). NO toca
    guiones legítimos sin whitespace ('Buenos Aires-La Plata'). Es a nivel LÍNEA:
    el corte de FIN de línea ('...el re-' / 'curso...') no lo agarra esta pasada
    (lo deshifena classify_outcome post-join) → el marginal de `guion` se espera
    chico; el harness lo MIDE, no lo asume."""
    return re.sub(r"(\w)[\u00ad\u002d]\s+(\w)", r"\1\2", text)


def es_linea_frase(linea: str) -> bool:
    """¿Es la línea-FRASE de un running-head? Editorial gana (nunca se enmascara)."""
    s = linea.strip()
    if not s or _es_marcador_editorial(linea):
        return False
    return bool(RE_RUNNING_HEAD_FRASE.match(s))


def _es_num_pelado(linea: str) -> bool:
    return bool(RE_NUM_PELADO.match(linea))


def offsets_relativos(linea_headers_abs, linea_inicio, linea_fin):
    """Traduce líneas-header ABSOLUTAS (de mapa_paginas, 0-indexadas) a offsets
    RELATIVOS al bloque = lines[linea_inicio:linea_fin+1]. Mismo sistema
    0-indexado (construir_bloque_desde_localizacion, parser ~1822). Descarta las
    que caen fuera de [linea_inicio, linea_fin]. Pura y testeable."""
    li, lf = int(linea_inicio), int(linea_fin)
    return sorted(lh - li for lh in (int(x) for x in linea_headers_abs)
                  if li <= lh <= lf)


def normalizar_bloque(bloque, header_offsets=(), *,
                      headers: bool = True, guion: bool = True, _diag=None):
    """Devuelve una COPIA del bloque (misma longitud, índices preservados).

    bloque         : lista de líneas del fallo (crudo, post-localización).
    header_offsets : offsets RELATIVOS al bloque de las líneas-tomo del mapa
                     (usar offsets_relativos()). VACÍO ⇒ no enmascara headers
                     (fail-safe: sin fuente canónica, no se inventa nada).
    headers=True   : enmascara la TERNA (ancla número-tomo + frase adyacente +
                     número de página del otro lado de la frase) a "" in-place.
                     Guard: si bloque[h] no es número pelado (drift o banner B116
                     interpolado) o es editorial → se saltea, NO se blanquea.
    guion=True     : _unhyphenate por línea (no a las enmascaradas).
    headers=False y guion=False ⇒ copia idéntica (baseline del harness).

    Si _diag es un dict, se le cargan contadores: ternas, ancla_saltada_drift,
    frase_no_adyacente (degenerado: solo se pudo enmascarar el ancla).
    """
    n = len(bloque)
    mask = [False] * n
    diag = _diag if _diag is not None else {}
    for k in ("ternas", "ancla_saltada_drift", "frase_no_adyacente", "deshifenadas"):
        diag.setdefault(k, 0)

    if headers:
        for h in header_offsets:
            if not (0 <= h < n):
                diag["ancla_saltada_drift"] += 1
                continue
            # El ancla canónica es la LÍNEA-TOMO = número pelado. Si no lo es,
            # es drift mapa<->bloque o un header B116 interpolado (banner de
            # sección): NO blanquear texto real / banner de apertura.
            if _es_marcador_editorial(bloque[h]) or not _es_num_pelado(bloque[h]):
                diag["ancla_saltada_drift"] += 1
                continue
            mask[h] = True  # línea-tomo
            # La frase está en h-1 o h+1; la página, del otro lado de la frase
            # (h-2 o h+2). Se prueban ambas orientaciones del pliego.
            frase_hallada = False
            for d in (-1, 1):
                f = h + d
                if 0 <= f < n and es_linea_frase(bloque[f]):
                    mask[f] = True
                    frase_hallada = True
                    p = h + 2 * d
                    if (0 <= p < n and _es_num_pelado(bloque[p])
                            and not _es_marcador_editorial(bloque[p])):
                        mask[p] = True
                    break
            if frase_hallada:
                diag["ternas"] += 1
            else:
                diag["frase_no_adyacente"] += 1  # solo el ancla; OCR de la frase?

    salida = []
    for i, ln in enumerate(bloque):
        if mask[i]:
            salida.append("")                       # enmascara; índice intacto
        elif guion:
            nl = _unhyphenate(ln)
            if nl != ln:
                diag["deshifenadas"] += 1
            salida.append(nl)
        else:
            salida.append(ln)
    return salida


# Mapa de configs del harness (BLUEPRINT §2). baseline = control.
CONFIGS = {
    "baseline": dict(headers=False, guion=False),
    "+headers": dict(headers=True,  guion=False),
    "+guion":   dict(headers=False, guion=True),
    "+ambos":   dict(headers=True,  guion=True),
}
