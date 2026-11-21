"""unir_sjconsulta.py — une cada caso del corpus con los datos de sjconsulta (M66, H221)

Lee los JSON que baja scripts/validacion/cruce_sjconsulta.py (sj_AAAAMM_v03.json, cache local)
y output/parser/csjn_casos.csv (solo lectura). No hace pedidos al sitio.

Escribe en el cache (local, gitignoreado):
  casos_sjconsulta.csv               una fila por caso del corpus con par en sjconsulta: secretaría,
                                     fecha de entrada a la Secretaría de Jurisprudencia, sentido, tipo de
                                     recurso, materia SJ, marcas, n de sumarios. SIN datos de funcionarios.
  casos_sjconsulta_funcionarial.csv  códigos, nombres y cargos de quienes cargaron cada caso. SOLO LOCAL:
                                     uso analítico de la tesis, anonimizar en toda exposición.
Imprime un primer análisis por secretaría con los datos de votación del corpus.

Llave: tomo+página (caso_id_canonico = <tomo>_p<pagina>). Si varios fallos de SJ caen en la misma
página (entradas de sumario), se conserva el primero y se informa la cantidad.

Uso:
  python scripts/analisis/unir_sjconsulta.py [--cache DIR]   (default scripts/diagnostico/sjconsulta)
"""
__version__ = "0.1"  # H221
import argparse, csv, glob, json, sys
from collections import Counter, defaultdict
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

RAIZ = Path(__file__).resolve().parents[2]
_ap = argparse.ArgumentParser(description="une casos del corpus con sjconsulta (M66)")
_ap.add_argument("--cache", default=str(RAIZ / "scripts" / "diagnostico" / "sjconsulta"))
CACHE = Path(_ap.parse_args().cache)
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"

def cod(u):
    return u.get("codigo") if isinstance(u, dict) else u

# 1. un registro por fallo de SJ (primer sumario), agregando n de sumarios y marcas
fallos, n_sum = {}, Counter()
for p in sorted(glob.glob(str(CACHE / "sj_*_v03.json"))):
    for r in json.load(open(p, encoding="utf-8")):
        n_sum[r["id_fallo"]] += 1
        f = fallos.setdefault(r["id_fallo"], dict(r, _arb=False, _inc=False))
        f["_arb"] = f["_arb"] or bool(r.get("sentencia_arbitraria"))
        f["_inc"] = f["_inc"] or bool(r.get("inconstitucional"))
if not fallos:
    sys.exit(f"ERROR: no hay sj_*_v03.json en {CACHE}")

por_clave, colisiones = {}, Counter()
for idf, f in fallos.items():
    if not f.get("tomo") or not f.get("pagina"): continue
    k = f"{f['tomo']}_p{f['pagina']}"
    colisiones[k] += 1
    por_clave.setdefault(k, (idf, f))

casos = {r["caso_id_canonico"]: r for r in csv.DictReader(CASOS.open(encoding="utf-8", newline=""))}

filas, filas_fun = [], []
for k, (idf, f) in sorted(por_clave.items()):
    if k not in casos: continue
    votos = " ; ".join(f"{v['tipo']}: {', '.join(v['ministros'])}" for v in f.get("an_votos") or [])
    filas.append({
        "caso_id_canonico": k, "id_fallo_sj": idf, "fallos_sj_misma_pagina": colisiones[k],
        "fecha_sj": f.get("fecha"), "secretaria": f.get("an_secretaria"),
        "fecha_entrada_sj": f.get("an_fecha_entrada"), "sentido": f.get("an_sentido"),
        "tipo_recurso": f.get("an_tipo_recurso"), "materia_sj": f.get("an_materia"),
        "sentencia_arbitraria": f["_arb"], "inconstitucional": f["_inc"],
        "n_sumarios": n_sum[idf], "votos_sj": votos,
    })
    fu = f.get("funcionarial") or {}
    an = fu.get("analisis") or {}
    um = an.get("usuarioModificacion")
    voces = sorted({cod(v.get("usuarioCreacion")) for v in fu.get("voces") or [] if v.get("usuarioCreacion")})
    filas_fun.append({
        "caso_id_canonico": k,
        "recibo_codigo": (fu.get("recibo") or {}).get("codigoUsuario"),
        "recibo_fecha": (fu.get("recibo") or {}).get("fecha"),
        "analisis_fecha_creacion": an.get("fechaCreacion"),
        "analisis_fecha_modificacion": an.get("fechaModificacion"),
        "analisis_modif_codigo": cod(um),
        "analisis_modif_nombre": (f"{um.get('apellido') or ''}, {um.get('nombre') or ''}".strip(", ")
                                  if isinstance(um, dict) else ""),
        "analisis_modif_cargo": um.get("cargo") if isinstance(um, dict) else "",
        "voces_codigos": " ".join(c for c in voces if c),
        "sumario_crea_codigo": (fu.get("sumario") or {}).get("usuarioCreacionOld"),
    })

def escribir(nombre, rows):
    if not rows: return
    with (CACHE / nombre).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

escribir("casos_sjconsulta.csv", filas)
escribir("casos_sjconsulta_funcionarial.csv", filas_fun)

print(f"unir_sjconsulta v{__version__} · fallos SJ {len(fallos)} · casos del corpus unidos {len(filas)} de {len(casos)}")
print(f"  páginas con más de un fallo SJ (entradas de sumario): {sum(1 for k, n in colisiones.items() if n > 1 and k in casos)}")
print(f"  archivos: {CACHE / 'casos_sjconsulta.csv'}\n           {CACHE / 'casos_sjconsulta_funcionarial.csv'} (solo local)\n")

# 2. primer análisis por secretaría con la votación del corpus (solo entradas tipo fallo)
agr = defaultdict(lambda: {"n": 0, "vp": Counter(), "disid": 0, "merit": 0})
for row in filas:
    c = casos[row["caso_id_canonico"]]
    if c.get("tipo_entrada") != "fallo": continue
    a = agr[row["secretaria"] or "(sin dato)"]
    a["n"] += 1
    a["vp"][c.get("voting_pattern") or "?"] += 1
    if (c.get("n_disidencias") or "0") not in ("", "0"): a["disid"] += 1
    if c.get("is_merit_decision") in ("1", "True", "true"): a["merit"] += 1

print("Por secretaría (fallos completos): n · % unánime · % según su voto · % disidencia · % mixed · % con ≥1 disidencia · % decisión de mérito")
for sec, a in sorted(agr.items(), key=lambda kv: -kv[1]["n"]):
    n = a["n"] or 1
    pct = lambda k: f"{a['vp'][k] * 100 / n:5.1f}"
    print(f"  {sec[:42]:42s} {a['n']:4d} · {pct('unanime')} · {pct('segun_su_voto')} · {pct('disidencia')} · {pct('mixed')}"
          f" · {a['disid'] * 100 / n:5.1f} · {a['merit'] * 100 / n:5.1f}")
