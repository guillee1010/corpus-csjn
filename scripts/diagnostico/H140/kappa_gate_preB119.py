#!/usr/bin/env python3
"""
kappa_gate_preB119.py - kappa(gate) LIMPIO con la prediccion del parser PRE-B119.

Contexto (H122 ledger, BITACORA 17197/17217): el gate (es_revision_fondo) es la
UNICA variable M20 contaminada por leakage. B119 (H121) se tuneo sobre el n300 ->
kappa 0,933 IN-SAMPLE. Este script recomputa kappa(gate) con la prediccion del
parser ANTERIOR a B119 (commit d856318, "checkpoint pre-B119"), que nunca vio el
gold como dev set -> kappa held-out de facto = el numero honesto para la tesis.

Regla del gate (COPIADA TAL CUAL de derivar_recursos.py v0.2):
    es_revision_fondo = "si" if is_merit_decision == "1" else "no"
Depende solo de is_merit_decision (lo que B119 movio dentro del parser); no usa
textos ni la capa de disposicion. Por eso basta recuperar is_merit pre-B119 de git
y aplicar esta regla -- no hace falta re-correr el deriver entero.

Sanity check: antes de usar la regla sobre el pre-B119, se verifica que reproduce
byte-a-byte el es_revision_fondo del recursos.csv ACTUAL. Si no, aborta.

Reusa kappa()/boot_ci()/norm()/landis_koch() del harness canonico (Gate 3).
Se corre DESDE LA RAIZ DEL REPO.

Uso (PowerShell):
  python scripts\diagnostico\H140\kappa_gate_preB119.py
"""
import sys, os, io, subprocess
import pandas as pd

REPO = os.getcwd()
HARNESS_DIR = os.path.join(REPO, "scripts", "diagnostico")
sys.path.insert(0, HARNESS_DIR)
try:
    from kappa_confiabilidad import norm, kappa, boot_ci, landis_koch
except ImportError as e:
    sys.exit(f"[ERROR] No pude importar kappa_confiabilidad desde {HARNESS_DIR}: {e}\n"
             f"Corre el script desde la raiz del repo (corpus-csjn).")

COMMIT_PRE_B119 = "d856318"   # checkpoint pre-B119
GOLD  = os.path.join("scripts", "diagnostico", "H120", "planilla_M20_LIMPIA_n300__rebuild.xlsx")
CASOS = os.path.join("output", "parser", "csjn_casos.csv")
RECUR = os.path.join("output", "parser", "csjn_casos_recursos.csv")
KEY   = "caso_id_canonico"
MERIT = "is_merit_decision"       # col del gate dentro del parser (casos.csv) - lo que B119 movio
PRED  = "es_revision_fondo"       # col del gate ya derivada (recursos.csv)
GCOL  = "cod_es_revision_fondo"   # col del gate en el gold


def gate_rule(x):
    # regla canonica literal de derivar_recursos.py v0.2
    return "si" if x == "1" else "no"


def git_blob(commit, path):
    """Recupera un blob de git como bytes, sin archivo intermedio."""
    path_posix = path.replace(os.sep, "/")
    r = subprocess.run(["git", "show", f"{commit}:{path_posix}"], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"[ERROR] git show {commit}:{path_posix} fallo:\n"
                 f"{r.stderr.decode('utf-8', 'replace')}")
    return r.stdout


def reportar(nombre, gser, pser):
    df = pd.DataFrame({"g": gser, "p": pser}).dropna()
    k, po = kappa(list(df.g), list(df.p))
    lo, hi, deg = boot_ci(list(df.g), list(df.p), B=5000)
    print(f"\n== GATE {nombre} ==")
    print(f"   n={len(df)}  acuerdo={po:.3f}  kappa={k:.3f}  "
          f"IC95=[{lo:.3f}, {hi:.3f}]  ({landis_koch(k)})  degenerados={deg*100:.1f}%")
    return k, len(df)


def main():
    # --- 1) SANITY: la regla canonica reproduce el es_revision_fondo actual? ---
    casos_now = pd.read_csv(CASOS, dtype=str, keep_default_na=False,
                            encoding="utf-8-sig", usecols=[KEY, MERIT])
    recur_now = pd.read_csv(RECUR, dtype=str, keep_default_na=False,
                            encoding="utf-8-sig", usecols=[KEY, PRED])
    chk = casos_now.merge(recur_now, on=KEY, how="inner")
    chk["regla"] = chk[MERIT].map(gate_rule)
    mism = chk[chk["regla"] != chk[PRED]]
    print(f"== Sanity: regla gate vs recursos.csv actual ==")
    print(f"   filas cruzadas={len(chk)}  mismatches={len(mism)}")
    if len(mism):
        print(mism.head(10).to_string(index=False))
        sys.exit("[ABORT] la regla copiada NO reproduce el recursos.csv actual; "
                 "revisar derivar_recursos antes de seguir.")
    print(f"   OK: la regla reproduce es_revision_fondo 1:1 "
          f"(is_merit=='1' -> 'si', resto -> 'no').")

    # --- 2) Gold n300 ---
    gold = pd.read_excel(GOLD, dtype=str)
    gold = gold[gold[KEY].notna()].set_index(KEY)
    g = gold[GCOL].map(norm)

    # --- 3) Prediccion PRE-B119: is_merit del casos pre-B119 (git) + regla canonica ---
    blob = git_blob(COMMIT_PRE_B119, CASOS)
    casos_pre = pd.read_csv(io.BytesIO(blob), dtype=str, keep_default_na=False,
                            encoding="utf-8-sig")
    if MERIT not in casos_pre.columns:
        sys.exit(f"[ERROR] La columna {MERIT} no esta en el casos.csv pre-B119 "
                 f"(commit {COMMIT_PRE_B119}). Columnas: {list(casos_pre.columns)[:8]}...")
    casos_pre = casos_pre[[KEY, MERIT]].copy()
    casos_pre["pred_pre"] = casos_pre[MERIT].map(gate_rule)
    pre = casos_pre.set_index(KEY)["pred_pre"]
    p_pre = gold.index.to_series().map(pre).map(norm)

    # --- 4) Prediccion POST-B119 (actual): check de maquinaria vs harness (~0,933) ---
    p_post = gold.index.to_series().map(recur_now.set_index(KEY)[PRED]).map(norm)

    k_post, n_post = reportar("POST-B119 (in-sample, = el de H139)", g, p_post)
    k_pre,  n_pre  = reportar("PRE-B119  (LIMPIO, held-out de facto)", g, p_pre)

    # cuantos casos flipea B119 dentro del n300
    flips = pd.DataFrame({"pre": gold.index.to_series().map(pre),
                          "post": gold.index.to_series().map(recur_now.set_index(KEY)[PRED])})
    flips = flips.dropna()
    n_flip = (flips["pre"] != flips["post"]).sum()

    print("\n== Resumen gate ==")
    print(f"   kappa reportado (post-B119, in-sample): {k_post:.3f}   (n={n_post})")
    print(f"   kappa LIMPIO    (pre-B119,  held-out):  {k_pre:.3f}   (n={n_pre})")
    print(f"   delta atribuible al leakage de B119:    {k_post - k_pre:+.3f}")
    print(f"   casos del n300 que B119 flipea:         {n_flip}")
    print("\n   Check: el kappa POST debe reproducir el 0,933 del harness oficial.")


if __name__ == "__main__":
    main()
