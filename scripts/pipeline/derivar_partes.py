#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derivar_partes.py — Capa de partes (M29): deriva RECURRENTE / RECURRIDO + su ROL
procesal del epílogo editorial.

Arquitectura (REE): NO muta nada. Sidecar keyed por caso_id_canonico, left-join
1:1, mismo patrón que derivar_materia. Lee `csjn_casos_epilogo.csv` (insumo
persistido por extraer_epilogos.py), NO el .md → reproducible para Dataverse.

Doctrina (Guillermo, H154): quién recurrió a la Corte sale SOLO del marcador
`Recurso ... interpuesto por X` del epílogo; el rol (actora/demandada/penal)
viene pegado al nombre en ese mismo marcador. Es la ÚNICA fuente que ata
*quién recurrió* con *qué rol tenía*. El actor/demandado del índice/cuerpo NO
define quién apeló → esa es capa futura (tipificación + casos sin epílogo).

Se extrae la PARTE, no el letrado: se resuelve `en representación de Y` /
`asistido por` / `representada por` / `con el patrocinio` para quedarse con la
parte sustantiva.

Capa 1 (epílogo) — esta versión. Salida por caso:
  recurrente, recurrente_rol, recurrido, recurrido_rol, multi_recurrente,
  partes_capa (epilogo | sin_epilogo | no_aplica), partes_fuente.

VALIDACIÓN: el parseo se validó sobre los 7 .md de las inversiones de rol de M25
(7/7 recurrente+recurrido legibles). La corrida sobre el universo (~4345) es la
que CIERRA y expone los casos difíciles (Arriola, extradiciones, multi).
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

__version__ = "0.17"  # H165 (B): ARTÍCULO INICIAL — pasada FINAL sobre la salida que quita el artículo gramatical en MINÚSCULA del nombre de la parte ("la Administración Federal de Ingresos Públicos" -> "Administración Federal de Ingresos Públicos"; "la ANSeS" -> "ANSeS"). El extractor antepone el artículo en minúscula; NO es parte del nombre. REGLA (validada vs revisión manual de Guillermo, ~100 nombres): SOLO minúscula -> el artículo en MAYÚSCULA es nombre propio y se PRESERVA ("La Nación", "La Serenísima S.A.I.C", "La Caja ART S.A."). EXCLUYE el wrapper letrado-por-parte ("el apoderado de X" / "la defensa de X" / "el letrado de X") para NO enmascararlo: esos 43 quedan con el artículo hasta resolver su propio frente (DEUDA L184/L179 — letrado-por-parte). Va como pasada FINAL sobre `salida` (después de _refinar_nombre_desde_caratula y _registrar, antes de escribir): así NO interfiere con RE_CARATULA_SOLO_ROL (que necesita ver el artículo para detectar el rol pelado) ni con el conteo de cobertura. Cambio aditivo puro = aplicar la función al csjn_casos_partes.csv v0.15 da byte-idéntico al output del script editado. Toca 1591 celdas recurrente/recurrido (1209 rec + 425 recd, dedup 948 nombres). Re-correr/re-sellar manifest. NOTA versión: v0.16 quedó quemada en la capa de adjudicación manual CONSTRUIDA y REVERTIDA (H163) -> next limpio = v0.17. // H163 (B): CRUCE NOMBRE-DESDE-ÍNDICE — recupera el NOMBRE del recurrente cuando el rol está pero el nombre es un rol pelado ("la actora"/"el demandado") o vacío. Cruza case_name_indice "X c/ Y" anclado a 'c/' (actora=izq, demandada=der; invertido "Y (X c/)" -> X actora). Sigue Eje B: el rol lo dio el epílogo, la carátula solo nombra el lado YA señalado (0 swaps posibles por el ancla 'c/'). RESTRICCIÓN DOCTRINA: SOLO con ancla 'c/' — la convención "primer segmento del índice = actora" se midió corpus-wide y da 85,3% (464 mismatch) -> NO confiable, NO se asume el orden sin c/. Helpers _partes_desde_indice + _refinar_nombre_desde_caratula; threaded case_name_indice en el loop. 42 nombres recuperados (eyeball 42/42 lado correcto); los caratula:rol_sin_nombre con c/ pasan a recurrente_ok (nombre real). 27 sin c/ + 3 anonimizados quedan sin tocar. // H162 (B, bump 1): HANDLER DE INVERSIÓN en parse_parte — "(art)(parte)? ROL[,] NOMBRE [cola]" (formato viejo "la parte actora, X" / "el demandado X por derecho propio"). El rol procesal va ADELANTE del nombre; v0.13 lo dejaba pegado (prefijo "la demandada Ciccone S.A.", rol duplicado, bug a) o cortaba en RE_CORTE perdiendo el nombre ("la parte actora, X" -> "la", bug b). Decisión de rol con Guillermo (H162): rol PROCESAL (actora/demandada/coactora/querellante/codemandada), no por_derecho_propio (eje procesal puro; pdp queda para letrado-es-parte sin rol procesal). RE_INVERSION captura el rol del prefijo; el nombre es lo que sigue, recortado por RE_CORTE_INV (superset de RE_CORTE: agrega representaci\\w+/apoderad/conjuntamente/"con la representación"/PDP/por sí, que RE_CORTE no cubría -> 330_p4459 "con la representación letrada"). Si tras el rol viene letrado/apoderado, recursa a parse_parte para resolver la PARTE representada (344_p1835 "el querellante, Dr. Bertoncello, apoderado de la Municipalidad de Puán" -> Municipalidad). Sin nombre tras el rol -> ("", rol) [rol_sin_nombre honesto: 330_p4459, 332_p2068 anonimizada]. Corrige también 330_p1034 (v0.13 RE_REPDE agarraba "su esposa" -> ahora "Antonini Modet"/demandada). Validado: 149 inversión-con-nombre + bare "la actora" pelada; diff v0.13->v0.14 sobre epílogo v0.3 = 0 PIERDE. Tags B0xx a asignar. // H161: anclar terminadores de RE_MARK_REC y RE_MARK_NOMBRE a inicio de línea (^Traslados? / ^Tribunal(?:es)? / ^Profesional / ^Normas?) — antes \b sin ancla. Fix colisión NOMBRE-vs-FOOTER: el nombre de pila "Norma" (y "Tribunal"/"Profesional" dentro de partes como "Superior Tribunal de Justicia", "Consejo Profesional de...") truncaba el recurrente a vacío/parcial. Recupera 6 (5 ya rotos en v0.12 baseline: 329_p4524/332_p2146/333_p68/334_p223/346_p193 + 346_p811 destapado por el fallback de epílogo de extraer_epilogos v0.3) + corrige 14 (de-trunca/de-basura/abogado->parte: 329_p2614 Coriolano->Lourtau, 331_p2449 Gavernet->Lima/penal, 329_p5310 ".Tribunal"->limpio). Validado: diff v0.12->v0.13 sobre epílogo v0.3 = 6 GANA, 0 PIERDE, 14 CAMBIA (todas mejoras); 0 regresión sobre los 3806. NOTA: recurrente_ok no sube (los Norma ya contaban como ok con captura vacía); mejora de CALIDAD, no de conteo. // 0.12 H161: cleanup (deuda #4) — re.split positional maxsplit -> keyword (L204 _match_letrado_caratula + L290 _nombre_desde_causa); saca DeprecationWarning Py3.13+ (error en 3.14). csjn_casos_partes.csv BYTE-IDÉNTICO. Deuda #5 (carátula "nombre enterrado en la causa interna") CERRADA SIN MATERIAL: 5 caratula:rol_sin_nombre con case_name_cuerpo sin "X c/ Y". Hallazgo (NO tocado): 54 recurrentes con prefijo artículo+rol pegado al nombre + rol duplicado, ticket parse_parte. // 0.11 H160 (cont.): capa de CARÁTULA — recuperación de NOMBRE del rol-sin-nombre. (1) rol_causa: la carátula vieja "deducido por la actora/demandada EN LA CAUSA X c/ Y" -> el token de rol elige el lado (actora->X izq, demandada->Y der); _nombre_desde_causa. Sigue Eje B (el recurrente lo da el marcador "deducido por la actora", la causa solo provee el nombre del lado señalado). (2) name-match: carátula NORMAL "X c/ Y" (la común; "Recurso deducido por X" es la moderna) — si el nombre del letrado del epílogo coincide (>=2 tokens, apellido+nombre) con una parte -> por_derecho_propio (_match_letrado_caratula). (3) fallback solo_letrado -> derivar_de_caratula (PASO 4 también cuando el epílogo solo nombró al letrado), preservando el recurrido del traslado. Validado: 66/66 nombres del lado correcto de c/ (41 actora izq + 25 demandada der, 0 swaps) + 10 fallos enteros extraídos (Szelagowski/Gil Domínguez->pdp, Torre/Benegas/Laitán->actora con nombre, Zubiri/Castellucci). NAME_RECOVERED 43->106, solo_letrado 47->9. Tags B0xx a asignar. // 0.10 H160: capa de PARSEO Capa 2 (parse_parte). Esquema de rol MP adjudicado con Guillermo: fiscal/fiscalía/Procurador Fiscal·General -> el funcionario es la parte, mp_fiscal (MPF acusa); defensor público/oficial/general·asesor de menores·incapaces·pobres·ausentes -> funcionario es la parte, mp_defensa (MPD defiende); defensor/abogado/en-ejercicio-de-la-defensa/a-cargo-de-la-defensa de <imputado nombrado> -> el imputado es la parte, penal; apoderado/representante/en-representación de X (civil) -> X, rol vacío; por/en-causa propia·con su propio patrocinio -> el letrado es la parte, por_derecho_propio. Fix indicador letrado: Dres?\\. -> Dr(?:es)?\\. (228 "Dr." singular no entraban a la rama). Defensor del Pueblo = institución-parte (no defensa penal). Over-fire mp_defensa corregido: "a cargo de la defensa de X" caía a MPD cuando el imputado estaba nombrado (329_p1541 Pirrello->Torres/penal); patrón "de la defensa de X" le gana a RE_DEFENSA_MP. Distribución: mp_fiscal 0->81, mp_defensa 0->16, por_derecho_propio 10->44. Token mp_fiscal/mp_defensa va a CODEBOOK v2.1 (conecta M32). // 0.9 H160: Capa 0 DESHIFENIZACIÓN del epílogo (_deshifenar, chokepoint en derivar_de_epilogo). Soft-hyphen-only (U+00AD) — NO el parser._unhyphenate de prosa, que une el guión REGULAR separador de entidad y corrompe ("Estado Nacional- Ministerio" -> "NacionalMinisterio"). NO colapsa saltos estructurales (los marcadores anclan por línea, re.M). 3079/5697 epílogos afectados, 420 nombres limpios, 0 regresión. STOPGAP: el fix de producción es 1 línea soft-only en extraer_epilogos.py (ticket DEUDA). // 0.8 H160: capa de MARCADORES (terminador over-capture), ORTOGONAL a v0.7 (no toca parse_parte). DOS ediciones: (1) RE_MARK_REC terminador \bTraslados?\b (antes \bTraslado\b singular -> no frenaba ante "Traslados" plural y over-capturaba la cola del traslado: 330_p298/339_p323/345_p549, + rol leido de la cola en 340_p1775). (2) RE_MARK_TRA cierre en linea: \bRecurso\b agregado al lookahead (antes solo \bTribunal\b|$ con re.S -> se comia la linea "Recurso de queja/de hecho interpuesto por..." siguiente: 348_p1334/329_p4066). head de TRA tambien plural (Traslados? contestad) -> captura el contestador del traslado plural como recurrido (62 recuperados, 0 perdidos, 0 good->bad), honrando el principio "la cola no se lleva a representados" (Guillermo H160): recortar la cola del recurrente NO debe dejar huerfano al representado del traslado. Poblacion re-medida en disco (H160) vs ~3 del PROMPT: SET A 64 (REC plural) + SET B 52 (TRA over-capture), corrupcion REAL = 5 por nombre (329/330/339/345/348) + ROL_ONLY destapados por el diff (340_p1775 etc.). Validado por diff_partes contra repro v0.7 (sha f09979db83e1). Tags B0xx a asignar en cierre. // 0.7 H159: capa de PARSEO del clause (parse_parte/_trim_nombre). B-H159a (BUG1, "por sí" precedence): "X, por sí y en representación de Y" -> el principal es X (recurrió por sí), no el representado Y; RE_POR_SI + rama 0 en parse_parte; rol desde la cola (_rol(clause), p.ej. "actora en autos"); head con letrado ("los Dres. ... por sí") -> nombre + por_derecho_propio; head rol-pelado ("el actor", típico anonimizado) -> caratula:rol_sin_nombre (NO "el actor" como nombre; el nombre llega del epílogo/Eje A). B-H159b (BUG2, "(" colgado): _trim_nombre saca paréntesis abierto sin cerrar al final, conservando sufijos válidos ("(h)"). ADITIVO PURO: 36 cambios sobre el baseline v0.6, TODOS mejoras (17 misatribuciones "por sí" rec+recd + ~17 strip de "(" + 1 rol-pelado a rol_sin_nombre + ANTONIO 343_p1758 recuperado vía carátula); validado por diff v0.6↔v0.7 en disco: NAME_LOST 0, PARTY_CHANGED-a-peor 0, campos tocados solo {recurrente, recurrente_rol, recurrido}. NO toca marcadores (terminador Traslados -> v0.8) ni el extractor (sin_zona -> bump propio). Tags B0xx a asignar en cierre. // 0.6: H157: alternancia de rol MASCULINA + PLURAL (el actor / los actores / el demandado / las demandadas / coactor[es] / codemandad[oa]s) en RE_ROL + RE_CARATULA_SOLO_ROL + RE_CORTE, normalizada al canónico (femenino singular) en _rol (_ROL_CANON) — el NÚMERO va en multi_recurrente, no fragmenta el value-set. El feminine-singular-only dejaba rol=∅ + basura colgada ("…, actor[es] en autos") + las carátulas "el actor"/"los actores" aterrizaban como recurrente="el actor" en vez de caratula:rol_sin_nombre. Recupera rol para ~302 recurrentes (masc 242 + plural 60), limpia los nombres con trailing, y espeja el comportamiento en carátula. ADITIVO PURO: agrega masculino/plural, conserva el femenino-singular verbatim → 0 recurrente-con-nombre cambia de parte ni se pierde; validado por diff v0.5↔v0.6 en disco (eyeball H157). NOTA (ticket): en multi-recurrente, recurrente_rol guarda solo el rol del recurrente PRIMARIO (leftmost); el resto queda señalado por multi_recurrente. // 0.5: H156: PASO 4 de la cascada — fallback `case_name_cuerpo` ("Recurso ... deducido por X en la causa ...", carátula del FALLO DE LA CORTE). Es la MISMA atribución de recurso del epílogo (Eje B), en voz de la Corte, en otro campo CANÓNICO (no es el actor/demandado = Eje A, que sí violaría la doctrina). Reusa parse_parte verbatim. ADITIVO PURO sobre el residual: solo dispara cuando falla el epílogo (sin_marcador_recurso) o no hay zona (sin_zona) -> 0 regresión sobre los recurrente_ok previos. Rol pelado ("la actora"/"la demandada") -> partes_fuente="caratula:rol_sin_nombre" (rol conocido, nombre vía Eje A futuro). // 0.4: H155: cobertura reportada también sobre el universo de MÉRITO (is_merit_decision, ya en casos.csv) — recurrente_ok 88,4% sobre los 2870 de mérito vs 63,9% sobre todos los fallos; el sin_epilogo del no-mérito (art.280 etc.) es ausencia esperada, no gap. Reporte-only: derivación y CSV de salida SIN cambios vs v0.3. // 0.3: H155 fallback formato viejo "Nombre del recurrente:" (Eje B directo) cuando falla RE_MARK_REC -> partes_fuente="epilogo:nombre_recurrente"; aditivo puro sobre el residual (NO toca los 3633 ya resueltos). // 0.2: H154 marcador flexible anclado a línea (queja/ordinario de apelación/deducido/federal/plural, salta arrastre de por_ello) -> recurrente_ok 2225->3633; parse_parte resuelve letrado (por derecho propio / por <parte> / defensor de <parte> / solo_letrado). // 0.1: marcador estricto (solo formato moderno) + capa epílogo inicial.

csv.field_size_limit(10 ** 7)

# --- Rutas (robusto al cwd; overridables CLI) -------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent.parent
DEFAULT_CASOS   = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_EPILOGO = REPO_ROOT / "output" / "parser" / "csjn_casos_epilogo.csv"
DEFAULT_OUTPUT  = REPO_ROOT / "output" / "parser" / "csjn_casos_partes.csv"

REQUIRED_CASOS   = ("caso_id_canonico", "tipo_entrada", "is_merit_decision")
REQUIRED_EPILOGO = ("caso_id_canonico", "epilogo_text")

OUT_COLS = ["caso_id_canonico", "recurrente", "recurrente_rol",
            "recurrido", "recurrido_rol", "multi_recurrente",
            "partes_capa", "partes_fuente"]

# ── Gramática del epílogo ────────────────────────────────────────────────────
# marcador del recurrente (singular y plural -> multi): "Recurso(s) ...
# interpuesto(s) por ..."; cubre extraordinario / de hecho / ordinario / directo.
# marcador del recurrente, FLEXIBLE y anclado a inicio de línea (re.M): cubre
# "Recurso extraordinario [federal] interpuesto por", "Recurso de queja
# interpuesto por", "Recurso ordinario de apelación interpuesto por", "Recurso
# de hecho deducido por", plural "Recursos ... interpuestos por", y "Queja
# interpuesta por". El ancla a línea SALTA el arrastre de por_ello que la zona a
# veces incluye antes del marcador. Case-sensitive en el anclaje (Recurso/Queja
# en mayúscula = pie editorial; "recurso" minúscula = por_ello, NO matchea).
RE_MARK_REC = re.compile(
    r"^(?:Recursos?|Queja)\b[^\n]*?(?:interpuest\w+|deducid\w+)\s+por\s+"
    r"(.*?)(?=^Traslados?\b|^Tribunal(?:es)?\b|^Profesional|^Normas?\b|\Z)",
    re.S | re.M)
RE_MARK_TRA = re.compile(
    r"Traslados?\s+contestad\w+\s+por\s+(.*?)(?=\bTribunal\b|\bRecurso\b|$)", re.S | re.I)
# FALLBACK formato viejo (tomos 329-334): rótulo explícito "Nombre del
# recurrente:" cuando NO hay marcador "Recurso ... interpuesto por". Da Eje B
# directo (quién recurrió). OJO: "Nombre del actor:" / "Parte demandada:" NO van
# acá — eso es Eje A (actor/demandado), otra capa; mapearlo a recurrente
# violaría la doctrina (el actor/demandado no define quién apeló).
RE_MARK_NOMBRE = re.compile(
    r"^Nombre\s+del\s+recurrente\s*:\s*(.*?)"
    r"(?=^Nombre\s+del\b|^Tribunal(?:es)?\b|^Profesional|^Normas?\b|\Z)",
    re.S | re.M | re.I)

# PASO 4 (H156): carátula del FALLO DE LA CORTE, campo canónico case_name_cuerpo.
# "Recurso de hecho deducido por X en la causa <CaseName>" — MISMA atribución de
# recurso que el epílogo (Eje B = quién apeló), en voz de la Corte. NO es Eje A:
# no se mapea actor/demandado, se lee el marcador de recurso. El terminador es
# "en la causa/los autos" (cierre del caption); ancla case-sensitive a "Recurso/
# Queja" (la carátula siempre arranca en mayúscula).
RE_MARK_CARATULA = re.compile(
    r"^(?:Recursos?|Queja)\b[^\n]*?(?:interpuest\w+|deducid\w+)\s+por\s+"
    r"(.*?)(?=\s+en\s+(?:la\s+causa|las\s+causas|los\s+autos)\b|\bTribunal\b|\Z)",
    re.S)
# rol pelado sin nombre en la carátula ("la actora", "la demandada", "la
# recurrente"): el rol se conserva, el NOMBRE se resuelve vía Eje A (capa futura).
RE_CARATULA_SOLO_ROL = re.compile(
    r"^(?:el|la|los|las)\s+(?:parte\s+)?"
    r"(?:actor(?:a|es|as)?|demandad(?:o|a|os|as)|querellantes?|"
    r"coactor(?:a|es|as)?|codemandad(?:o|a|os|as)|recurrentes?)\s*$", re.I)

# parte vs letrado: si hay "en representación de Y", la parte es Y.
RE_REPDE = re.compile(r"\b(?:en\s+representaci[oó]n|representante(?:\s+legal)?)\s+de(?:l)?\s+(.+)$", re.I)
# B-H159: "X, por sí y en representación de Y" -> X recurrió por sí (es el principal)
RE_POR_SI = re.compile(r",?\s+\bpor\s+s[ií]\b", re.I)
# corte del nombre de la parte (donde arranca rol/representación/patrocinio):
RE_CORTE = re.compile(
    r",?\s*(?:parte\s+\w+|(?:actor(?:a|es|as)?|demandad(?:o|a|os|as)|querellantes?|"
    r"coactor(?:a|es|as)?|codemandad(?:o|a|os|as))"
    r"\s+en\s+autos|representad\w+|asistid\w+|con\s+el\s+patrocinio|"
    r"en\s+su\s+car[aá]cter|en\s+calidad|patrocinad\w+|Defensor\w*|Fiscal\b|"
    r"Procurador\w*)", re.I)
# rol procesal explícito en el clause:
# H157: alternancia masculina + PLURAL (el actor / los actores / las demandadas / …),
# normalizada al canónico (femenino singular) en _rol; el NÚMERO va en multi_recurrente,
# no en el value-set de rol.
RE_ROL   = re.compile(
    r"\b(?:parte\s+)?(actor(?:a|es|as)?|demandad(?:o|a|os|as)|querellantes?|"
    r"coactor(?:a|es|as)?|codemandad(?:o|a|os|as))\b", re.I)
_ROL_CANON = {"actor": "actora", "actores": "actora", "actoras": "actora",
              "demandado": "demandada", "demandados": "demandada", "demandadas": "demandada",
              "coactor": "coactora", "coactores": "coactora", "coactoras": "coactora",
              "codemandado": "codemandada", "codemandados": "codemandada",
              "codemandadas": "codemandada", "querellantes": "querellante"}
RE_PENAL = re.compile(
    r"\b(Fiscal|Defensor\w*|Procurador\w*|imputad\w+|Ministerio\s+P[úu]blico)\b",
    re.I)
# señal de multi-recurrente: "Recursos ... interpuestos" (plural) o "y por ..."
RE_MULTI = re.compile(
    r"Recursos\s+\w+\s+interpuestos|\by\s+por\s+(?:el\s+|la\s+|los\s+|las\s+)?[A-ZÁÉÍÓÚÑ]",
    re.I)

# H162 (bump 1): INVERSIÓN "(art)(parte)? ROL[,] NOMBRE [cola]" — el rol procesal
# precede al nombre (formato viejo: "la parte actora, X" / "el demandado X por
# derecho propio"). RE_INVERSION ancla el prefijo y captura el rol; el nombre es lo
# que sigue. RE_CORTE_INV recorta la cola (representación/patrocinio/PDP/conjunción):
# es SUPERSET de RE_CORTE — agrega representaci\w+/representant/apoderad, "con la
# representación letrada", conjuntamente con, y los marcadores de PDP (por derecho
# propio / por sí / en causa propia), que RE_CORTE no cubría.
RE_INVERSION = re.compile(
    r"^(?:el|la|los|las)\s+(?:parte\s+)?"
    r"(?P<rol>actor(?:a|es|as)?|demandad(?:o|a|os|as)|querellantes?|"
    r"coactor(?:a|es|as)?|codemandad(?:o|a|os|as))\b", re.I)
RE_ART_PELADO = re.compile(r"^(?:el|la|los|las)(?:\s+parte)?$", re.I)
RE_CORTE_INV = re.compile(
    r",?\s*(?:representad\w+|representant\w+|representaci\w+|asistid\w+|asistenci\w+|"
    r"con\s+(?:el|la|los|las|su|sus)\s+(?:patrocini\w+|representaci\w+|asistenci\w+|"
    r"defens\w+|direcci[oó]n\s+letrad\w+)|con\s+el\s+patrocinio|patrocinad\w+|"
    r"patrocinant\w+|conjuntamente\s+con|juntamente\s+con|en\s+su\s+car[aá]cter|"
    r"en\s+calidad|en\s+representaci\w+|apoderad\w+|por\s+(?:su\s+)?(?:propio\s+)?"
    r"derecho\b|derecho\s+propio\b|por\s+s[ií]\b|(?:letrad\w+\s+)?en\s+causa\s+propia\b|"
    r"causa\s+propia\b|Defensor\w*|Fiscal\b|Procurador\w*)", re.I)


def _dehifen(txt: str) -> str:
    """Pega cortes de palabra del OCR y colapsa el clause a una línea."""
    txt = txt.replace("\u00ad", "")                       # soft hyphen
    txt = re.sub(r"[-\u2010\u2011]\s*\n\s*", "", txt)     # corte de palabra
    txt = re.sub(r"\s*\n\s*", " ", txt)                   # une líneas
    return re.sub(r"\s+", " ", txt).strip()


def _trim_nombre(s: str) -> str:
    """Recorta el nombre: saca coma/espacios; quita el punto de fin de oración
    PERO conserva las iniciales punteadas (`C. J. A.`)."""
    s = s.strip().strip(",").strip()
    if s.endswith(".") and not re.search(r"\b[A-ZÁÉÍÓÚÑ]\.$", s):
        s = s[:-1].strip()
    s = re.sub(r"\s*\(\s*$", "", s).strip()   # B-H159: "(" colgado (paréntesis abierto sin cerrar)
    return s


# sub-patrones de letrado (recurrente listado como abogado, no como parte):
# Capa 2 (H160): indicador = Dr.|Dra.|Dres.|Defensor|Procurador|Asesor (artículo opcional).
RE_LETRADO  = re.compile(r"^(?:(?:el|la|los|las)\s+)?(?:Dr(?:es)?\.|Dra\.|Defensora?|Procuradora?|Asesora?)", re.I)
RE_TITULO   = re.compile(r"^(?:(?:el|la|los|las)\s+)?(?:Dr(?:es)?\.|Dra\.|Defensora?|Procuradora?|Asesora?)\s*", re.I)
RE_DPROPIO  = re.compile(r"\bpor\s+(?:su\s+|mismo\s+)?(?:propio\s+)?derecho\b|\ben\s+causa\s+propia\b|\bcon\s+su\s+propio\s+patrocinio\b", re.I)
RE_POR_X    = re.compile(r",?\s*\bpor\s+(?!derecho\s+propio|su\s+|mismo\s+|mism|s[ií]\b)(.+)$", re.I)
RE_DEF_DE   = re.compile(r"(?:abogad\w+\s+)?defensor\w*\s+(?:particular\w*\s+|oficial\s+|p[uú]blic\w+\s+)?(?:de|del)\s+(.+)$", re.I)
RE_EJERC_DEF = re.compile(r"\b(?:en\s+ejercicio\s+|a\s+cargo\s+)?de\s+la\s+defensa\s+de(?:l)?\s+(.+)$", re.I)  # "(en ejercicio/a cargo) de la defensa de X" -> X, penal
RE_PATROCINANTE = re.compile(r"\b(?:letrad\w+\s+)?patrocinante\s+de(?:l)?\s+(.+)$", re.I)  # "letrado patrocinante de X" -> X
RE_APODERADO = re.compile(r"\bapoderad\w+\b[^,]{0,25}?\bde(?:l)?\s+(.+)$", re.I)
RE_ABOGADO_DE = re.compile(r"\babogad\w+\s+(?:defensor\s+)?de(?:l)?\s+(.+)$", re.I)  # "abogado del condenado X" -> X
# MP (Ministerio Público): SIN representado nombrado, el FUNCIONARIO es la parte.
RE_FISCAL    = re.compile(r"\bfiscal(?:[ií]a)?\b|\bprocurador\w*\s+(?:general|fiscal)\b", re.I)   # MPF: acusa
RE_DEFENSA_MP = re.compile(r"\bdefensor\w*\s+(?:p[uú]blic\w+|oficial|general)\b|\bdefensor[ií]a\b|\basesor\w*\s+de\s+(?:menores|incapac\w+|pobres|ausentes)|\bpobres\s+y\s+ausentes\b", re.I)  # MPD: defiende/representa menores·incapaces·pobres·ausentes
RE_TAG_CARGO = re.compile(r",?\s*(?:en\s+su\s+car[áa]cter|en\s+representaci|titular|fiscal|defensora?|procuradora?|asesora?|subprocurador)", re.I)


def _strip_titulo(s: str) -> str:
    return RE_TITULO.sub("", s, count=1)


def _letrado_name(clause: str) -> str:
    """Nombre del funcionario del MP (es la parte): saca el título y corta en el tag
    de cargo (', fiscal' / ', defensor público' / 'en su carácter…')."""
    s = _strip_titulo(clause)
    mt = RE_TAG_CARGO.search(s)
    return _trim_nombre(s[:mt.start()] if mt else s)


# --- Capa 2 (H160): name-matching del letrado contra la carátula NORMAL "X c/ Y" ---
# La carátula "X c/ Y" es el formato comun (vs "Recurso deducido por X", el moderno que
# da el recurrente directo). Cuando el epilogo solo nombra al letrado (solo_letrado) y la
# caratula es normal, si el nombre del letrado coincide con una parte => es por_derecho_propio.
RE_LETRADO_NOMBRE = re.compile(r"^([A-ZÁÉÍÓÚÑ][\wáéíóúñ.'-]*(?:\s+(?:[A-ZÁÉÍÓÚÑ][\wáéíóúñ.'-]*|de|del|la|los|las))*)")

def _letrado_solo_name(clause: str) -> str:
    """Corre el nombre propio del letrado al inicio del clause (frena en coma/conector
    minusculo: 'con el patrocinio', 'por', etc.)."""
    m = RE_LETRADO_NOMBRE.match(_strip_titulo(clause))
    return m.group(1).strip() if m else ""

def _name_tokens(s: str) -> set:
    return {t for t in re.findall(r"[a-záéíóúñ]{3,}", s.lower())}

def _match_letrado_caratula(clause: str, caratula: str):
    """Si el nombre del letrado del clause coincide (>=2 tokens, apellido+nombre) con una
    parte de la caratula 'X c/ Y', devuelve (nombre, 'por_derecho_propio'); si no, None.
    El >=2 tokens evita falsos por apellido comun (la caratula normal nombra 'Apellido, Nombre')."""
    if not caratula or " c/ " not in caratula:
        return None
    nombre = _letrado_solo_name(clause)
    lt = _name_tokens(nombre)
    if len(lt) < 2:
        return None
    actor, resto = caratula.split(" c/ ", 1)
    demandado = re.split(r"\s+s/\s+", resto, maxsplit=1)[0]
    for parte in (actor, demandado):
        if len(lt & _name_tokens(parte)) >= 2:
            return _trim_nombre(nombre), "por_derecho_propio"
    return None


def _rol(clause: str) -> str:
    mr = RE_ROL.search(clause)
    if mr:
        r = mr.group(1).lower()
        return _ROL_CANON.get(r, r)        # H157: masculino -> canónico femenino
    return "penal" if RE_PENAL.search(clause) else ""


def _limpiar_nombre_inv(name: str) -> str:
    """Limpieza del nombre extraído por el handler de inversión: saca paréntesis
    envolvente ("(Cachambi, Santos)" -> "Cachambi, Santos"), recorta cualquier cola
    residual (RE_CORTE_INV), saca el título "Dr./Dra." y el paréntesis abierto suelto."""
    name = name.strip()
    if name.startswith("(") and name.endswith(")"):
        name = name[1:-1]
    mc = RE_CORTE_INV.search(name)
    if mc:
        name = name[:mc.start()]
    name = _trim_nombre(_strip_titulo(name))
    if name.startswith("("):
        name = name[1:].strip()
    return name


def parse_parte(clause: str) -> tuple[str, str]:
    """(nombre_parte, rol). Resuelve representación y saca el letrado, quedándose
    con la PARTE sustantiva. Si el marcador solo nombra al letrado y no a la parte
    (típico penal), devuelve ('', 'solo_letrado') — no se inventa la parte."""
    clause = clause.strip(" .")
    # H162 (bump 1): INVERSIÓN "(art)(parte)? ROL[,] NOMBRE [cola]" — el rol procesal
    # precede al nombre. Va PRIMERO: estos clauses arrancan con "el/la ROL" y v0.13 los
    # dejaba con el prefijo pegado o cortaba en RE_CORTE perdiendo el nombre. El rol sale
    # del prefijo (procesal, decisión H162); el nombre es lo que sigue. Si tras el rol va
    # un letrado/apoderado, se recursa a parse_parte para resolver la PARTE representada.
    # RESTRICCIÓN (H162): solo retorna si RECUPERA un nombre. Si es rol-only sin nombre
    # ("la actora, representada por la Dra. X" — la parte no se nombra), CAE a la lógica
    # v0.13 (no toca): la re-clasificación rol-only -> rol_sin_nombre es un bump de
    # accounting aparte (mueve recurrente_ok). Así bump 1 = recuperación de nombre, 0
    # cambio de métrica, 0 regresión.
    mi = RE_INVERSION.match(clause)
    if mi:
        rol = _ROL_CANON.get(mi.group("rol").lower(), mi.group("rol").lower())
        rest = clause[mi.end():].lstrip(" ,.")
        name = ""
        if rest and not RE_ART_PELADO.match(rest):
            if RE_LETRADO.match(rest):                       # tras el rol va letrado/apoderado -> resolver la parte
                nn, _ = parse_parte(rest)
                name = _limpiar_nombre_inv(nn)
            else:
                mc = RE_CORTE_INV.search(rest)
                name = _limpiar_nombre_inv(rest[:mc.start()] if mc else rest)
        if name and not RE_ART_PELADO.match(name):
            return name, rol
        # rol-only / nombre no recuperable -> cae a la lógica v0.13 (sin tocar)
    # 0) B-H159: "X, por sí y en representación de Y" -> el principal es X (recurrió
    #    por sí); el rol puede estar en la cola ("actora en autos") -> _rol(clause).
    msi = RE_POR_SI.search(clause); _rep0 = RE_REPDE.search(clause)
    if msi and _rep0 and msi.start() < _rep0.start():
        head = clause[:msi.start()].rstrip(" ,")
        if RE_LETRADO.match(head):                       # "los Dres. ... por sí" = parte por derecho propio
            name = _trim_nombre(_strip_titulo(head))
            return name, (_rol(clause) or "por_derecho_propio")
        mc = RE_CORTE.search(head)
        return _trim_nombre(head[:mc.start()] if mc else head), _rol(clause)
    # 1) "en representación de Y" -> Y
    rep = RE_REPDE.search(clause)
    if rep:
        return _trim_nombre(rep.group(1)), _rol(clause)
    # 2) el clause arranca con un letrado -> buscar la PARTE real + su rol (Capa 2 H160)
    if RE_LETRADO.match(clause):
        if RE_DPROPIO.search(clause):                       # el letrado ES la parte
            return _trim_nombre(_strip_titulo(RE_DPROPIO.split(clause, maxsplit=1)[0])), "por_derecho_propio"
        md = RE_DEF_DE.search(clause)                       # "defensor de <imputado nombrado>" -> X, penal
        if md and "ante" not in md.group(1)[:6].lower():
            if re.match(r"Pueblo\b", md.group(1), re.I):     # "Defensor del Pueblo" = Ombudsman, institución-parte
                inst = re.sub(r"^(?:el|la)\s+", "", clause, flags=re.I).split(",")[0]
                return _trim_nombre(inst), ""
            return _trim_nombre(md.group(1)), "penal"
        mej = RE_EJERC_DEF.search(clause)                  # "en ejercicio de la defensa de X" -> X, penal
        if mej:
            return _trim_nombre(mej.group(1)), "penal"
        mab = RE_ABOGADO_DE.search(clause)                  # "abogado del condenado/imputado X" -> X
        if mab and "ante" not in mab.group(1)[:6].lower():
            x = mab.group(1)
            es_penal = bool(re.match(r"(?:el\s+|la\s+)?(?:condenad|imputad|procesad|acusad|reo\b|encausad)", x, re.I))
            x = re.sub(r"^(?:el\s+|la\s+)?(?:condenad[oa]|imputad[oa]|procesad[oa]|acusad[oa]|encausad[oa])\s+", "", x, flags=re.I)
            return _trim_nombre(x), ("penal" if es_penal else "")
        ma = RE_APODERADO.search(clause)                   # "apoderado de X" (civil) -> X, rol vacío (no sale del epílogo)
        if ma and "ante" not in ma.group(1)[:6].lower():
            return _trim_nombre(ma.group(1)), ""
        mpa = RE_PATROCINANTE.search(clause)               # "letrado patrocinante de X" -> X
        if mpa and "ante" not in mpa.group(1)[:6].lower():
            return _trim_nombre(mpa.group(1)), _rol(clause)
        mp = RE_POR_X.search(clause)                        # "..., por <parte>" (representación) -> parte
        if mp:
            return _trim_nombre(mp.group(1)), _rol(clause)
        if RE_FISCAL.search(clause):                        # MPF (acusa): el funcionario ES la parte
            return _letrado_name(clause), "mp_fiscal"
        if RE_DEFENSA_MP.search(clause):                    # MPD (defiende): el funcionario ES la parte
            return _letrado_name(clause), "mp_defensa"
        r = _rol(clause)                                    # "el Dr. X, actor en autos" -> el letrado ES esa parte
        if r:
            return _letrado_name(clause), r
        return "", "solo_letrado"                           # letrado sin parte: marcar
    # 3) caso general: recortar en el primer marcador de rol/representación
    m = RE_CORTE.search(clause)
    return _trim_nombre(clause[:m.start()] if m else clause), _rol(clause)


def _nombre_desde_causa(caratula: str, rol: str) -> str:
    """Capa 2 (H160): carátula vieja 'deducido por la actora/demandada EN LA CAUSA
    X c/ Y' -> el token de rol elige el lado de la causa (actora->X, demandada->Y).
    Recupera el NOMBRE que 'rol-sin-nombre' dejaba pendiente. Sigue siendo Eje B: el
    recurrente se identifica por el marcador de recurso ('deducido por la actora'),
    NO se mapea actor/demandado a ciegas; la causa solo provee el nombre del lado ya
    señalado por el marcador."""
    m = re.search(r"\ben\s+(?:la\s+causa|las\s+causas|los\s+autos)\s+(.+)$", _dehifen(caratula), re.I)
    if not m or " c/ " not in m.group(1):
        return ""
    actor, resto = m.group(1).split(" c/ ", 1)
    demandado = re.split(r"\s+s/\s+", resto, maxsplit=1)[0]
    if rol in ("actora", "querellante"):
        return _trim_nombre(actor)
    if rol == "demandada":
        return _trim_nombre(demandado)
    return ""


# --- Capa carátula-índice (H163): recuperación de NOMBRE desde case_name_indice -----
def _partes_desde_indice(car: str):
    """(actora, demandada) de case_name_indice, ANCLADO a 'c/' (actora=izq, demandada=der).
    Maneja la forma limpia 'A c/ B', el invertido 'Y (X c/)' (X=actora), el sufijo 's/ ...'
    y los segmentos separados por '|'. SOLO con ancla 'c/': el orden sin c/ NO es confiable
    (validado corpus-wide: "primer segmento = actora" da 85,3%, 464 mismatch) -> no se asume.
    Devuelve None si no hay 'c/' usable."""
    if not car:
        return None
    segs = [s.strip() for s in car.split("|")]
    for s in segs:                                       # forma limpia "A c/ B"
        m = re.search(r"^(.*?)\s+c/\s+(?!\))(.+)$", s)
        if m:
            actora = _trim_nombre(m.group(1))
            dem = re.split(r"\s+s/\s+", m.group(2), maxsplit=1)[0]
            dem = _trim_nombre(re.sub(r"\s*\(.*$", "", dem))
            if actora and dem:
                return actora, dem
    for s in segs:                                       # invertido "Y (X c/)" -> X actora
        m = re.search(r"^(.*?)\s*\((.+?)\s+c/\s*\)\s*$", s)
        if m:
            dem = _trim_nombre(re.split(r"\s+s/\s+", m.group(1), maxsplit=1)[0])
            actora = _trim_nombre(m.group(2))
            if actora and dem:
                return actora, dem
    return None


def _refinar_nombre_desde_caratula(d: dict, case_name_indice: str) -> dict:
    """Cuando el recurrente quedó como rol pelado ('la actora'/'el demandado') o vacío
    con rol conocido, recupera el NOMBRE del lado correspondiente de 'X c/ Y' en
    case_name_indice. Sigue Eje B: el rol ya lo dio el epílogo; la carátula solo nombra
    el lado YA señalado (anclado a 'c/', actora=izq/demandada=der; 0 swaps posibles). NO
    inventa: si no hay 'c/' usable, no toca. Los caratula:rol_sin_nombre que recuperan
    nombre pasan a recurrente_ok (nombre real)."""
    rol = d.get("recurrente_rol", "")
    rec = (d.get("recurrente", "") or "").strip()
    if rol not in ("actora", "coactora", "querellante", "demandada", "codemandada"):
        return d
    if rec and not RE_CARATULA_SOLO_ROL.match(rec):       # ya tiene nombre real
        return d
    par = _partes_desde_indice(case_name_indice)
    if not par:
        return d
    nombre = par[0] if rol in ("actora", "coactora", "querellante") else par[1]
    if not nombre or RE_CARATULA_SOLO_ROL.match(nombre):
        return d
    d["recurrente"] = nombre
    if d["partes_fuente"] == "caratula:rol_sin_nombre":   # ahora con nombre -> recurrente_ok
        d["partes_fuente"] = "indice:nombre_rol"
    else:
        d["partes_fuente"] = d["partes_fuente"] + "+indice:nombre_rol"
    return d


def derivar_de_caratula(case_name_cuerpo: str) -> dict | None:
    """PASO 4: fallback Eje B desde la carátula del FALLO ('Recurso ... deducido
    por X en la causa ...'), campo canónico case_name_cuerpo. Devuelve el dict de
    salida o None si no hay marcador de recurso en la carátula. NO inventa partes
    desde actor/demandado: solo lee el marcador de recurso (mismo Eje B que el
    epílogo)."""
    if not case_name_cuerpo:
        return None
    m = RE_MARK_CARATULA.match(case_name_cuerpo.strip())
    if not m:
        return None
    clause = _dehifen(m.group(1))
    multi = "si" if RE_MULTI.search(clause) else "no"
    # rol pelado ("la actora"/"los actores") -> el token elige el lado de "X c/ Y"
    if RE_CARATULA_SOLO_ROL.match(clause):
        rol = _rol(clause)
        nom = _nombre_desde_causa(case_name_cuerpo, rol)
        if nom:
            return {"recurrente": nom, "recurrente_rol": rol,
                    "recurrido": "", "recurrido_rol": "", "multi_recurrente": multi,
                    "partes_capa": "caratula", "partes_fuente": "caratula:rol_causa"}
        return {"recurrente": "", "recurrente_rol": rol,
                "recurrido": "", "recurrido_rol": "", "multi_recurrente": multi,
                "partes_capa": "caratula", "partes_fuente": "caratula:rol_sin_nombre"}
    rn, rr = parse_parte(clause)
    # B-H159: si tras "por sí" el head quedó como rol pelado ("el actor") en vez de
    # un nombre (típico cuando la carátula no nombra a la parte por ser anonimizada),
    # NO dejar "el actor" como nombre -> el token elige el lado de la causa, o rol_sin_nombre.
    if RE_CARATULA_SOLO_ROL.match(rn):
        nom = _nombre_desde_causa(case_name_cuerpo, rr)
        if nom:
            return {"recurrente": nom, "recurrente_rol": rr,
                    "recurrido": "", "recurrido_rol": "", "multi_recurrente": multi,
                    "partes_capa": "caratula", "partes_fuente": "caratula:rol_causa"}
        return {"recurrente": "", "recurrente_rol": rr,
                "recurrido": "", "recurrido_rol": "", "multi_recurrente": multi,
                "partes_capa": "caratula", "partes_fuente": "caratula:rol_sin_nombre"}
    return {"recurrente": rn, "recurrente_rol": rr,
            "recurrido": "", "recurrido_rol": "", "multi_recurrente": multi,
            "partes_capa": "caratula", "partes_fuente": "caratula:recurso"}


def _deshifenar(t: str) -> str:
    """Capa 0 (H160): une palabras partidas por guión/soft-hyphen a fin de línea
    (break interno de palabra OCR), preservando el en-dash separador "–". Los saltos
    de línea NO hifenados se colapsan a espacio (son cortes reales de palabra/cláusula).
    STOPGAP en el deriver; migrar al extractor con parser._unhyphenate cuando exista."""
    # Deshifenización del EPÍLOGO = soft-hyphen-only (NO el _unhyphenate de prosa).
    # El pie editorial usa soft-hyphen (U+00AD) para cortes de palabra ("representa­\nda");
    # el guión REGULAR en el listado es SEPARADOR de entidad ("Estado Nacional- Ministerio")
    # -> unirlo corrompe (canónico daba "NacionalMinisterio"). Soft-only enhebra la aguja: [CLEAN].
    # Solo consume el whitespace tras el soft-hyphen -> NO colapsa saltos estructurales (markers anclan por línea).
    # STOPGAP: el fix real es 1 línea en extraer_epilogos.py con ESTA regla (no parser._unhyphenate).
    t = re.sub(r"(\w)\u00ad\s*\n\s*(\w)", r"\1\2", t)
    return t                                                          # NO colapsar saltos: los marcadores anclan por línea (re.M)


def derivar_de_epilogo(epilogo_text: str, case_name_cuerpo: str = "") -> dict:
    """Aplica la gramática al epílogo crudo. Devuelve campos de salida (capa 1).
    Si el epílogo no trae marcador, intenta el PASO 4 (carátula) antes de declarar
    sin_marcador."""
    epilogo_text = _deshifenar(epilogo_text)                           # capa 0: texto limpio antes de marcadores/parse
    rec = RE_MARK_REC.search(epilogo_text)
    if not rec:
        # Fallback formato viejo: rótulo "Nombre del recurrente:" (Eje B directo).
        nom = RE_MARK_NOMBRE.search(epilogo_text)
        if nom:
            nom_clause = _dehifen(nom.group(1))
            nn, nr = parse_parte(nom_clause)
            return {"recurrente": nn, "recurrente_rol": nr,
                    "recurrido": "", "recurrido_rol": "",
                    "multi_recurrente": "si" if RE_MULTI.search(nom_clause) else "no",
                    "partes_capa": "epilogo",
                    "partes_fuente": "epilogo:nombre_recurrente"}
        # PASO 4: carátula del fallo (case_name_cuerpo) antes de rendirse.
        car = derivar_de_caratula(case_name_cuerpo)
        if car:
            return car
        return {"recurrente": "", "recurrente_rol": "", "recurrido": "",
                "recurrido_rol": "", "multi_recurrente": "",
                "partes_capa": "epilogo", "partes_fuente": "sin_marcador_recurso"}
    rec_clause = _dehifen(rec.group(1))
    rn, rr = parse_parte(rec_clause)
    multi = "si" if RE_MULTI.search(rec_clause) else "no"

    tra = RE_MARK_TRA.search(epilogo_text)
    dn, dr = ("", "")
    if tra:
        dn, dr = parse_parte(_dehifen(tra.group(1)))

    # Capa 2 (H160): el epílogo solo nombró al letrado (solo_letrado) -> la parte real
    # suele vivir en la carátula del fallo (Eje B, "Recurso ... deducido por X"). Disparar
    # el PASO 4 también acá; conservar el recurrido del traslado si lo hubo. Solo override
    # si la carátula aporta nombre o rol conocido (si no, queda solo_letrado).
    if rr == "solo_letrado" and not rn.strip():
        car = derivar_de_caratula(case_name_cuerpo)
        if car and (car["recurrente"].strip() or car["partes_fuente"] == "caratula:rol_sin_nombre"):
            return {"recurrente": car["recurrente"], "recurrente_rol": car["recurrente_rol"],
                    "recurrido": dn, "recurrido_rol": dr,
                    "multi_recurrente": car["multi_recurrente"],
                    "partes_capa": "caratula",
                    "partes_fuente": car["partes_fuente"].replace("caratula:", "caratula_via_letrado:")}
        # carátula NORMAL "X c/ Y": name-match del letrado contra las partes -> por_derecho_propio
        nm = _match_letrado_caratula(rec_clause, case_name_cuerpo)
        if nm:
            return {"recurrente": nm[0], "recurrente_rol": nm[1],
                    "recurrido": dn, "recurrido_rol": dr,
                    "multi_recurrente": "no",
                    "partes_capa": "caratula", "partes_fuente": "caratula_via_letrado:nombre_match"}

    fuente = "epilogo:recurso" + ("+traslado" if tra else "")
    return {"recurrente": rn, "recurrente_rol": rr,
            "recurrido": dn, "recurrido_rol": dr,
            "multi_recurrente": multi,
            "partes_capa": "epilogo", "partes_fuente": fuente}


def _registrar(d: dict, cov: Counter, rol_rec: Counter) -> tuple[str, int]:
    """Contabiliza un d CON recurrente (epílogo/nombre/carátula). Devuelve
    (clave_cobertura, incremento_multi). Separa la carátula-rol-sin-nombre
    (rol conocido, nombre pendiente de Eje A) de recurrente_ok (con nombre)."""
    if d["partes_fuente"] == "caratula:rol_sin_nombre":
        cov["caratula_rol_sin_nombre"] += 1
        return "caratula_rol_sin_nombre", 0
    cov["recurrente_ok"] += 1
    if d["partes_fuente"] == "caratula:recurso":
        cov["_via_caratula"] += 1          # sub-cuenta auditable del paso 4
    rol_rec[d["recurrente_rol"] or "(sin rol)"] += 1
    return "recurrente_ok", (1 if d["multi_recurrente"] == "si" else 0)


# H165 (B): normalización del ARTÍCULO INICIAL del nombre de la parte.
# El extractor antepone el artículo en MINÚSCULA ("la Administración Federal...",
# "el Fisco Nacional") — basura gramatical, no parte del nombre. Se quita en una
# PASADA FINAL sobre la salida (ver _strip_articulo_inicial y el loop de cierre en
# derivar()). Discriminante: minúscula = accesorio (sacar) / MAYÚSCULA = nombre
# propio (preservar: "La Nación", "La Serenísima"). EXCLUYE el wrapper
# letrado-por-parte para no enmascararlo (DEUDA L184/L179).
_RE_ART_INI  = re.compile(r"^(?:el|la|los|las)\s+")              # minúscula-only (sin re.I: "La"/"El" mayúscula NO matchea)
_RE_ART_WRAP = re.compile(                                       # wrapper letrado-por-parte -> NO tocar
    r"^(?:el|la|los|las)\s+(?:defensa|apoderad[oa]|letrad[oa]|"
    r"defensor[a]?|patrocin|representaci[oó]n)\b", re.I)


def _strip_articulo_inicial(name: str) -> str:
    """Quita el artículo gramatical en MINÚSCULA al inicio del nombre de la parte.
    Preserva el artículo en MAYÚSCULA (nombre propio: "La Nación", "La Serenísima")
    y los wrappers letrado-por-parte ("el apoderado de X", DEUDA L184/L179)."""
    if not name or not _RE_ART_INI.match(name):    # sin artículo minúscula -> intacto
        return name
    if _RE_ART_WRAP.match(name):                   # letrado-por-parte -> intacto (otro bug)
        return name
    return _RE_ART_INI.sub("", name, count=1)


def derivar(casos_path: Path, epilogo_path: Path, output_path: Path) -> dict:
    # universo: entradas de casos.csv (para left-join 1:1)
    if not casos_path.exists():
        sys.exit(f"[FATAL] no existe: {casos_path}")
    with casos_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_CASOS if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {casos_path}: {faltan}")
        # case_name_cuerpo es el insumo del PASO 4 (carátula). Si falta, el paso 4
        # queda deshabilitado (degrada, no rompe): r.get(...) devuelve "".
        tiene_caratula = "case_name_cuerpo" in (rd.fieldnames or [])
        if not tiene_caratula:
            print("[WARN] falta 'case_name_cuerpo' en casos.csv -> PASO 4 (carátula) "
                  "DESHABILITADO; la cobertura no incluye el fallback de carátula.")
        filas = list(rd)

    # insumo: epílogos
    epi = {}
    if not epilogo_path.exists():
        sys.exit(f"[FATAL] no existe el sidecar de epílogos: {epilogo_path}\n"
                 f"        (corré antes extraer_epilogos.py)")
    with epilogo_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_EPILOGO if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {epilogo_path}: {faltan}")
        tiene_status = "epilogo_status" in (rd.fieldnames or [])
        for r in rd:
            epi[r["caso_id_canonico"]] = {
                "text": r["epilogo_text"],
                # status del extractor (sin_zona/archivo_no_encontrado/ok); si el
                # CSV no lo trae, se infiere de si hay texto.
                "status": (r["epilogo_status"] if tiene_status
                           else ("ok" if r["epilogo_text"].strip() else "sin_zona")),
            }

    salida = []
    cov = Counter()
    cov_razon = Counter()
    rol_rec = Counter()
    multi_n = 0
    merit_cov = {"1": Counter(), "0": Counter()}  # cobertura split por universo de mérito
    for r in filas:
        cid = r["caso_id_canonico"]
        if r.get("tipo_entrada") != "fallo":
            salida.append({"caso_id_canonico": cid, "recurrente": "",
                           "recurrente_rol": "", "recurrido": "",
                           "recurrido_rol": "", "multi_recurrente": "",
                           "partes_capa": "no_aplica",
                           "partes_fuente": f"tipo_entrada={r.get('tipo_entrada')}"})
            cov["no_aplica"] += 1
            continue
        merit = r.get("is_merit_decision", "")
        caratula = r.get("case_name_cuerpo", "")          # insumo PASO 4
        indice = r.get("case_name_indice", "")            # insumo cruce nombre-rol (H163)
        if cid in epi and epi[cid]["status"] == "ok":
            d = derivar_de_epilogo(epi[cid]["text"], caratula)
            d["caso_id_canonico"] = cid
            d = _refinar_nombre_desde_caratula(d, indice)  # H163: nombre desde 'X c/ Y'
            salida.append(d)
            if d["partes_fuente"] == "sin_marcador_recurso":
                cov["epilogo_sin_marcador"] += 1
                clave = "epilogo_sin_marcador"
            else:
                clave, mi = _registrar(d, cov, rol_rec)
                multi_n += mi
        else:
            # sin zona de epílogo: intentar la carátula (PASO 4) antes de rendirse.
            razon = epi[cid]["status"] if cid in epi else "no_en_epilogo_csv"
            car = derivar_de_caratula(caratula)
            if car:
                car["caso_id_canonico"] = cid
                car = _refinar_nombre_desde_caratula(car, indice)  # H163
                salida.append(car)
                clave, mi = _registrar(car, cov, rol_rec)
                multi_n += mi
            else:
                # sin epílogo aprovechable: propaga la RAZÓN (sin_zona /
                # archivo_no_encontrado / no_en_epilogo_csv), no muerte silenciosa.
                salida.append({"caso_id_canonico": cid, "recurrente": "",
                               "recurrente_rol": "", "recurrido": "",
                               "recurrido_rol": "", "multi_recurrente": "",
                               "partes_capa": "sin_epilogo", "partes_fuente": razon})
                cov["sin_epilogo"] += 1
                cov_razon[razon] += 1
                clave = "sin_epilogo"
        if merit in merit_cov:
            merit_cov[merit][clave] += 1

    # H165 (B): PASADA FINAL — normalización del artículo inicial. Va acá, después
    # de _refinar_nombre_desde_caratula y _registrar (que necesitan/leen el nombre
    # con el artículo), antes de escribir. Solo toca recurrente/recurrido.
    for d in salida:
        if d.get("recurrente"):
            d["recurrente"] = _strip_articulo_inicial(d["recurrente"])
        if d.get("recurrido"):
            d["recurrido"] = _strip_articulo_inicial(d["recurrido"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(salida)

    return {"n": len(salida), "cov": cov, "cov_razon": cov_razon,
            "rol_rec": rol_rec, "multi": multi_n, "merit_cov": merit_cov}


def _reporte(st: dict) -> None:
    cov = st["cov"]
    fallos = (cov.get("recurrente_ok", 0) + cov.get("epilogo_sin_marcador", 0)
              + cov.get("sin_epilogo", 0) + cov.get("caratula_rol_sin_nombre", 0))
    print(f"\n  derivar_partes v{__version__}")
    print(f"  filas escritas: {st['n']}  (fallos: {fallos})")
    print("\n  === cobertura (capa 1 epílogo + paso 4 carátula) ===")
    for k in ["recurrente_ok", "caratula_rol_sin_nombre", "epilogo_sin_marcador",
              "sin_epilogo", "no_aplica"]:
        v = cov.get(k, 0)
        base = fallos if k != "no_aplica" else st["n"]
        pct = f"({100*v/base:5.1f}%)" if base else ""
        print(f"    {k:24s} {v:5d}  {pct}")
    print(f"    └─ de recurrente_ok, vía carátula (paso 4): {cov.get('_via_caratula', 0)}")
    print(f"  multi_recurrente (flag):  {st['multi']}")
    mc = st.get("merit_cov")
    if mc:
        for universo, lbl in [("1", "MÉRITO (universo SCDB)"), ("0", "no-mérito")]:
            c = mc.get(universo, Counter())
            tot = sum(c.values())
            if not tot:
                continue
            print(f"\n  === cobertura sobre {lbl}: {tot} fallos ===")
            for k in ["recurrente_ok", "caratula_rol_sin_nombre",
                      "epilogo_sin_marcador", "sin_epilogo"]:
                v = c.get(k, 0)
                print(f"    {k:24s} {v:5d}  ({100*v/tot:5.1f}%)")
    if st["cov_razon"]:
        print("\n  === sin_epilogo, por razón (auditable) ===")
        for razon, v in st["cov_razon"].most_common():
            print(f"    {razon:22s} {v:5d}")
    print("\n  === rol del recurrente (sobre recurrente_ok) ===")
    for rol, v in st["rol_rec"].most_common():
        print(f"    {rol:14s} {v:5d}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Deriva recurrente/recurrido + rol del epílogo (capa 1).")
    ap.add_argument("--casos", type=Path, default=DEFAULT_CASOS)
    ap.add_argument("--epilogo", type=Path, default=DEFAULT_EPILOGO)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args(argv)

    st = derivar(args.casos, args.epilogo, args.output)
    _reporte(st)
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
