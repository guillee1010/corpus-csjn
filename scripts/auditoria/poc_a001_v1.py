"""
PoC A001 v1: Firma independiente de dispositivo — validación full
=================================================================
Valida el impacto de integrar buscar_firma_inversa() como fallback
en procesar_archivo(). Usa las funciones EXACTAS que se insertarán
en parser.py (importa constantes de parser.py, no las redefine).

Flujo:
  1. Lee output/parser/csjn_casos.csv (baseline post-H046/B069).
  2. Para cada caso sin_firma (tipo_entrada=fallo), carga el bloque
     desde el corpus usando linea_inicio/linea_fin_real.
  3. Aplica buscar_firma_inversa() con guardas.
  4. Reporta mejoras (sin_firma → unanime/etc.) y estadísticas.
  5. Guarda CSV de diff en output/auditoria/poc_a001_diff.csv.

Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    python scripts/auditoria/poc_a001_v1.py

Requiere: parser.py en scripts/pipeline/ (importa funciones y constantes).
Lee: output/parser/csjn_casos.csv, corpus/*.md
"""

import sys
import re
import csv
from pathlib import Path
from collections import Counter

# ── Setup paths ──────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "pipeline"))

from parser import (
    linea_es_firma_de_juez,
    collect_firma_lines,
    parse_firma,
    RE_PAGE_HEADER,
    RE_APERTURA,
    RE_CONSIDERANDO,
    RE_FECHA_LINEA,
    JUECES_CONOCIDOS,
)

CASOS_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# ── Funciones A001 (código exacto que irá a parser.py) ───────────────

RE_DATOS_PARTES = re.compile(
    r"^(Recurso|Nombre del|Tribunal de origen|Tribunal que intervino|"
    r"Causa|Profesionales|Ministerio|Parte actora|Parte demandada)",
    re.I,
)

_SPAN_MINIMO_FIRMA_INVERSA = 20


def _encontrar_zona_fallo(bloque):
    """
    Encuentra el inicio de la zona del fallo propiamente dicho,
    excluyendo sumarios y dictamen del Procurador.

    Busca la ÚLTIMA ocurrencia de (en orden de prioridad):
    1. Apertura: "FALLO DE LA CORTE SUPREMA"
    2. Fecha: "Buenos Aires, ..."
    3. Considerando: "Considerando:"
    4. Vistos: "Vistos los autos:"

    Retorna el índice relativo al bloque, o None.
    """
    ultima_apertura = None
    ultima_fecha = None
    ultimo_cons = None
    ultimo_vistos = None
    for k in range(len(bloque)):
        s = bloque[k].strip()
        if RE_APERTURA.match(s):
            ultima_apertura = k
        if RE_FECHA_LINEA.match(s):
            ultima_fecha = k
        if RE_CONSIDERANDO.match(s):
            ultimo_cons = k
        if s.lower().startswith("vistos los autos"):
            ultimo_vistos = k
    if ultima_apertura is not None:
        return ultima_apertura
    if ultima_fecha is not None:
        return ultima_fecha
    if ultimo_cons is not None:
        return ultimo_cons
    if ultimo_vistos is not None:
        return ultimo_vistos
    return None


def buscar_firma_inversa(bloque, max_retroceso=80):
    """
    Busca firma desde el final del bloque hacia atrás.

    Retorna (firma_idx, firma_raw, motivo) donde motivo es:
      'ok'                   — firma encontrada
      'span_corto'           — bloque menor a _SPAN_MINIMO_FIRMA_INVERSA
      'sin_zona_fallo'       — no se encontró apertura/fecha/considerando
      'sin_firma_post_fallo' — zona de fallo encontrada pero sin firma
    """
    n = len(bloque)
    if n < _SPAN_MINIMO_FIRMA_INVERSA:
        return None, "", "span_corto"

    zona_fallo = _encontrar_zona_fallo(bloque)
    if zona_fallo is None:
        return None, "", "sin_zona_fallo"

    limite = max(zona_fallo, n - max_retroceso)

    firma_encontrada = None
    for k in range(n - 1, limite - 1, -1):
        s = bloque[k].strip()
        if not s:
            continue
        if RE_PAGE_HEADER.match(s):
            continue
        if RE_DATOS_PARTES.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_encontrada = k
            break

    if firma_encontrada is None:
        return None, "", "sin_firma_post_fallo"

    # Subir para encontrar el inicio de la firma (puede ser multi-línea)
    firma_inicio = firma_encontrada
    for k in range(firma_encontrada - 1, max(limite, firma_encontrada - 5) - 1, -1):
        s = bloque[k].strip()
        if not s:
            break
        if RE_PAGE_HEADER.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_inicio = k
        else:
            if any(p.search(s) for p, _ in JUECES_CONOCIDOS) and len(s) < 80:
                firma_inicio = k
            else:
                break

    firma_raw = collect_firma_lines(bloque, firma_inicio)
    return firma_inicio, firma_raw, "ok"


# ── Main ─────────────────────────────────────────────────────────────

def main():
    # Cargar casos sin_firma
    casos_sin_firma = []
    total_fallos = 0
    with open(CASOS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["tipo_entrada"] == "fallo":
                total_fallos += 1
                if row["voting_pattern"] == "sin_firma":
                    casos_sin_firma.append(row)

    print(f"Total fallos en CSV:     {total_fallos}")
    print(f"Casos sin_firma (fallos): {len(casos_sin_firma)}")
    print(f"{'='*70}")

    # Cache de archivos
    file_cache = {}

    recuperados = []
    no_recuperados = []
    errores = []

    for caso in casos_sin_firma:
        caso_id = caso["caso_id_canonico"]
        source_file = caso["source_file"]
        linea_inicio = int(caso["linea_inicio"])
        linea_fin_real = int(caso["linea_fin_real"])

        # Cargar archivo
        filepath = CORPUS_DIR / source_file
        if not filepath.exists():
            errores.append((caso_id, f"archivo no encontrado: {source_file}"))
            continue

        if source_file not in file_cache:
            with open(filepath, "r", encoding="utf-8") as f:
                file_cache[source_file] = f.readlines()

        lines = file_cache[source_file]
        start = max(0, linea_inicio - 1)
        end = min(len(lines), linea_fin_real)
        bloque = lines[start:end]

        if not bloque:
            errores.append((caso_id, "bloque vacío"))
            continue

        # Aplicar fallback A001
        firma_idx, firma_raw, motivo = buscar_firma_inversa(bloque)

        if firma_raw:
            parsed = parse_firma(firma_raw)
            n_jueces = len(parsed["jueces"])
            vp = parsed["voting_pattern"]
            jueces_str = ", ".join(j["nombre"] for j in parsed["jueces"])

            if n_jueces > 0:
                recuperados.append({
                    "caso_id": caso_id,
                    "tomo": caso["tomo"],
                    "outcome_actual": caso["outcome"],
                    "vp_antes": "sin_firma",
                    "vp_despues": vp,
                    "n_jueces": n_jueces,
                    "jueces": jueces_str,
                    "firma_raw_corta": firma_raw[:120].replace("\n", " "),
                    "firma_idx_rel": firma_idx,
                    "linea_abs": linea_inicio + firma_idx if firma_idx else None,
                    "motivo": "ok",
                    "span": len(bloque),
                })
            else:
                no_recuperados.append((caso_id, f"firma encontrada pero 0 jueces: {firma_raw[:80]}"))
        else:
            no_recuperados.append((caso_id, motivo))

    # ── Reporte ──────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"RESULTADOS PoC A001")
    print(f"{'='*70}")
    print(f"Total sin_firma:     {len(casos_sin_firma)}")
    print(f"Recuperados:         {len(recuperados)}")
    print(f"No recuperados:      {len(no_recuperados)}")
    print(f"Errores:             {len(errores)}")
    if casos_sin_firma:
        print(f"Tasa de recupero:    {len(recuperados)/len(casos_sin_firma)*100:.1f}%")
    print(f"\nImpacto en cobertura firma:")
    print(f"  Antes:  {total_fallos - len(casos_sin_firma)}/{total_fallos} "
          f"({100*(total_fallos - len(casos_sin_firma))/total_fallos:.1f}%)")
    n_post = total_fallos - len(casos_sin_firma) + len(recuperados)
    print(f"  Después: {n_post}/{total_fallos} "
          f"({100*n_post/total_fallos:.1f}%)")
    print(f"  sin_firma residual: {len(casos_sin_firma) - len(recuperados)}")

    # Desglose por tomo
    print(f"\n--- Recuperados por tomo ---")
    by_tomo = Counter(r["tomo"] for r in recuperados)
    for tomo in sorted(by_tomo.keys(), key=int):
        print(f"  Tomo {tomo}: {by_tomo[tomo]}")

    # Desglose por voting_pattern recuperado
    print(f"\n--- Voting patterns recuperados ---")
    by_vp = Counter(r["vp_despues"] for r in recuperados)
    for vp, n in by_vp.most_common():
        print(f"  {vp}: {n}")

    # Lista completa de recuperados
    print(f"\n--- Recuperados (todos) ---")
    for r in recuperados:
        print(f"  {r['caso_id']:15s} T{r['tomo']:>3s} | "
              f"{r['outcome_actual']:18s} | "
              f"{r['n_jueces']}J {r['vp_despues']:15s} | "
              f"{r['jueces'][:55]}")

    # Motivos de no recuperación
    print(f"\n--- Motivos de no recuperación ---")
    motivos = Counter(m for _, m in no_recuperados)
    for motivo, n in motivos.most_common():
        print(f"  {motivo[:55]:55s}: {n:3d}")

    # Primeros 10 no recuperados
    print(f"\n--- Primeros 10 no recuperados ---")
    for caso_id, motivo in no_recuperados[:10]:
        print(f"  {caso_id:15s} | {motivo[:60]}")

    if errores:
        print(f"\n--- Errores ---")
        for caso_id, err in errores[:5]:
            print(f"  {caso_id}: {err}")

    # Regresiones B069: verificar si se recuperan
    regresiones_b069 = {"330_p747", "330_p4071", "331_p548", "348_p1519"}
    recup_ids = {r["caso_id"] for r in recuperados}
    print(f"\n--- Regresiones B069 ---")
    for reg in sorted(regresiones_b069):
        if reg in recup_ids:
            r = next(x for x in recuperados if x["caso_id"] == reg)
            print(f"  {reg}: RECUPERADO → {r['vp_despues']}, {r['n_jueces']}J")
        elif any(reg == c_id for c_id, _ in no_recuperados):
            mot = next(m for c_id, m in no_recuperados if c_id == reg)
            print(f"  {reg}: no recuperado ({mot})")
        else:
            print(f"  {reg}: no está en sin_firma actual")

    # ── Guardar CSV de diff ──────────────────────────────────────────
    out_path = REPO_ROOT / "output" / "auditoria" / "poc_a001_diff.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if recuperados:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=recuperados[0].keys())
            w.writeheader()
            w.writerows(recuperados)
        print(f"\nCSV guardado: {out_path}")


if __name__ == "__main__":
    main()
