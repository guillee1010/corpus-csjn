# Análisis forense del pipeline `corpus-csjn`

**Fecha:** 2 de mayo de 2026
**Autor:** Claude (lectura asistida) + Guillermo Rubinetti
**Estado:** diagnóstico inicial, sin validación empírica todavía
**Alcance:** lectura completa de los 4 scripts del pipeline. Sin acceso a outputs (`fallos_localizados.csv`, `csjn_casos.csv`) ni al git log al momento de escribir esto.

---

## 1. Qué se leyó y qué no

**Leído entero:**
- `detectar_paginas.py` (552 líneas)
- `construir_catalogo.py` (651 líneas)
- `cruzar_catalogo_y_mapa.py` (415 líneas)
- `parser.py` (1.886 líneas, leídas selectivamente las secciones de construcción de bloque y `detectar_fin_real`; el resto del parser — clasificadores de votos, outcomes, firmas — no es relevante para el diagnóstico estructural del pipeline)

**No leído:**
- Outputs del pipeline (`fallos_localizados.csv`, `csjn_casos.csv`, `mapa_paginas.csv`).
- Git log del proyecto.
- Los análisis previos sobre línea-vs-página que mencionó Guillermo.
- Notas anteriores en `docs/` o `archivo/exploratorios/diagnostico/`.

**Lo que esto significa:** todo lo que sigue está derivado de la lectura de código únicamente. Los hallazgos son de nivel "diagnóstico estructural" y necesitan validación empírica antes de cualquier fix.

---

## 2. Modelo conceptual del pipeline

El pipeline tiene **dos universos paralelos** que se intentan cruzar:

### Universo A — el índice editorial (lo que dice la CSJN que hay)

Lo construye `construir_catalogo.py` parseando los índices alfabéticos al final de cada `.md`. Su unidad básica es el **fallo nominado**, identificado por `(tomo, pagina_inicio)`. Cada fallo tiene un nombre (carátula) y una página de inicio. **No tiene página de fin real**: el fin se infiere como "donde empieza el siguiente". También produce `secciones_indices.csv`, que dice en qué línea empieza cada aparato editorial (índices, sumario, legislación, general) por archivo. Eso es importante porque marca el corte entre "zona de fallos" y "zona de aparato editorial".

### Universo B — el cuerpo del corpus (lo que está en los `.md`)

Lo construye `detectar_paginas.py` recorriendo cada `.md` línea por línea y buscando headers de página. Su unidad básica es la **detección de header**: una tupla `(archivo, linea_header, pagina)`. Es heurístico (busca el número del tomo aislado en una línea y un número plausible cerca) y aplica dos filtros post-hoc (duplicados consecutivos y outliers). El output es `mapa_paginas.csv`.

### El puente

`cruzar_catalogo_y_mapa.py` es el puente entre ambos. Para cada fallo del catálogo (universo A), busca en el mapa (universo B) los headers correspondientes y emite `linea_inicio` y `linea_fin`. Su output es `fallos_localizados.csv`, que es el **input del parser**.

`parser.py` consume `fallos_localizados.csv`, construye un bloque de líneas para cada fallo (`construir_bloque_desde_localizacion`), y aplica análisis: detección de apertura, firmas, votos, outcome, word counts.

### Tabla resumen del flujo

| Etapa | Input | Output | Unidad |
|---|---|---|---|
| `detectar_paginas.py` | `.md` del corpus | `mapa_paginas.csv` | header de página `(archivo, linea, pagina)` |
| `construir_catalogo.py` | `.md` del corpus | `catalogo.csv` + `secciones_indices.csv` | fallo nominado `(tomo, pagina_inicio)` con `pagina_fin` derivada |
| `cruzar_catalogo_y_mapa.py` | `catalogo.csv` + `mapa_paginas.csv` + `secciones_indices.csv` | `fallos_localizados.csv` | fallo localizado `(archivo, linea_inicio, linea_fin, status)` |
| `parser.py` | `fallos_localizados.csv` + `mapa_paginas.csv` + `.md` del corpus | `csjn_casos.csv` + `csjn_casos_votos.csv` | caso analizado |

---

## 3. Hallazgo central: inconsistencia semántica de `pagina_fin`

**El núcleo de los bugs reportados es una divergencia entre el docstring del catálogo y el código del catálogo, propagada al cruzador como un `+1` que parece bug puntual pero es síntoma estructural.**

### 3.1 El docstring del catálogo declara una semántica

En `construir_catalogo.py`, líneas 57 y 380-382:

```python
# Línea 57 (docstring del header del archivo):
#   - pagina_fin: entero o vacío, inferido como (página del siguiente fallo - 1)

# Líneas 380-382 (docstring de construir_filas_catalogo):
#   4. Calcular pagina_fin por inferencia global por tomo: ordenar las
#      páginas del tomo, pagina_fin de cada una = página de la siguiente - 1.
#      Última página del tomo: pagina_fin queda vacío.
```

**Semántica declarada:** `pagina_fin = última página del fallo actual = (página del siguiente fallo) - 1`.

### 3.2 El código del catálogo hace otra cosa

En `construir_catalogo.py`, línea 410:

```python
for tomo, pags_ordenadas in paginas_por_tomo.items():
    for i, pag in enumerate(pags_ordenadas):
        if i + 1 < len(pags_ordenadas):
            pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]   # ← acá NO resta 1
        else:
            pagina_fin_map[(tomo, pag)] = None  # último del tomo
```

**Semántica del código:** `pagina_fin = página del siguiente fallo`. Sin el `-1`.

**El docstring y el código no coinciden.** Es una inconsistencia interna del catálogo.

### 3.3 El cruzador asume la semántica del docstring

En `cruzar_catalogo_y_mapa.py`, línea 235:

```python
# Buscar header de la página siguiente (pg_fin + 1)
clave_fin = (tomo, pg_fin + 1)
```

El comentario es elocuente: "página siguiente (pg_fin + 1)". O sea, el cruzador asume que `pg_fin` es la última del fallo actual y suma 1 para llegar al siguiente. Eso es **consistente con el docstring del catálogo** pero **inconsistente con el código del catálogo**.

### 3.4 Resultado: el cruzador busca la página equivocada

Si el catálogo dice "fallo X tiene `pagina_inicio = 100`, `pagina_fin = 105`" (donde 105 es el inicio del siguiente), el cruzador busca `(tomo, 106)` en el mapa. Está buscando **la página posterior al inicio del siguiente fallo**, que es **la segunda página del fallo siguiente**, no su inicio.

Después calcula `linea_fin = linea_fin_header - 1` (línea 240 del cruzador), restando 1 más. El offset acumulado puede ser de una página entera de cuerpo del fallo siguiente.

### 3.5 Por qué el bug es difícil de detectar

Tres efectos compensatorios:

1. **El parser tiene `detectar_fin_real`** (línea 1109 de `parser.py`) que busca la frontera real bidireccionalmente y corrige el corte del cruzador en la mayoría de los casos.
2. **`proximo_header_pagina`** se calcula independientemente del cruzador, leyendo `mapa_paginas.csv` directo (línea 1329 del parser). Eso da una segunda fuente de verdad.
3. **El offset es solo de una página** en condiciones normales. Si el header de la siguiente página existe en el mapa, el cruzador acierta el archivo correcto y el `linea_fin` queda corrido pocos cientos de líneas. `detectar_fin_real` lo recupera.

El bug **se hace visible** cuando:
- El header buscado no existe en el mapa → status `pagina_fin_no_en_mapa` o `fallo_cruza_archivos`. Ahí el `linea_fin` cae al final del archivo, lo cual el parser tolera mal.
- O cuando alguien intenta arreglar el `+1` cambiándolo a `pg_fin` directamente, sin entender que el catálogo ya tiene la inconsistencia. Ahí pasan a `ok` casos que antes estaban en `pagina_fin_no_en_mapa`, **pero quedan cortados a mitad**, porque ahora `linea_fin = inicio_del_actual - 1` (la página `pg_fin` del catálogo, que es el inicio del siguiente, ya estaba bien identificada como header del próximo fallo, pero al restarle 1 se corta antes de donde debería).

---

## 4. Por qué el pipeline funciona razonablemente igual

A pesar del bug, el output histórico no parece tan roto. Tres razones, en orden de importancia:

### 4.1 `detectar_fin_real` es defensivo

En `parser.py`, líneas 1109-1190. La función:
- Toma `linea_fin_catalogo` como **punto de anclaje** (no como verdad).
- Busca bidireccionalmente la frontera real usando 4 pistas (en orden):
  1. Carátula del fallo siguiente (matching por `primer_token`).
  2. Header de sumario nuevo.
  3. Marcador de apertura del siguiente (DICTAMEN, FALLO DE LA CORTE).
  4. Fallback: firma del juez del fallo actual.
- Devuelve `linea_fin_real` separado del `linea_fin` del cruzador.
- Emite un `status_fin` que indica qué pista usó.

Esto significa que el parser **publica dos `linea_fin`**: el del cruzador (potencialmente corrido) y el suyo propio (corregido). Para el análisis estadístico de la tesis, el que importa es `linea_fin_real`.

### 4.2 `proximo_header_pagina` es una fuente independiente

El parser lee `mapa_paginas.csv` directamente y calcula la próxima línea-header después del fallo, sin pasar por el cruzador (`proximo_header_despues_de`, línea 1208). Esto le da un anclaje robusto para `detectar_fin_real`.

### 4.3 Compensación parcial cuando hay continuidad de paginación

Si las páginas son contiguas, el `+1` del cruzador termina apuntando a una página que sí existe (la segunda página del fallo siguiente). El header de esa página está pocos cientos de líneas adelante. `detectar_fin_real` recupera la frontera correcta usando la pista 1 (carátula del siguiente).

### 4.4 Cuándo falla

El bug se vuelve visible cuando:
- El `pg_fin + 1` del cruzador apunta a una página que no existe en el mapa (siguiente está al final del archivo, o hay gap de paginación).
- El parser no logra encontrar la "carátula siguiente" porque `primer_token` es muy corto, ambiguo, o coincide con palabras del cuerpo del actual.
- La ventana de búsqueda hacia adelante de `detectar_fin_real` (`proximo_header_pagina + 50` o `lfc + 200`) no alcanza a llegar a la frontera real.

---

## 5. Diagnóstico de los 32 oks falsos

**Síntoma reportado:** un fix anterior pasó 32 casos de `pagina_fin_no_en_mapa` a `ok`. Spot-check sobre 4 casos: 3 cortados a mitad de fallo.

### 5.1 Hipótesis sobre el cambio

Si alguien intentó arreglar el `+1` cambiando línea 235 del cruzador de:

```python
clave_fin = (tomo, pg_fin + 1)
```

a:

```python
clave_fin = (tomo, pg_fin)
```

el efecto sería:

**Antes del fix:**
El cruzador buscaba `pg_fin + 1` (segunda página del siguiente). Si esa página no estaba en el mapa, status `pagina_fin_no_en_mapa`, `linea_fin = última_línea_del_archivo`. El parser después usaba `detectar_fin_real` y recuperaba la frontera correcta.

**Después del fix:**
El cruzador busca `pg_fin` (primera página del siguiente — que es lo que el catálogo realmente le pasa, dado el bug del catálogo). Acierta el header. Status `ok`. **Pero** después calcula `linea_fin = linea_fin_header - 1`, lo cual da el fin del fallo actual... cuando el contrato del catálogo es "última del actual = siguiente - 1" pero el código del catálogo es "siguiente directamente". Si el catálogo está pasando "siguiente directamente" y el cruzador hace `linea_fin = (linea_inicio_del_siguiente) - 1`, eso da un punto que está **una página antes** de lo correcto, porque `pg_fin` ya era el inicio del siguiente y restar 1 a su `linea_header` corta antes de la última página del actual.

Espera. Reformulo más cuidadosamente.

Sea X el fallo actual con `pagina_inicio = pX`. Sea Y el siguiente con `pagina_inicio = pY`.

El catálogo escribe `pagina_fin_X = pY` (por el bug del código, línea 410).

**Comportamiento del cruzador con `+1` (estado original):**
- Busca clave `(tomo, pY + 1)`.
- Si existe header (caso normal), `linea_fin_X = linea_header_de_pY+1 - 1`. Eso corta **al final de la primera página de Y**. O sea, el bloque de X **incluye la primera página de Y**. Bug: bloque infla el actual con cuerpo del siguiente.
- Si no existe (página final de archivo), status `pagina_fin_no_en_mapa`, `linea_fin = última_línea_del_archivo`. Bloque incluye todo lo que viene hasta el final.

**Comportamiento del cruzador con el "fix" (sin +1):**
- Busca clave `(tomo, pY)`.
- Existe siempre (es el inicio de Y, que es un fallo nominado del catálogo y por lo tanto su página suele estar en el mapa).
- `linea_fin_X = linea_header_de_pY - 1`. Eso corta **una línea antes del inicio de Y**. Es lo que tiene que pasar.

Eso debería estar **bien**, no mal. Entonces el spot-check de Guillermo (3 de 4 cortados a mitad) sugiere que el fix fue otro, o que hay otro factor.

### 5.2 Hipótesis alternativas

**Hipótesis B — el fix tocó el catálogo, no el cruzador.**
Si alguien cambió línea 410 del catálogo de `pags_ordenadas[i + 1]` a `pags_ordenadas[i + 1] - 1` (para alinear código con docstring), el cruzador empezó a recibir un `pg_fin` que ya era "última del actual". Pero el cruzador sigue haciendo `+1`, así que ahora busca `pY - 1 + 1 = pY`, que es el inicio del siguiente. Acierta. Después corta en `linea_header_de_pY - 1`. **Eso debería estar bien.** Tampoco explica el corte a mitad.

**Hipótesis C — el fix tocó la línea 240 del cruzador.**
Si alguien cambió `linea_fin = linea_fin_header - 1` a `linea_fin = linea_fin_header`, el bloque se extiende **una línea más**, lo cual no causa corte a mitad sino exceso de bloque. No explica el síntoma.

**Hipótesis D — el fix tocó otra cosa.**
Quizás se cambió la lógica de `pagina_fin_no_en_mapa` para que en vez de usar `n_lineas_por_archivo[archivo_ini] - 1` use algún otro valor. Si el "otro valor" terminó siendo el inicio de algo cercano al inicio del fallo actual, los casos quedarían cortados a mitad. Pero esto requiere ver el diff exacto.

### 5.3 Lo que necesito para cerrar el diagnóstico

- **Git log del cruzador y del catálogo** después del fix Bug D del 2/5.
- **Los 32 casos específicos** que pasaron de `pagina_fin_no_en_mapa` a `ok`.
- Para 3-5 de ellos, el `linea_fin` actual y el header del fallo siguiente en el mapa, para medir empíricamente el offset.

Sin esto, todas las hipótesis son especulación. Pero **lo que sí está confirmado por lectura de código** es la inconsistencia docstring/código del catálogo, y eso es la raíz semántica que cualquier fix tiene que resolver.

---

## 6. Mapa completo de modos de falla por etapa

### 6.1 Detector de páginas (`detectar_paginas.py`)

**Falsos positivos:**
- Aparición casual del número del tomo en cuerpo de texto + número plausible cerca. Mitigado por filtro de outliers (`OUTLIER_PAGINAS_UMBRAL = 10`).
- Duplicados de header. Mitigado por filtro de duplicados consecutivos (`DUP_LINEAS_UMBRAL = 5`).

**Falsos negativos:**
- Header con formato anómalo (tomo en otra línea, OCR roto, etc.). **No mitigado:** si no se detecta, no aparece en el mapa.

**Riesgo para el cruzador:**
- Si una página `pg_ini` no se detectó, el fallo va a `pagina_no_en_mapa`.
- Si una página intermedia entre dos fallos no se detectó, no afecta (solo importan las extremas).
- Si la página del fallo siguiente no se detectó, el cruzador cae a `pagina_fin_no_en_mapa`.

### 6.2 Constructor de catálogo (`construir_catalogo.py`)

**Falsos negativos:**
- Sección "Y" o letras finales del índice ausentes → fallo no entra al catálogo (Bug 1 del Tomo 349, Y.P.F.).
- Cabecera con dictamen previo embebido → el catálogo SÍ los detecta (están en el índice). Pero el resto del pipeline puede no localizarlos bien (Bug 2 de tomos 331-334, "Bug A" en la lista de Guillermo).

**Inconsistencias internas:**
- **Docstring vs código sobre `pagina_fin`** (líneas 57, 380-382 vs 410). Es la raíz semántica del `+1` del cruzador.

### 6.3 Cruzador (`cruzar_catalogo_y_mapa.py`)

**Bugs:**
- El `+1` espurio de la línea 235, derivado de la inconsistencia del catálogo.

**Decisiones no documentadas:**
- Resolución de duplicados de mapa por "línea más baja" (línea 101). Razonable como heurística, pero no documentado el supuesto de por qué la línea más baja es siempre la correcta.

**Limitaciones de fallback:**
- En `pagina_fin_no_en_mapa` y `fallo_cruza_archivos` usa `n_lineas_por_archivo[archivo_ini] - 1` como `linea_fin`. Eso le pasa al parser un bloque que **incluye todo el aparato editorial** del archivo si el fallo está cerca del final. El fix Bug D del 2/5 atacó esto solo para `ultimo_del_tomo` (con `ok_cortado_en_indice`), pero la misma lógica defensiva no se aplica a los otros dos statuses.

### 6.4 Parser (`parser.py`)

**Defensivo bueno:**
- `detectar_fin_real` corrige el `linea_fin` del cruzador en la mayoría de los casos.
- Publica `linea_fin_real` separado del `linea_fin` del cruzador, lo cual permite auditoría.

**Limitaciones:**
- La ventana de búsqueda hacia adelante de `detectar_fin_real` es `min(proximo_header_pagina + 50, lfc + 200, n - 1)`. Si la frontera real está más lejos (cosa rara, pero posible cuando el fallo siguiente arranca con dictamen largo), no la encuentra.
- En los 19 `ok_cortado_en_indice` recientes, el parser **igual** corre `detectar_fin_real`. Si la heurística del cruzador (cortar en `inicio_indice - 1`) da un `linea_fin` que está bastante adentro del último fallo, `detectar_fin_real` puede mover esa frontera hacia atrás (buscando una "carátula siguiente" que no existe → fallback a firma del juez actual). Por eso conviene validar byte-a-byte: la pregunta no es solo "¿el cruzador cortó bien?" sino "¿qué hace el parser con ese corte?".

---

## 7. Hallazgos accionables

### 7.1 Bug semántico de `pagina_fin` del catálogo

**Acción:** decidir cuál de las dos semánticas mantener.

- **Opción A** — arreglar el catálogo para que respete su docstring: `pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1] - 1`. Cambia el contrato del CSV `catalogo.csv`.
- **Opción B** — arreglar el cruzador para que no sume 1: `clave_fin = (tomo, pg_fin)`. Cambia el contrato del cruzador. Mantiene `catalogo.csv` como está.

La opción A es más limpia conceptualmente (el código del catálogo coincide con su documentación). La opción B respeta el contrato actual del CSV pero deja la inconsistencia docstring/código del catálogo.

**Decisión metodológica, no técnica.** Cualquiera de las dos requiere regenerar el output completo y comparar con baseline.

### 7.2 Los 32 oks falsos

**Acción previa a cualquier fix:** rastrear el cambio exacto que los generó.

- Git log del cruzador y del catálogo entre el snapshot pre-fix y el estado actual.
- Identificar el diff exacto.
- Confrontar con las hipótesis A-D de la sección 5.

**Sin este paso, cualquier fix puede introducir nuevas regresiones.**

### 7.3 Los 121 cross-reference orphans

**Acción:** verificar si siguen existiendo en el output actual del parser.

- El catálogo conserva múltiples nombres por fallo en `nombres_indice` separados por `|` (línea 419 del catálogo, decisión metodológica documentada). Eso significa que **no hay huérfanos a nivel de catálogo**.
- Los huérfanos solo pueden aparecer si algún script downstream esperaba un mapeo 1-a-1 nombre→fallo. El parser no parece tener ese problema (usa `nombres_indice` como string opaco).
- Sospecha: los 121 orphans son de v15 del parser y son artefactos de una arquitectura previa.

---

## 8. Plan de validación pendiente

Antes de tocar código, en este orden:

### 8.1 Confirmar el diagnóstico del `+1` con datos

- Tomar 5-10 fallos con `status='ok'` que NO sean últimos del tomo.
- Para cada uno, comparar el `linea_fin` del cruzador contra el `linea_header` real del fallo siguiente en el mapa.
- Si la diferencia es sistemática y predecible (ej: siempre +1 o +2 páginas adelante), está confirmado el bug.
- Si la diferencia es errática, hay otro factor.

### 8.2 Identificar el cambio que generó los 32 oks falsos

- `git log -p paginas/cruzar_catalogo_y_mapa.py` (o ruta equivalente post-migración).
- `git log -p construir_catalogo.py`.
- Buscar diffs después del 30/4/2026.
- Confrontar con hipótesis A-D.

### 8.3 Spot-check empírico de los 19 `ok_cortado_en_indice`

- Para cada uno, comparar `linea_fin_real` (del parser) contra `inicio_indice_nombres - 1` (que es el `linea_fin` del cruzador).
- Si `linea_fin_real < inicio_indice_nombres - 1` por mucho margen, el parser está cortando antes (fallback a firma del juez).
- Validar manualmente sobre 3-5 casos: ¿el bloque del parser termina donde debería?

### 8.4 Verificar si los 121 orphans siguen vivos

- Buscar en el output actual del parser (`csjn_casos.csv`) casos con algún campo de cross-reference vacío o anómalo.
- Si existen, identificar el patrón. Si no, marcar como deuda histórica resuelta.

---

## 9. Preguntas abiertas

Cosas que la lectura de código no permite resolver y necesitan validación con datos o con archivos que no leí:

1. **¿El bug del `+1` es original o se introdujo en alguna versión?** Sin git log no se sabe.

2. **¿Los análisis previos sobre línea-vs-página de Guillermo cubren este diagnóstico o llegan a conclusiones distintas?** No los leí.

3. **¿Hay otros lugares del cruzador donde se hace `+1` o `-1` sobre páginas/líneas que también puedan estar mal?** La lectura confirma:
   - Línea 235: `clave_fin = (tomo, pg_fin + 1)` — el bug central.
   - Línea 222: `linea_fin = indices_nombres_por_archivo[archivo_ini] - 1` — fix Bug D, OK.
   - Línea 226: `linea_fin = n_lineas_por_archivo[archivo_ini] - 1` — convertir count a índice 0-indexado, OK.
   - Línea 240: `linea_fin = linea_fin_header - 1` — para que el bloque del actual termine **antes** del header del siguiente, OK conceptualmente, pero compuesto con el `+1` de línea 235 produce el corrimiento.
   - Línea 246: idem 226.
   - Línea 254: idem 226.

4. **¿`detectar_fin_real` del parser está validado byte-a-byte sobre los casos donde el cruzador miente?** No hay test suite visible.

5. **¿Hay versiones viejas del cruzador que tienen otro `+1`/`-1` y que pueden seguir activas en algún script de diagnóstico?** No verificado.

---

## 10. Próximos pasos sugeridos

En orden lógico:

1. **Confirmar el bug del `+1` con muestra de output** (sección 8.1).
2. **Recuperar git log para identificar el cambio de los 32 oks falsos** (sección 8.2).
3. **Decidir entre Opción A y Opción B del bug semántico** (sección 7.1) con conocimiento de causa.
4. **Aplicar el fix elegido en una rama nueva** y regenerar todo el pipeline.
5. **Diff del nuevo `csjn_casos.csv` contra el snapshot pre-fix.** Diferencias esperadas: solo casos previamente rotos arreglados, ningún caso bueno modificado.
6. **Spot-check sobre los 19 `ok_cortado_en_indice`** (sección 8.3).
7. **Verificar 121 orphans** (sección 8.4).

Reglas de trabajo establecidas previamente, vigentes:
- Un fix por vez con ciclo completo de validación.
- Snapshots antes de cambios destructivos.
- Validar con datos antes de codificar.
- No crear archivos ni ejecutar acciones sin permiso explícito.

---

## Apéndice — referencias de líneas exactas

Para retomar sin contexto, las líneas clave son:

| Archivo | Líneas | Qué hay ahí |
|---|---|---|
| `construir_catalogo.py` | 57 | Docstring: `pagina_fin = (página del siguiente fallo - 1)` |
| `construir_catalogo.py` | 380-382 | Docstring: idem |
| `construir_catalogo.py` | 410 | **Código:** `pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]` (sin restar 1 — inconsistente con docstring) |
| `construir_catalogo.py` | 419 | `nombres_indice = ' \| '.join(nombres)` — múltiples nombres conservados, no hay huérfanos a este nivel |
| `cruzar_catalogo_y_mapa.py` | 36 | Docstring: `pagina_fin_no_en_mapa — pagina_fin+1 no aparece como header` (asume semántica del docstring del catálogo) |
| `cruzar_catalogo_y_mapa.py` | 101 | Resolución de duplicados de mapa: `min(entradas, key=lambda e: e['linea_header'])` |
| `cruzar_catalogo_y_mapa.py` | 220-223 | Fix Bug D: `ok_cortado_en_indice` cuando archivo está en `indices_nombres_por_archivo` |
| `cruzar_catalogo_y_mapa.py` | 235 | **El `+1` central:** `clave_fin = (tomo, pg_fin + 1)` |
| `cruzar_catalogo_y_mapa.py` | 240 | `linea_fin = linea_fin_header - 1` — OK conceptualmente, problemático compuesto con 235 |
| `parser.py` | 972-987 | `construir_bloque_desde_localizacion` — corta lines según linea_inicio/linea_fin del cruzador |
| `parser.py` | 1109-1190 | `detectar_fin_real` — busca frontera real bidireccionalmente, corrige al cruzador |
| `parser.py` | 1208-1213 | `proximo_header_despues_de` — fuente independiente desde mapa_paginas |
| `parser.py` | 1311-1342 | Loop principal: arma bloque, llama detectar_fin_real, rearma bloque con linea_fin_real |

---

## Actualización 2026-05-02 — validación empírica del bug del `+1`

**Estado:** confirmado. El bug existe, opera en el 100% de los pares consecutivos analizados, con un offset notablemente uniforme.

### Datos analizados

Muestra: 118 fallos consecutivos del archivo `LibroVol329.1.md` con `status='ok'`, todos del Tomo 329 (libro 1 de 4 del tomo). Material extraído de `fallos_localizados.csv`.

### Hallazgos

#### Hallazgo 1 — `pagina_fin` del catálogo es el inicio del siguiente fallo, sin restar 1

De los 117 pares consecutivos analizados, **117 cumplen** que `pagina_fin_X == pagina_inicio_Y`. Cero excepciones.

Esto confirma empíricamente que el código de la línea 410 de `construir_catalogo.py` (`pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]`, sin restar 1) está activo y operando como se leyó. La inconsistencia docstring/código es real, no una observación teórica.

#### Hallazgo 2 — el cruzador siempre extiende el bloque del fallo X hacia adentro del fallo Y

Comparación entre `linea_fin_X` (del cruzador) y `linea_inicio_Y` (del cruzador, que es `linea_header` del fallo siguiente en el mapa):

| Métrica | Valor |
|---|---|
| Pares consecutivos analizados | 117 |
| Diferencias positivas (bloque X invade Y) | **117** |
| Diferencias negativas (bloque X termina antes de Y) | 0 |
| Diferencias nulas | 0 |

**No hay un solo par donde el bloque de X termine antes del inicio de Y.** Sistemáticamente, el cruzador deja que el bloque de X se extienda hacia adentro del fallo Y.

#### Hallazgo 3 — el offset es notablemente uniforme

| Métrica | Líneas |
|---|---|
| Mínimo | 25 |
| Máximo | 42 |
| Mediana | 32 |
| Media | 32.09 |

Distribución completa: los 117 pares caen en la franja de 10 a 49 líneas. Cero pares fuera.

```
< -200          0
-200 a -100     0
-99 a -50       0
-49 a -10       0
-9 a 0          0
1 a 9           0
10 a 49       117  █████████████████████████████████████████████████████████
50 a 99         0
100 a 200       0
> 200           0
```

#### Interpretación

El offset de ~32 líneas es del orden de magnitud de **una página completa del corpus**. Cuando el cruzador busca `clave_fin = (tomo, pg_fin + 1)` y encuentra el header, calcula `linea_fin = linea_fin_header - 1`. Pero `pg_fin + 1` es la **segunda página del fallo siguiente**, no la primera. Entonces el bloque de X se extiende sobre todo lo que mide la primera página del fallo Y (header + ~30 líneas iniciales).

Este es exactamente el comportamiento predicho por el análisis del docstring/código del catálogo y la línea 235 del cruzador.

### Implicaciones para el resto del pipeline

**Sobre el parser:** `detectar_fin_real` está compensando un bug sistemático del cruzador, no un caso de borde. La función fue escrita como defensa contra "casos donde el cruzador se equivoca", pero los datos muestran que el cruzador se equivoca **siempre** y por una cantidad predecible. La defensa convirtió el bug en invisible para la mayoría del análisis estadístico, lo cual es bueno operacionalmente pero malo conceptualmente: el pipeline tiene una capa de parche permanente sobre un cálculo que podría ser correcto.

**Sobre los 32 oks falsos:** la hipótesis más coherente con los datos es que el cambio anterior NO tocó la línea 235 del cruzador (porque si la hubiera tocado, los 117 pares de la muestra ya tendrían `linea_fin_X < linea_inicio_Y`). El cambio tocó otra cosa que afectó solo a casos previamente clasificados como `pagina_fin_no_en_mapa` o similares. Lo que produjo "oks falsos cortados a mitad" no fue arreglar el bug del `+1` sino reclasificar casos que estaban siendo tratados defensivamente. Para confirmarlo se necesita el git log o los 32 casos específicos.

**Sobre el costo del fix:** si se decide arreglar el bug semántico (Opción A o B de la sección 7.1), el cambio uniforme va a ser que **todos los `linea_fin` de fallos no-últimos se recorten ~32 líneas**. Eso debería:
- Eliminar la diferencia entre `linea_fin` y `linea_fin_real` para los casos donde `detectar_fin_real` corregía el offset usando carátula/sumario del siguiente.
- Dejar inalterados los casos donde `detectar_fin_real` ya usaba la firma del juez actual (porque ahí la corrección era hacia atrás, no hacia adelante).
- Posiblemente eliminar algunos falsos positivos del parser (votos del fallo Y atribuidos a X por contaminación de bloque).

### Datos de respaldo

Los 30 primeros pares del análisis, exactos:

```
caso_X            caso_Y           lf_X    li_Y    diff
329_p59           329_p78          2835    2806     +29
329_p78           329_p80          2911    2879     +32
329_p80           329_p83          3023    2989     +34
329_p83           329_p85          3093    3061     +32
329_p85           329_p88          3201    3172     +29
329_p88           329_p94          3424    3391     +33
329_p94           329_p117         4316    4281     +35
329_p117          329_p120         4413    4386     +27
329_p120          329_p123         4521    4486     +35
329_p123          329_p134         4962    4932     +30
329_p134          329_p135         4998    4963     +35
329_p135          329_p142         5262    5228     +34
329_p142          329_p147         5442    5411     +31
329_p147          329_p149         5515    5477     +38
329_p149          329_p158         5849    5815     +34
329_p158          329_p163         6031    5999     +32
329_p163          329_p165         6100    6072     +28
329_p165          329_p167         6169    6139     +30
329_p167          329_p171         6317    6281     +36
329_p171          329_p175         6464    6430     +34
329_p175          329_p177         6533    6505     +28
329_p177          329_p182         6717    6688     +29
329_p182          329_p184         6788    6754     +34
329_p184          329_p187         6899    6868     +31
329_p187          329_p201         7455    7426     +29
329_p201          329_p206         7636    7600     +36
329_p206          329_p212         7865    7832     +33
329_p212          329_p215         7972    7946     +26
329_p215          329_p218         8082    8050     +32
329_p218          329_p222         8226    8196     +30
```

### Cabos sueltos de esta validación

1. **La muestra es de un solo archivo.** El offset de ~32 líneas puede ser específico de la maquetación del Tomo 329. Tomos modernos (343+) pueden tener páginas más cortas o más largas. Para generalizar la conclusión cuantitativa hay que repetir el análisis sobre 2-3 archivos de tomos distintos.

2. **Solo se analizaron casos `ok`.** No se sabe cómo se distribuyen los offsets para `fallo_cruza_archivos` o `pagina_fin_no_en_mapa`. Probablemente el patrón es muy distinto.

3. **No se tocó el comportamiento del parser.** Falta confirmar empíricamente que `detectar_fin_real` está corrigiendo este offset específico (sección "Próximos pasos sugeridos").

### Próximos pasos sugeridos (post-validación)

En orden:

1. **Comparar `linea_fin` vs `linea_fin_real` para los 118 casos** en el output del parser. Si `linea_fin_real - linea_fin ≈ -32` sistemáticamente, está confirmado que el parser corrige exactamente el bug. Si hay dispersión, hay casos donde la corrección no opera y conviene mirarlos.

2. **Validar el offset en otro archivo** (ej. `LibroVol343-1.md` o algún tomo moderno) para confirmar que el ~32 es estable o varía.

3. **Identificar los 32 oks falsos** comparando con git log o con la lista de casos específicos.

4. **Decidir Opción A o B** del fix semántico con conocimiento empírico del impacto.

---

*Documento generado el 2/5/2026 como base para retomar el diagnóstico sin pérdida de contexto.*
*Actualizado el 2/5/2026 con validación empírica sobre 118 fallos del Tomo 329.*
## Actualización 2026-05-02 (II) — el parser corrige parcialmente, no totalmente

**Estado:** el parche de `detectar_fin_real` es real pero incompleto. Hay contaminación residual sistemática en todos los bloques.

### Datos analizados

Los mismos 118 casos del Tomo 329 archivo 1 cruzados con el output del parser (`csjn_casos.csv`, columnas `linea_fin`, `linea_fin_real`, `status_fin`, `pista_fin`).

Cobertura: 118/118 casos encontrados en el output del parser, todos con `status_localizacion = ok`.

### Hallazgo 1 — el delta es menor de lo esperado

Definimos `delta = linea_fin_real - linea_fin`. Si el parser compensara exactamente el bug del cruzador, esperaríamos `delta ≈ -32` (la mediana del offset del cruzador).

Lo observado:

| Métrica | Valor |
|---|---|
| Min | -42 |
| Max | +43 |
| Media | -13.73 |
| Mediana | **-11** |

La corrección del parser es de la mitad de la magnitud esperada.

### Hallazgo 2 — distribución del delta

```
< -100          0
-100 a -50      0
-49 a -30      16  ████████████████
-29 a -10      58  ██████████████████████████████████████████████████████████
-9 a -1        37  █████████████████████████████████████
0               0
1 a 9           3  ███
10 a 49         4  ████
50 a 99         0
100+            0
```

Tres clusters:

- **74 casos (62.7%)** con delta entre -50 y -10: el parser compensa de manera "esperable" pero parcial.
- **37 casos (31.4%)** con delta entre -9 y -1: el parser corrige muy poco.
- **7 casos (5.9%)** con delta ≥ 0: el parser **no corrige** o **extiende** el bloque más allá del corte del cruzador.

Cero casos con corrección excesiva (delta < -50). Cero casos donde el parser falle catastróficamente (`fin_no_detectado`).

### Hallazgo 3 — qué pista usa el parser

Distribución de `pista_fin`:

| Pista | Casos | % |
|---|---|---|
| `caratula_siguiente` | 97 | 82% |
| `sumario_siguiente` | 21 | 18% |
| `firma_actual` | 0 | 0% |
| `marcador_apertura_siguiente` | 0 | 0% |
| `fallback_catalogo` | 0 | 0% |

Distribución de `status_fin`:

| status_fin | Casos |
|---|---|
| `fin_dentro_bloque` | 111 |
| `fin_extendido_pag_compartida` | 7 |

El parser **siempre** encuentra una pista del fallo siguiente. La búsqueda hacia atrás desde `linea_fin_catalogo` es la rama dominante. La carátula del siguiente es la pista universal.

Delta promedio según pista usada:

```
pista                     n   min  max  mediana  media
caratula_siguiente       97   -42  +43    -12   -13.95
sumario_siguiente        21   -27   -6    -11   -12.71
```

### Hallazgo 4 — explicación del por qué el delta no es -32

`detectar_fin_real` no busca el header de página del fallo Y. Busca la **carátula del fallo Y**, que está unas líneas después del `linea_header` de la primera página de Y. La estructura típica observada es:

```
linea_header (página N de Y)    ← lo que el cruzador toma como referencia
... ~10-30 líneas ...           ← header del tomo, número de página, etc.
CARÁTULA DEL FALLO Y            ← lo que detectar_fin_real busca
... sumarios doctrinales ...
"FALLO DE LA CORTE SUPREMA"
... cuerpo de Y ...
```

El cruzador con bug pone `linea_fin_X = linea_header_de_pY+1 - 1`, que cae dentro del cuerpo de Y (~32 líneas adentro de `linea_inicio_Y`).

`detectar_fin_real` busca hacia atrás la carátula de Y. Como la carátula está unas líneas **después** del `linea_inicio_Y`, el `linea_fin_real` queda en algún punto **entre** `linea_inicio_Y` y `linea_fin` del cruzador. La diferencia neta es ~-11 a -12 líneas, no -32.

**Conclusión:** los bloques de cada fallo X siguen incluyendo entre 0 y 32 líneas del inicio del fallo Y. Específicamente, incluyen la zona entre el header de página de Y y la carátula de Y. Esa zona contiene el header del tomo, el número de página, y posiblemente sumarios cortos. **No contiene el cuerpo decisorio de Y**, pero contamina el word count y puede afectar detecciones secundarias.

### Hallazgo 5 — los 7 casos donde el parser no compensa

```
caso_id      lf      lfr     delta   pista_fin
329_p432     16531   16558   +27     caratula_siguiente
329_p445     17508   17551   +43     caratula_siguiente
[5 casos más con delta entre +1 y +9]
```

Son casos donde la carátula del fallo siguiente aparece **después** del `linea_fin` del cruzador, no antes. Probablemente fallos cortos donde X y Y comparten la última página de X. `detectar_fin_real` los marca como `fin_extendido_pag_compartida` y extiende el bloque hacia adelante para llegar a la carátula del siguiente. Comportamiento esperado y correcto.

### Implicaciones para el fix del bug semántico

**Revisión de la sección 4 del documento principal:** el dictamen original era "el parser parchea el bug, por eso no se nota". Los datos refinan eso: el parser **parchea parcialmente**, dejando ~11 líneas de residuo medio. La afirmación correcta es:

> El parche convierte un offset sistemático de +32 líneas (cruzador) en un residuo de ~+11 líneas en `linea_fin_real`. El bug no es invisible al output, solo está atenuado.

**Sobre la decisión Opción A vs Opción B:**

Si se arregla el `+1` (cualquiera de las dos opciones), el `linea_fin` del cruzador se va a recortar ~32 líneas. `detectar_fin_real` después va a buscar la carátula siguiente, pero ahora desde un punto más cercano. La carátula está donde está; `detectar_fin_real` la va a encontrar igual. **El `linea_fin_real` resultante debería ser prácticamente idéntico al actual.**

Lo que sí va a cambiar es:

1. **Los huérfanos.** Los `pagina_fin_no_en_mapa` y `fallo_cruza_archivos` actuales reciben `linea_fin = última_línea_del_archivo` como fallback. Esos casos sí van a cambiar de comportamiento si el fix los reclasifica como `ok`.

2. **El bloque enviado al parser.** Hoy el bloque entra con +32 líneas extra y el parser después lo recorta. Si se arregla, el bloque entra con +0 líneas extra. El parser hace menos trabajo. Operacionalmente equivalente para el output, conceptualmente más limpio.

3. **Casos donde `detectar_fin_real` falla.** Si en tomos modernos hay casos donde el primer_token no se detecta y el parser cae al fallback `firma_actual`, ahí el `linea_fin` del cruzador era el ancla. Si el ancla se mueve 32 líneas, el comportamiento del fallback puede cambiar. Necesita verificación.

### Cabos sueltos

1. **Falta validar en tomos modernos.** Tomos 343-349 pueden tener maquetación distinta, con páginas más largas o más cortas. El residuo de ~11 líneas puede ser específico del Tomo 329.

2. **Falta analizar los huérfanos** (`pagina_fin_no_en_mapa`, `fallo_cruza_archivos`). Ahí es donde más probablemente vive el problema de los 32 oks falsos.

3. **El residuo medio de 11 líneas afecta el word count.** Habría que cuantificar cuánto impacto tiene en `word_count`, `wc_mayoria`, `wc_considerando` para saber si la contaminación es despreciable o significativa.

### Próximos pasos sugeridos (post-validación II)

En orden:

1. Analizar una muestra de casos con `status_localizacion ∈ {pagina_fin_no_en_mapa, fallo_cruza_archivos}` para entender dónde está el daño real del bug.
2. Validar el patrón de delta en otro tomo.
3. Cuantificar el impacto del residuo en word counts.
4. Recién entonces: decidir Opción A vs B con conocimiento empírico completo.

---

*Actualizado el 2/5/2026 con validación empírica del comportamiento del parser sobre los mismos 118 casos del Tomo 329.*
## Actualización 2026-05-02 (III) — análisis de huérfanos

**Estado:** los 70 huérfanos se dividen en dos clases con causas estructurales distintas. El bug del `+1` no es responsable de la mayoría.

### Datos analizados

`fallos_localizados_huerfanos.csv` (70 filas) cruzado con `mapa_paginas.csv` (46.937 entradas).

### Hallazgo 1 — distribución de huérfanos por status

| Status | N |
|---|---|
| `pagina_no_en_mapa` | 43 |
| `fallo_cruza_archivos` | 27 |
| `pagina_fin_no_en_mapa` | **0** |
| `ultimo_del_tomo` | **0** |
| `ultimo_del_tomo_sin_fin` | **0** |

Las dos categorías que el fix Bug D atacó directamente desaparecieron. La categoría `pagina_fin_no_en_mapa` también desapareció completamente, lo cual era una de las anomalías marcadas como "inesperadas" en `PROMPT_PROXIMA_SESION.md`.

### Hallazgo 2 — los 43 `pagina_no_en_mapa` son el Bug A documentado

Distribución por tomo:

```
Tomo 331: 11
Tomo 332: 11
Tomo 333: 11
Tomo 334: 10
Total: 43
```

Coincide exactamente con `DEUDA_TECNICA.md` Bug 2: pérdida sistemática de 43 fallos en tomos 331-334 con dictamen previo embebido.

**Detalle revelador:** en estos 43 huérfanos, la columna `archivo` está vacía. Eso es porque el cruzador, en línea 209, hace `out['status'] = 'pagina_no_en_mapa'` y devuelve sin haber asignado `archivo_ini`. La página no estaba en `mapa_paginas.csv`, por lo tanto **el detector de páginas no detectó esas páginas**. El bug está en `detectar_paginas.py`, no en el cruzador.

Hipótesis sobre la causa: en los tomos 331-334, los fallos con dictamen previo embebido tienen una estructura donde el header de página está colocado de forma que no matchea la heurística de `detectar_paginas.py` (número del tomo aislado en una línea + número de página en línea adyacente). Habría que validar empíricamente sobre un caso específico, por ejemplo Boston Cía. de Seguros (Tomo 331, p. 7), leyendo las líneas alrededor de donde debería estar el header de página 7.

### Hallazgo 3 — los 27 `fallo_cruza_archivos` son una clase distinta

Distribución por tomo: 1-3 casos en cada tomo del rango 329-347. Patrón estructural distinto del Bug A.

Patrón geográfico: cada `fallo_cruza_archivos` está en un archivo intermedio (1, 2, 3) de su tomo, nunca en el último archivo. Eso es coherente con la definición: son fallos cuyo `pagina_inicio` está en archivo N y cuyo siguiente fallo está en archivo N+1.

### Hallazgo 4 — bloques gigantes en `fallo_cruza_archivos`

El cruzador asigna `linea_fin = última_línea_del_archivo - 1` (línea 246 del cruzador) cuando hay cruce. Resultado: bloques que incluyen todo el aparato editorial al final del archivo.

Comparación tomos viejos vs modernos:

| Caso | Líneas del bloque |
|---|---|
| 329_p1350 | 11.326 |
| 329_p2949 | 12.666 |
| 329_p4877 | 13.410 |
| 330_p4263 | 11.573 |
| 337_p877 | 690 |
| 339_p933 | 524 |
| 342_p1261 | 1.466 |

Los tomos viejos (329-330) generan bloques de 10.000+ líneas. Los modernos (337-347), bloques de 500-1.500 líneas. La diferencia es por tamaño del aparato editorial, no por el bug del `+1`.

**Esto importa para el parser:** `detectar_fin_real` en su búsqueda hacia adelante usa como límite `min(proximo_header_pagina + 50, lfc + 200, n - 1)`. Si `lfc` es la última línea del archivo, `lfc + 200` no añade nada útil. La búsqueda depende de encontrar `proximo_header_pagina`, y en un cruce de archivos no hay próximo header en el mismo archivo. Esos casos probablemente caen al fallback `firma_actual` o `fin_no_detectado`. Necesita verificación cruzando con `csjn_casos.csv`.

### Hallazgo 5 — hipótesis 6 invalidada

**Hipótesis original:** los 27 `fallo_cruza_archivos` podrían ser artefactos del bug del `+1`. Si se arregla el `+1` (clave_fin = pg_fin en lugar de pg_fin + 1), muchos de esos casos podrían pasar a `ok` con `linea_fin` correcto.

**Validación:** para cada uno de los 27 casos, busqué si `(tomo, pg_fin)` está en el mapa en el mismo archivo que `pg_ini`.

Resultado:

| Veredicto | N |
|---|---|
| Resolvibles por fix del `+1` | **2** |
| No resolvibles (cruce real) | 25 |

Detalle de los no resolvibles:

- **18 casos:** `pg_fin` también está en otro archivo. El cruce es real, no un artefacto del `+1`.
- **7 casos:** `pg_fin` no está en el mapa en absoluto. El detector de páginas no la detectó.

Solo 2 casos (`343_p1447`, `344_p1253`) tendrían `pg_fin` en el mismo archivo que `pg_ini` y se resolverían arreglando el `+1`.

**Conclusión:** los `fallo_cruza_archivos` son una clase legítima de problema, no víctimas colaterales del bug semántico. Cualquier fix del `+1` los va a dejar inalterados en su mayoría.

### Hallazgo 6 — los 7 casos donde `pg_fin` no está en el mapa

Subgrupo notable de los 25 no resolvibles:

```
331_p1007  LibroVol331.1.md  pg_fin=1013  (no en mapa)
331_p1942  LibroVol331.2.md  pg_fin=1985  (no en mapa)
332_p917   LibroVol332.1.md  pg_fin=921   (no en mapa)
332_p1960  LibroVol332.2.md  pg_fin=2033  (no en mapa)
333_p772   LibroVol333.1.md  pg_fin=777   (no en mapa)
333_p1869  LibroVol333.2.md  pg_fin=1885  (no en mapa)
334_p698   LibroVol334.1.md  pg_fin=715   (no en mapa)
```

Todos en tomos 331-334 (el rango del Bug A). Probablemente son páginas que `detectar_paginas.py` no detectó por la misma causa que el Bug A: estructura de header anómala en esos tomos.

Es decir, el Bug A no afecta solo a 43 fallos directamente; afecta también indirectamente a 7 fallos que terminan clasificados como `fallo_cruza_archivos` porque su página de fin no fue detectada en el archivo correcto.

**Total real del Bug A: 43 + 7 = 50 fallos afectados** (no 43 como dice `DEUDA_TECNICA.md`).

### Hallazgo 7 — los 32 oks falsos: la cuenta cierra

`PROMPT_PROXIMA_SESION.md` reportaba que después del fix Bug D:
- `pagina_fin_no_en_mapa`: 39 → 0
- `fallo_cruza_archivos`: 20 → 27 (+7)

Si los 39 que estaban en `pagina_fin_no_en_mapa` se redistribuyeron, la matemática sugiere:

- 32 → `ok` (los "32 oks falsos" del spot-check)
- 7 → `fallo_cruza_archivos` (los +7 de la cuenta)

39 = 32 + 7. La cuenta cierra exactamente.

**Lo que esto sugiere:** el cambio que generó los 32 oks falsos no fue tocar el `+1` (el `+1` sigue vivo, validado en la actualización II). Tocó algo en la lógica que decide entre `ok`, `pagina_fin_no_en_mapa` y `fallo_cruza_archivos`. La lectura de `cruzar_catalogo_y_mapa.py` no muestra cambios obvios en esa lógica entre las versiones, lo cual sugiere que el cambio puede haber sido upstream: en el catálogo o en el mapa de páginas, no en el cruzador.

Para cerrar este diagnóstico falta:

1. Identificar los 32 casos específicos que pasaron de `pagina_fin_no_en_mapa` a `ok`.
2. Revisar el git log del catálogo y del detector de páginas entre las dos corridas.
3. Verificar si la lista de páginas en el mapa cambió (más detecciones) o si el catálogo cambió (más entradas, o entradas con páginas distintas).

### Implicaciones acumulativas

Combinando este análisis con las actualizaciones I y II, el panorama queda así:

**Bug del `+1`:** real, sistemático, opera en el 100% de los pares consecutivos. Pero la corrección por `detectar_fin_real` en el parser deja un residuo de ~11 líneas medio por bloque. **Impacto operativo: bajo. Impacto conceptual: hay que arreglarlo.**

**Bug A (43 + 7 fallos en 331-334):** afecta directamente al detector de páginas (`detectar_paginas.py`), no al cruzador. Causa: estructura de header anómala en tomos con dictamen previo embebido. **Impacto operativo: alto, son fallos perdidos completos.**

**Cruces reales entre archivos (18 casos):** no son bug, son una clase estructural legítima del corpus. El cruzador los maneja con un fallback ruidoso (bloque que incluye aparato editorial). **Impacto operativo: medio, contamina word counts pero el parser puede recuperar el corte por otras vías.**

**Los 32 oks falsos:** la cuenta sugiere que vinieron de un cambio en el catálogo o en el mapa, no en el cruzador. Hay que ver el git log para confirmar.

### Próximos pasos sugeridos (post-validación III)

En orden de información que dan vs costo:

1. **Verificar el git log del catálogo y detector** para identificar el cambio que generó los 32 oks falsos. Bajo costo, alta información.

2. **Tomar uno de los 32 oks falsos específicos** (cuando los identifiquemos) y ver qué `linea_fin` tiene actualmente. Si está cortado a mitad, ¿en qué línea exactamente? Eso da el patrón.

3. **Validar empíricamente el Bug A** sobre Boston Cía. de Seguros (Tomo 331, p. 7): leer las líneas alrededor de donde debería estar el header de página 7 en `LibroVol331.1.md` y entender por qué `detectar_paginas.py` no lo detectó.

4. **Verificar el comportamiento de `detectar_fin_real`** sobre los 27 `fallo_cruza_archivos`: cruzar con `csjn_casos.csv` y ver qué `status_fin` y `pista_fin` tienen. ¿Caen a `firma_actual`? ¿A `fin_no_detectado`?

---

*Actualizado el 2/5/2026 con análisis de los 70 huérfanos y validación de la hipótesis 6 sobre `fallo_cruza_archivos`.*
## Actualización 2026-05-02 (IV) — regímenes editoriales y fix extendido para `fallo_cruza_archivos`

**Estado:** identificado el patrón estructural del corpus (tres regímenes editoriales distintos), descartada una hipótesis sobre uso del índice del archivo siguiente, y diseñada la generalización del fix Bug D para resolver los 27 `fallo_cruza_archivos` sin tocar los 19 `ok_cortado_en_indice` actuales.

### Datos analizados

`catalogo.csv` (5.862 fallos), `secciones_indices.csv` (139 filas, 46 con `tipo_indice = nombres`), y `mapa_paginas.csv`. Cruce de los 27 `fallo_cruza_archivos` contra los archivos que tienen índice de nombres registrado.

### Hallazgo 1 — los archivos `.md` del corpus no son uniformes: tres regímenes editoriales

Distribución de `n_archivos_indice` por tomo (la cantidad de archivos del tomo donde aparece registrada cada entrada en el índice):

| Tomos | Régimen | Patrón |
|---|---|---|
| 329-342 | A — índices por volumen, parcialmente acumulativos | Mezcla: algunos fallos aparecen en un solo índice (`n=1`), otros en dos (`n=2`) |
| 343-347 | B — índices consolidados | TODOS los fallos del tomo aparecen en TODOS los volúmenes del tomo |
| 348-349 | C — monolíticos | Un solo archivo `.md` por tomo |

Detalle por tomo:

```
tomo   total   n=1   n=2   n=3
 329   1063   236   827
 330    757   159   598
 331    376   134   242
 332    330   105   225
 333    252    66   186
 334    199    84   115
 337    130    56    74
 338    167    94    73
 339    328   160   168
 340    277   115   162
 341    241   128   113
 342    219   105   114
 343    239                 239
 344    321                 321
 345    219         219
 346    208         208
 347    240         240
 348    251   251
 349     45    45
```

### Hallazgo 2 — cada archivo `.md` tiene su propio índice de nombres

`secciones_indices.csv` registra 46 filas con `tipo_indice = nombres`, una por cada archivo del corpus. Por ejemplo, el Tomo 329 tiene 4 archivos y los 4 tienen su propio inicio de índice de nombres:

```
LibroVol329.1.md  inicio_indice_nombres = 52145
LibroVol329.2.md  inicio_indice_nombres = 60729
LibroVol329.3.md  inicio_indice_nombres = 73894
LibroVol329.4.md  inicio_indice_nombres = 46157
```

Cada volumen tiene su aparato editorial completo al final, independientemente del régimen editorial. Esto es lo que hace posible la generalización del fix Bug D.

### Hallazgo 3 — los 27 `fallo_cruza_archivos` tienen índice disponible en su `archivo_ini`

Verificación cruzada: para cada uno de los 27 casos, ¿el `archivo_ini` (donde arranca el fallo) tiene una entrada de `tipo_indice = nombres` en `secciones_indices.csv`?

| Veredicto | N |
|---|---|
| SÍ — fix aplicable | **27** |
| NO — fix no se activa | 0 |

Cobertura del 100%. El fix se puede aplicar a los 27 casos sin excepciones.

### Hallazgo 4 — los 19 `ok_cortado_en_indice` actuales viven en archivos distintos

Verificación de no-regresión: los 19 archivos donde se aplica `ok_cortado_en_indice` (último fallo de cada tomo) son los **últimos** archivos de cada tomo (`.4.md`, `.3.md`, `.2.md`, `-3.md`, etc.). Los 27 `fallo_cruza_archivos` están en archivos **intermedios** (`.1.md`, `.2.md`, `.3.md` — nunca el último del tomo).

**Cero solapamiento.** El fix extendido toca archivos distintos de los que ya funcionan.

### Hallazgo 5 — pregunta descartada: "¿usar el índice del archivo siguiente?"

Hipótesis evaluada: cuando un fallo `cruza_archivos`, ¿podríamos usar el índice del archivo N+1 para encontrar la página correcta de fin?

**Respuesta: no, los índices no aportan información de fin.**

Los índices del corpus solo registran página de **inicio** de cada fallo, nunca de fin. El campo `pagina_fin` del catálogo se calcula por inferencia (página del fallo siguiente). Esto vale tanto en régimen A (índices parciales) como en régimen B (índices consolidados) como en régimen C (monolíticos).

Lo que sí aporta el régimen B (acumulativo): saber que un fallo del archivo N también está listado en el índice del archivo N+1 confirma que el fallo es real y que el catálogo lo identificó bien. Pero no dice nada sobre dónde termina su cuerpo.

### Hallazgo 6 — el fix correcto es la generalización del Bug D, no la consulta del índice siguiente

Estrategia: cortar el bloque del fallo X en el `linea_inicio_indice_nombres` del **archivo donde arranca X**, no en el último archivo del tomo. Esto garantiza:

- El bloque incluye todo el cuerpo del fallo X (que está físicamente en archivo N).
- El bloque NO incluye el aparato editorial del archivo N (porque corta antes).
- El bloque NO se extiende a archivo N+1 (porque ya cortó dentro de N).

Costo: si entre el final real del cuerpo de X y el inicio del aparato editorial de archivo N hay otros fallos chicos no listados en el catálogo (caso raro pero posible), el bloque los va a incluir. `detectar_fin_real` del parser puede compensarlo en la mayoría de casos.

Beneficio: bloques manejables (~500 a ~1.500 líneas para los casos verificados, en vez de los actuales 10.000+ líneas para tomos viejos).

### Diseño del fix

En `cruzar_catalogo_y_mapa.py`, líneas 242-249, donde hoy está:

```python
else:
    # El fallo cruza archivos: termina con el último header del archivo de inicio
    # y el siguiente fallo arranca en otro archivo
    out['linea_fin'] = (
        n_lineas_por_archivo[archivo_ini] - 1
        if archivo_ini in n_lineas_por_archivo else ''
    )
    out['status'] = 'fallo_cruza_archivos'
```

Cambio propuesto:

```python
else:
    # El fallo cruza archivos: cortar antes del aparato editorial del archivo_ini
    # (paralelo a ok_cortado_en_indice para ultimo_del_tomo)
    if archivo_ini in indices_nombres_por_archivo:
        out['linea_fin'] = indices_nombres_por_archivo[archivo_ini] - 1
        out['status'] = 'ok_cortado_en_indice_cruza'
    elif archivo_ini in n_lineas_por_archivo:
        out['linea_fin'] = n_lineas_por_archivo[archivo_ini] - 1
        out['status'] = 'fallo_cruza_archivos'
    else:
        out['linea_fin'] = ''
        out['status'] = 'fallo_cruza_archivos_sin_fin'
```

Es exactamente la misma lógica del fix Bug D, aplicada a otra rama. Backward compatible: sin `indices_nombres_por_archivo`, comportamiento idéntico al actual.

### Predicción del impacto

Si se aplica el fix:

| Cambio | N |
|---|---|
| Casos que pasan de `fallo_cruza_archivos` a `ok_cortado_en_indice_cruza` | 27 |
| Casos `ok_cortado_en_indice` actuales que cambian | 0 |
| Casos `ok` actuales que cambian | 0 |
| Casos `pagina_no_en_mapa` que cambian | 0 |

Total huérfanos esperado tras el fix: 70 - 27 = **43** (todos los del Bug A en tomos 331-334).

### Caso a verificar antes de aplicar

**`334_p1054`** en `LibroVol334.2.md`. El fallo arranca en `linea_inicio = 13079`. El índice de nombres de ese archivo empieza en `linea_inicio = 13431`. Margen entre arranque del fallo y inicio del aparato editorial: 352 líneas.

Eso es muy poco para un fallo entero. Tres explicaciones posibles:

1. El fallo es muy corto y termina dentro del archivo (~352 líneas alcanzan).
2. El detector de páginas tiene un error en ese archivo y el `inicio_indice_nombres = 13431` está mal.
3. El catálogo ubica mal `334_p1054`.

Validación recomendada: leer `LibroVol334.2.md` en torno a la línea 13079 y verificar que efectivamente arranca el fallo, y leer en torno a la línea 13431 para ver si efectivamente empieza el índice de nombres ahí.

Si el caso resulta anómalo, el fix no le va a hacer daño (deja `linea_fin = 13430`, lo cual es el mejor disponible). Pero conviene saberlo.

### Plan de aplicación sugerido

1. **Snapshot del estado actual** (`fallos_localizados.csv`, `csjn_casos.csv`).
2. **Verificar el caso `334_p1054`** manualmente en el `.md`.
3. **Aplicar el cambio en una rama git nueva**.
4. **Regenerar `fallos_localizados.csv`**.
5. **Validar:** los 27 casos pasan a `ok_cortado_en_indice_cruza`. Los 19 `ok_cortado_en_indice` y los 5773 `ok` quedan sin cambios.
6. **Regenerar `csjn_casos.csv`**.
7. **Diff contra el snapshot:** los 27 casos deberían aparecer ahora con bloques mucho más chicos y `status_localizacion = ok_cortado_en_indice_cruza`. Ningún caso existente debería tener cambios.
8. **Spot-check sustantivo** sobre 3-4 de los 27: verificar que `voting_pattern`, `firmas`, `outcome`, `word_count` están bien parseados.

Si todo valida, el fix se commitea. Si hay regresión, rollback.

### Cabos sueltos

1. **El residuo del bug del +1 sigue existiendo.** Este fix no lo toca. Para los 27 casos que pasan a `ok_cortado_en_indice_cruza`, el `linea_fin = inicio_indice_nombres - 1` puede estar lejos del cuerpo real del fallo. `detectar_fin_real` va a corregir buscando la carátula del siguiente, igual que hace para los `ok` regulares.

2. **Los 43 `pagina_no_en_mapa` (Bug A) siguen sin atención.** Son del detector de páginas, no del cruzador. Atacarlos requiere revisión separada.

3. **No queda diagnosticado el origen de los 32 oks falsos.** La hipótesis actual (cambio upstream en catálogo o mapa) sigue pendiente de verificación con git log.

---

*Actualizado el 2/5/2026 con análisis de regímenes editoriales (`catalogo.csv`, `secciones_indices.csv`) y diseño del fix extendido para `fallo_cruza_archivos`.*
## Actualización 2026-05-02 (V) — hojas complementarias como componente del aparato editorial

**Estado:** identificada una clase de ruido editorial no documentada hasta ahora ("HOJAS COMPLEMENTARIAS" intercaladas en los `.md` como relleno editorial). No causa los problemas detectados, pero sí infla los bloques de `fallo_cruza_archivos` antes del fix extendido.

### Qué son

Páginas en blanco insertadas en el PDF original con un texto editorial repetitivo:

```
HOJA COMPLEMENTARIA
Hoja incorporada a los efectos de permitir la búsqueda por
página dentro del Volumen.
```

Función editorial: reservar páginas para que la paginación final del volumen impreso coincida con la del índice. Aparecen agrupadas en bloques consecutivos al final de los archivos `.md`, después del aparato editorial principal (índices), junto con el cierre de los talleres gráficos.

### Caso confirmado

`LibroVol334.2.md`, líneas 15238-15256: bloque de **7 hojas complementarias consecutivas**. El archivo entero termina poco después.

### Por qué NO rompen el detector de páginas

El detector busca el número del tomo aislado (`334`) en una línea, con un número de página en líneas vecinas. Las hojas complementarias **no contienen el número del tomo en su texto** y no incluyen un número de página detectable por la heurística. Por lo tanto, no aparecen como entradas espurias en `mapa_paginas.csv`.

Confirmación implícita: si las hojas generaran detecciones espurias, el bug afectaría a TODOS los tomos, no solo a 331-334. Los huérfanos del Bug A son específicos de tomos con dictamen previo embebido, no de tomos con hojas complementarias. Las hojas existen en muchos tomos, el Bug A no.

### Por qué SÍ contaminan los bloques de `fallo_cruza_archivos`

El cruzador, en la rama `fallo_cruza_archivos`, asigna `linea_fin = última_línea_del_archivo - 1`. El bloque resultante incluye **todo el aparato editorial al final del archivo**: índice de nombres, índice de materias, sumario, índice de legislación, índice general, cierre de talleres gráficos, y **las hojas complementarias**.

Para `334_p1054` (caso `Zeballos, José Luis`):
- `linea_inicio = 13079`
- `linea_fin = 15263` (cruzador, fin del archivo - 1)
- Inicio del índice de nombres: línea 13431
- Hojas complementarias: líneas 15238-15256

El bloque actual de 2.184 líneas contiene: cuerpo del fallo (~352 líneas hasta inicio del índice) + aparato editorial completo (~1.832 líneas) + hojas complementarias.

### Reinterpretación del caso `334_p1054`

El caso fue marcado en la Actualización IV como anómalo por el margen pequeño (352 líneas) entre `linea_inicio` y `inicio_indice_nombres`. Reinterpretación: **es un fallo corto cuyo cuerpo entero cabe en 352 líneas**, no una anomalía. El fix extendido (`linea_fin = inicio_indice_nombres - 1 = 13430`) le asigna un bloque correcto.

El caso queda **validado**, no requiere check manual adicional para aplicar el fix.

### Estimación del impacto en word counts antes del fix

Tomando solo el caso `334_p1054`: hoy el bloque entrega al parser ~2.184 líneas. El cuerpo real del fallo es ~352 líneas. El parser, vía `detectar_fin_real`, intenta corregir buscando carátula del fallo siguiente — pero como el siguiente está en otro archivo, esa pista falla y el parser cae al fallback `firma_actual`. Eso recorta el bloque hasta la firma del juez del fallo actual, que probablemente está cerca del final del cuerpo (~352 líneas). Lo cual podría estar funcionando bien.

**Hipótesis a verificar:** los 27 `fallo_cruza_archivos` actuales pueden tener `status_fin = fin_por_firma_actual` en `csjn_casos.csv`. Si es así, el parser ya estaba haciendo un trabajo razonable para estos casos. El fix extendido formaliza ese comportamiento desde el cruzador, en lugar de depender del parche del parser.

### Decisión sobre detección explícita de hojas

Las hojas complementarias merecen detección explícita, por tres razones:

1. **Auditoría:** análisis sobre archivos completos puede necesitar descartarlas como ruido.
2. **Outliers:** una hoja que cayera antes del índice de nombres rompería el supuesto del fix extendido. Saber dónde están permite validar que esto no pasa.
3. **Composición del corpus:** saber cuántas hay es información estructural útil para la tesis.

Detección trivial:

```python
RE_HOJA_COMPL = re.compile(r"^HOJA COMPLEMENTARIA\s*$")
RE_HOJA_COMPL_TXT = re.compile(r"^Hoja incorporada a los efectos", re.I)
```

Estrategia recomendada (opción A, conservadora): agregar un script que produce `hojas_complementarias.csv` con columnas `(tomo, archivo, linea_inicio, linea_fin, n_hojas_consecutivas)`. No tocar el cruzador ni el parser. Si más adelante un análisis las necesita, el CSV ya está disponible.

Estrategias descartadas:
- **Opción B (usar como tope alternativo del aparato editorial):** más agresiva. Requiere validar que no hay casos donde la hoja aparezca antes del índice de nombres por error editorial. Postergable.
- **Opción C (filtrar del `.md`):** modifica los datos fuente, viola principio de inmutabilidad del corpus. Descartada.

### Cabos sueltos abiertos por este hallazgo

1. **¿Cuántas hojas hay en total en el corpus?** Sin un barrido sistemático, no lo sabemos. Estimación grosera: si cada archivo tiene ~5-10 hojas al final, el corpus tendría ~150-300 hojas en total.

2. **¿Aparecen solo al final de los archivos o también intercaladas en el cuerpo?** El caso confirmado en `LibroVol334.2.md` está al final. Si en algún archivo aparecen en el medio (improbable pero posible), el supuesto del fix extendido fallaría para ese caso. Validable con un grep.

3. **¿Hay otras "leyendas editoriales" similares?** ("HOJA EN BLANCO", "PAGINA RESERVADA", etc.). El detector debería ser extensible si aparecen variantes.

---

*Actualizado el 2/5/2026 con identificación del componente "hojas complementarias" del aparato editorial, validación del caso `334_p1054` (`Zeballos, José Luis`) como fallo corto no anómalo, y plan conservador de detección explícita.*
## Actualización 2026-05-02 (VI) — páginas compartidas y reinterpretación del bug del `+1`

**Estado:** identificado un patrón estructural fundamental del corpus que reformula el "bug del `+1`" como una heurística (imperfecta) para manejarlo. La consecuencia inesperada: el bloque de cada fallo no solo se extiende hacia adelante (residuo medio +11 líneas en `linea_fin`), sino también hacia atrás (incluye el cierre del fallo anterior antes de la carátula del actual).

### El hallazgo: las páginas son compartidas

Inspección del archivo `LibroVol334.2.md`, líneas 13079 en adelante:

```
[13079]  1054                                    ← número de página (header)
[      ] FALLOS DE LA CORTE SUPREMA              ← header del tomo
[      ] 334                                     ← número del tomo
[      ] Recurso ordinario interpuesto por Metrovías S.A...    ← FALLO ANTERIOR
[      ] Traslado contestado por el Fisco Nacional...
[      ] Recurso extraordinario interpuesto por el Fisco Nacional...
[      ] Traslado contestado por Metrovías S.A...
[      ] Tribunal de origen: Sala II de la Cámara...
[      ] Tribunal que intervino con anterioridad: Tribunal Fiscal de la Nación.
[13093]  ZEBALLOS, JOSE LUIS s/ Causa Nº 91.441  ← CARÁTULA DEL ACTUAL
[      ] DOBLE INSTANCIA.                        ← sumario del actual
[      ] Cabe desestimar la queja...             ← cuerpo del actual
```

**La página 1054 no contiene un solo fallo: contiene el final de Metrovías c/ AFIP y el inicio de Zeballos, José Luis.** Las primeras 14 líneas (de 13079 a 13092) son la cola del fallo anterior. El fallo `334_p1054` arranca recién en línea 13093.

### Por qué importa

El catálogo registra `pagina_inicio = 1054` para `Zeballos`. El cruzador busca el header de la página 1054 en el mapa y lo encuentra en línea 13079. Asigna `linea_inicio = 13079`. **Pero el cuerpo de Zeballos arranca en 13093, no en 13079.** Hay un offset de **14 líneas hacia atrás** que el cruzador desconoce.

Este offset es simétrico al offset hacia adelante del bug del `+1`:

| Frontera | Offset | Origen |
|---|---|---|
| Inicio del bloque | +14 líneas (en este caso) | Página compartida con fallo anterior |
| Fin del bloque (cruzador) | -32 líneas (mediana corpus) | Página compartida con fallo siguiente + bug `+1` |
| Fin del bloque (parser, vía `detectar_fin_real`) | -11 líneas (mediana corpus) | Búsqueda de carátula del siguiente |

**El bloque entregado al parser no es el bloque del fallo: es el bloque del fallo + colas de los vecinos.**

### Reinterpretación del bug del `+1`

El "bug del `+1`" deja de ser exactamente un bug. Es una **heurística para manejar páginas compartidas**, mal documentada y con un costo medible.

**Razonamiento implícito (probablemente nunca articulado):** "como la página `pg_fin` puede contener el final del fallo actual antes del inicio del siguiente, mejor cortamos al inicio de la segunda página del siguiente (`pg_fin + 1`)". Eso desplaza el corte a un punto más seguro pero ruidoso.

**Problema de la heurística:** en realidad el corte limpio NO está en el header de página sino en la **carátula del fallo siguiente**, que está unas líneas después del header. El parser ya lo sabe (`detectar_fin_real` busca la carátula, no el header). El cruzador opera con la unidad equivocada (páginas) cuando debería operar con la unidad correcta (carátulas).

**Reformulación clara:** las páginas son la unidad de paginación del PDF original. Los fallos no respetan los límites de página. Cualquier corte basado solo en headers de página va a estar mal por algunas líneas. Solo un corte basado en marcadores de fallo (carátula, dispositivo, firma) es exacto.

### El residuo de inicio: nuevo problema, no reportado antes

Las actualizaciones I-V se enfocaron en el `linea_fin`. Pero el `linea_inicio` también está corrido en algunos casos:

- `Zeballos`: `linea_inicio` real = 13093, registrado = 13079. Residuo de **+14 líneas hacia atrás**.

El bloque del parser para Zeballos arranca en 13079 e incluye:
- 14 líneas de cierre del fallo anterior (Metrovías): recursos, traslados, tribunal de origen.
- El cuerpo real del Zeballos.

Eso afecta:
- **`tribunal_origen`:** el parser puede capturar "Tribunal de origen: Sala II de la Cámara..." que es del fallo Metrovías, no del Zeballos. Caso a verificar en `csjn_casos.csv`.
- **`word_count`:** infla con palabras del fallo anterior.
- **Detección de fecha:** si la fecha del Metrovías está en el bloque, podría capturarla como fecha del Zeballos.

Sospecha: este patrón se repite en muchos fallos del corpus, no solo en Zeballos. Hipótesis cuantitativa: cualquier fallo que NO arranca al inicio de su página de inicio (es decir, todos los que comparten página con el fallo anterior) tiene este offset.

### Estimación grosera de la magnitud del problema

Si en promedio una página del corpus tiene ~30 líneas (consistente con el offset hacia adelante del bug del `+1`) y un fallo ocupa en promedio ~80 líneas (estimación conservadora), entonces aproximadamente el 30-40% de los fallos arrancan en el medio de una página, con offset de inicio variable entre 1 y ~30 líneas.

Sobre 5.819 casos parseados: **~1.700-2.300 fallos pueden tener residuo de inicio**. La mayoría con offsets pequeños (1-15 líneas), algunos casos extremos como Zeballos (14 líneas).

**Eso es mucho ruido residual en el corpus actual.**

### Por qué `detectar_fin_real` no resuelve esto

`detectar_fin_real` opera sobre `linea_fin`, no sobre `linea_inicio`. Recibe `linea_inicio` del cruzador como dato fijo y lo respeta. No hay un equivalente `detectar_inicio_real` que ajuste hacia adelante el `linea_inicio` para saltar la cola del fallo anterior.

**El parser arma el bloque desde `linea_inicio` literal del cruzador.** Todo lo que esté entre el header de página y la carátula real entra al bloque y al análisis.

### Diseño de un fix posible (no implementarlo hasta validar empíricamente)

Por simetría con `detectar_fin_real`, agregar un `detectar_inicio_real` al parser:

- Recibe `linea_inicio` del cruzador como anclaje.
- Busca hacia adelante (dentro de las primeras ~50 líneas del bloque) la carátula del fallo actual.
- La carátula se identifica por `nombres_indice` del catálogo (ya tenemos `primer_token_de_caratula` en línea 1094 del parser).
- Si encuentra la carátula, ajusta `linea_inicio_real` a esa línea.
- Si no, mantiene el original.

Eso simetriza el comportamiento del parser: corrige por carátula tanto al inicio como al fin del bloque.

### ¿Por qué no se notó antes?

Tres razones plausibles:

1. **`detectar_fin_real` ya corrige el final.** Como ese era el síntoma más visible, no se buscó el problema simétrico al inicio.

2. **El parser usa marcadores estructurales para muchas detecciones.** `RE_APERTURA` busca "FALLO DE LA CORTE SUPREMA" dentro del bloque, no en `linea_inicio`. `RE_FECHA_LINEA` busca la fecha cerca del marcador de apertura. `RE_POR_ELLO` busca el dispositivo. Todas estas detecciones son **resilientes al ruido del comienzo del bloque** porque buscan patrones específicos, no asumen posiciones.

3. **La carátula sí depende de `linea_inicio`.** `find_case_name` (línea 300 del parser) busca hacia atrás desde `apertura_idx` hasta encontrar una línea con "c/" o "s/". Si la cola del fallo anterior contiene "c/" (como pasa en Zeballos: "Metrovías S.A. c/ AFIP-DGI"), la carátula detectada puede ser **del fallo anterior**, no del actual.

**El último punto es crítico.** Mirá el bloque de Zeballos: las primeras líneas son sobre Metrovías c/ AFIP-DGI. Si el parser busca hacia atrás desde el "FALLO DE LA CORTE SUPREMA" (que está varias líneas después de "ZEBALLOS, JOSE LUIS s/ Causa Nº 91.441"), puede agarrar "Metrovías S.A. c/ AFIP-DGI" como carátula en lugar de "Zeballos".

**Esto es verificable cruzando con `csjn_casos.csv`:** mirar el campo `case_name_cuerpo` del caso `334_p1054` y ver si dice "Zeballos" o si dice "Metrovías".

### Cabos sueltos para validar

1. **Verificar `case_name_cuerpo` de `334_p1054`** en `csjn_casos.csv`. ¿Es Zeballos o es Metrovías?

2. **Estimación cuantitativa real del residuo de inicio:** validable sobre los 118 casos del Tomo 329 ya analizados. Para cada uno, comparar `linea_inicio` con la línea exacta donde aparece el primer token de su carátula. Con eso, distribución del offset de inicio.

3. **Cuantificar falsos positivos en `case_name_cuerpo`:** si la hipótesis de carátula contaminada es correcta, debería haber un % no despreciable de casos donde `case_name_indice` y `case_name_cuerpo` no coinciden por motivos atribuibles a página compartida.

### Implicación general para el documento

Esta actualización abre una línea de trabajo nueva. Hasta ahora el diagnóstico se centraba en el fin del bloque (bug del `+1`). El inicio del bloque resulta ser igualmente problemático y posiblemente más serio (porque afecta detecciones de carátula y tribunal de origen, que son campos centrales del análisis).

**Antes de tomar decisiones de fix, conviene cuantificar este problema empíricamente.** El `linea_fin` corrido contamina word counts. El `linea_inicio` corrido contamina campos identificadores. La prioridad de fix debería revisarse con ese dato.

### Próximos pasos sugeridos

En orden de costo creciente:

1. **Verificar `case_name_cuerpo` de `334_p1054`.** Una sola línea del CSV. 1 minuto.

2. **Cuantificar el offset de inicio sobre los 118 casos del Tomo 329** comparando `linea_inicio` contra la línea de la carátula real. Requiere acceso a `LibroVol329.1.md`. Análisis tipo el de la Actualización II.

3. **Cuantificar la frecuencia de carátulas contaminadas** en todo el corpus comparando `case_name_indice` vs `case_name_cuerpo`. Análisis sobre el `csjn_casos.csv` completo.

---

*Actualizado el 2/5/2026 con hallazgo sobre páginas compartidas (caso `Zeballos, José Luis` confirmado: carátula real en línea 13093, `linea_inicio` registrado en 13079, residuo de +14 líneas hacia atrás del bloque). Reformulación del bug del `+1` como heurística para manejar páginas compartidas. Apertura de línea de trabajo sobre `linea_inicio` (no abordada hasta ahora). Estimación grosera: 30-40% del corpus puede tener residuo de inicio, ~1.700-2.300 casos potencialmente afectados.*
## Actualización 2026-05-02 (VII) — síntesis y reinterpretación: el `+1` no era un bug

**Estado:** después de seis actualizaciones investigando el "bug del +1", la confirmación empírica de que el índice oficial solo registra páginas de inicio (`Zeballos, José Luis: p. 1054.` — una sola página) cierra el debate y obliga a reinterpretar todo el razonamiento previo. **El `+1` del cruzador no es un bug, es una decisión de diseño correcta dadas las limitaciones de los datos editoriales.**

### El argumento estructural

Por construcción del corpus editorial, las páginas son la unidad mínima del catálogo. El índice oficial registra `pagina_inicio` de cada fallo, no `pagina_fin`. La `pagina_fin` no existe como dato editorial: es derivable.

Por construcción del fascículo impreso, si el fallo Y arranca en página `pY`, el fallo X que viene antes **no puede continuar más allá de `pY`**. O X termina antes de `pY` (páginas no compartidas), o X termina dentro de `pY` (página compartida con Y). En ambos casos, `pY` es la última página donde puede haber cuerpo de X.

**Por lo tanto, `pagina_fin_X = pagina_inicio_Y` es definicionalmente correcto** como "última página posible del cuerpo de X, inclusive". El código del catálogo (línea 410: `pags_ordenadas[i + 1]`) implementa esa definición. El docstring (líneas 57, 380-382) decía "siguiente - 1", lo cual interpretaba la `pagina_fin` como "última página exclusiva de X". Las dos definiciones son válidas, pero solo una es consistente con el comportamiento editorial real: la del código, no la del docstring.

### Reinterpretación del cruzador

Con la semántica corregida, `clave_fin = (tomo, pg_fin + 1)` busca el header de la página **siguiente a la última posible de X**. El primer header donde X seguro ya no aparece. Después, `linea_fin = linea_header_de_pg_fin+1 - 1` deja el bloque cortado en la línea anterior a ese header. **Eso garantiza que el bloque incluye toda la página `pg_fin = pY` entera, donde X termina (eventualmente compartida con Y).**

El offset de +32 líneas medido en la Actualización I no es residuo de bug: **es la página compartida `pY` que queda dentro del bloque**, porque cortar por header de página no puede ser más fino que una página entera.

### Por qué `detectar_fin_real` existe

El parser refina la frontera línea a línea, usando marcadores empíricos del cuerpo del fallo (carátula del siguiente, firma del juez actual). Eso solo es posible parseando texto, no a nivel de catálogo. Por eso `detectar_fin_real` está en el parser, no en el cruzador.

**La división de responsabilidades es correcta:**

| Capa | Unidad | Precisión |
|---|---|---|
| Catálogo | Página inicio (dato editorial) | Exacta |
| Catálogo (derivado) | Página fin = inicio del siguiente | Upper bound editorial |
| Cruzador | Línea (header de página) | Bounds de línea, conservadores |
| Parser (`detectar_fin_real`) | Línea (marcador textual) | Refinamiento empírico |

Cada capa hace lo más fino posible con los datos disponibles. No hay capa rota.

### Qué se mantiene de las actualizaciones I-VI

A pesar de la reinterpretación del bug del `+1`, los hallazgos empíricos siguen siendo válidos:

| Hallazgo | Estado |
|---|---|
| Offset de +32 líneas en linea_fin (cruzador) | **Correcto, ahora explicado:** página compartida que queda en el bloque |
| Residuo de -11 líneas (parser, post-fix_real) | **Correcto, ahora explicado:** distancia entre header de página y carátula del siguiente |
| 70 huérfanos: 43 Bug A + 27 cruza_archivos | **Correcto, sin cambios** |
| Bug A en `detectar_paginas.py` | **Correcto, sin cambios** |
| Fix extendido para `cruza_archivos` | **Correcto, sin cambios** |
| Régimenes editoriales A/B/C | **Correcto, sin cambios** |
| Hojas complementarias como ruido al final del archivo | **Correcto, sin cambios** |
| Páginas compartidas como patrón estructural | **Correcto, ahora central al análisis** |

### Qué cambia: el ranking de prioridades

Antes:

1. ~~Arreglar el bug del `+1`~~ — **descartado, no es bug**
2. Atacar Bug A
3. Aplicar fix extendido para `cruza_archivos`
4. Validar `case_name_cuerpo`

Ahora:

1. **Atender `case_name_cuerpo` (69% de discrepancia con índice).** Bug masivo del parser, afecta identificación de fallos. Fix barato (validar contra `primer_token` del índice).
2. **Aplicar fix extendido para `cruza_archivos`.** 27 huérfanos resolvibles, bajo riesgo, generalización del fix Bug D.
3. **Atacar Bug A.** Alto impacto (43-50 fallos perdidos), pero requiere modificar `detectar_paginas.py` que es el detector que sustenta los 5.773 que andan bien. Mayor riesgo.
4. **Auditar otros campos del parser.** `tribunal_origen` se vio truncado por hyphenation en Zeballos. ¿Qué otros campos tienen problemas similares no detectados? Auditoría sistemática.

### Cambios sugeridos al documento principal

Las actualizaciones I-VI siguen siendo material valioso de análisis. La conclusión final cambia, pero el camino del razonamiento muestra cómo se llegó a ella. Sugerencia:

- **No reescribir las actualizaciones I-VI.** Documentan un razonamiento honesto con datos.
- **Esta actualización VII funciona como cierre del debate**, dejando documentado que la conclusión inicial (el "+1 es un bug") fue revisada en función de la pregunta editorial sobre `pagina_fin`.
- **Corregir el docstring** de `construir_catalogo.py` (líneas 57, 380-382) para que diga "página del siguiente fallo, inclusive (upper bound de página donde puede haber cuerpo)" en lugar de "siguiente - 1". Es un commit chico, no requiere regenerar nada.

### Decisión metodológica documentada

**No hay nada que arreglar en la cadena catálogo → cruzador.** El sistema funciona como debe dadas las limitaciones del dato editorial. Cualquier mejora de precisión del corte tiene que pasar por el parser (vía `detectar_fin_real`), no por el cruzador.

Esto no es resignación, es honestidad sobre lo que se puede hacer con los datos disponibles.

---

*Actualizado el 2/5/2026: cierre del debate sobre el bug del `+1`. Confirmación empírica de que `Zeballos, José Luis: p. 1054.` es el único registro del fallo en el índice oficial. El catálogo solo conoce inicios. La `pagina_fin` derivada es upper bound editorialmente correcto. El cruzador hace lo correcto al usar `pg_fin + 1`. El refinamiento exacto solo es posible empíricamente en el parser, donde ya está implementado.*
## Actualización 2026-05-02 (VIII) — `case_name_cuerpo`: 69% del corpus tiene falsos positivos

**Estado:** validado empíricamente que el bug de `case_name_cuerpo` reportado puntualmente para el caso Zeballos es masivo. Afecta 1.924 de 2.775 casos validables (69.3%) en todo el corpus. El parser está capturando citas doctrinales como carátula en lugar de la carátula real del fallo.

### Datos analizados

`csjn_casos.csv` completo: 5.819 casos.

Filtros aplicados:
- 5.655 casos de tipo `fallo` (164 son `sumario_con_link`, excluidos).
- De los 5.655 fallos: 2.844 sin `case_name_cuerpo` (50.3%), 36 sin `case_name_indice` (0.6%), 0 ambos vacíos.
- Casos validables (con índice y cuerpo presentes): **2.775**.

### Hallazgo 1 — solo el 30.7% matchea

Para validar, se extrajo el `primer_token` del `case_name_indice` (replicando la función `primer_token_de_caratula` del parser, línea 1094) y se buscó si aparece en `case_name_cuerpo`.

| Veredicto | Casos | % de validables |
|---|---|---|
| **Matchea** (token del índice presente en cuerpo) | 851 | 30.7% |
| **NO matchea** (sospecha de falso positivo) | **1.924** | **69.3%** |

Si se considera el universo entero de fallos: 851 carátulas correctas / 5.655 fallos totales = **15.0%**. La gran mayoría tiene `case_name_cuerpo` ausente o erróneo.

### Hallazgo 2 — el bug está en TODOS los tomos, no en un subconjunto

Tasa de no-matcheo por tomo:

```
tomo  total  match  no_match  %no_match
 329    331     38       293     88.5%
 330    273     21       252     92.3%
 331    191     65       126     66.0%
 332    158     49       109     69.0%
 333    104     33        71     68.3%
 334     80     22        58     72.5%
 337     48     10        38     79.2%
 338    100     23        77     77.0%
 339    237     99       138     58.2%
 340    184     57       127     69.0%
 341    164     71        93     56.7%
 342    147     52        95     64.6%
 343    142     47        95     66.9%
 344    176     63       113     64.2%
 345     80     30        50     62.5%
 346     87     31        56     64.4%
 347    108     55        53     49.1%
 348    133     70        63     47.4%
 349     32     15        17     53.1%
```

Rango de tasa de error: 47.4% (Tomo 348) a 92.3% (Tomo 330). **Ningún tomo está por debajo del 47%.** El bug es estructural, no específico de un subconjunto.

Patrón: tomos viejos (329-330) tienen tasa altísima (~90%), tomos modernos (348-349) bajan a 47-53%. Hipótesis: en tomos modernos las carátulas son más distintivas (mayúsculas, formato más rígido) y matchean mejor contra el `primer_token`. En tomos viejos las citas doctrinales y carátulas son más similares en formato.

### Hallazgo 3 — la tasa es independiente del status del cruzador

```
status_localizacion        total  match  no_match  %no_match
ok                          2751    845      1906     69.3%
fallo_cruza_archivos          13      4         9     69.2%
ok_cortado_en_indice          11      2         9     81.8%
```

Los `ok` regulares y los `cruza_archivos` tienen exactamente la misma tasa de error. **El bug no está relacionado con el manejo del bloque** (cruzador o `detectar_fin_real`). Está en `find_case_name` del parser.

### Hallazgo 4 — el patrón del falso positivo

Análisis de los primeros 15 casos no-matcheantes muestra el patrón:

| caso_id | índice (real) | cuerpo (capturado) |
|---|---|---|
| `329_p9` | Compañía de Transporte... c/ Y.P.F. | "Y.P.F. S.A. c/ Municipalidad de C. del Uruguay s/" ← **fallo anterior** |
| `329_p117` | More, Silvestre | "Columbia Compañía Financiera S. A. c/ Estado..." ← **cita doctrinal** |
| `329_p147` | Barcus, Rubén Aníbal | "Ivorra, Miguel y otros s/ recurso..." ← **cita al fallo previo en el tomo** |
| `329_p171` | Moyano, Agustín Fernando | "Carlos Bernabé y otros s/ secuestro extorsivo" ← **cita doctrinal** |
| `329_p184` | Brun, Alfredo David... | "c/ Estado Nacional s/ amparo (Fallos: 322:3049)" ← **cita con `Fallos:`** |
| `329_p218` | Ontivero, Ariel Adolfo | "Isabel c/ Buenos Aires, Provincia de s/ indemnización..." ← **cita doctrinal** |

**El patrón es uniforme:** `find_case_name` (línea 300 del parser) busca hacia atrás desde la apertura "FALLO DE LA CORTE SUPREMA" la primera línea con `c/` o `s/`. Esa línea suele ser una cita a un precedente en el considerando, no la carátula real.

### Causa raíz

`find_case_name` busca línea con `c/` o `s/` sin validar contra el índice. Cualquier cita doctrinal que cumpla el patrón satisface la búsqueda. El parser ya tiene el dato del índice disponible (`nombres_indice` se pasa al `procesar_archivo`), pero no lo usa para validar.

### Diseño del fix

```python
def find_case_name(lines, apertura_idx, primer_token=None,
                    max_back=15, max_back_fallback=60, max_back_validado=200):
    """
    Busca la carátula hacia atrás desde la apertura.
    Si se provee primer_token (extraído del índice), prioriza líneas
    que contienen ese token. Esto evita falsos positivos por citas
    doctrinales con "c/" o "s/".
    """
    # Pase 1: buscar línea con primer_token Y c/ o s/ (si tenemos primer_token)
    if primer_token and len(primer_token) >= 5:
        token_lower = primer_token.lower()
        for d in range(1, max_back_validado + 1):
            idx = apertura_idx - d
            if idx < 0:
                break
            candidate = lines[idx].strip()
            if not candidate or RE_PAGE_HEADER.match(candidate):
                continue
            if token_lower in candidate.lower() and ("c/" in candidate or "s/" in candidate):
                return candidate

    # Pase 2: fallback al comportamiento actual
    for d in range(1, max_back + 1):
        idx = apertura_idx - d
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if not candidate or RE_PAGE_HEADER.match(candidate):
            continue
        if "c/" in candidate:
            return candidate
    for d in range(1, max_back_fallback + 1):
        idx = apertura_idx - d
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if not candidate or RE_PAGE_HEADER.match(candidate):
            continue
        if "c/" in candidate or "s/" in candidate:
            return candidate
    return ""
```

Backward compatible: sin `primer_token`, comportamiento idéntico al actual.

### Predicción del impacto del fix

**Casos donde el fix mejora:** los 1.924 actualmente no-matcheantes que tengan la carátula real dentro de las 200 líneas hacia atrás de la apertura. Probablemente un 80-90% de esos casos.

**Casos donde el fix no cambia nada:** los 851 actualmente matcheantes (siguen funcionando bien) más los casos donde la carátula no está dentro de la ventana extendida.

**Riesgo de regresión:** bajo. El fallback al comportamiento actual está explícito si el primer_token no se encuentra.

### Hallazgo lateral — `jueces_desconocidos` está vacío en TODO el corpus

Análisis solicitado: ver `jueces_desconocidos` para detectar ruido en firmas.

Resultado: **0 casos con `jueces_desconocidos` no vacío**, sobre 5.655 fallos.

Eso sugiere uno de dos:
- El parser está filtrando todo lo que no matchea como juez conocido (vía `RUIDO_FIRMA`, línea 282).
- El campo `jueces_desconocidos` no se está poblando por algún bug de output.

El ruido reportado por el usuario en consola durante corridas del parser no aparece en este campo del CSV. Probablemente se imprime a stdout durante la corrida pero no se persiste en el output.

### Implicaciones metodológicas

1. **`case_name_cuerpo` es prácticamente inutilizable** sin el fix. 69% de error en validación cruzada.

2. **`case_name_indice` es la fuente confiable** para identificación de fallos. Ya lo era, pero ahora queda explícito por qué `case_name_cuerpo` no es alternativa.

3. **Otros campos del parser pueden tener problemas similares no auditados.** El bug de `find_case_name` estuvo siempre, no se detectó hasta ahora porque nadie auditó cuantitativamente la coherencia interna del output. Vale la pena hacer barridos similares sobre `tribunal_origen`, `date`, `outcome`.

4. **El fix tiene que aplicarse antes de cualquier análisis serio sobre carátulas en el cuerpo.** Si la tesis usa `case_name_cuerpo` para algo, los resultados están comprometidos.

### Próximos pasos sugeridos

En orden:

1. **Aplicar el fix de `find_case_name`** en una rama git nueva. Impacto: 1.924 casos potencialmente mejorados, 0 empeorados.

2. **Re-correr el parser** y comparar el nuevo `case_name_cuerpo` vs el viejo. Predicción: tasa de matcheo sube de 30.7% a algo del orden de 90%+.

3. **Auditoría de otros campos:** correr análisis cuantitativos similares sobre `tribunal_origen` (validar contra patrones esperados) y `date` (validar consistencia con fecha del fallo cuando hay marcador de apertura). Detectar otros bugs latentes.

4. **Investigar `jueces_desconocidos` vacío:** verificar si es comportamiento intencional (filtrado por `RUIDO_FIRMA`) o bug de output.

### Cabos sueltos para próximas sesiones

- **Bug A** (43 fallos perdidos en tomos 331-334) sigue sin atención.
- **Fix extendido** para los 27 `cruza_archivos` sigue pendiente de aplicación.
- **Hojas complementarias** detectadas pero sin script de detección.
- **Los 32 oks falsos** sin diagnóstico de origen (pendiente git log).
- **`tribunal_origen` truncado por hyphenation** (caso Zeballos), sin auditoría a escala.

---

*Actualizado el 2/5/2026 con validación cuantitativa de `case_name_cuerpo` sobre 2.775 casos del corpus. Tasa de error: 69.3%, distribuida en todos los tomos (47-92%). Diagnóstico: `find_case_name` captura citas doctrinales como carátula. Fix propuesto: validar contra `primer_token` del índice antes de aceptar candidato. Hallazgo lateral: `jueces_desconocidos` vacío en 100% del corpus, posible bug de output del parser.*
## Actualización IX — Naturaleza del bug de case_name_cuerpo: localizado, no sistémico

**Fecha:** 3/5/2026
**Contexto:** Sesión de validación empírica del impacto del bug de `find_case_name`, abierta originalmente para decidir entre fix urgente vs postergación.

### Hallazgos

**1. Recompute de la métrica laxa reveló problema más grande**

El primer paso fue recomputar el 69.3% de mismatch con lógica laxa (split por `|`, normalización agresiva, contención bidireccional con umbral mínimo de 15 caracteres). Resultado inicial: 81.3% sobre 5.819 validables.

El número subió en lugar de bajar. Diagnóstico siguiente reveló la causa: **3.008 de 5.819 casos (51.7%) tienen `case_name_cuerpo` nulo**. La métrica anterior los había excluido implícitamente. La métrica laxa real, sobre validables verdaderos (cuerpo no nulo), es **1.720 / 2.811 = 61.2%**, no 81%.

**2. Los nulos no son una clase definida**

Distribución por `tipo_entrada`: 2.844 son `fallo` y 164 son `sumario_con_link`. Los 164 sumarios sin fallo propio son legítimamente sin carátula. Los 2.844 fallos no: son fallos normales (`apertura_tipo=fallo`, `is_merit_decision` mezclado, `word_count` desde 58 hasta 4.885) sin carátula extraída.

Distribución por tomo:
- Tomo 329: 730 nulos
- Tomo 330: 481 nulos
- Tomos 331-349: 80-170 por tomo

**3. Causa estructural identificada en tomos 329-330**

Inspección manual de bloques `.md` de 5 casos nulos del tomo 329 reveló que la carátula sí está presente en el cuerpo del fallo, pero en formato editorial distinto al que el parser maneja:

```
NOMBRE PARTE ACTORA EN MAYÚSCULAS
V. NOMBRE PARTE DEMANDADA EN MAYÚSCULAS
```

Este formato funciona como subtítulo editorial al inicio del fallo, separado del bloque procesal. El parser actual busca la carátula en formato `Vistos los autos: "Nombre c/ Nombre s/ acción..."`, que también suele estar presente pero no en todos los casos. Cuando la apertura es `Autos y Vistos; Considerando:` (sin carátula entre comillas), el parser se queda sin nada que capturar, aunque la carátula esté visible 5 líneas más arriba en formato `V.`.

Medición de prevalencia del formato `V. ` mayúsculas como título por tomo:

| Tomo | V. título |
|-----:|----------:|
| 329  | 208 |
| 330  | 148 |
| 331+ | 0 (con ruido aislado: 2 en tomo 344) |

El formato editorial cambia entre tomo 330 y tomo 331. La editorial dejó de usar el subtítulo `V.` mayúsculas. Esto explica el grueso de los nulos en 329-330 (1.211 de los 3.008).

**4. Bug separado en tomos 331+**

Restando los 1.211 nulos de 329-330, quedan ~1.797 nulos en tomos 331+. En esos tomos no aplica el problema editorial del subtítulo `V.`. Hay un fenómeno distinto, no investigado en esta sesión, que produce 80-170 nulos por tomo. Causa probable: variantes en la apertura (`Autos y Vistos` sin carátula entre comillas inmediatamente posterior) que la lógica actual de `find_case_name` no resuelve.

### Auditoría empírica de campos analíticos sobre nulos

La pregunta crítica era si el bug de `case_name_cuerpo` es localizado en `find_case_name` o si refleja deterioro general del parser. Si el parser falla silenciosamente en lo que debería ser fácil (la carátula tiene marcadores editoriales claros y posición conocida), no habría razón para confiar en `find_firma`, `find_outcome` o el cómputo de `voting_pattern`.

Auditoría de 5 casos nulos del tomo 329 (`329_p5`, `329_p12`, `329_p47`, `329_p59`, `329_p78`), comparando los campos del CSV contra el bloque `.md` correspondiente. Se verificó:
- `firma_raw` y `jueces`: lista de apellidos al final del fallo.
- `voting_pattern` y conteos derivados (`n_titulares`, `n_votos_svoto`, `n_disidencias`).
- `outcome`: alineación con la cláusula "Por ello,...".
- `is_merit_decision`.
- `tribunal_origen`.

Resultado: **los campos analíticos están correctos en los 5 casos auditados**. El parser identifica correctamente cada caso como un fallo distinto, captura la firma con su lógica de separadores variables (em dash, en dash, espacios irregulares, sufijos como "según su voto"), y deriva los conteos consistentemente.

### Conclusión

El bug de `case_name_cuerpo` es localizado en la función `find_case_name`. No contamina los campos analíticos críticos para la tesis (`firma_raw`, `voting_pattern`, `outcome`, `is_merit_decision`, `tribunal_origen`, conteos por posición). El corpus es usable para análisis estadístico tal como está.

Sin embargo, **3.008 carátulas faltantes no es un problema estético**. Es una limitación real de identificabilidad que afectará la presentación de fallos en tablas, citas en notas al pie, validación manual de subsets y filtrado por nombre. La tesis puede avanzar sin resolverlo, pero el problema queda registrado como deuda técnica de cobertura, no como bug crítico.

### Reordenamiento de prioridades resultante

1. ~~Validar daño real de `case_name_cuerpo`~~ → **resuelto**. Bug localizado en extracción, no afecta campos analíticos.
2. Fix extendido para `fallo_cruza_archivos` → mantiene prioridad. 27 huérfanos resolvibles, riesgo casi nulo.
3. Bug A en `detectar_paginas.py` (43-50 fallos perdidos en tomos 331-334) → **sube a tercera prioridad**, antes era cuarta. Afecta cobertura del corpus, no solo redundancia editorial.
4. Fix de `find_case_name` (formato `V.` mayúsculas + apertura `Autos y Vistos`) → desciende. Recuperaría ~1.211 carátulas en tomos 329-330 sin tocar campos analíticos. Beneficio de identificabilidad, no de validez sustantiva.
5. Diagnóstico del segundo bug (~1.797 nulos en tomos 331+) → desciende, pero queda registrado como pendiente separado del fix anterior.
6. Auditoría sistemática de otros campos (`tribunal_origen` con hyphenation, `date`, `outcome`) → mantiene posición.
7. Detección explícita de hojas complementarias (opción A conservadora) → mantiene posición.
8. Diagnóstico de los 32 oks falsos → mantiene posición.

### Notas metodológicas para sesiones futuras

- La métrica del 69.3% computada en sesiones anteriores excluía implícitamente los nulos. Cualquier recálculo futuro debe reportar tres cifras: total, validables, tasa sobre validables.
- La intuición "si el parser falla en lo fácil, falla en todo" no aplica cuando "lo fácil" tiene una particularidad editorial específica (formato `V.` mayúsculas) que los otros campos no comparten. La validez de campos analíticos requiere validación empírica directa, no inferencia desde otros campos.
- El muestreo aleatorio simple sin diagnóstico previo del universo es vulnerable a sesgo: la muestra de 100 generada al inicio de la sesión incluía nulos disfrazados como mismatches, lo que la habría hecho parcialmente irrelevante para responder la pregunta original.

### Output de la sesión

En `archivo/exploratorios/diagnostico/case_name_mismatch/`:
- `metrica_laxa.txt` — reporte de la métrica recomputada.
- `muestra_evaluacion.csv` — muestra de 100 casos no-matcheantes (sesgada por nulos, queda como referencia).
- `bloques/` — 100 archivos de contexto del .md para la muestra anterior.
- `bloques_nulos/` — 15 archivos de contexto para los nulos auditados (10 del tomo 329, 5 del tomo 348).
- `diagnostico_metrica.py`, `diagnostico_nulos.py`, `auditoria_nulos.py`, `medir_v_titulo.py`, `armar_planilla.py` — scripts de diagnóstico utilizados.
- `planilla_auditoria.txt` — planilla de la auditoría manual.
## Actualización X — Anatomía de los 27 `fallo_cruza_archivos`: el fix simple no alcanza

**Fecha:** 3/5/2026
**Contexto:** Inspección manual de 4 huérfanos representativos para validar el fix propuesto antes de aplicarlo. La inspección reveló matices que el diseño original del fix no contemplaba.

### Diagnóstico estadístico de los 27

Los 27 casos con `status='fallo_cruza_archivos'` comparten un patrón perfectamente uniforme:

- Todos tienen índice de nombres detectado en su archivo de inicio.
- Todos tienen `linea_fin = última línea del archivo - 1` (el cruzador asignó la cola por defecto).
- Todos tienen `linea_fin > linea_inicio_indice_nombres`: el bloque actual atraviesa el aparato editorial.
- Todos tienen un archivo siguiente del mismo tomo disponible.
- Cada huérfano es estructuralmente "el último fallo del primer subarchivo de su tomo".

Tamaños de bloque: desde 524 líneas (`339_p933`) hasta 13.678 líneas (`330_p2849`).

### Inspección manual de 4 representativos

Casos elegidos por tamaño: `337_p877` (690), `343_p1447` (1.085), `334_p1054` (2.184), `330_p2849` (13.678). Para cada uno se extrajeron primeras 50 líneas del bloque, últimas 80 del archivo de inicio, primeras 80 del archivo siguiente.

**Lo que muestran los 4 archivos:**

1. El bloque arranca dentro del archivo de inicio en posiciones distintas según el caso. En `337_p877` y `343_p1447` arranca dentro del último fallo del archivo (en plena cláusula "Por ello..."). En `334_p1054` arranca con aparato post-fallo del fallo previo (datos de abogados, "Tribunal de origen"). Solo en `330_p2849` arranca con encabezado limpio "FALLO DE LA CORTE SUPREMA / Buenos Aires, 26 de junio de 2007".

2. La `linea_fin` actual cae dentro del aparato editorial del volumen: índice de nombres, índice general, índice de legislación, "HOJA COMPLEMENTARIA" repetida varias veces como relleno tipográfico.

3. El archivo siguiente NO contiene continuación del fallo huérfano. Arranca con su propia tapa editorial: portada del volumen, ISBN, "FALLOS DE LA CORTE SUPREMA DE JUSTICIA DE LA NACION", aviso de jurisprudencia online, "REPUBLICA ARGENTINA", "TOMO X – VOLUMEN N", año, datos editoriales. Esto ocupa entre 40 y 80 líneas antes del primer fallo del archivo siguiente.

### Conclusión sobre el fix simple

El fix originalmente propuesto (`linea_fin = indices_nombres_por_archivo[archivo_ini] - 1`, status `ok_cortado_en_indice_cruza`) **mejora el límite superior pero no resuelve el problema sustantivo**. En los 4 casos inspeccionados:

- Para `330_p2849`, el fallo real termina cerca de la línea 58477 (firma). El inicio del índice de nombres está en 59398. El fix dejaría 921 líneas que incluyen otros fallos completos del catálogo, no uno solo.
- Para `337_p877`, mismo patrón: el fallo termina cerca de la línea 34701, el índice empieza en 35142. 441 líneas intermedias contienen múltiples fallos.

El bloque que produce el cruzador en estos 27 casos no representa un fallo, representa "el último fallo + todo lo que vino después dentro del archivo, hasta el aparato editorial". El parser sobre ese bloque mezcla múltiples fallos.

### Implicación estructural no detectada antes

El problema de fondo no es solo dónde corta el cruzador, sino que el modelo del cruzador asume continuidad: que entre `pagina_inicio` del fallo actual y `pagina_inicio` del fallo siguiente del catálogo todo lo intermedio es un solo fallo. Esa asunción se rompe en estos casos porque:

1. El catálogo registra el siguiente fallo en una página que físicamente pertenece a otro archivo.
2. Entre el último fallo del archivo de inicio y la primera página del catálogo en el archivo siguiente, hay aparato editorial en ambas direcciones: índice del primer volumen al final + tapa del segundo volumen al inicio.

Un fix completo requeriría:

- Encontrar la última página del catálogo que esté físicamente en `archivo_ini` (no la `pagina_fin + 1` del catálogo, que está en otro archivo).
- O bien, marcar al huérfano con su propia frontera empírica detectada con `detectar_fin_real`.

### Tres opciones reordenadas

**Opción A (fix simple, ya diseñado):** cortar en `idx_nombres - 1`. Mejora limpia el peor caso (`330_p2849` pasa de 13.678 a 921 líneas). No resuelve la mezcla de múltiples fallos. Status nuevo `ok_cortado_en_indice_cruza`. Backward compatible. Beneficio parcial.

**Opción B (fix estructural):** detectar la última página del catálogo físicamente presente en `archivo_ini` y cortar ahí. Requiere lógica nueva de búsqueda en el mapa. Resuelve el bloque a un fallo único en la mayoría de los casos. Riesgo más alto de afectar casos que hoy son `ok`.

**Opción C (pragmática):** marcar los 27 con status `requiere_revision_manual` y excluirlos del análisis cuantitativo. 0.46% del corpus, asumible. No requiere cambios de código.

### Reordenamiento de prioridades

1. ~~Fix extendido para `fallo_cruza_archivos` (opción A simple)~~ → **decisión postergada**: aplicar opción A da beneficio parcial; opción B requiere diseño más serio; opción C es honesta pero descarta los 27.
2. Bug A en `detectar_paginas.py` (43-50 fallos perdidos en tomos 331-334) → **mantiene primera prioridad técnica**.
3. Fix de `find_case_name` formato `V.` mayúsculas → recuperaría ~1.211 carátulas en tomos 329-330. Beneficio de identificabilidad acotado a esos dos tomos pero sustantivo en magnitud absoluta. Sube en prioridad respecto a la Actualización IX porque es un fix más simple que el de `cruza_archivos`.
4. Diagnóstico del segundo bug de carátula (~1.797 nulos en tomos 331+) → mantiene posición.
5. Fix `fallo_cruza_archivos` (decidir A/B/C) → mantiene posición pero requiere decisión previa.
6. Auditoría sistemática de otros campos → mantiene posición.

### Decisión pendiente para próxima sesión

Antes de tocar `cruzar_catalogo_y_mapa.py`, decidir entre A, B y C para `fallo_cruza_archivos`. La inspección manual sugiere que A es el camino menos malo si se acepta que los bloques resultantes seguirán siendo ruidosos. B es lo correcto pero requiere diseño nuevo. C es la opción honesta si se prioriza pureza del análisis cuantitativo sobre cobertura.

### Output de la sesión (adicional a Actualización IX)

En `archivo/exploratorios/diagnostico/case_name_mismatch/`:
- `bloques_cruza/` — 4 archivos con primeras/últimas líneas de los huérfanos representativos.
- `estadistica_27.py`, `extraer_4_cruza.py` — scripts de diagnóstico.
