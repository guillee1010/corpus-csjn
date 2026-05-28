# Prompt de continuación — Sesión inventario de scripts y archivos

> Guardar en `_meta/prompts_continuacion/prompt_inventario_2026-05-XX.md`
> y pegar al inicio de la próxima sesión.

---

## Objetivo de la sesión

Inventario sistemático del proyecto `corpus-csjn` con el propósito de:
1. Limpiar zonas olvidadas (raíz, `bak/`, duplicados sospechosos).
2. Decidir qué hacer con snapshots completos y carpetas paralelas
   pre-reorganización.
3. Documentar las carpetas en `archivo/exploratorios/diagnostico/`
   con README de cierre por cada bug auditado.
4. Reordenar `scripts/diagnostico/` separando vivos de archivables.

**Plan acordado: Fases 1 → 2 → 3 → 4 en ese orden.** Pueden no entrar
en una sola sesión; partimos donde haga falta.

---

## Estado del proyecto al cierre de sesión 2026-05-14

### Último commit

```
72f6a0b (HEAD -> main) docs: rediagnóstico §4.6.b contra CSV vivo, descarte herramienta paralela
```

Cuatro archivos modificados: BITACORA.md (+70), CHANGELOG.md (+13),
PIPELINE.md (+60/-16), PIPELINE_HALLAZGOS.md (+244). Sin cambios al
parser ni a CSVs.

### Backup defensivo de la sesión anterior

`bak/sesion_20260514_2012/` contiene los cuatro archivos pre-edición
(BITACORA, CHANGELOG, PIPELINE_HALLAZGOS, PIPELINE). Recuperable en
cualquier momento.

### Estado §4.6.b al inicio del inventario

- `parser.py:121` `RE_CONSIDERANDO` intacto: `r"^Considerando\s*[:.]?\s*$"`.
- CSVs vivos sin regenerar.
- Cluster vivo: 320 sospechosos / 232 con apertura / 88 sin apertura
  / 1.672 vacíos.
- Sin fix aplicado. Detalle en BITACORA H019.

### Herramientas canónicas vigentes

- `scripts/auditoria/auditar_fallo.py` — diagnóstico fino del cuerpo
  del corpus (importa regex de `parser.py`).
- `scripts/pipeline/` — pipeline productivo (parser, catalogo,
  cruzador, detectar_paginas).
- Convención reafirmada (BITACORA H015): cualquier diagnóstico fino
  va via `auditar_fallo.py`, no scripts ad-hoc paralelos.

---

## Radiografía del proyecto por zonas

### 🟢 ZONA VIVA — productiva, no tocar mucho

```
corpus/                              46 .md (fallos), input crudo
scripts/pipeline/                    4 scripts canónicos
scripts/auditoria/                   2 scripts (auditar_fallo.py + medir_voto_hdr.py)
scripts/diagnostico/                 16 scripts vivos (foco Fase 4)
scripts/auxiliares/                  3 scripts
scripts/tests/                       4 tests
scripts/migraciones/                 vacío de .py, solo "otros" — inspeccionar
output/                              CSVs y mapas vivos
output/auditoria/auditar_fallo/      12 .md de reportes — revisar conservación
```

### 🟡 ZONA ARCHIVO — `archivo/exploratorios/diagnostico/`

Solo `4_6_b/` tiene README. El resto **no cumple** el patrón tríada
(prefix + postfix + salida + README). 10 carpetas:

```
4_6_b/                    ✅ Bug abierto, estructura correcta, 3 py + 1 md
auditar_autosyvistos/     ⚠ 1 py sin README ni postfix ni salida
auditar_casos_sin_voces/  ⚠ 1 py sin README
auditoria_pipeline/       ⚠ Sin scripts, solo "otros" (1)
bug_cruzador_pgfin/       ⚠ Solo 2 logs txt sin script
case_name_mismatc/        🔴 Carpeta typo (falta "h" final), 1 py
case_name_mismatch/       ⚠ 10 py + 1 csv + 2 txt + ~140 bloques sin README
casos_sin_voces/          ⚠ 3 py + 2 md + 4 csv — superposición sospechosa
                            con las dos "auditar_*" anteriores
fix1_validacion/          ⚠ 1 py (bug ya cerrado, CHANGELOG v16 fix1)
regresion_v16_v17/        ⚠ 1 py
```

### 🟠 ZONA DUPLICADA Y CONFUSA

```
archivo/scripts/analisis/, auxiliares/, parsers/    Estructura paralela pre-reorg 2/5
archivo/snapshots_ad_hoc/pre_fix_xii_20260503_1308/ Snapshot completo del repo pre-reorg
archivo/snapshots_ad_hoc/ (6 carpetas de fixes)     Snapshots de fixes individuales — están bien
snapshots/snapshot_2026-05-02_1559/                 OTRO snapshot completo del repo, mismo día
snapshots/snapshot_pre_reorg_2026-05-02_1843/       OTRO snapshot completo del repo, 3 hs después
                                                     14 py + 46 md + 6 csv + carpetas internas
```

Tres snapshots completos del repo en total. Hay que decidir cuántos
conservar.

### 🔴 ZONA OLVIDADA Y SOSPECHOSA

```
bak/                                  23 .md viejos en raíz, PIPELINE versionado 7×, idem HALLAZGOS
bak/limpieza_20260509_011259/         7 .md, sub-cementerio dentro del cementerio
bak/sesion_20260514_2012/             4 .md backup de hoy — ese sí está bien
validacion/pre/                       8 csv + 3 txt, huérfana, no mencionada en docs
logs/                                 2 archivos "otros", sin md/py/csv/txt
tests/ (en raíz, con __pycache__)     ¿Duplica scripts/tests/?
_meta/prompts_continuacion/           1 .md (prompts viejos de sesión)
prompts/                              1 .md (también prompts)
```

### Archivos sueltos en raíz al cierre

```
.env, .gitattributes, .gitignore
aplicar_ediciones_pipeline.ps1        Script de sesión 14/5, sin git tracking
BITACORA.md, CHANGELOG.md             Documentación viva, commiteados
PIPELINE.md, PIPELINE_HALLAZGOS.md    Documentación viva, commiteados
DEUDA_TECNICA.md                      Sin actualizar desde 2/5
README.md                             Sin actualizar desde 2/5
diff_3_6_e.txt, diff_4_6_b.txt (vacío), diff_docs.txt
                                      Outputs sueltos de comparaciones del 9/5
prompt_continuacion_2026-05-XX_regeneracion_1-5-6.md
                                      Prompt suelto en raíz desde 9/5
```

---

## Plan de 4 fases

### Fase 1 — Zona OLVIDADA (~30-40 min)

**Mayor ROI primero, más sucio y más rápido.**

1. **Raíz del repo**: decidir destino de:
   - `diff_3_6_e.txt`, `diff_4_6_b.txt` (vacío), `diff_docs.txt` → mover
     a snapshot correspondiente o eliminar.
   - `prompt_continuacion_2026-05-XX_regeneracion_1-5-6.md` → mover a
     `_meta/prompts_continuacion/`.
   - `aplicar_ediciones_pipeline.ps1` → decidir si gitignorear,
     archivar o commitear.

2. **`bak/`**: criterio claro:
   - `PIPELINE.md` está versionado 7 veces con timestamps. Conservar
     solo el último de cada serie (o ninguno, dado que git ya tiene
     historial).
   - `bak/limpieza_20260509_011259/` → revisar si tiene contenido
     distinto a lo que ya está en git, si no eliminar.
   - `bak/sesion_20260514_2012/` → conservar.

3. **`tests/` (en raíz) vs `scripts/tests/`**: investigar duplicación.

4. **`validacion/pre/`** y **`logs/`**: averiguar qué son y de qué
   sesión vienen. Probablemente outputs huérfanos.

5. **`_meta/`** vs **`prompts/`** en raíz: dos carpetas con prompts.
   Consolidar en una.

**Output:** commit por fase con mensaje claro.

### Fase 2 — Zona DUPLICADA (~30 min)

1. **Tres snapshots completos del repo**:
   - `snapshots/snapshot_2026-05-02_1559/`
   - `snapshots/snapshot_pre_reorg_2026-05-02_1843/`
   - `archivo/snapshots_ad_hoc/pre_fix_xii_20260503_1308/`
   Decidir cuántos vale conservar. El 1559 y el 1843 son del mismo día
   con 3 horas de diferencia — probable que uno sea subset del otro.
   git ya tiene historial completo.

2. **`archivo/scripts/`** (estructura paralela pre-reorg): verificar
   que no haya nada que se haya perdido en la migración.

3. **Los 6 snapshots de fixes individuales** en
   `archivo/snapshots_ad_hoc/`: dejar como están, son chicos y útiles.

### Fase 3 — Zona ARCHIVO/EXPLORATORIOS (~1-1.5 h)

Las 10 carpetas de `archivo/exploratorios/diagnostico/`. Para cada
una:
1. Identificar el bug que auditaba (cross-ref con PIPELINE.md).
2. Verificar si el bug está cerrado.
3. Agregar README de cierre (qué bug, cómo se resolvió, números
   pre/post).
4. Identificar heurísticas migrables (flagged como F### para sesión
   futura de migración).

**Casos especiales a resolver en esta fase:**
- `case_name_mismatc/` (typo) vs `case_name_mismatch/` → fusión.
- `auditar_autosyvistos/`, `auditar_casos_sin_voces/`,
  `casos_sin_voces/` → tres carpetas con nombres similares.
  Entender la superposición.

### Fase 4 — Zona VIVA, `scripts/diagnostico/` (~45 min)

Con el contexto de qué bugs están cerrados (Fase 3 hecha), revisar
los 16 scripts vivos:

```
diagnostico_fin_fallo.py              (23 KB, 29/4) — cluster fin de fallo
diag_sin_firma.py                     (5 KB, 29/4)  — cluster v16 → v17 firma
diag_sin_firma_ascii.py               (5 KB, 29/4)  — variante ASCII
diag-dictamen.py                      (5 KB, 29/4)  — diagnóstico dictamen
diag_sumario_link.py                  (5 KB, 30/4)  — detector sumario-con-link
verificacion_pre_v17.py               (3 KB, 30/4)
verificacion_2_v17.py                 (3 KB, 30/4)
clasificacion_matches_solapamiento.py (7 KB, 30/4)
explorar_firmas_procurador.py         (2 KB, 30/4)
buscar_firmas_corpus.py               (4 KB, 1/5)
validar_v17_beta_v2.py                (2 KB, 1/5)
_inspeccionar.py                      (200 B, 1/5)  — utility
cortar_lotes_349.py                   (5 KB, 2/5)   — específico tomo 349
test_gemini_un_fallo.py               (5 KB, 2/5)   — benchmark Gemini
auditoria_conteos.py                  (4 KB, 2/5)
identificar_perdidas_331_334.py       (4 KB, 2/5)   — bug §3.6.c
+ benchmark_gemini/ (6 md + 1 csv)
```

Decisiones por script:
- Si auditaba bug **cerrado** (sumario_con_link, sin_firma, dictamen
  v16→v17) → mover a `archivo/exploratorios/diagnostico/<bug>/` con
  README.
- Si auditaba bug **abierto** → queda en `scripts/diagnostico/`.
- Si es **utility puntual** → caso por caso.

---

## Pendientes técnicos (NO son trabajo de esta sesión)

Anotados para que Claude no se distraiga sugiriendo fixes durante el
inventario:

- §4.6.b sin fix. Próximo paso: sample dirigido del cluster de 232 con
  `auditar_fallo.py`.
- 88 casos "sin apertura" del cluster — bug separado de §4.6.b, sin
  diagnóstico propio.
- F013 candidato (caso 330_p2739).
- F012 (granularidad de JUECES_CONOCIDOS).
- F010 (off-by-one `detectar_fin_real` en firmas multilínea).
- F008, F007 preexistentes.

---

## Convenciones que aplican durante la sesión

- Rioplatense, no peninsular.
- RAE accents.
- Antes de modificar archivo, copiar al snapshot del día
  (`bak/sesion_<ts>/`).
- No commitear sin confirmación.
- Commits descriptivos en español, uno por fase.
- Encoding: editar archivos con acentos en VS Code, no PowerShell
  (riesgo de corrupción).
- No crear archivos sin preguntar dónde.
- No regenerar CSVs vivos.
- No tocar `parser.py`.

---

## Cómo arrancar

Pegar este documento al inicio de la sesión, decir "Sesión inventario,
arrancamos Fase 1" y Claude:

1. Pide los comandos de mapeo necesarios para Fase 1 (raíz, `bak/`,
   `tests/`, `validacion/pre/`, `logs/`).
2. Va archivo por archivo o cluster por cluster con decisión
   documentada.
3. Aplica movimientos/eliminaciones con backup defensivo en
   `bak/sesion_<ts>/`.
4. Cierra Fase 1 con commit antes de pasar a Fase 2.

Si Fase 1 + 2 entran en una sesión, seguimos. Si no, cierre limpio y
continuamos en otra.
