#!/usr/bin/env python3
"""
Inspeccionar las 5 regresiones de B070 v4.

Para cada regresión muestra:
- Las líneas alrededor de lfc (linea_fin del cruzador)
- Dónde matchea primer_token_siguiente
- Por qué _es_texto_corriente lo rechaza
- Dónde corta el fallback (Pista 2/3)

Genera: output/auditoria/H048/regresiones_v4.md
"""
import sys
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "pipeline"))

import parser as P
import pandas as pd

CSV_PATH = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUTPUT_DIR = REPO / "output" / "auditoria" / "H048"

df = pd.read_csv(CSV_PATH)

regressed = ['329_p988', '330_p1183', '331_p2614', '332_p1147', '345_p98']

# Build primer_token lookup
filas_loc, _ = P.cargar_localizados(
    str(REPO / "output" / "localizacion" / "fallos_localizados.csv"))
primer_token_por_caso = {
    row["caso_id_canonico"]: P.primer_token_de_caratula(row.get("nombres_indice", ""))
    for row in filas_loc
}
# Build siguiente_caso
cat_por_tomo = {}
for row in filas_loc:
    cat_por_tomo.setdefault(int(row["tomo"]), []).append({
        "caso_id_canonico": row["caso_id_canonico"],
        "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
    })
for t in cat_por_tomo:
    cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
siguiente_caso = {}
for t, lst in cat_por_tomo.items():
    for i, c in enumerate(lst[:-1]):
        siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]

_file_cache = {}
def cargar(src):
    if src not in _file_cache:
        p = CORPUS_DIR / src
        _file_cache[src] = open(p, encoding="utf-8").readlines() if p.exists() else []
    return _file_cache[src]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUTPUT_DIR / "regresiones_v4.md"

with open(out_path, "w", encoding="utf-8") as out:
    out.write("# B070 v4 — Inspección de 5 regresiones\n\n")

    for caso in regressed:
        r = df[df['caso_id_canonico'] == caso].iloc[0]
        src = r['source_file']
        li = int(r['linea_inicio'])
        lf = int(r['linea_fin'])
        lfr = int(r['linea_fin_real'])
        lines = cargar(src)

        sig = siguiente_caso.get(caso, "")
        token = primer_token_por_caso.get(sig, "") if sig else ""

        out.write(f"## {caso}\n\n")
        out.write(f"- source: `{src}` L{li}–{lfr} (lf={lf})\n")
        out.write(f"- siguiente: {sig}, token: `{token}`\n")
        out.write(f"- voting_pattern baseline: {r['voting_pattern']}\n\n")

        # Find ALL matches of token from lf-5 to lf+60
        if token and len(token) >= 5:
            pat = re.compile(r"\b" + re.escape(token) + r"\b", re.I)
            out.write(f"### Matches de `{token}` en zona lf-5 a lf+60:\n\n")
            for k in range(max(0, lf - 5), min(len(lines), lf + 61)):
                s = lines[k].rstrip()
                if pat.search(s):
                    # Check _es_texto_corriente conditions
                    first_alpha = None
                    for c in s.strip():
                        if c.isalpha():
                            first_alpha = c
                            break
                    starts_lower = first_alpha and first_alpha.islower()

                    # Find prev significant line
                    prev_line = None
                    for j in range(k - 1, max(k - 5, -1), -1):
                        ps = lines[j].strip()
                        if not ps:
                            continue
                        if P.RE_PAGE_HEADER.match(ps):
                            continue
                        if re.match(r'^\d{1,4}$', ps):
                            continue
                        if ps in ("FALLOS DE LA CORTE SUPREMA", "DE JUSTICIA DE LA NACION",
                                  "DE JUSTICIA DE LA NACIÓN"):
                            continue
                        prev_line = ps
                        break

                    ends_hyphen = prev_line and prev_line.endswith('-')
                    
                    rejected = starts_lower or ends_hyphen
                    reason = []
                    if starts_lower:
                        reason.append(f"starts_lower('{first_alpha}')")
                    if ends_hyphen:
                        reason.append(f"prev_ends_hyphen")

                    marker = "REJECTED" if rejected else "ACCEPTED"
                    out.write(f"- **L{k}** [{marker}]: `{s.strip()[:90]}`\n")
                    if reason:
                        out.write(f"  - Razón: {', '.join(reason)}\n")
                    if prev_line:
                        out.write(f"  - Prev: `{prev_line[:80]}`\n")
                    out.write(f"\n")

        # Show context: 10 lines before lf, lf marker, 40 lines after lf
        out.write(f"### Contexto L{lf-5}..L{lf+40}:\n\n```\n")
        for k in range(max(0, lf - 5), min(len(lines), lf + 41)):
            s = lines[k].rstrip()
            marker = ""
            if k == lf:
                marker = " <<<LF"
            if k == lfr:
                marker = " <<<LFR"
            if P.linea_es_firma_de_juez(lines[k]):
                marker += " <<<FIRMA"
            out.write(f"L{k:6d}  {s}{marker}\n")
        out.write("```\n\n---\n\n")

print(f"Generado: {out_path}")
