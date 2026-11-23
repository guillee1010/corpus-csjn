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

Modo --por-juez (H229, exige parser >= 45.0, columna voto_firmantes): la misma
invariante leída fila por fila en csjn_casos_votos.csv. El rótulo con que
empieza `texto_voto` ("Voto…", "Disidencia…", "Disidencia parcial…"; RE_VOTO_HDR
y RE_DISID_HDR importadas de scripts/pipeline/parser.py) tiene que coincidir
con `posicion` de esa fila: voto → "según su voto", disidencia → "en
disidencia", disidencia parcial → "en disidencia parcial". Clases de violación:
`mayoria` (voto propio y posición mayoría), `parcial` (parcial contra no
parcial), `cruzada` (voto contra disidencia), `sin_rotulo`. No ve a los jueces
sin fila en votos.csv (fuera del panel publicado): eso lo cubre el modo por
fallo, y los dos candados se corren juntos.

  python scripts/validacion/validar_m68.py --por-juez                 # informa
  python scripts/validacion/validar_m68.py --por-juez --baseline F    # candado, clave (caso, juez)
"""
__version__ = "0.2"  # H229: modo --por-juez (header de cada juez × su posición, desde votos.csv de parser >= 45.0); línea de base 36 filas en 25 fallos (output/validacion/m68_por_juez_baseline.csv). El modo por fallo no cambia. // v0.1, H226: primera versión; reproduce en disco el pool 26 de la auditoría FABLE-01 (H222)
import argparse, csv, json, sys
from collections import Counter
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

RAIZ = Path(__file__).resolve().parents[2]
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"
OUT = RAIZ / "output" / "validacion" / "m68_violaciones.csv"
VOTOS = RAIZ / "output" / "parser" / "csjn_casos_votos.csv"
OUT_JUEZ = RAIZ / "output" / "validacion" / "m68_por_juez_violaciones.csv"
PIPELINE = RAIZ / "scripts" / "pipeline"
_ESPERADA = {"voto": "según su voto", "disidencia": "en disidencia",
             "disidencia parcial": "en disidencia parcial"}


def _regex_del_parser():
    """Fuente única: las regex de header son las del parser, no una copia."""
    if str(PIPELINE) not in sys.path:
        sys.path.insert(0, str(PIPELINE))
    import parser as _p
    assert Path(_p.__file__).resolve() == (PIPELINE / "parser.py").resolve(), _p.__file__
    return _p.RE_VOTO_HDR, _p.RE_DISID_HDR


def evaluar_fila_voto(r, re_voto, re_disid):
    """Para una fila de votos.csv con texto_voto: (rotulo, clase) si viola la
    invariante por juez, o None."""
    t = r["texto_voto"]
    if re_voto.match(t):
        rotulo = "voto"
    else:
        m = re_disid.match(t)
        if not m:
            return "(sin rótulo)", "sin_rotulo"
        rotulo = "disidencia parcial" if m.group(1) else "disidencia"
    pos = r["posicion"]
    if pos == _ESPERADA[rotulo]:
        return None
    if pos == "mayoria":
        return rotulo, "mayoria"
    if "disidencia" in pos and "disidencia" in rotulo:
        return rotulo, "parcial"
    return rotulo, "cruzada"


def main_por_juez(args):
    re_voto, re_disid = _regex_del_parser()
    votos_path = Path(args.votos)
    with votos_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        if "voto_firmantes" not in (rd.fieldnames or []):
            sys.exit(f"[FATAL] {votos_path} no trae voto_firmantes: el modo --por-juez exige parser >= 45.0")
        filas, n = [], 0
        for r in rd:
            if not r["texto_voto"]:
                continue
            n += 1
            v = evaluar_fila_voto(r, re_voto, re_disid)
            if v:
                filas.append({"caso_id_canonico": r["caso_id_canonico"], "juez": r["juez"],
                              "rotulo_header": v[0], "posicion": r["posicion"],
                              "clase": v[1], "voto_firmantes": r["voto_firmantes"]})
    filas.sort(key=lambda f: (f["caso_id_canonico"], f["juez"]))
    out = Path(args.out if args.out != str(OUT) else OUT_JUEZ)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["caso_id_canonico", "juez", "rotulo_header",
                                           "posicion", "clase", "voto_firmantes"])
        w.writeheader(); w.writerows(filas)
    ids = {(f["caso_id_canonico"], f["juez"]) for f in filas}
    pc = Counter(f["clase"] for f in filas)
    print(f"validar_m68 v{__version__} --por-juez · filas con texto_voto {n} · "
          f"violaciones {len(filas)} en {len({f['caso_id_canonico'] for f in filas})} fallos")
    print("  por clase: " + " · ".join(f"{c} {pc[c]}" for c in sorted(pc)))
    print(f"\nArchivo: {out.relative_to(RAIZ) if out.is_relative_to(RAIZ) else out}")
    if args.baseline:
        base = {(r["caso_id_canonico"], r["juez"])
                for r in csv.DictReader(Path(args.baseline).open(encoding="utf-8", newline=""))}
        altas, bajas = sorted(ids - base), sorted(base - ids)
        print(f"\n[candado M68 por juez] baseline {len(base)} · actual {len(ids)} · altas {len(altas)} · bajas {len(bajas)}")
        if altas: print("  altas: " + " ".join(f"{c}|{j}" for c, j in altas))
        if bajas: print("  bajas: " + " ".join(f"{c}|{j}" for c, j in bajas))
        print("[candado M68 por juez] " + ("PASS" if not altas else "FAIL"))
        sys.exit(0 if not altas else 1)
    sys.exit(0 if not filas else 1)


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
    ap.add_argument("--por-juez", action="store_true",
                    help="invariante por juez sobre votos.csv (parser >= 45.0)")
    ap.add_argument("--votos", default=str(VOTOS))
    args = ap.parse_args()
    if args.por_juez:
        return main_por_juez(args)

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
