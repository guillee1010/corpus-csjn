"""
Validación post-patch B045 bidireccional (H069).

Compara el CSV pre-patch (git snapshot) con el post-patch para
identificar todos los casos que cambiaron y verificar que los
cambios son consistentes con el POC.

Uso (desde raíz del repo, después del re-run):
    python poc_b045_validacion.py

Lee:
    - CSV viejo: git show bdc42b3:output/parser/csjn_casos.csv
    - CSV nuevo: output/parser/csjn_casos.csv
"""

import csv
import subprocess
import sys
from collections import Counter
from io import StringIO
from pathlib import Path

CSV_NUEVO = Path("output/parser/csjn_casos.csv")
COMMIT_SNAPSHOT = "bdc42b3"  # snapshot pre-H069

# Columnas clave para comparar
COLS_CLAVE = [
    "linea_fin_real", "status_fin", "pista_fin",
    "voting_pattern", "outcome", "n_jueces", "n_votos_svoto",
    "n_disidencias", "firma_raw", "word_count", "wc_mayoria",
    "sin_dispositivo",
]


def cargar_csv_git(commit, path):
    """Lee un CSV desde un commit de git."""
    cmd = ["git", "show", f"{commit}:{path}"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"ERROR: no se pudo leer {path} desde {commit}")
        print(result.stderr)
        sys.exit(1)
    reader = csv.DictReader(StringIO(result.stdout))
    return {r["caso_id_canonico"]: r for r in reader}


def cargar_csv(path):
    """Lee un CSV desde disco."""
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {r["caso_id_canonico"]: r for r in reader}


def main():
    print("Cargando CSV viejo desde git...")
    viejo = cargar_csv_git(COMMIT_SNAPSHOT, "output/parser/csjn_casos.csv")
    print(f"  {len(viejo)} casos")

    print("Cargando CSV nuevo...")
    nuevo = cargar_csv(CSV_NUEVO)
    print(f"  {len(nuevo)} casos")

    # Verificar mismo universo
    ids_v = set(viejo.keys())
    ids_n = set(nuevo.keys())
    if ids_v != ids_n:
        print(f"  WARN: diferencia de IDs: +{len(ids_n - ids_v)} -{len(ids_v - ids_n)}")

    # ── Identificar cambios en linea_fin_real ─────────────────────────────
    cambios_lfr = []
    cambios_vp = []
    cambios_outcome = []
    cambios_otros = []

    for caso_id in sorted(ids_v & ids_n):
        v = viejo[caso_id]
        n = nuevo[caso_id]

        lfr_v = v.get("linea_fin_real", "")
        lfr_n = n.get("linea_fin_real", "")
        cambio_lfr = lfr_v != lfr_n

        vp_v = v.get("voting_pattern", "")
        vp_n = n.get("voting_pattern", "")
        cambio_vp = vp_v != vp_n

        out_v = v.get("outcome", "")
        out_n = n.get("outcome", "")
        cambio_out = out_v != out_n

        if cambio_lfr:
            delta_lfr = int(lfr_n) - int(lfr_v) if lfr_v and lfr_n else None
            cambios_lfr.append({
                "caso_id": caso_id,
                "lfr_v": lfr_v, "lfr_n": lfr_n, "delta_lfr": delta_lfr,
                "pista_v": v.get("pista_fin", ""), "pista_n": n.get("pista_fin", ""),
                "vp_v": vp_v, "vp_n": vp_n,
                "out_v": out_v, "out_n": out_n,
                "nj_v": v.get("n_jueces", ""), "nj_n": n.get("n_jueces", ""),
                "firma_v": v.get("firma_raw", "")[:50],
                "firma_n": n.get("firma_raw", "")[:50],
                "wc_v": v.get("word_count", ""), "wc_n": n.get("word_count", ""),
            })
        if cambio_vp:
            cambios_vp.append({"caso_id": caso_id, "vp_v": vp_v, "vp_n": vp_n})
        if cambio_out:
            cambios_outcome.append({"caso_id": caso_id, "out_v": out_v, "out_n": out_n})

        # Cualquier otro cambio en columnas clave (sin lfr ni vp ni outcome)
        if not cambio_lfr and not cambio_vp and not cambio_out:
            for col in COLS_CLAVE:
                if v.get(col, "") != n.get(col, ""):
                    cambios_otros.append({"caso_id": caso_id, "col": col,
                                          "v": v.get(col, "")[:40],
                                          "n": n.get(col, "")[:40]})
                    break  # solo reportar primer col diferente

    # ── Reporte ──────────────────────────────────────────────────────────

    print()
    print("=" * 110)
    print(f"CAMBIOS EN linea_fin_real: {len(cambios_lfr)} casos")
    print("=" * 110)
    print(f"  {'caso_id':>15s}  {'pista_v':>20s} {'pista_n':>20s}  {'lfr_v':>7s} {'lfr_n':>7s} {'Δlfr':>6s}  "
          f"{'vp_v':>15s} {'vp_n':>15s}  {'out_v':>12s} {'out_n':>12s}")
    print("  " + "-" * 106)
    for c in sorted(cambios_lfr, key=lambda x: -(x["delta_lfr"] or 0)):
        d = f"{c['delta_lfr']:+d}" if c["delta_lfr"] is not None else "?"
        print(f"  {c['caso_id']:>15s}  {c['pista_v']:>20s} {c['pista_n']:>20s}  "
              f"{c['lfr_v']:>7s} {c['lfr_n']:>7s} {d:>6s}  "
              f"{c['vp_v']:>15s} {c['vp_n']:>15s}  "
              f"{c['out_v']:>12s} {c['out_n']:>12s}")

    # Resumen de transiciones de pista
    print()
    pista_trans = Counter((c["pista_v"], c["pista_n"]) for c in cambios_lfr)
    print("Transiciones de pista_fin:")
    for (pv, pn), count in pista_trans.most_common():
        print(f"  {pv} → {pn}: {count}")

    # Resumen de transiciones de voting_pattern
    print()
    print(f"CAMBIOS EN voting_pattern: {len(cambios_vp)} casos")
    vp_trans = Counter((c["vp_v"], c["vp_n"]) for c in cambios_vp)
    for (vpv, vpn), count in vp_trans.most_common():
        print(f"  {vpv} → {vpn}: {count}")

    # Resumen de transiciones de outcome
    print()
    print(f"CAMBIOS EN outcome: {len(cambios_outcome)} casos")
    out_trans = Counter((c["out_v"], c["out_n"]) for c in cambios_outcome)
    for (ov, on), count in out_trans.most_common():
        print(f"  {ov} → {on}: {count}")

    # Cambios inesperados (sin cambio en lfr/vp/outcome)
    print()
    print(f"CAMBIOS EN OTRAS COLUMNAS (sin cambio en lfr/vp/outcome): {len(cambios_otros)}")
    if cambios_otros:
        for c in cambios_otros[:10]:
            print(f"  {c['caso_id']:>15s}  col={c['col']}  viejo={c['v']}  nuevo={c['n']}")

    # ── Verificación de no-regresión ─────────────────────────────────────
    print()
    print("=" * 110)
    print("VERIFICACIONES")
    print("=" * 110)

    # 1. Solo firma_actual debería cambiar
    non_fa_cambios = [c for c in cambios_lfr
                      if c["pista_v"] != "firma_actual" and c["pista_n"] != "firma_actual"]
    print(f"  Cambios en lfr fuera de firma_actual: {len(non_fa_cambios)}")
    if non_fa_cambios:
        for c in non_fa_cambios:
            print(f"    {c['caso_id']} pista: {c['pista_v']}→{c['pista_n']}")

    # 2. Ningún caso debería perder firma (sin_firma nuevo que no era antes)
    nuevos_sin_firma = [c for c in cambios_vp if c["vp_n"] == "sin_firma" and c["vp_v"] != "sin_firma"]
    print(f"  Nuevos sin_firma (regresión): {len(nuevos_sin_firma)}")

    # 3. Todos los cambios lfr deberían ser positivos (extensión, no retracción)
    retracciones = [c for c in cambios_lfr if c["delta_lfr"] is not None and c["delta_lfr"] < 0]
    print(f"  Retracciones (delta_lfr < 0): {len(retracciones)}")
    if retracciones:
        for c in retracciones:
            print(f"    {c['caso_id']} Δ={c['delta_lfr']}")

    # 4. Word count: debería subir (más contenido)
    wc_cambios = [(c["caso_id"], int(c["wc_v"] or 0), int(c["wc_n"] or 0))
                  for c in cambios_lfr if c["wc_v"] and c["wc_n"]]
    wc_bajas = [(cid, wv, wn) for cid, wv, wn in wc_cambios if wn < wv]
    wc_subas = [(cid, wv, wn) for cid, wv, wn in wc_cambios if wn > wv]
    print(f"  Word count sube: {len(wc_subas)},  baja: {len(wc_bajas)},  igual: {len(wc_cambios)-len(wc_subas)-len(wc_bajas)}")
    if wc_bajas:
        for cid, wv, wn in wc_bajas:
            print(f"    BAJA: {cid} {wv}→{wn} (Δ={wn-wv})")

    print()


if __name__ == "__main__":
    main()
