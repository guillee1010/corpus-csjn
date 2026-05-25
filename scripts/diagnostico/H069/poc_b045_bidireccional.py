"""
POC B045 — Bidireccional closest-to-lfc en fallback firma_actual.

Simula qué pasaría si detectar_fin_real buscara firma en ambas
direcciones y eligiera la más cercana a lfc, en lugar de backward-first.

Uso:
    python poc_b045_bidireccional.py

Requiere:
    - output/parser/csjn_casos.csv (CSV productivo)
    - corpus/*.md (archivos fuente)
    - output/mapa/mapa_paginas.csv (para proximo_header_pagina)

Output:
    Tabla de comparación: qué elige backward-only vs bidireccional.
    Flags: MEJORA / REGRESION / SIN_CAMBIO por caso.
"""

import csv
import re
from pathlib import Path
from collections import Counter

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT         = Path(".")
CSV_CASOS    = ROOT / "output" / "parser" / "csjn_casos.csv"
CSV_MAPA     = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS_DIR   = ROOT / "corpus"

# ── Dependencias mínimas de parser.py ────────────────────────────────────────

JUECES_CONOCIDOS = [
    (re.compile(r"horacio\s+(daniel\s+)?rosatti", re.I),                     "Rosatti"),
    (re.compile(r"carlos\s+fernando\s+rosenkrantz", re.I),                   "Rosenkrantz"),
    (re.compile(r"ricardo\s+(luis\s+)?lorenzetti", re.I),                    "Lorenzetti"),
    (re.compile(r"juan\s+carlos\s+maqueda", re.I),                           "Maqueda"),
    (re.compile(r"elena\s+(i\.|inés)\s*(highton)?(?:\s+de\s+nolasco)?", re.I),"Highton de Nolasco"),
    (re.compile(r"manuel\s+jos[eé]?\s+garc[íi]a[\-\s]+mansilla", re.I),       "García Mansilla"),
    (re.compile(r"e\.?\s*ra[úu]l\s+zaffaroni|eugenio\s+ra[úu]l\s+zaffaroni", re.I), "Zaffaroni"),
    (re.compile(r"enrique\s+santiago\s+petracchi|enrique\s+s\.?\s+petracchi", re.I), "Petracchi"),
    (re.compile(r"carmen\s+m\.?\s*argibay|carmen\s+mar[íi]a\s+argibay", re.I),"Argibay"),
    (re.compile(r"carlos\s+s\.?\s*fayt|carlos\s+santiago\s+fayt", re.I),      "Fayt"),
    (re.compile(r"antonio\s+boggiano|^boggiano\b|—\s*boggiano\s*—", re.I),    "Boggiano"),
    (re.compile(r"augusto\s+c[ée]sar\s+belluscio", re.I),                     "Belluscio"),
    (re.compile(r"guillermo\s+a\.?\s*f\.?\s*l[óo]pez", re.I),                 "López"),
    (re.compile(r"adolfo\s+roberto\s+v[áa]zquez", re.I),                      "Vázquez"),
    (re.compile(r"juli[oa]\s+s\.?\s*nazareno", re.I),                         "Nazareno"),
    (re.compile(r"juan\s+carlos\s+rodr[íi]guez\s+basavilbaso", re.I),         "Rodríguez Basavilbaso"),
    (re.compile(r"luis\s+c[ée]sar\s+otero", re.I),                            "Otero"),
    (re.compile(r"gabriel\s+(rub[ée]n|r\.?)\s+cavallo", re.I),                "Cavallo"),
    (re.compile(r"mariano\s+borinsky", re.I),                                "Borinsky"),
    (re.compile(r"alejandro\s+s\.?\s*catania", re.I),                        "Catania"),
    (re.compile(r"juan\s+carlos\s+gemignani", re.I),                         "Gemignani"),
    (re.compile(r"daniel\s+a\.?\s*petrone", re.I),                           "Petrone"),
    (re.compile(r"angela\s+e\.?\s*ledesma", re.I),                           "Ledesma"),
    (re.compile(r"diego\s+g\.?\s*barroetave[ñn]a", re.I),                    "Barroetaveña"),
    (re.compile(r"gustavo\s+m\.?\s*hornos", re.I),                           "Hornos"),
    (re.compile(r"javier\s+leal\s+de\s+ibarra", re.I),                       "Leal de Ibarra"),
    (re.compile(r"liliana\s+(catucci|cattucci)", re.I),                      "Catucci"),
    (re.compile(r"eduardo\s+r\.?\s*riggi", re.I),                            "Riggi"),
    (re.compile(r"guillermo\s+yacobucci", re.I),                             "Yacobucci"),
    (re.compile(r"ana\s+mar[íi]a\s+figueroa", re.I),                         "Figueroa"),
    (re.compile(r"carlos\s+a\.?\s*mahiques", re.I),                          "Mahiques"),
    (re.compile(r"mar[íi]a\s+susana\s+najurieta", re.I),                    "Najurieta"),
    (re.compile(r"roc[íi]o\s+alcal[áa]", re.I),                            "Alcalá"),
    (re.compile(r"jorge\s+eduardo\s+mor[áa]n\.?", re.I),                   "Morán"),
    (re.compile(r"mirta\s+(d\.?|delia)\s+tyden(?:\s+de\s+skanata)?", re.I), "Tyden de Skanata"),
    (re.compile(r"juan\s+carlos\s+poclava\s+lafuente", re.I),              "Poclava Lafuente"),
    (re.compile(r"carlos\s+(m\.?|mart[íi]n)\s+pereyra\s+gonz[áa]lez", re.I), "Pereyra González"),
    (re.compile(r"jorge\s+ferro", re.I),                                    "Ferro"),
    (re.compile(r"antonio\s+pacilio", re.I),                                "Pacilio"),
    (re.compile(r"[áa]ngel\s+a\.?\s*arga[ñn]araz", re.I),                  "Argañaraz"),
    (re.compile(r"rita\s+(mill|m\.?)\s+de\s+pereyra", re.I),               "Mill de Pereyra"),
    (re.compile(r"alberto\s+manuel\s+garc[íi]a\s+lema", re.I),            "García Lema"),
    (re.compile(r"luis\s+renato\s+rabbi[\s—-]+baldi\s+cabanillas", re.I),  "Rabbi-Baldi Cabanillas"),
    (re.compile(r"h[ée]ctor\s+(oscar\s+)?m[ée]ndez", re.I),               "Méndez"),
    (re.compile(r"graciela\s+susana\s+montesi", re.I),                     "Montesi"),
    (re.compile(r"marina\s+(josefa\s+)?cossio|cossio\s+marina", re.I),     "Cossio"),
    (re.compile(r"arturo\s+p[ée]rez\s+petit", re.I),                       "Pérez Petit"),
    (re.compile(r"otilio\s+roque\s+romano", re.I),                         "Romano"),
    (re.compile(r"julio\s+demetrio\s+petra\s+fern[áa]ndez", re.I),         "Petra Fernández"),
    (re.compile(r"gabriel\s+b\.?\s*chausovsky", re.I),                     "Chausovsky"),
    (re.compile(r"leopoldo\s+h\.?\s*schiffrin", re.I),                     "Schiffrin"),
    (re.compile(r"horacio\s+jos[ée]\s+aguilar", re.I),                     "Aguilar"),
    (re.compile(r"victoria\s+patricia\s+p[ée]rez\s+tognola", re.I),        "Pérez Tognola"),
    (re.compile(r"santiago\s+hern[áa]n\s+corcuera", re.I),                 "Corcuera"),
    (re.compile(r"silvina\s+mar[íi]a\s+andalaf(?:\s+casiello)?", re.I),    "Andalaf Casiello"),
    (re.compile(r"cintia\s+fern[áa]ndez\s+g[óo]mez", re.I),               "Fernández Gómez"),
]

RE_HEADER_VOTO_DISIDENCIA = re.compile(
    r"^\s*(disidencia|voto)\b|"
    r"^\s*(don|do[ñn]a|del\s+(se[ñn]or|se[ñn]ora))\b|"
    r"^\s*(se[ñn]or(es)?|se[ñn]ora(s)?)\s+(ministr|president|vicepresidente|juez|jueza)|"
    r"^\s*la\s+se[ñn]ora\s+|"
    r"^\s*el\s+se[ñn]or\s+",
    re.I
)


def linea_es_firma_de_juez(linea):
    """Copia literal de parser.py."""
    s = linea.strip()
    if not s or len(s) > 200:
        return False
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False
    primera_palabra = s.split()[0].lower() if s.split() else ""
    palabras_cuerpo = {
        "siguiendo", "como", "según", "segun", "que", "el", "la", "los", "las",
        "ya", "esta", "este", "ese", "esa", "ello", "por", "pero", "para",
        "tal", "incluso", "asimismo", "tambien", "también", "no", "si",
        "cuando", "mientras", "aunque", "luego", "después", "despues",
        "afirma", "sostiene", "entiende", "considera", "indicó", "indico",
        "destacó", "destaco", "señaló", "señalo", "concluyó", "concluyo",
    }
    if primera_palabra.rstrip(",;:") in palabras_cuerpo:
        return False
    encontrado = False
    for pat, _nombre in JUECES_CONOCIDOS:
        if pat.search(s):
            encontrado = True
            break
    if not encontrado:
        return False
    tiene_raya = "—" in s or " - " in s or "–" in s
    es_corta = len(s) <= 80
    termina_con_punto = s.rstrip().endswith(".")
    if tiene_raya or es_corta or (termina_con_punto and len(s) <= 120):
        return True
    return False


def buscar_atras(lines, check, desde, hasta):
    """Busca desde 'desde' hacia atrás hasta 'hasta' (inclusive)."""
    for k in range(desde, hasta - 1, -1):
        if 0 <= k < len(lines) and check(lines[k]):
            return k
    return None


def buscar_adelante(lines, check, desde, hasta):
    """Busca desde 'desde' hacia adelante hasta 'hasta' (inclusive)."""
    for k in range(desde, hasta + 1):
        if 0 <= k < len(lines) and check(lines[k]):
            return k
    return None


# ── Cargar mapa de páginas ───────────────────────────────────────────────────

def cargar_mapa(ruta):
    """Devuelve dict {(tomo, archivo): [(linea_header, pagina), ...]} ordenado."""
    por_archivo = {}
    with open(ruta, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (int(row["tomo"]), row["archivo"])
            por_archivo.setdefault(key, []).append(
                (int(row["linea_header"]), int(row["pagina"]))
            )
    for k in por_archivo:
        por_archivo[k].sort()
    return por_archivo


def proximo_header_despues_de(headers_archivo, linea):
    """Devuelve la próxima línea-header > linea, o None."""
    for ln, _pg in headers_archivo:
        if ln > linea:
            return ln
    return None


# ── Lógica principal ─────────────────────────────────────────────────────────

def main():
    # 1. Cargar CSV
    with open(CSV_CASOS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # 2. Cargar mapa
    mapa = cargar_mapa(CSV_MAPA)

    # 3. Filtrar firma_actual
    firma_actual = [r for r in rows if r["pista_fin"] == "firma_actual"]
    print(f"firma_actual: {len(firma_actual)} casos")

    # 4. Build next-case map
    by_file = {}
    for r in rows:
        if r["source_file"] and r["linea_inicio"]:
            by_file.setdefault(r["source_file"], []).append(r)
    for k in by_file:
        by_file[k].sort(key=lambda x: int(x["linea_inicio"]))

    # 5. Cache de archivos .md
    cache_lines = {}
    def get_lines(source_file):
        if source_file not in cache_lines:
            path = CORPUS_DIR / source_file
            if not path.exists():
                print(f"  WARN: {path} no existe, skip")
                cache_lines[source_file] = None
                return None
            cache_lines[source_file] = path.read_text(encoding="utf-8").split("\n")
        return cache_lines[source_file]

    # 6. Simular bidireccional
    resultados = []
    for r in firma_actual:
        caso_id = r["caso_id_canonico"]
        sf = r["source_file"]
        li = int(r["linea_inicio"])
        lf = int(r["linea_fin"])        # = lfc en detectar_fin_real
        lfr = int(r["linea_fin_real"])   # resultado actual (backward-only)
        vp = r["voting_pattern"]
        tomo = int(r["tomo"])

        lines = get_lines(sf)
        if lines is None:
            continue
        n = len(lines)

        # Calcular proximo_header_pagina (igual que parser.py)
        key_mapa = (tomo, sf)
        headers = mapa.get(key_mapa, [])
        prox_header = proximo_header_despues_de(headers, lf)

        # Calcular limite_adelante (igual que detectar_fin_real)
        if prox_header is not None and prox_header > lf:
            limite_adelante = min(prox_header + 50, n - 1)
        else:
            limite_adelante = min(lf + 200, n - 1)

        # Buscar next case linea_inicio (para diagnosticar si fwd es del caso siguiente)
        cases_in_file = by_file.get(sf, [])
        next_li = None
        for c in cases_in_file:
            if int(c["linea_inicio"]) > li:
                next_li = int(c["linea_inicio"])
                break

        # ── Simulación ──────────────────────────────────────────────────
        # Backward: igual que producción
        k_back = buscar_atras(lines, linea_es_firma_de_juez, lf, li)
        # Forward: lo que hoy NUNCA corre si backward encuentra algo
        k_fwd = buscar_adelante(lines, linea_es_firma_de_juez, lf + 1, limite_adelante)

        # Bidireccional closest-to-lfc
        if k_back is not None and k_fwd is not None:
            dist_back = lf - k_back
            dist_fwd = k_fwd - lf
            if dist_fwd <= dist_back:
                bidi_pick = "forward"
                bidi_lfr = k_fwd
            else:
                bidi_pick = "backward"
                bidi_lfr = k_back
        elif k_back is not None:
            bidi_pick = "backward_only"
            bidi_lfr = k_back
        elif k_fwd is not None:
            bidi_pick = "forward_only"
            bidi_lfr = k_fwd
        else:
            bidi_pick = "none"
            bidi_lfr = lf  # fallback_catalogo

        # ── Clasificar ──────────────────────────────────────────────────
        cambio = bidi_lfr != lfr

        # ¿El forward es del caso siguiente?
        fwd_en_next = (k_fwd is not None and next_li is not None
                       and k_fwd >= next_li)
        # ¿El forward es antes de proximo_header_pagina? (zona legítima del caso actual)
        fwd_pre_header = (k_fwd is not None and prox_header is not None
                          and k_fwd < prox_header)

        # Diagnóstico
        if not cambio:
            tag = "SIN_CAMBIO"
        elif vp == "unanime" and bidi_pick == "forward" and not fwd_en_next:
            tag = "MEJORA_SEGURA"
        elif vp == "unanime" and bidi_pick == "forward" and fwd_en_next:
            tag = "MEJORA_DUDOSA"
        elif vp != "unanime" and cambio and fwd_en_next:
            tag = "REGRESION"
        elif vp != "unanime" and cambio and not fwd_en_next:
            tag = "CAMBIO_REVISAR"
        else:
            tag = "OTRO"

        res = {
            "caso_id": caso_id,
            "vp": vp,
            "li": li,
            "lf": lf,
            "lfr_actual": lfr,
            "k_back": k_back,
            "k_fwd": k_fwd,
            "k_fwd_linea": lines[k_fwd].strip()[:70] if k_fwd is not None and k_fwd < n else "",
            "bidi_pick": bidi_pick,
            "bidi_lfr": bidi_lfr,
            "prox_header": prox_header,
            "next_li": next_li,
            "fwd_en_next": fwd_en_next,
            "fwd_pre_header": fwd_pre_header,
            "cambio": cambio,
            "tag": tag,
        }
        resultados.append(res)

    # ── Reporte ─────────────────────────────────────────────────────────────
    print()
    print("=" * 120)
    print("RESUMEN")
    print("=" * 120)
    tags = Counter(r["tag"] for r in resultados)
    for t, n in tags.most_common():
        print(f"  {t}: {n}")

    # Detalle por categoría
    for tag_filter in ["MEJORA_SEGURA", "MEJORA_DUDOSA", "REGRESION", "CAMBIO_REVISAR"]:
        subset = [r for r in resultados if r["tag"] == tag_filter]
        if not subset:
            continue
        print()
        print(f"{'─'*120}")
        print(f"  {tag_filter} ({len(subset)} casos)")
        print(f"{'─'*120}")
        print(f"  {'caso_id':>15s}  {'vp':>15s}  {'lfr_act':>7s}  {'k_back':>7s}  "
              f"{'k_fwd':>7s}  {'bidi':>10s}  {'bidi_lfr':>8s}  {'fwd_next':>8s}  "
              f"{'fwd_pre_h':>9s}  fwd_linea")
        for r in sorted(subset, key=lambda x: (x["vp"], x["caso_id"])):
            print(f"  {r['caso_id']:>15s}  {r['vp']:>15s}  {r['lfr_actual']:>7d}  "
                  f"{str(r['k_back']):>7s}  {str(r['k_fwd']):>7s}  "
                  f"{r['bidi_pick']:>10s}  {r['bidi_lfr']:>8d}  "
                  f"{str(r['fwd_en_next']):>8s}  {str(r['fwd_pre_header']):>9s}  "
                  f"{r['k_fwd_linea'][:60]}")

    # SIN_CAMBIO resumen por voting_pattern
    sin_cambio = [r for r in resultados if r["tag"] == "SIN_CAMBIO"]
    if sin_cambio:
        print()
        print(f"{'─'*120}")
        print(f"  SIN_CAMBIO ({len(sin_cambio)} casos) — desglose por voting_pattern:")
        vp_counts = Counter(r["vp"] for r in sin_cambio)
        for vp, n in vp_counts.most_common():
            print(f"    {vp}: {n}")
        # Motivo: k_fwd None o backward más cercano
        fwd_none = sum(1 for r in sin_cambio if r["k_fwd"] is None)
        back_closer = sum(1 for r in sin_cambio if r["k_fwd"] is not None and not r["cambio"])
        print(f"    (k_fwd=None: {fwd_none}, backward más cercano: {back_closer})")

    print()
    print("=" * 120)
    print(f"Total procesados: {len(resultados)} / {len(firma_actual)}")
    print()

    # ── Guarda propuesta: rechazar fwd si >= prox_header ──────────────
    print("SIMULACIÓN CON GUARDA (rechazar fwd si >= prox_header):")
    for r in resultados:
        if r["tag"] in ("REGRESION", "CAMBIO_REVISAR", "MEJORA_DUDOSA"):
            if r["k_fwd"] is not None and r["prox_header"] is not None:
                if r["k_fwd"] >= r["prox_header"]:
                    r["tag_guardado"] = "BLOQUEADO_POR_GUARDA"
                else:
                    r["tag_guardado"] = r["tag"]  # guarda no aplica
            else:
                r["tag_guardado"] = r["tag"]
        else:
            r["tag_guardado"] = r["tag"]

    tags_g = Counter(r["tag_guardado"] for r in resultados)
    for t, n in tags_g.most_common():
        print(f"  {t}: {n}")

    bloqueados = [r for r in resultados if r.get("tag_guardado") == "BLOQUEADO_POR_GUARDA"]
    if bloqueados:
        print(f"\n  Detalle BLOQUEADOS ({len(bloqueados)}):")
        for r in bloqueados:
            print(f"    {r['caso_id']:>15s} vp={r['vp']:>15s}  k_fwd={r['k_fwd']}  "
                  f"prox_header={r['prox_header']}  fwd_linea={r['k_fwd_linea'][:50]}")

    # Residuales post-guarda
    residuales = [r for r in resultados
                  if r.get("tag_guardado") in ("REGRESION", "CAMBIO_REVISAR", "MEJORA_DUDOSA")]
    if residuales:
        print(f"\n  Residuales post-guarda ({len(residuales)}):")
        for r in residuales:
            print(f"    {r['caso_id']:>15s} vp={r['vp']:>15s}  tag={r['tag_guardado']}")


if __name__ == "__main__":
    main()
