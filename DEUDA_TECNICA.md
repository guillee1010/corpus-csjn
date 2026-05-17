# Deuda Técnica

Lista canónica de bugs del pipeline corpus-csjn y de la herramienta auditora
(`scripts/auditoria/auditar_fallo.py`). Una entrada por bug. El diagnóstico
técnico vivo de los bugs cuantificados contra el código vive en `PIPELINE.md`
(secciones §X.Y); las entradas de esta lista que tienen referencia §X.Y
apuntan allá para detalle. Las entradas sin §X.Y tienen el diagnóstico
completo acá.

**Última actualización:** 2026-05-16 (sesión H029: B009 causa raíz
confirmada — hojas complementarias + inicio de volumen; B046 Fase E
ejecutada, hipótesis de bloque vacío sin testigo empírico, 43 faltantes
explicados por B009; Fase F abierta — título como ancla).

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

- **Catálogo:** 5862 entradas (v15).
- **Universo procesable:** 19 tomos (329-349, exclusión metodológica de 335-336).
- **Output parser productivo:** 5819 casos en `output/parser/csjn_casos.csv`
  (Fix 1 aplicado, commit `2adda06`).
- **Cobertura sobre catálogo:** 5819 / 5862 = **99,3%**.
- **Fixes aplicados en sprint 2026-05-09:** §3.6.a `pg_fin+1`, §3.6.e Fase 1
  (39 casos `pagina_fin_no_en_mapa` reasignados), §4.6.j `RE_APERTURA` doble
  espacio (17/18 casos), Fix 1 (V1 como fuente primaria de `case_name_cuerpo`).
- **Pendiente verificación post-sprint:** identificación caso-a-caso de los
  32 oks que cambiaron de status post §3.6.a (eran XXI-v).

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
**Estado del fix:** no diseñado. Dirección: Fase F (título como ancla).
**Referencias cruzadas:** PIPELINE §3.6.c. XXI-d. BITACORA H001, H002,
H029. ID histórico: era **Bug A** del documento del 2/5.

### B010 — `RE_CONSIDERANDO` restrictivo + `.match()` con anclaje `^...$`

**Componente:** parser.
**Origen / fuente del diagnóstico:** PIPELINE §4.6.b. Rediagnóstico
2026-05-09 (continuación) y recalibración 2026-05-14 sobre CSV vivo
(BITACORA H019).
**Causa raíz:** `RE_CONSIDERANDO` (parser.py línea 121) anclado con `^...$`
e invocado con `.match()` solo detecta `Considerando:` como línea aislada.
Las variantes con prefijo (`Vistos los autos; Considerando:`) caen al
fallback `inicio_cons = 0` que arrastra todo el bloque desde la primera línea.
**Diagnóstico / evidencia:** cluster recontado 14/5: 320 casos con
`wc_cons ≥ 0.9 × wc` (vs 480 estimados originalmente). Apertura `fallo`: 229.
Apertura `sentencia`: 3. Sin apertura: 88. Vacíos: 1.672. **El cluster
§4.6.b puro (con apertura detectada) no cambió: 232 casos.**
Hallazgo lateral: existe `RE_CONSIDERANDO_NUMERADO_1` separado, usado en
detección de "estructura autónoma" en votos largos. El diseño del fix debe
considerar si unificar criterios con el numerado.
**Estado de verificación:** `confirmado_cuantificado`.
**Validador propuesto:** diagnóstico fino del cluster de 232 con
`auditar_fallo.py` (catch-all sobre cluster). Sample dirigido de ~5 casos
con seed reproducible. Pendiente para próxima sesión (acordado 14/5).
**Estado del fix:** rediagnosticado, no diseñado todavía. El fix con guard
espacial es la dirección probable (`RE_CONSIDERANDO` permisivo + `.search()`
dentro de ventana `(apertura, por_ello)` excluyendo span del dictamen),
pero F013 enseñó que permisivo + .search() sin guard rompe fallos.
**Referencias cruzadas:** PIPELINE §4.6.b. BITACORA H019. Sin ID histórico.

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

**Estado del fix:** no diseñado. Diagnóstico a nivel código pendiente.
Hipótesis fuerte sobre la lógica que decide fronteras: asignación
de página entera al caso N+1 cuando una página contiene cierre del
N + inicio del N+1. Verificar en `scripts/pipeline/construir_catalogo.py`.

**Severidad:** alta. B045 es **causa raíz arquitectónica común** de:
- **B022** (arrastre al inicio): se elimina por construcción si se
  fixea B045.
- **B025** (414 falsos `unanime`): fallback de `detectar_fin_real`
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

### B046 — Casos desaparecidos por bloque vacío en cruzador (hipótesis, mecanismo bajo revisión)

**Componente:** cruzador (etapa 3) con captura silenciosa en parser
(etapa 4).
**Origen / fuente del diagnóstico:** H025 (inspección directa de
`cruzar_catalogo_y_mapa.py` líneas 173-283 y de `procesar_archivo`
parser.py líneas 1365-1367). Separado de B045 manifestación A para
trazamiento independiente.

**Causa raíz hipotética (lectura del código, pendiente de verificación):**
si el cruzador recibiera dos casos con la misma `pagina_inicio` en
el mismo tomo, el header de `pagina_inicio` y el header de
`pagina_fin` resolverían a la misma línea X y la operación produciría
`linea_fin = X − 1` y `linea_inicio = X`, es decir, bloque de
longitud negativa. El parser saltearía silenciosamente esa fila en
línea 1367 (`if not bloque: continue`). El caso desaparecería del
corpus sin warning.

**Refutación parcial del mecanismo escrito (verificado al cierre de H025):**
consulta sobre `catalogo.csv` con `csv.DictReader` agrupando por
`tomo`: hay cero pares de filas con el mismo `pagina_inicio` en el
mismo tomo. El catalogador deduplica por `(tomo, pagina_inicio)` en
`construir_filas_catalogo` (`construir_catalogo.py` líneas 388-397),
consolidando carátulas distintas bajo un solo `caso_id_canonico` con
`nombres_indice` separado por `" | "`. **El mecanismo descrito arriba
no se manifiesta en el catálogo real porque la deduplicación lo
impide aguas arriba.**

**Estado de la hipótesis:** abierta. El intento de verificación
empírica al cierre de H025 con caso testigo `346_p1205` (commit
`890714a`, revertido en `52d0bc6`) fue inválido: la consulta
`Select-String "346,1205,"` que devolvió vacío era una consulta mal
formada (el orden de columnas del CSV es
`caso_id_canonico,tomo,archivo,pagina_inicio,...`, no
`tomo,pagina_inicio,...`). La verificación correcta con DictReader
muestra que `346_p1205` está en `fallos_localizados.csv` con líneas
16883-16988 y status `ok`, y en `csjn_casos.csv` línea 5236
procesado correctamente. **B046 no tiene testigo empírico
confirmado.**

**Hipótesis alternativa para H026:** si B046 existe como bug
arquitectónico, su mecanismo de manifestación no es "dos filas del
catálogo con misma `pagina_inicio`" sino algo más sutil. Posibles
caminos: filas con `n_nombres > 1` donde las carátulas son
claramente casos distintos consolidados por error de la
deduplicación; algún filtro intermedio del cruzador que descarte
filas; alguna combinación específica de páginas en el mapa que
produzca el escenario degenerado por otra ruta. Investigación
dirigida pendiente.

**Validador propuesto:** dado que el mecanismo escrito está
refutado, el validador previo (contar filas con
`pagina_fin == pagina_inicio_siguiente`) tampoco aplica. Nuevo
validador: comparar el conteo de filas únicas en `catalogo.csv`
contra el conteo de filas únicas en `csjn_casos.csv`. Si ambos
coinciden (5862 vs ~5819), B046 puede no estar afectando filas. Si
hay diferencia, identificar qué `caso_id_canonico` falta entre
catálogo y producción. Plan para H026.

**Estado del fix:** no diseñado. La hipótesis de fix anotada en
B045 (revertir uno de los dos `-1`) sigue siendo válida como
exploración para B045 manifestación B, independientemente del
estado de B046.

**Severidad:** desconocida. Si el conteo cataloga-vs-producción
no muestra discrepancia, B046 puede ser un bug que la deduplicación
del catalogador previene en la práctica y queda como nota
arquitectónica sin manifestación real. Si hay discrepancia,
severidad por cuantificar.

**Interacciones con otros bugs:** comparte familia con B045
manifestación B (ambas surgen de leer el código del cruzador con
foco en páginas compartidas), pero los mecanismos de manifestación
real son distintos.

**Referencias cruzadas:** BITACORA H025 (hallazgo H025-F2-01 y
sección de cierre con el revert documentado). B045 (familia
arquitectónica común, hipótesis de fix +1/-1). Sin §X.Y en PIPELINE.

**Evidencia empírica adicional (H026, corrida `--random 80`):**
La corrida del auditor `--random 80` el 2026-05-16 selecciona casos
de `fallos_localizados.csv`. Los 80 casos seleccionados están todos
presentes en `csjn_casos.csv` (verificación implícita: el auditor los
procesa y emite spans para todos). **No hay testigos empíricos de
B046 en la muestra.**

La verificación dirigida sobre el corpus completo (Fase E pendiente
de H026) compara cardinales:

- `output/parser/csjn_casos.csv`: 5.819 filas.
- `output/localizacion/fallos_localizados.csv`: 5.862 filas.
- Diferencia: 43 filas.

Esa diferencia de 43 filas es **el espacio donde podría manifestarse
B046**: casos presentes en localización pero ausentes en parser. Si
la inspección identifica casos con bloque vacío o longitud negativa,
B046 quedaría confirmado con mecanismo concreto. Si la diferencia se
explica por otras causas (filtrado intencional, errores de
localización, etc.), B046 queda refutado.

**Resultado de Fase E (H029):** verificación ejecutada con `csv.DictReader`
y comparación de sets. Los 43 `caso_id_canonico` faltantes fueron
identificados y todos tienen `status: pagina_no_en_mapa` en
`fallos_localizados.csv` — con `archivo` y `linea_inicio` vacíos.
El mecanismo de B046 (casos desaparecidos por bloque vacío en el cruzador)
**no se manifiesta en estos 43 casos**. La causa real es la documentada
en B009: el localizador no pudo anclarlos porque el marcador numérico de
página está ausente del `.md` (consumido por hojas complementarias o inicio
de volumen). El parser nunca los recibió como entrada porque el localizador
los dejó sin coordenadas — no porque el cruzador produjera bloques vacíos.

**Conclusión sobre B046:** la hipótesis de bloque vacío por páginas
compartidas sigue sin testigo empírico confirmado. Los 43 faltantes se
explican íntegramente por B009. B046 queda como nota arquitectónica: el
mecanismo descrito en el código es real, pero la deduplicación del
catalogador lo previene en la práctica. Severidad: baja. Sin fix requerido
salvo que aparezca un testigo empírico en otra inspección.

---

## Deuda ACTIVA — Parser (Etapa 4)

### B013 — Bug XII: cascada del dispositivo por falso positivo

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-c del forense. Sesión XII
(3/5/2026) con caso Benedetti como arquetipo.
**Causa raíz:** `detectar_apertura_dispositivo` (parser.py líneas 92-118) +
loop principal "primera ocurrencia gana" (líneas 1554-1563). Variantes
alternativas del dispositivo (`En consecuencia`, `Por los fundamentos`,
etc.) matchean en cuerpo argumental antes del verdadero dispositivo.
Cascadea a firma capturada de lugar incorrecto.
**Diagnóstico / evidencia:** 234 casos identificados con
`voting_pattern=sin_firma` o firma anómala.
**Estado de verificación:** `confirmado_cuantificado` (234 casos).
**Validador propuesto:** auditar caso Benedetti con `auditar_fallo.py`
para confirmar mecanismo. Sample dirigido de N=5 sobre el cluster de 234
para verificar que todos tienen el mismo patrón. Plan.
**Estado del fix:** diseñado conceptualmente — cuatro opciones en XXI:
A (variantes solo en mitad inferior del bloque), B (validar con verbos
institucionales en línea siguiente), C (`Por ello` posterior como veto),
D (combinación A+C). No aplicado.
**Referencias cruzadas:** XXI-c. Sin §X.Y en PIPELINE. Sin ID histórico.

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
**Estado del fix:** no diseñado. Es rediseño del parser, no fix puntual
(motivo original de H013 que generó la construcción del auditor).
**Referencias cruzadas:** F006. H013. PIPELINE §4.4.g (cubre solo
sumarios con link). Sin ID histórico.

### B025 — 414 falsos `unanime` (mecanismo confirmado)

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

### B029 — `collect_firma_lines` con `max_lines=40` puede ser insuficiente

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-l del forense.
**Causa raíz:** constante hardcodeada `max_lines=40` en
`parser.py` línea 423. Casos con firma fuera de ese rango (Brizuela y
Colegio de Escribanos mencionados en sesión XV) no capturan firma.
**Diagnóstico / evidencia:** mencionado en XXI sin medición. Brizuela y
Colegio de Escribanos como casos paradigmáticos, no auditados directamente
sobre este mecanismo.
**Estado de verificación:** `hipotesis_no_verificada`.
**Validador propuesto:** identificar casos en CSV con `voting_pattern=
sin_firma` que sean fallos largos (`word_count > P75`). Auditar 5-10
contra `.md` para verificar si la firma existe pero está fuera del rango
de 40 líneas. Plan.
**Estado del fix:** no diseñado. Salida natural: aumentar `max_lines` o
hacer dinámico según largo del bloque.
**Referencias cruzadas:** XXI-l. Sin §X.Y en PIPELINE. Sin ID histórico.

### B030 — `detectar_fin_real` excluye solo las primeras 5 líneas del bloque

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-m del forense. Equivalente a F013
(= B018). Está documentado como bug separado en XXI pero el mecanismo es
el mismo que B018.
**Estado:** **redundante con B018**. Probablemente se fusionan en próxima
pasada del documento. Mantenido como entrada propia hasta confirmar que
"buscar_atras 5 líneas" (XXI-m) y "primer_token matchea dentro del
dictamen" (F013) son el mismo bug.
**Referencias cruzadas:** XXI-m. F013. B018.

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

### B032 — `RE_VOTO_HDR` requiere "Señor[es]" / "Vicepresidente" / etc.

**Componente:** parser.
**Origen / fuente del diagnóstico:** XXI-ñ del forense. Equivalente a F001
(BITACORA sesión H014). XXI-ñ y F001 son el mismo bug.
**Causa raíz:** `RE_VOTO_HDR` (parser.py línea 142) requiere palabras
específicas en el header del voto. No matchea `Voto la señora`
(sin "de" antes del artículo). Caso paradigmático: voto de Argibay no se
detecta en algunos formatos.
**Diagnóstico / evidencia:** medición empírica de F001 (BITACORA línea 305):
script `medir_voto_hdr.py` sobre 2 archivos (`LibroVol331.2.md`,
`LibroVol349-1.md`). Regex viejo: 32 matches. Regex nuevo: 34. Dos votos
perdidos (ambos "Voto la señora ministra doctora doña Carmen M. Argibay"
en tomo 331.2, líneas 957 y 11724). Verificados manualmente como votos
reales, no falsos positivos.
**Estado de verificación:** `confirmado_caso_testigo` con muestra parcial
(2 archivos). Cuantificación sobre corpus completo pendiente.
**Validador propuesto:** correr `medir_voto_hdr.py` sobre corpus completo
en Windows (pendiente desde 2026-05-08 según BITACORA línea 312). Plan.
**Estado del fix:** diseñado (fix de 1 línea identificado en BITACORA).
Aplicar coordinado con regeneración.
**Referencias cruzadas:** XXI-ñ. F001. Sin §X.Y en PIPELINE. Sin ID
histórico.

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

### B039 — Tomos antiguos sin `marcador_apertura_siguiente` (descriptivo)

**Componente:** parser (descriptivo).
**Origen / fuente del diagnóstico:** PIPELINE §4.6.i.
**Estado:** no es bug, es información descriptiva sobre el corpus. Útil
para entender por qué la cascada tiene cuatro pistas distintas. No
requiere fix.
**Referencias cruzadas:** PIPELINE §4.6.i.

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

### M01 — Re-recorrer parser y actualizar PIPELINE.md

PIPELINE.md fue construido leyendo el parser en muchas sesiones del 1-9/5.
Desde entonces se aplicaron Fix 1 (`2adda06`), fix §3.6.a (B001) y fix
§4.6.j doble espacio (B005), todos sobre `parser.py` y/o
`cruzar_catalogo_y_mapa.py`. PIPELINE.md ya tiene incorporados esos fixes
como cuadros "RESUELTO". Pero la línea 2834 reconoce explícitamente:
"incorporación de bugs F001–F011 reorganizados, actualización del diagrama
global". F012, F013 y F-AUDITOR-01 son aún más recientes.

**Acción pendiente:** sesión dedicada a re-recorrer `parser.py` vivo,
`construir_catalogo.py` vivo y `cruzar_catalogo_y_mapa.py` vivo contra
PIPELINE.md, agregando §X.Y nuevos para los bugs B017, B018, B019,
B020, B021, B022, B023, B024, B025 que hoy no están como §X.Y en
PIPELINE. Incorporar adicionalmente (H025): B045 manifestaciones A/B
con la causa raíz a nivel código identificada (catalogador 410 +
cruzador 245), B046 (hipótesis de casos desaparecidos por bloque
vacío, mecanismo bajo revisión), nota de acoplamiento B018 →
`detectar_fin_real` pista 1, y referencia a
`docs/GRAMATICA_DEL_FALLO.md` como insumo conceptual sobre arquitectura
deseada del parser. Cuatro fricciones nuevas o ampliadas a agregar en
PIPELINE: §2.5.a (consecuencia aguas abajo del `pagina_fin` sin restar),
§3.5 (escenario degenerado del bloque vacío), §3.9.d nuevo (caso
desaparecido silenciado por guarda en parser), §4 (asimetría de
`detectar_fin_real` y acoplamiento con B018). Conservar la versión
actual de PIPELINE.md como referencia (trabajo de muchas sesiones,
no se descarta).

**Precondición:** ninguna. Trabajo en sesión limpia con backup de
PIPELINE.md previo.

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

> **⚠ FLAGUEADO 15/5/2026 PARA RECONSIDERAR.** La redacción de esta entrada está cuestionada en dos planos:
> 1. Confunde XXI-v con XXI-f: nombra "Bloque B", que en realidad se menciona en XXI-f (= B025), no en XXI-v.
> 2. La premisa "probablemente son los mismos 32 casos" no se sostiene tras releer Hallazgo 7 del forense (= XXI-v). Los 32 de XXI-v pasaron de `pagina_fin_no_en_mapa` a `ok` por un cambio aguas arriba sin git log. Los 32 de §3.6.a pasaron de `ok` a `pagina_fin_no_en_mapa` post-fix B001. Direcciones opuestas; probablemente grupos distintos.
> 3. La identificación caso-a-caso de los 32 originales de XXI-v es imposible sin git log de ese período.
>
> Decisión: pendiente. Esta entrada se reconsidera en sesión futura — opciones: cerrarla como no-resoluble, reformularla como cierre indirecto, o eliminarla.

### M05 — Verificación caso-a-caso de identidad de los 32 oks de XXI-v

**Pendiente derivado de la sesión del 14/5.** XXI-v ("32 oks falsos")
quedó como "estado desconocido". Post §3.6.a (B001) hay 32 fallos que
pasaron de `ok` a `pagina_fin_no_en_mapa` (PIPELINE §3.6.a). El número
coincide. Probablemente son los mismos 32 casos, pero la identidad
caso-a-caso no se verificó.

**Acción pendiente:** comparar lista de los 32 documentados en §3.6.a
contra el "Bloque B" mencionado en XXI-v (si la lista existe en algún
output histórico). Trabajo estimado 10 minutos.

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
| XXI-l | B029 | `collect_firma_lines max_lines=40` |
| XXI-m | B030 (= B018) | Redundante con F013, mismo mecanismo |
| XXI-n | B031 | `linea_es_header_sumario` mayúsculas |
| XXI-ñ | B032 (= F001) | `RE_VOTO_HDR` |
| XXI-o | B033 | `ultimo_del_tomo_sin_fin` |
| XXI-p | B034 | `RE_FECHA_LINEA` paréntesis/guiones |
| XXI-q | (descartado) | XXI mismo: no es bug, código muerto |
| XXI-r | (no entra) | Decisión "no fixear" sesión V |
| XXI-s | (no entra) | `jueces_desconocidos` vacío, intencional |
| XXI-t | B003 parcial | Hojas complementarias Fase 1 ✅, Fase 2 = B009 |
| XXI-u | (no entra) | Cubierto implícito por §2.5.e PIPELINE |
| XXI-v | M05 | Verificación caso-a-caso pendiente |

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

- **Bugs cerrados:** 8 (B001-B008).
- **Bugs en validación:** 2 (B009 cuantificado pendiente fix, B010
  rediagnosticado pendiente fix).
- **Bugs activos del pipeline (catálogo + cruzador + parser):** 31
  (B011-B039, B048). De ellos:
  - 1 confirmado_cuantificado pendiente de aplicar fix de higiene (B028)
  - ~14 confirmado_caso_testigo o confirmado_cuantificado (B011, B012,
    B013, B014, B016, B017, B018, B019, B020, B021, B022, B023,
    B035-B039, B048)
  - 1 sospecha_cardinal (B025)
  - 7 hipotesis_no_verificada — identificados leyendo código en XXI sin
    medir (B015, B026, B027, B029, B031, B033, B034)
- **Bugs activos del auditor:** 7 (B040-B042, B047, B049, B050, B051).
- **Pendientes metodológicos:** 8 (M01-M08).

**Próximo trabajo priorizado (orden sugerido):**

1. Cerrar el bloque docs de la Fase 2 (commit de este archivo + decisión
   sobre destino del forense + decisión sobre PIPELINE.md M01).
2. Diagnóstico fino de B010 con `auditar_fallo.py` (acordado para
   próxima sesión, BITACORA H019).
3. M05: verificar identidad de los 32 oks de XXI-v contra los 32 de B001.
4. Cuantificar los `hipotesis_no_verificada` antes de fixearlos. Prioridad
   especial: B025 (414 unanime) re-medir post §3.6.a.
5. Bloque snapshots Fase 2 (M02).
6. **Fase F (H030, prioritaria):** portar `detectar_caratula` del auditor
   al parser como ancla de inicio de caso. Tomar muestras representativas
   de tomos viejos y nuevos antes de implementar. Snapshot pre-fix +
   auditoría antes y después. Ver hallazgo estructural en B009 y nota
   H028 al pie.
7. B049 Var-B (H030): diagnóstico fino de `340_p1551`.
8. Cuantificaciones B050-quant, B051-quant, HN3'-quant (H030).
9. M06 antes de implementar detector de epílogo: verificar persistencia
   editorial de la gramática sobre el corpus completo.


**Nota H028 — argumento de diseño para Fase F:** la fuente canónica para
`case_name_cuerpo` es el índice editorial (líneas antes del primer sumario),
no el cuerpo del fallo. Buscar en `Vistos los autos: "X"` introduce ruido
por remisiones a otras causas y carátulas de recursos de hecho.
`detectar_caratula` del auditor ya implementa esta estrategia correctamente
y es el candidato natural a portar al parser como fuente primaria.


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
