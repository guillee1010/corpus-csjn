# DELTA CODEBOOK — H211 (espera refresh M43/M35, patrón tabla-equivalencias H210)

Formato-agnóstico a propósito: contenido a mergear en el CODEBOOK publicado
cuando abra el refresh (M43). No tocar Dataverse antes.

## csjn_casos_textos.csv — columna NUEVA

- **`dictamen_text`** (4ª columna de texto, al final; parser ≥ v38.0, H211/M58):
  texto completo del dictamen de la Procuración embebido en el fallo, reconstruido
  de las líneas con zona `dictamen` (zonificador H052, post-relabel), unidas con
  espacio simple, líneas vacías descartadas, SIN des-guionado (misma convención de
  armado que `considerando_text`). Vacía cuando el caso no tiene zona dictamen.
  Invariante publicado: `dictamen_text != "" ⇔ dictamen_presente == 1`
  (3.434 casos en tomos 329–349; cruce exacto verificado, clase all-blank = 0).
  Fuente para: canal dictamen de materia (v4.1), ámbito `dictamen` del sidecar de
  normas (v1.1), y análisis de remisión (tesis-H2: ~3.400 dictámenes estructurados).

## csjn_casos_normas.csv — valor NUEVO de `ambito`

- **`ambito = "dictamen"`** (extraer_normas ≥ v1.1, H211/M59-parcial): leyes
  numeradas citadas dentro de `dictamen_text`. Mismo alcance que los demás ámbitos
  (RE_LEY: solo «ley N»; decreto-ley de rebote). El dominio de `ambito` pasa de
  {caratula, considerando, dispositivo, voto} a + {dictamen}. Cardinalidad al
  sello H211: 6.206 pares / 1.378 normas / 2.515 casos (total del CSV
  7.696 → 13.902 filas). Solo `ambito=considerando` y el tier dictamen (abajo)
  alimentan la cascada de materia; el resto extraído-inerte.

## csjn_casos_materia.csv — valor NUEVO de `materia_capa` + formato NUEVO de `materia_fuente`

- **`materia_capa = "lectura_dictamen"`** (derivar_materia ≥ v4.1, H211/M58;
  ejecuta la reserva de M49): clasificación tomada del dictamen de la Procuración
  cuando NINGUNA señal del caso propio clasificó (prioridad mínima de la cascada:
  corre solo sobre el residuo `sin_ancla`; los casos `conflicto_capa2` no entran).
  Gates: norma-en-dictamen = ancla fuerte; keyword sin norma exige ≥2 coincidencias;
  empate → no clasifica. 77 casos al sello H211. Precisión de muestra adjudicada
  por el operador: 24/25 TP (96%); 1 FP conocido y documentado (329_p5108, cita
  de rebote — BITACORA H211).
- **`materia_fuente` con prefijo `dictamen:`** — procedencia explícita del tier:
  `dictamen:norma:24240(1)` (norma-ancla, n = votos totales) ·
  `dictamen:kw+norma:23548(2)` (coincidencia keyword+norma) ·
  `dictamen:kw(2)` (≥2 keywords). Se suma a los formatos existentes de
  lectura_texto (`norma:…`, `kw`, `parte`, `objeto`, `coocur:…`, `provincia:ca`,
  `conflicto_capa2:…`, `sin_ancla`).
- Distribución de capas al sello H211 (5.894 filas): lectura_tribunal 2.301 ·
  lectura_tribunal_refinada 159 · lectura_texto 1.472 · **lectura_dictamen 77** ·
  sin_clasificar 1.084 · originaria 596 · sui_generis 8 · residual 6 · no_aplica 191.
  Cobertura sobre clasificable: 78,5%.

## Advertencias de estabilidad para el redactor del refresh (NO publicar antes de resolverlas)

- La decisión taxonómica H209 (dos ejes: `competencia_dirimente` / `procesal_propio`
  terminales + columna futura `materia_subyacente`) va a mover `materia_capa` de
  nuevo, e intersecta las altas de `lectura_dictamen` (constancia en M58).
- vocab_faltante / M61 (Digesto) van a re-decidir altas del tier al poblar el
  índice de normas.
- Por ambas: este delta se ACUMULA, no dispara refresh. El refresh es M43, última.
