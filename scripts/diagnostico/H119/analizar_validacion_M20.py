#!/usr/bin/env python3
"""H119 — Métricas de validación M20 (gate + disposición + parte_ganadora + reenvía).
Uso:  python analizar_validacion_M20.py [planilla_codificada.csv] [clave_parser.csv]
Mismo espíritu que analizar_validacion.py (M19): precision/recall por valor + Wilson 95%.
Corre DESPUÉS de codificar la planilla ciega. Filtra a filas codificadas."""
import sys, math, pandas as pd

PLAN  = sys.argv[1] if len(sys.argv)>1 else "planilla_M20_blind_n300.csv"
CLAVE = sys.argv[2] if len(sys.argv)>2 else "M20_clave_parser_n300.csv"
Z = 1.959963985

def wilson(k, n):
    if n == 0: return (float('nan'), float('nan'))
    p = k/n; z2 = Z*Z
    denom = 1 + z2/n
    centre = (p + z2/(2*n)) / denom
    half = (Z*math.sqrt(p*(1-p)/n + z2/(4*n*n))) / denom
    return (max(0,centre-half), min(1,centre+half))

def pr_por_valor(gold, pred, valores=None):
    g = list(gold); pr = list(pred)
    vals = valores or sorted(set(g) | set(pr))
    rows=[]
    for v in vals:
        tp = sum(1 for a,b in zip(g,pr) if a==v and b==v)
        fp = sum(1 for a,b in zip(g,pr) if a!=v and b==v)
        fn = sum(1 for a,b in zip(g,pr) if a==v and b!=v)
        sup = sum(1 for a in g if a==v)
        prec = tp/(tp+fp) if (tp+fp) else float('nan')
        rec  = tp/(tp+fn) if (tp+fn) else float('nan')
        f1 = 2*prec*rec/(prec+rec) if (prec==prec and rec==rec and (prec+rec)>0) else float('nan')
        rlo,rhi = wilson(tp, tp+fn)
        rows.append((v, sup, prec, rec, f1, rlo, rhi))
    return rows

def tabla(rows, titulo):
    print(f"\n  {titulo}")
    print(f"  {'valor':<26}{'sup':>5}{'prec':>8}{'rec':>8}{'F1':>8}   recall 95% CI    aviso")
    for v,sup,pr,rc,f1,lo,hi in rows:
        pf=lambda x:'  n/a ' if x!=x else f'{x:6.3f}'
        ci= '   n/a       ' if lo!=lo else f'[{lo:.2f},{hi:.2f}]'
        warn = '⚠ n<10' if sup<10 else ''
        print(f"  {v:<26}{sup:>5}{pf(pr):>8}{pf(rc):>8}{pf(f1):>8}   {ci:<13}{warn}")

def matriz(gold, pred, titulo):
    df = pd.crosstab(pd.Series(gold,name='GOLD'), pd.Series(pred,name='PARSER'))
    print(f"\n  Matriz de confusión {titulo} (filas=gold, cols=parser):")
    print(df.to_string().replace('\n','\n  '))

# ---- carga + merge ----
pl = pd.read_csv(PLAN, dtype=str, keep_default_na=False)
cl = pd.read_csv(CLAVE, dtype=str, keep_default_na=False)
df = pl.merge(cl, on="caso_id_canonico", how="left")
norm = lambda s: (s or "").strip().lower()
for c in ["cod_es_revision_fondo","cod_disposicion","cod_reenvia","cod_parte_ganadora"]:
    df[c]=df[c].map(norm)
df = df[df.cod_es_revision_fondo!=""]  # solo filas codificadas
print(f"Frame: {len(pl)}  |  codificado: {len(df)}")
if len(df)==0:
    print("\n>>> La planilla todavía no está codificada (cod_es_revision_fondo vacío). Codificá y volvé a correr.")
    sys.exit(0)

# =================== BLOQUE 1 — GATE (es_revision_fondo) ===================
print("\n" + "="*70 + "\nBLOQUE 1 — GATE  cod_es_revision_fondo vs parser (is_merit)\n" + "="*70)
g = df.cod_es_revision_fondo; pp = df.parser_es_revision_fondo
acc = (g==pp).mean()
matriz(g, pp, "GATE")
print(f"\n  Acuerdo gate: {acc:.3f}")
fn = df[(g=="si") & (pp=="no")]   # revisión de fondo que el gate dejó afuera
fp = df[(g=="no") & (pp=="si")]
print(f"  FALSOS NEGATIVOS del gate (humano=sí, parser=no): {len(fn)}")
for _,r in fn.iterrows():
    print(f"     {r.caso_id_canonico}  outcome_m19={r._ctx_outcome_m19:<12} «{r.caratula[:48]}»")
print(f"  Falsos positivos (humano=no, parser=sí): {len(fp)}")
for _,r in fp.iterrows():
    print(f"     {r.caso_id_canonico}  outcome_m19={r._ctx_outcome_m19:<12} «{r.caratula[:48]}»")

# universo de revisión = lo que el HUMANO marcó como revisión de fondo
rev = df[df.cod_es_revision_fondo=="si"].copy()
print(f"\n  Universo-revisión (humano=sí): n={len(rev)}")

# =================== BLOQUE 2 — DISPOSICIÓN ===================
print("\n" + "="*70 + "\nBLOQUE 2 — DISPOSICIÓN (universo-revisión)\n" + "="*70)
SCDB = ["revoca","deja_sin_efecto","nulidad","confirma","modifica"]
d = rev[rev.cod_disposicion!=""].copy()
# normalizar parser a comparable: lo no-SCDB del parser cuenta como error
d["parser_disp_cmp"] = d.parser_disposicion.where(d.parser_disposicion.isin(SCDB), "—(no_legible/no_rev)")
acc_d = (d.cod_disposicion==d.parser_disp_cmp).mean()
print(f"  n codificado en disposición: {len(d)}   |   accuracy global: {acc_d:.3f}")
tabla(pr_por_valor(d.cod_disposicion, d.parser_disp_cmp, SCDB), "Precision/Recall por valor SCDB")
matriz(d.cod_disposicion, d.parser_disp_cmp, "DISPOSICIÓN")

# =================== BLOQUE 3 — PARTE GANADORA ===================
print("\n" + "="*70 + "\nBLOQUE 3 — PARTE GANADORA (universo-revisión)\n" + "="*70)
PG = ["recurrente_gana","recurrente_pierde","parcial","reenvio_sin_resultado","no_aplica"]
pg = rev[rev.cod_parte_ganadora!=""].copy()
acc_pg = (pg.cod_parte_ganadora==pg.parser_parte_ganadora).mean()
print(f"  (a) Exactitud directa cod vs parser  —  n={len(pg)}  accuracy: {acc_pg:.3f}")
tabla(pr_por_valor(pg.cod_parte_ganadora, pg.parser_parte_ganadora, PG), "P/R por valor")

# (b) FIDELIDAD DE LA REGLA: derive(cod_disposicion) vs cod_parte_ganadora
def regla(disp):
    if disp in ("revoca","deja_sin_efecto","nulidad"): return "recurrente_gana"
    if disp=="confirma": return "recurrente_pierde"
    if disp=="modifica": return "parcial"
    return None
pgr = pg[pg.cod_disposicion.isin(SCDB)].copy()
pgr["regla_pred"]=pgr.cod_disposicion.map(regla)
fidel = (pgr.regla_pred==pgr.cod_parte_ganadora).mean() if len(pgr) else float('nan')
diverg = pgr[pgr.regla_pred!=pgr.cod_parte_ganadora]
print(f"\n  (b) FIDELIDAD DE LA REGLA (derive(cod_disp)==cod_parte_ganadora): {fidel:.3f}  sobre n={len(pgr)}")
print(f"      Casos donde la regla verbo→ganador FALLA según lectura humana: {len(diverg)}")
for _,r in diverg.iterrows():
    print(f"        {r.caso_id_canonico}  disp={r.cod_disposicion:<16} regla→{r.regla_pred:<18} humano→{r.cod_parte_ganadora}")

# (c) REENVÍO: cómo codificó el humano la parte ganadora cuando hubo reenvío
reenv = pg[pg.cod_reenvia=="si"]
print(f"\n  (c) Casos con reenvío (cod_reenvia=sí): n={len(reenv)}  →  decisión #3 (default grant_remand)")
if len(reenv): print("     " + reenv.cod_parte_ganadora.value_counts().to_string().replace('\n','\n     '))

# =================== BLOQUE 4 — REENVÍA (flag) ===================
print("\n" + "="*70 + "\nBLOQUE 4 — REENVÍA (flag remand)\n" + "="*70)
rv = rev[rev.cod_reenvia!=""]
if len(rv):
    matriz(rv.cod_reenvia, rv.parser_reenvia, "REENVÍA")
    print(f"\n  Acuerdo reenvía: {(rv.cod_reenvia==rv.parser_reenvia).mean():.3f}")

print("\n" + "="*70 + "\nFIN. Pegá el bloque que quieras en BITACORA/CHANGELOG (te preparo el texto).\n" + "="*70)
