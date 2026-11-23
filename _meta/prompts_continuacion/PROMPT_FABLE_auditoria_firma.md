# Auditoría de solo lectura — familia de la firma del parser de corpus-csjn

Sos un auditor externo e independiente. No conocés la historia de las sesiones y no la necesitás: trabajás con el código y la documentación del repositorio. **No modifiques nada. No hagas commits, ni ramas, ni pull requests.** El resultado es un informe.

## Contexto mínimo

- Repositorio: `guillee1010/corpus-csjn` (GitHub, público). Pipeline que convierte los tomos de Fallos de la Corte Suprema argentina (tomos 329-349, sin 335 y 336) en datos estructurados. El parser es `scripts/pipeline/parser.py` (v42.1).
- La variable de votos (posición de cada juez en cada fallo, columna `posiciones` de `output/parser/csjn_casos.csv` y filas de `output/parser/csjn_casos_votos.csv`) se validó contra un registro externo de la propia Corte: 10281 posiciones, acuerdo 98,9%, κ 0,960. Casi todo el desacuerdo restante viene de errores del parser concentrados en la lectura de la firma del fallo.
- Esos errores están documentados en `DEUDA_TECNICA.md` como B019, B177, B178, B180 y, relacionado, B179. Los casos concretos están en `output/validacion/adjudicacion_sjconsulta_h221.csv` (columna `clase`, con número de línea del corpus en `evidencia`). El texto de cada tomo está en `corpus/LibroVol*.md`; las líneas de cada caso, en `linea_inicio`/`linea_fin_real` de `csjn_casos.csv`.

## Qué leer

1. En `DEUDA_TECNICA.md`: las entradas `### B019`, `### B177`, `### B178`, `### B179`, `### B180`, y para contexto `### B168` y la familia B166 (buscar "B166").
2. En `scripts/pipeline/parser.py`: `parse_firma`, `RE_CALIFICADOR_FIRMA` y regex vecinas, `collect_firma_lines`, la lógica que fija `linea_fin_real`, `RE_VOTO_HDR` / `RE_DISID_HDR` y cómo se combinan firma y headers para producir `posiciones`.
3. Los casos testigo de cada clase en la tabla de adjudicación, leyendo el bloque del corpus (podés usar `scripts/diagnostico/extraer_caso.py <caso_id>` si lo corrés localmente, o abrir el `.md` en el rango de líneas).

## Preguntas que tiene que responder el informe

1. **Causa exacta de cada bug** (B019, B177, B178, B180), con la línea o función del código donde ocurre y por qué, verificada contra al menos dos casos testigo.
2. **¿Comparten causa o mecanismo?** En particular: ¿B019 y la variante (a) de B180 son el mismo problema (firma o calificador partido después de `linea_fin_real`)?
3. **Diseño de un arreglo conjunto** que corrija la mayor cantidad de clases con el menor cambio, sin romper casos que hoy andan. Para cada cambio propuesto: qué casos testigo debería mover y en qué dirección, qué otros consumidores del código toca (la DEUDA menciona varios consumidores de las regex de header) y qué riesgo de regresión tiene.
4. **B177**: ¿alcanza con dejar de descartar el grupo "parcial" del calificador, o la categoría nueva rompe consumidores (`voting_pattern`, `n_disidencias`, `clasificar_tipo_voto`, `fragmenta_ratio`)? Listá cada consumidor afectado.
5. **B179** no es un bug de lectura de la firma sino de diseño (la posición está dentro del texto del voto común). Decí si es detectable con reglas confiables o si conviene tratarlo como marca aparte, y qué falsos positivos esperás.
6. Cualquier otro problema de la misma familia que veas en el código y no esté documentado.

## Formato del informe

- En castellano rioplatense, técnico y directo. Sin dos puntos para unir oraciones.
- Una sección por pregunta. Cada afirmación sobre el código, con archivo y función o número de línea. Cada afirmación sobre el comportamiento, con al menos un `caso_id` verificado.
- Separá con claridad lo **verificado** (leíste el código y el caso) de lo **inferido** (hipótesis sin verificar).
- Al final, una lista priorizada de cambios propuestos, cada uno con su lista de casos testigo esperados (el "flip-set" previsto), lista para una prueba A/B en otra sesión.
- No propongas tocar el `golden`, el `manifest` ni los outputs canónicos: eso se hace después, en el ciclo del proyecto.
