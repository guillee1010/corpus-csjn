"""m67_mayoria_absoluta.py — tamaño del voto que encabeza frente a la mayoría absoluta del tribunal (M67, H221)

Lee output/parser/csjn_casos.csv (solo lectura; solo entradas tipo fallo) y clasifica cada fallo con la
MISMA función que secretarias_votacion.py (importada, no duplicada):
  unanime · cabeza_con_mayoria_abs · cabeza_sin_mayoria_abs (mayoría circunstancial) · sin_cabeza · sin_posiciones
Tribunal = jueces con posición en el fallo; mayoría absoluta = n//2 + 1; cabeza = firmas sin calificador.

Escribe estadisticas/resultados/m67_mayoria_absoluta.csv (una fila por fallo, para recomputar cualquier corte)
e imprime totales, por año (entre no unánimes) y por tamaño de tribunal.

Uso:
  python scripts/analisis/m67_mayoria_absoluta.py
"""
__version__ = "0.1"  # H221: reemplaza la medición ad hoc de H221 (298/5703)
import csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from secretarias_votacion import clasificar  # noqa: E402  (fuente única de la clasificación M67)

RAIZ = AQUI.parents[1]
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"
OUT = RAIZ / "estadisticas" / "resultados" / "m67_mayoria_absoluta.csv"

def main():
    filas = []
    for c in csv.DictReader(CASOS.open(encoding="utf-8", newline="")):
        if c.get("tipo_entrada") != "fallo": continue
        clase, n, cab, dis = clasificar(c.get("posiciones"))
        m = re.search(r"de\s+(\d{4})", c.get("date") or "")
        filas.append({"caso_id_canonico": c["caso_id_canonico"], "tomo": c["tomo"],
                      "anio": int(m.group(1)) if m else "", "merito": c.get("is_merit_decision") in ("1", "True", "true"),
                      "n_tribunal": n, "n_cabeza": cab, "n_disidencias": dis, "clase": clase})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)

    tot = Counter(f["clase"] for f in filas)
    mer = Counter(f["clase"] for f in filas if f["merito"])
    n = len(filas)
    print(f"m67_mayoria_absoluta v{__version__} · fallos tipo fallo {n}")
    for k, v in tot.most_common():
        print(f"  {k:24s} {v:5d} ({v * 100 / n:5.1f}%) · de mérito {mer[k]}")
    no_un = sum(v for k, v in tot.items() if k not in ("unanime", "sin_posiciones"))
    sin = tot["cabeza_sin_mayoria_abs"] + tot["sin_cabeza"]
    print(f"  sin mayoría absoluta entre no unánimes: {sin}/{no_un} ({sin * 100 / no_un:.1f}%)")

    print("\nPor año, no unánimes: con mayoría abs / sin mayoría abs / sin cabeza · % sin (tomos)")
    pa = defaultdict(Counter); tomos = defaultdict(set)
    for f in filas:
        pa[f["anio"]][f["clase"]] += 1; tomos[f["anio"]].add(f["tomo"])
    for y in sorted(k for k in pa if k):
        c = pa[y]; nu = c["cabeza_con_mayoria_abs"] + c["cabeza_sin_mayoria_abs"] + c["sin_cabeza"]
        if not nu: continue
        print(f"  {y}: {c['cabeza_con_mayoria_abs']:4d} / {c['cabeza_sin_mayoria_abs']:3d} / {c['sin_cabeza']:3d}"
              f" · {(c['cabeza_sin_mayoria_abs'] + c['sin_cabeza']) * 100 / nu:5.1f}% · {','.join(sorted(tomos[y]))}")

    print("\nPor tamaño de tribunal: fallos · % unánime · % sin mayoría absoluta (sobre todos)")
    pt = defaultdict(Counter)
    for f in filas: pt[f["n_tribunal"]][f["clase"]] += 1
    for t in sorted(pt):
        c = pt[t]; nt = sum(c.values())
        print(f"  {t:2d} (may.abs {t // 2 + 1}): {nt:5d} · {c['unanime'] * 100 / nt:5.1f} · {(c['cabeza_sin_mayoria_abs'] + c['sin_cabeza']) * 100 / nt:5.1f}")
    print(f"\nArchivo: {OUT.relative_to(RAIZ)}")

if __name__ == "__main__":
    main()
