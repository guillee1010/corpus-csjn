# Changelog

Registro de cambios al pipeline. Formato: [Fecha] — Versión/Componente — descripción.

## [2026-05-02] — `paginas/cruzar_catalogo_y_mapa.py`

**Tipo:** Fix (Bug D — último fallo del tomo arrastra aparato editorial de índices)

**Cambios:**

- Función nueva `cargar_indices_nombres(ruta)`: lee `secciones_indices_v14.csv` y devuelve dict `{archivo: linea_inicio_indice_nombres}`. Devuelve dict vacío si la ruta es `None` o el archivo no existe.
- `cruzar()` acepta nuevo parámetro opcional `indices_nombres_por_archivo` con default `None`.
- En la rama de "último fallo del tomo" (`pg_fin is None`):
  - Si el archivo está en el dict de índices: `linea_fin = linea_inicio_indice_nombres - 1`, status `ok_cortado_en_indice`.
  - Si no: fallback al comportamiento anterior (`linea_fin = última línea del .md`, status `ultimo_del_tomo`).
- `procesar()` y `main()` aceptan quinto argumento opcional `secciones_indices_csv`.
- Status nuevo agregado al docstring y al CSV de resumen: `ok_cortado_en_indice`.
- `huerfanos.csv` excluye tanto `ok` como `ok_cortado_en_indice` (los nuevos buenos).

**Backward compatibility:** sin el quinto argumento, comportamiento idéntico al anterior. Validado con tests sintéticos.

**Hash SHA256 del archivo modificado:** `FE1585DAA87CFA0ED2E8809F8C46370AF11E1132B7EB8B2D2C963D227B2A87C1`

**Resultado en corrida real (catálogo v15, 5862 entradas):**
- 19 nuevos casos `ok_cortado_en_indice` ✓
- 0 casos `ultimo_del_tomo` ✓
- Total huérfanos baja de 121 (estimado pre-fix) a 70 (real post-fix)
- Anomalía pendiente de diagnóstico: `pagina_fin_no_en_mapa` cayó a 0 (antes 39); `fallo_cruza_archivos` subió a 27 (antes 20). Hipótesis principal: cambio de catálogo v14→v15.

**Archivos afectados:**
- `paginas/cruzar_catalogo_y_mapa.py` (modificado)
- `paginas/fallos_localizados.csv` (regenerado)
- `paginas/fallos_localizados_huerfanos.csv` (regenerado)
- `paginas/fallos_localizados_resumen.csv` (regenerado, nueva columna `ok_cortado_en_indice`)

---

## [2026-05-01] — `csjnv17_beta.py`

**Tipo:** Patch (fix349)

**Cambios:**
- Tratamiento especial para Tomo 349 (provisorio, índice truncado en V).

**Output:** `csjn_casos_v17beta_fix349.csv` (10.9 MB, 5819 casos parseados).

---

## [2026-05-01] — `construir_catalogo_v15.py`

**Tipo:** Mejora del catálogo

**Cambios:**
- Corrección de bias en detección de fin de fallo (v14 sobreestimaba bloques).
- Output: `catalogo_v15.csv` (5862 entradas, +24 KB respecto a v14).

**Impacto medido:**
- `sin_dispositivo`: −580
- `unanime`: +831
- Word count global: −5,6%

---

## [2026-04-30] — `csjnv17beta.py` (rollback)

**Tipo:** Rollback de v17_beta_v2

**Contexto:** v17_beta_v2 intentó manejar fallos con dictamen del Procurador embebido (Bug A) pero introdujo regresiones en detección de fechas de fallo. Se hizo rollback a v17_beta original.

**Lección:** parchar dictámenes embebidos requiere refactor más profundo que un patch puntual. Documentado como Bug A en `DEUDA_TECNICA.md`.

---

## [2026-04-29] — `paginas/cruzar_catalogo_y_mapa.py` (versión inicial)

**Tipo:** Componente nuevo

**Cambios:**
- Script standalone para cruzar catálogo + mapa de páginas → fallos_localizados.csv.
- Genera `huerfanos.csv` con casos que no se pudieron localizar limpiamente.
- Hash SHA256 versión inicial: pendiente de registrar (archivo perdido en sobrescritura del 2/5/2026).

---

## [2026-04-28] — Generación de `mapa_paginas.csv`

**Tipo:** Componente del pipeline

**Cambios:**
- `paginas/detectar_paginas.py` produce `mapa_paginas.csv` con headers de página detectados en cada `.md`.
- Cobertura: 46.933 páginas únicas en 46 archivos.
- 3 duplicados (tomo, página) detectados y resueltos por regla "línea más baja gana": Tomo 338 p.338, Tomo 343 p.1457, Tomo 344 p.1259.

---

## Versiones históricas del parser

| Versión | Fecha | Casos parseados | Notas principales |
|---------|-------|----------------:|-------------------|
| v9 | 2026-04 (early) | 817 | Versión bifurcada: csjn_casos_v9.csv + csjn_casos_v9_votos.csv (2.803 votos individuales) |
| v10-v11 | 2026-04-26 | — | Iteraciones intermedias |
| v12 | 2026-04-28 | — | csjn_casos_v12_nueva.csv (12.6 MB) |
| v14 | 2026-04-28 | — | Catalog-delimited |
| v15 | 2026-04-29 | 817+ | Agrega `linea_fin_real`, `status_fin`, `pista_fin` con búsqueda bidireccional |
| v16 | 2026-04-29 | — | Mejoras incrementales |
| v17_beta | 2026-04-30 | 5819 | Versión actual estable |
| v17_beta_v2 | 2026-04-30 | — | Rollback (regresión en dictámenes) |
| v17_beta + fix349 | 2026-05-01 | 5819 | Tratamiento especial Tomo 349 provisorio |

---

## Convenciones para futuros cambios

- Cambios al pipeline se documentan acá antes de aplicarse.
- Cambios destructivos (sobrescritura de scripts, eliminación de archivos) requieren snapshot previo en `snapshots/snapshot_YYYY-MM-DD_HHMM/`.
- Hash SHA256 obligatorio para archivos modificados.
- Bugs detectados pero no fixeados van a `DEUDA_TECNICA.md`, no acá.
- Hallazgos de diagnóstico (positivos o negativos) van a `BITACORA.md`.

## [2026-05-06] — Sin cambios de código

Sesión de diagnóstico. No se modificó ningún script del pipeline.
Hallazgos en BITACORA.md H013.

## [2026-05-08] — `scripts/auditoria/auditar_fallo.py`

**Tipo:** Componente nuevo

**Cambios:**

- Módulo nuevo: `scripts/auditoria/auditar_fallo.py`. Herramienta de auditoría manual de bloques del corpus + API canónica programática (`auditar_fallo(tomo, pagina) -> dict`).
- Reusa por importación regex y helpers de `scripts/pipeline/parser.py` (no copia, no reimplementa). Heurísticas auxiliares propias del auditor: `es_header_sumario_auditoria` (cubre formatos sin puntuación + con `:` y subtítulo), `detectar_caratula` (estructural, no por mayúsculas/minúsculas).
- Función `segmentar_bloque(bloque, ...) -> list[Span]` materializa la separación entre segmentación y extracción de features, cosa que el parser actual no hace (parser.py L1513-1564).
- 10 tipos de span emitidos: `caratula`, `sumario`, `dictamen`, `cuerpo_mayoria`, `voto`, `disidencia`, `firma`, `sumario_con_link`, `header_pagina`, `catch_all`. `header_pagina` es transversal; los demás semánticos son disjuntos. Invariantes verificadas (cobertura + disjunción) en cada llamada.
- CLI: `--tomo X --pagina Y` (caso único), `--tomo X --pagina A,B,C` (varios), `--random N [--tomo X] [--status Y]` (muestreo). Output default a archivo en `scripts/auditoria/output/auditoria_<timestamp>.md`. Flag `--stdout` para terminal. Flag `--output` para ruta específica.
- Rutas default relativas al layout actual del repo: `corpus/`, `output/localizacion/fallos_localizados.csv`, `output/catalogo/mapa_paginas.csv`. Override con `--corpus`, `--localizados`, `--mapa`. Falla ruidoso si default no existe.

**Backward compatibility:** módulo nuevo, no modifica nada existente. No regenera CSVs. No consume `csjn_casos.csv` (decisión deliberada: la auditoría no audita el output del parser con el output del parser).

**Validación:**

Casos contrastados contra `.md` real durante construcción: Sivaslian (349_p306, status `ok_cortado_en_indice`, 3.93% residuo), Cerboni (331_p1028, voto separado de Argibay, 8.28%), Macri (349_p81, disidencia larga, 3.74%), Lavrentiev (349_p28, 8.12%), Décima (349_p40, 22.13% — caso siguiente arrastrado), Generación Zoe (349_p75, 0%). Cobertura y disjunción OK en todos.

**Bugs del parser identificados durante validación (anotados en BITACORA H014, no fixeados acá):**

- F001: `RE_VOTO_HDR` no matchea `Voto la señora` (medido: 2 votos perdidos en LibroVol331.2.md).
- F002: `detectar_fin_real` extiende al fallo siguiente.
- F003: `detectar_fin_real` corta corto en último del tomo.
- F004: arrastre del fallo previo al inicio del bloque.
- F005: fin del dictamen pisa el FALLO DE LA CORTE.
- F006: sumarios editoriales no segmentados (motivo original de H013).

**Archivos afectados:**

- `scripts/auditoria/auditar_fallo.py` (nuevo)
- `scripts/auditoria/medir_voto_hdr.py` (nuevo, helper de medición de F001)
- `scripts/auditoria/output/` (directorio nuevo, gitignored)

**Pendiente próxima sesión:**

- Corrida `--random 50` sobre corpus completo para medir distribución de residuo.
- Decidir partición `metadatos_editoriales` con datos empíricos.
- Migrar fixes F001-F005 al parser en bloque coordinado, regenerar corpus una sola vez.

