"""
diag_b095_ventana.py — Diagnóstico B095 residual: línea de match por token

Para cada caso ancla_catalogo con token≥4, busca el token en TODO el bloque
(sin límite de ventana) y reporta en qué línea matchea. Esto permite decidir
el umbral mínimo de MAX_LINEAS_BUSQUEDA_TITULO para capturar la mayor
cantidad de casos con el menor riesgo.

Correr desde raíz del repo:
    python scripts/auditoria/H076/diag_b095_ventana.py
"""

import csv
import re
import unicodedata
from pathlib import Path

# ── Copiar helpers del parser ─────────────────────────────────────────────────

def _strip_accents(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

_GENERICOS = {
    'RECURSO', 'CAUSA', 'SENTENCIA', 'FALLO', 'COMPETENCIA',
    'DENUNCIA', 'JUICIO', 'QUEJA', 'PRESENTACION', 'EXPTE',
    'INHIBITORIA', 'INCIDENTE', 'DEMANDA',
}

def primer_token_de_caratula(nombres_indice):
    if not nombres_indice:
        return None
    first = nombres_indice.split("|")[0].strip()
    first = re.sub(r"^\(\d+\)\s*", "", first)
    parts = re.split(r"[\s,./;:()]+", first)
    for p in parts:
        clean = re.sub(r"[^A-Za-zÀ-ÿ]", "", p)
        if len(clean) >= 2 and clean.upper() not in _GENERICOS:
            return clean
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    casos_path = Path("output/parser/csjn_casos.csv")
    corpus_dir = Path("corpus")

    # Cargar casos ancla_catalogo
    with casos_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        casos = [r for r in reader if "ancla_catalogo" in r.get("status_localizacion", "")]

    print(f"Total ancla_catalogo: {len(casos)}\n")

    results = []

    for caso in casos:
        caso_id = caso["caso_id_canonico"]
        nombres_indice = caso.get("case_name_indice", "")
        token = primer_token_de_caratula(nombres_indice)
        linea_inicio = int(caso.get("linea_inicio", 0))
        linea_fin = int(caso.get("linea_fin", 0))
        tomo = caso_id.split("_")[0]

        if not token or len(token) < 4:
            results.append({
                "caso_id": caso_id,
                "token": token or "(none)",
                "len_token": len(token) if token else 0,
                "linea_match": -1,
                "len_bloque": 0,
                "pct_trim": 0,
                "nota": "token<4, skip"
            })
            continue

        # Buscar archivo .md
        md_candidates = list(corpus_dir.glob(f"LibroVol{tomo}*.md"))
        if not md_candidates:
            results.append({
                "caso_id": caso_id, "token": token, "len_token": len(token),
                "linea_match": -1, "len_bloque": 0, "pct_trim": 0,
                "nota": f"md no encontrado para tomo {tomo}"
            })
            continue

        # Leer bloque
        md_path = md_candidates[0]
        try:
            lines = md_path.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            results.append({
                "caso_id": caso_id, "token": token, "len_token": len(token),
                "linea_match": -1, "len_bloque": 0, "pct_trim": 0,
                "nota": f"error leyendo {md_path.name}: {e}"
            })
            continue

        bloque = lines[linea_inicio:linea_fin + 1]
        len_bloque = len(bloque)

        # Buscar token sin límite de ventana
        token_norm = _strip_accents(token)
        pat = re.compile(r'\b' + re.escape(token_norm) + r'\b', re.I)
        pat_prefix = re.compile(r'\b' + re.escape(token_norm), re.I)

        match_line = -1
        match_type = "no_match"

        # Primero word-boundary exacto
        for k, ln in enumerate(bloque):
            if k >= len_bloque - 5:
                break
            if pat.search(_strip_accents(ln)):
                match_line = k
                match_type = "exact"
                break

        # Si no, prefix
        if match_line == -1:
            for k, ln in enumerate(bloque):
                if k >= len_bloque - 5:
                    break
                if pat_prefix.search(_strip_accents(ln)):
                    match_line = k
                    match_type = "prefix"
                    break

        pct_trim = round(100 * match_line / len_bloque, 1) if match_line > 0 else 0
        lines_restantes = len_bloque - match_line if match_line >= 0 else len_bloque

        nota = match_type
        if match_line > 50:
            nota += f" >50 (fuera de ventana actual)"
        if match_line >= 0 and pct_trim > 50:
            nota += " RIESGO:trim>50%"
        if match_line >= 0 and lines_restantes < 20:
            nota += " RIESGO:bloque_corto"

        results.append({
            "caso_id": caso_id,
            "token": token,
            "len_token": len(token),
            "linea_match": match_line,
            "len_bloque": len_bloque,
            "pct_trim": pct_trim,
            "lines_restantes": lines_restantes,
            "nota": nota
        })

    # ── Reporte ───────────────────────────────────────────────────────────────

    # Separar por categoría
    fuera_ventana = [r for r in results if r["linea_match"] > 50]
    dentro_ventana_sin_match = [r for r in results if r["linea_match"] == -1 and r.get("nota") != "token<4, skip"]
    token_corto = [r for r in results if r.get("nota") == "token<4, skip"]

    print(f"{'='*90}")
    print(f"  Token≥4 que matchea FUERA de ventana actual (>50): {len(fuera_ventana)} casos")
    print(f"{'='*90}")
    fuera_ventana.sort(key=lambda x: x["linea_match"])
    print(f"{'caso_id':<20} {'token':<20} {'linea':>6} {'bloque':>7} {'trim%':>6} {'rest':>5}  nota")
    print(f"{'-'*20} {'-'*20} {'-'*6} {'-'*7} {'-'*6} {'-'*5}  {'-'*20}")
    for r in fuera_ventana:
        print(f"{r['caso_id']:<20} {r['token']:<20} {r['linea_match']:>6} {r['len_bloque']:>7} {r['pct_trim']:>5.1f}% {r.get('lines_restantes',''):>5}  {r['nota']}")

    print(f"\n{'='*90}")
    print(f"  Token≥4 SIN match en todo el bloque: {len(dentro_ventana_sin_match)} casos")
    print(f"{'='*90}")
    for r in dentro_ventana_sin_match:
        print(f"  {r['caso_id']:<20} token={r['token']:<20} ({r['nota']})")

    print(f"\n{'='*90}")
    print(f"  Token<4 (no analizados aquí): {len(token_corto)} casos")
    print(f"{'='*90}")

    # Distribución de línea de match para fuera de ventana
    if fuera_ventana:
        lines_match = [r["linea_match"] for r in fuera_ventana]
        print(f"\n── Distribución de línea de match (fuera de ventana) ──")
        for threshold in [55, 60, 65, 70, 75, 80, 90, 100, 120, 150]:
            count = sum(1 for l in lines_match if l <= threshold)
            safe = sum(1 for r in fuera_ventana if r["linea_match"] <= threshold and r["pct_trim"] <= 50)
            print(f"  ventana={threshold:>3}: captura {count:>2}/{len(fuera_ventana)} ({safe} safe con trim≤50%)")


if __name__ == "__main__":
    main()
