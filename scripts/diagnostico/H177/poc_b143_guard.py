#!/usr/bin/env python3
r"""
poc_b143_guard.py — verificador bimodal del guard B143 (H177). READ-ONLY.
==========================================================================
Ubicación canónica: scripts/diagnostico/H177/poc_b143_guard.py
Uso (desde la raíz del repo):
    python scripts\diagnostico\H177\poc_b143_guard.py --modo pre    # ANTES de instalar v1.15
    python scripts\diagnostico\H177\poc_b143_guard.py --modo post   # DESPUÉS de instalar v1.15

Candado de versión: PRE exige clasificador_disposicion v1.14 en disco; POST exige
v1.15. Cualquier otra versión ABORTA (evita verificar contra la copia equivocada,
lección H175).

Contrato B143 (adjudicado H177, 16 lecturas contra el .md):
  - Flip-set EXACTO = 15 (si→no), 0 no→si. 330_p399 (sustitutiva con absolución)
    y 333_p405 (disp=revoca) quedan si.
  - gate=si: 2950 → 2935 · divergencia M39: 216 → 227 · parser 0 ripple.
POST tolera dos estados del recursos.csv publicado: pre-re-derivar (diff = los 15
exactos) o post-re-derivar (diff = 0). Cualquier otro diff = [FAIL].
"""
import argparse, sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent          # scripts/diagnostico/H177/
ROOT = HERE.parents[2]                           # raíz del repo
sys.path.insert(0, str(ROOT / "scripts" / "pipeline"))
import clasificador_disposicion as cd

CASOS    = ROOT / "output" / "parser" / "csjn_casos.csv"
TEXTOS   = ROOT / "output" / "parser" / "csjn_casos_textos.csv"
RECURSOS = ROOT / "output" / "parser" / "csjn_casos_recursos.csv"

FLIP_SET = {  # 15 FP adjudicados H177 (procesal bajo el criterio de codebook H176)
    "329_p1794", "330_p487", "330_p1169", "330_p4925", "330_p5052",
    "332_p1823", "333_p1671", "334_p1458", "337_p97", "339_p656",
    "344_p163", "344_p1259", "345_p191", "347_p327", "348_p1152",
}
ANCLAS_SI = {"330_p399", "333_p405"}   # deben quedar gate=si en POST

def cargar():
    c = pd.read_csv(CASOS, dtype=str, keep_default_na=False)[
        ["caso_id_canonico", "is_merit_decision", "is_originaria"]]
    t = pd.read_csv(TEXTOS, dtype=str, keep_default_na=False)[
        ["caso_id_canonico", "por_ello_text", "considerando_text"]]
    r = pd.read_csv(RECURSOS, dtype=str, keep_default_na=False)[
        ["caso_id_canonico", "disposicion", "es_revision_fondo"]]
    return c.merge(t, on="caso_id_canonico").merge(r, on="caso_id_canonico")

def recomputar_gate(df):
    return [cd.es_revision_fondo(d, pe, o == "1", co)
            for d, pe, o, co in zip(df.disposicion, df.por_ello_text,
                                    df.is_originaria, df.considerando_text)]

def falla(msg):
    print(f"[FAIL] {msg}"); sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["pre", "post"], required=True)
    modo = ap.parse_args().modo

    esperado = {"pre": "1.14", "post": "1.15"}[modo]
    if cd.__version__ != esperado:
        falla(f"candado de versión: modo {modo} exige clasificador v{esperado}, "
              f"en disco hay v{cd.__version__}. ABORTA.")
    print(f"[OK] candado: clasificador_disposicion v{cd.__version__} (modo {modo})")

    df = cargar()
    if len(df) != 5890:
        falla(f"merge = {len(df)} filas, esperado 5890")

    import re
    ALT = re.compile(r"\bnulidad\s+de\s+todo\s+lo\s+actuado\b", re.I)
    hits = {row.caso_id_canonico for row in df.itertuples()
            if row.disposicion == "nulidad" and ALT.search(cd.norm(row.por_ello_text))}
    if hits != FLIP_SET | {"330_p399"}:
        falla(f"superficie del alt∩nulidad = {len(hits)}, difiere del set adjudicado: "
              f"{sorted(hits ^ (FLIP_SET | {'330_p399'}))}")
    print(f"[OK] superficie del alt∩disp=nulidad = 16 (los adjudicados)")

    df["gate_re"] = recomputar_gate(df)
    gate_si = (df.gate_re == "si").sum()
    div = ((df.is_merit_decision == "1") != (df.gate_re == "si")).sum()
    diff = df[df.es_revision_fondo != df.gate_re]
    diff_ids = set(diff.caso_id_canonico)

    if modo == "pre":
        # v1.14 debe reproducir el estado publicado EXACTO (0 diffs) y las métricas selladas
        if diff_ids:
            falla(f"v1.14 no reproduce el publicado: {len(diff_ids)} diffs: {sorted(diff_ids)[:10]}")
        if gate_si != 2950 or div != 216:
            falla(f"métricas PRE: gate=si {gate_si} (esp. 2950), divergencia {div} (esp. 216)")
        publicado = df.set_index("caso_id_canonico").es_revision_fondo
        malos = [cid for cid in FLIP_SET | {"330_p399"} if publicado[cid] != "si"]
        if malos:
            falla(f"premisa B143 rota: no están todos gate=si en el publicado: {malos}")
        print("[OK] PRE: 0 diffs vs publicado · gate=si 2950 · divergencia 216 · los 16 en si")
        print("[PRE VERDE] premisas B143 verificadas. Instalar v1.15 y correr --modo post.")
    else:
        if gate_si != 2935 or div != 227:
            falla(f"métricas POST: gate=si {gate_si} (esp. 2935), divergencia {div} (esp. 227)")
        g = df.set_index("caso_id_canonico").gate_re
        if any(g[cid] != "no" for cid in FLIP_SET):
            falla(f"flip-set incompleto: {[c for c in FLIP_SET if g[c] != 'no']}")
        if any(g[cid] != "si" for cid in ANCLAS_SI):
            falla(f"ancla rota: {[c for c in ANCLAS_SI if g[c] != 'si']}")
        if diff_ids == FLIP_SET:
            print("[OK] POST (pre-re-derivar): diff vs publicado = los 15 exactos, 0 extras")
            print("[POST VERDE] Falta: re-derivar recursos → re-correr este PoC (diff debe dar 0) → build_m20 → manifest.")
        elif not diff_ids:
            print("[OK] POST (post-re-derivar): publicado ya coincide con v1.15 (0 diffs)")
            print("[POST VERDE] Sellado del deriver consistente. Siguen: build_m20 (candado) + manifest.")
        else:
            falla(f"diff inesperado ({len(diff_ids)}): fuera del flip-set: "
                  f"{sorted(diff_ids ^ FLIP_SET)[:10]}")
        print(f"[OK] métricas POST: gate=si 2935 · divergencia 227 · 399/405 en si")

if __name__ == "__main__":
    main()
