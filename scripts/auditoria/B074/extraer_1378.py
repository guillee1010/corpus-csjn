"""Extrae el bloque completo de 347_p1378 + contexto."""
import sys
from pathlib import Path

corpus = Path(sys.argv[1])
fp = corpus / "LibroVol347-2.md"
if not fp.exists():
    for f in corpus.rglob("LibroVol347-2.md"):
        fp = f; break

lines = fp.read_text(encoding='utf-8').split('\n')
li, lf, lfr = 7851, 7956, 7858

print(f"=== 347_p1378: li={li}, lf={lf}, lfr={lfr} (span={lfr-li}) ===")
print(f"=== case_name_indice: Robledo, María Alicia y Otros... ===")
print(f"=== token título: 'Robledo' ===\n")

# Bloque completo li-5 a lf+10, marcando posiciones clave
for k in range(max(0, li-5), min(len(lines), lf+10)):
    markers = []
    if k == li: markers.append("◄ li")
    if k == lfr: markers.append("◄ lfr_base")
    if k == lf: markers.append("◄ lf")
    # Buscar "Robledo" en la línea
    if 'obledo' in lines[k].lower(): markers.append("◄◄ ROBLEDO")
    marker = "  " + " ".join(markers) if markers else ""
    print(f"{k:6d} | {lines[k]}{marker}")
