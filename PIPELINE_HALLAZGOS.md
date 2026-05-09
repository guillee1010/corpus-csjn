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

- **Convención de naming inconsistente**: `LibroVol339.2.md` (con punto)
  vs `LibroVol340_2.md` (con guión bajo). El detector tolera ambas via
  `RE_FILENAME_TOMO`. Integrado en §1.9.

### Pendientes para §2 (`construir_catalogo.py`)

- **Contradicción docstring/código en `pagina_fin`**:
  - Docstring (líneas 56–57): `pagina_fin = pagina_inicio_siguiente - 1`.
  - Código (líneas 408–412): `pagina_fin = pagina_inicio_siguiente`.
  - Cruzador río abajo (línea 235): busca `pg_fin + 1` como header
    del siguiente, lo cual es coherente con el código (no con docstring).
  - **Conclusión preliminar**: código bien, docstring desactualizado.
  - **Qué hacer**: documentar en §2 como nota interna (no como PF, porque
    no afecta comportamiento). Sugerir corrección del docstring del
    script en sesión futura.

### Pendientes para §3 (`cruzar_catalogo_y_mapa.py`)

- **Posible mezcla de indexaciones 0/1 en `ok_cortado_en_indice`**:
  - `detectar_paginas.py` produce `linea_header` 0-indexed.
  - `construir_catalogo.py` produce secciones de índice 1-indexed
    (línea 195 explícita: `linea_inicio_0 + 1`).
  - `cruzar_catalogo_y_mapa.py` línea 222:
    `linea_fin = indices_nombres_por_archivo[archivo_ini] - 1`.
    Mezcla los dos sistemas: si el valor es 1-indexed y se le resta 1,
    queda 0-indexed apuntando AL header del índice, no a la línea
    anterior al header.
  - **Hipótesis**: esto puede ser el origen de los 19 casos
    `ok_cortado_en_indice` pendientes de validar en BITACORA.
  - **Qué hacer**: validar empíricamente en §3 con un caso concreto
    (tomar un archivo, ver `linea_inicio_indice` real en
    `secciones_indices.csv`, ver `linea_fin` resultante en
    `fallos_localizados.csv`, comparar contra el `.md` para ver si la
    línea efectivamente queda donde debería).

- **`fallo_cruza_archivos`**: status declarado en docstring del
  cruzador, pero no validado cuántos casos lo gatillan ni si el
  comportamiento (linea_fin = última línea del archivo de inicio) es
  el correcto editorial. Validar en §3.

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

- **`detectar_fin_real` con búsqueda bidireccional**: clave para
  entender por qué el detector `borde_inferior` ve solapamientos.
  La cascada de pistas (carátula del siguiente → sumario nuevo →
  marcador de apertura → firma actual) es la compensación del
  parser para PF-1.a. Documentar en §4 con ejemplo trazado contra
  caso real.

- **`extender_inicio_indice_nombres` (Fix v15)** en
  `construir_catalogo.py`: aplica solo a tomos modernos donde el
  reflow PDF→MD ubicó la portadilla del índice DESPUÉS de las primeras
  entradas. Ya leído en código pero NO validado contra archivo real.
  Pendiente para §2 si se consigue un `.md` del rango 337-349.

### Hallazgos transversales (afectan a todo el doc)

- **Convenciones de indexación NO uniformes en el pipeline**:
  - Etapa 1 produce 0-indexed.
  - Etapa 2 produce mezcla: `pagina_inicio` natural; secciones
    `linea_inicio`/`linea_fin` 1-indexed.
  - Etapa 3 hereda lo de Etapa 1 (0-indexed) para `linea_inicio` y
    `linea_fin` de fallos, y mezcla con 1-indexed cuando consume
    secciones (potencial bug de §3).
  - Etapa 4 asume 0-indexed (comentario línea 1022 del parser).
  - **Qué hacer**: agregar tabla resumen de convenciones de indexación
    al documento (probablemente en una sección de "Convenciones
    cruzadas" al final, después de §4).

- **Acoplamiento del parser a tres fuentes**: confirmar que el grafo
  de dependencias del diagrama global (Claude lo dibujó al inicio de
  §1) sigue siendo correcto después de leer las §2-§4 con detalle.

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
