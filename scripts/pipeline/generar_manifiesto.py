#!/usr/bin/env python3
"""
generar_manifiesto.py — M14: manifiesto de procedencia del pipeline corpus-csjn.

Escribe `output/parser/_manifest.json` con la procedencia COMPLETA de la cadena:

  A) git: commit HEAD + si el árbol estaba sucio  -> fija TODO el código del repo
     (todos los scripts del pipeline, transitivamente) cuando dirty=false.
  B) pipeline_scripts: __version__ de los cinco scripts de la cadena, en orden
     (detectar_paginas -> construir_catalogo -> cruzar -> parser/_editorial).
     Capa legible, redundante con el commit.
  C) corpus / inputs / outputs: hash + bytes (+ filas en CSV) de los artefactos,
     de la fuente cruda a los finales. Captura el DATO (cambios de corpus /
     intermedios que el commit no distingue). Cada artefacto del pipeline registra
     qué script lo generó; el corpus crudo no tiene generador (es fuente CSJN).

     El set del corpus NO se globea ni se hardcodea: se DERIVA de la columna
     `source_file` de csjn_casos.csv (el parser ya anota, por caso, de qué archivo
     salió cada caso). Así el manifiesto sella exactamente lo que produjo este
     dataset —ni los tomos parqueados que están en corpus/ pero no se parsearon,
     ni una lista a mano que haya que sincronizar—. Si el dataset declara una
     fuente que no está en corpus/, falla ruidoso. Cuando se desparqueen tomos
     (335/336), entran solos al re-correr el pipeline: source_file crece y el
     manifiesto los sella, sin tocar código ni conteos.

     Por archivo: sha256 + n_bytes. Arriba, un `digest` único (sha256 de las
     líneas `nombre:sha256` ordenadas) que resume los N hashes: detecta "cambió
     algo" de un vistazo, mientras el detalle por archivo localiza CUÁL.

No toca ningún CSV -> golden intacto -> check_regresion [CLEAN] por construcción.

Modos:
  (sin flag)  genera / sobreescribe el manifiesto.
  --verify    re-hashea corpus+inputs+outputs y los compara contra el manifiesto;
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

__version__ = "1.1"

# csjn_casos.csv tiene campos de texto grandes (considerando_text). Subimos el
# límite de campo de csv a un valor amplio pero seguro en Windows (sys.maxsize
# desborda el C long allá; 10**7 no).
csv.field_size_limit(10 ** 7)

# ── Rutas resueltas respecto del propio script (robusto al cwd) ───────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # .../scripts/pipeline
REPO_ROOT  = SCRIPT_DIR.parent.parent                 # raíz del repo
OUTPUT_DIR = REPO_ROOT / "output"
CORPUS_DIR = REPO_ROOT / "corpus"
MANIFEST_PATH = OUTPUT_DIR / "parser" / "_manifest.json"

SCHEMA_VERSION = 3

# ── Capa B: scripts del pipeline, en orden de la cadena ──────────────────────
PIPELINE_SCRIPTS = [
    "detectar_paginas.py",
    "construir_catalogo.py",
    "cruzar_catalogo_y_mapa.py",
    "parser.py",
    "parser_editorial.py",
]

# ── Capa C: artefactos del pipeline. (ruta relativa a output/, generador) ────
# inputs = intermedios de la cadena; outputs = los cinco CSV canónicos finales.
# Allow-list explícita a propósito (no glob): excluye BASELINE/_manifest.json,
# y si falta un canónico el script grita en vez de manifestar parcial en silencio.
# El corpus crudo NO va acá: se deriva de source_file (ver fuentes_corpus()).
INPUTS = [
    ("mapa/mapa_paginas.csv",               "detectar_paginas.py"),
    ("catalogo/catalogo.csv",               "construir_catalogo.py"),
    ("localizacion/fallos_localizados.csv", "cruzar_catalogo_y_mapa.py"),
]
OUTPUTS = [
    ("parser/csjn_casos.csv",                   "parser.py"),
    ("parser/csjn_casos_votos.csv",             "parser.py"),
    ("parser/csjn_casos_zonas.csv",             "parser.py"),
    ("parser/csjn_casos_editorial.csv",         "parser.py"),
    ("parser/csjn_editorial_indice_partes.csv", "parser_editorial.py"),
]

# CSV del que se derivan los archivos crudos del corpus (columna source_file).
CASOS_CSV = OUTPUT_DIR / "parser" / "csjn_casos.csv"


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


def entrada_artefacto(abs_path: Path, generado_por: str | None) -> tuple[str, dict]:
    """Entrada de manifiesto para un archivo, raíz-agnóstica (sirve a output/ y
    corpus/). `generado_por=None` para fuente cruda (sin generador). El path se
    guarda relativo a la raíz del repo. n_rows solo para CSV."""
    if not abs_path.exists():
        raise FileNotFoundError(
            f"Falta artefacto: {abs_path.relative_to(REPO_ROOT).as_posix()}")
    info: dict = {"path": abs_path.relative_to(REPO_ROOT).as_posix()}
    if generado_por is not None:
        info["generated_by"] = generado_por
        info["generator_version"] = leer_version_estatica(SCRIPT_DIR / generado_por)
    info["sha256"] = sha256_file(abs_path)
    if abs_path.suffix == ".csv":
        info["n_rows"] = contar_filas_csv(abs_path)
    info["n_bytes"] = abs_path.stat().st_size
    return abs_path.name, info


def fuentes_corpus() -> list[str]:
    """Nombres .md del corpus que produjeron este dataset, derivados de la columna
    source_file de csjn_casos.csv (no glob, no lista a mano). Preserva los nombres
    de la CSJN tal cual (separadores `.`, `_`, `-` inconsistentes incluidos)."""
    if not CASOS_CSV.exists():
        raise FileNotFoundError(
            f"No se puede derivar el corpus: falta {CASOS_CSV.relative_to(REPO_ROOT).as_posix()}")
    nombres: set[str] = set()
    with CASOS_CSV.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            sf = (fila.get("source_file") or "").strip()
            if sf:
                nombres.add(sf)
    if not nombres:
        raise ValueError("csjn_casos.csv no tiene source_file: no se puede sellar el corpus")
    return sorted(nombres)


def digest_corpus(hashes: dict[str, str]) -> str:
    """Huella única del corpus: sha256 de las líneas `nombre:sha256` ordenadas.
    Resume los N hashes en uno (smoke detector); el detalle por archivo localiza."""
    h = hashlib.sha256()
    for nombre in sorted(hashes):
        h.update(f"{nombre}:{hashes[nombre]}\n".encode("utf-8"))
    return h.hexdigest()


def entradas_corpus() -> dict:
    files = dict(entrada_artefacto(CORPUS_DIR / nombre, None)
                 for nombre in fuentes_corpus())
    return {
        "n_files": len(files),
        "digest": digest_corpus({n: info["sha256"] for n, info in files.items()}),
        "files": files,
    }


# ── Construcción / escritura / verificación ──────────────────────────────────
def construir_manifiesto() -> dict:
    corpus  = entradas_corpus()
    inputs  = dict(entrada_artefacto(OUTPUT_DIR / p, g) for p, g in INPUTS)
    outputs = dict(entrada_artefacto(OUTPUT_DIR / p, g) for p, g in OUTPUTS)
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_generator_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git": info_git(),
        "pipeline_scripts": versiones_pipeline(),
        "corpus": corpus,
        "inputs": inputs,
        "outputs": outputs,
    }


def escribir(m: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] {MANIFEST_PATH}")
    c = m["corpus"]
    print(f"  -- corpus --   {c['n_files']} archivos   digest {c['digest'][:12]}…")
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

    # corpus: hash por archivo (localiza CUÁL) + huella única (detecta "cambió algo")
    corpus = g.get("corpus", {})
    files = corpus.get("files", {})
    disco: dict[str, str] = {}
    for nombre, info in files.items():
        n += 1
        path = REPO_ROOT / info["path"]
        if not path.exists():
            problemas.append(f"{nombre}: falta en disco"); continue
        h = sha256_file(path)
        disco[nombre] = h
        if h != info["sha256"]:
            problemas.append(
                f"{nombre}: sha256 no coincide "
                f"(manifiesto {info['sha256'][:12]}… / disco {h[:12]}…)")
    if files and len(disco) == len(files):
        recalc = digest_corpus(disco)
        if recalc != corpus.get("digest"):
            problemas.append(
                f"corpus digest no coincide con disco "
                f"(manifiesto {str(corpus.get('digest'))[:12]}… / recalculado {recalc[:12]}…)")

    # inputs + outputs
    for seccion in ("inputs", "outputs"):
        for nombre, info in g.get(seccion, {}).items():
            n += 1
            path = REPO_ROOT / info["path"]
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
