"""mostrar_caso.py — Muestra qué ve el parser antes y después del fix."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from pipeline.parser import (
    RE_DICT_HDR, RE_FECHA_LINEA, RE_APERTURA,
    cargar_localizados, cargar_proximos_headers,
    construir_bloque_desde_localizacion, detectar_fin_real,
    refinar_inicio_por_titulo, detectar_apertura_en_bloque,
    detectar_apertura_dispositivo, primer_token_de_caratula,
    proximo_header_despues_de, collect_firma_lines,
)

CID = sys.argv[1] if len(sys.argv) > 1 else "331_p446"

loc_rows, _ = cargar_localizados(str(REPO / "output/localizacion/fallos_localizados.csv"))
headers_map = cargar_proximos_headers(str(REPO / "output/mapa/mapa_paginas.csv"))

# Construir siguiente_caso
cat_por_tomo = {}
for row in loc_rows:
    cat_por_tomo.setdefault(int(row["tomo"]), []).append({
        "caso_id_canonico": row["caso_id_canonico"],
        "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
    })
for t in cat_por_tomo:
    cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
siguiente_caso = {}
primer_token_por_caso = {}
for t, lst in cat_por_tomo.items():
    for i, c in enumerate(lst[:-1]):
        siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]
for row in loc_rows:
    primer_token_por_caso[row["caso_id_canonico"]] = primer_token_de_caratula(
        row.get("nombres_indice", "")
    )

fallo = [r for r in loc_rows if r["caso_id_canonico"] == CID]
if not fallo:
    print(f"Caso {CID} no encontrado")
    sys.exit(1)
fallo = fallo[0]
tomo = int(fallo["tomo"])
archivo = fallo["archivo"]
fp = REPO / "corpus" / archivo
lines = fp.read_text(encoding="utf-8").split("\n")
li = int(fallo["linea_inicio"])
lf_cat = int(fallo["linea_fin"]) if fallo["linea_fin"] else len(lines) - 1

sig = siguiente_caso.get(CID)
pt_sig = primer_token_por_caso.get(sig, "") if sig else ""
ha = list(headers_map.get((tomo, archivo), []))
ha.sort()
prox_h = proximo_header_despues_de(ha, lf_cat)
lfr, sf, pf = detectar_fin_real(lines, li, lf_cat, prox_h, pt_sig)

bloque = construir_bloque_desde_localizacion(lines, li, lfr)
offset, ancla = refinar_inicio_por_titulo(bloque, fallo.get("nombres_indice", ""))
bloque = bloque[offset:]
li_eff = li + offset


def run_dictamen_loop(bloque, use_backstop):
    """Corre el loop de dictamen con o sin backstop."""
    en_dict = False
    dict_lines = set()
    for k, bl in enumerate(bloque):
        s = bl.strip()
        if not s:
            continue
        if RE_DICT_HDR.match(s):
            en_dict = True
            dict_lines.add(k)
            continue
        elif en_dict:
            if use_backstop and RE_APERTURA.match(s):
                en_dict = False
            else:
                dict_lines.add(k)
                if RE_FECHA_LINEA.match(s) and k > 5:
                    prev = bloque[k - 1].strip() if k > 0 else ""
                    if prev and len(prev) < 80:
                        en_dict = False
                continue
    return dict_lines, en_dict


def run_anchored_search(bloque, apertura_rel, dict_lines):
    """Busca dispositivo con la logica anclada."""
    if apertura_rel is not None:
        ib = apertura_rel
    else:
        de = max(dict_lines) if dict_lines else None
        ib = (de + 1) if de is not None else 0
    for k in range(ib, len(bloque)):
        if k in dict_lines:
            continue
        s = bloque[k].strip()
        if not s:
            continue
        es, tipo = detectar_apertura_dispositivo(s)
        if es:
            return k
    return None


at, ar = detectar_apertura_en_bloque(bloque)

# Correr SIN backstop (comportamiento viejo)
dict_old, en_dict_old = run_dictamen_loop(bloque, use_backstop=False)
pe_old = run_anchored_search(bloque, ar, dict_old)

# Correr CON backstop (comportamiento nuevo)
dict_new, en_dict_new = run_dictamen_loop(bloque, use_backstop=True)
pe_new = run_anchored_search(bloque, ar, dict_new)

print("=" * 90)
print(f"  CASO: {CID}  |  archivo: {archivo}")
print(f"  bloque: lineas {li_eff}-{li_eff+len(bloque)-1} ({len(bloque)} lineas)")
print(f"  apertura: tipo={at} en linea {li_eff + ar if ar is not None else '?'}")
print("=" * 90)

print(f"\n  SIN backstop (viejo): dictamen={len(dict_old)} lineas, "
      f"en_dict_final={en_dict_old}, dispositivo={'SI' if pe_old else 'NO'}")
print(f"  CON backstop (nuevo): dictamen={len(dict_new)} lineas, "
      f"en_dict_final={en_dict_new}, dispositivo={'SI' if pe_new else 'NO'}")

if pe_new and not pe_old:
    firma = collect_firma_lines(bloque, pe_new + 1)
    print(f"\n  DISPOSITIVO RECUPERADO en linea {li_eff + pe_new}:")
    print(f"    {bloque[pe_new].strip()[:100]}")
    print(f"  FIRMA RECUPERADA:")
    print(f"    {firma[:100]}")

# Mostrar las lineas alrededor de la frontera dictamen/apertura
print(f"\n{'─' * 90}")
print(f"  LINEAS DEL .md ALREDEDOR DE LA FRONTERA (dictamen -> apertura)")
print(f"{'─' * 90}")

# Encontrar donde termina el dictamen nuevo
if dict_new:
    last_dict = max(dict_new)
else:
    last_dict = 0

# Mostrar desde 5 antes del fin del dictamen hasta 15 despues
start = max(0, last_dict - 5)
end = min(len(bloque), last_dict + 16)

for k in range(start, end):
    in_old = k in dict_old
    in_new = k in dict_new
    marker = ""
    if in_old and not in_new:
        marker = " <<<< ANTES: dictamen, AHORA: libre"
    elif not in_old and not in_new:
        marker = ""
    elif in_old and in_new:
        marker = " [dictamen]"

    s = bloque[k].strip()
    if not s:
        continue
    line_abs = li_eff + k
    tag = ""
    if pe_new == k:
        tag = " ** DISPOSITIVO **"
    if RE_APERTURA.match(s):
        tag = " ** APERTURA (backstop cierra dictamen aca) **"

    print(f"  {line_abs:>6} | {s[:70]:<70}{marker}{tag}")
