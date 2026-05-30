#!/usr/bin/env python3
# scripts/diagnostico/extraer_caso.py  (herramienta estable, no ligada a sesion)
# -----------------------------------------------------------------------------
# Extrae el bloque COMPLETO de un caso (caratula -> considerando -> por_ello)
# desde su .md de tomo, anclando en el source_file + rango de lineas que guarda
# el CSV canonico.
#
# v2.0 (H094): antes resolvia el .md por glob("LibroVol{tomo}*.md") + primer match
# del ancla de 80 chars. En tomos con volumenes solapados (338.1/338.2) o con
# fallos hermanos de considerando casi identico (los Mendoza de ejecucion), eso
# anclaba en el volumen equivocado y extraia OTRO caso, en silencio. Ahora usa la
# respuesta autoritativa del CSV (source_file, linea_inicio, linea_fin_real) y
# reproduce el bloque exacto que arma el parser reusando su propia funcion
# construir_bloque_desde_localizacion (REE: no reimplementar; mismo indexado
# 0-based, linea_fin_real inclusive, ver parser.py linea 3010).
#
# Sirve para validar a mano hits cuya frase causal cae pasado el truncado a 2000
# chars de csjn_casos.csv. DIAGNOSTICO, NO produccion: solo lee.
#
# Uso (desde cualquier subdirectorio del repo; raiz autodetectada por marcador):
#     python scripts/diagnostico/extraer_caso.py 338_p830
#     python scripts/diagnostico/extraer_caso.py 338_p830 --cola 40   # +40 lineas tras el fin real (espiar caso siguiente)
#     python scripts/diagnostico/extraer_caso.py 338_p830 --out diagnostico/_extraidos/338_p830.md
#     python scripts/diagnostico/extraer_caso.py 344_p1785 --md corpus/LibroVol344-2.md  # override manual (modo <=v1.01, anclaje por texto)
#
# Sin --md: resuelve el volumen por source_file del CSV y extrae por rango de
# lineas [linea_inicio, linea_fin_real]. Con --md: modo override por anclaje de
# texto. Fallback al modo viejo (glob+ancla) solo si la fila no trae
# source_file/lineas, con aviso explicito.
# -----------------------------------------------------------------------------

__version__ = "2.0"

import argparse
import ast
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10 ** 7)


def _find_root(start: Path) -> Path:
    """Sube desde la ubicacion del script hasta hallar la raiz del repo
    (marcador: scripts/pipeline/parser.py). Fallback conservador si no se halla."""
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start.parents[1] if len(start.parents) >= 2 else start


ROOT = _find_root(Path(__file__).resolve().parent)
CSV_CANONICO = ROOT / "output" / "parser" / "csjn_casos.csv"
PIPELINE_DIR = ROOT / "scripts" / "pipeline"
CORPUS_DEFAULT = ROOT / "corpus"


def cargar_parser_funcs():
    """Prefiere importar de parser.py; si no se puede (p.ej. falta parser_editorial),
    extrae solo las funciones necesarias via ast sin ejecutar el modulo entero.
    Devuelve (_unhyphenate, construir_bloque_desde_localizacion, modo)."""
    needed = ("_unhyphenate", "construir_bloque_desde_localizacion")
    if str(PIPELINE_DIR) not in sys.path:
        sys.path.insert(0, str(PIPELINE_DIR))
    try:
        import parser as _p  # noqa
        return _p._unhyphenate, _p.construir_bloque_desde_localizacion, "import"
    except Exception:
        src = (PIPELINE_DIR / "parser.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        ns = {"re": re}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in needed:
                exec(compile(ast.Module([node], []), "parser.py", "exec"), ns)
        return ns["_unhyphenate"], ns["construir_bloque_desde_localizacion"], "ast"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("caso_id", help="caso_id_canonico, p.ej. 338_p830")
    ap.add_argument("--md", default="",
                    help="override: ruta a un .md concreto (modo <=v1.01, anclaje por texto)")
    ap.add_argument("--corpus-dir", default=str(CORPUS_DEFAULT),
                    help="dir con LibroVol*.md (default: corpus/)")
    ap.add_argument("--csv", default=str(CSV_CANONICO))
    ap.add_argument("--cola", type=int, default=0,
                    help="lineas extra a mostrar tras linea_fin_real "
                         "(para espiar el caso siguiente; default 0)")
    ap.add_argument("--out", default="",
                    help="si se da, escribe un .md autocontenido en esa ruta "
                         "(crea el directorio si no existe) en vez de volcar a consola")
    args = ap.parse_args()

    unhyphenate, construir_bloque, modo_import = cargar_parser_funcs()

    def norm(t):
        return re.sub(r"\s+", " ", unhyphenate(t or "")).strip()

    # --- fila del CSV ---
    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"[FATAL] no encuentro {csv_path}")
    with open(csv_path, encoding="utf-8") as f:
        fila = next((x for x in csv.DictReader(f)
                     if x.get("caso_id_canonico") == args.caso_id
                     and x.get("tipo_entrada") == "fallo"), None)
    if fila is None:
        sys.exit(f"[FATAL] {args.caso_id} no esta en el CSV (o no es tipo fallo)")

    ancla = norm(fila.get("considerando_text", ""))[:80]
    pe = norm(fila.get("por_ello_text", ""))
    source_file = (fila.get("source_file") or "").strip()
    li_raw = (fila.get("linea_inicio") or "").strip()
    lfr_raw = (fila.get("linea_fin_real") or fila.get("linea_fin") or "").strip()

    cdir = Path(args.corpus_dir)
    metodo = md_file = span = None
    aviso = ""

    if args.md:
        # --- override: anclaje por texto en el .md dado (comportamiento <=v1.01) ---
        metodo = "override --md (anclaje por texto)"
        md_file = Path(args.md)
        if not md_file.exists():
            sys.exit(f"[FATAL] no existe --md {md_file}")
        if len(ancla) < 20:
            sys.exit(f"[FATAL] ancla demasiado corta para {args.caso_id}: {ancla!r}")
        md_norm = norm(md_file.read_text(encoding="utf-8"))
        i = md_norm.find(ancla)
        if i == -1:
            sys.exit(f"[FATAL] ancla no hallada en {md_file.name}\n  ancla={ancla!r}")
        end = None
        if pe:
            j = md_norm.find(pe[:50], i)
            if j != -1:
                end = j + len(pe) + 600
        end = end if end is not None else i + 6000
        span = md_norm[i:end]

    elif source_file and li_raw and lfr_raw:
        # --- canonico: source_file + rango de lineas == bloque del parser ---
        metodo = "source_file + rango de lineas (bloque del parser)"
        md_file = cdir / source_file
        if not md_file.exists():
            sys.exit(f"[FATAL] no existe el volumen indicado por el CSV: {md_file}\n"
                     f"  (source_file={source_file!r}); pasa --md explicito")
        lines = md_file.read_text(encoding="utf-8").splitlines()
        li, lfr = int(li_raw), int(lfr_raw)
        bloque = list(construir_bloque(lines, li, lfr))   # 0-indexed, lfr inclusive
        if not bloque:
            sys.exit(f"[FATAL] bloque vacio para [{li}, {lfr}] en {md_file.name}")
        if args.cola > 0:
            bloque += lines[lfr + 1: lfr + 1 + args.cola]
        span = norm(" ".join(bloque))
        # sanity: el ancla del considerando del CSV tiene que estar en el bloque
        if ancla and len(ancla) >= 20 and ancla not in span:
            aviso = ("[WARN] el ancla del considerando del CSV NO aparece en el bloque "
                     "extraido: posible drift CSV<->.md o linea_inicio/fin desfasados.")

    else:
        # --- fallback: fila sin source_file/lineas -> glob + ancla (modo viejo) ---
        metodo = "fallback glob+ancla (fila sin source_file/lineas)"
        aviso = ("[WARN] la fila no trae source_file/linea_inicio/linea_fin_real; "
                 "uso glob+ancla, que puede elegir el volumen equivocado.")
        if len(ancla) < 20:
            sys.exit(f"[FATAL] ancla demasiado corta para {args.caso_id}: {ancla!r}")
        if not cdir.is_dir():
            sys.exit(f"[FATAL] no existe corpus-dir {cdir}; pasa --md explicito")
        tomo = args.caso_id.split("_", 1)[0]
        cands = sorted(cdir.glob(f"LibroVol{tomo}*.md"))
        encontrado = None
        for c in cands:
            mn = norm(c.read_text(encoding="utf-8"))
            i = mn.find(ancla)
            if i != -1:
                end = None
                if pe:
                    j = mn.find(pe[:50], i)
                    if j != -1:
                        end = j + len(pe) + 600
                end = end if end is not None else i + 6000
                encontrado = (c, mn[i:end])
                break
        if encontrado is None:
            sys.exit(f"[FATAL] ancla no hallada por glob en {cdir}; pasa --md explicito")
        md_file, span = encontrado

    canon = metodo.startswith("source_file")
    trunc = "TRUNCADO" if len(fila.get("considerando_text", "")) >= 2000 else "completo"
    print(f"extraer_caso.py v{__version__}  (parser funcs via {modo_import})")
    print(f"caso_id           : {fila['caso_id_canonico']}")
    print(f"metodo            : {metodo}")
    print(f".md               : {md_file.name}")
    if canon:
        print(f"rango lineas      : [{li_raw}, {lfr_raw}]  (linea_fin={fila.get('linea_fin','')})")
        print(f"status_localizac. : {fila.get('status_localizacion','')}")
        print(f"status_fin        : {fila.get('status_fin','')}")
    print(f"outcome           : {fila.get('outcome','')}")
    print(f"causa_inadmisibil.: {fila.get('causa_inadmisibilidad','')}")
    print(f"dictamen_presente : {fila.get('dictamen_presente','')}")
    print(f"considerando_csv  : {len(fila.get('considerando_text',''))} chars ({trunc})")
    print(f"POR_ELLO          : {pe}")
    if aviso:
        print(aviso)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        meta_lineas = (
            f"- rango_lineas: [{li_raw}, {lfr_raw}] (linea_fin={fila.get('linea_fin','')})\n"
            f"- status_fin: {fila.get('status_fin','')}\n"
            if canon else ""
        )
        md_text = (
            f"# {fila['caso_id_canonico']}\n\n"
            f"- metodo: {metodo}\n"
            f"- fuente: {md_file.name}\n"
            f"{meta_lineas}"
            f"- outcome: {fila.get('outcome','')}\n"
            f"- causa_inadmisibilidad: {fila.get('causa_inadmisibilidad','')}\n"
            f"- dictamen_presente: {fila.get('dictamen_presente','')}\n"
            f"- considerando_csv: {len(fila.get('considerando_text',''))} chars ({trunc})\n"
            f"{('> ' + aviso + chr(10)) if aviso else ''}"
            f"\n## POR_ELLO\n\n{pe}\n\n"
            f"## BLOQUE (extraido del .md)\n\n{span}\n"
        )
        out.write_text(md_text, encoding="utf-8", newline="\n")   # LF, estandar del repo
        print(f"[escrito] {out}  ({len(md_text)} chars)")
    else:
        print("=" * 78)
        print(span)


if __name__ == "__main__":
    main()
