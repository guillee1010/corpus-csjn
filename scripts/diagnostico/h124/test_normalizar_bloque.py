#!/usr/bin/env python3
"""Tests de normalizar_bloque (M21 / H124). Sin deps externas: `python test_normalizar_bloque.py`.

Semántica (H124, tras verificar la forma real del banner sobre el corpus):
el running-head de Fallos son TRES líneas consecutivas (núm / FRASE / núm).
  - es_running_head() detecta SOLO la línea-FRASE (ancla inequívoco).
  - normalizar_bloque(headers=True) enmascara la TERNA: la frase + los números
    pelados que la flanquean. Un número pelado SUELTO (sin frase adyacente) se
    preserva (es inciso/monto/año/artículo del texto, no banner).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizar_bloque import (
    es_running_head, _es_num_pelado, normalizar_bloque, _unhyphenate, RE_RUNNING_HEAD,
)

ok = fail = 0
def check(cond, msg):
    global ok, fail
    if cond: ok += 1
    else:
        fail += 1
        print(f"  ✗ {msg}")

# ── 1. POSITIVOS: la línea-FRASE del banner (sola en su línea) ────────────────
frases = [
    "DE JUSTICIA DE LA NACION",                # forma real (sin tilde)
    "DE JUSTICIA DE LA NACIÓN",                # con tilde
    "FALLOS DE LA CORTE SUPREMA",              # pliego par
    "  DE JUSTICIA DE LA NACION  ",            # whitespace de borde
    "de justicia de la nacion",                # case-insensitive
]
for f in frases:
    check(es_running_head(f), f"deberia detectar frase-banner: {f!r}")

# ── 2. NEGATIVOS: frase legítima embebida / dispositivo / editorial / num ─────
negativos = [
    "competencia originaria de la Corte Suprema de Justicia de la Nación.",
    "Declarar que la presente causa no corresponde a la competencia originaria de la Corte Suprema de Justicia de la Nación. Notifíquese.",
    "Por ello, se resuelve: Hacer lugar a la queja",
    "I. Declarar la competencia originaria de la Corte para entender",
    "329",                                     # número solo NO es frase (lo resuelve el contexto)
    "147 DE JUSTICIA DE LA NACION 329",        # núm+frase+núm en un renglón: NO es la forma real
    "ACORDADAS Y RESOLUCIONES",                # editorial → preservar
    "INDICE POR LOS NOMBRES DE LAS PARTES",    # editorial → preservar
    "Vuelvan los autos al tribunal de origen para que",
    "DE JUSTICIA Y DERECHOS HUMANOS",          # 'DE JUSTICIA ...' pero NO la frase banner
]
for n in negativos:
    check(not es_running_head(n), f"NO deberia detectar frase-banner: {n!r}")

# _es_num_pelado
check(_es_num_pelado("329") and _es_num_pelado("  79  ") and _es_num_pelado("1968"),
      "num pelado reconocido")
check(not _es_num_pelado("2º)") and not _es_num_pelado("329 bis") and not _es_num_pelado("art. 14"),
      "num NO pelado (inciso/sufijo) rechazado")

# ── 3. TERNA real núm/frase/núm: las 3 líneas → "" ────────────────────────────
bloque = [
    "Por ello, se hace lugar a la queja y al recurso extraordinario dedu-",
    "cido, y se deja sin efecto el pronunciamiento en cuanto fue motivo de",
    "79",                                      # número de página
    "DE JUSTICIA DE LA NACION",                # frase
    "329",                                     # número de tomo
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

# headers=True enmascara la TERNA completa (índices 2,3,4) a ""
out_h = normalizar_bloque(bloque, headers=True, guion=False)
check(out_h[2] == "", f"num pagina (pre-frase) enmascarado (got {out_h[2]!r})")
check(out_h[3] == "", f"frase enmascarada (got {out_h[3]!r})")
check(out_h[4] == "", f"num tomo (post-frase) enmascarado (got {out_h[4]!r})")
check(out_h[0] == bloque[0], "texto previo intacto")
check(out_h[5] == bloque[5], "texto posterior intacto")
check(out_h[6] == bloque[6], "firma intacta (ventana k+1..k+41)")

# baseline = copia idéntica
check(normalizar_bloque(bloque, headers=False, guion=False) == bloque, "baseline idéntico al crudo")

# ── 4. Número pelado SUELTO (sin frase adyacente) se PRESERVA ──────────────────
bloque_inciso = [
    "I. Revocar la sentencia apelada. Con costas.",
    "2",                                       # inciso/numeral suelto, NO banner
    "Notifíquese y devuélvase.",
]
out_inc = normalizar_bloque(bloque_inciso, headers=True, guion=False)
check(out_inc[1] == "2", f"num suelto SIN frase adyacente NO se enmascara (got {out_inc[1]!r})")
check(out_inc == bloque_inciso, "bloque sin banner queda idéntico con headers=True")

# ── 5. Banner asimétrico: frase + número de un solo lado ──────────────────────
bloque_asim = [
    "texto previo del considerando",
    "DE JUSTICIA DE LA NACION",                # frase
    "329",                                     # solo número posterior
    "texto siguiente",
]
out_as = normalizar_bloque(bloque_asim, headers=True, guion=False)
check(out_as[1] == "" and out_as[2] == "", "asimétrico: frase + num posterior enmascarados")
check(out_as[0] == bloque_asim[0] and out_as[3] == bloque_asim[3], "asimétrico: texto intacto")

# ── 6. guion per-línea: corte INTRA-línea sí, fin de línea no ──────────────────
check(_unhyphenate("señor Procura- dor Fiscal") == "señor Procurador Fiscal",
      "guión intra-línea unido")
check(_unhyphenate("recurso extraordinario dedu-") == "recurso extraordinario dedu-",
      "guión de fin de línea NO se toca per-línea (lo hace classify_outcome post-join)")

# ── 7. editorial preservado aún con headers=True ──────────────────────────────
out_ed = normalizar_bloque(["ACORDADAS Y RESOLUCIONES", "79", "DE JUSTICIA DE LA NACION", "329"],
                           headers=True, guion=False)
check(out_ed[0] == "ACORDADAS Y RESOLUCIONES", "editorial NUNCA enmascarado")
check(out_ed[2] == "", "frase-banner sí enmascarada en el mismo bloque")
check(out_ed[3] == "", "num tomo del banner enmascarado")

print(f"\n{ok} OK · {fail} FAIL")
sys.exit(1 if fail else 0)
