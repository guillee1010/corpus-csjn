"""
poc_b095_tier4.py — PoC para Tier 4 de refinar_inicio_por_titulo

Mejoras sobre la versión actual:
  - Tier 4 con ventana ampliada (100 líneas) como fallback de Tiers 1-3
  - Guarda _es_texto_corriente (portada de Pista 1 de detectar_fin_real)
  - Stoplist de tokens genéricos + segundo token confirmatorio
  - Fullname+inverted para TODOS los tokens (no solo token<4)
  - Guarda trim ≤50% del bloque
  - Retry loop (descarta matches en texto corrido y sigue buscando)

Corre sobre los 75 ancla_catalogo y reporta mejoras.
No modifica parser.py — es diagnóstico puro.

Correr desde raíz del repo:
    python scripts/auditoria/H076/poc_b095_tier4.py
"""

import csv
import re
import unicodedata
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers copiados del parser (para no importar y evitar side-effects)
# ═══════════════════════════════════════════════════════════════════════════════

def _strip_accents(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

RE_PAGE_HEADER = re.compile(
    r"^-{2,}\s*Página\s+\d+\s*-{2,}$|"
    r"^\d{1,4}\s*$|"
    r"^FALLOS DE LA CORTE SUPREMA$|"
    r"^DE JUSTICIA DE LA NACION$|"
    r"^DE JUSTICIA DE LA NACIÓN$",
    re.I,
)

_SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
         "empresa", "compania", "compañia", "compañía"}
_GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
              "afip", "buenos", "nacional", "administracion",
              "federal", "direccion", "instituto"}

_STOPLIST = {"provincia", "anses", "nacion", "estado",
             "afip", "buenos", "nacional", "administracion",
             "federal", "direccion", "instituto"}


def primer_token_de_caratula(nombres_indice):
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


def segundo_token_de_caratula(nombres_indice):
    """Extrae el segundo token significativo (para confirmar genéricos)."""
    if not nombres_indice:
        return None
    first = nombres_indice.split("|")[0].strip()
    first = re.sub(r"^\(\d+\)\s*", "", first)
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", first)
    found_first = False
    for t in tokens:
        if len(t) < 3:
            continue
        if not found_first:
            found_first = True
            continue
        # Devolver el segundo token que no sea genérico ni skip
        if t.lower() not in _SKIP and t.lower() not in _GENERICOS:
            return t
    return None


def _build_fullname_variants(nombres_indice):
    if not nombres_indice:
        return []
    first = nombres_indice.split("|")[0].strip()
    first = re.sub(r"^\(\d+\)\s*", "", first)
    if len(first) < 2:
        return []
    variants = [first]
    if " c/ " in first:
        parties = first.split(" c/ ", 1)
        inv_parts = []
        for p in parties:
            p = p.strip()
            cp = p.split(",", 1)
            if len(cp) == 2 and cp[1].strip():
                inv_parts.append(cp[1].strip() + " " + cp[0].strip())
            else:
                inv_parts.append(p)
        inverted = " c/ ".join(inv_parts)
        if inverted != first:
            variants.append(inverted)
    elif "," in first:
        cp = first.split(",", 1)
        if cp[1].strip():
            inverted = cp[1].strip() + " " + cp[0].strip()
            if inverted != first:
                variants.append(inverted)
    return variants


def _build_flexible_pattern(text):
    norm = _strip_accents(text)
    if len(norm) < 2:
        return None
    parts = []
    for c in norm:
        if c == '.':
            parts.append(r'\.\s*')
        elif c == ',':
            parts.append(r',\s*')
        elif c == ' ':
            parts.append(r'\s+')
        elif c.isalnum():
            parts.append(re.escape(c))
        else:
            parts.append(re.escape(c))
    try:
        return re.compile(''.join(parts), re.I)
    except re.error:
        return None


def _es_texto_corriente(lines, k):
    """True si lines[k] parece continuación de texto corriente."""
    s = lines[k].strip()
    if not s:
        return False
    first_alpha = None
    for c in s:
        if c.isalpha():
            first_alpha = c
            break
    if first_alpha and first_alpha.islower():
        s_stripped = s.lstrip()
        if not (s_stripped.startswith("c/") or s_stripped.startswith("s/")):
            return True
    # Buscar línea anterior significativa
    prev_line = None
    for j in range(k - 1, max(k - 5, -1), -1):
        if j < 0:
            break
        ps = lines[j].strip()
        if not ps:
            continue
        if RE_PAGE_HEADER.match(ps):
            continue
        if re.match(r'^\d{1,4}$', ps):
            continue
        prev_line = ps
        break
    if prev_line is None:
        return False
    if prev_line.endswith('-') and len(prev_line) >= 2:
        char_antes = prev_line[-2]
        if char_antes.isalpha():
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# Función mejorada
# ═══════════════════════════════════════════════════════════════════════════════

MAX_VENTANA_BASE = 50
MAX_VENTANA_AMPLIADA = 100
MAX_TRIM_PCT = 50  # no recortar más del 50% del bloque


def _buscar_con_patron(bloque, pat, ventana, con_guardas=False):
    """Busca pat en bloque[0:ventana]. Con guardas: skip texto corriente + retry.
    
    Returns (linea_idx, match_found) o (None, False).
    """
    limite = min(ventana, len(bloque))
    desde = 0
    while desde < limite:
        found_k = None
        for k in range(desde, limite):
            if pat.search(_strip_accents(bloque[k])):
                found_k = k
                break
        if found_k is None:
            return (None, False)
        # Guarda: últimas 5 líneas del bloque = carátula del caso siguiente
        if found_k >= len(bloque) - 5:
            desde = found_k + 1
            continue
        # Guarda: texto corriente (solo en modo con_guardas)
        if con_guardas and _es_texto_corriente(bloque, found_k):
            desde = found_k + 1
            continue
        return (found_k, True)
    return (None, False)


def refinar_inicio_mejorado(bloque, nombres_indice):
    """
    Versión mejorada de refinar_inicio_por_titulo con Tier 4.
    
    Returns (offset, ancla, tier_usado).
    """
    token = primer_token_de_caratula(nombres_indice)
    token_norm = _strip_accents(token) if token else ""
    es_generico = token_norm.lower() in _STOPLIST if token_norm else False

    # ── Tier 1: exact word boundary, ventana base ─────────────────────────
    if token and len(token) >= 4:
        pat = re.compile(r'\b' + re.escape(token_norm) + r'\b', re.I)
        k, found = _buscar_con_patron(bloque, pat, MAX_VENTANA_BASE)
        if found:
            return (k, 'titulo', 'T1_exact')

    # ── Tier 2: prefix match, ventana base ────────────────────────────────
    if token and len(token) >= 4:
        pat_prefix = re.compile(r'\b' + re.escape(token_norm), re.I)
        k, found = _buscar_con_patron(bloque, pat_prefix, MAX_VENTANA_BASE)
        if found:
            return (k, 'titulo', 'T2_prefix')

    # ── Tier 3: fullname+inverted, ventana base (token<4) ─────────────────
    if not token or len(token) < 4:
        for variant in _build_fullname_variants(nombres_indice):
            pat = _build_flexible_pattern(variant)
            if pat is None:
                continue
            k, found = _buscar_con_patron(bloque, pat, MAX_VENTANA_BASE)
            if found:
                return (k, 'titulo', 'T3_fullname')

    # ── Tier 4: ventana ampliada con guardas ──────────────────────────────
    # Solo corre si Tiers 1-3 fallaron. Incluye:
    #   - Guardas: _es_texto_corriente, trim ≤50%, retry loop
    #   - Stoplist: tokens genéricos requieren segundo token confirmatorio
    #   - Fullname+inverted para TODOS los tokens (no solo <4)

    len_bloque = len(bloque)

    # 4a: exact con guardas, ventana ampliada
    if token and len(token) >= 4:
        pat = re.compile(r'\b' + re.escape(token_norm) + r'\b', re.I)
        k, found = _buscar_con_patron(bloque, pat, MAX_VENTANA_AMPLIADA,
                                       con_guardas=True)
        if found:
            pct = 100 * k / len_bloque if len_bloque > 0 else 100
            if pct <= MAX_TRIM_PCT:
                # Si token es genérico, verificar segundo token cerca
                if es_generico:
                    tok2 = segundo_token_de_caratula(nombres_indice)
                    if tok2 and len(tok2) >= 3:
                        tok2_norm = _strip_accents(tok2)
                        pat2 = re.compile(r'\b' + re.escape(tok2_norm) + r'\b', re.I)
                        # Buscar segundo token en las 5 líneas alrededor del match
                        ventana_conf = bloque[max(0, k-2):k+5]
                        if any(pat2.search(_strip_accents(ln)) for ln in ventana_conf):
                            return (k, 'titulo', 'T4a_exact_guardado')
                    # Genérico sin segundo token → no confiar
                else:
                    return (k, 'titulo', 'T4a_exact_guardado')

    # 4b: prefix con guardas, ventana ampliada
    if token and len(token) >= 4:
        pat_prefix = re.compile(r'\b' + re.escape(token_norm), re.I)
        k, found = _buscar_con_patron(bloque, pat_prefix, MAX_VENTANA_AMPLIADA,
                                       con_guardas=True)
        if found:
            pct = 100 * k / len_bloque if len_bloque > 0 else 100
            if pct <= MAX_TRIM_PCT:
                if es_generico:
                    tok2 = segundo_token_de_caratula(nombres_indice)
                    if tok2 and len(tok2) >= 3:
                        tok2_norm = _strip_accents(tok2)
                        pat2 = re.compile(r'\b' + re.escape(tok2_norm) + r'\b', re.I)
                        ventana_conf = bloque[max(0, k-2):k+5]
                        if any(pat2.search(_strip_accents(ln)) for ln in ventana_conf):
                            return (k, 'titulo', 'T4b_prefix_guardado')
                else:
                    return (k, 'titulo', 'T4b_prefix_guardado')

    # 4c: fullname+inverted para TODOS los tokens, ventana ampliada
    for variant in _build_fullname_variants(nombres_indice):
        pat = _build_flexible_pattern(variant)
        if pat is None:
            continue
        k, found = _buscar_con_patron(bloque, pat, MAX_VENTANA_AMPLIADA,
                                       con_guardas=True)
        if found:
            pct = 100 * k / len_bloque if len_bloque > 0 else 100
            if pct <= MAX_TRIM_PCT:
                return (k, 'titulo', 'T4c_fullname_ampliado')

    # ── Señal secundaria: "Vistos los autos" ──────────────────────────────
    RE_VISTOS = re.compile(r"^Vistos?\s+los\s+autos", re.I)
    for k, ln in enumerate(bloque[:MAX_VENTANA_AMPLIADA]):
        if RE_VISTOS.match(ln):
            return (k, 'vistos', 'vistos')

    # ── Fallback ──────────────────────────────────────────────────────────
    return (0, 'catalogo', 'fallback')


# ═══════════════════════════════════════════════════════════════════════════════
# Main: diagnóstico sobre ancla_catalogo
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    casos_path = Path("output/parser/csjn_casos.csv")
    corpus_dir = Path("corpus")

    with casos_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_casos = list(reader)

    ancla = [c for c in all_casos if "ancla_catalogo" in c.get("status_localizacion", "")]
    print(f"Total casos: {len(all_casos)}")
    print(f"ancla_catalogo: {len(ancla)}\n")

    # Cache de archivos .md
    md_cache = {}

    mejoras = []
    sin_cambio = []
    errores = []

    for caso in ancla:
        caso_id = caso["caso_id_canonico"]
        nombres = caso.get("case_name_indice", "")
        li = int(caso.get("linea_inicio", 0))
        lf = int(caso.get("linea_fin", 0))
        sf = caso.get("source_file", "")

        # Cargar .md
        md_path = corpus_dir / sf
        if sf not in md_cache:
            try:
                md_cache[sf] = md_path.read_text(encoding="utf-8").splitlines()
            except Exception as e:
                errores.append((caso_id, str(e)))
                continue
        lines = md_cache[sf]
        bloque = lines[li:lf + 1]

        if len(bloque) < 3:
            sin_cambio.append((caso_id, "bloque_corto", 0, "", ""))
            continue

        offset, ancla_usada, tier = refinar_inicio_mejorado(bloque, nombres)

        if ancla_usada == 'titulo':
            pct = round(100 * offset / len(bloque), 1) if len(bloque) > 0 else 0
            token = primer_token_de_caratula(nombres)
            # Mostrar la línea donde matcheó para auditoría
            linea_match = bloque[offset].strip()[:80] if offset < len(bloque) else ""
            mejoras.append((caso_id, tier, offset, len(bloque), pct, token, nombres, linea_match))
        elif ancla_usada == 'vistos':
            mejoras.append((caso_id, tier, offset, len(bloque),
                           round(100 * offset / len(bloque), 1) if len(bloque) > 0 else 0,
                           "(vistos)", nombres, bloque[offset].strip()[:80]))
        else:
            token = primer_token_de_caratula(nombres)
            sin_cambio.append((caso_id, "sin_match", 0, token, nombres))

    # ── Reporte ───────────────────────────────────────────────────────────

    print(f"{'='*95}")
    print(f"  MEJORAS: {len(mejoras)} casos rescatados de ancla_catalogo")
    print(f"{'='*95}")
    print(f"{'caso_id':<18} {'tier':<22} {'offset':>6} {'bloq':>5} {'trim%':>6}  {'token':<16} línea_match")
    print(f"{'-'*18} {'-'*22} {'-'*6} {'-'*5} {'-'*6}  {'-'*16} {'-'*30}")
    for caso_id, tier, offset, len_b, pct, token, nombres, linea in mejoras:
        print(f"{caso_id:<18} {tier:<22} {offset:>6} {len_b:>5} {pct:>5.1f}%  {token:<16} {linea[:50]}")

    print(f"\n{'='*95}")
    print(f"  SIN CAMBIO: {len(sin_cambio)} casos siguen como ancla_catalogo")
    print(f"{'='*95}")
    for caso_id, motivo, _, token, nombres in sin_cambio:
        print(f"  {caso_id:<18} {motivo:<14} token={token:<16} {nombres[:50]}")

    if errores:
        print(f"\n  ERRORES: {len(errores)}")
        for caso_id, err in errores:
            print(f"  {caso_id}: {err}")

    # ── Resumen ───────────────────────────────────────────────────────────
    print(f"\n{'='*95}")
    print(f"  RESUMEN")
    print(f"{'='*95}")
    print(f"  ancla_catalogo actual:  {len(ancla)}")
    print(f"  rescatados (mejoras):   {len(mejoras)}")
    print(f"  residual:               {len(sin_cambio)}")
    print(f"  ancla_catalogo nuevo:   {len(sin_cambio)}")
    if mejoras:
        from collections import Counter
        tier_counts = Counter(t for _, t, *_ in mejoras)
        print(f"\n  Por tier:")
        for t, c in tier_counts.most_common():
            print(f"    {t:<25} {c:>3}")


if __name__ == "__main__":
    main()
