# -----------------------------------------------------------------------------
# poblacion_b139b.py v0.1 — H181 · unidad B (B139b)
# Población y señal por-id, EN SCRIPT (no -c): el conteo por consola dio un
# resultado irreproducible (331_p100 con match=True en test directo pero
# ausente del str.contains del one-liner — causa no identificada, transporte
# por consola sospechado y no demostrado). El dato canónico sale de acá.
#
# Emite, para disp == no_revision_demanda:
#   - señal art.16 textual en pe (regex amplia de arranque)
#   - via_recurso == recurso_extraordinario (señal ancha H176)
#   - is_originaria, is_merit_decision
# y la tabla de las candidatas (via=REX ∧ ¬originaria) con ambas señales.
# Candados: parser 24.1 · clasif 1.16 · orig 595 · merit 2941.
# -----------------------------------------------------------------------------
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

import pandas as pd


def _find_root(start: Path) -> Path:
    p = start
    for _ in range(8):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
        p = p.parent
    sys.exit("[FATAL] raíz no encontrada")


ROOT = _find_root(Path(__file__).resolve().parent)

RE_ART16 = re.compile(r"art[íi]?c?u?l?o?s?\.?\s*16\b", re.I)
RE_LEY48 = re.compile(r"ley\s*48", re.I)

casos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos.csv")
recursos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos_recursos.csv")
textos = pd.read_csv(ROOT / "output" / "parser" / "csjn_casos_textos.csv")

assert int(casos.is_originaria.sum()) == 595, "candado orig"
assert int(casos.is_merit_decision.sum()) == 2941, "candado merit"

nd = (recursos[recursos.disposicion == "no_revision_demanda"]
      .merge(casos[["caso_id_canonico", "is_originaria", "is_merit_decision"]],
             on="caso_id_canonico")
      .merge(textos[["caso_id_canonico", "por_ello_text"]],
             on="caso_id_canonico"))
nd["por_ello_text"] = nd["por_ello_text"].fillna("")
nd["art16"] = nd.por_ello_text.map(lambda s: bool(RE_ART16.search(s)))
nd["ley48"] = nd.por_ello_text.map(lambda s: bool(RE_LEY48.search(s)))
nd["via_rex"] = nd.via_recurso == "recurso_extraordinario"

print(f"no_revision_demanda: {len(nd)}")
print(f"  art16 en pe: {int(nd.art16.sum())}  "
      f"(originarias: {int(nd.loc[nd.art16, 'is_originaria'].sum())})")
print(f"  art16 ∧ ley48: {int((nd.art16 & nd.ley48).sum())}")
print(f"  via=REX: {int(nd.via_rex.sum())}  "
      f"(originarias: {int(nd.loc[nd.via_rex, 'is_originaria'].sum())})")

cand = nd[(nd.via_rex | nd.art16) & (nd.is_originaria == 0)].sort_values("caso_id_canonico")
print(f"\nCANDIDATAS (¬originaria ∧ (via=REX ∨ art16)): {len(cand)}")
print(cand[["caso_id_canonico", "art16", "ley48", "via_rex",
            "is_merit_decision"]].to_string(index=False))

print("\nverificación puntual 331_p100:")
x = nd[nd.caso_id_canonico == "331_p100"]
print(x[["caso_id_canonico", "art16", "ley48", "via_rex"]].to_string(index=False)
      if len(x) else "  NO está en no_revision_demanda (!!)")
