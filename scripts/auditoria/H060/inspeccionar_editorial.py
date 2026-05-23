"""
H060 — Inspección de secciones editoriales.
Extrae las primeras 30 líneas de secciones representativas
para verificar que los subtipos son detectables con regex.

Correr desde la raíz del repo:
  python inspeccionar_editorial.py > inspeccion_editorial.txt
"""
import pandas as pd
from pathlib import Path

CORPUS = Path("corpus")
CSV = Path("output/parser/csjn_casos_editorial.csv")

# Secciones a inspeccionar (elegidas por variedad):
TARGETS = [
    # Tomo 329 vol 4: bloque gigante (32K líneas), probablemente
    # contiene múltiples subtipos concatenados.
    ("329", "LibroVol329.4.md"),
    # Tomo 330 vol 3: discursos interleaved con índices.
    ("330", "LibroVol330.3.md"),
    # Tomo 348 vol 1: bloque chico (468 líneas).
    ("348", "LibroVol348-1.md"),
    # Tomo 341 vol 2: tamaño medio (2704 líneas).
    ("341", "LibroVol341.2.md"),
]

CONTEXT = 30  # líneas a mostrar por sección

df = pd.read_csv(CSV)

for tomo_str, sf in TARGETS:
    tomo = int(tomo_str)
    secs = df[(df["tomo"] == tomo) & (df["source_file"] == sf)]
    if secs.empty:
        print(f"\n{'='*72}")
        print(f"NO HAY SECCIONES para tomo={tomo} / {sf}")
        continue

    filepath = CORPUS / sf
    if not filepath.exists():
        print(f"\n{'='*72}")
        print(f"ARCHIVO NO ENCONTRADO: {filepath}")
        continue

    lines = filepath.read_text(encoding="utf-8").splitlines()

    for _, sec in secs.iterrows():
        li = int(sec["linea_ini"])
        lf = int(sec["linea_fin"])
        nl = int(sec["n_lineas"])
        print(f"\n{'='*72}")
        print(f"TOMO {tomo} | {sf} | seccion={sec['seccion']} | "
              f"líneas {li}–{lf} ({nl} líneas, {sec['wc']} words)")
        print(f"--- Primeras {CONTEXT} líneas ---")
        for i in range(li, min(li + CONTEXT, lf + 1)):
            print(f"{i:6d}  {lines[i]}")

        # Si el bloque es grande, mostrar también las líneas donde
        # podrían arrancar subtipos (transiciones internas).
        if nl > 200:
            print(f"\n--- Scan de marcadores internos (primeros 20 hits) ---")
            import re
            RE_MARKER = re.compile(
                r"^(?:INDICE\s+POR\s+LOS\s+NOMBRES"
                r"|NOMBRES\s+DE\s+LAS\s+PARTES"
                r"|INDICE\s+GENERAL"
                r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
                r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
                r"|INDICE\s+SUMARIO"
                r"|LEGISLACI[OÓ]N\s+NACIONAL"
                r"|POR\s+MATERIAS"
                r"|A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
                r"|ACORDADAS\s+Y\s+RESOLUCIONES"
                r"|DISCURSOS\b"
                r")", re.I
            )
            hits = 0
            for i in range(li, lf + 1):
                s = lines[i].strip()
                if s and RE_MARKER.match(s):
                    # Mostrar ±2 líneas de contexto
                    print(f"\n  HIT en línea {i}: {s!r}")
                    for j in range(max(li, i-2), min(lf+1, i+3)):
                        tag = ">>>" if j == i else "   "
                        print(f"  {tag} {j:6d}  {lines[j]}")
                    hits += 1
                    if hits >= 20:
                        print("  ... (truncado a 20 hits)")
                        break
            if hits == 0:
                print("  (ningún marcador interno encontrado)")

print(f"\n{'='*72}")
print("FIN DE INSPECCIÓN")
