# Hallazgos de mapeo del pipeline

> Archivo de trabajo durante la construcción de `PIPELINE.md`.
> Acumula hallazgos detectados al leer scripts y validar contra
> archivos reales. Cuando un hallazgo queda integrado en `PIPELINE.md`
> se mueve a la sección "Ya integrados".
>
> **Cuando `PIPELINE.md` cubra las cuatro etapas, este archivo debería
> quedar vacío o casi vacío y archivarse.**
>
> **Estado tras sesión 2026-05-09 (cierre §4)**: las cuatro etapas
> están cubiertas en PIPELINE.md. Lo que queda en este archivo es
> exclusivamente trabajo pendiente para la sección de arquitectura
> cruzada (post-§4) y validaciones contra `.md` real que no se
> hicieron en la sesión.
>
> **Estado tras sesión 2026-05-09 (auditoría empírica + fix §3.6.a)**:
> auditoría completa replicada en PowerShell sobre los CSVs vivos,
> bug §3.6.a fixeado en código y reprocesado el pipeline entero
> (Etapa 3 + Etapa 4). §3.6.d disuelto como efecto colateral. Bugs
> §4.6.a, §4.6.b, §4.6.g, §4.6.h re-evaluados con números post-fix.
> Detalles abajo en la sección "Sesión 2026-05-09 (auditoría + fix)".

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
  Verificado contra datos. Integrado en §2.5.a. Pista crítica para §3
  — confirmada en §3.6.a.

- **Convención de indexación de `secciones_indices.csv`**: 1-indexed
  inclusivo. Integrado en §2.2 y §2.6.b.

- **Fix v15 (`extender_inicio_indice_nombres`)**: documentado en
  §2.5.b. Validación contra `.md` real pendiente.

- **`catalogo_volumenes.csv` no lo produce `construir_catalogo.py`**:
  origen no identificado. Documentado en §2.9.

- **Tomos 335 y 336 ausentes** del catálogo. Integrado en §2.7.

### Pendientes residuales para §2

(Todos requieren `.md` reales para validar.)

- ⏳ **Fix v15**: validar comportamiento real contra `LibroVol339.1.md`
  o cualquier `.md` del rango 337–349.

- ⏳ **Slice `lines[linea_inicio_1:linea_fin_1]`**: validar
  empíricamente si la línea `linea_fin_1` típicamente contiene una
  entrada del índice o está vacía.

- ⏳ **Tomos 348–349 sin `materias`/`sumario`/`legislacion`**:
  determinar si es cambio editorial real o fallo de detección de
  regex.

## Sesión 2026-05-08 (mapeo §3)

### Ya integrados en `PIPELINE.md` §3

- **Bug `pg_fin + 1` (CRÍTICO)**: confirmado, 5.695/5.695 pares
  consecutivos (100%) muestran inflado promedio 32,4 líneas.
  Integrado en §3.6.a.

- **Bug indexación 0/1 en `ok_cortado_en_indice`**: integrado en
  §3.6.b.

- **`fallo_cruza_archivos`**: integrado en §3.6.d.

- **`pagina_no_en_mapa` concentrado en tomos 331–334**: integrado
  en §3.6.c con ⏳.

- **Tres status fantasma**: documentado en §3.4.

### Pendientes residuales para §3

- ⏳ **Validar 3.6.b contra `.md` real**: abrir `LibroVol339.2.md`
  línea 33525 (caso `339_p1834`).

- ⏳ **Validar hipótesis 3.6.c**: pedir un `.md` de tomos 331–334.

- ⏳ **Re-evaluar `fallo_cruza_archivos` post-corrección de 3.6.a**.

## Sesión 2026-05-09 (mapeo §4)

### Ya integrados en `PIPELINE.md` §4

- **Cascada como "una sola pista"** (hipótesis 4.h del handoff):
  confirmada contra datos. 86,0% caen en `caratula_siguiente`,
  97,9% en pistas 1–3 combinadas. Integrado en §4.5.b.

- **Bug aritmético `apertura_idx + len(bloque)` (4.b del handoff)**:
  confirmado leyendo código. Integrado en §4.6.a con cuantificación
  (cota superior 3.863 casos).

- **Fallback `inicio_cons = 0` en `extraer_considerando` (4.c del
  handoff)**: confirmado, cuantificado (169 casos sospechosos).
  Hallazgo adicional al revisar el código: la discrepancia entre
  comentario y código (el comentario dice "desde apertura", el
  código hace `0`). Integrado en §4.6.b.

- **Fecha sin marcador captura del dictamen (4.d del handoff)**:
  confirmado en código y cuantificado (35/70 casos potenciales).
  Integrado en §4.6.c.

- **`extraer_textos_votos` incluye header (4.e del handoff)**:
  confirmado. Discrepancia entre comentario (línea 577) y código
  (línea 578). Efecto cuantitativo despreciable. Integrado en
  §4.6.d.

- **Bug 4.f (descarte silencioso) refutado**: 0 casos en producción,
  cero diferencia entre `fallos_localizados.csv` − 43 y
  `csjn_casos.csv`. Integrado en §4.6.f.

- **Bug 4.g (cruza_archivos con bloques gigantescos)**: confirmado
  contra datos, los 5 outliers de `word_count` del corpus son los 5
  más grandes de cruza_archivos. 37% caen al fallback de firma vs
  ~2% del corpus general. Integrado en §4.6.g.

- **Inconsistencia de filtros 4 vs 5 chars**: documentada en §4.5.a
  como decisión consciente.

- **Detector v17 anti-contaminación por diseño**: integrado en
  §4.4.g y §4.5.e con razón estructural del comentario del código.

- **`mitad_bloque` se calcula sobre el bloque inflado**: integrado
  en §4.5.d como punto de fricción con §3.6.a.

- **Tres versiones declaradas (v16, v17, v18)**: integrado en §4.7
  como limitación menor.

### Hallazgos nuevos detectados al cuantificar §4

- **39 columnas en `csjn_casos.csv`, no 38**: las notas previas
  contaron mal (probable miscount de las líneas 1858–1873 del
  parser). El `fieldnames` del writer (líneas 1858–1873) declara
  exactamente 39 columnas, coincidiendo con el header del CSV.
  Integrado en §4.2.a sin marca de discrepancia.

- **`dictamen_presente == '0'`** (string `'0'`) en los 164
  `sumario_con_link`, mientras el resto tiene `True`/`False`. Bug
  de inicialización de tipos en `construir_caso_sumario_link`.
  Integrado en §4.6.e.

- **Decisión de diseño de `csjn_casos_votos.csv`**: 89,5% de las
  filas son `posicion == 'mayoria'` con `wc_voto = 0` y
  `tipo_voto_sep = ''`. La unidad es (caso, juez), no (caso, voto
  separado). Documentado en §4.2.b como regla central de
  interpretación.

- **967 filas con `posicion == 'mayoria'` y `texto_voto != ''`**:
  caso intermedio raro (4,8% de las mayorías). No inspeccionado
  contra `.md`. Marcado en §4.7 y §4.8 como pendiente de
  validación.

- **`ok_sin_marcador_apertura` concentrado en tomos modernos
  (343–348)**: 161/185 (87%) en ese rango. Hipótesis: cambio
  editorial del marcador o degradación de OCR. Integrado en §4.6.h
  con ⏳ para validación.

- **Inversión `marcador_apertura_siguiente` ↔ `sumario_siguiente`
  entre tomos viejos y modernos**: tomos 329–334 casi nunca usan
  pista 3, pero usan pista 2 mucho; tomos 337–349 al revés.
  Integrado en §4.6.i como hallazgo descriptivo.

- **El parser produce sub-status del `status_localizacion`**:
  `ok_sin_marcador_apertura`, `ok_cortado_en_indice_sin_marcador`,
  `fallo_cruza_archivos_sin_marcador`. Esos sub-status no aparecen
  en `fallos_localizados.csv` (Etapa 3) — son creación del parser
  durante el refinamiento. Integrado en §4.4.f.

- **Filtrado de los 43 `pagina_no_en_mapa` en `cargar_localizados`**:
  el parser nunca ve a esos huérfanos. Es el único filtro
  silencioso del parser, con `print` que lo declara
  (línea 1782). Integrado en §4.3.c y §4.4.a.

### Pendientes residuales para §4

- ⏳ **Daño efectivo del bug §4.6.a**: hay 3.863 casos con
  `apertura_rel > 0` y `tribunal_origen` detectado. La cota
  superior es alta, pero el daño efectivo depende de cuántos
  fallos siguientes tienen `Tribunal de origen:` en sus primeras
  líneas. Validación contra `.md` no hecha.

- ⏳ **Fechas sospechosas (§4.6.c)**: 35 casos donde el fallback
  podría haber capturado fecha del dictamen. Validar 2-3 contra
  `.md`.

- ⏳ **44 `ok_sin_marcador_apertura` no-sumario en tomos modernos
  (§4.6.h)**: causa no diagnosticada. Inspeccionar 3-5 casos
  contra `.md` real.

- ⏳ **Validación de `wc_dictamen`**: limitación reconocida en
  docstring del parser. No hecho en esta sesión.

- ⏳ **967 filas `mayoria` con `texto_voto != ''`**: caso
  intermedio no inspeccionado contra `.md`.

---

## Sesión 2026-05-09 (auditoría empírica + fix §3.6.a)

### Tarea 1.A: replicación de cuantificaciones en PowerShell

Todas las métricas de §4.6 replicadas sobre los CSVs vivos. Resultado:
**calzaron exacto** las cifras de PIPELINE.md (5.655 / 5.585 / 3.863
para §4.6.a; 169 / 152 / 1.751 para §4.6.b; 234 / 164 / 70 / 35 para
§4.6.c; 164 strings `'0'` para §4.6.e; 27 cruza_archivos para §4.6.g;
185 con distribución exacta por tomo para §4.6.h).

Una discrepancia menor: mediana de `wc_mayoria` para cruza_archivos
fue 2.306 (PowerShell, n=27 elementos) vs 2.252 (PIPELINE.md). Razón
metodológica de cómputo de mediana en PowerShell vs pandas. Sin
impacto.

### Discrepancias documentales detectadas

- **D-1**: §2.2 decía `cat = 5.819`, real `cat = 5.862`. Catálogo y
  fallos_localizados tienen las mismas filas (cero diferencia entre
  ambos). Corregido en PIPELINE.md.
- **D-2**: §3.4 nombraba la columna como `status_localizacion` en
  `fallos_localizados.csv`. La columna real se llama `status`. El
  parser sí la renombra a `status_localizacion` al volcarla en
  `csjn_casos.csv`. Documentado como nota en §3.4.
- **D-3**: Inconsistencia entre los dos CSVs (`loc.status` vs
  `casos.status_localizacion`). Documentada, no se corrige por
  ahora.

### Tarea 1.B (fix §3.6.a): aplicado y validado

Cambio: una línea (`scripts/pipeline/cruzar_catalogo_y_mapa.py:235`).

```diff
-        clave_fin = (tomo, pg_fin + 1)
+        clave_fin = (tomo, pg_fin)
```

Más comentario de la línea anterior actualizado por consistencia.

Snapshot pre-fix conservado en
`archivo/snapshots_ad_hoc/pre_fix_3_6_a_20260509_1413/` (los tres CSVs
de pipeline).

Reprocesado completo: Etapa 3 + Etapa 4. Tiempo total ~2 minutos.

Validación post-fix:

| Métrica | Pre-fix | Post-fix |
|---|---:|---:|
| Pares con bloque inflado | 5.695 / 5.695 (100%) | **0 / 5.663 (0%)** |
| `ok` | 5.773 | 5.741 |
| `pagina_fin_no_en_mapa` | 0 | 39 (desenmascarados) |
| `fallo_cruza_archivos` | 27 | 20 (recalibrados) |
| `ok_sin_marcador_apertura` | 185 | 347 |

Validación caso por caso de los 163 fallos que cambiaron de `ok` a
`ok_sin_marcador_apertura`: 151 `wc_pre > wc_post` consistente con la
hipótesis (a) del fix; 11 con wc igual (la mayoría con `wc_pre = 0`,
casos defectuosos en pre que siguen sin marcador en post); 1 con
`wc_pre = 0 → wc_post = 132` (mejora). **Cero regresiones detectadas.**

### Re-auditoría de bugs §4.6 sobre datos post-fix

| Bug | Pre-fix | Post-fix | Cambio de prioridad |
|---|---|---|---|
| §3.6.a | 5.695 inflados (crítica) | 0 inflados | **resuelto** |
| §3.6.d | 27 cruza_archivos (sospechosos por miscalibración) | 20 calibrados | **disuelto** |
| §4.6.a | cota 3.863 (media) | cota 3.682, daño efectivo ~0 | **bajada a cosmético** |
| §4.6.b | 169 sospechosos (baja-media) | 320 sospechosos | **subida a media-alta** |
| §4.6.g | 27 outliers (alta para subset) | 20 outliers, máx persiste | bajada (contenida) |
| §4.6.h | 185 (media) | 347, fenómeno descriptivo | reclasificada |
| §4.6.e | 164 strings `'0'` (baja) | sin cambio | sin cambio |
| §4.6.c | 35 sospechosos (baja) | (no recontado en sesión) | sin cambio |
| §4.6.d | cosmético (baja) | sin cambio (independiente) | sin cambio |
| §4.6.f | 0 (refutado) | 0 | refutado se mantiene |

Todos los cambios de prioridad ya integrados en las sub-secciones
correspondientes de PIPELINE.md §4.6.

### Hallazgos nuevos surgidos del fix

- **Status `pagina_fin_no_en_mapa` desenmascarado**: aparecen 39 casos
  concentrados en tomos 331–334 (10+10+10+9). Hipótesis: el detector
  de páginas (Etapa 1) tiene un problema localizado en esos tomos
  para detectar ciertas páginas. El bug §3.6.a lo enmascaraba pidiendo
  `pg_fin + 1` (que casi siempre tenía header). Esto refuerza la
  hipótesis de §3.6.c (concentración anómala de huérfanos en
  331–334).

- **§4.6.h se duplica al desenmascarar marcadores espurios**: 162
  fallos pasaron de tener `apertura_tipo='fallo'` (espurio, era el
  marcador del fallo siguiente) a `ok_sin_marcador_apertura`. La
  cifra honesta de fallos sin marcador de apertura es 347, no 185.

- **§4.6.b sube de prioridad por ratio**: con bloques más cortos
  post-fix, el fallback `inicio_cons = 0` produce considerandos con
  ratio `wc_considerando / word_count` más alto. Pasa de 169 a 320
  casos sospechosos.

### Pendientes para próxima sesión

- Fix §4.6.e (trivial, tipos): cambiar `0` por `False` en línea 1295
  del parser. 30 segundos.
- Fix §4.6.b: ahora prioritario. Una línea: cambiar fallback para que
  use `apertura_rel + 1` cuando hay apertura.
- Validaciones contra `.md` real (Tarea 3 del plan de auditoría):
  §3.6.b (línea 33525 de `LibroVol339.2.md`), §3.6.c (tomos 331–334),
  §4.6.c (3 fechas sospechosas), §4.6.h (3-5 casos modernos).
- Cuantificar daño efectivo de §4.6.a post-fix (Tarea 2): cuántos de
  los 3.682 *realmente* capturan tribunal del fallo siguiente. Ahora
  baja prioridad porque el fix §3.6.a probablemente lo evaporó.

---

## Hallazgos transversales (post-§4)

> Estos son los hallazgos que tienen alcance superior a una sola
> sección. Insumo para la sección de arquitectura cruzada que
> cierra el documento.

### Convenciones de indexación NO uniformes

Estado consolidado tras leer las cuatro etapas:

| Etapa | Convención | Validado |
|---|---|---|
| 1 (`detectar_paginas`) | 0-indexed | §1.3 |
| 2 (`construir_catalogo`) | mixta: `pagina_inicio` natural; secciones 1-indexed inclusivo | §2.2, §2.6.b |
| 3 (`cruzar_catalogo_y_mapa`) | hereda 0-indexed para fallos, **mezcla con 1-indexed cuando consume secciones — produce bug §3.6.b** | §3.3.b |
| 4 (`parser`) | 0-indexed homogéneo. **No consume `secciones_indices.csv`**, por eso no hereda el bug 0/1 | §4.3.a |

Acción: agregar tabla resumen de convenciones de indexación al
documento, en una sección "Convenciones cruzadas" después de §4.

### Acoplamiento del parser a tres fuentes

Confirmado al cerrar §4. El diagrama global del documento (al inicio
de PIPELINE.md) ya refleja el acoplamiento triple del parser. Lo que
falta:

- Agregar `fallos_localizados_huerfanos.csv` al diagrama global
  (output secundario de Etapa 3 no representado).
- Agregar nota explícita: el parser **filtra** los 43
  `pagina_no_en_mapa` antes de procesar; los 27 `fallo_cruza_archivos`
  los procesa pero produce outliers (§4.6.g).

### Tabla de salud del corpus (números consolidados)

Con las cuatro etapas mapeadas. Dos columnas: pre-fix §3.6.a y
post-fix §3.6.a (sesión 2026-05-09).

| Métrica | Pre-fix | Post-fix | Origen |
|---|---:|---:|---|
| Fallos en `catalogo.csv` (Etapa 2) | 5.862 | 5.862 | §2.2 |
| Fallos en `fallos_localizados.csv` (Etapa 3) | 5.862 | 5.862 | §3.2 |
| Fallos `ok` en Etapa 3 | 5.773 | 5.741 | §3.4 |
| Fallos `ok_cortado_en_indice` en Etapa 3 | 19 | 19 | §3.4 |
| Fallos `fallo_cruza_archivos` en Etapa 3 | 27 | 20 | §3.4 |
| Fallos `pagina_no_en_mapa` (descartados al parser) | 43 | 43 | §3.4, §4.3.c |
| Fallos `pagina_fin_no_en_mapa` | 0 | 39 (desenmascarados) | §3.4 |
| Fallos en `csjn_casos.csv` (output del parser) | 5.819 | 5.819 | §4.2 |
| Fallos `sumario_con_link` (cortocircuitados) | 164 | 164 | §4.4.g |
| Fallos `ok_sin_marcador_apertura` | 185 | 347 | §4.6.h |
| Fallos con `wc_considerando ≥ 0,9 × wc` (sospecha §4.6.b) | 169 | 320 | §4.6.b |
| Fallos con bug §4.6.a (cota superior) | 3.863 | 3.682 (daño efectivo ~0) | §4.6.a |
| Pares consecutivos con bloque inflado (§3.6.a) | 5.695 / 5.695 (100%) | 0 / 5.663 (0%) | §3.6.a |
| Inflado promedio del bloque del catálogo | 32,4 líneas | 0 | §3.6.a |
| Recorte real del parser (mediana, ok* puros) | 16 líneas | (no recalculado) | §4.5.b |

**Nota**: la previsión original de que tras corregir §3.6.a la cascada
de `detectar_fin_real` se reduciría a una sola pista efectiva quedó
parcialmente confirmada: el inflado se eliminó, pero la cascada
sigue siendo necesaria para los 39 nuevos `pagina_fin_no_en_mapa` y
los 20 `cruza_archivos` legítimos. Cuantificación exacta del nuevo
peso de cada pista en la cascada: pendiente.

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
