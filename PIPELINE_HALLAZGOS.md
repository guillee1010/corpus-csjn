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
> **Estado tras sesión 2026-05-09 (cierre §3.6.e Fase 1)**: aplicado
> fix estructural en cruzador para los 39 casos
> `pagina_fin_no_en_mapa` por hojas complementarias. 32 reasignados
> a `ok_pg_fin_redirigida`, 7 a `ok_cortado_en_indice`. Cero
> regresiones. Cobertura efectiva: 5799/5862 = 98,9% (+0,7 sobre
> sesión anterior). Detalles abajo. Hallazgos nuevos detectados
> durante la validación: §3.6.e Fase 2 (43 `pagina_no_en_mapa`
> simétricos), headers de meses como ruptores, hojas complementarias
> no flagueadas, `detectar_fin_real` traspasando `linea_fin` en
> `ok_cortado_en_indice` (≤13 líneas).
>
> **Estado tras sesión 2026-05-09 (auditoría empírica + fix §3.6.a +
> fix RE_APERTURA + hallazgo hojas complementarias)**: auditoría
> completa replicada en PowerShell sobre los CSVs vivos. Dos fixes
> aplicados al pipeline (cruzador L235 y parser L57). §3.6.d disuelto
> como efecto colateral de §3.6.a. Bugs §4.6.a, §4.6.b, §4.6.g,
> §4.6.h re-evaluados con números post-fix. Hallazgo nuevo §3.6.e
> (hojas complementarias en tomos 331-334). Detalles abajo.

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

### Tarea complementaria (cerrada en la misma sesión): fix RE_APERTURA strict

Tras el fix de §3.6.a, se identificó otro problema relacionado en el
parser. El detector del marcador `FALLO DE LA CORTE SUPREMA`
(`RE_APERTURA`, línea 57) era estricto a espaciado literal. Búsqueda
contra el corpus reveló 18 ocurrencias del marcador con doble espacio
entre `CORTE` y `SUPREMA`, todas concentradas en `LibroVol343-1.md`.

Fix aplicado: cambio de regex literal a `\s+` libre, alineado con el
patrón de las regex hermanas `RE_FECHA_LINEA` y `RE_FECHA_EXTRACT`
(líneas 58-59). Agregado `re.I` por consistencia.

```diff
-RE_APERTURA      = re.compile(r"^(FALLO|SENTENCIA) DE LA CORTE SUPREMA\s*$")
+RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I)
```

Validación post-fix:

| Status | Pre | Post | Δ |
|---|---:|---:|---:|
| `ok` | 5.394 | 5.410 | +16 |
| `ok_sin_marcador_apertura` | 347 | 331 | −16 |
| `fallo_cruza_archivos_sin_marcador` | 1 | 0 | −1 |
| `fallo_cruza_archivos` | 19 | 20 | +1 |

17 de 18 casos capturados (94%). Cero regresiones. El caso 18
(`343_p646`, línea 24641 de `LibroVol343-1.md`) no fue capturado por
una razón distinta: la cascada `detectar_fin_real` cortó el bloque del
fallo en línea 24618 (antes del marcador en 24641). Inspección del
`.md` reveló estructura editorial irregular en este fallo (carátula
en mayúsculas, sumario editorial antes del marcador, header de página
intermedio entre el sumario y el marcador). Documentado en
PIPELINE.md §4.6.j como caso testigo del patrón.

### Hallazgo nuevo: hojas complementarias en tomos 331-334 (§3.6.e)

Los 39 casos `pagina_fin_no_en_mapa` que aparecieron tras el fix de
§3.6.a NO son bug del pipeline. Investigación caso por caso reveló
que son artefactos editoriales del corpus.

Caso testigo: `331_p373` (Pizarro c/ Orígenes A.F.J.P.). Ocupa páginas
372-377. El catálogo registra `pagina_fin = 379` porque ese es el
inicio del fallo siguiente (`331_p379`, Villarreal). Pero las
páginas 378-379 no existen físicamente: tras la 377 hay una `HOJA
COMPLEMENTARIA` y la 380 arranca directamente con la sección de
marzo. Comprobación contra el `.md` confirma el salto: el header de
página 377 está en línea 14080, y el siguiente header (página 380)
está en 14129.

Los tomos 331-334 contienen 95 hojas complementarias en total
(distribuidas en 11 `.md`):

| Archivo | Hojas |
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

De las 95, solo 39 caen exactamente en una `pagina_fin` esperada por
el catálogo (las otras 56 caen en lugares intra-fallo o post-último
fallo del tomo donde no afectan al cruzador).

**Pre-fix §3.6.a, el bug `pg_fin + 1` "compensaba" el problema
editorial por accidente** (buscaba página 380, que sí existe →
bloque "ok" pero inflado). **Post-fix, el cruzador busca página 379,
no la encuentra, y cae al fallback "última línea del archivo"** →
bloque gigantesco. Para `331_p373`: word_count pasó de 449 a 293.804
palabras.

89 casos en total tienen este patrón (los 39 `pagina_fin_no_en_mapa`
+ 50 fallos intermedios cuyo bloque se extiende hasta el final del
archivo en algunos casos donde el siguiente fallo cae en
`pagina_fin_no_en_mapa`).

Mitigación temporal: filtrar `status_localizacion ==
'pagina_fin_no_en_mapa'` en análisis estadístico (igual que
`fallo_cruza_archivos`). Cobertura efectiva: 99,0% (5760/5819).

Fix estructural propuesto (próxima sesión): en
`cruzar_catalogo_y_mapa.py`, cuando `pg_fin` no esté en el mapa,
usar la `linea_inicio` del fallo siguiente del catálogo (si está
localizado) y restarle 1, en lugar del fallback "última línea del
archivo". Documentado en PIPELINE.md §3.6.e.

---

## Sesión 2026-05-09 (cierre §3.6.e Fase 1)

### Resuelto

- **§3.6.e Fase 1** (cruzador, fallback `pagina_fin_no_en_mapa`).
  Aplicado fix estructural sobre `cruzar_catalogo_y_mapa.py`. La
  Opción B propuesta originalmente (usar `linea_inicio` del fallo
  siguiente) resultó inviable: en los 39 casos el fallo siguiente
  está en estado especular `pagina_no_en_mapa` con `linea_inicio`
  vacío. Se aplicó **Opción A** (próxima página existente en el
  mismo archivo) en cascada con `ok_cortado_en_indice` y
  `ultimo_del_tomo` para los 7 casos sin próxima página.

  **Resultado**:

  | Status | Pre-fix | Post-fix |
  |---|---:|---:|
  | `pagina_fin_no_en_mapa` | 39 | 0 |
  | `ok_pg_fin_redirigida` (nuevo) | — | 32 |
  | `ok_cortado_en_indice` | 19 | 26 (+7) |

  **Caso testigo `331_p373` (Pizarro)**: word_count pasó de 293.804
  a 449 (igual al pre-§3.6.a). `pista_fin = caratula_siguiente`,
  `linea_fin = 14128`. Distribución de los 32 redirigidos: 30 con
  `pista_fin = sumario_siguiente`, 2 con `caratula_siguiente`, 0 con
  `fallback_catalogo`. Ningún caso patológico observado.

  Cero efectos colaterales sobre los 5780 casos no afectados (ok,
  fallo_cruza_archivos, pagina_no_en_mapa sin cambio). Detalles
  completos en PIPELINE.md §3.6.e.

### Hallazgos nuevos detectados durante la validación

Anotados para sesiones futuras, sin acción inmediata.

- **§3.6.e Fase 2 (43 `pagina_no_en_mapa`)**. Fenómeno especular al
  resuelto en Fase 1: la `pagina_inicio` declarada por el catálogo no
  existe físicamente porque hay una hoja complementaria
  inmediatamente antes. La lógica simétrica al fix Fase 1 sería:
  cuando `(tomo, pagina_inicio)` no está en el mapa, inferir
  `archivo` desde el fallo anterior del catálogo y usar la próxima
  página existente como `linea_inicio` real. Más invasiva que Fase 1
  porque requiere acceso al fallo anterior y traer su `archivo`.
  Recuperaría los 43 fallos descartados hoy por el parser.

- **Headers de meses como ruptores estructurales**. Entre fallos
  aparecen `MARZO`, `ABRIL`, etc. como separadores editoriales del
  índice del libro. Hipótesis: estos tokens podrían interferir con
  `detectar_caratula` cuando el detector busca el nombre del caso
  inmediatamente después de `FALLO DE LA CORTE SUPREMA` o
  `FALLOS DE LA CORTE SUPREMA`. Causa potencial de algunas rupturas
  pre-§3.6.a. Revisar en próxima sesión: ¿el detector de carátula
  filtra explícitamente estos tokens? ¿Cuántos casos podrían estar
  afectados?

- **Hojas complementarias no flagueadas explícitamente**. Aunque
  identificamos `HOJA COMPLEMENTARIA` como problema editorial y
  desarrollamos el fix Fase 1 alrededor del fenómeno, el pipeline no
  produce un flag explícito que indique "este fallo tiene una hoja
  complementaria entre su fin y el inicio del siguiente". Sería útil
  para auditoría tener un campo derivado o un CSV separado que
  liste los 95 casos. Implementación posible: detector en Etapa 1 o
  2 que cuente ocurrencias de `HOJA COMPLEMENTARIA` por archivo y
  asocie cada una a la página donde aparece.

- **`construir_catalogo` saltea las hojas complementarias**. Es
  probablemente la razón última por la que `pg_fin = 379` queda en
  el catálogo cuando físicamente la 379 no existe: el detector de
  páginas (Etapa 1) no asigna número de página a las hojas
  complementarias, y por eso quedan registros `(tomo, pagina)`
  faltantes en el mapa pero presentes en el índice editorial.
  Verificar comportamiento exacto en próxima sesión.

- **`detectar_fin_real` puede traspasar `linea_fin` en
  `ok_cortado_en_indice`**. Observado en `333_p1869`
  (`linea_fin_real = 43590` vs `linea_fin = 43589`) y `334_p698`
  (`linea_fin_real = 27875` vs `linea_fin = 27862`). El contenido
  excedido es el inicio del aparato de índices del tomo (no contenido
  de otro fallo). Comportamiento preexistente del detector
  (independiente del fix §3.6.e). Impacto acotado, ≤13 líneas
  observadas. Auditoría futura: verificar si pasa también en los 19
  `ok_cortado_en_indice` originales y cuantificar el contenido
  espurio capturado.

### Pendientes para próxima sesión

Por orden de prioridad estimada:

1. **Fix §4.6.b** (parser, fallback `inicio_cons = 0`). Subió de
   prioridad tras fix §3.6.a (de 169 a 320 casos sospechosos). Una
   línea de cambio.
2. **Fix §4.6.e** (parser, `dictamen_presente` como string). Trivial,
   30 segundos. Cambiar `0` por `False` en línea 1295.
3. **Fix §3.6.e Fase 2** (cruzador, fallback `pagina_no_en_mapa`).
   Recuperaría 43 fallos descartados hoy. Más invasivo que Fase 1,
   requiere su propio diseño y validación.
4. **Validaciones contra `.md` real**: §3.6.b (línea 33525 de
   `LibroVol339.2.md`), §3.6.c (tomos 331-334 — parcialmente
   cubierto por el cierre §3.6.e Fase 1, los 43 restantes son los de
   Fase 2), §4.6.c (3 fechas sospechosas), §4.6.h (3-5 casos
   modernos).
5. **Investigación: `'FALLO DE LA CORTE'` sin `SUPREMA`** (33 casos
   en top desconocidos de firma post-fix RE_APERTURA). Fragmentos
   de OCR o patrón editorial distinto. No urgente.
6. **Cuantificar daño efectivo de §4.6.a post-fix** (cuántos de los
   3.682 *realmente* capturan tribunal del fallo siguiente). Baja
   prioridad porque el fix §3.6.a probablemente lo evaporó.
7. **Auditoría detallada**: headers de meses, flag de hojas
   complementarias, comportamiento de `detectar_fin_real` en
   `ok_cortado_en_indice` (los tres hallazgos nuevos arriba).

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
