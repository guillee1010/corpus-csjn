"""
PoC H051 — Diagnóstico de los ~55 casos firma_no_detectada.
Fase 1: clasificar modo de falla SIN tocar código de producción.

Para cada caso con voting_pattern=sin_firma y span>=20:
  1. Reconstruye el bloque exacto (linea_inicio a linea_fin_real).
  2. Replay de detección de dispositivo (3 tiers).
  3. Replay de collect_firma_lines y buscar_firma_inversa.
  4. Escanea últimas 30 líneas buscando JUECES_CONOCIDOS.
  5. Escanea buscando patrones de firma no reconocidos.
  6. Clasifica modo de falla.

Uso (PowerShell, desde la raíz del repo):
  python scripts/auditoria/poc_diagnostico_firma_h051.py

Salida:
  scripts/auditoria/diagnostico_firma_h051.csv  (detalle por caso)
  stdout: resumen por modo de falla

Requiere:
  - output/parser/csjn_casos.csv (post-H050, 69 sin_firma)
  - corpus/*.md
  - scripts/pipeline/parser.py
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
    print(f"  Ajustá REPO_ROOT si el script no está en scripts/auditoria/H051/")
    sys.exit(1)

# Importar parser.py por path explícito (evita colisión con el módulo
# built-in 'parser' de Python)
_spec = importlib.util.spec_from_file_location("csjn_parser", str(PARSER_PATH))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Extraer lo que necesitamos
JUECES_CONOCIDOS = _mod.JUECES_CONOCIDOS
RE_APERTURA = _mod.RE_APERTURA
RE_FECHA_LINEA = _mod.RE_FECHA_LINEA
RE_CONSIDERANDO = _mod.RE_CONSIDERANDO
RE_POR_ELLO = _mod.RE_POR_ELLO
POR_ELLO_ARGUMENTAL = _mod.POR_ELLO_ARGUMENTAL
RE_DISPOSITIVO_VARIANTES = _mod.RE_DISPOSITIVO_VARIANTES
RE_DICT_HDR = _mod.RE_DICT_HDR
RE_VOTO_HDR = _mod.RE_VOTO_HDR
RE_DISID_HDR = _mod.RE_DISID_HDR
RE_PAGE_HEADER = _mod.RE_PAGE_HEADER
RE_CALIFICADOR = _mod.RE_CALIFICADOR
detectar_apertura_dispositivo = _mod.detectar_apertura_dispositivo
construir_bloque_desde_localizacion = _mod.construir_bloque_desde_localizacion
detectar_apertura_en_bloque = _mod.detectar_apertura_en_bloque
refinar_inicio_por_titulo = _mod.refinar_inicio_por_titulo
collect_firma_lines = _mod.collect_firma_lines
buscar_firma_inversa = _mod.buscar_firma_inversa
linea_es_firma_de_juez = _mod.linea_es_firma_de_juez
parse_firma = _mod.parse_firma

# ── Configuración ─────────────────────────────────────────────────────────────
CSV_CASOS = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"
OUTPUT_CSV = Path(__file__).resolve().parent / "diagnostico_firma_h051.csv"
SPAN_MINIMO = 20  # por debajo es bloque_corto/vacio, no firma_no_detectada


def cargar_casos_target():
    """Carga los casos firma_no_detectada con span >= SPAN_MINIMO."""
    with open(CSV_CASOS, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    targets = []
    for r in rows:
        if r["tipo_entrada"] != "fallo":
            continue
        if r["voting_pattern"] != "sin_firma":
            continue
        li = int(r["linea_inicio"]) if r["linea_inicio"] else 0
        lfr = int(r["linea_fin_real"]) if r["linea_fin_real"] else (
            int(r["linea_fin"]) if r["linea_fin"] else 0)
        span = lfr - li
        if span < SPAN_MINIMO:
            continue
        r["_span"] = span
        r["_li"] = li
        r["_lfr"] = lfr
        targets.append(r)
    return targets


def cargar_lines(source_file):
    """Carga las líneas del archivo .md del corpus."""
    path = CORPUS_DIR / source_file
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").split("\n")


# ── Regex para detectar posibles firmas no reconocidas ────────────────────────
# Busca líneas cortas con patrón de apellido en mayúsculas que podrían ser
# una firma de juez no incluida en JUECES_CONOCIDOS.
RE_POSIBLE_FIRMA = re.compile(
    r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ\s\.\,\-—–]+$"
)


def escanear_ultimas_lineas(bloque, n=30):
    """
    Escanea las últimas n líneas del bloque buscando:
    1. Matches de JUECES_CONOCIDOS (firma que el parser debería detectar)
    2. Líneas que parecen firma pero no matchean (candidatas no reconocidas)
    3. Líneas con rayas (separadores de firma)

    Retorna dict con los hallazgos.
    """
    inicio = max(0, len(bloque) - n)
    segmento = bloque[inicio:]

    jueces_encontrados = []
    candidatas_no_reconocidas = []
    lineas_con_raya = []

    for k, ln in enumerate(segmento):
        s = ln.strip()
        if not s:
            continue

        # ¿Matchea algún JUECES_CONOCIDOS?
        for pat, nombre in JUECES_CONOCIDOS:
            if pat.search(s):
                jueces_encontrados.append((inicio + k, nombre, s[:80]))
                break
        else:
            # No matcheó JUECES_CONOCIDOS. ¿Parece firma?
            # Criterios: línea corta, con rayas o punto final,
            # o con patrón de nombres propios
            es_corta = len(s) <= 100
            tiene_raya = "—" in s or " - " in s or "–" in s
            termina_punto = s.endswith(".")
            tiene_mayusculas = sum(1 for c in s if c.isupper()) >= 3

            if tiene_raya and tiene_mayusculas and es_corta:
                candidatas_no_reconocidas.append((inicio + k, s[:120]))
            elif termina_punto and tiene_mayusculas and len(s) <= 60:
                # Filtrar headers de página y otros falsos positivos
                if not RE_PAGE_HEADER.match(s) and not s.startswith("Recurso"):
                    candidatas_no_reconocidas.append((inicio + k, s[:120]))

            if tiene_raya:
                lineas_con_raya.append((inicio + k, s[:120]))

    return {
        "jueces_encontrados": jueces_encontrados,
        "candidatas_no_reconocidas": candidatas_no_reconocidas,
        "lineas_con_raya": lineas_con_raya,
    }


def replay_dispositivo(bloque, lineas_dictamen):
    """
    Replay simplificado de la detección de dispositivo (Tiers 1+3).
    No replica exactamente procesar_caso (que tiene apertura_rel, votos, etc.)
    pero captura lo esencial: ¿hay un dispositivo detectable?

    Retorna (por_ello_idx, por_ello_tipo, tier_usado).
    """
    # Detectar apertura para anclar búsqueda
    _tipo, apertura_rel = detectar_apertura_en_bloque(bloque)
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    else:
        dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
        if dictamen_end is not None:
            inicio_busqueda = dictamen_end + 1
        else:
            inicio_busqueda = 0

    # Tier 1: forward con validación de firma
    fallback_idx = None
    fallback_tipo = None
    for k in range(inicio_busqueda, len(bloque)):
        if k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        es_disp, tipo_disp = detectar_apertura_dispositivo(stripped)
        if es_disp:
            if fallback_idx is None:
                fallback_idx = k
                fallback_tipo = tipo_disp
            # Validación: firma en las 40 líneas siguientes
            if any(linea_es_firma_de_juez(bloque[j])
                   for j in range(k + 1, min(k + 41, len(bloque)))):
                return (k, tipo_disp, "tier1_validado")

    if fallback_idx is not None:
        return (fallback_idx, fallback_tipo, "tier1_fallback")

    return (None, None, "sin_dispositivo")


def detectar_dictamen(bloque):
    """Detecta líneas de dictamen para excluir de búsqueda de dispositivo."""
    lineas_dict = set()
    en_dict = False
    for k, ln in enumerate(bloque):
        s = ln.strip()
        if not s:
            continue
        if RE_DICT_HDR.match(s):
            en_dict = True
            lineas_dict.add(k)
            continue
        if en_dict:
            if RE_APERTURA.match(s):
                en_dict = False
            else:
                lineas_dict.add(k)
                if RE_FECHA_LINEA.match(s) and k > 5:
                    prev = bloque[k - 1].strip() if k > 0 else ""
                    if prev and len(prev) < 80:
                        en_dict = False
    return lineas_dict


def clasificar_modo_falla(tiene_disp, firma_forward, firma_inversa_motivo,
                          jueces_en_ultimas, candidatas):
    """
    Clasifica el modo de falla principal:
    - A: juez_no_en_lista — firma existe pero juez no está en JUECES_CONOCIDOS
    - B: sin_dispositivo — no se detectó dispositivo, inversa también falla
    - C: dispositivo_ok_firma_vacia — dispositivo detectado, collect_firma_lines vacío
    - D: inversa_sin_firma — buscar_firma_inversa no encuentra firma
    - E: formato_no_estandar — hay candidatas de firma pero sin match
    """
    if jueces_en_ultimas:
        # Hay jueces conocidos en las últimas 30 líneas pero el parser no
        # los capturó. El problema es de flujo, no de regex.
        if not tiene_disp:
            return "B_disp_faltante_juez_presente"
        else:
            return "C_disp_ok_juez_no_capturado"

    if candidatas:
        # Hay líneas que parecen firma pero no matchean JUECES_CONOCIDOS
        return "A_juez_no_en_lista"

    if not tiene_disp:
        return "B_sin_dispositivo_sin_firma"

    return "D_sin_pistas_firma"


def diagnosticar_caso(caso, lines):
    """Diagnóstico completo de un caso firma_no_detectada."""
    li = caso["_li"]
    lfr = caso["_lfr"]

    # Reconstruir bloque (como hace procesar_caso)
    bloque = construir_bloque_desde_localizacion(lines, li, lfr)
    if not bloque:
        return {"modo": "ERROR_bloque_vacio", "detalle": ""}

    # Refinar inicio (como hace procesar_caso)
    nombres_indice = caso.get("case_name_indice", "")
    offset, ancla = refinar_inicio_por_titulo(bloque, nombres_indice)
    if offset > 0:
        bloque = bloque[offset:]
        if not bloque:
            return {"modo": "ERROR_bloque_vacio_post_refine", "detalle": ""}

    span_real = len(bloque)

    # 1. Detectar dictamen
    lineas_dictamen = detectar_dictamen(bloque)

    # 2. Replay dispositivo
    pe_idx, pe_tipo, pe_tier = replay_dispositivo(bloque, lineas_dictamen)

    # 3. collect_firma_lines (si hay dispositivo)
    firma_forward = ""
    if pe_idx is not None:
        firma_forward = collect_firma_lines(bloque, pe_idx + 1)

    # 4. buscar_firma_inversa
    fi_idx, fi_raw, fi_motivo = buscar_firma_inversa(bloque)

    # 5. Escaneo de últimas 30 líneas
    escaneo = escanear_ultimas_lineas(bloque, n=30)

    # 6. Clasificar
    modo = clasificar_modo_falla(
        tiene_disp=(pe_idx is not None),
        firma_forward=firma_forward,
        firma_inversa_motivo=fi_motivo,
        jueces_en_ultimas=escaneo["jueces_encontrados"],
        candidatas=escaneo["candidatas_no_reconocidas"],
    )

    # 7. Extraer últimas 10 líneas para inspección manual
    ultimas_10 = []
    for ln in bloque[-10:]:
        s = ln.strip()
        if s:
            ultimas_10.append(s)
    ultimas_10_str = " | ".join(ultimas_10)

    # 8. Texto alrededor del dispositivo (si existe)
    contexto_disp = ""
    if pe_idx is not None:
        start = max(0, pe_idx - 1)
        end = min(len(bloque), pe_idx + 5)
        contexto_disp = " | ".join(
            bloque[k].strip() for k in range(start, end)
            if bloque[k].strip()
        )

    jueces_str = "; ".join(
        f"{nombre}@L{idx}" for idx, nombre, _ in escaneo["jueces_encontrados"]
    )
    candidatas_str = "; ".join(
        f"L{idx}: {txt}" for idx, txt in escaneo["candidatas_no_reconocidas"]
    )

    return {
        "caso_id": caso["caso_id_canonico"],
        "tomo": caso["tomo"],
        "span": caso["_span"],
        "span_real": span_real,
        "modo": modo,
        "tiene_dispositivo": "si" if pe_idx is not None else "no",
        "disp_tipo": pe_tipo or "",
        "disp_tier": pe_tier,
        "disp_idx": pe_idx if pe_idx is not None else "",
        "firma_forward": firma_forward[:120] if firma_forward else "",
        "firma_inversa_motivo": fi_motivo,
        "firma_inversa_raw": fi_raw[:120] if fi_raw else "",
        "jueces_ultimas30": jueces_str,
        "candidatas_firma": candidatas_str[:300],
        "ultimas_10": ultimas_10_str[:500],
        "contexto_dispositivo": contexto_disp[:300],
    }


def main():
    print("=" * 70)
    print("PoC H051 — Diagnóstico firma_no_detectada")
    print("=" * 70)

    # Cargar target
    targets = cargar_casos_target()
    print(f"\nCasos target (span >= {SPAN_MINIMO}): {len(targets)}")

    # Cache de archivos
    cache_lines = {}
    resultados = []

    for caso in targets:
        sf = caso["source_file"]
        if sf not in cache_lines:
            lines = cargar_lines(sf)
            if lines is None:
                print(f"  WARN: archivo no encontrado: {sf}")
                cache_lines[sf] = None
            else:
                cache_lines[sf] = lines

        lines = cache_lines[sf]
        if lines is None:
            resultados.append({
                "caso_id": caso["caso_id_canonico"],
                "tomo": caso["tomo"],
                "span": caso["_span"],
                "modo": "ERROR_archivo_no_encontrado",
            })
            continue

        diag = diagnosticar_caso(caso, lines)
        resultados.append(diag)

    # ── Resumen por modo de falla ──────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RESUMEN POR MODO DE FALLA")
    print("=" * 70)

    modos = Counter(r["modo"] for r in resultados)
    for modo, cnt in modos.most_common():
        print(f"\n  {modo}: {cnt} casos")
        casos_modo = [r for r in resultados if r["modo"] == modo]
        for c in casos_modo[:5]:  # mostrar hasta 5 ejemplos
            disp = c.get("tiene_dispositivo", "?")
            inv = c.get("firma_inversa_motivo", "?")
            print(f"    {c['caso_id']} (t{c['tomo']}, span={c.get('span_real', c['span'])})"
                  f" disp={disp} inv={inv}")
            if c.get("jueces_ultimas30"):
                print(f"      jueces encontrados: {c['jueces_ultimas30']}")
            if c.get("candidatas_firma"):
                print(f"      candidatas: {c['candidatas_firma'][:200]}")
            if c.get("ultimas_10"):
                print(f"      últimas: {c['ultimas_10'][:200]}")
        if len(casos_modo) > 5:
            print(f"    ... y {len(casos_modo) - 5} más")

    # ── Distribución por tomo ──────────────────────────────────────────────────
    print("\n" + "-" * 40)
    print("Distribución por tomo:")
    tomos = Counter(r["tomo"] for r in resultados)
    for t, cnt in sorted(tomos.items(), key=lambda x: int(x[0])):
        modos_tomo = Counter(r["modo"] for r in resultados if r["tomo"] == t)
        modos_str = ", ".join(f"{m}:{c}" for m, c in modos_tomo.most_common())
        print(f"  T{t}: {cnt}  ({modos_str})")

    # ── Exportar CSV diagnóstico ──────────────────────────────────────────────
    fieldnames = [
        "caso_id", "tomo", "span", "span_real", "modo",
        "tiene_dispositivo", "disp_tipo", "disp_tier", "disp_idx",
        "firma_forward", "firma_inversa_motivo", "firma_inversa_raw",
        "jueces_ultimas30", "candidatas_firma",
        "ultimas_10", "contexto_dispositivo",
    ]
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in resultados:
            writer.writerow(r)
    print(f"\n[OK] CSV diagnóstico: {OUTPUT_CSV}")

    # ── Conteo final ──────────────────────────────────────────────────────────
    print(f"\nTotal diagnosticados: {len(resultados)}")
    print(f"Distribución: {dict(modos.most_common())}")

    # ── Veredicto preliminar ──────────────────────────────────────────────────
    n_juez_no_lista = modos.get("A_juez_no_en_lista", 0)
    n_flujo = (modos.get("B_disp_faltante_juez_presente", 0) +
               modos.get("C_disp_ok_juez_no_capturado", 0))
    n_sin_pistas = (modos.get("B_sin_dispositivo_sin_firma", 0) +
                    modos.get("D_sin_pistas_firma", 0))

    print(f"\n{'='*70}")
    print("VEREDICTO PRELIMINAR")
    print(f"{'='*70}")
    print(f"  Regex faltante (modo A):      {n_juez_no_lista}")
    print(f"  Problema de flujo (B/C):      {n_flujo}")
    print(f"  Sin pistas de firma (B/D):    {n_sin_pistas}")
    if n_juez_no_lista > n_flujo + n_sin_pistas:
        print("  → Mayoría modo A: fixes PUNTUALES (regex/JUECES_CONOCIDOS)")
    elif n_flujo > n_juez_no_lista + n_sin_pistas:
        print("  → Mayoría problemas de flujo: evaluar REFACCIÓN C")
    else:
        print("  → Distribución mixta: revisar CSV para decisión manual")


if __name__ == "__main__":
    main()
