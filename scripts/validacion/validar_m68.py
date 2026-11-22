"""validar_m68.py — candado M68: header de voto/disidencia × `posiciones` (H226)

Invariante M68 (DEUDA ### M68, H222), evaluada sobre los canónicos publicados
en output/parser/csjn_casos.csv, solo lectura:

  (D) si n_disidencias > 0, al menos una posición de `posiciones` contiene
      "disidencia" ("en disidencia" o "en disidencia parcial");
  (V) si n_votos_svoto > 0, al menos una posición es "según su voto" o
      voting_pattern == "segun_su_voto".

Un fallo viola la invariante si falla (D) o (V). El script lista las
violaciones en output/validacion/m68_violaciones.csv (una fila por fallo, con
qué rama falla) y resume por tomo y por rama.

Uso como candado de ciclo:
  python scripts/validacion/validar_m68.py                 # informa, exit 1 si hay violaciones
  python scripts/validacion/validar_m68.py --baseline F    # exit 0 si el pool actual es
                                                           # subconjunto del CSV F (sin altas)
"""
__version__ = "0.1"  # H226: primera versión; reproduce en disco el pool 26 de la auditoría FABLE-01 (H222)
import argparse, csv, json, sys
from collections import Counter
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

RAIZ = Path(__file__).resolve().parents[2]
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"
OUT = RAIZ / "output" / "validacion" / "m68_violaciones.csv"


def evaluar(c):
    """Devuelve la lista de ramas violadas ("D", "V") para una fila de casos.csv."""
    try: pos = json.loads(c["posiciones"] or "{}")
    except json.JSONDecodeError: pos = {}
    vals = [str(v).lower() for v in pos.values()]
    nd = int(c["n_disidencias"] or 0)
    nv = int(c["n_votos_svoto"] or 0)
    ramas = []
    if nd > 0 and not any("disidencia" in v for v in vals):
        ramas.append("D")
    if nv > 0 and not (any(v == "según su voto" for v in vals)
                       or c["voting_pattern"] == "segun_su_voto"):
        ramas.append("V")
    return ramas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--casos", default=str(CASOS))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--baseline", default=None,
                    help="CSV de violaciones de un cierre anterior; PASS si no hay altas")
    args = ap.parse_args()

    casos = [c for c in csv.DictReader(Path(args.casos).open(encoding="utf-8", newline=""))
             if c.get("tipo_entrada") == "fallo"]
    filas = []
    for c in casos:
        ramas = evaluar(c)
        if not ramas: continue
        filas.append({"caso_id_canonico": c["caso_id_canonico"], "tomo": c["tomo"],
                      "rama": "+".join(ramas),
                      "n_disidencias": c["n_disidencias"], "n_votos_svoto": c["n_votos_svoto"],
                      "voting_pattern": c["voting_pattern"], "posiciones": c["posiciones"]})

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["caso_id_canonico", "tomo", "rama", "n_disidencias",
                                           "n_votos_svoto", "voting_pattern", "posiciones"])
        w.writeheader(); w.writerows(filas)

    ids = {f["caso_id_canonico"] for f in filas}
    print(f"validar_m68 v{__version__} · fallos {len(casos)} · violaciones {len(filas)}")
    pr = Counter(f["rama"] for f in filas)
    print("  por rama: " + " · ".join(f"{r} {pr[r]}" for r in sorted(pr)))
    pt = Counter(f["tomo"] for f in filas)
    print("  por tomo: " + " · ".join(f"{t} {pt[t]}" for t in sorted(pt)))
    print(f"  ids: {' '.join(sorted(ids))}")
    print(f"\nArchivo: {out.relative_to(RAIZ) if out.is_relative_to(RAIZ) else out}")

    if args.baseline:
        base = {r["caso_id_canonico"] for r in csv.DictReader(Path(args.baseline).open(encoding="utf-8", newline=""))}
        altas, bajas = sorted(ids - base), sorted(base - ids)
        print(f"\n[candado M68] baseline {len(base)} · actual {len(ids)} · altas {len(altas)} · bajas {len(bajas)}")
        if altas: print("  altas: " + " ".join(altas))
        if bajas: print("  bajas: " + " ".join(bajas))
        print("[candado M68] " + ("PASS" if not altas else "FAIL"))
        sys.exit(0 if not altas else 1)
    sys.exit(0 if not filas else 1)


if __name__ == "__main__":
    main()
