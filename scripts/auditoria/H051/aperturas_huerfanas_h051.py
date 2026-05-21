"""
Aperturas huérfanas — ¿fallos no catalogados o citas textuales?

Para cada "FALLO DE LA CORTE SUPREMA" en el corpus, determina si cae
dentro del rango de páginas de un fallo catalogado (= cita textual) o
fuera (= posible fallo no catalogado).

Uso:
  python scripts/auditoria/H051/aperturas_huerfanas_h051.py
"""

import re
import csv
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CORPUS_DIR = REPO_ROOT / "corpus"
LOCALIZADOS = REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
OUTPUT = Path(__file__).resolve().parent / "aperturas_huerfanas_h051.md"

RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I)

# ── Cargar datos ──────────────────────────────────────────────────────────────

with open(LOCALIZADOS, encoding="utf-8") as f:
    cat = list(csv.DictReader(f))

with open(MAPA, encoding="utf-8") as f:
    mapa = list(csv.DictReader(f))

# Mapa: linea → pagina por archivo
linea_a_pagina = defaultdict(list)  # {archivo: [(linea_header, pagina), ...]}
for r in mapa:
    linea_a_pagina[r["archivo"]].append((int(r["linea_header"]), int(r["pagina"])))
for k in linea_a_pagina:
    linea_a_pagina[k].sort()


def pagina_de_linea(archivo, linea):
    """Dado un archivo y una línea, devuelve la página correspondiente."""
    headers = linea_a_pagina.get(archivo, [])
    if not headers:
        return None
    pag = headers[0][1]
    for lh, pg in headers:
        if lh > linea:
            break
        pag = pg
    return pag


# Catálogo: rangos de líneas por archivo
cat_rangos = defaultdict(list)  # {archivo: [(li, lf, caso_id), ...]}
for r in cat:
    if not r["archivo"] or not r["linea_inicio"]:
        continue
    li = int(r["linea_inicio"])
    lf = int(r["linea_fin"]) if r["linea_fin"] else li + 500
    cat_rangos[r["archivo"]].append((li, lf, r["caso_id_canonico"]))
for k in cat_rangos:
    cat_rangos[k].sort()


def caso_que_contiene(archivo, linea):
    """Devuelve el caso_id del fallo catalogado que contiene esa línea, o None."""
    for li, lf, cid in cat_rangos.get(archivo, []):
        if li <= linea <= lf:
            return cid
        if li > linea:
            break
    return None


# ── Recorrer corpus ───────────────────────────────────────────────────────────

archivos_cat = sorted(set(r["archivo"] for r in cat if r["archivo"]))
# También aperturas que el catálogo "espera" (líneas de inicio con apertura)
aperturas_catalogadas = set()
for r in cat:
    if r["archivo"] and r["linea_inicio"]:
        aperturas_catalogadas.add((r["archivo"], r["caso_id_canonico"]))

huerfanas = []
dentro_de_caso = []
total_aperturas = 0

for archivo in archivos_cat:
    path = CORPUS_DIR / archivo
    if not path.exists():
        continue

    lines = path.read_text(encoding="utf-8").split("\n")

    for k, ln in enumerate(lines):
        if not RE_APERTURA.match(ln.strip()):
            continue
        total_aperturas += 1

        caso_contenedor = caso_que_contiene(archivo, k)
        pag = pagina_de_linea(archivo, k)

        # ¿Es la apertura "propia" de un caso catalogado?
        # Verificar si la línea está cerca del linea_inicio de algún caso
        es_propia = False
        for li, lf, cid in cat_rangos.get(archivo, []):
            if abs(k - li) <= 3:
                es_propia = True
                break

        if es_propia:
            continue  # apertura esperada, parte del catálogo

        # Contexto: 2 líneas antes y después
        ctx_antes = []
        for j in range(max(0, k - 3), k):
            s = lines[j].strip()
            if s:
                ctx_antes.append(s)
        ctx_despues = []
        for j in range(k + 1, min(len(lines), k + 4)):
            s = lines[j].strip()
            if s:
                ctx_despues.append(s)

        entry = {
            "archivo": archivo,
            "linea": k,
            "pagina": pag,
            "caso_contenedor": caso_contenedor or "NINGUNO",
            "ctx_antes": " | ".join(ctx_antes[-2:]) if ctx_antes else "",
            "ctx_despues": " | ".join(ctx_despues[:2]) if ctx_despues else "",
        }

        if caso_contenedor:
            dentro_de_caso.append(entry)
        else:
            huerfanas.append(entry)

# ── Generar reporte ───────────────────────────────────────────────────────────

md = []
md.append("# Aperturas huérfanas — Reporte H051\n")
md.append(f"Total aperturas en corpus: {total_aperturas}")
md.append(f"Aperturas propias de caso catalogado: {total_aperturas - len(dentro_de_caso) - len(huerfanas)}")
md.append(f"Aperturas dentro de otro caso (citas): {len(dentro_de_caso)}")
md.append(f"Aperturas huérfanas (sin caso): {len(huerfanas)}\n")

if dentro_de_caso:
    md.append(f"## Aperturas dentro de otro caso ({len(dentro_de_caso)})\n")
    md.append("Estas son 'FALLO DE LA CORTE SUPREMA' que caen dentro del rango")
    md.append("de líneas de un fallo catalogado. Probablemente citas textuales")
    md.append("de sentencias reproducidas dentro del fallo contenedor.\n")
    for e in dentro_de_caso:
        md.append(f"- `{e['archivo']}` L{e['linea']} (pág {e['pagina']}) "
                  f"dentro de `{e['caso_contenedor']}`")
        if e["ctx_antes"]:
            md.append(f"  - antes: {e['ctx_antes'][:120]}")
        if e["ctx_despues"]:
            md.append(f"  - después: {e['ctx_despues'][:120]}")
    md.append("")

if huerfanas:
    md.append(f"## Aperturas huérfanas ({len(huerfanas)})\n")
    md.append("Estas aperturas NO caen dentro del rango de ningún caso catalogado.")
    md.append("Podrían ser fallos genuinamente no catalogados.\n")
    for e in huerfanas:
        md.append(f"- `{e['archivo']}` L{e['linea']} (pág {e['pagina']})")
        if e["ctx_antes"]:
            md.append(f"  - antes: {e['ctx_antes'][:120]}")
        if e["ctx_despues"]:
            md.append(f"  - después: {e['ctx_despues'][:120]}")
    md.append("")

OUTPUT.write_text("\n".join(md), encoding="utf-8")

# stdout
print(f"  Aperturas totales:     {total_aperturas}")
print(f"  Propias de catálogo:   {total_aperturas - len(dentro_de_caso) - len(huerfanas)}")
print(f"  Citas dentro de caso:  {len(dentro_de_caso)}")
print(f"  Huérfanas:             {len(huerfanas)}")
print(f"\n  [OK] {OUTPUT.name}")
