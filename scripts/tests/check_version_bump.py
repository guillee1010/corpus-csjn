#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_version_bump.py  — gate de coherencia de version (AUTODESCUBRIMIENTO)
Ubicacion propuesta en el repo: scripts/tests/check_version_bump.py

Que hace
--------
Si en este commit cambio el codigo de un script versionado de pipeline/auditoria
pero su __version__ NO subio de valor, FALLA (exit 1). Operacionaliza la regla
de memoria #19 y el invariante de procedencia del cierre: un cambio sin bump deja
el manifest stale.

NO usa lista hardcodeada (eso se desactualiza). AUTODESCUBRE: gatea todo .py bajo
SCAN_DIRS que declare __version__, leyendo el disco en cada corrida. Asi cubre los
derivers nuevos (derivar_partes.py = M29/M32, derivar_materia.py, etc.) sin tocar
este script.

Compara el VALOR entrecomillado de __version__, no la linea entera: parser.py
arrastra un comentario-changelog que muta en cada edicion, asi que comparar la
linea daria falso OK.

Ademas avisa (WARN) si staggeas un .py de pipeline SIN __version__: no se puede
gatear, conviene agregarle uno.

Uso (PowerShell, desde la raiz del repo)
----------------------------------------
    python scripts/tests/check_version_bump.py        # modo staged (hook)

Exit 0 = OK   |   Exit 1 = script versionado cambiado sin bump de __version__
"""
import re
import subprocess
import sys
from pathlib import Path

# Carpetas donde se autodescubren scripts versionados. >> ajustar si hace falta.
SCAN_DIRS = ["scripts/pipeline", "scripts/auditoria"]

# Valor entrecomillado de __version__ (para comparar numero, no la linea).
VERSION_RE = re.compile(r"""__version__\s*=\s*["']([^"']+)["']""")
# Declaracion a nivel de modulo (para detectar que un script es "versionado").
DECL_RE = re.compile(r"""(?m)^\s*__version__\s*=\s*["']""")


def _git(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, text=True, encoding="utf-8"
    )


def _staged():
    r = _git(["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def _versioned_scripts():
    """Set (posix) de .py bajo SCAN_DIRS que declaran __version__. Lee el disco."""
    out = set()
    for d in SCAN_DIRS:
        base = Path(d)
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*.py")):
            try:
                txt = p.read_text(encoding="utf-8")
            except OSError:
                continue
            if DECL_RE.search(txt):
                out.add(p.as_posix())
    return out


def _version_bumped(path):
    """True si el VALOR de __version__ cambio en el diff staged de `path`.
    Maneja archivo nuevo (sin valor viejo) y edicion de solo-comentario
    en la linea de version (valor viejo == nuevo -> NO es bump)."""
    r = _git(["diff", "--cached", "--unified=0", "--", path])
    old_val = new_val = None
    for ln in r.stdout.splitlines():
        if ln.startswith("---") or ln.startswith("+++"):
            continue
        m = VERSION_RE.search(ln)
        if not m:
            continue
        if ln.startswith("+"):
            new_val = m.group(1)
        elif ln.startswith("-"):
            old_val = m.group(1)
    return new_val is not None and new_val != old_val


def main():
    staged = _staged()
    versioned = _versioned_scripts()
    gated = sorted(p for p in staged if p in versioned)

    # .py de pipeline staged SIN __version__: no se pueden gatear -> aviso
    unversioned = sorted(
        p for p in staged
        if p.endswith(".py")
        and any(p.startswith(d + "/") for d in SCAN_DIRS)
        and p not in versioned
    )

    if not gated and not unversioned:
        print("[CLEAN] ningun script versionado de pipeline cambio en este commit.")
        return 0

    fallo = False
    for p in gated:
        if _version_bumped(p):
            print(f"[OK]   {p}: __version__ bumpeado (valor cambiado).")
        else:
            fallo = True
            print(f"[FAIL] {p}: cambio el script pero __version__ NO se bumpeo.")

    for p in unversioned:
        print(f"[WARN] {p}: script de pipeline SIN __version__ — no se puede gatear. "
              "Conviene agregarle __version__.")

    if gated and "CHANGELOG.md" not in staged:
        print("[WARN] cambio pipeline pero CHANGELOG.md no esta staged (recordatorio).")

    if fallo:
        print("\nCommit bloqueado: bumpea __version__ del/los script(s) y reintenta.")
        return 1
    print("\n[CLEAN] coherencia de version OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
