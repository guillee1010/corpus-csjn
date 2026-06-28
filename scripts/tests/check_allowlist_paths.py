#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_allowlist_paths.py  — gate de estructura (allowlist de paths)
Ubicacion propuesta en el repo: scripts/tests/check_allowlist_paths.py

Que hace
--------
Rechaza (exit 1) cualquier archivo que caiga FUERA de la estructura conocida:
- archivos nuevos en la RAIZ que no esten en la lista permitida, y
- archivos bajo un top-level dir que no este en la lista permitida.
Operacionaliza "no crear archivos en raiz ni fuera del schema sin preguntar"
(memoria #11/#22), volviendolo un bloqueo en vez de un pedido.

>> ESTAS LISTAS SALEN DEL ARBOL REAL (git ls-files), NO DE MEMORIA.
   Bendicen lo que HOY esta commiteado, para no dar falsos positivos sobre
   archivos existentes. Lo marcado como [CRUFT?] esta permitido pero es
   candidato a limpieza/mudanza — decidi vos si sale del allowlist al limpiarlo.

Por defecto el gate trabaja a granularidad de top-level. STRICT_SUBDIRS (abajo,
comentado) permite ademas exigir subcarpetas canonicas dentro de scripts/ y
output/ — activalo cuando quieras apretar la tuerca.

Uso (PowerShell, desde la raiz del repo)
----------------------------------------
    python scripts/tests/check_allowlist_paths.py            # modo staged (hook)
    python scripts/tests/check_allowlist_paths.py --all      # auditar todo el repo

Exit 0 = OK   |   Exit 1 = path fuera de la estructura permitida
"""
import subprocess
import sys

# --- Archivos permitidos en la RAIZ (single-component). Del arbol real. -------
ROOT_FILES_OK = {
    ".gitattributes",
    ".gitignore",
    "BITACORA.md",
    "CHANGELOG.md",
    "CODEBOOK.md",
    "DEUDA_TECNICA.md",
    "DISENO_SCDB_corpus.md",
     "MAPA.md",
    "README.md",
    "extraer_lote_M20.py",   # [CRUFT?] .py suelto en raiz — candidato a mover a scripts/
}

# --- Top-level dirs permitidos. Del arbol real. -------------------------------
TOP_DIRS_OK = {
    "335 y 336",   # [CRUFT?] OCR/legacy de tomos 335-336 — candidato a archivo/ o limpieza
    "_meta",
    "archivo",
    "corpus",
    "estadisticas",
    "output",
    "scripts",
    ".github",     # CI; no aparecio en ls-files (ver nota al usuario). Permitido por las dudas.
}

# --- (Opcional) subcarpetas canonicas. Descomentar para gate estricto. --------
# STRICT_SUBDIRS = {
#     "scripts": {"analisis", "auditoria", "auxiliares", "diagnostico",
#                 "explorador", "migraciones", "pipeline", "tests",
#                 "validacion", "visor"},
#     "output":  {"catalogo", "localizacion", "mapa", "parser",
#                 "validacion", "visor"},
# }
STRICT_SUBDIRS = {}


def _git_paths(mode):
    if mode == "all":
        args = ["git", "ls-files", "-z"]
    else:  # staged
        args = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return [p for p in r.stdout.split("\0") if p]


def _check(path):
    """Devuelve None si OK, o un string con el motivo del rechazo."""
    parts = path.split("/")
    if len(parts) == 1:
        if path not in ROOT_FILES_OK:
            return f"archivo nuevo en RAIZ no permitido: {path}"
        return None
    top = parts[0]
    if top not in TOP_DIRS_OK:
        return f"top-level dir no permitido: {top}/  (en {path})"
    sub_ok = STRICT_SUBDIRS.get(top)
    if sub_ok is not None and len(parts) >= 2 and parts[1] not in sub_ok:
        return f"subcarpeta no canonica en {top}/: {parts[1]}/  (en {path})"
    return None


def main():
    mode = "all" if "--all" in sys.argv else "staged"
    paths = _git_paths(mode)

    if not paths:
        print(f"[CLEAN] sin archivos para chequear (modo {mode}).")
        return 0

    fallos = []
    for p in paths:
        motivo = _check(p)
        if motivo:
            fallos.append(motivo)

    if fallos:
        print(f"[FAIL] {len(fallos)} path(s) fuera de la estructura permitida:")
        for m in fallos:
            print(f"   - {m}")
        print("\nSi es intencional, agregalo a ROOT_FILES_OK / TOP_DIRS_OK. "
              "Si no, movelo al schema antes de commitear.")
        return 1

    print(f"[CLEAN] {len(paths)} path(s) dentro de la estructura permitida (modo {mode}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
