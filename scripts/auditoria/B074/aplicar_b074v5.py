"""Aplica el patch B074v5 a parser.py in-place (con backup)."""
import sys, shutil
from pathlib import Path

parser_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\guill\Proyectos\corpus-csjn\scripts\pipeline\parser.py")

code = parser_path.read_text(encoding='utf-8')

old = """        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────
        # Buscar la frontera con el fallo siguiente (carátula/sumario/marcador)
        # para detectar dónde termina realmente el contenido decisorio.
        siguiente = siguiente_caso.get(caso_id_canonico)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""
        prox_header = proximo_header_despues_de(headers_archivo, int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1)
        linea_fin_real, status_fin, pista_fin = detectar_fin_real(
            lines,
            int(linea_inicio),
            int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1,
            prox_header,
            primer_token_siguiente
        )"""

new = """        # ── B074: pre-computar posición del título como lower-bound ─────────
        # Si el título del caso actual aparece en las primeras 15 líneas del
        # bloque, usarlo como li para detectar_fin_real. Así buscar_atras no
        # captura firma del caso anterior incluida en el residuo del bloque.
        # Si no se encuentra en 15 líneas → li original → baseline idéntico.
        _li_for_dfr = int(linea_inicio)
        _token_titulo = primer_token_de_caratula(nombres_indice)
        if _token_titulo and len(_token_titulo) >= 4:
            _pat_titulo = re.compile(r'\\b' + re.escape(_token_titulo) + r'\\b', re.I)
            for _k, _ln in enumerate(bloque[:15]):
                if _pat_titulo.search(_ln):
                    _li_for_dfr = int(linea_inicio) + _k
                    break

        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────
        # Buscar la frontera con el fallo siguiente (carátula/sumario/marcador)
        # para detectar dónde termina realmente el contenido decisorio.
        siguiente = siguiente_caso.get(caso_id_canonico)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""
        prox_header = proximo_header_despues_de(headers_archivo, int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1)
        linea_fin_real, status_fin, pista_fin = detectar_fin_real(
            lines,
            _li_for_dfr,
            int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1,
            prox_header,
            primer_token_siguiente
        )"""

if old not in code:
    print("ERROR: bloque a parchear no encontrado. ¿Ya fue aplicado?")
    sys.exit(1)

code = code.replace(old, new)
parser_path.write_text(code, encoding='utf-8')
print(f"✓ Patch B074v5 aplicado a {parser_path}")
