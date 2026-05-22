"""
L3 — Diagnóstico de arrastre del caso siguiente en epilogos
============================================================
Escanea desde el final de cada bloque buscando líneas ALL CAPS
(carátula del caso siguiente) o sumario_header dentro de la zona
epilogo. Reporta casos afectados con contexto.

Uso:
  python diagnostico_arrastre.py
"""

import csv
import re
from pathlib import Path
from collections import defaultdict

AUDIT_DIR = Path(__file__).resolve().parent
REPO = AUDIT_DIR.parent.parent.parent

ZONAS_CSV = REPO / "output" / "parser" / "csjn_casos_zonas.csv"
CASOS_CSV = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"

# Patrón de carátula ALL CAPS: "NOMBRE V. NOMBRE" o "NOMBRE c/ NOMBRE"
RE_CARATULA = re.compile(
    r"^[A-ZÁÉÍÓÚÑ\s,.\-()]+\s+[VvCc][./]\s+[A-ZÁÉÍÓÚÑ]",
)

def es_linea_allcaps(line):
    """True si la línea tiene ≥5 chars alfabéticos y todos son mayúsculas."""
    s = line.strip()
    if not s or len(s) < 5:
        return False
    chars = [c for c in s if c.isalpha()]
    if len(chars) < 5:
        return False
    return all(c.isupper() for c in chars)


def linea_es_header_sumario(linea):
    """Replica la detección del parser."""
    s = linea.strip()
    if not s or len(s) > 150:
        return False
    if not (s.endswith(".") or s.endswith(":") or ":" in s[:80]):
        return False
    primeros = [c for c in s if c.isalpha()][:5]
    if len(primeros) < 5 or not all(c.isupper() for c in primeros):
        return False
    primera = re.match(r"^[A-ZÁÉÍÓÚÑ]+", s)
    return primera and len(primera.group(0)) >= 5


def safe_int(v, d=0):
    try: return int(v)
    except: return d


def main():
    # Cargar casos
    casos = {}
    with open(CASOS_CSV, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["tipo_entrada"] != "fallo":
                continue
            casos[r["caso_id_canonico"]] = r

    # Cargar zonas agrupadas por caso
    zonas = defaultdict(list)
    with open(ZONAS_CSV, "r", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            zonas[r["caso_id_canonico"]].append({
                "zona": r["zona"],
                "linea_ini": int(r["linea_ini"]),
                "linea_fin": int(r["linea_fin"]),
                "wc": int(r["wc"]),
            })

    # Cache fuentes
    source_cache = {}

    hits = []

    for caso_id, caso in casos.items():
        zlist = zonas.get(caso_id, [])
        if not zlist:
            continue

        # Encontrar última zona no-header_pagina
        sem = [z for z in zlist if z["zona"] != "header_pagina"]
        if not sem:
            continue
        ultima = sem[-1]
        if ultima["zona"] != "epilogo":
            continue

        # Leer líneas del bloque
        sf = caso["source_file"]
        li = safe_int(caso["linea_inicio"])
        lf = safe_int(caso["linea_fin_real"])

        if sf not in source_cache:
            path = CORPUS_DIR / sf
            if path.exists():
                source_cache[sf] = path.read_text(encoding="utf-8").split("\n")
            else:
                source_cache[sf] = None
        lines = source_cache[sf]
        if lines is None:
            continue

        # Escanear desde el final del epilogo hacia atrás
        epi_fin_abs = li + ultima["linea_fin"]
        epi_ini_abs = li + ultima["linea_ini"]

        # Buscar líneas ALL CAPS al final del epilogo
        trailing_allcaps = []
        k = min(epi_fin_abs, len(lines) - 1)
        while k >= epi_ini_abs:
            line = lines[k].strip()
            if not line:  # saltar vacías
                k -= 1
                continue
            # Parar si es header de página (3 líneas: número, "DE JUSTICIA...", tomo)
            if re.match(r"^\d+$", line) or "DE JUSTICIA" in line or "FALLOS DE LA CORTE" in line:
                k -= 1
                continue
            if es_linea_allcaps(line) or linea_es_header_sumario(line):
                trailing_allcaps.append((k, line))
                k -= 1
            else:
                break

        if not trailing_allcaps:
            continue

        # Calcular wc del arrastre
        trailing_allcaps.reverse()  # orden cronológico
        arrastre_ini = trailing_allcaps[0][0]
        arrastre_fin = trailing_allcaps[-1][0]
        wc_arrastre = sum(len(line.split()) for _, line in trailing_allcaps)

        # Contexto: 3 líneas antes del arrastre
        ctx = []
        for j in range(max(li, arrastre_ini - 3), arrastre_ini):
            if j < len(lines):
                ctx.append((j, lines[j].rstrip()))

        hits.append({
            "caso_id": caso_id,
            "tomo": caso_id.split("_p")[0],
            "pag": caso_id.split("_p")[1] if "_p" in caso_id else "?",
            "n_lineas_arrastre": len(trailing_allcaps),
            "wc_arrastre": wc_arrastre,
            "arrastre_lines": trailing_allcaps,
            "ctx": ctx,
            "epi_wc": ultima["wc"],
        })

    # Ordenar por wc_arrastre desc
    hits.sort(key=lambda x: -x["wc_arrastre"])

    print(f"Casos con epilogo al final del bloque: {sum(1 for c in casos if zonas.get(c) and [z for z in zonas[c] if z['zona'] != 'header_pagina'] and [z for z in zonas[c] if z['zona'] != 'header_pagina'][-1]['zona'] == 'epilogo')}")
    print(f"Casos con arrastre detectado: {len(hits)}")
    print(f"WC total arrastre: {sum(h['wc_arrastre'] for h in hits):,}")
    print()

    # Top 30
    print("=" * 80)
    print(f"TOP 30 POR WC ARRASTRE")
    print("=" * 80)
    print(f"{'caso_id':<18} {'tomo':<6} {'pág':<8} {'n_lin':>5} {'wc_arr':>7} {'epi_wc':>7}")
    print("-" * 60)
    for h in hits[:30]:
        print(f"{h['caso_id']:<18} {h['tomo']:<6} {h['pag']:<8} "
              f"{h['n_lineas_arrastre']:>5} {h['wc_arrastre']:>7} {h['epi_wc']:>7}")

    # Detalle top 15
    print(f"\n{'='*80}")
    print(f"DETALLE TOP 15")
    print(f"{'='*80}")
    for h in hits[:15]:
        print(f"\n{'─'*60}")
        print(f"{h['caso_id']}  (arrastre: {h['n_lineas_arrastre']} líneas, {h['wc_arrastre']} wc)")
        print(f"{'─'*60}")
        for lnum, line in h["ctx"]:
            print(f"  │ L{lnum}: {line[:110]}")
        for lnum, line in h["arrastre_lines"]:
            print(f"  ▶ L{lnum}: {line[:110]}")


if __name__ == "__main__":
    main()
