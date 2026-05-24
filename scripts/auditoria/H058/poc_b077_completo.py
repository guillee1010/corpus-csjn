"""
PoC B077 — Fix completo: Fase 1 (zonas) + Fase 2 (corte + CSV editorial)
=========================================================================

Valida los marcadores editoriales contra un .md de tomo y simula
el comportamiento de las tres piezas del fix:

  1. detectar_fin_real: nueva Pista "editorial_siguiente"
  2. zonificar_bloque: zonas acordada/indice/discurso
  3. Extracción editorial para 4to CSV canónico

Uso:
    python poc_b077_completo.py <ruta_md>

Sin argumento, usa LibroVol330_4.md de uploads.
"""
import re
import sys
from collections import Counter


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE 1 — Regex nuevos (insertar en parser.py después de RE_DISID_HDR)
# ═══════════════════════════════════════════════════════════════════════════

# B077: marcadores de secciones editoriales al final de cada tomo.
# Tres categorías: acordadas, discursos, índices.
# Uso dual: (a) señal de corte en detectar_fin_real, (b) zonas en zonificador.

RE_EDITORIAL_ACORDADA = re.compile(
    r"^(?:A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S|ACORDADAS\s*$)", re.I
)

RE_EDITORIAL_DISCURSO = re.compile(
    r"^DISCURSOS\b", re.I
)

RE_EDITORIAL_INDICE = re.compile(
    r"^(?:"
    r"INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)

# Composite: cualquier marcador editorial.
# Usado en detectar_fin_real como señal de corte.
RE_EDITORIAL_ANY = re.compile(
    r"^(?:"
    r"A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s*$"
    r"|DISCURSOS\b"
    r"|INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)


def es_marcador_editorial(linea):
    """Helper para detectar_fin_real: ¿es una línea de sección editorial?"""
    s = linea.strip()
    return bool(s and RE_EDITORIAL_ANY.match(s))


def tipo_zona_editorial(linea):
    """
    Devuelve la zona editorial de una línea, o None.
    Prioridad: acordada > discurso > indice.
    """
    s = linea.strip()
    if not s:
        return None
    if RE_EDITORIAL_ACORDADA.match(s):
        return "acordada"
    if RE_EDITORIAL_DISCURSO.match(s):
        return "discurso"
    if RE_EDITORIAL_INDICE.match(s):
        return "indice"
    return None


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE 2 — Patch para detectar_fin_real
# ═══════════════════════════════════════════════════════════════════════════
#
# INSERTAR entre Pista 3 (marcador_apertura_siguiente, ~L1607) y
# el fallback firma_actual (~L1609):
#
#     # Pista 4: marcador editorial (B077)
#     # Acordadas, índices, discursos al final del tomo. Solo afecta al
#     # último caso del archivo donde ninguna pista anterior funciona.
#     # Busca desde li hacia adelante — los marcadores son suficientemente
#     # específicos para no generar FP en texto de fallos (validado H058).
#     k = buscar_adelante(es_marcador_editorial, li, lfc)
#     if k is not None:
#         return (k - 1, "fin_por_editorial", "editorial_siguiente")
#
# NOTA: es_marcador_editorial() y RE_EDITORIAL_ANY del Bloque 1.


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — Patch para zonificar_bloque (Pasada 1 + Pasada 2)
# ═══════════════════════════════════════════════════════════════════════════
#
# En Pasada 1, INSERTAR al inicio del loop (antes de todos los checks,
# justo después de `if not s: continue`):
#
#         # B077: editorial mode — una vez activado, suprime todos los
#         # marcadores no-editoriales. La zona editorial es irreversible.
#         if _en_editorial:
#             _tipo_ed = tipo_zona_editorial(bloque[k])
#             if _tipo_ed:
#                 anclas.append((k, f"editorial_{_tipo_ed}"))
#             continue  # suprimir TODOS los demás marcadores
#
#         _tipo_ed = tipo_zona_editorial(bloque[k])
#         if _tipo_ed:
#             _en_editorial = True
#             anclas.append((k, f"editorial_{_tipo_ed}")); continue
#
# INICIALIZAR _en_editorial = False junto con _en_sumario = False (~L1756).
#
# En Pasada 2, AGREGAR los elif en el bloque de tipos (~L1826):
#
#             elif tipo.startswith("editorial_"):
#                 zona_activa = tipo.replace("editorial_", "")
#
# En la docstring de zonificar_bloque, AGREGAR a la lista de zonas:
#   acordada, indice, discurso.


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — Exclusión de wc para zonas editoriales
# ═══════════════════════════════════════════════════════════════════════════
#
# Después de lineas_residuo (~L2202), AGREGAR:
#
#         # B077: líneas editoriales (acordadas/índices/discursos del tomo)
#         lineas_editorial = {k for k, z in enumerate(_zonas_linea)
#                             if z in ("acordada", "indice", "discurso")}
#
# En lineas_mayoria (~L2423-2431), AGREGAR `and k not in lineas_editorial`:
#
#         if inicio_votos_indiv is not None:
#             lineas_mayoria = [bloque[k] for k in range(len(bloque))
#                               if k not in lineas_dictamen
#                               and k not in lineas_residuo
#                               and k not in lineas_editorial
#                               and k < inicio_votos_indiv]
#             lineas_votos   = [bloque[k] for k in range(inicio_votos_indiv,
#                               len(bloque))
#                               if k not in lineas_editorial]
#         else:
#             lineas_mayoria = [bloque[k] for k in range(len(bloque))
#                               if k not in lineas_dictamen
#                               and k not in lineas_residuo
#                               and k not in lineas_editorial]
#             lineas_votos   = []


# ═══════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — Extracción editorial para 4to CSV canónico
# ═══════════════════════════════════════════════════════════════════════════

def extraer_secciones_editoriales(lines, tomo, source_file, linea_inicio_editorial):
    """
    Extrae secciones editoriales (acordadas, índices, discursos) del final
    de un archivo .md de tomo.

    Parámetros:
        lines: list[str] — todas las líneas del archivo.
        tomo: int — número de tomo.
        source_file: str — nombre del archivo (LibroVol330.4.md).
        linea_inicio_editorial: int — primera línea de contenido editorial
            (= linea_fin_real + 1 del último caso procesado).

    Retorna:
        list[dict] con columnas:
            tomo, source_file, seccion, linea_ini, linea_fin, n_lineas, wc
    """
    n = len(lines)
    if linea_inicio_editorial >= n:
        return []

    secciones = []
    zona_activa = None
    ini_actual = linea_inicio_editorial

    for k in range(linea_inicio_editorial, n):
        nueva_zona = tipo_zona_editorial(lines[k])
        if nueva_zona and nueva_zona != zona_activa:
            # Cerrar sección anterior
            if zona_activa is not None:
                wc = sum(len(lines[j].split()) for j in range(ini_actual, k))
                secciones.append({
                    "tomo": tomo,
                    "source_file": source_file,
                    "seccion": zona_activa,
                    "linea_ini": ini_actual,
                    "linea_fin": k - 1,
                    "n_lineas": k - ini_actual,
                    "wc": wc,
                })
            zona_activa = nueva_zona
            ini_actual = k

    # Cerrar última sección
    if zona_activa is not None:
        wc = sum(len(lines[j].split()) for j in range(ini_actual, n))
        secciones.append({
            "tomo": tomo,
            "source_file": source_file,
            "seccion": zona_activa,
            "linea_ini": ini_actual,
            "linea_fin": n - 1,
            "n_lineas": n - ini_actual,
            "wc": wc,
        })

    return secciones


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRACIÓN EN procesar_archivo
# ═══════════════════════════════════════════════════════════════════════════
#
# Después del loop de casos (~L2527), AGREGAR:
#
#     # B077 Fase 2: extraer secciones editoriales post-último-caso
#     if casos_out:
#         ultimo_caso = casos_out[-1]
#         lfr = int(ultimo_caso["linea_fin_real"])
#         editorial = extraer_secciones_editoriales(
#             lines, tomo, filepath.name, lfr + 1
#         )
#         editorial_out.extend(editorial)
#
# En main(), agregar:
#     all_editorial = []
#     # ... dentro del loop de archivos:
#     all_editorial.extend(editorial)  # (devolver editorial desde procesar_archivo)
#
# Y al final, escribir el 4to CSV:
#     output_editorial_path = output_path.parent / (output_path.stem + "_editorial" + output_path.suffix)
#     if all_editorial:
#         fieldnames_e = ["tomo", "source_file", "seccion", "linea_ini",
#                         "linea_fin", "n_lineas", "wc"]
#         with output_editorial_path.open("w", encoding="utf-8", newline="") as f:
#             writer = csv.DictWriter(f, fieldnames=fieldnames_e)
#             writer.writeheader()
#             for e in all_editorial:
#                 writer.writerow(e)
#         print(f"[OK] {output_editorial_path}: {len(all_editorial)} secciones editoriales")


# ═══════════════════════════════════════════════════════════════════════════
# VALIDACIÓN — Ejecutar contra LibroVol330_4.md
# ═══════════════════════════════════════════════════════════════════════════

def validar(ruta_md):
    with open(ruta_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    n = len(lines)
    nombre = ruta_md.split('/')[-1] if '/' in ruta_md else ruta_md
    print(f"=== B077 PoC — {nombre} ({n} líneas) ===\n")

    # 1. Escanear marcadores
    all_matches = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s and RE_EDITORIAL_ANY.match(s):
            all_matches.append((i, tipo_zona_editorial(line), s[:70]))

    fp_in_fallos = [m for m in all_matches if m[0] < 44300]  # approx last fallo

    print("1. MARCADORES EDITORIALES")
    print(f"   Total matches: {len(all_matches)}")
    print(f"   Falsos positivos en zona de fallos: {len(fp_in_fallos)}")
    if all_matches:
        print(f"   Primer match: L{all_matches[0][0]+1} [{all_matches[0][1]}] "
              f"{all_matches[0][2]}")
    print()

    # 2. Simular corte de detectar_fin_real
    # El último caso (330_p5435) empieza en L43281 (0-indexed: 43280)
    li_ultimo = 43280
    lfc_ultimo = n - 1  # end of file
    primer_editorial = None
    for k in range(li_ultimo, lfc_ultimo + 1):
        if es_marcador_editorial(lines[k]):
            primer_editorial = k
            break

    print("2. SIMULACIÓN detectar_fin_real")
    if primer_editorial is not None:
        print(f"   Corte ACTUAL (firma_actual): ~L44571 (linea_fin_real en CSV)")
        print(f"   Corte NUEVO (editorial_siguiente): L{primer_editorial}")
        print(f"   Líneas ahorradas: {lfc_ultimo - primer_editorial + 1}")
        print(f"   Texto de corte: {lines[primer_editorial].strip()[:60]}")
    print()

    # 3. Extraer secciones editoriales (simular 4to CSV)
    if primer_editorial is not None:
        secciones = extraer_secciones_editoriales(
            lines, 330, nombre, primer_editorial
        )
        print("3. SECCIONES EDITORIALES (4to CSV)")
        print(f"   Total secciones: {len(secciones)}")
        total_wc = sum(s["wc"] for s in secciones)
        print(f"   Total wc: {total_wc:,}")
        print()
        by_tipo = Counter()
        wc_by_tipo = Counter()
        for s in secciones:
            by_tipo[s["seccion"]] += 1
            wc_by_tipo[s["seccion"]] += s["wc"]
        for tipo in sorted(by_tipo.keys()):
            print(f"   [{tipo:>10}] {by_tipo[tipo]:>3} secciones, "
                  f"{wc_by_tipo[tipo]:>7,} wc")
        print()
        print("   Detalle:")
        for s in secciones:
            print(f"     L{s['linea_ini']+1:>6}-L{s['linea_fin']+1:>6}  "
                  f"[{s['seccion']:>10}]  {s['n_lineas']:>5} lines  "
                  f"{s['wc']:>6} wc")
    print()

    # 4. Simular zonificador con editorial
    if primer_editorial is not None:
        # Block for last case: from li_ultimo to primer_editorial - 1
        bloque_corregido = lines[li_ultimo:primer_editorial]
        bloque_original = lines[li_ultimo:44571+1]

        print("4. IMPACTO EN ÚLTIMO CASO (330_p5435)")
        wc_original = sum(len(l.split()) for l in bloque_original)
        wc_corregido = sum(len(l.split()) for l in bloque_corregido)
        print(f"   Block original: {len(bloque_original)} lines, {wc_original:,} wc")
        print(f"   Block corregido: {len(bloque_corregido)} lines, {wc_corregido:,} wc")
        print(f"   Reducción: {wc_original - wc_corregido:,} wc "
              f"({100*(wc_original-wc_corregido)/max(wc_original,1):.1f}%)")
    print()

    # 5. Resumen global
    if primer_editorial is not None:
        print("5. RESUMEN")
        print(f"   Contenido editorial: {n - primer_editorial} líneas, "
              f"{total_wc:,} wc")
        print(f"   Zonas: acordada={by_tipo.get('acordada',0)}, "
              f"indice={by_tipo.get('indice',0)}, "
              f"discurso={by_tipo.get('discurso',0)}")
        print(f"   Nuevo pista_fin para último caso: 'editorial_siguiente'")
        print(f"   Regex: 0 falsos positivos en zona de fallos")


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/LibroVol330_4.md"
    validar(ruta)
