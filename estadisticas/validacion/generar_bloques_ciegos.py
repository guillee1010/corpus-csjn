#!/usr/bin/env python3
# estadisticas/validacion/generar_bloques_ciegos.py
# -----------------------------------------------------------------------------
# Modulo de validacion (M19). Genera los bloques CIEGOS de un marco para
# codificacion manual en ventana fresca. DIAGNOSTICO, solo lee; no toca
# produccion. Etapa intermedia del flujo: muestrear_validacion -> (este) ->
# codificar -> analizar_validacion.
#
# Que hace:
#   1. Lee la clave de la muestra y toma los caso_id cuyo `marco` incluye la
#      letra pedida (default 'A').
#   2. Por cada caso, invoca scripts/diagnostico/extraer_caso.py --blind --out
#      (reusa el extractor canonico verbatim; REE: no reimplemento la extraccion).
#   3. Concatena los .md por caso en bundles de --batch-size, para subir pocos
#      archivos a la ventana fresca en vez de N sueltos.
#
# Por que la clave y no la planilla: la planilla ciega no trae la columna
# `marco`. Leer la clave SOLO para saber QUE casos entran en el marco no revela
# ninguna respuesta del parser (no se tocan los campos parser_*).
#
# Uso (desde cualquier subdir del repo; raiz autodetectada por marcador):
#   python estadisticas/validacion/generar_bloques_ciegos.py
#   python estadisticas/validacion/generar_bloques_ciegos.py --marco B --batch-size 50
# -----------------------------------------------------------------------------

__version__ = "1.0"

import argparse
import csv
import subprocess
import sys
from pathlib import Path


def find_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return Path.cwd()


ROOT = find_root(Path(__file__).resolve().parent)


def _resolver(ruta: str) -> Path:
    p = Path(ruta)
    return p if p.is_absolute() else (ROOT / p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clave",
                    default="estadisticas/validacion/ground_truth/muestra_clave_v18_15.csv",
                    help="CSV de la clave (solo se usa para filtrar por `marco`)")
    ap.add_argument("--marco", default="A",
                    help="letra de marco a generar (substring de la col `marco`)")
    ap.add_argument("--extractor", default="scripts/diagnostico/extraer_caso.py")
    ap.add_argument("--casos-dir", default="estadisticas/validacion/_blind/casos",
                    help="dir para los .md por caso")
    ap.add_argument("--bundles-dir", default="estadisticas/validacion/_blind/bundles",
                    help="dir para los bundles concatenados (lo que se sube)")
    ap.add_argument("--batch-size", type=int, default=40)
    args = ap.parse_args()

    clave = _resolver(args.clave)
    extractor = _resolver(args.extractor)
    casos_dir = _resolver(args.casos_dir)
    bundles_dir = _resolver(args.bundles_dir)

    if not clave.exists():
        sys.exit(f"[FATAL] no encuentro la clave: {clave}")
    if not extractor.exists():
        sys.exit(f"[FATAL] no encuentro el extractor: {extractor}")
    casos_dir.mkdir(parents=True, exist_ok=True)
    bundles_dir.mkdir(parents=True, exist_ok=True)

    with open(clave, encoding="utf-8") as f:
        ids = [r["caso_id_canonico"] for r in csv.DictReader(f)
               if args.marco in (r.get("marco") or "")]
    if not ids:
        sys.exit(f"[FATAL] no hay casos con marco que incluya {args.marco!r} en {clave.name}")

    print(f"generar_bloques_ciegos.py v{__version__}")
    print(f"raiz repo  : {ROOT}")
    print(f"marco {args.marco}    : {len(ids)} casos -> bundles de {args.batch_size}")
    print("-" * 60)

    ok, fallos = [], []
    for i, cid in enumerate(ids, 1):
        out_md = casos_dir / f"{cid}.md"
        r = subprocess.run(
            [sys.executable, str(extractor), cid, "--blind", "--out", str(out_md)],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and out_md.exists():
            ok.append(out_md)
        else:
            ultima = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
            fallos.append((cid, ultima[0]))
        if i % 25 == 0 or i == len(ids):
            print(f"  {i}/{len(ids)}  (ok={len(ok)}, fallos={len(fallos)})")

    n_bundles = 0
    for b, start in enumerate(range(0, len(ok), args.batch_size), 1):
        trozo = ok[start:start + args.batch_size]
        dst = bundles_dir / f"marco_{args.marco}_lote_{b:02d}.md"
        partes = [p.read_text(encoding="utf-8") for p in trozo]
        dst.write_text(
            f"<!-- M19 Marco {args.marco} | lote {b:02d} | {len(trozo)} casos | "
            f"CIEGO (sin respuestas del parser) -->\n\n"
            + ("\n\n---\n\n".join(partes)) + "\n",
            encoding="utf-8", newline="\n",
        )
        n_bundles += 1

    print("-" * 60)
    print(f"casos extraidos : {len(ok)}")
    print(f"bundles         : {n_bundles} en {bundles_dir}")
    if fallos:
        print(f"[WARN] {len(fallos)} casos no se pudieron extraer:")
        for cid, msg in fallos[:20]:
            print(f"   - {cid}: {msg}")
        if len(fallos) > 20:
            print(f"   ... (+{len(fallos) - 20})")
    print(f"\nSubi los bundles de {bundles_dir} + la planilla a una ventana fresca.")


if __name__ == "__main__":
    main()
