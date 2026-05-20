#!/usr/bin/env python3
"""
H048 — Inspección y clasificación de los 113 sin_firma residuales.

Genera: output/auditoria/H048/inspeccion_113.md
  - Grupo A (57): sin_firma_post_fallo — últimas 30 líneas + clasificación
  - Grupo B (33): sin_zona_fallo — primeras 15 + últimas 15
  - Grupo C (23): span_corto — bloque completo

Uso:
  python scripts/auditoria/H048/inspeccion_113.py

Requiere:
  - output/parser/csjn_casos.csv (post-H047)
  - corpus/*.md (archivos fuente)
"""

import re
import sys
import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent.parent.parent  # corpus-csjn/
CSV_PATH = REPO / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO / "corpus"
OUTPUT_DIR = REPO / "output" / "auditoria" / "H048"

# ── Importar constantes del parser ───────────────────────────────────────────
sys.path.insert(0, str(REPO / "scripts" / "pipeline"))
from parser import (
    JUECES_CONOCIDOS,
    RE_APERTURA,
    RE_CONSIDERANDO,
    RE_FECHA_LINEA,
    RE_PAGE_HEADER,
    linea_es_firma_de_juez,
    _encontrar_zona_fallo,
    buscar_firma_inversa,
)

# ── Cargar CSV ───────────────────────────────────────────────────────────────
import pandas as pd

df = pd.read_csv(CSV_PATH)
sf = df[df["voting_pattern"] == "sin_firma"].copy()
sf["span"] = sf["linea_fin_real"] - sf["linea_inicio"]
print(f"Total sin_firma: {len(sf)}")

# ── Clasificar en 3 grupos ───────────────────────────────────────────────────
grupo_c = sf[sf["span"] < 20].copy()                                    # span_corto
resto = sf[sf["span"] >= 20].copy()
grupo_a = resto[resto["apertura_tipo"] == "fallo"].copy()                # sin_firma_post_fallo
grupo_b = resto[resto["apertura_tipo"].isna()].copy()                    # sin_zona_fallo

print(f"Grupo A (sin_firma_post_fallo): {len(grupo_a)}")
print(f"Grupo B (sin_zona_fallo):       {len(grupo_b)}")
print(f"Grupo C (span_corto):           {len(grupo_c)}")
assert len(grupo_a) + len(grupo_b) + len(grupo_c) == len(sf)

# ── Cache de archivos ────────────────────────────────────────────────────────
_file_cache = {}

def cargar_archivo(source_file):
    if source_file not in _file_cache:
        path = CORPUS_DIR / source_file
        if not path.exists():
            print(f"  WARN: {path} no existe")
            _file_cache[source_file] = []
        else:
            with open(path, "r", encoding="utf-8") as f:
                _file_cache[source_file] = f.readlines()
    return _file_cache[source_file]

def extraer_bloque(row):
    lines = cargar_archivo(row["source_file"])
    li = int(row["linea_inicio"])
    lf = int(row["linea_fin_real"])
    if li >= len(lines):
        return []
    return lines[li : min(lf + 1, len(lines))]

# ── Patrones de clasificación para Grupo A ───────────────────────────────────

# Apellidos sueltos en ALL CAPS (sin nombre delante)
_APELLIDOS = [nombre for _, nombre in JUECES_CONOCIDOS]
_APELLIDOS_UPPER = []
for _, nombre in JUECES_CONOCIDOS:
    # Extraer el apellido principal (primer token del nombre canónico)
    parts = nombre.replace("(conjuez)", "").strip().split()
    if parts:
        _APELLIDOS_UPPER.append(parts[0].upper())
_APELLIDOS_UPPER = list(set(_APELLIDOS_UPPER))


def clasificar_zona_firma(bloque, n_cola=30):
    """
    Analiza las últimas n_cola líneas del bloque buscando por qué
    linea_es_firma_de_juez no matchea.
    
    Retorna (patron, detalle) donde patron es uno de:
      - 'firma_partida': nombre en una línea, apellido en la siguiente
      - 'apellido_upper_suelto': apellido en ALL CAPS sin regex match
      - 'firma_sin_raya': nombre+apellido presente pero sin señal de firma
      - 'ocr_corrupto': apellido parcialmente reconocible
      - 'juez_no_listado': posible firma pero sin match en JUECES_CONOCIDOS
      - 'indeterminado': no se pudo clasificar automáticamente
    """
    cola = bloque[-n_cola:] if len(bloque) > n_cola else bloque
    detalle_lines = []
    
    # --- Check 1: firma partida entre líneas consecutivas ---
    for i in range(len(cola) - 1):
        s1 = cola[i].strip()
        s2 = cola[i + 1].strip()
        if not s1 or not s2:
            continue
        combined = s1 + " " + s2
        if linea_es_firma_de_juez(combined):
            detalle_lines.append(f"  Líneas {i}/{i+1}: '{s1}' + '{s2}' → match combinado")
            return "firma_partida", detalle_lines
        # Also check: any JUECES_CONOCIDOS pattern matches the combined
        for pat, nombre in JUECES_CONOCIDOS:
            if pat.search(combined) and not pat.search(s1) and not pat.search(s2):
                detalle_lines.append(
                    f"  Líneas {i}/{i+1}: '{s1}' + '{s2}' → {nombre} (regex match en combinado)"
                )
                return "firma_partida", detalle_lines
    
    # --- Check 2: apellido ALL CAPS suelto en una línea ---
    for i, line in enumerate(cola):
        s = line.strip()
        if not s:
            continue
        # Línea corta en mayúsculas que contiene un apellido conocido
        if s == s.upper() and len(s) < 60:
            for ap in _APELLIDOS_UPPER:
                if ap in s:
                    detalle_lines.append(f"  Línea {i}: '{s}' → apellido {ap} en ALL CAPS")
                    return "apellido_upper_suelto", detalle_lines
    
    # --- Check 3: match de JUECES_CONOCIDOS pero linea_es_firma_de_juez dice False ---
    for i, line in enumerate(cola):
        s = line.strip()
        if not s:
            continue
        for pat, nombre in JUECES_CONOCIDOS:
            if pat.search(s):
                # El regex matchea pero linea_es_firma no lo acepta — ¿por qué?
                razones = []
                if len(s) > 200:
                    razones.append("len>200")
                if RE_PAGE_HEADER.match(s) if hasattr(RE_PAGE_HEADER, 'match') else False:
                    razones.append("page_header")
                primera = s.split()[0].lower() if s.split() else ""
                if primera.rstrip(",;:") in {
                    "siguiendo", "como", "según", "segun", "que", "el", "la",
                    "los", "las", "ya", "esta", "este", "ese", "esa", "ello",
                    "por", "pero", "para", "tal", "incluso", "asimismo",
                    "también", "tambien", "no", "si", "cuando", "mientras",
                    "aunque", "luego", "después", "despues", "afirma",
                    "sostiene", "entiende", "considera", "indicó", "indico",
                    "destacó", "destaco", "señaló", "señalo", "concluyó", "concluyo",
                }:
                    razones.append(f"primera_palabra_cuerpo='{primera}'")
                tiene_raya = "—" in s or " - " in s or "–" in s
                es_corta = len(s) <= 80
                termina_punto = s.rstrip().endswith(".")
                if not (tiene_raya or es_corta or (termina_punto and len(s) <= 120)):
                    razones.append(f"sin_señal_firma(len={len(s)},raya={tiene_raya})")
                
                detalle_lines.append(
                    f"  Línea {i}: '{s[:100]}{'...' if len(s)>100 else ''}'"
                )
                detalle_lines.append(f"    Juez: {nombre}. Rechazo: {', '.join(razones) if razones else '???'}")
                return "firma_sin_raya" if "sin_señal_firma" in str(razones) else "juez_en_cuerpo", detalle_lines
    
    # --- Check 4: líneas con rayas que podrían ser firmas no reconocidas ---
    for i, line in enumerate(cola):
        s = line.strip()
        if not s:
            continue
        if ("—" in s or "–" in s) and len(s) < 80 and s == s.upper():
            detalle_lines.append(f"  Línea {i}: '{s}' → posible firma no listada (ALL CAPS + raya)")
            return "juez_no_listado", detalle_lines
    
    return "indeterminado", []


# ── Generar MD ───────────────────────────────────────────────────────────────

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
out_path = OUTPUT_DIR / "inspeccion_113.md"

# Contadores de clasificación
clasificacion_counts = {}

with open(out_path, "w", encoding="utf-8") as out:
    out.write("# H048 — Inspección de los 113 sin_firma\n\n")
    out.write(f"Generado automáticamente por `inspeccion_113.py`.\n\n")
    out.write("---\n\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # GRUPO A: sin_firma_post_fallo (57)
    # ═══════════════════════════════════════════════════════════════════════
    out.write(f"## Grupo A — sin_firma_post_fallo ({len(grupo_a)} casos)\n\n")
    out.write("Zona de fallo encontrada pero `linea_es_firma_de_juez` no matchea.\n\n")
    
    for _, row in grupo_a.sort_values("caso_id_canonico").iterrows():
        caso_id = row["caso_id_canonico"]
        bloque = extraer_bloque(row)
        span = len(bloque)
        
        # Clasificar
        patron, detalle = clasificar_zona_firma(bloque)
        clasificacion_counts[patron] = clasificacion_counts.get(patron, 0) + 1
        
        # También correr buscar_firma_inversa para confirmar motivo
        _, _, motivo_real = buscar_firma_inversa(bloque)
        
        out.write(f"### {caso_id} (span={span}, patrón={patron})\n\n")
        out.write(f"- **source:** `{row['source_file']}` L{row['linea_inicio']}–{row['linea_fin_real']}\n")
        out.write(f"- **case_name_indice:** {row['case_name_indice']}\n")
        out.write(f"- **motivo buscar_firma_inversa:** {motivo_real}\n")
        if detalle:
            out.write(f"- **clasificación automática:**\n")
            for d in detalle:
                out.write(f"{d}\n")
        
        # Últimas 30 líneas
        n_cola = 30
        cola = bloque[-n_cola:] if len(bloque) > n_cola else bloque
        out.write(f"\n**Últimas {len(cola)} líneas:**\n```\n")
        for line in cola:
            out.write(line.rstrip() + "\n")
        out.write("```\n\n---\n\n")
    
    # Resumen clasificación Grupo A
    out.write("### Resumen clasificación Grupo A\n\n")
    out.write("| Patrón | Casos |\n|--------|------:|\n")
    for pat, cnt in sorted(clasificacion_counts.items(), key=lambda x: -x[1]):
        out.write(f"| {pat} | {cnt} |\n")
    out.write(f"| **TOTAL** | **{sum(clasificacion_counts.values())}** |\n")
    out.write("\n---\n\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # GRUPO B: sin_zona_fallo (33)
    # ═══════════════════════════════════════════════════════════════════════
    out.write(f"## Grupo B — sin_zona_fallo ({len(grupo_b)} casos)\n\n")
    out.write("Sin apertura, fecha, considerando ni vistos en el bloque.\n\n")
    
    for _, row in grupo_b.sort_values("caso_id_canonico").iterrows():
        caso_id = row["caso_id_canonico"]
        bloque = extraer_bloque(row)
        span = len(bloque)
        
        out.write(f"### {caso_id} (span={span})\n\n")
        out.write(f"- **source:** `{row['source_file']}` L{row['linea_inicio']}–{row['linea_fin_real']}\n")
        out.write(f"- **case_name_indice:** {row['case_name_indice']}\n")
        
        # Primeras 15 + últimas 15
        n_head = min(15, span)
        n_tail = min(15, span)
        
        out.write(f"\n**Primeras {n_head} líneas:**\n```\n")
        for line in bloque[:n_head]:
            out.write(line.rstrip() + "\n")
        out.write("```\n")
        
        if span > 30:
            out.write(f"\n*[... {span - 30} líneas omitidas ...]*\n")
        
        out.write(f"\n**Últimas {n_tail} líneas:**\n```\n")
        for line in bloque[-n_tail:]:
            out.write(line.rstrip() + "\n")
        out.write("```\n\n---\n\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # GRUPO C: span_corto (23)
    # ═══════════════════════════════════════════════════════════════════════
    out.write(f"## Grupo C — span_corto ({len(grupo_c)} casos)\n\n")
    out.write("Bloques de menos de 20 líneas.\n\n")
    
    for _, row in grupo_c.sort_values("caso_id_canonico").iterrows():
        caso_id = row["caso_id_canonico"]
        bloque = extraer_bloque(row)
        span = len(bloque)
        
        out.write(f"### {caso_id} (span={span})\n\n")
        out.write(f"- **source:** `{row['source_file']}` L{row['linea_inicio']}–{row['linea_fin_real']}\n")
        out.write(f"- **case_name_indice:** {row['case_name_indice']}\n")
        
        out.write(f"\n**Bloque completo:**\n```\n")
        for line in bloque:
            out.write(line.rstrip() + "\n")
        out.write("```\n\n---\n\n")

print(f"\nGenerado: {out_path}")
print(f"Clasificación Grupo A: {clasificacion_counts}")
