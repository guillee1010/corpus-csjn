#!/usr/bin/env python3
"""Tests de normalizar_bloque (M21 / H124). Sin deps externas: `python test_normalizar_bloque.py`."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizar_bloque import (
    es_running_head, normalizar_bloque, _unhyphenate, RE_RUNNING_HEAD,
)

ok = fail = 0
def check(cond, msg):
    global ok, fail
    if cond: ok += 1
    else:
        fail += 1
        print(f"  ✗ {msg}")

# ── 1. POSITIVOS: running-heads reales (de los por_ello del gold) ────────────
banners = [
    "147 DE JUSTICIA DE LA NACION 329",
    "80 FALLOS DE LA CORTE SUPREMA 329",
    "1968 FALLOS DE LA CORTE SUPREMA",        # frase + num izq, sin num der
    "437 DE JUSTICIA DE LA NACION",           # num izq + frase
    "DE JUSTICIA DE LA NACIÓN",               # frase sola, con tilde
    "  329 FALLOS DE LA CORTE SUPREMA 329  ", # con whitespace de borde
    "1628 FALLOS DE LA CORTE SUPREMA 329",
    "2115 DE JUSTICIA DE LA NACION 329",
]
for b in banners:
    check(es_running_head(b), f"deberia enmascarar: {b!r}")

# ── 2. NEGATIVOS: frase legítima embebida / dispositivo / editorial / num solo ─
negativos = [
    "competencia originaria de la Corte Suprema de Justicia de la Nación.",
    "Declarar que la presente causa no corresponde a la competencia originaria de la Corte Suprema de Justicia de la Nación. Notifíquese.",
    "Por ello, se resuelve: Hacer lugar a la queja",
    "I. Declarar la competencia originaria de la Corte para entender",
    "329",                                    # número solo → fuera de alcance (NO matchea)
    "ACORDADAS Y RESOLUCIONES",               # editorial → preservar
    "INDICE POR LOS NOMBRES DE LAS PARTES",   # editorial → preservar
    "Vuelvan los autos al tribunal de origen para que",
    "DE JUSTICIA Y DERECHOS HUMANOS",         # 'DE JUSTICIA ...' pero NO la frase banner
]
for n in negativos:
    check(not es_running_head(n), f"NO deberia enmascarar: {n!r}")

# ── 3. INVARIANTES de normalizar_bloque ──────────────────────────────────────
bloque = [
    "Por ello, se hace lugar a la queja y al recurso extraordinario dedu-",
    "cido, y se deja sin efecto el pronunciamiento en cuanto fue motivo de",
    "147 DE JUSTICIA DE LA NACION 329",
    "agravios. Notifíquese y devuélvase.",
    "ENRIQUE S. PETRACCHI - ELENA I. HIGHTON DE NOLASCO",
]
entrada_original = list(bloque)

# longitud preservada en las 4 configs
for cfg, kw in [("base", dict(headers=False, guion=False)),
                ("+h",  dict(headers=True,  guion=False)),
                ("+g",  dict(headers=False, guion=True)),
                ("+ab", dict(headers=True,  guion=True))]:
    out = normalizar_bloque(bloque, **kw)
    check(len(out) == len(bloque), f"[{cfg}] longitud preservada ({len(out)} vs {len(bloque)})")

# no muta la entrada
_ = normalizar_bloque(bloque, headers=True, guion=True)
check(bloque == entrada_original, "no muta el bloque de entrada")

# headers=True enmascara SOLO la línea del banner, a ""
out_h = normalizar_bloque(bloque, headers=True, guion=False)
check(out_h[2] == "", f"banner enmascarado a '' (got {out_h[2]!r})")
check(out_h[0] == bloque[0], "headers=True, guion=False: NO toca el guión de fin de línea")
check(out_h[4] == bloque[4], "firma intacta tras enmascarar banner (ventana k+1..k+41)")

# baseline = copia idéntica
check(normalizar_bloque(bloque, headers=False, guion=False) == bloque, "baseline idéntico al crudo")

# guion per-línea: agarra corte INTRA-línea, NO el de fin de línea
check(_unhyphenate("señor Procura- dor Fiscal") == "señor Procurador Fiscal",
      "guión intra-línea unido")
check(_unhyphenate("recurso extraordinario dedu-") == "recurso extraordinario dedu-",
      "guión de fin de línea NO se toca per-línea (lo hace classify_outcome post-join)")

# editorial preservado aún con headers=True
out_ed = normalizar_bloque(["ACORDADAS Y RESOLUCIONES", "147 DE JUSTICIA DE LA NACION 329"],
                           headers=True, guion=False)
check(out_ed[0] == "ACORDADAS Y RESOLUCIONES", "editorial NUNCA enmascarado")
check(out_ed[1] == "", "banner sí enmascarado en el mismo bloque")

print(f"\n{ok} OK · {fail} FAIL")
sys.exit(1 if fail else 0)
