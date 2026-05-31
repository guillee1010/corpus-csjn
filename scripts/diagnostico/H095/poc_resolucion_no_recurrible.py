#!/usr/bin/env python3
# scripts/diagnostico/H095/poc_resolucion_no_recurrible.py
# -----------------------------------------------------------------------------
# PoC H095 — causal nueva RESOLUCION_NO_RECURRIBLE.
#
# Mide DIRECCION antes de tocar produccion (regla: PoC antes de produccion;
# A/B old<->new sobre texto identico, M15). OLD = parser.clasificar_... actual
# (importado, sin reimplementar heuristicas). NEW = misma funcion con la causal
# nueva chequeada ULTIMA en el bloque gate-generico (asi, por construccion, solo
# puede convertir lo que de otro modo seria SIN_CAUSAL; nunca le roba a
# SD/FUND/DEPOSITO/FUERA). Reusa las regex compiladas de parser.py; solo agrega
# localmente las dos nuevas (identicas a las que van al patch).
#
# Diagnostico, NO produccion: solo lee. Corre sobre output/parser/csjn_casos.csv,
# que es texto truncado a 2000 -> el conteo es PISO (M15). El numero real de
# produccion sale de re-correr parser.py sobre los .md + check_regresion; los
# que aparezcan de mas son delta por truncado (ver watch-list al final) y se
# ojean con extraer_caso.py antes de re-goldear.
#
# Uso (desde cualquier subdirectorio del repo):
#     python scripts/diagnostico/H095/poc_resolucion_no_recurrible.py
# -----------------------------------------------------------------------------

import csv
import re
import sys
from collections import Counter
from pathlib import Path

csv.field_size_limit(10 ** 7)


def _find_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start.parents[1] if len(start.parents) >= 2 else start


ROOT = _find_root(Path(__file__).resolve().parent)
CSV = ROOT / "output" / "parser" / "csjn_casos.csv"
PIPELINE = ROOT / "scripts" / "pipeline"
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import parser as P  # noqa: E402  (OLD = la version actual, sin RNR)

# --- candidato NEW: las dos regex que van al patch (identicas) ---
RE_CAUSA_NO_RECURRIBLE = re.compile(
    r"(?:las\s+(?:decisiones|sentencias|resoluciones)\s+(?:dictadas?\s+)?"
    r"(?:de|por)\s+(?:esta\s+|la\s+)?corte|las\s+sentencias\s+del\s+tribunal)"
    r".{0,130}?no\s+son,?\s*(?:como\s+principio,?\s*)?suscepti\w*\s+de\s+"
    r"(?:recurso|reposici[oó]n|revocatoria|nulidad)", re.I)
RE_CAUSA_NO_RECURRIBLE_EXCL = re.compile(
    r"(?:se\s+resuelve\s+)?hac(?:er|e)\s+lugar\s+(?:a\s+)?(?:al?\s+|la\s+)?"
    r"(?:recurso\s+de\s+)?(?:reposici[oó]n|revocatoria)", re.I)


def clasificar_new(outcome, considerando_text, por_ello_text, dictamen_presente):
    """Copia EXACTA de parser.clasificar_causa_inadmisibilidad con la causal nueva
    chequeada ULTIMA dentro del bloque gate-generico. Reusa las regex de parser."""
    if outcome in P.OUTCOME_A_CAUSA:
        return P.OUTCOME_A_CAUSA[outcome]
    if outcome not in P.OUTCOMES_GATE_GENERICO and outcome != "otro":
        return ""
    co = re.sub(r"\s+", " ", P._unhyphenate(considerando_text)).strip()
    pe = re.sub(r"\s+", " ", P._unhyphenate(por_ello_text)).strip()
    txt = co + " || " + pe
    if outcome in P.OUTCOMES_GATE_GENERICO:
        if P.RE_CAUSA_SENTENCIA_DEFINITIVA.search(txt):
            return "FALTA_SENTENCIA_DEFINITIVA"
        if P.RE_CAUSA_FUNDAMENTACION.search(txt):
            return "FALTA_FUNDAMENTACION_AUTONOMA"
        if P.RE_CAUSA_DEPOSITO.search(txt):
            return "DEPOSITO_PREVIO"
        if (P.RE_CAUSA_FUERA_TERMINO.search(txt)
                and not P.RE_CAUSA_FUERA_TERMINO_EXCL.search(txt)
                and not P.RE_CAUSA_FUERA_TERMINO_EXCL_DISP.search(pe)):
            return "FUERA_DE_TERMINO"
        # --- NUEVO: ultimo en el bloque gate (no le roba a las anteriores) ---
        if (RE_CAUSA_NO_RECURRIBLE.search(co)
                and not RE_CAUSA_NO_RECURRIBLE_EXCL.search(pe)):
            return "RESOLUCION_NO_RECURRIBLE"
    if outcome == "otro":
        return ""
    if (P.RE_CAUSA_REMITE_DICTAMEN.search(co)
            and str(dictamen_presente).strip().lower() in ("true", "1", "presente")):
        return "INADMISIBLE_REMITE_DICTAMEN"
    return "INADMISIBLE_SIN_CAUSAL_EXPLICITA"


def main():
    if not CSV.exists():
        sys.exit(f"[FATAL] no encuentro {CSV}")
    with open(CSV, encoding="utf-8") as f:
        rows = [x for x in csv.DictReader(f) if x.get("tipo_entrada") == "fallo"]

    diffs, theft = [], []
    for x in rows:
        args = (x.get("outcome", ""), x.get("considerando_text", ""),
                x.get("por_ello_text", ""), x.get("dictamen_presente", ""))
        old = P.clasificar_causa_inadmisibilidad(*args)
        new = clasificar_new(*args)
        if old != new:
            diffs.append((x["caso_id_canonico"], old, new))
            # robo = una causal existente (no SIN_CAUSAL) pierde un caso
            if old not in ("INADMISIBLE_SIN_CAUSAL_EXPLICITA",) and new == "RESOLUCION_NO_RECURRIBLE":
                theft.append((x["caso_id_canonico"], old))

    print(f"A/B old<->new (piso CSV, texto truncado a 2000): {len(diffs)} filas cambian")
    print("  transiciones:", dict(Counter(f"{o} -> {n}" for _, o, n in diffs)))
    for cid, o, n in sorted(diffs, key=lambda z: (int(z[0].split('_')[0]), z[0])):
        print(f"    {cid:12s} {o:34s} -> {n}")

    print()
    if theft:
        print(f"[FAIL] ROBO a causal existente: {theft}")
        sys.exit(1)
    print("[OK] cero robo: toda transicion es SIN_CAUSAL -> RESOLUCION_NO_RECURRIBLE")
    print("     (RNR chequeada ultima => SD/FUND/DEPOSITO/FUERA intactas por construccion)")

    # watch-list de delta: gate, considerando truncado (==2000), menciona
    # reposicion/revocatoria, hoy SIN_CAUSAL -> donde la frase podria caer pasado
    # el truncado y disparar RNR en produccion (texto completo). Ojear estos en
    # el check_regresion antes de re-goldear.
    watch = [x["caso_id_canonico"] for x in rows
             if x.get("outcome", "") in P.OUTCOMES_GATE_GENERICO
             and len(x.get("considerando_text", "")) >= 2000
             and re.search(r"reposici|revocatoria", x.get("considerando_text", "") or "", re.I)
             and P.clasificar_causa_inadmisibilidad(
                 x.get("outcome", ""), x.get("considerando_text", ""),
                 x.get("por_ello_text", ""), x.get("dictamen_presente", "")
             ) == "INADMISIBLE_SIN_CAUSAL_EXPLICITA"]
    print()
    print(f"watch-list delta por truncado (a ojear en produccion): {len(watch)}")
    print("   ", watch)
    print()
    print("NOTA: 329_p5316 NO entra (OCR le inyecto el encabezado de pagina en")
    print("      'suscepti5317 DE JUSTICIA...bles'); su hermano 329_p5138 si. Miss")
    print("      conocido por running-head mid-palabra -> ver DEUDA (no se fuerza).")


if __name__ == "__main__":
    main()
