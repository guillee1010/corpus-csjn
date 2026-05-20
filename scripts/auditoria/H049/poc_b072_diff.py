"""
PoC B072 — Diff parser nuevo (15 conjueces) vs baseline.

Uso:
  python scripts/auditoria/H049/poc_b072_diff.py

Requiere:
  - output/parser/csjn_casos.csv  (baseline H048)
  - parser.py patcheado ya copiado a scripts/pipeline/parser.py
  - Corpus y archivos de localización en su lugar habitual

Flujo:
  1. Corre el parser nuevo → output temporal.
  2. Carga baseline y nuevo CSV.
  3. Diffea caso a caso: n_jueces, voting_pattern, jueces, linea_fin_real.
  4. Clasifica en MEJORA / REGRESION / CAMBIO_NEUTRO.
  5. Exporta diff a output/auditoria/H049/poc_b072_diff.csv.
"""

import csv
import subprocess
import sys
from pathlib import Path

# ── Rutas ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent.parent  # repo root
BASELINE = ROOT / "output" / "parser" / "csjn_casos.csv"
PARSER   = ROOT / "scripts" / "pipeline" / "parser.py"
LOCALIZ  = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA     = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS   = ROOT / "corpus"

OUT_DIR  = ROOT / "output" / "auditoria" / "H049"
OUT_DIR.mkdir(parents=True, exist_ok=True)
NUEVO_CSV   = OUT_DIR / "csjn_casos_b072.csv"
NUEVO_VOTOS = OUT_DIR / "csjn_casos_b072_votos.csv"
DIFF_CSV    = OUT_DIR / "poc_b072_diff.csv"

# ── Paso 1: correr parser nuevo ─────────────────────────────────────────────
print("=== Paso 1: corriendo parser nuevo ===")
cmd = [
    sys.executable, str(PARSER),
    "--localizados", str(LOCALIZ),
    "--mapa", str(MAPA),
    "--corpus", str(CORPUS),
    "--output", str(NUEVO_CSV),
    "--output-votos", str(NUEVO_VOTOS),
]
import os
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
    "jueces_desconocidos", "linea_fin_real", "firma_raw",
]

diffs = []
for caso_id in sorted(base.keys()):
    if caso_id not in nuevo:
        diffs.append({
            "caso_id": caso_id, "tipo": "DESAPARECIDO",
            "campo": "", "base": "", "nuevo": "",
        })
        continue
    b = base[caso_id]
    n = nuevo[caso_id]
    for campo in CAMPOS_DIFF:
        vb = b.get(campo, "")
        vn = n.get(campo, "")
        if vb != vn:
            # Clasificar
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
            else:
                tipo = "CAMBIO"
            diffs.append({
                "caso_id": caso_id, "tipo": tipo,
                "campo": campo,
                "base": str(vb)[:200],
                "nuevo": str(vn)[:200],
            })

# Casos nuevos
for caso_id in sorted(nuevo.keys()):
    if caso_id not in base:
        diffs.append({
            "caso_id": caso_id, "tipo": "NUEVO",
            "campo": "", "base": "", "nuevo": "",
        })

# ── Paso 4: resumen y export ────────────────────────────────────────────────
from collections import Counter

tipos = Counter(d["tipo"] for d in diffs)
campos_afectados = Counter(d["campo"] for d in diffs if d["campo"])

print(f"\nTotal diferencias: {len(diffs)}")
print("\nPor tipo:")
for t, c in tipos.most_common():
    print(f"  {t}: {c}")
print("\nPor campo:")
for campo, c in campos_afectados.most_common():
    print(f"  {campo}: {c}")

# Regresiones detalladas
regresiones = [d for d in diffs if "REGRESION" in d["tipo"]]
if regresiones:
    print(f"\n⚠️  REGRESIONES: {len(regresiones)}")
    for r in regresiones[:20]:
        print(f"  {r['caso_id']} [{r['campo']}]: {r['base']} → {r['nuevo']}")
else:
    print("\n✅ Cero regresiones.")

# Mejoras detalladas
mejoras = [d for d in diffs if "MEJORA" in d["tipo"]]
print(f"\n📈 Mejoras: {len(mejoras)}")
for m in mejoras[:30]:
    print(f"  {m['caso_id']} [{m['campo']}]: {m['base']} → {m['nuevo']}")

# Export
with open(DIFF_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["caso_id", "tipo", "campo", "base", "nuevo"])
    writer.writeheader()
    for d in diffs:
        writer.writerow(d)
print(f"\nDiff exportado a {DIFF_CSV}")

# ── Paso 5: stats finales del nuevo CSV ─────────────────────────────────────
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
