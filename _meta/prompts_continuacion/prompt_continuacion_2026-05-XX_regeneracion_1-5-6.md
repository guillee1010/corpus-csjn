# Prompt de continuación — sesión próxima (regeneración 1 + 5 + 6)

> **Origen**: cierre del paquete 3 en sesión 2026-05-09 (ver
> `BITACORA_2026-05-09_pipeline_pendientes.md`).
>
> **Objetivo de la sesión**: ejecutar los paquetes 1, 5 y 6 de
> `PIPELINE_PENDIENTES.md` en una sola sesión, regenerando los
> datasets canónicos una sola vez.

---

## Contexto en una pantalla

El proyecto `corpus-csjn` (rooted en
`C:\Users\guill\Proyectos\corpus-csjn`) cerró el mapeo de su
pipeline canónico el 09/05. Quedaron 7 paquetes residuales en
`PIPELINE_PENDIENTES.md`. Tres de ellos (1, 5, 6) son fixes de
código que regeneran `csjn_casos.csv` y `csjn_casos_votos.csv`.

**La sesión 2026-05-09** decidió agruparlos para evitar tres
regeneraciones sucesivas. También cerró el paquete 3 (higiene,
no toca datasets).

## Por qué agruparlos

Los tres paquetes regeneran los mismos dos CSVs canónicos. Hacerlos
separados produciría tres versiones del dataset en circulación, con
subconjuntos distintos de bugs corregidos. Agrupados en una sola
pasada → una sola regeneración → un único dataset final con los
tres fixes aplicados.

## Plan de ejecución (orden importa)

### Paso 1 — Paquete 5 (corrección `pg_fin+1` en cruzador)

**Por qué primero**: regenera `fallos_localizados.csv`, que es
input del parser. Si los demás paquetes corren sobre el
`fallos_localizados.csv` viejo, hay que rehacerlos.

**Trabajo**:
1. Localizar la línea ~220 de `scripts/pipeline/cruzar_catalogo_y_mapa.py`
   donde se busca `pg_fin + 1`.
2. Reemplazar por `pg_fin`.
3. Re-correr el cruzador.
4. Validar contra `fallos_localizados.csv` viejo:
   - ¿Cuántos `fallo_cruza_archivos` desaparecen?
   - ¿Cuántos `linea_fin` cambian?
   - ¿Mediana de bloque baja en ~32 líneas (predicción §3.6.a)?

**Tiempo**: 90-120 min.

### Paso 2 — Paquete 1 (fix doble espacio tomo 343 en parser)

**Trabajo**:
1. Localizar comparaciones literales contra
   `'FALLO DE LA CORTE SUPREMA'` y `'SENTENCIA DE LA CORTE SUPREMA'`
   en `scripts/pipeline/parser.py`.
2. Reemplazar por comparación con normalización de espacios
   (regex `\s+` o `re.sub(r'\s+', ' ', ...)`).
3. **NO** re-correr el parser todavía. Esperar al paso 3.

**Tiempo**: 15-20 min (solo edición; la ejecución sale en paso 4).

### Paso 3 — Paquete 6, opción A (fix votos mal clasificados §4.6.k en parser)

**Recomendación**: opción A (fix dentro del parser), no opción B
(post-procesamiento). Porque ya estamos editando el parser de todos
modos en paso 2. Hacer A en paralelo no agrega regeneración y deja
el flujo limpio.

**Trabajo**:
1. Localizar `detectar_posicion` (o equivalente) en `parser.py`.
2. Identificar la condición que asigna `mayoria` por default cuando
   `tipo_voto_sep` es `'indeterminado'`.
3. Reescribir: si `texto_voto` empieza con `Disidencia`/`DISIDENCIA`
   → `posicion='disidencia'`. Si empieza con `Voto`/`VOTO` →
   `posicion='segun_su_voto'`.

**Tiempo**: 60-90 min.

### Paso 4 — Re-correr el parser una sola vez

Sobre el `fallos_localizados.csv` corregido por paso 1, con los
fixes 1 y 6 aplicados al código del parser.

**Validaciones post-regeneración**:

- 0 filas con `posicion='mayoria'` y `texto_voto` no vacío
  (validación paquete 6).
- 12 casos del tomo 343 antes con `status_localizacion='ok_sin_marcador_apertura'`
  ahora con `status='ok'` y `apertura_tipo='fallo'` (validación paquete 1).
- Outliers de `word_count` (§4.6.g) bajan (validación paquete 5).
- Cascada `detectar_fin_real` reduce a una sola pista efectiva
  (predicción §A.5.a).

**Tiempo**: 30-45 min (incluye validación).

### Paso 5 — Actualizar `PIPELINE.md`

Cerrar:
- §3.6.a (corregido en paquete 5).
- §3.6.d (cuantificar comportamiento de `fallo_cruza_archivos`
  post-fix; cierra el ⏳ residual).
- §4.6.c (eliminar referencia al bug refutado, dejar nota del fix
  trivial de espacios aplicado).
- §4.6.k (corregido en paquete 6).
- §4.6.g (recalcular outliers).
- §A.5.a (validar predicción).

**Tiempo**: 30-45 min.

## Tiempo total estimado

3.5 - 4.5 horas. Es una sesión larga. Conviene tener buffer.

## Archivos a tener listos antes de empezar

| Archivo | Para qué paso |
|---|---|
| `scripts/pipeline/cruzar_catalogo_y_mapa.py` | 1 |
| `scripts/pipeline/parser.py` | 2, 3 |
| `output/localizacion/fallos_localizados.csv` | 1 (validación) |
| `output/parser/csjn_casos.csv` | 4 (validación) |
| `output/parser/csjn_casos_votos.csv` | 4 (validación) |
| `PIPELINE.md` | 5 |

## Antes de tocar código

**Snapshot del estado actual** (para poder revertir si algo sale
mal). Desde la raíz del repo:

```powershell
git status
git add -A
git commit -m "Snapshot pre-regeneración 1+5+6"
```

O snapshot manual de los CSVs:

```powershell
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
mkdir -Force "snapshots\pre_regen_$ts"
Copy-Item output\parser\csjn_casos.csv "snapshots\pre_regen_$ts\"
Copy-Item output\parser\csjn_casos_votos.csv "snapshots\pre_regen_$ts\"
Copy-Item output\localizacion\fallos_localizados.csv "snapshots\pre_regen_$ts\"
```

## Pendientes que quedan después de esta sesión

- **Paquete 2** (tomos 348-349 sin secciones) — sesión higiene.
- **Paquete 4** (outputs secundarios §1) — sesión higiene.
- **Paquete 7** (fix §4.6.j corte en dictamen) — solo si vale la
  pena recuperar 25 casos (0,4% del corpus).

Ninguno bloquea uso del corpus para análisis de tesis.

## Convención post-sesión

1. Actualizar `BITACORA.md` con la entrada de la sesión.
2. Actualizar `CHANGELOG.md` con los fixes aplicados al código.
3. Actualizar `PIPELINE.md` cerrando los ⏳ pertinentes.
4. Commit en git con mensaje claro:
   `"Fixes 1+5+6 aplicados: doble espacio tomo 343, pg_fin+1 cruzador, votos §4.6.k"`.

## Nota importante sobre opción A vs B del paquete 6

`PIPELINE_PENDIENTES.md` ofrece dos opciones para el paquete 6:

- **Opción A**: fix en el parser. 60-90 min. Más limpio, regenera
  datasets de manera canónica.
- **Opción B**: post-procesamiento sobre CSVs ya generados.
  30-40 min. Más rápido pero deja un CSV "post-procesado" colgando
  fuera del flujo canónico.

**Esta sesión usa opción A**. Justificación: ya estamos regenerando
los datasets en el mismo paso (parser corregido por paquete 1
también), así que no hay tiempo extra de regeneración. La opción A
mantiene el flujo canónico limpio y evita deuda técnica nueva.

## Decisión arquitectónica heredada de sesión 2026-05-09

`PIPELINE.md` documenta solo el pipeline canónico
(`scripts/pipeline/`). Cualquier descubrimiento sobre scripts
auxiliares durante la sesión **no se documenta en `PIPELINE.md`**:
se anota aparte para futura sesión dedicada al bloque
`scripts/auxiliares/`.
