#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificar_H109.py  --  chequeo del fix B115 sobre el catalogo.

Compara el catalogo canonico actual (output/catalogo/catalogo.csv) contra el
nuevo generado por construir_catalogo v1.01 (output/catalogo/catalogo_H109.csv).

Uso (desde la raiz del repo):
    python verificar_H109.py
"""

import csv
import re
import sys
from collections import defaultdict

OLD = "output/catalogo/catalogo.csv"
NEW = "output/catalogo/catalogo_H109.csv"


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def inicial(nombres):
    """Inicial del primer nombre del ' | ', salteando comillas/parentesis/(NN)."""
    n = nombres.split(" | ")[0].strip().lstrip('"').lstrip("(").strip()
    n = re.sub(r"^\(\d+\)\s*", "", n)
    return n[:1].upper() if n else "?"


def main():
    try:
        old_rows = cargar(OLD)
        new_rows = cargar(NEW)
    except FileNotFoundError as e:
        print(f"ERROR: no encuentro {e.filename}. Corre esto desde la raiz del repo.")
        sys.exit(1)

    old = {r["caso_id_canonico"] for r in old_rows}
    new = {r["caso_id_canonico"] for r in new_rows}

    recuperados = new - old
    perdidos = old - new

    print("=" * 60)
    print("VERIFICACION B115 / H109")
    print("=" * 60)
    print(f"Catalogo OLD: {len(old)} casos")
    print(f"Catalogo NEW: {len(new)} casos")
    print()
    print(f"Arriola 332_p1963 en NEW?  {'SI' if '332_p1963' in new else 'NO'}")
    print(f"Casos recuperados (NEW-OLD): {len(recuperados)}")
    print(f"Casos perdidos (OLD-NEW):    {len(perdidos)}  <- deberia ser 0")
    print()

    # A-fraccion por tomo (deberia recuperarse en 331-334)
    def afrac(rows):
        por_tomo_total = defaultdict(int)
        por_tomo_a = defaultdict(int)
        for r in rows:
            t = r["tomo"]
            por_tomo_total[t] += 1
            if inicial(r["nombres_indice"]) == "A":
                por_tomo_a[t] += 1
        return por_tomo_total, por_tomo_a

    tot_o, a_o = afrac(old_rows)
    tot_n, a_n = afrac(new_rows)
    print("A-fraccion por tomo (OLD -> NEW):")
    print(f"  {'tomo':>5} {'A_old':>6} {'%old':>6} {'A_new':>6} {'%new':>6}")
    for t in sorted(set(tot_o) | set(tot_n), key=lambda x: int(x)):
        po = 100 * a_o.get(t, 0) / tot_o[t] if tot_o.get(t) else 0
        pn = 100 * a_n.get(t, 0) / tot_n[t] if tot_n.get(t) else 0
        marca = "  <--" if t in ("331", "332", "333", "334") else ""
        print(f"  {t:>5} {a_o.get(t,0):>6} {po:>5.1f}% {a_n.get(t,0):>6} {pn:>5.1f}%{marca}")
    print()

    # Recuperados, ordenados por tomo+pagina
    def clave(cid):
        m = re.match(r"(\d+)_p(\d+)", cid)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

    print(f"Casos recuperados (primeros 40 de {len(recuperados)}):")
    nom_new = {r["caso_id_canonico"]: r["nombres_indice"] for r in new_rows}
    for cid in sorted(recuperados, key=clave)[:40]:
        print(f"  {cid:>12}  {nom_new.get(cid,'')[:55]}")

    if perdidos:
        print()
        print(f"ATENCION: {len(perdidos)} casos perdidos (revisar):")
        for cid in sorted(perdidos, key=clave)[:40]:
            print(f"  {cid}")


if __name__ == "__main__":
    main()
