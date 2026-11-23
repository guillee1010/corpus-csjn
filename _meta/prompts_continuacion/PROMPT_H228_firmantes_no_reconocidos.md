# H228 — Firmantes que la tabla de jueces no lee (B194, B195, B187, B182, B185)

Sesión de implementación del proyecto corpus-csjn. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`.

## Contexto

La auditoría FABLE-03 (H227) midió una familia de errores en la lectura de la firma. Cada clase sola tiene menos de 10 casos, pero juntas cambian `posiciones` de jueces titulares en fallos de 2024 y 2025, que es la excepción del criterio del operador para abrir un ciclo. Leé en la DEUDA las entradas B194, B195, B187, B182 y B185, y en la BITÁCORA los bloques H226 y H227. Son tu punto de partida y se tratan como afirmaciones a verificar.

| ID | Qué | Medido en H227 |
|---|---|---|
| B194 | Apellido compuesto impreso con raya ("García—Mansilla"), el patrón de `jueces_csjn.csv` solo admite guion o espacio | 4 fallos (348_p83, 348_p113, 348_p179, 348_p189), juez ausente del panel |
| B195 | Calificador atribuido al juez anterior cuando entre ambos hay un firmante no reconocido | 3 fallos (348_p189, 347_p1701, 347_p1673) |
| B187 | Conjueces firmados en orden apellido-nombre ("Borinsky Mariano Hernán") | 3 casos más 348_p708 |
| B182 | Apellido truncado por OCR ("Lorenzett.") | 1 caso (343_p1762) |
| B185 | "(SU VOTO)" a secas en la firma | 2 casos, ya curados por B180 (b) |

Repo `https://github.com/guillee1010/corpus-csjn`, la punta de `main`. Al empezar, registrá el commit y la versión del parser. Tiene que ser v44.0 con el regolden H227 hecho (golden y `_manifest.json` re-sellados por el operador). Si el regolden no está en `main`, pará y avisá.

## Reglas

- Trabajás sobre un clon, en una rama propia (`h228-firmantes`). Nada se commitea a `main` sin PR.
- Fuente única. Los predicados se importan de `scripts/pipeline/parser.py`. Para observar una función por dentro, envolvela con una grabadora, no la copies.
- Candado E0 antes de medir. `parser.main()` real, con `sys.argv` armado como en `correr_pipeline.py`, tiene que reproducir por sha256 los cinco CSV de `output/parser/`.
- Antes de tocar el parser, mostrale al operador la adjudicación completa del pool, caso por caso y leída en el tomo, con archivo y líneas, y frená a esperar su OK.
- Todo cambio de patrón en `_meta/jueces/jueces_csjn.csv` se mide con una superficie de radio sobre todos los consumidores de `JUECES_CONOCIDOS` (zonificador, frontera, B148, A001, B169), como se hizo en B019. Si el radio sale de la familia, se descarta y se documenta.
- Harness A/B. El brazo A es v44.0, el brazo B el mismo `main()` con el parche en memoria. Flip-set sellado keyed-by-caso en casos y por caso y juez en votos, con 0 celdas fuera del set.
- Candados M68 (`validar_m68.py --baseline`) y M55 al cierre de cada unidad. `validar_m68.py` escribe `output/validacion/m68_violaciones.csv`, que hay que borrar después de correrlo.
- Una unidad por vez, con un resumen corto al terminar cada una.

## Unidades

### U0 — Base

Clon, commit, versión, E0. Grep de las cinco entradas en DEUDA y BITÁCORA (Gate 2).

### U1 — Superficie común y adjudicación

Una sola superficie de firmantes impresos que la tabla no reconoce, sobre el panel publicado de cada fallo. Partí del instrumento de H227 (`u4_abiertos.py`, sección "firmantes impresos no reconocidos", y `u5_n_calificador_heredado.py`), y corregí su límite conocido, 37 paneles no identificables. Clasificá cada pieza en raya en el apellido, apellido-nombre, OCR a distancia 1, fuera de la tabla y ruido de epílogo. Leé todas las piezas que no sean ruido y adjudicá su clase y su efecto en `posiciones`, `n_jueces` y `voting_pattern`.

Corte bloqueante. Tabla de adjudicación al operador y espera de su OK.

### U2 — B195, calificador heredado (código)

El fix candidato está en la DEUDA. Medí si cambia algún fallo fuera de los 3 conocidos. Va primero porque es local a `parse_firma` y no toca la tabla.

### U3 — B194 y B187, patrones de la tabla (dato)

Raya en apellidos compuestos y forma apellido-nombre solo para conjueces. Superficie de radio antes del flip-set. Si los dos tienen radio distinto, van en commits separados.

### U4 — B182 y B185

B182 con un solo caso no justifica una regla tolerante. Proponé si se resuelve con una fila de dato o se deja documentado. B185 es el fix de una línea en `RE_CALIFICADOR_FIRMA`, solo si U3 no lo vuelve innecesario.

### U5 — Cierre

Versión del parser (MINOR si no cambia schema ni vocabulario), CHANGELOG, DEUDA, BITÁCORA y PR. El regolden lo corre el operador en su disco, con `correr_pipeline.py --consciente` y después `--regolden`. Dejale los sha esperados de los cinco CSV y los conteos de filas de los derivados.

## Entregables

Rama con los commits de parser y de dato, PR con el flip-set, los instrumentos en `scripts/diagnostico/H228/` (gitignoreado) entregados como archivos, y la adjudicación con archivo y líneas.
