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
