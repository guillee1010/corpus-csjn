# audit_b010_full.py — Auditoría completa B010
# Compara pre vs post en TODAS las columnas relevantes
import csv
from collections import Counter

PRE = "output/parser/csjn_casos_pre_b010.csv"
POST = "output/parser/csjn_casos.csv"

COLS_ANALITICAS = [
    "outcome", "voting_pattern", "n_jueces", "n_votos_svoto",
    "n_disidencias", "is_originaria", "is_full_bench",
    "is_merit_decision", "word_count", "wc_mayoria", "wc_votos",
    "wc_considerando", "wc_dictamen", "firma_raw",
    "apertura_tipo", "tipo_entrada", "sin_dispositivo",
]

def load(path):
    with open(path, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

pre = load(PRE)
post = load(POST)

# Solo fallos
ids_fallo = [k for k in post if post[k]["tipo_entrada"] == "fallo"]
print(f"Casos fallo: {len(ids_fallo)}")

# ── 1. Columnas con cambios ──────────────────────────────────────
print(f"\n{'='*70}")
print("1. COLUMNAS CON CAMBIOS")
print(f"{'='*70}")

col_diffs = {}
for col in COLS_ANALITICAS:
    if col not in list(post.values())[0]:
        continue
    cambios = []
    for k in ids_fallo:
        if k not in pre:
            continue
        v_pre = pre[k].get(col, "")
        v_post = post[k].get(col, "")
        if v_pre != v_post:
            cambios.append((k, v_pre, v_post))
    if cambios:
        col_diffs[col] = cambios
        print(f"\n  {col}: {len(cambios)} casos cambiaron")

# ── 2. Detalle de cambios en outcomes ─────────────────────────────
print(f"\n{'='*70}")
print("2. CAMBIOS EN OUTCOME")
print(f"{'='*70}")
if "outcome" in col_diffs:
    for k, v_pre, v_post in col_diffs["outcome"]:
        print(f"  {k}: {v_pre} -> {v_post}")
else:
    print("  Sin cambios")

# ── 3. Cambios en voting_pattern ──────────────────────────────────
print(f"\n{'='*70}")
print("3. CAMBIOS EN VOTING_PATTERN")
print(f"{'='*70}")
if "voting_pattern" in col_diffs:
    for k, v_pre, v_post in col_diffs["voting_pattern"]:
        print(f"  {k}: {v_pre} -> {v_post}")
else:
    print("  Sin cambios")

# ── 4. Cambios en is_originaria ───────────────────────────────────
print(f"\n{'='*70}")
print("4. CAMBIOS EN IS_ORIGINARIA")
print(f"{'='*70}")
if "is_originaria" in col_diffs:
    for k, v_pre, v_post in col_diffs["is_originaria"]:
        print(f"  {k}: {v_pre} -> {v_post}")
else:
    print("  Sin cambios")

# ── 5. Cambios en firma_raw ───────────────────────────────────────
print(f"\n{'='*70}")
print("5. CAMBIOS EN FIRMA_RAW")
print(f"{'='*70}")
if "firma_raw" in col_diffs:
    # Solo contar, no imprimir todas
    perdidas = [c for c in col_diffs["firma_raw"] if c[1] and not c[2]]
    ganadas = [c for c in col_diffs["firma_raw"] if not c[1] and c[2]]
    modificadas = [c for c in col_diffs["firma_raw"] if c[1] and c[2]]
    print(f"  Total cambios: {len(col_diffs['firma_raw'])}")
    print(f"  Firmas perdidas: {len(perdidas)}")
    print(f"  Firmas ganadas: {len(ganadas)}")
    print(f"  Firmas modificadas: {len(modificadas)}")
    if perdidas:
        print(f"  Perdidas (auditar!):")
        for k, v_pre, v_post in perdidas[:5]:
            print(f"    {k}: {v_pre[:80]} -> (vacio)")
else:
    print("  Sin cambios")

# ── 6. Cambios en n_votos_svoto / n_disidencias ──────────────────
print(f"\n{'='*70}")
print("6. CAMBIOS EN N_VOTOS / N_DISIDENCIAS")
print(f"{'='*70}")
for col in ["n_votos_svoto", "n_disidencias"]:
    if col in col_diffs:
        print(f"\n  {col}: {len(col_diffs[col])} casos")
        for k, v_pre, v_post in col_diffs[col][:10]:
            print(f"    {k}: {v_pre} -> {v_post}")
    else:
        print(f"  {col}: sin cambios")

# ── 7. wc_considerando: resumen y muestra ─────────────────────────
print(f"\n{'='*70}")
print("7. WC_CONSIDERANDO")
print(f"{'='*70}")
if "wc_considerando" in col_diffs:
    wc_cambios = col_diffs["wc_considerando"]
    red = [(k, int(p), int(q)) for k, p, q in wc_cambios if p and q and int(q) < int(p)]
    aum = [(k, int(p), int(q)) for k, p, q in wc_cambios if p and q and int(q) > int(p)]
    a0 = [(k, p, q) for k, p, q in wc_cambios if q == "0" or q == ""]
    print(f"  Total cambios: {len(wc_cambios)}")
    print(f"  Reducciones: {len(red)}")
    print(f"  Aumentos: {len(aum)}")
    print(f"  A cero: {len(a0)}")

    if red:
        red.sort(key=lambda x: x[1] - x[2], reverse=True)
        print(f"\n  Top 5 reducciones:")
        for k, p, q in red[:5]:
            print(f"    {k}: {p} -> {q} (delta {p-q})")

    if aum:
        aum.sort(key=lambda x: x[2] - x[1], reverse=True)
        print(f"\n  Top 5 aumentos:")
        for k, p, q in aum[:5]:
            print(f"    {k}: {p} -> {q} (delta +{q-p})")

# ── 8. Columnas que NO deberían cambiar ───────────────────────────
print(f"\n{'='*70}")
print("8. COLUMNAS QUE NO DEBERIAN CAMBIAR")
print(f"{'='*70}")
no_cambiar = ["n_jueces", "tipo_entrada", "apertura_tipo", "wc_dictamen"]
for col in no_cambiar:
    if col in col_diffs:
        print(f"  {col}: {len(col_diffs[col])} CAMBIOS (investigar!)")
        for k, v_pre, v_post in col_diffs[col][:3]:
            print(f"    {k}: {v_pre} -> {v_post}")
    else:
        print(f"  {col}: OK (sin cambios)")

# ── 9. Resumen ejecutivo ──────────────────────────────────────────
print(f"\n{'='*70}")
print("9. RESUMEN EJECUTIVO")
print(f"{'='*70}")
cols_con_cambio = list(col_diffs.keys())
cols_esperadas = {"wc_considerando", "word_count", "wc_mayoria"}
inesperadas = [c for c in cols_con_cambio if c not in cols_esperadas]
print(f"  Columnas con cambios: {cols_con_cambio}")
print(f"  Cambios esperados: {[c for c in cols_con_cambio if c in cols_esperadas]}")
print(f"  Cambios INESPERADOS: {inesperadas if inesperadas else 'ninguno'}")
