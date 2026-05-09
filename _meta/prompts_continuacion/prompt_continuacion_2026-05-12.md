# Prompt de continuación — PIPELINE.md §2 (sesión 2026-05-12)

Hola Claude. Soy Guillermo. Esta sesión continúa la producción de
`PIPELINE.md`, el documento de referencia persistente del pipeline
corpus-csjn que iniciamos en la sesión 2026-05-11.

## Estado al cierre de la sesión anterior

`PIPELINE.md` quedó con **diagrama global + Etapa 1 completa**
(`detectar_paginas.py`). 304 líneas markdown. Ya está commiteado en la
raíz del repo (`C:\Users\guill\Proyectos\corpus-csjn\PIPELINE.md`).

La sección 1 ya cubre:
- Inputs/outputs y estructura de `mapa_paginas.csv`.
- Convención central confirmada empíricamente: `linea_header` es
  0-indexed y apunta a la línea donde el número del tomo aparece
  aislado.
- Tres patrones tipográficos del header de página, verificados contra
  `LibroVol339.2.md`.
- Heurísticas con su razón (filtro duplicados, filtro outliers, gaps).
- Tomos 335 y 336 excluidos.
- 3 puntos de fricción registrados (PF-1.a, PF-1.b, PF-1.c — ver más
  abajo el cambio de naming).

## Lo que vamos a hacer en esta sesión

**Producir la Sección 2 de `PIPELINE.md`: `construir_catalogo.py`.**

Mismo nivel de detalle y mismo formato que la §1. La estructura tipo es:

```markdown
## Etapa 2 — `construir_catalogo.py`

### 2.1 Qué hace
### 2.2 Inputs y outputs
### 2.3 Convención central: el "índice por nombres"
### 2.4 Detección de secciones de índice
### 2.5 Fix v15: extender_inicio_indice_nombres
### 2.6 Parser del índice: regex de ancla y join multilínea
### 2.7 Construcción de filas: agrupación por (tomo, página)
### 2.8 Cálculo de pagina_fin
### 2.9 Limitaciones conocidas
### 2.10 Puntos de fricción con etapas posteriores
### 2.11 Estado de validación de la sección
```

## Cambio de naming acordado

En la sesión anterior usé **F1.10.a, F1.10.b, F1.10.c** para los puntos
de fricción de la §1. Esto choca visualmente con los códigos **F001–F011**
de BITACORA (que son bugs reales). Para no confundir, **renombrar a
PF-1.a, PF-1.b, PF-1.c** (Punto de Fricción, etapa 1, item a/b/c).

Distinción operativa (anotar para futuras sesiones):

- **PF-N.x** (PIPELINE.md): convención de diseño que una etapa fija y
  que las posteriores deben respetar. NO es un bug.
- **FXXX** (BITACORA.md): bug concreto a corregir.

**Primer paso de la sesión: aplicar el rename `F1.10.x → PF-1.x` en
`PIPELINE.md` antes de empezar la §2.** Es un sed simple en 3 puntos
del documento (tres ocurrencias en la sub-sección 1.10 y una en 1.11).

## Hallazgos detectados en sesión anterior, pendientes de incorporar

Estos surgieron leyendo el código pero **NO están todavía en
PIPELINE.md** porque aplican a etapas posteriores. Anotar para usar
cuando lleguemos a las §2, §3, §4:

### Para §2 (`construir_catalogo.py`)

- **Contradicción docstring vs código en `pagina_fin`**:
  el docstring (líneas 56–57 del script) dice
  `pagina_fin = pagina_inicio_siguiente - 1`. El código real (líneas
  408–412) calcula `pagina_fin = pagina_inicio_siguiente` (sin restar
  1). Verificar cuál es la convención que usa `cruzar_catalogo_y_mapa.py`
  río abajo (en el cruzador, línea 235, busca `pg_fin + 1` como header
  del siguiente — lo cual es coherente con `pagina_fin = pagina_inicio_siguiente`,
  no con `pagina_inicio_siguiente - 1`). Conclusión preliminar: **el
  código está bien, el docstring está mal**. Documentar como punto de
  fricción interno de la §2.

### Para §3 (`cruzar_catalogo_y_mapa.py`)

- **Posible mezcla de indexaciones 0 vs 1 en `ok_cortado_en_indice`**:
  - `detectar_paginas.py` produce `linea_header` 0-indexed.
  - `construir_catalogo.py` produce secciones de índice **1-indexed**
    (línea 195 explícita: `linea_inicio_0 + 1`).
  - `cruzar_catalogo_y_mapa.py` línea 222 hace
    `linea_fin = indices_nombres_por_archivo[archivo_ini] - 1`,
    mezclando los dos sistemas.
  - Si `linea_inicio_indice` es 1-indexed y se le resta 1, da una línea
    0-indexed que apunta al header del índice — NO a la línea anterior
    al header en 0-indexed.
  - **Hipótesis**: esto puede ser el origen de los 19 casos
    `ok_cortado_en_indice` pendientes de validar en BITACORA.
  - Validar empíricamente cuando lleguemos a §3.

### Para §4 (`parser.py`)

- **Filtro `>=5` chars en primer token**: tanto
  `detectar_fin_real` (línea 1190) como el detector `borde_inferior`
  del auditor aplican `len(primer_token_siguiente) >= 5`. Si la
  carátula del fallo siguiente arranca con un apellido de ≤4 chars
  (ej. "DIEZ"), nunca se usa como pista. Cae al fallback de firma
  o sumario. Documentar como PF-4.x cuando lleguemos a la §4.

## Archivos que vas a necesitar pedir

Para la §2 ya tenés todo lo necesario en lo que te subí en la sesión
anterior:

1. ✅ `construir_catalogo.py` — script completo, ya leído.
2. ⏳ `output/catalogo/catalogo.csv` — para validación empírica de
   formato de salida y de la convención `pagina_fin`.
3. ⏳ `output/catalogo/secciones_indices.csv` — para validar la
   detección de secciones (especialmente útil cuando lleguemos a §3).
4. ⏳ Posiblemente otro `.md` del corpus para validar el
   `extender_inicio_indice_nombres` (Fix v15) en un tomo moderno
   (337+). El que tengo del archivo en cuestión sirve si es uno de
   esos. **Pedirle a Guillermo cuál `.md` puede subir que tenga índice
   de nombres ubicado al final.**

Si ves saturación de contexto, **frenar y pedir nueva ventana** antes
de §3 (que es la sección más densa del documento).

## Reglas operativas vigentes

Las del prompt de la sesión anterior (no se cambian):

1. Nada de pseudocódigo ni pseudo-CSVs. Todo se contrasta contra
   archivos reales.
2. No asumir nada hasta tener el caso real en pantalla.
3. En pasos críticos, Claude pide explícitamente contrastar con `.md`
   o PDF original.
4. Claude pide los archivos que necesita. No alucina.
5. Ojo humano sobre el dato vale más que cualquier parser.
6. Si Claude se va por las ramas, mezcla conceptos, o el contexto se
   satura — frenar y pedir ventana nueva con prompt de continuación.
7. **El auditor NO corrige bugs de diseño, solo los señala.**
8. Al usar códigos F+número (BITACORA), agregar siempre glosa breve.
9. Distinguir "H+número (BITACORA)" de "H+número (hipótesis de tesis)"
   siempre que pueda haber ambigüedad.
10. **Nuevo (sesión 2026-05-12)**: distinguir "PF-N.x (PIPELINE.md,
    convenciones de diseño)" de "FXXX (BITACORA.md, bugs)".

## Reglas de actualización de PIPELINE.md

Patrón estándar para esta sesión:

1. Claude produce el archivo PIPELINE.md completo con la nueva sección
   integrada (no append parcial — es un documento que crece, no una
   bitácora).
2. Guillermo descarga y reemplaza la versión actual en raíz del repo.
3. Verificar con `Get-Content PIPELINE.md -Tail 20`.
4. Commit + push con mensaje descriptivo
   (ej. "PIPELINE.md: agregar §2 (construir_catalogo.py)").

## Reglas para PowerShell

- Pasar **un comando por bloque de código**.
- **No incluir ejemplos de output** dentro de bloques de código.
- Comandos de una sola línea siempre que sea posible.

## Forma de entrega esperada para esta sesión

**Dos entregas:**

1. **`PIPELINE.md` actualizado**: con el rename `F1.10.x → PF-1.x` y
   con la §2 completa. Para reemplazar el archivo en raíz del repo.

2. **Si surgen hallazgos nuevos durante la lectura empírica del
   catálogo**, registrarlos inline en la §2 con la misma convención
   (`✅` validado, `⏳` pendiente). No abrir bitácora paralela.

## Lo que NO hacemos esta sesión

- NO seguir tocando `auditar_fallo.py` ni el detector `borde_inferior`.
  Eso queda en pausa hasta tener el pipeline mapeado completo.
- NO escribir ya las §3 y §4. Una sección por sesión, salvo que el
  contexto sobre con holgura.
- NO interpretar todavía los resultados `--random 50` del auditor.
  Eso es el paso siguiente cuando estén las cuatro secciones.

## Punto de partida concreto

Al inicio de la sesión, Claude:

1. Confirma que recibió este prompt y entendió el alcance (§2 +
   rename PF).
2. Pide los archivos que necesita: PIPELINE.md actual (para el rename),
   `catalogo.csv`, `secciones_indices.csv`, y eventualmente un `.md`
   adicional si lo justifica.
3. NO empieza a escribir hasta tener confirmación de Guillermo sobre
   qué `.md` adicional se va a usar para validar.
