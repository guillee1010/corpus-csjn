#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gate_manifiesto.py  — gate de integridad de procedencia (WRAPPER, no reimplementa)
Ubicacion propuesta en el repo: scripts/tests/gate_manifiesto.py

Que hace
--------
Corre el verificador de manifiesto QUE YA EXISTE en el pipeline
(scripts/pipeline/generar_manifiesto.py --verify) y traduce su resultado a un
exit code limpio para usarlo como gate de cierre/push.

NO reimplementa nada de la logica de sellado (sha256, ast de __version__, filas,
bytes) — eso vive en generar_manifiesto.py. Esto es solo el enganche, respetando
Gate 3 de apertura ("no reinventar deteccion/logica existente"). Documentado en
cierre-sesion-corpus, Paso 2: esperado `[CLEAN] 8/8`.

  >> VERIFICA: el path del verificador y la cadena esperada de exito.
     Por la doc del skill: comando = generar_manifiesto.py --verify, salida [CLEAN].
     Si tu --verify ya devuelve exit!=0 ante mismatch, este wrapper igual lo
     respeta (chequea returncode Y la marca [CLEAN]).

Uso (PowerShell, desde la raiz del repo)
----------------------------------------
    python scripts/tests/gate_manifiesto.py

Exit 0 = [CLEAN]   |   Exit 1 = manifest stale / mismatch / verificador fallo
"""
import subprocess
import sys

VERIFICADOR = ["python", "scripts/pipeline/generar_manifiesto.py", "--verify"]
MARCA_OK = "[CLEAN]"  # >> VERIFICA: marca de exito que imprime tu --verify


def main():
    try:
        r = subprocess.run(VERIFICADOR, capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError as e:
        print(f"[FAIL] no pude correr el verificador: {e}")
        print(f"       comando: {' '.join(VERIFICADOR)}")
        return 1

    salida = (r.stdout or "") + (r.stderr or "")
    print(salida.rstrip())

    ok = (r.returncode == 0) and (MARCA_OK in salida)
    if ok:
        print("\n[CLEAN] procedencia sellada y consistente.")
        return 0
    print("\n[FAIL] manifest stale o inconsistente. Re-sellar antes de cerrar:")
    print("       python scripts/pipeline/generar_manifiesto.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
