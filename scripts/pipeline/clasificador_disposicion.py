#!/usr/bin/env python3
"""
clasificador_disposicion.py — fuente ÚNICA de la lógica de disposición (corpus-csjn).
=====================================================================================
Regex VERBATIM del PoC v3 (H118), congeladas. Importado por:
  - scripts/validacion/build_m20.py          (validación: genera la clave)
  - scripts/pipeline/derivar_recursos.py     (producción: csjn_casos_recursos.csv)
Una sola copia => el 0,857 blind describe exactamente lo que se shippea. Sin drift.

Garantía: corrido sobre los mismos textos, reproduce la clave blind 300/300
(disposición, reenvía, parte_ganadora). NO modificar sin re-validar contra held-out.

v1.01 — norm() ahora des-hifena el soft-hyphen (\u00ad) de fin de línea del OCR
        ('re­ curso' -> 'recurso'), que antes quedaba como 're curso' y rompía el
        match del verbo dispositivo. Cambio GENERAL (no a medida del gold). Validado
        en disco vs gold: disposición 0,887 -> 0,930, 0 regresiones, 6 mejoras.
        REQUIERE regenerar la clave (build_m20) y re-sellar antes de cerrar.
"""
import re
__version__ = "1.15"

# v1.15 (B143 — H177). Guard del GATE (patrón B119/B131/B138, verbo intacto):
# «nulidad de todo lo actuado» = nulidad DE ACTUACIONES (vicio in procedendo,
# retrotrae el trámite aunque barra la sentencia) = procesal, NO revisión de fondo
# — criterio de codebook fijado en H176 (nulidad de sentencia [art. 253 CPCCN] =
# fondo · nulidad de actuaciones = procesal; Pereyra 348_p1352 / Rivera 333_p1152).
# Señal = RE_NULIDAD_ACTUADO (VERBATIM del alt window-free 1º de la entrada
# `nulidad` de DISP — fuente conceptual única, dedup pendiente igual que
# RE_NULIDAD_CONCESION) anclada a disp=="nulidad" (deja fuera por construcción a
# 333_p405, disp=revoca). EXCEPCIÓN sustitutiva RE_ABSOLUCION: «nulidad + se
# absuelve» (art. 16 2ª parte ley 48) ES fondo — testigo 330_p399 (López),
# adjudicado H176/H177; co-ocurrencia alt∩absolución medida corpus-wide = solo
# {330_p399, 333_p405}. Los 16 del alt LEÍDOS contra el .md en H177 (extraídos a
# scripts/diagnostico/H177/) y adjudicados caso a caso: 15 FP del gate (6 in-forma-
# pauperis/asistencia ineficaz: 329_p1794, 330_p487, 330_p4925, 330_p5052,
# 333_p1671, 339_p656 · 4 juzgado incompetente/avocación: 330_p1169, 334_p1458,
# 337_p97, 345_p191 · 1 inexistencia de caso art. 116: 332_p1823 [sin controversia
# = umbral, coherente con in-limine B141 y con «falta de acción» de EXCEP] · 4
# retrotraídos por vicio de trámite: 344_p163, 344_p1259, 347_p327, 348_p1152)
# + 1 acierto (330_p399). Solapamiento con gold n300 = 0 (verificado H177) → el
# guard no re-mapea codificación humana. PoC read-only corpus-wide: flip-set
# EXACTO = los 15, si→no, 0 no→si; gate=si 2950→2935; divergencia M39 216→227
# (+13 coincide-en-error expuestos lado parser [los 2 restantes, 347_p327 y
# 348_p1152, ya eran divergentes con is_merit=0 y SALEN] — residuo para el paso 3
# de M39, mismo estatus que los 9 de B140b). disposicion() INTACTA (el alt sigue
# rindiendo caseDisposition=nulidad, correcto como verbo) → blind 0,930
# byte-idéntico por construcción (verificar igual con build_m20, candado).
# parte_ganadora=recurrente_gana QUEDA en los 15 (deriva del verbo lockeado,
# residual estilo B138). Parser 0 ripple (es_de_fondo/outcome intactos) →
# check_regresion [CLEAN] por construcción; re-derivar recursos + re-sellar
# manifest. Verificador bimodal: scripts/diagnostico/H177/poc_b143_guard.py.
# + Fix docstring L6: path de build_m20 scripts/diagnostico/H120 → scripts/validacion (stale).

# v1.14 (B136 vocabulario — H176; hallado por la re-estratificación B139). _DEM_FONDO
# gana «impugnación»: la originaria contencioso-administrativa resuelve la IMPUGNACIÓN
# del acto, sinónimo funcional de demanda/pretensión que el split de RE_DEMANDA no
# cubría. Testigos GEMELOS (San Juan c/ AFIP-DGI, mismo Convenio de Transferencia
# previsional), ambos LEÍDOS H176 contra el .md, ambos mérito real: 330_p1927
# («Rechazar la impugnación … y, en consecuencia, confirmar el acto administrativo»,
# rama reject, INADM=False en el considerando) y 330_p2478 («Hacer lugar parcialmente
# a la impugnación … dejar sin efecto la resolución 297/96», rama grant; su INADM=True
# es narrativa de mérito rubro-por-rubro, no cierre de umbral — adjudicado por lectura).
# Los dos eran coincide-en-error (is_merit=0 ∧ gate=no) INVISIBLES a la divergencia M39.
# Cardinalidad corpus-wide (PoC read-only, 589 originarias): 3 co-ocurrencias
# verbo+impugnación → flip-set EXACTO = {330_p1927, 330_p2478}; ancla no-op 331_p2769
# (ya si/si por otra ruta, debe quedar idéntica). disposicion() INTACTA: RE_DEMANDA es
# regex aparte y NO consume _DEM_FONDO → clave blind 0,930 byte-idéntica por
# construcción (verificar igual con build_m20, candado). Ripple (contrato completo,
# lección B140b): is_merit 3008→3010 (el parser importa es_de_fondo) + denormalización
# en votos → RE-GOLDEN consciente (diff exacto = los 2 IDs); es_revision_fondo
# 2948→2950 → re-derivar recursos + re-sellar manifest. Divergencia M39 = 216 SIN
# CAMBIO (ambas capas flipean juntas — el fix es tan invisible al instrumento como lo
# era el bug). parte_ganadora / admisibilidad / causa: 0 ripple (consumen
# disposicion/outcome, intactos). Verificador bimodal con candado de versión:
# scripts/diagnostico/H176/poc_b136_impugnacion.py. El κ de es_de_fondo sigue
# pendiente (M43) y validará esta versión.

# v1.13 (B140b — H175). Ensancha RE_NULIDAD_CONCESION (pre-cascada B131, usada
# por disposicion() L~): alternativa NUEVA que cubre la fórmula literal «nulidad
# (parcial) de la resolución/decisión/auto … conced… … recurso» SIN exigir
# «extraordinario» — el gap de ventana registrado en H170 (DEUDA L4656, testigo
# 343_p2098 con referencia intercalada) y cerrado en cardinalidad en H171: 10
# casos, 9 invisibles a la divergencia (outcome acompaña), fórmula «por la que
# se concedió el recurso»; testigo 329_p120 leído H171 (Olivero y Rodríguez:
# nulidad de concesión por auto no fundado — vía pura, 0 fondo). FLIP DE VERBO
# (a diferencia del guard B138): nulidad → nulidad_concesion en los 10, arrastra
# parte_ganadora recurrente_gana → no_aplica (la corrección buscada: los 10
# inflaban is_merit/gate/parte) y gate si → no (nulidad_concesion ∉ _FONDO).
# PoC read-only corpus-wide (poc_b140b_flips.py): flip-set EXACTO = los 10 IDs
# de DEUDA, 0 hits extra fuera de la familia. Divergencia M39 SUBE 208 → 216 y
# es correcto: los 9 invisibles tienen is_merit=1 del parser (outcome=nulidad,
# copia propia de la regex en parser L470 NO tocada — orden M39 lockeado) y
# quedan expuestos como residuo lado parser hasta el paso 3 (is_merit derivado
# del clasificador). Paccagnini (2098, abstracto) converge. Blind 0,930: exige
# verificación gold n300 en disco (build_m20) antes de sellar — los 10 IDs los
# lista el PoC.

# v1.12 (B138 — H175). Guard del GATE (patrón B119/B131, verbo intacto): cuando
# disp=confirma llegó por el FALLBACK RE_RECHAZA_REC (ningún patrón de DISP matchea
# el pe) Y el objeto rechazado es INEQUÍVOCAMENTE de acceso (RE_RECHAZA_ACCESO,
# lista POSITIVA: queja / recurso de hecho / recurso de queja / reposición) →
# es_revision_fondo=no. Rechazar la queja o el recurso de hecho es negarse a abrir
# la instancia por definición; la reposición es procesal. DISEÑO POST-TESTIGOS
# (H175): la primera versión del guard (lista negativa: suprimir todo salvo
# ordinario) se DESCARTÓ antes de instalarse porque la clase «se rechaza el REX»
# resultó HETEROGÉNEA al leerla contra el .md — 330_p3801 (Minaglia, Fallos
# 330:3801) es dispositivo MIXTO con fondo real («bien concedido» + «ingresando al
# fondo del agravio», rechaza en el mérito ≡ confirma; evidencia B142) y 331_p2567
# (Espejo Sola) trata un agravio en sustancia; vs 330_p1205 / 348_p747 / 331_p2621
# = acceso puro (280, mal concedido, insuficiencia). La lista positiva deja los REX
# y el «recurso» genérico FUERA del guard (gate=si se sostiene): 3 FP conocidos
# quedan documentados en B138, 0 FN fabricados, y el default ante objeto desconocido
# en corpus futuro es NO tocar. Respeta H172 (ordinarios 334_p1302/342_p1524 quedan
# si) y H171-05 (por objeto textual, NO por via_recurso — FP conocido de la columna:
# 330_p826 via=ordinario siendo queja pura). PoC read-only corpus-wide: flip-set
# EXACTO = 11 (9 quejas + 1 recurso de hecho + 1 reposición), si→no, 0 no→si;
# divergencia M39 219→208; is_merit del parser 0 ripple por construcción (importa
# es_de_fondo, intacto). disposicion() intacta (blind 0,930 en pie). Residuales:
# parte_ganadora=recurrente_pierde queda en los 11 (deriva del verbo lockeado) y
# los FP del fallback que el guard NO toca quedan como límite documentado — 4
# leídos/adjudicados H175: 330_p1205 (280 en una línea), 348_p747 (dictamen «mal
# concedido»), 331_p2621 (insuficiencia, remisión a dictamen), 330_p4891 (reposición
# contra desestimación de queja, pero el pe dice «el recurso de fs. 34» pelado —
# objeto genérico ambiguo, no entra a la lista positiva a propósito). Su eventual
# tratamiento exige señal de considerando y roza B142 (mixtos), fuera del alcance.

# v1.11 (B141 acople — H174). Guard IN LIMINE en la rama reject de es_de_fondo():
# el rechazo/desestimación «in limine» de la demanda es de UMBRAL (falta de caso
# justiciable, pronunciamiento teórico vedado — Fallos 325:474), no de mérito.
# Testigo adjudicado: 330_p3777 (San Luis c/ Nación, cons. 5º-8º) — con el por_ello
# COMPLETO (post-fix _barrer de B141) el reject matchearía «Rechazar in limine la
# demanda» e INADM no dispara (sus patrones cubren instancia/competencia ajena, no
# falta-de-caso) → sin guard, el fix de _barrer fabricaba 1 FP de mérito. Ventana =
# m.group(0) (mismo estilo que EXCEP): medido en disco, 5 co-ocurrencias reject∩
# in-limine en las 589 originarias, todas dentro del grupo (ventana+20 no agrega);
# cubre comillas OCR («rechazar “in limine” la demanda», 337_p627). A/B corpus-wide
# sobre textos canónicos actuales: 0 flips (no-op puro — pre-emptivo del fix de
# _barrer; además endurece 5 'no' correctos que hoy dependían de INADM: 329_p1675,
# 329_p2754, 330_p3109, 331_p1364, 337_p627). Testigos con texto completo: 3777
# True→False (correcto), 329_p3894 y 341_p1148 siguen True. Outputs byte-idénticos
# esperados → re-golden [CLEAN] por construcción; manifest re-sellar (CLF_VER en
# provenance). Residual documentado: falta-de-caso SIN la fórmula «in limine» no
# se guardea (0 casos vistos; evaluar patrón en INADM si aparece testigo).

# v1.10 (B136 — H169). Agrega es_de_fondo(considerando, por_ello): detector de MÉRITO
# para la originaria, que NO tiene verbos de apelación (confirma/revoca/deja_sin_efecto)
# sino que resuelve la demanda directamente. Vocabulario = split de RE_DEMANDA (hac\w+
# lugar|admit\w+ = grant ; rechaz\w+|desestim\w+ = reject) con {0,30} de interposición,
# reusa norm() (\xad-aware) + los guards de negación (B107) y excepción/falta-de. Extras
# no-demanda (inconstitucionalidad / nulidad de decreto-acto / condena / ejecución).
# ASIMETRÍA: grant = fondo siempre; reject = fondo SALVO que el considerando funde
# inadmisibilidad (RE_FONDO_INADM). es_revision_fondo() gana el parámetro `considerando`
# (default "") y su branch originaria pasa de hard-`no` (bug B136) a es_de_fondo. El MISMO
# detector lo importa el parser para is_merit (from clasificador_disposicion import
# es_de_fondo, L~57) → is_merit_decision y es_revision_fondo COINCIDEN en la originaria.
# Medido en disco (546 originarias): 133 de fondo (grant 89 + reject 44, precisión limpia,
# 0 FP en la rama reject). Corpus: is_merit 2870→3003, es_revision_fondo 2816→2949, 0
# cambios en no-originarias (ambos ejes). NO toca disposicion() (verbo congelado, blind
# 0,930 en pie). REQUIERE re-golden del parser (ripple is_merit + denormalización en votos)
# + re-derivar recursos + re-sellar manifest + κ ciego nuevo de es_de_fondo (pendiente).

# v1.09 (Bxxx — Ruta 1 partyWinning). parte_ganadora_regla: `modifica` ENTRA al grupo
# fondo-favorable (-> recurrente_gana), junto a revoca/deja_sin_efecto/nulidad/grant_remand.
# ELIMINA el valor `parcial`: SCDB partyWinning es petitioner-centric BINARIO (partial
# victory = win) y el gold humano coincide (0 parcial). Blindaje: no reformatio in pejus
# (el recurrente no sale peor de su propio recurso -> toda modificación que obtiene es
# favorable o neutra) + convención de recurrente-de-referencia, ya transversal a
# revoca/deja/confirma. NO toca disposicion() ni las regex (verbo intacto, κ disposición
# 0,912 sin cambio). 3 casos en disco (329_p2864/331_p1282/331_p1890, los únicos modifica,
# multi_recurso=no), validados a mano sobre el texto -> gana. PoC κ-parte: 0,784 -> 0,784
# (los 3 NO caen en el gold n=134; el cap son las 7 inversiones de rol, no los parciales).
# Eje queda binario puro {recurrente_gana, recurrente_pierde, no_aplica}. La firma NO cambia
# -> call site de derivar_recursos (.map) intacto. REQUIERE regenerar build_m20 (re-validar
# held-out) + re-derivar recursos.csv + re-sellar manifest.

# v1.08 (M26 Fase 2 — rewiring del gate). NO toca disposicion() (caseDisposition = el
# verbo, κ disposición 0,912 intacto). Agrega es_revision_fondo() = el GATE de revisión
# de fondo derivado de caseDisposition + guards B119 (competencia/inoficioso dispositivos
# = procedimiento, no fondo) + lookahead B129 (no dispara en "resultando inoficioso que
# dictamine el PGN"). Los guards van en el GATE, NO en el verbo: un fallo de competencia
# que revoca para sentar competencia conserva caseDisposition=revoca (lo que codea el gold)
# pero es_revision_fondo=no. Reemplaza la copia perezosa de derivar_recursos.
# Validado n300: gate 0,933→0,946 (supera al publicado), disposición 0,912 (sin cambio),
# 0 re-map del gold, 0 contaminación. Corpus: is_merit 2870→2816. RE_DISP_COMPETENCIA
# verbatim parser L488; RE_DISP_INOFICIOSO = parser L497 + lookahead B129. REQUIERE
# regenerar recursos + re-sellar. ABSORBE B129 (deja de ser commit standalone diferido).

# v1.07 (B131, M26 Fase 2): pre-cascada nulidad_concesion (RE_NULIDAD_CONCESION,
# verbatim del parser L470) — nulidad/deja del auto de concesión o denegatoria del
# REX = procedimiento, no fondo. Saca 30 casos de fondo (22 nulidad + 8 deja_sin_efecto).
# Validado vs gold n300: los 4 tocados tienen es_revision_fondo=no → 0 regresión;
# κ-gate del de-interleave 0,887→0,906 (+0,019). REQUIERE regenerar recursos + re-sellar.

# v1.06 (H139): RE_RUNNING_HEAD case-sensitive (saca re.I), sync con parser L218.
# El banner es MAYÚSCULAS; "Corte Suprema de Justicia de la Nación" en mixta es CUERPO,
# no header. Verificado en disco: por_ello 467/467 mayúsculas → disposición byte-idéntica
# (no-op sobre el output). Habilita limpiar el banner del considerando para materia (frente aparte).
# v1.05 (M21 Fase 2 en el submódulo): banner editorial (terna 'número FALLOS… número' /
# '…NACIÓN número') enmascarado en norm(). RE_RUNNING_HEAD VERBATIM del parser (L215) —
# fuente única, no un regex paralelo (el RE_BANNER del validador es el drift que evitamos;
# dedup futuro a módulo compartido). Recupera los INTERPOLADOS (banner mid-text que parte el
# OBJ → al sacarlo se re-pega el verbo de fondo): 330_p380/330_p960 → deja_sin_efecto,
# 333_p1951 → revoca, 344_p1444 → deja_sin_efecto. Los TRUNCADOS (verbo físicamente cortado)
# NO se recuperan acá: viven en el parser (por_ello_cortado los marca legítimamente).
RE_RUNNING_HEAD = re.compile(
    r"\d{1,6}\s+(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s+\d{1,6}"
    r"|\d{1,6}\s+(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\b"
    r"|\b(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s+\d{1,6}")  # H139: sin re.I → case-sensitive

def norm(s):
    s = s or ""
    s = re.sub(r"(\w)\u00ad\s*(\w)", r"\1\2", s)   # des-hifena el soft-hyphen de fin de linea ('re­ curso' -> 'recurso')
    s = re.sub(r"\u00ad", "", s)                    # limpia soft-hyphens sueltos restantes
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)         # des-hifena el guion normal
    s = RE_RUNNING_HEAD.sub(" ", s)                 # v1.05: enmascara el banner editorial (terna) -> recupera interpolados
    return re.sub(r"\s+", " ", s).strip()

OBJ  = r"(?:la|las|el|los)\s+(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto)s?\b"
# v1.03 (B127): OBJ con plural -es ('resoluciones'/'decisiones', que 's?' no cubria).
# Aplicado SOLO en revoca/deja_sin_efecto (verbos de revocacion limpia). NO en
# nulidad/invalidez/confirma: ahi el -es arrastra FP (nulidad-de-concesion, originarias,
# 'confirmar ... en cuanto a la nulidad de las resoluciones'). Verificado en disco (5890):
# 6 flips, 0 regresiones, gold 0/300 tocado. El frente del banner (por_ello truncado) es M21, no esto.
OBJ_es = r"(?:la|las|el|los)\s+(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto)(?:es|s)?\b"
OBJX = r"(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto|sanci[oó]n|pena|condena|multa)s?\b"
W = r"[^.;]{0,55}"
DISP = [
    ("revoca",  re.compile(rf"\b(?:se\s+)?revoca(?:n)?\b{W}{OBJ_es}|\brevocar\b{W}{OBJ_es}|revoc[áa]ndose{W}{OBJ_es}", re.I)),
    ("deja_sin_efecto", re.compile(
        rf"\bdeja(?:r|se|n)?\s+sin\s+efecto\b{W}{OBJ_es}|\bdej[áa]ndose\s+sin\s+efecto\b{W}?{OBJ_es}|"
        rf"\bdejando\s+sin\s+efecto\b{W}?{OBJ_es}|\bd[ée]jase\s+sin\s+efecto\b{W}?{OBJ_es}|\bdeje\s+sin\s+efecto\b{W}?{OBJ_es}", re.I)),
    ("nulidad", re.compile(
        rf"\bnulidad\s+de\s+todo\s+lo\s+actuado\b|\b(?:se\s+)?declara\s+(?:la\s+)?nul[ao]s?\b|\bnulidad\b{W}{OBJ}|"
        rf"\b(?:se\s+)?anula\b{W}{OBJ}|\binvalidez\b{W}?{OBJ}|\bdeclara\s+(?:la\s+)?inv[áa]lid", re.I)),
    ("confirma", re.compile(rf"\b(?:se\s+)?confirma(?:n)?\b{W}{OBJ}|\bconfirmar\b{W}{OBJ}|confirm[áa]ndose{W}{OBJ}", re.I)),
    ("modifica", re.compile(rf"\b(?:se\s+)?modifica(?:n)?\b{W}{OBJX}|\bsustituir\b{W}{OBJX}|\b(?:se\s+)?sustituye\b{W}{OBJX}", re.I)),
]
RE_RECHAZA_REC = re.compile(r"\b(?:se\s+)?rechaza(?:n)?\b[^.;]{0,40}\b(?:recurso|queja)\b", re.I)
# v1.12 (B138): objetos INEQUÍVOCOS de acceso (lista POSITIVA) — mismo esqueleto
# que RE_RECHAZA_REC con el objeto especializado. Usado SOLO por el guard del gate
# (es_revision_fondo); disposicion() no lo ve. Por objeto textual, NO via_recurso.
RE_RECHAZA_ACCESO = re.compile(
    r"\b(?:se\s+)?rechaza(?:n)?\b[^.;]{0,40}"
    r"\b(?:quejas?|recursos?\s+de\s+(?:hecho|queja|reposici[oó]n))\b", re.I)
# v1.15 (B143): señal del guard nulidad-de-actuaciones. VERBATIM del alt 1º de la
# entrada `nulidad` de DISP (fuente conceptual única; dedup pendiente). Usado SOLO
# por es_revision_fondo(); disposicion() no lo consulta (el verbo queda nulidad).
RE_NULIDAD_ACTUADO = re.compile(r"\bnulidad\s+de\s+todo\s+lo\s+actuado\b", re.I)
# v1.15 (B143): excepción sustitutiva — nulidad + absolución (art. 16 2ª parte ley 48)
# = fondo. Testigo 330_p399 (López).
RE_ABSOLUCION = re.compile(r"\babsuelv\w+|\babsolv\w+|\babsoluci[oó]n\b", re.I)
RE_REMAND = re.compile(r"vuelvan?\s+los\s+autos|dicte\s+(?:un\s+)?nuev[ao]|nuevo\s+(?:pronunciamiento|fallo|sentencia)", re.I)
RE_COMPET = re.compile(r"\bresulta\s+competente\b|\bdeclara\s+(?:la\s+)?(?:in)?competencia\b|\bdeber[áa]\s+entender\b|\bdeclara\s+competente\b", re.I)
RE_DEMANDA = re.compile(r"\b(?:hac\w+\s+lugar|rechaz\w+|admit\w+|desestim\w+)\b[^.;]{0,30}\b(?:demanda|acci[oó]n|pretensi[oó]n)\b", re.I)
RE_PROCESAL = re.compile(r"\bcaducidad\b|\breposici[oó]n\b|\baclaratoria\b|\bhonorarios\b|\bcitaci[oó]n\b|\bterceros?\b|"
                         r"\bsuspensi[oó]n\b|\brecusaci[oó]n\b|\bexcusaci[oó]n\b|\bcautelar\b|\bbeneficio\s+de\s+litigar\b|"
                         r"\bintimaci[oó]n\b|\bavocaci[oó]n\b|mal\s+(?:denegad|concedid)|\bexcepci[oó]n\b|\bdefecto\s+legal\b|"
                         r"\bfalta\s+de\s+legitimaci[oó]n\b", re.I)
RE_HEADER = re.compile(r"(?:DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N|FALLOS\s+DE\s+LA\s+CORTE)\s*\d*\s*$", re.I)
RE_GRANT = re.compile(r"hace\s+lugar|procedente", re.I)
# B131 (M26 Fase 2): nulidad/dejar sin efecto del AUTO DE CONCESIÓN o de la
# denegatoria del REX = ataca la VÍA (procedimiento), no el fondo. VERBATIM del
# parser.py L470 (RE_DISP_NULIDAD_CONCESION, B119, recall-safe n300=0 sobre gold=sí)
# — fuente conceptual única; dedup a módulo compartido pendiente (igual que RE_RUNNING_HEAD v1.05).
RE_NULIDAD_CONCESION = re.compile(
    r"auto\s+de\s+concesi[oó]n\s+del\s+recurso\s+extraordinario|"
    r"nulidad\s+de\s+(?:la\s+resoluci[oó]n|las\s+resoluciones)\b"
    r".{0,90}?conced\w+\b.{0,30}?recursos?\s+extraordinarios?|"
    r"(?:resoluci[oó]n|auto)\s+\w*\s*que\s+conced\w+\s+(?:el|los)\s+recursos?\s+extraordinarios?|"
    r"resoluci[oó]n\s+denegatoria\s+del\s+remedio\s+federal|"
    r"denegatoria\s+del\s+remedio\s+federal|"
    # v1.13 (B140b): «nulidad (parcial) de la resolución/decisión/auto …
    # conced… … recurso» SIN exigir «extraordinario» — cubre la conectiva
    # «por la que se concedió» (9 invisibles) y la intercalada de 343_p2098.
    r"nulidad\s+(?:parcial\s+)?de(?:l|\s+la|\s+las)?\s+"
    r"(?:resoluci[oó]n(?:es)?|decisi[oó]n(?:es)?|autos?)\b"
    r".{0,90}?conced\w+\b.{0,30}?recursos?\b", re.I)

# v1.08: guards del GATE (NO del verbo). VERBATIM del parser classify_outcome (B119):
# RE_DISP_COMPETENCIA L488, RE_DISP_INOFICIOSO L497 — competencia/inoficioso DISPOSITIVOS
# = procedimiento, no fondo. El alt-2 de inoficioso lleva el lookahead de B129 para NO
# disparar en el aside "resultando inoficioso que dictamine el PGN" (el fallo decide el
# fondo igual). Usados SOLO en es_revision_fondo(); disposicion() (el verbo) no los ve.
RE_DISP_COMPETENCIA = re.compile(
    r"resulta\s+competente\s+para\s+conocer|"
    r"tomar\s+intervenci[oó]n\s+en\s+el\s+conflicto|"
    r"conflicto\s+(?:positivo|negativo)\s+de\s+competencia", re.I)
RE_DISP_INOFICIOSO = re.compile(
    r"inoficioso\s+(?:emitir|expedirse|(?:un\s+)?pronunciamiento|pronunciarse)|"
    r"(?:deviene|torna\w*|result\w+)\s+(?:inoficioso|abstract\w+)(?![^.]{0,40}(?:dictamin|procurador))|"
    r"declara\w*\s+abstract\w+\s+la\s+cuesti[oó]n", re.I)

def disposicion(pe):
    """(label, reenvia_bool) a partir del por_ello_text."""
    pe = norm(pe)
    remand = bool(RE_REMAND.search(pe))
    if RE_NULIDAD_CONCESION.search(pe):           # B131: nulidad/deja del auto de concesión = vía, no fondo
        return "nulidad_concesion", remand
    enc = [lab for lab, pat in DISP if pat.search(pe)]
    if enc: return enc[0], remand
    if RE_RECHAZA_REC.search(pe): return "confirma", remand
    if RE_COMPET.search(pe):  return "no_revision_competencia", remand
    if RE_DEMANDA.search(pe): return "no_revision_demanda", remand
    if RE_PROCESAL.search(pe): return "no_revision_procesal", remand
    if RE_HEADER.search(pe):  return "por_ello_cortado", remand
    if RE_GRANT.search(pe) and remand: return "grant_remand_implicito", remand
    return "no_fondo", remand   # v1.02: ex 'sin_disposicion_legible'. El por_ello es legible; no hay disposicion de FONDO (competencia/liquidacion/desercion/queja/honorarios). El gold concuerda: 88/89 vacio.

def parte_ganadora_regla(disp):
    # v1.09 (Ruta 1): `modifica` -> recurrente_gana (SCDB binario; no reformatio in pejus).
    # Eliminado el valor `parcial` (fuera del esquema SCDB partyWinning).
    if disp in ("revoca", "deja_sin_efecto", "nulidad", "modifica", "grant_remand_implicito"): return "recurrente_gana"
    if disp == "confirma": return "recurrente_pierde"
    return "no_aplica"

_FONDO = {"revoca", "deja_sin_efecto", "nulidad", "confirma", "modifica", "grant_remand_implicito"}

# ── B136 (H169): detector de MÉRITO de la ORIGINARIA ─────────────────────────
# La originaria resuelve la demanda directamente (no revisa un inferior): sus
# verbos NO son confirma/revoca/deja_sin_efecto sino hacer lugar/rechazar/desestimar
# LA DEMANDA. Vocabulario = split de RE_DEMANDA (fuente única) + {0,30} interposición
# (recupera 'la presente demanda' / 'en todas sus partes la demanda' bajo norm).
_DEM_FONDO = r"(?:demanda|acci[oó]n|pretensi[oó]n|impugnaci[oó]n)"  # v1.14 (B136/H176): +impugnación — testigos gemelos 330_p1927/330_p2478
RE_FONDO_GRANT_DEM  = re.compile(rf"\b(?:hac\w+\s+lugar|admit\w+)\b[^.;]{{0,30}}\b{_DEM_FONDO}\b", re.I)
RE_FONDO_REJECT_DEM = re.compile(rf"\b(?:rechaz\w+|desestim\w+)\b[^.;]{{0,30}}\b{_DEM_FONDO}\b", re.I)
# Verbos de fondo que NO se anclan a 'demanda' (grant): la originaria a veces resuelve
# declarando inconstitucionalidad/nulidad de un decreto/acto, condenando o mandando ejecución.
RE_FONDO_EXTRA_GRANT = re.compile(
    r"declarar\s+la\s+inconstitucionalidad"
    r"|declarar\s+la\s+nulidad\s+de(?:l|\s+la)\s+(?!auto|concesi|resoluci[oó]n\s+de\s+fs)"  # NO nulidad_concesion
    r"|\bse\s+condena\b|\bcondenar\s+a\b"
    r"|(?:mandar|ordenar\s+que\s+se)\s+llev\w+\s+adelante\s+la\s+ejecuci[oó]n", re.I)
# Guard de negación: VERBATIM del parser B107 (RE_B107_NEG_HACER_LUGAR). 'no hacer lugar'
# no es grant. (El ruteo pleno de la negación a la rama reject se difiere a la 2ª pasada
# de apelados de resolución directa; 0 casos en las 546 originarias.)
RE_FONDO_NEG = re.compile(r"\bno\s+(?:se\s+)?(?:corresponde\s+)?(?:hacer?|ha|hace|hacen)\s+lugar\b", re.I)
# Guard de objeto: el verbo cae sobre una excepción/defensa procesal, no sobre la demanda.
RE_FONDO_EXCEP = re.compile(
    r"\bexcepci[oó]n\b|\bfalta\s+de\s+(?:acci[oó]n|legitimaci[oó]n)\b|\bdefecto\s+legal\b|\bacumulaci[oó]n\b", re.I)
# Asimetría: el rechazo es de fondo SALVO que el considerando funde inadmisibilidad
# (la instancia originaria no procede / la pretensión es ajena a la competencia originaria).
RE_FONDO_INADM = re.compile(
    r"inadmisibilidad\s+de\s+la\s+pretensi[oó]n|admisibilidad\s+de\s+la\s+instancia"
    r"|recaudos\s+que\s+condiciona\s+la\s+admisibilidad|requisitos\s+jurisdiccionales"
    r"|no\s+debe\s+tramitar\s+ante\s+esta\s+instancia"
    r"|ajena\s+a\s+la\s+(?:competencia|jurisdicci[oó]n)\s+originaria|en\s+condici[oó]n\s+de\s+parte", re.I)
# Guard de umbral (v1.11, B141/330_p3777): rechazo IN LIMINE de la demanda = falta de
# caso justiciable, no mérito. Se evalúa sobre m.group(0) del reject (como EXCEP);
# \b tolera las comillas del OCR («“in limine”»). i-acentuada por robustez.
RE_FONDO_IN_LIMINE = re.compile(r"\bin\s+l[ií]mine\b", re.I)

def es_de_fondo(considerando, por_ello):
    """¿La originaria resolvió el FONDO de la demanda? (isMerit de la originaria).

    Opera sobre texto norm()'d. grant = fondo siempre; reject = fondo salvo que el
    considerando funde inadmisibilidad (asimetría B136). Verbo sobre excepción/defensa
    o 'no hacer lugar' NO cuenta. Medido en disco: 133/546 originarias, precisión limpia.
    """
    pe = norm(por_ello); co = norm(considerando)
    if RE_FONDO_EXTRA_GRANT.search(pe):
        return True
    for m in RE_FONDO_GRANT_DEM.finditer(pe):
        if RE_FONDO_NEG.search(pe[max(0, m.start() - 25):m.end()]):
            continue                      # 'no hacer lugar' = no grant
        if RE_FONDO_EXCEP.search(m.group(0)):
            continue                      # 'hacer lugar a la excepción...' = procesal
        return True
    for m in RE_FONDO_REJECT_DEM.finditer(pe):
        if RE_FONDO_EXCEP.search(m.group(0)):
            continue                      # 'desestimar la excepción de falta de acción' = procesal
        if RE_FONDO_IN_LIMINE.search(m.group(0)):
            continue                      # v1.11: rechazo in limine = umbral (B141/330_p3777), no fondo
        return not bool(RE_FONDO_INADM.search(co))   # asimetría
    return False

def es_revision_fondo(disp, por_ello, is_originaria, considerando=""):
    """GATE de revisión de fondo (isMerit) — M26 rewiring + B136 (H169).

    Deriva de caseDisposition (disp) ∈ fondo, MENOS los guards dispositivos B119
    (competencia/inoficioso = procedimiento). El guard vive acá, NO en disposicion():
    un fallo de competencia que revoca para sentar competencia conserva
    caseDisposition=revoca, pero es_revision_fondo=no. B136: la originaria ya NO es
    hard-`no` — su mérito lo decide es_de_fondo (mismo detector que el is_merit del
    parser → ejes coinciden). Devuelve 'si'/'no'.
    """
    pe = norm(por_ello)
    if RE_DISP_COMPETENCIA.search(pe) or RE_DISP_INOFICIOSO.search(pe):
        return "no"                       # competencia/inoficioso dispositivo = procedimiento
    if is_originaria:
        return "si" if es_de_fondo(considerando, por_ello) else "no"   # B136: era 'no' fijo
    if (disp == "confirma"
            and not any(p.search(pe) for _, p in DISP)     # confirma llegó por el fallback
            and RE_RECHAZA_REC.search(pe)
            and RE_RECHAZA_ACCESO.search(pe)):             # solo objeto INEQUÍVOCO de acceso
        return "no"                       # v1.12 B138: queja/hecho/reposición ≠ revisión de fondo
    if (disp == "nulidad"
            and RE_NULIDAD_ACTUADO.search(pe)
            and not RE_ABSOLUCION.search(pe)):
        return "no"                       # v1.15 B143: nulidad de actuaciones = procesal (salvo sustitutiva con absolución)
    return "si" if disp in _FONDO else "no"
