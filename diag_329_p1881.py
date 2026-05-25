"""
H074 — Diagnóstico regresión 329_p1881 (Tortorelli)
Correr desde la raíz del repo: python scripts/auditoria/H074/diag_329_p1881.py
O copiar a la raíz y correr: python diag_329_p1881.py
"""
import csv, re, sys
from pathlib import Path

# ── Ajustar paths ──
REPO = Path(r"C:\Users\guill\Proyectos\corpus-csjn")
CSV_PATH = REPO / "output/parser/csjn_casos.csv"
CORPUS = REPO / "corpus"

CASO = "329_p1881"

# ── Leer CSV ──
with open(CSV_PATH, encoding="utf-8") as f:
    rows = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

r = rows[CASO]
source = CORPUS / r["source_file"]
li = int(r["linea_inicio"])
lfr = int(r["linea_fin_real"])
lf = int(r["linea_fin"]) if r["linea_fin"] else None

print(f"=== {CASO} ===")
print(f"source: {source.name}")
print(f"linea_inicio: {li}  linea_fin: {lf}  linea_fin_real: {lfr}")
print(f"status_fin: {r['status_fin']}  pista_fin: {r['pista_fin']}")
print(f"status_loc: {r['status_localizacion']}")
print(f"firma_raw: {r['firma_raw']!r}")
print(f"por_ello_text (primeros 200): {r['por_ello_text'][:200]!r}")
print(f"word_count: {r['word_count']}")
print()

# ── Leer bloque ──
text = source.read_text(encoding="utf-8")
lines = text.split("\n")
bloque = lines[li:lfr+1]
print(f"Bloque: {len(bloque)} líneas")
print()

# ── 1. Token de este caso y del siguiente ──
nombres = r.get("case_name_indice", "")
print(f"case_name_indice: {nombres}")

_GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
              "afip", "buenos", "nacional", "administracion",
              "federal", "direccion", "instituto"}
_SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
         "empresa", "compania", "compañia", "compañía"}

def primer_token_post_b093(nombres_indice):
    variantes = nombres_indice.split("|")
    for v in variantes:
        tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", v.strip())
        for t in tokens:
            if len(t) >= 4 and t.lower() not in _SKIP and t.lower() not in _GENERICOS:
                return t
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", variantes[0].strip())
    for t in tokens:
        if len(t) >= 4 and t.lower() not in _SKIP:
            return t
    return ""

def primer_token_pre_b093(nombres_indice):
    """Simula comportamiento pre-B093: primer token >=4 chars, sin skip de genéricos."""
    variantes = nombres_indice.split("|")
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", variantes[0].strip())
    for t in tokens:
        if len(t) >= 4 and t.lower() not in _SKIP:
            return t
    return ""

token_post = primer_token_post_b093(nombres)
token_pre = primer_token_pre_b093(nombres)
print(f"Token THIS caso — pre-B093: {token_pre!r}  post-B093: {token_post!r}")

# Token del siguiente
# Buscar caso siguiente por linea_inicio
t329 = [(k,v) for k,v in rows.items() if v["tomo"]=="329" and v["source_file"]==r["source_file"]]
t329.sort(key=lambda x: int(x[1]["linea_inicio"]))
siguiente = None
for i, (k,v) in enumerate(t329):
    if k == CASO and i+1 < len(t329):
        siguiente = t329[i+1]
        break

if siguiente:
    sig_id, sig_r = siguiente
    sig_nombres = sig_r.get("case_name_indice", "")
    sig_token_post = primer_token_post_b093(sig_nombres)
    sig_token_pre = primer_token_pre_b093(sig_nombres)
    print(f"Token NEXT ({sig_id}) — pre: {sig_token_pre!r}  post: {sig_token_post!r}")
    print(f"  case_name_indice: {sig_nombres[:80]}")
print()

# ── 2. ¿Dónde aparece "Aires" en el bloque? ──
print(f"=== Ocurrencias de token post-B093 ({token_post!r}) en bloque ===")
pat = re.compile(r'\b' + re.escape(token_post) + r'\b', re.I)
for k, ln in enumerate(bloque):
    if pat.search(ln):
        abs_line = li + k
        preview = ln.strip()[:100]
        print(f"  bloque[{k:>4d}] (abs {abs_line}): {preview}")
        if k > 20:  # solo primeras y últimas
            break

# También últimas 30 líneas
print(f"\n=== Últimas 30 líneas del bloque ===")
for k in range(max(0, len(bloque)-30), len(bloque)):
    ln = bloque[k].strip()
    if ln:
        abs_line = li + k
        print(f"  bloque[{k:>4d}] (abs {abs_line}): {ln[:120]}")

# ── 3. Buscar firma manualmente ──
JUECES = ["PETRACCHI", "HIGHTON", "MAQUEDA", "ZAFFARONI", "LORENZETTI",
          "FAYT", "ARGIBAY", "BELLUSCIO", "BOGGIANO", "MOLINÉ"]
print(f"\n=== Líneas con nombres de jueces en todo el bloque ===")
for k, ln in enumerate(bloque):
    s = ln.strip()
    for j in JUECES:
        if j in s.upper():
            abs_line = li + k
            print(f"  bloque[{k:>4d}] (abs {abs_line}): {s[:120]}  [{j}]")
            break

# ── 4. Buscar "Por ello" ──
print(f"\n=== Líneas con 'Por ello' en bloque ===")
for k, ln in enumerate(bloque):
    if re.search(r'Por ello', ln):
        abs_line = li + k
        preview = ln.strip()[:120]
        print(f"  bloque[{k:>4d}] (abs {abs_line}): {preview}")

# ── 5. refinar_inicio_por_titulo simulado ──
print(f"\n=== refinar_inicio_por_titulo simulación ===")
if token_post and len(token_post) >= 4:
    pat2 = re.compile(r'\b' + re.escape(token_post) + r'\b', re.I)
    for k, ln in enumerate(bloque[:50]):
        if pat2.search(ln):
            print(f"  Token {token_post!r} encontrado en bloque[{k}]: {ln.strip()[:100]}")
            print(f"  → offset_recorte = {k}")
            break
    else:
        print(f"  Token {token_post!r} NO encontrado en primeras 50 líneas")
        # Vistos los autos?
        for k, ln in enumerate(bloque[:50]):
            if re.match(r'\s*Vistos los autos', ln):
                print(f"  Fallback 'Vistos los autos' en bloque[{k}]: {ln.strip()[:80]}")
                break
        else:
            print(f"  → ancla_catalogo (sin refinamiento)")

print("\n=== FIN DIAGNÓSTICO ===")
