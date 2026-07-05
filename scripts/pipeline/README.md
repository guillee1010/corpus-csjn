# scripts/pipeline/

La tubería viva que produce el dataset (`output/parser/`). Cada script lleva su
`__version__` embebido; el sello de versiones de la última corrida está en
`output/parser/_manifest.json`.

## Etapas (en orden de ejecución)

| Script | Ver. | Consume | Produce |
|---|---|---|---|
| `construir_catalogo.py` | 1.01 | índice de partes de cada tomo | `output/catalogo/{catalogo,secciones_indices}.csv` — casos esperados + refs de página |
| `detectar_paginas.py` | 1.01 | `corpus/*.md` (+ catálogo, opcional) | `output/mapa/mapa_paginas.csv` — mapa de páginas (límites, números, estructura de tomo) |
| `cruzar_catalogo_y_mapa.py` | 1.0 | catálogo + mapa | `output/localizacion/fallos_localizados.csv` — rango de líneas por fallo |
| `parser.py` | 24.0 | `corpus/` + localización | `csjn_casos · _textos · _votos · _zonas · _editorial` — motor de extracción principal (carátula, fecha, jueces, posiciones, zonas, texto) |
| `parser_editorial.py` | 1.0 | `catalogo.csv` | *librería importada por `parser.py` (sin `__main__`, ver ⚠ en MAPA.md); su CSV atribuido quedó fósil, fuera de canónicos (H167/M35)* |
| `extraer_epilogos.py` | 0.3 | `csjn_casos` + `_zonas` + `corpus/` | `csjn_casos_epilogo.csv` — texto crudo de la zona epílogo (M29) |
| `derivar_partes.py` | 0.17 | `csjn_casos` + `_epilogo` | `csjn_casos_partes.csv` — recurrente/recurrido + rol (M29) |
| `derivar_materia.py` | 3.2 | `csjn_casos` + `_textos` + `_meta/vocab_materia/` | `csjn_casos_materia.csv` |
| `derivar_recursos.py` | 0.6 | `csjn_casos` + `_textos` | `csjn_casos_recursos.csv` — ejes M26; orquesta los `clasificador_*` |

## Clasificadores (submódulos de `derivar_recursos`)

Cada uno resuelve **un eje** de `csjn_casos_recursos.csv`. *(Rol confirmado por el
manifest / nombre de eje; la heurística interna de cada uno no está documentada acá —
leer el script para el detalle.)*

| Script | Ver. | Eje |
|---|---|---|
| `clasificador_disposicion.py` | 1.15 | `disposicion` (+ `reenvia`) |
| `clasificador_via.py` | 0.1 | `via_recurso` |
| `clasificador_admision.py` | 0.2 | `admisibilidad` |
| `clasificador_causa.py` | 0.5 | `causa_inadmisibilidad` |

## Herramientas / otros

- **`correr_pipeline.py`** (1.0, M42/H179) — orquestador de la cadena canónica: corre
  parser → epilogos → partes → materia → recursos → `check_regresion` → manifest en el
  orden del DAG de MAPA.md, con fail-fast, verificación de versiones (`--plan` imprime
  la tabla viva — más confiable que las columnas Ver. de arriba), gate de corpus-drift
  y assert golden==producción. Ver MAPA.md §«Cómo correr la cadena».
- **`generar_manifiesto.py`** (1.8) — produce `output/parser/_manifest.json` (hashes,
  filas, versión de cada generador). No genera dataset; es la herramienta de provenance.

---
*Altitud: interfaz (rol + IO + versión + comando). La lógica interna de cada script no se
reproduce acá por diseño; vive en el código y en `BITACORA.md` / `DEUDA_TECNICA.md`.*
