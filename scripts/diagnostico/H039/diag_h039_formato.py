"""
diag_h039_formato.py — Diagnóstico H039: formato no reconocido vs truncamiento
===============================================================================

Clasifica los ~249 casos sin_dispositivo + con_apertura en:
  - B1a (formato no reconocido): el bloque tiene texto resolutivo pero
    no matchea RE_DISPOSITIVO_VARIANTES.
  - B1b (truncamiento): el bloque no tiene texto resolutivo en la zona
    de búsqueda (el dispositivo cayó más allá de fin_real).

Para cada caso B1a, muestra las líneas candidatas a dispositivo que el
parser no reconoce, agrupadas por patrón. Esto permite diseñar las
variantes nuevas.

Uso (desde raíz del repo):
  $env:PYTHONIOENCODING = "utf-8"
  python scripts/diagnostico/H039/diag_h039_formato.py

Output:
  - Resumen cuantitativo a stdout.
  - Detalle en output/diagnostico/H039/diag_formato_detalle.md
"""

import csv
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

# ── Setup de imports ─────────────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent          # scripts/diagnostico/H039/
_REPO_ROOT = _SCRIPT_DIR.parent.parent.parent          # repo root
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from pipeline.parser import (
    RE_APERTURA,
    RE_DICT_HDR,
    RE_FECHA_LINEA,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    RE_POR_ELLO,
    RE_DISPOSITIVO_VARIANTES,
    RE_PAGE_HEADER,
    POR_ELLO_ARGUMENTAL,
    detectar_apertura_dispositivo,
    detectar_apertura_en_bloque,
    construir_bloque_desde_localizacion,
    detectar_fin_real,
    cargar_proximos_headers,
    cargar_localizados,
    proximo_header_despues_de,
    primer_token_de_caratula,
    refinar_inicio_por_titulo,
)

# ── Rutas ────────────────────────────────────────────────────────────────────

CSV_CASOS = _REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
LOCALIZADOS = _REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = _REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS_DIR = _REPO_ROOT / "corpus"
OUTPUT_DIR = _REPO_ROOT / "output" / "diagnostico" / "H039"

# ── Patrones resolutivos amplios (para detectar candidatos B1a) ──────────────
# Más permisivos que RE_DISPOSITIVO_VARIANTES: capturan cualquier texto
# que PUEDA ser un dispositivo, incluyendo variantes no reconocidas.

RE_RESOLUTIVO_AMPLIO = [
    ("se_resuelve",     re.compile(r"\bse\s+resuelve\b", re.I)),
    ("se_declara",      re.compile(r"\bse\s+declara\b", re.I)),
    ("se_confirma",     re.compile(r"\bse\s+confirma\b", re.I)),
    ("se_revoca",       re.compile(r"\bse\s+revoca\b", re.I)),
    ("se_rechaza",      re.compile(r"\bse\s+rechaza\b", re.I)),
    ("se_desestima",    re.compile(r"\bse\s+desestima\b", re.I)),
    ("se_hace_lugar",   re.compile(r"\bse\s+hace\s+lugar\b", re.I)),
    ("se_tiene",        re.compile(r"\bse\s+tiene\s+por\b", re.I)),
    ("notifiquese",     re.compile(r"\bnotif[íi]quese\b", re.I)),
    ("archivese",       re.compile(r"\barch[íi]vese\b", re.I)),
    ("cumplase",        re.compile(r"\bc[úu]mplase\b", re.I)),
    ("hagase_saber",    re.compile(r"\bh[áa]gase\s+saber\b", re.I)),
    ("el_tribunal_resuelve", re.compile(r"\bel\s+Tribunal\s+resuelve\b", re.I)),
    ("resolvio",        re.compile(r"\bresolvi[óo]\b", re.I)),
]


def cargar_csv_casos():
    """Carga CSV y filtra sin_dispositivo + con_apertura."""
    with open(CSV_CASOS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    target = []
    for r in rows:
        if r["tipo_entrada"] != "fallo":
            continue
        if r["voting_pattern"] != "sin_firma":
            continue
        if r["outcome"] != "sin_dispositivo":
            continue
        if r["apertura_tipo"] == "":
            continue
        target.append(r)
    return target


def cargar_archivo_md(filepath):
    """Lee un .md del corpus y devuelve lista de líneas."""
    with open(filepath, encoding="utf-8") as f:
        return f.readlines()


def reconstruir_bloque_para_caso(caso, filas_loc, headers_por_archivo, lines_cache):
    """
    Reconstruye el bloque de un caso tal como lo haría el parser,
    incluyendo fin_real y refinamiento de inicio.
    Devuelve (bloque, apertura_rel, inicio_busqueda, fin_busqueda) o None.
    """
    caso_id = caso["caso_id_canonico"]
    source_file = caso["source_file"]
    linea_inicio = int(caso["linea_inicio"])
    linea_fin_raw = caso["linea_fin"]
    linea_fin_real = int(caso["linea_fin_real"])

    filepath = CORPUS_DIR / source_file
    if not filepath.exists():
        return None

    if source_file not in lines_cache:
        lines_cache[source_file] = cargar_archivo_md(filepath)
    lines = lines_cache[source_file]

    # Construir bloque hasta fin_real
    bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin_real)
    if not bloque:
        return None

    # Detectar apertura
    apertura_tipo, apertura_rel = detectar_apertura_en_bloque(bloque)
    if apertura_rel is None:
        return None  # no debería pasar (filtrado por apertura_tipo != "")

    # Simular la cascada de inicio_busqueda del parser
    # Detectar dictamen
    en_dictamen = False
    lineas_dictamen = set()
    inicio_votos_indiv = None
    for k, bl in enumerate(bloque):
        stripped = bl.strip()
        if not stripped:
            continue
        if RE_DICT_HDR.match(stripped):
            en_dictamen = True
            lineas_dictamen.add(k)
            continue
        elif en_dictamen:
            if RE_APERTURA.match(stripped):
                en_dictamen = False
            else:
                lineas_dictamen.add(k)
                if RE_FECHA_LINEA.match(stripped) and k > 5:
                    prev = bloque[k - 1].strip() if k > 0 else ""
                    if prev and len(prev) < 80:
                        en_dictamen = False
                continue
        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            if inicio_votos_indiv is None:
                inicio_votos_indiv = k
            continue

    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    elif dictamen_end is not None:
        inicio_busqueda = dictamen_end + 1
    else:
        inicio_busqueda = 0

    if (inicio_votos_indiv is not None
            and (apertura_rel is None or inicio_votos_indiv > apertura_rel)):
        fin_busqueda = inicio_votos_indiv
    else:
        fin_busqueda = len(bloque)

    return (bloque, apertura_rel, inicio_busqueda, fin_busqueda, lineas_dictamen)


def buscar_resolutivos_en_zona(bloque, inicio, fin, lineas_dictamen):
    """
    Busca patrones resolutivos en la zona [inicio, fin) del bloque,
    excluyendo líneas de dictamen.
    Devuelve lista de (indice_rel, tipo, linea_texto).
    """
    hits = []
    for k in range(inicio, fin):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        for nombre, pat in RE_RESOLUTIVO_AMPLIO:
            if pat.search(stripped):
                hits.append((k, nombre, stripped))
                break  # solo el primer match por línea
    return hits


def verificar_dispositivo_parser(bloque, inicio, fin, lineas_dictamen):
    """
    Verifica si el parser detectaría algún dispositivo en la zona.
    Replica la lógica del parser (detectar_apertura_dispositivo).
    Devuelve True si hay al menos un match.
    """
    for k in range(inicio, fin):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, _ = detectar_apertura_dispositivo(stripped)
        if es_disp:
            return True
    return False


def main():
    print("Cargando datos...")
    target = cargar_csv_casos()
    print(f"Casos sin_dispositivo + con_apertura: {len(target)}")

    # Cache de archivos .md
    lines_cache = {}

    # Resultados
    b1a_casos = []    # formato no reconocido
    b1b_casos = []    # truncamiento
    errores = []
    parser_missed = [] # tiene resolutivo Y parser no lo detecta (confirmación)

    # Conteo de patrones resolutivos encontrados
    patron_counter = Counter()
    # Líneas candidatas agrupadas por inicio de línea
    lineas_candidatas = defaultdict(list)

    for i, caso in enumerate(target):
        caso_id = caso["caso_id_canonico"]
        result = reconstruir_bloque_para_caso(caso, None, None, lines_cache)
        if result is None:
            errores.append(caso_id)
            continue

        bloque, apertura_rel, inicio_busqueda, fin_busqueda, lineas_dictamen = result

        # Verificar que el parser no detecta dispositivo (sanity check)
        parser_detecta = verificar_dispositivo_parser(
            bloque, inicio_busqueda, fin_busqueda, lineas_dictamen
        )

        # Buscar resolutivos amplios
        hits = buscar_resolutivos_en_zona(
            bloque, inicio_busqueda, fin_busqueda, lineas_dictamen
        )

        if hits:
            b1a_casos.append({
                "caso_id": caso_id,
                "tomo": caso["tomo"],
                "hits": hits,
                "parser_detecta": parser_detecta,
                "n_lineas_zona": fin_busqueda - inicio_busqueda,
            })
            for _, tipo, linea in hits:
                patron_counter[tipo] += 1
                # Agrupar por los primeros 40 chars de la línea (para ver variantes)
                clave = linea[:60].strip()
                lineas_candidatas[clave].append(caso_id)
            if parser_detecta:
                parser_missed.append(caso_id)
        else:
            b1b_casos.append({
                "caso_id": caso_id,
                "tomo": caso["tomo"],
                "n_lineas_zona": fin_busqueda - inicio_busqueda,
            })

        if (i + 1) % 50 == 0:
            print(f"  procesados {i + 1}/{len(target)}...")

    # ── Resumen a stdout ─────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print(f"RESULTADOS DIAGNÓSTICO H039")
    print("=" * 70)
    print(f"Total casos analizados: {len(target)}")
    print(f"Errores (bloque no reconstruible): {len(errores)}")
    print(f"B1a (formato no reconocido): {len(b1a_casos)}")
    print(f"B1b (truncamiento probable): {len(b1b_casos)}")
    if parser_missed:
        print(f"⚠ Parser SÍ detecta dispositivo (sanity fail): {len(parser_missed)}")
    print()

    print("Patrones resolutivos encontrados en B1a:")
    for pat, count in patron_counter.most_common():
        print(f"  {pat}: {count}")
    print()

    print("B1a por tomo:")
    c_tomo = Counter(c["tomo"] for c in b1a_casos)
    for t, v in c_tomo.most_common(10):
        print(f"  tomo {t}: {v}")
    print()

    print("B1b por tomo:")
    c_tomo_b = Counter(c["tomo"] for c in b1b_casos)
    for t, v in c_tomo_b.most_common(10):
        print(f"  tomo {t}: {v}")

    # ── Detalle a archivo ────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "diag_formato_detalle.md"

    lines_out = []
    lines_out.append("# Diagnóstico H039 — Formato no reconocido vs Truncamiento")
    lines_out.append("")
    lines_out.append(f"Total casos: {len(target)}")
    lines_out.append(f"B1a (formato): {len(b1a_casos)}")
    lines_out.append(f"B1b (truncamiento): {len(b1b_casos)}")
    lines_out.append(f"Errores: {len(errores)}")
    lines_out.append("")

    lines_out.append("## B1a — Casos con texto resolutivo no reconocido")
    lines_out.append("")
    for c in sorted(b1a_casos, key=lambda x: x["caso_id"]):
        lines_out.append(f"### {c['caso_id']} (tomo {c['tomo']})")
        lines_out.append(f"Zona de búsqueda: {c['n_lineas_zona']} líneas")
        if c["parser_detecta"]:
            lines_out.append("⚠ Parser SÍ detecta — revisar lógica")
        for idx, tipo, linea in c["hits"]:
            lines_out.append(f"  - [{tipo}] línea rel {idx}: `{linea[:120]}`")
        lines_out.append("")

    lines_out.append("## Variantes de línea más frecuentes (agrupadas por inicio)")
    lines_out.append("")
    for clave, casos in sorted(lineas_candidatas.items(),
                                key=lambda x: -len(x[1])):
        if len(casos) >= 2:
            lines_out.append(f"- **{len(casos)}x** `{clave}`")
            lines_out.append(f"  Casos: {', '.join(casos[:10])}")
    lines_out.append("")

    lines_out.append("## B1b — Casos truncados (sin texto resolutivo)")
    lines_out.append("")
    for c in sorted(b1b_casos, key=lambda x: x["caso_id"]):
        lines_out.append(f"- {c['caso_id']} (tomo {c['tomo']}, zona {c['n_lineas_zona']} líneas)")

    out_path.write_text("\n".join(lines_out), encoding="utf-8")
    print(f"\nDetalle en: {out_path}")


if __name__ == "__main__":
    main()
