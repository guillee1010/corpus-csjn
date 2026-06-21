# scripts/pipeline/

La tubería viva que produce el dataset (`output/parser/`). Cada script lleva su
`__version__` embebido; el sello de versiones de la última corrida está en
`output/parser/_manifest.json`.

## Etapas (en orden de ejecución)

| Script | Ver. | Consume | Produce |
|---|---|---|---|
| `detectar_paginas.py` | 1.01 | `corpus/*.md` | `output/mapa/mapa_paginas.csv` — mapa de páginas (límites, números, estructura de tomo) |
| `construir_catalogo.py` | 1.01 | índice de partes de cada tomo | `output/catalogo/{catalogo,secciones_indices}.csv` — casos esperados + refs de página |
| `cruzar_catalogo_y_mapa.py` | 1.0 | catálogo + mapa | `output/localizacion/fallos_localizados.csv` — rango de líneas por fallo |
| `parser.py` | 22.0 | `corpus/` + localización | `csjn_casos · _textos · _votos · _zonas · _editorial` — motor de extracción principal (carátula, fecha, jueces, posiciones, zonas, texto) |
| `parser_editorial.py` | 1.0 | `corpus/` | `csjn_editorial_indice_partes.csv` — secciones editoriales (índice de partes) |
| `derivar_materia.py` | 3.2 | `csjn_casos` + `_meta/vocab_materia/` | `csjn_casos_materia.csv` |
| `derivar_recursos.py` | 0.5 | `csjn_casos` | `csjn_casos_recursos.csv` — ejes M26; orquesta los `clasificador_*` |

## Clasificadores (submódulos de `derivar_recursos`)

Cada uno resuelve **un eje** de `csjn_casos_recursos.csv`. *(Rol confirmado por el
manifest / nombre de eje; la heurística interna de cada uno no está documentada acá —
leer el script para el detalle.)*

| Script | Ver. | Eje |
|---|---|---|
| `clasificador_disposicion.py` | 1.08 | `disposicion` (+ `reenvia`) |
| `clasificador_via.py` | 0.1 | `via_recurso` |
| `clasificador_admision.py` | 0.2 | `admisibilidad` |
| `clasificador_causa.py` | 0.3 | `causa_inadmisibilidad` |

## Herramientas / otros

- **`generar_manifiesto.py`** (1.6) — produce `output/parser/_manifest.json` (hashes,
  filas, versión de cada generador). No genera dataset; es la herramienta de provenance.
- **`extraer_recuperados_H109.py`** — script *one-off* de recuperación (sesión H109);
  no figura en el manifest. Candidato a `archivo/`. *(Rol inferido del nombre — sin leer.)*

---
*Altitud: interfaz (rol + IO + versión + comando). La lógica interna de cada script no se
reproduce acá por diseño; vive en el código y en `BITACORA.md` / `DEUDA_TECNICA.md`.*
