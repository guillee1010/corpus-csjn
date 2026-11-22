#!/usr/bin/env python3
"""actualizar_codebook.py — cifras del CODEBOOK recalculadas desde los CSV canónicos (H227).

Recalcula, desde output/parser/*.csv, las cifras que el CODEBOOK publica en forma tabular:
  (1) tabla de archivos de §2: filas y columnas de cada `csjn_casos*.csv`;
  (2) tablas de valores codificados de §8 (`| `valor` | N | …`), por la columna de su encabezado
      ("### `columna` (in `archivo.csv`)"); la sección de materia usa `materia_capa`;
  (3) cifras en línea del diccionario de variables (§3 a §7): "`valor` N" y "`valor` (N)" dentro de la
      descripción de una variable cuyo nombre es columna de algún CSV;
  (4) las líneas "Counts as of parser vX" y el pie "corpus-csjn parser vX", con la __version__ de parser.py.
No toca texto: definiciones, límites conocidos (§11), cifras de validación (§9) ni prosa con números. Lo que
no sabe recalcular lo deja como está; la revisión del texto es del operador.

Uso, desde la raíz del repo:
  python scripts/auxiliares/actualizar_codebook.py --check     # informa diferencias, exit 1 si hay (no escribe)
  python scripts/auxiliares/actualizar_codebook.py             # escribe y lista cada línea cambiada
  python scripts/auxiliares/actualizar_codebook.py --subir     # además sube la versión menor del CODEBOOK (3.1 -> 3.2)
Va en el cierre de todo ciclo que cambie outputs canónicos, DESPUÉS del regolden.
"""
__version__ = "0.1"  # H227: generaliza actualizar_codebook_v44.py (diagnóstico H227) con --check y --subir
import argparse, collections, csv, re, sys
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

RAIZ = Path(__file__).resolve().parents[2]
RE_SECCION = re.compile(r"###\s+`([\w]+)`(?:,\s*`[\w]+`)*\s*(?:\(in `([\w.]+)`\))?")
RE_FILA_ARCHIVO = re.compile(r"(\|\s*`(csjn_casos[\w]*\.csv)`\s*\|[^|]*\|\s*)([\d,]+)(\s*\|\s*)(\d+)(\s*\|.*)$")
RE_FILA_VALOR = re.compile(r"(\|\s*`([^`]*)`\s*\|\s*)([\d,]+)(\s*\|.*)$")
RE_FILA_NULO = re.compile(r"(\|\s*\*?\((?:null|empty)\)\*?\s*\|\s*)([\d,]+)(\s*\|.*)$")
RE_EN_LINEA = re.compile(r"`([^`]+)`(\s*\(?)(\d(?:[\d,]{0,5}\d)?)")
RE_VERSION_PARSER = re.compile(r"""^__version__\s*=\s*["']([^"']+)["']""", re.M)
COLUMNA_DE_SECCION = {"materia": "materia_capa"}   # la tabla de §8 de materia cuenta materia_capa


def fmt(n):
    return f"{n:,}"


def cargar(outputs):
    tablas = {}
    for p in sorted(outputs.glob("csjn_casos*.csv")):
        with p.open(encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            tablas[p.name] = (r.fieldnames, list(r))
    return tablas


def conteo(tablas, col, archivo=None):
    for nombre, (h, filas) in tablas.items():
        if (archivo is None or nombre == archivo) and col in h:
            return collections.Counter(f[col] for f in filas)
    return None


def actualizar(lineas, tablas, version_parser):
    cambios = []

    def poner(i, nueva):
        if lineas[i] != nueva:
            cambios.append((i + 1, lineas[i], nueva))
            lineas[i] = nueva

    inicio_8 = next((i for i, l in enumerate(lineas) if l.startswith("## 8.")), len(lineas))
    # (1) tabla de archivos
    for i, l in enumerate(lineas):
        m = RE_FILA_ARCHIVO.match(l)
        if m and m.group(2) in tablas:
            h, filas = tablas[m.group(2)]
            poner(i, m.group(1) + fmt(len(filas)) + m.group(4) + str(len(h)) + m.group(6))
    # (2) tablas de §8
    col = archivo = None
    for i in range(inicio_8, len(lineas)):
        l = lineas[i]
        if l.startswith("## ") and i > inicio_8:
            col = None
        m = RE_SECCION.match(l)
        if m:
            col, archivo = COLUMNA_DE_SECCION.get(m.group(1), m.group(1)), m.group(2)
            continue
        if not col:
            continue
        c = conteo(tablas, col, archivo)
        if c is None:
            continue
        m = RE_FILA_VALOR.match(l)
        if m and (m.group(2) in c or re.fullmatch(r"[a-z_]+", m.group(2))):
            poner(i, m.group(1) + fmt(c.get(m.group(2), 0)) + m.group(4))
            continue
        m = RE_FILA_NULO.match(l)
        if m:
            poner(i, m.group(1) + fmt(c.get("", 0)) + m.group(3))
    # (3) cifras en línea del diccionario
    for i in range(0, inicio_8):
        m = re.match(r"\|\s*`(\w+)`\s*\|", lineas[i])
        if not m:
            continue
        c = conteo(tablas, m.group(1))
        if c is None:
            continue
        poner(i, RE_EN_LINEA.sub(lambda mm: f"`{mm.group(1)}`{mm.group(2)}{fmt(c[mm.group(1)])}"
                                 if mm.group(1) in c else mm.group(0), lineas[i]))
    # (4) versión del parser
    for i, l in enumerate(lineas):
        nueva = re.sub(r"Counts as of parser v\d+(?:\.\d+)*", f"Counts as of parser v{version_parser}", l)
        nueva = re.sub(r"(corpus-csjn parser )v\d+(?:\.\d+)*", rf"\g<1>v{version_parser}", nueva)
        poner(i, nueva)
    return cambios


def subir_version(lineas):
    for i, l in enumerate(lineas):
        m = re.search(r"\*Codebook version: (\d+)\.(\d+)", l)
        if m:
            nueva = l.replace(m.group(0), f"*Codebook version: {m.group(1)}.{int(m.group(2)) + 1}")
            lineas[i] = nueva
            return f"{m.group(1)}.{m.group(2)} -> {m.group(1)}.{int(m.group(2)) + 1}"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--codebook", default=str(RAIZ / "CODEBOOK.md"))
    ap.add_argument("--outputs", default=str(RAIZ / "output" / "parser"))
    ap.add_argument("--parser", default=str(RAIZ / "scripts" / "pipeline" / "parser.py"))
    ap.add_argument("--check", action="store_true", help="no escribe; exit 1 si hay cifras que no coinciden")
    ap.add_argument("--subir", action="store_true", help="sube la versión menor del CODEBOOK si hubo cambios")
    a = ap.parse_args()

    cb = Path(a.codebook)
    texto = cb.read_text(encoding="utf-8")
    lineas = texto.split("\n")
    version_parser = RE_VERSION_PARSER.search(Path(a.parser).read_text(encoding="utf-8")).group(1)
    cambios = actualizar(lineas, cargar(Path(a.outputs)), version_parser)

    print(f"actualizar_codebook v{__version__} · parser v{version_parser} · {len(cambios)} línea(s) con cifras distintas")
    for n, viejo, nuevo in cambios:
        print(f"  L{n}\n    antes:  {viejo[:150]}\n    ahora:  {nuevo[:150]}")
    if a.check:
        print("[CHECK] " + ("CLEAN" if not cambios else "FAIL: el CODEBOOK no coincide con los outputs"))
        return 1 if cambios else 0
    if cambios:
        if a.subir:
            print("  versión del CODEBOOK:", subir_version(lineas) or "no encontrada")
        cb.write_text("\n".join(lineas), encoding="utf-8")
        print(f"Escrito {cb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
