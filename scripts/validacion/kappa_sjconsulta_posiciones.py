"""kappa_sjconsulta_posiciones.py (H224, M66) — κ de posiciones corpus × SJ recomputado sobre el parser vigente, desde
posiciones_AAAA.csv del cache (bloque de votos de SJ por fallo, sin funcionarios). Reusa pos_sj, cat_corpus,
norm (cruce_sjconsulta) y kappa, boot (kappa_sjconsulta); no duplica lógica.
Brazo A = columna posiciones_corpus guardada en H221 (debe reproducir output/validacion/kappa_sjconsulta.csv).
Brazo B = posiciones de output/parser/csjn_casos.csv vigente.
Uso: python scripts/validacion/kappa_sjconsulta_posiciones.py [DIR_CACHE]   (default scripts/diagnostico/sjconsulta)
Escribe output/validacion/kappa_sjconsulta_posiciones.csv (brazo B por año y total) y
kappa_sjconsulta_posiciones_cambios.csv (posiciones que cambiaron entre el brazo A y el B, sin datos personales)."""
__version__ = "0.1"  # H224
import csv, glob, json, random, sys
from collections import Counter, defaultdict
from pathlib import Path
csv.field_size_limit(2**31 - 1)
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts/validacion"))
import cruce_sjconsulta as cx
from kappa_sjconsulta import kappa, boot
D = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "scripts/diagnostico/sjconsulta"
cur = {c["caso_id_canonico"]: c["posiciones"] for c in csv.DictReader((RAIZ / "output/parser/csjn_casos.csv").open(encoding="utf-8", newline=""))}
def votos(s):
    out = []
    for b in s.split(" ; "):
        t, _, m = b.partition(": ")
        out.append({"tipo": t, "ministros": [x.strip() for x in m.split(", ") if x.strip()]})
    return out
brazos = {"A": defaultdict(list), "B": defaultdict(list)}; dif = []
for p in sorted(glob.glob(str(D / "posiciones_*.csv"))):
    y = int(Path(p).stem.split("_")[1])
    for r in csv.DictReader(open(p, encoding="utf-8")):
        sj = cx.pos_sj(votos(r["sj_votos"]))
        for br, raw in (("A", r["posiciones_corpus"]), ("B", cur.get(r["caso_id_canonico"], "{}"))):
            co = {cx.norm(k): cx.cat_corpus(v) for k, v in json.loads(raw or "{}").items()}
            cel = Counter((sj[j], co[j]) for j in set(sj) & set(co))
            if cel: brazos[br][y].append(cel)
            if br == "B":
                for j in set(sj) & set(co):
                    coA = cx.cat_corpus(json.loads(r["posiciones_corpus"] or "{}").get(next((k for k in json.loads(r["posiciones_corpus"] or "{}") if cx.norm(k) == j), ""), "")) if r["posiciones_corpus"] else ""
                    if coA != co[j]: dif.append((r["caso_id_canonico"], j, sj[j], coA, co[j]))
for br in ("A", "B"):
    rng = random.Random(42); pa = brazos[br]
    fl = [f for y in pa for f in pa[y]]; tot = Counter()
    for f in fl: tot.update(f)
    po, k = kappa(tot); lo, hi = boot(fl, 2000, rng)
    n = sum(tot.values()); ok = sum(v for (a, b), v in tot.items() if a == b)
    print(f"brazo {br}: fallos {len(fl)} · posiciones {n} · coinciden {ok} · acuerdo {po:.4f} · κ {k:.4f} [{lo:.4f}; {hi:.4f}]")
    if br == "B":
        print("  desacuerdos SJ×corpus:", dict(Counter({kk: v for kk, v in tot.items() if kk[0] != kk[1]}).most_common(10)))
mv = Counter((a, b, c) for _, _, a, b, c in dif)
print(f"posiciones que cambiaron de A a B: {len(dif)} · (SJ, corpus_H221, corpus_v43.3):", dict(mv.most_common(12)))
mejora = sum(1 for _, _, s, a, b in dif if b == s and a != s); empeora = sum(1 for _, _, s, a, b in dif if a == s and b != s)
print(f"  pasan a coincidir con SJ {mejora} · dejan de coincidir {empeora}")
with open(RAIZ / "output/validacion/kappa_sjconsulta_posiciones_cambios.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh); w.writerow(["caso_id_canonico", "juez", "sj", "corpus_h221", "corpus_v433"]); w.writerows(dif)

rng = random.Random(42); filas = []
for y in sorted(brazos["B"]) + ["total"]:
    fl = [f for yy in brazos["B"] for f in brazos["B"][yy]] if y == "total" else brazos["B"][y]
    tot = Counter()
    for f in fl: tot.update(f)
    po, k = kappa(tot); lo, hi = boot(fl, 2000, rng)
    filas.append({"anio": y, "fallos": len(fl), "posiciones": sum(tot.values()), "coinciden": sum(v for (a, b), v in tot.items() if a == b),
                  "acuerdo": round(po, 4), "kappa": round(k, 4), "ic95_inf": round(lo, 4), "ic95_sup": round(hi, 4)})
with open(RAIZ / "output/validacion/kappa_sjconsulta_posiciones.csv", "w", encoding="utf-8", newline="") as fh:
    fh.write(f"# kappa_sjconsulta_posiciones v{__version__} · brazo B (posiciones del csjn_casos.csv vigente) · boot 2000 seed 42\n")
    w = csv.DictWriter(fh, fieldnames=list(filas[0]), lineterminator="\n"); w.writeheader(); w.writerows(filas)
print("Archivo: output/validacion/kappa_sjconsulta_posiciones.csv")
