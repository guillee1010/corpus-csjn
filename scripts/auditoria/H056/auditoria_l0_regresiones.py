"""
L0 — Auditoría de regresiones silenciosas (H051-H055)
======================================================
Compara csjn_casos.csv pre-H055 vs post-H055 para detectar:
  1. Delta WC > 50% del original
  2. WC post < 100
  3. Epilogo perdido (>0 pre, 0 post) — requiere zonas CSVs
  4. Cruce con los 35 sin_firma
  5. Distribución delta por tomo

Uso:
  python auditoria_l0_regresiones.py

Prerequisito: extraer snapshot pre-H055 en scripts/auditoria/H056/:
  git show 141f1a7:output/parser/csjn_casos.csv > scripts/auditoria/H056/pre_h055_casos.csv
  git show 141f1a7:output/parser/csjn_casos_zonas.csv > scripts/auditoria/H056/pre_h055_zonas.csv
  (si el zonas no existía en ese commit, el script corre igual sin la parte de epilogo)
"""

import csv
import os
from pathlib import Path
from collections import defaultdict

# ── Rutas ────────────────────────────────────────────────────────
AUDIT_DIR = Path(__file__).resolve().parent            # scripts/auditoria/H056/
REPO = AUDIT_DIR.parent.parent.parent                  # corpus-csjn/

PRE_CASOS  = AUDIT_DIR / "pre_h055_casos.csv"
POST_CASOS = REPO / "output" / "parser" / "csjn_casos.csv"

PRE_ZONAS  = AUDIT_DIR / "pre_h055_zonas.csv"
POST_ZONAS = REPO / "output" / "parser" / "csjn_casos_zonas.csv"

# ── Helpers ──────────────────────────────────────────────────────

def leer_casos(path):
    """Devuelve dict {caso_id_canonico: row_dict}."""
    data = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            data[row["caso_id_canonico"]] = row
    return data


def leer_wc_epilogo(path):
    """Devuelve dict {caso_id_canonico: sum(wc de zona epilogo)}."""
    wc = defaultdict(int)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["zona"] == "epilogo":
                wc[row["caso_id_canonico"]] += int(row["wc"])
    return dict(wc)


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


# ── Main ─────────────────────────────────────────────────────────

def main():
    # Verificar archivos
    if not PRE_CASOS.exists():
        print(f"ERROR: No se encontró {PRE_CASOS}")
        print("Ejecutá: git show 141f1a7:output/parser/csjn_casos.csv > scripts/auditoria/H056/pre_h055_casos.csv")
        return
    if not POST_CASOS.exists():
        print(f"ERROR: No se encontró {POST_CASOS}")
        return

    pre = leer_casos(PRE_CASOS)
    post = leer_casos(POST_CASOS)

    print(f"Pre-H055:  {len(pre)} casos")
    print(f"Post-H055: {len(post)} casos")

    # Casos comunes
    comunes = set(pre.keys()) & set(post.keys())
    solo_pre = set(pre.keys()) - set(post.keys())
    solo_post = set(post.keys()) - set(pre.keys())
    print(f"Comunes: {len(comunes)} | Solo pre: {len(solo_pre)} | Solo post: {len(solo_post)}")

    if solo_pre:
        print(f"\n⚠ Casos que DESAPARECIERON post-H055: {sorted(solo_pre)[:20]}")
    if solo_post:
        print(f"\nCasos NUEVOS post-H055: {sorted(solo_post)[:20]}")

    # ── S1. Delta WC > 50% ───────────────────────────────────────
    print("\n" + "="*70)
    print("S1. CASOS CON DELTA word_count > 50%")
    print("="*70)

    delta_grande = []
    for cid in sorted(comunes):
        wc_pre = safe_int(pre[cid].get("word_count"))
        wc_post = safe_int(post[cid].get("word_count"))
        if wc_pre > 0:
            ratio = wc_post / wc_pre
            if ratio < 0.5 or ratio > 2.0:
                delta_grande.append((cid, wc_pre, wc_post, ratio))

    print(f"Encontrados: {len(delta_grande)}")
    if delta_grande:
        print(f"{'caso_id':<20} {'wc_pre':>8} {'wc_post':>8} {'ratio':>8}")
        print("-"*50)
        for cid, wp, wpo, r in sorted(delta_grande, key=lambda x: x[3])[:30]:
            print(f"{cid:<20} {wp:>8} {wpo:>8} {r:>8.2f}")
        if len(delta_grande) > 30:
            print(f"... y {len(delta_grande)-30} más")

    # ── S2. WC post < 100 ───────────────────────────────────────
    print("\n" + "="*70)
    print("S2. CASOS CON word_count POST < 100")
    print("="*70)

    wc_bajo = []
    for cid in sorted(comunes):
        wc_post = safe_int(post[cid].get("word_count"))
        wc_pre = safe_int(pre[cid].get("word_count"))
        if wc_post < 100:
            wc_bajo.append((cid, wc_pre, wc_post))

    print(f"Encontrados: {len(wc_bajo)}")
    if wc_bajo:
        print(f"{'caso_id':<20} {'wc_pre':>8} {'wc_post':>8} {'delta':>8}")
        print("-"*50)
        for cid, wp, wpo in sorted(wc_bajo, key=lambda x: x[2]):
            print(f"{cid:<20} {wp:>8} {wpo:>8} {wpo-wp:>+8}")

    # ── S3. Epilogo perdido ──────────────────────────────────────
    print("\n" + "="*70)
    print("S3. EPILOGO PERDIDO (>0 pre, 0 post)")
    print("="*70)

    epi_pre = leer_wc_epilogo(PRE_ZONAS)
    epi_post = leer_wc_epilogo(POST_ZONAS)

    if epi_pre is None:
        print("⚠ No se encontró pre_h055_zonas.csv — salteando esta sección.")
        print(f"  Si existía en el commit, extraelo con:")
        print(f"  git show 141f1a7:output/parser/csjn_casos_zonas.csv > {PRE_ZONAS}")
    else:
        perdidos = []
        for cid in sorted(comunes):
            wp = epi_pre.get(cid, 0)
            wpo = epi_post.get(cid, 0) if epi_post else 0
            if wp > 0 and wpo == 0:
                perdidos.append((cid, wp))

        print(f"Encontrados: {len(perdidos)}")
        if perdidos:
            print(f"{'caso_id':<20} {'wc_epilogo_pre':>15}")
            print("-"*40)
            for cid, wp in sorted(perdidos, key=lambda x: -x[1])[:30]:
                print(f"{cid:<20} {wp:>15}")

    # ── S4. Cruce con sin_firma ──────────────────────────────────
    print("\n" + "="*70)
    print("S4. CRUCE CON SIN_FIRMA")
    print("="*70)

    sin_firma_post = [cid for cid in comunes
                      if post[cid].get("status_fin") == "sin_firma"]
    sin_firma_pre = [cid for cid in comunes
                     if pre[cid].get("status_fin") == "sin_firma"]

    print(f"Sin firma pre: {len(sin_firma_pre)} | post: {len(sin_firma_post)}")

    # ¿Algún sin_firma empeoró en WC?
    empeoraron = []
    for cid in sin_firma_post:
        wc_pre = safe_int(pre[cid].get("word_count"))
        wc_post = safe_int(post[cid].get("word_count"))
        if wc_pre > 0 and wc_post < wc_pre * 0.7:
            empeoraron.append((cid, wc_pre, wc_post))

    # Nuevos sin_firma (eran ok_firma y ahora sin_firma)
    nuevos_sf = [cid for cid in sin_firma_post if cid not in sin_firma_pre]
    recuperados = [cid for cid in sin_firma_pre if cid not in sin_firma_post]

    if nuevos_sf:
        print(f"⚠ NUEVOS sin_firma (regresión): {sorted(nuevos_sf)}")
    else:
        print("✓ Sin regresiones nuevas en sin_firma.")

    if recuperados:
        print(f"✓ Recuperados (eran sin_firma, ahora ok): {sorted(recuperados)[:20]}")

    if empeoraron:
        print(f"\n⚠ Sin_firma con caída de WC >30%:")
        for cid, wp, wpo in empeoraron:
            print(f"  {cid}: {wp} → {wpo} ({wpo/wp:.0%})")

    # ── S5. Distribución delta por tomo ──────────────────────────
    print("\n" + "="*70)
    print("S5. DISTRIBUCIÓN DEL DELTA WC POR TOMO")
    print("="*70)

    tomo_deltas = defaultdict(list)
    for cid in comunes:
        wc_pre = safe_int(pre[cid].get("word_count"))
        wc_post = safe_int(post[cid].get("word_count"))
        tomo = pre[cid].get("tomo", "?")
        if wc_pre > 0:
            delta_pct = (wc_post - wc_pre) / wc_pre * 100
            tomo_deltas[tomo].append(delta_pct)

    print(f"{'tomo':<8} {'n':>5} {'med_delta%':>12} {'min%':>8} {'max%':>8} {'n_>50%':>8}")
    print("-"*55)
    for tomo in sorted(tomo_deltas.keys(), key=lambda x: safe_int(x)):
        deltas = tomo_deltas[tomo]
        n = len(deltas)
        med = sum(deltas) / n
        mn = min(deltas)
        mx = max(deltas)
        n_big = sum(1 for d in deltas if abs(d) > 50)
        flag = " ⚠" if n_big > 0 else ""
        print(f"{tomo:<8} {n:>5} {med:>+11.1f} {mn:>+8.1f} {mx:>+8.1f} {n_big:>8}{flag}")

    # ── Resumen ──────────────────────────────────────────────────
    print("\n" + "="*70)
    print("RESUMEN L0")
    print("="*70)
    print(f"  S1 delta WC >50%:     {len(delta_grande)}")
    print(f"  S2 WC post <100:      {len(wc_bajo)}")
    print(f"  S3 epilogo perdido:   {'(sin datos)' if epi_pre is None else len(perdidos)}")
    print(f"  S4 nuevos sin_firma:  {len(nuevos_sf)}")
    print(f"  S4 sf empeorados WC:  {len(empeoraron)}")
    print(f"  Tomos con outliers:   {sum(1 for t,ds in tomo_deltas.items() if any(abs(d)>50 for d in ds))}")


if __name__ == "__main__":
    main()
