#!/usr/bin/env python3
"""
generar_manifiesto.py — M14: manifiesto de procedencia del pipeline corpus-csjn.

Escribe `output/parser/_manifest.json` con la procedencia COMPLETA de la cadena:

  A) git: commit HEAD + si el árbol estaba sucio  -> fija TODO el código del repo
     (todos los scripts del pipeline, transitivamente) cuando dirty=false.
  B) pipeline_scripts: __version__ de los cinco scripts de la cadena, en orden
     (detectar_paginas -> construir_catalogo -> cruzar -> parser/_editorial).
     Capa legible, redundante con el commit.
  C) inputs / outputs: hash + filas + bytes de los artefactos intermedios y
     finales. Captura el DATO (cambios de corpus / intermedios que el commit no
     distingue). Cada archivo registra qué script lo generó.

No toca ningún CSV -> golden intacto -> check_regresion [CLEAN] por construcción.

Modos:
  (sin flag)  genera / sobreescribe el manifiesto.
  --verify    re-hashea inputs+outputs y los compara contra el manifiesto;
              sale con código != 0 si algo no coincide (red de integridad).

Uso:
    python scripts/pipeline/generar_manifiesto.py
    python scripts/pipeline/generar_manifiesto.py --verify
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

__version__ = "1.0"

# ── Rutas resueltas respecto del propio script (robusto al cwd) ───────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # .../scripts/pipeline
REPO_ROOT  = SCRIPT_DIR.parent.parent                 # raíz del repo
OUTPUT_DIR = REPO_ROOT / "output"
MANIFEST_PATH = OUTPUT_DIR / "parser" / "_manifest.json"

SCHEMA_VERSION = 2

# ── Capa B: scripts del pipeline, en orden de la cadena ──────────────────────
PIPELINE_SCRIPTS = [
    "detectar_paginas.py",
    "construir_catalogo.py",
    "cruzar_catalogo_y_mapa.py",
    "parser.py",
    "parser_editorial.py",
]

# ── Capa C: artefactos. (ruta relativa a output/, generador) ─────────────────
# inputs = intermedios de la cadena; outputs = los cinco CSV canónicos finales.
# Allow-list explícita a propósito (no glob): excluye BASELINE/_manifest.json,
# y si falta un canónico el script grita en vez de manifestar parcial en silencio.
INPUTS = [
    ("mapa/mapa_paginas.csv",            "detectar_paginas.py"),
    ("catalogo/catalogo.csv",            "construir_catalogo.py"),
    ("localizacion/fallos_localizados.csv", "cruzar_catalogo_y_mapa.py"),
]
OUTPUTS = [
    ("parser/csjn_casos.csv",                  "parser.py"),
    ("parser/csjn_casos_votos.csv",            "parser.py"),
    ("parser/csjn_casos_zonas.csv",            "parser.py"),
    ("parser/csjn_casos_editorial.csv",        "parser.py"),
    ("parser/csjn_editorial_indice_partes.csv", "parser_editorial.py"),
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def contar_filas_csv(path: Path) -> int:
    """Registros de datos (sin header). csv.reader maneja newlines embebidos."""
    with path.open(encoding="utf-8", newline="") as f:
        n = sum(1 for _ in csv.reader(f))
    return max(n - 1, 0)


def leer_version_estatica(py_path: Path) -> str:
    """Lee `__version__` del fuente sin importar el módulo (sin efectos colaterales)."""
    if not py_path.exists():
        return "ausente"
    arbol = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign):
            for destino in nodo.targets:
                if (isinstance(destino, ast.Name) and destino.id == "__version__"
                        and isinstance(nodo.value, ast.Constant)
                        and isinstance(nodo.value.value, str)):
                    return nodo.value.value
    return "desconocida"


def versiones_pipeline() -> dict[str, str]:
    return {s: leer_version_estatica(SCRIPT_DIR / s) for s in PIPELINE_SCRIPTS}


def info_git() -> dict:
    """commit HEAD + si el árbol estaba sucio. None si no hay git."""
    def _git(*args):
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    try:
        return {"commit": _git("rev-parse", "HEAD"),
                "dirty": bool(_git("status", "--porcelain"))}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"commit": None, "dirty": None}


def entrada_archivo(rel_path: str, generado_por: str) -> tuple[str, dict]:
    path = OUTPUT_DIR / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Falta artefacto canónico: output/{rel_path}")
    nombre = Path(rel_path).name
    return nombre, {
        "path": f"output/{rel_path}",
        "generated_by": generado_por,
        "generator_version": leer_version_estatica(SCRIPT_DIR / generado_por),
        "sha256": sha256_file(path),
        "n_rows": contar_filas_csv(path),
        "n_bytes": path.stat().st_size,
    }


# ── Construcción / escritura / verificación ──────────────────────────────────
def construir_manifiesto() -> dict:
    inputs  = dict(entrada_archivo(p, g) for p, g in INPUTS)
    outputs = dict(entrada_archivo(p, g) for p, g in OUTPUTS)
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_generator_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": info_git(),
        "pipeline_scripts": versiones_pipeline(),
        "inputs": inputs,
        "outputs": outputs,
    }


def escribir(m: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] {MANIFEST_PATH}")
    for seccion in ("inputs", "outputs"):
        print(f"  -- {seccion} --")
        for nombre, info in m[seccion].items():
            print(f"     {nombre:<34} {info['n_rows']:>7} filas  "
                  f"{info['sha256'][:12]}…  v{info['generator_version']}")


def verificar() -> int:
    if not MANIFEST_PATH.exists():
        print(f"[ERROR] no existe {MANIFEST_PATH}; corré sin --verify primero.")
        return 2
    g = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    problemas, n = [], 0
    for seccion in ("inputs", "outputs"):
        for nombre, info in g.get(seccion, {}).items():
            n += 1
            path = OUTPUT_DIR / Path(info["path"]).relative_to("output")
            if not path.exists():
                problemas.append(f"{nombre}: falta en disco"); continue
            h = sha256_file(path)
            if h != info["sha256"]:
                problemas.append(
                    f"{nombre}: sha256 no coincide "
                    f"(manifiesto {info['sha256'][:12]}… / disco {h[:12]}…)")
    if problemas:
        print("[INTEGRIDAD] discrepancias:")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print(f"[CLEAN] {n} artefactos coinciden con el manifiesto.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="M14 — manifiesto de procedencia del pipeline.")
    ap.add_argument("--verify", action="store_true",
                    help="comparar artefactos contra el manifiesto existente (read-only)")
    args = ap.parse_args()
    return verificar() if args.verify else (escribir(construir_manifiesto()) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
