#!/usr/bin/env python3
"""
validar_b127_v104.py — gate de cierre en disco para clasificador_disposicion v1.04 (B127).
============================================================================================
Cubre v1.03 (OBJ plural -es en revoca/deja) + v1.04 (RE_HEADER variante SUPREMA, reordenado).
Gate ESTRUCTURAL (no lista de ids frágil): todo flip debe ser
  (a) uno de los 6 flips de fondo conocidos de v1.03, o
  (b) un no_fondo -> por_ello_cortado (relabel honesto del banner truncado),
y NINGÚN flip puede perder un 'recurrente_gana'. Sale != 0 si algo se sale de eso.

Sirve contra cualquier baseline:
  - vs recursos v1.02 -> 24 flips (6 fondo + 18 cortado)
  - vs recursos v1.03 -> 18 flips (solo cortado)

Uso:
  python scripts/auditoria/validar_b127_v104.py \
      --clasificador scripts/pipeline/clasificador_disposicion.py \
      --recursos     output/parser/csjn_casos_recursos.csv \
      --textos       output/parser/csjn_casos_textos.csv
"""
import csv, sys, argparse, importlib.util
csv.field_size_limit(sys.maxsize)

FONDO_V103 = {
    "332_p2769": ("no_fondo", "deja_sin_efecto"),
    "333_p1613": ("no_fondo", "deja_sin_efecto"),
    "334_p1272": ("no_fondo", "revoca"),            # conflicto con parser (es_revision_fondo=no) -> B-number
    "338_p1311": ("no_fondo", "revoca"),
    "341_p247":  ("grant_remand_implicito", "deja_sin_efecto"),  # parte_ganadora INVARIANTE
    "345_p220":  ("grant_remand_implicito", "deja_sin_efecto"),  # parte_ganadora INVARIANTE
}

def load_mod(path):
    spec = importlib.util.spec_from_file_location("clasificador_disposicion", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clasificador", default="scripts/pipeline/clasificador_disposicion.py")
    ap.add_argument("--recursos", default="output/parser/csjn_casos_recursos.csv")
    ap.add_argument("--textos",   default="output/parser/csjn_casos_textos.csv")
    a = ap.parse_args()

    cd = load_mod(a.clasificador)
    print(f"clasificador __version__ = {cd.__version__}")
    if cd.__version__ != "1.04":
        print("  AVISO: se esperaba 1.04")

    rec = load_csv(a.recursos); txt = load_csv(a.textos)
    ids = [c for c in rec if c in txt]
    print(f"casos cruzados recursos x textos = {len(ids)}")

    flips, n_fondo, n_cortado, perdidas = {}, 0, 0, []
    for c in ids:
        old = rec[c]["disposicion"].strip()
        new = cd.disposicion(txt[c]["por_ello_text"])[0]
        if old == new:
            continue
        flips[c] = (old, new)
        po, pn = cd.parte_ganadora_regla(old), cd.parte_ganadora_regla(new)
        if po == "recurrente_gana" and pn != "recurrente_gana":
            perdidas.append((c, old, new))
        if c in FONDO_V103: n_fondo += 1
        elif (old, new) == ("no_fondo", "por_ello_cortado"): n_cortado += 1

    no_permitidos = {c: v for c, v in flips.items()
                     if c not in FONDO_V103 and v != ("no_fondo", "por_ello_cortado")}

    print(f"\nFLIPS totales = {len(flips)}  (fondo conocidos={n_fondo}, cortado={n_cortado})")
    print(f"pérdidas de recurrente_gana: {len(perdidas)}")
    if no_permitidos:
        print(f"\n[FALLA] flips fuera del set permitido ({len(no_permitidos)}):")
        for c, (o, n) in list(no_permitidos.items())[:20]:
            print(f"  {c}: {o} -> {n}")
    if perdidas:
        print(f"\n[FALLA] se perdió recurrente_gana en: {perdidas}")
    ok = not no_permitidos and not perdidas
    print("\n[CLEAN] v1.04: solo flips permitidos (fondo conocido + banner->cortado), 0 pérdida de recurrente_gana."
          if ok else "\n[SUCIO] revisar arriba.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
