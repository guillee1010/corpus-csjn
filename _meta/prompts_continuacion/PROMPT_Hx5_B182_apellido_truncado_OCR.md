# Hx-5 — B182, apellidos de juez truncados por OCR en la firma

Quinta sesión de la serie Hx de la familia de la firma. El número H es el siguiente al último de la BITÁCORA. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`. Es una sesión de superficie. Si la clase resulta chica, se cierra documentada y sin fix.

## Qué leer antes de proponer (Gate 2)

En la DEUDA, `### B182`, `### B019` (por qué no se ensanchan los patrones de `jueces_csjn.csv`) y `### B169` (ruido de nombres en prosa).

## U1 — Superficie

Sobre `firma_raw` de `csjn_casos_textos.csv`, tokens a distancia de edición 1 (o con una letra final perdida) de los apellidos de `_RE_FIRMA_COMPLETA` que no matcheen `JUECES_CONOCIDOS`. Testigo 343_p1762 ("Ricardo Luis Lorenzett."). Cruzá cada candidato con el texto del tomo. Cuando haya SJ para el año, cruzá con la adjudicación de M66 para ver si el juez falta en `posiciones`.

## U2 — Decisión

Con la cardinalidad a la vista, el operador decide entre tres opciones.

1. Cerrar documentado.
2. Un patrón tolerante solo para los casos medidos, en `jueces_csjn.csv`, con superficie corpus-wide del patrón nuevo antes de aplicarlo.
3. Una corrección puntual del insumo OCR, si el proyecto tiene mecanismo para eso.

No implementes antes de esa decisión.

## Nota

B183 (fragmento de calificador a inicio de línea) no tiene prompt propio. Se trabaja junto con M57, cuando se aborde el consumidor de bordes de zona firma.
