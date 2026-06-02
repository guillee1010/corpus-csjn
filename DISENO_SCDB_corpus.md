# Diseño: mapeo SCDB → corpus-csjn

**Fuente:** *The Supreme Court Database Codebook*, v2025_01 (121 pp., 61 variables, Spaeth/Washington University–PSU). Documento de trabajo, NO de pipeline. Insumo del **Frente B (materia)** y del candidato de refactor **outcome → disposición + parte**.

**Estado del corpus de referencia:** parser v18.20, 5669 fallos + 193 sumarios.

---

## 0. Tesis de fondo del mapeo

El SCDB es el estándar de oro del área y nuestra arquitectura ya está alineada con él (separación caso/juez = `csjn_casos` / `csjn_casos_votos`; `n_votos`/`n_disidencias` ≈ `majVotes`/`minVotes`). Lo que NO tenemos que copiar es su lista de valores (derecho federal de EE.UU.); lo que SÍ sirve es:

1. **La arquitectura de las variables** (qué dimensiones separan y por qué).
2. **El estándar de reliability** (codificación a mano + reglas de scope documentadas por valor → conecta con nuestro kappa pendiente, M19).

Diferencia estructural que nos favorece: el SCDB codifica `issue`/`issueArea` (materia) A MANO, separada del tribunal de origen, **porque en EE.UU. los tribunales son de competencia general** y el origen no predice la materia. En Argentina el fuero es ESPECIALIZADO → `tribunal_origen → materia` es viable justo donde el método del SCDB no podría. Tomamos de ellos el QUÉ (taxonomía de 2 niveles) y explotamos una propiedad de nuestro sistema para el CÓMO.

---

## 1. Refactor candidato: `outcome` → dos ejes (disposición vs parte)

**Problema.** Nuestro `outcome` único mezcla dos dimensiones que el SCDB mantiene separadas en tres variables:

| SCDB | Qué codifica | Valores |
|---|---|---|
| `lcDisposition` | qué hizo el tribunal inferior con lo que revisó | 12 (mismo vocabulario que caseDisposition) |
| `caseDisposition` | qué le hace la Corte a la sentencia de abajo (afirma / revoca / revoca y reenvía / deja sin efecto y reenvía…) | 11 |
| `partyWinning` | quién ganó (recurrente gana total/parcial / pierde) | 3, **DERIVADO por regla** de caseDisposition |

Elegancia del SCDB: un solo diccionario de disposiciones sirve para el tribunal de abajo Y para la Corte (`lcDisposition`/`caseDisposition` comparten valores); y `partyWinning` no se codifica, **se computa**.

**Cómo se proyecta sobre nuestros 20 valores de `outcome` (v18.20):**

| outcome actual | n (fallos) | eje | nota |
|---|---|---|---|
| `revoca` | 343 | DISPOSICIÓN | reverse |
| `confirma` | 327 | DISPOSICIÓN | affirm |
| `deja_sin_efecto` | 89 | DISPOSICIÓN | vacate |
| `nulidad` | 61 | DISPOSICIÓN | — |
| `hace_lugar` | 1355 | PARTE (resultado sustantivo) | recurrente gana |
| `rechaza` | 267 | PARTE | recurrente pierde |
| `procedente` | 754 | PARTE / mixto | depende del recurso |
| `desestima` | 547 | PARTE / gate | — |
| `competencia` | 863 | EJE PROPIO (proceso) | no es disposición ni parte; ya separado |
| `inadmisible_280` | 240 | GATE | causa_inadmisibilidad lo refleja |
| `inadmisible_acordada_4` | 50 | GATE | idem |
| `inadmisible` | 24 | GATE | idem |
| `mal_concedido` | 39 | GATE | idem |
| `improcedente` | 21 | GATE | idem |
| `desierto` | 13 | GATE | idem |
| `caducidad` | 11 | GATE | causa CADUCIDAD_INSTANCIA |
| `desistimiento` | 10 | GATE | causa DESISTIMIENTO |
| `abstracto` | 89 | GATE/terminal | causa CUESTION_ABSTRACTA |
| `sin_dispositivo` | 25 | N/A | sin dispositivo legible |
| `otro` | 541 | catch-all | termómetro de cobertura (9,3%) |

**Lectura.** Ya tenemos parcialmente separado el eje GATE (vía `causa_inadmisibilidad`, H092) y el eje PROCESO (vía `is_originaria`/`tribunal_origen_status`, y `competencia` deslindado en H104). Lo que sigue mezclado es **disposición procesal** (revoca/confirma/deja_sin_efecto/nulidad) con **resultado de parte** (hace_lugar/rechaza). El refactor SCDB sería:

- `disposicion` (nueva): reverse / affirm / vacate / remand / nulidad / … — qué le hace la Corte a la sentencia revisada.
- `parte_ganadora` (nueva, DERIVADA): actora/recurrente gana total / parcial / pierde — computada de `disposicion` + apertura, no codificada a mano.
- `outcome` sobreviviría como vista o se deprecaría, según convenga al análisis.

**Cautela REE.** Es un cambio de comportamiento grande (toca el campo más usado, rompe el golden masivo, re-titular obligado). NO atómico, NO para una sesión suelta. Diseñar la equivalencia primero (qué `outcome` mapea a qué par disposición×parte) y validar contra los n=300. Candidato de frente propio, posterior al cierre de la cola de bugs de outcome (B109/B105).

---

## 2. Frente B — `materia` con molde SCDB

**Molde:** `issueArea` (14 áreas grandes) ⊃ `issue` (260 finos, numerados por rangos: 10000s penal, 20000s derechos civiles, …). Arquitectura de DOS niveles con rangos numéricos.

**Advertencia que el propio SCDB documenta:** las áreas más grandes (criminal procedure, civil rights, economic activity) quedan "sobre- y sub-especificadas"; recomiendan declarar qué sub-issues incluye cada análisis. → **Para nosotros:** no armar materias-paraguas demasiado anchas. Si "civil-comercial" se come media base, subdividir desde el diseño (p. ej. daños / contratos / concursos / familia).

**Taxonomía propuesta (borrador, derecho argentino, 2 niveles):**

- **laboral** → (despido / accidentes-ART / previsional-laboral / colectivo)
- **previsional / seguridad social** → (jubilaciones / reajustes / ANSeS)
- **contencioso-administrativo** → (empleo público / responsabilidad estatal / tributario-CA / regulatorio)
- **tributario** → (impuestos nacionales / aduanero / provincial)
- **penal** → (proceso penal / fondo / ejecución)
- **civil-comercial** → (daños / contratos / concursos-quiebras / familia / reales)
- **constitucional** → (control de constitucionalidad / amparos / derechos fundamentales)
- **electoral / partidos**
- **competencia (conflictos)** → ya parcialmente en `outcome=competencia` (863)

(Cerrar el vocabulario ANTES de extraer. Validar nombres contra el Anuario CSJN — ya tenemos CSV de referencia de H083 con secretaría/materia.)

**Extracción por capas (orden = limpieza de señal):**

1. **Capa 1 — `tribunal_origen → fuero → materia`** (lookup, alta precisión). PRE-REQUISITO: **B114** (tribunal_origen fragmentado por OCR, ver DEUDA). Determinístico para fuero nacional especializado: CNAT→laboral, Cám. Fed. Seg. Social→previsional, Cont. Adm.→CA, Casación Penal→penal, Civil/Comercial→civil-comercial, Nac. Electoral→electoral.
2. **Capa 2 — provinciales + SIN_TRIBUNAL (1791).** Multi-materia: el tribunal NO desambigua. Señal secundaria = normas citadas en el considerando (24.241→previsional, LCT/20.744→laboral, 11.683→tributario, Cód. Penal→penal) + partes (validado por SCDB: las party variables ayudan a ubicar la materia).
3. **Capa 3 — originaria (477).** Materia propia (competencia entre Estados, CA federal). Regla aparte.

**Validación:** `cod_materia` sobre los n=300 ya codificados (M19); precision/recall por valor, igual que el titular.

---

## 3. Variables SCDB candidatas a sumar (alto valor para la tesis H1–H5)

| SCDB | Qué es | Por qué nos sirve | ¿Lo tenemos? |
|---|---|---|---|
| `majOpinWriter` | autor de la opinión de la Corte | autoría de la mayoría = núcleo de estrategia colegiada | parcial (extraemos autor del texto) |
| `majOpinAssigner` | quién ASIGNA la opinión (regla: si el presidente está en la mayoría asigna él; si no, el decano de la mayoría) | **es literalmente la tesis** (diseño institucional de la decisión colegiada) | NO. Salvedad: SCDB lo deriva del voto de conferencia (no público acá; ellos admiten ~16% error). Derivable por regla en CSJN si se conoce composición + antigüedad |
| `declarationUncon` | declaró inconstitucional norma federal/provincial/municipal | control de constitucionalidad, eje central CSJN | NO — variable nueva de alto valor |
| `precedentAlteration` | el fallo alteró precedente propio | overruling / estrategia doctrinaria | NO |
| `certReason` / `jurisdiction` | vía de acceso y razón de admisibilidad | más rico que `es_queja`; emparenta con `causa_inadmisibilidad` | parcial |
| `decisionType` | signed opinion / per curiam / etc. | tipo de pronunciamiento; cruza con sumarios | parcial (apertura_tipo) |
| `lcDispositionDirection` / `decisionDirection` | dirección ideológica (liberal/conservador) de la decisión | el SCDB la codifica; en CSJN es discutible/no trivial | NO — evaluar si aplica al contexto argentino |

**Nota sobre `majOpinAssigner`:** el SCDB lo construye con la regla de asignación + composición de la mayoría. En Argentina no hay voto de conferencia público, pero la REGLA institucional (presidente de la Corte / antigüedad) sí es conocida y la composición de la mayoría la tenemos por `votos`. Es derivable con supuestos explícitos — material directo de la tesis, a discutir con el director.

---

## 4. Lo que ya hacemos alineado al SCDB (no tocar)

- Separación caso / juez = `csjn_casos` / `csjn_casos_votos` (= case-centered / justice-centered del SCDB).
- `n_votos` / `n_disidencias` ≈ `majVotes` / `minVotes`.
- voto por juez por caso = `vote`/`opinion`/`direction` del bloque justice-centered.
- `voting_pattern` (unanime/disidencia/segun_su_voto/mixed) ≈ combinación de `splitVote` + direcciones.

---

## 5. Accionables (orden sugerido)

1. **B114** — normalizar `tribunal_origen` (pre-requisito capa 1). PoC barato: deshifenar/colapsar variantes y medir cuántos valores distintos quedan.
2. **Frente B capa 1** — lookup tribunal→materia; medir % de cobertura sobre el corpus. PoC barato antes de capas 2-3.
3. **Cerrar taxonomía de materia** (vocabulario controlado, validar contra Anuario H083) ANTES de extraer.
4. **Refactor outcome→disposición+parte** — frente propio, grande, posterior a B109/B105; diseñar equivalencia + re-titular.
5. **Variables nuevas de tesis** (`declarationUncon`, `majOpinAssigner` derivado, `precedentAlteration`) — evaluar costo/valor con el director, una por una.

**Método (recordatorio REE):** vocabulario controlado primero; extracción por capas ordenadas por limpieza de señal; validación contra n=300 con precision/recall por valor; cambios de comportamiento = re-golden consciente + re-titular; nada de switches globales no atómicos.
