# H224 — Agenda que dejó H221 (análisis de votación y validaciones contra SJ)

Sesión de trabajo del proyecto corpus-csjn. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`.

## Origen de esta agenda

H221 cerró con una lista de pendientes "ver PROMPT_H222". El número 222 se usó después para la auditoría FABLE-01 de la familia de la firma, y 223 para su implementación. Esa agenda pasa a ser esta sesión. Si el operador adjunta el PROMPT_H222 original, leelo como complemento. Cuando haya diferencias, manda este prompt, porque está actualizado con lo que pasó después.

## Prerrequisito (bloqueante)

En la BITÁCORA tienen que estar cerradas H222 y H223. Leé el bloque de cierre de H223 para saber qué cambió en el parser (B019 y B181) y si hizo la unidad opcional de B179. Si H223 no está cerrada, pará y avisá.

Las cifras de votación de H221 (M67, tabla por secretaría) se midieron con el parser v42.1. Si H223 movió `posiciones`, recomputá con los scripts versionados antes de usar cualquier número (`scripts/analisis/m67_mayoria_absoluta.py`, `scripts/analisis/secretarias_votacion.py`).

## Qué ya no hace falta

- El diseño conjunto del fix de la familia de la firma y la auditoría externa ya se hicieron (H222, H223).
- 343_p1762 ya está leído. No es disidencia parcial sin publicar, es un apellido truncado por OCR (B182).
- La medición de B179 queda solo si H223 no hizo su unidad opcional. Si la hizo, usá su CSV adjudicado y no la repitas.

## Unidades

Una por vez (Gate 6).

### U1 — Corrección del dato curado

En `output/validacion/adjudicacion_sjconsulta_h221.csv`, la fila de 343_p1762 (LORENZETTI) dice `clase=B019`. Corregirla a `B182`, con la evidencia "firma 'Ricardo Luis Lorenzett.' L12264, apellido truncado por OCR". Verificá antes la línea en `corpus/LibroVol343-3.md`.

### U2 — Los tres fallos con marca de disidencia parcial sin disidencia publicada

332_p1394, 346_p931 y 344_p174. Están en `output/validacion/superficie_b177.csv` con marca y sin ninguna disidencia en `posiciones`. Leé cada uno y adjudicá la causa (cita de precedente, firma truncada, calificador deforme como B181, otra). Si alguno es clase nueva, se registra.

### U3 — B179 (solo si H223 no lo hizo)

Superficie sobre `considerando_text` y `por_ello_text` de `csjn_casos_textos.csv` con las fórmulas de la constancia H222 de B179 en la DEUDA. Adjudicación leyendo cada caso. Salida, un CSV adjudicado.

### U4 — Cruce doctrina × fallos sin mayoría absoluta

Sobre los fallos que M67 clasifica como voto de cabeza sin mayoría absoluta. Para cada uno, si SJ atribuye sumarios y holding, a qué voto los atribuye. La pregunta para la tesis es si la doctrina que se extrae de una mayoría circunstancial se atribuye al tribunal o al voto. Primero una muestra chica y leída, después la escala.

### U5 — Citas posteriores de mayorías circunstanciales

Cómo se citan después esos fallos en el corpus, como "Fallos: X" a secas o con la aclaración del voto. Superficie primero, sin interpretar antes de leer una muestra.

### U6 — Validaciones contra SJ que quedaron abiertas

- Secretaría de SJ contra el trabajo de campo de la tesis. Pedile al operador lo que necesites del campo, no lo supongas.
- Concordancia de disposición y vía con SJ, para achicar M43.

## Forma de trabajo

- Mostrá cada superficie antes de interpretar.
- Separá lo verificado de lo inferido.
- Lo que sirva para la tesis queda marcado como insumo, sin redactar conclusiones.
