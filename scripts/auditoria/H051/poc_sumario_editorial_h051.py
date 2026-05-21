"""
PoC H051 Paso 2 — Validación de reclasificación sumario_editorial.

Simula el check propuesto para parser.py: un bloque sin RE_APERTURA,
sin RE_FECHA_LINEA, sin RE_CONSIDERANDO y sin "Vistos los autos" se
reclasifica como sumario_editorial.

Corre sobre todo el corpus y reporta:
  - Cuántos se reclasificarían
  - Cuántos tienen firma actualmente (= regresión si se reclasifican)
  - Lista de candidatos con metadata

Uso:
  python scripts/auditoria/H051/poc_sumario_editorial_h051.py
"""

import csv
import re
import importlib.util
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSER_PATH = REPO_ROOT / "scripts" / "pipeline" / "parser.py"
CSV_CASOS = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# Importar parser
_spec = importlib.util.spec_from_file_location("csjn_parser", str(PARSER_PATH))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

RE_APERTURA = _mod.RE_APERTURA
RE_FECHA_LINEA = _mod.RE_FECHA_LINEA
RE_CONSIDERANDO = _mod.RE_CONSIDERANDO
RE_VISTOS_LOS_AUTOS = _mod.RE_VISTOS_LOS_AUTOS
detectar_apertura_dispositivo = _mod.detectar_apertura_dispositivo
linea_es_firma_de_juez = _mod.linea_es_firma_de_juez
construir_bloque_desde_localizacion = _mod.construir_bloque_desde_localizacion
refinar_inicio_por_titulo = _mod.refinar_inicio_por_titulo

# Cargar casos
with open(CSV_CASOS, encoding="utf-8") as f:
    casos = list(csv.DictReader(f))

fallos = [r for r in casos if r["tipo_entrada"] == "fallo"]
print(f"Fallos en CSV: {len(fallos)}")

# Cache de archivos
cache = {}
def cargar(sf):
    if sf not in cache:
        p = CORPUS_DIR / sf
        cache[sf] = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
    return cache[sf]

# Simular check
candidatos = []
regresiones = []

for caso in fallos:
    sf = caso["source_file"]
    lines = cargar(sf)
    if lines is None:
        continue

    li = int(caso["linea_inicio"]) if caso["linea_inicio"] else 0
    lfr = int(caso["linea_fin_real"]) if caso["linea_fin_real"] else (
        int(caso["linea_fin"]) if caso["linea_fin"] else len(lines) - 1)

    bloque = construir_bloque_desde_localizacion(lines, li, lfr)
    if not bloque:
        continue

    nombres_indice = caso.get("case_name_indice", "")
    offset, ancla = refinar_inicio_por_titulo(bloque, nombres_indice)
    if offset > 0:
        bloque = bloque[offset:]
    if not bloque:
        continue

    # ── Check propuesto ──────────────────────────────────────────────
    tiene_apertura = False
    tiene_fecha = False
    tiene_considerando = False
    tiene_vistos = False
    tiene_dispositivo = False
    tiene_firma = False

    for ln in bloque:
        s = ln.strip()
        if not s:
            continue
        if RE_APERTURA.match(s):
            tiene_apertura = True
            break  # suficiente, es fallo
        if RE_FECHA_LINEA.match(s):
            tiene_fecha = True
        if RE_CONSIDERANDO.match(s):
            tiene_considerando = True
        if RE_VISTOS_LOS_AUTOS.match(ln):
            tiene_vistos = True
        if not tiene_dispositivo:
            es_disp, _ = detectar_apertura_dispositivo(s)
            if es_disp:
                tiene_dispositivo = True
        if not tiene_firma and linea_es_firma_de_juez(ln):
            tiene_firma = True

    es_sumario_editorial = (not tiene_apertura and not tiene_fecha
                            and not tiene_considerando and not tiene_vistos
                            and not tiene_dispositivo and not tiene_firma)

    if es_sumario_editorial:
        tiene_firma = caso["voting_pattern"] != "sin_firma"
        entry = {
            "caso_id": caso["caso_id_canonico"],
            "tomo": caso["tomo"],
            "span": len(bloque),
            "firma_actual": caso["voting_pattern"],
            "outcome": caso["outcome"],
        }
        if tiene_firma:
            regresiones.append(entry)
        else:
            candidatos.append(entry)

# Reporte
print(f"\n{'='*60}")
print(f"RESULTADOS")
print(f"{'='*60}")
print(f"  Candidatos a sumario_editorial: {len(candidatos)}")
print(f"  Regresiones (tienen firma):     {len(regresiones)}")

if regresiones:
    print(f"\n⚠ REGRESIONES — estos casos tienen firma y se reclasificarían:")
    for r in regresiones:
        print(f"  {r['caso_id']} (t{r['tomo']}) firma={r['firma_actual']} outcome={r['outcome']}")

print(f"\nCandidatos ({len(candidatos)}):")
tomos = Counter(c["tomo"] for c in candidatos)
print(f"  Por tomo: {dict(sorted(tomos.items(), key=lambda x: int(x[0])))}")
for c in candidatos:
    print(f"  {c['caso_id']} (t{c['tomo']}, span={c['span']}) outcome={c['outcome']}")

# Impacto en sin_firma
n_sf_actual = sum(1 for r in fallos if r["voting_pattern"] == "sin_firma")
n_sf_nuevo = n_sf_actual - len(candidatos)
print(f"\nImpacto:")
print(f"  sin_firma actual:  {n_sf_actual}")
print(f"  reclasificados:   -{len(candidatos)}")
print(f"  sin_firma nuevo:   {n_sf_nuevo}")
print(f"  (regresiones:      {len(regresiones)})")
