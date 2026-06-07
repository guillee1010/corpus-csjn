#!/usr/bin/env python3
"""PoC H118 v3 — fix objeto plural + 'todo lo actuado' (nulidad), ruteo no-revisión,
y bucket grant_remand_implicito (vacate implícito, decisión de codificación). DIAGNÓSTICO."""
import pandas as pd, csv, re
csv.field_size_limit(10**7)
def norm(s):
    s=re.sub(r"­","",s or ""); s=re.sub(r"(\w)-\s+(\w)",r"\1\2",s); return re.sub(r"\s+"," ",s).strip()

# objeto: singular Y plural
OBJ  = r"(?:la|las|el|los)\s+(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto)s?\b"
OBJX = r"(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto|sanci[oó]n|pena|condena|multa)s?\b"
W = r"[^.;]{0,55}"
DISP = [
    ("revoca",  re.compile(rf"\b(?:se\s+)?revoca(?:n)?\b{W}{OBJ}|\brevocar\b{W}{OBJ}|revoc[áa]ndose{W}{OBJ}", re.I)),
    ("deja_sin_efecto", re.compile(
        rf"\bdeja(?:r|se|n)?\s+sin\s+efecto\b{W}{OBJ}|\bdej[áa]ndose\s+sin\s+efecto\b{W}?{OBJ}|"
        rf"\bdejando\s+sin\s+efecto\b{W}?{OBJ}|\bd[ée]jase\s+sin\s+efecto\b{W}?{OBJ}|\bdeje\s+sin\s+efecto\b{W}?{OBJ}", re.I)),
    ("nulidad", re.compile(
        rf"\bnulidad\s+de\s+todo\s+lo\s+actuado\b|\b(?:se\s+)?declara\s+(?:la\s+)?nul[ao]s?\b|\bnulidad\b{W}{OBJ}|"
        rf"\b(?:se\s+)?anula\b{W}{OBJ}|\binvalidez\b{W}?{OBJ}|\bdeclara\s+(?:la\s+)?inv[áa]lid", re.I)),
    ("confirma", re.compile(rf"\b(?:se\s+)?confirma(?:n)?\b{W}{OBJ}|\bconfirmar\b{W}{OBJ}|confirm[áa]ndose{W}{OBJ}", re.I)),
    ("modifica", re.compile(rf"\b(?:se\s+)?modifica(?:n)?\b{W}{OBJX}|\bsustituir\b{W}{OBJX}|\b(?:se\s+)?sustituye\b{W}{OBJX}", re.I)),
]
RE_RECHAZA_REC = re.compile(r"\b(?:se\s+)?rechaza(?:n)?\b[^.;]{0,40}\b(?:recurso|queja)\b", re.I)
RE_REMAND = re.compile(r"vuelvan?\s+los\s+autos|dicte\s+(?:un\s+)?nuev[ao]|nuevo\s+(?:pronunciamiento|fallo|sentencia)", re.I)
RE_COMPET = re.compile(r"\bresulta\s+competente\b|\bdeclara\s+(?:la\s+)?(?:in)?competencia\b|\bdeber[áa]\s+entender\b|\bdeclara\s+competente\b", re.I)
RE_DEMANDA = re.compile(r"\b(?:hac\w+\s+lugar|rechaz\w+|admit\w+|desestim\w+)\b[^.;]{0,30}\b(?:demanda|acci[oó]n|pretensi[oó]n)\b", re.I)
RE_PROCESAL = re.compile(r"\bcaducidad\b|\breposici[oó]n\b|\baclaratoria\b|\bhonorarios\b|\bcitaci[oó]n\b|\bterceros?\b|"
                         r"\bsuspensi[oó]n\b|\brecusaci[oó]n\b|\bexcusaci[oó]n\b|\bcautelar\b|\bbeneficio\s+de\s+litigar\b|"
                         r"\bintimaci[oó]n\b|\bavocaci[oó]n\b|mal\s+(?:denegad|concedid)|\bexcepci[oó]n\b|\bdefecto\s+legal\b|"
                         r"\bfalta\s+de\s+legitimaci[oó]n\b", re.I)
RE_HEADER = re.compile(r"(?:DE\s+JUSTICIA\s+DE\s+LA\s+NACI[OÓ]N|FALLOS\s+DE\s+LA\s+CORTE)\s*\d*\s*$", re.I)
RE_GRANT = re.compile(r"hace\s+lugar|procedente", re.I)

def disposicion(pe):
    pe = norm(pe)
    enc = [lab for lab,pat in DISP if pat.search(pe)]
    remand = bool(RE_REMAND.search(pe))
    if enc: return enc[0], len(set(enc)), remand
    if RE_RECHAZA_REC.search(pe): return "confirma", 1, remand
    if RE_COMPET.search(pe):  return "no_revision_competencia", 0, remand
    if RE_DEMANDA.search(pe): return "no_revision_demanda", 0, remand
    if RE_PROCESAL.search(pe): return "no_revision_procesal", 0, remand
    if RE_HEADER.search(pe):  return "por_ello_cortado", 0, remand
    if RE_GRANT.search(pe) and remand: return "grant_remand_implicito", 0, remand
    return "sin_disposicion_legible", 0, remand

df = pd.read_csv("/mnt/user-data/uploads/csjn_casos.csv", dtype=str, keep_default_na=False)
t  = pd.read_csv("/mnt/user-data/uploads/csjn_casos_textos.csv", dtype=str, keep_default_na=False)[["caso_id_canonico","por_ello_text"]]
f = df[(df.tipo_entrada=="fallo") & (df.is_merit_decision=="1")].merge(t, on="caso_id_canonico", how="left")
r = f.por_ello_text.map(disposicion)
f["disp"]=r.map(lambda x:x[0]); f["n_disp"]=r.map(lambda x:x[1])
DISPVALS={"revoca","deja_sin_efecto","confirma","nulidad","modifica"}
print("Universo is_merit=1:", len(f), "\n=== v3 ===")
for k,v in f.disp.value_counts().items(): print(f"  {k:<28} {v:>5} ({100*v/len(f):.1f}%)")
es=f.disp.isin(DISPVALS); norev=f.disp.str.startswith("no_revision")
univ_rev = len(f)-norev.sum()-(f.disp=='por_ello_cortado').sum()
print(f"\n  disposición leída: {es.sum()}   no-revisión ruteado: {norev.sum()}   cortado(bug): {(f.disp=='por_ello_cortado').sum()}")
print(f"  grant_remand_implícito (vacate implícito?): {(f.disp=='grant_remand_implicito').sum()}")
print(f"  residual duro: {(f.disp=='sin_disposicion_legible').sum()}")
print(f"\n>>> COBERTURA universo revisión: {es.sum()}/{univ_rev} = {100*es.sum()/univ_rev:.1f}%  (v1 obj-bound 84%, ahora con plural)")
f.to_csv("H118_poc/disp_poc_v3.csv", index=False)
