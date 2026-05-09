# Hallazgos de mapeo del pipeline

> Archivo de trabajo durante la construcción de `PIPELINE.md`.
> Acumula hallazgos detectados al leer scripts y validar contra
> archivos reales. Cuando un hallazgo queda integrado en `PIPELINE.md`
> se mueve a la sección "Ya integrados".
>
> **Cuando `PIPELINE.md` cubra las cuatro etapas, este archivo debería
> quedar vacío o casi vacío y archivarse.**

---

## Sesión 2026-05-11 (mapeo §1)

### Ya integrados en `PIPELINE.md` §1

- **PF-1.a**: `linea_inicio` apunta al header tipográfico de página
  (línea donde aparece el número del tomo aislado), no a la carátula
  del fallo. Confirmado contra `LibroVol339.2.md` línea 26.346 (caso
  339_p1644). Integrado en §1.10.a.

- **PF-1.b**: las dos líneas acompañantes del header tipográfico
  (`951`, `DE JUSTICIA DE LA NACIÓN` o `FALLOS DE LA CORTE SUPREMA`)
  no se filtran del cuerpo. ~1.600 tokens de ruido por libro grande.
  Integrado en §1.10.b.

- **PF-1.c**: mismo `(tomo, pagina)` puede aparecer en dos `.md` del
  mismo tomo. El cruzador (Etapa 3) resuelve quedándose con la línea
  más baja. Integrado en §1.10.c.

- **Hallazgo tipográfico**: tres patrones de orden interno del header
  de página (`pagina/editorial/tomo`, `tomo/pagina/editorial`, etc.).
  Razón empírica de la ventana `(-3, +2)` del detector. Integrado
  en §1.4.

- **Convención de naming inconsistente**: actualizada en §2 — son
  **tres** convenciones (punto, guión bajo, guión medio), no dos.
  El detector tolera todas via `RE_FILENAME_TOMO`. Integrado en §1.9
  y revisado en §2.7.

## Sesión 2026-05-08 (mapeo §2)

### Ya integrados en `PIPELINE.md` §2

- **Discordancia docstring/código en `pagina_fin`**: docstring línea 57
  dice "siguiente - 1", código línea 410 hace "siguiente" (sin restar).
  Verificado contra datos: 5.800/5.800 filas con `pagina_fin` no vacío
  cumplen `pagina_fin == pagina_inicio_siguiente`. Integrado en §2.5.a
  con marca de discordancia. Pista crítica para §3 — confirmada en §3.6.a.

- **Convención de indexación de `secciones_indices.csv`**: 1-indexed
  inclusivo, confirmado contra código (línea 195) y datos.
  Integrado en §2.2 y §2.6.b.

- **Fix v15 (`extender_inicio_indice_nombres`)**: leído en código,
  documentado en §2.5.b. **Validación contra `.md` real pendiente.**

- **`catalogo_volumenes.csv` no lo produce `construir_catalogo.py`**:
  origen no identificado. Documentado en §2.9 con hipótesis a verificar
  cuando se incorporen otros scripts. Hallazgos exploratorios sobre el
  archivo asentados allí.

- **Tomos 335 y 336 ausentes** del catálogo, coherente con Etapa 1.
  Confirmado contra datos: 19 tomos presentes en `catalogo.csv`.
  Integrado en §2.7.

### Pendientes residuales para §2 (`construir_catalogo.py`)

(Todos requieren `.md` reales para validar.)

- ⏳ **Fix v15**: validar comportamiento real contra `LibroVol339.1.md`
  o cualquier `.md` del rango 337–349. Verificar que el fix se dispara
  y captura las entradas pre-portadilla. Quedó marcado en §2.5.b y §2.8.

- ⏳ **Slice `lines[linea_inicio_1:linea_fin_1]`**: con valores
  1-indexed inclusivos, el slice de Python excluye la línea
  `linea_fin_1` del bloque parseado. Validar empíricamente si esa línea
  típicamente contiene una entrada del índice o está vacía. Si está
  vacía sistemáticamente, es intencional. Si tiene contenido, es bug
  menor. Quedó marcado en §2.6.c y §2.8.

- ⏳ **Tomos 348–349 sin `materias`/`sumario`/`legislacion`**:
  determinar si es cambio editorial real o fallo de detección de
  regex. Requiere mirar el final de `LibroVol348-1.md` y
  `LibroVol349-1.md`.

## Sesión 2026-05-08 (mapeo §3)

### Ya integrados en `PIPELINE.md` §3

- **Bug `pg_fin + 1` (CRÍTICO)**: hipótesis original confirmada, pero
  con consecuencia distinta a la prevista. Lo previsto: gatillaría
  `pagina_fin_no_en_mapa`. La realidad: cero casos en ese status; en
  cambio, el detector de páginas registra **todas** las páginas (no
  sólo inicios de fallo), entonces `pg_fin + 1` casi siempre tiene
  header detectado. Esto produce 5.773 `ok` con bloques sistemáticamente
  inflados ~32 líneas (el cuerpo de la primera página del fallo
  siguiente queda mal atribuido al fallo actual). Validado contra datos:
  5.695/5.695 pares consecutivos (100%) muestran inflado, promedio
  32,4 líneas, distribución concentrada en 21–40 líneas (= una página
  del corpus). Integrado en §3.6.a.

- **Bug indexación 0/1 en `ok_cortado_en_indice`**: hipótesis confirmada
  al leer línea 222 del cruzador. Resta `1` a un valor 1-indexed sin
  convertir a 0-indexed. Resultado: `linea_fin` apunta exactamente al
  header del índice de nombres, no a la línea anterior. Afecta los 19
  últimos del tomo. Severidad baja (una línea de ruido tipográfico, no
  página entera). Integrado en §3.6.b.

- **`fallo_cruza_archivos`**: validado contra
  `fallos_localizados_huerfanos.csv` — 27 casos, todos en bordes
  editoriales entre `.md`s del mismo tomo. Definición operacional
  ambigua post-corrección de `pg_fin+1`. Integrado en §3.6.d.

- **Solapamientos página-archivo**: ya documentados en §2.9
  (`catalogo_volumenes.csv`). El cruzador los resuelve con "línea más
  baja gana" (línea 100). Integrado implícitamente en §3.5.d.

### Hallazgos nuevos no anticipados detectados al mapear §3

- **`pagina_no_en_mapa` concentrado en tomos 331–334**: 43/43 casos
  exclusivamente en cuatro tomos consecutivos, mayoría en primeras
  páginas de cada `.md` físico. No estaba previsto en HALLAZGOS.
  Hipótesis: particularidad editorial de esos tomos o limitación del
  detector en bordes iniciales de archivo. Integrado en §3.6.c con ⏳.

- **Tres status fantasma** (`ultimo_del_tomo`, `ultimo_del_tomo_sin_fin`,
  `pagina_fin_no_en_mapa`): contemplados en código pero con cero
  observaciones cuando todos los inputs opcionales están provistos.
  El primero y el segundo son fallbacks para cuando falta
  `secciones_indices.csv`. El tercero es el fallback que "debería"
  capturar el bug `pg_fin+1` pero no lo hace por la razón explicada
  arriba. Documentado en §3.4.

- **Existencia de `fallos_localizados_huerfanos.csv` como output
  secundario**: no estaba en el diagrama global del documento. El
  diagrama hay que actualizarlo cuando se cierre el doc.

### Pendientes residuales para §3

- ⏳ **Validar 3.6.b contra `.md` real**: abrir `LibroVol339.2.md`
  línea 33525 (caso `339_p1834`) — verificar si esa línea es el
  header `INDICE POR LOS NOMBRES DE LAS PARTES` (bug confirmado) o la
  línea anterior (no hay bug, el ajuste compensa). Cualquiera de los
  19 `.md` afectados sirve.

- ⏳ **Validar hipótesis 3.6.c**: pedir un `.md` de tomos 331–334
  (ej. `LibroVol331.1.md`) e inspeccionar las primeras ~100 líneas:
  ¿hay header tipográfico para la página 7? ¿está la marca del tomo
  aislada? Cruzar con `mapa_paginas.csv` para tomos 331-334 y comparar
  con tomo 329 (sin casos) para identificar la diferencia.

- ⏳ **Re-evaluar `fallo_cruza_archivos` post-corrección de 3.6.a**:
  ver si los 27 casos siguen siendo los mismos o si la definición
  cambia significativamente cuando el cursor de búsqueda apunte al
  lugar correcto.

### Pendientes para §4 (`parser.py`)

- **Filtro `>= 5` chars en `primer_token_siguiente`**: tanto
  `detectar_fin_real` (línea 1190 del parser) como el detector
  `borde_inferior` del auditor aplican este filtro. Si la carátula del
  fallo siguiente arranca con un apellido de ≤4 chars (ej. "DIEZ" en
  el caso 339_p1651 ya identificado), nunca se usa como pista. Cae al
  fallback de firma o sumario.
  - **Qué hacer**: documentar como PF-4.x. Aclarar que es decisión
    consciente (consistencia parser+auditor), no bug. Revisar si el
    umbral 5 es óptimo o si bajar a 4 ayudaría sin generar falsos
    positivos.

- **Mezcla de fuentes en parser**: el parser consume tres fuentes
  simultáneas (`fallos_localizados.csv`, `mapa_paginas.csv`, `.md`
  del corpus). No es una cadena lineal. Documentar el grafo de
  dependencias en §4.

- **`detectar_fin_real` con búsqueda bidireccional como compensación
  de §3.6.a (NUEVO ÉNFASIS)**: confirmado al validar §3 — el bloque
  que recibe el parser está sistemáticamente inflado ~32 líneas. La
  cascada de pistas (carátula del siguiente → sumario nuevo → marcador
  de apertura → firma actual) es la compensación específica de Etapa
  4 para el bug 3.6.a. Hipótesis fuerte: corregir 3.6.a permitiría
  simplificar drásticamente la cascada. Documentar en §4 con ejemplo
  trazado contra caso real.

- **Los 70 huérfanos requieren tratamiento especial**: 43
  `pagina_no_en_mapa` (sin archivo/línea) + 27 `fallo_cruza_archivos`
  (con `linea_fin` = última línea del `.md` de inicio). Documentar en
  §4 cómo el parser decide qué hacer con cada uno.

### Hallazgos transversales (afectan a todo el doc)

- **Convenciones de indexación NO uniformes en el pipeline**
  (estado tras §3):
  - Etapa 1 produce 0-indexed.
  - Etapa 2 produce mezcla: `pagina_inicio` natural; secciones
    `linea_inicio`/`linea_fin` 1-indexed.
  - Etapa 3 hereda 0-indexed de Etapa 1 para `linea_inicio` y
    `linea_fin` de fallos, **y mezcla con 1-indexed cuando consume
    secciones — esto produjo el bug 3.6.b** (confirmado).
  - Etapa 4 asume 0-indexed (comentario línea 1022 del parser).
  - **Qué hacer**: agregar tabla resumen de convenciones de indexación
    al documento, en una sección "Convenciones cruzadas" después de §4.

- **Acoplamiento del parser a tres fuentes**: confirmar que el grafo
  de dependencias del diagrama global (Claude lo dibujó al inicio de
  §1) sigue siendo correcto después de leer §4 con detalle. Pendiente:
  agregar `fallos_localizados_huerfanos.csv` al diagrama si corresponde.

- **Sección de impacto cuantitativo de bugs**: con §3 cerrada hay
  números concretos del impacto:
  - Bug 3.6.a: 5.773 fallos (98,5% del corpus) con bloque inflado
    ~32 líneas.
  - Bug 3.6.b: 19 fallos con `linea_fin` corrida en uno.
  - 70 huérfanos sin localización limpia (1,2% del corpus).

  Considerar una tabla de "salud del corpus" después de §4 que
  consolide estos números antes/después de las correcciones
  propuestas.

---

## Convenciones de uso de este archivo

1. **Hallazgo nuevo detectado** → entra acá en la sección
   "Pendientes para §X" correspondiente, con la estructura:
   - Qué se observa (hechos verificables)
   - Hipótesis (si hay)
   - Qué hacer (acción concreta o decisión a tomar)
2. **Hallazgo se integra a PIPELINE.md** → se mueve a "Ya integrados"
   con referencia a la sección donde quedó.
3. **Hallazgo se descarta** → se mueve a "Descartados" con razón breve.
4. **No mantener este archivo cuando PIPELINE.md esté cerrado**:
   archivar o borrar.
