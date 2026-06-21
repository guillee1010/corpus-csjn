import pandas as pd, unicodedata, numpy as np
from pathlib import Path
HERE = Path(__file__).resolve().parent      # scripts/validacion
ROOT = HERE.parents[1]                       # raiz del repo
CODIFICAR = HERE / 'golds' / 'planilla_M20_codificar-56xlsx.xlsx'
CLAVE     = HERE / 'M20_clave_parser_n300.csv'
CSJN      = ROOT / 'output' / 'parser' / 'csjn_casos.csv'
OUT       = HERE / 'golds' / 'planilla_M20_LIMPIA_n300__rebuild.xlsx'   # no pisa la LIMPIA canonica
print('[paths]'); print('  codificar:',CODIFICAR); print('  clave    :',CLAVE); print('  csjn     :',CSJN)
def na(s): return unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower().strip()

# ---------- CARGA ----------
P=pd.read_excel(CODIFICAR,dtype=str).fillna('')
P=P[P.caso_id_canonico.str.strip()!=''].copy()          # drop 2 filas vacías -> 300
if 'cod_materia.1' in P.columns: P=P.drop(columns=['cod_materia.1'])

# ---------- NORMALIZACIÓN ----------
dmap={'remite':'remite','sin_dictamen':'sin_dictamen','oido':'oido','conformidad':'conformidad',
 'concordantemente':'conformidad','concordante':'conformidad','cocordante':'conformidad',
 'concordante mdf':'conformidad','de conformidad':'conformidad',
 'habiendo dictaminado':'REVISAR','habiendo_dictaminado':'REVISAR'}
def ndict(s):
    s=na(s)
    if s=='':return ''
    return dmap.get(s,'REVISAR')
P['dict_n']=P.cod_dictamen.map(ndict)

def ncf(s):
    s=na(s)
    if s=='':return ''
    if s=='-':return 'REVISAR'
    if 'arbitrar' in s or 'denegacion' in s:return 'arbitrariedad'
    if s=='ninguna':return 'ninguna'
    if 'cuestion' in s or 'federal' in s or 'simple' in s or 'compleja' in s or 'mixto' in s:return 'cuestion_federal'
    return 'REVISAR'
P['cf_n']=P.cod_tipo_cuestion_federal.map(ncf)

# ---------- MERGE PARSER ----------
clave=pd.read_csv(CLAVE,dtype=str,keep_default_na=False)
c=pd.read_csv(CSJN,dtype=str,keep_default_na=False)
pc=c[['caso_id_canonico','es_queja','dictamen_presente','tipo_cuestion_federal','is_originaria']].drop_duplicates('caso_id_canonico')
m=P.merge(clave,on='caso_id_canonico',how='left').merge(pc,on='caso_id_canonico',how='left')
m['gate_gold']=m.cod_es_revision_fondo.map(na)
m['gate_par']=m.parser_es_revision_fondo.map(na)   # la clave ya guarda 'si'/'no'

print('='*60);print('GATE  (cod_es_revision_fondo vs parser)  n=300')
acc=(m.gate_gold==m.gate_par).mean()
print(f'  accuracy={acc:.3f}')
print('  confusión [fila=gold, col=parser]:')
print(pd.crosstab(m.gate_gold,m.gate_par).to_string())
fp=m[(m.gate_gold=='no')&(m.gate_par=='si')]   # parser dice fondo, gold dice no
fn=m[(m.gate_gold=='si')&(m.gate_par=='no')]
print(f'  FP(parser sí/gold no)={len(fp)}  | de esos quejas(es_queja=1)={ (fp.es_queja=="1").sum()} [B119]')
print(f'  FN(parser no/gold sí)={len(fn)}')

print('='*60);print('DISPOSICIÓN  (sobre merit codificado)')
d=m[(m.cod_disposicion.map(na)!='')&(m.cod_disposicion.map(na)!='-')&(m.parser_disposicion.str.strip()!='')].copy()
d['gd']=d.cod_disposicion.map(na);d['pd']=d.parser_disposicion.map(na)
print(f'  n={len(d)}  accuracy={ (d.gd==d.pd).mean():.3f}')
print('  dist gold:',{k:int(v) for k,v in d.gd.value_counts().items()})
for cl in ['deja_sin_efecto','revoca','confirma']:
    sub=d[d.gd==cl]; 
    if len(sub):print(f'    recall {cl:<16} {(sub.gd==sub.pd).mean():.2f} (n={len(sub)})')

print('='*60);print('PARTE_GANADORA + CERTIORARI CRIOLLO (queja via parser es_queja)')
pg=m[m.cod_parte_ganadora.map(na).isin(['recurrente_gana','recurrente_pierde','parcial'])].copy()
pg['gana']=pg.cod_parte_ganadora.map(na)=='recurrente_gana'
for lab,q in [('QUEJA','1'),('CONCEDIDO',None)]:
    s=pg[pg.es_queja=='1'] if q else pg[pg.es_queja!='1']
    dec=s[s.cod_parte_ganadora.map(na).isin(['recurrente_gana','recurrente_pierde'])]
    print(f'  {lab:<10} gana={dec.gana.mean():.0%} (n_decididos={len(dec)}, +{ (s.cod_parte_ganadora.map(na)=="parcial").sum()} parciales)')

print('='*60);print('VÍA RECURSIVA  (cod_via_recurso vs parser)')
vv=m[m.cod_via_recurso.isin(['recurso_extraordinario','recurso_ordinario'])].copy()
print(f'  n={len(vv)}  accuracy={ (vv.cod_via_recurso==vv.parser_via_recurso).mean():.3f}  sin_deteccion={(vv.parser_via_recurso=="").sum()}')
print('  confusión [fila=gold, col=parser]:')
print(pd.crosstab(vv.cod_via_recurso,vv.parser_via_recurso.replace("",".vacío.")).to_string())
print(f'  multi_recurso(parser)=si en el frame n300: {(m.parser_multi_recurso=="si").sum()}')

print('='*60);print('CUESTIÓN FEDERAL  (gold 3-way colapsado vs parser)  [B111]')
cf=m[m.cf_n.isin(['arbitrariedad','cuestion_federal','ninguna'])].copy()
def pcf(s):
    s=na(s)
    if 'arbitrar' in s:return 'arbitrariedad'
    if s in('','ninguna','none','no'):return 'ninguna'
    return 'cuestion_federal'  # incluye mixto/simple/compleja
cf['pcf']=cf.tipo_cuestion_federal.map(pcf)
print(f'  n={len(cf)}  accuracy={ (cf.cf_n==cf.pcf).mean():.3f}')
print('  confusión [fila=gold, col=parser]:')
print(pd.crosstab(cf.cf_n,cf.pcf).to_string())
print('  valor crudo parser donde gold=arbitrariedad:',{k:int(v) for k,v in cf[cf.cf_n=="arbitrariedad"].tipo_cuestion_federal.map(na).value_counts().items()})

print('='*60);print('DICTAMEN  (presencia: gold vs parser dictamen_presente)')
dd=m[m.dict_n!=''].copy()
dd['gold_presente']=dd.dict_n.isin(['remite','conformidad','oido'])  # REVISAR y sin_dictamen excluidos del "presente"
dd2=dd[dd.dict_n.isin(['remite','conformidad','oido','sin_dictamen'])].copy()
dd2['gp']=dd2.dict_n!='sin_dictamen'
dd2['pp']=dd2.dictamen_presente.isin(['True','true','1'])
print(f'  presencia n={len(dd2)} accuracy={ (dd2.gp==dd2.pp).mean():.3f}')
print('  dist 4-verbos (semilla derivar_dictamen):',{k:int(v) for k,v in dd.dict_n.value_counts().items()})
con=dd[dd.dict_n.isin(['remite','conformidad','oido'])]
print(f'  adhesión (remite+conformidad)/(con dictamen) = {con.dict_n.isin(["remite","conformidad"]).mean():.0%} (n={len(con)})')
print(f'  [REVISAR pendientes de recodificar: {(dd.dict_n=="REVISAR").sum()}]')

# guardar planilla limpia
out=P.drop(columns=['dict_n','cf_n']).copy()
out['cod_dictamen_norm']=P['dict_n']; out['cod_cf_norm']=P['cf_n']
out.to_excel(OUT,index=False)
print(f'\n[guardada {OUT}]')
