# audit_b010.py — auditar casos donde wc_considerando fue a 0
import csv, sys
from pathlib import Path
sys.path.insert(0, "scripts/pipeline")
from parser import construir_bloque_desde_localizacion, zonificar_bloque, RE_CONSIDERANDO

casos_csv = Path("output/parser/csjn_casos.csv")
corpus_dir = Path("corpus")

targets = ["339_p444", "341_p929"]

for target in targets:
    row = None
    for r in csv.DictReader(open(casos_csv, encoding="utf-8")):
        if r["caso_id_canonico"] == target:
            row = r
            break
    if not row:
        print(f"{target}: no encontrado")
        continue

    source = row["source_file"]
    li = int(row["linea_inicio"])
    lfr = int(row["linea_fin_real"])
    lines = (corpus_dir / source).read_text(encoding="utf-8").splitlines()
    bloque = lines[li:lfr + 1]
    zonas, _ = zonificar_bloque(bloque)
    ld = {k for k, z in enumerate(zonas) if z == "dictamen"}

    print(f"=== {target} ({source}) ===")
    print(f"  bloque: {len(bloque)} lineas")
    print(f"  por_ello_text: {row['por_ello_text'][:80]}")
    print(f"  wc_considerando (post): {row['wc_considerando']}")
    print(f"  apertura_tipo: {row['apertura_tipo']}")
    print(f"  voting_pattern: {row['voting_pattern']}")

    # Buscar todos los matches de RE_CONSIDERANDO
    matches = []
    for k, ln in enumerate(bloque):
        if RE_CONSIDERANDO.search(ln.strip()):
            en_dict = "DICTAMEN" if k in ld else zonas[k]
            matches.append((k, en_dict, ln.strip()[:120]))

    print(f"  RE_CONSIDERANDO matches (total): {len(matches)}")
    for k, z, txt in matches:
        print(f"    L{k} [{z}]: {txt}")

    # Mostrar contexto alrededor del primer match fuera de dictamen
    matches_fallo = [(k, z, t) for k, z, t in matches if z != "DICTAMEN"]
    if matches_fallo:
        k0 = matches_fallo[0][0]
        print(f"  Contexto alrededor de L{k0}:")
        for j in range(max(0, k0 - 3), min(len(bloque), k0 + 4)):
            marca = ">>>" if j == k0 else "   "
            print(f"    {marca} L{j} [{zonas[j]}]: {bloque[j].strip()[:100]}")

    print()
