"""
H053-B Diagnóstico — 15 casos discrepantes de firma.

Zonificador detecta firma, parser no. Para cada caso:
1. Reconstruye bloque
2. Zonifica
3. Muestra las líneas de zona "firma"
4. Intenta detectar jueces conocidos en esas líneas
5. Clasifica modo de falla

Uso (PowerShell, desde raíz del repo):
  python scripts/auditoria/H053/diag_firma_15.py
"""

import sys
import csv
import importlib.util
from pathlib import Path
from collections import Counter

# ── Setup ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSER_PATH = REPO_ROOT / "scripts" / "pipeline" / "parser.py"

_spec = importlib.util.spec_from_file_location("csjn_parser", str(PARSER_PATH))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

zonificar_bloque = _mod.zonificar_bloque
construir_bloque_desde_localizacion = _mod.construir_bloque_desde_localizacion
refinar_inicio_por_titulo = _mod.refinar_inicio_por_titulo
linea_es_firma_de_juez = _mod.linea_es_firma_de_juez
JUECES_CONOCIDOS = _mod.JUECES_CONOCIDOS
collect_firma_lines = _mod.collect_firma_lines
buscar_firma_inversa = _mod.buscar_firma_inversa

CSV_CASOS = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# Los 15 discrepantes (zonif_firma=True, parser=sin_firma)
DISCREPANTES = [
    "329_p1568", "329_p1928", "329_p3564", "329_p4135", "329_p4170",
    "329_p4176", "329_p5151", "330_p1643", "330_p4071", "334_p1920",
    "344_p1102", "345_p378", "345_p715", "346_p1068", "347_p1084",
]


def reconstruir_bloque(caso, lines):
    li = int(caso["linea_inicio"]) if caso["linea_inicio"] else 0
    lfr = int(caso["linea_fin_real"]) if caso["linea_fin_real"] else (
        int(caso["linea_fin"]) if caso["linea_fin"] else len(lines) - 1)
    bloque = construir_bloque_desde_localizacion(lines, li, lfr)
    if not bloque:
        return None
    nombres_indice = caso.get("case_name_indice", "")
    offset, ancla = refinar_inicio_por_titulo(bloque, nombres_indice)
    if offset > 0:
        bloque = bloque[offset:]
    return bloque if bloque else None


def jueces_en_linea(linea):
    """Retorna lista de jueces conocidos que matchean en la línea."""
    encontrados = []
    for pat, nombre in JUECES_CONOCIDOS:
        if pat.search(linea):
            encontrados.append(nombre)
    return encontrados


def main():
    # Cargar casos
    with open(CSV_CASOS, encoding="utf-8") as f:
        todos = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

    cache_lines = {}
    clasificacion = Counter()

    for caso_id in DISCREPANTES:
        caso = todos.get(caso_id)
        if not caso:
            print(f"\n{'='*70}")
            print(f"  {caso_id}: NO ENCONTRADO EN CSV")
            continue

        sf = caso["source_file"]
        if sf not in cache_lines:
            path = CORPUS_DIR / sf
            if path.exists():
                cache_lines[sf] = path.read_text(encoding="utf-8").split("\n")
            else:
                cache_lines[sf] = None

        lines = cache_lines[sf]
        if lines is None:
            print(f"\n{'='*70}")
            print(f"  {caso_id}: ARCHIVO {sf} NO ENCONTRADO")
            continue

        bloque = reconstruir_bloque(caso, lines)
        if not bloque:
            print(f"\n{'='*70}")
            print(f"  {caso_id}: BLOQUE VACÍO")
            continue

        zonas, anclas = zonificar_bloque(bloque)

        # Líneas en zona firma
        lineas_firma = [(k, bloque[k]) for k in range(len(bloque))
                        if zonas[k] == "firma"]

        # Jueces encontrados en zona firma
        jueces_en_firma = []
        for k, linea in lineas_firma:
            js = jueces_en_linea(linea)
            if js:
                jueces_en_firma.extend([(k, j) for j in js])

        # Distribución de zonas
        zonas_dist = Counter(zonas)

        # Clasificar modo de falla
        tiene_dispositivo = "dispositivo" in set(zonas)
        tiene_cuerpo = "cuerpo" in set(zonas)
        n_firma_lines = len(lineas_firma)
        n_jueces_firma = len(jueces_en_firma)

        if n_firma_lines == 0:
            modo = "sin_zona_firma (falso positivo en zonificacion_h052?)"
        elif n_jueces_firma == 0:
            modo = "firma_sin_juez_conocido"
        elif not tiene_dispositivo:
            modo = "firma_ok_pero_sin_dispositivo"
        else:
            modo = "firma_y_dispositivo_ok (parser debería detectar)"

        clasificacion[modo] += 1

        # ── Imprimir ──────────────────────────────────────────────────────
        print(f"\n{'='*70}")
        print(f"  {caso_id}  tomo={caso['tomo']}  span={len(bloque)}")
        print(f"  outcome={caso['outcome']}  status={caso['status_localizacion']}")
        print(f"  Zonas: {dict(zonas_dist)}")
        print(f"  Modo de falla: {modo}")
        print(f"  Líneas en zona firma: {n_firma_lines}")
        print(f"  Jueces conocidos en zona firma: {n_jueces_firma}")

        if jueces_en_firma:
            print(f"  Jueces encontrados:")
            for k, j in jueces_en_firma:
                print(f"    L{k}: {j}")

        # Mostrar líneas de zona firma (max 20)
        if lineas_firma:
            print(f"\n  --- Zona firma (primeras 20 líneas) ---")
            for k, linea in lineas_firma[:20]:
                tag = " ← JUEZ" if jueces_en_linea(linea) else ""
                print(f"    [{k:4d}] {linea.rstrip()[:100]}{tag}")
            if len(lineas_firma) > 20:
                print(f"    ... ({len(lineas_firma) - 20} líneas más)")

        # Mostrar contexto: últimas líneas del bloque (zona de cada una)
        print(f"\n  --- Últimas 15 líneas del bloque ---")
        start = max(0, len(bloque) - 15)
        for k in range(start, len(bloque)):
            print(f"    [{k:4d}|{zonas[k]:<14}] {bloque[k].rstrip()[:100]}")

    # Resumen
    print(f"\n{'='*70}")
    print(f"RESUMEN DE CLASIFICACIÓN:")
    for modo, n in clasificacion.most_common():
        print(f"  {modo}: {n}")


if __name__ == "__main__":
    main()
