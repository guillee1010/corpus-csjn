# Hx-1 — B177 + B178, ciclo MAJOR del vocabulario de `posicion`

Primera sesión de la serie Hx de la familia de la firma. El número H es el siguiente al último que figure en la BITÁCORA. Usalo en carpetas, commits y cierre. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`.

## Prerrequisito (bloqueante)

Tienen que estar cerradas H223 y H224 en la BITÁCORA. Leé `__version__` del parser y el cierre de H223. Si H223 no cerró su ciclo, pará.

## Qué leer antes de proponer (Gate 2)

En la DEUDA, `### B177` y `### B178` completos, con sus constancias H222. Ahí están la causa, los consumidores leídos uno por uno y los flip-sets previstos. No los repito acá para que no se desincronicen.

## U0 — Decisión del operador (bloqueante)

Proponé y esperá la confirmación.

- B178, "por su voto" se normaliza a "según su voto".
- B177, valor nuevo "en disidencia parcial" en `posiciones` y en `csjn_casos_votos.csv`.
- Si `n_disidencias` sigue contando parciales y totales juntas (propuesta, sí, sin columna nueva en este ciclo).

## U1 — Superficie y consumidores, en disco

1. Superficie de B177 con `scripts/validacion/superficie_b177.py` (ya versionado). Lo esperado son 132 fallos con marca en la firma.
2. Grep de los literales "en disidencia", "por su voto" y "según su voto" en todo `scripts/`, incluido el explorador. Confirmá contra el código cada consumidor que la DEUDA da por invariante.

## U2 — Fix

- `parse_firma` (L1356-1368 en v42.1), leer el grupo 2 de `RE_CALIFICADOR_FIRMA` y normalizar "por su voto".
- `has_disid` (L1406), dejar de comparar por igualdad. Sin este cambio, un fallo con disidencia parcial única pasa a `unanime`.
- Las líneas citadas son de v42.1. Después de H223 pueden haberse corrido.

## U3 — PoC A/B y ciclo MAJOR

- Brazos sobre código real (instalado contra parcheado en memoria), candado E0 contra lo publicado. Si H223 dejó un harness en `scripts/diagnostico/`, reusalo.
- Flip-set previsto. `posiciones` en los fallos con marca en la firma más los 5 de B178. `voting_pattern` con 0 flips en todo el corpus. `n_disidencias` invariante.
- Ciclo MAJOR. CODEBOOK (`posiciones` y la tabla de `posicion`) y el DELTA de codebook que use el proyecto.
- Después del ciclo, corré `scripts/validacion/kappa_sjconsulta.py` y registrá cómo se mueve el acuerdo. Las posiciones B177 y B178 de la adjudicación H221 deberían pasar a coincidir.

## Fuera de alcance

Consumo de headers en `posiciones` (B180 (b)), que es la sesión siguiente de la serie.
