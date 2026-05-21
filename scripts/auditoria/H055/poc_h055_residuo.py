"""
PoC H055 — Reclasificación de intersticio inicial como residuo_caso_anterior.

Lógica (replica pseudocódigo del prompt H055):
  1. Para cada caso, buscar el primer segmento no-header_pagina.
  2. Buscar el primer segmento semántico.
  3. Si el primero es intersticio y termina antes del semántico → residuo.

Mide impacto en word_count cruzando con csjn_casos.csv.
Identifica edge cases y candidatos a spot-check.

Uso:
  python poc_h055_residuo.py \
      --zonas ../../output/parser/csjn_casos_zonas.csv \
      --casos ../../output/parser/csjn_casos.csv
"""

import csv
import argparse
from collections import defaultdict

ZONAS_SEMANTICAS = {"sumario", "dictamen", "apertura", "cuerpo",
                    "dispositivo", "firma", "voto_separado"}


def clasificar_residuo(segmentos):
    """
    Dado los segmentos de un caso (lista de dicts del zonas CSV),
    retorna (es_residuo: bool, seg_residuo: dict | None).
    
    Replica la lógica del visor_auditoria.py líneas 313-325,
    adaptada al schema del zonificador.
    """
    primer_no_header = None
    for s in segmentos:
        if s["zona"] != "header_pagina":
            primer_no_header = s
            break

    primer_semantico = None
    for s in segmentos:
        if s["zona"] in ZONAS_SEMANTICAS:
            primer_semantico = s
            break

    if (primer_no_header is not None
            and primer_semantico is not None
            and primer_no_header["zona"] == "intersticio"
            and int(primer_no_header["linea_fin"]) < int(primer_semantico["linea_ini"])):
        return True, primer_no_header

    return False, None


def main():
    ap = argparse.ArgumentParser(description="PoC H055: residuo_caso_anterior")
    ap.add_argument("--zonas", required=True)
    ap.add_argument("--casos", required=True)
    args = ap.parse_args()

    # ── Cargar zonas ──────────────────────────────────────────────────
    casos_segs = defaultdict(list)
    with open(args.zonas, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            casos_segs[row["caso_id_canonico"]].append(row)

    # ── Cargar casos (para word_count actual) ─────────────────────────
    wc_actual = {}
    wc_mayoria_actual = {}
    tomo_caso = {}
    tipo_entrada = {}
    with open(args.casos, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cid = row["caso_id_canonico"]
            wc_actual[cid] = int(row["word_count"]) if row["word_count"] else 0
            wc_mayoria_actual[cid] = int(row["wc_mayoria"]) if row["wc_mayoria"] else 0
            tomo_caso[cid] = row["tomo"]
            tipo_entrada[cid] = row.get("tipo_entrada", "fallo")

    # ── Clasificar ────────────────────────────────────────────────────
    n_residuo = 0
    n_sin_residuo = 0
    n_sin_semantico = 0
    wc_residuo_total = 0
    delta_por_tomo = defaultdict(lambda: {"n": 0, "wc": 0})
    casos_residuo = []   # para spot-check
    edge_cases = []      # transiciones raras

    for caso_id, segs in casos_segs.items():
        # Solo fallos (no sumarios)
        if tipo_entrada.get(caso_id, "fallo") != "fallo":
            continue

        es_residuo, seg = clasificar_residuo(segs)

        if es_residuo:
            n_residuo += 1
            wc_res = int(seg["wc"])
            wc_residuo_total += wc_res
            tomo = seg["tomo"]
            delta_por_tomo[tomo]["n"] += 1
            delta_por_tomo[tomo]["wc"] += wc_res

            # Qué zona sigue al residuo?
            idx_residuo = segs.index(seg)
            zona_siguiente = None
            for s in segs[idx_residuo + 1:]:
                if s["zona"] != "header_pagina":
                    zona_siguiente = s["zona"]
                    break

            casos_residuo.append({
                "caso_id": caso_id,
                "tomo": tomo,
                "wc_residuo": wc_res,
                "wc_actual": wc_actual.get(caso_id, 0),
                "wc_nuevo": wc_actual.get(caso_id, 0) - wc_res,
                "pct_residuo": round(100 * wc_res / wc_actual[caso_id], 1) if wc_actual.get(caso_id) else 0,
                "zona_siguiente": zona_siguiente,
                "linea_ini": seg["linea_ini"],
                "linea_fin": seg["linea_fin"],
                "n_lineas": seg["n_lineas"],
            })

            # Edge cases: transición a zona inesperada
            if zona_siguiente in ("dispositivo", "firma", "epilogo", "intersticio", None):
                edge_cases.append(casos_residuo[-1])
        else:
            # Verificar por qué no es residuo
            primer_no_header = next(
                (s for s in segs if s["zona"] != "header_pagina"), None)
            primer_semantico = next(
                (s for s in segs if s["zona"] in ZONAS_SEMANTICAS), None)
            if primer_semantico is None:
                n_sin_semantico += 1
            else:
                n_sin_residuo += 1

    # ── Reporte ───────────────────────────────────────────────────────
    n_fallos = sum(1 for v in tipo_entrada.values() if v == "fallo")
    print("=" * 65)
    print("PoC H055 — Reclasificación residuo_caso_anterior")
    print("=" * 65)
    print(f"Fallos analizados:         {n_fallos}")
    print(f"Con residuo inicial:       {n_residuo} ({100*n_residuo/n_fallos:.1f}%)")
    print(f"Sin residuo (inicia sem.): {n_sin_residuo}")
    print(f"Sin zona semántica:        {n_sin_semantico}")
    print(f"WC total reclasificado:    {wc_residuo_total:,}")
    print()

    # Delta por tomo
    print("── Delta por tomo ──")
    print(f"  {'Tomo':>6}  {'Casos':>6}  {'WC residuo':>10}  {'Media':>6}")
    for t in sorted(delta_por_tomo.keys(), key=lambda x: int(x)):
        d = delta_por_tomo[t]
        media = d["wc"] / d["n"] if d["n"] else 0
        print(f"  {t:>6}  {d['n']:>6}  {d['wc']:>10,}  {media:>6.0f}")
    print()

    # Distribución de transiciones post-residuo
    trans = defaultdict(int)
    for c in casos_residuo:
        trans[c["zona_siguiente"] or "NINGUNA"] += 1
    print("── Transición post-residuo ──")
    for z, n in sorted(trans.items(), key=lambda x: -x[1]):
        print(f"  {z:<25} {n:>5}  ({100*n/n_residuo:.1f}%)")
    print()

    # Distribución de tamaño del residuo
    wcs = [c["wc_residuo"] for c in casos_residuo]
    wcs.sort()
    print("── Distribución WC del residuo ──")
    print(f"  Min:      {wcs[0]}")
    print(f"  P25:      {wcs[len(wcs)//4]}")
    print(f"  Mediana:  {wcs[len(wcs)//2]}")
    print(f"  P75:      {wcs[3*len(wcs)//4]}")
    print(f"  Max:      {wcs[-1]}")
    print(f"  Media:    {sum(wcs)/len(wcs):.1f}")
    print()

    # Impacto en word_count: % del WC total que se reclasifica
    wc_total_corpus = sum(wc_actual.get(cid, 0) for cid, te in tipo_entrada.items() if te == "fallo")
    print(f"── Impacto global ──")
    print(f"  WC total corpus (fallos):  {wc_total_corpus:>12,}")
    print(f"  WC reclasificado:          {wc_residuo_total:>12,}  ({100*wc_residuo_total/wc_total_corpus:.2f}%)")
    print()

    # Top 10 residuos más grandes (spot-check candidates)
    print("── Top 15 residuos más grandes (spot-check) ──")
    top = sorted(casos_residuo, key=lambda c: -c["wc_residuo"])[:15]
    print(f"  {'caso_id':<20} {'tomo':>4} {'wc_res':>7} {'wc_act':>7} {'%res':>5} {'→zona':<15} {'rango'}")
    for c in top:
        print(f"  {c['caso_id']:<20} {c['tomo']:>4} {c['wc_residuo']:>7} "
              f"{c['wc_actual']:>7} {c['pct_residuo']:>5}% "
              f"{c['zona_siguiente'] or '?':<15} L{c['linea_ini']}-{c['linea_fin']}")
    print()

    # Edge cases: transición a dispositivo/firma (S2 del prompt)
    if edge_cases:
        print(f"── Edge cases ({len(edge_cases)}): residuo → dispositivo/firma/epilogo/intersticio ──")
        for c in edge_cases[:20]:
            print(f"  {c['caso_id']:<20} {c['tomo']:>4} wc={c['wc_residuo']:>5} "
                  f"→ {c['zona_siguiente'] or 'NINGUNA':<15}")
        if len(edge_cases) > 20:
            print(f"  ... y {len(edge_cases) - 20} más")
    print()

    # Casos con word_count negativo post-reclasificación (sanity check)
    negativos = [c for c in casos_residuo if c["wc_nuevo"] < 0]
    if negativos:
        print(f"⚠ {len(negativos)} casos con WC negativo post-reclasificación:")
        for c in negativos:
            print(f"  {c['caso_id']} wc_actual={c['wc_actual']} wc_residuo={c['wc_residuo']}")
    else:
        print("✓ Ningún caso con WC negativo post-reclasificación")


if __name__ == "__main__":
    main()
