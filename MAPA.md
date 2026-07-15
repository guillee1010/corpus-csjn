# MAPA del pipeline — corpus-csjn

Grafo de dependencias **consume → produce** de `scripts/pipeline/`, y el orden de
ejecución que se deriva de él. Pensado para reconstruir el pipeline sin abrir cada
script ni adivinar el orden.

**Verificado en disco (jun-2026)** por inspección de los `DEFAULT_*`, los `.open()`
y los imports de cada script (greps + lectura de `derivar_partes.py` y
`check_regresion.py`). Lo que NO se pudo confirmar está marcado con ⚠.
**Actualizado H209 (jul-2026):** etapa `extraer_normas.py` (M59 paso 1) — sidecar
de normas citadas, insumo de `derivar_materia` v3.3.

---

## DAG

```
corpus/*.md
  │
  ├─ construir_catalogo.py     [corpus]            → catalogo.csv, secciones_indices.csv
  │
  ├─ detectar_paginas.py       [corpus, catalogo?] → mapa_paginas.csv  (+ sidecars*)
  │
  └─ (los dos de arriba alimentan:)
       cruzar_catalogo_y_mapa.py [catalogo, mapa]  → fallos_localizados.csv  (+ _huerfanos, _resumen)

parser.py   [fallos_localizados, mapa_paginas, corpus]
            → csjn_casos.csv, csjn_casos_textos.csv, csjn_casos_votos.csv,
              csjn_casos_zonas.csv, csjn_casos_editorial.csv          (5 CSV)

extraer_epilogos.py  [casos, zonas]                → csjn_casos_epilogo.csv
derivar_partes.py    [casos, epilogo]              → csjn_casos_partes.csv
extraer_normas.py    [casos, textos, votos]        → csjn_casos_normas.csv   (M59, H209)
derivar_materia.py   [casos, textos, normas]       → csjn_casos_materia.csv
derivar_recursos.py  [casos, textos] + clasif.(lib) → csjn_casos_recursos.csv

⚠ parser_editorial.py  [catalogo]                  → csjn_editorial_indice_partes.csv
                       (librería sin __main__; ver nota abajo)

generar_manifiesto.py  [lee toda la cadena]        → _manifest.json   (sella, no produce datos)
```
\* `detectar_paginas` también emite `_resumen`, `_filtradas`, `_inferidas`,
`_sin_banner`; el canónico que consume `cruzar` es `mapa_paginas.csv`.

---

## Orden de ejecución (topológico)

1. `construir_catalogo.py`      — corpus → `catalogo.csv`, `secciones_indices.csv`
2. `detectar_paginas.py`        — corpus (+ catalogo) → `mapa_paginas.csv`
3. `cruzar_catalogo_y_mapa.py`  — catalogo + mapa → `fallos_localizados.csv`
4. `parser.py`                  — localizados + mapa + corpus → los 5 CSV del parser
5. `extraer_epilogos.py`        — casos + zonas → `csjn_casos_epilogo.csv`
6. derivers (todos dependen de `parser.py`; desde H209 **materia depende además
   de extraer_normas** — el resto son independientes entre sí):
   - `derivar_partes.py`    — casos + epilogo → `csjn_casos_partes.csv`
   - `extraer_normas.py`    — casos + textos + votos → `csjn_casos_normas.csv` (M59)
   - `derivar_materia.py`   — casos + textos + **normas** → `csjn_casos_materia.csv`
   - `derivar_recursos.py`  — casos + textos → `csjn_casos_recursos.csv`
7. `generar_manifiesto.py`      — relee todo y sella `_manifest.json` (último paso)

`parser_editorial.py` → ver nota ⚠.

---

## Cómo correr la cadena

Desde H179 la cadena canónica se corre con el **orquestador**
`scripts/pipeline/correr_pipeline.py` (M42; v1.1 desde H209), que implementa
este grafo:

```powershell
python scripts\pipeline\correr_pipeline.py --plan            # dry-run: secuencia exacta, nada se ejecuta
python scripts\pipeline\correr_pipeline.py                   # cadena completa: parser → derivers → gate → manifest
python scripts\pipeline\correr_pipeline.py --solo-derivers   # sin parser (epilogos → partes → normas → materia → recursos)
python scripts\pipeline\correr_pipeline.py --consciente      # post-fix: tolera [FAIL], muestra el diff y FRENA
python scripts\pipeline\correr_pipeline.py --regolden        # tras adjudicar: congela golden + assert + re-sello
```

Gates automáticos: fail-fast por etapa · versiones en pre-flight (pin opcional
`--esperar "parser=24.0,..."`) · frescura post-etapa · **corpus-drift** (aborta si
hay `.md` en `corpus/` fuera del universo `source_file`; `--ignorar-corpus-drift`
declara la exclusión deliberada) · assert **golden == producción** (sha256, los 5
CSV del parser) en toda corrida · manifest verify → sello condicional, siempre último.

**Upstream (orden 1–3: catálogo, páginas, cruce) queda FUERA del orquestador v1:**
se corre a mano según este mapa, en sesión propia. La v2 lo incorpora cuando haya
tomos nuevos reales (leyendo las CLIs de esas etapas, hoy no leídas).

---

## Dependencias por script (verificado)

| script | consume | produce | tipo |
|---|---|---|---|
| `construir_catalogo.py` | `corpus/*.md` | `catalogo.csv`, `secciones_indices.csv` | etapa |
| `detectar_paginas.py` | `corpus/*.md`, `catalogo.csv` (opcional, argv) | `mapa_paginas.csv` + sidecars | etapa |
| `cruzar_catalogo_y_mapa.py` | `catalogo.csv`, `mapa_paginas.csv` | `fallos_localizados.csv` (+ `_huerfanos`, `_resumen`) | etapa |
| `parser.py` | `fallos_localizados.csv`, `mapa_paginas.csv`, `corpus/*.md` | `csjn_casos`, `_textos`, `_votos`, `_zonas`, `_editorial` | etapa |
| `extraer_epilogos.py` | `csjn_casos.csv`, `csjn_casos_zonas.csv` | `csjn_casos_epilogo.csv` | etapa |
| `derivar_partes.py` | `csjn_casos.csv`, `csjn_casos_epilogo.csv` | `csjn_casos_partes.csv` | etapa |
| `extraer_normas.py` | `csjn_casos.csv`, `csjn_casos_textos.csv`, `csjn_casos_votos.csv` (+ `_norm` importado de `derivar_materia`) | `csjn_casos_normas.csv` | etapa (M59, H209) |
| `derivar_materia.py` | `csjn_casos.csv`, `csjn_casos_textos.csv`, `csjn_casos_normas.csv` | `csjn_casos_materia.csv` | etapa |
| `derivar_recursos.py` | `csjn_casos.csv`, `csjn_casos_textos.csv` + clasificadores | `csjn_casos_recursos.csv` | etapa |
| `parser_editorial.py` | `catalogo.csv` | `csjn_editorial_indice_partes.csv` | ⚠ librería |
| `generar_manifiesto.py` | toda la cadena | `_manifest.json` | sello |

Nota M59: `extraer_normas` importa `derivar_materia` **como librería** (solo
`_norm`, fuente única de normalización) — dependencia de código, no de datos;
no hay ciclo: `derivar_materia` consume el **CSV** de `extraer_normas`, no su
módulo. RE_LEY (extracción de leyes numeradas) vive en `extraer_normas.py`
desde H209.

### Clasificadores = librerías, no etapas

`clasificador_admision.py`, `clasificador_causa.py`, `clasificador_via.py`,
`clasificador_disposicion.py` **no tienen `__main__` ni producen CSV propio**. Se
importan: `admision` y `via` toman `norm` de `disposicion`; y `derivar_recursos.py`
importa los cuatro (`disposicion`, `via_recurso`, `admisibilidad`,
`causa_inadmisibilidad`), trayéndose su `__version__`. La etapa con I/O es
`derivar_recursos`; los clasificadores son su lógica.

### ⚠ parser_editorial.py — pendiente de confirmar

Verificado: **no tiene `__main__`** (no aparece en el grep de `if __name__`), lo
importa `parser.py` (`from parser_editorial import ...`), y su comentario declara
que consume `catalogo.csv`. Se le atribuye `csjn_editorial_indice_partes.csv`.

**Lo que NO está confirmado:** el disparador exacto de escritura de ese CSV. En la
corrida de `check_regresion.py` (que ejecuta `parser.py`) se generaron los 5 CSV
del parser pero **no** `csjn_editorial_indice_partes.csv`. O sea: o se escribe por
una invocación aparte que no vi, o bajo una condición distinta. Antes de tratarlo
como etapa con orden propio, confirmar quién y cuándo escribe ese archivo
(`Select-String parser_editorial.py -Pattern 'def |open\(|to_csv|DictWriter|indice_partes'`).

---

## Cómo se mantiene este mapa

Hecho a mano contra el disco, no autogenerado. Al **agregar o reconectar una etapa**
del pipeline, actualizar la tabla y el orden — **y el orquestador** (`correr_pipeline.py`,
H179): este grafo es su especificación; mapa y orquestador se mueven juntos.
