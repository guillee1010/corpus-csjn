#!/usr/bin/env python3
# scripts/diagnostico/H099/escanear_sumario_con_link.py
# -----------------------------------------------------------------------------
# Diagnostico H099. Mide el agujero de cobertura detectado por M19: cuantas
# entradas tipo_entrada=sumario_con_link del golden contienen en realidad un
# FALLO (dispositivo) embebido, o sea fallos que el dataset no esta codificando.
# Solo lee; no toca produccion. Reusa _unhyphenate del parser (REE) para ver el
# texto como lo ve el parser; fallback a strip de soft-hyphen si no se importa.
#
# Uso (desde cualquier subdir del repo):
#   python scripts/diagnostico/H099/escanear_sumario_con_link.py
# -----------------------------------------------------------------------------

__version__ = "1.0"

import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10 ** 7)


def find_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return Path.cwd()


ROOT = find_root(Path(__file__).resolve().parent)
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))
try:
    from parser import _unhyphenate  # noqa
    _MODO = "parser._unhyphenate"
except Exception:
    def _unhyphenate(t):
        return (t or "").replace("\xad", "").replace("\u00ad", "")
    _MODO = "fallback (strip soft-hyphen)"

GOLDEN = ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS = ROOT / "corpus"

# Marcadores de dispositivo de fallo, sobre texto normalizado en minuscula.
# FUERTES: casi nunca aparecen en un sumario editorial puro.
FUERTES = ("autos y vistos", "por ello se resuelve", "por ello, se resuelve",
           "por ello se desestima", "por ello, se desestima")
# DEBILES: verbos dispositivos sueltos; pueden dar falso positivo en una
# parafrasis de sumario, por eso se reportan aparte para revision.
DEBILES = ("se resuelve", "se desestima la queja", "se declara mal concedido",
           "se confirma la sentencia", "se revoca la sentencia", "se hace lugar")


def norm(t):
    return re.sub(r"\s+", " ", _unhyphenate(t or "")).lower()


def main():
    if not GOLDEN.exists():
        sys.exit(f"[FATAL] no encuentro el golden: {GOLDEN}")
    rows = [r for r in csv.DictReader(open(GOLDEN, encoding="utf-8"))
            if r.get("tipo_entrada") == "sumario_con_link"]
    print(f"escanear_sumario_con_link.py v{__version__}  (unhyphenate via {_MODO})")
    print(f"sumario_con_link en el golden: {len(rows)}")

    fuerte, debil, sin_loc = [], [], 0
    for r in rows:
        sf = (r.get("source_file") or "").strip()
        li = (r.get("linea_inicio") or "").strip()
        lf = (r.get("linea_fin_real") or r.get("linea_fin") or "").strip()
        if not (sf and li and lf):
            sin_loc += 1
            continue
        md = CORPUS / sf
        if not md.exists():
            sin_loc += 1
            continue
        lines = md.read_text(encoding="utf-8").splitlines()
        blk = norm(" ".join(lines[int(li):int(lf) + 1]))
        cid = r.get("caso_id_canonico")
        n = int(lf) - int(li) + 1
        hits_f = [m for m in FUERTES if m in blk]
        hits_d = [m for m in DEBILES if m in blk]
        if hits_f:
            fuerte.append((cid, n, ";".join(hits_f + hits_d)))
        elif hits_d:
            debil.append((cid, n, ";".join(hits_d)))

    total_sosp = len(fuerte) + len(debil)
    print(f"con marcador FUERTE (casi seguro fallo): {len(fuerte)}")
    print(f"solo marcador DEBIL (revisar):           {len(debil)}")
    print(f"sospechosos totales:                     {total_sosp} / {len(rows)}"
          f"  ({100*total_sosp/max(len(rows),1):.1f}%)")
    print(f"sin localizacion / .md ausente:          {sin_loc}")

    out = ROOT / "scripts" / "diagnostico" / "H099" / "sumario_con_link_con_fallo.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["caso_id_canonico", "lineas", "fuerza", "marcadores"])
        for cid, n, h in sorted(fuerte):
            w.writerow([cid, n, "FUERTE", h])
        for cid, n, h in sorted(debil):
            w.writerow([cid, n, "DEBIL", h])
    print(f"[escrito] {out}  ({total_sosp} filas)")

    print("\nprimeros FUERTES:")
    for cid, n, h in sorted(fuerte)[:20]:
        print(f"   {cid:14s} {n:5d} ln  [{h}]")
    if len(fuerte) > 20:
        print(f"   ... (+{len(fuerte) - 20})")


if __name__ == "__main__":
    main()
