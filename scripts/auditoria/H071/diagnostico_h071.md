# H071 — Diagnóstico barrido de monstruos

Sesión: 2026-05-25
Corpus: 5667 fallos, 35 sumario_editorial, 160 sumario_con_link
Inspeccionados en .md: 74 casos (monstruos_h071.md v1 + v2)

---

## Patrón 1: wcC incluye residuo — BUG confirmado (25/25 inspeccionados)

**Casos:** 161 con wcC > wcM total (72 sin dictamen, 89 con).
Subgrupo inspeccionado: 25 con wcC > 3x wcM y sin dictamen.

**Mecanismo:** `extraer_considerando()` (parser.py L703) excluye
`lineas_dictamen` pero NO excluye `lineas_residuo`. `wc_mayoria`
(L2554) sí excluye ambos. Resultado: considerando_text captura
texto del residuo (sumarios, dictámenes PGN, headers editoriales).

**Confirmación:** 25/25 casos tienen texto significativo (46-411 líneas)
antes de "FALLO DE LA CORTE SUPREMA". 3 casos ni siquiera tienen
header de fallo (332_p737, 334_p1659, 347_p1084).

**Fix:** parser.py L2514:
```python
# Actual:
_lineas_no_cons = set(lineas_dictamen)
# Propuesto:
_lineas_no_cons = set(lineas_dictamen) | lineas_residuo
```

**Impacto downstream:** classify_outcome() usa considerando_text para
detectar inadmisible_280 y acordada_4. Texto espurio contamina.

---

## Patrón 2: wcM ≤ 4 — confirmado 26/26

**Tomos:** 329 (12), 330 (7), 331 (2), 332 (2), 333 (2), 334 (1).

**Mecanismo:** Fallos donde todos los jueces votan individualmente.
26/26 empiezan con "VOTO DE..." o "DISIDENCIA DE..." en las primeras
líneas. El parser manda todo a wc_votos, wcM queda en 1-4 palabras.

**Subgrupo accionable:** 4 clasificados unanime que deberían ser
segun_su_voto: 329_p2218, 329_p2433, 329_p2680, 329_p6032.
Los otros 22 ya tienen vp correcto.

---

## Patrón 3: Monstruos — 3 casos individuales

### 330_p2849 (wc=110236, 13228 líneas)
linea_fin_real se extiende hasta el índice editorial del tomo
(INDICE DE LEGISLACION, DICTAMENES, etc.). Parser no encontró
el siguiente caso. Caso real: Estado Nacional c/ Buenos Aires.

### 333_p1474 (wcD=56173, wc=1249)
Caso Rachid (matrimonio igualitario). Dictamen PGN legítimamente
enorme (~130 páginas derecho comparado). case_name_cuerpo = NaN.
No es bug de detección — el dictamen realmente es así.

### 342_p1827 (wcD=7072, wc=442)
R., C. E. — violencia de género/legítima defensa. Dictamen largo,
resolución corta. Mismo mecanismo que 333_p1474.

---

## Patrón 4: sin_dispositivo + firma — 37 casos, 3 sub-mecanismos

10 inspeccionados en .md, 27 restantes diagnosticados por CSV.

### 4a. "Por ello" genuino perdido (1 caso confirmado)
337_p166 (Monner Sans c/ Consejo Magistratura). Tiene "Por ello" +
firma 7 jueces, pero después hay votos concurrentes (Zaffaroni,
Argibay). buscar_firma_inversa captura firma solo de Argibay al
final de su voto. Resultado: n_jueces=1, firma=Argibay, sin_disp.
Diagnóstico: por_ello_idx no fue detectado pese a existir.

### 4b. "por ello" mid-sentence, correctamente ignorado (3 casos)
340_p812 (en dictamen PGN), 344_p2123 (mid-reasoning),
348_p443 (mid-reasoning con "En virtud de lo expuesto" como
fórmula dispositiva real).

### 4c. Variantes de fórmula (33 casos = 6 inspeccionados + 27 restantes)
Los 27 restantes tienen por_ello_text vacío — ninguno tiene "Por ello".
Todos tienen firma real (n_jueces 1-7). Son autos, interlocutorios,
o resoluciones con fórmulas alternativas:
- "lo que así se resuelve" (329_p317, 331_p548)
- "Hágase saber" (330_p2794)
- "En virtud de lo expuesto, se rechaza..." (348_p443)
- "Notifíquese" como única fórmula (330_p1642, 342_p98)
- "Se declara..." (341_p739, 344_p2779)

Los 27 no inspeccionados probablemente caen en las mismas variantes.
wc mediana=657, rango 323-1834. Distribución: 329(4), 330(4), 331(2),
332(1), 333(2), 334(3), 337(1), 339(2), 340(1), 343(2), 344(3),
346(1), 348(1).

---

## Patrón 5: wcD >> wcM ratio > 20 — NO es patrón separado

10 inspeccionados. Mismo mecanismo que Patrón 2 (wcM≤4): fallos
con votos individuales dominando + dictamen grande. No agrega bug.

---

## Grupos pendientes de inspección

### wc_votos=0 + vp no unánime (37 casos)
Parser detecta posiciones en firma (disidencia en firma) pero no
separa bloques de texto. Todos los votos quedan en wc_mayoria.
NO inspeccionados en .md. Diagnóstico preliminar: limitación
editorial (no hay headers "VOTO DE" / "DISIDENCIA" en el cuerpo).

### n_jueces=1 (30 casos)
Autos de presidencia, votos individuales (Argibay, Maqueda, etc.).
NO inspeccionados en .md. Clasificados unanime (correcto formal).

### sin_dispositivo + firma restantes (27 casos)
Diagnosticados por CSV. Todos por_ello_text vacío. Probables
variantes de fórmula (sub-mecanismo 4c). Inspección .md opcional.

---

## Priorización de fixes

| # | Patrón | Casos | Esfuerzo | Impacto |
|---|--------|-------|----------|---------|
| 1 | wcC incluye residuo | 72-161 | Bajo (1 línea) | Alto (outcome) |
| 2 | 337_p166 por_ello perdido | 1+ | Medio | Medio |
| 3 | Fórmulas alternativas | ~33 | Medio | Medio (sin_disp FP) |
| 4 | wcM≤4 unanime→svoto | 4 | Medio | Bajo |
| 5 | 330_p2849 fin desbordado | 1 | Alto | Bajo |

---

## Archivos de soporte

- output/diagnostico/monstruos_h071.md (16 casos, extracto v1)
- output/diagnostico/monstruos_h071_v2.md (74 casos, extracto v2)
- output/diagnostico/diagnostico_h071.md (este archivo)
- scripts/auditoria/H071/extraer_monstruos.py (generador)
