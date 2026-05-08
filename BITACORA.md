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
