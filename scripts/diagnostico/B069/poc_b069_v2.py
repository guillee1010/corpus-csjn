# PoC B069 v2 - simula eliminar buscar_atras de Pista 1
#
# Para cada caso con pista_fin=caratula_siguiente + fin_dentro_bloque:
#   - Carga el .md fuente
#   - Corre detectar_fin_real SIN la busqueda atras de Pista 1
#   - Compara lfr viejo vs nuevo
#   - Verifica firma con el nuevo bloque
#
# Uso: python scripts/auditoria/poc_b069_v2.py
# Salida: output/auditoria/poc_b069_v2.csv + resumen en stdout

import csv
import re
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path("scripts/pipeline")))
from parser import (
    linea_es_firma_de_juez,
    linea_es_header_sumario_guardado,
    primer_token_de_caratula,
    RE_APERTURA,
    RE_DICT_HDR,
)

CORPUS = Path("corpus")


def detectar_fin_real_sin_p1_atras(lines, linea_inicio, linea_fin_catalogo,
                                    proximo_header_pagina, primer_token_siguiente):
    """
    Copia de detectar_fin_real con UNA modificacion:
    Pista 1 buscar_atras ELIMINADA. Solo queda buscar_adelante.
    Todo lo demas identico.
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

    # Pista 1: SOLO adelante (buscar_atras ELIMINADA)
    if primer_token_siguiente and len(primer_token_siguiente) >= 5:
        pat = re.compile(r"\b" + re.escape(primer_token_siguiente) + r"\b", re.I)
        def es_caratula(linea):
            return bool(pat.search(linea))
        # Solo adelante
        k = buscar_adelante(es_caratula, lfc + 1, limite_adelante)
        if k is not None:
            return (k - 1, "fin_extendido_pag_compartida", "caratula_siguiente")

    # Pista 2: header de sumario
    mitad_bloque = li + (lfc - li) // 2
    k = buscar_atras(linea_es_header_sumario_guardado, lfc, mitad_bloque)
    if k is not None:
        return (k - 1, "fin_dentro_bloque", "sumario_siguiente")
    k = buscar_adelante(linea_es_header_sumario_guardado, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "sumario_siguiente")

    # Pista 3: marcador apertura siguiente
    def es_marcador_apertura(linea):
        s = linea.strip()
        return (RE_APERTURA.match(s) is not None
                or RE_DICT_HDR.match(s) is not None
                or s.upper().startswith("DICTAMEN"))
    k = buscar_adelante(es_marcador_apertura, lfc + 1, limite_adelante)
    if k is not None:
        return (k - 1, "fin_extendido_pag_compartida", "marcador_apertura_siguiente")

    # Fallback: firma del fallo actual
    k = buscar_atras(linea_es_firma_de_juez, lfc, li)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")
    k = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")

    return (lfc, "fin_no_detectado", "fallback_catalogo")


def buscar_firma_en_rango(lines, desde, hasta):
    """Busca la primera linea de firma en un rango."""
    for k in range(desde, min(hasta + 1, len(lines))):
        if linea_es_firma_de_juez(lines[k]):
            return k, lines[k].strip()[:120]
    return None, ""


def main():
    with open("output/parser/csjn_casos.csv", encoding="utf-8") as f:
        todos = list(csv.DictReader(f))
    print(f"Casos totales: {len(todos)}")

    # siguiente_caso
    por_tomo = {}
    for r in todos:
        por_tomo.setdefault(r["tomo"], []).append(r)
    for t in por_tomo:
        por_tomo[t].sort(key=lambda r: int(r["linea_inicio"]))
    siguiente = {}
    for t, lst in por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente[c["caso_id_canonico"]] = lst[i + 1]

    # Headers por archivo (necesario para proximo_header_pagina)
    # Simplificacion: usamos None (el parser real usa mapa_paginas.csv)
    # Esto hace que limite_adelante = lfc + 200 en vez del valor real
    # Aceptable para el PoC

    # Target: todos los que usan Pista 1 atras
    target = [
        r for r in todos
        if r["tipo_entrada"] == "fallo"
        and r["pista_fin"] == "caratula_siguiente"
        and r["status_fin"] == "fin_dentro_bloque"
    ]
    print(f"Casos con Pista 1 atras: {len(target)}")

    por_archivo = {}
    for r in target:
        por_archivo.setdefault(r["source_file"], []).append(r)

    cols = [
        "caso_id_canonico", "tomo",
        "firma_vieja", "firma_nueva",
        "lfr_viejo", "lfr_nuevo", "delta_lfr",
        "pista_nueva", "status_nuevo",
        "tenia_firma", "tiene_firma_ahora",
        "cambio",
    ]
    resultados = []

    for archivo, casos in sorted(por_archivo.items()):
        filepath = CORPUS / archivo
        if not filepath.exists():
            print(f"  {archivo}: NO ENCONTRADO")
            continue

        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()

        for r in casos:
            li = int(r["linea_inicio"])
            lf = int(r["linea_fin"])
            lfr_viejo = int(r["linea_fin_real"])
            tenia_firma = bool(r["firma_raw"].strip())

            sig = siguiente.get(r["caso_id_canonico"])
            token = primer_token_de_caratula(
                sig["case_name_indice"]
            ) if sig else ""

            # Correr version modificada
            lfr_nuevo, status_nuevo, pista_nueva = detectar_fin_real_sin_p1_atras(
                lines, li, lf, None, token
            )

            # Buscar firma en el nuevo bloque
            firma_k, firma_texto = buscar_firma_en_rango(lines, li, lfr_nuevo)
            tiene_firma_ahora = firma_k is not None

            # Clasificar cambio
            if not tenia_firma and tiene_firma_ahora:
                cambio = "MEJORA"
            elif tenia_firma and not tiene_firma_ahora:
                cambio = "REGRESION"
            elif tenia_firma and tiene_firma_ahora:
                cambio = "OK_MANTIENE"
            else:
                cambio = "SIN_CAMBIO"

            resultados.append({
                "caso_id_canonico": r["caso_id_canonico"],
                "tomo": r["tomo"],
                "firma_vieja": r["firma_raw"][:80],
                "firma_nueva": firma_texto,
                "lfr_viejo": lfr_viejo,
                "lfr_nuevo": lfr_nuevo,
                "delta_lfr": lfr_nuevo - lfr_viejo,
                "pista_nueva": pista_nueva,
                "status_nuevo": status_nuevo,
                "tenia_firma": "SI" if tenia_firma else "",
                "tiene_firma_ahora": "SI" if tiene_firma_ahora else "",
                "cambio": cambio,
            })

    # Exportar
    out_path = Path("output/auditoria/poc_b069_v2.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in resultados:
            w.writerow(row)

    # Resumen
    cambios = Counter(row["cambio"] for row in resultados)
    pistas = Counter(row["pista_nueva"] for row in resultados)

    print(f"\nResultados: {len(resultados)} -> {out_path}")
    print(f"\n=== CAMBIOS ===")
    for k, v in cambios.most_common():
        print(f"  {k:<20} {v:>4}")
    print(f"\n=== PISTA NUEVA (que pista tomo el control) ===")
    for k, v in pistas.most_common():
        print(f"  {k:<35} {v:>4}")

    n_mejoras = cambios.get("MEJORA", 0)
    n_regresiones = cambios.get("REGRESION", 0)
    print(f"\n=== VEREDICTO ===")
    print(f"  Mejoras:     {n_mejoras}")
    print(f"  Regresiones: {n_regresiones}")
    if n_regresiones == 0:
        print(f"  -> SAFE: 0 regresiones, patchear parser.py")
    else:
        print(f"  -> INVESTIGAR regresiones antes de patchear")


if __name__ == "__main__":
    main()
