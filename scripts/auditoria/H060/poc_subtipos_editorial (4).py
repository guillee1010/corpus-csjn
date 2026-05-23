"""
H060 PoC — Detección de subtipos editoriales por títulos-mojón.

Escanea cada bloque editorial, busca la primera aparición de cada
título conocido, y clasifica las secciones entre mojones consecutivos.

Correr: python scripts/auditoria/H060/poc_subtipos_editorial.py

Convenciones del repo:
- No modifica parser.py ni CSVs canónicos.
- Output a stdout + CSV de comparación en scripts/auditoria/H060/.
"""
import re
import sys
import pandas as pd
from pathlib import Path

# Resolver repo root desde la ubicación del script
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR
while REPO_ROOT != REPO_ROOT.parent:
    if (REPO_ROOT / "corpus").is_dir() and (REPO_ROOT / "output").is_dir():
        break
    REPO_ROOT = REPO_ROOT.parent
else:
    print("ERROR: no encontré la raíz del repo (busco carpetas corpus/ y output/)")
    sys.exit(1)

CORPUS = REPO_ROOT / "corpus"
CURRENT_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos_editorial.csv"
OUTPUT_CSV = SCRIPT_DIR / "poc_editorial_subtipos.csv"

# ── Títulos-mojón ─────────────────────────────────────────────────────
# Cada uno aparece ~1 vez por archivo y marca el INICIO de una sección.
# Orden: más específico primero (evitar match parcial).
TITLE_MARKERS = [
    ("indice_partes",      re.compile(
        r"^INDICE POR LOS NOMBRES DE LAS PARTES\s*$", re.I)),
    ("indice_materias",    re.compile(
        r"^INDICE ALFAB[EÉ]TICO POR MATERIAS", re.I)),
    ("indice_legislacion", re.compile(
        r"^INDICE DE LEGISLACI[OÓ]N\s*\(\*\)", re.I)),
    ("acordadas",          re.compile(
        r"^ACORDADAS DE LA CSJN\s*$", re.I)),
    ("discurso",           re.compile(
        r"^DISCURSOS\s*$", re.I)),
    ("indice_general",     re.compile(
        r"^INDICE GENERAL\s*$", re.I)),
]

# ── Openers: determinan el subtipo inicial del bloque ─────────────────
# Se chequean contra las primeras líneas no vacías.
OPENER_MARKERS = [
    ("discurso",           re.compile(r"^DISCURSOS\b", re.I)),
    ("acordadas",          re.compile(
        r"^A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S", re.I)),
    ("acordadas",          re.compile(
        r"^ACORDADAS\s+Y\s+RESOLUCIONES\s*$", re.I)),
    ("acordadas",          re.compile(
        r"^ACORDADAS DE LA CSJN\s*$", re.I)),
    ("indice_legislacion", re.compile(
        r"^INDICE DE LEGISLACI[OÓ]N", re.I)),
    ("indice_partes",      re.compile(
        r"^NOMBRES DE LAS PARTES\s*$", re.I)),
    ("indice_partes",      re.compile(
        r"^INDICE POR LOS NOMBRES", re.I)),
]


def detectar_subtipo_inicial(lines, li, lf):
    """Subtipo de la primera sección, basado en las primeras líneas."""
    for i in range(li, min(li + 10, lf + 1)):
        s = lines[i].strip()
        if not s:
            continue
        for subtipo, rx in OPENER_MARKERS:
            if rx.match(s):
                return subtipo
        break  # solo la primera línea no vacía
    return "desconocido"


def encontrar_mojones(lines, li, lf):
    """Primera aparición de cada título-mojón en el bloque."""
    found = {}  # subtipo -> linea
    for i in range(li, lf + 1):
        s = lines[i].strip()
        if not s:
            continue
        for subtipo, rx in TITLE_MARKERS:
            if subtipo not in found and rx.match(s):
                found[subtipo] = i
                break
    return found


# ── Patrones de línea de TOC (INDICE GENERAL) ────────────────────────
RE_TOC_DOTS = re.compile(r"\.{4,}")                  # "Fallos ........"
RE_TOC_PAGE = re.compile(r"^\(?\d+\)?\s*$")          # "5", "(1)", "(175)"
RE_TOC_VOL  = re.compile(r"^Volumen\s+", re.I)       # "Volumen I"
RE_TOC_TOMO = re.compile(r"^Tomo\s+\d", re.I)        # "Tomo 330"
RE_TOC_PAG  = re.compile(r"^Pág\.\s*$", re.I)        # "Pág."


def _es_linea_toc(linea):
    """¿La línea es parte del TOC (INDICE GENERAL)?"""
    s = linea.strip()
    if not s:
        return True  # líneas vacías dentro del TOC
    if RE_TOC_DOTS.search(s):
        return True
    if RE_TOC_PAGE.match(s):
        return True
    if RE_TOC_VOL.match(s):
        return True
    if RE_TOC_TOMO.match(s):
        return True
    if RE_TOC_PAG.match(s):
        return True
    if s == "INDICE GENERAL":
        return True
    return False


def detectar_fin_toc(lines, pos_ig, linea_fin):
    """
    Encuentra la última línea de indice_general buscando el último
    marcador fuerte de TOC.

    Marcadores fuertes: líneas con puntos suspensivos (entries del TOC),
    headers de volumen, Tomo, Pág., "INDICE GENERAL".
    NO incluye: números sueltos, líneas vacías, HOJA COMPLEMENTARIA
    (aparece tanto en el cuerpo como al final de archivos).
    """
    ultima_fuerte = pos_ig  # al menos INDICE GENERAL mismo

    for i in range(pos_ig, min(linea_fin + 1, len(lines))):
        s = lines[i].strip()
        if not s:
            continue
        if (RE_TOC_DOTS.search(s)
                or RE_TOC_VOL.match(s)
                or RE_TOC_TOMO.match(s)
                or RE_TOC_PAG.match(s)
                or s == "INDICE GENERAL"):
            ultima_fuerte = i

    # Incluir líneas vacías y números de página que sigan al último
    # marcador fuerte (son parte del TOC pero no son "fuertes").
    fin = ultima_fuerte
    for i in range(ultima_fuerte + 1, min(linea_fin + 1, len(lines))):
        s = lines[i].strip()
        if not s or RE_TOC_PAGE.match(s):
            fin = i
        else:
            break

    return fin

    return linea_fin  # nunca salió del TOC → todo es TOC


def clasificar_editorial(lines, linea_ini, linea_fin, tomo, source_file):
    """
    Clasifica el bloque editorial en secciones con subtipos.

    Retorna lista de dicts:
        tomo, source_file, subtipo, linea_ini, linea_fin, n_lineas, wc
    """
    if linea_ini >= len(lines):
        return []
    linea_fin = min(linea_fin, len(lines) - 1)

    # 1. Subtipo inicial
    tipo_ini = detectar_subtipo_inicial(lines, linea_ini, linea_fin)

    # 2. Mojones
    mojones = encontrar_mojones(lines, linea_ini, linea_fin)

    # 3. Posición de INDICE GENERAL (si existe)
    pos_ig = mojones.get("indice_general")

    # 4. Filtrar mojones espurios: títulos dentro del indice_general
    #    (ej: "Indice por los nombres de las partes" como entrada del TOC,
    #     a < 30 líneas del INDICE GENERAL).
    if pos_ig is not None:
        mojones_filtrados = {}
        for sub, pos in mojones.items():
            if sub == "indice_general":
                mojones_filtrados[sub] = pos
            elif pos < pos_ig:
                # Título ANTES de INDICE GENERAL: legítimo.
                # Pero filtrar si está demasiado cerca (probable TOC).
                if (pos_ig - pos) > 30:
                    mojones_filtrados[sub] = pos
                else:
                    # Muy cerca de INDICE GENERAL → probable entrada del TOC
                    pass
            # Títulos DESPUÉS de INDICE GENERAL: ignorar
        mojones = mojones_filtrados

    # 5. Construir boundaries ordenadas
    #    Cada boundary = (linea, subtipo)
    boundaries = []

    # Agregar mojones que NO coinciden con el tipo inicial en las
    # primeras líneas (para evitar duplicar la sección inicial)
    for sub, pos in sorted(mojones.items(), key=lambda x: x[1]):
        if pos <= linea_ini + 5 and sub == tipo_ini:
            continue  # ya cubierto por el tipo inicial
        if not boundaries and pos > linea_ini + 5:
            # Hay gap entre inicio y primer mojón → sección inicial
            boundaries.append((linea_ini, tipo_ini))
        boundaries.append((pos, sub))

    # Si no hubo mojones (o todos filtrados), todo es tipo_ini
    if not boundaries:
        boundaries = [(linea_ini, tipo_ini)]
    # Si el primer boundary no empieza en linea_ini, agregar la inicial
    elif boundaries[0][0] > linea_ini:
        boundaries.insert(0, (linea_ini, tipo_ini))

    # 6. Generar secciones
    secciones = []
    for idx, (li, subtipo) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            lf = boundaries[idx + 1][0] - 1
        else:
            lf = linea_fin

        # Truncar indice_general al último marcador fuerte de TOC.
        # Descarta contenido post-TOC (ej: acumulativo en 330.4).
        if subtipo == "indice_general":
            lf_toc = detectar_fin_toc(lines, li, lf)
            if lf_toc < lf:
                descartado = lf - lf_toc
                print(f"  TRUNCADO {source_file}: indice_general L{li}–L{lf_toc} "
                      f"({descartado} líneas post-TOC descartadas)")
                lf = lf_toc

        n = lf - li + 1
        wc = sum(len(lines[j].split()) for j in range(li, min(lf + 1, len(lines))))

        secciones.append({
            "tomo": tomo,
            "source_file": source_file,
            "subtipo": subtipo,
            "linea_ini": li,
            "linea_fin": lf,
            "n_lineas": n,
            "wc": wc,
        })

    return secciones


# ── Main ──────────────────────────────────────────────────────────────

def main():
    df_actual = pd.read_csv(CURRENT_CSV)

    # Agrupar por archivo
    archivos = df_actual.groupby("source_file").agg(
        tomo=("tomo", "first"),
        linea_min=("linea_ini", "min"),
        linea_max=("linea_fin", "max"),
    ).reset_index().sort_values(["tomo", "source_file"])

    todas = []

    for _, row in archivos.iterrows():
        sf = row["source_file"]
        fp = CORPUS / sf
        if not fp.exists():
            print(f"  SKIP {sf} (no encontrado)")
            continue

        lines = fp.read_text(encoding="utf-8").splitlines()
        li = int(row["linea_min"])
        lf = min(int(row["linea_max"]), len(lines) - 1)
        tomo = int(row["tomo"])

        secciones = clasificar_editorial(lines, li, lf, tomo, sf)
        todas.extend(secciones)

    df_new = pd.DataFrame(todas)

    # ── Reporte ───────────────────────────────────────────────────────
    print("=" * 72)
    print(f"RESULTADO: {len(df_new)} secciones detectadas")
    print(f"  (CSV actual: {len(df_actual)} secciones)")
    print()

    # Subtipos
    print("Subtipos encontrados:")
    for sub, cnt in df_new["subtipo"].value_counts().items():
        print(f"  {sub:25s}  {cnt}")
    print()

    # Por archivo
    print("=" * 72)
    print("DETALLE POR ARCHIVO:")
    for sf in df_new["source_file"].unique():
        secs = df_new[df_new["source_file"] == sf].sort_values("linea_ini")
        tomo = secs.iloc[0]["tomo"]
        print(f"\n  T{tomo} {sf}:")
        for _, s in secs.iterrows():
            print(f"    {s['subtipo']:25s}  L{s['linea_ini']:6d}–{s['linea_fin']:6d}"
                  f"  ({s['n_lineas']:6d} líneas, {s['wc']:7d} wc)")

    # ── Comparación de cobertura ──────────────────────────────────────
    print()
    print("=" * 72)
    print("COBERTURA vs CSV ACTUAL:")
    for sf in archivos["source_file"]:
        actual = df_actual[df_actual["source_file"] == sf]
        nuevo = df_new[df_new["source_file"] == sf]

        if actual.empty or nuevo.empty:
            continue

        rango_actual = (actual["linea_ini"].min(), actual["linea_fin"].max())
        rango_nuevo = (nuevo["linea_ini"].min(), nuevo["linea_fin"].max())
        wc_actual = actual["wc"].sum()
        wc_nuevo = nuevo["wc"].sum()

        if rango_actual != rango_nuevo or wc_actual != wc_nuevo:
            print(f"  DIFF {sf}:")
            print(f"    rango actual: {rango_actual}  nuevo: {rango_nuevo}")
            print(f"    wc actual: {wc_actual}  nuevo: {wc_nuevo}")
        else:
            tomo = actual.iloc[0]["tomo"]
            n_actual = len(actual)
            n_nuevo = len(nuevo)
            print(f"  OK   T{tomo} {sf}: {n_actual}→{n_nuevo} secciones, "
                  f"rango={rango_actual}, wc={wc_actual}")

    # ── Guardar ───────────────────────────────────────────────────────
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_new.to_csv(OUTPUT_CSV, index=False)
    print(f"\nCSV guardado: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
