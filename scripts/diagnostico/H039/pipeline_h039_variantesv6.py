"""
pipeline_h039_variantes.py — Pipeline paralelo H039
====================================================
Agrega 6 variantes seguras a RE_DISPOSITIVO_VARIANTES sin tocar parser.py.
Corre el pipeline completo y compara contra el CSV productivo.

Uso (desde raíz del repo):
  $env:PYTHONIOENCODING = "utf-8"
  python scripts/diagnostico/H039/pipeline_h039_variantes.py

Output:
  - output/diagnostico/H039/csjn_casos_h039.csv
  - output/diagnostico/H039/csjn_casos_votos_h039.csv
  - Resumen de comparación a stdout
"""

import csv
import re
import sys
from pathlib import Path
from collections import Counter

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

# ── Importar parser y monkey-patch las variantes ─────────────────────────────

from pipeline import parser

NUEVAS_VARIANTES = [
    # ── H039: variantes seguras (no aparecen en texto argumental) ────────
    # Descartadas por falsos positivos en forward: en_las_condiciones (40),
    # por_lo_tanto (17), en_atencion (17). Ver analizar_cambios.py.
    ("por_lo_expresado",        re.compile(r"^Por lo expresado\b", re.I)),
    ("por_las_razones",         re.compile(r"^Por las razones\b", re.I)),
    ("por_las_consideraciones", re.compile(r"^Por las consideraciones\b", re.I)),
    ("oido_el",                 re.compile(r"^O[íi]dos?\s+(el|la|los|las)\b", re.I)),
    ("que_por_ello",            re.compile(r"^Que[,]?\s+por\s+ello\b", re.I)),
    ("que_de_conformidad",      re.compile(r"^Que[,]?\s+de\s+conformidad\b", re.I)),
]

# Agregar al final de la lista (después de las existentes)
parser.RE_DISPOSITIVO_VARIANTES.extend(NUEVAS_VARIANTES)
print(f"RE_DISPOSITIVO_VARIANTES: {len(parser.RE_DISPOSITIVO_VARIANTES)} entradas "
      f"({len(NUEVAS_VARIANTES)} nuevas)")

# ── Rutas ────────────────────────────────────────────────────────────────────

LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS_DIR = _REPO_ROOT / "corpus"
CSV_PRODUCTIVO = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
OUTPUT_DIR = _REPO_ROOT / "output" / "diagnostico" / "H039"

OUTPUT_CASOS = OUTPUT_DIR / "csjn_casos_h039.csv"
OUTPUT_VOTOS = OUTPUT_DIR / "csjn_casos_votos_h039.csv"

# ── Correr pipeline completo ─────────────────────────────────────────────────

def run_pipeline():
    """Corre el pipeline usando las funciones de parser.py (ya patcheadas)."""
    print("Cargando localizados...")
    filas_loc, n_sin = parser.cargar_localizados(str(LOCALIZADOS))
    print(f"  {len(filas_loc)} filas ({n_sin} descartadas)")

    print("Cargando mapa de páginas...")
    headers_por_archivo = parser.cargar_proximos_headers(str(MAPA))

    # Construir primer_token_por_caso (igual que main())
    primer_token_por_caso = {
        row["caso_id_canonico"]: parser.primer_token_de_caratula(
            row.get("nombres_indice", "")
        )
        for row in filas_loc
    }

    # Construir siguiente_caso (igual que main())
    cat_por_tomo = {}
    for row in filas_loc:
        cat_por_tomo.setdefault(int(row["tomo"]), []).append({
            "caso_id_canonico": row["caso_id_canonico"],
            "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
        })
    for t in cat_por_tomo:
        cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
    siguiente_caso = {}
    for t, lst in cat_por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]

    # Agrupar por archivo (igual que main())
    grupos = parser.agrupar_por_archivo(filas_loc, str(CORPUS_DIR))

    todos_casos = []
    todos_votos = []
    desconocidos_global = Counter()

    print(f"Procesando {len(grupos)} archivos...")
    for i, filepath in enumerate(sorted(grupos.keys(), key=lambda p: p.name)):
        if not filepath.exists():
            continue
        fallos_arch = grupos[filepath]

        # Headers del archivo
        tomos_archivo = set(int(r["tomo"]) for r in fallos_arch)
        headers_archivo = []
        for t in tomos_archivo:
            headers_archivo.extend(
                headers_por_archivo.get((t, filepath.name), [])
            )
        headers_archivo.sort()

        casos, votos, descon = parser.procesar_archivo(
            filepath, fallos_arch, headers_archivo,
            primer_token_por_caso, siguiente_caso,
        )
        todos_casos.extend(casos)
        todos_votos.extend(votos)
        desconocidos_global.update(descon)

        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(grupos)} archivos...")

    # Guardar
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if todos_casos:
        keys = todos_casos[0].keys()
        with open(OUTPUT_CASOS, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(todos_casos)
        print(f"Casos: {len(todos_casos)} → {OUTPUT_CASOS}")

    if todos_votos:
        keys_v = todos_votos[0].keys()
        with open(OUTPUT_VOTOS, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys_v)
            w.writeheader()
            w.writerows(todos_votos)
        print(f"Votos: {len(todos_votos)} → {OUTPUT_VOTOS}")

    return todos_casos


def comparar(casos_nuevos):
    """Compara CSV nuevo vs productivo campo por campo."""
    print("\n" + "=" * 70)
    print("COMPARACIÓN vs CSV productivo")
    print("=" * 70)

    # Cargar productivo
    with open(CSV_PRODUCTIVO, encoding="utf-8") as f:
        prod = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

    nuevo = {c["caso_id_canonico"]: c for c in casos_nuevos}

    # Conteos globales
    prod_fallos = {k: v for k, v in prod.items() if v["tipo_entrada"] == "fallo"}
    nuevo_fallos = {k: v for k, v in nuevo.items() if v.get("tipo_entrada") == "fallo"}

    prod_sf = sum(1 for v in prod_fallos.values() if v["voting_pattern"] == "sin_firma")
    nuevo_sf = sum(1 for v in nuevo_fallos.values() if v.get("voting_pattern") == "sin_firma")

    print(f"Fallos productivo: {len(prod_fallos)}, nuevo: {len(nuevo_fallos)}")
    print(f"Sin firma productivo: {prod_sf}, nuevo: {nuevo_sf} (delta: {nuevo_sf - prod_sf})")
    print()

    # Comparar caso a caso
    campos_clave = [
        "outcome", "voting_pattern", "n_jueces", "firma_raw",
        "por_ello_text", "apertura_tipo",
    ]

    mejoras = []       # sin_firma → con_firma
    regresiones = []   # con_firma → sin_firma
    cambio_outcome = []
    cambio_otro = []

    for cid in sorted(prod_fallos.keys()):
        if cid not in nuevo:
            continue
        p = prod[cid]
        n = nuevo[cid]

        if p["tipo_entrada"] != "fallo":
            continue

        vp_antes = p["voting_pattern"]
        vp_despues = n.get("voting_pattern", "")
        out_antes = p["outcome"]
        out_despues = n.get("outcome", "")

        if vp_antes == "sin_firma" and vp_despues != "sin_firma":
            mejoras.append({
                "caso_id": cid,
                "tomo": p["tomo"],
                "outcome_antes": out_antes,
                "outcome_despues": out_despues,
                "vp_despues": vp_despues,
                "n_jueces": n.get("n_jueces", ""),
                "por_ello": n.get("por_ello_text", "")[:100],
            })
        elif vp_antes != "sin_firma" and vp_despues == "sin_firma":
            regresiones.append({
                "caso_id": cid,
                "tomo": p["tomo"],
                "vp_antes": vp_antes,
                "outcome_antes": out_antes,
                "outcome_despues": out_despues,
            })
        elif out_antes != out_despues:
            cambio_outcome.append({
                "caso_id": cid,
                "tomo": p["tomo"],
                "outcome_antes": out_antes,
                "outcome_despues": out_despues,
                "vp_antes": vp_antes,
                "vp_despues": vp_despues,
            })

    print(f"MEJORAS (sin_firma → con_firma): {len(mejoras)}")
    for m in mejoras[:20]:
        print(f"  {m['caso_id']} (tomo {m['tomo']}): {m['outcome_antes']}→{m['outcome_despues']} "
              f"vp={m['vp_despues']} n_jueces={m['n_jueces']}")
    if len(mejoras) > 20:
        print(f"  ... y {len(mejoras) - 20} más")
    print()

    print(f"REGRESIONES (con_firma → sin_firma): {len(regresiones)}")
    for r in regresiones[:10]:
        print(f"  ⚠ {r['caso_id']} (tomo {r['tomo']}): vp={r['vp_antes']} "
              f"outcome={r['outcome_antes']}→{r['outcome_despues']}")
    print()

    print(f"CAMBIO OUTCOME (sin cambio firma): {len(cambio_outcome)}")
    for c in cambio_outcome[:10]:
        print(f"  {c['caso_id']}: {c['outcome_antes']}→{c['outcome_despues']} "
              f"vp={c['vp_antes']}→{c['vp_despues']}")
    if len(cambio_outcome) > 10:
        print(f"  ... y {len(cambio_outcome) - 10} más")

    # Resumen por variante nueva
    print()
    print("Mejoras por tomo:")
    c_tomo = Counter(m["tomo"] for m in mejoras)
    for t, v in c_tomo.most_common():
        print(f"  tomo {t}: {v}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    casos = run_pipeline()
    comparar(casos)
