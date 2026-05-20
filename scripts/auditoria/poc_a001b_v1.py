"""
PoC A001b: Fix zona_fallo envenenada por caso siguiente
========================================================
Bug: _encontrar_zona_fallo toma la ÚLTIMA apertura del bloque.
Cuando el bloque arrastra residuo del caso siguiente (con su propio
"FALLO DE LA CORTE SUPREMA"), zona_fallo queda al final del bloque
y la búsqueda inversa de firma no alcanza la firma real.

Fix: tomar la PRIMERA apertura en vez de la última. Los dictámenes
no usan "FALLO/SENTENCIA DE LA CORTE SUPREMA" (usan "Dictamen del
Procurador..."), así que la primera apertura es siempre la del fallo
actual. Para fecha/considerando/vistos: primera en la primera mitad
del bloque como guarda contra envenenamiento.

Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    python scripts/auditoria/poc_a001b_v1.py

Lee: output/parser/csjn_casos.csv (post-A001), corpus/*.md
"""

import sys
import re
import csv
from pathlib import Path
from collections import Counter

# ── Setup paths ──────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "pipeline"))

from parser import (
    linea_es_firma_de_juez,
    collect_firma_lines,
    parse_firma,
    RE_PAGE_HEADER,
    RE_APERTURA,
    RE_CONSIDERANDO,
    RE_FECHA_LINEA,
    JUECES_CONOCIDOS,
    # A001 ya en parser.py:
    RE_DATOS_PARTES,
    _SPAN_MINIMO_FIRMA_INVERSA,
    buscar_firma_inversa as buscar_firma_inversa_original,
)

CASOS_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# ── Fix: _encontrar_zona_fallo v2 (PRIMERA en vez de ÚLTIMA) ────────

def _encontrar_zona_fallo_v2(bloque):
    """
    v2: toma la PRIMERA ocurrencia en vez de la última.

    Apertura: PRIMERA siempre (dictámenes no usan RE_APERTURA).
    Fecha/Considerando/Vistos: PRIMERA en la primera mitad del bloque
    como guarda contra envenenamiento por caso siguiente.
    """
    n = len(bloque)
    mitad = n // 2

    # 1. Primera apertura (señal más fuerte, no ambigua)
    for k in range(n):
        s = bloque[k].strip()
        if RE_APERTURA.match(s):
            return k

    # 2. Primera fecha en primera mitad
    for k in range(mitad):
        s = bloque[k].strip()
        if RE_FECHA_LINEA.match(s):
            return k

    # 3. Primer considerando en primera mitad
    for k in range(mitad):
        s = bloque[k].strip()
        if RE_CONSIDERANDO.match(s):
            return k

    # 4. Primer vistos en primera mitad
    for k in range(mitad):
        s = bloque[k].strip()
        if s.lower().startswith("vistos los autos"):
            return k

    # 5. Fallback: sin restricción de mitad (para bloques cortos)
    for k in range(n):
        s = bloque[k].strip()
        if RE_FECHA_LINEA.match(s):
            return k
    for k in range(n):
        s = bloque[k].strip()
        if RE_CONSIDERANDO.match(s):
            return k
    for k in range(n):
        s = bloque[k].strip()
        if s.lower().startswith("vistos los autos"):
            return k

    return None


def buscar_firma_inversa_v2(bloque, max_retroceso=80):
    """
    Igual que buscar_firma_inversa pero con _encontrar_zona_fallo_v2.
    """
    n = len(bloque)
    if n < _SPAN_MINIMO_FIRMA_INVERSA:
        return None, "", "span_corto"

    zona_fallo = _encontrar_zona_fallo_v2(bloque)
    if zona_fallo is None:
        return None, "", "sin_zona_fallo"

    limite = max(zona_fallo, n - max_retroceso)

    firma_encontrada = None
    for k in range(n - 1, limite - 1, -1):
        s = bloque[k].strip()
        if not s:
            continue
        if RE_PAGE_HEADER.match(s):
            continue
        if RE_DATOS_PARTES.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_encontrada = k
            break

    if firma_encontrada is None:
        return None, "", "sin_firma_post_fallo"

    firma_inicio = firma_encontrada
    for k in range(firma_encontrada - 1, max(limite, firma_encontrada - 5) - 1, -1):
        s = bloque[k].strip()
        if not s:
            break
        if RE_PAGE_HEADER.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_inicio = k
        else:
            if any(p.search(s) for p, _ in JUECES_CONOCIDOS) and len(s) < 80:
                firma_inicio = k
            else:
                break

    firma_raw = collect_firma_lines(bloque, firma_inicio)
    return firma_inicio, firma_raw, "ok"


# ── Main ─────────────────────────────────────────────────────────────

def main():
    # Cargar casos sin_firma (post-A001)
    casos_sin_firma = []
    total_fallos = 0
    with open(CASOS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["tipo_entrada"] == "fallo":
                total_fallos += 1
                if row["voting_pattern"] == "sin_firma":
                    casos_sin_firma.append(row)

    print(f"Total fallos en CSV:      {total_fallos}")
    print(f"Casos sin_firma (post-A001): {len(casos_sin_firma)}")
    print(f"{'='*70}")

    file_cache = {}

    # Correr AMBAS versiones para comparar
    resultados_v1 = {}  # original
    resultados_v2 = {}  # fix

    for caso in casos_sin_firma:
        caso_id = caso["caso_id_canonico"]
        source_file = caso["source_file"]
        linea_inicio = int(caso["linea_inicio"])
        linea_fin_real = int(caso["linea_fin_real"])

        filepath = CORPUS_DIR / source_file
        if not filepath.exists():
            continue

        if source_file not in file_cache:
            with open(filepath, "r", encoding="utf-8") as f:
                file_cache[source_file] = f.readlines()

        lines = file_cache[source_file]
        start = max(0, linea_inicio - 1)
        end = min(len(lines), linea_fin_real)
        bloque = lines[start:end]

        if not bloque:
            continue

        # v1 (original, ya en parser.py)
        _, raw_v1, motivo_v1 = buscar_firma_inversa_original(bloque)
        parsed_v1 = parse_firma(raw_v1) if raw_v1 else None
        n_v1 = len(parsed_v1["jueces"]) if parsed_v1 else 0
        resultados_v1[caso_id] = {
            "motivo": motivo_v1,
            "n_jueces": n_v1,
            "raw": raw_v1[:80] if raw_v1 else "",
        }

        # v2 (fix)
        _, raw_v2, motivo_v2 = buscar_firma_inversa_v2(bloque)
        parsed_v2 = parse_firma(raw_v2) if raw_v2 else None
        n_v2 = len(parsed_v2["jueces"]) if parsed_v2 else 0
        vp_v2 = parsed_v2["voting_pattern"] if parsed_v2 else "sin_firma"
        jueces_v2 = ", ".join(j["nombre"] for j in parsed_v2["jueces"]) if parsed_v2 else ""
        resultados_v2[caso_id] = {
            "motivo": motivo_v2,
            "n_jueces": n_v2,
            "vp": vp_v2,
            "jueces": jueces_v2,
            "raw": raw_v2[:80] if raw_v2 else "",
            "tomo": caso["tomo"],
            "outcome": caso["outcome"],
        }

    # ── Análisis comparativo ─────────────────────────────────────────
    nuevos_recuperados = []
    perdidos = []  # regresiones (v1 encontraba, v2 no)

    for caso_id in resultados_v1:
        v1 = resultados_v1[caso_id]
        v2 = resultados_v2[caso_id]

        v1_ok = v1["n_jueces"] > 0
        v2_ok = v2["n_jueces"] > 0

        if not v1_ok and v2_ok:
            nuevos_recuperados.append(caso_id)
        elif v1_ok and not v2_ok:
            perdidos.append(caso_id)

    # Contar motivos v1 vs v2 para los sin_firma_post_fallo
    sfpf_v1 = [cid for cid, r in resultados_v1.items() if r["motivo"] == "sin_firma_post_fallo"]
    sfpf_v2_recuperados = [cid for cid in sfpf_v1 if resultados_v2[cid]["n_jueces"] > 0]

    print(f"\n{'='*70}")
    print(f"COMPARACIÓN v1 (ÚLTIMA) vs v2 (PRIMERA)")
    print(f"{'='*70}")
    print(f"sin_firma_post_fallo en v1:      {len(sfpf_v1)}")
    print(f"  → recuperados con v2:          {len(sfpf_v2_recuperados)}")
    print(f"  → siguen sin firma:            {len(sfpf_v1) - len(sfpf_v2_recuperados)}")
    print(f"")
    print(f"NUEVOS recuperados (v2 pero no v1): {len(nuevos_recuperados)}")
    print(f"REGRESIONES (v1 pero no v2):        {len(perdidos)}")

    if nuevos_recuperados:
        print(f"\n--- Nuevos recuperados ---")
        for cid in sorted(nuevos_recuperados):
            v2 = resultados_v2[cid]
            print(f"  {cid:15s} T{v2['tomo']:>3s} | "
                  f"{v2['outcome']:18s} | "
                  f"{v2['n_jueces']}J {v2['vp']:15s} | "
                  f"{v2['jueces'][:55]}")

    if perdidos:
        print(f"\n--- REGRESIONES (v1 encontraba, v2 no) ---")
        for cid in sorted(perdidos):
            v1 = resultados_v1[cid]
            v2 = resultados_v2[cid]
            print(f"  {cid:15s} | v1: {v1['n_jueces']}J ({v1['motivo']}) | "
                  f"v2: {v2['n_jueces']}J ({v2['motivo']})")
    else:
        print(f"\n  ✓ 0 regresiones")

    # Motivos v2
    print(f"\n--- Motivos v2 (todos los 114) ---")
    motivos_v2 = Counter(r["motivo"] for r in resultados_v2.values())
    for m, n in motivos_v2.most_common():
        print(f"  {m:30s}: {n:3d}")

    # Impacto total
    recuperados_a001 = 34  # ya commiteados
    total_nuevos = len(nuevos_recuperados)
    sf_final = len(casos_sin_firma) - total_nuevos
    print(f"\n{'='*70}")
    print(f"IMPACTO PROYECTADO")
    print(f"{'='*70}")
    print(f"  sin_firma actual (post-A001):  {len(casos_sin_firma)}")
    print(f"  Nuevos recuperados con v2:     {total_nuevos}")
    print(f"  sin_firma proyectado:          {sf_final}")
    print(f"  Cobertura firma proyectada:    {100*(total_fallos - sf_final)/total_fallos:.1f}%")


if __name__ == "__main__":
    main()
