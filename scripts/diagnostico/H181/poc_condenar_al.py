# -----------------------------------------------------------------------------
# poc_condenar_al.py v0.1 — H181 · micro-unidad candidata: ensanche
# «condenar a» → «condenar al?» en RE_FONDO_EXTRA_GRANT (es_de_fondo / gate)
#
# PoC READ-ONLY. Origen: adjudicación B135(c) — 348_p1686 (Equística) es
# originaria de FONDO real («Por ello, se resuelve: Condenar al Estado
# Nacional... a implementar y ejecutar el Plan Integral Estratégico») pero
# es_de_fondo=0 porque \bcondenar\s+a\b exige frontera tras la «a» y la
# contracción «al» la rompe (clasificador L328-332, verificado H181).
#
# El ensanche es ESTRICTAMENTE ADITIVO a nivel regex (todo match viejo sigue
# matcheando → no puede haber si→no). Lo que se mide y se LEE son los no→si:
# cada uno puede ser TP (fondo real tipo Equística) o FP (p.ej. «Condenar al
# pago de las costas» en una originaria resuelta por otra vía).
#
# Universo = originarias publicadas (589) ∪ los 6 flips adjudicados de B135(c)
# (= las 595 del estado post-v24.1: es_de_fondo solo se evalúa en la rama
# originaria del gate — fuera de ese universo el ensanche tiene efecto 0 hoy).
# Dato informativo aparte: cuántos «condenar al» hay en pe de NO-originarias
# (superficie futura si algún día el gate leyera resolución directa apelada).
#
# Anclas:
#   A0  identidad — gate v1.15 recomputado sobre el universo == is_merit
#       publicado en las 589 (0 diffs) y == lo adjudicado en los 6 de B135c.
#   A1  aditividad — 0 flips si→no (por construcción; se verifica igual).
#   A2  Equística (348_p1686) ∈ flips no→si.
#   A3  cada flip listado con excerpt del match para adjudicar por lectura.
#
# Candados: clasificador 1.15 · orig publicada 589 · merit publicado 2935.
# NOTA: corre sobre el estado SELLADO v24.0 (pre-cableado de 24.1) — por eso
# los 6 de B135c entran por lista explícita, no por columna.
#
# Uso:  python scripts/diagnostico/H181/poc_condenar_al.py
# -----------------------------------------------------------------------------
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

import pandas as pd

POC_VERSION = "0.1"
LOCK_CLASIF = "1.15"
LOCK_ORIG = 589
LOCK_MERIT = 2935
FLIPS_B135C = ["329_p3168", "329_p3403", "340_p1025",
               "342_p917", "344_p3476", "348_p1686"]
TESTIGO = "348_p1686"


def _find_root(start: Path) -> Path:
    p = start
    for _ in range(8):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
        p = p.parent
    sys.exit("[FATAL] no encuentro la raíz del repo")


ROOT = _find_root(Path(__file__).resolve().parent)
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import clasificador_disposicion as C                  # noqa: E402

# ── el ensanche bajo prueba (lo ÚNICO nuevo) ─────────────────────────────────
# v1.15 actual: ...r"|\bse\s+condena\b|\bcondenar\s+a\b"...
# candidato:                        \bcondenar\s+al?\b
RE_EXTRA_V116 = re.compile(
    C.RE_FONDO_EXTRA_GRANT.pattern.replace(
        r"\bcondenar\s+a\b", r"\bcondenar\s+al?\b"),
    re.I)
assert RE_EXTRA_V116.pattern != C.RE_FONDO_EXTRA_GRANT.pattern, \
    "el reemplazo no encontró el alt esperado — el clasificador cambió, revisar"
RE_CONDENAR_AL = re.compile(r"\bcondenar\s+al\b|\bcondena\w*\s+al\b", re.I)


def gate(pe, cons, con_ensanche):
    """es_revision_fondo REAL con is_originaria=True; el ensanche entra por
    swap controlado del objeto compilado (misma lógica, una sustitución)."""
    orig = C.RE_FONDO_EXTRA_GRANT
    try:
        if con_ensanche:
            C.RE_FONDO_EXTRA_GRANT = RE_EXTRA_V116
        disp, _ = C.disposicion(pe)
        return C.es_revision_fondo(disp, pe, True, cons)
    finally:
        C.RE_FONDO_EXTRA_GRANT = orig


def main():
    print(f"poc_condenar_al v{POC_VERSION} — repo: {ROOT}")
    if C.__version__ != LOCK_CLASIF:
        sys.exit(f"[FATAL] candado: clasificador {C.__version__} != {LOCK_CLASIF}")

    casos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos.csv")
    textos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos_textos.csv")
    df = casos.merge(
        textos[["caso_id_canonico", "considerando_text", "por_ello_text"]],
        on="caso_id_canonico", how="left")
    for col in ("considerando_text", "por_ello_text"):
        df[col] = df[col].fillna("")

    n_orig, n_merit = int(df.is_originaria.sum()), int(df.is_merit_decision.sum())
    if n_orig != LOCK_ORIG or n_merit != LOCK_MERIT:
        sys.exit(f"[FATAL] candado de estado: orig={n_orig} merit={n_merit} "
                 f"(esp {LOCK_ORIG}/{LOCK_MERIT}) — ¿ya corriste v24.1? este PoC "
                 f"es pre-cableado; si el estado es post-24.1 avisar y se recalza")
    print(f"[candados] clasif {LOCK_CLASIF} · orig {n_orig} · merit {n_merit}  [OK]")

    uni = df[(df.is_originaria == 1)
             | df.caso_id_canonico.isin(FLIPS_B135C)].copy()
    print(f"[universo] originarias publicadas + 6 B135c = {len(uni)}")

    # ── A0: identidad del gate v1.15 sobre el universo ──────────────────────
    uni["gate_pre"] = uni.apply(
        lambda r: gate(r.por_ello_text, r.considerando_text, False), axis=1)
    pub = uni[uni.is_originaria == 1]
    diffs = pub[(pub.gate_pre == "si").astype(int) != pub.is_merit_decision]
    if len(diffs):
        print(f"[A0] FAIL — gate recomputado != is_merit publicado en "
              f"{len(diffs)}: {diffs.caso_id_canonico.head(10).tolist()}")
        sys.exit(2)
    esp_b135c = {c: ("no" if c == TESTIGO else "si") for c in FLIPS_B135C}
    b135c_ok = all(
        uni.loc[uni.caso_id_canonico == c, "gate_pre"].iloc[0] == v
        for c, v in esp_b135c.items())
    print(f"[A0] identidad gate==publicado (589: 0 diffs) y ==adjudicado "
          f"(6 B135c): {'[OK]' if b135c_ok else '[FAIL]'}")

    # ── POST con ensanche ────────────────────────────────────────────────────
    uni["gate_post"] = uni.apply(
        lambda r: gate(r.por_ello_text, r.considerando_text, True), axis=1)
    perdidas = uni[(uni.gate_pre == "si") & (uni.gate_post == "no")]
    print(f"[A1] aditividad — flips si→no: {len(perdidas)} "
          f"{'[OK]' if len(perdidas) == 0 else '[FAIL] ' + str(perdidas.caso_id_canonico.tolist())}")

    flips = uni[(uni.gate_pre == "no") & (uni.gate_post == "si")]
    a2 = TESTIGO in set(flips.caso_id_canonico)
    print(f"[A2] testigo {TESTIGO} ∈ flips: {'[OK]' if a2 else '[FAIL]'}")

    # informativo: superficie fuera del universo (efecto 0 hoy)
    fuera = df[(df.is_originaria == 0)
               & ~df.caso_id_canonico.isin(FLIPS_B135C)
               & df.por_ello_text.str.contains(RE_CONDENAR_AL, na=False)]
    print(f"[info] «condenar/condena al» en pe de NO-originarias: {len(fuera)} "
          f"(efecto 0 hoy: es_de_fondo no corre ahí)")

    print(f"\n[FLIP-SET ensanche] = {len(flips)} — ADJUDICAR POR LECTURA cada uno:")
    for _, r in flips.iterrows():
        pe = C.norm(r.por_ello_text)
        m = RE_EXTRA_V116.search(pe)
        exc = pe[max(0, m.start() - 60):m.end() + 140].strip() if m else "(?)"
        print(f"\n  {r.caso_id_canonico}  (B135c-flip: "
              f"{'sí' if r.caso_id_canonico in FLIPS_B135C else 'no'})")
        print(f"    {exc}")

    print(f"\n[ripple predicho si 6/6+adjudicación limpia] "
          f"is_merit +{len(flips)} sobre el estado post-24.1")
    sys.exit(0 if (b135c_ok and len(perdidas) == 0 and a2) else 2)


if __name__ == "__main__":
    main()
