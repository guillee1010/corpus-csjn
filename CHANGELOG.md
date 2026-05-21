# Changelog

Registro de cambios del proyecto corpus-csjn: parser, auditor, cruzador y documentación.

## H053 — 2026-05-21

### Agregado
- `extraer_segmentos()` en parser.py: extrae segmentos contiguos de
  zonas con fronteras y word count.
- `csjn_casos_zonas.csv`: tercer output canónico del parser
  (149512 segmentos, schema: caso_id_canonico, tomo, zona, segmento,
  linea_ini, linea_fin, n_lineas, wc).
- Argumento `--output-zonas` en parser.py.
- `procesar_archivo()` retorna 4-tupla (casos, votos, zonas,
  desconocidos).

### Cambiado
- Búsqueda de fecha Caso (b): excluye líneas con zona "dictamen"
  (guarda defensiva, 0 impacto empírico).
- Eliminada NOTA de mejora futura en parser.py (implementada).

### Diagnóstico (sin patch)
- Firma zonificada: 15 discrepantes analizados. 10 irrecuperables
  (sin_dispositivo), 3 falsos positivos del zonificador (headers de
  sumario), 2 genuinamente complejos (ROI insuficiente: 35→33).
  Piso sin_firma ~17 confirmado.


## H052 — 2026-05-22

### Integración dictamen zonificado (Refacción C Paso 3)

**`zonificar_bloque()` enriquecido:**
- Retorna `(list[str], list[tuple])` en vez de `set(zonas)`.
  La lista por línea es la fuente canónica de fronteras de zona.
- Guarda dictamen: dentro de zona dictamen, solo `apertura` y `fecha`
  (sin apertura futura) cierran la zona. Suprime ~486 falsos positivos
  de dispositivo/firma del Procurador.
- Anclas nuevas: `RE_VISTOS` ("Vistos los autos"), `RE_REMISION`
  ("–Del dictamen/precedente...").

**`lineas_dictamen` derivado de zonas:**
- Reemplaza el loop `en_dictamen` (v12-v17) que tenía un bug: el
  `continue` dentro de `en_dictamen` saltaba la detección de votos y
  dispositivo. Si el dictamen no cerraba bien, todo el bloque quedaba
  como dictamen, inflando `wc_dictamen` y deflactando `wc_mayoria`.
- Afectaba ~3254 casos. Corregido.

**3 nuevos `sumario_editorial`:** 340_p232, 340_p538, 344_p325.
Detectados por las anclas RE_VISTOS/RE_REMISION.

**Métricas post-H052:**
- Corpus: 5862 casos (5668 fallos + 34 sumario_editorial + 160 sumario_con_link).
- sin_firma: 35 (era 38). Trayectoria: ...→69→38→35.
- Votos: 27335 (sin cambio).
- wc_dictamen: corregido en 3254 casos.



## H051 — 2026-05-21

### Refacción C: Zonificador de bloques (Paso 1 + Paso 2)

**Nuevo:** función `zonificar_bloque()` integrada en `parser.py`.
  Clasifica cada línea del bloque en zonas: sumario, dictamen, apertura,
  cuerpo, dispositivo, firma, voto_separado, epilogo, header_pagina.
  Algoritmo de 3 pasadas (headers → anclas → propagación).
  Concordancia con parser actual: firma 99.7%, dispositivo 99.6%.

**Nuevo:** `tipo_entrada="sumario_editorial"` para bloques sin zona de
  cuerpo, dispositivo ni firma. 31 casos reclasificados, 0 regresiones.

**Validación:** catálogo exhaustivo confirmado (0 fallos no catalogados
  en corpus, validado contra 5855 aperturas).

### Métricas

| Métrica | Pre-H051 | Post-H051 |
|---|---|---|
| sin_firma | 69 | 38 |
| tipo_entrada=fallo | 5702 | 5671 |
| tipo_entrada=sumario_editorial | 0 | 31 |
| tipo_entrada=sumario_con_link | 160 | 160 |
| Votos | 27335 | 27335 |
| Cobertura firma (fallos) | 98.8% | 99.3% |
| Regresiones | — | 0 |

Trayectoria sin_firma: ...→76→74→69→**38**.

### Scripts de auditoría (scripts/auditoria/H051/)

- `poc_diagnostico_firma_h051.py` — diagnóstico modos de falla
- `poc_zonificador_h051.py` — zonificador standalone con reportes
- `poc_sumario_editorial_h051.py` — validación pre-patch
- `conteo_aperturas_h051.py` — conteo RE_APERTURA vs catálogo
- `aperturas_huerfanas_h051.py` — clasificación de aperturas huérfanas
- `patch_zonificador_h051.py` — script de integración del patch



### B072: 15 conjueces en JUECES_CONOCIDOS (commit `bfad045`)

- 15 entradas nuevas en JUECES_CONOCIDOS y `_RE_FIRMA_COMPLETA`:
  García Lema, Rabbi-Baldi Cabanillas, Méndez, Montesi, Cossio,
  Pérez Petit, Romano, Petra Fernández, Chausovsky, Schiffrin,
  Aguilar, Pérez Tognola, Corcuera, Andalaf Casiello, Fernández Gómez.
- 21 mejoras, 1 regresión aceptada (346_p610).
- sin_firma: 76 → 74. Votos: 27303 → 27325.

### B073: cerrado sin fix

- 451 lfr_cambio de B070 verificados: 0 problemas.

### Clasificación sin_firma

- 74 sin_firma clasificados en 4 categorías.
- Texto del corpus extraído para inspección manual.

### B074: investigado, no committeado

- Guarda posicional en firma_actual: 13 mejoras pero 7 regresiones.
- Causa de regresiones no identificada. Queda abierto.


### H047 (2026-05-20)

- **fix(A001):** fallback `buscar_firma_inversa()` en `procesar_archivo`.
  Cuando el flujo normal no encuentra firma (`por_ello_idx=None` o
  `collect_firma_lines` vacío), busca desde el final del bloque hacia
  atrás con guardas: zona de fallo obligatoria, span ≥ 20 líneas,
  filtro zona post-firma (`RE_DATOS_PARTES`), retroceso ≤ 80 líneas.
  Funciones nuevas en parser.py: `buscar_firma_inversa()`,
  `_encontrar_zona_fallo()`, `RE_DATOS_PARTES`.
  34 mejoras, 0 regresiones. sin_firma: 148 → 114.
  Votos: 26959 → 27098. Cobertura firma: 97.4% → 98.0%.

- **fix(A001b):** `_encontrar_zona_fallo()` usa PRIMERA apertura en
  vez de última. Evita envenenamiento cuando el bloque arrastra
  residuo del caso siguiente con su propio "FALLO DE LA CORTE SUPREMA".
  Fecha/considerando/vistos restringidos a primera mitad del bloque.
  1 mejora (329_p317), 0 regresiones. sin_firma: 114 → 113.
  Votos: 27098 → 27103.

- **auditoria:** poc_a001_v1.py, poc_a001b_v1.py, diff_a001.py.
  Auditoría visual 80 casos (seed 420): 0 discrepancias.

### H046 (2026-05-20)

- **fix(B069):** eliminada búsqueda hacia atrás de Pista 1 en
  `detectar_fin_real()`. Pista 1 buscaba `primer_token_siguiente`
  desde `lfc` hasta `li+5` (bloque entero). Tokens genéricos
  (ANSES, Banco, Fisco, Provincia) y apellidos comunes (Oyarbide,
  Carmen, González) matcheaban en cuerpo argumentativo, Vistos los
  autos y firmas de jueces, truncando centenares de líneas y
  perdiendo firma + dispositivo. Fix: mantener solo búsqueda hacia
  adelante (`lfc+1` → `limite_adelante`). 277 mejoras, 4 regresiones
  aceptadas. sin_firma: 406 → 148. Cobertura firma: 92.9% → 97.4%.
  Votos: 25603 → 26959.

- **bat:** agregado `correr_parser.bat` para ejecución rápida del
  pipeline.



## H044 (2026-05-19)

### Fix
- **B067:** Tier 3 dispositivo retry sin techo. Cuando Tier 1+2 no
  encuentran dispositivo dentro del techo de `inicio_votos_indiv`,
  Tier 3 repite la búsqueda sin techo sobre todo el bloque.
  17 mejoras, 0 regresiones. sin_firma: 422 → 406 (-16).

### Invalidado
- **B066:** los ~85 "headers reales" con "juez/jueza" del inventario
  H043 eran citas jurisprudenciales wrapeadas por OCR al inicio de
  línea (42/42 validados como citas, 0 headers reales). No requiere
  fix.

### Hallazgos
- 12% del corpus (669 casos) tiene votos-antes-de-dispositivo: variante
  estructural donde los votos individuales se redactan antes del "Por
  ello" colectivo y la firma de la mayoría.
- `firma_end` pre-computado funciona como delimitador de zona (92.6%
  cobertura, p50=7 líneas del dispositivo).
- Opción D (reordenamiento del pipeline) invalidada empíricamente por
  la variante votos-antes-de-dispositivo.


## [H042] - 2026-05-18
### Fixed
- **B055 firma truncada/contaminada** (`collect_firma_lines`): eliminado
  `max_lines=40`; guarda de continuación por texto acumulado
  (`_RE_FIRMA_COMPLETA` regex de apellidos + calificador + punto);
  tolerancia a 1 línea vacía intercalada. 1262 mejoras, 0 regresiones
  reales. Commit `e258f66`.
### Added
- Constante `_RE_FIRMA_COMPLETA` en parser.py (regex de apellidos
  conocidos para detección de firma completa).
### Documented
- B061 (RE_DISID_HDR multi-línea), B062 (juez en dispositivo),
  B063 (conjueces faltantes), B064 (Otero encoding), B065 (validación
  firma↔votos).

### 2026-05-18 — H040: guardas de exclusión en Pista 2 de detectar_fin_real
**Fix:** en `detectar_fin_real`, Pista 2 usaba `linea_es_header_sumario`
directamente para detectar el inicio del sumario del caso siguiente.
La función matcheaba falsos positivos en la zona de firma: líneas como
"ARGIBAY (en disidencia)." pasan porque empiezan con ≥5 mayúsculas y
terminan en punto. Fix: nueva función `linea_es_header_sumario_guardado`
que excluye firmas (`linea_es_firma_de_juez`), calificadores
(`RE_CALIFICADOR`), headers de página (`RE_PAGE_HEADER`), marcadores de
apertura (`RE_APERTURA`, `RE_DICT_HDR`, "DICTAMEN") y headers de
voto/disidencia (`RE_HEADER_VOTO_DISIDENCIA`) antes de aceptar el match.
**Diagnóstico previo:** comparación cuantitativa de `linea_es_header_sumario`
(parser) vs `es_header_sumario_auditoria` (auditor) sobre 1.239.055 líneas
en la zona Pista 2: 124 falsos positivos del parser (38 firma-related),
10.740 matches reales compartidos. Scripts en `scripts/diagnostico/`.
**Impacto:** 32 casos recuperados (sin_firma 481 → 449). 0 regresiones.
Cobertura firma: 91.6% → 92.1%. 169 casos con n_jueces corregido,
55 con voting_pattern enriquecido (unanime → disidencia/segun_su_voto).
**Líneas modificadas:** `parser.py`, nueva función
`linea_es_header_sumario_guardado` (~línea 1151, 20 líneas) + 2 líneas
en `detectar_fin_real` Pista 2 (~líneas 1292-1295).

### 2026-05-18 — H039: 5 variantes de dispositivo nuevas
**Fix:** agregar 5 variantes a `RE_DISPOSITIVO_VARIANTES` en `parser.py`:
`por_lo_expresado`, `por_las_razones`, `por_las_consideraciones`,
`oido_el`, `que_por_ello`. Son fórmulas institucionales de apertura del
dispositivo no cubiertas por las variantes originales. Detectadas mediante
diagnóstico de los 249 casos sin_dispositivo+con_apertura, clasificados
en 77 B1a (formato no reconocido) y 172 B1b (truncamiento).
**Impacto:** 22 casos recuperados (sin_firma 503 → 481). 0 regresiones.
Cobertura firma: 91,2% → 91,6%.
**Líneas modificadas:** `parser.py`, lista `RE_DISPOSITIVO_VARIANTES`
(~línea 90). 6 líneas agregadas (5 variantes + comentario).
**Variantes evaluadas y descartadas (falsos positivos en forward):**
- `en_las_condiciones`: 40 regresiones outcome (frase argumentativa común).
- `por_lo_tanto`: 17 regresiones outcome.
- `en_atencion`: 17 regresiones outcome.
- `que_de_conformidad`: 3 regresiones outcome, 0 mejoras.
**Reversa desde votos testeada con 9 variantes:** 193 cambios outcome
(peor que forward). Confirma hallazgo H038.


### 2026-05-18 — H038: Fix B059 forward con validación de firma

**Fix:** en la búsqueda de dispositivo post-apertura, buscar el primer
match de `detectar_apertura_dispositivo` que tenga `linea_es_firma_de_juez`
en las 40 líneas siguientes. Si ningún match tiene firma, usa el primero
como fallback (comportamiento pre-fix, sin regresión). Resuelve falsos
positivos donde variantes débiles ("en consecuencia", "de conformidad",
"por lo expuesto") matcheaban texto argumental antes del dispositivo real.

**Impacto:** 279 casos recuperados (sin_firma 782 → 503). 0 regresiones.
Cobertura firma: 86.3% → 91.2%.

**Líneas modificadas:** `parser.py`, bloque de búsqueda de dispositivo
(~línea 1662). 18 líneas reemplazan 8.

**Estrategias evaluadas y descartadas:**
- Reversa pura: 278 mejoras, 86 regresiones (dispositivos de votos/resoluciones secundarias).
- Reversa desde inicio_votos_indiv: 146 mejoras, 8 regresiones.
- Reversa desde votos + firma: 147 mejoras, 7 regresiones.
- Forward + firma (elegida): 280 mejoras, 0 regresiones.

### 2026-05-18 — H036: Backstop dictamen con RE_APERTURA

**Fix:** en el loop de detección de dictamen de `procesar_archivo`, si
`en_dictamen=True` y la línea matchea `RE_APERTURA` ("FALLO/SENTENCIA
DE LA CORTE SUPREMA"), cerrar el dictamen sin consumir la línea. Evita
que dictámenes largos (donde `len(prev) >= 80` impide el cierre por
fecha) consuman el cuerpo del fallo, el dispositivo y la firma.

**Impacto:** 31 casos recuperados (sin_firma 813 → 782). 0 regresiones.
6 cambios neutros (5 B059 expuestos + 1 corrección de dispositivo).
Cobertura firma: 85.7% → 86.3%.

**Líneas modificadas:** `parser.py`, bloque `elif en_dictamen:` (~línea
1601). 7 líneas de código agregadas.

### Fix B013 — Búsqueda anclada de dispositivo (2026-05-18, H035)

- Detección de dispositivo movida fuera del loop principal a pasada
  separada con cascada: apertura_rel → dictamen_end+1 → 0.
- Techo en inicio_votos_indiv solo cuando votos son post-apertura.
- 302 casos con dispositivo prematuro resueltos.
- n_jueces=1 baja de 114 a 21; n_jueces 5-7 sube +162 casos.

---
## 2026-05-17 — visor_auditoria.py + auditar_fallo v1.0.0
- `scripts/visor/visor_auditoria.py`: nuevo script de visualización
  compacta de outputs de `auditar_fallo.py`. Agrupa spans por tipo,
  silencia headers embebidos y `catch_all_inicio` por posición.
  Opciones completas: `--solo`, `--excluir`, `--incluir`, `--tomo`,
  `--pagina`, `--con-alertas`, `--formato` (md/txt/csv), `--preview`,
  `--resumen`, `--stats`, `--stdout`, `--output`.
  Output default: `output/visor/<nombre>_vista.md`.
- `scripts/auditoria/auditar_fallo.py`: `__version__ = "1.0.0"`.
  Encabezado MD ahora incluye `Versión` y `Seed` (cuando aplica).
- `.gitignore`: agrega `archivo/auditoria/` y `output/visor/`.
- Reorganización: outputs viejos de `output/auditoria/auditar_fallo/`
  movidos a `archivo/auditoria/auditar_fallo/`.
---

## 2026-05-16 — Fix B049 Var-A: concatenar carátula partida en `detectar_caratula` (H028)

Fix en `scripts/auditoria/auditar_fallo.py`. `detectar_caratula` retrocedía
una sola línea desde el primer header de sumario; en casos de carátula partida
por salto de página devolvía solo la segunda mitad. Fix en Estrategia 1 y
Estrategia 2: si la candidata no tiene `c/`, `s/` ni `|` y no termina en
punto, busca la línea anterior y concatena con manejo de silabación. Guardia:
la línea anterior no debe ser mes calendario solo, no debe empezar con `V.`,
no debe terminar en punto ni empezar en minúscula. Validado con seed 15052026,
n=80: 7 mejoras, 0 regresiones. Var-B (340_p1551) pendiente. No afecta corpus
productivo. Detalle en BITACORA H028.

## 2026-05-16 — Documentación H027: refinamiento post-Fase A continuación

Tres commits de documentación:
- `GRAMATICA_DEL_FALLO.md`: refinamiento post-Fase A continuación (paralelo
  borde superior ↔ epílogo, HN3 → HN3').
- `BITACORA.md`: append H027 — lectura completa del auditor + mapeo
  producción × auditor (Fase B).
- `DEUDA_TECNICA.md`: B049 mecanismo refinado, B050/B051 nuevos, M07/M08
  nuevos, conteos del resumen ejecutivo actualizados.

## 2026-05-16 — Documentación H025: reflexión arquitectónica + revert

Commits de documentación sobre páginas compartidas y `detectar_fin_real`:
- `GRAMATICA_DEL_FALLO.md`: propuesta arquitectónica de parser por gramática
  del fallo + diálogo entre vecinos.
- `BITACORA.md`: H025 — reflexión arquitectónica, dos manifestaciones de B045.
- `DEUDA_TECNICA.md`: B045 refinado con manifestaciones A/B, B046 nuevo,
  B018 nota, M01 ampliada.
- `PIPELINE.md`: H025 — 4 fricciones nuevas/ampliadas.
- Intento fallido de verificación empírica B046 en 346_p1205 (commiteado,
  revertido y documentado honestamente al cierre).

---

## 2026-05-15 — Documentación H022-H024: verificación mecanismos B022/B025/B044/B045

Commits de documentación sobre verificación de bugs contra `.md` crudo:
- `DEUDA_TECNICA.md`: B045 nuevo (causa raíz arquitectónica), B044 nuevo,
  B022 y B025 con estado `confirmado_mecanismo`. B018 causa raíz refinada,
  B022 variante 2, B043 nuevo.
- `BITACORA.md`: H022 spot-check 7 testigos + H023 verificación contra
  `parser.py` (M3 refutado, M2 confirmado) + H024 verificación M5/M4/M1
  + 346_p1205, hallazgo arquitectónico B045.

## 2026-05-15 — feat(auditoria): --seed y wrapper tabular para auditar_fallo

- `feat`: agregar `--seed` a `auditar_fallo.py` para muestreo reproducible.
- `feat`: wrapper `tabular_senales_lote` para análisis en lote.
- `docs`: H021 — infraestructura auditoría persistencia. H020 — flag M05 +
  plan auditoría. `DEUDA_TECNICA.md`: reescritura canónica B001-B042 + M01-M08.

---

## 2026-05-14 — Inventario y limpieza del repositorio (Fase 1 y 2)

Reorganización documental en varias fases:
- Rescate de análisis a rama viva, archivado de scripts históricos.
- READMEs de `scripts/` y subdirectorios.
- Deduplicación de entradas en BITACORA.
- Untrack de prompts de continuación (scaffolding personal, no producto).
- Rediagnóstico §4.6.b contra CSV vivo; descarte de herramienta paralela
  (`auditoria_4_6_b_prefix.py` archivado, `diagnostico_4_6_b_cluster.py`
  eliminado). Convención: `scripts/diagnostico/` para diagnósticos
  cuantitativos sobre CSVs; diagnóstico fino del corpus vía
  `scripts/auditoria/auditar_fallo.py`.

---

## 2026-05-09 — fix(parser) + fix(cruzador): RE_APERTURA y bug pg_fin+1

Dos fixes con impacto en corpus productivo:
- `fix(cruzador)`: resuelto bug `pg_fin+1` (§3.6.a) en
  `cruzar_catalogo_y_mapa.py`. Output regenerado.
- `fix(parser)`: `RE_APERTURA` tolerante a doble espacio + hallazgo hojas
  complementarias tomos 331-334.
- `fix(cruzador)`: §3.6.e Fase 1 — resolver `pagina_fin_no_en_mapa` por
  hojas complementarias.
- Docs: PIPELINE cerrado §3 y §4; HALLAZGOS reorganizado.
- BITACORA: sesiones 2026-05-09 nocturna (validación H018 random-80 + F012)
  y 2026-05-10 (refinación de hallazgos).

## 2026-05-08 — feat(auditoria): auditar_fallo.py v1

- `auditar_fallo.py` v1: módulo de auditoría manual del corpus CSJN.
- Fix paths default + corrida random 50. F007 nuevo. Estrategia
  auditor→parser (H015).
- Docs: H014/H015, H016 (punto ciego del auditor), H017 (diseño detector
  amputación inferior), H018 (diseño detector borde inferior, implementación
  pospuesta, F010/F011 nuevos).

---

## 2026-05-03 — Fix 1: V1 como fuente primaria de `case_name_cuerpo`

- Cobertura `case_name_cuerpo` sube de 48.3 % a 84.1 %, 0 regresiones.
- Fix 1 commiteado en CSV productivo. Snapshots movidos a
  `archivo/snapshots_ad_hoc/`. Detalle en
  `docs/analisis_forense_pipeline.md` §XX-XXI.

---

## 2026-05-02 — Reorganización estructural del proyecto + re-corrida pipeline

- Reorganización estructural de directorios.
- Re-corrida pipeline post-migración: 5.819 fallos, 21.876 votos
  (genera `csjn_casos_votos.csv`). Validación funcional OK.
- `.gitattributes`: forzar LF en `.py/.md/.csv/.txt`, CRLF en `.ps1`.
- Actualización de paths en `scripts/pipeline/` (15 reemplazos, sin
  cambios de lógica de runtime).

---

## 2026-05-01 — v17 beta (descartada) + fix catálogo

- `construir_catalogo_v15.py`: fix detección inicio de índice de nombres
  en tomos modernos.
- v17 beta v1 conservado; v17 beta v2 descartada (rollback protocol
  documentado en CHANGELOG anterior). Scripts diagnósticos movidos a
  `scripts/diagnosticos/`.

---

## 2026-04-30 — v16 fix1 + merge v17 + outputs pipeline

- Fix 1 en `construir_catalogo.py` (sacar `-1` en línea 341): resuelve
  página compartida. Output: `csjn_casos_v16_fix1.csv` con 175 mejoras
  `sin_firma→firma`.
- Merge branch `v17`.
- Changelog reconstruido v1-v17 (`docs/changelog_parser.md`).

---

## Versiones anteriores del parser (v10-v16)

Ver `docs/changelog_parser.md` y historial de git (`git log --oneline`).

## H053 — 2026-05-21

### Agregado
- `extraer_segmentos()` en parser.py: extrae segmentos contiguos de
  zonas con fronteras y word count.
- `csjn_casos_zonas.csv`: tercer output canónico del parser
  (149512 segmentos, schema: caso_id_canonico, tomo, zona, segmento,
  linea_ini, linea_fin, n_lineas, wc).
- Argumento `--output-zonas` en parser.py.
- `procesar_archivo()` retorna 4-tupla (casos, votos, zonas,
  desconocidos).

### Cambiado
- Búsqueda de fecha Caso (b): excluye líneas con zona "dictamen"
  (guarda defensiva, 0 impacto empírico).
- Eliminada NOTA de mejora futura en parser.py (implementada).

### Diagnóstico (sin patch)
- Firma zonificada: 15 discrepantes analizados. 10 irrecuperables
  (sin_dispositivo), 3 falsos positivos del zonificador (headers de
  sumario), 2 genuinamente complejos (ROI insuficiente: 35→33).
  Piso sin_firma ~17 confirmado.
