"""
Mide el impacto del fix propuesto a RE_VOTO_HDR comparando, sobre los .md
del corpus disponible, cuántas líneas matchean el regex CON el fix pero
NO matchean el regex viejo.

Cada match nuevo es un voto separado que el parser actual NO está
detectando (queda en wc_mayoria contaminando el word count).
"""

import re
from pathlib import Path

# Regex actual del parser (csjnv17, líneas 142-146)
RE_VIEJO = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I,
)

# Regex propuesto: agrega "l[ao]s?" como tercera alternativa de artículo,
# para cubrir "Voto la señora" (sin "de" antes del artículo)
RE_NUEVO = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?|l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I,
)

CORPUS = Path("/home/claude/corpus")

print(f"Archivos en corpus: {sorted(p.name for p in CORPUS.glob('*.md'))}\n")

total_viejo = 0
total_nuevo = 0
nuevos_por_archivo = {}

for archivo in sorted(CORPUS.glob("*.md")):
    text = archivo.read_text(encoding="utf-8")
    lines = text.split("\n")
    n_viejo = 0
    n_nuevo = 0
    nuevos_lineas = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        m_v = RE_VIEJO.match(s)
        m_n = RE_NUEVO.match(s)
        if m_v:
            n_viejo += 1
        if m_n:
            n_nuevo += 1
        if m_n and not m_v:
            nuevos_lineas.append((i, s))
    total_viejo += n_viejo
    total_nuevo += n_nuevo
    nuevos_por_archivo[archivo.name] = nuevos_lineas
    print(f"{archivo.name}:")
    print(f"  matches regex viejo: {n_viejo}")
    print(f"  matches regex nuevo: {n_nuevo}")
    print(f"  diff (votos hoy perdidos): {n_nuevo - n_viejo}")
    if nuevos_lineas:
        print(f"  ejemplos de líneas nuevas matcheadas:")
        for ln_idx, ln_txt in nuevos_lineas[:5]:
            print(f"    L{ln_idx}: {ln_txt!r}")
    print()

print(f"=== TOTAL ===")
print(f"  Regex viejo total:  {total_viejo}")
print(f"  Regex nuevo total:  {total_nuevo}")
print(f"  Votos hoy perdidos: {total_nuevo - total_viejo}")
