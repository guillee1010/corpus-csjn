"""H130 - A/B de outcome entre golden (v19) y nuevo (v20, regla P + RE_PERF v2).

Espejo de votos_delta_P.py pero sobre la columna `outcome` de csjn_casos.csv.
Reporta los flips por DIRECCION y separa:
  - RECUPERACIONES   otro/sin_dispositivo -> outcome real   (lo que P busca)
  - REAL -> REAL     re-clasificacion entre outcomes reales  (revisar a ojo)
  - REGRESIONES      outcome real -> otro/sin_dispositivo     (NO debe haber)

Read-only. Correr DESPUES de aplicar el patch v20 y re-correr el parser (output/
queda v20; golden/ sigue v19). Clave = caso_id_canonico.

Uso:
  python outcome_delta_P.py
"""
import csv
from pathlib import Path
from collections import Counter, defaultdict

csv.field_size_limit(2**31 - 1)

RAIZ   = Path(__file__).resolve().parents[3]
GOLDEN = RAIZ / "scripts" / "tests" / "golden" / "csjn_casos.csv"
NUEVO  = RAIZ / "output"  / "parser" / "csjn_casos.csv"

NO_REAL = {"otro", "sin_dispositivo", ""}


def idx(p):
    with p.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        k = next((c for c in ("caso_id_canonico", "caso_id") if c in r.fieldnames),
                 r.fieldnames[0])
        return {row[k]: row for row in r}, k


g, kc = idx(GOLDEN)
n, _  = idx(NUEVO)

flips = defaultdict(list)   # (old, new) -> [cid]
for cid, row in n.items():
    if cid not in g:
        continue
    go, no = g[cid].get("outcome", ""), row.get("outcome", "")
    if go != no:
        flips[(go, no)].append(cid)

recup, real_real, regres = [], [], []
for (go, no), ids in flips.items():
    if go in NO_REAL and no not in NO_REAL:
        recup.append((go, no, ids))
    elif go not in NO_REAL and no in NO_REAL:
        regres.append((go, no, ids))
    else:
        real_real.append((go, no, ids))

total = sum(len(v) for v in flips.values())
print(f"clave: {kc!r}  |  golden {len(g)}  nuevo {len(n)}")
print(f"flips de outcome: {total}")
print(f"  RECUPERACIONES (otro/vacio -> real): {sum(len(i) for *_, i in recup)}")
print(f"  REAL -> REAL (re-clasificacion)    : {sum(len(i) for *_, i in real_real)}")
print(f"  REGRESIONES (real -> otro/vacio)   : {sum(len(i) for *_, i in regres)}  <<< debe ser 0")

def dump(titulo, grupo, muestras=8):
    if not grupo:
        return
    print(f"\n=== {titulo} ===")
    for go, no, ids in sorted(grupo, key=lambda x: -len(x[2])):
        print(f"  {go!r} -> {no!r}: {len(ids)}   {', '.join(ids[:muestras])}"
              + (" ..." if len(ids) > muestras else ""))

dump("RECUPERACIONES", recup)
dump("REAL -> REAL", real_real)
dump("REGRESIONES (revisar TODAS)", regres, muestras=9999)
