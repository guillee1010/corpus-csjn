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
