"""
PoC H055-S1b: impacto de restringir Causa -> Causa: en RE_DATOS_PARTES.

Busca epilogos cuya linea-ancla matchea ^Causa pero NO ^Causa\s*:
(falsos positivos que el fix eliminaria). Reporta casos afectados
y wc que dejaria de ser epilogo.

Uso:
    cd corpus-csjn
    python scripts/auditoria/H055/poc_causa_fix.py
"""

import re
import csv
from collections import defaultdict
from pathlib import Path

ZONAS_CSV  = Path("output/parser/csjn_casos_zonas.csv")
CASOS_CSV  = Path("output/parser/csjn_casos.csv")
CORPUS_DIR = Path("corpus")

RE_PAGE_HEADER = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N|\d{2,6})\s*$",
    re.I)

# Patron viejo (false-positive-prone)
RE_CAUSA_VIEJO = re.compile(r"^Causa\b", re.I)
# Patron nuevo (requiere dos puntos)
RE_CAUSA_NUEVO = re.compile(r"^Causa\s*:", re.I)

# Tambien testear Ministerio
RE_MINISTERIO_VIEJO = re.compile(r"^Ministerio\b", re.I)
RE_MINISTERIO_EDITORIAL = re.compile(
    r"^Ministerio\s+P[uú]blico", re.I)


def main():
    # Cargar metadata de casos
    caso_meta = {}
    with open(CASOS_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            caso_meta[r["caso_id_canonico"]] = r

    # Cargar zonas, agrupar por caso
    zonas_por_caso = defaultdict(list)
    with open(ZONAS_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            zonas_por_caso[r["caso_id_canonico"]].append(r)

    # Cache de archivos
    _cache = {}
    def get_lines(sf):
        if sf not in _cache:
            p = CORPUS_DIR / sf
            _cache[sf] = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
        return _cache[sf]

    # Analizar cada epilogo: buscar la primera linea que matchea Causa
    falsos_causa = []
    falsos_ministerio = []

    for caso_id, segs in zonas_por_caso.items():
        meta = caso_meta.get(caso_id)
        if not meta or meta.get("tipo_entrada", "fallo") != "fallo":
            continue

        li_caso = int(meta["linea_inicio"])
        sf = meta["source_file"]
        lines = get_lines(sf)
        if lines is None:
            continue

        epilogos = [s for s in segs if s["zona"] == "epilogo"]
        if not epilogos:
            continue

        wc_epilogo_total = sum(int(s["wc"]) for s in epilogos)

        for seg in epilogos:
            li_seg = int(seg["linea_ini"]) + li_caso
            lf_seg = int(seg["linea_fin"]) + li_caso

            # Buscar primera linea no-vacia, no-header del segmento
            for k in range(li_seg, min(lf_seg + 1, len(lines))):
                s = lines[k].strip()
                if not s or RE_PAGE_HEADER.match(s):
                    continue

                # Test Causa
                if RE_CAUSA_VIEJO.match(s) and not RE_CAUSA_NUEVO.match(s):
                    falsos_causa.append({
                        "caso_id": caso_id,
                        "tomo": meta["tomo"],
                        "linea": k,
                        "texto": s[:100],
                        "wc_seg": int(seg["wc"]),
                        "wc_epilogo_total": wc_epilogo_total,
                        "n_epilogos": len(epilogos),
                    })

                # Test Ministerio
                if RE_MINISTERIO_VIEJO.match(s) and not RE_MINISTERIO_EDITORIAL.match(s):
                    falsos_ministerio.append({
                        "caso_id": caso_id,
                        "tomo": meta["tomo"],
                        "linea": k,
                        "texto": s[:100],
                        "wc_seg": int(seg["wc"]),
                    })

                break  # solo la primera linea del segmento

    # Reporte
    print("=" * 70)
    print("PoC H055-S1b: impacto Causa -> Causa:")
    print("=" * 70)

    print(f"\n--- Falsos positivos de ^Causa (sin dos puntos): {len(falsos_causa)} ---")
    wc_causa_total = sum(f["wc_seg"] for f in falsos_causa)
    print(f"WC en segmentos afectados: {wc_causa_total:,}")
    print()
    print(f"{'caso_id':<20} {'tomo':>4} {'wc_seg':>7} {'wc_epi':>7} {'texto'}")
    print("-" * 100)
    for f in sorted(falsos_causa, key=lambda x: -x["wc_seg"])[:30]:
        print(f"{f['caso_id']:<20} {f['tomo']:>4} {f['wc_seg']:>7} "
              f"{f['wc_epilogo_total']:>7} {f['texto'][:60]}")

    # Casos unicos afectados
    casos_unicos = set(f["caso_id"] for f in falsos_causa)
    print(f"\nCasos unicos con falso Causa: {len(casos_unicos)}")

    print(f"\n--- Falsos positivos de ^Ministerio (no Ministerio Publico): "
          f"{len(falsos_ministerio)} ---")
    if falsos_ministerio:
        wc_min_total = sum(f["wc_seg"] for f in falsos_ministerio)
        print(f"WC en segmentos afectados: {wc_min_total:,}")
        for f in sorted(falsos_ministerio, key=lambda x: -x["wc_seg"])[:10]:
            print(f"  {f['caso_id']:<20} {f['tomo']:>4} wc={f['wc_seg']:>5} "
                  f"{f['texto'][:60]}")


if __name__ == "__main__":
    main()
