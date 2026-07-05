# -----------------------------------------------------------------------------
# poc_b139b_guard.py v0.1 — H181 · unidad B (B139b): guard sentencia-sustitutiva
#
# PoC READ-ONLY, bimodal (PRE = v1.16 publicado / POST = guard candidato v1.17).
# Guard (dirección INVERSA a B138/B143 — fuerza 'si'):
#     disp == "no_revision_demanda" ∧ ¬is_originaria ∧ (S1 ∨ S2)
#   S1: art. 16 ∧ ley 48 en el pe  («se rechaza la demanda, art. 16, segunda
#       parte, de la ley 48» — la sentencia sustitutiva citada)
#   S2: concesión-de-recurso ∧ «rechaza … demanda» en el MISMO pe
#       («se hace lugar a la queja, se declara procedente el recurso … y se
#       rechaza la demanda» — 332_p2559, sustitutiva SIN cita del art. 16)
#
# Adjudicado en sesión (9 lecturas, criterio confirmado por Guillermo):
#   6 TP → flip esperado: 331_p100 (testigo H170), 337_p1174 (Google),
#          343_p1259 (FADEEAC, TP-con-asterisco), 344_p277, 348_p895
#          (Defensor del Pueblo), 332_p2559 (sin art.16 → motiva S2)
#   3 aciertos → NO deben flipear: 330_p3160 (Bussi, inoficioso),
#          331_p530 (Cóspito, acceso), 332_p2237 (incidental)
#
# Universo del guard = TODAS las no_revision_demanda ∧ ¬orig (no solo las 9
# de via=REX): el PoC mide el flip-set corpus-wide; todo flip FUERA de los 6
# se adjudica por lectura antes de cablear.
#
# Anclas:
#   A0  identidad — gate v1.16 recomputado == es_revision_fondo publicado
#       (recursos.csv, 0 diffs sobre las 181; corte barato del round-trip).
#   A1  aditividad — 0 flips si→no (por construcción; verificado igual).
#   A2  los 6 TP ⊆ flip-set.
#   A3  los 3 aciertos ∉ flip-set.
#   A4  reporte de TODO flip extra con excerpt, para adjudicar.
#
# Candados: parser 24.1 · clasif 1.16 · orig 595 · merit 2941.
# Uso:  python scripts/diagnostico/H181/poc_b139b_guard.py
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
LOCK_PARSER = "24.0/24.1"  # informativo; el candado duro es clasif + estado
LOCK_CLASIF = "1.16"
LOCK_ORIG = 595
LOCK_MERIT = 2941
TP = ["331_p100", "337_p1174", "343_p1259", "344_p277", "348_p895", "332_p2559"]
ACIERTOS = ["330_p3160", "331_p530", "332_p2237"]


def _find_root(start: Path) -> Path:
    p = start
    for _ in range(8):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
        p = p.parent
    sys.exit("[FATAL] raíz no encontrada")


ROOT = _find_root(Path(__file__).resolve().parent)
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))

import clasificador_disposicion as C  # noqa: E402

# ── el guard candidato (lo ÚNICO nuevo; opera sobre norm(pe) como el gate) ───
RE_B139B_S1_ART16 = re.compile(r"art[íi]?c?u?l?o?s?\.?\s*16\b", re.I)
RE_B139B_S1_LEY48 = re.compile(r"ley\s*48", re.I)
RE_B139B_S2_GRANT = re.compile(
    r"hace\w*\s+lugar\s+a\s+la\s+queja"
    r"|declar\w+\s+(?:procedente|admisible)s?\s+(?:el|los)\s+recurso", re.I)
RE_B139B_S2_RECHAZA_DEM = re.compile(
    r"rechaz\w+\s+la\s+demanda", re.I)


def guard_b139b(pe_norm: str) -> bool:
    s1 = bool(RE_B139B_S1_ART16.search(pe_norm) and RE_B139B_S1_LEY48.search(pe_norm))
    s2 = bool(RE_B139B_S2_GRANT.search(pe_norm) and RE_B139B_S2_RECHAZA_DEM.search(pe_norm))
    return s1 or s2


def main():
    print(f"poc_b139b_guard v{POC_VERSION} — repo: {ROOT}")
    if C.__version__ != LOCK_CLASIF:
        sys.exit(f"[FATAL] candado: clasificador {C.__version__} != {LOCK_CLASIF}")

    casos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos.csv")
    recursos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos_recursos.csv")
    textos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos_textos.csv")
    if int(casos.is_originaria.sum()) != LOCK_ORIG or \
       int(casos.is_merit_decision.sum()) != LOCK_MERIT:
        sys.exit("[FATAL] candado de estado: orig/merit no calzan con el sello v24.1")
    print(f"[candados] clasif {LOCK_CLASIF} · orig {LOCK_ORIG} · merit {LOCK_MERIT}  [OK]")

    nd = (recursos[recursos.disposicion == "no_revision_demanda"]
          .merge(casos[["caso_id_canonico", "is_originaria", "is_merit_decision"]],
                 on="caso_id_canonico")
          .merge(textos[["caso_id_canonico", "por_ello_text", "considerando_text"]],
                 on="caso_id_canonico"))
    for col in ("por_ello_text", "considerando_text"):
        nd[col] = nd[col].fillna("")
    print(f"[universo] no_revision_demanda: {len(nd)} "
          f"(¬orig: {int((nd.is_originaria == 0).sum())})")

    # ── A0: identidad del gate publicado (round-trip sobre las 181) ─────────
    def gate_pre(r):
        disp, _ = C.disposicion(r.por_ello_text)
        return C.es_revision_fondo(disp, r.por_ello_text,
                                   bool(r.is_originaria), r.considerando_text)
    nd["gate_pre"] = nd.apply(gate_pre, axis=1)
    diffs = nd[nd.gate_pre != nd.es_revision_fondo]
    if len(diffs):
        print(f"[A0] FAIL — {len(diffs)} diffs vs recursos.csv: "
              f"{diffs.caso_id_canonico.head(10).tolist()}")
        sys.exit(2)
    print(f"[A0] identidad gate v1.16 == publicado: 0 diffs sobre {len(nd)}  [OK]")

    # ── POST: gate + guard candidato ─────────────────────────────────────────
    nd["pe_norm"] = nd.por_ello_text.map(C.norm)
    nd["guard"] = nd.pe_norm.map(guard_b139b) & (nd.is_originaria == 0)
    nd["gate_post"] = nd.gate_pre.where(~nd.guard, "si")

    perdidas = nd[(nd.gate_pre == "si") & (nd.gate_post == "no")]
    print(f"[A1] pérdidas si→no: {len(perdidas)}  "
          f"{'[OK]' if len(perdidas) == 0 else '[FAIL]'}")

    flips = nd[(nd.gate_pre == "no") & (nd.gate_post == "si")]
    ids = set(flips.caso_id_canonico)
    a2 = all(t in ids for t in TP)
    a3 = all(a not in ids for a in ACIERTOS)
    print(f"[A2] 6 TP ⊆ flips: {'[OK]' if a2 else '[FAIL] faltan ' + str(set(TP) - ids)}")
    print(f"[A3] 3 aciertos fuera: {'[OK]' if a3 else '[FAIL] ' + str(ids & set(ACIERTOS))}")

    extras = flips[~flips.caso_id_canonico.isin(TP)]
    print(f"\n[FLIP-SET] = {len(flips)}  (esperado 6; extras a adjudicar: {len(extras)})")
    for _, r in flips.iterrows():
        s1 = bool(RE_B139B_S1_ART16.search(r.pe_norm) and RE_B139B_S1_LEY48.search(r.pe_norm))
        tag = "TP adjudicado" if r.caso_id_canonico in TP else ">>> EXTRA: LEER Y ADJUDICAR"
        print(f"\n  {r.caso_id_canonico}  señal={'S1' if s1 else 'S2'}  [{tag}]")
        print(f"    pe: {r.pe_norm[:220]}")

    print(f"\n[ripple predicho] is_merit {LOCK_MERIT} → {LOCK_MERIT + len(flips)} "
          f"(+{len(flips)}) — ambas capas por construcción (parser importa el gate)")
    sys.exit(0 if (len(perdidas) == 0 and a2 and a3) else 2)


if __name__ == "__main__":
    main()
