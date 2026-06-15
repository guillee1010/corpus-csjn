"""H129 — Flips de es_queja entre golden (v19) y v20 (P).

es_queja es variable sustantiva de tesis (certiorari criollo). Al recolocar el
por_ello, P puede sacar falsos positivos: el por_ello mal ubicado arrastraba
"las quejas de las partes" (agravios) o "recurso de queja por casación denegada"
(la queja de la instancia inferior citada en el considerando), y eso disparaba
es_queja=1. Este script lista TODOS los flips (en cualquier dirección) con el
por_ello golden vs nuevo, para confirmar que son correcciones y no falsos
negativos (quejas reales que pierden el flag).

Read-only.
"""
import csv
from pathlib import Path
from collections import defaultdict

# csjn_casos_textos tiene campos > 131 KB (considerando_text). En Windows el long
# de C es de 32 bits, así que sys.maxsize desborda field_size_limit: usar 2**31-1.
csv.field_size_limit(2**31 - 1)

RAIZ    = Path(__file__).resolve().parents[3]
G_CASOS = RAIZ / "scripts" / "tests" / "golden" / "csjn_casos.csv"
N_CASOS = RAIZ / "output"  / "parser" / "csjn_casos.csv"
G_TEXT  = RAIZ / "scripts" / "tests" / "golden" / "csjn_casos_textos.csv"
N_TEXT  = RAIZ / "output"  / "parser" / "csjn_casos_textos.csv"

def idx(p):
    with p.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        k = next((c for c in ("caso_id_canonico", "caso_id") if c in r.fieldnames),
                 r.fieldnames[0])
        return {row[k]: row for row in r}, k

gc, kc = idx(G_CASOS)
nc, _  = idx(N_CASOS)
gt, _  = idx(G_TEXT)
nt, _  = idx(N_TEXT)

flips = defaultdict(list)
for cid, row in nc.items():
    if cid not in gc:
        continue
    gq, nq = gc[cid].get("es_queja", ""), row.get("es_queja", "")
    if gq != nq:
        flips[(gq, nq)].append(cid)

total = sum(len(v) for v in flips.values())
print(f"clave caso_id: {kc!r}")
print(f"total flips es_queja: {total}")
for (gq, nq), ids in sorted(flips.items()):
    print(f"\n=== es_queja {gq!r} -> {nq!r}: {len(ids)} ===")
    for cid in ids:
        gp = (gt.get(cid, {}).get("por_ello_text", "") or "")[:170]
        np_ = (nt.get(cid, {}).get("por_ello_text", "") or "")[:170]
        print(f"  {cid}\n    G: {gp!r}\n    N: {np_!r}")
