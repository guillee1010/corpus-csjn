#!/usr/bin/env python3
# scripts/diagnostico/H092/sub_gate.py
# -----------------------------------------------------------------------------
# PoC H092 - sub-clasificacion del gate de admisibilidad contra el vocabulario
# controlado de la Corte. DIAGNOSTICO, NO produccion: no toca outputs canonicos
# ni el parser; solo lee csjn_casos.csv e imprime un reporte (opcional --dump).
#
# Invocacion (resuelve el import de parser/parser_editorial igual que el harness):
#     pushd scripts\pipeline; python ..\diagnostico\H092\sub_gate.py; popd
# Tambien corre desde la raiz del repo (agrega scripts/pipeline al path). Si
# parser_editorial no esta disponible (entorno aislado), cae a extraccion
# estatica de los regexes 280/ac4 via ast -- mismo patron que generar_manifiesto.
#
# Objetivo: medir cuanto del universo gate-generico (desestima / inadmisible /
# improcedente / otro / mal_concedido / desierto) sube a una causal NOMBRADA del
# vocabulario de la Corte, con deteccion ANCLADA (la causal atada al recurso que
# se decide, no a una mencion suelta -- cada termino es polisemico como lo fue el
# art.280). Los conteos sobre el CSV son PISO: considerando_text esta truncado a
# 2000 chars; la medicion fina corre sobre texto completo en el pipeline.
# -----------------------------------------------------------------------------

__version__ = "1.0"

import argparse
import ast
import collections
import csv
import itertools
import re
import sys
from pathlib import Path

# --- localizacion robusta (no adivinar paths: derivar de __file__) ------------
ROOT = Path(__file__).resolve().parents[3]          # scripts/diagnostico/H092 -> raiz
CSV_CANONICO = ROOT / "output" / "parser" / "csjn_casos.csv"
PIPELINE_DIR = ROOT / "scripts" / "pipeline"


# --- reuso de los regexes 280/ac4 reales del parser (REE: no reimplementar) ---
def cargar_regexes_parser():
    """Prefiere importar de parser.py; si parser_editorial no esta, extrae los
    literales de los regexes via ast sin ejecutar el modulo entero."""
    if str(PIPELINE_DIR) not in sys.path:
        sys.path.insert(0, str(PIPELINE_DIR))
    want = ["RE_280_CONSIDERANDO", "RE_280_LIBRE", "RE_ACORDADA_4_CONSIDERANDO",
            "RE_ACORDADA_4_REGLAMENTO", "RE_ACORDADA_4_DIRECTA"]
    try:
        import parser as _p  # noqa
        objs = {k: getattr(_p, k) for k in want}
        unhyphen = _p._unhyphenate
        return objs, unhyphen, "import"
    except Exception:
        src = (PIPELINE_DIR / "parser.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        ns = {"re": re}
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id in want):
                exec(compile(ast.Module([node], []), "parser.py", "exec"), ns)
            if (isinstance(node, ast.FunctionDef) and node.name == "_unhyphenate"):
                exec(compile(ast.Module([node], []), "parser.py", "exec"), ns)
        return {k: ns[k] for k in want}, ns["_unhyphenate"], "ast"


# --- detectores de cola -------------------------------------------------------
# Cada entrada: (regex, excluir, gate_only, estado)
#   gate_only  -> solo asigna si el outcome es gatekeeping (evita el 'otro' con
#                 la palabra usada en sentido incidental)
#   estado     -> "validada" (muestreada a mano H092) | "candidata" (sin validar)
#
# Las cuatro validadas se anclan al recurso decidido. Las candidatas usan la
# formula canonica pero NO fueron muestreadas: tratar sus conteos como hipotesis.

GATE_OUTCOMES = {"desestima", "inadmisible", "improcedente",
                 "otro", "mal_concedido", "desierto"}
GATE_STRICT = GATE_OUTCOMES - {"otro"}   # para causales gate_only

COLA = {
    # --- validadas H092 (muestreo manual: precision alta) ---
    "FALTA_SENTENCIA_DEFINITIVA": dict(estado="validada", gate_only=False,
        rx=re.compile(
            r"no\s+se\s+dirige\s+contra\s+(?:una\s+|la\s+)?sentencia\s+definitiva"
            r"(?:\s+o\s+equiparable)?|"
            r"no\s+(?:constituye|reviste\s+(?:el\s+)?car[aá]cter\s+de|es)\s+"
            r"(?:la\s+|una\s+)?sentencia\s+definitiva|"
            r"recurso\s+extraordinario.{0,60}?no.{0,20}?sentencia\s+definitiva",
            re.I),
        excl=None),
    "FALTA_FUNDAMENTACION_AUTONOMA": dict(estado="validada", gate_only=False,
        rx=re.compile(
            r"(?:no\s+cumple\s+con\s+el\s+requisito\s+de|carece\s+de|sin|"
            r"defectuosa|insuficiente|deficiente)\s+(?:la\s+)?"
            r"fundamentaci[oó]n\s+aut[oó]noma|"
            r"fundamentaci[oó]n\s+aut[oó]noma\s+(?:exigid|que\s+exige|requerid)",
            re.I),
        excl=None),
    "DEPOSITO_PREVIO": dict(estado="validada", gate_only=False,
        rx=re.compile(
            r"no\s+(?:ha(?:berse)?\s+|se\s+ha\s+)?"
            r"(?:integrad|efectuad|abonad|acreditad|cumplid)\w+\s+(?:con\s+)?"
            r"el\s+dep[oó]sito|"
            r"intimad\w+\s+a\s+(?:efectuar|integrar|abonar)\s+el\s+dep[oó]sito"
            r".{0,120}?(?:no\s+|sin\s+)",
            re.I),
        excl=None),
    "FUERA_DE_TERMINO": dict(estado="validada", gate_only=True,
        rx=re.compile(
            r"(?:recurso|queja|apelaci[oó]n|remedio|presentaci[oó]n)\s+\w*\s*"
            r"(?:fue\s+|ha\s+sido\s+|resulta\s+|es\s+|deducid[ao]\s+)?"
            r"(?:interpuest|deducid|present)?\w*\s+(?:de\s+manera\s+|en\s+forma\s+)?"
            r"extempor[aá]ne|"
            r"(?:recurso|queja|apelaci[oó]n)\s+\w*\s*"
            r"(?:fue\s+|ha\s+sido\s+)?(?:interpuest|deducid)\w+\s+"
            r"fuera\s+del?\s+(?:plazo|t[eé]rmino)",
            re.I),
        # excluir: la palabra referida a algo que NO es el recurso de esta causa
        excl=re.compile(
            r"declar[oó]\s+extempor|"
            r"constancia\s+\w+\s+(?:resulta\s+|es\s+)?extempor|"
            r"(?:declaraci[oó]n\s+de\s+incompetencia|demanda)\s+\w*\s*"
            r"(?:resulta\s+|fue\s+|es\s+)?extempor",
            re.I)),

    # --- candidatas (formula canonica, SIN validar -- muestrear antes de lockear) ---
    "FALTA_DENEGACION_REX": dict(estado="candidata", gate_only=True,
        rx=re.compile(
            r"no\s+(?:medi[oó]|hubo|existe|se\s+dict[oó])\s+(?:resoluci[oó]n\s+)?"
            r"deneg\w+\s+del\s+recurso\s+extraordinario|"
            r"sin\s+(?:previa\s+)?deneg\w+\s+del\s+recurso\s+extraordinario|"
            r"ausencia\s+de\s+(?:resoluci[oó]n\s+)?deneg\w+",
            re.I),
        excl=None),
    "FALTA_RELACION_DIRECTA": dict(estado="candidata", gate_only=True,
        rx=re.compile(
            r"no\s+existe\s+relaci[oó]n\s+directa\s+e\s+inmediata|"
            r"(?:carece\s+de|falta\s+de)\s+relaci[oó]n\s+directa",
            re.I),
        excl=None),
    "FALTA_INTRODUCCION_OPORTUNA_CF": dict(estado="candidata", gate_only=True,
        rx=re.compile(
            r"no\s+(?:introdujo|plante[oó]|propuso)\s+(?:oportuna|tempestiva)mente"
            r"\s+la\s+cuesti[oó]n\s+federal|"
            r"cuesti[oó]n\s+federal\s+(?:no\s+fue\s+|fue\s+)?(?:planteada\s+|"
            r"introducida\s+)?(?:tard[ií]a|extempor)|"
            r"(?:tard[ií]a|extempor\w+)\s+introducci[oó]n\s+de\s+la\s+cuesti[oó]n\s+federal",
            re.I),
        excl=None),
    "TRIBUNAL_SUPERIOR_CAUSA": dict(estado="candidata", gate_only=True,
        rx=re.compile(
            r"no\s+(?:proviene|emana|se\s+trata)\s+del?\s+(?:superior\s+)?tribunal"
            r"\s+superior\s+de\s+la\s+causa|"
            r"no\s+(?:es|reviste\s+(?:el\s+)?car[aá]cter\s+de)\s+(?:el\s+)?"
            r"superior\s+tribunal\s+de\s+la\s+causa",
            re.I),
        excl=None),
    "SALTO_DE_INSTANCIA": dict(estado="candidata", gate_only=True,
        rx=re.compile(r"per\s+saltum|salto\s+de\s+instancia", re.I),
        excl=None),
}

# remision al dictamen del Procurador: la causal vive en el dictamen, no aca
RE_REMITE = re.compile(
    r"se\s+remite|comparte\s+(?:los\s+)?(?:sus\s+)?fundamentos|"
    r"adecuado\s+tratamiento\s+en\s+el\s+dictamen|"
    r"dictamen\s+(?:de|del|de\s+la)\s+(?:se[ñn]or|se[ñn]ora)\s+[Pp]rocurador", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(CSV_CANONICO),
                    help="ruta a csjn_casos.csv (default: output/parser/)")
    ap.add_argument("--dump", default="",
                    help="si se da, escribe un CSV (caso_id, causal, snippet) "
                         "para validacion manual")
    args = ap.parse_args()

    regexes, unhyphenate, modo = cargar_regexes_parser()
    RE_280C, RE_280L = regexes["RE_280_CONSIDERANDO"], regexes["RE_280_LIBRE"]
    RE_AC = [regexes["RE_ACORDADA_4_CONSIDERANDO"],
             regexes["RE_ACORDADA_4_REGLAMENTO"],
             regexes["RE_ACORDADA_4_DIRECTA"]]

    def norm(t):
        return re.sub(r"\s+", " ", unhyphenate(t)).strip()

    def det_280(c):
        return bool(RE_280C.search(c) or RE_280L.search(c))

    def det_ac4(c):
        return any(p.search(c) for p in RE_AC)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        sys.exit(f"[FATAL] no encuentro {csv_path}")

    with open(csv_path, encoding="utf-8") as f:
        rows = [x for x in csv.DictReader(f) if x.get("tipo_entrada") == "fallo"]
    sub = [x for x in rows if x["outcome"] in GATE_OUTCOMES]

    def clasificar(x):
        co = norm(x["considerando_text"])
        pe = norm(x["por_ello_text"])
        txt = co + " || " + pe
        # 0. sanity: 280/ac4 no deberian aparecer en el universo generico
        if det_280(co):
            return "ART_280", "sanity_280_en_generico", co
        if det_ac4(co):
            return "ACORDADA_4_2007", "sanity_ac4_en_generico", co
        # 1. cola anclada (especifico gana)
        for name, cfg in COLA.items():
            if cfg["gate_only"] and x["outcome"] not in GATE_STRICT:
                continue
            m = cfg["rx"].search(txt)
            if m and not (cfg["excl"] and cfg["excl"].search(txt)):
                win = txt[max(0, m.start() - 50):m.end() + 50]
                return name, cfg["estado"], win
        # 2. residual partido
        dp = str(x.get("dictamen_presente", "")).strip().lower()
        if RE_REMITE.search(co) and dp in ("true", "1", "presente"):
            return "INADMISIBLE_REMITE_DICTAMEN", "residual", co[-120:]
        return "INADMISIBLE_SIN_CAUSAL_EXPLICITA", "residual", pe[:120]

    asign = collections.Counter()
    por_causal = collections.defaultdict(list)   # causal -> [(id, outcome, win)]
    ids_por_causal = collections.defaultdict(set)
    for x in sub:
        causal, estado, win = clasificar(x)
        asign[causal] += 1
        por_causal[causal].append((x["caso_id_canonico"], x["outcome"], estado, win))
        ids_por_causal[causal].add(x["caso_id_canonico"])

    # ---- reporte ----
    print(f"sub_gate.py v{__version__}  (regexes parser via {modo})")
    print(f"CSV: {csv_path}")
    print(f"universo gate-generico (outcome in {sorted(GATE_OUTCOMES)}): {len(sub)}\n")

    RALAS = 8   # umbral: si una causal tiene <= RALAS hits, muestreo exhaustivo
    print("=== causal asignada ===")
    for causal, n in asign.most_common():
        est = next((c["estado"] for k, c in COLA.items() if k == causal), "—")
        print(f"  {causal:34} {n:>5}   [{est}]")

    print("\n=== muestreo (exhaustivo si <= {} hits, si no 5) ===".format(RALAS))
    for causal in COLA:
        hits = por_causal.get(causal, [])
        if not hits:
            print(f"\n--- {causal}: 0 ---")
            continue
        cap = len(hits) if len(hits) <= RALAS else 5
        print(f"\n--- {causal}: {len(hits)} (estado {COLA[causal]['estado']}) ---")
        for cid, oc, est, win in hits[:cap]:
            print(f"  [{cid}] {oc:13} …{win}")

    # ---- chequeo de solapes (un caso = una causal terminal) ----
    print("\n=== solapes entre causales de cola (deberia ser 0) ===")
    cola_ids = {k: ids_por_causal.get(k, set()) for k in COLA}
    hay = False
    for a, b in itertools.combinations(cola_ids, 2):
        ov = cola_ids[a] & cola_ids[b]
        if ov:
            hay = True
            print(f"  {a} ∩ {b}: {len(ov)} -> {sorted(ov)[:5]}")
    if not hay:
        print("  (sin solapes)")

    # ---- direccion vs techo (tablero docket 2025; corpus << docket) ----
    TECHO = {"ART_280": 12546, "ACORDADA_4_2007": 4549,
             "FALTA_SENTENCIA_DEFINITIVA": 1193, "FALTA_FUNDAMENTACION_AUTONOMA": 590,
             "DEPOSITO_PREVIO": 467, "FUERA_DE_TERMINO": 287,
             "FALTA_DENEGACION_REX": 144, "SALTO_DE_INSTANCIA": 29,
             "TRIBUNAL_SUPERIOR_CAUSA": 9,
             "FALTA_INTRODUCCION_OPORTUNA_CF": 2, "FALTA_RELACION_DIRECTA": 1}
    print("\n=== direccion vs techo (perforar el techo = bug, no hallazgo) ===")
    print(f"  {'causal':34} {'corpus':>7} {'docket25':>9}")
    for k, t in TECHO.items():
        c = asign.get(k, 0)
        flag = "  <-- PERFORA" if c > t else ""
        print(f"  {k:34} {c:>7} {t:>9}{flag}")

    # ---- dump opcional para validacion manual ----
    if args.dump:
        out = Path(args.dump)
        with open(out, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["caso_id", "causal", "estado", "outcome", "snippet"])
            for causal, hits in por_causal.items():
                for cid, oc, est, win in hits:
                    w.writerow([cid, causal, est, oc, win])
        print(f"\n[dump] {out}  ({sum(len(v) for v in por_causal.values())} filas)")


if __name__ == "__main__":
    main()
