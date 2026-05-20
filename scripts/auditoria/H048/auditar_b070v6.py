#!/usr/bin/env python3
"""
Auditoría visual de las 37 mejoras de B070 v6.

Para cada mejora, muestra:
- Últimas 20 líneas del bloque NUEVO (con firma incluida)
- Firma parseada y jueces detectados
- Comparación lfr viejo vs nuevo

Genera: output/auditoria/H048/auditoria_b070v6.md
"""
import sys
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "scripts" / "pipeline"))

import parser as P
import pandas as pd
import unicodedata

CSV_BASE = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUTPUT_DIR = REPO / "output" / "auditoria" / "H048"

df_base = pd.read_csv(CSV_BASE)

mejoras = [
    "329_p1306","329_p1311","329_p1672","329_p2174","329_p2485",
    "329_p2600","329_p2896","329_p324","329_p3848","329_p3890",
    "329_p4168","329_p4172","329_p4822","329_p5007","329_p5178",
    "329_p551","329_p5605","329_p5689","330_p1642","330_p2059",
    "330_p2575","330_p4796","330_p4807","330_p4851","330_p607",
    "331_p310","331_p360","332_p585","337_p339","338_p697",
    "339_p599","343_p1332","345_p1498","345_p599","346_p253",
    "348_p259","348_p53",
]

# New lfr values from v6 output
new_lfr = {
    "329_p1306":49753,"329_p1311":50103,"329_p1672":11443,"329_p2174":30556,
    "329_p2485":42429,"329_p2600":46518,"329_p2896":57533,"329_p324":12214,
    "329_p3848":34665,"329_p3890":36308,"329_p4168":46783,"329_p4172":47007,
    "329_p4822":71472,"329_p5007":4616,"329_p5178":11231,"329_p551":20824,
    "329_p5605":27284,"329_p5689":30400,"330_p1642":12012,"330_p2059":28148,
    "330_p2575":48178,"330_p4796":18372,"330_p4807":18901,"330_p4851":20719,
    "330_p607":23014,"331_p310":12013,"331_p360":13628,"332_p585":22868,
    "337_p339":13522,"338_p697":409,"339_p599":22503,"343_p1332":25328,
    "345_p1498":24633,"345_p599":22948,"346_p253":9839,"348_p259":9953,
    "348_p53":2085,
}

_file_cache = {}
def cargar(src):
    if src not in _file_cache:
        p = CORPUS_DIR / src
        _file_cache[src] = open(p, encoding="utf-8").readlines() if p.exists() else []
    return _file_cache[src]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUTPUT_DIR / "auditoria_b070v6.md"

with open(out_path, "w", encoding="utf-8") as out:
    out.write("# Auditoría B070 v6 — 37 mejoras\n\n")
    out.write("Últimas 25 líneas del bloque extendido para verificar firma.\n\n")

    for caso in mejoras:
        r = df_base[df_base['caso_id_canonico'] == caso]
        if not len(r):
            out.write(f"### {caso} — NO ENCONTRADO EN BASELINE\n\n---\n\n")
            continue
        r = r.iloc[0]
        src = r['source_file']
        li = int(r['linea_inicio'])
        lfr_old = int(r['linea_fin_real'])
        lfr_new = new_lfr.get(caso, lfr_old)

        lines = cargar(src)
        if not lines:
            out.write(f"### {caso} — ARCHIVO NO ENCONTRADO\n\n---\n\n")
            continue

        # Extract the NEW block (extended)
        bloque_new = lines[li:min(lfr_new + 1, len(lines))]

        # Run parse_firma on the new block to see what it finds
        # Find firma lines in the new extension
        firma_lines_found = []
        for k in range(max(0, len(bloque_new) - 25), len(bloque_new)):
            if P.linea_es_firma_de_juez(bloque_new[k]):
                firma_lines_found.append((k, bloque_new[k].strip()))

        out.write(f"### {caso}\n\n")
        out.write(f"- source: `{src}` L{li}\n")
        out.write(f"- lfr: {lfr_old} → {lfr_new} (ext +{lfr_new - lfr_old})\n")
        out.write(f"- case_name: {r['case_name_indice'][:70]}\n")
        if firma_lines_found:
            out.write(f"- firmas detectadas: {len(firma_lines_found)}\n")
            for k, fl in firma_lines_found:
                out.write(f"  - L+{k}: `{fl[:80]}`\n")

        # Show last 25 lines of new block
        n_tail = 25
        tail = bloque_new[-n_tail:] if len(bloque_new) > n_tail else bloque_new
        tail_start = li + len(bloque_new) - len(tail)

        out.write(f"\n```\n")
        for k, line in enumerate(tail):
            lineno = tail_start + k
            marker = ""
            if P.linea_es_firma_de_juez(line):
                marker = " <<<FIRMA"
            out.write(f"L{lineno:6d}  {line.rstrip()}{marker}\n")
        out.write("```\n\n---\n\n")

print(f"Generado: {out_path}")
print(f"Total: {len(mejoras)} casos")
