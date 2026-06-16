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

# v2.1 (H099): agrega --blind para codificacion ciega de M19. Suprime los campos
# que son la RESPUESTA del parser (outcome, causa_inadmisibilidad, dictamen_presente
# y el largo/trunc del considerando) tanto en consola como en --out. Deja caratula,
# POR_ELLO y el BLOQUE, que son texto fuente y el codificador necesita leer. Cambio
# aditivo: sin --blind el comportamiento es identico a v2.0.

# v2.2 (H135, B128): H113 movio considerando_text/por_ello_text de csjn_casos.csv
# al sidecar csjn_casos_textos.csv. Esta herramienta seguia leyendolos del canonico
# -> ancla y POR_ELLO vacios -> modos --md / fallback glob / --blind / sanity-check
# muertos, y el char-count reportaba 0. Fix: tras cargar la fila del canonico,
# mergear considerando_text/por_ello_text desde el sidecar por caso_id_canonico
# (mismo join que derivar_recursos.py en produccion). El char-count deja de usar
# el flag TRUNCADO@2000 (muerto post-H113: el sidecar guarda el considerando
# completo) y reporta largo + fuente honestos. La extraccion por rango de lineas
# sobre el .md ya funcionaba y no se toca. Nuevo flag --csv-textos (default al
# sidecar canonico). Cambio aditivo: si el canonico aun trajera las columnas, se
# respetan; si el sidecar falta, avisa y degrada en vez de fallar silencioso.

# v2.3 (H135): control del display del BLOQUE + cambio de default a CRUDO. El bloque
# se mostraba SIEMPRE normalizado (span = norm(" ".join(bloque))), mezclando DOS
# transformaciones: des-hifenado (_unhyphenate: pega cortes de palabra del OCR y
# soft-hyphens) y colapso de espacios (\s+ -> " ": aplana saltos de linea, espacios
# multiples, running-heads intercalados). Eso escondia los artefactos y no dejaba
# diagnosticar por que el CSV/sidecar corta o difiere de la fuente.
# DEFAULT = crudo (el .md tal cual, SIN ninguna normalizacion), a proposito: la
# herramienta de diagnostico debe ser INDEPENDIENTE del parser. El crudo es la
# referencia contra la cual se contrasta la salida del parser (CSV/sidecar); si la
# herramienta replicara la normalizacion del parser, heredaria sus mismos errores
# (truncado/corte/normalizacion) y veria lo mismo que el CSV -> cegaria el diagnostico.
# Por eso NO se reusa la norma del parser y NO se sube parser.py para copiarla.
# --norm / --deshifen / --colapso son conveniencias OPCIONALES (no una replica fiel
# del parser). El sanity-check del ancla corre siempre sobre el normalizado local total
# (no tira WARN falso). Crudo/perillas garantizados en modo canonico (rango de lineas);
# en --md/glob (anclaje por texto) el bloque sale normalizado y se avisa.

__version__ = "2.3"

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
CSV_TEXTOS = ROOT / "output" / "parser" / "csjn_casos_textos.csv"  # sidecar H113: considerando_text/por_ello_text
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
    ap.add_argument("--csv-textos", default=str(CSV_TEXTOS),
                    help="sidecar con considerando_text/por_ello_text "
                         "(default: output/parser/csjn_casos_textos.csv; H113)")
    ap.add_argument("--cola", type=int, default=0,
                    help="lineas extra a mostrar tras linea_fin_real "
                         "(para espiar el caso siguiente; default 0)")
    ap.add_argument("--norm", action="store_true",
                    help="muestra el BLOQUE normalizado (des-hifenado + espacios colapsados). "
                         "Atajo de --deshifen --colapso. Conveniencia de lectura, NO una "
                         "replica fiel del parser. (default = crudo: el .md tal cual.)")
    ap.add_argument("--deshifen", action="store_true",
                    help="perilla: des-hifena (pega los cortes de palabra del OCR y los "
                         "soft-hyphens) SIN colapsar los saltos de linea.")
    ap.add_argument("--colapso", action="store_true",
                    help="perilla: colapsa espacios multiples y saltos de linea a espacio "
                         "simple SIN des-hifenar.")
    ap.add_argument("--out", default="",
                    help="si se da, escribe un .md autocontenido en esa ruta "
                         "(crea el directorio si no existe) en vez de volcar a consola")
    ap.add_argument("--blind", action="store_true",
                    help="codificacion ciega (M19): omite outcome / causa_inadmisibilidad "
                         "/ dictamen_presente / largo del considerando, que son la "
                         "respuesta del parser. Deja caratula, POR_ELLO y el BLOQUE.")
    args = ap.parse_args()

    # Transformaciones del BLOQUE. DEFAULT = CRUDO (el .md tal cual): la herramienta saca
    # del .md para contrastar la fuente contra lo que el parser guardo en el CSV/sidecar.
    # --norm reproduce el procesado del parser; cada perilla aisla una transformacion.
    deshifen = args.deshifen or args.norm
    colapso = args.colapso or args.norm

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

    # --- B128 (H135): considerando_text/por_ello_text viven en el sidecar desde H113 ---
    # El canonico ya no los trae; sin este merge, ancla/pe quedan vacios y mueren los
    # modos --md / fallback glob / --blind / sanity-check. Join por caso_id_canonico,
    # mismo patron que derivar_recursos.py en produccion. Solo se completa lo que falte
    # (si el canonico volviera a traerlas, se respetan).
    aviso_textos = ""
    faltan = [c for c in ("considerando_text", "por_ello_text") if not fila.get(c)]
    if faltan:
        tpath = Path(args.csv_textos)
        if tpath.exists():
            with open(tpath, encoding="utf-8") as f:
                tfila = next((x for x in csv.DictReader(f)
                              if x.get("caso_id_canonico") == args.caso_id), None)
            if tfila is not None:
                for col in faltan:
                    if tfila.get(col) is not None:
                        fila[col] = tfila[col]
                aun_faltan = [c for c in faltan if not fila.get(c)]
                if aun_faltan:
                    aviso_textos = (f"[WARN] el sidecar {tpath.name} no trae {aun_faltan} "
                                    f"para {args.caso_id} (columnas ausentes o vacias).")
            else:
                aviso_textos = (f"[WARN] {args.caso_id} no esta en el sidecar {tpath.name}; "
                                f"ancla/POR_ELLO quedan vacios -> --md/--blind/sanity-check "
                                f"degradados (la extraccion por rango de lineas igual funciona).")
        else:
            aviso_textos = (f"[WARN] no encuentro el sidecar de textos {tpath}; "
                            f"considerando_text/por_ello_text quedan vacios -> "
                            f"--md/--blind/sanity-check degradados (el BLOQUE por rango "
                            f"de lineas igual funciona). Pasa --csv-textos si esta en otra ruta.")

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
        span_norm = norm(" ".join(bloque))   # normalizado total (deshifen + colapso): para el sanity-check
        # display segun perillas: cada transformacion se aplica por separado.
        if deshifen and colapso:
            span = span_norm
        else:
            txt = "\n".join(bloque)                       # base: lineas del .md preservadas
            if deshifen:
                txt = unhyphenate(txt)                     # pega cortes de palabra del OCR
            if colapso:
                txt = re.sub(r"\s+", " ", txt).strip()     # aplana espacios y saltos
            span = txt
        # sanity: el ancla del considerando (sidecar) tiene que estar en el bloque NORMALIZADO
        if ancla and len(ancla) >= 20 and ancla not in span_norm:
            aviso = ("[WARN] el ancla del considerando del sidecar NO aparece en el bloque "
                     "extraido: posible drift sidecar<->.md o linea_inicio/fin desfasados.")

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
    if (not deshifen or not colapso) and not canon:
        aviso = ((aviso + " ") if aviso else "") + (
            "[WARN] el crudo y las perillas solo se garantizan en modo canonico (rango de "
            "lineas); en anclaje por texto (--md/glob) el BLOQUE sale normalizado.")
    cons_len = len(fila.get("considerando_text", ""))
    # post-H113 el sidecar guarda el considerando COMPLETO -> el viejo flag TRUNCADO@2000
    # ya no aplica (un considerando largo legitimo lo disparaba en falso). Reportar fuente.
    cons_fuente = "sidecar, completo" if cons_len else "VACIO (sidecar no cargado)"
    print(f"extraer_caso.py v{__version__}  (parser funcs via {modo_import})")
    print(f"caso_id           : {fila['caso_id_canonico']}")
    print(f"metodo            : {metodo}")
    print(f".md               : {md_file.name}")
    if canon:
        print(f"rango lineas      : [{li_raw}, {lfr_raw}]  (linea_fin={fila.get('linea_fin','')})")
        print(f"status_localizac. : {fila.get('status_localizacion','')}")
        print(f"status_fin        : {fila.get('status_fin','')}")
    if not args.blind:
        print(f"outcome           : {fila.get('outcome','')}")
        print(f"causa_inadmisibil.: {fila.get('causa_inadmisibilidad','')}")
        print(f"dictamen_presente : {fila.get('dictamen_presente','')}")
        print(f"considerando      : {cons_len} chars ({cons_fuente})")
    print(f"POR_ELLO          : {pe}")
    if aviso_textos:
        print(aviso_textos)
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
        meta_respuesta = (
            f"- outcome: {fila.get('outcome','')}\n"
            f"- causa_inadmisibilidad: {fila.get('causa_inadmisibilidad','')}\n"
            f"- dictamen_presente: {fila.get('dictamen_presente','')}\n"
            f"- considerando: {cons_len} chars ({cons_fuente})\n"
            if not args.blind else ""
        )
        md_text = (
            f"# {fila['caso_id_canonico']}\n\n"
            f"- metodo: {metodo}\n"
            f"- fuente: {md_file.name}\n"
            f"{meta_lineas}"
            f"{meta_respuesta}"
            f"{('> ' + aviso_textos + chr(10)) if aviso_textos else ''}"
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
