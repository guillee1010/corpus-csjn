#!/usr/bin/env python3
"""
validar_m21_fase2.py — gate semántico de cierre para parser v21.0 (M21 Fase 2, banner).
=========================================================================================
Complementa a check_regresion (que es byte-vs-golden) con DOS gates que el harness
no mira:

  Gate A — DATO LIMPIO: 0 banners (terna running-head) deben quedar en el
           por_ello_text regenerado. Es el objetivo del fix; si quedan, no se logró.
  Gate B — DIRECCIÓN: las transiciones de `outcome` deben ser RECUPERACIONES
           (otro→real) y no REGRESIONES (real→otro). Cualquier X→otro con X!=otro
           es una pérdida y debe revisarse caso por caso → FALLA.

REE: el cierre lo da el dato en disco. Correr DESPUÉS de re-generar el parser v21.0.

Uso:
  python scripts/auditoria/validar_m21_fase2.py \
      --casos-old  backup/csjn_casos.csv \
      --casos-new  output/parser/csjn_casos.csv \
      --textos-new output/parser/csjn_casos_textos.csv

`--casos-old` = el csjn_casos.csv PRE-v21 (copialo a backup/ ANTES de re-correr, o
usá el del golden / git HEAD). El resto sale de output/parser/ regenerado.
"""
import csv, sys, re, argparse
from collections import Counter
csv.field_size_limit(sys.maxsize)

# Misma terna que RE_RUNNING_HEAD del parser (substring, ambas orientaciones).
RE_BANNER = re.compile(
    r"\d{1,6}\s+(?:FALLOS\s+DE\s+LA\s+CORTE\s+SUPREMA|DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N)\s+\d{1,6}"
    r"|\d{1,6}\s+(?:FALLOS\s+DE\s+LA\s+CORTE\s+SUPREMA|DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N)\b"
    r"|\b(?:FALLOS\s+DE\s+LA\s+CORTE\s+SUPREMA|DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N)\s+\d{1,6}", re.I)
REAL_OUTCOMES = {  # outcomes "resueltos" (un X→otro entre estos = pérdida)
    "hace_lugar","procedente","revoca","confirma","deja_sin_efecto","rechaza",
    "desestima","competencia","nulidad","abstracto","mal_concedido","improcedente",
    "inadmisible_280","inadmisible_acordada_4","caducidad","cautelar","nulidad_concesion",
    "desistimiento","desierto","inadmisible","originaria",
}

def load(path, keep=None):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["caso_id_canonico"]: (r if keep is None else {k: r[k] for k in keep})
                for r in csv.DictReader(f)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos-old",  required=True)
    ap.add_argument("--casos-new",  default="output/parser/csjn_casos.csv")
    ap.add_argument("--textos-new", default="output/parser/csjn_casos_textos.csv")
    a = ap.parse_args()

    old = load(a.casos_old, ["outcome"])
    new = load(a.casos_new, ["outcome"])
    txt = load(a.textos_new, ["por_ello_text"])
    ids = [c for c in new if c in old and c in txt]
    print(f"casos cruzados: {len(ids)}")

    # --- Gate A: dato limpio ---
    con_banner = [c for c in txt if RE_BANNER.search(txt[c]["por_ello_text"])]
    print(f"\n[Gate A] banners restantes en por_ello_text (nuevo): {len(con_banner)}")
    for c in con_banner[:10]:
        m = RE_BANNER.search(txt[c]["por_ello_text"])
        print(f"    {c}: ...{txt[c]['por_ello_text'][max(0,m.start()-20):m.end()+10]}...")

    # --- Gate B: dirección de transiciones de outcome ---
    flips = [(c, old[c]["outcome"], new[c]["outcome"]) for c in ids
             if old[c]["outcome"] != new[c]["outcome"]]
    recuperaciones = [(c,o,n) for c,o,n in flips if o == "otro" and n != "otro"]
    regresiones    = [(c,o,n) for c,o,n in flips if o in REAL_OUTCOMES and n == "otro"]
    otros          = [(c,o,n) for c,o,n in flips if (c,o,n) not in recuperaciones and (c,o,n) not in regresiones]
    print(f"\n[Gate B] flips de outcome: {len(flips)}")
    print(f"    recuperaciones (otro→real): {len(recuperaciones)}")
    print(f"    real→real (re-clasif):      {len(otros)}")
    print(f"    REGRESIONES (real→otro):    {len(regresiones)}")
    if flips:
        print("    transiciones top:", dict(Counter((o,n) for _,o,n in flips).most_common(8)))
    for c,o,n in regresiones[:15]:
        print(f"      REGRESIÓN {c}: {o} -> otro")

    ok = (len(con_banner) == 0) and (len(regresiones) == 0)
    print("\n[CLEAN] 0 banners restantes + 0 regresiones a otro." if ok
          else "\n[SUCIO] revisar: " + ("banners restantes; " if con_banner else "")
                 + ("regresiones a otro; " if regresiones else ""))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
