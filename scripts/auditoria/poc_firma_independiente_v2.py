"""
PoC H045: Firma independiente de dispositivo
=============================================
Prueba la hipótesis de que una búsqueda inversa (fin→inicio) con
linea_es_firma_de_juez() recupera firmas en casos sin_firma donde
el parser falló por no detectar el dispositivo.

Uso:
    cd C:\\Users\\guill\\Proyectos\\corpus-csjn
    python scripts/auditoria/poc_firma_independiente.py

Requiere: parser.py en scripts/pipeline/ (importa funciones).
Lee: output/parser/csjn_casos.csv, corpus/*.md

Antes de correr: aplicar patches B067 + B068 en parser.py (ver abajo).
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
    RE_DICT_HDR,
    RE_SUMARIO_LINK,
    JUECES_CONOCIDOS,
)

CASOS_CSV = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"

# ── Guardas contra falsos positivos ──────────────────────────────────

# Líneas que parecen firma pero no lo son:
# - Headers de sumario (IMPUESTO DE SELLOS, RECURSO EXTRAORDINARIO...)
# - Citas inline ("como dijo Petracchi en Fallos: 324:3876")
# - Datos de partes post-firma ("Recurso de queja interpuesto por...")

RE_SUMARIO_HEADER = re.compile(r"^[A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ\s:.,\-]{4,}$")
RE_DATOS_PARTES = re.compile(
    r"^(Recurso|Nombre del|Tribunal de origen|Tribunal que intervino|"
    r"Causa|Profesionales|Ministerio|Parte actora|Parte demandada)",
    re.I,
)

def es_zona_post_firma(bloque, idx):
    """Detecta si estamos en la zona de datos de partes (post-firma)."""
    s = bloque[idx].strip()
    return bool(RE_DATOS_PARTES.match(s))


# Patrones para encontrar el inicio de la zona válida (post-sumario)
RE_APERTURA_LOCAL = re.compile(
    r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I
)
RE_CONSIDERANDO_LOCAL = re.compile(r"^Considerando\s*[:.]?\s*$", re.I)
RE_FECHA_LOCAL = re.compile(
    r"^Buenos Aires[,]?\s+\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4}", re.I
)
RE_VISTOS_LOCAL = re.compile(r"^\s*Vistos los autos:", re.I)

# Span mínimo: un fallo real no puede tener menos de 20 líneas
SPAN_MINIMO = 20


def encontrar_zona_fallo(bloque):
    """
    Encuentra el inicio de la zona del fallo propiamente dicho,
    excluyendo sumarios y dictamen del Procurador.
    
    Busca (en orden de prioridad):
    1. Apertura: "FALLO DE LA CORTE SUPREMA"
    2. Fecha: "Buenos Aires, ..."
    3. Considerando: "Considerando:"
    4. Vistos: "Vistos los autos:"
    
    Retorna el índice relativo al bloque, o None si no encuentra nada.
    """
    # Buscar la ÚLTIMA apertura (por si hay una del dictamen antes)
    ultima_apertura = None
    for k in range(len(bloque)):
        s = bloque[k].strip()
        if RE_APERTURA_LOCAL.match(s):
            ultima_apertura = k
    if ultima_apertura is not None:
        return ultima_apertura
    
    # Buscar la última fecha "Buenos Aires"
    ultima_fecha = None
    for k in range(len(bloque)):
        s = bloque[k].strip()
        if RE_FECHA_LOCAL.match(s):
            ultima_fecha = k
    if ultima_fecha is not None:
        return ultima_fecha
    
    # Buscar último "Considerando:"
    ultimo_cons = None
    for k in range(len(bloque)):
        s = bloque[k].strip()
        if RE_CONSIDERANDO_LOCAL.match(s):
            ultimo_cons = k
    if ultimo_cons is not None:
        return ultimo_cons
    
    # Buscar "Vistos los autos:"
    for k in range(len(bloque)):
        s = bloque[k].strip()
        if RE_VISTOS_LOCAL.match(s):
            return k
    
    return None


def buscar_firma_inversa(bloque, max_retroceso=80):
    """
    Busca firma desde el final del bloque hacia atrás.
    
    Retorna (firma_idx, firma_raw) o (None, "").
    
    Guardas v2:
    - Solo busca DESPUÉS de la zona del fallo (post-apertura/considerando)
    - Si no encuentra zona de fallo → no busca (evita falsos en sumarios)
    - Ignora zona de datos de partes
    - Ignora page headers
    - Límite de retroceso
    """
    n = len(bloque)
    
    # Encontrar inicio de la zona del fallo
    zona_fallo = encontrar_zona_fallo(bloque)
    if zona_fallo is None:
        # Sin apertura, fecha, considerando ni vistos → no hay fallo parseable
        return None, "", "sin_zona_fallo"
    
    # Buscar desde el final hacia atrás, sin pasar de zona_fallo
    limite = max(zona_fallo, n - max_retroceso)
    
    firma_encontrada = None
    for k in range(n - 1, limite - 1, -1):
        s = bloque[k].strip()
        if not s:
            continue
        if RE_PAGE_HEADER.match(s):
            continue
        if es_zona_post_firma(bloque, k):
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
            # Verificar si es continuación de firma (línea corta con nombre)
            # que no matchea linea_es_firma_de_juez pero es parte de la firma
            if any(p.search(s) for p, _ in JUECES_CONOCIDOS) and len(s) < 80:
                firma_inicio = k
            else:
                break
    
    # Recolectar firma
    firma_raw = collect_firma_lines(bloque, firma_inicio)
    return firma_inicio, firma_raw, "ok"


# ── Main ─────────────────────────────────────────────────────────────

def main():
    # Cargar casos sin_firma
    casos_sin_firma = []
    with open(CASOS_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["voting_pattern"] == "sin_firma" and row["tipo_entrada"] == "fallo":
                casos_sin_firma.append(row)
    
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
        
        # Guarda: span mínimo — bloques muy cortos no contienen un fallo real
        span = len(bloque)
        if span < SPAN_MINIMO:
            no_recuperados.append((caso_id, f"span={span} < {SPAN_MINIMO} (bloque demasiado corto)"))
            continue
        
        # Buscar firma inversamente
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
                    "n_jueces": n_jueces,
                    "voting_pattern": vp,
                    "jueces": jueces_str,
                    "firma_raw_corta": firma_raw[:100].replace("\n", " "),
                    "firma_idx_rel": firma_idx,
                    "linea_abs": linea_inicio + firma_idx if firma_idx else None,
                })
            else:
                no_recuperados.append((caso_id, f"firma encontrada pero 0 jueces: {firma_raw[:80]}"))
        else:
            no_recuperados.append((caso_id, motivo))
    
    # ── Reporte ──────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"RESULTADOS")
    print(f"{'='*70}")
    print(f"Total sin_firma:    {len(casos_sin_firma)}")
    print(f"Recuperados:        {len(recuperados)}")
    print(f"No recuperados:     {len(no_recuperados)}")
    print(f"Errores:            {len(errores)}")
    print(f"Tasa de recupero:   {len(recuperados)/len(casos_sin_firma)*100:.1f}%")
    
    # Desglose por tomo
    print(f"\n--- Recuperados por tomo ---")
    by_tomo = Counter(r["tomo"] for r in recuperados)
    for tomo in sorted(by_tomo.keys(), key=int):
        print(f"  Tomo {tomo}: {by_tomo[tomo]}")
    
    # Desglose por voting_pattern recuperado
    print(f"\n--- Voting patterns recuperados ---")
    by_vp = Counter(r["voting_pattern"] for r in recuperados)
    for vp, n in by_vp.most_common():
        print(f"  {vp}: {n}")
    
    # Primeros 20 recuperados
    print(f"\n--- Primeros 20 recuperados ---")
    for r in recuperados[:20]:
        print(f"  {r['caso_id']:15s} | {r['n_jueces']}J | {r['voting_pattern']:15s} | {r['jueces'][:60]}")
    
    # Primeros 10 no recuperados
    print(f"\n--- Primeros 10 no recuperados ---")
    for caso_id, motivo in no_recuperados[:10]:
        print(f"  {caso_id:15s} | {motivo[:60]}")
    
    # Desglose de motivos
    print(f"\n--- Motivos de no recuperación ---")
    motivos = Counter(m for _, m in no_recuperados)
    for motivo, n in motivos.most_common():
        print(f"  {motivo[:50]:50s}: {n:3d}")
    
    if errores:
        print(f"\n--- Errores ---")
        for caso_id, err in errores[:5]:
            print(f"  {caso_id}: {err}")
    
    # Guardar CSV de recuperados
    out_path = REPO_ROOT / "output" / "auditoria" / "poc_firma_independiente.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if recuperados:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=recuperados[0].keys())
            w.writeheader()
            w.writerows(recuperados)
        print(f"\nCSV guardado: {out_path}")


if __name__ == "__main__":
    main()
