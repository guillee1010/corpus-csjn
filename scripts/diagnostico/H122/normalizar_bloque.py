#!/usr/bin/env python3
"""
M21 — pre-pasada de normalización del bloque  ·  arco `normalizar_bloque` (H124)
================================================================================

PoC. NO es canónico todavía: vive en scripts/H124 hasta pasar la compuerta del
BLUEPRINT. Cuando se integre, las regex RE_RUNNING_HEAD / RE_EDITORIAL_ANY y
_unhyphenate deben unificarse con las de parser.py (acá se ESPEJAN para que el
módulo sea testeable standalone, sin importar parser.py — que arrastra
parser_editorial).

Arquitectura (BLUEPRINT §1): localizar → **normalizar** → extraer.
    1. localización sobre crudo  (headers presentes, ruido-a-saltar)
    2. normalizar_bloque(bloque) → VISTA LIMPIA (copia, misma longitud)
    3. extracción sobre la vista limpia (_barrer, considerando, gate, materia)

Invariantes (las testea test_normalizar_bloque.py):
    - len(salida) == len(entrada)            (índices y ventana firma k+1..k+41)
    - running-heads → ""  (enmascarados IN-PLACE, NO eliminados)
    - marcadores editoriales (RE_EDITORIAL_ANY) NUNCA se enmascaran
      (son señal de corte de detectar_fin_real, parser ~2591)
    - la entrada no se muta (se devuelve copia)

Dos perillas independientes para el harness de 4 configs (BLUEPRINT §2):
    headers=on/off   ·   guion=on/off
"""
import re

# ── RE_RUNNING_HEAD (nueva, BLUEPRINT §1) ────────────────────────────────────
# Banner intercalado en línea propia: `número + frase + número`, p.ej.
#   "147 DE JUSTICIA DE LA NACION 329", "329 FALLOS DE LA CORTE SUPREMA",
#   "437 DE JUSTICIA DE LA NACION", o la frase sola.
# La FRASE es obligatoria; los números, opcionales. Anclado ^...$: solo matchea
# si la línea ES el banner (no la frase legítima "Corte Suprema de Justicia de
# la Nación" embebida en una oración — esa NO está sola en su línea).
# OJO: un número solo en su línea (page-number suelto) NO lo agarra esta regex
# (frase obligatoria); eso lo maneja RE_PAGE_HEADER donde corresponde. Fuera de
# alcance de M21 por ahora (ver DEUDA si aparece en la medición).
RE_RUNNING_HEAD = re.compile(
    r"^\s*(?:\d{1,4}\s+)?"
    r"(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)"
    r"(?:\s+\d{1,4})?\s*$",
    re.I,
)

# ── ESPEJO de parser.py (dedupe al integrar) ─────────────────────────────────
# RE_EDITORIAL_ANY: idéntica a parser.py línea 180 (B077). Preservar SIEMPRE.
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
    """Idéntica a parser.py línea 418 (B056/H066): une 'deses- tima' → 'desestima'
    cuando el guión de corte tipográfico va seguido de whitespace + \\w.
    NOTA (H124): a nivel LÍNEA esto solo agarra el corte INTRA-línea ('Procura-
    dor' en una misma línea). El corte de fin-de-línea ('...el re-' / 'curso...')
    NO lo toca esta pasada — pero classify_outcome ya lo deshifena POST-join. Por
    eso se espera que el marginal de `guion` en clasificación sea chico; el harness
    lo mide en vez de asumirlo."""
    return re.sub(r"(\w)[\u00ad\u002d]\s+(\w)", r"\1\2", text)


def es_running_head(linea: str) -> bool:
    """¿La línea ES un running-head a enmascarar? Editorial gana (nunca se enmascara)."""
    s = linea.strip()
    if not s:
        return False
    if _es_marcador_editorial(linea):
        return False
    return bool(RE_RUNNING_HEAD.match(s))


def normalizar_bloque(bloque, *, headers: bool = True, guion: bool = True):
    """Devuelve una COPIA del bloque (misma longitud, índices preservados).

    headers=True → running-heads enmascarados a "" in-place.
    guion=True   → _unhyphenate por línea.
    headers=False y guion=False → copia idéntica (baseline del harness).
    """
    salida = []
    for ln in bloque:
        if headers and es_running_head(ln):
            salida.append("")          # enmascara; preserva la línea (índice intacto)
            continue
        salida.append(_unhyphenate(ln) if guion else ln)
    return salida


# Mapa de configs del harness (BLUEPRINT §2). baseline = control.
CONFIGS = {
    "baseline": dict(headers=False, guion=False),
    "+headers": dict(headers=True,  guion=False),
    "+guion":   dict(headers=False, guion=True),
    "+ambos":   dict(headers=True,  guion=True),
}
