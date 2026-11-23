# PROMPT_H222 — corpus-csjn, sesión siguiente a H221

Arrancá con el skill `apertura-sesion-corpus` (gates) antes de proponer nada. Repositorio: `guillee1010/corpus-csjn` (público), en la máquina del operador en `C:\Users\guill\Proyectos\corpus-csjn` (Windows / PowerShell). Leé primero, en `DEUDA_TECNICA.md`, el encabezado y las entradas M66, M67, B177, B178, B179, B180 y B019, y en `BITACORA.md` el bloque H221 completo (H221-01 a H221 — Cierre).

## Qué pasó en H221 (resumen)

- Sesión read-only respecto del pipeline: parser v42.1, outputs canónicos y `_manifest.json` intactos desde H220. CHANGELOG sin entrada.
- Fuente nueva: **sjconsulta.csjn.gov.ar** (base de sumarios de la Secretaría de Jurisprudencia de la CSJN), usada como SEGUNDO CODIFICADOR externo (M66). Endpoints JSON no documentados; se baja en la máquina del operador (desde el entorno de Claude el dominio está bloqueado).
- Validación de la variable de votos: 2006-2026, 2480 fallos, 10281 posiciones juez×fallo, acuerdo 98,9%, **κ 0,960 [0,950; 0,969]**, reproducible con `scripts/validacion/kappa_sjconsulta.py` (salidas commiteadas en `output/validacion/`, con manifiesto sha256 del cache). 2016-2026 es censo; 2006-2015, codificación parcial de la Corte.
- Todo desacuerdo adjudicado y tipificado en `output/validacion/adjudicacion_sjconsulta_h221.csv` (98 filas; dice cuáles se leyeron con texto).
- Errores del corpus encontrados: B177 (disidencia parcial publicada como disidencia), B178 ("por su voto" sin normalizar), B179 (posición dejada a salvo DENTRO del voto común, invisible a la firma), B180 (calificador fuera de la línea de firma), B019 (último juez de la firma partido de línea, ahora 9 testigos).
- M67: el corpus llama "mayoria" al voto que encabeza aunque tenga una firma. Medido: 298/5703 fallos con voto de cabeza sin mayoría absoluta (14,1% de los no unánimes); sensible al tamaño del tribunal. Script `scripts/analisis/m67_mayoria_absoluta.py`.
- Secretaría de radicación: viene en sjconsulta, pero solo desde ~2015/2016 (2006-2015 = "MIGRACION"). Hallazgo exploratorio controlado por mérito y tamaño de tribunal: Sec. 6 con tribunal de cinco, 72,4% de fallos con disidencia vs 37,6% (p<0,0001), sobre todo Rosatti (disidencias totales). La fragmentación de la Sec. 4 es Rosenkrantz por su voto. Secretaría sin validar contra el trabajo de campo.
- Capa funcionarial (quién carga cada fallo en la Secretaría de Jurisprudencia): bajada y guardada solo en local, para análisis y anonimizada en toda exposición; no aporta a la pregunta de la tesis y quedó despriorizada.
- En H221 el operador autorizó a Claude a commitear directo en GitHub DEUDA, BITACORA, scripts de `scripts/validacion/` y `scripts/analisis/` y datos curados de `output/validacion/`. El pipeline sigue con el flujo de siempre (Claude no ejecuta en la máquina del operador; ciclo con orquestador y regolden adjudicado).

## Datos locales (no versionados, en la máquina del operador)

`scripts/diagnostico/sjconsulta/`: `sj_AAAAMM_v03.json` (2006-2026, faltan 06/2015 y 05/2023), logs por año, `casos_sjconsulta.csv` (caso × secretaría), `casos_sjconsulta_funcionarial.csv` (solo local). Si hace falta re-bajar: `python scripts\validacion\cruce_sjconsulta.py AAAA` (saltea lo que ya está).

## Opciones para esta sesión (el operador elige; una unidad por vez)

1. **Medir B179 en todo el corpus** (desde el repo, sin la máquina del operador): fórmulas "se remite a su voto", "remiten a sus disidencias", "por mayoría" dentro de `considerando_text`, con lectura de una muestra para medir falsos positivos.
2. **Quién escribe la doctrina en los fallos sin mayoría absoluta**: en los 306 fallos de M67, comparar el texto y la marca de holding de los sumarios de la Secretaría con el voto de cabeza y los demás votos. Antes, verificar en los JSON cómo viene el texto del sumario (atribuciones tipo "(voto de los jueces…)").
3. **Citas posteriores** (`citado_por`): ¿se citan igual los fallos sin mayoría absoluta que los demás?
4. **Concordancia de disposición y vía** con `an_sentido` y `an_tipo_recurso` de SJ, para ver si achica M43 (requiere tabla de equivalencias).
5. **Validar la secretaría** contra el trabajo de campo (cruce secretaría × materia del corpus).
6. Lecturas pendientes: los 3 fallos con marca de disidencia parcial sin disidencia publicada (`output/validacion/superficie_b177.csv`), 332_p1394, 346_p931, 344_p174, 343_p1762.
7. Diseño conjunto del fix de la familia firma (B019, B177, B178, B180) — eventualmente a partir de la auditoría externa (PROMPT_FABLE).

## Recordatorios del operador

- Verificar con datos antes de afirmar; marcar lo reconstruido como tal; citar DEUDA/BITACORA/línea de código.
- Todo número que vaya a la tesis tiene que salir de un script versionado o de una fila de la tabla de adjudicación. Nada de cálculos sueltos sin script.
- Comandos para PowerShell en bloques cortos (los pegados muy largos se cortan en la consola); scripts largos, subirlos al repo y que el operador haga `git pull`.
- Los caracteres no ASCII (º, tildes) se rompen al pasar código por la consola con `| python -`: en esos comandos, evitarlos.
