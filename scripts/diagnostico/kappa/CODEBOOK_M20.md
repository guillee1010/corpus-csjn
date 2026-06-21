# CODEBOOK M20 — disposición + parte_ganadora (validación ciega)

**Frame:** `planilla_M20_blind_n300.csv` (n=300, mismo frame Marco A de M19).
**Método:** codificación ciega. NO abrir `M20_clave_parser_n300.csv` hasta terminar de codificar.
**Universo:** disposición y parte_ganadora viven SOLO sobre revisiones de fondo. Por eso el gate se codifica primero.

---

## 1. `cod_es_revision_fondo`  → TODOS los 300

¿La Corte revisa el fondo de una sentencia anterior (la confirma, revoca, deja sin efecto, anula o modifica)?

- `si` — resuelve sobre el mérito de la decisión recurrida.
- `no` — competencia, queja desestimada, inadmisible (280/acordada 4), abstracto, desierto, desistimiento, cuestiones puramente procesales. NO codificar disposición ni parte_ganadora en estos.

> Esta columna valida el gate `is_merit`. Mirá con lupa los `outcome="otro"`: ahí es donde puede haber una revisión de fondo mal clasificada (falso negativo del gate).

## 2. `cod_disposicion`  → SOLO si `cod_es_revision_fondo = si`

Qué hace la Corte con la sentencia de abajo (valores SCDB):

- `revoca` — revoca / deja sin efecto y resuelve.
- `deja_sin_efecto` — deja sin efecto (típico 14 / arbitrariedad) y reenvía. Si dudás entre revoca y deja_sin_efecto, mirá si reenvía: reenvío ⇒ `deja_sin_efecto`.
- `nulidad` — declara nulo / nulidad de todo lo actuado.
- `confirma` — confirma la sentencia / rechaza el recurso o la queja por infundados.
- `modifica` — modifica parcialmente (sustituye monto, pena, alcance) sin revocar ni confirmar en bloque.

Dejá vacío si revisión=sí pero el dispositivo es ilegible/cortado **incluso yendo a la fuente** (anotalo en `notas_m20`).

## 3. `cod_reenvia`  → SOLO si revisión=sí

- `si` — manda devolver los autos / dictar nuevo pronunciamiento.
- `no` — resuelve definitivamente sin reenvío.

## 4. `cod_parte_ganadora`  → SOLO si revisión=sí — **CODIFICAR INDEPENDIENTE, NO DERIVAR DEL VERBO**

Pregunta guía: *¿la parte que llevó el caso a la Corte (el recurrente) obtuvo lo que pedía?*

- `recurrente_gana` — sí, obtuvo lo que buscaba.
- `recurrente_pierde` — no, se rechaza su planteo.
- `parcial` — obtuvo una parte; resultado mixto.
- `reenvio_sin_resultado` — vuelve a tribunal inferior y el ganador de fondo todavía no está determinado.
- `no_aplica` — no se puede atribuir (multi-recurrente, etc.).

> **Clave metodológica:** no codifiques esto mecánicamente desde el verbo del punto 2. Leé el resultado. Si coincide con lo que diría la regla, perfecto (confirma la base-rate); si NO coincide, ahí está la señal que valida la regla de derivación.

---

## Reglas operativas

- **`flag_revisar_fuente=1`** (12 casos): el `por_ello_text` puede estar truncado (running-head, B118). Andá a `source_file` + `linea_inicio`/`linea_fin_real` y codificá el dispositivo real.
- Ante duda genuina, codificá y dejá la duda en `notas_m20` (no fuerces un valor).
- Al terminar: `python analizar_validacion_M20.py planilla_M20_blind_n300.csv M20_clave_parser_n300.csv`

## Límites conocidos de este frame (declarar en la tesis)

- `nulidad` (n≈2) y `modifica` (n≈0): no validables acá; requieren oversampling dirigido (mini-frame), igual que valores raros en M19.
- `grant_remand_implícito` cae 1 vez en el frame (62 en el corpus): la **decisión #3** (default del reenvío implícito) no se resuelve con n=1; necesita pase aparte sobre los 62.
- Cola multi-recurrente (~2,1%): fuera de alcance de M20; va por PoC propio (#2) con `no_aplica` o fork por parte.
