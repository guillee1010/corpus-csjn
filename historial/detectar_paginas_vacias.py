"""
Detector de páginas vacías en archivos Markdown de Fallos CSJN
===============================================================
Estrategia: pasaje lineal único O(N).

Cada página del libro tiene en el MD:
    [número de página]     ← línea sola con número
    (header opcional)
    [número de tomo]       ← línea sola con el número del tomo

Detectamos el par (num_pag, num_tomo) en proximidad como marca
de inicio de página. Entre dos marcas consecutivas contamos
líneas de contenido real. Si hay menos de --umbral → página vacía.

Pasaje único O(N): se escanea el archivo una sola vez construyendo
la lista de marcas, luego una segunda pasada O(M) sobre las marcas.
No hay loops anidados sobre el contenido.
"""

import re
import argparse
import csv
from pathlib import Path
from collections import defaultdict

RE_NUM_SOLO  = re.compile(r"^\s*(\d{2,5})\s*$")
RE_TOMO_FILE = re.compile(r"LibroVol(\d+)", re.I)
RE_HEADER    = re.compile(
    r"^(FALLOS?\s+DE\s+LA\s+CORTE\s+SUPREMA|"
    r"DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N|"
    r"CORTE\s+SUPREMA\s+DE\s+JUSTICIA)\s*$",
    re.I
)


def es_contenido_real(s, tomo_str):
    if not s:
        return False
    if RE_HEADER.match(s):
        return False
    if s == tomo_str:
        return False
    if RE_NUM_SOLO.match(s):
        return False
    return True


def analizar_archivo(filepath, umbral=3):
    tomo_m = RE_TOMO_FILE.search(filepath.name)
    tomo     = int(tomo_m.group(1)) if tomo_m else 0
    tomo_str = str(tomo)

    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        print(f"  [ERROR] {filepath.name}: {e}")
        return [], tomo, 0

    n = len(lines)

    # ── Paso 1: encontrar marcas en un solo pasaje O(N) ───────────────────────
    # Pre-computar qué líneas son números solos
    nums = {}  # indice → valor entero
    for i, line in enumerate(lines):
        m = RE_NUM_SOLO.match(line)
        if m:
            v = int(m.group(1))
            nums[i] = v

    # Buscar patrón: línea con num_pag seguida (1-3 líneas) por num_tomo
    marcas = []  # lista de (num_pagina, idx_linea_del_tomo)
    usados = set()  # índices ya usados como marca para no duplicar

    for i, v in nums.items():
        if i in usados:
            continue
        # ¿Es un número de página plausible?
        if not (50 <= v <= 9999 and v != tomo):
            continue
        # Buscar el tomo en las próximas 3 líneas
        for offset in range(1, 4):
            j = i + offset
            if j in nums and nums[j] == tomo:
                marcas.append((v, j))
                usados.add(i)
                usados.add(j)
                break

    if not marcas:
        return [], tomo, n

    # ── Paso 2: contar contenido entre marcas O(M) ────────────────────────────
    paginas_vacias = []

    for idx in range(len(marcas) - 1):
        num_a, fin_a = marcas[idx]
        num_b, fin_b = marcas[idx + 1]

        # Solo pares de páginas consecutivas
        if not (1 <= num_b - num_a <= 4):
            continue

        # Contenido de la página A: entre fin_a+1 y unos pasos antes de fin_b
        ini = fin_a + 1
        fin = max(ini, fin_b - 3)

        n_real = sum(
            1 for l in lines[ini:fin]
            if es_contenido_real(l.strip(), tomo_str)
        )

        if n_real < umbral:
            muestra = " | ".join(
                l.strip() for l in lines[ini:fin] if l.strip()
            )[:120]
            paginas_vacias.append({
                "tomo":        tomo,
                "archivo":     filepath.name,
                "pag":         num_a,
                "pag_sig":     num_b,
                "linea_md":    fin_a + 1,
                "n_contenido": n_real,
                "muestra":     muestra,
            })

    return paginas_vacias, tomo, n


def main():
    ap = argparse.ArgumentParser(description="Detector de páginas vacías CSJN")
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--umbral", type=int, default=3,
                    help="Mínimo de líneas reales para no ser vacía (default=3)")
    ap.add_argument("--detalle", action="store_true")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    archivos = sorted(Path(args.input_dir).glob("LibroVol*.md"))
    if not archivos:
        print("No se encontraron archivos LibroVol*.md")
        return

    print(f"Analizando {len(archivos)} archivos | umbral={args.umbral}\n")

    resumen = defaultdict(lambda: {"n": 0, "lineas": 0,
                                    "archivos": [], "ejemplos": []})
    todas = []

    for fp in archivos:
        print(f"  {fp.name}...", end="", flush=True)
        vacias, tomo, n_lineas = analizar_archivo(fp, args.umbral)
        print(f" {len(vacias)} vacías")
        r = resumen[tomo]
        r["n"]      += len(vacias)
        r["lineas"] += n_lineas
        r["archivos"].append(fp.name)
        r["ejemplos"].extend(vacias[:3])
        todas.extend(vacias)

    # ── Tabla ─────────────────────────────────────────────────────────────────
    print(f"\n{'Tomo':<8} {'Págs vacías':>11} {'Líneas MD':>10}  Archivos")
    print("─" * 75)

    total = 0
    problemas = []
    for tomo in sorted(resumen):
        r = resumen[tomo]
        n = r["n"]
        total += n
        flag = "  ← GRAVE"   if n > 50 else \
               "  ← revisar" if n > 10 else ""
        if n > 50:
            problemas.append(tomo)
        arch = ", ".join(r["archivos"])
        print(f"{tomo:<8} {n:>11} {r['lineas']:>10}  {arch}{flag}")

        if args.detalle and r["ejemplos"]:
            for ej in r["ejemplos"][:3]:
                print(f"         pág {ej['pag']:>5}→{ej['pag_sig']} "
                      f"(real={ej['n_contenido']}): {ej['muestra'][:55]}")

    print("─" * 75)
    print(f"{'TOTAL':<8} {total:>11}")

    if problemas:
        print(f"\n⚠  Tomos con problema grave (>50 págs vacías): {problemas}")
    else:
        print("\n✓  Sin tomos con problema grave.")

    if args.output and todas:
        out = Path(args.output)
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "tomo", "archivo", "pag", "pag_sig",
                "linea_md", "n_contenido", "muestra"
            ])
            w.writeheader()
            w.writerows(todas)
        print(f"\n[OK] CSV: {out}  ({len(todas)} páginas)")

    print(f"\nTotal páginas vacías: {total}")


if __name__ == "__main__":
    main()
