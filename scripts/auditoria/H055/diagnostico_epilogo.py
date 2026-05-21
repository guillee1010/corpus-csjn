"""
Diagnóstico H055-S1: marcadores de epílogo.

Lee los segmentos `epilogo` del zonas CSV, extrae el texto del corpus,
y reporta:
  1. Frecuencia de la primera línea no-vacía (para detectar subtipos)
  2. Frecuencia de TODAS las líneas que matchean patrones conocidos
  3. Ejemplos de las primeras líneas más comunes

Uso:
  cd corpus-csjn
  python scripts/auditoria/H055/diagnostico_epilogo.py
"""

import re
import csv
from collections import Counter, defaultdict
from pathlib import Path

ZONAS_CSV  = Path("output/parser/csjn_casos_zonas.csv")
CASOS_CSV  = Path("output/parser/csjn_casos.csv")
CORPUS_DIR = Path("corpus")

# ── Marcadores candidatos (RE_DATOS_PARTES + ampliados) ────────────
MARCADORES = [
    ("recurso",               re.compile(r"^Recurso\b", re.I)),
    ("tribunal_origen",       re.compile(r"^Tribunal de origen\b", re.I)),
    ("tribunal_intervino",    re.compile(r"^Tribunal que intervino\b", re.I)),
    ("tribunales_interv",     re.compile(r"^Tribunales? que intervin", re.I)),
    ("profesionales",         re.compile(r"^Profesionales?\b", re.I)),
    ("parte_actora",          re.compile(r"^Parte actora\b", re.I)),
    ("parte_demandada",       re.compile(r"^Parte demandada\b", re.I)),
    ("nombre_del",            re.compile(r"^Nombre del\b", re.I)),
    ("causa",                 re.compile(r"^Causa\b", re.I)),
    ("ministerio",            re.compile(r"^Ministerio\b", re.I)),
    ("traslado",              re.compile(r"^Traslado\b", re.I)),
    ("nota_secretaria",       re.compile(r"^Nota\s+(de\s+)?(la\s+)?Secretar", re.I)),
    ("cedula",                re.compile(r"^C[ée]dula\b", re.I)),
    ("expediente",            re.compile(r"^Expediente\b", re.I)),
    ("norma",                 re.compile(r"^Norma\b", re.I)),
    ("doctrina",              re.compile(r"^Doctrina\b", re.I)),
    ("citados",               re.compile(r"^Citados?\b", re.I)),
    ("fecha_sentencia",       re.compile(r"^Fecha\b", re.I)),
    ("materia",               re.compile(r"^Materia\b", re.I)),
    ("sumario_pie",           re.compile(r"^-\s*(Del|De la|De los)\b", re.I)),
    ("guion_largo",           re.compile(r"^[–—]\s*", re.I)),
    ("asterisco",             re.compile(r"^\(\*\)", re.I)),
    ("ver_fallo",             re.compile(r"^Ver (fallo|en http)", re.I)),
    ("registro",              re.compile(r"^Registro\b", re.I)),
    ("querellante",           re.compile(r"^Querellante\b", re.I)),
    ("imputado",              re.compile(r"^Imputado\b", re.I)),
    ("fiscal",                re.compile(r"^Fiscal\b", re.I)),
    ("defensor",              re.compile(r"^Defensor", re.I)),
    ("amicus",                re.compile(r"^Amicus\b", re.I)),
    ("procurador",            re.compile(r"^Procurador\b", re.I)),
    ("actor",                 re.compile(r"^Actor\b", re.I)),
    ("demandado",             re.compile(r"^Demandado\b", re.I)),
]

# ── Headers de página (ignorar) ────────────────────────────────────
RE_PAGE_HEADER = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N|\d{2,6})\s*$",
    re.I)


def main():
    # ── Cargar zonas ──────────────────────────────────────────────────
    epilogos = []
    with open(ZONAS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["zona"] == "epilogo":
                epilogos.append(row)

    # ── Cargar caso → source_file, linea_inicio ──────────────────────
    caso_meta = {}
    with open(CASOS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            caso_meta[row["caso_id_canonico"]] = {
                "source_file": row["source_file"],
                "linea_inicio": int(row["linea_inicio"]) if row["linea_inicio"] else 0,
            }

    # ── Cache de archivos ─────────────────────────────────────────────
    file_cache = {}
    def get_lines(source_file):
        if source_file not in file_cache:
            p = CORPUS_DIR / source_file
            if p.exists():
                file_cache[source_file] = p.read_text(encoding="utf-8").split("\n")
            else:
                file_cache[source_file] = None
        return file_cache[source_file]

    # ── Analizar cada segmento epilogo ────────────────────────────────
    primera_linea_counter = Counter()
    marcador_freq = Counter()       # marcador → n líneas totales
    marcador_epilogos = Counter()   # marcador → n epilogos que lo contienen
    lineas_por_epilogo = []
    sin_marcador_ejemplos = []
    total_epilogos = 0
    total_lineas_epilogo = 0

    for seg in epilogos:
        caso_id = seg["caso_id_canonico"]
        meta = caso_meta.get(caso_id)
        if not meta:
            continue

        lines = get_lines(meta["source_file"])
        if lines is None:
            continue

        li_caso = meta["linea_inicio"]
        li_seg = int(seg["linea_ini"]) + li_caso
        lf_seg = int(seg["linea_fin"]) + li_caso

        # Extraer texto del segmento
        seg_lines = []
        for k in range(li_seg, min(lf_seg + 1, len(lines))):
            seg_lines.append(lines[k])

        if not seg_lines:
            continue

        total_epilogos += 1
        total_lineas_epilogo += len(seg_lines)

        # Primera línea no-vacía, no-header
        primera = None
        for ln in seg_lines:
            s = ln.strip()
            if s and not RE_PAGE_HEADER.match(s):
                primera = s
                break

        if primera:
            # Normalizar: tomar las primeras 3 palabras para agrupar
            palabras = primera.split()[:3]
            clave = " ".join(palabras)
            primera_linea_counter[clave] += 1

        # Contar marcadores en TODAS las líneas del segmento
        marcadores_encontrados = set()
        for ln in seg_lines:
            s = ln.strip()
            if not s or RE_PAGE_HEADER.match(s):
                continue
            for nombre, pat in MARCADORES:
                if pat.match(s):
                    marcador_freq[nombre] += 1
                    marcadores_encontrados.add(nombre)
                    break

        for m in marcadores_encontrados:
            marcador_epilogos[m] += 1

        # Si ninguna línea matcheó marcador, guardar ejemplo
        if not marcadores_encontrados and primera:
            sin_marcador_ejemplos.append((caso_id, primera[:100]))

    # ── Reporte ───────────────────────────────────────────────────────
    print("=" * 70)
    print("Diagnóstico H055-S1: Marcadores de epílogo")
    print("=" * 70)
    print(f"Total segmentos epilogo:  {total_epilogos}")
    print(f"Total líneas en epilogo:  {total_lineas_epilogo}")
    print(f"Media líneas/epilogo:     {total_lineas_epilogo/total_epilogos:.1f}")
    print()

    print("── Top 30 primeras líneas (3 primeras palabras) ──")
    for clave, n in primera_linea_counter.most_common(30):
        print(f"  {n:>5}  {clave}")
    print()

    print("── Marcadores por frecuencia de líneas ──")
    print(f"  {'Marcador':<25} {'Líneas':>7} {'Epilogos':>9} {'% epilogos':>10}")
    for nombre, n in sorted(marcador_freq.items(), key=lambda x: -x[1]):
        n_ep = marcador_epilogos[nombre]
        pct = 100 * n_ep / total_epilogos
        print(f"  {nombre:<25} {n:>7} {n_ep:>9} {pct:>9.1f}%")
    print()

    total_con_marcador = sum(1 for seg_id in range(total_epilogos)
                             # Approximate: count via examples
                             )
    n_sin = len(sin_marcador_ejemplos)
    print(f"── Epilogos sin ningún marcador conocido: {n_sin} ──")
    if sin_marcador_ejemplos:
        for caso_id, ej in sin_marcador_ejemplos[:20]:
            print(f"  {caso_id:<20} {ej}")
        if n_sin > 20:
            print(f"  ... y {n_sin - 20} más")


if __name__ == "__main__":
    main()
