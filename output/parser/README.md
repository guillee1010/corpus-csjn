# output/parser/

Outputs canónicos del pipeline. **Son el dataset** — lo que se publica en Dataverse.
Un CSV por dimensión. Clave de join entre tablas: `caso_id_canonico`.

| Archivo | Filas | Generador | Qué es |
|---|---|---|---|
| `csjn_casos.csv` | 5.890 | `parser.py` 22.0 | Nivel **caso**: carátula (índice y cuerpo), fecha, tomo, `apertura_tipo`, `voting_pattern`, `n_jueces`, word-counts por zona, firma, jueces, posiciones, `tribunal_origen`, localización. *(`outcome` presente pero **legacy** — superado por los ejes de `recursos`.)* |
| `csjn_casos_textos.csv` | 5.890 | `parser.py` 22.0 | Texto completo por caso (tabla pesada, ~32 MB). |
| `csjn_casos_votos.csv` | 27.697 | `parser.py` 22.0 | Nivel **voto** (un registro por juez por caso): posición, texto del voto, `tipo_voto_sep`, `fragmenta_ratio`, `punto_divergencia`. |
| `csjn_casos_zonas.csv` | 141.451 | `parser.py` 22.0 | Zonas de texto por caso: `zona` (sumario, dictamen, considerando, dispositiva, voto…), segmento, rangos de línea, word-count. |
| `csjn_casos_editorial.csv` | 152 | `parser.py` 22.0 | Zonas editoriales por tomo (`indice_partes`, `indice_materias`) con rangos de línea y word-count. |
| `csjn_editorial_indice_partes.csv` | 11.445 | `parser_editorial.py` 1.0 | Entradas parseadas del índice alfabético de partes de cada tomo. |
| `csjn_casos_materia.csv` | 5.890 | `derivar_materia.py` 3.2 | Materia por caso (derivada vía `_meta/vocab_materia/`). |
| `csjn_casos_recursos.csv` | 5.890 | `derivar_recursos.py` 0.5 | **Ejes recursivos M26** (un registro por caso): `disposicion`, `reenvia`, `parte_ganadora`, `via_recurso`, `multi_recurso`, `es_revision_fondo`, `admisibilidad`, `causa_inadmisibilidad`, `es_queja`. Usa los `clasificador_{disposicion,via,admision,causa}`. |

## Provenance

Según `_manifest.json` (schema v4):

```
corpus/ (46 vols, 329–349 excl. 335–336)
  ├─ detectar_paginas      → output/mapa/mapa_paginas.csv         ┐ intermedios
  ├─ construir_catalogo    → output/catalogo/{catalogo,secciones} │ regenerables
  └─ cruzar_catalogo_y_mapa→ output/localizacion/fallos_localizados.csv ┘ (gitignored)
corpus + localizacion
  ├─ parser.py 22.0        → csjn_casos · _textos · _votos · _zonas · _editorial
  └─ parser_editorial 1.0  → csjn_editorial_indice_partes
csjn_casos
  ├─ derivar_materia 3.2 (+ _meta/vocab_materia) → csjn_casos_materia
  └─ derivar_recursos 0.5 (+ clasificador_*)     → csjn_casos_recursos
```

## Convenciones

- **Encoding:** UTF-8.
- **Versionado:** sin sufijos de versión en los nombres — git versiona; el sello de
  hashes / filas / versión-de-generador vive en `_manifest.json`.
- **Cobertura:** volúmenes 329–349, **excluyendo 335–336** (OCR pendiente; ver CODEBOOK §11).

---
*Reemplaza a `scripts/pipeline/readme_output_parser.md` (stale: documentaba 5 CSV con cuentas viejas).*
