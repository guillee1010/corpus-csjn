"""superficie_b177.py — superficie textual de la disidencia parcial por CASO (B177, H221)

Para cada fallo de output/parser/csjn_casos.csv busca, dentro de su rango de líneas en corpus/<source_file>
(linea_inicio..linea_fin_real), las dos marcas de disidencia parcial:
  firma  "(en disidencia parcial)"      header "Disidencia parcial de…" al inicio de línea
y las compara con lo que publica `posiciones` (que hoy colapsa "parcial" en "en disidencia").
Solo lectura. Escribe output/validacion/superficie_b177.csv (una fila por fallo con alguna marca).

Uso:
  python scripts/validacion/superficie_b177.py
"""
__version__ = "0.1"  # H221: reemplaza el conteo ad hoc de H221 (253 marcas / 189 encabezados, por aparición)
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

RAIZ = Path(__file__).resolve().parents[2]
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"
OUT = RAIZ / "output" / "validacion" / "superficie_b177.csv"
RE_FIRMA = re.compile(r"\(\s*en\s+disidencia\s+parcial\s*\.?\s*\)", re.I)
RE_HEADER = re.compile(r"^\s*disidencia\s+parcial\s+de", re.I)

def main():
    casos = [c for c in csv.DictReader(CASOS.open(encoding="utf-8", newline="")) if c.get("tipo_entrada") == "fallo"]
    por_archivo = defaultdict(list)
    for c in casos: por_archivo[c["source_file"]].append(c)
    filas = []
    for sf, cs in por_archivo.items():
        lineas = (RAIZ / "corpus" / sf).read_text(encoding="utf-8").split("\n")
        for c in cs:
            a = int(c["linea_inicio"]); b = int(c["linea_fin_real"] or c["linea_fin"])
            bloque = lineas[a - 1:b]
            nf = sum(len(RE_FIRMA.findall(l)) for l in bloque)
            nh = sum(1 for l in bloque if RE_HEADER.match(l))
            if not (nf or nh): continue
            try: pos = json.loads(c["posiciones"] or "{}")
            except json.JSONDecodeError: pos = {}
            filas.append({"caso_id_canonico": c["caso_id_canonico"], "tomo": c["tomo"],
                          "marcas_firma": nf, "headers": nh,
                          "posiciones_en_disidencia": sum(1 for v in pos.values() if "disidencia" in str(v).lower()),
                          "posiciones_parcial": sum(1 for v in pos.values() if "parcial" in str(v).lower())})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)

    print(f"superficie_b177 v{__version__} · fallos {len(casos)} · con alguna marca de disidencia parcial {len(filas)}")
    print(f"  con marca en la firma {sum(1 for f in filas if f['marcas_firma'])} · con header {sum(1 for f in filas if f['headers'])}"
          f" · con ambas {sum(1 for f in filas if f['marcas_firma'] and f['headers'])}")
    print(f"  posiciones publicadas como 'parcial' en esos fallos: {sum(f['posiciones_parcial'] for f in filas)}"
          f" · fallos sin ninguna disidencia publicada pese a la marca: {sum(1 for f in filas if f['posiciones_en_disidencia'] == 0)}")
    pt = Counter(f["tomo"] for f in filas)
    print("  fallos con marca por tomo: " + " · ".join(f"{t} {pt[t]}" for t in sorted(pt)))
    print(f"\nArchivo: {OUT.relative_to(RAIZ)}")

if __name__ == "__main__":
    main()
