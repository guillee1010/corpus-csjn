# output/parser/

Outputs canónicos del parser y de los derivers. Un CSV por dimensión del dataset;
el sello de hashes / filas / versión-de-generador de la última corrida vive en
`_manifest.json`.

| Archivo | Registros | Descripción |
|---------|-----------|-------------|
| `csjn_casos.csv` | 5.890 | Dataset a nivel caso (39 columnas): carátula (índice y cuerpo), fecha, tomo, `apertura_tipo`, `outcome` (legacy), `voting_pattern`, `is_merit_decision`, `is_originaria`, `es_queja`, `queja_resultado`, `tipo_cuestion_federal`, word counts por zona, jueces, posiciones, `tribunal_origen`, localización |
| `csjn_casos_textos.csv` | 5.890 | Blobs de texto crudos por caso (`considerando_text`, `por_ello_text`, `firma_raw`), espejo 1:1, sin truncar |
| `csjn_casos_votos.csv` | 27.697 | Dataset a nivel voto: un registro por juez por caso, con posición, `texto_voto`, `tipo_voto_sep`, `fragmenta_ratio`, `punto_divergencia` (`is_merit` denormalizado) |
| `csjn_casos_zonas.csv` | 141.451 | Zonas de texto por caso: `zona` (dictamen, considerando, dispositiva, firma, voto, etc.), `segmento`, rangos de línea, word count |
| `csjn_casos_editorial.csv` | 152 | Zonas editoriales por tomo: `subtipo`, rangos de línea y word count |
| `csjn_casos_epilogo.csv` | 5.697 | Texto crudo de la zona epílogo por fallo (deriver, M29) |
| `csjn_casos_partes.csv` | 5.890 | Recurrente / recurrido + rol (deriver, M29) |
| `csjn_casos_materia.csv` | 5.890 | Materia inferida (deriver: capa 1 tribunal→fuero + capa 2 sobre considerando) |
| `csjn_casos_recursos.csv` | 5.890 | Ejes M26 (deriver): `disposicion`, `admisibilidad`, `causa_inadmisibilidad`, `via_recurso`, `es_revision_fondo`, `reenvia`, `parte_ganadora` |
| `_manifest.json` | — | Sello de provenance: hashes, filas y versión de cada generador (64 artefactos) |

## Cómo se producen (`_manifest.json`, schema v4)

```
corpus/ (46 vols, 329–349 excl. 335–336)
  ├─ construir_catalogo    → output/catalogo/{catalogo,secciones}    ┐ intermedios
  ├─ detectar_paginas      → output/mapa/mapa_paginas.csv            │ regenerables
  └─ cruzar_catalogo_y_mapa→ output/localizacion/fallos_localizados  ┘ (gitignored)
corpus + localizacion
  └─ parser.py 24.0        → csjn_casos · _textos · _votos · _zonas · _editorial
csjn_casos (+ derivers)
  ├─ extraer_epilogos 0.3                          → csjn_casos_epilogo
  ├─ derivar_partes 0.17   (+ epilogo)             → csjn_casos_partes
  ├─ derivar_materia 3.2   (+ _textos, vocab)      → csjn_casos_materia
  └─ derivar_recursos 0.6  (+ clasificador_*)      → csjn_casos_recursos
```

`parser_editorial.py` es librería importada por `parser.py` (sin `__main__`); su CSV
histórico (`csjn_editorial_indice_partes.csv`) quedó fósil, fuera de los canónicos
(H167/M35). Ver `MAPA.md` para el DAG completo y el orden de ejecución.

## Convenciones

- **Encoding:** UTF-8.
- **Versionado:** sin sufijos de versión en los nombres — git versiona; el sello de
  hashes / filas / versión-de-generador vive en `_manifest.json`.
- **Cobertura:** volúmenes 329–349, **excluyendo 335–336** (OCR pendiente; ver CODEBOOK §11).
