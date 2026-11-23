# Hx-4 — B179, marca `posicion_en_texto` para posiciones expresadas dentro del voto común

Cuarta sesión de la serie Hx de la familia de la firma. El número H es el siguiente al último de la BITÁCORA. Abrí con `apertura-sesion-corpus` y cerrá con `cierre-sesion-corpus`.

## Prerrequisito (bloqueante)

Tiene que existir la adjudicación de B179, hecha en H223 (unidad opcional) o en H224 (U3). Buscala en la BITÁCORA y usá ese CSV como gold. Si no existe, pará. Esta sesión implementa, no adjudica de cero.

## Qué leer antes de proponer (Gate 2)

En la DEUDA, `### B179` completo, `### B171` (remisión al dictamen, otra cosa, mismas fórmulas cercanas) y `### M67`.

## U0 — Decisión del operador (bloqueante)

La propuesta de H222 es una columna nueva y no recodificar `posiciones`, para no cambiar la definición validada contra SJ. Proponé y esperá la confirmación de estos puntos.

- Columna `posicion_en_texto` en `csjn_casos_votos.csv`, con los valores `remite_voto`, `remite_disidencia` y `mayoria_declarada`, vacía por defecto.
- Columna de caso `n_posiciones_en_texto` en `csjn_casos.csv`, si o no.

## U1 — Reglas y precisión

Reglas a partir de las fórmulas adjudicadas. Nombre de juez de la firma, más "se remite" o "se remiten", más "su voto", "sus votos", "su disidencia" o "sus disidencias", dentro de zona cuerpo o dispositivo. "Por mayoría" anclado en `por_ello_text`. Medí precisión y recall contra el gold. El FP sellado es 342_p287 y no puede marcarse.

## U2 — Implementación y ciclo

Detector en el parser con fuente única de zonas. PoC A/B con candado E0 en todas las columnas viejas (tienen que quedar byte-idénticas). La columna nueva se adjudica contra el gold. Ciclo MAJOR por schema, con CODEBOOK.
