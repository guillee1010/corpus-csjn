#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
ab_b129_inoficioso.py  —  A/B de B129 (falso inoficioso = dictamen del PGN).

Corre la funcion REAL classify_outcome de parser.py sobre el corpus entero,
con y sin el fix candidato, y reporta:
  - Fidelidad: classify_outcome(textos persistidos) vs outcome persistido.
  - Flips cur->fix (la recuperacion B129).
  - Regresiones (cualquier cosa que NO sea abstracto->merit del falso inoficioso).
  - Checks nominales: 334_p1272 (debe pasar a revoca), 348_p1499 (debe quedar abstracto).

FIX CANDIDATO (NO aplicado al parser; solo monkeypatch en memoria para el A/B):
  lookahead negativo  _NODIC = (?![^.]{0,40}(?:dictamin|procurador))
  sobre el "inoficioso" sin ancla de objeto en:
    - RE_DISP_INOFICIOSO  (parser.py ~l.497, alt-1 y alt-2 inoficioso)
    - pattern alto abstracto de OUTCOME_PATTERNS_DISPOSITIVO (parser.py ~l.342, bare inoficioso)

Solo LEE el corpus. No escribe nada. No toca parser.py.
Correr desde la raiz del repo:  python scripts\diagnostico\H141\ab_b129_inoficioso.py
"""
import csv, re, sys
from pathlib import Path

# csjn_casos_textos.csv tiene campos enormes (considerando_text sin truncar, H113).
# Subir el limite de campo de csv; robusto en Windows, donde sys.maxsize desborda el C long.
_lim = sys.maxsize
while True:
    try:
        csv.field_size_limit(_lim)
        break
    except OverflowError:
        _lim = int(_lim / 10)

# ---------------------------------------------------------------- localizacion
def find_repo_root(start: Path) -> Path:
    for q in [start.resolve(), *start.resolve().parents]:
        if (q / "output" / "parser" / "csjn_casos.csv").exists():
            return q
    sys.exit("ERROR: no encuentro output/parser/csjn_casos.csv subiendo desde " + str(start))

HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
ROOT = find_repo_root(HERE)
PIPELINE = ROOT / "scripts" / "pipeline"
CASOS   = ROOT / "output" / "parser" / "csjn_casos.csv"
TEXTOS  = ROOT / "output" / "parser" / "csjn_casos_textos.csv"

if not PIPELINE.exists():
    sys.exit("ERROR: no existe " + str(PIPELINE) + " (esperaba parser.py ahi).")
sys.path.insert(0, str(PIPELINE))
try:
    import parser as P  # parser.py real; parser_editorial resuelve desde PIPELINE
except Exception as e:
    sys.exit("ERROR importando parser.py desde {}: {}".format(PIPELINE, e))

if not hasattr(P, "classify_outcome"):
    sys.exit("ERROR: parser no expone classify_outcome.")
print("parser.py __version__ =", getattr(P, "__version__", "?"))

# ------------------------------------------------------------------- columnas
def detect_col(fieldnames, *cands):
    for c in cands:
        if c in fieldnames:
            return c
    sys.exit("ERROR: ninguna de {} en columnas {}".format(cands, fieldnames))

# --------------------------------------------------------------- leer corpus
with open(CASOS, encoding="utf-8", newline="") as f:
    r = csv.DictReader(f)
    cid_c = detect_col(r.fieldnames, "caso_id_canonico", "caso_id")
    out_c = detect_col(r.fieldnames, "outcome", "cod_outcome")
    outcome_persist = {row[cid_c]: row.get(out_c, "") for row in r}

with open(TEXTOS, encoding="utf-8", newline="") as f:
    r = csv.DictReader(f)
    cid_t = detect_col(r.fieldnames, "caso_id_canonico", "caso_id")
    pe_c  = detect_col(r.fieldnames, "por_ello_text", "por_ello")
    co_c  = detect_col(r.fieldnames, "considerando_text", "considerando")
    textos = {row[cid_t]: (row.get(pe_c, ""), row.get(co_c, "")) for row in r}

ids = [c for c in outcome_persist if c in textos]
print("Casos con outcome + textos:", len(ids))

# ------------------------------------------------------- compute CUR (pre-fix)
cur = {c: P.classify_outcome(textos[c][0], textos[c][1]) for c in ids}

# fidelidad: classify_outcome(persistido) vs outcome persistido
mismatch = [c for c in ids if cur[c] != outcome_persist[c]]
print("\n[FIDELIDAD] classify_outcome(textos) != outcome persistido: {}/{}".format(len(mismatch), len(ids)))
if mismatch:
    from collections import Counter
    ej = Counter((outcome_persist[c], cur[c]) for c in mismatch)
    for (a, b), n in ej.most_common(8):
        print("   persistido={:>16}  recompute={:>16}  x{}".format(a, b, n))
    print("   (si esto es alto, la reproduccion no es fiel -> revisar antes de confiar en el A/B)")

# --------------------------------------------------------- aplicar FIX (patch)
_NODIC = r"(?![^.]{0,40}(?:dictamin|procurador))"
RE_INOF_FIX = re.compile(
    r"inoficioso" + _NODIC + r"\s+(?:emitir|expedirse|(?:un\s+)?pronunciamiento|pronunciarse)|"
    r"(?:deviene|torna\w*|result\w+)\s+(?:inoficioso" + _NODIC + r"|abstract\w+)|"
    r"declara\w*\s+abstract\w+\s+la\s+cuesti[oó]n", re.I)
RE_ALTO_FIX = re.compile(r"\binoficioso\b" + _NODIC + r"|\babstracto\b|\bse declara abstracta?\b", re.I)

# patch 1: RE_DISP_INOFICIOSO
assert hasattr(P, "RE_DISP_INOFICIOSO"), "parser no expone RE_DISP_INOFICIOSO"
P.RE_DISP_INOFICIOSO = RE_INOF_FIX

# patch 2: entrada alta de abstracto en OUTCOME_PATTERNS_DISPOSITIVO (bare inoficioso)
TARGET_ALTO = r"\binoficioso\b|\babstracto\b|\bse declara abstracta?\b"
pat_list = P.OUTCOME_PATTERNS_DISPOSITIVO
idx = [i for i, (lab, pat) in enumerate(pat_list) if pat.pattern == TARGET_ALTO]
assert len(idx) == 1, "esperaba 1 pattern alto de abstracto, encontre {} (cambio el codigo?)".format(len(idx))
pat_list[idx[0]] = (pat_list[idx[0]][0], RE_ALTO_FIX)

# ------------------------------------------------------- compute FIX (post)
fix = {c: P.classify_outcome(textos[c][0], textos[c][1]) for c in ids}

# ------------------------------------------------------------------- reporte
flips = [c for c in ids if cur[c] != fix[c]]
recup = [c for c in flips if cur[c] == "abstracto"]
regres = [c for c in flips if cur[c] != "abstracto"]     # no esperado
nuevos_abstr = [c for c in flips if fix[c] == "abstracto"]  # no esperado

def snip(c, n=120):
    return re.sub(r"\s+", " ", textos[c][0])[:n]

print("\n[A/B] flips cur!=fix: {}".format(len(flips)))
print("  recuperacion (abstracto -> otro): {}".format(len(recup)))
from collections import Counter
print("  destino de los recuperados:", dict(Counter(fix[c] for c in recup)))

print("\n--- RECUPERADOS (abstracto -> X) ---")
for c in sorted(recup):
    print("  {:14} abstracto -> {:14} | {}".format(c, fix[c], snip(c)))

if regres:
    print("\n!!! REGRESIONES (cur != abstracto y cambio) — REVISAR:")
    for c in sorted(regres):
        print("  {:14} {} -> {} | {}".format(c, cur[c], fix[c], snip(c)))
else:
    print("\n[OK] 0 regresiones (ningun no-abstracto cambio).")

if nuevos_abstr:
    print("\n!!! NUEVOS abstracto (no esperado):", nuevos_abstr)

print("\n--- CHECKS NOMINALES ---")
for c, esp_cur, esp_fix in [("334_p1272", "abstracto", "revoca"),
                            ("348_p1499", "abstracto", "abstracto")]:
    if c in cur:
        ok = "OK" if fix[c] == esp_fix else "<-- REVISAR"
        print("  {:14} cur={:12} fix={:12} (esperado fix={}) {}".format(c, cur[c], fix[c], esp_fix, ok))
    else:
        print("  {:14} NO esta en el corpus".format(c))

print("\nabstracto total: cur={}  fix={}  (delta {})".format(
    sum(v == "abstracto" for v in cur.values()),
    sum(v == "abstracto" for v in fix.values()),
    sum(v == "abstracto" for v in fix.values()) - sum(v == "abstracto" for v in cur.values())))
