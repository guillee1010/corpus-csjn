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