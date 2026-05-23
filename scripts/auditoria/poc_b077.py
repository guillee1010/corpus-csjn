"""
PoC B077 — Validación completa contra corpus
=============================================

Escanea TODOS los archivos .md del corpus para:
  1. Detectar marcadores editoriales y verificar 0 FP en zona de fallos
  2. Simular el corte de detectar_fin_real (pista editorial_siguiente)
  3. Cuantificar impacto en wc de los casos afectados
  4. Generar preview del 4to CSV (csjn_casos_editorial.csv)

NO modifica parser.py ni ningún output. Solo lee y reporta.

Uso:
    cd corpus-csjn
    python scripts/auditoria/poc_b077.py

Requiere:
    - output/parser/csjn_casos.csv (post-H057)
    - corpus/*.md (archivos fuente)
"""

import re
import csv
from pathlib import Path
from collections import Counter, defaultdict

# ── Config ──────────────────────────────────────────────────────────────────

REPO_ROOT  = Path.cwd()
CASOS_CSV  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# ── Regex editoriales (candidatos para parser.py) ───────────────────────────

RE_EDITORIAL_ACORDADA = re.compile(
    r"^(?:A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s+Y\s+RESOLUCIONES\s*$"
    r"|ACORDADAS\s*$)", re.I
)
RE_EDITORIAL_DISCURSO = re.compile(r"^DISCURSOS\b", re.I)
RE_EDITORIAL_INDICE = re.compile(
    r"^(?:"
    r"INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)
RE_EDITORIAL_ANY = re.compile(
    r"^(?:"
    r"A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s+Y\s+RESOLUCIONES\s*$"
    r"|ACORDADAS\s*$"
    r"|DISCURSOS\b"
    r"|INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)


def es_marcador_editorial(linea):
    s = linea.strip()
    return bool(s and RE_EDITORIAL_ANY.match(s))


def tipo_zona_editorial(linea):
    s = linea.strip()
    if not s:
        return None
    if RE_EDITORIAL_ACORDADA.match(s):
        return "acordada"
    if RE_EDITORIAL_DISCURSO.match(s):
        return "discurso"
    if RE_EDITORIAL_INDICE.match(s):
        return "indice"
    return None


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("PoC B077 — Validación de marcadores editoriales")
    print("=" * 70)

    # 1. Cargar casos
    if not CASOS_CSV.exists():
        print(f"ERROR: no se encuentra {CASOS_CSV}")
        print("Ejecutar desde la raíz del repo: cd corpus-csjn")
        return

    casos = []
    with open(CASOS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            casos.append(row)
    print(f"Casos cargados: {len(casos)}")

    # 2. Agrupar por archivo, encontrar último caso por archivo
    por_archivo = defaultdict(list)
    for c in casos:
        por_archivo[c["source_file"]].append(c)

    ultimo_por_archivo = {}
    for sf, lista in por_archivo.items():
        # Último caso = mayor linea_fin_real
        lista_con_lfr = [(c, int(c["linea_fin_real"]))
                         for c in lista if c["linea_fin_real"]]
        if lista_con_lfr:
            ultimo = max(lista_con_lfr, key=lambda x: x[1])
            ultimo_por_archivo[sf] = {
                "caso": ultimo[0],
                "linea_fin_real": ultimo[1],
            }

    print(f"Archivos con casos: {len(ultimo_por_archivo)}")
    print()

    # 3. Escanear cada archivo
    total_fp = 0
    total_editorial_wc = 0
    total_editorial_lines = 0
    total_editorial_secciones = 0
    archivos_con_editorial = 0
    archivos_con_fp = 0
    cambios_detectar_fin = []
    all_editorial = []

    archivos_ordenados = sorted(ultimo_por_archivo.keys())
    for sf in archivos_ordenados:
        filepath = CORPUS_DIR / sf
        if not filepath.exists():
            continue

        info = ultimo_por_archivo[sf]
        ultimo_caso = info["caso"]
        lfr = info["linea_fin_real"]

        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
        n = len(lines)

        # 3a. Buscar marcadores editoriales en TODO el archivo
        marcadores_total = []
        for i, line in enumerate(lines):
            s = line.strip()
            if s and RE_EDITORIAL_ANY.match(s):
                marcadores_total.append((i, tipo_zona_editorial(line), s[:60]))

        if not marcadores_total:
            continue

        # 3b. Primer marcador después del último caso
        primer_post_caso = None
        for pos, tipo, txt in marcadores_total:
            if pos > lfr:
                primer_post_caso = pos
                break

        # 3c. Falsos positivos: marcadores DENTRO de la zona de fallos
        # (antes del linea_fin_real del último caso que NO es editorial)
        # Un marcador es FP si cae antes del primer marcador editorial legítimo
        # y dentro de un bloque de caso
        fp_en_fallos = []
        if primer_post_caso is not None:
            primer_editorial_real = primer_post_caso
        else:
            # Todos los marcadores están antes de lfr — revisar si alguno
            # está en un bloque de caso
            primer_editorial_real = n  # sentinel

        for pos, tipo, txt in marcadores_total:
            if pos <= lfr:
                # Está dentro de la zona de fallos
                # ¿Está dentro de un bloque de caso o en el epilogo del último?
                # Verificar: ¿algún caso tiene este pos entre su li y lfr?
                in_caso = False
                for c in por_archivo[sf]:
                    try:
                        c_li = int(c["linea_inicio"])
                        c_lfr = int(c["linea_fin_real"])
                    except (ValueError, KeyError):
                        continue
                    if c_li <= pos <= c_lfr:
                        in_caso = True
                        break
                if in_caso:
                    fp_en_fallos.append((pos, tipo, txt))

        n_fp = len(fp_en_fallos)
        total_fp += n_fp
        if n_fp:
            archivos_con_fp += 1

        # 3d. Contenido editorial: desde primer marcador post-caso hasta EOF
        if primer_post_caso is not None:
            editorial_lines = n - primer_post_caso
            editorial_wc = sum(len(lines[j].split())
                               for j in range(primer_post_caso, n))

            # Extraer secciones
            secciones = []
            zona_activa = None
            ini = primer_post_caso
            for k in range(primer_post_caso, n):
                nueva = tipo_zona_editorial(lines[k])
                if nueva and nueva != zona_activa:
                    if zona_activa:
                        wc = sum(len(lines[j].split()) for j in range(ini, k))
                        secciones.append({
                            "tomo": ultimo_caso["tomo"],
                            "source_file": sf,
                            "seccion": zona_activa,
                            "linea_ini": ini,
                            "linea_fin": k - 1,
                            "n_lineas": k - ini,
                            "wc": wc,
                        })
                    zona_activa = nueva
                    ini = k
            if zona_activa:
                wc = sum(len(lines[j].split()) for j in range(ini, n))
                secciones.append({
                    "tomo": ultimo_caso["tomo"],
                    "source_file": sf,
                    "seccion": zona_activa,
                    "linea_ini": ini,
                    "linea_fin": n - 1,
                    "n_lineas": n - ini,
                    "wc": wc,
                })

            all_editorial.extend(secciones)
            total_editorial_wc += editorial_wc
            total_editorial_lines += editorial_lines
            total_editorial_secciones += len(secciones)
            archivos_con_editorial += 1

            # 3e. ¿El corte cambia algo?
            # Simular: buscar primer marcador desde linea_inicio del último caso
            li_ultimo = int(ultimo_caso["linea_inicio"])
            primer_en_bloque = None
            for k in range(li_ultimo, n):
                if es_marcador_editorial(lines[k]):
                    primer_en_bloque = k
                    break

            if primer_en_bloque and primer_en_bloque <= lfr:
                # El último caso absorbe contenido editorial
                nuevo_lfr = primer_en_bloque - 1
                wc_old = sum(len(lines[j].split())
                             for j in range(li_ultimo, lfr + 1))
                wc_new = sum(len(lines[j].split())
                             for j in range(li_ultimo, nuevo_lfr + 1))
                cambios_detectar_fin.append({
                    "archivo": sf,
                    "caso": ultimo_caso["caso_id_canonico"],
                    "tomo": ultimo_caso["tomo"],
                    "lfr_old": lfr,
                    "lfr_new": nuevo_lfr,
                    "pista_old": ultimo_caso["pista_fin"],
                    "wc_old": wc_old,
                    "wc_new": wc_new,
                    "wc_saved": wc_old - wc_new,
                    "marker": lines[primer_en_bloque].strip()[:50],
                })

            # Imprimir por archivo
            tipo_counts = Counter(s["seccion"] for s in secciones)
            tipos_str = ", ".join(f"{t}={c}" for t, c in tipo_counts.items())
            fp_str = f" ⚠ {n_fp} FP!" if n_fp else ""
            print(f"  {sf}: {editorial_lines} ln, {editorial_wc:,} wc, "
                  f"{len(secciones)} sec ({tipos_str}){fp_str}")

    # ── Resumen ──────────────────────────────────────────────────────────────

    print()
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)

    print(f"\n1. FALSOS POSITIVOS")
    print(f"   Archivos escaneados: {len(archivos_ordenados)}")
    print(f"   Archivos con FP: {archivos_con_fp}")
    print(f"   Total FP en zona de fallos: {total_fp}")
    if archivos_con_fp:
        print("   ⚠ REVISAR antes de aplicar patch")
    else:
        print("   ✓ 0 FP — regex segura para producción")

    print(f"\n2. CONTENIDO EDITORIAL DETECTADO")
    print(f"   Archivos con editorial: {archivos_con_editorial}")
    print(f"   Total líneas editoriales: {total_editorial_lines:,}")
    print(f"   Total wc editorial: {total_editorial_wc:,}")
    print(f"   Total secciones: {total_editorial_secciones}")

    # Desglose por tipo
    tipo_global = Counter()
    wc_global = Counter()
    for s in all_editorial:
        tipo_global[s["seccion"]] += 1
        wc_global[s["seccion"]] += s["wc"]
    for tipo in sorted(tipo_global.keys()):
        print(f"     {tipo}: {tipo_global[tipo]} secciones, "
              f"{wc_global[tipo]:,} wc")

    print(f"\n3. IMPACTO EN detectar_fin_real")
    if cambios_detectar_fin:
        print(f"   Casos donde el corte cambia: {len(cambios_detectar_fin)}")
        total_wc_saved = sum(c["wc_saved"] for c in cambios_detectar_fin)
        print(f"   Total wc ahorrado: {total_wc_saved:,}")
        print()
        print(f"   {'Caso':<16} {'T':>4} {'LFR old':>8} {'LFR new':>8} "
              f"{'WC old':>8} {'WC new':>8} {'Saved':>8} Pista_old")
        for c in cambios_detectar_fin:
            print(f"   {c['caso']:<16} {c['tomo']:>4} {c['lfr_old']:>8} "
                  f"{c['lfr_new']:>8} {c['wc_old']:>8,} {c['wc_new']:>8,} "
                  f"{c['wc_saved']:>8,} {c['pista_old']}")
    else:
        print("   Ningún caso absorbe contenido editorial (ya cortados correctamente)")

    print(f"\n4. PREVIEW 4to CSV (csjn_casos_editorial.csv)")
    print(f"   Filas totales: {len(all_editorial)}")
    if all_editorial:
        print(f"\n   {'Tomo':>4} {'Archivo':<25} {'Seccion':<12} "
              f"{'Lineas':>7} {'WC':>8}")
        for s in all_editorial:
            print(f"   {s['tomo']:>4} {s['source_file']:<25} "
                  f"{s['seccion']:<12} {s['n_lineas']:>7} {s['wc']:>8,}")

    print()
    print("=" * 70)
    if total_fp == 0:
        print("✓ Listo para aplicar patch a parser.py")
    else:
        print("⚠ Revisar falsos positivos antes de patchear")


if __name__ == "__main__":
    main()
