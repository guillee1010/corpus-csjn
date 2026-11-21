"""kappa_sjconsulta.py — κ y acuerdo corpus × sjconsulta, reproducible desde el cache (M66, H221)

Hace auditable la validación externa de la variable de votos:
  1. Recalcula, desde los JSON del cache (sj_AAAAMM_v03.json) y output/parser/csjn_casos.csv, los
     pares juez×fallo con la MISMA lógica de cruce_sjconsulta.py (importa pos_sj, cat_corpus, norm;
     no la duplica). Excluye conjueces y fallos sin bloque de votos; compara la intersección de jueces.
  2. Acuerdo y κ de Cohen por año y total, con IC 95% por bootstrap por FALLO (las posiciones de un
     mismo fallo no son independientes). Seed fija.
  3. Manifiesto del cache: archivo, sha256, bytes, registros. Permite verificar que los números salen
     de esos archivos exactos sin publicar los datos (el cache trae la capa funcionarial).

No hace pedidos al sitio. Escribe en output/validacion/ (fuera del manifest del pipeline, allow-list):
  kappa_sjconsulta.csv · kappa_sjconsulta_matriz.csv · sjconsulta_manifest.csv  (agregados y hashes; sin datos personales)

Uso:
  python scripts/validacion/kappa_sjconsulta.py [--cache DIR] [--boot 2000] [--seed 42]
"""
__version__ = "0.1"  # H221
import argparse, csv, glob, hashlib, json, random, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import cruce_sjconsulta as cx  # noqa: E402  (fuente única de la equivalencia)

RAIZ = AQUI.parents[1]
OUT = RAIZ / "output" / "validacion"

def kappa(c):
    n = sum(c.values())
    if not n: return None, None
    cats = {a for a, _ in c} | {b for _, b in c}
    po = sum(v for (a, b), v in c.items() if a == b) / n
    fa = Counter(); fb = Counter()
    for (a, b), v in c.items(): fa[a] += v; fb[b] += v
    pe = sum(fa[k] * fb[k] for k in cats) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0

def boot(fallos, reps, rng):
    ks = []
    for _ in range(reps):
        c = Counter()
        for i in (rng.randrange(len(fallos)) for _ in range(len(fallos))):
            c.update(fallos[i])
        k = kappa(c)[1]
        if k is not None: ks.append(k)
    ks.sort()
    if not ks: return None, None
    return ks[int(0.025 * len(ks))], ks[min(len(ks) - 1, int(0.975 * len(ks)))]

def main():
    ap = argparse.ArgumentParser(description="κ corpus × sjconsulta (M66)")
    ap.add_argument("--cache", default=str(cx.CACHE_DEFAULT))
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    cache = Path(a.cache)
    archivos = sorted(glob.glob(str(cache / "sj_*_v03.json")))
    if not archivos: sys.exit(f"ERROR: no hay sj_*_v03.json en {cache}")

    # manifiesto
    man, regs = [], []
    for p in archivos:
        b = Path(p).read_bytes()
        rr = json.loads(b.decode("utf-8"))
        regs += rr
        man.append({"archivo": Path(p).name, "sha256": hashlib.sha256(b).hexdigest(),
                    "bytes": len(b), "registros": len(rr)})

    casos = list(csv.DictReader(cx.CASOS.open(encoding="utf-8", newline="")))
    idx = {tuple(map(int, c["caso_id_canonico"].split("_p"))): c for c in casos}
    pf = defaultdict(list)
    for r in regs: pf[r["id_fallo"]].append(r)

    por_anio = defaultdict(list)    # año -> [Counter por fallo]
    distintos = Counter(); excl_conj = Counter()
    for ss in pf.values():
        s = ss[0]
        c = idx.get((s["tomo"], s["pagina"])) if s.get("tomo") else None
        if not c or not s.get("an_votos"): continue
        try: y = datetime.strptime(s["fecha"], "%d/%m/%Y").year
        except (TypeError, ValueError): continue
        if any("CONJUE" in cx.norm(m) for v in s["an_votos"] for m in v["ministros"]):
            excl_conj[y] += 1; continue
        sj = cx.pos_sj(s["an_votos"])
        try: co_raw = json.loads(c["posiciones"] or "{}")
        except json.JSONDecodeError: co_raw = {}
        co = {cx.norm(k): cx.cat_corpus(v) for k, v in co_raw.items()}
        if set(sj) != set(co): distintos[y] += 1
        cel = Counter((sj[j], co[j]) for j in set(sj) & set(co))
        if cel: por_anio[y].append(cel)

    rng = random.Random(a.seed)
    filas, matriz = [], []
    print(f"kappa_sjconsulta v{__version__} · cruce v{cx.__version__} · {len(archivos)} archivos · boot {a.boot} · seed {a.seed}\n")
    print("  año  · fallos · posiciones · coinciden · acuerdo · κ      · IC95% (bootstrap por fallo) · conj. distintos · conjueces excl.")
    grupos = sorted(por_anio) + ["total"]
    for y in grupos:
        fl = [f for yy in por_anio for f in por_anio[yy]] if y == "total" else por_anio[y]
        tot = Counter()
        for f in fl: tot.update(f)
        po, k = kappa(tot)
        lo, hi = boot(fl, a.boot, rng) if fl else (None, None)
        n = sum(tot.values()); ok = sum(v for (p, q), v in tot.items() if p == q)
        dist = sum(distintos.values()) if y == "total" else distintos[y]
        conj = sum(excl_conj.values()) if y == "total" else excl_conj[y]
        filas.append({"anio": y, "fallos": len(fl), "posiciones": n, "coinciden": ok,
                      "acuerdo": round(po, 4) if po is not None else "", "kappa": round(k, 4) if k is not None else "",
                      "ic95_inf": round(lo, 4) if lo is not None else "", "ic95_sup": round(hi, 4) if hi is not None else "",
                      "conjuntos_distintos": dist, "conjueces_excluidos": conj})
        for (p, q), v in sorted(tot.items(), key=lambda kv: -kv[1]):
            matriz.append({"anio": y, "sj": p, "corpus": q, "n": v})
        f = filas[-1]
        print(f"  {str(y):5s}· {f['fallos']:6d} · {n:10d} · {ok:9d} · {f['acuerdo']!s:7} · {f['kappa']!s:6} · [{f['ic95_inf']}, {f['ic95_sup']}] · {dist:15d} · {conj}")

    OUT.mkdir(parents=True, exist_ok=True)
    def esc(nombre, rows, meta=None):
        with (OUT / nombre).open("w", encoding="utf-8", newline="") as fh:
            if meta: fh.write(f"# {meta}\n")
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    gen = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    meta = f"generado {gen} · kappa_sjconsulta v{__version__} · cruce_sjconsulta v{cx.__version__} · boot {a.boot} seed {a.seed}"
    esc("kappa_sjconsulta.csv", filas, meta)
    esc("kappa_sjconsulta_matriz.csv", matriz, meta)
    esc("sjconsulta_manifest.csv", man, f"generado {gen} · {len(archivos)} archivos de {cache.name}/ (datos locales, no versionados)")
    print(f"\nEscritos en {OUT}: kappa_sjconsulta.csv · kappa_sjconsulta_matriz.csv · sjconsulta_manifest.csv")

if __name__ == "__main__":
    main()
