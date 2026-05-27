# output/parser/

Outputs canónicos del parser (etapa 4). Un CSV por dimensión del dataset.

| Archivo | Registros | Descripción |
|---------|-----------|-------------|
| `csjn_casos.csv` | 5.862 | Dataset a nivel caso: carátula (índice y cuerpo), fecha, tomo, apertura_tipo, outcome, voting_pattern, n_jueces, word counts por zona, firma_raw, jueces, posiciones, tribunal_origen, localización |
| `csjn_casos_votos.csv` | 27.463 | Dataset a nivel voto: un registro por juez por caso, con posición, texto del voto separado, tipo_voto_sep, fragmenta_ratio, punto_divergencia |
| `csjn_casos_zonas.csv` | 140.956 | Zonas de texto por caso: zona (sumario, dictamen, considerando, dispositiva, voto, etc.), segmento, rangos de línea, word count |
| `csjn_casos_editorial.csv` | 151 | Zonas editoriales por tomo: indice_partes, indice_materias, con rangos de línea y word count |
| `csjn_editorial_indice_partes.csv` | 11.445 | Entradas parseadas del índice alfabético de partes de cada tomo |

Encoding: UTF-8. Sin sufijos de versión en nombres — git versiona.
