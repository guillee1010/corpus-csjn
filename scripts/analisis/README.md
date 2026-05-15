# scripts/analisis/

Análisis estadístico empírico del corpus CSJN para la tesis de maestría
sobre formación de mayorías en la Corte Suprema argentina.

## Estado actual: PAUSADO

Este componente del proyecto está **en pausa desde fines de abril de 2026**.
La pausa fue una decisión estratégica: se priorizó cerrar el bug del parser
(versión v17 beta) antes de retomar el análisis. No es abandono.

Cuando se retome, será probablemente el componente más importante del
proyecto desde el punto de vista de la tesis: produce los outputs
empíricos que sostienen las hipótesis H1–H5.

---

## Archivos

| Archivo | Función |
|---|---|
| `csjn_analisis_v3.py` | Script principal. Análisis con corpus extendido 2006-2026, 5 regímenes institucionales, estratificación opcional por tipo_caso, detector de templates opcional. |
| `clasificador_tipo_caso.py` | Dependencia de v3: asigna las variables `tipo_caso` y `tipo_caso_grupo` (admisibilidad / núcleo / originaria) al CSV de casos. Se usa cuando se invoca v3 con `--tipo-caso`. |
| `detector_templates.py` | Dependencia opcional de v3: detecta los templates Lorenzetti+Vidal y Rosenkrantz+Levinas. Se usa cuando se invoca v3 con `--templates`. |

Los tres archivos viven juntos para que las dependencias internas no se rompan.

## Versión histórica

`csjn_analisis_v2.py` está en `archivo/scripts_historicos/analisis/`.
v2 fue reemplazado por v3 (corpus más extendido, 5 regímenes institucionales).
v2 conserva interés como referencia metodológica para módulos que v3
podría no traer:
- ZINB sobre `wc_votos`
- Co-disidencia condicional al banco institucional con bootstrap IC95
- Análisis de robustez del efecto del dictamen (4 pruebas)
- Multinomial logit a nivel voto con efectos fijos por juez

Antes de reescribir cualquiera de esos análisis, revisar v2.

---

## ⚠ Antes de re-correr cualquier script

Los scripts fueron escritos contra el esquema del parser v9–v16. El
corpus vivo actual es **v17 beta**. Hay tres cosas que cambiaron:

### 1. Nombres de archivo

| Esquema viejo (en docstrings) | Esquema actual |
|---|---|
| `csjn_casos_v9.csv`, `v10.csv`, `v16.csv` | `csjn_casos.csv` |
| `csjn_casos_v9_votos.csv`, etc. | `csjn_casos_votos.csv` |

Ubicación actual: `output/parser/`.

### 2. Posibles cambios de columnas

El parser v17 introdujo:
- `tipo_entrada` (distingue `"fallo"` de `"sumario_con_link"`)
- Posibles cambios en la lógica de `voting_pattern`, `outcome`, `dictamen_presente`

Verificar contra el esquema actual antes de asumir compatibilidad.

### 3. Volumen

- v9: 817 casos
- v17 beta: 5.819 casos

Los modelos pueden necesitar revisión de potencia estadística, supuestos
de convergencia (especialmente ZINB y MNLogit), y los umbrales `N < 30`
en co-disidencia.

---

## Cómo retomar

1. Leer este README y el de v3 (en docstring del script).
2. Verificar nombres de columnas del corpus vivo:
   ```powershell
   python -c "import pandas as pd; print(pd.read_csv('output/parser/csjn_casos.csv', nrows=1).columns.tolist())"
   ```
3. Adaptar los nombres de archivo de input en los argumentos `--casos`
   y `--votos` de v3.
4. Correr una primera vez con `--tipo-caso nucleo` para validar que
   las dependencias internas (clasificador_tipo_caso) funcionan.
5. Si rompe algo: revisar `archivo/scripts_historicos/auxiliares/NOTAS.md`
   antes de reescribir, puede haber lógica vieja útil.

## Decisiones diferidas

- ¿Mantener v3 o forkearlo a v4 para el corpus v17? Si los cambios son
  grandes, conviene v4 con git history clara.
- ¿Mover `clasificador_tipo_caso.py` a `scripts/pipeline/` cuando v3
  retome? Conceptualmente es post-procesamiento del parser, pero su
  consumidor real es el análisis. Decisión: dejarlo en `analisis/`
  mientras esté pausado; reconsiderar al reactivar.
