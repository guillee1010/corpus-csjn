"""
diag_b095_token_corto.py — Diagnóstico B095 (H075)

Examina los 51 casos ancla_catalogo cuyo primer_token_de_caratula tiene <4 chars.
Para cada uno, lee el .md fuente y muestra las primeras 50 líneas del bloque
desde linea_inicio, marcando qué señales estructurales están presentes.

Objetivo: determinar qué señal (o combinación) puede anclar el inicio del caso
cuando el token de carátula es demasiado corto para matching seguro.

Uso:
    python scripts/auditoria/H075/diag_b095_token_corto.py

Requiere:
    - output/parser/csjn_casos.csv
    - corpus/*.md
"""

import csv
import re
import unicodedata
from pathlib import Path
from collections import Counter

# ── Config ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CSV_PATH = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
CORPUS_DIR = REPO_ROOT / "corpus"
WINDOW = 50  # líneas a inspeccionar desde linea_inicio

# ── Regexes (copiadas de parser.py para consistencia) ─────────────────────────
RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I)
RE_FECHA = re.compile(r"^Buenos Aires[,]?\s+\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4}", re.I)
RE_VISTOS_STRICT = re.compile(r'^\s*Vistos los autos:\s*[\u201C\u201D"\u2018\u2019\']', re.I)
RE_VISTOS_BROAD = re.compile(r'^\s*(Vistos los autos|Autos y [Vv]istos)', re.I)
RE_CONSIDERANDO = re.compile(r'^\s*Considerando:', re.I)
RE_PAGE_HEADER = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACIÓN|"
    r"DE JUSTICIA DE LA NACION|\d{2,6})\s*$", re.I)
RE_FIRMA = re.compile(
    r"(PETRACCHI|HIGHTON|MAQUEDA|ZAFFARONI|LORENZETTI|FAYT|ARGIBAY|"
    r"BOGGIANO|BELLUSCIO|VÁZQUEZ|ROSENKRANTZ|ROSATTI|MOLINE\s*O'CONNOR)",
    re.I)
RE_DICTAMEN_HEADER = re.compile(r"^\s*DICTAMEN\s+DE", re.I)

# ── Lógica de primer_token (replicada de parser.py) ──────────────────────────
_SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
         "empresa", "compania", "compañia", "compañía"}
_GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
              "afip", "buenos", "nacional", "administracion",
              "federal", "direccion", "instituto"}


def _strip_accents(s):
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def primer_token(nombres_indice):
    if not nombres_indice:
        return ""
    variantes = nombres_indice.split("|")
    for v in variantes:
        tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", v.strip())
        for t in tokens:
            if len(t) >= 4 and t.lower() not in _SKIP and t.lower() not in _GENERICOS:
                return t
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", variantes[0].strip())
    for t in tokens:
        if len(t) >= 4 and t.lower() not in _SKIP:
            return t
    return tokens[0] if tokens else ""


# ── Builders de pattern para nombre completo ──────────────────────────────────

def build_fullname_pattern(case_name_indice):
    """
    Construye un regex a partir del nombre completo del catálogo (primera variante).
    
    Ej: "N. N."   → r"N\.\s*N\."
        "P., S. D." → r"P\.,\s*S\.\s*D\."
        "D.G.A."  → r"D\.G\.A\."
        "EMM S.R.L." → r"EMM\s+S\.R\.L\."
    
    Devuelve (pattern_str, compiled_re) o (None, None) si no se pudo armar.
    """
    if not case_name_indice:
        return None, None
    
    first_variant = case_name_indice.split("|")[0].strip()
    # Limpiar prefijos editoriales: "(4) ", "(5) "
    first_variant = re.sub(r"^\(\d+\)\s*", "", first_variant)
    
    if len(first_variant) < 2:
        return None, None
    
    # Escapar y flexibilizar espacios
    pat = re.escape(first_variant)
    # Permitir espacios variables
    pat = re.sub(r"\\ ", r"\\s+", pat)
    # Permitir espacio opcional después de punto
    pat = re.sub(r"\\\.", r"\\.\\s*", pat)
    
    try:
        compiled = re.compile(pat, re.I)
        return first_variant, compiled
    except re.error:
        return None, None


def build_cuerpo_tokens(case_name_cuerpo, min_len=5):
    """
    Extrae tokens largos del case_name_cuerpo para matching alternativo.
    Devuelve lista de tokens únicos >= min_len, sin genéricos.
    """
    if not case_name_cuerpo:
        return []
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", case_name_cuerpo)
    seen = set()
    result = []
    for t in tokens:
        tl = t.lower()
        if (len(t) >= min_len
                and tl not in _SKIP
                and tl not in _GENERICOS
                and tl not in seen
                and tl not in {"recurso", "hecho", "deducido", "causa", "parte",
                               "demandada", "actora", "defensora", "oficial"}):
            seen.add(tl)
            result.append(t)
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Leer CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    
    # Filtrar: ancla_catalogo + token corto
    target = []
    for r in rows:
        if "ancla_catalogo" not in r["status_localizacion"]:
            continue
        tok = primer_token(r["case_name_indice"])
        if len(tok) < 4:
            target.append((r, tok))
    
    print(f"═══ DIAGNÓSTICO B095 — Token corto en ancla_catalogo ═══")
    print(f"Casos target: {len(target)}")
    print(f"CSV: {CSV_PATH}")
    print(f"Corpus: {CORPUS_DIR}")
    print()
    
    # Cache de archivos .md leídos
    md_cache = {}
    
    # Contadores de señales
    signal_counts = Counter()
    # Para cada caso: qué señal es la mejor candidata
    best_signal = []
    
    errors = []
    
    for idx, (r, tok) in enumerate(target):
        caso_id = r["caso_id_canonico"]
        source = r["source_file"]
        li = int(r["linea_inicio"])
        name_idx = r["case_name_indice"]
        name_cuerpo = r["case_name_cuerpo"]
        
        # Leer .md
        md_path = CORPUS_DIR / source
        if not md_path.exists():
            errors.append(f"{caso_id}: {md_path} no existe")
            continue
        
        if source not in md_cache:
            md_cache[source] = md_path.read_text(encoding="utf-8").splitlines()
        lines = md_cache[source]
        
        # Extraer bloque: linea_inicio..linea_inicio+WINDOW
        bloque = lines[li:li + WINDOW]
        if not bloque:
            errors.append(f"{caso_id}: bloque vacío en {source}:{li}")
            continue
        
        # ── Buscar señales ────────────────────────────────────────────────
        signals = {}  # señal → (linea_relativa, texto)
        
        for k, ln in enumerate(bloque):
            s = ln.strip()
            if not s:
                continue
            
            if RE_APERTURA.match(s) and "apertura" not in signals:
                signals["apertura"] = (k, s)
            
            if RE_FECHA.match(s) and "fecha_ba" not in signals:
                signals["fecha_ba"] = (k, s[:60])
            
            if RE_VISTOS_STRICT.match(ln) and "vistos_strict" not in signals:
                signals["vistos_strict"] = (k, s[:60])
            
            if RE_VISTOS_BROAD.match(ln) and "vistos_broad" not in signals:
                signals["vistos_broad"] = (k, s[:60])
            
            if RE_CONSIDERANDO.match(ln) and "considerando" not in signals:
                signals["considerando"] = (k, s[:60])
            
            if RE_PAGE_HEADER.match(s) and "page_hdr" not in signals:
                signals["page_hdr"] = (k, s[:40])
            
            if RE_FIRMA.search(s) and "firma" not in signals:
                signals["firma"] = (k, s[:60])
            
            if RE_DICTAMEN_HEADER.match(s) and "dictamen_hdr" not in signals:
                signals["dictamen_hdr"] = (k, s[:60])
        
        # Nombre completo del catálogo
        fn_label, fn_re = build_fullname_pattern(name_idx)
        if fn_re:
            for k, ln in enumerate(bloque):
                if fn_re.search(_strip_accents(ln)):
                    signals["fullname_idx"] = (k, ln.strip()[:60])
                    break
        
        # Tokens largos del cuerpo
        cuerpo_tokens = build_cuerpo_tokens(name_cuerpo)
        if cuerpo_tokens:
            for ct in cuerpo_tokens[:3]:  # primeros 3 tokens largos
                ct_norm = _strip_accents(ct)
                pat = re.compile(r"\b" + re.escape(ct_norm) + r"\b", re.I)
                for k, ln in enumerate(bloque):
                    if pat.search(_strip_accents(ln)):
                        signals.setdefault("cuerpo_token", (k, f"{ct} → {ln.strip()[:50]}"))
                        break
                if "cuerpo_token" in signals:
                    break
        
        # ── Clasificar residuo ────────────────────────────────────────────
        # Primera línea no-vacía, no-page-header
        first_content = ""
        first_content_k = 0
        for k, ln in enumerate(bloque):
            s = ln.strip()
            if s and not RE_PAGE_HEADER.match(s):
                first_content = s
                first_content_k = k
                break
        
        if RE_FIRMA.search(first_content):
            residue_type = "FIRMA_ANTERIOR"
        elif first_content.startswith("JURISDICCION") or first_content.startswith("CONSTITUCION"):
            residue_type = "SUMARIO_EDITORIAL"
        elif RE_APERTURA.match(first_content):
            residue_type = "LIMPIO_APERTURA"
        elif RE_VISTOS_BROAD.match(first_content):
            residue_type = "LIMPIO_VISTOS"
        elif RE_CONSIDERANDO.match(first_content):
            residue_type = "LIMPIO_CONSIDERANDO"
        elif first_content.startswith("Por ello") or first_content.startswith("por ello"):
            residue_type = "DISPOSITIVO_ANTERIOR"
        elif first_content.startswith("Recurso de hecho"):
            residue_type = "LIMPIO_RECURSO"
        else:
            residue_type = "OTRO"
        
        # ── Determinar mejor señal candidata ──────────────────────────────
        # Prioridad: fullname_idx > cuerpo_token > apertura > vistos > considerando
        if "fullname_idx" in signals:
            best = ("fullname_idx", signals["fullname_idx"][0])
        elif "cuerpo_token" in signals:
            best = ("cuerpo_token", signals["cuerpo_token"][0])
        elif "apertura" in signals:
            best = ("apertura", signals["apertura"][0])
        elif "vistos_broad" in signals:
            best = ("vistos_broad", signals["vistos_broad"][0])
        elif "considerando" in signals:
            best = ("considerando", signals["considerando"][0])
        else:
            best = ("NINGUNA", -1)
        
        for s_name in signals:
            signal_counts[s_name] += 1
        
        best_signal.append((caso_id, tok, residue_type, best, signals, name_idx))
        
        # ── Imprimir detalle ──────────────────────────────────────────────
        print(f"─── [{idx+1:02d}/51] {caso_id} ───")
        print(f"  Token: {tok!r}  |  Índice: {name_idx[:60]}")
        print(f"  Cuerpo: {name_cuerpo[:60] if name_cuerpo else '(vacío)'}")
        print(f"  Residuo: {residue_type}  |  Mejor señal: {best[0]} (línea +{best[1]})")
        print(f"  Señales encontradas:")
        for s_name, (s_k, s_text) in sorted(signals.items(), key=lambda x: x[1][0]):
            marker = " ◄◄" if s_name == best[0] else ""
            print(f"    +{s_k:02d}  {s_name:18s}  {s_text[:55]}{marker}")
        if not signals:
            print(f"    (ninguna señal estructural en las primeras {WINDOW} líneas)")
        print()
    
    # ── Resumen ───────────────────────────────────────────────────────────
    print("═══ RESUMEN ═══")
    print()
    
    # Cobertura de señales
    print("Frecuencia de señales (sobre 51 casos):")
    for s_name, cnt in signal_counts.most_common():
        print(f"  {s_name:18s}  {cnt:3d}  ({cnt*100/len(target):.0f}%)")
    print()
    
    # Distribución de mejor señal
    best_dist = Counter(b[0] for _, _, _, b, _, _ in best_signal)
    print("Mejor señal candidata:")
    for s_name, cnt in best_dist.most_common():
        print(f"  {s_name:18s}  {cnt:3d}  ({cnt*100/len(target):.0f}%)")
    print()
    
    # Distribución de residuo
    res_dist = Counter(rt for _, _, rt, _, _, _ in best_signal)
    print("Tipo de residuo:")
    for rt, cnt in res_dist.most_common():
        print(f"  {rt:22s}  {cnt:3d}  ({cnt*100/len(target):.0f}%)")
    print()
    
    # Casos sin señal
    sin_senal = [(cid, tok, ni) for cid, tok, _, b, _, ni in best_signal if b[0] == "NINGUNA"]
    if sin_senal:
        print(f"Casos SIN ninguna señal ({len(sin_senal)}):")
        for cid, tok, ni in sin_senal:
            print(f"  {cid:15s}  tok={tok!r:6s}  {ni[:50]}")
    else:
        print("✓ Todos los casos tienen al menos una señal candidata.")
    print()
    
    # Resumen de viabilidad
    atacable = sum(1 for _, _, _, b, _, _ in best_signal if b[0] != "NINGUNA")
    con_residuo = sum(1 for _, _, rt, _, _, _ in best_signal
                      if rt not in ("LIMPIO_APERTURA", "LIMPIO_VISTOS",
                                    "LIMPIO_CONSIDERANDO", "LIMPIO_RECURSO"))
    print(f"Atacables (tienen señal):   {atacable}/51")
    print(f"Con residuo real:           {con_residuo}/51")
    print(f"Atacables CON residuo real: ", end="")
    atacable_con_res = sum(1 for _, _, rt, b, _, _ in best_signal
                          if b[0] != "NINGUNA"
                          and rt not in ("LIMPIO_APERTURA", "LIMPIO_VISTOS",
                                         "LIMPIO_CONSIDERANDO", "LIMPIO_RECURSO"))
    print(f"{atacable_con_res}/51 ← estos son el target real del fix")
    print()
    
    if errors:
        print(f"ERRORES ({len(errors)}):")
        for e in errors:
            print(f"  {e}")


if __name__ == "__main__":
    main()
