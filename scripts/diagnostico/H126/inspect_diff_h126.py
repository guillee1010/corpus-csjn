#!/usr/bin/env python3
"""
Inspector direccional H126 — diff column-aware old↔new del skip en `_barrer`.
=============================================================================
Complementa check_regresion.py: este NO falla por byte-diff (el skip ES un
cambio de comportamiento esperado), sino que CLASIFICA el diff y verifica que
caiga DENTRO del scope previsto. Cualquier columna cambiada fuera del scope es
un RED FLAG (acoplamiento no anticipado → investigar antes de sellar).

Scope verificado leyendo procesar_archivo (H126):
  - csjn_casos.csv      → pueden cambiar: outcome (primario) y los acoplados
        is_merit_decision, causa_inadmisibilidad, es_queja, queja_resultado,
        is_originaria, tribunal_origen_status (derivan de por_ello_text/outcome).
  - csjn_casos_textos.csv → puede cambiar: por_ello_text (superset de flips:
        + whitespace colapsado / texto extendido en casos con vacía en la ventana).
        considerando_text y firma_raw deben quedar INTACTOS (keyean por_ello_idx=k).
Todo lo demás (votos/zonas/editorial) está cubierto por check_regresion ([OK]).

Uso:
    python inspect_diff_h126.py \
        --old-casos  GOLDEN/csjn_casos.csv  --new-casos  NEW/csjn_casos.csv \
        --old-textos GOLDEN/csjn_casos_textos.csv --new-textos NEW/csjn_casos_textos.csv
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

KEY = "caso_id_canonico"

SCOPE_CASOS = {
    "outcome", "is_merit_decision", "causa_inadmisibilidad",
    "es_queja", "queja_resultado", "is_originaria", "tribunal_origen_status",
}
SCOPE_TEXTOS = {"por_ello_text"}
INTACTOS_TEXTOS = {"considerando_text", "firma_raw"}

# votos: el skip cambia SOLO columnas denormalizadas del caso padre. La identidad
# del voto (juez/posicion/texto_voto/wc_voto/voting_pattern/...) NO debe moverse.
SCOPE_VOTOS = {
    "outcome", "is_merit_decision", "is_originaria",
    "tipo_voto_sep", "fragmenta_ratio", "punto_divergencia",
}
IDENTIDAD_VOTOS = {"caso_id_canonico", "tomo", "date", "juez", "posicion",
                   "es_conocido", "voting_pattern", "is_full_bench",
                   "wc_mayoria", "wc_votos", "dictamen_presente",
                   "texto_voto", "wc_voto"}


def cargar(path):
    with open(path, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return {row[KEY]: row for row in r}, r.fieldnames


def comparar(old, new, fields, scope, etiqueta, intactos=()):
    """Devuelve (cambios_por_col Counter, transiciones por col, red_flags set,
    set de keys agregadas/quitadas)."""
    cambios = Counter()
    trans = defaultdict(Counter)            # col -> Counter((viejo,nuevo))
    red_flags = set()
    intactos_violados = Counter()
    ks_old, ks_new = set(old), set(new)
    solo_old, solo_new = ks_old - ks_new, ks_new - ks_old

    for k in ks_old & ks_new:
        ro, rn = old[k], new[k]
        for col in fields:
            if col == KEY:
                continue
            vo, vn = ro.get(col, ""), rn.get(col, "")
            if vo != vn:
                cambios[col] += 1
                if col in scope:
                    trans[col][(vo, vn)] += 1
                if col not in scope:
                    red_flags.add(col)
                if col in intactos:
                    intactos_violados[col] += 1

    print(f"\n{'='*70}\n{etiqueta}")
    print(f"  filas: old={len(ks_old)}  new={len(ks_new)}  "
          f"solo_old={len(solo_old)}  solo_new={len(solo_new)}")
    if solo_old or solo_new:
        print(f"  ⚠ keys asimétricas: solo_old={sorted(solo_old)[:8]} "
              f"solo_new={sorted(solo_new)[:8]}")
    if not cambios:
        print("  (sin cambios de celda)")
    for col in sorted(cambios, key=lambda c: -cambios[c]):
        marca = "  ❗RED FLAG (fuera de scope)" if col not in scope else ""
        if col in intactos:
            marca = "  ❗❗VIOLA INTACTO (esperado 0)"
        print(f"  · {col:24} {cambios[col]:5} celdas{marca}")
    # histograma de transiciones de las columnas en scope
    for col in sorted(trans):
        top = trans[col].most_common(12)
        print(f"\n  transiciones [{col}]:")
        for (vo, vn), n in top:
            vo_s = (vo[:30] + "…") if len(vo) > 31 else vo
            vn_s = (vn[:30] + "…") if len(vn) > 31 else vn
            print(f"      {n:4}  {vo_s!r:34} → {vn_s!r}")
    return cambios, trans, red_flags, intactos_violados, (solo_old | solo_new)


def comparar_votos(old_path, new_path):
    """Comparación POSICIONAL de csjn_casos_votos.csv (multi-fila por caso →
    no se puede keyear por caso_id). El parser es determinista (mismo orden),
    así que comparar por posición detecta cambios de celda y filas +/-.
    Cambios fuera de SCOPE_VOTOS, o en cualquier columna de IDENTIDAD_VOTOS,
    son RED FLAG."""
    with open(old_path, encoding="utf-8", newline="") as f:
        ro = list(csv.reader(f))
    with open(new_path, encoding="utf-8", newline="") as f:
        rn = list(csv.reader(f))
    print(f"\n{'='*70}\ncsjn_casos_votos.csv (posicional)")
    print(f"  filas: old={len(ro)-1}  new={len(rn)-1}")
    if ro[0] != rn[0]:
        print("  ❗ HEADER cambiado → no comparable por columna"); return {"header"}
    if len(ro) != len(rn):
        print(f"  ❗ N FILAS difiere (dif={len(rn)-len(ro)}) → el set de votos cambió "
              "(NO esperado por el skip)")
        return {"nfilas"}
    header = ro[0]
    cambios = Counter()
    trans = defaultdict(Counter)
    red = set()
    n = len(ro)
    for i in range(1, n):
        if ro[i] == rn[i]:
            continue
        for j in range(len(header)):
            vo = ro[i][j] if j < len(ro[i]) else ""
            vn = rn[i][j] if j < len(rn[i]) else ""
            if vo != vn:
                col = header[j]
                cambios[col] += 1
                if col in SCOPE_VOTOS:
                    trans[col][(vo, vn)] += 1
                else:
                    red.add(col)
    if not cambios:
        print("  (sin cambios de celda)")
    for col in sorted(cambios, key=lambda c: -cambios[c]):
        marca = ""
        if col in IDENTIDAD_VOTOS:
            marca = "  ❗❗IDENTIDAD DEL VOTO (esperado 0)"
        elif col not in SCOPE_VOTOS:
            marca = "  ❗RED FLAG (fuera de scope)"
        print(f"  · {col:24} {cambios[col]:5} celdas{marca}")
    for col in sorted(trans):
        print(f"\n  transiciones [{col}]:")
        for (vo, vn), c in trans[col].most_common(12):
            vo_s = (vo[:28] + "…") if len(vo) > 29 else vo
            vn_s = (vn[:28] + "…") if len(vn) > 29 else vn
            print(f"      {c:4}  {vo_s!r:32} → {vn_s!r}")
    return red


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-casos", required=True)
    ap.add_argument("--new-casos", required=True)
    ap.add_argument("--old-textos", required=True)
    ap.add_argument("--new-textos", required=True)
    ap.add_argument("--old-votos", default=None)
    ap.add_argument("--new-votos", default=None)
    a = ap.parse_args()

    oc, fc = cargar(a.old_casos)
    nc, _ = cargar(a.new_casos)
    ot, ft = cargar(a.old_textos)
    nt, _ = cargar(a.new_textos)

    _, _, rf_c, _, asim_c = comparar(oc, nc, fc, SCOPE_CASOS,
                                     "csjn_casos.csv", intactos=())
    _, _, rf_t, intv_t, asim_t = comparar(ot, nt, ft, SCOPE_TEXTOS,
                                          "csjn_casos_textos.csv",
                                          intactos=INTACTOS_TEXTOS)
    rf_v = set()
    if a.old_votos and a.new_votos:
        rf_v = comparar_votos(a.old_votos, a.new_votos)

    print(f"\n{'='*70}\nVEREDICTO")
    problemas = []
    if rf_c:
        problemas.append(f"casos: columnas fuera de scope cambiadas: {sorted(rf_c)}")
    if rf_t:
        problemas.append(f"textos: columnas fuera de scope cambiadas: {sorted(rf_t)}")
    if intv_t:
        problemas.append(f"textos: INTACTOS violados: {dict(intv_t)} "
                         "(considerando/firma NO deberían moverse)")
    if rf_v:
        problemas.append(f"votos: cambios fuera de scope / identidad: {sorted(rf_v)}")
    if asim_c or asim_t:
        problemas.append("hay filas agregadas/quitadas (el parser cambió el set "
                         "de casos: NO esperado por el skip)")
    if problemas:
        print("  ❗ REVISAR antes de sellar:")
        for p in problemas:
            print(f"     - {p}")
        sys.exit(1)
    print("  ✔ Todos los cambios caen DENTRO del scope previsto del skip.")
    print("    casos/textos en scope · considerando/firma intactos · set de casos")
    print("    idéntico · votos solo en columnas denormalizadas (identidad intacta).")
    print("    Ojear transiciones de outcome (otro→competencia, acceso→fondo; sin fondo→otro).")
    sys.exit(0)


if __name__ == "__main__":
    main()
