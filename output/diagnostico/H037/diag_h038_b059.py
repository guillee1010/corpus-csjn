#!/usr/bin/env python3
"""
diag_h038_b059.py — Diagnóstico B059 (falso positivo post-apertura)

Para cada caso B059, encuentra TODOS los matches de dispositivo en la
ventana de búsqueda y evalúa tres estrategias:
  - Actual:       primer match (forward, como hoy)
  - Estrategia A: último match (reverse)
  - Estrategia C: primer match con firma en las 40 líneas siguientes

Ubicación en repo: output/diagnostico/H37/diag_h038_b059.py
Correr desde raíz del repo:
  $env:PYTHONIOENCODING = "utf-8"
  python output/diagnostico/H37/diag_h038_b059.py

Output: output/diagnostico/H038/diag_b059_resumen.txt
        output/diagnostico/H038/diag_b059_detalle.csv
"""

import sys
import csv
import re
from pathlib import Path
from collections import Counter

# ── Setup de imports ──────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
# output/diagnostico/H37/ → output/diagnostico/ → output/ → repo root
_REPO_ROOT = _SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from pipeline.parser import (
    RE_APERTURA,
    RE_FECHA_LINEA,
    RE_DICT_HDR,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    detectar_apertura_dispositivo,
    detectar_apertura_en_bloque,
    linea_es_firma_de_juez,
)

# ── Rutas ─────────────────────────────────────────────────────────────────────
CSV_PATH = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = _REPO_ROOT / "corpus"
OUTPUT_DIR = _REPO_ROOT / "output" / "diagnostico" / "H038"

# IDs de H036 como filtro opcional (más preciso que derivar del CSV)
IDS_A1_PATH = _REPO_ROOT / "output" / "diagnostico" / "H036" / "ids_A1_b059.txt"
IDS_A3_PATH = _REPO_ROOT / "output" / "diagnostico" / "H036" / "ids_A3_otro_con_verbo.txt"
IDS_A2_PATH = _REPO_ROOT / "output" / "diagnostico" / "H036" / "ids_A2_disp_real.txt"

# Variantes "débiles" — las que generan más falsos positivos
VARIANTES_DEBILES = {
    "en_consecuencia", "de_conformidad", "por_lo_expuesto",
    "por_todo_lo_exp", "atento_a", "en_merito", "en_su_merito",
    "por_estas_razones", "por_todo_ello",
}

VARIANTES_FUERTES = {
    "por_ello", "por_los_fund", "por_los_fund_simple",
}


def cargar_ids(path):
    """Carga IDs de un archivo de texto (uno por línea)."""
    if not path.exists():
        return None
    ids = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(line)
    return ids


def reconstruir_estructura(bloque):
    """
    Replica la detección mínima del parser para obtener:
    - apertura_rel
    - lineas_dictamen (set)
    - inicio_votos_indiv
    Necesario para delimitar la ventana de búsqueda.
    """
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
    """Replica la cascada de inicio/fin de búsqueda del parser."""
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


def encontrar_todos_los_dispositivos(bloque, inicio, fin, lineas_dictamen):
    """
    Encuentra TODOS los matches de dispositivo en [inicio, fin),
    no solo el primero. Devuelve lista de dicts con info de cada match.
    """
    matches = []
    for k in range(inicio, fin):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
        if es_disp:
            contexto = stripped[:120]

            # Verificar firma en las siguientes 40 líneas
            tiene_firma = False
            distancia_firma = None
            for j in range(k + 1, min(k + 41, len(bloque))):
                if linea_es_firma_de_juez(bloque[j]):
                    tiene_firma = True
                    distancia_firma = j - k
                    break

            matches.append({
                "idx": k,
                "variante": tipo_disp,
                "es_debil": tipo_disp in VARIANTES_DEBILES,
                "contexto": contexto,
                "tiene_firma_40": tiene_firma,
                "distancia_firma": distancia_firma,
            })
    return matches


def evaluar_estrategias(matches):
    """
    Dado todos los matches, determina qué elegiría cada estrategia:
    - actual:    primer match (forward, como hoy)
    - A:         último match (reverse)
    - C:         primer match con firma en 40 líneas
    - C_ref:     variantes fuertes siempre; débiles solo con firma
    """
    vacio = {"actual": None, "estrategia_A": None,
             "estrategia_C": None, "estrategia_C_ref": None}
    if not matches:
        return vacio

    actual = matches[0]
    estrategia_A = matches[-1]

    estrategia_C = None
    for m in matches:
        if m["tiene_firma_40"]:
            estrategia_C = m
            break

    estrategia_C_ref = None
    for m in matches:
        if not m["es_debil"]:
            estrategia_C_ref = m
            break
        if m["tiene_firma_40"]:
            estrategia_C_ref = m
            break

    return {
        "actual": actual,
        "estrategia_A": estrategia_A,
        "estrategia_C": estrategia_C,
        "estrategia_C_ref": estrategia_C_ref,
    }


def main():
    # ── Leer CSV ──────────────────────────────────────────────────────────────
    print("Leyendo CSV...")
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"  Total filas: {len(rows)}")

    # ── Filtrar candidatos ────────────────────────────────────────────────────
    # Usar IDs de H036 (clasificación precisa)
    ids_a1 = cargar_ids(IDS_A1_PATH)
    ids_a2 = cargar_ids(IDS_A2_PATH)
    ids_a3 = cargar_ids(IDS_A3_PATH)

    csv_por_id = {r["caso_id_canonico"]: r for r in rows}

    if ids_a1 is not None:
        # Modo preciso: usar las tres listas de H036
        ids_all = (ids_a1 or set()) | (ids_a2 or set()) | (ids_a3 or set())
        candidatos = [csv_por_id[cid] for cid in ids_all if cid in csv_por_id]
        print(f"  Usando IDs de H036: A1={len(ids_a1 or set())}, "
              f"A2={len(ids_a2 or set())}, A3={len(ids_a3 or set())}")
    else:
        # Fallback: derivar del CSV
        print("  IDs de H036 no encontrados, derivando del CSV...")
        candidatos = [
            r for r in rows
            if r["voting_pattern"] == "sin_firma"
            and r["apertura_tipo"].strip()
            and r["por_ello_text"].strip()
        ]

    print(f"  Candidatos totales: {len(candidatos)}")

    # Clasificar categoría con IDs de H036
    for r in candidatos:
        cid = r["caso_id_canonico"]
        if ids_a1 and cid in ids_a1:
            r["_cat"] = "A1"
        elif ids_a3 and cid in ids_a3:
            r["_cat"] = "A3"
        elif ids_a2 and cid in ids_a2:
            r["_cat"] = "A2"
        elif r["outcome"] != "otro":
            r["_cat"] = "A2"
        else:
            r["_cat"] = "A1_A3"

    for cat in sorted(set(r["_cat"] for r in candidatos)):
        n = sum(1 for r in candidatos if r["_cat"] == cat)
        print(f"    {cat}: {n}")

    # ── Agrupar por source_file ───────────────────────────────────────────────
    por_archivo = {}
    for r in candidatos:
        por_archivo.setdefault(r["source_file"], []).append(r)

    # ── Procesar ──────────────────────────────────────────────────────────────
    resultados = []
    errores = []
    archivos_procesados = 0

    for source_file, casos in sorted(por_archivo.items()):
        archivo_path = CORPUS_DIR / source_file
        if not archivo_path.exists():
            errores.append(f"Archivo no encontrado: {archivo_path}")
            continue

        text = archivo_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        archivos_procesados += 1

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

            apertura_rel, lineas_dict, votos_ini = reconstruir_estructura(bloque)
            inicio, fin = calcular_ventana(
                apertura_rel, lineas_dict, votos_ini, len(bloque)
            )

            all_matches = encontrar_todos_los_dispositivos(
                bloque, inicio, fin, lineas_dict
            )
            estrategias = evaluar_estrategias(all_matches)

            n_matches = len(all_matches)
            actual_idx = estrategias["actual"]["idx"] if estrategias["actual"] else None
            a_idx = estrategias["estrategia_A"]["idx"] if estrategias["estrategia_A"] else None
            c_idx = estrategias["estrategia_C"]["idx"] if estrategias["estrategia_C"] else None
            cref_idx = estrategias["estrategia_C_ref"]["idx"] if estrategias["estrategia_C_ref"] else None

            resultados.append({
                "caso_id": caso_id,
                "cat": caso["_cat"],
                "outcome_actual": caso["outcome"],
                "tomo": caso["tomo"],
                "n_matches": n_matches,
                "apertura_rel": apertura_rel,
                "ventana": f"{inicio}-{fin}",
                "len_bloque": len(bloque),
                "idx_actual": actual_idx,
                "var_actual": estrategias["actual"]["variante"] if estrategias["actual"] else "",
                "firma_actual": estrategias["actual"]["tiene_firma_40"] if estrategias["actual"] else "",
                "ctx_actual": estrategias["actual"]["contexto"] if estrategias["actual"] else "",
                "idx_A": a_idx,
                "var_A": estrategias["estrategia_A"]["variante"] if estrategias["estrategia_A"] else "",
                "firma_A": estrategias["estrategia_A"]["tiene_firma_40"] if estrategias["estrategia_A"] else "",
                "ctx_A": estrategias["estrategia_A"]["contexto"] if estrategias["estrategia_A"] else "",
                "idx_C": c_idx,
                "var_C": estrategias["estrategia_C"]["variante"] if estrategias["estrategia_C"] else "",
                "ctx_C": estrategias["estrategia_C"]["contexto"] if estrategias["estrategia_C"] else "",
                "idx_Cref": cref_idx,
                "var_Cref": estrategias["estrategia_C_ref"]["variante"] if estrategias["estrategia_C_ref"] else "",
                "firma_Cref": estrategias["estrategia_C_ref"]["tiene_firma_40"] if estrategias["estrategia_C_ref"] else "",
                "A_distinto": a_idx != actual_idx,
                "C_distinto": c_idx != actual_idx if c_idx is not None else "sin_match_C",
                "Cref_distinto": cref_idx != actual_idx if cref_idx is not None else "sin_match_Cref",
                "ultimo_tiene_firma": all_matches[-1]["tiene_firma_40"] if all_matches else "",
            })

    # ── Output ────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "diag_b059_detalle.csv"
    if resultados:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        print(f"\nDetalle: {csv_path}")

    resumen_path = OUTPUT_DIR / "diag_b059_resumen.txt"
    with open(resumen_path, "w", encoding="utf-8") as f:
        def w(s=""):
            print(s)
            f.write(s + "\n")

        w("=" * 70)
        w("DIAGNÓSTICO B059 — Evaluación de estrategias")
        w(f"Casos analizados: {len(resultados)}")
        w(f"Archivos .md procesados: {archivos_procesados}")
        w(f"Errores: {len(errores)}")
        w("=" * 70)

        if errores:
            w("\nErrores:")
            for e in errores[:10]:
                w(f"  {e}")

        # ── Distribución de matches ──
        w("\n── Distribución de cantidad de matches por caso ──")
        ctr = Counter(r["n_matches"] for r in resultados)
        for k in sorted(ctr):
            w(f"  {k} matches: {ctr[k]} casos")

        solo_uno = [r for r in resultados if r["n_matches"] == 1]
        multi = [r for r in resultados if r["n_matches"] > 1]
        w(f"\n  1 solo match (3 estrategias coinciden): {len(solo_uno)}")
        w(f"  2+ matches (estrategias pueden diferir): {len(multi)}")

        # ── Variantes del match actual ──
        w("\n── Variante del match actual (primer match) ──")
        var_ctr = Counter(r["var_actual"] for r in resultados)
        for v, n in var_ctr.most_common():
            w(f"  {v}: {n}")

        # ── Firma del match actual ──
        w("\n── ¿Match actual tiene firma en 40 líneas? ──")
        firma_ctr = Counter(str(r["firma_actual"]) for r in resultados)
        for v, n in firma_ctr.most_common():
            w(f"  {v}: {n}")

        # ── Estrategia A ──
        w("\n── Estrategia A (último match) ──")
        a_diff = sum(1 for r in multi if r["A_distinto"])
        w(f"  Donde A ≠ actual: {a_diff}/{len(multi)} multi-match")
        w(f"  Firma del último match:")
        ult = Counter(str(r["ultimo_tiene_firma"]) for r in multi)
        for v, n in ult.most_common():
            w(f"    {v}: {n}")

        # ── Estrategia C ──
        w("\n── Estrategia C (primer match con firma) ──")
        c_dist = [r for r in resultados if r["C_distinto"] is True]
        c_sin = [r for r in resultados if r["C_distinto"] == "sin_match_C"]
        c_igual = [r for r in resultados if r["C_distinto"] is False]
        w(f"  C = actual (ya tenía firma):       {len(c_igual)}")
        w(f"  C ≠ actual (encontró otro mejor):  {len(c_dist)}")
        w(f"  C sin match (ninguno tiene firma): {len(c_sin)}")

        # ── Estrategia C refinada ──
        w("\n── Estrategia C refinada (fuertes siempre, débiles con firma) ──")
        cr_dist = [r for r in resultados if r["Cref_distinto"] is True]
        cr_sin = [r for r in resultados if r["Cref_distinto"] == "sin_match_Cref"]
        cr_igual = [r for r in resultados if r["Cref_distinto"] is False]
        w(f"  Cref = actual:  {len(cr_igual)}")
        w(f"  Cref ≠ actual:  {len(cr_dist)}")
        w(f"  Cref sin match: {len(cr_sin)}")

        # ── Cruce por categoría ──
        w("\n── Cruce categoría × resultado ──")
        for cat in sorted(set(r["cat"] for r in resultados)):
            sub = [r for r in resultados if r["cat"] == cat]
            w(f"\n  {cat} ({len(sub)} casos):")
            w(f"    Match actual sin firma: {sum(1 for r in sub if r['firma_actual'] is False or str(r['firma_actual']) == 'False')}")
            w(f"    A ≠ actual:     {sum(1 for r in sub if r['A_distinto'])}")
            w(f"    A con firma:    {sum(1 for r in sub if str(r['ultimo_tiene_firma']) == 'True')}")
            w(f"    C ≠ actual:     {sum(1 for r in sub if r['C_distinto'] is True)}")
            w(f"    C sin match:    {sum(1 for r in sub if r['C_distinto'] == 'sin_match_C')}")
            w(f"    Cref ≠ actual:  {sum(1 for r in sub if r['Cref_distinto'] is True)}")
            w(f"    Cref sin match: {sum(1 for r in sub if r['Cref_distinto'] == 'sin_match_Cref')}")

        # ── Top 10 multi-match ──
        w("\n── Top 10 casos con más matches (auditoría manual) ──")
        top = sorted(multi, key=lambda r: r["n_matches"], reverse=True)[:10]
        for r in top:
            w(f"  {r['caso_id']}: {r['n_matches']} matches, "
              f"actual={r['var_actual']}(firma={r['firma_actual']}), "
              f"último={r['var_A']}(firma={r['ultimo_tiene_firma']})")

        # ── Casos sin match C ──
        if c_sin:
            w(f"\n── Casos sin match C ({len(c_sin)}): "
              f"ningún dispositivo tiene firma ──")
            cats = Counter(r["cat"] for r in c_sin)
            for c, n in cats.most_common():
                w(f"    {c}: {n}")

    print(f"\nResumen: {resumen_path}")


if __name__ == "__main__":
    main()
