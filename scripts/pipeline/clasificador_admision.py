#!/usr/bin/env python3
"""
clasificador_admision.py — fuente ÚNICA del eje de admisibilidad (corpus-csjn).
==============================================================================
Paralelo a clasificador_disposicion.py / clasificador_via.py. Reusa su norm()
(normalizador compartido, \xad-aware) para no divergir. Importado por:
  - scripts/diagnostico/H120/build_m20.py   (validación: clave admisibilidad)
  - scripts/pipeline/derivar_recursos.py     (producción: csjn_casos_recursos.csv)
Una sola copia de la lógica => el número validado describe lo que se shippea. Sin drift.

EJE PURO (decisión H146). `admisibilidad ∈ {admite, inadmite, no_aplica, sin_marcador}`
= SOLO la decisión de acceso. La VÍA (queja vs REX directo vs ordinario) es TRANSVERSAL:
ya vive en `es_queja` / `via_recurso` / `is_originaria`, NO se fusiona en el valor.
HM-01 (dos vías de acceso, el aporte vs SCDB) se lee como el cruce `admisibilidad × es_queja`,
no como valores compuestos (admite_queja/admite_rex). Verificado en disco (H146):
  - admitir la queja IMPLICA resolver el REX (87% de las admite_queja no enuncian
    'procedente' pero 1235/1292 resuelven al fondo) → la queja es modo de acceso, no disposición;
  - la queja es transversal a la vía-tipo (98,5% REX pero 30 ordinario), a la admisibilidad
    (admite 1598 / inadmite 624) y al mérito (revoca+deja 1412 / confirma 106).

Precedencia (gate externo → interno → estructural):
  1. eje queja  (queja_resultado, parser)  — la puerta externa; estable (1485/595).
  2. eje REX    (outcome=procedente / inadmisibles del considerando+dispositivo).
  3. REX-admit por TEXTO (object-aware): 'admisible/hace lugar' + objeto∈{REX, recurso de
     queja} cuando el outcome no lo nombró 'procedente' (recupera ~10 fugas de sin_marcador).
     Objeto acotado: NO reposición, NO demanda/cautelar (esos no son acceso al REX).
  4. originaria → no_aplica (sin gate de admisibilidad: competencia originaria, art. 117).
  5. disposición ∈ fondo → admite_implicito (revoca/deja/confirma sobre el REX, sin marcador).
  6. resto → sin_marcador (competencia/liquidación/honorarios/aclaratoria: por_ello legible,
     sin decisión de acceso al REX).

NO modificar sin re-validar contra el gold como held-out.
"""
import re
from clasificador_disposicion import norm   # normalizador compartido (\xad-aware)

__version__ = "0.1"

# ── Eje queja (de queja_resultado, parser — ESTABLE, A/B reproducido 1485/595) ──
Q_ADMITE   = {"hace_lugar", "admisible", "procedente"}
Q_INADMITE = {"desestima", "rechaza", "inadmisible", "improcedente",
              "nula", "suspendida", "desistida", "agreguese"}
# 'abstracta' (queja moot) NO entra a ninguno: cae a la cascada estructural (no es admite ni inadmite).

# ── Eje REX (de outcome) ───────────────────────────────────────────────────────
R_ADMITE   = {"procedente"}
R_INADMITE = {"inadmisible_280", "inadmisible_acordada_4", "desestima", "mal_concedido",
              "desierto", "caducidad", "inadmisible", "improcedente"}

# ── Disposición de fondo (de clasificador_disposicion) = admite_implicito ───────
_FONDO = {"revoca", "deja_sin_efecto", "confirma", "modifica", "nulidad", "grant_remand_implicito"}

# ── REX-admit por TEXTO (object-aware) ─────────────────────────────────────────
# Recupera 'se declara admisible el recurso extraordinario / el recurso de queja' y
# 'hace lugar al recurso extraordinario' cuando el outcome no salió 'procedente'.
# \b antes de 'admisible' para NO disparar dentro de 'inadmisible'. Objeto acotado al
# recurso (REX/queja), NO reposición (procesal) ni demanda/cautelar (no es acceso al REX).
RE_ADMITE_REX_TXT = re.compile(
    r"(?:se\s+)?declara\w*\s+(?:formalmente\s+|parcialmente\s+)?\badmisibles?\s+"
    r"(?:el\s+|la\s+|los\s+|las\s+)?(?:recursos?\s+extraordinarios?|recursos?\s+de\s+queja)|"
    r"(?:se\s+)?hace\w*\s+lugar\s+al?\s+recursos?\s+extraordinarios?", re.I)


def admisibilidad(queja_resultado, outcome, disposicion, is_originaria, por_ello=""):
    """Eje puro de admisibilidad. Devuelve 'admite' | 'inadmite' | 'no_aplica' | 'sin_marcador'.

    is_originaria: bool (el caller pasa is_originaria == '1', espejo de es_revision_fondo).
    La vía (queja/REX/ordinario) NO sale de acá: es transversal (es_queja/via_recurso).
    """
    if queja_resultado in Q_ADMITE:   return "admite"        # 1. gate queja (externo)
    if queja_resultado in Q_INADMITE: return "inadmite"
    if outcome in R_ADMITE:           return "admite"        # 2. gate REX directo
    if outcome in R_INADMITE:         return "inadmite"
    if RE_ADMITE_REX_TXT.search(norm(por_ello)):             # 3. REX-admit por texto (object-aware)
        return "admite"
    if is_originaria:                 return "no_aplica"     # 4. originaria: sin gate de admisibilidad
    if disposicion in _FONDO:         return "admite"        # 5. admite_implicito (fondo sin marcador)
    return "sin_marcador"                                    # 6. sin decisión de acceso al REX
