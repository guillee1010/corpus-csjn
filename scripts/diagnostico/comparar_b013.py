"""
Comparador B013 — diff caso a caso entre CSV productivo y CSV del fix.

Uso:
  python scripts/diagnostico/comparar_b013.py \
      --productivo output/parser/csjn_casos.csv \
      --fix output/diagnostico/B013/csjn_casos_b013.csv

Reporta:
  - Casos que cambiaron algún campo analítico
  - Clasificación: mejora / regresión / lateral
  - Totales por categoría
"""
import csv
import argparse
from collections import Counter

CAMPOS_ANALITICOS = [
    "firma_raw", "por_ello_text", "outcome", "voting_pattern",
    "n_jueces", "word_count", "wc_mayoria", "wc_considerando",
    "wc_dictamen",
]

def cargar_csv(path):
    with open(path, encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

def clasificar_cambio(prod, fix):
    """Clasifica el cambio entre productivo y fix."""
    prod_firma = prod.get("firma_raw", "")
    fix_firma = fix.get("firma_raw", "")
    prod_disp = prod.get("por_ello_text", "")
    fix_disp = fix.get("por_ello_text", "")
    prod_nj = int(prod.get("n_jueces", "0") or "0")
    fix_nj = int(fix.get("n_jueces", "0") or "0")

    # Mejora clara: ganó firma donde no había
    if not prod_firma and fix_firma:
        return "mejora_gano_firma"
    # Mejora: ganó más jueces
    if fix_nj > prod_nj and prod_nj == 0:
        return "mejora_gano_jueces"
    if fix_nj > prod_nj:
        return "mejora_mas_jueces"
    # Regresión: perdió firma
    if prod_firma and not fix_firma:
        return "regresion_perdio_firma"
    # Regresión: perdió jueces
    if fix_nj < prod_nj:
        return "regresion_menos_jueces"
    # Cambió dispositivo
    if prod_disp != fix_disp:
        if not prod_disp and fix_disp:
            return "mejora_gano_dispositivo"
        if prod_disp and not fix_disp:
            return "regresion_perdio_dispositivo"
        return "cambio_dispositivo"
    # Cambió outcome
    if prod.get("outcome") != fix.get("outcome"):
        return "cambio_outcome"
    # Otro cambio
    return "cambio_otro"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--productivo", required=True)
    ap.add_argument("--fix", required=True)
    ap.add_argument("--max-detalle", type=int, default=10,
                    help="Máximo de casos a detallar por categoría")
    args = ap.parse_args()

    prod = cargar_csv(args.productivo)
    fix = cargar_csv(args.fix)

    # Verificar mismos caso_id
    solo_prod = set(prod) - set(fix)
    solo_fix = set(fix) - set(prod)
    if solo_prod:
        print(f"ALERTA: {len(solo_prod)} casos solo en productivo")
    if solo_fix:
        print(f"ALERTA: {len(solo_fix)} casos solo en fix")

    # Diff campo por campo
    cambios = {}  # caso_id -> {campo: (prod, fix), ...}
    for caso_id in sorted(set(prod) & set(fix)):
        diffs = {}
        for campo in CAMPOS_ANALITICOS:
            v_prod = prod[caso_id].get(campo, "")
            v_fix = fix[caso_id].get(campo, "")
            if v_prod != v_fix:
                diffs[campo] = (v_prod, v_fix)
        if diffs:
            cambios[caso_id] = diffs

    print(f"\nCasos totales: {len(set(prod) & set(fix))}")
    print(f"Casos con cambios: {len(cambios)}")
    print(f"Casos sin cambios: {len(set(prod) & set(fix)) - len(cambios)}")

    if not cambios:
        print("\nNingún cambio detectado.")
        return

    # Clasificar
    clasificacion = Counter()
    por_categoria = {}
    for caso_id, diffs in cambios.items():
        cat = clasificar_cambio(prod[caso_id], fix[caso_id])
        clasificacion[cat] += 1
        por_categoria.setdefault(cat, []).append(caso_id)

    print(f"\n=== Clasificación de cambios ===")
    for cat, n in clasificacion.most_common():
        print(f"  {cat:<35} {n:>5}")

    # Detalle por categoría
    for cat in ["regresion_perdio_firma", "regresion_menos_jueces",
                "regresion_perdio_dispositivo",
                "mejora_gano_firma", "mejora_gano_jueces",
                "mejora_mas_jueces", "mejora_gano_dispositivo",
                "cambio_dispositivo", "cambio_outcome", "cambio_otro"]:
        casos = por_categoria.get(cat, [])
        if not casos:
            continue
        print(f"\n--- {cat} ({len(casos)} casos) ---")
        for caso_id in casos[:args.max_detalle]:
            diffs = cambios[caso_id]
            tomo = prod[caso_id].get("tomo", "?")
            print(f"  {caso_id} (tomo {tomo}):")
            for campo, (vp, vf) in diffs.items():
                vp_short = (vp[:70] + "...") if len(vp) > 70 else vp
                vf_short = (vf[:70] + "...") if len(vf) > 70 else vf
                print(f"    {campo}: {vp_short!r} → {vf_short!r}")
        if len(casos) > args.max_detalle:
            print(f"  ... y {len(casos) - args.max_detalle} más")


if __name__ == "__main__":
    main()
