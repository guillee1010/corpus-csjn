# corpus-csjn

Pipeline de extracción y análisis de fallos de la Corte Suprema de Justicia de la Nación (CSJN), Argentina, períodos 2007-2026.

Producto base de la tesis de Maestría en Argumentación Jurídica (UBA), director Dr. Eugenio Sarrabayrouse: *"Diseño institucional y estrategia en la decisión judicial colegiada"*.

## Qué es

Un pipeline que toma los `.md` de los Tomos de Fallos de la CSJN (publicación oficial de la Secretaría de Jurisprudencia) y produce un dataset estructurado con metadatos por fallo: composición de la mayoría, voting pattern (unánime, disidencia, según su voto, mixed), firmantes, outcome, word count, materia inferida, tribunal de origen, fecha.

El objetivo metodológico es producir el equivalente argentino del [Supreme Court Database (SCDB)](http://scdb.wustl.edu/) para análisis cuantitativo de patrones de decisión de la CSJN.

## Estado actual

- **Versión del parser:** v17beta
- **Versión del catálogo:** v15
- **Universo procesable:** 19 tomos (329-349, excluidos 335 y 336 por OCR no legible)
- **Fallos en catálogo:** 5862
- **Fallos parseados (último output):** 5819 → en validación tras fix Bug D (debe subir a ~5838+)
- **Cobertura:** ≥97,9% del universo procesable

## Estructura del repositorio

```
corpus-csjn/
├── README.md                          ← este archivo
├── DEUDA_TECNICA.md                   ← deuda y bugs activos
├── BITACORA.md                        ← log cronológico de hallazgos
├── CHANGELOG.md                       ← cambios versionados al pipeline
├── catalogo_v15.csv                   ← catálogo activo
├── secciones_indices_v14.csv          ← lookup de aparatos editoriales
├── construir_catalogo_v15.py          ← genera catálogo
├── csjnv17_beta.py                    ← parser principal
├── csjnv16.py, csjnv15.py, csjnv14.py ← versiones anteriores del parser
├── cruce_anuarios.py                  ← cruza corpus con anuarios CSJN
├── markdowns_v2/                      ← .md fuente de los Tomos (sólo lectura)
├── paginas/                           ← scripts y outputs intermedios
│   ├── detectar_paginas.py            ← detecta headers de página en .md
│   ├── cruzar_catalogo_y_mapa.py      ← localizador (catálogo + mapa)
│   ├── mapa_paginas.csv               ← output de detectar_paginas
│   ├── fallos_localizados.csv         ← output del cruce, input del parser
│   ├── fallos_localizados_huerfanos.csv
│   └── analisis_descriptivo.py
├── scripts/diagnosticos/              ← scripts ad-hoc de diagnóstico
├── snapshots/                         ← backups antes de cambios destructivos
└── historial/                         ← versiones obsoletas
```

## Pipeline de cuatro etapas

```
.md fuente
    ↓
[1] detectar_paginas.py        → mapa_paginas.csv
    ↓                            (en qué línea empieza cada página)
[2] construir_catalogo_v15.py  → catalogo_v15.csv
    ↓                            secciones_indices_v14.csv
    ↓                            (qué fallos existen + dónde empiezan los índices)
[3] cruzar_catalogo_y_mapa.py  → fallos_localizados.csv
    ↓                            fallos_localizados_huerfanos.csv
    ↓                            (qué archivo y qué líneas ocupa cada fallo)
[4] csjnv17_beta.py            → csjn_casos_v17beta_fix349.csv
                                 (dataset final con voting_pattern, firmas, etc.)
```

## Cómo correr el pipeline

Cada etapa es un script Python standalone invocado por línea de comando. No hay orquestador automático.

### Etapa 3: localización (con fix Bug D)

```powershell
cd C:\Users\guill\Proyectos\corpus-csjn\paginas
python cruzar_catalogo_y_mapa.py `
  ..\catalogo_v15.csv `
  mapa_paginas.csv `
  ..\markdowns_v2 `
  fallos_localizados.csv `
  ..\secciones_indices_v14.csv
```

El quinto argumento (`secciones_indices_v14.csv`) es opcional pero recomendado: activa el fix Bug D que recupera los últimos fallos de cada tomo cortando el bloque antes del aparato editorial de índices.

### Etapa 4: parsing

```powershell
cd C:\Users\guill\Proyectos\corpus-csjn
python csjnv17_beta.py
```

Configuración interna del parser (paths, etc.) en el header del script.

## Decisiones metodológicas relevantes

- **Tomos 335 y 336 excluidos** por imposibilidad de OCR (firmas hológrafas en lugar de texto). No es pérdida del pipeline, es decisión de soporte material.
- **Catálogo v15** corrige bias del v14 en detección de fin de fallo.
- **Sin orquestador automático**: cada script se invoca a mano. Decisión deliberada para mantener trazabilidad por etapa.
- **Validación incremental**: snapshots antes de cada cambio, diff post-cambio, spot-check sobre casos recuperados. Un fix por vez.

## Referencias del proyecto al output

El dataset producido alimenta los capítulos 3 y 4 de la tesis (análisis cuantitativo de patrones de mayoría, frecuencia de concurrencias y disidencias, evolución por composición de la Corte). Hipótesis cubiertas:

- **H3**: ausencia de incentivos institucionales para opinión unificada → promueve concurrencias y disidencias.
- **H4**: permanencia efectiva de secretarías letradas → memoria institucional acumulada.

Para detalles teóricos ver el documento de tesis. Para deuda técnica del pipeline, ver `DEUDA_TECNICA.md`. Para historial de hallazgos y diagnósticos, ver `BITACORA.md`.

## Versionado

Versiones del parser tienen sufijo numérico (`csjnv14.py`, `csjnv15.py`, etc.). Versiones obsoletas se mantienen en `historial/` para reproducibilidad de outputs anteriores. Cambios al pipeline se registran en `CHANGELOG.md`.
