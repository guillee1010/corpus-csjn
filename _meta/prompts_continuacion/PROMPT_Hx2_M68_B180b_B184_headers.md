# Hx-2 — M68 como candado, y después B180 (b) + B184 (headers que corrigen posiciones)

Segunda sesión de la serie Hx de la familia de la firma. El número H es el siguiente al último de la BITÁCORA. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`.

## Prerrequisito (bloqueante)

Tienen que estar cerradas H223 (B181) y Hx-1 (vocabulario con "en disidencia parcial"). Si no, pará. Esta sesión depende de las dos, porque los headers "Disidencia parcial" tienen que mapear a la categoría nueva y los calificadores deformes ya tienen que leerse.

## Qué leer antes de proponer (Gate 2)

En la DEUDA, `### B180`, `### B184`, `### M68`, `### B170` y `### B169` completos. B170 importa porque sus FP de header pasarían a tocar `posiciones` si las guardas fallan.

## U1 — M68, el validador

Script versionado en `scripts/validacion/` con la invariante de M68. Si hay header de disidencia detectado, al menos una posición con "disidencia". Si hay header de voto, al menos una posición de voto o `voting_pattern segun_su_voto`. Corrido sobre canónicos actuales. El pool de la auditoría eran 26 fallos con el parser v42.1. Después de H223 tiene que haber bajado en los B181. Adjudicá todo el pool que quede, leyendo los casos.

## U2 — B184

`_unhyphenate` sobre `header_completo` en `detectar_votos_disidencias` antes de buscar el juez. Superficie primero, con headers detectados cuyo marcador quedó sin juez. Testigo 344_p1444.

## U3 — B180 (b)

Subir la posición de un juez sin calificador cuando tiene marcador de header con juez detectado. Nunca cambiar una posición que ya trae calificador. Tres guardas.

1. Header posterior a `por_ello_idx`.
2. Juez presente en la firma del caso.
3. Juez con `texto_voto` no vacío.

Medí cuántos casos pasan cada guarda por separado antes de combinarlas. Flip-set previsto, el subconjunto del pool de M68 que sea B180 (b) genuino. 344_p1444, 348_p1505, 329_p6087 y 347_p2160 fueron leídos por la auditoría. Los FP conocidos (329_p3148, 348_p728, 344_p441) no pueden moverse. `voting_pattern` se recomputa con la misma regla de `parse_firma`, extraída a un helper para no duplicarla. El guard B087 tiene que correr después.

## U4 — Ciclo

PoC A/B con candado E0, ciclo MINOR o MAJOR según si cambia la semántica de `voting_pattern` (decidir con el operador). M68 queda como candado del ciclo.
