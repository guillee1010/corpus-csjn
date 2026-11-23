# CODEBOOK — corpus-csjn Dataset

## 1. Dataset Overview

**corpus-csjn** is a structured dataset of rulings issued by the Argentine Supreme Court of Justice (*Corte Suprema de Justicia de la Nación*, CSJN), parsed from the official digitized compilation *Colección de Fallos de la Corte Suprema de Justicia de la Nación*.

The dataset covers volumes (tomos) 329 through 349, excluding volumes 335 and 336 (not yet included in this release; see §11). This spans rulings from February 2006 through March 2026, comprising 19 annual terms of the Court, distributed across 46 source markdown files.

Each ruling is decomposed into case-level metadata, a recourse-and-disposition layer, individual judicial votes, and fine-grained textual zones, enabling quantitative analysis of admissibility decisions, dispositional outcomes, voting patterns, argumentative effort, and coalition formation within the Court.

The dataset was constructed automatically by a Python pipeline from OCR-digitized markdown source files, with iterative validation against the original volumes. Variable extraction is algorithmic. The main validation is a census against the Court's own summaries database (sjconsulta), an independent external coder, covering every matched ruling (§9.1); an earlier hand-coded sample of 300 rulings is reported in §9.

### Key Figures

| Dimension | Count |
|---|---|
| Cases (total entries) | 5,894 |
| Full rulings (*fallos*) | 5,732 |
| Editorial summaries with link (`sumario_con_link`) | 128 |
| Editorial summaries (`sumario_editorial`) | 34 |
| Individual votes | 28,080 |
| Text zones | 138,597 |
| Volumes (tomos) covered | 19 (329–334, 337–349) |
| Source files | 46 |
| Temporal span | Feb 2006 – Mar 2026 |
| Distinct judge names in `csjn_casos_votos.csv` | 100 (17 without the `(conjuez)` suffix, 83 conjueces). The 17 include the sitting justices of the period and justices of earlier benches who appear only in older rulings transcribed or published late. |

---

## 2. File Descriptions

The dataset consists of ten CSV files, sealed by `_manifest.json` (SHA-256, row counts and generator version of each file). All files are UTF-8 encoded with comma separators and are keyed on `caso_id_canonico` where a case-level key applies. Counts as of parser v45.0.

### Primary files

| File | Unit of observation | Rows | Columns | Description |
|---|---|---|---|---|
| `csjn_casos.csv` | Case | 5,894 | 40 | Case-level metadata: parties, date, voting configuration, word counts, judge panel, jurisdiction, localization within source files, and the legacy `outcome` field (see §3). |
| `csjn_casos_recursos.csv` | Case (recourse layer) | 5,894 | 10 | The M26 recourse-and-disposition layer: the orthogonal admissibility / disposition / merit-review / party-winning / remand axes plus `via_recurso`, `multi_recurso`, `causa_inadmisibilidad` and `es_queja`. Keyed 1:1 to `csjn_casos.csv`. This is the canonical layer for outcome analysis (see §4). |
| `csjn_casos_votos.csv` | Judge × Case | 28,080 | 20 | One row per judge per case. Records each justice's voting position and, where applicable, the text and classification of their separate opinion. Includes denormalized case-level fields for analytical convenience. |
| `csjn_casos_zonas.csv` | Text zone × Case | 138,597 | 8 | Segmentation of each ruling into structural zones (opinion body, dictamen, operative clause, signature block, separate votes, etc.) with line references and word counts. |

### Auxiliary files

| File | Unit of observation | Rows | Columns | Description |
|---|---|---|---|---|
| `csjn_casos_textos.csv` | Case | 5,894 | 5 | Full-text fields extracted per case: `considerando_text`, `por_ello_text`, `firma_raw`, `dictamen_text`. Keyed 1:1 by `caso_id_canonico`. |
| `csjn_casos_materia.csv` | Case | 5,894 | 4 | Subject-matter (*materia*) sidecar, keyed 1:1. Under active development; see §7 and §8. |
| `csjn_casos_partes.csv` | Case | 5,894 | 8 | Appellant (*recurrente*) and respondent (*recurrido*) with their procedural role, derived from the editorial epilogue and the caption. See §7. |
| `csjn_casos_normas.csv` | Case × statute × scope | 13,959 | 5 | Statutes cited ("ley N") per case and per scope (caption, *considerando*, dictamen, operative clause, separate votes), 4,115 cases with at least one. See §7. |
| `csjn_casos_epilogo.csv` | Ruling | 5,732 | 7 | Raw text of the editorial epilogue after the signature (appeal and filing notes, counsel, court of origin), input of `csjn_casos_partes.csv`. See §7. |
| `csjn_casos_editorial.csv` | Editorial section | 152 | 7 | Non-judicial editorial content in the volumes: indexes (by parties, by subject, by legislation), *acordadas* (administrative resolutions), and miscellaneous texts. |

`csjn_editorial_indice_partes.csv`, published in earlier versions, is no longer produced by the pipeline and was removed (M35).

---

## 3. Variable Dictionary — `csjn_casos.csv`

40 columns. **Note:** as of the M26 refactor (parser v22.0), the full-text fields (`considerando_text`, `por_ello_text`, `firma_raw`) live in `csjn_casos_textos.csv`, and `causa_inadmisibilidad` lives in `csjn_casos_recursos.csv`. They are no longer columns of this file.

### Identification

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Unique case identifier. Format: `{tomo}_p{page}`, where `page` is the starting page in the volume (e.g., `329_p5`). |
| `tomo` | integer | Volume number in the Colección de Fallos series. Range: 329–349 (excluding 335–336). |
| `case_name_indice` | string | Case name(s) as listed in the volume's alphabetical party index. Multiple variants separated by ` \| `. May be null for entries not found in the index. |
| `case_name_cuerpo` | string | Case name extracted from the ruling's header in the body text. Typically the full procedural caption (*carátula*). |
| `case_name_cuerpo_legacy` | string | Earlier extraction of the body case name, retained for backward compatibility. |
| `case_name_cuerpo_fuente` | string | Provenance of `case_name_cuerpo` (since parser v42.0, H218): `v1` (3,838) extracted from the ruling's header; `fallback` (1,161) the header extractor did not find the caption and the old fallback, which returned the whole procedural record, was removed, so `case_name_cuerpo` is empty (the old value stays in `case_name_cuerpo_legacy`); `vacio` (895) no caption found. `case_name_indice` is never empty. |
| `source_file` | string | Source markdown file from which the case was extracted (e.g., `LibroVol329.1.md`). |
| `linea_inicio` | integer | Start line (0-indexed) within the source file. |
| `linea_fin` | integer | Projected end line within the source file. |
| `linea_fin_real` | integer | Actual end line after boundary adjustments. |

### Temporal and jurisdictional

| Variable | Type | Description |
|---|---|---|
| `date` | string | Date of the ruling in Spanish natural-language format (e.g., `7 de febrero de 2006`). Null for 311 entries (149 rulings and the 162 editorial entries) where no date marker was detected. |
| `tribunal_origen` | string | Name of the lower court whose decision is being reviewed. Null for original-jurisdiction cases and entries where detection failed (162 null). Free text; not normalized. |
| `tribunal_origen_status` | string | Detection status for the lower court. See [Coded Values](#tribunal_origen_status). |
| `is_originaria` | integer (0/1) | Whether the case falls under the Court's original jurisdiction (*competencia originaria*, Art. 117 of the Constitution). 598 cases. |
| `es_queja` | integer (0/1) | Whether the case arises from a *recurso de queja* (complaint appeal filed after a denied extraordinary appeal). 2,313 cases. Also published, denormalized, in `csjn_casos_recursos.csv`. |
| `queja_resultado` | string | Outcome of the *queja*, where applicable. See [Coded Values](#queja_resultado). Null for non-queja cases and quejas with no recorded result. |
| `tipo_cuestion_federal` | string | Type of federal question raised in the extraordinary appeal. See [Coded Values](#tipo_cuestion_federal). Null where none was detected. |

### Outcome (legacy) and voting

| Variable | Type | Description |
|---|---|---|
| `apertura_tipo` | string | Type of ruling opening marker detected: `fallo`, `sentencia`, or null (207 null). |
| `outcome` | string | **LEGACY — frozen (*congelada*).** Single-axis dispositional outcome extracted from the *por ello* clause under the pre-M26 schema. Superseded by the orthogonal axes in `csjn_casos_recursos.csv` (§4). Retained for backward compatibility and reproducibility of earlier analyses; **not** the recommended field for new outcome analysis. See [Coded Values](#outcome). |
| `voting_pattern` | string | Voting configuration of the panel. See [Coded Values](#voting_pattern). |
| `n_jueces` | integer | Total number of judges who signed the ruling. |
| `n_titulares` | integer | Number of permanent (*titular*) justices among the signatories. |
| `n_votos_svoto` | integer | Number of *según su voto* (concurring with separate reasoning) votes. |
| `n_disidencias` | integer | Number of dissenting votes. |
| `is_full_bench` | integer (0/1) | 1 when exactly five titular justices signed (`n_titulares == 5`). 1,547 cases. **This matches a full bench only in volumes 339–344 (2016–2021).** In volumes 329–337 the Court had seven members, so five signatures is not a full bench and seven is coded 0; in 338 and 345–349 the Court had three or four members and no ruling is coded 1. See Known Limitations (B156). |
| `is_merit_decision` | integer (0/1) | Whether the ruling addresses the merits of the case (as opposed to procedural dismissals). 2,981 cases. |
| `dictamen_presente` | boolean | Whether the ruling includes an embedded *dictamen* from the Procurador General or Fiscal. `True` 3,443 · `False` 2,289 · `0` 162 (editorial entries). |

### Word counts

| Variable | Type | Description |
|---|---|---|
| `word_count` | integer | Total word count of the ruling, including all zones. |
| `wc_mayoria` | integer | Word count of the majority opinion body (*cuerpo*). |
| `wc_votos` | integer | Aggregate word count of all separate votes (*votos separados*), counted on the ruling's text from the first separate-vote header onward; each vote is counted once regardless of how many justices sign it. `word_count` = `wc_mayoria` + `wc_votos` in every ruling. |
| `wc_considerando` | integer | Word count of the *considerando* section (legal reasoning). |
| `wc_dictamen` | integer | Word count of the *dictamen*, if present. |

### Panel composition

| Variable | Type | Description |
|---|---|---|
| `firma_raw` | string | *(Moved.)* Raw signature-block text now lives in `csjn_casos_textos.csv`. |
| `jueces` | string | Pipe-separated (`\|`) list of judges who signed the ruling, in order of appearance. |
| `jueces_conocidos` | string | Pipe-separated list of judges matched to the canonical list of known CSJN justices and conjueces. |
| `jueces_desconocidos` | float | Count of judges in the signature block not matched to any known justice. Null when signature detection failed entirely. |
| `posiciones` | string | JSON dictionary mapping each judge's name to their voting position (e.g., `{"Petracchi": "mayoria", "Fayt": "en disidencia", "Lorenzetti": "en disidencia parcial"}`). Vocabulary: `mayoria`, `según su voto`, `en disidencia`, `en disidencia parcial` (see `posicion`). Source: the qualifier printed after the judge's name in the signature block; since parser v43.3 (H226, B180 (b)), a judge whose signature carries no qualifier but who heads a separate vote or dissent in the ruling (header "Voto del…" / "Disidencia (parcial) del…") is published with the position the header states, under four guards (header after the dispositive clause, judge in the signature, non-empty vote text, no other signed panel between the dispositive clause and the header). 11 positions in 10 rulings moved at v43.3. |

### Pipeline metadata

| Variable | Type | Description |
|---|---|---|
| `tipo_entrada` | string | Entry type. See [Coded Values](#tipo_entrada). |
| `status_localizacion` | string | Result of the case-localization process. See [Coded Values](#status_localizacion). |
| `status_fin` | string | Method used to detect the ruling's end boundary. See [Coded Values](#status_fin). |
| `pista_fin` | string | Specific textual clue used for end detection. See [Coded Values](#pista_fin). |

---

## 4. Variable Dictionary — `csjn_casos_recursos.csv`

The **recourse-and-disposition layer** introduced in the M26 refactor (parser v22.0; deriver `derivar_recursos.py` + the M26 classifiers). It decomposes what the legacy single `outcome` field conflated into a set of **orthogonal axes**: the access decision is separated from the merit verb, the merit verb from who prevailed, and the remand decision from all of the above. Keyed 1:1 to `csjn_casos.csv` by `caso_id_canonico`. **This is the canonical layer for outcome analysis.**

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `admisibilidad` | string | The **access decision**: whether the Court admitted the recourse. See [Coded Values](#admisibilidad). Values: `admite` 2,900 · `sin_marcador` 1,295 · `inadmite` 1,127 · `no_aplica` 572. |
| `disposicion` | string | The **merit verb** (≈ SCDB *caseDisposition*): how the Court disposed of the case on review. See [Coded Values](#disposicion). |
| `es_revision_fondo` | string (si/no) | Whether the ruling reviews the merits (*fondo*) as opposed to deciding on procedural/access grounds only. `no` 2,913 · `si` 2,981. Gates the domain of `parte_ganadora`. |
| `parte_ganadora` | string | **Party-winning** (SCDB *partyWinning* convention): whether the *recurrente* obtained a favorable disposition. Petitioner-centric and binary. See [Coded Values](#parte_ganadora). |
| `reenvia` | string (si/no) | Whether the Court **remands** to the lower court (*reenvía*) rather than resolving the controversy itself. `no` 4,524 · `si` 1,370. **Reliability pending (B130); κ not yet reportable** — see Reliability. |
| `via_recurso` | string | Procedural avenue of access. See [Coded Values](#via_recurso). `recurso_extraordinario` 3,399 · `recurso_ordinario` 327 · null 2,168. |
| `multi_recurso` | string (si/no) | Whether the case resolves more than one recourse jointly. `no` 5,533 · `si` 361. |
| `causa_inadmisibilidad` | string | Specific ground for inadmissibility. Non-null **iff** `admisibilidad = inadmite` (the invariant below). See [Coded Values](#causa_inadmisibilidad). |
| `es_queja` | integer (0/1) | Whether the case arises from a *queja* (denormalized from `csjn_casos.csv`). |

> **Invariant (verified on disk).** `causa_inadmisibilidad ≠ "" ⟺ admisibilidad = "inadmite"`. Exactly **1,127 = 1,127**: every inadmissibility decision carries a ground, and no admitted case does. `causa_inadmisibilidad` is the **reason** for declining access; `admisibilidad` is the **access decision**; `disposicion` is the **merit verb**. Analyses of inadmissibility grounds should use `causa_inadmisibilidad`; analyses of the access decision should use `admisibilidad`.

---

## 5. Variable Dictionary — `csjn_casos_textos.csv`

Full-text fields, one row per case, keyed 1:1 by `caso_id_canonico`.

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `considerando_text` | string | Full text of the *considerando* section (legal reasoning of the majority). |
| `por_ello_text` | string | Full text of the *por ello* clause (the dispositional section where the Court states its operative decision). |
| `firma_raw` | string | Raw text of the signature block as extracted from the source. |
| `dictamen_text` | string | Full text of the opinion of the Procuración General (*dictamen*) embedded in the ruling, empty if none. |

---

## 6. Variable Dictionary — `csjn_casos_votos.csv`

One row per judge per case. Includes denormalized case-level fields for direct analytical use without joins.

### Judge-level fields

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `tomo` | integer | Volume number (denormalized). |
| `date` | string | Ruling date (denormalized). |
| `juez` | string | Judge name. Conjueces are suffixed with `(conjuez)`. 44 unique values. |
| `posicion` | string | Voting position. See [Coded Values](#posicion). |
| `es_conocido` | integer (0/1) | Whether the judge is in the canonical list of known CSJN justices. All published rows = 1. |

### Separate vote analysis

| Variable | Type | Description |
|---|---|---|
| `texto_voto` | string | Text of the judge's separate vote (header included), truncated to its first 5,000 characters (1,338 of 3,808 rows reach the limit; `wc_voto` counts the whole vote). Null for judges voting with the majority without a separate opinion. **Since parser v45.0 (H229, B193) a separate vote signed jointly by several judges (header "Voto de los señores ministros X e Y") carries the same text in the row of each signer**; up to v44.1 it was attached to one of them only and the co-signers had empty `texto_voto` and `wc_voto` 0 (950 judge rows in 761 rulings gained their text at v45.0). Use `voto_firmantes` to count each vote once. |
| `wc_voto` | integer | Word count of the judge's separate vote. 0 for majority-only votes. Every signer of a joint vote carries the full count of that vote: summing `wc_voto` over all rows of a ruling counts a joint vote once per signer. Summed over distinct votes (one row per `caso_id_canonico` × `voto_firmantes`) it equals `wc_votos` in 2,176 of the 2,190 rulings with separate votes; in the other 14 a vote is attributed to no row and the sum is lower, never higher. |
| `tipo_voto_sep` | string | Classification of the separate vote. Coded A–E or `indeterminado`; null for judges without a separate vote (24,272 null). Co-signers of a joint vote share its classification. See [Coded Values](#tipo_voto_sep). |
| `fragmenta_ratio` | float | Ratio measuring how fragmented the separate vote text is relative to the total ruling. Null for majority-only votes. |
| `punto_divergencia` | float | Estimated point (0.0–1.0) within the ruling's argumentative structure where the separate vote diverges from the majority. Null for majority-only votes. |
| `voto_firmantes` | string | Justices who sign this row's separate vote, as named in the vote header, in printed order, joined by ` | ` (e.g. `Lorenzetti | Highton de Nolasco | Argibay`). Identical in the row of every signer; a single-signer vote lists that judge alone. Empty when the row has no `texto_voto`. **A vote is a distinct value of `voto_firmantes` within a ruling**: 3,808 rows with text are 2,860 distinct votes (2,072 signed by one justice, 628 by two, 156 by three, 4 by four). Names come from the header and follow the judge table; a co-signer the table does not read in the header is missing from the list (9 joint headers, B188), and in one ruling (329_p4804) the list names a justice with no row in the published panel. New in parser v45.0 (H229, B193). |

### Denormalized case-level fields

`outcome`, `voting_pattern`, `is_originaria`, `is_full_bench`, `is_merit_decision`, `wc_mayoria`, `wc_votos`, `dictamen_presente` — all carried over from `csjn_casos.csv` for convenience. (Note: `outcome` here is the same legacy field; for outcome analysis join `csjn_casos_recursos.csv` instead.)

---

## 7. Variable Dictionary — auxiliary files

### `csjn_casos_zonas.csv`

One row per contiguous text zone per case. A single ruling may have dozens of zone rows, since zones are segmented at page boundaries.

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `tomo` | integer | Volume number. |
| `zona` | string | Zone type. See [Coded Values](#zona). |
| `segmento` | integer | Segment number within the case for this zone type (1-indexed). |
| `linea_ini` | integer | Start line (0-indexed) within the ruling's line range. |
| `linea_fin` | integer | End line within the ruling's line range. |
| `n_lineas` | integer | Number of lines in this segment. |
| `wc` | integer | Word count of this segment. |

### `csjn_casos_materia.csv`

Subject-matter sidecar. Keyed 1:1 by `caso_id_canonico`. See [Coded Values](#materia). **Under active development.**

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `materia` | string | Derived subject matter. Null for unclassified cases (1,904). |
| `materia_capa` | string | Classification tier (how the case was classified). See [Coded Values](#materia). |
| `materia_fuente` | string | The specific signal(s) that fired (e.g. `regla` for capa1; `objeto`, `norma`, `parte`, `kw`, `coocur:{rule}` for capa2; `sin_ancla` / `conflicto_capa2:{m1}/{m2}` for the residual). |

### `csjn_casos_editorial.csv`

| Variable | Type | Description |
|---|---|---|
| `tomo` | integer | Volume number. |
| `source_file` | string | Source markdown file. |
| `subtipo` | string | Type of editorial section: `indice_partes` (46), `indice_general` (46), `indice_legislacion` (20), `acordadas` (20), `indice_materias` (19), `discurso` (1). |
| `linea_ini` | integer | Start line in source file. |
| `linea_fin` | integer | End line in source file. |
| `n_lineas` | integer | Number of lines. |
| `wc` | integer | Word count. |

### `csjn_casos_partes.csv`

Appellant and respondent, keyed 1:1 by `caso_id_canonico`. The appellant comes only from the appeal marker of the editorial epilogue ("Recurso … interpuesto por X"), which ties who appealed to their procedural role; the caption is used as a fallback for the name, never to decide who appealed.

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `recurrente` | string | Appellant (the party, not counsel). Empty when no appeal marker was found. |
| `recurrente_rol` | string | Procedural role of the appellant: `actora`, `demandada`, `codemandada`, `coactora`, `penal`, `querellante`, `mp_fiscal`, `mp_defensa`, `por_derecho_propio`, `solo_letrado`; empty if unknown. In multi-appellant rulings, the role of the first appellant. |
| `recurrido` | string | Respondent, from the reply-to-appeal marker (*traslado contestado por*). Often empty. |
| `recurrido_rol` | string | Procedural role of the respondent (same values). |
| `multi_recurrente` | string | `si` / `no` (more than one appellant); empty when no appellant was identified. |
| `partes_capa` | string | Layer that produced the row: `epilogo`, `caratula`, `sin_epilogo`, `no_aplica` (editorial entries). |
| `partes_fuente` | string | Specific source within the layer (e.g. `epilogo:recurso`, `epilogo:recurso+traslado`, `caratula:recurso`, `sin_zona`, `sin_marcador_recurso`). |

### `csjn_casos_normas.csv`

Statutes cited, one row per case × statute × scope. Only "ley N" citations are extracted (`tipo = ley`); decrees, resolutions and *acordadas* are not yet covered, and citations without a number (codes, constitutional articles) are out of scope.

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `tipo` | string | Type of norm. Currently always `ley`. |
| `norma` | string | Statute number as cited (e.g. `24557`, `1285`). |
| `ambito` | string | Where it is cited: `caratula`, `considerando`, `dictamen`, `dispositivo` (*por ello*), `voto` (separate votes, aggregated per case; a vote signed by several justices is counted once, by `voto_firmantes`, since extraer_normas v1.2). |
| `n_menciones` | integer | Number of mentions in that scope. |

### `csjn_casos_epilogo.csv`

One row per ruling (`tipo_entrada = fallo`).

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `tomo` | integer | Volume number. |
| `source_file` | string | Source markdown file. |
| `epilogo_status` | string | `ok` (4,445) or `sin_zona` (1,287, no epilogue zone found). |
| `n_seg` | integer | Number of epilogue segments joined. |
| `wc` | integer | Word count. |
| `epilogo_text` | string | Raw epilogue text (soft hyphens removed). |

---

## 8. Coded Values

### `admisibilidad` {#admisibilidad}

The access decision in the recourse layer. **This axis is a synthesis** of the disposition and access signals, not an independent detector; it has no standalone κ (see Reliability).

| Value | N | Description |
|---|---|---|
| `admite` | 2,900 | The Court admitted the recourse (access granted; merits or competence reached). |
| `sin_marcador` | 1,295 | No explicit access marker; admissibility not determinable from access signals alone. |
| `inadmite` | 1,127 | The Court declined to admit the recourse. Carries a `causa_inadmisibilidad` (the invariant). |
| `no_aplica` | 572 | Access axis does not apply (e.g. original jurisdiction, editorial entries). |

### `disposicion` {#disposicion}

The merit verb (≈ SCDB *caseDisposition*). Distribution across 5,894 cases:

| Value | N | Description |
|---|---|---|
| `no_fondo` | 1,821 | No merit disposition (resolved on access/procedural grounds). |
| `deja_sin_efecto` | 1,373 | Prior decision set aside (*deja sin efecto*). |
| `revoca` | 914 | Lower court decision reversed (*revoca*). |
| `no_revision_competencia` | 592 | No merit review; jurisdictional-competence resolution. |
| `confirma` | 542 | Lower court decision affirmed. |
| `no_revision_procesal` | 359 | No merit review; procedural resolution. |
| `no_revision_demanda` | 181 | No merit review; resolution at the demand/claim stage. |
| `nulidad` | 57 | Lower court decision annulled. |
| `nulidad_concesion` | 42 | Annulment of the grant of the appeal (*nulidad de la concesión*). |
| `grant_remand_implicito` | 9 | Implicit grant-and-remand disposition. |
| `modifica` | 4 | Decision modified. |

### `es_revision_fondo` {#es_revision_fondo}

| Value | N | Description |
|---|---|---|
| `no` | 2,913 | The ruling does not review the merits. |
| `si` | 2,981 | The ruling reviews the merits. |

### `parte_ganadora` {#parte_ganadora}

Party-winning under the SCDB *partyWinning* convention: **binary and petitioner-centric** — the *recurrente* either obtains a favorable disposition (`recurrente_gana`) or does not (`recurrente_pierde`). Defined only on merit-review cases (`es_revision_fondo = "si"`).

| Value | N | Description |
|---|---|---|
| `no_aplica` | 2,995 | Axis undefined (no merit review, or no identifiable petitioner outcome). |
| `recurrente_gana` | 2,357 | The *recurrente* obtained a favorable disposition. Following SCDB, partial victories (`disposicion = modifica`) and reversal-and-remand are coded as wins: any favorable element to the *recurrente* is a win. |
| `recurrente_pierde` | 542 | The *recurrente* did not prevail. |

> **Derivation and limitation.** `parte_ganadora` is derived from `disposicion` by a fixed rule (revoca / deja_sin_efecto / nulidad / modifica / grant_remand → `recurrente_gana`; confirma → `recurrente_pierde`). For `modifica`, the win coding is guaranteed by the prohibition of *reformatio in pejus* — a petitioner cannot be left worse off by its own appeal — so a modification it obtained is favorable or neutral, never adverse. The rule assigns relative to a single *recurrente* of reference; in the rare case of genuinely reciprocal appeals (both parties appeal: `multi_recurso = si`) this reference may not match the party an analyst would pick. This imprecision is transversal to all disposition verbs, not specific to `modifica`. The granularity of *who* wins among identified parties (petitioner vs. respondent) is out of scope here and belongs to the prospective party-typing layer (§10).

### `reenvia` {#reenvia}

| Value | N | Description |
|---|---|---|
| `no` | 4,524 | The Court resolves the controversy itself (no remand). |
| `si` | 1,370 | The Court remands to the lower court (*reenvía*). |

> Reliability is **not yet reportable** for this axis (κ = 0.408 on a provisional gold; B130 paused pending manual recoding of the 42-case reversal universe). Use with caution.

### `via_recurso` {#via_recurso}

| Value | N | Description |
|---|---|---|
| `recurso_extraordinario` | 3,399 | Access via the federal extraordinary appeal (REX, Art. 14 Law 48). |
| `recurso_ordinario` | 327 | Access via the ordinary appeal to the Court. |
| *(null)* | 2,168 | Avenue not detected / not applicable. |

### `multi_recurso` {#multi_recurso}

| Value | N | Description |
|---|---|---|
| `no` | 5,533 | A single recourse is resolved. |
| `si` | 361 | More than one recourse is resolved jointly. |

### `causa_inadmisibilidad` {#causa_inadmisibilidad}

Specific ground for inadmissibility. Derived in the recourse layer (`clasificador_causa.py`, single source) and published in `csjn_casos_recursos.csv`. Computed **only when `admisibilidad == "inadmite"`** (the invariant). Grounds are detected from the *por ello* and considerando text, with the controlled vocabulary grounded in the Secretaría de Jurisprudencia's *Recurso Extraordinario* treatise.

| Value | N | Description |
|---|---|---|
| `INADMISIBLE_SIN_CAUSAL_EXPLICITA` | 476 | Inadmissibility declared without a canonical ground detectable in the text (discretionary/silent residual). |
| `ART_280` | 232 | Rejected under Art. 280 CPCCN (discretionary certiorari). |
| `INADMISIBLE_REMITE_DICTAMEN` | 170 | Inadmissibility resolved by reference to the Procurador General's *dictamen*. |
| `CUESTION_ABSTRACTA` | 94 | Rejected because the question became moot. Restricted to genuine mootness: cases that also decide the merits are recorded as `admite`. |
| `ACORDADA_4_2007` | 51 | Rejected for non-compliance with the formal requirements of *Acordada* 4/2007. |
| `FALTA_SENTENCIA_DEFINITIVA` | 43 | Rejected for absence of a final judgment (a prerequisite for the REX). |
| `CADUCIDAD_INSTANCIA` | 13 | Dismissed for lapse of instance (treatise §2.6). |
| `RESOLUCION_NO_RECURRIBLE` | 12 | The challenged resolution is not subject to appeal. |
| `FALTA_FUNDAMENTACION_AUTONOMA` | 12 | The appeal lacks the required autonomous grounds. |
| `DESISTIMIENTO` | 10 | Withdrawal — predominantly default on the deposit requirement (art. 286 CPCCN), not voluntary termination (treatise §2.1.11). |
| `FUERA_DE_TERMINO` | 10 | Appeal filed out of time. |
| `INTERPOSICION_INCORRECTA` | 2 | REX filed before the wrong forum (treatise §1.2.2). |
| `DEPOSITO_PREVIO` | 2 | Rejected in connection with the prior-deposit requirement. |
| *(null)* | 4,767 | `admisibilidad ≠ inadmite` (not applicable). |

### `outcome` (LEGACY — frozen) {#outcome}

> **Frozen field.** Single-axis disposition under the pre-M26 schema, superseded by §4. Retained for reproducibility only. Distribution across 5,894 cases:

| Value | N | | Value | N |
|---|---|---|---|---|
| `hace_lugar` | 1,409 | | `nulidad_concesion` | 32 |
| `competencia` | 936 | | `sin_dispositivo` | 21 |
| `desestima` | 818 | | `inadmisible_280` | 24 |
| `procedente` | 760 | | `inadmisible` | 23 |
| `otro` | 350 | | `improcedente` | 23 |
| `confirma` | 351 | | `caducidad` | 15 |
| `revoca` | 342 | | `desierto` | 12 |
| `rechaza` | 284 | | `desistimiento` | 10 |
| *(null)* | 162 | | `cautelar` | 5 |
| `abstracto` | 150 | | `inadmisible_acordada_4` | 5 |
| `deja_sin_efecto` | 82 | | | |
| `nulidad` | 42 | | | |
| `mal_concedido` | 38 | | | |

### `tipo_cuestion_federal` {#tipo_cuestion_federal}

| Value | N | Description |
|---|---|---|
| `cuestion_federal` | 1,307 | Ordinary federal question (*cuestión federal* in the strict sense). |
| `arbitrariedad` | 888 | Arbitrariness doctrine invoked (*arbitrariedad de sentencia*). |
| `mixto` | 678 | Both an ordinary federal question and arbitrariness. |
| *(null)* | 3,021 | No federal-question type detected. |

### `queja_resultado` {#queja_resultado}

Outcome of the *recurso de queja*, where `es_queja = 1`.

| Value | N | | Value | N |
|---|---|---|---|---|
| *(null)* | 3,765 | | `abstracta` | 17 |
| `hace_lugar` | 1,224 | | `suspendida` | 15 |
| `desestima` | 528 | | `desistida` | 10 |
| `procedente` | 182 | | `inadmisible` | 1 |
| `admisible` | 101 | | `nula` | 1 |
| `agreguese` | 30 | | | |
| `rechaza` | 19 | | | |

### `voting_pattern` {#voting_pattern}

| Value | N | Description |
|---|---|---|
| `unanime` | 3,529 | All judges joined a single opinion. |
| `disidencia` | 1,124 | At least one judge dissented from the majority disposition. |
| `segun_su_voto` | 764 | All judges agreed on the disposition but at least one filed separate concurring reasoning. |
| `mixed` | 307 | Combination of dissents and concurrences. |
| *(null)* | 162 | Not available (editorial entries). |
| `sin_firma` | 8 | No judicial signatures could be extracted. |

Counts as of parser v45.0. The pattern is derived from the signature block (and, since v43.3, from vote headers; see `posicion`). Positions a judge states only inside the common opinion (e.g., "la jueza X se remite a su disidencia en…") are not captured; see Known Limitations.

### `tipo_entrada` {#tipo_entrada}

| Value | N | Description |
|---|---|---|
| `fallo` | 5,732 | Full ruling with complete text. |
| `sumario_con_link` | 128 | Summary entry with a cross-reference to another volume. |
| `sumario_editorial` | 34 | Editorial summary without full ruling text. |

### `posicion` (in `csjn_casos_votos.csv`) {#posicion}

| Value | N | Description |
|---|---|---|
| `mayoria` | 24,222 | Judge voted with the majority. |
| `según su voto` | 1,588 | Judge concurred in the result but filed separate reasoning. Since parser v43.1 (H225, B178) this also covers the signature variant "(por su voto)" (8 positions). |
| `en disidencia` | 2,032 | Judge dissented from the majority disposition. |
| `en disidencia parcial` | 238 | Judge dissented in part, as marked in the signature block "(en disidencia parcial)". A vote header "Disidencia parcial" does not override a printed "(en disidencia)": 19 positions with "parcial" only in the header are published as `en disidencia`, and 5 with "parcial" only in the signature as `en disidencia parcial` (H229; the earlier figure, 13, counted one justice per joint vote). Counts as a dissent for `voting_pattern`. Since parser v43.0 (H225, B177). |

Source of the position: the qualifier printed in the signature block. Since parser v43.3 (H226, B180 (b)), when the signature carries no qualifier for a judge who heads a separate vote or dissent in the text, the position stated by that header is published instead (never overriding a printed qualifier). Counts as of parser v45.0 (28,044 rows at parser v44.0; 11 positions in 10 rulings moved from `mayoria` at v43.3; 2 more at v45.0, when co-signers of a joint vote became visible to the header rule: 330_p4399 and 344_p2441).

### `tipo_voto_sep` (in `csjn_casos_votos.csv`) {#tipo_voto_sep}

Classification of separate votes by their structural relationship to the majority. Applied to every row with a separate-vote text (3,808 judge rows, which are 2,860 distinct votes; null for the remaining 24,272 rows). Counts below are judge rows: a vote signed by three justices counts three times. Up to parser v44.1 only one signer per vote was classified (2,858 rows). **Schema A–E under development.**

| Value | N | Description |
|---|---|---|
| `indeterminado` | 1,862 | Could not be classified into a defined category. |
| `B` | 798 | *To be documented.* |
| `D` | 739 | *To be documented.* |
| `A` | 211 | *To be documented.* |
| `C` | 118 | *To be documented.* |
| `E` | 80 | *To be documented.* |

### `zona` (in `csjn_casos_zonas.csv`) {#zona}

| Value | N (segments) | Description |
|---|---|---|
| `header_pagina` | 44,808 | Page header inserted by the publisher. Not part of the ruling. |
| `cuerpo` | 25,489 | Body of the majority opinion (*considerandos* and reasoning). |
| `dictamen` | 16,978 | Opinion of the Procurador General or Fiscal, embedded before the Court's decision. |
| `dispositivo` | 11,612 | Operative section (*por ello* clause). |
| `firma` | 9,789 | Signature block listing the judges' names. |
| `sumario` | 8,012 | Intended for the editorial summaries printed before the ruling. **Not reliable for that purpose** (see Known Limitations). |
| `epilogo` | 4,936 | Trailing text after the signature: notifications, dissent notes, annotations. |
| `residuo_caso_anterior` | 7,747 | Residual text belonging to the preceding case on a shared page. |
| `apertura` | 5,811 | Opening section: case caption, date, initial procedural framing. |
| `voto_separado` | 3,415 | Separate opinion (concurrence or dissent) by an individual judge. |

Counts as of parser v45.0. `linea_ini` and `linea_fin` are offsets relative to the case block: the absolute line in the source file is `linea_inicio` + offset + 1.

### `tribunal_origen_status` {#tribunal_origen_status}

| Value | N | Description |
|---|---|---|
| `apelado_detectado` | 3,891 | Lower court identified from the *Tribunal de origen* marker. |
| `sin_marcador` | 1,243 | No marker found; populated from other heuristics or left as free text. |
| `originaria` | 598 | Original-jurisdiction case (no lower court). |
| *(null)* | 162 | Not available. |

### `status_localizacion` {#status_localizacion}

| Value | N | Description |
|---|---|---|
| `ok` | 5,618 | Standard localization via page map and opening markers. |
| `ok_sin_marcador_apertura` | 181 | Located without the standard opening marker. |
| `ok_ancla_catalogo` | 27 | Located using the volume catalog as anchor. |
| `fallo_cruza_archivos` | 27 | Ruling spans two source files. |
| `ok_cortado_en_indice` | 19 | Case spans a page boundary indicated in the index. |
| `ok_sin_marcador_apertura_ancla_catalogo` | 17 | Compound: no opening marker + catalog anchor. |
| `ok_sin_marcador_apertura_ancla_vistos` | 4 | Compound: no opening marker + *vistos* anchor. |
| `ok_ancla_vistos` | 1 | Located using the *vistos* clause as anchor. |

### `status_fin` {#status_fin}

| Value | N | Description |
|---|---|---|
| `fin_extendido_pag_compartida` | 5,695 | End extended to accommodate a shared page with the next ruling. |
| `fin_por_firma_actual` | 115 | End determined by the ruling's own signature block. |
| `fin_por_editorial` | 46 | End determined by the start of an editorial section. |
| `fin_dentro_bloque` | 21 | End falls within the ruling's allocated block. |
| `fin_no_detectado` | 17 | End boundary could not be detected reliably. |

### `pista_fin` {#pista_fin}

| Value | N | Description |
|---|---|---|
| `caratula_siguiente` | 5,203 | Next ruling's case caption found. |
| `sumario_siguiente` | 336 | Next ruling's editorial summary found. |
| `marcador_apertura_siguiente` | 177 | Next ruling's opening marker found. |
| `firma_actual` | 115 | Current ruling's own signature block used. |
| `editorial_siguiente` | 46 | Start of editorial content found. |
| `fallback_catalogo` | 17 | Catalog-based fallback used. |

### `materia`, `materia_capa`, `materia_fuente` (in `csjn_casos_materia.csv`) {#materia}

> **Under active development.** Subject-matter is derived from `csjn_casos` and `csjn_casos_textos` by a standalone, deterministic, layered stage (`derivar_materia.py`), re-runnable without re-parsing. The classifiable universe excludes original-jurisdiction cases. Counts below are a snapshot.

`materia_capa` (how the case was classified; values renamed in M49, H210, from the earlier `capa1` / `capa2` / `pendiente_capa2` / `capa1_refinado`):

| Value | N | Description |
|---|---|---|
| `lectura_tribunal` | 2,312 | Derived from the specialized court of origin (`tribunal_origen` → fuero → materia). Highest precision. (Formerly `capa1`.) |
| `lectura_texto` | 1,441 | Derived from the ruling's text: cited statutes, parties, case object, keywords, co-occurrence engine. (Formerly `capa2`.) |
| `sin_clasificar` | 1,130 | Not classifiable with available signals (no anchor or unresolved tie). (Formerly `pendiente_capa2`.) |
| `originaria` | 598 | Original-jurisdiction case (Art. 117). Terminal category, excluded from the coverage denominator. |
| `no_aplica` | 162 | Editorial-summary entries. |
| `lectura_tribunal_refinada` | 160 | A `lectura_tribunal` label overridden by a tax-authority signal (CA → `tributario`). (Formerly `capa1_refinado`.) |
| `lectura_dictamen` | 77 | Derived from the Procuración's opinion (statutes and keywords), only for cases with no anchor in the ruling's own text. |
| `sui_generis` | 8 | Impeachment juries and judicial councils. |
| `residual` | 6 | Arbitral tribunals and OCR/anaphora artifacts. |

`materia` values (when classified): `civil_comercial` (1,001), `contencioso_administrativo` (939), `penal` (684), `laboral` (479), `previsional` (354), `tributario` (353), `ambiental` (59), `constitucional` (30), `electoral` (29), `consumo` (29), `salud` (19), `cambiario` (7), `lesa_humanidad` (3), `penal_tributario` (2), `penal_cambiario` (2); null (1,904).

`materia_fuente` records the specific signal that fired (e.g. `regla:…` for the court-of-origin rule, `objeto(n)`, `norma`, `provincia:…`, `dictamen:norma:N`, `sin_ancla`). Its values are implementation labels, kept for auditability.

---

## 9. Reliability — inter-rater Cohen's κ (recourse-layer axes)

The primary validation of the dataset is the census against the Court's summaries database (§9.1), which covers every ruling with a match. The hand-coded n = 300 κ below is kept as the earlier, sample-based validation; no new hand-coded round is planned.

The M26 recourse-layer axes were validated against a hand-coded gold standard by computing Cohen's κ between the pipeline prediction and the human coding (`kappa_confiabilidad.py`; bootstrap 95% CI, B = 5,000). This measures agreement corrected for chance between parser and gold — it is **not** a double-coding (codebook-reproducibility) κ.

| Axis | N | Agreement | κ | 95% CI | Landis–Koch |
|---|---|---|---|---|---|
| `es_revision_fondo` | 300 | 0.947 | **0.893** | [0.840, 0.940] | almost perfect |
| `via_recurso` | 133 | 0.985 | **0.943** | [0.850, 1.000] | almost perfect |
| `disposicion` | 140 | 0.950 | **0.923** | [0.862, 0.976] | almost perfect |
| `parte_ganadora` | 134 | 0.940 | **0.804** | [0.658, 0.925] | almost perfect |
| `reenvia` | 75 | 0.853 | 0.458 | [0.184, 0.702] | moderate — **not reportable** |

Recomputed in H224 against the current `csjn_casos_recursos.csv` (gold `golds/planilla_M20_57GOLD_parte_limpia.xlsx`; output `output/validacion/kappa_resultados_parte.csv`). The previous published values (0.940 / 0.943 / 0.912 / 0.784 / 0.408) predate the unification of the merit gate (H178). The gold was coded before the decision to count original-jurisdiction rulings decided on the merits as merit decisions, following the SCDB (B136, H169): 8 of the 16 `es_revision_fondo` disagreements are such rulings (`disposicion = no_revision_demanda`), coded "no" in the gold and "si" by the pipeline. This is a difference of criterion, not a parser error. `parte_ganadora` and `reenvia` have no SJ counterpart, so for them this table remains the only reliability estimate.

> **Notes.** (a) `admisibilidad` is a synthesis of the disposition/access signals (≈99.9% relabel-consistent), not an independent detector, so it carries no standalone κ. (b) `parte_ganadora` is binary on both sides: the pipeline derives `recurrente_gana`/`recurrente_pierde` with no `parcial` value (`modifica → gana`), and the gold's original three-value coding (gana / parcial / pierde) was collapsed to the same binary scheme; the three-value gold is retained in the repository so the collapse is auditable. The κ remains capped below 1.0 by seven residual role-inversions preserved as genuine disagreements. (c) `reenvia` κ is moderate and **not reportable**: the reversal universe requires manual recoding (B130, in progress) before a reliable estimate over the full reversal set can be published.

### 9.1 External validation against the Court's summaries database (sjconsulta)

The Court's Secretaría de Jurisprudencia (SJ) publishes a summaries database (`sjconsulta.csjn.gov.ar`) in which its staff code, for each ruling, the votes of each justice, the outcome (`sentido`) and the type of appeal (`tipo_recurso`). SJ coding is independent of this pipeline, so it works as a large external second coder. Rulings are matched by volume and page (`caso_id_canonico`); entries with several SJ rulings on the same page and rulings with *conjueces* are excluded. Figures as of parser v43.3 (H224); bootstrap 95% CI, B = 2,000.

| Variable | SJ field | N | Agreement | κ | 95% CI |
|---|---|---|---|---|---|
| `posicion` (justice × ruling) | vote blocks | 10,301 positions in 2,480 rulings (2006–2026) | 0.997 | **0.988** | [0.982, 0.993] |
| `es_queja` | `tipo_recurso` = queja | 2,549 | 0.937 | **0.868** | [0.848, 0.888] |
| `disposicion` | `sentido` | 3,126 | 0.937 | **0.914** | [0.903, 0.925] |
| `es_revision_fondo` (merit / non-merit) | `sentido` | 2,984 | 0.963 | **0.916** | [0.901, 0.931] |
| `via_recurso` | `tipo_recurso` | 2,549 | 0.915 | 0.606 | [0.563, 0.651] |

> **Notes.** (a) `posicion`: SJ's first UNANIMIDAD / VOTO CONJUNTO block is `mayoria`, other non-dissenting blocks are `según su voto`, DISIDENCIA (PARCIAL) blocks are `en disidencia (parcial)`; the bootstrap resamples rulings, since positions within a ruling are not independent. Of the 33 remaining disagreements, 18 are SJ VOTO PROPIO vs corpus `mayoria`, the pattern of a known definitional difference (a heading opinion signed by fewer than a majority is `mayoria` in the corpus and VOTO PROPIO in SJ; not read one by one), and the 5 read in H224 were SJ errors (e.g., "(en disidencia parcial)" printed in the signature, coded as full dissent by SJ). The comparison is made on the justices present in both sources: a justice missing from the corpus panel (or from SJ) is not counted as a disagreement. 212 of the 2,480 rulings have different sets of justices in the two sources (M69, H227). The figures were computed at parser v43.3; v44.0 adds 29 rulings of 2022–2025 not yet compared. Scripts: `scripts/validacion/kappa_sjconsulta.py` (from the SJ cache) and `kappa_sjconsulta_posiciones.py` (same logic, reproducible without the personal data in the cache). (b) `disposicion`, `via_recurso`, `es_queja`: the mapping between SJ labels and corpus values is set at the top of `scripts/validacion/kappa_disposicion_via_sj.py` (six disposition classes; jurisdiction rulings, DECLARA (IN)COMPETENCIA, count as non-merit, the same criterion as the hand-coded gold; original-jurisdiction rulings on the claim are left out of the merit / non-merit row; 142 rulings with SJ labels outside the mapping, e.g. PROCEDIMIENTO or ADMITE, are excluded). (c) The lower κ for `via_recurso` is driven by 186 rulings where the corpus detects no appeal type and SJ records an extraordinary (153) or ordinary (33) appeal: a recall gap, not a confusion between types. (d) This is agreement with an external coder over the whole overlap, not a blind κ against a hand-coded gold standard (table above).

---

## 10. Crosswalk to the Supreme Court Database (SCDB)

For analysts familiar with the U.S. Supreme Court Database, the recourse-layer axes map approximately as follows. The mapping is **conceptual, not identical** — the CSJN's procedural architecture differs from SCOTUS's.

| corpus-csjn (Spanish) | SCDB analogue | Notes |
|---|---|---|
| `parte_ganadora` | *partyWinning* | Same petitioner-centric binary convention. Partial victories coded as wins. |
| `disposicion` | *caseDisposition* | The merit verb. Value sets differ (CSJN has *competencia*, *deja sin efecto*, etc.). |
| `es_revision_fondo` | (merits flag) | No exact SCDB field; gates the domain of `parte_ganadora`. |
| `via_recurso` | (jurisdiction/avenue) | Federal extraordinary vs. ordinary appeal. |
| `reenvia` | (remand outcome) | Whether the Court remands rather than resolving itself. |
| — | *declarationUncon* | **Gap.** The dataset does not currently flag declarations of unconstitutionality as a separate dimension. |
| — | *petitioner* / *respondent* | **Gap — prospective.** Party identity (actor/demandado) and party *type* (individual, business, national/provincial/municipal state, tax authority, agency) are not yet derived; only the raw caption (`case_name_cuerpo`, `case_name_indice`) and the party index are available. Deriving this layer would enable a `decisionDirection`-style analysis (which party type the Court favors) when crossed with `parte_ganadora`. See the technical-debt entry on the party-typing layer. |
| — | *majOpinWriter* / *majOpinAssigner* | **Dropped — category error for the CSJN.** The Court rules predominantly *per curiam*; there is no single majority-opinion author or assigner analogous to SCOTUS opinion assignment. |

---

## 11. Known Limitations

### Data quality

1. **Legacy `outcome` residual (`otro`: 350).** The frozen `outcome` field retains an unclassified residual. This field is superseded by the §4 axes and is not the recommended basis for outcome analysis.
2. **`reenvia` reliability pending (B130).** κ for the remand axis is not yet reportable; manual recoding of the reversal universe is in progress. Treat `reenvia` as provisional.
3. **Party identity/type not derived.** `parte_ganadora` records whether the *recurrente* won, but the dataset does not yet identify the parties (actor/demandado) or their type (individual, business, state, etc.). This precludes a `decisionDirection`-style analysis (which party type the Court favors). The raw material is present (captions, party index); the derivation is a planned layer (see §10 and the technical-debt register).
4. **Missing signatures (`sin_firma`: 8 rulings, 0.1%).** OCR artifacts or non-standard formatting.
5. **Missing dispositional clause (`sin_dispositivo` in legacy `outcome`: 21 cases).** No extractable *por ello* clause.
6. **Dates in natural language.** `date` is Spanish free text, not ISO. 311 entries (5.3%) have no date.

### Coverage

7. **Volumes 335–336 not yet included.** Volumes 335–336 are not yet included in this release. They were unavailable in digitized form at processing time and are planned for inclusion in a future version, once physical copies are obtained and OCR-processed. They cover parts of the 2012–2013 terms.
8. **Non-normalized lower courts.** 1,243 entries have `sin_marcador` status; even where detected, court names are not normalized.
9. **No *secretaría letrada* information.** The dataset does not identify which law-clerk office drafted each ruling; this is absent from the published volumes.

### Methodological

10. **OCR-dependent source text.** Source markdown was produced by OCR digitization of printed volumes; residual OCR errors may affect extraction accuracy.
11. **`materia` under development.** Coverage and taxonomy of the subject-matter sidecar are not final (see §8).
12. **Separate-vote typology (A–E) under development.** `tipo_voto_sep` uses a provisional schema; 1,371 of 2,860 distinct separate votes (47.9%) are `indeterminado` (1,862 of 3,808 judge rows, 48.9%).
13. **Editorial entries.** 162 entries (`tipo_entrada ≠ fallo`) are summaries/cross-references with null analytical fields; filter via `tipo_entrada = 'fallo'` for ruling-level analysis.
14. **Positions stated inside the common opinion are not coded (B179).** `posicion`, `posiciones` and `voting_pattern` come from the signature block and vote headers. When every judge signs the common opinion without a qualifier but the text says that a judge "se remite a su disidencia/voto" in a precedent, or the *por ello* clause says "por mayoría", that position is not captured. A lower-bound surface (H224) finds 56 such positions in 38 rulings, all published as `mayoria`; in 16 rulings at least one of them dissents from the result. The read adjudication is in `output/validacion/adjudicacion_b179_h224.csv`.
15. **`zona = sumario` does not capture the printed summaries (B190).** The editorial summaries printed before each ruling largely fall in unlabeled stretches or in `residuo_caso_anterior`, and the `sumario` label also covers other material (volume front matter, *acordadas*, opinions). Do not use `zona = sumario` to recover the summaries or their attribution to a vote.
16. **Rulings not indexed in the catalog (B192).** Six printed rulings of 2022–2024 have no row of their own because the volume index does not list them: they sit inside the block of another entry (346_p542, 347_p1763, 345_p204, 345_p386). Four of them are signed only by *conjueces*. Their panel is not published, and in 345_p386 the text of one of them is counted with the ruling of the entry.
17. **`is_full_bench` is not period-aware (B156).** It is `n_titulares == 5`, a full bench only in volumes 339–344 (see §3).
18. **Joint separate votes (B193, fixed in parser v45.0).** A separate vote signed by several justices carries the same `texto_voto` and `wc_voto` in the row of each signer, and `voto_firmantes` identifies the vote (see §6): per-justice counts need no adjustment, per-ruling sums must take one row per `voto_firmantes`. Residue: 9 joint votes have a co-signer whose name the judge table does not read in the header (B188), who keeps the right `posicion` but no text; 57 of 3,858 non-majority positions have no text. The printed volume sometimes contradicts itself between a vote header and the signature block (B198): the signature qualifier prevails, so 330_p4399 is published with four dissenters out of seven, and 24 positions differ from their vote header only in the word "parcial".
19. **Signers not recognized by the judge table.** The panel is read against a table of name patterns (`_meta/jueces/jueces_csjn.csv`, 110 rows). Since parser v44.1 (H228) the table reads surname-first signatures of *conjueces* (the volume sometimes transcribes the digital-signature stamp, "Borinsky Mariano Hernan"), the compound surname printed with a dash ("García—Mansilla"), 18 *conjueces* that had no row, and five printed variants taken as name variants of a known judge, each with its ruling as witness: "Carlos Maqueda" (346_p319), "Lorenzett." (343_p1762), "Rosatti Horacio" (348_p708, the only occurrence of a sitting justice printed surname-first), "Borinski" (347_p863) and "María Inés Catalano" (348_p1435). 29 rulings changed; the three rulings where a printed qualifier was attributed to the previous justice (B195) are corrected. The panels were read in the volume and checked against the Secretaría de Jurisprudencia records (sjconsulta) in 31 rulings, with no contradiction. Known residue: in 339_p323 one signer ("Jorge Morán") is not in the table because his identity could not be confirmed (5 of 6 signers published); a *conjuez* who is not in the table is missing from `posiciones`, and his printed qualifier is no longer given to another judge; three *conjueces* enter the panel without `texto_voto` because the header of their vote is not read (347_p1701, 347_p1084, 342_p459; B188).

---

## 12. Pipeline Methodology

The dataset is produced by a staged Python pipeline (`scripts/pipeline/`; dependency graph and run order in `MAPA.md`):

1. **`detectar_paginas.py`** — Reads the OCR-digitized markdown source files and builds a page map (`mapa_paginas.csv`).
2. **`construir_catalogo.py`** — Parses the volume indexes to produce a catalog of expected cases (`catalogo.csv`, `secciones_indices.csv`), with a curated errata supplement (`_meta/catalogo_suplemento_editorial.csv`).
3. **`cruzar_catalogo_y_mapa.py`** — Cross-references catalog and page map to produce a localization table (`fallos_localizados.csv`).
4. **`parser.py`** (v44.1) — The main extraction engine. Detects case openings, extracts caption, date, judges (`_meta/jueces/jueces_csjn.csv`), voting positions, and the full text of each structural zone. Produces `csjn_casos.csv`, `csjn_casos_votos.csv`, `csjn_casos_zonas.csv`, `csjn_casos_textos.csv` and `csjn_casos_editorial.csv` (with `parser_editorial.py`).
5. **`extraer_epilogos.py`** and **`extraer_normas.py`** — Epilogue text and cited statutes (`csjn_casos_epilogo.csv`, `csjn_casos_normas.csv`).
6. **Derivers** — `derivar_recursos.py` plus the M26 classifiers (`clasificador_disposicion.py`, `clasificador_via.py`, `clasificador_admision.py`, `clasificador_causa.py`) produce `csjn_casos_recursos.csv`; `derivar_partes.py` produces `csjn_casos_partes.csv`; `derivar_materia.py` (with the vocabularies in `_meta/vocab_materia/`) produces `csjn_casos_materia.csv`.
7. **`generar_manifiesto.py`** — Seals the outputs, inputs, corpus and vocabularies in `_manifest.json`.

`correr_pipeline.py` runs steps 4–7 in order with version checks, a regression check against a frozen golden copy and the manifest verification. Steps 1–3 are run by hand when volumes are added. Reliability validation lives in `scripts/validacion/` (`kappa_sjconsulta.py`, `kappa_disposicion_via_sj.py`, `kappa_confiabilidad.py`).

### Versioning

Pipeline scripts carry embedded `__version__` strings, recorded in `_manifest.json`. This dataset was produced with **parser.py v45.0**. The full version history and bug registry are in the repository's `BITACORA.md` (session journal), `CHANGELOG.md` and `DEUDA_TECNICA.md` (technical-debt and bug tracker).

---

## 13. Source and Legal

**Source:** *Colección de Fallos de la Corte Suprema de Justicia de la Nación*, volumes 329–349 (excluding 335–336). Digitized versions available at [https://sjconsulta.csjn.gov.ar](https://sjconsulta.csjn.gov.ar).

**Legal status of source material:** The rulings of the Argentine Supreme Court are official public documents and are not subject to copyright. The editorial summaries (*sumarios*) included in the *Colección de Fallos* are authored by the publisher and may be subject to separate copyright. They are part of the source volumes (`corpus/*.md`) distributed for reproducibility; the dataset does not claim authorship over them. `zona = "sumario"` does not reliably delimit them (see §11).

**Dataset license:** CC-BY 4.0 International.
**Code license:** MIT.

---

## 14. Suggested Citation

> Rubinetti, Guillermo. *corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings (Volumes 329–349)*. Harvard Dataverse, 2026. https://doi.org/10.7910/DVN/TJTVKW. Licensed under CC-BY 4.0.

```bibtex
@misc{rubinetti_corpus_csjn_2026,
  author    = {Rubinetti, Guillermo},
  title     = {corpus-csjn: A Structured Dataset of Argentine Supreme Court Rulings (Volumes 329--349)},
  year      = {2026},
  publisher = {Harvard Dataverse},
  doi       = {10.7910/DVN/TJTVKW},
  license   = {CC-BY-4.0},
  note      = {Covers volumes 329--349 (excluding 335--336), Feb 2006 -- Mar 2026}
}
```

---

*Codebook version: 4.0 — corpus-csjn parser v45.0 (H229). Version 4.0: schema change, new column `voto_firmantes` in `csjn_casos_votos.csv`.*
