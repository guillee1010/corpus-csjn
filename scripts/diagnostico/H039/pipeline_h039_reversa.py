"""
pipeline_h039_reversa.py — Pipeline paralelo H039 (reversa desde votos)
========================================================================
Copia parser.py en memoria, cambia la búsqueda de dispositivo a reversa
(desde inicio_votos_indiv hacia arriba), agrega las 9 variantes, y corre
el pipeline completo.

Hipótesis: la reversa encuentra el dispositivo real primero (está cerca
de votos/firma) y nunca llega al texto argumental de arriba.

Uso:
  $env:PYTHONIOENCODING = "utf-8"
  python scripts/diagnostico/H039/pipeline_h039_reversa.py
"""

import csv
import importlib.util
import re
import shutil
import sys
import tempfile
from pathlib import Path
from collections import Counter

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent.parent

# ── Crear parser modificado en temp ──────────────────────────────────────────

PARSER_ORIGINAL = _REPO_ROOT / "scripts" / "pipeline" / "parser.py"
TEMP_DIR = Path(tempfile.mkdtemp(prefix="h039_"))
TEMP_PARSER = TEMP_DIR / "parser_h039_rev.py"

# Leer, parchear, escribir
source = PARSER_ORIGINAL.read_text(encoding="utf-8")

# 1. Cambiar forward a reverse en la búsqueda de dispositivo
OLD_RANGE = "for k in range(inicio_busqueda, fin_busqueda):"
NEW_RANGE = "for k in range(fin_busqueda - 1, inicio_busqueda - 1, -1):"
assert OLD_RANGE in source, f"No encontré la línea de búsqueda forward en parser.py"
source = source.replace(OLD_RANGE, NEW_RANGE, 1)  # solo la primera ocurrencia

# 2. Agregar 9 variantes al final de RE_DISPOSITIVO_VARIANTES
OLD_LIST_END = '    ("atento_a",          re.compile(r"^Atento\\s+(a\\s+)?(que|lo|el)\\b", re.I)),\n]'
NEW_LIST_END = '''    ("atento_a",          re.compile(r"^Atento\\s+(a\\s+)?(que|lo|el)\\b", re.I)),
    # ── H039: variantes nuevas ───────────────────────────────────────
    ("por_lo_expresado",        re.compile(r"^Por lo expresado\\b", re.I)),
    ("por_las_razones",         re.compile(r"^Por las razones\\b", re.I)),
    ("por_las_consideraciones", re.compile(r"^Por las consideraciones\\b", re.I)),
    ("en_atencion",             re.compile(r"^En atenci[óo]n\\b", re.I)),
    ("en_las_condiciones",      re.compile(r"^En las condiciones\\b", re.I)),
    ("por_lo_tanto",            re.compile(r"^Por lo tanto\\b", re.I)),
    ("oido_el",                 re.compile(r"^O[íi]dos?\\s+(el|la|los|las)\\b", re.I)),
    ("que_por_ello",            re.compile(r"^Que[,]?\\s+por\\s+ello\\b", re.I)),
    ("que_de_conformidad",      re.compile(r"^Que[,]?\\s+de\\s+conformidad\\b", re.I)),
]'''
assert OLD_LIST_END in source, "No encontré el fin de RE_DISPOSITIVO_VARIANTES"
source = source.replace(OLD_LIST_END, NEW_LIST_END, 1)

TEMP_PARSER.write_text(source, encoding="utf-8")
print(f"Parser modificado en: {TEMP_PARSER}")

# ── Importar el parser parcheado ─────────────────────────────────────────────

spec = importlib.util.spec_from_file_location("parser_h039_rev", str(TEMP_PARSER))
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

print(f"RE_DISPOSITIVO_VARIANTES: {len(parser.RE_DISPOSITIVO_VARIANTES)} entradas")

# ── Rutas ────────────────────────────────────────────────────────────────────

LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS_DIR = _REPO_ROOT / "corpus"
CSV_PRODUCTIVO = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
OUTPUT_DIR = _REPO_ROOT / "output" / "diagnostico" / "H039"

OUTPUT_CASOS = OUTPUT_DIR / "csjn_casos_h039.csv"
OUTPUT_VOTOS = OUTPUT_DIR / "csjn_casos_votos_h039.csv"

# ── Pipeline ─────────────────────────────────────────────────────────────────

def run_pipeline():
    print("Cargando localizados...")
    filas_loc, n_sin = parser.cargar_localizados(str(LOCALIZADOS))
    print(f"  {len(filas_loc)} filas ({n_sin} descartadas)")

    print("Cargando mapa de páginas...")
    headers_por_archivo = parser.cargar_proximos_headers(str(MAPA))

    primer_token_por_caso = {
        row["caso_id_canonico"]: parser.primer_token_de_caratula(
            row.get("nombres_indice", "")
        )
        for row in filas_loc
    }

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

    grupos = parser.agrupar_por_archivo(filas_loc, str(CORPUS_DIR))

    todos_casos = []
    todos_votos = []
    desconocidos_global = Counter()

    print(f"Procesando {len(grupos)} archivos...")
    for i, filepath in enumerate(sorted(grupos.keys(), key=lambda p: p.name)):
        if not filepath.exists():
            continue
        fallos_arch = grupos[filepath]
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
    print("\n" + "=" * 70)
    print("COMPARACIÓN vs CSV productivo")
    print("=" * 70)
    with open(CSV_PRODUCTIVO, encoding="utf-8") as f:
        prod = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}
    nuevo = {c["caso_id_canonico"]: c for c in casos_nuevos}

    prod_fallos = {k: v for k, v in prod.items() if v["tipo_entrada"] == "fallo"}
    nuevo_fallos = {k: v for k, v in nuevo.items() if v.get("tipo_entrada") == "fallo"}
    prod_sf = sum(1 for v in prod_fallos.values() if v["voting_pattern"] == "sin_firma")
    nuevo_sf = sum(1 for v in nuevo_fallos.values() if v.get("voting_pattern") == "sin_firma")

    print(f"Fallos productivo: {len(prod_fallos)}, nuevo: {len(nuevo_fallos)}")
    print(f"Sin firma productivo: {prod_sf}, nuevo: {nuevo_sf} (delta: {nuevo_sf - prod_sf})")
    print()

    mejoras = []
    regresiones = []
    cambio_outcome = []

    for cid in sorted(prod_fallos.keys()):
        if cid not in nuevo:
            continue
        p, n = prod[cid], nuevo[cid]
        if p["tipo_entrada"] != "fallo":
            continue
        vp_a, vp_d = p["voting_pattern"], n.get("voting_pattern", "")
        out_a, out_d = p["outcome"], n.get("outcome", "")

        if vp_a == "sin_firma" and vp_d != "sin_firma":
            mejoras.append({"caso_id": cid, "tomo": p["tomo"],
                "out_a": out_a, "out_d": out_d, "vp_d": vp_d,
                "nj": n.get("n_jueces",""), "pet": n.get("por_ello_text","")[:100]})
        elif vp_a != "sin_firma" and vp_d == "sin_firma":
            regresiones.append({"caso_id": cid, "tomo": p["tomo"],
                "vp_a": vp_a, "out_a": out_a, "out_d": out_d})
        elif out_a != out_d:
            cambio_outcome.append({"caso_id": cid, "tomo": p["tomo"],
                "out_a": out_a, "out_d": out_d, "vp_a": vp_a, "vp_d": vp_d})

    print(f"MEJORAS (sin_firma → con_firma): {len(mejoras)}")
    for m in mejoras[:25]:
        print(f"  {m['caso_id']} (t{m['tomo']}): {m['out_a']}→{m['out_d']} "
              f"vp={m['vp_d']} nj={m['nj']}")
    if len(mejoras) > 25:
        print(f"  ... y {len(mejoras) - 25} más")
    print()

    print(f"REGRESIONES (con_firma → sin_firma): {len(regresiones)}")
    for r in regresiones[:10]:
        print(f"  ⚠ {r['caso_id']} (t{r['tomo']}): vp={r['vp_a']} {r['out_a']}→{r['out_d']}")
    print()

    print(f"CAMBIO OUTCOME (sin cambio firma): {len(cambio_outcome)}")
    for c in cambio_outcome[:15]:
        print(f"  {c['caso_id']}: {c['out_a']}→{c['out_d']} vp={c['vp_a']}→{c['vp_d']}")
    if len(cambio_outcome) > 15:
        print(f"  ... y {len(cambio_outcome) - 15} más")

    print()
    print("Mejoras por tomo:")
    ct = Counter(m["tomo"] for m in mejoras)
    for t, v in ct.most_common():
        print(f"  tomo {t}: {v}")


if __name__ == "__main__":
    casos = run_pipeline()
    comparar(casos)
    # Limpiar temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
