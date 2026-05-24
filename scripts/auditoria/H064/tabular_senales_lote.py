"""
tabular_senales_lote.py — Wrapper de auditar_fallo para análisis tabular en lote
================================================================================

Toma una muestra de N casos (random o filtrada), invoca auditar_fallo() sobre
cada uno, y produce tres outputs:

  1. tabla_senales_<N>_<seed>.csv    — 25 columnas crudas por caso
  2. dicts_<N>_<seed>.json           — dicts completos para re-análisis futuro
  3. auditoria_<N>_<seed>.md         — Markdown del auditor (idéntico al CLI)

No reimplementa lógica de detección. Toda la heurística vive en parser.py
(reusado vía auditar_fallo.py). Este script solo orquesta la corrida en lote
y aplana los dicts en CSV.

CLI:
  python tabular_senales_lote.py
  python tabular_senales_lote.py --random 80 --seed 15052026
  python tabular_senales_lote.py --random 50 --seed 42 --tomo 349
  python tabular_senales_lote.py --random 20 --status ok_cortado_en_indice

Defaults pensados para la auditoría de persistencia de bugs (sesión 2026-05-15):
  --random 80
  --seed 15052026
"""

import argparse
import csv
import json
import random
import sys
from datetime import datetime
from pathlib import Path

# Importar del auditor (mismo directorio)
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from auditar_fallo import (  # noqa: E402
    auditar_fallo,
    _seleccionar_random,
    _render_doc_completo,
    DEFAULT_CORPUS,
    DEFAULT_LOCALIZADOS,
    DEFAULT_MAPA,
    TIPO_CARATULA,
    TIPO_SUMARIO,
    TIPO_DICTAMEN,
    TIPO_CUERPO_MAYORIA,
    TIPO_VOTO,
    TIPO_DISIDENCIA,
    TIPO_FIRMA,
    TIPO_SUMARIO_CON_LINK,
    TIPO_HEADER_PAGINA,
    TIPO_CATCH_ALL,
)

# Reusa también helpers de carga del parser (vía auditar_fallo)
sys.path.insert(0, str(_SCRIPT_DIR.parent))
from pipeline.parser import cargar_localizados, cargar_proximos_headers  # noqa: E402

_REPO_ROOT = _SCRIPT_DIR.parent.parent
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output" / "auditoria" / "auditar_fallo"

# Columnas del CSV (25). Orden importa — define el orden en el archivo.
COLUMNAS_CSV = [
    # Identificación (4)
    "caso_id_canonico", "tomo", "archivo", "pagina_inicio",
    # Cobertura del bloque (5)
    "n_lineas_bloque", "lineas_residuo", "porcentaje_residuo",
    "invariante_cobertura", "invariante_disjuncion",
    # Estructura interna (10)
    "tiene_caratula", "tiene_dictamen", "tiene_cuerpo_mayoria", "tiene_firma",
    "n_sumarios", "n_votos", "n_disidencias",
    "n_sumarios_con_link", "n_catch_all", "n_headers_pagina",
    # Borde inferior (3)
    "borde_estado", "borde_delta", "borde_alertas",
    # Status del parser (3)
    "status_localizacion", "status_fin", "pista_fin",
]


def extraer_columnas(d):
    """Aplana un dict del auditor a las 25 columnas del CSV.

    Si el dict tiene 'error' (caso no resuelto), devuelve fila con
    identificación vacía y columnas numéricas en None / booleanas en False.
    """
    if "error" in d:
        return {
            "caso_id_canonico": d.get("fila", {}).get("caso_id_canonico", "")
                                or f"ERROR_{d.get('tomo', '?')}_{d.get('pagina', '?')}",
            "tomo": d.get("tomo", ""),
            "archivo": d.get("fila", {}).get("archivo", ""),
            "pagina_inicio": d.get("pagina", ""),
            "n_lineas_bloque": "",
            "lineas_residuo": "",
            "porcentaje_residuo": "",
            "invariante_cobertura": "",
            "invariante_disjuncion": "",
            "tiene_caratula": "",
            "tiene_dictamen": "",
            "tiene_cuerpo_mayoria": "",
            "tiene_firma": "",
            "n_sumarios": "",
            "n_votos": "",
            "n_disidencias": "",
            "n_sumarios_con_link": "",
            "n_catch_all": "",
            "n_headers_pagina": "",
            "borde_estado": "",
            "borde_delta": "",
            "borde_alertas": "",
            "status_localizacion": "",
            "status_fin": f"ERROR: {d['error']}",
            "pista_fin": "",
        }

    spans = d.get("spans", [])
    tipos = [sp["tipo"] for sp in spans]

    def conteo(tipo):
        return sum(1 for t in tipos if t == tipo)

    borde = d.get("borde_inferior", {})

    return {
        "caso_id_canonico": d["caso_id_canonico"],
        "tomo": d["tomo"],
        "archivo": d["archivo"],
        "pagina_inicio": d["pagina_inicio"],
        "n_lineas_bloque": d["n_lineas_bloque"],
        "lineas_residuo": d["lineas_residuo"],
        "porcentaje_residuo": d["porcentaje_residuo"],
        "invariante_cobertura": d["invariante_cobertura"],
        "invariante_disjuncion": d["invariante_disjuncion"],
        "tiene_caratula": TIPO_CARATULA in tipos,
        "tiene_dictamen": TIPO_DICTAMEN in tipos,
        "tiene_cuerpo_mayoria": TIPO_CUERPO_MAYORIA in tipos,
        "tiene_firma": TIPO_FIRMA in tipos,
        "n_sumarios": conteo(TIPO_SUMARIO),
        "n_votos": conteo(TIPO_VOTO),
        "n_disidencias": conteo(TIPO_DISIDENCIA),
        "n_sumarios_con_link": conteo(TIPO_SUMARIO_CON_LINK),
        "n_catch_all": conteo(TIPO_CATCH_ALL),
        "n_headers_pagina": conteo(TIPO_HEADER_PAGINA),
        "borde_estado": borde.get("estado", ""),
        "borde_delta": borde.get("delta", ""),
        "borde_alertas": ";".join(borde.get("alertas", [])),
        "status_localizacion": d.get("status_localizacion", ""),
        "status_fin": d.get("status_fin", ""),
        "pista_fin": d.get("pista_fin", ""),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Wrapper de auditar_fallo para tabulación en lote"
    )
    ap.add_argument("--random", type=int, default=80,
                    help="Cantidad de casos a samplear (default: 80)")
    ap.add_argument("--seed", type=int, default=15052026,
                    help="Seed para sampling reproducible (default: 15052026)")
    ap.add_argument("--tomo", type=int, default=None,
                    help="Filtrar muestra por tomo (opcional)")
    ap.add_argument("--status", type=str, default=None,
                    help="Filtrar muestra por status_localizacion (opcional)")
    ap.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR),
                    help=f"Directorio de salida (default: {DEFAULT_OUTPUT_DIR})")
    ap.add_argument("--corpus", type=str, default=str(DEFAULT_CORPUS))
    ap.add_argument("--localizados", type=str, default=str(DEFAULT_LOCALIZADOS))
    ap.add_argument("--mapa", type=str, default=str(DEFAULT_MAPA))
    ap.add_argument("--skip-md", action="store_true", help="No escribir .md")
    ap.add_argument("--skip-json", action="store_true", help="No escribir .json")
    args = ap.parse_args()

    # Validar paths
    for label, p in (("corpus", args.corpus),
                     ("localizados", args.localizados),
                     ("mapa", args.mapa)):
        if not Path(p).exists():
            print(f"ERROR: no encontré '{label}' en `{p}`", file=sys.stderr)
            sys.exit(2)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Cargar CSVs una sola vez (cache compartido entre llamadas)
    print(f"[INFO] Cargando catálogo y mapa...", file=sys.stderr)
    cache = {}
    cache["filas_loc"], _ = cargar_localizados(args.localizados)
    cache["headers_por_archivo"] = cargar_proximos_headers(args.mapa)

    # Sampling reproducible con instancia local de PRNG
    rng = random.Random(args.seed)
    seleccion = _seleccionar_random(
        cache["filas_loc"], args.random,
        tomo=args.tomo, status=args.status, rng=rng,
    )
    if not seleccion:
        print("ERROR: muestra vacía (filtros demasiado restrictivos?)",
              file=sys.stderr)
        sys.exit(2)

    print(f"[INFO] Muestra: {len(seleccion)} casos (seed={args.seed})",
          file=sys.stderr)

    # Construir pares (tomo, pagina) para iterar
    pares = [(int(r["tomo"]), int(r["pagina_inicio"])) for r in seleccion]

    # Auditar cada caso
    resultados = []
    for i, (tomo, pagina) in enumerate(pares, 1):
        if i % 10 == 0 or i == len(pares):
            print(f"[INFO] Auditando {i}/{len(pares)}...", file=sys.stderr)
        r = auditar_fallo(
            tomo, pagina,
            corpus_dir=args.corpus,
            localizados_path=args.localizados,
            mapa_path=args.mapa,
            _cache=cache,
        )
        resultados.append(r)

    # Sufijo común para los tres archivos
    sufijo = f"{args.random}_{args.seed}"

    # === CSV ===
    csv_path = output_dir / f"tabla_senales_{sufijo}.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
        writer.writeheader()
        for r in resultados:
            writer.writerow(extraer_columnas(r))
    print(f"[OK] CSV: {csv_path}", file=sys.stderr)

    # === JSON ===
    if not args.skip_json:
        json_path = output_dir / f"dicts_{sufijo}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON: {json_path}", file=sys.stderr)

    # === MD ===
    if not args.skip_md:
        md_path = output_dir / f"auditoria_{sufijo}.md"
        cmd_str = " ".join(sys.argv[1:])
        md = _render_doc_completo(resultados, cmd_str)
        md_path.write_text(md, encoding="utf-8")
        print(f"[OK] MD:  {md_path}", file=sys.stderr)

    # Resumen
    n_ok = sum(1 for r in resultados if "error" not in r)
    n_err = len(resultados) - n_ok
    print(f"[RESUMEN] {n_ok} casos OK" + (f", {n_err} errores" if n_err else ""),
          file=sys.stderr)


if __name__ == "__main__":
    main()
