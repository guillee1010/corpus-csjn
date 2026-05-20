# H042 - aplicar_patch_b055_v3.py
# Fix B055 v3: collect_firma_lines con guarda sobre texto acumulado.
# Correr desde raiz del repo.

import re
from pathlib import Path

PARSER_SRC = Path("scripts/pipeline/parser.py")
PARSER_DST = Path("scripts/diagnostico/H055/parser_b055_fix.py")

src = PARSER_SRC.read_text(encoding="utf-8")
lines_src = src.splitlines(keepends=True)

func_start = None
func_end = None
for i, ln in enumerate(lines_src):
    if ln.strip().startswith("def collect_firma_lines("):
        func_start = i
    elif func_start is not None and func_end is None:
        stripped = ln.strip()
        if stripped and not ln[0].isspace():
            func_end = i
            break

if func_start is None or func_end is None:
    print("ERROR: no encontre collect_firma_lines en parser.py")
    raise SystemExit(1)

print(f"collect_firma_lines encontrada en lineas {func_start+1}-{func_end}")

# --- Construir el bloque de reemplazo ---

apellidos = [
    "rosatti", "rosenkrantz", "lorenzetti", "maqueda",
    r"highton(?:\s+de\s+nolasco)?", "nolasco",
    r"garc.a.mansilla", "mansilla",
    "zaffaroni", "petracchi", "argibay", "fayt",
    "boggiano", "belluscio", r"l.pez", r"v.zquez", "nazareno",
    r"rodr.guez\s+basavilbaso", "basavilbaso",
    "otero", "cavallo",
    "borinsky", "catania", "gemignani", "petrone", "ledesma",
    r"barroetave.a", "hornos", r"leal\s+de\s+ibarra",
    "catucci", "cattucci", "riggi", "yacobucci", "figueroa", "mahiques",
]
apellidos_pattern = "|".join(apellidos)

# Verificar que el patron compila
re.compile(apellidos_pattern, re.I)
print(f"Patron de apellidos OK ({len(apellidos)} entradas)")

# Constante de modulo
re_const = (
    f'_RE_FIRMA_COMPLETA = re.compile(\n'
    f'    r"(?:{apellidos_pattern})"\n'
    f'    r"(?:\\s*\\((?:en\\s+disidencia|seg[u\u00fa]n\\s+su\\s+voto)(?:\\s+parcial)?\\))?\\s*\\.\\s*$",\n'
    f'    re.I\n'
    f')\n\n'
)

emdash = "\u2014"
endash = "\u2013"

func_text = (
    'def collect_firma_lines(bloque, idx_start, max_lines=None):\n'
    '    """Junta lineas de firma. H042 fix B055 v3.\n'
    '\n'
    '    - Techo = len(bloque) (bloque acotado por catalogo/mapa).\n'
    '    - Guarda: cuando texto acumulado termina en apellido conocido\n'
    '      + calificador opcional + punto -> firma podria estar completa\n'
    '      -> aplicar guarda estricta. Si no -> seguir con breaks.\n'
    '    - Tolera 1 linea vacia intercalada si la siguiente parece firma.\n'
    '    """\n'
    '    techo = len(bloque) if max_lines is None else min(idx_start + max_lines, len(bloque))\n'
    '    firma_lines = []\n'
    '    started = False\n'
    '\n'
    '    def es_continuacion_firma(s):\n'
    '        if any(p.search(s) for p, _ in JUECES_CONOCIDOS):\n'
    '            return True\n'
    f'        if "{emdash}" in s or " - " in s or "{endash}" in s:\n'
    '            return True\n'
    '        if RE_CALIFICADOR.search(s):\n'
    '            return True\n'
    '        return False\n'
    '\n'
    '    for k in range(idx_start, techo):\n'
    '        line = bloque[k].strip()\n'
    '        if not line:\n'
    '            if started:\n'
    '                next_firma = False\n'
    '                for j in range(k + 1, min(k + 3, techo)):\n'
    '                    nxt = bloque[j].strip()\n'
    '                    if not nxt:\n'
    '                        continue\n'
    '                    if es_continuacion_firma(nxt):\n'
    '                        next_firma = True\n'
    '                    break\n'
    '                if next_firma:\n'
    '                    continue\n'
    '                break\n'
    '            continue\n'
    '        if not started:\n'
    '            if any(p.search(line) for p, _ in JUECES_CONOCIDOS):\n'
    '                started = True\n'
    '                firma_lines.append(line)\n'
    '            continue\n'
    '        # Breaks estructurales\n'
    '        if RE_PAGE_HEADER.match(line) or line.startswith("Recurso de"):\n'
    '            break\n'
    '        if RE_VOTO_HDR.match(line) or RE_DISID_HDR.match(line):\n'
    '            break\n'
    '        if line.startswith("Tribunal de origen") or line.startswith("Tribunal que"):\n'
    '            break\n'
    '        # Guarda: texto acumulado termina en apellido conocido + punto?\n'
    '        firma_so_far = " ".join(firma_lines)\n'
    '        if _RE_FIRMA_COMPLETA.search(firma_so_far):\n'
    '            if not es_continuacion_firma(line):\n'
    '                break\n'
    '        firma_lines.append(line)\n'
    '    return " ".join(firma_lines)\n'
    '\n'
)

replacement = re_const + func_text
patched = lines_src[:func_start] + [replacement] + lines_src[func_end:]

PARSER_DST.parent.mkdir(parents=True, exist_ok=True)
PARSER_DST.write_text("".join(patched), encoding="utf-8")
print(f"Parser parcheado v3: {PARSER_DST}")
print()
print("Correr:")
print(f"  python {PARSER_DST} --localizados output/localizacion/fallos_localizados.csv --mapa output/mapa/mapa_paginas.csv --corpus corpus --output output/diagnostico/B055/csjn_casos_b055_fix.csv")
print()
print("Comparar:")
print("  python scripts/diagnostico/H055/comparar_b055_fix.py")
