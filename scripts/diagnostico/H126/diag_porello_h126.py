#!/usr/bin/env python3
r"""
Spot-check H126 — ¿los cambios de por_ello_text SIN flip de outcome son
whitespace/extensión, o hay pérdida de contenido?
=======================================================================
El skip estructuralmente no puede perder palabras (saltea vacías, extiende
alcance). Esto lo DEMUESTRA sobre datos: toma N casos donde por_ello_text
cambió pero outcome NO, y para cada uno clasifica el cambio:

  WHITESPACE  : new == old salvo colapso de espacios   (idénticos tras normalizar)
  EXTENSION   : old (sin espacios) es prefijo de new    (new agrega texto al final)
  ⚠ OTRO      : ninguna de las dos → mirar a mano (posible pérdida)

Si todo cae en WHITESPACE/EXTENSION → 0 pérdida, cambio benigno.

Uso:
    python diag_porello_h126.py \
        --old-casos  output\parser\csjn_casos.csv  --new-casos  tmp_h126\csjn_casos.csv \
        --old-textos output\parser\csjn_casos_textos.csv --new-textos tmp_h126\csjn_casos_textos.csv \
        --n 8
"""
import argparse, csv, re, sys
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
KEY = "caso_id_canonico"
_ws = lambda s: re.sub(r"\s+", " ", s).strip()


def idx(path, col):
    with open(path, encoding="utf-8", newline="") as f:
        return {r[KEY]: r.get(col, "") for r in csv.DictReader(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-casos", required=True); ap.add_argument("--new-casos", required=True)
    ap.add_argument("--old-textos", required=True); ap.add_argument("--new-textos", required=True)
    ap.add_argument("--n", type=int, default=8)
    a = ap.parse_args()

    oc, nc = idx(a.old_casos, "outcome"), idx(a.new_casos, "outcome")
    ot, nt = idx(a.old_textos, "por_ello_text"), idx(a.new_textos, "por_ello_text")

    # casos: por_ello cambió Y outcome NO cambió
    cambia_pe_sin_flip = [k for k in ot
                          if k in nt and ot[k] != nt[k]
                          and oc.get(k) == nc.get(k)]
    total = len(cambia_pe_sin_flip)
    print(f"por_ello cambió SIN flip de outcome: {total} casos\n")

    cont = {"WHITESPACE": 0, "EXTENSION": 0, "OTRO": 0}
    otros = []
    for k in cambia_pe_sin_flip:
        o, n = ot[k], nt[k]
        if _ws(o) == _ws(n):
            cont["WHITESPACE"] += 1
        elif _ws(n).startswith(_ws(o)):
            cont["EXTENSION"] += 1
        else:
            cont["OTRO"] += 1; otros.append(k)

    print("Clasificación de los", total, "cambios:")
    for kind, c in cont.items():
        print(f"  {kind:11} {c}")
    print()

    # muestra N ejemplos (priorizando OTRO si hay)
    muestra = otros[:a.n] + [k for k in cambia_pe_sin_flip if k not in otros][:max(0, a.n - len(otros))]
    for k in muestra[:a.n]:
        o, n = ot[k], nt[k]
        kind = ("WHITESPACE" if _ws(o) == _ws(n)
                else "EXTENSION" if _ws(n).startswith(_ws(o)) else "⚠ OTRO")
        print("=" * 72)
        print(f"### {k}   [{kind}]   outcome={oc.get(k)!r} (sin cambio)")
        print(f"  OLD ({len(o)}): {o!r}")
        print(f"  NEW ({len(n)}): {n!r}")

    print("\n" + "=" * 72)
    if cont["OTRO"] == 0:
        print("✔ 0 casos OTRO → ningún cambio pierde contenido. Todo whitespace/extensión.")
        sys.exit(0)
    print(f"⚠ {cont['OTRO']} casos OTRO ({otros[:10]}) → revisar a mano antes de sellar.")
    sys.exit(1)


if __name__ == "__main__":
    main()
