#!/usr/bin/env python3
"""
validar_b127_v103.py — gate de cierre en disco para clasificador_disposicion v1.03 (B127).
============================================================================================
Corre el clasificador v1.03 sobre el por_ello ACTUAL del sidecar y confirma que el unico
efecto sobre el corpus es EXACTAMENTE el set esperado de flips, 0 regresiones. Sale != 0 si
aparece cualquier flip no esperado (gate duro).

Uso:
  python scripts/auditoria/validar_b127_v103.py \
      --clasificador scripts/pipeline/clasificador_disposicion.py \
      --recursos     output/parser/csjn_casos_recursos.csv \
      --textos       output/parser/csjn_casos_textos.csv

Defaults apuntan a esas rutas. La columna `disposicion` de --recursos es el ESTADO PRE-FIX
(salida de v1.02); el script la usa como baseline para el diff. Tras pasar el gate: re-correr
derivar_recursos.py para regenerar csjn_casos_recursos.csv con el clasificador v1.03.
"""
import csv, sys, argparse, importlib.util
csv.field_size_limit(sys.maxsize)

FLIPS_ESPERADOS = {
    "332_p2769": ("no_fondo", "deja_sin_efecto"),
    "333_p1613": ("no_fondo", "deja_sin_efecto"),
    "334_p1272": ("no_fondo", "revoca"),            # OJO: conflicto con parser (es_revision_fondo=no) -> ver B-number
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
    if cd.__version__ != "1.03":
        print("  AVISO: se esperaba 1.03"); 

    rec = load_csv(a.recursos)
    txt = load_csv(a.textos)
    ids = [c for c in rec if c in txt]
    print(f"casos cruzados recursos x textos = {len(ids)}")

    flips, parte_delta = {}, {"gana": 0, "pierde": 0}
    for c in ids:
        old = rec[c]["disposicion"].strip()
        new = cd.disposicion(txt[c]["por_ello_text"])[0]
        if old != new:
            flips[c] = (old, new)
            po, pn = cd.parte_ganadora_regla(old), cd.parte_ganadora_regla(new)
            if po != "recurrente_gana" and pn == "recurrente_gana": parte_delta["gana"] += 1
            if po == "recurrente_gana" and pn != "recurrente_gana": parte_delta["pierde"] += 1

    inesperados = {c: v for c, v in flips.items() if c not in FLIPS_ESPERADOS}
    faltantes   = {c: v for c, v in FLIPS_ESPERADOS.items() if c not in flips}
    distintos   = {c: (flips[c], FLIPS_ESPERADOS[c]) for c in flips if c in FLIPS_ESPERADOS and flips[c] != FLIPS_ESPERADOS[c]}

    print(f"\nFLIPS totales = {len(flips)} (esperados {len(FLIPS_ESPERADOS)})")
    for c, (o, n) in sorted(flips.items()):
        print(f"  {c}: {o} -> {n}")
    print(f"\nparte_ganadora: +{parte_delta['gana']} gana / -{parte_delta['pierde']} pierde")

    ok = not inesperados and not faltantes and not distintos
    if inesperados: print(f"\n[FALLA] flips INESPERADOS: {inesperados}")
    if faltantes:   print(f"\n[FALLA] flips esperados que FALTAN: {faltantes}")
    if distintos:   print(f"\n[FALLA] flips con destino distinto: {distintos}")
    print("\n[CLEAN] v1.03 hace exactamente lo esperado, 0 regresiones." if ok else "\n[SUCIO] revisar arriba.")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
