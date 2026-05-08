# Changelog

Registro de versiones del parser de fallos CSJN (`csjnvN.py`) y scripts auxiliares.

## v17 beta v2 — 2026-05-01

### Estado: en pruebas, no validado.

### Cambios respecto a v17 beta:

- **Detector de fin de dictamen reescrito.** Reemplaza la heurística "línea con fecha + previa corta" por una regla OR de dos señales:
  - Firma de Procurador conocido al final de línea corta. Lista ampliada empíricamente del corpus: Casal, Monti, Abramovich, Cosarin, Righi, Bausset, Warcalde, Netto, Becerra, Carbó, Obarrio, Beiró, Sachetta.
  - Línea que empieza con "Buenos Aires, X de mes de YYYY" (fecha al pie típica del dictamen).
  - Ambas señales con exclusión de contextos de cita (comillas, "Fallos:", "fs.", "Procurador Fiscal", "Ministerio Público:", "precedente").
- **Nueva columna `wc_fallo_neto = word_count - wc_dictamen`.** Permite análisis del cuerpo decisorio separado del aporte del dictamen.
- **Tipos unificados.** `dictamen_presente`, `is_originaria`, `is_full_bench`, `is_merit_decision` se exportan como `int` (0/1) en todos los casos. v17 beta v1 tenía mezcla de `True/False` (para fallos) y `0` (para sumarios).

### Pendientes / problemas conocidos:

- En la primera corrida con la regla AND (solo firma), `sin_firma` saltó a 1093 (vs 312 en v17 beta v1) y 2600 casos tuvieron `wc_dictamen >= word_count` (dictamen comió todo el bloque). La regla OR busca corregir esto.
- Si la corrida con OR sigue mostrando >500 casos sin firma, considerar rollback a v17 beta v1 o v16.
- 22 casos sospechosos de falso positivo en `tipo_entrada = sumario_con_link` con `status_localizacion = ok` (Ruiz c/ AFIP, Asociación Gremial). No abordado en esta versión.

---

## v17 beta — 2026-05-01

### Estado: validado parcialmente (4 casos de sumario-con-link verificados manualmente; 2 casos de falso positivo identificados pero no resueltos).

### Cambios respecto a v16:

- **Detector de sumarios-con-link.** A partir del tomo 345, la CSJN publica algunos casos solo como sumario editorial con link al fallo online, sin reproducir el fallo completo. v17 detecta el patrón `(*) Sentencia del [fecha]. Ver en https://sj.csjn.gov.ar/...` (variantes "Ver fallo." en tomos 347-349) y marca esos casos como `tipo_entrada = "sumario_con_link"`. Campos analíticos quedan vacíos. Metadata estructural (linea_inicio, linea_fin, source_file, etc.) se conserva.
- **Nueva columna `tipo_entrada`** con valores `"fallo"` (default) o `"sumario_con_link"`.
- **Nueva columna `wc_dictamen`** que exporta el word count del dictamen (heurística heredada de v16, no validada).

### Resultados:

- 5647 casos procesados.
- 160 marcados como `sumario_con_link`:
  - 104 con `status_localizacion = ok_sin_marcador_apertura` (limpios).
  - 56 con `status_localizacion = ok` (ambiguos: 3/5 verificados son sumarios reales; 2/5 son fallos legítimos contaminados por solapamiento de páginas).
- `sin_firma` bajó de 399 (v16 fix1) a 312.

### Pendientes / problemas conocidos:

- Solapamiento estructural del catálogo: una misma página de la edición oficial puede contener dos casos distintos (fallo + sumario, o dos sumarios encadenados), pero el catálogo asigna un solo `caso_id_canonico`. Esto produce:
  - Falsos positivos del detector (~22 casos: fallos largos cuyo bloque incluye un sumario-con-link siguiente).
  - 28 sumarios-con-link cuya firma es del fallo anterior, no propia.
- Solución estructural pendiente (ver "Opción C" en bitácora): post-procesar el catálogo para dividir entradas con múltiples casos. Postergado a v18.

---

## v16 fix1 — 2026-04-29

### Estado: producción (baseline actual).

### Cambios respecto a v16:

- Fix aplicado en `construir_catalogo.py`. Output regenerado como `csjn_casos_v16_fix1.csv`.

---

## v16 — 2026-04-29

### Cambios respecto a v15:

- Fix de extracción de fecha. v15 buscaba la fecha solo en las primeras 8 líneas del bloque, pero el bloque arranca con sumarios y dictamen. v16 busca la fecha cerca del marcador `FALLO DE LA CORTE SUPREMA` (caso a) o como última fecha "Buenos Aires" del bloque (caso b).
- Solo el 5.6% de los fallos tenía fecha extraída en v15. v16 mejora sustancialmente.

---

## v15 — 2026-04-28

### Cambios respecto a v14:

- Detección de fin real del fallo dentro del bloque (`linea_fin_real`). Permite cortar el bloque cuando empieza el caso siguiente, evitando contaminación.
- Output bifurcado: CSV de casos + CSV de votos (uno por juez por caso).

---

## v14, v12, anteriores

Ver historial de git y comentarios en cabecera de cada archivo.


## 2026-05-09 — Diseño detector amputación inferior (H016)

Sesión de diseño puro, sin commits de código. Se cierra decisión sobre variante a implementar (clasificador activo del gap, no pasivo ni con reclasificación), tipos de span de iteración 1 (firma_arrastrada, header_pagina, no_clasificable), alertas estructurales (firma_truncada_en_silabacion, caratula_siguiente_anticipada), y heurística de firma multilínea sin tope arbitrario de líneas (cierre por límites estructurales). Se identifica F008 (off-by-one entre reporte de auditoría y líneas reales del .md, pendiente investigar). Detalle completo en BITACORA H017.

