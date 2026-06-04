# HALLAZGOS — Validación de `materia` (GOLD, codificación ciega)

**Parser:** `derivar_materia.py` v3.2 · **Muestra:** v18.15 · **Coder:** Claude (ciego, misma metodología que M19) · **Sesión:** H117

## Diseño

- **Marco A:** los 300 ids ya anclados en la planilla consolidada M19 (SRS de los fallos → estimador del corpus).
- **Marco B:** oversample por valor de `materia`, `min(20, N_corpus)` anclado en los 300 → +106. **Unión = 406.** `doble_cod = 50`. Seed 20260531.
- **Ceguera:** se codificó leyendo carátula + `considerando_text` + `por_ello_text`. **Se excluyó `tribunal_origen`** del bundle a propósito (es la señal de capa1 → evita circularidad). Se codificó desde la sustancia del litigio.
- **Regla de codificación:** materia solo si el objeto del litigio está en el texto; trámite puro sin objeto → `AMBIGUO` (fuera del denominador). No se infiere materia por tipo de parte. Daños c/ Estado/provincia → `contencioso_administrativo` (responsabilidad estatal).

## Titular

| métrica | valor | IC95 (Wilson) | n |
|---|---|---|---|
| Marco A — cobertura (emite) | 74,1 % | 68,0–79,4 | 166/224 |
| Marco A — exactitud \| emite | 81,3 % | 74,7–86,5 | 135/166 |
| Marco A — exactitud global | 60,3 % | 53,7–66,5 | 135/224 |
| Capa 1 (tribunal→fuero) — exactitud \| emite | 82,5 % | 75,0–88,2 | 104/126 |
| Capa 2 (cascada) — exactitud \| emite | 66,1 % | 57,2–74,0 | 78/118 |

**AMBIGUO:** 104/406 (25,6 %), concentrado en originaria/provincia con considerando de trámite. Útiles: 302.

## Precisión / recall por valor (unión 406, AMBIGUO excluido)

| valor | precisión | recall |
|---|---|---|
| previsional | 95 % (18/19) | 100 % (18/18) |
| salud | 95 % (19/20) | 63 % (19/30) |
| penal | 94 % (29/31) | 50 % (29/58) |
| laboral | 89 % (16/18) | 84 % (16/19) |
| tributario | 87 % (13/15) | 62 % (13/21) |
| electoral | 80 % (12/15) | 86 % (12/14) |
| civil_comercial | 71 % (30/42) | 62 % (30/48) |
| contencioso_administrativo | 68 % (27/40) | 42 % (27/65) |
| ambiental | 65 % (11/17) | 85 % (11/13) |
| consumo | 33 % (5/15) | 83 % (5/6) |
| lesa_humanidad | 33 % (1/3) | 50 % (1/2) |
| cambiario | 25 % (1/4) | 100 % (1/1) |
| constitucional | 0 % (0/5) | 0 % (0/7) |

## Hallazgos (candidatos a frente, NO se tocó el pipeline)

- **H1 — silver del held-out confirmado.** CA precisión gold 68 % ≈ 68,8 % silver (H116). El gold valida el held-out en su valor más incierto.
- **H2 — `constitucional` roto como valor plano (0/0).** Parser=constitucional → cod tributario (3, patrón acción declarativa de inconstitucionalidad s/ impuesto provincial) y CA (2). Cod=constitucional → parser CA (4)/electoral (2)/lesa (1). Categoría transversal; no funciona plana.
- **H3 — `consumo` sobre-dispara (precisión 33 %).** capa2: consumo→civil_comercial ×6, consumo→CA ×4. Recall alto (83 %) pero muchos FP.
- **H4 — `cambiario` (25 %) y `lesa_humanidad` (33 %) sobre-aplicados** (n chico, revisar reglas/normas gatillo).
- **H5 — frontera ambiental/penal en ley 24.051.** 5 casos: parser ambiental por la norma; cod penal por competencia criminal. Desacuerdo legítimo.
- **H6 — recall CA bajo (42 %) por abstención.** 10 originaria + 11 pendiente_capa2 codificados CA con parser vacío. La capa originaria y la cola de pendiente_capa2 esconden CA.
- **H7 — capa 2 es el frente débil** (66 % vs 82,5 % capa1).

## Productos

- `muestra_clave_materia_v18.15.csv` — clave (parser_materia, materia_capa, materia_fuente, marco, doble_cod).
- `planilla_codificacion_materia_v18.15_CODIFICADA.csv` — planilla ciega + `cod_materia`.
- `cod_claude.csv` — códigos crudos.
- `METRICAS_materia_v18.15.txt` — salida completa (incluye matriz de desacuerdos y capa perdida).
- `muestrear_materia.py` — sampler (candidato a mergear como modo materia de `muestrear_validacion.py` → v1.2).

## Pendiente

- **Test-retest Claude-vs-Claude** sobre los 50 `doble_cod` (ventana fresca) → confiabilidad intra-coder.
- **Anclaje humano opcional:** Guillermo codifica los 50 `doble_cod` → primer kappa humano del programa.
- Reducir AMBIGUO en originaria/provincia leyendo considerando completo vía `extraer_caso` (si se quiere subir n útil).
