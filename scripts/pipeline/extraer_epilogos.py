#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_epilogos.py — Vuelca el texto CRUDO de la zona `epilogo` de cada fallo a
un sidecar (insumo de la capa de partes, M29).

Arquitectura (REE): determinístico, NO muta nada, y **emite el universo COMPLETO
de fallos** (1:1 con casos.csv, tipo_entrada=fallo) — NO solo los que tienen
zona epilogo. Los fallos sin epílogo se emiten con `epilogo_status` explícito
(`sin_zona` / `archivo_no_encontrado`), nunca se omiten en silencio: así la
ausencia es AUDITABLE (¿el fallo no tiene epílogo, o el detector de zonas no se
lo marcó?), no una muerte silenciosa.

Lee los spans `epilogo` de csjn_casos_zonas.csv (líneas RELATIVAS al caso:
offset = linea_inicio del caso, verbatim del flujo H055) y el corpus crudo.
Mismo patrón sidecar que csjn_casos_textos.csv. El derivador de partes lee ESTE
csv, NO el .md → reproducible para Dataverse.

Se guarda el texto CRUDO (con saltos de línea): los marcadores del epílogo
(`Recurso ... interpuesto por`, `Tribunal de origen:`) están anclados a inicio
de línea. El parseo vive en `derivar_partes.py`.

H161 (v0.3) — DOS edits ortogonales, ambos sobre el texto que se vuelca:
  (1) FALLBACK `sin_zona` para cierres `fin_por_firma_actual`: el pie editorial
      va DESPUÉS de la firma → cae fuera de [linea_inicio, linea_fin] y el
      zonificador no lo marca (100/113 de esos cierres caen sin_zona). Se escanea
      el pie entre la firma (~linea_fin_real) y el caso siguiente. Validado
      end-to-end (H161) contra los 30 huérfanos de mérito: 27 recuperan
      recurrente vía derivar_partes (2 negativos correctos: sin pie / Eje-A
      originaria; 1 bloqueado por el gap de gramática `por:` en derivar_partes).
  (2) DESHIFENIZACIÓN soft-hyphen (deuda #3): migrada desde el STOPGAP de
      derivar_partes._deshifenar. Soft-only (U+00AD), NO el guión regular
      separador de entidad. Idempotente con el deriver (que queda de defensa).

NOTA offset: replica el cálculo de H055 (`linea_ini + linea_inicio`, 0-based
sobre `.split("\\n")`). El fallback usa líneas ABSOLUTAS (linea_fin_real /
linea_inicio del caso siguiente, ya absolutas en casos.csv).
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

__version__ = "0.3"  # H161: (1) fallback sin_zona para fin_por_firma_actual (pie tras firma, escaneo firma->caso siguiente con guard al footer; +27 huérfanos de mérito recuperan recurrente, validado end-to-end vs 30 ventanas). (2) deshifenización soft-hyphen migrada de derivar_partes (deuda #3), idempotente. Output csjn_casos_epilogo.csv CAMBIA (sin_zona->ok via firma + soft-hyphen unidos); re-correr derivar_partes y re-sellar manifest. Status nuevo auditable: "ok" con n_seg=0 = recuperado por fallback de firma. // 0.2 H154: emite los 5697 fallos con epilogo_status (no solo los 4345 con zona). // 0.1: solo casos con zona (muerte silenciosa de los sin-epilogo) -- corregido.

csv.field_size_limit(10 ** 7)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent.parent
DEFAULT_ZONAS  = REPO_ROOT / "output" / "parser" / "csjn_casos_zonas.csv"
DEFAULT_CASOS  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_CORPUS = REPO_ROOT / "corpus"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "parser" / "csjn_casos_epilogo.csv"

REQUIRED_ZONAS = ("caso_id_canonico", "zona", "linea_ini", "linea_fin")
REQUIRED_CASOS = ("caso_id_canonico", "tomo", "source_file", "linea_inicio",
                  "tipo_entrada")
# columnas SOFT del fallback sin_zona: si faltan, el fallback se deshabilita
# (degrada, no rompe).
SOFT_CASOS = ("status_fin", "linea_fin_real")

OUT_COLS = ["caso_id_canonico", "tomo", "source_file", "epilogo_status",
            "n_seg", "wc", "epilogo_text"]

# ── Fallback sin_zona (pie editorial tras la firma) ──────────────────────────
# Arranque del pie: marcador editorial anclado a línea. Incluye "por:" (dos
# puntos, formato viejo) y los rótulos Eje-A/viejo para volcar el pie completo;
# derivar_partes decide qué mapea a recurrente (Eje-A originaria NO mapea).
RE_PIE_START = re.compile(
    r"^(?:Recursos?|Queja)\b[^\n]*?(?:interpuest\w+|deducid\w+)\s+por[:\s]"
    r"|^Nombre\s+del\s+recurrente\s*:"
    r"|^Parte\s+(?:actora|demandada)\s*:"
    r"|^Nombre\s+de\s+(?:la|el)\s+(?:actora?|demandad[oa])\s*:", re.I)
# líneas que pertenecen al cuerpo/footer del pie editorial.
RE_PIE_LINE = re.compile(
    r"^(?:Recursos?|Queja|Traslados?|Tribunales?|Norma|Profesional\w*|"
    r"Parte\s|Nombre\s|Tercero\b)", re.I)
# artefactos de página (no rompen el pie, no son contenido): se saltan.
RE_PAGE = re.compile(
    r"^\s*$|^\d{1,4}\s*$|^DE\s+JUSTICIA\s+DE\s+LA\s+NACI|^FALLOS\s+DE\s+LA\s+CORTE",
    re.I)
RE_FOOTER = re.compile(r"^(?:Tribunales?|Profesional)", re.I)
# cola de línea que indica continuación (el pie venía partido).
_CONT_TAIL = re.compile(r"\b(?:por|del|de|la|el|y|con|en|representad\w*)$", re.I)


def _deshifenar(t: str) -> str:
    """Capa 0 (deuda #3, migrada de derivar_partes): une palabras partidas por
    soft-hyphen (U+00AD) a fin de línea. SOFT-ONLY: NO toca el guión REGULAR
    separador de entidad ('Estado Nacional- Ministerio' se preserva). NO colapsa
    saltos estructurales (los marcadores anclan por línea, re.M). Idempotente con
    el _deshifenar de derivar_partes, que queda como defensa."""
    return re.sub(r"(\w)\u00ad\s*\n\s*(\w)", r"\1\2", t)


def _pie_desde_firma(lines: list[str], lfr: int, hi: int) -> str:
    """Fallback `sin_zona` para cierres `fin_por_firma_actual`: el pie editorial
    va DESPUÉS de la firma. Busca el marcador de pie en [lfr-8, hi) y junta el
    bloque hasta el footer (Tribunal/Profesional), frenando ANTES de la próxima
    carátula. `hi` = linea_inicio del caso siguiente (cota dura). La firma está
    ~linea_fin_real, con jitter (artefactos de página) -> NO se ancla rígido:
    se BUSCA el marcador. Validado H161 vs 30 huérfanos de mérito."""
    n = len(lines)
    lo = max(0, lfr - 8)
    start = None
    for i in range(lo, min(hi, n)):
        if RE_PIE_START.match(lines[i]):
            start = i
            break
    if start is None:
        return ""
    out = [lines[start]]
    seen_footer = bool(RE_FOOTER.match(lines[start]))
    for i in range(start + 1, min(hi, n)):
        l = lines[i]
        if RE_PAGE.match(l):                       # artefacto: saltar sin cerrar
            continue
        if RE_PIE_LINE.match(l):
            out.append(l)
            if RE_FOOTER.match(l):
                seen_footer = True
            continue
        # línea sin keyword: ¿continuación de un pie partido o nueva carátula?
        prev = out[-1].rstrip()
        cont = (not seen_footer and
                (prev.endswith((",", "-", "\u00ad")) or _CONT_TAIL.search(prev)
                 or not prev.endswith(".")))
        if cont:
            out.append(l)
            continue
        break                                      # próxima carátula -> cerrar
    return "\n".join(out)


def _abrir_required(path: Path, required: tuple):
    if not path.exists():
        sys.exit(f"[FATAL] no existe: {path}")
    fh = path.open(encoding="utf-8", newline="")
    rd = csv.DictReader(fh)
    faltan = [c for c in required if c not in (rd.fieldnames or [])]
    if faltan:
        sys.exit(f"[FATAL] faltan columnas en {path}: {faltan}")
    return rd, fh


def derivar(zonas_path: Path, casos_path: Path, corpus_dir: Path,
            output_path: Path) -> dict:
    # spans `epilogo` por caso
    rd, fh = _abrir_required(zonas_path, REQUIRED_ZONAS)
    spans = defaultdict(list)
    with fh:
        for r in rd:
            if r["zona"] == "epilogo":
                spans[r["caso_id_canonico"]].append(
                    (int(r["linea_ini"]), int(r["linea_fin"])))

    # cache del corpus
    cache: dict[str, list | None] = {}
    def get_lines(sf: str):
        if sf not in cache:
            p = corpus_dir / sf
            cache[sf] = (p.read_text(encoding="utf-8").split("\n")
                         if p.exists() else None)
        return cache[sf]

    # universo: TODOS los fallos de casos.csv (1:1). Se materializa para poder
    # computar el inicio del caso SIGUIENTE (cota dura del fallback).
    rd, fh = _abrir_required(casos_path, REQUIRED_CASOS)
    with fh:
        cols = rd.fieldnames or []
        fallback_on = all(c in cols for c in SOFT_CASOS)
        if not fallback_on:
            print(f"[WARN] faltan {[c for c in SOFT_CASOS if c not in cols]} en "
                  f"casos.csv -> fallback sin_zona (fin_por_firma_actual) "
                  f"DESHABILITADO.")
        filas = list(rd)

    # inicio del caso siguiente por source_file (sobre TODAS las entradas, no
    # solo fallos: el pie está acotado por la próxima carátula de cualquier tipo).
    nxt: dict[str, int] = {}
    if fallback_on:
        bysf: dict[str, list] = defaultdict(list)
        for r in filas:
            li = int(r["linea_inicio"]) if r["linea_inicio"] else 0
            bysf[r["source_file"]].append((li, r["caso_id_canonico"]))
        for sf in bysf:
            arr = sorted(bysf[sf])
            for j, (li, cid) in enumerate(arr):
                nxt[cid] = arr[j + 1][0] if j + 1 < len(arr) else 10 ** 9

    salida = []
    st = Counter()
    sin_archivo = Counter()
    via_firma = 0
    for r in filas:
        if r.get("tipo_entrada") != "fallo":
            continue
        cid = r["caso_id_canonico"]
        sf = r["source_file"]
        li_caso = int(r["linea_inicio"]) if r["linea_inicio"] else 0
        segs = spans.get(cid, [])
        status, texto, wc, n_seg = "sin_zona", "", 0, len(segs)
        if segs:
            lines = get_lines(sf)
            if lines is None:
                status = "archivo_no_encontrado"
                sin_archivo[sf] += 1
            else:
                bloques = []
                for (li, lf) in sorted(segs):
                    ini = li + li_caso
                    fin = lf + li_caso
                    bloques.append("\n".join(lines[ini:min(fin + 1, len(lines))]))
                texto = _deshifenar("\n".join(bloques).strip("\n"))   # deuda #3
                wc = len(texto.split())
                status = "ok"
        elif fallback_on and r.get("status_fin") == "fin_por_firma_actual":
            # FALLBACK H161: el pie cae tras la firma, fuera de la zona.
            lines = get_lines(sf)
            if lines is not None:
                lfr = int(r["linea_fin_real"]) if r["linea_fin_real"] else 0
                hi = nxt.get(cid, len(lines))
                pie = _pie_desde_firma(lines, lfr, min(hi, len(lines)))
                if pie.strip():
                    texto = _deshifenar(pie)               # deuda #3
                    wc = len(texto.split())
                    status = "ok"                          # n_seg=0 -> vía firma
                    via_firma += 1
        salida.append({
            "caso_id_canonico": cid, "tomo": r["tomo"], "source_file": sf,
            "epilogo_status": status, "n_seg": n_seg, "wc": wc,
            "epilogo_text": texto,
        })
        st[status] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(salida)

    return {"n": len(salida), "status": st, "sin_archivo": dict(sin_archivo),
            "via_firma": via_firma}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Extrae el texto crudo de la zona epilogo (universo de fallos).")
    ap.add_argument("--zonas", type=Path, default=DEFAULT_ZONAS)
    ap.add_argument("--casos", type=Path, default=DEFAULT_CASOS)
    ap.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args(argv)

    s = derivar(args.zonas, args.casos, args.corpus_dir, args.output)
    st = s["status"]
    print(f"\n  extraer_epilogos v{__version__}")
    print(f"  fallos emitidos (1:1): {s['n']}")
    for k in ("ok", "sin_zona", "archivo_no_encontrado"):
        v = st.get(k, 0)
        pct = f"({100*v/s['n']:5.1f}%)" if s["n"] else ""
        print(f"    {k:22s} {v:5d}  {pct}")
    print(f"    └─ de ok, recuperados vía fallback de firma (n_seg=0): {s['via_firma']}")
    if s["sin_archivo"]:
        print(f"  [WARN] source_file no encontrado en corpus-dir:")
        for sf, n in s["sin_archivo"].items():
            print(f"    {sf}: {n}")
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
