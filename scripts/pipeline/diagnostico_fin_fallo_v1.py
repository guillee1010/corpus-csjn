#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostico_fin_fallo.py

Para cada fila de csjn_casos_v14.csv calcula la linea donde realmente
termina el contenido decisorio del fallo (la firma del último voto), usando
la lógica de ajuste discutida:

  1. Buscar firma desde el FONDO del bloque del catálogo hacia atrás.
     Si encuentra: status_fin = "fin_detectado_dentro_bloque"

  2. Si no encuentra, buscar HACIA ADELANTE hasta el próximo header de
     página físico (sale del mapa_paginas.csv) — porque la firma puede
     caer en la página compartida con el fallo siguiente.
     Si encuentra: status_fin = "fin_extendido_a_pag_compartida"

  3. Si no encuentra, buscar el primer marcador del fallo siguiente
     (carátula, DICTAMEN, FALLO DE LA CORTE) hacia adelante.
     Si encuentra: status_fin = "fin_inferido_por_marcador_siguiente"

  4. Si nada: status_fin = "fin_no_detectado", linea_fin_real = linea_fin
     del catálogo (fallback).

NO modifica csjn_casos_v14.csv. Genera un CSV diagnóstico nuevo y un log.

Uso (PowerShell):
    python diagnostico_fin_fallo.py <casos_v14_csv> <mapa_paginas_csv> <localizados_csv> <corpus_dir> [<salida_csv>]

Ejemplo:
    python diagnostico_fin_fallo.py paginas\\csjn_casos_v14.csv paginas\\mapa_paginas.csv paginas\\fallos_localizados.csv markdowns_v2 paginas\\diagnostico_fin.csv
"""

import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Reusar JUECES_CONOCIDOS de csjnv14
sys.path.insert(0, str(Path(__file__).parent))
from csjnv14 import JUECES_CONOCIDOS, RE_APERTURA, RE_DICT_HDR


# ---------------------------------------------------------------------------
# Detección de firma de juez en una línea
# ---------------------------------------------------------------------------

RE_HEADER_VOTO_DISIDENCIA = re.compile(
    r"^\s*(disidencia|voto)\b|"
    r"^\s*(don|do[ñn]a|del\s+(se[ñn]or|se[ñn]ora))\b|"
    r"^\s*(se[ñn]or(es)?|se[ñn]ora(s)?)\s+(ministr|president|vicepresidente|juez|jueza)|"
    r"^\s*la\s+se[ñn]ora\s+|"
    r"^\s*el\s+se[ñn]or\s+",
    re.I
)


def linea_es_firma_de_juez(linea):
    """
    Una línea es firma de juez si su contenido (limpio) matchea alguno de los
    patterns de JUECES_CONOCIDOS, descartando líneas que sean headers de votos
    individuales o menciones del juez en cuerpo de texto.

    El editor publica firmas en dos formatos según la época:
      - Tomos 329-330: TODO MAYÚSCULAS, ej: "ENRIQUE SANTIAGO PETRACCHI — ELENA"
      - Tomos 331+:    Mayúsculas+minúsculas, ej: "Ricardo Luis Lorenzetti — Elena"
    Tolerar ambos.

    Para distinguir firma de mención en cuerpo de texto, exigimos al menos UNA
    de estas señales típicas de firma:
      - Contiene "—" (raya larga, separador entre apellidos)
      - Termina con "." y es corta (cierre de firma)
      - Línea muy corta (≤ 80 chars) y contiene un apellido conocido
    """
    s = linea.strip()
    if not s:
        return False
    if len(s) > 200:
        return False
    # Descartar headers de voto/disidencia que mencionan al juez (no son firma)
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False
    # Descartar líneas que arrancan con verbo en cuerpo de texto
    # ("siguiendo el voto del Dr. Lorenzetti...")
    primera_palabra = s.split()[0].lower() if s.split() else ""
    palabras_cuerpo = {
        "siguiendo", "como", "según", "segun", "que", "el", "la", "los", "las",
        "ya", "esta", "este", "ese", "esa", "ello", "por", "pero", "para",
        "tal", "incluso", "asimismo", "tambien", "también", "no", "si",
        "cuando", "mientras", "aunque", "luego", "después", "despues",
        "afirma", "sostiene", "entiende", "considera", "indicó", "indico",
        "destacó", "destaco", "señaló", "señalo", "concluyó", "concluyo",
    }
    if primera_palabra.rstrip(",;:") in palabras_cuerpo:
        return False
    # Buscar al menos un juez conocido
    encontrado = False
    for pat, _nombre in JUECES_CONOCIDOS:
        if pat.search(s):
            encontrado = True
            break
    if not encontrado:
        return False
    # Señales positivas: la línea es claramente una firma
    tiene_raya = "—" in s or " - " in s or "–" in s
    es_corta = len(s) <= 80
    termina_con_punto = s.rstrip().endswith(".")
    # Aceptar si tiene cualquier señal positiva fuerte
    if tiene_raya or es_corta or (termina_con_punto and len(s) <= 120):
        return True
    return False


# ---------------------------------------------------------------------------
# Marcador del siguiente fallo
# ---------------------------------------------------------------------------

RE_SUMARIO_HEADER = re.compile(r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ /\-]{4,}:\s*[A-ZÁÉÍÓÚÑa-záéíóúñ]")


def linea_es_inicio_fallo_siguiente(linea, primer_token_caratula_siguiente):
    """
    True si la línea parece el inicio del fallo siguiente.
    primer_token_caratula_siguiente: primer apellido o nombre principal de la
    carátula del fallo siguiente, para matching exacto.
    """
    s = linea.strip()
    if not s:
        return False
    # Marcadores universales
    if RE_APERTURA.match(s):
        return True
    if RE_DICT_HDR.match(s):
        return True
    if s.upper().startswith("DICTAMEN"):
        return True
    # Sumario nuevo (línea en mayúsculas con doble punto)
    if RE_SUMARIO_HEADER.match(s):
        return True
    # Carátula del siguiente fallo
    if primer_token_caratula_siguiente and len(primer_token_caratula_siguiente) >= 4:
        if primer_token_caratula_siguiente.upper() in s.upper():
            return True
    return False


def primer_token_de_caratula(nombres_indice):
    """Extrae el primer apellido/nombre principal de nombres_indice del catálogo."""
    if not nombres_indice:
        return ""
    # nombres_indice puede tener varias entradas separadas por |
    primera = nombres_indice.split("|")[0].strip()
    # Tomar el primer token "razonable" (>= 4 chars, alfabético)
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", primera)
    for t in tokens:
        if len(t) >= 4 and t.lower() not in (
            "otro", "otros", "sociedad", "sucesion", "sucesión",
            "empresa", "compania", "compañia", "compañía"
        ):
            return t
    return tokens[0] if tokens else ""


# ---------------------------------------------------------------------------
# Detección del fin real
# ---------------------------------------------------------------------------

def detectar_fin_real(lines, linea_inicio, linea_fin_catalogo,
                      proximo_header_pagina, primer_token_siguiente):
    """
    Devuelve (linea_fin_real, status_fin).

    lines: todas las líneas del archivo
    linea_inicio: 0-indexada
    linea_fin_catalogo: 0-indexada (la del catálogo)
    proximo_header_pagina: 0-indexada, línea del próximo header físico
                           (puede ser None si no hay; en ese caso usamos
                            linea_fin_catalogo + 50 como límite blando)
    primer_token_siguiente: para matching de carátula del fallo siguiente
    """
    n = len(lines)
    li = max(0, int(linea_inicio))
    lfc = min(n - 1, int(linea_fin_catalogo))

    # 1. Buscar firma desde el fondo del bloque hacia atrás
    for k in range(lfc, li - 1, -1):
        if linea_es_firma_de_juez(lines[k]):
            return (k, "fin_detectado_dentro_bloque")

    # 2. Buscar firma hacia adelante hasta el próximo header de página físico
    if proximo_header_pagina is not None and proximo_header_pagina > lfc:
        limite_adelante = min(proximo_header_pagina, n - 1)
    else:
        limite_adelante = min(lfc + 50, n - 1)

    for k in range(lfc + 1, limite_adelante + 1):
        if linea_es_firma_de_juez(lines[k]):
            return (k, "fin_extendido_a_pag_compartida")

    # 3. Buscar marcador del fallo siguiente hacia adelante
    for k in range(lfc + 1, limite_adelante + 1):
        if linea_es_inicio_fallo_siguiente(lines[k], primer_token_siguiente):
            return (max(k - 1, lfc), "fin_inferido_por_marcador_siguiente")

    # 4. Fallback: linea_fin del catálogo
    return (lfc, "fin_no_detectado")


# ---------------------------------------------------------------------------
# Carga de mapa de páginas: para cada (tomo, archivo, linea), encontrar la
# próxima línea-header dentro del mismo archivo
# ---------------------------------------------------------------------------

def cargar_proximos_headers(ruta_mapa):
    """
    Devuelve dict {(tomo, archivo): [(linea_header, pagina), ...]} ordenado.
    """
    por_archivo = defaultdict(list)
    with open(ruta_mapa, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            por_archivo[(int(row["tomo"]), row["archivo"])].append(
                (int(row["linea_header"]), int(row["pagina"]))
            )
    for k in por_archivo:
        por_archivo[k].sort()
    return dict(por_archivo)


def proximo_header_despues_de(headers_archivo, linea):
    """En la lista ordenada de (linea, pagina), devuelve la próxima linea > linea, o None."""
    for ln, _pg in headers_archivo:
        if ln > linea:
            return ln
    return None


# ---------------------------------------------------------------------------
# Procesamiento principal
# ---------------------------------------------------------------------------

def procesar(ruta_casos, ruta_mapa, ruta_localizados, dir_corpus, ruta_salida):
    salida_path = Path(ruta_salida)
    log_path = salida_path.with_name(salida_path.stem + "_log.txt")
    log_lines = []

    def emit(s=""):
        print(s)
        log_lines.append(s)

    emit(f"Casos:        {ruta_casos}")
    emit(f"Mapa:         {ruta_mapa}")
    emit(f"Localizados:  {ruta_localizados}")
    emit(f"Corpus:       {dir_corpus}")
    emit()

    # Cargar casos del v14
    with open(ruta_casos, encoding="utf-8") as f:
        casos = list(csv.DictReader(f))
    emit(f"Casos cargados: {len(casos)}")

    # Cargar mapa para encontrar próximos headers
    headers_por_archivo = cargar_proximos_headers(ruta_mapa)
    emit(f"Archivos con headers en mapa: {len(headers_por_archivo)}")

    # Cargar localizados para tener el primer_token de cada fallo siguiente
    with open(ruta_localizados, encoding="utf-8") as f:
        localizados = list(csv.DictReader(f))
    emit(f"Filas en localizados: {len(localizados)}")

    # Mapear caso_id_canonico -> primer_token de su carátula
    primer_token_por_caso = {
        row["caso_id_canonico"]: primer_token_de_caratula(row.get("nombres_indice", ""))
        for row in localizados
    }

    # Para cada caso del v14, necesitamos saber el primer_token del fallo
    # SIGUIENTE en el catálogo (mismo tomo). Para eso ordenamos los casos del
    # catálogo por (tomo, pagina_inicio).
    cat_por_tomo = defaultdict(list)
    for row in localizados:
        if row.get("status") == "pagina_no_en_mapa":
            continue
        cat_por_tomo[int(row["tomo"])].append({
            "caso_id_canonico": row["caso_id_canonico"],
            "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
            "archivo": row["archivo"],
        })
    for t in cat_por_tomo:
        cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
    # Para cada caso, su siguiente del catálogo en el mismo tomo
    siguiente_caso = {}
    for t, lst in cat_por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]

    emit()

    # Cache de archivos abiertos
    archivo_cache = {}

    def get_lines(filepath):
        if filepath not in archivo_cache:
            try:
                with open(filepath, encoding="utf-8") as f:
                    archivo_cache[filepath] = f.read().split("\n")
            except FileNotFoundError:
                archivo_cache[filepath] = None
        return archivo_cache[filepath]

    # Procesar cada caso
    resultados = []
    contador_status = Counter()
    sin_archivo = 0

    corpus_path = Path(dir_corpus)

    for i, caso in enumerate(casos):
        if i % 500 == 0 and i > 0:
            print(f"  ... {i}/{len(casos)} procesados")

        caso_id = caso["caso_id_canonico"]
        archivo_nombre = caso.get("source_file", "")
        if not archivo_nombre:
            sin_archivo += 1
            continue
        filepath = corpus_path / archivo_nombre
        lines = get_lines(filepath)
        if lines is None:
            sin_archivo += 1
            continue

        try:
            li = int(caso["linea_inicio"])
            lf = int(caso["linea_fin"]) if caso.get("linea_fin") else len(lines) - 1
        except (ValueError, KeyError):
            continue

        tomo = int(caso["tomo"])
        siguiente = siguiente_caso.get(caso_id)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""

        headers = headers_por_archivo.get((tomo, archivo_nombre), [])
        prox_header = proximo_header_despues_de(headers, lf)

        linea_fin_real, status_fin = detectar_fin_real(
            lines, li, lf, prox_header, primer_token_siguiente
        )

        contador_status[status_fin] += 1
        delta = linea_fin_real - lf

        resultados.append({
            "caso_id_canonico": caso_id,
            "tomo": tomo,
            "archivo": archivo_nombre,
            "linea_inicio": li,
            "linea_fin_catalogo": lf,
            "linea_fin_real": linea_fin_real,
            "delta_lineas": delta,
            "status_fin": status_fin,
        })

    emit()
    emit("=" * 70)
    emit("Distribución de status_fin")
    emit("=" * 70)
    total = sum(contador_status.values())
    for status in [
        "fin_detectado_dentro_bloque",
        "fin_extendido_a_pag_compartida",
        "fin_inferido_por_marcador_siguiente",
        "fin_no_detectado",
    ]:
        n = contador_status.get(status, 0)
        pct = 100.0 * n / total if total else 0
        emit(f"  {status:<40} {n:>5}  ({pct:.1f}%)")
    if sin_archivo:
        emit(f"  (descartados sin archivo o linea válida: {sin_archivo})")
    emit()

    # Distribución de delta (cuánto se mueve el fin respecto al catálogo)
    deltas = [r["delta_lineas"] for r in resultados]
    if deltas:
        emit("Delta líneas (linea_fin_real - linea_fin_catalogo):")
        emit(f"  delta == 0:                    {sum(1 for d in deltas if d == 0):>5}  (firma cae justo en linea_fin del catálogo)")
        emit(f"  delta < 0 (corta antes):       {sum(1 for d in deltas if d < 0):>5}")
        emit(f"  delta > 0 (extiende):          {sum(1 for d in deltas if d > 0):>5}")
        if any(d > 0 for d in deltas):
            extiende = [d for d in deltas if d > 0]
            emit(f"    máxima extensión:           {max(extiende)} líneas")
            emit(f"    extensión promedio:         {sum(extiende)/len(extiende):.1f} líneas")
        if any(d < 0 for d in deltas):
            corta = [d for d in deltas if d < 0]
            emit(f"    máximo recorte:             {-min(corta)} líneas")
            emit(f"    recorte promedio:           {-sum(corta)/len(corta):.1f} líneas")

    # Distribución por tomo
    emit()
    emit("Status por tomo:")
    por_tomo = defaultdict(Counter)
    for r in resultados:
        por_tomo[r["tomo"]][r["status_fin"]] += 1
    emit(f"  {'tomo':>5}  {'total':>6}  {'dentro':>7}  {'pag_comp':>9}  {'inferido':>9}  {'no_det':>7}")
    for t in sorted(por_tomo):
        c = por_tomo[t]
        tot = sum(c.values())
        emit(f"  {t:>5}  {tot:>6}  "
             f"{c.get('fin_detectado_dentro_bloque', 0):>7}  "
             f"{c.get('fin_extendido_a_pag_compartida', 0):>9}  "
             f"{c.get('fin_inferido_por_marcador_siguiente', 0):>9}  "
             f"{c.get('fin_no_detectado', 0):>7}")

    # Escribir CSV diagnóstico
    with open(salida_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "caso_id_canonico", "tomo", "archivo",
            "linea_inicio", "linea_fin_catalogo", "linea_fin_real",
            "delta_lineas", "status_fin",
        ])
        writer.writeheader()
        writer.writerows(resultados)
    emit()
    emit(f"CSV diagnóstico: {salida_path}  ({len(resultados)} filas)")

    # Escribir log
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
    print(f"Log: {log_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv):
    if len(argv) < 5:
        print(__doc__)
        sys.exit(1)
    ruta_casos = argv[1]
    ruta_mapa = argv[2]
    ruta_localizados = argv[3]
    dir_corpus = argv[4]
    ruta_salida = argv[5] if len(argv) >= 6 else "diagnostico_fin.csv"
    procesar(ruta_casos, ruta_mapa, ruta_localizados, dir_corpus, ruta_salida)


if __name__ == "__main__":
    main(sys.argv)
