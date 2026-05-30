#!/usr/bin/env python3
"""
Harness de regresion del parser (corpus-csjn).
==============================================

Congela los 4 CSV que produce scripts/pipeline/parser.py como GOLDEN output
y verifica que una corrida nueva los reproduzca byte-a-byte.

Pensado para refactor seguro (REE): refactor = misma salida, mejor estructura.
Si una sola celda cambia, el runner falla con codigo 1.

NOTA: parser.py emite 4 CSV (casos, votos, zonas, editorial). El 5o canonico
(csjn_editorial_indice_partes.csv) lo produce parser_editorial.py aparte: NO
esta cubierto por este harness.

Ubicacion esperada: scripts/tests/check_regresion.py
Golden:             scripts/tests/golden/  (commitear al repo)

Uso (desde cualquier carpeta del repo):
    python scripts/tests/check_regresion.py --make-golden   # congela el estado actual
    python scripts/tests/check_regresion.py                 # verifica contra el golden

El runner NUNCA pisa output/parser/ productivo: corre el parser a un dir temporal.
"""

import sys
import csv
import shutil
import hashlib
import tempfile
import argparse
import subprocess
from pathlib import Path

# ── Rutas (relativas a la raiz del repo) ─────────────────────────────────────
# scripts/tests/check_regresion.py -> parents[2] = raiz del repo
REPO_ROOT   = Path(__file__).resolve().parents[2]
PIPELINE    = REPO_ROOT / "scripts" / "pipeline"
PARSER      = PIPELINE / "parser.py"
LOCALIZADOS = REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA        = REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS      = REPO_ROOT / "corpus"
GOLDEN_DIR  = REPO_ROOT / "scripts" / "tests" / "golden"

# Los 4 CSV que emite parser.py (derivados del stem de --output).
OUTPUTS = [
    "csjn_casos.csv",
    "csjn_casos_votos.csv",
    "csjn_casos_zonas.csv",
    "csjn_casos_editorial.csv",
]

# Cuantos diffs de celda mostrar por archivo antes de cortar.
MAX_DIFFS = 25


def _check_inputs():
    faltan = [p for p in (PARSER, LOCALIZADOS, MAPA, CORPUS) if not p.exists()]
    if faltan:
        print("[ABORT] No encuentro estos paths (¿corres desde el repo correcto?):")
        for p in faltan:
            print(f"   {p}")
        sys.exit(2)


def correr_parser(out_dir: Path):
    """Corre parser.py a out_dir. cwd=PIPELINE para que resuelva
    `from parser_editorial import ...` y se generen los 4 CSV juntos."""
    out_csv = out_dir / "csjn_casos.csv"
    cmd = [
        sys.executable, "parser.py",
        "--localizados", str(LOCALIZADOS),
        "--mapa", str(MAPA),
        "--corpus", str(CORPUS),
        "--output", str(out_csv),
    ]
    print(f"[run] {' '.join(cmd)}  (cwd={PIPELINE})")
    r = subprocess.run(cmd, cwd=str(PIPELINE))
    if r.returncode != 0:
        print(f"[ABORT] el parser salio con codigo {r.returncode}")
        sys.exit(2)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def diff_celdas(golden: Path, nuevo: Path):
    """Diff posicional fila a fila. El parser es determinista (itera ordenado),
    asi que comparar por posicion detecta cambios de celda, filas agregadas/
    quitadas y reordenamientos. Devuelve lista de strings describiendo diffs."""
    diffs = []
    with golden.open(encoding="utf-8", newline="") as fg, \
         nuevo.open(encoding="utf-8", newline="") as fn:
        rg = list(csv.reader(fg))
        rn = list(csv.reader(fn))

    if rg[0] != rn[0]:
        diffs.append(f"  HEADER cambiado:\n    golden: {rg[0]}\n    nuevo : {rn[0]}")
        return diffs  # si cambio el header no tiene sentido seguir por columna

    if len(rg) != len(rn):
        diffs.append(f"  N FILAS: golden={len(rg)-1}  nuevo={len(rn)-1}  (dif={len(rn)-len(rg)})")

    header = rg[0]
    n = min(len(rg), len(rn))
    for i in range(1, n):
        if rg[i] == rn[i]:
            continue
        caso = rg[i][0] if rg[i] else "?"
        # columnas que difieren
        for j in range(max(len(rg[i]), len(rn[i]))):
            vg = rg[i][j] if j < len(rg[i]) else "<falta>"
            vn = rn[i][j] if j < len(rn[i]) else "<falta>"
            if vg != vn:
                col = header[j] if j < len(header) else f"col{j}"
                diffs.append(f"  fila {i} [{caso}] col '{col}':\n"
                             f"      golden: {vg!r}\n      nuevo : {vn!r}")
                if len(diffs) >= MAX_DIFFS:
                    diffs.append(f"  ... (cortado en {MAX_DIFFS} diffs)")
                    return diffs
    return diffs


def make_golden():
    _check_inputs()
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        correr_parser(tmp)
        print()
        for name in OUTPUTS:
            src = tmp / name
            if not src.exists():
                print(f"[WARN] el parser no genero {name}, lo salteo")
                continue
            shutil.copy2(src, GOLDEN_DIR / name)
            print(f"[golden] {name}  sha256={sha256(GOLDEN_DIR / name)[:12]}")
    print(f"\n[OK] Golden congelado en {GOLDEN_DIR}")
    print("     Acordate de commitearlo: es el contrato de regresion.")


def check():
    _check_inputs()
    if not GOLDEN_DIR.exists() or not any((GOLDEN_DIR / n).exists() for n in OUTPUTS):
        print(f"[ABORT] no hay golden en {GOLDEN_DIR}. Corre primero --make-golden")
        sys.exit(2)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        correr_parser(tmp)
        print("\n── Comparacion contra golden ──")
        fallidos = []
        for name in OUTPUTS:
            g, nuevo = GOLDEN_DIR / name, tmp / name
            if not g.exists():
                print(f"  [skip] {name}: no esta en el golden")
                continue
            if not nuevo.exists():
                print(f"  [FAIL] {name}: el parser no lo genero esta corrida")
                fallidos.append(name)
                continue
            if sha256(g) == sha256(nuevo):
                print(f"  [OK]   {name}")
            else:
                print(f"  [FAIL] {name}: difiere del golden")
                fallidos.append(name)
                for line in diff_celdas(g, nuevo):
                    print(line)

    print()
    if fallidos:
        print(f"[REGRESION] {len(fallidos)}/{len(OUTPUTS)} CSV cambiaron: {', '.join(fallidos)}")
        print("Si esto es un refactor, NO mergear: refactor = misma salida.")
        sys.exit(1)
    print(f"[CLEAN] los {len(OUTPUTS)} CSV son identicos al golden. Salida intacta.")
    sys.exit(0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Harness de regresion del parser corpus-csjn")
    ap.add_argument("--make-golden", action="store_true",
                    help="Regenera y congela los 4 CSV como golden (commitear)")
    args = ap.parse_args()
    if args.make_golden:
        make_golden()
    else:
        check()
