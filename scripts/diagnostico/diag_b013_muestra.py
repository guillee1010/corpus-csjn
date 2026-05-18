"""
Diagnóstico B013 — muestra de casos sin firma con dispositivo.
Muestra para cada caso:
  - posición de RE_APERTURA en el bloque (apertura_rel)
  - posición del primer match de dispositivo (por_ello_rel)
  - si por_ello_rel < apertura_rel (= premature)
  - 3 líneas alrededor de cada hit
"""
import csv, re
from pathlib import Path

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


# — Casos a diagnosticar —
CASOS = [
    # "dispositivo_real" (texto parece real, firma vacía)
    "329_p53", "330_p120", "330_p1398", "341_p2015",
    # "otro" (texto argumentativo)
    "348_p189", "337_p1361", "329_p4449",
    # "dictamen"
    "333_p1205", "329_p2986",
    # B055 (firma truncada)
    "329_p49", "341_p971", "330_p1718",
]

BASE = Path(".")
loc_path = BASE / "output" / "localizacion" / "fallos_localizados.csv"

# Cargar localizados
with open(loc_path, encoding="utf-8") as f:
    loc_rows = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

corpus = BASE / "corpus"

for caso_id in CASOS:
    meta = loc_rows.get(caso_id)
    if not meta:
        print(f"\n{'='*70}\n{caso_id}: NO ENCONTRADO en localizados\n")
        continue

    archivo = meta.get("archivo", "")
    li = int(meta["linea_inicio"]) if meta.get("linea_inicio") else None
    lf = int(meta["linea_fin"]) if meta.get("linea_fin") else None
    if li is None or lf is None:
        print(f"\n{'='*70}\n{caso_id}: sin linea_inicio/fin\n")
        continue

    # Leer archivo
    fpath = corpus / archivo
    if not fpath.exists():
        print(f"\n{'='*70}\n{caso_id}: archivo {archivo} no existe\n")
        continue

    lines = fpath.read_text(encoding="utf-8").split("\n")
    bloque = lines[li:lf+1]

    # Buscar apertura
    apertura_rel = None
    for k, ln in enumerate(bloque):
        if RE_APERTURA.match(ln.strip()):
            apertura_rel = k
            break

    # Buscar TODOS los matches de dispositivo (no solo el primero)
    disp_matches = []
    for k, ln in enumerate(bloque):
        s = ln.strip()
        if not s:
            continue
        es, tipo = detectar_apertura_dispositivo(s)
        if es:
            disp_matches.append((k, tipo, s[:100]))

    primer_disp = disp_matches[0] if disp_matches else None

    print(f"\n{'='*70}")
    print(f"CASO: {caso_id}  |  archivo: {archivo}")
    print(f"Bloque: líneas {li}–{lf} ({len(bloque)} líneas)")
    print(f"apertura_rel: {apertura_rel}", end="")
    if apertura_rel is not None:
        print(f"  (línea abs {li + apertura_rel}: {bloque[apertura_rel].strip()[:80]})")
    else:
        print("  (SIN MARCADOR)")

    print(f"Primer dispositivo: ", end="")
    if primer_disp:
        k0, tipo0, txt0 = primer_disp
        es_prematuro = apertura_rel is not None and k0 < apertura_rel
        print(f"rel {k0} ({tipo0}) {'*** PREMATURO ***' if es_prematuro else ''}")
        print(f"  texto: {txt0}")
    else:
        print("NINGUNO")

    print(f"Total matches dispositivo en bloque: {len(disp_matches)}")
    for k, tipo, txt in disp_matches:
        tag = ""
        if apertura_rel is not None:
            tag = " [pre-apertura]" if k < apertura_rel else " [post-apertura]"
        print(f"  rel {k:>4} ({tipo:<20}){tag}: {txt[:90]}")

    # Mostrar primeras 5 y últimas 5 líneas del bloque para contexto
    print(f"\n--- Primeras 5 líneas del bloque ---")
    for i in range(min(5, len(bloque))):
        print(f"  [{i:>4}] {bloque[i].rstrip()[:100]}")
    print(f"--- Últimas 5 líneas del bloque ---")
    for i in range(max(0, len(bloque)-5), len(bloque)):
        print(f"  [{i:>4}] {bloque[i].rstrip()[:100]}")