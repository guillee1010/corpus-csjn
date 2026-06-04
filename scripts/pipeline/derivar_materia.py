#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derivar_materia.py — Frente B: deriva la variable `materia` del corpus CSJN.

Arquitectura (REE): NO muta csjn_casos.csv. Lee la tabla primaria read-only y
escribe un sidecar keyed por `caso_id_canonico`, igual patrón que
csjn_casos_votos / csjn_casos_zonas / csjn_casos_editorial. El analisis hace
left-join 1:1 por caso_id_canonico. Se re-corre y se refina por capa sin
reparsear ni ensuciar el golden de la tabla primaria.

Capas de extraccion (orden = limpieza de senal, ver DISENO_SCDB_corpus.md):
  - Capa 1 (ESTE MODULO): tribunal_origen -> fuero -> materia. Deterministica.
    Solo fuero nacional/federal ESPECIALIZADO, donde el tribunal == materia.
  - Capa 2 (pendiente, tras csjn_casos_textos): provincial + SIN_TRIBUNAL.
    El tribunal NO desambigua -> senal = normas citadas + partes.
  - Capa 3 (pendiente): originaria (art. 117). Regla propia.

Salida `materia_capa`:
  capa1 | pendiente_capa2 | pendiente_capa3 | sui_generis | residual | no_aplica

Hallazgos del PoC (H112) que el diseno fija:
  - tributario = 0 en capa 1: sube por la Camara Cont. Adm. Federal -> cae en
    contencioso_administrativo. tributario NO es derivable de tribunal_origen;
    es materia de capa 2 (norma: 11.683, Cod. Aduanero). Fuera del vocab capa 1.
  - sui generis (Jurado de Enjuiciamiento, Consejo de la Magistratura): no son
    un fuero. Se rutean a `sui_generis`, decision de taxonomia pendiente.
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path

__version__ = "1.0"  # H112: capa 1 (tribunal_origen -> fuero). Sidecar nuevo.

# --- Rutas canonicas (overridables por CLI) ---
DEFAULT_INPUT = Path("output/parser/csjn_casos.csv")
DEFAULT_OUTPUT = Path("output/parser/csjn_casos_materia.csv")

# Columnas requeridas en la tabla primaria (falla ruidoso si falta alguna).
REQUIRED_COLS = ("caso_id_canonico", "tribunal_origen", "tribunal_origen_status",
                 "tipo_entrada")

# Centinela del parser para "sin tribunal de origen detectable".
SENTINEL_SIN_TRIBUNAL = "SIN_TRIBUNAL_ORIGEN"

# --- Capa 1: reglas ordenadas (la primera que matchea gana) ---
# Solo fuero nacional/federal especializado. Patrones sobre nombre NORMALIZADO
# (sin acentos, minuscula, espacios colapsados).
REGLAS_CAPA1: list[tuple[str, list[str]]] = [
    ("laboral",                    [r"\bdel trabajo\b"]),
    ("previsional",                [r"seguridad social"]),
    ("contencioso_administrativo", [r"contencioso administrativo"]),
    ("penal",                      [r"casacion penal", r"criminal y correccional",
                                    r"penal economico", r"\ben lo penal\b",
                                    r"casacion en lo penal", r"oral en lo criminal",
                                    r"oral federal"]),
    ("tributario",                 [r"tribunal fiscal", r"fiscal de la nacion"]),
    ("civil_comercial",            [r"civil y comercial federal", r"\ben lo comercial\b",
                                    r"\ben lo civil\b", r"relaciones de consumo"]),
    ("electoral",                  [r"electoral"]),
]
_REGLAS = [(m, [re.compile(p) for p in pats]) for m, pats in REGLAS_CAPA1]

# Cuerpos sui generis: NO son un fuero (decision de taxonomia pendiente).
_RE_SUIGENERIS = re.compile(r"jurado de enjuiciamiento|consejo de la magistratura|"
                            r"tribunal de etica|tribunal de enjuiciamiento")

# Jurisdiccion general -> capa 2 (el tribunal no desambigua materia).
_RE_GENERAL = re.compile(
    r"suprema corte|corte suprema|superior tribunal|tribunal superior|"
    r"corte de justicia|tribunal de justicia|"
    r"camara federal|camara nacional de apelaciones|camara de apelaciones|"
    r"camara (en lo )?civil|camara del crimen|camara penal|camara contencioso|"
    r"juzgado|tribunal oral|jueza con funciones|juez ")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).lower().strip()


def clasificar(tribunal_origen: str, status: str, tipo_entrada: str
               ) -> tuple[str, str, str]:
    """Devuelve (materia, materia_capa, materia_fuente).

    `materia` queda vacia salvo en capa1 (la materia resuelta). El ruteo de las
    capas pendientes vive en `materia_capa`. `materia_fuente` registra la regla
    o el motivo (auditable, REE).
    """
    if tipo_entrada != "fallo":
        return ("", "no_aplica", f"tipo_entrada={tipo_entrada}")

    # Originaria (art. 117): no hay tribunal apelado. La materia la da la regla de
    # capa 3, NUNCA el tribunal_origen (que en originaria suele ser citado, no
    # apelado). Corta antes de capa 1 para que esta no reclame casos originaria.
    if status == "originaria":
        return ("", "pendiente_capa3", "originaria")

    to = (tribunal_origen or "").strip()
    n = _norm(to)

    if to == SENTINEL_SIN_TRIBUNAL or n == "":
        return ("", "pendiente_capa2", "sin_tribunal")

    for materia, pats in _REGLAS:
        for p in pats:
            if p.search(n):
                return (materia, "capa1", f"regla:{p.pattern}")

    if _RE_SUIGENERIS.search(n):
        return ("", "sui_generis", to[:80])

    if _RE_GENERAL.search(n):
        return ("", "pendiente_capa2", "jurisdiccion_general")

    return ("", "residual", to[:80])


def derivar(input_path: Path, output_path: Path) -> dict:
    if not input_path.exists():
        sys.exit(f"[FATAL] no existe el input: {input_path}")

    with input_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {input_path}: {faltan}")
        filas = list(reader)

    salida = []
    cobertura: dict[str, int] = {}
    materias: dict[str, int] = {}
    for r in filas:
        materia, capa, fuente = clasificar(
            r["tribunal_origen"], r["tribunal_origen_status"], r["tipo_entrada"])
        salida.append({
            "caso_id_canonico": r["caso_id_canonico"],
            "materia": materia,
            "materia_capa": capa,
            "materia_fuente": fuente,
        })
        cobertura[capa] = cobertura.get(capa, 0) + 1
        if capa == "capa1":
            materias[materia] = materias.get(materia, 0) + 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["caso_id_canonico", "materia", "materia_capa",
                            "materia_fuente"],
            lineterminator="\n")  # LF determinístico (consistente con parser H111)
        writer.writeheader()
        writer.writerows(salida)

    return {"n": len(salida), "cobertura": cobertura, "materias": materias}


def _reporte(stats: dict, fallos: int) -> None:
    print(f"\n  derivar_materia v{__version__}")
    print(f"  filas escritas: {stats['n']}  (fallos: {fallos})")
    print("\n  === cobertura (sobre fallos) ===")
    cov = stats["cobertura"]
    orden = ["capa1", "pendiente_capa2", "pendiente_capa3", "sui_generis",
             "residual", "no_aplica"]
    for k in orden:
        v = cov.get(k, 0)
        base = fallos if k != "no_aplica" else stats["n"]
        pct = f"({100*v/base:5.1f}%)" if base else ""
        print(f"    {k:18s} {v:5d}  {pct}")
    cap1 = cov.get("capa1", 0)
    print(f"\n  CAPA 1 deterministica: {cap1} / {fallos} = "
          f"{100*cap1/fallos:.1f}%" if fallos else "")
    print("\n  === materia capa 1 ===")
    for m, v in sorted(stats["materias"].items(), key=lambda kv: -kv[1]):
        print(f"    {m:30s} {v:5d}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deriva materia capa 1 (sidecar).")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                    help=f"tabla primaria (default: {DEFAULT_INPUT})")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                    help=f"sidecar de salida (default: {DEFAULT_OUTPUT})")
    args = ap.parse_args(argv)

    stats = derivar(args.input, args.output)
    fallos = stats["n"] - stats["cobertura"].get("no_aplica", 0)
    _reporte(stats, fallos)
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
