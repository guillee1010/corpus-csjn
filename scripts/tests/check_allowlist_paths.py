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

En AMBOS modos se chequean ademas los archivos UNTRACKED no-ignorados del
working tree (v1.1, ver changelog).

Exit 0 = OK   |   Exit 1 = path fuera de la estructura permitida
"""
import subprocess
import sys

__version__ = "1.2"  # H173: M41 (2ª iteracion) — el gate delegaba TODA la vista del arbol en git, pero la politica del repo (publico) es que git NO vea el scratch de diagnostico: .gitignore 42 `scripts/diagnostico/*` (intencional, solo README trackeado) y 50/53 `/diagnostico/`. La v1.1 (untracked via --exclude-standard) quedaba ciega a lo IGNORADO → el PoC de la deriva no fallaba. v1.2 agrega _fs_toplevel(): escaneo de PRIMER NIVEL del filesystem desde la raiz real del repo (git rev-parse --show-toplevel) — dirs de raiz fuera de TOP_DIRS_OK y archivos de raiz fuera de ROOT_FILES_OK fallan SIN importar su estado en git, marcados (en disco). No camina el arbol completo (los ignorados profundos —__pycache__, extraidos en scripts/diagnostico/HXX/— son legitimos por politica). // 1.1 (H173): + untracked no-ignorados en ambos modos. // 1.0 (H166): gate original, allowlist desde el arbol real.

# --- Archivos permitidos en la RAIZ (single-component). Del arbol real. -------
ROOT_FILES_OK = {
    ".env",          # [SECRETS] convención estándar; ignorado por git, vive en raíz (triage M41/H173)
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
    ".tmp.driveupload",  # [SYNC] transitoria de Google Drive for Desktop; aparece/desaparece con el sync (triage M41/H173)
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


def _run_git(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return [p for p in r.stdout.split("\0") if p]


def _git_paths(mode):
    """Devuelve [(path, origen)] con origen ∈ {"tracked", "staged", "untracked"}.

    v1.1 (M41): en ambos modos se agregan los untracked no-ignorados del
    working tree — la regla de schema aplica al arbol, no solo a los commits;
    los archivos que git no trackea eran el punto ciego exacto de la deriva
    H171/H172.
    """
    if mode == "all":
        base = [(p, "tracked") for p in _run_git(["git", "ls-files", "-z"])]
    else:  # staged
        base = [(p, "staged") for p in _run_git(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"])]
    vistos = {p for p, _ in base}
    untracked = [(p, "untracked") for p in _run_git(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"])
        if p not in vistos]
    return base + untracked


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


def _fs_toplevel():
    """v1.2 (M41): audita el PRIMER NIVEL del working tree EN DISCO, sin pasar
    por git — unica forma de ver lo ignorado (.gitignore /diagnostico/,
    scripts/diagnostico/*), que es politica del repo publico y fue el punto
    ciego exacto de la deriva H171/H172. Devuelve [(path, "en disco")].
    Solo primer nivel: los ignorados profundos son legitimos por politica.
    """
    import os
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True, encoding="utf-8")
    raiz = r.stdout.strip()
    if not raiz:
        return []  # fuera de un repo git: no hay raiz que auditar
    out = []
    for nombre in sorted(os.listdir(raiz)):
        if nombre == ".git":
            continue
        full = os.path.join(raiz, nombre)
        if os.path.isdir(full):
            if nombre not in TOP_DIRS_OK:
                out.append((nombre + "/", "en disco"))
        else:
            if nombre not in ROOT_FILES_OK:
                out.append((nombre, "en disco"))
    return out


def main():
    mode = "all" if "--all" in sys.argv else "staged"
    paths = _git_paths(mode)

    fallos = []
    ya_en_disco = set()

    # v1.2 (M41): primer nivel del disco, independiente de git/ignorados.
    for p, _ in _fs_toplevel():
        ya_en_disco.add(p.rstrip("/"))
        if p.endswith("/"):
            fallos.append(f"top-level dir no permitido: {p}  (en disco, ignorado o no)")
        else:
            fallos.append(f"archivo nuevo en RAIZ no permitido: {p}  (en disco, ignorado o no)")

    if not paths and not fallos:
        print(f"[CLEAN] sin archivos para chequear (modo {mode}); raiz en disco OK.")
        return 0

    for p, origen in paths:
        if p.split("/")[0] in ya_en_disco:
            continue  # ya reportado por el escaneo de disco
        motivo = _check(p)
        if motivo:
            if origen == "untracked":
                motivo += "  (untracked)"
            fallos.append(motivo)

    if fallos:
        print(f"[FAIL] {len(fallos)} path(s) fuera de la estructura permitida:")
        for m in fallos:
            print(f"   - {m}")
        print("\nSi es intencional, agregalo a ROOT_FILES_OK / TOP_DIRS_OK. "
              "Si no, movelo al schema antes de commitear.")
        return 1

    print(f"[CLEAN] {len(paths)} path(s) via git + raiz en disco, dentro de la estructura permitida (modo {mode}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
