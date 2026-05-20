"""
Fase 2 H043 — Inventario de headers de voto/disidencia en el corpus.

Escanea todos los LibroVol*.md buscando líneas con "disidencia", "voto del",
"voto de la", "voto concurrente", etc. Para cada hit:
  - Testea si RE_VOTO_HDR o RE_DISID_HDR lo matchea.
  - Detecta headers multi-línea (B061).
  - Agrupa por patrón normalizado.

Uso (desde raíz del repo):
  python scripts/diagnostico/H043/inventario_headers_voto.py
"""

import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
CORPUS = ROOT / "corpus"

# ── Regex del parser (copiados tal cual) ─────────────────────────────────────
RE_VOTO_HDR = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)
RE_DISID_HDR = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)

# ── Keywords de búsqueda (case-insensitive) ──────────────────────────────────
KEYWORDS = [
    "disidencia",
    "voto del",
    "voto de la",
    "voto de el",
    "voto de los",
    "voto de las",
    "voto concurrente",
    "voto conjunto",
    "ampliación de fundamentos",
    "ampliacion de fundamentos",
]


def normalizar(s):
    """Normaliza un header para agrupar variantes."""
    s = s.strip()
    # Quitar nombre del juez (todo después de "doctor/doctora/ministro/señor + nombre")
    s = re.sub(r"(doctor|doctora|ministro|ministra|señor|señora|juez|jueza)\s+.*",
               r"\1 [NOMBRE]", s, flags=re.I)
    # Quitar "de la Corte Suprema" y similares
    s = re.sub(r"\s+de la Corte.*", "", s, flags=re.I)
    return s


def main():
    archivos = sorted(CORPUS.glob("LibroVol*.md"))
    if not archivos:
        print(f"ERROR: no hay archivos LibroVol*.md en {CORPUS}")
        return

    print(f"Archivos a escanear: {len(archivos)}")

    hits_voto = []      # (archivo, linea_num, texto, matchea_regex, es_multilinea)
    hits_disid = []
    hits_otro = []       # keywords que no son ni voto ni disidencia estándar

    patrones_voto = Counter()
    patrones_disid = Counter()
    patrones_otro = Counter()

    no_matchea_voto = []
    no_matchea_disid = []

    for filepath in archivos:
        lines = filepath.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            s = line.strip()
            s_lower = s.lower()

            # ¿Contiene algún keyword?
            found_kw = None
            for kw in KEYWORDS:
                if kw in s_lower:
                    found_kw = kw
                    break
            if not found_kw:
                continue

            # Ignorar líneas muy largas (probablemente texto corrido, no headers)
            if len(s) > 200:
                continue

            # Ignorar si es parte de un párrafo (no empieza con mayúscula o keyword)
            if not re.match(r"^(Voto|Disidencia|VOTO|DISIDENCIA|Ampliaci)", s, re.I):
                # Podría ser multi-línea: la línea anterior era el inicio
                # O es una mención dentro del texto
                # Solo nos interesan las que parecen headers
                continue

            # Clasificar
            m_voto = RE_VOTO_HDR.match(s)
            m_disid = RE_DISID_HDR.match(s)

            # Detectar multi-línea: header que empieza con keyword pero no matchea,
            # y la siguiente línea tiene "señor/ministr"
            es_multilinea = False
            texto_completo = s
            if not m_voto and not m_disid and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if re.match(r"(Se[nñ]or|Ministr|Vicepresidente|Presidente|Doctor)", next_line, re.I):
                    es_multilinea = True
                    texto_completo = s + " " + next_line
                    # Re-testear con texto unido
                    m_voto = RE_VOTO_HDR.match(texto_completo)
                    m_disid = RE_DISID_HDR.match(texto_completo)

            loc = f"{filepath.stem}:{i+1}"

            if "disidencia" in s_lower:
                matchea = bool(m_disid)
                hits_disid.append((loc, texto_completo, matchea, es_multilinea))
                norm = normalizar(texto_completo)
                patrones_disid[norm] += 1
                if not matchea:
                    no_matchea_disid.append((loc, texto_completo, es_multilinea))
            elif "voto" in s_lower:
                matchea = bool(m_voto)
                hits_voto.append((loc, texto_completo, matchea, es_multilinea))
                norm = normalizar(texto_completo)
                patrones_voto[norm] += 1
                if not matchea:
                    no_matchea_voto.append((loc, texto_completo, es_multilinea))
            else:
                hits_otro.append((loc, texto_completo, False, es_multilinea))
                norm = normalizar(texto_completo)
                patrones_otro[norm] += 1

    # ── Reporte ──────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"INVENTARIO DE HEADERS DE VOTO/DISIDENCIA")
    print(f"{'='*70}")

    print(f"\nHits totales:")
    print(f"  Voto:        {len(hits_voto)} ({sum(1 for h in hits_voto if h[2])} matchean regex)")
    print(f"  Disidencia:  {len(hits_disid)} ({sum(1 for h in hits_disid if h[2])} matchean regex)")
    print(f"  Otro:        {len(hits_otro)}")

    n_multi_v = sum(1 for h in hits_voto if h[3])
    n_multi_d = sum(1 for h in hits_disid if h[3])
    print(f"\n  Multi-línea (B061): {n_multi_v} voto + {n_multi_d} disidencia")

    # ── Patrones de VOTO ────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"PATRONES DE VOTO (agrupados, {len(patrones_voto)} variantes)")
    print(f"{'─'*70}")
    for pat, n in patrones_voto.most_common():
        # Testear si el patrón matchea
        m = RE_VOTO_HDR.match(pat)
        status = "✓" if m else "✗"
        print(f"  {status} {n:>3}x  {pat[:90]}")

    # ── Patrones de DISIDENCIA ──────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"PATRONES DE DISIDENCIA (agrupados, {len(patrones_disid)} variantes)")
    print(f"{'─'*70}")
    for pat, n in patrones_disid.most_common():
        m = RE_DISID_HDR.match(pat)
        status = "✓" if m else "✗"
        print(f"  {status} {n:>3}x  {pat[:90]}")

    # ── Otros ───────────────────────────────────────────────────────────
    if patrones_otro:
        print(f"\n{'─'*70}")
        print(f"OTROS PATRONES ({len(patrones_otro)} variantes)")
        print(f"{'─'*70}")
        for pat, n in patrones_otro.most_common():
            print(f"  ? {n:>3}x  {pat[:90]}")

    # ── Detalle: NO MATCHEAN ────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"VOTO: NO MATCHEAN RE_VOTO_HDR ({len(no_matchea_voto)} hits)")
    print(f"{'─'*70}")
    for loc, texto, multi in no_matchea_voto[:30]:
        tag = " [MULTI]" if multi else ""
        print(f"  {loc:30s} {texto[:80]}{tag}")

    print(f"\n{'─'*70}")
    print(f"DISIDENCIA: NO MATCHEAN RE_DISID_HDR ({len(no_matchea_disid)} hits)")
    print(f"{'─'*70}")
    for loc, texto, multi in no_matchea_disid[:30]:
        tag = " [MULTI]" if multi else ""
        print(f"  {loc:30s} {texto[:80]}{tag}")

    # ── Resumen ─────────────────────────────────────────────────────────
    total = len(hits_voto) + len(hits_disid)
    matchean = sum(1 for h in hits_voto if h[2]) + sum(1 for h in hits_disid if h[2])
    cobertura = 100 * matchean / total if total else 0
    print(f"\n{'='*70}")
    print(f"COBERTURA: {matchean}/{total} headers matchean ({cobertura:.1f}%)")
    print(f"No matchean: {len(no_matchea_voto)} voto + {len(no_matchea_disid)} disidencia")
    print(f"Multi-línea (B061): {n_multi_v + n_multi_d}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
