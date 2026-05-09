# Pipeline corpus-csjn

> **Estado del documento**: borrador en construcción.
> Sesiones: 2026-05-08 (mapeo §2, §3), 2026-05-09 (mapeo §4 + cierre
> auditoría + fix §3.6.a + fix RE_APERTURA + hallazgo hojas
> complementarias + fix §3.6.e Fase 1), 2026-05-11 (mapeo §1).
> Cubre: diagrama global + las cuatro etapas + auditoría empírica de
> bugs.
> Pendiente: sección de arquitectura cruzada (por qué cuatro scripts y
> no uno), recálculo de algunas métricas históricas con datos
> post-fix, validaciones contra `.md` real (§3.6.b, §3.6.c, §4.6.c,
> §4.6.h).
>
> **Bugs cerrados**: §3.6.a (resuelto 2026-05-09), §3.6.d (disuelto
> 2026-05-09 como efecto colateral de §3.6.a), §3.6.e Fase 1
> (resuelto 2026-05-09 — los 39 casos `pagina_fin_no_en_mapa`
> reasignados a `ok_pg_fin_redirigida` (32) o `ok_cortado_en_indice`
> (7)), §4.6.f (refutado), RE_APERTURA strict (resuelto 2026-05-09,
> ver §4.6.j).
>
> **Bugs abiertos con prioridad subida tras fix §3.6.a**: §4.6.b
> (fallback considerando, 320 casos sospechosos).
>
> **Bugs abiertos con prioridad bajada tras fix §3.6.a**: §4.6.a
> (cosmético, daño efectivo evaporado), §4.6.g (contenido a 20 casos
> reales de cruce de archivos; los 39 casos espurios por hojas
> complementarias se cerraron en §3.6.e Fase 1).
>
> **Hallazgos nuevos sin acción inmediata**: §3.6.e Fase 2 (los 43
> `pagina_no_en_mapa`, "otra cara" del mismo fenómeno editorial —
> requiere su propio fix), headers de meses como ruptores de detección
> de carátula (`MARZO`/`ABRIL`/etc. entre fallos pueden confundirse
> con nombre de caso tras `FALLO DE LA CORTE SUPREMA`), hojas
> complementarias no flagueadas explícitamente en el pipeline,
> `detectar_fin_real` puede traspasar `linea_fin` en `ok_cortado_en_indice`
> (≤13 líneas observadas, contenido = inicio del aparato de índices),
> caso testigo `343_p646` (patrón editorial irregular en tomo 343,
> documentado en §4.6.j).

## Propósito

Mapa funcional de las cuatro etapas que transforman los `.md` del corpus
en los datasets `csjn_casos.csv` y `csjn_casos_votos.csv`. El objetivo
es que el pipeline sea legible sin abrir scripts: convenciones explícitas,
heurísticas con su razón empírica, limitaciones registradas y puntos de
fricción entre etapas.

No reemplaza los docstrings de los scripts. Los amplía con (a) la
**convención cruzada** que ningún script documenta solo, (b) los
**hallazgos empíricos** detectados al validar contra archivos reales, y
(c) las **discordancias** entre lo que el código hace y lo que dice
hacer.

---

## Diagrama global

```
┌──────────────┐   conversión externa al pipeline
│  PDFs Fallos │ ───────────────────────────────────────┐
└──────────────┘                                        │
                                                        ▼
                                              ┌──────────────────┐
                                              │ corpus/*.md      │
                                              │ (LibroVol{tomo}* │
                                              │  .md)            │
                                              └─────────┬────────┘
                                                        │
                ┌───────────────────────────────────────┼────────────────────┐
                │                                       │                    │
                ▼                                       ▼                    │
   ┌─────────────────────────┐             ┌─────────────────────────┐       │
   │ detectar_paginas.py     │             │ construir_catalogo.py   │       │
   │                         │             │ lee índices al final    │       │
   │ recorre el cuerpo       │             │ de cada .md             │       │
   └────────┬────────────────┘             └────────┬────────────────┘       │
            │                                       │                        │
            ▼                                       ▼                        │
   ┌─────────────────────────┐             ┌─────────────────────────┐       │
   │ output/mapa/            │             │ output/catalogo/        │       │
   │   mapa_paginas.csv      │             │   catalogo.csv          │       │
   │   (+_resumen,           │             │   secciones_indices.csv │       │
   │    _filtradas, _log)    │             │                         │       │
   └────────┬────────────────┘             └────────┬────────────────┘       │
            │                                       │                        │
            └───────────────┐         ┌─────────────┘                        │
                            ▼         ▼                                      │
                  ┌─────────────────────────┐                                │
                  │ cruzar_catalogo_y_      │                                │
                  │   mapa.py               │                                │
                  └────────┬────────────────┘                                │
                           │                                                 │
                           ▼                                                 │
                  ┌─────────────────────────┐                                │
                  │ output/localizacion/    │                                │
                  │   fallos_localizados.   │                                │
                  │   csv                   │                                │
                  └────────┬────────────────┘                                │
                           │                                                 │
                           └──────┐    ┌────────────────────────────────────-┘
                                  ▼    ▼     (también consume mapa_paginas
                              ┌────────────┐  para detectar_fin_real, y
                              │ parser.py  │  el corpus directamente)
                              └─────┬──────┘
                                    ▼
                          ┌──────────────────────┐
                          │ output/parser/       │
                          │   csjn_casos.csv     │
                          │   csjn_casos_votos.  │
                          │   csv                │
                          └──────────────────────┘
```

**Datos que NO son artefactos del pipeline pero el pipeline los usa**:
- `corpus/*.md`: input crudo (conversión PDF→Markdown externa).
- Tomos 335 y 336: excluidos de `detectar_paginas.py` (ver §1.6).

**Acoplamiento entre etapas**: el parser (Etapa 4) consume tres fuentes
simultáneamente — `fallos_localizados.csv` (Etapa 3), `mapa_paginas.csv`
(Etapa 1, sin pasar por Etapa 3) y los `.md` directamente. No es una
cadena lineal estricta.

---

## Etapa 1 — `detectar_paginas.py`

### 1.1 Qué hace

Recorre los `.md` del corpus y produce un mapa de **dónde aparece cada
header tipográfico de página**. El header tipográfico es la marca que
en el PDF original era cabecera o pie de página, y que tras la
conversión PDF→Markdown quedó incrustada como tres líneas seguidas
dentro del flujo de texto.

### 1.2 Inputs y outputs

| | |
|---|---|
| **Input principal** | Carpeta `corpus/` con archivos `LibroVol*.md` |
| **Input opcional** | `output/catalogo/catalogo.csv` (validación cruzada) |
| **Output principal** | `output/mapa/mapa_paginas.csv` |
| **Outputs secundarios** | `mapa_paginas_resumen.csv`, `mapa_paginas_filtradas.csv`, `mapa_paginas_log.txt` |

Estructura de `mapa_paginas.csv`:

| Columna | Tipo | Significado |
|---|---|---|
| `tomo` | int | Número del tomo (329–349) |
| `archivo` | str | Filename del `.md` (ej. `LibroVol339.2.md`) |
| `linea_header` | int | **0-indexed**. Línea donde aparece el número del tomo aislado |
| `pagina` | int | Número de página tipográfica del libro |

### 1.3 Convención central: qué cuenta como "header"

Un header de página se detecta cuando una línea, tras strip y reemplazo
de NBSP por espacio, es **exactamente** el número del tomo (ej. la
cadena `"339"` y nada más). Si alguna de las vecinas en ventana
`(-3, +2)` es un entero plausible (1–10000), esa vecina se toma como
el número de página.

**Validación empírica** (`LibroVol339.2.md`, primer header registrado
en mapa: `linea_header=50, pagina=951`):

```
Línea 49 (sed): 951                               ← número de página
Línea 50 (sed): DE JUSTICIA DE LA NACIÓN          ← texto editorial fijo
Línea 51 (sed): 339                               ← línea del tomo (= linea_header en 0-index)
Línea 52 (sed): ACORDADAS Y RESOLUCIONES          ← cuerpo del fallo
```

`linea_header=50` (0-indexed) corresponde a la línea 51 de un editor de
texto tradicional (1-indexed). El detector apunta a la línea del tomo,
no a la del número de página ni a la del texto editorial.

### 1.4 Patrones tipográficos del header (no documentado en el script)

El header de página aparece como **tres líneas seguidas** en los `.md`,
pero el orden interno varía. En `LibroVol339.2.md` se observan al
menos tres patrones:

| Patrón | Línea i-1 | Línea i (header) | Línea i+1 |
|---|---|---|---|
| A | `951` | `339` | (vacío o cuerpo) |
| B | (vacío) | `339` | `952` |
| C | `953` `DE JUSTICIA DE LA NACIÓN` | `339` | (cuerpo) |

La ventana `(-3, +2)` se eligió para cubrir todos los patrones.
Empíricamente, el offset negativo es más frecuente que el positivo
(observación interna del script, líneas 105–125: las candidatas hacia
atrás se priorizan sobre las hacia adelante).

**Consecuencia importante para etapas posteriores**: las dos líneas
acompañantes del header (`951`, `DE JUSTICIA DE LA NACIÓN`,
`FALLOS DE LA CORTE SUPREMA`) **no se filtran del cuerpo del fallo**.
Cualquier conteo de palabras hecho por el parser sobre el bloque
crudo arrastra ese ruido tipográfico.

### 1.5 Heurísticas con su razón

#### Filtro de duplicados consecutivos (`filtrar_duplicados_consecutivos`)

> Si dos detecciones tienen la misma página y están a ≤5 líneas, la
> segunda es un duplicado.

**Razón**: ocurre cuando la página coincide numéricamente con el tomo
(ej. tomo 339, página 339). En ese caso ambas líneas matchean como
"línea-tomo" y el detector las registra dos veces.

#### Filtro de outliers (`filtrar_outliers`)

> Si una página difiere de ambas vecinas en >10 páginas mientras las
> vecinas están cerca entre sí (≤10), es un outlier.

**Razón**: capturas accidentales del número del tomo en cuerpo de texto
(ej. "ley 339 de…" o citas). El número del tomo aparece en una línea
sola por azar y una vecina coincide con un entero plausible. Captura
outliers ascendentes (`19 → 339 → 21`) y descendentes
(`1591 → 338 → 1593`).

**Limitación**: si el outlier está al inicio o al final de la lista (sin
dos vecinas), no se filtra. Tampoco se filtran outliers consecutivos.

#### Diagnóstico de gaps (`GAP_FLAG = 3`)

Saltos de página > 3 se reportan como sospechosos en el resumen, pero
**no se eliminan**. Es señal para revisión manual, no acción
automática.

### 1.6 Tomos excluidos

Tomos 335 y 336 están **descartados explícitamente** en
`descubrir_archivos` (línea 360 del script): se anotan en
`descartados` con motivo `"tomo {t} excluido (problemas conocidos)"`.

**Limitación**: el script no documenta cuáles son esos problemas. Es
un costo de mantenimiento: cuando alguien quiera reincorporarlos, va
a tener que reconstruir la razón empírica.

### 1.7 Validación cruzada con catálogo

Si se pasa `--ruta_catalogo`, el script verifica que el rango de páginas
detectado por archivo (`pagina_min, pagina_max`) sea coherente con el
rango que el catálogo declara para ese tomo. Tolerancia de ±5 páginas.
Solo emite mensaje, no aborta.

**Asimetría documentada**: la validación es **contra el rango global del
tomo**, no contra el rango del archivo individual. Un `.md` cuyo rango
detectado caiga totalmente dentro del rango del tomo aunque no
corresponda al volumen físico, no levanta alerta.

### 1.8 Métricas de resumen por archivo

`mapa_paginas_resumen.csv` produce, por archivo:

- `n_headers`, `pagina_min`, `pagina_max`
- `monotonia_pct`: % de pares consecutivos donde la página crece
- `dup_filtrados`, `outliers_filtrados`
- `n_gaps_grandes` (saltos > 3 páginas)
- `n_paginas_duplicadas_postfiltro`
- `n_pares_fuera_de_orden`
- `anomalias`: texto libre con resumen

### 1.9 Limitaciones conocidas

1. **Tomos 335 y 336 excluidos** sin documentación de la razón.
2. **Headers tipográficos parciales** (las 2 líneas que acompañan al
   número del tomo) no se filtran y siguen formando parte del cuerpo.
3. **Outliers en bordes** (primera o última detección de un archivo)
   no se filtran.
4. **El umbral DUP_LINEAS_UMBRAL=5 y OUTLIER_PAGINAS_UMBRAL=10 son
   constantes**, no parametrizables sin modificar el código.
5. **Convención de filename**: el detector espera `LibroVol{tomo}{sufijo}.md`
   donde sufijo puede ser `.1`, `-1`, `_1` o vacío. La inconsistencia
   de sufijos (vimos `LibroVol339.2.md` y `LibroVol340_2.md` en el mismo
   mapa) **no genera error pero refleja que el corpus tiene dos
   convenciones de naming activas**.

### 1.10 Puntos de fricción con etapas posteriores

> Estos no son problemas del script en sí — son convenciones que las
> etapas siguientes deben respetar para no producir resultados
> inconsistentes.

#### F1.10.a — `linea_header` apunta al header tipográfico, no a la carátula del fallo

`linea_header` registra la línea donde aparece el número del tomo
aislado, que es una marca tipográfica del PDF, **no** el inicio del
contenido decisorio de un fallo. El cruzador (Etapa 3) hereda esta
convención: el `linea_inicio` de `fallos_localizados.csv` es esa misma
línea-tomo. Confirmado contra archivo real en §1.3.

**Consecuencia**: cuando un fallo termina a media página, todo lo que
va desde el header de página hasta la próxima carátula es **cola del
fallo anterior**, dentro del bloque del fallo nuevo. Esto explica el
"hallazgo extendido B" del prompt (caso `339_p1644` arranca con 6
líneas que pertenecen al `339_p1642`). El parser tiene que compensar
esto con `detectar_fin_real` y con `find_case_name` desde el cuerpo.

#### F1.10.b — Tres líneas de ruido tipográfico por página

Las dos líneas acompañantes del header de página (`951`,
`DE JUSTICIA DE LA NACIÓN` o `FALLOS DE LA CORTE SUPREMA`) están en el
cuerpo del bloque y van a contar para `word_count`. Para 800 páginas
de un fallo largo, son ~1.600 tokens de ruido fijo.

#### F1.10.c — Mismo `(tomo, pagina)` puede aparecer en dos archivos

Un mismo `(tomo, pagina)` puede tener detecciones en dos `.md` distintos
del mismo tomo (si el corte editorial entre volúmenes cae en una
página). El cruzador (Etapa 3) resuelve esta colisión quedándose con la
detección de **línea más baja**, pero esa decisión depende de un
ordenamiento estable que `detectar_paginas.py` no garantiza
explícitamente. La estabilidad surge de que `detectar_en_lineas`
recorre el archivo en orden, y `procesar_corpus` itera los archivos
ordenados por `(tomo, nombre)`.

### 1.11 Estado de validación de la sección

- ✅ Convención de `linea_header` (0-indexed, apunta a la línea del
  tomo) verificada contra `LibroVol339.2.md`.
- ✅ Patrones tipográficos del header (3 variantes mínimas) verificados
  contra archivo real.
- ✅ Hallazgo F1.10.a verificado contra el caso `339_p1644` (zona
  línea 26.346 del `.md`).
- ⏳ Outputs secundarios (`_resumen`, `_filtradas`, `_log`) no
  inspeccionados — no fueron necesarios para la sección, pero deberían
  revisarse si surgen dudas sobre filtros aplicados.
- ⏳ Comportamiento real con tomos 343–349 (índice consolidado
  multi-volumen) no validado — pendiente para sesión que tenga acceso
  a esos archivos.

---

## Etapa 2 — `construir_catalogo.py`

### 2.1 Qué hace

Lee los `.md` del corpus, encuentra al final de cada uno el **índice
editorial de nombres de las partes** (`INDICE POR LOS NOMBRES DE LAS
PARTES`) y lo parsea para construir un catálogo heurístico de fallos.
Una fila por `(tomo, página)` con todos los nombres bajo los que el
editor catalogó ese fallo.

A diferencia de Etapa 1 (que mapea **dónde están las páginas en el
archivo**), Etapa 2 opera en el plano **editorial**: qué fallos existen
y bajo qué nombres aparecen en el índice oficial.

### 2.2 Inputs y outputs

| | |
|---|---|
| **Input** | Carpeta `corpus/` con archivos `LibroVol*.md` |
| **Output principal** | `output/catalogo/catalogo.csv` |
| **Output secundario** | `output/catalogo/secciones_indices.csv` |

**No usa `mapa_paginas.csv`**: esta etapa es independiente de Etapa 1.
La validación cruzada entre ambas se hace en Etapa 3.

Estructura de `catalogo.csv` (5.862 filas con datos actuales):

| Columna | Tipo | Significado |
|---|---|---|
| `tomo` | int | Número del tomo (329–349, sin 335 y 336) |
| `pagina_inicio` | int | Página donde empieza el fallo (en el libro impreso) |
| `pagina_fin` | int o vacío | **Página de inicio del fallo siguiente del mismo tomo**. Vacío para el último fallo de cada tomo. Ver §2.5.a — el docstring del script dice otra cosa |
| `caso_id_canonico` | str | `f"{tomo}_p{pagina_inicio}"`. Identificador único en todo el pipeline |
| `nombres_indice` | str | Carátulas asociadas a la página, separadas por `" \| "` |
| `n_nombres` | int | Cantidad de carátulas distintas |
| `n_archivos_indice` | int | En cuántos `.md` del tomo aparece la entrada en el índice |

Estructura de `secciones_indices.csv` (139 filas con datos actuales):

| Columna | Tipo | Significado |
|---|---|---|
| `tomo` | int | Número del tomo |
| `archivo` | str | Filename del `.md` |
| `tipo_indice` | str | Uno de: `nombres`, `materias`, `sumario`, `legislacion`, `general` |
| `linea_inicio` | int | **1-indexed**, inclusivo. Línea donde empieza la sección |
| `linea_fin` | int | **1-indexed**, inclusivo. Línea donde termina (= línea anterior al próximo header de sección) |

### 2.3 Convención central: cómo se delimita el índice

El parseo procede en dos pasos lógicos:

1. **Detectar las cinco secciones de índice** (`detectar_secciones`,
   líneas 157–197). Cada una identificada por su header exacto:
   - `INDICE POR LOS NOMBRES DE LAS PARTES`
   - `INDICE ALFAB[EÉ]TICO POR MATERIAS`
   - `INDICE SUMARIO`
   - `INDICE DE LEGISLACI[OÓ]N` (con `(*)` opcional)
   - `INDICE GENERAL`

   El header tiene que estar **en línea sola, en mayúsculas exactas**,
   sin puntos suspensivos. Esto distingue el header del índice de la
   tabla de contenidos del final del libro.

2. **Encontrar la sección `nombres`** y parsear su contenido
   (`parsear_indice_nombres`, líneas 289–344). El bloque va desde la
   línea siguiente al header hasta la línea anterior al próximo header
   de sección.

#### Cabeceras repetidas y colapso

Las secciones de índice (sobre todo `legislacion` y `sumario`)
**repiten su header como cabecera de página**: cada vez que el PDF
arrancaba una página nueva dentro de la sección, el header se imprimía
de nuevo. Si no se colapsan, cada repetición se contaría como una
sección distinta.

Solución (`detectar_secciones`, líneas 181–185): cuando aparecen dos
matches consecutivos del mismo tipo, se conserva sólo el primero. Los
siguientes son cabeceras de página repetidas, no secciones nuevas.

### 2.4 La unidad parseable: el "ancla"

El índice de nombres tiene la estructura visual:

```
A
ABALOS, Juan c/ Estado Nacional: p. 537.
ACME S.A. (Estado Nacional c/): p. 243, 244, 297.
ADMINISTRACION FEDERAL DE INGRESOS PUBLICOS (Aguas
Argentinas S.A. c/): p. 1316
y 1334.

B
BANCO CENTRAL c/ ...
```

El parser no opera por línea, opera por **ancla**. Una ancla es el
patrón regex `RE_ANCLA` (líneas 141–146):

```
:\s*(ps?\.)\s*[\xa0\s]*(\d+(?:\s*[,y]\s*\d+)*)\s*\.?
```

Que captura: dos puntos, `p.` o `ps.`, número(s) separados por `,` o
`y`, punto final opcional.

#### Por qué no se parsea por línea

El reflow PDF→Markdown produjo casos donde **dos entradas distintas
quedaron en la misma línea**. Si el parser cortara por `\n`, perdería
la segunda. Solución (líneas 312–328): se concatenan todas las líneas
útiles del bloque en un único string, y el ancla actúa como delimitador
lógico entre entradas.

#### Variantes editoriales que el ancla tolera

A lo largo de los 18 años cubiertos, el formato cambió:

| Variación | Tomos viejos | Tomos nuevos |
|---|---|---|
| Punto final tras la página | sí (`p. 537.`) | no (`p. 537`) |
| Espacio entre `p.` y número | espacio normal | espacio o NBSP `\xa0` |
| Separador en páginas múltiples | `,` | `y` |

El regex acepta todas las combinaciones.

### 2.5 Heurísticas con su razón

#### 2.5.a Inferencia de `pagina_fin` (línea 410)

El script calcula `pagina_fin` ordenando todas las páginas detectadas
por tomo y asignando a cada una la página de inicio de la siguiente:

```python
pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]
```

**Sin restar 1.** Para la última página de cada tomo, `pagina_fin` queda
vacío.

##### Discordancia entre código y docstring

El docstring (línea 57) dice:

> `pagina_fin: entero o vacío, inferido como (página del siguiente fallo - 1)`

El código (línea 410) hace:

> `pagina_fin = (página del siguiente fallo)`

**Verificado contra datos**: en `catalogo.csv` (5.862 filas), las entradas
con `pagina_fin` no vacío cumplen exactamente
`pagina_fin == pagina_inicio_del_siguiente_fallo`. Cero excepciones.

**Conclusión**: el código manda, el docstring está desactualizado.
Corregir el docstring del script en una sesión futura. **Esta convención
afecta directamente a Etapa 3** — ver fricción F2.6.a.

#### 2.5.b Fix v15: extender inicio del índice (líneas 216–282)

En tomos modernos (337–349), el reflow PDF→Markdown a veces ubicó la
**portadilla** `INDICE POR LOS NOMBRES DE LAS PARTES` **después** de
las primeras entradas alfabéticas del listado, en lugar de antes.

Síntoma: el header se detecta correctamente, pero las entradas que
están físicamente antes del header en el `.md` no se parsean — son
parte del listado real.

Solución (`extender_inicio_indice_nombres`):

1. Look-back desde el header hasta 200 líneas atrás, buscando una línea
   con sólo `'A'`.
2. Validar que la línea anterior a la `'A'` esté vacía (separación
   visual entre fin de fallo y arranque del listado).
3. Validar que entre la `'A'` y el header haya al menos **3 anclas**
   `: p. N` (confirma que es un listado real, no una `'A'` que aparece
   por otro motivo).
4. Abortar si en el look-back se cruza otro header de sección.

Si pasa las tres validaciones, el inicio del índice se extiende hasta
la línea de la `'A'`.

⏳ **No validado contra archivo `.md` real**: se requiere un `.md` del
rango 337–349 para confirmar que el fix se dispara correctamente y
captura las entradas que estaban antes de la portadilla.

#### 2.5.c Filtros del bloque parseable (líneas 312–325)

Antes de joinear las líneas del bloque, se descartan:

- Líneas vacías.
- Cabeceras alfabéticas (`A`, `B`, `C`...): regex `[A-ZÑÁÉÍÓÚ]{1,2}` solas.
- `NOMBRES DE LAS PARTES` sin el prefijo `INDICE POR LOS` — es la
  cabecera de página repetida del índice impreso.
- Romanos en paréntesis (`(I)`, `(VIII)`): aparecen en algunos tomos
  como complemento del header de página (ej. tomo 348).
- Cualquier otro header de sección que se haya colado.

#### 2.5.d Limpieza de carátulas (`limpiar_caratula`, líneas 347–362)

Mínima e intencionalmente conservadora:

- NBSP → espacio normal.
- Guión de continuación de palabra: `Fede- ral` → `Federal`.
- Espacios múltiples → uno solo.

**No corrige** caracteres OCR raros, no decide entre may/min, no toca
acentos. La política es preservar la fidelidad al original; las
correcciones agresivas se delegan a etapas posteriores que tengan más
contexto.

#### 2.5.e Sin deduplicación forzada de carátulas

El mismo fallo aparece en el índice bajo múltiples carátulas:

- Por la actora: `Y. P. F. S.A. c/ Municipalidad de C. del Uruguay`
- Por la demandada (entrada cruzada): `Municipalidad de C. del Uruguay (Y. P. F. S.A. c/)`
- Variantes ortográficas: `Y.P.F. S.A. c/ Municipalidad de C. del Uruguay`

El script **no intenta colapsar estas variantes**. Las agrupa por
página y las concatena con `" | "`. Razón documentada en el docstring
(líneas 39–50): el formato editorial cambió entre tomos (paréntesis en
329, sin paréntesis en 334, casi sin cruzadas en 348). Una regla de
dedupe única forzaría inventar carátulas o descartar información en
algún tomo.

**Consecuencia para análisis**: la columna `n_nombres` es interpretable
como "redundancia editorial del índice", no como "cantidad de fallos".
Una fila con `n_nombres=3` es un único fallo con tres carátulas
distintas en el índice.

### 2.6 Puntos de fricción con etapas posteriores

#### F2.6.a — `pagina_fin` no es la última página del fallo, es la inicial del siguiente

El cruzador (Etapa 3) **debe interpretar correctamente esta
convención**. Si busca el header tipográfico de la página `pagina_fin`,
está apuntando al inicio del fallo siguiente, no al final del actual.

Si en cambio busca `pagina_fin + 1` como header del siguiente, está
buscando una página **que no es** el inicio del siguiente — el inicio
del siguiente está en `pagina_fin`.

⏳ **Hipótesis a verificar en Bloque 3**: el bug `pg_fin+1` registrado
en BITACORA podría originarse exactamente acá — un cruzador escrito
asumiendo la convención del docstring (`pagina_fin = siguiente - 1`)
en vez de la del código (`pagina_fin = siguiente`). Validar leyendo
`cruzar_catalogo_y_mapa.py`.

#### F2.6.b — Convenciones de indexación heterogéneas dentro de Etapa 2

`secciones_indices.csv` produce líneas **1-indexed inclusivas**
(línea 195: `linea_inicio_0 + 1, linea_fin_0 + 1`). Etapa 1 produce
**0-indexed**. Etapa 3 hereda 0-indexed para fallos pero consume
secciones 1-indexed para cortes de fin. La mezcla es real y está
documentada en HALLAZGOS como la causa más probable de los 19 casos
`ok_cortado_en_indice` pendientes — confirmar en Bloque 3.

#### F2.6.c — Slice del bloque parseable: posible pérdida de la última línea

`parsear_indice_nombres` (línea 310) hace:

```python
bloque = lines[linea_inicio_1:linea_fin_1]
```

Con `linea_inicio_1` y `linea_fin_1` siendo 1-indexed inclusivos. El
slice de Python es 0-indexed exclusivo en el extremo superior:

- `lines[linea_inicio_1:...]` empieza en `linea_inicio_1` (0-indexed),
  que es la línea siguiente al header (correcto, salta el header).
- `lines[...:linea_fin_1]` termina en `linea_fin_1 - 1` (0-indexed),
  que es la línea anterior a `linea_fin_1` 1-indexed.

Es decir: la línea `linea_fin_1` (la última línea del bloque según el
contrato de `secciones_indices.csv`, que es **inclusiva**) **no se
incluye en el slice parseado**.

Esto puede ser:
- **Intencional**: la línea `linea_fin_1` es la línea anterior al
  próximo header de sección, que típicamente es vacía. Saltarla no
  pierde información.
- **Bug menor**: si la última línea contiene una entrada del índice,
  esa entrada no se parsea.

⏳ **No validado**: se requiere inspeccionar un `.md` real para
confirmar qué hay en la línea `linea_fin_1` típicamente.

### 2.7 Limitaciones conocidas

1. **Tomos 335 y 336 ausentes**, igual que en Etapa 1. El catálogo no
   los cubre.
2. **`secciones_indices.csv` produce líneas 1-indexed mientras Etapa 1
   produce 0-indexed**. Convención cruzada no documentada en ninguno
   de los dos scripts.
3. **Tres convenciones de naming de archivos coexisten**: punto
   (`329.1.md`), guión bajo (`340_2.md`), guión medio (`342-1.md`). El
   regex `LibroVol(\d{3})` (línea 131) es agnóstico al separador y
   tolera todo, pero el corpus tiene **tres convenciones activas**, no
   dos como decía la observación inicial de Etapa 1.
4. **No todas las secciones aparecen en todos los tomos**: tomo 348 y
   349 tienen sólo `nombres + general` en `secciones_indices.csv`. No
   está claro si es un cambio editorial real (los tomos modernos no
   tienen `materias`, `sumario`, `legislacion`) o un fallo de detección
   de regex.
5. **`pagina_fin` es la página de inicio del siguiente fallo, no la
   última página del actual**. Diferencia respecto al docstring.
6. **Inferencia de `pagina_fin` por orden global del tomo**: si una
   página queda fuera del índice por error de parseo, las páginas
   adyacentes heredan `pagina_fin` mal calculados (saltan al fallo
   siguiente al perdido).

### 2.8 Estado de validación de la sección

- ✅ Convención de `pagina_fin` (= inicio del siguiente, sin restar 1)
  verificada contra `catalogo.csv` completo: 5.800/5.800 filas con
  `pagina_fin` no vacío cumplen la igualdad. Cero excepciones.
- ✅ Indexación 1-indexed inclusiva de `secciones_indices.csv`
  verificada contra código (línea 195) y consistente con docstring
  (línea 162).
- ✅ Tres convenciones de naming de archivos verificadas contra los 46
  archivos listados en `secciones_indices.csv`.
- ✅ Tomos 335 y 336 ausentes confirmados contra datos: 19 tomos
  presentes, no 21.
- ⏳ Fix v15 (`extender_inicio_indice_nombres`) no validado contra `.md`
  real. Requiere subir un archivo del rango 337–349.
- ⏳ Comportamiento del slice `lines[linea_inicio_1:linea_fin_1]` (¿se
  pierde la última línea?) no validado contra `.md` real.
- ⏳ Faltante de secciones `materias`/`sumario`/`legislacion` en tomos
  348–349: no se determinó si es cambio editorial o fallo de detección.

### 2.9 Artefacto fuera del diagrama: `catalogo_volumenes.csv`

Existe un archivo `output/catalogo/catalogo_volumenes.csv` con 45 filas
y la siguiente estructura:

```
tomo, archivo, pagina_min, pagina_max, n_paginas
```

**No lo produce `construir_catalogo.py`** (verificado por grep:
ninguna mención del filename ni de las columnas en el script). No
figura en el diagrama global del pipeline.

⏳ **Origen no identificado**. Hipótesis a verificar cuando se incorporen
los demás scripts:

1. Lo produce `detectar_paginas.py` como output secundario que no
   estaba documentado en Etapa 1 (Etapa 1 declara
   `mapa_paginas_resumen.csv` pero no este).
2. Lo produce un script auxiliar no incorporado todavía al mapeo.
3. Es un derivado calculable a partir de `mapa_paginas.csv` agrupando
   por archivo (`min`, `max`, `count` de la columna `pagina`).

**Hallazgos preliminares al inspeccionar el archivo**:

- `LibroVol338.2.md` declara `pagina_min=338`. Coincide sospechosamente
  con el número del tomo. Probable outlier que escapó al filtro de
  Etapa 1 (`filtrar_outliers` no captura outliers en el borde inicial
  de un archivo — limitación documentada en §1.5).
- `LibroVol343-2.md` y `LibroVol343-3.md` solapan en página 1457:
  el primer archivo termina en 1457, el segundo empieza en 1457.
  Confirma F1.10.c (mismo `(tomo, pagina)` en dos archivos).
- `LibroVol344-1.md` y `LibroVol344-2.md` solapan en página 1259.
  Mismo patrón.

Estos hallazgos pertenecen a Etapa 1. Anotados acá para no perderlos
hasta que el origen del archivo quede identificado.

---

## Etapa 3 — `cruzar_catalogo_y_mapa.py`

### 3.1 Qué hace

Cruza el catálogo editorial (Etapa 2) con el mapa físico de páginas
(Etapa 1) y produce, por cada fallo del catálogo, su localización
**física** en el corpus: archivo `.md`, línea de inicio, línea de fin
y status del cruce.

Es la única etapa que junta las dos vistas paralelas que produjeron
las etapas anteriores: el "qué fallos hay y entre qué páginas viven"
de Etapa 2, y el "dónde, en qué línea de qué archivo, está cada
página" de Etapa 1. El parser (Etapa 4) consume el resultado.

### 3.2 Inputs y outputs

| | |
|---|---|
| **Input principal 1** | `output/catalogo/catalogo.csv` (Etapa 2) |
| **Input principal 2** | `output/mapa/mapa_paginas.csv` (Etapa 1) |
| **Input opcional 1** | Carpeta `corpus/` (para `n_lineas` por archivo) |
| **Input opcional 2** | `output/catalogo/secciones_indices.csv` (Etapa 2) |
| **Output principal** | `output/localizacion/fallos_localizados.csv` |
| **Outputs secundarios** | `_resumen.csv`, `_huerfanos.csv`, `_log.txt` |

Estructura de `fallos_localizados.csv` (5.862 filas con datos
actuales):

| Columna | Tipo | Significado |
|---|---|---|
| `caso_id_canonico` | str | Heredado de Etapa 2 |
| `tomo` | int | Heredado de Etapa 2 |
| `archivo` | str | `.md` donde arranca el fallo (vacío si `pagina_no_en_mapa`) |
| `pagina_inicio` | int | Heredado de Etapa 2 |
| `pagina_fin` | int o vacío | Heredado de Etapa 2 (vacío para último del tomo) |
| `linea_inicio` | int | **0-indexed**. Línea del header tipográfico de `pagina_inicio`. Heredado de Etapa 1 |
| `linea_fin` | int o vacío | **0-indexed**. Línea calculada según el status. Ver §3.4 |
| `nombres_indice` | str | Heredado de Etapa 2 |
| `n_nombres` | int | Heredado de Etapa 2 |
| `status` | str | Uno de los siete status descritos en §3.4 |

`_huerfanos.csv` filtra el principal por `status not in ('ok',
'ok_cortado_en_indice')` — el conjunto que requiere atención manual o
revisión del pipeline.

### 3.3 Convenciones cruzadas críticas (acoplamiento entre etapas)

Esta etapa es el primer punto donde las convenciones de las etapas
anteriores **se encuentran**. Tres son centrales:

#### 3.3.a — `pagina_fin` del catálogo es la página **del** siguiente, no la **anterior** al siguiente

Ya tratada en F2.6.a. Para el cruzador, esto significa: si quiero
encontrar el header tipográfico que marca el inicio del fallo siguiente,
tengo que buscar `(tomo, pagina_fin)` en el mapa, **no**
`(tomo, pagina_fin + 1)`.

#### 3.3.b — Indexación 0-indexed (Etapa 1) vs. 1-indexed (Etapa 2)

`mapa_paginas.csv` produce `linea_header` en **0-indexed**.
`secciones_indices.csv` produce `linea_inicio` y `linea_fin` en
**1-indexed inclusivo**. El cruzador consume ambos sin convertir
explícitamente entre sistemas. La consecuencia se manifiesta en el
status `ok_cortado_en_indice` — ver §3.5.b.

#### 3.3.c — Línea de inicio = header tipográfico, no carátula

`linea_inicio` de `fallos_localizados.csv` es la línea del header
tipográfico de la página, heredada del mapa. **No** apunta al inicio
del cuerpo decisorio del fallo (que es la carátula). Es la convención
F1.10.a propagada hasta esta etapa. El parser (Etapa 4) tiene que
compensar esto desde el cuerpo del bloque.

### 3.4 Los siete status del cruce

> **Nota documental (2026-05-09)**: la columna se llama `status` en
> `fallos_localizados.csv` (Etapa 3), no `status_localizacion`. El
> parser sí la renombra a `status_localizacion` al volcarla en
> `csjn_casos.csv` (Etapa 4). Esta inconsistencia entre los dos CSVs
> existe pero no afecta el funcionamiento.

El docstring (líneas 30–38) los enumera. Se observan así en los datos
actuales (post-fix §3.6.a, sesión 2026-05-09):

| Status | n | % | Significado |
|---|---:|---:|---|
| `ok` | 5.741 | 97,93% | Cruce limpio |
| `pagina_no_en_mapa` | 43 | 0,73% | `pagina_inicio` del catálogo no aparece como header en el mapa |
| `pagina_fin_no_en_mapa` | 39 | 0,67% | `pagina_fin` no aparece como header en el mapa (desenmascarado por el fix) |
| `fallo_cruza_archivos` | 20 | 0,34% | El "siguiente fallo" arranca en otro `.md` del mismo tomo |
| `ok_cortado_en_indice` | 19 | 0,32% | Último fallo del tomo, cortado antes del aparato editorial de índices |
| `ultimo_del_tomo` | 0 | 0% | Último fallo del tomo, fallback sin secciones de índice |
| `ultimo_del_tomo_sin_fin` | 0 | 0% | Último fallo del tomo, sin acceso al corpus |

**Total: 5.862 filas. 98,25% (5.760) en estados "limpios" (`ok` +
`ok_cortado_en_indice`); 1,75% (102) huérfanos.**

Los dos status restantes con cero observaciones son fallbacks que el
código contempla pero que no se gatillan con todos los inputs
opcionales provistos: `ultimo_del_tomo` y `ultimo_del_tomo_sin_fin`
solo aparecerían si no se pasara `secciones_indices.csv` o si éste no
incluyera el archivo del último fallo del tomo. Como el archivo se
pasa y los 19 últimos del tomo tienen su `secciones_indices`
correspondiente, todos caen en `ok_cortado_en_indice`.

#### Comparación pre/post fix §3.6.a

Pre-fix (sesión 2026-05-08), `pagina_fin_no_en_mapa` registraba 0
casos. La razón aparente era que `pg_fin + 1` casi siempre tenía
header detectado en el mapa. Una vez aplicado el fix (búsqueda de
`pg_fin` en lugar de `pg_fin + 1`), aparecen 39 casos en este status,
concentrados en tomos 331–334 (10+10+10+9). Hipótesis: estos tomos
tienen una particularidad editorial o de OCR que el detector de
páginas (Etapa 1) no capta para ciertas páginas. El bug `pg_fin + 1`
los enmascaraba pidiendo *la página siguiente*, que casi siempre sí
estaba detectada.

| Status | Pre-fix | Post-fix | Δ |
|---|---:|---:|---:|
| `ok` | 5.773 | 5.741 | −32 |
| `pagina_fin_no_en_mapa` | 0 | 39 | +39 |
| `fallo_cruza_archivos` | 27 | 20 | −7 |
| Otros | 62 | 62 | 0 |

Aritmética: −32 = −39 + 7. Los 39 nuevos `pagina_fin_no_en_mapa`
salieron de `ok` (32) y de `fallo_cruza_archivos` (7).

### 3.5 Cómo se calcula `linea_fin` por status

#### 3.5.a — `ok` y `fallo_cruza_archivos`

Lógica del código **post-fix §3.6.a (sesión 2026-05-09)**, líneas
234–249:

```python
clave_fin = (tomo, pg_fin)
if clave_fin in mapa_pagina:
    archivo_fin, linea_fin_header = mapa_pagina[clave_fin]
    if archivo_fin == archivo_ini:
        out['linea_fin'] = linea_fin_header - 1   # status 'ok'
    else:
        out['linea_fin'] = n_lineas[archivo_ini] - 1   # status 'fallo_cruza_archivos'
```

El cursor de búsqueda es ahora `pg_fin` (la página de inicio del fallo
siguiente). El `linea_fin_header - 1` da la línea anterior al header
del fallo siguiente — el comportamiento esperado.

Pre-fix, el código tenía `clave_fin = (tomo, pg_fin + 1)`. Ese era el
bug §3.6.a y producía bloques inflados en una página entera (~32
líneas extra del fallo siguiente, en el 100% de los casos `ok`). Ver
§3.6.a para detalles del bug y del fix.

#### 3.5.b — `ok_cortado_en_indice`

Para los 19 últimos fallos de tomo (uno por tomo), el código corta el
bloque antes del aparato editorial de índices que ocupa el final de
cada `.md` (línea 222):

```python
out['linea_fin'] = indices_nombres_por_archivo[archivo_ini] - 1
```

`indices_nombres_por_archivo` viene de `secciones_indices.csv`, que
es **1-indexed inclusivo** (verificado en §2.2 y §2.6.b). El cruzador
trabaja en **0-indexed** (heredado del mapa). Esta línea aplica `- 1`
sin convertir entre sistemas. El bug se trata en §3.6.b.

#### 3.5.c — `pagina_no_en_mapa`

Si `(tomo, pg_ini)` no está en el mapa, no se puede ubicar el inicio
del fallo. Se devuelve la fila con `archivo`, `linea_inicio` y
`linea_fin` vacíos. La distribución por tomo es altamente concentrada
(§3.6.c).

#### 3.5.d — Resolución de duplicados de página

Cuando `(tomo, pagina)` aparece en dos archivos del mismo tomo (caso
F1.10.c), el cargador del mapa elige la entrada con `linea_header`
**más baja** (línea 100 del cruzador):

```python
elegida = min(entradas, key=lambda e: e['linea_header'])
```

La estabilidad del orden depende de que `detectar_paginas.py` recorra
los archivos en orden — verificado en §1.10.c. La política está
documentada también en el docstring (línea 71).

### 3.6 Bugs detectados

#### 3.6.a — Bug `pg_fin + 1`: bloque inflado en una página entera

> **✅ RESUELTO 2026-05-09**
>
> Fix aplicado: línea 235 del cruzador, cambio de `clave_fin = (tomo,
> pg_fin + 1)` a `clave_fin = (tomo, pg_fin)`. Una sola línea.
>
> Validación post-fix:
> - 5.663/5.663 pares consecutivos sin bloque inflado (vs 5.695/5.695
>   inflados pre-fix).
> - 32 fallos pasaron de `ok` a `pagina_fin_no_en_mapa` (status
>   desenmascarado, ver §3.4).
> - 7 fallos `fallo_cruza_archivos` recalibrados (de 27 a 20 — el bug
>   §3.6.d se disolvió como efecto colateral del fix).
> - 162 fallos pasaron de tener `apertura_tipo` espurio a
>   `ok_sin_marcador_apertura`. Validación caso por caso confirmó que
>   el marcador detectado pre-fix era del fallo siguiente (ver
>   bitácora: 151/163 con `wc_pre > wc_post`, delta de palabras
>   coherente con el inflado de ~30 líneas; 0 regresiones).
>
> El contenido original del bug se conserva debajo para registro
> histórico.

---

**Severidad: crítica. Afecta el 100% de los `ok` (5.773 fallos).**

##### El error

Línea 235:
```python
clave_fin = (tomo, pg_fin + 1)
```

La hipótesis de F2.6.a queda confirmada al leer el código: el cursor
de búsqueda fue escrito asumiendo la convención del docstring de
Etapa 2 ("`pagina_fin = página del siguiente − 1`"), no la convención
real del código de Etapa 2 ("`pagina_fin = página del siguiente`").

Con la convención real, `pg_fin` ya **es** la página de inicio del
fallo siguiente. Sumarle 1 apunta a la **segunda** página del fallo
siguiente.

##### Por qué no se manifiesta como `pagina_fin_no_en_mapa`

Si el detector de páginas detectara solamente los headers de las
páginas de inicio de fallo, buscar `pg_fin + 1` daría `KeyError` en el
mapa y el status sería `pagina_fin_no_en_mapa`. Pero el detector de
Etapa 1 detecta **todas** las páginas (cada página del libro impreso
tiene su header tipográfico). Entonces `pg_fin + 1` casi siempre
existe en el mapa, y el código sigue: pone `linea_fin = header de
pg_fin+1 − 1`. El bloque de cada fallo termina al final de la primera
página del fallo siguiente, no al inicio de la primera página del
fallo siguiente.

##### Validación contra datos

De 5.773 casos `ok`, hay 5.695 pares de fallos consecutivos en el
mismo `.md` con `pagina_fin(actual) == pagina_inicio(siguiente)`.
En los **5.695** (100%):

```
linea_fin(actual)  >  linea_inicio(siguiente)
```

es decir, el `linea_fin` del fallo actual está sistemáticamente **más
abajo** que el `linea_inicio` del fallo siguiente.

| Métrica | Valor |
|---|---|
| Pares analizados | 5.695 |
| Pares con bloque inflado (lin_fin actual > lin_ini siguiente) | 5.695 (100,00%) |
| Inflado promedio | 32,4 líneas |
| Inflado mínimo | 9 líneas |
| Inflado máximo | 46 líneas |

**Distribución del inflado** (líneas que se solapan con el fallo
siguiente):

| Rango | Casos |
|---|---:|
| 1–10 líneas | 1 |
| 11–20 líneas | 9 |
| 21–40 líneas | 5.651 |
| 41–60 líneas | 34 |

El pico en 21–40 líneas es coherente con que el bloque de cada fallo
incluye exactamente **una página del fallo siguiente** (el cuerpo de
una página de los `.md` del corpus es ~30–35 líneas).

##### Caso testigo

`329_p5` y `329_p9` en `LibroVol329.1.md`:

```
caso 329_p5:  pg_ini=5,  pg_fin=9,  linea_inicio=39,   linea_fin=210
caso 329_p9:  pg_ini=9,  pg_fin=12, linea_inicio=178,  linea_fin=315
```

El bloque del caso `329_p5` se extiende hasta la línea 210, pero el
caso `329_p9` arranca en la línea 178. Las líneas 178–210 (33 líneas)
son la primera página del caso `329_p9` indebidamente atribuidas al
caso `329_p5`.

##### Corrección

Cambiar línea 235:

```python
clave_fin = (tomo, pg_fin + 1)   # actual: bloque inflado
clave_fin = (tomo, pg_fin)        # corregido
```

Y eliminar `- 1` en línea 240 (o, alternativamente, dejar `- 1` y
restar 1 en la búsqueda — equivale, pero hay que ser consistente):

```python
out['linea_fin'] = linea_fin_header - 1   # actual
out['linea_fin'] = linea_fin_header - 1   # corregido (queda igual: la línea anterior al header del siguiente)
```

Con `clave_fin = (tomo, pg_fin)` y `linea_fin = header - 1`, el bloque
del fallo actual termina exactamente una línea antes del header del
fallo siguiente — el comportamiento esperado.

##### Impacto en el parser (Etapa 4)

Cada bloque del parser viene con ~30 líneas extra del fallo siguiente
al final. La cascada `detectar_fin_real` del parser (carátula del
siguiente → sumario nuevo → marcador de apertura → firma) compensa
este inflado en muchos casos, pero no en todos. Hipótesis fuerte:
buena parte de los falsos positivos del detector `borde_inferior` del
auditor (mencionados en HALLAZGOS, sección §4) tienen origen acá.
Validar en §4.

#### 3.6.b — Bug indexación 0/1: `linea_fin` apunta AL header del índice, no a la línea anterior

**Severidad: baja. Afecta los 19 `ok_cortado_en_indice` (uno por
tomo).**

##### El error

Línea 222:
```python
out['linea_fin'] = indices_nombres_por_archivo[archivo_ini] - 1
```

`indices_nombres_por_archivo[archivo_ini]` es `linea_inicio` del
índice de nombres en `secciones_indices.csv`, **1-indexed inclusivo**.
La intención del autor era "la línea anterior al header del índice".
Pero al restarle 1 a un valor 1-indexed para usarlo como
`linea_fin` 0-indexed:

- Valor 1-indexed `N` corresponde a la línea 0-indexed `N - 1`.
- Restarle 1 al valor 1-indexed para "ir a la anterior" da `N - 1`.
- Ese mismo valor `N - 1` interpretado como 0-indexed apunta
  exactamente a la línea `N` 1-indexed, **es decir, al header del
  índice**, no a la anterior.

##### Validación contra archivo real

⏳ **Pendiente.** Para confirmar, abrir cualquiera de los 19 `.md`
afectados (ej. `LibroVol339.2.md`, caso `339_p1834` con `linea_fin =
33525`) y verificar si la línea 33525 (en el editor, 1-indexed) o la
línea 33526 (1-indexed) corresponde al texto del header `INDICE POR
LOS NOMBRES DE LAS PARTES`. Si es la línea del header, está corrido
en uno (bug confirmado). Si es la línea anterior, no hay bug y el
ajuste compensa.

⏳ **Acción**: pedir el `.md` de un tomo afectado para validar.

##### Impacto

Los 19 bloques `ok_cortado_en_indice` arrastran como última línea el
header del índice de nombres. Para el parser, es ruido tipográfico
acotado (una línea de 36 caracteres en mayúsculas), no una página
entera. Mucho menos grave que 3.6.a.

#### 3.6.c — Concentración anómala de `pagina_no_en_mapa` en tomos 331–334

**Severidad: media. 43 fallos sin localizar (~10% de los huérfanos).**

##### Distribución

| Tomo | Casos `pagina_no_en_mapa` |
|---|---:|
| 331 | 11 |
| 332 | 11 |
| 333 | 11 |
| 334 | 10 |
| Resto (329, 330, 337–349) | 0 |

La concentración exclusiva en cuatro tomos consecutivos sugiere una
particularidad del corpus de esos tomos, no un problema general del
cruzador.

##### Patrón

Las páginas afectadas tienden a ser **primera página de cada volumen
físico** (`.md`) del tomo. Por ejemplo, en tomo 333:

```
333_p5    (probable inicio del primer .md del tomo)
333_p133, 311, 561, 777, 1147, 1205, 1723, 1885, 2061, 2261
```

Cruzando con `catalogo_volumenes.csv` (§2.9), las páginas afectadas
caen muy cerca de los bordes editoriales entre `.md`s. Hipótesis:

1. El detector de páginas (Etapa 1) no detecta el primer header
   tipográfico al inicio de cada `.md` por la limitación documentada
   en §1.5 ("outliers en bordes no se filtran" — pero también, la
   ventana `(-3, +2)` puede no encontrar pareja para un header al
   inicio absoluto del archivo).
2. Los tomos 331–334 tienen alguna particularidad editorial (índices
   o aparato preliminar al **inicio** en vez de al final) que el
   detector tampoco contempla.

##### Validación pendiente

⏳ Para diagnosticar, hace falta inspeccionar:

1. Las primeras ~100 líneas de `LibroVol331.1.md` (¿hay un header
   tipográfico para la página 7? ¿está la marca del tomo aislada?).
2. `mapa_paginas.csv` para tomos 331–334: ¿cuál es la primera página
   detectada en cada `.md`?
3. Comparar con tomo 329 (sin casos): ¿qué hace distinto su `.md` 1?

⏳ **Acción**: pedir un `.md` del rango 331–334 para validar la
hipótesis.

#### 3.6.d — Solapamiento conceptual: `fallo_cruza_archivos` con la convención correcta

> **✅ RESUELTO 2026-05-09**
>
> Disuelto como efecto colateral del fix §3.6.a. Con el cursor
> apuntando ahora a `pg_fin` (no `pg_fin + 1`), el detector de
> `fallo_cruza_archivos` queda correctamente calibrado: detecta cuando
> la primera página del fallo siguiente está en otro archivo.
>
> Cuantitativamente: 27 casos pre-fix → 20 casos post-fix. Los 7
> casos que salieron del status eran los falsos positivos predichos
> por el análisis original.
>
> El contenido original del bug se conserva debajo para registro
> histórico.

---

**Severidad: baja, posible falso positivo/negativo.**

El status `fallo_cruza_archivos` se activa cuando `(tomo, pg_fin + 1)`
está en un `.md` distinto al de `pg_ini`. Pero como el cursor está
mal (§3.6.a), este status puede estar capturando un caso ligeramente
distinto al esperado:

- **Caso real "fallo cruza archivos"**: el fallo arranca en
  `archivo_X` y su última página está en `archivo_Y`.
- **Caso que detecta el código actual**: la primera página del
  **siguiente** fallo arranca en un archivo distinto al del actual.

Ambos son aproximadamente equivalentes en la mayoría de los casos
(porque la última página del fallo actual y la primera del siguiente
suelen estar contiguas físicamente), pero pueden divergir en bordes
exactos. Después de corregir 3.6.a, este status habría que revisarlo
para ver si captura lo correcto.

#### 3.6.e — Hojas complementarias en tomos 331-334 (efecto colateral del fix §3.6.a)

> **✅ RESUELTO Fase 1 2026-05-09: 39 casos `pagina_fin_no_en_mapa`
> reasignados (32 → `ok_pg_fin_redirigida`, 7 →
> `ok_cortado_en_indice`). Causa estructural en el corpus, fix
> estructural en el cruzador. Fase 2 pendiente para los 43
> `pagina_no_en_mapa` (fenómeno especular).**

##### El fenómeno

Tras el fix de §3.6.a, aparecieron 39 casos con status
`pagina_fin_no_en_mapa`, concentrados en tomos 331-334 (10+11+10+9).
Investigación caso por caso reveló que **estos fallos no tienen bug
en el pipeline — tienen un problema estructural en el corpus
editorial**.

##### Causa

Los tomos 331-334 contienen **hojas complementarias**: páginas que
aparecen en el índice editorial pero no existen físicamente en el
`.md`. Marca textual literal:

```
HOJA COMPLEMENTARIA
Hoja incorporada a los efectos de permitir la búsqueda por
página dentro del Volumen.
```

Búsqueda contra el corpus muestra **95 ocurrencias** de "HOJA
COMPLEMENTARIA" distribuidas en los 11 `.md` de tomos 331-334. La
distribución por archivo:

| Archivo | Hojas complementarias |
|---|---:|
| LibroVol331.1.md | 13 |
| LibroVol331.2.md | 3 |
| LibroVol331.3.md | 13 |
| LibroVol332.1.md | 11 |
| LibroVol332.3.md | 10 |
| LibroVol333.1.md | 7 |
| LibroVol333.2.md | 8 |
| LibroVol333.3.md | 7 |
| LibroVol334.1.md | 9 |
| LibroVol334.2.md | 11 |
| LibroVol334.3.md | 3 |

Cuando una hoja complementaria cae exactamente en la `pagina_fin` que
el catálogo registró para un fallo (porque el fallo siguiente arranca
después del salto), el cruzador busca esa página en el mapa, no la
encuentra (porque no existe físicamente), y cae al fallback "última
línea del archivo". Eso produce un bloque gigantesco que se procesa
mal en Etapa 4.

##### Caso testigo: `331_p373`

`331_p373` (Pizarro, Julio César c/ Orígenes A.F.J.P.) ocupa páginas
372-377 del tomo 331. El catálogo registra `pagina_fin = 379` porque
ese es el inicio del fallo siguiente (`331_p379`, Villarreal). Pero
las páginas 378 y 379 no existen físicamente: tras la página 377 hay
una `HOJA COMPLEMENTARIA` y después arranca directamente la página
380 con la sección de marzo. El mapa de páginas confirma el salto:

```
331  LibroVol331.1.md  14080  377
331  LibroVol331.1.md  14129  380   ← saltó de 377 a 380
```

Resultado pre-fix §3.6.a: el bug `pg_fin + 1` buscaba página 380, que
sí existe → bloque "ok" pero inflado por la página extra (~32 líneas).

Resultado post-fix §3.6.a: el cruzador busca página 379, que no
existe → cae al fallback → bloque desde línea 13935 hasta el final
físico del `.md` (~32.000 líneas). El parser procesa todo eso como
un solo fallo y produce `word_count = 293.804` (vs 449 pre-fix).

**El bug original "compensaba" el problema editorial por accidente.**
Cuando se arregló el bug, el problema editorial quedó al descubierto.

##### Diagnóstico: no es bug del pipeline

El cruzador hace lo correcto: busca la página y no la encuentra
porque el catálogo registró una `pg_fin` que no existe físicamente.
El error está aguas arriba: el catálogo (Etapa 2) extrae `pg_fin` del
índice editorial sin saber que entre dos fallos puede haber una hoja
complementaria. El detector de páginas (Etapa 1) tampoco está
fallando: las páginas 378-379 efectivamente no existen.

##### Mitigación temporal (superada por Fase 1)

Pre-fix, los 39 casos eran identificables vía
`status_localizacion == 'pagina_fin_no_en_mapa'` y se filtraban
antes de análisis estadístico (igual que `fallo_cruza_archivos`).
Post-fix Fase 1, este filtro ya no es necesario: los 32 redirigidos
quedaron como `ok_pg_fin_redirigida` (status análogo a `ok` para
fines analíticos), y los 7 sin próxima página quedaron como
`ok_cortado_en_indice` (mismo tratamiento que los últimos fallos
genuinos).

##### Fix aplicado: Fase 1 (resuelto 2026-05-09)

**Diseño**. En `cruzar_catalogo_y_mapa.py`, la rama del fallback
`pagina_fin_no_en_mapa` se reemplazó por una cascada que primero
busca la **próxima página existente en el mismo archivo** después de
`pg_fin` y la usa como `linea_fin = linea_proxima - 1` (status
`ok_pg_fin_redirigida`). Si no hay próxima página en el archivo
(fallo es de hecho el último útil), reusa la lógica ya validada de
`ok_cortado_en_indice` o `ultimo_del_tomo`.

La función `cruzar` recibió un argumento adicional, `mapa_por_archivo`
(dict `{(tomo, archivo): [(linea_header, pagina), ...]}`), que ya era
producido por `cargar_mapa` y se descartaba. La firma cambió y la
llamada en `procesar` se actualizó correspondientemente.

**Por qué Opción A y no Opción B**. La Opción B propuesta
originalmente (usar `linea_inicio` del fallo siguiente) resultó
inviable: en los 39 casos, el fallo siguiente está exactamente en el
estado especular `pagina_no_en_mapa` (su `pagina_inicio` también es
una página inexistente porque la hoja complementaria ocupa el lugar
donde debería arrancar). La Opción A (próxima página existente)
resolvió 32 de los 39 directamente; los 7 restantes son últimos
útiles del archivo y se cerraron por la rama `ok_cortado_en_indice`.

**Resultado empírico**.

| Status | Pre-fix | Post-fix |
|---|---:|---:|
| `pagina_fin_no_en_mapa` | 39 | 0 |
| `ok_pg_fin_redirigida` (nuevo) | — | 32 |
| `ok_cortado_en_indice` | 19 | 26 (+7) |
| `ok` | 5741 | 5741 (sin cambio) |
| `fallo_cruza_archivos` | 20 | 20 (sin cambio) |
| `pagina_no_en_mapa` | 43 | 43 (sin cambio) |
| **Total** | 5862 | 5862 |

**Validación caso testigo `331_p373` (Pizarro)**:

| Métrica | Pre-§3.6.a | Post-§3.6.a (gigante) | Post-§3.6.e |
|---|---:|---:|---:|
| `word_count` | 449 (compensado por bug) | 293.804 | **449** |
| `linea_fin` | — | ~32.000 (final del .md) | 14.128 |
| `pista_fin` | — | (cascada agotada) | `caratula_siguiente` |

El parser cierra el bloque en la línea anterior al header de página
380 (`linea_fin = 14128`) y `detectar_fin_real` corta más arriba,
sobre la disidencia de Argibay. El word_count vuelve exactamente al
valor pre-§3.6.a, confirmando que el fix no introduce ruido sobre los
casos previamente correctos.

**Validación distribución de los 32 redirigidos**: 30 con
`pista_fin = sumario_siguiente`, 2 con `caratula_siguiente`, 0 con
`fallback_catalogo`. Esto significa que el detector siempre encontró
una pista real dentro del bloque acotado — confirmación
estructural, no por accidente. Word counts en rango natural (378 -
12.126).

**Cobertura efectiva post-fix**: `ok` + `ok_pg_fin_redirigida` +
`ok_cortado_en_indice` = 5799/5862 = 98,9%. Si se cuentan también
los `fallo_cruza_archivos` con su mitigación, sube a 99,3%. Los 43
`pagina_no_en_mapa` quedan como residuo legítimo, pendientes para
Fase 2.

**Caveat menor**. Para algunos casos `ok_cortado_en_indice`,
`detectar_fin_real` puede asignar `linea_fin_real` levemente
superior a `linea_fin` del cruzador (≤13 líneas observadas en
`333_p1869` y `334_p698`). El contenido excedido pertenece al inicio
del aparato de índices del tomo, no a otro fallo. Es comportamiento
preexistente del detector (independiente del fix §3.6.e), de impacto
acotado y no bloqueante. Se anota para auditoría futura.

##### Fase 2 (pendiente)

Los 43 casos `pagina_no_en_mapa` son la "otra cara" del mismo
fenómeno editorial: fallos cuya `pagina_inicio` declarada por el
catálogo no existe físicamente porque hay una hoja complementaria
inmediatamente antes. La lógica simétrica al fix Fase 1 sería:
cuando `(tomo, pagina_inicio)` no está en el mapa, inferir `archivo`
desde el fallo anterior del catálogo y usar la próxima página
existente como `linea_inicio` real. Más invasiva que Fase 1, requiere
diseño y validación propios.

##### Distinción importante con §4.6.g

§4.6.g (`fallo_cruza_archivos`) es un fenómeno *real*: hay 20 fallos
que efectivamente cruzan archivos. §3.6.e es un fenómeno *espurio*:
los 39 casos no cruzaban archivos, simplemente tenían una hoja
complementaria entre el fin del fallo actual y el inicio del
siguiente. Pre-fix, ambos producían el mismo síntoma operativo
(bloques gigantescos), por lo que la mitigación era la misma.
Post-fix Fase 1, los 39 casos espurios se cerraron y los 20 casos
reales de §4.6.g siguen requiriendo su propia mitigación.

### 3.7 Limitaciones conocidas

1. **Bug `pg_fin + 1`** (§3.6.a) afecta a TODOS los bloques `ok`. El
   parser compensa parcialmente con `detectar_fin_real`.
2. **Off-by-one en `ok_cortado_en_indice`** (§3.6.b): los 19 bloques
   correspondientes incluyen la línea del header del índice de
   nombres como última línea.
3. **43 fallos sin localizar** (§3.6.c) en tomos 331–334. Sus filas
   en `fallos_localizados.csv` tienen `archivo`, `linea_inicio` y
   `linea_fin` vacíos.
4. **`fallo_cruza_archivos` ambiguo** (§3.6.d): definición operacional
   no exactamente coincide con la conceptual.
5. **Ningún status diagnostica el bug `pg_fin + 1`**: como el bug se
   "compensa" con un cursor desplazado pero válido, los 5.773 `ok`
   pasan los chequeos. No hay forma de detectar esto sin validación
   externa contra datos.
6. **El cruzador no valida**: que `pagina_fin` del catálogo coincida
   con alguna página real del archivo, ni que el rango
   `linea_inicio..linea_fin` sea no-vacío y monótono. Errores
   silenciosos en estas dimensiones quedan en el output sin marca.

### 3.8 Estado de validación de la sección

- ✅ Bug `pg_fin + 1` (§3.6.a) **confirmado contra datos**: 5.695/5.695
  pares consecutivos (100%) muestran `linea_fin(actual) >
  linea_inicio(siguiente)` con inflado promedio de 32,4 líneas.
- ✅ Distribución de status confirmada contra
  `fallos_localizados.csv`: 5.773 `ok`, 43 `pagina_no_en_mapa`, 27
  `fallo_cruza_archivos`, 19 `ok_cortado_en_indice`, cero en los tres
  fallbacks.
- ✅ Concentración de `pagina_no_en_mapa` en tomos 331–334
  (§3.6.c) confirmada contra datos: 43/43 casos son de esos cuatro
  tomos.
- ✅ Patrón de `fallo_cruza_archivos` (un caso por borde editorial
  entre `.md` del mismo tomo) confirmado contra
  `fallos_localizados_huerfanos.csv`.
- ✅ Convenciones cruzadas críticas (§3.3) confirmadas leyendo el
  código del cruzador y comparando con las convenciones documentadas
  en §1 y §2.
- ⏳ Bug indexación 0/1 en `ok_cortado_en_indice` (§3.6.b) **no
  validado contra `.md` real**. Requiere abrir uno de los 19 archivos
  afectados y verificar qué hay en la línea declarada como
  `linea_fin`.
- ⏳ Hipótesis sobre origen de `pagina_no_en_mapa` en tomos 331–334
  (§3.6.c) **no validada**. Requiere inspeccionar el inicio de un
  `.md` de esos tomos.
- ⏳ Comportamiento de `fallo_cruza_archivos` después de corregir
  `pg_fin + 1` (§3.6.d) no analizado en profundidad.

### 3.9 Puntos de fricción con Etapa 4 (parser)

#### F3.9.a — Bloques inflados: el parser ve siempre una página del fallo siguiente al final

Consecuencia directa de §3.6.a. El parser recibe bloques cuyo
`linea_fin` está sistemáticamente ~32 líneas dentro del fallo
siguiente. Tiene que detectar el final real desde dentro del bloque,
con una cascada de pistas que está documentada en HALLAZGOS para §4
(`detectar_fin_real`: carátula del siguiente → sumario nuevo →
marcador de apertura → firma actual). La existencia y complejidad de
esa cascada es **una compensación de Etapa 4 para un bug de Etapa 3**.

Corregir §3.6.a probablemente simplificaría drásticamente el parser:
muchos casos resueltos por la cascada se resolverían con sólo
respetar `linea_fin`.

#### F3.9.b — Los 70 huérfanos requieren tratamiento especial en el parser

Los 70 fallos con `status not in ('ok', 'ok_cortado_en_indice')`
tienen `archivo` o `linea_inicio` o `linea_fin` vacíos. El parser
tiene que decidir qué hacer con cada uno. Documentar en §4.

#### F3.9.c — `linea_inicio` apunta al header tipográfico, no a la carátula

Reiteración de F1.10.a. El parser tiene que avanzar desde
`linea_inicio` para encontrar la carátula real del fallo (saltando
header tipográfico, líneas acompañantes, posibles colas del fallo
anterior).

---

## Etapa 4 — `parser.py`

### 4.1 Qué hace

Recorre los `.md` del corpus consumiendo simultáneamente la
localización producida por Etapa 3 (`fallos_localizados.csv`) y el
mapa físico de páginas producido por Etapa 1 (`mapa_paginas.csv`),
y por cada fallo localizado extrae 39 atributos analíticos al
nivel de fallo y 19 al nivel de voto individual. Es la etapa donde
el corpus deja de ser "un mapa de dónde están las cosas" y pasa a
ser un dataset estructurado: cada fallo queda con su carátula,
fecha, jueces firmantes, dispositivo, considerando, conteo de
palabras, posición individual de cada juez y clasificación
tipológica del voto.

A diferencia de las tres etapas previas, el parser no es una etapa
de cadena lineal: consume tres fuentes en paralelo y opera sobre
los `.md` directamente, no sobre derivados intermedios. La
localización de Etapa 3 le dice "dónde está cada fallo"; el mapa
de páginas le dice "cuál es el siguiente header tipográfico"; y
el `.md` le da el cuerpo crudo del bloque a procesar.

El parser hace además una segunda función crítica: **compensar el
bug §3.6.a** de Etapa 3. Como los bloques que recibe vienen
sistemáticamente inflados con la primera página del fallo
siguiente, el parser tiene que detectar el final real de cada
fallo desde dentro del bloque mediante una cascada de pistas
estructurales (`detectar_fin_real`). Esa cascada, y todas las
heurísticas asociadas (filtros de tokens, mitad de bloque,
detector de sumarios-con-link), son la huella en el código del
trabajo de compensación.

### 4.2 Inputs y outputs

| | |
|---|---|
| **Input principal 1** | `output/localizacion/fallos_localizados.csv` (Etapa 3) |
| **Input principal 2** | `output/mapa/mapa_paginas.csv` (Etapa 1) |
| **Input principal 3** | Carpeta `corpus/` con archivos `LibroVol*.md` |
| **Output principal 1** | `output/parser/csjn_casos.csv` (5.819 filas) |
| **Output principal 2** | `output/parser/csjn_casos_votos.csv` (21.876 filas) |

El parser **no consume** `catalogo.csv` ni `secciones_indices.csv`
directamente. Toda la información del catálogo le llega via
`fallos_localizados.csv` (que ya integró catálogo y mapa). Esta es
una decisión de diseño deliberada: el parser hereda 0-indexed para
todas las líneas (Etapa 1) y nunca toca los valores 1-indexed de
secciones (Etapa 2). La consecuencia es que el bug 0/1 de §3.6.b
no se propaga al parser, y la indexación interna del parser es
homogénea — ver §4.3.

#### 4.2.a — Estructura de `csjn_casos.csv`

39 columnas con datos actuales. Una fila por fallo localizado
con `status != 'pagina_no_en_mapa'` — ver §4.4 sobre cómo se
filtran los huérfanos.

| # | Columna | Tipo | Significado |
|---:|---|---|---|
| 1 | `caso_id_canonico` | str | Heredado de Etapa 2: `f"{tomo}_p{pagina_inicio}"` |
| 2 | `tomo` | int | Heredado de Etapa 2 |
| 3 | `case_name_indice` | str | Heredado de Etapa 2 (campo `nombres_indice`, primera carátula) |
| 4 | `case_name_cuerpo` | str | Carátula extraída del cuerpo del fallo. Fix v18: primario `extraer_caratula_v1` (busca `Vistos los autos: "X"`), fallback `find_case_name` (heurística v12) |
| 5 | `case_name_cuerpo_legacy` | str | **Shadow**: siempre guarda lo que produciría `find_case_name`, para auditar el diff del Fix v18 |
| 6 | `date` | str | Fecha del fallo. Cascada de tres pasos: 10 líneas tras apertura → última fecha del bloque → primera fecha en primeras 30 líneas |
| 7 | `apertura_tipo` | str | `fallo`, `sentencia` o vacío. Detectado por regex `RE_APERTURA = ^(FALLO\|SENTENCIA) DE LA CORTE SUPREMA\s*$` |
| 8 | `outcome` | str | Una de 13 categorías más `otro` y `sin_dispositivo` (ver §4.5) |
| 9 | `voting_pattern` | str | `unanime`, `disidencia`, `segun_su_voto`, `mixed`, `sin_firma`, vacío |
| 10 | `n_jueces` | int | Cantidad de jueces detectados en firma |
| 11 | `n_titulares` | int | Cantidad de jueces titulares (excluye conjueces) |
| 12 | `n_votos_svoto` | int | Cantidad de votos "según su voto" |
| 13 | `n_disidencias` | int | Cantidad de disidencias |
| 14 | `dictamen_presente` | bool/'0' | `True`, `False` o `'0'` (los 164 `sumario_con_link` — anomalía de tipos, ver §4.6) |
| 15 | `is_originaria` | bool | Cuatro señales: texto `originaria`, art. 117 CN, `Originario` en case_name, `forma originaria` |
| 16 | `is_full_bench` | bool | Pleno completo |
| 17 | `is_merit_decision` | bool | Decisión sobre el fondo |
| 18 | `word_count` | int | Conteo de palabras del bloque sin dictamen |
| 19 | `wc_mayoria` | int | Bloque sin dictamen y antes de `inicio_votos_indiv` |
| 20 | `wc_votos` | int | Desde `inicio_votos_indiv` hasta el fin |
| 21 | `wc_considerando` | int | Sobre `considerando_text` |
| 22 | `wc_dictamen` | int | Suma de palabras de líneas en `lineas_dictamen` (v17) |
| 23 | `firma_raw` | str | Texto crudo de las líneas de firma |
| 24 | `jueces` | str | Jueces detectados (lista) |
| 25 | `jueces_conocidos` | str | Subset de jueces en lista canónica |
| 26 | `jueces_desconocidos` | str | Resto |
| 27 | `posiciones` | str | Posición de cada juez (mayoría / disidencia / según su voto / por su voto) |
| 28 | `tribunal_origen` | str | Texto extraído tras `Tribunal/Juzgado/Cámara de origen:` |
| 29 | `tribunal_origen_status` | str | `originaria`, `apelado_detectado`, `sin_marcador`, vacío |
| 30 | `por_ello_text` | str | Texto del dispositivo desde `Por ello` o variante |
| 31 | `considerando_text` | str | Texto entre `Considerando:` y `Por ello`, sin dictamen |
| 32 | `source_file` | str | `.md` de origen |
| 33 | `linea_inicio` | int | **0-indexed**. Heredado del mapa (header tipográfico de página de inicio) |
| 34 | `linea_fin` | int | **0-indexed**. Heredado de Etapa 3 (con bug §3.6.a) |
| 35 | `linea_fin_real` | int | **0-indexed**. Calculado por `detectar_fin_real`. Es lo que el parser efectivamente usó como fin del bloque |
| 36 | `status_localizacion` | str | Heredado de Etapa 3 con sub-status del parser (ver §4.4) |
| 37 | `status_fin` | str | `fin_dentro_bloque`, `fin_extendido_pag_compartida`, `fin_por_firma_actual`, `fin_no_detectado` |
| 38 | `pista_fin` | str | Cuál pista de la cascada disparó el `linea_fin_real`: `caratula_siguiente`, `sumario_siguiente`, `marcador_apertura_siguiente`, `firma_actual`, `fallback_catalogo` |
| 39 | `tipo_entrada` | str | `fallo` o `sumario_con_link` (v17). Los 164 `sumario_con_link` se cortocircuitan: campos analíticos vacíos |

#### 4.2.b — Estructura de `csjn_casos_votos.csv`

19 columnas con datos actuales. **Una fila por par
(caso, juez)**, no por voto separado: si un caso tiene 5 jueces
con voto unánime de mayoría, produce 5 filas en este archivo.

| # | Columna | Tipo | Significado |
|---:|---|---|---|
| 1 | `caso_id_canonico` | str | FK a `csjn_casos.csv` |
| 2 | `tomo` | int | |
| 3 | `date` | str | |
| 4 | `juez` | str | Nombre del juez |
| 5 | `posicion` | str | `mayoria`, `según su voto`, `por su voto`, `en disidencia` |
| 6 | `es_conocido` | bool | Si el juez está en la lista canónica |
| 7 | `outcome` | str | Heredado del caso |
| 8 | `voting_pattern` | str | Heredado del caso |
| 9 | `is_originaria` | bool | Heredado del caso |
| 10 | `is_full_bench` | bool | Heredado del caso |
| 11 | `is_merit_decision` | bool | Heredado del caso |
| 12 | `wc_mayoria` | int | Heredado del caso |
| 13 | `wc_votos` | int | Heredado del caso |
| 14 | `dictamen_presente` | bool | Heredado del caso |
| 15 | `texto_voto` | str | Texto del voto individual; **vacío para `posicion == "mayoria"`** |
| 16 | `wc_voto` | int | Conteo del texto del voto; **0 para `posicion == "mayoria"`** |
| 17 | `tipo_voto_sep` | str | A / B / C / D / E / indeterminado / vacío. **Vacío para `posicion == "mayoria"`** |
| 18 | `fragmenta_ratio` | str | Métrica de fragmentación de la decisión |
| 19 | `punto_divergencia` | str | Punto donde el voto diverge de la mayoría (cuando aplica) |

##### Regla central de interpretación

19.569 de las 21.876 filas (89,5%) tienen `texto_voto = ""`,
`wc_voto = 0` y `tipo_voto_sep = ""`. **Todas son posiciones de
mayoría**: el archivo de votos extrae texto y clasifica
únicamente para los votos separados (`según su voto`,
`por su voto`, `en disidencia`). La fila para un juez en mayoría
existe pero codifica solamente la pertenencia al cuerpo decisorio
mayoritario, no su voto individual.

| `posicion` | n filas | con `texto_voto` | sin `texto_voto` |
|---|---:|---:|---:|
| `mayoria` | 20.070 | 967 | 19.103 |
| `en disidencia` | 1.055 | 729 | 326 |
| `según su voto` | 745 | 607 | 138 |
| `por su voto` | 6 | 4 | 2 |

Las 967 filas con `posicion == "mayoria"` y `texto_voto != ""` son
casos donde el detector marcó la posición como mayoría pero el
loop de extracción capturó texto del voto individual — caso
intermedio que requiere validación manual sobre el `.md` (no se
hizo en esta sesión; ver §4.7).

### 4.3 Convenciones cruzadas

#### 4.3.a — Indexación 0-indexed homogénea

El parser declara explícitamente la convención (comentario en
línea 1022 del script). Hereda 0-indexed de:

- `linea_inicio` y `linea_fin` de `fallos_localizados.csv`
  (Etapa 3, que a su vez hereda 0-indexed de Etapa 1).
- `linea_header` de `mapa_paginas.csv` (Etapa 1, 0-indexed).

No consume `secciones_indices.csv` (1-indexed). Por eso el parser
**no hereda el bug 0/1** de §3.6.b — ver F2.6.b. El error de
indexación cruzada queda confinado a Etapa 3.

Internamente, el parser produce dos columnas más en `csjn_casos.csv`
(`linea_inicio`, `linea_fin`, `linea_fin_real`), todas en 0-indexed.

#### 4.3.b — Acoplamiento simultáneo a tres fuentes

A diferencia de Etapas 1, 2 y 3 (cada una consume una fuente
estable), el parser ensambla:

```
fallos_localizados.csv ─────┐
                            │
mapa_paginas.csv ──────────►│ procesar_archivo
                            │
corpus/{archivo}.md ────────┘
```

El `mapa_paginas.csv` se carga agrupado por `(tomo, archivo)` con
headers ordenados (función `cargar_proximos_headers`, línea 1237
del parser): el parser usa esta estructura para resolver
"siguiente header tipográfico" en `detectar_fin_real`. Esto NO se
puede derivar solo de `fallos_localizados.csv`, que tiene una fila
por fallo (no por header de página).

#### 4.3.c — Filtrado de los 43 `pagina_no_en_mapa` al cargar

`cargar_localizados` (línea 1725 del parser) descarta toda fila
con `status == 'pagina_no_en_mapa'` o sin `linea_inicio`. **El
parser nunca ve los 43 huérfanos de §3.6.c**.

Confirmado contra datos: `fallos_localizados.csv` tiene 5.862
filas, los 43 `pagina_no_en_mapa` se descartan, quedan 5.819, que
es exactamente la cantidad de filas en `csjn_casos.csv`. Cero
descartes silenciosos posteriores (ver §4.6 — el bug sospechado
4.f no se manifiesta en producción).

#### 4.3.d — Cruce de tomo no se mapea

`siguiente_caso` (líneas 1796–1807 del parser) ordena fallos por
tomo y mapea cada caso al siguiente del mismo tomo. **El último
fallo de cada tomo no tiene siguiente** y por lo tanto la pista 1
de `detectar_fin_real` (carátula del siguiente) no se puede
disparar para los 19 últimos del tomo. Para esos 19 casos, la
detección del fin real depende exclusivamente de las pistas 2–4
de la cascada o del fallback al catálogo.

### 4.4 Etapas internas del parser

`procesar_archivo` (líneas 1326–1721) opera fallo por fallo dentro
de cada `.md`. La secuencia de operaciones por fallo es la
siguiente.

#### 4.4.a — Carga y filtrado en `cargar_localizados`

Antes de procesar nada, `cargar_localizados` (línea 1725) lee
`fallos_localizados.csv` y filtra:

- Filas con `status == 'pagina_no_en_mapa'` se descartan.
- Filas con `linea_inicio` vacío también.

Esto es **el único filtro silencioso** del parser. Verificación
contra datos: 5.862 − 43 = 5.819 filas, exactamente lo que llega
a la salida. Cero pérdidas posteriores.

#### 4.4.b — Construcción del bloque inicial

`construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin)`
(línea 1016) devuelve `lines[linea_inicio : linea_fin + 1]`. El
bloque incluye `linea_fin`, ambos índices son 0-indexed (declarado
en docstring de la función, línea 1022).

El bloque inicial **es el bloque inflado del catálogo** —
contiene en promedio 32 líneas extra del fallo siguiente (§3.6.a).

#### 4.4.c — Detección del fin real (`detectar_fin_real`)

Cascada de cuatro pistas (línea 1153). Detallada en §4.5.b.
Devuelve la tupla `(linea_fin_real, status_fin, pista_fin)`.

#### 4.4.d — Reconstrucción del bloque

El bloque se construye **una segunda vez** con `linea_fin_real`
(línea 1385). A partir de aquí, todo el procesamiento opera sobre
el bloque recortado (o, con menor frecuencia, extendido).

#### 4.4.e — Detección de apertura clásica

`detectar_apertura_en_bloque` (línea 1034) busca la primera línea
que matchee `RE_APERTURA = ^(FALLO|SENTENCIA) DE LA CORTE SUPREMA\s*$`.
Devuelve `(apertura_tipo, apertura_rel)` donde `apertura_rel` es
0-indexed dentro del bloque, o `(None, None)` si no encuentra.

`apertura_idx` es el equivalente absoluto en `lines`:
`apertura_idx = linea_inicio + apertura_rel` cuando hay marcador,
`apertura_idx = linea_inicio` cuando no.

#### 4.4.f — Refinamiento de `status_localizacion`

Si `apertura_rel is None`, el parser sufija el status original con
`_sin_marcador_apertura` (para `ok`) o `_sin_marcador` (para los
demás). Resultado contra datos:

| Status original (Etapa 3) | Sin marcador | Con marcador | Total |
|---|---:|---:|---:|
| `ok` | 185 | 5.588 | 5.773 |
| `ok_cortado_en_indice` | 1 | 18 | 19 |
| `fallo_cruza_archivos` | 1 | 26 | 27 |

Los 187 sin marcador se concentran en tomos modernos
(343, 345–348) — ver §4.6.

#### 4.4.g — Detector v17 de sumario-con-link

Si el bloque contiene el patrón `RE_SUMARIO_LINK` (línea 133)
en cualquier línea, el caso se cortocircuita: se llama a
`construir_caso_sumario_link` (línea 1426) con campos analíticos
vacíos y `tipo_entrada = "sumario_con_link"`, y `continue`.

**No depende de si el parser podría detectar firma**. La razón
está en el comentario del código (líneas 1416–1421): cuando un
fallo termina y un sumario empieza en la misma página, el bloque
del sumario arrastra firma del fallo previo. La presencia del
patrón es señal suficiente.

Resultado contra datos: 164 casos cortocircuitados, todos en
tomos 345–349. Coherente con la motivación documentada
(la práctica editorial de sumarios-con-link arranca en tomo 345).

#### 4.4.h — Cascada de fecha (líneas 1450–1476)

Tres pasos:

1. Si hay apertura: buscar fecha en las 10 líneas siguientes
   al marcador.
2. Si no hay apertura: buscar la **última** fecha "Buenos Aires"
   del bloque (asumiendo que la del dictamen está antes).
3. Fallback v15: primera fecha del bloque en las primeras 30
   líneas.

El comentario del código (línea 1446) admite que el paso 2 puede
capturar la fecha del dictamen como falso positivo, porque
`lineas_dictamen` aún no está calculado a esa altura.

#### 4.4.i — `case_name_cuerpo` con Fix v18 (líneas 1491–1497)

- Si hay apertura:
  - `case_name_cuerpo_legacy = find_case_name(lines, apertura_idx)`
    (heurística v12, busca atrás desde apertura líneas con `c/`).
  - `case_name_cuerpo_v1 = extraer_caratula_v1(bloque, apertura_rel)`
    (busca `Vistos los autos: "X"` desde apertura).
  - `case_name_cuerpo = case_name_cuerpo_v1 or case_name_cuerpo_legacy`.
- Si no hay apertura: ambos vacíos.

`case_name_cuerpo_legacy` es **siempre** lo que produciría
`find_case_name`, para auditar el diff post-fix. Es columna
shadow eliminable en una corrida posterior cuando el fix esté
validado (comentario línea 1490).

#### 4.4.j — Tribunal de origen (línea 1500)

`find_tribunal_origen(lines, apertura_idx, apertura_idx + len(bloque))`.
La función busca `RE_TRIB_ORIG` (`Tribunal/Juzgado/Cámara de origen:`)
desde `apertura_idx` hasta el límite. **El segundo argumento
contiene un bug aritmético** — ver §4.6.

#### 4.4.k — Loop línea por línea (líneas 1513–1563)

Sobre el bloque ya recortado, en una sola pasada:

- Marca `lineas_dictamen` (set) entre `RE_DICT_HDR` y la siguiente
  línea con `RE_FECHA_LINEA` (`Buenos Aires, fecha`).
- Detecta votos individuales con `RE_VOTO_HDR` y `RE_DISID_HDR`,
  registra `marcadores_votos` con `(k_relativo, juez, tipo)`.
- Captura `por_ello_idx` con la primera apertura de dispositivo
  vía `detectar_apertura_dispositivo` (línea 92, que cubre 12
  patrones — ver §4.5.c).

#### 4.4.l — Considerando, dispositivo, firma, votos

- `extraer_considerando` (línea 536): texto entre `RE_CONSIDERANDO`
  y `por_ello_idx`, excluyendo dictamen. Con bug de fallback —
  ver §4.6.
- `classify_outcome` (línea 256): cascada que prioriza
  `inadmisible_280` y `inadmisible_acordada_4` en el considerando,
  luego patrones del dispositivo, fallback `otro`.
- `collect_firma_lines` desde `por_ello_idx + 1` (línea 423),
  recolecta hasta 40 líneas. `parse_firma` (línea 449) detecta
  jueces conocidos y calificadores.
- `extraer_textos_votos` (línea 559) le asigna a cada juez con
  voto separado el texto entre su marcador y el siguiente.
- `clasificar_tipo_voto` (línea 834) clasifica A/B/C/D/E o
  indeterminado.

#### 4.4.m — Word counts

Cuatro métricas (líneas 1585–1595):

- `wc_mayoria`: bloque sin dictamen y antes de
  `inicio_votos_indiv`.
- `wc_votos`: desde `inicio_votos_indiv` hasta el fin.
- `wc_considerando`: sobre `considerando_text`.
- `wc_dictamen` (v17): suma de palabras de cada `bloque[k]` con
  `k in lineas_dictamen`.

#### 4.4.n — `is_originaria` y `tribunal_origen_status`

`is_originaria` (línea 622) integra cuatro señales: texto de
competencia originaria, art. 117 CN, `Originario` en case_name,
`forma originaria` en cuerpo. Criterio amplio (cualquiera basta).

`tribunal_origen_status` (líneas 1599–1606) en cascada:

1. Si `is_originaria` → `originaria`.
2. Si `tribunal_str != "SIN_TRIBUNAL_ORIGEN"` → `apelado_detectado`.
3. Si `hay_tribunal_interviniente(lines, apertura_idx, apertura_idx + len(bloque))`
   → `apelado_detectado`. (Misma aritmética buggeada — §4.6.)
4. Si no, `sin_marcador`.

#### 4.4.o — Output del caso (línea 1637) y de los votos (línea 1680)

39 columnas en `csjn_casos.csv`. Por cada juez en firma, una fila
en `csjn_casos_votos.csv` con 19 columnas.

### 4.5 Heurísticas con su razón

#### 4.5.a — Filtros de tokens

`primer_token_de_caratula` (línea 1138) extrae el primer apellido
de `nombres_indice`. Filtros:

- `len(t) >= 4` chars.
- Lista negra: `otro`, `otros`, `sociedad`, `sucesion`, `empresa`,
  `compañía`, etc.
- Si todos los tokens fallan, devuelve el primero como fallback.

`detectar_fin_real`, pista 1 (línea 1190) aplica un filtro
**diferente**: `>= 5` chars sobre el mismo token. La inconsistencia
es real.

##### Inconsistencia entre los dos filtros

Apellidos de 4 chars (DIEZ, RUIZ, BLAS) **entran** al token via
`primer_token_de_caratula` (filtro `>= 4`), pero **no se usan**
como pista de carátula del siguiente en `detectar_fin_real`
(filtro `>= 5`). Caso ya identificado: `339_p1651` con primer
token "DIEZ" cae al fallback de firma porque no se puede usar
como pista.

**Razón probable**: con `>= 4`, tokens cortos pueden tener
falsos positivos al matchear contra palabras comunes del cuerpo
(`AUTOS`, `JUEZA`, `ACTA`...). Subir el umbral a 5 reduce el
ruido a costa de cobertura.

##### Decisión a tomar

Como decisión consciente (consistencia parser+auditor), está
documentada en HALLAZGOS como PF-4.x. Bajar el umbral a 4
ayudaría a cubrir los casos perdidos pero requeriría auditar
falsos positivos. Pendiente.

#### 4.5.b — Cascada de `detectar_fin_real`

Cuatro pistas en orden (líneas 1189–1234):

| # | Pista | Atrás | Adelante | Status si éxito |
|---:|---|---|---|---|
| 1 | Carátula del siguiente (`primer_token_siguiente`) | `lfc → li+5` | `lfc+1 → limite_adelante` | `fin_dentro_bloque` (atrás) o `fin_extendido_pag_compartida` (adelante) |
| 2 | Header de sumario nuevo | `lfc → mitad_bloque` | `lfc+1 → limite_adelante` | idem |
| 3 | Marcador de apertura siguiente (`FALLO/SENTENCIA/DICTAMEN`) | — | `lfc+1 → limite_adelante` | `fin_extendido_pag_compartida` |
| 4 | Firma del fallo actual | `lfc → li` | `lfc+1 → limite_adelante` | `fin_por_firma_actual` |
| — | Fallback | — | — | `fin_no_detectado` (= `lfc`) |

`limite_adelante` se calcula así (líneas 1172–1175):

- Si `proximo_header_pagina is not None and > lfc`:
  `min(proximo_header_pagina + 50, n - 1)`.
- Si no: `min(lfc + 200, n - 1)`.

Las pistas 1–3 devuelven `k - 1` (línea anterior al header del
siguiente). La pista 4 devuelve `k` directamente (la firma misma
forma parte del fallo).

##### Razón empírica de la cascada

Compensación específica para los dos modos de falla del catálogo
(comentario línea 1054 del parser):

- (a) catálogo extendió de más → bug §3.6.a, multi-fallo en
  bloque. Resuelto por pistas 1–3 con búsqueda atrás dentro del
  bloque.
- (b) catálogo cortó corto → firma cae en página compartida.
  Resuelto por pista 4 atrás, o por pistas 1–3 adelante hasta
  `limite_adelante`.

##### La cascada es efectivamente "una sola pista" en el corpus

Validación contra datos (Q1 de las queries de §4.6):

| `pista_fin` | n | % |
|---|---:|---:|
| `caratula_siguiente` | 5.005 | 86,0% |
| `sumario_siguiente` | 527 | 9,1% |
| `marcador_apertura_siguiente` | 166 | 2,9% |
| `firma_actual` | 120 | 2,1% |
| `fallback_catalogo` | 1 | 0,02% |

Los 5.005 + 527 + 166 = 5.698 (97,9%) se resuelven con pistas
1–3, todas dependientes del bloque inflado. Solo 120 (2,1%) caen
a la firma del fallo actual. La hipótesis 4.h del handoff queda
confirmada: **el grueso del trabajo de la cascada lo hace la
pista 1**, las demás son fallbacks raros, y la existencia misma
de la cascada es la huella de la compensación de §3.6.a.

#### 4.5.c — Detector de apertura de dispositivo

`detectar_apertura_dispositivo` (línea 92) cubre 12 patrones más
la regla "Por ello":

- `RE_POR_ELLO` con discriminador anti-argumental
  (`POR_ELLO_ARGUMENTAL` = 13 verbos como `concluyó`, `estimó`,
  `considera`...). Si la palabra siguiente a "Por ello" está en
  esa lista, no cuenta como dispositivo.
- `RE_DISPOSITIVO_VARIANTES` (línea 77): 11 alternativas
  empíricamente verificadas en `LibroVol329_3.md` sobre 79 fallos
  sin "Por ello":
  - `Por los fundamentos [y conclusiones del dictamen]` — 41/79.
  - `De conformidad con [lo dictaminado]` — 27/79.
  - Residuales: `Por todo lo expuesto`, `Por lo expuesto`,
    `Atento a`, `En consecuencia`, `En mérito a lo`,
    `En su mérito`, `Por todo ello`, `Por estas razones`.

##### Tolerancias OCR

El regex de `por_los_fund` acepta `conc[lu]+siones` (= `concusiones`,
typo OCR conocido en tomos 329–336).

##### Bugfix v11 documentado en código

El comentario de la función (líneas 102–107) registra que v10 tenía
roto el discriminador "Por ello" sin coma: el regex aceptaba
`Por ello concluyó` pero el `re.sub` no lo limpiaba, dejando
`first_w = 'por'` y saltándose la regla argumental. v11 cambió a
`[,.]?` opcional. Patrón típico del proyecto: bugs documentados
como cambios entre versiones, sin tests automáticos.

#### 4.5.d — `mitad_bloque` para la pista 2

La pista 2 (header de sumario nuevo) limita la búsqueda atrás a
`mitad_bloque = li + (lfc - li) // 2` (línea 1206).

##### Razón estructural

Evitar matchear sumarios del propio fallo X (que aparecen al
inicio del bloque). Restringir la búsqueda a la mitad inferior
fuerza que el sumario detectado pertenezca al fallo siguiente,
no al actual.

##### Circularidad con §3.6.a

`lfc` viene del catálogo inflado (~32 líneas extra). La "mitad"
se calcula sobre el bloque inflado. **En fallos cortos con
inflado proporcionalmente grande, "la mitad" puede caer dentro
del fallo siguiente**: la búsqueda atrás cubre menos del fallo
actual, y un sumario del fallo siguiente puede quedar fuera de
la zona buscada (matcheable desde la pista 1 adelante, pero no
atrás).

#### 4.5.e — Detector v17 de sumario-con-link es anti-contaminación por diseño

`RE_SUMARIO_LINK` (línea 133) tolera dos variantes:

- Tomos 345–346: `(*) Sentencia del [fecha]. Ver en https://sj.csjn.gov.ar/...`.
- Tomos 347–349: `(*) Sentencia del [fecha]. Ver fallo.`

La detección se hace **en cualquier línea del bloque**
(`any(...)` en línea 1422), no solo después del marcador o solo
en la línea final. Razón estructural (comentario del código,
líneas 1416–1421): cuando un fallo termina y un sumario empieza
en la misma página, el bloque del sumario arrastra firma del
fallo previo. La presencia del patrón es señal suficiente — las
firmas que pueda haber en el bloque pertenecen al fallo previo.

#### 4.5.f — Discriminadores semánticos del clasificador de tipo de voto

`clasificar_tipo_voto` (línea 834) usa cinco categorías. Las
heurísticas centrales (calibradas empíricamente, ver código):

- **Tipo B (art. 280)**: `wc_voto <= 250`. Calibración: ejemplos
  B típicos rondan las 89 palabras; el corpus puede tener
  variantes con párrafo adicional, por eso 250 con margen.
- **Tipo C (adhesión parcial)**: tres subpatrones (exclusión /
  hasta N / lista de adheridos). El último de la lista citada
  es el último adherido; divergencia en N+1.
- **Tipo A anafórico**: ventana de 250 chars previa que requiere
  "dictamen" para evitar falsos positivos (la frase "al que cabe
  remitirse" puede aplicar a precedente, no a dictamen).
- **Tipo D**: `wc_voto >= 1500 + estructura "Considerando: 1°)"`,
  o `is_merit + wc_voto >= 2500`.

#### 4.5.g — Limpieza mínima de carátulas

Igual que en Etapa 2, `find_case_name` y `extraer_caratula_v1`
no corrigen agresivamente: NBSP → espacio, juntar wraps, espacios
múltiples → uno solo. No tocan acentos, may/min ni OCR raro.

### 4.6 Bugs detectados

#### 4.6.a — Bug aritmético en `apertura_idx + len(bloque)`

> **🟡 RE-EVALUADO 2026-05-09: bug aritmético sobrevive, daño efectivo
> evaporado tras fix §3.6.a.**
>
> Re-cuantificación post-fix:
>
> | Métrica | Pre-fix §3.6.a | Post-fix §3.6.a | Δ |
> |---|---:|---:|---:|
> | tipo_entrada == fallo | 5.655 | 5.659 | +4 |
> | ... y apertura_tipo ≠ '' | 5.585 | 5.435 | −150 |
> | ... y tribunal_origen_status=apelado | 3.863 | 3.682 | −181 |
>
> La cota superior bajó de 3.863 a 3.682. Pero el cambio sustantivo
> es otro: con bloques que ya no incluyen 32 líneas del fallo
> siguiente, las "líneas extra" que el bug aritmético lee caen sobre
> líneas vacías, header de página, o final del archivo — no sobre un
> fallo siguiente. **El bug aritmético sigue pero el daño efectivo
> plausible es ~0.**
>
> Prioridad de fix: **baja** (cosmético post-fix §3.6.a). La aritmética
> sigue siendo incorrecta y vale la pena fixearla por higiene del
> código, pero no produce sesgo material en el output.
>
> Corrección original (sigue siendo válida): pasar `linea_inicio +
> len(bloque)` en lugar de `apertura_idx + len(bloque)`. El contenido
> original se conserva debajo.

---

**Severidad: media. Aritmética confirmada en código; daño
efectivo no medido contra `.md`. Afecta hasta 5.585 casos.**

##### El error

Líneas 1500 y 1603:
```python
tribunal_str = find_tribunal_origen(lines, apertura_idx, apertura_idx + len(bloque))
# y
hay_tribunal_interviniente(lines, apertura_idx, apertura_idx + len(bloque))
```

Aritmética. El bloque ya está recortado a `linea_fin_real` (línea
1385), por lo que:

```
len(bloque) = linea_fin_real - linea_inicio + 1   (función construir_bloque, línea 1031)
apertura_idx = linea_inicio + apertura_rel       (línea 1396)

apertura_idx + len(bloque) = linea_fin_real + apertura_rel + 1
```

`find_tribunal_origen` y `hay_tribunal_interviniente` usan
`idx_fin` como **límite exclusivo** (`range(idx_inicio, min(idx_fin, len(lines)))`,
líneas 389 y 416). Lectura efectiva: hasta `linea_fin_real + apertura_rel`
inclusive. **`apertura_rel` líneas más allá del fin real del
fallo.**

Cuando `apertura_rel = 0`: el límite cae en `linea_fin_real + 1`
exclusive → lee hasta `linea_fin_real` inclusive → comportamiento
correcto.

Cuando `apertura_rel is None`: `apertura_idx = linea_inicio`,
`apertura_rel` no participa en la suma → comportamiento correcto.

Cuando `apertura_rel > 0` (caso típico — el marcador
`FALLO DE LA CORTE SUPREMA` aparece después del dictamen y los
vistos): lee `apertura_rel` líneas extra, dentro del fallo
siguiente en escenario §3.6.a.

##### Cuantificación contra datos

| Condición | n |
|---|---:|
| Casos que ejecutan línea 1500 (`tipo_entrada == 'fallo'`) | 5.655 |
| De ellos, con `apertura_tipo != ''` (≈ `apertura_rel > 0`) | 5.585 |
| De ellos, con `tribunal_origen_status == 'apelado_detectado'` | 3.863 |

Cota superior del daño: 3.863 casos donde la lectura extra
podría haber capturado el "Tribunal de origen:" del fallo
siguiente en lugar del actual. **Cota superior**, no daño
efectivo: `find_tribunal_origen` retorna al primer match (línea
411), entonces si el fallo actual ya tiene `Tribunal de origen:`
en sus líneas legítimas, las líneas extra son inocuas.

##### Daño efectivo plausible

El daño efectivo se concentra en los casos donde el fallo actual
**no** tiene `Tribunal de origen:` (típicamente fallos cortos
tipo art. 280, originarios, o decisiones procesales) pero el
siguiente sí. Cuantificar requiere validación contra `.md` —
pendiente.

##### Corrección

Pasar `linea_inicio + len(bloque)` en lugar de
`apertura_idx + len(bloque)`. Equivalentemente, pasar
`linea_fin_real + 1`.

```python
# actual
tribunal_str = find_tribunal_origen(lines, apertura_idx, apertura_idx + len(bloque))
# corregido
tribunal_str = find_tribunal_origen(lines, apertura_idx, linea_inicio + len(bloque))
# o equivalente
tribunal_str = find_tribunal_origen(lines, apertura_idx, linea_fin_real + 1)
```

#### 4.6.b — Fallback `inicio_cons = 0` en `extraer_considerando`

> **🔴 PRIORIDAD SUBIDA 2026-05-09: pasó de 169 a 320 casos
> sospechosos post-fix §3.6.a.**
>
> Re-cuantificación post-fix:
>
> | Métrica | Pre-fix §3.6.a | Post-fix §3.6.a | Δ |
> |---|---:|---:|---:|
> | wc_considerando ≥ 0,9 × word_count | 169 | 320 | +151 |
> | ... y apertura_tipo == fallo | 152 | 229 | +77 |
> | wc_considerando == 0 | 1.751 | 1.681 | −70 |
>
> Los casos sospechosos casi se duplicaron. Lectura: con bloques más
> cortos (sin la página extra del fallo siguiente), un fallback que
> arrastra "todo el bloque" produce considerandos relativamente más
> cercanos al `word_count`. El bug se vuelve más visible porque el
> denominador (word_count) bajó.
>
> Prioridad de fix: **media-alta**. Pasa a ser el bug más relevante
> por fixear en el parser ahora que §3.6.a está resuelto. El contenido
> original se conserva debajo.

---

**Severidad: baja a media. 169 casos con `wc_considerando ≥ 0,9 ×
word_count` (sospecha de fallback gatillado).**

##### El error

`extraer_considerando` (línea 536) busca `RE_CONSIDERANDO` saltando
las líneas del dictamen. Si no encuentra (línea 549):

```python
if inicio_cons is None:
    # Fallback: a veces no hay marcador "Considerando:" explícito,
    # pero el considerando empieza igual. Tomamos desde apertura hasta
    # por_ello_idx como aproximación.
    inicio_cons = 0
```

El **comentario** dice "desde apertura hasta `por_ello_idx`". El
**código** hace `inicio_cons = 0` — desde el inicio del bloque,
no desde apertura. Discrepancia entre comentario y código.

Consecuencia: el fallback arrastra todo el bloque desde la
primera línea (carátula, header de página, vistos, etc.),
excluyendo solo `lineas_dictamen`. El considerando termina
inflado.

##### Cuantificación contra datos

| Condición | n |
|---|---:|
| Casos con `wc_considerando >= 0,9 × word_count` | 169 |
| De ellos, con `apertura_tipo == 'fallo'` | 152 |
| Casos con `wc_considerando == 0` (no encontró considerando ni gatilló fallback) | 1.751 |

El dato sorprendente: **152/169 casos sospechosos tienen
`apertura_tipo == 'fallo'`** (es decir, el marcador clásico fue
detectado). El fallback se gatilla por la ausencia de
`RE_CONSIDERANDO`, no por la ausencia de apertura. Esos 152 son
casos donde hay marcador `FALLO DE LA CORTE SUPREMA` pero no se
detecta `Considerando:` debajo — probablemente porque la línea
está formateada distinto (sin dos puntos, con prefijo, OCR
roto).

Los 1.751 con `wc_considerando == 0` son distintos: ahí
`por_ello_idx` también es `None`, así que `fin_cons = len(bloque)`
y la suma ignora todo el bloque. **El fallback se gatilla pero
produce considerando vacío** (no inflado). Inspección rápida:
el grueso son `ok` (1.604) y `ok_sin_marcador_apertura` (128).

##### Corrección

Cambiar `inicio_cons = 0` por `inicio_cons = apertura_rel + 1`
cuando hay apertura, o por `0` solo cuando no hay apertura. Esto
alinearía el código con el comentario y reduciría el inflado del
considerando para 152 casos. Pendiente.

#### 4.6.c — Fecha sin marcador de apertura captura del dictamen

**Severidad: baja. Hasta 35 casos potencialmente afectados.**

##### El error

`fecha_str` cascada (líneas 1450–1476). Caso (b) — sin marcador
de apertura — hace búsqueda atrás de la última fecha del bloque.
**El propio comentario del código** (línea 1446) admite que
`lineas_dictamen` aún no está calculado, así que la fecha
capturada puede ser la del dictamen.

##### Cuantificación contra datos

| Condición | n |
|---|---:|
| Casos con `apertura_tipo == ''` | 234 |
| De ellos, `tipo_entrada == 'sumario_con_link'` (cortocircuitan antes) | 164 |
| De ellos, `tipo_entrada == 'fallo'` (ejecutan caso b) | 70 |
| De los 70, con `date != ''` (fecha asignada) | 35 |

35 casos donde se gatilla el fallback (b) y produce fecha. La
mitad de esos 35 podrían tener fecha del dictamen, no del fallo.
Validación contra `.md` pendiente para 2-3 casos.

##### Corrección

Calcular `lineas_dictamen` antes del bloque de fecha, o filtrar
las líneas de la búsqueda atrás. Cambio menor pero requiere
reordenar el flujo.

#### 4.6.d — `extraer_textos_votos` incluye el header del voto

**Severidad: baja, decisión de diseño con efecto colateral
menor.**

##### El error declarado vs el código

Comentario línea 577: "Extraer texto entre k_ini+1 y k_fin
(el k_ini es el header del voto)".

Código línea 578:
```python
texto = " ".join([bloque[k].strip() for k in range(k_ini, k_fin)
                  if bloque[k].strip()])
```

`range(k_ini, k_fin)`, no `range(k_ini + 1, k_fin)`. **El header
del voto queda concatenado al texto del voto**, contradiciendo
el comentario.

##### Efecto

El header del voto (`Voto del Señor Ministro Doctor...`) tiene
~10 palabras. Inflado constante de `wc_voto` por 10. Para votos
largos (tipo D, ≥1.500 palabras), efecto despreciable. Para
votos cortos:

- Tipo A (anafórico): texto ~30–50 palabras + header → 40–60.
  Sigue muy lejos del umbral B (≤250).
- Tipo B (art. 280): texto ~89 palabras + header → ~99. Margen
  de seguridad del umbral 250 sigue siendo amplio.

**No altera la clasificación A/B/C/D/E en ningún caso plausible.**

##### Naturaleza

Probablemente intencional: dejar el header en el texto permite
que `clasificar_tipo_voto` use información del header (tipo de
voto declarado, juez). Pero la **discrepancia con el comentario
es real**.

#### 4.6.e — `dictamen_presente == '0'` (string) en sumario_con_link

**Severidad: baja, inconsistencia de tipos en el output.**

##### El hallazgo

164 filas tienen `dictamen_presente == '0'` (string `'0'`) en lugar
de `True` o `False` como las otras 5.655 filas. Las 164 son
**exactamente** las `tipo_entrada == 'sumario_con_link'`.

Origen: `construir_caso_sumario_link` (línea 1426) probablemente
inicializa los campos analíticos con `0` numérico en vez de
`False` booleano. Al pasar por el writer CSV, se serializa como
`'0'` literal.

##### Efecto

Cualquier consumidor del CSV que filtre `df['dictamen_presente'] == True`
o `df['dictamen_presente'] == False` excluirá las 164 filas
`sumario_con_link`. Para análisis estadístico filtrado por
presencia de dictamen, la decisión correcta es excluir
sumarios-con-link de antemano (`df['tipo_entrada'] == 'fallo'`),
pero el tipo inconsistente puede generar errores silenciosos.

##### Corrección

En `construir_caso_sumario_link`, inicializar `dictamen_presente`
como `False` (no `0`) y revisar el resto de campos analíticos
para garantizar tipos consistentes.

#### 4.6.f — Bug 4.f (descarte silencioso): refutado empíricamente

**Severidad: nula. Estructura presente en código, sin
manifestación en producción.**

`construir_bloque_desde_localizacion` (línea 1029) puede
devolver `[]` si `linea_inicio > linea_fin`. La guarda en
`procesar_archivo` (línea 1387) hace `continue` sin emitir
mensaje. Si `detectar_fin_real` devolviera `linea_fin_real <
linea_inicio` (caso teóricamente posible si la pista de carátula
del siguiente matchea cerca del inicio del bloque, ya que la
búsqueda atrás solo excluye las primeras 5 líneas — línea 1196),
el segundo `construir_bloque` (línea 1385) descarte silencioso.

Cuantificación contra datos:

- `fallos_localizados.csv`: 5.862 filas.
- Filtro `pagina_no_en_mapa`: −43.
- Esperado en parser: 5.819.
- `csjn_casos.csv`: 5.819 filas. Cero descartes silenciosos.
- Casos con `linea_fin_real < linea_inicio`: 0.

El bug existe estructuralmente pero el corpus actual no lo
dispara. Documentado por completitud, sin acción inmediata.

#### 4.6.g — `fallo_cruza_archivos` produce bloques gigantescos

> **🟡 RE-EVALUADO 2026-05-09: 20 casos post-fix (vs 27 pre-fix), pero
> outlier máximo persiste.**
>
> Tras el fix §3.6.a, el detector de `fallo_cruza_archivos` quedó
> calibrado correctamente (§3.6.d disuelto). Cantidad bajó de 27 a 20
> casos legítimos.
>
> Sin embargo, el problema estructural sigue: los 20 casos que
> realmente cruzan archivos reciben `linea_fin = última línea física
> del .md` y producen bloques que pueden incluir el aparato editorial
> del final del archivo. El outlier máximo (`wc_mayoria` = 105.559)
> persiste post-fix.
>
> Prioridad: **media** (contenida a 20 casos identificables). Mitigación
> temporal sigue siendo la misma: filtrar
> `status_localizacion in ('fallo_cruza_archivos',
> 'fallo_cruza_archivos_sin_marcador')` antes de análisis estadístico.
> Costo de cobertura: 20/5.819 ≈ 0,3%.
>
> El contenido original se conserva debajo.

---

**Severidad: alta para los 27 casos afectados, contenida en
ese subset.**

##### El problema

Los 27 casos `fallo_cruza_archivos` (heredados de §3.6.d)
llegan al parser con `linea_fin = última línea física del .md
de inicio` (asignación en Etapa 3, línea 246 del cruzador). Para
estos casos, el bloque cubre desde el header del fallo hasta el
final físico del archivo — cientos o miles de líneas, incluyendo
el aparato editorial de índices del final del `.md`.

`detectar_fin_real` debería compensar, pero la cascada degrada:

| Pista | Fallos cruza_archivos | n |
|---|---|---:|
| `caratula_siguiente` | dispara correctamente atrás | 13 |
| `sumario_siguiente` | idem | 4 |
| `firma_actual` | fallback — puede caer en el aparato editorial | 10 |

10/27 (37%) caen al fallback `firma_actual`, comparado con
~2% del corpus general.

##### Cuantificación de outliers

`wc_mayoria` para los 27 cruza_archivos vs el resto:

| Métrica | cruza_archivos (n=27) | resto (n=5.792) |
|---|---:|---:|
| Mediana | 2.252 | 838 |
| p75 | 7.949 | 1.673 |
| Máximo | 105.559 | 31.547 |

**Los cinco fallos con `word_count` más alto del corpus son los
cinco con `word_count` más alto de cruza_archivos**:

| caso | tomo | word_count | pista_fin |
|---|---:|---:|---|
| 329_p4877 | 329 | 106.353 | firma_actual |
| 330_p2849 | 330 | 105.559 | caratula_siguiente |
| 329_p2949 | 329 | 96.323 | firma_actual |
| 330_p4263 | 330 | 94.119 | firma_actual |
| 330_p1309 | 330 | 78.787 | firma_actual |

Estos no son fallos legítimamente largos: 4/5 caen al fallback
`firma_actual`, lo que sugiere que el bloque procesado contiene
el aparato editorial completo del `.md`.

##### Corrección

Dependiente de §3.6.a y §3.6.d. Si Etapa 3 corrigiera
`pg_fin + 1` y la asignación de `linea_fin` para
cruza_archivos, el parser no necesitaría procesar bloques
gigantes.

##### Mitigación temporal

Filtrar `status_localizacion in ('fallo_cruza_archivos',
'fallo_cruza_archivos_sin_marcador')` antes del análisis
estadístico. Son 27 casos identificables. Con 5.819 casos en
total, descartarlos cuesta 0,5% de cobertura.

#### 4.6.h — `ok_sin_marcador_apertura` concentrado en tomos modernos

> **🟢 RECLASIFICADO 2026-05-09: 185 → 347 post-fix §3.6.a. No es
> bug, es información descriptiva.**
>
> El status `ok_sin_marcador_apertura` casi se duplicó tras el fix:
> 185 → 347 (+162). La lectura del cambio:
>
> - Pre-fix, el bug §3.6.a regalaba al parser ~32 líneas extra del
>   fallo siguiente. La cascada `detectar_fin_real` encontraba
>   marcadores de apertura del fallo *siguiente* en esas líneas y los
>   asignaba como si fueran del fallo actual.
> - Post-fix, esos marcadores espurios desaparecen. 162 fallos quedan
>   correctamente clasificados como "sin marcador detectado".
>
> Validación caso por caso (sesión 2026-05-09): de 163 fallos que
> pasaron de `ok` (pre) a `ok_sin_marcador_apertura` (post), 151
> tienen `wc_pre > wc_post` (consistente con "el bloque dejó de
> incluir contenido del fallo siguiente"), 11 tienen wc igual (con
> linea_fin más corto, casos sin contenido sustantivo), 1 tiene wc
> subió (caso pre con `wc=0` que pasó a `wc=132`, mejora). **Cero
> regresiones.**
>
> Prioridad: ninguna. Es un fenómeno editorial real del corpus que
> ahora se mide correctamente. Las hipótesis (a) cambio editorial,
> (b) OCR degradado, (c) fallos sin marcador como diseño editorial,
> son todas plausibles y la métrica honesta es 347, no 185.
>
> El contenido original se conserva debajo. Algunos números absolutos
> de la versión original (los 161/185 en tomos 343–348) ya no son
> aplicables — la nueva distribución requiere recálculo.

---

**Severidad: media, posible cambio editorial no contemplado.**

##### Distribución

185 casos `ok_sin_marcador_apertura`:

| Tomo | n |
|---|---:|
| 329 | 14 |
| 330 | 9 |
| 332 | 1 |
| 343 | 17 |
| 344 | 2 |
| 345 | 54 |
| 346 | 34 |
| 347 | 20 |
| 348 | 34 |

161/185 (87%) en tomos 343–348. De ellos, 117 son
`sumario_con_link` (que son los que cortocircuitan después).
Quedan **44 casos `ok_sin_marcador_apertura` con `tipo_entrada
== 'fallo'` en tomos modernos** que requieren atención: el
parser no encontró `FALLO/SENTENCIA DE LA CORTE SUPREMA`.

##### Hipótesis

(a) Cambio editorial: los tomos modernos pueden estar usando un
formato distinto del marcador (ej. minúsculas, prefijo
adicional, header diferente).

(b) OCR degradado: PDFs de tomos modernos pueden tener problemas
distintos de los viejos.

(c) Falsos positivos del detector v17 de sumario: algunos
sumarios-con-link no se detectan, y caen como
`ok_sin_marcador_apertura` con campos analíticos pobres.

##### Validación pendiente

Inspeccionar 3-5 casos de `ok_sin_marcador_apertura` en tomos
modernos contra `.md` real. Pendiente.

#### 4.6.i — Tomos antiguos sin `marcador_apertura_siguiente`

**Severidad: nula, hallazgo descriptivo.**

Cross-tab `tomo × pista_fin`:

| Tomo | `marcador_apertura_siguiente` | `sumario_siguiente` |
|---|---:|---:|
| 329 | 0 | 171 |
| 330 | 0 | 92 |
| 331 | 1 | 72 |
| 332 | 0 | 70 |
| 333 | 0 | 55 |
| 334 | 2 | 46 |
| 337 | 8 | 2 |
| 338 | 8 | 2 |
| 339 | 22 | 1 |
| 340–349 | 8–22 | 0–4 |

Inversión clara entre tomos viejos y modernos:

- **Viejos (329–334)**: la pista 3 no se gatilla casi nunca; la
  pista 2 (sumario nuevo) sí se usa mucho.
- **Modernos (337–349)**: la pista 3 se gatilla con frecuencia;
  la pista 2 casi no.

Hipótesis: en tomos viejos, los fallos siguen un patrón con
sumario-encabezado consistente (que la pista 2 detecta), y el
marcador `FALLO DE LA CORTE SUPREMA` puede estar faltando o
formateado distinto. En modernos, los sumarios desaparecieron y
el marcador está más presente, por lo que la pista 3 toma el
relevo.

##### Decisión

Ningún cambio. Es información descriptiva sobre el corpus, útil
para entender por qué la cascada tiene cuatro pistas distintas
en vez de una sola.

#### 4.6.j — RE_APERTURA estricto: doble espacio en CORTE  SUPREMA

> **✅ RESUELTO 2026-05-09**
>
> Fix aplicado: parser.py línea 57. Regex `RE_APERTURA` cambió de
> espaciado literal a `\s+` libre (alineado con el patrón de
> `RE_FECHA_LINEA` y `RE_FECHA_EXTRACT` líneas 58-59). También se
> agregó `re.I` por consistencia con el resto del parser.

##### El problema

El detector del marcador `FALLO DE LA CORTE SUPREMA` tenía la regex:

```python
RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA) DE LA CORTE SUPREMA\s*$")
```

Espaciado literal entre cada par de palabras. El comentario interno
del código (línea 1043) lo declara: "RE_APERTURA es estricto (línea
exacta = 'FALLO DE LA CORTE SUPREMA')".

##### El hallazgo

Búsqueda contra el corpus reveló 18 ocurrencias del marcador con
**doble espacio entre `CORTE` y `SUPREMA`**, todas concentradas en
`LibroVol343-1.md` (tomo 343, parte 1). Verificación caracter por
caracter: ambos espacios son código ASCII 32 (espacio normal, no
nbsp ni tab).

| Variante | Casos |
|---|---:|
| `FALLO DE LA CORTE SUPREMA` (espacio normal) | 5.717 |
| `SENTENCIA DE LA CORTE SUPREMA` | 120 |
| `FALLO DE LA CORTE  SUPREMA` (doble espacio) | 18 |

##### Por qué `\s+` libre y no tope (como `\s{1,2}`)

Las regex hermanas en el parser (`RE_FECHA_LINEA`, `RE_FECHA_EXTRACT`)
ya usan `\s+` libre sin tope. Aplicar el mismo patrón mantiene
consistencia interna del código. El riesgo de matchear líneas
anómalas con whitespace excesivo está mitigado por el `^...$` que
requiere que la línea entera sea exactamente el marcador.

##### Validación post-fix

| Métrica | Pre-fix | Post-fix |
|---|---:|---:|
| `ok` | 5.394 | 5.410 |
| `ok_sin_marcador_apertura` | 347 | 331 |
| `fallo_cruza_archivos_sin_marcador` | 1 | 0 |

**17 de 18 casos capturados** (16 pasaron de `ok_sin_marcador_apertura`
a `ok`, 1 de `fallo_cruza_archivos_sin_marcador` a
`fallo_cruza_archivos`). Cero regresiones.

##### El caso 18: `343_p646` (no capturado, patrón editorial irregular)

La línea 24641 de `LibroVol343-1.md` tiene el marcador con doble
espacio. Pero la cascada `detectar_fin_real` cortó el bloque del
caso `343_p646` en línea 24618 — antes del marcador. Por eso el
parser nunca lo procesa.

Inspección del `.md` reveló estructura editorial irregular:

1. Carátula del fallo en MAYÚSCULAS (`MONTEVER SA c/ DGA s/...`).
2. Tema en mayúsculas (`RECURSO EXTRAORDINARIO`).
3. **Sumario editorial** (~10 líneas).
4. Header tipográfico de página (`647 / DE JUSTICIA DE LA NACIÓN / 343`).
5. **Marcador `FALLO DE LA CORTE  SUPREMA`** (línea 24641).
6. Cuerpo del fallo.

La cascada cortó en (4) tomando el header de página como pista de
fin. Pre-fix §3.6.a, el bloque inflado tapaba este problema. Post-fix
queda al descubierto.

Esto **no es bug del fix RE_APERTURA**. Es un patrón editorial
distinto del estándar que la cascada `detectar_fin_real` no
contempla. Caso aislado en este corpus (1 detectado), documentado
para registro. Si aparecieran más en futuros catálogos, podría
justificarse extender la cascada para mirar más adelante antes de
aceptar un corte basado en header de página.

##### Otro patrón a futuro: 'FALLO DE LA CORTE' (sin SUPREMA)

El reporte post-fix de "Top desconocidos en firma" registra 33 casos
donde aparece la cadena `'FALLO DE LA CORTE'` (sin la palabra
`SUPREMA`). Es un patrón distinto, posiblemente fragmentos de OCR
roto o variantes editoriales. No relacionado con el fix actual,
documentado para investigación futura.

### 4.7 Limitaciones conocidas

1. **Tres versiones declaradas en el mismo archivo**: docstring
   línea 2 dice v17, línea 158 dice v18 (Fix 1), `argparse`
   línea 1765 dice v16. El script no es trazable a un único
   número de versión. Costo: confusión al revisar el changelog.

2. **`wc_dictamen` no validado exhaustivamente**: el propio
   docstring (línea 30) dice "tratar wc_dictamen como
   aproximación hasta ronda de validación".

3. **Bug aritmético §4.6.a en `apertura_idx + len(bloque)`**:
   afecta hasta 3.863 casos (cota superior, daño efectivo
   probablemente menor).

4. **Fallback `inicio_cons = 0` con comentario engañoso
   (§4.6.b)**: 152 casos con considerando inflado, 1.751 con
   considerando vacío.

5. **Inconsistencia de tipos en `dictamen_presente` (§4.6.e)**:
   164 filas con `'0'` literal en lugar de booleano.

6. **`extraer_textos_votos` incluye header del voto (§4.6.d)**:
   discrepancia entre código (línea 578) y comentario (línea
   577). Probablemente intencional, efecto cuantitativo
   despreciable.

7. **27 fallos `cruza_archivos` con bloques gigantescos
   (§4.6.g)**: los 5 con mayor `word_count` del corpus son de
   este subset. Filtrarlos del análisis estadístico es la
   mitigación recomendada hasta corregir §3.6.

8. **44 fallos `ok_sin_marcador_apertura` no-sumario en tomos
   modernos (§4.6.h)**: causa no diagnosticada.

9. **Decisión de diseño "voto" en `csjn_casos_votos.csv`** (§4.2.b):
   89,5% de las filas son posiciones de mayoría con
   `texto_voto = ""`, `wc_voto = 0`, `tipo_voto_sep = ""`. La
   estructura es por (caso, juez), no por voto separado. No es
   bug, pero es una convención no documentada en el archivo
   mismo y puede sorprender al consumidor que filtre por
   `tipo_voto_sep != ""`.

10. **No hay separación entre script y librería**: todas las
    constantes, funciones y `main` viven en un único archivo de
    1.944 líneas. Mantenibilidad limitada.

11. **Inconsistencia de filtros de tokens (§4.5.a)**: 4 chars
    en `primer_token_de_caratula`, 5 chars en
    `detectar_fin_real`. Decisión consciente pero documentar.

### 4.8 Estado de validación de la sección

- ✅ Distribución de `pista_fin` y `status_fin` confirmada
  contra datos: 5.005 `caratula_siguiente`, 527
  `sumario_siguiente`, 166 `marcador_apertura_siguiente`, 120
  `firma_actual`, 1 `fallback_catalogo`. La cascada es
  efectivamente "una sola pista" en el grueso del corpus.

- ✅ Refinamiento de `status_localizacion` confirmado:
  5.773 `ok` → 5.588 + 185 `ok_sin_marcador_apertura`;
  19 `ok_cortado_en_indice` → 18 + 1 `_sin_marcador`;
  27 `fallo_cruza_archivos` → 26 + 1 `_sin_marcador`.
  Suma 5.819 = 5.862 − 43.

- ✅ Bug 4.6.a (aritmética `apertura_idx + len(bloque)`)
  confirmado leyendo código (líneas 1500, 1603, 389, 416, 1031,
  1396). Cota superior de daño cuantificada (3.863 casos).

- ✅ Bug 4.6.b (fallback `inicio_cons = 0`) confirmado leyendo
  código (líneas 549–553) y cuantificado (169 casos sospechosos
  por proxy `wc_cons >= 0,9 × wc`, de los cuales 152 con
  apertura).

- ✅ Bug 4.6.c (fecha del fallback puede ser del dictamen)
  confirmado en código (líneas 1446, 1459–1467) y cuantificado
  (35 casos potencialmente afectados de un universo de 70).

- ✅ Bug 4.6.d (header del voto en texto) confirmado leyendo
  código (línea 578) vs comentario (línea 577). Efecto
  despreciable cuantitativamente.

- ✅ Bug 4.6.e (`dictamen_presente = '0'` en sumario_con_link)
  confirmado contra datos: 164/164 sumario_con_link tienen `'0'`,
  ninguna fila no-sumario lo tiene.

- ✅ Bug 4.6.f (descarte silencioso) **refutado empíricamente**:
  cero casos en producción.

- ✅ Bug 4.6.g (cruza_archivos con bloques gigantescos)
  confirmado contra datos: mediana wc_mayoria 2,7× la del corpus,
  los 5 outliers más grandes del corpus son de este subset, 37%
  caen a la pista 4.

- ✅ Hallazgo 4.6.h (`ok_sin_marcador_apertura` concentrado en
  modernos) confirmado contra datos: 161/185 en tomos 343–348.

- ✅ Hipótesis 4.h del handoff (cascada como "una sola pista")
  confirmada: 86% en `caratula_siguiente`, 97,9% en pistas 1–3
  combinadas.

- ⏳ Daño efectivo del bug 4.6.a no medido contra `.md` real.
  Requiere inspeccionar casos donde `find_tribunal_origen`
  produjo respuesta y verificar si proviene del fallo actual o
  del siguiente.

- ⏳ Validación de fechas sospechosas (§4.6.c) contra `.md` no
  hecha (35 casos).

- ⏳ Diagnóstico de los 44 `ok_sin_marcador_apertura` no-sumario
  en tomos modernos (§4.6.h) pendiente.

- ⏳ Validación de `wc_dictamen` no hecha (limitación
  reconocida en docstring).

- ⏳ Las 967 filas de votos con `posicion == 'mayoria'` y
  `texto_voto != ''` no inspeccionadas (§4.2.b). Caso intermedio
  poco frecuente pero merece chequeo.

### 4.9 Puntos de fricción con etapas anteriores

#### F4.9.a — La cascada de `detectar_fin_real` es la compensación de §3.6.a

Confirmado contra datos. El bloque del catálogo está
sistemáticamente inflado ~32 líneas. El parser tiene que
recortar ese inflado desde dentro del bloque mediante una
cascada de cuatro pistas. **86% de los casos se resuelven con la
pista 1 (carátula del siguiente)** — buscando atrás dentro del
bloque, exactamente la zona inflada por §3.6.a.

Si Etapa 3 corrigiera el bug `pg_fin + 1`, la pista 1 se
volvería redundante en los 4.843 casos que actualmente la usan
con búsqueda atrás (`fin_dentro_bloque`). El bloque vendría ya
recortado correctamente. La cascada quedaría como compensación
para los modos de falla restantes:

- (b) catálogo cortó corto → firma cae en página compartida
  (120 casos hoy en `fin_por_firma_actual`).
- Páginas compartidas con marcador del siguiente fuera del
  bloque (162 casos hoy en `fin_extendido_pag_compartida` con
  `caratula_siguiente`).

La cascada se reduciría de cuatro pistas usadas en producción a
una pista efectiva (`firma_actual`) más fallback adelante.

#### F4.9.b — `mitad_bloque` se calcula sobre el bloque inflado

Detallado en §4.5.d. Punto de fricción específico con §3.6.a:
el cálculo de `(lfc - li) // 2` opera sobre `lfc` heredado del
catálogo, no sobre `linea_fin_real`. Para fallos cortos con
inflado proporcionalmente grande, "la mitad" cae dentro del
fallo siguiente, sesgando la pista 2. Cuantificación específica
no hecha (la pista 2 se gatilla 527 veces, mayoritariamente en
tomos viejos donde los fallos son más cortos).

#### F4.9.c — Los 70 huérfanos requieren tratamiento distinto

Los 70 fallos con `status_localizacion not in ('ok',
'ok_cortado_en_indice')` se reparten:

- 43 `pagina_no_en_mapa`: **descartados silenciosamente** por
  `cargar_localizados`. No llegan al parser.
- 27 `fallo_cruza_archivos`: **llegan al parser** con `linea_fin`
  = última línea física del `.md`. Producen bloques gigantes
  (§4.6.g) y outliers de `word_count`.

La asimetría es relevante: corregir §3.6.c (los 43 sin
localización) tendría que hacerse en Etapa 1 o 3; corregir el
manejo de los 27 cruza_archivos podría hacerse en Etapa 3 (cortar
en el verdadero borde editorial, no al final del `.md`) o en el
parser (limitar el bloque inicial a un máximo razonable, ej.
`linea_inicio + 5000`).

#### F4.9.d — Inconsistencia 0/1 contenida fuera del parser

A diferencia del cruzador (Etapa 3), el parser **no consume
fuentes con indexación mixta**. Hereda 0-indexed de Etapa 3
(que a su vez heredó 0-indexed del mapa) y nunca toca
`secciones_indices.csv`. Por eso el bug §3.6.b no se propaga.

Esto es un dato favorable para la arquitectura: la elección de
hacer Etapa 3 como integrador y dejar al parser fuera del cruce
con secciones aislada el problema de indexación al cruzador. Si
en el futuro se reescribiera el parser para consumir
`secciones_indices.csv` directamente (por ejemplo, para acceder
a otras secciones del aparato editorial), habría que hacer la
conversión de índices explícita.

---

> **Fin de la sección 4.** Pendiente del documento global:
> sección de arquitectura cruzada (convenciones de indexación
> 0/1 a lo largo del pipeline, grafo de dependencias del parser,
> tabla de salud del corpus pre/post correcciones), incorporación
> de bugs F001–F011 reorganizados, actualización del diagrama
> global con `fallos_localizados_huerfanos.csv` y posibles otros
> outputs secundarios.
