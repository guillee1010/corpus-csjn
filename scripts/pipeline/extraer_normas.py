#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_normas.py — etapa canonica del pipeline (M59 paso 1, H209): sidecar
caso x norma citada x ambito — la norma citada como HECHO separado de su
interpretacion.

Promocion de la diagnostica v0.2 (H208, scripts/diagnostico/H208/). Emite
`output/parser/csjn_casos_normas.csv` keyed por `caso_id_canonico`, mismo
patron que los demas sidecars.

Schema (columna `tipo` desde v1 aunque por ahora solo emite 'ley'):
  caso_id_canonico, tipo, norma, ambito, n_menciones

CUATRO ambitos desde v1 (correccion del operador H208 post-cierre: extraer
TODO lo ya exportado en CSVs sellados, habilitar por unidad):
  - caratula      case_name_cuerpo + case_name_indice (csjn_casos.csv),
                  normalizados igual que la cascada de derivar_materia.
  - considerando  considerando_text (csjn_casos_textos.csv). UNICO ambito que
                  consume la cascada de materia en M59 paso 1 (candado
                  byte-identico de csjn_casos_materia.csv).
  - dispositivo   por_ello_text (csjn_casos_textos.csv). Extraido, INERTE
                  para la cascada ("art. 280" / "ley 48" viven ahi).
  - voto          texto_voto (csjn_casos_votos.csv), AGREGADO por caso
                  (n_menciones = suma sobre todos los votos del caso). La
                  granularidad por juez (dato de tesis: citacion normativa
                  por ministro) exige schema propio -> ampliacion futura,
                  NO se emite acota de contrabando.

Fuente unica de la extraccion:
  - RE_LEY vive ACA desde H209 (movida VERBATIM de derivar_materia v3.2
    L198, su unico consumidor historico): este script es el extractor
    canonico; derivar_materia v3.3 consume el sidecar y ya no la corre.
  - `_norm` se IMPORTA de derivar_materia (fuente unica de normalizacion:
    el contrato de los patrones y del sidecar es el mismo texto normalizado).

Alcance v1.0 (heredado v0.2, nota de legibilidad H208): RE_LEY = solo
"ley N" (decreto-ley entra DE REBOTE por substring sin \\b — explica el par
1285/58); decretos / resoluciones / acordadas = ampliacion futura CON
SUPERFICIE PROPIA (formato NNNN/AA colisiona con expedientes y fechas; la
columna `tipo` ya esta para recibirlos). Citas sin numero (Codigo Penal, CN
por articulo) = territorio del canal kw, NO de este sidecar.

Determinismo de salida: casos en el orden del CSV de entrada (espejo de los
demas sidecars) · ambitos en orden fijo (caratula, considerando, dispositivo,
voto) · normas ordenadas dentro de cada (caso, ambito) · lineterminator LF.

Uso (PowerShell, raiz del repo):
  $env:PYTHONUTF8=1
  python scripts\\pipeline\\extraer_normas.py
  python scripts\\pipeline\\extraer_normas.py --casos ... --textos ... `
      --votos ... --output ...
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

__version__ = "1.0"  # H209 (M59 paso 1): promocion de la diagnostica v0.2 (H208) a etapa canonica. CUATRO ambitos (caratula/considerando/dispositivo/voto), columna tipo desde v1 (solo 'ley'), RE_LEY movida VERBATIM de derivar_materia v3.2 L198 (unico consumidor historico), _norm importado de derivar_materia (fuente unica). Salida determinista LF. Solo `ambito=considerando` alimenta la cascada de materia en este paso (candado byte-identico, ver derivar_materia v3.3).

# textos.csv (considerando completo) y votos.csv (texto_voto) traen campos
# grandes: regla de proyecto — field_size_limit en TODO script que los lea.
csv.field_size_limit(10 ** 8)

SCRIPT_DIR = Path(__file__).resolve().parent           # .../scripts/pipeline
REPO_ROOT  = SCRIPT_DIR.parent.parent                  # raiz del repo

# _norm de derivar_materia = fuente unica de normalizacion (Gate 3). Direccion
# de import extraer_normas -> derivar_materia, sin ciclo: dm consume el CSV de
# este script, no su modulo. sys.path por si el cwd no es scripts/pipeline.
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from derivar_materia import _norm
except ImportError as e:
    sys.exit(f"[FATAL] no pude importar _norm de derivar_materia: {e}")

# Movida VERBATIM de derivar_materia v3.2 (L198) en H209 — leyes numeradas
# (24.241 / 11683); anclar por presencia. Duena nueva: esta etapa.
RE_LEY = re.compile(r"ley(?:es)?\s+(?:n[ºo]?\.?\s*)?(\d{1,3}(?:\.\d{3})+|\d{4,6})")

DEFAULT_CASOS  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_TEXTOS = REPO_ROOT / "output" / "parser" / "csjn_casos_textos.csv"
DEFAULT_VOTOS  = REPO_ROOT / "output" / "parser" / "csjn_casos_votos.csv"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "parser" / "csjn_casos_normas.csv"

# Columnas requeridas (falla ruidoso si falta alguna — patron derivar_materia).
REQUIRED_CASOS  = ("caso_id_canonico", "case_name_cuerpo", "case_name_indice")
REQUIRED_TEXTOS = ("caso_id_canonico", "considerando_text", "por_ello_text")
REQUIRED_VOTOS  = ("caso_id_canonico", "texto_voto")

FIELDNAMES = ["caso_id_canonico", "tipo", "norma", "ambito", "n_menciones"]
AMBITOS    = ("caratula", "considerando", "dispositivo", "voto")  # orden fijo


def extraer(texto_norm: str) -> Counter:
    """norma (sin puntos) -> n_menciones. Formula VERBATIM del canal norma
    historico de clasificar_capa2 (dedup por norma con puntos removidos)."""
    return Counter(m.replace(".", "") for m in RE_LEY.findall(texto_norm))


def _abrir_verificado(path: Path, requeridas: tuple[str, ...]) -> csv.DictReader:
    """DictReader con chequeo de existencia y columnas. El caller itera."""
    if not path.exists():
        sys.exit(f"[FATAL] no existe: {path}")
    fh = path.open(encoding="utf-8", newline="")
    rd = csv.DictReader(fh)
    faltan = [c for c in requeridas if c not in (rd.fieldnames or [])]
    if faltan:
        sys.exit(f"[FATAL] faltan columnas en {path}: {faltan}")
    return rd


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="M59 — sidecar caso x norma citada x ambito (etapa canonica).")
    ap.add_argument("--casos",  type=Path, default=DEFAULT_CASOS,
                    help=f"tabla primaria (default: {DEFAULT_CASOS})")
    ap.add_argument("--textos", type=Path, default=DEFAULT_TEXTOS,
                    help=f"sidecar de textos (default: {DEFAULT_TEXTOS})")
    ap.add_argument("--votos",  type=Path, default=DEFAULT_VOTOS,
                    help=f"sidecar de votos (default: {DEFAULT_VOTOS})")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                    help=f"sidecar de salida (default: {DEFAULT_OUTPUT})")
    args = ap.parse_args(argv)

    # -- casos: fija el ORDEN de emision + la caratula --------------------------
    casos: list[tuple[str, str]] = []          # (cid, caratula cruda)
    for r in _abrir_verificado(args.casos, REQUIRED_CASOS):
        casos.append((r["caso_id_canonico"],
                      f'{r.get("case_name_cuerpo", "")} {r.get("case_name_indice", "")}'))

    # -- textos: considerando + dispositivo por caso ----------------------------
    textos: dict[str, tuple[str, str]] = {}
    for r in _abrir_verificado(args.textos, REQUIRED_TEXTOS):
        textos[r["caso_id_canonico"]] = (r.get("considerando_text", ""),
                                         r.get("por_ello_text", ""))

    # -- votos: extraccion por fila, AGREGADA por caso (suma de menciones) ------
    votos_agg: dict[str, Counter] = {}
    n_filas_votos = 0
    for r in _abrir_verificado(args.votos, REQUIRED_VOTOS):
        n_filas_votos += 1
        cnt = extraer(_norm(r.get("texto_voto", "")))
        if cnt:
            cid = r["caso_id_canonico"]
            if cid in votos_agg:
                votos_agg[cid].update(cnt)
            else:
                votos_agg[cid] = cnt

    # -- emision determinista ----------------------------------------------------
    filas: list[dict] = []
    pares_por_ambito: Counter = Counter()
    normas_por_ambito: dict[str, set] = {a: set() for a in AMBITOS}
    casos_por_ambito: dict[str, set] = {a: set() for a in AMBITOS}
    por_caso_cons: dict[str, set] = {}
    por_caso_car: dict[str, set] = {}

    for cid, caratula in casos:
        cons, disp = textos.get(cid, ("", ""))
        fuentes = (("caratula",     extraer(_norm(caratula))),
                   ("considerando", extraer(_norm(cons))),
                   ("dispositivo",  extraer(_norm(disp))),
                   ("voto",         votos_agg.get(cid, Counter())))
        for ambito, cnt in fuentes:
            for norma, n in sorted(cnt.items()):
                filas.append({"caso_id_canonico": cid, "tipo": "ley",
                              "norma": norma, "ambito": ambito,
                              "n_menciones": n})
                pares_por_ambito[ambito] += 1
                normas_por_ambito[ambito].add(norma)
                casos_por_ambito[ambito].add(cid)
                if ambito == "considerando":
                    por_caso_cons.setdefault(cid, set()).add(norma)
                elif ambito == "caratula":
                    por_caso_car.setdefault(cid, set()).add(norma)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        wr.writeheader()
        wr.writerows(filas)

    # -- resumen (leccion REEL+L H208: los totales que responden la pregunta) ---
    normas_distintas = set().union(*normas_por_ambito.values()) \
        if any(normas_por_ambito.values()) else set()
    casos_con_norma = set().union(*casos_por_ambito.values()) \
        if any(casos_por_ambito.values()) else set()
    solo_car = {cid for cid, ns in por_caso_car.items()
                if not ns <= por_caso_cons.get(cid, set())}

    print(f"\n  extraer_normas v{__version__}")
    print(f"  filas (pares caso x norma x ambito): {len(filas)}")
    for a in AMBITOS:
        print(f"    {a:14s} pares {pares_por_ambito[a]:5d}   "
              f"normas {len(normas_por_ambito[a]):5d}   "
              f"casos {len(casos_por_ambito[a]):5d}")
    print(f"  NORMAS DISTINTAS en el corpus (todos los ambitos): {len(normas_distintas)}")
    print(f"  casos con >=1 norma citada (cualquier ambito): "
          f"{len(casos_con_norma)} / {len(casos)}")
    print(f"  gap caratula (norma en caratula NO citada en su considerando): "
          f"{len(solo_car)} casos")
    print(f"  filas de votos leidas: {n_filas_votos} "
          f"(casos con norma en algun voto: {len(votos_agg)})")
    print("  NOTA alcance: RE_LEY = solo 'ley N' (decreto-ley entra de rebote "
          "por substring; decretos/resoluciones/acordadas = superficie propia, "
          "columna tipo prevista).")
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
