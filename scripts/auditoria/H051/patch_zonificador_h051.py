"""
Patch H051 — Integra zonificar_bloque() en parser.py.

Aplica 2 cambios:
  1. Agrega la función zonificar_bloque() antes de procesar_archivo
  2. Agrega el check de sumario_editorial en procesar_caso
     (después del check de sumario_con_link)

Uso:
  python scripts/auditoria/H051/patch_zonificador_h051.py

Valida que los anchors existen antes de patchear.
Genera parser.py patcheado in-place (hacer snapshot git ANTES).
"""

from pathlib import Path

PARSER = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "pipeline" / "parser.py"

if not PARSER.exists():
    print(f"ERROR: {PARSER} no encontrado")
    exit(1)

text = PARSER.read_text(encoding="utf-8")

# ══════════════════════════════════════════════════════════════════════════════
# CAMBIO 1: agregar zonificar_bloque() antes de procesar_archivo
# ══════════════════════════════════════════════════════════════════════════════

ANCHOR_1 = "# ── Procesamiento de un archivo ───────────────────────────────────────────────"

ZONIFICADOR = '''
# ── H051 Refacción C: zonificador de bloques ──────────────────────────────────
#
# Asigna una zona a cada línea de un bloque de fallo. Usa 3 pasadas:
#   Pasada 0: marcar headers de página (ruido transversal)
#   Pasada 1: detectar anclas (marcadores estructurales)
#   Pasada 2: propagar zonas entre anclas
#
# Uso actual: clasificar bloques como sumario_editorial (sin cuerpo/disp/firma).
# Uso futuro: reemplazar detección de dictamen, firma, dispositivo por zonas.

def zonificar_bloque(bloque):
    """
    Retorna set de zonas presentes en el bloque.

    Zonas posibles: header_pagina, sumario, dictamen, apertura, cuerpo,
    dispositivo, firma, voto_separado, epilogo, intersticio.
    """
    n = len(bloque)
    zonas = ["intersticio"] * n

    # ── Pasada 0: headers de página ──────────────────────────────────
    for k in range(n):
        s = bloque[k].strip()
        if s and RE_PAGE_HEADER.match(s):
            zonas[k] = "header_pagina"

    # ── Pasada 1: detectar anclas ────────────────────────────────────
    anclas = []
    for k in range(n):
        if zonas[k] == "header_pagina":
            continue
        s = bloque[k].strip()
        if not s:
            continue

        if RE_DICT_HDR.match(s):
            anclas.append((k, "dictamen_inicio")); continue
        if RE_APERTURA.match(s):
            anclas.append((k, "apertura")); continue
        if RE_FECHA_LINEA.match(s):
            anclas.append((k, "fecha")); continue
        if RE_CONSIDERANDO.match(s):
            anclas.append((k, "considerando")); continue
        if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
            anclas.append((k, "voto_header")); continue

        es_disp, _ = detectar_apertura_dispositivo(s)
        if es_disp:
            anclas.append((k, "dispositivo")); continue

        if linea_es_firma_de_juez(bloque[k]):
            anclas.append((k, "firma_linea")); continue

        # Sumario antes de epilogo (prioridad)
        if linea_es_header_sumario(bloque[k]):
            anclas.append((k, "sumario_header")); continue

        # Epilogo solo después de firma/voto/dispositivo
        if RE_DATOS_PARTES.match(s):
            if any(t in ("firma_linea", "voto_header", "dispositivo")
                   for _, t in anclas):
                anclas.append((k, "epilogo_marker")); continue

    # ── Pasada 2: propagar zonas ─────────────────────────────────────
    zona_activa = "intersticio"
    ancla_en = {pos: tipo for pos, tipo in anclas}

    for k in range(n):
        if zonas[k] == "header_pagina":
            continue
        if k in ancla_en:
            tipo = ancla_en[k]
            if tipo == "sumario_header":
                zona_activa = "sumario"
            elif tipo == "dictamen_inicio":
                zona_activa = "dictamen"
            elif tipo == "apertura":
                zona_activa = "apertura"
            elif tipo == "fecha":
                if zona_activa in ("apertura", "intersticio", "sumario"):
                    zona_activa = "cuerpo"
                elif zona_activa == "dictamen":
                    if not any(t == "apertura" for _, t in anclas if _ > k):
                        zona_activa = "cuerpo"
            elif tipo == "considerando":
                zona_activa = "cuerpo"
            elif tipo == "dispositivo":
                zona_activa = "dispositivo"
            elif tipo == "firma_linea":
                zona_activa = "firma"
            elif tipo == "voto_header":
                zona_activa = "voto_separado"
            elif tipo == "epilogo_marker":
                zona_activa = "epilogo"
        zonas[k] = zona_activa if zonas[k] != "header_pagina" else "header_pagina"

    return set(zonas)


'''

if ANCHOR_1 not in text:
    print(f"ERROR: anchor 1 no encontrado en parser.py")
    exit(1)

text = text.replace(ANCHOR_1, ZONIFICADOR + ANCHOR_1, 1)
print("  [1/2] zonificar_bloque() insertado")

# ══════════════════════════════════════════════════════════════════════════════
# CAMBIO 2: agregar check de sumario_editorial en procesar_caso
# ══════════════════════════════════════════════════════════════════════════════

ANCHOR_2 = "        # Fecha del fallo. v16: cambio respecto a v15."

SUMARIO_CHECK = '''        # ── H051: detector de sumario_editorial ────────────────────────────
        # Usa el zonificador para clasificar el bloque. Si no tiene zonas
        # de cuerpo, dispositivo ni firma, es contenido editorial puro
        # (sumarios temáticos, dictámenes sueltos, remisiones a precedentes).
        # Diferencia con sumario_con_link: estos NO tienen el patrón
        # "(*) Sentencia del...Ver..." sino que son entradas del índice
        # sin fallo reproducido en el tomo.
        _zonas_bloque = zonificar_bloque(bloque)
        _es_sumario_editorial = (
            "cuerpo" not in _zonas_bloque
            and "dispositivo" not in _zonas_bloque
            and "firma" not in _zonas_bloque
        )
        if _es_sumario_editorial:
            casos_out.append(construir_caso_sumario_link(
                caso_id_canonico=caso_id_canonico,
                tomo=tomo,
                nombres_indice=nombres_indice,
                source_file=filepath.name,
                linea_inicio=linea_inicio,
                linea_fin=linea_fin,
                linea_fin_real=linea_fin_real,
                status_loc_final=status_loc_final,
                status_fin=status_fin,
                pista_fin=pista_fin,
            ))
            # Reclasificar tipo_entrada en el dict ya creado
            casos_out[-1]["tipo_entrada"] = "sumario_editorial"
            continue

'''

if ANCHOR_2 not in text:
    print(f"ERROR: anchor 2 no encontrado en parser.py")
    exit(1)

text = text.replace(ANCHOR_2, SUMARIO_CHECK + ANCHOR_2, 1)
print("  [2/2] check sumario_editorial insertado")

# ══════════════════════════════════════════════════════════════════════════════
# Escribir
# ══════════════════════════════════════════════════════════════════════════════

PARSER.write_text(text, encoding="utf-8")
print(f"\n[OK] {PARSER} patcheado")
print(f"     Correr el parser y comparar output contra snapshot anterior.")
