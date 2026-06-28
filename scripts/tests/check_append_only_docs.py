#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_append_only_docs.py  — gate append-only para BITACORA.md / CHANGELOG.md
Ubicacion propuesta en el repo: scripts/tests/check_append_only_docs.py

Que hace
--------
Mira el diff *staged* (lo que esta por commitearse) de BITACORA.md y CHANGELOG.md
y FALLA (exit 1) si alguna linea EXISTENTE fue borrada o modificada. Solo se
permiten adiciones. Es la regla "solo preparar texto para append" (memoria #16)
vuelta mecanica: el cierre no puede reescribir historia, solo agregarla.

Nota de diseno: NO exige que las adiciones esten al final del archivo, porque no
asumo si BITACORA crece arriba (cronologico inverso) o abajo. Lo que garantiza es
que nada previo se toca. Si queres la version estricta "solo append al EOF",
avisame y la endurezco (necesito saber donde van los appends).

Uso (PowerShell, desde la raiz del repo)
----------------------------------------
    python scripts/tests/check_append_only_docs.py            # modo staged (hook)
    python scripts/tests/check_append_only_docs.py --tracked  # revisa HEAD vs working tree

Exit 0 = OK (solo adiciones)   |   Exit 1 = se modifico/borro contenido previo
"""
import subprocess
import sys

# Paths de los docs append-only (relativos a la raiz del repo). Schema memoria #11.
DOCS = ["BITACORA.md", "CHANGELOG.md"]


def _git(args):
    return subprocess.run(
        ["git"] + args, capture_output=True, text=True, encoding="utf-8"
    )


def _diff(path, mode):
    if mode == "staged":
        # lo que esta en el index vs HEAD
        r = _git(["diff", "--cached", "--unified=0", "--", path])
    else:  # tracked: working tree vs HEAD
        r = _git(["diff", "--unified=0", "HEAD", "--", path])
    return r.stdout.splitlines()


def _removed_lines(diff_lines):
    """Lineas realmente borradas (empiezan con '-' pero no son la cabecera '---')."""
    out = []
    for ln in diff_lines:
        if ln.startswith("-") and not ln.startswith("---"):
            out.append(ln[1:])
    return out


def main():
    mode = "tracked" if "--tracked" in sys.argv else "staged"
    fallo = False

    for doc in DOCS:
        diff = _diff(doc, mode)
        if not diff:
            continue  # sin cambios staged en este doc
        removed = _removed_lines(diff)
        if removed:
            fallo = True
            print(f"[FAIL] {doc}: se modificaron/borraron {len(removed)} linea(s) existente(s).")
            print("       Este archivo es append-only: solo se permiten adiciones.")
            for ln in removed[:8]:
                print(f"         - {ln}")
            if len(removed) > 8:
                print(f"         ... (+{len(removed) - 8} mas)")
        else:
            adds = sum(
                1 for ln in diff if ln.startswith("+") and not ln.startswith("+++")
            )
            print(f"[OK]   {doc}: solo adiciones ({adds} linea(s) nueva(s)).")

    if fallo:
        print("\nCierre/commit bloqueado: corregi los docs append-only y reintenta.")
        return 1
    print("\n[CLEAN] docs append-only intactos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
