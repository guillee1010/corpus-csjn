"""
diag_sumario_link.py
====================
Diagnóstico de casos sumario-con-link en el corpus CSJN.

Detecta casos cuyo bloque de texto:
  (a) contiene el patrón de nota al pie de sumario-con-link
      `(*) Sentencia del ... Ver (en https://sj.csjn.gov.ar | fallo)`
  (b) NO contiene el marcador de apertura `FALLO DE LA CORTE SUPREMA`

Uso:
  python diag_sumario_link.py \
      --casos paginas/csjn_casos_v16_fix1.csv \
      --corpus markdowns_v2 \
      --output paginas/diag_sumario_link.csv

Salida:
  - Tabla CSV con caso_id_canonico, tomo, source_file, voting_pattern,
    outcome, n_patrones (cantidad de notas al pie en el bloque)
  - Resumen en consola: total, por tomo, cruce con sin_firma
"""

import re
import csv
import argparse
from pathlib import Path
from collections import Counter

RE_SUMARIO_LINK = re.compile(
    r"^\(\*\)\s+Sentencia del .+? Ver (en https://sj\.csjn\.gov\.ar|fallo)",
    re.IGNORECASE
)
RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA) DE LA CORTE SUPREMA\s*$")


def cargar_casos(ruta):
    casos = []
    with open(ruta, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            casos.append(row)
    return casos


def procesar(casos, carpeta_corpus):
    carpeta = Path(carpeta_corpus)
    cache_archivos = {}
    resultados = []

    for caso in casos:
        source_file = caso.get("source_file", "")
        if not source_file:
            continue

        filepath = carpeta / source_file
        if not filepath.exists():
            continue

        # Cache de archivos ya leídos
        if source_file not in cache_archivos:
            try:
                cache_archivos[source_file] = filepath.read_text(encoding="utf-8").split("\n")
            except Exception:
                continue
        lines = cache_archivos[source_file]

        # Extraer bloque
        try:
            li = int(caso["linea_inicio"])
            lf = caso.get("linea_fin_real") or caso.get("linea_fin") or ""
            lf = int(lf) if lf not in ("", None) else len(lines) - 1
            lf = min(lf, len(lines) - 1)
        except (ValueError, KeyError):
            continue

        bloque = lines[li:lf + 1]

        # Condición (b): no tiene marcador de apertura
        tiene_apertura = any(RE_APERTURA.match(ln.strip()) for ln in bloque)
        if tiene_apertura:
            continue

        # Condición (a): tiene al menos una nota de sumario-con-link
        n_patrones = sum(1 for ln in bloque if RE_SUMARIO_LINK.match(ln.strip()))
        if n_patrones == 0:
            continue

        resultados.append({
            "caso_id_canonico": caso["caso_id_canonico"],
            "tomo":             caso["tomo"],
            "source_file":      source_file,
            "voting_pattern":   caso.get("voting_pattern", ""),
            "outcome":          caso.get("outcome", ""),
            "status_localizacion": caso.get("status_localizacion", ""),
            "n_patrones":       n_patrones,
            "case_name_indice": caso.get("case_name_indice", ""),
        })

    return resultados


def imprimir_resumen(resultados):
    total = len(resultados)
    print(f"\nTotal casos sumario-con-link detectados: {total}")

    por_tomo = Counter(r["tomo"] for r in resultados)
    print("\n── Por tomo ──")
    for tomo, n in sorted(por_tomo.items(), key=lambda x: int(x[0])):
        print(f"  Tomo {tomo}: {n}")

    por_vp = Counter(r["voting_pattern"] for r in resultados)
    print("\n── Por voting_pattern ──")
    for vp, n in por_vp.most_common():
        print(f"  {vp:<20} {n}")

    por_outcome = Counter(r["outcome"] for r in resultados)
    print("\n── Por outcome ──")
    for oc, n in por_outcome.most_common():
        print(f"  {oc:<25} {n}")

    por_status = Counter(r["status_localizacion"] for r in resultados)
    print("\n── Por status_localizacion ──")
    for st, n in por_status.most_common():
        print(f"  {st:<35} {n}")

    n_sin_firma = sum(1 for r in resultados if r["voting_pattern"] == "sin_firma")
    n_con_firma = total - n_sin_firma
    print(f"\n── Cruce con firma ──")
    print(f"  sin_firma:  {n_sin_firma}")
    print(f"  con firma:  {n_con_firma}  ← revisar manualmente")


def main():
    ap = argparse.ArgumentParser(description="Diagnóstico de sumarios-con-link en corpus CSJN")
    ap.add_argument("--casos",  required=True, help="CSV de casos (csjn_casos_v16_fix1.csv)")
    ap.add_argument("--corpus", required=True, help="Directorio con archivos LibroVol*.md")
    ap.add_argument("--output", default="paginas/diag_sumario_link.csv")
    args = ap.parse_args()

    print(f"Cargando {args.casos}...")
    casos = cargar_casos(args.casos)
    print(f"  {len(casos)} casos cargados")

    print(f"Procesando bloques desde {args.corpus}...")
    resultados = procesar(casos, args.corpus)

    imprimir_resumen(resultados)

    # Guardar CSV
    if resultados:
        fieldnames = ["caso_id_canonico", "tomo", "source_file", "voting_pattern",
                      "outcome", "status_localizacion", "n_patrones", "case_name_indice"]
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados)
        print(f"\n[OK] {args.output}: {len(resultados)} filas")


if __name__ == "__main__":
    main()
