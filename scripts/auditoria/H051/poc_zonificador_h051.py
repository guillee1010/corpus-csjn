"""
PoC H051 — Zonificador de bloques (Paso 1, Refacción C).

Asigna una etiqueta de zona a cada línea de un bloque de fallo.
NO modifica el parser ni el flujo actual. Solo anota y reporta.

Zonas detectadas (en orden típico de un fallo completo):
  header_pagina   — ruido de paginación (tomo, página, "FALLOS DE LA CORTE...")
  sumario         — headers temáticos editoriales en MAYÚSCULAS + texto editorial
  dictamen        — dictamen del Procurador
  apertura        — "FALLO/SENTENCIA DE LA CORTE SUPREMA"
  cuerpo          — cuerpo del fallo (Vistos, Considerando, argumentos)
  dispositivo     — "Por ello..." y variantes
  firma           — nombres de jueces con rayas/calificadores
  voto_separado   — votos individuales y disidencias
  epilogo         — metadata post-firma/post-votos (Tribunal de origen, etc.)
  intersticio     — líneas no clasificadas

Algoritmo: 3 pasadas.
  Pasada 0: marcar headers de página (ruido transversal)
  Pasada 1: detectar anclas (marcadores estructurales) con posición
  Pasada 2: propagar zonas entre anclas

Uso (PowerShell, desde raíz del repo):
  python scripts/auditoria/H051/poc_zonificador_h051.py
  python scripts/auditoria/H051/poc_zonificador_h051.py --verbose
  python scripts/auditoria/H051/poc_zonificador_h051.py --caso 329_p1554

Salida:
  stdout: resumen de concordancia con parser actual + estadísticas de zonas
  scripts/auditoria/H051/zonificacion_h051.csv  (resumen por caso)
"""

import sys
import csv
import re
import random
import importlib.util
import argparse
from pathlib import Path
from collections import Counter, defaultdict

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

# Importar lo necesario del parser
JUECES_CONOCIDOS = _mod.JUECES_CONOCIDOS
RE_APERTURA = _mod.RE_APERTURA
RE_FECHA_LINEA = _mod.RE_FECHA_LINEA
RE_CONSIDERANDO = _mod.RE_CONSIDERANDO
RE_DICT_HDR = _mod.RE_DICT_HDR
RE_VOTO_HDR = _mod.RE_VOTO_HDR
RE_DISID_HDR = _mod.RE_DISID_HDR
RE_PAGE_HEADER = _mod.RE_PAGE_HEADER
RE_CALIFICADOR = _mod.RE_CALIFICADOR
RE_DATOS_PARTES = _mod.RE_DATOS_PARTES
detectar_apertura_dispositivo = _mod.detectar_apertura_dispositivo
construir_bloque_desde_localizacion = _mod.construir_bloque_desde_localizacion
refinar_inicio_por_titulo = _mod.refinar_inicio_por_titulo
linea_es_firma_de_juez = _mod.linea_es_firma_de_juez
linea_es_header_sumario = _mod.linea_es_header_sumario

# ── Configuración ─────────────────────────────────────────────────────────────
CSV_CASOS = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"
OUTPUT_CSV = Path(__file__).resolve().parent / "zonificacion_h051.csv"
OUTPUT_MD = Path(__file__).resolve().parent / "zonificacion_h051_reporte.md"

# Regex adicional para "Vistos los autos" (sin requerir comilla)
RE_VISTOS = re.compile(r"^\s*Vistos? los autos", re.I)

# Remisión a precedente/dictamen — señal fuerte de sumario editorial
# Patrones: "–Del dictamen de la Procuración General, al que remitió..."
#           "–Del precedente 'X' (Fallos: ...), al que remitió..."
RE_REMISION = re.compile(
    r"^[–—-]\s*Del\s+(dictamen|precedente|voto|fallo)",
    re.I
)


# ══════════════════════════════════════════════════════════════════════════════
# ZONIFICADOR
# ══════════════════════════════════════════════════════════════════════════════

def zonificar_bloque(bloque):
    """
    Asigna una zona a cada línea del bloque.

    Retorna:
      zonas: list[str]  — etiqueta de zona para cada línea (len == len(bloque))
      anclas: list[tuple] — (linea, tipo_marcador) detectadas en pasada 1
    """
    n = len(bloque)
    zonas = ["intersticio"] * n
    anclas = []

    # ── Pasada 0: headers de página ──────────────────────────────────────
    for k in range(n):
        s = bloque[k].strip()
        if not s:
            continue
        if RE_PAGE_HEADER.match(s):
            zonas[k] = "header_pagina"

    # ── Pasada 1: detectar anclas ────────────────────────────────────────
    # Recorre el bloque una vez, registra marcadores con su posición.
    # Un marcador en una línea ya marcada como header_pagina se ignora.
    for k in range(n):
        if zonas[k] == "header_pagina":
            continue
        s = bloque[k].strip()
        if not s:
            continue

        # Orden de prioridad: marcadores más específicos primero

        # Dictamen
        if RE_DICT_HDR.match(s):
            anclas.append((k, "dictamen_inicio"))
            continue

        # Apertura (FALLO/SENTENCIA DE LA CORTE SUPREMA)
        if RE_APERTURA.match(s):
            anclas.append((k, "apertura"))
            continue

        # Fecha
        if RE_FECHA_LINEA.match(s):
            anclas.append((k, "fecha"))
            continue

        # Considerando
        if RE_CONSIDERANDO.match(s):
            anclas.append((k, "considerando"))
            continue

        # Vistos los autos
        if RE_VISTOS.match(s):
            anclas.append((k, "vistos"))
            continue

        # Voto/Disidencia header
        if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
            anclas.append((k, "voto_header"))
            continue

        # Dispositivo
        es_disp, tipo_disp = detectar_apertura_dispositivo(s)
        if es_disp:
            anclas.append((k, "dispositivo"))
            continue

        # Firma de juez
        if linea_es_firma_de_juez(bloque[k]):
            anclas.append((k, "firma_linea"))
            continue

        # Sumario editorial header — ANTES de epilogo para ganar prioridad.
        # "RECURSO EXTRAORDINARIO: Requisitos..." es sumario, no epilogo.
        if linea_es_header_sumario(bloque[k]):
            anclas.append((k, "sumario_header"))
            continue

        # Remisión a precedente/dictamen — señal de sumario editorial
        if RE_REMISION.match(s):
            anclas.append((k, "sumario_header"))
            continue

        # Epílogo (Tribunal de origen, Recurso de, etc.)
        # Guarda contextual: solo es epilogo si ya vimos firma, voto o
        # dispositivo. Un "Recurso de..." antes de eso es parte del
        # cuerpo o sumario, no epilogo.
        if RE_DATOS_PARTES.match(s):
            ya_paso_firma = any(t in ("firma_linea", "voto_header", "dispositivo")
                                for _, t in anclas)
            if ya_paso_firma:
                anclas.append((k, "epilogo_marker"))
                continue

    # ── Pasada 2: propagar zonas entre anclas ────────────────────────────
    # Recorre las anclas en orden y asigna zonas hacia adelante.
    # Cada ancla "abre" una zona que se cierra con la siguiente ancla.

    zona_activa = "intersticio"

    # Construir mapa de anclas por posición para lookup rápido
    ancla_en = {}
    for pos, tipo in anclas:
        ancla_en[pos] = tipo

    # Recorrido forward: la zona activa se propaga hasta la próxima ancla
    for k in range(n):
        if zonas[k] == "header_pagina":
            continue  # headers de página mantienen su etiqueta siempre

        s = bloque[k].strip()

        if k in ancla_en:
            tipo = ancla_en[k]
            # Transición de zona según el marcador
            if tipo == "sumario_header":
                zona_activa = "sumario"
            elif tipo == "dictamen_inicio":
                zona_activa = "dictamen"
            elif tipo == "apertura":
                zona_activa = "apertura"
            elif tipo == "fecha":
                # Fecha marca transición a cuerpo (si venimos de apertura
                # o dictamen). Si venimos de dictamen y la fecha es del
                # dictamen, no cambia zona — pero eso se detecta por la
                # presencia de apertura después.
                if zona_activa in ("apertura", "intersticio", "sumario"):
                    zona_activa = "cuerpo"
                # Si estamos en dictamen, la fecha puede ser del dictamen
                # (no cambia zona) o puede marcar fin de dictamen.
                # Heurística: si hay apertura después, es fecha del dictamen.
                elif zona_activa == "dictamen":
                    # Mirar si hay apertura más adelante
                    hay_apertura_despues = any(
                        t == "apertura" for p, t in anclas if p > k
                    )
                    if not hay_apertura_despues:
                        zona_activa = "cuerpo"
                    # si hay apertura después, la fecha es del dictamen, no cambiar
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

        # Asignar zona (si no es header_pagina, que ya fue asignado)
        if zonas[k] != "header_pagina":
            zonas[k] = zona_activa

    return zonas, anclas


def resumen_zonas(zonas):
    """Cuenta líneas por zona y detecta rangos contiguos."""
    conteo = Counter(zonas)
    # Detectar rangos contiguos de cada zona
    rangos = {}
    zona_actual = None
    inicio_actual = 0
    for k, z in enumerate(zonas):
        if z != zona_actual:
            if zona_actual is not None:
                rangos.setdefault(zona_actual, []).append((inicio_actual, k - 1))
            zona_actual = z
            inicio_actual = k
    if zona_actual is not None:
        rangos.setdefault(zona_actual, []).append((inicio_actual, len(zonas) - 1))
    return conteo, rangos


def imprimir_bloque_anotado(bloque, zonas, caso_id, max_lineas=None):
    """Imprime bloque con etiqueta de zona por línea."""
    print(f"\n{'═'*78}")
    print(f"  {caso_id}")
    print(f"{'═'*78}")
    n = len(bloque)
    if max_lineas and n > max_lineas:
        # Mostrar primeras y últimas líneas
        mitad = max_lineas // 2
        rango = list(range(mitad)) + [-1] + list(range(n - mitad, n))
    else:
        rango = list(range(n))

    for k in rango:
        if k == -1:
            print(f"  {'...':<16} ... ({n - max_lineas} líneas omitidas) ...")
            continue
        zona = zonas[k]
        linea = bloque[k].rstrip()
        # Color-code por zona (abreviatura)
        abrev = {
            "header_pagina": "HDR",
            "sumario": "SUM",
            "dictamen": "DIC",
            "apertura": "APE",
            "cuerpo": "CUE",
            "dispositivo": "DIS",
            "firma": "FIR",
            "voto_separado": "VOT",
            "epilogo": "EPI",
            "intersticio": "---",
        }
        tag = abrev.get(zona, zona[:3].upper())
        # Truncar línea para display
        if len(linea) > 58:
            linea = linea[:55] + "..."
        print(f"  {tag:<4} L{k:>4}  {linea}")


# ══════════════════════════════════════════════════════════════════════════════
# CARGA DE DATOS Y EJECUCIÓN
# ══════════════════════════════════════════════════════════════════════════════

def cargar_todos_los_casos():
    """Carga todos los fallos del CSV."""
    with open(CSV_CASOS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cargar_lines(source_file, cache):
    """Carga las líneas del archivo .md, con cache."""
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


def comparar_con_parser(caso, zonas):
    """
    Compara la zonificación con los campos del parser actual.
    Retorna dict con concordancias/discrepancias.
    """
    resultado = {}

    # 1. ¿El parser detectó dictamen? vs ¿zonificador tiene zona dictamen?
    parser_dictamen = caso.get("dictamen_presente", "") == "1"
    zonif_dictamen = "dictamen" in zonas
    resultado["dictamen_parser"] = parser_dictamen
    resultado["dictamen_zonif"] = zonif_dictamen
    resultado["dictamen_concuerda"] = parser_dictamen == zonif_dictamen

    # 2. ¿El parser detectó dispositivo? vs ¿zonificador tiene zona dispositivo?
    parser_disp = caso.get("outcome", "") != "sin_dispositivo"
    zonif_disp = "dispositivo" in zonas
    resultado["disp_parser"] = parser_disp
    resultado["disp_zonif"] = zonif_disp
    resultado["disp_concuerda"] = parser_disp == zonif_disp

    # 3. ¿El parser detectó firma? vs ¿zonificador tiene zona firma?
    parser_firma = caso.get("voting_pattern", "") != "sin_firma"
    zonif_firma = "firma" in zonas
    resultado["firma_parser"] = parser_firma
    resultado["firma_zonif"] = zonif_firma
    resultado["firma_concuerda"] = parser_firma == zonif_firma

    # 4. ¿Tiene zona cuerpo? (si no, probablemente es sumario editorial)
    zonif_cuerpo = "cuerpo" in zonas
    resultado["tiene_cuerpo"] = zonif_cuerpo

    # 5. Clasificación propuesta
    if not zonif_cuerpo and not zonif_disp:
        resultado["clasif_zonif"] = "sumario_editorial"
    elif zonif_disp and zonif_firma:
        resultado["clasif_zonif"] = "fallo_completo"
    elif zonif_disp and not zonif_firma:
        resultado["clasif_zonif"] = "fallo_sin_firma"
    elif zonif_cuerpo and not zonif_disp:
        resultado["clasif_zonif"] = "fallo_sin_dispositivo"
    else:
        resultado["clasif_zonif"] = "indeterminado"

    return resultado


def main():
    ap = argparse.ArgumentParser(description="PoC Zonificador H051")
    ap.add_argument("--seed", type=int, default=42, help="Seed para muestreo")
    ap.add_argument("--n", type=int, default=100, help="Tamaño de muestra")
    ap.add_argument("--verbose", action="store_true",
                    help="Imprimir bloques anotados")
    ap.add_argument("--caso", type=str, default=None,
                    help="Diagnosticar un caso específico (ej: 329_p1554)")
    ap.add_argument("--todos", action="store_true",
                    help="Correr sobre TODOS los casos (no muestreo)")
    ap.add_argument("--solo-sin-firma", action="store_true",
                    help="Correr solo sobre los sin_firma")
    ap.add_argument("--max-lineas", type=int, default=80,
                    help="Máx líneas a mostrar en modo verbose")
    args = ap.parse_args()

    print("=" * 70)
    print("PoC H051 — Zonificador de bloques (Refacción C, Paso 1)")
    print("=" * 70)

    todos = cargar_todos_los_casos()
    fallos = [r for r in todos if r["tipo_entrada"] == "fallo"]
    print(f"\nFallos en CSV: {len(fallos)}")

    # Seleccionar muestra
    if args.caso:
        muestra = [r for r in fallos if r["caso_id_canonico"] == args.caso]
        if not muestra:
            print(f"ERROR: caso {args.caso} no encontrado")
            sys.exit(1)
        print(f"Modo: caso individual {args.caso}")
        args.verbose = True  # forzar verbose para caso individual
    elif args.solo_sin_firma:
        muestra = [r for r in fallos if r["voting_pattern"] == "sin_firma"]
        print(f"Modo: solo sin_firma ({len(muestra)} casos)")
    elif args.todos:
        muestra = fallos
        print(f"Modo: todos ({len(muestra)} casos)")
    else:
        # Muestreo estratificado: incluir todos los sin_firma + random del resto
        sin_firma = [r for r in fallos if r["voting_pattern"] == "sin_firma"]
        con_firma = [r for r in fallos if r["voting_pattern"] != "sin_firma"]
        random.seed(args.seed)
        n_con = min(args.n - len(sin_firma), len(con_firma))
        muestra_con = random.sample(con_firma, n_con) if n_con > 0 else []
        muestra = sin_firma + muestra_con
        random.shuffle(muestra)
        print(f"Modo: muestreo (seed={args.seed}, n={len(muestra)}: "
              f"{len(sin_firma)} sin_firma + {len(muestra_con)} con_firma)")

    # Procesar
    cache_lines = {}
    resultados = []

    for caso in muestra:
        sf = caso["source_file"]
        lines = cargar_lines(sf, cache_lines)
        if lines is None:
            continue

        bloque = reconstruir_bloque(caso, lines)
        if bloque is None or len(bloque) < 2:
            continue

        zonas, anclas = zonificar_bloque(bloque)
        conteo, rangos = resumen_zonas(zonas)
        comparacion = comparar_con_parser(caso, set(zonas))

        caso_id = caso["caso_id_canonico"]

        if args.verbose:
            imprimir_bloque_anotado(bloque, zonas, caso_id,
                                   max_lineas=args.max_lineas)
            # Resumen de zonas para este caso
            print(f"\n  Zonas: ", end="")
            for z in ["sumario", "dictamen", "apertura", "cuerpo",
                       "dispositivo", "firma", "voto_separado", "epilogo",
                       "header_pagina", "intersticio"]:
                if conteo.get(z, 0) > 0:
                    print(f"{z}={conteo[z]}", end="  ")
            print()
            print(f"  Parser: firma={caso['voting_pattern']}"
                  f"  outcome={caso['outcome']}"
                  f"  dictamen={'sí' if caso.get('dictamen_presente')=='1' else 'no'}")
            print(f"  Zonif:  clasif={comparacion['clasif_zonif']}"
                  f"  firma={'sí' if comparacion['firma_zonif'] else 'no'}"
                  f"  disp={'sí' if comparacion['disp_zonif'] else 'no'}"
                  f"  cuerpo={'sí' if comparacion['tiene_cuerpo'] else 'no'}")

        resultados.append({
            "caso_id": caso_id,
            "tomo": caso["tomo"],
            "span": len(bloque),
            "parser_firma": caso["voting_pattern"],
            "parser_outcome": caso["outcome"],
            "parser_dictamen": caso.get("dictamen_presente", ""),
            "zonif_clasif": comparacion["clasif_zonif"],
            "zonif_firma": comparacion["firma_zonif"],
            "zonif_disp": comparacion["disp_zonif"],
            "zonif_cuerpo": comparacion["tiene_cuerpo"],
            "zonif_dictamen": comparacion["dictamen_zonif"],
            "concuerda_firma": comparacion["firma_concuerda"],
            "concuerda_disp": comparacion["disp_concuerda"],
            "concuerda_dictamen": comparacion["dictamen_concuerda"],
            "n_sumario": conteo.get("sumario", 0),
            "n_dictamen": conteo.get("dictamen", 0),
            "n_cuerpo": conteo.get("cuerpo", 0),
            "n_dispositivo": conteo.get("dispositivo", 0),
            "n_firma": conteo.get("firma", 0),
            "n_voto": conteo.get("voto_separado", 0),
            "n_epilogo": conteo.get("epilogo", 0),
            "n_header": conteo.get("header_pagina", 0),
            "n_intersticio": conteo.get("intersticio", 0),
        })

    # ══════════════════════════════════════════════════════════════════════
    # GENERAR REPORTE (.md) + CSV
    # ══════════════════════════════════════════════════════════════════════

    _parser_key = {"firma": "parser_firma", "disp": "parser_outcome",
                   "dictamen": "parser_dictamen"}

    md = []
    md.append(f"# Zonificación H051 — Reporte\n")
    md.append(f"Casos procesados: {len(resultados)}\n")

    # ── Concordancia ──────────────────────────────────────────────────
    md.append(f"\n## Concordancia zonificador vs parser\n")
    for campo in ["firma", "disp", "dictamen"]:
        concuerda = sum(1 for r in resultados if r[f"concuerda_{campo}"])
        total = len(resultados)
        pct = 100 * concuerda / total if total else 0
        discrepancias = [r for r in resultados if not r[f"concuerda_{campo}"]]
        md.append(f"\n### {campo}: {concuerda}/{total} ({pct:.1f}%)\n")
        if discrepancias:
            md.append(f"Discrepancias ({len(discrepancias)}):\n")
            for r in discrepancias:
                md.append(f"- `{r['caso_id']}` (t{r['tomo']}, span={r['span']}): "
                          f"parser={r[_parser_key[campo]]} zonif={r[f'zonif_{campo}']}")
            md.append("")

    # ── Clasificación ─────────────────────────────────────────────────
    md.append(f"\n## Clasificación por zonificador\n")
    clasifs = Counter(r["zonif_clasif"] for r in resultados)
    md.append(f"| Clasificación | Total | sin_firma del parser |")
    md.append(f"|---|---|---|")
    for c, cnt in clasifs.most_common():
        n_sf = sum(1 for r in resultados
                   if r["zonif_clasif"] == c and r["parser_firma"] == "sin_firma")
        md.append(f"| {c} | {cnt} | {n_sf} |")
    md.append("")

    # ── Candidatos a reclasificar ─────────────────────────────────────
    sumario_candidates = [r for r in resultados
                          if r["zonif_clasif"] == "sumario_editorial"
                          and r["parser_firma"] == "sin_firma"]
    if sumario_candidates:
        md.append(f"\n## Candidatos a reclasificar como sumario_editorial ({len(sumario_candidates)})\n")
        md.append(f"Estos casos tienen `voting_pattern=sin_firma` en el parser pero el "
                  f"zonificador no detecta ni cuerpo ni dispositivo.\n")
        for r in sumario_candidates:
            md.append(f"- `{r['caso_id']}` (t{r['tomo']}, span={r['span']})")
        md.append("")

    # ── Fallos sin firma con firma detectada por zonificador ──────────
    firma_recovered = [r for r in resultados
                       if r["parser_firma"] == "sin_firma"
                       and r["zonif_firma"] == True]
    if firma_recovered:
        md.append(f"\n## Fallos sin_firma donde el zonificador SÍ ve firma ({len(firma_recovered)})\n")
        md.append(f"Posible firma del caso anterior en el bloque, o firma que el parser no alcanzó.\n")
        for r in firma_recovered:
            md.append(f"- `{r['caso_id']}` (t{r['tomo']}, span={r['span']}, "
                      f"clasif={r['zonif_clasif']})")
        md.append("")

    # ── Distribución de zonas promedio ────────────────────────────────
    md.append(f"\n## Distribución promedio de zonas (sobre {len(resultados)} casos)\n")
    zona_names = ["n_sumario", "n_dictamen", "n_cuerpo", "n_dispositivo",
                  "n_firma", "n_voto", "n_epilogo", "n_header", "n_intersticio"]
    md.append(f"| Zona | Total líneas | Promedio | Casos con zona |")
    md.append(f"|---|---|---|---|")
    for zn in zona_names:
        total_lineas = sum(r[zn] for r in resultados)
        promedio = total_lineas / len(resultados) if resultados else 0
        casos_con = sum(1 for r in resultados if r[zn] > 0)
        nombre = zn.replace("n_", "")
        md.append(f"| {nombre} | {total_lineas} | {promedio:.1f} | {casos_con} |")
    md.append("")

    # ── Escribir .md ──────────────────────────────────────────────────
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")

    # ── Escribir .csv ─────────────────────────────────────────────────
    fieldnames = list(resultados[0].keys()) if resultados else []
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)

    # ── stdout: resumen mínimo ────────────────────────────────────────
    n_sf = sum(1 for r in resultados if r["parser_firma"] == "sin_firma")
    n_sumario_ed = clasifs.get("sumario_editorial", 0)
    n_completo = clasifs.get("fallo_completo", 0)
    n_sin_firma_z = clasifs.get("fallo_sin_firma", 0)

    print(f"\n  Procesados: {len(resultados)}")
    print(f"  Concordancia — firma: {sum(1 for r in resultados if r['concuerda_firma'])}/{len(resultados)}"
          f"  disp: {sum(1 for r in resultados if r['concuerda_disp'])}/{len(resultados)}"
          f"  dictamen: {sum(1 for r in resultados if r['concuerda_dictamen'])}/{len(resultados)}")
    print(f"  Clasificación — completo: {n_completo}  sin_firma: {n_sin_firma_z}"
          f"  sumario_editorial: {n_sumario_ed}")
    if sumario_candidates:
        print(f"  Candidatos a reclasificar (sin_firma → sumario): {len(sumario_candidates)}")
    if firma_recovered:
        print(f"  sin_firma con firma visible en bloque: {len(firma_recovered)}")
    print(f"\n  [OK] {OUTPUT_MD.name}")
    print(f"  [OK] {OUTPUT_CSV.name}")


if __name__ == "__main__":
    main()
