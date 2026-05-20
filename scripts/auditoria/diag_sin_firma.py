import csv
from collections import Counter

with open("output/parser/csjn_casos.csv", encoding="utf-8") as f:
    todos = list(csv.DictReader(f))

sf = [r for r in todos if r["tipo_entrada"] == "fallo" and not r["firma_raw"].strip()]
print(f"Sin firma: {len(sf)}")

print(f"\nPor pista_fin:")
for k, v in Counter(r["pista_fin"] for r in sf).most_common():
    print(f"  {k:<35} {v}")

print(f"\nPor status_fin:")
for k, v in Counter(r["status_fin"] for r in sf).most_common():
    print(f"  {k:<35} {v}")

print(f"\nPor tomo:")
for k, v in sorted(Counter(r["tomo"] for r in sf).items(), key=lambda x: int(x[0])):
    print(f"  T{k}: {v}")

# Cuantos tienen lfc en zona de indice? (linea_fin muy alta)
print(f"\nCasos con bloque > 2000 lineas (posible indice):")
grandes = [(int(r["linea_fin"])-int(r["linea_inicio"]), r["caso_id_canonico"], r["pista_fin"]) for r in sf]
grandes.sort(reverse=True)
for tam, caso, pista in grandes[:10]:
    print(f"  {caso:<15} bloque={tam:<6} pista={pista}")
