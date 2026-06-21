# scripts/diagnostico/

**Archivo forense. No reproducible. No es parte del pipeline ni del dataset.**

Acá vive el trabajo de diagnóstico puntual de cada bug y sesión: snapshots, PoCs,
scripts de un solo uso, exploraciones. Se conserva como rastro de auditoría del
desarrollo, **no se mantiene** y **no se garantiza que corra** contra el estado actual.
Para el porqué de cada cambio, la fuente viva es `BITACORA.md` / `DEUDA_TECNICA.md`.

## Organización

Carpetas por sesión, ~46 en total:
- **`B0xx`** — diagnóstico atado a un bug (`B013`, `B055`, `B069`, `B123`…).
- **`H0xx`** — diagnóstico de una sesión/handoff (`H036`–`H142`).
- **`_b109` / `_b110`** — directorios de trabajo de esos bugs.
- **`benchmark_gemini`**, **`h124`** — exploraciones puntuales.
- Scripts sueltos: `explorar_residual.py`, `extraer_caso.py`.

## No es forense (se va de acá)

- **`kappa/`** → se promueve a **`scripts/validacion/`**. Es validación esencial y
  reproducible (genera la tabla de κ), no diagnóstico descartable.

## Gitignoreado dentro de este árbol

`_extraidos/` (extracciones de trabajo) no se trackea.
