"""
PoC H052 v2 — Integración zonas + guarda dictamen.

Cambio respecto a v1: en la Pasada 2 del zonificador, dentro de zona
dictamen solo apertura ("FALLO DE LA CORTE SUPREMA") y fecha sin apertura
futura cierran la zona. Los demás marcadores (dispositivo, firma, etc.)
se suprimen — son falsos positivos del vocabulario compartido entre el
dictamen del Procurador y el fallo. ~486 casos afectados.

Uso (PowerShell, desde raíz del repo):
  python scripts/auditoria/H052/poc_integracion_zonas_h052_v2.py

Salida:
  scripts/auditoria/H052/csjn_casos_zonas_h052_v2.csv
  scripts/auditoria/H052/integracion_zonas_h052_v2_reporte.md
  stdout: resumen de concordancia
"""

import sys
import csv
import re
import importlib.util
from pathlib import Path
from collections import Counter

# ── Setup de paths ────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSER_PATH = REPO_ROOT / "scripts" / "pipeline" / "parser.py"

if not PARSER_PATH.exists():
    print(f"ERROR: no se encontró parser.py en {PARSER_PATH}")
    print(f"  REPO_ROOT calculado: {REPO_ROOT}")
    sys.exit(1)

_spec = importlib.util.spec_from_file_location("csjn_parser", str(PARSER_PATH))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Importar del parser
RE_APERTURA = _mod.RE_APERTURA
RE_FECHA_LINEA = _mod.RE_FECHA_LINEA
RE_CONSIDERANDO = _mod.RE_CONSIDERANDO
RE_DICT_HDR = _mod.RE_DICT_HDR
RE_VOTO_HDR = _mod.RE_VOTO_HDR
RE_DISID_HDR = _mod.RE_DISID_HDR
RE_PAGE_HEADER = _mod.RE_PAGE_HEADER
RE_DATOS_PARTES = _mod.RE_DATOS_PARTES
detectar_apertura_dispositivo = _mod.detectar_apertura_dispositivo
construir_bloque_desde_localizacion = _mod.construir_bloque_desde_localizacion
refinar_inicio_por_titulo = _mod.refinar_inicio_por_titulo
linea_es_firma_de_juez = _mod.linea_es_firma_de_juez
linea_es_header_sumario = _mod.linea_es_header_sumario

# ── Configuración ─────────────────────────────────────────────────────────────
CSV_CASOS = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_ZONAS = OUTPUT_DIR / "csjn_casos_zonas_h052_v2.csv"
OUTPUT_MD = OUTPUT_DIR / "integracion_zonas_h052_v2_reporte.md"

# Regex adicionales del PoC H051 (no están en producción todavía)
RE_VISTOS = re.compile(r"^\s*Vistos? los autos", re.I)
RE_REMISION = re.compile(
    r"^[–—-]\s*Del\s+(dictamen|precedente|voto|fallo)",
    re.I
)


# ══════════════════════════════════════════════════════════════════════════════
# ZONIFICADOR (versión PoC — devuelve list + anclas)
# ══════════════════════════════════════════════════════════════════════════════

def zonificar_bloque(bloque):
    """
    Asigna una zona a cada línea del bloque.

    Retorna:
      zonas: list[str]  — etiqueta de zona para cada línea
      anclas: list[tuple] — (linea, tipo_marcador)
    """
    n = len(bloque)
    zonas = ["intersticio"] * n

    # ── Pasada 0: headers de página ──────────────────────────────────
    for k in range(n):
        s = bloque[k].strip()
        if s and RE_PAGE_HEADER.match(s):
            zonas[k] = "header_pagina"

    # ── Pasada 1: detectar anclas ────────────────────────────────────
    anclas = []
    for k in range(n):
        if zonas[k] == "header_pagina":
            continue
        s = bloque[k].strip()
        if not s:
            continue

        if RE_DICT_HDR.match(s):
            anclas.append((k, "dictamen_inicio")); continue
        if RE_APERTURA.match(s):
            anclas.append((k, "apertura")); continue
        if RE_FECHA_LINEA.match(s):
            anclas.append((k, "fecha")); continue
        if RE_CONSIDERANDO.match(s):
            anclas.append((k, "considerando")); continue
        if RE_VISTOS.match(s):
            anclas.append((k, "vistos")); continue
        if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
            anclas.append((k, "voto_header")); continue

        es_disp, _ = detectar_apertura_dispositivo(s)
        if es_disp:
            anclas.append((k, "dispositivo")); continue

        if linea_es_firma_de_juez(bloque[k]):
            anclas.append((k, "firma_linea")); continue

        if linea_es_header_sumario(bloque[k]):
            anclas.append((k, "sumario_header")); continue

        if RE_REMISION.match(s):
            anclas.append((k, "sumario_header")); continue

        if RE_DATOS_PARTES.match(s):
            ya_paso_firma = any(t in ("firma_linea", "voto_header", "dispositivo")
                                for _, t in anclas)
            if ya_paso_firma:
                anclas.append((k, "epilogo_marker")); continue

    # ── Pasada 2: propagar zonas entre anclas ────────────────────────
    zona_activa = "intersticio"
    ancla_en = {pos: tipo for pos, tipo in anclas}

    for k in range(n):
        if zonas[k] == "header_pagina":
            continue

        if k in ancla_en:
            tipo = ancla_en[k]

            # ── H052 guarda: dentro de dictamen, solo apertura y fecha
            # (sin apertura futura) cierran la zona. Los demás marcadores
            # (dispositivo del Procurador, firma del Procurador, etc.) se
            # ignoran — son falsos positivos del vocabulario compartido
            # entre el dictamen y el fallo. (~486 casos afectados.)
            if zona_activa == "dictamen" and tipo not in (
                "apertura", "fecha", "dictamen_inicio"
            ):
                pass  # mantener zona_activa = "dictamen"
            elif tipo == "sumario_header":
                zona_activa = "sumario"
            elif tipo == "dictamen_inicio":
                zona_activa = "dictamen"
            elif tipo == "apertura":
                zona_activa = "apertura"
            elif tipo == "fecha":
                if zona_activa in ("apertura", "intersticio", "sumario"):
                    zona_activa = "cuerpo"
                elif zona_activa == "dictamen":
                    hay_apertura_despues = any(
                        t == "apertura" for p, t in anclas if p > k
                    )
                    if not hay_apertura_despues:
                        zona_activa = "cuerpo"
            elif tipo == "considerando":
                zona_activa = "cuerpo"
            elif tipo == "vistos":
                if zona_activa not in ("dictamen",):
                    zona_activa = "cuerpo"
            elif tipo == "dispositivo":
                zona_activa = "dispositivo"
            elif tipo == "firma_linea":
                zona_activa = "firma"
            elif tipo == "voto_header":
                zona_activa = "voto_separado"
            elif tipo == "epilogo_marker":
                zona_activa = "epilogo"

        if zonas[k] != "header_pagina":
            zonas[k] = zona_activa

    return zonas, anclas


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACCIÓN DE SEGMENTOS
# ══════════════════════════════════════════════════════════════════════════════

def extraer_segmentos(zonas, bloque):
    """
    Extrae segmentos contiguos de zonas con sus fronteras y word count.

    Retorna lista de dicts:
      zona, segmento (1-indexed), linea_ini, linea_fin, n_lineas, wc
    """
    if not zonas:
        return []

    segmentos = []
    conteo_zona = Counter()  # para numerar segmentos por zona

    zona_actual = zonas[0]
    ini_actual = 0

    for k in range(1, len(zonas)):
        if zonas[k] != zona_actual:
            # Cerrar segmento anterior
            conteo_zona[zona_actual] += 1
            wc = sum(
                len(re.findall(r'\b\w+\b', bloque[j]))
                for j in range(ini_actual, k)
            )
            segmentos.append({
                "zona": zona_actual,
                "segmento": conteo_zona[zona_actual],
                "linea_ini": ini_actual,
                "linea_fin": k - 1,
                "n_lineas": k - ini_actual,
                "wc": wc,
            })
            zona_actual = zonas[k]
            ini_actual = k

    # Último segmento
    conteo_zona[zona_actual] += 1
    wc = sum(
        len(re.findall(r'\b\w+\b', bloque[j]))
        for j in range(ini_actual, len(zonas))
    )
    segmentos.append({
        "zona": zona_actual,
        "segmento": conteo_zona[zona_actual],
        "linea_ini": ini_actual,
        "linea_fin": len(zonas) - 1,
        "n_lineas": len(zonas) - ini_actual,
        "wc": wc,
    })

    return segmentos


# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_todos_los_casos():
    with open(CSV_CASOS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cargar_lines(source_file, cache):
    if source_file in cache:
        return cache[source_file]
    path = CORPUS_DIR / source_file
    if not path.exists():
        cache[source_file] = None
        return None
    lines = path.read_text(encoding="utf-8").split("\n")
    cache[source_file] = lines
    return lines


def reconstruir_bloque(caso, lines):
    """Reconstruye el bloque como lo hace procesar_caso."""
    li = int(caso["linea_inicio"]) if caso["linea_inicio"] else 0
    lfr = int(caso["linea_fin_real"]) if caso["linea_fin_real"] else (
        int(caso["linea_fin"]) if caso["linea_fin"] else len(lines) - 1)

    bloque = construir_bloque_desde_localizacion(lines, li, lfr)
    if not bloque:
        return None

    nombres_indice = caso.get("case_name_indice", "")
    offset, ancla = refinar_inicio_por_titulo(bloque, nombres_indice)
    if offset > 0:
        bloque = bloque[offset:]

    return bloque if bloque else None


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("PoC H052 v2 — Integración zonas + guarda dictamen")
    print("=" * 70)

    todos = cargar_todos_los_casos()
    fallos = [r for r in todos if r["tipo_entrada"] == "fallo"]
    print(f"\nFallos en CSV: {len(fallos)}")

    cache_lines = {}
    all_segmentos = []      # filas para csjn_casos_zonas
    concordancia_wc = []    # para reporte de wc_dictamen

    n_procesados = 0
    n_skip = 0

    for caso in fallos:
        sf = caso["source_file"]
        lines = cargar_lines(sf, cache_lines)
        if lines is None:
            n_skip += 1
            continue

        bloque = reconstruir_bloque(caso, lines)
        if bloque is None or len(bloque) < 2:
            n_skip += 1
            continue

        caso_id = caso["caso_id_canonico"]
        tomo = caso["tomo"]

        # ── Zonificar ─────────────────────────────────────────────────
        zonas, anclas = zonificar_bloque(bloque)
        segmentos = extraer_segmentos(zonas, bloque)

        # Agregar metadata del caso a cada segmento
        for seg in segmentos:
            seg["caso_id_canonico"] = caso_id
            seg["tomo"] = tomo
            all_segmentos.append(seg)

        # ── Derivar wc_dictamen desde zonas ───────────────────────────
        wc_dictamen_zonas = sum(
            seg["wc"] for seg in segmentos if seg["zona"] == "dictamen"
        )
        wc_dictamen_parser = int(caso.get("wc_dictamen", 0) or 0)

        # Derivar dictamen_presente desde zonas
        dictamen_presente_zonas = any(
            seg["zona"] == "dictamen" for seg in segmentos
        )
        dictamen_presente_parser = str(caso.get("dictamen_presente", "")).lower() in ("1", "true")

        concordancia_wc.append({
            "caso_id": caso_id,
            "tomo": tomo,
            "wc_parser": wc_dictamen_parser,
            "wc_zonas": wc_dictamen_zonas,
            "delta": wc_dictamen_zonas - wc_dictamen_parser,
            "delta_pct": (
                round(100 * (wc_dictamen_zonas - wc_dictamen_parser) / wc_dictamen_parser, 1)
                if wc_dictamen_parser > 0 else
                (0.0 if wc_dictamen_zonas == 0 else float('inf'))
            ),
            "presencia_parser": dictamen_presente_parser,
            "presencia_zonas": dictamen_presente_zonas,
            "presencia_concuerda": dictamen_presente_parser == dictamen_presente_zonas,
        })

        n_procesados += 1

    print(f"  Procesados: {n_procesados}  Salteados: {n_skip}")

    # ══════════════════════════════════════════════════════════════════
    # EXPORTAR CSV DE ZONAS
    # ══════════════════════════════════════════════════════════════════
    fieldnames_zonas = [
        "caso_id_canonico", "tomo", "zona", "segmento",
        "linea_ini", "linea_fin", "n_lineas", "wc",
    ]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_ZONAS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames_zonas)
        writer.writeheader()
        for seg in all_segmentos:
            writer.writerow({k: seg[k] for k in fieldnames_zonas})

    print(f"\n  [OK] {OUTPUT_ZONAS.name}: {len(all_segmentos)} segmentos")

    # ══════════════════════════════════════════════════════════════════
    # REPORTE DE CONCORDANCIA WC_DICTAMEN
    # ══════════════════════════════════════════════════════════════════

    # Presencia
    n_presencia_ok = sum(1 for r in concordancia_wc if r["presencia_concuerda"])
    n_total = len(concordancia_wc)

    # WC exacto
    n_wc_exacto = sum(1 for r in concordancia_wc if r["delta"] == 0)
    n_wc_cercano = sum(1 for r in concordancia_wc
                       if abs(r["delta"]) > 0 and abs(r["delta_pct"]) <= 5.0
                       and r["delta_pct"] != float('inf'))
    discrepantes_wc = [r for r in concordancia_wc
                       if abs(r["delta"]) > 0 and r["wc_parser"] > 0]
    discrepantes_wc.sort(key=lambda r: abs(r["delta"]), reverse=True)

    # Presencia discrepancias
    disc_presencia = [r for r in concordancia_wc if not r["presencia_concuerda"]]

    # Estadísticas de zonas
    zonas_counter = Counter(seg["zona"] for seg in all_segmentos)
    wc_por_zona = {}
    for seg in all_segmentos:
        wc_por_zona.setdefault(seg["zona"], []).append(seg["wc"])

    # ── Escribir reporte ──────────────────────────────────────────────
    md = []
    md.append("# H052 v2 — Integración zonas + guarda dictamen: reporte\n")
    md.append(f"Fallos procesados: {n_procesados}\n")
    md.append(f"Segmentos totales: {len(all_segmentos)}\n")

    md.append("\n## 1. Concordancia dictamen_presente\n")
    md.append(f"Concordancia: {n_presencia_ok}/{n_total} "
              f"({100*n_presencia_ok/n_total:.1f}%)\n")
    if disc_presencia:
        md.append(f"Discrepancias ({len(disc_presencia)}):\n")
        for r in disc_presencia[:20]:
            md.append(f"- `{r['caso_id']}` (t{r['tomo']}): "
                      f"parser={r['presencia_parser']} zonas={r['presencia_zonas']}")
        md.append("")

    md.append("\n## 2. Concordancia wc_dictamen\n")
    md.append(f"| Métrica | N | % |")
    md.append(f"|---|---|---|")
    md.append(f"| Exacto (delta=0) | {n_wc_exacto} | {100*n_wc_exacto/n_total:.1f}% |")
    md.append(f"| Cercano (delta≤5%) | {n_wc_cercano} | {100*n_wc_cercano/n_total:.1f}% |")
    md.append(f"| Con delta>0 (parser>0) | {len(discrepantes_wc)} | {100*len(discrepantes_wc)/n_total:.1f}% |")
    md.append("")

    if discrepantes_wc:
        md.append("### Top 30 discrepancias wc_dictamen (por delta absoluto)\n")
        md.append("| caso_id | tomo | wc_parser | wc_zonas | delta | delta% |")
        md.append("|---|---|---|---|---|---|")
        for r in discrepantes_wc[:30]:
            md.append(f"| `{r['caso_id']}` | {r['tomo']} | {r['wc_parser']} "
                      f"| {r['wc_zonas']} | {r['delta']:+d} | {r['delta_pct']:+.1f}% |")
        md.append("")

    md.append("\n## 3. Distribución de segmentos por zona\n")
    md.append("| Zona | Segmentos | WC total | WC promedio | WC mediana |")
    md.append("|---|---|---|---|---|")
    for zona in ["sumario", "dictamen", "cuerpo", "apertura", "dispositivo",
                 "firma", "voto_separado", "epilogo", "header_pagina", "intersticio"]:
        n_seg = zonas_counter.get(zona, 0)
        wcs = wc_por_zona.get(zona, [])
        wc_total = sum(wcs)
        wc_prom = wc_total / n_seg if n_seg else 0
        wc_med = sorted(wcs)[len(wcs)//2] if wcs else 0
        md.append(f"| {zona} | {n_seg} | {wc_total} | {wc_prom:.0f} | {wc_med} |")
    md.append("")

    # Casos con más segmentos (fragmentación)
    segs_por_caso = Counter()
    for seg in all_segmentos:
        segs_por_caso[seg["caso_id_canonico"]] += 1
    top_fragmentados = segs_por_caso.most_common(10)

    md.append("\n## 4. Top 10 casos más fragmentados\n")
    md.append("| caso_id | n_segmentos |")
    md.append("|---|---|")
    for caso_id, n_seg in top_fragmentados:
        md.append(f"| `{caso_id}` | {n_seg} |")
    md.append("")

    # Promedio de segmentos por caso
    avg_seg = len(all_segmentos) / n_procesados if n_procesados else 0
    md.append(f"\nPromedio de segmentos por caso: {avg_seg:.1f}\n")

    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"  [OK] {OUTPUT_MD.name}")

    # ── stdout: resumen ───────────────────────────────────────────────
    print(f"\n  Concordancia presencia dictamen: {n_presencia_ok}/{n_total}")
    print(f"  Concordancia wc_dictamen exacta: {n_wc_exacto}/{n_total}")
    if discrepantes_wc:
        print(f"  Discrepancias wc (delta>0): {len(discrepantes_wc)}")
        print(f"    Top 5 por delta absoluto:")
        for r in discrepantes_wc[:5]:
            print(f"      {r['caso_id']} (t{r['tomo']}): "
                  f"parser={r['wc_parser']} zonas={r['wc_zonas']} "
                  f"delta={r['delta']:+d}")

    # Resumen de zonas
    print(f"\n  Distribución de zonas:")
    for zona in ["sumario", "dictamen", "cuerpo", "dispositivo",
                 "firma", "voto_separado", "epilogo"]:
        n = zonas_counter.get(zona, 0)
        wc_t = sum(wc_por_zona.get(zona, []))
        print(f"    {zona:<16} {n:>6} segmentos  {wc_t:>10} palabras")


if __name__ == "__main__":
    main()
