"""H129 — Delta de filas en csjn_casos_votos entre golden (v19) y v20 (P).

check_regresion reportó: N FILAS golden=27639 nuevo=27632 (dif=-7).
P recolocó el dispositivo y eso recortó el corte de votos (inicio_votos_indiv)
en algunos casos. Este script localiza QUÉ casos cambiaron de cantidad de votos
y vuelca los votos de cada uno (golden vs nuevo) para auditar si lo que se cae
es espurio (artefacto del dispositivo mal ubicado) o son votos reales perdidos.

Read-only. No toca nada.
"""
import csv
from pathlib import Path
from collections import defaultdict

RAIZ   = Path(__file__).resolve().parents[3]          # .../corpus-csjn
GOLDEN = RAIZ / "scripts" / "tests" / "golden" / "csjn_casos_votos.csv"
NUEVO  = RAIZ / "output"  / "parser" / "csjn_casos_votos.csv"

def cargar(p):
    with p.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r), r.fieldnames

g_filas, g_fn = cargar(GOLDEN)
n_filas, n_fn = cargar(NUEVO)

print(f"golden: {len(g_filas)} filas | nuevo: {len(n_filas)} filas | "
      f"delta total: {len(n_filas) - len(g_filas):+d}")
print(f"fieldnames golden == nuevo: {g_fn == n_fn}")
if g_fn != n_fn:
    print("  golden:", g_fn)
    print("  nuevo :", n_fn)

def key_col(fn):
    for c in ("caso_id_canonico", "caso_id"):
        if c in fn:
            return c
    return fn[0]

kc = key_col(n_fn)
print(f"columna caso_id: {kc!r}\n")

def por_caso(filas):
    d = defaultdict(list)
    for row in filas:
        d[row[kc]].append(row)
    return d

g, n = por_caso(g_filas), por_caso(n_filas)
cambiados = []
for c in sorted(set(g) | set(n)):
    ng, nn = len(g.get(c, [])), len(n.get(c, []))
    if ng != nn:
        cambiados.append((c, ng, nn, nn - ng))

print(f"casos con delta de votos: {len(cambiados)}  "
      f"(suma delta = {sum(d for *_, d in cambiados):+d})\n")

cols = [c for c in ("posicion", "juez", "jueces", "tipo_voto", "tipo_voto_sep",
                    "outcome", "is_merit_decision", "wc_voto") if c in n_fn]

for c, ng, nn, d in cambiados:
    print(f"━━ {c}: {ng} → {nn}  (delta {d:+d})")
    for etiqueta, dic in (("GOLDEN", g), ("NUEVO ", n)):
        print(f"   {etiqueta}:")
        for row in dic.get(c, []):
            print("     " + " | ".join(f"{k}={row.get(k,'')!r}" for k in cols))
    print()
