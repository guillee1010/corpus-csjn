"""
Diagnóstico B013 — cuantificación completa.
Clasifica todos los casos sin_firma + con_dispositivo según:
  - prematuro: primer disp ANTES de apertura_rel
  - post_apertura: primer disp DESPUÉS de apertura_rel
  - sin_marcador: sin RE_APERTURA en bloque
  - sin_dispositivo: ningún match de dispositivo en bloque
"""
import csv, re
from pathlib import Path
from collections import Counter

# — Regexes del parser (copiadas) —
RE_APERTURA = re.compile(
    r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I
)
RE_POR_ELLO = re.compile(r"^Por ello[,.]?\s*", re.I)
POR_ELLO_ARGUMENTAL = {
    "concluyó", "concluyo", "estimo", "estimó", "considera",
    "considero", "consideró", "entiende", "entendió",
    "afirma", "afirmó", "sostiene", "sostuvo",
}
RE_DISPOSITIVO_VARIANTES = [
    ("por_los_fund", re.compile(r"^Por los fundamentos\s+y\s+conc[lu]+siones", re.I)),
    ("por_los_fund_simple", re.compile(r"^Por los fundamentos\b", re.I)),
    ("de_conformidad", re.compile(r"^De conformidad con\b", re.I)),
    ("por_todo_lo_exp", re.compile(r"^Por todo lo expuesto\b", re.I)),
    ("por_todo_ello", re.compile(r"^Por todo ello\b", re.I)),
    ("por_lo_expuesto", re.compile(r"^Por lo expuesto\b", re.I)),
    ("por_estas_razones", re.compile(r"^Por estas razones\b", re.I)),
    ("en_merito", re.compile(r"^En m[ée]rito\s+a\s+lo\b", re.I)),
    ("en_su_merito", re.compile(r"^En su m[ée]rito\b", re.I)),
    ("en_consecuencia", re.compile(r"^En consecuencia\s*,?\s*\b", re.I)),
    ("atento_a", re.compile(r"^Atento\s+(a\s+)?(que|lo|el)\b", re.I)),
]

def detectar_apertura_dispositivo(stripped_line):
    if RE_POR_ELLO.match(stripped_line):
        rest = re.sub(r"^Por ello[,.]?\s*", "", stripped_line, flags=re.I)
        first_w = rest.split()[0].lower().rstrip(",;") if rest.split() else ""
        if first_w in POR_ELLO_ARGUMENTAL:
            return (False, None)
        return (True, "por_ello")
    for nombre, pat in RE_DISPOSITIVO_VARIANTES:
        if pat.match(stripped_line):
            return (True, nombre)
    return (False, None)


BASE = Path(".")
loc_path = BASE / "output" / "localizacion" / "fallos_localizados.csv"
casos_path = BASE / "output" / "parser" / "csjn_casos.csv"
corpus = BASE / "corpus"

# Cargar localizados
with open(loc_path, encoding="utf-8") as f:
    loc_rows = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

# Identificar universo B013: firma_raw vacío, por_ello_text no vacío
b013_ids = []
with open(casos_path, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["firma_raw"] == "" and r["por_ello_text"] != "":
            b013_ids.append(r["caso_id_canonico"])

print(f"Universo B013 total: {len(b013_ids)} casos")

# Cache de archivos leídos
file_cache = {}

cat = Counter()        # prematuro / post_apertura / sin_marcador / sin_disp / sin_loc
tipo_primer = Counter()  # tipo de variante del primer match prematuro
post_apertura_tipos = Counter()  # tipo de variante del primer match post-apertura
post_apertura_ejemplos = []

for caso_id in b013_ids:
    meta = loc_rows.get(caso_id)
    if not meta or not meta.get("linea_inicio") or not meta.get("linea_fin"):
        cat["sin_loc"] += 1
        continue

    archivo = meta["archivo"]
    li = int(meta["linea_inicio"])
    lf = int(meta["linea_fin"])

    fpath = corpus / archivo
    if archivo not in file_cache:
        if not fpath.exists():
            cat["sin_loc"] += 1
            continue
        file_cache[archivo] = fpath.read_text(encoding="utf-8").split("\n")
    lines = file_cache[archivo]
    bloque = lines[li:lf+1]

    # Buscar apertura
    apertura_rel = None
    for k, ln in enumerate(bloque):
        if RE_APERTURA.match(ln.strip()):
            apertura_rel = k
            break

    if apertura_rel is None:
        cat["sin_marcador"] += 1
        continue

    # Buscar primer match de dispositivo
    primer_disp_k = None
    primer_disp_tipo = None
    for k, ln in enumerate(bloque):
        s = ln.strip()
        if not s:
            continue
        es, tipo = detectar_apertura_dispositivo(s)
        if es:
            primer_disp_k = k
            primer_disp_tipo = tipo
            break

    if primer_disp_k is None:
        cat["sin_disp"] += 1
        continue

    if primer_disp_k < apertura_rel:
        cat["prematuro"] += 1
        tipo_primer[primer_disp_tipo] += 1
    else:
        cat["post_apertura"] += 1
        post_apertura_tipos[primer_disp_tipo] += 1
        if len(post_apertura_ejemplos) < 20:
            txt = bloque[primer_disp_k].strip()[:100]
            post_apertura_ejemplos.append(
                f"  {caso_id} rel {primer_disp_k} ({primer_disp_tipo}): {txt}"
            )

print(f"\n=== Clasificación ===")
for k, v in cat.most_common():
    print(f"  {k:<20} {v:>5}")

print(f"\n=== Tipo de variante en prematuros ({cat['prematuro']}) ===")
for k, v in tipo_primer.most_common():
    print(f"  {k:<25} {v:>5}")

print(f"\n=== Tipo de variante en post-apertura ({cat['post_apertura']}) ===")
for k, v in post_apertura_tipos.most_common():
    print(f"  {k:<25} {v:>5}")

print(f"\n=== Ejemplos post-apertura (primeros 20) ===")
for ej in post_apertura_ejemplos:
    print(ej)