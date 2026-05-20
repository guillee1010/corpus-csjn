# H042 - Paso 0b: Clasificar B055 en subtipos.
# Tipo 1: firma completa pero contaminada (tiene "." interno post-juez)
# Tipo 2: firma truncada (nombre cortado, sin "." en ningun lado post-juez)

import csv, re
from pathlib import Path
from collections import Counter

CSV_CASOS = Path("output/parser/csjn_casos.csv")

APELLIDOS = [
    "rosatti", "rosenkrantz", "lorenzetti", "maqueda", "highton",
    "zaffaroni", "petracchi", "argibay", "fayt", "boggiano",
    "belluscio", "nazareno", "garcia mansilla",
]
re_apellido = re.compile("|".join(APELLIDOS), re.I)

with open(CSV_CASOS, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

b055 = [r for r in rows
        if r.get("firma_raw", "").strip()
        and not r.get("firma_raw", "").strip().endswith(".")]

tipo1 = []  # contaminada: tiene punto despues de un apellido conocido
tipo2 = []  # truncada: no tiene punto despues de ningun apellido

for r in b055:
    firma = r["firma_raw"].strip()
    # Buscar ultimo apellido conocido en firma_raw
    last_match_end = -1
    for m in re_apellido.finditer(firma):
        last_match_end = m.end()
    if last_match_end == -1:
        tipo2.append(r)
        continue
    # Hay texto despues del ultimo apellido?
    post_ultimo = firma[last_match_end:]
    # Buscar punto en la zona post-ultimo-apellido (puede haber calificador)
    if "." in post_ultimo:
        tipo1.append(r)
    else:
        tipo2.append(r)

print(f"Total B055: {len(b055)}")
print(f"Tipo 1 (contaminada, firma OK + basura post): {len(tipo1)}")
print(f"Tipo 2 (truncada, nombre cortado): {len(tipo2)}")

# Distribucion n_jueces por tipo
print(f"\n--- Tipo 1: n_jueces ---")
d1 = Counter(int(r["n_jueces"]) for r in tipo1)
for k in sorted(d1): print(f"  n_jueces={k}: {d1[k]}")

print(f"\n--- Tipo 2: n_jueces ---")
d2 = Counter(int(r["n_jueces"]) for r in tipo2)
for k in sorted(d2): print(f"  n_jueces={k}: {d2[k]}")

# Muestra tipo 1 (5 casos)
print(f"\n--- Muestra Tipo 1 (contaminada) ---")
for r in tipo1[:5]:
    caso = r.get("caso_id_canonico", "?")
    firma = r["firma_raw"].strip()
    # Mostrar desde el ultimo apellido
    last_pos = 0
    for m in re_apellido.finditer(firma):
        last_pos = m.start()
    tail = firma[max(0, last_pos - 10):]
    if len(tail) > 120:
        tail = tail[:120]
    print(f"  {caso} | n_jueces={r['n_jueces']}")
    print(f"    ...{tail}")
    print()

# Muestra tipo 2 (5 casos)
print(f"\n--- Muestra Tipo 2 (truncada) ---")
for r in tipo2[:5]:
    caso = r.get("caso_id_canonico", "?")
    firma = r["firma_raw"].strip()
    tail = firma[-80:] if len(firma) > 80 else firma
    print(f"  {caso} | n_jueces={r['n_jueces']}")
    print(f"    firma_tail: ...{tail}")
    print()

# Longitud de firma_raw por tipo
print(f"--- Longitud firma_raw ---")
len1 = [len(r["firma_raw"]) for r in tipo1]
len2 = [len(r["firma_raw"]) for r in tipo2]
if len1:
    print(f"  Tipo 1: min={min(len1)}, median={sorted(len1)[len(len1)//2]}, max={max(len1)}")
if len2:
    print(f"  Tipo 2: min={min(len2)}, median={sorted(len2)[len(len2)//2]}, max={max(len2)}")
