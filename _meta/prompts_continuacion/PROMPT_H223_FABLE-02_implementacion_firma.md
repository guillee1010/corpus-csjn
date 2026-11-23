# H223 (FABLE-02) — Implementación de dos fixes de la familia de la firma (corpus-csjn)

Esta sesión es la H223, rotulada FABLE-02. La H222 fue la auditoría FABLE-01 y su registro documental. La H224 es otra agenda, no la toques. Usá H223 en los nombres de carpeta, commits y pull request.

Trabajás sobre el repositorio `guillee1010/corpus-csjn`. Usá el skill `apertura-sesion-corpus` y respetá sus gates. Lo adjunto es el informe de una auditoría previa de solo lectura (`informe_auditoria_firma.docx`). Sus números salieron de un sandbox y son **hipótesis a reproducir**, no datos. La DEUDA ya los registra, en las constancias H222 de B019 y en la entrada B181. Leelas antes de empezar (Gate 2). Si la DEUDA y este prompt dicen cosas distintas, parás y me preguntás.

## Paso 0 — base de trabajo (bloqueante)

1. Pedí acceso de escritura al repositorio (`add_repo` con `access: "push"`) y cloná. Si falla, decime qué falta y seguí en modo solo lectura, entregando el parche como archivo.
2. Leé `__version__` de `scripts/pipeline/parser.py` y el último commit. Lo esperado es parser v42.1 y como último commit `d05b344` (H222-05, cierre documental de H222, sin cambios de pipeline). La auditoría se hizo sobre `aa4c742` (cierre H221), que tiene el mismo parser. **Preguntame si mi disco local tiene cambios sin pushear en el parser o en los outputs canónicos.** No avances hasta que confirme que la base es la misma.
3. Trabajá en una rama nueva `h223-familia-firma`. Nunca en `main`.

## Qué tenés que entregar

- Un pull request con el cambio de `scripts/pipeline/parser.py`, en **dos commits separados, uno por unidad** (Gate 6). Cada commit con su bump de versión propuesto (MINOR, v42.2 y v42.3) y el comentario in situ con el estilo del parser (causa, espec, flip-set sellado).
- Los scripts de superficie y PoC, más sus CSV de baseline, en `scripts/diagnostico/H223/`. Leé antes `scripts/diagnostico/README.md` para respetar la convención, y si dice que esa carpeta no se commitea, entregámelos como archivos.
- Un informe corto por unidad con superficie medida, flip-set sellado y adjudicación fila a fila de todo lo que se mueve.

No toques el golden, el manifest, los outputs canónicos, el CODEBOOK, la DEUDA, la BITÁCORA ni el CHANGELOG. El regolden, el manifest, el gate M55 y el cierre documental los corro yo en mi disco. Esa corrida local es la que cierra la unidad.

## Harness común (antes de las dos unidades)

Un PoC A/B con dos brazos sobre **código real**, el brazo A con el parser instalado y el brazo B con el mismo parser y el parche aplicado en memoria. Cero réplica de lógica. Para armarlo, leé `main()` entero (L4717 en v42.1) y replicá su loop verbatim. Los PoC de sesiones anteriores no están en el repo, así que el harness hay que escribirlo.

Candado E0. El brazo A tiene que dar igual a lo publicado en `output/parser/` en todas las columnas de `csjn_casos.csv`, y en `csjn_casos_votos.csv` y `csjn_casos_textos.csv`. Si E0 no da exacto, parás y me mostrás la diferencia. Sin E0 limpio no hay flip-set.

## U1 — B019, firma partida después de `linea_fin_real`

**Hipótesis de la auditoría.** Los patrones de `_meta/jueces/jueces_csjn.csv` exigen nombre y apellido. Un renglón de continuación de firma ("Carlos Maqueda.", "Rosatti.", "LORENZETTI.", "ARGIBAY.", "RAÚL ZAFFARONI.") no pasa `hay_juez_conocido` (L1095) ni `linea_es_firma_de_juez` (L2282). Eso deja `linea_fin_real` un renglón antes por tres caminos.

- Camino A, pista `firma_actual`. `extender_firma` (L3284) frena en la continuación. Testigos 339_p155 y 344_p3695.
- Camino B, pista `sumario_siguiente`. `linea_es_header_sumario_guardado` (L2468) acepta "LORENZETTI." como header de sumario. Testigo 329_p158.
- Camino C, pista `caratula_siguiente`. En la etapa B de `retroceder_frontera` (L3055), "RAÚL ZAFFARONI." pasa como carátula por forma y `_es_continuacion_wrap` (L3003) no lo protege porque la línea anterior termina en "E.". Testigo 330_p4345.

**Paso 1, superficie.** La línea `linea_fin_real` pasa `linea_es_firma_de_juez`, y la siguiente no vacía mide 60 caracteres o menos, matchea `_RE_FIRMA_COMPLETA` (L1252) y no pasa `linea_es_firma_de_juez`. El sandbox dio 40 casos, 22 por A, 7 por B y 11 por C (anexo A del informe). Si da otro número, adjudicá la diferencia leyendo los casos. Medí también el mismo predicado sobre todo el corpus sin la condición de `linea_fin_real` (el sandbox dio 1.571 pares) y revisá una muestra para confirmar que no hay pares que no sean firma.

**Paso 2, fix.** Agregá un helper `_es_continuacion_firma(lines, k)` con ese predicado, aplicado una sola vez al fin que devuelve `detectar_fin_real`, un renglón como máximo y sin pasar `limite_adelante`. El lugar preferido es el caller, entre L4122 y la reconstrucción del bloque en L4133, porque cubre todas las pistas en un solo punto. Si al leer el código encontrás una razón para ponerlo adentro de `detectar_fin_real`, explicámela antes de hacerlo. No toques `jueces_csjn.csv` ni `hay_juez_conocido`, porque un patrón de apellido solo cambia el radio de decenas de consumidores (ver B169 y RUIDO_FIRMA, L1107).

**Paso 3, flip-set previsto.** Los 40 casos, con `linea_fin_real` +1, `n_jueces` +1 y el juez agregado en `posiciones`. El único flip de `voting_pattern` previsto es 338_p1060 (`unanime` → `segun_su_voto`), por el calificador que trae la continuación. `n_votos_svoto` no debería moverse en ningún caso. El voto que sigue a la firma en 338_p1060 y 329_p5210 queda igual fuera del bloque, y es una sub-clase aparte que solo se registra. 343_p1762 queda fuera, porque es un "Lorenzett." de OCR y no B019. Cualquier movimiento fuera del set se adjudica leyendo el caso.

## U2 — B181, calificador deforme

**Hipótesis de la auditoría.** `RE_CALIFICADOR_FIRMA` (L1127) no tolera calificadores con guion de corte, guion blando U+00AD, puntuación antes del ")" o la variante "mi voto". `parse_firma` (L1317) no aplica `_unhyphenate` (L627). En el sandbox afecta a 10 fallos.

- Guion de corte. 329_p928, 329_p2649, 329_p2655, 329_p2847 y 330_p685.
- Guion blando. 334_p35, 332_p1095 y 333_p1464.
- "(según mi voto)". 331_p866.
- "(en disidencia.)". 343_p1800, que la H221 registró como B180 (a) y la H222 reclasificó a B181.

**Paso 1, superficie.** Grep sobre `corpus/*.md` de las cuatro variantes, cruzado con el rango de cada caso y con su `firma_raw` publicado. Antes del fix, grep de U+00AD en `jueces_csjn.csv` para confirmar que ningún patrón depende del guion blando.

**Paso 2, fix.** En `parse_firma`, pasá `firma_raw` por `_unhyphenate` antes de buscar jueces y calificadores, así los índices y las ventanas quedan sobre el mismo string. `RE_CALIFICADOR_FIRMA` tiene que admitir `(?:su|mi)` y puntuación opcional antes del cierre. `RE_CALIFICADOR` (L1117) queda intacta, porque tiene consumidores en frontera y en B148 que no están medidos (decisión H216). El `firma_raw` publicado no cambia.

**Paso 3, flip-set previsto.** Los 10 casos. En 343_p1800, 329_p928 y 334_p35, `voting_pattern` pasa a `disidencia`, y en 331_p866 pasa a `segun_su_voto`. En los otros seis cambia solo la posición de un juez. `panel_cprima` (L1428) usa el mismo `parse_firma`, así que `tiene_cal` puede cambiar la zona elegida. Si E0 fuera del set no da exacto, cada movimiento se adjudica.

## U3 opcional — B179 (solo lectura, sin tocar el parser)

Hacelo solo si U1 y U2 quedaron cerradas y te lo confirmo. El problema es una posición expresada dentro del voto común con firma limpia. Medí la superficie sobre `considerando_text` y `por_ello_text` de `csjn_casos_textos.csv` con estas fórmulas.

- "X se remite a su voto/disidencia".
- "se remiten a sus votos/disidencias".
- "por mayoría, se resuelve/declara/hace/desestima".
- "los jueces A y B consideran/entienden".
- "deja a salvo su opinión".

Leé cada caso y adjudicalo como remisión propia, minoría declarada sin nombre o falso positivo. Los testigos positivos son 341_p961, 341_p1063, 343_p536 y 343_p1923, y el falso positivo sellado es 342_p287. El resultado es un CSV adjudicado y una propuesta de reglas con su precisión medida. No implementes nada.

## Fuera de alcance

B177 y B178 quedan afuera porque requieren una decisión de schema mía (ciclo MAJOR). También quedan afuera B180 (b), M68, B182, B183 y B184. Si al trabajar ves algo nuevo, lo anotás en el informe y no lo abrís.

## Forma de trabajo

- Escribí en castellano rioplatense.
- Antes de cada fix, mostrame la superficie y esperá que diga que sigas.
- Separá lo verificado de lo inferido.
- Ningún "validado" ni "limpio" sin el dato corrido a la vista.
