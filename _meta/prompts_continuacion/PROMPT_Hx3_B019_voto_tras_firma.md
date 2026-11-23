# Hx-3 — Residual de B019, voto entero que queda fuera del bloque detrás de la firma

Tercera sesión de la serie Hx de la familia de la firma. El número H es el siguiente al último de la BITÁCORA. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`.

## Prerrequisito (bloqueante)

Tiene que estar cerrada H223 (fix de B019, extensión de un renglón al salir de `detectar_fin_real`). Si no, pará.

## Qué leer antes de proponer (Gate 2)

En la DEUDA, `### B019` completo (constancia H222 y cierre de H223), `### B020` y `### B021` (misma cascada `detectar_fin_real`) y `### B168` (colector de firma y headers de voto).

## El problema

En 338_p1060 la firma del voto común termina en "Carlos Maqueda (según su voto)." y en la línea siguiente arranca "Voto del señor ministro doctor don Juan Carlos Maqueda" (L15306 de LibroVol338.2). La pista `firma_actual` cierra el bloque en la firma del voto común y el voto separado queda afuera. Su texto no llega a `texto_voto` y `n_votos_svoto` queda en 0. 329_p5210 tiene la misma forma con un voto del presidente.

## U1 — Superficie

Fallos cuyo `linea_fin_real` es seguido, antes del inicio del caso siguiente, por un header de voto o disidencia que matchea `_hdr_tipo_wrap` (fuente única). Desglosá por pista. Leé una muestra de cada pista antes de diseñar.

## U2 — Diseño

La hipótesis de partida es extender el fin hasta la última firma del último voto separado contiguo, frenando en la carátula o el sumario del caso siguiente. Antes de proponerla, leé `extender_firma` y `retroceder_frontera` completos y explicá por qué no basta con ensancharlas. El riesgo principal es B020, que el fin se extienda al fallo siguiente. Medilo explícitamente.

## U3 — PoC A/B y ciclo

Candado E0. Flip-set con `linea_fin_real`, `n_votos_svoto` o `n_disidencias`, `wc_votos` y `texto_voto` en votos.csv. Cualquier caso cuyo nuevo fin pase el inicio del caso siguiente es costo y se adjudica.
