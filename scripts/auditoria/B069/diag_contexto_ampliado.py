"""
Diagnóstico: contexto de los 42 headers ampliados del PoC A
=============================================================
Muestra ±5 líneas alrededor de cada match para inspección visual.
Determina si es header de sección o cita inline.

Uso:
  python diag_contexto_ampliado.py

Ubicación: scripts/auditoria/diag_contexto_ampliado.py
"""

import csv
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_candidates = [
    _SCRIPT_DIR.parent,
    _SCRIPT_DIR.parent.parent / "scripts",
    _SCRIPT_DIR / "scripts",
    _SCRIPT_DIR,
]
for _c in _candidates:
    if (_c / "pipeline" / "parser.py").exists():
        sys.path.insert(0, str(_c))
        break

from pipeline.parser import (
    RE_APERTURA, RE_FECHA_LINEA, RE_CONSIDERANDO, RE_DICT_HDR,
    RE_VOTO_HDR, RE_DISID_HDR,
    detectar_apertura_dispositivo, detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion, detectar_fin_real,
    cargar_proximos_headers, cargar_localizados,
    proximo_header_despues_de, primer_token_de_caratula,
    linea_es_firma_de_juez, collect_firma_lines,
    refinar_inicio_por_titulo,
    POR_ELLO_ARGUMENTAL,
)

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

# Los 39 casos con matches del PoC A (hardcoded para velocidad)
CASOS_TARGET = [
    "329_p1092", "329_p1191", "329_p3235", "329_p3680", "329_p4542",
    "329_p4593", "329_p4741", "329_p4944", "329_p5068",
    "330_p3248", "330_p5345",
    "331_p756", "331_p1123", "331_p2006", "331_p2562",
    "332_p1835", "333_p2079",
    "340_p47",
    "341_p1251", "341_p1854",
    "342_p1665", "342_p1921", "342_p2244",
    "343_p1457", "343_p1871", "343_p1894",
    "344_p1151", "344_p2256", "344_p2690", "344_p3104", "344_p3307", "344_p3636",
    "345_p1249", "345_p1531",
    "346_p103", "346_p868", "346_p970",
    "347_p2286",
    "348_p1655",
]

CONTEXTO = 5  # líneas antes y después


def encontrar_firma_end(firma_lines_indices, por_ello_idx, gap=3):
    if por_ello_idx is None or not firma_lines_indices:
        return None
    post = [f for f in firma_lines_indices if f > por_ello_idx]
    if not post:
        return None
    end = post[0]
    for i in range(1, len(post)):
        if post[i] - post[i - 1] <= gap:
            end = post[i]
        else:
            break
    return end


def main():
    filas_loc, _ = cargar_localizados(str(DEFAULT_LOCALIZADOS))
    headers_por_archivo = cargar_proximos_headers(str(DEFAULT_MAPA))
    corpus_dir = DEFAULT_CORPUS

    # Index por caso_id
    loc_idx = {r["caso_id_canonico"]: r for r in filas_loc}

    # siguiente_caso
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
                c["nombres_indice"])

    n_header_real = 0
    n_cita = 0
    n_ambiguo = 0

    for caso_id in CASOS_TARGET:
        fila = loc_idx.get(caso_id)
        if not fila:
            print(f"\n{'='*70}\n{caso_id}: NO ENCONTRADO\n")
            continue

        tomo = int(fila["tomo"])
        archivo = fila["archivo"]
        filepath = corpus_dir / archivo
        if not filepath.exists():
            continue

        text = filepath.read_text(encoding="utf-8")
        lines = text.split("\n")
        linea_inicio = int(fila["linea_inicio"])
        linea_fin_raw = fila.get("linea_fin", "")
        linea_fin = int(linea_fin_raw) if linea_fin_raw.strip() else len(lines) - 1
        nombres_indice = fila.get("nombres_indice", "")

        sig = siguiente_caso.get(caso_id)
        pt_sig = primer_token_por_caso.get(sig, "") if sig else ""
        headers_archivo = sorted(headers_por_archivo.get((tomo, archivo), []))
        prox_header = proximo_header_despues_de(headers_archivo, linea_fin)
        linea_fin_real, _, _ = detectar_fin_real(
            lines, linea_inicio, linea_fin, prox_header, pt_sig)

        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin_real)
        if not bloque:
            continue
        offset_titulo, _ = refinar_inicio_por_titulo(bloque, nombres_indice)
        if offset_titulo > 0:
            linea_inicio += offset_titulo
            bloque = bloque[offset_titulo:]

        _, apertura_rel = detectar_apertura_en_bloque(bloque)

        # Replicar pipeline hasta firma_end
        en_dictamen = False
        lineas_dictamen = set()
        firma_lines = []
        inicio_votos_indiv = None

        for k, bl in enumerate(bloque):
            s = bl.strip()
            if not s:
                continue
            if RE_DICT_HDR.match(s):
                en_dictamen = True
                lineas_dictamen.add(k)
                continue
            elif en_dictamen:
                if RE_APERTURA.match(s):
                    en_dictamen = False
                else:
                    lineas_dictamen.add(k)
                    if RE_FECHA_LINEA.match(s) and k > 5:
                        prev = bloque[k-1].strip() if k > 0 else ""
                        if prev and len(prev) < 80:
                            en_dictamen = False
                    continue
            if linea_es_firma_de_juez(s):
                firma_lines.append(k)
            if inicio_votos_indiv is None:
                if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
                    inicio_votos_indiv = k

        # Dispositivo (con techo)
        dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
        inicio_b = apertura_rel if apertura_rel is not None else (
            dictamen_end + 1 if dictamen_end is not None else 0)
        fin_b = inicio_votos_indiv if (
            inicio_votos_indiv is not None and
            (apertura_rel is None or inicio_votos_indiv > (apertura_rel or 0))
        ) else len(bloque)

        firma_set = set(firma_lines)
        por_ello_idx = None
        fb_idx = None
        for k in range(inicio_b, fin_b):
            if k in lineas_dictamen:
                continue
            s = bloque[k].strip()
            if not s:
                continue
            es_d, _ = detectar_apertura_dispositivo(s)
            if es_d:
                if fb_idx is None:
                    fb_idx = k
                if any(j in firma_set for j in range(k+1, min(k+41, len(bloque)))):
                    por_ello_idx = k
                    break
        if por_ello_idx is None and fb_idx is not None:
            por_ello_idx = fb_idx

        firma_end = encontrar_firma_end(firma_lines, por_ello_idx)

        if firma_end is None:
            continue

        # Buscar matches ampliados post-firma
        for k in range(firma_end + 1, len(bloque)):
            s = bloque[k].strip()
            if not s:
                continue
            m = RE_VOTO_HDR_AMPLIADO.match(s) or RE_DISID_HDR_AMPLIADO.match(s)
            if not m:
                continue
            ya_narrow = RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s)
            if ya_narrow:
                continue  # solo mostrar los NUEVOS

            # Contexto
            k_abs = linea_inicio + k
            ini_ctx = max(0, k - CONTEXTO)
            fin_ctx = min(len(bloque) - 1, k + CONTEXTO)

            # Clasificación automática tentativa
            es_cita = False
            motivo = ""
            if s.endswith(").") or s.endswith(");"):
                es_cita = True
                motivo = "termina en ').' o ');'"
            elif "Fallos:" in s or "–" in s or "—" in s:
                es_cita = True
                motivo = "contiene 'Fallos:' o guión largo"
            elif len(s) > 100:
                es_cita = True
                motivo = f"línea larga ({len(s)} chars)"
            else:
                # Mirar si la línea siguiente empieza un cuerpo de voto
                for j in range(k+1, min(k+4, len(bloque))):
                    ns = bloque[j].strip()
                    if not ns:
                        continue
                    if (RE_CONSIDERANDO.match(ns)
                            or re.match(r"^\d+[°ºª]\s*\)", ns)
                            or ns.startswith("Que ")):
                        motivo = f"siguiente línea = '{ns[:50]}' → HEADER REAL"
                        break
                    else:
                        es_cita = True
                        motivo = f"siguiente línea = '{ns[:50]}' → no parece inicio de voto"
                        break

            if es_cita:
                n_cita += 1
                tag = "CITA"
            elif "HEADER REAL" in motivo:
                n_header_real += 1
                tag = "HEADER REAL"
            else:
                n_ambiguo += 1
                tag = "AMBIGUO"

            print(f"\n{'='*70}")
            print(f"{caso_id} | k_rel={k} k_abs={k_abs} | firma_end={firma_end} "
                  f"por_ello={por_ello_idx}")
            print(f">>> [{tag}] {motivo}")
            print(f"{'-'*70}")
            for j in range(ini_ctx, fin_ctx + 1):
                prefix = ">>>" if j == k else "   "
                ln = bloque[j].rstrip()
                if len(ln) > 120:
                    ln = ln[:117] + "..."
                print(f"  {prefix} {j:>4} | {ln}")

    print(f"\n{'='*70}")
    print(f"RESUMEN: {n_header_real} HEADER REAL | {n_cita} CITA | {n_ambiguo} AMBIGUO")
    print(f"Total: {n_header_real + n_cita + n_ambiguo}")


if __name__ == "__main__":
    main()
