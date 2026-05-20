# H042 - commit_b055.py
# Procedimiento de commit del fix B055.
# 1. Snapshot de CSVs productivos
# 2. Parchear parser.py productivo
# 3. Correr pipeline
# 4. Verificar contra paralelo
# 5. Instrucciones de commit
# Correr desde raiz del repo.

import shutil, csv, sys
from pathlib import Path

PARSER_PROD = Path("scripts/pipeline/parser.py")
PARSER_FIX = Path("scripts/diagnostico/H055/parser_b055_fix.py")
CSV_PROD = Path("output/parser/csjn_casos.csv")
CSV_VOTOS_PROD = Path("output/parser/csjn_casos_votos.csv")
CSV_FIX = Path("output/diagnostico/B055/csjn_casos_b055_fix.csv")
CSV_VOTOS_FIX = Path("output/diagnostico/B055/csjn_casos_b055_fix_votos.csv")
SNAP_DIR = Path("output/diagnostico/B055/snapshots")

# --- Paso 1: Snapshots ---
print("=== Paso 1: Snapshots ===")
SNAP_DIR.mkdir(parents=True, exist_ok=True)
for f in [CSV_PROD, CSV_VOTOS_PROD, PARSER_PROD]:
    dst = SNAP_DIR / f"snapshot_pre_b055_{f.name}"
    if dst.exists():
        print(f"  Ya existe: {dst.name}")
    else:
        shutil.copy2(f, dst)
        print(f"  Copiado: {f} -> {dst}")

# --- Paso 2: Parchear parser productivo ---
print("\n=== Paso 2: Parchear parser.py productivo ===")

src_prod = PARSER_PROD.read_text(encoding="utf-8")
src_fix = PARSER_FIX.read_text(encoding="utf-8")

# Extraer _RE_FIRMA_COMPLETA del fix
re_const_start = src_fix.find("_RE_FIRMA_COMPLETA = re.compile(")
if re_const_start == -1:
    print("ERROR: no encontre _RE_FIRMA_COMPLETA en parser fix")
    sys.exit(1)
# Encontrar el cierre del re.compile(...)
re_const_end = src_fix.find("\n)\n", re_const_start)
if re_const_end == -1:
    print("ERROR: no encontre cierre de _RE_FIRMA_COMPLETA")
    sys.exit(1)
re_const_end += 3  # incluir "\n)\n"
re_const_block = src_fix[re_const_start:re_const_end]

# Extraer collect_firma_lines del fix
func_marker = "def collect_firma_lines("
fix_func_start = src_fix.find(func_marker, re_const_end)
if fix_func_start == -1:
    print("ERROR: no encontre collect_firma_lines en parser fix")
    sys.exit(1)
# Encontrar fin de la funcion (siguiente def o linea no indentada no vacia)
fix_lines = src_fix[fix_func_start:].splitlines(keepends=True)
fix_func_end_rel = len(fix_lines)
for i, ln in enumerate(fix_lines):
    if i == 0:
        continue
    stripped = ln.strip()
    if stripped and not ln[0].isspace():
        fix_func_end_rel = i
        break
fix_func_text = "".join(fix_lines[:fix_func_end_rel])

# Encontrar y reemplazar en productivo
prod_func_start = src_prod.find(func_marker)
if prod_func_start == -1:
    print("ERROR: no encontre collect_firma_lines en parser productivo")
    sys.exit(1)
prod_lines = src_prod[prod_func_start:].splitlines(keepends=True)
prod_func_end_rel = len(prod_lines)
for i, ln in enumerate(prod_lines):
    if i == 0:
        continue
    stripped = ln.strip()
    if stripped and not ln[0].isspace():
        prod_func_end_rel = i
        break
prod_func_text = "".join(prod_lines[:prod_func_end_rel])

# Reemplazar: insertar constante + nueva funcion
patched = src_prod[:prod_func_start] + re_const_block + "\n" + fix_func_text + src_prod[prod_func_start + len(prod_func_text):]

# Verificar que no se duplico _RE_FIRMA_COMPLETA
if patched.count("_RE_FIRMA_COMPLETA = re.compile(") > 1:
    print("ERROR: _RE_FIRMA_COMPLETA duplicada")
    sys.exit(1)

PARSER_PROD.write_text(patched, encoding="utf-8")
print(f"  parser.py parcheado OK")

# --- Paso 3: Correr pipeline ---
print("\n=== Paso 3: Correr pipeline ===")
print("  Ejecutar manualmente:")
print(f"  python {PARSER_PROD} --localizados output/localizacion/fallos_localizados.csv --mapa output/mapa/mapa_paginas.csv --corpus corpus")
print()
print("  Despues correr:")
print("  python scripts/diagnostico/H055/commit_b055_verify.py")
