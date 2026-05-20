#!/usr/bin/env python3
"""
aplicar_patch_h041.py — Crea parser_h041.py con Tier 2 mid-line.

Ubicacion: scripts/diagnostico/H041/
Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    python scripts/diagnostico/H041/aplicar_patch_h041.py
    python output/diagnostico/H041/parser_h041.py --localizados output/localizacion/fallos_localizados.csv --mapa output/localizacion/mapa_paginas.csv --corpus corpus --output output/diagnostico/H041/csjn_casos_h041.csv --output-votos output/diagnostico/H041/csjn_casos_votos_h041.csv
"""
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PARSER_ORIG = os.path.join(REPO, "scripts", "pipeline", "parser.py")
OUT_DIR = os.path.join(REPO, "output", "diagnostico", "H041")
PARSER_OUT = os.path.join(OUT_DIR, "parser_h041.py")

os.makedirs(OUT_DIR, exist_ok=True)

with open(PARSER_ORIG, encoding="utf-8") as f:
    lines = f.readlines()

# Buscar la línea "por_ello_text = _fallback_text"
insert_after = None
for i, line in enumerate(lines):
    if "por_ello_text = _fallback_text" in line and "_fallback" in line:
        insert_after = i
        break

if insert_after is None:
    print("ERROR: no encontre la linea anchor 'por_ello_text = _fallback_text'")
    raise SystemExit(1)

# Tier 2 como lista de líneas
tier2_lines = [
    "",
    "        # -- H041 Tier 2: .search() mid-line para patrones seguros -----",
    "        # Solo se activa si Tier 1 no encontro NADA (ni validado ni fallback).",
    "        # Guardas: (a) patrones seguros, (b) fin de oracion antes del match,",
    "        #          (c) filtro argumental, (d) firma validada sin fallback.",
    "        if por_ello_idx is None:",
    '            _t2_pats = [',
    r'                re.compile(r"Por ello[,.]?\s", re.I),',
    r'                re.compile(r"Por lo expuesto\b", re.I),',
    r'                re.compile(r"Por las razones\b", re.I),',
    r'                re.compile(r"Por lo expresado\b", re.I),',
    r'                re.compile(r"Por las consideraciones\b", re.I),',
    r'                re.compile(r"Que[,]?\s+por\s+ello\b", re.I),',
    r'                re.compile(r"O[íi]dos?\s+(el|la|los|las)\b", re.I),',
    '            ]',
    "            for k in range(inicio_busqueda, fin_busqueda):",
    "                if k in lineas_dictamen:",
    "                    continue",
    "                stripped = bloque[k].strip()",
    "                if not stripped:",
    "                    continue",
    "                _t2_hit = False",
    "                for _t2_pat in _t2_pats:",
    "                    _t2_m = _t2_pat.search(stripped)",
    "                    if _t2_m and _t2_m.start() > 0:",
    "                        # Guarda: fin de oracion antes del match",
    "                        _t2_pre = stripped[:_t2_m.start()].rstrip()",
    '                        if not (_t2_pre.endswith(".") or _t2_pre.endswith(")")',
    '                                or stripped.lstrip().startswith("Que")):',
    "                            continue",
    "                        # Guarda argumental",
    "                        _t2_rest = stripped[_t2_m.end():].strip()",
    '                        _t2_fw = _t2_rest.split()[0].lower().rstrip(",;") if _t2_rest.split() else ""',
    "                        if _t2_fw in POR_ELLO_ARGUMENTAL:",
    "                            continue",
    "                        # Firma validada obligatoria",
    "                        if any(linea_es_firma_de_juez(bloque[j])",
    "                               for j in range(k + 1, min(k + 41, len(bloque)))):",
    "                            chunk = []",
    "                            for m2 in range(k, min(k + 6, len(bloque))):",
    "                                chunk.append(bloque[m2])",
    '                                if bloque[m2].strip().endswith("."):',
    "                                    break",
    "                            por_ello_idx = k",
    '                            por_ello_text = " ".join(chunk).strip()',
    "                            _t2_hit = True",
    "                            break",
    "                if _t2_hit:",
    "                    break",
    "",
]

new_lines = lines[:insert_after + 1] + [l + "\n" for l in tier2_lines] + lines[insert_after + 1:]

with open(PARSER_OUT, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"OK: {PARSER_OUT}")
print(f"Lineas: {len(lines)} -> {len(new_lines)}")
print()
print("Correr:")
print(f'python "{PARSER_OUT}" --localizados output/localizacion/fallos_localizados.csv --mapa output/localizacion/mapa_paginas.csv --corpus corpus --output output/diagnostico/H041/csjn_casos_h041.csv --output-votos output/diagnostico/H041/csjn_casos_votos_h041.csv')
