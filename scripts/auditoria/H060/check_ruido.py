"""
H060 — Inspección de secciones con ruido.
Muestra las primeras líneas de los casos problemáticos.
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
while REPO_ROOT != REPO_ROOT.parent:
    if (REPO_ROOT / "corpus").is_dir():
        break
    REPO_ROOT = REPO_ROOT.parent

CORPUS = REPO_ROOT / "corpus"

CASES = [
    ("LibroVol332.2.md", 43206, 43305, "desconocido (100 líneas)"),
    ("LibroVol334.2.md", 13342, 13429, "desconocido (88 líneas)"),
    ("LibroVol333.1.md", 30125, 30160, "indice_partes cortísimo (13 líneas)"),
    # También 330.4 post-INDICE GENERAL
    ("LibroVol330.4.md", 48496, 48560, "indice_general inicio (ver qué sigue al TOC)"),
]

for sf, li, lf, label in CASES:
    fp = CORPUS / sf
    if not fp.exists():
        print(f"NO ENCONTRADO: {sf}")
        continue
    lines = fp.read_text(encoding="utf-8").splitlines()
    lf = min(lf, len(lines) - 1)
    print(f"\n{'='*72}")
    print(f"{sf} | L{li}–L{lf} | {label}")
    print(f"--- Primeras 30 líneas ---")
    for i in range(li, min(li + 30, lf + 1)):
        print(f"  {i:6d}  {lines[i].rstrip()}")
