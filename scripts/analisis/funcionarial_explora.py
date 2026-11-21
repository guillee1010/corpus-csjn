"""funcionarial_explora.py — exploración de la capa funcionarial de sjconsulta (M66, H221)

Solo lectura de los JSON que baja scripts/validacion/cruce_sjconsulta.py (sj_AAAAMM_v03.json, cache
local gitignoreado). No hace pedidos al sitio. No imprime nombres: solo códigos de usuario y cargos.
Un fallo = el primer sumario de cada id_fallo.

Uso:
  python scripts/analisis/funcionarial_explora.py [--cache DIR]   (default scripts/diagnostico/sjconsulta)
"""
__version__ = "0.1"  # H221
import argparse, json, glob, re, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

RAIZ = Path(__file__).resolve().parents[2]
_ap = argparse.ArgumentParser(description="exploración de la capa funcionarial (M66)")
_ap.add_argument("--cache", default=str(RAIZ / "scripts" / "diagnostico" / "sjconsulta"))
AQUI = Path(_ap.parse_args().cache)

def f_ddmmaaaa(s):
    try: return datetime.strptime(s, "%d/%m/%Y")
    except (TypeError, ValueError): return None

def f_num(n):  # 202003031124 -> datetime
    try: return datetime.strptime(str(n)[:8], "%Y%m%d")
    except (TypeError, ValueError): return None

def cod(u):
    if isinstance(u, dict): return u.get("codigo")
    return u

def prefijo(c):
    m = re.match(r"[A-Z]+", c or "")
    return m.group(0)[:3] if m else "?"

fallos = {}
for p in sorted(glob.glob(str(AQUI / "sj_*_v03.json"))):
    for r in json.load(open(p, encoding="utf-8")):
        fallos.setdefault(r["id_fallo"], r)
print(f"fallos con sumario (v0.3): {len(fallos)}\n")

por_anio = defaultdict(lambda: {"n": 0, "an": 0, "recibo": set(), "modif": set(), "voces": set(), "dias": [], "lag_an": []})
por_sec = defaultdict(lambda: {"n": 0, "recibo": Counter(), "dias": []})
roles = defaultdict(Counter)   # rol -> prefijo
cargos = Counter()

for r in fallos.values():
    ff = f_ddmmaaaa(r.get("fecha"))
    if not ff: continue
    a = por_anio[ff.year]; a["n"] += 1
    fu = r.get("funcionarial") or {}
    if r.get("an_presente"): a["an"] += 1
    rc = (fu.get("recibo") or {}).get("codigoUsuario")
    if rc: a["recibo"].add(rc); roles["recibo"][prefijo(rc)] += 1
    um = (fu.get("analisis") or {}).get("usuarioModificacion")
    if um:
        a["modif"].add(cod(um)); roles["modifica_analisis"][prefijo(cod(um))] += 1
        if isinstance(um, dict) and um.get("cargo"): cargos[um["cargo"]] += 1
    for v in fu.get("voces") or []:
        c = v.get("usuarioCreacion")
        if c: a["voces"].add(cod(c)); roles["carga_voces"][prefijo(cod(c))] += 1
    so = (fu.get("sumario") or {}).get("usuarioCreacionOld")
    if so: roles["crea_sumario"][prefijo(so)] += 1
    fe = f_ddmmaaaa(r.get("an_fecha_entrada"))
    if fe:
        d = (ff - fe).days; a["dias"].append(d)
        por_sec[r.get("an_secretaria") or "(sin dato)"]["dias"].append(d)
    fc = f_num((fu.get("analisis") or {}).get("fechaCreacion"))
    if fc: a["lag_an"].append((fc - ff).days)
    s = por_sec[r.get("an_secretaria") or "(sin dato)"]; s["n"] += 1
    if rc: s["recibo"][rc] += 1

def med(xs): return f"{statistics.median(xs):.0f}" if xs else "-"

print("A. Por año: fallos · con análisis · códigos distintos (registro de entrada / modifica análisis / carga voces)")
print("   · días registro de entrada → fallo (mediana) · días fallo → creación del análisis (mediana)")
for y in sorted(por_anio):
    a = por_anio[y]
    print(f"  {y}: {a['n']:4d} · {a['an']:4d} · {len(a['recibo']):3d} / {len(a['modif']):3d} / {len(a['voces']):3d}"
          f" · {med(a['dias']):>5} d · {med(a['lag_an']):>5} d")

print("\nB. Por secretaría (todos los años): fallos · códigos de registro distintos · los 3 más frecuentes (% de sus fallos) · días registro→fallo (mediana)")
for sec, s in sorted(por_sec.items(), key=lambda kv: -kv[1]["n"]):
    if s["n"] == 0: continue
    top = ", ".join(f"{c} {n * 100 / s['n']:.0f}%" for c, n in s["recibo"].most_common(3))
    print(f"  {sec[:45]:45s} {s['n']:4d} · {len(s['recibo']):3d} · {top} · {med(s['dias'])} d")

print("\nC. Prefijo de código por rol (oficina probable del usuario; hipótesis a verificar)")
for rol, c in roles.items():
    print(f"  {rol:18s} " + ", ".join(f"{p} {n}" for p, n in c.most_common(6)))

print("\nD. Cargos de quien modificó por última vez el análisis")
for cg, n in cargos.most_common(10):
    print(f"  {n:5d} · {cg}")

dias = [d for a in por_anio.values() for d in a["dias"]]
if dias:
    print(f"\nE. Control de lectura del campo 'fecha de entrada': días registro→fallo, total {len(dias)} fallos ·"
          f" negativos {sum(d < 0 for d in dias)} · 0-30 d {sum(0 <= d <= 30 for d in dias)} ·"
          f" 31-365 d {sum(30 < d <= 365 for d in dias)} · >365 d {sum(d > 365 for d in dias)}")
