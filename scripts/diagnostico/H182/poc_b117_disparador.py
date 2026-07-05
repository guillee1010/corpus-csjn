#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
poc_b117_disparador.py — Diagnóstico READ-ONLY del flip cuerpo->epilogo (B117).

Spec: constancia H179 de la entrada B117 (DEUDA_TECNICA). Para cada caso de la
selección (wc_epilogo>500, exportada del explorador), toma el PRIMER span
`epilogo` de csjn_casos_zonas.csv, lee la línea REAL del .md donde arranca y
la clasifica:
  - pie_genuino       -> RE_PIE_START de extraer_epilogos (gramática estricta,
                         fuente única, Gate 3) matchea: el span arranca en el
                         pie editorial real. Si wc igual es enorme, el problema
                         es la frontera INFERIOR (arrastre, familia B096).
  - recurso_narrativo -> la rama ^Recurso de RE_DATOS_PARTES disparó sobre una
                         línea argumental ("recurso extraordinario cuya...")
                         dejada a inicio de línea por el wrap del OCR
                         (mecanismo (b) de la constancia H179).
  - causa_dos_puntos  -> disparó la rama Causa\\s*: (familia H055/B-Causa).
  - rotulo_pie        -> disparó un rótulo del pie (Tribunal de origen /
                         Profesionales / Nombre del / Parte ...) sin la
                         gramática canónica de arranque.
  - sin_match         -> RE_DATOS_PARTES no matchea la línea (esperable solo
                         con desync parser/output, ver columna a0).

Además verifica el ENVENENAMIENTO del guard (mecanismo (a)): re-corre
`zonificar_bloque` de parser.py (import directo, cero lógica paralela) sobre el
bloque reconstruido VERBATIM como producción
(lines[linea_inicio : linea_fin_real + 1], 0-based sobre split("\\n"),
aritmética de construir_bloque_desde_localizacion + offset de extraer_epilogos)
y separa las anclas {firma_linea, voto_header, dispositivo} anteriores al span
en PRE-apertura-propia (satisfacen el guard desde el residuo/cola del caso
anterior) vs POST (firma/voto/dispositivo del caso propio ya pasados).

  guard_fuente: solo_pre_apertura -> mecanismo (a) puro (guard envenenado)
                propia            -> guard legítimo (flip tardío, p.ej. en votos)
                mixta             -> ambas
                ninguna           -> anomalía (el marker no debió disparar)

Columna a0: cross-check identidad — primer índice epilogo del zonificador vivo
== primer span de producción. Si da "desync", el parser en disco no es el que
selló zonas.csv y la fila NO se interpreta.

Uso (local, corpus en disco):
  python scripts\\diagnostico\\H182\\poc_b117_disparador.py --seleccion <csv del explorador>

Read-only: no escribe nada fuera de su propio output en scripts/diagnostico/H182/.
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

__version__ = "0.1"  # H182: diagnostico del disparador B117 sobre la seleccion wc_epilogo>500 (clase de la 1ra linea + fuente del guard + posicion del span vs apertura propia).

csv.field_size_limit(10 ** 7)

SCRIPT_DIR = Path(__file__).resolve().parent          # scripts/diagnostico/H182
REPO_ROOT  = SCRIPT_DIR.parent.parent.parent          # raíz del repo
PIPELINE   = REPO_ROOT / "scripts" / "pipeline"
sys.path.insert(0, str(PIPELINE))

from parser import zonificar_bloque, RE_DATOS_PARTES          # noqa: E402
from extraer_epilogos import RE_PIE_START                     # noqa: E402

DEFAULT_ZONAS  = REPO_ROOT / "output" / "parser" / "csjn_casos_zonas.csv"
DEFAULT_CASOS  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_CORPUS = REPO_ROOT / "corpus"
DEFAULT_OUT    = SCRIPT_DIR / "poc_b117_disparador_out.csv"

# Ramas de RE_DATOS_PARTES, en el MISMO orden y con el mismo re.I, solo para
# reportar CUAL alternativa disparó. No deciden pipeline: clasifican el reporte.
_RAMAS = [
    ("Recurso",              re.compile(r"^Recurso", re.I)),
    ("Nombre del",           re.compile(r"^Nombre del", re.I)),
    ("Tribunal de origen",   re.compile(r"^Tribunal de origen", re.I)),
    ("Tribunal que intervino", re.compile(r"^Tribunal que intervino", re.I)),
    ("Causa:",               re.compile(r"^Causa\s*:", re.I)),
    ("Profesionales",        re.compile(r"^Profesionales", re.I)),
    ("Parte actora",         re.compile(r"^Parte actora", re.I)),
    ("Parte demandada",      re.compile(r"^Parte demandada", re.I)),
]

_SATISFACEN_GUARD = ("firma_linea", "voto_header", "dispositivo")
_APERTURA_PROPIA  = ("sumario_header", "dictamen_inicio", "apertura",
                     "vistos", "considerando", "fecha")

OUT_COLS = ["caso_id_canonico", "source_file", "a0", "k0_rel", "k0_abs",
            "clase", "rama", "guard_fuente", "n_anclas_pre", "n_anclas_post",
            "k_propio_rel", "span_pre_apertura", "wc_primer_span", "n_spans", "wc_epilogo_total",
            "primera_linea", "k_post_rel", "clase_post", "rama_post",
            "guard_fuente_post", "primera_linea_post"]


def _rama(linea: str) -> str:
    for nombre, rx in _RAMAS:
        if rx.match(linea):
            return nombre
    return ""


def _clase(linea: str, rama: str) -> str:
    if RE_PIE_START.match(linea):
        return "pie_genuino"
    if rama == "Causa:":
        return "causa_dos_puntos"
    if rama == "Recurso":
        return "recurso_narrativo"
    if rama:
        return "rotulo_pie"
    return "sin_match"


def _leer_csv(path: Path, required: tuple) -> list[dict]:
    if not path.exists():
        sys.exit(f"[FATAL] no existe: {path}")
    with path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in required if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {path}: {faltan}")
        return list(rd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Diagnóstico del disparador B117.")
    ap.add_argument("--seleccion", type=Path, required=True,
                    help="CSV del explorador (wc_epilogo>500); usa caso_id_canonico")
    ap.add_argument("--zonas", type=Path, default=DEFAULT_ZONAS)
    ap.add_argument("--casos", type=Path, default=DEFAULT_CASOS)
    ap.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)

    ids = [r["caso_id_canonico"]
           for r in _leer_csv(args.seleccion, ("caso_id_canonico",))]
    idset = set(ids)
    print(f"  seleccion: {len(ids)} casos")

    casos = {r["caso_id_canonico"]: r
             for r in _leer_csv(args.casos, ("caso_id_canonico", "source_file",
                                             "linea_inicio", "linea_fin_real"))
             if r["caso_id_canonico"] in idset}

    spans = defaultdict(list)   # cid -> [(linea_ini_rel, linea_fin_rel, wc)]
    for r in _leer_csv(args.zonas, ("caso_id_canonico", "zona",
                                    "linea_ini", "linea_fin")):
        if r["zona"] == "epilogo" and r["caso_id_canonico"] in idset:
            spans[r["caso_id_canonico"]].append(
                (int(r["linea_ini"]), int(r["linea_fin"]),
                 int(r["wc"]) if r.get("wc") not in (None, "") else 0))

    cache: dict[str, list | None] = {}
    def get_lines(sf: str):
        if sf not in cache:
            p = args.corpus_dir / sf
            cache[sf] = (p.read_text(encoding="utf-8").split("\n")
                         if p.exists() else None)
        return cache[sf]

    filas, faltantes = [], []
    for cid in ids:
        meta = casos.get(cid)
        segs = sorted(spans.get(cid, []))
        if meta is None or not segs:
            faltantes.append(cid)
            continue
        lines = get_lines(meta["source_file"])
        if lines is None:
            faltantes.append(cid)
            continue
        li  = int(meta["linea_inicio"])
        lfr = int(meta["linea_fin_real"]) if meta["linea_fin_real"] else len(lines) - 1
        # bloque VERBATIM produccion: construir_bloque_desde_localizacion
        bloque = lines[max(0, li): min(len(lines) - 1, lfr) + 1]

        zonas_live, anclas = zonificar_bloque(bloque)
        k0 = segs[0][0]                                  # primer span (produccion)
        k0_live = next((k for k, z in enumerate(zonas_live) if z == "epilogo"), None)
        a0 = "ok" if k0_live == k0 else f"desync(live={k0_live})"

        primera = bloque[k0].strip() if 0 <= k0 < len(bloque) else ""
        rama = _rama(primera)
        clase = _clase(primera, rama)

        k_propio = next((pos for pos, t in sorted(anclas)
                         if t in _APERTURA_PROPIA), None)
        sat = [(pos, t) for pos, t in anclas
               if t in _SATISFACEN_GUARD and pos < k0]
        pre  = [a for a in sat if k_propio is None or a[0] < k_propio]
        post = [a for a in sat if k_propio is not None and a[0] >= k_propio]
        if pre and post:
            guard = "mixta"
        elif pre:
            guard = "solo_pre_apertura"
        elif post:
            guard = "propia"
        else:
            guard = "ninguna"

        # primer span a partir de la apertura propia: el flip que importa
        # para el mecanismo (b) en bloques fin_extendido (el 1er span global
        # puede ser pie/cola del caso ANTERIOR, ver smoke H182).
        k_post = next((s[0] for s in segs
                       if k_propio is None or s[0] >= k_propio), None)
        if k_post is not None and k_post != k0:
            lp = bloque[k_post].strip() if 0 <= k_post < len(bloque) else ""
            rp = _rama(lp)
            cp = _clase(lp, rp)
            satp = [(pos, t) for pos, t in anclas
                    if t in _SATISFACEN_GUARD and pos < k_post]
            prep  = [a for a in satp if k_propio is None or a[0] < k_propio]
            postp = [a for a in satp if k_propio is not None and a[0] >= k_propio]
            gp = ("mixta" if prep and postp else
                  "solo_pre_apertura" if prep else
                  "propia" if postp else "ninguna")
        elif k_post is not None:                      # k_post == k0
            lp, rp, cp, gp = primera, rama, clase, guard
        else:
            lp, rp, cp, gp = "", "", "", ""

        filas.append({
            "caso_id_canonico": cid, "source_file": meta["source_file"],
            "a0": a0, "k0_rel": k0, "k0_abs": li + k0,
            "clase": clase, "rama": rama, "guard_fuente": guard,
            "n_anclas_pre": len(pre), "n_anclas_post": len(post),
            "k_propio_rel": k_propio if k_propio is not None else "",
            "span_pre_apertura": int(k_propio is not None and k0 < k_propio),
            "wc_primer_span": segs[0][2], "n_spans": len(segs),
            "wc_epilogo_total": sum(s[2] for s in segs),
            "primera_linea": primera[:120],
            "k_post_rel": k_post if k_post is not None else "",
            "clase_post": cp, "rama_post": rp, "guard_fuente_post": gp,
            "primera_linea_post": lp[:120],
        })

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)

    # ── resumen ──────────────────────────────────────────────────────────
    print(f"\n  poc_b117_disparador v{__version__} — {len(filas)} casos procesados"
          f" / {len(faltantes)} faltantes")
    if faltantes:
        print(f"  [WARN] sin meta/span/archivo: {faltantes[:10]}"
              f"{' ...' if len(faltantes) > 10 else ''}")
    desync = [f for f in filas if f["a0"] != "ok"]
    print(f"  A0 identidad zonificador vivo == zonas.csv: "
          f"{len(filas) - len(desync)} ok / {len(desync)} desync")
    if desync:
        print("  [WARN] desync (NO interpretar esas filas): "
              + ", ".join(f['caso_id_canonico'] for f in desync[:10]))

    print("\n  clase x guard_fuente (solo filas a0=ok):")
    tab = Counter((f["clase"], f["guard_fuente"]) for f in filas if f["a0"] == "ok")
    clases  = sorted({c for c, _ in tab})
    fuentes = sorted({g for _, g in tab})
    ancho = max((len(c) for c in clases), default=10) + 2
    print("  " + " " * ancho + "".join(f"{g:>20}" for g in fuentes) + f"{'total':>10}")
    for c in clases:
        tot = sum(tab[(c, g)] for g in fuentes)
        print("  " + c.ljust(ancho)
              + "".join(f"{tab[(c, g)]:>20}" for g in fuentes) + f"{tot:>10}")

    print("\n  clase_post x guard_fuente_post (1er span DENTRO del caso propio,\n"
          "  filas a0=ok con span propio):")
    tab2 = Counter((f["clase_post"], f["guard_fuente_post"])
                   for f in filas if f["a0"] == "ok" and f["clase_post"])
    clases2  = sorted({c for c, _ in tab2})
    fuentes2 = sorted({g for _, g in tab2})
    ancho2 = max((len(c) for c in clases2), default=10) + 2
    print("  " + " " * ancho2 + "".join(f"{g:>20}" for g in fuentes2) + f"{'total':>10}")
    for c in clases2:
        tot2 = sum(tab2[(c, g)] for g in fuentes2)
        print("  " + c.ljust(ancho2)
              + "".join(f"{tab2[(c, g)]:>20}" for g in fuentes2) + f"{tot2:>10}")

    npre = sum(1 for f in filas if f["a0"] == "ok" and f["span_pre_apertura"])
    print(f"\n  primer span ANTES de la apertura propia (= material del caso\n"
          f"  anterior absorbido, no flip en cuerpo propio): {npre}")

    print("\n  wc del primer span vs total (mediana, filas ok):")
    oks = [f for f in filas if f["a0"] == "ok"]
    if oks:
        ratios = sorted(f["wc_primer_span"] / f["wc_epilogo_total"]
                        for f in oks if f["wc_epilogo_total"])
        med = ratios[len(ratios) // 2] if ratios else 0
        print(f"    primer span explica mediana {med:.0%} del wc_epilogo")

    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
