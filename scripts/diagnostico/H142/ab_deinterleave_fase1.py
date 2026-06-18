#!/usr/bin/env python3
"""
ab_deinterleave_fase1.py — A/B en disco del de-interleave admisión/mérito (M26, Fase 1). v2.
=============================================================================================
NO toca el parser. Simula sobre los 5890 reales la separación de `outcome` (plano) en
los dos canales canónicos y recomputa `is_merit` desde el deriver, ANTES de implementar.

Doctrina (Guillermo, H142):
  - procedente / admisible = SIEMPRE admisibilidad (canal admisión). No deciden el ganador.
  - El mérito y el ganador = el VERBO: disposicion ∈ {revoca, deja_sin_efecto, confirma, modifica, nulidad}.
  - hace lugar AL RECURSO = recurrente gana (trae el verbo atrás); hace lugar A LA QUEJA = admisión.
  - is_merit nuevo = (disposicion ∈ FONDO [+ grant_remand]) [AND NOT originaria].
  El canal admisión se arma de `queja_resultado` (admisión de la queja) + `procedente`/inadmisibles (REX).

Uso:  python ab_deinterleave_fase1.py [casos.csv] [recursos.csv]
"""
import csv, sys, os
from collections import Counter

_HERE=os.path.dirname(os.path.abspath(__file__))
_ROOT=os.path.abspath(os.path.join(_HERE,"..","..",".."))
sys.path.insert(0, os.path.join(_ROOT,"scripts","pipeline"))
import clasificador_disposicion as cd

CASOS=sys.argv[1] if len(sys.argv)>1 else os.path.join(_ROOT,"output","parser","csjn_casos.csv")
RECUR=sys.argv[2] if len(sys.argv)>2 else os.path.join(_ROOT,"output","parser","csjn_casos_recursos.csv")

FONDO=set(lab for lab,_ in cd.DISP)   # {revoca, deja_sin_efecto, nulidad, confirma, modifica}
GR="grant_remand_implicito"
ADMITE_Q={'hace_lugar','admisible','procedente'}
INADM_Q ={'desestima','rechaza','inadmisible','improcedente','abstracta','desistida','agreguese'}
INADM_OC={'inadmisible_280','inadmisible_acordada_4','desestima','mal_concedido','desierto','improcedente','caducidad','inadmisible'}

def load(p):
    with open(p,newline='',encoding='utf-8') as f: return {r['caso_id_canonico']:r for r in csv.DictReader(f)}
casos=load(CASOS); rec=load(RECUR)
R=[dict(oc=casos[k]['outcome'], qr=casos[k]['queja_resultado'], q=casos[k]['es_queja']=='1',
        orig=casos[k]['is_originaria']=='1', old=casos[k]['is_merit_decision']=='1',
        disp=rec[k]['disposicion']) for k in casos]
N=len(R); old1=sum(1 for x in R if x['old'])
print(f"# A/B v2 — de-interleave admisión/mérito (N={N})\n")

def merit(x,gr,guard):
    m=x['disp'] in FONDO or (gr and x['disp']==GR)
    return m and not (guard and x['orig'])
print("[1] is_merit nuevo — sensibilidad a las 2 decisiones abiertas")
print(f"    {'variante':38s} {'merit=1':>8s} {'gana':>6s} {'pierde':>7s} {'neto':>6s}")
for name,gr,guard in [("FONDO 5 verbos (base)",False,False),("+ grant_remand",True,False),
                      ("+ grant_remand + guard originaria",True,True)]:
    nm=[merit(x,gr,guard) for x in R]; n1=sum(nm)
    gain=sum(1 for x,m in zip(R,nm) if m and not x['old']); loss=sum(1 for x,m in zip(R,nm) if x['old'] and not m)
    print(f"    {name:38s} {n1:8d} {gain:6d} {loss:7d} {n1-old1:+6d}")
print(f"    (viejo is_merit=1 = {old1})\n")

print("[2] canal MÉRITO (disposicion fino):", dict(Counter(x['disp'] for x in R).most_common()),"\n")

def admision(x):
    if x['q'] and x['qr']:
        if x['qr'] in ADMITE_Q: return 'admite_queja'
        if x['qr'] in INADM_Q:  return 'inadmite_queja'
    if x['oc']=='procedente': return 'admite_rex'
    if x['oc'] in INADM_OC:   return 'inadmite_rex'
    if x['disp'] in FONDO or x['disp']==GR: return 'admite_implicito'
    return 'sin_marcador'
print("[3] canal ADMISIÓN (provisional — value-set §11 sin lockear):")
for lab,n in Counter(admision(x) for x in R).most_common(): print(f"     {n:5d}  {lab}")
print()

def coarse(x):
    if (x['disp'] in FONDO or x['disp']==GR) and not x['orig']: return 'fondo'
    return 'originaria' if x['orig'] else 'procedimiento'
print("[4] eje COARSE:", dict(Counter(coarse(x) for x in R).most_common()),"\n")

def legacyB(x):
    if x['disp'] in FONDO: return x['disp']
    if x['disp']==GR: return 'hace_lugar_recurso'
    return admision(x)
print("[5] outcome legacy bajo opción B (derivado):")
for lab,n in Counter(legacyB(x) for x in R).most_common(12): print(f"     {n:5d}  {lab}")
