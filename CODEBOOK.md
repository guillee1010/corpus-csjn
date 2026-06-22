# CODEBOOK — corpus-csjn Dataset

## 1. Dataset Overview

**corpus-csjn** is a structured dataset of rulings issued by the Argentine Supreme Court of Justice (*Corte Suprema de Justicia de la Nación*, CSJN), parsed from the official digitized compilation *Colección de Fallos de la Corte Suprema de Justicia de la Nación*.

The dataset covers volumes (tomos) 329 through 349, excluding volumes 335 and 336 (not yet included in this release; see §11). This spans rulings from February 2006 through March 2026, comprising 19 annual terms of the Court, distributed across 46 source markdown files.

Each ruling is decomposed into case-level metadata, a recourse-and-disposition layer, individual judicial votes, and fine-grained textual zones, enabling quantitative analysis of admissibility decisions, dispositional outcomes, voting patterns, argumentative effort, and coalition formation within the Court.

The dataset was constructed automatically by a Python pipeline from OCR-digitized markdown source files, with iterative validation against the original volumes. Variable extraction is algorithmic; the recourse-layer axes (§4) were additionally validated against a hand-coded gold standard via inter-rater Cohen's κ (see Reliability).

### Key Figures

| Dimension | Count |
|---|---|
| Cases (total entries) | 5,890 |
| Full rulings (*fallos*) | 5,697 |
| Editorial summaries with link (`sumario_con_link`) | 160 |
| Editorial summaries (`sumario_editorial`) | 33 |
| Individual votes | 27,697 |
| Text zones | 141,451 |
| Volumes (tomos) covered | 19 (329–334, 337–349) |
| Source files | 46 |
| Temporal span | Feb 2006 – Mar 2026 |
| Unique judges identified | 44 (titular justices + conjueces) |

---

## 2. File Descriptions

The dataset consists of eight CSV files. All files are UTF-8 encoded with comma separators and are keyed on `caso_id_canonico` where a case-level key applies.

### Primary files

| File | Unit of observation | Rows | Columns | Description |
|---|---|---|---|---|
| `csjn_casos.csv` | Case | 5,890 | 39 | Case-level metadata: parties, date, voting configuration, word counts, judge panel, jurisdiction, localization within source files, and the legacy `outcome` field (see §3). |
| `csjn_casos_recursos.csv` | Case (recourse layer) | 5,890 | 10 | The M26 recourse-and-disposition layer: the orthogonal admissibility / disposition / merit-review / party-winning / remand axes plus `via_recurso`, `multi_recurso`, and `causa_inadmisibilidad`. Keyed 1:1 to `csjn_casos.csv`. This is the canonical layer for outcome analysis (see §4). |
| `csjn_casos_votos.csv` | Judge × Case | 27,697 | 19 | One row per judge per case. Records each justice's voting position and, where applicable, the text and classification of their separate opinion. Includes denormalized case-level fields for analytical convenience. |
| `csjn_casos_zonas.csv` | Text zone × Case | 141,451 | 8 | Fine-grained segmentation of each ruling into structural zones (summary, opinion body, dictamen, signature block, etc.) with line references and word counts. |

### Auxiliary files

| File | Unit of observation | Rows | Columns | Description |
|---|---|---|---|---|
| `csjn_casos_textos.csv` | Case | 5,890 | 4 | Full-text fields extracted per case: `considerando_text`, `por_ello_text`, `firma_raw`. Separated from `csjn_casos.csv` for compactness. Keyed 1:1 by `caso_id_canonico`. |
| `csjn_casos_materia.csv` | Case | 5,890 | 4 | Subject-matter (*materia*) derivation sidecar, keyed 1:1 by `caso_id_canonico`. Produced by `derivar_materia.py` (a standalone post-parser stage). Under active development; see §8 and §9. |
| `csjn_casos_editorial.csv` | Editorial section | 152 | 7 | Non-judicial editorial content in the volumes: indexes (by parties, by subject, by legislation), *acordadas* (administrative resolutions), and miscellaneous texts. |
| `csjn_editorial_indice_partes.csv` | Index entry | 11,445 | 7 | Individual entries from the alphabetical party index (*índice de partes*) in each volume. Used during pipeline construction for cross-referencing and validation. |

---

## 3. Variable Dictionary — `csjn_casos.csv`

39 columns. **Note:** as of the M26 refactor (parser v22.0), the full-text fields (`considerando_text`, `por_ello_text`, `firma_raw`) live in `csjn_casos_textos.csv`, and `causa_inadmisibilidad` lives in `csjn_casos_recursos.csv`. They are no longer columns of this file.

### Identification

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Unique case identifier. Format: `{tomo}_p{page}`, where `page` is the starting page in the volume (e.g., `329_p5`). |
| `tomo` | integer | Volume number in the Colección de Fallos series. Range: 329–349 (excluding 335–336). |
| `case_name_indice` | string | Case name(s) as listed in the volume's alphabetical party index. Multiple variants separated by ` \| `. May be null for entries not found in the index. |
| `case_name_cuerpo` | string | Case name extracted from the ruling's header in the body text. Typically the full procedural caption (*carátula*). |
| `case_name_cuerpo_legacy` | string | Earlier extraction of the body case name, retained for backward compatibility. |
| `source_file` | string | Source markdown file from which the case was extracted (e.g., `LibroVol329.1.md`). |
| `linea_inicio` | integer | Start line (0-indexed) within the source file. |
| `linea_fin` | integer | Projected end line within the source file. |
| `linea_fin_real` | integer | Actual end line after boundary adjustments. |

### Temporal and jurisdictional

| Variable | Type | Description |
|---|---|---|
| `date` | string | Date of the ruling in Spanish natural-language format (e.g., `7 de febrero de 2006`). Null for 344 entries where no date marker was detected. |
| `tribunal_origen` | string | Name of the lower court whose decision is being reviewed. Null for original-jurisdiction cases and entries where detection failed (193 null). Free text; not normalized. |
| `tribunal_origen_status` | string | Detection status for the lower court. See [Coded Values](#tribunal_origen_status). |
| `is_originaria` | integer (0/1) | Whether the case falls under the Court's original jurisdiction (*competencia originaria*, Art. 117 of the Constitution). 546 cases. |
| `es_queja` | integer (0/1) | Whether the case arises from a *recurso de queja* (complaint appeal filed after a denied extraordinary appeal). 2,297 cases. Also published, denormalized, in `csjn_casos_recursos.csv`. |
| `queja_resultado` | string | Outcome of the *queja*, where applicable. See [Coded Values](#queja_resultado). Null for non-queja cases and quejas with no recorded result. |
| `tipo_cuestion_federal` | string | Type of federal question raised in the extraordinary appeal. See [Coded Values](#tipo_cuestion_federal). Null where none was detected. |

### Outcome (legacy) and voting

| Variable | Type | Description |
|---|---|---|
| `apertura_tipo` | string | Type of ruling opening marker detected: `fallo`, `sentencia`, or null (239 null). |
| `outcome` | string | **LEGACY — frozen (*congelada*).** Single-axis dispositional outcome extracted from the *por ello* clause under the pre-M26 schema. Superseded by the orthogonal axes in `csjn_casos_recursos.csv` (§4). Retained for backward compatibility and reproducibility of earlier analyses; **not** the recommended field for new outcome analysis. See [Coded Values](#outcome). |
| `voting_pattern` | string | Voting configuration of the panel. See [Coded Values](#voting_pattern). |
| `n_jueces` | integer | Total number of judges who signed the ruling. |
| `n_titulares` | integer | Number of permanent (*titular*) justices among the signatories. |
| `n_votos_svoto` | integer | Number of *según su voto* (concurring with separate reasoning) votes. |
| `n_disidencias` | integer | Number of dissenting votes. |
| `is_full_bench` | integer (0/1) | Whether all sitting titular justices participated. 1,541 cases. |
| `is_merit_decision` | integer (0/1) | Whether the ruling addresses the merits of the case (as opposed to procedural dismissals). 2,870 cases. |
| `dictamen_presente` | boolean | Whether the ruling includes an embedded *dictamen* from the Procurador General or Fiscal. `True` 3,434 · `False` 2,263 · `0` 193 (editorial entries). |

### Word counts

| Variable | Type | Description |
|---|---|---|
| `word_count` | integer | Total word count of the ruling, including all zones. |
| `wc_mayoria` | integer | Word count of the majority opinion body (*cuerpo*). |
| `wc_votos` | integer | Aggregate word count of all separate votes (*votos separados*). |
| `wc_considerando` | integer | Word count of the *considerando* section (legal reasoning). |
| `wc_dictamen` | integer | Word count of the *dictamen*, if present. |

### Panel composition

| Variable | Type | Description |
|---|---|---|
| `firma_raw` | string | *(Moved.)* Raw signature-block text now lives in `csjn_casos_textos.csv`. |
| `jueces` | string | Pipe-separated (`\|`) list of judges who signed the ruling, in order of appearance. |
| `jueces_conocidos` | string | Pipe-separated list of judges matched to the canonical list of known CSJN justices and conjueces. |
| `jueces_desconocidos` | float | Count of judges in the signature block not matched to any known justice. Null when signature detection failed entirely. |
| `posiciones` | string | JSON dictionary mapping each judge's name to their voting position (e.g., `{"Petracchi": "mayoria", "Fayt": "en disidencia"}`). |

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
| `admisibilidad` | string | The **access decision**: whether the Court admitted the recourse. See [Coded Values](#admisibilidad). Values: `admite` 2,896 · `sin_marcador` 1,363 · `inadmite` 1,107 · `no_aplica` 524. |
| `disposicion` | string | The **merit verb** (≈ SCDB *caseDisposition*): how the Court disposed of the case on review. See [Coded Values](#disposicion). |
| `es_revision_fondo` | string (si/no) | Whether the ruling reviews the merits (*fondo*) as opposed to deciding on procedural/access grounds only. `no` 3,074 · `si` 2,816. Gates the domain of `parte_ganadora`. |
| `parte_ganadora` | string | **Party-winning** (SCDB *partyWinning* convention): whether the *recurrente* obtained a favorable disposition. Petitioner-centric and binary. See [Coded Values](#parte_ganadora). |
| `reenvia` | string (si/no) | Whether the Court **remands** to the lower court (*reenvía*) rather than resolving the controversy itself. `no` 4,599 · `si` 1,291. **Reliability pending (B130); κ not yet reportable** — see Reliability. |
| `via_recurso` | string | Procedural avenue of access. See [Coded Values](#via_recurso). `recurso_extraordinario` 3,370 · `recurso_ordinario` 328 · null 2,192. |
| `multi_recurso` | string (si/no) | Whether the case resolves more than one recourse jointly. `no` 5,530 · `si` 360. |
| `causa_inadmisibilidad` | string | Specific ground for inadmissibility. Non-null **iff** `admisibilidad = inadmite` (the invariant below). See [Coded Values](#causa_inadmisibilidad). |
| `es_queja` | integer (0/1) | Whether the case arises from a *queja* (denormalized from `csjn_casos.csv`). |

> **Invariant (verified on disk).** `causa_inadmisibilidad ≠ "" ⟺ admisibilidad = "inadmite"`. Exactly **1,107 = 1,107**: every inadmissibility decision carries a ground, and no admitted case does. `causa_inadmisibilidad` is the **reason** for declining access; `admisibilidad` is the **access decision**; `disposicion` is the **merit verb**. Analyses of inadmissibility grounds should use `causa_inadmisibilidad`; analyses of the access decision should use `admisibilidad`.

---

## 5. Variable Dictionary — `csjn_casos_textos.csv`

Full-text fields, one row per case, keyed 1:1 by `caso_id_canonico`.

| Variable | Type | Description |
|---|---|---|
| `caso_id_canonico` | string | Foreign key to `csjn_casos.csv`. |
| `considerando_text` | string | Full text of the *considerando* section (legal reasoning of the majority). |
| `por_ello_text` | string | Full text of the *por ello* clause (the dispositional section where the Court states its operative decision). |
| `firma_raw` | string | Raw text of the signature block as extracted from the source. |

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
| `texto_voto` | string | Full text of the judge's separate vote, if any. Null for judges voting with the majority without a separate opinion. |
| `wc_voto` | integer | Word count of the individual judge's separate vote. 0 for majority-only votes. |
| `tipo_voto_sep` | string | Classification of the separate vote. Coded A–E or `indeterminado`; null for judges without a separate vote (24,941 null). See [Coded Values](#tipo_voto_sep). |
| `fragmenta_ratio` | float | Ratio measuring how fragmented the separate vote text is relative to the total ruling. Null for majority-only votes. |
| `punto_divergencia` | float | Estimated point (0.0–1.0) within the ruling's argumentative structure where the separate vote diverges from the majority. Null for majority-only votes. |

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
| `materia` | string | Derived subject matter. Null for unclassified cases (1,916). |
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

### `csjn_editorial_indice_partes.csv`

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

### `admisibilidad` {#admisibilidad}

The access decision in the recourse layer. **This axis is a synthesis** of the disposition and access signals, not an independent detector; it has no standalone κ (see Reliability).

| Value | N | Description |
|---|---|---|
| `admite` | 2,896 | The Court admitted the recourse (access granted; merits or competence reached). |
| `sin_marcador` | 1,363 | No explicit access marker; admissibility not determinable from access signals alone. |
| `inadmite` | 1,107 | The Court declined to admit the recourse. Carries a `causa_inadmisibilidad` (the invariant). |
| `no_aplica` | 524 | Access axis does not apply (e.g. original jurisdiction, editorial entries). |

### `disposicion` {#disposicion}

The merit verb (≈ SCDB *caseDisposition*). Distribution across 5,890 cases:

| Value | N | Description |
|---|---|---|
| `no_fondo` | 1,867 | No merit disposition (resolved on access/procedural grounds). |
| `deja_sin_efecto` | 1,353 | Prior decision set aside (*deja sin efecto*). |
| `revoca` | 903 | Lower court decision reversed (*revoca*). |
| `no_revision_competencia` | 587 | No merit review; jurisdictional-competence resolution. |
| `confirma` | 537 | Lower court decision affirmed. |
| `no_revision_procesal` | 355 | No merit review; procedural resolution. |
| `no_revision_demanda` | 178 | No merit review; resolution at the demand/claim stage. |
| `nulidad` | 66 | Lower court decision annulled. |
| `nulidad_concesion` | 31 | Annulment of the grant of the appeal (*nulidad de la concesión*). |
| `grant_remand_implicito` | 10 | Implicit grant-and-remand disposition. |
| `modifica` | 3 | Decision modified. |

### `es_revision_fondo` {#es_revision_fondo}

| Value | N | Description |
|---|---|---|
| `no` | 3,074 | The ruling does not review the merits. |
| `si` | 2,816 | The ruling reviews the merits. |

### `parte_ganadora` {#parte_ganadora}

Party-winning under the SCDB *partyWinning* convention: **binary and petitioner-centric** — the *recurrente* either obtains a favorable disposition (`recurrente_gana`) or does not (`recurrente_pierde`). Defined only on merit-review cases (`es_revision_fondo = "si"`).

| Value | N | Description |
|---|---|---|
| `no_aplica` | 3,018 | Axis undefined (no merit review, or no identifiable petitioner outcome). |
| `recurrente_gana` | 2,335 | The *recurrente* obtained a favorable disposition. Following SCDB, partial victories (`disposicion = modifica`) and reversal-and-remand are coded as wins: any favorable element to the *recurrente* is a win. |
| `recurrente_pierde` | 537 | The *recurrente* did not prevail. |

> **Derivation and limitation.** `parte_ganadora` is derived from `disposicion` by a fixed rule (revoca / deja_sin_efecto / nulidad / modifica / grant_remand → `recurrente_gana`; confirma → `recurrente_pierde`). For `modifica`, the win coding is guaranteed by the prohibition of *reformatio in pejus* — a petitioner cannot be left worse off by its own appeal — so a modification it obtained is favorable or neutral, never adverse. The rule assigns relative to a single *recurrente* of reference; in the rare case of genuinely reciprocal appeals (both parties appeal: `multi_recurso = si`) this reference may not match the party an analyst would pick. This imprecision is transversal to all disposition verbs, not specific to `modifica`. The granularity of *who* wins among identified parties (petitioner vs. respondent) is out of scope here and belongs to the prospective party-typing layer (§10).

### `reenvia` {#reenvia}

| Value | N | Description |
|---|---|---|
| `no` | 4,599 | The Court resolves the controversy itself (no remand). |
| `si` | 1,291 | The Court remands to the lower court (*reenvía*). |

> Reliability is **not yet reportable** for this axis (κ = 0.408 on a provisional gold; B130 paused pending manual recoding of the 42-case reversal universe). Use with caution.

### `via_recurso` {#via_recurso}

| Value | N | Description |
|---|---|---|
| `recurso_extraordinario` | 3,370 | Access via the federal extraordinary appeal (REX, Art. 14 Law 48). |
| `recurso_ordinario` | 328 | Access via the ordinary appeal to the Court. |
| *(null)* | 2,192 | Avenue not detected / not applicable. |

### `multi_recurso` {#multi_recurso}

| Value | N | Description |
|---|---|---|
| `no` | 5,530 | A single recourse is resolved. |
| `si` | 360 | More than one recourse is resolved jointly. |

### `causa_inadmisibilidad` {#causa_inadmisibilidad}

Specific ground for inadmissibility. Derived in the recourse layer (`clasificador_causa.py`, single source) and published in `csjn_casos_recursos.csv`. Computed **only when `admisibilidad == "inadmite"`** (the invariant). Grounds are detected from the *por ello* and considerando text, with the controlled vocabulary grounded in the Secretaría de Jurisprudencia's *Recurso Extraordinario* treatise.

| Value | N | Description |
|---|---|---|
| `INADMISIBLE_SIN_CAUSAL_EXPLICITA` | 466 | Inadmissibility declared without a canonical ground detectable in the text (discretionary/silent residual). |
| `ART_280` | 229 | Rejected under Art. 280 CPCCN (discretionary certiorari). |
| `INADMISIBLE_REMITE_DICTAMEN` | 165 | Inadmissibility resolved by reference to the Procurador General's *dictamen*. |
| `CUESTION_ABSTRACTA` | 92 | Rejected because the question became moot. Restricted to genuine mootness: cases that also decide the merits are recorded as `admite`. |
| `ACORDADA_4_2007` | 51 | Rejected for non-compliance with the formal requirements of *Acordada* 4/2007. |
| `FALTA_SENTENCIA_DEFINITIVA` | 43 | Rejected for absence of a final judgment (a prerequisite for the REX). |
| `CADUCIDAD_INSTANCIA` | 13 | Dismissed for lapse of instance (treatise §2.6). |
| `RESOLUCION_NO_RECURRIBLE` | 12 | The challenged resolution is not subject to appeal. |
| `FALTA_FUNDAMENTACION_AUTONOMA` | 12 | The appeal lacks the required autonomous grounds. |
| `DESISTIMIENTO` | 10 | Withdrawal — predominantly default on the deposit requirement (art. 286 CPCCN), not voluntary termination (treatise §2.1.11). |
| `FUERA_DE_TERMINO` | 10 | Appeal filed out of time. |
| `INTERPOSICION_INCORRECTA` | 2 | REX filed before the wrong forum (treatise §1.2.2). |
| `DEPOSITO_PREVIO` | 2 | Rejected in connection with the prior-deposit requirement. |
| *(null)* | 4,783 | `admisibilidad ≠ inadmite` (not applicable). |

### `outcome` (LEGACY — frozen) {#outcome}

> **Frozen field.** Single-axis disposition under the pre-M26 schema, superseded by §4. Retained for reproducibility only. Distribution across 5,890 cases:

| Value | N | | Value | N |
|---|---|---|---|---|
| `hace_lugar` | 1,401 | | `nulidad_concesion` | 31 |
| `competencia` | 925 | | `sin_dispositivo` | 26 |
| `desestima` | 806 | | `inadmisible_280` | 24 |
| `procedente` | 759 | | `inadmisible` | 23 |
| `otro` | 362 | | `improcedente` | 23 |
| `confirma` | 345 | | `caducidad` | 13 |
| `revoca` | 340 | | `desierto` | 12 |
| `rechaza` | 276 | | `desistimiento` | 10 |
| *(null)* | 193 | | `cautelar` | 5 |
| `abstracto` | 148 | | `inadmisible_acordada_4` | 5 |
| `deja_sin_efecto` | 82 | | | |
| `nulidad` | 42 | | | |
| `mal_concedido` | 39 | | | |

### `tipo_cuestion_federal` {#tipo_cuestion_federal}

| Value | N | Description |
|---|---|---|
| `cuestion_federal` | 1,302 | Ordinary federal question (*cuestión federal* in the strict sense). |
| `arbitrariedad` | 883 | Arbitrariness doctrine invoked (*arbitrariedad de sentencia*). |
| `mixto` | 677 | Both an ordinary federal question and arbitrariness. |
| *(null)* | 3,028 | No federal-question type detected. |

### `queja_resultado` {#queja_resultado}

Outcome of the *recurso de queja*, where `es_queja = 1`.

| Value | N | | Value | N |
|---|---|---|---|---|
| *(null)* | 3,794 | | `abstracta` | 16 |
| `hace_lugar` | 1,211 | | `suspendida` | 15 |
| `desestima` | 524 | | `desistida` | 10 |
| `procedente` | 173 | | `inadmisible` | 1 |
| `admisible` | 101 | | `nula` | 1 |
| `agreguese` | 25 | | | |
| `rechaza` | 19 | | | |

### `voting_pattern` {#voting_pattern}

| Value | N | Description |
|---|---|---|
| `unanime` | 3,529 | All judges joined a single opinion. |
| `disidencia` | 1,113 | At least one judge dissented from the majority disposition. |
| `segun_su_voto` | 746 | All judges agreed on the disposition but at least one filed separate concurring reasoning. |
| `mixed` | 293 | Combination of dissents and concurrences. |
| *(null)* | 193 | Not available (editorial entries). |
| `sin_firma` | 16 | No judicial signatures could be extracted. |

### `tipo_entrada` {#tipo_entrada}

| Value | N | Description |
|---|---|---|
| `fallo` | 5,697 | Full ruling with complete text. |
| `sumario_con_link` | 160 | Summary entry with a cross-reference to another volume. |
| `sumario_editorial` | 33 | Editorial summary without full ruling text. |

### `posicion` (in `csjn_casos_votos.csv`) {#posicion}

| Value | N | Description |
|---|---|---|
| `mayoria` | 23,931 | Judge voted with the majority. |
| `en disidencia` | 2,230 | Judge dissented from the majority disposition. |
| `según su voto` | 1,528 | Judge concurred in the result but filed separate reasoning. |
| `por su voto` | 8 | Variant of *según su voto*. |

### `tipo_voto_sep` (in `csjn_casos_votos.csv`) {#tipo_voto_sep}

Classification of separate votes by their structural relationship to the majority. Applied only to judges with a separate vote (2,756 votes; null for the remaining 24,941). **Schema A–E under development.**

| Value | N | Description |
|---|---|---|
| `indeterminado` | 1,333 | Could not be classified into a defined category. |
| `B` | 556 | *To be documented.* |
| `D` | 534 | *To be documented.* |
| `A` | 161 | *To be documented.* |
| `C` | 114 | *To be documented.* |
| `E` | 58 | *To be documented.* |

### `zona` (in `csjn_casos_zonas.csv`) {#zona}

| Value | N (segments) | Description |
|---|---|---|
| `header_pagina` | 46,144 | Page header inserted by the publisher. Not part of the ruling. |
| `cuerpo` | 23,043 | Body of the majority opinion (*considerandos* and reasoning). |
| `dictamen` | 17,012 | Opinion of the Procurador General or Fiscal, embedded before the Court's decision. |
| `dispositivo` | 12,500 | Operative section (*por ello* clause). |
| `firma` | 10,616 | Signature block listing the judges' names. |
| `sumario` | 8,007 | Editorial summary printed before the ruling, authored by the publisher. |
| `epilogo` | 7,618 | Trailing text after the signature: notifications, dissent notes, annotations. |
| `residuo_caso_anterior` | 7,541 | Residual text belonging to the preceding case on a shared page. |
| `apertura` | 5,776 | Opening section: case caption, date, initial procedural framing. |
| `voto_separado` | 3,194 | Separate opinion (concurrence or dissent) by an individual judge. |

### `tribunal_origen_status` {#tribunal_origen_status}

| Value | N | Description |
|---|---|---|
| `apelado_detectado` | 3,879 | Lower court identified from the *Tribunal de origen* marker. |
| `sin_marcador` | 1,272 | No marker found; populated from other heuristics or left as free text. |
| `originaria` | 546 | Original-jurisdiction case (no lower court). |
| *(null)* | 193 | Not available. |

### `status_localizacion` {#status_localizacion}

| Value | N | Description |
|---|---|---|
| `ok` | 5,615 | Standard localization via page map and opening markers. |
| `ok_sin_marcador_apertura` | 180 | Located without the standard opening marker. |
| `ok_ancla_catalogo` | 27 | Located using the volume catalog as anchor. |
| `fallo_cruza_archivos` | 27 | Ruling spans two source files. |
| `ok_cortado_en_indice` | 19 | Case spans a page boundary indicated in the index. |
| `ok_sin_marcador_apertura_ancla_catalogo` | 16 | Compound: no opening marker + catalog anchor. |
| `ok_sin_marcador_apertura_ancla_vistos` | 5 | Compound: no opening marker + *vistos* anchor. |
| `ok_ancla_vistos` | 1 | Located using the *vistos* clause as anchor. |

### `status_fin` {#status_fin}

| Value | N | Description |
|---|---|---|
| `fin_extendido_pag_compartida` | 5,689 | End extended to accommodate a shared page with the next ruling. |
| `fin_por_firma_actual` | 115 | End determined by the ruling's own signature block. |
| `fin_por_editorial` | 46 | End determined by the start of an editorial section. |
| `fin_dentro_bloque` | 23 | End falls within the ruling's allocated block. |
| `fin_no_detectado` | 17 | End boundary could not be detected reliably. |

### `pista_fin` {#pista_fin}

| Value | N | Description |
|---|---|---|
| `caratula_siguiente` | 5,196 | Next ruling's case caption found. |
| `sumario_siguiente` | 339 | Next ruling's editorial summary found. |
| `marcador_apertura_siguiente` | 177 | Next ruling's opening marker found. |
| `firma_actual` | 115 | Current ruling's own signature block used. |
| `editorial_siguiente` | 46 | Start of editorial content found. |
| `fallback_catalogo` | 17 | Catalog-based fallback used. |

### `materia`, `materia_capa`, `materia_fuente` (in `csjn_casos_materia.csv`) {#materia}

> **Under active development.** Subject-matter is derived from `csjn_casos` and `csjn_casos_textos` by a standalone, deterministic, layered stage (`derivar_materia.py`), re-runnable without re-parsing. The classifiable universe excludes original-jurisdiction cases. Counts below are a snapshot.

`materia_capa` (the confidence tier):

| Value | N | Description |
|---|---|---|
| `capa1` | 2,307 | Derived from the specialized court of origin (`tribunal_origen` → fuero → materia). Highest precision. |
| `capa2` | 1,508 | Derived from secondary signals: cited statutes, parties, case object, keywords, co-occurrence engine. |
| `pendiente_capa2` | 1,163 | Not classifiable with available signals (no anchor or unresolved tie). |
| `originaria` | 546 | Original-jurisdiction case (Art. 117). Terminal category, excluded from the coverage denominator. |
| `no_aplica` | 193 | Editorial-summary entries. |
| `capa1_refinado` | 159 | A `capa1` label overridden by a tax-authority signal (CA → `tributario`). |
| `sui_generis` | 8 | Impeachment juries and judicial councils. |
| `residual` | 6 | Arbitral tribunals and OCR/anaphora artifacts. |

`materia` values (when classified): `civil_comercial` (1,013), `contencioso_administrativo` (940), `penal` (686), `laboral` (457), `previsional` (357), `tributario` (350), `ambiental` (57), `constitucional` (36), `electoral` (29), `salud` (20), `consumo` (18), `cambiario` (8), `lesa_humanidad` (3); null (1,916).

---

## 9. Reliability — inter-rater Cohen's κ (recourse-layer axes)

The M26 recourse-layer axes were validated against a hand-coded gold standard by computing Cohen's κ between the pipeline prediction and the human coding (`kappa_confiabilidad.py`; bootstrap 95% CI, B = 5,000). This measures agreement corrected for chance between parser and gold — it is **not** a double-coding (codebook-reproducibility) κ.

| Axis | N | Agreement | κ | 95% CI | Landis–Koch |
|---|---|---|---|---|---|
| `es_revision_fondo` | 300 | 0.970 | **0.940** | [0.899, 0.973] | almost perfect |
| `via_recurso` | 133 | 0.985 | **0.943** | [0.850, 1.000] | almost perfect |
| `disposicion` | 140 | 0.943 | **0.912** | [0.847, 0.966] | almost perfect |
| `parte_ganadora` | 134 | 0.933 | **0.784** | [0.632, 0.908] | substantial |
| `reenvia` | 75 | 0.827 | 0.408 | [0.160, 0.635] | moderate — **not reportable** |

> **Notes.** (a) `admisibilidad` is a synthesis of the disposition/access signals (≈99.9% relabel-consistent), not an independent detector, so it carries no standalone κ. (b) `parte_ganadora` is binary on both sides: the pipeline derives `recurrente_gana`/`recurrente_pierde` with no `parcial` value (`modifica → gana`), and the gold's original three-value coding (gana / parcial / pierde) was collapsed to the same binary scheme; the three-value gold is retained in the repository so the collapse is auditable. The κ remains capped below 1.0 by seven residual role-inversions preserved as genuine disagreements. (c) `reenvia` κ is moderate and **not reportable**: the reversal universe requires manual recoding (B130, in progress) before a reliable estimate over the full reversal set can be published.

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

1. **Legacy `outcome` residual (`otro`: 362).** The frozen `outcome` field retains an unclassified residual. This field is superseded by the §4 axes and is not the recommended basis for outcome analysis.
2. **`reenvia` reliability pending (B130).** κ for the remand axis is not yet reportable; manual recoding of the reversal universe is in progress. Treat `reenvia` as provisional.
3. **Party identity/type not derived.** `parte_ganadora` records whether the *recurrente* won, but the dataset does not yet identify the parties (actor/demandado) or their type (individual, business, state, etc.). This precludes a `decisionDirection`-style analysis (which party type the Court favors). The raw material is present (captions, party index); the derivation is a planned layer (see §10 and the technical-debt register).
4. **Missing signatures (`sin_firma`: 16 cases, 0.3%).** OCR artifacts or non-standard formatting.
5. **Missing dispositional clause (`sin_dispositivo` in legacy `outcome`: 26 cases).** No extractable *por ello* clause.
6. **Dates in natural language.** `date` is Spanish free text, not ISO. 344 entries (5.8%) have no date.

### Coverage

7. **Volumes 335–336 not yet included.** Volumes 335–336 are not yet included in this release. They were unavailable in digitized form at processing time and are planned for inclusion in a future version, once physical copies are obtained and OCR-processed. They cover parts of the 2012–2013 terms.
8. **Non-normalized lower courts.** 1,272 entries have `sin_marcador` status; even where detected, court names are not normalized.
9. **No *secretaría letrada* information.** The dataset does not identify which law-clerk office drafted each ruling; this is absent from the published volumes.

### Methodological

10. **OCR-dependent source text.** Source markdown was produced by OCR digitization of printed volumes; residual OCR errors may affect extraction accuracy.
11. **`materia` under development.** Coverage and taxonomy of the subject-matter sidecar are not final (see §8).
12. **Separate-vote typology (A–E) under development.** `tipo_voto_sep` uses a provisional schema; 1,333 of 2,756 separate votes (48.4%) are `indeterminado`.
13. **Editorial entries.** 193 entries (`tipo_entrada ≠ fallo`) are summaries/cross-references with null analytical fields; filter via `tipo_entrada = 'fallo'` for ruling-level analysis.

---

## 12. Pipeline Methodology

The dataset is produced by a staged Python pipeline:

1. **`detectar_paginas.py`** — Reads the OCR-digitized markdown source files and builds a page map (`mapa_paginas.csv`).
2. **`construir_catalogo.py`** — Parses the alphabetical party index to produce a catalog of expected cases (`catalogo.csv`).
3. **`cruzar_catalogo_y_mapa.py`** — Cross-references catalog and page map to produce a localization table (`fallos_localizados.csv`).
4. **`parser.py`** (v22.0) — The main extraction engine. Detects case openings, extracts caption, date, judges, voting positions, and the full text of each structural zone. Produces `csjn_casos.csv`, `csjn_casos_votos.csv`, `csjn_casos_zonas.csv`, and `csjn_casos_textos.csv`.
5. **Recourse-and-disposition deriver** — `derivar_recursos.py` plus the M26 classifiers (`clasificador_disposicion.py`, `clasificador_via.py`, `clasificador_admision.py`, `clasificador_causa.py`) produce `csjn_casos_recursos.csv`.
6. **`derivar_materia.py`** — Standalone subject-matter derivation producing `csjn_casos_materia.csv`.

`parser_editorial.py` handles non-judicial editorial sections separately. `auditar_fallo.py` audits individual cases against the source text. Reliability validation lives in `scripts/validacion/` (`kappa_confiabilidad.py`).

### Versioning

Pipeline scripts carry embedded `__version__` strings. This dataset was produced with **parser.py v22.0** and the M26 recourse layer. The full version history and bug registry are in the repository's `BITACORA.md` (session journal) and `DEUDA_TECNICA.md` (technical-debt and bug tracker).

---

## 13. Source and Legal

**Source:** *Colección de Fallos de la Corte Suprema de Justicia de la Nación*, volumes 329–349 (excluding 335–336). Digitized versions available at [https://sjconsulta.csjn.gov.ar](https://sjconsulta.csjn.gov.ar).

**Legal status of source material:** The rulings of the Argentine Supreme Court are official public documents and are not subject to copyright. The editorial summaries (*sumarios*) included in the *Colección de Fallos* are authored by the publisher and may be subject to separate copyright. The dataset labels these as `zona = "sumario"` and does not claim authorship over them.

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

*Codebook version: 2.0 — Generated for corpus-csjn parser v22.0 (M26 recourse layer).*
