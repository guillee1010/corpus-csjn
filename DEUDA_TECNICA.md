# Deuda Técnica

Lista canónica de bugs del pipeline corpus-csjn y de la herramienta auditora
(`scripts/auditoria/auditar_fallo.py`). Una entrada por bug. Las entradas con
referencia §X.Y apuntan a `archivo/docs/PIPELINE_v1.md` (deprecado H062) para
contexto histórico del diagnóstico original; el estado vivo de cada bug está
en este archivo.

**Última actualización:** 2026-05-30 (H087: M14 — manifiesto sidecar de procedencia IMPLEMENTADO. `scripts/pipeline/generar_manifiesto.py` v1.0 (standalone, último paso del pipeline) escribe `output/parser/_manifest.json` de tres capas: (A) git commit + flag dirty —fija todo el código del repo cuando dirty=false—; (B) `__version__` de los 5 scripts de la cadena (detectar_paginas/construir_catalogo/cruzar/parser/parser_editorial), leído estáticamente vía ast sin importar el módulo; (C) sha256 + filas + bytes de los 3 intermedios (mapa_paginas/catalogo/fallos_localizados) y los 5 outputs canónicos. Decisiones: standalone, no hook en parser.py (cubre el 5º CSV de parser_editorial, se re-corre sobre outputs viejos, no engrosa procesar_archivo); allow-list explícita, no glob (excluye BASELINE y el propio _manifest.json, falla ruidoso si falta un canónico); sha256 = 2ª red de integridad además del golden, usable vía `--verify`. NO toca CSV → golden [CLEAN] por construcción; parser sin bump (sigue v18.07). Validado en máquina real: generar OK, check_regresion [CLEAN] 4/4, --verify [CLEAN] 8/8. Conteos sellados: outputs 5862/27463/140956/151/11445, inputs 46936/5862/5862. Pendiente menor: digest del corpus crudo (LibroVol*.md), único eslabón de la cadena aún sin fijar. | H086: R5 — colapso de la cascada de dispositivo Tier 1→2→3→3b→4 a un motor `_barrer()` único + 4 detectores `_cand_*` + 5 llamadas configuradas (M13). NO es extracción pura: reescribe la lógica de las 5 capas (el mismo bucle ×5, difería solo en rango/exclusión de dictamen/detector/fallback); riesgo medio, sobre función ya aislada por R1 con red M12. `_T2_PATS`/`_T3B_ARG_RE`/`_RE_ASI` subidos a nivel de módulo (compilaban en cada llamada); los 12 literales raw quedan byte-idénticos. La cascada de 5 llamadas NO se data-ificó (rangos dependen de runtime, el orden codifica prioridad). resolver_dispositivo 223→63 líneas; archivo 3650→3603. Validación: PoC de equivalencia original↔parcheado (21 dirigidos + 9 adversariales + 60k fuzz idénticos; 5644/5644 dispositivos reales reconocidos por las closures) → check_regresion [CLEAN] (4/4 CSV idénticos al golden); parser v18.06→18.07. M14 (manifiesto sidecar) sigue diferido. | H085: primer refactor del parser bajo la red (M12). R1 — cascada de dispositivo Tier 1→2→3→3b→4 extraída de procesar_archivo a `resolver_dispositivo(bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv) → (por_ello_idx, por_ello_text)` (M13). Extracción pura: 0 cambios de heurística; procesar_archivo 757→543 líneas. check_regresion [CLEAN] (4/4 CSV idénticos al golden); parser v18.05→18.06. Decisión de diseño: trazabilidad de versión NO va en columna de los CSV (rompería el golden y cada bump daría regresión espuria) sino en manifiesto sidecar — diferido a H086 (M14). | H084: diagnóstico de deuda estructural sobre parser v18.05 (set mínimo: parser + DEUDA + BITACORA + csjn_casos.csv + árbol). Recomendación: frente A (refacción REE), primer paso obligado = red de regresión (no había). Construido `scripts/tests/check_regresion.py` + golden de los 4 CSV del parser (casos/votos/zonas/editorial); verificado [CLEAN] (el golden se reproduce a sí mismo). Cierra el agujero "refactor sin red" (ver M12). Hallazgos de datos: dictamen_presente con 3 valores True/False/'0' (B037); 58 outcome=originaria con is_originaria=0 (valida frente D); outcome=otro 688/5862. NO toca pipeline ni outputs. | H083: módulo `estadisticas/` nuevo — extractor Playwright de los tableros Tableau del Anuario CSJN (sortea el AWS WAF vía navegador real); CSV de referencia 2024/2025 (secretaría, materia, admitidos); cruce voto×ministro 2025 extraído; HALLAZGO: voto propio de Lorenzetti 2025 = 12.899 ≈ total art. 280 (12.546), repartido transversalmente entre secretarías → suscripción individual del 280, no fragmentación doctrinaria (material H1/H3). Sesión de frente analítico, NO toca pipeline ni outputs canónicos. Decisión de fondo de H082 (variable materia) sigue postergada. | H080: diagnóstico refinado de tomos 335/336 (Tesseract); ruta de índice 336 diseñada y VALIDADA en construir_catalogo v1.01 (138 entradas, 0 regresión) pero PARQUEADA pendiente tomos papel; main revertido a baseline limpio pre-335 (056c31e); worklist de 62 firmas a escanear generado; infra: repo sacado del sync de Google Drive que corrompía .git. | H079 cont.: 4 minor outcomes
(desierto/inadmisible/improcedente/caducidad) — otro 757→688. Tomo 335
incorporado (+255 fallos, corpus 5862→6117). detectar_paginas.py v1.01
(exclusión 335-336 removida). Tomo 336 pendiente: construir_catalogo
no detecta su índice editorial. 335 con problemas de calidad: sin_firma
16→78, votos fragmentados por formato OCR distinto. parser.py v18.05.
H073: B091 aplicado — fallback
"revocar" en classify_outcome v13, revoca 208→359. B093 aplicado —
primer_token_de_caratula con búsqueda profunda de tokens no-genéricos
+ stoplist sincronizada; sin_firma 31→17, sin_dispositivo 35→24,
votos +73.
H072: B085 aplicado — Tier 3b sin
exclusión dictamen ni rango, sin_dispositivo 50→40, 71 mejoras 0 regresiones.
B086 parcial — Tier 4 "tribunal resuelve", 40→35, "hágase saber" descartado.
B087 aplicado — guard unanime wcM≤4→svoto, 5 casos. B088 aplicado — reorden
Pistas editorial antes de sumario, 330_p2849 110k→7448 wc. 3 bugs nuevos:
B089-B091.
H070: B082 fix parcial aplicado —
excluir líneas >= inicio_votos_indiv del considerando. 19 outcomes
corregidos (inadmisible_280 contaminado → outcome correcto del
dispositivo), 66 wc_considerando limpiados (Δ promedio -1155), 0
regresiones. M10 nuevo: zonificador debería distinguir zonas de
mayoría vs votos individuales.
H069: B045 fix parcial aplicado —
bidireccional closest-to-lfc en fallback firma_actual de detectar_fin_real.
33 casos cambian, 2 empates bloqueados por strict less-than, 0 regresiones.
votos +5 (27341), sin_firma -1 (33), unanime -3 (3505), segun_su_voto +3 (735),
disidencia +1 (1102), zonas +535 (142505). B025 parcialmente corregido (3 falsos
unanime eliminados). B082 nuevo: classify_outcome sobre bloque completo.
H068: re-medición B025 (414→72),
diagnóstico arrastre 280 (15 FP, POC B081 no aplicado por REE),
inspección causa raíz B045 (catalogador+cruzador), re-medición B018.
B079 aplicado — MERIT_OUTCOMES ampliado con competencia, abstracto, originaria,
desistimiento; 5 casos movidos de 280 a outcomes correctos.
B080 POC (RE_280_ABREVIADO para CPCCN/C.P.C.C.N.) testeado y revertido:
1 caso recuperado no justifica código extra.
Conteos validados: 280=291, ac4=52, desestima=476, otro=1668.
H066: B077 _unhyphenate aplicado —
85 dispositivos corregidos, 229 outcomes afectados. B078 RE_ACORDADA_4_DIRECTA
+ fix año corto + (?!\d) guard. classify_outcome v12.
Diagnóstico: 6 FP ac4 fantasma, 43 FP 280 fantasma (inconsistencia
CSV/parser), 16 arrastre B045 en 280, 18 FN 280 pendientes.
H065: recalibración detectores
post-B010. Fix regex `art[íi]?culo?` → `(?:art\.?|art[íi]culo)` en 4
constantes (RE_280_CONSIDERANDO, RE_280_LIBRE, RE_ACORDADA_4, RE_ART_117_CN).
RE_ACORDADA_4 reescrito (cualquier artículo del reglamento, no solo art. 1).
classify_outcome v11 con merit guard. inadmisible_280: 41→278. acordada_4:
0→40. is_originaria: 462→478. 3 FP ac4 documentados. H064: M09 aplicado,
B010 aplicado.
H062: auditoría de deuda técnica y
limpieza documental. B013, B029, B030, B039, B046, B060 cerrados. B009
actualizado (Fase F). B052/B053/B054 deduplicados. Resumen ejecutivo
reescrito. PIPELINE.md y PIPELINE_HALLAZGOS.md deprecados a `archivo/docs/`.
Sesiones anteriores H046–H059:
B069 cerrado — eliminada búsqueda atrás Pista 1, 277 mejoras, sin_firma 406→148.
A001 cerrado — fallback firma inversa, 34 mejoras, sin_firma 148→114.
A001b — _encontrar_zona_fallo primera apertura, 1 mejora, sin_firma 114→113.
B070+B071 cerrados — Pista 1 forward: validación texto corriente +
normalización tildes, 37 mejoras, sin_firma 113→76, votos 27103→27303.
B072 cerrado — 15 conjueces en JUECES_CONOCIDOS, 21 mejoras, sin_firma 76→74,
votos 27303→27325. B073 cerrado sin fix (verificado sin problemas).
B074 cerrado — guard posicional título en detectar_fin_real, 5 mejoras +
2 correcciones, sin_firma 74→69, votos 27325→27335.
B075 abierto — Hornos "Roberto Enrique" (1 caso, prioridad baja).
H051 — Refacción C Paso 1+2: zonificador integrado en parser.py,
31 sumarios editoriales reclasificados, sin_firma 69→38, 0 regresiones.
Catálogo validado contra corpus (0 fallos no catalogados).
H052 — Refacción C Paso 3: dictamen zonificado integrado en parser.py.
Fix bug `continue` en loop `en_dictamen` (inflaba wc_dictamen en 3254 casos).
Guarda dictamen en zonificador (suprime ~486 falsos dispositivo del Procurador).
3 sumarios editoriales nuevos (anclas RE_VISTOS + RE_REMISION), sin_firma 38→35.
Concordancia dictamen 41.4% era artefacto de type mismatch → 100% real.
H053 — CSV zona-centered canónico (149512 segmentos) integrado como tercer
output del parser. Guarda defensiva fecha/dictamen (0 impacto). Diagnóstico
firma zonificada: 15 discrepantes analizados, ROI insuficiente (35→33 máximo),
piso irrecuperable ~17 confirmado.
H054 — análisis y diagnóstico. B065 parcialmente validado
(n_jueces↔n_votos: 0 discrepancias). B061 desvinculado de B066.
Zona residuo_caso_anterior planificada para H055.
H055 — zona `residuo_caso_anterior` implementada en parser.py.
Pasada 3 en zonificador reclasifica intersticio pre-semántico.
word_count/wc_mayoria excluyen residuo: −1,055,756 wc (8.6% del corpus).
5152 fallos afectados, 7677 segmentos reclasificados. 0 regresiones.
B045 manifestación B mitigada a nivel de datos (Camino C Paso 1 completado).
Fix `Causa` → `Causa\s*:` en RE_DATOS_PARTES: elimina 612K wc de falsos
epilogos en 871 casos. Segmentos: 149512 → 147952. Epilogo: 1826K → 1214K wc.
H056 — explorador v4.1 (outlier indicators/presets). Pasada 3b: revert
residuo FP en 37 per curiam sin apertura. L2 Ministerio en RE_DATOS_PARTES.
B076: flag `_en_sumario` suprime firma espuria en sumarios. sin_firma 35→34.
H057 — documentación (BITACORA, CHANGELOG, DEUDA_TECNICA).
H058 — B077 cerrado: editorial detection (acordadas/índices/discursos). Nueva
pista `editorial_siguiente` en `detectar_fin_real`. 4to CSV canónico:
`csjn_casos_editorial.csv` (182 secciones). −645 segmentos, +1 voto.
H059 — Fix editorial: `acordada` eliminada como tipo — 67 hits eran FP
(subsecciones del índice). `_tipo_zona_editorial` remapea a `"indice"`.
Editorial 182→53 (49 indice, 4 discurso). Auditoría sin_dispositivo: 56/57
legítimos, 1 recuperable (331_p1013, mid-line). 0 regresiones.
Cobertura firma: 97.4% → 98.0% → 98.7% → 98.8% → 99.3% → 99.4%.
Votos: 26959 → 27103 → 27303 → 27325 → 27335 → 27336).
H061 — B079 cerrado: `parser_editorial.py` con subtipos (135 secciones:
46 ig, 45 ip, 20 il, 18 im, 5 ac, 1 di). Refactoring parser.py (−111
líneas). Catálogo regenerado (5862, diff 0). Parseo entries descartado
(redundante con `construir_catalogo.py`).

---

## Convención

**IDs:** los bugs activos y cerrados se numeran `B001..B0NN` correlativos,
agrupados por componente. La letra `H` no se usa para bugs porque se reserva
a las hipótesis de la tesis (H1-H5).

**Campos por entrada de bug activo:**

- **Componente:** catálogo / cruzador / parser / auditor.
- **Origen / fuente del diagnóstico:** dónde se identificó (XXI-letra del
  forense, F-N de BITACORA, sesión X, etc.).
- **Causa raíz:** mecanismo del bug en el código, cuando se conoce.
- **Diagnóstico / evidencia:** caso testigo, cuantificación, líneas exactas.
- **Estado de verificación:** uno de cuatro niveles —
  - `confirmado_cuantificado`: con números contra el CSV o el corpus.
  - `confirmado_caso_testigo`: con un `.md` auditado, sin cuantificación.
  - `hipotesis_no_verificada`: identificado leyendo código, sin medir.
  - `sospecha_cardinal`: número estimado pero sin verificar el mecanismo.
- **Validador propuesto:** script o método de verificación. Si requiere
  trabajo significativo, se anota como plan, no se codea aún.
- **Estado del fix:** no diseñado / diseñado / aplicado / aplicado y validado.
- **Referencias cruzadas:** §X.Y de PIPELINE.md cuando existe, equivalencias
  con otras letras (XXI-N, F-N), etc.

**Mapeo histórico de IDs viejos (A, B, C, D, Bug 1) al final del archivo.**

---

## Estado del corpus

- **Catálogo:** 6117 entradas (v15 + tomo 335).
- **Universo procesable:** 20 tomos (329-335, 337-349; 336 pendiente).
- **Output parser productivo:** 6117 casos en `output/parser/csjn_casos.csv`.
  Desglose por tipo_entrada: 5876 `fallo` + 34 `sumario_editorial` +
  207 `sumario_con_link`.
- **Cobertura sobre catálogo:** 6117 / 6117 = **100%** (todos en CSV).
  Catálogo validado contra corpus: 0 fallos no catalogados (H051).
  Cobertura de firma sobre fallos: 5798/5876 = **98.7%**.
- **Sin firma:** 78 casos (post-H079). 62 nuevos del tomo 335 por
  formato OCR fragmentado de encabezados de voto. Residual pre-335: 16.
  Trayectoria sin_firma: 813→...→16→78.
- **Votos:** 27774 filas (post-H079).
- **Arquitectura:** `zonificar_bloque()` integrado en parser.py (H051-H052,
  Refacción C). Retorna `(list[str], list[tuple])` con zonas por línea y
  anclas. `extraer_segmentos()` genera CSV zona-centered (H053).
  Uso actual: clasificación sumario_editorial + lineas_dictamen +
  CSV zona-centered canónico. Uso futuro: firma zonificada (descartado
  por ROI insuficiente, ver diagnóstico H053-B).
- **Zonas:** 146145 segmentos en `output/parser/csjn_casos_zonas.csv` (post-H079).
  Schema: caso_id_canonico, tomo, zona, segmento, linea_ini, linea_fin,
  n_lineas, wc.
- **Editorial:** 160 secciones en `output/parser/csjn_casos_editorial.csv`.
- **Jueces conocidos:** 56 entradas en JUECES_CONOCIDOS (28 titulares/previos +
  13 conjueces B063 + 15 conjueces B072).
- **Fixes aplicados:**
  - Sprint 2026-05-09: §3.6.a `pg_fin+1`, §3.6.e Fase 1, §4.6.j
    `RE_APERTURA` doble espacio, Fix 1 (V1 → `case_name_cuerpo`).
  - H035: búsqueda anclada de dispositivo (B013, 302 prematuros).
  - H036: backstop dictamen con RE_APERTURA (31 casos).
  - H038: forward con validación de firma (B059, 279 casos).
  - H039: 5 variantes dispositivo nuevas (22 casos).
  - H040: guardas exclusión Pista 2 en detectar_fin_real (32 casos).
  - H041: Tier 2 mid-line dispositivo search (11 casos).
  - H042: fix B055 firma truncada/contaminada (1262 mejoras calidad).
  - H043: B063 conjueces + fix cosmético desconocidos (40 mejoras, +55 votos).
  - H044: B067 Tier 3 dispositivo retry sin techo (17 mejoras, sin_firma 422→406).
  - H045: visor explorador + PoC firma independiente v2 (diagnóstico, sin fix aplicado).
  - H046: B069 cerrado — eliminada búsqueda atrás Pista 1 (277 mejoras, sin_firma 406→148).
  - H047: A001 cerrado — fallback firma inversa (34 mejoras, sin_firma 148→114).
    A001b — _encontrar_zona_fallo primera apertura (1 mejora, sin_firma 114→113).
  - H048: B070+B071 cerrados — Pista 1 forward: validación texto corriente +
    normalización tildes (37 mejoras, sin_firma 113→76, votos 27103→27303).
  - H049: B072 cerrado — 15 conjueces en JUECES_CONOCIDOS + _RE_FIRMA_COMPLETA
    (21 mejoras, 1 regresión aceptada 346_p610, sin_firma 76→74, votos 27303→27325).
    B073 cerrado sin fix (451 lfr_cambio verificados, 0 problemas).
  - H050: B074 cerrado — guard posicional título en detectar_fin_real
    (5 mejoras + 2 correcciones, sin_firma 74→69, votos 27325→27335).
    B075 anotado (Hornos "Roberto Enrique", 1 caso, no fixeado).
  - H051: Refacción C Paso 1+2 — zonificador integrado en parser.py
    (3 pasadas: headers, anclas, propagación). 31 sumarios editoriales
    reclasificados, sin_firma 69→38, 0 regresiones. Catálogo validado
    contra corpus (5855 aperturas, 0 huérfanos genuinos).
  - H052: Refacción C Paso 3 — dictamen zonificado. zonificar_bloque()
    retorna (list, anclas). Guarda dictamen: solo apertura/fecha cierran
    zona dictamen (~486 falsos dispositivo suprimidos). lineas_dictamen
    derivado de zonas, eliminado loop en_dictamen (fix bug continue que
    inflaba wc_dictamen en 3254 casos). Anclas RE_VISTOS + RE_REMISION:
    3 sumarios editoriales nuevos. sin_firma 38→35, 0 regresiones.
  - H053: CSV zona-centered canónico — `extraer_segmentos()` integrada
    en parser.py, `csjn_casos_zonas.csv` como tercer output (149512
    segmentos). Guarda defensiva fecha/dictamen en Caso (b) (0 impacto).
    Diagnóstico firma zonificada: 15 discrepantes (10 sin_dispositivo
    irrecuperables, 3 falsos positivos zonificador, 2 complejos).
    Piso irrecuperable ~17 confirmado. sin_firma sin cambio (35).
  - H054: B065 parcialmente validado (n_jueces↔n_votos: 0 discrepancias).
    B061 desvinculado de B066. Diagnóstico, sin fix aplicado.
  - H055: zona `residuo_caso_anterior` (Pasada 3 en zonificador).
    word_count/wc_mayoria excluyen residuo (−1,055,756 wc, 8.6% del corpus).
    5152 fallos afectados. Fix Causa→Causa\s*: en RE_DATOS_PARTES (−612K wc
    de falsos epilogos). Segmentos 149512→147952. 0 regresiones.
  - H056: explorador v4.1. Pasada 3b revert residuo FP (37 per curiam).
    L2 Ministerio en RE_DATOS_PARTES (−171 epilogos falsos). B076: flag
    `_en_sumario` suprime firma espuria en sumarios. sin_firma 35→34.
    Segmentos 147952→142615.
  - H057: documentación (BITACORA, CHANGELOG, DEUDA_TECNICA).
  - H058: B077 cerrado — nueva pista `editorial_siguiente` en
    `detectar_fin_real`. 4to CSV canónico `csjn_casos_editorial.csv`
    (182 secciones). −645 segmentos (142615→141970), +1 voto (27335→27336).
  - H059: fix editorial — `acordada` eliminada como tipo en
    `_tipo_zona_editorial` (67 FP remapeados a `"indice"`).
    Editorial 182→53 (49 indice, 4 discurso). Auditoría sin_dispositivo:
    56/57 legítimos, 1 recuperable (`331_p1013`, mid-line). 0 regresiones.

---

## Deuda CERRADA

Bugs resueltos en commit con validación. Quedan documentados acá para
trazabilidad histórica; el diagnóstico técnico vive en PIPELINE.md.

### B001 — Bug `pg_fin + 1` del cruzador

**Componente:** cruzador.
**Fix aplicado:** 2026-05-09, una línea en `cruzar_catalogo_y_mapa.py`
línea 235. Disolvió bloques inflados de ~32 líneas en 5.695/5.695 pares
consecutivos.
**Referencias:** PIPELINE §3.6.a. XXI-e del forense. ID histórico: no
tenía letra propia en el documento del 2/5 (era el bug del +1 que
DEUDA_TECNICA original no había identificado todavía).

### B002 — `fallo_cruza_archivos` calibración (efecto colateral §3.6.a)

**Componente:** cruzador.
**Fix:** disuelto como efecto colateral de B001. 27 casos pre-fix → 20
post-fix. Los 7 casos que salieron eran falsos positivos predichos.
Cierre 2026-05-09.
**Referencias:** PIPELINE §3.6.d. XXI-b del forense. ID histórico: era
**Bug B** del documento del 2/5.

### B003 — Hojas complementarias tomos 331-334 (Fase 1)

**Componente:** cruzador.
**Fix aplicado:** 2026-05-09, post §3.6.a. 39 casos `pagina_fin_no_en_mapa`
reasignados (32 → `ok_pg_fin_redirigida`, 7 → `ok_cortado_en_indice`).
Fase 2 sigue abierta para los 43 `pagina_no_en_mapa` simétricos (= B009).
**Referencias:** PIPELINE §3.6.e. ID histórico: era **Bug C** del
documento del 2/5 (39 casos `pagina_fin_no_en_mapa` que se pensaban
resueltos por catálogo v15; en realidad se resolvieron acá).

### B004 — Último fallo del tomo arrastra aparato editorial

**Componente:** cruzador.
**Fix aplicado:** 2/5/2026, `cruzar_catalogo_y_mapa.py` usa
`linea_fin = linea_inicio_indice_nombres - 1` cuando se pasa
`secciones_indices_v14.csv`. Status nuevo: `ok_cortado_en_indice`. 19
casos cubiertos, uno por tomo.
**Referencias:** PIPELINE §3.6.e (mismo dominio). BITACORA H005-H008. ID
histórico: era **Bug D** del documento del 2/5.

### B005 — `RE_APERTURA` estricto doble espacio (parcial)

**Componente:** parser.
**Fix aplicado:** 2026-05-09, `parser.py` línea 57. `RE_APERTURA` cambió
de espaciado literal a `\s+` libre. 17 de 18 casos capturados (16 pasaron
de `ok_sin_marcador_apertura` a `ok`, 1 de `fallo_cruza_archivos_sin_marcador`
a `fallo_cruza_archivos`). El caso 18 (`343_p646`) tiene patrón editorial
irregular distinto, queda como B016.
**Referencias:** PIPELINE §4.6.j. XXI-g del forense (variante 1 de 3 — las
otras dos variantes "pegado" y "partido en 2 líneas" siguen vivas como B015,
B016). Sin ID histórico.

### B006 — `apertura_idx + len(bloque)` aritmético (efecto evaporado post-§3.6.a)

**Componente:** parser.
**Estado:** bug aritmético sobrevive en código pero daño efectivo plausible
es ~0 post-fix B001. La cota superior bajó de 3.863 a 3.682 casos
potenciales. Re-evaluado 2026-05-09 como prioridad baja (cosmético).
**Referencias:** PIPELINE §4.6.a. XXI-k del forense. Sin ID histórico.

### B007 — `ok_sin_marcador_apertura` reclasificado (descriptivo)

**Componente:** parser.
**Estado:** no era bug, era información descriptiva contaminada. 185 →
347 casos post §3.6.a. Validación caso-a-caso confirmó cero regresiones
(151/163 con `wc_pre > wc_post`, 11 igual, 1 mejora). Reclasificado como
fenómeno editorial real del corpus.
**Referencias:** PIPELINE §4.6.h. Sin equivalente en XXI. Sin ID histórico.

### B008 — Fix 1: V1 como fuente primaria de `case_name_cuerpo`

**Componente:** parser.
**Fix aplicado:** commit `2adda06`. V1 como fuente primaria + columna
shadow `case_name_cuerpo_legacy` para comparación. Cubre el ~67% del
corpus donde V1 acierta. El 33% restante cae al fallback de `find_case_name`
(viejo comportamiento, sigue con bug — ver B011).
**Referencias:** PIPELINE §4.4.i. XXI-a del forense (XXI decía "no aplicado"
porque XXI fue del 3-4/5 y el commit posterior).

### B013 — Bug XII: cascada del dispositivo por falso positivo

**Componente:** parser.
**Fix aplicado:** en dos fases:
  - **H035:** búsqueda anclada con cascada apertura_rel → dictamen_end+1 → 0
    (302 prematuros). 0 regresiones.
  - **H038:** forward con validación de firma (279 post-apertura). 0 regresiones.
**Referencias:** XXI-c. BITACORA H035, H036, H038.

### B029 — `collect_firma_lines` con `max_lines=40` (resuelto por B055)

**Componente:** parser.
**Cerrado:** H062 (auditoría). El fix B055 (H042, commit `e258f66`) eliminó
`max_lines=40`. Firma actual: `def collect_firma_lines(bloque, idx_start,
max_lines=None)` (parser.py línea 499). Con `max_lines=None`, el techo es
`len(bloque)`. El mecanismo descrito ya no opera.
**Referencias:** XXI-l.

### B030 — `detectar_fin_real` excluye solo primeras 5 líneas (= B018)

**Componente:** parser.
**Cerrado:** H062 (auditoría). Redundante con B018 (ya anotado en el propio
texto). La búsqueda atrás de Pista 1 fue eliminada en H046 (B069). El
mecanismo de B030 ya no existe.
**Referencias:** XXI-m. F013. B018.

### B039 — Tomos antiguos sin `marcador_apertura_siguiente` (descriptivo)

**Componente:** parser (descriptivo).
**Cerrado:** H062. No era bug, era información descriptiva sobre el corpus.
**Referencias:** PIPELINE §4.6.i.

### B046 — Casos desaparecidos por bloque vacío en cruzador (no manifestado)

**Componente:** cruzador.
**Cerrado:** H062 (auditoría). La hipótesis de bloque vacío por páginas
compartidas nunca tuvo testigo empírico. Los 43 faltantes catálogo-parser
se explicaban por B009, y Fase F los resolvió. Deduplicación del catalogador
previene el mecanismo en la práctica. Queda como nota arquitectónica.
**Referencias:** H025, H026, H029.

### B060 — Pista 2 de `detectar_fin_real` matchea firmas como sumarios

**Componente:** parser.
**Fix aplicado:** 2026-05-18 (H040). `linea_es_header_sumario_guardado` con
exclusión de firmas, calificadores, headers de página, marcadores de apertura.
32 mejoras, 0 regresiones.
**Referencias:** H040.

---

## Deuda EN VALIDACIÓN

### B009 — `pagina_no_en_mapa` tomos 331-334 (Fase 2 de §3.6.e)

**Componente:** cruzador (localizador).
**Origen / fuente del diagnóstico:** XXI-d del forense. BITACORA H001, H002.
Causa raíz confirmada en H029 (Fase E).
**Causa raíz:** los 43 casos tienen `status: pagina_no_en_mapa` y campos
`archivo` y `linea_inicio` vacíos en `fallos_localizados.csv`. El localizador
los detecta en el índice editorial del tomo pero no puede anclarlos en el
cuerpo del `.md` porque el marcador numérico de página no aparece como línea
standalone. Dos sub-causas verificadas:

- **Sub-causa 1 — hoja complementaria consume la página de inicio de
  sección mensual:** la página N es una hoja complementaria editorial
  (separador de mes: "MARZO", "ABRIL", etc.). En el `.md` esa página
  se renderiza como texto de la hoja complementaria + encabezado de mes
  sin el número N como línea sola. El caso que el índice editorial ubica
  en página N arranca en página N+1 con su título limpio. Verificado con
  `331_p379` (Marzo=379, cuerpo arranca en 380) y `331_p439` (Abril=439).

- **Sub-causa 2 — inicio de volumen sin marcador previo:** el primer caso
  del volumen arranca antes del primer marcador de página. El índice
  editorial lo ubica en página 7 (`331_p7`) pero el cuerpo del `.md`
  no tiene línea `7` standalone antes del título del caso.

**Análisis de saltos en `mapa_paginas.csv` (H029):** script sobre el mapa
detectó 86 saltos de página (diferencia > 1 entre consecutivos) en todo
el corpus (tomos 329-348). El patrón es universal, no exclusivo de 331-334.
Los 43 faltantes coinciden con saltos de esos tomos. Salto negativo aislado
en `LibroVol338.2.md` (de=1591 a=338, salto=-1253): causa probable OCR
defectuoso en una página, no sistemático.

**Diagnóstico / evidencia:** 43 casos. Distribución: tomo 331: 11,
tomo 332: 11, tomo 333: 11, tomo 334: 10. Casos paradigmáticos verificados:
`331_p7` (Boston Cía. de Seguros c/ Federal Express) — título limpio en
línea 57 del `.md`, antes de sumarios, dictamen y cuerpo. `331_p379`
(Villarreal c/ Fernández) — hoja complementaria "MARZO" consume página 379,
cuerpo arranca en 380.

**Magnitud:** 43/5.862 = 0,73%. Pérdida aceptable, no requiere fix urgente.

**Hallazgo estructural (H029):** el título del caso que aparece antes de los
sumarios es una señal más robusta que "Vistos los autos" para anclar el
inicio de cada fallo. `detectar_caratula` del auditor ya implementa esta
lógica con guardias y detectó correctamente estos títulos en las pruebas.
Portar esa lógica al parser (Fase F) resolvería también estos 43 casos.
Requiere muestras representativas de tomos viejos antes de implementar
(variaciones conocidas: `V.`, mayúsculas, sin separador `c/`/`s/`/`|`).

**Estado de verificación:** `confirmado_cuantificado` (43 casos
identificados, causa raíz verificada empíricamente en H029).
**Estado del fix:** **parcialmente resuelto (Fase F, H030).** `cargar_localizados`
(parser.py) ahora infiere archivo y linea_inicio estimados para los 43 casos
`pagina_no_en_mapa` usando vecinos del mismo tomo (docstring: "v18 Fase F: los
fallos con status='pagina_no_en_mapa' ya no se descartan automáticamente"). Los 43
casos se procesan con localización estimada. El diferencial catálogo-parser
(5862 vs 5819 = 43) ya no existe: el pipeline produce 5862 casos.
Residual: la localización estimada puede no ser exacta. La causa raíz
(marcador de página ausente del .md) sigue sin resolver a nivel de Etapa 1.
**Referencias cruzadas:** PIPELINE §3.6.c. XXI-d. BITACORA H001, H002,
H029, H030. ID histórico: era **Bug A** del documento del 2/5.

### B010 — `RE_CONSIDERANDO` restrictivo + `.match()` con anclaje `^...$` — CERRADO H064

**Componente:** parser.
**Fix aplicado (H064):** regex cambiado de `^Considerando\s*[:.]?\s*$` a
`Considerando\s*[:.]\s*$` (sin anchor `^`, colon/punto obligatorio).
`.match()` → `.search()` en 5 ubicaciones (L657, L1305, L1321, L1812, L2287).
Guarda en `extraer_considerando`: solo acepta matches antes de `por_ello_idx`
para evitar matchear "Considerando:" de votos individuales o del caso siguiente.
**Validación:** 1188 cambios en `wc_considerando` (911 reducciones, 277 aumentos,
0 a cero). Cascada: 62 `is_originaria` (36 mejoras legítimas 1→0 por exclusión
de texto editorial, 26 nuevas 0→1, 0 bugs — auditados con audit_originaria_1a0.py).
2 `outcome` (otro→inadmisible_280). Firma, voting_pattern, n_votos, n_disidencias
sin cambios.
**Referencias cruzadas:** PIPELINE §4.6.b. BITACORA H019, H063, H064.

---

## Deuda ACTIVA — Catálogo (Etapa 2)

### B011 — Bug catalográfico `344_p344` (caso aislado)

**Componente:** catálogo.
**Origen / fuente del diagnóstico:** XXI-j del forense.
**Causa raíz:** dos entradas distintas del catálogo (`344_p1` con
`inicio_pag=51`, `344_p344` con `inicio_pag=53`) apuntan al mismo arranque
del corpus (caso ARAUJO).
**Diagnóstico / evidencia:** caso aislado. Verificable directamente en
`catalogo.csv` con filtro `tomo=344` y `caso in ('p1', 'p344')`.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** script de 5 líneas: `df_cat[df_cat['tomo']==344
& df_cat['caso'].isin(['p1','p344'])]` y verificar `inicio_pag`. Plan.
**Estado del fix:** no diseñado. Probablemente requiere mirar
`construir_catalogo.py` para entender por qué dos entradas distintas
matchean el mismo arranque.
**Referencias cruzadas:** XXI-j. Sin §X.Y en PIPELINE. Sin ID histórico.

### B045 — Frontera catalográfica mal puesta entre casos consecutivos

**Componente:** catálogo (etapa 2) o cruzador (etapa 3) — causa raíz
a nivel de quién decide las fronteras entre casos consecutivos.
**Origen / fuente del diagnóstico:** H024 (verificación de M1 y del
caso huérfano `346_p1205`). Identificado como causa raíz arquitectónica
común de B022, B025, B044.
**Causa raíz:** cuando una página del PDF contiene **final del caso N
+ inicio del caso N+1** (típico cuando el cierre del N termina al
medio de página y el N+1 arranca en la misma página), el catalogador
asigna la **página entera** al caso N+1. Resultado simultáneo:

- **Caso N queda truncado:** las últimas líneas de su cuerpo +
  dispositiva + firma + pie editorial caen fuera del bloque que el
  catálogo le asigna.
- **Caso N+1 hereda arrastre del caso N:** las primeras líneas de su
  bloque son contenido residual del N (= B022 en sus variantes
  V1a/V1b/V2/V2b según qué porción del N quedó incluida).

Los dos síntomas son **las dos caras del mismo bug**. B022 venía
documentando sólo la cara visible desde el parser (arrastre al inicio
del N+1). B045 documenta la cara del catálogo (frontera mal puesta)
y unifica el cuadro causal.

**Diagnóstico / evidencia:**
- **`343_p2243` (Salvatierra y Otros, H024).** Bloque del catálogo
  `LibroVol343-3.md` líneas 30534-31027. Truncado al medio del
  considerando 4° del Salvatierra. La dispositiva, firma y pie
  editorial del Salvatierra quedan en líneas absolutas 31028+
  (asignadas al caso siguiente del catálogo). Cara del N+1: el caso
  siguiente hereda esas ~30 líneas como arrastre.
- **`346_p1205` (Álvarez, H024).** Bloque del catálogo
  `LibroVol346-2.md` líneas 16883-16988. Truncado al medio del
  considerando 4° del Álvarez. Las ~34 líneas siguientes (16989-17022)
  contienen considerando 4° final + 5° + "Por ello, se declara
  procedente" + firma colegiada Rosatti/Rosenkrantz/Maqueda/Lorenzetti
  + pie editorial. El localizador confirma que el bloque siguiente
  (`346_p1208`, Frigorífico Paladini) arranca en 16989 según
  `fallos_localizados.csv` fila 5280. Es decir, el bloque del
  Paladini hereda esas 34 líneas como arrastre del Álvarez.

**Estado de verificación:** `confirmado_caso_testigo`. Dos testigos
verificados byte por byte (cara N: truncamiento al final) +
identificación de la otra cara (N+1: arrastre, ya documentada en
B022 con sus seis testigos). Causa raíz a nivel código (etapa
catálogo o cruzador) pendiente de diagnóstico — no se inspeccionó
`construir_catalogo.py` ni el cruzador en H024.

**Validador propuesto:**
1. Detector de "truncamiento al final" del auditor: para cada caso,
   verificar si las últimas líneas del bloque contienen una firma de
   juez completa + "Por ello"; si no, marcar truncamiento posible.
   Complementario del detector de borde superior (arrastre) ya
   pedido en B022. Plan.
2. Corrida cruzada sobre corpus completo: para cada par de bloques
   consecutivos (N, N+1), verificar si la línea inicial del bloque
   N+1 está dentro del rango natural del caso N (e.g., antes de un
   nuevo `RE_APERTURA` + carátula). Plan.

**Estado del fix:** mitigado a nivel de datos (H055, Camino C Paso 1).
La zona `residuo_caso_anterior` en el zonificador reclasifica el
intersticio pre-semántico (arrastre del caso N al inicio del N+1) y
lo excluye del word_count. 5152/5668 fallos afectados, 1,055,756 wc
excluidos. La causa raíz arquitectónica (frontera catalográfica)
sigue sin fix: el bloque del caso N+1 todavía contiene el arrastre
en el texto, pero queda etiquetado y excluido del análisis
cuantitativo. Fix raíz (Camino C Paso 2, revert del −1 en
catalogador/cruzador) evaluable en H056+.

**Severidad:** alta. B045 es **causa raíz arquitectónica común** de:
- **B022** (arrastre al inicio): se elimina por construcción si se
  fixea B045.
- **B025** (14-20 falsos `unanime`, re-medido H068): fallback de `detectar_fin_real`
  captura firma del previo arrastrado cuando la firma real fue
  truncada. Se elimina por construcción si se fixea B045.
- **B044** (span voto espurio): cuando B045 + B022 V2b arrastra un
  voto unipersonal entero. Se reduce su universo si se fixea B045
  (pero queda residual en escenarios sin truncamiento).
- **B018** (subset V1 del cluster, donde la mención del primer_token
  siguiente cae en el arrastre): se reduce el subset si se fixea
  B045.

Cuatro de los cinco mecanismos identificados por H022 tienen causa
raíz común en B045. El quinto (B018/M2) es el único independiente
(puede dispararse aún sin arrastre por el defecto de
`primer_token_de_caratula` en carátulas con sustantivos institucionales
genéricos, ver B043).

**Prioridad de fix:** máxima desde el punto de vista arquitectónico.
**Interacciones con otros bugs:** B022, B025, B044, B018 (cluster
V1), B043. Ver tabla arriba.
**Referencias cruzadas:** H024 (verificación de M1 y huérfano
`346_p1205`, identificación de B045 como causa raíz arquitectónica
común). B022 (cara N+1 del mismo bug). PIPELINE §X.Y a definir (no
hay sección documentada para esta lógica). Sin ID histórico.

**Refinamiento H025 (16/5/2026).** Inspección directa de
`construir_catalogo.py` y `cruzar_catalogo_y_mapa.py` (no realizada
en H024) identifica las líneas exactas y revela que B045 produce
**dos manifestaciones distintas** del mismo defecto arquitectónico,
no una única "frontera mal puesta" simétrica.

`construir_catalogo.py` línea 410 escribe
`pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]` sin restar uno.
Discordancia entre docstring (línea 57 y línea 381 prometen "− 1") y
código ya documentada en PIPELINE §2.5.a.

`cruzar_catalogo_y_mapa.py` línea 245 escribe
`out['linea_fin'] = linea_fin_header - 1`. La resta es correcta
cuando los casos no comparten página. Cuando dos casos comparten una
sola página física, el header de `pagina_inicio` del actual y el
header de `pagina_fin` (= `pagina_inicio` del siguiente) son la
misma línea X del `.md`. La operación produce `linea_fin = X − 1` y
`linea_inicio = X`, es decir bloque vacío o de longitud negativa.

Grep sobre el cruzador confirma ausencia de guarda: ninguna validación
de `linea_fin vs linea_inicio` entre líneas 175-281. Status escrito
en el caso degenerado: `'ok'`.

**Manifestación A — caso desaparecido (silenciosa).** Cuando dos casos
comparten página, el caso N recibe del cruzador un bloque vacío. El
parser, en `procesar_archivo` línea 1365-1367, hace
`if not bloque: continue` sin warning. La fila no aparece en
`csjn_casos.csv` o aparece con campos vacíos. Sub-diagnosticado en
H022/H024: no produce filas con error en el CSV, produce ausencia
de fila (invisible salvo comparación catálogo vs CSV). Tratamiento
separado como **B046**.

**Manifestación B — bloque con arrastre.** Cuando el cierre del N cae
físicamente dentro de la página de inicio del N+1 sin que sea
exactamente la misma página única, el bloque del N+1 hereda el cierre
del N como arrastre. Es la manifestación ya documentada en B045 con
los seis testigos vigentes (`343_p2243`, `346_p1205`, etc.) y la
responsable de B022, B025, B044.

**Observación lateral sobre redundancia +1/−1.** La coexistencia del
`pagina_fin` sin restar (catalogador) y el `linea_fin_header − 1`
(cruzador) constituye redundancia arquitectónica: dos etapas
implementando media operación cada una sin comunicación. Cuando los
casos están en páginas distintas, las dos mitades se complementan
correctamente. Cuando comparten página, se cancelan y producen
bloque vacío. Memoria de H022 indica que el `-1` fue removido
deliberadamente del catalogador para mejorar `sin_firma` aguas
abajo, pero la remoción se hizo sin verificar si otro script ya
asumía el `-1` previo. **Hipótesis fuerte de fix:** revertir uno de
los dos `-1` restaura coherencia. Pendiente de verificación contra
el código completo del pipeline antes de implementar (sesión
dedicada).

**Causa raíz a nivel código:** identificada en H025 (catalogador 410
+ cruzador 245). El estado "Causa raíz a nivel código (etapa catálogo
o cruzador) pendiente de diagnóstico" anotado en H024 queda
**superado** por esta inspección.

**Cuantificación H068 (2026-05-24).** Medición sobre CSV vivo:

- 97.0% de fallos (5499/5667) tienen `linea_fin_real > linea_fin`:
  el parser extiende más allá del catálogo en casi todos los casos.
  Extensión mediana: 11 líneas. p95: 27. Máximo: 199.
- 0 casos con `linea_fin_real == linea_fin` (coincidencia exacta nunca).
- 168 casos con `linea_fin_real < linea_fin` (parser cortó dentro del
  bloque: 90 firma_actual, 61 sumario_siguiente, 17 editorial_siguiente).
- 110 casos en fallback `firma_actual` (pistas 1-4 fallaron):
  72 unanime (→ B025), 15 segun_su_voto, 15 disidencia, 6 mixed, 2 sin_firma.

**Arrastre 280 (H068).** 15 casos clasificados `inadmisible_280` por
arrastre B045: el `considerando_text` empieza con el per curiam 280
del caso anterior (art. 280 + "Por ello, se desestima" + firma).
Discriminador limpio: RE_280 match antes de "Por ello" en
`considerando_text` → 15/15 arrastre, 0 FP sobre 276 genuinos 280.
POC B081 (guard posicional en `classify_outcome`) testeado: 15 cambios,
0 regresiones. **No aplicado** (REE: 15 casos no justifican guard extra).
Transiciones: 6 → desestima, 1 → mal_concedido, 8 → otro (por gaps
preexistentes en OUTCOME_PATTERNS_DISPOSITIVO).

**Opciones de fix discutidas (H068):**

- **Camino A (cruzador):** aumentar `linea_fin` en cruzador (+30 líneas
  cubriría 98.4%). Los bloques pasan a incluir arrastre del caso
  siguiente (manejable por `refinar_inicio_por_titulo`). Riesgo:
  efectos cascada no previstos aguas abajo.
- **Camino B (parser fallback):** invertir orden del fallback firma_actual
  (L1710-1715): buscar adelante primero, atrás después. Encuentra firma
  real en zona de extensión antes de tropezar con arrastrada. Riesgo:
  rompe fallos cortos cuya firma está en la misma página de inicio.
- **Camino C (semántica inter-caso):** que cada caso pase su `linea_fin_real`
  al siguiente como indicio. Riesgo: cascada de errores si un caso cierra
  mal.

Decisión H068: evaluar opciones con tests en sesión dedicada. El `-1` del
cruzador podría estar compensando en otras partes del parser (memoria de
intento previo revertido).

**Fix parcial aplicado H069 — bidireccional closest-to-lfc.**
Nuevo enfoque descartó Caminos A/B/C. El fallback `firma_actual` en
`detectar_fin_real` (L1709-1731) ahora busca en ambas direcciones y elige
la firma más cercana a `lfc`. Strict less-than: empate → backward gana.
Motivación: backward-first encontraba firma arrastrada del caso anterior
(lejos de lfc) e ignoraba la firma real en la zona de extensión (cerca de
lfc). POC sobre 112 firma_actual: 35 mejoras predichas (16 unanime +
19 votos truncados), 0 regresiones. Spot-check de 3 CAMBIO_REVISAR:
342_p1426 (FP cosmético de header), 341_p878 (voto Rosenkrantz recuperado),
344_p603 (disidencia Maqueda 701 lín recuperada). Re-run validado:
33 cambios (2 empates bloqueados), 0 fuera de firma_actual, 0 nuevos
sin_firma, 0 retracciones, 33/33 wc suben. Commit en parser.py.
Efecto colateral: 9 outcomes redistribuidos (3→otro) porque
classify_outcome corre sobre bloque completo incluyendo disidencia
extendida → ver B082.
**Estado del fix:** causa raíz arquitectónica (frontera catalográfica)
sigue sin fix. Fix parcial cubre el fallback firma_actual (110→77 casos
siguen en firma_actual, los 33 ahora con firma correcta). Los Caminos
A/B/C del cruzador/catalogador siguen disponibles para fix raíz futuro.

**Propuesta arquitectónica alternativa:** ver `docs/GRAMATICA_DEL_FALLO.md`.
Documento conceptual que propone un parser por gramática del fallo
más diálogo entre bloques vecinos, con resolución de B045 sin tocar
catálogo ni cruzador. Sin compromiso de implementación; insumo para
H026+.

**Evidencia empírica en escala (H026, corrida `--random 80`):**
La auditoría con `auditar_fallo.py --random 80` el 2026-05-16
confirma que B045 manifestación B (arrastre del caso N al inicio del
N+1) es el patrón dominante del corpus, no la excepción.

- 73 de 80 casos (91,2 %) están en `EST_SOLAPADO`: el catálogo del
  próximo caso empieza antes o en la línea declarada como fin del
  caso actual. Solo 7 (8,8 %) están en `EST_GAP_CON_RESIDUO`. Cero
  casos en `EST_CONTINUO`, `EST_HEADER_NORMAL` o
  `EST_GAP_SOLO_HEADERS`. El parser sistemáticamente extiende el
  bloque del caso N más allá de la frontera catalográfica del N+1.
- 62 de 80 casos (77,5 %) tienen catch_all al inicio del bloque
  (residuo arrastrado del caso anterior). Clasificación del catch_all
  inicial por primera línea:

  | Tipo            | Casos |    % | Diagnóstico                                                       |
  | --------------- | ----: | ---: | ----------------------------------------------------------------- |
  | `mitad_oracion` |    25 | 40,3 | `detectar_fin_real` corta dentro del cuerpo del considerando (B048 modo A) |
  | `epilogo`       |    16 | 25,8 | Bloque editorial post-firma sin span propio en auditor (B047)     |
  | `por_ello`      |    10 | 16,1 | `detectar_fin_real` corta antes del cierre dispositivo (B048 modo B) |
  | `caratula`      |     8 | 12,9 | Carátula del caso actual no detectada (B049)                      |
  | `otro`          |     3 |  4,8 | Fragmentos ambiguos                                               |

  La distribución muestra que B045 manifestación B es agregado de
  varios mecanismos distintos. Al menos dos modos de falla
  independientes de `detectar_fin_real` (corte a mitad de oración,
  corte antes del Por ello) explican el 56,4 % del catch_all inicial.
  El 25,8 % restante es estructural (falta del span epílogo). El
  12,9 % es bug del detector de carátula.

- 39 de 70 casos con catch_all (55,7 %) tienen catch_all al final del
  bloque (epílogo propio del caso). Estos son los casos donde
  `detectar_fin_real` cortó dentro de o muy cerca del cierre real, y
  el epílogo editorial cayó dentro del bloque pero sin span propio.
  Análisis de patrón sobre los 48 catch_all finales identificados:

  - **Epílogo propio (23 casos, 48 %):** componentes editoriales
    post-firma con orden interno estable (bloque de recurso +
    traslado + partes + tribunal de origen + tribunales
    intervinientes). Ver gramática en
    `docs/GRAMATICA_DEL_FALLO.md`.
  - **Continuación de firma (≈17 casos, 35 %):** apellido de juez
    cortado, queda como catch_all de 1-2 líneas. Esto es B045
    manifestación A operando: el detector
    `linea_es_continuacion_firma` ya existe pero solo se usa en el
    borde inferior, no se incorpora al span `firma`.
  - **Ruido benigno (≈8 casos, 15 %):** líneas vacías o fragmentos
    editoriales menores. Catch_all que no indica bug.

**Implicaciones para el roadmap de fix:**

1. B045 manifestación B no es resoluble por arreglo único. Tiene
   componentes separables que requieren fixes distintos: epílogo
   arrastrado (B047, ~26 % del problema), modos de falla del parser
   (B048 modos A y B, ~56 %), carátula no detectada del auditor
   (B049, ~13 %).
2. La promoción del auditor a parser de Forma 1, por sí sola, no
   resuelve la mayoría del problema. `detectar_fin_real` está
   importado del parser y se ejecuta igual de mal en el auditor. La
   diferencia es que el auditor expone el fallo (vía catch_all); el
   parser lo silencia.
3. El detector de borde superior + detector de epílogo, juntos,
   resuelven el componente "epílogo arrastrado" del N+1 sin tocar
   `detectar_fin_real` del N. El borde superior se construye
   implícitamente al extender el span `epilogo` del caso N hasta la
   carátula del N+1.

---

## Deuda ACTIVA — Cruzador (Etapa 3)

### B012 — Catálogo de localización con `linea_fin` extendido sobre próximo caso

**Componente:** cruzador (o etapa de localización aguas arriba).
**Origen / fuente del diagnóstico:** F011 (BITACORA sesión 2026-05-09,
línea 640).
**Causa raíz:** no diagnosticada. Caso paradigmático: 339_p1648 con
catálogo dice fin=26634, pero contenido real termina en 26599. Líneas
26605-26634 ya pertenecen al fallo 339_p1651 (sumarios + dictamen de
"Diez, Ernesto Osvaldo"). No es problema del detector de borde inferior
del auditor; es del proceso de localización/catalogación.
**Diagnóstico / evidencia:** caso testigo `339_p1648`. Magnitud
desconocida — no se midió todavía cuántos casos tienen `linea_fin`
extendido similar.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** script ad-hoc que para cada caso compare
`linea_fin` del catálogo de localización contra la primera línea del
caso siguiente. Si `linea_fin > linea_inicio_siguiente - margen`, flag.
Cuantificar magnitud antes de diseñar fix. Plan.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** F011. Sin §X.Y en PIPELINE. Sin ID histórico.
Probable relación con la dinámica de §3.6.a residual.

---

## Deuda ACTIVA — Parser (Etapa 4)

### B014 — `find_case_name` retrocede y captura citas del dictamen previo (fallback Fix 1)

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-a del forense. Sesión VIII
(2/5/2026), 6 casos auditados manualmente.
**Causa raíz:** `find_case_name` (parser.py línea 344,
`max_back=15, max_back_fallback=60`) retrocede desde `apertura_idx`. Cuando
el dictamen previo contiene citas doctrinales con `c/`, las captura como
carátula. También captura cierre del fallo anterior cuando hay página
compartida.
**Diagnóstico / evidencia:** 33% del corpus cae al fallback de Fix 1 (B008
cubre el 67% restante con V1). Casos testigos: 329_p9, 329_p117, 329_p147,
329_p171, 329_p184, 329_p218.
**Estado de verificación:** `confirmado_cuantificado` (33% del corpus =
~1.920 casos).
**Validador propuesto:** comparar `case_name_cuerpo` vs
`case_name_cuerpo_legacy` (columna shadow del Fix 1) en los casos donde V1
no acertó. Cuantificar cuántos del 33% tienen captura espuria de
dictamen previo. Plan.
**Estado del fix:** diseñado en sesión VIII: validar contra `primer_token`
del índice antes de aceptar candidato. Pase 1 con primer_token, pase 2
fallback al comportamiento actual. Backward compatible. No aplicado.
**Referencias cruzadas:** XXI-a (segunda mitad). PIPELINE §4.4.i menciona
Fix 1 pero no el fallback residual. Sin ID histórico.

### B015 — `RE_APERTURA` variante "pegado en línea continua con cuerpo"

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-g del forense (variante 2 de 3),
chat 28/4.
**Causa raíz:** `RE_APERTURA` requiere línea exacta. Cuando el marcador
`FALLO DE LA CORTE SUPREMA` aparece pegado en línea continua con el cuerpo
(sin salto de línea propio), el anclaje `^...$` no matchea.
**Diagnóstico / evidencia:** mencionado en chat 28/4. No cuantificado.
**Estado de verificación:** `hipotesis_no_verificada`.
**Validador propuesto:** grep en `markdowns_v2/*.md` con expresión que
matchee el marcador no aislado. Plan.
**Estado del fix:** no diseñado. Aclarar primero si "pegado" significa
"sin salto antes" o "sin salto después" o "embebido en línea de cuerpo".
**Referencias cruzadas:** XXI-g variante 2. Sin §X.Y en PIPELINE (B005
cubrió solo doble espacio). Sin ID histórico.

### B016 — `RE_APERTURA` variante "partido en dos líneas"

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-g del forense (variante 3 de 3),
mencionada por el usuario en sesión XXI. Caso testigo es el "caso 18" de
B005: `343_p646`.
**Causa raíz:** carátula del fallo en mayúsculas, tema en mayúsculas,
sumario editorial, header tipográfico de página, **luego** marcador
`FALLO DE LA CORTE SUPREMA` con doble espacio (línea 24641 de
`LibroVol343-1.md`). La cascada `detectar_fin_real` cortó el bloque en
línea 24618 (tomando el header de página como pista de fin) antes de
llegar al marcador.
**Diagnóstico / evidencia:** 1 caso confirmado (`343_p646`). No
cuantificado en otros tomos.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** revisar tomos modernos buscando estructura
"carátula → tema → sumario → header pág → marcador". Plan.
**Estado del fix:** no diseñado. Posible dirección: extender la cascada
`detectar_fin_real` para mirar más adelante antes de aceptar un corte
basado en header de página.
**Referencias cruzadas:** PIPELINE §4.6.j (mencionado como "caso 18" pero
no abierto como bug propio). XXI-g variante 3. Sin ID histórico.

### B017 — Firma multilínea partida por header de página intra-bloque cae a catch_all

**Componente:** parser.
**Origen / fuente del diagnóstico:** F012 (BITACORA sesión 2026-05-09,
líneas 771, 901). Diagnóstico mecánico cerrado en la misma sesión leyendo
`parser.py` línea 283.
**Causa raíz:** los 14 patrones de `JUECES_CONOCIDOS` exigen nombre+apellido
en la misma línea (ej. `r"carmen\s+m\.?\s*argibay"`). Cuando la firma se
parte por corte editorial entre nombre y apellido, la línea aislada con el
apellido suelto no matchea ningún patrón y cae al `catch_all 31`.
**Diagnóstico / evidencia:** caso testigo `333_p2410`, línea 20848:
"M. Argibay." cae al catch_all porque la línea anterior (20847, dentro
del span de firma) termina en "Carmen". El patrón completo
"Carmen ... Argibay" no existe en una línea sola y por eso no matchea.
Contribuye a `voting_pattern=sin_firma`.
**Estado de verificación:** `confirmado_caso_testigo`. Magnitud no
cuantificada.
**Validador propuesto:** extender `auditar_fallo.py` con detector
"apellido suelto post-Considerando". La función
`linea_es_continuacion_firma` del auditor (líneas 159-211) ya usa
`APELLIDOS_FIRMA_TITULARES` con apellidos sueltos y es directamente
reutilizable. Plan.
**Estado del fix:** diseñado conceptualmente — agregar reconocimiento de
apellido suelto como continuación de firma reutilizando
`linea_es_continuacion_firma` en `detectar_firma_mayoria` del segmentador.
Precondición pendiente: confirmar caso testigo en `.md` crudo (BITACORA
línea 923).
**Referencias cruzadas:** F012. Sin §X.Y en PIPELINE (línea 2834 reconoce
la deuda). Sin ID histórico.

### B018 — Pista 1 `detectar_fin_real` con falso positivo en el bloque

**Componente:** parser.
**Origen / fuente del diagnóstico:** F013 (BITACORA sesión 2026-05-09,
línea 897). Equivalente a XXI-m. H023 refina causa raíz y agrega
testigos.
**Causa raíz (refinada en H023):** la pista 1 de `detectar_fin_real`
(parser.py líneas 1189-1202) busca el `primer_token_siguiente` dentro
del bloque con `buscar_atras(es_caratula, lfc, li + 5)`. El defecto
tiene tres componentes acoplados:
1. **`primer_token_de_caratula` (parser.py 1138-1150) no excluye
   sustantivos institucionales genéricos.** La lista de exclusión
   cubre `otro/otros/sociedad/sucesión/empresa/compañía` pero no
   `provincia/estado/nación/ciudad/buenos/aires/banco/ministerio/
   municipalidad/...`. En carátulas como `PROVINCIA DEL NEUQUÉN c/...`
   o `PROVINCIA DE BUENOS AIRES c/...`, el primer token devuelto es
   un sustantivo común que aparece masivamente en otros fallos. Ver
   B043.
2. **El test `es_caratula` no verifica estructura.** Sólo testea
   presencia de la palabra con boundaries `\b...\b` case-insensitive.
   No exige `c/` cercano, mayúsculas, ni que la línea sea corta.
   Acepta cualquier mención en prosa.
3. **El orden de operaciones impide guardias espaciales.**
   `detectar_fin_real` corre antes de detectar el span del dictamen
   o de la firma, así que no puede rechazar matches que caigan
   dentro de esos spans del propio caso. Documentado como limitación
   en el fix propuesto original (DEUDA_TECNICA pre-H023).

**Variantes empíricas (H023):**
- **V1 — match en arrastre del caso anterior:** el bloque arranca con
  contenido del caso previo (B022), donde aparecen apellidos casuales
  que matchean el primer_token siguiente. Resultado: el parser corta
  el bloque casi al inicio. Testigo: `344_p3543`, primer_token =
  `Sánchez`, match contra "Carlos Sánchez Herrera" en lista de
  profesionales del caso arrastrado (Coihue c/ Provincia de Santa
  Cruz). Bloque truncado a ~30 líneas iniciales, residuo 77.78%.
- **V2 — match en cuerpo o dictamen del caso actual con token
  genérico:** el primer_token siguiente es un sustantivo institucional
  que aparece naturalmente en el propio dictamen o cuerpo del fallo
  actual. Testigo: `339_p1393`, primer_token = `Provincia` (caso
  siguiente: `PROVINCIA DEL NEUQUÉN c/...`), múltiples menciones de
  "provincia" en el dictamen del Procurador y la dispositiva del
  FALLO. El parser corta al medio del bloque, perdiendo el FALLO de
  la Corte entero. Residuo 0% engañoso (lo procesado está bien
  clasificado, pero se asignó intervalo corto).

**Diagnóstico / evidencia:** tres testigos confirmados:
- `330_p2739` (V0 original, F013): match dentro del cuerpo del
  dictamen previo.
- `344_p3543` (V1, H023): gap +133, residuo 77.78%.
- `339_p1393` (V2, H023): gap +84, residuo 0% engañoso.
H022 sube prevalencia esperada a ~570 casos proyectados sobre corpus
completo a partir del cluster `pista_fin=caratula_siguiente` +
`borde_alertas=caratula_siguiente_en_gap` (7/80 en muestra del
spot-check).
**Estado de verificación:** `confirmado_mecanismo` (causa raíz en
código + tres testigos cubriendo dos variantes claramente
caracterizadas). Subido desde `confirmado_caso_testigo` en H023.
**Validador propuesto:** script de auditoría que, para cada caso con
`pista=caratula_siguiente`, verifique (a) si el primer_token es un
sustantivo institucional (cluster V2), (b) si el match cae en el
arrastre del previo (cluster V1), (c) si el match cae dentro de un
span de dictamen detectado (cluster V0). Permite cuantificar prevalencia
por variante.
**Estado del fix:** rediseñado en H023. Matriz de opciones evaluadas:

| Opción | Riesgo | Facilidad | Tiempo | Robustez | Escalabilidad |
|---|---|---|---|---|---|
| A — engrosar lista exclusión en `primer_token_de_caratula` | medio-alto: en `PROVINCIA DE BUENOS AIRES c/...` todos los primeros tokens son genéricos | alta | 30 min | baja | pobre |
| B — endurecer test `es_caratula` (línea corta, `c/` cercano, mayúsculas) | medio: OCR puede partir carátulas reales | media | 2-3 hs | media-alta | buena |
| C — guard espacial sobre span de dictamen | bajo en daño, alto en intrusividad arquitectónica | baja (requiere reordenar pipeline) | 1-2 días | media (sólo V0/V2 con match dentro del dictamen) | buena para su scope |
| **D — validación cruzada con `proximo_header_pagina`** (rechazar matches lejos de la frontera del mapa) | bajo | alta | 1-2 hs | alta | muy buena |
| E — validación cruzada con segundo token de carátula | bajo | media | 3-4 hs | alta | buena |
| F — multi-strategy con voto | bajo en FP, medio en FN | baja-media | 1 día | muy alta | excelente |
| G — no-op, downstream filtra | cero al pipeline, alto en pérdida (~570 casos) | trivial | 30 min | baja a medio plazo | mala |

**Recomendación direccional H023:** orden D → B → E. D ataca raíz
(usa el mapa de páginas como anclaje estructural confiable, captura
todas las variantes), bajo costo. B y E como refuerzo si queda
residual. A descartada como solución principal (techo bajo por
carátulas con todos los tokens contaminados). C en cartera para
refactor más amplio. F sobreintensiva. G sólo si conviene postergar.
No aplicado.
**Interacciones con otros bugs:** alimentado por B022 (variante V1).
Fijar B022 reduce el subset V1. Acoplado a B043 (defecto de
`primer_token_de_caratula`).
**Referencias cruzadas:** F013. XXI-m. H022 §2 (mecanismo M2). H023
sección M2. PIPELINE §4.4.k (loop principal). Sin §X.Y en PIPELINE.md
para esta lógica de pista 1. Sin ID histórico.

**Nota H025 (16/5/2026).** Lectura dirigida de `detectar_fin_real`
(parser.py 1153-1234) confirma el acoplamiento ya documentado en
causa raíz componente 3 y en variante V1. H025 aporta foco inverso:
la pista 1 no sólo se dispara espuriamente cuando hay arrastre, sino
que **también puede inducir cortes prematuros en bloques sin arrastre**
cuando el `primer_token_siguiente` es un sustantivo institucional
genérico que aparece naturalmente en cuerpo o dictamen del caso
actual (variante V2). El defecto de `primer_token_de_caratula`
(B043) tiene entonces dos efectos colaterales sobre `detectar_fin_real`,
no uno. Sin testigos nuevos en H025: la nota es por completitud del
mapa arquitectónico, no por verificación empírica adicional.

**Nota H062 (auditoría).** Dos de los tres componentes de causa raíz están
sustancialmente mitigados por fixes posteriores:
- Componente 1 (búsqueda atrás): **eliminado por B069 (H046).**
- Componente 2 (test `es_caratula` sin estructura): la búsqueda forward
  ahora usa `_es_texto_corriente()` (B070, H048) + normalización tildes
  (B071) + guard posicional título (B074, H050).
- Componente 3 (orden de operaciones): sigue vigente pero impacto reducido.
La estimación de "~570 casos proyectados" (H022) es obsoleta. Re-medir
prevalencia residual antes de diseñar fix adicional (opción D pendiente).

**Re-medición H068 (2026-05-24).** 554 casos tienen `primer_token`
genérico no excluido (Banco 88, Provincia 81, Asociación 78, Estado 57,
Ministerio 41, etc.). De estos, 185 casos previos fueron cerrados por
Pista 1 con token genérico del caso siguiente. Sin embargo, no hay
señal medible de FP residual desde el CSV: solo 3 casos
`caratula_siguiente` tienen wc ≤ 100, y son legítimos (competencias).
B069 (eliminó búsqueda atrás) + B070 (`_es_texto_corriente`) absorben
la gran mayoría. Medición de FP concretos requiere .md o re-run con
logging. Ampliar la exclusion list en `primer_token_de_caratula` es una
línea de código pero necesita validación para no romper Pista 1 en casos
donde el token genérico es realmente el primer token legítimo.

### B019 — `detectar_fin_real` off-by-one en firmas multilínea

**Componente:** parser.
**Origen / fuente del diagnóstico:** F010 (BITACORA sesión 2026-05-09,
línea 631).
**Causa raíz:** no diagnosticada al nivel de mecanismo. Caso paradigmático
`339_p1648`: la firma se extiende líneas 26598-26599 con silabación
("Juan / Carlos Maqueda."). `detectar_fin_real` reporta linea_fin_real=26598,
omitiendo la segunda línea de la firma.
**Diagnóstico / evidencia:** caso testigo `339_p1648`. Detectado por la
alerta `firma_multilinea_partida_por_fin_real` del detector de borde
inferior del auditor.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** correr `auditar_fallo.py --random 50` con
detector de borde inferior activo y filtrar alerta
`firma_multilinea_partida_por_fin_real` para cuantificar magnitud. Plan.
**Estado del fix:** no diseñado. Prioridad alta según BITACORA.
**Referencias cruzadas:** F010. Sin §X.Y en PIPELINE. Sin ID histórico.

### B020 — `detectar_fin_real` extiende al fallo siguiente

**Componente:** parser.
**Origen / fuente del diagnóstico:** F002 (BITACORA sesión H014).
**Causa raíz:** no diagnosticada al nivel de mecanismo. Pista de la
cascada que extiende `linea_fin_real` más allá del fallo actual hacia
contenido del fallo siguiente.
**Diagnóstico / evidencia:** caso testigo Décima (`349_p40`), residuo 22%
en auditor: el bloque incluye Y.P.F. c/ Mercante entero.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** muestra mayor con `auditar_fallo.py --random 50`
filtrando por residuo >15%. Identificar cuántos casos tienen el mecanismo
"linea_fin_real extiende al siguiente". Plan.
**Estado del fix:** no diseñado. Severidad: alta. Probable relación con
B018 (mismo dominio: pistas de la cascada `detectar_fin_real`).
**Referencias cruzadas:** F002. Sin §X.Y en PIPELINE. Sin ID histórico.

### B021 — `detectar_fin_real` corta corto en último del tomo

**Componente:** parser.
**Origen / fuente del diagnóstico:** F003 (BITACORA sesión H014).
**Causa raíz:** no diagnosticada al nivel de mecanismo. La cascada corta
antes de incluir la segunda línea de la firma cuando es último del tomo.
**Diagnóstico / evidencia:** caso testigo Sivaslian (`349_p306`), pierde
segunda línea de firma. Status `ok_cortado_en_indice` (= fix de B004).
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** auditar los 19 casos con status
`ok_cortado_en_indice` (uno por tomo) y verificar si pierden segunda
línea de firma o algún elemento estructural. Plan.
**Estado del fix:** no diseñado. Probable relación con B019 (mismo
dominio: cascada `detectar_fin_real`).
**Referencias cruzadas:** F003. Sin §X.Y en PIPELINE. Sin ID histórico.

### B022 — Arrastre del fallo previo al inicio del bloque (sistemático)

**Componente:** parser (síntoma observado); causa raíz a nivel
catálogo (= B045). El arrastre al inicio del bloque siguiente es la
cara visible desde el parser del bug catalográfico de frontera
(B045).
**Origen / fuente del diagnóstico:** F004 (BITACORA sesión H014).
H023 amplía con testigos nuevos y caracterización de variantes.
H024 verifica byte por byte cuatro testigos cubriendo cuatro
variantes, identifica B045 como causa raíz arquitectónica común,
desdobla V1 en V1a/V1b, y agrega V2b.
**Causa raíz:** B045 ubica mal la frontera entre dos casos consecutivos
del catálogo. Cuando una página contiene final del caso N + inicio
del caso N+1, el catalogador asigna la página entera al caso N+1.
El bloque que llega al parser para N+1 inicia con contenido del
caso N. Cuatro variantes empíricas verificadas:

- **V1a (chica, ≤15 líneas):** firma + pie editorial del caso
  anterior. Sólo metadatos, sin cuerpo argumental.
- **V1b (grande, 15-30 líneas):** considerandos finales del cuerpo +
  dispositiva + firma + pie editorial + tribunal de origen del caso
  anterior. Sin matches espurios de regex estructural; daño por
  proximidad sobre `find_tribunal_origen` y `find_case_name`
  retroactivo.
- **V2 (grande, 30-50 líneas):** `FALLO DE LA CORTE SUPREMA` completo
  del caso anterior, con `Autos y Vistos`, dispositiva, firma. Dispara
  match espurio de RE_APERTURA (parser.py 57) que el parser usa como
  `apertura_rel` del caso, contaminando `fecha_str` y dejando el
  cuerpo real como catch_all.
- **V2b (~10 líneas):** voto unipersonal completo del previo (header
  `Voto del señor ministro doctor don X` + `Autos y Vistos:` +
  cuerpo del voto + firma simple). Dispara match espurio de
  RE_VOTO_HDR (parser.py 142). Cuando el parser carece de guardia
  espacial sobre `marcadores_votos` (= B044), el span voto resultante
  envuelve carátula + sumarios + dictamen + cuerpo del caso real.

**Diagnóstico / evidencia:** seis testigos verificados, cubriendo
las cuatro variantes:
- Sivaslian, Cerboni, Macri, Lavrentiev (V1a, muestra H014, F004).
- `330_p829` (**V1b**, gap +7, span 2 catch_all de 25 líneas,
  considerandos 3°-5° del ANSeS arrastrados + firma colegiada
  Lorenzetti/Fayt/Petracchi/Maqueda/Argibay + "Tribunal de origen:
  Cámara Federal de la Seguridad Social, Sala II"; spot-check H022
  + verificación H024). `find_tribunal_origen` (parser.py 383-412)
  captura sistemáticamente el tribunal del arrastre en lugar del
  real, contaminando el CSV de producción.
- `332_p913` (**V2**, solapado -22, residuo 86.05%; H023): bloque
  arrastra cierre de una resolución sobre competencia en Bahía Blanca
  antes de la carátula real `Deluca c/ ANSeS`. Identificado primero
  como mecanismo M3 en H022 y re-asignado a B022 en H023.
- `346_p1205` (**V2** + B045, H024): bloque arrastra fallo completo
  de 10/10/2023 sobre conflicto de competencia (Juzgado Federal Seg.
  Social n°4 vs Contencioso Administrativo n°20 CABA) antes de la
  carátula real `Álvarez c/ M° RREECI`. Identificado como M3 en H022
  y como huérfano en H023; H024 lo re-asigna a B022 V2 + B045.
- `332_p244` (**V2b** + B044, H024): bloque arrastra voto unipersonal
  de Petracchi sobre causa de competencia previa (Santa Fe vs Civil
  26 sobre quiebra), L3-L12 del bloque, antes de la carátula real
  `Fernández c/ Fed. Asoc. Católicas`. Dispara match espurio de
  RE_VOTO_HDR que produce span voto envolvente de 114 líneas (M5 de
  H022).
- `343_p2243` (**V1b** + B045 + fallback de `detectar_fin_real`,
  H024): bloque arrastra cierre del fallo Gente Grossa S.R.L. con
  firma colegiada en L8-9 (líneas absolutas 30541-30542). Combinado
  con truncamiento al final (B045), el fallback de
  `detectar_fin_real` parser.py 1225-1231 captura la firma del previo
  como firma del caso, produciendo `voting_pattern=unanime` espurio
  (M1 / B025).

**Estado de verificación:** `confirmado_mecanismo`. Causa raíz
identificada al nivel arquitectónico (B045) + cuatro variantes
caracterizadas + seis testigos. Magnitud agregada no cuantificada
(la muestra H022 sugiere alta prevalencia, ~88% de los casos con
borde inferior solapado podría tener algún grado de arrastre, pero
la mayoría son V1a chicos sin daño significativo).
**Validador propuesto:** corrida `--random 50` con detector de borde
**superior** del auditor (análogo al de borde inferior implementado
en H018). El detector debe cubrir las cuatro variantes. Idealmente
cruzar con `csjn_casos.csv` para medir contaminación de
`tribunal_origen` (proxy de V1b sistemático).
**Interacciones con otros bugs:**
- Causa raíz: **B045** (frontera catalográfica mal puesta). B022 es
  la cara visible del mismo bug.
- Alimenta **B018** (V1 introduce líneas del previo donde la pista 1
  de `detectar_fin_real` puede matchear contra menciones casuales del
  primer_token siguiente; confirmado H023 con `344_p3543`).
- Alimenta **B025** (V1b + B045 al final → fallback de firma captura
  la firma del previo; confirmado H024 con `343_p2243`).
- Alimenta **B044** (V2b → span voto espurio; confirmado H024 con
  `332_p244`).
- Fijar B045 elimina B022 por construcción.
**Estado del fix:** no diseñado a nivel B022. Fix correcto va a B045
(causa raíz). Si se aplica fix a B045 a nivel catálogo, B022 desaparece
en todas sus variantes.
**Referencias cruzadas:** F004. H022 §2 (mecanismos M3 refutado, M4
confirmado, M5 reformulado). H023 sección M3 (refutación y
re-asignación de `332_p913`). H024 (verificación cuatro testigos,
identificación de B045 como causa raíz). B045, B025, B044, B018, B043.
Sin §X.Y en PIPELINE. Sin ID histórico.

### B023 — Fin del dictamen pisa el FALLO DE LA CORTE

**Componente:** parser.
**Origen / fuente del diagnóstico:** F005 (BITACORA sesión H014).
**Causa raíz:** mismo patrón del bug interno del auditor (ya fixeado en
el auditor durante H014, sesión 8/5). Cuando el dictamen no termina con
"Buenos Aires, fecha." en línea propia, la heurística del parser
confunde la fecha del fallo con cierre del dictamen.
**Diagnóstico / evidencia:** detectado durante construcción del auditor
en H014. Cuantificación agregada no realizada.
**Estado de verificación:** `confirmado_caso_testigo` (al menos los casos
de la muestra inicial de H014).
**Validador propuesto:** el fix ya validado en el auditor es directamente
aplicable. Validar en muestra de N=10 antes de migrar.
**Estado del fix:** diseñado (mismo fix del auditor). Migración al parser
pendiente.
**Referencias cruzadas:** F005. Sin §X.Y en PIPELINE. Sin ID histórico.

### B024 — Sumarios editoriales no segmentados contaminan `wc_mayoria`

**Componente:** parser.
**Origen / fuente del diagnóstico:** F006 (BITACORA sesión H014).
Equivalente al motivo original de H013.
**Causa raíz:** el parser no separa sumarios editoriales del cuerpo del
fallo. Los sumarios quedan incluidos en `wc_mayoria` inflando el conteo.
**Diagnóstico / evidencia:** sistemático en casos auditados con sumarios
editoriales pre-fallo (caso Lavrentiev `349_p28` entre otros).
**Estado de verificación:** `confirmado_caso_testigo`. Magnitud agregada
no cuantificada.
**Validador propuesto:** el detector v17 de `sumario_con_link` (§4.4.g
PIPELINE) cubre 164 casos con link. Falta detector para sumarios sin link
(formato editorial más viejo). Diseñar detector de "sumario sin link"
análogo. Plan.
**Estado del fix:** parcialmente mitigado. H051 implementó el zonificador
que clasifica sumarios editoriales como zona propia (34 `sumario_editorial`
reclasificados). H055 implementó `residuo_caso_anterior` que excluye
arrastre del word_count (−1,055,756 wc). El impacto cuantitativo en
`wc_mayoria` está sustancialmente reducido. Residual: sumarios dentro del
bloque entre carátula y apertura del fallo que no son residuo del caso
anterior.
**Referencias cruzadas:** F006. H013. H051, H055. PIPELINE §4.4.g (cubre
solo sumarios con link). Sin ID histórico.

### B025 — Falsos `unanime` — re-medido H068 (414→72)

**Componente:** parser (síntoma); causa raíz a nivel catálogo (B045)
+ fallback de `detectar_fin_real` (parser.py 1225-1231).
**Origen / fuente del diagnóstico:** XXI-f del forense. Hipótesis
original sobre `parse_firma` (parser.py línea 449). H024 verifica
mecanismo contra `.md` crudo en caso testigo y refina causa raíz.
**Causa raíz (refinada H024):** composición de tres factores:

1. **B045 (frontera catalográfica mal puesta):** el catálogo trunca
   el caso N al final del bloque, antes de su dispositiva y firma.
   La firma real del caso queda en el bloque del caso N+1.
2. **B022 (arrastre del previo al inicio):** el bloque del caso N+1
   arrastra el cierre del caso N — incluyendo su firma colegiada.
   Tipicamente variante V1b.
3. **Fallback de `detectar_fin_real` (parser.py 1225-1231):** las
   pistas 1, 2, 3 fallan (no hay carátula siguiente dentro del bloque,
   no hay header de sumario en mitad inferior, no hay marcador de
   apertura después del fin dentro del rango limite_adelante). Cae
   a `buscar_atras(linea_es_firma_de_juez, lfc, li)`. Como la firma
   real del caso N+1 fue truncada por B045, no la encuentra al
   retroceder; encuentra primero la firma del caso N arrastrada en
   el inicio del bloque. Cierra ahí.

El caso resultante tiene:
- Cuerpo procesado: sólo las primeras líneas del bloque (= arrastre
  del previo).
- Firma capturada: la firma del caso anterior.
- `voting_pattern = unanime` espurio (porque la firma del previo
  suele ser colegiada plana sin disidencias ni votos).
- Cuerpo real del caso queda como catch_all (no procesado).

**Diagnóstico / evidencia:**
- **Cardinalidad:** 414 casos con `voting_pattern=unanime` en cruce
  del Bloque B (XXI, 3-4/5/2026). Estimación pre-fix §3.6.a. Post
  fix §3.6.a (B001 resuelto) el número puede haberse reducido —
  pendiente re-medición.
- **Caso testigo verificado (H024):** `343_p2243` (Salvatierra y Otros
  s/ Daño agravado). Bloque `LibroVol343-3.md` líneas 30534-31027
  (494 líneas, gap +485 — el más extremo de la muestra H022).
  Verificación con regex y lectura dirigida del código:
  - L8-L9 (= líneas absolutas 30541-30542) contienen firma colegiada
    Rosenkrantz/Maqueda/Lorenzetti/Rosatti del caso anterior "Gente
    Grossa S.R.L." sobre publicación satírica (= B022 V1b al inicio).
  - L17-L18 (= líneas absolutas 30549-30550) contienen carátula real
    del Salvatierra.
  - El bloque del catálogo cierra en línea 31027 al medio del
    considerando 4° del Salvatierra. No hay "Por ello", no hay
    dispositiva, no hay firma del Salvatierra dentro del bloque
    (= B045 al final).
  - `detectar_fin_real` cae al fallback en línea 1226 y captura la
    firma del Gente Grossa de L8-L9. Caso registrado con
    `voting_pattern=unanime` y firma "Rosenkrantz/Maqueda/Lorenzetti/
    Rosatti" en lugar de la firma real del Salvatierra (que está
    más allá de 31027, junto con la dispositiva).

**Estado de verificación:** `confirmado_mecanismo`. Sube desde
`sospecha_cardinal` (XXI-f). Mecanismo verificado byte por byte en
un caso testigo + causa raíz identificada en código + cardinalidad
estimada en 414 casos (pendiente re-medición post §3.6.a).
**Validador propuesto:**
1. Re-medir post §3.6.a contra CSV vivo del 14/5
   (`output/parser/csjn_casos.csv`). Filtrar
   `voting_pattern=unanime` + `wc_mayoria` muy bajo (proxy de cuerpo
   procesado mínimo, consistente con captura sólo del arrastre).
2. Sample dirigido de N=5 contra `.md` para verificar que los casos
   filtrados tienen B045 (truncamiento al final) + B022 (firma del
   previo al inicio). Plan.

**Estado del fix:** no diseñado. Acoplado a B045 (causa raíz). Si se
fixea B045 a nivel catálogo, B025 desaparece por construcción (el
fallback de `detectar_fin_real` no se activaría porque la firma real
del caso estaría dentro del bloque).
**Referencias cruzadas:** XXI-f. H022 §3.1 (mecanismo M1). H024
(verificación con `343_p2243` y refinamiento de causa raíz). B045
(causa raíz). B022 (mecanismo intermedio). Sin §X.Y en PIPELINE.
Sin ID histórico.

**Nota H062:** la cardinalidad 414 es dato pre-fix (sesión XXI, 3-4/5).
Desde entonces se aplicaron B001 (cruzador), B069 (Pista 1 atrás
eliminada), B074 (guard posicional), A001 (firma inversa), B055 (firma
truncada), H055 (residuo_caso_anterior). El número real post-fixes es
desconocido y probablemente mucho menor. Re-medición prioritaria.

**Re-medición H068 (2026-05-24).** Pool unanime = 3508.
`pista_fin = firma_actual` (mecanismo B025): **72 casos** (2.1% del pool,
era ~11.8%). Análisis por dos señales cruzadas:

- **Cat A (14, falsos seguros):** `status_localizacion` contiene
  `ancla_catalogo` + `considerando_text` empieza con header de tomo
  (arrastre puro, sin apertura ni considerando propio). Caso testigo
  `343_p2243` acá.
- **Cat B (6, ambiguos):** `ancla_catalogo` pero con "Considerando:"
  legítimo. Podrían ser per curiam cortos con firma_actual correcta.
  2 tienen `wc_mayoria = 7` (sospechoso pero texto coherente).
- **Cat C (9, prob. legítimos):** localización `ok`, considerando normal.
  Firma_actual fue fallback correcto.

Discriminadores: `ancla_catalogo` sobrerrepresentado 8x (65.5% en B025
vs 8.3% corpus). Tasa unanime corregida: 61.5-61.7% (vs 61.9% sin
corregir). Δ = 0.2-0.4pp.

Cardinalidad actualizada: **14-20 falsos** (piso cat A, techo A+B),
down from 414.

**Corrección parcial H069:** fix bidireccional en fallback firma_actual
(B045 H069) corrige 3 falsos unanime en el re-run: unanime→disidencia (1),
unanime→segun_su_voto (2). + 1 sin_firma→unanime. unanime: 3508→3505.
Cardinalidad residual estimada: **11-17 falsos** (los restantes cat A
que no cambiaron de vp porque el caso era genuinamente unanime con firma
arrastrada — firma diferente pero mismo patrón de votación).

### B026 — `V.` mayúsculas en tomos 329-330 (subtítulos editoriales viejos)

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-h del forense.
**Causa raíz:** el parser no tiene detector para el formato editorial
`NOMBRE V. NOMBRE` que aparece como subtítulo en tomos viejos antes de
`Autos y Vistos;` o `Autos y Vistos:`.
**Diagnóstico / evidencia:** ~1.211 nulos en tomos 329-330 (sesión IX).
Tipo de nulo no especificado en XXI (probable: `case_name_cuerpo` vacío
en el régimen 2008-2011).
**Estado de verificación:** `hipotesis_no_verificada` para el mecanismo.
La magnitud (1.211 nulos) es cuantificada, pero no se confirmó que estos
nulos sean efecto del formato `V.` mayúsculas y no de otro patrón.
**Validador propuesto:** filtrar tomos 329-330 por `case_name_cuerpo` vacío
y verificar manualmente en 5-10 casos si tienen el formato `NOMBRE V.
NOMBRE` antes de `Autos y Vistos`. Plan.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** XXI-h. Sin §X.Y en PIPELINE. Sin ID histórico.

### B027 — `Autos y Vistos;` / `Autos y Vistos:` sin regex específica (V4/V5)

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-i del forense.
**Causa raíz:** el parser actual no tiene regex específica para esos
marcadores fuera del fallback archivado en el bloque de XVII. Cuando un
fallo abre con `Autos y Vistos;` (sin carátula entre comillas), V1 no
captura y la lógica del parser cae a paths no diseñados.
**Diagnóstico / evidencia:** mencionado en XXI sin caso testigo concreto.
Magnitud desconocida.
**Estado de verificación:** `hipotesis_no_verificada`.
**Validador propuesto:** grep en `markdowns_v2/*.md` por `Autos y Vistos`
y cruzar con casos donde V1 no acertó. Cuantificar. Plan.
**Estado del fix:** no diseñado. Probable: agregar regex específica como
fuente adicional para V1 / `case_name_cuerpo`.
**Referencias cruzadas:** XXI-i. Sin §X.Y en PIPELINE. Sin ID histórico.

### B028 — `find_tribunal_origen` ventana excede el bloque

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-k del forense. Equivalente a
PIPELINE §4.6.a (B006 era el cerrado por daño efectivo ~0; este es el
mismo bug aritmético pero como entrada viva con prioridad baja).
**Causa raíz:** ver PIPELINE §4.6.a. Aritmética
`apertura_idx + len(bloque)` excede el bloque cuando `apertura_rel > 0`.
**Diagnóstico / evidencia:** ver PIPELINE §4.6.a.
**Estado de verificación:** `confirmado_cuantificado` (daño efectivo ~0
post §3.6.a).
**Validador propuesto:** ya cuantificado. No requiere validador adicional.
**Estado del fix:** diseñado (PIPELINE §4.6.a tiene el código corregido).
Prioridad baja (cosmético post §3.6.a). Aplicar como higiene del código.
**Referencias cruzadas:** PIPELINE §4.6.a. XXI-k.
**Nota:** redundante con B006. B006 documenta el cierre conceptual (daño
~0); B028 está acá como recordatorio de que el fix de higiene sigue
pendiente. Si se aplica el fix, ambos pasan a CERRADO. Si se decide no
aplicar, B028 puede mergearse con B006 en una próxima pasada del documento.

### B031 — `linea_es_header_sumario` requiere MAYÚSCULAS en primeros 5 caracteres

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-n del forense.
**Causa raíz:** `parser.py` línea 1077. Si el sumario empieza con
capitalización mixta (formato corpus moderno), no matchea.
**Diagnóstico / evidencia:** identificado leyendo código en XXI. Sin
medición.
**Estado de verificación:** `hipotesis_no_verificada`.
**Validador propuesto:** grep en `markdowns_v2/*.md` por headers de
sumario en capitalización mixta. Verificar si esos casos tienen
`is_sumario_con_link=False` cuando deberían tener `True`. Plan.
**Estado del fix:** no diseñado. Salida natural: relajar el match a
`re.IGNORECASE` o detectar mayúsculas en porción mayor del header.
**Referencias cruzadas:** XXI-n. Sin §X.Y en PIPELINE. Sin ID histórico.

### B032 — `RE_VOTO_HDR` requiere "Señor[es]" / "Vicepresidente" / etc. — CERRADO H063

**Componente:** parser.
**Fix aplicado (H063):** agregado `|l[ao]s?` al grupo de artículos en
`RE_VOTO_HDR` (L160) y `RE_DISID_HDR` (L165). Validación corpus completo:
+13 votos, +3 disidencias, 0 regresiones. Todos Argibay, tomos 329–332.
Impacto: corrección de `n_votos_svoto`/`n_disidencias` en 16 casos y
mejor delimitación de `texto_voto`. Filas de votos sin cambio (generadas
por `parse_firma`, no por RE_VOTO_HDR).

### B033 — `cargar_localizados` no filtra `ultimo_del_tomo_sin_fin`

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-o del forense.
**Causa raíz:** `parser.py` línea 1735. Los casos con status
`ultimo_del_tomo_sin_fin` entran al loop con `linea_fin` vacía y el
bloque se extiende hasta el final del archivo, arrastrando todo el
aparato editorial e inflando word counts.
**Diagnóstico / evidencia:** XXI-o identifica el mecanismo leyendo código.
PIPELINE §4.6.g cubre el caso análogo con `fallo_cruza_archivos` (20 casos
post-fix con outlier máximo `wc_mayoria=105.559`). Probable que B033 sea
una variante del mismo síndrome.
**Estado de verificación:** `hipotesis_no_verificada` para el mecanismo
específico de `ultimo_del_tomo_sin_fin`. La magnitud y los casos
específicos no están listados.
**Validador propuesto:** identificar casos con
`status_localizacion=ultimo_del_tomo_sin_fin` en CSV y verificar
`word_count`. Comparar contra distribución del corpus. Plan.
**Estado del fix:** no diseñado. Salida natural análoga a la mitigación
de §4.6.g: filtrar este status antes de procesar.
**Nota H062:** en producción normal, `--corpus` siempre se pasa al cruzador,
por lo que `ultimo_del_tomo_sin_fin` nunca se asigna (se usa
`ok_cortado_en_indice` o `ultimo_del_tomo` con linea_fin válido). El riesgo
real es ~0. Degradado a nota/cosmético.
**Referencias cruzadas:** XXI-o. PIPELINE §4.6.g (dominio relacionado).
Sin ID histórico.

### B034 — `RE_FECHA_LINEA` no cubre formatos con paréntesis o guiones

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-p del forense.
**Causa raíz:** `parser.py` líneas 58-59.
`RE_FECHA_LINEA = r"^Buenos Aires[,]?\s+\d{1,2}..."`. No cubre
`(Buenos Aires, 14 de marzo...)` o `Buenos Aires - 14 de...`.
**Diagnóstico / evidencia:** identificado leyendo código en XXI. Sin
medición. Caso testigo no proporcionado.
**Estado de verificación:** `hipotesis_no_verificada`.
**Validador propuesto:** grep en `markdowns_v2/*.md` por patrones de
fecha con paréntesis o guiones y cruzar con casos donde la columna
`date` está vacía. Plan.
**Estado del fix:** no diseñado. Salida natural: extender regex para
cubrir variantes.
**Referencias cruzadas:** XXI-p. Sin §X.Y en PIPELINE. Sin ID histórico.

### B035 — Fecha sin marcador de apertura captura del dictamen

**Componente:** parser.
**Origen / fuente del diagnóstico:** PIPELINE §4.6.c.
**Estado:** ya documentado en PIPELINE. La entrada acá apunta para
trazabilidad.
**Diagnóstico / evidencia:** ver PIPELINE §4.6.c. 35 casos potencialmente
afectados. Validación contra `.md` pendiente para 2-3 casos.
**Estado de verificación:** `confirmado_cuantificado` (35 casos como cota
superior).
**Validador propuesto:** ya identificado en PIPELINE — auditar 2-3 casos
con `apertura_tipo=''`, `tipo_entrada='fallo'`, `date != ''` contra `.md`.
**Estado del fix:** diseñado (PIPELINE §4.6.c). Cambio menor, requiere
reordenar flujo. No aplicado.
**Referencias cruzadas:** PIPELINE §4.6.c. Sin equivalente en XXI ni en
BITACORA. Sin ID histórico.

### B036 — `extraer_textos_votos` incluye el header del voto

**Componente:** parser.
**Origen / fuente del diagnóstico:** PIPELINE §4.6.d.
**Estado:** ya documentado en PIPELINE. Probable que sea decisión de
diseño intencional, no bug.
**Diagnóstico / evidencia:** ver PIPELINE §4.6.d. Inflado constante de
`wc_voto` por ~10 palabras (header del voto). No altera la clasificación
A/B/C/D/E en ningún caso plausible.
**Estado de verificación:** `confirmado_cuantificado` con efecto medido
nulo en clasificación.
**Validador propuesto:** no se requiere — el efecto ya está cuantificado
como no-impactante.
**Estado del fix:** decisión pendiente — confirmar si es intencional
(permite que `clasificar_tipo_voto` use info del header) y reescribir
comentario, o aplicar fix mínimo (cambiar `range(k_ini, k_fin)` a
`range(k_ini + 1, k_fin)`).
**Referencias cruzadas:** PIPELINE §4.6.d. Sin equivalente. Sin ID
histórico.

### B037 — `dictamen_presente == '0'` (string) en `sumario_con_link`

**Componente:** parser.
**Origen / fuente del diagnóstico:** PIPELINE §4.6.e.
**Estado:** ya documentado en PIPELINE. Inconsistencia de tipos en output.
**Diagnóstico / evidencia:** ver PIPELINE §4.6.e. 164 filas con
`dictamen_presente == '0'` (string) en lugar de booleano. Coincide
exactamente con `tipo_entrada == 'sumario_con_link'`.
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto:** ya identificado.
**Estado del fix:** diseñado (PIPELINE §4.6.e). No aplicado.
**Referencias cruzadas:** PIPELINE §4.6.e. Sin equivalente. Sin ID
histórico.

### B038 — `fallo_cruza_archivos` produce bloques gigantescos (residual)

**Componente:** parser (efecto), cruzador (origen).
**Origen / fuente del diagnóstico:** PIPELINE §4.6.g. Re-evaluado
2026-05-09 (20 casos post-fix B001).
**Estado:** ya documentado en PIPELINE. Prioridad media. Mitigación
temporal: filtrar `status_localizacion in ('fallo_cruza_archivos',
'fallo_cruza_archivos_sin_marcador')` antes del análisis estadístico
(20/5.819 = 0,3% de cobertura).
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto:** ya identificado.
**Estado del fix:** dependiente de Etapa 3 (corregir asignación de
`linea_fin` para cruza_archivos). No aplicado.
**Referencias cruzadas:** PIPELINE §4.6.g. Sin equivalente en XXI ni en
BITACORA con ese nombre. Sin ID histórico.

### B043 — `primer_token_de_caratula` no excluye sustantivos institucionales genéricos

**Componente:** parser.
**Origen / fuente del diagnóstico:** H023 sección M2 (verificación de
B018 contra .md crudo).
**Causa raíz:** `primer_token_de_caratula` (parser.py líneas 1138-1150)
itera tokens de longitud ≥ 4 de la primera mitad de la carátula (lo
que está antes del `|` que separa actor de demandado) y devuelve el
primero que no esté en una lista de exclusión. La lista actual cubre
`otro/otros/sociedad/sucesion/sucesión/empresa/compania/compañia/
compañía` — pensada para evitar genéricos relacionados con tipos
societarios. No cubre sustantivos institucionales que aparecen
masivamente como cabeza de carátula en casos de competencia:
`provincia/estado/nación/nacional/ciudad/banco/ministerio/
municipalidad/universidad/superintendencia/dirección/administración/
instituto/secretaría/gobierno`. El token devuelto en esos casos es
una palabra de uso común que aparece naturalmente en el cuerpo de
casi cualquier fallo.
**Diagnóstico / evidencia:** testigo `339_p1393`, caso siguiente
`PROVINCIA DEL NEUQUÉN c/ VITAL SOJA S.A.`, primer_token devuelto =
`Provincia`. Cuatro apariciones de "provincia" en el bloque del caso
actual (dos en el dictamen, una en la dispositiva, una al inicio de
la carátula del siguiente). La pista 1 de `detectar_fin_real`
matchea contra una de las apariciones interiores. Esta es la causa
inmediata del comportamiento documentado en B018 V2.
**Caso patológico no resuelto por engrosar lista:** carátulas como
`PROVINCIA DE BUENOS AIRES c/ Y.P.F.` tienen **todos los primeros
tokens contaminados** (`PROVINCIA`, `BUENOS`, `AIRES`). Excluirlos
todos lleva el token a `Y.P.F.` si el regex lo acepta, o a cadena
vacía. Engrosar la lista de exclusión es paliativo, no solución.
**Estado de verificación:** `confirmado_mecanismo` (causa raíz en
código + un testigo claro `339_p1393` + caso patológico identificado).
**Validador propuesto:** script que recorra `csjn_casos.csv`,
calcule `primer_token_de_caratula` para cada caso, y cuente cuántas
veces el primer_token cae en la lista de sustantivos institucionales
genéricos. Sirve para acotar el universo de casos potencialmente
afectados por B018 V2.
**Estado del fix:** acoplado a B018. La opción A de la matriz de
fixes de B018 (engrosar lista de exclusión) ataca esto pero tiene
techo bajo. La opción D (validación cruzada con `proximo_header_pagina`)
hace que el defecto de B043 sea inocuo en la pista 1 sin necesidad de
arreglar `primer_token_de_caratula`. Por eso B043 no requiere fix
propio si se aplica D en B018. Si después se quiere usar `primer_token`
para otra cosa (ej. validación de carátula del caso actual), B043 sí
hay que fixarlo aparte.
**Referencias cruzadas:** H023 sección M2. Acoplado a B018 (alimenta
V2). Sin §X.Y en PIPELINE. Sin ID histórico.

### B044 — Apertura espuria de span voto sobre header de voto arrastrado del previo

**Componente:** parser.
**Origen / fuente del diagnóstico:** H022 §3.2 propuso B044 (mecanismo
M5). H024 verifica contra `.md` crudo, corrige etiología y refina
causa raíz.
**Causa raíz:** composición de dos defectos acoplados:

1. **B022 V2b al inicio del bloque:** el bloque arrastra del caso
   anterior un **voto unipersonal completo** (header
   `Voto del señor ministro doctor don X` + `Autos y Vistos:` +
   cuerpo del voto + firma simple), ~10 líneas. Variante caracterizada
   en H024 al verificar `332_p244`.
2. **Falta de guardia espacial en parser.py 1513-1552:** el loop
   principal de `procesar_archivo` arranca en `k=0` y recorre todo
   el bloque sin restringir a "después de la apertura del caso
   actual". `RE_VOTO_HDR` (parser.py 142) se evalúa sobre cada línea
   del bloque, incluyendo las que están antes de `apertura_rel` o
   antes de la carátula del caso. La protección de `en_dictamen`
   (1518-1529) sólo cubre matches dentro del dictamen detectado, no
   matches en el rango pre-apertura.

Cuando el header de voto arrastrado matchea `RE_VOTO_HDR`, el parser
lo agrega a `marcadores_votos` (línea 1543) como voto del caso
actual. Después, `extraer_textos_votos` (parser.py 559-582) toma el
rango desde el match espurio hasta el siguiente marcador, produciendo
un span voto que envuelve todo lo que hay en el medio: carátula +
sumarios + dictamen + cuerpo del caso + firma colegiada de la
mayoría.

**Diagnóstico / evidencia:** caso testigo verificado byte por byte
en H024:
- `332_p244` (Fernández c/ Fed. Asoc. Católicas). Bloque
  `LibroVol332.1.md` líneas 9536-9713 (178 líneas).
  - L3-L12 arrastre de voto unipersonal de Petracchi sobre causa de
    competencia previa (Santa Fe vs Civil 26 sobre quiebra). L3
    `"Voto del señor ministro"` + L4
    `"doctor don Enrique Santiago Petracchi"` + L12
    `"Enrique Santiago Petracchi."` (firma simple).
  - L13-L14 carátula real `ELVA GRACIELA FERNANDEZ c/ FEDERACION de
    ASOCIACIONES / CATOLICAS de EMPLEADAS ASOCIACION CIVIL`.
  - L62 apertura real del FALLO del Fernández.
  - L117 `"Voto de los señores ministros doctores"` (voto legítimo
    Petracchi-Zaffaroni "según su voto").
  - L166 `"Voto del señor ministro"` (voto legítimo Maqueda "según
    su voto").
  - Producción: `n_votos=3` (uno espurio L3 + dos legítimos L117/L166).
  - Span voto espurio resultante: L3 a L117 = 114 líneas (cuadra con
    cifra reportada por H022), envolviendo carátula + sumarios +
    dictamen del Procurador + cuerpo plenario del Fernández + firma
    colegiada de la mayoría.

**Etiología corregida respecto de H022:** H022 propuso que el match
espurio venía de "una sentencia per saltum vieja del propio caso".
Verificación contra `.md` muestra que es **arrastre del caso
anterior**, no per saltum del propio caso. El mecanismo subyacente
H022 acertó correctamente (`RE_VOTO_HDR` matchea header que no
pertenece al caso actual), pero la etiología debe leerse como
B022 V2b, no como per saltum.

**Estado de verificación:** `confirmado_mecanismo`. Causa raíz en
código + un testigo verificado byte por byte del `.md` y del CSV.
**Validador propuesto:** corrida sobre corpus completo del filtro
`invariante_disjuncion=False AND n_votos >= 1`. En la muestra H022
sólo `332_p244` cumple. Cuantificación esperada baja pero daño por
caso muy alto (span voto envuelve cuerpo entero del fallo y contamina
`wc_voto`, `voting_pattern`, conteos de jueces, etc.). Plan.
**Estado del fix:** no diseñado. Dos vías independientes:
- **Vía A (estructural, vía B045):** fijar la frontera catalográfica
  elimina el arrastre. Sin arrastre, sin header espurio. B044
  desaparece sin necesidad de tocar el loop de votos.
- **Vía B (guardia espacial en parser.py 1513-1552):** introducir
  `if k < apertura_rel: continue` (o equivalente con `idx_caratula`)
  antes de aplicar `RE_VOTO_HDR`/`RE_DISID_HDR`/`RE_DICT_HDR`. Cubre
  una familia de bugs análogos sobre otros detectores estructurales
  además de B044.

La vía A es estructuralmente preferible (cierra B022/B025/B044
simultáneamente). La vía B es complementaria (cubre matches espurios
de regex estructural en otros escenarios donde no haya arrastre).
**Interacciones con otros bugs:**
- **B045** (causa raíz arquitectónica): si se elimina el arrastre,
  desaparece B044.
- **B022 V2b** (mecanismo intermedio).
- **B040** (auditor): mismo mecanismo en el auditor. H022 §3.2 lo
  predijo correctamente. B044 lo extiende al parser.
**Referencias cruzadas:** H022 §3.2 (propuesta original, reformulada
H024). H023 (lección metodológica). H024 sección M5 (verificación y
corrección). B045, B022, B040. PIPELINE §4.4.k (loop principal).
Sin ID histórico.

---

### B048 — `detectar_fin_real` tiene dos modos de falla independientes

**Componente:** parser (`parser.py`) — función `detectar_fin_real` y
heurísticas relacionadas.
**Origen / fuente del diagnóstico:** H026 (auditoría `--random 80`
del 2026-05-16).
**Causa raíz:** `detectar_fin_real` falla sistemáticamente de dos
maneras distintas en la muestra:

- **Modo A — corta a mitad de oración del considerando.** La línea
  declarada como fin del fallo cae dentro del cuerpo del considerando,
  no en el cierre dispositivo ni en la firma. Aparece en 25 de 62
  catch_all iniciales (40,3 % de la muestra). Síntoma: el catch_all
  inicial del N+1 comienza con minúscula (continuación de oración).
  Hipótesis de causa raíz: pista de fin que matchea texto del cuerpo
  (falso positivo de `pista_fin`), o regex de cierre con anclaje
  demasiado laxo.

- **Modo B — corta antes del cierre dispositivo.** La línea declarada
  como fin cae antes del "Por ello" o equivalente. Aparece en 10 de
  62 catch_all iniciales (16,1 % de la muestra). Síntoma: el catch_all
  inicial del N+1 comienza con "Por ello", "Por lo expuesto" o "Por
  lo tanto". Hipótesis de causa raíz: `RE_CONSIDERANDO` o equivalente
  fallando en variantes léxicas del cierre dispositivo.

**Diagnóstico / evidencia:**

- 35 de 62 catch_all iniciales (56,4 %) en la muestra `--random 80`
  son modo A o modo B combinados. En más de la mitad del corpus
  `detectar_fin_real` corta sustancialmente antes del cierre real.
- Casos testigo modo A: `330_p4129`, `340_p658`, `329_p1501`,
  `330_p3758`, `348_p756`, `332_p274`, `347_p257`, `346_p537`,
  `332_p1346`, `330_p2574`, `347_p785`, `331_p2784`, entre otros.
- Casos testigo modo B: `329_p4577`, `329_p3890`, `330_p1564`,
  `330_p4129`, `340_p658`, `340_p1294`, `338_p1347`, `339_p490`,
  `343_p140`, `347_p614`, `331_p530`, `349_p28`.

**Estado de verificación:** `confirmado_cuantificado` (muestra n=80).
Causa raíz a diagnosticar para cada modo.

**Validador propuesto:** diagnóstico dirigido sobre 3-5 casos testigo
por modo, trazando línea por línea qué decide el corte en
`detectar_fin_real`. Una vez identificada la causa raíz, fix dirigido
+ re-corrida `--random 80` para validar la reducción del catch_all
inicial.

**Estado del fix:** no diseñado. Bloqueado por diagnóstico fino de
causa raíz.

**Interacciones con otros bugs:** B048 es subdiagnóstico técnico del
mecanismo de B045 manifestación B. Mientras B045 documenta el síntoma
arquitectónico (frontera mal puesta, arrastre observable), B048
identifica los modos específicos de falla del componente que produce
el síntoma. Pueden coexistir: B045 sigue siendo el cuadro causal
unificado; B048 detalla los modos del parser cuya corrección
contribuye a reducir B045. La corrección de B048 NO resuelve por sí
sola B045: queda el componente "epílogo arrastrado" (B047, 25,8 % de
la muestra) y el componente "carátula no detectada" (B049, 12,9 %).

**Referencias cruzadas:** B045 (síntoma arquitectónico), B047
(componente arquitectónico complementario), B049 (componente del
auditor complementario). BITACORA H026 sección "Fase D — análisis
empírico del catch_all". Sin ID histórico.

---

## Deuda ACTIVA — Auditor (`auditar_fallo.py`)

Bugs de la herramienta de diagnóstico. No afectan el corpus producido,
pero afectan la calidad de las auditorías que se usan para diagnosticar
bugs del pipeline.

### B040 — Auditor emite spans de fallos previos arrastrados

**Componente:** auditor.
**Origen / fuente del diagnóstico:** F007 (BITACORA sesión H014, línea 370).
**Causa raíz:** `detectar_votos_y_disidencias()` en `auditar_fallo.py` busca
matches de `RE_VOTO_HDR` y `RE_DISID_HDR` en TODO el bloque. Cuando el
bloque arrastra contenido del fallo previo (= B022, F004), los headers de
voto/disidencia del previo matchean y se emiten como spans del actual.
**Diagnóstico / evidencia:** 4 casos con disjunción rota en muestra de 50
(BITACORA línea 368).
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** corrida `--random 50` con detector de borde
superior (análogo al de borde inferior, no implementado todavía). Plan.
**Estado del fix:** no diseñado. Acoplado con B022 (mientras el parser
arrastre fallo previo, el auditor va a heredarlo).
**Referencias cruzadas:** F007. Sin ID histórico.

### B041 — Off-by-one entre auditor y `.md`

**Componente:** auditor.
**Origen / fuente del diagnóstico:** F008 (BITACORA sesión 2026-05-09,
línea 476).
**Causa raíz:** no diagnosticada al nivel de mecanismo. Posible bug en el
renderer absoluto/relativo del auditor o bug real en cálculo de offsets.
**Diagnóstico / evidencia:** caso testigo `339_p1648`. Span 17 del reporte
dice `firma (26598-26598)` con texto "Ricardo Luis Lorenzetti – Elena I.
Highton de Nolasco – Juan", pero la línea 26598 del `.md` real es
"mencionada localidad bonaerense." (la firma está en 26599-26600).
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** investigar en sesión separada. Mirar funciones
de conversión absoluta/relativa del renderer del auditor. Plan.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** F008. Sin ID histórico.

### B042 — Colisión de timestamp en `auditar_fallo.py`

**Componente:** auditor.
**Origen / fuente del diagnóstico:** F-AUDITOR-01 (BITACORA sesión
2026-05-09, línea 911).
**Causa raíz:** `auditar_fallo.py` línea 1694: `ts = datetime.now().strftime
("%Y-%m-%d_%H-%M-%S")` con resolución de segundos. `out_path.write_text
(md, encoding="utf-8")` sobreescribe sin avisar.
**Diagnóstico / evidencia:** tres llamadas seguidas el 9/5
(`333_p2420`, `330_p1854`, `330_p2746`) cayeron todas en `21-15-54`,
las dos primeras se perdieron. Hubo que reorrer las dos.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** trivial. Tres llamadas seguidas verifican el fix.
**Estado del fix:** diseñado y trivial (agregar microsegundos al timestamp,
o sufijo numérico cuando el archivo ya existe). No aplicado.
**Referencias cruzadas:** F-AUDITOR-01. Sin ID histórico.

---

### B047 — Modelo de spans del auditor sin producción `epilogo`

**Componente:** auditor (`auditar_fallo.py`) — modelo de spans
tipados.
**Origen / fuente del diagnóstico:** H026 (auditoría `--random 80`
del 2026-05-16 + lectura conceptual de la gramática del fallo).
**Causa raíz:** el modelo de spans tipados del auditor tiene 10 tipos
(carátula, sumario, dictamen, cuerpo_mayoria, voto, disidencia,
firma, sumario_con_link, header_pagina, catch_all). Falta una
producción para el bloque editorial post-firma que contiene:
componentes de partes y representación letrada, tribunal de origen,
tribunales intervinientes anteriores, eventualmente nota al pie con
link. Este bloque está editorialmente presente en la mayoría de los
casos del corpus pero, al no tener span propio, cae en `catch_all`
cuando queda dentro del bloque del caso correcto, o arrastra al
catch_all inicial del caso siguiente cuando `detectar_fin_real`
corta antes (acumulándose con B045 manifestación B y los modos de
falla de B048).

**Diagnóstico / evidencia:**

- 23 de 48 catch_all finales (48 %) de la muestra `--random 80` son
  epílogo propio puro: 4-10 líneas con orden interno estable. Ver
  gramática completa en `docs/GRAMATICA_DEL_FALLO.md` (sección "El
  epílogo: producción faltante").
- 16 de 62 catch_all iniciales (25,8 %) de la misma muestra son
  epílogo del caso anterior arrastrado al inicio del N+1. La
  combinación catch_all final + catch_all inicial cubre todos los
  destinos posibles del epílogo cuando no tiene span propio.
- Marcadores explícitos identificados (9): bloque_recurso,
  bloque_traslado, bloque_partes_alt, bloque_nombres_legacy,
  tribunal_origen, tribunales_intervinientes, profesionales, tercero,
  continuacion_firma. Detalle de regex en
  `docs/GRAMATICA_DEL_FALLO.md`.

**Fix esperado:** agregar `TIPO_EPILOGO = "epilogo"` al modelo, con
sub-spans opcionales tipados (`epilogo_recurso`, `epilogo_traslado`,
`epilogo_tribunal_origen`, etc.) o atributos del span. Implementar
`detectar_epilogo(bloque, headers_pagina, firma_fin)` análogo a
`detectar_borde_inferior`. Mover la lógica de extracción de tribunal
de origen y partes (hoy en `parser.py` líneas 365-444) a operar sobre
el span detectado en vez de búsqueda en todo el bloque.

**Estado de verificación:** `confirmado_cuantificado` (muestra n=80).
Pendiente verificación de persistencia editorial sobre el corpus
completo (M06): ¿el epílogo es estable entre tomos 329 y 349? ¿hay
drift editorial en marcadores?

**Estado del fix:** hallazgo de H026, no implementado. Bloqueado por
M06.

**Interacciones con otros bugs:** resuelve el 25,8 % del catch_all
inicial documentado en B045 manifestación B. Junto con un detector
de borde superior (provisto implícitamente al extender el span
`epilogo` del caso N hasta la carátula del N+1) cubre el componente
arquitectónico del problema. Los modos de falla del parser (B048) y
el detector de carátula (B049) son separables y requieren fix propio.

**Referencias cruzadas:** B045 (familia arquitectónica común,
contribuye a la cara de arrastre al N+1), B048 (modos de falla
complementarios del parser), B049 (carátula no detectada del N+1).
`docs/GRAMATICA_DEL_FALLO.md` sección "El epílogo: producción
faltante". BITACORA H026 sección "Fase D — análisis empírico del
catch_all". Sin ID histórico.

---

### B049 — Detector de carátula del auditor falla en carátulas partidas

**Componente:** auditor (`auditar_fallo.py`) — función
`detectar_caratula` (línea 499).
**Origen / fuente del diagnóstico:** H026 (auditoría `--random 80`
del 2026-05-16). Causa raíz refinada por lectura de código en H027.
Verificación empírica sobre 8 testigos y fix implementado en H028.
**Causa raíz:** `detectar_caratula` retrocede exactamente una línea
no-vacía no-header_pagina desde el primer header de sumario con `:`
(Estrategia 1, líneas 548-556) o devuelve la línea previa al primer
header de sumario (Estrategia 2, línea 571). No verifica si la línea
encontrada es una carátula completa ni si es continuación de la
línea anterior.

Dos variantes de falla identificadas en Fase D2 (H028):

- **Var-A (4 casos):** la carátula está partida en dos líneas por
  salto de página editorial. El catch_all absorbe la primera línea
  junto con el epílogo anterior; el detector retrocede una línea y
  encuentra solo la segunda mitad (sin `c/`, `s/` ni `|`).
  Casos auditados: 331_p1516, 344_p2665, 348_p751, 348_p1505.

- **Var-B (1 caso):** la carátula detectada es la firma del caso
  anterior al auditado — doble solapamiento hacia atrás.
  Caso: 340_p1551.

**Nota sobre IDs:** el auditor con `--pagina N` audita el caso que
*termina* en página N (`fin_extendido_pag_compartida`), no el que
empieza. Los IDs de H026 (331_p1519, 344_p2669, 348_p755, 348_p1511,
340_p1554, 343_p988, 348_p1352, 348_p1277) son del parser (caso
siguiente); los IDs auditados (caso anterior) son los listados arriba.
343_p987 y 348_p1351 no presentaron falla. 348_p1351 es
`sumario_con_link`, no aplica.

**Diagnóstico / evidencia:**

- 5/7 casos evaluables con carátula espuria (71 %).
- Verificación de código: Estrategia 1 retrocede una sola línea
  (auditar_fallo.py líneas 548-556). Sin verificación de formato
  ni concatenación con línea anterior.
- Señal disponible no usada: en Var-A la línea candidata no contiene
  `c/`, `s/` ni `|`. La línea anterior sí tiene la primera parte.

**Cruce con corpus productivo:** los 8 casos tienen `case_name_indice`
correcto en `csjn_casos.csv`. B049 es bug del auditor únicamente.
Corpus productivo sano.

**Fix implementado (H028, Var-A):** en Estrategia 1 y Estrategia 2,
si la candidata no tiene `c/`, `s/`, `|` y no termina en punto,
se busca la línea anterior y se concatenan con manejo de silabación.
Guardia sobre la línea anterior: no debe ser mes calendario solo
(`ENERO`...`DICIEMBRE`), no debe empezar con `V.` o `v.`, no debe
terminar en punto ni empezar en minúscula.
Validación: seed 15052026, n=80. 7 mejoras, 0 regresiones.

**Fix pendiente (Var-B):** requiere análisis separado. El ancla al
último header de página antes del dictamen/apertura reduce el rango
de búsqueda pero no resuelve si la firma del previo está dentro de
esa ventana.

**Estado de verificación:** `confirmado_cuantificado` (n=80 H026) +
`verificado_testigos` (8/8 Fase D2 H028).

**Estado del fix:** Var-A implementado y validado (commit H028).
Var-B pendiente de diagnóstico.

**Interacciones con otros bugs:** B049 es la cara dual interna de
B045 manifestación B. B045 corre hacia adelante (N se come parte
del N+1); B049 corre hacia atrás (detector de N+1 no encuentra ancla
y devuelve material del N como carátula). Separable de B048 y B047
en cuanto al fix, aunque los tres comparten origen estructural.

**Referencias cruzadas:** B045, B047, B048. BITACORA H026 Fase D +
H027 Fase A continuación + H028 Fase D2. Sin ID histórico.

### B050 — `detectar_firma_mayoria` puede absorber líneas del epílogo

**Componente:** auditor (`auditar_fallo.py`) — función
`detectar_firma_mayoria` (línea 835), línea 890 en particular.
**Origen / fuente del diagnóstico:** H027 (lectura de código + revisión
de `JUECES_CONOCIDOS` importado de `parser.py`).
**Causa raíz:** el loop de extensión del span de firma (líneas
876-893) acepta como continuación de firma cualquier línea que sea
(a) corta (≤100 chars) y (b) contenga un apellido de
`JUECES_CONOCIDOS`. Ese set tiene 29 patrones, varios con apellidos
comunes en castellano (Otero, Catania, Cavallo, Petrone, Hornos,
Riggi, Mahiques, Figueroa, etc.). Cuando el epílogo del fallo
contiene una línea corta que casualmente menciona un apellido del set
— frecuente en "Recurso de queja interpuesto por X, representado por
Dr. Y" o en "Tribunal de origen: ... — Dr. Z" — la línea se incorpora
al span de firma. El cuerpo de mayoría y la firma quedan correctos en
sus márgenes superiores, pero el span de firma se extiende
inválidamente sobre el epílogo, "comiéndoselo" hacia adelante.

**Diagnóstico / evidencia:** hipótesis no verificada empíricamente.
Surgida por lectura del detector + inspección del contenido de
`JUECES_CONOCIDOS`. Probabilidad alta por el cruce entre:
- 14 conjueces explícitos en `JUECES_CONOCIDOS`, varios con apellidos
  comunes.
- 9 marcadores del epílogo (documentados en
  `docs/GRAMATICA_DEL_FALLO.md`) que típicamente mencionan apellidos
  de letrados, conjueces previos, integrantes de tribunales de
  origen, etc.
- Loop de extensión sin guarda contra esta interacción.

**Validador propuesto:** sobre la corrida `--random 80` ya existente,
contar casos donde el span `firma` reportado por el auditor incluye
líneas que matchean al menos uno de los 9 marcadores del epílogo.
Esos son los casos con contaminación. Cuantificación esperada:
plausible que sea no despreciable (sin estimación numérica firme
hasta correrlo).

**Fix candidato (no diseñado):** en el loop de extensión, antes de
aceptar una línea como continuación de firma por la regla "corta +
contiene apellido conocido", descartar si la línea matchea alguno
de los marcadores del epílogo. Esto introduce dependencia entre dos
detectores que hoy son independientes (firma de mayoría vs epílogo);
es síntoma de que la solución correcta es **implementar primero la
producción `epilogo`** (B047) y entonces la firma extiende solo
hasta el inicio del epílogo, sin necesidad de guardas explícitas.

**Estado de verificación:** `hipotesis_no_verificada`.

**Estado del fix:** no diseñado. Acoplado con B047.

**Interacciones con otros bugs:** acoplamiento conceptual con B047
(producción `epilogo` faltante). Independiente de B045/B048/B049. La
contaminación opera dentro del bloque correcto del caso (no es
arrastre desde el vecino).

**Referencias cruzadas:** B047. BITACORA H027 Fase A continuación
(hallazgo HN4). Sin ID histórico.

### B051 — Último voto/disidencia extendido hasta el fin del bloque absorbe epílogo

**Componente:** auditor (`auditar_fallo.py`) — función
`detectar_votos_y_disidencias` (línea 791), lógica de cierre del
último span (línea 821).
**Origen / fuente del diagnóstico:** H027 (lectura de código).
**Causa raíz:** la función genera spans para cada voto o disidencia
detectado; el span termina en `inicios[i+1] - 1` para todos menos
el último, que termina en `len(bloque) - 1`. Cuando hay votos o
disidencias en el fallo, **el epílogo cae por construcción dentro del
span del último voto/disidencia**. El catch_all final no se dispara
porque el voto ya cubre la cola.

**Diagnóstico / evidencia:** hipótesis no verificada
cuantitativamente. Confirmada por lectura del código (la línea 821
es categórica: `k_fin = len(bloque) - 1`). Plausibilidad alta porque:
- Es el mecanismo por el que un caso con votos disidentes nunca
  produce catch_all final aunque tenga epílogo.
- Explica parcialmente por qué la muestra `--random 80` mostró que el
  catch_all final aparece solo en el 55,7 % de los casos: en los
  fallos con votos disidentes, el epílogo está oculto dentro del
  último voto, no en catch_all.

**Validador propuesto:** sobre `--random 80` o sobre el corpus
completo, partición de casos por (a) presencia de votos/disidencias,
(b) presencia de catch_all final. La hipótesis predice que los
casos con votos tienen catch_all final mucho menos frecuente que
los casos sin votos. Adicionalmente, inspección manual de 5-10
spans `voto` o `disidencia` de los más largos de la muestra para
confirmar que sus últimas líneas son contenido editorial post-firma
del voto (epílogo del caso), no contenido del razonamiento del
ministro.

**Fix candidato (no diseñado):** análogo a B050. La solución
estructural es implementar la producción `epilogo` (B047) y entonces
el último voto/disidencia termina antes del inicio del epílogo. Sin
B047, el fix requiere recortar el span del último voto hacia atrás
por marcadores del epílogo, introduciendo el mismo acoplamiento que
discute B050.

**Estado de verificación:** `confirmado_por_lectura_de_codigo`,
cuantificación pendiente.

**Estado del fix:** no diseñado. Acoplado con B047.

**Interacciones con otros bugs:** B051 explica por qué el catch_all
final está sub-representado en los casos con votos. Junto con B047
(modelo sin producción epílogo) y B050 (firma de mayoría se extiende
sobre epílogo), forma el cluster de **bugs del borde inferior
interno** del fallo. Los tres se resuelven naturalmente al
implementar la producción `epilogo` como span propio.

**Referencias cruzadas:** B047, B050. BITACORA H027 Fase A
continuación (hallazgo 8). Sin ID histórico.

---

## Deuda METODOLÓGICA

Pendientes que no son bugs concretos sino mejoras de proceso o
arquitectura. No usan ID `B0NN`.

### M01 — Re-recorrer parser y actualizar PIPELINE.md — CERRADO H062

**Cerrado H062 (auditoría).** PIPELINE.md deprecado a `archivo/docs/PIPELINE_v1.md`.
El documento tenía valor como mapa de las cuatro etapas, pero las secciones de
bugs (§X.Y) quedaron obsoletas tras ~30 sesiones de desarrollo (H035-H061). El
conocimiento vivo de bugs migró íntegramente a DEUDA_TECNICA.md. Actualizar las
secciones de bugs requeriría trabajo de varias sesiones sin beneficio claro: la
fuente única de verdad ya es este archivo.

PIPELINE_HALLAZGOS.md también deprecado a `archivo/docs/` (el propio archivo
declaraba "cuando PIPELINE.md cubra las cuatro etapas, este archivo debería
archivarse").

### M02 — Reorganización del repo (continuación)

La Fase 2 del inventario del repo está abierta. Bloque scripts cerrado
(commits `e695e16`, `e3c53b2`). Bloque docs parcialmente avanzado en
sesión 14/5. Bloque snapshots pendiente (tres snapshots por procesar:
`snapshots/snapshot_2026-05-02_1559/`, `snapshots/snapshot_pre_reorg_2026-05-02_1843/`,
`archivo/snapshots_ad_hoc/pre_fix_xii_20260503_1308/`).

Una decisión ya tomada (XXI): `csjn_casos_pre_refactor_subloques.csv` y
su par de votos son byte-a-byte idénticos al productivo (MD5 confirmado).
Pueden archivarse cuando se llegue al bloque snapshots.

**Acción pendiente:** sesión dedicada al bloque snapshots de la Fase 2.
Después, Fase 3 (zona oscura) y Fase 4 (hallazgos laterales acumulados:
`.pytest_cache/` raíz, `scripts/pipeline/parser.py.bak` del 9/5).

### M03 — Refactor v18 — unidad operativa por línea

**Propuesta arquitectónica registrada en BITACORA H011 (2/5/2026).** La
arquitectura actual mezcla dos sistemas de coordenadas (página + línea).
Los clusters `pagina_no_en_mapa` y `pagina_fin_no_en_mapa` (82 casos
pre-fix) son errores de la traducción página↔línea, no de detección de
contenido. Refactorizar a "línea como unidad primaria" eliminaría
categóricamente dos clusters de bugs.

**Decisión:** mantener arquitectura actual para esta tesis. Considerar
para v18 si el proyecto continúa post-tesis. **No es trabajo para
v17.x.**

### M04 — Convención: snapshots cubren todo archivo modificable

**Lección de la sesión 2026-05-02 (BITACORA H012).** El snapshot inicial
solo cubrió archivos de raíz, no de `paginas/`. Cuando se aplicó el fix
Bug D al script de `paginas/`, el original quedó sobrescrito sin backup
explícito.

**Convención adoptada:** antes de modificar archivo X, copiar X al
snapshot del día sin asumir que el snapshot inicial cubre todo.

### M05 — Verificación caso-a-caso de identidad de los 32 oks de XXI-v — CERRADO H062

**Cerrado H062 (auditoría).** Ya flagueado 15/5 para reconsiderar: la premisa
"probablemente son los mismos 32 casos" no se sostiene (direcciones opuestas),
y la identificación caso-a-caso es imposible sin git log de ese período. Cerrado
como no-resoluble. No tiene impacto operativo.

---

### M06 — Verificación de la gramática del epílogo sobre el corpus completo

**Origen:** H026 (corrida `--random 80` + síntesis de gramática del
epílogo).
**Pendiente:** la gramática del epílogo identificada en
`docs/GRAMATICA_DEL_FALLO.md` (sección "El epílogo: producción
faltante") está validada empíricamente sobre 80 casos. Antes de
implementar el detector de epílogo en el auditor (B047), verificar la
persistencia editorial sobre el corpus completo:

1. **Frecuencia de cada marcador por tomo.** Contar apariciones de los
   9 marcadores explícitos del epílogo en cada tomo (329-349).
   Identificar si hay marcadores nuevos en tomos no muestreados o
   marcadores que dejan de aparecer.
2. **Convivencia de convenciones editoriales.** "Nombre del
   actor/demandado:" vs "Recurso ... interpuesto por" vs "Parte
   actora:": ¿hay tomos donde una convención reemplaza a otra, o
   coexisten todas? Si hay drift, identificar el punto de transición.
3. **Casos sin epílogo.** ¿Cuántos casos del corpus efectivamente no
   tienen epílogo? Distinguir entre (a) casos cortos
   (`sumario_con_link`, casos de cuestiones de competencia con
   resolución de una línea) y (b) casos largos donde el epílogo
   debería estar y no está. Los segundos son candidatos a bug del
   parser.

**Método:** scripts diagnósticos en
`archivo/exploratorios/diagnostico/B047_epilogo/` (crear directorio
en H026 continuación). Salida: CSV con conteo por marcador por tomo,
más reporte cualitativo de hallazgos. **Ejecutar antes de implementar
el detector** para no descubrir variantes después del fix.

**Disciplina:** validar formato real de los CSVs con `csv.DictReader`
y nombres de columna; nunca con `Select-String` posicional. Esta es
la corrección de método del cierre honesto de H025.

### M07 — Reimplementación de heurísticas que la docstring del auditor prohíbe

**Origen:** H027 (lectura de código).
**Diagnóstico:** la docstring del módulo `auditar_fallo.py` (líneas
16-20) declara:

> CRÍTICO — relación con parser.py: Este script REUSA por importación
> los regex y helpers de parser.py. No reimplementa heurísticas. Si
> una heurística está rota en parser.py, acá va a estar igual de rota
> — y el catch-all lo va a delatar.

La lectura de Fase A continuación encuentra dos violaciones de esta
regla:

1. **`es_header_sumario_auditoria` (línea 607)** es una segunda
   implementación del detector de header de sumario. El comentario
   declara "más permisivo que `linea_es_header_sumario` del parser",
   y el parser importa `linea_es_header_sumario` pero el auditor no
   lo usa: implementa su propia versión.

2. **`detectar_dictamen` (línea 741)** "Replica la lógica del parser
   pero devuelve rango de líneas en vez de set de índices" (docstring
   de la función). Reusa `RE_DICT_HDR` por importación pero
   reimplementa el algoritmo de barrido del fin del dictamen.

**Consecuencia operativa:** si el parser cambia el algoritmo (no solo
los regex) de detección de sumarios o dictamen, el auditor diverge
silenciosamente. La auditoría deja de reflejar lo que el parser hace.

**Acción pendiente:** decidir política. Tres opciones, sin
recomendación previa:

1. Promover `es_header_sumario_auditoria` y la lógica de fin de
   dictamen a `parser.py` y reimportar desde el auditor.
2. Documentar explícitamente en las docstrings de ambas funciones del
   auditor que son **forks deliberados** (más permisivos en el caso
   del sumario, con ajuste de auditoría en el caso del dictamen) y
   relajar la declaración de la docstring del módulo.
3. Refactor: dividir las funciones del parser en (a) extracción de
   índices y (b) decisión de span, exportar ambas piezas, y que el
   auditor componga lo que necesite.

**Precondición:** ninguna. Trabajo independiente.

### M08 — `_ordenar_y_validar` no implementa la validación que su nombre y docstring prometen

**Origen:** H027 (lectura de código).
**Diagnóstico:** la función `_ordenar_y_validar` (línea 1176) tiene
docstring "Ordena por linea_ini y valida invariantes". El cuerpo de
la función solo ordena. No verifica las invariantes que
`segmentar_bloque` declara (líneas 974-979):

> INVARIANTES:
>   - Spans semánticos (TIPOS_SEMANTICOS) son disjuntos entre sí.
>   - header_pagina es transversal: puede caer adentro de cualquier
>     span semántico. Se emite como span propio, no se excluye de
>     los demás.
>   - Cobertura: toda línea del bloque pertenece a ≥1 span (catch_all
>     si nada más matchea).

Ninguna de las tres se verifica en runtime. Un span solapado con otro
del mismo tipo semántico, o una línea sin cobertura, o cualquier
violación pasaría silenciosamente. Si un detector futuro emite spans
inválidos por un bug propio, el auditor no avisa.

**Acción pendiente:** dos opciones:

1. **Implementar la validación.** Verificar disjunción de spans
   semánticos, cobertura total, y tipos válidos. Si una invariante
   falla, emitir alerta (en el modo `--stdout`) o agregar campo
   `alertas_invariantes` al resultado (en el modo API). Costo
   estimado: 20-30 líneas.
2. **Renombrar a `_ordenar`** y actualizar la docstring para reflejar
   lo que efectivamente hace. Costo: trivial.

La opción 1 es preferible si la salud del modelo de spans se considera
importante para validación cruzada con el parser; la opción 2 si se
asume que las invariantes están garantizadas estructuralmente por la
construcción de `segmentar_bloque` y no necesitan check en runtime.

**Precondición:** ninguna. Trabajo independiente.

---

### M09 — Detección sin constraint de zona (deuda arquitectónica) — APLICADO H064

**Componente:** parser (loop principal de votos).
**Origen / fuente del diagnóstico:** H063 (diagnóstico B010).
**Descripción:** el zonificador crea zonas (dictamen, mayoria, voto,
disidencia, editorial) pero el loop principal de detección de votos (L2256-2289)
solo excluía `lineas_dictamen`. Zonas como `residuo_caso_anterior`, `sumario`,
`epilogo` y `header_pagina` no se filtraban.
**Fix aplicado (H064):** nuevo set `lineas_excluir` derivado de `_zonas_linea`
(todo lo que no esté en `{apertura, cuerpo, dispositivo, firma, voto_separado}`).
Reemplaza `lineas_dictamen` en el skip del loop.
**Validación:** 0 regresiones sobre 5667 fallos (poc_m09.py). ~500K líneas
ahora protegidas (155K sumario, 137K header_pagina, 107K residuo, 100K epílogo).
**Impacto directo:** ninguno (los regex actuales no matcheaban en esas zonas).
**Impacto preventivo:** protege B010 y futuros regex más permisivos contra
FP en zonas no-fallo.
**Pendiente:** extender constraint a otros detectores (apertura, dispositivo,
considerando) cuando se justifique. `_encontrar_zona_fallo` no puede usar
zonas (corre antes del zonificador).

---

### M10 — Zonificador: distinguir zonas de mayoría vs votos individuales

**Componente:** parser (zonificar_bloque).
**Origen / fuente del diagnóstico:** H070 (diagnóstico B082).
**Descripción:** el zonificador asigna las mismas etiquetas de zona
(`cuerpo`, `dispositivo`, `firma`) tanto a la mayoría como a los votos
individuales. Solo `voto_separado` (post voto_header) es específico.
El visor ya distingue mayoría/disidencia/concurrencia, pero lo hace
por posición (antes/después de inicio_votos_indiv), no por zona.
**Impacto:** B082 requirió un fix posicional (excluir >= inicio_votos_indiv)
en vez de usar zonas, porque las zonas no capturan la frontera.
Otros consumidores del zonificador (wc_mayoria, lineas_mayoria) también
usan posición y no zonas.
**Propuesta:** prefixar zonas post-inicio_votos_indiv como `voto_cuerpo`,
`voto_dispositivo`, `voto_firma`. O agregar una segunda capa (zona +
scope mayoría/individual).
**Precondición:** validar que inicio_votos_indiv es confiable en todos
los casos. En 64 casos, inicio_votos_indiv cae antes del dispositivo
de la mayoría — requiere diagnóstico.
**Estado:** no diseñado.
**Referencias cruzadas:** H070. B082. M09.

---

## Mapeo histórico

Trazabilidad de IDs viejos del documento del 2026-05-02 a los IDs
canónicos actuales B0NN.

| ID histórico | ID actual | Estado |
|---|---|---|
| **Bug A** (`pagina_no_en_mapa`, 43 casos) | **B009** | En validación (cuantificado, sin fix) |
| **Bug B** (`fallo_cruza_archivos`, 20/27 casos) | **B002** | Cerrado 2026-05-09 (disuelto como efecto colateral de B001) |
| **Bug C** (`pagina_fin_no_en_mapa`, 39 casos) | **B003** | Cerrado 2026-05-09 (Fase 1 de §3.6.e). Fase 2 = B009 |
| **Bug D** (`ultimo_del_tomo`, 19 casos) | **B004** | Cerrado 2/5/2026 |
| **Bug 1** (Y.P.F. Tomo 349 truncamiento de índice) | (no entra) | Decisión XXI: editorial CSJN, no resoluble en código. Se espera publicación definitiva del Tomo 349. Anotado en CHANGELOG / nota de tesis |

**IDs históricos del forense XXI mapeados a B0NN:**

| Letra XXI | ID actual | Notas |
|---|---|---|
| XXI-a | B008 (cerrado) + B014 (residuo del fallback) | Fix 1 aplicado; el 33% que cae al fallback sigue como B014 |
| XXI-b | B002 (cerrado) | El "fix extendido" mencionado en XXI-b sigue como mitigación temporal en B038 |
| XXI-c | B013 | Bug XII, 234 casos |
| XXI-d | B009 | En validación |
| XXI-e | B001 (cerrado) | `pg_fin+1` |
| XXI-f | B025 | 414 falsos unánime, sospecha cardinal |
| XXI-g variante 1 | B005 (cerrado) | Doble espacio |
| XXI-g variante 2 | B015 | Pegado |
| XXI-g variante 3 | B016 | Partido en 2 líneas |
| XXI-h | B026 | V. mayúsculas tomos 329-330 |
| XXI-i | B027 | Autos y Vistos |
| XXI-j | B011 | `344_p344` |
| XXI-k | B006 (cerrado conceptual) + B028 (fix de higiene pendiente) | Aritmética `apertura_idx + len(bloque)` |
| XXI-l | B029 (cerrado H062) | `collect_firma_lines max_lines=40`, resuelto por B055 |
| XXI-m | B030 (cerrado H062, = B018) | Redundante con B018, búsqueda atrás eliminada B069 |
| XXI-n | B031 | `linea_es_header_sumario` mayúsculas |
| XXI-ñ | B032 (= F001) | `RE_VOTO_HDR` |
| XXI-o | B033 | `ultimo_del_tomo_sin_fin` |
| XXI-p | B034 | `RE_FECHA_LINEA` paréntesis/guiones |
| XXI-q | (descartado) | XXI mismo: no es bug, código muerto |
| XXI-r | (no entra) | Decisión "no fixear" sesión V |
| XXI-s | (no entra) | `jueces_desconocidos` vacío, intencional |
| XXI-t | B003 parcial | Hojas complementarias Fase 1 ✅, Fase 2 = B009 |
| XXI-u | (no entra) | Cubierto implícito por §2.5.e PIPELINE |
| XXI-v | M05 (cerrado H062) | No-resoluble, sin impacto operativo |

**IDs F-numerados de BITACORA mapeados a B0NN:**

| F-N | ID actual | Notas |
|---|---|---|
| F001 | B032 (= XXI-ñ) | `RE_VOTO_HDR` |
| F002 | B020 | `detectar_fin_real` extiende |
| F003 | B021 | `detectar_fin_real` corta corto |
| F004 | B022 | Arrastre del fallo previo |
| F005 | B023 | Fin del dictamen pisa FALLO |
| F006 | B024 | Sumarios editoriales |
| F007 | B040 | Spans del fallo previo (auditor) |
| F008 | B041 | Off-by-one auditor vs `.md` |
| F009 | (descartado) | Retractado en BITACORA línea 648 |
| F010 | B019 | Off-by-one firmas multilínea |
| F011 | B012 | Catálogo localización extendido |
| F012 | B017 | Firma partida → catch_all |
| F013 | B018 (= XXI-m) | Pista 1 falso positivo en dictamen |
| F-AUDITOR-01 | B042 | Colisión timestamp |
| F-AUDITOR-02 | (descartado) | Retractado en BITACORA línea 913 |

---

## Resumen ejecutivo

*Actualizado H080 (2026-05-28).*

**Estado de main (H080):** main revertido al baseline limpio pre-tomos 335/336
(`056c31e`): corpus ~5862, sin_firma 16, parser v18.05, detectar_paginas con
exclusión 335/336. Los tomos 335 y 336 quedan PARQUEADOS hasta conseguir los
tomos papel (B098/B099). La ruta de catálogo 336 (validada) queda como archivo
y en branch `tomos-335-336`, sin mergear. Los conteos del snapshot H079 cont.
abajo (corpus 6117, sin_firma 78) describen el estado parqueado, no main.

*Snapshot H079 cont. (referencia histórica, parqueado):*

- **Bugs cerrados:** ~39 (B001-B008, B013, B029, B030, B032, B039, B046,
  B055, B060, B063-B064, B066-B074, B076-B077, B079, A001,
  B077-nuevo, B078, B079-nuevo, B083, B084, B085, B087, B088).
  B086 fix parcial.
- **Bugs en validación:** 1 (B009 parcialmente resuelto por Fase F).
  B010 cerrado (H064).
- **Bugs activos del pipeline (catálogo + cruzador + parser):** ~30.
  Catálogo: B011, B045.
  Cruzador: B012.
  Parser: B014-B022, B023-B028, B031, B033-B038, B043-B044, B048,
  B053-B054, B082 (residual), B086 (residual), B089-B091, B098, B099.
  De ellos:
  - B098 (335 firma fragmentada): 62 sin_firma nuevos por OCR.
  - B099 (336 catálogo): construir_catalogo no detecta índice editorial.
  - B025 (falsos unánime): re-medido H068. 414→72 (14-20 falsos reales).
  - B018, B024: sustancialmente mitigados por fixes colaterales (H046-H055).
  - B028 (cosmético), B033 (cosmético), B036 (cosmético), B037 (cosmético).
  - ~5 hipotesis_no_verificada: B015, B026, B027, B031, B034.
  - B089 (residuo pre-carátula): 96% de bloques, prioridad pre-publicación.
  - B090 (Tier 5): diseñado, PoC pendiente.
  - B091 (classify_outcome revoca): 2 casos testigo.
- **Detectores (H079 cont., parser v18.05):**
  - outcome "otro": 712 (era 757, 4 minor outcomes: desierto 13,
    inadmisible 25, improcedente 21, caducidad 11).
  - deja_sin_efecto: 92. procedente: 780.
  - es_queja: 2055/5876 (35.0%). queja_resultado 98.2% cobertura.
  - tipo_cuestion_federal: 2949/5876 detectados (50.2%).
    cuestion_federal 1354, arbitrariedad 904, mixto 691, sin_dato 2927.
  - sin_dispositivo: 33. sin_firma: 78 (62 de tomo 335). ancla_catalogo: ~35.

**Próximo trabajo priorizado (orden sugerido, H080 — línea limpia, 335/336 parqueados):**

*335/336 quedan fuera de esta lista: parqueados pendiente tomos papel (B098/B099).*

*H084: hay red de regresión del parser (M12). Todo refactor del parser se gatea a que `scripts/tests/check_regresion.py` dé [CLEAN]. La refacción REE (frente A) es ahora trabajo seguro: candidatos M03 (unidad por línea), M07 (dedup parser↔auditor), M08, classify_outcome como gate+action (ítem 6), colapso de la cascada de tiers 1→4 en procesar_archivo (757 líneas).*

*H085: R1 aplicado — cascada extraída a `resolver_dispositivo()` (M13). procesar_archivo 757→543. Sucesor inmediato sugerido: colapso de los 5 tiers a barrido parametrizado (M13; ya NO es refactor puro). El manifiesto de trazabilidad de versión es M14, diferido a H086.*

*H086: R5 aplicado — cascada de dispositivo colapsada a `_barrer()` + 4 detectores `_cand_*` + 5 llamadas (M13; reescritura de lógica, no extracción pura). resolver_dispositivo 223→63; archivo 3650→3603; patrones a nivel de módulo. check_regresion [CLEAN], parser v18.07. M13 sigue EN PROGRESO (resta es_originaria + detector de sumarios). Candidatos inmediatos: M14 (manifiesto sidecar, diseñado), R2 (classify_outcome como gate+action, ojo con la lógica 280/ac4 duplicada), o frente D/B (cambio de comportamiento sobre código ya limpio).*

*H087: M14 implementado — manifiesto sidecar de procedencia del pipeline (`scripts/pipeline/generar_manifiesto.py` v1.0 → `output/parser/_manifest.json`). Tres capas: git commit+dirty (A, fija todo el código), versiones de los 5 scripts vía ast (B), sha256+filas+bytes de 3 intermedios + 5 outputs (C, DAG de datos). Standalone, no-hook (cubre el 5º CSV, re-corrible, no engrosa el parser); allow-list explícita; `--verify` como 2ª red de integridad. NO toca el parser → golden [CLEAN] por construcción, sin bump (parser sigue v18.07). M13 sigue EN PROGRESO (es_originaria + detector de sumarios). Candidatos inmediatos sin cambios: M13 cont. (habilita frente D), R2, frente D/B. Pendiente nuevo: digest del corpus crudo (LibroVol*.md).*

1. **Variable `materia` (inferida desde tribunal_origen).** Normalizar
   tribunal_origen (limpiar OCR, unificar variantes provinciales), mapear a
   materia por keywords. ~1454 sin_marcador. Habilita análisis temático.
2. **B090 — Tier 5 dispositivo embebido.** 33 sin_dispositivo con firma. PoC pendiente.
3. **Recalibrar `is_originaria` (art.117) / `inadmisible_280` (art.280) / art.4.**
   Regexes dependían de considerando_text con editorial pre-B010; recalibrar
   contra texto limpio. Toca variables centrales de las hipótesis.
4. **sin_firma residual (16 casos pre-335)** — auditar residuo.
5. **Análisis para hipótesis:** H2 red de citas, secretaría letrada, expansión H3, dashboard.
6. **Diseño taxonómico: outcome como par gate+action.**

*Pendientes del módulo `estadisticas/` (H083, frente analítico, fuera del pipeline):*
- **Correr el extractor de los 4 tableros completo.** `export_tableau_playwright.py` quedó
  armado para ingresos/resueltos × 2024/2025 pero solo se corrió resueltos 2025. Un comando.
- **Procesar el tab voto × materia** (`Hoja 66 (2)`, ya bajado en resueltos 2025): confirma
  por materia el hallazgo del 280 de Lorenzetti.
- **Etiquetar por secretaría las capturas del cruce voto×juez.** El capturador pasivo bajó
  16 capturas filtradas pero el `filtersJson` de la respuesta no expone qué secretaría estaba
  seleccionada (los `tuples` vienen con `s:false`); falta cruzar por totales o por orden de
  clic para asignar nombre a cada captura. Tarea acotada, no cerrada en H083.
- **Limitación estructural del motor de filtros por API:** lanzar `categorical-filter` desde
  Python da 410 (sesión consumida); solo funciona el clic real en la UI capturado pasivamente.
  El capturador pasivo (`capturador_pasivo.py`) fue el camino que funcionó; el motor automático
  (`motor_voto_x_secretaria.py`) quedó descartado. Ambos scripts se borraron en limpieza H083.

*Al desparquear 335/336: incorporar ruta 336 (construir_catalogo v1.01, validada)
+ re-escaneo de páginas de cierre del papel para firmas/fechas (worklist listo).*


### Referencia: taxonomía oficial CSJN (Anuario Estadístico 2025)

Fuente: Informe sobre Anuario Estadístico 2025, Oficina de Estadísticas,
CSJN. Analizado en H077 para alinear la taxonomía del parser con las
categorías institucionales. Las tablas cubren el período 2025; nuestro
corpus es 2006–2011 (tomos 329–349) pero la estructura clasificatoria
es estable.

**Sentido de la resolución (recursos admitidos, 3722 casos 2025):**
Revoca 51.61%, **Deja sin efecto 36.32%**, Confirma 9.73%, Revoca
parcialmente 1.02%, otros 1.32% (declara competencia, rechaza,
desestima, nulidad, declara inexistencia, declara inoficioso, declara
improcedente, modifica, rechaza la demanda). → "Deja sin efecto" es
categoría separada de "Revoca". **Implementado H079:** 87 casos
como outcome `deja_sin_efecto`.

**Causales de inadmisibilidad (20823 recursos inadmitidos 2025):**
Art. 280 CPCCN 60.25%, Acordada 4/2007 21.85%, falta sentencia
definitiva 5.73%, falta fundamentación 2.83%, depósito previo 2.24%,
cuestión abstracta 1.97%, desistimiento 1.85%, fuera de término 1.38%,
falta denegación REF, caducidad instancia, salto de instancia, falta
firma, otras. → Nuestro parser distingue 280 y ac4. Subdivisión
adicional de baja prioridad.

**Cuestiones federales (recursos admitidos, 3767 cuestiones 2025):**
Art. 14 ley 48: 67.29% (cuestión federal propiamente dicha — conflicto
norma local vs. Constitución/ley federal). Sentencia arbitraria: 32.71%
(doctrina pretoriana — sentencia sin fundamentos válidos, omisión prueba
decisiva, valoración absurda, exceso ritual, auto-contradicción).
74.92% de arbitrariedades se originan en la Cámara Nacional de
Apelaciones del Trabajo. → **Implementado H078:** `tipo_cuestion_federal`
(arbitrariedad / cuestion_federal / mixto). Detección primaria en sumario
editorial (headers Secretaría de Jurisprudencia), fallback a considerando_text.
2843/5669 (50.1%) detectados.

**Vía de acceso recursiva (56614 recursos ingresados 2025):**
Queja REF denegado 77.9%, REF concedido 21.61%, queja recurso
ordinario denegado 0.35%, salto de instancia 0.09%, recurso ordinario
0.06%. → **Implementado H078:** `es_queja` (bool) + `queja_resultado`
(12 categorías). 1993/5669 fallos (35.2%). Sinónimos: queja / recurso
de hecho / presentación directa.

**Materia (por secretaría de radicación, 26524 resueltos 2025):**
Previsional 54.06%, Penal 11.84%, Laboral 11.35%, Penal Especial
5.68%, Contencioso-Administrativo 4.68%, Civil y Comercial 4.46%,
Consumo 3.93%, Tributario/Aduanero/Bancario 3.34%, Juicios Originarios
0.33%, Juicios Ambientales 0.33%. → No tenemos secretaría. Inferible
desde `tribunal_origen` (Cám. Trabajo→laboral, CFSS→previsional, etc.)
tras normalización. También desde carátula: "ANSeS"→previsional,
"ART"→laboral.

**Tipos de votos (79928 votos emitidos 2025):**
Unanimidad 48.97%, voto conjunto 33.97%, voto propio 16.92%,
disidencia propia 0.11%, disidencia conjunta 0.03%, disidencia parcial
propia 0.001%. → Nuestro parser captura voting_pattern (unanime,
disidencia, segun_su_voto, mixed). "Voto conjunto" vs "voto propio"
requeriría análisis del texto de cada voto individual.

**Cruce voto × ministro 2025 (extraído del tablero en H083; conformación de ministros, sin conjueces):**
Total firmas por ministro ~26.380 (Rosatti, Lorenzetti, Rosenkrantz; García-Mansilla 208,
asunción tardía). Unanimidad casi idéntica entre los tres (~12.960). La bifurcación es el
dato: en el tramo no-unánime, Rosatti y Rosenkrantz votan en CONJUNTO (13.345 / 12.893),
Lorenzetti vota PROPIO (12.899, solo 513 conjunto). Reparto del voto propio total (13.486):
Lorenzetti 95.6%, Rosenkrantz 3.8%, Rosatti 0.5%, García-Mansilla 0.0%. → HALLAZGO: voto
propio de Lorenzetti (12.899) ≈ total art. 280 (12.546, de la tabla de causales). Las
capturas filtradas por secretaría muestran ese voto propio repartido transversalmente
(~10-11% en las secretarías grandes), no concentrado en previsional. Lectura: Lorenzetti
emite su versión individual de la desestimación 280 a lo largo de las materias, mientras
Rosatti y Rosenkrantz la suscriben en conjunto. Es diferencia de forma de suscripción sobre
un acto impersonal (280), no fragmentación doctrinaria. Para H1: la postura frente al
proyecto de secretaría es disposición estable del ministro, no asignación institucional.
Para H3: matiza a la baja la lectura de "proliferación de votos propios" (artefacto de cómo
un ministro suscribe el 280). CSV: `estadisticas/cruce_voto_x_ministro_2025.csv`.


### B052 — `detectar_caratula` del auditor: carátula partida entre catch_all y span carátula

**Componente:** auditor (cosmético — no afecta CSV).
**Origen:** sesión H030, inspección auditoría postfix_fase_f_v2, caso `346_p885`.
**Causa raíz (corregida en H031):** el refinador `refinar_inicio_por_titulo()`
ancló correctamente en la primera línea de la carátula de Wang. El problema
real es que `detectar_caratula()` del auditor toma solo la segunda mitad de
la carátula como carátula porque la primera quedó en el catch_all inicial
(zona de residuo del caso anterior). Cuando la carátula está partida en dos
o más líneas por salto de página, `prev_no_header` se pisa en cada iteración
y devuelve solo la línea más cercana al primer sumario.
**Diagnóstico / evidencia:** `346_p885` (Wang, Dingjian): catch_all inicial
contiene epílogo de Schenone + `WANG, DINGJIAN c/ EN - M INTERIOR OP y V – DNM`.
El auditor detecta como carátula solo `s/ Recurso directo DNM`. Mismo patrón
en `329_p9` (carátula en 3 líneas) y `329_p5` (carátula con `V.`).
**Severidad:** cosmético. El dato correcto ya está en `nombres_indice` por
definición del índice editorial. No afecta `case_name_indice` del CSV ni
ningún campo analítico.
**Fix propuesto:** usar el primer token de `nombres_indice` como límite
dentro del catch_all anterior para identificar el inicio real de la carátula.
Dependiente de B054 (separar catch_all anterior del posterior por posición).
POC disponible en `scripts/auditoria/poc_b052v3.py` — 1 mejora, 0 regresiones
sobre 11 casos testigo.
**Estado del fix:** poc_validado. Pendiente integración con B054.
**Referencias:** H030, H031, commit `27bf3d5`.

---

### B053 — Parser reimplementa lógica de segmentación del auditor

**Componente:** parser / auditor.
**Origen:** sesión H030, observación durante auditoría postfix.
**Causa raíz:** `segmentar_bloque()` del auditor (carátula, sumarios,
dictamen, cuerpo_mayoria, firma, votos, disidencias) fue construida
iterativamente con inspección humana y produce segmentación más
confiable que la lógica paralela del parser productivo. El parser
reimplementa las mismas heurísticas de forma más cruda, sin el
refinamiento acumulado del auditor.
**Diagnóstico / evidencia:** comparación visual en auditorías H030 —
el auditor detecta correctamente secciones que el parser procesa
como ruido (epílogo en catch_all, carátulas partidas, dictamenes
embebidos).
**Impacto:** todos los campos analíticos del CSV (`wc_mayoria`,
`wc_votos`, `wc_considerando`, `firma_raw`, `dictamen_presente`)
son menos confiables de lo que serían si el parser consumiera
`segmentar_bloque()`.
**Estado de verificación:** confirmado_caso_testigo.
**Fix propuesto:** refactorizar `procesar_archivo` para que llame a
`segmentar_bloque()` del auditor como fuente de segmentación, en lugar
de reimplementar. Requiere mover `segmentar_bloque()` a un módulo
compartido (`scripts/pipeline/segmentador.py`) e importarlo desde
ambos. Cambio arquitectónico — requiere planificación cuidadosa y
validación exhaustiva.
**Estado del fix:** no diseñado.
**Referencias:** H030.

---

### B054 — Epílogo post-firma no tipificado (catch_all)

**Componente:** parser / auditor.
**Origen:** sesión H030, observación durante auditoría postfix.
**Causa raíz:** el bloque post-firma de cada fallo contiene información
analíticamente valiosa (representación letrada de cada parte, tribunal
de origen, tribunales intervinientes) que hoy cae en `catch_all` porque
ni el parser ni el auditor lo tipifican como span propio.
**Diagnóstico / evidencia:** casos Buttice (329_p5368) y Andreani
(329_p1301) auditados en H030 — el catch_all final tiene estructura
consistente y delimitable.
**Señal de inicio:** primera línea post-firma que matchea
`Recurso .* interpuesto por` | `Traslado contestado por` |
`Nombre de la actora` | `Nombre del actor`.
**Señal de fin:** carátula del caso siguiente o fin de bloque.
**Impacto:** tribunal de origen hoy se extrae desde el cuerpo del fallo
(menos confiable); desde el epílogo sería más preciso. Representación
letrada no se extrae en absoluto — datos para análisis de litigantes
frecuentes.
**Estado de verificación:** confirmado_caso_testigo.
**Validador propuesto:** M06 (verificar persistencia editorial de la
gramática del epílogo sobre corpus completo) antes de implementar.
**Estado del fix:** no diseñado.
**Referencias:** H030, M06.

---

### VIS001 — Clasificación robusta de catch_all_inicio en auditar_fallo
**Componente:** auditor (`auditar_fallo.py`).
**Origen:** sesión H032.
**Causa raíz:** el primer `catch_all` de cada caso es residuo del caso
anterior (epílogo arrastrado, firma del fallo previo). Hoy se distingue
en el visor por posición (termina antes del primer span semántico), pero
esta heurística falla cuando hay una firma arrastrada al inicio del bloque
que el parser detecta como span semántico, o cuando `caratula_rel` es
None (casos sin carátula detectada).
**Solución de fondo:** implementar la clasificación en `auditar_fallo.py`
usando `caratula_rel` como referencia principal, con fallback al primer
span semántico, y emitir tipos explícitos `catch_all_inicio` /
`catch_all_fin` en lugar de `catch_all` genérico. Requiere análisis
cuidadoso de casos con dos fallos cortos en la misma página y casos
con firma arrastrada al inicio del bloque.
**Estado de verificación:** identificado, no verificado exhaustivamente.
**Estado del fix:** no diseñado. Workaround activo en visor (posicional).
**Referencias:** H031 (B054), H032.
---
### VIS002 — Tipificación de epílogo como span propio en auditar_fallo
**Componente:** auditor / parser.
**Origen:** sesión H032 (referenciado desde B054).
**Nota:** este ítem complementa B054. La clasificación `catch_all_fin`
como `epilogo` requiere primero resolver VIS001 (distinguir inicio/fin
de forma robusta). Una vez resuelto VIS001, el `catch_all_fin` con señal
`Recurso .* interpuesto por` puede tipificarse como `epilogo`.
**Estado del fix:** bloqueado por VIS001.
**Referencias:** B054, H032.
---
### VIS003 — Soporte de rango en --pagina de auditar_fallo
**Componente:** auditor (`auditar_fallo.py`), CLI.
**Origen:** sesión H032.
**Causa raíz:** `--pagina` solo acepta lista comma-separated. Para
auditar casos consecutivos hay que conocer las páginas válidas de
antemano. Un rango `344-354` debería resolver automáticamente qué
páginas de inicio existen en ese intervalo según el catálogo.
**Fix propuesto:** en `_parse_paginas()`, detectar tokens con `-`,
splitear en inicio/fin, filtrar contra `fallos_localizados.csv` las
páginas válidas en ese rango. Sin cambios de lógica de auditoría.
**Estado del fix:** no diseñado.
**Referencias:** H032.
---
### VIS004 — Headers de página embebidos en contenido de spans (visor)
**Componente:** visor (`visor_auditoria.py`).
**Origen:** sesión H032.
**Causa raíz:** el parser deja líneas de `header_pagina` dentro del
texto de los spans semánticos (sumarios, cuerpos, votos). El visor
los filtra con `_limpiar_headers_embebidos()` pero el filtro es
heurístico (número de página, "FALLOS DE LA CORTE SUPREMA",
"DE JUSTICIA DE LA NACIÓN"). Si aparecen variantes editoriales
no contempladas en el regex, pasan sin filtrar.
**Impacto en tesis:** leve inflación de `wc_considerando` y
`wc_votos`. No afecta firma ni carátula.
**Fix de fondo:** resolver en el parser, no en el visor.
**Estado del fix:** workaround activo en visor. Fix de fondo
bloqueado por M08 (refactorización arquitectónica).
**Referencias:** H032, M08.
---
### B055 — Firma multilinea truncada (nombre partido por salto de línea)
**Componente:** parser.
**Origen:** sesión H032, auditoría de muestra de 80 casos. Revisado H033, H034, H042.
**Causa raíz:** `collect_firma_lines` tenía dos problemas: (1) `max_lines=40`
se agotaba antes de llegar a la firma cuando el dispositivo era largo;
(2) no tenía guarda de continuación post-started, recolectando texto
editorial post-firma (secretarios, carátulas, abogados) como parte de
la firma. Resultado: Tipo 1 (firma contaminada, 189 casos) y Tipo 2
(firma truncada mid-nombre, 48 casos), total 237 en CSV post-H041.
**Fix aplicado (H042, commit `e258f66`):**
- Eliminar `max_lines=40`, usar `len(bloque)` como techo.
- Guarda de continuación: `_RE_FIRMA_COMPLETA` (regex de apellidos
  conocidos + calificador opcional + punto) sobre texto acumulado.
  Cuando el texto acumulado termina en apellido conocido + punto,
  la firma podría estar completa → guarda estricta (`es_continuacion_firma`).
  Si no termina en apellido conocido (mid-nombre, abreviatura tipo "M."),
  seguir recolectando con solo breaks estructurales.
- Tolerancia a 1 línea vacía intercalada con lookahead.
**Resultado:** 1262 mejoras (1087 firma limpia, 159 firma con punto, 16
más jueces), 0 regresiones reales (31 falsas: prod inflado por abogados
con apellido de juez, headers de disidencia comidos, carátulas). Desconocidos:
"Ricardo Luis" 196→7, "Juan Carlos" 64→0, "CARMEN M." 52→6.
**Estado del fix:** **cerrado** (commiteado H042).
**Residuos conocidos:** 7+4 "Ricardo Luis"/"RICARDO LUIS" y 6 "CARMEN M."
aún truncados (línea anterior no termina en apellido reconocido por
`_RE_FIRMA_COMPLETA`). 45 "Estado Nacional" y 21 "Fisco Nacional" como
desconocidos indican firma_raw con texto post-firma residual.
**Referencias:** H032, H033, H034, H042, B013.
---
### B056 — Apertura de mayoría no detectada cuando hay residuo antes de "FALLO DE LA CORTE SUPREMA"
**Componente:** parser / auditor.
**Origen:** sesión H032, análisis de `344_p1695`.
**Causa raíz:** cuando el bloque comienza con residuo del caso
anterior (catch_all_inicio), `detectar_apertura_mayoria` no
encuentra "FALLO DE LA CORTE SUPREMA" / "Vistos los autos" en la
posición esperada porque el rango de búsqueda queda contaminado
por los spans previos o porque el residuo desplaza la posición
relativa del indicador.
**Diagnóstico / evidencia:** `344_p1695` (Corvalán c/ Intercórdoba):
el parser CSV tiene firma correcta (5 jueces, disidencia), pero el
auditor no detecta cuerpo_mayoria ni firma. El bug es del auditor,
no afecta el CSV productivo en este caso.
**Impacto en auditor:** cuerpo_mayoria y firma caen en catch_all,
dificultando la inspección visual. No confirmado impacto en CSV.
**Estado de verificación:** confirmado_caso_testigo (auditor).
**Estado del fix:** no diseñado. Requiere análisis de
`detectar_apertura_mayoria()` en auditar_fallo.py.
**Referencias:** H032, B057.
---
### B057 — Dictamen consume "FALLO DE LA CORTE SUPREMA" y cuerpo de mayoría cae en catch_all
**Componente:** parser / auditor.
**Origen:** sesión H032, análisis de `333_p1257`.
**Causa raíz:** cuando el dictamen es largo y termina con la firma
de la Procuradora justo antes de "FALLO DE LA CORTE SUPREMA",
el span del dictamen incluye esa línea. `detectar_apertura_mayoria`
busca después del dictamen y no encuentra nada — el cuerpo ya fue
consumido. Resultado: cuerpo_mayoria cae en catch_all como dos
spans separados ("Vistos los autos" y "Considerando").
**Diagnóstico / evidencia:** `333_p1257` (El Trébol S.A.): dictamen
(18880–19064, 185 líneas) incluye "FALLO DE LA CORTE SUPREMA" y
"Buenos Aires, 3 de agosto de 2010". Catch_all tiene "Vistos los
autos" (19065–19069) y "Considerando" (19073–19083).
**Impacto:** wc_mayoria=0, cuerpo del fallo no extraído, datos de
votación potencialmente incorrectos.
**Estado de verificación:** confirmado_caso_testigo.
**Fix propuesto:** en `detectar_dictamen()`, establecer como límite
fin del dictamen la línea inmediatamente anterior a "FALLO DE LA
CORTE SUPREMA" cuando este patrón aparece dentro del bloque del
dictamen. Requiere validación con M06 antes de implementar.
**Estado del fix:** no diseñado.
**Referencias:** H032, B056.
---
### B058 — Pérdida de símbolo de grado (°) en numeración de considerandos
**Componente:** visor / parser (encoding).
**Origen:** sesión H032, caso testigo `329_p3546`.
**Causa raíz:** el símbolo `°` en numeración ordinal (`1°`, `2°`)
parece perderse en algún punto del pipeline, dejando solo el número.
El filtro `_limpiar_headers_embebidos()` del visor tiene un regex
`\d{1,4}` que podría estar eliminando líneas que son solo un número
si el `°` ya se perdió antes. Requiere verificación contra el MD
original y el PDF para determinar si el problema está en el corpus,
el parser o el visor.
**Diagnóstico / evidencia:** caso `329_p3546`, considerandos
aparecen como `1` en lugar de `1°` en la vista del visor.
**Impacto:** leve — cosmético en el visor, posible inflación mínima
de wc si líneas de numeración se pierden.
**Estado de verificación:** identificado, pendiente comparación
MD original vs PDF.
**Estado del fix:** no diseñado. Primera acción: ajustar regex de
`_limpiar_headers_embebidos` de `\d{1,4}` a `\d{3,4}` para no
eliminar números de 1-2 dígitos que podrían ser numeración de
considerandos.
**Referencias:** H032.
---
### B061 — RE_DISID_HDR / RE_VOTO_HDR no matchean headers multi-línea
**Componente:** parser.
**Origen:** sesión H042, auditoría de regresiones B055.
**Causa raíz:** `RE_DISID_HDR` requiere `^Disidencia\s+...Señor` en la
misma línea. En el MD los headers están frecuentemente partidos:
```
DISIDENCIA PARCIAL DEL
SEÑOR MINISTRO DOCTOR DON CARLOS S. FAYT
```
"DISIDENCIA PARCIAL DEL" solo no matchea → el break en `collect_firma_lines`
no se activa. Idem para `RE_VOTO_HDR` con "Voto del Señor\nMinistro...".
**Impacto:** bajo post-B055 (la guarda de texto acumulado cubre estos
casos como segunda línea de defensa). Sin la guarda, el parser comería
el header y el texto de la disidencia/voto como parte de firma_raw.
**Fix propuesto:** comparar heurísticas con el auditor (`auditar_fallo.py`).
Posible: matchear solo "^Disidencia" o "^Voto del?" sin exigir "Señor"
en la misma línea.
**Estado de verificación:** confirmado_en_auditoria (múltiples casos en H042).
**Estado del fix:** no diseñado.
**Referencias:** H042.
---
### B062 — Nombre de juez en texto de dispositivo activa started=True
**Componente:** parser (`collect_firma_lines`).
**Origen:** sesión H042, caso testigo `347_p520`.
**Causa raíz:** `collect_firma_lines` busca el primer match de
`JUECES_CONOCIDOS` después de `por_ello_idx` para activar `started=True`.
Cuando el texto del dispositivo menciona a un juez por nombre completo
(ej: "Aceptar la excusación formulada por el señor Presidente de la
Corte Suprema de Justicia de la Nación, Doctor Don Horacio Rosatti"),
`started` se activa prematuramente. La guarda corta en la siguiente
línea que no parece firma → firma_raw = "Horacio Rosatti." con nj=1.
La firma real (líneas 20543-20544, 3 jueces) nunca se alcanza.
**Impacto:** bajo (1 caso confirmado: `347_p520`, nj 4→1).
**Fix propuesto:** en `collect_firma_lines`, no activar `started` si la
línea está en medio de una oración (verificar que la línea sea corta,
tenga dash, o esté precedida por línea vacía o fin de dispositivo).
**Estado de verificación:** confirmado_caso_testigo.
**Estado del fix:** no diseñado.
**Referencias:** H042.
---
### B063 — Conjueces faltantes en JUECES_CONOCIDOS ✓ CERRADO
**Componente:** parser.
**Origen:** sesión H042, análisis de desconocidos post-fix B055.
**Causa raíz:** `JUECES_CONOCIDOS` no incluía conjueces frecuentes.
**Fix aplicado (H043, commit `8a2558e`):**
- 10 conjueces agregados: Najurieta (8), Alcalá (9), Morán (7),
  Tyden de Skanata (5), Poclava Lafuente (3), Pereyra González (5,
  corregido PEREIRA→PEREYRA), Ferro (5), Pacilio (6), Argañaraz (4),
  Mill de Pereyra (2, nueva).
  Moliné O'Connor excluido: destituido 12/2003, no puede ser conjuez.
- Apellidos sincronizados en `_RE_FIRMA_COMPLETA`.
- Fix cosmético línea 550: `j["nombre"].split(" (")[0].lower()` para
  que el filtro de desconocidos no deje pasar nombres con sufijo "(conjuez)".
**Resultado:** 40 mejoras n_jueces (↑40, ↓0), +55 votos, sin_firma 425→422.
**Estado del fix:** aplicado y validado (PoC v2 con comparación campo a campo).
---
### B064 — LUIS CÉSAR OTERO no matchea pese a estar en JUECES_CONOCIDOS ✓ CERRADO
**Componente:** parser.
**Origen:** sesión H042, análisis de desconocidos.
**Diagnóstico (H043):** no era problema de encoding. Era el bug cosmético
en línea 550 de `parse_firma`: el filtro de desconocidos comparaba
`"otero (conjuez)" in "luis césar otero"` → False. Otero sí matcheaba
en JUECES_CONOCIDOS (10 casos reconocidos).
**Fix:** resuelto como parte de B063 (fix cosmético línea 550).
**Estado del fix:** cerrado (commit `8a2558e`).
---
### B065 — Validación cruzada firma↔votos (calificador sin bloque)
**Componente:** parser (validación).
**Origen:** sesión H042, observación durante auditoría.
**Causa raíz:** cuando `firma_raw` contiene "(en disidencia)" o
"(según su voto)", debería existir un bloque correspondiente
"DISIDENCIA DE..." o "Voto del..." en el caso. Si no existe, la
firma puede haber sido capturada del lugar equivocado (ej: firma
de disidencia tomada como firma de mayoría).
**Impacto:** no cuantificado. Señal de diagnóstico, no bug funcional.
**Fix propuesto:** agregar validación post-parseo que cruce calificadores
en firma con votos detectados. Loguear warnings.
**Estado del fix:** no diseñado.
**Validación parcial H054:** cruce de `n_jueces` (csjn_casos.csv) vs
`count(*)` por caso (csjn_casos_votos.csv): 0 discrepancias sobre
5668 fallos. La dimensión n_jueces↔n_votos está validada. La dimensión
calificador↔bloque_voto sigue pendiente.
**Referencias:** H042, H054.

(ya incluido en la primera parte de H032 — no agregar nueva entrada)

---
### B066 — RE_VOTO_HDR/RE_DISID_HDR: "juez/jueza" requiere filtro posicional — INVALIDADO
**Componente:** parser.
**Origen:** sesión H043, Fase 2 inventario de headers.
**Diagnóstico original (H043):** inventario del corpus mostraba ~85 headers de
voto/disidencia con "juez/jueza" en vez de "Señor Ministro". Agregar
`Juez(?:as?|es)?` al grupo de títulos causaba regresiones (sin_firma +19).
Se estimó que un filtro posicional (post-firma) resolvería el problema.
**Invalidado (H044):** PoC empírico con regex ampliado restringido a zona
post-firma encontró 42 matches, de los cuales **42/42 son citas
jurisprudenciales** (texto corrido que cita votos de otros fallos), no
headers de sección. Diagnóstico de contexto ±5 líneas confirmó que ninguno
es un header real: todos son mid-sentence wraps de OCR tipo
"(Fallos: 328:3312, voto del juez Fayt)." o "voto del juez Lorenzetti,
considerando 6°).".
Los ~85 "headers reales" del inventario H043 eran en su mayoría citas.
**Impacto real:** ~0 headers recuperables con filtro posicional.
**Estado:** INVALIDADO. No requiere fix. B066 no existe como fue estimado.
**Lección:** validar matches contra contexto real antes de estimar impacto.
**Referencias:** H043 Fase 2, H044 PoC A + diagnóstico de contexto.

---
### B067 — Tier 3: dispositivo retry sin techo ✓ CERRADO
**Componente:** parser (`procesar_archivo`, búsqueda de dispositivo).
**Origen:** sesión H044, análisis arquitectónico de segmentación por zonas.
**Causa raíz:** cuando `inicio_votos_indiv` cae antes del dispositivo real
(por votos-antes-de-dispositivo o residuo de fallo anterior no recortado),
el techo trunca el rango de búsqueda del dispositivo. Tier 1 y Tier 2
buscan en rango vacío o insuficiente, y el caso queda como sin_dispositivo
aunque el "Por ello" existe más adelante en el bloque.
**Diagnóstico (H044):** 22 casos con votos detectados + sin_dispositivo.
17 de ellos tienen dispositivo presente pero bloqueado por el techo
(TECHO_CORTA). Dos patrones: (a) bloque corto que es un voto individual
completo (first_voto=1, apertura=None); (b) fallo largo con votos
separados antes del dispositivo colectivo.
**Fix aplicado (H044):** Tier 3 — si Tier 1+2 con techo no encuentran
NADA (por_ello_idx queda None), repetir Tier 1 sin techo sobre todo el
bloque. Solo se activa para casos que producirían sin_dispositivo.
Incluye fallback (primer candidato sin firma validada) como Tier 1.
**Resultado:** 17 mejoras (16 recuperan firma, 1 queda sin_firma).
sin_firma: 422 → 406 (-16). 0 regresiones (validado full corpus, 5702).
2 casos bonus no anticipados (347_p2160, 348_p728).
**Estado del fix:** aplicado y validado (PoC B067 full corpus).
**Referencias:** H044.

---
### B068 — Moliné O'Connor en JUECES_CONOCIDOS — CANCELADO

**Componente:** parser (JUECES_CONOCIDOS).
**Origen:** H045, visor explorador.
**Síntoma:** Eduardo Moliné O'Connor desaparece de `jueces` y
`jueces_desconocidos` en 3 casos donde aparece en `firma_raw`
(329_p3568, 329_p4178, 330_p224). `parse_firma()` pierde el nombre
por el apóstrofe en O'Connor que rompe el tokenizador de desconocidos.
**Cancelado:** Moliné O'Connor es PARTE (demandante) en 2 juicios
post-remoción (340_p1993 "c/ EN - M° Desarrollo Social",
347_p1673 "c/ Estado Nacional"). Agregarlo a JUECES_CONOCIDOS
haría que `linea_es_firma_de_juez()` matchee líneas de carátula
(la carátula contiene " - " que pasa la guarda `tiene_raya`).
Impacto: ±1 juez en 3 casos vs. 2 falsos positivos. No justifica.
**Detectado por:** visor explorador, búsqueda libre "Moliné".
**Estado:** CANCELADO.
**Referencias:** H045.

---
### B069 — detectar_fin_real Pista 1 trunca por tokens comunes

**Componente:** parser (`detectar_fin_real`, Pista 1).
**Origen:** H045, diagnóstico de sin_firma vía visor explorador + PoC.
**Casos testigo:** 346_p1180 (token "Fisco", cortó 411 líneas),
346_p1257 (token "Fundación", cortó 399 líneas), 346_p1419 (token
"Banco", cortó 92 líneas).
**Síntoma:** `status_fin=fin_dentro_bloque` + `pista_fin=caratula_
siguiente`. Bloques largos truncados centenares de líneas antes de
firma y dispositivo.
**Causa raíz:** Pista 1 busca `primer_token_siguiente` (primer token
de ≥5 chars de la carátula del caso siguiente) **hacia atrás** desde
`linea_fin_catalogo`. Palabras comunes en derecho ("Fisco", "Banco",
"Fundación", "Estado", "Provincia") matchean en citas, cuerpo
argumentativo y dictámenes → corte falso.
**Impacto cuantificado (PoC v2 H045):** 201 de 422 sin_firma (47.6%)
tienen motivo `sin_firma_post_fallo` — la firma no está en el bloque
porque Pista 1 lo truncó antes. **Causa raíz principal de sin_firma.**
**Fix propuesto:** Reforzar Pista 1. Opciones:
  (a) Exigir más de un token coincidente.
  (b) Largo mínimo mayor para el token.
  (c) Validar que el match esté en zona de sumario (headers ALL CAPS
      cortos, no texto corriente).
  (d) Combinar con firma como contra-señal: si hay firma detectada
      DESPUÉS del punto de corte candidato, el corte es falso.
**Prioridad:** ALTA — mayor impacto potencial que cualquier otro fix.
**Estado:** **CERRADO H046.** Eliminada búsqueda atrás de Pista 1 en
`detectar_fin_real()`. 277 mejoras, 4 regresiones aceptadas (330_p747,
330_p4071, 331_p548, 348_p1519). sin_firma 406→148. Cobertura firma
92.9%→97.4%. Votos 25603→26959.
**Referencias:** H045, H046. PoC: `scripts/auditoria/B069/poc_b069_v3.py`.

---
### A001 — Firma depende de dispositivo (hallazgo arquitectónico)

**Componente:** parser (`procesar_archivo`, flujo principal).
**Origen:** H045, análisis del flujo + PoC firma independiente.
**Síntoma:** Si `por_ello_idx is None`, `collect_firma_lines()` nunca
se ejecuta → `firma_raw = ""` → `sin_firma`, aunque la firma exista
en el bloque.
**Causa raíz:** Flujo lineal `apertura → considerando → dispositivo
→ firma` sin fallback inverso. Falla en un eslabón → cascada.
Dependencia circular: el parser YA usa `linea_es_firma_de_juez()`
como validación de candidatos de dispositivo (línea ~1776), pero
después solo busca firma a partir de `por_ello_idx`.
**Impacto cuantificado (PoC v2 H045):** 43 de 422 sin_firma (10.2%)
son recuperables buscando firma inversamente con guardas
(post-zona-fallo, span≥20, excluyendo sumarios).
**PoC:** `scripts/auditoria/poc_firma_independiente_v2.py`.
42 unánime + 1 según_su_voto. Tasa cero de falsos positivos con
guardas v2 (zona de fallo obligatoria + span mínimo).
**Fix aplicado (H047):** Fallback post-dispositivo en `procesar_archivo`:
si `firma_parsed["voting_pattern"] == "sin_firma"`, ejecuta
`buscar_firma_inversa()` desde fin de bloque hacia atrás. Guardas:
zona de fallo obligatoria (primera apertura/fecha/considerando),
span mínimo 20 líneas, filtro zona post-firma, retroceso máximo 80.
A001b: `_encontrar_zona_fallo` cambiada de ÚLTIMA a PRIMERA apertura
para evitar envenenamiento por marcadores del caso siguiente.
**Estado:** **CERRADO H047.** 34+1 mejoras, 0 regresiones.
sin_firma 148→114→113. Votos 26959→27103.
331_p548 (regresión B069) recuperada por A001.
**Referencias:** H045, H047. PoC: `scripts/auditoria/A001/poc_a001_v1.py`.

---
### B070 — Pista 1 forward matchea en texto corriente del caso actual

**Componente:** parser (`detectar_fin_real`, Pista 1 forward).
**Origen:** H048, inspección de 57 sin_firma_post_fallo.
**Casos testigo:** 329_p551 (token "Nación" matchea en dispositivo),
329_p1554 (token "Nación" matchea en "Código Procesal Civil y Comercial
de la Nación."), 329_p2829 (token "ANSeS" matchea en "ANSeS dedujo
recurso ordinario de apelación").
**Síntoma:** `status_fin=fin_extendido_pag_compartida` +
`pista_fin=caratula_siguiente`. Bloque truncado antes de la firma
porque Pista 1 forward encuentra el token del caso siguiente en el
texto corriente del caso actual.
**Causa raíz:** Pista 1 forward busca `primer_token_siguiente` desde
`lfc+1` hacia adelante. Tokens comunes en derecho ("Nación", "Provincia",
"Estado", "ANSeS", "Banco") matchean en dispositivos, considerandos y
citas de jurisprudencia del caso actual → corte antes de la firma.
Variante forward del mismo problema que B069 (que era backward).
**Impacto cuantificado:** 43 de 57 sin_firma_post_fallo (75.4%) tienen
la firma dentro de 20 líneas post-corte.
**Fix aplicado (H048):** `_es_texto_corriente()` valida que el match
de Pista 1 forward NO sea texto corriente. Condiciones (OR):
  (a) Línea empieza con minúscula (excepto "c/" y "s/").
  (b) Línea anterior significativa termina con word-split genuino
      (letra + guión, no puntuación + guión).
Si es texto corriente, skip y seguir buscando el próximo match.
6 versiones de PoC (v1 contra-señal firma → v6 texto corriente + tildes).
**Estado:** **CERRADO H048.** 37 mejoras, 0 regresiones.
sin_firma 113→76. Votos 27103→27303.
**Referencias:** H048. PoC: `scripts/auditoria/H048/poc_b070_v6.py`.

---
### B071 — Pista 1 no matchea carátulas ALL CAPS sin tildes

**Componente:** parser (`detectar_fin_real`, Pista 1).
**Origen:** H048, investigación de regresiones de B070 v4/v5.
**Causa raíz:** `primer_token_siguiente` proviene del catálogo con
tildes modernas ("Administración", "Martínez", "González") pero las
carátulas en el .md son ALL CAPS sin tildes ("ADMINISTRACION",
"MARTINEZ", "GONZALEZ"). El regex con `re.I` es case-insensitive
pero NO tilde-insensitive → no matchea.
**Impacto:** 19.4% de los tokens (1126/5819) tienen tilde. Antes de
B070 funcionaban por accidente (el token matcheaba en texto corriente
donde sí hay tildes). Con B070 los matches falsos se rechazan y la
carátula real nunca matchea.
**Fix aplicado (H048):** `_strip_accents()` normaliza tildes (á→a,
é→e, etc.) en el token y en cada línea antes del regex.
**Estado:** **CERRADO H048** (incluido en fix B070).
**Referencias:** H048. Integrado en `poc_b070_v6.py`.

---
### B072 — Conjueces faltantes en JUECES_CONOCIDOS

**Componente:** parser (JUECES_CONOCIDOS).
**Origen:** H048, inspección de sin_firma_post_fallo y auditoría v6.
**Fix aplicado (H049):** 15 conjueces agregados a JUECES_CONOCIDOS y
`_RE_FIRMA_COMPLETA`:
  - García Lema, Rabbi-Baldi Cabanillas, Méndez, Montesi, Cossio,
    Pérez Petit, Romano, Petra Fernández (del listado original H048).
  - Chausovsky, Schiffrin, Aguilar, Pérez Tognola, Corcuera,
    Andalaf Casiello, Fernández Gómez (descubiertos en H049).
  - 5 del listado original no aparecen en firma_raw del corpus:
    Bertuzzi, Botana, Rivera, Torres, Caballero (no agregados).
**Resultado:** 21 mejoras, 1 regresión aceptada (346_p610 — firma del
caso anterior capturada por superposición de bloques, caso ya deficiente
en baseline). sin_firma 76→74. Votos 27303→27325.
**Validación:** PoC `poc_b072_diff.py` contra corpus completo.
**Estado:** **CERRADO H049** (commit `bfad045`).

---
### B073 — Interacción detectar_fin_real ↔ refinar_inicio_por_titulo

**Componente:** parser (flujo procesar_archivo).
**Origen:** H048, auditoría de mejoras B070 v6.
**Investigación H049:** análisis de los 451 lfr_cambio de B070 v6.
  - 0 casos con lfr_new < linea_inicio.
  - 0 casos que perdieron firma o cambiaron voting_pattern.
  - 398 acortaron lfr (corrección B070), 53 extendieron.
  - Mediana delta: -2 líneas, media: -5.5.
  - Los 18 casos con span < 10 son bloques cortos legítimos.
  La inconsistencia lfr < li_refinado es interna al parser (el
  linea_inicio refinado no se exporta al CSV). No afecta el output.
**Estado:** **CERRADO H049** sin fix (verificado, sin problemas).

---
### B074 — Guarda posicional en búsqueda de firma (superposición de bloques)

**Componente:** parser (`detectar_fin_real`, fallback firma_actual).
**Origen:** H049, análisis de regresión 346_p610 de B072 y clasificación
de los 74 sin_firma.
**Problema:** cuando el bloque catálogo incluye residuo del caso anterior
(firma, tribunal de origen), `linea_es_firma_de_juez` detecta esa firma
como `firma_actual` del caso corriente, cortando el bloque prematuramente.
**Fix aplicado (H050, commit `47f2059`):** pre-computar la posición del
token del título (`primer_token_de_caratula`) en las primeras 15 líneas
del bloque. Pasar esa posición como `li` a `detectar_fin_real`, de modo
que `buscar_atras` no alcance la firma del caso anterior.
Si el título no se encuentra en 15 líneas → li original → baseline idéntico.
**Iteraciones H050:** 5 versiones de PoC (v1-v5).
  - v1/v2 H049 (RE_APERTURA guard): bug de implementación desactivaba
    buscar_atras siempre. 13 mejoras, 7 regresiones (causa: bug de flujo).
  - v3 (RE_APERTURA guard, rango limitado li+40): 10 mejoras, 6 regresiones
    (causa: apertura del caso siguiente dentro del bloque grande).
  - v4 (reordenar refinar_inicio antes de detectar_fin_real): 13 mejoras,
    15 regresiones (causa: false matches del título en sumarios/citas).
  - v5 (pre-cómputo título 15 líneas como lower-bound): 5 mejoras,
    2 "regresiones" (ambas correcciones), 0 regresiones reales. Aplicado.
**Resultado:** sf 74→69, votos 27325→27335. 5 mejoras + 2 correcciones
(343_p1388: firma del caso anterior 5→3 jueces correctos; 347_p1378:
sumario_con_link correctamente reclasificado). 3 MEJORA_JUECES.
**Estado:** **CERRADO H050** (commit `47f2059`).

---
### B075 — Hornos "Roberto Enrique" (conjuez no reconocido)

**Componente:** parser (JUECES_CONOCIDOS, _RE_FIRMA_COMPLETA).
**Origen:** H049 hallazgo lateral, documentado H050.
**Problema:** "Roberto Enrique Hornos" en 347_p1673 no matchea el regex
existente (`gustavo\s+m\.?\s*hornos`). Es un conjuez distinto de
Gustavo M. Hornos. Agravado por guión pegado en OCR: `(según su voto)—`
sin espacio fusiona el chunk con Rabbi-Baldi en parse_firma.
**Impacto:** 1 caso, n_jueces 4→5.
**Fix propuesto:** agregar regex `roberto\s+enrique\s+hornos` a
JUECES_CONOCIDOS y `roberto` a _RE_FIRMA_COMPLETA.
**Estado:** Abierto. Prioridad baja.

---

### B076 — Firma espuria en sumarios: Pasada 1 no sectoriza heurísticas

**Componente:** parser.py / `zonificar_bloque()`.
**Origen:** H056, inspección visual de `329_p94` en explorador v4.1.
**Causa raíz:** Pasada 1 detecta anclas (`firma_linea`,
`epilogo_marker`, `sumario_header`) de forma global sobre todo el
bloque. Las heurísticas de firma (`linea_es_firma_de_juez`) matchean
dentro de sumarios editoriales: líneas como
`(Voto del Dr. Juan Carlos Maqueda).` o `Carlos S. Fayt.` al cierre
de un párrafo de sumario disparan `firma_linea`. Esto fragmenta la
zona sumario en decenas de segmentos intercalados con firma espuria.
**Diagnóstico / evidencia:** `329_p94` tiene 17 segmentos de sumario
y 12 segmentos de firma en la zona pre-apertura. Las firmas son
líneas de atribución de votos dentro de los sumarios, no firmas
reales del fallo. Probablemente afecta a cientos de casos (todo fallo
con sumarios de votos disidentes o según-su-voto).
**Impacto:** fragmentación de la zona sumario, inflado del conteo
de segmentos firma, potencial distorsión de métricas basadas en firma.
No afecta `sin_firma` ni `word_count` porque las firmas espurias
están en zona pre-apertura. Contamina el análisis de zonas.
**Fix propuesto:** sectorizar Pasada 1. Primero detectar límites de
sumario (anclas `sumario_header` son confiables: ALL CAPS con `:` o
`.`). Después correr `firma_linea` y `epilogo_marker` SOLO fuera de
regiones de sumario detectadas. Alternativa: post-pass que re-absorba
firmas dentro de sumarios.
**Severidad:** media-alta. Afecta calidad de zonificación de muchos
casos pero no rompe métricas analíticas principales.
**Estado:** **CERRADO H057.** Flag `_en_sumario` en Pasada 1. -256887 wc firma, +226902 wc sumario. 520 casos, 142615 segmentos (-5166). sin_firma 35→34.
**Referencias:** H056.

---

## B077 — Fronteras de caso absorben acordadas/discursos/índice

**Severidad:** media. **Detectado:** H057. **Cerrado:** H058+H059.

Casos ubicados al final de la sección de fallos de un tomo absorbían
las secciones posteriores (acordadas de la Corte, discursos, índice
alfabético por materias, índice por nombres de partes).
`detectar_fin_real` no cortaba antes de estas secciones editoriales.

**Fix aplicado (H058):**
- Nueva Pista `editorial_siguiente` en `detectar_fin_real`: busca
  marcadores editoriales (regex `RE_EDITORIAL_ANY`) desde
  `linea_inicio` hacia adelante. Si encuentra uno, corta en `k - 1`.
- `RE_EDITORIAL_ANY` excluye `ACORDADAS\s*$` standalone (FP en
  sumarios temáticos, caso testigo 339_p933). Solo matchea formas
  no ambiguas: `A C O R D A D A S` (espaciado),
  `ACORDADAS Y RESOLUCIONES`, `INDICE POR LOS NOMBRES`,
  `INDICE GENERAL`, `INDICE ALFABETICO POR MATERIAS`, etc.
- Nuevo output canónico: `csjn_casos_editorial.csv`. Función
  `extraer_secciones_editoriales()`, independiente del parser.
- Zonas editoriales en `zonificar_bloque` (Bloque 3) revertidas
  por regresión (ver B078).

**Fix adicional (H059):**
- Clasificación `acordada` eliminada en `_tipo_zona_editorial()`:
  los 67 hits eran todos FP — subsecciones del índice que listaban
  acordadas bajo headers "ACORDADAS", "A C O R D A D A S". Ahora
  `RE_EDITORIAL_ACORDADA.match()` devuelve `"indice"`. Las secciones
  se fusionan con los índices adyacentes.
- Editorial: 182→53 secciones (49 indice, 4 discurso, 0 acordada).

**Impacto acumulado:** −645 segmentos, +1 voto. 0 regresiones.

**Estado:** cerrado.

## B078 — Zonas editoriales en zonificador (revertido)

**Severidad:** baja. **Detectado:** H058.

Intento de agregar zonas `acordada`/`indice`/`discurso` en Pasada 1
de `zonificar_bloque` como safety net para contenido editorial
residual dentro de bloques de caso. Revertido por regresión:
`_en_editorial` (flag irreversible) se activaba con `ACORDADAS`
standalone en sumarios temáticos, suprimiendo firma y todos los
anclas posteriores. sin_firma subió de 34 a 74.

**Fix requerido (si se reimplementa):** guard posicional — solo
activar `_en_editorial` después de la última firma detectada en el
bloque. Alternativa: restringir la activación al último caso del
archivo (flag pasado como parámetro a `zonificar_bloque`).

**Prioridad:** baja. Con el corte en `detectar_fin_real` funcionando,
el contenido editorial no entra en bloques de caso. El zonificador
solo sería necesario como safety net para edge cases no cubiertos
por la pista.

**Estado:** abierto (diferido).

## B079 — Arquitectura editorial: subtipos de índice y parser separado

**Severidad:** cosmética→media (escalabilidad). **Detectado:** H058.
**Ampliado:** H059. **PoC validada:** H060.

El CSV editorial clasifica todos los índices como zona genérica
`indice`. Falta distinguir subtipos:
- `indice_partes` (INDICE POR LOS NOMBRES DE LAS PARTES)
- `indice_materias` (INDICE ALFABETICO POR MATERIAS)
- `indice_legislacion` (INDICE DE LEGISLACION)
- `indice_general` (INDICE GENERAL / tabla de contenidos)
- `acordadas` (ACORDADAS DE LA CSJN / A C O R D A D A S Y R E S O L U C I O N E S)
- `discurso` (DISCURSOS)

**Problema arquitectural (H059):** los regex de clasificación
editorial (`ACORDADAS`, `INDICE`, `POR MATERIAS`) matchean texto
dentro de fallos. La detección de corte (Capa 1, `detectar_fin_real`)
no genera FP porque busca en rango acotado, pero la clasificación
(Capa 2, `_tipo_zona_editorial`) es frágil — demostrado por los
67 FP de `acordada` corregidos en H059. Agregar regex nuevos para
subtipos o para parsear estructura interna amplifica el riesgo.

**Propuesta:** `parser_editorial.py` como módulo separado. La
separación de dominio (caso vs. editorial) antes de parsear
elimina la necesidad de guards anti-FP. Permite parsear la
estructura interna de los índices (case_name, descriptores
temáticos, legislación citada), acordadas (número, fecha, texto),
y discursos. Escalable para el doctorado (tomos nuevos).

**PoC H060 — Resultados:**
- 135 secciones detectadas (de 53 genéricas): 45 indice_partes,
  18 indice_materias, 20 indice_legislacion, 46 indice_general,
  5 acordadas, 1 discurso. 0 desconocido.
- Detección por títulos-mojón (primera aparición de cada título
  conocido) + openers para subtipo inicial del bloque.
- Opener espaciado por OCR: `A C O R D A D A S  Y  R E S O L U C I O N E S`
  resuelve 2 secciones que eran `desconocido`.
- Truncado de INDICE GENERAL: última línea con `\.{4,}\s*$`
  (puntos trailing = entry TOC) + su página de inicio = fin del TOC.
  Sin puntos (Era 2, TOC degradado) → no trunca.
  Descarta boilerplate post-TOC y acumulativo de 330.4 (12.078 líneas).
- 329.4 conserva entry legítima de 6 puntos (Jurado de Enjuiciamiento).
- Anomalía 330.4 documentada: único archivo con índice acumulativo
  post-TOC. Se descarta por consistencia con procesamiento per-archivo.
- HOJA COMPLEMENTARIA descartada como marcador (aparece en cuerpo).

**Pendiente (H061):** Integrar en `parser_editorial.py`, migrar
desde `parser.py`, actualizar CSV con columna subtipo, commit.

**Resolución H061:**
- `parser_editorial.py` creado con `clasificar_editorial()` (254 líneas).
- parser.py refactorizado: eliminados `extraer_secciones_editoriales`,
  `_tipo_zona_editorial`, `RE_EDITORIAL_ACORDADA/DISCURSO/INDICE`,
  `lineas_editorial` (dead code). Retenidos `RE_EDITORIAL_ANY` +
  `_es_marcador_editorial` (Pista 4).
- Parseo de entries del índice de partes explorado y descartado —
  redundante con `construir_catalogo.py` (`parsear_indice_nombres`),
  que es más robusto (NBSP, separador "y", mid-line, extensión de
  inicio). Fuente canónica: `output/catalogo/catalogo.csv`.
- Crosscheck catálogo vs parser: 0 MISS, 450 EXTRA (casos en parser
  no listados en índice — legítimos). Pipeline reproducible (diff 0).
- LibroVol330.2.md: no tiene indice_partes en clasificador (45/46).
  `construir_catalogo.py` la cubre con `extender_inicio_indice_nombres`.

**Estado:** cerrado (H061).

### B077 — Quiebres de línea con guión rompen detección de outcomes — APLICADO H066

**Componente:** parser (classify_outcome).
**Origen / fuente del diagnóstico:** H066, análisis de 334_p256 ("mal con- cedido"
no matchea `mal concedid[ao]`).
**Causa raíz:** el texto digitalizado corta palabras con guión al final de
línea ("se deses- tima", "se revo- ca", "proce- dente", "mal con- cedido").
Los regex de OUTCOME_PATTERNS_DISPOSITIVO esperan palabras continuas y no
matchean las variantes rotas. El dispositivo cae en catch-all "otro", lo que
deshabilita la merit guard y permite que paso 3 (280/ac4) sobreescriba con
un outcome incorrecto.
**Diagnóstico / evidencia:** 37.3% de los fallos (2112/5667) tienen guión de
quiebre en por_ello_text. 150 rompen un outcome keyword. 85 cambiarían de
outcome de dispositivo con la normalización. 229 outcomes finales cambian
(simulación sobre CSV H065).
**Estado de verificación:** `confirmado_cuantificado`.
**Fix aplicado (H066):** función `_unhyphenate(text)` que aplica
`re.sub(r"(\w)[-\u00ad]\s+(\w)", r"\1\2", text)` — une quiebres tipográficos
sin tocar guiones legítimos (Buenos Aires-La Plata no tiene whitespace
después del guión). Aplicada en `classify_outcome` v12 (paso 0, antes de
regex matching) y en el fallback sin_dispositivo. No modifica el texto
almacenado en CSV, solo el usado para clasificación.
**Validación (H067):** re-run confirmado. otro: 1791→1668 (-123),
redistribuidos a outcomes correctos: procedente +51, confirma +17,
competencia +15, hace_lugar +11, 280 +18, ac4 +12, abstracto +3,
mal_concedido +1, originaria +1. Diverge de la simulación H066 porque
el re-run re-extrae texto desde .md fuente (más preciso que el CSV viejo).
**Referencias cruzadas:** H066, H067. Afecta B025 (falsos unánime), 280/ac4
(merit guard), sin_firma (indirectamente via outcomes).


### B078 — RE_ACORDADA_4 no captura "art. N de la acordada 4/2007" — APLICADO H066

**Componente:** parser (classify_outcome, regex ac4).
**Origen / fuente del diagnóstico:** H066, auditoría de 40 ac4.
**Causa raíz:** las dos regex originales (RE_ACORDADA_4_CONSIDERANDO y
RE_ACORDADA_4_REGLAMENTO) exigen la secuencia "del reglamento ... acordada
4/2007". La Corte también usa la variante directa "art. N de la acordada
4/2007" (sin mencionar "reglamento"). Además, el año solo aceptaba "2007"
(4 dígitos), no la variante corta "4/07". Y "art." no matcheaba "arts."
(plural).
**Diagnóstico / evidencia:** 1 FN confirmado (333_p1235: "artículo 4º de la
acordada 4/2007, por lo que corresponde declarar inadmisible"). 4 borderline
(menciones contextuales que la regex captura: 339_p597, 342_p122, 344_p1783,
348_p1502) — revisar post re-run.
**Estado de verificación:** `confirmado_cuantificado`.
**Fix aplicado (H066):** tres cambios:
1. Nueva regex `RE_ACORDADA_4_DIRECTA`: captura "art. N de la acordada 4".
2. Año: `2007` → `(?:20)?07` en las 3 regex.
3. Guard: `4` → `4(?!\d)` para no matchear "acordada 47/91" etc.
4. Plural: `art\.?` → `art[s]?\.?` para matchear "arts.".
Agregada en classify_outcome (paso 3) y fallback sin_dispositivo.
**Validación:** 8/8 strings de prueba correctos. 34/40 actuales preservados.
6 FP fantasma (sin mención de ac4 en texto) quedan fuera. FN 333_p1235
recuperado.
**Validación (H067):** re-run confirmado. ac4: 40→52. 0 fantasmas
detectables (los 12 sin match en CSV truncado son textos donde la
mención aparece después de los 2000 chars — el parser clasifica con
texto completo). Los 6 fantasmas del CSV viejo desaparecieron (guard
`4(?!\d)` funciona). 4 borderline siguen como ac4.
**Referencias cruzadas:** H066, H067. Subsume el fix de regex parcial de H065.


### B079 — MERIT_OUTCOMES incompleto en classify_outcome — CERRADO H067

**Componente:** parser (classify_outcome).
**Origen / fuente del diagnóstico:** H067, auditoría post re-run B077+B078.
**Causa raíz:** MERIT_OUTCOMES en classify_outcome solo contenía
{hace_lugar, procedente, revoca, confirma, nulidad}. Faltaban competencia,
abstracto, originaria, desistimiento. Estos outcomes de dispositivo eran
sobreescritos por 280/ac4 en paso 3 cuando el considerando mencionaba
art. 280 o acordada 4, aunque la mención fuera tangencial.
mal_concedido NO se agrega: puede coexistir legítimamente con 280/ac4
(la Corte declara "mal concedido" porque "es inadmisible art. 280").
**Diagnóstico / evidencia:** 5 casos afectados:
331_p1854 (280→competencia), 331_p2309 (280→abstracto),
330_p5158 y 338_p724 (280→originaria), 340_p251 (280→desistimiento).
Verificación: 3 mal_concedido+280 confirmados como genuinos (329_p292,
329_p437, 330_p88: el considerando dice "es inadmisible art. 280").
**Estado de verificación:** `confirmado_cuantificado`.
**Fix aplicado (H067):** MERIT_OUTCOMES ampliado a {hace_lugar, procedente,
revoca, confirma, nulidad, competencia, abstracto, originaria, desistimiento}.
Docstring de classify_outcome actualizado (v12b).
**Validación (H067):** re-run confirmado. 280: 296→291 (-5). competencia
577→578 (+1), originaria 158→160 (+2), abstracto 86→87 (+1),
desistimiento 9→10 (+1). mal_concedido 38→38 (sin cambio, correcto).
**Referencias cruzadas:** H067.


### B080 — RE_280_ABREVIADO (CPCCN, C.P.C.C.N.) — POC REVERTIDO H067

**Componente:** parser (classify_outcome, regex 280).
**Origen / fuente del diagnóstico:** H067, análisis del corpus de 280
(corpus_inadmisible_280.md, 291 casos). Inventario de formas de cita:
535 "del Código Procesal Civil y Comercial", 219 "CPCCN", 222 "C.P.C.C.N.",
21 "del CPCCN", 24 "del C.P.C.C.N.", ~3 "del CPCC".
**Causa raíz:** RE_280_LIBRE exige "del Código Procesal Civil y Comercial".
Si un caso solo usa la forma abreviada (CPCCN, C.P.C.C.N.), no matchea.
**Diagnóstico / evidencia:** POC sobre CSV: 1 FN recuperado (344_p3095,
desestima→280, usa "art. 280 del CPCCN"). Re-run parser: 280 291→292 (+1).
0 FP. La forma abreviada casi siempre coexiste con la forma larga.
**Decisión (H067):** revertido. 1 caso no justifica regex extra (REE).
**Estado del fix:** revertido.
**Referencias cruzadas:** H067.


### B082 — classify_outcome corre sobre bloque completo incluyendo disidencias — FIX PARCIAL H070

**Componente:** parser (extraer_considerando / classify_outcome).
**Origen / fuente del diagnóstico:** H069, efecto colateral del fix
bidireccional B045.
**Causa raíz (corregida H070):** `extraer_considerando` no excluía
líneas de votos individuales (>= inicio_votos_indiv). El texto de
disidencias, votos según su voto, y sumarios editoriales filtraba al
considerando_text. En 19 casos, la detección de art. 280 en texto de
disidencia contaminaba el outcome (inadmisible_280 incorrecto).
Diagnóstico H069 parcialmente incorrecto: los 3 sospechosos originales
(344_p220, 347_p818, 348_p659) son unánimes sin disidencias — outcomes
"otro" legítimos, no B082.
**Fix aplicado (H070):** excluir del considerando todas las líneas
>= inicio_votos_indiv (fix posicional). 3 líneas de código.
Validación: 19 outcomes corregidos (todos inadmisible_280 → outcome
correcto del dispositivo: 10 desestima, 8 otro, 1 mal_concedido),
66 wc_considerando limpiados (Δ promedio -1155 palabras), 0 regresiones,
0 cambios voting_pattern, 3 is_originaria corregidos.
**Residual:** `por_ello_text` sigue extrayéndose del bloque completo.
En 64 casos, por_ello_idx >= inicio_votos_indiv (el dispositivo de
la mayoría está después de headers de votos). El fix v3 limpia el
considerando pero no aborda este camino — requiere que el zonificador
distinga zonas de mayoría vs votos individuales (ver M10).
**Referencias cruzadas:** H069. H070. B045. M10.


### B083 — considerando_text incluye residuo_caso_anterior — CERRADO H071

**Componente:** parser (extraer_considerando).
**Origen / fuente del diagnóstico:** H071, barrido diagnóstico de monstruos.
**Causa raíz:** `extraer_considerando()` (L703) excluía `lineas_dictamen`
pero NO `lineas_residuo`. `wc_mayoria` (L2554) sí excluía ambos.
Resultado: considerando_text capturaba sumarios, dictámenes PGN y headers
editoriales del caso anterior. En 161 casos wcC > wcM (72 sin dictamen).
Concentrado en competencia (26 casos) y otro (15).
**Fix aplicado (H071):** L2514: `_lineas_no_cons = set(lineas_dictamen) | lineas_residuo`.
1 línea. Validación: 0 outcomes cambiados, 617 wcC limpiados (todos Δ
negativos, min=-4640, mean=-116), 2 is_originaria FP corregidos
(329_p2469, 330_p1599: residuo mencionaba art. 117 / cónsul del caso anterior),
wcC > wcM: 161→0. 0 regresiones.
**Referencias cruzadas:** H071. B082.


### B084 — Tier 4 dispositivo "así se resuelve" — CERRADO H071

**Componente:** parser (detección de dispositivo).
**Origen / fuente del diagnóstico:** H071, clasificación de 37 sin_dispositivo+firma.
**Causa raíz:** 7 fallos usan "Lo que así se resuelve" / "Así se resuelve"
como cierre dispositivo en vez de "Por ello". El parser no tenía esta variante.
Es un CIERRE (no apertura), aparece mid-line, siempre precede a firma.
**Fix aplicado (H071):** Tier 4 — último recurso, solo si Tier 1/2/3 no
encontraron nada. `.search()` mid-line con firma validada obligatoria.
20 líneas. Validación: 7 sin_dispositivo→otro, 0 regresiones.
Casos: 329_p317, 330_p22, 330_p4590, 331_p548, 333_p1784, 340_p1392, 348_p532.
**Referencias cruzadas:** H071. B085 (Por ello perdido). B086 (otras fórmulas).


### B085 — 7 "Por ello" genuinos no detectados por Tier 1/2/3 — CERRADO H072

**Componente:** parser (detección de dispositivo).
**Fix aplicado (H072):** Tier 3b insertado entre Tier 3 y Tier 4. Búsqueda
forward desde línea 0 hasta len(bloque), sin exclusión de lineas_dictamen,
sin restricción de rango. Firma validada obligatoria, sin fallback. Guarda
argumental extendida (opino, opinó, etc.). Validación PoC corpus completo:
71 mejoras (5/7 B085 targets + 66 extras), 0 regresiones. Los 2 targets
no contados (331_p1013, 334_p1033) ya eran resueltos por el baseline del
PoC — diferencia entre reimplementación simplificada y parser real.
sin_dispositivo 50→40.


### B086 — Fórmulas dispositivas alternativas — FIX PARCIAL H072

**Componente:** parser (detección de dispositivo).
**Fix aplicado (H072):** "el Tribunal resuelve" agregado a Tier 4 regex
junto a "así se resuelve". 4 casos rescatados: 330_p1971→otro,
331_p2363→otro, 334_p362→otro, 339_p676→abstracto. sin_dispositivo 40→35.
**"Hágase saber" descartado (H072):** revisión manual confirmó que "Hágase
saber y archívese" es providencia de mero trámite, no dispositivo. El
dispositivo real está embebido en el considerando (caducidad de instancia,
competencia).
**Residual (4 sin_dispositivo):** 330_p1172 (competencia, "deberá entender"),
330_p2794 (caducidad), 343_p473 (competencia), 344_p776 (competencia).
Dispositivo embebido sin fórmula estándar. → ver B090 (Tier 5).
**classify_outcome:** 331_p2363 y 334_p362 dan "otro" en vez de "revoca". → ver B091.
**Referencias cruzadas:** H071, H072. B084, B090, B091.


### B087 — 4 unanime que deberían ser segun_su_voto (wcM≤4) — CERRADO H072

**Componente:** parser (voting_pattern).
**Fix aplicado (H072):** guard post-firma: si voting_pattern=="unanime" y
wc_mayoria≤4 y wc_votos>wc_mayoria, reclasificar a segun_su_voto.
5 casos corregidos (4 originales + 331_p793). unanime 3501→3496,
segun_su_voto 740→745.


### B088 — 330_p2849 linea_fin_real desbordada al índice editorial (110k wc) — CERRADO H072

**Componente:** parser (detectar_fin_real).
**Fix aplicado (H072):** reorden de Pistas en detectar_fin_real. Pista
editorial (B077) movida de posición 4 a posición 2, antes de sumario y
apertura. El bug ocurría porque Pista 2-sumario encontraba un header
de sumario dentro del índice editorial y cortaba ahí, impidiendo que
Pista 4-editorial detectara los marcadores reales. Post-fix: 330_p2849
wc 110236→7448, status_fin fin_por_editorial. Efecto colateral positivo:
editorial sections 135→150, zonas 142489→141938, votos 27377→27382.
0 regresiones en sin_dispositivo (35).


### B089 — Bloque incluye residuo del caso anterior (pre-carátula) — PARCIAL H074

**Componente:** parser (delimitación de bloques).
**Origen / fuente del diagnóstico:** H072, revisión manual de 329_p2221.
**Causa raíz:** el bloque de cada caso arranca en el inicio de la página
compartida, no en la carátula. Todo el contenido previo a la carátula
(epílogo, firma, dispositivo del caso anterior) queda dentro del bloque.
Cuando el caso anterior es corto y cabe entero en la página compartida,
el parser captura `apertura_rel`, dispositivo y firma del caso
**equivocado** — el caso real nunca se parsea.
**Impacto confirmado (H072):** 61 casos con `por_ello_text` idéntico al
caso anterior (data corruption silenciosa). Concentrados en tomos
tempranos (329+). Además, 96% de bloques (5646/5862) tienen residuo
que contamina zonas y word counts.
**Estado de verificación:** `confirmado_cuantificado`.
**Fix parcial aplicado (H074):** causa raíz identificada: `refinar_inicio_por_titulo`
no normalizaba tildes (mismo bug que B071 en Pista 1). El catálogo tiene
tildes ("Juárez", "Martínez") pero el .md es ALL CAPS sin tildes ("JUAREZ").
Fix: `_strip_accents` en token y línea del bloque para matching
tilde-insensitive. Aplicado también a B074 `_li_for_dfr`.
Guarda adicional: skip match en últimas 5 líneas del bloque (protege contra
token que matchea carátula del caso siguiente, ej: 329_p2218 "Bergés"
matcheaba "BERGES" al final del bloque).
Validación: ancla_catalogo 428→123 (-305), ~490 casos afectados, ~15
outcomes corregidos, votos +17, 0 regresiones reales. 2 aparentes
(329_p5151, 329_p326) son correcciones de datos previamente corruptos.
**Residuo:** 123 ancla_catalogo restantes. Desglose: 51 token corto (<4
chars, B095), 59 token sin tilde que no matchea (residuo >50 líneas o
nombre distinto en .md), 12+ otros (cruza archivos, página no en mapa).
**Prioridad:** residuo no es bloqueante (zonificador protege), pero B095
es atacable.
**Referencias cruzadas:** H072, H074. B083, B092, B095.


### B090 — Tier 5: fallback para sin_dispositivo con dispositivo embebido

**Componente:** parser (detección de dispositivo).
**Origen / fuente del diagnóstico:** H072, revisión manual B086 residuales.
**Causa raíz:** fallos cortos donde el dispositivo está integrado en el
considerando sin fórmula introductoria ("Por ello", "tribunal resuelve").
Patrones: "deberá entender" (competencia), "declárase competente",
"declárase operada la perención" (caducidad).
**Casos testigo:** 330_p1172, 330_p2794, 343_p473, 344_p776.
**Diseño propuesto:** Tier 5 que solo corre cuando por_ello_idx sigue
None después de Tiers 1-4. Buscar patrones embebidos con firma validada.
Sin riesgo de desplazar dispositivo correcto (no hay ninguno que
desplazar). Guarda opcional de wc bajo.
**Estado de verificación:** `confirmado_caso_testigo`.
**Estado del fix:** diseñado, PoC pendiente.
**Referencias cruzadas:** H072. B086.


### B091 — classify_outcome no detecta "revoca" en textos con "tribunal resuelve" — CERRADO H073

**Componente:** parser (classify_outcome).
**Fix aplicado (H073):** fallback `("revoca", re.compile(r"\brevocar\b", re.I))`
insertado justo antes del catch-all "otro" en OUTCOME_PATTERNS_DISPOSITIVO.
Posición final para que originaria, abstracto y otros merit outcomes
mantengan prioridad. classify_outcome v13. Validación corpus completo:
151 outcomes cambiados (otro→revoca ~140, inadmisible_280→revoca ~10
por merit guard), 1 FP marginal (347_p109, editorial). revoca 208→359.
0 regresiones en sin_dispositivo, sin_firma, votos.
**Referencias cruzadas:** H073. B086.


### B092 — Dictamen embebido sin header: zonificador no detecta, infla dispositivo

**Componente:** parser (zonificador).
**Origen / fuente del diagnóstico:** H072, inspección de 329_p49.
**Causa raíz:** dictámenes que aparecen antes de "FALLO DE LA CORTE
SUPREMA" sin header "DICTAMEN DEL PROCURADOR" no son clasificados como
zona dictamen. Si contienen "Por ello" (ej: "Por ello, es mi parecer"),
el zonificador los clasifica como zona dispositivo, inflando wc del
dispositivo. Resultado: `dictamen_presente=False`, `wc_dictamen=0`,
zona dispositivo inflada.
**Caso testigo:** 329_p49 (Cáceres c/ La Rioja). Dictamen de Bausset
con "Por ello, es mi parecer..." clasificado como dispositivo (2 seg,
308 wc). Parser captura dispositivo correcto del Tribunal más abajo.
**Impacto:** campos estructurales (outcome, por_ello_text, firma)
correctos. Solo afecta `dictamen_presente`, `wc_dictamen` y zonas.
**Estado de verificación:** `confirmado_caso_testigo`. Cardinalidad
desconocida.
**Estado del fix:** no diseñado. B089 (trimming pre-carátula)
mitigaría parcialmente.
**Referencias cruzadas:** H072. B089.


### B093 — Pista 1 falsa carátula por token genérico en citas del cuerpo — CERRADO H073

**Componente:** parser (detectar_fin_real, primer_token_de_caratula).
**Origen / fuente del diagnóstico:** H073, análisis de 31 sin_firma.
**Causa raíz:** `primer_token_de_caratula` devolvía el primer token
significativo (ej: "Provincia", "ANSeS") sin verificar si era genérico.
Pista 1 encontraba estos tokens en citas jurisprudenciales del cuerpo
("Fallos: 329:573", "Halper, Cristina María c/ ANSeS"), firmas de
jueces ("Ricardo Luis Lorenzetti"), o transcripciones in extenso
("Dicha sentencia dice así:"), truncando el bloque antes de la firma.
**Fix aplicado (H073):** dos capas:
1. `primer_token_de_caratula` reescrita con búsqueda profunda: recorre
   TODOS los tokens de TODAS las variantes (separadas por "|"), saltea
   tokens en `_GENERICOS` (provincia, anses, nación, estado, afip,
   buenos, nacional, administracion, federal, direccion, instituto),
   devuelve el primer token específico. Ej: "D.G.I. c/ Provincia de
   Mendoza" → "Mendoza"; "ANSeS (Benaben c/) | Benaben c/ ANSeS" →
   "Benaben".
2. `_STOPLIST_PISTA1` sincronizada con `_GENERICOS` como red de
   seguridad: si ambas variantes son entidades genéricas, Pista 1
   se saltea y el fallo cae a Pista 2/3/4/fallback-firma.
**Iteraciones descartadas:** guarda de mayúsculas ≥60% (v1, −297
votos por carátulas mixed-case en tomos 337+); stoplist sola (v2,
+0 votos, +6 blanks).
**Validación:** sin_firma 31→17 (−14), sin_dispositivo 35→24 (−11),
votos 27382→27455 (+73), blanks 194→193 (−1). 0 regresiones masivas.
**Residuo (17 sin_firma):** ~5 citas in extenso (token específico
aparece en texto transcrito), ~4 bloques cortos, ~3 firma atípica
o token en firma, ~5 otros. 1 regresión nueva: 329_p1881
(Tortorelli, no era sin_firma antes de B093, investigar causa).
**Referencias cruzadas:** H073. B070, B071.


### B094 — Pista 1 forward matchea firma de juez como carátula del siguiente — CERRADO H074

**Componente:** parser (detectar_fin_real, Pista 1 forward).
**Origen / fuente del diagnóstico:** H074, regresión 329_p1881 post-B093.
**Causa raíz:** B093 cambió el token del caso siguiente (Zavalía c/
Provincia de Santiago del Estero) de "Provincia" a "Santiago". "SANTIAGO"
matcheaba en la firma "ENRIQUE SANTIAGO PETRACCHI —" antes de llegar a
la carátula real. Pista 1 cortaba en la firma → bloque perdía la firma.
`_es_texto_corriente` no filtraba porque la firma es ALL CAPS.
**Fix aplicado (H074):** guarda en Pista 1 forward: si la línea matchea
`linea_es_firma_de_juez` Y tiene raya (— o –), skip y seguir buscando.
Raya obligatoria para no filtrar carátulas de jueces-parte (Boggiano,
Moliné O'Connor — verificados: 0 FP en 5862 casos).
**Validación:** diff 5862 casos: 8 cambios, todos en 2 casos recuperados.
sin_firma 17→15 (329_p1881 Tortorelli, 340_p1213). 0 regresiones.
**Referencias cruzadas:** H074. B093, B070.


### B095 — Token corto en refinar_inicio_por_titulo (ancla_catalogo residual) — PARCIAL H076

**Componente:** parser (refinar_inicio_por_titulo).
**Origen / fuente del diagnóstico:** H074, diagnóstico B089 residual.
**Causa raíz:** 51 casos con `case_name_indice` corto o anonimizado
(N.N., R.M., J.L., EMM S.R.L., QC, etc.) donde `primer_token_de_caratula`
devuelve tokens <4 chars. La función los descarta por riesgo de FP en
texto. Resultado: `refinar_inicio_por_titulo` no recorta el residuo.
**Importancia:** muchos son casos sensibles (menores, privacidad,
causas penales anonimizadas) donde la anonimización genera nombres
cortos. No son marginales.
**Fix aplicado (H075):**
- Pista 5 H1: prefix match (sin trailing `\b`) como fallback cuando
  word-boundary falla. Cubre abreviaciones catálogo→.md: Camnasi→CAMNASIO,
  Transp→TRANSPORTES, Schr→SCHRÖDER, Bank→BANKBOSTON, Pers→PERSONAL,
  Serv→Servicios. 6 casos. Commit `ff7b765`.
- Pista 5b: fullname + inverted para token <4. Busca el nombre completo
  del catálogo como frase, primero directo ("N. N.") luego invertido
  ("S. D. P." ← "P., S. D.") porque el catálogo usa "apellido, nombre"
  pero el .md usa "nombre apellido". Para carátulas con "c/", invierte
  cada parte. 41 casos rescatados. -2 votos = mejora (firma caso anterior
  contaminante removida, confirmado con auditar_fallo).
- Total: ancla_catalogo 122→75 (-47). Zonas -137 (residuo eliminado).
**Fix aplicado (H076) — Tier 4:**
- Ventana ampliada (100 líneas) como fallback cuando Tiers 1-3 (ventana
  50) fallan. Guardas portadas de Pista 1 de detectar_fin_real:
  `_es_texto_corriente` con retry loop, stoplist + `segundo_token_de_caratula`
  confirmatorio para tokens genéricos, trim ≤50%, fullname+inverted para
  TODOS los tokens (no solo <4). "Vistos los autos" extendido a 100 líneas.
- 11 casos rescatados (8 por Tier 4a exact guardado, 3 por vistos ampliado).
  ancla_catalogo 75→64. Zonas -99. 0 regresiones. 2 outcomes corregidos
  (contaminación del caso anterior eliminada).
**Residuo pendiente:** 64 ancla_catalogo. Desglose: 36 OCR/typo catálogo→.md
(no atacables sin fuzzy matching o parche manual), 17 token<4 sin match
fullname, 11 ventana/genéricos bloqueados por guardas (trim>50% o sin
segundo token).
**Estado de verificación:** `confirmado_cuantificado`.
**Estado del fix:** aplicado (parcial).
**Referencias cruzadas:** H074, H075, H076. B089.

### B096 — Residuo post-epílogo: sumarios del caso siguiente en bloque

**Componente:** parser (detectar_fin_real).
**Origen / fuente del diagnóstico:** H075, spot-check 333_p1192 post-fix.
**Causa raíz:** `linea_fin_real` se extiende más allá del epílogo del caso
e incluye sumarios editoriales del caso siguiente (HOJA COMPLEMENTARIA,
carátula+sumarios de otro caso). Pista de fin no detectó el límite.
**Diagnóstico / evidencia:** 333_p1192 — después de firma + datos recurso
+ tribunal de origen, aparecen HOJA COMPLEMENTARIA + carátula "CESAR
VALENZUELA" + sumarios de EXTRADICION que pertenecen al caso siguiente.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** buscar patrón en otros casos con `fin_extendido`.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** H075.

### B097 — Voto de Argibay cortado en display (zona voto mal delimitada)

**Componente:** parser (zonificador).
**Origen / fuente del diagnóstico:** H075, spot-check 331_p466 post-fix.
**Causa raíz:** la disidencia de Argibay aparece contada correctamente
(disidencia) pero el span del voto está truncado: "Disidencia de la señora"
como zona de voto separado, "ministra doctora doña Carmen M. Argibay" como
firma. El contenido del voto no se captura completo en la zona.
**Estado de verificación:** `confirmado_caso_testigo`.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** H075.

### B098 — Tomo 335: encabezados de voto fragmentados por OCR

**Componente:** parser (detectar_fin_real / firma).
**Origen / fuente del diagnóstico:** H079, incorporación tomo 335.
**Causa raíz:** el OCR de tomo 335 fragmenta los encabezados de voto
individual en múltiples líneas cortas: "TO DEL SEÑOR MINISTRO",
"DENCIA DE LA SEÑORA", "MINISTRA DOCTORA DOÑA CARMEN", etc. El parser
no reconoce estos fragmentos como marcadores de voto → sin_firma masivo.
**Diagnóstico / evidencia:** sin_firma salta de 16 a 78 (+62, todos de
tomo 335). Ratio votos/fallos en 335: 311/255 = 1.2 (normal ~5).
Top desconocidos en firma: fragmentos de encabezados de voto.
**Estado de verificación:** `confirmado_cuantificado`.
**Diagnóstico refinado (H080):** la prosa del cuerpo (considerandos, "por ello",
resúmenes editoriales, carátulas-en-cuerpo) está LIMPIA. El daño está localizado
en el bloque de cierre de cada fallo (fecha + firmas), que en el PDF es imagen
embebida (firma digital) y no texto. Eso rompe la detección de firma y arrastra
los cuerpos vacíos, porque el parser usa fecha/firma como anclas estructurales.
62 fallos sin firma / 207 (30%). No recuperable por parser: no hay texto.
**Estado del fix (H080):** vía decidida — re-escanear SOLO las páginas de cierre
del tomo papel (nombres tipeados, OCR limpio) de los 62 fallos rotos. Worklist
generado: `335_firmas_a_escanear.csv` (62 filas, página inicio/cierre estimado).
PARQUEADO: pendiente conseguir tomo papel.
**Referencias cruzadas:** H079, H080.

### B099 — Tomo 336: construir_catalogo no detecta índice editorial

**Componente:** construir_catalogo.
**Origen / fuente del diagnóstico:** H079, incorporación tomo 336.
**Causa raíz:** el formato del índice editorial en tomo 336 difiere de
los tomos existentes. `construir_catalogo.py` no detecta entradas →
0 filas en catálogo → 0 en fallos_localizados → parser no procesa 336.
El OCR de 336 también tenía formato distinto (page numbers inline con
tomo: "336 29" / "80 336"), corregido con preprocesamiento.
**Diagnóstico / evidencia:** `Select-String "^336" catalogo.csv` = 0.
detectar_paginas sí procesa 336 correctamente (843+1582 headers).
**Estado de verificación:** `confirmado_cuantificado`.
**Diagnóstico refinado (H080):** la hipótesis de columnas entreveradas por
Tesseract quedó REFUTADA con datos. Causa real: 336 no tiene índice de nombres
canónico; solo un índice general alfabético por carátula, con header
"Índice"/"Indice" suelto (title case) y SIN ancla ": p.". Dos sub-formatos:
336.1 trailing ("Carátula. 448"), 336.2 con líderes de puntos
("Carátula s/ tipo. ... 1477"). El cuerpo de 336 arrastra el mismo daño de
bloque de cierre que 335 (ver B098).
**Estado del fix (H080):** DISEÑADO Y VALIDADO, PARQUEADO. construir_catalogo
v1.01 agrega ruta 336 (header title-case + dos extractores, guarda "canónico
primero" = cero regresión). Validado: 336 = 138 entradas (62 vol.1 + 76 vol.2),
329-349 idénticos al baseline (catálogo 6117→6255). El patch NO está mergeado a
main: vive como archivo (`construir_catalogo.py` patcheado) y en branch
`tomos-335-336`. Se incorpora junto con el re-escaneo de firmas (B098) cuando
llegue el papel.
**Referencias cruzadas:** H079, H080.

### M11 — Versionar scripts canónicos con __version__ — CERRADO H076

**Componente:** parser + pipeline + auditor.
**Origen:** H075, propuesta de Guillermo.
**Fix aplicado (H076):** `__version__` agregado a 6 scripts canónicos:
parser.py (v18.01), parser_editorial.py (v1.0), construir_catalogo.py (v1.0),
cruzar_catalogo_y_mapa.py (v1.0), detectar_paginas.py (v1.0),
auditar_fallo.py (v1.0.0, ya lo tenía). Print de versión en output del parser.
Convención: minor sube .01 por sesión, major por cambio de arquitectura.
**Referencias cruzadas:** H076.

### M12 — Harness de regresión del parser (red para refactor) — APLICADO H084

**Componente:** infra / tests.
**Origen / fuente del diagnóstico:** H084. Restricción REE innegociable del
frente A: ningún refactor se mergea sin demostrar outputs idénticos (diff de los
CSV canónicos pre/post sobre el corpus completo). El diagnóstico encontró que esa
condición no se podía ejecutar: no había red.
**Descripción:** el parser de 3638 líneas (procesar_archivo 757 líneas;
classify_outcome; cascada de dispositivo Tier 1→2→3→3b→4; es_originaria 212
líneas) producía los 4 CSV canónicos sin ningún test de regresión.
`scripts/tests/` cubría los scripts chicos (clasificador, construir_catalogo,
cruzar_catalogo_y_mapa, detectar_paginas) pero NO parser.py ni auditar_fallo.py.
Existía `csjn_casos_BASELINE_H079.csv` suelto, sin harness que lo usara.
Refactorizar bajo esa condición violaba la propia regla REE ("refactor sin red").
**Fix aplicado (H084):** `scripts/tests/check_regresion.py`, harness de dos modos.
`--make-golden` corre el parser a un dir temporal y congela los 4 CSV
(casos/votos/zonas/editorial) en `scripts/tests/golden/`. Modo default corre el
parser a otro temporal y diffea contra el golden: SHA256 por archivo (pasada
rápida) + diff posicional fila-a-fila celda por celda en caso de mismatch
(reporta fila, caso_id, columna). Sale con código 1 si cambia una sola celda.
Nunca pisa `output/parser/` productivo (corre a tempdir). Invoca con
`cwd=scripts/pipeline` para resolver el import de `parser_editorial`.
**Validación:** golden congelado sobre main `bcc143f`; `check` inmediato dio
[CLEAN] (4/4 CSV idénticos; el golden se reproduce a sí mismo).
**Alcance:** cubre los 4 CSV de parser.py. NO cubre
`csjn_editorial_indice_partes.csv` (lo emite parser_editorial.py aparte) ni el
pipeline upstream (catálogo/localización/cruce), tratados como inputs congelados.
Extender a esos es otro golden con otra invocación.
**Habilita:** refactor seguro de M03 (unidad por línea), M07 (dedup
parser↔auditor), M08 (`_ordenar_y_validar`), classify_outcome gate+action, y el
colapso de la cascada de tiers en procesar_archivo. Cada refactor se gatea a
[CLEAN]: si cambia un número, es bug, no refactor.
**Referencias cruzadas:** H084. M03, M07, M08.

### M13 — Descomposición de procesar_archivo (función monstruo) — EN PROGRESO

**Componente:** parser.
**Origen / fuente del diagnóstico:** H084 (diagnóstico de deuda estructural).
**Diagnóstico:** procesar_archivo concentraba 757 líneas mezclando localización,
detección de sumarios, dictamen zonificado y la cascada de dispositivo Tier
1→2→3→3b→4. Acumulación incremental pura: cada tier agregado en sesión distinta
(B067, B084, B085, B086) con la misma forma "si los anteriores no encontraron
nada, repetir con menos guardas".
**Plan:** descomponer en pasos de extracción pura (cada uno gateado a [CLEAN]
por M12) y, recién después, refactor de la lógica de las piezas ya aisladas.
Mover primero, reescribir después: más barato de depurar que las dos cosas a la vez.
**Progreso:**
- **R1 (H085) — APLICADO.** Cascada Tier 1→4 extraída a
  `resolver_dispositivo(bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv)
  → (por_ello_idx, por_ello_text)`. Extracción pura, 0 cambios de heurística.
  Contrato verificado leyendo el código: las internas (inicio_busqueda,
  fin_busqueda, dictamen_end) no escapan; los únicos valores que cruzan la
  frontera son por_ello_idx y por_ello_text. procesar_archivo 757→543 líneas.
  check_regresion [CLEAN] (4/4 CSV idénticos al golden). parser v18.06.
  Commit en branch `refactor/h085-r1-resolver-dispositivo`.
- **R5 (H086) — APLICADO.** Cascada Tier 1→2→3→3b→4 colapsada a un motor
  `_barrer(bloque, rango, lineas_dictamen, *, excluye_dictamen, es_candidato,
  permite_fallback)` único + 4 detectores `_cand_*` + 5 llamadas en cascada. NO
  es extracción pura: reescribe la lógica de las 5 capas (el mismo bucle ×5, que
  difería solo en rango / exclusión de dictamen / detector / fallback). Lo común
  (skip de vacías, armado del chunk, validación de firma) pasa de 5 copias a 1.
  Decisión de diseño: `_T2_PATS`/`_T3B_ARG_RE`/`_RE_ASI` subidos a nivel de módulo
  (antes se compilaban en cada una de las ~5862 llamadas); los 12 literales raw
  quedan byte-idénticos (solo se mudan + renombran). La cascada de 5 llamadas en
  orden NO se data-ificó: los rangos dependen de valores de runtime y el orden
  codifica prioridad de dominio (elegante ≠ máximamente comprimido). Equivalencia
  no solo empírica: chunk y firma están anclados a `k` (independientes del
  detector), y la única reescritura real —Tier 2 chequeaba firma per-patrón, ahora
  una vez tras "algún patrón pasó la guarda"— es equivalente porque firma(k) no
  depende del patrón. resolver_dispositivo 223→63 líneas; archivo 3650→3603.
  Validación: PoC de equivalencia original↔parcheado (21 dirigidos + 9
  adversariales + 60k fuzz, todos idénticos; 5644/5644 dispositivos reales
  reconocidos por las closures → 0 bugs de transcripción) → check_regresion
  [CLEAN] (4/4 CSV idénticos al golden). parser v18.06→18.07. B090 (Tier 5)
  entraría como sexta configuración, no como otra copia.
**Pendiente:**
- Extraer es_originaria (212 líneas) y el detector de sumarios.
**Referencias cruzadas:** H084, H085. M12. B090.

### M14 — Manifiesto de procedencia del pipeline (trazabilidad) — IMPLEMENTADO H087

**Componente:** parser / outputs.
**Origen / fuente del diagnóstico:** H085 (propuesta de Guillermo).
**Diagnóstico:** los 4 CSV canónicos no registran con qué versión del parser
fueron generados. No hay trazabilidad de procedencia del dataset.
**Decisión de diseño:** NO agregar columna de versión a los CSV. Motivos:
(a) rompería el golden de M12 y, peor, cada bump de `__version__` dispararía una
[REGRESION] espuria — el harness dejaría de distinguir cambio de lógica de
cambio de etiqueta, que es justo la propiedad que lo hace útil; (b) redundancia
de una string repetida en 175k+ filas; (c) cambiaría el esquema de datasets ya
publicados en Dataverse (doi:10.7910/DVN/TJTVKW). En su lugar, manifiesto
sidecar (`_meta/` o `output/parser/_manifest.json`) con parser_version,
git_commit, fecha, conteos y sha256 de cada CSV. No toca los CSV → golden
intacto → harness [CLEAN]. De paso, los hashes son una segunda red de
integridad.
**Estado del fix:** IMPLEMENTADO H087. Script `scripts/pipeline/generar_manifiesto.py`
v1.0 (standalone, último paso del pipeline; no hook en parser.py). Escribe
`output/parser/_manifest.json` de tres capas: **(A)** `git` commit HEAD + flag
`dirty` —cuando dirty=false fija TODO el código del repo, transitivamente, no solo
los dos generadores—; **(B)** `pipeline_scripts`: `__version__` de los 5 scripts de
la cadena (detectar_paginas, construir_catalogo, cruzar_catalogo_y_mapa, parser,
parser_editorial), leído ESTÁTICAMENTE vía `ast` sin importar el módulo (un PoC
mostró que `import parser` dispara `from parser_editorial import ...` y compila los
regex de módulo: leer la versión no debe depender de que ese grafo importe limpio);
**(C)** `inputs`/`outputs`: sha256 + filas (vía csv.reader, robusto a newlines
embebidos) + bytes de los 3 intermedios (`mapa_paginas.csv`, `catalogo.csv`,
`fallos_localizados.csv`) y los 5 CSV canónicos finales — captura el DATO (cambios de
corpus/intermedios que el commit no distingue). Decisiones de diseño: standalone y
no-hook (cubre el 5º CSV que escribe `parser_editorial.py`, se re-corre sobre
outputs ya publicados sin reparsear, no engrosa la función monstruo); allow-list
explícita en vez de glob (excluye `csjn_casos_BASELINE_H079.csv` y el propio
`_manifest.json`, y falla ruidoso si falta un canónico en vez de manifestar parcial
en silencio); el sha256 es una 2ª red de integridad además del golden, materializada
en el modo `--verify` (re-hashea y compara, exit≠0 si discrepa). No toca ningún CSV →
golden `[CLEAN]` por construcción; parser sin bump (sigue v18.07) — esta sesión corta
la racha de bumps sin procedencia agregando el mecanismo, sin bumpear ella misma.
Validación en máquina real (H087): generar OK; `check_regresion` `[CLEAN]` 4/4;
`--verify` `[CLEAN]` 8/8. Conteos sellados — outputs 5862/27463/140956/151/11445,
inputs 46936/5862/5862. Los 3 intermedios canónicos se confirmaron contra BITACORA
(no se adivinaron): `fallos_localizados.csv` = output de etapa 3 / frontera
arquitectónica; `catalogo.csv` = fuente de `linea_inicio`; `mapa_paginas.csv` =
mapa que consume el parser (`--mapa` confirmado en el log de invocación). **Pendiente
menor (futura sesión):** digest del corpus crudo (`LibroVol*.md`), único eslabón de
la cadena que el manifiesto todavía no fija.
**Referencias cruzadas:** H085, H086. M12.
