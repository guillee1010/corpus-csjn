r"""
poc_b082_compare.py — Compara baseline vs output con fix B082.

Uso:
  1. Copiar baseline:
       copy output\parser\csjn_casos.csv output\parser\csjn_casos_pre_b082.csv
  2. Aplicar patch B082 a parser.py (ver instrucciones en PATCH).
  3. Correr parser:
       python scripts\pipeline\parser.py
  4. Correr este script:
       python poc_b082_compare.py
"""

import pandas as pd
from pathlib import Path
import sys

BASE = Path("output/parser")
OLD = BASE / "csjn_casos_pre_b082.csv"
NEW = BASE / "csjn_casos.csv"

if not OLD.exists():
    print(f"ERROR: no existe {OLD}")
    print("  Copia el CSV actual antes de aplicar el patch:")
    print(r"  copy output\parser\csjn_casos.csv output\parser\csjn_casos_pre_b082.csv")
    sys.exit(1)

old = pd.read_csv(OLD)
new = pd.read_csv(NEW)

key = "caso_id_canonico"
fallos_old = old[old["tipo_entrada"] == "fallo"].set_index(key)
fallos_new = new[new["tipo_entrada"] == "fallo"].set_index(key)

common = fallos_old.index.intersection(fallos_new.index)
print(f"Fallos en baseline: {len(fallos_old)}")
print(f"Fallos en nuevo:    {len(fallos_new)}")
print(f"En común:           {len(common)}")
print()

# ── 1. Outcome changes ──────────────────────────────────────────────
outcome_diff = []
for cid in common:
    o_old = fallos_old.loc[cid, "outcome"]
    o_new = fallos_new.loc[cid, "outcome"]
    if o_old != o_new:
        outcome_diff.append({
            "caso_id": cid,
            "outcome_old": o_old,
            "outcome_new": o_new,
            "vp": fallos_new.loc[cid, "voting_pattern"],
            "n_dis": fallos_new.loc[cid, "n_disidencias"],
            "n_svoto": fallos_new.loc[cid, "n_votos_svoto"],
            "pista_fin": fallos_new.loc[cid, "pista_fin"],
            "pet_old": str(fallos_old.loc[cid, "por_ello_text"])[:120],
            "pet_new": str(fallos_new.loc[cid, "por_ello_text"])[:120],
        })

print(f"=== OUTCOME CHANGES: {len(outcome_diff)} ===")
if outcome_diff:
    df_diff = pd.DataFrame(outcome_diff)
    # Resumen
    print("\nTransiciones:")
    for _, r in df_diff.iterrows():
        print(f"  {r['caso_id']}: {r['outcome_old']} → {r['outcome_new']}  "
              f"(vp={r['vp']}, dis={r['n_dis']}, svoto={r['n_svoto']})")
        if r["pet_old"] != r["pet_new"]:
            print(f"    pet_old: {r['pet_old']}")
            print(f"    pet_new: {r['pet_new']}")
    print()

    # Clasificar: mejora / regresión / neutro
    MERIT = {"hace_lugar", "procedente", "revoca", "confirma", "nulidad",
             "competencia", "abstracto", "originaria", "desistimiento",
             "desestima", "mal_concedido", "inadmisible_280",
             "inadmisible_acordada_4"}
    mejoras = [r for r in outcome_diff
               if r["outcome_old"] in ("otro", "sin_dispositivo")
               and r["outcome_new"] in MERIT]
    regresiones = [r for r in outcome_diff
                   if r["outcome_old"] in MERIT
                   and r["outcome_new"] in ("otro", "sin_dispositivo")]
    neutros = [r for r in outcome_diff
               if r not in mejoras and r not in regresiones]
    print(f"  Probables mejoras:     {len(mejoras)}")
    print(f"  Probables regresiones: {len(regresiones)}")
    print(f"  Neutros/inciertos:     {len(neutros)}")
print()

# ── 2. por_ello_text changes ────────────────────────────────────────
pet_changes = 0
for cid in common:
    p_old = str(fallos_old.loc[cid, "por_ello_text"])[:300]
    p_new = str(fallos_new.loc[cid, "por_ello_text"])[:300]
    if p_old != p_new:
        pet_changes += 1
print(f"=== POR_ELLO_TEXT CHANGES: {pet_changes} ===")
print()

# ── 3. wc_considerando changes ──────────────────────────────────────
wc_changes = []
for cid in common:
    wc_old = fallos_old.loc[cid, "wc_considerando"]
    wc_new = fallos_new.loc[cid, "wc_considerando"]
    if wc_old != wc_new:
        wc_changes.append({
            "caso_id": cid,
            "wc_old": wc_old,
            "wc_new": wc_new,
            "delta": wc_new - wc_old,
        })
print(f"=== WC_CONSIDERANDO CHANGES: {len(wc_changes)} ===")
if wc_changes:
    deltas = [w["delta"] for w in wc_changes]
    print(f"  Δ promedio: {sum(deltas)/len(deltas):.0f}")
    print(f"  Δ min:      {min(deltas)}")
    print(f"  Δ max:      {max(deltas)}")
    # Los que más bajan (= más leakage removido)
    wc_changes.sort(key=lambda x: x["delta"])
    print("\n  Top 10 mayor reducción (leakage removido):")
    for w in wc_changes[:10]:
        print(f"    {w['caso_id']}: {w['wc_old']} → {w['wc_new']} (Δ={w['delta']})")
print()

# ── 4. Outcome distribution comparison ─────────────────────────────
print("=== OUTCOME DISTRIBUTION ===")
dist_old = fallos_old["outcome"].value_counts().sort_index()
dist_new = fallos_new["outcome"].value_counts().sort_index()
all_outcomes = sorted(set(dist_old.index) | set(dist_new.index))
print(f"{'outcome':<25} {'baseline':>8} {'nuevo':>8} {'Δ':>6}")
print("-" * 50)
for o in all_outcomes:
    v_old = dist_old.get(o, 0)
    v_new = dist_new.get(o, 0)
    d = v_new - v_old
    flag = " ←" if d != 0 else ""
    print(f"{o:<25} {v_old:>8} {v_new:>8} {d:>+6}{flag}")
print()

# ── 5. Voting pattern distribution (sanity check) ──────────────────
print("=== VOTING PATTERN (sanity — no debería cambiar) ===")
vp_old = fallos_old["voting_pattern"].value_counts().sort_index()
vp_new = fallos_new["voting_pattern"].value_counts().sort_index()
all_vp = sorted(set(vp_old.index) | set(vp_new.index))
changed = False
for v in all_vp:
    vo = vp_old.get(v, 0)
    vn = vp_new.get(v, 0)
    if vo != vn:
        print(f"  {v}: {vo} → {vn}")
        changed = True
if not changed:
    print("  Sin cambios ✓")
print()

# ── 6. is_originaria check ──────────────────────────────────────────
orig_changes = 0
for cid in common:
    if fallos_old.loc[cid, "is_originaria"] != fallos_new.loc[cid, "is_originaria"]:
        orig_changes += 1
print(f"=== IS_ORIGINARIA CHANGES: {orig_changes} ===")
