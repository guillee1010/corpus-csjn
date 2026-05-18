#!/usr/bin/env python3
"""
pipeline_h038_reversa.py — Pipeline paralelo: búsqueda reversa de dispositivo

Fix B059: en vez de buscar el dispositivo desde apertura_rel hacia adelante
(primer match gana → falso positivo argumental), buscar desde fin_busqueda
hacia atrás (último match = el real, que está justo antes de la firma).

Para cada caso de los 363 sin_firma (A1+A2+A3 de H036):
  1. Reconstruye bloque desde el .md
  2. Busca dispositivo con lógica reversa
  3. Corre collect_firma_lines + parse_firma desde el nuevo dispositivo
  4. Compara contra el CSV productivo

Ubicación: output/diagnostico/H038/pipeline_h038_reversa.py
Correr:
  $env:PYTHONIOENCODING = "utf-8"
  python output/diagnostico/H038/pipeline_h038_reversa.py

Output:
  output/diagnostico/H038/comparar_h038.csv
  output/diagnostico/H038/comparar_h038_resumen.txt
"""

import sys
import csv
import re
from pathlib import Path
from collections import Counter

# ── Setup de imports ──────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
# output/diagnostico/H038/ → output/diagnostico/ → output/ → repo root
_REPO_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from pipeline.parser import (
    RE_APERTURA,
    RE_FECHA_LINEA,
    RE_DICT_HDR,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    RE_CONSIDERANDO,
    RE_280_CONSIDERANDO,
    RE_280_LIBRE,
    RE_ACORDADA_4_CONSIDERANDO,
    detectar_apertura_dispositivo,
    detectar_apertura_en_bloque,
    linea_es_firma_de_juez,
    collect_firma_lines,
    parse_firma,
    classify_outcome,
    extraer_considerando,
)

# ── Rutas ─────────────────────────────────────────────────────────────────────
CSV_PATH = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = _REPO_ROOT / "corpus"
OUTPUT_DIR = _REPO_ROOT / "output" / "diagnostico" / "H038"

IDS_A1_PATH = _REPO_ROOT / "output" / "diagnostico" / "H036" / "ids_A1_b059.txt"
IDS_A2_PATH = _REPO_ROOT / "output" / "diagnostico" / "H036" / "ids_A2_disp_real.txt"
IDS_A3_PATH = _REPO_ROOT / "output" / "diagnostico" / "H036" / "ids_A3_otro_con_verbo.txt"


def cargar_ids(path):
    if not path.exists():
        return set()
    ids = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(line)
    return ids


def reconstruir_estructura(bloque):
    """Replica detección mínima del parser: apertura, dictamen, votos."""
    apertura_tipo, apertura_rel = detectar_apertura_en_bloque(bloque)

    lineas_dictamen = set()
    en_dictamen = False
    inicio_votos_indiv = None

    for k, bl in enumerate(bloque):
        stripped = bl.strip()
        if not stripped:
            continue

        if RE_DICT_HDR.match(stripped):
            en_dictamen = True
            lineas_dictamen.add(k)
            continue
        elif en_dictamen:
            if RE_APERTURA.match(stripped):
                en_dictamen = False
            else:
                lineas_dictamen.add(k)
                if RE_FECHA_LINEA.match(stripped) and k > 5:
                    prev = bloque[k - 1].strip() if k > 0 else ""
                    if prev and len(prev) < 80:
                        en_dictamen = False
                continue

        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            if inicio_votos_indiv is None:
                inicio_votos_indiv = k
            continue

    return apertura_rel, lineas_dictamen, inicio_votos_indiv


def calcular_ventana(apertura_rel, lineas_dictamen, inicio_votos_indiv, n):
    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio = apertura_rel
    elif dictamen_end is not None:
        inicio = dictamen_end + 1
    else:
        inicio = 0

    if (inicio_votos_indiv is not None
            and (apertura_rel is None or inicio_votos_indiv > apertura_rel)):
        fin = inicio_votos_indiv
    else:
        fin = n
    return inicio, fin


def buscar_dispositivo_reversa(bloque, inicio, fin, lineas_dictamen):
    """
    Búsqueda REVERSA: desde fin-1 hacia inicio.
    Encuentra el dispositivo más cercano al final del bloque
    (= el real, antes de la firma).
    """
    for k in range(fin - 1, inicio - 1, -1):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
        if es_disp:
            # Extraer por_ello_text (misma lógica que parser)
            chunk = []
            for m2 in range(k, min(k + 6, len(bloque))):
                chunk.append(bloque[m2])
                if bloque[m2].strip().endswith("."):
                    break
            por_ello_text = " ".join(chunk).strip()
            return k, tipo_disp, por_ello_text
    return None, None, ""


def main():
    print("Leyendo CSV productivo...")
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    csv_por_id = {r["caso_id_canonico"]: r for r in rows}
    print(f"  Total filas: {len(rows)}")

    # Cargar IDs de las 3 categorías
    ids_a1 = cargar_ids(IDS_A1_PATH)
    ids_a2 = cargar_ids(IDS_A2_PATH)
    ids_a3 = cargar_ids(IDS_A3_PATH)
    ids_all = ids_a1 | ids_a2 | ids_a3
    print(f"  IDs: A1={len(ids_a1)}, A2={len(ids_a2)}, A3={len(ids_a3)}, total={len(ids_all)}")

    candidatos = [csv_por_id[cid] for cid in ids_all if cid in csv_por_id]
    for r in candidatos:
        cid = r["caso_id_canonico"]
        if cid in ids_a1:
            r["_cat"] = "A1"
        elif cid in ids_a3:
            r["_cat"] = "A3"
        else:
            r["_cat"] = "A2"

    # Agrupar por source_file
    por_archivo = {}
    for r in candidatos:
        por_archivo.setdefault(r["source_file"], []).append(r)

    # ── Procesar ──────────────────────────────────────────────────────────────
    resultados = []
    errores = []

    for source_file, casos in sorted(por_archivo.items()):
        archivo_path = CORPUS_DIR / source_file
        if not archivo_path.exists():
            errores.append(f"Archivo no encontrado: {archivo_path}")
            continue

        text = archivo_path.read_text(encoding="utf-8")
        lines = text.split("\n")

        for caso in casos:
            caso_id = caso["caso_id_canonico"]
            linea_inicio = int(caso["linea_inicio"])
            linea_fin_raw = caso.get("linea_fin_real", caso.get("linea_fin", ""))
            if linea_fin_raw and str(linea_fin_raw).strip():
                linea_fin = int(linea_fin_raw)
            else:
                linea_fin = len(lines) - 1

            li = max(0, linea_inicio)
            lf = min(len(lines) - 1, linea_fin)
            if li > lf:
                errores.append(f"{caso_id}: linea_inicio({li}) > linea_fin({lf})")
                continue
            bloque = lines[li:lf + 1]
            if not bloque:
                errores.append(f"{caso_id}: bloque vacío")
                continue

            # Reconstruir estructura
            apertura_rel, lineas_dict, votos_ini = reconstruir_estructura(bloque)
            inicio, fin = calcular_ventana(
                apertura_rel, lineas_dict, votos_ini, len(bloque)
            )

            # ── BÚSQUEDA REVERSA ──
            new_idx, new_tipo, new_por_ello_text = buscar_dispositivo_reversa(
                bloque, inicio, fin, lineas_dict
            )

            # Clasificar outcome con el nuevo dispositivo
            if new_por_ello_text:
                new_considerando = extraer_considerando(bloque, new_idx, lineas_dict)
                new_outcome = classify_outcome(new_por_ello_text, new_considerando)
            else:
                new_considerando = ""
                new_outcome = "sin_dispositivo"

            # Fallback outcome por considerando (misma lógica que parser)
            if new_outcome == "sin_dispositivo" and new_considerando:
                if RE_280_CONSIDERANDO.search(new_considerando) or RE_280_LIBRE.search(new_considerando):
                    new_outcome = "inadmisible_280"
                elif RE_ACORDADA_4_CONSIDERANDO.search(new_considerando):
                    new_outcome = "inadmisible_acordada_4"

            # Recolectar firma desde el nuevo dispositivo
            new_firma_raw = ""
            new_firma_parsed = {"jueces": [], "voting_pattern": "sin_firma", "desconocidos": []}
            if new_idx is not None:
                new_firma_raw = collect_firma_lines(bloque, new_idx + 1)
                if new_firma_raw:
                    new_firma_parsed = parse_firma(new_firma_raw)

            # Datos viejos del CSV
            old_outcome = caso["outcome"]
            old_vp = caso["voting_pattern"]
            old_n = int(caso["n_jueces"])
            old_firma = caso["firma_raw"]
            old_pet = caso["por_ello_text"]

            new_vp = new_firma_parsed["voting_pattern"]
            new_n = len(new_firma_parsed["jueces"])
            new_jueces = " | ".join(j["nombre"] for j in new_firma_parsed["jueces"])

            # Clasificar cambio
            if old_vp == "sin_firma" and new_vp != "sin_firma":
                cambio = "mejora_gano_firma"
            elif old_vp == "sin_firma" and new_vp == "sin_firma" and new_outcome != old_outcome:
                cambio = "cambio_outcome"
            elif old_vp == "sin_firma" and new_vp == "sin_firma":
                cambio = "sin_cambio"
            elif old_vp != "sin_firma" and new_vp == "sin_firma":
                cambio = "regresion_perdio_firma"
            elif old_n != new_n:
                cambio = "cambio_n_jueces"
            else:
                cambio = "neutro"

            resultados.append({
                "caso_id": caso_id,
                "cat": caso["_cat"],
                "tomo": caso["tomo"],
                "cambio": cambio,
                "old_outcome": old_outcome,
                "new_outcome": new_outcome,
                "old_vp": old_vp,
                "new_vp": new_vp,
                "old_n_jueces": old_n,
                "new_n_jueces": new_n,
                "old_por_ello": old_pet[:80],
                "new_por_ello": new_por_ello_text[:80],
                "new_variante": new_tipo or "",
                "new_firma_raw": new_firma_raw[:120],
                "new_jueces": new_jueces,
                "new_idx": new_idx,
                "apertura_rel": apertura_rel,
                "ventana": f"{inicio}-{fin}",
            })

    # ── Output ────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "comparar_h038.csv"
    if resultados:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        print(f"\nDetalle: {csv_path}")

    resumen_path = OUTPUT_DIR / "comparar_h038_resumen.txt"
    with open(resumen_path, "w", encoding="utf-8") as f:
        def w(s=""):
            print(s)
            f.write(s + "\n")

        w("=" * 70)
        w("COMPARADOR H038 — Búsqueda reversa de dispositivo")
        w(f"Casos procesados: {len(resultados)}")
        w(f"Errores: {len(errores)}")
        w("=" * 70)

        if errores:
            w("\nErrores:")
            for e in errores[:10]:
                w(f"  {e}")

        # ── Resumen de cambios ──
        w("\n── Resumen de cambios ──")
        cambio_ctr = Counter(r["cambio"] for r in resultados)
        for c, n in cambio_ctr.most_common():
            w(f"  {c}: {n}")

        mejoras = [r for r in resultados if r["cambio"] == "mejora_gano_firma"]
        regresiones = [r for r in resultados if r["cambio"] == "regresion_perdio_firma"]
        sin_cambio = [r for r in resultados if r["cambio"] == "sin_cambio"]

        w(f"\n  MEJORAS (sin_firma → con firma): {len(mejoras)}")
        w(f"  REGRESIONES (tenía firma → perdió): {len(regresiones)}")
        w(f"  SIN CAMBIO: {len(sin_cambio)}")

        # ── Por categoría ──
        w("\n── Cambios por categoría ──")
        for cat in ["A1", "A2", "A3"]:
            sub = [r for r in resultados if r["cat"] == cat]
            w(f"\n  {cat} ({len(sub)} casos):")
            cat_ctr = Counter(r["cambio"] for r in sub)
            for c, n in cat_ctr.most_common():
                w(f"    {c}: {n}")

        # ── Mejoras: distribución de voting_pattern nuevo ──
        if mejoras:
            w(f"\n── Mejoras ({len(mejoras)}): distribución voting_pattern ──")
            vp_ctr = Counter(r["new_vp"] for r in mejoras)
            for v, n in vp_ctr.most_common():
                w(f"  {v}: {n}")

            w(f"\n── Mejoras: distribución n_jueces ──")
            nj_ctr = Counter(r["new_n_jueces"] for r in mejoras)
            for v in sorted(nj_ctr):
                w(f"  n_jueces={v}: {nj_ctr[v]}")

            w(f"\n── Mejoras: distribución outcome ──")
            oc_ctr = Counter(r["new_outcome"] for r in mejoras)
            for v, n in oc_ctr.most_common():
                w(f"  {v}: {n}")

            w(f"\n── Mejoras: variante del dispositivo encontrado ──")
            vr_ctr = Counter(r["new_variante"] for r in mejoras)
            for v, n in vr_ctr.most_common():
                w(f"  {v}: {n}")

        # ── Regresiones: detalle ──
        if regresiones:
            w(f"\n── REGRESIONES ({len(regresiones)}) — detalle ──")
            for r in regresiones:
                w(f"  {r['caso_id']}: {r['old_vp']}→{r['new_vp']}, "
                  f"n_jueces {r['old_n_jueces']}→{r['new_n_jueces']}")

        # ── Sin cambio: ¿por qué no mejoraron? ──
        if sin_cambio:
            w(f"\n── Sin cambio ({len(sin_cambio)}): ¿por qué? ──")
            w("  Estos casos siguen sin firma después de la búsqueda reversa.")
            cats = Counter(r["cat"] for r in sin_cambio)
            for c, n in cats.most_common():
                w(f"    {c}: {n}")
            # ¿Tienen nuevo dispositivo distinto?
            cambio_disp = sum(1 for r in sin_cambio
                              if r["new_por_ello"][:40] != r["old_por_ello"][:40])
            w(f"  Dispositivo cambió pero firma sigue vacía: {cambio_disp}")
            mismo_disp = sum(1 for r in sin_cambio
                             if r["new_por_ello"][:40] == r["old_por_ello"][:40])
            w(f"  Mismo dispositivo (1 solo match): {mismo_disp}")

        # ── Cambio outcome: detalle ──
        cambio_oc = [r for r in resultados if r["cambio"] == "cambio_outcome"]
        if cambio_oc:
            w(f"\n── Cambio outcome sin firma ({len(cambio_oc)}) ──")
            for r in cambio_oc[:15]:
                w(f"  {r['caso_id']}: {r['old_outcome']}→{r['new_outcome']}")

        # ── Top 10 mejoras para auditoría ──
        if mejoras:
            w(f"\n── 10 mejoras para auditoría manual ──")
            for r in mejoras[:10]:
                w(f"  {r['caso_id']} ({r['cat']}): "
                  f"outcome {r['old_outcome']}→{r['new_outcome']}, "
                  f"vp {r['old_vp']}→{r['new_vp']}, "
                  f"n_jueces 0→{r['new_n_jueces']}")
                w(f"    old_disp: {r['old_por_ello']}")
                w(f"    new_disp: {r['new_por_ello']}")
                w(f"    firma: {r['new_firma_raw'][:80]}")

    print(f"\nResumen: {resumen_path}")


if __name__ == "__main__":
    main()
