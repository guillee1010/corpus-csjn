"""
poc_pista2_guardas.py — H040 proof-of-concept

Parcha detectar_fin_real para agregar guardas de exclusión en Pista 2:
antes de aceptar un match de linea_es_header_sumario, excluir líneas que
sean firma, calificador de firma, header de página, o marcador de apertura.

Corre el pipeline completo con el parche, compara contra el CSV actual,
y reporta mejoras/regresiones en firma_raw.

Uso:
  cd corpus-csjn
  python scripts/diagnostico/poc_pista2_guardas.py
"""

import csv
import re
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from pipeline.parser import (
    linea_es_header_sumario,
    linea_es_firma_de_juez,
    RE_APERTURA,
    RE_DICT_HDR,
    RE_PAGE_HEADER,
    RE_CALIFICADOR,
    RE_HEADER_VOTO_DISIDENCIA,
    # Funciones del pipeline
    cargar_localizados,
    cargar_proximos_headers,
    proximo_header_despues_de,
    construir_bloque_desde_localizacion,
    primer_token_de_caratula,
    detectar_fin_real as detectar_fin_real_original,
)

LOC_CSV   = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
CASOS_CSV = ROOT / "output" / "parser" / "csjn_casos.csv"
MAPA_CSV  = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS    = ROOT / "corpus"


# ── Pista 2 con guardas ─────────────────────────────────────────────────────

def linea_es_header_sumario_guardado(linea):
    """
    Wrapper de linea_es_header_sumario con guardas de exclusión.
    Rechaza la línea si es firma, calificador, header de página,
    marcador de apertura, o header de voto/disidencia.
    """
    if not linea_es_header_sumario(linea):
        return False

    s = linea.strip()

    # Guardia 1: firma de juez conocido
    if linea_es_firma_de_juez(linea):
        return False

    # Guardia 2: calificador de firma ("en disidencia", "según su voto", etc.)
    if RE_CALIFICADOR.search(s):
        return False

    # Guardia 3: header de página ("FALLOS DE LA CORTE SUPREMA", nro de tomo, etc.)
    if RE_PAGE_HEADER.match(s):
        return False

    # Guardia 4: marcador de apertura (Pista 3 los maneja)
    if RE_APERTURA.match(s):
        return False
    if RE_DICT_HDR.match(s):
        return False
    if s.upper().startswith("DICTAMEN"):
        return False

    # Guardia 5: header de voto/disidencia
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False

    return True


def detectar_fin_real_parcheado(lines, linea_inicio, linea_fin_catalogo,
                                 proximo_header_pagina, primer_token_siguiente):
    """
    Replica detectar_fin_real pero usa linea_es_header_sumario_guardado
    en Pista 2.
    """
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

    # Pista 1: carátula del fallo siguiente (sin cambios)
    if primer_token_siguiente and len(primer_token_siguiente) >= 5:
        pat = re.compile(r"\b" + re.escape(primer_token_siguiente) + r"\b", re.I)
        def es_caratula(linea):
            return bool(pat.search(linea))
        k = buscar_atras(es_caratula, lfc, li + 5)
        if k is not None:
            return (k - 1, "fin_dentro_bloque", "caratula_siguiente")
        k = buscar_adelante(es_caratula, lfc + 1, limite_adelante)
        if k is not None:
            return (k - 1, "fin_extendido_pag_compartida", "caratula_siguiente")

    # Pista 2: header de sumario CON GUARDAS
    mitad_bloque = li + (lfc - li) // 2
    k = buscar_atras(linea_es_header_sumario_guardado, lfc, mitad_bloque)
    if k is not None:
        return (k - 1, "fin_dentro_bloque", "sumario_siguiente")
    k = buscar_adelante(linea_es_header_sumario_guardado, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "sumario_siguiente")

    # Pista 3: marcador de apertura del siguiente (sin cambios)
    def es_marcador_apertura(linea):
        s = linea.strip()
        return (RE_APERTURA.match(s) is not None
                or RE_DICT_HDR.match(s) is not None
                or s.upper().startswith("DICTAMEN"))
    k = buscar_adelante(es_marcador_apertura, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "marcador_apertura_siguiente")

    # Fallback: firma del fallo actual (sin cambios)
    k = buscar_atras(linea_es_firma_de_juez, lfc, li)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")
    k = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")

    return (lfc, "fin_no_detectado", "fallback_catalogo")


# ── Comparación ──────────────────────────────────────────────────────────────

def main():
    print("Cargando datos...")
    filas_loc, _descartadas = cargar_localizados(LOC_CSV)
    headers_por_archivo = cargar_proximos_headers(MAPA_CSV)

    # Cargar CSV actual para comparar firma_raw
    firma_actual = {}
    with open(CASOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            firma_actual[row["caso_id_canonico"]] = row.get("firma_raw", "").strip()

    # Calcular primer_token_por_caso y siguiente_caso (replica main del parser)
    primer_token_por_caso = {
        row["caso_id_canonico"]: primer_token_de_caratula(row.get("nombres_indice", ""))
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

    # Agrupar por archivo
    from pipeline.parser import agrupar_por_archivo
    grupos = agrupar_por_archivo(filas_loc, CORPUS)

    # Comparar detectar_fin_real original vs parcheado
    cambios = []
    total = 0

    for filepath in sorted(grupos.keys(), key=lambda p: p.name):
        if not filepath.exists():
            continue
        with open(filepath, encoding="utf-8") as fh:
            lines = fh.readlines()

        fallos_arch = grupos[filepath]
        tomos_archivo = set(int(r["tomo"]) for r in fallos_arch)
        headers_archivo = []
        for t in tomos_archivo:
            headers_archivo.extend(headers_por_archivo.get((t, filepath.name), []))
        headers_archivo.sort()

        for fallo in fallos_arch:
            caso_id = fallo["caso_id_canonico"]
            li = int(fallo["linea_inicio"])
            lf_str = fallo.get("linea_fin", "")
            lf = int(lf_str) if lf_str not in ("", None) else len(lines) - 1

            siguiente = siguiente_caso.get(caso_id)
            primer_token = primer_token_por_caso.get(siguiente, "") if siguiente else ""
            prox_header = proximo_header_despues_de(headers_archivo, lf)

            # Original
            fin_orig, status_orig, pista_orig = detectar_fin_real_original(
                lines, li, lf, prox_header, primer_token
            )
            # Parcheado
            fin_patch, status_patch, pista_patch = detectar_fin_real_parcheado(
                lines, li, lf, prox_header, primer_token
            )

            total += 1

            if fin_orig != fin_patch:
                # ¿Tenía firma antes?
                firma_antes = firma_actual.get(caso_id, "")
                cambios.append({
                    "caso_id": caso_id,
                    "tomo": fallo["tomo"],
                    "fin_orig": fin_orig,
                    "pista_orig": pista_orig,
                    "fin_patch": fin_patch,
                    "pista_patch": pista_patch,
                    "delta_lineas": fin_patch - fin_orig,
                    "firma_antes": "si" if firma_antes else "no",
                })

    # ── Reporte ──────────────────────────────────────────────────────────────
    print(f"\nTotal casos evaluados: {total}")
    print(f"Casos con cambio en linea_fin_real: {len(cambios)}")

    if not cambios:
        print("Sin cambios. El parche no tiene efecto.")
        return

    # Clasificar cambios
    extensiones = [c for c in cambios if c["delta_lineas"] > 0]
    contracciones = [c for c in cambios if c["delta_lineas"] < 0]
    print(f"  Extensiones (bloque más largo):  {len(extensiones)}")
    print(f"  Contracciones (bloque más corto): {len(contracciones)}")

    # Cambios en pista_fin
    transiciones = Counter()
    for c in cambios:
        transiciones[(c["pista_orig"], c["pista_patch"])] += 1
    print(f"\nTransiciones de pista_fin:")
    for (orig, patch), cnt in transiciones.most_common():
        print(f"  {orig} → {patch}: {cnt}")

    # Firma antes = no → posible mejora (bloque extendido puede recuperar firma)
    sin_firma_cambiados = [c for c in cambios if c["firma_antes"] == "no"]
    con_firma_cambiados = [c for c in cambios if c["firma_antes"] == "si"]
    print(f"\nCasos sin_firma afectados: {len(sin_firma_cambiados)} (candidatos a mejora)")
    print(f"Casos con_firma afectados: {len(con_firma_cambiados)} (vigilar regresiones)")

    # Muestra
    print(f"\nMuestra de cambios (primeros 20):")
    print(f"{'caso_id':<25} {'T':>4} {'fin_o':>6} {'fin_p':>6} {'delta':>6} {'pista_orig':<25} {'pista_patch':<25} {'firma'}")
    print("-" * 130)
    for c in cambios[:20]:
        print(f"{c['caso_id']:<25} {c['tomo']:>4} {c['fin_orig']:>6} {c['fin_patch']:>6} {c['delta_lineas']:>+6} {c['pista_orig']:<25} {c['pista_patch']:<25} {c['firma_antes']}")

    # Guardar detalle
    out_dir = ROOT / "output" / "diagnostico"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "poc_pista2_guardas_cambios.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "caso_id", "tomo", "fin_orig", "pista_orig",
            "fin_patch", "pista_patch", "delta_lineas", "firma_antes"
        ])
        writer.writeheader()
        writer.writerows(cambios)
    print(f"\nDetalle guardado en: {out_path}")


if __name__ == "__main__":
    main()
