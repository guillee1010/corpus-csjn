#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modo materia para muestrear_validacion.py (-> v1.2). Anclado a la SRS de M19.

- Marco A: los MISMOS 300 ids ya codificados en M19 (se leen de la planilla
  consolidada; NO se re-sortea -> el gold de materia es sobre la misma muestra
  insesgada que el resto de la validacion).
- Marco B: oversample por valor de `materia` (parser), min(N_OBJETIVO, N_corpus)
  por valor, tomado del corpus menos los 300. Censa las finas.
- Ceguera: la planilla de codificacion NO trae materia/capa/fuente. La clave si.
"""
import csv, random
from collections import OrderedDict, Counter

__version__ = "1.2"
ID = "caso_id_canonico"
SEED = 20260531
N_OBJETIVO_B = 20
N_DOBLE = 50

U = "/mnt/user-data/uploads/"
csv.field_size_limit(10**7)

def cargar(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))

casos = {r[ID]: r for r in cargar(U+"csjn_casos.csv")}
mat   = {r[ID]: r for r in cargar(U+"csjn_casos_materia.csv")}
p300  = cargar(U+"planilla_consolidada_MARCO_A_v18_15_n300.csv")
marco_a = [r[ID] for r in p300]
marco_a_set = set(marco_a)

rng = random.Random(SEED)

# --- Marco B: oversample por valor de materia (solo substantivos), anclado en 300 ---
porval = {}
for cid, r in mat.items():
    v = r["materia"]
    if v:  # solo valores substantivos
        porval.setdefault(v, []).append(cid)

extra_b = OrderedDict()  # cid -> [etiquetas]
for v, ids in sorted(porval.items(), key=lambda kv: len(kv[1])):
    obj = min(N_OBJETIVO_B, len(ids))
    ya = [i for i in ids if i in marco_a_set or i in extra_b]
    et = "materia=%s" % v
    for i in ya:
        if i in extra_b:
            extra_b[i].append(et)
    faltan = obj - len(ya)
    if faltan > 0:
        disp = [i for i in ids if i not in marco_a_set and i not in extra_b]
        for i in rng.sample(disp, min(faltan, len(disp))):
            extra_b.setdefault(i, []).append(et)

marco_b_set = set(extra_b)
union = sorted(marco_a_set | marco_b_set, key=lambda c: (int(c.split("_")[0]), c))
doble = set(rng.sample(union, min(N_DOBLE, len(union))))

# --- clave (con la respuesta del parser) ---
with open("muestra_clave_materia_v18.15.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow([ID,"marco","origen_b","doble_cod","materia_capa","materia_fuente","parser_materia"])
    for cid in union:
        m=mat.get(cid,{})
        marco=("A" if cid in marco_a_set else "")+("B" if cid in marco_b_set else "")
        w.writerow([cid,marco,"|".join(extra_b.get(cid,[])),int(cid in doble),
                    m.get("materia_capa",""),m.get("materia_fuente",""),m.get("materia","")])

# --- planilla CIEGA (sin materia/capa/fuente) ---
with open("planilla_codificacion_materia_v18.15.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f)
    w.writerow([ID,"tomo","date","case_name_cuerpo","source_file","linea_inicio",
                "linea_fin_real","doble_cod","cod_materia","notas"])
    for cid in union:
        r=casos.get(cid,{})
        w.writerow([cid,r.get("tomo",""),r.get("date",""),r.get("case_name_cuerpo",""),
                    r.get("source_file",""),r.get("linea_inicio",""),
                    r.get("linea_fin_real",""),int(cid in doble),"",""])

# --- reporte ---
print("muestrear_materia v%s  seed=%d"%(__version__,SEED))
print("Marco A %d | Marco B(extra) %d | UNION %d | doble %d"%(
      len(marco_a_set),len(marco_b_set),len(union),len(doble)))
print("\nMarco B top-up por valor:")
cb=Counter()
for cid,ets in extra_b.items():
    for e in ets:
        if cid not in marco_a_set: cb[e]+=1
for e,n in cb.most_common():
    print("   %-26s +%d"%(e.split("=")[1],n))
