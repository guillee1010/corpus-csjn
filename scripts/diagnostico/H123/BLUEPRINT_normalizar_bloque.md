# Blueprint — sesión `normalizar_bloque` (corpus-csjn)

Branch sugerido: `refactor/normalizar-bloque` (o continuar en `refactor/m20-disposicion`).
Clase de cambio: **B112 (re-golden masivo, no atómico).** Disciplina: **PoC-mide-primero → decidir → commit.**

---

## 0. Causa raíz confirmada (no re-diagnosticar)

La deshifenación y el saltado de headers hoy son **per-función** (~10 call-sites de `_unhyphenate`; `RE_PAGE_HEADER` en ~11 sitios, siempre para saltar). El que **arma** el `por_ello` —`_barrer`— NO limpia al juntar el chunk; recién `classify_outcome` deshifena *después* de recibirlo. Resultado: la **extracción** ve texto sucio, solo la **clasificación** lo limpia, e inconsistentemente.

- Mecanismo B122/B118: el chunk de `_barrer` (parser ~3091) topa a 6 líneas o al primer `.`; el running-head intercalado (`NNN DE JUSTICIA DE LA NACION TTT`) está en línea propia, gasta presupuesto, y el chunk corta sobre el banner antes del `.` real → `por_ello` truncado → disposición jurisdiccional cae a `otro`. Confirmado contra el gold (banco de 42, 2/3 marcados `ZONA` a mano).
- `RE_PAGE_HEADER` (línea 204) NO matchea el banner real (está anclada a frase-sola o número-solo; el banner real es `número + frase + número`). Hace falta `RE_RUNNING_HEAD` nueva.

## 1. Arquitectura: localizar → limpiar → extraer

Orden de pasadas (resuelve los índices):

1. **Localización sobre crudo** — `detectar_fin_real` / `construir_bloque_desde_localizacion` fijan `linea_inicio`/`linea_fin_real`. Los headers siguen presentes acá (ruido-a-saltar, como hoy). Índices clavados.
2. **`normalizar_bloque(bloque)` → vista limpia** — post-localización, pre-extracción. Devuelve una copia del bloque (misma longitud, índices preservados):
   - **Enmascarar running-heads a `""` in-place** (NO eliminar — preservar conteo de líneas y ventana de firma `k+1..k+41`).
   - **Deshifenar cada línea.**
   - **PRESERVAR marcadores editoriales** (`RE_EDITORIAL_ANY`: ACORDADAS/ÍNDICE) — son señal de corte en `detectar_fin_real` (línea 2591). NO tocarlos.
3. **Extracción sobre la vista limpia** — `resolver_dispositivo`/`_barrer`, `extraer_considerando`, detección de firma matchean contra la vista limpia.

### Doble vista (la decisión arquitectónica a clavar ANTES de codear)

- **Vista limpia** → match/extracción (dispositivo, considerando, gate, materia).
- **Crudo** → campos **persistidos**: `case_name_*`, `firma_raw`, y el **sidecar `csjn_casos_textos.csv`** (fidelidad). `tribunal_origen` ya tiene su propio guard (H111) — dejarlo como está.
- Backstop: si una función lee la vista equivocada, corrompe (persistir limpio) o pierde match (extraer sobre crudo). Threadear ambas vistas por `procesar_archivo` es el costo de ingeniería real, más que las regex.

### `RE_RUNNING_HEAD` (nueva)

```python
RE_RUNNING_HEAD = re.compile(
    r"^\s*(\d{1,4}\s+)?(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)(\s+\d{1,4})?\s*$",
    re.I)
```
Matchea `147 DE JUSTICIA DE LA NACION 329`, `329 FALLOS DE LA CORTE SUPREMA`, y la frase sola.

## 2. PoC — harness de medición (NO sella nada)

4 configs sobre la **misma muestra** (correr el parser con cada normalización on/off):

| config | headers | guión |
|---|---|---|
| baseline | off | off |
| +headers | on | off |
| +guión | off | on |
| **+ambos** | on | on |

Muestra: **banco de 42** (B122) + **gold n300** + corte corpus-wide (sample ~500 o full si el tiempo da).

Métricas por config:
- `por_ello` no vacío (dispositivos capturados) y `sin_dispositivo` count.
- Distribución de `outcome` / `is_merit`.
- **Exactitud contra el gold** (`cod_disposicion`, `cod_es_revision_fondo`) sobre los que caen en el n300.
- Marginal aislado: Δ(+headers − baseline), Δ(+guión − baseline).
- **Interacción:** Δ(+ambos) vs Δ(+headers)+Δ(+guión) — NO asumir aditividad; +ambos es lo que se commitea.

## 3. Compuerta de decisión (big-bang IFF)

Commitear `normalizar_bloque` (headers+guión juntos) **si y solo si**:
- (a) +ambos es **net-positivo** contra el gold (más aciertos que regresiones en `cod_disposicion`/`cod_es_revision_fondo`).
- (b) recupera el banco de 42 (la cláusula jurisdiccional vuelve → reclasifica a competencia/originaria).
- (c) `check_regresion` corpus-wide: flips **concentrados** en la familia truncado/hifenado, NO espuriando en otras columnas.
- **Si solo uno gana:** shippear solo ese (headers-solo o guión-solo), el otro a DEUDA.
- **Si la combinada es sub-aditiva o net-negativa:** parar, re-diseñar; no commitear.

## 4. Commit (post-go)

- Una `normalizar_bloque`, re-golden consciente.
- `check_regresion` [FAIL esperado, flips deliberados] → verificar perímetro.
- Manifest si tocó cadena (probable: cambia `por_ello`/`considerando`/derivados → re-sellar).
- Docs: DEUDA directo (cerrar B122/B118 como subsumidos por la pre-pasada); BITACORA/CHANGELOG append.
- **Versión parser: bump MAJOR** (v18.26 → v19.0) — es cambio de arquitectura, no fix.
- El parche B122 local NO se shippea (subsumido).

## 5. Riesgos vivos

- **Doble-vista mal threadeada** → corrupción/pérdida silenciosa. Bug-risk #1.
- **Guión global crea adyacencias nuevas** que algún regex false-dispara → lo caza el `check_regresion` direccional.
- **Interacción no aditiva** → por eso se mide +ambos, no se infiere.
- **Marcadores editoriales** preservados — si se enmascaran por error, se rompe `detectar_fin_real`.

---

### Banco de entrada
`B122_banco_truncado_jurisdiccional_n42.csv` (con coordenadas `.md` + cruce gold) ya generado.
