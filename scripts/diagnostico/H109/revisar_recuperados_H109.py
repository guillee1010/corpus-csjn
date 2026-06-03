#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
revisar_recuperados_H109.py  --  QA de los casos recuperados por B115.

Lista los casos que aparecen en el catalogo NEW y no en OLD, restringidos a
los tomos del fix (331-334; se excluye 335 que es incorporacion de corpus),
y para cada uno cruza:
  - status del cruce (fallos_localizados_H109)
  - case_name_indice / case_name_cuerpo / outcome / date (csjn_casos_H109)
  - conteo de aperturas y dispositivos (zonas) -> deberia ser 1/1 si limpio

Marca:
  [sin_mapa]   si quedo sin header de pagina (cae fuera del parser)
  [APERT>=2]   si todavia tiene >1 apertura (posible swallow residual)

Uso (desde la raiz del repo):
    python revisar_recuperados_H109.py
"""

import csv
import re
from collections import Counter

OLD_CAT = "output/catalogo/catalogo.csv"
NEW_CAT = "output/catalogo/catalogo_H109.csv"
LOC = "output/localizacion/fallos_localizados_H109.csv"
CASOS = "output/parser/csjn_casos_H109.csv"
ZONAS = "output/parser/csjn_casos_H109_zonas.csv"

TOMOS_FIX = {"331", "332", "333", "334"}


def ids(ruta):
    with open(ruta, encoding="utf-8") as f:
        return {r["caso_id_canonico"] for r in csv.DictReader(f)}


def index_by_id(ruta):
    with open(ruta, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}


def clave(cid):
    m = re.match(r"(\d+)_p(\d+)", cid)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def main():
    old = ids(OLD_CAT)
    new = ids(NEW_CAT)
    recuperados = sorted(
        (c for c in (new - old) if c.split("_p")[0] in TOMOS_FIX),
        key=clave,
    )

    loc = index_by_id(LOC)
    casos = index_by_id(CASOS)

    ap = Counter()
    dp = Counter()
    with open(ZONAS, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["zona"] == "apertura":
                ap[r["caso_id_canonico"]] += 1
            elif r["zona"] == "dispositivo":
                dp[r["caso_id_canonico"]] += 1

    print("=" * 78)
    print(f"RECUPERADOS POR B115 (tomos 331-334): {len(recuperados)} casos")
    print("=" * 78)

    n_ok = n_sinmapa = n_swallow = 0
    for cid in recuperados:
        l = loc.get(cid, {})
        status = l.get("status", "?")
        rango = f'{l.get("pagina_inicio","?")}-{l.get("pagina_fin","?")}'
        c = casos.get(cid)
        flags = []
        if "pagina_no_en_mapa" in status:
            flags.append("sin_mapa")
            n_sinmapa += 1
        a = ap.get(cid, 0)
        if a >= 2:
            flags.append(f"APERT={a}")
            n_swallow += 1
        if not flags and c:
            n_ok += 1
        nombre = (c["case_name_cuerpo"][:42] if c and c["case_name_cuerpo"]
                  else (c["case_name_indice"][:42] if c else l.get("nombres_indice", "")[:42]))
        outcome = c["outcome"] if c else "(no en parser)"
        marca = ("  <<" + ",".join(flags) if flags else "")
        print(f"  {cid:>11}  pg {rango:>11}  a/d={a}/{dp.get(cid,0)}  "
              f"{outcome:<12} {nombre}{marca}")

    print("-" * 78)
    print(f"  limpios (ok, apertura=1): {n_ok}")
    print(f"  sin_mapa (no localizados): {n_sinmapa}")
    print(f"  apertura>=2 (revisar swallow residual): {n_swallow}")


if __name__ == "__main__":
    main()
