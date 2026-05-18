"""
diag_h036_sin_firma.py — Diagnóstico de los 813 fallos sin firma
=================================================================
Sesión H036. Clasifica los 813 sin_firma en categorías y audita
muestras de cada una con auditar_fallo.py.

Ubicación: scripts/diagnostico/diag_h036_sin_firma.py

Uso:
  cd C:\\Users\\guill\\Proyectos\\corpus-csjn
  $env:PYTHONIOENCODING = "utf-8"
  python scripts/diagnostico/diag_h036_sin_firma.py

Output:
  output/diagnostico/H036/diag_h036_resumen.txt    — resumen cuantitativo
  output/diagnostico/H036/ids_<categoria>.txt       — IDs de cada categoría
  output/diagnostico/H036/auditoria_<cat>.md        — 10 casos auditados

Requiere: parser.py, auditar_fallo.py, CSVs productivos.
"""

import csv
import random
import re
import sys
from collections import Counter
from pathlib import Path

# ── Setup de paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from auditoria.auditar_fallo import (
    auditar_fallo,
    _render_doc_completo,
    cargar_localizados,
    cargar_proximos_headers,
)

CSV_CASOS = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
LOCALIZADOS = REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS = REPO_ROOT / "corpus"
OUTPUT_DIR = REPO_ROOT / "output" / "diagnostico" / "H036"

SEED = 42  # reproducibilidad

# ── Regex de clasificación ──────────────────────────────────────────────────

VERBOS_RESOLUTIVOS = re.compile(
    r"(se\s+(declara|resuelve|rechaza|hace\s+lugar|confirma|revoca|desestima|dispone|deja\s+sin\s+efecto))|"
    r"(decl[aá]ra(se|n)?|res[uo]elv[ea]|rech[aá]za(se)?|confir?m[aáó]|rev[oó]ca|desest[ií]m[aáó]|"
    r"dispon(e|er)|h[áa]gase|notif[ií]quese|arch[ií]vese|c[oó]rrase|rem[ií]tase|"
    r"devuélvase|vuelvan los autos)",
    re.I,
)

DISP_PHRASES = re.compile(
    r"(por ello|por los fundamentos|de conformidad con|por todo lo expuesto|"
    r"por estas razones|en consecuencia|en m[ée]rito|atento a|por lo expuesto|"
    r"se resuelve|se declara|notif[ií]quese|h[áa]gase saber)",
    re.I,
)


def clasificar_sin_firma(rows):
    """Clasifica los 813 sin_firma en categorías."""
    fallos = [r for r in rows if r["tipo_entrada"] == "fallo"]
    sin_firma = [r for r in fallos if r["voting_pattern"] == "sin_firma"]

    con_disp = [r for r in sin_firma if r["por_ello_text"].strip()]
    sin_disp = [r for r in sin_firma if not r["por_ello_text"].strip()]

    # A1: B059 falso positivo (argumental sin verbo, outcome=otro)
    a1 = [r for r in con_disp
          if not VERBOS_RESOLUTIVOS.search(r["por_ello_text"]) and r["outcome"] == "otro"]
    # A2: dispositivo real (outcome != otro)
    a2 = [r for r in con_disp if r["outcome"] != "otro"]
    # A3: outcome=otro pero con verbo resolutivo
    a3 = [r for r in con_disp if r not in a1 and r not in a2]

    # B1: con apertura + sin dispositivo
    b1_all = [r for r in sin_disp if r["apertura_tipo"].strip()]
    # B1a: dispositivo embebido en considerando
    b1_embebido = [r for r in b1_all if r["considerando_text"]
                   and DISP_PHRASES.search(r["considerando_text"][-500:])]
    # B1b: sin frase -> truncado o formato
    b1_truncado = [r for r in b1_all if r not in b1_embebido]

    # B2: sin apertura
    b2 = [r for r in sin_disp if not r["apertura_tipo"].strip()]

    return {
        "A1_b059": a1,
        "A2_disp_real": a2,
        "A3_otro_con_verbo": a3,
        "B1_embebido": b1_embebido,
        "B1_truncado": b1_truncado,
        "B2_sin_apertura": b2,
    }


def auditar_muestra(categoria, casos, n, cache, label):
    """Audita n casos al azar de una categoria."""
    rng = random.Random(SEED)
    muestra = rng.sample(casos, min(n, len(casos)))

    resultados = []
    for r in muestra:
        tomo = int(r["tomo"])
        pagina = int(r["caso_id_canonico"].split("_p")[1])
        res = auditar_fallo(
            tomo, pagina,
            corpus_dir=str(CORPUS),
            localizados_path=str(LOCALIZADOS),
            mapa_path=str(MAPA),
            _cache=cache,
        )
        resultados.append(res)

    cmd_str = f"diag_h036 --categoria {label} --n {n} --seed {SEED}"
    md = _render_doc_completo(resultados, cmd_str, seed=SEED)
    return md, muestra


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cargar CSV
    with open(CSV_CASOS, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cats = clasificar_sin_firma(rows)

    # ── Resumen cuantitativo ──
    resumen = []
    resumen.append("DIAGNOSTICO H036 — 813 fallos sin firma")
    resumen.append("=" * 55)
    resumen.append("")
    total = sum(len(v) for v in cats.values())
    resumen.append(f"Total sin_firma: {total}")
    resumen.append("")
    resumen.append("-- A. CON_DISP_SIN_FIRMA (363) --")
    resumen.append(f"  A1. B059 falso positivo post-apertura:     {len(cats['A1_b059']):>4}")
    resumen.append(f"  A2. Dispositivo real, firma falla:          {len(cats['A2_disp_real']):>4}")
    resumen.append(f"  A3. outcome=otro + verbo resolutivo:        {len(cats['A3_otro_con_verbo']):>4}")
    resumen.append("")
    resumen.append("-- B. SIN_DISPOSITIVO (450) --")
    resumen.append(f"  B1a. Dispositivo embebido en considerando:  {len(cats['B1_embebido']):>4}")
    resumen.append(f"  B1b. Sin frase (truncado/formato):          {len(cats['B1_truncado']):>4}")
    resumen.append(f"  B2.  Sin apertura:                          {len(cats['B2_sin_apertura']):>4}")
    resumen.append("")

    # Distribucion por tomo de cada categoria
    for label, casos in cats.items():
        tomos = Counter(r["tomo"] for r in casos)
        dist = ", ".join(f"{k}:{v}" for k, v in sorted(tomos.items(), key=lambda x: int(x[0])))
        resumen.append(f"  {label} por tomo: {dist}")

    resumen.append("")

    # A2: outcomes
    oc_a2 = Counter(r["outcome"] for r in cats["A2_disp_real"])
    resumen.append("-- A2 outcomes --")
    for k, v in oc_a2.most_common():
        resumen.append(f"  {k:<25} {v:>4}")

    # A2: por_ello wc stats
    wc_a2 = [len(r["por_ello_text"].split()) for r in cats["A2_disp_real"]]
    if wc_a2:
        resumen.append(f"  por_ello wc: min={min(wc_a2)}, max={max(wc_a2)}, median={sorted(wc_a2)[len(wc_a2)//2]}")

    resumen.append("")

    # B1b: wc distribution
    wc_b1b = [int(r["word_count"]) for r in cats["B1_truncado"]]
    if wc_b1b:
        resumen.append("-- B1b word_count --")
        resumen.append(f"  <200: {sum(1 for w in wc_b1b if w<200)}")
        resumen.append(f"  200-1000: {sum(1 for w in wc_b1b if 200<=w<1000)}")
        resumen.append(f"  >=1000: {sum(1 for w in wc_b1b if w>=1000)}")

    resumen_text = "\n".join(resumen)
    (OUTPUT_DIR / "diag_h036_resumen.txt").write_text(resumen_text, encoding="utf-8")
    print(resumen_text)
    print()

    # ── Auditorias ──
    cache = {}
    filas_loc, _ = cargar_localizados(str(LOCALIZADOS))
    cache["filas_loc"] = filas_loc
    cache["headers_por_archivo"] = cargar_proximos_headers(str(MAPA))

    auditorias = [
        ("A2_disp_real", 10),
        ("A3_otro_con_verbo", 10),
        ("B1_embebido", 10),
        ("B1_truncado", 10),
        ("B2_sin_apertura", 10),
    ]

    # Exportar caso_id de cada categoria
    for label, casos in cats.items():
        ids = [r["caso_id_canonico"] for r in casos]
        (OUTPUT_DIR / f"ids_{label}.txt").write_text("\n".join(ids), encoding="utf-8")

    for label, n in auditorias:
        casos = cats[label]
        if not casos:
            print(f"  {label}: 0 casos, salteando")
            continue
        print(f"  Auditando {label} ({n} de {len(casos)})...", end=" ", flush=True)
        md, muestra = auditar_muestra(label, casos, n, cache, label)
        out_path = OUTPUT_DIR / f"auditoria_{label}.md"
        out_path.write_text(md, encoding="utf-8")
        ids_muestra = [r["caso_id_canonico"] for r in muestra]
        print(f"OK -> {out_path.name}  [{', '.join(ids_muestra)}]")

    print(f"\n[OK] Output en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
