# Changelog

Registro de cambios del proyecto corpus-csjn: parser, auditor, cruzador y documentación.

### 2026-05-18 — H036: Backstop dictamen con RE_APERTURA

**Fix:** en el loop de detección de dictamen de `procesar_archivo`, si
`en_dictamen=True` y la línea matchea `RE_APERTURA` ("FALLO/SENTENCIA
DE LA CORTE SUPREMA"), cerrar el dictamen sin consumir la línea. Evita
que dictámenes largos (donde `len(prev) >= 80` impide el cierre por
fecha) consuman el cuerpo del fallo, el dispositivo y la firma.

**Impacto:** 31 casos recuperados (sin_firma 813 → 782). 0 regresiones.
6 cambios neutros (5 B059 expuestos + 1 corrección de dispositivo).
Cobertura firma: 85.7% → 86.3%.

**Líneas modificadas:** `parser.py`, bloque `elif en_dictamen:` (~línea
1601). 7 líneas de código agregadas.

### Fix B013 — Búsqueda anclada de dispositivo (2026-05-18, H035)

- Detección de dispositivo movida fuera del loop principal a pasada
  separada con cascada: apertura_rel → dictamen_end+1 → 0.
- Techo en inicio_votos_indiv solo cuando votos son post-apertura.
- 302 casos con dispositivo prematuro resueltos.
- n_jueces=1 baja de 114 a 21; n_jueces 5-7 sube +162 casos.

---
## 2026-05-17 — visor_auditoria.py + auditar_fallo v1.0.0
- `scripts/visor/visor_auditoria.py`: nuevo script de visualización
  compacta de outputs de `auditar_fallo.py`. Agrupa spans por tipo,
  silencia headers embebidos y `catch_all_inicio` por posición.
  Opciones completas: `--solo`, `--excluir`, `--incluir`, `--tomo`,
  `--pagina`, `--con-alertas`, `--formato` (md/txt/csv), `--preview`,
  `--resumen`, `--stats`, `--stdout`, `--output`.
  Output default: `output/visor/<nombre>_vista.md`.
- `scripts/auditoria/auditar_fallo.py`: `__version__ = "1.0.0"`.
  Encabezado MD ahora incluye `Versión` y `Seed` (cuando aplica).
- `.gitignore`: agrega `archivo/auditoria/` y `output/visor/`.
- Reorganización: outputs viejos de `output/auditoria/auditar_fallo/`
  movidos a `archivo/auditoria/auditar_fallo/`.
---

## 2026-05-16 — Fix B049 Var-A: concatenar carátula partida en `detectar_caratula` (H028)

Fix en `scripts/auditoria/auditar_fallo.py`. `detectar_caratula` retrocedía
una sola línea desde el primer header de sumario; en casos de carátula partida
por salto de página devolvía solo la segunda mitad. Fix en Estrategia 1 y
Estrategia 2: si la candidata no tiene `c/`, `s/` ni `|` y no termina en
punto, busca la línea anterior y concatena con manejo de silabación. Guardia:
la línea anterior no debe ser mes calendario solo, no debe empezar con `V.`,
no debe terminar en punto ni empezar en minúscula. Validado con seed 15052026,
n=80: 7 mejoras, 0 regresiones. Var-B (340_p1551) pendiente. No afecta corpus
productivo. Detalle en BITACORA H028.

## 2026-05-16 — Documentación H027: refinamiento post-Fase A continuación

Tres commits de documentación:
- `GRAMATICA_DEL_FALLO.md`: refinamiento post-Fase A continuación (paralelo
  borde superior ↔ epílogo, HN3 → HN3').
- `BITACORA.md`: append H027 — lectura completa del auditor + mapeo
  producción × auditor (Fase B).
- `DEUDA_TECNICA.md`: B049 mecanismo refinado, B050/B051 nuevos, M07/M08
  nuevos, conteos del resumen ejecutivo actualizados.

## 2026-05-16 — Documentación H025: reflexión arquitectónica + revert

Commits de documentación sobre páginas compartidas y `detectar_fin_real`:
- `GRAMATICA_DEL_FALLO.md`: propuesta arquitectónica de parser por gramática
  del fallo + diálogo entre vecinos.
- `BITACORA.md`: H025 — reflexión arquitectónica, dos manifestaciones de B045.
- `DEUDA_TECNICA.md`: B045 refinado con manifestaciones A/B, B046 nuevo,
  B018 nota, M01 ampliada.
- `PIPELINE.md`: H025 — 4 fricciones nuevas/ampliadas.
- Intento fallido de verificación empírica B046 en 346_p1205 (commiteado,
  revertido y documentado honestamente al cierre).

---

## 2026-05-15 — Documentación H022-H024: verificación mecanismos B022/B025/B044/B045

Commits de documentación sobre verificación de bugs contra `.md` crudo:
- `DEUDA_TECNICA.md`: B045 nuevo (causa raíz arquitectónica), B044 nuevo,
  B022 y B025 con estado `confirmado_mecanismo`. B018 causa raíz refinada,
  B022 variante 2, B043 nuevo.
- `BITACORA.md`: H022 spot-check 7 testigos + H023 verificación contra
  `parser.py` (M3 refutado, M2 confirmado) + H024 verificación M5/M4/M1
  + 346_p1205, hallazgo arquitectónico B045.

## 2026-05-15 — feat(auditoria): --seed y wrapper tabular para auditar_fallo

- `feat`: agregar `--seed` a `auditar_fallo.py` para muestreo reproducible.
- `feat`: wrapper `tabular_senales_lote` para análisis en lote.
- `docs`: H021 — infraestructura auditoría persistencia. H020 — flag M05 +
  plan auditoría. `DEUDA_TECNICA.md`: reescritura canónica B001-B042 + M01-M08.

---

## 2026-05-14 — Inventario y limpieza del repositorio (Fase 1 y 2)

Reorganización documental en varias fases:
- Rescate de análisis a rama viva, archivado de scripts históricos.
- READMEs de `scripts/` y subdirectorios.
- Deduplicación de entradas en BITACORA.
- Untrack de prompts de continuación (scaffolding personal, no producto).
- Rediagnóstico §4.6.b contra CSV vivo; descarte de herramienta paralela
  (`auditoria_4_6_b_prefix.py` archivado, `diagnostico_4_6_b_cluster.py`
  eliminado). Convención: `scripts/diagnostico/` para diagnósticos
  cuantitativos sobre CSVs; diagnóstico fino del corpus vía
  `scripts/auditoria/auditar_fallo.py`.

---

## 2026-05-09 — fix(parser) + fix(cruzador): RE_APERTURA y bug pg_fin+1

Dos fixes con impacto en corpus productivo:
- `fix(cruzador)`: resuelto bug `pg_fin+1` (§3.6.a) en
  `cruzar_catalogo_y_mapa.py`. Output regenerado.
- `fix(parser)`: `RE_APERTURA` tolerante a doble espacio + hallazgo hojas
  complementarias tomos 331-334.
- `fix(cruzador)`: §3.6.e Fase 1 — resolver `pagina_fin_no_en_mapa` por
  hojas complementarias.
- Docs: PIPELINE cerrado §3 y §4; HALLAZGOS reorganizado.
- BITACORA: sesiones 2026-05-09 nocturna (validación H018 random-80 + F012)
  y 2026-05-10 (refinación de hallazgos).

## 2026-05-08 — feat(auditoria): auditar_fallo.py v1

- `auditar_fallo.py` v1: módulo de auditoría manual del corpus CSJN.
- Fix paths default + corrida random 50. F007 nuevo. Estrategia
  auditor→parser (H015).
- Docs: H014/H015, H016 (punto ciego del auditor), H017 (diseño detector
  amputación inferior), H018 (diseño detector borde inferior, implementación
  pospuesta, F010/F011 nuevos).

---

## 2026-05-03 — Fix 1: V1 como fuente primaria de `case_name_cuerpo`

- Cobertura `case_name_cuerpo` sube de 48.3 % a 84.1 %, 0 regresiones.
- Fix 1 commiteado en CSV productivo. Snapshots movidos a
  `archivo/snapshots_ad_hoc/`. Detalle en
  `docs/analisis_forense_pipeline.md` §XX-XXI.

---

## 2026-05-02 — Reorganización estructural del proyecto + re-corrida pipeline

- Reorganización estructural de directorios.
- Re-corrida pipeline post-migración: 5.819 fallos, 21.876 votos
  (genera `csjn_casos_votos.csv`). Validación funcional OK.
- `.gitattributes`: forzar LF en `.py/.md/.csv/.txt`, CRLF en `.ps1`.
- Actualización de paths en `scripts/pipeline/` (15 reemplazos, sin
  cambios de lógica de runtime).

---

## 2026-05-01 — v17 beta (descartada) + fix catálogo

- `construir_catalogo_v15.py`: fix detección inicio de índice de nombres
  en tomos modernos.
- v17 beta v1 conservado; v17 beta v2 descartada (rollback protocol
  documentado en CHANGELOG anterior). Scripts diagnósticos movidos a
  `scripts/diagnosticos/`.

---

## 2026-04-30 — v16 fix1 + merge v17 + outputs pipeline

- Fix 1 en `construir_catalogo.py` (sacar `-1` en línea 341): resuelve
  página compartida. Output: `csjn_casos_v16_fix1.csv` con 175 mejoras
  `sin_firma→firma`.
- Merge branch `v17`.
- Changelog reconstruido v1-v17 (`docs/changelog_parser.md`).

---

## Versiones anteriores del parser (v10-v16)

Ver `docs/changelog_parser.md` y historial de git (`git log --oneline`).
