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
