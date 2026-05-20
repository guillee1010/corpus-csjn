"""Inspección rápida de openers B1a candidatos."""
import sys
sys.path.insert(0, "scripts")
from pipeline.parser import (
    construir_bloque_desde_localizacion,
    detectar_apertura_en_bloque,
    cargar_localizados,
)

ids = [
    "329_p4242", "329_p4355", "329_p988", "330_p2915", "343_p956", "345_p1473",
    "331_p2240", "332_p752", "330_p748",
    "343_p300", "343_p473", "344_p997", "343_p720",
    "331_p436", "332_p1957", "331_p1013",
    "330_p4396", "344_p776",
]

KEYWORDS = [
    "por lo expresado", "por las razones", "por las consideraciones",
    "en atención", "en las condiciones", "por lo tanto",
    "oído el", "oido el", "que por ello", "que, de conformidad",
]

filas, _ = cargar_localizados("output/localizacion/fallos_localizados.csv")
for fila in filas:
    cid = fila["tomo"] + "_p" + fila["pagina_inicio"]
    if cid not in ids:
        continue
    li = int(fila["linea_inicio"])
    lf_raw = fila.get("linea_fin", "")
    lf = int(lf_raw) if lf_raw else li + 500
    fp = "corpus/" + fila["archivo"]
    lines = open(fp, encoding="utf-8").readlines()
    bloque = construir_bloque_desde_localizacion(lines, li, min(lf, len(lines) - 1))
    if not bloque:
        continue
    at, ar = detectar_apertura_en_bloque(bloque)
    if ar is None:
        continue
    print(f"=== {cid} (apertura rel {ar}, bloque {len(bloque)} líneas) ===")
    for k in range(ar, len(bloque)):
        s = bloque[k].strip()
        if not s:
            continue
        sl = s.lower()
        if any(kw in sl for kw in KEYWORDS):
            print(f"  L{k}: {s[:140]}")
    print()
