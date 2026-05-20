# H042 - aplicar_patch_b055_v2.py
# Fix B055: collect_firma_lines con guarda condicional.
# - Sin max_lines (techo = len(bloque))
# - Guarda de continuacion SOLO si ultima linea termina en punto
# - Si ultima linea NO termina en punto -> mid-nombre, seguir
# - Tolera 1 linea vacia intercalada con lookahead
# Correr desde raiz del repo.

from pathlib import Path

PARSER_SRC = Path("scripts/pipeline/parser.py")
PARSER_DST = Path("scripts/diagnostico/H055/parser_b055_fix.py")

lines = PARSER_SRC.read_text(encoding="utf-8").splitlines(keepends=True)

func_start = None
func_end = None
for i, ln in enumerate(lines):
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

EMDASH = "\u2014"
ENDASH = "\u2013"

NEW_FUNC = f'''\
def collect_firma_lines(bloque, idx_start, max_lines=None):
    """Junta lineas de firma desde despues de 'Por ello' hasta encontrar fin.

    H042 fix B055 v2:
    - Techo = len(bloque) (el bloque ya esta acotado por catalogo/mapa).
    - Si ultima linea recolectada NO termina en punto, estamos mid-nombre
      -> continuar sin guarda (la firma esta partida entre lineas fisicas).
    - Si ultima linea termina en punto, la firma podria estar completa
      -> guarda estricta: solo seguir si la linea tiene JUECES_CONOCIDOS,
         dash, o calificador.
    - Tolera 1 linea vacia intercalada si la siguiente es firma.
    """
    techo = len(bloque) if max_lines is None else min(idx_start + max_lines, len(bloque))
    firma_lines = []
    started = False

    def es_continuacion_firma(s):
        if any(p.search(s) for p, _ in JUECES_CONOCIDOS):
            return True
        if "{EMDASH}" in s or " - " in s or "{ENDASH}" in s:
            return True
        if RE_CALIFICADOR.search(s):
            return True
        return False

    for k in range(idx_start, techo):
        line = bloque[k].strip()
        if not line:
            if started:
                # Tolerar 1 vacia: lookahead a la siguiente no vacia
                next_firma = False
                for j in range(k + 1, min(k + 3, techo)):
                    nxt = bloque[j].strip()
                    if not nxt:
                        continue
                    if es_continuacion_firma(nxt):
                        next_firma = True
                    break
                if next_firma:
                    continue
                break
            continue
        # Saltarse el dispositivo hasta encontrar firma con jueces conocidos
        if not started:
            if any(p.search(line) for p, _ in JUECES_CONOCIDOS):
                started = True
                firma_lines.append(line)
            continue
        # Una vez empezada la firma: breaks estructurales
        if RE_PAGE_HEADER.match(line) or line.startswith("Recurso de"):
            break
        if RE_VOTO_HDR.match(line) or RE_DISID_HDR.match(line):
            break
        if line.startswith("Tribunal de origen") or line.startswith("Tribunal que"):
            break
        # Si la ultima linea recolectada NO termina en punto,
        # estamos mid-nombre -> continuar sin guarda
        last_collected = firma_lines[-1].rstrip() if firma_lines else ""
        if last_collected.endswith("."):
            # Firma podria estar completa -> guarda estricta
            if not es_continuacion_firma(line):
                break
        # Si no termina en punto, o paso la guarda -> recolectar
        firma_lines.append(line)
    return " ".join(firma_lines)

'''

patched_lines = lines[:func_start] + [NEW_FUNC] + lines[func_end:]

PARSER_DST.parent.mkdir(parents=True, exist_ok=True)
PARSER_DST.write_text("".join(patched_lines), encoding="utf-8")
print(f"Parser parcheado v2: {PARSER_DST}")
print()
print("Correr:")
print(f"  python {PARSER_DST} --localizados output/localizacion/fallos_localizados.csv --mapa output/mapa/mapa_paginas.csv --corpus corpus --output output/diagnostico/B055/csjn_casos_b055_fix.csv")
print()
print("Comparar:")
print("  python scripts/diagnostico/H055/comparar_b055_fix.py")
