# corpus-csjn

[![DOI](https://img.shields.io/badge/DOI-10.7910%2FDVN%2FTJTVKW-blue)](https://doi.org/10.7910/DVN/TJTVKW)

Pipeline de extracción y análisis de fallos de la Corte Suprema de Justicia de la Nación (CSJN), Argentina, tomos 329–349 (período 2006–2026).

Producto base de la tesis de Maestría en Argumentación Jurídica (UBA), director Dr. Eugenio Sarrabayrouse: *"Diseño institucional y estrategia en la decisión judicial colegiada"*.

## Dataset publicado

El corpus está disponible como dataset académico de acceso libre:

> **Rubinetti, Guillermo (2026).** *corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings, Volumes 329–349 (2006–2026).* Harvard Dataverse. <https://doi.org/10.7910/DVN/TJTVKW>

Licencia: CC-BY 4.0.

> **Nota de versión.** La versión publicada en Dataverse es un *snapshot* anterior (parser v18.15, previo al refactor M26 del eje admisión/mérito). Este repositorio está en el parser **v43.3**, con la capa de recursos (disposición, mérito, admisibilidad, vía), los derivers de materia, partes y normas, las correcciones de firma y voto de H223-H226 y la validación externa contra la base de sumarios de la Corte (H224). La republicación del dataset en Dataverse está pendiente. Hasta entonces, para reproducibilidad exacta contra el DOI usar el snapshot publicado; para el estado vigente, este repositorio.

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

- **Versión del parser:** v43.3
- **Universo procesable:** 19 tomos (329–349, excluidos 335 y 336 por OCR no legible)
- **Casos:** 5.894 (5.703 fallos + 157 sumarios con link a fallo + 34 sumarios editoriales)
- **Votos individuales:** 27.938
- **Zonas de texto:** 138.062
- **Zonas editoriales:** 152
- **Normas citadas:** 13.911
- **Manifiesto:** `_manifest.json` sella 65 artefactos `[CLEAN]` (regolden H226)

Versiones de la cadena: parser `43.3` · extraer_epilogos `0.4` · extraer_normas `1.1` · derivar_partes `0.18` · derivar_materia `4.1` · derivar_recursos `0.6` · clasificador_disposicion `1.18` · clasificador_via `0.1` · clasificador_admision `0.2` · clasificador_causa `0.5` · generar_manifiesto `1.9` · correr_pipeline `1.1`.

### Validación

La validación principal es un censo contra la base de sumarios de la Secretaría de Jurisprudencia de la Corte (sjconsulta), un codificador externo e independiente del pipeline (CODEBOOK §9.1).

| Variable | N | Acuerdo | κ |
|---|---|---|---|
| Posición de cada juez | 10.301 posiciones en 2.480 fallos | 99,7 % | **0,988** |
| Mérito (fondo / no fondo) | 2.984 | 96,3 % | **0,916** |
| Disposición | 3.126 | 93,7 % | **0,914** |
| Queja | 2.549 | 93,7 % | **0,868** |
| Vía del recurso | 2.549 | 91,5 % | 0,606 |

La vía tiene una brecha de detección (186 fallos sin vía en el corpus que SJ registra como extraordinario u ordinario). Parte ganadora y reenvío no tienen contraparte en SJ; para esas dos variables vale la validación manual previa sobre una muestra de 300 fallos (κ 0,804 y 0,458, este último no reportable; CODEBOOK §9).

### Eje de mérito (SCDB-equivalente)

Tras el cierre de M39 (paso 3, H178), `is_merit_decision` se deriva del gate del clasificador (`es_revision_fondo`) como fuente única para todo el corpus; la divergencia entre ambas capas es **0 por construcción**.

`is_merit_decision = 1`: **2.969** (50,4 %) · `= 0`: 2.925 (49,6 %), idéntico a `es_revision_fondo = si`: 2.969.
`is_originaria = 1`: **596** (10,1 %).

### Disposición (`disposicion`), eje de mérito canónico

Derivado por `derivar_recursos` / `clasificador_disposicion`. Distribución sobre los 5.894 casos (11 valores):

`no_fondo` 1838 · `deja_sin_efecto` 1366 · `revoca` 910 · `no_revision_competencia` 590 · `confirma` 541 · `no_revision_procesal` 356 · `no_revision_demanda` 181 · `nulidad` 57 · `nulidad_concesion` 42 · `grant_remand_implicito` 9 · `modifica` 4.

### Admisibilidad y gatekeeping

`admisibilidad`: `admite` 2888 (49,0 %) · `sin_marcador` 1320 (22,4 %) · `inadmite` 1116 (18,9 %) · `no_aplica` 570 (9,7 %).

`causa_inadmisibilidad` separa el **gate** (por qué la Corte no entra al fondo) de la **acción** (`disposicion`). Vocabulario controlado, anclado al recurso efectivamente decidido. Distribución (13 valores):

`INADMISIBLE_SIN_CAUSAL_EXPLICITA` 467 (gate sin causal nominada) · `ART_280` 231 · `INADMISIBLE_REMITE_DICTAMEN` 170 · `CUESTION_ABSTRACTA` 93 · `ACORDADA_4_2007` 51 · `FALTA_SENTENCIA_DEFINITIVA` 43 · `CADUCIDAD_INSTANCIA` 13 · `RESOLUCION_NO_RECURRIBLE` 12 · `FALTA_FUNDAMENTACION_AUTONOMA` 12 · `DESISTIMIENTO` 10 · `FUERA_DE_TERMINO` 10 · `INTERPOSICION_INCORRECTA` 2 · `DEPOSITO_PREVIO` 2 · vacío 4.778 (no-gate / fondo).

Invariante (post-M26): `causa_inadmisibilidad != "" ⇔ admisibilidad = inadmite` (**1.116** casos, 18,9 %; se cumple en los 5.894).

### Vía y queja

`via_recurso`: `recurso_extraordinario` 3382 (57,4 %) · `recurso_ordinario` 327 (5,5 %) · vacío 2185.
`es_queja = 1`: 2.301 (39,0 %). `queja_resultado` (sobre las quejas): `hace_lugar` 1217 · `desestima` 525 · `procedente` 182 · `admisible` 101 · `agreguese` 30 · resto ≤ 19 · vacío 183.

### Materia (inferida)

`derivar_materia` (lectura del tribunal de origen, del texto y del dictamen, más originarias). 15 valores:

`civil_comercial` 999 · `contencioso_administrativo` 933 · `penal` 680 · `laboral` 475 · `previsional` 354 · `tributario` 350 · `ambiental` 58 · `constitucional` 29 · `electoral` 29 · `consumo` 29 · `salud` 18 · `cambiario` 7 · `lesa_humanidad` 3 · `penal_tributario` 2 · `penal_cambiario` 2 · vacío 1.926 (32,7 %; `sin_clasificar` 1.125, `no_aplica` 191).

### Partes (recurrente / recurrido)

`derivar_partes` (deriva del epílogo + carátula). Rol del recurrente (10 valores): `actora` 590 · `demandada` 514 · `penal` 392 · `mp_fiscal` 89 · `por_derecho_propio` 44 · `codemandada` 35 · `querellante` 25 · `mp_defensa` 14 · `solo_letrado` 10 · `coactora` 7 · sin rol 4.174. Cobertura del epílogo (`csjn_casos_epilogo.csv`): `ok` 4.421 / 5.703 fallos (77,5 %).

### Outcome (legacy)

`outcome` es el campo plano heredado, **congelado como legacy** tras el refactor M26 (los ejes canónicos son `disposicion` + `admisibilidad` + `causa_inadmisibilidad`). Se conserva por continuidad. Distribución (22 valores):

`hace_lugar` 1402 · `competencia` 932 · `desestima` 809 · `procedente` 757 · `confirma` 350 · `otro` 347 · `revoca` 341 · `rechaza` 284 · `abstracto` 149 · `deja_sin_efecto` 82 · `nulidad` 42 · `mal_concedido` 38 · `nulidad_concesion` 32 · `inadmisible_280` 24 · `inadmisible` 23 · `improcedente` 23 · `sin_dispositivo` 21 · `caducidad` 15 · `desierto` 12 · `desistimiento` 10 · `cautelar` 5 · `inadmisible_acordada_4` 5 (+ 191 sumarios sin dispositivo propio).

### Voting pattern y posiciones

`unanime` 3507 (59,5 %) · `disidencia` 1121 (19,0 %) · `segun_su_voto` 762 (12,9 %) · `mixed` 305 (5,2 %) · `sin_firma` 8 (+ 191 sumarios).

`posicion` (votos): `mayoria` 24.096 · `según su voto` 1.579 · `en disidencia` 2.026 · `en disidencia parcial` 237. Fuente, la firma impresa completada por el encabezado del voto (desde v43.3). Las posiciones que un juez expresa solo dentro del voto común no se codifican (B179, CODEBOOK §11).

## Estructura del repositorio

```
corpus-csjn/
├── README.md                          ← este archivo
├── DEUDA_TECNICA.md                   ← deuda técnica y bugs activos
├── BITACORA.md                        ← log cronológico de sesiones (H001–H226)
├── CHANGELOG.md                       ← cambios versionados al pipeline
├── MAPA.md                            ← mapa de arquitectura + orden de ejecución (spec del DAG)
├── CODEBOOK.md                        ← diccionario de variables, valores, validación y limitaciones
├── scripts/
│   ├── pipeline/                      ← pipeline productivo + orquestador + sello
│   │   ├── correr_pipeline.py         ← orquestador de la cadena (v1.1)
│   │   ├── parser.py                  ← parser principal (v43.3)
│   │   ├── parser_editorial.py        ← zonas editoriales (librería)
│   │   ├── construir_catalogo.py      ← catálogo (etapa de localización)
│   │   ├── detectar_paginas.py        ← mapa de páginas (etapa de localización)
│   │   ├── cruzar_catalogo_y_mapa.py  ← localizador (etapa de localización)
│   │   ├── extraer_epilogos.py        ← extrae epílogos (v0.4)
│   │   ├── extraer_normas.py          ← normas citadas (v1.1)
│   │   ├── derivar_partes.py          ← recurrente/recurrido (v0.18)
│   │   ├── derivar_materia.py         ← materia inferida (v4.1)
│   │   ├── derivar_recursos.py        ← disposición/admisibilidad/causa/vía (v0.6)
│   │   ├── clasificador_disposicion.py ← lógica de disposición/mérito (v1.18, librería)
│   │   ├── clasificador_admision.py   ← lógica de admisibilidad (v0.2, librería)
│   │   ├── clasificador_causa.py      ← lógica de causa de inadmisibilidad (v0.5, librería)
│   │   ├── clasificador_via.py        ← lógica de vía del recurso (v0.1, librería)
│   │   └── generar_manifiesto.py      ← sella output/parser/_manifest.json (v1.9)
│   ├── validacion/                    ← confiabilidad: censo contra sjconsulta + gold n300 (ver su README)
│   │   ├── cruce_sjconsulta.py        ← baja sjconsulta y cruza posiciones
│   │   ├── kappa_sjconsulta.py        ← κ de posiciones contra SJ
│   │   ├── kappa_disposicion_via_sj.py ← κ de disposición, mérito, vía y queja contra SJ
│   │   ├── kappa_confiabilidad.py     ← κ contra el gold n300
│   │   └── validar_m68.py · superficie_b177.py · superficie_b179.py
│   ├── analisis/                      ← análisis para la tesis (M67, secretarías)
│   ├── tests/                         ← harness de regresión + gates
│   │   ├── check_regresion.py         ← regresión contra el golden
│   │   └── test_*.py · gate_manifiesto.py · check_*.py
│   ├── auditoria/                     ← auditor canónico (+ PoCs por sesión)
│   │   └── auditar_fallo.py
│   ├── diagnostico/                   ← PoCs y diagnósticos por sesión (H0NN/, B0NN/)
│   │   └── extraer_caso.py            ← extrae considerando+por_ello de un fallo
│   ├── explorador/                    ← explorador Streamlit del corpus
│   └── visor/                         ← visor de auditoría
├── output/
│   ├── parser/                        ← outputs canónicos del parser + derivers
│   │   ├── csjn_casos.csv             ← dataset de casos (5.894 · 40 columnas)
│   │   ├── csjn_casos_textos.csv      ← blobs de texto crudos (considerando/por_ello/firma)
│   │   ├── csjn_casos_votos.csv       ← votos individuales (27.938)
│   │   ├── csjn_casos_zonas.csv       ← zonas de texto por caso (138.062)
│   │   ├── csjn_casos_editorial.csv   ← zonas editoriales por tomo (152)
│   │   ├── csjn_casos_epilogo.csv     ← epílogos extraídos (deriver)
│   │   ├── csjn_casos_normas.csv      ← normas citadas (13.911, extractor)
│   │   ├── csjn_casos_partes.csv      ← recurrente/recurrido (deriver)
│   │   ├── csjn_casos_materia.csv     ← materia inferida (deriver)
│   │   └── csjn_casos_recursos.csv    ← disposición/admisibilidad/causa/vía (deriver)
│   ├── validacion/                    ← resultados de κ, adjudicaciones y superficies
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
    extraer_normas.py          → csjn_casos_normas.csv
[6] derivers (dependen de parser; materia, además, de normas):
      derivar_partes.py        → csjn_casos_partes.csv
      derivar_materia.py       → csjn_casos_materia.csv
      derivar_recursos.py      → csjn_casos_recursos.csv   (importa los clasificadores)
[7] generar_manifiesto.py      → _manifest.json (sella, último paso)
```

Los **clasificadores** (`disposicion`, `admision`, `causa`, `via`) son librerías sin `__main__`: no producen CSV propio, los importa `derivar_recursos`. La etapa con I/O es el deriver; los clasificadores son su lógica.

El orquestador **`correr_pipeline.py`** (v1.1; v1.0 en H179) corre la cadena canónica en orden (`parser → epilogos → derivers → check_regresion → manifest`) con `MAPA.md` como especificación, verificación de versiones en pre-flight, gate de corpus-drift y assert de golden. La etapa upstream (catálogo / páginas / cruce) queda fuera de la v1 del orquestador y se corre a mano cuando hay tomos nuevos.

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
