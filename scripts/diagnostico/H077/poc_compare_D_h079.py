"""
PoC H079-D: comparación baseline vs nuevo parser (procedente regex + deja_sin_efecto).
Uso:
  1. Guardar snapshot del CSV actual:
       copy output\parser\csjn_casos.csv output\parser\csjn_casos_BASELINE_H079.csv
  2. Aplicar patches a parser.py (ver instrucciones de Claude)
  3. Correr parser:
       python scripts\pipeline\parser.py
  4. Correr este script:
       python scripts/diagnostico/poc_compare_D_h079.py
"""

import csv
import sys
from collections import Counter
from pathlib import Path

BASELINE = Path("output/parser/csjn_casos_BASELINE_H079.csv")
NUEVO    = Path("output/parser/csjn_casos.csv")

def load(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["caso_id_canonico"]] = r
    return rows

def main():
    if not BASELINE.exists():
        print(f"ERROR: no encontré {BASELINE}")
        print("Copiá el CSV actual antes de correr el parser:")
        print("  copy output\\parser\\csjn_casos.csv output\\parser\\csjn_casos_BASELINE_H079.csv")
        sys.exit(1)
    if not NUEVO.exists():
        print(f"ERROR: no encontré {NUEVO}")
        sys.exit(1)

    base = load(BASELINE)
    nuevo = load(NUEVO)

    # ── Integridad ──
    ids_base = set(base.keys())
    ids_nuevo = set(nuevo.keys())
    if ids_base != ids_nuevo:
        print(f"⚠ Diferencia de caso_ids: {len(ids_base)} vs {len(ids_nuevo)}")
        print(f"  Solo en baseline: {ids_base - ids_nuevo}")
        print(f"  Solo en nuevo:    {ids_nuevo - ids_base}")
    else:
        print(f"✓ Mismo set de {len(ids_base)} caso_ids")

    # ── Cambios en outcome ──
    cambios = []
    for cid in sorted(ids_base & ids_nuevo):
        ob = base[cid]["outcome"]
        on = nuevo[cid]["outcome"]
        if ob != on:
            cambios.append((cid, ob, on, base[cid]["tomo"]))

    print(f"\n{'='*70}")
    print(f"CAMBIOS EN OUTCOME: {len(cambios)}")
    print(f"{'='*70}")

    if not cambios:
        print("  Ningún cambio. ¿Aplicaste los patches?")
        return

    # ── Transiciones ──
    trans = Counter((ob, on) for _, ob, on, _ in cambios)
    print(f"\n── Transiciones ──")
    for (ob, on), n in trans.most_common():
        print(f"  {ob:25s} → {on:25s}  {n:>4}")

    # ── Regresiones (cambios NO esperados) ──
    esperadas = {
        ("otro", "procedente"),
        ("otro", "deja_sin_efecto"),
    }
    regresiones = [(cid, ob, on, t) for cid, ob, on, t in cambios
                   if (ob, on) not in esperadas]
    print(f"\n── Regresiones (transiciones no esperadas): {len(regresiones)} ──")
    for cid, ob, on, t in regresiones:
        pe = nuevo[cid].get("por_ello_text", "")[:150]
        print(f"  ⚠ T{t} {cid}: {ob} → {on}")
        print(f"    por_ello: {pe}")

    # ── Distribución nueva de outcomes ──
    fallos_b = [r for r in base.values() if r.get("tipo_entrada","").strip() == "fallo"]
    fallos_n = [r for r in nuevo.values() if r.get("tipo_entrada","").strip() == "fallo"]
    oc_b = Counter(r["outcome"] for r in fallos_b)
    oc_n = Counter(r["outcome"] for r in fallos_n)

    print(f"\n── Distribución de outcomes ──")
    print(f"  {'outcome':25s} {'baseline':>8} {'nuevo':>8} {'delta':>8}")
    print(f"  {'-'*55}")
    all_oc = sorted(set(list(oc_b.keys()) + list(oc_n.keys())),
                    key=lambda x: -(oc_n.get(x, 0)))
    for oc in all_oc:
        b = oc_b.get(oc, 0)
        n = oc_n.get(oc, 0)
        delta = n - b
        flag = " ←" if delta != 0 else ""
        print(f"  {oc:25s} {b:>8} {n:>8} {delta:>+8}{flag}")

    # ── Detalle de cada caso cambiado ──
    print(f"\n── Detalle de cambios ({len(cambios)} casos) ──")
    for cid, ob, on, t in cambios:
        pe = nuevo[cid].get("por_ello_text", "")[:200]
        print(f"  T{t} {cid}: {ob} → {on}")
        print(f"    {pe}")
        print()

    # ── Verificar is_merit_decision ──
    merit_check = []
    for cid, ob, on, t in cambios:
        im_b = base[cid].get("is_merit_decision", "")
        im_n = nuevo[cid].get("is_merit_decision", "")
        if im_b != im_n:
            merit_check.append((cid, im_b, im_n))
    if merit_check:
        print(f"\n── Cambios en is_merit_decision: {len(merit_check)} ──")
        for cid, ib, inn in merit_check[:10]:
            print(f"  {cid}: {ib} → {inn}")

    # ── Columnas que no deberían cambiar ──
    cols_estables = ["es_queja", "queja_resultado", "tipo_cuestion_federal",
                     "voting_pattern", "n_jueces", "word_count"]
    cols_existentes = [c for c in cols_estables if c in list(base.values())[0]]
    drifts = {}
    for cid in ids_base & ids_nuevo:
        for col in cols_existentes:
            vb = base[cid].get(col, "")
            vn = nuevo[cid].get(col, "")
            if vb != vn:
                drifts.setdefault(col, []).append(cid)

    print(f"\n── Drift en columnas estables ──")
    if not drifts:
        print("  ✓ Sin drift en columnas estables")
    else:
        for col, cids in drifts.items():
            print(f"  ⚠ {col}: {len(cids)} cambios")

if __name__ == "__main__":
    main()
