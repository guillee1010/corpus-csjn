# corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings, Volumes 329–349 (2006–2026)

**Version 4.0** · parser v44.1 · November 2026
**Author:** Guillermo Rubinetti
**DOI:** [10.7910/DVN/TJTVKW](https://doi.org/10.7910/DVN/TJTVKW) · **License:** data CC-BY 4.0, code MIT
**Source code and history:** <https://github.com/guillee1010/corpus-csjn>

A structured dataset of the rulings of the Argentine Supreme Court (*Corte Suprema de Justicia de la Nación*, CSJN) published in the official *Colección de Fallos*, volumes 329 to 349 (February 2006 to March 2026, excluding volumes 335–336). It is modelled on the U.S. Supreme Court Database (SCDB) and built for quantitative research on admissibility, outcomes and voting in the Court. It was produced as part of a Master's thesis in Legal Argumentation (Universidad de Buenos Aires), *Diseño institucional y coordinación judicial. Un análisis comparado de los mecanismos de formación de mayorías en la Corte Suprema argentina frente al modelo estadounidense*.

The full variable dictionary, coded values, validation and known limitations are in **`dataverse/CODEBOOK.md`**. Start there.

## Contents

| Folder | Files | What it is |
|---|---|---|
| `dataverse/` | 3 | This README, the CODEBOOK and `MAPA.md` (pipeline dependency graph and run order). |
| `output/parser/` | 11 | **The dataset.** Ten CSV files and `_manifest.json`, which seals each file's SHA-256, row count and generator version. |
| `output/validacion/` | 8 | Reliability results cited in CODEBOOK §9 and §11 (κ tables, confusion matrices, read adjudications of disagreements). |
| `corpus/` | 46 | Source text of the volumes (OCR-digitized markdown), needed to reproduce the pipeline. |
| `output/mapa/`, `output/catalogo/`, `output/localizacion/` | 4 | Pipeline inputs built from the volumes (page map, case catalog, localization table). |
| `_meta/` | 7 | Reference tables used by the pipeline (justices, catalog errata, subject-matter vocabularies). |
| `scripts/pipeline/` | 16 | The pipeline code. |

### The ten CSV files

| File | Rows | Unit |
|---|---|---|
| `csjn_casos.csv` | 5,894 | Case: caption, date, panel, voting pattern, positions, merit, *queja*. |
| `csjn_casos_recursos.csv` | 5,894 | Case: disposition, merit review, admissibility and its cause, appeal type, party winning, remand. **Use this layer for outcomes.** |
| `csjn_casos_votos.csv` | 28,080 | Justice × case: position and separate-opinion text. |
| `csjn_casos_materia.csv` | 5,894 | Case: inferred subject matter (under development). |
| `csjn_casos_partes.csv` | 5,894 | Case: appellant and respondent with procedural role. |
| `csjn_casos_normas.csv` | 13,959 | Case × statute × scope: statutes cited ("ley N"). |
| `csjn_casos_textos.csv` | 5,894 | Case: full text of the reasoning, operative clause, signature block and the Procuración's opinion. |
| `csjn_casos_zonas.csv` | 138,597 | Text zone × case, with line ranges. |
| `csjn_casos_epilogo.csv` | 5,732 | Ruling: editorial epilogue text. |
| `csjn_casos_editorial.csv` | 152 | Editorial section of each volume (indexes, *acordadas*). |

All files are UTF-8, comma-separated, keyed on `caso_id_canonico` (`{volume}_p{first page}`, e.g. `344_p174`). Of the 5,894 entries, 5,732 are full rulings and 162 are editorial summaries; filter on `tipo_entrada = 'fallo'` for ruling-level analysis.

## Validation

The main validation is a census against the Court's own summaries database (sjconsulta, kept by its Secretaría de Jurisprudencia), an external coder independent of the pipeline, over every ruling that could be matched. Cohen's κ with 95% bootstrap intervals:

| Variable | N | Agreement | κ |
|---|---|---|---|
| Position of each justice | 10,301 positions in 2,480 rulings | 99.7% | **0.988** |
| Merit review (yes / no) | 2,984 | 96.3% | **0.916** |
| Disposition | 3,126 | 93.7% | **0.914** |
| *Queja* (yes / no) | 2,549 | 93.7% | **0.868** |
| Appeal type | 2,549 | 91.5% | 0.606 |

The position agreement compares the justices present in both sources; 212 of the 2,480 rulings have different sets of justices, which this κ does not count as disagreement (CODEBOOK §9.1). Figures computed at parser v43.3. The lower value for appeal type comes from rulings where the pipeline finds no appeal type and SJ records one, not from confusion between types. Party winning and remand have no SJ counterpart; for them, the earlier hand-coded sample of 300 rulings applies (κ 0.804 and 0.458, the latter not reportable). Details in CODEBOOK §9.

## Quick start

```python
import pandas as pd
casos = pd.read_csv("output/parser/csjn_casos.csv")
recursos = pd.read_csv("output/parser/csjn_casos_recursos.csv")
votos = pd.read_csv("output/parser/csjn_casos_votos.csv")

fallos = casos[casos.tipo_entrada == "fallo"].merge(recursos, on="caso_id_canonico")
merito = fallos[fallos.es_revision_fondo == "si"]
```

## Reproducing the dataset

1. Download the whole dataset keeping its folder structure.
2. With Python 3, run the scripts of `scripts/pipeline/` from the root folder in the order given in `dataverse/MAPA.md` (page map, catalog, localization, parser, epilogues and statutes, derivers, manifest). Each stage is a standalone script with default paths.
3. Compare the outputs with `output/parser/_manifest.json`.

The orchestrator `correr_pipeline.py` runs the same chain with version checks and a regression check against a frozen golden copy, which live in the GitHub repository (`scripts/tests/`). For a fully checked run, clone the repository instead.

Two caveats for checking hashes. Harvard Dataverse converts CSV files to its tabular format on upload, so verify SHA-256 against the files downloaded in **original format**. And the `corpus/*.md` files are distributed with Unix line endings, while the corpus hashes in the manifest were computed on a Windows copy; the pipeline reads both identically and produces the same outputs, but the corpus hashes will not match.

## Known limitations

The full list is in CODEBOOK §11. The main ones are:

- Volumes 335–336 are not included.
- Six printed rulings of 2022–2024 are not indexed in the volume catalog and have no row of their own (CODEBOOK §11, item 16).
- `is_full_bench` means five titular justices signed; it equals a full bench only in volumes 339–344 (CODEBOOK §3).
- The text of a separate vote signed jointly by several justices is attached to one of them only (CODEBOOK §6).
- Positions that a justice states only inside the common opinion (for example "se remite a su disidencia" in a precedent) are not coded; a lower-bound review finds 56 such positions in 38 rulings.
- `materia` is incomplete (32.3% of entries unclassified) and its taxonomy is not final.
- The appeal type is missing for part of the rulings (see Validation).
- Text comes from OCR; residual OCR errors exist.

## Source, rights and personal data

The source is the *Colección de Fallos de la Corte Suprema de Justicia de la Nación*. The rulings are official public documents. The editorial summaries (*sumarios*) printed in the volumes, which are part of `corpus/*.md`, are authored by the publisher and may be subject to separate copyright; the dataset does not claim authorship over them.

The dataset contains the names of the justices and of the parties as they appear in the published rulings. The validation uses only the votes and outcomes recorded in sjconsulta; no data about the court staff who load that database is included.

## Changes since version 3.0

Version 3.0 was produced with parser v18.15. Version 4.0 adds the recourse layer (disposition, merit review, admissibility and its cause, appeal type, party winning, remand), the subject-matter, parties, statutes and epilogue files, the Procuración's opinion text, partial dissent as its own position, many corrections to signatures and positions, the source corpus and inputs for reproduction, and the census validation against sjconsulta. The file `csjn_editorial_indice_partes.csv` is no longer produced and was removed.

## Citation

> Rubinetti, Guillermo (2026). *corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings, Volumes 329–349 (2006–2026)*. Version 4.0. Harvard Dataverse. https://doi.org/10.7910/DVN/TJTVKW
