"""
diagnostico_pista2_sumario.py — H040 diagnóstico

Compara linea_es_header_sumario (parser) vs es_header_sumario_auditoria
(auditor) en la zona exacta donde detectar_fin_real aplica Pista 2.

Reporta:
  - Cuántos casos usan pista_fin=sumario_siguiente (del CSV existente).
  - Para cada línea en la zona Pista 2, qué función matchea.
  - Clasificación de falsos positivos: ¿firma? ¿header de página? ¿carátula? ¿otro?
  - Líneas que matchea solo el parser (candidatas a falso positivo).

Uso:
  cd corpus-csjn
  python scripts/diagnostico/diagnostico_pista2_sumario.py

Output: stdout + archivo de detalle en output/diagnostico/pista2_sumario_detalle.csv
"""

import csv
import re
import sys
from pathlib import Path
from collections import Counter

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent  # scripts/diagnostico/ → repo root
LOC_CSV   = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
CASOS_CSV = ROOT / "output" / "parser" / "csjn_casos.csv"
MAPA_CSV  = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS    = ROOT / "corpus"
OUT_DIR   = ROOT / "output" / "diagnostico"

# ── Importar funciones del parser y auditor ──────────────────────────────────
# auditar_fallo importa como `from pipeline.parser import ...`
# → necesitamos scripts/ en sys.path
sys.path.insert(0, str(ROOT / "scripts"))

from pipeline.parser import (
    linea_es_header_sumario,
    linea_es_firma_de_juez,
    RE_APERTURA,
    RE_DICT_HDR,
    RE_PAGE_HEADER,
)
from auditoria.auditar_fallo import es_header_sumario_auditoria


# ── Parte 0: Resumen rápido desde csjn_casos.csv ────────────────────────────

def resumen_csv():
    """Cuenta pista_fin y cruza con firma_raw."""
    print("=" * 70)
    print("PARTE 0: Resumen desde csjn_casos.csv")
    print("=" * 70)

    pista_counter = Counter()
    pista_x_firma = Counter()  # (pista_fin, tiene_firma) → count
    total = 0

    with open(CASOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("tipo_entrada") == "sumario_con_link":
                continue
            total += 1
            pista = row.get("pista_fin", "")
            firma = row.get("firma_raw", "").strip()
            tiene_firma = "con_firma" if firma else "sin_firma"
            pista_counter[pista] += 1
            pista_x_firma[(pista, tiene_firma)] += 1

    print(f"\nTotal fallos (excl. sumario_con_link): {total}\n")
    print(f"{'pista_fin':<35} {'total':>6}  {'con_firma':>10}  {'sin_firma':>10}")
    print("-" * 70)
    for pista, cnt in pista_counter.most_common():
        cf = pista_x_firma.get((pista, "con_firma"), 0)
        sf = pista_x_firma.get((pista, "sin_firma"), 0)
        print(f"{pista:<35} {cnt:>6}  {cf:>10}  {sf:>10}")
    print()


# ── Parte 1: Comparación línea por línea en zona Pista 2 ────────────────────

def cargar_headers_mapa():
    """Carga mapa_paginas.csv → dict {(tomo, archivo): [(linea, pagina), ...]}"""
    por_archivo = {}
    with open(MAPA_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (int(row["tomo"]), row["archivo"])
            por_archivo.setdefault(key, []).append(
                (int(row["linea_header"]), int(row["pagina"]))
            )
    for k in por_archivo:
        por_archivo[k].sort()
    return por_archivo


def cargar_localizacion():
    """Carga fallos_localizados.csv → lista de dicts (solo con archivo y lineas)."""
    filas = []
    with open(LOC_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("archivo") or not row.get("linea_inicio"):
                continue
            if row.get("tipo_entrada") == "sumario_con_link":
                continue
            try:
                li = int(row["linea_inicio"])
                lf = int(row["linea_fin"]) if row.get("linea_fin") else None
            except (ValueError, TypeError):
                continue
            filas.append({
                "caso_id": row["caso_id_canonico"],
                "tomo": int(row["tomo"]),
                "archivo": row["archivo"],
                "linea_inicio": li,
                "linea_fin": lf,
                "nombres_indice": row.get("nombres_indice", ""),
            })
    return filas


def proximo_header_despues_de(headers_archivo, linea):
    for ln, _pg in headers_archivo:
        if ln > linea:
            return ln
    return None


def es_header_pagina(linea):
    """Proxy simple: línea que matchea RE_PAGE_HEADER del auditor."""
    return bool(RE_PAGE_HEADER.match(linea.strip()))


def es_marcador_apertura(linea):
    s = linea.strip()
    return (RE_APERTURA.match(s) is not None
            or RE_DICT_HDR.match(s) is not None
            or s.upper().startswith("DICTAMEN"))


def clasificar_linea(linea):
    """Clasifica una línea que matcheó solo en el parser."""
    s = linea.strip()
    if linea_es_firma_de_juez(linea):
        return "firma_juez"
    if es_header_pagina(linea):
        return "header_pagina"
    if es_marcador_apertura(linea):
        return "marcador_apertura"
    # Heurística simple para carátula: tiene "c/" o "s/" o "|"
    if "c/" in s or "s/" in s or "|" in s:
        return "posible_caratula"
    # Línea mayúsculas pura corta (firma sin juez conocido?)
    n_mayus = sum(1 for c in s if c.isupper())
    n_minus = sum(1 for c in s if c.islower())
    if len(s) <= 60 and n_mayus > n_minus:
        return "linea_mayus_corta"
    return "otro"


def diagnostico_linea_por_linea():
    """
    Para cada fallo, evalúa las dos funciones en la zona Pista 2
    de detectar_fin_real y reporta divergencias.
    """
    print("=" * 70)
    print("PARTE 1: Comparación línea por línea en zona Pista 2")
    print("=" * 70)

    headers_mapa = cargar_headers_mapa()
    filas_loc = cargar_localizacion()

    # Agrupar por archivo
    por_archivo = {}
    for f in filas_loc:
        path = CORPUS / f["archivo"]
        por_archivo.setdefault(path, []).append(f)

    # Contadores globales
    total_lineas_zona = 0
    match_solo_parser = 0
    match_solo_auditor = 0
    match_ambos = 0
    match_ninguno = 0
    clasificacion_solo_parser = Counter()
    # Detalle para CSV
    detalle_rows = []

    archivos_procesados = 0

    for filepath in sorted(por_archivo.keys(), key=lambda p: p.name):
        if not filepath.exists():
            continue

        with open(filepath, encoding="utf-8") as fh:
            lines = fh.readlines()
        n = len(lines)

        fallos = por_archivo[filepath]
        tomos = set(f["tomo"] for f in fallos)
        headers_archivo = []
        for t in tomos:
            headers_archivo.extend(headers_mapa.get((t, filepath.name), []))
        headers_archivo.sort()

        for fallo in fallos:
            li = fallo["linea_inicio"]
            lf_cat = fallo["linea_fin"]
            if lf_cat is None:
                lf_cat = n - 1
            lfc = min(n - 1, lf_cat)
            li = max(0, li)

            # Calcular limite_adelante (replica detectar_fin_real)
            prox_header = proximo_header_despues_de(headers_archivo, lfc)
            if prox_header is not None and prox_header > lfc:
                limite_adelante = min(prox_header + 50, n - 1)
            else:
                limite_adelante = min(lfc + 200, n - 1)

            # Zona Pista 2 atrás: mitad_bloque → lfc
            mitad_bloque = li + (lfc - li) // 2

            # Evaluar zona atrás (mitad_bloque → lfc)
            for k in range(mitad_bloque, lfc + 1):
                if k < 0 or k >= n:
                    continue
                linea = lines[k]
                total_lineas_zona += 1
                mp = linea_es_header_sumario(linea)
                ma = es_header_sumario_auditoria(linea)

                if mp and ma:
                    match_ambos += 1
                elif mp and not ma:
                    match_solo_parser += 1
                    cls = clasificar_linea(linea)
                    clasificacion_solo_parser[cls] += 1
                    detalle_rows.append({
                        "caso_id": fallo["caso_id"],
                        "tomo": fallo["tomo"],
                        "linea_abs": k,
                        "zona": "atras",
                        "clasificacion": cls,
                        "texto": linea.rstrip()[:120],
                    })
                elif not mp and ma:
                    match_solo_auditor += 1
                else:
                    match_ninguno += 1

            # Evaluar zona adelante (lfc+1 → limite_adelante)
            for k in range(lfc + 1, limite_adelante + 1):
                if k < 0 or k >= n:
                    continue
                linea = lines[k]
                total_lineas_zona += 1
                mp = linea_es_header_sumario(linea)
                ma = es_header_sumario_auditoria(linea)

                if mp and ma:
                    match_ambos += 1
                elif mp and not ma:
                    match_solo_parser += 1
                    cls = clasificar_linea(linea)
                    clasificacion_solo_parser[cls] += 1
                    detalle_rows.append({
                        "caso_id": fallo["caso_id"],
                        "tomo": fallo["tomo"],
                        "linea_abs": k,
                        "zona": "adelante",
                        "clasificacion": cls,
                        "texto": linea.rstrip()[:120],
                    })
                elif not mp and ma:
                    match_solo_auditor += 1
                else:
                    match_ninguno += 1

        archivos_procesados += 1

    # ── Reporte ──────────────────────────────────────────────────────────────
    print(f"\nArchivos procesados: {archivos_procesados}")
    print(f"Total líneas evaluadas en zona Pista 2: {total_lineas_zona:,}")
    print()
    print(f"  Match ambas funciones:     {match_ambos:>7,}  (sumarios reales probables)")
    print(f"  Match solo parser:         {match_solo_parser:>7,}  ← FALSOS POSITIVOS candidatos")
    print(f"  Match solo auditor:        {match_solo_auditor:>7,}  (auditor más permisivo aquí)")
    print(f"  Match ninguna:             {match_ninguno:>7,}")
    print()

    if clasificacion_solo_parser:
        print("Clasificación de 'solo parser' (falsos positivos candidatos):")
        print(f"  {'tipo':<25} {'count':>7}")
        print("  " + "-" * 35)
        for cls, cnt in clasificacion_solo_parser.most_common():
            print(f"  {cls:<25} {cnt:>7}")
    print()

    # ── Guardar detalle CSV ──────────────────────────────────────────────────
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "pista2_sumario_detalle.csv"
    if detalle_rows:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "caso_id", "tomo", "linea_abs", "zona", "clasificacion", "texto"
            ])
            writer.writeheader()
            writer.writerows(detalle_rows)
        print(f"Detalle guardado en: {out_path}")
        print(f"  ({len(detalle_rows)} líneas de falso positivo del parser)")
    else:
        print("Sin falsos positivos detectados (nada que guardar).")

    # ── Muestra de las primeras 20 líneas solo-parser ────────────────────────
    if detalle_rows:
        print()
        print("Muestra (primeras 20 líneas solo-parser):")
        print("-" * 70)
        for row in detalle_rows[:20]:
            print(f"  [{row['clasificacion']:<20}] T{row['tomo']} L{row['linea_abs']:>5} | {row['texto'][:70]}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Validar que existen los archivos necesarios
    for p, desc in [(LOC_CSV, "fallos_localizados.csv"),
                    (CASOS_CSV, "csjn_casos.csv"),
                    (MAPA_CSV, "mapa_paginas.csv")]:
        if not p.exists():
            print(f"ERROR: no se encuentra {desc} en {p}")
            sys.exit(1)

    resumen_csv()
    diagnostico_linea_por_linea()
