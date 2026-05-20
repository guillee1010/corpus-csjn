#!/usr/bin/env python3
"""
PoC B070 v5 — Validación de NO-texto-corriente en Pista 1 forward.

Fix: cuando Pista 1 forward encuentra un match, verificar que la línea
NO sea texto corriente. Es texto corriente si:
  (a) empieza con minúscula (continuación de oración),
      EXCEPTO si empieza con "c/" o "s/" (conector de carátula), O
  (b) la línea anterior significativa termina con word-split genuino
      (letra + guión), no guión editorial (puntuación + guión).

v5 fixes sobre v4:
  - (a) excepción para "c/" y "s/"
  - (b) guión solo cuenta si precedido por letra, no por ) ] " etc.

Uso:
  python scripts/auditoria/H048/poc_b070_v5.py
"""

import sys
import csv
import time
import re as _re
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "pipeline"))

import parser as P
import pandas as pd

# ── Helper: ¿la línea es continuación de texto corriente? ────────────────

def _es_texto_corriente(lines, k):
    """
    True si lines[k] parece continuación de texto corriente,
    no una carátula/sumario editorial.
    """
    s = lines[k].strip()
    if not s:
        return False

    # (a) Empieza con minúscula → es continuación de oración
    #     EXCEPTO si empieza con "c/" o "s/" (conector de carátula)
    first_alpha = None
    for c in s:
        if c.isalpha():
            first_alpha = c
            break
    if first_alpha and first_alpha.islower():
        s_stripped = s.lstrip()
        if not (s_stripped.startswith("c/") or s_stripped.startswith("s/")):
            return True

    # Buscar línea anterior significativa (no vacía, no page header)
    prev_line = None
    for j in range(k - 1, max(k - 5, -1), -1):
        if j < 0:
            break
        ps = lines[j].strip()
        if not ps:
            continue
        if P.RE_PAGE_HEADER.match(ps):
            continue
        # Skip pure numbers (page numbers) and tomo numbers
        if _re.match(r'^\d{1,4}$', ps):
            continue
        # Skip "FALLOS DE LA CORTE SUPREMA" / "DE JUSTICIA DE LA NACION"
        if ps in ("FALLOS DE LA CORTE SUPREMA", "DE JUSTICIA DE LA NACION",
                   "DE JUSTICIA DE LA NACIÓN"):
            continue
        prev_line = ps
        break

    if prev_line is None:
        return False

    # (b) Línea anterior termina con word-split genuino: letra + guión
    #     No cuenta guión editorial después de puntuación ()-]"
    if prev_line.endswith('-') and len(prev_line) >= 2:
        char_antes = prev_line[-2]
        if char_antes.isalpha():
            return True

    return False


# ── Monkey-patch detectar_fin_real ───────────────────────────────────────

def detectar_fin_real_b070v5(lines, linea_inicio, linea_fin_catalogo,
                              proximo_header_pagina, primer_token_siguiente):
    n = len(lines)
    li = max(0, int(linea_inicio))
    lfc = min(n - 1, int(linea_fin_catalogo))

    if proximo_header_pagina is not None and proximo_header_pagina > lfc:
        limite_adelante = min(proximo_header_pagina + 50, n - 1)
    else:
        limite_adelante = min(lfc + 200, n - 1)

    def buscar_atras(check, desde, hasta):
        for k in range(desde, hasta - 1, -1):
            if check(lines[k]):
                return k
        return None

    def buscar_adelante(check, desde, hasta):
        for k in range(desde, hasta + 1):
            if check(lines[k]):
                return k
        return None

    # ── Pista 1 con validación no-texto-corriente ───────────────────────
    if primer_token_siguiente and len(primer_token_siguiente) >= 5:
        pat = _re.compile(r"\b" + _re.escape(primer_token_siguiente) + r"\b", _re.I)

        desde = lfc + 1
        while desde <= limite_adelante:
            k = buscar_adelante(lambda linea: bool(pat.search(linea)), desde, limite_adelante)
            if k is None:
                break

            if _es_texto_corriente(lines, k):
                desde = k + 1
                continue

            return (k - 1, "fin_extendido_pag_compartida", "caratula_siguiente")

    # ── Pistas 2, 3, fallback: idénticas ────────────────────────────────
    mitad_bloque = li + (lfc - li) // 2
    k = buscar_atras(P.linea_es_header_sumario_guardado, lfc, mitad_bloque)
    if k is not None:
        return (k - 1, "fin_dentro_bloque", "sumario_siguiente")
    k = buscar_adelante(P.linea_es_header_sumario_guardado, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "sumario_siguiente")

    def es_marcador_apertura(linea):
        s = linea.strip()
        return (P.RE_APERTURA.match(s) is not None
                or P.RE_DICT_HDR.match(s) is not None
                or s.upper().startswith("DICTAMEN"))
    k = buscar_adelante(es_marcador_apertura, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "marcador_apertura_siguiente")

    k = buscar_atras(P.linea_es_firma_de_juez, lfc, li)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")
    k = buscar_adelante(P.linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")

    return (lfc, "fin_no_detectado", "fallback_catalogo")


P.detectar_fin_real = detectar_fin_real_b070v5

# ── Cargar baseline ──────────────────────────────────────────────────────
CSV_BASE = REPO / "output" / "parser" / "csjn_casos.csv"
df_base = pd.read_csv(CSV_BASE)
base_map = {}
for _, r in df_base.iterrows():
    base_map[r["caso_id_canonico"]] = {
        "vp_base": r["voting_pattern"],
        "lfr_base": r["linea_fin_real"],
        "n_jueces_base": r.get("n_jueces", 0),
    }

# ── Re-correr parser ────────────────────────────────────────────────────
LOCALIZADOS = REPO / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = REPO / "output" / "mapa" / "mapa_paginas.csv"
CORPUS = REPO / "corpus"

print("Cargando localizados...")
filas_loc, n_sin_loc = P.cargar_localizados(str(LOCALIZADOS))
print(f"  {len(filas_loc)} fallos ({n_sin_loc} descartados)")

headers_por_archivo = P.cargar_proximos_headers(str(MAPA))
primer_token_por_caso = {
    row["caso_id_canonico"]: P.primer_token_de_caratula(row.get("nombres_indice", ""))
    for row in filas_loc
}

cat_por_tomo = {}
for row in filas_loc:
    cat_por_tomo.setdefault(int(row["tomo"]), []).append({
        "caso_id_canonico": row["caso_id_canonico"],
        "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
    })
for t in cat_por_tomo:
    cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
siguiente_caso = {}
for t, lst in cat_por_tomo.items():
    for i, c in enumerate(lst[:-1]):
        siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]

grupos = P.agrupar_por_archivo(filas_loc, str(CORPUS))

print(f"\nRe-corriendo parser con fix B070 v3...")
t0 = time.time()
all_casos = []
all_votos = []

for filepath in sorted(grupos.keys(), key=lambda p: p.name):
    if not filepath.exists() or filepath.stat().st_size < 200:
        continue
    fallos_arch = grupos[filepath]
    tomos_archivo = set(int(r["tomo"]) for r in fallos_arch)
    headers_archivo = []
    for t in tomos_archivo:
        headers_archivo.extend(headers_por_archivo.get((t, filepath.name), []))
    headers_archivo.sort()
    try:
        casos, votos, _ = P.procesar_archivo(
            filepath, fallos_arch, headers_archivo,
            primer_token_por_caso, siguiente_caso
        )
    except Exception as e:
        print(f"  ERROR {filepath.name}: {e}")
        continue
    all_casos.extend(casos)
    all_votos.extend(votos)

t1 = time.time()
print(f"Parser completado en {t1-t0:.1f}s. {len(all_casos)} casos, {len(all_votos)} votos.")

# ── Diff ─────────────────────────────────────────────────────────────────
new_map = {c["caso_id_canonico"]: c for c in all_casos}
mejoras = regresiones = cambios_lfr = 0
diff_rows = []

for cid in sorted(set(list(base_map.keys()) + list(new_map.keys()))):
    b = base_map.get(cid, {})
    n = new_map.get(cid, {})
    vp_b = b.get("vp_base", "???")
    vp_n = n.get("voting_pattern", "???")
    lfr_b = b.get("lfr_base", -1)
    lfr_n = n.get("linea_fin_real", -1)

    if vp_b == vp_n:
        if lfr_b != lfr_n:
            cambios_lfr += 1
            diff_rows.append({"caso_id": cid, "tipo": "lfr_cambio",
                "vp_base": vp_b, "vp_new": vp_n, "lfr_base": lfr_b, "lfr_new": lfr_n,
                "n_jueces_new": n.get("n_jueces", "")})
        continue

    if vp_b == "sin_firma" and vp_n != "sin_firma":
        mejoras += 1; tipo = "MEJORA"
    elif vp_b != "sin_firma" and vp_n == "sin_firma":
        regresiones += 1; tipo = "REGRESION"
    else:
        tipo = "cambio_vp"
    diff_rows.append({"caso_id": cid, "tipo": tipo,
        "vp_base": vp_b, "vp_new": vp_n, "lfr_base": lfr_b, "lfr_new": lfr_n,
        "n_jueces_new": n.get("n_jueces", "")})

sf_base = sum(1 for v in base_map.values() if v["vp_base"] == "sin_firma")
sf_new = sum(1 for c in all_casos if c["voting_pattern"] == "sin_firma")

print(f"\n{'='*60}")
print(f"=== RESULTADO B070 v5 ===")
print(f"{'='*60}")
print(f"Mejoras: {mejoras}")
print(f"Regresiones: {regresiones}")
print(f"Cambios solo lfr: {cambios_lfr}")
print(f"sin_firma: {sf_base} -> {sf_new}")
print(f"Votos: {len(all_votos)}")

out_dir = REPO / "output" / "auditoria" / "H048"
out_dir.mkdir(parents=True, exist_ok=True)
pd.DataFrame(diff_rows).to_csv(out_dir / "poc_b070v5_diff.csv", index=False, encoding="utf-8")

print(f"\n=== MEJORAS ===")
for d in diff_rows:
    if d["tipo"] == "MEJORA":
        print(f"  {d['caso_id']}: {d['vp_base']} -> {d['vp_new']} (lfr {d['lfr_base']}->{d['lfr_new']}, jueces={d['n_jueces_new']})")

print(f"\n=== REGRESIONES ===")
for d in diff_rows:
    if d["tipo"] == "REGRESION":
        print(f"  {d['caso_id']}: {d['vp_base']} -> {d['vp_new']} (lfr {d['lfr_base']}->{d['lfr_new']})")
