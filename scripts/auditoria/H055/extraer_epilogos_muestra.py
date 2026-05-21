"""Extrae epilogos de los 20 casos muestra + casos problematicos."""
import csv, random
from pathlib import Path

ZONAS_CSV  = Path("output/parser/csjn_casos_zonas.csv")
CASOS_CSV  = Path("output/parser/csjn_casos.csv")
CORPUS_DIR = Path("corpus")

# Cargar caso metadata
caso_meta = {}
with open(CASOS_CSV, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        caso_meta[r["caso_id_canonico"]] = r

# Cargar zonas
from collections import defaultdict
zonas_por_caso = defaultdict(list)
with open(ZONAS_CSV, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        zonas_por_caso[r["caso_id_canonico"]].append(r)

# Cache de archivos
_cache = {}
def get_lines(sf):
    if sf not in _cache:
        p = CORPUS_DIR / sf
        _cache[sf] = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
    return _cache[sf]

# 20 random (seed=55) + casos problematicos
random.seed(55)
fallos = [r for r in caso_meta.values() if r.get("tipo_entrada","fallo")=="fallo"]
muestra_ids = [r["caso_id_canonico"] for r in random.sample(fallos, 20)]

# Casos problematicos: top residuo, residuo->dispositivo, residuo->firma
PROB = [
    "329_p244", "329_p326", "329_p437", "329_p553", "329_p792",  # residuo->disp/firma
    "348_p1435", "329_p5683", "333_p1650",                        # top residuo
    "330_p3853", "332_p2559",                                      # mixed/segun_su_voto largos
]
todos = list(dict.fromkeys(muestra_ids + PROB))  # dedup preservando orden

for cid in todos:
    meta = caso_meta.get(cid)
    if not meta:
        continue
    sf = meta["source_file"]
    li = int(meta["linea_inicio"])
    lines = get_lines(sf)
    if not lines:
        continue

    segs = zonas_por_caso.get(cid, [])
    epilogos = [s for s in segs if s["zona"] == "epilogo"]
    residuos = [s for s in segs if s["zona"] == "residuo_caso_anterior"]

    marcador = ""
    if cid in PROB:
        marcador = " *** PROBLEMATICO ***"

    print(f"\n{'='*70}")
    print(f"CASO: {cid} (tomo {meta['tomo']}, {meta['voting_pattern']}, "
          f"wc={meta['word_count']}){marcador}")
    print(f"{'='*70}")

    # Mostrar residuo si existe
    if residuos:
        print(f"\n--- RESIDUO CASO ANTERIOR ({len(residuos)} seg) ---")
        for seg in residuos[:2]:  # max 2 segmentos
            ini = int(seg["linea_ini"]) + li
            fin = int(seg["linea_fin"]) + li
            for k in range(ini, min(fin + 1, len(lines))):
                ln = lines[k].rstrip()
                if ln.strip():
                    print(f"  {k:>6} | {ln[:100]}")
            if int(seg["n_lineas"]) > 10:
                print(f"  ... ({seg['n_lineas']} lineas, {seg['wc']} wc)")

    # Mostrar epilogo
    if epilogos:
        print(f"\n--- EPILOGO ({len(epilogos)} seg, "
              f"{sum(int(s['wc']) for s in epilogos)} wc) ---")
        for seg in epilogos:
            ini = int(seg["linea_ini"]) + li
            fin = int(seg["linea_fin"]) + li
            for k in range(ini, min(fin + 1, len(lines))):
                ln = lines[k].rstrip()
                if ln.strip():
                    print(f"  {k:>6} | {ln[:100]}")
    else:
        print("\n  (sin epilogo)")

    # Mostrar ultimas 3 lineas del bloque (para ver si hay arrastre)
    lf = int(meta["linea_fin_real"])
    print(f"\n--- ULTIMAS 3 LINEAS (fin_real={lf}) ---")
    for k in range(max(li, lf - 2), min(lf + 1, len(lines))):
        ln = lines[k].rstrip()
        print(f"  {k:>6} | {ln[:100]}")
