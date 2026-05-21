"""
L2 — Diagnóstico Ministerio en epilogos
========================================
Extrae todas las líneas que matchean ^Ministerio\b dentro de zonas
epilogo, con contexto (3 líneas antes/después) para clasificar
editorial vs argumentativo.

Uso:
  python diagnostico_ministerio.py
"""

import csv
import re
from pathlib import Path
from collections import defaultdict, Counter

AUDIT_DIR = Path(__file__).resolve().parent
REPO = AUDIT_DIR.parent.parent.parent

ZONAS_CSV = REPO / "output" / "parser" / "csjn_casos_zonas.csv"
CASOS_CSV = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"

RE_MINISTERIO = re.compile(r"^Ministerio\b", re.I)


def safe_int(v, d=0):
    try: return int(v)
    except: return d


def main():
    # Cargar casos (para source_file y linea_inicio)
    casos = {}
    with open(CASOS_CSV, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            casos[r["caso_id_canonico"]] = r

    # Cargar zonas epilogo
    epilogos = []  # (caso_id, linea_ini_rel, linea_fin_rel, wc)
    with open(ZONAS_CSV, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["zona"] == "epilogo":
                epilogos.append((
                    r["caso_id_canonico"],
                    int(r["linea_ini"]),
                    int(r["linea_fin"]),
                    int(r["wc"]),
                ))

    print(f"Total segmentos epilogo: {len(epilogos)}")

    # Cache de archivos fuente
    source_cache = {}

    # Buscar ^Ministerio en cada segmento de epilogo
    hits = []
    for caso_id, rel_ini, rel_fin, wc in epilogos:
        caso = casos.get(caso_id)
        if not caso:
            continue
        sf = caso["source_file"]
        li = safe_int(caso["linea_inicio"])

        if sf not in source_cache:
            path = CORPUS_DIR / sf
            if path.exists():
                source_cache[sf] = path.read_text(encoding="utf-8").split("\n")
            else:
                source_cache[sf] = None

        lines = source_cache[sf]
        if lines is None:
            continue

        for rel_k in range(rel_ini, rel_fin + 1):
            abs_k = li + rel_k
            if abs_k >= len(lines):
                break
            line = lines[abs_k].strip()
            if RE_MINISTERIO.match(line):
                # Contexto: 3 líneas antes/después
                ctx_before = []
                for j in range(max(0, abs_k - 3), abs_k):
                    ctx_before.append(lines[j].rstrip())
                ctx_after = []
                for j in range(abs_k + 1, min(len(lines), abs_k + 4)):
                    ctx_after.append(lines[j].rstrip())

                hits.append({
                    "caso_id": caso_id,
                    "tomo": caso_id.split("_p")[0],
                    "linea_abs": abs_k,
                    "linea_rel": rel_k,
                    "text": line[:120],
                    "full_text": line,
                    "ctx_before": ctx_before,
                    "ctx_after": ctx_after,
                    "wc_epilogo": wc,
                })

    print(f"Hits ^Ministerio en epilogo: {len(hits)}")
    print()

    # Clasificar patrones
    print("=" * 80)
    print("ANÁLISIS DE PATRONES")
    print("=" * 80)

    # Señales editoriales: ":", "c/", "Público"
    n_con_colon = sum(1 for h in hits if ":" in h["full_text"])
    n_con_c_barra = sum(1 for h in hits if "c/" in h["full_text"])
    n_publico = sum(1 for h in hits if "Público" in h["full_text"] or "Publico" in h["full_text"])
    n_defensa = sum(1 for h in hits if "Defensa" in h["full_text"])
    n_economia = sum(1 for h in hits if "Economía" in h["full_text"] or "Economia" in h["full_text"])
    n_trabajo = sum(1 for h in hits if "Trabajo" in h["full_text"])

    print(f"  Con ':' en la línea:     {n_con_colon}")
    print(f"  Con 'c/' en la línea:    {n_con_c_barra}")
    print(f"  Con 'Público':           {n_publico}")
    print(f"  Con 'Defensa':           {n_defensa}")
    print(f"  Con 'Economía':          {n_economia}")
    print(f"  Con 'Trabajo':           {n_trabajo}")

    # Prefijos más comunes (primeras 3 palabras)
    prefijos = Counter()
    for h in hits:
        words = h["full_text"].split()[:4]
        prefijos[" ".join(words)] += 1

    print(f"\nTop 20 prefijos (4 palabras):")
    for pref, n in prefijos.most_common(20):
        print(f"  {n:>4}  {pref}")

    # Mostrar todos los hits con contexto
    print(f"\n{'='*80}")
    print(f"TODOS LOS HITS ({len(hits)})")
    print(f"{'='*80}")

    for i, h in enumerate(hits):
        print(f"\n{'─'*60}")
        print(f"[{i+1}/{len(hits)}] {h['caso_id']}  L{h['linea_abs']}  (epilogo wc={h['wc_epilogo']})")
        print(f"{'─'*60}")
        for cl in h["ctx_before"]:
            print(f"  │ {cl[:110]}")
        print(f"  ▶ {h['text']}")
        for cl in h["ctx_after"]:
            print(f"  │ {cl[:110]}")

    # Resumen por tomo
    print(f"\n{'='*80}")
    print("DISTRIBUCIÓN POR TOMO")
    print(f"{'='*80}")
    tomo_count = Counter(h["tomo"] for h in hits)
    for t, n in sorted(tomo_count.items()):
        print(f"  T{t}: {n}")


if __name__ == "__main__":
    main()
