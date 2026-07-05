# dump_diff_h181c.py v0.1 — H181 unidad C: tabla de adjudicación del diff v25.0
# Emite scripts/diagnostico/H181/diff_c_adjudicacion.csv con una fila por caso
# tocado (golden vs producción): flips de outcome/is_merit/is_originaria/
# es_queja/queja_resultado + pe viejo (cola) y pe nuevo (300c) para leer.
import sys
from pathlib import Path
import pandas as pd

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass


def _find_root(start):
    p = start
    for _ in range(8):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
        p = p.parent
    sys.exit("[FATAL] raíz no encontrada")


ROOT = _find_root(Path(__file__).resolve().parent)
G = ROOT / "scripts" / "tests" / "golden"
P = ROOT / "output" / "parser"

gc = pd.read_csv(G / "csjn_casos.csv").set_index("caso_id_canonico")
nc = pd.read_csv(P / "csjn_casos.csv").set_index("caso_id_canonico")
gt = pd.read_csv(G / "csjn_casos_textos.csv").set_index("caso_id_canonico")
nt = pd.read_csv(P / "csjn_casos_textos.csv").set_index("caso_id_canonico")

cols = ["outcome", "is_merit_decision", "is_originaria", "es_queja",
        "queja_resultado", "tribunal_origen_status"]
dif_casos = (gc[cols].fillna("").astype(str) != nc[cols].fillna("").astype(str)).any(axis=1)
dif_pe = (gt.por_ello_text.fillna("") != nt.por_ello_text.fillna(""))
tocados = sorted(set(gc.index[dif_casos]))

rows = []
for cid in tocados:
    g, n = gc.loc[cid], nc.loc[cid]
    pev = str(gt.loc[cid, "por_ello_text"] or "")
    pen = str(nt.loc[cid, "por_ello_text"] or "")
    rows.append({
        "caso": cid,
        "outcome": f"{g.outcome}->{n.outcome}" if g.outcome != n.outcome else "",
        "merit": f"{g.is_merit_decision}->{n.is_merit_decision}"
                 if g.is_merit_decision != n.is_merit_decision else "",
        "orig": f"{g.is_originaria}->{n.is_originaria}"
                if g.is_originaria != n.is_originaria else "",
        "queja": (f"{g.queja_resultado}->{n.queja_resultado}"
                  if str(g.queja_resultado) != str(n.queja_resultado) else ""),
        "pe_cambio": "si" if pev != pen else "no",
        "pe_viejo_cola": pev[-160:],
        "pe_nuevo_300": pen[:300],
        "pe_nuevo_cola": pen[-200:],
    })

out = ROOT / "scripts" / "diagnostico" / "H181" / "diff_c_adjudicacion.csv"
pd.DataFrame(rows).to_csv(out, index=False, lineterminator="\n")
print(f"[out] {out}  ({len(rows)} casos tocados en columnas de decisión)")
print(f"[contexto] pe cambiados totales: {int(dif_pe.sum())} "
      f"(la mayoría solo higiene/extensión sin flip de columna — no van a la tabla)")
print(f"[totalidad textos] considerando cambiados: "
      f"{int((gt.considerando_text.fillna('') != nt.considerando_text.fillna('')).sum())} · "
      f"firma_raw cambiados: {int((gt.firma_raw.fillna('') != nt.firma_raw.fillna('')).sum())}")
