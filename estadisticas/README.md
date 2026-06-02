# estadisticas/validacion — M19, validación contra ground truth

Mide la **exactitud** del dataset (no la regresión). El pipeline es un censo
determinístico: el error no es de muestreo sino sistemático (sesgo de
extracción/clasificación) y no decrece con n. `check_regresion.py` verifica
"no rompí lo que andaba"; esto verifica "qué fracción de las filas coincide
con la verdad de campo codificada a mano contra el `.md`".

Complementa al análisis descriptivo (`estadisticas/analisis/`), que calcula
**asumiendo** el dataset correcto. M19 le pone número a ese supuesto.

## Diseño

- Semilla fija: **20260531** (reproducible).
- Dos marcos por tabla:
  - **Marco A** — aleatorio simple (insesgado → exactitud global + IC de Wilson).
  - **Marco B** — oversample por valor, `min(20, N_valor)` por cada valor de
    cada columna de clasificación; los valores chicos quedan censados. Habilita
    precisión/recall **por valor**. Se reporta separado del global de A.
- Codificación **ciega**: la planilla no muestra el valor del parser; el cruce
  lo hace el analizador al final.
- **AMBIGUO**: celda `cod_*` = `AMBIGUO` cuando el OCR no permite decidir. Es
  indeterminación de la fuente, no error del parser; queda fuera del denominador.
- **Doble codificación**: subconjunto de 50 (`doble_cod=1`) para kappa de Cohen
  (inter-codificador si hay dos personas; intra si es recodificación ciega).

## Cobertura (golden v18.15, seed 20260531)

- **Casos**: 653 únicos (Marco A 300 + Marco B 353). Columnas: `outcome`,
  `causa_inadmisibilidad`, `es_queja`, `queja_resultado`, `tipo_cuestion_federal`.
- **Votos**: 3845 votos en 779 casos (626 de la muestra de casos + 153 extra por
  valores raros). Anclado al caso: se lee cada `.md` una sola vez. Columnas:
  `posicion`, `tipo_voto_sep`, `fragmenta_ratio`, `punto_divergencia` +
  `juez`/completitud.
- `.md` a leer en total: **806**.

## Flujo

1. Generar la muestra (semilla fija, reproducible):
   ```
   python muestrear_validacion.py --casos output/parser/csjn_casos.csv \
     --votos output/parser/csjn_casos_votos.csv \
     --outdir ground_truth --golden v18.15
   ```
2. Codificar a mano contra el `.md` (con `scripts/diagnostico/extraer_caso.py`,
   regla M15). Llenar las columnas `cod_*` de las planillas. No mirar la `_clave_`.
3. Analizar:
   ```
   python analizar_validacion.py \
     --planilla ground_truth/planilla_codificacion_v18.15.csv \
     --clave ground_truth/muestra_clave_v18.15.csv \
     --label casos_v18.15 --outdir resultados
   ```
   (ídem con `--id-col voto_id` y los archivos `_votos_` para la tabla de votos.)

## Salida

Exactitud por columna con IC de Wilson, precisión/recall por valor,
falso-residual, kappa, spot-check estructural (regla de tres si 0 errores).
Insumo de la sección *Reliability / known limitations* del CODEBOOK y candidato
a dataset v2.1 si la validación no toca el parser.

## Estado

Scaffold implementado (H098): muestreo + analizador + ground_truth generado y
verificado (planilla vacía + codificación sintética). **La codificación manual
está pendiente** — es el trabajo de la sesión siguiente. Sin codificar, no hay
número de error todavía.
