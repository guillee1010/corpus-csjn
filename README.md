# corpus-csjn

[![DOI](https://img.shields.io/badge/DOI-10.7910%2FDVN%2FTJTVKW-blue)](https://doi.org/10.7910/DVN/TJTVKW)

Pipeline de extracción y análisis de fallos de la Corte Suprema de Justicia de la Nación (CSJN), Argentina, tomos 329–349 (período 2006–2026).

Producto base de la tesis de Maestría en Argumentación Jurídica (UBA), director Dr. Eugenio Sarrabayrouse: *"Diseño institucional y estrategia en la decisión judicial colegiada"*.

## Dataset publicado

El corpus está disponible como dataset académico de acceso libre:

> **Rubinetti, Guillermo (2026).** *corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings, Volumes 329–349 (2006–2026).* Harvard Dataverse. <https://doi.org/10.7910/DVN/TJTVKW>

Licencia: CC-BY 4.0.

> **Nota de versión.** La versión publicada en Dataverse es un *snapshot* anterior (parser v18.15, previo al refactor M26 del eje admisión/mérito). El pipeline y los outputs de este repositorio están más avanzados (parser **v24.0**): el eje de mérito se unificó, `causa_inadmisibilidad` se movió a la capa deriver y se agregaron los derivers de materia y partes. La republicación del dataset a Dataverse con el estado v24.0 está pendiente (re-validación de confiabilidad en curso). Hasta entonces, para reproducibilidad exacta contra el DOI usar el snapshot publicado; para el estado vigente, este repositorio.

## Qué es

Un pipeline en Python que toma los `.md` de los Tomos de Fallos de la CSJN (publicación oficial de la Secretaría de Jurisprudencia) y produce un dataset estructurado con metadatos por fallo, organizado en ejes analíticos separados:

- **Composición y voto:** firmantes, `voting_pattern` (unánime, disidencia, según su voto, mixed), número de jueces / titulares / disidencias, votos individuales denormalizados.
- **Eje de mérito (SCDB-equivalente):** `is_merit_decision` — si la Corte revisó el fondo — derivado del gate del clasificador como fuente única, con `is_originaria` como rama propia.
- **Eje de disposición:** `disposicion` (multiclass fino: revoca, confirma, deja sin efecto, nulidad, no-fondo, no-revisión, etc.).
- **Eje de admisibilidad / gatekeeping:** `admisibilidad` (admite / inadmite / no aplica) y `causa_inadmisibilidad` (vocabulario controlado: por qué la Corte no entra al fondo).
- **Vía y queja:** `via_recurso` (extraordinario / ordinario), `es_queja`, `queja_resultado`.
- **Cuestión federal, materia, partes:** `tipo_cuestion_federal`; `materia` inferida; recurrente/recurrido y sus roles; tribunal de origen; fecha; y zonas de texto (dictamen, considerandos, parte dispositiva, firma).

El objetivo metodológico es producir el equivalente argentino del [Supreme Court Database (SCDB)](http://scdb.wustl.edu/) para análisis cuantitativo de patrones de decisión de la CSJN.

## Estado actual

- **Versión del parser:** v24.0
- **Universo procesable:** 19 tomos (329–349, excluidos 335 y 336 por OCR no legible)
- **Casos:** 5.890 (5.697 fallos + 160 sumarios con link a fallo + 33 sumarios editoriales)
- **Votos individuales:** 27.697
- **Zonas de texto:** 141.451
- **Zonas editoriales:** 152
- **Manifiesto:** `_manifest.json` sella 64 artefactos `[CLEAN]`

Versiones de la cadena (pre-flight `correr_pipeline.py`): parser `24.0` · extraer_epilogos `0.3` · derivar_partes `0.17` · derivar_materia `3.2` · derivar_recursos `0.6` · clasificador_disposicion `1.15` · clasificador_via `0.1` · clasificador_admision `0.2` · clasificador_causa `0.5` · generar_manifiesto `1.8`.

### Eje de mérito (SCDB-equivalente)

Tras el cierre de M39 (paso 3, H178), `is_merit_decision` se deriva del gate del clasificador (`es_revision_fondo`) como fuente única para todo el corpus; la divergencia entre ambas capas es **0 por construcción**.

`is_merit_decision = 1`: **2.935** (49,8 %) · `= 0`: 2.955 (50,2 %) — idéntico a `es_revision_fondo = si`: 2.935.
`is_originaria = 1`: **589** (10,0 %).

### Disposición (`disposicion`) — eje de mérito canónico

Derivado por `derivar_recursos` / `clasificador_disposicion`. Distribución sobre los 5.890 casos (11 valores):

`no_fondo` 1862 · `deja_sin_efecto` 1353 · `revoca` 904 · `no_revision_competencia` 587 · `confirma` 537 · `no_revision_procesal` 356 · `no_revision_demanda` 181 · `nulidad` 56 · `nulidad_concesion` 41 · `grant_remand_implicito` 10 · `modifica` 3.

### Admisibilidad y gatekeeping

`admisibilidad`: `admite` 2886 (49,0 %) · `sin_marcador` 1332 (22,6 %) · `inadmite` 1109 (18,8 %) · `no_aplica` 563 (9,6 %).

`causa_inadmisibilidad` — separa el **gate** (por qué la Corte no entra al fondo) de la **acción** (`disposicion`). Vocabulario controlado, anclado al recurso efectivamente decidido. Distribución (14 valores):

`INADMISIBLE_SIN_CAUSAL_EXPLICITA` 467 (gate sin causal nominada) · `ART_280` 229 · `INADMISIBLE_REMITE_DICTAMEN` 165 · `CUESTION_ABSTRACTA` 93 · `ACORDADA_4_2007` 51 · `FALTA_SENTENCIA_DEFINITIVA` 43 · `CADUCIDAD_INSTANCIA` 13 · `RESOLUCION_NO_RECURRIBLE` 12 · `FALTA_FUNDAMENTACION_AUTONOMA` 12 · `DESISTIMIENTO` 10 · `FUERA_DE_TERMINO` 10 · `INTERPOSICION_INCORRECTA` 2 · `DEPOSITO_PREVIO` 2 · vacío 4.781 (no-gate / fondo).

Invariante (post-M26): `causa_inadmisibilidad != "" ⇔ admisibilidad = inadmite` (**1.109** casos, 18,8 %).

### Vía y queja

`via_recurso`: `recurso_extraordinario` 3371 (57,2 %) · `recurso_ordinario` 327 (5,6 %) · vacío 2192.
`es_queja = 1`: 2.297 (39,0 %). `queja_resultado` (sobre las quejas): `hace_lugar` 1211 · `desestima` 524 · `procedente` 173 · `admisible` 101 · resto ≤ 25.

### Materia (inferida)

`derivar_materia` (capa 1 tribunal→fuero + capa 2 sobre considerando). 14 valores:

`civil_comercial` 1001 · `contencioso_administrativo` 925 · `penal` 686 · `laboral` 455 · `previsional` 357 · `tributario` 349 · `ambiental` 53 · `constitucional` 33 · `electoral` 29 · `salud` 20 · `consumo` 17 · `cambiario` 8 · `lesa_humanidad` 3 · vacío 1.954 (33,2 %; cobertura parcial, `pendiente_capa2` 1158).

### Partes (recurrente / recurrido)

`derivar_partes` (deriva del epílogo + carátula). Rol del recurrente (11 valores): `actora` 590 · `demandada` 515 · `penal` 389 · `mp_fiscal` 84 · `por_derecho_propio` 46 · `codemandada` 34 · `querellante` 24 · `mp_defensa` 14 · `solo_letrado` 9 · `coactora` 7 · sin rol 4.178. Cobertura del epílogo (`csjn_casos_epilogo.csv`): `ok` 4.434 / 5.697 fallos (77,8 %).

### Outcome (legacy)

`outcome` es el campo plano heredado, **congelado como legacy** tras el refactor M26 (los ejes canónicos son `disposicion` + `admisibilidad` + `causa_inadmisibilidad`). Se conserva por continuidad. Distribución (23 valores):

`hace_lugar` 1400 · `competencia` 925 · `desestima` 806 · `procedente` 759 · `otro` 359 · `confirma` 345 · `revoca` 340 · `rechaza` 278 · `abstracto` 149 · `deja_sin_efecto` 82 · `nulidad` 42 · `mal_concedido` 39 · `nulidad_concesion` 31 · `sin_dispositivo` 26 · `inadmisible_280` 24 · `inadmisible` 23 · `improcedente` 23 · `caducidad` 14 · `desierto` 12 · `desistimiento` 10 · `cautelar` 5 · `inadmisible_acordada_4` 5 (+ 193 sumarios sin dispositivo propio).

### Voting pattern

`unanime` 3529 (59,9 %) · `disidencia` 1113 (18,9 %) · `segun_su_voto` 746 (12,7 %) · `mixed` 293 (5,0 %) · `sin_firma` 16 (+ 193 sumarios).

## Estructura del repositorio

```
corpus-csjn/
├── README.md                          ← este archivo
├── DEUDA_TECNICA.md                   ← deuda técnica y bugs activos
├── BITACORA.md                        ← log cronológico de sesiones (H001–H179+)
├── CHANGELOG.md                       ← cambios versionados al pipeline
├── MAPA.md                            ← mapa de arquitectura + orden de ejecución (spec del DAG)
├── scripts/
│   ├── pipeline/                      ← pipeline productivo
│   │   ├── correr_pipeline.py         ← orquestador de la cadena (v1.0)
│   │   ├── parser.py                  ← parser principal (v24.0)
│   │   ├── parser_editorial.py        ← parser de zonas editoriales (librería)
│   │   ├── construir_catalogo.py      ← genera catálogo
│   │   ├── cruzar_catalogo_y_mapa.py  ← localizador
│   │   ├── detectar_paginas.py        ← detecta headers de página
│   │   ├── extraer_epilogos.py        ← extrae epílogos (v0.3)
│   │   ├── derivar_partes.py          ← recurrente/recurrido (v0.17)
│   │   ├── derivar_materia.py         ← materia inferida (v3.2)
│   │   ├── derivar_recursos.py        ← disposición/admisibilidad/causa/vía (v0.6)
│   │   ├── clasificador_disposicion.py ← lógica de disposición/mérito (v1.15, librería)
│   │   ├── clasificador_admision.py   ← lógica de admisibilidad (v0.2, librería)
│   │   ├── clasificador_causa.py      ← lógica de causa de inadmisibilidad (v0.5, librería)
│   │   └── clasificador_via.py        ← lógica de vía del recurso (v0.1, librería)
│   ├── validacion/                    ← regresión, κ y sellado
│   │   ├── check_regresion.py         ← harness de regresión (golden)
│   │   ├── kappa_confiabilidad.py     ← κ inter-codificador (n300)
│   │   └── generar_manifiesto.py      ← sella _manifest.json (v1.8)
│   ├── auditoria/                     ← auditor canónico
│   │   └── auditar_fallo.py           ← auditor canónico
│   └── diagnostico/                   ← herramientas y PoCs por sesión
│       ├── extraer_caso.py            ← extrae considerando+por_ello de un fallo
│       └── H0NN/                      ← PoCs y diagnósticos por sesión
├── output/
│   ├── parser/                        ← outputs canónicos del parser + derivers
│   │   ├── csjn_casos.csv             ← dataset de casos (5.890 · 39 columnas)
│   │   ├── csjn_casos_textos.csv      ← blobs de texto crudos (considerando/por_ello/firma)
│   │   ├── csjn_casos_votos.csv       ← votos individuales (27.697)
│   │   ├── csjn_casos_zonas.csv       ← zonas de texto por caso (141.451)
│   │   ├── csjn_casos_editorial.csv   ← zonas editoriales por tomo (152)
│   │   ├── csjn_casos_epilogo.csv     ← epílogos extraídos (deriver)
│   │   ├── csjn_casos_partes.csv      ← recurrente/recurrido (deriver)
│   │   ├── csjn_casos_materia.csv     ← materia inferida (deriver)
│   │   └── csjn_casos_recursos.csv    ← disposición/admisibilidad/causa/vía (deriver)
│   ├── mapa/mapa_paginas.csv          ← mapa de páginas por tomo
│   ├── localizacion/fallos_localizados.csv ← localización de fallos
│   └── catalogo/                      ← catálogo + lookup de aparatos editoriales
├── corpus/                            ← .md fuente de los Tomos (sólo lectura)
└── archivo/                           ← versiones anteriores y material deprecado
```

## Pipeline: cadena y orquestador

El grafo de dependencias `consume → produce` y el orden topológico completo viven en **`MAPA.md`** (fuente única del DAG). En resumen, el orden de ejecución es:

```
corpus/*.md
    ↓
[1] construir_catalogo.py      → catalogo.csv, secciones_indices.csv
[2] detectar_paginas.py        → mapa_paginas.csv
[3] cruzar_catalogo_y_mapa.py  → fallos_localizados.csv
[4] parser.py                  → csjn_casos.csv (+ _textos, _votos, _zonas, _editorial)
[5] extraer_epilogos.py        → csjn_casos_epilogo.csv
[6] derivers (dependen de parser):
      derivar_partes.py        → csjn_casos_partes.csv
      derivar_materia.py       → csjn_casos_materia.csv
      derivar_recursos.py      → csjn_casos_recursos.csv   (importa los clasificadores)
[7] generar_manifiesto.py      → _manifest.json (sella, último paso)
```

Los **clasificadores** (`disposicion`, `admision`, `causa`, `via`) son librerías sin `__main__`: no producen CSV propio, los importa `derivar_recursos`. La etapa con I/O es el deriver; los clasificadores son su lógica.

El orquestador **`correr_pipeline.py`** (v1.0, H179) corre la cadena canónica en orden (`parser → epilogos → derivers → check_regresion → manifest`) con `MAPA.md` como especificación, verificación de versiones en pre-flight, gate de corpus-drift y assert de golden. La etapa upstream (catálogo / páginas / cruce) queda fuera de la v1 del orquestador y se corre a mano cuando hay tomos nuevos.

## Decisiones metodológicas relevantes

- **Tomos 335 y 336 excluidos** por imposibilidad de OCR (firmas hológrafas en lugar de texto). Decisión de soporte material, no limitación del pipeline. El gate de corpus-drift del orquestador los detecta y aborta salvo `--ignorar-corpus-drift` (exclusión deliberada).
- **Etapas standalone + orquestador acotado**: cada script se puede invocar manualmente (trazabilidad por etapa); `correr_pipeline.py` cablea la cadena parser→derivers→sello sin tocar upstream.
- **Validación incremental**: snapshots antes de cada cambio, diff post-cambio, spot-check sobre casos recuperados. Un fix por vez. Golden + `check_regresion` + `_manifest.json` sellan el estado.
- **Versionado por `__version__`**: cada script canónico tiene versión interna. Minor sube en .01 por fix; major sube solo con cambio de arquitectura. Git versiona los archivos de datos (sin sufijos de versión en nombres de archivo).
- **Principio REE**: Robusto, Escalable, Elegante. No asumir, verificar con datos; nunca declarar limpio sin demostrarlo en disco.

## Referencias del proyecto a la tesis

El dataset producido alimenta los capítulos 3 y 4 de la tesis (análisis cuantitativo de patrones de mayoría, frecuencia de concurrencias y disidencias, evolución por composición de la Corte). Hipótesis cubiertas:

- **H3**: ausencia de incentivos institucionales para opinión unificada → promueve concurrencias y disidencias, impidiendo la formación de ratio decidendi unificada.
- **H4**: permanencia efectiva de secretarías letradas → memoria institucional acumulada en la burocracia.
- **H5**: autonomía relativa de la burocracia letrada respecto del cuerpo ministerial.

Para deuda técnica del pipeline, ver `DEUDA_TECNICA.md`. Para historial de sesiones y hallazgos, ver `BITACORA.md`. Para la arquitectura del DAG y el orden de ejecución, ver `MAPA.md`.
