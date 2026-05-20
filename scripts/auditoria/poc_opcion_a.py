"""
PoC Opción A — Votos ampliados post-firma (aditivo puro)
=========================================================
Sesión H044 · corpus-csjn

Diseño: NO toca la lógica existente. Replica el parser actual
tal cual, y DESPUÉS agrega un scan con regex ampliado en la zona
post-firma. Compara baseline vs A para medir mejoras y confirmar
cero regresiones.

Cambios respecto a poc_opcion_d.py:
  - Mantiene el techo de votos para dispositivo (no lo remueve)
  - Mantiene la detección narrow de votos en el loop (no la mueve)
  - Solo AGREGA: firma_lines pre-computadas + firma_end + scan ampliado

Uso:
  python poc_opcion_a.py
  python poc_opcion_a.py --random 200 --seed 42

Ubicación canónica: scripts/auditoria/poc_opcion_a.py
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
_candidates = [
    _SCRIPT_DIR.parent,                          # scripts/
    _SCRIPT_DIR.parent.parent / "scripts",       # repo/scripts/
    _SCRIPT_DIR / "scripts",                     # repo_root/
    _SCRIPT_DIR,
]
for _c in _candidates:
    if (_c / "pipeline" / "parser.py").exists():
        sys.path.insert(0, str(_c))
        break

from pipeline.parser import (  # noqa: E402
    RE_APERTURA, RE_FECHA_LINEA, RE_CONSIDERANDO, RE_DICT_HDR,
    RE_VOTO_HDR, RE_DISID_HDR,
    detectar_apertura_dispositivo, detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion, detectar_fin_real,
    cargar_proximos_headers, cargar_localizados,
    proximo_header_despues_de, primer_token_de_caratula,
    linea_es_firma_de_juez, collect_firma_lines, parse_firma,
    detectar_juez_en_voto_header, POR_ELLO_ARGUMENTAL,
    refinar_inicio_por_titulo,
)

# ── Rutas default ─────────────────────────────────────────────────────────────
_REPO_ROOT = None
for _c in [_SCRIPT_DIR.parent.parent, _SCRIPT_DIR.parent, _SCRIPT_DIR]:
    if (_c / "corpus").exists() and (_c / "output").exists():
        _REPO_ROOT = _c
        break
if _REPO_ROOT is None:
    _REPO_ROOT = _SCRIPT_DIR

DEFAULT_CORPUS = _REPO_ROOT / "corpus"
DEFAULT_LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
DEFAULT_MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
DEFAULT_CASOS = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output" / "auditoria" / "poc_opcion_a"

# ── Regex ampliados ───────────────────────────────────────────────────────────

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


def encontrar_firma_end(firma_lines_indices, por_ello_idx, gap_tolerancia=3):
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


def procesar_fallo_opcion_a(bloque, apertura_rel):
    """
    Replica el parser actual + agrega scan ampliado post-firma.
    Puramente aditivo: todo lo que el parser hace, A lo hace igual.
    """
    r = {}

    # ══ FASE 1: Loop idéntico al parser (dictamen + votos narrow) ═══════
    en_dictamen = False
    lineas_dictamen = set()
    firma_lines_indices = []       # ← NUEVO: pre-compute firma lines
    n_votos_svoto = 0
    n_disidencias = 0
    inicio_votos_indiv = None
    marcadores_votos = []

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

        # [A] Pre-compute firma lines (nuevo, no afecta nada)
        if linea_es_firma_de_juez(stripped):
            firma_lines_indices.append(k)

        # Votos narrow (idéntico al parser)
        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            tipo = "voto" if RE_VOTO_HDR.match(stripped) else "disidencia"
            if tipo == "voto":
                n_votos_svoto += 1
            else:
                n_disidencias += 1
            if inicio_votos_indiv is None:
                inicio_votos_indiv = k
            header_completo = stripped
            for offset in range(1, 4):
                juez = detectar_juez_en_voto_header(header_completo)
                if juez:
                    marcadores_votos.append((k, juez, tipo))
                    break
                if k + offset < len(bloque):
                    sig = bloque[k + offset].strip()
                    if not sig:
                        continue
                    if RE_CONSIDERANDO.match(sig):
                        break
                    header_completo += " " + sig
            continue

    # ══ FASE 2: Dispositivo (idéntico al parser, CON techo) ═════════════

    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    elif dictamen_end is not None:
        inicio_busqueda = dictamen_end + 1
    else:
        inicio_busqueda = 0

    if (inicio_votos_indiv is not None
            and (apertura_rel is None
                 or inicio_votos_indiv > (apertura_rel or 0))):
        fin_busqueda = inicio_votos_indiv
    else:
        fin_busqueda = len(bloque)

    # B059: con firma_lines_set (optimización, mismo resultado)
    firma_lines_set = set(firma_lines_indices)

    por_ello_idx = None
    por_ello_text = ""
    _fallback_idx = None
    _fallback_text = ""
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
            if _fallback_idx is None:
                _fallback_idx = k
                _fallback_text = candidate_text
            if any(j in firma_lines_set
                   for j in range(k + 1, min(k + 41, len(bloque)))):
                por_ello_idx = k
                por_ello_text = candidate_text
                break
    if por_ello_idx is None and _fallback_idx is not None:
        por_ello_idx = _fallback_idx
        por_ello_text = _fallback_text

    # Tier 2 (idéntico al parser)
    if por_ello_idx is None:
        _t2_pats = [
            re.compile(r"Por ello[,.]?\s", re.I),
            re.compile(r"Por lo expuesto\b", re.I),
            re.compile(r"Por las razones\b", re.I),
            re.compile(r"Por lo expresado\b", re.I),
            re.compile(r"Por las consideraciones\b", re.I),
            re.compile(r"Que[,]?\s+por\s+ello\b", re.I),
            re.compile(r"O[íi]dos?\s+(el|la|los|las)\b", re.I),
        ]
        for k in range(inicio_busqueda, fin_busqueda):
            if k in lineas_dictamen:
                continue
            stripped = bloque[k].strip()
            if not stripped:
                continue
            _t2_hit = False
            for _t2_pat in _t2_pats:
                _t2_m = _t2_pat.search(stripped)
                if _t2_m and _t2_m.start() > 0:
                    _t2_pre = stripped[:_t2_m.start()].rstrip()
                    if not (_t2_pre.endswith(".") or _t2_pre.endswith(")")
                            or stripped.lstrip().startswith("Que")):
                        continue
                    _t2_rest = stripped[_t2_m.end():].strip()
                    _t2_fw = (_t2_rest.split()[0].lower().rstrip(",;")
                              if _t2_rest.split() else "")
                    if _t2_fw in POR_ELLO_ARGUMENTAL:
                        continue
                    if any(linea_es_firma_de_juez(bloque[j])
                           for j in range(k + 1, min(k + 41, len(bloque)))):
                        chunk = []
                        for m2 in range(k, min(k + 6, len(bloque))):
                            chunk.append(bloque[m2])
                            if bloque[m2].strip().endswith("."):
                                break
                        por_ello_idx = k
                        por_ello_text = " ".join(chunk).strip()
                        _t2_hit = True
                        break
            if _t2_hit:
                break

    # ══ FASE 3: Firma (idéntico al parser) ══════════════════════════════

    firma_raw = ""
    voting_pattern = "sin_firma"
    n_jueces = 0
    if por_ello_idx is not None:
        firma_raw = collect_firma_lines(bloque, por_ello_idx + 1)
        if firma_raw:
            fp = parse_firma(firma_raw)
            voting_pattern = fp["voting_pattern"]
            n_jueces = len(fp["jueces"])

    r["por_ello_idx"] = por_ello_idx
    r["voting_pattern"] = voting_pattern
    r["n_jueces"] = n_jueces
    r["n_votos_baseline"] = n_votos_svoto
    r["n_disid_baseline"] = n_disidencias
    r["inicio_votos_indiv"] = inicio_votos_indiv
    r["n_marcadores_baseline"] = len(marcadores_votos)

    # ══ FASE 4 [NUEVO A]: firma_end + scan ampliado post-firma ══════════

    firma_end = encontrar_firma_end(firma_lines_indices, por_ello_idx)
    r["firma_end"] = firma_end
    r["firma_lines_count"] = len(firma_lines_indices)

    # Scan ampliado solo post-firma
    nuevos_votos = []
    nuevos_disid = []
    if firma_end is not None:
        for k in range(firma_end + 1, len(bloque)):
            stripped = bloque[k].strip()
            if not stripped:
                continue

            m_voto = RE_VOTO_HDR_AMPLIADO.match(stripped)
            m_disid = RE_DISID_HDR_AMPLIADO.match(stripped)
            if not (m_voto or m_disid):
                continue

            # ¿Ya detectado por narrow en el loop?
            ya_narrow = RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped)

            tipo = "voto" if m_voto else "disidencia"

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

            entry = {
                "k": k, "tipo": tipo, "juez": juez,
                "header": stripped[:120],
                "es_nuevo": not ya_narrow,
            }

            if tipo == "voto":
                nuevos_votos.append(entry)
            else:
                nuevos_disid.append(entry)

    solo_ampliado = [v for v in nuevos_votos + nuevos_disid if v["es_nuevo"]]
    r["n_nuevos_ampliado"] = len(solo_ampliado)
    r["nuevos_detalle"] = solo_ampliado

    # Total A = baseline + nuevos que no estaban
    r["n_votos_total_a"] = n_votos_svoto + sum(
        1 for v in solo_ampliado if v["tipo"] == "voto"
    )
    r["n_disid_total_a"] = n_disidencias + sum(
        1 for v in solo_ampliado if v["tipo"] == "disidencia"
    )

    return r


# ── Orquestación ──────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="PoC Opción A — corpus-csjn")
    ap.add_argument("--random", type=int, default=None)
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

    # Precalcular siguiente_caso
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
            linea_fin_real, _, _ = detectar_fin_real(
                lines, linea_inicio, linea_fin, prox_header, pt_sig
            )

            bloque = construir_bloque_desde_localizacion(
                lines, linea_inicio, linea_fin_real
            )
            if not bloque:
                errores += 1
                continue

            offset_titulo, _ = refinar_inicio_por_titulo(bloque, nombres_indice)
            if offset_titulo > 0:
                bloque = bloque[offset_titulo:]

            _, apertura_rel = detectar_apertura_en_bloque(bloque)

            r = procesar_fallo_opcion_a(bloque, apertura_rel)
            r["caso_id_canonico"] = caso_id
            r["tomo"] = tomo

            bl = baseline.get(caso_id, {})
            r["bl_voting_pattern"] = bl.get("voting_pattern", "")
            r["bl_n_votos"] = int(bl.get("n_votos_svoto", 0))
            r["bl_n_disid"] = int(bl.get("n_disidencias", 0))

            resultados.append(r)

        except Exception as e:
            errores += 1
            if errores <= 5:
                print(f"  ERROR {caso_id}: {e}", file=sys.stderr)

    # ── Reporte ───────────────────────────────────────────────────────────────

    n = len(resultados)
    print(f"\nProcesados: {n} | Errores: {errores}")
    print("=" * 70)

    # Verificación de paridad baseline
    diffs_vp = 0
    diffs_votos = 0
    for r in resultados:
        if r["voting_pattern"] != r["bl_voting_pattern"]:
            diffs_vp += 1
        if r["n_votos_baseline"] != r["bl_n_votos"]:
            diffs_votos += 1
    print(f"\n── Paridad con baseline (cero = sin regresiones) ──")
    print(f"  voting_pattern difiere: {diffs_vp}")
    print(f"  n_votos difiere: {diffs_votos}")

    # Firma end
    con_fe = sum(1 for r in resultados if r["firma_end"] is not None)
    print(f"\n── Firma end ──")
    print(f"  Con firma_end: {con_fe} / {n} ({100*con_fe/n:.1f}%)")

    # === RESULTADO CLAVE ===
    con_nuevos = [r for r in resultados if r["n_nuevos_ampliado"] > 0]
    total_nuevos = sum(r["n_nuevos_ampliado"] for r in resultados)
    print(f"\n══ RESULTADO CLAVE: Headers nuevos por ampliado post-firma ══")
    print(f"  Casos con headers nuevos: {len(con_nuevos)}")
    print(f"  Total headers nuevos: {total_nuevos}")

    if con_nuevos:
        # Agrupar por tipo de header
        tipo_ctr = Counter()
        juez_ctr = Counter()
        tomo_ctr = Counter()
        for r in con_nuevos:
            for v in r["nuevos_detalle"]:
                tipo_ctr[v["tipo"]] += 1
                juez_ctr[v["juez"] or "sin_detectar"] += 1
                tomo_ctr[r["tomo"]] += 1

        print(f"\n  Por tipo: {dict(tipo_ctr)}")
        print(f"  Por juez detectado: {dict(juez_ctr)}")
        print(f"  Por tomo: {dict(sorted(tomo_ctr.items()))}")

        print(f"\n  Detalle completo:")
        for r in sorted(con_nuevos, key=lambda x: (x["tomo"], x["caso_id_canonico"])):
            for v in r["nuevos_detalle"]:
                print(f"    {r['caso_id_canonico']}: [{v['tipo']}] "
                      f"\"{v['header']}\" (juez={v['juez'] or '?'})")

    # Impacto total
    bl_total = sum(r["bl_n_votos"] + r["bl_n_disid"] for r in resultados)
    a_total = sum(r["n_votos_total_a"] + r["n_disid_total_a"] for r in resultados)
    print(f"\n── Impacto total ──")
    print(f"  Votos+disid baseline: {bl_total}")
    print(f"  Votos+disid A:        {a_total}")
    print(f"  Diferencia:           {a_total - bl_total:+d}")
    print(f"  (puramente aditivo: A ≥ baseline siempre)")

    # Falsos positivos potenciales: headers ampliados que matchean
    # text que no es header de voto real (citas jurisprudenciales)
    print(f"\n── Inspección de falsos positivos potenciales ──")
    sospechosos = []
    for r in con_nuevos:
        for v in r["nuevos_detalle"]:
            h = v["header"].lower()
            # Señales de cita jurisprudencial (no header real):
            if "fallos:" in h or "–" in h or "—" in h:
                sospechosos.append((r["caso_id_canonico"], v))
            elif h.endswith(")") or h.endswith(")."):
                # Parentético: "voto del juez X)." = cita, no header
                if not h.endswith("parcial)."):
                    sospechosos.append((r["caso_id_canonico"], v))
            elif ", " in h and not h.endswith("."):
                # "voto del juez X, considerando 6°)." = cita inline
                sospechosos.append((r["caso_id_canonico"], v))

    if sospechosos:
        print(f"  Sospechosos de ser citas (no headers reales): {len(sospechosos)}")
        for caso_id, v in sospechosos:
            print(f"    {caso_id}: \"{v['header']}\"")
    else:
        print(f"  Ninguno detectado (todos parecen headers reales)")

    # ── CSV ────────────────────────────────────────────────────────────────
    if args.output:
        out_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = DEFAULT_OUTPUT_DIR / f"poc_opcion_a_{ts}.csv"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "caso_id_canonico", "tomo",
        "voting_pattern", "bl_voting_pattern",
        "n_votos_baseline", "bl_n_votos",
        "n_disid_baseline", "bl_n_disid",
        "n_votos_total_a", "n_disid_total_a",
        "n_nuevos_ampliado", "firma_end", "firma_lines_count",
        "por_ello_idx", "inicio_votos_indiv",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)
    print(f"\n[OK] CSV: {out_path}")


if __name__ == "__main__":
    main()
