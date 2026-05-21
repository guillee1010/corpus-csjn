"""
L0-muestreo — Inspección de los peores S1 (delta WC) y S3 (epilogo perdido)
============================================================================
Dumpe zonas pre/post y las primeras líneas del bloque para los N peores
casos de cada categoría.

Prerequisito: haber corrido auditoria_l0_regresiones.py y tener los
snapshots pre-H055 en scripts/auditoria/H056/.

Uso:
  python muestreo_l0.py
"""

import csv
from pathlib import Path
from collections import defaultdict

# ── Rutas ────────────────────────────────────────────────────────
AUDIT_DIR = Path(__file__).resolve().parent
REPO = AUDIT_DIR.parent.parent.parent

PRE_CASOS  = AUDIT_DIR / "pre_h055_casos.csv"
POST_CASOS = REPO / "output" / "parser" / "csjn_casos.csv"
PRE_ZONAS  = AUDIT_DIR / "pre_h055_zonas.csv"
POST_ZONAS = REPO / "output" / "parser" / "csjn_casos_zonas.csv"
CORPUS_DIR = REPO / "corpus"

N_MUESTRA = 5

# ── Helpers ──────────────────────────────────────────────────────

def leer_casos(path):
    data = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            data[row["caso_id_canonico"]] = row
    return data


def leer_zonas_por_caso(path):
    """Devuelve dict {caso_id: [(zona, segmento, linea_ini, linea_fin, wc), ...]}"""
    data = defaultdict(list)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            data[row["caso_id_canonico"]].append((
                row["zona"],
                int(row["segmento"]),
                int(row["linea_ini"]),
                int(row["linea_fin"]),
                int(row["wc"]),
            ))
    return dict(data)


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def leer_lineas_bloque(source_file, linea_ini, linea_fin):
    """Lee líneas del archivo fuente .md."""
    path = CORPUS_DIR / source_file
    if not path.exists():
        return [f"(archivo no encontrado: {path})"]
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    ini = max(0, linea_ini)
    fin = min(len(lines), linea_fin + 1)
    return [l.rstrip("\n") for l in lines[ini:fin]]


def mostrar_zonas(zonas_lista, label):
    """Imprime tabla de zonas."""
    if not zonas_lista:
        print(f"  ({label}: sin datos)")
        return
    total_wc = sum(z[4] for z in zonas_lista)
    print(f"  {label} ({len(zonas_lista)} segmentos, {total_wc} wc total):")
    for zona, seg, li, lf, wc in zonas_lista:
        print(f"    {zona:<25} seg={seg} L{li}-L{lf} wc={wc}")


def mostrar_caso(caso_id, pre_row, post_row, zonas_pre_caso, zonas_post_caso, contexto):
    """Imprime diagnóstico completo de un caso."""
    print(f"\n{'─'*70}")
    print(f"CASO: {caso_id}  ({contexto})")
    print(f"{'─'*70}")

    wc_pre = safe_int(pre_row.get("word_count"))
    wc_post = safe_int(post_row.get("word_count"))
    ratio = wc_post / wc_pre if wc_pre > 0 else float("inf")
    print(f"  word_count: {wc_pre} → {wc_post} (ratio {ratio:.2f})")
    print(f"  source: {post_row.get('source_file', '?')}")
    print(f"  líneas: {post_row.get('linea_inicio', '?')}-{post_row.get('linea_fin_real', '?')}")
    print(f"  tipo: {post_row.get('tipo_entrada', '?')}")
    print(f"  case_name: {post_row.get('case_name_indice', '?')[:80]}")

    mostrar_zonas(zonas_pre_caso, "ZONAS PRE")
    mostrar_zonas(zonas_post_caso, "ZONAS POST")

    # Dump primeras y últimas líneas del bloque
    sf = post_row.get("source_file", "")
    li = safe_int(post_row.get("linea_inicio"))
    lf = safe_int(post_row.get("linea_fin_real"))
    lines = leer_lineas_bloque(sf, li, lf)

    n_show = 15
    print(f"\n  PRIMERAS {n_show} LÍNEAS (L{li}-L{li+n_show-1}):")
    for i, l in enumerate(lines[:n_show]):
        print(f"    L{li+i:>5}: {l[:120]}")

    if len(lines) > n_show * 2:
        print(f"  ... ({len(lines) - n_show*2} líneas omitidas) ...")

    if len(lines) > n_show:
        tail = lines[-n_show:]
        tail_start = li + len(lines) - n_show
        print(f"  ÚLTIMAS {n_show} LÍNEAS (L{tail_start}-L{lf}):")
        for i, l in enumerate(tail):
            print(f"    L{tail_start+i:>5}: {l[:120]}")


# ── Main ─────────────────────────────────────────────────────────

def main():
    pre = leer_casos(PRE_CASOS)
    post = leer_casos(POST_CASOS)
    comunes = set(pre.keys()) & set(post.keys())

    zonas_pre = leer_zonas_por_caso(PRE_ZONAS)
    zonas_post = leer_zonas_por_caso(POST_ZONAS)

    # ── S1: peores por delta WC ──────────────────────────────────
    print("=" * 70)
    print(f"S1 — TOP {N_MUESTRA} PEORES DELTA WC (ratio más bajo)")
    print("=" * 70)

    s1 = []
    for cid in comunes:
        wc_pre = safe_int(pre[cid].get("word_count"))
        wc_post = safe_int(post[cid].get("word_count"))
        if wc_pre > 0:
            ratio = wc_post / wc_pre
            if ratio < 0.5:
                s1.append((cid, ratio))

    s1.sort(key=lambda x: x[1])
    for cid, ratio in s1[:N_MUESTRA]:
        zp = zonas_pre.get(cid, []) if zonas_pre else []
        zpo = zonas_post.get(cid, []) if zonas_post else []
        mostrar_caso(cid, pre[cid], post[cid], zp, zpo, f"S1 ratio={ratio:.2f}")

    # ── S3: peores epilogo perdido ───────────────────────────────
    print("\n\n" + "=" * 70)
    print(f"S3 — TOP {N_MUESTRA} EPILOGOS PERDIDOS MÁS GRANDES")
    print("=" * 70)

    if zonas_pre is None:
        print("⚠ Sin datos de zonas pre-H055.")
        return

    epi_pre = defaultdict(int)
    epi_post = defaultdict(int)
    for cid, zlist in zonas_pre.items():
        for z in zlist:
            if z[0] == "epilogo":
                epi_pre[cid] += z[4]
    if zonas_post:
        for cid, zlist in zonas_post.items():
            for z in zlist:
                if z[0] == "epilogo":
                    epi_post[cid] += z[4]

    s3 = []
    for cid in comunes:
        wp = epi_pre.get(cid, 0)
        wpo = epi_post.get(cid, 0)
        if wp > 0 and wpo == 0:
            s3.append((cid, wp))

    s3.sort(key=lambda x: -x[1])
    for cid, wp in s3[:N_MUESTRA]:
        zp = zonas_pre.get(cid, []) if zonas_pre else []
        zpo = zonas_post.get(cid, []) if zonas_post else []
        mostrar_caso(cid, pre[cid], post[cid], zp, zpo, f"S3 epilogo_pre={wp} wc")


if __name__ == "__main__":
    main()
