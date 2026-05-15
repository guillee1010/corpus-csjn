# Notas — Auxiliares históricos

Este directorio contiene 6 scripts archivados en Fase 2 del inventario
(14/5/2026). Son herramientas de QA, diagnóstico y exploración que se
usaron durante el desarrollo del parser (v10 a v16) y que ya no forman
parte del pipeline vivo.

El archivo no es descarte: si reaparece una necesidad similar, conviene
revisar este documento antes de reescribir nada.

---

## Activos rescatables (consultar sin reabrir los .py)

### Padrón histórico de jueces — `reparser_firmas.py`

**Estado: redundante en parser.py vivo.** Verificado el 14/5/2026:
las 5 entradas críticas (Zaffaroni, Petracchi, Argibay, Fayt, Boggiano)
están en `scripts/pipeline/parser.py` líneas 294-299.

Sin embargo, `reparser_firmas.py` contiene 30+ regex de jueces, incluyendo
conjueces históricos (Rodríguez Basavilbaso, Otero, Cavallo) y conjueces
frecuentes (Borinsky, Catania, Gemignani, Petrone, Ledesma, Barroetaveña,
Hornos, Leal de Ibarra, Catucci, Riggi, Yacobucci, Figueroa, Mahiques).
Si en algún momento el parser pierde reconocimiento de algún conjuez,
ahí está el regex.

### Regex de calificadores de voto — `reparser_firmas.py`

```python
RE_CALIFICADOR = re.compile(
    r"\(\s*(en\s+disidencia|seg[úu]n\s+su\s+voto|por\s+su\s+voto)"
    r"(\s+parcial)?\s*\)",
    re.I
)
```

Capta "(en disidencia)", "(según su voto)", "(por su voto)" con variante
"parcial" opcional. Confirmar si el parser vivo lo usa antes de reactivar.

### Regex de estructura del MD — `detectar_paginas_vacias.py`

```python
RE_NUM_SOLO  = re.compile(r"^\s*(\d{2,5})\s*$")
RE_TOMO_FILE = re.compile(r"LibroVol(\d+)", re.I)
RE_HEADER    = re.compile(
    r"^(FALLOS?\s+DE\s+LA\s+CORTE\s+SUPREMA|"
    r"DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N|"
    r"CORTE\s+SUPREMA\s+DE\s+JUSTICIA)\s*$",
    re.I
)
```

`RE_HEADER` matchea las tres variantes del encabezado institucional
de los Fallos. Calibrado contra OCR real, vale como referencia si
alguna vez hay que detectar headers fuera del parser.

### Algoritmo de detección de marcas página/tomo — `detectar_paginas_vacias.py`

Detecta el patrón "número de página + (header opcional) + número de
tomo en 1-3 líneas" en O(N). Lógica de fondo similar a la que necesita
el cruzador para resolver páginas compartidas (relacionado con el bug
Y.P.F. del v17 beta, donde `pista_fin = caratula_siguiente` dropeó
un fallo). No es trasplantable directo al parser, pero la lógica es
referencia.

### Estratos de wc_voto — `auditar_indeterminados.py`

Clasificación operativa de votos por extensión:
- **Cortos:** `wc_voto < 200`
- **Medios:** `200 ≤ wc_voto < 1000`
- **Largos:** `wc_voto ≥ 1000`

### Definición operativa de R1 / R2 — `extraer_muestra.py`

Casos `sin_firma` agrupados según outcome:

- **R1** (no detectó dispositivo):
  `firma_raw vacía` AND (`outcome == sin_dispositivo` OR
  `outcome ∈ {inadmisible_280, inadmisible_acordada_4}`)

- **R2** (otros outcomes):
  `firma_raw vacía` AND outcome distinto a los de R1

**Hallazgo empírico (28-29/4/2026):** los casos R1 se concentran
en tomo 345. Tomos también afectados: 347, 348, 346, 344.

### Umbrales de severidad de páginas vacías — `detectar_paginas_vacias.py`

- `> 50 páginas vacías por tomo` → GRAVE
- `> 10 páginas vacías por tomo` → revisar
- `≤ 10` → tolerable

---

## Diagnósticos congelados en `archivo/data/`

Outputs generados por estos scripts al correrlos en su momento:

| Archivo | Origen | Qué contiene |
|---|---|---|
| `auditoria_indeterminados.txt` | `auditar_indeterminados.py` | 30 votos `indeterminado` estratificados por wc, con texto completo para inspección manual |
| `diag_originaria_tribunal.csv` | `diagnostico_originaria.py` | Distribución de casos `is_originaria=1` por tribunal de origen |
| `diag_originaria_outcome.csv` | `diagnostico_originaria.py` | Distribución por outcome |
| `diag_originaria_por_tomo.csv` | `diagnostico_originaria.py` | Distribución por tomo |
| `diag_originaria_muestra50.csv` | `diagnostico_originaria.py` | 50 casos originarios para inspección manual |
| `muestra_R1.csv` | `extraer_muestra.py` | 10 casos R1 estratificados (tomos 345, 347, 348, 346, 344) |
| `muestra_R2.csv` | `extraer_muestra.py` | 8 casos R2 con outcome='otro' (tomos 345, 347, 348, 337, 344, 329, 330, 338) |

Si en algún momento se necesita rehacer alguno, los scripts están acá
al lado y los inputs viven en el corpus actual (con renombres: el
parser vivo produce `csjn_casos.csv`, no `csjn_casos_v16.csv`).

---

## Sobre `pdf_to_md_v2.py`

Conversor de PDF a Markdown. **No es parte del pipeline** — corrió
upstream del proyecto para generar el corpus inicial de archivos `.md`
a partir de los PDFs de los Tomos de Fallos.

Heurística clave: detección de páginas a dos columnas. Si en algún
momento aparece Tomo 350+ o hay que reconvertir, el script está acá.

---

## Reactivación

Si un script vuelve a ser útil:

1. Verificar que los nombres de columnas en el CSV input siguen
   coincidiendo (los scripts asumen el esquema de `csjn_casos_v9` a
   `v16`; el corpus actual es v17 beta).
2. Mover con `git mv` a `scripts/diagnostico/` o `scripts/auxiliares/`
   según corresponda.
3. Actualizar el docstring del script con la fecha de reactivación
   y los cambios necesarios.
