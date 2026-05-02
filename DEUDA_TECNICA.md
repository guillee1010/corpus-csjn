# Deuda Técnica

Estado de bugs identificados en el pipeline. Diferencia clara entre **deuda activa** (bugs sin resolver), **deuda en validación** (fix aplicado, validación pendiente) y **deuda cerrada** (resuelto y verificado).

**Última actualización:** 2/5/2026.

---

## Estado del corpus

- **Catálogo:** 5862 entradas (v15)
- **Universo procesable:** 19 tomos (329-349, exclusión metodológica de 335-336)
- **Cobertura objetivo:** ≥99%
- **Cobertura actual (último parser):** 5819 / 5862 = 99,3% del catálogo
- **Cobertura post fix Bug D (esperada, en validación):** ≥99,7%

---

## Deuda EN VALIDACIÓN

### Bug D — Último fallo del tomo arrastraba aparato editorial de índices

**Estado:** Fix aplicado 2/5/2026, validación post-corrida pendiente.

**Causa raíz:** el localizador `paginas/cruzar_catalogo_y_mapa.py` asignaba `linea_fin = última línea del .md` para los últimos fallos del tomo. Como el final del `.md` contiene los índices oficiales (nombres, materias, sumario, legislación, general), el bloque del último fallo arrastraba todo el aparato editorial. El localizador, defensivamente, marcaba estos casos como `ultimo_del_tomo` y los enviaba a huérfanos.

**Casos afectados:** 19 (uno por archivo terminal de cada tomo: 329_p6087, 330_p5435, 331_p2925, 332_p2898, 333_p2445, 334_p1920, 337_p1581, 338_p1583, 339_p1834, 340_p2029, 341_p2027, 342_p2399, 343_p2280, 344_p3782, 345_p1549, 346_p1564, 347_p2352, 348_p1796, 349_p306).

**Fix aplicado:** modificación de `paginas/cruzar_catalogo_y_mapa.py` para usar `linea_fin = linea_inicio_indice_nombres - 1` cuando se pasa `secciones_indices_v14.csv` como quinto argumento. Status nuevo: `ok_cortado_en_indice`. Backward compatible.

**Validación pendiente en próxima sesión:**
1. Spot-check que los 19 casos tengan `linea_fin` exactamente igual a la predicción.
2. Re-corrida del parser sobre `fallos_localizados.csv` regenerado.
3. Verificación que los 19 casos quedan bien parseados (voting_pattern, firmas, outcome).
4. Diff contra output del parser pre-fix para confirmar cero regresión en los 5819 que andaban.

---

## Deuda ACTIVA

### Bug A — Cabecera con dictamen del Procurador embebido (`pagina_no_en_mapa`)

**Casos afectados:** 43.

**Patrón estructural:**
```
Línea N:         CARÁTULA EN MAYÚSCULAS         ← cabecera del fallo
Líneas N+1 a M:  Sumarios doctrinales            ← resumen oficial
Línea M+1:       Dictamen de la Procuración General
...              [cuerpo del dictamen, secciones romanas I-V]
Línea P:         [fecha del dictamen]
Línea P+1:       FALLO DE LA CORTE SUPREMA
```

**Causa raíz hipotética:** el detector de páginas (`paginas/detectar_paginas.py`) no reconoce la cabecera en mayúsculas como inicio de página de fallo cuando hay dictamen previo. Por lo tanto la página de inicio del fallo nunca entra al `mapa_paginas.csv`, y el localizador devuelve `pagina_no_en_mapa`.

**Distribución por tomo:**
- Tomo 331: 11 casos (Boston Cía. de Seguros, Villarreal, Barhoumi, etc.)
- Tomo 332: 11 casos
- Tomo 333: 11 casos
- Tomo 334: 10 casos

Es decir: el bug se concentra en el régimen editorial 2008-2011 de la Secretaría de Jurisprudencia. Tomos posteriores tienen el patrón en proporción mucho menor o no lo tienen.

**Caso paradigmático:** Boston Cía. de Seguros (Tomo 331 p. 7). En `markdowns_v2/LibroVol331.1.md`:
- Línea 58: cabecera `BOSTON Cía. de SEGUROS S.A. c/ FEDERAL EXPRESS`
- Líneas 59-96: sumarios
- Líneas 97-230: dictamen del Procurador Esteban Righi
- Línea 231: marcador `FALLO DE LA CORTE SUPREMA`
- Línea 232: `Buenos Aires, 5 de febrero de 2008.`

**Importancia metodológica:** estos 43 casos pueden tener composición sustantiva distinta del corpus general — fallos con dictamen tienden a ser por recurso extraordinario, con disidencias presentes. Boston confirmó: tiene mayoría + Lorenzetti/Maqueda en disidencia. Si los 43 casos están sesgados hacia disidencias, perderlos sesga el corpus contra H3 de la tesis (que postula que la ausencia de incentivos institucionales para opinión unificada promueve concurrencias y disidencias).

**Fix candidato:** modificar `paginas/detectar_paginas.py` para reconocer el patrón "cabecera mayúsculas + sumarios + dictamen" como inicio alternativo de página cuando el header convencional no aparece.

**Estimación:** 1-3 horas de trabajo + validación. Riesgo medio-alto: el detector sustenta los 5773 casos que ya andan, cualquier modificación puede generar regresión.

**Atribuible a:** pipeline interno. Resoluble en código.

**Prioridad:** ALTA. Es el cluster más grande pendiente y el más relevante metodológicamente.

---

### Bug C — Página final +1 no detectada (`pagina_fin_no_en_mapa`)

**Casos afectados:** 39 (pre-fix). **Post-fix Bug D: 0 casos.**

**Anomalía detectada en validación post-fix Bug D:** los 39 casos desaparecieron del CSV de huérfanos sin que el fix los hubiera tocado directamente. Hipótesis principal: la categorización pre-fix se hizo contra `fallos_localizados_huerfanos.csv` generado con catálogo v14, mientras que la corrida post-fix usó catálogo v15.

**Estado:** sospechoso de estar resuelto por mejora del catálogo (v14→v15), pero pendiente de verificación.

**Acción pendiente:** confirmar la hipótesis comparando carátulas entre snapshot del huérfanos viejo y output actual.

---

### Bug B — Fallo cruza archivos (`fallo_cruza_archivos`)

**Casos afectados:** 20 (pre-fix) / 27 (post-fix Bug D).

**Anomalía detectada:** subió +7 casos post-fix. Improbable que sea efecto del fix Bug D (toca otra rama). Hipótesis principal: cambio de catálogo v14→v15.

**Causa raíz:** el catálogo coloca el fallo siguiente en otro `.md`, y el localizador termina el bloque actual con la última línea del archivo de inicio. Mismo problema que Bug D pero entre archivos en lugar de al final del tomo.

**Fix candidato:** aplicar la misma lógica del Bug D — cortar en `linea_inicio` del primer índice (de nombres) del archivo de inicio. Cambio quirúrgico en la rama `fallo_cruza_archivos` del mismo script.

**Estimación:** 30-45 minutos. Riesgo bajo si se aplica como fix separado de Bug D.

**Decisión metodológica:** no aplicar junto con Bug D. Validar Bug D primero, después abrir sesión separada para Bug B.

**Prioridad:** MEDIA. Pocos casos, pero fix barato.

---

### Cluster sin causa raíz documentada — fallos breves de 2014-2025

**Casos afectados:** ~5 fallos breves del régimen reciente (rango 6-13 páginas) que aparecen como huérfanos sin patrón obvio.

**Estado:** sin investigar. La hipótesis de "plenos largos atípicos" cubría los huérfanos largos del régimen reciente, pero estos cinco son cortos.

**Acción pendiente:** abrir 2-3 de estos casos en su `.md` correspondiente y mapear el patrón.

**Prioridad:** BAJA. Pocos casos, sustantivamente menos relevante.

---

### Bug 1 (CSJN editorial, no resoluble en código) — Y.P.F. c/ Mercante Hnos. del Tomo 349

**Casos afectados:** 1 (Y.P.F. en p.43 del Tomo 349).

**Causa:** truncamiento del índice oficial del Tomo 349 (provisorio, publicado 2026). El índice corta en V (Vargas) y omite W-Z. El fallo Y.P.F. existe en el cuerpo del `.md` pero no en el índice, por lo que el catálogo no lo registra.

**Atribuible a:** Editor de Fallos de la CSJN, no al pipeline.

**Resolución prevista:** esperar publicación de la versión definitiva del Tomo 349 con índice completo. Re-correr el pipeline. Y.P.F. quedará incorporado naturalmente.

**Tomos auditados con índice completo:** 337 (2014), 343 (2020), 347 (2024), 348 (2025) — todos terminan en Z. El 349 es excepcional por ser provisorio del año en curso.

**Hallazgo sustantivo (anotado para tesis):** Y.P.F. tiene composición ampliada por conjueces (Rosatti + Lorenzetti + Aranguren + Lozano + Sánchez = 5 firmantes, 3 conjueces). Caso útil como ejemplo de integración atípica para H4 de la tesis.

---

## Deuda CERRADA

(Pendiente de mover Bug D acá una vez confirmada la validación.)

---

## Deuda METODOLÓGICA

### Reorganización del proyecto

**Estado:** pendiente de sesión dedicada.

Hay duplicados de varios `.py` entre raíz y `paginas/`:
- `construir_catalogo.py` (raíz) ≡ `paginas/construir_catalogo.py`
- `cruce_anuarios.py` (raíz) ≡ `paginas/cruce_anuarios.py`
- `extraer_muestra.py` (raíz) ≡ `paginas/extraer_muestra_sf.py`
- `diag_sin_firma_ascii.py` (en `scripts/diagnosticos/` y `paginas/`)

Sugerencia de estructura objetivo:
```
corpus-csjn/
├── pipeline/                  ← scripts del pipeline activo
│   ├── 01_detectar_paginas.py
│   ├── 02_construir_catalogo.py
│   ├── 03_cruzar_catalogo_y_mapa.py
│   └── 04_parser.py (csjnv17)
├── data/                      ← inputs y outputs
│   ├── catalogos/
│   ├── mapas/
│   └── corpus_estructurado/
├── markdowns_v2/              ← .md fuente (sin cambio)
├── analisis/                  ← scripts de análisis (cruce_anuarios, etc.)
├── diagnosticos/              ← scripts ad-hoc
├── snapshots/                 ← backups
└── docs/                      ← README, CHANGELOG, BITACORA, DEUDA
```

**Riesgo:** los scripts usan rutas relativas que cambian con la mudanza. Requiere validación del pipeline completo post-mudanza.

**Recomendación:** sesión dedicada con backup completo previo, plan de rollback claro, y suite de tests post-reorganización.

---

### Refactor v18 — unidad operativa por línea, no por página

**Estado:** propuesta para versión futura del pipeline.

**Diagnóstico:** la arquitectura actual mezcla dos sistemas de coordenadas (página del catálogo, línea del archivo). Los clusters `pagina_no_en_mapa` y `pagina_fin_no_en_mapa` (82 casos pre-fix) son errores de la traducción página↔línea, no de detección de contenido.

**Propuesta:** trabajar siempre en líneas. La página queda como metadato de validación post-hoc, no como anclaje primario. La detección de inicio/fin de fallo se hace buscando patrones textuales (carátula, firma, marcador editorial) directamente en el `.md`.

**Beneficio estimado:** elimina categóricamente dos clusters de bugs.

**Riesgo:** refactor profundo, requiere revalidación del pipeline entero.

**Decisión:** mantener arquitectura actual para esta tesis. Considerar para v18 si el proyecto continúa post-tesis.

---

### Refactor — parser de estructura editorial por secciones

**Estado:** propuesta para versión futura del pipeline.

**Idea:** detectar secciones editoriales del `.md` (portada → prólogo → fallos → índices → apéndices) como primer paso del pipeline, y parsear cada sección con lógica específica. Reemplaza heurísticas puntuales de delimitación por arquitectura explícita.

**Decisión:** propuesta para v18, no v17.x. Mismo razonamiento que el refactor anterior.

---

### Snapshots: cubrir todo archivo modificable

**Lección de la sesión 2/5/2026:** el snapshot inicial solo cubrió archivos de raíz, no de `paginas/`. Cuando se aplicó el fix Bug D al script de `paginas/`, el original quedó sobrescrito sin backup. Quedó recuperable solo a través del diff registrado en la sesión.

**Convención adoptada:** antes de modificar archivo X, copiar X al snapshot del día. No asumir que el snapshot inicial cubre todo.

---

## Universo de huérfanos esperado post-fix Bug D

Si se confirma la validación, el desglose post-fix sería:

| Status | Casos | Cluster |
|--------|------:|---------|
| `pagina_no_en_mapa` | 43 | Bug A (activo) |
| `fallo_cruza_archivos` | 27 | Bug B (activo) |
| `pagina_fin_no_en_mapa` | 0-? | Bug C (en validación) |
| Total huérfanos esperado | 70 | |

Cobertura procesada esperada: 5862 - 70 = **5792 casos delimitados correctamente** (asumiendo parser exitoso sobre todos).

---

## Roadmap de fixes restantes (orden sugerido)

1. **Validar Bug D** (próxima sesión, prioridad alta).
2. **Confirmar diagnóstico de Bug C** (¿catálogo v15 lo resolvió?).
3. **Bug B — `fallo_cruza_archivos`** (fix barato, ~30-45 min).
4. **Bug A — `pagina_no_en_mapa`** (fix mediano, 1-3 horas, riesgo medio).
5. **Cluster fallos breves sin causa documentada** (investigación, prioridad baja).
6. **Reorganización del proyecto** (sesión dedicada, prioridad media).
7. **Refactor v18** (post-tesis si corresponde).
