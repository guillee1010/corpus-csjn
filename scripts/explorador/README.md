# Explorador del Corpus CSJN — v8

Visor Streamlit **read-only** sobre los outputs canónicos del pipeline.
No recomputa lógica del parser (lección H045: los regex del visor
divergían) ni escribe nada en `output/`. Herramienta no canónica
(`scripts/explorador/`, gitignoreada). Cierra el pendiente M16
(modo auditoría-de-precisión + panel inline de textos completos).

## Uso

```
cd corpus-csjn
streamlit run scripts/explorador/exploradorv8.py
```

## Fuentes de datos (todas de `output/parser/`)

| CSV | Aporta | Join |
|---|---|---|
| `csjn_casos.csv` | base (39 cols, schema parser v26.1) | — |
| `csjn_casos_recursos.csv` | disposicion, admisibilidad, **causa_inadmisibilidad** (vive acá desde H148, no en casos), es_revision_fondo, via_recurso, reenvia, parte_ganadora, multi_recurso | left 1:1 (se dropea su `es_queja`: la fuente canónica del flag es casos.csv) |
| `csjn_casos_partes.csv` | recurrente/recurrido + roles, multi_recurrente, partes_capa/fuente | left 1:1 |
| `csjn_casos_materia.csv` | materia, materia_capa, materia_fuente | left 1:1 |
| `csjn_casos_epilogo.csv` | epilogo_status, epilogo_n_seg, epilogo_wc_sidecar (NO carga epilogo_text: pesado, se ve pintado en la fuente) | left, solo fallos |
| `csjn_casos_zonas.csv` | pivot `wcz_*` / `nseg_*` por zona, secuencia, banderas, cobertura | left, solo fallos |
| `csjn_casos_votos.csv` | votos del detalle | por caso |
| `csjn_casos_textos.csv` | considerando/por_ello/firma completos (H113), panel inline del detalle | por caso |
| `corpus/*.md` | texto fuente pintado por zonas en el detalle | lectura directa |

Todos los joins son *graceful*: si falta un sidecar, el explorador anda
sin sus columnas/filtros. Los filtros categóricos se autopueblan del CSV
(sin listas hardcodeadas).

**Namespace `wcz_*`:** las métricas de zona usan prefijo propio para no
colisionar con las columnas `wc_*` del parser (`wc_dictamen` existe en
ambas fuentes y mide cosas distintas: la del parser es su medición
interna; `wcz_dictamen` es la suma de wc de los segmentos de esa zona
en zonas.csv).

## Filtros del sidebar

**🔎 Búsqueda**
- *Solo fallos*: `tipo_entrada == fallo` (default ON).
- *Tomo / Página*: match exacto sobre tomo y sufijo `_pNNN` del id.
- *Texto libre*: substring case-insensitive sobre carátulas, jueces,
  tribunal de origen, recurrente/recurrido y secuencia de zonas
  (p.ej. buscar `firma>cuerpo` encuentra secuencias que contengan eso).

**⚖️ Clasificación** (ejes del parser)
- *Tipo de entrada*: fallo / sumario / etc.
- *Outcome (eje legacy)*: la clasificación vieja del dispositivo. Sigue
  útil para cruzarla contra el eje nuevo (los coincide-en-error tipo
  B142/B143 que la divergencia M39 nunca vio).
- *Voting pattern*: unanime / disidencia / segun_su_voto / mixed / sin_firma.
- *Decisión sobre el fondo*: `is_merit_decision`. Desde H178 es derivado
  del gate del clasificador (fuente única) — coincide con
  `es_revision_fondo=si` por construcción.

**📨 Recurso / admisibilidad** (deriver M26/M39)
- *Disposición*: qué hizo la Corte (no_fondo, deja_sin_efecto, revoca,
  confirma, nulidad, no_revision_*...).
- *Admisibilidad*: admite / inadmite / sin_marcador / no_aplica (gate).
- *Causa de inadmisibilidad*: ART_280, ACORDADA_4_2007, CUESTION_ABSTRACTA,
  etc. El checkbox "solo con causal" filtra no-nulos.
- *Revisión de fondo (gate)*: si/no — el eje unificado.
- *Vía del recurso*: extraordinario / ordinario.
- *Parte ganadora*: recurrente_gana / recurrente_pierde / no_aplica.
- *¿Reenvía? / ¿Multi-recurso?*: tri-state (—/Sí/No).

**🏛️ Proceso / jurisdicción**
- *¿Es queja? / Resultado de queja*: flag del parser + resultado.
- *Competencia originaria*: `is_originaria`.
- *Cuestión federal / Tipo de apertura / Status tribunal de origen*.

**📚 Materia y partes**
- *Materia / capa / fuente*: la capa dice qué método la asignó (capa1,
  capa2, originaria, sin ancla...); la fuente, la regla concreta.
- *Capa de partes*: de dónde salió la extracción (epilogo, caratula,
  sin_epilogo, no_aplica).
- *Roles de recurrente/recurrido*: actora, demandada, penal, mp_fiscal...
- *¿Multi-recurrente?*: tri-state.

**👥 Panel / decisión**
- *Juez interviniente*: pertenencia en `jueces_conocidos` (multi = OR).
- *Tribunal en pleno / Con dictamen*: tri-state.
- *N° de jueces / disidencias*: sliders de rango.

**📐 Zonas: wc y segmentos**
- *Word count (total)*: slider sobre el wc del caso.
- *Zonas a filtrar por wc / por n° de segmentos*: elegís zonas y aparece
  un slider por cada una (`wcz_*` / `nseg_*`). Evita 18 sliders fijos.
- *Cobertura de zonificación (%)*: proporción de líneas del bloque
  asignadas a alguna zona. Baja cobertura = mucho intersticio = probable
  miss de zonificación.

**🚩 Banderas de auditoría** — ver leyenda abajo. Se combinan con **OR**.

**🩺 Diagnóstico del parser**
- *Status localización / Status fin / Pista fin*: columnas de diagnóstico
  del parser, antes solo visibles en el detalle. `pista_fin=firma_actual`
  era exactamente la población de B019.
- *Status epílogo (sidecar)*: ok / sin_zona.

## Banderas: leyenda y umbrales

Los umbrales están calibrados sobre el corpus real (H186): wc de firma
p50=20, p95=71; nseg de firma 1–3 cubre ~92% de los fallos. Conteos de
referencia al momento de la calibración entre paréntesis.

| Código (tabla) | Bandera | Qué caza |
|---|---|---|
| `F0` | Sin zona firma (20) | fallo zonificado sin ningún segmento firma → miss de detección de firma |
| `D0` | Sin dispositivo (49) | ídem para dispositivo |
| `C0` | Sin cuerpo | ídem para cuerpo |
| `Ff` | Firma en ≥4 segmentos (453) | firma muy partida: banner/OCR/falso corte |
| `Fw` | Firma > 200 wc (142) | firma que probablemente se comió otra zona (max real: 18.353 wc) |
| `Cw` | Cuerpo con wc 0 | clase B117: cuerpo flipeado entero a otra zona |
| `Gt` | Epílogo no terminal (154) | hay zonas después del epílogo — gramática |
| `Gr` | Residuo no inicial (0) | residuo_caso_anterior fuera de la posición 0 |
| `Ga` | Apertura múltiple | más de un tramo de apertura (colapsado) |
| `Gs` | Sumario/dictamen tardío | sumario o dictamen después de la apertura |
| `Gf` | Firma antes del dispositivo (179) | primera firma precede al primer dispositivo |
| `Cb` | Cobertura < 85% | muchas líneas sin zona |
| `E` | Epílogo > 500 wc | validador histórico B117/H179 |
| `R` | Residuo > 300 wc | residuo sobredimensionado (familia B089/B096) |

**Epistemología:** una bandera es *señal adjudicable*, no bug demostrado.
En particular `Gt` (154) y `Gf` (179) son poblaciones nuevas sin adjudicar
— pueden esconder patrones estructurales legítimos que la gramática no
modela. La gramática SÍ modela el patrón multi-voto
(`...dispositivo>firma>voto_separado>cuerpo>dispositivo>firma>epilogo`
es legítimo y no dispara nada).

## Tabla: selección y exportes

Los **ticks de la tabla seleccionan** (multi-selección, por página); no
abren el caso. Con la selección:
- **🔍 Abrir caso**: entra al detalle (habilitado con exactamente 1 tickeado).
- **⬇️ Crudos (.md)**: descarga los bloques crudos de los tickeados, cada
  uno con encabezado de metadatos (id, carátula, ejes, banderas, secuencia,
  fuente y líneas). Anclaje canónico `source_file` + `linea_inicio`/
  `linea_fin_real` — el mismo de `extraer_caso.py` v2.0 (lección B102).
- **📋 Reporte auditoría (.md)**: filtros activos + conteos de banderas +
  muestra (N y seed) + marcas TP/FP/dudoso de la sesión + los crudos de
  los tickeados. Pensado como **insumo directo de la sesión H siguiente**
  (reemplaza el ciclo manual extraer_caso + notas sueltas).
- La descarga del **CSV filtrado** (datos tabulares) sigue aparte.

## Tab Auditoría (workflow)

1. **Panel de banderas**: conteo sobre la selección actual y sobre el
   corpus completo; el botón *Filtrar* activa el checkbox correspondiente.
2. **Muestreo**: N + seed → muestra aleatoria reproducible de la selección
   actual (mismo seed + misma selección = misma muestra; queda visible en
   el sidebar y se quita desde ahí). Para adjudicación por lectura.
3. **Marcado**: en el detalle de cada caso (tab Fuente → "Marcar caso"),
   botones TP / FP / dudoso + nota. El tab Auditoría acumula las marcas y
   las exporta a CSV. ⚠️ **Las marcas viven en la sesión del navegador:
   descargar el CSV antes de cerrar o refrescar.**

## Detalle de caso

Tabs **Fuente** (el `.md` pintado por zonas a ancho completo, con toggles
y presets de zona), **Metadatos** (todos los campos, incluidos los del
deriver, la secuencia de zonas, y el panel inline de considerando /
por_ello / firma completos desde textos.csv), y **Votos y zonas**
(votos individuales + resumen y tabla de segmentos).

## Historial

- v8/v8.1 (H186): sidecars del deriver, wcz_/nseg_ por zona, gramática de
  zonas (instrumento nuevo), tab Auditoría con muestreo y marcado,
  detalle en tabs, README. Fix post-smoke: namespace wcz_* por colisión
  con wc_dictamen del parser. v8.1: tabla multi-selección (los ticks
  eligen, no abren) + export de casos crudos .md + reporte de auditoría.
- v7/v6 (H096, M16 parcial): filtros de categorías nuevas, sidebar en
  grupos, tabs Tabla/Resumen, descarga CSV.
- v4.1 (H056): outliers, presets de zona.
- v1 (H045): visor inicial + diagnóstico sin_firma.
