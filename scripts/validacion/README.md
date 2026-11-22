# scripts/validacion/

Subsistema de **validación de confiabilidad** del pipeline. No es forense de sesión:
es esencial y reproducible — produce la tabla de κ que reporta la calidad del dataset.
*(Promovido desde `scripts/diagnostico/kappa/` — ver nota de paths al final.)*

## Scripts

### `kappa_confiabilidad.py` *(leído)*
κ de Cohen entre la predicción del parser y el gold humano, **por variable**.
No es κ de doble codificación (esa validaría la reproducibilidad del codebook con una
2.ª codificación; esto mide parser ↔ gold).

- IC 95% por bootstrap (default 5.000 réplicas, seed 42); lectura Landis-Koch.
- Normaliza a NA: `{"", "-", "revisar"}` y valores puramente numéricos.
- Variables evaluadas: `es_revision_fondo`, `via_recurso`, `disposicion`,
  `parte_ganadora`, `reenvia` (la lista `VARIABLES` se edita en el head del script;
  para sumar `cuestion_federal`/`dictamen`/`materia` hay que agregar la fuente en `SOURCES`).
- CLI: `--gold <xlsx|csv> --recursos <csv> [--out <csv>] [--boot N]`.

```powershell
python scripts\validacion\kappa_confiabilidad.py `
  --gold scripts\validacion\golds\planilla_M20_57GOLD_parte_limpia.xlsx `
  --recursos output\parser\csjn_casos_recursos.csv `
  --out output\validacion\kappa_resultados_parte.csv
```

### `cruce_sjconsulta.py` *(H221, M66)*
Cruce de la posición de cada juez titular entre el corpus y sjconsulta (base de sumarios de la
Secretaría de Jurisprudencia), como segundo codificador externo. Lee `output/parser/csjn_casos.csv`
(read-only) y escribe en el cache local (JSON limpios por mes + `posiciones_AAAA.csv`).

- Baja los sumarios por mes desde sjconsulta (pausa 1,5 s); reusa el cache; si un mes falla, reintenta por quincenas.
- v0.3: guarda también la capa funcionarial (código de usuario, nombre, cargo y fechas de carga/modificación por sumario, análisis y elemento cargado), sin CUIL ni mail; cache `sj_AAAAMM_v03.json`. Uso analítico; anonimizar en toda exposición.
- Reintentos: mes → quincenas → semanas, y hasta 3 intentos por página.
- Excluye fallos con CONJUECES en SJ. Diferencias de definición conocidas en M67.
- CLI: `AAAA [--cache DIR]` (default `scripts/diagnostico/sjconsulta/`, gitignoreado).

```powershell
foreach ($y in 2016..2026) { python scripts\validacion\cruce_sjconsulta.py $y *> scripts\diagnostico\sjconsulta\log_$y.txt }
```

### `kappa_sjconsulta.py` *(H221, M66)*
Hace auditable la validación externa de votos. Recalcula desde el cache de `cruce_sjconsulta.py`
(importa su lógica, no la duplica) los pares juez×fallo y escribe en `output/validacion/`:
`kappa_sjconsulta.csv` (acuerdo y κ por año y total, IC 95% por bootstrap por fallo),
`kappa_sjconsulta_matriz.csv` (matriz SJ × corpus) y `sjconsulta_manifest.csv` (sha256 y registros
de cada archivo del cache). Los tres son agregados o hashes, sin datos personales, y se versionan.

```powershell
python scripts\validacion\kappa_sjconsulta.py
```

### `superficie_b177.py` *(H221, B177)*
Por caso: marcas de disidencia parcial en la firma y en headers dentro del rango de líneas del fallo, contra lo
que publica `posiciones`. Salida `output/validacion/superficie_b177.csv`.

### `output/validacion/adjudicacion_sjconsulta_h221.csv` *(dato curado, H221)*
Una fila por discrepancia corpus × sjconsulta adjudicada: clase (B177, B179, B019…), quién tiene razón,
si se leyó con texto y la evidencia con número de línea. Cada fila leída se verifica con
`scripts/diagnostico/extraer_caso.py <caso_id>`.

### `superficie_b179.py` *(H224, B179)*
Fórmulas con que un juez deja a salvo su posición dentro del voto común (remisión a su voto o disidencia
en un precedente, "por mayoría" en el por_ello, mayoría con nombres, escisión del conjunto decisorio),
sobre `considerando_text` y `por_ello_text` des-guionados. Una fila por match, con los jueces de
`posiciones` nombrados en la ventana. Salida `output/validacion/superficie_b179.csv`. Es un piso.

### `output/validacion/adjudicacion_b179_h224.csv` *(dato curado, H224)*
Una fila por juez en cada fallo de la superficie B179 v0.6: clase (RV, RD, RA, VC, RS, PUB, FP_*), efecto
en el resultado (disiente si el por_ello dice "por mayoría"; concurre; sin_determinar) y evidencia.

### Resto del subsistema *(rol; internals sin leer — verificar)*
| Archivo | Rol (aproximado) |
|---|---|
| `build_m20.py` | Construye la planilla M20 (insumo de codificación a mano). |
| `validar_H120.py` | Regenera el gold `__rebuild` (su `OUT`). |
| `analizar_validacion_M20.py` | Análisis de la validación M20. |
| `CODEBOOK_M20.md` | Codebook de la codificación M20. |
| `M20_clave_parser_n300.csv` | Clave del parser para el n=300. |
| `textos_n300.csv` | Textos del n=300 para codificación blind. |
| `golds/` | Golds de validación: `…_57GOLD_parte_limpia` (binario, parte limpia) y `…codificar-56` (original 3-valores). `__rebuild` es derivado/regenerable. |

## Notas

- **Working files gitignoreados** que viven acá pero **no** se trackean:
  `reenvia_42.md` y `_extraidos_reenvia/`.
- **Paths:** `build_m20.py` y `validar_H120.py` hardcodean `HERE / <gold>`; con el move a
  `scripts/validacion/` hay que ajustarlos a `HERE / "golds" / <gold>`.
  `kappa_confiabilidad.py` no se ve afectado (usa `--gold`).

### `kappa_disposicion_via_sj.py` *(H224, M66)*
κ de Cohen con IC 95% bootstrap de `disposicion`, `via_recurso` y `es_queja` (`csjn_casos_recursos.csv`)
contra `sentido` y `tipo_recurso` de sjconsulta. Lee `casos_sjconsulta.csv` del cache local (sin datos de
funcionarios). Las tablas de equivalencia están al principio del script y son decisión del operador.
Salidas `output/validacion/kappa_disposicion_via_sj.csv` y `kappa_disposicion_via_sj_matriz.csv`.
