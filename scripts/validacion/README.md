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
