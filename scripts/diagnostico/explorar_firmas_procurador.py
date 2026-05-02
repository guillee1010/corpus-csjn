# explorar_firmas_procurador.py
# Explora las lineas que parecen firma de Procurador en un md.
# Output a archivo.

import re
from pathlib import Path

ARCHIVO = Path("markdowns_v2/LibroVol345-1.md")
OUTPUT = Path("firmas_procurador_345-1.txt")

# Linea termina con apellido de procurador (con o sin punto final)
RE_FIRMA = re.compile(
    r"^.{0,80}\b(Casal|Monti|Abramovich|Cosarin|Righi)\b\.?\s*$"
)

# Exclusiones: contextos de cita, no firma
RE_EXCLUSION = re.compile(
    r'"|Fallos:|fs\.|Procurador Fiscal|Ministerio P[uú]blico:|precedente'
)

lines = ARCHIVO.read_text(encoding="utf-8").split("\n")

matches_limpios = []
matches_excluidos = []

for i, ln in enumerate(lines, start=1):
    stripped = ln.strip()
    if RE_FIRMA.match(stripped):
        if RE_EXCLUSION.search(stripped):
            matches_excluidos.append((i, stripped))
        else:
            matches_limpios.append((i, stripped))

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(f"ARCHIVO: {ARCHIVO}\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"MATCHES LIMPIOS (probables firmas): {len(matches_limpios)}\n")
    f.write("-" * 70 + "\n")
    for n, t in matches_limpios:
        f.write(f"L{n}: {t}\n")
    f.write("\n")
    f.write(f"MATCHES EXCLUIDOS (descartados como cita/contexto): {len(matches_excluidos)}\n")
    f.write("-" * 70 + "\n")
    for n, t in matches_excluidos:
        f.write(f"L{n}: {t}\n")

print(f"Output escrito en: {OUTPUT}")
print(f"Matches limpios: {len(matches_limpios)}")
print(f"Matches excluidos: {len(matches_excluidos)}")
