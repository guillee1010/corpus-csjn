"""validar_fix.py — Muestra antes/despues de los 31 casos mejorados."""
import csv
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
PROD = REPO / "output" / "parser" / "csjn_casos.csv"
FIX = REPO / "output" / "diagnostico" / "H036" / "csjn_casos_h036.csv"

with open(PROD, encoding="utf-8") as f:
    prod = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}
with open(FIX, encoding="utf-8") as f:
    fix = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

mejoras = []
neutros = []
regresiones = []

for cid in sorted(prod):
    p, f = prod[cid], fix[cid]
    p_nj, f_nj = int(p["n_jueces"]), int(f["n_jueces"])
    p_vp, f_vp = p["voting_pattern"], f["voting_pattern"]
    p_oc, f_oc = p["outcome"], f["outcome"]
    if p_nj == f_nj and p_vp == f_vp and p_oc == f_oc:
        continue
    delta = f_nj - p_nj
    row = (cid, p_nj, f_nj, p_vp, f_vp, p_oc, f_oc, p, f)
    if delta > 0 or (p_vp == "sin_firma" and f_vp != "sin_firma"):
        mejoras.append(row)
    elif delta < 0 or (p_vp != "sin_firma" and f_vp == "sin_firma"):
        regresiones.append(row)
    else:
        neutros.append(row)

sep = "=" * 100
print(sep)
print(f"  VALIDACION FIX H036: backstop dictamen con RE_APERTURA")
print(f"  Mejoras: {len(mejoras)}   Regresiones: {len(regresiones)}   Neutros: {len(neutros)}")
print(sep)

print(f"\n{'CASO':<14} {'NJ':>3}->{'NJ':>3} {'VOTING PATTERN':<28} {'OUTCOME':<22} FIRMA (primeros 90 chars)")
print("-" * 100)
for cid, pnj, fnj, pvp, fvp, poc, foc, p, f in mejoras:
    print(f"{cid:<14} {pnj:>3}->{fnj:>3} {pvp:<13}->{fvp:<13} {poc:<10}->{foc:<10} {f['firma_raw'][:90]}")

if neutros:
    print(f"\n--- Cambios neutros ---")
    for cid, pnj, fnj, pvp, fvp, poc, foc, p, f in neutros:
        print(f"{cid:<14} {pnj:>3}->{fnj:>3} {pvp:<13}->{fvp:<13} {poc:<10}->{foc:<10}")
        if p["por_ello_text"] != f["por_ello_text"]:
            print(f"  ANTES: {p['por_ello_text'][:100]}")
            print(f"  AHORA: {f['por_ello_text'][:100]}")

if regresiones:
    print(f"\n*** REGRESIONES ***")
    for cid, pnj, fnj, pvp, fvp, poc, foc, p, f in regresiones:
        print(f"{cid:<14} {pnj:>3}->{fnj:>3} {pvp:<13}->{fvp:<13} {poc:<10}->{foc:<10}")
        print(f"  ANTES firma: {p['firma_raw'][:100]}")
        print(f"  AHORA firma: {f['firma_raw'][:100]}")

print(f"\n{sep}")
print(f"  VEREDICTO: {'LISTO PARA COMMIT' if not regresiones else 'HAY REGRESIONES - NO COMMITEAR'}")
print(sep)
