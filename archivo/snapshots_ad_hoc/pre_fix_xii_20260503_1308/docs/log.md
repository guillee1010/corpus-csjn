# Bitácora del proyecto corpus-csjn

## 30 de abril de 2026

Setup completo de versionado y aplicación del Cambio 1 (Fix de página compartida).

### Setup de infraestructura

- Instalación de Git en máquina Windows.
- Instalación de VS Code con configuración como editor por defecto de Git.
- Configuración de identidad: `Guillermo Rubinetti / guillee@gmail.com`.
- Configuración de comportamiento Windows: `init.defaultBranch=main`, `core.autocrlf=true`.
- Creación de repositorio privado en GitHub: `github.com/guillee1010/corpus-csjn`.
- Migración del proyecto fuera de Google Drive a `C:\Users\guill\Proyectos\corpus-csjn\` (Drive sincroniza mal con repos Git).
- Decisión de no incluir colección de PDFs en el repo (quedan en Drive como respaldo).
- Inclusión selectiva de archivos históricos: 17 archivos de versiones anteriores (.py viejos, CSVs chicos de diagnóstico, log de auditoría) en carpeta `historial/`. Los 7 CSVs grandes de v10-v12 (~82 MB) quedaron afuera por ser regenerables.

### Cambio 1 aplicado

Modificación en `construir_catalogo.py` línea 341:

- **Antes:** `pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1] - 1`
- **Después:** `pagina_fin_map[(tomo, pag)] = pags_ordenadas[i + 1]`

Justificación: el `-1` asumía que dos casos consecutivos no comparten página, pero en la práctica los casos se desbordan a la página siguiente compartida. La cola del fallo (dispositivo + firmas) quedaba fuera del bloque del caso. El fix extiende el bloque hasta incluir la página de cabecera del siguiente caso, y `detectar_fin_real` corta fino con sus heurísticas existentes.

Cambio adicional: sincronización de la copia duplicada en `paginas/construir_catalogo.py` (importada por `detectar_paginas.py` mediante `from construir_catalogo import extraer_tomo_de_filename`).

### Validación

Ejecución del pipeline completo (catálogo → cruce → parser):

- 5690 fallos en catálogo.
- 5601 OK en cruce (98.4%).
- 89 huérfanos totales del cruce (vs 121 en v15: 32 menos).
- 5647 casos parseados.

Comparación contra `csjn_casos_v16_PRE_FIX1.csv` (output pre-fix):

- **Mejoras (sin_firma → firma):** 175 casos.
- **Regresiones aparentes (firma → sin_firma):** 1 caso (`334_p829`).
- **`sin_firma` total:** 573 → 399 (10.1% → 7.1%).

### Diagnóstico del caso `334_p829` ("P., A. c/ ANSeS s/ Pensiones")

Inspección del PDF (tomo 334, páginas 829-836) confirmó que el caso ocupa 8 páginas con firmas Lorenzetti, Highton, Fayt, Petracchi, Maqueda, Zaffaroni en página 836. El parser POST asignó al caso un bloque de líneas 4474-4801 en `LibroVol334.3.md`, pero esas líneas corresponden a otro caso (Francisco Osvaldo Díaz S.A., página 1185 del tomo).

**Conclusión:** el bug no es del Cambio 1, es de localización en tomos multi-volumen. El cruce eligió `LibroVol334.3.md` para la página 829 cuando debió ser `LibroVol334.2.md` (rango 716-1062 según el catálogo de volúmenes generado hoy).

En PRE el bug quedaba enmascarado: el bloque era enorme (10.789 líneas, 81.012 palabras = ~40 fallos pegados) y el parser detectaba firmas de un caso muy posterior, atribuyéndolas falsamente a `334_p829` como "unanime". El Cambio 1 limita el bloque a un tamaño razonable y expone el problema honestamente como `sin_firma`.

### Catálogo de volúmenes generado

Script `generar_catalogo_volumenes.py` creado en raíz. Procesa `mapa_paginas.csv` y produce `paginas/catalogo_volumenes.csv` con `tomo / archivo / pagina_min / pagina_max / n_paginas` por cada combinación.

Resultado: esquema de paginación A confirmado (continuo entre volúmenes) en la mayoría del corpus. Tres anomalías:

- **Tomo 338:** solapamiento de 343 páginas (Vol.1 llega a 681, Vol.2 empieza en 338). Falso positivo del extractor de páginas: confundió "338" del título preliminar del Vol.2 ("TOMO 338 - VOLUMEN 2") como número de página.
- **Tomos 343 y 344:** solapamientos de 1 página (1457 y 1259 respectivamente). Páginas compartidas entre volúmenes contiguos, manejables.

### Categorías editoriales identificadas (mapeadas inspeccionando tomo 338 en PDF)

1. **`fallo_completo`** — caso típico, mayoría del corpus.
2. **`sumario_con_link`** — solo doctrina + "Ver fallo." literal (categoría B detectada antes en tomo 346).
3. **`acordada`** — actos administrativos numerados, formato propio. Detectados en tomo 338 desde página 687 ("ACORDADAS Y RESOLUCIONES").
4. **`material_preliminar`** — 6 páginas iniciales por volumen: tapa bordó, blanco, copyright + texto de consulta de jurisprudencia, título "REPUBLICA ARGENTINA / FALLOS / TOMO N - VOLUMEN N".
5. **`separador_mes`** — página con nombre de mes centrado sin numeración. Detectado en tomo 334 página 837 ("JULIO").
6. *Posible:* discurso del presidente al inicio de algunos volúmenes (no profundizado).

### Estructura del repo en este punto

- `main`: 5 commits. Estado v16 + Fix 1 (script y outputs).
- `v17`: 3 commits, mergeado a `main`.
- Working tree: untracked con scripts ad-hoc, archivos basura para limpiar, copia redundante de PRE_FIX1.

### Pendientes (orden sugerido)

1. Limpiar working tree (archivos basura, redundancias).
2. Rama dedicada `reorg-estructura`: todos los `.py` a raíz, renombrar `paginas/` a `data/`, ajustar paths internos.
3. Cambio 3 — integrar `catalogo_volumenes.csv` a `cruzar_catalogo_y_mapa.py`. Resuelve bug del 334 y similares en tomos multi-volumen.
4. Filtrar material editorial preliminar antes del mapa de páginas (resuelve solapamiento aparente del tomo 338).
5. Cambio 2 ampliado — columna `categoria_editorial` con los 5 valores identificados.
### Sesión posterior — limpieza de working tree

Limpieza del working tree antes de encarar la reorganización del repo. No fue una sesión pesada comparada con la del setup; sobre todo decisiones de inventario y dos commits chicos.

#### Inventario de scripts
- 14 .py en raíz, 9 en `paginas/`, 10 en `historial/`.
- Tres duplicados confirmados idénticos (byte a byte) entre raíz y `paginas/`: `construir_catalogo.py`, `cruce_anuarios.py`, `diag_sin_firma_ascii.py`. Decisión postergada para la rama de reorganización: en cada caso se conservará la copia de raíz.

#### Archivos borrados
- Archivo con nombre roto (`"bject -First 5..."`, 1.4 MB residuo de comando mal pegado).
- `catalogo_v14_fix1.csv` en raíz (redundante con la copia de `paginas/`).
- `paginas/csjn_casos_v16_PRE_FIX1.csv` (redundante con Git).
- `paginas/comparar_fix1.py` (script ad-hoc).

Ninguno estaba trackeado, no generan commit.

#### Mudanzas (commit A)
- `historial/bitacora.md` → `docs/log.md`. La bitácora estaba mal ubicada en `historial/` y debía estar en `docs/`.
- `paginas/secciones_indices_v14.csv` → `historial/secciones_indices_v14.csv`. Es un catálogo de índices generado durante exploración previa al armado del catálogo principal; cubre solo un volumen. Se conserva en `historial/` por valor documental.

#### Trackeo de archivos productivos (commit B)
- `generar_catalogo_volumenes.py`: script del Cambio 3 (parte 1).
- `paginas/catalogo_volumenes.csv`: output del script anterior. Se trackea provisoriamente; la decisión sobre versionado de outputs grandes queda pendiente.

#### Estado del repo al cierre de la sesión
- `main`: 2 commits nuevos (mudanzas + Cambio 3 parte 1), pusheados a GitHub.
- Working tree limpio.

#### Pendientes nuevos identificados en esta sesión
- README desactualizado (refleja estado v10, ignora pipeline de 4 etapas, padrón viejo, paths obsoletos). Decisión tomada: no reescribir entero hasta después de la reorganización del repo. Solución provisoria: README mínimo con remisión a `docs/log.md`.
- Reconstrucción retroactiva del log: el trabajo de coding previo al 30/04 (parsers v1 a v15, armado de pipeline) nunca entró a la bitácora. Pendiente para sesión propia con chats viejos a mano.