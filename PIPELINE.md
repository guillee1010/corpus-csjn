# Pipeline corpus-csjn

> **Estado del documento**: borrador en construcción (sesión 2026-05-11).
> Cubre: diagrama global + Etapa 1.
> Pendiente: Etapa 2 (`construir_catalogo.py`), Etapa 3
> (`cruzar_catalogo_y_mapa.py`), Etapa 4 (`parser.py`), bugs F001–F011
> reorganizados, contradicciones cruzadas consolidadas.

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

> **Fin de la sección 1.** Pendiente: §2 (catalogo), §3 (cruce — el
> crítico), §4 (parser).
