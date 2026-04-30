# CSJN — Pipeline completo (corpus 2006-2026)

## Archivos en este paquete

| Archivo | Función |
|---|---|
| `csjnv10.py` | Parser de Markdown a CSV. Versión extendida con padrón histórico completo (Petracchi, Zaffaroni, Fayt, Argibay, Boggiano, etc.) |
| `reparser_firmas.py` | Atajo: si ya generaste CSVs con un parser sin padrón histórico, este script reparsea las firmas sin re-correr el parser |
| `clasificador_tipo_caso.py` | Asigna `tipo_caso` (admisibilidad / núcleo / originaria) a cada caso |
| `detector_templates.py` | Detecta los templates Lorenzetti+Vidal y Rosenkrantz+no-Levinas |
| `csjn_analisis_v3.py` | Análisis estadístico extendido con composición 2006-2026 (5 regímenes), modelos a nivel voto, ZINB, co-disidencia, etc. |
| `csjn_analisis_v2.py` | Versión anterior (corpus 2021-2026, 3 regímenes). Conservar como respaldo |

## Decidir el camino: A o B

### Camino A — re-parsear desde los .md (recomendado para tesis)

Si tenés todos los .md y no te molesta esperar la corrida del parser
(unos minutos por cada 100 casos):

```bash
python csjnv10.py --input-dir markdowns/ --output csjn_casos_v10.csv
```

Este genera `csjn_casos_v10.csv` y `csjn_casos_v10_votos.csv` con la columna
`texto_voto` poblada (necesaria para el detector de templates).

### Camino B — atajo si ya generaste CSVs con la versión antigua

Si ya tenés CSVs producidos por una versión del parser que no incluía a
Petracchi/Zaffaroni/Fayt/Argibay en el padrón:

```bash
python reparser_firmas.py \
  --casos csjn_casos_v10.csv \
  --votos csjn_casos_v10_votos.csv \
  --output-casos csjn_casos_v10_corregido.csv \
  --output-votos csjn_casos_v10_votos_corregido.csv
```

Esto re-parsea las firmas con el padrón completo en pocos segundos.
**Importante**: este atajo NO regenera `texto_voto`. Si querés usar el
detector de templates con todo el rigor, hay que ir por el Camino A.

## Pipeline completo (después de A o B)

```bash
# 1. Clasificador de tipo_caso
python clasificador_tipo_caso.py \
  --casos csjn_casos_v10[_corregido].csv \
  --output csjn_casos_v10_clasificado.csv

# 2. Detector de templates (solo Camino A: requiere texto_voto)
python detector_templates.py \
  --casos csjn_casos_v10[_corregido].csv \
  --votos csjn_casos_v10_votos[_corregido].csv \
  --output-dir resultados_templates

# 3a. Análisis estadístico — corpus completo
python csjn_analisis_v3.py \
  --casos csjn_casos_v10_clasificado.csv \
  --votos csjn_casos_v10_votos[_corregido].csv \
  --templates resultados_templates/templates_resultado.csv \
  --output-dir resultados_v3

# 3b. Análisis solo sobre el "núcleo" (sin admisibilidad ni originaria) — RECOMENDADO
python csjn_analisis_v3.py \
  --casos csjn_casos_v10_clasificado.csv \
  --votos csjn_casos_v10_votos[_corregido].csv \
  --templates resultados_templates/templates_resultado.csv \
  --tipo-caso nucleo \
  --output-dir resultados_v3_nucleo
```

## Composiciones institucionales (5 regímenes)

El v3 maneja 5 regímenes en la variable `composicion`:

| Régimen | Período | Composición |
|---|---|---|
| `banco_de_7` | hasta 09/05/2014 | Lorenzetti, Highton, Fayt, Petracchi, Maqueda, Zaffaroni, Argibay |
| `transicion` | 10/05/2014 — 21/08/2016 | Vacantes progresivas: 6→5→4 jueces |
| `banco_de_5` | 22/08/2016 — 01/11/2021 | Lorenzetti, Highton, Maqueda, Rosatti, Rosenkrantz |
| `banco_de_4` | 02/11/2021 — 28/12/2024 | Sin Highton |
| `banco_de_3` | 29/12/2024 → presente | Sin Maqueda (incluye intervalo García-Mansilla) |

Fechas tomadas del cuadro institucional verificado.

## Salidas principales

### Del parser (`csjnv10.py`)
- `csjn_casos_v10.csv`: 1 fila por caso
- `csjn_casos_v10_votos.csv`: 1 fila por (caso, juez), con `texto_voto`

### Del clasificador
- `csjn_casos_v10_clasificado.csv`: input + columnas `tipo_caso` y `tipo_caso_grupo`

### Del detector de templates
- `templates_resultado.csv`: flags por caso
- `templates_serie_mensual.csv` / `templates_serie_anual.csv`: serie temporal
- `fig_templates_serie.png`: gráfico de aparición temporal
- `templates_consolidado.xlsx`: Excel con todas las tablas

### Del análisis estadístico v3
- `corpus_limpio_v3.csv`: corpus modelable
- `csjn_resultados_v3.xlsx`: todas las tablas
- `fig_dissent_forest.png`: forest plot logit disidencia
- `fig_voto_mlogit_forest.png`: multinomial a nivel voto
- `fig_zinb_obs_vs_pred.png`: ZINB observado vs predicho
- `fig_codisidencia_banco_de_7.png` y los 4 bancos restantes

## Resultados esperados (validación con corpus 2006-2026)

Con corpus de ~5.700 casos correctamente parseados:

- **Detección de jueces históricos**: Petracchi, Zaffaroni, Fayt, Argibay
  cada uno con ~1.500-1.800 votos en banco de 7
- **Co-disidencia banco de 7**: φ Highton+Argibay ≈ 0,28; Fayt+Zaffaroni ≈ 0,25
- **Co-disidencia banco de 5**: φ Rosatti+Maqueda ≈ 0,28 (corrige el dato
  inflado de versiones anteriores)
- **Co-disidencia banco de 3**: φ Rosatti+Lorenzetti ≈ 0,66 (eje nuevo emergente)

## Limitaciones conocidas

- **Tomos 335 y 336 con 0 jueces detectados**: probablemente .md vacíos o
  con formato roto. No afectan al resto del análisis.
- **Detección de inadmisible_280 baja en tomos viejos** (solo ~23 casos
  detectados): la fórmula textual cambió a lo largo del tiempo.
- **Casos sin_dispositivo en tomos viejos (~19%)**: el "Por ello" en libros
  pre-2014 puede tener formato distinto al esperado.

## Próximos pasos sugeridos

1. Validación manual de templates: muestrear 30-50 casos con flag y verificar.
2. Análisis temporal completo de templates: ¿desde cuándo Lorenzetti usa Vidal?
3. Detector de remisiones (fundamentación por mero reenvío a precedente).
4. Detector ANSES masivo (tribunal previsional + Badaro/Elliff/Blanco).
5. Diagnóstico de outcomes mal detectados en tomos viejos.
