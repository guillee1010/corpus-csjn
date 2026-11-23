# H225 — B177 y B178, vocabulario de `posicion` (corpus-csjn)

Esta sesión es la H225. La H223 fue FABLE-02 (B019 y B181, parser v42.3, cerrada con regolden y manifest). La H224 está reservada para la agenda que dejó la H221, no la toques. Usá H225 en los nombres de carpeta, commits y pull request.

Trabajás sobre el repositorio `guillee1010/corpus-csjn`. Usá el skill `apertura-sesion-corpus` y respetá sus gates. Leé antes de empezar las entradas B177 y B178 de `DEUDA_TECNICA.md`, con sus constancias H222 y la decisión del operador registrada en H223 (Gate 2). Si la DEUDA y este prompt dicen cosas distintas, parás y me preguntás.

## Paso 0, base de trabajo (bloqueante)

1. Pedí acceso de escritura al repositorio (`add_repo` con `access: "push"`) y cloná.
2. Leé `__version__` de `scripts/pipeline/parser.py` y el último commit de `main`. Lo esperado es parser v42.3 y el commit de la decisión de B177 (H223-07) o uno posterior solo documental. Preguntame si mi disco tiene cambios sin pushear en el parser o en los outputs canónicos, y no avances hasta que confirme.
3. Trabajá en una rama nueva `h225-vocabulario-posicion`. Nunca en `main`.

## La decisión ya está tomada

Valor nuevo "en disidencia parcial" en `posiciones` y en `csjn_casos_votos.csv.posicion`, ciclo MAJOR con CODEBOOK. "por su voto" pasa a "según su voto" en el mismo ciclo. Solo la vía de la firma (`parse_firma`). La vía de los headers (`RE_DISID_HDR` colapsado en `detectar_votos_disidencias`) queda para B180 (b), no la toques.

## Harness

Te adjunto `harness_ab.py` de la H223. Llama a `parser.main()` real con los argumentos de `correr_pipeline.py`, brazo B con el parche aplicado en memoria, y tiene modos `A`, `B`, `real` y `diff`. Ponelo en `scripts/diagnostico/H225/`. Si no lo adjunté, pedímelo antes de escribir uno.

Candado E0. El brazo A tiene que dar igual por sha256 a lo publicado en `output/parser/` en casos, votos y textos. Sin E0 limpio no hay flip-set. Al final verificá que el parser commiteado, corrido sin parche, reproduce el brazo B byte a byte en los cinco CSV del parser.

## U1, B177 disidencia parcial

Paso 1, superficie. Corpus-wide sobre `firma_raw` publicado, con `RE_CALIFICADOR_FIRMA` importada del parser, todos los matches con el grupo 2 ("parcial") no vacío. La H222 dio 132 fallos en sandbox, es hipótesis. Cruzá con las 12 posiciones de 11 fallos que lista la DEUDA desde sjconsulta.

Paso 2, fix. En `parse_firma`, leer el grupo 2 y publicar "en disidencia parcial". Cambiar `has_disid` (L1406 en v42.1, buscá la línea en v42.3) para que la parcial cuente como disidencia, así `voting_pattern` no se mueve. Releé los consumidores que la constancia H222 dio por invariantes y confirmalos en el código de v42.3, porque la H223 tocó `parse_firma`.

Paso 3, flip-set previsto. Los fallos de la superficie en `posiciones` y en `votos.csv.posicion`, cero en `voting_pattern` y en `n_disidencias`. Cualquier otro movimiento se adjudica leyendo el caso.

## U2, B178 "por su voto"

Superficie, las 8 posiciones en 5 fallos que lista la constancia H222. Fix de una línea en `parse_firma`. Flip-set previsto, esas 8 posiciones, cero en `voting_pattern`.

## Qué tenés que entregar

- Un pull request con `scripts/pipeline/parser.py` en dos commits, uno por unidad. Proponé el bump de versión de cada uno y justificalo. Si B178 necesita su propio MAJOR, decímelo antes de commitear.
- El texto de los cambios del CODEBOOK (vocabulario de `posicion` y la tabla de conteos), en el informe, sin commitearlo.
- Un informe corto por unidad con superficie medida, flip-set sellado y adjudicación de todo lo que se mueve.
- Los scripts y CSV en `scripts/diagnostico/H225/`. Esa carpeta no se commitea, entregámelos como archivos.

No toques el golden, el manifest, los outputs canónicos, la DEUDA, la BITÁCORA ni el CHANGELOG. El regolden, el manifest, M55 y el cierre documental los hacemos después, con mi corrida local.

## Forma de trabajo

- Escribí en castellano rioplatense.
- Antes de cada fix, mostrame la superficie y esperá que diga que sigas.
- Separá lo verificado de lo inferido.
- Ningún "validado" ni "limpio" sin el dato corrido a la vista.
- Si una superficie da menos de 10 casos, avisame antes de armar el ciclo completo de harness y flip-set. Puede alcanzar con cerrarla documentada.
- Si al trabajar ves algo nuevo, lo anotás en el informe y no lo abrís.
