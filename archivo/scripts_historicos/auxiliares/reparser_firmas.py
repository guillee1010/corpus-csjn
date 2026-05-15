"""
CSJN — Re-parseo de firmas con padrón histórico extendido
==========================================================
Si el corpus fue generado con una versión del parser anterior que no incluía
a Petracchi/Zaffaroni/Argibay/Fayt/Boggiano en el padrón, este script
re-parsea las firmas (columna `firma_raw`) y regenera las columnas
`jueces`, `jueces_conocidos`, `posiciones`, `n_titulares`, `n_jueces`.

NOTA: este script es una alternativa a re-correr el parser desde los .md.
Es más rápido pero solo corrige las columnas relacionadas con la firma de
mayoría. NO regenera `texto_voto` por juez (eso requiere re-correr el parser).
Usar este script únicamente si:
  - El corpus en CSV ya está generado y completo
  - Solo te interesa que aparezcan los jueces históricos
  - No te importa regenerar la columna `texto_voto`

Uso:
  python reparser_firmas.py \
    --casos csjn_casos_v10.csv \
    --votos csjn_casos_v10_votos.csv \
    --output-casos csjn_casos_v10_corregido.csv \
    --output-votos csjn_casos_v10_votos_corregido.csv
"""

import argparse
import re
import json
from pathlib import Path
import pandas as pd

# ── Padrón completo (idéntico al v10 extendido) ───────────────────────────────

JUECES_CONOCIDOS = [
    # Banco actual / reciente
    (re.compile(r"horacio\s+(daniel\s+)?rosatti", re.I),                    "Rosatti"),
    (re.compile(r"carlos\s+fernando\s+rosenkrantz", re.I),                  "Rosenkrantz"),
    (re.compile(r"ricardo\s+(luis\s+)?lorenzetti", re.I),                   "Lorenzetti"),
    (re.compile(r"juan\s+carlos\s+maqueda", re.I),                          "Maqueda"),
    (re.compile(r"elena\s+(i\.|inés)\s*(highton)?(?:\s+de\s+nolasco)?", re.I),"Highton de Nolasco"),
    (re.compile(r"manuel\s+jos[eé]?\s+garc[íi]a[\-\s]+mansilla", re.I),     "García Mansilla"),
    # Banco de 7 (2006-2014/2015)
    (re.compile(r"e\.?\s*ra[úu]l\s+zaffaroni|eugenio\s+ra[úu]l\s+zaffaroni", re.I), "Zaffaroni"),
    (re.compile(r"enrique\s+santiago\s+petracchi|enrique\s+s\.?\s+petracchi", re.I), "Petracchi"),
    (re.compile(r"carmen\s+m\.?\s*argibay|carmen\s+mar[íi]a\s+argibay", re.I),"Argibay"),
    (re.compile(r"carlos\s+s\.?\s*fayt|carlos\s+santiago\s+fayt", re.I),     "Fayt"),
    # Pre-2006 (apariciones marginales)
    (re.compile(r"antonio\s+boggiano|^boggiano\b|—\s*boggiano\s*—", re.I),  "Boggiano"),
    (re.compile(r"augusto\s+c[ée]sar\s+belluscio", re.I),                   "Belluscio"),
    (re.compile(r"guillermo\s+a\.?\s*f\.?\s*l[óo]pez", re.I),               "López"),
    (re.compile(r"adolfo\s+roberto\s+v[áa]zquez", re.I),                    "Vázquez"),
    (re.compile(r"juli[oa]\s+s\.?\s*nazareno", re.I),                       "Nazareno"),
    # Conjueces históricos
    (re.compile(r"juan\s+carlos\s+rodr[íi]guez\s+basavilbaso", re.I),       "Rodríguez Basavilbaso (conjuez)"),
    (re.compile(r"luis\s+c[ée]sar\s+otero", re.I),                          "Otero (conjuez)"),
    (re.compile(r"gabriel\s+(rub[ée]n|r\.?)\s+cavallo", re.I),              "Cavallo (conjuez)"),
    # Conjueces frecuentes (heredados)
    (re.compile(r"mariano\s+borinsky", re.I),                               "Borinsky (conjuez)"),
    (re.compile(r"alejandro\s+s\.?\s*catania", re.I),                       "Catania (conjuez)"),
    (re.compile(r"juan\s+carlos\s+gemignani", re.I),                        "Gemignani (conjuez)"),
    (re.compile(r"daniel\s+a\.?\s*petrone", re.I),                          "Petrone (conjuez)"),
    (re.compile(r"angela\s+e\.?\s*ledesma", re.I),                          "Ledesma (conjuez)"),
    (re.compile(r"diego\s+g\.?\s*barroetave[ñn]a", re.I),                   "Barroetaveña (conjuez)"),
    (re.compile(r"gustavo\s+m\.?\s*hornos", re.I),                          "Hornos (conjuez)"),
    (re.compile(r"javier\s+leal\s+de\s+ibarra", re.I),                      "Leal de Ibarra (conjuez)"),
    (re.compile(r"liliana\s+(catucci|cattucci)", re.I),                     "Catucci (conjuez)"),
    (re.compile(r"eduardo\s+r\.?\s*riggi", re.I),                           "Riggi (conjuez)"),
    (re.compile(r"guillermo\s+yacobucci", re.I),                            "Yacobucci (conjuez)"),
    (re.compile(r"ana\s+mar[íi]a\s+figueroa", re.I),                        "Figueroa (conjuez)"),
    (re.compile(r"carlos\s+a\.?\s*mahiques", re.I),                         "Mahiques (conjuez)"),
]

RE_CALIFICADOR = re.compile(
    r"\(\s*(en\s+disidencia|seg[úu]n\s+su\s+voto|por\s+su\s+voto)"
    r"(\s+parcial)?\s*\)",
    re.I
)

# ── Función de parseo (idéntica a la de csjnv10.py extendido) ─────────────────

def parse_firma(firma_raw):
    """Parsea firma multi-línea: detecta jueces conocidos y calificadores."""
    if not isinstance(firma_raw, str) or not firma_raw.strip():
        return {"jueces": [], "voting_pattern": "sin_firma"}

    jueces_out = []
    has_voto    = False
    has_disid   = False

    matches = []
    for pat, nombre in JUECES_CONOCIDOS:
        for m in pat.finditer(firma_raw):
            matches.append((m.start(), m.end(), nombre))
    matches.sort()
    matches_dedup = []
    last_end = -1
    for ini, fin, nombre in matches:
        if ini < last_end:
            continue
        matches_dedup.append((ini, fin, nombre))
        last_end = fin

    for i, (ini, fin, nombre) in enumerate(matches_dedup):
        if i + 1 < len(matches_dedup):
            limite_busqueda = matches_dedup[i + 1][0]
        else:
            limite_busqueda = len(firma_raw)
        ventana = firma_raw[fin:limite_busqueda]
        cm = RE_CALIFICADOR.search(ventana)
        calificador = None
        if cm:
            cal_text = cm.group(1).lower()
            if "disidencia" in cal_text:
                calificador = "en disidencia"
                has_disid   = True
            elif "seg" in cal_text:
                calificador = "según su voto"
                has_voto    = True
            elif "por" in cal_text:
                calificador = "por su voto"
                has_voto    = True
        jueces_out.append({
            "nombre":      nombre,
            "calificador": calificador,
            "conocido":    True,
        })

    if has_voto and has_disid:
        voting_pattern = "mixed"
    elif has_voto:
        voting_pattern = "segun_su_voto"
    elif has_disid:
        voting_pattern = "disidencia"
    elif jueces_out:
        voting_pattern = "unanime"
    else:
        voting_pattern = "sin_firma"

    return {"jueces": jueces_out, "voting_pattern": voting_pattern}

# ── Procesamiento ─────────────────────────────────────────────────────────────

def reparsear_caso(row):
    """Reparsea un caso individual y devuelve dict con columnas actualizadas."""
    firma_raw = row.get("firma_raw", "")
    parsed = parse_firma(firma_raw)
    jueces_obj = parsed["jueces"]

    nombres        = [j["nombre"] for j in jueces_obj]
    nombres_titul  = [j["nombre"] for j in jueces_obj if "(conjuez)" not in j["nombre"]]
    posiciones     = {j["nombre"]: (j["calificador"] or "mayoria") for j in jueces_obj}

    return {
        "n_jueces":            len(jueces_obj),
        "n_titulares":         len(nombres_titul),
        "voting_pattern":      parsed["voting_pattern"],
        "jueces":              " | ".join(nombres),
        "jueces_conocidos":    " | ".join(nombres),  # todos están en padrón
        "posiciones":          json.dumps(posiciones, ensure_ascii=False),
    }

def regenerar_votos(casos_corregidos, votos_originales):
    """
    A partir de los casos corregidos, regenera la tabla de votos.
    Cada juez en `posiciones` se transforma en una fila.

    Mantiene los textos de votos del CSV original cuando coinciden caso_id+juez.
    """
    nuevos_votos = []
    # Index de votos originales para preservar texto_voto y wc_voto
    votos_idx = {}
    for _, v in votos_originales.iterrows():
        key = (v["caso_id"], v["juez"])
        votos_idx[key] = v

    for _, c in casos_corregidos.iterrows():
        try:
            posiciones = json.loads(c["posiciones"]) if isinstance(c["posiciones"], str) else {}
        except Exception:
            continue
        for juez, posicion in posiciones.items():
            es_conocido = 1
            # Recuperar texto_voto del CSV original si existe
            v_orig = votos_idx.get((c["caso_id"], juez))
            if v_orig is not None:
                texto_voto = v_orig.get("texto_voto", "")
                wc_voto    = v_orig.get("wc_voto", 0)
            else:
                texto_voto = ""
                wc_voto    = 0
            nuevos_votos.append({
                "caso_id":            c["caso_id"],
                "tomo":               c["tomo"],
                "date":               c["date"],
                "juez":               juez,
                "posicion":           posicion,
                "es_conocido":        es_conocido,
                "outcome":            c["outcome"],
                "voting_pattern":     c["voting_pattern"],
                "is_originaria":      c.get("is_originaria", 0),
                "is_full_bench":      c.get("is_full_bench", 0),
                "is_merit_decision":  c.get("is_merit_decision", 0),
                "wc_mayoria":         c.get("wc_mayoria", 0),
                "wc_votos":           c.get("wc_votos", 0),
                "dictamen_presente":  c.get("dictamen_presente", 0),
                "texto_voto":         texto_voto,
                "wc_voto":            wc_voto,
            })
    return pd.DataFrame(nuevos_votos)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Re-parseo de firmas con padrón completo")
    ap.add_argument("--casos",        required=True)
    ap.add_argument("--votos",        required=True)
    ap.add_argument("--output-casos", required=True)
    ap.add_argument("--output-votos", required=True)
    args = ap.parse_args()

    print(f"Cargando {args.casos}...")
    casos = pd.read_csv(args.casos, low_memory=False)
    votos = pd.read_csv(args.votos, low_memory=False)
    print(f"  {len(casos):,} casos, {len(votos):,} votos")

    # Re-parsear cada caso
    print("\nRe-parseando firmas...")
    cambios = casos.apply(reparsear_caso, axis=1, result_type="expand")

    # Métricas pre/post
    n_titulares_antes = casos["n_titulares"].sum()
    n_titulares_despues = cambios["n_titulares"].sum()
    print(f"  Total titulares (antes): {n_titulares_antes:,}")
    print(f"  Total titulares (después): {n_titulares_despues:,}")
    print(f"  Diferencia: +{n_titulares_despues - n_titulares_antes:,} jueces "
          f"identificados que antes estaban perdidos")

    # Comparar por tomo
    casos_pre = casos[["caso_id", "tomo", "n_titulares"]].copy()
    casos_pre.columns = ["caso_id", "tomo", "n_titulares_antes"]
    cambios_compare = cambios[["n_titulares"]].copy()
    cambios_compare.columns = ["n_titulares_despues"]
    comp_df = pd.concat([casos_pre.reset_index(drop=True),
                          cambios_compare.reset_index(drop=True)], axis=1)

    print("\nDetección por tomo (media de titulares):")
    by_tomo = comp_df.groupby("tomo").agg(
        n=("caso_id", "count"),
        antes=("n_titulares_antes", "mean"),
        despues=("n_titulares_despues", "mean"),
    ).round(2)
    print(by_tomo.to_string())

    # Aplicar las correcciones al DataFrame de casos
    for col in ["n_jueces", "n_titulares", "voting_pattern", "jueces",
                "jueces_conocidos", "posiciones"]:
        casos[col] = cambios[col]

    # Guardar
    casos.to_csv(args.output_casos, index=False, encoding="utf-8")
    print(f"\n[OK] {args.output_casos}: {len(casos):,} casos")

    # Regenerar tabla de votos
    print("\nRegenerando tabla de votos...")
    votos_nuevos = regenerar_votos(casos, votos)
    votos_nuevos.to_csv(args.output_votos, index=False, encoding="utf-8")
    print(f"[OK] {args.output_votos}: {len(votos_nuevos):,} votos")

    # Resumen de jueces detectados
    print("\nFrecuencia de jueces (top 20):")
    print(votos_nuevos["juez"].value_counts().head(20).to_string())


if __name__ == "__main__":
    main()
