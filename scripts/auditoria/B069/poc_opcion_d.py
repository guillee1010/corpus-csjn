"""
PoC Opción D — Validación del reordenamiento de pipeline
=========================================================
Sesión H044/H045 · corpus-csjn

Objetivo: medir el impacto de tres cambios simultáneos:
  (1) Pre-computar firma_lines_indices en el loop
  (2) Usar firma_end como delimitador de zona post-firma
  (3) Buscar votos/disidencias con regex AMPLIADO solo post-firma

Para cada fallo del corpus:
  - Replica la lógica del parser hasta firma
  - Pre-computa firma_lines_indices
  - Detecta firma_end (fin del cluster post-dispositivo)
  - Busca headers ampliados en zona post-firma
  - Aplica validación post-hoc del techo
  - Compara con baseline actual (csjn_casos.csv)

Métricas de salida:
  - Nuevos votos encontrados por ampliado que el parser actual no ve
  - Regresiones (votos que se pierden)
  - Efecto de la validación post-hoc del techo
  - Distribución de firma_end

Uso:
  python poc_opcion_d.py
  python poc_opcion_d.py --random 200 --seed 42
  python poc_opcion_d.py --tomo 344

Ubicación canónica: scripts/auditoria/poc_opcion_d.py
Output:             output/auditoria/poc_opcion_d/poc_opcion_d_<ts>.csv
"""

import argparse
import csv
import random
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# ── Setup de imports ──────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SCRIPT_DIR.parent if _SCRIPT_DIR.name == "auditoria" else _SCRIPT_DIR

# Buscar scripts/pipeline/parser.py desde varias posiciones posibles
_candidates = [
    _SCRIPTS_DIR,                                # scripts/
    _SCRIPTS_DIR.parent / "scripts",             # repo_root/scripts/
    _SCRIPT_DIR / "scripts",                     # si está en repo_root/
    _SCRIPT_DIR,                                 # fallback
]
for _c in _candidates:
    if (_c / "pipeline" / "parser.py").exists():
        sys.path.insert(0, str(_c))
        break

from pipeline.parser import (  # noqa: E402
    RE_APERTURA,
    RE_FECHA_LINEA,
    RE_CONSIDERANDO,
    RE_DICT_HDR,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    RE_PAGE_HEADER,
    detectar_apertura_dispositivo,
    detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion,
    detectar_fin_real,
    cargar_proximos_headers,
    cargar_localizados,
    proximo_header_despues_de,
    primer_token_de_caratula,
    linea_es_firma_de_juez,
    collect_firma_lines,
    parse_firma,
    detectar_juez_en_voto_header,
    JUECES_CONOCIDOS,
    POR_ELLO_ARGUMENTAL,
    refinar_inicio_por_titulo,
)

# ── Rutas default ─────────────────────────────────────────────────────────────
_REPO_ROOT = _SCRIPTS_DIR.parent if (_SCRIPTS_DIR / "pipeline").exists() else _SCRIPT_DIR
if not (_REPO_ROOT / "corpus").exists() and (_SCRIPT_DIR / "corpus").exists():
    _REPO_ROOT = _SCRIPT_DIR

DEFAULT_CORPUS = _REPO_ROOT / "corpus"
DEFAULT_LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
DEFAULT_MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
DEFAULT_CASOS = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output" / "auditoria" / "poc_opcion_d"

# ── Regex ampliados (D) ──────────────────────────────────────────────────────
# Incluyen "juez/jueza", "doctor/a", "conjuez/a" que el parser actual no usa
# porque generan falsos positivos en el considerando.
# En zona post-firma son SEGUROS.

RE_VOTO_HDR_AMPLIADO = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|"
    r"Ministr[ao]s?|[Jj]uez[as]?|[Dd]oct?or[as]?|[Cc]onjuez[as]?)",
    re.I
)
RE_DISID_HDR_AMPLIADO = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|"
    r"Ministr[ao]s?|[Jj]uez[as]?|[Dd]oct?or[as]?|[Cc]onjuez[as]?)",
    re.I
)


# ── Lógica D ─────────────────────────────────────────────────────────────────

def encontrar_firma_end(firma_lines_indices, por_ello_idx, gap_tolerancia=3):
    """
    Dado el set pre-computado de firma_lines y el por_ello_idx,
    encuentra el fin del cluster de firma que sigue al dispositivo.

    gap_tolerancia: máximo de líneas entre dos firma_lines para
    considerarlas parte del mismo cluster (tolera vacías / headers).

    Devuelve firma_end (índice relativo) o None.
    """
    if por_ello_idx is None or not firma_lines_indices:
        return None

    post_disp = [f for f in firma_lines_indices if f > por_ello_idx]
    if not post_disp:
        return None

    cluster_end = post_disp[0]
    for i in range(1, len(post_disp)):
        if post_disp[i] - post_disp[i - 1] <= gap_tolerancia:
            cluster_end = post_disp[i]
        else:
            break
    return cluster_end


def buscar_votos_ampliado_post_firma(bloque, firma_end):
    """
    Busca headers de voto/disidencia con regex AMPLIADO desde
    firma_end+1 hasta fin del bloque.
    """
    hallazgos = []
    if firma_end is None:
        return hallazgos

    for k in range(firma_end + 1, len(bloque)):
        stripped = bloque[k].strip()
        if not stripped:
            continue

        m_voto_amp = RE_VOTO_HDR_AMPLIADO.match(stripped)
        m_disid_amp = RE_DISID_HDR_AMPLIADO.match(stripped)

        if not (m_voto_amp or m_disid_amp):
            continue

        tipo = "voto" if m_voto_amp else "disidencia"

        # ¿También matchea el regex narrow?
        m_narrow = RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped)
        regex_que_matcheo = "narrow" if m_narrow else "ampliado"

        # Detectar juez
        header_completo = stripped
        juez = detectar_juez_en_voto_header(header_completo)
        if not juez:
            for offset in range(1, 4):
                if k + offset >= len(bloque):
                    break
                sig = bloque[k + offset].strip()
                if not sig:
                    continue
                if RE_CONSIDERANDO.match(sig):
                    break
                header_completo += " " + sig
                juez = detectar_juez_en_voto_header(header_completo)
                if juez:
                    break

        hallazgos.append({
            "k": k,
            "header": stripped[:120],
            "tipo": tipo,
            "juez": juez,
            "regex": regex_que_matcheo,
        })

    return hallazgos


# ── Pipeline D para un fallo ─────────────────────────────────────────────────

def procesar_fallo_opcion_d(bloque, linea_inicio, apertura_rel, nombres_indice):
    """
    Ejecuta la pipeline D completa para un fallo.
    Devuelve dict con resultados D + baseline para comparación.
    """
    resultado = {}

    # ── Fase 1: Loop COLLECT ──────────────────────────────────────────────

    en_dictamen = False
    dictamen_presente = False
    lineas_dictamen = set()
    firma_lines_indices = []
    first_voto_narrow = None

    # Baseline: replicar detección actual de votos
    votos_narrow_actual = []
    n_votos_actual = 0
    n_disid_actual = 0
    inicio_votos_indiv_actual = None

    for k, bl in enumerate(bloque):
        stripped = bl.strip()
        if not stripped:
            continue

        # Dictamen (idéntico a parser)
        if RE_DICT_HDR.match(stripped):
            en_dictamen = True
            dictamen_presente = True
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

        # [D] Collect firma lines
        if linea_es_firma_de_juez(stripped):
            firma_lines_indices.append(k)

        # [D] Record first voto narrow (para validación post-hoc)
        if first_voto_narrow is None:
            if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
                first_voto_narrow = k

        # [baseline] Detección actual de votos
        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            tipo = "voto" if RE_VOTO_HDR.match(stripped) else "disidencia"
            if tipo == "voto":
                n_votos_actual += 1
            else:
                n_disid_actual += 1
            if inicio_votos_indiv_actual is None:
                inicio_votos_indiv_actual = k
            header_completo = stripped
            juez = None
            for offset in range(0, 4):
                if offset > 0:
                    if k + offset >= len(bloque):
                        break
                    sig = bloque[k + offset].strip()
                    if not sig:
                        continue
                    if RE_CONSIDERANDO.match(sig):
                        break
                    header_completo += " " + sig
                juez = detectar_juez_en_voto_header(header_completo)
                if juez:
                    break
            votos_narrow_actual.append({
                "k": k, "tipo": tipo, "juez": juez,
                "header": stripped[:120],
            })

    resultado["dictamen_presente"] = dictamen_presente
    resultado["firma_lines_count"] = len(firma_lines_indices)
    resultado["first_voto_narrow"] = first_voto_narrow
    resultado["n_votos_actual"] = n_votos_actual
    resultado["n_disid_actual"] = n_disid_actual

    # ── Fase 2: Dispositivo ───────────────────────────────────────────────

    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    elif dictamen_end is not None:
        inicio_busqueda = dictamen_end + 1
    else:
        inicio_busqueda = 0

    # Baseline: con techo
    if (inicio_votos_indiv_actual is not None
            and (apertura_rel is None
                 or inicio_votos_indiv_actual > (apertura_rel or 0))):
        fin_busqueda_baseline = inicio_votos_indiv_actual
    else:
        fin_busqueda_baseline = len(bloque)

    firma_lines_set = set(firma_lines_indices)

    def buscar_dispositivo(fin_busqueda):
        por_ello_idx = None
        por_ello_text = ""
        fallback_idx = None
        fallback_text = ""
        for k in range(inicio_busqueda, fin_busqueda):
            if k in lineas_dictamen:
                continue
            stripped = bloque[k].strip()
            if not stripped:
                continue
            es_disp, _ = detectar_apertura_dispositivo(stripped)
            if es_disp:
                chunk = []
                for m2 in range(k, min(k + 6, len(bloque))):
                    chunk.append(bloque[m2])
                    if bloque[m2].strip().endswith("."):
                        break
                candidate_text = " ".join(chunk).strip()
                if fallback_idx is None:
                    fallback_idx = k
                    fallback_text = candidate_text
                # B059: lookup en firma_lines_set
                if any(j in firma_lines_set
                       for j in range(k + 1, min(k + 41, len(bloque)))):
                    return (k, candidate_text)
        if fallback_idx is not None:
            return (fallback_idx, fallback_text)
        return (None, "")

    pe_idx_baseline, _ = buscar_dispositivo(fin_busqueda_baseline)
    pe_idx_d, _ = buscar_dispositivo(len(bloque))  # sin techo

    resultado["pe_idx_baseline"] = pe_idx_baseline

    # ── Fase 3: Validación post-hoc ───────────────────────────────────────

    posthoc_rejected = False
    pe_idx_d_validado = pe_idx_d
    if pe_idx_d is not None and first_voto_narrow is not None:
        if pe_idx_d >= first_voto_narrow:
            pe_idx_d_validado = None
            posthoc_rejected = True

    resultado["pe_idx_d_validado"] = pe_idx_d_validado
    resultado["posthoc_rejected"] = posthoc_rejected
    resultado["disp_cambio"] = (pe_idx_baseline != pe_idx_d_validado)
    resultado["disp_cambio_detalle"] = (
        f"baseline={pe_idx_baseline} D={pe_idx_d_validado}"
        if pe_idx_baseline != pe_idx_d_validado else ""
    )

    # ── Fase 4: Firma end ─────────────────────────────────────────────────

    por_ello_idx = (pe_idx_d_validado if pe_idx_d_validado is not None
                    else pe_idx_baseline)
    firma_end = encontrar_firma_end(firma_lines_indices, por_ello_idx)

    resultado["firma_end"] = firma_end
    resultado["por_ello_idx_usado"] = por_ello_idx

    firma_raw = ""
    firma_parsed = {"jueces": [], "voting_pattern": "sin_firma"}
    if por_ello_idx is not None:
        firma_raw = collect_firma_lines(bloque, por_ello_idx + 1)
        if firma_raw:
            firma_parsed = parse_firma(firma_raw)

    resultado["voting_pattern"] = firma_parsed["voting_pattern"]
    resultado["n_jueces_firma"] = len(firma_parsed["jueces"])

    # ── Fase 5: Votos ampliado post-firma ─────────────────────────────────

    votos_ampliado = buscar_votos_ampliado_post_firma(bloque, firma_end)
    resultado["votos_ampliado"] = votos_ampliado
    resultado["n_votos_ampliado"] = len(votos_ampliado)

    nuevos_por_ampliado = [v for v in votos_ampliado if v["regex"] == "ampliado"]
    ya_detectados = [v for v in votos_ampliado if v["regex"] == "narrow"]
    resultado["n_nuevos_por_ampliado"] = len(nuevos_por_ampliado)
    resultado["n_ya_detectados_post_firma"] = len(ya_detectados)

    # Votos narrow que estaban ANTES de firma_end
    if firma_end is not None:
        votos_pre_firma = [v for v in votos_narrow_actual if v["k"] <= firma_end]
    else:
        votos_pre_firma = []
    resultado["n_votos_narrow_pre_firma"] = len(votos_pre_firma)
    resultado["votos_narrow_pre_firma_detalle"] = "; ".join(
        f"k={v['k']}:{v['header'][:60]}" for v in votos_pre_firma
    )

    return resultado


# ── Orquestación ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="PoC Opción D — corpus-csjn")
    ap.add_argument("--random", type=int, default=None,
                    help="Procesar N casos al azar (default: todos)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tomo", type=int, default=None)
    ap.add_argument("--corpus", type=str, default=str(DEFAULT_CORPUS))
    ap.add_argument("--localizados", type=str, default=str(DEFAULT_LOCALIZADOS))
    ap.add_argument("--mapa", type=str, default=str(DEFAULT_MAPA))
    ap.add_argument("--casos", type=str, default=str(DEFAULT_CASOS))
    ap.add_argument("--output", type=str, default=None)
    args = ap.parse_args()

    for label, p in [("corpus", args.corpus), ("localizados", args.localizados),
                     ("mapa", args.mapa)]:
        if not Path(p).exists():
            print(f"ERROR: no encontré '{label}' en `{p}`.", file=sys.stderr)
            sys.exit(2)

    print("Cargando datos...")
    filas_loc, _ = cargar_localizados(args.localizados)
    headers_por_archivo = cargar_proximos_headers(args.mapa)

    baseline = {}
    if Path(args.casos).exists():
        with open(args.casos, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                baseline[row["caso_id_canonico"]] = row

    candidatos = filas_loc
    if args.tomo is not None:
        candidatos = [r for r in candidatos if int(r["tomo"]) == args.tomo]
    candidatos = [
        r for r in candidatos
        if baseline.get(r["caso_id_canonico"], {}).get("tipo_entrada", "fallo") == "fallo"
    ]

    if args.random is not None:
        rng = random.Random(args.seed)
        candidatos = rng.sample(candidatos, min(args.random, len(candidatos)))

    print(f"Procesando {len(candidatos)} fallos...")

    # Precalcular siguiente_caso + primer_token
    cat_por_tomo = {}
    for row in filas_loc:
        cat_por_tomo.setdefault(int(row["tomo"]), []).append({
            "caso_id_canonico": row["caso_id_canonico"],
            "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
            "nombres_indice": row.get("nombres_indice", ""),
        })
    for t in cat_por_tomo:
        cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
    siguiente_caso = {}
    primer_token_por_caso = {}
    for t, lst in cat_por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]
        for c in lst:
            primer_token_por_caso[c["caso_id_canonico"]] = primer_token_de_caratula(
                c["nombres_indice"]
            )

    # Procesar
    resultados = []
    errores = 0
    corpus_dir = Path(args.corpus)

    for fallo_meta in candidatos:
        caso_id = fallo_meta["caso_id_canonico"]
        tomo = int(fallo_meta["tomo"])
        linea_inicio = int(fallo_meta["linea_inicio"])
        linea_fin_raw = fallo_meta.get("linea_fin", "")
        nombres_indice = fallo_meta.get("nombres_indice", "")
        archivo = fallo_meta["archivo"]

        filepath = corpus_dir / archivo
        if not filepath.exists():
            errores += 1
            continue

        try:
            text = filepath.read_text(encoding="utf-8")
            lines = text.split("\n")
            linea_fin = int(linea_fin_raw) if linea_fin_raw.strip() else len(lines) - 1

            sig = siguiente_caso.get(caso_id)
            pt_sig = primer_token_por_caso.get(sig, "") if sig else ""
            headers_archivo = sorted(
                headers_por_archivo.get((tomo, archivo), [])
            )
            prox_header = proximo_header_despues_de(headers_archivo, linea_fin)

            linea_fin_real, status_fin, pista_fin = detectar_fin_real(
                lines, linea_inicio, linea_fin, prox_header, pt_sig
            )

            bloque = construir_bloque_desde_localizacion(
                lines, linea_inicio, linea_fin_real
            )
            if not bloque:
                errores += 1
                continue

            offset_titulo, ancla_inicio = refinar_inicio_por_titulo(
                bloque, nombres_indice
            )
            if offset_titulo > 0:
                linea_inicio += offset_titulo
                bloque = bloque[offset_titulo:]

            apertura_tipo, apertura_rel = detectar_apertura_en_bloque(bloque)

            r = procesar_fallo_opcion_d(
                bloque, linea_inicio, apertura_rel, nombres_indice
            )
            r["caso_id_canonico"] = caso_id
            r["tomo"] = tomo
            r["n_lineas_bloque"] = len(bloque)
            r["apertura_rel"] = apertura_rel

            bl = baseline.get(caso_id, {})
            r["baseline_voting_pattern"] = bl.get("voting_pattern", "")
            r["baseline_n_votos_svoto"] = int(bl.get("n_votos_svoto", 0))
            r["baseline_n_disidencias"] = int(bl.get("n_disidencias", 0))

            resultados.append(r)

        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"  ERROR {caso_id}: {e}", file=sys.stderr)

    # ── Reporte ───────────────────────────────────────────────────────────────

    n = len(resultados)
    print(f"\nProcesados: {n} | Errores: {errores}")
    print("=" * 70)

    con_firma_lines = sum(1 for r in resultados if r["firma_lines_count"] > 0)
    con_firma_end = sum(1 for r in resultados if r["firma_end"] is not None)
    print(f"\n── Firma lines pre-computadas ──")
    print(f"  Con firma_lines: {con_firma_lines} / {n} ({100*con_firma_lines/n:.1f}%)")
    print(f"  Con firma_end:   {con_firma_end} / {n} ({100*con_firma_end/n:.1f}%)")

    if con_firma_end:
        distancias = [
            r["firma_end"] - r["por_ello_idx_usado"]
            for r in resultados
            if r["firma_end"] is not None and r["por_ello_idx_usado"] is not None
        ]
        if distancias:
            ds = sorted(distancias)
            print(f"  Dist firma_end-dispositivo: "
                  f"p50={ds[len(ds)//2]} p90={ds[int(len(ds)*0.9)]} "
                  f"max={ds[-1]} mean={sum(ds)/len(ds):.1f}")

    posthoc_n = sum(1 for r in resultados if r["posthoc_rejected"])
    disp_cambios = [r for r in resultados if r["disp_cambio"]]
    print(f"\n── Validación post-hoc ──")
    print(f"  Post-hoc rechazó dispositivo: {posthoc_n}")
    print(f"  Dispositivo cambió vs baseline: {len(disp_cambios)}")
    for r in disp_cambios[:10]:
        print(f"    {r['caso_id_canonico']}: {r['disp_cambio_detalle']}")
    if len(disp_cambios) > 10:
        print(f"    ... y {len(disp_cambios) - 10} más")

    # === RESULTADO CLAVE ===
    con_nuevos = [r for r in resultados if r["n_nuevos_por_ampliado"] > 0]
    total_nuevos = sum(r["n_nuevos_por_ampliado"] for r in resultados)
    print(f"\n══ RESULTADO CLAVE: Votos ampliados post-firma ══")
    print(f"  Casos con headers NUEVOS (solo ampliado): {len(con_nuevos)}")
    print(f"  Total headers nuevos: {total_nuevos}")
    if con_nuevos:
        print()
        for r in sorted(con_nuevos, key=lambda x: x["tomo"]):
            for v in r["votos_ampliado"]:
                if v["regex"] == "ampliado":
                    print(f"  {r['caso_id_canonico']}: [{v['tipo']}] "
                          f"\"{v['header']}\" (juez={v['juez'] or '?'})")

    con_pre_firma = [r for r in resultados if r["n_votos_narrow_pre_firma"] > 0]
    print(f"\n── Votos narrow PRE-firma (diagnóstico falsos positivos) ──")
    print(f"  Casos con votos narrow antes de firma_end: {len(con_pre_firma)}")
    for r in con_pre_firma[:10]:
        det = r.get("votos_narrow_pre_firma_detalle", "")
        if det:
            print(f"    {r['caso_id_canonico']}: {det[:100]}")

    # Regex breakdown
    regex_ctr = Counter()
    for r in resultados:
        for v in r["votos_ampliado"]:
            regex_ctr[v["regex"]] += 1
    print(f"\n── Headers post-firma por regex ──")
    for k, v in regex_ctr.most_common():
        print(f"  {k}: {v}")

    total_d = sum(
        r["n_ya_detectados_post_firma"] + r["n_nuevos_por_ampliado"]
        for r in resultados
    )
    total_bl = sum(
        r["baseline_n_votos_svoto"] + r["baseline_n_disidencias"]
        for r in resultados
    )
    print(f"\n── Impacto total ──")
    print(f"  Votos+disid baseline: {total_bl}")
    print(f"  Votos+disid post-firma D: {total_d}")
    print(f"  Diferencia: {total_d - total_bl:+d}")

    # ── CSV ────────────────────────────────────────────────────────────────

    if args.output:
        out_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DEFAULT_OUTPUT_DIR / f"poc_opcion_d_{ts}.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "caso_id_canonico", "tomo", "n_lineas_bloque",
        "apertura_rel", "firma_lines_count", "firma_end",
        "pe_idx_baseline", "pe_idx_d_validado", "disp_cambio",
        "posthoc_rejected",
        "voting_pattern", "n_jueces_firma",
        "baseline_voting_pattern", "baseline_n_votos_svoto",
        "baseline_n_disidencias",
        "n_votos_actual", "n_disid_actual",
        "n_votos_ampliado", "n_nuevos_por_ampliado",
        "n_ya_detectados_post_firma", "n_votos_narrow_pre_firma",
        "first_voto_narrow",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)

    print(f"\n[OK] CSV: {out_path}")


if __name__ == "__main__":
    main()
