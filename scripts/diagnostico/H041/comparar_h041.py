#!/usr/bin/env python3
"""
comparar_h041.py — Compara CSV productivo vs H041 Tier 2.

Ubicacion: scripts/diagnostico/H041/
Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    python scripts/diagnostico/H041/comparar_h041.py
"""
import csv
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CSV_PROD = os.path.join(REPO, "output", "parser", "csjn_casos.csv")
CSV_H041 = os.path.join(REPO, "output", "diagnostico", "H041", "csjn_casos_h041.csv")

CAMPOS = [
    "outcome", "voting_pattern", "n_jueces", "firma_raw",
    "wc_mayoria", "wc_votos", "por_ello_text",
]

with open(CSV_PROD, encoding="utf-8") as f:
    prod = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

with open(CSV_H041, encoding="utf-8") as f:
    nuevo = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

mejoras = []
regresiones = []
otros = []

for cid in prod:
    if cid not in nuevo:
        continue
    p, n = prod[cid], nuevo[cid]
    diffs = {}
    for campo in CAMPOS:
        v_old = p.get(campo, "")
        v_new = n.get(campo, "")
        if v_old != v_new:
            diffs[campo] = (v_old, v_new)
    if not diffs:
        continue

    firma_ganada = "firma_raw" in diffs and not diffs["firma_raw"][0] and diffs["firma_raw"][1]
    firma_perdida = "firma_raw" in diffs and diffs["firma_raw"][0] and not diffs["firma_raw"][1]
    outcome_perdido = "outcome" in diffs and diffs["outcome"][0] != "sin_dispositivo" and diffs["outcome"][1] == "sin_dispositivo"

    if firma_perdida or outcome_perdido:
        regresiones.append((cid, diffs))
    elif firma_ganada:
        mejoras.append((cid, diffs))
    else:
        otros.append((cid, diffs))

print("=" * 60)
print(f"MEJORAS (sin_firma -> con_firma): {len(mejoras)}")
print(f"REGRESIONES: {len(regresiones)}")
print(f"OTROS CAMBIOS: {len(otros)}")
print("=" * 60)

if mejoras:
    print("\n--- MEJORAS ---")
    for cid, diffs in mejoras:
        print(f"\n  {cid}:")
        for campo, (old, new) in diffs.items():
            if campo == "firma_raw":
                print(f"    firma: (vacio) -> {new[:70]}")
            elif campo == "por_ello_text":
                print(f"    por_ello: -> {new[:70]}")
            else:
                print(f"    {campo}: {old} -> {new}")

if regresiones:
    print("\n--- REGRESIONES ---")
    for cid, diffs in regresiones:
        print(f"\n  {cid}:")
        for campo, (old, new) in diffs.items():
            print(f"    {campo}: {old[:60]} -> {new[:60]}")

if otros:
    print("\n--- OTROS CAMBIOS ---")
    for cid, diffs in otros:
        print(f"\n  {cid}:")
        for campo, (old, new) in diffs.items():
            print(f"    {campo}: {old[:60]} -> {new[:60]}")

print(f"\nTotal casos prod: {len(prod)}, Total h041: {len(nuevo)}")
