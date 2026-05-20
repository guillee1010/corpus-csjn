"""
PoC B074 — Guarda posicional en firma_actual de detectar_fin_real.

No acepta firma encontrada antes de la primera apertura/fecha del bloque.
Previene que firma del caso anterior (por superposición de páginas) se
capture como firma del caso actual.

Uso:
  python scripts/auditoria/H049/poc_b074_diff.py

Requiere:
  - parser.py ya patcheado con B074 en scripts/pipeline/parser.py
  - output/parser/csjn_casos.csv como baseline (post-B072)
"""

import csv
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
BASELINE = ROOT / "output" / "parser" / "csjn_casos.csv"
PARSER   = ROOT / "scripts" / "pipeline" / "parser.py"
LOCALIZ  = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA     = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS   = ROOT / "corpus"

OUT_DIR  = ROOT / "output" / "auditoria" / "H049"
OUT_DIR.mkdir(parents=True, exist_ok=True)
NUEVO_CSV   = OUT_DIR / "csjn_casos_b074.csv"
NUEVO_VOTOS = OUT_DIR / "csjn_casos_b074_votos.csv"
DIFF_CSV    = OUT_DIR / "poc_b074_diff.csv"

# ── Paso 1: correr parser nuevo ─────────────────────────────────────────────
print("=== Paso 1: corriendo parser con B074 ===")
cmd = [
    sys.executable, str(PARSER),
    "--localizados", str(LOCALIZ),
    "--mapa", str(MAPA),
    "--corpus", str(CORPUS),
    "--output", str(NUEVO_CSV),
    "--output-votos", str(NUEVO_VOTOS),
]
env = os.environ.copy()
env["PYTHONUTF8"] = "1"
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
if result.returncode != 0:
    print("ERROR corriendo parser:")
    print(result.stderr[-500:])
    sys.exit(1)

# ── Paso 2: cargar ambos CSV ────────────────────────────────────────────────
print("\n=== Paso 2: cargando CSVs ===")


def cargar(path):
    with open(path, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}


base = cargar(BASELINE)
nuevo = cargar(NUEVO_CSV)
print(f"Baseline: {len(base)} casos")
print(f"Nuevo:    {len(nuevo)} casos")

# ── Paso 3: diff ────────────────────────────────────────────────────────────
print("\n=== Paso 3: diffing ===")

CAMPOS_DIFF = [
    "voting_pattern", "n_jueces", "jueces", "jueces_conocidos",
    "jueces_desconocidos", "linea_fin_real", "firma_raw", "pista_fin",
]

diffs = []
for caso_id in sorted(base.keys()):
    if caso_id not in nuevo:
        diffs.append({"caso_id": caso_id, "tipo": "DESAPARECIDO",
                      "campo": "", "base": "", "nuevo": ""})
        continue
    b = base[caso_id]
    n = nuevo[caso_id]
    for campo in CAMPOS_DIFF:
        vb = b.get(campo, "")
        vn = n.get(campo, "")
        if vb != vn:
            if campo == "n_jueces":
                nb, nn = int(vb or 0), int(vn or 0)
                if nn > nb and b.get("voting_pattern") == "sin_firma":
                    tipo = "MEJORA"
                elif nn > nb:
                    tipo = "MEJORA_JUECES"
                elif nn < nb:
                    tipo = "REGRESION"
                else:
                    tipo = "CAMBIO"
            elif campo == "voting_pattern":
                if vb == "sin_firma" and vn != "sin_firma":
                    tipo = "MEJORA"
                elif vb != "sin_firma" and vn == "sin_firma":
                    tipo = "REGRESION"
                else:
                    tipo = "CAMBIO_VP"
            elif campo == "linea_fin_real":
                tipo = "LFR_CAMBIO"
            elif campo == "pista_fin":
                tipo = "PISTA_CAMBIO"
            else:
                tipo = "CAMBIO"
            diffs.append({"caso_id": caso_id, "tipo": tipo,
                          "campo": campo,
                          "base": str(vb)[:200], "nuevo": str(vn)[:200]})

for caso_id in sorted(nuevo.keys()):
    if caso_id not in base:
        diffs.append({"caso_id": caso_id, "tipo": "NUEVO",
                      "campo": "", "base": "", "nuevo": ""})

# ── Paso 4: resumen ─────────────────────────────────────────────────────────
from collections import Counter

tipos = Counter(d["tipo"] for d in diffs)
campos = Counter(d["campo"] for d in diffs if d["campo"])

print(f"\nTotal diferencias: {len(diffs)}")
print("\nPor tipo:")
for t, c in tipos.most_common():
    print(f"  {t}: {c}")
print("\nPor campo:")
for campo, c in campos.most_common():
    print(f"  {campo}: {c}")

regresiones = [d for d in diffs if "REGRESION" in d["tipo"]]
if regresiones:
    print(f"\n⚠️  REGRESIONES: {len(regresiones)}")
    for r in regresiones[:20]:
        print(f"  {r['caso_id']} [{r['campo']}]: {r['base']} → {r['nuevo']}")
else:
    print("\n✅ Cero regresiones.")

mejoras = [d for d in diffs if "MEJORA" in d["tipo"]]
print(f"\n📈 Mejoras: {len(mejoras)}")
for m in mejoras[:30]:
    print(f"  {m['caso_id']} [{m['campo']}]: {m['base']} → {m['nuevo']}")

# Cambios de pista_fin (indica que la guarda redirigió)
pista_cambios = [d for d in diffs if d["tipo"] == "PISTA_CAMBIO"]
if pista_cambios:
    print(f"\n🔄 Cambios de pista_fin: {len(pista_cambios)}")
    for p in pista_cambios:
        print(f"  {p['caso_id']}: {p['base']} → {p['nuevo']}")

# Export
with open(DIFF_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["caso_id", "tipo", "campo", "base", "nuevo"])
    writer.writeheader()
    for d in diffs:
        writer.writerow(d)
print(f"\nDiff exportado a {DIFF_CSV}")

# ── Paso 5: stats finales ──────────────────────────────────────────────────
sf_base = sum(1 for r in base.values()
              if r.get("voting_pattern") == "sin_firma"
              and r.get("tipo_entrada") == "fallo")
sf_nuevo = sum(1 for r in nuevo.values()
               if r.get("voting_pattern") == "sin_firma"
               and r.get("tipo_entrada") == "fallo")
votos_base = sum(1 for _ in open(
    BASELINE.parent / "csjn_casos_votos.csv", encoding="utf-8")) - 1
votos_nuevo = sum(1 for _ in open(NUEVO_VOTOS, encoding="utf-8")) - 1

print(f"\n=== Stats finales ===")
print(f"sin_firma (fallos): {sf_base} → {sf_nuevo} (Δ{sf_nuevo - sf_base})")
print(f"votos:              {votos_base} → {votos_nuevo} (Δ{votos_nuevo - votos_base})")
