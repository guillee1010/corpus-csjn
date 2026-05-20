# H042 - aplicar_patch_b055.py
# Genera parser parcheado con fix de collect_firma_lines.
# Correr desde raiz del repo.

from pathlib import Path

PARSER_SRC = Path("scripts/pipeline/parser.py")
PARSER_DST = Path("scripts/diagnostico/H055/parser_b055_fix.py")

lines = PARSER_SRC.read_text(encoding="utf-8").splitlines(keepends=True)

# Buscar inicio y fin de collect_firma_lines
func_start = None
func_end = None
for i, ln in enumerate(lines):
    if ln.strip().startswith("def collect_firma_lines("):
        func_start = i
    elif func_start is not None and func_end is None:
        # Fin = siguiente linea que NO es indentada y no es vacia
        # (siguiente def o comentario de seccion al nivel 0)
        stripped = ln.strip()
        if stripped and not ln[0].isspace():
            func_end = i
            break

if func_start is None or func_end is None:
    print("ERROR: no encontre collect_firma_lines en parser.py")
    raise SystemExit(1)

print(f"collect_firma_lines encontrada en lineas {func_start+1}-{func_end}")

NEW_FUNC = '''\
def collect_firma_lines(bloque, idx_start, max_lines=None):
    """Junta lineas de firma desde despues de 'Por ello' hasta encontrar fin.

    H042 fix B055:
    - Techo = len(bloque) (el bloque ya esta acotado por catalogo/mapa).
    - Guarda de continuacion post-started: solo seguir si la linea
      tiene JUECES_CONOCIDOS, dash, o calificador.
    - Tolera 1 linea vacia intercalada si la siguiente es firma.
    """
    techo = len(bloque) if max_lines is None else min(idx_start + max_lines, len(bloque))
    firma_lines = []
    started = False

    def es_continuacion_firma(s):
        if any(p.search(s) for p, _ in JUECES_CONOCIDOS):
            return True
        if "\\u2014" in s or " - " in s or "\\u2013" in s:
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
                    continue  # saltar la vacia, seguir recolectando
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
        # Guarda de continuacion: solo seguir si parece firma
        if not es_continuacion_firma(line):
            break
        firma_lines.append(line)
    return " ".join(firma_lines)

'''

# Reemplazar las lineas con unicode correcto
NEW_FUNC = NEW_FUNC.replace("\\u2014", "\u2014").replace("\\u2013", "\u2013")

patched_lines = lines[:func_start] + [NEW_FUNC] + lines[func_end:]

PARSER_DST.parent.mkdir(parents=True, exist_ok=True)
PARSER_DST.write_text("".join(patched_lines), encoding="utf-8")
print(f"Parser parcheado: {PARSER_DST}")
print()
print("Siguiente paso:")
print(f"  python {PARSER_DST}")
print("  python scripts/diagnostico/H055/comparar_b055_fix.py")
