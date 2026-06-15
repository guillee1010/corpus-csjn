#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PoC B019 — extensión del fallback `firma_actual` de detectar_fin_real.

QUÉ MIDE (A/B, sin tocar el pipeline):
  El bug B019: cuando la firma de la Corte wrapea en >1 línea del OCR, el
  fallback `firma_actual` de detectar_fin_real ancla linea_fin_real en la
  PRIMERA línea-firma y deja la continuación afuera del bloque -> firma/votos
  truncados. Confirmado: 18/18 colgantes tienen pista_fin=firma_actual; el
  blast radius del fallback es ~115 casos.

  Este script SIMULA el fix (extender linea_fin_real hacia adelante mientras la
  línea siguiente sea firma) sobre TODOS los casos pista_fin=firma_actual, y
  reporta:
    1) cuántas firmas extiende y cuántos votos recupera (parse_firma real);
    2) SAFETY: que la extensión NUNCA cruce al linea_inicio del caso siguiente
       (riesgo B020/F002, arrastre hacia adelante);
    3) que los casos con firma ya completa NO se toquen (0 cambios).

  NO modifica parser.py ni ningún output. Es el gate "medir antes de implementar".
  Correr en DISCO LOCAL sobre el corpus real (las .md no están en el sandbox).

USO:
  python poc_b019_extender_firma_actual.py \
      --casos   output/parser/csjn_casos.csv \
      --textos  output/parser/csjn_casos_textos.csv \
      --corpus  corpus \
      --parser  scripts/pipeline/parser.py

  (corpus = dir con los LibroVol*.md; parser = ruta al parser.py canónico)
"""
import argparse
import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(10**8)


def cargar_parser(ruta_parser: Path):
    """Importa el parser.py canónico para reusar SUS funciones (Gate 3: no
    reinventar linea_es_firma_de_juez / parse_firma con regex paralelas)."""
    # parser.py importa módulos hermanos por nombre (from parser_editorial
    # import ...); hay que poner su carpeta en sys.path ANTES de importarlo.
    ruta_parser = ruta_parser.resolve()
    if str(ruta_parser.parent) not in sys.path:
        sys.path.insert(0, str(ruta_parser.parent))
    spec = importlib.util.spec_from_file_location("parser_canonico", str(ruta_parser))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # main() está guardado por if __name__
    return mod


def predicado_continuacion_firma(mod, linea: str) -> bool:
    """Continuación = línea-firma con juez reconocido (el MISMO predicado que
    usa el fallback firma_actual para anclar). Deliberadamente NO extiende por
    raya o calificador sueltos: el PoC v1 mostró que eso traga la línea
    editorial 'Recurso ... interpuesto por ... – ...' (tiene raya pero no es
    firma). El wrap legítimo siempre trae el apellido del juez en la
    continuación, así que linea_es_firma_de_juez lo cubre sin falsos positivos."""
    return mod.linea_es_firma_de_juez(linea)


def simular_extension(mod, lines, lfr: int, techo_excl: int):
    """Extiende lfr hacia adelante mientras la línea sea continuación de firma,
    tolerando 1 línea vacía (espejo de collect_firma_lines). NUNCA alcanza
    techo_excl (= linea_inicio del caso siguiente). Devuelve (nuevo_lfr,
    lineas_agregadas, alcanzo_techo)."""
    nuevo = lfr
    agregadas = []
    blancos = 0
    k = lfr + 1
    alcanzo_techo = False
    n = len(lines)
    while k < n:
        if k >= techo_excl:
            alcanzo_techo = True   # SAFETY: la firma seguía hasta el caso siguiente
            break
        s = lines[k].strip()
        if not s:
            blancos += 1
            if blancos > 1:
                break
            k += 1
            continue
        if predicado_continuacion_firma(mod, lines[k]):
            nuevo = k
            agregadas.append(lines[k])
            blancos = 0
            k += 1
            continue
        break  # primera línea no-firma (típicamente "Nombre de los actores")
    return nuevo, agregadas, alcanzo_techo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", required=True, type=Path)
    ap.add_argument("--textos", required=True, type=Path)
    ap.add_argument("--corpus", required=True, type=Path,
                    help="dir con los LibroVol*.md")
    ap.add_argument("--parser", required=True, type=Path,
                    help="ruta a scripts/pipeline/parser.py")
    args = ap.parse_args()

    mod = cargar_parser(args.parser)

    # firma_raw por caso (para el A/B de votos vía parse_firma)
    firma_raw = {}
    with args.textos.open(newline="", encoding="utf-8") as f:
        for x in csv.DictReader(f):
            firma_raw[x["caso_id_canonico"]] = x.get("firma_raw") or ""

    # casos.csv: todos (para el techo del caso siguiente) + filtro firma_actual
    casos = []
    por_archivo = defaultdict(list)  # source_file -> [(linea_inicio, caso_id)]
    with args.casos.open(newline="", encoding="utf-8") as f:
        for x in csv.DictReader(f):
            try:
                li = int(x["linea_inicio"])
            except (ValueError, KeyError):
                continue
            por_archivo[x["source_file"]].append((li, x["caso_id_canonico"]))
            casos.append(x)
    for sf in por_archivo:
        por_archivo[sf].sort()

    def techo_siguiente(source_file, li):
        """linea_inicio del PRÓXIMO caso en el mismo .md (techo exclusivo)."""
        techo = None
        for li2, _cid in por_archivo[source_file]:
            if li2 > li:
                techo = li2
                break
        return techo if techo is not None else 10**12

    objetivo = [x for x in casos if x.get("pista_fin") == "firma_actual"]

    # cache de lines por archivo
    cache_lines = {}

    def get_lines(source_file):
        if source_file not in cache_lines:
            ruta = args.corpus / source_file
            cache_lines[source_file] = ruta.read_text(encoding="utf-8").split("\n")
        return cache_lines[source_file]

    extendidos = []   # (cid, lfr, nuevo_lfr, dv, agregadas)
    sin_cambio = 0
    sobre_extension = []  # SAFETY flags
    errores = []

    for x in objetivo:
        cid = x["caso_id_canonico"]
        sf = x["source_file"]
        try:
            lfr = int(x["linea_fin_real"])
            li = int(x["linea_inicio"])
        except (ValueError, KeyError):
            errores.append((cid, "lfr/li no numérico"))
            continue
        try:
            lines = get_lines(sf)
        except FileNotFoundError:
            errores.append((cid, f"no se encontró {sf}"))
            continue

        techo = techo_siguiente(sf, li)
        nuevo, agregadas, alcanzo_techo = simular_extension(mod, lines, lfr, techo)

        if alcanzo_techo:
            lo = max(0, min(lfr, techo) - 1)
            hi = min(len(lines), max(lfr, nuevo, techo) + 2)
            ctx = [(i, lines[i]) for i in range(lo, hi)]
            sobre_extension.append((cid, sf, lfr, nuevo, techo, ctx))

        if nuevo == lfr:
            sin_cambio += 1
            continue

        # A/B de votos con parse_firma real
        fr_old = firma_raw.get(cid, "")
        fr_new = (fr_old + " " + " ".join(agregadas)).strip()
        try:
            v_old = len(mod.parse_firma(fr_old)["jueces"])
            v_new = len(mod.parse_firma(fr_new)["jueces"])
        except Exception as e:  # noqa
            errores.append((cid, f"parse_firma: {e}"))
            continue
        extendidos.append((cid, lfr, nuevo, v_old, v_new, v_new - v_old, agregadas))

    # ───────────────────────── REPORTE ─────────────────────────
    print("=" * 72)
    print("PoC B019 — extensión del fallback firma_actual (A/B, sin tocar pipeline)")
    print("=" * 72)
    print(f"Casos pista_fin=firma_actual (blast radius) : {len(objetivo)}")
    print(f"  → EXTIENDE (firma estaba truncada)        : {len(extendidos)}")
    print(f"  → sin cambio (firma ya completa)          : {sin_cambio}")
    print(f"  → errores                                 : {len(errores)}")
    print()
    total_votos = sum(d for *_, d, _ in extendidos)
    print(f"Filas de voto recuperadas (suma de deltas)  : +{total_votos}")
    print()
    print("-" * 72)
    print("SAFETY — sobre-extensión (la firma seguía hasta el caso siguiente):")
    if not sobre_extension:
        print("  [CLEAN] 0 casos alcanzaron el linea_inicio del caso siguiente.")
    else:
        print(f"  [REVISAR] {len(sobre_extension)} casos tocaron el techo (= línea")
        print("  del caso siguiente). 'extendió=SÍ' solo si nuevo>lfr; si dice")
        print("  'inerte', el caso vecino arranca pegado y NO se movió nada.")
        for cid, sf, lfr, nuevo, techo, ctx in sobre_extension:
            ext = "SÍ" if nuevo > lfr else "no (inerte)"
            print(f"    · {cid} {sf} | lfr={lfr} nuevo={nuevo} techo={techo} "
                  f"| extendió={ext}")
            for i, ln in ctx:
                marca = ""
                if i == lfr:
                    marca = "   <- lfr (fin actual)"
                elif nuevo > lfr and i == nuevo:
                    marca = "   <- nuevo fin propuesto"
                elif i == techo:
                    marca = "   <- INICIO caso siguiente"
                print(f"        {i}: {ln[:70]!r}{marca}")
    print("-" * 72)
    print()
    print("Detalle de los que EXTIENDEN (cid | lfr→nuevo | votos old→new (Δ) | +líneas):")
    for cid, lfr, nuevo, vo, vn, dv, agg in sorted(extendidos):
        print(f"  {cid:12} | {lfr}→{nuevo} | {vo}→{vn} (+{dv}) | "
              f"{repr(' '.join(agg))[:60]}")
    if errores:
        print()
        print("Errores:")
        for cid, msg in errores:
            print(f"  {cid:12} {msg}")
    print()
    print("=" * 72)
    print("LECTURA DEL GATE:")
    print("  - SAFETY [CLEAN] + 'sin cambio' = los firma-completa intactos")
    print("    => la extensión es segura: recién entonces se aplica a")
    print("    detectar_fin_real. Si hay sobre-extensión, revisar esos casos")
    print("    ANTES de tocar el parser.")
    print("=" * 72)


if __name__ == "__main__":
    main()
