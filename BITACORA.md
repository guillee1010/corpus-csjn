# Bitácora de hallazgos

Registro de hipótesis, diagnósticos, falsos positivos e iteraciones de pensamiento sobre el pipeline. Pensado para que en sesiones futuras no se repitan caminos ya recorridos ni se den por buenas conclusiones que fueron invalidadas.

Formato por entrada: hipótesis o hallazgo, evidencia, conclusión (válido / invalidado / parcialmente válido), implicancias.

---

## Sesión 2026-05-02

### H001 — La deuda técnica subestimaba el problema

**Hipótesis inicial (DEUDA_TECNICA.md pre-sesión):** "43 huérfanos perdidos en tomos 331-334".

**Hallazgo:** los huérfanos reales son **121**, distribuidos en todos los tomos del corpus, con dos regímenes claramente distintos:

- Régimen 2008-2011 (tomos 329-334): entre 4 y 22 huérfanos por tomo, promedio ~16. Alta densidad.
- Régimen 2014-2025 (tomos 337-348): entre 1 y 3 huérfanos por tomo, promedio ~2. Baja densidad.
- Régimen 2026 (tomo 349 provisorio): 1 caso (Y.P.F. fuera de índice por truncamiento).

**Estado:** válido. La cobertura honesta del corpus pre-fix era 5819 / (5819 + 121) = **97,96%**, no 99,27% como decía la deuda técnica.

**Implicancia:** la deuda técnica original mezclaba dos cosas distintas — los 43 casos del régimen 2008-2011 que sí son del patrón Boston (Bug A), y los huérfanos genéricos. Conviene mantener documentación cuantitativa actualizada con el output del pipeline, no estimaciones.

---

### H002 — Los 121 huérfanos son todos del mismo bug

**Hipótesis inicial:** un único bug del localizador (heurística que falla por dictamen embebido).

**Diagnóstico:** los huérfanos se dividen en cuatro clusters distintos según el campo `status` del CSV:

| Status | Casos | Causa raíz | Bug ID |
|--------|------:|------------|--------|
| `pagina_no_en_mapa` | 43 | Cabecera del fallo no detectada en `mapa_paginas.csv` (probable: dictamen embebido) | A |
| `pagina_fin_no_en_mapa` | 39 | Página final +1 no detectada en mapa | C |
| `fallo_cruza_archivos` | 20 | Fallo siguiente está en otro `.md` | B |
| `ultimo_del_tomo` | 19 | Último fallo del tomo, bloque incluye índices | D |

**Estado:** invalidado en su forma original. Son **al menos cuatro bugs distintos** con causas diferentes.

**Implicancia:** cada bug requiere fix propio. Atacarlos juntos genera regresiones cruzadas. Decisión metodológica: un fix por vez con ciclo completo de validación.

---

### H003 — Los huérfanos del régimen reciente son fallos largos atípicos

**Hipótesis durante diagnóstico:** los huérfanos de 2014-2025 se concentran en plenos largos con estructura compleja.

**Análisis:** distribución bimodal real dentro del régimen reciente:

- Cluster grande (8 casos): rangos de 24 a 94 páginas. Plenos largos.
- Cluster chico (5 casos): rangos de 6 a 13 páginas. Fallos comunes.
- Cluster sin `pagina_fin` (13 casos): los últimos del tomo de cada año (Bug D).

**Estado:** parcialmente válido. La hipótesis original capturaba solo los fallos largos. Los breves y los últimos-del-tomo son patrones distintos.

**Implicancia:** Bug B y Bug D (los dos identificables) son ortogonales. El cluster chico (5 fallos breves) sigue sin causa raíz documentada — investigar en sesión dedicada.

---

### H004 — `cruce_anuarios.py` es el localizador del pipeline

**Hipótesis inicial (basada en nombre y mención de `linea_fin_real`):** el script `cruce_anuarios.py` es donde se asigna el status de localización.

**Investigación:** lectura del código mostró que `cruce_anuarios.py` **no es el localizador**. Es el script que cruza el corpus parseado contra los anuarios estadísticos de la CSJN para análisis de tesis (calcula `materia_pct`, `pct_unanime`, etc.).

**El localizador real es `paginas/cruzar_catalogo_y_mapa.py`.**

**Estado:** invalidado.

**Implicancia:** evitar inferir función de un script por su nombre o por menciones cruzadas en grep. Leer el código antes de modificar. Esta confusión costó un ciclo de diagnóstico.

---

### H005 — Los 19 huérfanos `ultimo_del_tomo` no tienen `linea_inicio`

**Hipótesis durante diagnóstico:** si están en huérfanos, es porque el localizador no encontró el inicio del fallo.

**Verificación:** los 19 casos tienen `linea_inicio` Y `linea_fin` poblados. La columna que está vacía es `pagina_fin` (la página final). El parser podría procesarlos directamente si los recibiera.

**Diagnóstico real:** el localizador asigna `status = 'ultimo_del_tomo'` deliberadamente cuando no puede determinar `pagina_fin`, aunque tenga las líneas. Es decisión defensiva: prefiere mandar el caso a huérfanos antes que procesarlo con un bloque que incluya el aparato editorial de índices del `.md`.

**Estado:** invalidado.

**Implicancia:** el problema no es de detección sino de delimitación. El fix correcto no es "encontrar el caso" sino "decirle al localizador dónde cortar el bloque".

---

### H006 — La regla simple "última línea del .md" es buena solución

**Hipótesis intermedia:** asignar `linea_fin = última línea del .md` para los últimos del tomo y dejar que el parser limpie la basura.

**Contra-argumento (planteado por el usuario):** el aparato editorial de índices contiene **carátulas de TODOS los fallos del tomo** ("Boston Cía. de Seguros... 7", "Villarreal, Daniel... 379", etc.). Es ruido estructuralmente similar al contenido válido. Cualquier heurística del parser que use patrones de texto (carátulas, firmantes, fechas) va a confundirse. El bloque resultante es prácticamente impredecible.

**Estado:** invalidado.

**Implicancia:** la regla simple es la que el localizador YA usaba (línea 173 del script original). Por eso los 19 casos están en huérfanos: es decisión defensiva preexistente, no falla. El fix correcto es **cortar antes del aparato de índices**.

---

### H007 — `secciones_indices_v14.csv` ya tiene la información necesaria

**Hipótesis:** el archivo `secciones_indices_v14.csv` (5.986 bytes en raíz) podría tener la línea de inicio de los índices por archivo, lo que haría el fix trivial.

**Verificación:** el archivo tiene una fila por cada índice de cada archivo, con columnas `tomo, archivo, tipo_indice, linea_inicio, linea_fin`. Cinco tipos de índice por archivo (nombres, materias, sumario, legislación, general), siempre en ese orden contiguo.

**Verificación adicional:** "índice de nombres" es siempre el primer índice del archivo (invariante confirmada en TODOS los archivos del corpus, no solo en los 19 con problema).

**Estado:** válido.

**Implicancia:** el fix se reduce a leer el CSV y hacer un join. No requiere refactor del detector ni reanálisis de los `.md`. Es la diferencia entre "1-2 horas de trabajo" y "medio día de refactor".

---

### H008 — La línea `linea_fin` actual de los huérfanos coincide con el final del último índice

**Hallazgo durante validación:** para los 19 casos `ultimo_del_tomo`, la `linea_fin` actual es exactamente `ultimo_indice_fin - 1` del archivo (diferencia de 1 línea consistente en los 19).

**Implicancia:** el localizador actual no usa "última línea del .md" como creía la documentación; usa "fin del último índice". Es ya una heurística sofisticada que consume `secciones_indices` indirectamente. El fix solo cambia el tope de "después del aparato" a "antes del aparato".

**Estado:** válido. Mejora la comprensión del comportamiento existente del script.

**Importancia:** la lectura inicial del docstring del script ("linea_fin = última línea del .md") era engañosa respecto al comportamiento real. Lectura del código fuente reveló el uso del CSV de secciones por la rama `fallo_cruza_archivos`. Lección: docstrings desactualizados son peligrosos; verificar contra código.

---

### H009 — Los outputs anómalos post-fix son del fix mismo

**Hipótesis durante validación post-corrida:** las anomalías observadas (`pagina_fin_no_en_mapa` 39 → 0, `fallo_cruza_archivos` 20 → 27) son efectos colaterales del fix Bug D.

**Contra-evidencia:** el fix solo modifica la rama `if pg_fin is None`. Las ramas que producen `pagina_fin_no_en_mapa` y `fallo_cruza_archivos` están en la rama `else` y no fueron tocadas. No hay vía técnica directa para que el fix afecte esos status.

**Hipótesis alternativa:** la categorización pre-fix de 121 huérfanos se hizo contra `fallos_localizados_huerfanos.csv` del 30/4/2026 02:14, generado contra alguna versión anterior del catálogo (probablemente `catalogo_v14.csv`). El fix corrió contra `catalogo_v15.csv` actual. Las anomalías son producto de mejoras del catálogo entre fechas.

**Estado:** **pendiente de verificación en próxima sesión**. Hipótesis alternativa marcada como más probable.

**Implicancia:** antes de avanzar al parser, confirmar la causa de las anomalías. Si son del catálogo, son mejora gratuita. Si son del fix, son regresión silenciosa.

---

### H010 — Reorganizar el proyecto durante el fix

**Propuesta intermedia (descartada):** aprovechar la sesión para limpiar duplicados de scripts entre raíz y `paginas/`, mover archivos a estructura más clara.

**Decisión:** rechazada. Razones:
1. La reorganización masiva durante un fix puntual aumenta superficie de regresión.
2. Los scripts dependen de rutas relativas que cambian con la mudanza.
3. No hay validación post-mudanza programada.
4. Mejor reservar sesión dedicada para reorganización con backup completo previo.

**Estado:** decisión metodológica. Reorganización pendiente como ítem separado en `DEUDA_TECNICA.md`.

---

### H011 — Pasar de "página + traducción a línea" a "línea como primaria"

**Observación del usuario durante diagnóstico:** la arquitectura actual mezcla dos sistemas de coordenadas (página del catálogo + línea del archivo). Los clusters `pagina_no_en_mapa` y `pagina_fin_no_en_mapa` (82 casos) son errores de la traducción página↔línea, no de detección de contenido.

**Hipótesis:** si el pipeline trabajara siempre en líneas y la página fuera solo metadato de validación, esos 82 casos no existirían (la detección de inicio/fin se haría buscando patrones textuales directamente en el `.md`).

**Estado:** válido como diagnóstico arquitectónico. **Rechazado como acción para la sesión.**

**Implicancia:** anotado como mejora futura (propuesta v18). Refactorizar la unidad operativa elimina categóricamente dos clusters de bugs (82 casos), pero requiere validación del pipeline entero. No es trabajo de fix puntual.

---

### H012 — La sobrescritura del archivo viejo era recuperable

**Confusión durante operación de archivos:** intento de mantener trazabilidad histórica reconstruyendo el archivo original antes del fix.

**Realidad:** el archivo original (`cruzar_catalogo_y_mapa.py` de 13.624 bytes, 28/4/2026) fue sobrescrito durante la operación de reemplazo por el modificado. No quedó copia en snapshot porque el snapshot inicial solo cubría archivos de raíz, no de `paginas/`.

**Mitigación:** el diff completo entre original y modificado quedó en el output de la sesión. Si fuera necesario rollback, puede reconstruirse partiendo del modificado y revirtiendo cambios identificables.

**Lección:** snapshots deben cubrir TODO archivo que se vaya a modificar, no solo lo que se anticipa. Para futuras sesiones, regla: antes de tocar archivo X, copiar X al snapshot, sin importar si el snapshot inicial lo incluyó.

---

## Hallazgos de sesiones anteriores (resumen)

### Sesión 2026-05-01

- Catálogo v15 corrige bias de v14: `sin_dispositivo` -580, `unanime` +831, word count -5,6%.
- Fix349 aplicado a parser para Tomo 349 provisorio.

### Sesión 2026-04-30

- Rollback de v17_beta_v2 por regresiones en detección de dictámenes.
- Diagnóstico: el patrón "cabecera mayúsculas + dictamen embebido + FALLO DE LA CORTE SUPREMA" del régimen 2008-2011 requiere refactor más profundo que un patch puntual.

### Sesión 2026-04-29

- Generación inicial de `cruzar_catalogo_y_mapa.py`.
- Diagnóstico de Boston Cía. de Seguros (Tomo 331 p.7) como caso paradigmático del Bug A: cabecera en línea 58, dictamen líneas 97-230, fallo desde línea 232.

---

## Convenciones para entradas futuras

- Toda hipótesis durante diagnóstico se anota acá, válida o no.
- Estados posibles: `válido` / `invalidado` / `parcialmente válido` / `pendiente`.
- Se documenta evidencia, no solo conclusión.
- Las hipótesis invalidadas son tan importantes como las válidas — evitan repetición de caminos errados.
- Lecciones aprendidas (sobre proceso, no sobre contenido) van al final de cada sesión como bloque separado.

---

## Sesión 2026-05-06

### Nota: gap de bitácora 2026-05-02 a 2026-05-06

Las sesiones intermedias (2026-05-04 auditoría post-fix, 2026-05-05 diagnóstico Chabán) no fueron migradas a este archivo. Documentación de esas sesiones existe en `output/auditoria/auditoria_post_fix_2026-05-04.txt` y `output/auditoria/diagnostico_2026-05-05.md`. Pendiente migrar si se decide consolidar bitácora.

### H013 — El parser no separa sumarios editoriales del cuerpo del fallo

**Hipótesis inicial (heredada de memoria de proyecto):** "52 sumarios sj.csjn mal clasificados como fallos. Detector existe pero no captura el patrón."

**Evolución del diagnóstico durante la sesión:**

1. Verificación contra `auditoria_post_fix_2026-05-04.txt`: el número 52 no aparece en ningún archivo del repo. Origen del número no verificable.
2. Lectura de `parser.py`: `RE_SUMARIO_LINK` (L133) detecta una variante editorial específica (post-tomo 345, casos publicados solo como sumario con link al fallo online). 160 casos están clasificados como `tipo_entrada='sumario_con_link'`. El detector funciona para lo que pretende detectar.
3. El usuario observa: "son pocos sumarios para tanto fallo". Aclaración terminológica: hay dos cosas distintas llamadas "sumario":
   - **Sumario editorial**: resumen al inicio de cada fallo. Estándar editorial. Múltiples por caso.
   - **Sumario con link** (`tipo_entrada`): modalidad nueva post-345, no es un fallo, solo resumen + link.

**Hallazgo:** el parser solo tiene `linea_es_header_sumario` (L1065), heurística que detecta el INICIO de cada sumario editorial. Se usa exclusivamente como marcador de frontera entre casos en `detectar_fin_real`. NO extrae el sumario, NO detecta su fin, NO lo cuenta como entidad.

**Evidencia:** caso 329_p5 (LibroVol329.1.md, líneas 39-184). 2 sumarios editoriales al inicio, ambos con voz "RECURSO EXTRAORDINARIO:", atribución "–Del dictamen de la Procuración General–". Después dictamen, después fallo. La heurística actual identificaría las 2 líneas-título de sumario, pero no su contenido ni su fin.

**Implicación:** word count, considerando_text y métricas derivadas están sesgadas sistemáticamente para los 5659 casos con `tipo_entrada='fallo'`. Sesgo no marginal: si cada caso tiene en promedio 1-2 sumarios de 100-200 palabras, son cientos de miles de palabras de sesgo a través del corpus.

**Estado:** válido. Confirmado por usuario: "sobreestimé la capacidad de identificación de sumarios. Era solo el inicio. Eso rompe cualquier wc, cualquier estadística".

**Plan acordado:** abordar en 4 fases.

- **Fase 1**: exploración de variantes editoriales sin código. Mirar 5-8 casos representativos (simple, con disidencia, con votos concurrentes, con sumario que mencione disidencia, viejo 329-334, moderno 343-348, sumario_con_link).
- **Fase 2**: calibrar heurística inicio+fin sobre los casos vistos.
- **Fase 3**: medir cobertura sobre los 5819 casos del corpus.
- **Fase 4**: integrar al parser. Columnas nuevas: `lineas_sumario`, `n_sumarios`, `wc_sumario`, `wc_cuerpo`. Solo después de heurística validada.

---

### Hallazgos secundarios

**Diagnóstico parcial del índice general** (objetivo original de la sesión, no completado):

- Dos formatos editoriales distintos: viejo (329-334) en columna única con leaders de puntos, moderno (337+) con descripciones antes del header `INDICE GENERAL` y páginas después.
- El índice general es consolidado por tomo (cubre todos los volúmenes), no uno por volumen. Validado en 329, 334 (viejos) y 338, 343, 344 (modernos).
- En tomos modernos multi-volumen, cada volumen tiene una copia del índice general. Las copias divergen solo en paginación romana del aparato editorial. Las páginas árabes son idénticas entre copias del mismo tomo.
- Erratas editoriales detectadas: 343-2 dice `2328` donde 343-1 y 343-3 dicen `2327`. 349-1 dice `TOMO 348` en su `INDICE GENERAL` (errata real, no migración).
- Tomo 349 marcado como provisorio (publicación parcial, faltan volúmenes). Decisión: marcar con flag `tomo_estado='provisorio'` cuando se construya esa pieza, excluir de análisis estadístico.
- Detector actual de `tipo_indice='general'` en `construir_catalogo.py` corta rangos de manera inconsistente: en formato moderno corta antes de descripciones (las pierde), en formato viejo a veces solo agarra Volumen I cuando el índice cubre todos los volúmenes.

Trabajo del índice general queda en roadmap, no atacado en esta sesión.

### Reglas de trabajo fijadas en esta sesión (vigentes)

1. Nada de pseudocódigo ni pseudo-CSVs. Todo se contrasta contra archivos reales.
2. No asumir nada hasta tener el caso real en pantalla.
3. En pasos críticos, Claude pide explícitamente contrastar con `.md` o PDF original. En rutinarios, no.
4. Claude pide los archivos que necesita. No alucina.
5. Ojo humano sobre el dato vale más que cualquier parser. Para decisiones de diseño, mirar antes de codear.


## Sesión 2026-05-08

### H014 — Construcción de `auditar_fallo.py` (Fase 2 del plan H013)

**Contexto:** continúa H013 (parser no separa sumarios editoriales del cuerpo). El plan acordado tenía 4 fases. Esta sesión construyó la herramienta de la Fase 2: calibrar heurística sobre casos reales con código en lugar de inspección manual.

**Decisión arquitectónica previa al código:**

`auditar_fallo.py` no es solo herramienta de inspección. Materializa la **separación entre segmentación y extracción de features** que el parser actual no hace. El parser corre un solo loop sobre el bloque (parser.py L1513-1564) en el que mezcla detección de zonas con cómputo de features. Solo materializa `lineas_dictamen` como set de índices; las demás zonas existen como variables sueltas (`por_ello_idx`, `inicio_votos_indiv`, `marcadores_votos`) y se descartan después de emitir la fila del CSV. Por eso cuando una línea no encaja en ninguna heurística no falla ruidosamente: cae silenciosamente en `wc_mayoria` (línea 1585-1586).

`segmentar_bloque(bloque) -> list[Span]` materializa esa segmentación con invariantes verificables (cobertura exhaustiva + disjunción) y un span explícito `catch_all` para residuo. El catch_all es el instrumento de medición que faltaba.

**Decisiones de diseño cerradas durante la sesión:**

- **(B) Headers de página como partición transversal `header_pagina`**, no inclusivos en otros spans, no en catch_all. Los pares "número solo + frase institucional + tomo" se reconocen por cruce con `mapa_paginas.csv` + `RE_PAGE_HEADER`.
- **(C) Un span por sumario editorial**, no agrupados. Permite inspeccionar atribución de cada uno por separado (relevante para H3 de la tesis: unidad de ratio decidendi).
- **(D) Resolución de página en CLI**: match exacto si `pagina_inicio <= P <= pagina_fin`. Si `pagina_fin` está vacío, tope = `pagina_inicio` del siguiente caso menos 1, o `pagina_inicio + 50` si es último del tomo (defensivo).
- **(A) `metadatos_editoriales` como partición**: **diferida**. Aparece sistemáticamente al inicio del bloque (arrastre del fallo previo) y al final (cierre del propio fallo), pero no se subió a partición rígida sin medir frecuencia primero. Cae al catch_all hasta que la auditoría empírica lo confirme.

**Decisión de scope**: aclaratorias de la CSJN se ignoran. Frecuencia "0,0000111" según experiencia profesional de 25 años del usuario. Si aparecen, caen al catch_all. No justifica complejidad adicional en v1.

**Bugs de la propia auditoría detectados y fixeados durante validación contra texto real:**

1. `linea_es_header_sumario` del parser exige `.` o `:` o tener `:` en primeros 80 chars. Sivaslian usa `RECURSOS LOCALES` (sola, sin puntuación). Implementado `es_header_sumario_auditoria` propio en `auditar_fallo.py`, sin tocar el parser.
2. Detector de carátula confundía `ALEJANDRO CERBONI` (formato viejo, todo MAYÚSCULAS) con header de sumario. Refactor: si hay headers con `:`, la carátula es la línea anterior al primer header con `:`; si no, la línea anterior al primer header detectable.
3. `detectar_por_ello_mayoria` empezaba desde 0 cuando no había dictamen. Matcheaba "Por ello" del fallo previo arrastrado al inicio del bloque. Macri (349_p81) pasó de 46.54% residuo a 3.74%. Fix: empezar búsqueda desde `apertura_mayoria`.
4. Fin del dictamen pisaba el FALLO DE LA CORTE cuando el dictamen no termina con "Buenos Aires, fecha." en línea propia. Heurística del parser confundía la fecha del fallo con cierre del dictamen. Ajuste: si la línea previa a la fecha es `RE_APERTURA`, retroceder. Documentado: el parser tiene el mismo bug y va a inflar `wc_dictamen` en casos similares.

**Hallazgos confirmados sobre el parser (no fixeados, anotados):**

| ID | Hallazgo | Severidad | Migración recomendada |
|----|----------|-----------|----------------------|
| F001 | `RE_VOTO_HDR` no matchea `Voto la señora` (sin "de" antes del artículo). Voto de Argibay no se detecta. | Alta | Fix de 1 línea, validar en regeneración coordinada |
| F002 | `detectar_fin_real` extiende al fallo siguiente. Décima (349_p40): bloque incluye Y.P.F. c/ Mercante entero. Residuo 22%. | Alta | Requiere muestra mayor para diagnosticar |
| F003 | `detectar_fin_real` corta corto en último del tomo. Sivaslian (349_p306): pierde 2da línea de firma. | Media | Requiere muestra mayor |
| F004 | Arrastre de fallo previo al inicio del bloque (firma + metadatos editoriales del caso anterior). Sistemático en Sivaslian, Cerboni, Macri, Lavrentiev. | Sistemática | Decisión A pendiente, no migrar antes de medir |
| F005 | Fin del dictamen pisa el FALLO DE LA CORTE (mismo patrón que el bug interno del auditor). | Media | Mismo fix que ya está en auditor; validar en muestra |
| F006 | Sumarios editoriales no segmentados → contaminan `wc_mayoria`. | Sistemática | Es el motivo original de H013, requiere rediseño parser |

**Medición empírica de F001 (impacto del fix `RE_VOTO_HDR`):**

Script `medir_voto_hdr.py` corrido sobre los 2 archivos disponibles en sandbox (LibroVol331.2.md, LibroVol349-1.md):
- Regex viejo: 32 matches totales.
- Regex nuevo: 34 matches totales.
- Diff: 2 votos perdidos (ambos `Voto la señora ministra doctora doña Carmen M. Argibay` en tomo 331.2, líneas 957 y 11724).
- Verificados manualmente como votos reales, no falsos positivos.
- Pendiente: medir sobre corpus completo en Windows.

**Casos validados:**

| Caso | Tomo | Tipo | Residuo | Hallazgos |
|------|-----:|------|--------:|-----------|
| Sivaslian, Rosa | 349_p306 | Unánime, status `ok_cortado_en_indice` | 3.93% | Arrastre previo (F004), firma cortada (F003) |
| Cerboni, Alejandro | 331_p1028 | Voto separado de Argibay | 8.28% | Arrastre previo (F004), voto Argibay no detectado (F001), arrastre del fallo siguiente |
| Macri, Jorge | 349_p81 | Disidencia larga | 3.74% | Arrastre previo (F004) |
| Lavrentiev, Dmitri | 349_p28 | Sumarios consecutivos | 8.12% | Arrastre previo (F004) |
| Décima, Verónica | 349_p40 | — | 22.13% | `linea_fin_real` extiende al caso siguiente entero (F002) |
| Generación Zoe | 349_p75 | Caso simple | 0% | Sin hallazgos |

**Estado:** Fase 2 cerrada. Módulo en `scripts/auditoria/auditar_fallo.py`. Outputs en `scripts/auditoria/output/`. Cobertura y disjunción OK en todos los casos validados.

**Pendientes para próxima sesión (Fase 3):**

1. Correr `--random 50` sobre corpus completo en Windows. Medir distribución de residuo y patrones recurrentes en catch_all.
2. Decidir Decisión A (`metadatos_editoriales`) con muestra empírica.
3. Migrar al parser, en bloque, todos los fixes identificados (F001 y posiblemente F005 ya validados; F002-F004 según muestra).
4. Coordinar regeneración del corpus con los fixes migrados.

**No regenerar `csjn_casos.csv` antes de auditar más casos.** La auditoría no consume el output del parser, así que cambios en el parser no rompen la auditoría. Pero cada regeneración invalida análisis estadísticos que use el CSV. Conviene acumular fixes y regenerar una sola vez.

---


### H014 — extensión: muestra empírica `--random 50`

**Corrida:** `python scripts/auditoria/auditar_fallo.py --random 50` sobre el corpus completo (2026-05-08 16:23). Output en `output/auditoria/auditar_fallo/auditoria_2026-05-08_16-23-05.md` (28k líneas, 50 casos).

**Distribución de residuo:**

| Bucket | Casos | % de la muestra |
|--------|------:|----------------:|
| 0% | 6 | 12% |
| 0-2% | 8 | 16% |
| 2-5% | 9 | 18% |
| 5-10% | 11 | 22% |
| 10-20% | 11 | 22% |
| 20-50% | 5 | 10% |
| >50% | 0 | 0% |

**Agregado:** mediana 5.45%, residuo global 5.22%. Un 28% de la muestra (14 casos) está bajo 2% — la mayoría del corpus se segmenta razonablemente bien con la heurística actual del auditor.

**Top 5 con más residuo:**
- 333_p2420 (44.8%, Gómez c/ Alto Paraná)
- 330_p1854 (31.1%, Bongiovanni)
- 330_p2746 (30.0%, Mendoza c/ Nación Argentina — caso de Riachuelo)
- 341_p1617 (26.8%, Rojas c/ Alto Paraná)
- 341_p221 (23.1%, Amabile Cibils)

**Status:** los 50 casos sampleados son todos `status='ok'`. El sampleo no agarró ninguno de los 19 `ok_cortado_en_indice` (esperable — son <0.4% del corpus).

**Invariantes:**
- Cobertura: 50/50 OK.
- **Disjunción: 46/50 OK. Cuatro casos con disjunción rota** → bug del auditor identificado, ver F007 abajo.

### F007 (nuevo, bug del AUDITOR no del parser) — votos/disidencias del fallo previo arrastrado se emiten como spans semánticos del fallo actual

**Casos afectados (4/50):**
- 329_p2179 (disidencia del previo, 257 líneas que solapan carátula + 6 sumarios + dictamen del actual)
- 329_p4789 (voto del previo, 591 líneas)
- 342_p899 (disidencia del previo, 75 líneas)
- 333_p1619 (disidencia parcial del previo, 81 líneas)

**Causa:** `detectar_votos_y_disidencias()` en `auditar_fallo.py` busca matches de `RE_VOTO_HDR` y `RE_DISID_HDR` en TODO el bloque. Cuando el bloque arrastra contenido del fallo previo (F004), los headers de voto/disidencia del previo matchean y se emiten como spans del actual.

Resultado: el span aparece ANTES de la carátula del fallo actual, abarcando cientos de líneas, y solapa con todo lo que viene después (carátula, sumarios, dictamen). Disjunción FALLA.

**Fix conceptual (no implementado):** `detectar_votos_y_disidencias` debería usar la carátula como límite inferior. Cualquier match ANTES de `caratula_rel` es residuo del previo, no semántica del actual. Esto requiere reordenar la pipeline de `segmentar_bloque`: detectar carátula PRIMERO, después detectar votos solo desde caratula+1.

**Severidad:** baja en términos cuantitativos (4/50 = 8% de los casos), pero alta en términos de confiabilidad: cuando ocurre, el span erróneo se come ~50% del bloque y oculta la estructura real. Las invariantes del auditor delataron el problema sin necesidad de inspección manual.

**Estado:** pendiente fix. La invariante de disjunción sigue siendo útil exactamente para estos casos: garantiza que el bug se detecta automáticamente.

---

### H015 — Estrategia de promoción del auditor al parser

**Pregunta planteada por el usuario:** si el auditor termina siendo mejor que el parser (más heurísticas validadas, mejor segmentación), ¿no es más simple promoverlo a parser que ir parchando el parser fix por fix?

**Argumentos a favor de promover el auditor:**
- El auditor ya implementa el rediseño arquitectónico que la BITACORA H013/H014 identifica como necesario (separación de segmentación y extracción de features).
- Parchar el parser fix por fix conserva su deuda técnica (heurísticas mezcladas con cómputo de features).
- Es trabajo evolutivo razonable: prototipo paralelo que supera al sistema en producción.

**Argumentos en contra (lo que el parser tiene y el auditor no):**
- El parser emite `csjn_casos.csv` y `csjn_casos_votos.csv` en el formato que la tesis ya consume. El auditor emite spans, no CSVs.
- El parser está validado contra los 5819 casos hace meses. Sus números (con sus bugs) están medidos.
- El parser tiene heurísticas calibradas que el auditor no replica: `classify_outcome`, `clasificar_tipo_voto` (Tipo A/B/C/D/E), `es_originaria`, word counts, parseo de firma. Cientos de líneas de código.

**Decisión: promoción gradual con punto de inflexión a evaluar.**

Cuatro fases:

1. **Fase de auditoría (actual).** El auditor evoluciona heurísticas mejores, los overrides `_auditoria` se acumulan validados.

2. **Migración seleccionada.** Los overrides validados se migran al parser uno por uno, priorizando los de mayor impacto.

3. **Punto de inflexión.** Cuando la diferencia entre auditor y parser sea principalmente arquitectónica (segmentación + extracción), evaluar: construir un parser nuevo (v18 o v19) sobre la arquitectura del auditor, importando del parser actual las funciones de cómputo (classify_outcome, clasificar_tipo_voto, es_originaria, word counts).

4. **Validación cruzada y deprecación.** Parser nuevo corre sobre el corpus, comparar salidas con `csjn_casos.csv` actual, las diferencias deben ser explicables por los bugs identificados. Si pasa, parser viejo a `historial/`.

**Convención operativa para la fase 1:**
- Cada override del auditor se nombra con sufijo `_auditoria` (ej: `es_header_sumario_auditoria`).
- Cada override lleva docstring con: razón del override, diferencia con el original, ID en BITACORA, estado de validación.
- Compromiso de migración periódica: cuando hay 5 overrides validados, se migran en bloque coordinado.
- El auditor NO es un parser sombra. Si acumula 30+ overrides indefinidamente, es señal de que estamos esquivando la migración.

**Estado:** decisión metodológica. Aplicable desde ahora.

---


### H016 — Punto ciego: la auditoría no detecta amputaciones del bloque

**Contexto:** pregunta del usuario al cierre de sesión 2026-05-08. ¿Puede haber contenido del fallo que el auditor no procese porque el bloque ya viene cortado por el parser?

**Respuesta: sí, sistemáticamente.** Y las invariantes actuales del auditor (cobertura + disjunción) **no detectan** este tipo de error por construcción.

**Diagnóstico:**

El auditor recibe un bloque delimitado por `(linea_inicio, linea_fin_real)` donde:
- `linea_inicio` viene del catálogo (`catalogo.csv`).
- `linea_fin_real` lo computa `detectar_fin_real()` del parser sobre el bloque del catálogo.

Si cualquiera de los dos límites está mal puesto, el bloque que llega al auditor está amputado o inflado. El auditor procesa correctamente lo que recibe (cobertura=OK, disjunción=OK), pero **no tiene cómo saber qué quedó afuera**.

**Tres puntos del pipeline donde esto puede ocurrir:**

1. **Catálogo (`construir_catalogo.py`)**: si la detección de `linea_inicio` falla, contenido pre-carátula queda fuera del bloque desde la base.
2. **Localizador (`cruzar_catalogo_y_mapa.py`)**: huérfanos, casos `pagina_no_en_mapa`, `fallo_cruza_archivos`. Lo que entra mal localizado al parser nunca llega al auditor.
3. **`detectar_fin_real()` del parser**: F002 (extiende de más, contamina el bloque con el fallo siguiente) y F003 (corta de menos, pierde firma multi-línea o metadatos editoriales finales). Ambos ya identificados en H014.

**Implicancia metodológica:** el residuo del catch_all es una **cota inferior del error**, no un estimador. Si el catch_all reporta 5%, el error real puede ser 5% o más alto. La auditoría hoy detecta solo errores **dentro del bloque recibido**, no errores **del recorte del bloque**.

**Implicancia para tesis:** las cifras finales del Capítulo 4 (frecuencia de unanimidad/concurrencia/disidencia, word counts por tipo de voto, etc.) requieren validación adicional sobre el .md original, no sólo sobre el bloque parseado.

**Tres mitigaciones posibles, en orden de costo:**

1. **Detector de amputación inferior automatizado.** Función nueva en el auditor que mire si hay líneas entre `linea_fin_real` y la próxima carátula detectable en el .md. Si las hay, reportar como `posible_amputacion_fin`. Costo bajo. Detecta F003 sistemáticamente.
2. **Expansión de contexto en el output.** Incluir 30 líneas previas a `linea_inicio` y 30 posteriores a `linea_fin_real` rotuladas como `contexto_previo`/`contexto_posterior`. Costo medio. El humano detecta amputaciones por inspección visual.
3. **Auditoría estratificada con ojo humano sobre .md/PDF original.** Muestra de N casos comparados manualmente contra fuente. Costo alto. Es el único método que cubre los tres puntos del pipeline simultáneamente.

**Estado:** registrado como hallazgo metodológico. No hay fix de código en esta sesión. Para próxima sesión, decidir si implementar mitigación 1 antes de avanzar con F007 u otros fixes.

**Implicancia para H015:** el auditor, en su forma actual, **no es candidato a reemplazar al parser** sin antes resolver este punto ciego. Un parser nuevo sobre la arquitectura del auditor heredaría el mismo problema de heredar bloques mal recortados, salvo que se rediseñe la entrada (operar sobre el .md crudo, no sobre el bloque pre-cortado).

---


## H017 — 2026-05-09 — Diseño detector de amputación inferior (H016): decisión de scope y heurística de firma multilínea

**Contexto.** Sesión de diseño previo a implementación. Objetivo: definir el detector de amputación inferior planteado en H016, considerando el horizonte de uso (tesis maestría / doctorado / producto) más amplio que solo el corpus 344-349.

**Decisión 1 — Horizonte de diseño.** Se descarta optimizar el detector solo para tesis. La tesis ya tiene cifras suficientes sin H016 resuelto. El detector se diseña pensando en doctorado y eventual aplicación comercial. Implica: clasificaciones del gap con confiabilidad medible, no solo conteo agregado.

**Decisión 2 — Variante elegida.** Se descarta variante 1 (detector pasivo puro) y variante 3 (detector + reclasificación con extensión del bloque). Se adopta variante 2 (detector activo con clasificación tipada del gap), justificación: variante 1 es insuficiente para doctorado, variante 3 acopla el auditor al estado actual del parser que tiene F001-F006 sin migrar.

**Decisión 3 — Tipos de span en clasificador del gap (iteración 1).** Tres tipos: `firma_arrastrada` (multilínea), `header_pagina`, `no_clasificable`. Se posponen para iteración 2: `voto_arrastrado`, `disidencia_arrastrada`, `metadata_editorial`. Razón para posponer: voto/disidencia requieren detección de cuerpo multi-párrafo; metadata editorial requiere validación con caso real donde aparezca (no aparece en corpus 339+, aparente reformateo editorial).

**Decisión 4 — Alertas estructurales.** Se incorporan dos alertas que salen al revisar caso real 339_p1648: `firma_truncada_en_silabacion` (última línea del span firma del bloque no termina en punto, termina en nombre propio aislado — indicador casi gratuito de amputación) y `caratula_siguiente_detectada_antes_de_linea_inicio_proximo_caso` (señal de bug en catálogo).

**Hallazgo F008 — off-by-one entre auditor y .md.** Al validar caso 339_p1648 contra LibroVol339_2.md se detecta inconsistencia: el span 17 del reporte de auditoría dice `firma (26598-26598)` con texto "Ricardo Luis Lorenzetti – Elena I. Highton de Nolasco – Juan", pero la línea 26598 del .md real es "mencionada localidad bonaerense." (la firma está en 26599-26600). Hay un off-by-one en el renderer absoluto/relativo del auditor o un bug real en cálculo de offsets. Pendiente investigar en próxima sesión, no bloqueante para H017.

**Decisión 5 — Heurística de firma multilínea: límite estructural, no de líneas.** Inicialmente se propuso "≤80 char + 1-3 líneas". Corrección sustantiva del usuario: la CSJN tuvo composición de 9 ministros (1990-2006), 7 ministros (2006-2014), 5 ministros (2014+), más conjueces frecuentes y disidencias firmadas separadamente. Una firma puede ocupar 3-5+ líneas legítimamente. Diseñar para corpus 344-349 (5 ministros) sería miopía: el sistema apunta a aplicarse a períodos anteriores y posteriores con composiciones desconocidas a priori. Se reformula la heurística: el span de firma_arrastrada se extiende mientras la línea matchee criterios de firma, y se cierra solo por **límites estructurales duros**: RE_PAGE_HEADER, linea_es_header_sumario, RE_VISTOS_LOS_AUTOS, RE_APERTURA, carátula del próximo caso, RE_VOTO_HDR/RE_DISID_HDR (que cierra firma y abre alerta separada), línea en blanco terminal (con lookahead de 1 línea para captar separador entre firma de mayoría y firma de disidencia). NO hay tope arbitrario de N líneas.

**Implementación pendiente.** No se codeó nada esta sesión. Toda la discusión es de diseño. Próxima sesión arranca con codificación dentro de `auditar_fallo.py` (sección nueva `# ── Detección de amputación inferior (H016) ──`), seguido de validación contra caso 339_p1648 y luego corrida `--random 50` con detector activo.

**Archivos analizados esta sesión.**
- `scripts/auditoria/auditar_fallo.py` (estado actual del módulo).
- `output/localizacion/fallos_localizados.csv` (validación de columna `linea_inicio` como ancla del próximo caso).
- `scripts/pipeline/parser.py` (regex disponibles, JUECES_CONOCIDOS, linea_es_firma_de_juez, detectar_fin_real).
- `output/auditoria/auditar_fallo/auditoria_2026-05-08_16-23-05.md` (corrida --random 50 anterior).
- `corpus/LibroVol339_2.md` líneas 26595-26660 (caso paradigmático 339_p1648).

**Prioridades reordenadas para siguiente sesión.** A1 = codear el detector según diseño consolidado en H017. A2 = validar contra 339_p1648 y otros 4-5 casos de la corrida anterior. A3 = corrida `--random 50` con detector activo. B-D = sin cambios respecto a H016 (F007, casos >20%, F001).


## H018 — 2026-05-09 · Sesión de diseño del detector de borde inferior. Decisiones consolidadas. Implementación pospuesta a próxima sesión.

Sesión larga de diseño y validación previa contra archivos reales. NO se
implementó código en esta sesión; se acumuló contexto suficiente para
codear de una sola vez en sesión limpia. El plan original H017 era
implementar el detector de "amputación inferior", pero la sesión derivó
en discusión de scope, helper, alertas y lógica de clasificación. Al
final hubo confusión acumulada por el contexto saturado (Claude entregó
un `.py` separado cuando se había acordado integración directa, y empezó
a crear archivo modificado fuera del flujo). Se decide cerrar acá y
retomar limpio.

Lo que sí queda registrado en esta entrada: las decisiones de diseño
tomadas, los hallazgos nuevos detectados al validar contra archivos
reales, y los puntos pendientes para la próxima sesión.

### Renombre del detector

Se descarta "amputación inferior" (excesivamente gráfico) y se adopta
**`borde_inferior`**. El nombre cubre los estados posibles del borde
entre el fallo actual y el próximo del catálogo: continuo,
header_normal, gap_con_residuo, gap_grande_solo_headers,
solapado_con_proximo, fin_archivo. Es geográfico, no direccional ni
violento.

### Verificación del caso paradigmático contra archivos reales

El prompt de continuación 2026-05-09 declaraba que `339_p1648` tenía
firma cortada en "Juan" sin "Carlos Maqueda." y un gap de líneas
26599-26604. Verificación contra `LibroVol339_2.md`:

- La firma cierra completa en línea 26599 (`Carlos Maqueda.`). NO está
  amputada.
- `detectar_fin_real` del parser corta en línea 26598 (off-by-one):
  reconoce la firma pero no extiende el fin sobre la silabación.
- El catálogo dice `linea_fin=26634` para 1648, pero el contenido real
  termina en 26599. Las líneas 26605-26634 ya pertenecen a 339_p1651.

El detector que diseñamos sí captura este caso vía la alerta
`firma_multilinea_partida_por_fin_real` (delta=4, primera línea no
vacía del gap es firma_arrastrada).

### Decisiones de diseño consolidadas

**1. Versión simple primero, robusta documentada en código como
reserva.** La simple es una resta entre `linea_inicio_proximo_caso` y
`linea_fin_real` con clasificación de las líneas del gap. La robusta
(con ventana de búsqueda de cierre estructural alrededor de
`linea_fin_real`) queda documentada para activarse si la corrida
`--random 50` muestra > 10% de falsos positivos por bugs heredados
del parser.

**2. Helper de detección de firma con apellidos canónicos**
(`linea_es_continuacion_firma`). Set:
```
APELLIDOS_FIRMA_TITULARES = {
    "ROSATTI", "ROSENKRANTZ", "LORENZETTI", "MAQUEDA",
    "HIGHTON", "NOLASCO", "MANSILLA",
    "ZAFFARONI", "PETRACCHI", "ARGIBAY", "FAYT",
    "BOGGIANO", "BELLUSCIO", "LÓPEZ", "LOPEZ",
    "VÁZQUEZ", "VAZQUEZ", "NAZARENO",
}
```
Solo titulares, sin conjueces (decisión avalada por contexto Elías).
Apellidos compuestos (Highton/Nolasco, García-Mansilla) proveen
redundancia natural contra OCR sucio. Cero tolerancia OCR explícita
en esta iteración.

Criterio del helper: presencia de apellido del set + compatibilidad
discursiva (mayúsculas dominantes ≥70%, o línea ≤80 chars terminada
en punto/raya, o presencia de em-dash). Validado contra
LibroVol329_2.md (72k líneas): 1646 detectadas correctamente vs 222
no-detectadas, todas las no-detectadas son discursivas legítimas.

**3. Lógica de clasificación: el contenido decide el estado, no solo
el delta.** El detector siempre clasifica las líneas del gap por
contenido. Si hay líneas no benignas (distintas a vacía/header_pagina),
estado=gap_con_residuo independiente del delta. Si todas son benignas
y delta ≤ UMBRAL_GAP_RESIDUO (=4), estado=header_normal. Si todas son
benignas y delta > UMBRAL, estado=gap_grande_solo_headers. Esto
corrige una versión inicial que dependía solo del umbral y dejaba
escapar 339_p1648 (delta=4 caía en header_normal).

**4. Regla de coherencia: apellido titular repetido en span contiguo
de firma_arrastrada = bug del detector.** Validado empíricamente: en
LibroVol329_2 (72k líneas) cero casos legítimos de repetición. La
firma de mayoría es disyuntiva por construcción institucional. Alerta
`apellido_repetido_en_firma_arrastrada` con cierre estructural duro
del span.

**5. Render condicional con resumen global.** En cada caso del reporte
solo se renderiza la sección de borde inferior si hay anomalía (estados
gap_con_residuo, solapado_con_proximo, gap_grande_solo_headers) o
alertas. En el header del documento se agrega línea agregada con
resumen global de los estados (N continuos · M header_normal · K
gap_con_residuo · L solapados · F fin_archivo).

**6. Umbral inicial: `UMBRAL_GAP_RESIDUO = 4`.** Cubre 1 vacía + header
de página de hasta 3 líneas. Constante reversible.

**7. Próximo caso del MISMO ARCHIVO (no del mismo tomo).** Un tomo se
divide en varios archivos `.md`. La cota del detector usa
`fila["archivo"]` como filtro, no solo `fila["tomo"]`. El cálculo se
hace iterando `filas_loc` filtradas por archivo y ordenadas por
`linea_inicio`.

### Estructura del output del detector

```python
"borde_inferior": {
    "linea_fin_real": int,
    "linea_inicio_proximo_caso": int | None,
    "delta": int,
    "estado": "continuo" | "header_normal" | "gap_con_residuo"
              | "gap_grande_solo_headers" | "solapado_con_proximo"
              | "fin_archivo",
    "lineas_gap": [
        {"linea_abs": int, "clasificacion": str, "texto": str},
        ...
    ],
    "alertas": [str, ...]
}
```

Clasificaciones de líneas del gap (cuando estado != continuo/header_normal/fin_archivo):
- `vacia`
- `header_pagina` (matchea RE_PAGE_HEADER o está en mapa de headers)
- `firma_arrastrada` (apellidos titulares + criterio discursivo)
- `voto_disidencia_individual` (RE_VOTO_HDR o RE_DISID_HDR)
- `apertura_proximo_caso` (RE_VISTOS_LOS_AUTOS o primer_token_siguiente)
- `no_clasificable` (catch-all)

Alertas posibles:
- `firma_multilinea_partida_por_fin_real`
- `apellido_repetido_en_firma_arrastrada`
- `voto_disidencia_individual_en_gap`
- `caratula_siguiente_en_gap`
- `gap_grande_solo_headers` (cuando aplica)

### Hallazgo nuevo: F010 — off-by-one de detectar_fin_real en firmas multilínea

Caso paradigmático 339_p1648. La firma se extiende líneas 26598-26599
con silabación ("Juan / Carlos Maqueda."). `detectar_fin_real` reporta
linea_fin_real=26598. El detector de borde inferior captura esto vía
alerta `firma_multilinea_partida_por_fin_real`. F010 es bug del parser
(`detectar_fin_real`), no del auditor. Investigación queda para sesión
separada. Prioridad alta.

### Hallazgo nuevo: F011 — catálogo de localización con linea_fin extendido

Caso paradigmático 339_p1648. Catálogo dice fin=26634, pero contenido
real termina en 26599. Las líneas 26605-26634 ya pertenecen al fallo
339_p1651 (sumarios + dictamen de "Diez, Ernesto Osvaldo"). NO es
problema del detector de borde inferior. Es del proceso de
localización/catalogación. Investigación separada. Prioridad media.

### Hallazgo descartado: F009

Test inicial sugería que RE_VOTO_HDR/RE_DISID_HDR no cubrían formato
pre-2015 ("DOCTORA DOÑA ELENA..."). Verificación posterior mostró que
los regex SÍ matchean los headers reales del libro viejo
("VOTO DE LA SEÑORA VICEPRESIDENTA"); el caso falso del test inicial
era una línea SUBSIGUIENTE al header (continuación, no header).
F009 retractado, no se registra como bug.

### Cuestión abierta para próxima sesión: alerta de líneas vacías consecutivas

Validación empírica:
- LibroVol339_2.md: 898 runs de 1 vacía / 3 runs de 2 vacías / cero
  de 3+. Los 3 runs de 2 vacías son transiciones macro del libro
  (título, índice, apéndice).
- LibroVol329_2.md (72k líneas): 1836 runs de 1 vacía / cero de 2+.

Conclusión: entre fallos contiguos del catálogo, lo normal es 0-1
línea vacía. 2+ vacías seguidas es estadísticamente muy raro y
anómalo. Propuesta: agregar alerta `vacias_consecutivas_anomalas`
con umbral `UMBRAL_VACIAS_CONSECUTIVAS = 2`. Decisión final queda
para sesión de implementación.

### Plan de validación post-implementación (próxima sesión)

1. Caso paradigmático 339_p1648 debe reportar:
   - estado: gap_con_residuo
   - delta: 4
   - lineas_gap: 4 entradas (firma_arrastrada L26599 + vacia L26600
     + header_pagina L26601 + header_pagina L26602)
   - alerta: firma_multilinea_partida_por_fin_real (apunta a L26599)

2. Comparación con corrida `--random 50` previa
   (`auditoria_2026-05-08_16-23-05.md`).

3. Corrida nueva `--random 50` con detector activo. Cifras agregadas
   esperadas (a contrastar con datos):
   - ~70-85% header_normal
   - ~5-15% gap_con_residuo
   - ~5-10% continuo
   - ~5-10% fin_archivo
   - <5% solapado_con_proximo

### Pendientes ordenados por prioridad para próximas sesiones

- **Próxima sesión**: implementar `borde_inferior` integrado dentro
  de `auditar_fallo.py` (NO archivo separado). Validar contra
  339_p1648. Corrida `--random 50`. Decidir versión robusta según
  datos.
- F010 (alta): off-by-one de detectar_fin_real en firmas multilínea.
  Sesión separada del parser.
- F011 (media): catálogo extendido sobre próximo caso. Sesión
  separada del proceso de localización.
- F008 (preexistente): off-by-one entre reporte del auditor y líneas
  reales del .md. Sesión separada.
- F007 (preexistente): detectar_votos_y_disidencias no respeta
  carátula como límite inferior.
- 5 casos con residuo >20% sin investigar: 333_p2420, 330_p1854,
  330_p2746, 341_p1617, 341_p221.
- Decisión A pendiente: metadatos_editoriales como partición rígida
  o no.

---

## Sesión 2026-05-09 (continuación nocturna) — Validación empírica de H018 con `--random 80`

Sesión corta de validación post-implementación del detector de borde
inferior (H018, implementado 2026-05-10 según header del script). Se
corrió `--random 80` sobre el corpus completo y se contrastó la
distribución observada con la predicción registrada en H018. Resultado
principal: la predicción no se cumple. Adicionalmente, la inspección
caso por caso reveló dos hallazgos nuevos no registrados en bitácora.

### Resultados de la corrida `auditoria_2026-05-09_17-41-42.md`

- 80 casos auditados, todos con `status_localizacion=ok`.
- 23.895 líneas de bloques totales, 819 líneas de residuo.
- Residuo global: **3,43%** (media). Mediana 3,00%, p75 8,14%, p90 17,12%.
- 7 casos con `disjunción=FALLA` (no solo el outlier de residuo alto).

### Distribución observada vs predicción de H018

| Estado | Predicción H018 | Observado | Delta |
|---|---:|---:|---|
| `header_normal` | 70-85% | **0%** | desplome |
| `gap_con_residuo` | 5-15% | 10% | dentro de rango |
| `continuo` | 5-10% | 0% | ausente |
| `fin_archivo` | 5-10% | 0% | ausente |
| `solapado_con_proximo` | <5% | **90%** | sobre-disparo |

La predicción y la realidad están invertidas en los dos estados
extremos. `header_normal` (transición editorial limpia, esperado como
caso típico) **no apareció en ningún caso**, mientras que
`solapado_con_proximo` (anomalía esperada como marginal) apareció en
72/80 = 90%.

Inspección caso por caso confirma que el `solapado_con_proximo`
dispara incluso en casos visualmente sanos. Ejemplo: `349_p1` tiene
residuo 0%, cobertura OK, disjunción OK, estructura completa
(mayoría + 2 votos), y aun así borde inferior reporta
`solapado_con_proximo` con `delta=-12`.

### Hipótesis sobre la calibración

`fin_extendido_pag_compartida` apareció como pista de corte en 72/80
casos (idéntica frecuencia que `solapado_con_proximo`). Esto sugiere
que **ambos estados son la misma cosa vista desde dos ángulos**: el
parser extiende `linea_fin` hasta la carátula del próximo (porque
detecta página compartida) y el detector de borde inferior lo lee
como solapamiento. La página compartida es la regla en el formato
editorial Fallos, no la excepción.

La predicción de H018 estaba implícitamente pensando en transiciones
con header de página intermedio (3 líneas editoriales seguidas:
número de tomo, número de página, "DE JUSTICIA DE LA NACIÓN" o
"FALLOS DE LA CORTE SUPREMA"). En la práctica, el patrón dominante
parece ser página compartida sin header completo intermedio, lo que
hace que `header_normal` sea poco frecuente.

**Cuestión abierta**: ¿la calibración de H018 era ingenua o el
detector está clasificando como `solapado` cosas que deberían ser
`header_normal`? Decisión pendiente para próxima sesión.

### F012 (nuevo) — Firma multilínea partida por header de página intra-bloque cae a catch_all

**Caso testigo**: caso del tomo 329 (visto durante inspección de
auditoría, span 53). Pattern observado:

```
Línea N:   ...— Carmen           <- final del span firma
Línea N+1: 329                   <- header_pagina
Línea N+2: <num pag>             <- header_pagina
Línea N+3: DE JUSTICIA...        <- header_pagina
Línea N+4: M. Argibay.           <- ESTA cae a catch_all
```

La cola de la firma (`"M. Argibay."`) cumple los criterios de
`linea_es_continuacion_firma()`: contiene apellido titular
(`ARGIBAY`), longitud ≤80, termina en punto. El detector funcionaría
bien si se aplicara acá. **El problema no es el detector — es dónde
se aplica**: hoy solo se invoca en el borde inferior (transición
entre fallos), no en transiciones intra-bloque por header de página.

Diferencia con F007: F007 es contaminación cross-bloque del fallo
**previo** invadiendo el bloque del actual. F012 es fragmentación
intra-bloque del fallo **actual** por inserción editorial de header
de página entre líneas semánticamente continuas.

**Fix conceptual (no implementado)**: aplicar
`linea_es_continuacion_firma` también dentro del bloque, no solo en
el borde inferior. Probablemente como paso de post-procesamiento
sobre los catch_all de 1-3 líneas que están entre un span de firma y
el siguiente span semántico, cuando todas las líneas del catch_all
son apellido titular o header de página.

**Severidad**: baja en residuo (1-3 líneas por caso), pero sistemática
(ocurre cada vez que firma multilínea atraviesa salto de página). En
la corrida de 80, la cola larga de residuo (p90=17%) probablemente
está alimentada parcialmente por F012 acumulado.

### Hallazgo abierto — Acordadas, resoluciones y discursos como tipo de documento distinto al fallo

Detectado conceptualmente (no en caso testigo concreto de esta
corrida). Los tomos de Fallos contienen, además de sentencias,
acordadas (actos institucionales de la Corte), resoluciones
administrativas y eventualmente discursos de apertura del año
judicial. El catálogo (Etapa 2) a veces los lista como entradas y a
veces no. El parser asume que toda entrada del catálogo es un fallo
y aplica heurísticas de fallo (RE_APERTURA, considerando, dispositivo,
firma).

Cuando una entrada es acordada o discurso, esas heurísticas no
matchean y el caso cae sin estructura. Caso visto en sesión:
`342_p1313` ("Integración Eléctrica Sur c/ EN-AGIP"). Resultó ser
**fallo regular**, no acordada — los sumarios doctrinales tenían
header `"ACORDADA 4/2007"` como voz temática (norma citada por el
fallo), pero la pieza era un fallo común con `FALLO DE LA CORTE
SUPREMA`. **El hallazgo queda abierto sin caso testigo confirmado**:
hace falta ver si el catálogo realmente lista acordadas como
entradas, o si las excluye de raíz.

**Acción pendiente**: cuando aparezca el primer caso real (entrada
del catálogo que no es fallo), registrar como F013 o equivalente.

### Hallazgo accesorio — `disjunción=FALLA` es más frecuente de lo esperado

7/80 casos (8,75%) tienen `disjunción=FALLA`, no solo los outliers
de residuo alto. Cinco de los siete tienen residuo bajo (≤8%):
`330_p2064` (5,8%), `344_p983` (0,0%), `331_p2827` (1,1%),
`329_p2946` (3,6%), `329_p2944` (8,1%), `329_p513` (0,0%).

Particularmente extraño: `344_p983` y `329_p513` con residuo 0% y
disjunción rota — cobertura completa sin residuo, pero spans que se
pisan. Probable F007 (detectar_votos_y_disidencias arrastrando
contenido del previo y solapando con la carátula del actual). No
investigado en detalle.

### Pendientes ordenados por prioridad — actualización post-validación

- **Decisión H018**: con `solapado_con_proximo=90%` la métrica
  pierde poder de filtrado. Dos opciones para próxima sesión:
  (a) recalibrar — entender qué constituye un solapamiento "real"
  (con residuo) vs solapamiento estructural (página compartida sin
  residuo); o (b) eliminar el estado y reemplazarlo por una métrica
  binaria (residuo en gap sí/no).
- **§4.6.b RE_CONSIDERANDO** (PIPELINE_HALLAZGOS.md, prioridad
  alta): fix de regex ya validado, sin aplicar. Una línea de
  cambio. Caso testigo confirmado en validación: `344_p2835` (80%
  residuo, considerando con prefijo "Vistos los autos;
  Considerando:" no detectado, todo el cuerpo cae a catch_all).
- **F010** (alta): off-by-one de detectar_fin_real en firmas
  multilínea. Confirmado adicional en `348_p955` ("Lorenzetti."
  como cola sin reconocer) y `339_p488` (efecto cascada por
  contaminación del fallo previo). Sesión separada del parser.
- **F012** (nueva): firma multilínea partida intra-bloque cae a
  catch_all. Fix conceptual conocido. Sesión separada.
- **F011** (media): catálogo extendido sobre próximo caso. Sesión
  separada del proceso de localización.
- **F008, F007** (preexistentes).
- **5 casos con residuo >20% sin investigar** (lista preexistente):
  333_p2420, 330_p1854, 330_p2746, 341_p1617, 341_p221.
- **Sesgo por tomo confirmado**: tomos viejos (329-333) concentran
  residuo, tomos modernos (345+) son casi limpios. El parser está
  optimizado para formato editorial moderno.
- Acordadas/discursos como tipo distinto: hallazgo abierto, sin
  caso testigo. Anotar cuando aparezca.

## Sesión 2026-05-10 — Lectura del código y refinación de hallazgos

Continúa la sesión nocturna del 09/05. La sesión anterior había validado H018 con `--random 80` y registrado la calibración fallida del detector de borde inferior (mediana de residuo OK pero `solapado_con_proximo` disparando en 90% de los casos, contra los <5% esperados). El diagnóstico de la sesión anterior fue mecánico pero parcial: identificó que el delta sale negativo cuando el parser usa `caratula_siguiente`, pero atribuyó la falla a la calibración de H018.

La presente sesión avanzó por dos pasos: primero auditoría manual de los cinco casos pendientes de residuo alto (333_p2420, 330_p1854, 330_p2746, 341_p1617, 341_p221), después lectura del código real de `auditar_fallo.py` y `parser.py` para chequear cada conclusión preliminar contra la implementación. La lectura del código corrigió varias afirmaciones de la sesión anterior y precisó la causa-raíz de tres bugs.

### Resultados empíricos de los cinco casos

Ninguno superó el umbral del 20% de residuo declarado en BITACORA H018. El mayor fue 341_p221 con 17,09%; 341_p1617 bajó a 0,41%. Esto pone en duda la lista misma — los outliers de "más de 20%" deben provenir de una corrida anterior al random-80 cuyo registro no se preservó. Cuadro resumen:

| Caso (línea_inicio_real) | Residuo | Diagnóstico |
|---|---|---|
| `333_p2410` | 4,64% | F007 entrada + F012 (firma cortada) + disidencia glotona (no visible al auditor) |
| `330_p1849` | 12,95% | F007 entrada + R-postfirma + F007 salida |
| `330_p2739` | 10,13% | **F013 candidato**: parser corta caso al final del dictamen, omite cuerpo de mayoría + firma |
| `341_p1611` | 0,41% | Sano. `solapado_con_proximo` con delta=-15 puro estructural |
| `341_p218` | 17,09% | F012 (firma cortada por header) + R-postfirma |

### Hallazgos refinados con base en el código

**Sobre `solapado_con_proximo` y H018.** La sesión anterior leyó el detector de borde inferior y atribuyó la falla a su calibración. La lectura de `detectar_fin_real` (parser.py, línea 1153) corrige la atribución: la métrica geométrica del borde inferior no falla por calibración propia, falla porque mide contra una decisión semántica del parser que es estructuralmente prospectiva. Las cuatro pistas de `detectar_fin_real` priorizan referencias al fallo siguiente (carátula_siguiente, sumario_siguiente, marcador_apertura_siguiente), y la firma del propio fallo es solo fallback. Cuando la pista 1 acierta y la carátula del siguiente está físicamente debajo de la firma del actual (página compartida, patrón editorial estándar), `linea_fin_real > linea_inicio_proximo_caso` por construcción, y delta resulta negativo. El estado `solapado_con_proximo` mide geometría correctamente — lo que no captura es que esa geometría es la norma, no la patología. Para que la métrica recupere poder de filtrado, tendría que ajustarse al pista usada por `detectar_fin_real` (si pista=`caratula_siguiente`, esperar delta negativo y no alarmar).

**F013 con causa-raíz mecánica: caso 330_p2739.** El parser corta el caso al final del dictamen (`linea_fin_real=54297`, `status=fin_dentro_bloque`, pista=`caratula_siguiente`). El span de dictamen también termina en 54297. La lectura del código revela que la pista 1 hace búsqueda hacia atrás dentro del bloque (`buscar_atras(es_caratula, lfc, li + 5)`) usando un regex sobre primer_token. Cuando ese token aparece como mención dentro del cuerpo del dictamen, la pista 1 matchea ahí y corta. Después `construir_bloque_desde_localizacion` recibe `linea_fin_real` como tope, el bloque queda truncado, y `segmentar_bloque` trabaja sobre lo que sobrevive — sin ver el cuerpo de la mayoría ni la firma que vienen después de 54297. El bug se manifiesta en cadena pero la causa-raíz es la pista 1 con falso positivo. Pendiente de confirmación: chequear el .md crudo entre líneas 54165–54297 para identificar la mención que disparó el match.

Caracter sistémico: esto es invisible al auditor. La invariante de cobertura da OK porque cubre el bloque truncado. La de disjunción también, porque ningún span se pisa con otro dentro del rango truncado. **Solo la inspección humana detecta que falta el dispositivo del fallo.** El blind-spot real está acá.

**F012 con causa-raíz precisa: granularidad de JUECES_CONOCIDOS.** Los 14 patrones de JUECES_CONOCIDOS (parser.py, línea 283) exigen nombre+apellido en la misma línea (ej. `r"carmen\s+m\.?\s*argibay"`). Cuando la firma se parte por corte editorial entre nombre y apellido, la línea aislada con el apellido suelto no matchea ningún patrón. Caso testigo: 333_p2410, línea 20848 con "M. Argibay." cae al catch_all 31 porque la línea anterior (20847, dentro del span de firma) termina en "Carmen" y el siguiente match esperado sería el patrón completo "Carmen ... Argibay" — que no existe en una línea sola.

Esto cambia el fix conceptual de F012. La opción D del prompt previo ("aplicar `linea_es_continuacion_firma` intra-bloque, no solo en borde inferior") era correcta de fondo pero imprecisa en el mecanismo. El fix concreto es: agregar reconocimiento de apellido suelto como continuación de firma. La función `linea_es_continuacion_firma` del auditor (líneas 159-211) ya hace exactamente eso, usa `APELLIDOS_FIRMA_TITULARES` con apellidos sueltos. Esa función está pensada para borde inferior pero la lógica es directamente reutilizable en `detectar_firma_mayoria` del segmentador.

**Disidencia glotona en 333_p2410.** `detectar_votos_y_disidencias` asigna a la última disidencia el rango `[k_ini, len(bloque) - 1]` sin verificar cierre estructural. En 333_p2410, el span 32 disidencia (20849–20983) absorbe la firma de la disidencia, su bloque post-firma editorial y la línea de carátula "JUAN JOSE GOMEZ c/ ALTO PARANA S.A. y Otro" del próximo caso. Es invisible al invariante de disjunción porque ningún otro span pisa ese rango. Es el mismo tipo de blind-spot que F013: el segmentador toma decisiones que el auditor respeta, y el contenido equivocado dentro de un span no se chequea.

**R-postfirma: patrón estructural confirmado.** El bloque editorial post-firma ("Recurso extraordinario interpuesto por...", "Tribunal de origen...", "Tribunal que intervino con anterioridad...") cae sistemáticamente a catch_all en casos sanos. No tiene span dedicado. Aporta entre 5-15 líneas de residuo no patológico. Confirmado en 342_p1313, 341_p218 y 330_p1849. Decisión pendiente: o se le crea un span dedicado al segmentador (p.ej. `metadata_editorial`), o se acepta como ruido editorial conocido y se descuenta del cómputo de residuo.

### Hallazgos del propio auditor

**F-AUDITOR-01: colisión de timestamp.** `auditar_fallo.py` línea 1694: `ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")` con resolución de segundos. `out_path.write_text(md, encoding="utf-8")` sobreescribe sin avisar. Confirmado hoy: tres llamadas seguidas (333_p2420, 330_p1854, 330_p2746) cayeron todas en `21-15-54`, las dos primeras se perdieron. Hubo que reorrer 333_p2420 y 330_p1854. Fix simple: agregar microsegundos al timestamp, o sufijo numérico cuando el archivo ya existe.

**F-AUDITOR-02 descartado.** En la primera lectura propuse "el invariante de disjunción no detecta contaminación intra-span" como bug del auditor. Lectura del código (línea 1365-1372) muestra que la disjunción solo chequea solapamiento entre spans semánticos — eso es lo que define que hace. Que un span de disidencia absorba contenido del próximo caso no es violación de disjunción, es bug del segmentador. El invariante hace su trabajo. La idea original sigue siendo válida pero no como bug del invariante: lo que falta es **otro chequeo**, no una corrección al existente. Idea anotada como mejora futura del auditor: validador de "límite estructural de span" que mire los últimos N caracteres de spans semánticos buscando carátulas embebidas o firmas posteriores.

### Lección de método

La sesión anterior diagnosticó la calibración fallida desde la lectura del detector de borde inferior pero sin abrir `detectar_fin_real`. Eso permitió ver el síntoma (delta negativo en 90% de los casos) pero no la causa. La sesión actual leyó el código de las dos funciones y corrigió tres atribuciones — solapado estructural no es bug de calibración, F012 no es bug del extensor de span sino de la granularidad de patrones, F013 no es bug de detección del cuerpo sino de la pista 1 con falso positivo en cuerpo del dictamen. Ratifica el principio de la BITACORA: chequear código real antes de diagnosticar. La conclusión de hoy puede tener errores que se vean recién cuando se aplique algún fix.

### Pendientes inmediatos

1. Verificar F013 contra el .md crudo: leer LibroVol330.2.md líneas 54165–54310 e identificar qué mención del primer_token del siguiente caso disparó la pista 1.
2. Definir si R-postfirma se crea como span dedicado en el segmentador o se descuenta del cómputo de residuo. Decisión de diseño pendiente.
3. Fix conceptual de F012 con `linea_es_continuacion_firma` reutilizable en `detectar_firma_mayoria`. Precondición: confirmar caso testigo en el .md crudo.
4. Fix de F-AUDITOR-01 con microsegundos en timestamp. Trivial.
5. Pendiente sin fecha: aplicar fix de §4.6.b RE_CONSIDERANDO al parser (caso testigo 344_p2835 con 80% de residuo en la corrida del 09/05). Este pendiente sigue pendiente.


## Sesión 2026-05-14 — H019: rediagnóstico §4.6.b sobre CSV vivo, descarte de herramienta paralela, adopción de `auditar_fallo.py`

Sesión corta de auditoría sin commits de código. Objetivo declarado al inicio: implementar el fix §4.6.b siguiendo el "Draft — Reescritura" registrado al final de PIPELINE.md (sesión 2026-05-09 continuación). La sesión derivó en limpieza de premisas, recálculo del cluster contra CSV vivo, descarte de un script paralelo que se había armado sin conocer la infraestructura existente, y reafirmación de `scripts/auditoria/auditar_fallo.py` como la herramienta correcta para el diagnóstico fino.

### Verificación: el fix §4.6.b nunca llegó al código

Los logs postfix del 9/5 (`+0/+0` sospechosos, `+0` vacíos) habían quedado registrados ambiguamente como "el fix no movió la aguja". `git log -p --all -S "RE_CONSIDERANDO" scripts/pipeline/parser.py` confirma que el único commit que toca el regex es `cf836cc` (2/5, reorganización estructural — commit de introducción del regex, no de modificación). Los dos commits posteriores que tocan `parser.py` (`2adda06` Fix1 V1 case_name, `2aeb280` RE_APERTURA tolerante doble espacio) no modifican `RE_CONSIDERANDO`. El regex está exactamente como dice el plan original: `r"^Considerando\s*[:.]?\s*$"`.

Lectura: la validación postfix del 9/5 fue prematura. No hubo fix aplicado al código y por eso pre vs post salieron idénticos. **El bug §4.6.b está vivo, intacto, y el CSV vivo refleja ese estado.** El terreno está limpio para diagnóstico fino.

Hallazgo lateral: existe `RE_CONSIDERANDO_NUMERADO_1` (`r"Considerando\s*:\s*1\s*[°ºª]\s*\)"`), distinto del `RE_CONSIDERANDO` principal, usado en detección de "estructura autónoma" para votos largos (`wc_voto >= 1500 and es_estructura_autonoma`). No afecta el cluster pre-fix (el cluster mide `wc_considerando` del fallo principal, no de votos individuales), pero hay que tenerlo presente al diseñar el fix: cualquier cambio en `RE_CONSIDERANDO` debe considerar si conviene unificar criterios con el numerado o dejarlos separados a propósito.

### Cluster vivo recontado: 320 / 232 / 88 / 1672

El plan original de sesión arrastraba "480 sospechosos" como tamaño del cluster. La auditoría contra `output/parser/csjn_casos.csv` (5.819 filas) sobre el CSV vivo dio:

| Variable | Plan original (S2026-05-09 cont.) | CSV vivo (S2026-05-14) | Coincide |
|---|---:|---:|---|
| Total cluster (`wc_cons ≥ 0.9 × wc`) | 480 | **320** | ✗ |
| Apertura `fallo` | 229 | 229 | ✓ |
| Apertura `sentencia` | 3 | 3 | ✓ |
| Sin apertura | 248 | **88** | ✗ |
| Vacíos (`wc_cons == 0`) | — | 1.672 | — |

Los **232 con apertura detectada coinciden exactamente** entre plan y vivo. Lo que difiere son los "sin apertura" (88 vs 248), y por arrastre el total. Probable explicación: el commit `2aeb280` del 2/5 ("RE_APERTURA tolerante a doble espacio") detectó aperturas que antes no detectaba, y esos casos salieron del cluster porque su `wc_considerando` se acotó al haber apertura.

Implicancia: **el cluster relevante para §4.6.b (los 232) sigue intacto**. La hipótesis del bug se mantiene (`RE_CONSIDERANDO` no detecta formatos 2/3). Lo que cambió es la magnitud del bug paralelo "sin apertura detectada": de 248 a 88. No es §4.6.b — es otro bug aún sin diagnóstico propio.

### Hipótesis vieja vs nueva, redefinición de §4.6.b

El diagnóstico original de PIPELINE §4.6.b apuntaba al fallback `inicio_cons = 0` como causa. La sesión del 9/5 (continuación) ya había rediagnosticado: el fallback es síntoma, la causa raíz es `RE_CONSIDERANDO` restrictivo + invocación con `.match()` en lugar de `.search()`. El "Draft — Reescritura §4.6.b" al final de PIPELINE.md registra ese rediagnóstico.

Esta sesión confirma la hipótesis del 9/5 y la actualiza con cifras del CSV vivo (320, no 480; 88 sin apertura, no 248).

### Descarte de herramienta paralela: `auditoria_4_6_b_prefix.py` (v2)

Durante la sesión se construyó un script nuevo en `scripts/diagnostico/auditoria_4_6_b_prefix.py` que reimplementaba regex en paralelo al parser (RE_F1, RE_F2, RE_PERMISIVO). El script corrió y dio el dimensionamiento del cluster (Bloques 1, 2, 5), pero el Bloque 3 (clasificación f1/f2/f3 con lectura de `.md`) abortó por nombres de columna distintos a los asumidos (`archivo` y `linea_fin` en lugar de `source_file` y `linea_fin_real`).

Antes de arreglar las columnas, una pregunta del usuario ("¿no hicimos un script auditoría_csjn que separaba bien las secciones con info del regex?") reveló la existencia de `scripts/auditoria/auditar_fallo.py` (69 KB, construido en sesión 2026-05-08 según H014). Inspección del docstring confirmó: **`auditar_fallo.py` reusa los regex y helpers de `parser.py` por importación** ("No reimplementa heurísticas. Si una heurística está rota en parser.py, acá va a estar igual de rota — y el catch-all lo va a delatar"). Es exactamente la arquitectura que `auditoria_4_6_b_prefix.py` no tenía.

Lectura crítica del propio trabajo:
- El script paralelo reimplementaba regex que el parser ya tenía → mala práctica (si el parser cambia, el diagnóstico mide el viejo).
- El script paralelo no particionaba el bloque en spans tipados → no podía dar input al diseño del fix con guard espacial.
- El script paralelo había sido construido sin antes inventariar las herramientas existentes → trabajo duplicado e inferior.

Decisión: descartar `auditoria_4_6_b_prefix.py`, archivar en `archivo/exploratorios/diagnostico/4_6_b/auditoria_4_6_b_prefix_v2.py` (junto al del 9/5 que también está archivado ahí). El log de la única corrida útil (dimensionamiento) queda en `archivo/exploratorios/diagnostico/4_6_b/salida/auditoria_4_6_b_prefix_20260514_1931.txt`. El script anterior `diagnostico_4_6_b_cluster.py` que también se había creado y descartado en esta sesión fue eliminado directamente, sin valor documental.

### Conexión con H015 (estrategia de promoción gradual del auditor)

Esta sesión es evidencia operativa de la decisión H015: cuando aparece un problema de diagnóstico, **no escribir herramienta ad-hoc paralela; usar el auditor**. El auditor materializa la arquitectura de "separación entre segmentación y extracción de features" que el parser actual no tiene (BITACORA H014). Para §4.6.b específicamente, el catch-all del auditor sobre el cluster de 232 es el camino correcto: va a delatar dónde el cuerpo del fallo cae porque `RE_CONSIDERANDO` no matchea.

Convención reafirmada: cualquier diagnóstico fino del corpus va via `auditar_fallo.py`, no via scripts ad-hoc en `scripts/diagnostico/`. Esto deja a `scripts/diagnostico/` solo para diagnósticos cuantitativos sobre los CSVs producidos, no sobre el cuerpo del corpus.

### Sin fix aplicado al cierre

- `parser.py`: sin cambios.
- CSVs vivos: sin regenerar.
- `RE_CONSIDERANDO` sigue intacto en línea 121.

### Pendientes para próxima sesión

1. **Diagnóstico fino del cluster con `auditar_fallo.py`.** Sample dirigido de ~5 casos al azar del cluster de 232 (con seed reproducible). El catch-all del auditor va a mostrar dónde cada "Considerando" no detectado cae respecto a los spans (dictamen vs cuerpo_mayoria). Esto da el input directo para diseñar el fix con guard espacial.
2. **Diseño del fix con guard espacial.** Sobre la base del diagnóstico fino, decidir si el fix es `RE_CONSIDERANDO` permisivo + `.search()` dentro de la ventana `(apertura, por_ello)` excluyendo span del dictamen, u otra estrategia. F013 ya enseñó que `permisivo + .search()` sin guard rompe fallos.
3. **Validación postfix.** El script `archivo/exploratorios/diagnostico/4_6_b/auditoria_4_6_b_postfix.py` sigue siendo válido como base (compara métricas pre/post, detecta regresiones). Reusable sin cambios para esta iteración.

### Lección de método

Antes de construir herramienta nueva, inventario de herramientas existentes. Esta sesión perdió ~2 horas reconstruyendo en paralelo lo que `auditar_fallo.py` ya hacía mejor. El inventario formal de scripts (`scripts/diagnostico/`, `scripts/auditoria/`, `archivo/`) sigue pendiente — anotado al cierre de la sesión como trabajo separado para sesión dedicada.
### Hallazgo lateral durante inventario Fase 1 — tests fantasma del 4/5

Durante la Fase 1 del inventario se encontró `tests/__pycache__/` con cinco
`.pyc` del 4/5/2026 ~00:35:25 sin sus `.py` correspondientes:

- `test_corte_indice.cpython-314-pytest-9.0.3.pyc`
- `test_fix_mas_uno.cpython-314-pytest-9.0.3.pyc`
- `test_salto_huerfano.cpython-314-pytest-9.0.3.pyc`
- `conftest.cpython-314-pytest-9.0.3.pyc`
- `__init__.cpython-314.pyc`

Los `.py` originales no existen en filesystem (búsqueda recursiva en repo
vivo, `snapshots/` y `archivo/`), ni en git history
(`git log --diff-filter=D` vacío). Tests escritos, ejecutados al menos
una vez (de ahí los `.pyc`) y borrados sin llegar a commit. No mencionados
en BITACORA ni CHANGELOG previos.

Inferencia por nombres:
- `corte_indice` → probablemente `ok_cortado_en_indice` (cerrado §3.6.e Fase 1).
- `fix_mas_uno` → probablemente `pg_fin+1` (bug abierto del cruzador).
- `salto_huerfano` → bug temprano del cruzador, no identificado.

Decisión: eliminar `tests/` durante Fase 1 de inventario. Esta entrada
queda como única evidencia histórica del experimento.
## Sesión 2026-05-14 — Inventario del repo, Fases 1 y 2

### Fase 1 — Zona OLVIDADA  [CERRADA]
- Raíz canónica: 9 archivos. `bak/` solo con sesión actual. Eliminadas carpetas `logs/`, `tests/`, `validacion/`, `prompts/`. `archivo/snapshots_ad_hoc/` con 12 sub-carpetas legibles.
- Commits: `671d796`, `eac5a06`.
- Hallazgo lateral: `.pytest_cache/` en raíz, residuo de tests fantasma del 4/5 → diferido a Fase 4.

### Fase 2 — Zona DUPLICADA  [EN CURSO]

**Bloque scripts** [cerrado, commits `e695e16` + este]
- Rescatados a `scripts/analisis/`: `csjn_analisis_v3.py`, `clasificador_tipo_caso.py`, `detector_templates.py`.
- Rescatado a `scripts/pipeline/`: `diagnostico_fin_fallo_v1.py` (relevante para bug Y.P.F.).
- Archivados en `archivo/scripts_historicos/`: parsers v10-v16, `csjn_analisis_v2.py`, 6 auxiliares de QA.
- Verificado: padrón de jueces históricos ya está en `parser.py` vivo (líneas 294-299).
- README de auxiliares documenta activos rescatables (regex, padrones, umbrales, diagnósticos congelados en `archivo/data/`).

**Bloque docs** [pendiente, próxima sesión]
- Hallazgo: sistema de docs fragmentado entre `BITACORA.md` (75 KB), `docs/analisis_forense_pipeline.md` (254 KB), `PIPELINE.md` (121 KB), `PIPELINE_HALLAZGOS.md` (39 KB), `CHANGELOG.md`, `DEUDA_TECNICA.md`.
- Posibles contradicciones y alucinaciones/rollbacks entre archivos sin mapear.
- Plan acordado: inventario de hallazgos por archivo, plan (a) con freno → si se complica, caer a (b) críticos.
- Inventario de BITACORA ya hecho: 19 hallazgos H001-H019 + 4 F-numerados (F007, F010-F012).
- Bugs críticos a no perder: Y.P.F. (`pista_fin=caratula_siguiente`), 19 `ok_cortado_en_indice`, 121 orphans, Bug XII (sin_firma cascada), F010-F012, H019.

**Bloque snapshots** [pendiente]
- Tres snapshots completos por procesar: `snapshots/snapshot_2026-05-02_1559/`, `snapshots/snapshot_pre_reorg_2026-05-02_1843/`, `archivo/snapshots_ad_hoc/pre_fix_xii_20260503_1308/`.

### Hallazgos laterales pendientes (acumulan para Fase 4)
- `.pytest_cache/` en raíz (de Fase 1).
- `scripts/pipeline/parser.py.bak` del 9/5 — decidir si se queda al lado del parser o va a `bak/`.

### Convenciones fijadas en esta sesión
- **Esquema de docs:** solo 5 .md en raíz (README, MAPA, BITACORA, CHANGELOG, DEUDA_TECNICA). Otros .md viven en carpetas específicas como README.md de la carpeta.
- **No crear archivos .md nuevos** sin antes verificar si la información va en alguno de los 5 existentes.
- Editar archivos con acentos en VS Code, nunca PowerShell.
- No tocar `parser.py`, no regenerar CSVs vivos.
## Sesión 2026-05-14 (cont.) — Inventario del repo, bloque docs (parcial)

Continuación de la sesión de inventario. El bloque docs era el más
delicado y se planeó como "tabla de cobertura completa de hallazgos
con freno, plan (a) o caer a plan (b)". El recorrido cambió ese plan:
no hay 6 docs fragmentados que mergear, hay dos eras documentales con
un puente entre ellas.

### Recorrido y método

Se leyeron las cabeceras de `docs/analisis_forense_pipeline.md` (Niveles
1-3), y las secciones XVII-XXI palabra por palabra. Después se leyeron
las cabeceras de `PIPELINE.md` y `PIPELINE_HALLAZGOS.md`. Ningún archivo
se editó (el doc forense queda como journal congelado).

### Hipótesis de la estructura documental real

- **`PIPELINE.md` = spec técnica viva** del pipeline, organizada por
  etapas (1-4), con bugs catalogados §X.Y anclados al código. Es el
  ground truth técnico actual. Cubre fixes hasta el 9/5 (§3.6.a fix
  pg_fin+1, §3.6.e fase 1 hojas complementarias, §4.6.j RE_APERTURA
  doble espacio).
- **`PIPELINE_HALLAZGOS.md` = journal de actualización de `PIPELINE.md`**,
  con tracking por sesión: "Ya integrados / Pendientes residuales /
  Hallazgos nuevos". Última entrada: 14/5 — rediagnóstico §4.6.b sobre
  CSV vivo (= H019).
- **`docs/analisis_forense_pipeline.md` = journal histórico anterior**,
  del 1/5 al 4/5. Cerrado con la sesión XXI, que produjo el "inventario
  consolidado de bugs vivos a-v". Era anterior a la era PIPELINE.
- **`BITACORA.md` = journal general del proyecto**, distinto y más alto
  nivel que los anteriores. H001-H019 son sus hallazgos.
- **`CHANGELOG.md`, `DEUDA_TECNICA.md`** = formales, no abiertos esta
  sesión.

### Zona muerta del forense: sesiones XVI-XVIII

Las sesiones XVI, XVII (duplicada en el journal: 2941 y 3029) y XVIII
fueron pseudocódigo y refactor abandonados ("Tanda 1 / Tanda 2"
alucinadas, basadas en código supuesto en vez de leer `parser.py` real).
**Nunca tocaron el código**: confirmado por `git log --all --follow
scripts/pipeline/parser.py` — entre `7f245a6` (v17 beta v1, 1/5) y
`2adda06` (Fix 1 aplicado, post-XX) no hay commits al parser. XVIII
contiene el reconocimiento del error y desarma la narrativa. XXI agrega
flags retrospectivas a XVIII y XIX-XX señalando exactamente qué fue
alucinación y qué fue medición sólida. No se reescribe nada: la franja
queda como capa geológica con sus propias flags.

### El inventario a-v de XXI

XXI armó un inventario consolidado de 22 bugs (a-v), cada uno con lugar
exacto en el código, síntoma, casos cuando se midió, estado del fix,
referencia a la sesión donde se diagnosticó. La nomenclatura "Fix 1 /
Fix 2 / Fix 3" del cierre XIX-XX se descarta porque el usuario nunca la
aprobó; sólo Fix 1 (V1 como fuente primaria de `case_name_cuerpo`)
corresponde a una decisión real.

Estado del inventario al 14/5:
- Fix 1: aplicado y commiteado (`2adda06`).
- Bug XXI-g (RE_APERTURA estricto): parcialmente fixeado (`2aeb280`,
  variante doble espacio). Variante "header partido en dos líneas"
  sigue abierta.
- Resto del inventario a-v: presumiblemente cubierto/actualizado en
  `PIPELINE.md` con su sistema §X.Y, pero el cruce no se hizo aún.

### Hallazgo lateral

`csjn_casos.csv` productivo es **byte-a-byte idéntico** a
`csjn_casos_pre_refactor_subloques.csv` (MD5 confirmado en XXI). El
snapshot es redundante; se puede archivar cuando se llegue al bloque
snapshots de la Fase 2.

### Bug de duplicado en `BITACORA.md`

El commit `e3c53b2` (anoche) commiteó la entrada del 14/5 duplicada (la
escribió dos veces consecutivas; primera con redacción "commit pendiente
con READMEs", segunda con redacción "commits e695e16 + este"). El
duplicado se detectó hoy revisando los headers con `Select-String
"^## Sesión 2026-05-14"`. Se deduplicó conservando la segunda versión
(redacción correcta). Commit `4248ba1` con -35 líneas / +0.

### Trabajo pendiente del bloque docs

1. **Cruzar el inventario a-v de XXI contra los bugs §X.Y de
   `PIPELINE.md`** para confirmar la hipótesis de que PIPELINE.md cubre
   y supera el inventario. Producir una tabla a-v → §X.Y con huérfanos.
2. **Cruzar BITACORA H001-H019 + F-numerados contra el resultado del
   paso anterior** para detectar hallazgos no recogidos en ninguno de
   los dos.
3. **Decidir destino de `docs/analisis_forense_pipeline.md`**: dejarlo
   como histórico congelado (probable), o mover a `archivo/` (poco
   probable, es valioso como journal de aprendizaje).
4. **Recién entonces**, decidir qué va en `DEUDA_TECNICA.md` como lista
   viva y qué se queda en PIPELINE.md como spec.

### Bloque snapshots: pendiente

Sin avance esta sesión. Se mantiene el plan original.

## Sesión 2026-05-15 (apertura, cierre rápido)

**Estado al cierre:** sin commits, sin cambios en código. Sesión de planning
y corrección de doc pendiente.

**Hallazgo:** M05 en DEUDA_TECNICA está mal redactado. Dice "comparar lista 
de los 32 documentados en §3.6.a contra el Bloque B mencionado en XXI-v". 
Confusión: Bloque B se menciona en XXI-f (= B025, los 414 sospechosos 
unanime), no en XXI-v. XXI-v dice explícitamente "los casos específicos 
nunca se identificaron; sin git log no hay forma de diagnosticar el cambio 
que los generó". No hay lista archivada para cruzar.

**Lección operativa:** el mapeo histórico XXI-letra → B0NN (tabla al final 
de DEUDA_TECNICA) puede estar correcto pero generar confusión si no se 
cruza contra el contenido real de cada letra del forense al redactar 
acciones. El error en M05 vino exactamente de no hacer ese cruce.

**Plan para próxima sesión:**

1. Releer XXI-v contra el mapeo histórico — confirmar la confusión 
   con propios ojos antes de corregir.
2. Reformular M05 en DEUDA_TECNICA. Nueva redacción acordada: 
   "Identificar los 32 casos desenmascarados por §3.6.a filtrando 
   `fallos_localizados.csv` por status_localizacion = pagina_fin_no_en_mapa, 
   separar por tomo (331-334 = B009; otros = los 32 de B001), spot-check 
   3-5 contra .md para verificar legitimidad del status nuevo." Esfuerzo: 
   30 min, no 10.
3. Nota a incorporar dentro de M05: la coincidencia entre los 32 de §3.6.e 
   (reasignados pagina_fin_no_en_mapa → ok_pg_fin_redirigida) y los 32 de 
   §3.6.a (desenmascarados ok → pagina_fin_no_en_mapa) es sospechosa. 
   Antes de ejecutar el filtro, fijar expectativa: ¿32, 43, 75, o algo 
   distinto? La distribución por tomo es el diagnóstico.
4. Nota a incorporar dentro de M05: alcance excluido — el spot-check 
   verifica legitimidad del status, NO ausencia de falsos negativos en 
   csjn_casos.csv. Validación cruzada contra parser queda como alcance 
   separado.
5. Ejecutar M05 reformulado.
6. Si cierra rápido, seguir con B025 (re-medición 414 contra CSV vivo).

**No se commiteó nada porque no hubo cambios en código ni en doc.**
## H020 — Flag de M05 + decisión de auditar persistencia de bugs (15/5/2026)

Sesión corta. Releyendo Hallazgo 7 del forense (= XXI-v) en función
de corregir M05 según plan del 14/5, se identificó que la
reformulación propuesta también era incorrecta. Los 32 de §3.6.a y
los 32 de XXI-v son fenómenos de direcciones opuestas (uno desenmascarado
post-fix B001, otro enmascarado pre-fix por cambio sin git log).
Probablemente grupos distintos. Identificación caso-a-caso de los
originales de XXI-v es imposible sin git log de ese período.

Decisión: en lugar de reformular M05 una segunda vez sobre supuestos
frágiles, flaguearlo en DEUDA_TECNICA con las dudas concretas y dejar
la resolución para sesión futura. Flag aplicado en commit da70e04.

Hallazgo más amplio: la lista de bugs de DEUDA_TECNICA mezcla
diagnósticos de distintas épocas del parser, sin garantía de que
persistan en el CSV actual. Próxima sesión: auditar con
auditar_fallo.py sobre muestra random para evaluar cuáles bugs siguen
vivos y priorizar a partir de eso, en vez de seguir trabajando la
lista existente como si todo estuviera al día.

## H021 — Infraestructura para auditoría de persistencia de bugs (15/5/2026)

Sesión enfocada en preparar la auditoría planificada en H020. No se
ejecutaron los Pasos 4-6 del plan (tabulación, spot-check,
re-priorización); quedan para H022. Lo que sí se hizo: agregar
infraestructura mínima para que la corrida de 80 sea reproducible y
tabulable.

### Cambios al auditor (regla del plan violada deliberadamente)

El plan H020 decía "no tocar auditar_fallo.py". Se incumplió esa regla
con justificación: agregar un flag `--seed N` al CLI para sampling
reproducible. La modificación es de infraestructura (5 + 3 líneas), no
de lógica de detección — la API canónica `auditar_fallo(tomo, pagina)`
no cambió. Implementación con `random.Random(N)` (instancia local) en
vez de `random.seed()` global para evitar contaminación del PRNG del
módulo si el auditor se importa desde otro script.

Verificación: dos corridas con `--seed 15052026 --random 5` devolvieron
exactamente los mismos 5 case_ids en el mismo orden. Dos corridas sin
seed dieron muestras distintas (control negativo OK). Commit `a0809ee`.

Alternativa descartada: script de sampling efímero al lado del auditor.
Razón: scripts de un solo uso se vuelven ilegibles en pocas semanas
("no sabemos qué son los archivos o qué hacen"). Mejor flag permanente
documentado en `--help`.

### Wrapper de tabulación en lote

Archivo nuevo: `scripts/auditoria/tabular_senales_lote.py` (260 líneas).
Orquesta corrida en lote de `auditar_fallo()` sobre una muestra random
con seed, y produce tres outputs en `output/auditoria/auditar_fallo/`:

1. `tabla_senales_<N>_<seed>.csv` — 25 columnas crudas por caso
   (identificación, cobertura, estructura de spans, borde inferior,
   status del parser).
2. `dicts_<N>_<seed>.json` — los N dicts completos del auditor, para
   regenerar la tabla con columnas distintas sin re-correr el lote.
3. `auditoria_<N>_<seed>.md` — idéntico al output del CLI del auditor.

Defaults: `--random 80 --seed 15052026`. Reusa funciones del auditor
(`_seleccionar_random`, `_render_doc_completo`) en vez de duplicar
lógica. Cache compartido entre las 80 invocaciones para no recargar
CSVs grandes. Commit 5156523.

Decisión metodológica clave: la tabla agrupa **señales crudas** del
auditor, no diagnósticos por bug B0NN. El mapeo señal → bug se hace
post hoc en spot-check (Paso 5), no a priori. Razón: la lista de
DEUDA_TECNICA puede tener bugs que el auditor no sabe detectar y
señales del auditor que no tienen entrada en DEUDA_TECNICA. Tabular
por señal evita que el mapeo sesgue lo que se ve.

### Muestra de 80 (seed 15052026)

Corrida ejecutada al final de la sesión. Outputs en `output/auditoria/auditar_fallo/` con sufijo `80_15052026`
(no versionados — `.gitignore` excluye `output/auditoria/auditar_fallo`).
Archivos: `tabla_senales_80_15052026.csv` (15 KB),
`dicts_80_15052026.json` (2.0 MB), `auditoria_80_15052026.md` (1.8 MB).

### Hallazgo preliminar (no interpretado)

En el test con `--random 5 --seed 999` previo a la corrida real, 4 de
5 casos cayeron en `borde_estado = solapado_con_proximo` y 2 con
porcentaje de residuo >50%. No se interpretó: n=5 no permite inferir
prevalencia, y la magnitud del solapamiento (`borde_delta`) no se
revisó. El estado solapado puede ser ruido editorial (1-2 líneas) o
bug serio (20+ líneas) — pendiente análisis sobre los 80 en H022.

### Pendiente para H022

1. Análisis exploratorio de `tabla_senales_80_15052026.csv`:
   distribuciones por señal, especialmente `borde_estado`,
   `borde_delta`, `porcentaje_residuo`, `pista_fin`.
2. Mapeo de señales observadas a bugs de DEUDA_TECNICA.
3. Spot-check de 5-10 casos contra `.md` (Paso 5 del plan H020).
4. Conclusiones de re-priorización en
   `output/auditoria/auditar_fallo/conclusiones.md` (Paso 6).
5. **No** actualizar DEUDA_TECNICA en H022 — las conclusiones quedan
   como insumo para una sesión posterior dedicada a esa re-priorización.

### Ideas anotadas para sesiones futuras

- **Integración auditor → parser productivo.** El auditor segmenta el
  bloque de un fallo en 10 tipos de span (carátula, sumario, dictamen,
  cuerpo_mayoría, voto, disidencia, firma, sumario_con_link,
  header_pagina, catch_all) con mejor granularidad que el parser
  actual. Evaluar si esa segmentación puede reemplazar o complementar
  la del parser productivo. Decisión arquitectónica grande, sesión
  dedicada.
- **Expansión de tabla de señales a 40+ columnas.** Hoy en 25. Si la
  auditoría escala a corpus completo (5800+ casos), conviene agregar
  flags derivados (`tiene_firma_sin_votos`, `voto_sin_firma`) y
  alertas individuales como columnas booleanas separadas. Marginal a
  80 casos, útil a escala.
## H022 — Auditoría exploratoria de 80 casos: spot-check de 7 testigos y mapeo preliminar a deuda (15/5/2026)

Ejecución de los Pasos 4-6 del plan H020 sobre la muestra de 80 casos
con seed 15052026 generada en H021. Outputs en
`output/auditoria/auditar_fallo/conclusiones_h022.md` (no versionado).

### Análisis exploratorio de la tabla de señales (80 casos)

Distribución de `borde_estado`: 71 `solapado_con_proximo` (88.8%), 9
`gap_con_residuo` (11.2%). **Ningún caso de la muestra cierra
exactamente donde el catálogo dice.** Magnitud del solapamiento
(n=71): mediana 16 líneas, máx 43. Magnitud del gap (n=9): mediana
23 líneas, máx 485. Cuatro casos con gap > 50 con alerta
`caratula_siguiente_en_gap`.

`porcentaje_residuo`: mediana 6.0%, media 12.4%, máx 86.1%. Diez
casos con residuo > 25%; cinco con residuo > 50%. `invariante_cobertura
== False`: 0/80. `invariante_disjuncion == False`: 5/80, de los
cuales dos con residuo 0% (señal aparentemente limpia que esconde bug
catastrófico).

### Spot-check de 7 casos extremos

Selección: tres por gap (`343_p2243`, `344_p3543`, `339_p1393`), dos
por residuo alto (`332_p913`, `346_p1205`), uno con disjunción rota
y residuo 0% (`332_p244`), uno para conectar con bug multi-volume
conocido (`330_p829`).

Identificación a ojo de cinco mecanismos preliminares contra el .md:

- **M1 — Cierre prematuro por firma falsa.** Testigo `343_p2243`. El
  parser cerró en una firma de la Corte que pertenecía al fallo
  anterior. Mapeo preliminar → B025.
- **M2 — Cierre prematuro por carátula falsa.** Testigos `344_p3543`,
  `339_p1393`. El parser interpretó una línea interna del cuerpo o
  dictamen como inicio del próximo caso. Mapeo preliminar → B018.
- **M3 — Cuerpo cerrado antes de dispositiva extendida.** Testigos
  `332_p913`, `346_p1205`. Hipótesis: el parser asume one fallo per
  case. Mapeo preliminar → no listado, propuesto como B043. **(Ver
  H023 para refutación.)**
- **M4 — Mala localización del inicio del bloque.** Testigo
  `330_p829`. El catálogo apunta al inicio del bloque varias líneas
  antes del fallo real; las líneas iniciales son cierre del caso
  anterior. Mapeo preliminar → B022.
- **M5 — Apertura espuria de span voto sobre header de sentencia
  previa.** Testigo `332_p244`. El parser matcheó "Voto del señor
  ministro doctor don Enrique Santiago Petracchi" de una sentencia
  previa publicada antes del fallo plenario, y abrió span voto que
  envolvió la sentencia plenaria entera. Mapeo preliminar → no
  listado en parser (sólo B040 en auditor), propuesto como B044.

### Trampa metodológica detectada

`porcentaje_residuo == 0%` no implica "el parser hizo bien". Residuo
mide calidad de clasificación dentro del intervalo que el parser se
asignó, no respecto del intervalo que debería haber procesado. En
los Mecanismos M2 (cierre prematuro) y M5 (apertura espuria
envolvente), residuo 0% es engañoso. Implicancia operativa: cualquier
criterio futuro de calidad debe combinar `residuo` con `borde_estado` +
`borde_delta` + `invariante_disjuncion`. El residuo aislado tiene
falsos negativos.

### Regla operativa heredada

H022 deja proposiciones de mecanismos y mapeos preliminares pero
**no actualiza DEUDA_TECNICA.md** (regla del plan H020). La
verificación contra código y la actualización de deuda quedan para
H023.

### Pendiente para H023

Verificación de los cinco mecanismos contra `parser.py`. Para cada
uno: lectura dirigida del código, confirmación de causa raíz, estado
de verificación propuesto, propuesta de fix direccional. Orden:
M3 → M2 → M5 → M4 → M1 (priorizando los más novedosos primero).
**Verificar mecanismos contra .md crudo antes de declararlos** —
el spot-check de H022 es rápido y puede haber confundido patrones
distintos.

## H023 — Verificación de mecanismos H022 contra parser.py: M3 refutado, M2 confirmado y refinado (15/5/2026)

Sesión enfocada en verificar contra `parser.py` los cinco mecanismos
identificados a ojo en H022. Se cubrieron M3 y M2; M1, M4, M5 quedan
para sesión posterior.

**Cambio metodológico crítico aplicado mid-sesión:** chequear cada
mecanismo contra el .md crudo antes de declararlo. La regla emergió
de la refutación de M3 (ver abajo) y se aplicó retroactivamente a
M2. Se documenta como lección para sesiones siguientes.

### M3 refutado: no existe como mecanismo independiente

Los dos testigos de M3 (`332_p913` y `346_p1205`) fallan por motivos
distintos, ninguno por "doble dispositiva legítima del mismo caso".

**`332_p913` (caso Deluca c/ ANSeS).** Lectura del .md mostró que las
líneas iniciales del bloque son el cierre de **otro fallo** (una
resolución sobre competencia en Bahía Blanca, no Deluca). El parser
matchea `De conformidad con lo dictaminado` (variante del detector
de dispositivo) en ese cierre arrastrado, captura la firma del fallo
anterior como firma del caso Deluca, y deja el verdadero fallo de
Deluca (con su `FALLO DE LA CORTE SUPREMA / Vistos los autos /
Considerandos 1°-10° / Por ello / firma Lorenzetti-Fayt-Maqueda-
Zaffaroni) en catch_all. Es B022 (arrastre del previo) con una
variante nueva: el arrastre puede incluir un FALLO completo del caso
anterior, no sólo líneas residuales de firma. B022 se actualiza
en DEUDA_TECNICA con `332_p913` como testigo y la Variante 2
caracterizada.

**`346_p1205` (caso Osorio c/ GCBA).** Lectura del .md mostró un
único fallo, una única dispositiva, fecha única (10 de octubre de
2023). La afirmación de H022 sobre "dos resoluciones, 10-oct-2023 y
19-oct-2023" no se sostiene en el .md. El residuo alto del 80.30%
no se explica por doble dispositiva. Hipótesis abierta: el bloque
está dominado por el dictamen del Procurador (3 de las 5 páginas
del caso), y algo en la separación dictamen/cuerpo dejó parte del
dictamen contado fuera. Mecanismo no determinado en H023. Caso
huérfano para sesión posterior.

**B043 propuesta retirada.** No corresponde abrir entrada nueva por
M3. El ID B043 queda libre y se reutiliza para el defecto de
`primer_token_de_caratula` (ver M2).

### M2 confirmado y refinado: B018 con tres componentes acoplados

Los dos testigos de M2 (`344_p3543` y `339_p1393`) confirman el
mecanismo de B018 (pista 1 de `detectar_fin_real` matchea mención
casual del primer_token del siguiente), con dos variantes distintas
que refinan la causa raíz:

**`344_p3543` (V1, gap +133, residuo 77.78%).** Caso siguiente:
`SÁNCHEZ, MARTÍN IGNACIO c/ PRUZZO PINNA`. primer_token = `Sánchez`.
La mención que disparó el match: **"Carlos Sánchez Herrera"** en la
lista de profesionales del **caso anterior** (Coihue c/ Provincia
de Santa Cruz, página 3543). Esa línea estaba en el bloque sólo
porque el catálogo arrastró el cierre del caso anterior (B022). El
parser cortó el bloque al principio, dejando el verdadero fallo
Sancor entero fuera. Esto demuestra **interacción B022 → B018**:
el arrastre del previo introduce líneas donde hay apellidos
casuales que matchean el primer_token siguiente.

**`339_p1393` (V2, gap +84, residuo 0% engañoso).** Caso siguiente:
`PROVINCIA DEL NEUQUÉN c/ VITAL SOJA S.A.`. primer_token =
`Provincia`. Cuatro apariciones de "provincia" en el bloque actual
(dos en el dictamen, una en la dispositiva del FALLO, una en la
carátula del siguiente). El parser corta en alguna de las
apariciones interiores. Esto expone un **defecto adyacente**:
`primer_token_de_caratula` no excluye sustantivos institucionales
genéricos. La lista de exclusión cubre tipos societarios pero no
`provincia/estado/nación/ciudad/...`. Se abre **B043** para este
defecto.

**Causa raíz refinada (tres componentes acoplados):**
1. `primer_token_de_caratula` puede devolver sustantivos genéricos
   (B043).
2. El test `es_caratula` en pista 1 no verifica estructura, sólo
   presencia de la palabra.
3. El orden de operaciones impide guardias espaciales —
   `detectar_fin_real` corre antes de detectar dictamen o firma.

**Caso patológico identificado:** carátulas como `PROVINCIA DE
BUENOS AIRES c/ Y.P.F.` tienen todos los primeros tokens
contaminados. Engrosar la lista de exclusión es paliativo, no
solución. Esto descarta la "Opción A" de fix simple.

**Matriz de opciones de fix (7 opciones evaluadas).** Detalle en
DEUDA_TECNICA B018. Recomendación direccional: **D → B → E**.
D (validación cruzada con `proximo_header_pagina`) ataca raíz con
costo bajo. B y E como refuerzo si queda residual. C en cartera
para refactor más amplio. F sobreintensiva. G sólo si conviene
postergar. A descartada como solución principal.

B018 sube de `confirmado_caso_testigo` a `confirmado_mecanismo`
(causa raíz en código + tres testigos cubriendo dos variantes).

### Cambios aplicados a DEUDA_TECNICA en esta sesión

- **B018** reescrito: causa raíz refinada con tres componentes, dos
  variantes empíricas caracterizadas, dos testigos nuevos
  (`344_p3543`, `339_p1393`), matriz de fixes en "Estado del fix",
  sección de interacciones con B022 y B043, estado subido a
  `confirmado_mecanismo`.
- **B022** ampliado: testigo nuevo `332_p913` (Variante 2 con FALLO
  completo arrastrado), `330_p829` confirmado como testigo (era de
  XXI pero el spot-check H022 lo verificó), sección de interacciones
  con B018. Sigue en `confirmado_caso_testigo` (6 testigos).
- **B043** abierto: defecto de `primer_token_de_caratula`,
  `confirmado_mecanismo`, acoplado a B018.

### Pendiente para sesión posterior

1. Verificación de M1 (`343_p2243` → B025), M4 (`330_p829` → B022,
   pero ya parcialmente cubierto en H023), M5 (`332_p244` →
   propuesta B044) contra parser.py. Mismo método: lectura .md crudo
   primero, código después.
2. Diagnóstico individual de `346_p1205` (caso huérfano).
3. Aplicación de fix de B018 (recomendación direccional: opción D
   primero). Sesión dedicada con snapshot/commit antes.
4. Eventual nota a PIPELINE §4.4.k señalando que "primera apertura
   de dispositivo" es el defecto arquitectónico subyacente de B013
   y de futuros bugs análogos.

### Lección metodológica registrada

El spot-check de H022 fue rápido (7 casos, lectura a ojo) y mezcló
tres patrones que dan al auditor residuos parecidos pero causas
distintas: doble dispositiva legítima (no observada en realidad),
arrastre del previo con FALLO completo (`332_p913`), y dictamen
mayoritario con cuerpo breve (`346_p1205`). H023 confirmó que
**verificar mecanismo contra .md crudo antes de declararlo es
indispensable**. La regla operativa del plan H020 ("el spot-check
identifica patrones, no causas raíz") se cumplió literalmente: M3
era un patrón, no un mecanismo. La verificación contra código + .md
lo disuelve.
## H024 — Verificación de M5/M4/M1 + huérfano 346_p1205: B044 nuevo, B045 nuevo, B022 ampliado, B025 confirmado (15/5/2026)

Continuación directa de H023. Plan: verificar contra `parser.py` y
contra el `.md` crudo los mecanismos M5, M4, M1 + el huérfano
`346_p1205`, aplicando la regla operativa que emergió en H023
(verificar cada mecanismo contra el `.md` crudo antes de declararlo).

Método aplicado en los cuatro casos: pedir bordes exactos del bloque
al localizador (`output/localizacion/fallos_localizados.csv`),
extraer el bloque al archivo `.txt`, aplicar regex reales del parser
mecánicamente (RE_APERTURA, RE_FECHA_LINEA, RE_DICT_HDR, RE_VOTO_HDR,
RE_DISID_HDR), interpretar matches contra la estructura del bloque, y
recién ahí formular hipótesis sobre causa raíz para verificación
dirigida del código. Los `.txt` quedan en raíz del repo, pendientes
de moverse a directorio de output diagnóstico (ver §H024.pendientes).

### M5 confirmado, etiología corregida: B044 nuevo

Testigo `332_p244` (Fernández c/ Federación de Asociaciones Católicas
de Empleadas Asoc. Civil). Bloque `LibroVol332.1.md` líneas 9536-9713
(178 líneas, gap +7 según H022). Carátula real en L13-14, apertura
del FALLO en L62.

**Hipótesis H022 (etiología):** "el caso publica primero una sentencia
per saltum vieja con voto de Petracchi y después el fallo plenario
del propio caso; el parser matcheó el header de la per saltum y
abrió un span voto de 114 líneas que se tragó la sentencia plenaria
entera". El `n_votos=3` resultaba de span voto espurio + dos votos
legítimos al final.

**Verificación contra `.md`:** RE_VOTO_HDR matchea tres veces sobre el
bloque: L3 ("Voto del señor ministro" + L4 "doctor don Enrique
Santiago Petracchi"), L117 ("Voto de los señores ministros doctores"),
L166 ("Voto del señor ministro"). El match L3 ocurre **antes** de la
carátula (L13-14) y de la apertura del FALLO (L62), y antes del
dictamen del Procurador del propio caso (L41). El cierre del voto
unipersonal en L12 con firma simple "Enrique Santiago Petracchi."
muestra que **L3-L12 son arrastre completo de un fallo anterior** —
una resolución de competencia (Santa Fe vs Juzgado Civil 26 sobre
quiebra), no una per saltum del propio caso. Los matches de L117 y
L166 son legítimos del caso Fernández ("según su voto" en la firma
colegiada de L114-116).

**Verificación contra el código (parser.py 1513-1552):** el loop
principal de `procesar_archivo` arranca en `k=0` y recorre todo el
bloque. No hay guardia espacial tipo `if k < apertura_rel: continue`
ni `if k < idx_caratula: continue` antes de aplicar
`RE_VOTO_HDR`/`RE_DISID_HDR`/`RE_DICT_HDR`. La protección de
`en_dictamen` (1518-1529) sólo cubre matches dentro del dictamen
ya detectado. El match espurio de L3 entra al `marcadores_votos`
sin filtrado.

**Mecanismo confirmado, causa raíz refinada:** composición de B022
(arrastre del previo) + falta de guardia espacial. Pero el arrastre
en `332_p244` no es V1 ni V2 conocidos: arrastra **un voto unipersonal
entero** del previo (header `Voto del señor ministro doctor don X` +
`Autos y Vistos:` + cuerpo del voto + firma simple), ~10 líneas. Se
abre **variante V2b** de B022.

**Daño cuantificado:** el span voto resultante se extiende desde L3
hasta el siguiente marcador de voto en L117 (cuando `extraer_textos_votos`
parser.py 559-582 toma el rango hasta el próximo marcador). 114 líneas
envueltas como "voto Petracchi del caso Fernández" que en realidad
contienen carátula + sumarios + dictamen + cuerpo plenario + firma
colegiada de la mayoría del Fernández. El conteo `114 líneas` cuadra
con la cifra reportada por H022.

**Se abre B044** (parser, `confirmado_mecanismo`) con causa raíz
acoplada a B022 V2b y al loop de votos. Fix: dos vías independientes
(fijar B022 elimina el arrastre; introducir guardia espacial cubre
una familia de bugs análogos en otros detectores).

### M4 confirmado, B022 V1 desdoblada en V1a/V1b

Testigo `330_p829` (Brandsen c/ AFIP-DGI). Bloque `LibroVol330.1.md`
líneas 31412-31591 (180 líneas, gap +7).

H022 reportó que las primeras 25 líneas son cierre del fallo anterior
(recurso de hecho ANSeS con firma colegiada y "Tribunal de origen:")
antes de la carátula real del Brandsen partida en tres líneas. H023
incorporó el caso como testigo a B022 V1 sin verificar contra `.md`.

**Verificación contra `.md`:** los matches regex sobre el bloque son
RE_APERTURA en L141, RE_FECHA_LINEA en L142, RE_DICT_HDR en L60,
RE_DISID_HDR en L165, y RE_VOTO_HDR sin matches. L1-25 no disparan
ningún match estructural. L22 es la firma colegiada del fallo anterior
(Lorenzetti/Fayt/Petracchi/Maqueda/Argibay). L25 contiene "Tribunal de
origen: Cámara Federal de la Seguridad Social, Sala II" del ANSeS. La
carátula real del Brandsen está partida en L27-29 con formato editorial
viejo de tomos 329-330 ("V." en mayúsculas, conectado con B026).

**Verificación del daño concreto:** `find_tribunal_origen` (parser.py
383-412) recorre desde `idx_inicio` del bloque y devuelve el **primer**
match de `RE_TRIB_ORIG`. En `330_p829` captura "Cámara Federal de la
Seguridad Social, Sala II" de L25 (del ANSeS arrastrado) en lugar de
"Sala III, Cámara Federal de la Seguridad Social" del Brandsen (después
de L165). El campo `tribunal_origen` del CSV de producción queda
contaminado. `extraer_caratula_v1` (parser.py 170) captura bien el
case_name desde el "Vistos los autos:" del FALLO real en L143-145
(buscado desde apertura_rel hacia adelante, fuera del rango del
arrastre). `find_case_name` (parser.py 344) hubiera fallado (carátula
con "V." no matchea su búsqueda de "c/" en `max_back=15`), pero como
Fix 1 prima V1 sobre find_case_name, el daño no llega al CSV.

**Refinamiento de B022:** la variante V1 actual ("firma + metadatos
editoriales, ~5-25 líneas") subsume dos sub-patrones distintos. El
arrastre en `330_p829` (25 líneas con considerandos argumentales 3°-5°
+ dispositiva + firma + pie editorial + tribunal de origen) no es lo
mismo que el arrastre chico de Sivaslian/Cerboni/Macri/Lavrentiev
(~5-15 líneas con sólo firma + metadatos). Se distinguen V1a (chica,
≤15 líneas, sólo firma + metadatos) y V1b (grande, 15-30 líneas,
incluye considerandos del cuerpo del previo). La distinción importa
porque V1b incluye texto argumental que aumenta el residuo del
auditor y porque genera daño específico en `find_tribunal_origen`
cuando el arrastre incluye el pie editorial completo del previo.

### Caso huérfano 346_p1205: doble corrección de H022 + H023

Testigo `346_p1205` (Álvarez c/ EN - M° RREECI Cancillería). Bloque
`LibroVol346-2.md` líneas 16883-16988 (106 líneas).

**Hipótesis H022:** "el parser detecta correctamente cuerpo + firma
de una primera dispositiva breve, pero el caso continúa con sumarios
+ un segundo `FALLO DE LA CORTE SUPREMA` con su dispositiva extendida.
Hay dos resoluciones distintas (10-oct-2023 y 19-oct-2023) en el mismo
expediente". H022 lo nombró M3 ("cuerpo cerrado antes de dispositiva
extendida, doble fallo en mismo caso").

**Refutación de H023:** "Lectura del .md mostró un único fallo, una
única dispositiva, fecha única (10 de octubre de 2023). La afirmación
de H022 sobre dos resoluciones no se sostiene en el .md. Hipótesis
abierta: el bloque está dominado por el dictamen del Procurador".

**Verificación contra `.md` (H024):** matches sobre bloque + extensión
post-16988 muestran tres RE_APERTURA (L3, L45, L152) y tres
RE_FECHA_LINEA (L4=10/10/2023, L46=19/10/2023, L153=19/10/2023). El
fallo de L3-15 (10/10/2023) **no es del caso Álvarez** — es una
resolución sobre conflicto de competencia entre Juzgado Federal de
la Seguridad Social n°4 y Contencioso Administrativo n°20 CABA, sin
relación con la carátula del Álvarez (M° RREECI sobre reintegro de
gastos médicos en Shanghái). El fallo del Álvarez arranca en L45-46
(19/10/2023) y se extiende por considerandos 1°-4° hasta L107, donde
el bloque del catálogo termina **al medio del considerando 4°**.

La extensión (líneas absolutas 16989 en adelante) muestra que el
fallo Álvarez continúa por ~34 líneas más (considerando 4° final + 5°
+ "Por ello, se declara procedente" + firma colegiada
Rosatti/Rosenkrantz/Maqueda/Lorenzetti + pie editorial). El caso
siguiente del catálogo (`346_p1208`, Frigorífico Paladini, según
`fallos_localizados.csv` fila 5280) arranca en línea 16989, es decir
**al medio del fallo Álvarez**.

**Doble corrección:**
1. H022 erró en la etiología: las dos fechas son de dos casos
   **consecutivos distintos**, no del mismo expediente. M3 como
   mecanismo de "doble dispositiva legítima" no existe.
2. H023 también erró: leyó las primeras líneas, vio una sola fecha
   en L4 ("10 de octubre de 2023") y supuso que era del caso, sin
   notar la segunda fecha en L46 ("19 de octubre de 2023"). La regla
   "leer el .md crudo" se cumplió, pero la lectura fue incompleta.

**Lección metodológica adicional:** la regla de H023 ("verificar
contra `.md` crudo antes de declarar") se refuerza con un paso de
identificación previa: localizar la **carátula real** del caso antes
que cualquier otro marcador. Carátula primero, después dispositiva,
firma, dictamen — no por orden de aparición en el bloque. Si H023
hubiera identificado la carátula del Álvarez (L17-18, ÁLVAREZ
ARMANDO DAVID) antes que la fecha de L4, habría notado de inmediato
que el FALLO de L3 no podía pertenecer al Álvarez.

**Diagnóstico real de 346_p1205:**
- **B022 V2** al inicio del bloque (L3-L15 = fallo completo del caso
  anterior con FALLO + Autos y Vistos + dispositiva + firma colegiada,
  ~15 líneas). Mismo patrón que `332_p913` (también re-asignado en
  H023 a B022 V2). Se suma como segundo testigo de V2.
- **Truncamiento al final** del bloque (~34 líneas del fallo Álvarez
  quedan fuera del bloque del catálogo, asignadas al bloque siguiente
  `346_p1208`). Esto **no tiene ID en DEUDA_TECNICA actual** —
  componente catálogo (etapa 2) o cruzador (etapa 3), distinto de
  B011 (caso aislado) y de B012 (`linea_fin` extendido). Acá es
  `linea_fin` **acortado**. Se abre **B045**.

### M1 confirmado, B025 sube a confirmado_mecanismo

Testigo `343_p2243` (Salvatierra y Otros s/ Daño agravado). Bloque
`LibroVol343-3.md` líneas 30534-31027 (494 líneas, gap +485, el más
extremo de la muestra H022).

**Hipótesis H022:** el parser detectó una firma real
(Rosenkrantz/Maqueda/Lorenzetti/Rosatti) en líneas 30541-30542 y cerró
el fallo ahí. Esa firma pertenece al fallo anterior; el Salvatierra no
había arrancado. Las 485 líneas del gap son cuerpo + dictamen + sumarios
+ firma de la Corte del fallo real.

**Verificación contra `.md`:** extracto inicio (30534-30563) + extracto
fin (30987-31027). Cero matches estructurales (RE_APERTURA,
RE_FECHA_LINEA, RE_DICT_HDR, RE_VOTO_HDR, RE_DISID_HDR) en ambos
extractos. Las 423 líneas del medio (30564-30986) no fueron chequeadas
con regex, no necesario.

- **Inicio:** L1-2 header de página. L3-9 cierre del fallo anterior
  "Gente Grossa S.R.L." sobre publicación satírica, dispositiva
  "se rechaza la demanda" en L7-8, firma colegiada
  Rosenkrantz/Maqueda/Lorenzetti/Rosatti en L8-9 (líneas absolutas
  **30541-30542 — exactamente las que H022 reporta**). L10-14 pie
  editorial. L16-17 carátula real del Salvatierra. L19-31 sumarios.
- **Fin:** L1-39 cuerpo argumental (considerandos 3°-4° con citas
  Fallos 155:374, 312:1042, 329:1219). L41 "2255" (número de página).
  **No hay "Por ello", no hay dispositiva, no hay firma del Salvatierra
  dentro del bloque del catálogo.**

**Verificación del código (parser.py 1153-1234, `detectar_fin_real`):**
- Pista 1 (carátula del siguiente, líneas 1189-1202): falla. No hay
  matches del `primer_token_siguiente` ni dentro del bloque ni en
  el rango `limite_adelante`.
- Pista 2 (header de sumario, 1204-1212): falla. La mitad inferior
  del bloque es cuerpo argumental del Salvatierra, sin headers de
  sumario.
- Pista 3 (RE_APERTURA o RE_DICT_HDR del siguiente, 1214-1223):
  falla. La apertura del fallo siguiente está más allá de
  `lfc + 200 ≈ 31227`.
- Fallback (1225-1231): `buscar_atras(linea_es_firma_de_juez, lfc=31027,
  li=30534)`. Como la firma del Salvatierra fue truncada por el bug
  catalográfico, no la encuentra al retroceder. Encuentra primero la
  firma del Gente Grossa en 30542. **Cierra ahí, status
  `fin_por_firma_actual`, pista `firma_actual`.**

**Caso resultante:** cuerpo de ~9 líneas (sólo el arrastre del Gente
Grossa procesado, las 485 líneas restantes del Salvatierra quedan
como catch_all), firma del previo capturada, `voting_pattern=unanime`
espurio. Este es **el mecanismo concreto de B025** (414 falsos `unanime`).

**Cambios a B025:** sube de `sospecha_cardinal` a `confirmado_mecanismo`.
Causa raíz refinada como composición:
1. Bug catalográfico de frontera (B045 nuevo): truncamiento del caso
   al fin del bloque deja al `detectar_fin_real` sin firma real para
   anclar.
2. Arrastre del previo al inicio (B022 V1b típicamente): provee la
   firma alternativa que el fallback captura.
3. Fallback de `detectar_fin_real` (parser.py 1225-1231): busca hacia
   atrás sin verificar si la firma pertenece al caso actual o a
   contenido arrastrado.

### B045 nuevo — Bug catalográfico de frontera mal puesta

Componente: catálogo (etapa 2) o cruzador (etapa 3) — causa raíz a
nivel de quién decide las fronteras entre casos consecutivos.

Caracterización: cuando una página del PDF contiene **final del caso N
+ inicio del caso N+1** (típico cuando el cierre del N termina al
medio de página y el N+1 arranca en la misma página), el catalogador
asigna la **página entera** al caso N+1. Resultado simultáneo:
- Caso N queda **truncado** antes de su dispositiva/firma.
- Caso N+1 hereda **arrastre del caso N** al inicio del bloque
  (= B022).

Los dos síntomas son **las dos caras del mismo bug**. B022 venía
documentando sólo la cara visible desde el parser (arrastre al
inicio). B045 documenta la cara del catálogo y unifica el cuadro
causal.

Testigos verificados en H024:
- `343_p2243` (Salvatierra): truncamiento al medio del considerando 4°,
  hereda al caso siguiente.
- `346_p1205` (Álvarez): truncamiento al medio del considerando 4°,
  hereda al `346_p1208` (Paladini).

**B045 acopla con:**
- **B022** (arrastre al inicio del bloque siguiente): mismo bug visto
  desde la otra cara. Fix de B045 a nivel catálogo elimina B022 por
  construcción.
- **B025** (414 falsos `unanime`): cuando B045 trunca antes de la
  firma real, `detectar_fin_real` cae al fallback de firma y captura
  la del previo arrastrado. Fix de B045 elimina B025 por
  construcción.
- **B044** (apertura espuria de span voto): cuando B045 + B022 V2b
  arrastra un voto unipersonal entero, B044 se dispara. Fix de B045
  reduce el universo de B044 (pero no lo elimina del todo: B044
  también puede activarse por arrastres V2b que no impliquen
  truncamiento).

### Hallazgo arquitectónico

H024 establece que **B045 es la causa raíz común de M1, M3-refutado,
M4 y M5**. Las cinco hipótesis de mecanismo de H022, después de
H023 + H024:

| Hipótesis H022 | Status final | Bug actualizado |
|---|---|---|
| M1 (cierre por firma falsa) | Confirmado | B025 (refinado a `confirmado_mecanismo`) |
| M2 (cierre por carátula falsa) | Confirmado en H023 | B018 (`confirmado_mecanismo` + B043) |
| M3 (doble dispositiva legítima) | Refutado | Inexistente; ambos testigos eran B022 |
| M4 (mala localización inicio) | Confirmado | B022 (V1 desdoblada en V1a/V1b) |
| M5 (apertura espuria span voto) | Confirmado con etiología nueva | B044 nuevo |

De los cinco mecanismos propuestos por H022, **cuatro tienen causa
raíz común en B045** (frontera catalográfica mal puesta). El único
mecanismo independiente es **B018/M2**, que puede dispararse aún sin
arrastre por el defecto de `primer_token_de_caratula` (B043) en
carátulas con sustantivos institucionales genéricos.

**Consecuencia para priorización de fix:** B045 es prioridad máxima
arquitectónica. Su fix elimina B022/B025/B044 por construcción y
reduce el universo de B018. La opción D recomendada para B018 en
H023 (validación cruzada con `proximo_header_pagina`) podría ser un
patrón aplicable también para detectar y corregir las fronteras mal
puestas de B045.

### Cambios aplicados a DEUDA_TECNICA en esta sesión

- **B022** reescrito: causa raíz movida a "B045 visto desde el lado
  parser". Variantes refinadas a V1a/V1b/V2/V2b (cuatro testigos
  verificados en H024 cubren las cuatro variantes). Sección de
  interacciones ampliada (acopla con B045, B025, B044 además de
  B018).
- **B025** subido de `sospecha_cardinal` a `confirmado_mecanismo`.
  Causa raíz refinada (composición B045 + B022 + fallback parser.py
  1225-1231). Testigo verificado `343_p2243`.
- **B044** abierto: apertura espuria de span voto sobre header
  arrastrado del previo. Composición B022 V2b + falta de guardia
  espacial en loop de parser.py 1513-1552. Testigo `332_p244`.
  Estado `confirmado_mecanismo`.
- **B045** abierto: frontera catalográfica mal puesta entre casos
  consecutivos. Causa raíz arquitectónica común de B022/B025/B044.
  Testigos `343_p2243`, `346_p1205`. Componente: catálogo o
  cruzador. Estado `confirmado_caso_testigo`.

### Pendientes inmediatos

1. **Mover archivos diagnóstico:** los `.txt` generados en raíz del
   repo (`bloque_332_p244.txt`, `bloque_330_p829.txt`,
   `bloque_346_p1205.txt`, `bloque_346_p1205_extension.txt`,
   `bloque_343_p2243_inicio.txt`, `bloque_343_p2243_fin.txt`)
   deberían moverse a un directorio dedicado, e.g.
   `output/auditoria/auditar_fallo/h024_blocks/`. Esto al cierre o
   en sesión de housekeeping.

2. **Diagnóstico al nivel código de B045:** abrir
   `scripts/pipeline/construir_catalogo.py` (etapa 2) o el equivalente
   del cruzador (etapa 3) e identificar la lógica que decide las
   fronteras entre casos. Hipótesis fuerte: la asignación de página
   entera al caso N+1 cuando una página contiene cierre del N +
   inicio del N+1. Sesión dedicada.

3. **Fix de B018 (recomendación H023, opción D):** sigue pendiente.
   Vale evaluarlo en conjunto con B045 ahora que se identificó la
   causa raíz arquitectónica común.

4. **Re-medición de cardinalidad de B025** post §3.6.a (B001
   resuelto). H022 estimó 414 casos en el cluster pre-fix. Verificar
   contra CSV vivo (`output/parser/csjn_casos.csv`).

5. **Aplicar fix de B044:** dos vías ya documentadas (fix de B022 vía
   B045, o guardia espacial en parser.py 1513-1552). La primera es
   estructural; la segunda cubre familia de bugs análogos. Decidir
   en sesión dedicada.

### Lección metodológica acumulada (H023 → H024)

La regla operativa de H023 ("verificar mecanismo contra .md crudo
antes de declararlo") se refuerza en H024 con dos correcciones
concretas a H023 mismo:

1. `346_p1205` se había clasificado como huérfano en H023 con
   hipótesis abierta sobre "dictamen domina el bloque". H024 muestra
   que ni hay dictamen en el bloque (`RE_DICT_HDR` = 0 matches) ni
   hay un único fallo. Es B022 V2 + B045. H023 leyó las primeras
   líneas y supuso fecha única.

2. `343_p2243` fue procesado en H024 directo, no había verificación
   previa de H023. Pero el caso aporta una segunda lección:
   identificar la **carátula real** del caso debe ser el primer paso
   de la lectura, antes que dispositiva/fecha/firma. La carátula
   ancla el caso; los otros marcadores sin carátula identificada
   pueden ser arrastre o caso anterior.

Regla operativa actualizada para sesiones futuras:
1. Pedir bordes exactos al localizador.
2. Aplicar regex mecánicamente sobre el bloque.
3. **Identificar carátula real primero.** Después dispositiva, fecha,
   firma, dictamen.
4. Verificar arrastre al inicio (B022) y truncamiento al fin (B045)
   como pasos separados.
5. Recién entonces formular hipótesis de mecanismo y verificar contra
   el código.

6. **Actualizar `README.md` global del repo:** desactualizado desde
   antes del sprint 2026-05-09. No refleja la estructura actual
   (`scripts/pipeline/` + `output/{catalogo,mapa,localizacion,parser,auditoria}/`),
   sigue documentando rutas viejas (`paginas/`, archivos `_v15.csv`
   en raíz), no menciona `auditar_fallo.py` (herramienta central de
   diagnóstico desde H013), no menciona la carpeta de outputs de
   auditoría, mantiene lenguaje de "Bug D" ya cerrado. Sesión
   dedicada de housekeeping, idealmente cruzada con el inventario
   de zona DUPLICADA y zona OLVIDADA (H020 Fases 1-2).

## H025 — Reflexión arquitectónica sobre el pipeline: dos manifestaciones de B045, propuesta de gramática del fallo (16/5/2026)

Continuación de H024. Plan original: reflexión profunda sobre cómo
funciona el pipeline en conjunto, mapeando el orden de operaciones y
los acoplamientos entre las cuatro etapas, con foco en comprobar la
declaración fuerte de H024 ("fix de B045 elimina B022, B025, B044 y
subset V1 de B018 por construcción"). Seis fases previstas: mapa
estructural (1), modelo conceptual del catálogo y cruzador (2),
ballet del parser (3), comparación contra auditor (3-bis), experimento
mental de bugs sobrevivientes (4), matriz de opciones de fix (5),
roadmap (6).

La sesión avanzó por las fases 1, 2 y 3. A mitad de fase 3 emergió
una propuesta arquitectónica alternativa que reorientó el cierre de
la sesión hacia documentarla. Las fases 3-bis, 4, 5 y 6 se posponen
a H026.

### Fase 1: mapa estructural del pipeline

Inventario de funciones top-level y docstrings de los cinco scripts
relevantes: `detectar_paginas.py` (551 líneas), `construir_catalogo.py`
(650), `cruzar_catalogo_y_mapa.py` (435), `parser.py` (1.944),
`auditar_fallo.py` (1.729). El auditor tiene volumen comparable al
parser, no es herramienta auxiliar — es un segundo parser con
arquitectura diferente: funciones `segmentar_bloque`,
`_agregar_catch_all`, `_ordenar_y_validar` no existen en el parser
y sugieren un modelo de spans tipados con cobertura total e
invariante de "toda línea pertenece a al menos un span". El docstring
del auditor declara explícitamente que "REUSA por importación los
regex y helpers de parser.py. No reimplementa heurísticas. Si una
heurística está rota en parser.py, acá va a estar igual de rota". La
hipótesis previa de que el auditor segmenta mejor que el parser por
tener mejor información queda descartada: la diferencia tiene que
estar en cómo procesan, no en qué reciben.

`fallos_localizados.csv` se identifica como **frontera arquitectónica**
del pipeline. Es el output de etapa 3 y el input compartido del parser
de producción y del auditor. Cualquier defecto aguas arriba (catálogo
o cruzador) se propaga simétricamente a ambos. Cualquier divergencia
entre parser y auditor sobre el mismo caso es divergencia en el
procesamiento del bloque, no en su acotación.

### Fase 2: las dos manifestaciones de B045

Lectura dirigida de `construir_catalogo.py` y `cruzar_catalogo_y_mapa.py`
con foco en cómo se decide la frontera entre casos consecutivos.

**Hallazgo H025-F2-01.** B045, tal como está documentado en
DEUDA_TECNICA con seis testigos, mezcla dos manifestaciones distintas
del mismo defecto arquitectónico. La separación de ambas surge del
análisis de las decisiones de cada etapa.

`construir_catalogo.py` línea 410 escribe
`pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]`. **No resta uno.**
El docstring del archivo (línea 57) y de la función (línea 381)
prometen "(página del siguiente fallo − 1)" pero el código asigna
directamente la página de inicio del siguiente, sin transformación.
La discordancia ya estaba documentada en PIPELINE §2.5.a. Lo que H025
agrega es la consecuencia aguas abajo.

`cruzar_catalogo_y_mapa.py` línea 245 escribe
`out['linea_fin'] = linea_fin_header - 1`. Es decir, busca el header
de página de `pagina_fin` (que es la página de inicio del siguiente)
y le resta uno para obtener la última línea del caso actual. Esta
resta es correcta cuando los casos están en páginas físicas distintas.
Cuando dos casos comparten una sola página, el header de
`pagina_inicio` del actual y el header de `pagina_fin` del actual son
**la misma línea** del `.md`, y la operación produce
`linea_fin = linea_inicio − 1`. El bloque queda vacío o de longitud
negativa.

Grep sobre el cruzador confirma que **no hay guarda**: línea 175
(arriba) hasta 281 (abajo) no contiene ninguna validación de
`linea_fin vs linea_inicio`, ningún warning, ninguna comparación
entre filas consecutivas del catálogo. El status escrito en el caso
degenerado sigue siendo `'ok'`.

Las dos manifestaciones que se distinguen son:

- **Manifestación A — caso desaparecido (silenciosa).** Cuando dos
  casos comparten una sola página, el caso N recibe del cruzador un
  bloque vacío. `procesar_archivo` en `parser.py` línea 1365-1367
  hace `bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin); if not bloque: continue`.
  El caso se saltea **silenciosamente** sin warning, sin contador, sin
  log. La fila no aparece en `csjn_casos.csv` o aparece con campos
  vacíos. Sub-diagnosticado en H022/H024 porque no produce filas con
  error en el CSV: produce ausencia de fila, que es invisible salvo
  que se compare conteos catálogo vs CSV.

- **Manifestación B — bloque con arrastre.** Cuando dos casos no
  comparten página única pero el cierre del N físicamente cae dentro
  de la página de inicio del N+1 (escenario típico en `343_p2243`,
  `346_p1205`), el bloque del N queda truncado al final y el bloque
  del N+1 hereda el cierre del N como arrastre. Es la manifestación
  ya documentada en B045 con sus seis testigos y la responsable de
  B022, B025, B044.

H024 había declarado a B045 como causa raíz arquitectónica común de
B022, B025, B044 y subset V1 de B018. H025 refina esa declaración:
B045 es causa raíz pero produce **dos modos de falla distintos** que
requieren tratamiento separado, incluso si comparten origen.

**Observación lateral sobre la composición de redundancias.** El
`pagina_fin` sin restar en el catalogador (línea 410) y el
`linea_fin_header - 1` en el cruzador (línea 245) constituyen una
**redundancia arquitectónica**: dos etapas implementando media operación
cada una sin saber la otra. Cuando los casos están en páginas
distintas, las dos mitades se complementan y el resultado es correcto.
Cuando comparten página, las dos mitades se cancelan y producen
bloque vacío. La memoria de H022 registra que el `-1` fue removido
deliberadamente del catalogador para mejorar `sin_firma` aguas abajo;
pero la remoción se hizo sin verificar si otro script ya asumía el
`-1` previo. Hipótesis fuerte de fix: revertir uno de los dos `-1`
restaura coherencia. Pendiente de verificación contra el código
completo del pipeline antes de implementar.

### Fase 3: ballet del parser

Lectura de `procesar_archivo` (parser.py 1326-1620) con foco en orden
de operaciones, decisiones irreversibles y compensaciones documentadas.

**Decisiones tempranas (1326-1500).** Antes del loop por línea, el
parser toma seis decisiones cuyo orden no respeta la estructura
tipográfica del documento que procesa. (1) Construye el bloque desde
la localización del cruzador. Si el bloque es vacío, hace `continue`
silencioso — la guarda que captura sin warning la manifestación A de
B045. (2) Llama a `detectar_fin_real` (parser.py 1153-1234), que
implementa búsqueda en cascada de cuatro pistas para ajustar
`linea_fin`. La cascada es asimétrica: ajusta el final del bloque
pero nunca el principio. Si el bloque tiene arrastre al inicio
(manifestación B), ninguna función lo detecta. (3) Llama a
`detectar_apertura_en_bloque` (parser.py 1034-1051) que devuelve la
primera línea del bloque que matchea `RE_APERTURA`. Cero validación
de contexto. La decisión es irreversible: `apertura_rel` se usa como
referencia para extracción de fecha, carátula y tribunal de origen
sin que ningún paso posterior la revise. (4) Si el bloque matchea
`RE_SUMARIO_LINK`, se trata como nota editorial y se sale del
procesamiento con registro vacío. (5) Se extrae la fecha del fallo,
con comentario explícito del autor (parser.py 1446-1449) reconociendo
que la extracción ocurre antes de la detección de dictamen y que
puede capturar la fecha del dictamen en vez de la del fallo:
"Es lo mejor que podemos hacer sin reordenar el código entero". (6)
Se extrae `case_name_cuerpo` con `extraer_caratula_v1` desde la
posición de apertura, más fallback a `find_case_name`.

**Loop por línea (1513-1564).** Después de las decisiones tempranas,
el parser entra a un loop con prioridades en serie: dictamen primero
(activa estado `en_dictamen` como guarda espacial), después votos y
disidencias, después detección de "Por ello". El estado `en_dictamen`
funciona razonablemente bien — es una pequeña máquina de estados
implícita que protege las líneas del dictamen de ser evaluadas con
regex de voto o de dispositiva. Pero llega tarde: la decisión sobre
`apertura_rel` ya está tomada cuando el loop empieza.

**Post-loop (1565-1620).** `collect_firma_lines` arranca desde
`por_ello_idx + 1`. Si `por_ello_idx` quedó mal por una apertura
espuria, la firma recogida puede ser de un voto y no de la mayoría.

**Tres compensaciones documentadas en código.** El parser tiene tres
parches defensivos contra problemas arquitectónicos que el autor
reconoció pero no resolvió. (a) Guardia de sumario-con-link
(parser.py 1410-1421): comentario explícito sobre que en bloques con
solapamiento de páginas la firma detectada puede pertenecer al fallo
anterior, por eso se ignora cuando el bloque matchea
`RE_SUMARIO_LINK`. (b) Orden de extracción de fecha (1446-1449,
citado arriba). (c) Fallback de fecha en tres niveles (1471-1476)
cuando la lógica nueva no encuentra. Tres soluciones locales para un
mismo problema: el orden de operaciones está mal pero parcharlo es
más barato que repensarlo.

**Acoplamiento B018 → `detectar_fin_real` no documentado en
DEUDA_TECNICA.** La pista 1 de `detectar_fin_real` (parser.py 1190)
usa `primer_token_siguiente` como ancla de búsqueda. Si el primer
token del caso siguiente es genérico (B018 documentado en
DEUDA_TECNICA con `primer_token_de_caratula` capturando sustantivos
institucionales como "RECURSO" o "BANCO"), la regex de la línea 1191
puede matchear cualquier mención del token dentro del bloque del
caso actual, induciendo cortes prematuros. B018, hasta ahora
documentado como bug puntual de detección de carátula, también
contamina la detección de fin del caso anterior. Acoplamiento abierto
para anotar en DEUDA_TECNICA al cierre de H025.

### Reorientación de la sesión: propuesta de gramática del fallo

A mitad de Fase 3, en intercambio sobre el orden de operaciones del
parser, emergió una propuesta arquitectónica alternativa: que el
parser respete el orden tipográfico del documento (carátula →
sumarios → dictamen → fallo → firma → votos y disidencias → cierre
editorial), modelando la estructura como una gramática en la que
cada sección detectada define qué secciones son válidas a
continuación. La idea creció en sucesivos intercambios hasta
incorporar dos componentes adicionales: (a) validación de transiciones
entre secciones como mecanismo de auto-corrección frente a arrastres
(una transición FIRMA → CARATULA es violación de gramática y señal
de que el bloque contiene dos casos pegados); (b) diálogo entre
bloques vecinos para resolver el caso específico de páginas
compartidas (una firma huérfana al inicio del bloque N+1 pertenece
al caso N, y reasignarla resuelve B045 sin tocar el catálogo ni el
cruzador).

La propuesta queda documentada en `docs/GRAMATICA_DEL_FALLO.md` como
borrador conceptual sin compromiso de implementación. El documento
desarrolla las tres formas posibles de implementación (dos pasadas
separadas; una pasada con vista relacional; convergencia iterativa)
con pros y contras de cada una, y recomienda preliminarmente empezar
por Forma 1 sólo pasada 1 — gramática local sobre cada bloque sin
diálogo entre vecinos — para validar el modelo antes de agregar
complejidad. Incluye dos diagramas: el de las dos manifestaciones
de B045 (motivación) y el del ballet actual del parser (contraste).

Pregunta abierta y aplazada a H026: cuánto de esta propuesta ya está
implementado en `auditar_fallo.py`. La lectura preliminar de nombres
de funciones (`detectar_apertura_mayoria`, `_ordenar_y_validar`,
`_agregar_catch_all`) sugiere que el auditor implementa una versión
parcial de la gramática. Si la lectura detallada lo confirma, el
camino a implementación se acorta: no sería refactor desde cero del
parser, sino promoción del auditor a parser de producción con el
agregado de validaciones de transición. Fase 3-bis original de H025
se reanuda en H026 con foco específico en esta hipótesis.

### Decisiones tomadas en H025

Más allá del documento conceptual, H025 produce cuatro cambios
operativos en los archivos del proyecto:

(a) **B045 refinado** en DEUDA_TECNICA con bloque "Refinamiento
H025" agregado al final de la entrada vigente, sin tocar el texto
previo. Separa las dos manifestaciones, identifica las líneas de
código exactas (catalogador 410, cruzador 245), marca como completado
el diagnóstico a nivel código que H024 había declarado pendiente,
referencia el documento `docs/GRAMATICA_DEL_FALLO.md` como propuesta
arquitectónica de fix.

(b) **B046 abierto** para la manifestación A (casos desaparecidos
por bloque vacío en el cruzador). Estado de verificación:
`abierto_pendiente_de_medicion`. Acción inmediata propuesta: contar
sobre `catalogo.csv` cuántas filas tienen `pagina_fin == pagina_inicio`
del caso siguiente del mismo tomo y comparar contra `csjn_casos.csv`
para cuantificar la magnitud.

(c) **B018 ampliado** con nota de acoplamiento a `detectar_fin_real`
pista 1 (parser.py 1190). Hasta H024, B018 figuraba como bug puntual
de detección de carátula. H025 documenta el efecto colateral sobre la
detección de fin del caso anterior.

(d) **M01 actualizado** en alcance: la sesión pendiente de
re-recorrer parser.py y actualizar PIPELINE.md ahora debe incorporar
también B045 manifestaciones A/B, B046, el acoplamiento B018 →
detectar_fin_real, y eventualmente referenciar `GRAMATICA_DEL_FALLO.md`
como insumo conceptual.

PIPELINE.md recibe cuatro fricciones nuevas o ampliadas (§2.5.a con
consecuencia aguas abajo del `pagina_fin` sin restar; §3.5 con
escenario degenerado del bloque vacío; §3.9 con F3.9.d sobre el
silenciamiento por la guarda de bloque vacío en parser; §4 con
asimetría de `detectar_fin_real` y acoplamiento con B018).

### Pendientes para H026

Fases 3-bis, 4, 5, 6 del plan original.

Específicamente:

- Lectura detallada de `auditar_fallo.py` para verificar cuánto de la
  gramática propuesta ya está implementado.
- Medición empírica sobre `catalogo.csv` y `csjn_casos.csv` de la
  cardinalidad de B045 manifestaciones A y B (cuántas filas con
  `pagina_fin == pagina_inicio_siguiente`, cuántas terminan en CSV con
  campos vacíos, cuántas son caso N+1 con apertura sospechosa).
- Experimento mental bifurcado: qué bugs sobreviven a un fix de B045
  manifestación A, qué bugs sobreviven a un fix de B045 manifestación
  B, qué bugs son independientes de ambos.
- Matriz de opciones de fix con criterios estandarizados (costo,
  riesgo, cobertura).
- Roadmap propuesto para sesiones siguientes.

### Pendientes operativos

- Los archivos `.txt` de bloques producidos en H024 (`h024_blocks/`)
  siguen en raíz del repo, pendientes de moverse a directorio de
  output diagnóstico. Heredado de H024.

- Snapshot de DEUDA_TECNICA.md previo a las modificaciones de H025,
  para preservar el estado pre-edit según M04 (convención de
  snapshots cubren todo archivo modificable).

### Notas metodológicas

H025 confirmó dos reglas operativas heredadas. (1) Verificar contra
el código vivo, no contra la documentación: la inconsistencia del
catalogador entre docstring y código (línea 381 vs 410) habría
pasado desapercibida si se confiaba en el docstring. (2) Identificar
mecanismo antes de proponer fix: el hallazgo de las dos
manifestaciones de B045 sólo aparece al leer el código completo del
cruzador, no al pensar abstractamente en "el catalogador asigna mal
la página".

Una regla nueva surge en H025: las propuestas arquitectónicas se
documentan conceptualmente en `docs/` y se referencian desde
BITACORA y DEUDA_TECNICA, sin pretender implementación inmediata. La
existencia del documento no compromete a actuar; preserva el
pensamiento para sesiones futuras.

### Intento de verificación al cierre, error operativo y revert (16/5/2026)

Después de los cinco commits originales de H025 (`7f23128` →
`2583a3f`), al preparar insumos para H026 se intentó verificar
empíricamente B046 contra el caso `346_p1205`. La verificación se
hizo en dos pasos: corrida del auditor sobre `--pagina 1205` (que
devolvió `346_p1201`, no `346_p1205`) y `Select-String` sobre
`fallos_localizados.csv` con patrón `"346,1205,"` (que devolvió
vacío). De ambos resultados se concluyó erróneamente que `346_p1205`
había desaparecido del corpus.

Con esa conclusión falsa se commiteó `890714a` ("verificación
empírica al cierre"), agregando a BITACORA una sección que declaraba
a `346_p1205` como primer testigo de B046, y a DEUDA_TECNICA una
nota de "Refinamiento post-verificación empírica" sobre B045 con
manifestaciones A y B simultáneas. Ambas afirmaciones falsas.

El error operativo: el patrón `Select-String "346,1205,"` no
matcheaba ninguna fila porque el orden real de columnas de
`fallos_localizados.csv` es
`caso_id_canonico,tomo,archivo,pagina_inicio,pagina_fin,...`. El
literal `346,1205,` no aparece en ese formato. La consulta correcta
(`csv.DictReader` filtrando por columna) muestra que `346_p1205`
está en `fallos_localizados.csv` con líneas 16883-16988 y status
`ok`, **y también está en `csjn_casos.csv` línea 5236** con todos
los campos del fallo procesados correctamente (carátula, firma
Rosatti/Rosenkrantz/Maqueda/Lorenzetti, dispositivo, voting_pattern
unanime, status_fin `fin_extendido_pag_compartida`, pista_fin
`caratula_siguiente`).

**El caso no se evaporó. B046 no tiene testigo empírico.** El commit
`890714a` fue revertido con `52d0bc6` (revert automático con `git
revert --no-edit`).

**Lección operativa.** Una consulta `Select-String` que devuelve
vacío no es evidencia de ausencia hasta que el patrón se valide
contra el formato real del archivo. Regla nueva para sesiones
posteriores: antes de declarar "testigo empírico confirmado", la
verificación debe hacerse por dos vías independientes; si una sola
consulta no encuentra evidencia esperada, el primer paso es validar
la consulta misma, no concluir la ausencia.

### Hallazgos parciales pendientes de procesar en H026

Durante el intento fallido de verificación, varias consultas
laterales aportaron información útil que sí está verificada
cruzadamente y queda como insumo para H026. No se incorporan a
DEUDA_TECNICA ahora porque cada una requiere análisis adicional
antes de afirmar conclusiones; el commit revertido enseñó que
declarar prematuramente cuesta caro.

**Catalogador deduplica por `(tomo, pagina_inicio)`.** Consulta sobre
`catalogo.csv`: pares de filas con el mismo `pagina_inicio` en el
mismo tomo: cero. Coherente con la lógica de `construir_filas_catalogo`
en `construir_catalogo.py` (líneas 388-397): el agrupamiento por
`(tomo, pag)` consolida múltiples entradas del índice editorial bajo
una sola fila con `nombres_indice` separado por `" | "`. Implicación
para B046: el mecanismo escrito en DEUDA_TECNICA ("dos casos del
catálogo comparten `pagina_inicio`") no se manifiesta en el catálogo
real porque la deduplicación lo impide. Si B046 existe como bug
arquitectónico, su mecanismo de manifestación es otro, todavía no
identificado.

**34% del catálogo tiene `n_nombres > 1`.** 2.023 filas sobre 5.862
tienen más de un nombre asociado. Esto es deduplicación legítima del
editor (mismo caso listado bajo nombre del actor, del demandado,
etc.) y no es bug. Importante para H026: si dos casos físicamente
distintos compartían `pagina_inicio` en el índice editorial, el
catalogador los habría fusionado en una fila con `n_nombres > 1`
(carátulas distintas en `nombres_indice`). Para detectar B046
correctamente habría que buscar filas con `n_nombres > 1` donde las
carátulas sean **claramente distintas** (no variantes de un mismo
caso). Plan para H026.

**Auditor con `--pagina N` busca por rango contenedor, no por
`pagina_inicio` exacta.** El primer intento de auditar `346_p1205`
con `--pagina 1205` devolvió `346_p1201` (Osorio), cuyo rango
catalográfico es 1201-1205. Es decir, la página 1205 está cubierta
por el rango del Osorio y el auditor la encuentra ahí. Para auditar
el Álvarez específicamente hay que invocar con su `pagina_inicio`
exacta o con un argumento que diga "caso cuyo `pagina_inicio` es N".
Detalle de interfaz a confirmar en H026 leyendo `_resolver_caso` en
`auditar_fallo.py`.

**Caso `346_p1208` (Frigorífico Paladini) tiene 80.3% de residuo en
auditor.** 106 líneas sin clasificar sobre 132 totales del bloque.
Este caso es el N+1 del par Álvarez-Paladini que H024 documentó
como testigo de B045 manifestación B. El residuo alto del auditor es
consistente con arrastre masivo del Álvarez en el bloque del
Paladini. Este sí es candidato fuerte a inspección detallada en
H026: el output del auditor (en
`output/auditoria/auditar_fallo/auditoria_2026-05-16_05-54-53.md`)
permite ver qué líneas quedaron sin clasificar y dónde está el
límite real entre los dos casos.

**Mecanismo extensión-de-fin operando en Álvarez.** La fila de
`346_p1205` en `csjn_casos.csv` tiene `status_fin =
fin_extendido_pag_compartida` y `pista_fin = caratula_siguiente`. Es
decir, `detectar_fin_real` extendió el bloque del Álvarez **más
allá** de su `linea_fin` catalográfica (16988), llegando hasta 17014
(26 líneas adicionales). Esto es la cara observable del caso que
H024 había caracterizado como B045 testigo: el Álvarez físicamente
extiende hasta dentro de la página de inicio del Paladini, y el
parser lo detecta y compensa. El cuadro de H024 sobre B045
manifestación B sigue siendo válido. Lo que sí cae con el revert es
la idea de "manifestaciones simultáneas": no hay evidencia de
manifestación A en este caso. El Álvarez se procesa correctamente.

**Implicación para B046 en DEUDA_TECNICA.** El mecanismo escrito en
la entrada vigente (cuando dos casos comparten `pagina_inicio`,
bloque vacío) está refutado por la consulta sobre catálogo. La
entrada queda con mecanismo incorrecto. Refinamiento al cierre: la
entrada se ajusta para reflejar que el mecanismo está bajo revisión,
sin pretender un mecanismo alternativo todavía no verificado.

### Estado de cierre H025

Cinco commits originales en `origin/main` con material verificado
contra el código. Un commit revertido (`890714a` → `52d0bc6`)
preserva la trazabilidad del error. Este append documenta lo que
sí se aprendió en el intento. H026 hereda cuatro hipótesis abiertas
sobre B046 y el auditor, listas para investigación dirigida con la
disciplina de verificación cruzada que el error de cierre enseñó.



---

## H026 — Lectura del auditor + gramática empírica del epílogo (primera mitad)

Sesión abierta. Este append documenta lo verificado en la primera
mitad: Fase A parcial (lectura estructural de `auditar_fallo.py`
hasta línea 414, `detectar_borde_inferior` inclusive) + Fase D parcial
(análisis del catch_all sobre corrida `--random 80`). Las Fases B, C,
E, F, G quedan pendientes para continuación.

### Pivote conceptual al inicio de sesión

Conversación inicial sobre el camino arquitectónico hacia Forma 1.
Tres precisiones que redirigen la lectura del auditor:

**El camino no es "promover el auditor a parser".** Es "tomar del
auditor lo que el auditor hace mejor (segmentación tipada con
cobertura total) y combinarlo con lo que el parser hace mejor
(extracción de campos del resumen final: tribunal de origen, fecha,
status, etc.)". El parser ya emite 38 columnas con `tribunal_origen`,
`tribunal_origen_status`, `date`, etc. (parser.py líneas 1858-1874).
Esa lógica de extracción no se reescribe, se traslada al modelo de
spans.

**Falta una sección al modelo de spans del auditor.** El modelo
actual tiene 10 tipos (carátula, sumario, dictamen, cuerpo_mayoria,
voto, disidencia, firma, sumario_con_link, header_pagina, catch_all).
No hay span para el bloque editorial post-firma que contiene partes,
representación letrada, tribunal de origen y tribunales
intervinientes anteriores. Sin span propio, ese material cae en
catch_all (cuando queda dentro del caso correcto) o arrastra al
catch_all inicial del caso siguiente (cuando el detector de fin_real
corta antes).

**El borde superior es estructural, no marginal.** El detector
`detectar_borde_inferior` mira hacia adelante desde `linea_fin_real`
hasta el inicio del próximo caso, pero no hay detector simétrico que
mire hacia atrás desde el inicio del caso actual. Si la primera
página del caso es compartida con el anterior, las líneas previas a
`linea_inicio` pueden contener residuo del anterior. La auditoría
empírica de Fase D (más abajo) confirma que el borde superior es
necesario en la mayoría de los casos del corpus, no en una minoría.

**Las pistas que viajan entre vecinos son indicios, no verdades.**
`primer_token_siguiente` aparece hoy como argumento de
`_clasificar_linea_gap` y dispara clasificación dura (`CLAS_APERTURA_PROXIMO`)
por orden de prioridad: el primer regex que matchea, gana. Un modelo
más robusto trata cada detección como indicio con peso y resuelve
por acumulación o desvirtuación con otros indicios. Conceptualmente
es la diferencia entre parsing por reglas duras y parsing por
evidencia. La lectura del auditor en Fase A se hace con doble lente:
qué decisión dura toma cada función, y qué información disponible no
está usando que podría confirmarla o desvirtuarla.

### Fase A — lectura estructural (parcial)

Cubierto hasta línea 414. Resumen:

**Encabezado y declaraciones (líneas 1-160).** Confirma que el
auditor reusa por importación los regex y helpers de `parser.py`
(líneas 16-20, 57-79): RE_APERTURA, RE_FECHA_LINEA, RE_CONSIDERANDO,
RE_DICT_HDR, RE_VOTO_HDR, RE_DISID_HDR, RE_SUMARIO_LINK,
RE_PAGE_HEADER, RE_TOMO, RE_VISTOS_LOS_AUTOS, y nueve helpers. La
diferencia entre auditor y parser está en cómo procesan, no en qué
reciben. Invariante declarado: toda línea pertenece a al menos un
span (catch_all si nada más matchea). Doble propósito declarado:
output Markdown legible + API canónica `auditar_fallo(tomo, pagina)
-> dict` (la función ya está pensada para uso programático).

**`linea_es_continuacion_firma` (159-211).** Detector con dos
criterios: (1) presencia de apellido titular en
`APELLIDOS_FIRMA_TITULARES` (set hardcodeado de 17 apellidos
cubriendo titulares 329-349); (2) una de tres pistas discursivas
(ratio mayúsculas ≥70%, línea corta terminada en punto/em-dash, o
contiene em-dash/m-dash como separador entre firmantes).
**Limitación visible:** depende del set hardcodeado. Conjueces con
apellido fuera del set no se detectan como continuación de firma.
Esto es relevante para Y.P.F. (caso H025 con cinco firmantes
incluyendo tres conjueces) y para cualquier caso colegiado donde
participe un conjuez. Pendiente medir cuántos apellidos de conjueces
aparecen en el corpus 329-349 fuera del set.

**`_clasificar_linea_gap` (214-253).** Esta función ya implementa
diálogo entre vecinos en la dirección N → N+1: usa
`primer_token_siguiente` (dato del caso siguiente) para clasificar
líneas del gap del caso actual. El orden de prioridad de las seis
clasificaciones está pensado para que la información del vecino
tenga precedencia: `apertura_proximo_caso` se chequea **antes** que
`firma_arrastrada` porque la carátula del próximo caso puede contener
apellidos del set (ejemplo: "MAQUEDA" como parte en una causa).
**Confirma una hipótesis arquitectónica grande:** el diálogo entre
vecinos ya existe parcialmente, en la dirección descendente. Lo que
falta es la dirección simétrica (N+1 mira a N), o sea el borde
superior.

**`detectar_borde_inferior` (256-414).** Cuatro casos terminales
tempranos + un caso productivo. En el caso productivo, clasifica
cada línea del gap y dispara hasta cuatro alertas independientes
(`firma_multilinea_partida_por_fin_real`,
`apellido_repetido_en_firma_arrastrada`,
`voto_disidencia_individual_en_gap`, `caratula_siguiente_en_gap`).
Bloque de comentario explícito (líneas 417-444) documenta una
**versión robusta no implementada**: agregaría búsqueda en ventana
W~10 alrededor de `linea_fin_real` para detectar desvíos sistémicos
del detector de fin. Criterio de activación: si `--random 50` muestra
>10% de falsos positivos en `firma_multilinea_partida_por_fin_real`.
**El criterio nunca se evaluó empíricamente.** La corrida `--random 80`
de esta sesión es una primera medición indirecta (ver Fase D).

### Fase D — análisis empírico del catch_all sobre `--random 80`

Corrida: `python scripts/auditoria/auditar_fallo.py --random 80`
Output: `output/auditoria/auditar_fallo/auditoria_2026-05-16_06-51-29.md`
Resumen de la corrida (header del archivo):

```
Borde inferior: solapado_con_proximo=73, gap_con_residuo=7
Alertas totales: 80
Casos: 80 | Líneas totales: 22.424 | Líneas residuo: 1.731 (7,72 %)
Top residuo: 333_p1732 70,14 % | 332_p1362 49,44 % | 330_p3758 30,0 %
```

**Hallazgo grande #1 — `EST_SOLAPADO` es la norma, no la excepción.**
73 de 80 casos (91,2 %) están en `EST_SOLAPADO`: el catálogo del
próximo caso empieza antes o en la línea declarada como fin del
fallo actual. Solo 7 (8,8 %) están en `EST_GAP_CON_RESIDUO`. Ningún
caso en `EST_CONTINUO`, `EST_HEADER_NORMAL`, `EST_GAP_SOLO_HEADERS`
ni `EST_FIN_ARCHIVO`. Implicación: el parser sistemáticamente extiende
el bloque del caso N más allá del inicio del N+1 según catálogo. El
detector de borde inferior está pensado como diagnóstico de excepción;
la realidad empírica es que casi todos los casos lo disparan.

**Hallazgo grande #2 — distribución de catch_all por posición.** En
los 70 casos con al menos un catch_all (87,5 % del total):

- 62 / 70 (88,5 %) tienen catch_all al inicio del bloque (con o sin
  catch_all final adicional).
- 39 / 70 (55,7 %) tienen catch_all al final del bloque.
- 0 / 70 tienen catch_all solo en el medio: el modelo de spans del
  auditor segmenta bien el interior; el residuo es estructuralmente
  periférico.

El catch_all al inicio es el fenómeno dominante. Esto valida la
necesidad de un detector de borde superior: en ~78 % del corpus el
inicio de bloque viene contaminado.

**Hallazgo grande #3 — clasificación del catch_all inicial por tipo
de bug.** Análisis automatizado sobre los 62 catch_all iniciales,
clasificando por la primera línea del catch_all:

| Tipo | Casos | % | Diagnóstico |
| --- | ---: | ---: | --- |
| `mitad_oracion` | 25 | 40,3 % | Línea comienza con minúscula. Texto del cuerpo del considerando del caso anterior cortado a mitad de oración. **Bug grave de `detectar_fin_real`**: corta dentro del cuerpo del fallo, no en el cierre. |
| `epilogo` | 16 | 25,8 % | Línea comienza con marcador editorial (`Tribunal de origen:`, `Recurso extraordinario interpuesto por`, `Traslado contestado por`, `Nombre de los actores:`, `Parte demandada:`, etc.). **Falta del span `epilogo`** en el modelo del auditor. |
| `por_ello` | 10 | 16,1 % | Línea comienza con "Por ello", "Por lo expuesto", "Por lo tanto". El cierre dispositivo + firma + epílogo del caso anterior arrastrado. **`detectar_fin_real` corta antes del Por ello.** |
| `caratula` | 8 | 12,9 % | Línea es la carátula del caso actual. **Bug del detector de carátula del auditor**: la carátula está en el texto pero no se detecta. |
| `otro` | 3 | 4,8 % | Fragmento ambiguo o caso especial (dictamen mal ubicado, etc.). |

**Reformulación crítica del problema.** Solo el 25,8 % del catch_all
inicial se explica por la falta del span `epilogo` (hallazgo
arquitectónico). El 74 % restante son bugs distintos:

- 40,3 % bug grave de fin_real (mitad de oración).
- 16,1 % bug menor de fin_real (corta antes del Por ello).
- 12,9 % bug del detector de carátula del auditor.

**Implicación:** la promoción del auditor a parser, por sí sola, no
resuelve la mayoría del problema de catch_all inicial. El detector
`fin_real` necesita revisión independientemente del modelo de spans.

**Hallazgo grande #4 — gramática empírica del epílogo.** Análisis de
los 48 catch_all finales (caso con epílogo propio):

Distribución por tamaño:
- 1 línea: 17 casos (35 %)
- 2-3 líneas: 7 casos (15 %)
- 4-10 líneas: 23 casos (48 %)
- 11-30 líneas: 1 caso (2 %)

Tres patrones identificados:

1. **Epílogo propio (23 casos, 48 %).** Tamaño 4-10 líneas. Contenido
   editorial post-firma con orden interno estable:

   ```
   epilogo := continuacion_firma?            ← apellidos cortados
              bloque_recurso?                ← "Recurso [extraordinario/de hecho/...] interpuesto por X, representado por Y"
              bloque_traslado?               ← "Traslado [contestado/recibido] por Z"
              bloque_recurso?                ← puede haber un segundo recurso (caso 339_p919)
              bloque_partes_alt*             ← "Parte actora:" / "Parte demandada:" / "Tercero citado:"
              bloque_nombres_legacy*         ← "Nombre del actor:" / "Nombre de los actores:" (tomos viejos)
              tribunal_origen?               ← "Tribunal de origen: ..."
              tribunales_intervinientes?     ← "Tribunal/es que intervinieron con anterioridad: ..."
   ```

   Todos opcionales, orden estable cuando coexisten. Conviven dos
   convenciones editoriales: "Nombre del actor/demandado:" (tomos
   más antiguos, ej. 329, 330, 333) y "Recurso ... interpuesto por"
   (tomos más recientes, ej. 346-349). La convivencia es real,
   no reemplazo limpio.

2. **Continuación de firma (≈17 casos, 35 %).** Tamaño 1-2 líneas.
   Una o dos líneas con apellido de juez que quedó cortado: "Carlos
   Maqueda.", "Lorenzetti.", "M. ARGIBAY.", "(según su voto)." Esto
   es B045 manifestación A o B operando en escala: el detector
   `linea_es_continuacion_firma` ya existe en el auditor pero solo
   se usa en el borde inferior; no se incorpora al span `firma`.

3. **Ruido editorial / vacío (≈8 casos, 15 %).** Líneas vacías o
   fragmentos editoriales menores benignos. Catch_all que no
   indica bug.

**Hallazgo grande #5 — marcadores explícitos del epílogo.** Cada
componente del epílogo abre con una línea que matchea un marcador
identificable. Lista empírica:

1. `^(Recurso|Recursos)\s+(extraordinario|de\s+hecho|de\s+queja|ordinario|de\s+reposición|de\s+apelación|de\s+revocatoria|directo|directos)\s+(interpuesto|deducido|interpuestos)`
2. `^Traslado\s+(contestado|recibido|del\s+recurso)`
3. `^(Parte|Partes)\s+(actora|demandada|ejecutante|querellante|recurrente|coactora|codemandada)`
4. `^Tercero\s+(citado|interviniente)`
5. `^Profesionales\s+intervinientes`
6. `^Nombre\s+(del|de\s+los|de\s+la|de\s+las)\s+(actor|demandado|demandada|actores|demandados|actoras|demandadas)`
7. `^Tribunal\s+de\s+origen\s*:`
8. `^(Tribunal|Tribunales|Otros\s+tribunales)\s+(que\s+intervino|que\s+intervinieron|intervinientes)`
9. **Continuación de firma**: `linea_es_continuacion_firma` ya existe.

Estos nueve marcadores cubren todos los componentes observados en
los 48 catch_all finales. Pendiente verificar empíricamente la
persistencia editorial en el corpus completo (no en 80 casos).

**Hallazgo grande #6 — el detector de epílogo resuelve borde superior
para el subset epílogo-puro.** Si el detector de epílogo se aplica
"hacia atrás" desde la firma del caso N (extendiendo el span hasta
encontrar la carátula del caso N+1), lo que quede arrastrado al
inicio del N+1 será solo el residuo verdadero (mitad_oracion,
por_ello, caratula-no-detectada). Es decir, **el detector de epílogo
resuelve implícitamente el borde superior para el 25,8 % que es
epílogo puro**. El 74 % restante sigue siendo bug separado.

### Hipótesis abiertas de H025 — estado al cierre de la primera mitad

- **H1 (B046 mecanismo desconocido):** sin investigar todavía. La
  corrida `--random 80` muestra que los 80 casos seleccionados están
  en `csjn_casos.csv`, sin testigos empíricos de B046. Pendiente
  Fase E (comparar `catalogo.csv` 5.862 vs `csjn_casos.csv` 5.819 con
  `csv.DictReader`).

- **H2 (Paladini 80,3 % residuo):** no cayó en la muestra random,
  pero el análisis del catch_all sobre los 80 casos confirma que el
  mecanismo de arrastre del Álvarez sería consistente con la
  distribución observada en el resto del corpus: combinación de
  bugs `mitad_oracion` (40 %) + `por_ello` (16 %) de
  `detectar_fin_real`. No corresponde clasificarlo como bug aislado
  del Paladini; es un caso extremo del fenómeno sistémico.

- **H3 (auditor con `--pagina N` busca por rango contenedor):**
  pendiente. La función `_resolver_caso` (línea 1188) está
  identificada pero no leída todavía. Diferida a Fase A continuación.

- **H4 (`346_p1205` Álvarez procesado con `fin_extendido_pag_compartida`):**
  consistente con todo lo aprendido. La extensión del Álvarez 26
  líneas más allá del catálogo es exactamente el mecanismo de los
  16 catch_all "epilogo" puros y de los 10 "por_ello", combinado.

### Hipótesis nuevas surgidas en H026

- **HN1.** El detector `fin_real` tiene **al menos dos modos de
  falla independientes**, ambos cuantificables en la muestra:

  - **Modo A — corta a mitad de oración del considerando.** 40,3 % de
    los catch_all iniciales. Bug grave. Causa raíz a determinar:
    podría ser pista de fin que matchea texto del cuerpo (falso
    positivo de pista_fin), o regex de cierre que matchea
    prematuramente.
  - **Modo B — corta antes del cierre dispositivo.** 16,1 % de los
    catch_all iniciales. Bug menor pero sistémico. Causa raíz a
    determinar: probablemente RE_CONSIDERANDO o equivalente fallando
    en variantes de "Por ello" (ej. "Por lo expuesto").

- **HN2.** El detector de carátula del auditor falla en
  aproximadamente 12,9 % de los casos del corpus donde la carátula
  está físicamente presente pero no se detecta. Requiere inspección
  de los 8 casos identificados (`331_p1519`, `348_p1352`, `348_p755`,
  `348_p1511`, `340_p1554`, `344_p2669`, `348_p1277`, `343_p988`)
  para identificar el patrón.

- **HN3.** El catálogo `APELLIDOS_FIRMA_TITULARES` está incompleto
  para casos con conjueces. La detección de continuación de firma
  falla cuando el apellido del conjuez no está en el set hardcodeado.
  Pendiente medir cobertura.

### Decisiones operativas

- No tocar código en esta primera mitad. La sesión es de lectura y
  diagnóstico; las modificaciones esperan a tener el mapa completo.
- Anotar gramática del epílogo en `GRAMATICA_DEL_FALLO.md` como
  producción nueva.
- Actualizar `DEUDA_TECNICA.md`: agregar evidencia empírica a B045
  (manifestación B verificada en escala), nota empírica a B046
  (ausencia de testigos en la muestra), e incorporar dos items
  nuevos (B047 — span `epilogo` faltante; B048 — `fin_real` modos
  A y B). Refrescar M-items si corresponde.

### Continuación pendiente

Sesión H026 abierta. Fases pendientes:

- Fase A continuación: leer detectores 4-7 del auditor
  (`detectar_caratula`, `detectar_sumarios`, `detectar_dictamen`,
  `detectar_votos_y_disidencias`, `detectar_firma_mayoria`,
  `detectar_por_ello_mayoria`, `detectar_apertura_mayoria`,
  `detectar_sumario_con_link`), `segmentar_bloque`,
  `_agregar_catch_all`, `_ordenar_y_validar`, `_resolver_caso`.
- Fase B: para cada producción de `GRAMATICA_DEL_FALLO.md`, mapear
  si el auditor la detecta, valida orden, detecta múltiples
  instancias, reporta violaciones.
- Fase C: confirmar que el diálogo entre vecinos N → N+1 está
  implementado en `_clasificar_linea_gap`. Identificar qué le falta
  para la dirección simétrica N+1 → N.
- Fase E: comparar `catalogo.csv` vs `csjn_casos.csv` con
  `csv.DictReader` para verificar B046.
- Fase F: síntesis de reutilización (qué fracción del código del
  auditor se promueve, qué se reescribe, qué es nuevo). Estimación
  en sesiones.
- Fase G (nueva): diseño del detector de borde superior + detector
  de epílogo + integración con la fase de extracción de campos del
  parser.


### Cierre del día H026 — sesión queda abierta

Tres commits realizados al cierre del día:

1. `docs(h026): append bitacora H026 primera mitad - lectura auditor + analisis empirico catch_all sobre random N=80`
2. `docs(h026): actualizar deuda tecnica - B045 evidencia escala, B046 sin testigos, agregar B047/B048/B049/M06`
3. `docs(h026): agregar produccion epilogo a gramatica + refinamiento post-lectura H026`

Estado al cierre del día:

**Lo entregado:** Fase A parcial (lectura del auditor hasta línea
414, `detectar_borde_inferior` inclusive), Fase D completa (análisis
empírico del catch_all sobre `--random 80` con clasificación
cuantificada de 6 hallazgos grandes), gramática empírica del epílogo
con 9 marcadores explícitos, identificación de 3 bugs nuevos
(B047/B048/B049) y 1 ítem metodológico (M06).

**Lo pendiente para H027:**

- Fase A continuación: leer detectores 4-7 del auditor
  (`detectar_caratula`, `detectar_sumarios`, `detectar_dictamen`,
  `detectar_votos_y_disidencias`, `detectar_firma_mayoria`,
  `detectar_por_ello_mayoria`, `detectar_apertura_mayoria`,
  `detectar_sumario_con_link`), `segmentar_bloque`,
  `_agregar_catch_all`, `_ordenar_y_validar`, `_resolver_caso`
  (responde H3).
- Fase B: mapeo producción × auditor (¿detecta? ¿valida orden?
  ¿múltiples instancias? ¿reporta violaciones?).
- Fase C: confirmar diálogo entre vecinos N → N+1 + identificar qué
  falta para N+1 → N.
- Fase E: verificar B046 con `csv.DictReader` — identificar los 43
  casos faltantes entre `fallos_localizados.csv` y `csjn_casos.csv`.
- Fase F: síntesis de reutilización del auditor para parser de
  Forma 1, estimación en sesiones.
- Fase G (nueva, surgida en H026): diseño detector de borde superior
  + detector de epílogo + integración con extracción de campos del
  parser.
- B049 diagnóstico fino: leer `detectar_caratula` con foco en los 8
  casos testigo de la muestra.
- B048 diagnóstico fino de causa raíz: trazar 3-5 casos testigo por
  modo (A y B) línea por línea en `detectar_fin_real`.

Sesión H026 queda **abierta**. H027 retoma desde Fase A continuación.

## H027 — Lectura del auditor completa: detectores 4-12 + orquestador + closers (16/5/2026)

Sesión que cierra Fase A continuación. Documenta: lectura de los
detectores 4-12 del auditor (desde `detectar_headers_pagina` línea
414 hasta `detectar_sumario_con_link` línea 952), del orquestador
`segmentar_bloque` (línea 967), de los closers `_agregar_catch_all`
(línea 1133), `_ordenar_y_validar` (línea 1176) y `_resolver_caso`
(línea 1188). Fase B (mapeo producción × auditor) embebida como
subsección de esta entrada. Fases C, D2, E, F, G quedan pendientes
para H028+.

### Fase A continuación — síntesis por detector

La lectura siguió doble lente: qué decisión dura toma cada función,
y qué información disponible no está usando. Los hallazgos
funcionales por detector quedaron así:

- **`detectar_headers_pagina` (línea 456).** Devuelve `set[int]` de
  índices relativos al bloque. Doble vía: autoridad `headers_archivo`
  con halo asimétrico (`-1, 1, 2`) + barrido auxiliar con
  confirmación por adyacencia. Asimetría del halo solo es correcta si
  el mapa ancla la primera línea del header de 3 líneas; si anclara
  la del medio, hay subdetección silenciosa. No verificado.

- **`detectar_caratula` (línea 499).** Devuelve índice único o `None`.
  Tres estrategias en cascada: (1) primer header con `:` → línea
  anterior; (2) par X-Y con Y header de sumario → X; (3) fallback
  final: última línea no-trivial antes del tope. **Ninguna estrategia
  impone filtro de formato sobre la línea devuelta.** La hipótesis
  preliminar de B049 sobre formatos de carátula no contemplados queda
  refutada por lectura — la causa real es la falta de ancla superior
  (ver B049 refinado en DEUDA).

- **`es_header_sumario_auditoria` (línea 607) + `detectar_sumarios`
  (línea 670).** Detector propio del auditor, más permisivo que
  `linea_es_header_sumario` del parser. La docstring del módulo
  prohíbe reimplementación de heurísticas. Violación documentada en
  M07.

- **`detectar_dictamen` (línea 741).** Reusa `RE_DICT_HDR` por
  importación pero reimplementa el algoritmo de barrido. Segunda
  violación de M07. Parámetro `headers_pagina` recibido y no usado.

- **`detectar_votos_y_disidencias` (línea 791).** Todos los matches
  de `RE_VOTO_HDR`/`RE_DISID_HDR`, partición por inicios sucesivos.
  El último span se cierra en `len(bloque) - 1`. **Implicación
  estructural:** el epílogo queda absorbido dentro del último voto/
  disidencia cuando los hay. Hallazgo nuevo → B051.

- **`detectar_firma_mayoria` (línea 835).** Loop de extensión acepta
  líneas cortas con apellido de `JUECES_CONOCIDOS`. **Vulnerabilidad
  por amplitud del set:** apellidos comunes en el epílogo (letrados,
  conjueces previos, integrantes de tribunales de origen) pueden
  hacer que la firma se extienda sobre la cola del fallo. Hallazgo
  nuevo → B050.

- **`detectar_por_ello_mayoria` (línea 900).** Ancla en
  `apertura_mayoria` para evitar arrastre del previo o del dictamen.
  Toma el primer match. Vulnerable si `apertura_mayoria` está mal
  detectada.

- **`detectar_apertura_mayoria` (línea 931).** Primer match de
  `RE_APERTURA` después del dictamen. Limpio.

- **`detectar_sumario_con_link` (línea 952).** Decisión de
  clasificación de bloque entero, no de span dentro de bloque. No
  cruza con el campo `tipo_entrada` del catálogo (información
  disponible y no usada).

- **`segmentar_bloque` (línea 967).** Orquestador en 9 pasos. La
  decisión clave es el orden: la carátula se detecta en **paso 7**,
  después de dictamen, apertura, votos, por_ello y firma. Para
  entonces el bloque está prácticamente segmentado, pero el rango
  de búsqueda de la carátula sigue empezando en `0`. Esta es la
  raíz mecánica de B049 (ver entrada en DEUDA).

- **`_agregar_catch_all` (línea 1133).** Colector pasivo, no
  clasificador. Marca cubierto a todo span semántico + header_pagina,
  y emite catch_all sobre cualquier hueco contiguo no cubierto. No
  distingue entre residuo del vecino y laguna interna.

- **`_ordenar_y_validar` (línea 1176).** Solo ordena. No valida nada
  pese a nombre y docstring. Las invariantes declaradas en
  `segmentar_bloque` (disjunción, cobertura) no se verifican en
  runtime. Hallazgo nuevo → M08.

- **`_resolver_caso` (línea 1188).** Match por rango contenedor
  (`p_ini <= P <= p_fin`). Tres fuentes para `p_fin`: catálogo
  explícito, `pagina_inicio` del siguiente menos 1, o `pagina_inicio +
  50` para el último caso del tomo. La heurística +50 es ciega al
  contenido pero defensiva. Confirma H026-H1 con matiz.

### Fase B — mapeo producción × auditor

Mapeo de cada producción de GRAMATICA contra qué hace el auditor con
ella. Las cuatro columnas son: ¿detecta como span?, ¿valida orden?,
¿maneja múltiples instancias?, ¿reporta violaciones?

| Producción | ¿Span? | ¿Valida orden? | ¿Múltiples? | ¿Reporta violaciones? |
|---|---|---|---|---|
| `header_pagina` | sí (transversal) | n/a (transversal) | sí | no |
| `caratula` | sí (índice único) | implícito por tope superior | no (una por caso, correcto) | no (silencioso ante fallo: `None`) |
| `sumario` | sí (lista de spans) | implícito (entre carátula y fin_busqueda) | sí | no |
| `dictamen` | sí | implícito | toma solo el primero (no verificado si correcto) | no |
| `apertura_mayoria` | no (índice interno, no span emitido) | implícito (después de dictamen) | toma el primero | no |
| `por_ello_mayoria` | no (índice interno) | implícito (después de apertura, antes de votos) | toma el primero | no |
| `cuerpo_mayoria` | sí | implícito (apertura → firma/votos) | no (uno por caso, correcto) | no |
| `firma` (mayoría) | sí | implícito (después de por_ello, antes de votos) | una | no, pero contaminable por B050 |
| `voto` | sí (lista) | implícito | sí | no |
| `disidencia` | sí (lista) | implícito | sí | no |
| **`epilogo`** | **no (faltante, B047)** | n/a | n/a | n/a |
| `sumario_con_link` | sí (cobertura total del bloque) | n/a | no | no |
| `catch_all` | sí (huecos contiguos) | n/a | sí | no (es residuo, no anomalía clasificada) |

La tabla deja explícito qué está y qué falta. Ninguna producción
tiene validación de orden activa (todas son implícitas por
construcción del orquestador, no chequeadas). Ninguna reporta
violaciones de la gramática. La única producción faltante con
identidad propia es `epilogo`.

### Síntesis de hallazgos H027

1. **H026-H1 confirmada** con matiz: `_resolver_caso` busca por rango
   contenedor con `p_fin` imputado heurísticamente cuando el catálogo
   no lo trae explícito. Heurística defensiva +50 páginas para el
   último caso del tomo. No bug per se.

2. **B049 refinado** — causa raíz reformulada. No es el formato de
   carátula sino la falta de ancla superior. Mecanismo detallado en
   la entrada B049 reescrita de DEUDA. Mejora barata candidata:
   anclar `inicio_busqueda` al último header de página antes del
   dictamen/apertura.

3. **B050 nuevo** — `detectar_firma_mayoria` puede extender el span
   de firma sobre el epílogo cuando una línea de la cola contiene un
   apellido común de `JUECES_CONOCIDOS`. Hipótesis no verificada,
   cuantificable sobre `--random 80`.

4. **B051 nuevo** — `detectar_votos_y_disidencias` cierra el último
   voto/disidencia en `len(bloque) - 1`. El epílogo queda absorbido.
   Explica parcialmente por qué el catch_all final aparece solo en el
   55,7 % de los casos: en casos con votos disidentes, el epílogo
   está escondido dentro del último voto, no en catch_all.

5. **HN3 reformulada como HN3'** — el sesgo opera en el borde
   inferior, no en la firma principal. Existen dos sets paralelos:
   `APELLIDOS_FIRMA_TITULARES` (9 apellidos, solo titulares, usado en
   `detectar_borde_inferior`) y `JUECES_CONOCIDOS` (29 patrones, 14
   conjueces, usado en `detectar_firma_mayoria`). La firma principal
   SÍ cubre conjueces. El sesgo, si existe, opera en la clasificación
   `firma_arrastrada` de `_clasificar_linea_gap`, donde continuaciones
   de firma de conjuez se clasifican como `no_clasificable`,
   perdiendo el diagnóstico fino. Magnitud pendiente de cuantificar.
   No promovido a bug — queda como hipótesis abierta hasta medir.

6. **M07 nuevo** — `es_header_sumario_auditoria` y `detectar_dictamen`
   reimplementan lógica del parser pese a la prohibición declarada
   en la docstring del módulo.

7. **M08 nuevo** — `_ordenar_y_validar` no implementa la validación
   que su nombre y docstring prometen.

8. **Paralelo conceptual borde superior ↔ epílogo.** B045 (catch_all
   extendido del N hacia N+1) y B049 (catch_all inicial del N+1 que
   contiene prosa del N) son **caras duales** del mismo problema
   estructural: ausencia de la producción `epilogo`. Documentado en
   GRAMATICA, subsección "Refinamiento post-Fase A continuación
   (H027)".

9. **Catch_all como colector pasivo.** Confirmado por lectura de
   `_agregar_catch_all`: el catch_all no clasifica, solo recoge.
   Cualquier residuo no clasificado por los detectores semánticos
   cae acá, sin distinción entre arrastre del vecino y laguna
   interna. Esto es coherente con el hallazgo H026 de que el
   catch_all es estructuralmente periférico (88,5 % al inicio, 55,7 %
   al final, 0 % solo en el medio).

### Estado de hipótesis al cierre de H027

- **H026-H1:** confirmada con matiz (rango contenedor + heurística
  +50 para último caso del tomo).
- **H026-H2:** parcialmente refutada por HN3' (ver punto 5). Pendiente
  de medir magnitud sobre el corpus.
- **H025-H1 (B046, mecanismo desconocido):** pendiente. Fase E sigue
  abierta para H028+.
- **HN1 (B048, dos modos de falla):** pendiente. La lectura H027 no
  abordó `detectar_fin_real` (vive en parser.py, no en auditor.py).
  Diagnóstico fino sigue como pendiente del prompt H028.
- **HN2 (B049, mecanismo):** **resuelta**. Causa raíz documentada:
  falta de ancla superior. Mejora candidata identificada.
- **HN3 (set incompleto para conjueces):** reformulada como HN3'.
  Magnitud pendiente.
- **HN4 (nueva, firma de mayoría absorbe epílogo):** promovida a
  B050. Pendiente de cuantificar.

### Commits programados al cierre

Tres commits planificados para H027:

1. `docs(h027): append bitacora H027 - lectura completa auditor + mapeo produccion x auditor (fase B)`
2. `docs(h027): actualizar deuda tecnica - B049 mecanismo refinado, B050/B051 nuevos, M07/M08 nuevos, conteos resumen ejecutivo`
3. `docs(h027): agregar refinamiento post-fase A continuacion a gramatica del fallo`

### Pendientes para H028+

- **Fase C (dirección N+1 → N):** identificar qué le falta a
  `_clasificar_linea_gap` para tener simetría con el detector de
  carátula. Decidir si la dirección simétrica se construye con un
  detector independiente o emerge del detector de epílogo extendiendo
  hacia adelante.
- **Fase D2 (diagnóstico fino B049):** sobre los 8 casos testigo
  (`331_p1519`, `348_p1352`, `348_p755`, `348_p1511`, `340_p1554`,
  `344_p2669`, `348_p1277`, `343_p988`), verificar que el mecanismo
  documentado en B049 refinado se cumple. Confirmar que la carátula
  real está pegada o muy cerca del último header de página antes del
  dictamen/apertura. Si se confirma, implementar la mejora del ancla.
- **Fase E (verificación B046):** comparar `catalogo.csv` /
  `fallos_localizados.csv` (5862) vs `csjn_casos.csv` (5819) con
  `csv.DictReader`. Identificar los 43 `caso_id_canonico` faltantes
  e inspección caso a caso.
- **Fase F (síntesis de reutilización):** estimar qué fracción del
  código del auditor se promueve a parser de Forma 1, cuántas
  funciones nuevas, cuánto refactor vs código nuevo.
- **Fase G (diseño detector de epílogo + borde superior):** boceto
  de `detectar_epilogo(bloque, headers_pagina, firma_fin)`. Interfaz
  análoga a `detectar_borde_inferior`. Integración con extracción de
  `tribunal_origen` del parser.
- **Cuantificación de B050 y B051 sobre `--random 80`.**
- **Cuantificación de HN3' sobre el corpus** (apariciones de
  continuaciones de firma de conjuez en gaps de borde inferior).
- **Decisión sobre M07** — promover lógica al parser, documentar
  forks deliberados, o refactor con split de funciones.
- **Decisión sobre M08** — implementar validación o renombrar.
- **Diagnóstico fino de B048** (causa raíz de los dos modos, sigue
  pendiente desde H026).

Sesión H027 queda **cerrada**. H028 retoma con las prioridades de
arriba; el orden lo decide la próxima sesión.

### Nota de cierre — estado de fases del proyecto

Para evitar ambigüedad sobre qué fase está abierta y qué fase cerrada
(la letra "B" se usó con dos sentidos distintos entre H026 y H027), el
estado al cierre de H027 es:

- **Fase A** (lectura del auditor) — cerrada en H027.
- **Fase B** (mapeo producción × auditor) — cerrada en H027 como tabla
  embebida en esta entrada.
- **Fase C** (dirección N+1 → N) — abierta, sin sesión asignada.
- **Fase D** (análisis empírico del catch_all sobre `--random 80`) —
  cerrada en H026.
- **Fase D2** (diagnóstico fino B049 sobre 8 testigos) — abierta,
  prioritaria para H028.
- **Fase E** (verificación B046 con `csv.DictReader`) — abierta,
  prioritaria para H028.
- **Fase F** (síntesis de reutilización auditor → parser de Forma 1) —
  abierta, sin sesión asignada.
- **Fase G** (diseño detector de epílogo + borde superior) — abierta,
  sin sesión asignada.
- **Cuantificaciones nuevas** (B050-quant, B051-quant, HN3'-quant) —
  abiertas, candidatas para H028.

H028 salta a D2 + E + cuantificaciones porque las Fases C, F y G son
discusión arquitectónica que se enmarca mejor **después** de tener D2
resuelta: la mejora del ancla del detector de carátula que podría
implementarse tras D2 es insumo para Fase G (diseño del detector de
epílogo + borde superior). El orden razonado es: cuantificar y
verificar primero, diseñar después.

---

# H028 — Fase D2: diagnóstico B049 sobre 8 testigos + fix Var-A (16/5/2026)

## Objetivo

Sesión de ejecución sobre el corpus. Continuación de H027 (lectura del
auditor). Foco principal: Fase D2 (verificación empírica de B049 sobre
los 8 testigos) + implementación del fix Var-A de B049.

## Fase D2 — Diagnóstico B049 sobre 8 testigos

Corrida de `auditar_fallo.py` para los 8 casos testigos de B049.
Hallazgo estructural clave: el auditor con `--pagina N` audita el caso
que *termina* en página N (`fin_extendido_pag_compartida`), no el que
empieza. Los IDs del parser y del auditor siempre difieren en un caso.

**Tabla de resultados (8/8):**

| Consultado | Auditado | Carátula detectada | Veredicto |
|---|---|---|---|
| 331_p1519 | 331_p1516 | `ARGENTINA` | ✗ Var-A |
| 340_p1554 | 340_p1551 | `Carlos Maqueda — Horacio Rosatti — ...` | ✗ Var-B |
| 343_p988 | 343_p987 | `LESTELLE, MANUEL ÁNGEL c/ ANSES...` | ✓ OK |
| 344_p2669 | 344_p2665 | `Pablo Gustavo` | ✗ Var-A |
| 348_p755 | 348_p751 | `Familia, Niñez y Adolescencia n° 4` | ✗ Var-A |
| 348_p1352 | 348_p1351 | N/A (sumario_con_link) | — |
| 348_p1277 | 348_p1269 | `S., N. s/ incidente de competencia` | ✓ OK |
| 348_p1511 | 348_p1505 | `extraordinario` | ✗ Var-A |

5/7 evaluables con carátula espuria (71 %). Var-A dominante (4 casos):
carátula partida en dos líneas por salto de página, detector toma solo
la segunda mitad. Var-B (1 caso, 340_p1551): detector toma la firma
del caso anterior al auditado.

Cruce con `csjn_casos.csv`: los 8 casos tienen `case_name_indice`
correcto. B049 es bug del auditor únicamente. Corpus productivo sano.

Lectura de código (`detectar_caratula`, línea 499): Estrategia 1
retrocede una sola línea desde el primer header con `:`; Estrategia 2
devuelve la línea previa al primer header de sumario. Sin verificación
de formato ni concatenación. Señal disponible no usada: candidata
en Var-A no tiene `c/`, `s/` ni `|`.

## Fix B049 Var-A

Fix implementado en `detectar_caratula`, Estrategia 1 y Estrategia 2:
si la candidata no tiene `c/`, `s/`, `|` y no termina en punto, busca
la línea anterior y concatena con manejo de silabación.

Guardia sobre la línea anterior (para evitar concatenar fragmentos de
epílogo): no debe ser mes calendario solo (`ENERO`...`DICIEMBRE`), no
debe empezar con `V.` o `v.`, no debe terminar en punto ni empezar en
minúscula.

Proceso de validación:
- Primera iteración (sin guardia): 21 cambios, 4 regresiones parciales
  donde el fix concatenaba fragmentos de epílogo con carátulas espurias.
- Segunda iteración (con guardia v3 + excepción meses): 7 mejoras,
  0 regresiones, 0 pérdidas de detección (seed 15052026, n=80).
- 4 testigos Var-A re-corridos: carátulas completas post-fix.

Var-B pendiente: 340_p1551 requiere análisis separado.

## Fases no abordadas

Fase E (B046, 43 casos faltantes), B050-quant, B051-quant,
HN3'-quant — pasan a H029.

## Commits

- `fix(auditor): B049 Var-A — concatenar carátula partida en dos líneas`

## Estado de fases

- **Fase D2** — cerrada.
- **Fase E** — abierta, prioritaria H029.
- **B050-quant, B051-quant, HN3'-quant** — abiertas, H029.
- **Fases C, F, G** — abiertas, sin sesión asignada.

---
# H029 — Fase E: diagnóstico B046 (43 faltantes) + hallazgo estructural título como ancla (16/5/2026)

## Objetivo
Continuación de H028. Foco principal: Fase E (verificación B046 —
43 casos en `fallos_localizados` ausentes de `csjn_casos`).
Cuantificaciones B050, B051, HN3' postergadas a H030.

## Fase E — Diagnóstico B046

Comparación de sets `caso_id_canonico` entre `csjn_casos.csv`
(5.819 filas) y `fallos_localizados.csv` (5.862 filas) con
`csv.DictReader`. Diferencia: 43 casos presentes en localizados
pero ausentes en casos.

**Distribución por tomo:**

| Tomo | en casos | en localizados | faltantes |
|------|----------|----------------|-----------|
| 331  | 365      | 376            | 11        |
| 332  | 319      | 330            | 11        |
| 333  | 241      | 252            | 11        |
| 334  | 189      | 199            | 10        |
| **Total** | | | **43** |

Tomos 335 y 336 ausentes del parser por diseño (PDFs ilegibles,
firmas holográficas que rompen el OCR). No es bug.

**Causa raíz confirmada:** los 43 tienen `status: pagina_no_en_mapa`
y `archivo: ''`, `linea_inicio: ''` vacíos en `fallos_localizados`.
El localizador los detecta en el índice editorial pero no puede
anclarlos en el cuerpo del `.md` porque el marcador numérico de
página no aparece como línea standalone — está consumido por una
hoja complementaria (separador de sección mensual) o es el inicio
del volumen (página 7 de 331, antes del primer marcador).

Ejemplo verificado: `331_p379` corresponde a "Marzo" — la hoja
complementaria ocupa la página 379, el cuerpo arranca en 380.
El marcador `379` no existe en el `.md`; el parser no puede anclar.

**Análisis de saltos en `mapa_paginas.csv`:** script sobre
`mapa_paginas.csv` detectó 86 saltos de página en todo el corpus
(tomos 329–348). El patrón es universal, no exclusivo de 331–334.
Los 43 faltantes coinciden con saltos de esos tomos. Salto negativo
aislado en `LibroVol338.2.md` (de=1591 a=338, salto=-1253):
causa probable OCR defectuoso en una página, no sistemático.

**Magnitud:** 43/5.862 = 0,73%. Pérdida aceptable, no requiere
fix urgente.

## Hallazgo estructural — título del caso como ancla

Durante el diagnóstico se identificó que cada fallo tiene un título
limpio antes de los sumarios, dictamen y cuerpo, coincidente con
el índice editorial. Este título es una señal más robusta que
"Vistos los autos" para delimitar el inicio de cada caso.

Ejemplo verificado (331_p7):

```
BOSTON Cía. de SEGUROS S.A. c/ FEDERAL EXPRESS
[sumarios]
[dictamen]
[cuerpo]
```

`detectar_caratula` del auditor ya implementa esta lógica con
guardias (no mes solo, no empieza con V., no termina en punto,
no empieza en minúscula) y la detectó correctamente en las pruebas.
Es el candidato natural a portar al parser como ancla de inicio
de caso — reemplazando o complementando la búsqueda por "Vistos
los autos". Esto resolvería también los 43 faltantes de B046.

Requiere muestras representativas de tomos viejos y nuevos antes
de implementar (variaciones conocidas: `V.`, mayúsculas, sin
separador `c/`/`s/`/`|`). Fase asignada a H030.

## Fases no abordadas
B049 Var-B, B050-quant, B051-quant, HN3'-quant — pasan a H030.

## Commits
- Ninguno. Sesión de diagnóstico puro, sin cambios al pipeline.

## Estado de fases
- **Fase E** — cerrada. Causa raíz documentada, fix diferido.
- **Fase F (título como ancla)** — abierta, prioritaria H030.
- **B049 Var-B** — abierta, H030.
- **B050-quant, B051-quant, HN3'-quant** — abiertas, H030.


## H030 — Fase F: refinador linea_inicio por título (B009)

**Fecha:** 2026-05-16
**Sesión:** H030 (continuación de H029)

### Objetivo

Portar `detectar_caratula` del auditor al parser como ancla de inicio
de caso (Fase F). Resolver los 43 faltantes de B009 y reducir el residuo
pre-título que contamina los bloques de todos los casos.

### Diagnóstico previo a la implementación

**Diagnóstico de los 43 faltantes (B009):**
- Todos tienen `status=pagina_no_en_mapa`, `archivo=''`,
  `linea_inicio=''` vacíos en `fallos_localizados.csv`.
- Distribuidos en tomos 331, 332, 333, 334 (no solo 331 como se
  creía). Confirmado con script diagnóstico.
- `primer_token_de_caratula` matchea en el `.md` para 43/43 —
  el título existe en el corpus, el localizador simplemente no
  pudo anclarlos por página.
- 6 tokens ambiguos (`Estado`, `Buenos`, `autos`, `E`, `Fiscal`,
  `Banco`) — ambigüedad resuelta por ventana de vecinos.

**Diagnóstico del residuo pre-título (sistémico):**
- Script sobre muestra de 200 casos ok: 64.5% tienen residuo
  pre-título (promedio 6.2 líneas). El localizador ancla en el
  header de página compartida, que incluye epílogo del fallo anterior.
- Script de cobertura de título en bloque: 89% de casos tienen el
  token del título detectable en las primeras 60 líneas del bloque.
- 11% sin título en bloque: fallos cortos sin sumarios editoriales
  donde la carátula quedó en el bloque anterior.

**Hallazgo arquitectónico:**
El auditor segmenta mejor que el parser productivo. `segmentar_bloque()`
del auditor (carátula, sumarios, dictamen, cuerpo, firma, epílogo)
produce resultados más confiables que la lógica paralela del parser.
A largo plazo el parser debería consumir `segmentar_bloque()` en lugar
de reimplementar las heurísticas. Anotado como bug nuevo.

**Hallazgo: epílogo como span propio:**
El catch_all post-firma contiene información analíticamente valiosa
(representación letrada, tribunal de origen, tribunales intervinientes).
Su delimitación es precisa: empieza después de la firma con
`Recurso ... interpuesto por` o `Traslado contestado por` o
`Tribunal de origen`. Anotado como bug nuevo.

### Implementación

**Patch aplicado** (`27bf3d5`): cuatro cambios en `parser.py`:

- **C1** — `refinar_inicio_por_titulo()`: función nueva que busca el
  token del título en las primeras 50 líneas del bloque y recorta
  el residuo pre-título. Señal secundaria: `RE_VISTOS_LOS_AUTOS`.
  Fallback: `linea_inicio` del catálogo sin cambios.
- **C2** — Llamada al refinador en `procesar_archivo` post construcción
  de bloque, antes de `detectar_apertura_en_bloque`.
- **C3** — `ancla_inicio` propagada a `status_localizacion`:
  `ok` (título), `ok_ancla_vistos`, `ok_ancla_catalogo`.
- **C4** — `cargar_localizados`: no descarta `pagina_no_en_mapa`,
  infiere `archivo` y `linea_inicio` desde vecinos del mismo tomo.

**Resultado de corrida completa del parser:**
- Cobertura: 5819 → 5862 casos (+43 faltantes recuperados)
- Votos: 21876 → 22489 (+613)
- Status breakdown: `ok=4938`, `ok_ancla_catalogo=387`,
  `ok_sin_marcador_apertura=330`, `ok_ancla_vistos=8`,
  `pagina_no_en_mapa=14` (parcialmente recuperados), otros.

**Resultado de auditoría (seed=42, n=80):**
- Baseline: 2201 / 36208 líneas residuo (6.08%)
- Postfix:  1055 / 29711 líneas residuo (3.55%)
- Mejora: -52% en residuo absoluto, -2.53pp en porcentaje

### Bugs identificados durante la sesión

**Bug en `refinar_inicio_por_titulo` (B_nuevo — pendiente ID):**
El refinador busca el token del título con `\btoken\b` en las
primeras 50 líneas del bloque. Puede matchear en el epílogo del
fallo anterior si el apellido aparece en la representación letrada
o en la carátula del caso siguiente que el fallo anterior menciona
como metadata de cierre. Caso testigo: `346_p885` (Wang) — el token
`Wang` matcheó en la línea de carátula del caso Wang que el fallo
anterior incluye en su epílogo, dejando la primera línea de la
carátula en catch_all.

Rediseño acordado: búsqueda probabilista con tokens distribuidos
del `nombres_indice` (inicio + medio + final). Cada token que matchea
en una ventana de 2-3 líneas suma peso; umbral de coincidencia para
declarar match. Robusto a OCR, saltos de página, mayúsculas.
Fix pendiente para H031.

**Bug en `detectar_fin_real` (B_existente — ver B021):**
Caso `342_p148`: `detectar_fin_real` cortó el bloque en línea 5949
usando `caratula_siguiente` como pista, dejando el bloque con 11
líneas (casi todo residuo). El fallo completo quedó sin cuerpo ni
firma. Acumulación con `detectar_caratula` que tomó una línea de
firma como carátula. Ambos bugs preexistentes, no introducidos por
Fase F.

**Bug arquitectónico: parser reimplementa lógica del auditor (B_nuevo):**
`segmentar_bloque()` del auditor produce segmentación más confiable
que la lógica del parser productivo. El parser debería consumir
`segmentar_bloque()` como fuente canónica en lugar de reimplementar
heurísticas paralelas. Impacto: todos los campos analíticos del CSV
(`wc_mayoria`, `wc_votos`, `firma_raw`, etc.) son menos confiables
que lo que el auditor produciría.

**Hallazgo: epílogo como span propio (B_nuevo):**
El catch_all post-firma contiene representación letrada y tribunal
de origen — información analítica valiosa hoy no tipificada.
Señal de inicio: `Recurso .* interpuesto por` | `Traslado contestado
por` | `Nombre de` | `Tribunal de origen`. Señal de fin: carátula
del caso siguiente o fin de bloque. Documentar y priorizar.

### Pendientes que pasan a H031

- Rediseño de `refinar_inicio_por_titulo` con tokens distribuidos
- Verificación de que los 43 faltantes recuperados tienen datos
  correctos en el CSV (auditoría caso por caso de los 43)
- Diff formal baseline vs postfix sobre mismos 80 casos
  (bloqueado por cambio de universo en C4)
- B049 Var-B, B050-quant, B051-quant, HN3'-quant — sin abordar
- Limpieza de archivos temporales: `test_fase_f/`, `diag*.py`,
  `ver_zona.py`, `aplicar_patch_fase_f.py` → mover a lugar canónico

### Commits

- `27bf3d5` — feat(parser): Fase F — refinador linea_inicio por
  titulo (B009)
- CSV regenerados: pendiente commit (en stash)

### Estado de fases

- **Fase F** — aplicada parcialmente. Fix funciona para los 43
  faltantes y reduce residuo global. Refinador necesita rediseño
  para evitar falsos positivos. H031.
- **B049 Var-B, B050-quant, B051-quant, HN3'-quant** — sin abordar,
  pasan a H031.


## H030 — Fase F: refinador linea_inicio por título (B009)

**Fecha:** 2026-05-16
**Sesión:** H030 (continuación de H029)

### Objetivo

Portar `detectar_caratula` del auditor al parser como ancla de inicio
de caso (Fase F). Resolver los 43 faltantes de B009 y reducir el residuo
pre-título que contamina los bloques de todos los casos.

### Diagnóstico previo a la implementación

**Diagnóstico de los 43 faltantes (B009):**
- Todos tienen `status=pagina_no_en_mapa`, `archivo=''`,
  `linea_inicio=''` vacíos en `fallos_localizados.csv`.
- Distribuidos en tomos 331, 332, 333, 334 (no solo 331 como se
  creía). Confirmado con script diagnóstico.
- `primer_token_de_caratula` matchea en el `.md` para 43/43 —
  el título existe en el corpus, el localizador simplemente no
  pudo anclarlos por página.
- 6 tokens ambiguos (`Estado`, `Buenos`, `autos`, `E`, `Fiscal`,
  `Banco`) — ambigüedad resuelta por ventana de vecinos.

**Diagnóstico del residuo pre-título (sistémico):**
- Script sobre muestra de 200 casos ok: 64.5% tienen residuo
  pre-título (promedio 6.2 líneas). El localizador ancla en el
  header de página compartida, que incluye epílogo del fallo anterior.
- Script de cobertura de título en bloque: 89% de casos tienen el
  token del título detectable en las primeras 60 líneas del bloque.
- 11% sin título en bloque: fallos cortos sin sumarios editoriales
  donde la carátula quedó en el bloque anterior.

**Hallazgo arquitectónico:**
El auditor segmenta mejor que el parser productivo. `segmentar_bloque()`
del auditor (carátula, sumarios, dictamen, cuerpo, firma, epílogo)
produce resultados más confiables que la lógica paralela del parser.
A largo plazo el parser debería consumir `segmentar_bloque()` en lugar
de reimplementar las heurísticas. Anotado como bug nuevo.

**Hallazgo: epílogo como span propio:**
El catch_all post-firma contiene información analíticamente valiosa
(representación letrada, tribunal de origen, tribunales intervinientes).
Su delimitación es precisa: empieza después de la firma con
`Recurso ... interpuesto por` o `Traslado contestado por` o
`Tribunal de origen`. Anotado como bug nuevo.

### Implementación

**Patch aplicado** (`27bf3d5`): cuatro cambios en `parser.py`:

- **C1** — `refinar_inicio_por_titulo()`: función nueva que busca el
  token del título en las primeras 50 líneas del bloque y recorta
  el residuo pre-título. Señal secundaria: `RE_VISTOS_LOS_AUTOS`.
  Fallback: `linea_inicio` del catálogo sin cambios.
- **C2** — Llamada al refinador en `procesar_archivo` post construcción
  de bloque, antes de `detectar_apertura_en_bloque`.
- **C3** — `ancla_inicio` propagada a `status_localizacion`:
  `ok` (título), `ok_ancla_vistos`, `ok_ancla_catalogo`.
- **C4** — `cargar_localizados`: no descarta `pagina_no_en_mapa`,
  infiere `archivo` y `linea_inicio` desde vecinos del mismo tomo.

**Resultado de corrida completa del parser:**
- Cobertura: 5819 → 5862 casos (+43 faltantes recuperados)
- Votos: 21876 → 22489 (+613)
- Status breakdown: `ok=4938`, `ok_ancla_catalogo=387`,
  `ok_sin_marcador_apertura=330`, `ok_ancla_vistos=8`,
  `pagina_no_en_mapa=14` (parcialmente recuperados), otros.

**Resultado de auditoría (seed=42, n=80):**
- Baseline: 2201 / 36208 líneas residuo (6.08%)
- Postfix:  1055 / 29711 líneas residuo (3.55%)
- Mejora: -52% en residuo absoluto, -2.53pp en porcentaje

### Bugs identificados durante la sesión

**Bug en `refinar_inicio_por_titulo` (B_nuevo — pendiente ID):**
El refinador busca el token del título con `\btoken\b` en las
primeras 50 líneas del bloque. Puede matchear en el epílogo del
fallo anterior si el apellido aparece en la representación letrada
o en la carátula del caso siguiente que el fallo anterior menciona
como metadata de cierre. Caso testigo: `346_p885` (Wang) — el token
`Wang` matcheó en la línea de carátula del caso Wang que el fallo
anterior incluye en su epílogo, dejando la primera línea de la
carátula en catch_all.

Rediseño acordado: búsqueda probabilista con tokens distribuidos
del `nombres_indice` (inicio + medio + final). Cada token que matchea
en una ventana de 2-3 líneas suma peso; umbral de coincidencia para
declarar match. Robusto a OCR, saltos de página, mayúsculas.
Fix pendiente para H031.

**Bug en `detectar_fin_real` (B_existente — ver B021):**
Caso `342_p148`: `detectar_fin_real` cortó el bloque en línea 5949
usando `caratula_siguiente` como pista, dejando el bloque con 11
líneas (casi todo residuo). El fallo completo quedó sin cuerpo ni
firma. Acumulación con `detectar_caratula` que tomó una línea de
firma como carátula. Ambos bugs preexistentes, no introducidos por
Fase F.

**Bug arquitectónico: parser reimplementa lógica del auditor (B_nuevo):**
`segmentar_bloque()` del auditor produce segmentación más confiable
que la lógica del parser productivo. El parser debería consumir
`segmentar_bloque()` como fuente canónica en lugar de reimplementar
heurísticas paralelas. Impacto: todos los campos analíticos del CSV
(`wc_mayoria`, `wc_votos`, `firma_raw`, etc.) son menos confiables
que lo que el auditor produciría.

**Hallazgo: epílogo como span propio (B_nuevo):**
El catch_all post-firma contiene representación letrada y tribunal
de origen — información analítica valiosa hoy no tipificada.
Señal de inicio: `Recurso .* interpuesto por` | `Traslado contestado
por` | `Nombre de` | `Tribunal de origen`. Señal de fin: carátula
del caso siguiente o fin de bloque. Documentar y priorizar.

### Pendientes que pasan a H031

- Rediseño de `refinar_inicio_por_titulo` con tokens distribuidos
- Verificación de que los 43 faltantes recuperados tienen datos
  correctos en el CSV (auditoría caso por caso de los 43)
- Diff formal baseline vs postfix sobre mismos 80 casos
  (bloqueado por cambio de universo en C4)
- B049 Var-B, B050-quant, B051-quant, HN3'-quant — sin abordar
- Limpieza de archivos temporales: `test_fase_f/`, `diag*.py`,
  `ver_zona.py`, `aplicar_patch_fase_f.py` → mover a lugar canónico

### Commits

- `27bf3d5` — feat(parser): Fase F — refinador linea_inicio por
  titulo (B009)
- CSV regenerados: pendiente commit (en stash)

### Estado de fases

- **Fase F** — aplicada parcialmente. Fix funciona para los 43
  faltantes y reduce residuo global. Refinador necesita rediseño
  para evitar falsos positivos. H031.
- **B049 Var-B, B050-quant, B051-quant, HN3'-quant** — sin abordar,
  pasan a H031.

## H031 — Auditoría B052: carátula partida y catch_all inicial

**Fecha:** 2026-05-17
**Sesión:** H031 (continuación de H030)

### Objetivo

Investigar B052 (crosscheck título vs índice) y B054 (separar
catch_all anterior del posterior). Sesión de diagnóstico puro —
ningún fix commiteado.

### Hallazgos

**B052 — no es un problema crítico:**
La carátula correcta ya está en `nombres_indice` / `case_name_indice`
por definición del índice editorial. El parser no depende de
`detectar_caratula()` del auditor para ese dato. El catch_all inicial
es basura por definición (epílogo del anterior, firma arrastrada) y
no tiene valor analítico. El sumario es la señal confiable. B052 en
el auditor es cosmético — afecta el rendering del MD pero no el CSV.

**Bug en `_resolver_caso()` del auditor (B_nuevo):**
Introducido por Fase F (C4). Cuando dos casos comparten página
límite (`pagina_fin` del anterior = `pagina_inicio` del siguiente),
el loop devuelve el primero en orden de iteración. Caso testigo:
`--pagina 885` resuelve Schenone en vez de Wang. Fix trivial: pase
previo de match exacto por `pagina_inicio` antes del loop de rangos.
Solo afecta al auditor — el parser usa `linea_inicio` directamente.

**B054 — separación posicional trivial:**
`linea_inicio` y `linea_fin_real` ya están disponibles. Todo lo que
está antes de la carátula dentro del bloque es catch_

---
**Fecha:** 2026-05-17
**Sesión:** H032
### Objetivo
Desarrollar `visor_auditoria.py`: herramienta de visualización compacta
de los outputs de `auditar_fallo.py`. Mejoras menores a `auditar_fallo.py`.
### Trabajo realizado
- Diseño e implementación de `scripts/visor/visor_auditoria.py` desde cero.
  Agrupa spans por tipo, silencia `header_pagina` y `catch_all_inicio` por
  default, limpia headers de página embebidos dentro del contenido de spans.
  Opciones: `--solo`, `--excluir`, `--incluir`, `--tomo`, `--pagina`,
  `--con-alertas`, `--formato` (md/txt/csv), `--preview`, `--resumen`,
  `--stats`, `--stdout`, `--output`.
- Output default en `output/visor/<nombre>_vista.md` (crea directorio).
- `auditar_fallo.py`: agrega `__version__ = "1.0.0"`, campo `Versión` y
  `Seed` en encabezado del MD generado.
- Reorganización de `output/auditoria/auditar_fallo/`: outputs viejos
  movidos a `archivo/auditoria/auditar_fallo/` (de versión de script
  desconocida). `.gitignore` actualizado.
- Validación con diff pre/post versión: solo difieren `Generado` y
  `Versión: 1.0.0` — sin regresiones.
- Pruebas con múltiples auditorías reales (random + tomo/página).
### Decisiones
- `visor_auditoria.py` vive en `scripts/visor/` (no es pipeline),
  con espejo en `output/visor/`.
- `catch_all_inicio` se silencia en el visor por posición (termina antes
  del primer span semántico), sin modificar `auditar_fallo.py`.
- Clasificación robusta de `catch_all_inicio`/`catch_all_fin` en
  `auditar_fallo.py` postergada — requiere análisis más profundo del
  parser (ver DEUDA_TECNICA VIS001, VIS002).
### Pendiente
- Soporte de rango en `--pagina` (ej: `344-354`) — ver VIS003.
- Clasificación robusta catch_all inicio/fin en auditar_fallo — ver VIS001.
- Fix firma multilinea con paréntesis en parser — ver B055.
- Fix apertura mayoría perdida cuando hay residuo antes de "FALLO DE LA CORTE SUPREMA" — ver B056.
- Fix dictamen que consume "FALLO DE LA CORTE SUPREMA" — ver B057.
- Fix pérdida de `°` en numeración de considerandos (encoding) — ver B058, caso testigo 329_p3546.
- Ningún fix al parser commiteado en esta sesión.

---
**Fecha:** 2026-05-17
**Sesión:** H033
### Objetivo
Auditar casos testigo de B055 (firma multilinea) en el MD crudo y el CSV
productivo para confirmar causa raíz y diseñar fix.
### Trabajo realizado
- Revisión de los tres casos testigo documentados en B055:
  - `347_p128` (Perret): causa raíz es B013, no B055. El parser captura
    `"De conformidad con la regulación prevista..."` (texto argumental del
    considerando) como dispositivo `de_conformidad`. `por_ello_idx` queda
    en mitad del cuerpo y `collect_firma_lines` no llega a la firma real.
    `firma_raw` vacío, `n_jueces=0`. Adicionalmente: `Rocio Alcala` (conjuez)
    no está en `JUECES_CONOCIDOS`.
  - `348_p1540` (Guardia): parser correcto. Firma multilinea reconstruida
    bien por join. `n_jueces=3`, calificadores presentes.
  - `333_p1254`: parser correcto. Fallo auditado era el equivocado (zona
    17229, no 18719). El fallo real no tiene calificadores — unanime limpio.
- Cuantificación de `sin_firma` en CSV: 872 casos (15% del corpus).
  - 479 con `por_ello_text` no vacío → probable B013.
  - 393 sin `por_ello_text` → causa distinta (B057 u otros).
- Cuantificación de B055 real: 345 casos con `firma_raw` no vacío pero
  sin punto final. Muestra confirma nombres truncados (`JUAN`, `CARLOS`,
  `E. RAÚL`). Este es el universo real de B055.
- Hallazgo: el auditor y el parser detectan universos consistentes de
  `sin_firma` (~15%). El auditor es más robusto para firmas partidas
  (usa `APELLIDOS_FIRMA_TITULARES`), el parser no.
### Decisiones
- B055 redocumentado en DEUDA_TECNICA: casos testigo originales
  corregidos, cuantificación actualizada a 345 casos.
- No se commiteó ningún fix. Sesión de auditoría pura (M04).
### Pendiente
- Fix B055: diseñar condición de continuación en `collect_firma_lines`
  para firmas sin punto final.
- Fix B013: sigue pendiente (479 casos sin firma por dispositivo prematuro).
- Agregar `Rocio Alcala` y otros conjueces recientes a `JUECES_CONOCIDOS`
  si se confirman más apariciones.
- Auditar los 393 `sin_firma` sin `por_ello_text` para identificar causa.

---
**Fecha:** 2026-05-17
**Sesión:** H034
### Objetivo
Fix B055 (firma truncada, 345 casos). Auditar mecanismo de corte,
diseñar fix en `collect_firma_lines`, validar con pipeline paralelo.
### Trabajo realizado
- Diagnóstico con `diag_b055_muestra.py` (10 casos, sin seed):
  confirmado que la firma está partida en 2-3 líneas físicas. En la
  muestra el mecanismo de corte parecía ser línea vacía intercalada.
- Comparación con `detectar_firma_mayoria` del auditor: el auditor
  tolera una línea vacía y además usa `APELLIDOS_FIRMA_TITULARES`
  como criterio de continuación — más permisivo que `JUECES_CONOCIDOS`.
- Fix v1 (`parser_b055.py`): tolerar una línea vacía, cortar en dos
  consecutivas. Sin efecto — 0 casos cambiados. Los mixtos del
  comparador mostraban firma_raw acumulando texto editorial del caso
  siguiente (regresión).
- Fix v2 (`parser_b055_v2.py`): lookahead sobre línea siguiente a la
  vacía — continuar solo si contiene apellido de `APELLIDOS_FIRMA`
  (set nuevo de ~35 apellidos de titulares y conjueces). Sin efecto
  en el pipeline — 0 diferencias en votos y casos respecto al
  productivo.
- Diagnóstico profundo: el fix funciona en test directo (`341_p971`
  con `por_ello_idx` correcto → firma completa). El pipeline no lo
  activa porque `por_ello_idx` es prematuro — toma el dispositivo
  del residuo del caso anterior o del dictamen antes de llegar a la
  firma real.
- Análisis de muestra de 10 casos B055 con `por_ello_text` no vacío:
  3 sin dispositivo en bloque (B013 variante), 4 OK en test directo
  (CSV desactualizado), 3 truncados — los tres son B013 disfrazado.
- Lectura completa de `procesar_archivo` en `parser.py`: confirmado
  que el loop toma el primer `detectar_apertura_dispositivo` desde
  el inicio del bloque sin ancla previa. El dictamen se excluye
  correctamente por `en_dictamen`, pero el residuo del caso anterior
  no se excluye si `refinar_inicio_por_titulo` falla.
- Comparación arquitectónica parser vs auditor: el auditor usa
  `RE_APERTURA` ("FALLO DE LA CORTE SUPREMA") como ancla antes de
  buscar el dispositivo. El parser no usa esa ancla para `por_ello_idx`.
### Hallazgos principales
- **B055 y B013 están entrelazados:** el universo de 345 casos B055
  es en su mayoría B013 subyacente — `por_ello_idx` prematuro hace
  que `collect_firma_lines` arranque lejos de la firma real. B055
  puro (firma partida sin dispositivo prematuro) es un universo
  mucho menor, posiblemente cercano a cero casos reproducibles hoy.
- **La diferencia arquitectónica clave:** el auditor ancla la búsqueda
  del dispositivo en `apertura_mayoria` ("FALLO DE LA CORTE SUPREMA").
  El parser no. Adoptar esa ancla en el parser resolvería B013 en la
  mayoría de los casos y exppondría el universo real de B055 puro.
- **Fix correcto de B013:** antes de buscar `por_ello_idx`, detectar
  `RE_APERTURA` en el bloque y restringir la búsqueda del dispositivo
  a `[apertura_rel, votos_inicio]`. Cambio de superficie acotada,
  impacto potencialmente alto.
### Scripts generados (en scripts/diagnostico/)
- `diag_b055_muestra.py` — muestra líneas crudas de casos B055.
- `parser_b055.py` — fix v1 (línea vacía, sin efecto).
- `parser_b055_v2.py` — fix v2 (lookahead apellidos, sin efecto).
- `comparar_b055.py` — diff caso a caso entre dos CSVs.
### Artefactos en output/diagnostico/B055/
- `csjn_casos_b055.csv` — output de parser_b055_v2.py (idéntico al productivo).
- `csjn_casos_b055_votos.csv` — idem votos.
### Decisiones
- No se commitea ningún fix. Pipeline paralelo descartado como solución.
- B055 se reclasifica: bug dependiente de B013. Fix de B055 puro
  postergado hasta resolver B013.
- B013 se eleva a prioridad máxima con dirección de fix documentada.
### Pendiente → H035
- Fix B013: usar `RE_APERTURA` como ancla para `por_ello_idx` en
  `procesar_archivo`. Sesión dedicada, ciclo completo de validación.
- Verificar universo B055 puro post-fix B013.
- Limpiar `output/diagnostico/B055/` antes de H035.

---
**Fecha:** 2026-05-18
**Sesión:** H035
### Objetivo
Fix B013 (dispositivo prematuro, ~479 casos sin firma). Búsqueda anclada
de dispositivo emulando el approach del auditor.
### Trabajo realizado
- Cuantificación del universo B013: 479 casos sin firma con dispositivo.
  461 con apertura_tipo (fix los cubre), 18 sin marcador.
- Clasificación por texto del por_ello_text: 66 dictamen, 370
  argumentativo ("otro"), 46 dispositivo aparentemente real.
- Diagnóstico con `diag_b013_muestra.py` (12 casos): 6/12 prematuros
  confirmados (por_ello_idx < apertura_rel), 2 falsos positivos
  post-apertura, 2 sin marcador, 1 sin dispositivo, 1 anomalía.
- Cuantificación completa con `diag_b013_cuantificar.py`: 302
  prematuros (63%), 146 post-apertura (30%), 17 sin marcador, 8
  sin localización, 6 sin dispositivo.
- Pipeline paralelo `parser_b013.py` v1: cascada apertura_rel →
  dictamen_end+1 → 0, techo en inicio_votos_indiv. Resultado:
  227 mejoras, 139 regresiones. Causa: techo en inicio_votos_indiv
  tomaba votos de residuo del fallo anterior.
- Pipeline paralelo v2: techo solo cuando votos post-apertura.
  Resultado: 268 mejoras, 95 regresiones aparentes.
- Auditoría manual de 7 casos: las 57 regresion_perdio_firma son
  fallos cortados por detectar_fin_real o datos del caso equivocado.
  Las 27 regresion_menos_jueces son correcciones (firma del caso
  correcto con menos firmantes). 0 regresiones reales confirmadas.
- Validación estadística: n_jueces=1 baja de 114 a 21 (-82%);
  n_jueces=5-7 suben +162 casos; outcome "otro" baja 152.
- Commit del fix en parser.py.
### Hallazgos principales
- **B013 ⊂ problema de arquitectura:** el parser procesaba el bloque
  de principio a fin sin ancla. El auditor ancla en "FALLO DE LA
  CORTE SUPREMA" y busca el dispositivo solo post-apertura. Adoptar
  esa arquitectura resuelve B013 y es la dirección correcta para
  B055, B056, B057.
- **146 falsos positivos post-apertura:** variantes de dispositivo
  (`en_consecuencia`, `por_estas_razones`, etc.) matchean texto
  argumentativo DENTRO del cuerpo del fallo, después de la apertura.
  El fix B013 no los toca. Requieren tratamiento separado (filtro
  argumental en variantes, o búsqueda desde el final del bloque).
- **57 "regresiones" son exposición de bugs preexistentes:**
  detectar_fin_real corta el bloque antes del dispositivo real
  (fallo continúa en el gap), o el bloque contiene dos fallos y
  el caso_id corresponde al fallo previo a la apertura.
### Scripts generados (en scripts/diagnostico/)
- `diag_b013_muestra.py` — diagnóstico de 12 casos testigo.
- `diag_b013_cuantificar.py` — cuantificación completa prematuros
  vs post-apertura sobre los 479 casos.
- `parser_b013.py` — pipeline paralelo con fix (v2 final).
- `comparar_b013.py` — diff caso a caso entre CSV productivo y fix.
### Artefactos en output/diagnostico/B013/
- `csjn_casos_b013.csv`, `csjn_casos_b013_votos.csv` — output del
  pipeline paralelo v2.
- `parser_b013_log.txt`, `parser_b013_log_v2.txt` — logs de corrida.
- `comparar_b013_log.txt`, `comparar_b013_log_v2.txt` — logs del
  comparador.
### Decisiones
- Fix commiteado en parser.py. Búsqueda anclada de dispositivo con
  cascada apertura_rel → dictamen_end+1 → 0 y techo en votos
  post-apertura.
- B013 cerrado para el universo de 302 prematuros.
- 146 post-apertura documentados como sub-problema separado.
### Pendiente → H036
- Análisis de los ~813 fallos sin firma (363 con_disp_sin_firma +
  450 sin_dispositivo, excluidos 160 sumario_con_link).
- Limpiar output/diagnostico/B013/ y scripts de diagnóstico.
- Investigar n_jueces=11 y n_jueces=14 (posible B055 expuesto).
- Actualizar DEUDA_TECNICA: cerrar B013, abrir sub-bug post-apertura.

---
**Fecha:** 2026-05-18
**Sesión:** H036
### Objetivo
Diagnóstico y clasificación de los 813 fallos sin firma post-fix B013.
Fix de dictamen no cerrado (backstop RE_APERTURA).
### Trabajo realizado
- Corrida del parser con fix B013 commiteado en H035 (CSV estaba desactualizado).
- Clasificación de los 813 sin_firma en 6 categorías con evidencia empírica:
  - A1 B059 falso positivo post-apertura: 265 casos.
  - A2 dispositivo real, firma falla: 39 casos (concentrados en tomos 329-330).
  - A3 outcome=otro + verbo resolutivo (ambiguos): 59 casos.
  - B1a dispositivo embebido en considerando (page header mid-line): 27 casos.
  - B1b sin frase de dispositivo (truncado por detectar_fin_real): 258 casos.
  - B2 sin apertura: 165 casos.
- Auditoría con auditar_fallo.py de muestras de 10 casos por categoría (seed=42).
  Hallazgo: solapado_con_proximo dominante (7-10/10 en cada categoría).
- Matriz de priorización por impacto, riesgo, robustez, escalabilidad, dificultad.
- Debug con pipeline real en 4 casos testigo (329_p6064, 340_p812, 330_p1305,
  348_p1569). Tres causas raíz confirmadas empíricamente:
  1. Dictamen no cerrado: len(prev) >= 80 impide cierre por fecha, dictamen
     consume FALLO DE LA CORTE SUPREMA y todo el cuerpo del fallo. Confirmado
     en 348_p1569 (en_dict_final=True, 135 líneas consumidas).
  2. Truncamiento por detectar_fin_real: dispositivo cae más allá de fin_real.
     Confirmado en 329_p6064.
  3. Formato no reconocido: dispositivo existe pero no matchea variantes.
     Confirmado en 340_p812.
- Fix: backstop en loop de dictamen — si en_dictamen=True y la línea matchea
  RE_APERTURA ("FALLO/SENTENCIA DE LA CORTE SUPREMA"), cerrar dictamen sin
  consumir la línea. 7 líneas de código.
- Validación: pipeline paralelo (parser_h036.py), comparador caso a caso.
  31 mejoras, 0 regresiones, 6 cambios neutros (5 B059 expuestos + 1
  corrección de dispositivo). Verificación visual con mostrar_caso.py
  sobre 331_p446: líneas del .md marcadas como dictamen antes vs libres ahora.
- Commit del fix en parser.py.
### Hallazgos principales
- **Dictamen desbordado como causa raíz sistémica:** la heurística de cierre
  del dictamen (fecha + prev < 80 chars) falla en dictámenes largos donde la
  última línea del Procurador tiene >= 80 caracteres. Afecta ~31 casos
  directamente, probablemente más en combinación con otras causas.
- **813 sin_firma se descomponen en causas raíz independientes:** B059 (265),
  truncamiento (258), sin apertura (165), formato (66), ambiguos (59).
  No es un solo bug — son 4-5 problemas ortogonales.
- **M08 (dos zonas) resolvería 388 casos:** B1b (223) + B2 (165) comparten
  causa de fondo: el bloque no contiene el fallo completo. La migración a
  arquitectura de dos zonas (dictamen ← FALLO DE LA CORTE → cuerpo) los
  resolvería de raíz.
### Scripts generados (en scripts/diagnostico/)
- `diag_h036_sin_firma.py` — clasificación + auditoría de los 813.
- `debug_h036.py` — debug con pipeline real en casos testigo.
- `validar_fix.py` — comparador antes/después de los 31 mejorados.
- `mostrar_caso.py` — evidencia visual línea por línea del fix.
- `H036/parser_h036.py` — pipeline paralelo con fix.
### Artefactos en output/diagnostico/H036/
- `csjn_casos_h036.csv`, `csjn_casos_h036_votos.csv` — output del fix.
- `diag_h036_resumen.txt` — resumen cuantitativo.
- `ids_*.txt` — IDs de cada categoría.
- `auditoria_*.md` — auditorías de muestras.
### Decisiones
- Fix commiteado: backstop dictamen con RE_APERTURA.
- B059 (329 casos) postergado: impacto benigno (outcome=otro), fix complejo.
- B1b + B2 (388 casos) postergados: requieren M08 (dos zonas).
- Próxima sesión: fix formato no reconocido (65 casos) + clasificar A3 (60).
### Pendiente → H037
- Fix formato no reconocido (B1a 26 + A2 39): auditar patrones, agregar variantes.
- Clasificar A3 (60 casos): ¿B059 sutiles o firma real?
- Evaluar estrategia B059: búsqueda desde final vs filtro argumental.
- Regenerar CSV productivo con el fix commiteado.
- Actualizar DEUDA_TECNICA: cerrar fix dictamen, documentar categorías.

---
**Fecha:** 2026-05-18
**Sesión:** H038
### Objetivo
Fix B059: falso positivo post-apertura. Variantes de dispositivo ("en
consecuencia", "de conformidad", etc.) matchean texto argumental, no
dispositivo real. 329 casos identificados en H036 (265 A1 + 59 A3 + 5
expuestos por backstop).
### Trabajo realizado
- Diagnóstico con `diag_h038_b059.py`: para cada caso B059, buscar TODOS
  los matches de dispositivo en la ventana y verificar presencia de firma
  en 40 líneas. Hallazgo clave: 0/363 primeros matches tienen firma;
  273/283 últimos matches sí tienen firma.
- Evaluación de 4 estrategias con pipeline paralelo sobre 5702 fallos:
  1. Reversa pura (desde fin_busqueda): 278 mejoras, 86 regresiones.
     Causa: dispositivos de votos individuales o resoluciones secundarias.
  2. Reversa desde inicio_votos_indiv: 146 mejoras, 8 regresiones.
     Mejora el techo pero pierde casos sin votos detectados.
  3. Reversa desde votos + validación firma: 147 mejoras, 7 regresiones.
     Salva acordadas pero no resuelve múltiples resoluciones en mayoría.
  4. Forward + validación firma: 280 mejoras, 0 regresiones. Elegida.
- Fix aplicado en parser.py: forward con firma. Primer match con
  `linea_es_firma_de_juez` en 40 líneas gana. Si ninguno tiene firma,
  fallback al primer match (= comportamiento pre-fix).
- Pipeline completo: 5862 casos, 0 errores. sin_firma 782 → 503.
  Verificación CSV a CSV: 0 regresiones confirmadas.
### Hallazgos principales
- **La firma como discriminador perfecto de falso positivo:** en los 363
  casos B059, 0 primeros matches tienen firma. En los ~5000 normales, el
  primer match sí tiene firma. La señal es binaria y no requiere
  heurísticas argumentales.
- **La búsqueda reversa es peligrosa:** bloques con múltiples "Por ello"
  en la zona de mayoría (resoluciones con puntos I, II, III; acordadas
  embebidas) hacen que el último match no sea el principal. Forward con
  validación es más robusto que reverse con cualquier guardia.
- **90 casos fallback_sin_firma:** 90 casos donde ningún dispositivo tiene
  firma en 40 líneas. Son los mismos 88 sin_cambio del diagnóstico parcial
  (81 con un solo match, 7 con cambio de dispositivo pero sin firma).
  Requieren fix separado (B055 firma partida, formatos no reconocidos).
### Scripts generados
- `diag_h038_b059.py` — diagnóstico: todos los matches por caso.
- `pipeline_h038_reversa.py` — test reversa pura (descartada).
- `pipeline_h038_full.py` — test reversa full 5702 (descartada).
- `pipeline_h038_desde_votos.py` — test reversa desde votos (descartada).
- `pipeline_h038_reversa_firma.py` — test reversa+firma (descartada).
- `pipeline_h038_forward_firma.py` — test forward+firma (elegida).
### Decisiones
- Fix commiteado: forward con validación de firma.
- CSV productivo actualizado (5862 casos, 503 sin_firma).
- B059 cerrado como bug activo. 90 residuales son sub-problemas distintos.
### Pendiente → H039
- Actualizar DEUDA_TECNICA: cerrar B059, actualizar conteos.
- 90 fallback_sin_firma: clasificar (¿B055? ¿formato? ¿single-match?).
- Formato no reconocido (B1a 27 + A2 39): postergado de H037.
- Investigar los 98 cambio_outcome del full pipeline.

---
**Fecha:** 2026-05-18
**Sesión:** H039
### Objetivo
Formato no reconocido: identificar y agregar variantes de dispositivo
faltantes en RE_DISPOSITIVO_VARIANTES. Diagnóstico de los 503 sin_firma
post-H038.

### Trabajo realizado
- Diagnóstico cuantitativo de los 503 sin_firma:
  - 165 sin apertura (B2, bloqueado por M08).
  - 249 sin_dispositivo con apertura → clasificados con `diag_h039_formato.py`:
    77 B1a (formato no reconocido), 172 B1b (truncamiento).
  - 89 con dispositivo sin firma (36 con outcome real, 53 fallback B059).
- Inspección con `inspect_b1a.py` de 18 casos B1a: confirmadas líneas
  de dispositivo al inicio de línea con variantes no cubiertas.
- 9 variantes candidatas identificadas:
  `por_lo_expresado`, `por_las_razones`, `por_las_consideraciones`,
  `en_atencion`, `en_las_condiciones`, `por_lo_tanto`, `oido_el`,
  `que_por_ello`, `que_de_conformidad`.
- Pipeline paralelo forward+firma con 9 variantes: 33 mejoras, 0
  regresiones firma, **67 regresiones outcome** (specific→otro).
  Causa: `en_las_condiciones` (40), `por_lo_tanto` (17), `en_atencion` (17)
  son frases argumentativas comunes que matchean antes del dispositivo real.
- Pipeline paralelo con 6 variantes (sin las 3 peligrosas): 24 mejoras,
  0 regresiones firma, 4 cambios outcome (3 de `que_de_conformidad`).
- Pipeline paralelo reversa desde votos + 9 variantes: 33 mejoras, 0
  regresiones firma, **193 cambios outcome**. Reversa descartada —
  confirma hallazgo H038: múltiples "Por ello" en zona de mayoría hacen
  que el último no sea el principal.
- Fix final: 5 variantes seguras en forward+firma. Pipeline productivo:
  22 mejoras, 0 regresiones. sin_firma 503 → 481. Commiteado.

### Hallazgos principales
- **Clasificación de los 249 sin_disp+apertura:** 77 B1a (31%) tienen
  texto resolutivo que el parser no reconoce; 172 B1b (69%) están
  genuinamente truncados. El grueso del problema (B1b + B2 = 337 casos)
  requiere M08 (arquitectura de dos zonas).
- **Variantes argumentativas vs dispositivo:** frases como "En las
  condiciones expresadas", "Por lo tanto", "En atención a" son
  dispositivo en ~30% de los casos pero argumentativas en ~70%. No sirven
  para forward search. "Por lo expresado", "Por las razones expuestas",
  "Oído el" son exclusivas del dispositivo.
- **Reversa sigue siendo peor que forward:** 193 vs 67 cambios de outcome
  con las mismas variantes. El último "Por ello" en la zona de mayoría
  frecuentemente es una resolución accesoria (desestimación de queja,
  intimación) y no el dispositivo principal.
- **B055 expuesto:** "RICARDO LUIS" en desconocidos subió de 26 a 30.
  Casos nuevos con dispositivo detectado exponen firma partida de
  Lorenzetti.

### Scripts generados (en scripts/diagnostico/H039/)
- `diag_h039_formato.py` — clasificación B1a vs B1b de los 249 casos.
- `inspect_b1a.py` — inspección de líneas opener en 18 casos candidatos.
- `pipeline_h039_variantes.py` / `pipeline_h039_variantesv6.py` — pipelines
  paralelos forward con 9/6 variantes.
- `pipeline_h039_reversa.py` — pipeline paralelo reversa desde votos.
- `analizar_cambios.py` — análisis de cambios de outcome nuevo vs productivo.

### Artefactos en output/diagnostico/H039/
- `diag_formato_detalle.md` — detalle caso por caso de B1a y B1b.
- `csjn_casos_h039.csv`, `csjn_casos_votos_h039.csv` — último output paralelo.

### Decisiones
- Fix commiteado: 5 variantes seguras (`por_lo_expresado`, `por_las_razones`,
  `por_las_consideraciones`, `oido_el`, `que_por_ello`).
- Descartadas: `en_las_condiciones`, `por_lo_tanto`, `en_atencion` (falsas
  en forward), `que_de_conformidad` (3 regresiones, 0 mejoras).
- Reversa descartada (peor que forward en cambios de outcome).

### Pendiente → H040
- B055 (firma partida): 30 "RICARDO LUIS" en desconocidos. Prioridad alta.
- B1b truncamiento (172 casos) + B2 sin apertura (165): requieren M08.
- B1a residual (~53 casos): dispositivo mid-line por OCR line-wrap.
- 89 con dispositivo sin firma: clasificar sub-causas.
- Actualizar DEUDA_TECNICA con conteos post-H039.
- Limpiar output/diagnostico/H039/ (conservar solo diag_formato_detalle.md).

### Validación post-H039: auditoría comparativa (18/5/2026)

Corrida de validación para confirmar que los cambios acumulados
(Fase F, B049, B052, variantes de dispositivo) no introdujeron
regresiones en el parser.

| Muestra | N | Baseline | Resultado |
|---|---|---|---|
| Casos individuales (archivo/, 08-09/05) | 7 | Pre-Fase F | 6 idénticos, 1 mejora |
| 80 casos seed 2024 (17/05) | 80 | Pre-H039 | Idéntico |
| 12 casos seed 891 (17/05) | 12 | Pre-H039 | Idéntico |
| 5 casos seed 137 (17/05) | 5 | Pre-H039 | Idéntico |
| **Total** | **104** | | **0 regresiones, 1 mejora** |

Mejora detectada: `339_p1648` (B.C., J.G. c/ R.P.) — el catálogo
viejo incluía 32 líneas de residuo del caso siguiente (DANNA);
el nuevo las excluye correctamente.

Outputs en `output/auditoria/auditar_fallo/compare_*.md` (no versionados).
---
**Fecha:** 2026-05-18
**Sesión:** H040
### Objetivo
Reducir sin_firma refinando la detección de sumarios en `detectar_fin_real`
(Pista 2). Diagnóstico comparativo de heurísticas parser vs auditor.

### Trabajo realizado
- Diagnóstico cuantitativo `diagnostico_pista2_sumario.py`: comparación
  línea por línea de `linea_es_header_sumario` (parser) vs
  `es_header_sumario_auditoria` (auditor) sobre 1.239.055 líneas en la
  zona exacta donde `detectar_fin_real` aplica Pista 2.
  - Match ambas funciones: 10.740 (sumarios reales).
  - Solo parser: 124 falsos positivos (38 firma-related, 38 carátulas,
    40 otro, 8 mayúsculas cortas).
  - Solo auditor: 40.798 (15.676 headers de página, 13.955 mayúsculas
    cortas, 5.719 marcadores apertura, 2.828 firmas, 2.404 carátulas).
- Resumen desde `csjn_casos.csv`: de los 481 sin_firma, 405 usan
  `pista_fin=caratula_siguiente`, 58 `sumario_siguiente`, 10
  `marcador_apertura_siguiente`, 8 `firma_actual`.
- POC `poc_pista2_guardas.py`: replica `detectar_fin_real` con wrapper
  `linea_es_header_sumario_guardado` que excluye firmas, calificadores,
  headers de página, marcadores de apertura y headers de voto/disidencia.
  Resultado: 238 casos con cambio en `linea_fin_real` (233 extensiones,
  5 contracciones). 34 sin_firma afectados (candidatos a mejora).
- Pipeline paralelo `parser_h040_guardas.py` con fix aplicado. Validación
  campo por campo contra CSV productivo:
  - firma_raw: 170 cambios (32 sin_firma→con_firma, 138 firmas extendidas).
  - outcome: 1 cambio (otro→revoca), 0 regresiones a sin_dispositivo.
  - voting_pattern: 55 cambios (unanime→disidencia/segun_su_voto).
  - n_jueces: 169 cambios (mayoritariamente al alza: 2→5, 5→7).
  - 0 regresiones en ningún campo.
- Fix aplicado a `parser.py` productivo. Pipeline re-corrido. Commiteado.

### Hallazgos principales
- **El auditor es bueno por arquitectura, no por heurística:** la función
  `es_header_sumario_auditoria` del auditor matchea 40.798 líneas que NO
  son sumarios en la zona Pista 2 (headers de página, firmas, aperturas).
  El auditor funciona bien porque restringe espacialmente (sumarios solo
  entre carátula y dictamen/apertura), no porque su heurística sea mejor.
  Adoptar la heurística del auditor en Pista 2 empeoraría las cosas.
- **El parser tiene pocos falsos positivos, pero letales:** 124 líneas
  en total, pero 38 son firmas (ARGIBAY en disidencia, calificadores de
  firma) que truncan bloques antes de la firma real. Fix: guardas de
  exclusión, no cambio de heurística.
- **JUECES_CONOCIDOS no matchea apellido solo:** "ARGIBAY (en disidencia)."
  pasa `linea_es_header_sumario` pero no `linea_es_firma_de_juez` porque
  el pattern exige nombre de pila ("carmen m. argibay"). La guarda
  `RE_CALIFICADOR` es la que lo atrapa.
- **Impacto en cascada:** las 32 firmas recuperadas arrastran 169
  correcciones de n_jueces y 55 enriquecimientos de voting_pattern.
  Un bloque más largo → más texto → más votos detectados → mejor análisis.
- **B054 (epílogo) sigue presente:** las firmas recuperadas incluyen
  epílogo pegado ("Tribunales que intervinieron con anterioridad: ...").
  Comportamiento pre-existente, no introducido por este fix.

### Scripts generados (en scripts/diagnostico/)
- `diagnostico_pista2_sumario.py` — comparación cuantitativa parser vs auditor.
- `poc_pista2_guardas.py` — POC de exclusión en Pista 2.
- `parser_h040_guardas.py` — pipeline paralelo con fix.
- `comparar_h040.py` — comparación antes/después por caso.

### Artefactos en output/diagnostico/H040/
- `csjn_casos.csv`, `csjn_casos_votos.csv` — output del pipeline con fix.
- `snapshot_pre_h040_csjn_casos.csv`, `snapshot_pre_h040_csjn_casos_votos.csv`.
- `pista2_sumario_detalle.csv` — detalle de falsos positivos.
- `poc_pista2_guardas_cambios.csv` — cambios del POC.

### Decisiones
- Fix commiteado: guardas de exclusión en Pista 2 (`linea_es_header_sumario_guardado`).
- Opción 1 (B055 "ricardo luis" en JUECES_CONOCIDOS) postergada — parche
  nominal, no solución robusta.
- Opción 2 (refinar heurística de sumario) descartada con datos — el
  problema no es la heurística sino la falta de exclusiones.
- Opción 5 (M08 dos zonas) sigue pendiente para B1b+B2 (337 casos).

### Pendiente → H041
- B055 (firma partida por salto de línea): 345 casos con firma truncada.
- B1b truncamiento (172) + B2 sin apertura (165): requieren M08.
- B1a residual (~53): dispositivo mid-line por OCR line-wrap.
- Investigar 2 casos con wc_mayoria que baja mucho (329_p1307, 329_p4811).
- Opción 4: diagnosticar los 89 con dispositivo sin firma.


---
**Fecha:** 2026-05-18
**Sesión:** H041
### Objetivo
Reducir sin_firma con búsqueda Tier 2 de dispositivo mid-line (.search()
como fallback de .match() cuando Tier 1 no encuentra nada).

### Trabajo realizado
- Diagnóstico cuantitativo de los 392 sin_dispositivo:
  - 227 con apertura (B1a+B1b), 165 sin apertura (B2).
  - 220 hits de .search() mid-line sin filtro — mayoría argumentales.
  - Con filtro de firma validada: 51 candidatos.
  - Distribución por patrón: de_conformidad 25, por_ello 10,
    en_consecuencia 7, atento_a 5, por_lo_exp 3, por_las_razones 1.
- Análisis caso por caso de los 51: ~12 dispositivos reales, ~5 falsos
  argumentales, ~4 ambiguos. Discriminador clave: los dispositivos reales
  tienen fin de oración antes del match (. o )), los argumentales tienen
  conjunción (, y por ello).
- Implementación de Tier 2 con triple guarda:
  (a) solo patrones seguros (por_ello + variantes H039),
  (b) contexto de fin de oración antes del match,
  (c) filtro POR_ELLO_ARGUMENTAL,
  (d) firma validada obligatoria sin fallback.
- Pipeline paralelo parser_h041.py: 11 mejoras, 0 regresiones, 0 otros
  cambios. Verificación CSV a CSV campo por campo.
- Fix commiteado en parser.py (29184ba). sin_firma 449 → 438.

### Hallazgos principales
- **Los patrones peligrosos de H039 son igual de peligrosos mid-line:**
  de_conformidad (25 hits), en_consecuencia (7), atento_a (5) son
  argumentales en la mayoría de los casos incluso con firma validada
  cercana. La firma valida presencia pero no distingue dispositivo real
  de texto argumental cerca del final del fallo.
- **El contexto previo es el discriminador clave:** dispositivos reales
  a mitad de línea siempre aparecen después de punto o cierre de
  paréntesis (fin de oración del considerando). Los usos argumentales
  aparecen después de conjunciones (", y por ello", "y por ello").
- **Tier 2 es ortogonal a Tier 1:** solo se activa cuando Tier 1 no
  encontró ni match validado ni fallback. No puede causar regresiones
  en casos que ya tienen dispositivo.
- **11 de los 14 estimados se recuperaron:** 3 casos del diagnóstico
  no pasaron alguna guarda (329_p573 contexto ambiguo, 329_p5950 y
  339_p1223 probablemente filtrados por argumental).

### Scripts generados (en scripts/diagnostico/H041/)
- `aplicar_patch_h041.py` — genera parser_h041.py con Tier 2.
- `comparar_h041.py` — comparación antes/después por caso.

### Artefactos en output/diagnostico/H041/
- `parser_h041.py` — parser parcheado (ya copiado a productivo).
- `csjn_casos_h041.csv`, `csjn_casos_votos_h041.csv` — output paralelo.
- `snapshot_pre_h041_csjn_casos.csv`, `snapshot_pre_h041_csjn_casos_votos.csv`.

### Decisiones
- Fix commiteado: Tier 2 mid-line con triple guarda.
- Patrones mid-line restringidos a los seguros (por_ello + 6 variantes
  H039). de_conformidad, en_consecuencia, atento_a excluidos.
- B1a residual post-H041: ~42 casos (53 - 11). Recuperables si se
  encuentran guardas para de_conformidad et al, o con M08.

### Pendiente → H042
- B055 firma partida (345 casos): diagnosticar si causa raíz es
  max_lines=40 que se consume en texto del dispositivo.
- Opción 3: 57 con dispositivo sin firma (clasificar sub-causas).
- Opción 4: 2 casos wc_mayoria que baja (329_p1307, 329_p4811).
- Actualizar DEUDA_TECNICA con conteos post-H041.

---
**Fecha:** 2026-05-18
**Sesión:** H042
### Objetivo
Fix B055: firma truncada/contaminada en `collect_firma_lines`.
Transición de cobertura (sin_firma) a calidad de datos (firma_raw).
### Trabajo realizado
- Re-cuantificación de B055 contra CSV actual (post-H041): 237 casos
  (no 345 como estimado en H033 — B013 fix resolvió ~108).
- Clasificación en dos subtipos: Tipo 1 contaminada (189, firma OK +
  basura post-firma) y Tipo 2 truncada (48, nombre cortado mid-línea).
- PoC v1: eliminar max_lines + guarda es_continuacion_firma en toda
  línea. Resultado: 985 mejoras, 1298 regresiones. La guarda cortaba
  mid-nombre porque JUECES_CONOCIDOS requiere nombre completo y las
  líneas físicas tienen nombres partidos.
- PoC v2: guarda condicional — solo aplicar si última línea recolectada
  termina en punto. Resultado: 1273 mejoras, 181 regresiones. Abreviaturas
  tipo "M." (Carmen M.) y "S." (Carlos S.) generaban falsos positivos
  de punto final.
- PoC v3 (final): guarda sobre texto acumulado — `_RE_FIRMA_COMPLETA`
  (regex de apellidos conocidos + calificador opcional + punto) sobre
  `" ".join(firma_lines)`. Solo activa guarda cuando el texto acumulado
  termina en apellido conocido. "CARMEN M." no matchea (sigue), "CARMEN
  M. ARGIBAY." matchea (guarda). Resultado: 1262 mejoras, 31 regresiones.
- Auditoría manual de las 31 regresiones contra MD crudo: 0 reales.
  Categorías: headers de disidencia comidos (12), abogados con apellido
  de juez en post-firma (4, incluyendo Rosenkrantz y Zaffaroni como
  letrados patrocinantes), texto editorial post-firma (12), bug
  preexistente expuesto (1: 347_p520), cosmético (1).
- Verificación: nj=1 prod 23 → fix 24 (1 caso: 347_p520 preexistente).
- Pipeline productivo: output idéntico al paralelo campo por campo.
- Commit `e258f66`, push OK.
### Hallazgos principales
- **B055 tenía dos subtipos distintos:** Tipo 1 (contaminada, 80%) y
  Tipo 2 (truncada, 20%). El fix resuelve ambos con un solo mecanismo.
- **Abogados con apellido de juez:** Rosenkrantz (letrado en 338_p1389),
  Zaffaroni (patrocinante en 347_p321), Belluscio (patrocinante en
  339_p921), García Mansilla (patrocinante en 338_p884) aparecían como
  jueces firmantes en el productivo. El fix los elimina correctamente.
- **RE_DISID_HDR/RE_VOTO_HDR no toleran headers multi-línea:** la firma
  comía headers de disidencia partidos en dos líneas. La guarda B055
  los cubre como segunda línea de defensa.
- **Desconocidos como indicador de calidad:** la caída de "Ricardo Luis"
  (196→7) y "Juan Carlos" (64→0) confirma que los nombres truncados
  mid-línea se resuelven. Los residuales (Estado Nacional 45, Fisco
  Nacional 21) indican firma_raw con leaking post-firma residual.
### Scripts generados (en scripts/diagnostico/H055/)
- `diag_b055_recuantificar.py` — re-cuantifica B055 contra CSV actual.
- `diag_b055_subtipos.py` — clasifica en Tipo 1 y Tipo 2.
- `aplicar_patch_b055.py` — genera parser parcheado v1.
- `aplicar_patch_b055_v2.py` — v2 (guarda condicional por punto).
- `aplicar_patch_b055_v3.py` — v3 final (guarda por texto acumulado).
- `comparar_b055_fix.py` — comparación campo por campo prod vs fix.
- `auditar_regresiones_b055.py` — MD crudo de las 31 regresiones.
- `commit_b055.py` — snapshot + parcheo del productivo.
- `commit_b055_verify.py` — verificación prod vs paralelo.
### Artefactos en output/diagnostico/B055/
- `csjn_casos_b055_fix.csv`, `csjn_casos_b055_fix_votos.csv` — output paralelo v3.
- `snapshots/snapshot_pre_b055_*.csv` — snapshots pre-fix.
### Decisiones
- Fix commiteado con guarda de texto acumulado (`_RE_FIRMA_COMPLETA`).
- Enfoque de apellidos conocidos preferido sobre regex genérico de
  abreviatura (`\b[A-Z]\.$`) por robustez: no deja pasar líneas sin
  chequeo, degrada a breaks estructurales para conjueces desconocidos.
- B055 cerrado. Residuos documentados en DEUDA_TECNICA.
- Cinco bugs nuevos documentados: B061-B065.
### Pendiente para próximas sesiones
- B063: agregar conjueces faltantes a JUECES_CONOCIDOS (fix mecánico, ~39 casos).
- B064: verificar encoding de LUIS CÉSAR OTERO (9 casos).
- Auditoría de segmentos parser vs auditor (Opción B del prompt H042).
- Actualizar conteos sin_firma en DEUDA_TECNICA (ahora 425).

# ============================================================
# BITACORA — APPEND (agregar al final, después del bloque H042)
# ============================================================

### Nota de productividad
Sesión H042 fue excepcionalmente productiva: 3 iteraciones de PoC
(v1→v2→v3) diagnosticadas, implementadas y evaluadas en una sola
sesión. Ciclo completo desde re-cuantificación (número stale 345→237),
clasificación en subtipos (Tipo 1/Tipo 2), 3 versiones de fix con
evaluación empírica, auditoría manual de 31 regresiones, hasta
commit y push — todo en H042.

Hallazgos destacados:
- **Transición cobertura→calidad:** primera sesión focalizada en
  calidad de datos existentes en vez de expandir cobertura sin_firma.
  Retorno mayor por esfuerzo que las últimas 3 sesiones de cobertura
  combinadas (H039=22, H040=32, H041=11 vs H042=1262 mejoras).
- **Abogados contados como jueces:** Rosenkrantz como letrado
  patrocinante (338_p1389), Zaffaroni como letrado (347_p321),
  Belluscio como patrocinante (339_p921), García Mansilla como
  patrocinante (338_p884). El productivo los contaba como jueces
  firmantes — inflando n_jueces silenciosamente.
- **Número stale como riesgo:** el universo B055 (345 casos) venía
  de H033 y nunca se re-cuantificó post-B013. El paso 0 de
  re-cuantificación evitó diseñar un fix para un universo equivocado.
- **Iteración rápida de PoC:** v1 (1298 regresiones) → v2 (181) →
  v3 (31, todas falsas) muestra el valor de evaluar antes de commitear.
  Cada iteración reveló un patrón nuevo (nombres partidos, abreviaturas,
  texto acumulado).


# ============================================================
# PROMPT H043
# ============================================================

## H043 — Conjueces B063 + inventario headers voto/disidencia

**Fecha:** 2026-05-19
**Sesión:** H043
**Commit:** `8a2558e` (B063: 10 conjueces + fix cosmético desconocidos)

### Objetivo

Fase 1: agregar conjueces faltantes a JUECES_CONOCIDOS (B063).
Fase 2: auditoría de headers de disidencia/voto (inventario completo).
Fase 3 (no alcanzada): validación cruzada firma↔votos (B065).

### Fase 1 — B063 conjueces (cerrado)

**Problema:** 10 conjueces frecuentes no estaban en JUECES_CONOCIDOS,
causando n_jueces subestimado en ~40 casos.

**Proceso:**
1. Primer intento: patch directo al vivo (error metodológico — violó
   protocolo PoC→validar→commitear). Se restauró con `git checkout`.
2. PoC v1: 9 conjueces. 36 mejoras, 0 regresiones. Descubrió:
   - PEREYRA (no PEREIRA) — typo en la lista del plan H043.
   - Rita Mill de Pereyra — conjuez adicional no contemplada (2 casos).
   - Bug cosmético línea 550: filtro de desconocidos no stripea "(conjuez)".
   - B064 (Otero "encoding") era el mismo bug cosmético, no encoding.
3. PoC v2: 10 conjueces + fix cosmético + Pereyra corregido.
   40 mejoras, +55 votos, 0 regresiones.
4. Patch producción + commit `8a2558e`.

**Conjueces agregados (10):**

| Conjuez | Casos | Nota |
|---|---|---|
| Najurieta | 8 | |
| Alcalá | 9 | |
| Morán | 7 | |
| Tyden de Skanata | 5 | CV confirmado: camarista federal Posadas |
| Pereyra González | 5 | Corregido de PEREIRA. Variante Carlos Martín |
| Ferro | 5 | |
| Pacilio | 6 | |
| Argañaraz | 4 | |
| Poclava Lafuente | 3 | |
| Mill de Pereyra | 2 | Nueva, no estaba en plan H043 |

**Excluido:** Eduardo Moliné O'Connor — destituido 12/2003 por juicio
político, no puede ser conjuez. Sus 3 apariciones son ruido.

**Fix cosmético (línea 550):**
```python
# Antes:
nombres_jueces = {j["nombre"].lower() for j in jueces_out}
# Después:
nombres_jueces = {j["nombre"].split(" (")[0].lower() for j in jueces_out}
```
Resuelve que "otero (conjuez)" no se filtraba contra "luis césar otero".
Cierra B064.

**Métricas post-H043:**
- sin_firma: 425 → 422 (-3)
- Votos: 25548 → 25603 (+55)
- JUECES_CONOCIDOS: 28 → 38 entradas

### Fase 2 — Inventario headers voto/disidencia

**Script:** `scripts/diagnostico/H043/inventario_headers_voto.py`

**Resultado del inventario:**
- Headers escaneados: 3539 (1490 voto + 2049 disidencia + 8 otro)
- Cobertura RE_VOTO_HDR/RE_DISID_HDR: 81% (2868/3539)
- No matchean: 210 voto + 461 disidencia
- Multi-línea B061: 26 (2 voto + 24 disidencia)

**Gaps principales:**
- "juez/jueza" no en grupo de títulos (~85 headers reales)
- "concurrente" no soportado (~12)
- "doctor/doctora" (~15)
- "vicepresidenta" femenino (~3)
- Multi-línea B061 (26)
- "Ampliación de fundamentos" — tipo nuevo (8)
- Muchos "no matchean" son ruido: firma fragmentada (~200) y citas en texto (~40)

**PoC juez/jueza — DESCARTADO (regresiones):**
Agregar `Juez(?:as?|es)?` al grupo de títulos causa:
- sin_firma: 422 → 441 (+19 regresión)
- sin_dispositivo: 380 → 400 (+20 regresión)
- Votos: 25603 → 25519 (-84)
- Casos con n_jueces→0: 330_p2800, 330_p304

**Causa:** "voto del juez [NOMBRE]" aparece en texto corrido (considerandos,
citas jurisprudenciales). RE_VOTO_HDR.match() interpreta inicio de línea
como header de sección → corta bloque → pierde firma y dispositivo.
"Señor Ministro" no tiene este problema por ser formal y exclusivo de headers.

**Conclusión:** ampliar los regex de headers requiere filtro posicional —
buscar solo después del cierre de la mayoría. Documentado como B066,
bloqueado por M08 (arquitectura de dos zonas).

### Lecciones metodológicas

1. **Nunca patchear el vivo sin PoC validado.** El primer intento aplicó
   directo sobre parser.py, corrompiendo el archivo. Restaurado con
   `git checkout`. A partir de ahí, todo PoC → validar → commitear.
2. **Hash SHA-256 como check de integridad.** CRLF vs LF entre uploads
   y disco genera hashes distintos; usar bytes crudos del disco.
3. **Diagnóstico antes de fix:** PEREYRA (no PEREIRA) se descubrió
   recién al correr el PoC. B064 no era encoding sino bug cosmético.
4. **PoC descarta regresiones temprano:** el PoC de juez/jueza reveló
   19 regresiones de sin_firma en 3 minutos, evitando un commit roto.

### Scripts generados (en scripts/diagnostico/H043/)
- `poc_b063_conjueces.py` — PoC v1 (9 conjueces).
- `poc_b063_v2.py` — PoC v2 (10 conjueces + Pereyra + fix cosmético).
- `patch_b063_produccion.py` — patch definitivo.
- `diag_b063_desconocidos.py` — diagnóstico desconocidos post-v1.
- `inventario_headers_voto.py` — Fase 2 inventario completo.
- `poc_juez_header.py` — PoC juez/jueza (descartado por regresiones).

### Pendiente para próximas sesiones
- B066: headers con "juez/jueza" requieren filtro posicional (M08).
- B065: validación cruzada firma↔votos (Fase 3 no alcanzada).
- Auditoría de segmentos parser vs auditor (Opción B de H042).
- Desconocidos residuales: Estado Nacional (45), Fisco Nacional (21)
  son post-firma leaking. Truncados: Ricardo Luis (Lorenzetti),
  CARMEN M. (Argibay), Manuel José García (García Mansilla).


# PROMPT H044

## H044 — Análisis arquitectónico de segmentación por zonas + B067

**Sesión:** H044
**Fecha:** 2026-05-19
**Objetivo original:** análisis arquitectónico puro — entender cómo
segmentan parser y auditor, identificar delimitadores robustos para zonas,
diseñar incorporación de segmentación sin reescritura total.
**Resultado:** análisis completado + hallazgo empírico que invalidó B066 +
fix B067 (17 mejoras, sin_firma 422→406).

### Fase 1 — Mapeo de segmentación parser vs auditor

Recorrido completo de `procesar_archivo()` (parser) y `segmentar_bloque()`
(auditor). Documentado el grafo de dependencias:

**Parser:** loop único → dictamen + votos(narrow) → dispositivo(anchored,
techo=inicio_votos_indiv) → firma(collect_firma_lines) → analítica.
Dependencia circular: votos → techo → dispositivo → firma → (se querría
votos ampliado post-firma).

**Auditor:** pasos independientes modulares. Detecta dictamen, apertura,
votos, por_ello, firma como funciones separadas con scope restringido.
PERO: `detectar_votos_y_disidencias()` también busca en todo el bloque
(misma limitación que el parser, solo que no causa problemas con la
regex narrow actual).

### Fase 2 — Evaluación de opciones de diseño

Cuatro opciones evaluadas:

| Opción | Idea | Resultado |
|--------|------|-----------|
| A — Post-firma aditivo | Agregar scan ampliado post-firma | PoC: 42 matches, 42/42 citas. Beneficio ~0 |
| B — Two-pass | Separar loop en dos pasadas | No implementado, riesgo medio |
| C — Auditor portado | Reescribir procesar_archivo como segmentar_bloque | Objetivo final, 4-6 sesiones |
| D — Reordenado | Pre-computar firma_lines, mover votos post-firma | **Invalidado**: 12% del corpus tiene votos-antes-de-dispositivo |

### Fase 3 — Hallazgo empírico: votos-antes-de-dispositivo

El PoC D reveló que 669/5702 casos (11.7%) tienen headers de voto/disidencia
ANTES de `firma_end`. Inspección confirmó que es una variante estructural
real del corpus (especialmente tomos 329-332): los votos individuales se
redactan antes del dispositivo colectivo y la firma de la mayoría.

Consecuencia: la premisa "votos siempre post-firma" es falsa. Cualquier
diseño de segmentación debe contemplar ambas variantes.

### Fase 4 — Invalidación de B066

El PoC A encontró 42 matches de regex ampliado (`juez/jueza/doctor`)
restringido a zona post-firma. Diagnóstico de contexto (±5 líneas) reveló:

- **42/42 son citas jurisprudenciales**, no headers de sección
- Patrón típico: `"(Fallos: 328:3312, voto del juez Fayt)."` wrapeado
  por OCR al inicio de línea
- 1 clasificado como "HEADER REAL" por el detector automático era también
  cita (referencia a considerandos de otro voto, no inicio de sección)

Los ~85 "headers reales" del inventario H043 eran en su mayoría citas
clasificadas por inspección superficial. B066 no existe como fue estimado.

### Fase 5 — Descubrimiento y fix de B067 (TECHO_CORTA)

Pregunta derivada: si 12% del corpus tiene votos antes del dispositivo,
¿el techo de `inicio_votos_indiv` está causando regresiones silenciosas?

Diagnóstico: 22 casos con votos detectados + sin_dispositivo. 17 de ellos
tienen dispositivo presente pero bloqueado por el techo (TECHO_CORTA).

**Fix B067:** Tier 3 — si Tier 1+2 con techo no encuentran NADA, repetir
Tier 1 sin techo sobre todo el bloque. Puramente aditivo.

**Validación:**
- PoC full corpus (5702 fallos): 0 regresiones, 17 mejoras
- 16 de 17 recuperan firma (sin_firma -16)
- 2 bonus no anticipados (347_p2160, 348_p728)
- Diagnóstico de contexto (±3 líneas) de los 17 casos: todos legítimos
- Patrones: (a) bloque corto = voto individual completo, (b) fallo largo
  con votos separados antes del dispositivo colectivo

**Métricas post-H044:**
- sin_firma: 422 → 406 (-16)
- Trayectoria: 813 → 782 → 503 → 481 → 449 → 438 → 425 → 422 → **406**

### Hallazgos arquitectónicos para C (futuro)

1. `linea_es_firma_de_juez()` es función pura — puede pre-computarse
   en el loop sin dependencia del dispositivo. firma_end funciona como
   delimitador (92.6% cobertura, p50=7 líneas del dispositivo).
2. El 12% de votos-antes-de-dispositivo invalida cualquier diseño que
   asuma votos siempre post-firma. C debe contemplar ambas variantes.
3. El techo de votos es protector para 5685 casos pero dañino para 17.
   Tier 3 lo resuelve sin romper la protección.

### Scripts generados (en scripts/auditoria/)
- `poc_opcion_d.py` — PoC Opción D (invalidado por votos pre-firma).
- `poc_opcion_a.py` — PoC Opción A (42 matches, 42/42 citas).
- `diag_contexto_ampliado.py` — diagnóstico ±5 líneas de los 42 matches.
- `poc_b067_tier3.py` — PoC B067 Tier 3 (17 mejoras, 0 regresiones).
- `diag_b067_contexto.py` — diagnóstico ±3 líneas de los 17 mejoras.

### Pendiente para próximas sesiones
- B1b (172 truncamientos) y B2 (165 sin apertura) siguen siendo el
  grueso de sin_firma (337/406). Requieren M08 o equivalente.
- C (arquitectura auditor portada al parser) sigue como objetivo a
  largo plazo, informado por los hallazgos empíricos de H044.

# H045 — Visor explorador + diagnóstico sin_firma

**Sesión:** H045
**Fecha:** 2026-05-20
**Objetivo original:** construir un visor Streamlit para explorar el
corpus (Vista 1: Explorador de casos). Objetivo secundario emergente:
diagnóstico de sin_firma a través de exploración visual.
**Resultado:** visor funcional + diagnóstico cuantificado de sin_firma
con causa raíz identificada (B069) + PoC firma independiente v2.

### Fase 1 — Construcción del visor explorador

Visor Streamlit con sidebar de filtros y vista de detalle de caso.
Ubicación: `scripts/explorador/explorador.py`.

**Funcionalidad:**
- Tabla de casos paginada con filtros: tomo (input numérico), página,
  texto libre (carátula + dispositivo + firma + jueces), voting pattern,
  outcome, solo fallos, solo sin_firma.
- Vista de detalle: panel izquierdo (metadatos parseados, votos
  individuales, dispositivo, firma) + panel derecho (bloque fuente .md
  con resaltado por secciones).
- Resaltado con regex del parser: apertura, fecha, considerando,
  dictamen, dispositivo (15+ variantes), firma (post-apertura), voto/
  disidencia, headers de sumario, headers de página.
- Navegación anterior/siguiente dentro del filtro activo.

**Decisiones de diseño:**
- El visor muestra el voting_pattern del CSV (lo que el parser
  determinó), no recomputa nada. Los colores del bloque fuente son
  detección visual independiente.
- Firma solo se resalta post-apertura (evita falso positivo con
  carátulas que contienen guiones largos, e.g. "BFSA –ex Nación–").
- Los regex del visor NO son idénticos a los del parser. Discrepancias
  entre resaltado visual y metadata del CSV = bugs del parser visibles.
- Color de sumario headers: celeste (#5cb8ff) por pedido explícito.

### Fase 2 — Diagnóstico de sin_firma vía exploración

La exploración visual con el visor reveló tres bugs y un hallazgo
arquitectónico mayor:

**B067 — "En virtud de lo expuesto"** no está en DISPOSITIVO_ALT.
Caso 348_p443 (Fernández de Kirchner, recusación). El visor mostró
firma en azul pero metadata dice sin_firma. Validación empírica:
5 hits en tomo 346-2, solo 2 son dispositivos (60% falsos positivos).
Patrón demasiado amplio — pospuesto.

**B068 — Moliné O'Connor — CANCELADO.** El visor mostró 5 hits para
"Moliné": 3 como juez en firma, 2 como parte demandante
(340_p1993, 347_p1673 — juicios post-remoción). Agregar a
JUECES_CONOCIDOS generaría falsos positivos. Cancelado.

**B069 — detectar_fin_real Pista 1 trunca por tokens comunes.**
Diagnóstico a partir de los 7 sin_firma del tomo 346-2: 6/7 tenían
bloques truncados centenares de líneas antes de la firma. Análisis
del CSV mostró tokens causantes: "Fisco" (cortó 411 líneas),
"Fundación" (399), "Banco" (92). Cuantificación vía PoC v2:
201/422 sin_firma (47.6%) tienen motivo `sin_firma_post_fallo`.
**Causa raíz principal de sin_firma.**

**A001 — Firma depende de dispositivo.** El flujo `dispositivo →
firma` hace que si el dispositivo no se detecta, la firma nunca se
busca. El parser YA usa `linea_es_firma_de_juez()` como validación
de candidatos de dispositivo pero no como señal independiente.

### Fase 3 — PoC firma independiente

**v1:** 79 recuperados — incluía falsos positivos de sumarios
(parentéticas como "(Voto de la Dra. Argibay)") y bloques cortos
(firmas de casos adyacentes). Detectado por: "unánime 1 juez" es
incoherente.

**v2 (con guardas):** 43 recuperados, 0 falsos positivos.
Guardas: span mínimo 20 líneas + zona de fallo obligatoria
(requiere apertura, fecha, considerando o "Vistos los autos"
en el bloque).

Desglose de 422 sin_firma:
- 201 sin_firma_post_fallo (B069, truncados)
- 119 sin_zona_fallo
- 59 span < 20
- **43 recuperables** (A001)

### Entregables

1. `scripts/explorador/explorador.py` — visor Streamlit.
2. `scripts/auditoria/poc_firma_independiente_v2.py` — PoC validado.
3. `output/auditoria/poc_firma_independiente.csv` — 43 casos recuperables.
4. DEUDA_TECNICA.md actualizado (B068 cancelado, B069, A001, matriz).

### Camino a seguir

1. **H046: fix B069** — reforzar Pista 1 de detectar_fin_real.
   Impacto potencial: 201 casos. Después re-correr parser y PoC.
2. **H047: A001** — implementar firma independiente sobre lo que
   quede después de B069.
3. Visor Vistas 2-3 (estadísticas, comparador) — cuando haya
   estabilidad en el pipeline.

---


### H046 — Fix B069: detectar_fin_real Pista 1 (2026-05-20)

**Objetivo:** resolver los 406 sin_firma, de los cuales 309 eran
causados por falsos matches de Pista 1 hacia atrás.

**Diagnóstico:**
1. Inventario de los 309 sin_firma con `pista_fin=caratula_siguiente`
   + `status_fin=fin_dentro_bloque`. Extraídos tokens del caso
   siguiente: 36% genéricos (ANSES, Estado, Provincia), 4% nombres
   de orgs (Federación, Partido), 60% apellidos reales que matchean
   en citas y firmas.
2. Inspección visual en `.md` reales (tomos 329-330):
   - 329_p2523: "Carmen" del siguiente matcheó "CARMEN M. ARGIBAY"
     en firma de jueza.
   - 329_p1762: "Banco" matcheó en "Vistos los autos: ...c/ Banco
     Central..." — el nombre del propio caso.
   - 329_p1350: `lfc` en el índice del volumen (último caso del
     archivo), Pista 1 barrió 6512 líneas hacia atrás.
3. Censo completo (censo_b069.py): 169/309 (55%) tenían firma
   detectable entre lfr y lf (contenido perdido). 183/309 (59%)
   perdieron el dispositivo.

**Decisión de fix:**
- Evaluadas 5 opciones: (a) multi-token, (b) largo mínimo mayor,
  (c) validación zona sumario, (d) contra-señal firma, (e) c+d.
- Descartadas tras análisis: el problema no es el token sino la
  dirección de búsqueda. La carátula del siguiente está DESPUÉS de
  lfc, no antes. La búsqueda atrás es inherentemente frágil.
- Fix adoptado: eliminar `buscar_atras` de Pista 1, mantener solo
  `buscar_adelante`. Evaluada variante intermedia (MAX_RETROCESO=20)
  que daba 209 mejoras / 1 regresión / sin_firma=214, pero
  178 sin_firma remanentes vs 4 regresiones no justificaba
  mantener la búsqueda atrás.

**Validación:**
- PoC con pasada completa del parser (poc_b069_v3.py).
- Variante MAX_RETROCESO=20: 209 mejoras, 1 regresión, sf=214.
- Variante sin búsqueda atrás: 277 mejoras, 4 regresiones, sf=148.
- Adoptada variante sin búsqueda atrás por ratio 277:4.
- 4 regresiones aceptadas: 330_p747, 330_p4071, 331_p548, 348_p1519.

**Resultado:**
- sin_firma: 406 → 148 (trayectoria: 813→782→503→481→449→438→425→422→406→148).
- Cobertura firma: 92.9% → 97.4%.
- Votos: 25603 → 26959.

**Pendientes para H047:**
- Investigar las 4 regresiones (330_p747, 330_p4071, 331_p548, 348_p1519).
- A001: firma independiente de dispositivo (43 casos originales, verificar cuántos quedan en los 148).
- Pista 0: marcador INDICE como hard cutoff para últimos casos de cada archivo.
- Commit de H045 (snapshot ya hecho).

## Sesión H046 — 2026-05-20: B069 cerrado (eliminación búsqueda atrás Pista 1)

### H046-01 — B069: búsqueda atrás de Pista 1 causa 47.6% de sin_firma

**Hipótesis (H045):** Pista 1 en `detectar_fin_real()` busca hacia atrás
el primer token de la carátula siguiente. Tokens cortos y comunes en
derecho ("Fisco", "Banco", "Fundación") matchean en citas o texto
argumentativo → corte falso → firma fuera del bloque → sin_firma.

**Fix:** eliminación total de la búsqueda hacia atrás (`buscar_adelante`).
Se evaluaron tres variantes:
- Sin búsqueda atrás: 277 mejoras, 4 regresiones, sf=148.
- MAX_RETROCESO=20: 209 mejoras, 1 regresión, sf=214.
- MAX_RETROCESO=10: intermedia, descartada.

Adoptada variante sin búsqueda atrás por ratio 277:4.

**4 regresiones aceptadas:** 330_p747, 330_p4071, 331_p548, 348_p1519.
Casos donde la búsqueda atrás acertaba; pérdida aceptable vs 277 mejoras.

**Validación:** PoC con pasada completa del parser (poc_b069_v3.py).
Diff explícito contra CSV baseline.

**Resultado:**
- sin_firma: 406 → 148. Cobertura firma: 92.9% → 97.4%.
- Votos: 25603 → 26959.
- Trayectoria: 813→782→503→481→449→438→425→422→406→148.

---

## Sesión H047 — 2026-05-20: A001 cerrado (fallback firma inversa)

### H047-01 — "Así se decide" como variante de dispositivo

**Hipótesis:** agregar "Así se decide" a RE_DISPOSITIVO_VARIANTES podría
resolver sin_firma sin necesidad de firma inversa.

**Resultado:** grep en corpus → 1 solo hit (342_p98). Descartado por
impacto mínimo.

**Lección:** verificar frecuencia en corpus antes de agregar variantes.

---

### H047-02 — A001: fallback firma inversa en procesar_archivo

**Hipótesis:** buscar firma desde el final del bloque hacia atrás
(independiente de dispositivo) recupera sin_firma donde
`por_ello_idx is None` o `collect_firma_lines` falla.

**PoC:** poc_a001_v1.py — 34 recuperados, 0 falsos positivos sobre
los 148 sin_firma post-B069. Todos unanime, todos sin_dispositivo.
Las funciones del PoC usan las constantes de parser.py directamente
(RE_APERTURA, RE_CONSIDERANDO, RE_FECHA_LINEA) — código exacto que
se insertó en producción.

**Guardas:** zona de fallo obligatoria (apertura/fecha/considerando/vistos),
span mínimo 20 líneas, filtro zona post-firma (RE_DATOS_PARTES),
límite de retroceso 80 líneas.

**Validación:** pasada completa del parser + diff_a001.py contra
CSV baseline. 34 mejoras, 0 regresiones, 0 otros cambios.

**Dato notable:** 331_p548 (regresión B069) recuperada por A001.

**Resultado:**
- sin_firma: 148 → 114. Cobertura firma: 97.4% → 98.0%.
- Votos: 26959 → 27098.

---

### H047-03 — A001b: _encontrar_zona_fallo primera apertura

**Hallazgo:** caso 329_p317 — auditor del visor ve la firma pero
buscar_firma_inversa no la encuentra. Causa: el bloque arrastra
residuo del caso siguiente, que incluye su propio "FALLO DE LA
CORTE SUPREMA". `_encontrar_zona_fallo` tomaba la ÚLTIMA apertura
→ zona_fallo queda al final → búsqueda inversa no alcanza la firma
real del caso.

**Fix:** cambiar de ÚLTIMA a PRIMERA apertura. Para fecha/considerando/
vistos: restringir a primera mitad del bloque (evita envenenamiento).
Fallback sin restricción de mitad para bloques cortos.

**Validación:** poc_a001b_v1.py — 1 nuevo recuperado (329_p317),
0 regresiones. Pasada completa del parser confirma sin_firma 114→113.

**Lección:** cuando el bloque incluye inicio del caso siguiente,
los marcadores del caso siguiente envenenan heurísticas que buscan
"el último X". Preferir "el primero" para marcadores del caso actual.

**Resultado:**
- sin_firma: 114 → 113. Votos: 27098 → 27103.

---

### H047-04 — Auditoría visual 80 casos (seed 420)

**Método:** `auditar_fallo.py --random 80 --seed 420` + visor_auditoria.

**Resultado:** 0 sin_firma en la muestra de 80 (coherente: 113/5702 = 2%,
esperado ~1.6 sin_firma en 80 casos random). 0 discrepancias
auditor-parser. Residuo total: 4.67%.

---

### H047-05 — Diagnóstico de los 113 sin_firma residuales

**Desglose por motivo (buscar_firma_inversa):**
- 57 sin_firma_post_fallo: zona de fallo encontrada pero
  `linea_es_firma_de_juez` no matchea. Causa probable: firmas en ALL
  CAPS partidas entre líneas (nombre al final de una línea, apellido
  al inicio de la siguiente — los regex de JUECES_CONOCIDOS requieren
  nombre+apellido juntos).
- 33 sin_zona_fallo: bloques sin apertura, fecha, considerando ni
  vistos. Contenido mayormente editorial o sumario.
- 23 span_corto: bloques de menos de 20 líneas. No son fallos reales
  o son entradas extremadamente breves.

**Estado al cierre H047:**
- sin_firma: 113 / 5702 fallos (2.0%). Cobertura firma: 98.0%.
- Votos: 27103.
- Trayectoria: 813→782→503→481→449→438→425→422→406→148→114→113.

### H048-01 — Inspección de los 113 sin_firma residuales

**Método:** script `inspeccion_113.py` que clasifica los 113 en tres grupos:
- 57 sin_firma_post_fallo (zona de fallo encontrada, firma no matchea)
- 33 sin_zona_fallo (sin apertura/fecha/considerando)
- 23 span_corto (bloques < 20 líneas)

**Hallazgo clave:** clasificador automático de patrones de firma solo
detectó 5/57 (2 firma_partida, 3 juez_no_listado). Los 52 restantes
quedaron como "indeterminado".

---

### H048-02 — Diagnóstico: firma post-corte

**Método:** script `contexto_corte_57.py` que muestra las 20 líneas
posteriores a `linea_fin_real` para cada caso sin_firma_post_fallo.

**Resultado:** 43/57 tienen la firma detectada DESPUÉS del corte.
La firma está en el bloque del caso siguiente, no en el bloque actual.

**Causa raíz confirmada:** `detectar_fin_real` Pista 1 forward encuentra
`primer_token_siguiente` en el texto corriente del caso actual (zona
post-lfc). Tokens comunes como "Nación", "Provincia", "ANSeS" matchean
en el dispositivo o considerando del caso actual, truncando el bloque
antes de la firma.

Ejemplo: 329_p551, token "Nación" matchea en "mercial de la Nación).
Notifíquese." (L20818) — texto del dispositivo — en vez de en la
carátula real "KARINA VERONICA RODRIGUEZ V. NACION ARGENTINA" (L20825).

Los 14 restantes:
- 7 texto continúa (firma > 20 líneas después del corte)
- 5 jueces no listados en JUECES_CONOCIDOS (conjueces)
- 1 remisión a fallo embebido con (*)
- 1 índice (334_p1920, no es fallo real)

---

### H048-03 — B070: validación texto corriente en Pista 1 forward

**Evolución del fix (6 versiones de PoC):**

| Versión | Estrategia | Mejoras | Regresiones | Problema |
|---------|-----------|--------:|------------:|----------|
| v1 | Contra-señal firma | 1 | 195 | Firma siempre entre lfc y carátula |
| v2 | Uppercase ratio > 50% | 51 | 60 | Tomos nuevos usan Title Case |
| v3 | Texto corriente: a+b+c | 43 | 13 | Condición c demasiado agresiva |
| v4 | Solo a+b (sin c) | 30 | 5 | 3 tildes + 1 "c/" + 1 guión editorial |
| v5 | a+b refinados | 29 | 3 | Solo tildes (pre-existente) |
| **v6** | **a+b + strip_accents** | **37** | **0** | **—** |

**Condiciones finales de `_es_texto_corriente()`:**
- (a) Línea empieza con minúscula → texto corriente (excepto "c/" y "s/")
- (b) Línea anterior significativa termina con word-split genuino
  (letra + guión, no puntuación + guión)

**B071 (incluido en v6):** `_strip_accents()` normaliza tildes en el
token y en cada línea antes del regex. "Administración" matchea
"ADMINISTRACION". Resuelve desacople catálogo (con tildes) vs .md
(ALL CAPS sin tildes). 19.4% de los tokens tienen tilde (1126/5819).

---

### H048-04 — Auditoría de las 37 mejoras

**Método:** script `auditar_b070v6.py` — últimas 25 líneas del bloque
extendido con marcadores de firma para cada mejora.

**Resultado:** 33/37 OK (firma con jueces conocidos verificados).
4 warnings: 2 mejoras cuestionables (345_p599, 348_p259: lfr_new <
linea_inicio refinado), 2 reclasificaciones inofensivas (346_p253,
348_p53: jueces=0, sumarios editoriales).

**Observación (329_p2174):** Argibay contada doble — header de voto
"MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY" detectado como firma.
Pre-existente, no del fix.

**Conjueces faltantes detectados:** Pérez Petit, Romano, Petra
Fernández, García Lema, Bertuzzi, Rabbi-Baldi Cabanillas, Botana,
Rivera, Torres, Caballero, Méndez, Montesi, Cossio. → B072.

---

### H048-05 — Resultado final

**Fix aplicado:** `parser.py` — 3 cambios:
1. `import unicodedata`
2. Funciones helper `_strip_accents()` y `_es_texto_corriente()`
3. Pista 1 forward reescrita con loop + validación + normalización

**Resultado:**
- sin_firma: 113 → 76 (trayectoria: ...→113→76).
- Cobertura firma: 98.0% → 98.7%.
- Votos: 27103 → 27303.
- Mejoras: 37. Regresiones: 0.
- Cambios solo lfr: 451 (bloques extendidos/recortados sin cambio de vp).

**Pendientes para próxima sesión:**
- B072: agregar ~13 conjueces a JUECES_CONOCIDOS.
- B073: investigar 345_p599 y 348_p259 (lfr < li refinado).
  37 casos con span < 10 potencialmente afectados por interacción
  detectar_fin_real ↔ refinar_inicio_por_titulo.
- Inspección de los 76 sin_firma restantes (33 sin_zona_fallo +
  23 span_corto + 20 sin_firma_post_fallo residuales).

### H049-01 — B072: 15 conjueces en JUECES_CONOCIDOS

**Método:** grep de los 13 conjueces listados en H048 contra `firma_raw`
del CSV. 8 de 13 aparecen en firma_raw. 5 no aparecen (Bertuzzi, Botana,
Rivera, Torres, Caballero — no agregados). Descubiertos 7 bonus en
firma_raw: Chausovsky, Schiffrin, Aguilar, Pérez Tognola, Corcuera,
Andalaf Casiello, Fernández Gómez. Total: 15 conjueces agregados.

**Hallazgo lateral:** "Roberto Enrique Hornos" en 347_p1673 no matchea
el regex existente (`gustavo\s+m\.?\s*hornos`). Puede ser homónimo o
error OCR. No resuelto.

**Validación:** PoC `poc_b072_diff.py` contra corpus completo.
21 mejoras, 1 regresión aceptada (346_p610 — superposición de bloques
preexistente, firma de caso anterior capturada). sf 76→74, votos
27303→27325.

**Commit:** `bfad045`.

---

### H049-02 — B073: verificación lfr < li (cerrado sin fix)

**Método:** análisis de los 451 `lfr_cambio` de B070 v6 contra
`linea_inicio` del CSV baseline.

**Resultado:**
- 0 casos con lfr_new < linea_inicio.
- 0 cambios de voting_pattern.
- 398 acortaron lfr, 53 extendieron. Mediana -2, media -5.5.
- 18 casos con span < 10 son bloques cortos legítimos.

**Conclusión:** B073 no requiere fix. La inconsistencia lfr < li_refinado
es interna al parser (li refinado no se exporta). Cerrado.

---

### H049-03 — Clasificación de los 74 sin_firma

**Método:** clasificación automática por estructura del bloque +
extracción de texto del corpus para inspección visual.

**Categorías (74 sin_firma post-B072):**
- firma_no_detectada: 35 (tienen apertura + fecha, firma no encontrada).
- sin_zona_fallo: 24 (sin apertura ni fecha).
- bloque_corto: 13 (span < 20).
- bloque_vacío: 4 (span ≤ 4).

**Análisis de residuos (diff catálogo vs parser):**
- 55 sin residuo (lfr == lf, parser usa todo el bloque).
- 19 con residuo, clasificados en 3 grupos:
  - Grupo 1 (3): span=0, parser corta inmediatamente en sumario.
  - Grupo 2 (12): parser corta en sumario_siguiente antes del fallo.
  - Grupo 3 (5): firma del caso anterior confunde al parser.

**Piso estimado de irrecuperables:** ~27 (4 vacíos + 13 cortos + ~10
sin_zona_fallo chicos).

**Artefactos generados:**
- `output/auditoria/H049/sin_firma_76_clasificados.csv`
- `output/auditoria/H049/sin_firma_76_clasificados.md`
- `output/auditoria/H049/sin_firma_texto_completo.md`
- `output/auditoria/H049/sin_firma_bloque_catalogo.md`
- `output/auditoria/H049/sin_firma_bloque_parser.md`

---

### H049-04 — B074: guarda posicional en firma_actual (no committeado)

**Problema:** `detectar_fin_real` fallback `firma_actual` captura firmas
del caso anterior que están en el bloque por superposición de páginas.

**Fix propuesto:** no aceptar firma antes de `RE_APERTURA` del bloque.

**PoC v1 (RE_APERTURA + RE_FECHA_LINEA):** 13 mejoras, 7 regresiones.
RE_FECHA_LINEA matchea "Buenos Aires, [fecha]" en dictámenes.

**PoC v2 (solo RE_APERTURA):** mismas 7 regresiones. Las regresiones
ocurren en casos sin apertura formal donde `primera_apertura=None` y
la guarda no debería activarse. Causa no identificada — posiblemente
el `if` anidado cambia el branching cuando `buscar_atras` encuentra
firma pero la condición falla, permitiendo caer al `buscar_adelante`
que encuentra firma del caso siguiente.

**Decisión:** no commitear. Investigar en H050.

---

### H049-05 — Resultado final

**Committeado:**
- B072: 15 conjueces. sf 76→74, votos 27303→27325.

**Cerrado sin fix:**
- B073: verificado, sin problemas.

**Abierto:**
- B074: guarda posicional, 7 regresiones inexplicadas. Prioridad alta.

**Trayectoria sin_firma:** ...→113→76→74.
**Cobertura firma:** 98.7%.
**Votos:** 27325.

**Pendientes para H050:**
- B074: investigar regresiones (branching del `if` anidado).
- Inspección manual de los 74 sin_firma con el texto extraído.
- Hallazgo Hornos ("Roberto Enrique" vs "Gustavo M.").

### H050-01 — B074: diagnóstico del bug de la PoC H049

**Hallazgo:** la PoC H049 tenía un bug de implementación que desactivaba
`buscar_atras` en TODOS los casos (no solo los que la guarda debía filtrar).
Los 22 casos afectados SIEMPRE extendían lfr. Resultado real de la PoC H049:
3 mejoras genuinas, 6 regresiones explícitas, ~7 regresiones ocultas
(etiquetadas MEJORA_JUECES pero con jueces completamente distintos).

**Mecanismo:** en los 22 bloques afectados, la estructura es idéntica:
residuo del caso anterior (dispositivo + firma + metadata) seguido del
caso actual. `buscar_atras(lfc→li)` pesca firma del caso anterior.

**Estado:** válido. Diagnóstico confirmado con extracción del corpus.

---

### H050-02 — B074v3: guarda RE_APERTURA con límite 40 líneas

**Versión:** guarda posicional por RE_APERTURA en las primeras 40 líneas.
**Resultado:** 10 mejoras, 6 regresiones.
**Problema:** en bloques de 100-500+ líneas, la búsqueda sin límite
encuentra RE_APERTURA del caso SIGUIENTE (contenido en el mismo bloque
por páginas compartidas). Con límite de 40, pierde apertura legítima
cuando hay sumarios largos o dictamen antes.
**Estado:** descartado.

---

### H050-03 — B074v4: reordenar refinar_inicio antes de detectar_fin_real

**Versión:** mover refinar_inicio_por_titulo ANTES de detectar_fin_real.
**Resultado:** 13 mejoras, 15 regresiones (9 nuevas).
**Problema:** refinar_inicio sobre el bloque largo [li, lf] (vs [li, lfr])
produce false matches del token del título en sumarios/citas en las
primeras 50 líneas, moviendo li más allá de la firma correcta.
**Estado:** descartado como fix directo, pero confirmó el concepto.

---

### H050-04 — B074v5: pre-cómputo del título como lower-bound (15 líneas)

**Versión:** pre-computar la posición del token del título en las primeras
15 líneas del bloque. Pasar esa posición como li a detectar_fin_real.
No mover refinar_inicio de lugar.

**Resultado:** 5 mejoras, 2 "regresiones" (ambas correcciones), 3 MEJORA_JUECES.
sin_firma 74→69, votos 27325→27335.

**Análisis de las 2 "regresiones":**
- 343_p1388 (5→3 jueces): los 5 eran del caso anterior. 3 jueces es correcto.
- 347_p1378 (4→0): era un sumario_con_link mal clasificado como fallo.
  El baseline capturaba firma del caso anterior. Ahora el bloque se extiende,
  el detector de sumario_con_link ve la línea "(*) Sentencia... Ver fallo",
  y lo clasifica correctamente con campos analíticos vacíos.

**Commit:** `47f2059`.
**Estado:** cerrado, aplicado y validado.

---

### H050-05 — Hallazgo Hornos

"Roberto Enrique Hornos" en 347_p1673 no matchea el regex existente
(`gustavo\s+m\.?\s*hornos`). Es un conjuez distinto de Gustavo M. Hornos.
Agravado por guión pegado en OCR: `(según su voto)—` sin espacio fusiona
el chunk con Rabbi-Baldi en parse_firma. Impacto: 1 caso, n_jueces 4→5.
**Estado:** anotado en DEUDA_TECNICA, no fixeado.

---

### H050-06 — Reclasificación sin_firma post-B074v5

**69 sin_firma** (vs 74 pre-H050):
- firma_no_detectada: 52 (era 35) — población target para refacción C
- sin_zona_fallo: 3 (era 24) — B074 reclasificó la mayoría
- bloque_corto: 11 (era 13)
- bloque_vacío: 3 (era 4)
- Piso irrecuperables: ~17 (era ~27)

Concentración: 29/52 firma_no_detectada en tomos 329-330 (formato antiguo).

## Sesión 2026-05-21 (H051)

### H051-01 — Diagnóstico de los 55 firma_no_detectada

**Hipótesis:** los 55 casos sin_firma con span≥20 tienen modos de falla
heterogéneos que determinan si corresponde fixes puntuales o refacción
estructural.

**Diagnóstico (poc_diagnostico_firma_h051.py):**
- A_juez_no_en_lista: 26 (candidatas heurísticas, mayormente ruido)
- B_sin_dispositivo_sin_firma: 21 (sin marcadores de fallo)
- D_sin_pistas_firma: 6 (dispositivo ok, firma no alcanzada)
- B_disp_faltante_juez_presente: 2 (juez en bloque, sin dispositivo)

**Hallazgo clave:** la mayoría de los "A" no son firmas reales sino líneas
de sumario editorial con mayúsculas que el scanner confundió. La distribución
real es ~40 bloques editoriales + ~6 fallos reales largos + ~2 de flujo.

**Estado:** válido. Confirmado empíricamente que el problema es clasificación
de bloques, no detección de firma.

---

### H051-02 — Zonificador PoC (Refacción C Paso 1)

**Diseño:** función `zonificar_bloque()` con 3 pasadas:
  - Pasada 0: headers de página (ruido transversal)
  - Pasada 1: anclas estructurales (dictamen, apertura, fecha, considerando,
    vistos, dispositivo, firma, voto/disidencia, epilogo, sumario)
  - Pasada 2: propagación de zonas entre anclas

**Resultados sobre corpus completo (5699 fallos):**
- Concordancia firma: 99.7% (5684/5699)
- Concordancia dispositivo: 99.6% (5677/5699)
- Concordancia dictamen: 41.4% (2361/5699) — esperado, el zonificador
  es más agresivo que el parser en detección de dictamen
- Clasificación: 5613 fallo_completo, 34 sumario_editorial, 15 fallo_sin_firma

**Bugs encontrados y corregidos en PoC:**
- RE_DATOS_PARTES (`^Recurso|...`) capturaba sumarios como epilogo →
  fix: prioridad sumario sobre epilogo + guarda contextual
- KeyError en reporte → fix: mapa de campos a keys del dict

**Estado:** validado. Concordancia suficiente para integración.

---

### H051-03 — Validación catálogo vs corpus (0 fallos perdidos)

**Pregunta:** ¿el catálogo de 5862 entradas es exhaustivo respecto del corpus?

**Método:**
1. Conteo de RE_APERTURA en cada .md vs entradas del catálogo por archivo
2. Clasificación de aperturas: propias (±3 líneas de linea_inicio), citas
   dentro de caso, huérfanas (fuera de todo rango catalogado)

**Resultados:**
- 5855 aperturas totales en corpus
- 235 propias de catálogo
- 5571 citas dentro de caso (sentencias reproducidas textualmente)
- 49 huérfanas → clasificadas como:
  - ~30 gaps de borde (apertura entre linea_fin del anterior y linea_inicio
    del siguiente — el fallo SÍ está catalogado)
  - ~19 índices al final del tomo (falso positivo: "FALLO DE LA CORTE SUPREMA"
    como encabezado en el índice temático)
- **0 fallos genuinamente no catalogados**

**Estado:** válido. Catálogo es exhaustivo. Defendible en metodología de tesis.

---

### H051-04 — Integración zonificador + sumario_editorial (Paso 2)

**Cambio:** `zonificar_bloque()` integrado en `parser.py` como paso previo.
Bloques sin zona cuerpo/dispositivo/firma → `tipo_entrada="sumario_editorial"`.

**Validación PoC (poc_sumario_editorial_h051.py):**
- Check de 6 marcadores (apertura, fecha, considerando, vistos, dispositivo,
  firma): 30 candidatos, 0 regresiones
- Check de 4 marcadores (sin fecha/vistos): 40 candidatos, 40 regresiones →
  descartado (fallos reales sin apertura por page sharing)

**Resultado en producción:**
- 31 casos reclasificados fallo → sumario_editorial (1 extra: 333_p1442)
- 0 regresiones en campos analíticos de los 5831 casos restantes
- sin_firma: 69 → 38
- Votos: 27335 (sin cambio)

**Observación sobre la arquitectura:** el zonificador está integrado pero
solo se usa para la decisión sumario_editorial. El loop monolítico de
procesar_caso sigue intacto para dictamen, dispositivo, firma. La Refacción C
completa requiere que el downstream lea de las zonas (Pasos 3-4, H052+).

**Estado:** aplicado y validado.

---

### H051-05 — Reclasificación sin_firma post-H051

**38 sin_firma** (vs 69 pre-H051). Nuevo desglose:
- firma_no_detectada: ~21 (fallos reales con bloque correcto pero firma no capturada)
- bloque_corto: 11 (span < 20 líneas)
- bloque_vacío: 3 (span ≤ 4)
- otros (sin_zona_fallo, formato atípico): ~3

Los 31 que salieron eran sumarios editoriales que el parser trataba como
fallos. Nunca tuvieron firma.

Concentración remanente: tomos 329-330 (formato antiguo, 2006).

Trayectoria sin_firma: 813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38.

### H052-01 — Fix type mismatch en concordancia dictamen (41.4% → 100%)

**Hallazgo:** la concordancia de dictamen reportada en H051 (41.4%, 2361/5699)
era un artefacto de comparación de tipos. El PoC H051 comparaba
`caso.get("dictamen_presente","") == "1"`, pero parser.py escribe Python
`bool` → el CSV tiene `"True"`/`"False"`, nunca `"1"`. La comparación
siempre daba `False`, y el 41.4% medía simplemente la fracción de casos
sin dictamen.

**Fix:** `str(caso.get("dictamen_presente","")).lower() in ("1","true")`.

**Resultado post-fix:** concordancia dictamen 5671/5671 (100%).
3330 casos con dictamen, 2341 sin dictamen. Cero discrepancias reales
entre zonificador y parser en detección de presencia.

**Estado:** validado. Fase 1 y Fase 2 del Paso 3 eliminadas.

---

### H052-02 — CSV zona-centered: PoC de integración

**Diseño:** `extraer_segmentos()` convierte la lista por-línea del
zonificador en segmentos contiguos con fronteras (linea_ini, linea_fin,
n_lineas, wc). Output: `csjn_casos_zonas_h052.csv`, 152430 segmentos.

**Concordancia wc_dictamen v1 (zonas vs parser):** exacta en 2394/5671.
Los top 5 deltas eran enormes (parser=23118 vs zonas=8). Causa: el bug
del `continue` en el loop `en_dictamen` del parser — cuando el dictamen
no cerraba, todo el bloque quedaba como dictamen.

**Hallazgo en secuencias de zonas:** 486 casos con patrón
`dictamen→dispositivo→apertura`. El primer "dispositivo" era la
conclusión del Procurador ("Por los fundamentos y conclusiones..."),
detectada por `detectar_apertura_dispositivo()` dentro del dictamen.
Falso positivo por vocabulario compartido.

**Estado:** validado, motivó la guarda dictamen (H052-03).

---

### H052-03 — Guarda dictamen en zonificador

**Regla:** dentro de zona dictamen, solo `apertura` ("FALLO DE LA CORTE
SUPREMA") y `fecha` (sin apertura futura) cierran la zona. Los demás
marcadores (dispositivo, firma, epilogo, etc.) se suprimen — son falsos
positivos del vocabulario compartido entre el dictamen del Procurador
y el fallo.

**Jerarquía de marcadores:**
- Fuertes (delimitan macro-zonas): RE_DICT_HDR, RE_APERTURA, RE_VOTO_HDR
- Débiles (solo válidos dentro de su macro-zona): detectar_apertura_dispositivo,
  linea_es_firma_de_juez, RE_CONSIDERANDO, RE_DATOS_PARTES

**Resultado v2:** concordancia wc_dictamen mejoró drásticamente.
Top delta bajó de -23110 a -966. Dictamen wc total: 3.97M → 5.38M
(+1.4M palabras recuperadas de falsos dispositivo/firma). Deltas
remanentes son sistemáticos: headers de página dentro de dictamen
que el parser cuenta y el zonificador excluye correctamente.

**Estado:** validado, integrado en H052-04.

---

### H052-04 — Integración en parser.py (Refacción C Paso 3)

**Cambios en parser.py:**

1. `RE_VISTOS` y `RE_REMISION`: anclas nuevas para el zonificador.
2. `zonificar_bloque()`: retorna `(list[str], list[tuple])` en vez de
   `set(zonas)`. Incluye guarda dictamen y anclas vistos/remisión.
3. Caller de sumario_editorial: usa `set(_zonas_linea)` para el check.
4. `lineas_dictamen`: derivado de `_zonas_linea` con set comprehension.
   Reemplaza el loop `en_dictamen` (18 líneas eliminadas, 3 nuevas).
5. `wc_dictamen`: misma fórmula pero sobre lineas_dictamen corregido.

**Validación (diff pre/post):**
- `n_jueces`: 0 cambios ✓
- `dictamen_presente`: 3 cambios (los 3 nuevos sumario_editorial → 0)
- `wc_dictamen`: 3254 cambios (corrección del bug del continue)
- `wc_mayoria`: 3214 cambios (cascada)
- `wc_considerando`: 895 cambios (cascada)
- `outcome`: 3 cambios (sin_dispositivo → "" por reclasificación)
- `voting_pattern`: 3 cambios (sin_firma → "" por reclasificación)
- `tipo_entrada`: 3 cambios (fallo → sumario_editorial)

**3 nuevos sumario_editorial:** 340_p232, 340_p538, 344_p325. Detectados
por las anclas RE_VISTOS/RE_REMISION que enriquecen el check del
zonificador. Eran falsos fallos sin dispositivo ni firma.

**sin_firma: 38 → 35.**

**Trayectoria sin_firma:**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

**Estado:** aplicado, committeado.

---

### H052-05 — Pendientes

- Generar `csjn_casos_zonas.csv` como tercer artefacto canónico del parser
  (CSV zona-centered con fronteras y wc por segmento).
- Paso 4 (firma zonificada): usar zona firma del zonificador para los 15
  casos donde el zonificador ve firma y el parser no.
- Mejora futura: excluir líneas con zona "dictamen" de la búsqueda de
  fecha del fallo (NOTA en parser.py, _zonas_linea ya disponible).

## Sesión H053 — 2026-05-21

**Objetivo:** integrar CSV zona-centered como tercer output canónico,
mejora defensiva de fecha, diagnóstico de firma zonificada.

**Archivos modificados:** `scripts/pipeline/parser.py`.
**Archivos creados:** `output/parser/csjn_casos_zonas.csv`,
`scripts/auditoria/H053/diag_firma_15.py`,
`scripts/auditoria/H053_fechas_pre.csv`.

---

### H053-A — CSV zona-centered canónico

Integración de `csjn_casos_zonas.csv` como tercer output del parser,
junto a `csjn_casos.csv` y `csjn_casos_votos.csv`.

**Cambios en parser.py:**

1. `extraer_segmentos(zonas, bloque)`: función nueva, movida del PoC
   H052 v2. Extrae segmentos contiguos de zonas con fronteras y wc.
2. `procesar_archivo()`: retorna 4-tupla `(casos, votos, zonas,
   desconocidos)`. Después de `casos_out.append(caso)`, extrae
   segmentos y los acumula en `zonas_out`. Solo para fallos (sumarios
   se saltean).
3. `main()`: acumula `all_zonas`, escribe `csjn_casos_zonas.csv` con
   argumento `--output-zonas` (default: `<output>_zonas.csv`).

**Schema:** `caso_id_canonico, tomo, zona, segmento, linea_ini,
linea_fin, n_lineas, wc`.

**Validación contra PoC H052 v2:**
- Nuevo: 149512 segmentos. PoC: 149536. Delta: -24.
- 3 casos en PoC pero no en nuevo: `340_p232`, `340_p538`, `344_p325`
  — reclasificados como `sumario_editorial` en H052-04. El PoC los
  incluía porque leía un CSV anterior. Correctamente excluidos.
- 1 caso con +3 segmentos (`334_p1033`): diferencia menor en
  reconstrucción de bloque (parser en runtime vs PoC desde CSV).
- 0 regresiones en casos, votos, sin_firma.

**Estado:** integrado, committeado.

---

### H053-C — Mejora fecha del fallo (guarda defensiva)

En el Caso (b) de detección de fecha (sin marcador de apertura), se
excluyen líneas con `_zonas_linea[k] == "dictamen"` de la búsqueda
inversa. Eliminada la NOTA de mejora futura en parser.py.

**Impacto empírico:** 0 fechas cambiadas. La búsqueda inversa (desde
el final del bloque) ya saltaba el dictamen naturalmente porque este
aparece al principio del bloque. La guarda es defensiva contra casos
atípicos donde el dictamen pudiera estar al final.

**Estado:** aplicado, committeado.

---

### H053-B — Diagnóstico firma zonificada (15 discrepantes)

Análisis de los 15 casos donde el zonificador detecta firma pero el
parser reporta `sin_firma`.

**Clasificación:**

- **10 `firma_ok_pero_sin_dispositivo`:** el zonificador detecta
  nombres de jueces en sumarios, epílogos o headers de sumario (e.g.
  "Disidencia de la Dra. Carmen M. Argibay"). No son firmas reales.
  Sin dispositivo, el parser no tiene dónde anclar la detección.
  Irrecuperables con la arquitectura actual.

- **3 falsos positivos del zonificador** (329_p1568, 329_p5151,
  330_p4071): la "firma" está en las primeras 15 líneas del bloque.
  Son headers de sumario tipo "PETRACCHI — HIGHTON DE NOLASCO —
  MAQUEDA" que listan los jueces del fallo. `linea_es_firma_de_juez`
  matchea por formato (mayúsculas + guiones), pero son parte del
  sumario, no firmas del fallo.

- **2 genuinamente complejos** (344_p1102, 347_p1084): fallos largos
  (span 1391 y 1730) con múltiples votos separados. La firma principal
  está mid-fallo (antes del último dispositivo). El parser busca firma
  después del dispositivo. Teóricamente recuperables con un fallback
  por zona firma, pero el ROI es 2 casos sobre 5668.

**Conclusión:** el piso irrecuperable (~17 estimado en el prompt) se
confirma. Un fallback por zona firma rendiría como mucho 35→33.
Se cierra B como diagnóstico sin patch.

**sin_firma remanentes: 35 (sin cambio).**

**Trayectoria sin_firma:**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

---

### H053 — Estado final

- **Corpus:** 5862 casos (5668 fallos + 34 sumario_editorial +
  160 sumario_con_link).
- **Sin firma:** 35 / 5668 fallos (0.6%). Cobertura: 99.4%.
- **Votos:** 27335 filas.
- **Zonas:** 149512 segmentos en `csjn_casos_zonas.csv` (nuevo).
- **Outputs canónicos:** 3 (casos, votos, zonas).
- **Commits:** 3 (H053-A, H053-C, H053-C/fechas_pre).

## Sesión H053 — 2026-05-21

**Objetivo:** integrar CSV zona-centered como tercer output canónico,
mejora defensiva de fecha, diagnóstico de firma zonificada.

**Archivos modificados:** `scripts/pipeline/parser.py`.
**Archivos creados:** `output/parser/csjn_casos_zonas.csv`,
`scripts/auditoria/H053/diag_firma_15.py`,
`scripts/auditoria/H053_fechas_pre.csv`.

---

### H053-A — CSV zona-centered canónico

Integración de `csjn_casos_zonas.csv` como tercer output del parser,
junto a `csjn_casos.csv` y `csjn_casos_votos.csv`.

**Cambios en parser.py:**

1. `extraer_segmentos(zonas, bloque)`: función nueva, movida del PoC
   H052 v2. Extrae segmentos contiguos de zonas con fronteras y wc.
2. `procesar_archivo()`: retorna 4-tupla `(casos, votos, zonas,
   desconocidos)`. Después de `casos_out.append(caso)`, extrae
   segmentos y los acumula en `zonas_out`. Solo para fallos (sumarios
   se saltean).
3. `main()`: acumula `all_zonas`, escribe `csjn_casos_zonas.csv` con
   argumento `--output-zonas` (default: `<output>_zonas.csv`).

**Schema:** `caso_id_canonico, tomo, zona, segmento, linea_ini,
linea_fin, n_lineas, wc`.

**Validación contra PoC H052 v2:**
- Nuevo: 149512 segmentos. PoC: 149536. Delta: -24.
- 3 casos en PoC pero no en nuevo: `340_p232`, `340_p538`, `344_p325`
  — reclasificados como `sumario_editorial` en H052-04. El PoC los
  incluía porque leía un CSV anterior. Correctamente excluidos.
- 1 caso con +3 segmentos (`334_p1033`): diferencia menor en
  reconstrucción de bloque (parser en runtime vs PoC desde CSV).
- 0 regresiones en casos, votos, sin_firma.

**Estado:** integrado, committeado.

---

### H053-C — Mejora fecha del fallo (guarda defensiva)

En el Caso (b) de detección de fecha (sin marcador de apertura), se
excluyen líneas con `_zonas_linea[k] == "dictamen"` de la búsqueda
inversa. Eliminada la NOTA de mejora futura en parser.py.

**Impacto empírico:** 0 fechas cambiadas. La búsqueda inversa (desde
el final del bloque) ya saltaba el dictamen naturalmente porque este
aparece al principio del bloque. La guarda es defensiva contra casos
atípicos donde el dictamen pudiera estar al final.

**Estado:** aplicado, committeado.

---

### H053-B — Diagnóstico firma zonificada (15 discrepantes)

Análisis de los 15 casos donde el zonificador detecta firma pero el
parser reporta `sin_firma`.

**Clasificación:**

- **10 `firma_ok_pero_sin_dispositivo`:** el zonificador detecta
  nombres de jueces en sumarios, epílogos o headers de sumario (e.g.
  "Disidencia de la Dra. Carmen M. Argibay"). No son firmas reales.
  Sin dispositivo, el parser no tiene dónde anclar la detección.
  Irrecuperables con la arquitectura actual.

- **3 falsos positivos del zonificador** (329_p1568, 329_p5151,
  330_p4071): la "firma" está en las primeras 15 líneas del bloque.
  Son headers de sumario tipo "PETRACCHI — HIGHTON DE NOLASCO —
  MAQUEDA" que listan los jueces del fallo. `linea_es_firma_de_juez`
  matchea por formato (mayúsculas + guiones), pero son parte del
  sumario, no firmas del fallo.

- **2 genuinamente complejos** (344_p1102, 347_p1084): fallos largos
  (span 1391 y 1730) con múltiples votos separados. La firma principal
  está mid-fallo (antes del último dispositivo). El parser busca firma
  después del dispositivo. Teóricamente recuperables con un fallback
  por zona firma, pero el ROI es 2 casos sobre 5668.

**Conclusión:** el piso irrecuperable (~17 estimado en el prompt) se
confirma. Un fallback por zona firma rendiría como mucho 35→33.
Se cierra B como diagnóstico sin patch.

**sin_firma remanentes: 35 (sin cambio).**

**Trayectoria sin_firma:**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

---

### H053 — Estado final

- **Corpus:** 5862 casos (5668 fallos + 34 sumario_editorial +
  160 sumario_con_link).
- **Sin firma:** 35 / 5668 fallos (0.6%). Cobertura: 99.4%.
- **Votos:** 27335 filas.
- **Zonas:** 149512 segmentos en `csjn_casos_zonas.csv` (nuevo).
- **Outputs canónicos:** 3 (casos, votos, zonas).
- **Commits:** 3 (H053-A, H053-C, H053-C/fechas_pre).

## Sesión H054 — 2026-05-21

**Objetivo:** análisis exploratorio del corpus con zonas (línea A),
estadísticas descriptivas del corpus (línea B), validación cruzada
votos↔firma (línea C), y diagnóstico de tratamiento de catch_all
para planificación de H055.

---

### H054-B — Estadísticas descriptivas del corpus

Tabla resumen del corpus para Capítulo 4 de la tesis, generada con
PoC `poc_h054_ab.py`. Datos sobre 5668 fallos (excluidos 194 sumarios).

**Hallazgos principales:**

1. **Tres períodos institucionales visibles en los datos.**
   - *Corte post-renovación (tomos 329–334, 2006–2011):* 5–6 firmantes
     promedio, unanimidad 51–64%, dictamen presente en 63–78%.
   - *Transición (tomos 337–339, 2014–2016):* firmantes caen a 3.3,
     unanimidad se dispara a 93% en tomo 339, mediana word_count baja
     a 631 (mínimo histórico).
   - *Estabilización (tomos 340+, 2017+):* ~4 firmantes, unanimidad
     55–62%, con excepciones tardías (tomo 348: 77%, solo 3 firmantes).

2. **Tendencia secular descendente del dictamen:** de ~70% con dictamen
   (tomos 329–337) a ~35% (tomos 345–349). Pero cuando hay dictamen
   en tomos recientes, ocupa mayor proporción del fallo — mediana del
   ratio dictamen/total sube de ~55% (329–334) a ~68–70% (345–349).

3. **Outcomes:** `otro` domina (33.7%), seguido de `hace_lugar` (19%),
   `desestima` (11.5%), `procedente` (10.6%), `competencia` (9.9%).

4. **Voting patterns:** unánime 61.9%, disidencia 19.4%,
   según_su_voto 12.9%, mixed 5.2%, sin_firma 0.6%.

5. **Jueces firmantes por tomo:** visible el quiebre entre el período
   de Corte completa (5.6–5.9 firmantes, tomos 329–334) y la Corte
   reducida post-2015 (3.0–4.4 firmantes, tomos 338+). Tomo 349
   (2026): mediana 3 firmantes.

**Gráficos generados (7):**
g01_unanimidad_por_tomo.png, g02_dictamen_por_tomo.png,
g03_voting_pattern_tomo.png, g04_wc_por_zona_boxplot.png,
g05_wc_mediana_tomo.png, g06_ratio_dictamen_tomo.png,
g07_njueces_tomo.png.

---

### H054-A — Análisis exploratorio con zonas

Primer análisis cuantitativo usando `csjn_casos_zonas.csv` (149512
segmentos, H053).

**A1 — Distribución de largo por zona (agregado por caso):**

| Zona            | Casos | Mediana wc | Media wc |
|-----------------|------:|-----------:|---------:|
| dictamen        | 3327  |      1213  |    1615  |
| cuerpo          | 5599  |       405  |     925  |
| epilogo         | 4476  |        66  |     408  |
| sumario         | 3789  |       233  |     443  |
| dispositivo     | 5609  |        75  |     256  |
| intersticio     | 5152  |        71  |     205  |
| firma           | 5641  |        20  |      93  |
| voto_separado   | 2146  |         9  |      74  |
| apertura        | 5537  |         5  |      13  |

El dictamen es la zona más pesada (mediana 1213 wc). Los votos
separados tienen mediana 9 wc — la mayoría son líneas formales
de cierre, no textos sustantivos.

**A2 — Proporción dictamen/fallo:**
En los 3327 fallos con dictamen (58.7% del total): media 53.2%
del texto total es dictamen, mediana 58.2%. Por tomo, la proporción
sube en los tomos recientes (345–349: mediana 67–70%).

**A3 — Fragmentación:**
Media 26.4 segmentos por caso, mediana 20. Los fallos `mixed` son
los más fragmentados (media 62.3, mediana 48) vs unánimes (media
18.6, mediana 14). Correlación clara entre complejidad del voting
pattern y fragmentación.

**A4 — Votos separados:**
37.9% de los fallos tiene algún segmento `voto_separado`. Proporción
wc_votos/total: media 1.9%, mediana 0.5%.

**A5 — Largo ↔ voting pattern:**
Los fallos `mixed` son los más largos (mediana 3604 wc), seguidos
de `segun_su_voto` (2128), `disidencia` (1448), `unanime` (752).
Correlación clara entre división del tribunal y extensión del fallo.

---

### H054-C — Validación cruzada votos↔firma

Cruce de `n_jueces` (de `csjn_casos.csv`) con `count(*)` por caso
(de `csjn_casos_votos.csv`).

**Resultado: 0 discrepancias** sobre 5668 fallos. El pipeline es
internamente consistente entre los dos CSV canónicos.

B065 (validación firma↔votos) queda parcialmente cubierto por este
resultado: la dimensión n_jueces↔n_votos está validada. La dimensión
calificador↔bloque_voto (si un juez firmó "en disidencia" pero no
hay bloque de disidencia) sigue pendiente.

---

### H054-D — Diagnóstico de catch_all e intersticio

Análisis cruzado del intersticio inicial (zonificador) con la lógica
de `catch_all_inicio` (auditor/visor) para planificar H055.

**Hallazgo cuantitativo (zonas):**

- 4830 / 5668 fallos (85.2%) arrancan con un segmento `intersticio`
  como primera zona no-header_pagina.
- Mediana del intersticio inicial: 63 palabras. Media: 88. Max: 420.
- Total acumulado: 425429 palabras (2.41% del corpus total).
- El intersticio total (incluyendo mid-fallo) suma 1055756 wc. El
  primer segmento explica el 40% del total.

**Transición después del intersticio inicial:**

| Siguiente zona   | Casos |     % |
|------------------|------:|------:|
| sumario          | 2865  | 59.3% |
| apertura         | 1159  | 24.0% |
| dictamen         |  478  |  9.9% |
| dispositivo      |  165  |  3.4% |
| firma            |  125  |  2.6% |
| cuerpo           |   38  |  0.8% |

El 93.2% de los intersticios iniciales transicionan a sumario,
apertura o dictamen — material del caso actual. El intersticio previo
es residuo del caso anterior (B045 manifestación B).

Los 165 intersticio→dispositivo y 125 intersticio→firma son
sospechosos: posible detección faltante de apertura/considerando.
Candidatos a auditoría puntual en sesiones futuras.

**Hallazgo del auditor/visor:**

El visor (`visor_auditoria.py`, líneas 313–325) ya implementa la
exclusión de `catch_all_inicio`: identifica el catch_all con la
`linea_ini` más baja que termina antes del primer span semántico, y
lo excluye del render por default (`EXCLUIDOS_DEFAULT`). El auditor
(`auditar_fallo.py`, líneas 112–416) complementa con el
`borde_inferior`: clasifica cada línea del gap entre `linea_fin_real`
y `linea_inicio` del próximo caso como `firma_arrastrada`,
`apertura_proximo_caso`, `voto_disidencia_individual`,
`no_clasificable`, etc.

**Conclusión:** la lógica de exclusión de residuo ya está probada
visualmente. Lo que falta es portarla al parser como dato
estructural (nueva zona `residuo_caso_anterior` que se excluye del
cálculo de `word_count`).

**Matriz de decisión (3 caminos):**

| Criterio             | A (fix raíz -1)  | B (zona residuo)  | C (B luego A)    |
|----------------------|-------------------|-------------------|------------------|
| Impacto en wc        | alto              | alto              | máximo           |
| Riesgo de regresión  | alto              | mínimo            | medio            |
| Complejidad          | media             | baja (~20 líneas) | media (2 pasos)  |
| Elegancia            | máxima            | buena             | máxima           |
| Escalabilidad        | alta              | buena             | alta             |
| Precedente validado  | no                | sí (visor)        | sí               |
| Tiempo estimado      | 1–2 sesiones      | ½ sesión          | 2–3 sesiones     |

**Decisión:** Camino C (secuencial). H055 aplica B (zona residuo,
seguro y rápido). H056+ evalúa A (fix raíz) usando zonas como
detector de regresión. Solo si el ROI lo justifica post-tesis.

---

### H054 — Estado final

- **Corpus:** sin cambios (5862 casos, 5668 fallos, 35 sin_firma).
- **Outputs canónicos:** sin cambios (3 CSV).
- **Commits:** 0 (sesión de análisis y diagnóstico, sin cambios al pipeline).
- **Gráficos:** 7 generados para evaluación de inclusión en Capítulo 4.
- **PoC:** `poc_h054_ab.py` (estadísticas descriptivas + zonas).
- **Deuda técnica:** B065 parcialmente validado (n_jueces↔n_votos: 0
  discrepancias). B061 desvinculado de B066 (ya invalidado).
- **Planificación H055:** camino C definido (zona residuo → fix raíz).

**Trayectoria sin_firma (sin cambio):**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

---

## Sesión 2026-05-21 (H055)

### H055-A — Zona residuo_caso_anterior en parser.py

Implementación del Camino C, Paso 1 (planificado en H054-D): nueva
zona `residuo_caso_anterior` en el zonificador del parser.

**Cambio 1 — Pasada 3 en `zonificar_bloque()`:** post-pass después
de la propagación de zonas (Pasada 2). Recorre las líneas desde el
inicio del bloque y reclasifica todo `intersticio` que aparezca antes
de la primera zona semántica (`sumario`, `dictamen`, `apertura`,
`cuerpo`, `dispositivo`, `firma`, `voto_separado`) como
`residuo_caso_anterior`. Los `header_pagina` intercalados no se
tocan. Lógica equivalente al `catch_all_inicio` del visor
(líneas 313-325), portada al parser como dato estructural.

**Cambio 2 — Exclusión del word_count:** en `procesar_archivo()`,
se deriva `lineas_residuo` de `_zonas_linea` (misma lógica que
`lineas_dictamen`) y se excluye de `lineas_mayoria`. Impacto:
`word_count` y `wc_mayoria` bajan; `wc_votos` y `wc_dictamen` no
cambian.

**Resultados:**

| Métrica                        |     Pre |      Post |     Delta |
|--------------------------------|--------:|----------:|----------:|
| Casos totales                  |   5862  |     5862  |         0 |
| Fallos                         |   5668  |     5668  |         0 |
| Votos                          |  27335  |    27335  |         0 |
| Segmentos zonas                | 149512  |   149512  |         0 |
| sin_firma                      |     35  |       35  |         0 |
| WC total corpus (fallos)       | 12327080| 11271324  | −1055756  |
| Fallos con residuo reclasif.   |      —  |     5152  |     (91%) |
| Segmentos residuo_caso_ant.    |      —  |     7677  |         — |

El PoC (`poc_h055_residuo.py`) predecía 446,981 wc de impacto porque
solo contaba el primer segmento de intersticio por caso. El impacto
real es 1,055,756 porque el parser reclasifica **todos** los
segmentos de intersticio antes de la primera zona semántica,
incluyendo los separados por `header_pagina` (promedio 1.49 segmentos
por caso). Esto coincide con el total de intersticio pre-semántico
reportado en H054-D: "El intersticio total (incluyendo mid-fallo)
suma 1055756 wc. El primer segmento explica el 40% del total."

Sanity checks: 0 casos con WC negativo post-reclasificación. 0
regresiones en conteos de casos, votos, segmentos, sin_firma.

**Observación sobre los edge cases (de la PoC):**

310 casos (171 → dispositivo, 139 → firma) tienen el residuo
seguido directamente por dispositivo o firma sin zonas intermedias.
Son bugs puntuales del zonificador (detección faltante de
apertura/considerando) documentados como S2 en el prompt H055.
La reclasificación como residuo es correcta: el material antes del
dispositivo/firma sigue siendo del caso anterior. Los 1246 casos
residuo → intersticio tienen un segundo gap (blancos/headers) entre
el residuo y la zona semántica.

**Trayectoria sin_firma (sin cambio):**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

### H055-B — Fix Causa en RE_DATOS_PARTES (falsos epilogos)

Diagnóstico de marcadores de epílogo reveló que `^Causa\b` en
`RE_DATOS_PARTES` generaba falsos positivos masivos: la palabra
"causa" al inicio de línea en texto argumentativo disparaba zona
`epilogo` dentro de votos separados y cuerpo del fallo. Caso
extremo: 332_p2559 tenía 5,999 wc de epilogo que eran considerandos
completos sobre "real malicia".

**Fix:** `Causa` → `Causa\s*:` (requiere dos puntos). El patrón
editorial legítimo es "Causa: Smith c/ Jones" o "Causa N°...".

**Resultados:**

| Métrica               |       Pre |      Post |     Delta |
|-----------------------|----------:|----------:|----------:|
| Segmentos zonas       |    149512 |    147952 |    −1560  |
| Epilogo total (wc)    | 1,826,369 | 1,213,887 | −612,482  |
| Casos con epilogo     |      4476 |      4375 |     −101  |
| Casos afectados       |         — |       871 |         — |

0 regresiones. Conteos de casos, votos, sin_firma idénticos.

**Hallazgo secundario (Ministerio):** 89 segmentos con falso
epilogo por `^Ministerio\b` que matchea "Ministerio de Economía"
en texto argumentativo. No fixeado: requiere análisis más fino
(algunos son carátulas legítimas en epilogo). Candidato H056.

### H055 — Estado final

- **Corpus:** 5862 casos (5668 fallos + 34 sumario_editorial + 160
  sumario_con_link). Sin cambios en conteos.
- **Sin firma:** 35/5668 (0.6%). Sin cambios.
- **Votos:** 27335. Sin cambios.
- **Zonas:** 147952 segmentos (era 149512 pre-fix Causa). Nueva zona
  `residuo_caso_anterior` (7677 segmentos, 1,055,756 wc).
- **word_count:** corregido, excluye residuo del caso anterior.
  Total corpus fallos baja de 12,327,080 a 11,271,324 (−8.6%).
- **Epilogo:** fix `Causa` → `Causa\s*:` en `RE_DATOS_PARTES` elimina
  612,482 wc de falsos epilogos en 871 casos (33% del epilogo total
  era body text mal clasificado). Epilogo: 1,826K → 1,214K wc.
- **Commits:** 3 (residuo_caso_anterior, fix Causa, PoCs+docs).
- **PoCs:** `poc_h055_residuo.py`, `diagnostico_epilogo.py`,
  `poc_causa_fix.py`, `extraer_epilogos_muestra.py`.
- **Explorador v4:** `scripts/explorador/exploradorv4.py` con zonas
  del parser, toggles por zona, colores diferenciados.

**Trayectoria sin_firma (sin cambio):**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

## H056 — Auditoría de regresiones + fixes de zonificación

Sesión del 21/05/2026. Foco: auditoría post-H055, fixes de
zonificación (residuo falso positivo, Ministerio falso positivo),
explorador v4.1.

### H056-L0 — Auditoría de regresiones silenciosas (H051-H055)

Script `auditoria_l0_regresiones.py` cruzó `csjn_casos.csv` pre-H055
(commit `141f1a7`) vs post-H055 en 5 secciones:

| Sección | Hallazgo | Acción |
|---------|----------|--------|
| S1 (112 delta WC >50%) | 37 son FP de residuo, resto genuino | Fix Pasada 3b |
| S2 (218 WC<100) | ~194 sumario_con_link (0→0), resto subconjunto S1 | Cubierto por 3b |
| S3 (101 epilogo perdido) | Fix Causa correcto, epilogos falsos → cuerpo | Ninguna |
| S4 (sin_firma) | 0 regresiones | Ninguna |
| S5 (tomos) | Deltas negativos uniformes, esperables | Ninguna |

### H056-P3b — Pasada 3b: revertir residuo falso positivo

**Problema:** Pasada 3 (H055-A) reclasificaba TODO intersticio
pre-semántico como `residuo_caso_anterior`. En 37 fallos per curiam
sin apertura detectada, esto enterraba el cuerpo argumentativo entero
en residuo. Estructura típica: `residuo → dispositivo → firma`.

**Fix:** Pasada 3b en `zonificar_bloque()`, inmediatamente después de
Pasada 3. Si el bloque no tiene ninguna zona en
`{apertura, cuerpo, dictamen, sumario}`, revierte
`residuo_caso_anterior` → `cuerpo`.

**Validación:** 5/5 top cases verificados en explorador (T337 p822,
T331 p1679, T333 p2261, T333 p311, T334 p53). word_count restaurado
al valor original en los 37 casos. 0 regresiones. 24,582 wc
recuperados. 5115 casos con residuo genuino intactos.

### H056-L1 — Explorador v4.1

Mejoras al explorador para revisión masiva de zonas:

- **Indicadores de outliers en tabla:** columnas `Epi` (wc epilogo),
  `Res` (wc residuo), flag `⚠` con `E` (epilogo >500 wc) y `R`
  (residuo >300 wc).
- **Filtros de outliers en sidebar:** checkboxes
  `⚠ Epilogo > 500 wc` y `⚠ Residuo > 300 wc`.
- **Presets de zona:** botones `📎 Epilogo`, `🗑️ Residuo`,
  `✒️ Firma` que setean toggles de un golpe para inspección rápida.

### H056-L2 — Remover Ministerio de RE_DATOS_PARTES

**Problema:** `^Ministerio\b` en `RE_DATOS_PARTES` matcheaba tanto
marcadores editoriales legítimos ("Ministerio Público: Dra. Monti")
como texto argumentativo ("Ministerio de Economía y Producción
afecten...").

**Diagnóstico:** `diagnostico_ministerio.py` encontró 293 hits de
`^Ministerio` en zonas epilogo. ~100 editoriales (siempre precedidos
por otros marcadores como `Recurso`, `Profesionales`, `Nombre del`),
~80 índices de tomo, ~110 body text falso positivo.

**Fix:** remover `Ministerio` de `RE_DATOS_PARTES`. Los epilogos
legítimos no se pierden porque ya están abiertos por marcadores
previos. Resultado: -171 segmentos (147952→147781). 0 regresiones.

### H056-L3 — Diagnóstico arrastre caso siguiente (NO FIXEADO)

`diagnostico_arrastre.py` detectó 270 casos con carátula ALL CAPS del
caso siguiente al final del epilogo. Impacto total: 1,312 wc. Máximo
por caso: 23 wc (3 líneas). Decisión: no fixear, es cosmético y el
epilogo ya está excluido de `wc_mayoria`. Además, B076 (refactor de
Pasada 1) podría alterar los límites de zona.

### H056 — Hallazgo: B076 (firma espuria en sumarios)

Al inspeccionar `329_p94` en el explorador, se detectó que la
detección de firma corre globalmente sobre todo el bloque sin
respetar zonas de sumario. Líneas tipo `(Voto del Dr. Juan Carlos
Maqueda).` dentro de sumarios editoriales disparan `firma_linea` y
fragmentan el sumario en 17 segmentos intercalados con 12 segmentos
de firma espuria.

**Causa raíz:** Pasada 1 detecta todas las anclas (firma, epilogo,
sumario) globalmente. La zonificación debería sectorizar: primero
sumarios, después firma/epilogo solo fuera de sumarios.

Registrado como B076. Prioridad alta para H057.

### H056 — Estado final

- **Corpus:** 5862 casos. Sin cambios en conteos.
- **Sin firma:** 35/5668 (0.6%). Sin cambios.
- **Votos:** 27335. Sin cambios.
- **Zonas:** 147781 segmentos (era 147952 post-H055, -171 por fix
  Ministerio).
- **word_count:** 37 per curiam recuperados (+24,582 wc) por
  Pasada 3b.
- **Epilogo:** fix Ministerio elimina 171 segmentos de epilogo falso.
- **Explorador:** v4.1 con outliers, filtros y presets de zona.
- **Commits:** 4 (pre-patch snapshot, Pasada 3b, explorador v4.1,
  fix Ministerio).
- **PoCs/diagnósticos:** `auditoria_l0_regresiones.py`,
  `muestreo_l0.py`, `poc_falso_positivo_residuo.py`,
  `diagnostico_ministerio.py`, `diagnostico_arrastre.py`.

**Trayectoria sin_firma (sin cambio):**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35.

## Sesión 2026-05-22 (H058)

### H058-01 — B077: las secciones editoriales son la estructura más regular del corpus

**Hipótesis:** los marcadores de secciones editoriales (acordadas,
índices por partes, índices por materias, discursos) al final de
cada archivo .md son suficientemente consistentes para detectarlos
con regex y usarlos como señal de corte en `detectar_fin_real`.

**Diagnóstico:** PoC contra 3 archivos individuales (330.4, 342-1,
342-2) + corpus completo (46 archivos). Tres variantes de header
de acordadas detectadas:
- `A C O R D A D A S  Y  R E S O L U C I O N E S` (tomo 330, espaciado)
- `ACORDADAS Y RESOLUCIONES` (tomo 342, normal)
- `ACORDADAS` / `Acordadas` (standalone, en TOCs e índices)

0 falsos positivos de la regex compuesta (`RE_EDITORIAL_ANY`) contra
zona de fallos en los 46 archivos — con una excepción crítica
descubierta en producción (ver H058-02).

**Estado:** válido. Las secciones editoriales son detectables con
alta confianza.

---

### H058-02 — `ACORDADAS` standalone es FP en sumarios temáticos

**Hallazgo en producción:** el primer run del patch generó regresión
en sin_firma (34→74). Diagnóstico: no era el Bloque 3 (zonificador)
como primera hipótesis — era el Bloque 2 (`detectar_fin_real`).
`ACORDADAS\s*$` matcheaba en sumarios de fallos que tratan sobre
acordadas (e.g. 339_p933, cuyo sumario abre con "ACORDADAS /
Corresponde declarar inadmisible..."). El corte eliminaba todo el
contenido del caso (wc=0).

**Fix:** sacar `ACORDADAS\s*$` de `RE_EDITORIAL_ANY` (usada en
`detectar_fin_real`). Mantenerla en `RE_EDITORIAL_ACORDADA` (usada
solo en `extraer_secciones_editoriales`, que corre post-último-caso
donde no hay FP).

**Estado:** válido y corregido. Lección: los keywords temáticos del
sumario reproducen exactamente los marcadores editoriales. Testear
siempre con corpus completo antes de patchear, no solo con archivos
individuales.

---

### H058-03 — Bloque 3 (zonas editoriales en zonificador) causa regresión masiva

**Hipótesis:** agregar detección de zonas editoriales en Pasada 1
del zonificador (`_en_editorial` irreversible, suprime todos los
anclas no-editoriales) sería un safety net por si contenido
editorial queda dentro de un bloque de caso.

**Resultado:** regresión sin_firma 34→74 (+40 casos). La causa:
`_en_editorial` se activaba dentro de casos normales cuando una
línea matcheaba un marcador editorial (e.g. "ACORDADAS" en sumario),
suprimiendo toda detección posterior (firma, dispositivo, votos).

**Fix:** revertir Bloque 3 completo. No es necesario como safety
net porque el corte en `detectar_fin_real` (Bloque 2) ya evita que
el contenido editorial entre en bloques de caso.

**Estado:** invalidado. Si algún día se reimplementa, requiere guard
posicional: solo activar `_en_editorial` después de la última firma
detectada del bloque.

---

### H058-04 — Impacto colateral: -40 sin_dispositivo

**Observación:** sin_dispositivo bajó de 97 a 57. Blank
voting_pattern subió de 158 a 195.

**Causa:** casos que absorbían contenido editorial tenían señales
falsas de dispositivo ("Por ello" en texto de acordadas/índices
dentro del bloque inflado). Al cortar el bloque antes del contenido
editorial, esas señales falsas desaparecen. Los casos pasan de
sin_dispositivo a blank (sin contenido procesable o
`fallo_cruza_archivos`).

**Estado:** efecto colateral positivo, no investigado caso por caso.

---

### H058-05 — Diseño del 4to CSV canónico

**Decisión:** crear `csjn_casos_editorial.csv` como 4to output
canónico. Estructura nivel-tomo (no nivel-caso): cada fila es una
sección editorial con columnas `tomo, source_file, seccion,
linea_ini, linea_fin, n_lineas, wc`.

Tres tipos de sección: `acordada`, `indice`, `discurso`.

Implementado en `extraer_secciones_editoriales()`, función
independiente que no usa ninguna lógica del parser de fallos (no
llama RE_APERTURA, no busca firma, no usa zonificador). Solo
escanea marcadores editoriales en el tail post-último-caso de cada
archivo.

**Resultado:** 182 secciones editoriales en 46 archivos.

---

### H058 — Estado final

- **Corpus:** 5862 casos. Sin cambios en conteos.
- **Sin firma:** 34/5668 (0.6%). Sin cambios.
- **Votos:** 27336 (+1 vs H057). Caso recupera voto al cortarse
  correctamente.
- **Zonas:** 141970 segmentos (era 142615 post-H057, -645 por
  contenido editorial removido de bloques de caso).
- **Editorial:** 182 secciones en 46 archivos. Nuevo output
  canónico `csjn_casos_editorial.csv`.
- **sin_dispositivo:** 97→57 (-40, FP eliminados).
- **Commits:** 1 (snapshot pre-H058) + 1 pendiente (fix final).
- **PoCs/diagnósticos:** `poc_b077_completo.py`,
  `poc_b077.py` (corpus), `patch_explorador_editorial.py`,
  `diag_b077.py`, `diag_b077b.py`.

**Trayectoria sin_firma (sin cambio):**
813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35→34.

**Outputs canónicos (4):**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27336 filas.
- `output/parser/csjn_casos_zonas.csv` — 141970 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 182 secciones.

---

## Sesión 2026-05-23 (H059)

### H059-01 — Auditoría sin_dispositivo

**Objetivo:** verificar que los 57 `sin_dispositivo` actuales son
legítimos. El prompt planteaba diff 97→57, pero el baseline de 97
no se encontró en ningún CSV del historial de git (todos los commits
desde H051 muestran 57-58). El 97 fue probablemente un run
intermedio de H058 no commiteado.

**Método:** auditoría directa de los 57 sin_dispositivo.

**Resultado:**
- **31 headnote/sumario:** no arrancan con "Considerando:". Son
  secciones de sumario temático o fragmentos sueltos. Legítimos.
- **26 fallo real:** arrancan con "Considerando:" pero se cortan
  antes del dispositivo. Todos con
  `status_fin=fin_extendido_pag_compartida` +
  `pista_fin=caratula_siguiente`. Genuinamente truncados.
- **1 caso recuperable:** `331_p1013` (wc=397). Tiene "Por ello,
  se declara admisible" inline (mid-paragraph), no capturado por
  `detectar_apertura_dispositivo` que usa `.match()` (inicio de
  línea). No prioritario — fix posible como fallback mid-line
  para casos sin_dispositivo.

**Conclusión:** 56/57 legítimos. No requiere acción.

### H059-02 — Fix editorial: acordada eliminada como tipo

**Problema:** `csjn_casos_editorial.csv` tenía 67 secciones
clasificadas como `acordada` que eran todas FP — subsecciones
del índice que listaban acordadas del tomo bajo headers
"ACORDADAS", "A C O R D A D A S", "ACORDADAS Y RESOLUCIONES".

**Fix aplicado en dos pasos:**

1. Sacar rama `ACORDADAS\s*$` de `RE_EDITORIAL_ACORDADA` (la más
   agresiva, standalone). Resultado: 67→24 acordadas.

2. Remap completo: `_tipo_zona_editorial()` ahora devuelve
   `"indice"` cuando matchea `RE_EDITORIAL_ACORDADA` en vez de
   `"acordada"`. Las secciones se fusionan con los índices
   adyacentes porque `nueva_zona == zona_activa` no dispara
   cambio. Resultado: 24→0 acordadas.

**Impacto:** editorial 182→53 secciones (49 indice, 4 discurso,
0 acordada). 0 regresiones en casos, votos, zonas, sin_firma.

### H059-03 — Diagnóstico: ¿parser editorial separado?

**Observación:** los regex de clasificación editorial
(`ACORDADAS`, `INDICE`, `POR MATERIAS`) matchean texto legítimo
dentro de fallos. La Capa 1 (corte del último caso) no genera FP
porque busca en rango acotado, pero la Capa 2 (inventario editorial)
es frágil. El fix de H059 fue un parche de remap, no una solución
arquitectural.

**Propuesta para H060:** evaluar `parser_editorial.py` como módulo
separado. La separación de dominio (caso vs. editorial) antes de
parsear elimina la necesidad de guards anti-FP. Permite parsear
la estructura interna de los índices (case_name, descriptores
temáticos, legislación citada), acordadas (número, fecha, texto),
y discursos. Escalable para el doctorado (tomos nuevos).

**Decisiones pendientes:** módulo separado vs. refactorización
interna; subtipos de índice ahora vs. después; outputs (1 CSV
expandido vs. múltiples CSVs); manejo de regex compartidos con
`detectar_fin_real`.

Prompt H060 preparado con análisis completo y decisiones a tomar.

### H059 — Estado final

- **Corpus:** 5862 casos. Sin cambios en conteos.
- **Sin firma:** 34/5668 (0.6%). Sin cambios.
- **Votos:** 27336. Sin cambios.
- **Zonas:** 141970 segmentos. Sin cambios.
- **Editorial:** 53 secciones (49 indice, 4 discurso, 0 acordada).
  Era 182 (111 indice, 67 acordada, 4 discurso).
- **sin_dispositivo:** 57. Sin cambios (56 legítimos + 1 recuperable).
- **Commits:** 1 snapshot pre-H059 + 1 fix editorial + 1 docs.

**Outputs canónicos (4):**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27336 filas.
- `output/parser/csjn_casos_zonas.csv` — 141970 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 53 secciones.

## H060 — Parser editorial: PoC de subtipos (2026-05-23)

**Objetivo:** Evaluar separación de detección editorial en módulo propio con clasificación por subtipos.

**Inspección de datos:**
- Inventario de títulos editoriales: separación título/header nítida por frecuencia.
- Mapa estructural por archivo: Era 1 (329–334) con editorial completa (partes, materias, legislación, general); Era 2 (337–349) simplificada (partes + general).
- INDICE GENERAL presente en los 46 archivos. Era 1 con TOC estructurado (entries con puntos); Era 2 con TOC degradado (solo números).
- 330.4 anomalía: único archivo con índice acumulativo post-TOC (12K líneas).

**PoC validada (`poc_subtipos_editorial.py`):**
- 135 secciones (de 53 genéricas): 45 indice_partes, 18 indice_materias, 20 indice_legislacion, 46 indice_general, 5 acordadas, 1 discurso. 0 desconocido.
- Detección por títulos-mojón + openers (incluye `A C O R D A D A S` espaciado por OCR).
- Truncado de INDICE GENERAL por puntos trailing (`\.{4,}\s*$`): última entry TOC + su página = fin. Sin puntos (Era 2) → no trunca. Descarta boilerplate (HOJA COMPLEMENTARIA, notas de imprenta) y acumulativo de 330.4.
- 329.4 conserva entry de 6 puntos (Jurado de Enjuiciamiento). Artefactos OCR de 330.4 (4–5 puntos en medio de texto) excluidos por el anclaje `\s*$`.

**Decisiones:**
- HOJA COMPLEMENTARIA descartada como marcador (aparece en el cuerpo de fallos).
- Procesamiento per-archivo: índices acumulativos cross-volumen se descartan por consistencia.
- Regla REE fijada en memoria: Robusto, Escalable, Elegante. Verificar con datos, no asumir.

**Scripts creados:** `scripts/auditoria/H060/` — poc_subtipos_editorial.py, inventario_titulos_editorial.py, mapa_estructura_editorial.py, ver_final_indice_general.py, ver_dots_indice_general.py, check_ruido.py, check_330_4_transicion.py, check_paginas_editorial.py, check_duplicados_editorial.py, inspeccionar_editorial.py.

**Pendiente (H061):** Integrar en `parser_editorial.py`, migrar desde `parser.py`, actualizar CSV con columna subtipo, commit.

## H061 — Integración de parser_editorial.py + regeneración del catálogo (2026-05-23)

**Objetivo:** Integrar la PoC de subtipos editoriales (H060) en el pipeline productivo, explorar parseo de entries del índice de partes para crosscheck y búsqueda futura.

### H061-01 — Módulo parser_editorial.py

Nuevo módulo `scripts/pipeline/parser_editorial.py` con función
`clasificar_editorial()`. Reemplaza `extraer_secciones_editoriales()`
de parser.py.

**Cambios en parser.py (3051 → 2940 líneas, −111):**
- Import: `from parser_editorial import clasificar_editorial`
- Eliminados: `RE_EDITORIAL_ACORDADA`, `RE_EDITORIAL_DISCURSO`,
  `RE_EDITORIAL_INDICE`, `_tipo_zona_editorial()`,
  `extraer_secciones_editoriales()`
- Retenidos: `RE_EDITORIAL_ANY`, `_es_marcador_editorial()` (Pista 4
  de `detectar_fin_real` — intocable)
- Limpieza: `lineas_editorial` (dead code, siempre set vacío) eliminado
  de 4 ubicaciones. El zonificador nunca produce zonas "acordada"/
  "indice"/"discurso" — Pista 4 corta el bloque antes del editorial.
- CSV editorial: columna `seccion` → `subtipo`.

**Validación:** 0 cambios en casos (5862), votos (27336), zonas
(141970). Editorial 53 → 135 secciones con subtipos. 0 desconocido.

### H061-02 — Exploración: parseo de entries de indice_partes

Se escribió `parsear_indice_partes()` para extraer entries
individuales del índice de nombres (case_name + páginas) y cruzar
contra `csjn_casos.csv`.

**Resultados del crosscheck:**
- 11,408 entries parseadas con página (45 secciones).
- 0 MISS (todo lo que el índice lista, el parser lo tiene).
- 450 EXTRA (casos en parser no listados en el índice).
- 37 incompletas (basura de frontera: HOJA COMPLEMENTARIA, entries
  de INDICE GENERAL, contenido de la sección siguiente).
- 4,245 entries duplicadas cross-archivo (índices tomo-level repetidos
  en cada archivo del mismo tomo).

**Hallazgo clave:** `parsear_indice_partes` es redundante con
`construir_catalogo.py`, que tiene un parser más robusto:
- Join-then-split por anclas (`RE_ANCLA.finditer`) vs acumulación
  línea por línea.
- Maneja NBSP (`\xa0`), separador "y" (`ps. 1316 y 1334`), entries
  concatenadas mid-line, extensión de inicio para tomos modernos.
- Fuente canónica: `output/catalogo/catalogo.csv`.

**Decisión:** eliminar `parsear_indice_partes` del módulo. No duplicar
lógica que ya existe y está más madura.

### H061-03 — Regeneración del catálogo

Se regeneró la cadena completa desde cero:
- `construir_catalogo.py` → `catalogo.csv` (5862 filas)
- `cruzar_catalogo_y_mapa.py` → `fallos_localizados.csv` (5862 filas)
- Diff contra localizados anteriores: **0** — pipeline reproducible.

**Hallazgo:** el catálogo archivado (`archivo/data/catalogo_v14.csv`)
era idéntico al regenerado. No había fantasmas.

Renombrado de outputs: sin sufijos de versión en nombres de archivo.
Git versiona, no el nombre del archivo.

**Observación:** LibroVol330.2.md no tiene sección `indice_partes`
según el clasificador editorial (solo tiene `indice_legislacion` +
`indice_general`). `construir_catalogo.py` la encuentra con
`extender_inicio_indice_nombres()` — lógica de lookback que el
clasificador no tiene. 45 indice_partes de 46 archivos.

### H061 — Estado final

- **Corpus:** 5862 casos. Sin cambios.
- **Votos:** 27336. Sin cambios.
- **Zonas:** 141970 segmentos. Sin cambios.
- **Editorial:** 135 secciones (46 indice_general, 45 indice_partes,
  20 indice_legislacion, 18 indice_materias, 5 acordadas, 1 discurso).
  Era 53 genéricas (49 indice, 4 discurso).
- **Catálogo:** regenerado en `output/catalogo/catalogo.csv` (5862).
  Idéntico al archivado.

**Outputs canónicos (4 parser + 2 catálogo):**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27336 filas.
- `output/parser/csjn_casos_zonas.csv` — 141970 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.
- `output/catalogo/catalogo.csv` — 5862 filas.
- `output/catalogo/secciones_indices.csv`.

**Scripts creados:** `scripts/auditoria/H061/` — validar_h061.py,
crosscheck_indice_partes.py (histórico, no corre — importaba función
eliminada).

**Commits:** 3 (snapshot pre-H061, integración subtipos, limpieza +
catálogo regenerado).

## H062 — Auditoría de deuda técnica y limpieza documental (2026-05-24)

**Objetivo:** releer DEUDA_TECNICA.md completa contra el estado actual del
código. Marcar cerrados bugs resueltos implícitamente, descartar obsoletos,
reescribir sección de prioridades.

### H062-01 — Auditoría contra código

Lectura línea por línea de DEUDA_TECNICA.md (3320 líneas) cruzada contra
parser.py (2941), cruzar_catalogo_y_mapa.py (436), construir_catalogo.py,
detectar_paginas.py, parser_editorial.py. Contexto de BITACORA H046-H061
y PIPELINE.md.

**Bugs cerrados (6):**
- B013: ya decía "aplicado y validado H035+H038" pero seguía en ACTIVA.
- B029: `max_lines=40` eliminado por B055 (H042). `collect_firma_lines`
  ahora usa `max_lines=None` (techo = `len(bloque)`).
- B030: redundante con B018, búsqueda atrás eliminada por B069.
- B039: descriptivo, no bug.
- B046: sin manifestación empírica. Deduplicación del catalogador previene
  el mecanismo. Los 43 faltantes explicados por B009 (y resueltos por Fase F).
- B060: ya aplicado H040, estaba en EN VALIDACIÓN.

**Bugs actualizados (5):**
- B009: Fase F aplicada. `cargar_localizados` infiere ubicación para los
  43 `pagina_no_en_mapa`. Diferencial catálogo-parser = 0.
- B018: 2/3 componentes de causa raíz mitigados (B069 eliminó backward,
  B070 validación texto corriente, B074 guard posicional). Estimación
  ~570 obsoleta.
- B024: parcialmente mitigado por zonificador (H051) + residuo (H055).
- B025: cardinalidad 414 obsoleta post-fixes. Re-medición pendiente.
- B033: degradado a cosmético (`ultimo_del_tomo_sin_fin` no se manifiesta
  en producción).

### H062-02 — Limpieza estructural

- Duplicados B052/B053/B054 eliminados (aparecían dos veces).
- Dos secciones "NOTAS PARA LA SESIÓN SIGUIENTE" eliminadas (contenido
  histórico tachado).
- Matriz pendiente post-H053 eliminada (obsoleta).
- Resumen ejecutivo reescrito con conteo actual (~30 cerrados, ~25 activos
  pipeline, ~10 auditor).
- Próximo trabajo priorizado reescrito (B010, B032, B025, B018, B045,
  B054/M06, M02).

### H062-03 — Decisiones documentales

- M01 cerrado: PIPELINE.md deprecado a `archivo/docs/PIPELINE_v1.md`.
- M05 cerrado: no-resoluble (sin git log del período, sin impacto operativo).
- PIPELINE_HALLAZGOS.md → `archivo/docs/` (el propio archivo declaraba
  archivarse cuando PIPELINE.md cubriera las 4 etapas).
- Flag de M04 limpiado (contenido correspondía a M05).
- Mapeo histórico XXI-l, XXI-m, XXI-v actualizado a cerrado.

### H062 — Estado final

- DEUDA_TECNICA.md: 3320 → 2934 líneas (−386).
- Corpus sin cambios: 5862 casos, 27336 votos, 141970 zonas, 135 editorial.
- Código sin cambios (sesión de documentación pura).

## H063 — Fix B032 (RE_VOTO_HDR) + diagnóstico B010 (RE_CONSIDERANDO) (2026-05-24)

### H063-01 — B032: fix RE_VOTO_HDR y RE_DISID_HDR

**Problema:** regex `RE_VOTO_HDR` exigía `del?|de\s+l[ao]s?` antes del
título, descartando "Voto la señora ministra..." (sin "de"). Idem
`RE_DISID_HDR`.

**Fix:** agregar `|l[ao]s?` al grupo de artículos en ambas regex (L160,
L165). Comentario inline `# B032`.

**Validación:**
- `medir_voto_hdr.py` sobre 46 archivos: +13 votos, +3 disidencias,
  0 regresiones. Todos Argibay, concentrados en tomos 329–332.
- Regeneración full corpus: 27336 votos (sin cambio en filas — los
  votos ya se detectaban por firma/`parse_firma`).
- Diff `n_votos_svoto` pre/post: +13 casos con delta +1.
- Diff `n_disidencias` pre/post: +3 casos con delta +1.
- Impacto real: corrección de contadores `n_votos_svoto`/`n_disidencias`
  en `csjn_casos.csv` y mejor delimitación de `texto_voto` en
  `csjn_casos_votos.csv` para esos 16 casos.

**Hallazgo:** RE_VOTO_HDR no genera filas de votos — esas vienen de
`parse_firma` (L2566). RE_VOTO_HDR alimenta `marcadores_votos` →
`extraer_textos_votos` (texto del voto individual) y contadores
`n_votos_svoto`/`n_disidencias`.

### H063-02 — B010: diagnóstico de RE_CONSIDERANDO

**Patrón identificado:** "Autos y Vistos; Considerando:" — header
combinado que no matchea `RE_CONSIDERANDO` (`^Considerando\s*[:.]?\s*$`
con `.match()`). 24 ocurrencias solo en 331.2, ~1238 en todo el corpus.

**Fix propuesto:** `Considerando\s*[:.]\s*$` con `.search()`. Cambios:
remover ancla `^`, hacer `[:.] ` obligatorio (no opcional), usar
`.search()` en 5 ubicaciones (L654, L1302, L1318, L1809, L2276).

**Validación pre-fix:**
- `verificar_considerando_dictamen.py` sobre 46 archivos: +1238
  nuevos en fallo, 8 FP en zona de dictamen.
- Los 8 FP son filtrados por `lineas_dictamen` en `extraer_considerando`.
- Riesgo residual: apertura detection (L1302/L1318) y zonificador
  (L1809) no filtran por zona de dictamen. Documentar como sub-item.

**Hallazgo arquitectónico:** el zonificador crea zonas pero no todos
los loops de detección las usan como constraint. `extraer_considerando`
filtra por `lineas_dictamen`; apertura detection, marcadores_votos y
dispositivo escanean el bloque entero. Documentar como M-item.

**Estado:** diagnóstico completo, fix diseñado, validación de seguridad
hecha. Pendiente aplicar en próxima sesión.

### H063 — Estado final

- **B032:** cerrado. parser.py + medir_voto_hdr.py commiteados.
- **B010:** diagnóstico completo, fix listo para aplicar.
- **Nuevo M-item:** detección sin constraint de zona (arquitectónico).
- Scripts de auditoría nuevos: `scripts/auditoria/medir_voto_hdr.py`,
  `scripts/auditoria/verificar_considerando_dictamen.py`.
s
## H064 — M09 + B010: constraint de zona y RE_CONSIDERANDO (2026-05-24)

**Objetivo:** aplicar constraint de zona en detección de votos (M09) y
relajar RE_CONSIDERANDO (B010) para capturar variantes con prefijo.

### H064-01 — Housekeeping H062

Verificación de pendientes H062: PIPELINE.md y PIPELINE_HALLAZGOS.md
ya movidos a `docs/` (commit `3b55b85`). DEUDA_TECNICA.md con cambios
sin commitear, CSVs pendientes. Scripts duplicados identificados para
limpieza posterior.

### H064-02 — M09: constraint de zona en loop de votos

Diagnóstico: el loop principal de detección de votos/disidencias
(L2248-2281) solo excluía `lineas_dictamen`. ~500K líneas de sumario,
header_pagina, residuo_caso_anterior y epílogo se escaneaban sin
constraint.

Implementación: set `lineas_excluir` derivado de `_zonas_linea`
(zonas fuera de `{apertura, cuerpo, dispositivo, firma, voto_separado}`).
Reemplaza `if k in lineas_dictamen` por `if k in lineas_excluir`.

Validación (poc_m09.py): 0 diffs sobre 5667 fallos. 500K líneas
protegidas (155K sumario, 137K header_pagina, 107K residuo, 100K epílogo).
Impacto directo: ninguno. Impacto preventivo: protege B010 y futuros
regex más permisivos.

### H064-03 — B010: RE_CONSIDERANDO permisivo + guarda dispositivo

Fix: regex `^Considerando\s*[:.]?\s*$` → `Considerando\s*[:.]\s*$`
(sin anchor `^`, colon/punto obligatorio). `.match()` → `.search()`
en 5 ubicaciones. Guarda en `extraer_considerando`: solo acepta matches
antes de `por_ello_idx`.

Primera corrida sin guarda: 2 regresiones a wc=0 (339_p444 y 341_p929).
Causa: "Considerando:" del caso siguiente o de voto individual matcheaba
después del dispositivo. Guarda `por_ello_idx` resolvió ambas.

Validación final (audit_b010_full.py):
- wc_considerando: 1188 cambios (911 reducciones, 277 aumentos, 0 a cero).
- is_originaria: 62 cambios. Auditoría con audit_originaria_1a0.py:
  36/36 mejoras legítimas (1→0 por exclusión de texto editorial),
  26 nuevas (0→1), 0 bugs.
- outcome: 2 cambios (otro → inadmisible_280).
- firma_raw, voting_pattern, n_votos, n_disidencias: sin cambios.
- n_jueces, tipo_entrada, apertura_tipo, wc_dictamen: sin cambios.

### H064-04 — Housekeeping

Limpieza de scripts:
- Raíz: 3 PoCs eliminados/movidos a `scripts/auditoria/H064/`.
- `scripts/pipeline/`: `medir_voto_hdr.py` y `parser_fix.py` movidos.
- `scripts/auditoria/`: duplicados eliminados, scripts organizados en
  H057/, H058/, H064/.

Skill `cierre-sesion-corpus` creado para protocolo de cierre de sesión.

### H064 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 195 sumario_editorial/sumario_con_link).
- **Sin firma:** 34 / 5667 fallos (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27336 filas.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27336 filas.
- `output/parser/csjn_casos_zonas.csv` — 142030 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.

**Scripts creados:** `scripts/auditoria/H064/` — poc_m09.py,
audit_b010.py, audit_b010_full.py, audit_originaria_1a0.py,
diff_b010.py, medir_voto_hdr.py, parser_fix.py,
verificar_considerando_dictamen.py, diagnostico_fin_fallo_v1.py,
tabular_senales_lote.py.

**Commits:** 1 (M09+B010 parser + CSVs).

## H065 — Recalibración detectores 280/ac4/art.117 (2026-05-24)

**Objetivo:** recalibrar los detectores de outcome post-B010 — inadmisible_280,
inadmisible_acordada_4 e is_originaria.

### H065-01 — Diagnóstico

Exploración sobre csjn_casos.csv pre-fix. Hallazgo principal: el patrón
`art[íi]?culo?` en 4 regexes (RE_280_CONSIDERANDO, RE_280_LIBRE,
RE_ACORDADA_4_CONSIDERANDO, RE_ART_117_CN) no matcheaba la abreviatura
"art." — forma dominante en el corpus. Solo matcheaba "artículo" completo.
RE_ACORDADA_4 además exigía "artículo 1" pero la Corte cita arts. 2, 4, 5, 7.
285 menciones de "art. 280 del Código Procesal" en considerando, solo 17
matcheaban. 60 menciones de "acordada 4/2007", 0 matcheaban.

Diagnóstico de fallos mixtos (280 parcial + merit outcome en dispositivo):
49 casos tienen 280 en considerando pero el dispositivo concede el recurso.
Diseño de merit guard en classify_outcome para no sobreescribir
hace_lugar/procedente/revoca/confirma/nulidad.

### H065-02 — Fix aplicado

6 ediciones en parser.py:
1. RE_280_CONSIDERANDO: `art[íi]?culo?` → `(?:art\.?|art[íi]culo)`
2. RE_280_LIBRE: mismo fix + paréntesis opcional `\(?`
3. RE_ACORDADA_4_CONSIDERANDO: reescrito — `\d+` en vez de `1`, incisos opcionales
4. Nuevo RE_ACORDADA_4_REGLAMENTO: variante libre "reglamento...acordada 4/2007"
5. classify_outcome v10 → v11: merit guard (evalúa dispositivo primero)
6. RE_ART_117_CN: mismo fix para is_originaria
7. Fallback sin_dispositivo: agrega RE_ACORDADA_4_REGLAMENTO

Validación pipeline completo: 5862 casos, 27336 votos, 142030 zonas, 135 editorial.
0 cambios en sin_firma, votos, zonas.

### H065-03 — Validación manual de ac4

Revisión caso por caso (40 casos) en explorador v5 por Guillermo.
37 genuinos, 3 FP documentados (339_p185, 345_p1421, 348_p811 — ac4
mencionada como antecedente del tribunal inferior, no aplicación de la Corte).
Se evaluaron filtros (revocatoria en dispositivo, revocatoria cerca de ac4 en
considerando, señal de aplicación directa). Ninguno limpia FP sin matar
genuinos. FP residual aceptado como limitación técnica (7.5%).

Bugs estructurales encontrados en revisión: 340_p2001 (caso roto),
332_p1085 (dos dispositivos), 333_p1464 (voto conjunto no detectado),
334_p256 (firma de voto conjunto rota).

### H065-04 — Diagnóstico de inadmisible_280 (pendiente H066)

Preclasificación de los 278 inadmisible_280:
168 per curiam genuino (wc ≤ 60), 24 corto probable ok (wc 61-200),
14 parcial (280 al final), 12 largo (revisar), 16 arrastre probable
(280 del caso anterior en primer 10% del texto, B045), 44 fantasma
(sin match de regex — dato inconsistente, investigar).

Scripts de diagnóstico creados: poc_280_ac4.py, diag_280_corpus.py.

### H065 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 195 sumario_editorial/sumario_con_link).
- **Sin firma:** 34 / 5667 fallos (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27336 filas.
- **Outcomes:** inadmisible_280: 278, inadmisible_acordada_4: 40,
  desestima: 475, otro: 1791, hace_lugar: 1084.
- **is_originaria:** 478.
- **Trayectoria sin_firma:** sin cambio (34).

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27336 filas.
- `output/parser/csjn_casos_zonas.csv` — 142030 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.

**Scripts creados:** `scripts/auditoria/H065/` — poc_280_ac4.py,
diag_280_corpus.py.

**Commits:** 2 (snapshot pre-fix, fix aplicado).

## H066 — Auditoría ac4 + 280 + unhyphenate (2026-05-24)

**Objetivo:** auditar la cobertura de inadmisible_acordada_4 (40 casos),
diagnosticar inadmisible_280 (278 casos), e investigar bugs estructurales
de H065. Se descubrió B077 (quiebres de línea con guión rompen outcomes)
y se aplicó junto con B078 (regex ac4 ampliada).

### H066-01 — Auditoría de ac4 (40 casos)

Diagnóstico sobre CSV H065. De los 40 clasificados:
- 34 genuinos: tienen "acordada 4/2007" en considerando_text y la regex
  original los captura.
- 6 fantasmas: no contienen "acordada 4" en su texto. Son inconsistencia
  CSV/parser (versión intermedia de H065). IDs: 332_p1085, 333_p1254,
  339_p1463, 340_p2001, 341_p512, 345_p1421.

FN: 12 candidatos se reducen a 1 genuino (333_p1235: "artículo 4º de la
acordada 4/2007, por lo que corresponde declarar inadmisible"). Escapaba
porque la regex exigía "del reglamento... acordada" pero el texto dice
"de la acordada" (referencia directa al articulado).

4 borderline capturados por la regex ampliada: menciones contextuales
(reposiciones, devoluciones a inferior) que no son rechazos genuinos por ac4.

### H066-02 — B078: RE_ACORDADA_4_DIRECTA + fixes regex

Tres cambios en las regex de ac4:
1. Nueva RE_ACORDADA_4_DIRECTA: "art N de la acordada 4/2007".
2. Año: `2007` → `(?:20)?07` (acepta "4/07").
3. Guard: `4(?!\d)` (no matchea "acordada 47/91").
4. Plural: `art[s]?\.?` (matchea "arts.").

Validación: 8/8 strings de prueba, 34/40 preservados, FN 333_p1235
recuperado.

### H066-03 — B077: _unhyphenate (descubrimiento + fix)

Al investigar 334_p256 ("mal con- cedido" no matcheaba `mal concedid[ao]`),
se descubrió que 37.3% de los fallos (2112/5667) tienen guión de quiebre
en por_ello_text, y 150 rompen un outcome keyword.

Función `_unhyphenate()` aplicada en classify_outcome v12 (paso 0) y en
fallback sin_dispositivo. Simulación sobre CSV: 85 dispositivos cambian,
229 outcomes finales cambian. Principales: otro→desestima (31),
otro→procedente (29), otro→confirma (24), inadmisible_280→otro (33 por
merit guard corregida).

### H066-04 — Diagnóstico de 280

278 clasificados, desglose:
- 168 per curiam (wc_cons ≤ 60) — genuinos.
- 43 fantasmas (sin "280" en texto) — inconsistencia CSV/parser.
- 20 arrastre (280 en primer 10% del considerando, 16 con "Por ello"
  inmediato → B045 residuo del caso anterior).
- 39 normal + 8 largo — genuinos.
- 18 FN: mencionan art. 280, outcome no-merit, pero no clasificados
  como 280 (capturables post re-run).

### H066-05 — Investigación bugs estructurales H065

Desde el CSV (sin corpus .md):
- 340_p2001: solapamiento de spans con vecinos (L39521 empieza dentro de
  340_p2000 que termina en L39542). Por_ello dice "hacer lugar" (merit).
- 340_p188: wc_may=6547 con wc_cons=164 — dos casos pegados.
- 332_p1085: FP ac4, dos dispositivos, sin mención de acordada.
- 333_p1464: GENUINO ac4 (tiene "art. 7º... acordada 4/2007" en
  considerando). Bug es el voto conjunto de Highton no detectado.
- 334_p256: GENUINO ac4 pero por_ello dice "mal con- cedido" — roto
  por guión (B077 lo arregla).

### H066-06 — sin_firma (34 casos)

21 sin_dispositivo + 13 con por_ello truncado (status_fin=
fin_extendido_pag_compartida). Concentrados en tomos 329 (15) y 330 (6).
Los 13 con por_ello no tienen firma detectable — el parser no llegó a la
zona de firma. Requiere investigación con corpus .md.

### H066 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 195 sumario_editorial/sumario_con_link).
- **Sin firma:** 34 / 5667 (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27336 filas.

**Outputs canónicos:** sin cambio (parser no re-ejecutado).

**Parser modificado (no re-run):**
- `parser.py`: classify_outcome v11→v12, `_unhyphenate()`, RE_ACORDADA_4_DIRECTA.

**Commits pendientes:** 1 (parser.py con B077+B078).

### H067-01 — Validación B077+B078 post re-run

Re-run del parser con B077 (unhyphenate) y B078 (ac4 regex ampliado)
aplicados en H066 pero no validados. Totales estables: 5862 casos,
27336 votos.

Outcome principal: `otro` baja 123 (1791→1668), redistribuido a
outcomes correctos: procedente +51, confirma +17, competencia +15,
hace_lugar +11, 280 +18, ac4 +12, abstracto +3, mal_concedido +1,
originaria +1, desestima +1. revoca -6, desistimiento -1.

Divergencia con simulación H066 (que corría sobre texto CSV viejo):
ac4 sube a 52 (esperado ~35), 280 sube a 296 (esperado ~253).
Causa: el re-run re-extrae texto desde .md fuente, la unhyphenación
recupera FN que la simulación no podía prever.

Auditoría ac4 (52): 0 fantasmas detectables. Los 12 sin match en
CSV truncado tienen considerando_text de ~2000 chars (el parser
clasifica con texto completo, el CSV trunca a 2000). Los 6 fantasmas
del CSV viejo desaparecieron (guard `4(?!\d)` funciona).

Auditoría 280 (296): 0 fantasmas. Los 54 sin match visible están
todos truncados. Todos los 291 (post-B079) mencionan "de la Nación".

### H067-02 — B079: MERIT_OUTCOMES ampliado

Descubierto que MERIT_OUTCOMES en classify_outcome solo protegía
{hace_lugar, procedente, revoca, confirma, nulidad}. Faltaban
competencia, abstracto, originaria, desistimiento.

Decisión de diseño: mal_concedido NO se agrega. Verificación empírica:
3 casos mal_concedido+280 (329_p292, 329_p437, 330_p88) son genuinos —
el considerando dice "es inadmisible (art. 280)". El dispositivo
"mal concedido" y la razón "280" coexisten legítimamente, como
"desestima" + "280".

Fix: una línea. 5 casos movidos: 280→competencia (1), 280→abstracto (1),
280→originaria (2), 280→desistimiento (1). Validado con re-run.

### H067-03 — B080: RE_280_ABREVIADO (POC, revertido)

Análisis del corpus de 280 (corpus_inadmisible_280.md, 291 casos,
6.2MB). Inventario de formas de cita: "del Código Procesal Civil y
Comercial" (535), "CPCCN" (219), "C.P.C.C.N." (222), "del CPCCN" (21).

POC de regex para formas abreviadas: 1 FN recuperado (344_p3095,
desestima→280, usa "art. 280 del CPCCN"). Re-run: 280 291→292.
Decisión: revertido por REE (1 caso no justifica regex extra).

Discusión conceptual: outcome vs razón son dimensiones ortogonales.
desestima = resolución, 280 = fundamento. No son excluyentes.
El sistema actual colapsa en una columna, prioriza la razón como
más informativa. Tema abierto para posible reingeniería futura.

### H067 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 195 sumario_editorial/sumario_con_link).
- **Sin firma:** 34 / 5667 (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27336 filas.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27336 filas.
- `output/parser/csjn_casos_zonas.csv` — 142030 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.

**Outcomes (post B079, B080 revertido):**
otro 1668, hace_lugar 1095, procedente 651, competencia 578,
desestima 476, inadmisible_280 291, confirma 237, revoca 208,
originaria 160, abstracto 87, nulidad 59, sin_dispositivo 57,
inadmisible_acordada_4 52, mal_concedido 38, desistimiento 10.

**Commits:** 2 (snapshot pre-B079, B079 validado + B080 revertido).

## H068 — Diagnóstico B025 + B045 + B018 (2026-05-24)

**Objetivo:** re-medición de bugs pendientes (B025, B045 arrastre 280,
B018 residual) y análisis de causa raíz B045 con scripts de catálogo y
cruzador.

### H068-01 — Re-medición B025 (falsos unánime)

Pool unanime: 3508 fallos. Filtrado por `pista_fin = firma_actual`
(mecanismo B025): 72 casos (2.1%, era 414 = ~11.8%).

Distribución de wc en los 72: rango 55-7017, sin gap natural limpio.
Análisis por dos señales cruzadas:

- `status_localizacion` contiene `ancla_catalogo`: 65.5% en los 72
  vs 8.3% en corpus (8x sobrerrepresentado).
- `considerando_text` empieza con header de tomo (patrón `3XX ...`):
  señal directa de arrastre.

Tres poblaciones (wc ≤ 300, 29 casos):
- Cat A: ancla + tomo_header → 14 falsos seguros.
- Cat B: ancla + Considerando → 6 ambiguos.
- Cat C: ok + Considerando → 9 prob. legítimos.

Caso testigo `343_p2243` sigue en pool (wc=64, cat A).
Tasa unanime corregida: 61.5-61.7% (vs 61.9%). Δ = 0.2-0.4pp.

### H068-02 — Diagnóstico arrastre 280 (B045 manifestación B)

291 casos `inadmisible_280`. Búsqueda de 280 en primer 10% del
considerando + "Por ello" en primer 15%: 15 hits (era 16 en H066,
B079 sacó 1 vía merit guard).

Verificación textual: los 15 tienen `considerando_text` que empieza con
per curiam 280 del caso anterior ("art. 280... Por ello, se desestima"
+ firma), seguido del contenido real del caso. Word counts altos
(936-18477) confirman que el 280 es arrastre.

Discriminador probado con regex real del parser: RE_280 match antes de
"Por ello" en `considerando_text` → 15/15 arrastre, 0 FP sobre 276
genuinos. POC B081 (guard en `classify_outcome`): 15 cambios
(6 desestima, 1 mal_concedido, 8 otro), 0 regresiones. Pool 280:
291→276. **No aplicado** (REE: 15 casos no justifican guard extra;
8 van a `otro` por gaps preexistentes en OUTCOME_PATTERNS_DISPOSITIVO).

### H068-03 — Inspección causa raíz B045

Con `construir_catalogo.py` y `cruzar_catalogo_y_mapa.py` en mano:

- `construir_catalogo.py:410`: `pagina_fin = pagina_inicio_next` (sin -1).
- `cruzar_catalogo_y_mapa.py:245`: `linea_fin = linea_header - 1`.
- Resultado: bloque termina una línea antes del header de página del
  caso siguiente.

Cuantificación sobre CSV:
- 97.0% (5499/5667) con `linea_fin_real > linea_fin` (parser extiende).
- Extensión mediana: 11 líneas. p95: 27. Max: 199.
- 0 casos con coincidencia exacta.
- 110 en fallback `firma_actual` (72 unanime, 15 ssv, 15 dis, 6 mixed, 2 sf).

Tres opciones de fix discutidas:
- Camino A: bump cruzador +30 líneas (cubre 98.4%). Riesgo cascada.
- Camino B: invertir fallback firma (adelante primero). Riesgo en fallos
  cortos.
- Camino C: semántica inter-caso (pasar linea_fin_real al siguiente).
  Riesgo cascada de errores.

Decisión: evaluar con tests en sesión dedicada. El -1 del cruzador
podría estar compensando en otras partes del parser.

### H068-04 — Re-medición B018 residual

554 casos con `primer_token` genérico no excluido (Banco 88,
Provincia 81, Asociación 78, Estado 57, Ministerio 41). 185 cerrados
por Pista 1 con token genérico del siguiente. B069 (búsqueda atrás
eliminada) + B070 (`_es_texto_corriente`) absorben la mayoría. Solo 3
casos `caratula_siguiente` con wc ≤ 100, todos legítimos. Sin señal
medible de FP residual desde CSV. Requiere .md o logging para confirmar.

### H068 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 195 sumario_editorial/sumario_con_link).
- **Sin firma:** 34 / 5667 (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27336 filas.

**Outputs canónicos:** sin cambio (sesión de diagnóstico, parser no
re-ejecutado).

**Scripts creados:** ninguno (POC B081 descartado).

**Commits:** 0.

## H069 — B045 bidireccional closest-to-lfc en fallback firma_actual (2026-05-25)

**Objetivo:** corregir falsos unanime (B025) y votos truncados causados por
el fallback backward-first en `detectar_fin_real`.

### H069-01 — Diagnóstico y evaluación de opciones

Análisis de los 112 casos `firma_actual`. Hallazgo clave: backward search
encuentra firma arrastrada del caso anterior (lejos de lfc) y retorna
inmediatamente — el forward search nunca corre. La firma real está en la
zona de extensión (gap entre lfc y next case, mediana 15 líneas, 99% ≤ 30).

Matriz de opciones evaluadas:
- **A (bidireccional closest-to-lfc):** parser only, ~10 líneas, auto-ajustable.
- **B (cruzador +30):** 1 línea, magic number, efectos cascada en pistas 1-4.
- **C (A+B combinado):** máxima cobertura, riesgo medio.
Decisión: opción A (más REE).

### H069-02 — POC bidireccional

Script `poc_b045_bidireccional.py` simuló bidireccional sobre los 112 firma_actual.
Resultado: 16 MEJORA_SEGURA (unanime), 19 CAMBIO_REVISAR (non-unanime, votos
truncados), 0 REGRESION, 77 SIN_CAMBIO. Guarda `fwd >= prox_header` descartada
(bloqueaba mejoras y cambios por igual; discriminador real es `fwd_en_next`
que dio False en los 112 casos).

### H069-03 — Spot-check de CAMBIO_REVISAR

Script `poc_b045_inspeccion.py` inspeccionó 3 casos representativos:
- 342_p1426 (disidencia, Δ=6): FP cosmético de `linea_es_firma_de_juez` en
  header de disidencia partido en varias líneas. Sin daño.
- 341_p878 (según_su_voto, Δ=146): voto separado de Rosenkrantz (146 lín)
  recuperado íntegramente. Mejora genuina.
- 344_p603 (mixed, Δ=701): disidencia completa de Maqueda (~700 lín)
  recuperada. Mejora masiva.
Conclusión: los 19 CAMBIO_REVISAR son votos/disidencias truncados, no regresiones.

### H069-04 — Patch y validación

Patch: `detectar_fin_real` L1709-1731, fallback firma_actual cambia de
backward-first a bidireccional closest-to-lfc con strict less-than
(empate → backward). Re-run reproducible.

Validación (`poc_b045_validacion.py`) comparando CSV pre/post via git:
- 33 cambios (todos firma_actual→firma_actual, todos Δlfr > 0).
- 2 empates correctamente bloqueados (342_p1426 dist=3, 345_p1205 dist=6).
- 0 cambios fuera de firma_actual, 0 nuevos sin_firma, 0 retracciones.
- 33/33 word_count suben, 0 bajan.
- 5 transiciones de voting_pattern: unanime→svoto (3), unanime→disidencia (1),
  sin_firma→unanime (1).
- 9 outcomes redistribuidos, 3 a "otro" (B082: classify_outcome sobre bloque
  completo incluyendo disidencia).

### H069 — Estado final

- **Corpus:** 5862 casos (5668 fallos + 34 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 33 / 5668 fallos (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27341 filas.
- **Trayectoria sin_firma:** 813→782→503→481→449→438→425→422→406→148→114→113→76→74→69→38→35→34→33.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27341 filas.
- `output/parser/csjn_casos_zonas.csv` — 142505 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.

**Scripts creados:** `poc_b045_bidireccional.py`, `poc_b045_inspeccion.py`,
`poc_b045_validacion.py` (raíz del repo).

**Commits:** 3 (snapshot pre-H069, snapshot post re-run, B045 fix parser.py).

## H070 — B082 fix: considerando limpio de votos individuales (2026-05-25)

**Objetivo:** corregir la contaminación de `considerando_text` con texto de disidencias/votos individuales que afectaba `classify_outcome`.

### H070-01 — Diagnóstico

Análisis del CSV confirmó 62 casos con `wc_considerando > wc_mayoria` en
fallos con disidencias (señal de leakage). Los 3 sospechosos originales
de H069 (344_p220, 347_p818, 348_p659) descartados: son unánimes sin
disidencias, outcomes "otro" legítimos.

Caso testigo 329_p437: `wc_mayoria=26`, `wc_considerando=833`.
El considerando incluía texto de disidencia con firma y sumarios
editoriales. Caso 332_p5: el art. 280 estaba explícitamente dentro
de un "Voto del señor presidente", no en la mayoría.

### H070-02 — PoC v1 (descartado)

Fix: buscar dispositivo alternativo en zona mayoría cuando
`por_ello_idx >= inicio_votos_indiv`. Resultado: 63 regresiones
(todos a sin_dispositivo). Causa: en 64 casos, el dispositivo legítimo
de la mayoría está DESPUÉS de inicio_votos_indiv (headers de votos
antes del dispositivo). El patch descartaba un dispositivo correcto
sin encontrar reemplazo.

### H070-03 — PoC v2 (insuficiente)

Fix: excluir líneas con zona `voto_separado` del considerando.
Resultado: 11 wc_considerando cambios mínimos (Δ promedio -60),
0 outcomes. Insuficiente porque el zonificador asigna `dispositivo`,
`firma`, `cuerpo` dentro de votos individuales — solo `voto_separado`
(body post-header) es específico.

### H070-04 — PoC v3 (aplicado)

Fix: excluir del considerando todas las líneas >= `inicio_votos_indiv`.
3 líneas de código. Resultado:
- 19 outcomes corregidos (todos inadmisible_280 → outcome correcto:
  10 desestima, 8 otro, 1 mal_concedido)
- 66 wc_considerando limpiados (Δ promedio -1155 palabras)
- 0 regresiones, 0 cambios voting_pattern, 3 is_originaria corregidos
- Verificación caso a caso: en los 19, el art. 280 estaba en texto de
  disidencia/voto individual, no en la mayoría

Deuda residual: `por_ello_text` sigue extrayéndose del bloque completo.
Deuda nueva M10: zonificador debería distinguir zonas mayoría vs votos.

### H070 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 195 sumario_editorial/sumario_con_link).
- **Sin firma:** 33 / 5667 (0.6%). Cobertura firma: 99.4%.
- **Votos:** 27341 filas.
- **Outcomes:** otro 1679, hace_lugar 1097, procedente 651,
  competencia 578, desestima 483, inadmisible_280 272, confirma 236,
  revoca 206, originaria 160, abstracto 88, nulidad 60,
  sin_dispositivo 57, inadmisible_acordada_4 52, mal_concedido 38,
  desistimiento 10.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27341 filas.
- `output/parser/csjn_casos_zonas.csv` — 142505 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.

**Scripts creados:** `scripts/auditoria/069/poc_b082_compare.py`,
`scripts/auditoria/069/poc_b082_verificar.py` (verificación H070, ubicación provisional).

**Commits:** snapshot pre-B082, B082 fix v3 aplicado.

## H071 — Barrido diagnóstico de monstruos + B083 + B084 (2026-05-25)

**Objetivo:** barrer el corpus buscando casos patológicos (rotos, cortos, largos, inconsistentes) sin perseguir bugs conocidos — diagnóstico bottom-up.

### H071-01 — Barrido sistemático por CSV

Queries incrementales sobre csjn_casos.csv (5667 fallos):
- wc ultracortos (0-200): 1 fallo con wc=37 (345_p378), 7 con wc 51-100, 233 con wc 101-200.
- wcM=0: 0 casos. wcM≤4: 26 casos (tomos 329-334).
- wcM=1 + unanime: 4 mal clasificados (deberían ser segun_su_voto).
- sin_dispositivo + firma: 37 casos.
- wc_votos=0 + vp no unánime: 37 casos.
- wcC > wcM: 161 casos (72 sin dictamen). Anomalía estructural.
- n_jueces=1: 30 casos.
- Monstruos: 330_p2849 (110k wc), 333_p1474 (wcD=56k), 342_p1827 (wcD=7k).
- Ratios extremos wcD/wcM > 20: 17 casos (overlap con wcM≤4).

### H071-02 — Inspección .md de 101 casos

Tres extracts generados con scripts:
- monstruos_h071.md (v1: 16 casos, v2: 74 casos)
- sin_disp_h071.md (27 sin_dispositivo + firma restantes)

Patrones identificados:
1. **wcC incluye residuo** (161 casos): extraer_considerando no excluye lineas_residuo. Confirmado 25/25 en .md.
2. **wcM≤4** (26 casos): todos empiezan con "VOTO DE" / "DISIDENCIA DE". Confirmado 26/26.
3. **Monstruos** (3): 330_p2849 fin desbordado, 333_p1474 dictamen legítimamente enorme (Rachid), 342_p1827 dictamen largo.
4. **sin_dispositivo + firma** (37): clasificados en 5 sub-mecanismos: 7 "Por ello" perdido (B085), 7 "así se resuelve" (B084), 4 "tribunal resuelve" (B086), 4 "hágase saber" (B086), 15 sin fórmula (crónico).

### H071-03 — B083: excluir residuo de considerando_text

Fix: parser.py L2514, `_lineas_no_cons = set(lineas_dictamen) | lineas_residuo`.
Validación: 0 outcomes cambiados, 617 wcC limpiados (Δ mean=-116, todos negativos), 2 is_originaria FP corregidos (329_p2469, 330_p1599), wcC>wcM 161→0, 0 regresiones.

### H071-04 — B084: Tier 4 dispositivo "así se resuelve"

Fix: Tier 4 último recurso, solo si Tier 1/2/3 no encontraron nada. Regex `[Aa]sí se resuelve` con `.search()` y firma validada.
Validación: 7 sin_dispositivo→otro (329_p317, 330_p22, 330_p4590, 331_p548, 333_p1784, 340_p1392, 348_p532), 0 regresiones.

### H071 — Estado final

- **Corpus:** 5862 casos (5667 fallos + 35 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 33 / 5667 (0.6%). Cobertura: 99.4%.
- **Votos:** 27341 filas.
- **sin_dispositivo:** 57→50 (B084).
- **Trayectoria sin_firma:** 813→…→33 (sin cambio).

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27341 filas.
- `output/parser/csjn_casos_zonas.csv` — 142505 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 135 secciones.

**Scripts creados:** `scripts/auditoria/H071/` — extraer_monstruos.py, extraer_sin_disp.py.

**Outputs diagnósticos:** `output/diagnostico/` — monstruos_h071.md (v1+v2), sin_disp_h071.md, diagnostico_h071.md, problematic

## H072 — B085-B088: dispositivo, voting_pattern, editorial (2026-05-25)

**Objetivo:** validar y aplicar fixes B085-B088 diagnosticados en H071. Reducir sin_dispositivo y corregir voting_pattern y desborde editorial.

### H072-01 — B085 Tier 3b: validación PoC y aplicación

PoC poc_b085.py sobre corpus completo (5667 fallos). Bug en PoC: columna `type_entrada` → `tipo_entrada` corregido. Resultado: 71 mejoras (5/7 targets B085 + 66 extras concentrados en tomos 329-334), 0 regresiones. Los 2 targets no contados (331_p1013, 334_p1033) ya resueltos por el baseline del PoC (diferencia entre reimplementación simplificada y parser real). Parser corrido: sin_dispositivo 50→40. Commit: `B085: Tier 3b — sin_dispositivo 50 -> 40, 0 regresiones`.

### H072-02 — B086 "tribunal resuelve" + revisión manual

Diagnóstico de 8 casos B086. Regex `[Ee]l\s+[Tt]ribunal\s+resuelve` agregada a Tier 4. "Hágase saber" descartado tras revisión manual: es providencia de mero trámite, no dispositivo. Caso 330_p2794 (caducidad de instancia) confirmó que el dispositivo real ("declárase operada la perención") está embebido en el considerando. 4 rescatados: 330_p1971→otro, 331_p2363→otro, 334_p362→otro, 339_p676→abstracto. 4 residuales sin fórmula estándar. sin_dispositivo 40→35. Commit: `B086: Tier 4 tribunal resuelve — sin_dispositivo 40 -> 35`.

Hallazgo: 331_p2363 y 334_p362 dan "otro" en vez de "revoca" → B091 nuevo.

### H072-03 — B087 guard unanime wcM≤4

Guard post-firma: si unanime y wcM≤4 y wc_votos>wc_mayoria → segun_su_voto. 5 casos corregidos (4 originales + 331_p793). unanime 3501→3496, svoto 740→745.

### H072-04 — B088 reorden Pistas detectar_fin_real

Diagnóstico: 330_p2849 (110k wc) desbordaba porque Pista 2 (sumario backward) encontraba header de sumario dentro del índice editorial, cortocircuitando Pista 4 (editorial). Fix: mover Pista editorial de posición 4 a posición 2. Resultado: 330_p2849 wc 110236→7448, status_fin fin_por_editorial. Efecto colateral: editorial sections 135→150, zonas 142489→141938, votos 27377→27382. Commit: `B087+B088: guard wcM<=4 svoto + reorden Pistas editorial primero`.

### H072-05 — Hallazgos nuevos

- **B089 (residuo pre-carátula):** 96% de bloques (5646/5862) incluyen cola del caso anterior. Campos de texto y wc contaminados. Prioridad pre-publicación.
- **B090 (Tier 5):** diseño para sin_dispositivo con dispositivo embebido sin fórmula. Solo corre cuando Tiers 1-4 fallan. PoC pendiente.
- **B091 (classify_outcome):** regex revoca no cubre "Tribunal resuelve: Revocar".
- Dataverse account creada con ORCID. Codebook (inglés) y README publicable pendientes.

### H072 — Estado final

- **Corpus:** 5862 casos.
- **Sin dispositivo:** 35 (trayectoria: 57→50 H071 → 40 B085 → 35 B086).
- **Sin firma:** 31.
- **Votos:** 27382 filas.
- **Editorial:** 150 secciones.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27382 filas.
- `output/parser/csjn_casos_zonas.csv` — 141938 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 150 secciones.

**Scripts creados:** `scripts/auditoria/poc_b085.py`.

**Commits:** 3 (B085 Tier 3b, B086 tribunal resuelve, B087+B088 guard svoto + reorden Pistas).

## H073 — B091 revocar fallback + B093 token inteligente (2026-05-25)

**Objetivo:** mejorar classify_outcome para formas infinitivas de "revocar" y reducir sin_firma por tokens genéricos en Pista 1.

### H073-01 — B091: fallback "revocar" en classify_outcome

classify_outcome v13. Agregado entry `("revoca", re.compile(r"\brevocar\b", re.I))` justo antes del catch-all "otro" en OUTCOME_PATTERNS_DISPOSITIVO. Posición final para que originaria, abstracto y otros merit outcomes mantengan prioridad sobre menciones de "revocar" en dispositivos mixtos.

Impacto: 151 outcomes cambiados. revoca 208→359. otro 1692→~1559. 10 inadmisible_280→revoca por merit guard (fallos mixtos donde Corte rechaza un agravio por 280 pero revoca otro). 1 FP marginal (347_p109, sección editorial). 0 regresiones en sin_dispositivo, sin_firma, votos.

### H073-02 — B093: diagnóstico sin_firma y primer_token_de_caratula inteligente

Diagnóstico de 31 sin_firma con script `extraer_sin_firma.py`: en todos los casos, Pista 1 de `detectar_fin_real` encontraba el token del caso siguiente en una cita jurisprudencial del cuerpo (ej: "Halper, Cristina María c/ ANSeS"), en la firma de jueces (ej: "Ricardo Luis Lorenzetti"), o en transcripciones in extenso ("Dicha sentencia dice así:"). La guarda `_es_texto_corriente` no alcanzaba porque las citas empiezan con mayúscula sin word-split previo.

Tres iteraciones:
- **v1 (descartada):** guarda de mayúsculas ≥60% en línea matcheada. sin_firma 31→21 pero −297 votos por carátulas mixed-case en tomos 337+.
- **v2 (descartada):** stoplist de tokens genéricos ("Provincia", "ANSeS", etc.) que saltea Pista 1 enteramente. sin_firma 31→18, votos +0, blanks +6.
- **v3 (aplicada):** `primer_token_de_caratula` reescrita con búsqueda profunda + stoplist sincronizada. Recorre TODOS los tokens de TODAS las variantes (separadas por "|"), saltea genéricos, devuelve primer token específico. Ej: "ANSeS (Benaben c/) | Benaben c/ ANSeS" → "Benaben"; "D.G.I. c/ Provincia de Mendoza" → "Mendoza". Stoplist como red de seguridad para casos donde ambas variantes son genéricas.

Decisión de diseño: `_GENERICOS` = {provincia, anses, nacion, nación, estado, afip, buenos, nacional, administracion, federal, direccion, instituto}. Extensible sin riesgo — el mecanismo prueba tokens más profundos antes de rendirse.

### H073 — Estado final

- **Corpus:** 5862 casos (5668 fallos + 34 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 17 / 5668 fallos (0.3%). Cobertura firma: 99.7%.
- **Votos:** 27455 filas.
- **Sin dispositivo:** 24.
- **Trayectoria sin_firma:** ...33→31→17.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27455 filas.
- `output/parser/csjn_casos_zonas.csv` — 141859 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Scripts creados:** `scripts/auditoria/extraer_sin_firma.py`.

**Commits:** 2 (snapshot pre-H073, H073: B091+B093).

## H074 — B094 guarda firma Pista 1 + B089 trim pre-carátula con tildes (2026-05-25)

**Objetivo:** corregir regresión 329_p1881 post-B093, eliminar residuo pre-carátula masivo (B089).

### H074-01 — Diagnóstico regresión 329_p1881 (Opción C)

Caso Tortorelli (329_p1881): sin_firma post-B093 pero con dispositivo. Diagnóstico: B093 cambió token del caso siguiente de "Provincia" a "Santiago". "SANTIAGO" matcheaba en la firma "ENRIQUE SANTIAGO PETRACCHI —" antes de la carátula real. Pista 1 cortaba en la firma → bloque perdía la firma. Verificado: firma no en el bloque (0 líneas con jueces en 709 líneas), linea_fin_real=20094 corta justo antes de la firma en L20095+.

Segundo hallazgo: 340_p1213 tenía mecanismo idéntico (token "Ricardo" matcheaba en "Ricardo Luis Lorenzetti —").

### H074-02 — B094: guarda firma en Pista 1 forward

Fix: en `detectar_fin_real`, Pista 1 forward, agregar guarda: si la línea matchea `linea_es_firma_de_juez` Y tiene raya (— o –), skip y seguir buscando. Raya obligatoria para no filtrar carátulas de jueces-parte (Boggiano, Moliné — 0 FP verificados en 5862 casos, solo 3 carátulas matchean JUECES_CONOCIDOS y ninguna tiene raya).

Validación: diff 5862 casos, 8 cambios, todos en 2 casos recuperados (329_p1881, 340_p1213). sin_firma 17→15. 0 regresiones.

Commit: `H074: B094 aplicado — guarda firma Pista 1, sin_firma 17→15`.

### H074-03 — B089: diagnóstico de ancla_catalogo

428 casos con `ancla_catalogo` analizados. Desglose de causa raíz:
- 318 (74%): token con tilde (Juárez, Martínez, Díaz) vs .md ALL CAPS sin tildes (JUAREZ). `refinar_inicio_por_titulo` no normalizaba tildes — mismo bug que B071 resolvió para Pista 1.
- 59: token sin tilde que no matchea (residuo >50 líneas o nombre distinto).
- 51: token corto (<4 chars, nombres anonimizados N.N., R.M., etc.).

### H074-04 — B089: fix _strip_accents + guarda cola

Fix: agregar `_strip_accents` a `refinar_inicio_por_titulo` (token y línea) y a B074 `_li_for_dfr`. Guarda adicional: skip match en últimas 5 líneas del bloque (protege contra token que matchea carátula del caso siguiente, caso testigo: 329_p2218 "Bergés").

Primer run sin guarda cola: 3 regresiones identificadas. Diagnóstico con script `diag_b089_regresiones.py`:
- 329_p2218: token "Berges" matcheaba en bloque[17]/18 (última línea = carátula del siguiente). → guarda cola resuelve.
- 329_p326, 329_p5151: trim correcto, datos previos eran corrupción del caso anterior. No son regresiones.

Segundo run con guarda cola: 329_p2218 protegido. 490 casos afectados, 996 campos cambiados (mayoría word_count). Diff validado contra baseline.

### H074 — Estado final

- **Corpus:** 5862 casos (5668 fallos + 34 sumario_editorial + 160 sumario_con_link).
- **Votos:** 27465 filas.
- **sin_firma:** 16 / 5668 fallos (0.3%). Cobertura firma: 99.7%.
- **sin_dispositivo:** 25.
- **ancla_catalogo:** 123 (era 428).
- **ok (status_loc):** 5451 (era 5080).
- **Trayectoria sin_firma:** 813→…→33→31→17→15→16.

**Outcomes corregidos (B089):** ~15 casos con por_ello_text del caso anterior → outcome correcto. competencia -6, desestima -6, inadmisible_280 +6, procedente +3, originaria +1.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27465 filas.
- `output/parser/csjn_casos_zonas.csv` — 141192 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Commits:** 2.
1. `H074: B094 aplicado — guarda firma Pista 1, sin_firma 17→15`
2. `H074: B089 — trim pre-caratula con _strip_accents, ancla_catalogo 428→123, votos +17`

## H075 — B095 Pista 5: prefix match + fullname+inverted para ancla_catalogo (2026-05-25)

**Objetivo:** reducir ancla_catalogo atacando tokens cortos (<4 chars) y abreviaciones catálogo→.md.

### H075-01 — Diagnóstico B089 residual (71 token≥4)

Clasificación de los 71 ancla_catalogo con token ≥4 chars que no matchean:
- H1 (prefix sin word boundary): 6 — catálogo abrevia (Transp→TRANSPORTES, Camnasi→CAMNASIO, Schr→SCHRÖDER, Bank→BANKBOSTON, Pers→PERSONAL, Serv→Servicios).
- H2 (después de línea 50): 25 — token existe pero más allá de MAX_LINEAS_BUSQUEDA_TITULO.
- H3 (guarda últimas 5 correcta): 13 — bloques cortos, guarda protege correctamente.
- H4 (ausente total): 27 — nombre distinto catálogo→.md (OCR/typo: Hojean→HOJMAN, Jiménez→GIMENEZ, SOMOSA→SOMISA, GCBA→GOBIERNO DE LA CIUDAD).

Scripts: `scripts/auditoria/H075/diag_b095_token_corto.py`, `diag_b095_token_largo.py`.

### H075-02 — B095 Pista 5 H1: prefix match (6 casos)

Segundo paso en `refinar_inicio_por_titulo`: si word-boundary (`\b`+token+`\b`) falla, probar prefix match (`\b`+token sin trailing `\b`). Solo corre si paso 1 no matcheó. 6 casos rescatados. ancla_catalogo 122→116. Zonas -17 (residuo eliminado). Votos invariante. Commit `ff7b765`.

### H075-03 — Diagnóstico B095 token corto (51 casos)

Inspección de las carátulas reales en los .md fuente. Hallazgo clave: las iniciales anonimizadas están **invertidas** entre catálogo ("P., S. D." = apellido, nombre) y .md ("S. D. P." = nombre apellido). Los 15 casos que matcheaban con fullname directo eran palindrómicos ("N. N.") o sin coma ("M. D. H. c/ M. B. M. F.").

### H075-04 — B095 Pista 5b: fullname + inverted (41 casos)

Helpers `_build_fullname_variants` (genera forma directa + invertida vía `split(",",1)` + swap) y `_build_flexible_pattern` (regex con espaciado variable). Para carátulas con "c/", invierte cada parte por separado. Corre solo cuando token <4 chars.

Validación: 41 casos rescatados. -2 votos: 329_p2133 (7→5) y 331_p68 (6→4) — confirmado con auditar_fallo que las firmas removidas pertenecían al caso anterior (Bernasconi, no D., J. A.; caso previo a J., L. L., no J., L. L.). Mejora de calidad, no regresión. ancla_catalogo 116→75. Zonas -120.

Spot-checks post-fix: 333_p1192 tiene residuo post-epílogo (B096 nuevo). 331_p466 tiene voto Argibay truncado (B097 nuevo). Ambos preexistentes, no causados por el fix.

### H075 — Estado final

- **Corpus:** 5862 casos (5669 fallos + 33 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 16 / 5669 fallos. Cobertura firma: 99.7%.
- **Votos:** 27463 filas.
- **Zonas:** 141055 segmentos.
- **ancla_catalogo:** 75 (trayectoria: ...428→123→122→116→75).
- **Trayectoria sin_firma:** ...33→31→17→15→16.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27463 filas.
- `output/parser/csjn_casos_zonas.csv` — 141055 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Scripts creados:** `scripts/auditoria/H075/` — `diag_b095_token_corto.py`, `diag_b095_token_largo.py`, `ver_caratulas_b095.py`.

**Commits:** 4 (diagnósticos, H1 prefix match, snapshot pre-5b, 5b fullname+inverted)

## H076 — Limpieza repo + M11 versionado + B095 Tier 4 (2026-05-26)

**Objetivo:** housekeeping del repo, versionar scripts canónicos, ampliar matching de refinar_inicio_por_titulo con guardas de Pista 1.

### H076-01 — Limpieza del repositorio

Scripts sueltos en raíz, scripts/pipeline/ y scripts/auditoria/ movidos a subdirectorios H0xx/ según sesión de origen (cruzado con BITACORA). Snapshots pre_* movidos de output/parser/ a archivo/data/. Scripts colados en output/ (conteo_aperturas_h051.py en output/mapa/, extraer_monstruos (1).py en output/diagnostico/) devueltos a scripts/auditoria/. Directorios vacíos (HB063, 041) eliminados. Nombres inconsistentes normalizados (H37→H037). directorio 069/ fusionado en H070/.

Resultado: raíz con solo 4 .md canónicos + config; pipeline con solo 5 scripts productivos; auditoria con solo auditar_fallo.py suelto + 24 subdirectorios de sesión.

### H076-02 — M11: versionar scripts canónicos

Script `agregar_version.py` agrega `__version__` después del docstring de 6 scripts canónicos. Idempotente. auditar_fallo.py ya tenía v1.0.0 con print propio.

Versiones iniciales: parser.py v18.0, parser_editorial.py v1.0, construir_catalogo.py v1.0, cruzar_catalogo_y_mapa.py v1.0, detectar_paginas.py v1.0. Print de versión agregado al bloque diagnóstico del parser.

Convención: minor sube .01 por sesión, major por cambio de arquitectura.

### H076-03 — B095 Tier 4: refinar_inicio con ventana ampliada y guardas

Diagnóstico previo (`diag_b095_ventana.py`): de 75 ancla_catalogo, solo 8 tienen token≥4 que matchea fuera de la ventana actual (>50 líneas). 5 safe con trim≤50%, 3 riesgosos.

Decisión de diseño: en vez de ampliar la ventana ciegamente, portar guardas de Pista 1 de detectar_fin_real a refinar_inicio_por_titulo. Guardas portadas: `_es_texto_corriente` (retry loop), stoplist con `segundo_token_de_caratula` confirmatorio, trim ≤50%. También fullname+inverted para TODOS los tokens (no solo <4) y "Vistos los autos" extendido a 100 líneas.

PoC inicial (poc_b095_tier4.py) mostró 24 rescates, pero 13 eran falsos positivos por bug en construcción del bloque (usaba linea_fin en vez de linea_fin_real). Corregido, el número real era 11 (8 T4a + 3 vistos).

Se patchó el parser directamente (no el PoC). Parser corrido con v18.01. Diff validado: 11 cambios en status_localizacion, 0 regresiones. 2 outcomes corregidos por eliminación de texto contaminante del caso anterior. 334_p471 (Morán) auditado manualmente — correcto: fallo corto de competencia con dictamen largo, el trim eliminó el caso anterior completo.

### H076 — Estado final

- **Corpus:** 5862 casos (5669 fallos + 33 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 16 / 5669 fallos (0.3%). Cobertura firma: 99.7%.
- **Sin dispositivo:** 25.
- **ancla_catalogo:** 64. Trayectoria: 428→123→122→116→75→64.
- **Votos:** 27463 filas.
- **Zonas:** 140956 segmentos.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27463 filas.
- `output/parser/csjn_casos_zonas.csv` — 140956 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Scripts creados:** `scripts/auditoria/H076/` — agregar_version.py, diag_b095_ventana.py, poc_b095_tier4.py, diff_h076.py, ver_cambios_h076.py, check_t1.py.

**Versiones de scripts canónicos:** parser.py v18.01, parser_editorial.py v1.0, construir_catalogo.py v1.0, cruzar_catalogo_y_mapa.py v1.0, detectar_paginas.py v1.0, auditar_fallo.py v1.0.0.

**Commits:** 3 (limpieza repo, M11 versionado, B095 Tier 4)..

## H077 — classify_outcome v14: rechaza + infinitivos + normalización (2026-05-26)

**Objetivo:** reducir el outcome "otro" (27.5% del corpus) mediante diagnóstico
de patrones dispositivos no capturados y mejora de classify_outcome.

### H077-01 — Diagnóstico del outcome "otro" (1562 casos)

Descomposición completa de los 1562 fallos clasificados como "otro".
Identificadas tres brechas principales:
1. **Rechazar no existía como pattern** — 213 casos sin captura.
2. **Formas infinitivas** ("el Tribunal resuelve: Confirmar/Desestimar/
   Hacer lugar/Declarar procedente") — 516 casos.
3. **Regex rotas por OCR** (double spaces, plurales, pronombres) — 49 casos.

Agrupados en tres tracks: Track 1 (mecánico, cero riesgo), Track 2
(taxonómico, requiere decisiones), Track 3 (variables nuevas).

### H077-02 — PoC classify_outcome v14

PoC v14a: 840 cambios pero 129 merit→merit por normalización whitespace
que cambia orden de match en dispositivos compuestos. Descartado.
PoC v14b: zona fallback intacta + patterns nuevos solo como fallbacks
después de los existentes. 610 cambios, 0 regresiones. Aprobado.
Whitespace normalization aplicada uniformemente a ambas zonas.

### H077-03 — Aplicación y validación

parser.py v18.01→v18.02. classify_outcome v13→v14. Cambios:
- Paso 0b: `re.sub(r"\s+", " ", text)` en por_ello_text y considerando_text.
- Outcome "rechaza" nuevo: formas directas + infinitivo.
- Fallbacks infinitivo: confirmar, desestimar, hacer lugar, declarar procedente.
- Fallbacks plurales/pronombres: "se la desestima", "se declaran procedentes",
  "se confirman".
- Fallback competencia: "se declara competente", "declararse incompetente".
- "rechaza" agregado a MERIT_OUTCOMES.

Resultados parser completo:
- otro: 1562→893 (−669, de 27.5% a 15.7%)
- rechaza: 0→216 (nuevo)
- hace_lugar: 1102→1367 (+265)
- confirma: 237→327 (+90)
- desestima: 476→541 (+65)
- procedente: 656→697 (+41)
- competencia: 571→603 (+32)
- inadmisible_280: 267→245 (−22, ahora merit outcomes skip Paso 3)
- revoca: 360→340 (−20, dispositivos compuestos)
- sin_firma: 16, sin_dispositivo: 25, ancla_catalogo: 64 (sin cambio)

### H077-04 — Diagnóstico taxonómico con Anuario CSJN 2025

Comparación de taxonomía del parser con Anuario Estadístico CSJN 2025
(Oficina de Estadísticas). Hallazgos clave:
- "Deja sin efecto" es categoría separada de "Revoca" en estadística oficial
  (36.32% vs 51.61% de recursos admitidos). 85 casos detectados en nuestro
  corpus dentro de "otro".
- "Rechaza" existe como categoría separada de "Desestima" → validado.
- CSJN distingue "Art. 14 ley 48" (67.29%) de "Sentencia Arbitraria" (32.71%)
  en cuestiones federales. Variable futura: tipo_cuestion_federal.
- Queja vs. Concedido trackeado oficialmente (77.9% vs 21.6%). Variables
  futuras: es_queja, queja_resultado (2181 fallos, 38.5%).
- Causales de inadmisibilidad más granulares que nuestro 280/ac4.

### H077 — Estado final

- **Corpus:** 5862 casos (5669 fallos + 33 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 16 / 5669 fallos (0.3%). Cobertura firma: 99.7%.
- **Sin dispositivo:** 25.
- **Outcome "otro":** 893 / 5669 fallos (15.7%). Trayectoria: 27.5%→15.7%.
- **Votos:** 27463 filas.
- **Ancla catálogo:** 64.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27463 filas.
- `output/parser/csjn_casos_zonas.csv` — 140956 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Versiones:** parser.py v18.02.

**Commits:** 2 (parser v18.02 + outputs; docs).

## H078 — Variables nuevas: es_queja, queja_resultado, tipo_cuestion_federal (2026-05-26)

**Objetivo:** implementar tres columnas analíticas nuevas en csjn_casos.csv — vía de acceso (queja vs REF concedido), resultado de la queja, y tipo de cuestión federal (arbitrariedad vs art. 14 ley 48).

### H078-01 — es_queja + queja_resultado

PoC sobre por_ello_text (truncado a 300 chars en CSV). Detección por sinónimos: "queja" / "recurso de hecho" / "presentación directa". Cascada de 12 patterns para queja_resultado: hace_lugar, desestima, procedente, admisible, rechaza, inadmisible, agreguese, desistida, abstracta, improcedente, nula, suspendida.

PoC en CSV: 1951 quejas detectadas (34.4%), cobertura resultado 98.4%. Run completo (por_ello_text sin truncar): 1993 (35.2%), cobertura 98.2% (36 sin_clasificar). Los 42 adicionales son cases donde el pattern matchea en chars 301+.

Decisión de diseño: normalización interna en classify_queja() con _unhyphenate + whitespace collapse, igual que classify_outcome.

### H078-02 — tipo_cuestion_federal

Iteración 1 (considerando_text solo): 772/5669 detectados (13.6%). Cobertura muy baja.

Exploración de casos reales (tomos 348 y 330 subidos): el considerando de la Corte frecuentemente dice solo "razones de brevedad" (27.5% de merit decisions). La señal real está en el **sumario editorial** — los headers de la Secretaría de Jurisprudencia clasifican explícitamente:
- Tomo 330 (viejo): `RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Sentencias arbitrarias.` / `... Cuestión federal.`
- Tomo 348 (nuevo): `SENTENCIA ARBITRARIA` como header standalone.

Iteración 2 (sumario + fallback considerando): extracción de texto pre-apertura del bloque (`bloque[0:apertura_rel]`). Detección primaria en sumario (RE_SUMARIO_ARBITRARIEDAD, RE_SUMARIO_CUESTION_FEDERAL), fallback a considerando_text.

Run completo: 2843/5669 (50.1%). cuestion_federal 1291, arbitrariedad 882, mixto 670, sin_dato 2826. Los sin_dato incluyen competencia, originaria, extradición, etc. donde la distinción no aplica.

Nota conceptual (Guillermo): tipo_cuestion_federal es la **vía procesal de acceso** al REF, no un resultado. Ortogonal al outcome.

### H078 — Estado final

- **Corpus:** 5862 casos (5669 fallos + 33 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 16 / 5669 fallos (0.3%). Cobertura firma: 99.7%.
- **Votos:** 27463 filas.

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas (3 columnas nuevas: es_queja, queja_resultado, tipo_cuestion_federal).
- `output/parser/csjn_casos_votos.csv` — 27463 filas.
- `output/parser/csjn_casos_zonas.csv` — 140956 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Commits:** 2 (snapshot pre-H078, feature v18.03).

## H079 — Diagnóstico tipo_cuestion_federal + outcome deja_sin_efecto (2026-05-27)

**Objetivo:** validar la variable tipo_cuestion_federal (H078) y agregar outcome deja_sin_efecto al parser.

### H079-01 — Diagnóstico tipo_cuestion_federal (A+B)

**A — Cobertura per-tomo:** 50.1% global (2843/5669), rango 38.7% (T339) a 74.2% (T347). Sin caídas abruptas que indiquen formato editorial no detectado. Fuente sumario editorial ~72% consistente en todos los tomos, sin cambio de régimen.

**B — Validación por muestreo:** 30 casos auditados (10 arbitrariedad, 10 cuestion_federal, 10 mixto): 0 falsos positivos. Mixto genuino: 486/670 clasificados solo por sumario editorial. Proporción mixto sube de ~8% a ~19% en tomos tardíos (341-349), consistente con ratio de fuente. 74 competencia/originaria con tipo_cuestion_federal: plausibles. 513 quejas sin dato: genuino (resoluciones cortas que remiten al Procurador).

**Conclusión:** variable sólida, sin ajustes necesarios.

### H079-02 — Outcome deja_sin_efecto + procedente regex

Análisis de 893 "otro": 128 contienen "deja sin efecto" en por_ello_text. Desglose: 41 con "procedente" (gap regex), 48 con "admisible" sin procedente, 39 puro deja_sin_efecto.

**PoC v1 (parser v18.04, regex procedente en zona alta):** 190 cambios, 54 regresiones — el regex expandido ("se declara formalmente procedente") en posición alta de la cascada pisaba revoca/confirma existentes. "Se declara formalmente procedente el REF y se revoca la sentencia" matcheaba procedente en vez de revoca.

**Decisión de diseño:** mover regex expandido a zona fallback (después de revoca, confirma, etc.). Así "se declara formalmente procedente y se revoca" mantiene revoca (outcome más informativo), y solo casos sin otro merit outcome se rescatan de "otro". Pregunta abierta: outcome como par gate+action (procedente + revoca) para la tesis.

**PoC v2 (regex en zona fallback):** 143 cambios, 0 regresiones reales.
- otro → deja_sin_efecto: 85
- otro → procedente: 51
- inadmisible_280 → procedente: 5 (mejoras: dispositivo dice procedente, considerando menciona 280 por otro agravio)
- inadmisible_280 → deja_sin_efecto: 2 (ídem)

Patterns agregados a OUTCOME_PATTERNS_DISPOSITIVO (zona fallback):
- Fix A1: `\bse\s+declara\s+(?:formalmente|parcialmente)\s+procedente\b`
- Fix A2: `\bprocedentes?\s+(?:el\s+recurso|los\s+recursos)` (aposición)
- Fix B: `(?:se\s+)?deja(?:r|n)?\s+sin\s+efecto` + `corresponde dejar sin efecto`

deja_sin_efecto agregado a ambos MERIT_OUTCOMES (classify_outcome e is_merit_decision).

### H079 — Estado final

- **Corpus:** 5862 casos (5669 fallos + 33 sumario_editorial + 160 sumario_con_link).
- **Sin firma:** 16 / 5669 fallos (0.3%). Cobertura firma: 99.7%.
- **Votos:** 27463 filas.
- **Outcome "otro":** 757 (era 893, -136).

**Outputs canónicos:**
- `output/parser/csjn_casos.csv` — 5862 filas.
- `output/parser/csjn_casos_votos.csv` — 27463 filas.
- `output/parser/csjn_casos_zonas.csv` — 140956 segmentos.
- `output/parser/csjn_casos_editorial.csv` — 151 secciones.

**Distribución de outcomes (H079, classify_outcome v14 + deja_sin_efecto):**

## H080 — Diagnóstico de tomos 335/336 y ruta de catálogo 336 (parqueada) (2026-05-28)

**Objetivo:** decidir cómo tratar los tomos 335/336 (digitalizados con Tesseract) y, si correspondía, incorporar 336.

### H080-01 — Diagnóstico refinado de 335/336
La prosa del cuerpo de ambos tomos está limpia (considerandos, "por ello", resúmenes editoriales, carátulas-en-cuerpo). El daño está localizado en el bloque de cierre de cada fallo (fecha + firmas), que en el PDF es imagen embebida (firma digital) y no texto. Esto explica sin_firma alto (62/207 en 335) y cuerpos vacíos (el parser usa fecha/firma como anclas). La hipótesis inicial de columnas entreveradas por Tesseract quedó refutada con datos: los índices entran en orden de lectura correcto.

### H080-02 — Ruta de índice 336 en construir_catalogo (v1.01)
336 no tiene índice de nombres canónico; solo un índice general alfabético por carátula, con header "Índice"/"Indice" suelto y sin ancla ": p.". Dos sub-formatos: 336.1 trailing ("Carátula. 448"), 336.2 con líderes de puntos ("Carátula s/ tipo. ... 1477"). Se diseñó y validó una ruta de fallback (detección de header title-case + dos extractores, guarda "canónico primero"). Validación: 336 = 138 entradas (62 vol.1 + 76 vol.2), 329-349 idénticos al baseline, catálogo 6117→6255. Sin trampa de números embebidos (TF/dto/resol).

### H080-03 — Decisión: parquear 335/336
Se decidió no perseguir la corrupción de Tesseract con el parser (las firmas son imagen, no hay texto que recuperar). Vía de solución: re-escanear solo las páginas de cierre del tomo papel para los fallos rotos. Worklist generado: 335_firmas_a_escanear.csv (62 fallos, página inicio/cierre). main revertido al baseline limpio pre-335/336 (056c31e); la ruta 336 queda como archivo y en branch tomos-335-336, sin mergear.

### H080-04 — Infra: Google Drive corrompía el repo
El repo estaba sincronizado por Google Drive, que lockeaba .git/objects y disparaba el flood de gc (deletion failed y/n) más miles de temporales .tmp.driveupload trackeados. Se cerró Drive, se puso exclusión de Defender, gc.auto 0, se limpió .tmp.driveupload y se agregó al .gitignore. Repo verificado sano (fsck limpio, count 0). Pendiente ideal: mover el repo fuera de toda carpeta sincronizada.

### H080 — Estado final
- **main:** baseline limpio pre-tomos 335/336 (056c31e). Corpus ~5862, sin_firma 16, parser v18.05.
- **Parqueado:** construir_catalogo v1.01 (ruta 336, validada) como archivo + branch tomos-335-336; worklist de firmas 335 (62 fallos).

**Versiones:** parser.py v18.05 (sin cambios). construir_catalogo.py v1.01 (parqueado, no en main).

**Commits:** snapshot pre-H080, branch tomos-335-336 (experimento 336), reset de main a 056c31e, housekeeping gitignore/Drive.

## H083 — Módulo estadisticas/: extractor de tableros Tableau del Anuario CSJN (2026-05-29)

**Objetivo:** acceder a los datos del Anuario Estadístico de la CSJN (publicados solo como tableros Tableau, sin exportación de datos) para comparar contra el corpus y explorar el cruce voto × juez. Frente analítico: NO toca pipeline, parser ni outputs canónicos.

### H083-01 — Tablas de referencia del Anuario (PDF)

Los PDF de los Anuarios 2024 y 2025 sí traen las marginales. Se extrajeron tres CSV de referencia a `estadisticas/`: `anuario_csjn_por_secretaria.csv` (ingresos+resueltos, 10 secretarías, 2024-25), `anuario_csjn_por_materia.csv` (resueltos, 2024-25), `anuario_csjn_admitidos_por_materia.csv` (2024-25). Hallazgo de los tres universos: la composición cambia drásticamente según se mire ingresos (previsional ~70%), resueltos (~35-54%) o admitidos (laboral 48.7% en 2024, previsional 53% en 2025 — la composición de admitidos es volátil año a año). El universo más comparable al corpus (fallos publicados) es admitidos, pero no anclar a un solo año.

### H083-02 — Extractor Playwright de los tableros (sortea el AWS WAF)

Tableau Public de la CSJN está detrás de AWS WAF (CAPTCHA): requests/python no pasa (410/CAPTCHA), exportación de datos deshabilitada (solo PDF/imagen). Solución: `estadisticas/export_tableau_playwright.py` — navegador real (Playwright Chromium) que pasa el WAF al renderizar; captura el bootstrap real en vuelo (evita el 410 de re-disparar sesión); recorre los story points clickeando cada tab y captura la respuesta de `set-active-story-point`; parsea entrando al story point activo dentro del flipboard y tomando los `dataSegments` de la respuesta del comando (no del bootstrap, que viene con secondaryInfo vacío). Reescrito a loop sobre 4 tableros (ingresos/resueltos × 2024/2025), salida a `estadisticas/output_tableau/<viz>/`. Resueltos 2025 extraído completo: 57 hojas reales. Los otros 3 tableros quedan pendientes de correr (un comando).

### H083-03 — Cruce voto × ministro 2025 y hallazgo del 280 de Lorenzetti

Del tab "Tipos de voto según Juez" se extrajo el cruce (`estadisticas/cruce_voto_x_ministro_2025.csv`). Conformación de ministros: unanimidad casi idéntica entre los tres estables (~12.960), pero el tramo no-unánime se bifurca: Rosatti y Rosenkrantz votan conjunto (13.345 / 12.893), Lorenzetti vota propio (12.899). Lorenzetti concentra 95.6% de los votos propios de ministros. Su voto propio (12.899) ≈ total art. 280 (12.546). Las capturas filtradas por secretaría muestran ese voto propio repartido transversalmente, no concentrado en previsional. Lectura: Lorenzetti suscribe su versión individual del 280 a lo largo de las materias; los otros dos lo firman conjunto. Diferencia de forma de suscripción sobre acto impersonal, no fragmentación doctrinaria. Material para H1 (postura estable del ministro, no asignación) y H3 (matiza la "proliferación de votos propios" como artefacto del 280).

### H083-04 — Motor de filtros: capturador pasivo

Para el cruce voto × juez × secretaría (que el tablero no publica como hoja) se necesita filtrar. Lanzar `categorical-filter` por API desde Python da 410 (sesión consumida); solo funciona el clic real en la UI. Se descartó el motor automático y se usó un capturador pasivo (`capturador_pasivo.py`): el navegador escucha mientras el usuario navega y toca filtros a mano, y graba cada respuesta. Funcionó: 162 acciones capturadas, 16 con el cruce filtrado por secretaría. Pendiente: etiquetar qué secretaría es cada captura (el filtersJson de la respuesta no expone el estado de selección). Scripts de sonda/motor borrados en limpieza.

### H083 — Estado final

- **Pipeline:** sin cambios. main sigue en baseline H080 (056c31e), corpus ~5862, parser v18.05.
- **Módulo nuevo `estadisticas/`:** `export_tableau_playwright.py` (extractor 4 tableros), 3 CSV de referencia del Anuario, `cruce_voto_x_ministro_2025.csv`, `output_tableau/resueltos_2025/` (57 hojas).
- **Decisión H082 (variable materia) sigue postergada.** Esta sesión fue de acceso a datos externos, no del frente del corpus.

**Versiones:** sin cambios en scripts canónicos del pipeline.

**Commits:** módulo estadisticas/ nuevo (extractor + CSV de referencia + cruce). Sin commits al pipeline.

## H084 — Diagnóstico de deuda estructural + harness de regresión del parser (2026-05-29)

**Objetivo:** diagnóstico-primero sobre el corpus estable (parser v18.05, baseline bcc143f); recomendar frente fundado en lectura de código y datos reales, y —si correspondía— dar el primer paso del frente elegido sin tocar lógica.

### H084-01 — Diagnóstico (set mínimo: parser + DEUDA + BITACORA + csjn_casos.csv + árbol)
Lectura de parser.py (3638 líneas) y del CSV real (5862 casos). Deuda estructural confirmada: procesar_archivo es la función monstruo (757 líneas, 2542–3299: localización + sumarios + dictamen + cascada de dispositivo Tier 1→2→3→3b→4, cada tier de una sesión distinta); es_originaria 212 líneas; duplicación parser↔auditor sin resolver (M07/M08). El parser core no tenía tests: scripts/tests/ cubría los scripts chicos, no parser.py ni auditar_fallo.py; csjn_casos_BASELINE_H079.csv existía suelto, sin harness. Hallazgos de datos: dictamen_presente con 3 valores True/False/'0' (3400/2269/193, los '0' son los 193 sumarios → B037); 58 outcome=originaria con is_originaria=0 (50 sin_marcador, 8 apelado_detectado → valida frente D); outcome=otro 688 (11.7%). Confirmado main = 5862 / 4 CSV de parser.py.

### H084-02 — Recomendación: frente A (refacción REE), primer paso = red de regresión
Con el corpus estable, consolidar deuda estructural antes de seguir sumando variables. Restricción REE innegociable: ningún refactor se mergea sin outputs idénticos. Como no había red, el primer paso obligado es construirla, no tocar lógica. A y B (materia) no compiten a largo plazo: refactorizar primero abarata agregar materia sobre código limpio.

### H084-03 — Harness de regresión (M12)
`scripts/tests/check_regresion.py`, dos modos. `--make-golden`: corre el parser a un temporal y congela los 4 CSV (casos/votos/zonas/editorial) en scripts/tests/golden/. Default: corre a otro temporal y diffea contra golden (SHA256 + diff posicional celda por celda; reporta fila/caso_id/columna), sale 1 si cambia una celda. Nunca pisa output/parser/ productivo. Invoca con cwd=scripts/pipeline para resolver el import de parser_editorial. Validación: golden congelado sobre bcc143f, check inmediato = [CLEAN] (4/4 idénticos, el golden se reproduce a sí mismo). Alcance: 4 CSV de parser.py; indice_partes (parser_editorial) y el pipeline upstream quedan fuera (inputs congelados).

### H084-04 — Housekeeping (snapshots M02)
De los tres snapshots pendientes de M02, dos ya no existen; queda solo archivo/snapshots_ad_hoc/pre_fix_xii_20260503_1308 (72 archivos, 23.71 MB, estado pre-B013/"Bug XII"). Untracked (git ls-files = 0). NO borrado: al no estar en git requiere verificar que su contenido sea copia de algo commiteado antes de eliminar. Parqueado.

### H084 — Estado final
- **Corpus:** 5862 casos (5669 fallos + 160 sumario_con_link + 33 sumario_editorial). Sin firma: 16/5669. Pipeline intacto.
- **Parser:** v18.05 (sin cambios).
- **Votos / zonas / editorial:** sin cambios (no se tocó pipeline).

**Outputs canónicos:** sin cambios. El harness corre a temporal; el golden los duplica byte-a-byte (git deduplica blobs idénticos).

**Scripts creados:** `scripts/tests/check_regresion.py` (+ `scripts/tests/golden/` con los 4 CSV).

**Commits:** H084 — harness + golden (red para refactor); docs (BITACORA + DEUDA M12). Push de bcc143f (H083) pendiente desde H083.

**Versiones:** sin cambios en scripts canónicos del pipeline (parser.py v18.05). Nuevo: check_regresion.py (infra de tests, no canónico).