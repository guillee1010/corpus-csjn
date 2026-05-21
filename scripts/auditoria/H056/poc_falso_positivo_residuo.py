"""
PoC L0-S1 — Falsos positivos de residuo_caso_anterior
======================================================
Identifica casos donde residuo transiciona directamente a
dispositivo o firma, sin apertura/cuerpo/dictamen/sumario
intermedios. Cruza con S1 (delta WC > 50%).

Salida: tomo, página, caso_id, wc_pre, wc_post, primera zona
post-residuo, y primera línea del residuo para inspección.
"""

import csv
from pathlib import Path
from collections import defaultdict

AUDIT_DIR = Path(__file__).resolve().parent
REPO = AUDIT_DIR.parent.parent.parent

PRE_CASOS  = AUDIT_DIR / "pre_h055_casos.csv"
POST_CASOS = REPO / "output" / "parser" / "csjn_casos.csv"
POST_ZONAS = REPO / "output" / "parser" / "csjn_casos_zonas.csv"
CORPUS_DIR = REPO / "corpus"


def safe_int(v, d=0):
    try: return int(v)
    except: return d


def main():
    # Leer casos pre/post
    pre, post = {}, {}
    with open(PRE_CASOS, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            pre[r["caso_id_canonico"]] = r
    with open(POST_CASOS, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            post[r["caso_id_canonico"]] = r

    # Leer zonas post agrupadas por caso
    zonas = defaultdict(list)
    with open(POST_ZONAS, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            zonas[r["caso_id_canonico"]].append({
                "zona": r["zona"],
                "linea_ini": int(r["linea_ini"]),
                "linea_fin": int(r["linea_fin"]),
                "wc": int(r["wc"]),
            })

    # Clasificar cada caso con residuo
    ZONAS_CUERPO = {"apertura", "cuerpo", "dictamen", "sumario"}
    resultados = []

    for cid, zlist in zonas.items():
        if cid not in pre or cid not in post:
            continue
        # Filtrar header_pagina
        sem = [z for z in zlist if z["zona"] != "header_pagina"]
        if not sem:
            continue

        # ¿Tiene residuo?
        tiene_residuo = any(z["zona"] == "residuo_caso_anterior" for z in sem)
        if not tiene_residuo:
            continue

        # Encontrar primera zona NO residuo
        primera_post_residuo = None
        wc_residuo = 0
        for z in sem:
            if z["zona"] == "residuo_caso_anterior":
                wc_residuo += z["wc"]
            elif primera_post_residuo is None:
                primera_post_residuo = z["zona"]

        if primera_post_residuo is None:
            primera_post_residuo = "(solo_residuo)"

        # ¿Hay alguna zona de cuerpo?
        tiene_cuerpo = any(z["zona"] in ZONAS_CUERPO for z in sem)

        # Calcular delta
        wc_pre = safe_int(pre[cid].get("word_count"))
        wc_post = safe_int(post[cid].get("word_count"))
        ratio = wc_post / wc_pre if wc_pre > 0 else float("inf")

        # Extraer tomo y página del caso_id
        parts = cid.split("_p")
        tomo = parts[0] if len(parts) == 2 else "?"
        pagina = parts[1] if len(parts) == 2 else "?"

        # Primera línea del bloque (para inspección)
        source = post[cid].get("source_file", "")
        linea_inicio = safe_int(post[cid].get("linea_inicio"))
        primera_linea = ""
        if source:
            src_path = CORPUS_DIR / source
            if src_path.exists():
                with open(src_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i == linea_inicio:
                            primera_linea = line.strip()[:100]
                            break

        resultados.append({
            "cid": cid,
            "tomo": tomo,
            "pagina": pagina,
            "wc_pre": wc_pre,
            "wc_post": wc_post,
            "ratio": ratio,
            "wc_residuo": wc_residuo,
            "primera_post_residuo": primera_post_residuo,
            "tiene_cuerpo": tiene_cuerpo,
            "primera_linea": primera_linea,
            "case_name": post[cid].get("case_name_indice", "")[:50],
        })

    # Separar en dos grupos
    fp = [r for r in resultados if not r["tiene_cuerpo"]]  # falso positivo candidato
    ok = [r for r in resultados if r["tiene_cuerpo"]]       # residuo probablemente genuino

    # Mostrar falsos positivos (ordenados por wc_residuo desc)
    fp.sort(key=lambda x: -x["wc_residuo"])

    print("=" * 90)
    print(f"CANDIDATOS A FALSO POSITIVO: residuo sin zonas de cuerpo ({len(fp)} casos)")
    print("  (residuo transiciona a dispositivo/firma/epilogo — sin apertura/cuerpo/dictamen/sumario)")
    print("=" * 90)
    print(f"{'tomo':<6} {'pág':<8} {'caso_id':<18} {'wc_pre':>7} {'wc_post':>7} {'ratio':>6} "
          f"{'wc_res':>7} {'1ra_zona_post':<15} case_name")
    print("-" * 90)
    for r in fp:
        print(f"{r['tomo']:<6} {r['pagina']:<8} {r['cid']:<18} {r['wc_pre']:>7} {r['wc_post']:>7} "
              f"{r['ratio']:>6.2f} {r['wc_residuo']:>7} {r['primera_post_residuo']:<15} "
              f"{r['case_name']}")

    # Estadísticas
    print(f"\nTotal con residuo: {len(resultados)}")
    print(f"  Candidatos FP (sin cuerpo): {len(fp)}")
    print(f"  Residuo genuino (con cuerpo): {len(ok)}")
    print(f"  WC total en FP residuo: {sum(r['wc_residuo'] for r in fp):,}")

    # Desglose por primera zona post-residuo en FP
    from collections import Counter
    trans = Counter(r["primera_post_residuo"] for r in fp)
    print(f"\n  Transiciones en FP:")
    for z, n in trans.most_common():
        print(f"    residuo → {z}: {n}")

    # Los que cruzan con S1 (ratio < 0.5)
    s1_fp = [r for r in fp if r["ratio"] < 0.5]
    print(f"\n  De esos, con ratio < 0.5 (S1): {len(s1_fp)}")

    # Mostrar primeras líneas de los top 10 FP para inspección visual
    print(f"\n{'='*90}")
    print(f"PRIMERA LÍNEA DEL BLOQUE (top 20 FP por wc_residuo)")
    print(f"{'='*90}")
    for r in fp[:20]:
        print(f"  T{r['tomo']} p{r['pagina']:>5} ({r['wc_residuo']:>5} wc res): {r['primera_linea']}")


if __name__ == "__main__":
    main()
