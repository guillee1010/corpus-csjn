# H042 - commit_b055_verify.py
# Verifica que el output del productivo parcheado coincide con el paralelo.
# Correr desde raiz del repo, DESPUES de correr el pipeline.

import csv
from pathlib import Path

CSV_PROD = Path("output/parser/csjn_casos.csv")
CSV_FIX = Path("output/diagnostico/B055/csjn_casos_b055_fix.csv")

def load(path):
    with open(path, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

prod = load(CSV_PROD)
fix = load(CSV_FIX)

print(f"Productivo: {len(prod)} casos")
print(f"Paralelo:   {len(fix)} casos")

if len(prod) != len(fix):
    print("ERROR: distinto numero de casos")
    raise SystemExit(1)

# Comparar campo por campo
campos = ["firma_raw", "n_jueces", "voting_pattern",
          "jueces_mayoria", "jueces_disidencia", "jueces_voto"]
diffs = 0
for caso_id in sorted(prod):
    rp, rf = prod[caso_id], fix.get(caso_id)
    if rf is None:
        print(f"  FALTA en paralelo: {caso_id}")
        diffs += 1
        continue
    for c in campos:
        if rp.get(c, "") != rf.get(c, ""):
            print(f"  DIFF {caso_id}.{c}: prod={rp.get(c,'')[:60]} fix={rf.get(c,'')[:60]}")
            diffs += 1
            break

if diffs == 0:
    print("\nVERIFICACION OK: productivo y paralelo coinciden en todos los campos de firma.")
    print("\nProceder con commit:")
    print("  git add scripts/pipeline/parser.py output/parser/csjn_casos.csv output/parser/csjn_casos_votos.csv")
    print('  git commit -m "fix B055: collect_firma_lines con guarda de texto acumulado')
    print()
    print('Remover max_lines=40, guarda por apellido+punto en texto acumulado,')
    print('tolerancia a 1 linea vacia intercalada. 1262 mejoras, 0 regresiones reales.')
    print('firma_raw limpia (sin basura post-firma), 16 casos con n_jueces mejorado,')
    print('desconocidos Ricardo Luis 196->7, Juan Carlos 64->0, CARMEN M. 52->6."')
    print()
    print("  git push")
else:
    print(f"\nDIFERENCIAS: {diffs}. Revisar antes de commitear.")
