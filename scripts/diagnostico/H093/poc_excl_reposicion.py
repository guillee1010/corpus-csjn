#!/usr/bin/env python3
# scripts/diagnostico/H093/poc_excl_reposicion.py
# -----------------------------------------------------------------------------
# PoC H093 - fix de precision de FUERA_DE_TERMINO. Mide el efecto de extender la
# exclusion con una firma de DISPOSITIVO: cuando el por_ello desestima una
# reposicion/revocatoria/aclaratoria (recurso presente que NO es la apelacion
# tardia), el "extempor" del considerando pertenece al antecedente y FUERA es FP.
#
# Los 2 FP confirmados a mano (329_p5138/5316) tienen por_ello "se desestima la
# reposicion"; los 10 TP tienen por_ello de queja/presentacion directa. El
# discriminador vive en el por_ello, que el CSV guarda COMPLETO (max 300 chars,
# 0 truncados), asi que esta medicion es EXACTA pese al truncado del considerando.
#
# DIAGNOSTICO, NO produccion: no toca outputs ni el parser; solo lee csjn_casos.csv
# y reusa los regexes reales del parser (REE: no reimplementar).
#
#     pushd scripts\pipeline; python ..\diagnostico\H093\poc_excl_reposicion.py; popd
# -----------------------------------------------------------------------------

__version__ = "1.0"

import ast
import csv
import re
import sys
from pathlib import Path

csv.field_size_limit(10 ** 7)

ROOT = Path(__file__).resolve().parents[3]
CSV_CANONICO = ROOT / "output" / "parser" / "csjn_casos.csv"
PIPELINE_DIR = ROOT / "scripts" / "pipeline"

# regexes/funcs reales del parser que necesita la cadena clasificar (menos FUERA)
WANT = ["RE_CAUSA_SENTENCIA_DEFINITIVA", "RE_CAUSA_FUNDAMENTACION",
        "RE_CAUSA_DEPOSITO", "RE_CAUSA_REMITE_DICTAMEN",
        "OUTCOME_A_CAUSA", "OUTCOMES_GATE_GENERICO"]


def cargar_del_parser():
    if str(PIPELINE_DIR) not in sys.path:
        sys.path.insert(0, str(PIPELINE_DIR))
    try:
        import parser as _p  # noqa
        return {k: getattr(_p, k) for k in WANT}, _p._unhyphenate, "import"
    except Exception:
        src = (PIPELINE_DIR / "parser.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        ns = {"re": re}
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in WANT):
                exec(compile(ast.Module([node], []), "parser.py", "exec"), ns)
            if isinstance(node, ast.FunctionDef) and node.name == "_unhyphenate":
                exec(compile(ast.Module([node], []), "parser.py", "exec"), ns)
        return {k: ns[k] for k in WANT}, ns["_unhyphenate"], "ast"


# --- PROPUESTA: firma de dispositivo de reposicion (sobre por_ello) -----------
# Ancla al recurso PRESENTE rechazado: reposicion / revocatoria / aclaratoria.
# No toca el considerando, asi que es inmune al truncado.
RE_DISPOSITIVO_REPOSICION = re.compile(
    r"(?:se\s+)?(?:desestima\w*|rechaza\w*|no\s+ha\s+lugar\s+a)\s+"
    r"(?:el\s+|la\s+|los\s+|las\s+)?(?:recurso\s+de\s+)?"
    r"(?:reposici[oó]n|revocatoria|aclaratoria)",
    re.I)


def main():
    objs, unhyphenate, modo = cargar_del_parser()
    RE_SD = objs["RE_CAUSA_SENTENCIA_DEFINITIVA"]
    RE_FU = objs["RE_CAUSA_FUNDAMENTACION"]
    RE_DP = objs["RE_CAUSA_DEPOSITO"]
    RE_RD = objs["RE_CAUSA_REMITE_DICTAMEN"]
    OUTCOME_A_CAUSA = objs["OUTCOME_A_CAUSA"]
    GATE = objs["OUTCOMES_GATE_GENERICO"]

    def norm(t):
        return re.sub(r"\s+", " ", unhyphenate(t or "")).strip()

    def causal_sin_fuera(outcome, co, pe, dic):
        """Reproduce clasificar_causa_inadmisibilidad SALTEANDO FUERA (como si la
        nueva exclusion lo hubiera soltado). Exacto si el considerando no esta
        truncado (los 2 FP lo tienen completo)."""
        if outcome in OUTCOME_A_CAUSA:
            return OUTCOME_A_CAUSA[outcome]
        if outcome not in GATE and outcome != "otro":
            return ""
        txt = co + " || " + pe
        if RE_SD.search(txt): return "FALTA_SENTENCIA_DEFINITIVA"
        if RE_FU.search(txt): return "FALTA_FUNDAMENTACION_AUTONOMA"
        if RE_DP.search(txt): return "DEPOSITO_PREVIO"
        # (FUERA salteado a proposito)
        if outcome == "otro": return ""
        if RE_RD.search(co) and str(dic).strip().lower() in ("true","1","presente"):
            return "INADMISIBLE_REMITE_DICTAMEN"
        return "INADMISIBLE_SIN_CAUSAL_EXPLICITA"

    with open(CSV_CANONICO, encoding="utf-8") as f:
        fal = [x for x in csv.DictReader(f) if x.get("tipo_entrada") == "fallo"]

    print(f"poc_excl_reposicion.py v{__version__}  (parser via {modo})")
    print(f"CSV: {CSV_CANONICO}  | fallos: {len(fal)}\n")

    fuera = [x for x in fal if x["causa_inadmisibilidad"] == "FUERA_DE_TERMINO"]
    print(f"=== FUERA_DE_TERMINO actuales: {len(fuera)} ===")
    print("aplico la firma de dispositivo sobre por_ello (drop = nuevo EXCL lo suelta)\n")
    drop, keep = [], []
    for x in sorted(fuera, key=lambda r: r["caso_id_canonico"]):
        pe = norm(x["por_ello_text"])
        cae = bool(RE_DISPOSITIVO_REPOSICION.search(pe))
        (drop if cae else keep).append(x)
        marca = "DROP -> recalcula" if cae else "keep"
        print(f"  {x['caso_id_canonico']:12} {marca:18} por_ello: {pe[:80]}")

    print(f"\n  -> DROP {len(drop)}  |  KEEP {len(keep)}  (esperado: drop 2, keep 10)")

    print("\n=== nuevo destino de los DROP (recalculo sin FUERA) ===")
    for x in drop:
        co = norm(x["considerando_text"]); pe = norm(x["por_ello_text"])
        trunc = " [considerando TRUNCADO: destino aproximado]" if len(x["considerando_text"]) >= 2000 else ""
        nuevo = causal_sin_fuera(x["outcome"], co, pe, x.get("dictamen_presente",""))
        print(f"  {x['caso_id_canonico']:12} FUERA_DE_TERMINO -> {nuevo}{trunc}")

    # falsa exclusion: ningun KEEP/TP deberia matchear la firma (ya verificado arriba,
    # pero lo dejo explicito como invariante)
    print("\n=== invariante: ningun TP cae por la firma ===")
    falsos = [x for x in keep if RE_DISPOSITIVO_REPOSICION.search(norm(x["por_ello_text"]))]
    print(f"  TP excluidos por error: {len(falsos)} (debe ser 0)")

    # barrido del universo: reposiciones-desestimadas y su causal actual
    print("\n=== barrido: por_ello con firma de reposicion en TODO gate-generico ===")
    universo = [x for x in fal if x["outcome"] in (GATE | {"otro"})]
    rep = [x for x in universo if RE_DISPOSITIVO_REPOSICION.search(norm(x["por_ello_text"]))]
    from collections import Counter
    print(f"  reposiciones/revocatorias desestimadas en gate-generico: {len(rep)}")
    print(f"  su causa_inadmisibilidad ACTUAL: {dict(Counter(x['causa_inadmisibilidad'] for x in rep))}")
    print("  (las que hoy son FUERA son las que el fix corrige; el resto ya estan")
    print("   en SIN_CAUSAL u otra y el fix no las toca)")


if __name__ == "__main__":
    main()
