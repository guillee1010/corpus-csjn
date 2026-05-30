#!/usr/bin/env python3
# scripts/diagnostico/extraer_caso.py  (herramienta estable, no ligada a sesion)
# -----------------------------------------------------------------------------
# Extrae el texto COMPLETO (considerando + por_ello) de un caso desde su .md de
# tomo, anclando en el prefijo del considerando que guarda el CSV canonico. Sirve
# para validar a mano hits cuya frase causal cae pasado el truncado a 2000 chars
# de csjn_casos.csv, SIN tener que abrir el .md entero (frugal en ventana: lee el
# archivo de disco e imprime solo el span del caso).
#
# DIAGNOSTICO, NO produccion: no toca outputs ni el parser; solo lee.
# Reusa _unhyphenate del parser (REE: no reimplementar) via import con fallback ast.
#
# Uso (local, pegando la salida) o desde la raiz del repo:
#     python scripts/diagnostico/extraer_caso.py 344_p1785
#     python scripts/diagnostico/extraer_caso.py 344_p1785 --md corpus/LibroVol344-2.md
#     python scripts/diagnostico/extraer_caso.py 341_p2027 --corpus-dir corpus
#     python scripts/diagnostico/extraer_caso.py 344_p1785 --out diagnostico/_extraidos/344_p1785.md
#
# Sin --md: escanea --corpus-dir buscando LibroVol{tomo}*.md y usa el volumen que
# contenga el ancla (no hace falta saber el numero de volumen). La raiz del repo
# se autodetecta por marcador, asi que el script funciona desde cualquier
# subdirectorio del repo sin tocar nada.
# -----------------------------------------------------------------------------

__version__ = "1.01"

import argparse
import ast
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10 ** 7)

def _find_root(start: Path) -> Path:
    """Sube desde la ubicacion del script hasta hallar la raiz del repo
    (marcador: scripts/pipeline/parser.py). Independiza al script de su
    profundidad: anda igual en scripts/diagnostico/, en una H0NN/, o donde sea.
    Fallback conservador si no se halla el marcador (entorno aislado)."""
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start.parents[1] if len(start.parents) >= 2 else start


ROOT = _find_root(Path(__file__).resolve().parent)
CSV_CANONICO = ROOT / "output" / "parser" / "csjn_casos.csv"
PIPELINE_DIR = ROOT / "scripts" / "pipeline"
CORPUS_DEFAULT = ROOT / "corpus"


def cargar_unhyphenate():
    """Prefiere importar de parser.py; si no se puede (p.ej. falta
    parser_editorial), extrae _unhyphenate via ast sin ejecutar el modulo."""
    if str(PIPELINE_DIR) not in sys.path:
        sys.path.insert(0, str(PIPELINE_DIR))
    try:
        import parser as _p  # noqa
        return _p._unhyphenate, "import"
    except Exception:
        src = (PIPELINE_DIR / "parser.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        ns = {"re": re}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_unhyphenate":
                exec(compile(ast.Module([node], []), "parser.py", "exec"), ns)
        return ns["_unhyphenate"], "ast"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caso_id", help="caso_id_canonico, p.ej. 344_p1785")
    ap.add_argument("--md", default="", help="ruta a un .md de tomo concreto")
    ap.add_argument("--corpus-dir", default=str(CORPUS_DEFAULT),
                    help="dir con LibroVol*.md (default: corpus/)")
    ap.add_argument("--csv", default=str(CSV_CANONICO))
    ap.add_argument("--cola", type=int, default=600,
                    help="chars extra a mostrar tras el por_ello (default 600)")
    ap.add_argument("--out", default="",
                    help="si se da, escribe un .md autocontenido en esa ruta "
                         "(crea el directorio si no existe) en vez de volcar a consola")
    args = ap.parse_args()

    unhyphenate, modo = cargar_unhyphenate()

    def norm(t):
        return re.sub(r"\s+", " ", unhyphenate(t or "")).strip()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"[FATAL] no encuentro {csv_path}")
    with open(csv_path, encoding="utf-8") as f:
        fila = next((x for x in csv.DictReader(f)
                     if x.get("caso_id_canonico") == args.caso_id
                     and x.get("tipo_entrada") == "fallo"), None)
    if fila is None:
        sys.exit(f"[FATAL] {args.caso_id} no esta en el CSV (o no es tipo fallo)")

    ancla = norm(fila["considerando_text"])[:80]
    pe = norm(fila["por_ello_text"])
    if len(ancla) < 20:
        sys.exit(f"[FATAL] ancla demasiado corta para {args.caso_id}: {ancla!r}")

    # --- resolver el .md ---
    candidatos = []
    if args.md:
        candidatos = [Path(args.md)]
    else:
        tomo = args.caso_id.split("_", 1)[0]
        cdir = Path(args.corpus_dir)
        if not cdir.is_dir():
            sys.exit(f"[FATAL] no existe corpus-dir {cdir}; pasa --md explicito")
        candidatos = sorted(cdir.glob(f"LibroVol{tomo}*.md")) + \
            sorted(cdir.glob(f"LibroVol{tomo}-*.md"))
        candidatos = list(dict.fromkeys(candidatos))   # dedup conservando orden
        if not candidatos:
            sys.exit(f"[FATAL] sin LibroVol{tomo}*.md en {cdir}; pasa --md explicito")

    encontrado = None
    md_norm = None
    for c in candidatos:
        if not c.exists():
            continue
        md_norm = norm(c.read_text(encoding="utf-8"))
        i = md_norm.find(ancla)
        if i != -1:
            encontrado = (c, i)
            break

    if encontrado is None:
        nombres = ", ".join(c.name for c in candidatos)
        sys.exit(f"[FATAL] ancla no hallada en: {nombres}\n  ancla={ancla!r}")

    md_file, start = encontrado

    # --- fin del span: posicion del por_ello en el .md (incluye dispositivo) ---
    end = None
    if pe:
        pe_anchor = pe[:50]
        j = md_norm.find(pe_anchor, start)
        if j != -1:
            end = j + len(pe) + args.cola
    if end is None:
        end = start + 6000
        fin_nota = "(por_ello no localizado; ventana fija 6000)"
    else:
        fin_nota = "(acotado al por_ello)"

    span = md_norm[start:end]

    trunc = "TRUNCADO" if len(fila["considerando_text"]) >= 2000 else "completo"
    print(f"extraer_caso.py v{__version__}  (_unhyphenate via {modo})")
    print(f"caso_id           : {fila['caso_id_canonico']}")
    print(f".md               : {md_file.name}  {fin_nota}")
    print(f"outcome           : {fila.get('outcome','')}")
    print(f"causa_inadmisibil.: {fila.get('causa_inadmisibilidad','')}")
    print(f"dictamen_presente : {fila.get('dictamen_presente','')}")
    print(f"considerando_csv  : {len(fila['considerando_text'])} chars ({trunc})")
    print(f"POR_ELLO          : {pe}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)   # crea la ruta si no existe
        md_text = (
            f"# {fila['caso_id_canonico']}\n\n"
            f"- outcome: {fila.get('outcome','')}\n"
            f"- causa_inadmisibilidad: {fila.get('causa_inadmisibilidad','')}\n"
            f"- dictamen_presente: {fila.get('dictamen_presente','')}\n"
            f"- fuente: {md_file.name}  {fin_nota}\n"
            f"- considerando_csv: {len(fila['considerando_text'])} chars ({trunc})\n\n"
            f"## POR_ELLO\n\n{pe}\n\n"
            f"## CONSIDERANDO (completo, extraido del .md)\n\n{span}\n"
        )
        out.write_text(md_text, encoding="utf-8", newline="\n")   # LF, estandar del repo
        print(f"[escrito] {out}  ({len(md_text)} chars)")
    else:
        print("=" * 78)
        print(span)


if __name__ == "__main__":
    main()
