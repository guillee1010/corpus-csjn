# Changelog del parser CSJN

Pipeline: `paginas/csjnvNN.py` → `csjn_casos_vNN.csv` + `csjn_casos_vNN_votos.csv`  
Corpus: Fallos CSJN Tomos 329–349 (2006–2026), excluyendo 335–336  
Fuente: PDFs oficiales convertidos a Markdown

---

## v1–v3 — Prueba de concepto (28 abril 2026, sesión inicial)

**Problema motivador:** extraer datos estructurados de los volúmenes de Fallos convertidos a Markdown. El corpus tenía drift editorial de casi 20 años; no se sabía qué marcadores eran estables.

**Trabajo de v1:** identificación de marcadores de apertura y cierre. Se confirmó que `FALLO DE LA CORTE SUPREMA` (singular, no plural) seguido de `Buenos Aires, [fecha]` es el marcador de apertura de cada caso. `Tribunal de origen:` es el marcador de cierre. Ambos se verificaron contra los PDFs originales.

**v2:** se agregó detección básica del dispositivo `Por ello,` y extracción de carátula (`case_name`). Primer CSV de salida con una fila por caso.

**v3:** se incorporó manejo de `dictamen embebido` (opinión del Procurador intercalada en el cuerpo del fallo). Sin esta distinción el parser contaminaba el cuerpo del fallo con texto del dictamen.

**Resultado:** parser funcional sobre tomos recientes (344–349). Dataset: ~500 casos aproximados. Output: un solo CSV de casos.

---

## v4–v6 — Detección de firmas y votos (28 abril 2026)

**Problema motivador:** los fallos incluyen votos separados (concurrencias, disidencias). El parser v3 los ignoraba y el `voting_pattern` era irrecuperable.

**v4:** primer intento de detección de firmas de jueces. Se definió una ventana de N líneas después del dispositivo para buscar nombres. Bug inicial: la ventana era fija y en fallos largos no alcanzaba las firmas.

**v5:** firma multilínea (`firma_raw` acumulado). Se incorporó detección de conjueces. Se definieron las posiciones de voto: `mayoria`, `según su voto`, `en disidencia`, `por su voto`.

**v6:** distinción crítica entre `Por ello` dispositivo (verbo institucional: `se`, `habiendo`) versus `Por ello` argumental (cláusula subordinada: `la`, `concluyó`). Sin esta distinción el parser confundía partes argumentativas con el dispositivo. Se incorporó `wc_mayoria` y `wc_votos` (word count por bloque).

**Resultado:** detección de firmas funcional en tomos recientes. `wc_votos = 0` para mayorías sin voto separado es decisión de diseño deliberada, no bug.

---

## v7–v9 — Bifurcación del output y estabilización (28 abril 2026)

**Problema motivador:** el CSV de casos mezclaba información de nivel caso con información de nivel voto. Dificulta el análisis estadístico.

**v7:** refactor del loop principal a procesamiento en un solo pase (`single-pass block processing`). Mejoras en detección de carátula. Sugerencias de colega parcialmente incorporadas.

**v8:** se separaron los outcomes en patrones: `inadmisible_280`, `inadmisible_acordada_4`, `hace_lugar`, `rechaza`, `competencia`, `otro`. Se incorporó `is_full_bench`, `is_merit_decision`, `caso_id` como FK estable.

**v9:** **bifurcación del output.** El parser produce dos datasets:
- `csjn_casos_v9.csv` — case-centered, una fila por sentencia (817 casos, tomos 344–349)
- `csjn_casos_v9_votos.csv` — vote-centered, una fila por juez/voto (2.803 votos)

Se incorporó `posiciones` (JSON dict con posición de cada juez) y se completó el companion script `csjn_analisis.py` con exportación a Excel.

**Hallazgo empírico clave:** decisiones unánimes tienen mediana `wc_votos = 0`; patrón `mixed` tiene mediana 1.803. Evidencia directa para H3 (coordinación inercial vs. deliberación).

**Dataset identificado** como equivalente embrionario argentino del Spaeth SCDB.

---

## v10 — Corpus extendido y detección de art. 280 (28 abril 2026)

**Problema motivador:** extender el corpus de 6 tomos (344–349) a 19 tomos (329–349, sin 335–336). El parser v9 estaba diseñado para tomos recientes y fallaba en tomos viejos (banco de 7 jueces, formato ligeramente distinto).

**Cambios:**
- `classify_outcome` recibe ahora tanto el dispositivo como el considerando para detectar `inadmisible_280`. El art. 280 figura en el considerando, no en el dispositivo — bug de diseño en v9.
- Nuevo outcome: `inadmisible_acordada_4`.
- CSV de votos enriquecido con columna `texto_voto` (texto íntegro del voto individual).
- Nueva columna `considerando_texto` en CSV de casos.

**Problemas detectados en validación:**
- Tomos 335–336 producen `n_titulares = 0` en 401 casos (formato de MD distinto o corrupción). Se excluyen del corpus analítico.
- `inadmisible_280` detecta solo 39 casos sobre ~5.700 (0,7%) — muy por debajo de lo esperable institucionalmente. Bug pendiente, no resuelto en v10.
- `sin_firma` = 797 casos (14%), alto para corpus completo.
- `outcome = otro` = 1.941 casos (34%) — dispositivo detectado pero verbo no matchea ningún patrón.

**Resultado:** corpus extendido a 5.323 casos. Dataset con `csjn_casos_v10.csv` + votos.

---

## v11 — Detección positiva de originaria y detector de dispositivo ampliado (28 abril 2026)

**Problema motivador:** dos bugs masivos identificados en auditoría del v10.

**Bug 1 — Detector de dispositivo:** v10 solo captaba `Por ello` como apertura del dispositivo. En tomos viejos (329–340), ~25% de los fallos usan otras fórmulas (`Por los fundamentos del dictamen`, `De conformidad con lo dictaminado`, `Por todo lo expuesto`). Resultado: 1.123 fallos sin dispositivo detectado.

**Bug 2 — `is_originaria` por heurística negativa:** v10 clasificaba como originaria todo caso donde no encontraba `Tribunal de origen:`. Resultado: 2.238 casos (39%) marcados erróneamente como originarios cuando la Corte tramita solo ~300 por año por esa vía.

**Cambios:**
- `RE_DISPOSITIVO_VARIANTES`: 11 patrones de apertura de dispositivo. Nueva función `detectar_apertura_dispositivo()`. Tolerancia al typo OCR `concusiones` por `conclusiones`. Fix bonus: `[,.]` → `[,.]?` en el regex argumental (evitaba detectar `"Por ello concluyó..."` sin coma como dispositivo).
- `is_originaria`: reemplazada por función `es_originaria()` con detección positiva sobre 4 señales: `"competencia originaria"` en cuerpo, art. 117 CN, `"Originario"` en carátula, `"en forma originaria"` / `"instancia originaria"`.
- Nueva columna `tribunal_origen_status` en CSV de casos.

**Resultado:** `sin_dispositivo` baja de 1.123 a ~173 (−85%). `is_originaria` baja de 2.238 a 358 (coherente con realidad institucional). Dataset: ~5.300+ casos.

---

## v12 — Clasificación de tipo de voto separado (28 abril 2026)

**Problema motivador:** el CSV de votos no distinguía el tipo de concurrencia. Un voto `según su voto` puede ser adhesión con matiz (el juez firma la mayoría pero agrega argumento propio) o puede ser el fallo más importante del caso. Sin clasificación el análisis textual es ciego.

**Cambios:**
- Nueva función `clasificar_tipo_voto()` con detección de 5 tipos de voto separado.
- Nueva columna `tipo_voto_sep` en CSV de votos.
- Nueva columna `fragmenta_ratio` (indicador de si el voto introduce razonamiento divergente del majority).
- Tests sobre 8 ejemplos del ground truth con `assert`.

**Nota:** esta versión fue desarrollada en colaboración con Claude Opus sobre prompt estructurado (`prompt_opus_v12.md`) con el script v11 embebido.

**Resultado:** CSV de votos con 3 columnas nuevas. Sin cambios en el CSV de casos.

---

## v13 — Catálogo de entradas del índice (28–29 abril 2026)

**Problema motivador:** el parser producía casos a partir del cuerpo de los MD pero no tenía fuente de verdad sobre *cuántos* fallos debería haber en cada tomo. Sin catálogo no había manera de detectar fallos que el parser perdía.

**Trabajo de esta versión:** se construyó `construir_catalogo.py` como script separado que extrae las entradas del índice temático de cada tomo y genera `catalogo_v13.csv`. Se resolvieron problemas de diseño: entradas cruzadas (ej. `A.F.I.P. (Aguas de la Costa S.A. c/):`), páginas múltiples por entrada, cálculo de `pagina_fin` inter-archivo en tomos multi-volumen.

**Deduplicación:** regex `\([^)]*c\/[^)]*\)` para clasificar entradas cruzadas vs. directas; se conserva la directa. `pagina_fin` calculada globalmente por `(tomo, pagina_inicio)` para cruzar fronteras de archivo.

**Resultado:** `catalogo_v13.csv` con 5.690 entradas en 19 tomos.

---

## v14 — Mapa de páginas y cruce (29 abril 2026)

**Problema motivador:** el catálogo tiene páginas del índice pero el parser opera sobre líneas del MD. Necesitaba un puente entre ambas coordenadas.

**Trabajo de esta versión:**
- `detectar_paginas.py`: genera `mapa_paginas.csv` con 46.936 headers de página detectados en los 46 archivos MD.
- `cruzar_catalogo_mapa.py`: vincula cada entrada del catálogo con su ubicación física (`linea_inicio`) en el MD. Produce `fallos_localizados.csv`.

**Resultado del cruce:** 5.569 ok / 121 huérfanos (entradas del catálogo sin ubicación en el mapa). El parser v14 usa el catálogo como fuente de verdad para delimitar bloques (en lugar de depender solo de marcadores textuales). Corpus: 5.690 entradas.

**Sesgo identificado post-v14:** el parser usaba la línea de inicio del *siguiente* fallo como fin del actual, sin buscar el fin real. Esto inflaba los bloques de los últimos fallos de cada tomo (`ultimo_del_tomo`).

---

## v15 — Corrección del sesgo de fin de bloque (29–30 abril 2026)

**Problema motivador:** v14 tenía sesgo sistemático en la detección del fin de bloque. Los últimos fallos de cada tomo tenían bloques inflados porque no había "siguiente fallo" que sirva de límite.

**Cambios:**
- Nueva columna `linea_fin_real` calculada por búsqueda bidireccional.
- Nuevas columnas `status_fin` y `pista_fin` (trazabilidad del método de detección).
- La carátula del siguiente caso es la pista más fuerte (85% de los fines bien detectados).

**Impacto medido (v14 → v15):**
- `sin_dispositivo`: −580
- `unanime`: +831
- Word count global: −5,6%

**Resultado:** `csjn_casos_v15.csv` con 5.647 fallos. Corpus principal para análisis estadístico.

---

## v16 — Corrección de fechas (30 abril 2026)

**Problema motivador:** v15 tenía bug en la extracción de fechas. Muchos casos quedaban sin fecha o con fecha incorrecta.

**Cambios:** corrección del extractor de fechas. 92,6% de los casos con fecha extraída correctamente post-v16.

**Resultado:** `csjn_casos_v16.csv` (5.647 fallos) + `csjn_casos_v16_votos.csv` (20.562 votos). Este es el dataset en producción al inicio de la jornada del 29–30 abril 2026.

**Anomalías documentadas al cierre de v16** (`anomalias_pipeline_completo.csv`, 26 anomalías en 5 capas):
- 573 casos `sin_firma` (10,1% del corpus). Distribución: R1 (no detectó dispositivo) 51,7%, R2 (dispositivo ok, ningún juez en ventana de 40 líneas) 48,3%.
- Concentración en tomos recientes: tomo 345 28,7%, tomo 347 18,9%, tomo 348 18,1%.
- 121 huérfanos del cruce.
- 19 casos `ultimo_del_tomo` con bloques inflados.
- 3 casos `fin_no_detectado`: `345_p250`, `345_p800`, `346_p74`.
- Categoría A (bloques mutilados por bug de `detectar_fin_real`): caso testigo `329_p53` (7 líneas, 58 palabras).
- Categoría B (sumarios con link externo): innovación editorial desde tomo 347. Patrón: `(*) Ver fallo.` literal. Estos casos no tienen pieza decisoria en el corpus y deben filtrarse, no parsearse mejor.

---

## v17 — Fix de `sin_firma` y columna `categoria_editorial` (30 abril 2026)

**Problema motivador:** 573 casos `sin_firma`. Diagnóstico: la ventana de búsqueda de firmas en `csjnv16.py` (`d=1` bucket) tiene un bug de delimitación: la constante `-1` en `construir_catalogo.py:341` causa que el último bloque de cada tomo se extienda hasta el final del archivo en lugar de hasta el marcador real de fin. Esto infla los bloques en los últimos fallos de cada tomo y desplaza las firmas fuera de la ventana.

**Cambios (en dos commits separados):**

*Cambio 1 (commit independiente):*
- Fix de `construir_catalogo.py:341`: eliminar el `-1` que causaba extensión indebida del último bloque.
- Tests de regresión definidos: Colonia Penal de Ezeiza (`346_p57`), N.N. s/ Incidente de incompetencia, caso de tomo viejo bit a bit.
- Métrica de éxito: baja de `sin_firma` en bucket `d=1`, Colonia Penal de Ezeiza pasa a detectar firmas.

*Cambio 2 (commit sobre el 1):*
- Nueva columna `categoria_editorial` en CSV de casos. Cinco valores: `fallo_completo` (default), `sumario_con_link` (detector literal `Ver fallo.` case-sensitive), `acordada`, `material_preliminar`, `separador_mes`.
- Detector de `sumario_con_link` es ortográficamente seguro: sin riesgo de regresión sobre tomos viejos.

**Estado al cierre del 30 abril 2026:**
- Cambio 1 mergeado y validado: 175 mejoras, `sin_firma` baja de 10,1% a 7,1%, 32 huérfanos menos.
- El caso `334_p829` confirmado como no-regresión: bug de localización en tomos multi-volumen enmascarado en PRE.
- `catalogo_volumenes.csv` generado, pendiente integración al cruce (Cambio 3).
- Cinco/seis categorías editoriales identificadas; detector implementado.

**Pendientes para v18:**
- Filtro de material preliminar en `detectar_paginas.py` + regenerar mapa y catálogo de volúmenes (debe hacerse antes del Cambio 3 para no invalidar el catálogo existente).
- Cambio 3: integrar `catalogo_volumenes.csv` al cruce.
- 19 casos `ultimo_del_tomo` con bloques inflados aún pendientes.
- 3 casos `fin_no_detectado` pendientes.
- 121 huérfanos: reducción parcial lograda en v17 Cambio 1, restan ~89.
- Mejora de `detectar_fin_real` para `primer_token` débil (postergada, requiere sesión dedicada).

---

*Nota metodológica:* este changelog se reconstruyó retrospectivamente a partir de los logs de sesiones de trabajo. Fechas confirmadas por timestamps de archivos (`historial/csjnv10.py` → 28/04, `historial/csjnv11.py` → 28/04) y commits del repo (`git log`, primer commit con snapshot v16 → 30/04). Las versiones v1–v9 se desarrollaron en una sola sesión el 28/04 según el summary del chat fundacional. Las versiones v12–v15 no tienen archivo commiteado individualmente; sus fechas (28–30/04) se infieren por el contexto de sesiones.

---

## v17 beta v2 — 2026-05-01

### Estado: descartada.

### Intención del cambio:

Reescribir el detector de fin de dictamen reemplazando la heurística v16 ("línea con fecha + previa corta") por una regla OR de dos señales:

- Firma de Procurador conocido al final de línea corta. Lista ampliada empíricamente del corpus: Casal, Monti, Abramovich, Cosarin, Righi, Bausset, Warcalde, Netto, Becerra, Carbó, Obarrio, Beiró, Sachetta.
- Línea que empieza con "Buenos Aires, X de mes de YYYY" (fecha al pie típica del dictamen).
- Ambas señales con exclusión de contextos de cita (comillas, "Fallos:", "fs.", "Procurador Fiscal", "Ministerio Público:", "precedente").

Se incorporó además la columna `wc_fallo_neto = word_count - wc_dictamen` para permitir análisis del cuerpo decisorio separado del aporte del dictamen, y se unificaron los tipos de las columnas booleanas (`dictamen_presente`, `is_originaria`, `is_full_bench`, `is_merit_decision`) como `int` en todos los casos.

### Razones del descarte:

- **Regresión en `sin_firma`.** Pasó de 312 (v17 beta v1) a 580. La regla nueva interfirió con la detección de firmas de jueces del fallo posterior al dictamen, sin beneficio comprobado en la detección del dictamen mismo.
- **Métrica de validación inválida.** El script `validar_v17_beta_v2.py` reportaba 2155 casos "patológicos" donde `wc_dictamen ≥ word_count`. La métrica está mal construida: `word_count` se calcula como `wc_mayoria + wc_votos`, no incluye preámbulo ni dictamen. Que el dictamen sea más extenso que la suma de mayoría más votos del fallo posterior es estructuralmente normal en fallos breves resueltos por remisión al dictamen. La métrica no diagnostica nada útil.
- **No se llegó a inspeccionar empíricamente** ningún bloque concreto para confirmar si el detector acotaba bien el dictamen. La sesión se cerró antes de poder hacerlo.

### Hallazgo metodológico para v18:

Diseñar una métrica de validación que sea efectivamente diagnóstica del corte del dictamen. Una opción es comparar la línea de fin de dictamen detectada con la posición esperada del marcador de inicio del fallo (la fecha "Buenos Aires, ..." que abre el fallo de la Corte): el fin del dictamen debería caer inmediatamente antes de ese marcador. Esto pone el inicio del fallo como ancla, en vez de buscar señales débiles de fin de dictamen.

### Estado de los archivos:

- `csjnv17_beta_v2.py` y sus CSVs (`csjn_casos_v17_beta_v2.csv`, `csjn_casos_v17_beta_v2_votos.csv`) eliminados del repo.
- Script de validación movido a `scripts/diagnosticos/validar_v17_beta_v2.py` para referencia futura.
- Output de la corrida (`validacion_v17_beta_v2.txt`) eliminado.

---

## v17 beta — 2026-05-01

### Estado: versión activa (validada parcialmente: 4 casos de sumario-con-link verificados manualmente; 2 casos de falso positivo identificados pero no resueltos). Reemplaza a v16 fix1 como baseline tras descarte de v17 beta v2 (2026-05-01).

### Cambios respecto a v16:

- **Detector de sumarios-con-link.** A partir del tomo 345, la CSJN publica algunos casos solo como sumario editorial con link al fallo online, sin reproducir el fallo completo. v17 detecta el patrón `(*) Sentencia del [fecha]. Ver en https://sj.csjn.gov.ar/...` (variantes "Ver fallo." en tomos 347-349) y marca esos casos como `tipo_entrada = "sumario_con_link"`. Campos analíticos quedan vacíos. Metadata estructural (linea_inicio, linea_fin, source_file, etc.) se conserva.
- **Nueva columna `tipo_entrada`** con valores `"fallo"` (default) o `"sumario_con_link"`.
- **Nueva columna `wc_dictamen`** que exporta el word count del dictamen (heurística heredada de v16, no validada).

### Resultados:

- 5647 casos procesados.
- 160 marcados como `sumario_con_link`:
  - 104 con `status_localizacion = ok_sin_marcador_apertura` (limpios).
  - 56 con `status_localizacion = ok` (ambiguos: 3/5 verificados son sumarios reales; 2/5 son fallos legítimos contaminados por solapamiento de páginas).
- `sin_firma` bajó de 399 (v16 fix1) a 312.

### Pendientes / problemas conocidos:

- Solapamiento estructural del catálogo: una misma página de la edición oficial puede contener dos casos distintos (fallo + sumario, o dos sumarios encadenados), pero el catálogo asigna un solo `caso_id_canonico`. Esto produce:
  - Falsos positivos del detector (~22 casos: fallos largos cuyo bloque incluye un sumario-con-link siguiente).
  - 28 sumarios-con-link cuya firma es del fallo anterior, no propia.
- Solución estructural pendiente (ver "Opción C" en bitácora): post-procesar el catálogo para dividir entradas con múltiples casos. Postergado a v18.

---

## v16 fix1 — 2026-04-29

### Estado: producción (baseline actual).

### Cambios respecto a v16:

- Fix aplicado en `construir_catalogo.py`. Output regenerado como `csjn_casos_v16_fix1.csv`.

---

## v16 — 2026-04-29

### Cambios respecto a v15:

- Fix de extracción de fecha. v15 buscaba la fecha solo en las primeras 8 líneas del bloque, pero el bloque arranca con sumarios y dictamen. v16 busca la fecha cerca del marcador `FALLO DE LA CORTE SUPREMA` (caso a) o como última fecha "Buenos Aires" del bloque (caso b).
- Solo el 5.6% de los fallos tenía fecha extraída en v15. v16 mejora sustancialmente.

---

## v15 — 2026-04-28

### Cambios respecto a v14:

- Detección de fin real del fallo dentro del bloque (`linea_fin_real`). Permite cortar el bloque cuando empieza el caso siguiente, evitando contaminación.
- Output bifurcado: CSV de casos + CSV de votos (uno por juez por caso).

---

## v14, v12, anteriores

Ver historial de git y comentarios en cabecera de cada archivo.

---

## Protocolo de rollback

Si una versión activa muestra problemas en el análisis estadístico y conviene volver a una versión anterior estable, el procedimiento es:

**De v17 beta v1 a v16 fix1:**

1. Confirmar que el CSV de v16 fix1 (`paginas/csjn_casos_v16_fix1.csv`) está commiteado y trackeado.
2. En el script de análisis, cambiar el path de entrada de `csjn_casos_v17_beta.csv` a `csjn_casos_v16_fix1.csv`.
3. Documentar en `docs/log.md` la razón del rollback (qué problema motivó volver atrás, en qué tomos o qué tipo de casos).
4. No es necesario borrar el CSV ni el script de v17 beta del repo: queda como histórico.

**Identificación de la versión activa:**

La versión activa es la marcada como tal en este changelog. Al cierre de cada sesión que cambie la versión activa, actualizar el campo "Estado" de la entrada correspondiente y agregar la nota "Reemplaza a vXX como baseline tras [razón]".

**Antes de declarar una versión nueva como activa:**

- Diff de métricas clave contra la versión anterior (`sin_firma`, `voting_pattern`, `wc_*`).
- Inspección manual de al menos 3 casos representativos (un fallo unánime largo, un fallo con dictamen, un sumario con link si aplica).
- Verificación de que no haya regresión cuantitativa sin justificación cualitativa (caso v17 beta v2: +268 sin_firma sin beneficio comprobado → descartada).
## construir_catalogo v15 — 2026-05-01

### Estado: producción (reemplaza a `construir_catalogo.py` con Fix 1).

### Problema motivador

Detectado durante la sesión de validación cruzada con Gemini sobre el Tomo 349. El `csjnv16.py` (y posteriores) reportaba 36 fallos para el Tomo 349 cuando Gemini detectaba 45. El bug no estaba en el parser sino en el **extractor del catálogo**: la función `detectar_secciones` busca el marcador `INDICE POR LOS NOMBRES DE LAS PARTES` para arrancar a parsear el listado del índice. En tomos modernos (337-349), el reflow del conversor PDF→md ubicaba sistemáticamente esa portadilla **después** de las primeras entradas alfabéticas del listado (A, B, C), no antes. Resultado: pérdida silenciosa de 9-15 entradas alfabéticamente tempranas por tomo.

### Cambios

- Nueva función `extender_inicio_indice_nombres()` con look-back desde el header `INDICE POR LOS NOMBRES DE LAS PARTES` hasta una cabecera "A" aislada, validada por la presencia de al menos 3 anclas `: p. N` entre la "A" y el header. Tres validaciones encadenadas garantizan no-regresión en tomos donde el header ya estaba en su lugar correcto.
- Integración en `procesar_archivo`: llamada después de `encontrar_indice_nombres`. Logging `[FIX-v15]` cuando el fix se activa, silencioso cuando no.

### Resultados

- Catálogo: pasa de 5690 a 5862 entradas (+172).
- `fallos_localizados`: 5862 cruzados, 5741 ok.
- `csjn_casos`: pasa de 5647 a 5819 fallos.
- Distribución de los 172 nuevos: 154 en `ok` (89.5%), 18 en `ok_sin_marcador_apertura` (10.5%). Cero huérfanos nuevos.
- Bug confirmado en TODOS los tomos modernos (337-349), no solo en el 349. Pérdida típica: 9-15 entradas por tomo.

### Tomo 349 específico

9 entradas recuperadas en orden alfabético: Aballay (p. 210), Agencia de Administración de Bienes del Estado (p. 300), Arias (p. 34), Asociación Gremial de Computación (p. 286), Becerra (p. 53), Bertotto (p. 244), Bodereau (p. 258), Buttera (p. 253), Colegio de Martilleros y Corredores (p. 1).

### Pendientes documentados

- Tomos 337-341: arrancan con primera entrada en p. 23-61 (en lugar de p. 1). Diagnóstico previo identificó esto como un bug **distinto** al del Tomo 349, no relacionado con la portadilla mal ubicada. Auditoría pendiente.
- Tomo 349 con solo 45 entradas (vs ~200 típicas en tomos modernos). Probablemente falta procesar `LibroVol349-2.md`, `-3.md`, etc. Pipeline upstream, no parser.
- 121 huérfanos del cruce siguen estructurales, sin cambio respecto a v14.

---

