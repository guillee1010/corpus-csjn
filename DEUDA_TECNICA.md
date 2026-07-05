# Deuda Técnica

Lista canónica de bugs del pipeline corpus-csjn y de la herramienta auditora
(`scripts/auditoria/auditar_fallo.py`). Una entrada por bug. Las entradas con
referencia §X.Y apuntan a `archivo/docs/PIPELINE_v1.md` (deprecado H062) para
contexto histórico del diagnóstico original; el estado vivo de cada bug está
en este archivo.

**Última actualización:** 2026-07-05 (H181 — **B135 CERRADO COMPLETO ((c) señal compuesta, parser v24.0→24.1) + B139 CERRADO COMPLETO ((b) guard sentencia-sustitutiva, clasificador v1.16→v1.17) + M21 FASE 3 CERRADA (skip RE_PAGE_HEADER en el chunk, parser v25.0) + 2 micro-unidades del gate (v1.16 «condenar al?» · v1.18 B143-ext deja-sin-efecto-todo-lo-actuado)**: is_originaria 589→**596** (+7) · is_merit 2935→**2965** (+30, **0 pérdidas** en toda la sesión — cobro COMPLETO de los costos aceptados del paso 3: 2 originarias B135c + 331_p100 + los 4 truncados M21, más los recuperos que las unidades destaparon) · divergencia 0 sostenida · manifest [CLEAN] 64. Gate de apertura reproducido exacto (2935/2935/0/589 · `--plan` del orquestador con pins · docs post-H179 re-verificados; los subidos primero eran PRE-H179, detectado por header/M42-esbozo). NOTA de numeración: **H180 fue la sesión de housekeeping/docs de otra conversación** (READMEs a v24.0, archivado, correr_pipeline trackeado, micro-item «Dónde está cada cosa» PEGADO al skill — corpus byte-idéntico a H179); esta sesión corre como H181. **UNIDAD A — B135(c) (parser v24.1, MINOR):** señal 6 COMPUESTA en `es_originaria` — case_name demanda-contra-Estado/Provincia (`RE_CN_DEMANDA_ESTADO` ensanchada con la forma invertida «c/ <Nombre>, Provincia de», verificada en Ferrari L191 y Coihue L499; la regex DEJA de ser huérfana) ∧ `_orig_pelada_con_guards` REUSADA INTACTA sobre la ventana RESULTA (`_ventana_resulta`: apertura RE_VISTOS → primer RE_CONSIDERANDO, VERBATIM de poc_b135c v0.1 — mismo código = misma ventana = flip-set medido vale). PoC en disco: A0 identidad réplica==publicada **0 diffs / 5890** · pool case_name-compuesto **326** → la corroboración deja pasar **6** (la precisión que el case_name-solo ≈11% no tenía) · flip-set **6 = 6 TP** adjudicados por lectura caso a caso (329_p3168 López Casanegra · 329_p3403 Ferrari · 340_p1025 Fotógrafos Iguazú · 342_p917 Barrick · 344_p3476 Coihue · 348_p1686 Equística — los 6 con declaración de competencia EN EL PROPIO EXPEDIENTE) · 0 FP · FP-F5 de H172 intactos. **Ruta D (dispositivo) evaluada y DESCARTADA-FUNDADA:** su testigo único 348_p473 resultó **fila FANTASMA** — rango [18027,18040] ⊂ 348_p461 (Estado Nacional c/ La Rioja, [17575,18046], orig=1/merit=1 ya sanos bajo su id); la fila lleva el nombre de catálogo de Hotesur con texto ajeno; gap 18047–18076 = candidato al Hotesur real → constancia en **B045**. **CORRECCIÓN de constancia H178: los «3 costos autorreparables B135c» eran 2 reales + 1 espurio (473).** Micro-unidad **v1.16** (destapada por la adjudicación): «Condenar AL Estado Nacional» — la contracción «al» rompe la frontera de `\bcondenar\s+a\b` en `RE_FONDO_EXTRA_GRANT` → ensanche `al?`; poc_condenar_al v0.1 sobre el universo COMPLETO donde corre es_de_fondo (595): flip-set **1 = el testigo Equística**, 0 pérdidas, 0 FP-costas; «condenar al» fuera del universo originaria: 5 (efecto 0 hoy — superficie dimensionada). Ciclo A EMPAQUETADO (v24.1+v1.16, un solo re-golden, patrón H178): diff adjudicado contra contrato + TOTALIDAD por columnas — casos EXACTAMENTE 6 filas {is_originaria, is_merit_decision ×6, tribunal_origen_status→originaria; Coihue corrige un `apelado_detectado` FALSO, contraejemplo documentado del flag como componente de «ausencia de a-quo»} · votos 28 filas confinadas; **tipo_voto: 2 D-por-fallback NUEVOS en Barrick 342_p917 (Rosenkrantz + Highton, indeterminado→D)** = clase B137, van al audit · orig 595 · merit 2941 · div 0. **UNIDAD B — B139(b) (clasificador v1.17):** población RE-MEDIDA EN SCRIPT sobre el sello v24.1 (`poblacion_b139b` v0.1: no_revision_demanda 181 · art16 7/2-orig · via=REX 14/5-orig · **9 apeladas == flip-set H176 reconciliado**); **8 lecturas adjudicadas caso a caso (criterio confirmado por Guillermo)** → 6 TP: 331_p100 (testigo H170 — cierra su costo del paso 3), 337_p1174 (Rodríguez c/ Google, sustitutiva nítida), 343_p1259 (FADEEAC, **TP-con-asterisco**: único REX desestimado + art. 16, la Corte dispone igual sobre la demanda — criterio del usuario), 344_p277, 348_p895 (Defensor del Pueblo, con exhorto al Congreso), 332_p2559 (sustitutiva SIN cita del art. 16 → motiva S2); 3 aciertos que NO se tocan: 330_p3160 (Bussi, inoficioso/mootness), 331_p530 (Cóspito, acceso 280+116/117), 332_p2237 (incidental, «continúe el trámite»). **Guard v1.17 en dirección INVERSA (fuerza `si`), patrón B119/B143 con verbo intacto:** `disp==no_revision_demanda` ∧ (**S1** art. 16 ∧ ley 48 en el pe — NO la columna via, FP conocidos 330_p826/331_p1262 — ∨ **S2** concesión-de-recurso ∧ «rechaza la demanda» en el MISMO pe); ¬originaria POR CONSTRUCCIÓN (la rama originaria retorna antes). poc_b139b_guard v0.1: A0 round-trip gate==publicado 0 diffs/181 · flip-set corpus-wide **EXACTAMENTE 6, 0 extras, 0 pérdidas** · S1 y S2 ambas NECESARIAS (1174/1259 solo-S1; 2559 solo-S2). Ciclo B: casos 6 filas SOLO is_merit_decision · votos 28 filas SOLO is_merit_decision · **tipo_voto 0 flips** · único downstream movido: recursos.csv (materia/partes/epilogo hashes idénticos = 0 ripple oculto) · **`disposicion` de los 6 QUEDA no_revision_demanda** (el guard vive en el gate, no en disposicion(); la tensión sustitutiva-vs-eje-dispositivo y su efecto en `parte_ganadora` quedan anotados en la entrada B139) · merit **2947** == gate=si · div 0 · golden casos 0a9cb3019966 / votos 2001e3173935 · manifest [CLEAN] 64. **UNIDAD C — M21 FASE 3 (parser v25.0, MAJOR):** skip de `RE_PAGE_HEADER` (línea-sola: frase pelada o \d{2,6}) dentro del chunk de `_barrer` SIN contar presupuesto — simétrico al skip de vacías de F1; cierra la clase banner-partido-en-N-líneas que la terna-substring de F2 no cubre; detector reusado, 0 regex nueva. FUERA DE ALCANCE declarado y verificado quieto: 330_p563. Medición = ciclo `--consciente` (un cambio de `_barrer` no admite PoC read-only; camino H126), adjudicado por `dump_diff_h181c` v0.1 — 52 casos con flip de decisión leídos UNO A UNO: **pe cambiados 547** · **outcome 23** (6 otro→competencia + 5 otro→real + ~10 real→real, todos coherentes con el pe destapado) · **merit +18 TP** (los 4 truncados del paso 3 ✓ + 14 extras nítidos) · **orig +1 TP** (343_p726, art. 117 en el pe; mérito quieto vía RE_DISP_COMPETENCIA, correcto) · quejas ~15 recuperos · **totalidad estructural: considerando 1 / firma_raw 1 = SOLO 332_p663 → testigo B126 SANADO** (panel 4→6, +2 votos, pick al performativo real; revierte la exposición de H130; el frente corpus-wide de B126 sigue abierto). **FP EVITADO ANTES DEL GOLDEN (lógica de orden (a) de H177, segunda aplicación): 348_p1352 Pereyra** — el pe completo destapó «deja sin efecto TODO LO ACTUADO» = nulidad de actuaciones bajo `disp=grant_remand_implicito` (verificado en disco: el remand lo metía en _FONDO), fuera del ancla disp==nulidad de v1.15 → **micro-unidad v1.18** (guard espejo B143, anclas {grant_remand_implicito, deja_sin_efecto} ∧ RE_DSE_ACTUADO ∧ ¬RE_ABSOLUCION; superficie corpus-wide sobre norm(pe) = EXACTAMENTE 1 = el testigo — la medición cerró la adjudicación; bimodal verde). **FP NUEVO del eje legacy → ticket B144:** 330_p1525 outcome otro→caducidad por match DENTRO de un apercibimiento; no toca mérito (gate=no correcto). Ciclo C: UN regolden (25.0+1.18), sello **orig 596 · merit 2965 · div 0** · [CLEAN] 64. **Lecciones ops H181:** (1) **regex con no-ASCII NO viajan confiables por `python -c` en PowerShell** — el conteo por consola OMITIÓ al testigo 331_p100 (match=True demostrado en disco con hex-dump; art.\xa016 con NBSP era inocente); los conteos que deciden van en SCRIPT (patrón `poblacion_b139b`); (2) el docstring de `extraer_caso.py` ejemplifica `diagnostico/_extraidos/` — el schema vigente es `scripts/diagnostico/HNN/`; corregir el ejemplo en el próximo bump de la herramienta; (3) **las mediciones sobre el pe van sobre `norm(pe)`, nunca sobre el crudo** — el guión de corte del OCR («efec- to») derrota cualquier regex sobre crudo (la superficie de v1.18 dio 0 hasta normalizar): lo que el gate ve es lo que se mide; (4) para adjudicar un diff ancho de `_barrer`, el patrón `dump_diff_h181c` (una fila por caso con flip de decisión + pe viejo-cola/nuevo) rinde: 52 casos leídos en una pasada. Decisión git: `git add -f` de los 5 verificadores de H181 (poc_b135c + poc_condenar_al + poc_b139b_guard + poblacion_b139b + dump_diff_h181c — evidencia de adjudicación, patrón H177/H178). Clave blind: build_m20 re-corrido al cierre (resultado en BITACORA; si cambió, misma desviación-consciente H178 — M43 es el sucesor). PENDIENTE H182: **M43** (re-κ ciego del eje unificado **2965**, pre-Dataverse v2 + nota semántica is_merit en CODEBOOK — SIGUIENTE unidad natural: el eje quedó quieto tras cobrar todos los costos conocidos) · audit **B137** (universo 2965; dato: +2 D-por-fallback de Barrick en el ciclo A, 0 en B y C) · **B144** (guard de apercibimiento en la cascada de outcome, testigo 330_p1525) · **B126** (scan corpus-wide de firmas partidas; el testigo 332_p663 quedó sano vía F3) · B142 · D3/M40 (dedup RE_NULIDAD_*) · B117 F1 · Hotesur real (gap 18047-18076, B045).)

**Anterior:** 2026-07-05 (H179 — **M42 EJECUTADA Y CERRADA: `correr_pipeline.py` v1.0 (scripts/pipeline/) — orquestador de la cadena canónica con el DAG de MAPA.md como spec; validado reproduciendo el sello H178 en 0 CAMBIOS**. Gate de apertura reproducido exacto (is_merit 2935 == gate=si · divergencia 0 · orig 589 · manifest [CLEAN] 64 · versiones 24.0/1.15/0.6 verificadas en disco). Diseño adjudicado: alcance v1 parser→extraer_epilogos→derivar_partes→derivar_materia→derivar_recursos→check_regresion(gate)→manifest (el esbozo H174 omitía epilogos/partes; MAPA manda) · upstream catálogo/mapa/cruce FUERA del ejecutable (CLIs no leídas, zonas ⚠ en MAPA; **v2 cuando haya tomos nuevos reales**) · `--sin-parser` ELIMINADO (redundante con `--solo-derivers`) · `--consciente`/`--regolden` en DOS pasos (freno humano tras el diff; nada irreversible sin adjudicación). Invariantes H178 cableados: (a) fail-fast total por returncode; (b) pre-flight de versiones de los 10 módulos + pin `--esperar` + frescura post-etapa por mtime (mata la clase H178-1 «corrió pero no era»); (c) assert golden==producción por sha256 de los 5 CSV del parser en TODA corrida (el freno del PoC POST, permanente — H178-2 imposible por construcción); (d) cero paths adivinados (constantes REPO_ROOT patrón generar_manifiesto, existencia verificada pre-invocación). NUEVO no-previsto-en-esbozo: gate de **CORPUS-DRIFT** en pre-flight (corpus/*.md vs universo source_file de casos.csv, misma derivación que fuentes_corpus del manifiesto — que NO detecta esta clase: sella solo lo referenciado); en su primer contacto con el disco detectó los 4 .md de 335/336 (exclusión deliberada conocida; `--ignorar-corpus-drift` la declara). Invocaciones cableadas VERBATIM de las CLIs leídas en sesión (no uniformes a propósito: `--out` en recursos, `--input` en materia). Validación: smoke sandbox 7 tests → `--plan` adjudicado contra MAPA.md ANTES de la corrida real (regla dura H175–H179) → corrida completa → check [CLEAN] 5/5 → hashes golden==prod idénticos (dc3830dcef82 / 05ddd9acafd4 / 8e320b59aea1 / 98ce265d9854 / 30a6da652e3a) → manifest [CLEAN] 64 SIN re-sello. DECISIÓN de provenance: correr_pipeline.py NO entra a PIPELINE_SCRIPTS del manifest (no moldea datos — mismo estatus que check_regresion; el manifest sella lógica que produce bytes, no infra de ejecución) → manifest INTACTO. Infra: PYTHONUTF8=1 en el env de cada subprocess (clase charmap H174 cubierta para toda la cadena sin tocar los hijos) + errors=replace en stdout propio. MAPA.md gana la sección «Cómo correr la cadena» (el mapa era la spec; el orquestador es su implementación). Micro-item «Dónde está cada cosa»: TERCERA verificación NO-pegada (H177/H178/H179), decisión pega-o-abandona DIFERIDA por Guillermo — resolver en H180 o abandonar con constancia. PENDIENTE H180: **M43** (re-κ ciego del eje unificado — pre-Dataverse) · B139b (8 lecturas) · B135(c) · M21 F3 · audit B137 (desbloqueado) · B142 · dedup RE_NULIDAD_* (D3/M40) · nota semántica is_merit en CODEBOOK (v2 Dataverse).)


*Histórico de sesiones (H157 y anteriores, hasta H097): ver BITACORA.md. Esta línea registra solo la última sesión — reemplazar, no encadenar.*

> El detalle cronológico por sesión vive en `BITACORA.md` / `CHANGELOG.md`; este encabezado registra solo la sesión vigente. El estado ABIERTO de un vistazo está en el **Tablero de estado** (abajo). El cuerpo conserva las cerradas como referencia (se reabren: B045, familia B009, is_originaria/B010, etc.).

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

## Tablero de estado (radar activo)

Vista compacta de lo ABIERTO / en radar. El cuerpo de abajo es el ledger completo (incluye
las cerradas como referencia). La entrada completa de cada ítem está más abajo por su ID.

**Parser (abierto):**

| ID | Qué | Estado |
|----|-----|--------|
| B104 | running-heads mid-considerando rompen regex cross-token | abierto |
| B105 | `por_ello` capturado de considerando/feria/oficio en vez del dispositivo | abierto |
| B106 | `case_name_cuerpo` vacío teniendo «Vistos los autos:» presente | abierto |
| B110 | `es_queja` capa-fuente (carátula hecha; tail débil + considerando abiertos) | parcial (H107) |
| B111 | `tipo_cuestion_federal` sobre-usa `mixto` / pierde `arbitrariedad` | abierto; diagnosticado H134 (señal distribuida 3 zonas; seed dos-zonas recall 84% / prec ~80%; codebook art.14; campo pide weak-supervision) |
| B119 | `is_merit` sobre-incluye NO-fondo (capa disposición) | CERRADO H121: gate 0,907→0,953; FP 19→5; capa disposición pre-cascada (competencia/cautelar/nulidad_concesion/inoficioso) + #1 originaria + #2 des-hifenado. **κ in-sample recomputado limpio H140: 0,813 (pre-B119) vs 0,933 (post)** |
| B136 | `is_merit` excluye originaria DE FONDO (premisa SCDB falsa: SCDB la INCLUYE) | **CERRADO H169** — la premisa H165 (guard #1, 1 palanca) era FALSA: el eje vive en 2 capas (parser `is_merit` + deriver `es_revision_fondo`) y la originaria usa verbos hacer_lugar/rechazar, no confirma/revoca. Fix = detector `es_de_fondo` en `clasificador_disposicion.py` v1.10, importado por parser (v23.0) + usado por `es_revision_fondo` (v0.6) → ejes consistentes. **133 de-fondo** (89 grant + 44 reject); `is_merit` 2870→3003, `es_revision_fondo` 2816→2949; 0 no-orig tocadas; `[CLEAN]`; commit `10f2c5c`. Cascade tipo_voto → 13 votos (→ **B137**). Pendiente: κ ciego → Dataverse |
| B137 | `clasificar_tipo_voto` marca D-por-fallback (`is_merit AND wc>=2500`) cuando los matchers A/B/C/E fallan el fraseo | **NUEVO H169** — confirmado_caso_testigo: error SILENCIOSO corpus-wide (2870 apelados + 133 orig). B136 lo destapó en 13 votos de fondo-originarias (`indeterminado→D`). 2 dudosos: 333_p1088 Argibay («coincide con los resultandos de la disidencia»), 343_p1944 Rosenkrantz («al que cabe remitir»). Audit REPROGRAMADO (H170 se dedicó a la auditoría REE/D1 → M39; el universo del audit ahora depende del fix de M39 porque `is_merit` define la superficie del fallback). **H178: audit DESBLOQUEADO — paso 3 cerrado, universo del fallback definido (is_merit unificado = 2935); dato de referencia: los flips D-por-fallback del paso 3 fueron 6 reales sobre cota 15+2** |
| B117 | zona `epilogo` absorbe la cola del considerando (testigo 329_p595) | abierto, generalidad sin verificar |
| B118 | `por_ello`/dispositivo truncado por running-head de página (pierde el verbo de fondo) | CERRADO H126: subsumido por el skip de `_barrer` (M21 Fase 1, parser v19.0) |
| B124 | `_barrer` ancla el PRIMER "Por ello" (argumental) en vez del dispositivo de fondo | CERRADO H130: regla P (`RE_PERF v2`, primer performativo-con-firma), parser v20.0; +121 recup / 0 regresiones a otro / `scan_concurrencia` 0 |
| B126 | extractor de firma dropea nombres partidos por salto de línea del OCR (testigo 332_p663 Salas) | abierto — **testigo SANADO colateralmente H181** (M21 F3 movió el pick de 332_p663 al performativo real → panel 4→6, +2 votos; revierte la exposición de H130); el frente corpus-wide (scan de firmas partidas) sigue pendiente |
| B129 | falso inoficioso: `result\w+ inoficioso` (dictamen PGN) marca revocación como `abstracto`/`is_merit=0` (testigo 334_p1272) | **CERRADO H145** — lookahead `(?![^.]{0,40}(?:dictamin\|procurador))` en el guard `RE_DISP_INOFICIOSO` de `es_revision_fondo` (clasificador_disposicion v1.08); absorbido por el rewiring M26; corpus 24 asides conservados / 22 mootness fuera; gate 0,946 |
| B131 | `nulidad del auto de concesión` puede clasificarse como fondo (OBJ de `clasificador_disposicion` incluye `auto`) | **CERRADO H143** (commit `a890d92`): pre-cascada `RE_NULIDAD_CONCESION` (VERBATIM del parser L470, B119) en `clasificador_disposicion` v1.06→v1.07; 31 casos → `nulidad_concesion`, 30 salen de fondo (2892→2862); gold n300: 4/4 tocados `es_revision_fondo=no` → 0 regresión; κ-gate del de-interleave latente +0,019 (0,887→0,906). `parte_ganadora` de los 30: `recurrente_gana`→`no_aplica` (correcto). Detector reusado, no reinventado |
| B133 | `clasificador_admision` sub-marcaba la mootness: de 148 `abstracto` solo 5 eran `inadmite`; los ~96 puros (disp=no_fondo) caían a `sin_marcador`/`admite` | **CERRADO H148** — `outcome=="abstracto" ∧ disposicion∉fondo → inadmite` (clasificador_admision v0.1→v0.2), insertado tras la originaria (originaria-mootness quedan `no_aplica`); aditivo verificado en disco: 87 `sin_marcador→inadmite`, todos abstracto, 0 colaterales; `inadmite` 1020→1107. Acoplado al re-cableo de causa (mismo pass del deriver). Habilita CUESTION_ABSTRACTA vía detector textual sobre el gate corregido |
| B134 | originarias con `outcome=desestima` leak a `inadmite`: el gate REX (paso 2) precede a `is_originaria→no_aplica` (paso 4) en clasificador_admision | **NUEVO H149** — confirmado_cuantificado (13 en inadmite, 11 en cajón SIN_CAUSAL; queja vacío, es_queja=0, outcome=desestima → entran por gate REX). Doctrinal: originaria (art.117) sin gate de admisibilidad → debe ser `no_aplica`. Fix: validar is_originaria (9 limpios + 2 contradictorios via=REX: 331_p1432/348_p439), luego reordenar precedencia; NO flipear a ciegas. Conecta M27 + cajón SIN_CAUSAL |
| B144 | cascada de outcome matchea DENTRO de un apercibimiento («bajo apercibimiento de declarar la caducidad» → outcome=caducidad; lo dispuesto es un diferimiento) | **NUEVO H181** — confirmado_caso_testigo (330_p1525, destapado por M21 F3); eje legacy, NO toca mérito (gate=no correcto, verificado); guard de apercibimiento pendiente |
| B138 | `RE_RECHAZA_REC` sobre-dispara en denegatoria de acceso pura (queja/recurso de hecho) → `es_revision_fondo=si` + `recurrente_pierde` espurios | **CERRADO H175** — guard lista-POSITIVA en `es_revision_fondo` (v1.12): 11 FP corregidos (9 quejas + hecho + reposición); ordinarios y REX quedan si; 4 FP residuales documentados; Minaglia 330_p3801 = fondo real (→B142) |
| B139 | FN de `disposicion()`: verbo de fondo con objeto MATERIAL («confirmar el reajuste») + «rechaza la demanda» en sede recursiva (art. 16 in fine ley 48) | **RE-ESTRATIFICADO Y DIFERIDO H176** — 59 brutos re-corridos post-B141/B138/B140b; 17 lecturas adjudicadas; FN reales del gate = 10 (5 mecanismos), documentados-sin-guard (heterogeneidad probada por lectura; guard tocaría `disposicion()` lockeada). Superficie es_de_fondo (1927) CERRADA vía v1.14 (+«impugnación», gemelo 2478). Sub-causa (b) diferida con diseño (señal art.16 textual ∧ ¬originaria; 8 lecturas pendientes). **(b) CERRADO H181** — guard v1.17 sentencia-sustitutiva (S1 art16∧ley48 ∨ S2 concesión∧rechaza-demanda), 8 lecturas adjudicadas → flip-set corpus-wide 6=6TP/0 extras/0 pérdidas; is_merit +6 (2941→2947). **B139 COMPLETO** (a: 10 FN documentados-sin-guard · b: cerrado) |
| B140 | FP del gate: revoca-FORMAL en abstracto (doctrina «sin perjuicio de revocar…no importa abrir juicio») + nulidad-de-concesión fuera de la ventana del guard B131 | **(b) CERRADO H175** — ensanche `RE_NULIDAD_CONCESION` (v1.13): 10 flips de verbo nulidad→nulidad_concesion, ripple adjudicado (parte, gate, admisibilidad). **(a) resuelto-sin-guard**: cardinalidad 1 (ADC), documentado como FP conocido |

**Catálogo / cruzador (abierto):**

| ID | Qué | Estado |
|----|-----|--------|
| B009 | `pagina_no_en_mapa` 331-334 (Fase 2) | en validación |
| B011 | bug catalográfico `344_p344` (caso aislado) | abierto |
| B045 | frontera catalográfica mal puesta entre casos consecutivos | abierto |
| B012 | localización con `linea_fin` extendido sobre el próximo caso | abierto |

**Frentes / features / infra:**

| ID | Qué | Estado |
|----|-----|--------|
| Frente B — materia | capas 1-2-3 HECHAS (v3.2); held-out capa 2 (H116) + GOLD H117 (era **codificación IA**, menos casos) — exactitud\|emite 81,3% (capa1 82,5% / capa2 66,1%); CA silver 68,8% confirmado; finas medidas: salud/previsional/penal altas, **constitucional 0/0**, consumo 33% precisión. **GOLD HUMANO n=300 codificado en H119** (label dominante a mano) → es el gold de referencia; validar `derivar_materia` contra este | medido; refinamientos pendientes |
| csjn_casos_textos | separar texto pesado (desbloquea materia capa 2) | pendiente, PRIORITARIO |
| M20 | refactor `outcome`→disposición+parte (molde SCDB, unidad parte×recurso) | **VALIDADO H120** (n=300 completo): disposición 0,857 (confirma tesis), reenvía 0,773 (cruce valida codebook: deja_sin_efecto reenvía 71% vs revoca 44%), parte_ganadora 0,788, **certiorari criollo queja 95% vs concedido 68%**. Falta: `derivar_recursos.py` + re-golden + merge. **NUEVO campo:** vía ordinario/extraordinario (interactúa con dictamen). **H165:** el golden se armó sobre el universo que EXCLUYE originaria-de-fondo (guard #1 de B119, premisa SCDB falsa → **B136**); ampliar `is_merit` a las 167 originarias-de-fondo (153 con Estado) obliga a re-codificar partyWinning para ellas + re-κ |
| capa dictamen | `derivar_dictamen.py` (uso del dictamen PGN: remite/conformidad/oido/sin_dictamen) | gold ciego construido (H119); deriver no diseñado. **Caveat de alcance:** generaliza solo al vértice publicado (censura ~90%). Lectura teórica (Schelling inverso, sala de admisibilidad) → BITACORA/campo, no pipeline |
| M19 | kappa / doble codificación + sección reliability del CODEBOOK | titular n=300 hecho; **κ(parser↔gold) cerrado H139** (5 vars, IC bootstrap, `kappa_confiabilidad.py` v1.0); **gate limpio H140 (0,813 [0,741–0,873] held-out de facto, vs 0,933 in-sample)**; doble-codificación + sección CODEBOOK + muestra fresca gate (M20-b) pendientes |
| M25 | `parte_ganadora`: detector real del texto (hoy derivada de disposición, techo 0,889) | diseñado H140; banco 15 casos (8 parcial + 7 inversiones de rol). **Gold listo H151** (`parcial`→binario SCDB, bycatch blanqueado, `planilla_M20_57GOLD_parte_limpia.xlsx`, 134 fondo / 110 gana / 24 pierde); κ recomputado **H151: 0,784** [.632–.908] (n=134, acuerdo 0,933, sustancial; sube de 0,653 por el colapso de parcial; techo = 7 inversiones de rol). **Output binarizado H153** (`clasificador_disposicion` v1.09, `modifica→gana`, `parcial` fuera del OUTPUT, `recursos.csv` {2335/537/3018}, κ 0,784 sin cambio). **DESBLOQUEADO H156** — M29 ya deriva `recurrente_rol` (el insumo que pedía la entrada de M25); el detector de las 7 inversiones de rol puede construirse. MATIZ: rol poblado solo en ~1276/3749 (penal 466 / demandada 369 / actora 343 / etc; sin_rol 2473) → refina partyWinning donde hay rol, medir cuántas inversiones caen en cobertura antes de prometer el salto de κ. Detector de texto pendiente. **H157:** validado gate A (eyeball) + fix de rol masculino (v0.6) → **rol procesal usable sobre mérito 32,1%→38,0% (+169)**; las 7 inversiones del gold tienen partes nombradas (no caen en los defectos del eyeball) → el detector puede construirse ya. Insumo: `csjn_casos_partes.csv` v0.6 + `recursos.csv` (parte_ganadora) + gold `planilla_M20_57GOLD_parte_limpia.xlsx`. **H158 — DESCARTADO y LOCKEADO:** probadas las dos rutas determinísticas (cruce rol; marcador de disposición), ambas over-firean; la señal de inversión es de mérito, no patrón → detector inviable. Sin cambios canónicos. No reabrir sin evidencia nueva. |
| M26 | refactor admisión/mérito: de-interleave de `outcome` en dos canales canónicos (`admision` + `disposicion` multiclass + eje coarse fondo/procedimiento/originaria) | **DISEÑADO H141 + Fase 1 A/B CERRADA H142** (175/153 reproducido en disco; doctrina admisión/mérito LOCKED; canal admisión = `queja_resultado`+`procedente`/`admisible`; perillas grant_remand/originaria con sensibilidad +16/+22/+32); Fase 2 = cirugía parser [próxima]; reabre κ + republica Dataverse; handoff `PROMPT_H143_cirugia_parser.md`. **Paso 3 (H147) scopeado:** `outcome`→legacy congelada; gate swap; detectores caducidad 13/13 + desistimiento 10/10; abstracto=admisibilidad (no relocaliza); causa al deriver. **Paso 3 (H148) IMPLEMENTADO + CERRADO:** `clasificador_causa.py` NUEVO (gate=inadmite); parser v22.0 sin columna causa; B133 cerrado; detectores caducidad 13/13 + desistimiento 10/10 + abstracta (guard disposicion∉fondo); A/B 134 deltas; invariante causa⟺inadmite (1107); manifest 64. **Pendiente paso 4:** re-golden full + recomputar todos los κ + camelCase + republicar Dataverse. **Paso 4 (H149) PARCIAL:** κ v22.0 recomputado (in-sample, sellado); `admisibilidad`=SÍNTESIS (sin κ independiente, confiabilidad compositiva); κ-causa diferido; **camelCase DESCARTADO**; cadena sin cambios (manifest 64). Sigue → M27 (PROMPT_H150) |
| M27 | vocabulario canónico de `causa_inadmisibilidad` sobre el tratado de la Secretaría de Jurisprudencia (`documento__37_.md`) | **ABIERTO H147** — mapeo verificado (8 causas ✓; 5 gaps: interposición incorrecta / tribunal superior de la causa / relación directa / CF oportuna / salto de instancia); ~95/429 del cajón SIN_CAUSAL recuperables; valida polisemia caducidad (§2.6.1/§2.6.2); un detector por causal con disciplina holding-vs-antecedente, commit separado. **Próximo H150 (idea Guillermo):** parsear el tratado como 2do corpus → `causal → [casos_id] → fraseo` = gold EXTERNO case-level (supervisión a distancia, las citas de la Secretaría son las etiquetas); handoff PROMPT_H150 |
| M35 | `csjn_editorial_indice_partes.csv` = output **FÓSIL** (productor muerto H061; manifest L115 mal atribuido a `parser_editorial`) — demover | **APLICADO H167 (①②③ de 4)** — ① fuera del set canónico: `generar_manifiesto.py` v1.7→v1.8, `OUTPUTS` 10→9, `--verify [CLEAN] 64`, `check_regresion [CLEAN]` 5890; ② preservado **trackeado** en `archivo/fosiles/` (insumo B115/M32); ③ redundancia **reproducida en disco** (crosscheck EXTRA-vs-`catalogo` v.H167): 478/478 EXTRA + **358/358 SOSPECHOSOS** en catalogo con `nombres_indice`, 0 fuera. Productor-muerto confirmado (grep: único writer `H061/crosscheck`). **④ PENDIENTE H168:** de-publicar de Dataverse (doi:10.7910/DVN/TJTVKW) + subir manifest v1.8 — a mano, irreversible; publicado quedó atrás (10 outputs). Registro: el commit no fue `git mv` (fósil untracked, ya relocado de antes 23/5); `scripts/auditoria/` gitignored → crosscheck one-shot, no commiteado |
| M35-④ | de-publicar el fósil de Dataverse + subir `_manifest.json` v1.8 (publicado sella 10 outputs, repo 9) | **ABIERTO H167 — BUNDLE con B136 (decisión H167).** NO publicar M35 solo: sería una versión MAYOR cosmética que B136 supersede de inmediato (B136 cambia `is_merit` → re-golden + re-κ → también republica). Dataverse **espera a B136** y se publica UNA vez con M35+B136. Checklist M35 (a aplicar en esa publicación): draft → borrar `csjn_editorial_indice_partes.csv` → manifest v1.8 → version note → publish mayor. La v.actual con el fósil queda inmutable = red de recupero |
| M36 | harness de regresión cubre solo los 5 CSV del parser; los derivers **SIN golden** | **NUEVO H166** — confirmado. **Actualizado H167:** tras M35 son **4** derivers sin red (partes/materia/recursos/epilogo); el `indice` fósil salió del set canónico. Extender golden a los 4 derivers o englobar en M24 |
| M29 | capa de partes (petitioner/respondent): recurrente/recurrido + rol del epílogo editorial | **capa 1 (epílogo) CERRADA H154** — `extraer_epilogos.py` v0.2 + `derivar_partes.py` v0.2. **PASO 4 (carátula) CERRADO H156** — `derivar_partes.py` v0.5: fallback desde `case_name_cuerpo` cuando falla el epílogo, aditivo puro, 0 regresión (diff 169 filas). **recurrente_ok 3641→3749** (+108 nombre vía carátula) + `caratula_rol_sin_nombre` 61; **cobertura mérito 88,4%→90,5%** (91,8% nombre-o-rol). Manifest [CLEAN] 65. Hallazgo: DOS ejes — Eje B recurrente/recurrido (=petitioner) ≠ Eje A actor/demandado. **Pendiente: validar 91,8% (eyeball) + capa-cuerpo tail (~235 mérito, carátula plana, ver B-tail) + frente 3 arrastre de zona (~103)**. Desbloquea M25 (rol disponible). **H157:** eyeball (gate A, 30 casos) → **parte 96,7% correcto** + 91,8% conteo confirmado real; **fix de rol masculino v0.6** (rol +242, 191 nombres limpiados, 0 regresión). `recurrente_ok 3749→3745`, `caratula_rol_sin_nombre 61→65`. Tail (~235) y frente parse_parte (ticket consolidado) siguen pendientes. **H160 — Capa 2 (parseo) CERRADA + capa CARÁTULA nueva (`derivar_partes` v0.7→v0.11):** frente `parse_parte` CERRADO (ver fila propia: MP `mp_fiscal`/`mp_defensa`, representado, penal, `por_derecho_propio`, fix `Dr.`). **Capa carátula — recuperación de NOMBRE del `rol_sin_nombre`:** `rol_causa` (el token actora/demandada del marcador "deducido por la actora EN LA CAUSA X c/ Y" elige el lado de la causa: actora→X izq, demandada→Y der; sigue Eje B, la causa solo provee el nombre del lado ya señalado) **recupera 66 nombres** (41 actora + 25 demandada, **0 swaps** validados contra el lado de `c/`) + name-match letrado↔carátula normal "X c/ Y" (≥2 tokens apellido+nombre → `por_derecho_propio`, p.ej. Szelagowski/Gil Domínguez, 2) + fallback `solo_letrado`→`derivar_de_caratula` (PASO 4 también cuando el epílogo solo nombra al letrado, preservando el recurrido del traslado). **`NAME_RECOVERED` 43→106, `solo_letrado` 47→9** (los 9 residuales = letrado de parte no nombrada ni en epílogo ni en carátula, sentinel correcto). Capa 0 deshifenización soft-hyphen (3079 epílogos afectados, 420 nombres limpios). Validado vs 10 fallos enteros extraídos (Szelagowski/Gil Domínguez→pdp, Torre/Benegas/Laitán→actora con nombre, Zubiri/Castellucci, 329_p1541→Torres/penal). **H161 — recupero del pie perdido (`extraer_epilogos` v0.3 + `derivar_partes` v0.13, filas propias):** fallback `sin_zona` + fix colisión terminador-Norma → **cobertura mérito `recurrente_ok` 91,9%→92,8% (2637→2664, +27)**; overall 3806→3845. Distribución de fuente (3836 con nombre): epílogo 3690 (`recurso` 2618 + `+traslado` 1072 + `nombre_recurrente` 8) · carátula 125 · carátula_vía_letrado 13. **H162 — handler de INVERSIÓN (`derivar_partes` v0.14, ver fila parse_parte L184):** 146 recurrente + 4 recurrido + 2 correcciones; `recurrente_ok` 3845; sha `f2894294…`. **H163 — cruce NOMBRE-desde-índice (`derivar_partes` v0.15):** `_partes_desde_indice`+`_refinar_nombre_desde_caratula` cruzan `case_name_indice` "X c/ Y" anclado a `c/` para los rol-conocido-sin-nombre → **42 nombres** (eyeball 42/42); `recurrente_ok` 3845→3846 (calidad, no conteo); sha `8b5eb721…` v0.15, `[CLEAN] 65`. **Capa de adjudicación manual v0.16 CONSTRUIDA y REVERTIDA** (override pisa el regex y tapa los fallos; no escala a 60k). **Gold congelado fuera del pipeline:** `partes_gold_nombre.csv` (72: 42 `caratula_c/`/regex-OK + 27 `pipe_editorial` + 3 `cuerpo_caption`/regex-NO); cobertura regex-vs-gold **42/72**. **Pendiente H164:** ¿`csjn_editorial_indice_partes.csv` conserva el `c/` que el índice colapsado perdió? → cruce vs gold (27 `pipe`) + caption del cuerpo (3) → medir, no parchear. |
| post-B010 | recalibrar `is_originaria` / `inadmisible_280` / art. 4 sobre el considerando más preciso | pendiente (ver **B135**, cuantificado; **+3 candidatos FN H174:** 329_p3403, 330_p4526, 338_p699 — Autos y Vistos originarios flaggeados 0; 338_p699 recuperaría el mérito solo con el flip, EXTRA_GRANT ya matchea) |
| B135 | `is_originaria` SUBDETECTA (señal de demanda originaria disponible pero no usada en el gate) | **(a)+(b) CERRADO H172** — cableado a parser v23.1 (mask RE_RUNNING_HEAD antes de _unhyphenate + 5ª señal «competencia originaria» pelada con 4 guards por-match local/apelada/precedente/provincial W=120). Flip-set 43 (PoC poc_b135_flips v0.1→v0.3, anclas A1-A6 [OK]) = 39 TP + 4 FP-F5 aceptados 0,07% (349_p163/347_p2146/347_p2286/334_p1842). is_originaria 546→589; ripple is_merit 3003→3006 (+6/−3, B136). Divergencia M39 234→219, M1-parser=0. Ensanche art.117 RECHAZADO (0TP/1FP). M1 15→14 (337_p901=Duarte FP-CIDH). **(c) señal compuesta PENDIENTE** (case_name+corroboración+ausencia recurso; precisión case_name-solo ≈11% H156). Paso 1 de M39 EJECUTADO. **H178 (paso 3): 3 originarias no capturadas (329_p3403, 344_p3476, 348_p473) quedaron is_merit=0 como costo documentado — (c) las recupera de punto único vía la rama originaria del gate, lo que le sube el ROI**. **(c) CERRADO H181** — señal 6 compuesta (case_name ensanchado-invertida ∧ pelada-con-guards sobre ventana Resulta, parser v24.1); flip-set 6=6TP/0FP; orig 589→595, merit +5 vía gate (+1 Equística vía v1.16). Corrección H178: los «3 autorreparables» eran 2+1 espurio (348_p473 = fila fantasma → B045). **B135 COMPLETO** |
| M32 | clasificador de TIPO SCDB (petitioner/respondent): mapear el NOMBRE del recurrente (M29) a la taxonomía categórica de Spaeth (~200-300 clases: Estado federal / provincial / empresa / particular / imputado / agencia) | **NUEVO H156** — capa nueva, NO fix. M29 da nombre + rol procesal; el TIPO no está en el texto (es conocimiento del mundo) → requiere clasificación inteligente, NO regex. Complicaciones: misma entidad mil grafías (AFIP/DGI), ambigüedad real, cola larga (empresas/personas). Opciones: (1) diccionario+reglas (determinístico, auditable, techo bajo); (2) LLM (cubre cola larga, ROMPE determinismo REE/Dataverse); (3) **híbrido rec.** (80% determinístico + residuo a modelo con revisión, salidas congeladas + κ). Llena el gap "petitioner/respondent prospectivo" del CODEBOOK §10. Va DESPUÉS de M25. Antes: verificar la lista exacta de códigos del codebook de Spaeth para fijar el crosswalk. **NOTA H157 (vínculo con `materia` v3.2):** M32 y `materia` son el MISMO tipo de problema (clasificación semántica, no extracción de patrón → híbrido determinístico+clasificador, gold nuevo, validación REE con discusión del no-determinismo) — conviene encararlos con el mismo molde arquitectónico. **Decisión de taxonomía PENDIENTE (M32):** ¿adoptar la taxonomía de Spaeth tal cual (crosswalk 1:1, comparabilidad directa con SCDB) o una adaptada al sistema argentino (Estado nacional/provincial/municipal / ente autárquico / empresa / particular / imputado…; más fiel, rompe comparabilidad)? Misma tensión comparable-vs-fiel que el camelCase descartado. No resolver hasta llegar a M32. **NOTA H159 (flag adyacente `parte_anonimizada`):** en casos de menores la parte va anonimizada a iniciales punteadas ("E. G. P. B.", "M. V. C.", "K. A. M."). Detectable por patrón (nombre = puras iniciales punteadas) → flag derivado barato: un anonimizado es SIEMPRE `particular` para M32 (no entidad-tipo) y NUNCA hay que intentar entity-linking entre casos. Además marca la clase familia/menores. Aditivo, capa de partes. |
| parse_parte — frente consolidado | `parse_parte` tira partes recuperables en 3 patrones afines: (a) "la defensa de X", (b) "apoderado/a de X" / "a favor de X" / "en ejercicio de la defensa de X", (c) Ministerio Público (Fiscal/Defensor/Procurador/Asesor Gral. = funcionario-parte) | **NUEVO H156 / RE-MEDIDO H157 (magnitud 6×).** El ticket original estimaba "~4 carátulas" (Careaga/Ibañez/Berraz/Benítez) — el conteo en disco da **24** "la defensa de X" en `recurrente` (tomos 329-347), no 4. Frente (c)/(b) descubierto vía los `solo_letrado` (idea Guillermo: ¿abogado apelando honorarios?): de **47 solo_letrado (31 mérito)**, honorarios per se es raro (1/47 dice "honorario", ~2 "causa propia"), pero el desglose en disco da **~23 Ministerio Público** (funcionario = parte institucional; debería ser nombre + rol `penal`/MP, hoy sentinel) + **~9-12 parte nombrada recuperable** (`apoderado de X`/`a favor de X` literal en el clause, se tira) + ~13 letrado genuinamente pelado (acá sentinel correcto). **(a) y (b)/(c) son el MISMO patrón sin resolver** → una sola extensión a `parse_parte` (`la defensa de | apoderado/a de | a favor de | en ejercicio de la defensa de → parte X`; MP → nombre + `penal`) liquida ambos. **Frente consolidado ~30-40 casos** (~24 carátulas + ~9-23 solo_letrado), no "~4". **Consecuencia en cobertura:** los 31 solo_letrado de mérito se cuentan hoy dentro del 91,8% nombre-o-rol porque `recurrente_rol="solo_letrado"`≠vacío, pero es sentinel, no rol procesal usable → cobertura estricta **nombre-o-rol-real = 90,7%** (2604/2870), y parte del gap es recuperable (miss de extracción, no ausencia). **Decisión de taxonomía PENDIENTE (no es regex):** rol del MP — ¿`penal` o un rol propio `ministerio_publico`/`fiscal`? Conecta con M25 (inversiones) y M32 (tipo SCDB del petitioner) → no apurar. TOCA función compartida con el epílogo (los 3749) → su propia verificación de no-regresión. Scope a fijar con la data del eyeball (A) junta (decisión H157: eyeball primero). Bajo ROI individual, pero consolidado y con decisión de schema embebida. **ACTUALIZACIÓN H157 (post-eyeball):** el eyeball destapó que el frente MÁS grande no era ninguno de (a)/(b)/(c) sino el **rol masculino** (`RE_ROL`/`RE_CARATULA_SOLO_ROL`/`RE_CORTE` feminine-only, 227 casos) → **CERRADO H157** (`derivar_partes.py` v0.6, alternancia masc + `_ROL_CANON`, 0 regresión, +169 rol usable mérito; cierra de paso 13 falsos-positivos penal). **SIGUE ABIERTO el resto del frente:** (a) la-defensa-de [24] · (b)/(c) apoderado-de/a-favor-de/MP [~30] · + **NUEVOS de H157:** **RE_REPDE over-fire en "por sí y en representación de"** (`343_p1758`, ÚNICA misatribución de los 30 — devuelve al representado, tira al que recurre por sí; fix: si hay "por sí", el principal es quien recurre por sí) · **"(" colgado en `RE_MARK_NOMBRE`** (formato viejo, ~8: `329_p1514`/`329_p6002`) · **over-capture de recurrido en `RE_MARK_TRA`** (`348_p1334`: el traslado se come la línea "Recurso de queja interpuesto por…" siguiente; terminador débil) · **rol penal no detectado en "defensor oficial de X"** del nombre_recurrente/carátula (`330_p4476`/`330_p487`). Todos tocan `parse_parte`/regex compartidas → una sola no-regresión sobre los 3745. **PARCIAL CERRADO H159 (`derivar_partes` v0.7):** BUG1 (`RE_REPDE` "por sí" precedence — el principal es quien recurre por sí, no el representado) + BUG2 ("(" colgado, strip en `_trim_nombre`) cerrados; ruteo del head rol-pelado ("el actor") a `caratula:rol_sin_nombre`. 36 cambios sobre baseline v0.6, 0 regresión, 16 misatribuciones corregidas (14/16 menores), validado por `diff_partes_v06_v07.py` [CLEAN]; `343_p1758` (ANTONIO) recuperado vía carátula. **SIGUEN ABIERTOS:** terminador (→ v0.8, fila propia) y (a) la-defensa-de / (b) apoderado-a-favor / (c) MP — estos tres con **decisión de taxonomía pendiente** (rol MP `penal` vs propio; conecta M32), NO regex. **CERRADO H160 (`derivar_partes` v0.10, Capa 2 parseo):** los tres patrones resueltos en `parse_parte`, validado contra 10 fallos enteros extraídos + diff. (a)/(b) la-defensa-de / apoderado-de / en-ejercicio-de-la-defensa / a-cargo-de-la-defensa / abogado-del-condenado → **parte X** (penal si imputado, vacío si civil). (c) **MP con rol ADJUDICADO con Guillermo:** `mp_fiscal` (fiscal/fiscalía/Procurador Fiscal·General — acusa, MPF) y `mp_defensa` (defensor público/oficial/general · asesor de menores·incapaces·pobres·ausentes — defiende, MPD) → el **funcionario es la parte**; defensor DE imputado nombrado → imputado/`penal` (NO MPD). Resuelta la tensión `penal` vs propio: tokens propios `mp_fiscal`/`mp_defensa` (más legibles, conectan M32). + fix indicador `Dr.` (`Dres?\.`→`Dr(?:es)?\.`, 228 "Dr." singular que no entraban) + `por_derecho_propio`/`con su propio patrocinio`/`en causa propia` + Defensor del Pueblo = institución-parte (no defensa penal). **Bug intra-sesión cerrado:** over-fire `mp_defensa` cuando el imputado se nombra ("a cargo de la defensa de Justo Santiago Torres" → MPD en vez de Torres/penal, `329_p1541`); patrón "de la defensa de X" le gana a `RE_DEFENSA_MP`. Distribución final: `mp_fiscal` 0→81, `mp_defensa` 0→16, `por_derecho_propio` 10→44, `solo_letrado` 47→9. |
| multi-recurrente — rol single-valued | `recurrente_rol` guarda SOLO el rol del recurrente primario (leftmost); en multi, el resto se pierde | **NUEVO H157 (obs. Guillermo).** Cuando recurren DOS partes de lados opuestos (p.ej. `333_p2136` "Fargosi, **actor en autos**… y por la ANSeS, **demandada**"), el leftmost toma "actora" y descarta que la demandada también apeló. `multi_recurrente` lo flaguea (155 casos), pero el rol queda parcial. **Impacto M25:** un multi con roles mixtos (actor + demandada apelaron) es AMBIGUO para partyWinning → M25 debe tratarlo aparte (skip/flag), no asumir el rol primario. **Decisión de diseño PENDIENTE:** (a) mantener rol=primario + flag, documentar convención (actual); (b) `recurrente_rol` multi-valuado ("actora\|demandada"). No apurar — conecta con M25 y el value-set. **Gap colateral de `RE_MULTI`:** no flaguea "; y la X" sin "por" (`332_p674` "IVE… y la Empresa Constructora INDECO" quedó multi=no); el flag agarra "y por X" pero no "y la X". **MEDIDO H157:** la señal "y el/la X" da 68 candidatos, pero 27 son co-letrado ("y el Dr/Dra") + 14 tras representación/apoderado + varios nombre de institución ("y la Familia") → residuo silencioso REAL **~10-15**, NO separable por regex de co-letrado/institución/nombre-compuesto. **NO naive-fixear `RE_MULTI`** (flaguearía co-letrados como co-partes = FP en el flag, peor que el residuo). Dejar conservador (alta precisión); el residuo silencioso ~10-15 es límite conocido documentado. Separar co-parte de co-letrado necesita entender, no matchear (misma raíz que la dificultad de partyWinning en multi). |
| terminador over-capture (Traslados plural / línea siguiente) | `RE_MARK_REC`/`RE_MARK_TRA` no frenan ante "Traslado**s**" plural ni cierran el traslado → se comen la línea siguiente | **NUEVO H157.** `RE_MARK_REC` termina en `\bTraslado\b` (singular) → ante "Traslados contestados" (plural) no frena y over-captura la cola del traslado (`340_p1775` Milagro Sala: el rol se leyó de la cola, penal→querellante en v0.6, ninguno limpio). También `348_p1334`: `RE_MARK_TRA` se comió la línea "Recurso de queja interpuesto por el Fisco…" siguiente. Fix: terminador `\bTraslados?\b` + cierre del traslado en la línea. Toca el recurrido/over-capture, no el recurrente con nombre. Bajo volumen, pero ensucia rol cuando dispara. **→ TARGET v0.8 (H159):** terminador `\bTraslados?\b` + cierre del traslado en línea. Medido en disco (H159): de 47 over-capture en `RE_MARK_TRA` + 64 con "Traslados" en el clause de `RE_MARK_REC`, la **corrupción REAL son ~3** (`348_p1334`, `330_p298`, `345_p549`); el resto es cosmético — `parse_parte` recupera el nombre al recortar en el primer marcador de rol. Los "corruptos" restantes de `RE_MARK_REC` (~8) son **multi-recurrente** ("; y por X"), no terminador → fila de arriba (decisión pendiente). **CERRADO H161 (`derivar_partes` v0.13) — 2º defecto del terminador (colisión nombre-vs-footer):** los terminadores del lookahead (`\bTraslados?\b|\bTribunal\b|\bProfesional|\bNorma\b`) estaban SIN anclar → matcheaban dentro del clause del recurrente cuando una parte se llamaba "Norma X" (nombre de pila) o contenía "Tribunal"/"Profesional" ("Superior **Tribunal** de Justicia", "Consejo **Profesional** de…"), truncando a vacío/parcial. Fix: anclar a inicio de línea (`^Traslados?\b|^Tribunal(?:es)?\b|^Profesional|^Normas?\b`) — el footer editorial SIEMPRE arranca línea; bonus: `^Tribunal(?:es)?` agarra el plural "Tribunales que intervinieron". **+6 nombres recuperados** (`329_p4524`/`332_p2146`/`333_p68`/`334_p223`/`346_p193` ya rotos en baseline + `346_p811` destapado por el fallback de B) **+14 correcciones** (de-trunca / de-basura `.Tribunal` / abogado→parte: `329_p2614` Coriolano→Lourtau, `331_p2449` Gavernet→Lima/penal). Validado: diff v0.12→v0.13 = 6 GANA, **0 PIERDE**, 14 CAMBIA (todas mejoras), 0 regresión sobre los 3806. NOTA: `recurrente_ok` no sube (los Norma ya contaban como ok con captura vacía) → mejora de CALIDAD, no de conteo. |
| extractor epílogo — `sin_zona` en cierre por firma | `extraer_epilogos.py` deja `sin_zona` fallos que SÍ tienen pie editorial, cuando el caso cierra `fin_por_firma_actual`: el pie va DESPUÉS de la firma y cae fuera de la ventana `[linea_inicio, linea_fin]` | **NUEVO H159 — confirmado_cuantificado.** Señal limpia: de los cerrados `fin_por_firma_actual`, **100/113 (88%) caen `sin_zona`** vs ~24% base; ANTONIO `343_p1758` es el testigo (firma 11893, pie 11894–11910, dentro de `linea_fin_real` 11910 pero fuera de `linea_fin`). El borde OSDE/ANTONIO está limpio (`343_p1752` OSDE = `ok`). **Residual real = 30 huérfanos de mérito** (de los 100: 15 recuperados por carátula como ANTONIO + 19 `rol_sin_nombre` + 30 sin recurrente; su `case_name_cuerpo` es Eje A "Apellido c/ X", el PASO 4 no dispara → el pie es su ÚNICA fuente, p.ej. `344_p2669` tiene "E. G. P. B." solo en el epílogo perdido). Es una tajada nítida del body-search (~206). **OJO `linea_fin_real` no sirve de cota** (a veces < `linea_fin`): ventana robusta = firma → `linea_inicio` del caso siguiente. **Estado del fix:** diseñado, NO implementado — toca `extraer_epilogos.py` (no subido aún). Bump propio. **NOTA H160 (2º frente del extractor):** la DESHIFENIZACIÓN del epílogo vive HOY en `derivar_partes` (Capa 0, `_deshifenar`, soft-hyphen-only U+00AD) como **STOPGAP** — el fix de producción es 1 línea soft-only en `extraer_epilogos.py` con la MISMA regla, NO el `parser._unhyphenate` de prosa (que une el guión REGULAR separador de entidad y corrompe "Estado Nacional- Ministerio"→"NacionalMinisterio"). Migrar cuando se prefiera limpiar en la fuente; mientras, el deriver lo cubre. **CERRADO H161 (`extraer_epilogos.py` v0.3):** fallback `sin_zona` para `fin_por_firma_actual` — `_pie_desde_firma` escanea el pie desde `linea_fin_real` (=fin de la última zona `firma`, validado en los 30) hasta `linea_inicio` del caso siguiente, con guard al footer (`^Tribunal(es)?`/`^Profesional`), saltando artefactos de página (`RE_PAGE`). **+89 epílogos recuperados** (sin_zona 1352→1263); de los 30 huérfanos de mérito, **27 recuperan recurrente** (2 negativos correctos: `337_p45` sin pie / `348_p473` originaria Eje-A; 1 bloqueado por colisión "Norma" → resuelto por `derivar_partes` v0.13). **Convención validada vs zonas.csv:** la zona `epilogo` real arranca firma+1 (72,6%) / firma+4 con artefacto (8,3%) → el ancla+`RE_PAGE` la replica. **Deshifen migrada (deuda #3):** `_deshifenar` soft-only (U+00AD) ahora en el extractor, idempotente con el de `derivar_partes` (que queda de defensa); preserva el guión-separador de entidad. `csjn_casos_epilogo.csv` regenerado (sha `56eae57f…` v0.3), manifest re-sellado. |
| `RE_MARK_REC` — marcador `por:` (dos puntos) | el ancla del marcador exige `…por\s+` → el formato viejo "interpuesto **por:** X" (sin espacio antes de `:`) no matchea | **NUEVO H161 — confirmado_caso_testigo.** `337_p948` ("Fisco Nacional (AFIP-DGI)") tiene el pie recuperado por el fallback de B pero `parse_parte` cae a `sin_marcador_recurso` porque `RE_MARK_REC` pide `por\s+` y "por:" no calza. Toca la gramática compartida (`RE_MARK_REC`, los 3845). **Estado del fix:** no diseñado (candidato: `por[:\s]\s*`). Dimensionar corpus-wide antes (¿cuántos "interpuesto por:" hay?). Bump propio de `derivar_partes`. Bajo ROI individual; +1 confirmado, magnitud real sin medir. |
| calidad `parse_parte` — prefijo rol + inversión nombre | el general path de `parse_parte` (a) no stripea el artículo+rol pegado ("la demandada Ciccone S.A.", rol duplicado en `recurrente_rol`) y (b) corta en `RE_CORTE` ANTES del nombre cuando el rol precede ("por la parte actora, NOMBRE" → "la") | **NUEVO H161 — confirmado_cuantificado.** Medido en C (v0.12): **54 recurrentes (38 mérito)** con prefijo artículo+rol pegado, 53/54 de epílogo. Testigos de B: `344_p1030`→`"la"` (corta en "parte actora" antes de "Gisela Denisa Romero"), `344_p220`→rol `penal` espurio (de `RE_PENAL` sobre el "Fiscal" del REPRESENTANTE, no de la parte "Provincia del Chaco"), `347_p905` nombre MP sucio. Afecta `epilogo:recurso` corpus-wide. **NO uniforme** (algunos tienen nombre tras el rol, otros van sin nombre tras "la actora"→representación) → no es strip a ciegas. Toca la función compartida (los 3690 de epílogo) → su propia no-regresión. **Estado del fix:** no diseñado. Conecta con M32 (limpieza de nombre para el entity-typing). Bump propio. **CERRADO (a)+(b) H162 (`derivar_partes` v0.14) — handler de INVERSIÓN:** `RE_INVERSION` ancla "(art)(parte)? ROL", toma el rol procesal del prefijo y el nombre de lo que sigue, recortado por `RE_CORTE_INV` (superset de `RE_CORTE`: + representaci\w+/representant/apoderad/conjuntamente/"con la representación"/PDP). Si tras el rol va letrado/apoderado, recursa a `parse_parte` (`344_p1835`→"la Municipalidad de Puán"). Rol PROCESAL (decisión H162, 9 PDP triple-validados). RESTRINGIDO a recuperación de nombre (rol-only cae a v0.13). Validado: baseline v0.13 byte-idéntico (`54fe7e27`), **146 recurrente + 4 recurrido + 2 correcciones de representación** (`330_p1034`/`346_p491`), **0 PIERDE, 0 cambio de métrica**. `csjn_casos_partes.csv` sha `f2894294…` v0.14. **SIGUEN ABIERTOS (bumps propios de esta fila):** **bump 2 — penal-falso** (`344_p220`: `RE_PENAL` sobre el "Fiscal" del REPRESENTANTE marca penal espurio a "Provincia del Chaco"; guard: penal solo si no viene únicamente del representante; **RE-MEDIDO H163: 17 casos** —entidades públicas marcadas `penal` por el cargo "Fiscal de Estado/Procurador/Fiscal de Cámara" del representante, no de la parte—, no 1 como estimó H162; una heurística a ciegas regresaría 376 penales correctos —imputado+defensor oficial—, así que el guard tiene que distinguir cargo-del-representante de imputado-nombrado) · **bump 3 — MP office-title garbled** (4 casos `331_p53`/`339_p1453`/`345_p1363`/`347_p905`: `_strip_titulo`/`_letrado_name` sacan solo el primer token del cargo) · **bump 4 — nombre-en-clause no extraído (NUEVO H163, confirmado_cuantificado):** 6 recurrentes con rol pelado + nombre EN el clause que `parse_parte` no saca (la cola lo traba): `342_p583`→"Gardebled Hnos. S.A.", `342_p899`→"Valtellina Sud América S.A.", `342_p1434`→"Equity Group Consultores SRL", `344_p2383`→"María Lucila Colombo", `329_p4140`→"ENCOTeSA", `347_p917`→"Almada Benítez". El handler de inversión debería recortarlos y no lo hace. Pre-existentes (idénticos al golden v0.14, 0 regresión); los destapó la verificación de completitud de H163 (la detección estricta de target —rol pelado a secas— no los veía). Toca la función compartida → su no-regresión. **Estado del fix:** no diseñado. + 4 casos del mismo barrido necesitan carátula (`330_p4459`/`332_p2068`/`333_p1325`/`339_p1302`) → caen en el cruce editorial-index de H164 si se afloja el gating a "empieza con rol pelado". |
| rol por carátula — epílogo con nombre, sin rol (M33) | el rol procesal del recurrente vive en la carátula ("…deducido por la actora en la causa X c/ Y"), pero el paso 4 solo corre si falta el marcador del epílogo; cuando el nombre vino del epílogo sin rol, nunca leemos el rol de la carátula | **NUEVO H162 — confirmado_cuantificado.** De los 2138 `(sin rol)`: **531 con rol leíble directo de la carátula** (frase "la actora"/"la demandada" en `case_name_cuerpo`), 573 con marcador de carátula sin rol legible, 1034 sin marcador. Consistencia: **~415 caen del lado correcto del `c/`**, 61 discrepan, 31 ambiguos. Reusa `RE_MARK_CARATULA`+`_rol`+`_nombre_desde_causa`. **Guard obligatorio:** asignar rol SOLO si el recurrente del epílogo cae del lado del `c/` que da el rol; si discrepa → dejar `(sin rol)`. Impacto: +~415 roles (rol-cobertura de recurrente_ok ~44%→~55%). **Estado del fix:** diseñado, no aplicado. Bump propio (→ entrada **M33**). |
| inflación rol-only → `rol_sin_nombre` (M34) | ~80 casos "la actora, representada por la Dra. X" (parte sin nombre, solo el letrado) cuentan como `recurrente_ok` con nombre "la actora" | **NUEVO H162 — confirmado_cuantificado.** El handler de inversión (bump 1) ya los detecta y vacía, pero quedan como recurrente_ok con nombre vacío en vez de `rol_sin_nombre`. **Mérito-con-nombre honesto ≈ 90,7% (2604/2870)** vs 92,8% reportado (consistente con la cota estricta ya anotada en la fila "frente consolidado"). Re-clasificar mueve recurrente_ok ~−80 y mérito ~−57. Fix: en `derivar_de_epilogo`, si `parse_parte`→("", rol) setear fuente `epilogo:rol_sin_nombre`; en `_registrar` contar fuente endswith "rol_sin_nombre" en el bucket rol_sin_nombre. **Estado del fix:** diseñado, no aplicado. **Mueve canónico → requiere OK explícito.** Bump propio (→ entrada **M34**). |
| multi-recurrente — cola sin resolver (preexistente) | clauses multi-parte con representaciones encadenadas no se segmentan; la cola queda dentro del nombre | **NUEVO H162 — confirmado_caso_testigo.** Testigos `332_p1488` ("Carlos Ernesto Romero y el Dr. César José Torelli, ambos por su propio derecho"), `341_p1619` (Estado Nacional + ENARGAS + Distribuidora, multi-apoderado). NO lo toca el handler de inversión (no arrancan con "el/la ROL"). Afín a la fila "multi-recurrente — rol single-valued". **Estado del fix:** no diseñado. Fuera de scope de B. |
| M39 | eje de mérito BICAPA divergente: `is_merit` ⟺ `es_revision_fondo` — **234→219 mismatches** tras paso 1 (H172) | **NUEVO H170 (entrada madre de D1); PASO 1 EJECUTADO H172.** Desglose original: M1 15 (→B135) · M2A 98 (gate ok) · M2B 18 (MIXTO: →B139 + outcome) · M2C 13 (4 originarias + B139b) · M3 44 (gate ok) · M4 24 asides B129 + 3 (→B140 ×2 + variante) · M5 19 (→B138). ORDEN LOCKEADO: **B135 (✓ H172)** → guards del gate (B138/B139/B140) → extender B136 corpus-wide. Post-B135: divergencia 219, M1 convergió (14 salieron; el «1» residual es ruido de la regex amplia del diagnóstico sin guards, no del parser). **PASO 2 SUSTANCIALMENTE EJECUTADO H175** (B138 ✓ v1.12 · B140b ✓ v1.13 · B140a documentado-sin-guard): divergencia 219→208→**216** (los 9 de B140b EXPUESTOS = residuo lado parser, se absorben en paso 3). Próximo: B139 (re-estratificar post-B141), luego paso 3. **H176: B139 re-estratificado/adjudicado/diferido + v1.14 (impugnación): is_merit 3010 · gate=si 2950 · divergencia 216 sin cambio (flip bicapa simétrico). ~7 aciertos-del-gate nuevos adjudicados = insumo directo del paso 3. **H178: PASO 3 EJECUTADO Y CERRADO — is_merit derivado del gate (parser v24.0, fuente única); divergencia 0 POR CONSTRUCCIÓN; D1 RETIRADO (límite: coincide-en-error → B142/M43). M39 CERRADA**|
| M40 | backlog auditoría REE H170: D2 (INOFICIOSO divergido) · D3 (_FONDO 4 copias, 1 divergente) · D4 (280/ac4 duplicada, dedup antes de post-B010) · D5 (normalización asimétrica — RE-JERARQUIZADO: condición previa de M39 paso 1) · D6 (doble gramática pie sin test de contrato) · R2 (=audit B137) · R3 (writers upstream sin lineterminator → CRLF) · R4 (columnas sin REQUIRED en derivar_recursos) · R5 (merge sin assert) · E1 (changelogs inline ~9k) · E2 (fuente CRLF) | **NUEVO H170** — confirmado_caso_testigo (líneas citadas en BITACORA H170). Triage por ROI pendiente; D5 sube por M39/B135(b) |

**Integración de materia capa 1 (pendiente):**

| Ítem | Qué | Estado |
|------|-----|--------|
| CODEBOOK | documentar `materia` / `materia_capa` / `materia_fuente` (tributario = capa 2) | pendiente |
| csjn_analisis_v4 | left-join del sidecar por `caso_id_canonico` | pendiente |

**Sui generis / terminales:** 8 `sui_generis` (Jurado de Enjuiciamiento + Consejo de la Magistratura) sin label, pendientes de lectura (cuestión federal / disposición) antes de taxonomía.

**Cola larga sin triar:** las secciones `Deuda ACTIVA — Parser/Auditor` (B014–B099, M0x, VIS, A0x) tienen entradas viejas SIN marcador de estado — dormidas/superadas en su mayoría. Requieren un pase de triage de LECTURA para confirmar estado; NO están en este tablero hasta triarlas (escalón 2 del reordenamiento de DEUDA).


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

### B100 — `FUERA_DE_TERMINO` falso positivo en reposiciones contra resolución de la Corte — CERRADO H093

**Componente:** parser (`clasificar_causa_inadmisibilidad`, campo `causa_inadmisibilidad` de H092).
**Origen / fuente del diagnóstico:** H093, validando la cola de `causa_inadmisibilidad` contra `.md` reales (pendiente que H092 dejó abierto). Gatillo: H092 reportó la cola como «4 validadas» con conteos del PISO del PoC (`sub_gate.py` lee `considerando_text` truncado a 2000 → FUERA 10), pero **producción emitía 12** (corre sobre texto completo). Los 2 hits faltantes (341_p2027, 344_p249) tienen el `extempor` pasado el char 2000 — parte de los 14 «delta» de toda la cola que H092 nunca eyeballeó.
**Causa raíz:** `RE_CAUSA_FUERA_TERMINO` matchea «recurso … extemporáneo / fuera de plazo» sin distinguir si el recurso tardío es **el que la Corte decide** o uno del **antecedente narrado**. En las reposiciones contra una resolución de la Corte, el `extempor` describe la queja previa rechazada por extemporánea; el holding presente es «se desestima la reposición» (resoluciones de la Corte no susceptibles de recurso, Fallos 316:1706). `extempor` del antecedente → FUERA es FP.
**Diagnóstico / evidencia:** 12 FUERA validados a mano sobre `.md` completos = **10 TP / 2 FP**. TP: 330_p2574, 339_p180, 339_p1171, 340_p902, 341_p552, 342_p1548, 343_p1388, 344_p249, 341_p2027 (TP por considerando subsidiario «la presentación directa ha sido deducida en forma extemporánea», art. 282), 344_p1785. FP: 329_p5138, 329_p5316. Discriminador validado 11/12 (el 12º, 344_p1785, cerrado con `extraer_caso.py` sobre el vol 2): FUERA correcto cuando el recurso/queja PRESENTE es el tardío; FP cuando el `extempor` califica un recurso del antecedente. Sub-hallazgo: el truncado a 2000 no solo esconde hits, **da vuelta veredictos** (341_p2027 parecía FP leído truncado, es TP completo) → M15.
**Estado de verificación:** `confirmado_cuantificado`.
**Fix aplicado (H093):** nuevo `RE_CAUSA_FUERA_TERMINO_EXCL_DISP` anclado al `por_ello` (dispositivo: «(se) desestima/rechaza/no ha lugar a (la) reposición/revocatoria/aclaratoria»), inmune al truncado del considerando; condición extra en el bloque FUERA de `clasificar_causa_inadmisibilidad`. Efecto: 2 casos `FUERA_DE_TERMINO`→`INADMISIBLE_SIN_CAUSAL_EXPLICITA` (residual honesto; FUERA 12→10, SIN_CAUSAL 441→443). Validación: PoC `scripts/diagnostico/H093/poc_excl_reposicion.py` (drop 2 / keep 10, 0 TP falso-excluido, barrido del universo = solo 2 afectables); A/B old↔new sobre texto idéntico = 2 diffs exactos; check_regresion column-aware [FAIL] con exactamente fila 871/897 col `causa_inadmisibilidad`, votos/zonas/editorial [OK]; re-golden consciente. parser v18.11→18.12, commit 7bcac83.
**Pendiente relacionado:** el resto de la cola (SENTENCIA_DEFINITIVA 44, FUNDAMENTACION 12, DEPOSITO 4) NO está eyeball-validado a fondo (solo spot-check 348_p494 = TP; los delta nunca mirados). Posible causal nueva RESOLUCION_NO_RECURRIBLE para las 26 reposiciones-desestimadas del universo gate-genérico (hoy 22 en SIN_CAUSAL, 1 en DEPOSITO_PREVIO —posible mislabel a revisar—, 1 en `""`, 2 eran las FUERA corregidas).
**Referencias cruzadas:** H092 (causa_inadmisibilidad), H093. M15. Sin ID histórico.

### B101 — `FALTA_SENTENCIA_DEFINITIVA` falso positivo en outcome `otro` (match en dictamen/antecedente, no holding) — CERRADO H094

**Componente:** parser (`clasificar_causa_inadmisibilidad`, campo `causa_inadmisibilidad` de H092).
**Origen / fuente del diagnóstico:** H094, validando los 12 «delta» de la cola contra `.md` reales (continuación de H093/B100). Único FP de los 12: 334_p419.
**Causa raíz:** las 3 causales de cola (SENTENCIA_DEFINITIVA, FUNDAMENTACION, DEPOSITO) se chequeaban ANTES del guard `outcome == "otro" → ""`, mientras que FUERA_DE_TERMINO ya exigía `outcome in OUTCOMES_GATE_GENERICO`. Para outcome `otro` (el parser no determinó dispositivo de gate) el regex matcheaba la frase «no constituye sentencia definitiva» citada en la resolución denegatoria de la Cámara y en el dictamen del Defensor Oficial — antecedente/dictamen, no el holding. En 334_p419 la Corte declaró la NULIDAD de la sentencia de grado y reenvió (favorable): afirmar inadmisibilidad por falta de sentencia definitiva es FP.
**Diagnóstico / evidencia:** 334_p419 validado sobre el bloque exacto del parser (`extraer_caso.py` v2.0, LibroVol334.1 líneas 16342-16676): 2 matches del regex, ambos en antecedente/dictamen; dispositivo real «se declara la nulidad» posterior a ambos. Universo afectable = 1 fila (único hit de cola con outcome fuera de gate-genérico).
**Estado de verificación:** `confirmado_cuantificado`.
**Fix aplicado (H094):** las 4 causales de cola (las 3 + FUERA) gateadas bajo `if outcome in OUTCOMES_GATE_GENERICO:` (FUERA pierde su condición inline, ahora la hereda del bloque). Para `otro` no se afirma causal. PoC `scripts/diagnostico/H094/poc_cola_gate.py` (dirección = 1 fila). A/B old↔new sobre texto idéntico (M15) = exactamente 1 fila (334_p419: FALTA_SENTENCIA_DEFINITIVA → ""); re-golden consciente, check_regresion [CLEAN] 4/4. parser v18.12→18.13. Conteo: FALTA_SENTENCIA_DEFINITIVA 44→43, (vacío) 4632→4633.
**Referencias cruzadas:** H092 (causa_inadmisibilidad), H093/B100 (mismo discriminador holding-vs-antecedente). M15. Sin ID histórico.

### B102 — `extraer_caso.py` ancla en el volumen equivocado en tomos con volúmenes solapados — CERRADO H094

**Componente:** diagnóstico (`scripts/diagnostico/extraer_caso.py`, herramienta no ligada a sesión).
**Origen / fuente del diagnóstico:** H094, validando 338_p830 (ACUMAR/Mendoza). La herramienta daba 0 matches del regex y aparentaba un «label fantasma» (el CSV etiquetaba FALTA_SENTENCIA_DEFINITIVA pero el texto extraído no lo soportaba).
**Causa raíz:** `extraer_caso.py` <v2.0 resolvía el `.md` por `glob(LibroVol{tomo}*.md)` + primer match del ancla de 80 chars del considerando. En tomos partidos en volúmenes solapados (p.ej. 338.1/338.2) con fallos hermanos de considerando casi idéntico (los Mendoza de ejecución), el ancla matcheaba primero en el volumen equivocado y extraía OTRO caso. El `source_file` real de 338_p830 es LibroVol338.2.md; la herramienta leía 338.1.
**Diagnóstico / evidencia:** comparación `source_file` (CSV) vs volumen leído por v1.01 sobre los 12 delta = solo 338_p830 desalineado (los otros 11 leyeron bien). Re-validado en 338.2 (bloque del parser): el holding está presente («la prohibición… no constituye la sentencia definitiva que exige el art. 14») → 338_p830 es TP, nunca fue FP.
**Estado de verificación:** `confirmado_caso_testigo`.
**Fix aplicado (H094):** `extraer_caso.py` v1.01→v2.0. Sin `--md`: resuelve el volumen por `source_file` del CSV y extrae el bloque por rango de líneas `[linea_inicio, linea_fin_real]` reusando `construir_bloque_desde_localizacion` del parser (reproduce el bloque exacto que clasifica el parser, 0-indexado, lfr inclusive). `--md` queda como override (anclaje por texto, modo ≤v1.01); fallback a glob+ancla solo si la fila no trae source_file/líneas, con `[WARN]`; sanity check que avisa si el ancla del CSV no aparece en el bloque. Diagnóstico, no toca pipeline/golden.
**Referencias cruzadas:** H093 (creación de extraer_caso.py), H094. M17. Sin ID histórico.

### B103 — `DEPOSITO_PREVIO` falso positivo en revocatorias contra una resolución previa de la Corte — CERRADO H096

**Componente:** parser (`clasificar_causa_inadmisibilidad`, bloque DEPOSITO).
**Origen / fuente del diagnóstico:** H095, triage de los hits VISIBLE de la cola (DEPOSITO: 3 VISIBLE = 1 TP + 2 FP). El prompt de H094 anticipaba «1 posible mislabel»; son 2.
**Causa raíz:** mismo discriminador holding-vs-antecedente que B100/B101, pero el bloque DEPOSITO no tiene guard. En `330_p1025` y `343_p166` la frase del depósito describe una resolución ANTERIOR de la Corte («la resolución de fs. X, que desestimó la queja en razón de no haberse efectuado el depósito»); lo que el fallo decide es una revocatoria/planteo contra esa resolución, rechazada por el mérito del depósito (acordada 47/91 / ley 23.898), no un gate de depósito sobre el recurso decidido.
**Diagnóstico / evidencia:** `330_p1025` por_ello = desestima el recurso de revocatoria interpuesto contra la resolución de fs. 46; `343_p166` por_ello = desestima el planteo de fs. 68/70, estese a lo resuelto a fs. 62. `340_p225` = TP (holding desestima la queja por no acreditar el depósito tras intimación). Universo afectable = 2 filas.
**Estado de verificación:** `confirmado_cuantificado`.
**Estado del fix:** aplicado (H096). NO lo absorbe `RESOLUCION_NO_RECURRIBLE` (H095): estos 2 se rechazan por el mérito del depósito, no por irrecurribilidad — su considerando no enuncia la doctrina 316:1706. Fix correcto = guard en el bloque DEPOSITO, de nivel considerando (más amplio que el de B100: `343_p166` dice «planteo», no «revocatoria»; el discriminador robusto es «la resolución de fs. X que desestimó … en razón de no haberse efectuado el depósito»). Resultado esperado: 2 casos DEPOSITO_PREVIO → INADMISIBLE_SIN_CAUSAL_EXPLICITA (DEPOSITO 4→2).
**Referencias cruzadas:** H093/B100, H094/B101 (mismo discriminador). H095. Sin ID histórico.
**Fix aplicado (H096):** `RE_CAUSA_DEPOSITO_EXCL` (anclado al considerando `co`, inmune al truncado) sumado como `and not RE_CAUSA_DEPOSITO_EXCL.search(co)` a la condición del bloque DEPOSITO. PoC `scripts/diagnostico/H096/poc_b103_guard_deposito.py`: (1) A/B OLD↔NEW sobre texto idéntico = 2 flips exactos (330_p1025, 343_p166), universo de cambios ⊆ DEPOSITO del golden (el guard solo saca, nunca agrega); (2) capa anti-M15 que reconstruye el bloque completo del `.md` por `source_file` + `[linea_inicio, linea_fin_real]` (reusa `construir_bloque_desde_localizacion`) y exige EXCL solo en los 2 FP — `348_p805` (TP con considerando truncado a 2000 en el CSV) da `EXCL_full=False`, no se flipea. Hallazgo metodológico: correr la función sobre el `considerando_text` del CSV NO reproduce el golden para causales con ancla pasada el corte (p.ej. 329_p440 REMITE_DICTAMEN) → el A/B es OLD↔NEW sobre el mismo texto, el delta-conteos se deriva del golden. check_regresion [FAIL] solo esas 2 celdas de `casos` (verificado por `git diff`: 2 filas, resto byte-idéntico), votos/zonas/editorial [OK]; re-golden consciente (csjn_casos sha256 8d6360599442). parser v18.14→18.15 (DEPOSITO_PREVIO 4→2, INADMISIBLE_SIN_CAUSAL_EXPLICITA 413→415; gate total sin cambio 1036).

### B104 — Encabezados de página (running-heads) inyectados mid-considerando rompen regex cross-token

**Componente:** parser (datos: `considerando_text` con running-heads embebidos) / cualquier regex que cruce tokens.
**Origen / fuente del diagnóstico:** H095, diseño de `RESOLUCION_NO_RECURRIBLE`. `329_p5316` enuncia la doctrina pero NO es detectado porque el OCR insertó el encabezado de página en medio de una palabra: «no son suscepti**5317 DE JUSTICIA DE LA NACION 329**bles de recurso». Su hermano `329_p5138` (OCR limpio) sí entra.
**Causa raíz:** el texto digitalizado conserva los running-heads de página («NNNN DE JUSTICIA DE LA NACION TTT», «TTT NNNN FALLOS DE LA CORTE SUPREMA») embebidos en el flujo del considerando, a veces partiendo una palabra. `_unhyphenate` une quiebres con guión pero no remueve estos encabezados. Cualquier regex que dependa de adyacencia de tokens (no solo RNR) puede fallar en silencio sobre los casos afectados.
**Diagnóstico / evidencia:** caso testigo `329_p5316` (FN de RNR confirmado contra el `.md`). Los running-heads son visibles a lo largo de muchos `considerando_text`. Universo total sin cuantificar.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** strip de running-heads en la normalización del considerando (regex `\d+\s+DE JUSTICIA DE LA NACION\s+\d+` y `\d+\s+\d+\s+FALLOS DE LA CORTE SUPREMA`, ambas orientaciones), con A/B sobre TODAS las columnas para medir efectos cascada (afecta a todas las detecciones, no solo RNR) antes de aplicar. Mejora general de calidad de datos, no RNR-específica.
**Estado del fix:** no diseñado. NO se forzó en H095: meterlo a la regex de RNR sería frágil; el fix correcto es de normalización, transversal, con su propia validación.
**Referencias cruzadas:** H095. RESOLUCION_NO_RECURRIBLE. M15. Sin ID histórico.

### B105 — `por_ello` capturado del considerando / feria / oficio en vez del dispositivo

**Componente:** parser (`resolver_dispositivo` / cascada de tiers).
**Origen / fuente del diagnóstico:** H098 (codificación ciega del Marco A, M19).
**Causa raíz:** en ciertos fallos el campo `por_ello` no contiene el dispositivo sino un párrafo de considerando, una habilitación de feria, una orden procesal de oficio o una remisión a precedentes sin verbo resolutivo. La cascada no aísla el dispositivo real y emite texto no-dispositivo.
**Diagnóstico / evidencia:** 9 casos testigo, todos `cod_outcome=AMBIGUO` en la codificación porque el `por_ello` extraído no tiene verbo dispositivo: 332_p2625 (Lalo/YPF, remisión a precedentes), 334_p1081 (D.J.B., considerando de nulidades), 334_p941 (Cía. Gral. de Gas, considerando), 343_p412 y 343_p580 (habilitación de feria), 344_p2393 (Gatica, considerando), 345_p583 (GCBA c/ EN, considerando de cosa juzgada), 347_p412 (Carrizo, orden de oficio), 348_p405 (Cepas Argentinas, considerando).
**Estado de verificación:** `confirmado_cuantificado` (sobre el Marco A). Evidencia del titular H100: `outcome=otro` precision 14,8% (23/27 falso-residual: el humano les asignó categoría definida); el frente A es un componente de esa fuga. Caso testigo nuevo desde el suplemento H100: **343_p595** (La Meridional c/ Delta) — `por_ello` capturó solo el punto 1 (habilitación de feria); el dispositivo real (punto 2: «declarar parcialmente procedente el recurso extraordinario y dejar sin efecto») quedó afuera → parser `outcome=otro`, semántica `procedente`.
**Validador propuesto:** traer el dispositivo real con `extraer_caso.py`, comparar contra el `por_ello` del CSV, medir incidencia sobre el corpus. Posible heurística: si el `por_ello` no contiene verbo resolutivo conocido (o solo «habilitar días y horas»), reintentar la cascada al siguiente bloque resolutivo o marcar `sin_dispositivo`.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** H098, H100. M19. B083/B084/B085/B086 (cascada de dispositivo). B108 (parte de la fuga a `otro`). Sin ID histórico.

### B106 — `case_name_cuerpo` vacío teniendo «Vistos los autos: "…"» presente en el cuerpo

**Componente:** parser (extractor de carátula del cuerpo).
**Origen / fuente del diagnóstico:** H098 (codificación ciega del Marco A, M19).
**Causa raíz:** el extractor deja `case_name_cuerpo` vacío en fallos que SÍ traen el caption «Vistos los autos: "…"» en el cuerpo. No es residuo (B089) ni token genérico (B043/B093): es una falla de extracción de un caption presente.
**Diagnóstico / evidencia:** 2 casos testigo, ambos `cod_caratula_ok=0`: 332_p2797 (caption «Autolatina Argentina S.A. TF 13892-I c/ Dirección General Impositiva»), 346_p1241 (caption «C., J.M. c/ Swiss Medical s/ ley de discapacidad»).
**Estado de verificación:** `confirmado_caso_testigo` (2 casos).
**Validador propuesto:** grep de «Vistos los autos» en el bloque de los casos con `case_name_cuerpo` vacío; medir incidencia. Revisar por qué el caption presente no se captura (¿formato del tomo, ruido OCR en el delimitador?).
**Estado del fix:** no diseñado.
**Referencias cruzadas:** H098. M19. B014/B093/B094 (carátula), B089/B096 (residuo). Sin ID histórico.

### B107 — Cascada de `outcome` mal-clasifica negación y «excepción de incompetencia» — CERRADO H103

**Componente:** parser (`OUTCOME_PATTERNS_DISPOSITIVO`, cascada primer-match-gana).
**Origen / fuente del diagnóstico:** H098 (codificación ciega del Marco A, M19).
**Causa raíz:** la cascada matchea «hacer lugar» por substring dentro de «no hacer lugar al recurso» (negación) y dentro de «hacer lugar a la excepción de incompetencia» (decisión de competencia), devolviendo `hace_lugar` donde la semántica es `rechaza` y `competencia` respectivamente.
**Diagnóstico / evidencia:** casos testigo 348_p61 (Piumato c/ Guerrero, «no hacer lugar al recurso» → semántica rechaza) y 329_p53 («Hacer lugar a la excepción de incompetencia» → semántica competencia). En la codificación se asignó la semántica y se anotó la divergencia con la cascada.
**Estado de verificación:** `confirmado_caso_testigo` (2 casos; sin recall).
**Validador propuesto:** guard de negación («no hacer lugar») y de «excepción de incompetencia» antes del match de `hace_lugar`; PoC A/B sobre texto idéntico; medir incidencia sobre el corpus antes de aplicar.
**Fix aplicado (H103):** dos guards en `classify_outcome` (parser v18.15→18.16). (1) `RE_B107_NEG_HACER_LUGAR` enmascara el span «no (se) hace(r) lugar» antes de la cascada → la negación no dispara `hace_lugar`; el dispositivo real lo resuelve la cascada sobre el texto enmascarado (un «hacer lugar a X» NO negado sobrevive, así los dispositivos mixtos siguen bien), y la negación pura sin otro verbo cae a `rechaza` como base DÉBIL (el 280/ac4 del considerando aún puede ganar en Paso 3 — evita pisar `inadmisible_acordada_4`). (2) `RE_B107_LUGAR_EXCEP_INCOMP`, escopado a la frase exacta, routea «hacer/se hace lugar a la excepción de incompetencia» → `competencia` antes del match de `hace_lugar`. PoC A/B (`poc_b107_v2.py`); check_regresion [FAIL] solo 29 celdas de `outcome` + `is_merit_decision` derivado, votos denormalizado, zonas/editorial [OK]; re-golden consciente, [CLEAN]. Transiciones: `hace_lugar`→`rechaza` 21 / `competencia` 4 / `desestima` 2 / `revoca` 1 (329_p1399, otorgamiento mixto); `otro`→`rechaza` 1 (329_p1669); `originaria`→`competencia` 1 (331_p1302). Conteos: hace_lugar 1367→1340, rechaza 216→237, competencia 603→608, desestima 541→543, revoca 340→341, otro 688→687, originaria 166→165. Nota M15: el A/B sobre la columna `por_ello_text` truncada a 300 sobre-predijo 1 caso mixto que el parser resolvió bien sobre texto completo (29 reales, no 30).
**Estado del fix:** aplicado (CERRADO H103, commit propio).
**Referencias cruzadas:** H098, H103. M19. B091. Sin ID histórico.

### B108 — `competencia` (incompetencia originaria) cae a `outcome=otro` — CERRADO H104

**Componente:** parser (`classify_outcome` / cascada de dispositivo).
**Origen / fuente del diagnóstico:** H100 (titular M19).
**Causa raíz:** la cascada no reconoce los dispositivos de incompetencia originaria («declárase incompetente», «ajena a la competencia originaria», «no corresponde a la competencia originaria») y los buckea en `otro`.
**Diagnóstico / evidencia:** de los 26 `otro` evaluables del Marco A, 21 son `competencia` por lectura ciega; precision `otro` 14,8%, recall `competencia` 65,5%. Casos: 329_p1917, 329_p2911, 329_p3834, 329_p4342, 329_p5336, 329_p5670, 330_p610, 330_p619, 331_p194, 332_p1029, 332_p548, 339_p506, 340_p397, 340_p822, 341_p1338, 343_p1319, 347_p833, 348_p1576 (+ 330_p3777 originaria, 348_p92 hace_lugar).
**Estado de verificación:** `confirmado_cuantificado` (Marco A; recall corpus por medir).
**Validador propuesto:** patrones de incompetencia originaria en `classify_outcome`; PoC A/B sobre texto idéntico; medir incidencia y cascada sobre `is_originaria`.
**Fix aplicado — CORE (H103):** patrón nuevo en `classify_outcome`, zona fallback (solo rescata de `otro`; parser v18.16→18.17): `declara(r|se)? (la )?incompetencia` | `(es )?ajena a (su|la) competencia originaria` | `no corresponde a (su|la) competencia originaria` → `competencia`. Cubre la Corte DECLINANDO competencia originaria (el adjetivo «incompetente» ya estaba; faltaba el sustantivo «incompetencia» y las formas «ajena a»/«no corresponde a»). Incidencia medida sobre el corpus entero (no la muestra): **157** `otro`→`competencia`. PoC A/B (`poc_b108.py`); check_regresion [FAIL] solo 157 celdas de `outcome` (CERO derivadas: ni `is_merit_decision` ni `is_originaria` se mueven, `is_originaria=1` queda en 477), votos denormalizado, zonas/editorial [OK]; re-golden consciente, [CLEAN]. Conteos: `competencia` 608→765 (+157), `otro` 687→530 (−157).
**Fix aplicado — DECLINE-GAP (H104):** el core de H103 tenía `no corresponde a` pero le faltaba `no es de la competencia originaria`; sumada esa alternativa (parser v18.17→18.18). Incidencia: **16** `otro`→`competencia` (15 vistas a ojo + 339_p876, que la deshifenación del parser rescató y mi scan truncado no veía). check_regresion [FAIL] solo esas 16 + votos denormalizado, zonas/editorial [OK]; re-golden consciente. `competencia` 765→781, `otro` 530→514.
**Estado del fix:** CERRADO H104. La mitad ACEPTA de la frontera (las «corresponde a la competencia originaria», la Corte acepta) NO se trató como `competencia` vs `originaria`: se absorbió en **B112** (deprecación de `outcome=originaria`), que las manda a `competencia`. Los **48** remite-dictamen siguen en B105.
**Referencias cruzadas:** H100, H103. M19. B105 (los 48 remite-dictamen), B107. Frente D (is_originaria/competencia). Sin ID histórico.

### B109 — Sobre-trigger `inadmisible_280` / `inadmisible_acordada_4` en outcome de quejas desestimadas — CERRADO H106

**Componente:** parser (`classify_outcome`, 280/Acordada 4; `clasificar_causa_inadmisibilidad`, bloque gate-genérico).
**Origen / fuente del diagnóstico:** H100 (titular M19).
**Causa raíz:** en quejas donde el REX es inadmisible (art.280 / Acordada 4/2007) y la disposición de la queja es `desestima`, el parser ponía `inadmisible_280`/`inadmisible_acordada_4` en `outcome`. `desestima` no estaba en `OUTCOMES_NO_FALLBACK_280`, así que caía al Paso 3 de `classify_outcome` y el 280/ac4 del considerando lo pisaba. La convención correcta (confirmada leyendo 20 `.md` completos): el verbo dispositivo manda — `outcome=desestima`, el 280/ac4 va a `causa_inadmisibilidad`.
**Diagnóstico / evidencia:** Marco A reportó 12 casos; el A/B sobre corpus completo reveló **246** (la patología afectaba todo el corpus, no solo la muestra). precision `inadmisible_280` 14%, `inadmisible_acordada_4` 0% (Marco A).
**Estado de verificación:** `cerrado_validado` (texto completo M15 + check_regresion).
**Fix (dos partes, H106, parser v18.20→18.21):**
  1. `classify_outcome`: `desestima` sumado a `OUTCOMES_NO_FALLBACK_280`. El verbo dispositivo no se sobreescribe con el 280/ac4 del considerando.
  2. `clasificar_causa_inadmisibilidad`: detección TEXTUAL de 280/ac4 al inicio del bloque gate-genérico (reusa las mismas regex de `classify_outcome`, no reimplementa). Antes la causal ART_280/ACORDADA_4 venía "gratis" del mapa `OUTCOME_A_CAUSA` cuando outcome era inadmisible_280/ac4; al pasar a `desestima` se hubiera perdido. Va PRIMERO en el bloque (fórmula explícita y literal del rechazo; ante coexistencia con causal de cola gana, 1 caso 329_p510: 280 + extempor → preserva ART_280).
**Conteos (v18.20→v18.21):** `desestima` 547→793 (+246), `inadmisible_280` 240→38 (−202), `inadmisible_acordada_4` 50→6 (−44). Conservación exacta (+246 = −246). Causa preservada en los 246, **0 caídas a SIN_CAUSAL**; invariante de gate intacto (`causa != ""` = 1056, ART_280=240, ACORDADA_4=50 idénticos). Otros outcomes sin cambio.
**Método / validación M15:** PoC A/B sobre CSV truncado dio 229 flips; el parser real dio 246. La diferencia (17) son casos con el 280/ac4 pasado el corte de 2000 del `considerando_text` del CSV — el parser clasifica sobre el `.md` completo (líneas 3307→3311 de parser.py, pre-truncamiento), el PoC no los veía. Confirmación de M15. A/B final con parsers reales v18.20↔v18.21 sobre 20 `.md` extraídos con `extraer_caso.py` = 20/20 correctos. check_regresion [FAIL] solo casos+votos (246 + espejo denormalizado), zonas/editorial [CLEAN]; re-golden consciente; golden sellado (sha256 casos f79679fe2ba1, votos 5f5bc5171fe2).
**Cola del refactor (NO B109, va a M20):** 342_p1017 (mixto de resultados opuestos: desestima queja de una parte + procedente/revoca REX de otra → `desestima` no captura la disposición de fondo); 331_p530 (dos verbos, mismo resultado: inadmisibles REX concedidos + desestima queja); 339_p597 (prioridad ACORDADA_4 vs RESOLUCION_NO_RECURRIBLE en el gate — el holding del presente, reposición contra decisión propia, sería no-recurrible; matiz menor). Residual `inadmisible_280`=38 / `ac4`=6: casos donde el dispositivo declara inadmisible directamente (legítimos); revisar en sesión futura que ninguno sea queja desestimada escapada.
**Referencias cruzadas:** H100, H106. M19. M20 (refactor etapa/disposición+parte, donde viven los mixtos). B092 (gate `causa`). DISENO_SCDB_corpus §1.

### B110 — `es_queja` sub-detectado (falsos negativos) — PARCIAL H107 (sub-causa PLURAL cerrada; capa-fuente abierta)

**Componente:** parser (detección de recurso de hecho / queja, `classify_queja` + `RE_ES_QUEJA` + `QUEJA_RESULTADO_PATTERNS`, ~líneas 686-746).
**Origen / fuente del diagnóstico:** H100 (titular M19); causa raíz re-diagnosticada en H107.
**Causa raíz (re-diagnosticada H107 — NO es única, son tres mecanismos):** `classify_queja` clasifica mirando SOLO `por_ello_text` (el dispositivo). Los 20 FN del Marco A fallan por causas distintas: (1) **carátula/encabezado** — la queja se nombra en el `case_name` («recurso de hecho deducido por…», «s/ recurso de queja»), que `classify_queja` no mira: 12/20; (2) **considerando** — la queja se nombra en el considerando, no en el `por_ello`: 9/20 (solapan con (1)); (3) **plural** — `\bqueja\b` no matchea «quejas»: 330_p2445, 338_p40, 348_p1378. La sub-causa «soft-hyphen» (`que­ ja`) que se sospechó en H107 NO existe: `_unhyphenate` ya une el corte. Dos FN sin señal visible en el CSV (truncado): 329_p1487, 348_p1717.
**Diagnóstico / evidencia:** 20 FN (cod=1, parser=0) en el Marco A: 329_p1487, 329_p4094, 329_p4717, 329_p5789, 330_p1907, 330_p238, 330_p2445, 330_p4632, 330_p5010, 330_p5197, 332_p2625, 337_p329, 337_p373, 338_p40, 343_p412, 344_p2393, 345_p583, 348_p1378, 348_p1717, 348_p92. Sobre el corpus entero, el plural solo sangraba 63 quejas multi-recurrente (no 3): las que el dispositivo resuelve en plural («se hace lugar a las quejas», «se desestiman las quejas»).
**Estado de verificación:** `confirmado_cuantificado` (Marco A + corpus entero, A/B sobre el `classify_queja` real + check_regresion).
**Fix aplicado (H107 — sub-causa PLURAL):** pluralización estricta (solo número, sin cobertura nueva): `RE_ES_QUEJA` `\bqueja\b`→`\bquejas?\b`, `\brecurso de hecho\b`→`\brecursos?\s+de\s+hecho\b`, `\bpresentaci[oó]n directa\b`→`\bpresentaci[oó]n(?:es)?\s+directas?\b`; `_SYN_Q` idem; en `QUEJA_RESULTADO_PATTERNS` `la\s+`→`la[s]?\s+`, `hace\s+`→`hace[n]?\s+`, `agr[ée]guese\s+`→`agr[ée]guese[n]?\s+`, `esta?\s+`→`esta?s?\s+`. Parser v18.21→18.22. `es_queja` 1993→2056 (+63, puramente aditivo: 0 flips 1→0), ~59 celdas de `queja_resultado` pobladas (57 de los flips —hace_lugar 31/desestima 9/procedente 8/admisible 7/suspendida 1/abstracta 1, 3 sin label— + 2 toques en casos ya-queja consistentes con `outcome`: 332_p2441 desestima→hace_lugar mixto multi-parte, 343_p637 ''→hace_lugar). check_regresion [FAIL] solo casos (es_queja+queja_resultado); votos [CLEAN] byte-idéntico a H106 (el patch no toca `outcome`); zonas/editorial [CLEAN]; re-golden consciente (casos 904bfdedeadc, votos 5f5bc5171fe2). M15 al revés: PoC sobre `por_ello` truncado a 300 = 60, parser real sobre `.md` = 63 (3 escondidos por el truncado, p. ej. 330_p3055).
**FP residual conocido (aceptado, sin guard):** 329_p1703 — «las quejas de las partes resultan inhábiles» en un juicio de expropiación (`outcome=otro`, `queja_resultado` vacío): «quejas» = agravios (sustantivo común), no recurso de hecho. 1/63 → precisión del flip 98,4% (> 96,9% global). Sin guard por decisión REE: «inhábil» es ancla ruidosa (de 40 apariciones en `por_ello`, ~38 son «días inhábiles»/feria —tanda del tomo 343—, 1 sola es queja-agravio) y «queja…inhábil» es hapax=1 en el corpus → un guard sería overfitting a un caso. Aprendizaje de diseño: el discriminador recurso-vs-agravio NO es léxico sino estructural (la queja-recurso es OBJETO de un verbo de admisibilidad; la queja-agravio es SUJETO de un verbo de mérito) → se resuelve en la capa-fuente con contexto completo, no con un parche.
**Capa-fuente (PENDIENTE, prepara M20):** ampliar la fuente de `es_queja` más allá del `por_ello` a (a) carátula/encabezado con fórmula ritual («recurso de hecho deducid», «s/ recurso de queja», «s/ queja por…») y (b) considerando con ANCLA fuerte («dio origen a la presente queja», «la queja en examen»), NO mera aparición de la palabra. Universo de flip dimensionado (H107): ~219 casos por fórmula ritual de carátula, ~316 por considerando truncado → cambio MASIVO (tipo B112), NO atómico: rompe golden grande, re-titular, validar precisión sobre muestra de los flips (riesgo: residuo_caso_anterior y menciones de queja como antecedente). Frente propio, diseño por capas ordenadas por limpieza de señal (igual que materia). Consolida la «vía de acceso» antes del refactor M20 (que la lleva a nivel parte×recurso).
**Estado del fix:** PARCIAL (plural aplicado H107; capa-fuente no diseñada en detalle).
**Referencias cruzadas:** H100, H107. M19. M20 (vía de acceso a nivel parte). B105 (frente A, solapa con varios FN de carátula). B104 (OCR mid-palabra, descartado como sub-causa acá). Sin ID histórico.

### B111 — `tipo_cuestion_federal` sobre-usa `mixto` y pierde `arbitrariedad`

**Componente:** parser (clasificador `tipo_cuestion_federal`).
**Origen / fuente del diagnóstico:** H100 (titular M19).
**Causa raíz:** el clasificador sobre-asigna `mixto` (precision 38%) donde el agravio es simple (casi siempre arbitrariedad) y pierde `arbitrariedad` cuando no aparece la palabra (recall 65%). Además emite `tipo_cf` fuera de REX/queja (debería ser null en originaria/ordinario; ej. 329_p4150, `cuestion_federal` sobre una acción declarativa originaria, del suplemento).
**Diagnóstico / evidencia:** precision `mixto` 38,1%, recall `arbitrariedad` 65,5% (Marco A); 13 casos parser=`mixto` / cod=simple. **Cuantificado H120** (gold humano completo n=300, 3-way arbitrariedad/cuestion_federal/ninguna): accuracy 0,676 (n=136); **recall `arbitrariedad` 50%** — el parser etiqueta **15 arbitrariedades reales como `mixto`** y 9 como `cuestion_federal`. Confirma el sobre-disparo de `mixto` a costa de `arbitrariedad`.
**Estado de verificación:** `confirmado_cuantificado` (Marco A; ratificado y cuantificado H120).
**Validador propuesto:** los scans de keyword ya se descartaron en M19 (falsos +/−); lectura sustantiva. Gate de `tipo_cf` a REX/queja.
**Estado del fix:** no diseñado en código; **dirección estructural definida H134** (descomposición pretoriana, ver abajo). El campo NO se cierra con regex — pide ML/weak-supervision.

**Diagnóstico estructural ampliado (H134):**
- **Root cause del sobre-disparo de `mixto`** (cuantificado en disco): `classify_cuestion_federal` aplica una regla de co-ocurrencia `has_arb AND has_cf → mixto`; en el fallback sobre el considerando, `has_arb` dispara con `\barbitrariedad\b` pelado y `has_cf` con `ley 48` pelado, **ambos casi ubicuos en REX** → `mixto` = "menciona las dos palabras". Conteos: `mixto` 677 (parser) vs **1** (gold humano n=300, que usó "mixto" una sola vez) vs 230 con voz literal "Sentencias arbitrarias" de la Secretaría. De los 677, solo ~27% tienen marcador fuerte de ambos lados.
- **La señal de arbitrariedad está DISTRIBUIDA en tres zonas** (hallazgo central): (1) **sumario editorial** = voz de la Secretaría de Jurisprudencia, taxonomía verbatim, precisa pero **~24% recall** (sub-cuenta); (2) **considerando** = palabra suelta "arbitrar", sobre-dispara; (3) **dictamen** = donde vive la causal cuando la Corte remite ("comparte y hace suyos los términos del dictamen"). Verificado: de 38 misses gold-arbitrariedad, 29 NO tienen "arbitrar" en el considerando; de 28 misses-sin-`arbitrar`, **21 con `cod_dictamen=remite`** y 23 con considerando <400 chars. Ninguna zona es completa → es el caso empírico de weak supervision.
- **Taxonomía de causales** (voz de la Secretaría, verbatim, leaf tras "RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Sentencias arbitrarias. Procedencia del recurso. _<LEAF causal>_"): Defectos en la consideración de extremos conducentes (55), Falta de fundamentación suficiente (48), Excesos u omisiones en el pronunciamiento (39), Defectos en la fundamentación normativa (38), Exceso ritual manifiesto (22), Apartamiento de constancias de la causa (18), Contradicción (12), Valoración de circunstancias de hecho y prueba (7). **Gravedad institucional = flag ORTOGONAL, no es causal.**
- **Seed de dos zonas** (`harvestear_sumarios.py` v0.1 → `sumarios_arbitrariedad.csv`, 1560 filas voz + dictamen): clasificador de 8-9 causales que sirven en ambas zonas. Cobertura de causal: voz sola 462 → voz+dictamen ~931 (+469 que recupera el dictamen). **Recall vs gold-arbitrariedad-en-CSV (n=45): 18/45 (voz) → 38/45 (84%, voz+dictamen).** Quedan ~7 sin señal (343_p1233, 339_p1530, 346_p646, 342_p1358, 339_p824, 349_p280, 347_p1215). **Precisión muestreada ~80%** (10 recuperados leídos: 8 con causal predicada de la sentencia, 2 discurso reportado de parte). **El gate de discurso reportado descarta solo 10 casos / 0 cambio de recall → el FP NO es discurso reportado sino marcador ancho ("carece de fundamentación", "contradicción") en contexto legítimo = TECHO de la regex.**
- **Codebook de CF anclado en art. 14 Ley 48** (descomposición pretoriana = el fix de fondo): **inc. 1 + inc. 3 = CF simple** (validez/inteligencia de norma o cláusula federal, desestimada), **inc. 2 = CF compleja** (ley/autoridad provincial vs CN, prelación art. 31); **arbitrariedad = doctrina pretoriana ORTOGONAL** (flag aparte, NO un tipo de CF); **mixto genuino** = voz de CF Y voz de arbitrariedad coexistiendo. "ley 48" = 21% del corpus (23% de arbitrariedad pura) → NO discrimina; art. 15 / "relación directa" = boilerplate de admisibilidad, no ancla de tipo. art.14-inciso = alta precisión / baja cobertura.
- **Retractación honesta:** el "85% over-fire" que se afirmó al principio de H134 se corrigió — solo 230/1560 tienen voz literal "Sentencias arbitrarias", pero la voz SUB-CUENTA: 11/45 gold-arb con voz literal, y **14 gold-arb ni siquiera fueron taggeados por el parser (FN)**.
**Fix de fondo propuesto (no aplicado):** descomponer `tipo_cuestion_federal` en (eje CF art.14: simple/compleja/ninguna) + (flag arbitrariedad ortogonal, alimentado por las 3 zonas) + (flag gravedad institucional). Costo: re-golden (recodificar el gold de CF con el codebook art.14 como paso cero). `causal_arbitrariedad` como módulo deriver (patrón disposición/vía) o vía weak supervision (Snorkel: voz = LF alta precisión, dictamen = LF alto recall, considerando = LF ruidosa; conserva trazabilidad determinística para la defendibilidad de la tesis).
**Referencias cruzadas:** H100. M19. H119/H120 (gold). **H134** (diagnóstico estructural + seed dos-zonas + codebook art.14 + B128). Sin ID histórico.

---

### B112 — `outcome=originaria` era category error (tipo de proceso, no disposición) — CERRADO H104

**Componente:** parser (`classify_outcome` / cascada de dispositivo, pattern estructural línea 318).
**Origen / fuente del diagnóstico:** H104 (observación del usuario al resolver la frontera de B108: «originaria es un tipo de proceso, no un mérito; competencia originaria es una de las decisiones que puede tener un originario»).
**Causa raíz:** el pattern estructural `^Por ello,.*se resuelve:\s*(I\.|1°|Primero)` etiquetaba `originaria` a cualquier dispositivo enumerado por FORMATO, no por disposición. Peor: posicionado ANTES de los patterns de verbo en infinitivo (~335-346), así que «se resuelve: I. Desestimar/Rechazar/Hacer lugar» caía en `originaria` antes de su pattern de mérito → robaba disposiciones reales.
**Diagnóstico / evidencia:** los 165 `outcome=originaria` descomponían en ~47 aceptación de competencia originaria, ~67 méritos secuestrados (rechaza/hace_lugar/desestima/abstracto/desistimiento en infinitivo), 16 traslado/apertura, resto cautelar/oficio/declina. La dimensión proceso ya vive completa en `is_originaria` (477) y `tribunal_origen_status=originaria` (477) → `outcome=originaria` no aportaba información, solo pisaba la disposición. Lossless al sacarlo.
**Estado de verificación:** `confirmado_cuantificado` (corpus entero; diff fino caso por caso, proxy=parser 182/188).
**Fix aplicado (H104):** removido el pattern estructural; en su lugar aceptación de competencia originaria → `competencia` (simétrico con la declinación de B108): `(?<!no )corresponde a (la|su)? competencia originaria` | `(?<!no )es de la competencia originaria` | `declarar la competencia originaria`. Parser v18.18→18.19. Los 165 caen a su disposición real (`originaria` 165→0): aceptaciones a `competencia`; méritos en infinitivo rescatados; ~52 aperturas/procesales (traslado, cautelar, oficio) a `otro`. Cascada: `is_merit_decision` 0→1 en ~22 (rescatados a MERIT_OUTCOMES) + ripple en `tipo_voto`. Validación: proxy v19 = outcome real 182/188; los 6 diffs son override 280/ac4 del considerando + guard B107 (parser correcto, ej. 330_p5158→inadmisible_280, 331_p1302→competencia). check_regresion [FAIL] esperado (cambio de salida deliberado); re-golden consciente. Conteos: `originaria` 165→0, `competencia` 781→863, `otro` 514→541, `rechaza` 237→267, `hace_lugar` 1340→1355, `desestima` 543→547.
**Estado del fix:** CERRADO H104. Cola larga (logueada, NO perseguida — rendimiento decreciente, quedan en `otro`): «no pertenece a la competencia originaria» (decline), «corresponde, prima facie, a la competencia originaria» (accept con interjección), deferimientos «sin perjuicio de lo que se decida respecto de la competencia originaria» (~4-5 casos).
**Referencias cruzadas:** H104. Cierra la mitad ACEPTA de la frontera de B108. Frente D (is_originaria). M19. Sin ID histórico.

### B113 — `Declarar abstracta` (infinitivo) cae a `otro` en vez de `abstracto` — CERRADO H105

**Componente:** parser (`classify_outcome`, cascada de dispositivo / pattern de `abstracto`).
**Origen / fuente del diagnóstico:** H104 (expuesto por la deprecación de `outcome=originaria`: 12 casos «Declarar abstracta la cuestión» estaban enmascarados como `originaria` y al caer afloraron en `otro`).
**Causa raíz:** el pattern de `abstracto` (`inoficioso` | `abstracto` | `se declara abstracta?`) no cubre la forma infinitiva «Declarar abstracta/o la cuestión/pretensión». Nota de diseño: la forma real lleva el ADJETIVO ANTES del sustantivo («Declarar abstracta la cuestión»), no después — el validador propuesto en H104 (`declarar (la )?(cuestión|pretensión )?abstract[oa]`) habría matcheado igual de casualidad (los grupos `(cuestión|pretensión)` son opcionales y colapsa a `declarar (la)? abstracta`), pero esos grupos eran ruido; se usó la forma mínima `declarar abstract[oa]`.
**Diagnóstico / evidencia:** 12 casos en `otro`: 329_p40, 329_p1853, 329_p1898, 329_p2293, 329_p2733, 329_p4054, 329_p4370, 330_p3893, 331_p322, 337_p1439, 344_p1230, 344_p2020. Conteo sellado: el check_regresion confirmó exactamente esos 12, sin residuales (los 4 candidatos que el truncado a 300 de `por_ello_text` no dejaba descartar —330_p5070, 343_p1096, 344_p159, 345_p123— NO entraron al regenerar con el `.md` completo).
**Estado de verificación:** `confirmado_cuantificado` (corpus entero; A/B sobre `classify_outcome` real + check_regresion column-aware = 12 celdas exactas).
**Fix aplicado (H105):** nueva entrada `("abstracto", re.compile(r"\bdeclarar\s+abstract[oa]\b", re.I))` en ZONA FALLBACK (posición final, antes del catch-all). NO se extendió el pattern alto de `abstracto` a propósito: «declarar abstracta» aparece en dispositivos MIXTOS donde no domina —329_p753 (I. declarar abstracta una cuestión incidental, II. rechazar la impugnación de liquidación → `rechaza`) y 344_p3070 (I. competencia originaria, II. declarar abstracta → `competencia`)—; subirlo a zona alta los robaría. Como fallback solo rescata de `otro` (cascada primero-que-matchea). `abstracto` ∈ `OUTCOMES_NO_FALLBACK_280` → no lo pisa el 280/ac4 del considerando; NO ∈ `MERIT_OUTCOMES` → `is_merit_decision` no se mueve. Parser v18.19→18.20. Conteos: `otro` 541→529, `abstracto` 89→101; los 12 arrastran `causa_inadmisibilidad` `""`→`CUESTION_ABSTRACTA` (vía `OUTCOME_A_CAUSA`). check_regresion [FAIL] esperado (cambio de salida deliberado): `csjn_casos.csv` 12 casos × {outcome, causa_inadmisibilidad}; `csjn_casos_votos.csv` espeja `outcome` en las filas de voto de esos 12 (propagación denormalizada, línea 3460); zonas/editorial [OK]; re-golden consciente.
**Estado del fix:** CERRADO H105. Cambio atómico (no mezclado con B112).
**Referencias cruzadas:** H104, H105. B112 (lo expuso). Sin ID histórico.

### B114 — `tribunal_origen` fragmentado por OCR (corte de línea / running-head) y no normalizado — CERRADO H111

**Componente:** parser (extractor de `tribunal_origen`, ~`find_tribunal_origen`).
**Origen / fuente del diagnóstico:** H105 (al evaluar `tribunal_origen` como señal para el Frente B/materia — ver abajo).
**Causa raíz:** el campo captura el nombre del tribunal hasta el corte de línea del OCR INCLUSIVE, sin unir la continuación. Mismo tribunal aparece en variantes fragmentadas: «Cámara Nacional de Apelaciones en lo Contencioso Administra­» / «… Contencioso Admi-» / «… Contencioso Administra-». Distinto de un mero deshifenado: si la continuación de la palabra quedó FUERA del span capturado, `_unhyphenate` no tiene qué unir → el fix no es solo aplicar `_unhyphenate` al valor, hay que revisar el rango que toma el extractor.
**Diagnóstico / evidencia:** sobre el corpus (v18.20), top de `tribunal_origen`: «Contencioso Administra­» 178 + «Contencioso Admi-» 172 + «Contencioso Administra-» 36 son el MISMO tribunal cortado en tres formas → inflan los valores distintos y rompen cualquier lookup tribunal→materia. `tribunal_origen` poblado en los 5669 fallos; `SIN_TRIBUNAL_ORIGEN` 1791, originaria 477, apelado_detectado 3876.
**Estado de verificación:** `confirmado_cuantificado` (H111: leído el extractor y el OCR fuente; PoC A/B sobre el corpus completo).
**Nota de diseño (deshyphenate selectivo, regla):** NO aplicar `_unhyphenate` «a todo» indiscriminado. Criterio = para qué se usa el texto. (a) Donde se MATCHEA regex sobre OCR, normalizar ANTES ayuda y varios sitios ya lo hacen (`classify_outcome` lo hace con por_ello/considerando); el bug es donde se matchea/extrae sobre crudo sin normalizar (este B114). (b) Donde el texto es CONTENIDO persistido (case_name, firma_raw, texto_voto, tribunal_origen), unir mejora legibilidad pero `\w-\s+\w` une también guiones legítimos con espacio espurio del OCR («Buenos Aires- La Plata» → «Buenos AiresLa Plata») → decisión campo por campo, con guard. Hay diferencia entre normalizar para PARSEAR (transitorio, no se persiste — lo que el parser hace hoy a propósito) y persistir el dato normalizado (cambia contenido). Un unhyphenate global NO es atómico: rompe el golden masivo y puede meter regresiones sutiles en nombres → se descarta como switch único. (H111: confirmado seguro para `tribunal_origen` — los únicos guiones legítimos del campo, «La Plata - Sala II» / «Córdoba -Sala», tienen espacio ANTES del guión y no matchean `(\w)[­\u00ad-]\s+(\w)`.)
**Fix aplicado (H111):** `find_tribunal_origen` v11→v12 + helper `_parece_caratula`. Dos sub-patrones de corte confirmados leyendo el OCR: **intra-palabra** (valor termina en guión/soft-hyphen «…Admi-»/«…Administra␤», continuación en minúscula que cierra en `.` — la regla vieja la rechazaba por `not endswith(".")`) e **inter-palabra** (valor corta en preposición sin guión «…en lo Contencioso », continuación en MAYÚS — rechazada por `islower()`). v12: une líneas siguientes hasta la que cierra en `.`, parando en breaks estructurales (vacío, running-head, «Tribunal(es) que…»/«Intervino…»/«Ministerio…»/«Recurso…», y carátula vía `_parece_caratula` ≥60% de tokens largos en MAYÚS); `_unhyphenate` al final colapsa el corte intra-palabra. PoC A/B sobre `.md` completo (M15): **0 violaciones de invariante** (ningún tribunal que ya cerraba en `.` se movió), residual real 0 (el único «…Federal -Sala II-» es adorno, no corte), FP de carátula L1144 («…Jujuy MARIA EUGENIA CIRILO y Otro…») resuelto por `_parece_caratula`. parser v18.23→18.24. check_regresion column-aware: **1129 celdas `tribunal_origen`** recuperadas, 0 en otras columnas, header igual, 5890/5890 filas, `tribunal_origen_status` intacto (apelado_detectado 3889 / sin_marcador 1331 / originaria 477); votos/zonas/editorial [CLEAN]; re-golden consciente + verificación [CLEAN] 4/4. Colapso a fuero demostrado en el PoC (sobre los marcadores del corpus): contencioso-adm 634, civil-comercial 769, penal 448, laboral 375, previsional 279, electoral 28, bolsón otro/provincial/sin 1348 (= insumo de la capa 2). El nombre completo SUBE los valores distintos (fidelidad: distingue Salas y variantes) pero a nivel fuero —lo que importa para materia— colapsa.
**Estado del fix:** CERRADO H111. Habilita la **capa 1 del Frente B/materia** (lookup tribunal→fuero→materia sobre la columna ya limpia).
**Referencias cruzadas:** H105, H111. B028 (`find_tribunal_origen` ventana excede el bloque). M15 (truncado/normalización). Frente B/materia. Sin ID histórico.

### B115 — Merge de fallos por hueco en índice de partes (familia B009) — CERRADO H109

**Componente:** catálogo (`construir_catalogo` / índice de partes).
**Origen / fuente del diagnóstico:** H108 (canario: los 3 FP de la capa-fuente `es_queja` — 332_p1960, 343_p1987, 331_p856).
**Causa raíz:** el índice de partes no lista ciertos fallos (p. ej. quejas penales landmark: Arriola 332:1963, Acosta 331:858). `construir_catalogo` asigna a la entrada indexada anterior un rango que se estira hasta el próximo caso indexado, fundiendo todo fallo intermedio en una sola entrada. El parser extrae fielmente el rango del catálogo (es inocente — NO es el fin-de-bloque del parser).
**Diagnóstico / evidencia:** set-diff `catalogo.csv` vs `csjn_casos.csv` = 0/0 (mismos 5862 ids → el merge ya está en el catálogo). El catálogo define `332_p1960 = pg 1960-2033 "Massuh S.A."` (73 págs, traga Arriola); `331_p856 = 856-866 "Hernández"` (traga Acosta); `343_p1987 = 1987-2006 "N.N."` (traga una versión abreviada de Pérez, que sí sobrevive como caso propio en 343_p2122). Arriola/Acosta ausentes del índice (búsqueda en `nombres_indice`: solo homónimos civiles). Detector limpio en zonas: `apertura≥2` (un caso normal = 1, incluso con votos múltiples: 329_p28 tiene firma=5/disp=3 pero apertura=1). Dimensión: 103 casos con apertura≥2 → **71 con dispositivo≥2** (merge real, 2+ fallos completos) + 32 con dispositivo≤1 (probable acumulación de causas, 1 fallo, NO swallow). Multi-merge gordos: 344_p1151 (apert=16/disp=14), 346_p970 (disp=13). Casos perdidos del orden de ~70 (~1,2% del corpus), incluye landmarks. El span de páginas NO sirve como detector (conflaciona fallos largos legítimos —Boggiano 35k, Mazzeo 42k, Schiffrin, Bertuzzi— y pierde swallows chicos: 331_p856 span=10).
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto:** `apertura≥2 & dispositivo≥2` sobre `csjn_casos_zonas.csv`; refinar con sample de lectura (separar merge de acumulación; verificar leakage en el bucket disp≤1, p. ej. 333_p1732 Apablaza firma=2/span=27). Confirmar el fork con el índice fuente.
**Estado del fix:** no diseñado. Fork pendiente: (a) si el índice CONTIENE Arriola/Acosta y `construir_catalogo` falla al parsear esas líneas → bug de parseo acotado; (b) si el índice los OMITE genuinamente (quejas penales no indexadas por parte) → body-scan supplement (detectar aperturas en el cuerpo que el índice no tiene). Requiere `csjn_editorial_indice_partes.csv` o el `.md` del índice de esos tomos.
**Fork RESUELTO (H108, Arriola) → rama (a) [CORRIGE una conclusión previa errónea de esta misma sesión]:** el índice SÍ lista a Arriola. La imagen del «ÍNDICE POR LOS NOMBRES DE LAS PARTES / Por nombre del actor», sección A (tomo 332), muestra «Arriola, Sebastián y otros s/ causa 9080: p. 1963» como entrada propia (y «Aguilar, Alfredo Ernesto: p. 1960» = el caso Massuh). Error de verificación previo: se buscó «Arriola» en `catalogo.csv` (la SALIDA de construir_catalogo, que ya tiene el bug horneado) y el set-diff catalog↔casos (también derivado) en vez del índice FUENTE (.md) — se chequeó la capa derivada, no el origen. Conclusión corregida: NO es omisión estructural y NO es como Y.P.F. c/ Mercante (que sí era omisión real del índice del t.349) → el fix NO es body-scan. Es un **bug acotado de parseo/cruce en `construir_catalogo` (o `cruzar_catalogo_y_mapa`)**: la entrada del índice existe pero el pipeline la perdió, por lo que el rango de Aguilar (1960) se estiró hasta el próximo caso capturado (2033) tragando a Arriola (1963). Dos lugares candidatos del fallo (a verificar con .md + scripts): (i) parseo del índice — la entrada tiene un número embebido («s/ causa 9080») antes del «: p. 1963», la regex de línea puede grabar 9080 como página (fuera de rango → descarta) o no matchear; (ii) cruce índice→cuerpo — el ancla del cuerpo es «SEBASTIAN ARRIOLA y Otros» (sin c//v//s/) y el cruzador puede no localizar la entrada y dropearla.
**Detector de «cuántos más» (H109):** índice-FUENTE vs catálogo (no `apertura≥2`, que es el lado cuerpo). Extraer del .md todas las entradas «Nombre: p. NNNN», agrupar por página (dedup actor/demandado), obtener el set de páginas esperadas y diferenciar contra las páginas de los `caso_id` del catálogo; cada página del índice sin `caso_id` = entrada perdida (cuenta autoritativa de drops). Cross-check con `apertura≥2` (71, lado cuerpo). Requiere el índice fuente (.md de los tomos, o `csjn_editorial_indice_partes.csv`/`secciones_indices.csv`) + `construir_catalogo.py` + `cruzar_catalogo_y_mapa.py`. **Arriola sigue siendo caso testigo** (leading case, inconstitucionalidad art. 14, 2º párr., ley 23.737), pero por bug de pipeline, NO por límite del índice.
**Fork RESUELTO (H109) → ni (i) ni (ii): rama (i') recorte del INICIO del bloque del índice.** Leído el `.md` fuente (LibroVol332_3.md), la entrada del índice de actor es `Arriola, Sebastián y otros: p. 1963.` — limpia, con ancla `: p.` (sin «s/ causa 9080»; eso era reconstrucción del prompt, no la fuente — lección H108 reincidente). El parseo de línea NO falla y el cruce no machea por carátula (cruza por `(tomo,página)`, nunca dropea filas). Causa raíz real: la portadilla repetida `INDICE POR LOS NOMBRES DE LAS PARTES` aparece A MITAD del listado «A» (L34087, entre «Automotores Saavedra» y «Autotransportes Andesmar»); `detectar_secciones` toma esa primera ocurrencia como inicio del bloque, y `extender_inicio_indice_nombres` (fix v15) NO lo rescata porque su **Validación 1 exigía que la línea previa a la «A» sola estuviera en blanco** — pero en tomos 331-334 el listado arranca con el header de subsección `Por nombre del actor` justo encima de la «A». La validación abortaba y se recortaban todas las entradas tempranas de la «A» (Arriola, Acosta, Astiz, Alsogaray, Apablaza…). Diagnóstico cuantitativo: A-fracción del catálogo (inicial del primer nombre) 1-4% en 331-334 vs 8-19% normal.
**Fix aplicado (H109):** `construir_catalogo.py` v1.0→1.01. (1) `RE_SUBSECCION_NOMBRES` (`^Por\s+nombre\s+del\s+(?:actor|demandado)\s*$`, IGNORECASE); (2) Validación 1 de `extender_inicio_indice_nombres` acepta línea previa vacía O header de subsección; (3) filtro de `RE_SUBSECCION_NOMBRES` en `parsear_indice_nombres` (anti-polución de carátulas — limpia el residual «Por nombre del demandado …» de B009). Validación con código real (A/B old↔new sobre LibroVol332.3): 481→515 entradas, 1963 capturado, 0 páginas perdidas, 1 polución eliminada; A-fracción 331-334 → 12.9/10.4/7.9/12.7%. Re-golden: catálogo 5862→6145 ids (+283 = **28 B115 en 331-334** [331:12, 332:8, 333:2, 334:6] + 255 tomo 335 incorporado al corpus, NO atribuible a B115); `csjn_casos` 5862→**5890** (+28; los 255 de 335 caen por `pagina_no_en_mapa`). Swallow roto: `332_p1960` (Massuh) apertura 2→1 / dispositivo 2→1, `case_name_cuerpo` deja de ser la carátula de Arriola; `332_p1963` (Arriola) caso propio 1/1, dueño de su carátula; `332_p2043` (Pérez) intacto, no absorbido. QA de los 28: 27 localizados `ok` (apertura=1), 1 (Astiz 334_p1063) `sin_mapa`→B116. FP de `es_queja`: 332_p1960 y 331_p856 → `es_queja=0` (caídos); 343_p1987 sigue `=1` (tomo no recortado, mecanismo lado-cuerpo → B116). check_regresion [FAIL] consciente (+28 casos, rangos cambiados, tomo 335). golden NO re-sellado en H109 (deuda); **re-sellado en H110** junto con B116 (estado combinado B115+B116, check_regresion [CLEAN] 4/4; hashes en `_manifest.json` al regenerarlo).
**Estado del fix:** aplicado (CERRADO H109).
**Referencias cruzadas:** H108, H109. Familia B009 (casos perdidos; mecanismo distinto del B009 original = tomos 331-334). B077 (fronteras de caso). B116 NUEVO (lado cuerpo: `pagina_no_en_mapa`, complementa este fix). Downstream: 2/3 FP de `es_queja` (332_p1960, 331_p856) cayeron; el de 343_p1987 va a B116. Sin ID histórico.

### B116 — `pagina_no_en_mapa`: páginas-apertura-de-sección sin header en el mapa (familia B009, lado cuerpo) — CERRADO H110

**Componente:** detectar_paginas / mapa (`mapa_paginas.csv`) — cruce/parser aguas abajo.
**Origen / fuente del diagnóstico:** H109 (descubierto al dimensionar y cerrar B115).
**Causa raíz (confirmada contra la fuente, H110):** las **páginas de apertura de sección** del tomo (cada mes + Acordadas/Resoluciones) **suprimen el running-head superior** `NNNN / DE JUSTICIA DE LA NACION / 33X` (convención tipográfica de página de apertura): el cuerpo arranca con un banner de sección en mayúsculas (`OCTUBRE`, `NOVIEMBRE`…) seguido del título del primer fallo. `detectar_paginas` keya *exclusivamente* en una línea `== tomo` con entero vecino, así que no emite header para esas páginas → no entran al mapa → el cruce las marca `pagina_no_en_mapa` y el parser las descarta. Verificado leyendo `LibroVol334.3.md`: páginas 1063 (Octubre, además inicio de chunk), 1143 (Noviembre), 1659 (Diciembre) sin el triple, con banner. (Corrección al prompt H110: el banner de 1143 es NOVIEMBRE, no Diciembre — el TOC del tomo venía con OCR sucio.)
**Diagnóstico / evidencia:** cruce con catálogo v1.01: tomos 331/332/333/334 = **11 `pagina_no_en_mapa` cada uno** (44 total), sistemático y acotado. Simulación de blast radius (mapa+catálogo, H110): los 44 candidatos están **todos** en 331-334, 0 fuera; los 15 tomos restantes (329-330, 337-349) sin páginas de catálogo faltantes → intactos por construcción.
**Fix aplicado (H110):** `detectar_paginas.py` v1.0→**v1.01**. Interpolación de headers sintéticos en páginas-apertura-de-sección, con tres guardas: (1) **guiada por catálogo** — `cargar_paginas_catalogo()` lee el set de `pagina_inicio` por tomo; solo se interpola una página que el catálogo espera (descarta colaterales sin caso, p.ej. 334_p1658, y aperturas de índice como 1923); (2) **anclada al banner** — `RE_BANNER_SECCION` (12 meses + ACORDADAS/RESOLUCIONES); el `linea_header` sintético apunta a la línea del banner, que cumple el rol estructural de la línea-tomo (última antes del título) → `linea_inicio == linea_header`, título en `+1`, igual que los `ok`; (3) **región file-local** — `interpolar_secciones()` solo emite en hueco interior (entre dos headers del mismo archivo) o abridor de chunk (`P == min_detectado − 1`). Trazabilidad: `mapa_paginas_inferidas.csv` (las sintéticas) y `mapa_paginas_sin_banner.csv` (páginas de catálogo en región resoluble sin banner — red de cobertura). Schema del mapa intacto (4 cols) → `cruzar` sin cambios.
**Validación (H110):** detectar_paginas → **44 inferidas** (11/11/11/11), **sin_banner=0** (las 41 no vistas en diagnóstico también tenían banner). Cruce: `pagina_no_en_mapa` 299→255 (los 44 de 331-334 a 0; 335 intacto en 255). Astiz `334_p1063` → `status_localizacion=ok`, `linea_inicio=54` (banner OCTUBRE en idx 53, título en 54), `outcome=improcedente` preservado, voto unánime 4 jueces, por_ello/considerando completos. check_regresion perímetro confinado a **331-334**: comparación por clave golden↔nuevo = 0 nuevos / 0 desaparecidos / **84 modificados = 21/tomo** (11 recuperados `pagina_no_en_mapa*`→`ok` + ~10 vecinos cuyo `linea_fin` se corrigió al aparecer el borde de sección — bonus: se arregló el bleed-through, p.ej. 331_p373 dejaba de sangrar a la sección siguiente), **0 fuera de 331-334**. Editorial +1 solo en 331 (14→15) = afloramiento de B115 (el golden era pre-B115; `331.1` recupera su sección `acordadas`), coherente. Outputs: mapa 46936→46980 (+44), fallos_localizados `pagina_no_en_mapa` 299→255, csjn_casos 84 mod, votos 27615→27639 (+24), zonas 141054→141451 (+397), editorial 151→152 (+1). Re-golden consciente + baseline re-sellado (resuelve de paso la deuda del re-sello de H109): check_regresion [CLEAN] 4/4 con el estado B115+B116.
**Estado del fix:** aplicado (CERRADO H110).
**Referencias cruzadas:** H109 (diagnóstico), H110 (cierre). Familia B009 (lado cuerpo; complementa B115, lado índice). **No incluye:** 343_p1987 (tomo 343 = 0 `pagina_no_en_mapa`; NO era B116 — su FP de `es_queja` tiene otra causa, queda pendiente aparte) ni 335-336 (excluidos hasta tener fuente confiable/legible; siguen pendientes, ver H079/H080/H088). Sin ID histórico.

### B117 — Zona `epilogo` absorbe la cola del considerando (cuerpo) a mitad del bloque

**Componente:** parser (zonificación cuerpo/epilogo en `csjn_casos_zonas.csv`).
**Origen / fuente del diagnóstico:** H112 (observado al revisar `329_p595` en el explorador).
**Causa raíz:** `hipotesis_no_verificada` — a partir de cierta línea del considerando, la zonificación cambia `cuerpo`→`epilogo` cuando el considerando todavía sigue; luego retoma bien (dispositivo, firma correctos). Falta leer el `.md` fuente para localizar el disparador (candidatos: un patrón de cierre/footer o `Buenos Aires, <fecha>` que aparece DENTRO del considerando largo y dispara epilogo temprano; o efecto de `fin_extendido_pag_compartida`/borde de página).
**Diagnóstico / evidencia (caso testigo `329_p595`):** contencioso_administrativo (CNACAF Sala III), revoca, unánime 6, `status_fin=fin_extendido_pag_compartida`, `pista_fin=caratula_siguiente`, líneas 22432–23320 de `LibroVol329.1.md`. Zona `epilogo` = **731 wc en 3 segmentos**, capturando la cola del considerando 7º (discusión de la resolución 208/98 / FEDEI), cortada mid-word «…(FEDEI), ot». `cuerpo` 3249 wc vs `wc_considerando` 3894 → la diferencia (~645) es coherente con texto de considerando sangrado a epilogo. Dispositivo y firma detectados OK, `outcome=revoca` correcto: el bug es SOLO la frontera cuerpo→epilogo, no la cascada de dispositivo.
**Cuantificación (H155, vía la capa de partes):** dimensionado sobre `csjn_casos_epilogo.csv`: **478 zonas con wc>200 (11% de 4345), 205 >1000, 60 >3000, max 19788** (mediana de un epílogo limpio = 58 wc). **NO corrompe la derivación de partes** — `RE_MARK_REC` ancla a inicio de línea + case-sensitive, así que el cuerpo arrastrado no matchea; verificado en Mazzeo/Riveros (330_p3248), ALITT (329_p5266) y Estado Nacional (340_p257) → 3/3 footer correcto al final de la zona inflada. Riesgo de derivación real = 80 zonas con ≥2 marcadores anclados, triadas 53 multi-recurrente / 16 multivoto / 11 come-varios-casos (segmentación, familia B009; ~4 con partes distintas a recodear). Techo del fix (recupero de partes) = **189 fallos de MÉRITO sin zona epílogo** (los 1163 sin-zona no-mérito = ausencia esperada: art.280=229 etc.).
**Estado de verificación:** `confirmado_cuantificado` (478 zonas, H155; antes `confirmado_caso_testigo` con `329_p595`). Generalidad verificada — transversal al corpus, ~7-20% por tomo, sin corte de época.
**Validador propuesto:** el explorador YA tiene el filtro «⚠ Epílogo > 500 wc» (`outlier_epi`) → población candidata = casos con `wc_epilogo > 500`; dimensionar ahí, cruzar con `status_fin=fin_extendido_pag_compartida`, y leer el `.md` de una muestra con `extraer_caso.py` (regla M15: validar sobre texto completo, no sobre el CSV truncado).
**Impacto:** las zonas alimentan el word-count por zona (módulo 8 del análisis, H2/H5). Si la cola del considerando cae en epilogo, `wc_considerando`/`wc_cuerpo` quedan subcontados y `wc_epilogo` inflado — justo en casos de doctrina larga, que son los de mayor valor para la tesis.
**Constancia H179 (post-cierre) — MECANISMO LOCALIZADO EN CÓDIGO (pendiente de testigo en disco):** lectura del zonificador (parser.py L2722-2850) + `RE_DATOS_PARTES` (L1890) sobre las selecciones del explorador (wc_epilogo>500: 299 casos, 93% `fin_extendido_pag_compartida`; wc_residuo>300: 793, sesgo tomos 337+, síntoma APARTE familia B089/B096). Dos fallas que se combinan: **(a) guard envenenado por el residuo** — el gate del `epilogo_marker` («solo después de firma/voto/dispositivo») evalúa las anclas del BLOQUE ENTERO (Pasada 1), y en `fin_extendido_pag_compartida` el bloque arranca con la cola del caso ANTERIOR (firma+pie incluidos) → el guard está satisfecho desde la línea cero del caso propio (la Pasada 3 reclasifica el residuo DESPUÉS de que las anclas ya se juntaron); **(b) `^Recurso` con `re.I` demasiado ancha** — matchea cualquier línea que el wrap del OCR deje empezando en «recurso…» dentro del considerando (frecuente en doctrina larga), flipeando cuerpo→epilogo a mitad del bloque hasta la próxima ancla («luego retoma bien» del testigo 329_p595 = exactamente esto). El sesgo dictamen de los peores casos (11/12 del top) sería confusor (más páginas → más fin_extendido), no causa. Gramática estricta del pie real YA existe y está validada: `RE_PIE_START` de extraer_epilogos (`Recursos?|Queja … interpuest|deducid … por`) — fuente única candidata para el fix (Gate 3). **Validador para H180:** `poc_b117_disparador.py` — para los 299, tomar el PRIMER span epilogo de zonas.csv, leer la línea real del .md donde arranca, clasificarla (pie genuino por RE_PIE_START vs «recurso narrativo») + verificar anclas-firma pre-apertura (envenenamiento (a)). MAJOR al fixear: bordes de ~478 zonas → wc_* de casos.csv → re-golden adjudicado + re-derivar epilogo→partes + re-sello (ciclo con correr_pipeline --consciente/--regolden).
**Estado del fix:** no diseñado. Toca el zonificador (parser) → re-golden. **ROI acotado por H155:** el over-capture NO corrompe partes; la justificación del fix es higiene de `wc_*` por zona (módulos de tesis H2/H5) + recupero de ≤189 fallos de mérito-sin-zona. Decisión de valor (base limpia / modelo SCDB), no de ROI de Eje B. Próximo paso barato antes de tocar el parser: muestrear los 189 (¿footer recuperable o per curiam genuino?).
**Referencias cruzadas:** H112, H155. Elevado a deuda estructural en **M31** (delimitación de zonas = escalabilidad/modularidad). Posible familia con B045 (arrastre) / B077 (cola editorial absorbida) / el outlier de epilogo. Sin ID histórico.

### B118 — `por_ello`/dispositivo truncado por running-head de página (pierde la disposición de fondo) — CERRADO H126

**Fix aplicado (H126):** subsumido por el skip de `_barrer` (M21 Fase 1, parser v19.0). El presupuesto del chunk lo gastaban el banner Y las líneas en blanco del OCR a su alrededor; saltear las vacías sin contarlas libera el chunk hasta el `.` real y recupera el verbo de fondo pasado el corte. Las transiciones acceso→fondo del corpus (otro/procedente → confirma/revoca/hace_lugar, ~12 en casos + 44 en votos denormalizados) son exactamente este bug. Validación: inspector direccional + spot-check (487 `por_ello` extendidos, 0 pérdida) + check_regresion [CLEAN]. Ver B122/M21.

**Componente:** parser (extracción de `por_ello_text` / borde de página).
**Origen / fuente del diagnóstico:** H118 (PoC de disposición M20: casos de fondo sin verbo dispositivo legible).
**Causa raíz:** **confirmada H125** (familia del presupuesto de `_barrer`, igual que B122). El `por_ello` se corta en el salto de página: el running-head editorial («1049 DE JUSTICIA DE LA NACION 329» / «FALLOS DE LA CORTE SUPREMA») queda pegado al final del texto capturado y el verbo de disposición que sigue en la página siguiente se pierde. Testigos: `329_p1045` (`por_ello` termina en «…recurso extraordinario 1049 DE JUSTICIA DE LA NACION 329»); `329_p1480` («dejándose sin efecto la sentencia» seguida de «1484 FALLOS DE LA CORTE SUP…»).
**Diagnóstico / evidencia:** `confirmado_cuantificado` — sobre el universo de fondo (`is_merit_decision=1`, 2941), el PoC de disposición (v3) marca **33** casos `por_ello_cortado` (regex de header al final del texto). Límite superior de los que pierden disposición por borde de página; la mayoría tiene la disposición ANTES del header (recuperable corriendo el borde).
**Estado de verificación:** `confirmado_cuantificado` (33 sobre fondo; testigos 329_p1045 / 329_p1480).
**Validador propuesto:** dimensionar `por_ello` que terminan en running-head (`(DE JUSTICIA DE LA NACION|FALLOS DE LA CORTE)\s*\d*\s*$`); leer muestra con `extraer_caso.py`; arreglar el borde para arrastrar el texto post-header hasta el fin real del dispositivo (regla M15: validar sobre `.md` completo).
**Impacto:** subcuenta la disposición de fondo en M20 (queda fuera del `por_ello`) y puede truncar `outcome` en página compartida. Acotado (~33 de fondo), pero toca el campo de mayor valor del refactor.
**Estado del fix:** validado en PoC (H125, vía el skip de M21), integración H126. El skip recupera el verbo de fondo pasado el corte — las transiciones acceso→fondo del PoC (procedente/hace_lugar/mal_concedido → revoca/confirma/hace_lugar) son exactamente este bug.
**Referencias cruzadas:** H118, H125. Familia B104 (running-heads), B117 (borde de zona). M20 (disposición). DISENO_SCDB_corpus §1. H119: 12 casos marcados `flag_revisar_fuente` en el frame M20 n=300 (subconjunto del universo afectado). Sin ID histórico.

### B119 — `is_merit` sobre-incluye NO-fondo (capa disposición) — CERRADO H121

**Componente:** parser (`classify_outcome` + `is_merit_decision` + `es_originaria`).
**Origen / fuente del diagnóstico:** H119 (validación ciega M20, gate `cod_es_revision_fondo` sobre el frame n=300).
**Causa raíz:** `hipotesis_no_verificada`. El detector de revisión de fondo cuenta como merit casos de queja que resuelven acceso/admisibilidad (no el fondo sustantivo de una sentencia anterior). Probable interacción con la sobre-inclusión de quejas en la cadena de outcome (familia B109/B110).
**Diagnóstico / evidencia:** `confirmado_cuantificado` (H120, gold completo n=300). GATE accuracy 0,907; **19 FP** (parser=fondo / gold=no): **6 quejas, ~4 originarias, 3 competencia, 1 cautelar, resto mixto**. Hallazgo clave: NO es solo un problema de quejas — `is_merit` toma como fondo varias categorías de no-fondo (competencia, cautelar, originaria). El fix debe excluir esas familias, no solo gatear quejas. 9 FN (parser pierde fondo real).
**Estado de verificación:** `confirmado_cuantificado` (H120).
**Validador propuesto:** `validar_H120.py` bloque GATE (confusión + FP×es_queja/is_originaria) sobre planilla completa. HECHO.
**Estado del fix:** **APLICADO H121 (parser v18.26).** Tres edits encolados en una sola re-corrida + re-golden:
- **#1** — guard `is_merit = int(outcome in MERIT_OUTCOMES and not is_originaria)`: las originarias no son revisión de fondo.
- **#2** — `_unhyphenate` sobre el cuerpo de `es_originaria`: «Corte Su- prema» rompía `RE_COMPETENCIA_ORIGINARIA` y comía competencias originarias.
- **PASO 2 (capa disposición)** — 4 detectores pre-cascada en `classify_outcome` (corren ANTES de `OUTCOME_PATTERNS_DISPOSITIVO`, donde el verbo de merit ganaba por posición): `RE_DISP_NULIDAD_CONCESION` (nulidad/auto de concesión + denegatoria del REX → label nuevo `nulidad_concesion`, distinto de la `nulidad` de fondo), `RE_DISP_CAUTELAR` (revoca/deja sin efecto medida cautelar → `cautelar`), `RE_DISP_COMPETENCIA` («resulta competente para conocer» / «tomar intervención en el conflicto» → `competencia`), `RE_DISP_INOFICIOSO` («inoficioso emitir pronunciamiento» → `abstracto`). Dos labels nuevos (`cautelar`, `nulidad_concesion`) agregados a `OUTCOMES_NO_FALLBACK_280`; ninguno entra a `MERIT_OUTCOMES`.

**REVISITADO H165 (→ B136):** el guard #1 (`not is_originaria`) excluye la originaria DE FONDO además de la no-fondo. Se construyó —junto con el golden de M20— sobre la premisa (FALSA) de que SCDB excluye la jurisdicción originaria; el codebook SCDB v2021_01 (§17) la INCLUYE (Marbury entra). Medido en disco (H165): de 546 originarias, 167 son de-fondo (96 hace_lugar + 68 rechaza + 3 otras; 153 con Provincia/Estado en carátula) y hoy quedan indebidamente fuera de mérito. El fix NO es revertir #1 sino CONDICIONARLO a la disposición (originaria-no-fondo sigue excluida; originaria-de-fondo entra). Es cambio del eje más usado → re-golden + re-κ. Ver **B136**.
**Validación (H121):** recall-safety n300 = **0 disparos sobre gold=sí** (no crea FN). Gate **0,907→0,953** (FP 19→5, FN=9 sin cambios). Recupera 11 FP: competencia(5) 339_p490·347_p360·329_p2645·331_p989·340_p431, cautelar(1) 342_p2399, nulidad_concesion(4) 329_p1626·348_p1717·329_p472·346_p439, inoficioso→abstracto(1) 348_p1499. Corpus completo: `competencia` 877, `abstracto` 146, `nulidad_concesion` 30, `cautelar` 4. **Proyección sandbox == corrida real** (medido sobre `csjn_casos.csv` post-fix).
**FP residuales (5, deferidos a sus arcos, NO fallas de detector):** `329_p1936` (gold-edge: confirma sobre incidente de revisión, codificado no-fondo — irreducible), `329_p2856` (queja de cumplimiento de fallo previo), `343_p646` (recurso directo, reenvío procesal), `344_p1283` (competencia vía «radicación ante el juzgado que corresponda», cue débil — duro), `346_p1241` (remisión total al dictamen: la disposición vive en el dictamen, no en el `por_ello` — va al deriver de dictamen).
**FN (9, sin cambios):** 6 de zona → **B122** (`330_p1907`, `332_p2625`, `334_p941`, `334_p1081`, `344_p2393`, `345_p583`; `334_p1081` reclasificado de "limpio" a frontera de captura); 3 de detector → **B120** (merit-recall).
**Fragilidad conocida (DEUDA viva):** el guard inoficioso asume que un `revoca` acompañante es instrumental a la abstracción. Un mixto inoficioso+merit sobre puntos SEPARADOS (tipo `332_p2208`, hoy con el inoficioso en el dictamen y no en el `por_ello`) sería FN si el «inoficioso» cayera en el dispositivo. 0 casos en n300. Mismo punto ciego del hifenado probable en `es_queja` / cuestión federal (no medido).
**Referencias cruzadas:** H119 (diagnóstico). H120 (cuantificación, gate 0,907 sellado). H121 (fix). B120 (merit-recall, FN), B122 (zona, FN). Familia B109/B110 (quejas — confirmado que NO eran la causa: 69/114 quejas son merit). Sin ID histórico.

### B120 — Merit-recall: precedencia/scope de la cascada pierde fondo en dispositivos mixtos

**Componente:** parser (`classify_outcome`, orden de `OUTCOME_PATTERNS_DISPOSITIVO`).
**Origen / fuente del diagnóstico:** H121 (los 3 FN "de detector" del gate M20, tras separar los 6 de zona).
**Causa raíz:** `confirmado_caso_testigo`. La cascada matchea por ORDEN de patrón, no por posición en el texto. En dispositivos mixtos un verbo de rechazo/secundario le gana al de fondo: (a) `desestima` está en posición 2 y `rechazar`(inf) en 14, mientras `deja_sin_efecto` está en 26 y `hacer lugar`(inf) en 20; (b) sub-issue de scope: el patrón `desestima` («se desestima…») dispara sobre «se desestima la **demanda**» — que es MÉRITO (rechazo del reclamo de fondo), no gate de la vía. Ya anotado en el comentario B109 de `classify_outcome` como diferido al "refactor etapa/disposición+parte (M20)".
**Diagnóstico / evidencia:** 3 testigos (n300): `330_p4592` → `rechaza` (rechazar-inf le gana a hacer-lugar + dejar sin efecto la sentencia); `338_p40` → `desestima` (se desestima la demanda tapa deja sin efecto la sentencia apelada); `344_p3394` → `desestima` (se desestima la queja tapa procedente + confirma la sentencia — el mixto queja+REX). **Banco cuantificado corpus-wide (H122):** la corrida de `derivar_recursos` sobre 5890 dejó **166 casos no-merit con verbo de disposición** (gate=no pero el `por_ello` dispone) — candidatos directos a gate-FN. B120 se diseña mirando esos 166, no adivinando.
**Estado de verificación:** `confirmado_caso_testigo` (3/3, n300) + banco corpus-wide 166 (H122).
**Validador propuesto:** guard de precedencia-mérito pre-cascada (verbo de mérito gobernando «la sentencia apelada/recurrida/impugnada» o «procedente el recurso extraordinario»), PUESTO DESPUÉS de los detectores de disposición B119. FP-safety n300: 119 gold=sí (recupera los 3 FN), 7 gold=no — pero los 7 son 4 ya-capturados por B119 + 3 ya-FP → **0 FP nuevos en n300**. Proyectaría gate 0,953→0,963 (FN 9→6).
**Estado del fix:** **diseñado, NO aplicado.** Riesgo: el guard es ANCHO (matchea 126/300), y el gold solo cubre 300/5890 → superficie de regresión corpus-wide no validable con el gold actual. A diferencia de B119 (anclas angostas), un cambio de precedencia ancho puede meter FP en los otros 5590. Plan: aplicar como arco propio con revisión del diff de `check_regresion` corpus-wide antes de re-goldear.
**Referencias cruzadas:** H121. B119 (los detectores de disposición deben correr ANTES). Comentario B109 en `classify_outcome` (diferimiento original a M20). Sin ID histórico.

### Capa-fuente `es_queja` — tail débil y capa considerando DIFERIDOS (H108)

**Componente:** parser (`classify_queja`).
**Hecho (H108):** capa-fuente por carátula implementada (parser v18.23). `classify_queja(por_ello_text, caratula_text="")` detecta la vía en la carátula (`RE_CARAT_QUEJA` = `recursos?\s+de\s+hecho\s+(?:deducidos?|interpuestos?)\s+por` + `RE_CARAT_CITA` como guard de cita), además del `por_ello`. Solo ancla fuerte. es_queja 2056→2281 (+225, 0 flips 1→0); queja_resultado sin_clasificar 38→263. Precisión de flip 222/225 = 98,7% (7 fallos leídos: 4 TP de tercero + 3 FP downstream de B115).
**Diferido:** (1) tail de ancla débil (~11 casos carátula-ritual sin la fórmula fuerte); (2) capa considerando (quejas nombradas solo en el considerando — sigue abierta desde B110).
**Estado del fix:** parcial (ancla fuerte hecha; tail + considerando diferidos).
**Referencias cruzadas:** H108. B110 (capa-fuente abierta). B115 (los 3 FP). Sin ID histórico.

### Frente B — `materia` (y su proyección a `secretaría` de origen)

**Componente:** variable NUEVA de salida (taxonomía + extracción multicapa). Frente de feature, NO un bug. Históricamente postergado (H082; CSV de referencia del Anuario con secretaría/materia en H083).
**Norte / modelo:** SCDB (Supreme Court Database). Su variable `issue` (260 valores) anidada en `issueArea` (14 áreas grandes) es el molde directo: taxonomía de DOS niveles, materia gruesa + submateria, con reglas de scope por valor documentadas. Las party variables del SCDB (petitioner/respondent) validan usar las partes como señal secundaria. Su separación case-centered / justice-centered ya está replicada acá (casos/votos). OJO: el SCDB CODIFICA A MANO con reglas — da el molde del PRODUCTO (qué variables, qué valores, qué reglas) y el estándar de reliability, NO el método de extracción automática del OCR. Refs: `scdb.la.psu.edu/online-codebook`, `/online-codebook/issue/`, codebook PDF.
**Diseño accionable (por capas, ordenado por limpieza de señal):**
- **Capa 1 (alta precisión, barata) — IMPLEMENTADA H112:** `tribunal_origen` → fuero → materia, lookup de reglas ordenadas sobre la columna limpia (post-B114). Vive en `scripts/pipeline/derivar_materia.py` v1.0 (módulo de derivación standalone, NO en el parser — mismo criterio REE que `generar_manifiesto.py`: lookup determinístico sobre output ya escrito, re-corrible por capa sin reparsear). Escribe el sidecar **`output/parser/csjn_casos_materia.csv`** keyed por `caso_id_canonico` (cols: materia / materia_capa / materia_fuente; LF; join 1:1 con casos, 5890 filas, 0 huérfanos). **Cobertura (sobre 5697 fallos): capa1 2474 (43,4%)** — civil_comercial 746, contencioso_administrativo 618, penal 414, laboral 374, previsional 292, electoral 30. Reglas para fuero nacional/federal especializado (del Trabajo→laboral; Seguridad Social→previsional; Contencioso Administrativo→CA; Casación Penal/Criminal y Correccional/Penal Económico→penal; en lo Civil/Comercial/Civil y Comercial Federal→civil-comercial; Electoral→electoral). Decisión de diseño: `status==originaria` **corta a capa 3 ANTES** de las reglas (capa 3 es dueña de la originaria; en art. 117 el `tribunal_origen` suele ser citado, no apelado) — 0 originaria reclamados por capa 1. Verificado reproducible en máquina del usuario (idéntico al de referencia).
- **Capa 2 (provinciales + SIN_TRIBUNAL) — PENDIENTE, bloqueada por `csjn_casos_textos`:** `pendiente_capa2` = **2732 (48,0%)** de los fallos (provincial/federal-regional + `SIN_TRIBUNAL` sin_marcador). El tribunal NO desambigua → señal secundaria = normas citadas en el considerando (24.241→previsional, LCT/20.744→laboral, 11.683→tributario, Cód. Penal→penal) u objeto/partes. **Bloqueada:** el considerando está truncado a 2000 en el CSV → leer normas exige `csjn_casos_textos` primero (orden H111-01). **Hallazgo H112 (advertencia SCDB confirmada):** `tributario` = 0 en capa 1 — los tributarios suben por la Cámara Cont. Adm. Federal y caen en `contencioso_administrativo`; `tributario` NO es derivable de tribunal, es materia de capa 2 por norma (11.683 / aduanero), y capa 2 podrá RECLASIFICAR un subconjunto de `contencioso_administrativo`→`tributario`. **Estrategia H112 (capa 1 como set de entrenamiento):** los 2474 de capa 1 tienen materia GROUND TRUTH (determinística del fuero nacional especializado, sede CABA). Minar sobre sus considerandos COMPLETOS (vía `csjn_casos_textos`) los patrones distintivos por materia —normas, partes, keywords de carátula— da un léxico norma/partes→materia DATA-DRIVEN y validado sobre etiquetas reales, que clasifica los provinciales/SIN_TRIBUNAL; combinar con el vocab controlado a mano (las normas obvias). Caveat de transferencia: el lenguaje del fuero nacional puede diferir del provincial (estilos de redacción) → validar que los patrones transfieren.
- **Capa 3 (originaria) — PENDIENTE:** `pendiente_capa3` = **477 (8,4%) = originaria exacto** (capa 1 corta antes, ver arriba). Materia propia (competencia entre Estados, CA federal); regla aparte. `outcome=competencia` (863) ya captura parte del eje.
- **Casos terminales H112:** `sui_generis` = 8 (Jurado de Enjuiciamiento + Consejo de la Magistratura, nación y provincias) → categoría TERMINAL agrupada, SIN label de materia por ahora (decisión del usuario: agrupar no daña; **pendiente de lectura** caso por caso —si hubo cuestión federal / cómo se decidió— antes de darles taxonomía). `residual` = 6: tribunales arbitrales (Bolsa de Comercio, Obras Públicas), 1 typo OCR (`Superior Tribual`), 1 anáfora (`Sala D de la referida Cámara`) — NO es hueco de clasificación. `no_aplica` = 193 (sumarios).
**Observación H112 (validez del corpus, material de tesis):** el 43,4% de capa 1 es el fuero nacional/federal especializado con sede en CABA (CNAT, Civil, Comercial, CNACAF, Casación Penal, Fed. Seg. Social, Nac. Electoral). Su distribución de materia NO replica el ingreso/egreso del Anuario (donde previsional/laboral/penal dominan por volumen de causas repetitivas + 280 masivo): en el corpus publicado civil_comercial (746) y penal (414) superan a laboral (374), con previsional (292) abajo pese a ser de los de mayor ingreso. NO es anomalía: la publicación de tomos es un set CURADO por relevancia (elimina repetidos, remisiones, 280 en masa) → la distribución refleja la DOCTRINA de la Corte (+ la provincial que llega), no el docket. Refuerza el encuadre del corpus como equivalente del SCDB (decisiones con doctrina, no cert denials). El contraste docket-vs-publicado es contrastable contra el CSV del Anuario H083 (ingreso por materia) y es en sí un hallazgo.
**Validación:** taxonomía controlada PRIMERO (vocabulario de materias del derecho argentino, antes de extraer); luego `cod_materia` sobre los n=300 ya codificados (M19) y precision/recall por valor, igual que el titular.
**Proyección a secretaría (terreno del usuario, conocimiento de insider):** materia → secretaría de origen en la CSJN. Dos alertas que el corpus impone: (1) la estructura de secretarías CAMBIÓ en el período (tomos 329–349 ≈ 2006–2025) → la inferencia debe ser TEMPORAL (qué secretaría tenía esa materia en ese año); (2) los provinciales multi-materia son punto ciego también para la secretaría, no solo para la materia.
**Estado:** Capa 1 IMPLEMENTADA (H112). Capas 2 y 3 + validación PENDIENTES. **Integración de capa 1:** (1) `generar_manifiesto.py` v1.1→**1.2** — `csjn_casos_materia.csv` sumado como 6º output + `derivar_materia.py` en la cadena; `--verify` [CLEAN] **55** (HECHO H112). (2) CODEBOOK — documentar `materia` / `materia_capa` / `materia_fuente` (con la nota de que `tributario` es capa 2). PENDIENTE. (3) `csjn_analisis_v4.py` — left-join por `caso_id_canonico` cuando se use materia. PENDIENTE.
**Referencias cruzadas:** H082, H083, H105, H111, **H112**. B114 (pre-requisito, CERRADO). `csjn_casos_textos` (bloquea capa 2). M19 (validación `cod_materia` sobre n=300, una vez estable el set). SCDB. is_originaria / tribunal_origen_status.

#### Avance H113–H115 (capa 2 desbloqueada + Tier 1 + Tier 3)

`csjn_casos_textos` ya disponible (considerando completo); capa 2 desbloqueada. Progresión de `derivar_materia.py`: v1.0 (H112, capa1) → v2.0 (capa2 vocabularios: norma/keyword/parte) → v2.1 (H113, capa objeto) → v3.0 (H114, Tier 1 router de partes→CA) → v3.1 (H114, refinamiento capa1: override CA→tributario por autoridad fiscal) → **v3.2 (H115, Tier 3 co-ocurrencia)**.

- **Tier 3 — motor de co-ocurrencia (H115):** `_meta/vocab_materia/vocab_coocurrencia.csv` (reglas como DATO: signal_a/signal_b/excluye/materia/prioridad/ambito_a/ambito_b). Función `desambiguar_co_ocurrencia(caratula, considerando, vocab)`: una señal polisémica se vuelve ancla cuando co-ocurre con otra corroborante. Se llama (a) en la rama EMPATE antes de devolver `conflicto_capa2` (desempate) y (b) en `sin_ancla` ANTES del trigger Estado→CA. 6 reglas validadas: `tributario_disfrazado` (acc. declarativa EN CARÁTULA + tributo; GT mudo→spot-check ~95%; resolvió const/trib 8→0 y CA/trib 10→9), `corralito_emergencia`→CA (decretos 1570/01·214/02·1606/01 o ley 25.561 + PEN, ambos en carátula; GT 14/14 CA), `accion_civil`+accidente→laboral (GT 93%), `indemniz`+despido excl. empleo público→laboral (GT 90%), `danos`+tránsito excl. resp. estatal→civil (GT 89%), `salud_amparo` (entidad de salud LITIGANTE en carátula + amparo, excl. obra social actora cobrando aportes; GT mudo→spot-check 20/20).
- **Lección de diseño (REE):** la señal de materia vive en la **carátula** (litigante/objeto), no en el considerando completo. Buscar señales débiles (obra social, acción declarativa, alimentos) en el considerando entero contamina vía menciones al pasar y **citas de precedentes** (el considerando cita carátulas ajenas: «X c/ provincia s/ acción declarativa de inconst.»). Por eso `ambito` es POR SEÑAL: la señal-objeto se scopea a carátula; la señal corroborante (tributo) puede ir al considerando. Esto eliminó misfires reales (bazan→penal, spreafico→tasa de justicia, abarca→tarifas, kersich→agua, escribanos→previsional).
- **Familia→civil_comercial (decisión usuario H115):** anclas de objeto en `vocab_objeto.csv` (alimentos, restitución/reintegro de hijo, filiación/adopción/guarda, capacidad/insania/curatela, divorcio/visitas, sucesión; objeto-scoped, GT 83-100%). NO materia nueva: familia es secretaría civil y comercial. `tenencia` pelado descartado (se fuga a penal=tenencia de armas).
- **Relabel originaria:** `pendiente_capa3`→`originaria` (categoría TERMINAL, no «pendiente»; tiene secretaría propia, no es universo de derivación). Cobertura se reporta sobre **universo clasificable = fallos − originaria = 5220**, no sobre fallos. n=477, relabel 1:1.
- **Norma:** frente AGOTADO. Solo 11.723 (Propiedad Intelectual) añadida (GT 6/6 civil). 19.549 (58% CA), 24.065 (33%), 25.156 (mixto) no llegan al piso; ley 1.285 (organización judicial) es ruido ubicuo en el residual.
- **Cobertura H114→H115:** 75,3%→**77,3%** (+104 netos, TODOS auditados). Final: capa1 2315 + capa1_refinado 159 + capa2 1563 = 4037 / 5220. pendiente_capa2 1169 (sin_ancla 1104 + conflicto_capa2 65). Conflictos 83→64. Aditividad ESTRICTA: 0 casos capa1/capa1_refinado cambiaron.
- **Hallazgo honesto (anti-optimismo del prompt):** la meta ~92-94% NO es alcanzable con precisión. El residual (`sin_ancla` ~1100) es mayormente IRREDUCIBLE: amparos genéricos contra PEN, objetos puramente procesales (ordinario, incidente, casación, recurso) sin segunda señal corroborante. Clasificarlos sería ADIVINAR (viola REE). El motor de co-ocurrencia rescata lo que tiene doble señal limpia (~+2pp reales), no infla cobertura.

**Pendientes materia abiertos al cierre H115:**
- **Procedencia de la cadena de materia FUERA del manifiesto:** `derivar_materia.py` NO está entre los 5 scripts sellados; `csjn_casos_materia.csv` y `_meta/vocab_materia/*.csv` NO se hashean. Riesgo: cambios de materia/vocab no quedan en `_manifest.json`. Sumar al manifest: `derivar_materia.py` a la cadena de versiones, el sidecar a outputs, y `_meta/vocab_materia/` a inputs. Estado: no diseñado.
- **Fuga `is_originaria` en const/tributario:** algunos casos dicen «competencia originaria art. 116/117» en el considerando pero `tribunal_origen_status = sin_marcador` → el parser no los marcó originaria y caen al universo clasificable. Cardinalidad chica (~2-6, no cuantificada). Componente: parser. Estado: hipótesis no verificada. Relacionado con la deuda is_originaria post-B010.
- **Lever penal-objeto DIFERIDO:** anclas de objeto→penal evaluadas y descartadas por precisión: extradición (GT 86%), delitos nominados estafa/defraudación/hurto/robo/homicidio/lesiones/abuso (GT 87%), denuncia/averiguación pelada (GT 62%). Las dos primeras quedan por debajo del piso ~90-95% que sostienen salud/tributario/familia. ~62 candidatos en residual. Reabrir solo si se baja conscientemente el piso de precisión penal. Estado: evaluado, no aplicado.
- **Conflicto nuevo `332_p908`** («alonso s/ curatela», causa de competencia): la ancla `curatela`→civil empata con un kw penal preexistente (penal por el conflicto de fuero) → pasó de penal-confiado (H114) a `conflicto_capa2:civil_comercial/penal`. Es más honesto, no menos; efecto colateral aceptado de sumar anclas civiles de objeto.

#### Avance H116 — validación held-out de capa 2 + diseño de la proyección `secretaria`

**Validación held-out (capa 1 como silver-GT de capa 2).** Señales ORTOGONALES: capa1 clasifica por `tribunal_origen`, capa2 por carátula+considerando → capa2 no ve la señal de capa1, no hay leakage. Se corrió `clasificar_capa2` sobre los 2315 casos capa1 y se comparó contra su etiqueta de tribunal (harness ad-hoc `heldout.py`, NO canónico; MIDE, no muta — parser y `derivar_materia.py` v3.2 intactos).
- Cobertura capa2 (emite materia): 1383/2315 = **59,7%** [57,7–61,7]; se abstiene en ~40% (sin_ancla 848 + conflicto 84).
- Accuracy | emite (pred==tribunal): **75,8%** [73,5–78,0]; colapsando predicciones más finas que el tribunal (lesa_humanidad→penal, consumo/cambiario→civil): **78,4%** [76,1–80,5] (granularidad explica solo +2,6pp → el disenso es REAL, no artefacto de la vara gruesa).
- Precisión por valor (cuando capa2 se compromete): previsional 93,3%, civil_comercial 90,4%, laboral 90,1%, penal 87,6%, **CA 68,8%**. Recall: laboral 63,4, previsional 67,1, CA 42,3, civil 37,7, penal 34,1, electoral 0 (capa2 no tiene vía electoral).
- Lectura: capa2 es **alta precisión / bajo recall POR DISEÑO** (la abstención es la política REE de H115 — el residual `sin_ancla` es irreducible, forzarlo = adivinar).

**Dos fugas de precisión cuantificadas (candidatas a refinar, NO aplicadas):**
- **Sobre-ruteo Estado→CA:** 282 casos no-CA de capa1 terminaron etiquetados CA por el trigger genérico. Es el sumidero de precisión de CA (68,8%). Candidato #1 de refinamiento (exigir corroboración antes del genérico). Riesgo ALTO: roza originaria + refinamiento fiscal + co-ocurrencia → exige re-validación completa. Componente: `derivar_materia.py`. Estado: no diseñado. **CONFIRMADO H117 (gold):** CA precisión 68% (27/40) ≈ 68,8% silver — sumidero real. Además recall CA 42%: 10 originaria + 11 pendiente_capa2 codificados CA con parser mudo → la **abstención** (no solo el sobre-ruteo) pierde CA. Candidato #1, ahora con vara fina para validar el refinamiento.
- **`salud_amparo` desborda:** las 19 veces que predijo `salud` sobre capa1, las 19 estaban mal (18 civil, 1 CA). Misfire chico pero 100% en held-out → apretar la regla. Estado: no diseñado. **ACTUALIZADO H117 (gold):** la alarma era artefacto del held-out (capa1 NO contiene salud → toda predicción salud sobre capa1 cuenta mal por construcción). El gold mide **salud precisión 95% (19/20)** sobre datos reales → `salud_amparo` es net-sano en su territorio (capa2 provincial). DE-PRIORIZADO (el refinamiento solo evitaría el sobre-disparo sobre el subconjunto capa1, ganancia marginal).

**Frontera AFIP/DGI (NO es bug — ambigüedad real):** las confusiones previsional↔tributario (24) y previsional↔CA (25) son el límite verdadero: AFIP/DGI recauda impuestos Y aportes. Verificado con datos: aduana/ANA 48/67→tributario (NO seguridad social, corrige un recuerdo del usuario); AFIP 98/128→tributario + 8→previsional; DGI 111/170→tributario + 16→previsional. El silver-GT grueso no las adjudica; las resuelve solo el gold humano.

**Límite estructural del held-out:** la vara capa1 NO contiene tributario/consumo/salud/ambiental/cambiario/lesa_humanidad (materias EXCLUSIVAS de capa2) → el ejercicio valida el SOLAPAMIENTO, es CIEGO a las materias finas. Por eso el gold (`cod_materia` sobre los 300, ya planeado en este frente, ver arriba) es el ÚNICO modo de medirlas.

**M19 NO codifica materia (aclaración):** los 7 campos `cod_*` de `planilla_consolidada_MARCO_A_v18_15_n300.csv` son outcome/estructurales; no hay `cod_materia`. "Validar materia contra M19" NO existe como opción. El camino real: held-out (HECHO) + GOLD nuevo reusando la SRS de los 300.

**Diseño de la proyección `secretaria` (decisión usuario, refina/precisa el párrafo "Proyección a secretaría" de arriba):** el organigrama de secretarías es una **capa de agrupamiento administrativo MUTABLE**, no una ontología de temas (Nº5 suprimida→Consejo de la Magistratura; Consumo Ac.36/2015, Ambiental 8/2015, Penal Especial Ac.18-19/2024 POSTDATAN buena parte del corpus 2006–2026). Decisión: `materia` queda **sustantiva e intacta**; `secretaria` = variable DERIVADA (materia→secretaría actual vía organigrama), foto ACTUAL, NO time-indexed (la versión temporal del párrafo de arriba se descartó por costo, opción B rechazada). previsional ≡ Seguridad Social (solo naming). Mapeo: Nº1 civil_comercial · Nº2 previsional · Nº3 penal · Nº4 CA · Nº6 laboral+**salud** · Nº7 tributario+cambiario · Ambiental · Consumo · Penal Especial=lesa_humanidad · Originarios. Sin hogar (transversales): **constitucional→`transversal`** (todas las secretarías tratan lo constitucional; es competencia de la Corte, salvo arbitrariedad); **electoral→`fuero_externo` / PENDIENTE_VERIFICAR** (28/30 vienen de la Cámara Nacional Electoral, fuero especializado externo sin secretaría interna; el usuario chequea el ruteo interno). `secretaria` es DERIVADA, no observada — el corpus tiene `tribunal_origen` (inferior), no la secretaría interna de la Corte; documentarlo así en el CODEBOOK.

**FP detectado al pasar:** `Edenor S.A. / Provincia de Buenos Aires` clasificado `electoral` por `regla:electoral` (capa1) — huele a falso positivo de la regla; revisar al armar el gold. **CONFIRMADO H117 (gold):** es FP — el caso es `remoción de electroductos` (CA) y «electroductos»/«Edenor» dispara `regla:electoral`. Anclar la regla electoral a partido/CNE/comicios, no a la raíz «electr». Estado: no diseñado.

#### Avance H117 — GOLD de `materia` (codificación ciega)

Ejecutado el GOLD planeado (opción b): `cod_materia` a ciego por Claude (misma metodología que M19) sobre 406 casos = 300 SRS de M19 (Marco A) + 106 oversample por valor (Marco B, min(20,N), seed 20260531). Bundles ciegos = carátula + considerando + por_ello, **sin `tribunal_origen`** (señal de capa1 → evita circularidad). MIDE, no toca pipeline (`derivar_materia.py` v3.2, outputs intactos). Productos en `estadisticas/validacion/`: `muestrear_materia.py` (sampler), `muestra_clave_materia_v18.15.csv`, `cod_claude.csv`, `planilla_codificacion_materia_v18.15_CODIFICADA.csv`, `METRICAS_materia_v18.15.txt`, `HALLAZGOS_validacion_materia_v18.15.md`.

- **Titular Marco A (SRS → estimador del corpus de fallos):** cobertura 74,1% [68,0–79,4]; **exactitud|emite 81,3%** [74,7–86,5]; exactitud global 60,3% [53,7–66,5].
- **Por capa (unión):** capa1 (tribunal→fuero) 82,5% [75,0–88,2]; **capa2 (cascada) 66,1%** [57,2–74,0] → confirma capa2 como frente débil (−16pp).
- **Precisión / recall por valor (unión, AMBIGUO excluido):** previsional 95/100, salud 95/63, penal 94/50, laboral 89/84, tributario 87/62, electoral 80/86, civil_comercial 71/62, contencioso_administrativo 68/42, ambiental 65/85, consumo 33/83, lesa_humanidad 33/50, cambiario 25/100, constitucional 0/0.
- **AMBIGUO 104/406 (25,6%)**, fuera del denominador (igual que titular M19), concentrado en originaria/provincia con considerando de trámite y snippet corto. Útiles 302.

**Hallazgos nuevos (frentes; NO se tocó el pipeline):**
- **`constitucional` plano inservible (0/0):** valor transversal; parser=constitucional→cod tributario(3)/CA(2), cod=constitucional→parser CA(4)/electoral(2)/lesa(1). Coherente con la decisión `constitucional→transversal` de la proyección secretaría: como materia plana no funciona para ninguno de los dos coders. Repensar (flag aparte o derivación por sub-objeto). Estado: no diseñado.
- **`consumo` sobre-dispara (precisión 33%):** capa2 consumo→civil_comercial ×6, consumo→CA ×4. Recall alto (83%) pero muchos FP → apretar gatillos norma/keyword 24.240. Estado: no diseñado.
- **`cambiario` (25%) y `lesa_humanidad` (33%) sobre-aplicados** (n chico; revisar reglas/normas gatillo). Estado: no diseñado.
- **Frontera ambiental/penal en ley 24.051** (residuos peligrosos): parser ambiental por la norma, cod penal por competencia criminal — desacuerdo legítimo, fijar criterio en CODEBOOK. Estado: decisión pendiente.
- **Capa2 = frente débil** (66% vs 82,5% capa1): foco prioritario de mejora.

**Reconciliación con held-out (H116):** CA precisión gold 68% **confirma** el silver 68,8%. La alarma `salud_amparo` 19/19 queda **REFUTADA** (artefacto capa1-only; salud real 95%). El FP Edenor→electoral queda **confirmado**.

**Pendientes materia abiertos al cierre H117:**
- **Refinamiento fuga CA (candidato #1, ahora con vara fina):** el gold confirma sumidero 68% + recall 42% (sobre-ruteo Estado→CA + abstención originaria/pendiente_capa2). Refinar exigiendo corroboración y re-validar contra el gold. Estado: no diseñado.
- **Repensar `constitucional` / `consumo` / `cambiario` / `lesa_humanidad`** (ver hallazgos). Estado: no diseñado.
- **Test-retest Claude-vs-Claude** sobre los 50 `doble_cod` (ventana fresca) → confiabilidad intra-coder; **kappa humano opcional** si el usuario codifica los 50. Estado: pendiente.
- **`muestrear_validacion.py` → v1.2:** mergear `muestrear_materia.py` como modo materia (hoy standalone en `estadisticas/validacion/`, con la constante de paths a ajustar a `output/parser/`). Estado: candidato.
- **Reducir AMBIGUO** en originaria/provincia leyendo el considerando completo vía `extraer_caso` (sube n útil). Estado: opcional.
- (Vigentes: CODEBOOK materia; csjn_analisis_v4 left-join. ~~procedencia de la cadena de materia fuera del manifiesto~~ → CERRADO C1/H118.)

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

**Constancia H181 — fila FANTASMA 348_p473 (nueva evidencia de la familia, adjudicada en disco):** la fila `348_p473` (nombre de catálogo «Hotesur S.A. c/ Altman…») tiene rango [18027, 18040] **enteramente contenido** en el de `348_p461` (Estado Nacional c/ La Rioja, acción de lesividad, [17575, 18046]) — sus 14 líneas son la cola de 461 (dispositivo «Hacer lugar a la demanda de nulidad… contra la Provincia de La Rioja»), con `case_name_cuerpo` vacío y atributos derivados de texto AJENO. 461 está sano (orig=1, merit=1): **no hay mérito perdido; hay doble-conteo de un slice bajo id equivocado**. Gap 18047–18076 (entre el fin de 461 y el arranque de 474) = candidato a la ubicación del Hotesur real que el localizador no ancló. Destapada al evaluar la Ruta D de B135(c) (H181), que se descartó por esto. El fix es de localización/frontera (esta familia + B012), NO de detectores; mientras tanto 473 queda documentada como fila espuria conocida.

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

### B136 — `is_merit` excluye originaria DE FONDO (premisa SCDB falsa) — golden/eje partyWinning afectados — CERRADO H169

**Componente:** parser (`is_merit_decision` / `es_revision_fondo`, guard #1 de B119) + metodología (golden M20).
**Origen / fuente del diagnóstico:** H165 (obs. Guillermo; verificado contra el codebook SCDB v2021_01 y el corpus en disco).
**Causa raíz — PREMISA FALSA:** el guard #1 de B119 (`is_merit = int(outcome in MERIT_OUTCOMES and not is_originaria)`) excluye TODA originaria del universo de mérito en bloque. Se construyó —y con él el golden de partyWinning (M20)— sobre la premisa de que **SCDB excluye los casos de jurisdicción originaria**. La premisa es FALSA: el codebook SCDB v2021_01 (`varJurisdiction`, §17 «Manner in which the Court takes Jurisdiction») lista la jurisdicción originaria como UNA categoría más del modo de acceso, junto a certiorari/appeal/error/certification; Marbury v. Madison (originaria) ESTÁ en la base, codificado por el writ (mandamus). SCDB INCLUYE la originaria y le asigna petitioner/respondent; solo difiere en cómo codifica el modo de acceso y deja partyWinning INDEFINIDO fuera del mérito (que es OTRA variable). «SCDB no computa quién ganó en no-mérito» ≠ «SCDB excluye el caso».
**Diagnóstico / evidencia:** `confirmado_cuantificado` (H165, en disco sobre csjn_casos.csv). `is_originaria=1` = 546 fallos; `is_originaria=1 ∩ is_merit=1` = **0** (exclusión en bloque confirmada — coincide con cómo Guillermo armó el golden). Desglose por `outcome` de las 546: **379 NO-fondo** (281 competencia + abstracto/desestima/cautelar/sin_dispositivo) — exclusión CORRECTA — y **167 DE FONDO** (96 hace_lugar + 68 rechaza + 2 procedente + 1 confirma) — exclusión INDEBIDA: son sentencias donde la Corte resuelve el FONDO en instancia originaria. De las 167, **153 tienen Provincia/Estado en la carátula** = el Estado-litigante de H1–H5 en su forma más pura (Estado demandado de origen, no recurrente de un extraordinario), hoy fuera del universo de mérito y del golden.
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto:** sobre csjn_casos.csv: `is_originaria=1 ∧ outcome∈MERIT_OUTCOMES → is_merit=1`; medir el delta (≈167) y verificar que las 379 no-fondo siguen en `is_merit=0`. El golden M20 (partyWinning) se RE-CODIFICA sobre el universo ampliado (las 167 entran como mérito; codificar `parte_ganadora` a mano para ellas) y se re-computa κ.
**Estado del fix:** aplicado (H169). **La «UNA palanca» era falsa:** el eje NO estaba solo en el guard #1 de B119 (`is_merit`) sino en DOS capas — `is_merit` (parser) Y `es_revision_fondo` (deriver `derivar_recursos.py`), que también hardcodeaba «no» para toda originaria. Y los verbos NO estaban: la originaria resuelve la demanda (hacer lugar / rechazar), no revisa un inferior (confirma/revoca/deja_sin_efecto que trae `outcome`). Condicionar solo el guard #1 al `outcome` habría dejado el deriver inconsistente y no habría capturado los verbos correctos.
**Fix aplicado (H169):** detector nuevo `es_de_fondo(considerando, por_ello)` en `clasificador_disposicion.py` (v1.09→v1.10, módulo hoja que solo importa `re`), reusado en las DOS capas para consistencia: (1) importado por `parser.py` (v22.0→v23.0) → `if is_originaria: is_merit = int(es_de_fondo(...))`; (2) usado por `es_revision_fondo` (gana param `considerando`, `derivar_recursos.py` v0.5→v0.6, backward-compat 3-args). Detector = split de `RE_DEMANDA`: grant (`hac\w+ lugar`|`admit\w+`) + reject (`rechaz\w+`|`desestim\w+`), con {0,30} de interposición («la presente demanda», «en todas sus partes la demanda»), verbos de fondo extra (inconstitucionalidad / nulidad-decreto / condena / ejecución), y asimetría: grant⇒fondo siempre, reject⇒fondo salvo INADM en considerando. Reusa el `norm()` \xad-aware del módulo (resuelve el soft-hyphen sin reinventar `_unhyphenate`) y los guards `RE_B107_NEG_HACER_LUGAR` + excepción. NO toca `disposicion()` (verbo congelado, blind 0.930). El estimador naive del diagnóstico (167 por `outcome∈{hace_lugar,rechaza,…}`) se refina a **133** exigiendo el fraseo de grant/reject de la demanda (no un hacer-lugar a una excepción/cautelar). **Medido en disco:** 133/546 originarias-de-fondo (89 grant + 44 reject); `is_merit` 2870→3003, `es_revision_fondo` 2816→2949; 0 no-originarias tocadas; consistencia `is_merit`⟺`es_revision_fondo` en las 546 = True. Validación: `check_regresion` [CLEAN] 5/5 (re-golden consciente — solo `csjn_casos.csv` [133] + `csjn_casos_votos.csv` [denormalización 662 + cascade tipo_voto 13]; textos/zonas/editorial byte-idénticos); `confirmar_scope_b136` [OK] (cascade confinado a las 133); `--verify [CLEAN] 64`; commit `10f2c5c`. **Cascade → B137:** las 13 filas de tipo_voto reclasificadas (`indeterminado→D`) destapan un error silencioso pre-existente de `clasificar_tipo_voto` (ver B137). **Pendiente:** κ ciego nuevo de `es_de_fondo` sobre muestra de originarias antes de republicar Dataverse (M35-④).
**Constancia H176 (v1.14):** `_DEM_FONDO` gana «impugnación» — sinónimo funcional de demanda/pretensión en la originaria contencioso-administrativa; gap hallado por la re-estratificación B139. Gemelos San Juan c/ AFIP-DGI leídos contra el `.md` (330_p1927 reject/INADM=False + 330_p2478 grant), ambos mérito real, ambos coincide-en-error invisibles a la divergencia. Riesgo acotado con dato: la palabra aparece en el pe de solo 3/589 originarias (los 3 leídos; ancla no-op 331_p2769). Flip-set exacto {1927, 2478} verificado bimodal (poc_b136_impugnacion.py, scripts/diagnostico/H176/): is_merit 3008→3010, gate=si 2948→2950, divergencia 216 sin cambio; disposicion() 0 diffs / clave n300 byte-idéntica (RE_DEMANDA es regex aparte). Golden re-congelado (2 filas casos + 13 votos), manifest [CLEAN] 64. Riesgo residual documentado: tomos futuros con «impugnación» procesal (liquidación/pericia) entrarían por la rama grant sin red — testigo nuevo a leer si aparece; M43 vigila.

**Referencias cruzadas:** REABRE/REFINA **B119** (su guard #1 `not is_originaria` es el que sobre-excluye). **B112** (doctrina originaria=proceso, no mérito — sigue válida; el matiz nuevo es que un proceso originario SÍ puede tener una disposición de fondo). **M20** (golden de partyWinning a re-codificar). **M32** (las 153 partes con Estado son tesis-central y hoy quedan fuera del universo). **B135** (is_originaria subdetecta — si se cablea, más originarias entran al pool). Sin ID histórico.
**Observación lateral (H171, teórica, no muerde hoy):** `RE_FONDO_EXTRA_GRANT` cubre «declarar la inconstitucionalidad» y «declarar la nulidad de…» pero NO «declarar la **invalidez** de…». No morde mientras el `pe` traiga también «hacer lugar a la demanda» (ruta grant-demanda llega antes — verificado en 337_p813 Johnsondiversey, acierto del gate); mordería solo en una originaria que declare invalidez SIN esa fórmula. Anotado para el eventual afinado de `es_de_fondo` junto con el κ ciego pendiente.

### B137 — `clasificar_tipo_voto` marca D-por-fallback cuando los matchers A/B/C/E fallan el fraseo

**Componente:** parser (`clasificar_tipo_voto`).
**Origen / fuente del diagnóstico:** H169 (destapado por el cascade de B136; los 13 votos de fondo-originarias reclasificados `indeterminado→D` obligaron a leer la función entera).
**Causa raíz:** `clasificar_tipo_voto` tiene DOS caminos al tipo D («concurrencia sustantiva independiente»): (1) `wc_voto >= 1500 AND es_estructura_autonoma` (`RE_CONSIDERANDO_NUMERADO_1` detecta «1°)»), independiente de is_merit; (2) fallback `if is_merit_decision and wc_voto >= 2500: return D`, para «OCR roto o voto que arranca con un considerando no numerado». El regex del camino 1 falla fraseos de OCR habituales («1 )» con espacio, «1º)» con ordinal º) → votos largos que SÍ son estructura autónoma no lo disparan y caen al camino 2. El camino 2 dispara **SILENCIOSAMENTE**: cualquier voto cuyo matcher A/B/C/E falle el fraseo (p. ej. C caza «considerandos N» numerados pero no «coincide con los **resultandos** de la disidencia» — sin número, resultandos≠considerandos) cae al fallback y se clasifica D por descarte, sin señal de que el matcher correcto no corrió.
**Diagnóstico / evidencia:** `confirmado_caso_testigo`. B136 (is_merit 0→1 en 133 originarias-de-fondo) activó el camino 2 en **13 votos** (12 casos): 329_p3806 (Zaffaroni), 330_p3908 (Maqueda), 333_p1088 (Maqueda + Argibay, 2 votos), 333_p2367 (Argibay), 337_p1346 (Highton), 343_p1944 (Rosenkrantz), 343_p2039 (Rosatti), 344_p809 / 344_p936 (Rosenkrantz), 345_p801 (Rosenkrantz), 347_p2044 (Rosenkrantz, Formosa), 347_p2242 (Rosenkrantz). Todos wc 2598–7640, todos fallaron el camino 1. En estos 13 la reclasificación a D parece CORRECTA (votos largos de razonamiento independiente que el bug de `is_merit=0` tenía subcontados como `indeterminado`), pero **2 son dudosos** por traer fórmula de adhesión/remisión que un matcher C/A/E debería haber cazado ANTES: 333_p1088 Argibay («coincide con los resultandos de la disidencia de Petracchi y Maqueda») y 343_p1944 Rosenkrantz («al que cabe remitir en este aspecto»). El riesgo NO son estos 13: es toda la superficie «D-por-camino-2» del corpus (2870 apelados is_merit=1 + 133 orig), donde el fallback puede estar absorbiendo votos C/A/E con el matcher fallado — subcontando concurrencias/remisiones e inflando D + `fragmenta_ratio`. Dato sensible para H3 (proliferación de votos concurrentes / fragmentación de la ratio).
**Estado de verificación:** `confirmado_caso_testigo` (13 votos en disco); magnitud corpus-wide `hipotesis_no_verificada` (falta instrumentar qué rama disparó en los 27697 votos).
**Validador propuesto:** `auditar_tipo_voto_D.py` (necesita `csjn_casos_votos.csv`): re-correr `clasificar_tipo_voto` con instrumentación de rama; contar D-camino-1 vs D-camino-2 sobre los 27697 votos; spot-check del conjunto camino-2 (¿concurrencias sustantivas genuinas o C/A/E con matcher fallado?). Según resultado: ampliar matchers C/A/E («resultandos», remisión a la mayoría, «1 )»/«1º)» en el regex de estructura para vaciar el camino 2) o endurecer el fallback; re-golden propio. Frente = H170.
**Nota de precisión (pre-existente, corpus-wide, no de B136):** el tipo D siempre setea `punto_divergencia="dispositivo"` — correcto para una disidencia, flojo para una concurrencia pura (que coincide en el dispositivo y diverge en fundamentos). Afecta a TODO voto tipo D; candidato a afinar junto con B137.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** destapado por **B136** (H169). Toca el cascade que también mueve `fragmenta_ratio` / `punto_divergencia` / `tipo_voto_sep` (dato de H3/H5). Sin ID histórico.

### B138 — `RE_RECHAZA_REC` sobre-dispara en la denegatoria de acceso pura → `es_revision_fondo=si` espurio — CERRADO H175

**Componente:** deriver (`clasificador_disposicion.py`, regla `RE_RECHAZA_REC` → `confirma`).
**Origen / fuente del diagnóstico:** H170 (D1, mecanismo M5 de la taxonomía de M39).
**Causa raíz:** `rechaza…{0,40}(recurso|queja)→confirma` es doctrina válida para el REX tratado al fondo (rechazo = deja firme), pero matchea igual «se rechaza la queja / el recurso de hecho» = gatekeeping puro sin tratamiento del mérito. Los guards del gate (competencia / inoficioso / nulidad_concesion) no lo cubren. `parte_ganadora_regla` proyecta el FP a `recurrente_pierde` y `es_revision_fondo` lo cuenta como fondo.
**Diagnóstico / evidencia:** `confirmado_cuantificado` (**CORPUS-WIDE, H171**) — **cardinalidad total = 19, invisibles a D1 = 0** (medido con `cardinalidad_gate.py` v0.2, detectores reales; ancla 19/19 de M5 [OK]). La invisibilidad temida NO existe empíricamente: cuando el `pe` dice «se rechaza el recurso/queja», el parser lee el mismo texto y da `outcome=rechaza` (nunca `confirma`) → el mecanismo SIEMPRE diverge y D1 lo vio completo. Composición por objeto del match: **queja 9 + recurso de hecho 1** (denegatoria de acceso clara) · **recurso 9** (7 REX, 2 ordinarios) · 1 reposición dentro de los 9 (procesal). Testigos leídos contra el `.md` (4 acumulados): `329_p4083` y `330_p826` (H170, gatekeeping puro) + **`330_p1205` (H171: considerando de UNA línea — «el recurso extraordinario es inadmisible, art. 280 CPCCN» — 280 disfrazado de «rechaza»)** + **`348_p747` (H171: remisión al dictamen que funda en falta de fundamentación autónoma art. 15 ley 48 y opina «mal concedido»)** — los 4 son FP del gate. IDs completos: 329_p4083, 329_p4783, 330_p826, 330_p1205, 330_p1534, 330_p1564, 330_p3657, 330_p3801, 330_p4549, 330_p4891, 331_p1284, 331_p2567, 331_p2621, 332_p1406, 334_p1302, 340_p725, 340_p1068, 342_p1524, 348_p747. **Residuo sin leer: los 2 ordinarios (`334_p1302` «rechaza el ordinario + declara desierto», `342_p1524` «rechaza el ordinario de apelación del Estado Nacional») — únicos candidatos a `confirma` CORRECTO (el ordinario es apelación plena; rechazarlo puede ser confirmar en el fondo) — + 4 REX restantes.** Los 19 tienen `gate=si` y `parte_ganadora=recurrente_pierde` hoy.
**Validador propuesto:** ~~medición corpus-wide~~ **EJECUTADO H171**; **residuo de los 2 ordinarios ADJUDICADO H172**. `334_p1302` (Mezzadra c/ EN, 3ª instancia ordinaria: cons. 7° «cabe ingresar… en el examen del planteo», revisa responsabilidad estatal por morosidad judicial — «rechaza el ordinario» ≡ confirma en el fondo) y `342_p1524` (Deutsche Rück c/ Caja Nac. Ahorro: la mayoría escribe «rechaza el recurso ordinario», los votos Rosenkrantz y Rosatti escriben «confirma» para el MISMO resultado — equivalencia rechaza≡confirma TEXTUAL dentro del fallo) → **ambos ACIERTO del gate**. **B138 = 17 FP reales (REX/quejas/recurso de hecho) + 2 aciertos ordinarios.**
**Fix aplicado (H175, clasificador_disposicion v1.11→v1.12):** guard en `es_revision_fondo` (patrón B119/B131, verbo intacto): si `disp=confirma` llegó por el FALLBACK (ningún patrón de DISP matchea) ∧ `RE_RECHAZA_REC` ∧ objeto INEQUÍVOCO de acceso (`RE_RECHAZA_ACCESO`, lista POSITIVA: queja / recurso de hecho / recurso de queja / reposición) → `no`. **El diseño v1 (lista negativa: suprimir todo salvo ordinario, 17 flips) se DESCARTÓ pre-instalación** al leer los 4 testigos no-leídos contra el `.md`: la clase «se rechaza el REX» es HETEROGÉNEA — `330_p3801` (Minaglia, Fallos 330:3801) es FONDO REAL (dispositivo MIXTO: mal concedido ×2 + «bien concedido»/«ingresando al fondo del agravio» en el 3º, art. 18 CN en 4 considerandos, 2 disidencias → evidencia B142) y `331_p2567` (Espejo Sola) borderline inclinado a fondo (cons. 4º trata un agravio en sustancia); vs `331_p2621` (insuficiencia, remisión a dictamen) y `330_p4891` (reposición encubierta: el pe dice «el recurso de fs. 34» pelado — objeto genérico ambiguo, fuera de la lista a propósito) = acceso puro. La excepción del ordinario va POR OBJETO TEXTUAL, NO por `via_recurso` (FP conocido de la columna: 330_p826 via=ordinario siendo queja pura — mismo modo que 331_p1262/B139b). **Contabilidad 19/19:** 11 FP corregidos (flip-set exacto, PoC corpus-wide + verificación bimodal en disco) + 2 aciertos ordinarios (si) + 4 FP RESIDUALES documentados (1205, 747, 2621, 4891 — límite del guard; su tratamiento exigiría señal de considerando y roza B142) + Minaglia (si, correcto) + 2567 (si, sin daño). Validación: divergencia M39 219→208; `disposicion()` 0 diffs sobre 5697 (verbo intacto); `parte_ganadora` 0 cambios (residual: los 11 quedan `recurrente_pierde` — deriva del verbo lockeado; partyWinning solo interpretable bajo gate=si); is_merit del parser 0 ripple (importa `es_de_fondo`, intacto); gold n300 no tocado. Verificador: `scripts/diagnostico/H175/poc_b138_flips.py` (bimodal pre/post rederivación).
**Estado del fix:** APLICADO H175 (v1.12). Restricciones históricas que rigieron el diseño — Restricción dura: `disposicion()` está LOCKEADA (blind 0,930) → **preferir el patrón B119/B131: guard nuevo en `es_revision_fondo`** (denegatoria-de-acceso → no), verbo intacto, sin re-validar el blind. **Restricción nueva (H171): el guard debe discriminar POR OBJETO — queja/recurso de hecho/reposición → no es fondo; REX requiere discriminador propio (280/remisión-mal-concedido vs. REX tratado al fondo), NO barrer todo `RE_RECHAZA_REC`.** **Restricción H172: EXCLUIR `via_recurso=ordinario` del barrido** — en el ordinario «se rechaza el recurso» ES la disposición de mérito (la Corte opera como tribunal de apelación plena; Deutsche Rück da el par mínimo rechaza≡confirma para el test del guard). Si se toca la regla misma → re-validación held-out completa obligatoria. Impacta `parte_ganadora` (re-κ parte).
**Referencias cruzadas:** M39 (M5), M25/κ-parte, B119/B131 (patrón guard-en-gate). H170, H172. Sin ID histórico.

### B139 — FN de `disposicion()`: verbo de fondo con objeto MATERIAL, y «rechaza la demanda» en sede recursiva (art. 16 in fine ley 48) — (a) documentado-sin-guard H176 · (b) CERRADO H181 (guard sentencia-sustitutiva v1.17)

**Componente:** deriver (`clasificador_disposicion.py`), dos sub-causas del mismo síntoma (fondo real clasificado `no_fondo` / `no_revision_*`).
**Origen / fuente del diagnóstico:** H170 (D1, sub-audit M2B + testigo 331_p100 de M2C).
**Causa raíz:** (a) la ventana `W{0,55}`/OBJ exige objeto FORMAL («sentencia/pronunciamiento/fallo»); cuando el POR_ELLO nombra el objeto **material** — «confirmar **el reajuste de haberes**» (332_p731 Chimondeguy), «revocar **la declaración de inconstitucionalidad** del art. 25» (340_p411 Gualtieri) — el verbo de fondo real no matchea y el caso cae al fallback. (b) La regla «rechaza la demanda → `no_revision_demanda`» asume contexto originario; en sede de queja/REX con **sentencia sustitutiva** («se rechaza la demanda, art. 16, segunda parte, ley 48» — 331_p100 Superior Gobierno de Tucumán c/ Fisco Nacional) el rechazo de la demanda ES la decisión de mérito.
**Diagnóstico / evidencia:** `confirmado_cuantificado` (**CORPUS-WIDE, H171** — `cardinalidad_gate.py` v0.2). **Sub-causa (a): 59 candidatos brutos** (verbo pelado sin ventana W/OBJ; verbos: deja_sin_efecto 30 · nulidad 13 · revoca 8 · confirma 6 · modifica 2; 43 apel / 16 orig), estratificados en 4 clases a adjudicar caso a caso: (i) **FN de objeto material REAL** — 3 testigos leídos: 332_p731 Chimondeguy («el reajuste de haberes»), 340_p411 Gualtieri («la declaración de inconstitucionalidad»), **+ 330_p1927 (H171: «rechazar la impugnación… y, en consecuencia, confirmar el acto administrativo» de la DGI — mérito clarísimo, `confirma` de DISP no matchea porque «acto administrativo» ∉ OBJ → cae a `no_fondo`)**; (ii) *aciertos del clasificador* (objeto procesal: intimación, excusación, costas, honorarios, cautelar); (iii) ***`pe` truncado por OCR/banner*** — **329_p4634 CONFIRMADO contra fuente H171** (el `pe` de producción termina «se deja sin efecto la sen-» con banner interpolado; el `.md` sigue «-tencia apelada. Notifíquese…») → **estos casos salen del universo B139 y pertenecen a la familia M21/B122 del parser**; (iv) *ruido del verbo pelado de diagnóstico* (329_p1568 «seguro colectivo de invalidez», 332_p1957 narrativa de ley). **Sub-causa (b): 13/178 `no_revision_demanda`** con señal recursiva; la vía derivada (`via_recurso=rex` de recursos.csv) captura los 13, incluidos TODOS los que citan art. 16 ley 48 (5) → **la señal estructural resuelve (b) sola, PERO restringida a NO-originarias**: FP confirmado H171 en `331_p1262` (originaria OSPLAD c/ Catamarca de fondo; la única mención de «extraordinario» en todo el bloque es la cita de Fallos 324:2153, línea 693 — `via_recurso` leyó narrativa del considerando). Testigo 331_p100 (art. 16 in fine, sentencia sustitutiva) ya adjudicado en H170. Nota H171 (originarias del bucket a): 337_p813 es ACIERTO del gate (ruta grant-demanda de `es_de_fondo`); deja dos observaciones laterales — «invalidez» ∉ `RE_FONDO_EXTRA_GRANT` (gap teórico, no muerde mientras acompañe «hacer lugar a la demanda»; anotado en B136) y `parte_ganadora=no_aplica` en originaria ganada por la actora (= re-codificación pendiente de las 133, M19/M20).
**Validador propuesto:** ~~(a) contar verbos de fondo sin OBJ formal; (b) contar art. 16 / vía~~ **EJECUTADO H171** (`cardinalidad_gate.py` v0.2). Falta: adjudicar el estrato (i) vs (ii) del bucket (a) — los 59 traen snippet para triage rápido.
**Estado del fix:** **RESUELTO-POR-PARTES H176.** (i) Superficie `es_de_fondo` (originarias): CERRADA — v1.14 (+«impugnación» en `_DEM_FONDO`; gemelos San Juan 330_p1927/330_p2478 leídos = mérito real; flip-set exacto verificado bimodal; blind byte-idéntica; ver B136). (ii) Guard B139a apeladas: **DIFERIDO con fundamento** — 10 FN reales adjudicados por lectura con 5 mecanismos (objeto material ×6: 332_p731, 340_p411, 341_p1924 Blanco, 341_p1075 Bercun, 343_p28 laudo, [348_p1352 re-adjudicado a ACIERTO por criterio nulidad-de-actuaciones]; ventana W corta: 338_p234; OCR: 331_p2628; pronominal: 337_p1042; mixto ordinario/art.16/honorarios: 332_p2797). El mismo shape mecánico cubre FN y ~12 aciertos procesales (intimación/excusación/medida/providencia/acordada/cautelar) → discriminar exige semántica del sustantivo (lista positiva fiteada = overfitting) y toca `disposicion()` LOCKEADA (held-out completo); pronominal heterogéneo POR LECTURA (1042 fondo vs 1857/4094 competencia). Los 10 quedan documentados-sin-guard (estatus B138-residuales); candidato «laudo»→OBJ: cardinalidad 1 corpus-wide, anotado para el próximo bump de DISP (junto con docstring L6). Aciertos del gate adjudicados H176 (DIV = residuo lado parser → paso 3): 330_p1950, 330_p4396, 337_p1024, 339_p852, 344_p2513, 348_p83, 333_p1857. (iii) Sub-causa (b): DIFERIDA con diseño — guard estilo B138 (disp=no_revision_demanda ∧ señal art.16 TEXTUAL ∧ ¬originaria; NO la columna via sola: FP 330_p826/331_p1262); flip-set = 9 apeladas, solo 331_p100 leída → 8 lecturas pendientes, unidad propia. Extracciones H176 en `scripts/diagnostico/H176/`.
**Cierre H181 — sub-causa (b) IMPLEMENTADA y validada en disco (clasificador v1.16→v1.17), `confirmado_cuantificado`:** población re-medida EN SCRIPT sobre el sello v24.1 (`poblacion_b139b` v0.1: 181 no_revision_demanda · art16 7/2-orig · via=REX 14/5-orig · 9 apeladas == flip-set H176 reconciliado; el conteo previo por `python -c` OMITIÓ al testigo — lección ops: regex no-ASCII van en script). **Las 8 lecturas adjudicadas caso a caso (extractos en `scripts/diagnostico/H181/`, criterio confirmado por Guillermo): 6 TP** — 331_p100 (testigo), 337_p1174 (Rodríguez c/ Google), 343_p1259 (FADEEAC, TP-con-asterisco: ÚNICO REX y desestimado + art. 16 — la Corte dispone igual sobre la demanda, criterio del usuario), 344_p277, 348_p895 (Defensor del Pueblo), 332_p2559 (sustitutiva SIN cita del art. 16) — **+ 3 aciertos del gate** (330_p3160 Bussi/inoficioso, 331_p530 Cóspito/acceso, 332_p2237 incidental). **Guard v1.17, dirección INVERSA (fuerza `si`), verbo intacto:** `disp==no_revision_demanda` ∧ (S1 = art. 16 ∧ ley 48 en el pe [5/6; NO la columna via — FP 330_p826/331_p1262] ∨ S2 = concesión-de-recurso ∧ «rechaza la demanda» en el MISMO pe [agarra 2559]); ¬originaria por construcción (la rama originaria retorna antes). `poc_b139b_guard` v0.1: A0 round-trip 0 diffs/181 · flip-set corpus-wide EXACTAMENTE 6 · 0 extras · 0 pérdidas · S1 y S2 ambas necesarias. Ciclo: casos/votos SOLO is_merit_decision (6/28 filas), tipo_voto 0 flips, recursos único downstream movido; **is_merit 2941→2947**, div 0, manifest [CLEAN] 64. **NOTA de eje (abierta, no de esta unidad):** `disposicion` de los 6 QUEDA `no_revision_demanda` (eje de dispositivo, verbo intacto — patrón B119/B143) pese a que la Corte dispone sustitutivamente sobre la demanda; `parte_ganadora` derivada de esa disposicion puede quedar conocido-equivocada para las 6 sustitutivas (el recurrente gana en sustancia) — re-mirar en M19/M20/M25 junto con la re-codificación de las 133 originarias. Sub-causa (a) sigue documentada-sin-guard (10 FN, 5 mecanismos; candidato «laudo»→OBJ para el próximo bump de DISP).
**Referencias cruzadas:** M39 (M2B/M2C), B119/B131 (patrón guard), M19 (blind 0,930), `clasificador_via` (insumo para sub-causa b). H170, H181. Sin ID histórico.

### B140 — FP del gate: revoca-FORMAL en abstracto (sin juicio de mérito) y nulidad-de-concesión fuera de la ventana del guard — (b) CERRADO H175 · (a) resuelto-sin-guard H175

**Componente:** deriver (`clasificador_disposicion.py` / `es_revision_fondo`), dos mecanismos de FP con el mismo síntoma (`es_revision_fondo=si` espurio en casos no-de-fondo).
**Origen / fuente del diagnóstico:** H170 (D1, sub-audit M4_ABSTRACTO_OTRO). Corrección de atribución intra-sesión: el gap de ventana pertenece al guard de **B131** (`RE_NULIDAD_CONCESION`, cerrado H143), no a B133 como se rotuló provisoriamente.
**Causa raíz:** (a) **revoca-formal en abstracto**: doctrina «aun devenida abstracta la cuestión, revocar la apelada» con salvedad expresa de no abrir juicio («sin perjuicio de revocar… lo resuelto no importa abrir juicio») — el verbo `revoca` es real pero NO hay decisión de mérito; ningún guard existente lo cubre. Testigo: `329_p5261` (ADC, imagen religiosa). (b) **nulidad de concesión fuera de ventana**: «declarar la **nulidad** parcial **del auto** de fs. 8145/8149 en cuanto, en el punto II, **concedió** el recurso» — nulidad de concesión pura que `RE_NULIDAD_CONCESION` (guard B131) no captura porque «nulidad» y «concedió» quedan separados por la referencia intercalada al auto. Testigo: `343_p2098` (Paccagnini).
**Diagnóstico / evidencia:** `confirmado_cuantificado` (**CORPUS-WIDE, H171** — `cardinalidad_gate.py` v0.2). **Sub-causa (a):** población `outcome=abstracto ∧ disp∈fondo` = 50, de los cuales **27 con gate=si [OK ancla D1]** y 23 ya suprimidos por el guard `RE_DISP_INOFICIOSO`. Detector textual «sin perjuicio de revocar» / «no importa abrir juicio» corpus-wide (pe+co): 32 hits, pero **solo 3 FUERTES (salvedad en el `pe` dispositivo)**: `329_p5261` ADC (FP confirmado H170), **`340_p1973` adjudicado ACIERTO H171** (el considerando 7° invoca expresamente el art. 16, segunda parte, ley 48 «y decidir sobre el fondo de la cuestión sometida» — la salvedad refiere al asunto subyacente, no a la revisión; revoca real sobre legitimación colectiva) y **`329_p5115` PENDIENTE de decisión doctrinal** (remand de arbitrariedad puro: «sin abrir juicio sobre el fondo, se deja sin efecto la sentencia» + remisión al dictamen — ¿cuenta como revisión de fondo? posición Spaeth-compatible: *vacated & remanded* = disposición de mérito → si se adopta, **B140a se reduce a UN caso (ADC)** y conviene evaluar documentarlo como FP conocido en vez de guard). Los 29 hits en `co` son boilerplate débil (fórmula de arbitrariedad-por-demora / asides limitativos) — el guard candidato, si existe, solo debe mirar el `pe`. **Sub-causa (b): 10 CERRADO, 9 invisibles a D1** (los 9 con `outcome=nulidad ∧ gate=si`: ambas capas mal juntas; solo Paccagnini 343_p2098, outcome=abstracto, asomó en D1). **Fórmula única en los 9**: «se declara la nulidad de la resolución (de fs. X,) **por la que se concedió el recurso**» — el guard no matchea porque sus alt-2/alt-3 exigen «recurso **extraordinario**» y la conectiva «por la que se concedió» no está cubierta. Testigo `329_p120` leído H171 (Olivero y Rodríguez: nulidad de concesión por auto no fundado — vía pura, 0 fondo) + verificación mecánica: `RE_NULIDAD_CONCESION.search(norm(pe))` = False sobre el `pe` de producción. IDs: 329_p120, 329_p4279, 329_p5579, 331_p1906, 331_p2583, 332_p2813, 334_p1139, 339_p299, 343_p2098, 344_p1435. Los 10 inflan `is_merit`, `es_revision_fondo` y `parte_ganadora=recurrente_gana`.
**Validador propuesto:** ~~(a) outcome=abstracto ∧ disp∈fondo + detector; (b) nulidad+conce* sin guard~~ **EJECUTADO H171**; **decisión doctrinal de 329_p5115 TOMADA H172**. Adjudicación Spaeth-compatible: `329_p5115` (Civitarreale, doble conforme penal) es FONDO / gate ACIERTO — la cuestión federal (arbitrariedad por denegación de revisión) fue adjudicada en pleno a favor del recurrente; la salvedad «sin abrir juicio sobre el fondo» reserva el fondo penal subyacente al reenvío, no niega la revisión. *Vacated & remanded* = disposición de mérito, consistente con el 41% de `deja_sin_efecto` del corpus (M20) — la posición estricta colapsaría el eje entero, no solo B140a. En contraste, `329_p5261` (ADC) es *Munsingwear-style vacatur*: revocación profiláctica por mootness (imagen retirada) SIN adjudicación de nada (cons. 6° expreso: «no importa confirmar ni afirmar… impedida de emitir opinión»). **→ B140a cardinalidad real = 1 (solo ADC/329_p5261).** 340_p1973 y 329_p5115 son aciertos.
**Fix aplicado (H175, clasificador_disposicion v1.12→v1.13) — sub-causa (b):** alternativa NUEVA en `RE_NULIDAD_CONCESION` (se suma, no reemplaza): «nulidad (parcial) de la/del resolución(es)/decisión/auto … conced… … recurso» SIN exigir «extraordinario» — cubre la conectiva «por la que se concedió» (los 9) y la intercalada de 343_p2098. FLIP DE VERBO (la regex vive en la pre-cascada de `disposicion()`): los 10 → `nulidad_concesion` (31→41), `parte_ganadora` → `no_aplica`, gate → `no`. **Ripple NO PREDICHO adjudicado:** `admisibilidad` consume `disposicion` (firma de derivar_recursos) → los 10 salen de `admite` (donde estaban MAL: una concesión anulada no es admisión): 9→`sin_marcador` (coherentes por construcción con los 31 veteranos B131: dist final 40 sin_marcador + 1 inadmite) y 1→`inadmite`+CUESTION_ABSTRACTA (Paccagnini, outcome=abstracto). Lección: el contrato de ripple de un flip de verbo debe enumerar TODOS los ejes aguas abajo que consumen `disposicion` (parte, gate, admisibilidad, causa). Validación: PoC corpus-wide flip-set EXACTO = los 10 IDs, 0 hits extra; divergencia M39 208→216 y es CORRECTO (los 9 invisibles tienen is_merit=1 del parser — su COPIA de la regex, parser L470, NO se tocó, orden M39 lockeado — quedan expuestos como residuo para el paso 3; Paccagnini converge); gold n300: 0 de los 10 en la clave, `build_m20` con v1.13 regenera clave BYTE-IDÉNTICA (0 celdas diff/300) → blind 0,930 intacto por construcción; verificación bimodal en disco [OK]. Verificador: `scripts/diagnostico/H175/poc_b140b_flips.py`. **Sub-causa (a): resuelto-sin-guard** — cardinalidad 1 (ADC/329_p5261), documentado como FP conocido conforme la adjudicación H172; un guard para 1 unicum no paga. Menor: el docstring L6 del clasificador apunta al path viejo de build_m20 (`scripts/diagnostico/H120/`; hoy `scripts/validacion/`) — corregir en el próximo bump del módulo.
**Estado del fix:** (b) APLICADO H175 (v1.13) · (a) documentado-sin-guard. Candidatos originales: (a) **RESUELTO H172 — arbitrariedad-remand = fondo (Spaeth), universo = 1 caso (ADC). Tratamiento: documentar como FP conocido / corrección puntual de 1 caso, NO guard** (un guard `abstracto+revoca-formal` sobre 1 unicum no paga y arriesga FN; el criterio «sin perjuicio de/sin abrir juicio sobre el fondo» acompañando deja_sin_efecto NO niega mérito → a CODEBOOK). Alternativa si se prefiere guard: mirar SOLO el `pe`; si no, guard `abstracto+revoca-formal` en `es_revision_fondo` mirando SOLO el `pe`; (b) **cubrir la conectiva «(resolución|auto|decisión) … por (la|el) que se concedió el recurso» SIN exigir «extraordinario»** — ensanche del guard `RE_NULIDAD_CONCESION` o segunda pasada; los 9 comparten fórmula literal → fix quirúrgico de bajo riesgo, validar 0 regresiones sobre los matches actuales del guard. Verbo lockeado intacto en ambos.
**Referencias cruzadas:** M39 (M4_ABSTRACTO_OTRO), **B131** (el guard cuya ventana falla), B129 (familia aside; la variante «inoficioso…recursos de hecho» del lado parser queda anotada en M39), B133 (mootness — colindante, no causa), CODEBOOK (criterio «sin abrir juicio sobre el fondo» ≠ negación de mérito, H172). H170, H172. Sin ID histórico.

### B141 — Falso terminador de oración en el chunk de `_barrer`: inicial anonimizada / numeral romano a fin de línea truncaba el dispositivo — CERRADO H174

**Componente:** parser (`_barrer`, chunk del dispositivo). NO el detector: `es_de_fondo` v1.10 resultó INOCENTE (PoC sobre el texto completo de 3894 → `True`; los 3 candidatos de H173 descartados: `rechaz\w+` cubre el infinitivo, `finditer` barre todo el pe, ningún guard suprimía).
**Causa raíz (H174, verificada contra código):** el chunk corta en la primera línea terminada en `.` (v23.1 L3102). Una inicial anonimizada («...sus hijos E.»), la inicial de un juez o parte («Eugenio R.», «Dolores G.») o un enumerador romano a fin de línea («se resuelve: I.», «...Nación); II.») actúa como falso terminador: partía el dispositivo escondiendo (a) el verbo de fondo al detector, (b) la granularidad al cascade de outcome, y (c) el marcador performativo a la regla P — tercera cara descubierta al validar: 334_p1047, el «: I.» ocultaba «Se revoca» → chunk no-performativo → fallback al pick argumental equivocado, que además ROBABA el cierre del considerando (wc 2471→2629 al sanar).
**Cardinalidad (H174, cerrada corpus-wide):** firma de dos niveles (inicial suelta ∪ numeral romano) = 16 hits → 14 truncamientos reales + 2 FP de firma (fines genuinos en inicial: 332_p238 «M. E. A. V.», 340_p397 «Sala B.»); los 14 adjudicados contra texto fuente. Mérito perdido por el mecanismo = **2 exactos** (329_p3894, 341_p1148 — «se resuelve: I.» le comió el dispositivo entero, «Hacer lugar a la demanda» c/ INAI).
**Fix aplicado (H174):** parser v23.1→v23.2 — `RE_FALSO_TERMINADOR` + peek `_proxima_linea_es_firma` (reusa `linea_es_firma_de_juez`, fuente única): la línea en falso terminador NO corta salvo que lo próximo con contenido sea firma (freno anti-contaminación para los 2 fines genuinos). **ACOPLE embarcado ANTES:** `clasificador_disposicion` v1.10→v1.11, guard `RE_FONDO_IN_LIMINE` en la rama reject de `es_de_fondo` — el rechazo «in limine» de la demanda es UMBRAL (falta de caso justiciable, Fallos 325:474), no fondo; testigo adjudicado 330_p3777 (cons. 5º-8º): sin guard, destapar «Rechazar in limine la demanda» fabricaba 1 FP de mérito (INADM no cubre falta-de-caso). Guard no-op sobre el corpus pre-fix (A/B módulo-vs-módulo, 0 flips en 589 originarias) y endurece 5 'no' que dependían de INADM (329_p1675, 329_p2754, 330_p3109, 331_p1364, 337_p627; cubre comillas OCR).
**Validación (H174, en disco):** `_barrer` de producción viejo-vs-parcheado sobre los 14 bloques fuente (el viejo reproduce el CSV = fidelidad; el nuevo recupera 12, genuinos byte-idénticos) + corrida completa + `verificar_b141_post.py` + diff contra golden 100% adjudicado: 13 `por_ello` extendidos (12 familia + 1047), is_merit flips EXACTOS {329_p3894, 341_p1148} 0→1 (3006→3008, coherente bicapa), 330_p3777 sostenido en 0 por el guard EN PRODUCCIÓN, outcome flips solo en familia (3894 hace_lugar→rechaza = mejora; 1148/4526/1047 → B142), zonas/editorial byte-idénticos. Divergencia M39 = 219 sin cambio. Golden re-sellado, recursos + materia re-derivados, manifest [CLEAN] 64. + Fix infra: stdout/stderr `errors="replace"` (UnicodeEncodeError cp1252 bajo stdout REDIRIGIDO, latente en todas las versiones — reproducido sobre v23.1 intacta; a consola directa PEP 528 lo tapaba).
**Residuales (adjudicados, NO de este fix):** 333_p1951, 343_p2080, 334_p1237, 330_p563 y la medida 3 de 344_p274 = truncamiento por PRESUPUESTO (banner partido en 3 líneas físicas que drena el chunk, o dispositivo largo) → clase M21 Fase 3, encolados en su nota H174. 2080/1237 ganan cola de banner cosmética (norm() enmascara la terna downstream). 338_p699: su mérito lo bloquea `is_originaria=0`, no el truncado (EXTRA_GRANT ya matcheaba sobre el trunco) → candidato post-B010.
**Referencias cruzadas:** B135 (el ripple que lo expuso), B136 (detector compartido), M39 (divergencia verificada estable; constancia H174), M21 (residuales de presupuesto → Fase 3), **B142** (dispositivos mixtos, destapado por este diff), post-B010 (candidatos FN is_originaria). Scratch: `scripts/diagnostico/H174/` (verificar_b141_post, pocs, backups PRE, corrida_v232.log). H172, H173, H174. Sin ID histórico.

### B142 — Sesgo de mérito/outcome en dispositivos MIXTOS: la señal accesoria le gana al verbo dominante en AMBAS capas

**Componente:** `classify_outcome` (parser: detectores pre-cascada + orden del cascade) + guards de `es_de_fondo`/`es_revision_fondo` (clasificador_disposicion) — bicapa.
**Origen / fuente del diagnóstico:** H174 — los outcome-flips del diff de B141: al destapar dispositivos completos, los mixtos quedaron clasificados por la señal equivocada.
**Causa raíz:** en dispositivos con ≥2 puntos resolutivos, la clasificación se queda con la PRIMERA señal del cascade o con un detector pre-cascada, no con la disposición dominante: (i) 341_p1148 → outcome=`rechaza` («Rechazar la excepción», punto I) cuando la verdad es `hace_lugar` («Hacer lugar a la demanda», punto II); (ii) **334_p1047 (testigo bicapa)** → el detector pre-cascada `inoficioso` (punto II, REX) le gana al `revoca` de mérito (punto I, recurso ordinario) EN LAS DOS CAPAS: parser outcome=`abstracto`/is_merit=0, y en el deriver `disposicion()`=`revoca` pero `es_revision_fondo`=`no` (guard) → las capas COINCIDEN EN EL ERROR, invisible al instrumento de divergencia M39; (iii) 330_p4526 → `caducidad` (incidente de costas) cuando la verdad es `desistimiento` (extinción por desistimiento del derecho). Contracara: 329_p3894 el mismo mecanismo MEJORÓ el valor (hace_lugar→rechaza es lo correcto del mixto excepción+demanda).
**Diagnóstico / evidencia:** `confirmado_caso_testigo` — 334_p1047 (Metrovías, verificado en sandbox con módulos reales H174: `disposicion()`=revoca / gate=no); 341_p1148 y 330_p4526 evidencia del cascade. Es la clase M3_MIXTO de M39 trasladada al eje OUTCOME/disposición. **Evidencia nueva (H175, testigos B138 leídos contra el `.md`):** `330_p3801` (Minaglia, Fallos 330:3801) — dispositivo mixto de 3 puntos (mal concedido ×2 + rechaza EN EL FONDO el agravio de fundamentación del allanamiento, «bien concedido» expreso, art. 18 CN en 4 considerandos, disidencias Petracchi y Maqueda-Zaffaroni que revocan): el registro «se rechaza el REX» del pe esconde la adjudicación de mérito; `331_p2567` (Espejo Sola) mixto menor (un agravio extemporáneo + uno tratado en sustancia). Ambos quedan gate=si (correcto) tras el rediseño B138; documentan que el rechazo-de-REX puede ser mérito y que su discriminación exige señal de considerando — territorio de esta entrada.
**Cardinalidad:** NO medida. El universo (dispositivos con puntos resolutivos de familias contradictorias) exige PoC corpus-wide; los truncamientos de B141 lo SUBREPRESENTABAN — puede haber más mixtos ya visibles desde antes.
**Validador propuesto:** barrer `por_ello` con ≥2 matches de familias de verbos distintas (grant/reject/inoficioso/incidental); medir cuántos outcome salen de la señal no-dominante; taxonomizar (excepción-vs-demanda, mérito-vs-inoficioso, principal-vs-incidente) antes de diseñar regla de dominancia.
**Estado del fix:** no diseñado. Nota de diseño: cualquier fix debe tocar `classify_outcome` Y los guards del gate A LA VEZ (lección 1047: las dos capas comparten el sesgo, y el coincidir-en-error no aparece en la divergencia — límite del instrumento M39).
**Referencias cruzadas:** B141 (lo destapa), M39 (clase M3_MIXTO, eje hermano), B119 (detectores pre-cascada, origen del lever `inoficioso`), M20. H174. Sin ID histórico.

### B143 — FP latente del gate: «nulidad de todo lo actuado» (nulidad DE ACTUACIONES) cuenta como fondo vía el alt window-free de DISP — CERRADO H177 · EXTENDIDO v1.18 H181

**Componente:** deriver (`clasificador_disposicion.py`) — eje gate (`es_revision_fondo`), NO el verbo.
**Fix aplicado (H177):** guard del gate v1.15 (patrón B119/B131, verbo intacto): `disp=="nulidad" ∧ RE_NULIDAD_ACTUADO ∧ ¬RE_ABSOLUCION → "no"`. Prerequisitos cumplidos: 16 lecturas contra el `.md` (extraídas a `scripts/diagnostico/H177/`, adjudicadas caso a caso con Guillermo) + solapamiento con gold n300 = **0**. Adjudicación: **15 FP procesales** (6 in-forma-pauperis/asistencia ineficaz [incl. 330_p5052 Domínguez: «desde la sentencia» pero retrotrae por defensa ineficaz, no sustituye] · 4 juzgado incompetente/avocación · 1 inexistencia de caso art. 116 [332_p1823 PROCURAR, sin controversia = umbral, coherente con B141] · 4 vicio de trámite) + **1 acierto** (330_p399 López, sustitutiva con absolución → cubierto por la excepción RE_ABSOLUCION). Corrección al diagnóstico H176: eran 14 invisibles + 2 ya divergentes (347_p327, 348_p1152, is_merit=0). Superficie del alt = 17; el 17º (333_p405, disp=revoca) queda fuera por el ancla disp==nulidad. Validación: PoC bimodal `poc_b143_guard.py` (candado de versión) PRE+POST verdes en disco; flip-set EXACTO 15 si→no, 0 no→si; gate=si 2950→**2935** · divergencia 216→**227** (+13 expuestos lado parser → paso 3, −2 salen) · parser 0 ripple ([CLEAN] sin re-golden) · clave n300 byte-idéntica (blind 0,930 vigente) · manifest [CLEAN] 64. Residual estilo B138: `parte_ganadora=recurrente_gana` queda en los 15 (deriva del verbo lockeado). RE_NULIDAD_ACTUADO duplica el alt de DISP verbatim (dedup pendiente, mismo estatus que RE_NULIDAD_CONCESION → D3/M40).
**Origen / fuente del diagnóstico:** H176 — destapado por el CRITERIO DE CODEBOOK fijado por Guillermo al adjudicar 348_p1352 (Pereyra): **nulidad DE LA SENTENCIA (vicio de la decisión, subsumida en la apelación — art. 253 CPCCN) = fondo · nulidad DE ACTUACIONES/procedimiento (vicio in procedendo, retrotrae el trámite aunque barra la sentencia) = procesal.** Coherente con Rivera 333_p1152 (H172, nulidad por vicio pupilar = acierto en 'no').
**Causa raíz:** el alt window-free `nulidad de todo lo actuado` de DISP (correcto como caseDisposition=nulidad) arrastra gate=si por `nulidad ∈ _FONDO`, pero bajo el criterio nuevo la mayoría de esa fórmula es retrotraer-el-trámite (procesal), no revisión de fondo. Mismo patrón conceptual que B119/B131: verbo-de-fondo ≠ revisión-de-fondo.
**Diagnóstico / evidencia:** `confirmado_cuantificado` (H176, PoC read-only): **16 casos** disposicion=nulidad vía el alt, TODOS gate=si, TODOS coincide-en-error candidatos (outcome del parser acompaña) → **invisibles a la divergencia M39**. Familias por contexto: in-forma-pauperis/voluntad recursiva (329_p1794, 330_p487, 330_p4925, 333_p1671 — patrón Pereyra), actuado ante juzgado incompetente (334_p1458, 337_p97, 345_p191), inexistencia de «caso» art. 116 (332_p1823 — primo del in-limine B141), retrotraídos varios (330_p1169, 330_p5052, 339_p656, 344_p163, 344_p1259, 347_p327, 348_p1152). **Contraejemplo que PROHÍBE guard ciego: 330_p399** («nulidad de todo lo actuado Y SE ABSUELVE», art. 16 segunda parte ley 48 — sustitutiva con absolución = fondo indiscutible).
**Validador propuesto:** leer los 16 contra el `.md` (extraer_caso) ANTES de diseñar; verificar solapamiento con el gold n300 (si alguno está en la clave, el κ-gate 0,946 ya incorpora codificación humana de estos casos — respetar o re-mapear conscientemente).
**Estado del fix:** no diseñado. Candidato: guard del gate estilo B119/B131 (verbo intacto) con señal de excepción para sustitutivas (absolución / art. 16). NO abrir sin las 16 lecturas.
**Referencias cruzadas:** B119/B131 (patrón guard-en-gate), B141 (umbral/falta de caso), B142 (mixtos), M39 (invisible al instrumento), M43 (re-κ medirá el eje post-fix), criterio de codebook H176 (registrado también en B139). H176. Sin ID histórico.

**Constancia H181 — extensión v1.18 (la clase 333_p405, materializada):** el pe completo de Pereyra `348_p1352` (destapado por M21 F3) muestra «se deja sin efecto **todo lo actuado** con posterioridad a la notificación…» = nulidad de actuaciones bajo `disp=grant_remand_implicito` (verificado en disco: el remand «vuelvan los autos… conforme lo decidido» lo metía en `_FONDO`), fuera del ancla `disp=="nulidad"` de v1.15. Guard espejo v1.18: `disp ∈ {grant_remand_implicito, deja_sin_efecto} ∧ RE_DSE_ACTUADO ∧ ¬RE_ABSOLUCION → no`. Superficie corpus-wide de `RE_DSE_ACTUADO` medida sobre `norm(pe)` ANTES de cablear = **exactamente 1 = el testigo** (0 lecturas nuevas). Método: sobre el pe CRUDO la superficie da 0 — el guión de corte «efec- to» derrota la regex; medir siempre sobre norm. Bimodal verde (control sin-guard = si = el FP que el golden habría consagrado — lógica de orden (a) de esta entrada, aplicada por segunda vez).


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
**Estado del fix:** no se aplica — reclasificado no-bug (H088).
**Nota H088 (reexaminado sobre el corpus actual):** `dictamen_presente=='0'`
son 193 filas = TODOS los sumarios (160 `sumario_con_link` + 33
`sumario_editorial`), no solo con_link como decía el diagnóstico viejo; y
NUNCA aparece en un fallo (los 5669 fallos tienen booleano limpio
`True`/`False`). El `'0'` es un centinela de "no aplica" para entradas que no
son fallos, perfectamente segregado por `tipo_entrada`. Forzarlo a `False`
perdería información (confundiría "no es un fallo" con "fallo sin dictamen").
NO es bug: a lo sumo incomodidad de tipos en una columna que el análisis
filtra por `tipo_entrada=='fallo'` igual. Fix NO recomendado.
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

### M15 — Validar un patch del parser es A/B sobre texto idéntico, no contra la columna de producción

**Origen:** H093 (fix B100). Recalcular una función del parser sobre `csjn_casos.csv` NO reproduce producción para los casos cuyo match cae pasado el truncado a 2000 chars de `considerando_text`: la propia detección (p.ej. FUERA) falla sobre texto truncado aunque en producción (texto completo) acierte. Consecuencias observadas: (a) los conteos de cola sobre el CSV son PISO, no producción (H092 reportó 58, producción emitía 72 — los 14 delta); (b) leer un caso truncado puede **dar vuelta el veredicto** a ojo (341_p2027 parecía FP, es TP completo).
**Regla:** para medir el efecto de un patch del parser, correr A/B `old↔new` de la función sobre EL MISMO texto: el artefacto de truncado se cancela y queda solo el delta del patch. Nunca comparar patched-vs-columna-de-producción (mezcla el patch con el desfase truncado↔completo). La verificación de regresión cero final es el harness sobre texto completo (`check_regresion.py`), no el recálculo sobre el CSV. Para validar a ojo hits truncados, usar `scripts/diagnostico/extraer_caso.py` (texto completo desde el `.md`), nunca el snippet del CSV.
**Estado:** regla activa.
**Referencias cruzadas:** H092, H093. B100.

### M16 — Refacción del explorador Streamlit para auditoría a ojo

**Origen:** H093. El explorador (`scripts/explorador/`, Streamlit) quedó desactualizado tras las categorías nuevas de filtro (causa_inadmisibilidad, queja, cuestión federal) y ya venía recargado de filtros; dudas de escalabilidad (Streamlit re-ejecuta todo el script ante cada widget, muchos filtros degradan UX y latencia).
**Propuesta:** refaccionarlo orientado a **auditoría a ojo** en vez de a apilar filtros. Modo «un caso a la vez» con texto completo (considerando+por_ello, estilo `extraer_caso.py` pero en navegador), navegable filtrando por outcome/causa_inadmisibilidad; separar el modo exploración-masiva del modo auditoría-de-precisión. Habilita la validación pendiente de la cola (B100) sin scripts ad-hoc.
**Estado:** PARCIAL (H096). `scripts/explorador/exploradorv6.py` agrega los filtros de las categorías nuevas (`causa_inadmisibilidad`, `es_queja`/`queja_resultado`, `tipo_cuestion_federal`, `apertura_tipo`, `tribunal_origen_status`, flags is_*/dictamen, filtro por juez, rangos numéricos), todos autopoblados del CSV (sin listas hardcodeadas). Sidebar reorganizado en grupos colapsables (Búsqueda / Clasificación / Proceso / Panel / Métricas) + contador y «limpiar filtros»; toggles de zona movidos al panel de fuente del detalle. Tabs Tabla/Resumen (distribuciones de la selección) + descarga del subconjunto a CSV. El detalle (un caso a la vez) muestra el bloque `.md` completo coloreado por zona — cubre el «texto completo en navegador». PENDIENTE: separación explícita modo masivo / modo auditoría-de-precisión; panel inline del considerando+por_ello completos (hoy se ven vía el bloque `.md`, no como campo dedicado).
**Referencias cruzadas:** H093, H096. B100. M15.

### M17 — Revalidar validaciones de cola previas sobre tomos con volúmenes solapados

**Origen:** H094 (B102). El bug de volumen equivocado de `extraer_caso.py` <v2.0 pudo contaminar validaciones a ojo de la cola hechas con la herramienta antes del fix, no solo la de H094. Si en H092/H093 (p.ej. FUERA_DE_TERMINO) se validó algún hit de un tomo partido (329, 334, 338, 343, 344, 345…) leyendo el volumen equivocado, el veredicto podría estar mal.
**Regla / acción:** revalidar con `extraer_caso.py` v2.0 (que ancla por `source_file`) cualquier hit de cola eyeballeado pre-v2.0 cuyo tomo tenga más de un volumen. No urgente: los conteos de producción no dependen de la herramienta; es saneamiento de la evidencia de validación.
**Estado:** parcialmente saneado (H095). Los 10 `FUERA_DE_TERMINO` (todos en tomos partidos) se revalidaron por chequeo de ancla única intra-tomo desde el CSV (no por re-extracción): los 10 tienen ancla de considerando única dentro del tomo → el glob+ancla pre-v2.0 resolvía el volumen correcto, sin contaminación B102. Los 12 «delta» de SENTENCIA_DEFINITIVA/FUNDAMENTACION ya se habían leído con v2.0 en H094, y los 44 VISIBLE se triaron con v2.0 en H095. Residual: cualquier hit de cola eyeballeado pre-v2.0 que no se haya re-tocado, si reapareciera.
**Referencias cruzadas:** H094. B102. M15. H095.

---

### M18 — Capa de anotación LLM para distinciones semánticas finas (futuro)

**Origen:** H095 (`RESOLUCION_NO_RECURRIBLE`). El regex captura robusto el hecho de superficie («la Corte invocó la irrecurribilidad de sus propias decisiones para rechazar este recurso») pero NO distingue holding de obiter, ni la causal-vehículo (recusación/competencia/depósito) del fundamento operativo. Esa distinción requiere comprensión lectora, no patrones.
**Regla / acción:** para N chico (p.ej. los 12 de RNR) la codificación fina se hace A MANO (más confiable que regex o LLM, y ya se hizo en H095). Para escala (otras causales, miles de casos), una capa de anotación LLM SEPARADA del pipeline determinista, con protocolo propio (muestreo, acuerdo inter-codificador, validación contra codificación manual); nunca mezclada en el pipeline de regex. La heterogeneidad misma —la Corte usa la doctrina a veces como holding, a veces como respaldo mientras decide el fondo— es además hallazgo para la tesis.
**Estado:** no diseñado, frente futuro.
**Referencias cruzadas:** H095. RESOLUCION_NO_RECURRIBLE. B104.

---

### M19 — Estudio de validación contra ground truth (error de medición del dataset)

**Origen:** H097 (publicación Dataverse v2.0). Surgió de la pregunta sobre la solidez estadística del pipeline para uso empírico. Hasta H096 lo verificado es REGRESIÓN (`check_regresion.py`: «no rompí lo que andaba»), distinto de EXACTITUD («qué fracción de las filas es correcta contra verdad de campo»). El error de medición del dataset hoy NO está cuantificado.
**Diagnóstico:** el pipeline es un censo determinístico, no una muestra → no hay error de muestreo; el error es SISTEMÁTICO (sesgo de extracción/clasificación), no aleatorio, y NO decrece con n (tener 5862 casos no compra precisión sobre el sesgo). Confiabilidad por capas: campos estructurales (caso_id/tomo/fecha/carátula) casi exactos; detección de votos/firmas intermedia (bordes conocidos: conjueces, sustitutos, outliers residuo→dispositivo/firma); clasificaciones semánticas (`outcome`, `causa_inadmisibilidad`, `tipo_cuestion_federal`) las más ruidosas. Residuales como incertidumbre visible: `outcome` "otro" 11.7%, `tipo_voto_sep` indeterminado 1330. Cobertura incompleta (faltan 335/336, parqueados B098/B099) → el marco poblacional es incompleto y hay que declararlo.
**Plan (H098):** muestra aleatoria n≈300–400 casos; codificación manual contra el `.md` con `scripts/diagnostico/extraer_caso.py`; exactitud por columna con IC; precisión/recall POR VALOR en las columnas de clasificación (un global "94%" puede esconder una categoría chica acertada al 40%); idealmente doble codificación (o codificación ciega en dos momentos) para inter-coder reliability — es lo que tiene el SCDB y lo que pedirá un evaluador. Salidas: sección "Reliability / known limitations" para el CODEBOOK con el encuadre completo (census determinístico, error sistemático no cuantificado, residuales, cobertura incompleta, validación) y, si la validación dispara correcciones, recalibrar el parser bajo la red M12. Si NO toca el parser, candidato a dataset v2.1 (cambio de metadatos/docs = versión menor en Dataverse).
**Estado (H098):** parte de campo EJECUTADA. Codificación ciega del Marco A (292 fallos; `sumario_con_link` fuera) en los 7 campos `cod_*` contra el bloque de cada caso → 8 `cod_marco_A_lote_NN.csv`, planilla mergeada `planilla_codificacion_v18_15_MARCO_A_codificado.csv`, `HALLAZGOS_validacion_Marco_A_v18_15.md`. Cruce 1-a-1 con los bundles, sin huecos. Reglas firmes: `outcome` por la cascada del parser como desempate en multi-verbo (semántica codificada y anotada donde choca con la cascada); `tipo_cuestion_federal` solo a REX/queja; `causa` solo a dismissals y leída del considerando; `caratula_ok` cnc vacío→1 / coincide→1 / fragmento-cita-expediente-caso distinto→0; `fecha_ok`=1 si la fecha de planilla está en el bloque. AMBIGUO donde el texto no decide (outcome 9, causa 31, fecha 11, tipo_cf 1, carátula 1, queja_res 7). Hallazgos → B105/B106/B107 nuevos; `caratula_ok=0` 48/292 (16,4%; grueso residuo, amplía B043/B089/B096); fecha vacía 11/292 (sobre todo tomos 344-349). Aprendizajes de método: el atajo mecánico de carátula/fecha solo sirve limpio en el tomo 329; los scans de keyword para `causa`/`tipo_cf` se descartaron (falsos positivos por citas/votos de minoría, falsos negativos por arbitrariedad sin la palabra).
**Estado (H100):** TITULAR EJECUTADO. `analizar_validacion.py` corrido sobre los 292 fallos ciegos vs la salida del parser; resultado por campo en el encabezado (es_queja 92,1%, outcome 86,6%, queja_resultado 84,0%, tipo_cf 71,7%, causa 47,1% ralo; carátula 83,5% fiel, fecha 100%). El Marco A se confirmó SRS de los 5669 fallos (réplica seed 20260531), así que es estimación del corpus de fallos. Cuatro modos de falla cuantificados → B108/B109/B110/B111. Las divergencias de outcome reproducen B105 (frente A) y B107 (cascada) desde casos del Marco A.
**Tooling del estudio — fixes pendientes (no tocan el parser de producción):** (1) `analizar_validacion.py`: el bloque estructural cuenta `N`/`NO` pero la codificación usa `1`/`0` → reporta 0 errores de carátula/fecha aunque haya 48 carátulas mal; alinear el encoding (la fidelidad real de carátula se calculó a mano, 83,5%). (2) `muestrear_validacion.py`: filtrar `tipo_entrada=='fallo'` antes del `sample` (hoy sortea sobre los 5862 y descarta los no-fallos que caen, dejando n<300 y un sorteo de tamaño aleatorio).
**Incidente metodológico (H100):** la completación del Marco A a 300 (8 fallos suplementarios sorteados seed 20260531 sobre el pool de 5377) se codificó NO-ciega — se consultó la salida del parser de los 8 antes de fijar los códigos. Viola el protocolo de ciego que sostiene la validez del estudio. Los 8 quedan inválidos; el titular vigente es **n=292** (ciego, prior). Completar a 300 limpio exige recodificar los 8 en ventana fresca con los `.md --blind` y SIN subir la clave ni `csjn_casos.csv`.
**Estado (H102):** TITULAR CERRADO sobre **n=300**. Los 8 suplementarios se recodificaron a CIEGO en H101 (supera la codificación no-ciega de H100) y se integraron acá: cruce con `clave_supl_8.csv` posterior a la codificación, 8/8 limpio, sin colisión con los 292, regla `ok_` reproduce los 292 con 0 discrepancias → `planilla_consolidada_MARCO_A_v18_15_n300.csv`. **El titular vigente pasa de n=292 a n=300:** es_queja 92,3% [88,8–94,8], outcome 86,6% [82,2–90,0] (291 eval), queja_resultado 84,3% [76,2–89,9] (108 eval), tipo_cf 70,8% [61,1–79,0] (96 eval), causa 50,0% [29,0–71,0] (18 eval, ralo); carátula 83,6% (250/299, recomputada a mano), fecha 100% (289/289). Deltas vs n=292 no significativos (IC solapados); el n=300 CONFIRMA B108–B111. Único error nuevo de outcome: 343_p595 (procedente vs otro, POR_ELLO truncado). Desempates de H101: 329_p4150 (rechaza) y 329_p4503 (confirma) coinciden con el parser; 341_p560 carátula_ok=0 real por truncado de `case_name_cuerpo`; AMBIGUO de 329_p4356 (causa) fuera del denominador. El fix de tooling (1) se reconfirma sobre n=300 (0 carátulas mal reportadas habiendo 49) y sigue pendiente.
**Pendiente del estudio:** doble codificación / inter-coder reliability; sección «Reliability / known limitations» del CODEBOOK con el titular **n=300**; los 2 fixes de tooling de validación (ver arriba); si las correcciones (B108–B111, B105–B107) se aplican, recalibrar el parser bajo la red M12. Si no toca el parser, candidato a dataset v2.1.
**Referencias cruzadas:** H097, H098, H100, H101, H102. B105, B106, B107, B108, B109, B110, B111. M18 (complementaria). M12 (red de regresión, para recalibraciones). CODEBOOK, nota de versión Dataverse.

### M20 — Validación M20 (disposición/recursos): contaminación dev/validación del gold n300

**Origen:** H121–H122 (validación de la capa disposición/recursos, continuación de M19).
**Causa raíz:** el gold n300 se usa a la vez como set de AJUSTE y de VALIDACIÓN para las mismas variables. Cada fix tuneado sobre el gold vuelve su accuracy *in-sample* (optimista). El n300 no puede cumplir ambos roles para una misma variable.
**Inventario (H122):**
- *Tuneado sobre n300 → in-sample:* gate (B119 chequeó FP-safety en n300); B120 y B122 lo serían (sus bancos son casos del propio gold).
- *Congelado pre-gold → blind limpio:* disposición / parte_ganadora / reenvía (regex H118, frozen antes de existir el gold). Son los números fuertes para citar.
- *Por verificar → RESUELTO H140:* **el único contaminado del set H139 es el gate.** materia limpia (`derivar_materia` v3.2: refinamientos diagnosticados pero **nunca aplicados**; mide contra `cod_materia` sin haberse calibrado contra él); cf/dictamen limpios (fix nunca aplicado); disposición/parte/reenvía congelados pre-gold; vía limpia (deriva de señales pre-gold, per saltum revertido en H132). El leakage de cortes B118 no se materializó (el skip M21 es mecánico, sin umbral).
**Plan:** (1) split dev/test del n300 (ej. 200 dev / 100 held-out) ANTES de B120/B122/B111 → fixes se tunean en dev y se validan en held-out limpio; (2) ledger de uso del gold por variable/caso; (3) en CODEBOOK/tesis liderar con números congelados-pre-gold y etiquetar los tuneados como dev-set.
**Estado:** gate RESUELTO H140 (κ honesto recomputado pre-B119, ver abajo). El bloqueo sigue vigente solo para fix FUTURO que tunee sobre el gold (B120, B122, B111).
**Revisión pendiente (H126):** a discutir el alcance y el origen del bloqueo (el usuario no lo dispuso conscientemente). Distinción clave: el bloqueo aplica solo a **fitear** thresholds/regex a las labels in-sample, NO a **validar** un detector ya congelado contra el gold como held-out (eso es legítimo). El skip de M21/H126 NO lo violó: es mecánico, sin umbral, validado por flips de outcome corpus-wide (no por exactitud vs gold). Tareas: (1) re-evaluar qué más se puede aprender/validar del gold sin contaminar (p.ej. `reenvía` M22, el escrutinio de B123); (2) decidir si el bloqueo sigue, se acota a "tuneo" explícito, o se levanta con el split dev/test pre-registrado.
**Resolución del gate (H140):** κ(gate) recomputado con la predicción PRE-B119 (`is_merit_decision` del `csjn_casos.csv` en commit `d856318`, blob de git + regla canónica `derivar_recursos` `is_merit=='1'→'si'`; sanity 0 mismatches/5890; harness `kappa_confiabilidad.py`). **κ(gate) limpio = 0,813 [0,741–0,873], acuerdo 0,907, "casi perfecto"** — held-out de facto. El acuerdo 0,907 reproduce exacto el número limpio del ledger H122; el κ POST 0,933 reproduce el harness oficial. Script `scripts/diagnostico/H140/kappa_gate_preB119.py`. **Reporte (a):** 0,813 como número honesto + ledger declarado.

**(b) DEUDA NUEVA — validación in-distribution del gate FINAL:** el 0,813 es el gate PRE-ajuste; el gate del pipeline FINAL (post-B119, el del dataset publicado) no tiene validación limpia sobre el n300 (fue su dev). Requiere **muestra fresca codificada a ciego (otros ~300, fuera del gold actual)** → conecta con M19 (ventana fresca). **Estado del fix:** diseñado (muestreo fresco), pendiente.

**Referencias cruzadas:** H121, H122, **H140**. M19 (estudio madre). B119 (in-sample → limpio H140), B120, B122, B111. Capa disposición/`derivar_recursos` (blind). `kappa_gate_preB119.py` (H140). Sin ID histórico.

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

*H088: M14 ext — corpus crudo sellado en el manifiesto; cierra el último eslabón de trazabilidad de la cadena (el "Pendiente nuevo: digest del corpus crudo" de H087 queda CERRADO). Capa `corpus` DERIVADA de `source_file` (no glob, no lista a mano): 46 `.md`, sha256+n_bytes por archivo + `digest` rolled-up; fail-loud si una fuente declarada falta en disco; los parqueados 335/336 se excluyen solos y entran al desparquear sin tocar código ni conteos. `entrada_artefacto()` generalizada a raíz del repo. `generar_manifiesto.py` v1.0→1.1, schema 2→3. check_regresion [CLEAN] 4/4, --verify [CLEAN] 54, commit f8233ff. Frente datos relevado sin aplicar: B037 reclasificado no-bug (ver entrada); `is_originaria` descartada por marginal a la tesis (~1%, no toca H1–H5); `inadmisible_280` no apto para recalibración simple (ver ítem 3). M13 sigue EN PROGRESO. Candidatos inmediatos: M13 cont. (detector de sumarios), R2, frente B (materia).*

*H089: M13 cont. — detector de sumarios extraído de `procesar_archivo` a `clasificar_tipo_entrada(bloque, zonas_linea)` (refactor de extracción casi puro; única costura el reorden de `zonificar_bloque`, hoisteada arriba del detector). procesar_archivo −23 líneas. Equivalencia old↔new sobre 2009 bloques (0 discrepancias) → check_regresion [CLEAN] 4/4. parser v18.07→18.08. M13: detector HECHO; resta el bucle de votos/disidencias y el refinamiento de `status_localizacion`. Candidatos inmediatos: R2 (ítem 6), frente B/280 (cambio de comportamiento).*

*H090: R2 aplicado — dedup de la lógica 280/ac4 unificada en `classify_outcome` como sede única (ítem 6, mitad "dedup"). El inline `sin_dispositivo` de procesar_archivo colapsó a una línea. Refactor con red: equivalencia old↔new por triplicado (0/0/0) → check_regresion [CLEAN] 4/4 0-delta; parser v18.08→18.09, commit d0ced2b, manifiesto regenerado a 18.09. Diagnóstico de la frontera del 280 parcial relevado y cuantificado (70 casos, 28 'parcial' explícito; `art.280` polisémico) → alimenta el Frente 280 (ítem 3). M13 sigue EN PROGRESO (resta el bucle de votos/disidencias + `status_localizacion`). Candidatos inmediatos: M13 cont. (bucle de votos/status), Frente 280 (taxonomía del parcial, ítem 3), Frente B (materia, ítem 1).*

*H091: M13 CERRADO — extraídas las dos últimas piezas inline de `procesar_archivo`: el bucle de votos/disidencias → `detectar_votos_disidencias(bloque, lineas_excluir)` (movimiento puro, se descartó el `pass` muerto de H085) y el refinamiento de status → `refinar_status_localizacion(status_loc, apertura_rel, ancla_inicio)` (colapsa el `if/else` muerto, dos ramas con el mismo sufijo). `procesar_archivo` 513→458 líneas, ahora orquestador puro. Refactor con red sin re-golden: poc_votos (13×4 + 80k fuzz = 0), poc_status (105 exhaustivas = 0), check_regresion [CLEAN] 4/4 0-delta, manifiesto a 18.10 (sha256 sin cambios), --verify [CLEAN] 54. parser v18.09→18.10. **Con esto termina el desmonte de la función monstruo.** Candidatos inmediatos (ya sin refactor de extracción pendiente): Frente 280 (taxonomía del parcial, ítem 3, el más teed up), Frente B (materia, ítem 1), scoping por zonas (frente H089), B090 (Tier 5).*

*H092: Frente 280 / gate de admisibilidad — campo nuevo `causa_inadmisibilidad` (mitad de fondo del ítem 6, HECHA). Aditivo, vocabulario controlado de la Corte; 5 nativas (derivadas del outcome) + 4 de cola validadas (sent. definitiva 34, fuera de término 10, fundamentación autónoma 10, depósito previo 4) + residual bipartido (remite_dictamen 139, sin_causal 441); `otro` queda "" salvo causal explícita; no-gate 4633. Rename `MERIT_OUTCOMES`→`OUTCOMES_NO_FALLBACK_280` en classify_outcome (cosmético). PoC `scripts/diagnostico/H092/sub_gate.py` + check_columna. Re-golden consciente de casos (votos/zonas/editorial [OK]); parser v18.11; commit ee0a62d; --verify [CLEAN] 54. Pendiente: validar cola contra `.md` reales, candidatas de cola (salto de instancia, denegación REX, etc.) sin emitir, `causa_inadmisibilidad_parcial` (ítem 3) y reclasificación de is_merit, ambas diferidas. Candidatos inmediatos: validación de cola contra `.md` (recall), columna parcial-280, Frente B (materia, ítem 1).*

*H093: validación de la cola de `causa_inadmisibilidad` arrancada por FUERA_DE_TERMINO contra `.md` reales. Corrección importante: producción emitía 12 FUERA (no los 10 del piso del PoC de H092); el PoC lee `considerando_text` truncado a 2000 y no veía 2 hits cuyo `extempor` cae pasado el corte — son los «14 delta» de la cola que H092 reportó como «validadas» pero nunca eyeballeó. FUERA cerrado: 10 TP / 2 FP; los 2 FP (B100, 329_p5138/5316) son reposiciones contra resolución de la Corte. Fix `RE_CAUSA_FUERA_TERMINO_EXCL_DISP` anclado al por_ello, parser v18.12, 2 casos→SIN_CAUSAL, re-golden consciente, commit 7bcac83. Herramienta canónica nueva `scripts/diagnostico/extraer_caso.py`. Lecciones nuevas: M15 (A/B sobre texto idéntico; el truncado da vuelta veredictos), M16 (refacción del explorador). Pendiente inmediato: validar el resto de la cola (SENTENCIA_DEFINITIVA 44, FUNDAMENTACION 12, DEPOSITO 4 — los delta nunca eyeballeados; solo spot-check 348_p494 TP) con `extraer_caso.py`; posible causal RESOLUCION_NO_RECURRIBLE para las 26 reposiciones-desestimadas (hoy en SIN_CAUSAL); revisar la reposición hoy en DEPOSITO_PREVIO (posible mislabel); candidatas de cola (salto de instancia, etc.) aún sin emitir; columna parcial-280 (ítem 3); Frente B (materia, ítem 1).*

*H094: cierre de la cola «delta» de `causa_inadmisibilidad`. Triage de los 60 hits de cola: 12 delta (match pasado el truncado a 2000 del CSV) + 48 VISIBLE. Los 12 delta validados a mano contra `.md` reales = 11 TP / 1 FP. Bug de la herramienta de diagnóstico corregido en el camino (B102): `extraer_caso.py` <v2.0 leía el volumen equivocado en tomos partidos en volúmenes solapados (338.1/338.2) → fingió un «label fantasma» en 338_p830 (TP); fix v2.0 ancla por `source_file` + rango de líneas. Único FP (B101): 334_p419 (outcome `otro`, match en dictamen/antecedente, holding = nulidad); fix = las 4 causales de cola gateadas a `OUTCOMES_GATE_GENERICO`; A/B = 1 fila exacta, re-golden, [CLEAN], parser v18.13 (SENTENCIA_DEFINITIVA 44→43). M17 nueva (revalidar cola previa sobre tomos partidos, contaminable por el bug de la herramienta). Pendiente inmediato: los 48 hits VISIBLE de la cola sin triar; causal RESOLUCION_NO_RECURRIBLE para las 26 reposiciones-desestimadas (hoy en SIN_CAUSAL); revisar la reposición en DEPOSITO_PREVIO; candidatas de cola sin emitir; columna parcial-280 (ítem 3); Frente B (materia, ítem 1).*

*H095: causal nueva `RESOLUCION_NO_RECURRIBLE` emitida (irrecurribilidad de las decisiones propias de la Corte, Fallos 316:1706). Validados los 44 hits VISIBLE de la cola pendientes de H094 (SENTENCIA_DEFINITIVA 32/32 TP, FUNDAMENTACION 9/9 TP, DEPOSITO 1 TP + 2 FP → B103). Diseño: el ancla del dispositivo (por_ello, 29 candidatos) mal-etiquetaba ~80% (lo confirmó leer 16 `.md`); la causal se ancla en el FUNDAMENTO del considerando, chequeada ÚLTIMA en el bloque gate-genérico (por construcción no le roba a SD/FUND/DEPOSITO/FUERA) + guard de hace-lugar (excluye 344_p1904). Decisiones taxonómicas: recusación NO es gatekeeping (incidente → residual); depósito-mérito ya vive en DEPOSITO_PREVIO (lo residual es revocatoria-sobre-intimación → B103); competencia es eje materia (Frente B; `outcome=competencia` 603 ya la captura), no inadmisibilidad. PoC `scripts/diagnostico/H095/poc_resolucion_no_recurrible.py`; A/B = 12 SIN_CAUSAL→RNR; check_regresion [FAIL] solo esas 12 celdas, votos/zonas/editorial [OK]; re-golden consciente; parser v18.13→18.14 (RNR 0→12, SIN_CAUSAL 425→413, gate total sin cambio 1036). B103 ABIERTO (2 FP DEPOSITO), B104 NUEVO (running-heads OCR mid-palabra, miss de 329_p5316), M17 saneado para FUERA, M18 NUEVO (capa LLM para holding/obiter, futuro). Candidatos inmediatos: B103 (guard DEPOSITO), Frente B (materia/competencia, ítem 1), columna parcial-280 (ítem 3), candidatas de cola sin emitir.*

*H096: B103 CERRADO — guard EXCL en el bloque DEPOSITO de `clasificar_causa_inadmisibilidad`. Los 2 FP (330_p1025, 343_p166) son revocatorias/planteos contra una resolución ANTERIOR de la Corte: la frase del depósito describe el antecedente atacado, no un gate sobre el recurso presente. `RE_CAUSA_DEPOSITO_EXCL` anclado al considerando («la resolución de fs. X que desestimó … no haberse … el depósito»), sumado como `and not RE_CAUSA_DEPOSITO_EXCL.search(co)` a la condición DEPOSITO (mismo discriminador holding-vs-antecedente que B100/B101; de nivel considerando porque 343_p166 dice «planteo», no «revocatoria»). PoC `scripts/diagnostico/H096/poc_b103_guard_deposito.py`: A/B OLD↔NEW sobre texto idéntico = 2 flips exactos, universo de cambios ⊆ DEPOSITO del golden (el guard solo saca); capa anti-M15 reconstruye el bloque completo del `.md` y exige EXCL solo en los 2 FP (348_p805, TP truncado a 2000 en el CSV, da EXCL_full=False). Hallazgo metodológico: correr la función sobre el `considerando_text` del CSV no reproduce el golden para causales con ancla pasada el corte (329_p440 REMITE_DICTAMEN) → el A/B es OLD↔NEW sobre el mismo texto, el delta de conteos se deriva del golden. check_regresion [FAIL] solo esas 2 celdas (git diff: 2 filas, resto byte-idéntico), votos/zonas/editorial [OK]; re-golden consciente (csjn_casos sha256 8d6360599442); parser v18.14→18.15 (DEPOSITO_PREVIO 4→2, INADMISIBLE_SIN_CAUSAL_EXPLICITA 413→415, gate total sin cambio 1036). Pendiente: B104 (running-heads OCR mid-palabra), Frente B (materia/competencia, ítem 1), columna parcial-280 (ítem 3), candidatas de cola sin emitir.*

*H097: publicación del dataset v2.0 a Harvard Dataverse (en review). Subidos los 5 CSV del golden v18.15 + `CODEBOOK.md` v1.1 + `README.md` publicable + `_manifest.json` + scripts de pipeline y de mapa; limpieza del upload anterior (test/auditoría + los `.tab` del ingest tabular). NO toca pipeline ni outputs (parser v18.15, golden sin cambios). M19 NUEVO: estudio de validación contra ground truth para cuantificar el error de medición del dataset — diseñado, es el trabajo de H098 a pedido del usuario. **Próxima sesión (H098):** (1) M19 — muestra aleatoria n≈300–400, codificación manual con `extraer_caso.py`, exactitud + precisión/recall por columna con IC, doble codificación para inter-coder reliability; (2) RETOMAR los frentes abiertos de la lista de abajo: Frente B/materia (ítem 1), B090 Tier 5 (ítem 2), parcial-280 (ítem 3), sin_firma residual (ítem 4), B104 running-heads OCR. Pendientes de la publicación Dataverse (no de pipeline): confirmar si los CSV ingestaron — el `.tab` archivable no matchea el sha256 del manifiesto, la verificación va contra el «original format»; si ingestaron, aclararlo en el README publicable o bloquear el ingest; release note pública 1.x→2.0 y versión previamente publicada sin confirmar (pestaña Versions no leída).*

*H098: M19 — parte de campo EJECUTADA. Codificación ciega del Marco A (292 fallos) en los 7 campos `cod_*` contra el bloque de cada caso; cruce 1-a-1 con los bundles, sin huecos. Productos: 8 `cod_marco_A_lote_NN.csv` + planilla mergeada + `HALLAZGOS_validacion_Marco_A_v18_15.md`. `caratula_ok=0` 48/292 (16,4%), fecha vacía 11/292; AMBIGUO outcome 9 / causa 31 / fecha 11. Hallazgos → B105 (`por_ello`=considerando/feria/oficio en 9 casos), B106 (`case_name_cuerpo` vacío con «Vistos los autos» presente: Autolatina, Swiss Medical), B107 (cascada de outcome mal-buckea negación y excepción de incompetencia). NO toca pipeline ni outputs (parser v18.15). **Pendiente del estudio (próxima sesión):** correr `analizar_validacion.py` vs `csjn_casos.csv` para el TITULAR (exactitud global + IC de Wilson + precisión/recall por valor); doble codificación / inter-coder reliability; sección «Reliability / known limitations» del CODEBOOK; recalibrar bajo M12 si dispara correcciones. Frentes de pipeline siguen abiertos (ver lista): Frente B/materia (ítem 1), B090 Tier 5 (ítem 2), parcial-280 (ítem 3), sin_firma residual (ítem 4), B104 running-heads OCR.*

*H102: M19 — TITULAR CERRADO sobre n=300. Integrados los 8 suplementarios recodificados a CIEGO en H101 (supera la codificación no-ciega de H100; el titular vigente pasa de n=292 a n=300). Cruce 8/8 limpio, regla `ok_` reproduce los 292 con 0 discrepancias; deltas vs n=292 no significativos; el n=300 confirma B108–B111. Producto `planilla_consolidada_MARCO_A_v18_15_n300.csv`. NO toca pipeline ni outputs (parser v18.15). **Pendiente del estudio:** doble codificación / inter-coder reliability (kappa); sección «Reliability / known limitations» del CODEBOOK con el titular n=300; los 2 fixes de tooling de validación (`analizar_validacion.py` encoding 1/0, `muestrear_validacion.py` filtro `tipo_entrada=='fallo'`); recalibración bajo M12 si se aplican B105–B111. Frentes de pipeline abiertos sin cambios: Frente B/materia (ítem 1), B090 Tier 5 (ítem 2), parcial-280 (ítem 3), sin_firma residual (ítem 4), B104 running-heads OCR.*

*H108: capa-fuente `es_queja` IMPLEMENTADA (parser v18.22→18.23; +225 quejas detectadas por carátula —`RE_CARAT_QUEJA` ancla fuerte + guard de cita—; es_queja 2056→2281, queja_resultado sin_clasificar 38→263; precisión de flip 98,7% leyendo 7 fallos; golden re-sellado e7e59ca; 3 FP residuales —332_p1960/343_p1987/331_p856— downstream de B115). **Hallazgo grande: B115 NUEVO** — merge/caso-perdido por hueco en índice de partes (familia B009): ~70 fallos fundidos en la entrada indexada anterior (Arriola, Acosta perdidos como caso propio); root cause aguas arriba (catálogo/índice), parser inocente; set-diff catalogo vs casos 0/0; detector `apertura≥2` (103 → 71 merge real + 32 acumulación); fix no diseñado. CODEBOOK v1.3 local (no publicado), ya stale en es_queja. **Próximo: arco B115** (conseguir `csjn_editorial_indice_partes.csv` o el `.md` del índice, resolver el fork índice-parseo vs body-scan, dimensionar fino, diseñar fix; al cerrarlo caen los 3 FP de es_queja). Dataverse desactualizado (v18.15 publicado vs v18.23 actual). M19 sin cerrar (inter-coder kappa). Frentes abiertos sin cambios: Frente B/materia (ítem 1), B090 Tier 5 (ítem 2), parcial-280 (ítem 3), B104 running-heads OCR.*

*H109: **B115 CERRADO** — `construir_catalogo` v1.0→1.01 (recorte del inicio del bloque de índice de partes en 331-334; `RE_SUBSECCION_NOMBRES` + Validación 1 acepta header de subsección + filtro anti-polución). A/B sobre LibroVol332.3: 481→515 entradas, 1963 capturado, 0 pérdidas. Catálogo +283 ids (28 B115 [331:12/332:8/333:2/334:6] + 255 tomo 335); `csjn_casos` 5862→5890; swallow Massuh/Arriola roto. QA 28: 27 ok + 1 (Astiz 334_p1063) `sin_mapa`→B116. **B116 logueado** (lado cuerpo). Golden NO re-sellado (deuda → saldada en H110).*

*H110: **B116 CERRADO** — `detectar_paginas` v1.0→v1.01. Causa raíz (leída en `LibroVol334.3.md`): las páginas de apertura de sección suprimen el running-head superior; el cuerpo arranca con banner de mes/Acordadas. Fix: `interpolar_secciones` emite headers sintéticos guiados por catálogo + anclados al banner + región file-local; CSVs `mapa_paginas_inferidas.csv`/`_sin_banner.csv`; schema del mapa intacto. Validación: 44 inferidas [11×4], sin_banner=0; `pagina_no_en_mapa` 299→255 (44 a 0; 335 intacto 255); Astiz `ok`/`improcedente`; perímetro confinado a 331-334 (0 nuevos/0 desaparecidos/84 modificados=21/tomo, 0 fuera, 15 tomos byte-idénticos; bleed-through de vecinos corregido como bonus; editorial +1 en 331 = afloramiento de B115). Re-golden + **baseline re-sellado** (salda la deuda de H109) → check_regresion [CLEAN] 4/4. NO toca 343_p1987 (mis-scope del prompt: tomo 343 sin `pagina_no_en_mapa`; su FP de `es_queja` tiene otra causa, pendiente aparte) ni 335-336 (excluidos hasta fuente confiable). Frentes abiertos: Frente B/materia (ítem 1), B114 (tribunal_origen fragmentado), parcial-280 (ítem 3), B104 (running-heads OCR), 343_p1987 (FP es_queja, causa distinta), M19 inter-coder kappa, Dataverse desactualizado (v18.15 publicado vs actual), CODEBOOK v1.3 sin publicar.*

**Prioridad H169 — B136 CERRADO (`is_merit` de la originaria de fondo).** El eje de mérito SCDB ya incluye las originarias que resuelven el fondo: detector `es_de_fondo` en `clasificador_disposicion.py` v1.10, reusado por `parser.py` v23.0 (`is_merit`) y `es_revision_fondo` v0.6 (deriver) → ejes consistentes. 133 de-fondo; `is_merit` 2870→3003, `es_revision_fondo` 2816→2949; `[CLEAN]`; `--verify [CLEAN] 64`; commit `10f2c5c`. **Teed up, en orden:** (a) **κ ciego nuevo de `es_de_fondo`** sobre muestra de originarias — pre-requisito para republicar Dataverse; (b) **M35-④ + Dataverse** (doi:10.7910/DVN/TJTVKW): de-publicar el fósil `csjn_editorial_indice_partes.csv` + subir manifest, desbloqueado por B136 pero esperando el κ; (c) **B137 / H170** — audit de `clasificar_tipo_voto` (error silencioso D-por-fallback corpus-wide; `auditar_tipo_voto_D.py`); (d) **2ª pasada de-fondo apelados** (~80 «hacer lugar a la demanda» hoy en `no_revision_demanda` + ruteo de negación «no hacer lugar»→reject); (e) lecturas doctrinales: par impugnación tributaria originaria (330_p2478/330_p1927), 3 intimaciones estructurales (330_p111/343_p1704/345_p1498) + 331_p1622 (por_ello roto); (f) FPs de `is_originaria` (330_p520/331_p2119/341_p536/343_p38/344_p2543/345_p61); (g) auditoría deshif global (regex del parser que no pasan por `_unhyphenate`/`norm`). 335-336 siguen excluidos.

**Prioridad H154 — M29 capa 1 (partes desde el epílogo) CERRADA.** El Eje B (recurrente/recurrido = petitioner SCDB) ya se deriva del epílogo editorial: `extraer_epilogos.py` v0.2 + `derivar_partes.py` v0.2 (NUEVOS, capa-deriver, parser intacto) → `csjn_casos_epilogo.csv` (5697 1:1) + `csjn_casos_partes.csv` (recurrente_ok **3633 = 63,8% fallos / 84% epílogos**, con rol). Manifest a 10 canónicos (v1.7), re-sello esperado [CLEAN] 65. **Teed up para H155, en orden:** (a) **frente 2 — formato viejo** (~365 epílogos `Nombre del actor:`/`Parte demandada:` que listan partes sin marcar el recurrente → 2ª gramática, la de mayor ganancia; primero verificar si traen marca de recurso más abajo que el flexible no agarra, o si solo listan partes); (b) **frente 3 — arrastre de zona** (~103, tocaría parser/re-golden, evaluar ROI, cf. B117); (c) **¿`epilogo`/`partes` en el CODEBOOK y refresh de Dataverse?** (decisión separada); (d) **B130/reenvia** (coding manual, pausado); (e) **M25 detector de texto** de las 7 inversiones de rol (ahora con el rol procesal disponible). El gold de M25 NO se tocó en M29 (decisión: no acumular incertidumbres). 335-336 siguen excluidos.

**Prioridad H152 — documentación de repo + higiene + leftover H148/H149 CERRADOS.** 6 READMEs por directorio colocados; κ promovido a `scripts/validacion/` (demo en disco idéntica, parte 0,784); `.gitignore` reescrito (intermedios conservados, forense/`docs` fuera del tracking). **Leftover H148/H149 SALDADO:** `clasificador_causa.py` v0.4→v0.5 (M27 `INTERPOSICION_INCORRECTA` §1.2.2 reordenado al final de la cola = solo drena SIN_CAUSAL + H151 recall-gap `remite-dictamen(disp)`), `recursos.csv` re-derivado, `_manifest.json` re-sellado `--verify [CLEAN] 63` (reorden empíricamente nulo, `INTERPOSICION` en 2). **Teed up para H153, en orden:** (a) **reescritura del CODEBOOK** (sigue v1.3/`outcome` legacy → ejes M26 como variables + crosswalk SCDB contra nombres en español + tabla κ desintercalada reemplazando accuracy M19 + bump de versión); (b) **refresh de Dataverse** (publicado pre-M26, `doi:10.7910/DVN/TJTVKW`); (c) **B130/reenvia** (codear 42 del universo de reversión leyendo `scripts/validacion/reenvia_42.md` → recomputar → reportable sobre ~113); (d) `auditar_fallo.py` carve-out (tool vs `validacion/`). 335-336 siguen excluidos.

**Prioridad H111 — B114 CERRADO (`tribunal_origen` normalizado).** El pre-requisito del Frente B/materia está saldado: `find_tribunal_origen` v12 recupera el nombre completo del tribunal (1129 celdas), el corte de línea del OCR ya no fragmenta el campo, y el lookup tribunal→fuero es viable (colapso a fuero demostrado en el PoC). De paso se saneó el harness: la escritura de CSV es LF determinística (`lineterminator="\n"`), el contrato de regresión vuelve a ser estable. **Próximo natural: Frente B/materia capa 1** — lookup tribunal→fuero→materia sobre la columna ya limpia; cerrar el vocabulario controlado de materias (validar contra Anuario H083) ANTES de extraer; medir cobertura; después capas 2 (provinciales/normas, el bolsón otro/provincial≈1348) y 3 (originaria). Otros candidatos sin cambio: parcial-280 (ítem 3); B104 (running-heads OCR mid-palabra); 343_p1987 (FP `es_queja`, causa propia); M19 inter-coder kappa + sección Reliability del CODEBOOK; sync CODEBOOK v1.3 + Dataverse (v18.15 publicado → v18.24 actual). 335-336 excluidos hasta fuente confiable.

**Prioridad H110 — arco B115/B116 CERRADO (familia B009 saldada en 331-334).** Tanto el lado-índice (B115, `construir_catalogo`) como el lado-cuerpo (B116, `detectar_paginas`) están cerrados; los 331-334 quedan localizados limpio y el baseline re-sellado. Candidatos para la próxima: Frente B/materia (ítem 1) con su pre-requisito B114 (tribunal_origen fragmentado por OCR); parcial-280 (ítem 3); B104 (running-heads OCR mid-palabra); diagnóstico de 343_p1987 (FP de `es_queja` con causa propia, no era B116); cierre de M19 (inter-coder kappa + sección Reliability del CODEBOOK); actualización del Dataverse (v18.15 publicado → actual) y publicación del CODEBOOK v1.3. 335-336 siguen excluidos hasta tener fuente confiable/legible.

1. **Variable `materia` (inferida desde tribunal_origen).** Normalizar
   tribunal_origen (limpiar OCR, unificar variantes provinciales), mapear a
   materia por keywords. ~1454 sin_marcador. Habilita análisis temático.
2. **B090 — Tier 5 dispositivo embebido.** 33 sin_dispositivo con firma. PoC pendiente.
3. **Recalibrar `is_originaria` (art.117) / `inadmisible_280` (art.280) / art.4.**
   Regexes dependían de considerando_text con editorial pre-B010; recalibrar
   contra texto limpio. Toca variables centrales de las hipótesis.
   **(H088, relevado):** `is_originaria` descartada por marginal a la tesis
   (166 `outcome=originaria`, ~1%; 58 con `is_originaria=0` quedan como testigos
   si alguna vez se retoma, pero no toca H1–H5). `inadmisible_280` SÍ toca H1
   (gestión del docket) pero la recalibración no es trivial: la mención de
   art.280 en el texto está contaminada (montos tipo `$ 277.280`, fojas, citas
   de Fallos t.280) y, sobre todo, hay casos de **280 parcial** —el 280 voltea
   algunas pretensiones y el caso sigue resolviéndose al fondo (`330_p2146`,
   `340_p1280`)—. Antes de recalibrar regex hay que decidir taxonómicamente si
   un 280 parcial cuenta como `inadmisible_280`. Es sesión de diseño, no patch.
   **(H090, frontera cuantificada):** los casos con `art.280` en el considerando
   pero outcome merit son **70** — 28 con 'parcial' explícito en el dispositivo
   ("se hace lugar parcialmente a la queja y al REF": concede parte + 280 al
   resto, el mixto genuino) + 42 sin 'parcial'. Dentro de los 42, `art.280` es
   **polisémico**: varios refieren al 2º/último párrafo (memorial/traslado), no
   al rechazo discrecional del 1er párrafo → mencionar 280 ≠ rechazo por 280; la
   detección por mención cruda sobrecontaría. El short-circuit de merit del
   dispositivo mantiene a los 70 bien como merit (no contamina el outcome).
   Decisión de fondo: el 280 opera a nivel **agravio**, no caso, y la columna
   `outcome` (case-level) no puede representar gatekeeping parcial. Extractor de
   la frontera: `scripts/diagnostico/H090/extraer_por_outcome.py` (filtro
   `--considerando-regex` + `--exclude-outcome`).
   **(H092):** el campo `causa_inadmisibilidad` (gate, nivel caso) ya está
   implementado (ver ítem 6). Los 70 de la frontera quedan con `causa=""`
   porque llegaron al fondo (el short-circuit de merit los mantiene como merit).
   Lo que queda pendiente del 280 parcial es una columna
   `causa_inadmisibilidad_parcial` que anote el 280 a nivel agravio sin tocar el
   `outcome` ni la columna terminal — DIFERIDA.
4. **sin_firma residual (16 casos pre-335)** — auditar residuo.
5. **Análisis para hipótesis:** H2 red de citas, secretaría letrada, expansión H3, dashboard.
6. **Diseño taxonómico: outcome como par gate+action.** **(H090, mitad HECHA):**
   R2 cerró la parte "dedup" — la lógica 280/ac4 estaba duplicada entre
   `classify_outcome` (dispositivo no-merit) y un bloque inline de
   `procesar_archivo` (`sin_dispositivo`); ahora `classify_outcome` es la sede
   única (maneja `por_ello_text` vacío con base `sin_dispositivo`). check_regresion
   [CLEAN] 0-delta, parser v18.09. Pendiente la mitad de fondo: modelar el outcome
   como par gate+action explícito (separar admisibilidad de mérito), que conecta
   con el ítem 3 (el 280 a nivel agravio).
   **(H092, mitad de fondo HECHA):** campo nuevo `causa_inadmisibilidad` (nivel
   caso, ADITIVO, no relabel del outcome de mérito). Vocabulario controlado de la
   Corte; la causal se ata al recurso decidido. Emite 5 nativas (derivadas del
   `outcome`) + 4 de cola validadas a mano (sent. definitiva, fuera de término,
   fundamentación autónoma, depósito previo) + residual bipartido
   (`INADMISIBLE_REMITE_DICTAMEN` / `INADMISIBLE_SIN_CAUSAL_EXPLICITA`). `otro`
   queda `""` salvo causal explícita. Invariante `causa != "" ⇔ gatekeeping`
   (0 fugas de mérito/otro). Hecho también: rename `MERIT_OUTCOMES`→
   `OUTCOMES_NO_FALLBACK_280` en `classify_outcome` (cosmético). PoC en
   `scripts/diagnostico/H092/sub_gate.py`. parser v18.11, commit ee0a62d,
   re-golden consciente de casos. **Pendiente del ítem:** validar la cola contra
   `.md` reales (eyeball + recall); habilitar las candidatas de cola
   (`SALTO_DE_INSTANCIA`, `FALTA_DENEGACION_REX`, `FALTA_RELACION_DIRECTA`,
   `FALTA_INTRODUCCION_OPORTUNA_CF`, `TRIBUNAL_SUPERIOR_CAUSA`) tras validación;
   reclasificación de `is_merit` (rechaza/competencia/originaria → merit) como
   cambio de comportamiento aparte.

*Pendientes del módulo `estadisticas/` (H083, frente analítico, fuera del pipeline):*
- **Taxonomía oficial de inadmisibilidad de la Corte (vocabulario controlado para el
  campo gate, ítems 3 y 6).** Archivo:
  `estadisticas/output_tableau/resueltos_2025/Recursos_según_cumplimiento_de_requisitos__causa_inad.csv`
  (hermanas: `__causa_inad_3.csv` con porcentajes; `__tipo_des_causas.csv` con el split
  admisible/inadmisible por tipo de recurso). NO son solo 280 + ac4: son ~22 causales.
  Conteos de la fila `%all%` (docket completo 2025, NO joineable caso a caso con nuestro
  corpus publicado — sirven como **vocabulario** y como **techo de validación** por
  causal cuando parseemos nuestro 2025: perforar el techo = bug):

  | causal (lengua de la Corte) | n 2025 |
  |---|---|
  | ART. 280 CPCCN | 12.546 |
  | ACORDADA 4/2007 | 4.549 |
  | FALTA DE SENTENCIA DEFINITIVA | 1.193 |
  | FALTA DE FUNDAMENTACIÓN | 590 |
  | DEPÓSITO PREVIO | 467 |
  | CUESTIÓN ABSTRACTA | 411 |
  | DESISTIMIENTO | 385 |
  | FUERA DE TÉRMINO | 287 |
  | FALTA DENEGACIÓN DEL REC. EXTRAORDINARIO | 144 |
  | CADUCIDAD DE LA INSTANCIA | 92 |
  | SALTO DE INSTANCIA | 29 |
  | AUTO DE CONCESIÓN (art. 257) | 25 |
  | FALTA DE FIRMA | 23 |
  | OTRAS CAUSALES | 21 |
  | PROCEDIMIENTO | 18 |
  | TRASLADO (art. 257) | 17 |
  | SIN FÓRMULA | 12 |
  | N/C | 9 |
  | TRIBUNAL SUPERIOR DE LA CAUSA | 9 |
  | MAL PRESENTADO | 9 |
  | PRESENTACIONES VARIAS | 5 |
  | FALTA DE INTRODUCCIÓN OPORTUNA DE LA CUESTIÓN FEDERAL | 2 |
  | FALTA DE RELACIÓN DIRECTA | 1 |

  Total inadmisibles 20.823 / 24.545 resueltos (84,8% del docket); 280+ac4 = 82% de los
  inadmisibles, cola larga el resto. Hoy el parser resuelve limpio 5 (280, ac4, abstracto,
  desistimiento, caducidad); la cola (falta de sentencia definitiva, falta de fundamentación,
  depósito previo, fuera de término, falta de denegación del REX…) cae a `desestima` genérico
  (541 casos) o `inadmisible`/`otro` → blanco de sub-clasificación del campo gate. Salvedad:
  verificar desfase tomo/año-calendario antes de usar el techo como cota dura.
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

### M13 — Descomposición de procesar_archivo (función monstruo) — CERRADO H091

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
- **H089 — APLICADO.** Detector de sumarios extraído a
  `clasificar_tipo_entrada(bloque, zonas_linea)` (única costura: `zonificar_bloque`
  hoisteada arriba del detector). Equivalencia old↔new sobre 2009 bloques (0) →
  check_regresion [CLEAN] 4/4. parser v18.07→18.08.
- **R2 (H090) — APLICADO.** Fallback 280/ac4 unificado en `classify_outcome` como
  sede única (el bloque inline `sin_dispositivo` de procesar_archivo colapsó a una
  línea). parser v18.08→18.09.
- **H091 — APLICADO (cierra M13).** Las dos últimas piezas inline extraídas:
  `detectar_votos_disidencias(bloque, lineas_excluir) → (n_votos_svoto, n_disidencias,
  inicio_votos_indiv, marcadores_votos)` (movimiento puro del bucle; se descartó el
  `pass` muerto que dejó H085 al sacar la detección de dispositivo) y
  `refinar_status_localizacion(status_loc, apertura_rel, ancla_inicio) →
  status_loc_final` (colapsa el `if/else` cuyas dos ramas producían el mismo sufijo
  — dead branching, behavior-preserving). `procesar_archivo` 513→458 líneas, ahora
  orquestador puro. Validación: poc_votos (13 dirigidos × 4 máscaras de exclusión +
  80k fuzz = 0 discrepancias), poc_status (105 combinaciones exhaustivas = 0),
  check_regresion [CLEAN] 4/4 (5862/27463/140956/151, 0-delta), manifiesto regenerado
  a 18.10 (sha256 sin cambios), --verify [CLEAN] 54. parser v18.09→18.10.
**Pendiente:** ninguno — M13 cerrado. `es_originaria` quedó fuera de alcance (ya era
top-level desde antes de M13; candidata de recalibración art. 117, no de extracción).
B090 (Tier 5) entraría como 6ª configuración del motor `_barrer`, no como copia.
**Referencias cruzadas:** H084, H085, H086, H089, H090, H091. M12. B090.

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

### B122 — Zonificador: dispositivo cortado/ausente, carátula faltante, contaminación entre fallos — CERRADO H126 (dispositivo truncado)
**Componente:** parser (segmentación / detección de zonas).
**Origen:** H121 (notas_m20 del gold M20).
**Causa raíz:** la detección de zona dispositiva y la frontera de fallos falla en una clase de casos; el `por_ello` queda cortado por header, ausente, o con texto de otro fallo. **Mecanismo confirmado H123:** el chunk de `_barrer` (~3091) topa a 6 líneas o al primer `.`; el running-head intercalado (línea propia) gasta presupuesto y el chunk corta sobre el banner antes del `.` real → `por_ello` truncado. La `RE_PAGE_HEADER` existente (línea 204) NO lo agarra: está anclada a frase-sola/número-solo, pero el banner real es `número + frase + número` → hace falta `RE_RUNNING_HEAD`.
**Diagnóstico/evidencia:** 25 casos zona-flagged en n=300. Impacto medido en el gate: 1 FP (340_p431) + 5/9 FN (330_p1907, 332_p2625, 334_p941, 344_p2393, 345_p583). Contaminación entre fallos: 334_p941. Carátula faltante: 330_p50, 332_p2625, 337_p481, 345_p241, 348_p1378. **Banco ampliado H123:** 42 casos no-merit con `por_ello` truncado por banner + señal jurisdiccional (incompetencia/competencia originaria) en el considerando, que cayeron a `otro` en vez de competencia/originaria (la cláusula determinante quedó pasada el corte). Cruce gold: 3/42 en el n300, gate parser==gold **3/3** (son no-merit de verdad — el gate NO se equivoca; lo que se pierde es la disposición específica), 2/3 marcados `ZONA` a mano. Banco en `B122_banco_truncado_jurisdiccional_n42.csv`. **Aclaración B118:** para el subconjunto merit el verbo de fondo sobrevive antes del banner → outcome correcto; la pérdida es de granularidad de disposición en la cola no-merit, NO de clasificación de fondo.
**Estado de verificación:** `confirmado_cuantificado` (notas_m20 + cruce gate + banco 42 cruzado contra gold).
**Resultado H125 (PoC corpus-wide en disco, n=5697):** el lever real es el **skip de vacías en el presupuesto del chunk de `_barrer`**, NO el masking — el presupuesto lo comen el banner Y las líneas en blanco del OCR a su alrededor; saltearlas libera el chunk hasta el `.` real. Medido: +masking solo 0 flips / +skip solo 50 / +masking+skip 64. `otro→competencia` 37; `otro` 528→473; `competencia` 877→914. Las 9 transiciones no-`otro` verificadas con `diag_textos` son todas ganancias (acceso→fondo, H118/M20); 0 regresiones. El masking suma +14 (limpia ruido donde el banner tapaba el regex).
**Estado del fix (H126):** **INTEGRADO** — skip en `_barrer` (parser v18.26→v19.0). Resultado en disco sobre el corpus completo: `competencia` 877→**910** (+33), `otro` 528→**483** (−45), 50 flips de outcome (33 otro→competencia + acceso→fondo), 487 `por_ello` con la cola recuperada (todo extensión, 0 pérdida vía spot-check), votos solo en columnas denormalizadas (identidad intacta), considerando/firma/zonas/editorial byte-idénticos. Re-golden [CLEAN] + manifest v19.0. **Cierra la mitad de dispositivo-truncado de B122** (y B118). El skip recuperó ~33 de las 37 `competencia` previstas; los ~4 restantes son territorio del masking (Fase 2). **Pendiente (NO cerrado por el skip):** carátula faltante (330_p50, 332_p2625, 337_p481, 345_p241, 348_p1378) y contaminación entre fallos (334_p941) — frentes de zonificación aparte. **M21 Fase 2 (masking):** gated, ver M21. Perilla `guion` DROP (redundante, downstream ya deshifena).

### B144 — Cascada de outcome matchea dentro de un APERCIBIMIENTO (caducidad anunciada ≠ caducidad dispuesta)

**Componente:** parser (`classify_outcome`, eje legacy de dispositivo).
**Origen / fuente del diagnóstico:** H181 (adjudicación del diff de M21 F3, `dump_diff_h181c`).
**Causa raíz:** el detector de `caducidad` matchea el sustantivo dentro de la cláusula de apercibimiento: «difiérese la consideración… **bajo apercibimiento de** declarar la caducidad de la instancia» → `outcome=caducidad`, cuando lo DISPUESTO es un diferimiento. La amenaza no es la disposición.
**Diagnóstico / evidencia:** 330_p1525 (pe completo destapado por F3, leído en H181). Cardinalidad corpus-wide sin medir.
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** guard de ventana previa («bajo apercibimiento de», W~40 antes del match) en la cascada; medir la superficie por outcome ANTES de cablear (puede afectar a más outcomes que caducidad). NO toca mérito (el gate ya da `no`, verificado).
**Estado del fix:** no diseñado.
**Referencias cruzadas:** M21 F3 (lo destapó), B107 (familia de guards de la cascada), B123 (cola de `otro`). H181. Sin ID histórico.

### M21 — Recuperación del `por_ello` truncado: skip en `_barrer` (F1) + masking del banner (F2) + skip de RE_PAGE_HEADER (F3) — CERRADA H181 (F1 H126 · F2 parcial-documentada H138 · F3 H181)

**Componente:** parser (arquitectura de pasadas).
**Origen:** H123 (revisión a mano del gold: los ruidos recurrentes en los `por_ello` son hifenado + running-heads).
**Motivación:** hoy deshifenado y saltado de headers son per-función (~10 call-sites `_unhyphenate`; `RE_PAGE_HEADER` en ~11 sitios). La EXTRACCIÓN (`_barrer`, zona) ve texto sucio; solo la CLASIFICACIÓN limpia, e inconsistentemente → familia B122/B118.
**Diseño:** pasada `normalizar_bloque` post-localización / pre-extracción que devuelve una vista limpia (running-heads enmascarados a `""` in-place — preserva índices; líneas deshifenadas), preservando marcadores editoriales (`RE_EDITORIAL_ANY`, señal de corte en `detectar_fin_real`). **Doble vista:** limpio → match/extracción; crudo → campos persistidos (case_name, firma_raw, sidecar textos). Subsume B122/B118.
**Caso testigo nuevo (H171):** `329_p4634` — el `por_ello` de producción termina «se deja sin efecto la sen-» con banner «4645 DE JUSTICIA DE LA NACION 329» interpolado mid-dispositivo; verificado contra fuente (`--cola`): el `.md` sigue «-tencia apelada. Notifíquese…». Salió del bucket B139a de H171 (el truncado esconde el objeto, no la ventana W/OBJ); hay más de la misma clase entre los 59 de B139a (330_p4129, 329_p59) — población de prueba adicional para esta mejora.
**Método (decisión H123):** por pasos para atribución (medir +headers y +guión por separado + interacción en +ambos), big-bang en la implementación SI ambos son ganancia. Compuerta contra el gold + dirección de check_regresion. PoC-mide-primero, sin re-golden hasta decidir.
**Clase:** B112 (re-golden masivo). Bump parser MAJOR (v18.26→v19.0) al aplicar.
**Corrección de modelo (H125):** el blueprint original fijaba el fix como "enmascarar a `""` preservando el conteo de líneas". Eso ataca el mecanismo equivocado: preservar el conteo es justamente NO liberar el presupuesto del chunk de `_barrer` (L3092-3095, cuenta líneas no contenido). El lever real, emergido del diagnóstico, es que **`_barrer` saltee las líneas vacías sin contarlas** en el presupuesto de 6 → el chunk pasa de largo el banner y los blancos del OCR y llega al `.` real. `extraer_considerando` (sin presupuesto, filtra vacías) y zona (escaneo de marcadores) ya consumen bien la vista limpia; el único camino con presupuesto-por-líneas es `_barrer`.
**Estado del fix (H126):** **Fase 1 (skip) INTEGRADA** en `parser.py` v19.0. El skip en el chunk de `_barrer` (L3091+) saltea las líneas vacías sin contarlas en el presupuesto de 6 → no mueve `k`/`por_ello_idx` ni la ventana de firma k+1..k+41 (verificado leyendo + unit-test del `_barrer` real). Resultado corpus-completo en disco: 50 flips outcome, competencia 877→910, otro 528→483, 487 `por_ello` extendidos (0 pérdida), votos denormalizado (identidad intacta), resto byte-idéntico, re-golden [CLEAN], manifest v19.0. Diagnósticos en `scripts/diagnostico/H126/` (`inspect_diff_h126.py` column-aware + votos posicional; `diag_porello_h126.py` clasifica extensión/whitespace/pérdida). Infra: `csv.field_size_limit` agregado a `check_regresion` (el sidecar textos tiene campos > 131072 → diff_celdas crasheaba la 1ª vez que textos difiere).

**Fase 2 (masking del banner) — PARCIAL, parser v21.0 (H138).** `RE_RUNNING_HEAD` (terna substring, número obligatorio a un lado, 0 FP sobre 'Corte Suprema de Justicia de la Nación') se enmascara en `_barrer` ANTES de armar el chunk. **Corrido y medido en disco H138:** Gate A = **467 banners restantes (= pre-fix)**, Gate B = 0 flips `real→otro`, `check_regresion` **[CLEAN]** (5 CSV byte-idénticos). **Por qué no movió nada: el masking limpia la vista de matching (`candidate_text`), pero el `por_ello_text` que se PERSISTE al sidecar sale del CRUDO, no del chunk enmascarado** → v21.0 = no-op sobre todo output persistido. **La mitad faltante de Fase 2 = persistir al `por_ello_text` el chunk YA enmascarado** (entonces Gate A baja de 467 y el canónico cambia → re-golden consciente + re-sello, bump MAJOR). El banner INTERPOLADO (línea presente) ya se recupera aguas abajo en el clasificador (v1.05, B127/banner cerrado H138); lo que queda para el parser es el TRUNCADO (verbo nunca persistido). **Decisión H138:** v21.0 QUEDA (código correcto), documentado como parcial — no se revierte por estética de git. Diagnósticos en `scripts/diagnostico/H138/`; validador `validar_m21_fase2.py`.
**(histórico) Fase 2 original — gated.** Suma ~+4 competencia (los que faltan para 37) + limpia el banner que hoy queda **embebido como ruido** en el `por_ello` extendido (testigo: `…550 FALLOS DE LA CORTE SUPREMA 329 de Quilmes…`). Preguntas abiertas a resolver ANTES de integrar (verificando, no presuponiendo): (1) bug de detección de terna en layouts orden tomo/página/frase (343_p86 deja "96 FALLOS…"; 340_p1428 deja "1430"); (2) fuente de los offsets al parsear — verificar si `headers_archivo` ya provee los `linea_header` o hay que cablear `mapa_paginas`; (3) threading crudo-vs-limpio por campo (extracción sobre limpio; persistidos case_name/firma_raw/sidecar sobre crudo, lección B114). Base: `normalizar_bloque.py` (detección por `mapa_paginas`, no regex). Importar `RE_EDITORIAL_ANY` del parser (deduplicar). Bump MINOR al integrar.
**Referencias cruzadas:** B118, B122, B114 (el global sobre la copia de match NO es lo que B114 rechazó, que era PERSISTIR texto deshifenado). H123.
**Nota H174 (población para Fase 3):** el cierre de B141 dejó adjudicada la sub-clase PRESUPUESTO, hermana del banner-partido: 333_p1951 y 343_p2080 (banner en 3 líneas físicas — «1959 / DE JUSTICIA DE LA NACION / 333» — cuenta como contenido y drena el chunk; `RE_RUNNING_HEAD` cubre la terna en UNA línea, no el split), 334_p1237 (ídem; el fix B141 le recupera el verbo del punto II pero arrastra «1239 DE JUSTICIA DE LA NACION 334» como cola cosmética que norm() enmascara downstream), 330_p563 (dispositivo largo de 6 líneas justas, pierde el punto II sin banner de por medio) y la medida 3 de 344_p274. Lever candidato: skipear `RE_PAGE_HEADER` (línea-sola, parser L204) dentro del chunk SIN contar presupuesto — mismo patrón que el skip de vacías de Fase 1; cardinalidad corpus-wide no medida, exige PoC en disco. Se suman a 329_p4634/330_p4129/329_p59 (H171).

**Cierre H181 — FASE 3 IMPLEMENTADA y validada en disco (parser v24.1→25.0, MAJOR):** skip de `RE_PAGE_HEADER` (línea-sola) dentro del chunk de `_barrer` sin contar presupuesto — el lever exacto de la Nota H174, simétrico al skip de vacías de F1; el banner partido en N líneas físicas dejaba de drenar hasta 3 unidades del presupuesto de 6. Detector reusado, 0 regex nueva; el componente no entra al chunk (higiene del pe persistido). Medición = ciclo `--consciente` corpus-wide adjudicado por lectura (`dump_diff_h181c`, 52 casos con flip de decisión): pe 547 cambiados · outcome 23 (1 FP nuevo del eje legacy → **B144**) · **is_merit +18 TP** (4/4 truncados del paso 3 + 14 extras nítidos) · orig +1 (343_p726) · quejas ~15 · totalidad estructural considerando/firma = SOLO 332_p663 (**testigo B126 sanado**, panel 4→6, +2 votos). FUERA DE ALCANCE declarado y verificado quieto: 330_p563 (dispositivo >6 líneas sin banner — si se ataca alguna vez, es presupuesto, otra clase). FP evitado pre-golden: Pereyra 348_p1352 (→ constancia v1.18 en B143). Sello: orig 596 · merit 2965 · div 0 · [CLEAN] 64. El residual de la fila F2-original (threading crudo-vs-limpio) queda histórico: el skip de F3 remueve la línea-sola entera, la mayor fuente del ruido.

### B123 — `outcome=otro` residual (~483 post-skip): cola sin clasificar que merece escrutinio

**Componente:** parser (clasificación de dispositivo / cobertura de `classify_outcome`).
**Origen / fuente del diagnóstico:** H126 (post-integración del skip: `otro` bajó 528→483, pero el residual sigue alto y heterogéneo).
**Causa raíz:** NO es M21 — el skip ya recuperó lo truncado por banner. Los ~483 restantes caen a `otro` por otras causas a relevar: dispositivos sin verbo en el vocabulario actual de `classify_outcome`, fórmulas alternativas no cubiertas, `por_ello` ausente/mal localizado, casos sin dispositivo real (aclaratorias, providencias), etc. Candidata de categoría: `aclaratoria` (surge en 329_p551, flagueada en H125).
**Diagnóstico / evidencia:** `confirmado_cuantificado` (H127, triage sobre v19.0 + lectura de 77 `.md` estratificados, seed=127). **Reframe: los 483 son DOS frentes, no uno.**
  - **186 (38%) — mislocalización del `por_ello` (→ B124, NO taxonomía).** El `por_ello` capturado no tiene señal de dispositivo (ni "se resuelve:" ni fórmula de cierre Notifíquese/devuélvase/archívese); el parser ancló en un "Por ello, [razonamiento]" no-final del considerando/dictamen. Testigos leídos: 332_p2425 (Sosa, dispositivo real = `revoca` MERIT perdido), 337_p388 (`confirma`), 329_p2631 (`desestima`) — el verbo YA está en vocab, el clasificador no lo vio. Doble daño: `extraer_considerando` también corta en ese `por_ello_idx` (L1298) → **considerando truncado** (alimenta materia/causa_inadmisibilidad).
  - **297 (61%) — dispositivo capturado, verbo no en vocab (frente taxonómico real).** Composición (estrato primario por keyword del `por_ello`, contaminada por la mislocalización): deferencia_dictamen 87 (→ `derivar_dictamen`, no `otro`), remite_reenvia 66 (pisa M22+competencia), procesal_menor 42 (mayoría mero trámite → residual), suspension 28, aclaratoria 6, recusacion 6, honorarios 6, reposicion 3, caducidad 1, sin_keyword 238.
  - **Categorías candidatas VERIFICADAS contra `.md`:** `aclaratoria` real ("Aclarar la sentencia en el sentido indicado", verbo no en vocab) — **reabre la decisión de scope de BITACORA L285** (ignorar por frecuencia), reversión consciente; `regulacion_honorarios` real ("se regulan los honorarios de…"); `suspension` real ("Suspender el trámite/los términos"). `caducidad` YA existe en vocab (L397) → es mislocalización, no categoría. **`recusacion` MUERTA por B095** (incidente de excusación → residual, no disposición del recurso); leído confirma (jueces excusándose). Todas, de promoverse, van en zona fallback (patrón H079, solo rescatan de `otro`).
**Validador propuesto:** B124 primero (la mislocalización se arregla con localización, no con vocab nuevo, y recupera mérito + considerando). Luego, sobre el residual confiable, promover las categorías verificadas (re-golden consciente por label). Pendiente: leer deferencia/remite/procesal/sin_keyword del lado 297; cruce con gold = validación, no tuneo.
**Estado del fix:** B124 diseñado (no implementado); taxonomía 297 parcialmente caracterizada.
**Referencias cruzadas:** **B124** (mislocalización, prioritario), B117 (zona epílogo/considerando), M21 (truncado-por-banner), B120 (merit-recall), B095 (recusación residual), M22 (remite/reenvía), **B127** (capa-deriver: dispositivo bifásico, sub-patrón del frente taxonómico). H126, H127. Sin ID histórico.

**Nota H132 (capa-deriver):** el frente taxonómico de la disposición se materializó en la capa-deriver (`clasificador_disposicion.py`, importado por `derivar_recursos.py`) como el bucket **`no_fondo`** (ex `sin_disposicion_legible`), **1860 casos = 31,6% del corpus**. NO es un bug de extracción: el `por_ello` se lee perfecto, lo que falta es vocabulario para las disposiciones que no son de fondo. **El gold lo respalda** (88/89 vacío) y se diseñó binario, así que NO requiere desagregar en sub-etiquetas (competencia/liquidación/etc.) — solo se renombró el cajón a un nombre honesto. El sub-patrón "verbo de fondo PRESENTE pero precedido por la cláusula de admisibilidad" se separó como **B127** (sí accionable, toca `parte_ganadora`).

### B124 — `por_ello` mislocalizado: `_barrer` ancla el PRIMER "Por ello", no el del dispositivo — CERRADO H130

**Componente:** parser (`resolver_dispositivo` / `_barrer`, L3071-3181; `detectar_apertura_dispositivo`, L103-129).
**Origen / fuente del diagnóstico:** H127 (escrutinio B123: ~186/483 `otro` con `por_ello` = razonamiento, no dispositivo).
**Causa raíz (verificada en código + `.md`):** `_barrer` (L3083-3118) devuelve el **PRIMER** candidato con firma de juez en k+1..k+41 (o el primero sin firma como fallback B059, L3116). El único filtro por línea es el **blacklist angosto** `POR_ELLO_ARGUMENTAL` (L68-71, ~15 verbos): un "Por ello, si bien…/cabe…/es que…" del considerando de la Corte (no excluido como dictamen) pasa el guard, y si está ANTES del dispositivo real con firma a ≤40 líneas, gana. La cascada Tier 1→4 no prefiere el último. Segundo mecanismo: si la frontera del dictamen (`RE_FECHA_LINEA`/"Buenos Aires", L62) se dibuja mal, los "Por ello" del dictamen dejan de excluirse.
**Diagnóstico / evidencia:** `confirmado_caso_testigo` (332_p2425/337_p388/329_p2631: sidecar `por_ello` = razonamiento; dispositivo real = revoca/confirma/desestima en el `.md`). `confirmado_cuantificado` para la cota: 186/483 `otro` sin señal de dispositivo (proxy, cota superior). MEDIDO corpus-wide H128 (ver Fix validado abajo).
**Fix hipótesis descartada (H127, "último-con-firma"):** que `_barrer` devuelva el ÚLTIMO candidato con firma. **REFUTADA en disco H128:** mete el accesorio posterior (acordada 47/91, art. 94 CPCC, "no se hace lugar a fs. 58/59") → rompe 86 (A1) / 93 (A2) casos en corpus y 14 en gold. La posición pura no distingue dispositivo de accesorio.
**Fix VALIDADO (H128, regla P):** `_barrer` debe devolver el **PRIMER candidato performativo con firma**, con fallback al actual (primer-con-firma) si no hay performativo. Performativo = `RE_PERF.search(chunk)` con `RE_PERF = \bse\s+(resuelve|decide|declara|revoca|confirma|hace lugar|deja sin efecto|rechaza|desestima|tiene por|admite|anula|hace saber|intima)\b`. Razón: el dispositivo de fondo SIEMPRE abre con marca performativa ("se resuelve/declara/revoca…"); el argumental que se cuela antes es no-performativo ("En consecuencia, no discutida…", "Por ello, si bien…", "Por lo expuesto, habida cuenta…") y se saltea; los accesorios posteriores son no-performativos o performativos-posteriores (y P toma el PRIMER performativo, no el último). Distingue por forma estructural, no por posición ni por enumerar verbos semánticos (no se pierde los verbos nuevos de B123, que viven en el frente taxonómico aparte).
**Evidencia (corrida en disco local, scripts `variantes_dispositivo.py` + `cruce_gold_variantes.py` + `autopsia_candidatos.py`):** sobre las 6 reglas medidas (actual, A1, A2, B=último-c/verbo, C=primer-c/verbo, P). **Corpus 5890:** rotos P=31 (mínimo; A1=86, A2=93, B=69, C=39), recuperados reales P=119 (sin pérdida a `sin_dispositivo`; B/C inflan +295 a vacío), neto P=+88 (mejor; A1=+40, A2=+33). **Gold M20 n300:** cambios en fuente-OK (probable regresión) P=7 — **los 7 son mejoras** (argumental→dispositivo: 332_p2625, 334_p941, 334_p1081, 344_p2393, 345_p583, 346_p44, 348_p405); A1/A2=14 (incluyen los 5 accesorios 331_p2913/332_p979/332_p1280/339_p1530/340_p1554 que P NO mete), B=25, C=23. Autopsia de 11 casos clave: hipótesis confirmada 11/11 (el dispositivo de fondo es el primer `perf=si` c/firma; argumentales `perf=.`; accesorios posteriores). Gates: G1 99,4%, G2 réplica cascada 0 fails, firma confiable.
**Validador propuesto:** `autopsia_rotos_P.py` (entregado H128) — autodetecta los 31 rotos de P en corpus e imprime el paisaje de candidatos (idx|zona|firma|perf|outcome|texto) + picks actual/P, para clasificar cada cambio como corrección (el actual capturaba mal, p.ej. `inadmisible_280` espurio del considerando) o regresión (hueco de `RE_PERF`). El gold solapa solo ~5% con los rotos del corpus → NO los cubre; van por lectura. Patrón esperado: correcciones `inadmisible_280`→merit (338_p1032, 340_p1380, 341_p242, 342_p259); revisar 330_p1759 (único P→`sin_dispositivo`).
**Estado del fix:** **CERRADO H130 (parser v20.0, `RE_PERF v2`).** Fix aplicado: `_barrer` devuelve el PRIMER candidato performativo-con-firma; si ninguno lo es, cae al primer-con-firma (= comportamiento v19, sin regresión). `RE_PERF v2` = `se <verbo>` (clítico opc., v1) | `(el Tribunal|esta Corte|la Corte) resuelve` | `resuelve:`. El universo "resuelve sin se" se auditó en disco ANTES de diseñar la regex (`audit_resuelve_sin_se.py`, 5890): únicas formas sin-`se` entre candidatos-con-firma = "el Tribunal resuelve" (300) + "resuelve:" (23, = Tribunal hifenado por OCR / interpuestos / "esta Corte Suprema" / "la mayoría del Tribunal"); `OTRO_RESUELVE`/`ESTA_CORTE`/`LA_CORTE`/`RESUELVE_UP` = 0 → sin over-match de instancia inferior. **Validación en disco:** outcome **+121 recup** (otro→real) / 29 real→real (dom. `inadmisible_280`→merit) / **0 regresiones a otro**; **`scan_concurrencia` (check NUEVO de pick-de-concurrencia, generaliza `scan_disidencia` con `RE_VOTO_HEAD v2` que agarra "Voto la señora/el señor ministro") = 0 sospechosos** (331_p1028 cerrado, ninguno nuevo); `es_queja` +8 recup / 2 correcciones de FP / 1 FN conocido (340_p114); votos net +1 (342_p1170 1→5 panel, 348_p1435 dedup; **332_p663 −2 = exposición de B126, frente aparte**). Re-golden [CLEAN] 5/5 + manifest re-sellado [CLEAN] 61 artefactos, parser v20.0. Scripts H130: `audit_resuelve_sin_se.py`, `scan_concurrencia.py`, `outcome_delta_P.py` (`scripts/diagnostico/H130/`).

**Antecedente H129 (regla P v1, implementada y revertida):** **IMPLEMENTADO en H129 (v20.0, `RE_PERF` con clítico opcional) y ROLLBACK a v19.0 — REABIERTO por mis-pick.** Validación en disco H129 (scripts `cruce_gold_variantes_clitico.py`, `impacto_P_clitico.py`, `autopsia_rotos_P_clitico.py`, `scan_disidencia_recup.py`): outcome **+147 corrige / 0 rompe** (119 otro→real + 28 real→real), gold n300 **7 mejoras / 0 regresiones**, `es_queja` **+6 neto** (7 quejas reales recuperadas; el clítico fixeó 346_p931). **PERO** `check_regresion` destapó **−7 filas en `csjn_casos_votos`** (4 casos); auditados sobre `.md` con `extraer_caso`: **331_p1028 = mis-pick** — la mayoría cierra "Por ello, **el Tribunal resuelve**: I)…" (sin `se` → `RE_PERF` NO matchea) seguida de Argibay según-su-voto "Por ello, **se confirma**…" → P ancla en la concurrencia (outcome=confirma de Argibay, firma solo Argibay, 9→1). **Causa: `RE_PERF` solo cubre `se <verbo>`; los performativos de mayoría sin `se` ("el Tribunal resuelve", "resuelve:", "RESUELVE:") quedan fuera → P prefiere el según-su-voto performativo sobre la mayoría.** **Blind spot de la validación H128/H129:** el scan de disidencia buscaba *votos perdedores*, no *concurrencias* (Argibay concurre, mismo resultado) → el A/B contó el `otro→confirma` como corrección. (342_p1170 1→5 = mejora; 348_p1435 dedup; **332_p663 6→4 = B126, no mis-pick.**) **Fix pendiente: `RE_PERF v2`** que matchee performativos de mayoría sin `se` — **auditar el universo "resuelve sin se" en el corpus (frecuencia + formas) ANTES de tocar la regex**, después re-implementar + re-validar con **check NUEVO de pick-de-concurrencia** (no solo disidencia) + re-correr A/B completo + votos-delta + `check_regresion` column-aware + re-golden + bump MAJOR + re-sello manifest. Scripts diagnóstico H129: `votos_delta_P.py`, `esqueja_flips_P.py` (`scripts/diagnostico/H129/`).
**Referencias cruzadas:** B123 (lo descubre), B117 (zona epílogo absorbe considerando), B120 (merit-recall), B125 (t345 sidecar, hallazgo colateral), M21 Fase 2 (frontera banner/dictamen). H127, H128. Sin ID histórico.

### B125 — t345: `por_ello_text` vacío en CSV donde la reconstrucción SÍ extrae dispositivo

**Componente:** sidecar `csjn_casos_textos.csv` (poblado de `por_ello_text`) — o `linea_inicio`/`linea_fin_real` de `csjn_casos.csv` para t345 (causa no determinada).
**Origen / fuente del diagnóstico:** H128 (gate G1 de `variantes_dispositivo.py`: 37 mismatch reconstrucción-vs-CSV, de los cuales **15 son de t345** con CSV vacío y reconstrucción no-vacía).
**Diagnóstico / evidencia:** `confirmado_cuantificado` — 15 casos de t345 (345_p157, p187, p204, p244, p251, p338, p384, p386, p400, p605, p716, p849, p1170, p1233, p1309) donde `por_ello_text` en el CSV está VACÍO pero la reconstrucción del diagnóstico (mismas funciones del parser, mismas líneas del `.md`) extrae un dispositivo real ("Por ello, se suspende el trámite…", "Por ello, se hace lugar a la queja…", etc.). `hipotesis_no_verificada` para la causa: no determinado si es (a) poblado del sidecar que perdió esos casos, (b) `li`/`lfr` del CSV mal apuntados para t345, o (c) el bloque real en producción difiere. NO afirmar causa sin diagnóstico.
**Estado de verificación:** `confirmado_cuantificado` (la discrepancia), `hipotesis_no_verificada` (la causa).
**Validador propuesto:** comparar para los 15 el `li`/`lfr` del CSV vs el rango real en el `.md`; correr el parser aislado sobre esos bloques y ver si `por_ello_text` sale vacío en producción. Si el parser los extrae pero el CSV no los tiene → bug de escritura del sidecar.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** B124 (mismo frente dispositivo, lo destapa el gate), H113 (creación del sidecar `csjn_casos_textos`), H128. Sin ID histórico.

### B126 — Extractor de firma: nombres partidos por salto de línea se dropean según la posición del `por_ello`

**Componente:** parser (`collect_firma_lines`, L3479; `parse_firma`; loop de votos L3618).
**Origen / fuente del diagnóstico:** H129 (auditoría del −7 de filas en `csjn_casos_votos` al implementar B124/regla P; `votos_delta_P.py`).
**Causa raíz (verificada en código + `.md`):** `firma_raw = collect_firma_lines(bloque, por_ello_idx + 1)` (L3479) colecta la firma desde la línea siguiente al dispositivo; el conteo de votos = una fila por juez en `firma_parsed["jueces"]` (loop L3618). `parse_firma` no stitchea los nombres cuyas dos mitades caen en líneas distintas del OCR. Como la firma se colecta relativa al `por_ello_idx`, mover el dispositivo (regla P) cambia el arranque del `collect_firma_lines` → cambia la lista de firmantes. Caso testigo **332_p663** (Salas/Salta, ORIGINARIA no-fondo): firma real de 6 — "Lorenzetti — Highton — Carlos\nS. Fayt — Petracchi — Maqueda — E.\nRaúl Zaffaroni"; con el `por_ello` en "se resuelve:" + cuerpo multipunto I-IV entre el opener y la firma, el parse dropea **Fayt y Zaffaroni** (exactamente los dos partidos por salto de línea) y devuelve 4. El golden (con `por_ello` anterior) los stitcheaba → el conteo depende de la posición de arranque.
**Diagnóstico / evidencia:** `confirmado_caso_testigo` (332_p663: 6→4, los 2 dropeados = nombres cortados por línea). Acoplamiento dispositivo→firma confirmado en código (L3479 + loop L3618).
**Estado de verificación:** `confirmado_caso_testigo`.
**Validador propuesto:** escanear el corpus por firmas con nombre partido (mitad-inicial al fin de línea + mitad-final al inicio de la siguiente) y comparar `n_jueces`/`jueces` parseados vs los nombres reales; cuantificar casos que pierden firmantes. Reusar `_unhyphenate` / la lógica de join inter-línea del parser.
**Estado del fix:** no diseñado — **PRÓXIMO FRENTE (post-H130).** **Independiente de B124** (toca cualquier firma con nombre cortado por línea, no solo bajo regla P); la regla P apenas lo EXPONE al mover el arranque del `collect_firma_lines`. **Confirmado en disco H130:** con B124 integrado (parser v20.0), `votos_delta` mide 332_p663 **6→4** — dropea **Fayt y Zaffaroni**, los 2 nombres partidos por el wrap del OCR; es el ÚNICO negativo de votos del fix B124 (el resto son mejoras: 342_p1170 +4 recupera panel, 348_p1435 dedup). Testigo Salas/BOSQUES verificado sobre el `.md` crudo: firma de la mayoría "Lorenzetti — Highton — Carlos\nS. Fayt — Petracchi — Maqueda — E.\nRaúl Zaffaroni" (6 reales). **Decisión H130:** se cerró B124 con el golden v20.0 cargando este −2 como instancia B126 conocida (firma 332_p663 = 4, real = 6), documentada acá; NO se re-stitcheó. El fix necesita el escaneo corpus-wide de firmas partidas ANTES de tocar el stitcher (riesgo de over-stitching: pegar dos jueces distintos o un nombre con su anotación inline "(en disidencia)"/"(según su voto)").
**Referencias cruzadas:** B124 (lo destapa al implementar P), L3479/L3618 (parser). H129. Sin ID histórico.

### B127 — Dispositivo bifásico (admisibilidad + fondo) — CERRADO H139 (premisa refutada: `search` es global)

**Componente:** capa-deriver (`clasificador_disposicion.py`, NO el parser).
**Origen / fuente del diagnóstico:** H132 (diagnóstico del bucket `no_fondo`: de 1860, 31 con verbo de fondo en el `por_ello` que el clasificador no captura).
**Causa raíz:** el dispositivo de la CSJN es BIFÁSICO — primero ADMISIBILIDAD del recurso ("se declara procedente/admisible el recurso extraordinario", "se hace lugar a la queja") y DESPUÉS el FONDO ("y se deja sin efecto / se revoca / se declara la nulidad"). `disposicion()` matchea el PRIMER verbo dispositivo; el primero es la admisibilidad (no está en el vocab de fondo ni de no-revisión) → cae a `no_fondo` sin seguir hasta el verbo de fondo tras la conjunción "y".
**Diagnóstico / evidencia:** de los 31 con verbo de fondo en el bucket `no_fondo`: **26 con `es_revision_fondo=si`** (FN reales de fondo — revocaciones/nulidades = victorias del recurrente perdidas) y **5 con `es_revision_fondo=no`** (FP de la regex de detección: el "deja sin efecto/nulidad" es de algo accesorio — cautelar/actuaciones procesales/concesión de recursos; el parser los marcó no-fondo bien: 330_p4045, 331_p1583, 334_p1272, 346_p439, 346_p960). **14 de los 26 son quejas** (fórmula "se declara procedente la queja, se hace lugar al REX y se deja sin efecto" — admisibilidad de la queja + fondo en el mismo dispositivo). **Confirmación gold:** de los 89 del bucket en el n300, solo **1** está codificado como fondo (330_p1907 = `deja_sin_efecto`); los otros 25 candidatos NO caen en el n300 → no validados contra ground truth.
**Estado de verificación:** `confirmado_caso_testigo` (330_p1907, gold) + `hipotesis_cuantificada` (26 corpus, por estructura, no validados).
**Impacto:** COBERTURA del corpus (~26 victorias de fondo subcontadas → sesga `parte_ganadora` en producción), NO la métrica validada (el gold sub-representa la fórmula bifásica; cuesta 1 caso en el n300, ~+0,7 pts). M20 sigue defendible sobre el gold.
**Validador propuesto:** enseñar a `disposicion()` a SALTAR la cláusula de admisibilidad ("se declara procedente/admisible el recurso", "se hace lugar a la queja") y leer el verbo de FONDO que sigue. Cambio de LÓGICA (no una regex más), sobre el clasificador congelado → re-validar contra el gold como held-out. Los 5 FP de la regex de detección NO se tocan (el parser ya los marca no-fondo).
**Estado del fix:** **PARCIAL.** El sub-frente **banner interpolado** (el `por_ello` trae embebido un running-head `…FALLOS DE LA CORTE SUPREMA…` que tapa el verbo de fondo) se **CERRÓ H138**: `clasificador_disposicion.py` v1.03→**v1.05** enmascara `RE_RUNNING_HEAD` en `norm()` antes de clasificar → `por_ello_cortado` 18→0, 4 interpolados recuperan fondo (330_p380/330_p960/333_p1951/344_p1444), fondo leída 2886→2892, 0 regresiones. El sub-frente **bifásico (admisibilidad + fondo)** se **CERRÓ H139 — PREMISA REFUTADA en disco.** Leído `disposicion()`: hace `pat.search(pe)` **GLOBAL** sobre todo el `por_ello` (NO "matchea el primer verbo dispositivo"); la cláusula de admisibilidad no está en el vocab DISP → no matchea ni bloquea, y el verbo de fondo tras la "y" se captura igual. Medido en disco: de **1935** `por_ello` con forma bifásica, **1917 se capturan como fondo**; los **13** que caen a `no_fondo` se leyeron uno por uno y **NINGUNO** cae por el bifásico — causas reales: truncado/banner (329_p4634/347_p474/348_p355), OCR/typo (331_p2628), OBJ fuera de vocab (laudo, "lo resuelto", "declaración de inconstitucionalidad", contracautela, "recurso de casación", "todo lo actuado") y plural `-es` en nulidad (340_p1193). **No hay lógica de salto que diseñar.** El recuperable real (≈ +0,1pp sobre `parte_ganadora`) pertenece a **OBJ-vocab + M21**, NO a B127. (vía/quejas, capa-deriver hermana). H132, **H139**. Sin ID histórico.

### B128 — `extraer_caso.py` stale post-H113: lee `considerando_text`/`por_ello_text` de `csjn_casos.csv`, que ya no los tiene — CERRADO H135

**Componente:** diagnóstico (`scripts/diagnostico/extraer_caso.py` v2.1, herramienta canónica no ligada a sesión).
**Origen / fuente del diagnóstico:** H134 (al intentar usarla para auditar arbitrariedad por remisión al dictamen).
**Causa raíz:** H113 separó el texto pesado a un sidecar — `considerando_text` y `por_ello_text` viven ahora en `output/parser/csjn_casos_textos.csv` (cols 2-3) y ya NO están en `csjn_casos.csv`. Pero `extraer_caso.py` sigue leyendo del canónico (`CSV_CANONICO = .../csjn_casos.csv`, línea 60) y hace `fila.get("considerando_text","")` / `por_ello_text` (líneas 121-122) → ambos devuelven `""`.
**Diagnóstico / evidencia (verificado en disco H134):** `head -1 csjn_casos.csv` NO contiene `considerando_text`/`por_ello_text`; el sidecar SÍ. En el script: `ancla` (121) y `pe` (122) quedan vacíos; el char-count y el flag `TRUNCADO` (213/230) reportan 0/completo erróneo. Modos que dependen del ancla → **muertos**: `--md` override, fallback por glob, `--blind`, y el sanity-check ancla↔bloque. **La extracción canónica por rango de líneas sobre el `.md` (líneas 158+, vía `source_file` + rango) SÍ funciona** — no depende de esas columnas.
**Estado de verificación:** `confirmado_cuantificado` (columnas inspeccionadas en disco; rutas/líneas del script confirmadas).
**Validador propuesto:** leer `considerando_text`/`por_ello_text` del sidecar `csjn_casos_textos.csv` (join por `caso_id_canonico`) en vez del canónico; o re-derivar el ancla del `.md` directamente. Fix mínimo: cargar el sidecar y mergear las dos columnas a `fila`.
**Estado del fix:** **aplicado y validado (H135), commit `0333379`.** `extraer_caso.py` v2.1→**v2.3**. (1) **B128:** tras cargar la fila del canónico, mergea `considerando_text`/`por_ello_text` desde el sidecar `csjn_casos_textos.csv` por `caso_id_canonico` (mismo join que `derivar_recursos.py`), solo si faltan; degrada con WARN si el sidecar no está. Revive `--md`/`--blind`/glob/sanity-check. Nuevo flag `--csv-textos`. El flag `TRUNCADO@2000` muerto post-H113 se reemplazó por largo+fuente honestos. (2) **Display:** el `norm()` mezclaba dos transformaciones (des-hifenado + colapso de espacios); ahora **default = CRUDO** (el `.md` tal cual) + perillas ortogonales `--norm` (atajo), `--deshifen`, `--colapso`. Decisión de diseño: la herramienta de diagnóstico NO reusa la normalización del parser a propósito — replicarla heredaría sus errores y cegaría el contraste fuente↔CSV (por eso tampoco se sube `parser.py` para copiarla). Sanity-check sigue sobre el normalizado total (sin WARN falso). **Validación en disco:** 332_p663 (POR_ELLO poblado; char-count del sidecar 12453; firmas partidas Fayt/Zaffaroni de B126 visibles en crudo); 329_p142 (POR_ELLO poblado, char-count 162; running-head embebido en el dispositivo visible). NO toca pipeline ni golden.
**Referencias cruzadas:** H113 (split del sidecar, causa), B102 (otro bug de la misma herramienta, CERRADO H094), B125 (t345 con sidecar vacío: el BLOQUE del `.md` lo muestra igual), B126 (firmas partidas, visibles con el default crudo). H134, **H135**. Sin ID histórico.

### B130 — Gold de `reenvía`: clase negativa ruidosa (codificación) → κ no reportable

**Componente:** gold de validación M20 (no el pipeline).
**Origen / fuente del diagnóstico:** H139 (κ parser↔gold: reenvía κ 0,408 [0,16–0,635], n=75).
**Causa raíz:** al codificar `reenvía`, el gold marcó los `si` con confianza pero dejó los ambiguos en blanco y en algunos puso `no` sin certeza (la válvula `'-'` para no-codificable NO se usó acá, sí en disposición/parte/vía). Resultado: 69 `si` / 6 `no` → clase negativa chica Y contaminada.
**Diagnóstico / evidencia:** κ 0,408 (acuerdo crudo 0,827) — bajo por desbalance + ruido; IC bootstrap [0,16–0,635] va de "pobre" a "sustancial" → con n=75 no se puede ni ubicar la categoría. El κ bajo es mitad base-rate, mitad ruido de codificación (informado por el usuario H139).
**Estado de verificación:** `confirmado_cuantificado` (κ + IC en disco, H139).
**Validador propuesto:** recodificar negativos explícitos de `reenvía` (revisar casos sin reenvío de fondo y marcar `no` con criterio; dejar `'-'` los no-codificables), subir n, recomputar κ con `kappa_confiabilidad.py`.
**Actualización H149 (en disco):** confirmado que el 0,408 es artefacto de DISEÑO, no de confiabilidad — muestra sparse (n=74 ambos codeados), sesgo de selección (`si` en remands explícitos, blanco en la duda, solo 6 `no`) + base-rate degenerada. **SALE de la tabla de confiabilidad** (no se reporta). Regla doctrinal anclada: `deja_sin_efecto ⟹ remand` near-determinística (gold **45/46 = 97,8%**); única excepción `330_p4592` (Larrabeiti) CORRECTA = deja sin efecto + resolución directa del fondo (prescripción, art. 16 2º párr. ley 48). Producción sub-detecta (deja 68,6% si) → ~425 candidatos a falso negativo. Lado revoca SIN establecer (gold sesgado 21 si/2 no por selección; producción 33,6% si es piso por sub-detección).
**Estado del fix:** no diseñado. **Path nuevo (H149):** derivar reenvía-deja desde `disposicion` con guard de resolución-directa (no flipear ciego los ~425; los Larrabeiti-type son legítimos). Lado revoca sin tocar. `reenvía` NO reportable.
**Referencias cruzadas:** M22 (reenvía desde dispositivo), M19 (κ/doble-codificación), `kappa_confiabilidad.py` (H139). H139, H149. Sin ID histórico.

### M22 — `reenvía` desde el dispositivo (validable contra el gold)

**Componente:** parser / capa de disposición (campo `reenvía`).
**Origen / fuente del diagnóstico:** H126 (observación al cierre: el skip recupera la cláusula de reenvío que antes el banner truncaba).
**Motivación:** la fórmula de reenvío («vuelvan los autos al tribunal de origen para que se dicte nuevo fallo/pronunciamiento») es de baja dificultad de detección desde el dispositivo, y ahora cae DENTRO del `por_ello_text` extendido (antes quedaba pasada el banner — testigo `329_p142`, recuperado en H126: «…agravios. Vuelvan los autos al tribunal de origen a fin de que, por»). Se espera ganancia de recall del detector de `reenvía` post-skip (baseline blind 0,773).
**Validador propuesto:** detector ancla sobre `por_ello_text`; medir recall vs la columna `reenvía` del gold (held-out = validación legítima, NO tuneo). Re-medir el 0,773 blind post-H126.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** M21/H126 (habilitador), capa disposición/`derivar_recursos`. Sin ID histórico.

### M23 — Vía recursiva: ¿feature de dispositivo o fin analítico? + per saltum diferido

**Componente:** capa-deriver (`clasificador_via.py` v0.1 / `derivar_recursos.py` v0.2).
**Origen / fuente del diagnóstico:** H132 (detector de vía fuente-única validado 0,956 vs gold n=136; reflexión de cierre sobre el VALOR de la vía-tipo).
**Replanteo (H132, decisión del usuario):** el TIPO de recurso (ordinario/extraordinario/per saltum) NO es un fin analítico en sí. El anuario estadístico de la CSJN compara **concedidos vs quejas**, eje que ya vive en `es_queja` (y sostiene H1, certiorari criollo). La separación por tipo se concibió como **heurística para clasificar el dispositivo**: originaria, competencia, ordinario y extraordinario tienen cada uno un patrón de dispositivo característico, así que conocer el tipo ayuda a predecir/clasificar la disposición (p. ej. "se desestima el recurso" puede indicar que era extraordinario). **Reevaluar si la vía-tipo merece ser CAMPO de salida o es solo un feature interno** del clasificador de dispositivo.
**Per saltum (art. 257 bis CPCCN) — diseñado y validado, NO aplicado:** se prototipó en v0.2 (regex 'per saltum' / 'salto de instancia' / '257 bis', **16 detectados**, vía 0,956 intacta, 0 casos ext/ord del gold reclasificados) y se **revirtió a v0.1** por decisión H132: la "primacía" sobre extraordinario es innecesaria para algo <1% del corpus, y un per saltum ES un extraordinario por salto de instancia (dejarlo caer en `recurso_extraordinario` no rompe nada). Re-aplicar solo si la vía-tipo prueba valor. Casos a revisar si se retoma: 339_p1254 (posible mención no-vía), 340_p1383 (per saltum local/provincial).
**Pendientes (anotados, no diseñados):**
  - **253 quejas sin vía** (de 2297): la queja es recurso de hecho por REX denegado (art. 285 CPCCN); imputar `extraordinario` rescataría la mayoría, pero **incierto si se puede capturar** de forma confiable (la minoría son quejas por ordinario denegado). Conecta con concedido-vs-queja (el eje del anuario).
  - **Originarios sin vía:** en competencia originaria (art. 117 CN) NO hay vía recursiva → `via_recurso=""` es CORRECTO. Usar `is_originaria` como eje para excluirlos. Conecta con la deuda de recalibrar `is_originaria`.
**Estado del fix:** per saltum revertido (diseñado, no aplicado); imputación quejas + exclusión originarios + decisión vía-como-campo NO diseñados.
**Referencias cruzadas:** `clasificador_via.py`, is_originaria/B010, B127 (capa-deriver hermana), H1 (certiorari criollo queja/concedido). H132. Sin ID histórico.

### M24 — `check_regresion` general: runner que englobe el harness del parser + el resto de checks deterministas

**Componente:** infra de tests (`scripts/tests/`).
**Origen / fuente del diagnóstico:** H138 (al sellar la capa-deriver, el usuario pide "un check regression general que englobe check regresion y al resto").
**Diseño propuesto (NO implementado):** runner de nivel superior que invoque y agregue los checks ya existentes, reportando un único pass/fail. Distingue regímenes por NATURALEZA del output, NO los mezcla:
  - **Byte-regression (refactor = misma salida):** `check_regresion.py` (parser, 5 CSV) **+ `csjn_editorial_indice_partes.csv`** (output determinista de `parser_editorial`, hoy NO cubierto por el harness — único gap real de byte-regression; ver abajo).
  - **Provenance/integridad:** `generar_manifiesto.py --verify` (63 artefactos).
  - **Correctitud de clasificadores (cambian POR DISEÑO):** accuracy-gold n300 (disposición/materia/etc.). **`materia` y `recursos` NO van a byte-regression** — recursos cambió en H138 con clasificador v1.05; un byte-golden les fallaría en cada tune. Su régimen correcto es accuracy-gold + manifest.
  - **Unit tests existentes (sintéticos, fixtures):** `test_construir_catalogo.py`, `test_cruzar_catalogo_y_mapa.py`, `test_detectar_paginas.py`, `test_clasificador.py`.
**Gaps a verificar EN DISCO antes de escribir el runner (no asumir):** (1) DÓNDE vive cada test (los `test_*` hacen `sys.path.insert(0, parent)` → deben estar pegados a su módulo); (2) `test_clasificador.py` importa `from csjnv11 import …` (`clasificar_tipo_voto`/`tipo_voto_sep`) — **huele a versión vieja monolítica**, verificar si está VIVO o es legacy (si es legacy NO va al runner); (3) baseline: ¿están TODOS en verde hoy? El runner no puede envolver tests rotos/stale.
**Sub-gap `indice_partes` en `check_regresion`:** el harness corre `parser.py` a un temp y compara 5 CSV; `parser_editorial` corre en la misma llamada (cwd=PIPELINE) pero `csjn_editorial_indice_partes.csv` NO está en `OUTPUTS`. Para agregarlo hay que confirmar que `parser_editorial` ESCRIBE al dir del `--output` temp (el docstring dice "aparte" → puede escribir a ruta fija; si es así, parametrizar primero). Hoy solo lo cubre el manifest (provenance), no la byte-regression de refactor.
**Estado del fix:** no diseñado en código (scope nuevo; requiere el inventario en disco de arriba). Diferido de H138 por ventana.
**Referencias cruzadas:** `check_regresion.py`, `generar_manifiesto.py` (v1.5), accuracy-gold n300, los 4 `test_*`. H138. Sin ID histórico.

### M25 — `parte_ganadora`: detector real del texto en vez de derivarla de la disposición — DESCARTADO H158 (lockeado)

**Componente:** capa-deriver (`clasificador_disposicion.py` / `derivar_recursos.py`).
**Origen / fuente del diagnóstico:** H140. Al examinar por qué `parte_ganadora` da el κ más bajo del set M20 (**0,653 [0,504–0,783]**, "sustancial", frente al casi-perfecto del resto).
**Causa raíz:** `parte_ganadora` NO se lee del texto — se *deriva* de la disposición (`out["parte_ganadora"] = out["disposicion"].map(parte_ganadora_regla)`). Es una proyección de disposición, no una detección independiente. "Quién gana" necesita el ROL procesal (quién recurrió) y la GRANULARIDAD (total vs parcial), que el verbo dispositivo no contiene.
**Diagnóstico / evidencia (H140, medido sobre el gold n=135 fondo):** la regla determinística óptima disposición→parte (deja_sin_efecto/revoca→recurrente_gana; confirma→recurrente_pierde; modifica→parcial) toca un **TECHO de 0,889** — aun con la disposición perfecta no puede superarlo. Los 15 que escapan son SEÑAL, no ruido, en dos grupos:
- **parcial (8):** `329_p3213`, `332_p962`, `337_p373` (confirma); `329_p5007`, `337_p505`, `349_p280` (revoca); `348_p296`, `332_p2208` (deja_sin_efecto). Resultado mixto que una disposición binaria no refleja.
- **inversiones de rol (7):** confirma→recurrente_gana `329_p5368`/`331_p2257`/`340_p1450`/`344_p344`; revoca→recurrente_pierde `333_p300`/`333_p1639`; deja_sin_efecto→recurrente_pierde `346_p675`. La disposición favorece a una parte pero el recurrente está del otro lado.
**Efecto en el κ:** además del techo, el desbalance (`recurrente_gana` 104/135 = 77%) infla pe y comprime κ → accuracy 0,794 pero κ 0,653. Las clases minoritarias (`parcial`, `recurrente_pierde`) son las que κ premia; un detector real que las recupere sube el κ fuerte, no solo el accuracy.
**Validador propuesto:** extraer los 15 con `extraer_caso.py`, confirmar que son inversiones/parciales genuinos (no error de codificación del gold). Si lo son → detector de texto leyendo rol procesal (`es_queja` + vía/tipo de recurso + partes) + granularidad. Banco de prueba = esos 15.
**Actualización H151:** los 8 `parcial` recodeados a mano leyendo el `.md` y colapsados a binario por la regla SCDB (`partyWinning` no tiene clase parcial; victoria parcial = gana) → `329_p3213`/`337_p373`→pierde, resto→gana, Maza→gana. Con el parcial resuelto, el banco efectivo del detector de texto se concentra en las **7 inversiones de rol** (la señal genuina que el verbo dispositivo no contiene). Gold consolidado en `planilla_M20_57GOLD_parte_limpia.xlsx` (134 fondo, 110 gana / 24 pierde). **κ recomputado H151: 0,784** [.632–.908] (n=134, acuerdo 0,933) — sube de 0,653; el residual (~9 desacuerdos) son las 7 inversiones de rol = el banco del detector de texto.
**Actualización H153 (Ruta 1 — `parcial` eliminado del OUTPUT):** la regla de derivación `parte_ganadora_regla` (`clasificador_disposicion` v1.08→**v1.09**) deja de emitir `parcial`: `modifica` entra al grupo gana (SCDB: `partyWinning` binario, victoria parcial = gana; blindaje no-reformatio-in-pejus — el recurrente no sale peor de su propio recurso). Los **3 únicos `parcial` del corpus** (`329_p2864` Olivan/superintendencia, `331_p1282` Patoco c/ ANSeS/movilidad, `331_p1890` Picapau/pesificación) — los tres `multi_recurso=no`, los tres coincidían 1:1 con `disposicion=modifica` — validados a mano sobre el `.md` (extraídos con `extraer_caso.py`) → los tres `recurrente_gana`. `recursos.csv` re-derivado: `parte_ganadora` **binario {recurrente_gana 2335 / recurrente_pierde 537 / no_aplica 3018}**, 0 `parcial`, 3 celdas cambian. `disposicion()` INTACTO (κ disposición 0,912 sin tocar); firma de la regla sin cambio (call site `.map` del deriver intacto). **κ-parte 0,784 sin cambio** (los 3 no caen en el gold n=134). Manifest re-sellado **[CLEAN] 63** (`recursos.csv` sha `e4e90c08d091…`, 5890 filas, deriver v0.5). **M25 SIGUE ABIERTO:** esto alinea el OUTPUT con el gold binario de H151 (elimina el valor `parcial`), pero el detector de texto de las **7 inversiones de rol** —la señal genuina que el verbo dispositivo no contiene— sigue sin construir.
**Estado de verificación:** `confirmado_cuantificado` (techo 0,889 medido en disco H140).

**Actualización H158 — DESCARTADO y LOCKEADO.** Probadas en disco las dos rutas determinísticas para detectar las inversiones de rol: (1) el cruce `disposicion × recurrente_rol` over-firea (`confirma×demandada` 61 casos para ~3 inversiones; `deja×demandada` 164 para 1); (2) el marcador de disposición `"con el alcance"` over-firea ~3:2. La señal que separa una inversión real de una no-inversión es de **MÉRITO** (a favor de quién era la sentencia revisada y de qué lado está el recurrente), no un patrón presente en `{disposicion, recurrente_rol, por_ello}` — par mínimo `342_p1393`/`344_p344`: `por_ello` casi byte-idéntico + firma `(confirma,demandada)` idéntica, lecturas opuestas. **Detector determinístico inviable; no hay banco que detectar por patrón.** Sin cambios canónicos (parser v22.0 intacto, golden [CLEAN]).
**Estado del fix:** DESCARTADO — no reabrir sin evidencia nueva.
**Estado del fix:** no diseñado (es el campo v0.3 que `derivar_recursos` ya anota: "eje queja/concedido, admisión").
**Referencias cruzadas:** M20 (validación), disposición (`clasificador_disposicion`), B127 (OBJ-vocab toca parte). H140. Sin ID histórico.

### M26 — Refactor admisión/mérito: de-interleave de `outcome` en dos canales canónicos

**Componente:** parser (+ `derivar_recursos`, votos, `causa_inadmisibilidad`, CODEBOOK, Dataverse).
**Origen / fuente del diagnóstico:** H141 (escalado desde B129).
**Causa raíz:** `outcome` es un campo plano que conflaciona dos ejes —admisión (procedente/280/desestima) y mérito (revoca/confirma)— e `is_merit` cuelga de él. Resultado medido en disco (H141): **175** casos `disposicion=FONDO` ∧ `gate=no`, **153** `gate=sí` ∧ `disposicion≠FONDO`, `procedente` total **759** (casos donde el parser se quedó en admisibilidad). El deriver ya tiene la señal correcta (24/25 de B129 con `disposicion=FONDO` pero `es_revision_fondo=no`); la fix robusta no es parchar el deriver sino separar los canales en el origen.
**Diseño (LOCKED):** dos canales canónicos del parser — `admision` (multiclass) y `disposicion` (multiclass FINO) — + eje COARSE `{fondo, procedimiento, originaria}` como rollup. `is_merit = (disposicion ∈ fondo)`, con **fondo = revoca · deja_sin_efecto · confirma · modifica · nulidad sustantiva**. `disposicion` fino conserva los granulares (competencia, nulidad_concesion, aclaratoria, revocatoria, procesal); `procedimiento` = no-fondo, no-originaria (rollup). **Corte de nulidad (define el borde del fondo):** nulidad del auto de concesión = procedimiento; nulidad de la sentencia / de todo lo actuado = fondo. Reusa la detección existente (REE, no reinventa): `clasificador_disposicion` para mérito; consolidar `RE_GRANT` (admite) + cascade 280/ac4/desestima (inadmite) en `clasificador_admision.py` nuevo (fuente única). `outcome` → derivado legacy deprecado (opción B recomendada; A = corte duro abierto).
**Refinamiento doctrinal (H142, LOCKED por Guillermo):** `procedente`/`admisible` = SIEMPRE admisión, NUNCA fondo por sí (no indican ganador; el mérito y el ganador = el VERBO). `hace lugar` es OBJECT-DEPENDENT: **al recurso** = recurrente_gana (fondo, trae verbo atrás) / **a la queja** = admisión / a la cautelar/demanda = procesal/originaria. Material del canal admisión ya existe: `admisible` vive en `QUEJA_RESULTADO_PATTERNS` (parser l.766+, campo `queja_resultado`); fórmula canónica en el comentario de parser l.392-394. `is_merit = (disposicion ∈ fondo [+ grant_remand]) AND NOT originaria`.
**Estado de verificación:** `confirmado_cuantificado` (175/153/759 en disco, H141).
**Validador propuesto:** Fase 1 = A/B en disco que simula el de-interleave sobre los 5890 antes de implementar (flips de `is_merit`, resolución de los 175/153, distribución de `admision`/`disposicion`, eyeball). Después: re-golden consciente contra `cod_disposicion`/`cod_es_revision_fondo` + recomputar TODOS los κ + re-sellar manifest + republicar Dataverse.
**Estado del fix:** diseñado; **Fase 1 (A/B) CERRADA H142** (`scripts/diagnostico/H142/ab_deinterleave_fase1.py` v2 — 175/153/+22 reproducido en disco; doctrina lockeada; canal admisión armado de `queja_resultado`+`procedente`). Fase 2 (cirugía del parser) = próxima. Plan por fases en `PROMPT_H143_cirugia_parser.md`.
**Decisiones abiertas (tras H142):** `outcome` A (dura) vs B (blanda) — sin lock; value-set de `admision` (~1047 a clasificar + competencia 903 al coarse; material en `queja_resultado`); **perilla grant_remand** (dentro de fondo, rec.) y **guard originaria** (se queda, rec.) — pendientes de lock formal. **RESUELTAS H142:** `competencia` → bifurca originaria/procedimiento (Q2); `procedente`/`admisible` → admisión (nunca fondo).
**Referencias cruzadas:** B129 (origen), B127 (premisa bifásica refutada H139), B131 (nulidad/auto), HM-01, M19/M20 (κ se reabre). H141. Sin ID histórico.

### B129 — Falso inoficioso: `result\w+ inoficioso` (dictamen PGN) clasifica revocación como `abstracto` — CERRADO H145

**Fix aplicado (H145):** el lookahead `(?![^.]{0,40}(?:dictamin|procurador))` se incorporó al guard `RE_DISP_INOFICIOSO` de `clasificador_disposicion` v1.08 (gate function `es_revision_fondo`, NO al parser — `outcome`/`is_merit_decision` siguen con el bug, pero el gate ya no cuelga de ellos tras el rewiring). Absorbido por el rewiring M26, no commit standalone. Validado en disco corpus: 24 asides-dictamen conservados como fondo (revoca/deja/procedente), 22 mootness genuina fuera de fondo; n300 gate 0,946, 0 regresión.

**Componente:** parser (`RE_DISP_INOFICIOSO` + pattern alto abstracto).
**Origen / fuente del diagnóstico:** H138 (alta) / H141 (diagnóstico cerrado). Caso testigo `334_p1272` (salvataje hipotecario, leyes 25.798/26.167).
**Causa raíz:** alt-2 `(?:deviene|torna|result\w+)\s+inoficioso` matchea "resultando inoficioso que dictamine el PGN" → devuelve `abstracto` ANTES de que la cascada vea "se revocan" → `outcome=abstracto` → `is_merit=0` → `es_revision_fondo=no`. Es un aside del dictamen, no mootness de fondo. Fórmula endémica CSJN; el comentario de B119 (parser ~l.493-496) ya lo anticipaba.
**Diagnóstico / evidencia (H141):** A/B validado (`scripts/diagnostico/H141/ab_b129_inoficioso.py`) — **25 flips** `abstracto`→`{revoca 5, procedente 16, confirma 2, hace_lugar 1, nulidad 1}`, **0 regresiones**, `348_p1499` intacto, los 25 ∈ MERIT_OUTCOMES, `is_originaria=0`, eyeball = falso-inoficioso genuino.
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto / fix:** lookahead `(?![^.]{0,40}(?:dictamin|procurador))` en `RE_DISP_INOFICIOSO` + pattern alto. VALIDADA en A/B.
**Estado del fix:** **APLICADO / CERRADO H145** — el lookahead va en el guard del gate (`es_revision_fondo`, clasificador_disposicion v1.08), no en el parser; absorbido por el rewiring M26.
**Referencias cruzadas:** M26 (lo subsume), B119. H141, H145.

### B131 — `nulidad del auto de concesión` puede clasificarse como fondo

**Componente:** parser / `clasificador_disposicion`.
**Origen / fuente del diagnóstico:** H141 (taxonomía del refactor M26, corte de nulidad).
**Causa raíz:** el pattern `nulidad` de `clasificador_disposicion` usa `OBJ` que incluye `auto` → puede matchear "nulidad del auto de concesión" (que es procedimiento) como `nulidad` sustantiva (fondo).
**Diagnóstico / evidencia:** hipótesis del corte de nulidad. **Cuantificado parcialmente H142:** el A/B muestra **30 casos `outcome=nulidad_concesion` que el deriver etiqueta `disposicion∈fondo`** (los gana el de-interleave) — hotspot exacto donde el `nulidad` del clasificador podría estar colando "nulidad del auto de concesión" como fondo. Falta el por_ello de esos 30 para confirmar.
**Estado de verificación:** `confirmado_caso_testigo` (30 candidatos cuantificados H142; eyeball pendiente, requiere `csjn_casos_textos.csv`).
**Validador propuesto:** grep de "nulidad del auto" / "nulidad ... concesión" en `por_ello_text`; verificar que `nulidad_concesion` (pre-cascade del parser) lo agarre antes que `nulidad`, o desambiguar el regex del clasificador.
**Estado del fix:** no diseñado (se resuelve dentro de M26, Fase 2).
**Referencias cruzadas:** M26, H141. Sin ID histórico.
**Nota H170:** el guard `RE_NULIDAD_CONCESION` (cerrado H143 con esta entrada) tiene la ventana insuficiente cuando la referencia al auto se intercala («nulidad parcial del auto de fs. … en cuanto … concedió», testigo `343_p2098`) → gap registrado como sub-causa (b) de **B140**.

### B132 — `_SYN_Q` no cubre "recurso de queja" → admisión de queja perdida en `queja_resultado`

**Componente:** parser (`QUEJA_RESULTADO_PATTERNS` / `classify_queja`, ~L766).
**Origen / fuente del diagnóstico:** H146 (object-aware del canal admisibilidad; fuga de `sin_marcador`).
**Causa raíz:** el sinónimo de queja `_SYN_Q` matchea `quejas?` / `presentación directa` / `recursos? de hecho`, pero NO la frase "recurso de queja". El patrón de admisión espera `(?:el\s+)?{_SYN_Q}`, así que "se declara admisible **el recurso de queja**" no dispara (el "el " consume y después viene "recurso", no la palabra queja) → `queja_resultado` queda vacío y el caso cae a `sin_marcador`.
**Diagnóstico / evidencia:** `331_p434` "se declara admisible el recurso de queja" → `queja_resultado=''`. Recuperado en H146 por el `RE_ADMITE_REX_TXT` del `clasificador_admision` (object ∈ {REX, queja}), pero el origen está en el parser. Cardinalidad sin cuantificar (grep de "recurso de queja" en `por_ello_text` pendiente).
**Estado de verificación:** `confirmado_caso_testigo` (1 caso; cardinalidad pendiente).
**Validador propuesto:** grep `recurso(s)? de queja` en `csjn_casos_textos.csv`; comparar contra `queja_resultado` no-vacío; agregar la alternativa a `_SYN_Q` y re-medir `queja_resultado` + `es_queja`.
**Estado del fix:** no diseñado (capa parser → fuera de M26 capa-deriver; commit separado).
**Referencias cruzadas:** H146, M26 (canal admisibilidad). Sin ID histórico.

### HM-01 — El gate de admisibilidad como aporte del corpus frente al SCDB (metodológico)

**Componente:** metodológico (CODEBOOK / tesis, capítulo metodológico).
**Origen:** H141 (encuadre del refactor M26).
**Contenido:** el SCDB deriva `partyWinning` de `caseDisposition` trabajando POST-gate (los cert denials no se colectan). corpus-csjn tiene el gate ADENTRO (art. 280 / certiorari criollo conviven en Fallos con el fondo) → debe DETECTARLO. La admisibilidad es una dimensión que el SCDB descartó; modelarla explícitamente (canal `admision` + flag de revisión de fondo) es la sofisticación específica del instrumento argentino. El refactor M26 (separación admisión/mérito) es su expresión arquitectónica.
**Destino:** sección de método del CODEBOOK (Fase 5 de M26) + tesis (relación con H1, certiorari criollo). Grepeable como `HM-01`.
**Materializado H142:** los dos gates YA están en el corpus — admisión de la queja en `queja_resultado` (campo H078) + procedencia del REX en `procedente`/`admisible`. El A/B confirma las dos vías: `procedente` 9% queja (REX concedido) vs `hace_lugar` 93% queja (recurso de hecho). `clasificador_admision` (Fase 2) los consolida; el de-interleave es la expresión arquitectónica de HM-01.
**Avance H146:** `clasificador_admision.py` v0.1 construido; HM-01 NO se modela como valores fusionados sino como el cruce `admisibilidad × es_queja` (la queja es modo de acceso TRANSVERSAL, no un valor del eje). Cuantificado en disco: la queja es transversal a la vía-tipo (98,5% REX, 30 ordinario), a la admisibilidad (admite 1598 / inadmite 624) y al mérito (revoca+deja 1412 / confirma 106); admitir la queja implica resolver el REX (193/1485 enuncian "procedente" explícito, 1235/1292 restantes resuelven al fondo).
**Referencias cruzadas:** M26, M20 (certiorari criollo queja 95% vs concedido 68%). H141.

### B133 — `clasificador_admision` sub-marca la cuestión abstracta (mootness) como NO inadmite

**Componente:** deriver (`clasificador_admision.py`, eje admisibilidad).
**Origen / fuente del diagnóstico:** H147 (A/B del re-cableo de `causa_inadmisibilidad` + corrección doctrinal de Guillermo, respaldada por el tratado de la Secretaría: la mootness es decisión de ADMISIBILIDAD — la actualidad del agravio es requisito de admisibilidad, no fondo; sin caso vivo se rechaza el planteo sin entrar al fondo).
**Causa raíz:** `clasificador_admision` keyea en señales de concesión/gate (procedente / hace lugar / admisible) y NO reconoce "se declara abstracta la cuestión" como inadmisión. La mootness pura no trae verbo de mérito ni marcador de inadmisión explícito → cae a `admite` / `sin_marcador`.
**Diagnóstico / evidencia (5890):** de 148 `outcome=abstracto`, solo **5** son `admisibilidad=inadmite`; 143 quedaron `admite`(49) / `sin_marcador`(87) / `no_aplica`(7). Split: **~96 abstracción pura** (`disposicion=no_fondo`, gate=no) → deberían ser `inadmite` + causa `CUESTION_ABSTRACTA`; **~52 mixtos** (verbo de mérito real: 28 revoca + 15 deja_sin_efecto + 4 nulidad…) → son mérito, el abstracto es un subtema secundario (vive en `outcome` legacy), NO se tocan.
**Estado de verificación:** `confirmado_cuantificado` (sobre 5890, en disco H147).
**Validador propuesto:** detector `se declara abstracta la cuestión` / `devino abstracto` (ancla dispositivo; guard contra el mixto = sin verbo de mérito en `disposicion`) → `admisibilidad=inadmite`; A/B sobre los ~96 puros; re-medir κ-admisibilidad. Rótulo de causa confirmado por la Secretaría: `CUESTION_ABSTRACTA` ("cuestión abstracta" / "falta de actualidad del agravio").
**Estado del fix:** no diseñado (frente κ-admisibilidad; el detector vive en `clasificador_admision`).
**Referencias cruzadas:** H147, M26 paso 3 (re-cableo causa), κ-admisibilidad (verificación diferida H146), M27 (vocabulario canónico). Sin ID histórico.

### M27 — Vocabulario canónico de `causa_inadmisibilidad` sobre la taxonomía de la Secretaría de Jurisprudencia

**Origen:** H147. Fuente = tratado del REX de la **Secretaría de Jurisprudencia de la CSJN** (`documento__37_.md`, actualizado 11/06/2026), la misma Secretaría que edita los tomos del corpus.
**Fundamento (validez de constructo):** aterrizar `causa_inadmisibilidad` en el esquema sistemático de requisitos de admisibilidad de la Secretaría = operacionalizar la doctrina de admisibilidad de la Corte sobre las propias decisiones de la Corte (análogo al SCDB con sus dispositions). Reemplaza el vocabulario ad-hoc por categorías canónicas.
**Mapeo verificado (índice del doc):** 8 causas actuales mapean a categorías reales — extemporáneo §1.3.10, fundamentación §1.4.3, Acordada 4/2007 §1.5, desistimiento §2.1.11, caducidad §2.6, sentencia definitiva §4, art. 280, depósito (queja, art. 286). Rótulo de mootness confirmado: `CUESTION_ABSTRACTA` = "cuestión abstracta" / "falta de actualidad del agravio" (término de la Secretaría, NO cambia).
**5 GAPS (categorías Secretaría sin causa hoy):** interposición incorrecta / ante-quién §1.2.2 (queja→CSJN, REX→a quo = "tribunal equivocado"); salto de instancia / per saltum §1.2.7.3, §1.5.1.2.3; tribunal superior de la causa (Levinas, Fallos 347:2286); relación directa; introducción oportuna de la CF.
**Oportunidad medida (5890):** ~95/429 del cajón `INADMISIBLE_SIN_CAUSAL_EXPLICITA` llevan señal canónica detectable (depósito 43 sub-capturado · tribunal superior de la causa 19 · relación directa 15 · CF oportuna 13 · per saltum 6 · fundamentación 3). **EXPLORATORIO, cota superior, polisémico** → cada causal exige disciplina holding-vs-antecedente (el doc da el fraseo por sección).
**Validación cruzada:** el tratado confirma la polisemia de caducidad (§2.6.1 *se hace lugar al planteo* / §2.6.2 *se rechaza el planteo*) = el guard del detector caducidad de H147.
**Disciplina:** un detector por causal, fuente = su sección del doc, guard de polisemia, eyeball, **commit SEPARADO** (NO fundido al re-cableo M26 paso 3 — atomicidad: el re-cableo se valida por su A/B; cada causal nueva por su sección + eyeball). Conecta con las candidatas H092 (`sub_gate.py`, parser L608-610, nunca validadas) y la cola larga.
**Estado:** ABIERTO H147 (diseño + dimensionamiento). Construcción pendiente. Fuente: `documento__37_.md` (subir al arrancar).
**Referencias cruzadas:** H147, M26 paso 3, B133 (mootness), H092 (candidatas `sub_gate.py`).

### B134 — `clasificador_admision`: originarias leak a `inadmite` por precedencia de cascada

**Componente:** deriver (`clasificador_admision.py`, eje admisibilidad).
**Origen / fuente del diagnóstico:** H149 (auditoría del cajón `INADMISIBLE_SIN_CAUSAL_EXPLICITA`, gatillada por Guillermo: "son muchos los sin causa").
**Causa raíz:** en la cascada de `admisibilidad()`, la rama `is_originaria → no_aplica` (paso 4) va DESPUÉS del gate REX (paso 2, `outcome ∈ R_INADMITE`). Una originaria con `outcome="desestima"` (∈ R_INADMITE) se captura como `inadmite` antes de llegar a su rama. Doctrinal: en competencia originaria (art. 117) NO hay gate de admisibilidad — la Corte resuelve la acción en su instancia; "desestima" ahí es resolución, no rechazo de un REX → debe ser `no_aplica`.
**Diagnóstico / evidencia (5890):** 11 `is_originaria=1` en el cajón SIN_CAUSAL, 13 en todo `inadmite`. Los 13: `queja_resultado` vacío, `es_queja=0`, `outcome=desestima` → entran por el gate REX, no por queja. 9 limpios (via vacía, disposicion no_fondo/no_revision_*); 2 contradictorios (`331_p1432`, `348_p439`: `via_recurso=recurso_extraordinario`, que choca con originaria → o is_originaria es FP o la vía lo es).
**Estado de verificación:** `confirmado_cuantificado` (sobre 5890, en disco H149).
**Validador propuesto:** banco de los 13 + sample de is_originaria; eyeball de los 2 contradictorios sobre texto real.
**Estado del fix:** no diseñado. Reordenar precedencia (`is_originaria` pre-empta el gate outcome) **solo tras validar la calidad de is_originaria** — no flipear a ciegas (los 2 contradictorios avisan posibles FP). Magnitud chica (13) — NO explica el cajón 473 (eso es M27 + diseño `no_revision_*`).
**Referencias cruzadas:** H149, M27, cajón SIN_CAUSAL, `clasificador_admision`. Sin ID histórico.

### B135 — `is_originaria` SUBDETECTA: señal de demanda originaria disponible pero no usada en el gate — CERRADO COMPLETO H181 ((a)+(b) H172 · (c) H181)

**Componente:** parser (`es_originaria`, L1285) / eje is_originaria.
**Origen / fuente del diagnóstico:** H156 (al reconciliar el residual de M29: ¿por qué tantos fallos sin recurrente? — separar originaria real de acceso-denegado).
**Causa raíz:** `es_originaria` no aprovecha toda la señal disponible. `RE_CN_DEMANDA_ESTADO` (parser L1277-1321) está DEFINIDA pero NUNCA USADA en `es_originaria` — el detector deja afuera demandas originarias que el case_name marca (`c/ Provincia de …` / `c/ Estado Nacional` en posición de demanda directa, sin a-quo ni recurso).
**Diagnóstico / evidencia:** pool de **275 fallos** con `case_name` tipo `c/ Provincia|Estado` pero `is_originaria=0`, de los cuales **133 son de mérito**. PERO la precisión de case_name SOLA es baja ≈**11%** (medido sobre 64 legibles: 22 apelación / 7 originaria / 3 ambiguo / 32 indeterminado) → el case_name NO alcanza para flipear; un `c/ Provincia` puede ser apelación de un juicio donde la provincia es parte, no acción originaria. Total `is_originaria=1` hoy = **546** (consistente con la cota doctrinal "~500-550").
**Estado de verificación:** `confirmado_cuantificado` (275/133 sobre el corpus; precisión 11% sobre muestra de 64 — H156).
**Validador propuesto:** señal COMPUESTA en `es_originaria` (case_name `c/ Estado-provincia` **+** corroboración de demanda-originaria del cuerpo **+** ausencia de recurso/a-quo), NO case_name a secas. Cuantificar el flip-limpio corpus-wide requiere `csjn_casos_textos.csv`; eyeball del subconjunto ambiguo.
**Estado del fix:** no diseñado. Toca el parser → re-golden (NO aprovecha lo de H156, que es capa-deriver). Limpia el denominador de M29 (separa originaria real de acceso-denegado) y desbloquea/depura **B134** (los 2 contradictorios via=REX).
**Referencias cruzadas:** **B134** (originarias leak a inadmite), **post-B010** (recalibrar is_originaria, ahora cuantificado), L624, M27. H156. Sin ID histórico.

**Actualización H170 (D1/M39), `confirmado_cuantificado` — TRES sub-causas nuevas:**
**(a) Regex angosta:** `RE_COMPETENCIA_ORIGINARIA` (parser L1260) exige la cola «de esta Corte / del Tribunal / de la Corte Suprema»; las fórmulas «mantener su / asume su competencia originaria para dictar sentencia» NO matchean. Medido (consistencia_merito v0.3): **15/15 del bucket M1 recuperables por el ensanche** — 329_p2226, 329_p2688, 329_p3894, 329_p4944, 330_p563, 331_p1690, 332_p1688, 332_p2265, 332_p2842, 334_p996, 334_p1821, 337_p901, 338_p652, 342_p2198, 348_p983. Guard obligatorio antes de aplicar: holding-vs-antecedente («competencia originaria» citada de un precedente no debe flipear) + validar 0 flips sobre las 546 actuales.
**(b) Guionado + banner parte la señal:** verificado en disco (sidecar de `337_p234` Credicoop): «competencia origi- [running head 247 DE JUSTICIA…] naria de esta Corte» — la palabra partida por fin de página derrota CUALQUIER regex sobre texto crudo, incluso la amplia. La detección debe correr sobre texto normalizado (des-guionado + banner mask) → **los 15 de (a) son PISO**; cardinalidad real del miss por guionado pendiente de medir corpus-wide. **Re-jerarquiza D5** (asimetría de normalización intra-deriver, ver M40): deja de ser consistencia/elegancia y pasa a condición previa del fix.
**(c) Carátula invertida:** `RE_CN_DEMANDA_ESTADO` (L1278, la regex huérfana) NO cubre la forma canónica de Fallos «X c/ <Nombre>, Provincia de» (verificado: «Bustos c/ La Pampa, Provincia de»; «Coihue S.R.L. c/ Santa Cruz, Provincia de») — 0/15 flags en M1 y 3/13 en M2C siendo casi todos pleitos contra provincias. Cablearla tal cual está rendiría poco; normalizar la forma invertida es parte del fix de la señal compuesta.
**El ensanche (a) NO cierra B135:** `329_p3403` (Ferrari de Grand, señal en el Resulta) y `344_p3476` (Coihue, señal solo en Resulta/voto concurrente) tienen la mención FUERA de `considerando_text` → la señal compuesta (case_name normalizado + corroboración + ausencia de recurso/a-quo) sigue siendo necesaria. **Originarias adicionales confirmadas por lectura H170:** 329_p3403, 337_p234, 344_p3476 (+ 348_p473 ya adjudicada H161). Post-B136 este bug contamina `is_merit` directamente (la originaria no detectada cae a la cascada de apelados). Orden del fix: B135 es el paso 1 de M39.

**Cierre H172 — sub-causas (a)+(b) IMPLEMENTADAS y validadas en disco (parser v23.0→23.1), `confirmado_cuantificado`:**
Fix cableado a `es_originaria`: **(b)** `RE_RUNNING_HEAD.sub(" ", cuerpo)` ANTES de `_unhyphenate` — el banner intercalado partía la señal («competencia origi-[banner]naria») y `_unhyphenate` unía el guión con el NÚMERO de página (`\w` matchea dígitos), no con «naria». Miss por guionado corpus-wide **medido = 1** (337_p234 Credicoop; los 15 de (a) NO eran piso, eran casi el techo). **(a)** 5ª señal `competencia originaria` pelada, DESPUÉS de las 4 existentes, con 4 guards POR-MATCH calibrados contra FP leídos: `local` (cita CIDH «competencia originaria local», Barreto Leiva: 337_p901/342_p2389), `apelada` («originaria o apelada», aside doctrinal: 339_p1254), `precedente` («…originaria en la causa "X"»: 345_p220), `provincial` (tribunal/constitución provincial en ventana previa W=120: 329_p6072 TSJ Neuquén, 330_p76 Const. del Chaco).

**Metodología (PoC read-only antes de tocar el parser):** `scripts/diagnostico/H172/poc_b135_flips.py` v0.1→v0.3, importa detectores reales del parser (Gate 3), mide el flip-set corpus-wide bajo las condiciones EXACTAS del fix. Anclas A1 (replicación es_originaria == columna publicada), A4 (0 pérdidas 1→0), A2' (14/14 M1), A3 (Credicoop por mask), A5 (7 FP fuera), A6 (igualdad exacta contra set de 43) — TODAS [OK] en v0.3. Los 8 flips ambiguos adjudicados por lectura contra el `.md` (extraídos H172).

**Flip-set final = 43 = 39 TP + 4 FP-F5 aceptados.** Clases de FP identificadas y su tratamiento: **F1** «originaria local» CIDH (guard `local`), **F2** tribunal provincial (guard `provincial`), **F3** «originaria o apelada» (guard `apelada`), **F4** precedente «en la causa X» (guard `precedente`), **F6** doctrina causa-o-controversia art. 116/117 (resuelto al RECHAZAR el ensanche art.117), **F5** historia procesal narrada / doctrina — NO regexeable sin overfit → **4 FP ACEPTADOS y documentados**: 349_p163 (Banco de Bosques, cautelar), 347_p2146 (Cruz c/ Tucumán), 347_p2286 (Ferrari-Levinas), 334_p1842 (Sorrento, precedente citado ANTES de la mención → guard precedente no aplica). **Costo real medido del FP-F5: 347_p2146 pierde is_merit** (REX de mérito genuino que al marcarse originaria cae porque es_de_fondo no ve verbos de demanda) — 1 caso de mérito incorrecto contra 39 TP. Los otros 3 F5 no tenían is_merit que perder.

**Ensanche de `RE_ART_117_CN` a «116 y 117»: medido y RECHAZADO.** Contribución marginal corpus-wide = 0 TP / 1 FP (348_p841, doctrina causa-o-controversia en REX). `RE_ART_117_CN` queda INTACTA; la señal pelada ya cubre los holdings «artículos 116 y 117».

**M1 corregido 15→14:** 337_p901 (Duarte, doble conforme penal) adjudicado FP — su única mención de originaria es la cita CIDH; es REX penal, no originaria. Su membresía en M1 era mecánica (señal amplia + is_merit=1 + is_originaria=0), no adjudicada. Gemelo confirmatorio 342_p2389 (misma cita párrafo 90 Barreto Leiva).

**Validación post-cableado (`verificar_b135_post.py` v0.2, diff fila-a-fila vs golden):** P1 is_originaria=1 546→**589** [OK]; P2 43/43 [OK]; P3 7/7 FP fuera [OK]; P4 cambios confinados a los 43 IDs × {is_originaria, is_merit_decision, tribunal_origen_status} [OK]. **Ripple de is_merit BIDIRECCIONAL** (B136 sobre las 43 nuevas): 3003→**3006** (+6/−3). Suben (0→1, todas `rechaza`-de-fondo, mérito denegatorio que el verbo apelativo no veía): 329_p2088, 330_p748, 330_p4064, 332_p552, 334_p376, 337_p712. Bajan (1→0): 329_p2226 (caducidad en originaria, correcto), 329_p3894 (M1, `hace_lugar` — **eyeball pendiente H173**: ¿a la demanda o a un incidente?), 347_p2146 (FP-F5, costo documentado). Golden re-sellado (csjn_casos sha b8a21dcd1169), recursos re-derivado v0.6, manifest [CLEAN] 64.

**Efecto en M39 (paso 1):** divergencia 234→**219**. Los 14 M1-verdaderos convergieron. El «1» que `consistencia_merito` v0.3 sigue reportando en M1 (337_p901) es divergencia del detector de DIAGNÓSTICO (regex `RE_ORIG_AMPLIA` sin guards) contra el parser — en el parser 337_p901 está correctamente en 0. **M1-real-del-parser = 0.** (Fix cosmético opcional: portar los 4 guards a la regex amplia del diagnóstico.)

**Sub-causa (c) — señal compuesta — PENDIENTE:** case_name «c/ Provincia|Estado» normalizado (incl. carátula invertida «X c/ Nombre, Provincia de») + corroboración de demanda-originaria + ausencia de recurso/a-quo. NO cablear case_name solo (precisión ≈11%, H156). Casos con señal fuera de `considerando_text` que (a)+(b) NO recuperan: 329_p3403 (Ferrari de Grand, señal en el Resulta), 344_p3476 (Coihue, voto concurrente) — siguen en M2C. Es diseño de precisión para sesión dedicada.

**Cierre H181 — sub-causa (c) IMPLEMENTADA y validada en disco (parser v24.0→24.1), `confirmado_cuantificado`:** señal 6 COMPUESTA en `es_originaria` = case_name demanda-contra-Estado/Provincia (`RE_CN_DEMANDA_ESTADO` ensanchada con la forma invertida «c/ <Nombre>, Provincia de» — Ferrari L191 «c/ Entre Ríos, Provincia de», Coihue L499 «c/ Santa Cruz, Provincia de»; la regex deja de ser huérfana) ∧ `_orig_pelada_con_guards` reusada INTACTA (4 guards H172) sobre la ventana RESULTA (`_ventana_resulta`: apertura `RE_VISTOS` → primer `RE_CONSIDERANDO`, verbatim de `poc_b135c` v0.1). La señal de los objetivos vivía en el Resulta («A fs. 380 esta Corte asume su competencia originaria», 329_p3403 L335; «a fs. 90/91, esta Corte declara su competencia originaria», 344_p3476 L607) — fuera de `considerando_text` por construcción. PoC en disco: A0 identidad 0 diffs/5890 · pool 326 → 6 · **flip-set 6 = 6 TP adjudicados por lectura** (329_p3168, 329_p3403, 340_p1025, 342_p917, 344_p3476, 348_p1686) · 0 FP · F5 intactos. Ripple: **is_originaria 589→595** · is_merit +5 vía rama originaria del gate (Equística requirió además v1.16: «Condenar AL Estado» rompía `\bcondenar\s+a\b` de `RE_FONDO_EXTRA_GRANT` por la contracción — ensanche `al?`, poc_condenar_al: flip-set 1=testigo, 0 pérdidas, 0 FP-costas, superficie no-originaria 5 con efecto 0) · `tribunal_origen_status→originaria` en los 6 (Coihue corrige `apelado_detectado` FALSO — contraejemplo del flag como señal de a-quo). **Ruta D (dispositivo: verbos-de-demanda en el pe ∧ contra-Provincia ∧ sin a-quo) evaluada y DESCARTADA-FUNDADA:** su testigo único 348_p473 = fila fantasma (⊂ 348_p461 La Rioja, ya orig=1/merit=1 — ver constancia B045). Corrección de constancia H178: los «3 costos autorreparables» eran **2 reales + 1 espurio**. Golden/manifest: ciclo empaquetado con v1.16, casos 6 filas / votos 28 (2 D-por-fallback en Barrick → B137), [CLEAN] 64.

### M28 — `admisibilidad` es síntesis determinística, no detección (reframe de reliability + HM-01)

**Origen:** H149 (medición sobre 5890, gatillada por Guillermo: "el derivador de admisible no detecta nada").
**Hallazgo:** `admisibilidad` reproduce **99,86% (5882/5890)** por relabeling de `{outcome, queja_resultado, disposicion, is_originaria}`; detector propio (`RE_ADMITE_REX_TXT`) = 8 casos. El eje NO detecta — sintetiza señales que el parser ya detecta.
**Implicaciones:** (a) **CODEBOOK** — `admissibility` NO lleva κ directo; reliability COMPOSITIVA (κ upstream outcome/queja M19 + disposicion 0,912 + is_originaria), regla de síntesis auditada por cruce (sacó B134). (b) **HM-01** — la contribución vs SCDB es de MODELADO (eje explícito acceso-vs-mérito sobre detección del parser), NO un detector novedoso del derivador; el writeup debe decir "eje explícito", no "detector". (c) El **ciego de admisibilidad deja de ser requisito**. (d) Si se quiere detección propia del acceso (leer por_ello/considerando independiente de outcome), es un frente nuevo.
**Estado:** registrado H149; sin acción de código requerida (reframe de documentación + HM-01).
**Referencias cruzadas:** H149, HM-01, M19 (κ upstream), B134, M27. Sin ID histórico.

### M29 — Capa de partes (petitioner/respondent): derivar actor/demandado + tipificación [PRIORITARIA — insumo SCDB]

**Componente:** capa-deriver (nuevo, patrón `derivar_materia` / `clasificador_*`).
**Origen / fuente del diagnóstico:** H153 (al cerrar Ruta 1 de `parte_ganadora`: el detector de texto de M25 necesita el ROL procesal —quién recurrió— que hoy NO existe derivado).
**Motivación / fundamento (SCDB):** no hay data derivada de partes; solo la carátula en bruto. Derivar actor/demandado + tipificar (persona física / sociedad / Estado-organismo) habilitaría un eje estilo `decisionDirection` del SCDB y le daría a M25 el insumo de rol procesal que le falta para resolver las 7 inversiones de rol (la disposición favorece a una parte pero el recurrente está del otro lado).
**Insumos disponibles (cuantificado H153, 5697 fallos):** `case_name_cuerpo` con patrón `c/` = **59,0% (3362)**; `case_name_indice` cruzado al índice editorial = **100%** (`csjn_editorial_indice_partes.csv`, 11445 entradas); señales de tipo triviales = **1370** sufijo societario (SA/SRL) · **1351** organismo/Estado (ANSeS/AFIP/Provincia).
**Estado de verificación:** `confirmado_cuantificado` (insumos medidos en disco H153).
**Validador propuesto:** parseo actor/demandado sobre `c/` + tipificación por diccionario; cruce con el índice editorial para los que no traen `c/`; medir cobertura; banco = las 7 inversiones de rol de M25.
**Estado del fix:** **capa 1 (epílogo) APLICADA Y VALIDADA H154**; **PASO 4 (carátula `case_name_cuerpo`) APLICADO Y VALIDADO H156**; frente 3 (arrastre de zona) + capa-cuerpo tail pendientes.
**Implementado H156 — paso 4 (carátula del fallo):** `derivar_partes.py` v0.4→v0.5 agrega `derivar_de_caratula()` como 4º escalón de la cascada: cuando falla el epílogo (`sin_marcador_recurso`) o no hay zona (`sin_zona`), deriva el recurrente de `case_name_cuerpo` ("Recurso … deducido por X en la causa …") con `RE_MARK_CARATULA` (= marcador de recurso + terminador "en la causa/las causas/los autos") + `parse_parte` verbatim. Es la MISMA atribución de recurso del epílogo (Eje B, voz de la Corte) en otra ubicación canónica → NO viola la doctrina de los dos ejes (no mapea actor/demandado). Buckets nuevos: `caratula:recurso` (nombre) / `caratula:rol_sin_nombre` (rol pelado "la actora"/"la demandada" → rol conocido, nombre vía Eje A). Soft-check de la columna `case_name_cuerpo` (degrada si falta). **ADITIVO PURO probado por diff v0.4↔v0.5 en disco: 169 filas cambian, TODAS desde `sin_zona` (98) o `sin_marcador_recurso` (71) → carátula; 0 regresión sobre los 3641.** Cobertura: **recurrente_ok 3641→3749 (+108 nombre)**, `caratula_rol_sin_nombre` 61. **Mérito (2870): 88,4%→90,5%** (nombre 89,3% · nombre-o-rol 91,8% · sin recurrente 235 = 8,2%). Eyeball de los 108: limpios (Boggiano, Astiz, AFIP, Estado Nacional, multi). Manifest [CLEAN] 65. **Reconciliación del residual (1893):** no-mérito-no-originaria 1133 + originaria 525 + mérito-no-originaria 235 (gap real = capa-cuerpo tail); `is_originaria`=1 total 546. **Hallazgo:** el recurrente del residual vive en `case_name_cuerpo` (canónico), NO en el `.md` → solo la cola con carátula plana `X c/ Y` (extradición/avocación/REX-directo, ~235) necesita leer cuerpo (capa-cuerpo tail, menor ROI). **Desbloquea M25** (el `recurrente_rol` que pedía existe). Polish abierto: `parse_parte` no resuelve "la defensa de X".
**Implementado H154 — capa 1 (Eje B: recurrente/recurrido desde el epílogo):** dos scripts NUEVOS en `scripts/pipeline/` (capa-deriver, parser v22.0 intacto): `extraer_epilogos.py` v0.2 → `csjn_casos_epilogo.csv` (insumo persistido; lee `zonas`+`corpus/*.md` con el offset relativo verbatim de H055; emite 5697 fallos 1:1 con `epilogo_status` ok 4345/76,3% · sin_zona 1352 · archivo_no_encontrado 0); `derivar_partes.py` v0.2 → `csjn_casos_partes.csv` (output; lee el CSV de epílogos, no el .md → reproducible para Dataverse; deriva el recurrente con marcador flexible anclado a línea `^(Recursos?|Queja)…(interpuest|deducid) por X[, rol]`). Cobertura: **recurrente_ok 3633 (63,8% de fallos / 84% de epílogos)**, epilogo_sin_marcador 712, sin_epilogo 1352, no_aplica 193, multi_recurrente (flag) 149. Rol del recurrente (sobre 3633): sin_rol 2383 · penal 444 · demandada 368 · actora 343 · solo_letrado 45 · querellante 21 · codemandada 18 · por_derecho_propio 9 · coactora 2. `parse_parte` resuelve el sub-patrón letrado (`por derecho propio`, `, por <parte>`, `defensor de <parte>`, `solo_letrado`). Corrida en disco de Guillermo = idéntica al sandbox (3633 exacto). Manifest: 2 scripts a PIPELINE_SCRIPTS + 2 CSV a OUTPUTS (`generar_manifiesto.py` v1.7, 8→10 canónicos).
**Corrección de framing (H154) — DOS ejes de partes, no uno:** los insumos cuantificados arriba (`c/` 59% en `case_name_cuerpo`, índice editorial) describen el **Eje A actor/demandado**, que es la relación procesal de origen. El insumo que M25 necesita es el **Eje B recurrente/recurrido (= petitioner SCDB): quién apeló a la Corte**, y eso sale SOLO del epílogo editorial (marcador `Recurso … interpuesto por X` + `Traslado contestado por Y`), NO de la carátula. El actor/demandado del índice no define quién recurrió. Capa 1 = Eje B (hecha); el Eje A (cruce con el índice) queda como capa futura.
**Frentes pendientes (H154):** **frente 2 — formato viejo** (`Nombre del actor:`/`Parte demandada:`, ~365 de los 712 `epilogo_sin_marcador`: listan partes pero NO marcan quién recurrió → 2ª gramática, la de mayor ganancia de cobertura); **frente 3 — arrastre de zona** (~103: la zona `epilogo` agarró cuerpo; tocaría el parser → re-golden caro, evaluar ROI; cf. B117). Residual restante: `Profesionales:` 137, tribunal/otros 107. La verificación del gold de M25 (las 7 inversiones de rol) queda FUERA de M29 por decisión (no acumular incertidumbres; 7/7 dan recurrente legible, valida el Eje B).
**Marcador de casos contrapuestos:** `multi_recurso=si` ya marca el universo donde el recurrente-de-referencia es insuficiente → NO duplicar ese marcado en `parte_ganadora`.
**Referencias cruzadas:** M25 (le da el insumo de rol), HM-01 / SCDB, `csjn_editorial_indice_partes.csv` (Eje A, futuro), zona `epilogo` / B117 (frente 3), patrón `derivar_materia`. H153/H154. Sin ID histórico.

### M30 — Centralizar resolución de paths + orquestador de re-corrida downstream

**Componente:** infra del pipeline (`scripts/pipeline/`).
**Origen / fuente del diagnóstico:** H153 (al re-derivar `recursos.csv` por Ruta 1: cada script resuelve su raíz por su cuenta).
**Causa raíz:** paths hardcodeados y dispersos — `derivar_recursos` usa `HERE.parents[1]` + `ROOT/output/parser/`; `extraer_caso` ancla por marcador `scripts/pipeline/parser.py` + `ROOT/corpus`; el subsistema κ usa `parents[1]/golds/`. No hay fuente única de paths, y la profundidad de carpeta ya rompió builds antes (path fixes `parents[2]→[1]` en H152 por el move del κ).
**Diagnóstico / evidencia:** dispersión observada al tocar el deriver en H153 + los fixes de profundidad de H152.
**Estado de verificación:** `confirmado_caso_testigo` (los fixes de H152 + la dispersión observada H153).
**Validador propuesto:** módulo único de paths (`paths.py` / config) importado por todos los scripts de `scripts/pipeline/`; encima, un orquestador de re-corrida que propague el downstream del nodo que cambió (corpus→todo · parser→parser+derivers · deriver→solo ese deriver · detección→desde ahí abajo). Destraba además unificar los dirs `scripts/parser` vs `scripts/pipeline` + `output/`.
**Estado del fix:** no diseñado.
**Referencias cruzadas:** **M24** (runner de *validación*; esto es de *ejecución* + paths — complementarios, NO duplicados), H152 (path fixes de profundidad), `derivar_recursos` / `extraer_caso` / κ. H153. Sin ID histórico.

### M31 — Zonificación de epílogo (y de zonas en general): delimitación heurística floja = deuda de escalabilidad/modularidad

**Componente:** parser (zonificador, `zonificar_bloque()` → `csjn_casos_zonas.csv`).
**Origen / fuente del diagnóstico:** H155 (al consolidar la capa de partes; cuantificación del over-capture de B117).
**Causa raíz:** la asignación de zonas es heurística por bloque y no tiene control de calidad de frontera. La zona `epilogo` sobre-captura cuerpo/considerando (B117): **478 zonas con wc>200, 205 >1000, max 19788**, vs mediana 58 de un epílogo limpio. No es el caso testigo aislado `329_p595` — es **transversal** (~7-20% por tomo, sin corte de época). El zonificador no distingue el pie editorial real del cuerpo arrastrado.
**Impacto (por qué es deuda aunque hoy no muerda):** la capa de partes es ROBUSTA al desprolijo porque `RE_MARK_REC` ancla al footer (line-anchored + case-sensitive) — H155 verificó **0 corrupción de derivación**. PERO esa robustez es del *consumidor*, no de la *fuente*: cualquier capa futura que consuma el contenido de `epilogo_text`, los `wc_*` por zona, o las fronteras de zona, **hereda el desprolijo y tiene que defenderse sola**. A medida que el repo madura y más derivers cuelgan de `zonas`, una delimitación floja acopla a todos los consumidores a su ruido = costo de **escalabilidad y modularidad**. Es Escalable/Elegante (REE), no funcional-urgente.
**Estado de verificación:** `confirmado_cuantificado` (478 zonas, H155).
**Validador propuesto:** endurecer la frontera del zonificador (¿el epílogo arranca SOLO en el pie editorial — `Recurso … interpuesto por` / `Tribunal de origen` / `Nombre del …` / `Profesionales:` — y no en el cuerpo?); población de prueba = `wc>200`; A/B contra el golden. Antes de tocar el parser: muestrear los **189 de mérito-sin-zona** (B117) para acotar el recupero real.
**Estado del fix:** no diseñado. Toca el zonificador (parser) → re-golden. ROI funcional bajo (no recupera Eje B, no corrompe nada hoy); se justifica por base limpia + escalabilidad/modularidad = decisión de valor, no de ROI inmediato.
**Referencias cruzadas:** **B117** (síntoma puntual cuantificado), **M09** (detección sin constraint de zona — deuda arquitectónica previa), **M10** (zonificar mayoría vs votos), familia **B009** (merge come-varios-casos), H155. Sin ID histórico.

### M32 — Clasificador de TIPO SCDB (petitioner/respondent): del nombre a la categoría de Spaeth

**Componente:** capa-deriver nueva (consume `csjn_casos_partes.csv` de M29).
**Origen / fuente del diagnóstico:** H156 (al precisar el crosswalk SCDB con Guillermo: `partyWinning` ≠ `petitioner`/`respondent`; M29 da el NOMBRE, falta el TIPO).
**Motivación / fundamento (SCDB):** SCDB codifica `petitioner`/`respondent` como **TIPO categórico** (~200-300 clases: Estado federal / Estado provincial / empresa / persona física / imputado / agencia de gobierno / asociación / sindicato …), NO como nombre libre. Es lo que habilita las cuentas comparadas ("¿cuántas veces gana el Estado vs un particular?"). M29 da nombre + `recurrente_rol` (procesal: actora/demandada/penal); el TIPO es una clasificación distinta (por naturaleza de la parte) que **no está en el texto** — es conocimiento del mundo, requiere clasificación inteligente, NO regex. Llena el gap "petitioner/respondent prospectivo" del CODEBOOK §10 (crosswalk SCDB).
**Complicaciones:** (a) misma entidad con mil grafías (AFIP / A.F.I.P. / Administración Federal de Ingresos Públicos / DGI); (b) ambigüedad real (un "Estado Nacional – Ministerio de X" ¿es Estado federal o agencia federal?); (c) cola larga (empresas y personas que ningún diccionario lista → clasificar por rasgos: sufijo SA/SRL → empresa, patrón nombre-apellido → persona física, "Colegio de" → entidad profesional).
**Estado de verificación:** `confirmado_caso_testigo` (la estructura SCDB partyWinning ⊕ petitioner/respondent es firme; la lista EXACTA de códigos de Spaeth hay que verificarla contra su codebook antes de fijar el crosswalk §10).
**Validador propuesto / opciones de arquitectura:** (1) **diccionario + reglas** (gazetteer de entes públicos + heurísticas de sufijo/patrón) → determinístico, auditable, reproducible para Dataverse, pero techo bajo en la cola larga; (2) **LLM como clasificador** → cubre la cola larga, pero ROMPE el determinismo REE/Dataverse (reproducibilidad bit-a-bit) — exigiría congelar salidas, versionar prompts, validar con κ; (3) **híbrido (RECOMENDADO)** → diccionario+reglas resuelven el 80% obvio y barato (Estado/provincias/AFIP), solo el residuo va a modelo con revisión humana sobre la fracción dudosa; salidas congeladas + κ.
**Estado del fix:** no diseñado. **Capa NUEVA grande, NO un fix** — va DESPUÉS de M25. Antes de codear: confirmar la taxonomía de códigos de Spaeth para el crosswalk.
**Referencias cruzadas:** **M29** (le da el insumo nombre+rol), **M25** (partyWinning, la otra mitad SCDB), CODEBOOK §10 (gap petitioner/respondent prospectivo), HM-01 / crosswalk SCDB. H156. Sin ID histórico.

### M33 — Derivación de rol por carátula (epílogo con nombre, sin rol)

**Componente:** capa-deriver (`derivar_partes.py`, nuevo paso post-epílogo).
**Origen / fuente del diagnóstico:** H162 (al medir por qué los `(sin rol)` son 2138, a raíz de la pregunta de Guillermo).
**Causa raíz:** el rol procesal del recurrente suele estar en la carátula del cuerpo ("Recurso … deducido por la actora en la causa X c/ Y"), no en el epílogo editorial. El PASO 4 (carátula) solo dispara cuando el epílogo no trae marcador; cuando el nombre vino del epílogo SIN rol, nunca volvemos a la carátula a leer el rol aunque esté disponible.
**Diagnóstico / evidencia:** de los 2138 `(sin rol)` → **531 con rol leíble directo de la carátula** (`RE_MARK_CARATULA`+`_rol` dan "la actora"/"la demandada"; muestra: `Ferrocarriles Metropolitanos S.A.`+"la demandada", `Y.P.F. S.A.`+"la actora"); 573 con marcador de carátula pero sin rol legible ("X c/ Y" directo); 1034 sin marcador de recurso en la carátula. Los `(sin rol)` son ~98,5% estructurales (el epílogo no declara rol), no parse roto; solo 31 tienen palabra-de-rol en el clause del epílogo sin capturar (varios roles NO modelados: ejecutado, Defensor del Pueblo, Fiscalía de Estado; recuperables reales `337_p307` "actor en autos", `337_p675` "apoderada de la actora").
**Estado de verificación:** `confirmado_cuantificado` (H162).
**Validador propuesto:** nuevo paso que, cuando hay nombre del epílogo sin rol, lea el rol de la carátula reusando `RE_MARK_CARATULA`+`_rol`+`_nombre_desde_causa`. **Guard de consistencia OBLIGATORIO:** asignar el rol SOLO si el recurrente nombrado por el epílogo cae del lado del `c/` que ese rol elige; si discrepa → dejar `(sin rol)`. Consistencia medida: ~415 caen del lado correcto, **61 discrepan** (multi-parte / terceros / el nombre es el letrado), 31 ambiguos. Etiquetar `partes_fuente` propio (p.ej. `epilogo:nombre+caratula:rol`) para auditar. Impacto estimado: +~415 roles (rol-cobertura de recurrente_ok ~44%→~55%). Validar el guard contra los 61 antes de sellar.
**Estado del fix:** diseñado, no aplicado.
**Referencias cruzadas:** **M29** (la capa de partes que da el nombre), `derivar_de_caratula`/PASO 4 (la maquinaria que se reusa), **M25**/**M32** (consumen el rol), fila "rol por carátula" del Tablero. H162. Sin ID histórico.

### M34 — Re-clasificar rol-only → `rol_sin_nombre` (corregir inflación de `recurrente_ok`)

**Componente:** capa-deriver (`derivar_partes.py`: `derivar_de_epilogo` + `_registrar`).
**Origen / fuente del diagnóstico:** H162 (efecto secundario medido del handler de inversión, bump 1).
**Causa raíz:** ~80 casos "la actora, representada por la Dra. X" (la parte no se nombra en el epílogo, solo el letrado) cuentan hoy como `recurrente_ok` con nombre "la actora" — un rol restado como si fuera nombre. El handler de inversión (v0.14) ya los detecta y los vacía, pero, por la restricción de bump 1 (solo recuperación de nombre, 0 cambio de métrica), quedan como recurrente_ok con nombre vacío en vez de `rol_sin_nombre`.
**Diagnóstico / evidencia:** mérito-con-nombre honesto ≈ **90,7% (2604/2870)** vs 92,8% reportado (coincide con la cota estricta "nombre-o-rol-real = 90,7%" ya anotada en el Tablero, fila "frente consolidado"). Re-clasificar mueve `recurrente_ok` ~−80 y mérito ~−57. ~78 PURO ROL + 2 (apoderado/representación) — todos genuinamente sin nombre de parte recuperable del epílogo (el nombre vendría de la carátula/Eje A).
**Estado de verificación:** `confirmado_cuantificado` (H162).
**Validador propuesto:** en `derivar_de_epilogo`, si `parse_parte`→("", rol) con rol presente, setear `partes_fuente="epilogo:rol_sin_nombre"`; en `_registrar`, contar `partes_fuente` que termine en "rol_sin_nombre" dentro del bucket `caratula_rol_sin_nombre` (rol_sin_nombre). Diff esperado: recurrente_ok 3845→~3765, mérito 2664→~2607.
**Estado del fix:** diseñado, no aplicado. **Mueve un canónico de cobertura → requiere OK explícito de Guillermo.**
**Referencias cruzadas:** bump 1 / handler de inversión (lo destapó), **M33** (complementario: M34 limpia el accounting del nombre-ausente, M33 recupera el rol), CODEBOOK (la cifra de cobertura publicada). H162. Sin ID histórico.

### M35 — `csjn_editorial_indice_partes.csv`: output FÓSIL — demover

**Componente:** output canónico (`output/parser/`) / manifiesto de procedencia (`generar_manifiesto.py`) / atribución a `parser_editorial.py`.
**Origen / fuente del diagnóstico:** H166 (crosscheck del índice de partes vs corpus + triple verificación del productor: fuente de `parser_editorial`, grep recursivo, tabla del manifiesto).
**Causa raíz:** el CSV **no lo emite ningún script de la cadena**. Productor real = `scripts/auditoria/H061/crosscheck_indice_partes.py` (one-shot), que importa `parsear_indice_partes` — función **ELIMINADA en H061** (verificada ausente en `parser_editorial.py` y `construir_catalogo.py`). Por tanto el output es un **fósil que no se regenera**. El manifiesto (**línea 115**) lo atribuye INCORRECTAMENTE a `parser_editorial.py`, que es librería de `parser.py` (expone `clasificar_editorial`, NO emite CSV — verificado en `MAPA.md`).
**Diagnóstico / evidencia (medido en disco H166, RE-REPRODUCIDO H167):** vs `catalogo.csv` (extracción robusta del MISMO índice oficial) — **MISS = 0**; **478 EXTRA**, los 478 EN `catalogo.csv`, **478/478 con `nombres_indice` poblado**. **Reproducción H167 sobre el corpus actual (5890), no testimonio (regla #27/#28):** el censo casos-vs-fósil (`caracterizar_extra_indice.py`, escape-hatch argv) da EXTRA=478 (120 esperado + **358 SOSPECHOSOS** = mérito que el índice debería listar); el crosscheck nuevo `caracterizar_extra_vs_catalogo.py` (reúsa `pag()`/`NO_MERITO`/`esperado` del censo, anclado por `.git`) confirma **478/478 EXTRA y 358/358 SOSPECHOSOS en catalogo con `nombres_indice` poblado, 0 fuera** → `[VERDE]`: catalogo cubre lo del fósil. El fósil es redundante E INCOMPLETO frente al catálogo (los 358 son drops del fósil que el catálogo sí lista con partes). NO es FP del parser.
**Estado de verificación:** `confirmado_cuantificado` (reproducido en disco H167).
**Validador APLICADO (H167):** ① `generar_manifiesto.py` v1.7→v1.8 (sacada la tupla del fósil de `OUTPUTS`, **10→9 outputs**); `--verify [CLEAN] 64 artefactos` (46 corpus + 5 vocab + 4 inputs + 9 outputs); `check_regresion [CLEAN]` 5890 (no dependía del fósil — L13 era comentario, no contrato). ② fósil **relocado y trackeado** en `archivo/fosiles/csjn_editorial_indice_partes.csv` (ya estaba ahí de antes, `LastWriteTime` 23/5; el `git mv` falló porque era **untracked**, no por gitignore). ③ redundancia reproducida (ver evidencia). Caracterización conservada en `scripts/auditoria/H166/caracterizar_extra_indice.py`; crosscheck en `scripts/auditoria/H167/caracterizar_extra_vs_catalogo.py` (one-shot, `auditoria/` gitignored → no commiteado, Opción A).
**Estado del fix:** **① ② ③ APLICADOS y probados H167. ④ Dataverse PENDIENTE → ver entrada M35-④** (de-publicar a mano + subir manifest v1.8; el publicado quedó atrás, 10 outputs / manifest viejo). Deuda menor destapada: **D-anchor** — el anclaje `REPO = Path(__file__).resolve().parent` de `caracterizar_extra_indice.py` (y probable de `H061/crosscheck_indice_partes.py`) ancla a la carpeta del script, no a la raíz (de ahí el FATAL); el crosscheck nuevo ya usa el patrón `.git`-anclado.
**Referencias cruzadas:** M14 (manifiesto de procedencia — la atribución incorrecta vive ahí), M29/M32 (capa de partes, output adyacente), `MAPA.md` (grafo que destapó el huérfano). H061 (origen del productor muerto), H166. Sin ID histórico.

### M36 — Frontera del harness de regresión: los derivers no tienen golden

**Componente:** `scripts/tests/check_regresion.py` (harness de regresión del parser).
**Origen / fuente del diagnóstico:** H166 (instalación de los gates de cierre; lectura del golden existente).
**Causa raíz:** el golden de `check_regresion.py` cubre SOLO los **5 CSV que emite `parser.py`** (`csjn_casos`, `_textos`, `_votos`, `_zonas`, `_editorial`). Los **5 outputs de los derivers corren SIN red**: `csjn_casos_partes` (M29/M32), `csjn_casos_materia`, `csjn_casos_recursos`, `csjn_casos_epilogo`, `csjn_editorial_indice_partes` (este último, fósil → M35). Un cambio en cualquier deriver no lo agarra ninguna regresión congelada — la disciplina de byte-identidad que protege al parser no existe para la capa de derivación.
**Diagnóstico / evidencia:** verificado leyendo el script en H166 — `--make-golden` y la comparación operan sobre los 5 del parser; ningún deriver está en el set. (Cada bump de `derivar_partes` se validó a mano corriendo el script real end-to-end — verificación ad-hoc por sesión, no harness.)
**Estado de verificación:** `confirmado_cuantificado` (cobertura 5/10 outputs).
**Validador propuesto:** extender el golden a los outputs de derivers (requiere fijar la invocación canónica de cada deriver + sus inputs, ya mapeada en `MAPA.md`). Decisión: ¿golden por deriver, o un solo runner **M24** que los englobe?
**Estado del fix:** diseñado (alcance), no aplicado.
**Referencias cruzadas:** **M24** (runner general — superconjunto natural), M14 (manifiesto: sella los 10 outputs por hash pero NO compara contenido), `MAPA.md`. H166. Sin ID histórico.

### M37 — BITACORA atrasada respecto del código (H164–H165 sin documentar)

**Componente:** documentación de proceso (`BITACORA.md`).
**Origen / fuente del diagnóstico:** H166 (al fijar el número de sesión para el cierre).
**Causa raíz:** la BITACORA llega documentada hasta **H163**, pero los changelog de los scripts ya referencian **H165** (`derivar_partes` v0.15→v0.17, B136). Al menos dos sesiones (H164, H165) tocaron código pero no se escribieron en BITACORA — el relato quedó detrás del disco. Esto rompe la deducción del número de sesión por conteo desde la BITACORA (H166 se fijó por confirmación manual, no por inferencia).
**Diagnóstico / evidencia:** `Select-String -Path scripts\pipeline\*.py -Pattern 'H1[0-9][0-9]'` → máx H165; último `## H` en BITACORA → H163. Gap = H164, H165.
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto:** backfill de H164–H165 en BITACORA reconstruyendo desde los changelog de `derivar_partes` (conservan el detalle de cada bump) + el encabezado "Última actualización" de este archivo. Refuerza la regla de conducta: la BITACORA es **testimonio** que puede quedar viejo.
**Estado del fix:** no diseñado (backfill pendiente).
**Referencias cruzadas:** encabezado de este archivo (registró H165 vía "Última actualización", ahora reemplazado por H166), changelog de `derivar_partes`. H166. Sin ID histórico.

### M38 — Disparo de los gates de cierre: pre-commit vs paso del cierre

**Componente:** `scripts/tests/` (los gates de H166) + protocolo `cierre-sesion-corpus`.
**Origen / fuente del diagnóstico:** H166 (instalación de los gates).
**Causa raíz:** los gates (`check_allowlist_paths`, `check_append_only_docs`, `check_version_bump`, `gate_manifiesto`, + `check_regresion` ya existente, + golden) están instalados y probados en ambos sentidos, pero **standalone** — hoy se corren a mano. Falta decidir el disparo: (a) framework `pre-commit` (hook automático por commit) vs (b) un paso explícito del protocolo `cierre-sesion-corpus`. Trade-off: pre-commit es automático pero agrega dependencia + fricción por commit; el paso del cierre es explícito pero depende de no saltearlo.
**Estado de verificación:** `confirmado_cuantificado` (gates probados; mecanismo de disparo abierto).
**Validador propuesto:** decidir (a) vs (b). Si (a): `.pre-commit-config.yaml` con los gates como hooks locales. Si (b): agregar el bloque de comandos al skill `cierre-sesion-corpus` como Gate de salida.
**Estado del fix:** no diseñado (decisión pendiente de Guillermo).
**Referencias cruzadas:** **M24** (runner general — los gates serían sus clientes), skill `cierre-sesion-corpus`. H166. Sin ID histórico.

### M39 — Eje de mérito bicapa divergente: `is_merit` ⟺ `es_revision_fondo` (234 mismatches, taxonomía M1-M5 cerrada) — CERRADA H178 (paso 3 ejecutado; divergencia 0; D1 retirado)

**Componente:** parser (`is_merit_decision` vía outcome) + deriver (`es_revision_fondo` vía disposicion+guards) — el eje vive en DOS capas con derivaciones distintas; B136 las unificó SOLO en la originaria (vía `es_de_fondo`).
**Origen / fuente del diagnóstico:** H170 (auditoría REE, ítem D1; `scripts/diagnostico/H170/consistencia_merito.py` v0.1→v0.3 — v0.2+ importan `norm`/`DISP`/`RE_RECHAZA_REC` del clasificador real, no regex paralelas).
**Diagnóstico / evidencia:** `confirmado_cuantificado` — **234/5697 fallos (4,1%), 0 en las 546 originarias, 0 residuales**. Desglose FINAL (v0.3 en disco + **19 testigos leídos contra el `.md`**):
- **M1_ORIGINARIA_PERDIDA (15):** originarias no detectadas por la regex angosta → error de AMBAS capas → **B135** (sub-causa a; recuperables por ensanche, son PISO por la sub-causa b).
- **M2A_SOBREINCLUSION (98):** hace_lugar/procedente sobre acto procesal/vía (citaciones, quejas por ordinario, suspensiones) — **el gate tiene razón**, error de `is_merit`. Testigos: 329_p222 (OSDOP, citación de terceros), 329_p926 (Vaggi, queja por mal denegado), 329_p623 (Casas, «sin pronunciamiento sobre el fondo» textual).
- **M2B_OUTCOME_FONDO (18):** outcome de fondo × gate=no. Adjudicado MIXTO sobre 4 testigos: 2 FN reales del gate por objeto material (332_p731, 340_p411 → **B139a**) y 2 aciertos del gate con outcome equivocado (330_p251 Carrillo dejar-sin-efecto-la-EXCUSACIÓN; 333_p1152 Rivera nulidad por vicio pupilar). IDs completos: 330_p251, 330_p1950, 330_p4396, 332_p731, 332_p2797, 333_p1152, 337_p1024, 338_p234, 338_p284, 339_p852, 340_p411, 341_p1924, 344_p2513, 345_p722, 347_p729, 348_p83, 348_p1714, 349_p207 — los 14 no leídos exigen adjudicación caso a caso antes de cualquier fix masivo.
- **M2C_CAND_ORIGINARIA (13):** hace_lugar × no_revision_demanda. 3/3 testigos = fondo real: 337_p234 y 344_p3476 **originarias confirmadas** (señal fuera de `considerando_text` → B135) — con 329_p3403 (Ferrari de Grand) y 348_p473 (H161) suman **4 originarias confirmadas del bucket**; 331_p100 (Tucumán c/ Fisco) NO es originaria sino sentencia sustitutiva art. 16 in fine ley 48 (→ **B139b**). IDs restantes sin leer: 331_p718, 332_p2559, 333_p1279, 337_p548, 337_p1174, 338_p113, 344_p277, 348_p895.
- **M3_MIXTO (44):** dispositivo mixto — `outcome` ancla el PRIMER verbo (de gate), `disposicion()` lee el de fondo con search global. **El gate tiene razón.** Testigo: 329_p1767 (Mathieu).
- **M4_ASIDE_B129 (24):** coincide EXACTO con los «24 asides conservados» de B129/H145 — **validación cruzada independiente**. El gate tiene razón. Testigo: 334_p1272 (Breitfeld).
- **M4_ABSTRACTO_OTRO (3):** adjudicado 3/3 — 337_p850 (Malossi) fondo real, el aside es «inoficioso…**recursos de hecho**» (variante del patrón B129 del lado parser/outcome, el lookahead del deriver la cubre y el del parser no existe); 329_p5261 (ADC) y 343_p2098 (Paccagnini) = FP del gate → **B140**.
- **M5_RECHAZA_REC (19):** FP del gate por `RE_RECHAZA_REC` en denegatoria de acceso pura → **B138**.
**Impacto:** `is_merit` se denormaliza a votos (define el universo del audit B137), es denominador de la cobertura de partes (92,8% M29) y delimitó el golden M20. Hoy el corpus publica DOS respuestas a «¿decidió el fondo?» en 234 casos. Pesa sobre Dataverse (M35-④+B136): decidir si la publicación documenta la divergencia o espera la unificación.
**Fix (diseñado, NO implementado) — por mecanismo y EN ORDEN OBLIGATORIO:** (1) **B135** (ensanche + normalización de señal + señal compuesta) → M1 converge solo vía `es_de_fondo`; (2) **bugs del gate**: B138, B139, B140 → como guards, verbo lockeado intacto; (3) recién entonces **extender el patrón B136** (clasificador como fuente única; `is_merit` derivado, no paralelo) a todo el corpus → absorbe M2A/M3/M4 por construcción. **El orden inverso consagra los FP del gate como canon.** Cada paso: re-golden + re-derivar + re-κ.
**Actualización H171:** cardinalidad corpus-wide del paso 2 MEDIDA (`scripts/diagnostico/H171/cardinalidad_gate.py` v0.2, read-only, anclas contra D1 [OK]): B138=19 cerrado (0 invisibles) · B139a=59 brutos estratificados · B139b=13/178 (la vía derivada resuelve, restringida a no-originarias) · B140a=3 fuertes (1 FP confirmado ADC, 1 acierto 340_p1973 art. 16 in fine, 1 pendiente doctrinal 329_p5115) · B140b=10 cerrado (9 invisibles, fórmula única). Detalle y adjudicaciones en cada entrada. El orden del fix NO cambia.
**Constancia H172 — PASO 1 (B135) EJECUTADO.** El paso (1) del orden lockeado se implementó (B135 sub-causas a+b, parser v23.1) y se midió: divergencia **234→219**, los 14 M1-verdaderos convergieron vía `es_de_fondo` (B136), ripple bidireccional de is_merit 3003→3006. El orden de fix SIGUE lockeado — próximo es (2) guards del gate (B138/B139/B140), con la adjudicación de H172 ya hecha: B138 = 17 FP + 2 aciertos ordinarios (guard debe excluir via=ordinario + barrer por objeto), B140a cardinalidad real = 1 (ADC/329_p5261). B135(c) señal compuesta queda como refinamiento, NO bloquea el paso 2.

**Constancia H175 — PASO 2 SUSTANCIALMENTE EJECUTADO (B138 ✓ + B140b ✓ + B140a documentado).** B138 cerrado con guard lista-positiva (v1.12, 11 flips; la lectura de testigos REVIRTIÓ el diseño v1 pre-instalación — Minaglia 330_p3801 fondo real → B142) y B140b cerrado con ensanche de `RE_NULIDAD_CONCESION` (v1.13, 10 flips de verbo, ripple a admisibilidad adjudicado). Divergencia: 219→208 (B138: 17 convergen menos los residuales)→**216** (B140b: +9 invisibles EXPUESTOS = residuo lado parser [outcome=nulidad / is_merit=1, copia propia de la regex en parser L470 sin tocar], −1 Paccagnini). Los 9 expuestos son la señal honesta de que el instrumento ahora VE lo que antes coincidía-en-error; se absorben en el paso 3. Gold n300 intacto (clave byte-idéntica con v1.13). Restante del paso 2: **B139** (re-estratificar los 59 contra el corpus post-B141 antes de decidir guard o diferir) — luego paso 3.

**Constancia H176 — PASO 2 COMPLETADO (B139 re-estratificado, adjudicado y diferido-fundado; superficie originaria cerrada v1.14).** Los 59 brutos de B139a re-corridos post-B141/B138/B140b (mismo total, composición rotada 42/17); 17 lecturas adjudicadas caso a caso: 10 FN reales del gate (5 mecanismos, documentados-sin-guard — detalle en B139) + ~7 aciertos-del-gate con outcome equivocado del parser (1950, 4396, 1024, 852, 2513, 83, 1857) que son **insumo directo del paso 3**. Micro-unidad cableada: v1.14 (+«impugnación», gemelos San Juan) → is_merit 3008→**3010** · gate=si 2948→**2950** · **divergencia 216 SIN CAMBIO** (flip bicapa simétrico — el fix es tan invisible al instrumento como lo era el bug, tercera instancia documentada de la clase coincide-en-error junto a 334_p1047/B142 y los 16 de B143). Criterio de codebook nuevo (nulidad de sentencia vs. de actuaciones) destapa **B143** (16 FP latentes del gate, invisibles). Golden re-congelado (2+13 filas, solo is_merit), clave n300 byte-idéntica probada vía git, manifest [CLEAN] 64. **El orden lockeado avanza: próximo es el PASO 3** (is_merit derivado del clasificador como fuente única) — absorbe los 9 expuestos de B140b + los ~15 aciertos-del-gate/outcome-equivocado ya adjudicados (H172+H176).

**Constancia H178 — PASO 3 EJECUTADO Y CERRADO; M39 CERRADA; RETIRO FORMAL DE D1.** is_merit derivado del gate como fuente única (parser v24.0, opción (i)/patrón B136 extendido; MERIT_OUTCOMES retirado, GATEKEEP_OUTCOMES muerto removido). Flip-set = exactamente la divergencia (227 = 151+76, PoC bimodal A1-A5 [CLEAN] sandbox+disco); golden con totalidad demostrada (227 filas casos / 1078 votos exactas); derivers 0 ripple (hashes idénticos); clave n300 con 8 filas nuevas → candado byte-idéntico retirado CON D1, blind 0,930 describe el eje viejo, re-validación = M43; tipo_voto 6 flips reales (≤ cota 15+2). Costos aceptados (~22, con unidad sucesora): 9 FN-B139a · 4 resid-B138 (tomos completados: 330_p1205/330_p4891/331_p2621/348_p747) · 3 originarias B135(c) (329_p3403/344_p3476/348_p473, autorreparables) · 331_p100 (B139b) · 4 truncados M21 · ADC/329_p5261. **Límite de D1, para el registro:** el instrumento midió divergencia, no verdad — las clases coincide-en-error (B142; B143 pre-fix; v1.14/impugnación) le fueron invisibles por construcción; su detección exigió criterio de codebook + lectura, no diff. Trayectoria: 234→219→208→216→227→0. Sucesor de medición: M43 (re-κ ciego del eje unificado).

**Constancia H177 — B143 CERRADO ANTES del paso 3 (decisión de orden (a), la lógica del orden lockeado aplicada al propio gate).** Los 16 del alt «nulidad de todo lo actuado» leídos y adjudicados (15 FP + 330_p399 acierto-por-excepción); guard v1.15 en el gate, verbo intacto. La razón del orden se verificó en el dato: el paso 3 sin este cierre habría consagrado 14 coincide-en-error como canon **y fabricado 2 errores nuevos** (347_p327/348_p1152, hoy is_merit=0 correcto, habrían flipeado a 1). Divergencia 216→**227**: +13 coincide-en-error expuestos lado parser (outcome hace_lugar/nulidad sobre nulidades procesales — se suman a los 9 de B140b y a los ~15 de H172/H176 como residuo que el paso 3 absorbe), −2 que convergen. Gate=si 2950→**2935**. Solapamiento con gold n300 = 0; clave byte-idéntica; parser 0 ripple. **El paso 3 arranca H178 sobre gate limpio de FP conocidos** — pendientes de diseño ya identificados: dónde vive is_merit derivado (¿parser importa el gate, patrón B136 extendido, o migra al deriver?), destino de la copia parser L470, denormalización a votos (cascade B137/tipo_voto), golden con diff ~227 adjudicado POR CLASE, ¿build_m20 consume is_merit? (verificar, no asumir), retiro documentado del instrumento D1 (la divergencia pasa a 0 por construcción; B142/B143 quedan como el límite que el instrumento nunca vio), y corrección del docstring del parser («40 columnas» → 39 real).

**Constancia H174 — B141 CERRADO sobre el mismo módulo; el paso 2 SIGUE pendiente y lockeado.** El cierre de B141 tocó `clasificador_disposicion` (v1.11: guard in-limine en `es_de_fondo`) y el parser (v23.2) SIN tocar los guards del gate — próximo sigue siendo (2) B138/B139/B140b. Divergencia re-medida post-B141: **219 sin cambio** (329_p3894 y 341_p1148 convergen en `si` por ambas capas a la vez; 334_p1047 coincide-en-error en `no`/0 en ambas → clase nueva **B142**, invisible al instrumento de divergencia — límite documentado). is_merit 3006→3008.

**Constancia H173 — eyeball 329_p3894 EJECUTADO → regresión detectada (B141).** El pendiente H172 se adjudicó contra el `.md` real: 329_p3894 es FONDO (ver B141) → el flip is_merit 1→0 del ripple B135 fue una regresión, no una corrección. Costo real de B135 en mérito genuino perdido = **2** (347_p2146 FP-F5 documentado + 329_p3894 vía B141). La divergencia 219 y el orden lockeado NO cambian; B141 se encola con los bugs del detector compartido (afecta AMBAS capas por construcción, cf. B136: mismo `es_de_fondo` en parser y deriver).

**Referencias cruzadas:** B135, B136, B137, B138, B139, B140, B129, B131, M19, M20, M26. H170, H171. Sin ID histórico.

### M40 — Backlog de la auditoría REE H170: divergencias, robustez y elegancia del pipeline (D2-D6 / R2-R5 / E1-E2)

**Componente:** transversal (`scripts/pipeline/` completo).
**Origen / fuente del diagnóstico:** H170 (ejes 2+3 de la auditoría, informe completo en BITACORA H170). D1 se ejecutó (→ M39); R1 quedó absorbido en B135. El resto, priorizado:
- **D2:** `RE_DISP_INOFICIOSO` DIVERGIDO — parser L498 SIN el lookahead B129, clasificador CON; hoy acoplado-por-suerte vía el guard disposicion∉fondo. Testigo colateral H170: 337_p850 (variante «recursos de hecho» que ningún lookahead cubre del lado parser).
- **D3:** `_FONDO` en 4 copias, 1 divergente (`derivar_recursos.main` DISPVALS sin `grant_remand_implicito`, L131) → exportar desde `clasificador_disposicion`, una fuente.
- **D4:** familia 280/ac4 duplicada parser L277-318 ↔ `clasificador_causa` → dedup ANTES de la recalibración post-B010 (eje 5 de la auditoría, nunca ejecutado).
- **D5:** asimetría de normalización intra-deriver — `causa` usa `_prep` (sin banner mask), disposicion/via/admision usan `norm()` (con banner) → un 280 partido por running-head cae a `SIN_CAUSAL`. **RE-JERARQUIZADO H170:** el guionado+banner también parte la señal de originaria (B135 sub-causa b, verificado 337_p234) → D5 es condición previa del paso 1 de M39, no solo consistencia.
- **D6:** doble gramática del pie editorial (`extraer_epilogos` RE_PIE_* vs `derivar_partes` RE_MARK_*) sin test de contrato → conecta M36/M24.
- **R2:** fallback D silencioso de `clasificar_tipo_voto` L1663 → es el audit B137 (instrumentar rama).
- **R3:** writers upstream SIN `lineterminator="\n"` (cruzar L377/385/409, detectar_paginas L617-676, construir_catalogo L526/535) → CRLF, misma clase que el bug que H111 fixeó downstream; produce `--verify FAIL` espurio en re-corridas.
- **R4:** `derivar_recursos` accede columnas a pelo (is_originaria, queja_resultado, outcome, dictamen_presente) sin REQUIRED check (extraer_epilogos/derivar_partes SÍ validan).
- **R5:** merge de `derivar_recursos` L78 sin assert de cardinalidad.
- **E1:** changelogs inline monstruo (~9k chars en `__version__` de parser.py y derivar_partes.py) → mover a CHANGELOG, dejar entrada vigente.
- **E2:** fuente de `cruzar_catalogo_y_mapa.py` en CRLF.
**Estado de verificación:** `confirmado_caso_testigo` (cada ítem con línea citada en el informe de BITACORA H170; ninguno cuantificado corpus-wide salvo lo absorbido por M39/B135).
**Estado del fix:** no diseñado; triage por ROI pendiente. D5 sube de prioridad por M39.
**Referencias cruzadas:** M39, B135, B137, B129, M36, M24, post-B010, H111. H170. Sin ID histórico.

### M41 — Deriva del schema de directorios: salidas de diagnóstico fuera del árbol canónico

**Componente:** estructura de directorios del repo + gate `check_allowlist_paths` (H166) + skills apertura/cierre-sesion-corpus.
**Origen / fuente del diagnóstico:** H172 (Guillermo, al cerrar la sesión — «cuando extrajimos casos no estuvimos respetando el schema»).
**Causa raíz:** las extracciones de diagnóstico (`extraer_caso.py --out …`) se vienen escribiendo en `diagnostico/_extraidos/HXX/` **en la raíz del repo** — una carpeta que NO pertenece al schema. El precedente lo fijó H171 y H172 lo siguió sin cuestionarlo (deriva por imitación de sesión previa). Los SCRIPTS de diagnóstico están bien ubicados (`scripts/diagnostico/HXX/`); son las SALIDAS las que quedaron fuera. Existió una carpeta histórica `outputs/diagnostico/HXX` que también quedó en desuso. La regla de directorios (documentada, «no crear archivos fuera del schema sin preguntar») no la verifica ningún gate → se erosiona en la práctica: H171 y H172 son la prueba.
**Diagnóstico / evidencia:** `confirmado_caso_testigo` — `diagnostico/_extraidos/H171/` (10 archivos) y `diagnostico/_extraidos/H172/` (15: extraídos + `b135_flips*.csv`) estaban en la raíz (medido H172 antes de la eliminación). `check_allowlist_paths` (gate H166) no incluye la raíz `\diagnostico\` en su lista de rechazo. Descubierto además: existe `archivo/exploratorios/diagnostico/` (fósiles) y `scripts/diagnostico/_extraidos/{H094,H095}/` (forma legada del agrupador) — el árbol tenía TRES `diagnostico/` distintos, fuente de la ambigüedad que causó la deriva.
**Validador propuesto / decisión pendiente de Guillermo:** (1) **destino canónico** de las salidas de diagnóstico — propuesta: `output/diagnostico/HXX/` (consistente con el árbol `output/`), manteniendo scripts en `scripts/diagnostico/HXX/`; confirmar o elegir otro. (2) **enforcement estructural**: agregar la raíz `\diagnostico\` a lo que `check_allowlist_paths` rechaza + una línea en los skills apertura/cierre-sesion-corpus (la regla que no verifica un gate se erosiona).
**Estado del fix:** **parcialmente EJECUTADO H172 con incidente de pérdida.** La carpeta fuera-de-schema `diagnostico/` (raíz) fue eliminada — objetivo cumplido. PERO: los extraídos de H171/H172 (`.md` + `b135_flips*.csv`) **NUNCA estuvieron trackeados en git** (`git ls-files diagnostico/` vacío — el diagnóstico no se versiona), y un `git mv` que falló con «source directory is empty» fue seguido de `Remove-Item diagnostico -Recurse -Force`, que **borró los archivos físicos sin papelera** (Remove-Item no usa recycle bin). **Pérdida sin consecuencia material:** los extraídos son 100% regenerables (`extraer_caso.py` sobre el corpus intacto) y toda la adjudicación analítica ya estaba destilada en DEUDA/BITACORA/CHANGELOG (clases F1-F6, IDs, veredictos por caso). No se regeneraron (no aportan sobre lo documentado). **REGLA NUEVA reforzada por el incidente:** (i) todo lo de una sesión de diagnóstico vive en `scripts/diagnostico/HXX/` (script + extraídos + CSV juntos — regla confirmada H172; el `_extraidos/` agrupador de H094/H095 queda como forma legada, no se replica); (ii) **NUNCA `Remove-Item -Recurse -Force` sobre una carpeta sin correr `git status` antes** — los archivos no-trackeados no tienen red; si hay algo que conservar, trackearlo o moverlo primero. **Pendiente H173:** wiring del enforcement (agregar raíz `\diagnostico\` a `check_allowlist_paths`; línea en skills apertura/cierre); consolidar `_extraidos/H094`+`H095` a `scripts/diagnostico/H094|H095/` (limpieza diferida, no urgente).
**Constancia H173 — WIRING EJECUTADO (gate v1.2).** El diagnóstico original era impreciso en el mecanismo: `diagnostico/` de raíz YA era rechazable (allowlist, no está en `TOP_DIRS_OK`); el gate no lo VEÍA. Dos capas de ceguera: (1) v1.0 solo miraba trackeados/staged → v1.1 sumó untracked no-ignorados (`git ls-files --others --exclude-standard`) en ambos modos; (2) el PoC en disco siguió [CLEAN] → causa real: el `.gitignore` oculta la zona a propósito (L42 `scripts/diagnostico/*` + `!README.md`, L50/53 `/diagnostico/` duplicada) — **política deliberada del repo público: el scratch de diagnóstico no se publica** (confirmado por Guillermo; `git ls-files scripts/diagnostico` = solo H109 + README). v1.2 resuelve sin violar la política: `_fs_toplevel()` audita el **primer nivel del working tree en disco** (raíz real vía `git rev-parse --show-toplevel`), esté trackeado/untracked/**ignorado**, marcado «(en disco, ignorado o no)»; deliberadamente NO camina el árbol → el scratch en `scripts/diagnostico/HXX/` sigue legítimo, ignorado y sin flagear. Validación EN DISCO: fixture `diagnostico/PoC/test.md` → [FAIL] en `--all` y staged; borrado → desaparece del reporte. **Efecto colateral valioso: el gate destapó 4 residentes fuera de schema antes invisibles.** Triage: `.env` → `ROOT_FILES_OK` [SECRETS]; `.tmp.driveupload/` → `TOP_DIRS_OK` [SYNC — transitoria de Google Drive for Desktop; nota: el repo vive en carpeta sincronizada, relevante para el incidente Remove-Item de esta misma entrada]; `muestra_zona_epilogo.csv` (scratch H155, cf. comentario `.gitignore` L55) → BORRADO (regenerable); `docs/` (PIPELINE.md 126kB pre-deprecación + analisis_forense 254kB + GRAMATICA_DEL_FALLO + changelog_parser + figuras H025) → [COMPLETAR: resolución — destino natural `archivo/docs/`, verificar duplicación con `PIPELINE_v1.md` por hash antes de mover]. Pendientes menores: línea en skills apertura/cierre (texto propuesto entregado H173, pega Guillermo); dedup de `/diagnostico/` en `.gitignore` (L50/53) o eliminación de la regla (el gate ya la cubre); decisión sobre publicar `extraer_caso.py` (herramienta canónica citada en CODEBOOK, hoy ignorada por L42 — `!scripts/diagnostico/extraer_caso.py` si se quiere reproducibilidad externa).

**Referencias cruzadas:** `check_allowlist_paths` (H166), M38 (disparo de los gates de cierre — mismo problema de enforcement no automático), skills apertura/cierre-sesion-corpus, directriz de schema del system prompt del proyecto. H172, H173. Sin ID histórico.

### M42 — Orquestador del pipeline: script único que corra la cadena completa en orden — CERRADO H179

**Componente:** infra del pipeline.
**Origen / fuente del diagnóstico:** H174 (Guillermo, durante la re-corrida de B141: la invocación canónica del parser no vive en el repo — se reconstruyó desde argparse + chats — y la cadena de post-fix se corre a mano y en orden de memoria).
**Motivación:** la cadena canónica es parser → derivar_recursos → derivar_materia (si cambió considerando) → check_regresion (→ adjudicar → --make-golden) → generar_manifiesto + --verify, con precondición de orden (manifest sella el estado FINAL). Correrla a mano produjo en H174: invocación olvidada (una corrida en falso), manifest fuera de orden (benigno de casualidad: el golden vive fuera de los 64 artefactos sellados) y materia casi-stale (el considerando de 1047 cambió y materia capa 2 lo consume). Un orquestador con la invocación hardcodeada + orden + gates elimina la clase entera.
**Diseño (esbozo):** `correr_pipeline.py` con flags `--solo-derivers` / `--sin-parser` / `--consciente` (sin él, aborta si check_regresion FAIL); invocación canónica confirmada H174: `python scripts/pipeline/parser.py --localizados output/localizacion/fallos_localizados.csv --mapa output/mapa/mapa_paginas.csv --corpus corpus --output output/parser/csjn_casos.csv`. Considerar portar el fix infra de salida (stdout errors="replace", parser v23.2) a los demás scripts de la cadena si el orquestador loguea.
**Fix aplicado (H179):** `correr_pipeline.py` v1.0 en `scripts/pipeline/`. Alcance v1: parser → extraer_epilogos → derivar_partes → derivar_materia → derivar_recursos → check_regresion (gate) → manifest (verify → sello condicional, siempre último), con el DAG de MAPA.md como spec (el esbozo omitía epilogos/partes; MAPA manda). Invocaciones verbatim de las CLIs leídas en sesión (`--out` en recursos, `--input` en materia — la no-uniformidad se cablea, no se normaliza). Invariantes H178: (a) fail-fast total; (b) pre-flight de versiones (10 módulos) + pin `--esperar` + frescura post-etapa por mtime; (c) assert golden==producción (sha256, 5 CSV del parser) en toda corrida; (d) paths constantes desde REPO_ROOT, existencia verificada. Flags: `--plan` (dry-run), `--solo-derivers`, `--consciente` (tolera [FAIL], imprime el diff y FRENA con exit 3 sin tocar golden/manifest), `--regolden` (make-golden + assert + re-sello), `--esperar`, `--ignorar-corpus-drift`; `--sin-parser` del esbozo eliminado (redundante). NUEVO: gate de corpus-drift en pre-flight (corpus/*.md vs universo source_file, derivación de fuentes_corpus) — primer contacto con disco detectó los 4 .md de 335/336. Upstream fuera del ejecutable v1: **la v2 se diseña cuando haya tomos nuevos reales, leyendo las CLIs de las etapas 1–3** (unidad futura explícita, no omisión silenciosa). Provenance: NO entra a PIPELINE_SCRIPTS del manifest (no moldea datos; mismo estatus que check_regresion). Validación: `--plan` adjudicado contra MAPA.md; corrida real reprodujo el sello H178 en **0 cambios** (check [CLEAN] 5/5 · hashes golden==prod idénticos · manifest [CLEAN] 64 sin re-sello). Infra: PYTHONUTF8=1 al env de los hijos (clase charmap H174) + errors=replace propio.
**Estado del fix:** **CERRADO H179** (v2-upstream queda como unidad futura, condicionada a tomos nuevos).
**Referencias cruzadas:** M38 (enforcement de gates, mismo espíritu), M41 (schema), `check_regresion --make-golden`, `generar_manifiesto`, MAPA.md §«Cómo correr la cadena». H174, H179. Sin ID histórico.

### M43 — Paquete de re-validación pre-Dataverse: re-κ ciego n300 + κ de es_de_fondo

**Componente:** validación (scripts/validacion/) — condición de publicación de la próxima versión del dataset.
**Origen / fuente del diagnóstico:** H175 (Guillermo, durante el gold de B140b): los κ publicados (gate 0,946 · vía 0,941 · disposición 0,912 · parte 0,784) describen el pipeline al momento en que se midieron; con B136+B138+B140b encima (y el paso 3 de M39 en el horizonte) quedan descriptivamente stale respecto de lo que se publicaría. Además arrastra el κ ciego de `es_de_fondo` pendiente desde H169 (v1.10).
**Motivación:** la regresión build_m20 verifica que el blind NO SE ROMPIÓ (clave estable), pero no re-describe la confiabilidad del pipeline actual sobre una muestra ciega nueva. Antes de subir la versión 2 a Dataverse: ronda ciega n300 nueva (o re-uso del frame con re-codificación donde los ejes cambiaron) para los cinco ejes + κ de es_de_fondo sobre las originarias. Insumos ya en disco: `scripts/validacion/kappa_confiabilidad.py`, golds/, textos_n300.csv.
**Estado del fix:** no diseñado — **CALZADA COMO PRÓXIMA UNIDAD (H178)**: el paso 3 quedó ejecutado y el eje unificado (is_merit == gate, 2935) es lo que la ronda ciega debe re-describir. El candado byte-idéntico de la clave n300 se retiró con D1 (el paso 3 cambió 8 filas: parser_es_revision_fondo/_ctx_is_merit ahora SON el gate) → el blind 0,930 describe el eje viejo; M43 es la re-validación comprometida en el retiro. Sesión propia; atar al hito de publicación.
**Referencias cruzadas:** M19/M20 (gold y frame), B136 (κ es_de_fondo pendiente — el κ ciego validará la versión FINAL del detector, incluida v1.14/«impugnación» de H176), M39 paso 3 (conviene medir DESPUÉS del paso 3, con el eje bicapa unificado). H175. Sin ID histórico.
