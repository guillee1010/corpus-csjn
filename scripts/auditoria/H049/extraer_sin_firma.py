"""
Extractor de sin_firma — H049 Fase 3

Extrae del corpus el texto de cada caso sin_firma.
Genera 3 archivos:

  1. sin_firma_texto_completo.md   — bloque catálogo + marca de corte (para leer a mano)
  2. sin_firma_bloque_catalogo.md  — solo linea_inicio → linea_fin (para diff)
  3. sin_firma_bloque_parser.md    — solo linea_inicio → linea_fin_real (para diff)

Uso:
  python scripts/auditoria/H049/extraer_sin_firma.py

Output:
  output/auditoria/H049/sin_firma_texto_completo.md
  output/auditoria/H049/sin_firma_bloque_catalogo.md
  output/auditoria/H049/sin_firma_bloque_parser.md
"""

import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent.parent
CSV_CASOS = ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS = ROOT / "corpus"
OUT_DIR = ROOT / "output" / "auditoria" / "H049"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_COMPLETO = OUT_DIR / "sin_firma_texto_completo.md"
OUT_CATALOGO = OUT_DIR / "sin_firma_bloque_catalogo.md"
OUT_PARSER   = OUT_DIR / "sin_firma_bloque_parser.md"


def clasificar(r):
    li = int(r["linea_inicio"])
    lfr = int(r["linea_fin_real"])
    span = lfr - li
    tiene_apertura = bool(r.get("apertura_tipo", "").strip())
    tiene_fecha = bool(r.get("date", "").strip())
    if span < 5:
        return "bloque_vacio"
    elif span < 20:
        return "bloque_corto"
    elif not tiene_apertura and not tiene_fecha:
        return "sin_zona_fallo"
    else:
        return "firma_no_detectada"


# Cargar casos
with open(CSV_CASOS, encoding="utf-8") as f:
    all_rows = list(csv.DictReader(f))

sin_firma = [r for r in all_rows
             if r["voting_pattern"] == "sin_firma" and r["tipo_entrada"] == "fallo"]
sin_firma.sort(key=lambda r: (clasificar(r), r["tomo"], r["caso_id_canonico"]))

print(f"sin_firma fallos: {len(sin_firma)}")

# Cargar archivos del corpus (cache)
archivos_necesarios = {r["source_file"] for r in sin_firma}
cache_lines = {}
for fname in archivos_necesarios:
    fpath = CORPUS / fname
    if fpath.exists():
        cache_lines[fname] = fpath.read_text(encoding="utf-8").splitlines()
    else:
        print(f"  WARN: {fpath} no encontrado")
        cache_lines[fname] = []


def header_caso(r):
    """Header común para los 3 archivos."""
    cat = clasificar(r)
    caso = r["caso_id_canonico"]
    li = int(r["linea_inicio"])
    lf = int(r["linea_fin"])
    lfr = int(r["linea_fin_real"])
    nombres = r.get("case_name_indice", "").split(" | ")
    caratula = nombres[0].strip() if nombres else "?"

    h = []
    h.append(f"### {caso} — {caratula}\n")
    h.append(f"- **Categoría:** {cat} | **Tomo:** {r['tomo']}")
    h.append(f"- **Archivo:** {r['source_file']}")
    h.append(f"- **Líneas:** inicio={li} | fin_real={lfr} | fin_cat={lf}")
    h.append(f"- **Span parser:** {lfr - li} | **Span catálogo:** {lf - li}")
    h.append(f"- **WC:** {r.get('word_count', '?')} | **Apertura:** "
             f"{r.get('apertura_tipo', '') or '—'} | **Fecha:** "
             f"{r.get('date', '') or '—'}")
    h.append(f"- **Pista fin:** {r.get('pista_fin', '')}")
    h.append("")
    return "\n".join(h)


# ── Archivo 1: completo (para leer a mano) ─────────────────────────────────
completo = []
completo.append("# Sin firma — texto completo del corpus\n")
completo.append(f"Total: {len(sin_firma)} fallos. Bloque catálogo con marca de corte.\n")
completo.append("Leyenda: `[pre]` = contexto previo, `>>LFR>>` = línea de corte, "
                "`[res]` = residuo descartado, `[post]` = contexto posterior.\n")
completo.append("---\n")

cat_actual = None
for r in sin_firma:
    cat = clasificar(r)
    if cat != cat_actual:
        cat_actual = cat
        n_cat = sum(1 for x in sin_firma if clasificar(x) == cat)
        completo.append(f"\n## {cat} ({n_cat})\n")

    li = int(r["linea_inicio"])
    lf = int(r["linea_fin"])
    lfr = int(r["linea_fin_real"])
    lines = cache_lines.get(r["source_file"], [])

    completo.append(header_caso(r))
    completo.append("```")

    if not lines:
        completo.append("[archivo no encontrado]")
    else:
        ctx_start = max(0, li - 5)
        ctx_end = min(len(lines), lf + 5)

        for i in range(ctx_start, ctx_end):
            if i < li:
                prefix = "  [pre] "
            elif i == lfr and lfr != lf:
                prefix = ">>LFR>> "
            elif i > lfr and i <= lf:
                prefix = "  [res] "
            elif i > lf:
                prefix = "  [post]"
            else:
                prefix = "        "

            line_text = lines[i] if i < len(lines) else ""
            completo.append(f"{prefix}{i:6d} | {line_text}")

            if i == lfr and lfr != lf:
                completo.append(
                    f"       | {'=' * 60}")
                completo.append(
                    f"       | >>> CORTE linea_fin_real={lfr} — "
                    f"residuo abajo ({lf - lfr} líneas) <<<")
                completo.append(
                    f"       | {'=' * 60}")

    completo.append("```\n")

OUT_COMPLETO.write_text("\n".join(completo), encoding="utf-8")
print(f"Generado: {OUT_COMPLETO} ({len(completo)} líneas)")


# ── Archivo 2: bloque catálogo (para diff) ──────────────────────────────────
catalogo = []
catalogo.append("# Sin firma — bloque catálogo (linea_inicio → linea_fin)\n")
catalogo.append("---\n")

cat_actual = None
for r in sin_firma:
    cat = clasificar(r)
    if cat != cat_actual:
        cat_actual = cat
        catalogo.append(f"\n## {cat}\n")

    li = int(r["linea_inicio"])
    lf = int(r["linea_fin"])
    lines = cache_lines.get(r["source_file"], [])

    catalogo.append(header_caso(r))
    catalogo.append("```")
    if not lines:
        catalogo.append("[archivo no encontrado]")
    else:
        for i in range(li, min(len(lines), lf + 1)):
            catalogo.append(f"{i:6d} | {lines[i] if i < len(lines) else ''}")
    catalogo.append("```\n")

OUT_CATALOGO.write_text("\n".join(catalogo), encoding="utf-8")
print(f"Generado: {OUT_CATALOGO} ({len(catalogo)} líneas)")


# ── Archivo 3: bloque parser (para diff) ────────────────────────────────────
parser_out = []
parser_out.append("# Sin firma — bloque parser (linea_inicio → linea_fin_real)\n")
parser_out.append("---\n")

cat_actual = None
for r in sin_firma:
    cat = clasificar(r)
    if cat != cat_actual:
        cat_actual = cat
        parser_out.append(f"\n## {cat}\n")

    li = int(r["linea_inicio"])
    lfr = int(r["linea_fin_real"])
    lines = cache_lines.get(r["source_file"], [])

    parser_out.append(header_caso(r))
    parser_out.append("```")
    if not lines:
        parser_out.append("[archivo no encontrado]")
    else:
        for i in range(li, min(len(lines), lfr + 1)):
            parser_out.append(f"{i:6d} | {lines[i] if i < len(lines) else ''}")
    parser_out.append("```\n")

OUT_PARSER.write_text("\n".join(parser_out), encoding="utf-8")
print(f"Generado: {OUT_PARSER} ({len(parser_out)} líneas)")

print("\nListo. Para diff:")
print(f"  diff {OUT_CATALOGO.name} {OUT_PARSER.name}")
