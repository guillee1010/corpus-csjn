"""
Conteo de aperturas vs catálogo — ¿faltan fallos?

Cuenta "FALLO DE LA CORTE SUPREMA" / "SENTENCIA DE LA CORTE SUPREMA"
en cada .md del corpus y compara contra entradas del catálogo.

Uso:
  python scripts/auditoria/H051/conteo_aperturas_h051.py
"""

import re
import csv
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CORPUS_DIR = REPO_ROOT / "corpus"
LOCALIZADOS = REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"

RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I)

# Cargar catálogo
with open(LOCALIZADOS, encoding="utf-8") as f:
    cat = list(csv.DictReader(f))

cat_por_archivo = Counter(r["archivo"] for r in cat if r["archivo"])
archivos_catalogo = sorted(set(r["archivo"] for r in cat if r["archivo"]))

print(f"{'Archivo':<30} {'Aperturas':>10} {'Catálogo':>10} {'Diff':>6}  Nota")
print("-" * 80)

total_apert = 0
total_cat = 0
diffs = []

for archivo in archivos_catalogo:
    path = CORPUS_DIR / archivo
    if not path.exists():
        print(f"{archivo:<30} {'???':>10} {cat_por_archivo[archivo]:>10} {'':>6}  ARCHIVO NO ENCONTRADO")
        continue

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    n_apert = sum(1 for ln in lines if RE_APERTURA.match(ln.strip()))
    n_cat = cat_por_archivo[archivo]
    diff = n_apert - n_cat
    total_apert += n_apert
    total_cat += n_cat

    nota = ""
    if diff > 0:
        nota = f"← {diff} aperturas sin entrada en catálogo"
        diffs.append((archivo, diff, n_apert, n_cat))
    elif diff < 0:
        nota = f"← {-diff} entradas sin apertura (sumarios/remisiones)"

    flag = f"{diff:>+6}" if diff != 0 else f"{'ok':>6}"
    print(f"{archivo:<30} {n_apert:>10} {n_cat:>10} {flag}  {nota}")

print("-" * 80)
print(f"{'TOTAL':<30} {total_apert:>10} {total_cat:>10} {total_apert - total_cat:>+6}")

if diffs:
    print(f"\n⚠ Hay {sum(d for _, d, _, _ in diffs)} aperturas en el corpus sin entrada en el catálogo.")
    print(f"  Esto podría indicar fallos no catalogados.")
else:
    print(f"\n✓ No hay aperturas sobrantes. El catálogo cubre todas las aperturas del corpus.")

if total_cat > total_apert:
    print(f"\n  {total_cat - total_apert} entradas del catálogo no tienen apertura en el corpus.")
    print(f"  Estas son probablemente sumarios editoriales, remisiones a precedentes,")
    print(f"  o resoluciones sin el marcador 'FALLO DE LA CORTE SUPREMA'.")
