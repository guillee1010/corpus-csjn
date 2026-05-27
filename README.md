# corpus-csjn

[![DOI](https://img.shields.io/badge/DOI-10.7910%2FDVN%2FTJTVKW-blue)](https://doi.org/10.7910/DVN/TJTVKW)

Pipeline de extracción y análisis de fallos de la Corte Suprema de Justicia de la Nación (CSJN), Argentina, tomos 329–349 (período 2006–2026).

Producto base de la tesis de Maestría en Argumentación Jurídica (UBA), director Dr. Eugenio Sarrabayrouse: *"Diseño institucional y estrategia en la decisión judicial colegiada"*.

## Dataset publicado

El corpus está disponible como dataset académico de acceso libre:

> **Rubinetti, Guillermo (2026).** *corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings, Volumes 329–349 (2006–2026).* Harvard Dataverse. <https://doi.org/10.7910/DVN/TJTVKW>

Licencia: CC-BY 4.0.

## Qué es

Un pipeline en Python que toma los `.md` de los Tomos de Fallos de la CSJN (publicación oficial de la Secretaría de Jurisprudencia) y produce un dataset estructurado con metadatos por fallo: composición de la mayoría, voting pattern (unánime, disidencia, según su voto, mixed), firmantes, outcome, word count, materia inferida, tribunal de origen, fecha, y zonas de texto (dictamen, considerandos, parte dispositiva).

El objetivo metodológico es producir el equivalente argentino del [Supreme Court Database (SCDB)](http://scdb.wustl.edu/) para análisis cuantitativo de patrones de decisión de la CSJN.

## Estado actual

- **Versión del parser:** v18.0
- **Universo procesable:** 19 tomos (329–349, excluidos 335 y 336 por OCR no legible)
- **Casos parseados:** 5.862
- **Votos individuales:** 27.463
- **Zonas de texto:** 140.956

## Estructura del repositorio

```
corpus-csjn/
├── README.md                          ← este archivo
├── DEUDA_TECNICA.md                   ← deuda técnica y bugs activos
├── BITACORA.md                        ← log cronológico de sesiones (H001–H032+)
├── CHANGELOG.md                       ← cambios versionados al pipeline
├── MAPA.md                            ← mapa de arquitectura
├── scripts/
│   ├── pipeline/                      ← pipeline productivo
│   │   ├── parser.py                  ← parser principal (v18.0)
│   │   ├── parser_editorial.py        ← parser de zonas editoriales (v1.0)
│   │   ├── construir_catalogo.py      ← genera catálogo (v1.0)
│   │   ├── cruzar_catalogo_y_mapa.py  ← localizador (v1.0)
│   │   └── detectar_paginas.py        ← detecta headers de página (v1.0)
│   └── auditoria/                     ← auditoría y diagnósticos
│       ├── auditar_fallo.py           ← auditor canónico (v1.0.0)
│       └── H0xx/                      ← diagnósticos por sesión
├── output/
│   ├── parser/                        ← outputs canónicos del parser
│   │   ├── csjn_casos.csv             ← dataset de casos (5.862)
│   │   ├── csjn_casos_votos.csv       ← votos individuales (27.463)
│   │   ├── csjn_casos_zonas.csv       ← zonas de texto por caso (140.956)
│   │   ├── csjn_casos_editorial.csv   ← zonas editoriales por tomo
│   │   └── csjn_editorial_indice_partes.csv ← índice alfabético de partes
│   ├── mapa/
│   │   └── mapa_paginas.csv           ← mapa de páginas por tomo
│   ├── localizacion/
│   │   └── fallos_localizados.csv     ← localización de fallos (5.862)
│   ├── catalogo/
│   │   ├── catalogo.csv               ← catálogo de fallos
│   │   └── secciones_indices.csv      ← lookup de aparatos editoriales
│   └── diagnostico/                   ← outputs de diagnóstico
├── corpus/                            ← .md fuente de los Tomos (sólo lectura)
└── archivo/                           ← versiones anteriores y material deprecado
    └── data/                          ← catálogos viejos
```

## Pipeline de cuatro etapas

```
.md fuente (corpus/)
    ↓
[1] detectar_paginas.py        → output/mapa/mapa_paginas.csv
    ↓                            (en qué línea empieza cada página)
[2] construir_catalogo.py      → output/catalogo/catalogo.csv
    ↓                            output/catalogo/secciones_indices.csv
    ↓                            (qué fallos existen + dónde empiezan los índices)
[3] cruzar_catalogo_y_mapa.py  → output/localizacion/fallos_localizados.csv
    ↓                            (qué archivo y qué líneas ocupa cada fallo)
[4] parser.py                  → output/parser/csjn_casos.csv
                                 output/parser/csjn_casos_votos.csv
                                 output/parser/csjn_casos_zonas.csv
```

Cada etapa es un script Python standalone. No hay orquestador automático (decisión deliberada para mantener trazabilidad por etapa).

## Decisiones metodológicas relevantes

- **Tomos 335 y 336 excluidos** por imposibilidad de OCR (firmas hológrafas en lugar de texto). Decisión de soporte material, no limitación del pipeline.
- **Sin orquestador automático**: cada script se invoca manualmente. Trazabilidad por etapa.
- **Validación incremental**: snapshots antes de cada cambio, diff post-cambio, spot-check sobre casos recuperados. Un fix por vez.
- **Versionado por `__version__`**: cada script canónico tiene versión interna. Minor sube en .01 por fix; major sube solo con cambio de arquitectura. Git versiona los archivos de datos (sin sufijos de versión en nombres de archivo).
- **Principio REE**: Robusto, Escalable, Elegante. No asumir, verificar con datos.

## Referencias del proyecto a la tesis

El dataset producido alimenta los capítulos 3 y 4 de la tesis (análisis cuantitativo de patrones de mayoría, frecuencia de concurrencias y disidencias, evolución por composición de la Corte). Hipótesis cubiertas:

- **H3**: ausencia de incentivos institucionales para opinión unificada → promueve concurrencias y disidencias, impidiendo la formación de ratio decidendi unificada.
- **H4**: permanencia efectiva de secretarías letradas → memoria institucional acumulada en la burocracia.
- **H5**: autonomía relativa de la burocracia letrada respecto del cuerpo ministerial.

Para deuda técnica del pipeline, ver `DEUDA_TECNICA.md`. Para historial de sesiones y hallazgos, ver `BITACORA.md`.
