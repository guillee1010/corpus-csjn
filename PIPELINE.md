# Pipeline corpus-csjn

> **Estado del documento**: borrador en construcción (sesión 2026-05-11,
> continuada el 2026-05-08).
> Cubre: diagrama global + Etapa 1 + Etapa 2.
> Pendiente: Etapa 3 (`cruzar_catalogo_y_mapa.py`), Etapa 4 (`parser.py`),
> bugs F001–F011 reorganizados, contradicciones cruzadas consolidadas,
> sección de arquitectura (por qué cuatro scripts y no uno).

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

Estructura de `catalogo.csv` (5.819 filas con datos actuales):

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

**Verificado contra datos**: en `catalogo.csv` (5.819 filas), las 5.800
entradas con `pagina_fin` no vacío cumplen exactamente
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

El docstring (líneas 30–38) los enumera. Se observan así en los datos
actuales:

| Status | n | % | Significado |
|---|---:|---:|---|
| `ok` | 5.773 | 98,48% | Cruce limpio (con caveat — ver §3.6.a) |
| `pagina_no_en_mapa` | 43 | 0,73% | `pagina_inicio` del catálogo no aparece como header en el mapa |
| `fallo_cruza_archivos` | 27 | 0,46% | El "siguiente fallo" arranca en otro `.md` del mismo tomo |
| `ok_cortado_en_indice` | 19 | 0,32% | Último fallo del tomo, cortado antes del aparato editorial de índices |
| `ultimo_del_tomo` | 0 | 0% | Último fallo del tomo, fallback sin secciones de índice |
| `ultimo_del_tomo_sin_fin` | 0 | 0% | Último fallo del tomo, sin acceso al corpus |
| `pagina_fin_no_en_mapa` | 0 | 0% | `pagina_fin + 1` no aparece como header en el mapa |

**Total: 5.862 filas. 98,80% (5.792) en estados "limpios" (`ok` +
`ok_cortado_en_indice`); 1,20% (70) huérfanos.**

Los tres status con cero observaciones son fallbacks que el código
contempla pero que no se gatillan en producción con todos los inputs
opcionales provistos:

- `ultimo_del_tomo` y `ultimo_del_tomo_sin_fin` solo aparecerían si no
  se pasara `secciones_indices.csv` o si éste no incluyera el archivo
  del último fallo del tomo. Como el archivo se pasa y los 19 últimos
  del tomo tienen su `secciones_indices` correspondiente, todos caen
  en `ok_cortado_en_indice`.
- `pagina_fin_no_en_mapa` requeriría que `(tomo, pg_fin + 1)` no
  estuviera en el mapa. Esto efectivamente pasaría en una sola
  configuración: cuando el bug `pg_fin + 1` (§3.6.a) busca una página
  que no existe físicamente en el libro. En la práctica, como el
  detector de páginas registra **todas** las páginas (no sólo las de
  inicio de fallo), `pg_fin + 1` casi siempre tiene un header
  detectado. Por eso este status nunca se activa.

### 3.5 Cómo se calcula `linea_fin` por status

#### 3.5.a — `ok` y `fallo_cruza_archivos`

Lógica del código (líneas 234–249):

```python
clave_fin = (tomo, pg_fin + 1)
if clave_fin in mapa_pagina:
    archivo_fin, linea_fin_header = mapa_pagina[clave_fin]
    if archivo_fin == archivo_ini:
        out['linea_fin'] = linea_fin_header - 1   # status 'ok'
    else:
        out['linea_fin'] = n_lineas[archivo_ini] - 1   # status 'fallo_cruza_archivos'
```

El cursor de búsqueda del cruce es `pg_fin + 1`, no `pg_fin`. Tal como
quedó documentado en F2.6.a, esto es incompatible con la convención
real del catálogo. El bug se trata en §3.6.a.

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

> **Fin de la sección 3.** Pendiente: §4 (parser), sección de
> arquitectura cruzada (convenciones de indexación 0/1 a lo largo del
> pipeline, grafo de dependencias del parser), incorporación de
> bugs F001–F011 reorganizados.
