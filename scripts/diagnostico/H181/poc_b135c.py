# -----------------------------------------------------------------------------
# poc_b135c.py v0.1 — H181 · B135(c) Ruta R: señal compuesta de is_originaria
#
# PoC READ-ONLY (no escribe canónicos; solo un CSV de flips en su propio dir).
# Patrón poc_b135_flips (H172) / poc_paso3_m39 (H178): importa los detectores
# REALES del parser (Gate 3) y mide en disco, sobre el corpus real, el flip-set
# corpus-wide de la señal compuesta ANTES de tocar el parser.
#
# Señal R (adjudicada en sesión, 2 objetivos: 329_p3403 Ferrari, 344_p3476 Coihue):
#   case_name_cuerpo marca demanda-contra-Estado/Provincia
#       (RE_CN_DEMANDA_ESTADO huérfana del parser ∪ forma INVERTIDA
#        «c/ <Nombre>, Provincia de» — Ferrari L191, Coihue L499)
#   ∧ _orig_pelada_con_guards (reusada INTACTA, 4 guards H172) sobre la
#       ventana RESULTA: bloque[apertura(RE_VISTOS) → primer RE_CONSIDERANDO),
#       normalizada con el MISMO orden de es_originaria (mask RE_RUNNING_HEAD
#       → _unhyphenate).
#   Ruta D (dispositivo) DESCARTADA en sesión: su único testigo (348_p473)
#   resultó fila fantasma (slice de 348_p461, que ya tiene orig=1/merit=1).
#
# Anclas:
#   A0  identidad — es_originaria replicada sobre casos⨝textos == columna
#       publicada (0 diffs). Si falla, NADA de lo que sigue vale.
#   A1  {329_p3403, 344_p3476} ⊆ flip-set.
#   A2  aditividad — solo se evalúan filas publicadas en 0 (por construcción);
#       los 4 FP-F5 aceptados de H172 siguen en 1, intactos.
#   A3  pool — tamaño del pool case_name-compuesto (descendiente del 275/H156)
#       y cuántos pasan la corroboración (precisión de la compuesta a la vista).
#   A4  gate preview — para CADA flip, es_revision_fondo(disp, pe, True, cons):
#       predice el ripple de is_merit (los 2 objetivos deben dar 'si').
#
# Candados de versión/estado (aborta si no calzan): parser 24.0 ·
# clasificador_disposicion 1.15 · is_originaria=589 · is_merit_decision=2935.
#
# Uso (desde cualquier subdir del repo):
#   python scripts/diagnostico/H181/poc_b135c.py
# Salida: consola + scripts/diagnostico/H181/poc_b135c_flips.csv
# -----------------------------------------------------------------------------
import csv
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")   # lección H174: la consola no mata la corrida
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

import pandas as pd

POC_VERSION = "0.1"
LOCK_PARSER = "24.0"
LOCK_CLASIF = "1.15"
LOCK_ORIG = 589
LOCK_MERIT = 2935
TARGETS = ["329_p3403", "344_p3476"]
FP_F5 = ["349_p163", "347_p2146", "347_p2286", "334_p1842"]


def _find_root(start: Path) -> Path:
    p = start
    for _ in range(8):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
        p = p.parent
    sys.exit("[FATAL] no encuentro la raíz del repo (marcador scripts/pipeline/parser.py)")


ROOT = _find_root(Path(__file__).resolve().parent)
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import parser as P                                    # noqa: E402
from clasificador_disposicion import (                # noqa: E402
    __version__ as CLASIF_VERSION, disposicion, es_revision_fondo, es_de_fondo,
)

# ── señal nueva del PoC (lo ÚNICO que no existe en el parser) ────────────────
# Forma invertida de Fallos: «X c/ Entre Ríos, Provincia de y otros»,
# «Coihue S.R.L. c/ Santa Cruz, Provincia de s/ ...». La huérfana
# RE_CN_DEMANDA_ESTADO no la cubre (verificado L1299-1305, H181).
RE_CN_INVERTIDA = re.compile(r"c/\s*[^,/]{1,80},\s*Provincia\s+de\b", re.I)


def case_name_compuesto(cn: str) -> bool:
    if not cn:
        return False
    return bool(P.RE_CN_DEMANDA_ESTADO.search(cn) or RE_CN_INVERTIDA.search(cn))


def norm_ventana(lineas) -> str:
    """MISMO orden de normalización que es_originaria (L1377-1379):
    join → mask RE_RUNNING_HEAD → _unhyphenate."""
    t = " ".join(lineas)
    t = P.RE_RUNNING_HEAD.sub(" ", t)
    return P._unhyphenate(t)


def ventana_resulta(bloque):
    """bloque[apertura(RE_VISTOS) → primer RE_CONSIDERANDO). None si falta
    cualquiera de las dos anclas (conservador: sin ventana no hay flip)."""
    ap = None
    for i, ln in enumerate(bloque):
        if P.RE_VISTOS.match(ln):
            ap = i
            break
    if ap is None:
        return None, "sin_apertura"
    for j in range(ap + 1, len(bloque)):
        if P.RE_CONSIDERANDO.search(bloque[j].strip()):
            return bloque[ap:j], "ok"
    return None, "sin_considerando"


def match_sobreviviente(w: str):
    """Primer match de RE_ORIG_PELADA que sobrevive a los guards. Replica el
    LOOP de _orig_pelada_con_guards usando los MISMOS objetos compilados del
    parser (solo para ubicar el excerpt; la decisión de flip la toma la
    función real)."""
    for m in P.RE_ORIG_PELADA.finditer(w):
        post = w[m.end():]
        pre = w[max(0, m.start() - P._ORIG_W_PROV):m.start()]
        if (P.RE_ORIG_G_LOCAL.search(post) or P.RE_ORIG_G_APELADA.search(post)
                or P.RE_ORIG_G_PRECEDENTE.search(post)
                or P.RE_ORIG_G_PROVINCIAL.search(pre)):
            continue
        return m
    return None


def main():
    print(f"poc_b135c v{POC_VERSION} — repo: {ROOT}")

    # ── candados ─────────────────────────────────────────────────────────────
    if P.__version__ != LOCK_PARSER:
        sys.exit(f"[FATAL] candado: parser {P.__version__} != {LOCK_PARSER}")
    if CLASIF_VERSION != LOCK_CLASIF:
        sys.exit(f"[FATAL] candado: clasificador {CLASIF_VERSION} != {LOCK_CLASIF}")

    casos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos.csv")
    textos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos_textos.csv")
    df = casos.merge(
        textos[["caso_id_canonico", "considerando_text", "por_ello_text"]],
        on="caso_id_canonico", how="left")
    for col in ("case_name_cuerpo", "considerando_text", "por_ello_text"):
        df[col] = df[col].fillna("")

    n_orig = int(df.is_originaria.sum())
    n_merit = int(df.is_merit_decision.sum())
    if n_orig != LOCK_ORIG or n_merit != LOCK_MERIT:
        sys.exit(f"[FATAL] candado de estado: orig={n_orig} (esp {LOCK_ORIG}) "
                 f"merit={n_merit} (esp {LOCK_MERIT})")
    print(f"[candados] parser {LOCK_PARSER} · clasif {LOCK_CLASIF} · "
          f"orig {n_orig} · merit {n_merit}  [OK]")

    # ── A0: identidad de la réplica ─────────────────────────────────────────
    replica = df.apply(lambda r: int(P.es_originaria(
        r.case_name_cuerpo, r.considerando_text, r.por_ello_text)), axis=1)
    diffs = df[replica != df.is_originaria]
    if len(diffs):
        print(f"[A0] FAIL — réplica != publicada en {len(diffs)} filas: "
              f"{diffs.caso_id_canonico.head(10).tolist()}")
        sys.exit(2)
    print(f"[A0] identidad réplica==publicada: 0 diffs sobre {len(df)}  [OK]")

    # ── A2 (parte fija): los 4 FP-F5 intactos en 1 ──────────────────────────
    f5 = df[df.caso_id_canonico.isin(FP_F5)]
    ok_f5 = len(f5) == 4 and int(f5.is_originaria.sum()) == 4
    print(f"[A2] FP-F5 en 1 e intocados (solo se evalúan publicadas=0): "
          f"{'[OK]' if ok_f5 else '[FAIL] ' + f5.to_string()}")

    # ── pool y ventanas ──────────────────────────────────────────────────────
    pool = df[(df.tipo_entrada == "fallo") & (df.is_originaria == 0)
              & df.case_name_cuerpo.map(case_name_compuesto)].copy()
    print(f"[A3] pool case_name-compuesto ∧ orig=0: {len(pool)} "
          f"(descendiente del 275/H156; invertida sola: "
          f"{int(pool.case_name_cuerpo.map(lambda c: bool(RE_CN_INVERTIDA.search(c)) and not bool(P.RE_CN_DEMANDA_ESTADO.search(c))).sum())})")

    flips, sin_ventana = [], {"sin_apertura": 0, "sin_considerando": 0}
    cache = {}
    for _, r in pool.iterrows():
        sf = r.source_file
        if sf not in cache:
            fp = ROOT / "corpus" / sf
            if not fp.exists():
                sys.exit(f"[FATAL] falta corpus/{sf}")
            cache[sf] = fp.read_text(encoding="utf-8").splitlines()
        li, lfr = int(r.linea_inicio), int(r.linea_fin_real)
        bloque = cache[sf][li:lfr + 1]          # 0-indexed, inclusive (conv. extraer_caso)
        ventana, status = ventana_resulta(bloque)
        if ventana is None:
            sin_ventana[status] += 1
            continue
        w = norm_ventana(ventana)
        if not P._orig_pelada_con_guards(w):
            continue
        m = match_sobreviviente(w)
        exc = (w[max(0, m.start() - 110):m.end() + 110].strip()
               if m else "(match no relocalizado)")
        disp, _ = disposicion(r.por_ello_text)
        gate = es_revision_fondo(disp, r.por_ello_text, True, r.considerando_text)
        flips.append({
            "caso_id_canonico": r.caso_id_canonico, "tomo": r.tomo,
            "case_name": (r.case_name_cuerpo or "")[:90],
            "outcome": r.outcome, "is_merit_actual": int(r.is_merit_decision),
            "gate_si_orig": gate, "es_de_fondo": int(es_de_fondo(
                r.considerando_text, r.por_ello_text)),
            "merit_predicho": int(gate == "si"), "excerpt": exc,
        })

    print(f"[A3] con ventana Resulta evaluada: {len(pool) - sum(sin_ventana.values())} "
          f"(sin apertura {sin_ventana['sin_apertura']} / "
          f"sin Considerando {sin_ventana['sin_considerando']})")
    print(f"\n[FLIP-SET Ruta R] = {len(flips)}")

    ids = {f["caso_id_canonico"] for f in flips}
    a1 = all(t in ids for t in TARGETS)
    print(f"[A1] objetivos ⊆ flips: {'[OK]' if a1 else '[FAIL] faltan ' + str(set(TARGETS) - ids)}")
    a4 = all(f["gate_si_orig"] == "si" for f in flips if f["caso_id_canonico"] in TARGETS)
    print(f"[A4] gate='si' en los 2 objetivos (recupero de is_merit de punto único): "
          f"{'[OK]' if a1 and a4 else '[FAIL]'}")
    dm = sum(f["merit_predicho"] - f["is_merit_actual"] for f in flips)
    print(f"[ripple predicho] is_originaria {n_orig}→{n_orig + len(flips)} · "
          f"is_merit {n_merit}→{n_merit + dm} ({dm:+d})")

    out = Path(__file__).resolve().parent / "poc_b135c_flips.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(flips[0].keys()) if flips
                             else ["caso_id_canonico"], lineterminator="\n")
        wtr.writeheader()
        wtr.writerows(flips)
    print(f"\n[out] {out}  ({len(flips)} filas)")
    print("\nCada flip fuera de {329_p3403, 344_p3476} se ADJUDICA POR LECTURA "
          "antes de cablear nada (extraer_caso + excerpt del CSV).")
    for f in flips:
        marca = " <== objetivo" if f["caso_id_canonico"] in TARGETS else ""
        print(f"  {f['caso_id_canonico']:>10}  gate={f['gate_si_orig']:>2} "
              f"merit {f['is_merit_actual']}→{f['merit_predicho']}  "
              f"{f['case_name'][:60]}{marca}")

    sys.exit(0 if (a1 and a4 and ok_f5) else 2)


if __name__ == "__main__":
    main()
