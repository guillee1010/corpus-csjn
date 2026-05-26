"""
diag_b095_token_largo.py — Diagnóstico B089 residual (H075)

Examina los 71 casos ancla_catalogo cuyo primer_token_de_caratula tiene >=4 chars.
¿Por qué no matchea en las primeras 50 líneas del bloque?

Hipótesis de fallo:
  H1: Token es prefijo/abreviación (catálogo dice "Transp" pero .md dice "TRANSPORTES")
  H2: Token aparece después de línea 50
  H3: Token cae en últimas 5 líneas del bloque (guarda B089)
  H4: Token no aparece en ningún lado (nombre totalmente distinto)
  H5: Otro (carácter especial, encoding, etc.)

Uso:
    python scripts/auditoria/H075/diag_b095_token_largo.py

Requiere:
    output/parser/csjn_casos.csv, corpus/*.md
"""

import csv
import re
import unicodedata
from pathlib import Path
from collections import Counter

# ── Config ────────────────────────────────────────────────────────────────────
_script_dir = Path(__file__).resolve().parent
if (_script_dir / "output" / "parser" / "csjn_casos.csv").exists():
    REPO_ROOT = _script_dir
elif (_script_dir.parent.parent.parent / "output" / "parser" / "csjn_casos.csv").exists():
    REPO_ROOT = _script_dir.parent.parent.parent
else:
    REPO_ROOT = Path.cwd()

CSV_PATH = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"
MAX_LINEAS = 50  # mismo que MAX_LINEAS_BUSQUEDA_TITULO en parser.py

# ── Lógica replicada de parser.py ─────────────────────────────────────────────

_SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
         "empresa", "compania", "compañia", "compañía"}
_GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
              "afip", "buenos", "nacional", "administracion",
              "federal", "direccion", "instituto"}


def _strip_accents(s):
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def primer_token(nombres_indice):
    if not nombres_indice:
        return ""
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
    return tokens[0] if tokens else ""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Filtrar: ancla_catalogo + token largo
    target = []
    for r in rows:
        if "ancla_catalogo" not in r["status_localizacion"]:
            continue
        tok = primer_token(r["case_name_indice"])
        if len(tok) >= 4:
            target.append((r, tok))

    print(f"═══ DIAGNÓSTICO B089 RESIDUAL — Token ≥4 en ancla_catalogo ═══")
    print(f"Casos: {len(target)}")
    print()

    md_cache = {}
    failure_reasons = Counter()
    details = []

    for idx, (r, tok) in enumerate(target):
        caso_id = r["caso_id_canonico"]
        source = r["source_file"]
        li = int(r["linea_inicio"])
        name_idx = r["case_name_indice"]

        # Leer .md
        md_path = CORPUS_DIR / source
        if not md_path.exists():
            print(f"  ERROR: {md_path} no existe")
            continue

        if source not in md_cache:
            md_cache[source] = md_path.read_text(encoding="utf-8").splitlines()
        lines = md_cache[source]

        bloque = lines[li:]
        bloque_50 = bloque[:MAX_LINEAS]

        # ── Replicar la búsqueda exacta del parser ───────────────────────
        tok_norm = _strip_accents(tok)
        pat_word = re.compile(r'\b' + re.escape(tok_norm) + r'\b', re.I)
        pat_prefix = re.compile(re.escape(tok_norm), re.I)  # sin word boundary

        # Buscar en primeras 50 líneas (como hace el parser)
        match_50_word = None      # match con \b en primeras 50
        match_50_prefix = None    # match sin \b en primeras 50
        match_200_word = None     # match con \b en líneas 50-200
        match_full_word = None    # match con \b en todo el bloque
        match_50_guard = None     # match con \b pero en últimas 5 del bloque

        for k, ln in enumerate(bloque_50):
            ln_norm = _strip_accents(ln)
            if pat_word.search(ln_norm):
                if k >= len(bloque) - 5:
                    match_50_guard = (k, ln.strip()[:70])
                elif match_50_word is None:
                    match_50_word = (k, ln.strip()[:70])
            if pat_prefix.search(ln_norm) and match_50_prefix is None:
                match_50_prefix = (k, ln.strip()[:70])

        # Buscar en líneas 50-200
        for k, ln in enumerate(bloque[MAX_LINEAS:MAX_LINEAS + 150], start=MAX_LINEAS):
            ln_norm = _strip_accents(ln)
            if pat_word.search(ln_norm) and match_200_word is None:
                match_200_word = (k, ln.strip()[:70])
                break

        # Buscar en todo el bloque (hasta 500 líneas)
        if match_50_word is None and match_200_word is None:
            for k, ln in enumerate(bloque[:500]):
                ln_norm = _strip_accents(ln)
                if pat_word.search(ln_norm):
                    match_full_word = (k, ln.strip()[:70])
                    break

        # ── Clasificar razón de fallo ─────────────────────────────────────
        if match_50_word is not None:
            # Debería haber matcheado — ¿bug en el diagnóstico o en el parser?
            reason = "MISTERIO_matchea_en_50"
            detail = f"+{match_50_word[0]:02d}: {match_50_word[1]}"
        elif match_50_guard is not None:
            reason = "H3_guarda_ultimas5"
            detail = f"+{match_50_guard[0]:02d}: {match_50_guard[1]}"
        elif match_50_prefix is not None and match_50_word is None:
            # Token matchea como prefijo pero no como word boundary
            reason = "H1_prefijo_no_word"
            detail = (f"tok='{tok_norm}' matchea como prefijo en "
                      f"+{match_50_prefix[0]:02d}: {match_50_prefix[1]}")
        elif match_200_word is not None:
            reason = "H2_despues_linea50"
            detail = f"+{match_200_word[0]:02d}: {match_200_word[1]}"
        elif match_full_word is not None:
            reason = "H2_muy_lejos"
            detail = f"+{match_full_word[0]:02d}: {match_full_word[1]}"
        else:
            # No aparece en ningún lado
            reason = "H4_ausente_total"
            # Intentar con prefijo en todo el bloque
            prefix_anywhere = None
            for k, ln in enumerate(bloque[:500]):
                if pat_prefix.search(_strip_accents(ln)):
                    prefix_anywhere = (k, ln.strip()[:70])
                    break
            if prefix_anywhere:
                reason = "H1_solo_prefijo_en_bloque"
                detail = (f"tok='{tok_norm}' como prefijo en "
                          f"+{prefix_anywhere[0]:02d}: {prefix_anywhere[1]}")
            else:
                detail = f"tok='{tok_norm}' no aparece en las primeras 500 líneas"

        failure_reasons[reason] += 1
        details.append((caso_id, tok, reason, detail, name_idx))

        # ── Imprimir ──────────────────────────────────────────────────────
        print(f"─── [{idx+1:02d}/{len(target)}] {caso_id} ───")
        print(f"  Token: {tok!r} → norm: {tok_norm!r}")
        print(f"  Índice: {name_idx[:65]}")
        print(f"  Razón: {reason}")
        print(f"  Detalle: {detail}")

        # Mostrar primeras 5 líneas del bloque para contexto
        print(f"  Bloque[0:5]:")
        for k in range(min(5, len(bloque_50))):
            print(f"    +{k:02d}  {bloque_50[k].rstrip()[:75]}")
        print()

    # ── Resumen ───────────────────────────────────────────────────────────
    print("═══ RESUMEN ═══")
    print()
    print("Razón de fallo (71 casos):")
    for reason, cnt in failure_reasons.most_common():
        print(f"  {reason:30s}  {cnt:3d}  ({cnt*100/len(target):.0f}%)")
    print()

    # Agrupar atacables
    atacable_prefix = sum(1 for _,_,r,_,_ in details
                          if r in ("H1_prefijo_no_word", "H1_solo_prefijo_en_bloque"))
    atacable_50plus = sum(1 for _,_,r,_,_ in details
                          if r.startswith("H2_"))
    atacable_guard = sum(1 for _,_,r,_,_ in details
                         if r == "H3_guarda_ultimas5")
    misterio = sum(1 for _,_,r,_,_ in details
                   if r == "MISTERIO_matchea_en_50")
    ausente = sum(1 for _,_,r,_,_ in details
                  if r == "H4_ausente_total")

    print("Resumen por grupo:")
    print(f"  H1 (prefijo/abreviación):   {atacable_prefix:3d} ← fix: relajar word boundary")
    print(f"  H2 (después de línea 50):   {atacable_50plus:3d} ← fix: ampliar ventana")
    print(f"  H3 (guarda últimas 5):      {atacable_guard:3d} ← revisar guarda")
    print(f"  H4 (ausente total):         {ausente:3d} ← nombre diferente, no atacable")
    print(f"  Misterio (debería matchear): {misterio:3d} ← investigar")
    print()

    # Listar H1 para inspección
    h1_cases = [(c,t,d,n) for c,t,r,d,n in details
                if r in ("H1_prefijo_no_word", "H1_solo_prefijo_en_bloque")]
    if h1_cases:
        print(f"═══ DETALLE H1 — Prefijo sin word boundary ({len(h1_cases)} casos) ═══")
        for c, t, d, n in h1_cases:
            print(f"  {c:15s} tok={t!r:18s} | {d[:65]}")
        print()

    # Listar H4 para inspección
    h4_cases = [(c,t,d,n) for c,t,r,d,n in details if r == "H4_ausente_total"]
    if h4_cases:
        print(f"═══ DETALLE H4 — Ausente total ({len(h4_cases)} casos) ═══")
        for c, t, d, n in h4_cases:
            print(f"  {c:15s} tok={t!r:18s} | {n[:55]}")
        print()


if __name__ == "__main__":
    main()
