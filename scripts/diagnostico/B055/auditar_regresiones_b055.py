# H042 - auditar_regresiones_b055.py
# Muestra texto crudo del MD alrededor de la firma para cada regresion.
# Permite clasificar si la regresion es falsa (prod inflado) o real.
# Correr desde raiz del repo.

import csv, re, os
from pathlib import Path
from collections import OrderedDict

CSV_PROD = Path("output/parser/csjn_casos.csv")
CSV_FIX = Path("output/diagnostico/B055/csjn_casos_b055_fix.csv")
CSV_LOC = Path("output/localizacion/fallos_localizados.csv")
CORPUS = Path("corpus")

def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

prod = load_csv(CSV_PROD)
fix = load_csv(CSV_FIX)

# Cargar localizacion
with open(CSV_LOC, encoding="utf-8") as f:
    loc = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

# Identificar regresiones
regresiones = []
for caso_id in sorted(prod):
    rp, rf = prod[caso_id], fix.get(caso_id)
    if rf is None:
        continue
    nj_p = int(rp.get("n_jueces", 0))
    nj_f = int(rf.get("n_jueces", 0))
    firma_p = rp.get("firma_raw", "").strip()
    firma_f = rf.get("firma_raw", "").strip()
    if nj_f < nj_p:
        regresiones.append({"caso_id": caso_id, "nj_p": nj_p, "nj_f": nj_f,
                            "firma_p": firma_p, "firma_f": firma_f,
                            "vp_p": rp.get("voting_pattern", ""),
                            "vp_f": rf.get("voting_pattern", "")})
    elif firma_p.endswith(".") and not firma_f.endswith("."):
        regresiones.append({"caso_id": caso_id, "nj_p": nj_p, "nj_f": nj_f,
                            "firma_p": firma_p, "firma_f": firma_f,
                            "vp_p": rp.get("voting_pattern", ""),
                            "vp_f": rf.get("voting_pattern", "")})

print(f"Total regresiones a auditar: {len(regresiones)}")
print("=" * 80)

# Cache de archivos
file_cache = {}

for i, reg in enumerate(regresiones):
    caso_id = reg["caso_id"]
    lo = loc.get(caso_id)
    if lo is None:
        print(f"\n[{i+1}] {caso_id} — sin localizacion, skip")
        continue

    archivo = lo.get("archivo", "")
    linea_inicio = int(lo.get("linea_inicio", 0))
    linea_fin = lo.get("linea_fin_real", lo.get("linea_fin", ""))
    if linea_fin:
        linea_fin = int(linea_fin)
    else:
        linea_fin = linea_inicio + 200

    # Cargar archivo
    if archivo not in file_cache:
        ruta = CORPUS / archivo
        if not ruta.exists():
            print(f"\n[{i+1}] {caso_id} — archivo {archivo} no encontrado")
            continue
        file_cache[archivo] = ruta.read_text(encoding="utf-8").splitlines()
    lines = file_cache[archivo]

    # Buscar "Por ello" o variante en el bloque
    bloque = lines[linea_inicio:linea_fin + 1]
    por_ello_rel = None
    for k, ln in enumerate(bloque):
        s = ln.strip().lower()
        if s.startswith("por ello") or s.startswith("por lo expuesto"):
            por_ello_rel = k

    # Mostrar contexto: desde por_ello -5 hasta fin del bloque o +40
    if por_ello_rel is not None:
        ctx_start = max(0, por_ello_rel - 2)
        ctx_end = min(len(bloque), por_ello_rel + 50)
    else:
        # Sin por_ello, mostrar ultimas 50 lineas del bloque
        ctx_start = max(0, len(bloque) - 50)
        ctx_end = len(bloque)

    print(f"\n{'=' * 80}")
    print(f"[{i+1}/{len(regresiones)}] {caso_id}")
    print(f"  nj: {reg['nj_p']} -> {reg['nj_f']}  |  vp: {reg['vp_p']} -> {reg['vp_f']}")
    print(f"  PROD firma_tail: ...{reg['firma_p'][-80:]}")
    print(f"  FIX  firma_tail: ...{reg['firma_f'][-80:]}")
    print(f"  Archivo: {archivo}, lineas {linea_inicio}-{linea_fin}")
    print(f"  Por ello relativo: {por_ello_rel}")
    print(f"  --- Contexto MD (lineas {ctx_start}-{ctx_end} del bloque) ---")
    for k in range(ctx_start, ctx_end):
        abs_line = linea_inicio + k
        marker = ">>>" if k == por_ello_rel else "   "
        text = bloque[k].rstrip()
        # Marcar lineas que parecen firma
        if re.search(r"rosatti|rosenkrantz|lorenzetti|maqueda|highton|zaffaroni|petracchi|argibay|fayt|boggiano|belluscio", text, re.I):
            marker = "FIR"
        print(f"  {marker} {abs_line:6d} | {text}")
    print()
