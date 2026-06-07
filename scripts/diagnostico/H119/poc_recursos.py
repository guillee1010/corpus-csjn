#!/usr/bin/env python3
"""PoC H119 — candidato csjn_casos_recursos: disposición (paso-3, de H118) +
parte_ganadora DERIVADA por regla + vía. DIAGNÓSTICO, no toca el parser.

Regla parte_ganadora (estilo SCDB partyWinning, derivada NO codificada):
  el recurrente trae el REX/queja contra una sentencia que le fue adversa →
   - disposición revoca/deja_sin_efecto/nulidad  -> recurrente GANA (la de abajo cae)
   - disposición confirma                        -> recurrente PIERDE (la de abajo queda)
   - disposición modifica                        -> PARCIAL
   - grant_remand_implícito                      -> GANA  [DECISIÓN: vacate implícito, default]
   - no_revision_* / sin_disposicion             -> no_aplica

Unidad: parte×recurso. Para el 98% single-recurrente = 1 fila/caso (regla directa).
La cola multi-recurrente (~2%) se MARCA needs_alignment (requiere alinear carátula↔por_ello
por nombre — problema de alias, PoC aparte)."""
import pandas as pd, csv, re
csv.field_size_limit(10**7)
def norm(s):
    s=re.sub(r"­","",s or ""); s=re.sub(r"(\w)-\s+(\w)",r"\1\2",s); return re.sub(r"\s+"," ",s).strip()

OBJ=r"(?:la|las|el|los)\s+(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto)s?\b"
OBJX=r"(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto|sanci[oó]n|pena|condena|multa)s?\b"
W=r"[^.;]{0,55}"
DISP=[("revoca",re.compile(rf"\b(?:se\s+)?revoca(?:n)?\b{W}{OBJ}|\brevocar\b{W}{OBJ}|revoc[áa]ndose{W}{OBJ}",re.I)),
 ("deja_sin_efecto",re.compile(rf"\bdeja(?:r|se|n)?\s+sin\s+efecto\b{W}{OBJ}|\bdej[áa]ndose\s+sin\s+efecto\b{W}?{OBJ}|\bdejando\s+sin\s+efecto\b{W}?{OBJ}|\bd[ée]jase\s+sin\s+efecto\b{W}?{OBJ}|\bdeje\s+sin\s+efecto\b{W}?{OBJ}",re.I)),
 ("nulidad",re.compile(rf"\bnulidad\s+de\s+todo\s+lo\s+actuado\b|\b(?:se\s+)?declara\s+(?:la\s+)?nul[ao]s?\b|\bnulidad\b{W}{OBJ}|\b(?:se\s+)?anula\b{W}{OBJ}|\binvalidez\b{W}?{OBJ}|\bdeclara\s+(?:la\s+)?inv[áa]lid",re.I)),
 ("confirma",re.compile(rf"\b(?:se\s+)?confirma(?:n)?\b{W}{OBJ}|\bconfirmar\b{W}{OBJ}|confirm[áa]ndose{W}{OBJ}",re.I)),
 ("modifica",re.compile(rf"\b(?:se\s+)?modifica(?:n)?\b{W}{OBJX}|\bsustituir\b{W}{OBJX}|\b(?:se\s+)?sustituye\b{W}{OBJX}",re.I))]
RE_RECHAZA_REC=re.compile(r"\b(?:se\s+)?rechaza(?:n)?\b[^.;]{0,40}\b(?:recurso|queja)\b",re.I)
RE_REMAND=re.compile(r"vuelvan?\s+los\s+autos|dicte\s+(?:un\s+)?nuev[ao]|nuevo\s+(?:pronunciamiento|fallo|sentencia)",re.I)
RE_COMPET=re.compile(r"\bresulta\s+competente\b|\bdeclara\s+(?:la\s+)?(?:in)?competencia\b|\bdeber[áa]\s+entender\b|\bdeclara\s+competente\b",re.I)
RE_DEMANDA=re.compile(r"\b(?:hac\w+\s+lugar|rechaz\w+|admit\w+|desestim\w+)\b[^.;]{0,30}\b(?:demanda|acci[oó]n|pretensi[oó]n)\b",re.I)
RE_PROCESAL=re.compile(r"\bcaducidad\b|\breposici[oó]n\b|\baclaratoria\b|\bhonorarios\b|\bcitaci[oó]n\b|\bterceros?\b|\bsuspensi[oó]n\b|\brecusaci[oó]n\b|\bexcusaci[oó]n\b|\bcautelar\b|\bbeneficio\s+de\s+litigar\b|\bintimaci[oó]n\b|\bavocaci[oó]n\b|mal\s+(?:denegad|concedid)|\bexcepci[oó]n\b|\bdefecto\s+legal\b|\bfalta\s+de\s+legitimaci[oó]n\b",re.I)
RE_HEADER=re.compile(r"(?:DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N|FALLOS\s+DE\s+LA\s+CORTE)\s*\d*\s*$",re.I)
RE_GRANT=re.compile(r"hace\s+lugar|procedente",re.I)

def disposicion(pe):
    pe=norm(pe); enc=[l for l,p in DISP if p.search(pe)]; remand=bool(RE_REMAND.search(pe))
    if enc: return enc[0], len(set(enc)), remand
    if RE_RECHAZA_REC.search(pe): return "confirma",1,remand
    if RE_COMPET.search(pe): return "no_revision_competencia",0,remand
    if RE_DEMANDA.search(pe): return "no_revision_demanda",0,remand
    if RE_PROCESAL.search(pe): return "no_revision_procesal",0,remand
    if RE_HEADER.search(pe): return "por_ello_cortado",0,remand
    if RE_GRANT.search(pe) and remand: return "grant_remand_implicito",0,remand
    return "sin_disposicion_legible",0,remand

GANA={"revoca","deja_sin_efecto","nulidad","grant_remand_implicito"}
def parte_ganadora(disp):
    if disp in GANA: return "recurrente_gana"
    if disp=="confirma": return "recurrente_pierde"
    if disp=="modifica": return "parcial"
    return "no_aplica"

df=pd.read_csv("/mnt/user-data/uploads/csjn_casos.csv",dtype=str,keep_default_na=False)
t=pd.read_csv("/mnt/user-data/uploads/csjn_casos_textos.csv",dtype=str,keep_default_na=False)[["caso_id_canonico","por_ello_text"]]
f=df[(df.tipo_entrada=="fallo")&(df.is_merit_decision=="1")].merge(t,on="caso_id_canonico",how="left")
r=f.por_ello_text.map(disposicion)
f["disposicion"]=r.map(lambda x:x[0]); f["n_disp"]=r.map(lambda x:x[1]); f["reenvia"]=r.map(lambda x:x[2])
f["via"]=f.es_queja.map(lambda q:"queja" if q=="1" else "recurso_concedido")
f["parte_ganadora"]=f.disposicion.map(parte_ganadora)
f["needs_alignment"]=f.n_disp>=2   # cola multi-recurrente: fork por parte (PoC aparte)

print("Universo fondo:",len(f))
print("\n=== parte_ganadora (derivada) ===")
for k,v in f.parte_ganadora.value_counts().items(): print(f"  {k:<20} {v:>5} ({100*v/len(f):.1f}%)")
print("\n=== cruce disposición × parte_ganadora ===")
print(pd.crosstab(f.disposicion,f.parte_ganadora).to_string())
print("\n=== vía × parte_ganadora (¿gana más por queja o por recurso concedido?) ===")
rev=f[f.parte_ganadora.isin(["recurrente_gana","recurrente_pierde"])]
print(pd.crosstab(rev.via,rev.parte_ganadora,normalize='index').round(3).to_string())
print(f"\n  cola multi-recurrente needs_alignment: {f.needs_alignment.sum()} (fork por parte, PoC aparte)")

cols=["caso_id_canonico","via","disposicion","parte_ganadora","reenvia","needs_alignment"]
f[cols].to_csv("/home/claude/H119_poc/cand_recursos.csv",index=False)
print("\ncandidato csjn_casos_recursos (98% = 1 fila/caso) -> cand_recursos.csv")
