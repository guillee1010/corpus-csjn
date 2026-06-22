#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derivar_partes.py — Capa de partes (M29): deriva RECURRENTE / RECURRIDO + su ROL
procesal del epílogo editorial.

Arquitectura (REE): NO muta nada. Sidecar keyed por caso_id_canonico, left-join
1:1, mismo patrón que derivar_materia. Lee `csjn_casos_epilogo.csv` (insumo
persistido por extraer_epilogos.py), NO el .md → reproducible para Dataverse.

Doctrina (Guillermo, H154): quién recurrió a la Corte sale SOLO del marcador
`Recurso ... interpuesto por X` del epílogo; el rol (actora/demandada/penal)
viene pegado al nombre en ese mismo marcador. Es la ÚNICA fuente que ata
*quién recurrió* con *qué rol tenía*. El actor/demandado del índice/cuerpo NO
define quién apeló → esa es capa futura (tipificación + casos sin epílogo).

Se extrae la PARTE, no el letrado: se resuelve `en representación de Y` /
`asistido por` / `representada por` / `con el patrocinio` para quedarse con la
parte sustantiva.

Capa 1 (epílogo) — esta versión. Salida por caso:
  recurrente, recurrente_rol, recurrido, recurrido_rol, multi_recurrente,
  partes_capa (epilogo | sin_epilogo | no_aplica), partes_fuente.

VALIDACIÓN: el parseo se validó sobre los 7 .md de las inversiones de rol de M25
(7/7 recurrente+recurrido legibles). La corrida sobre el universo (~4345) es la
que CIERRA y expone los casos difíciles (Arriola, extradiciones, multi).
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

__version__ = "0.4"  # H155: cobertura reportada también sobre el universo de MÉRITO (is_merit_decision, ya en casos.csv) — recurrente_ok 88,4% sobre los 2870 de mérito vs 63,9% sobre todos los fallos; el sin_epilogo del no-mérito (art.280 etc.) es ausencia esperada, no gap. Reporte-only: derivación y CSV de salida SIN cambios vs v0.3. // 0.3: H155 fallback formato viejo "Nombre del recurrente:" (Eje B directo) cuando falla RE_MARK_REC -> partes_fuente="epilogo:nombre_recurrente"; aditivo puro sobre el residual (NO toca los 3633 ya resueltos). // 0.2: H154 marcador flexible anclado a línea (queja/ordinario de apelación/deducido/federal/plural, salta arrastre de por_ello) -> recurrente_ok 2225->3633; parse_parte resuelve letrado (por derecho propio / por <parte> / defensor de <parte> / solo_letrado). // 0.1: marcador estricto (solo formato moderno) + capa epílogo inicial.

csv.field_size_limit(10 ** 7)

# --- Rutas (robusto al cwd; overridables CLI) -------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT  = SCRIPT_DIR.parent.parent
DEFAULT_CASOS   = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_EPILOGO = REPO_ROOT / "output" / "parser" / "csjn_casos_epilogo.csv"
DEFAULT_OUTPUT  = REPO_ROOT / "output" / "parser" / "csjn_casos_partes.csv"

REQUIRED_CASOS   = ("caso_id_canonico", "tipo_entrada", "is_merit_decision")
REQUIRED_EPILOGO = ("caso_id_canonico", "epilogo_text")

OUT_COLS = ["caso_id_canonico", "recurrente", "recurrente_rol",
            "recurrido", "recurrido_rol", "multi_recurrente",
            "partes_capa", "partes_fuente"]

# ── Gramática del epílogo ────────────────────────────────────────────────────
# marcador del recurrente (singular y plural -> multi): "Recurso(s) ...
# interpuesto(s) por ..."; cubre extraordinario / de hecho / ordinario / directo.
# marcador del recurrente, FLEXIBLE y anclado a inicio de línea (re.M): cubre
# "Recurso extraordinario [federal] interpuesto por", "Recurso de queja
# interpuesto por", "Recurso ordinario de apelación interpuesto por", "Recurso
# de hecho deducido por", plural "Recursos ... interpuestos por", y "Queja
# interpuesta por". El ancla a línea SALTA el arrastre de por_ello que la zona a
# veces incluye antes del marcador. Case-sensitive en el anclaje (Recurso/Queja
# en mayúscula = pie editorial; "recurso" minúscula = por_ello, NO matchea).
RE_MARK_REC = re.compile(
    r"^(?:Recursos?|Queja)\b[^\n]*?(?:interpuest\w+|deducid\w+)\s+por\s+"
    r"(.*?)(?=\bTraslado\b|\bTribunal\b|\bProfesional|\bNorma\b|\Z)",
    re.S | re.M)
RE_MARK_TRA = re.compile(
    r"Traslado\s+contestad\w+\s+por\s+(.*?)(?=\bTribunal\b|$)", re.S | re.I)
# FALLBACK formato viejo (tomos 329-334): rótulo explícito "Nombre del
# recurrente:" cuando NO hay marcador "Recurso ... interpuesto por". Da Eje B
# directo (quién recurrió). OJO: "Nombre del actor:" / "Parte demandada:" NO van
# acá — eso es Eje A (actor/demandado), otra capa; mapearlo a recurrente
# violaría la doctrina (el actor/demandado no define quién apeló).
RE_MARK_NOMBRE = re.compile(
    r"^Nombre\s+del\s+recurrente\s*:\s*(.*?)"
    r"(?=^Nombre\s+del\b|\bTribunal\b|\bProfesional|\bNorma\b|\Z)",
    re.S | re.M | re.I)

# parte vs letrado: si hay "en representación de Y", la parte es Y.
RE_REPDE = re.compile(r"\ben\s+representaci[oó]n\s+de\s+(.+)$", re.I)
# corte del nombre de la parte (donde arranca rol/representación/patrocinio):
RE_CORTE = re.compile(
    r",?\s*(?:parte\s+\w+|(?:actora|demandada|querellante|coactora|codemandada)"
    r"\s+en\s+autos|representad\w+|asistid\w+|con\s+el\s+patrocinio|"
    r"en\s+su\s+car[aá]cter|en\s+calidad|patrocinad\w+|Defensor\w*|Fiscal\b|"
    r"Procurador\w*)", re.I)
# rol procesal explícito en el clause:
RE_ROL   = re.compile(
    r"\b(?:parte\s+)?(actora|demandada|querellante|coactora|codemandada)\b", re.I)
RE_PENAL = re.compile(
    r"\b(Fiscal|Defensor\w*|Procurador\w*|imputad\w+|Ministerio\s+P[úu]blico)\b",
    re.I)
# señal de multi-recurrente: "Recursos ... interpuestos" (plural) o "y por ..."
RE_MULTI = re.compile(
    r"Recursos\s+\w+\s+interpuestos|\by\s+por\s+(?:el\s+|la\s+|los\s+|las\s+)?[A-ZÁÉÍÓÚÑ]",
    re.I)


def _dehifen(txt: str) -> str:
    """Pega cortes de palabra del OCR y colapsa el clause a una línea."""
    txt = txt.replace("\u00ad", "")                       # soft hyphen
    txt = re.sub(r"[-\u2010\u2011]\s*\n\s*", "", txt)     # corte de palabra
    txt = re.sub(r"\s*\n\s*", " ", txt)                   # une líneas
    return re.sub(r"\s+", " ", txt).strip()


def _trim_nombre(s: str) -> str:
    """Recorta el nombre: saca coma/espacios; quita el punto de fin de oración
    PERO conserva las iniciales punteadas (`C. J. A.`)."""
    s = s.strip().strip(",").strip()
    if s.endswith(".") and not re.search(r"\b[A-ZÁÉÍÓÚÑ]\.$", s):
        s = s[:-1].strip()
    return s


# sub-patrones de letrado (recurrente listado como abogado, no como parte):
RE_LETRADO  = re.compile(r"^(?:el|la|los|las)\s+(?:Dres?\.|Dra\.|Defensora?|Procuradora?)", re.I)
RE_DPROPIO  = re.compile(r"\bpor\s+derecho\s+propio\b", re.I)
RE_POR_X    = re.compile(r",?\s*\bpor\s+(?!derecho\s+propio)(.+)$", re.I)
RE_DEF_DE   = re.compile(r"(?:abogad\w+\s+)?defensor\w*\s+(?:oficial\s+)?de\s+(.+)$", re.I)


def _rol(clause: str) -> str:
    mr = RE_ROL.search(clause)
    if mr:
        return mr.group(1).lower()
    return "penal" if RE_PENAL.search(clause) else ""


def parse_parte(clause: str) -> tuple[str, str]:
    """(nombre_parte, rol). Resuelve representación y saca el letrado, quedándose
    con la PARTE sustantiva. Si el marcador solo nombra al letrado y no a la parte
    (típico penal), devuelve ('', 'solo_letrado') — no se inventa la parte."""
    clause = clause.strip(" .")
    # 1) "en representación de Y" -> Y
    rep = RE_REPDE.search(clause)
    if rep:
        return _trim_nombre(rep.group(1)), _rol(clause)
    # 2) el clause arranca con un letrado -> buscar la parte real
    if RE_LETRADO.match(clause):
        if RE_DPROPIO.search(clause):                       # el letrado ES la parte
            nombre = _trim_nombre(re.split(r",?\s*por\s+derecho", clause, maxsplit=1)[0])
            return nombre, "por_derecho_propio"
        mp = RE_POR_X.search(clause)                        # "..., por <parte>"
        if mp:
            return _trim_nombre(mp.group(1)), _rol(clause)
        md = RE_DEF_DE.search(clause)                       # "defensor de <parte>"
        if md and "ante" not in md.group(1)[:6].lower():
            return _trim_nombre(md.group(1)), "penal"
        return "", "solo_letrado"                           # letrado sin parte: marcar
    # 3) caso general: recortar en el primer marcador de rol/representación
    m = RE_CORTE.search(clause)
    return _trim_nombre(clause[:m.start()] if m else clause), _rol(clause)


def derivar_de_epilogo(epilogo_text: str) -> dict:
    """Aplica la gramática al epílogo crudo. Devuelve campos de salida (capa 1)."""
    rec = RE_MARK_REC.search(epilogo_text)
    if not rec:
        # Fallback formato viejo: rótulo "Nombre del recurrente:" (Eje B directo).
        nom = RE_MARK_NOMBRE.search(epilogo_text)
        if nom:
            nom_clause = _dehifen(nom.group(1))
            nn, nr = parse_parte(nom_clause)
            return {"recurrente": nn, "recurrente_rol": nr,
                    "recurrido": "", "recurrido_rol": "",
                    "multi_recurrente": "si" if RE_MULTI.search(nom_clause) else "no",
                    "partes_capa": "epilogo",
                    "partes_fuente": "epilogo:nombre_recurrente"}
        return {"recurrente": "", "recurrente_rol": "", "recurrido": "",
                "recurrido_rol": "", "multi_recurrente": "",
                "partes_capa": "epilogo", "partes_fuente": "sin_marcador_recurso"}
    rec_clause = _dehifen(rec.group(1))
    rn, rr = parse_parte(rec_clause)
    multi = "si" if RE_MULTI.search(rec_clause) else "no"

    tra = RE_MARK_TRA.search(epilogo_text)
    dn, dr = ("", "")
    if tra:
        dn, dr = parse_parte(_dehifen(tra.group(1)))

    fuente = "epilogo:recurso" + ("+traslado" if tra else "")
    return {"recurrente": rn, "recurrente_rol": rr,
            "recurrido": dn, "recurrido_rol": dr,
            "multi_recurrente": multi,
            "partes_capa": "epilogo", "partes_fuente": fuente}


def derivar(casos_path: Path, epilogo_path: Path, output_path: Path) -> dict:
    # universo: entradas de casos.csv (para left-join 1:1)
    if not casos_path.exists():
        sys.exit(f"[FATAL] no existe: {casos_path}")
    with casos_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_CASOS if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {casos_path}: {faltan}")
        filas = list(rd)

    # insumo: epílogos
    epi = {}
    if not epilogo_path.exists():
        sys.exit(f"[FATAL] no existe el sidecar de epílogos: {epilogo_path}\n"
                 f"        (corré antes extraer_epilogos.py)")
    with epilogo_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_EPILOGO if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {epilogo_path}: {faltan}")
        tiene_status = "epilogo_status" in (rd.fieldnames or [])
        for r in rd:
            epi[r["caso_id_canonico"]] = {
                "text": r["epilogo_text"],
                # status del extractor (sin_zona/archivo_no_encontrado/ok); si el
                # CSV no lo trae, se infiere de si hay texto.
                "status": (r["epilogo_status"] if tiene_status
                           else ("ok" if r["epilogo_text"].strip() else "sin_zona")),
            }

    salida = []
    cov = Counter()
    cov_razon = Counter()
    rol_rec = Counter()
    multi_n = 0
    merit_cov = {"1": Counter(), "0": Counter()}  # cobertura split por universo de mérito
    for r in filas:
        cid = r["caso_id_canonico"]
        if r.get("tipo_entrada") != "fallo":
            salida.append({"caso_id_canonico": cid, "recurrente": "",
                           "recurrente_rol": "", "recurrido": "",
                           "recurrido_rol": "", "multi_recurrente": "",
                           "partes_capa": "no_aplica",
                           "partes_fuente": f"tipo_entrada={r.get('tipo_entrada')}"})
            cov["no_aplica"] += 1
            continue
        merit = r.get("is_merit_decision", "")
        if cid in epi and epi[cid]["status"] == "ok":
            d = derivar_de_epilogo(epi[cid]["text"])
            d["caso_id_canonico"] = cid
            salida.append(d)
            if d["partes_fuente"] == "sin_marcador_recurso":
                cov["epilogo_sin_marcador"] += 1
                clave = "epilogo_sin_marcador"
            else:
                cov["recurrente_ok"] += 1
                clave = "recurrente_ok"
                if d["recurrente_rol"]:
                    rol_rec[d["recurrente_rol"]] += 1
                else:
                    rol_rec["(sin rol)"] += 1
                if d["multi_recurrente"] == "si":
                    multi_n += 1
        else:
            # sin epílogo aprovechable: propaga la RAZÓN (sin_zona /
            # archivo_no_encontrado / no_en_epilogo_csv), no muerte silenciosa.
            razon = epi[cid]["status"] if cid in epi else "no_en_epilogo_csv"
            salida.append({"caso_id_canonico": cid, "recurrente": "",
                           "recurrente_rol": "", "recurrido": "",
                           "recurrido_rol": "", "multi_recurrente": "",
                           "partes_capa": "sin_epilogo", "partes_fuente": razon})
            cov["sin_epilogo"] += 1
            cov_razon[razon] += 1
            clave = "sin_epilogo"
        if merit in merit_cov:
            merit_cov[merit][clave] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(salida)

    return {"n": len(salida), "cov": cov, "cov_razon": cov_razon,
            "rol_rec": rol_rec, "multi": multi_n, "merit_cov": merit_cov}


def _reporte(st: dict) -> None:
    cov = st["cov"]
    fallos = (cov.get("recurrente_ok", 0) + cov.get("epilogo_sin_marcador", 0)
              + cov.get("sin_epilogo", 0))
    print(f"\n  derivar_partes v{__version__}")
    print(f"  filas escritas: {st['n']}  (fallos: {fallos})")
    print("\n  === cobertura (capa 1, epílogo) ===")
    for k in ["recurrente_ok", "epilogo_sin_marcador", "sin_epilogo", "no_aplica"]:
        v = cov.get(k, 0)
        base = fallos if k != "no_aplica" else st["n"]
        pct = f"({100*v/base:5.1f}%)" if base else ""
        print(f"    {k:22s} {v:5d}  {pct}")
    print(f"  multi_recurrente (flag):  {st['multi']}")
    mc = st.get("merit_cov")
    if mc:
        for universo, lbl in [("1", "MÉRITO (universo SCDB)"), ("0", "no-mérito")]:
            c = mc.get(universo, Counter())
            tot = sum(c.values())
            if not tot:
                continue
            print(f"\n  === cobertura sobre {lbl}: {tot} fallos ===")
            for k in ["recurrente_ok", "epilogo_sin_marcador", "sin_epilogo"]:
                v = c.get(k, 0)
                print(f"    {k:22s} {v:5d}  ({100*v/tot:5.1f}%)")
    if st["cov_razon"]:
        print("\n  === sin_epilogo, por razón (auditable) ===")
        for razon, v in st["cov_razon"].most_common():
            print(f"    {razon:22s} {v:5d}")
    print("\n  === rol del recurrente (sobre recurrente_ok) ===")
    for rol, v in st["rol_rec"].most_common():
        print(f"    {rol:14s} {v:5d}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Deriva recurrente/recurrido + rol del epílogo (capa 1).")
    ap.add_argument("--casos", type=Path, default=DEFAULT_CASOS)
    ap.add_argument("--epilogo", type=Path, default=DEFAULT_EPILOGO)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args(argv)

    st = derivar(args.casos, args.epilogo, args.output)
    _reporte(st)
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
