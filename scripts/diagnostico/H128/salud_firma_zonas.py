#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B124 · PASO 0 — Salud de FIRMA y ZONAS + gate de auto-validacion de la reconstruccion.

NO toca parser.py ni outputs. Solo MIDE. Antes de comprometernos con la variante A
("ultimo candidato CON firma"), este script responde con numeros sobre el corpus real
las dos dudas: cuan confiable es la firma y en que estado estan las zonas.

Reconstruye el bloque de cada caso EXACTAMENTE como procesar_archivo:
  - el .md se lee igual que el parser:  read_text(encoding="utf-8").split("\\n")   (parser.py L3223-3224)
  - bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin_real)
    donde linea_inicio del CSV YA es post-refinamiento (procesar_archivo L3295) y
    linea_fin_real esta persistido (construir_caso_* L2724). Equivale a
    lines[linea_inicio : linea_fin_real+1], identico al bloque que ve el parser tras
    bloque = bloque[offset_titulo:]. => no hace falta re-correr detectar_fin_real ni
    refinar_inicio_por_titulo. El GATE lo confirma.

Replica el tramo zonas->votos->dispositivo de procesar_archivo (L3316-3443) reusando
funciones reales del parser (Gate 3: no se reinventa nada), y mide:

  GATE  : por_ello_text reproducido por resolver_dispositivo (rama ACTUAL) ==
          csjn_casos_textos.por_ello_text. Si el match no es ~total, la reconstruccion
          diverge -> hay que arreglarla ANTES de confiar en el resto del reporte.
  FIRMA : cobertura (#firmas/caso; casos con 0 = piso de falsos negativos) y
          ruido (firmas detectadas FUERA de la zona 'firma' = sospecha de FP / disidencia),
          desglosado por zona y por juez, con ejemplos.
  ZONAS : casos sin zona 'dispositivo' / sin zona 'firma'; y el desajuste clave que te
          preocupa: 'voto_separado' presente en zonas PERO inicio_votos_indiv = None
          (la deteccion de votos no coincide con el zonificador -> A barreria sin techo).

Uso:
  python salud_firma_zonas.py
  python salud_firma_zonas.py --casos ... --textos ... --corpus ... --ejemplos 20 --dump fuera.csv
"""
import sys
import csv
import argparse
import pathlib
from collections import Counter

# --- localizacion del script dentro del schema: scripts/diagnostico/B124/este.py ---
HERE     = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"   # scripts/pipeline
REPO     = HERE.parents[3]                # raiz del repo
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402  (importa parser_editorial; disponible en scripts/pipeline)

# csv del parser parte texto largo -> subir el limite de campo (igual que check_regresion)
csv.field_size_limit(10 * 1024 * 1024)

# Mismo set que procesar_archivo L3430 (constraint de zona para votos/disidencias).
ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}


def hacer_cache_lines(corpus_dir):
    """Lee cada .md una sola vez. None si el archivo no existe."""
    cache = {}

    def get(source_file):
        if source_file not in cache:
            p = pathlib.Path(source_file)
            if not p.is_absolute():
                p = corpus_dir / source_file
            cache[source_file] = (
                p.read_text(encoding="utf-8").split("\n") if p.exists() else None
            )
        return cache[source_file]

    return get


def juez_de_linea(linea):
    """Nombre del juez que dispara linea_es_firma_de_juez, reusando JUECES_CONOCIDOS."""
    for pat, nombre in P.JUECES_CONOCIDOS:
        if pat.search(linea):
            return nombre
    return "?"


def reproducir(bloque):
    """
    Replica EXACTO procesar_archivo L3316-3443 (rama ACTUAL del parser).
    Devuelve (zonas, por_ello_idx, por_ello_text, inicio_votos_indiv).
    """
    zonas, _anclas = P.zonificar_bloque(bloque)
    lineas_dictamen = {k for k, z in enumerate(zonas) if z == "dictamen"}
    lineas_excluir = {k for k, z in enumerate(zonas) if z not in ZONAS_FALLO}
    _apertura_tipo, apertura_rel = P.detectar_apertura_en_bloque(bloque)
    _nv, _nd, inicio_votos_indiv, _mv = P.detectar_votos_disidencias(bloque, lineas_excluir)
    por_ello_idx, por_ello_text = P.resolver_dispositivo(
        bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv
    )
    return zonas, por_ello_idx, por_ello_text, inicio_votos_indiv


def _norm(s):
    return " ".join((s or "").split())


def listar(titulo, items, k):
    """Imprime hasta k ejemplos de una lista, con conteo total."""
    print(f"  {titulo}: {len(items)}")
    for x in items[:k]:
        print(f"      - {x}")
    if len(items) > k:
        print(f"      ... (+{len(items) - k} mas)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos",  default=str(REPO / "output" / "parser" / "csjn_casos.csv"))
    ap.add_argument("--textos", default=str(REPO / "output" / "parser" / "csjn_casos_textos.csv"))
    ap.add_argument("--corpus", default=str(REPO / "corpus"))
    ap.add_argument("--ejemplos", type=int, default=12, help="ejemplos a listar por categoria")
    ap.add_argument("--dump", default="", help="CSV opcional con TODO el detalle firmas-fuera-de-zona")
    args = ap.parse_args()

    corpus_dir = pathlib.Path(args.corpus)
    get_lines = hacer_cache_lines(corpus_dir)

    # por_ello_text del sidecar de textos (H113), keyed por caso_id_canonico
    por_ello_csv = {}
    with open(args.textos, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            por_ello_csv[row["caso_id_canonico"]] = row.get("por_ello_text", "")

    with open(args.casos, encoding="utf-8") as f:
        casos = list(csv.DictReader(f))

    n_total = len(casos)

    # --- contadores ---
    no_reconstruible = []   # source faltante / li-lfr invalidos / bloque vacio
    error_proc = []         # excepcion al reproducir el pipeline
    gate_exacto = 0
    gate_norm = 0           # match tras colapsar whitespace (distingue divergencia de ruido cosmetico)
    gate_mismatch = []      # ni exacto ni normalizado
    n_evaluados = 0

    firmas_bucket = Counter()
    casos_0_firmas = []
    fuera_por_zona = Counter()
    fuera_por_juez = Counter()
    fuera_ejemplos = []     # (cid, zona, juez, texto)

    sin_zona_dispositivo = []
    sin_zona_firma = []
    desajuste_voto_sep = [] # voto_separado en zonas pero inicio_votos_indiv None

    for c in casos:
        cid = c.get("caso_id_canonico", "")
        sf = c.get("source_file", "")
        li = c.get("linea_inicio", "")
        lfr = c.get("linea_fin_real", "")

        lines = get_lines(sf) if sf else None
        if lines is None:
            no_reconstruible.append(f"{cid} (source: {sf!r})")
            continue
        try:
            li_i = int(li)
            lfr_i = int(lfr) if str(lfr) != "" else None
        except (ValueError, TypeError):
            no_reconstruible.append(f"{cid} (li/lfr {li!r}/{lfr!r})")
            continue

        bloque = P.construir_bloque_desde_localizacion(lines, li_i, lfr_i)
        if not bloque:
            no_reconstruible.append(f"{cid} (bloque vacio)")
            continue

        try:
            zonas, _idx, por_ello_rep, ivi = reproducir(bloque)
        except Exception as e:  # noqa: BLE001
            error_proc.append(f"{cid}: {e!r}")
            continue

        n_evaluados += 1

        # --- GATE ---
        ref = por_ello_csv.get(cid, "")
        if por_ello_rep == ref:
            gate_exacto += 1
            gate_norm += 1
        elif _norm(por_ello_rep) == _norm(ref):
            gate_norm += 1
        else:
            gate_mismatch.append(cid)

        # --- FIRMA: cobertura ---
        idx_firmas = [k for k in range(len(bloque)) if P.linea_es_firma_de_juez(bloque[k])]
        nf = len(idx_firmas)
        firmas_bucket["5+" if nf >= 5 else str(nf)] += 1
        if nf == 0:
            casos_0_firmas.append(cid)

        # --- FIRMA: ruido (fuera de zona 'firma') ---
        for k in idx_firmas:
            z = zonas[k] if k < len(zonas) else "?"
            if z != "firma":
                fuera_por_zona[z] += 1
                jz = juez_de_linea(bloque[k])
                fuera_por_juez[jz] += 1
                fuera_ejemplos.append((cid, z, jz, _norm(bloque[k])[:140]))

        # --- ZONAS: salud ---
        zset = set(zonas)
        if "dispositivo" not in zset:
            sin_zona_dispositivo.append(cid)
        if "firma" not in zset:
            sin_zona_firma.append(cid)
        if "voto_separado" in zset and ivi is None:
            desajuste_voto_sep.append(cid)

    # ================= REPORTE =================
    K = args.ejemplos
    pct = lambda x, base: f"{100.0 * x / base:.1f}%" if base else "n/a"

    print("=" * 78)
    print(f"B124 PASO 0 — SALUD FIRMA+ZONAS  ·  parser v{P.__version__}")
    print("=" * 78)
    print(f"casos en csjn_casos.csv : {n_total}")
    print(f"reconstruidos+evaluados : {n_evaluados}")
    listar("NO reconstruibles", no_reconstruible, K)
    listar("error al reproducir", error_proc, K)

    print("\n--- GATE de auto-validacion (por_ello reproducido vs CSV) ---")
    print(f"  match EXACTO     : {gate_exacto}/{n_evaluados}  ({pct(gate_exacto, n_evaluados)})")
    print(f"  match NORMALIZADO: {gate_norm}/{n_evaluados}  ({pct(gate_norm, n_evaluados)})  (colapsa whitespace)")
    listar("MISMATCH (reconstruccion diverge)", gate_mismatch, K)
    if gate_norm < n_evaluados:
        print("  >> OJO: si el mismatch no es ~0, la reconstruccion no es fiel todavia;")
        print("     el resto de las metricas son sobre bloques posiblemente desalineados.")

    print("\n--- FIRMA · cobertura (linea_es_firma_de_juez sobre JUECES_CONOCIDOS) ---")
    for b in ["0", "1", "2", "3", "4", "5+"]:
        v = firmas_bucket.get(b, 0)
        print(f"  {b:>2} firmas/caso : {v:>5}  ({pct(v, n_evaluados)})")
    listar("casos con 0 firmas (piso de FALSOS NEGATIVOS de firma)", casos_0_firmas, K)

    print("\n--- FIRMA · ruido: firmas detectadas FUERA de zona 'firma' (sospecha FP/disidencia) ---")
    total_fuera = sum(fuera_por_zona.values())
    print(f"  total firmas fuera de zona 'firma': {total_fuera}")
    print("  por zona donde caen:")
    for z, v in fuera_por_zona.most_common():
        print(f"      {z:<22} {v}")
    print("  top jueces de esas firmas-fuera:")
    for jz, v in fuera_por_juez.most_common(12):
        print(f"      {jz:<28} {v}")
    print(f"  ejemplos (cid · zona · juez · texto), {min(K, len(fuera_ejemplos))} de {len(fuera_ejemplos)}:")
    for cid, z, jz, txt in fuera_ejemplos[:K]:
        print(f"      [{cid}] {z}/{jz}: {txt}")

    print("\n--- ZONAS · salud ---")
    listar("casos SIN zona 'dispositivo'", sin_zona_dispositivo, K)
    listar("casos SIN zona 'firma'", sin_zona_firma, K)
    listar("DESAJUSTE voto_separado(zona) vs inicio_votos_indiv=None (A sin techo)", desajuste_voto_sep, K)

    print("\n" + "=" * 78)
    print("LECTURA: la firma es confiable para A si  match-gate ~total,  pocos casos 0-firmas,")
    print("y firmas-fuera-de-zona acotado/auditable. El desajuste voto_sep mide el riesgo de")
    print("que A caiga en disidencia. Esto NO decide aun; habilita medir A vs B (paso 1).")
    print("=" * 78)

    if args.dump and fuera_ejemplos:
        with open(args.dump, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["caso_id_canonico", "zona", "juez", "texto"])
            w.writerows(fuera_ejemplos)
        print(f"\n[dump] detalle firmas-fuera-de-zona -> {args.dump} ({len(fuera_ejemplos)} filas)")


if __name__ == "__main__":
    main()
