#!/usr/bin/env python3
"""
clasificador_causa.py — fuente ÚNICA de la causa de inadmisibilidad (corpus-csjn).
==================================================================================
Paralelo a clasificador_disposicion / via / admision. Portado de
parser.clasificar_causa_inadmisibilidad (H092..H107, v21.01) con el RE-CABLEO M26
paso 3: el GATE deja de ser `outcome` y pasa a `admisibilidad=="inadmite"`.

Importado por derivar_recursos.py (producción) y (futuro) build_m20/kappa (validación).

Cambios M26 paso 3:
  - GATE outcome -> admisibilidad=="inadmite".
  - DETECTORES NUEVOS anclados al tratado de la Secretaría (documento__37_.md):
      · CADUCIDAD §2.6 (por_ello, +guard polisemia §2.6.1/§2.6.2).
      · DESISTIMIENTO §2.1.11 (por_ello; 9/10 = default de depósito).
      · CUESTION_ABSTRACTA: mootness = decisión de admisibilidad (actualidad del
        agravio). Reusa la señal VALIDADA del parser (outcome=="abstracto", 148 casos
        vía H105/B113/B129) + RE_MOOT de respaldo, con guard `disposicion∉fondo`
        (separa los 96 puros de los 50 mixtos con verbo de mérito real).
  - Cola verbatim H092 (SD/FUND/DEPOSITO/FUERA/NO_RECURRIBLE) + guards holding-vs-
    antecedente (B100/B101/B103) SIN cambios, abierta a TODO `inadmite`.

Cambios M27 (tratado de la Secretaría, un detector por causal, commit separado):
  - INTERPOSICION_INCORRECTA §1.2.2: REX ante foro equivocado (no el tribunal que
    dictó la resolución, art. 257 CPCCN). Tratado §1.2.2 (1 prop, fallos 329:1538,
    312:1613, 307:639). Señal = foro equivocado + violación no subsanada, NO el
    "ante el tribunal que dictó" suelto (FP de antecedente: 339_p1417 explica la
    regla; 347_p352 la causa real es fundamentación). Va al FINAL de la cola, DESPUÉS de remite-dictamen
    (v0.5): solo drena SIN_CAUSAL, nunca preempta una causal etiquetada.
    Rinde: 2 (329_p1538/340_p1068), 0 FP. v0.2 tenía P3 ("REX presentado ante
    juzgado") → FP en 348_p1130 (holding real = extemporaneidad, no foro). v0.3
    remueve P3 tras eyeball (Guillermo).

Cambios H151 (bucket 1 del cajón SIN_CAUSAL — recall-gap remite-dictamen):
  - REMITE_DICTAMEN recall-gap: la variante "de conformidad con lo dictaminado por
    el Procurador" vive en el DISPOSITIVO (por_ello), NO en el considerando; el
    detector base sólo mira `co`. Nueva rama anclada a `pe` + verbo desestima/
    inadmisible (RE_REMITE_DICT_DISP / _VERBO), guard `disposicion∉_DISP_FONDO`
    (excluye 329_p2523/334_p109 = `confirma`, mérito). NO 'mal concedido' (bucket 3,
    329_p2005 queda en SIN_CAUSAL). GATEADA en dictamen_presente igual que la rama
    base (robusto/consistente: NO se workaroundea el parser). Rinde +5 con el flag
    actual (6º limpio 334_p417 + 345_p608 tienen wc_dictamen=0 → dictamen_presente
    False por un gap de SEGMENTACIÓN del parser en tomos recientes [Bxxx, dx. H151];
    se recuperan SOLOS al arreglar la fuente). Incluye 330_p170 (inhibitoria) que se
    auto-corrige cuando B135 le flipee la admisibilidad. Extiende el detector
    EXISTENTE, no agrega valor. Eyeball del banco completo (Guillermo).

Cascada (dispositivo/explícito antes que considerando/inferencia; espejo B109):
  caducidad → desistimiento → abstracta → 280 → ac4 → SD → FUND → DEPOSITO →
  FUERA → NO_RECURRIBLE → REMITE_DICTAMEN(co) → REMITE_DICTAMEN(disp,H151) → INTERPOSICION_INCORRECTA → SIN_CAUSAL.
  (caducidad/desistimiento van PRIMERO: son holdings del por_ello; el 280/ac4 se
   ancla al considerando y puede venir de un antecedente citado — testigo 340_p251.)

NO modificar sin re-validar contra el gold/A/B.
"""
import re

__version__ = "0.5"

# disposiciones de FONDO (verbo de mérito) — espejo de clasificador_disposicion._FONDO.
# Se replica como literal para no acoplar el import a la firma; si _FONDO cambia allá,
# sincronizar (igual criterio que RE_RUNNING_HEAD verbatim).
_DISP_FONDO = {"revoca", "deja_sin_efecto", "nulidad", "confirma", "modifica",
               "grant_remand_implicito"}

# ── normalización VERBATIM del parser (_unhyphenate L431 + whitespace) ─────────
def _unhyphenate(text: str) -> str:
    return re.sub(r"(\w)[­\u00ad-]\s+(\w)", r"\1\2", text)

def _prep(text):
    return re.sub(r"\s+", " ", _unhyphenate(text or "")).strip()

# ── 280 / Acordada 4 (VERBATIM parser L276-318) ───────────────────────────────
RE_280_CONSIDERANDO = re.compile(
    r"recurso\s+extraordinario.{0,150}?"
    r"(es|resulta|se\s+declara)\s+inadmisible"
    r".{0,150}?(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal",
    re.I | re.DOTALL)
RE_280_LIBRE = re.compile(
    r"\(?\s*(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal\s+Civil\s+y\s+Comercial",
    re.I)
RE_ACORDADA_4_CONSIDERANDO = re.compile(
    r"(?:art[s]?\.?\s*|art[íi]culo\s*)\d+\s*[°º]?\s*"
    r"(?:,\s*inc[s.]?.{0,30}?)?\s*del\s+reglamento"
    r".{0,80}?acordada\s*(?:n[°º]?\s*)?4(?!\d)\s*/?\s*(?:(?:del?\s+)?(?:20)?07)?",
    re.I | re.DOTALL)
RE_ACORDADA_4_REGLAMENTO = re.compile(
    r"reglamento.{0,60}?acordada\s*(?:n[°º]?\s*)?4(?!\d)\s*/?\s*(?:(?:del?\s+)?(?:20)?07)?",
    re.I | re.DOTALL)
RE_ACORDADA_4_DIRECTA = re.compile(
    r"(?:art[s]?\.?\s*|art[íi]culo\s*)\d+\s*[°º]?\s*"
    r"(?:,\s*inc[s.]?.{0,30}?)?\s*de\s+la\s+"
    r"acordada\s*(?:n[°º]?\s*)?4(?!\d)\s*/?\s*(?:(?:del?\s+)?(?:20)?07)?",
    re.I | re.DOTALL)

# ── DETECTORES NUEVOS (M26 paso 3) — tratado de la Secretaría ──────────────────
# CADUCIDAD §2.6: ancla dispositivo. Tratado L4941/4976/4997.
RE_CADUCIDAD_DISP = re.compile(
    r"(?:se\s+)?(?:declara|declarar|resuelve\b.{0,15})\s*(?:operada\s+)?(?:la\s+)?"
    r"caducidad\s+de\s+(?:la\s+)?instancia", re.I)
# Guard polisemia §2.6.1 (hace lugar) / §2.6.2 (rechaza): apercibimiento o rechazo del planteo.
RE_CADUCIDAD_GUARD = re.compile(
    r"apercibimiento\s+de\s+declarar|"
    r"(?:rechaz|desestim)\w*.{0,25}?(?:planteo|pedido|incidente|excepci[oó]n)\s+"
    r"(?:de\s+)?caducidad", re.I)

# DESISTIMIENTO §2.1.11: "se (lo) tiene por desistid{o} ... queja/recurso/presentación".
# Tolera adjetivo intercalado ("la presente queja") con gap acotado, sin cruzar '.'/';'.
RE_DESISTIMIENTO = re.compile(
    r"se\s+(?:lo\s+|la\s+|los\s+|las\s+)?tiene\s+por\s+desisti\w+"
    r"[^.;]{0,30}?(?:queja|recurso|presentaci[oó]n|hecho)", re.I)

# CUESTION_ABSTRACTA (respaldo textual; la señal primaria es outcome=="abstracto").
# Extiende inoficioso a 'dictar/el tratamiento/un pronunciamiento'. Guard B129 (no aside
# del dictamen) embebido como lookahead.
RE_MOOT = re.compile(
    r"inoficioso\s+(?:emitir|expedirse|pronunciarse|dictar|"
    r"(?:un\s+|el\s+|su\s+)?(?:pronunciamiento|tratamiento))"
    r"(?![^.]{0,40}(?:dictamin|procurador))|"
    r"(?:deviene|devino|devenid\w*|torn[oóa]\w*|result[oóa]\w*|qued[oó]\w*)\s+"
    r"(?:inoficioso|abstract\w+)(?![^.]{0,40}(?:dictamin|procurador))|"
    r"(?:se\s+)?declara\w*\s+abstract\w+\s+(?:la\s+)?cuesti[oó]n|"
    r"declarar\s+abstract\w+", re.I)

# ── Cola validada H092 (VERBATIM parser L630-697) ─────────────────────────────
RE_CAUSA_SENTENCIA_DEFINITIVA = re.compile(
    r"no\s+se\s+dirige\s+contra\s+(?:una\s+|la\s+)?sentencia\s+definitiva"
    r"(?:\s+o\s+equiparable)?|"
    r"no\s+(?:constituye|reviste\s+(?:el\s+)?car[aá]cter\s+de|es)\s+"
    r"(?:la\s+|una\s+)?sentencia\s+definitiva|"
    r"recurso\s+extraordinario.{0,60}?no.{0,20}?sentencia\s+definitiva", re.I)
RE_CAUSA_FUNDAMENTACION = re.compile(
    r"(?:no\s+cumple\s+con\s+el\s+requisito\s+de|carece\s+de|sin|"
    r"defectuosa|insuficiente|deficiente)\s+(?:la\s+)?"
    r"fundamentaci[oó]n\s+aut[oó]noma|"
    r"fundamentaci[oó]n\s+aut[oó]noma\s+(?:exigid|que\s+exige|requerid)", re.I)
RE_CAUSA_DEPOSITO = re.compile(
    r"no\s+(?:ha(?:berse)?\s+|se\s+ha\s+)?"
    r"(?:integrad|efectuad|abonad|acreditad|cumplid)\w+\s+(?:con\s+)?el\s+dep[oó]sito|"
    r"intimad\w+\s+a\s+(?:efectuar|integrar|abonar)\s+el\s+dep[oó]sito"
    r".{0,120}?(?:no\s+|sin\s+)", re.I)
RE_CAUSA_DEPOSITO_EXCL = re.compile(
    r"la\s+resoluci[oó]n\s+de\s+fs\.?\s*\d+[\s,]+que\s+desestim[oó]\b"
    r".{0,80}?no\s+haberse\s+(?:efectuad|integrad|abonad|acreditad|cumplid)\w*"
    r"\s+(?:con\s+)?el\s+dep[oó]sito", re.I)
RE_CAUSA_FUERA_TERMINO = re.compile(
    r"(?:recurso|queja|apelaci[oó]n|remedio|presentaci[oó]n)\s+\w*\s*"
    r"(?:fue\s+|ha\s+sido\s+|resulta\s+|es\s+|deducid[ao]\s+)?"
    r"(?:interpuest|deducid|present)?\w*\s+(?:de\s+manera\s+|en\s+forma\s+)?"
    r"extempor[aá]ne|"
    r"(?:recurso|queja|apelaci[oó]n)\s+\w*\s*(?:fue\s+|ha\s+sido\s+)?"
    r"(?:interpuest|deducid)\w+\s+fuera\s+del?\s+(?:plazo|t[eé]rmino)", re.I)
RE_CAUSA_FUERA_TERMINO_EXCL = re.compile(
    r"declar[oó]\s+extempor|"
    r"constancia\s+\w+\s+(?:resulta\s+|es\s+)?extempor|"
    r"(?:declaraci[oó]n\s+de\s+incompetencia|demanda)\s+\w*\s*"
    r"(?:resulta\s+|fue\s+|es\s+)?extempor", re.I)
RE_CAUSA_FUERA_TERMINO_EXCL_DISP = re.compile(
    r"(?:se\s+)?(?:desestima\w*|rechaza\w*|no\s+ha\s+lugar\s+a)\s+"
    r"(?:el\s+|la\s+|los\s+|las\s+)?(?:recurso\s+de\s+)?"
    r"(?:reposici[oó]n|revocatoria|aclaratoria)", re.I)
RE_CAUSA_REMITE_DICTAMEN = re.compile(
    r"se\s+remite|comparte\s+(?:los\s+)?(?:sus\s+)?fundamentos|"
    r"adecuado\s+tratamiento\s+en\s+el\s+dictamen|"
    r"dictamen\s+(?:de|del|de\s+la)\s+(?:se[ñn]or|se[ñn]ora)\s+[Pp]rocurador", re.I)

# ── REMITE_DICTAMEN recall-gap (H151 bucket 1) — variante del DISPOSITIVO ───────
# "de conformidad con lo dictaminado por el/la (señor/a) Procurador..." en el por_ello
# (el detector base sólo mira `co`). GATEADA en dictamen_presente igual que la base —
# NO se workaroundea el parser. Los casos con remisión real pero wc_dictamen=0
# (334_p417/345_p608) son un gap de SEGMENTACIÓN del parser (Bxxx, clusteriza en tomos
# recientes); se recuperan al arreglar la fuente, no acá. Va con verbo desestima/
# inadmisible (NO 'mal concedido' = bucket 3) y guard ∉ fondo.
RE_REMITE_DICT_DISP = re.compile(
    r"de\s+conformidad\s+con\s+lo\s+dictaminad\w+\s+por\s+(?:el\s+|la\s+)?"
    r"(?:se[ñn]or\w?\s+|se[ñn]ora\s+)?procurador", re.I)
RE_REMITE_DICT_DISP_VERBO = re.compile(
    r"se\s+desestima|desestimar\b|"
    r"(?:se\s+declara|declarar)\s+inadmisible|inadmisible\s+el\s+recurso", re.I)

RE_CAUSA_NO_RECURRIBLE = re.compile(
    r"(?:las\s+(?:decisiones|sentencias|resoluciones)\s+(?:dictadas?\s+)?"
    r"(?:de|por)\s+(?:esta\s+|la\s+)?corte|las\s+sentencias\s+del\s+tribunal)"
    r".{0,130}?no\s+son,?\s*(?:como\s+principio,?\s*)?suscepti\w*\s+de\s+"
    r"(?:recurso|reposici[oó]n|revocatoria|nulidad)", re.I)
RE_CAUSA_NO_RECURRIBLE_EXCL = re.compile(
    r"(?:se\s+resuelve\s+)?hac(?:er|e)\s+lugar\s+(?:a\s+)?(?:al?\s+|la\s+)?"
    r"(?:recurso\s+de\s+)?(?:reposici[oó]n|revocatoria)", re.I)

# ── INTERPOSICION_INCORRECTA §1.2.2 (M27) — REX ante foro equivocado ───────────
# Foro equivocado + violación NO subsanada. NO el "ante el tribunal que dictó"
# suelto (eso es la regla; FP de antecedente 339_p1417/347_p352). Anclado a
# considerando+por_ello; va al final de la cola (solo drena SIN_CAUSAL).
RE_INTERP_INCORRECTA = re.compile(
    # P1: (no) presentado/interpuesto ante el tribunal/cámara que dictó
    r"(?:no\s+fue\s+|no\s+se\s+ha\s+)(?:present|interpu|deduc)\w+\s+ante\s+(?:el\s+|la\s+)?"
    r"(?:tribunal|c[aá]mara|[oó]rgano)\s+que\s+(?:dict|pronunci)\w*"
    r"|"
    # P2: debe/debía interponerse ante el tribunal que dictó … sin que … subsane
    r"(?:debe\s+ser\s+|deb[ií]a\s+(?:ser\s+)?)(?:interpu|present|deduc)\w+\s+ante\s+(?:el\s+|la\s+)?"
    r"(?:tribunal|c[aá]mara|[oó]rgano)\s+que\s+(?:dict|pronunci)\w*[^.]{0,160}?"
    r"(?:sin\s+que|no)[^.]{0,90}?subsan",
    re.I)
# NOTA: P3 ("REX presentado ante juzgado de primera instancia") REMOVIDA — era FP:
# 348_p1130 se presentó ante el juzgado pero el holding es EXTEMPORANEIDAD (llegó
# vencido el plazo del art. 257), no foro equivocado. El hecho del foro ≠ el ground.


def causa_inadmisibilidad(admisibilidad, disposicion, considerando_text,
                          por_ello_text, dictamen_presente="", outcome=""):
    """Causa de inadmisibilidad. Gate = admisibilidad=="inadmite". "" si no es inadmite.

    disposicion: para el guard de mootness (B133: abstracta solo si NO hay verbo de mérito).
    outcome: señal primaria validada de mootness (=="abstracto"); RE_MOOT es respaldo.
    """
    if admisibilidad != "inadmite":
        return ""
    co = _prep(considerando_text)
    pe = _prep(por_ello_text)
    txt = co + " || " + pe

    # 1. holdings del DISPOSITIVO (por_ello), explícitos
    if RE_CADUCIDAD_DISP.search(pe) and not RE_CADUCIDAD_GUARD.search(txt):
        return "CADUCIDAD_INSTANCIA"
    if RE_DESISTIMIENTO.search(pe):
        return "DESISTIMIENTO"
    # mootness (admisibilidad): guard disposicion∉fondo separa puros de mixtos.
    # Señal primaria = outcome=="abstracto" (validada por el parser). El respaldo RE_MOOT
    # se ancla al DISPOSITIVO (pe), NO al considerando: un "inoficioso/abstracto" incidental
    # del considerando es antecedente, no holding (testigos 329_p4446/344_p2011/345_p423).
    if disposicion not in _DISP_FONDO and (outcome == "abstracto" or RE_MOOT.search(pe)):
        return "CUESTION_ABSTRACTA"

    # 2. fórmulas del CONSIDERANDO (280/ac4)
    if RE_280_CONSIDERANDO.search(co) or RE_280_LIBRE.search(co):
        return "ART_280"
    if (RE_ACORDADA_4_CONSIDERANDO.search(co)
            or RE_ACORDADA_4_REGLAMENTO.search(co)
            or RE_ACORDADA_4_DIRECTA.search(co)):
        return "ACORDADA_4_2007"

    # 3. cola validada H092 (inferencia sobre el fundamento) + guards antecedente
    if RE_CAUSA_SENTENCIA_DEFINITIVA.search(txt):
        return "FALTA_SENTENCIA_DEFINITIVA"
    if RE_CAUSA_FUNDAMENTACION.search(txt):
        return "FALTA_FUNDAMENTACION_AUTONOMA"
    if RE_CAUSA_DEPOSITO.search(txt) and not RE_CAUSA_DEPOSITO_EXCL.search(co):
        return "DEPOSITO_PREVIO"
    if (RE_CAUSA_FUERA_TERMINO.search(txt)
            and not RE_CAUSA_FUERA_TERMINO_EXCL.search(txt)
            and not RE_CAUSA_FUERA_TERMINO_EXCL_DISP.search(pe)):
        return "FUERA_DE_TERMINO"
    if (RE_CAUSA_NO_RECURRIBLE.search(co)
            and not RE_CAUSA_NO_RECURRIBLE_EXCL.search(pe)):
        return "RESOLUCION_NO_RECURRIBLE"

    # 4. residual
    if (RE_CAUSA_REMITE_DICTAMEN.search(co)
            and str(dictamen_presente).strip().lower() in ("true", "1", "presente")):
        return "INADMISIBLE_REMITE_DICTAMEN"
    # recall-gap H151 (bucket 1): remite-dictamen anclado al DISPOSITIVO (el detector
    # base sólo mira `co`) + verbo desestima/inadmisible, guard ∉ fondo. GATEADO en
    # dictamen_presente igual que la rama base — NO se workaroundea el parser. Los casos
    # con remisión real pero wc_dictamen=0 (334_p417/345_p608, gap de SEGMENTACIÓN del
    # parser clusterizado en tomos recientes, Bxxx) se recuperan SOLOS al arreglar la fuente.
    if (str(dictamen_presente).strip().lower() in ("true", "1", "presente")
            and disposicion not in _DISP_FONDO
            and RE_REMITE_DICT_DISP.search(pe)
            and RE_REMITE_DICT_DISP_VERBO.search(pe)):
        return "INADMISIBLE_REMITE_DICTAMEN"
    # interposición incorrecta §1.2.2 (M27) — al FINAL de la cola (post remite-dictamen,
    # v0.5): solo drena SIN_CAUSAL, nunca preempta una causal etiquetada.
    if RE_INTERP_INCORRECTA.search(txt):
        return "INTERPOSICION_INCORRECTA"
    return "INADMISIBLE_SIN_CAUSAL_EXPLICITA"
