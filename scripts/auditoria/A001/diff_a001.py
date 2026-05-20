"""
Diff A001: compara csjn_casos.csv pre vs post patch
====================================================
Uso:
    1. Copiar CSV actual a output/auditoria/csjn_casos_pre_a001.csv
    2. Reemplazar parser.py con versión patcheada
    3. Correr parser (correr_parser.bat)
    4. Correr este script

    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    copy output\\parser\\csjn_casos.csv output\\auditoria\\csjn_casos_pre_a001.csv
    [reemplazar parser.py, correr parser]
    python scripts/auditoria/diff_a001.py

Reporta:
  - Mejoras: sin_firma → otro voting_pattern
  - Regresiones: tenía firma → sin_firma (o cambio de VP)
  - Cambios en n_jueces, outcome
  - Totales antes/después
"""

import csv
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CSV_PRE  = REPO_ROOT / "output" / "auditoria" / "csjn_casos_pre_a001.csv"
CSV_POST = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"


def cargar(path):
    with open(path, "r", encoding="utf-8") as f:
        return {row["caso_id_canonico"]: row for row in csv.DictReader(f)}


def main():
    pre  = cargar(CSV_PRE)
    post = cargar(CSV_POST)

    print(f"Casos PRE:  {len(pre)}")
    print(f"Casos POST: {len(post)}")

    # Solo fallos
    pre_fallos  = {k: v for k, v in pre.items()  if v["tipo_entrada"] == "fallo"}
    post_fallos = {k: v for k, v in post.items() if v["tipo_entrada"] == "fallo"}

    sf_pre  = sum(1 for v in pre_fallos.values()  if v["voting_pattern"] == "sin_firma")
    sf_post = sum(1 for v in post_fallos.values() if v["voting_pattern"] == "sin_firma")
    print(f"\nsin_firma PRE:  {sf_pre}")
    print(f"sin_firma POST: {sf_post}")
    print(f"Delta:          {sf_post - sf_pre:+d}")

    mejoras = []
    regresiones = []
    cambios_otros = []

    common = set(pre_fallos.keys()) & set(post_fallos.keys())
    for caso_id in sorted(common):
        vp_pre  = pre_fallos[caso_id]["voting_pattern"]
        vp_post = post_fallos[caso_id]["voting_pattern"]
        if vp_pre == vp_post:
            continue
        nj_pre  = pre_fallos[caso_id]["n_jueces"]
        nj_post = post_fallos[caso_id]["n_jueces"]
        oc_pre  = pre_fallos[caso_id]["outcome"]
        oc_post = post_fallos[caso_id]["outcome"]
        tomo    = pre_fallos[caso_id]["tomo"]
        entry = {
            "caso_id": caso_id,
            "tomo": tomo,
            "vp_pre": vp_pre,
            "vp_post": vp_post,
            "nj_pre": nj_pre,
            "nj_post": nj_post,
            "oc_pre": oc_pre,
            "oc_post": oc_post,
        }
        if vp_pre == "sin_firma" and vp_post != "sin_firma":
            mejoras.append(entry)
        elif vp_pre != "sin_firma" and vp_post == "sin_firma":
            regresiones.append(entry)
        else:
            cambios_otros.append(entry)

    # ── Mejoras ──
    print(f"\n{'='*70}")
    print(f"MEJORAS (sin_firma → firma): {len(mejoras)}")
    print(f"{'='*70}")
    for m in mejoras:
        print(f"  {m['caso_id']:15s} T{m['tomo']:>3s} | "
              f"{m['vp_pre']:12s} → {m['vp_post']:12s} | "
              f"{m['nj_pre']}J→{m['nj_post']}J | "
              f"outcome: {m['oc_pre']} → {m['oc_post']}")

    # ── Regresiones ──
    print(f"\n{'='*70}")
    print(f"REGRESIONES (firma → sin_firma): {len(regresiones)}")
    print(f"{'='*70}")
    if regresiones:
        for r in regresiones:
            print(f"  {r['caso_id']:15s} T{r['tomo']:>3s} | "
                  f"{r['vp_pre']:12s} → {r['vp_post']:12s} | "
                  f"{r['nj_pre']}J→{r['nj_post']}J")
    else:
        print("  (ninguna)")

    # ── Otros cambios ──
    if cambios_otros:
        print(f"\n{'='*70}")
        print(f"OTROS CAMBIOS DE VP: {len(cambios_otros)}")
        print(f"{'='*70}")
        for c in cambios_otros:
            print(f"  {c['caso_id']:15s} T{c['tomo']:>3s} | "
                  f"{c['vp_pre']:12s} → {c['vp_post']:12s} | "
                  f"{c['nj_pre']}J→{c['nj_post']}J")

    # ── Votos ──
    votos_pre_path  = CSV_PRE.parent / "csjn_casos_pre_a001_votos.csv"
    votos_post_path = REPO_ROOT / "output" / "parser" / "csjn_casos_votos.csv"
    if votos_pre_path.exists() and votos_post_path.exists():
        with open(votos_pre_path, "r", encoding="utf-8") as f:
            nv_pre = sum(1 for _ in csv.DictReader(f))
        with open(votos_post_path, "r", encoding="utf-8") as f:
            nv_post = sum(1 for _ in csv.DictReader(f))
        print(f"\nVotos PRE:  {nv_pre}")
        print(f"Votos POST: {nv_post}")
        print(f"Delta:      {nv_post - nv_pre:+d}")

    # ── Resumen final ──
    print(f"\n{'='*70}")
    print(f"RESUMEN")
    print(f"{'='*70}")
    print(f"  Mejoras:      {len(mejoras)}")
    print(f"  Regresiones:  {len(regresiones)}")
    print(f"  Otros cambios:{len(cambios_otros)}")
    print(f"  sin_firma:    {sf_pre} → {sf_post}")
    if len(regresiones) == 0:
        print(f"\n  ✓ LIMPIO — 0 regresiones. Safe to commit.")
    else:
        print(f"\n  ✗ HAY REGRESIONES — revisar antes de commitear.")


if __name__ == "__main__":
    main()
