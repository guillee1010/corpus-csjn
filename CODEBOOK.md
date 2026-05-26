# CODEBOOK — corpus-csjn Dataset

## 1. Dataset Overview

**corpus-csjn** is a structured dataset of rulings issued by the Argentine Supreme Court of Justice (*Corte Suprema de Justicia de la Nación*, CSJN), parsed from the official digitized compilation *Colección de Fallos de la Corte Suprema de Justicia de la Nación*.

The dataset covers volumes (tomos) 329 through 349, excluding volumes 335 and 336 (not available in digitized form at the time of processing). This spans rulings from February 2006 through March 2026, comprising 19 annual terms of the Court.

Each ruling is decomposed into case-level metadata, individual judicial votes, and fine-grained textual zones, enabling quantitative analysis of voting patterns, opinion assignment, argumentative effort, and coalition formation within the Court.

The dataset was constructed automatically by a Python pipeline from OCR-digitized markdown source files, with iterative validation against the original volumes. No manual coding of variables was performed; all values are extracted algorithmically from the source text.

### Key Figures

| Dimension | Count |
|---|---|
| Cases (total entries) | 5,862 |
| Full rulings (*fallos*) | 5,669 |
| Editorial summaries with link | 160 |
| Editorial summaries | 33 |
| Individual votes | 27,463 |
| Text zones | 140,956 |
| Volumes covered | 19 (329–334, 337–349) |
| Temporal span | Feb 2006 – Mar 2026 |
| Unique judges identified | 44 (9 titular justices + 35 conjueces and others) |

---

## 2. File Descriptions

The dataset consists of five CSV files. All files are UTF-8 encoded with comma separators.

### Primary files

| File | Unit of observation | Rows | Columns | Description |
|---|---|---|---|---|
| `csjn_casos.csv` | Case | 5,862 | 39 | Case-level metadata: parties, date, outcome, voting configuration, word counts, judge panel, and localization within source files. |
| `csjn_casos_votos.csv` | Judge × Case | 27,463 | 19 | One row per judge per case. Records each justice's voting position and, where applicable, the text and classification of their separate opinion. Includes denormalized case-level fields for analytical convenience. |
| `csjn_casos_zonas.csv` | Text zone × Case | 140,956 | 8 | Fine-grained segmentation of each ruling into structural zones (summary, opinion body, dictamen, signature block, etc.) with line references and word counts. |

### Auxiliary files

| File | Unit of observation | Rows | Columns | Description |
|---|---|---|---|---|
| `csjn_casos_editorial.csv` | Editorial section | 151 | 7 | Non-judicial editorial content in the volumes: indexes (by parties, by subject, by legislation), *acordadas* (administrative resolutions), and miscellaneous texts. |
| `csjn_editorial_indice_partes.csv` | Index entry | 11,445 | 7 | Individual entries from the alphabetical party index (*índice de partes*) in each volume. Used during pipeline construction for cross-referencing and validation. |

---

## 3. Variable Dictionary — `csjn_casos.csv`

### Identification and text

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Unique case identifier. Format: `{tomo}_p{page}`, where `page` is the starting page in the volume (e.g., `329_p5`). |
| `tomo` | integer | Volume number in the Colección de Fallos series. Range: 329–349 (excluding 335–336). |
| `case_name_indice` | string | Case name(s) as listed in the volume's alphabetical party index. Multiple name variants are separated by ` \| `. May be null for entries not found in the index. |
| `case_name_cuerpo` | string | Case name extracted from the ruling's header in the body text. Typically includes the full procedural caption (*carátula*). |
| `case_name_cuerpo_legacy` | string | Earlier extraction of the body case name, retained for backward compatibility. |
| `source_file` | string | Source markdown file from which the case was extracted (e.g., `LibroVol329.1.md`). |
| `linea_inicio` | integer | Start line (0-indexed) within the source file. |
| `linea_fin` | integer | Projected end line within the source file. |
| `linea_fin_real` | integer | Actual end line after boundary adjustments. |

### Temporal and jurisdictional

| Variable | Type | Description |
|---|---|---|
| `date` | string | Date of the ruling in Spanish natural language format (e.g., `7 de febrero de 2006`). Null for 362 entries where no date marker was detected. |
| `tribunal_origen` | string | Name of the lower court whose decision is being reviewed. Null for original jurisdiction cases and entries where detection failed. Free text; not normalized. |
| `tribunal_origen_status` | string | Detection status for lower court. See [Coded Values](#tribunal_origen_status). |
| `is_originaria` | integer (0/1) | Whether the case falls under the Court's original jurisdiction (*competencia originaria*, Art. 117 of the Constitution). |

### Outcome and voting

| Variable | Type | Description |
|---|---|---|
| `apertura_tipo` | string | Type of ruling opening marker detected: `fallo`, `sentencia`, or null. |
| `outcome` | string | Dispositional outcome of the ruling, extracted from the *por ello* clause. See [Coded Values](#outcome). 26.6% of cases are classified as `otro` (not yet subcategorized). |
| `voting_pattern` | string | Voting configuration of the panel. See [Coded Values](#voting_pattern). |
| `n_jueces` | integer | Total number of judges who signed the ruling. |
| `n_titulares` | integer | Number of permanent (*titular*) justices among the signatories. |
| `n_votos_svoto` | integer | Number of *según su voto* (concurring with separate reasoning) votes. |
| `n_disidencias` | integer | Number of dissenting votes. |
| `is_full_bench` | integer (0/1) | Whether all sitting titular justices participated. |
| `is_merit_decision` | integer (0/1) | Whether the ruling addresses the merits of the case (as opposed to procedural dismissals). |
| `dictamen_presente` | boolean | Whether the ruling includes an embedded opinion (*dictamen*) from the Procurador General or Fiscal. |

### Word counts

| Variable | Type | Description |
|---|---|---|
| `word_count` | integer | Total word count of the ruling, including all zones. |
| `wc_mayoria` | integer | Word count of the majority opinion body (*cuerpo*). |
| `wc_votos` | integer | Aggregate word count of all separate votes (*votos separados*). |
| `wc_considerando` | integer | Word count of the *considerando* section (legal reasoning). |
| `wc_dictamen` | integer | Word count of the *dictamen* (Procurador General's opinion), if present. |

### Panel composition

| Variable | Type | Description |
|---|---|---|
| `firma_raw` | string | Raw text of the signature block as extracted from the source. |
| `jueces` | string | Pipe-separated (`\|`) list of judges who signed the ruling, in order of appearance. |
| `jueces_conocidos` | string | Pipe-separated list of judges matched to the canonical list of known CSJN justices and conjueces. |
| `jueces_desconocidos` | float | Count of judges in the signature block that could not be matched to any known justice. Null when signature detection failed entirely. |
| `posiciones` | string | JSON dictionary mapping each judge's name to their voting position (e.g., `{"Petracchi": "mayoria", "Fayt": "en disidencia"}`). |

### Full-text fields

| Variable | Type | Description |
|---|---|---|
| `por_ello_text` | string | Full text of the *por ello* clause (the dispositional section where the Court states its operative decision). |
| `considerando_text` | string | Full text of the *considerando* section (legal reasoning of the majority). |

### Pipeline metadata

| Variable | Type | Description |
|---|---|---|
| `tipo_entrada` | string | Entry type. See [Coded Values](#tipo_entrada). |
| `status_localizacion` | string | Result of the case localization process (cross-referencing page maps, catalogs, and body text). See [Coded Values](#status_localizacion). |
| `status_fin` | string | Method used to detect the ruling's end boundary. See [Coded Values](#status_fin). |
| `pista_fin` | string | Specific textual clue used for end detection. See [Coded Values](#pista_fin). |

---

## 4. Variable Dictionary — `csjn_casos_votos.csv`

One row per judge per case. Includes denormalized case-level fields for direct analytical use without requiring joins.

### Judge-level fields

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `tomo` | integer | Volume number (denormalized). |
| `date` | string | Ruling date (denormalized). |
| `juez` | string | Judge name. Conjueces are suffixed with `(conjuez)`. 44 unique values. |
| `posicion` | string | Voting position: `mayoria`, `en disidencia`, `según su voto`, `por su voto`. |
| `es_conocido` | integer (0/1) | Whether the judge is in the canonical list of known CSJN justices. |

### Separate vote analysis

| Variable | Type | Description |
|---|---|---|
| `texto_voto` | string | Full text of the judge's separate vote, if any. Null for judges voting with the majority without a separate opinion. |
| `wc_voto` | integer | Word count of the individual judge's separate vote. 0 for majority-only votes. |
| `tipo_voto_sep` | string | Classification of the separate vote. Coded A–E (see [Coded Values](#tipo_voto_sep)) or `indeterminado` when the vote could not be classified. Null for judges without a separate vote. |
| `fragmenta_ratio` | float | Ratio measuring how fragmented the separate vote text is relative to the total ruling. Null for majority-only votes. |
| `punto_divergencia` | float | Estimated point (0.0–1.0) within the ruling's argumentative structure where the separate vote diverges from the majority. Null for majority-only votes. |

### Denormalized case-level fields

| Variable | Type | Description |
|---|---|---|
| `outcome` | string | Case outcome (from `csjn_casos`). |
| `voting_pattern` | string | Voting pattern (from `csjn_casos`). |
| `is_originaria` | integer (0/1) | Original jurisdiction flag (from `csjn_casos`). |
| `is_full_bench` | integer (0/1) | Full bench flag (from `csjn_casos`). |
| `is_merit_decision` | integer (0/1) | Merit decision flag (from `csjn_casos`). |
| `wc_mayoria` | integer | Majority word count (from `csjn_casos`). |
| `wc_votos` | integer | Aggregate separate-vote word count (from `csjn_casos`). |
| `dictamen_presente` | boolean | Dictamen presence flag (from `csjn_casos`). |

---

## 5. Variable Dictionary — `csjn_casos_zonas.csv`

One row per contiguous text zone per case. A single ruling may have dozens of zone rows, since zones are segmented at page boundaries (each page break creates a new segment of the same zone type).

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `tomo` | integer | Volume number. |
| `zona` | string | Zone type. See [Coded Values](#zona). |
| `segmento` | integer | Segment number within the case for this zone type (1-indexed). Zones spanning multiple pages are split into sequential segments. |
| `linea_ini` | integer | Start line (0-indexed) within the ruling's line range. |
| `linea_fin` | integer | End line within the ruling's line range. |
| `n_lineas` | integer | Number of lines in this segment. |
| `wc` | integer | Word count of this segment. |

---

## 6. Variable Dictionary — `csjn_casos_editorial.csv`

| Variable | Type | Description |
|---|---|---|
| `tomo` | integer | Volume number. |
| `source_file` | string | Source markdown file. |
| `subtipo` | string | Type of editorial section: `indice_partes`, `indice_general`, `indice_legislacion`, `indice_materias`, `acordadas`, `discurso`. |
| `linea_ini` | integer | Start line in source file. |
| `linea_fin` | integer | End line in source file. |
| `n_lineas` | integer | Number of lines. |
| `wc` | integer | Word count. |

---

## 7. Variable Dictionary — `csjn_editorial_indice_partes.csv`

| Variable | Type | Description |
|---|---|---|
| `tomo` | integer | Volume number. |
| `source_file` | string | Source markdown file. |
| `case_name_indice` | string | Case name as listed in the party index. |
| `paginas` | string | Page reference(s) as printed in the index (may contain multiple pages separated by commas). |
| `n_paginas` | integer | Number of page references for this entry. |
| `linea_ini` | integer | Start line of the entry in the index section. |
| `linea_fin` | integer | End line of the entry in the index section. |

---

## 8. Coded Values

### `outcome`

Dispositional outcome extracted from the *por ello* clause. Distribution across 5,862 cases:

| Value | N | Description |
|---|---|---|
| `otro` | 1,562 | Unclassified outcome. Residual category pending further subdivision (see Limitations). |
| `hace_lugar` | 1,102 | Complaint or appeal granted (*hace lugar al recurso*). |
| `procedente` | 656 | Appeal declared procedurally admissible and granted on the merits. |
| `competencia` | 571 | Jurisdictional competence ruling (*declárase competente* or assigns competence). |
| `desestima` | 476 | Appeal dismissed on procedural or substantive grounds. |
| `revoca` | 360 | Lower court decision reversed (*revoca la sentencia*). |
| `inadmisible_280` | 267 | Appeal declared inadmissible under Art. 280 of the CPCCN (discretionary certiorari). |
| `confirma` | 237 | Lower court decision affirmed. |
| `originaria` | 162 | Decision in original jurisdiction proceedings. |
| `abstracto` | 90 | Case declared moot (*abstracto*). |
| `nulidad` | 60 | Lower court decision annulled. |
| `inadmisible_acordada_4` | 52 | Appeal declared inadmissible under *Acordada* 4/2007 (formal requirements). |
| `mal_concedido` | 39 | Appeal declared improperly granted by the lower court. |
| `sin_dispositivo` | 25 | No dispositional clause could be extracted. |
| *(null)* | 193 | Outcome not available (typically `sumario_con_link` or `sumario_editorial` entries). |

### `voting_pattern`

| Value | N | Description |
|---|---|---|
| `unanime` | 3,513 | All judges joined a single opinion. |
| `disidencia` | 1,106 | At least one judge dissented from the majority disposition. |
| `segun_su_voto` | 742 | All judges agreed on the disposition but at least one filed a separate concurring opinion with different reasoning. |
| `mixed` | 292 | Combination of dissents and concurrences. |
| `sin_firma` | 16 | No judicial signatures could be extracted. |
| *(null)* | 193 | Not available. |

### `tipo_entrada`

| Value | N | Description |
|---|---|---|
| `fallo` | 5,669 | Full ruling with complete text. |
| `sumario_con_link` | 160 | Summary entry with a cross-reference to another volume. Full text not included. |
| `sumario_editorial` | 33 | Editorial summary without full ruling text. |

### `posicion` (in `csjn_casos_votos.csv`)

| Value | N | Description |
|---|---|---|
| `mayoria` | 23,724 | Judge voted with the majority. |
| `en disidencia` | 2,216 | Judge dissented from the majority disposition. |
| `según su voto` | 1,515 | Judge concurred in the result but filed separate reasoning. |
| `por su voto` | 8 | Variant of *según su voto*, used in some rulings. |

### `tipo_voto_sep` (in `csjn_casos_votos.csv`)

Classification of separate votes by their structural relationship to the majority opinion. Applied only to judges with a separate vote (2,749 votes; null for the remaining 24,714 majority-only votes).

| Value | N | Description |
|---|---|---|
| `indeterminado` | 1,342 | Could not be classified into a defined category. |
| `B` | 550 | *To be documented.* |
| `D` | 524 | *To be documented.* |
| `A` | 161 | *To be documented.* |
| `C` | 114 | *To be documented.* |
| `E` | 58 | *To be documented.* |

> **Note:** The A–E classification schema is under development. Detailed definitions will be added once the typology is finalized.

### `zona` (in `csjn_casos_zonas.csv`) {#zona}

| Value | N (segments) | Description |
|---|---|---|
| `header_pagina` | 45,952 | Page header inserted by the publisher (volume number, page number). Not part of the ruling. |
| `cuerpo` | 22,947 | Body of the majority opinion (*considerandos* and reasoning). |
| `dictamen` | 16,923 | Opinion of the Procurador General or Fiscal, embedded before the Court's own decision. |
| `dispositivo` | 12,476 | Operative section (*por ello* clause) stating the Court's decision. |
| `firma` | 10,608 | Signature block listing the judges' names. |
| `sumario` | 7,966 | Editorial summary (*sumario*) printed before the ruling, authored by the publisher (La Ley). |
| `epilogo` | 7,628 | Trailing text after the signature: notifications, dissent notes, procedural annotations. |
| `residuo_caso_anterior` | 7,513 | Residual text belonging to the preceding case on a shared page. |
| `apertura` | 5,754 | Opening section: case caption, date, and initial procedural framing. |
| `voto_separado` | 3,189 | Separate opinion (concurrence or dissent) by an individual judge. |

### `tribunal_origen_status`

| Value | N | Description |
|---|---|---|
| `apelado_detectado` | 3,876 | Lower court identified from the *Tribunal de origen* marker. |
| `sin_marcador` | 1,316 | No *Tribunal de origen* marker found; field is populated from other heuristics or left as free text. |
| `originaria` | 477 | Original jurisdiction case (no lower court). |
| *(null)* | 193 | Not available. |

### `status_localizacion`

Method used to locate the ruling within the source files:

| Value | N | Description |
|---|---|---|
| `ok` | 5,500 | Standard localization via page map and opening markers. |
| `ok_sin_marcador_apertura` | 181 | Located without the standard opening marker (*FALLO DE LA CORTE SUPREMA*). |
| `ok_ancla_catalogo` | 33 | Located using the volume catalog as anchor. |
| `ok_pg_fin_redirigida` | 30 | End page redirected due to page-sharing between rulings. |
| `ok_cortado_en_indice` | 26 | Case spans a page boundary indicated in the index. |
| `pagina_no_en_mapa` | 23 | Page reference in catalog not found in the page map. |
| `fallo_cruza_archivos` | 20 | Ruling spans two source files. |
| Other compound statuses | 49 | Combinations of the above flags. |

### `status_fin`

Method used to detect the ruling's end boundary:

| Value | N | Description |
|---|---|---|
| `fin_extendido_pag_compartida` | 5,631 | End extended to accommodate a shared page with the next ruling. |
| `fin_por_firma_actual` | 114 | End determined by the ruling's own signature block. |
| `fin_dentro_bloque` | 55 | End falls within the ruling's allocated block. |
| `fin_por_editorial` | 45 | End determined by the start of an editorial section. |
| `fin_no_detectado` | 17 | End boundary could not be detected reliably. |

### `pista_fin`

Specific textual clue used for end detection:

| Value | N | Description |
|---|---|---|
| `caratula_siguiente` | 5,130 | Next ruling's case caption (*carátula*) found. |
| `sumario_siguiente` | 379 | Next ruling's editorial summary found. |
| `marcador_apertura_siguiente` | 177 | Next ruling's opening marker found. |
| `firma_actual` | 114 | Current ruling's own signature block used. |
| `editorial_siguiente` | 45 | Start of editorial content found. |
| `fallback_catalogo` | 17 | Catalog-based fallback used. |

---

## 9. Known Limitations

### Data quality

1. **Outcome classification (`otro`: 26.6%).** 1,562 cases have an unclassified outcome. The *por ello* clauses of these cases contain dispositional formulas not yet captured by the extraction patterns. This is the largest remaining data quality gap and affects any analysis of case outcomes.

2. **Missing signatures (`sin_firma`: 16 cases, 0.3%).** Sixteen cases could not have their judicial signatures extracted, typically due to OCR artifacts or non-standard formatting.

3. **Missing dispositional clause (`sin_dispositivo`: 25 cases, 0.4%).** Twenty-five cases have no extractable *por ello* clause.

4. **Catalog-anchored cases (`ancla_catalogo`: 64 cases, 1.1%).** Sixty-four cases could not be located using standard page-map methods and were instead located using the volume catalog as a fallback anchor. Localization is less precise for these cases.

5. **Dates in natural language.** The `date` field is stored as Spanish free text, not as a standardized date format. Parsing into ISO dates requires handling the Spanish month names and ordinal conventions. 362 entries (6.2%) have no date.

### Coverage

6. **Volumes 335–336 missing.** These two volumes were not available in digitized form at the time of processing. They cover parts of the 2012–2013 judicial terms.

7. **Non-normalized lower courts.** The `tribunal_origen` field contains 1,316 entries with `sin_marcador` status, where the lower court name was not reliably detected. Even where detected, court names are not normalized (e.g., the same court may appear with different abbreviations).

8. **No *secretaría letrada* information.** The dataset does not identify which *secretaría letrada* (law clerk office) drafted each ruling. This information is not present in the published volumes and would require external sources.

### Methodological

9. **OCR-dependent source text.** The source markdown files were produced by OCR digitization of printed volumes. While generally high quality, OCR errors in case names, judge names, and legal text persist and may affect extraction accuracy.

10. **Separate vote typology (A–E) under development.** The `tipo_voto_sep` classification in `csjn_casos_votos.csv` uses a provisional schema. 1,342 of 2,749 separate votes (48.8%) are classified as `indeterminado`.

11. **`sumario_con_link` and `sumario_editorial` entries.** 193 entries (160 + 33) are not full rulings but editorial summaries or cross-references. These entries have null values for most analytical fields (outcome, voting_pattern, word counts). They are included for completeness but should typically be filtered out in analyses. They can be identified via `tipo_entrada != 'fallo'`.

---

## 10. Pipeline Methodology

The dataset is produced by a four-stage Python pipeline:

1. **`detectar_paginas.py`** — Reads the OCR-digitized markdown source files and builds a page map (`mapa_paginas.csv`), identifying page boundaries, page numbers, and volume structure.

2. **`construir_catalogo.py`** — Parses the alphabetical party index (*índice de partes*) at the end of each volume, producing a catalog of expected cases with their page references (`catalogo.csv`).

3. **`cruzar_catalogo_y_mapa.py`** — Cross-references the catalog entries with the page map to produce a localization table (`fallos_localizados.csv`), determining the line range in the source files where each ruling is expected to be found.

4. **`parser.py`** — The main extraction engine. For each localized ruling, detects the case opening, extracts the case caption, date, judges, voting positions, outcome, and full text of each structural zone. Produces the three primary output files.

An additional module, **`parser_editorial.py`**, handles non-judicial editorial sections separately.

Validation is performed by **`auditar_fallo.py`**, which audits individual cases against the source text, checking extraction boundaries, signature detection, and zone segmentation.

### Versioning

All pipeline scripts are version-controlled with embedded `__version__` strings. The dataset documented here was produced with parser.py v18.01. The full version history and bug registry are maintained in the repository's `BITACORA.md` (session journal) and `DEUDA_TECNICA.md` (technical debt and bug tracker).

---

## 11. Source and Legal

**Source:** *Colección de Fallos de la Corte Suprema de Justicia de la Nación*, volumes 329–349 (excluding 335–336). Published by La Ley / Thomson Reuters. Digitized versions available at [https://sjconsulta.csjn.gov.ar](https://sjconsulta.csjn.gov.ar).

**Legal status of source material:** The rulings of the Argentine Supreme Court are official public documents and are not subject to copyright. The editorial summaries (*sumarios*) included in the *Colección de Fallos* are authored by the publisher and may be subject to separate copyright. The dataset extracts and labels these summaries as `zona = "sumario"` but does not claim authorship over them.

**Dataset license:** CC-BY 4.0 International.

**Code license:** MIT.

---

## 12. Suggested Citation

> Rubinetti, Guillermo. *corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings (Volumes 329–349)*. Harvard Dataverse, 2026. https://doi.org/[DOI]. Licensed under CC-BY 4.0.

BibTeX:

```bibtex
@misc{rubinetti_corpus_csjn_2026,
  author    = {Rubinetti, Guillermo},
  title     = {corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings (Volumes 329--349)},
  year      = {2026},
  publisher = {Harvard Dataverse},
  doi       = {[DOI]},
  license   = {CC-BY-4.0},
  note      = {Covers volumes 329--349 (excluding 335--336), Feb 2006 -- Mar 2026}
}
```

---

*Codebook version: 1.0 — Generated for corpus-csjn parser v18.01.*
