# H227 — FABLE-03. Auditoría externa de lo implementado después de FABLE-01

Sesión de auditoría del proyecto corpus-csjn, de solo lectura respecto del pipeline. Abrí con `apertura-sesion-corpus`. No cierres con `cierre-sesion-corpus`. El registro en DEUDA y BITÁCORA lo hace el operador en otra sesión, con tu informe, como pasó con FABLE-01 en H222.

## Quién sos en esta sesión

Sos un auditor externo. No tenés historia de las sesiones y no la necesitás. Lo que sigue es lo que las sesiones dicen que hicieron. Tratalo como afirmaciones a verificar, no como hechos. Si algo de lo declarado no se reproduce, ese es el hallazgo más valioso que podés entregar.

Repo `https://github.com/guillee1010/corpus-csjn`. Base de esta auditoría, la punta de `main` al momento de clonar. Al empezar, registrá el commit (cuando se escribió este prompt era `d1ec353`, H224-24, parser v43.3). Si `main` tiene commits posteriores que tocan `scripts/pipeline/` u `output/parser/`, pará y avisá antes de seguir.

Base de FABLE-01, el commit `aa4c742` (cierre H221, parser v42.1). Su informe, `informe_auditoria_firma.docx`, no está en el repo. Lo que encontró está resumido en el bloque H222 de la BITÁCORA y en las entradas de la DEUDA que cita.

## Qué pasó desde FABLE-01

| Sesión | Qué declara | Parser | Commits |
|---|---|---|---|
| H222 | Registro de FABLE-01 en la DEUDA. Abre B181, B182, B183, B184 y M68. | v42.1, sin cambios | — |
| H223 (FABLE-02) | Cierra B019 (continuación de firma partida después de `linea_fin_real`) y B181 (calificador deforme). No hace B179. | v42.2, v42.3 | `185728d`, `1fa85b4`, merge `0c03d58`, regolden `66c7bf3`, M55 `981bee2` |
| H225 | Cierra B177 ("en disidencia parcial" como valor propio, MAJOR) y B178 ("por su voto" normalizado). | v43.0, v43.1 | `aa69ad9`, `3513e87`, merge `af0921c`, regolden `eade476` |
| H226 | Versiona M68 (`validar_m68.py`), cierra B184 (header deshifenado) y B180 (b) (headers que corrigen `posiciones`, cuatro guardas). Abre B185 a B189. | v43.2, v43.3 | `6948d96`, `54be8f7`, merge `2fdb190`, regolden `31baab1` |
| H224 | Solo lectura. B179 medido (56 posiciones en 38 fallos), M67 recomputado, κ de posiciones contra SJ 0,9598 → 0,988, B190 nuevo, CODEBOOK 3.0, paquete de Dataverse 4.0. | v43.3, sin cambios | `eeca8b0` a `d1ec353` |

Las cifras declaradas de cada unidad (flip-sets, superficies, movimientos de `voting_pattern`, conteos de `posicion`) están en los bloques H223, H225, H226 y H224 de la BITÁCORA y en las entradas cerradas de la DEUDA. Leelas antes de empezar. Son tu lista de afirmaciones.

## Reglas

- Solo lectura. No commitees ni pushees nada al repo, ni a `main` ni a una rama. Trabajás sobre un clon.
- Fuente única. Los predicados y funciones del parser se importan o se llaman desde `scripts/pipeline/parser.py`. No reescribas una regex para medir. Si necesitás observar una función por dentro, envolvela (grabadora), no la copies.
- Candado E0 antes de medir. Corré `parser.main()` real (con `sys.argv` armado como lo hace `scripts/pipeline/correr_pipeline.py`) sobre el corpus del clon y comprobá por sha256 que reproduce los cinco CSV de `output/parser/` byte a byte. Sin E0 limpio no se mide nada.
- No compares los `.md` del corpus contra el sha del manifest. El manifest hasheó una copia CRLF y el repo normaliza a LF (constancia H223). Eso es conocido y no es hallazgo.
- Todo testigo que cites, leído con texto en el `.md` del tomo, con archivo y líneas.
- Cada superficie, con su instrumento entregado y con las cifras separadas en medido, leído y sin leer.
- Una unidad por vez. Al terminar cada una, un resumen corto antes de seguir.
- Si te falta tiempo, el orden de prioridad es U0, U1, U2, U5, U4, U3, U6.

## Unidades

### U0 — Base y candados

1. Clon, commit de base y versión del parser leída de `__version__`.
2. E0 sobre la base (v43.3).
3. Reconstrucción de la cadena de versiones. Corré el parser de cada commit de la tabla (`aa4c742`, `185728d`, `1fa85b4`, `aa69ad9`, `3513e87`, `6948d96`, `54be8f7`) sobre el mismo corpus y guardá los CSV de casos y votos de cada uno. Para cada versión, comprobá que el resultado coincide con lo que el regolden correspondiente dejó en `output/parser/` en ese momento de la historia (cuando haya regolden), y avisá cualquier diferencia.

### U1 — ¿Las correcciones hicieron lo que dicen?

Con los CSV de U0, un diff keyed-by-caso (y keyed-by-caso y juez en votos) entre cada versión y la siguiente. Cada paso es el flip-set real de un fix.

- Compará cada flip-set real con el declarado en la BITÁCORA, en cantidad de casos, columnas que se mueven y casos nombrados. Ejemplos de lo declarado, B019 40 casos con `n_jueces` +1 en 38 y un solo flip de `voting_pattern` (338_p1060); B181 12 casos con `voting_pattern` corregido en 5; B184 8 celdas de votos en 2 casos; B180 (b) 10 casos y 11 jueces, `voting_pattern` en 7. Para B177 y B178, las cifras de H225-02 y H225-03.
- Diff acumulado `aa4c742` → base. Toda celda movida tiene que caer en algún flip-set. Las que no caen son hallazgo.
- Columnas que no debían moverse (textos, zonas, editorial, y en casos todo lo que no sea panel y posición). Confirmá que no se movieron, o listá qué se movió.
- Leé con texto una muestra de cada flip-set (todos si son 12 o menos, 10 al azar con semilla fija si son más) y adjudicá cada caso como corrección verdadera, costo o error nuevo. Incluí en la muestra los tres "curados por rebote" de H226 (330_p452, 330_p472, 348_p708) y decí si el rebote es una corrección legítima o un acierto por la razón equivocada.

### U2 — Las superficies de FABLE-01, re-medidas sobre v43.3

Los instrumentos de FABLE-01 no se versionaron. Reconstruílos desde la descripción del bloque H222 y de cada entrada de la DEUDA, con predicados importados.

- B019. ¿Queda alguna continuación de firma partida fuera del bloque? Estado del residual que el fix no curaba (voto entero detrás de la firma partida, 338_p1060 y 329_p5210).
- B181. ¿Queda algún calificador deforme sin leer? Probá las variantes que FABLE-01 nombró (guion de corte, guion blando, "mi voto", puntuación interna) y buscá otras.
- B177 y B178. Conteo de "en disidencia parcial" y de "por su voto" crudos que no llegan a `posiciones` normalizados.
- B180 (b) y M68. Corré `scripts/validacion/validar_m68.py --baseline output/validacion/m68_pool_baseline.csv`. El pool declarado es 13. Adjudicá los 13 con lectura y decí si cada uno es FP conocido, bug abierto con número (B185 a B189) o algo nuevo.
- B179. Reproducí `scripts/validacion/superficie_b179.py` v0.6 (declarado, 81 matches en 53 fallos) y contrastá una muestra de `output/validacion/adjudicacion_b179_h224.csv` con el texto.

### U3 — Lectura del código de los fixes

`git diff aa4c742..HEAD -- scripts/pipeline/parser.py`, función por función.

- Por cada cambio, radio real. Qué otros consumidores llaman a la función tocada y si alguno cambia de comportamiento fuera del flip-set.
- Reglas duplicadas o que ahora conviven en dos lugares (por ejemplo `RE_CALIFICADOR` y `RE_CALIFICADOR_FIRMA`, M65).
- Guardas que no filtran nada. H226 declara que la guarda 3 de B180 (b) es vacua y se mantiene por diseño. Evaluá si eso se sostiene.
- Orden de las etapas. `_subir_posiciones_desde_headers` corre después de `extraer_textos_votos` y antes del guard B087. Verificá que ese orden no deja casos en que un header de un documento ajeno (B186) suba una posición.
- Decisiones de versión (MAJOR o MINOR) contra lo que el CODEBOOK documenta del schema.

### U4 — Abiertos de la familia, con cardinalidad

Para B182, B183, B185, B186, B187, B188, B189 y B190, corré el validador que propone cada entrada de la DEUDA (o uno equivalente con predicados importados). Para cada uno, cardinalidad medida, efecto en columnas publicadas (`posiciones`, `voting_pattern`, `n_jueces`, `votos.texto_voto`), testigos leídos y una recomendación de si justifica un ciclo. El criterio del operador es que una superficie de menos de 10 casos no justifica un ciclo entero de harness y flip-set, salvo que mueva una columna que la tesis usa (posiciones, voting_pattern, mayoría absoluta).

### U5 — Hallazgos nuevos

Buscá clases de error que la DEUDA no tenga. Empezá por invariantes baratas sobre los canónicos, que no exigen leer el tomo.

- `voting_pattern` recalculado desde `posiciones` con la regla del parser (`_voting_pattern_de_jueces`) contra el publicado.
- `n_jueces` contra la cantidad de jueces de `posiciones`.
- Cada juez de `posiciones` con su fila en `csjn_casos_votos.csv` y la misma posición, y al revés.
- `is_full_bench` contra la aritmética que declara H223.
- Nombres distintos de jueces en `votos.csv` (H224 contó 79 contra "44" del CODEBOOK). Agrupá variantes y decí cuáles son el mismo juez.
- Headers conjuntos que dejan un solo juez en el marcador (B188).
- Las 5 posiciones con "(en disidencia parcial)" impreso que SJ registra distinto (H224-10) y las 20 de 301 de M67 que cambian de clase si el disidente parcial cuenta en la cabeza (H224-03). No decidas la definición, mostrá qué la decide.

Después, si queda tiempo, cualquier otra familia que veas en el camino. Todo hallazgo nuevo, con número provisorio (N1, N2…), testigo leído, cardinalidad y daño en columnas publicadas.

### U6 — Lo que se va a publicar en Dataverse 4.0

El paquete se arma con `_meta/dataverse/archivos_publicacion.txt` y `scripts/auxiliares/preparar_bundle_dataverse.py`.

- Toda cifra de `CODEBOOK.md` (versión 3.0) y de `_meta/dataverse/README.md`, recalculada desde los CSV del repo. Lista de las que no coinciden.
- La lista de publicación contra el manifest y contra lo que existe en el repo.
- Ningún archivo de la lista con datos de funcionarios o del cache de sjconsulta.
- Los κ contra SJ no se pueden reproducir sin el cache, que no está en el repo. Solo comprobá que las cifras del CODEBOOK coinciden con `output/validacion/kappa_*.csv`.

## Entregables

Todo como archivos para descargar, fuera del repo.

1. `informe_FABLE-03.docx`. Arriba, un resumen de una página con tres listas. Afirmaciones verificadas. Afirmaciones que no se reproducen (con la cifra declarada y la medida). Hallazgos nuevos ordenados por daño en columnas publicadas. Después, una sección por unidad.
2. `propuesta_agenda.md`. Los próximos ciclos sugeridos, en orden de prioridad, cada uno con su superficie, el fix candidato si lo hay, el radio estimado y por qué va en ese lugar. Separá lo que es del parser, lo que es de validación y lo que es de documentación.
3. Un `.zip` con los instrumentos (`scripts/diagnostico/H227/`, pensado para gitignorear), los CSV de cada superficie y de cada flip-set reconstruido, y las adjudicaciones con archivo y líneas.

Las superficies son preliminares hasta que el operador las reproduzca en su disco local (Gate 4). Decilo en el informe.
