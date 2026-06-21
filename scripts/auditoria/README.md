# scripts/auditoria/

**Archivo forense. No reproducible. No es parte del pipeline ni del dataset.**

Auditorías puntuales por bug y sesión: verificaciones de extracción, chequeos de
límites, comparaciones contra el texto fuente hechas para cerrar un bug o validar una
sesión. Se conserva como rastro de auditoría; **no se mantiene**. La fuente viva del
porqué es `BITACORA.md` / `DEUDA_TECNICA.md`.

## Organización

Carpetas por sesión, ~24 en total: `A001`, `B0xx` (`B067`, `B069`, `B074`),
y `H048`–`H076`.

## No es forense (decisión pendiente)

- **`auditar_fallo.py`** (suelto en la raíz de este dir) — auditor de casos individuales,
  citado en el CODEBOOK §10 como módulo de validación. Es **herramienta reusable**, no
  forense de sesión. Decisión: dejarlo como tool acá, o moverlo a `scripts/validacion/`.
