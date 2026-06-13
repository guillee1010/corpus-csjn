#!/usr/bin/env python3
"""PoC H118 — extractor de disposición paso-3 (qué le hace la Corte a la sentencia
de abajo), leyendo el por_ello como cadena ritual. DIAGNÓSTICO, no toca el parser.
Universo: is_merit_decision=1. Mide redistribución vs outcome y % no legible."""
import pandas as pd, csv, re, sys
csv.field_size_limit(10**7)

def _unhyphen(s): return re.sub(r"­","", s or "").replace("- ", "").replace("-\n","")
def norm(s):
    s = re.sub(r"­","", s or "")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)   # de-hifenar OCR (alcan­ ce -> alcance)
    return re.sub(r"\s+"," ", s).strip()

# objeto = la sentencia de abajo (lo que la Corte revisa)
OBJ = r"(?:la\s+sentencia|el\s+pronunciamiento|la\s+resoluci[oó]n|el\s+fallo|lo\s+resuelto|el\s+decisorio|la\s+decisi[oó]n|el\s+auto|la\s+resoluci[oó]n\s+recurrida)"
W = r"[^.;]{0,55}"   # ventana verbo->objeto, sin cruzar fin de cláusula

# disposiciones (verbo ATADO al objeto sentencia)
DISP = [
    ("revoca",          re.compile(rf"\b(?:se\s+)?revoca(?:n)?\b{W}{OBJ}|\brevocar\b{W}{OBJ}", re.I)),
    ("deja_sin_efecto", re.compile(rf"\bdeja(?:r|se|n)?\s+sin\s+efecto\b{W}{OBJ}|"
                                   rf"\b(?:se\s+)?dej[óo]\s+sin\s+efecto\b{W}{OBJ}", re.I)),
    ("nulidad",         re.compile(rf"\b(?:se\s+)?declara\s+(?:la\s+)?nul[ao]\b|\bnulidad\b{W}{OBJ}|"
                                   rf"\b(?:se\s+)?anula\b{W}{OBJ}", re.I)),
    ("confirma",        re.compile(rf"\b(?:se\s+)?confirma(?:n)?\b{W}{OBJ}|\bconfirmar\b{W}{OBJ}", re.I)),
    ("modifica",        re.compile(rf"\b(?:se\s+)?modifica(?:n)?\b{W}{OBJ}", re.I)),
]
# rechaza el recurso = se mantiene la de abajo = affirm (objeto = recurso, no sentencia)
RE_RECHAZA_REC = re.compile(r"\b(?:se\s+)?rechaza(?:n)?\b[^.;]{0,40}\b(?:recurso|queja)\b", re.I)
# remand
RE_REENVIA = re.compile(r"vuelvan?\s+los\s+autos|rem[íi]tan?se|devu[ée]lvanse\s+los\s+autos|"
                        r"nuevo\s+(?:pronunciamiento|fallo|sentencia)|dicte\s+(?:un\s+)?nuev[ao]", re.I)
# fallback: verbo de disposición SUELTO (sin objeto) -> baja confianza
DISP_SUELTO = [
    ("revoca", re.compile(r"\b(?:se\s+)?revoca\b|\brevocar\b", re.I)),
    ("deja_sin_efecto", re.compile(r"\bdeja(?:r|se|n)?\s+sin\s+efecto\b", re.I)),
    ("confirma", re.compile(r"\b(?:se\s+)?confirma\b|\bconfirmar\b", re.I)),
    ("nulidad", re.compile(r"\bnulidad\b|\b(?:se\s+)?anula\b", re.I)),
]

def disposicion(pe):
    pe = norm(pe)
    encontrados = [lab for lab,pat in DISP if pat.search(pe)]
    remand = bool(RE_REENVIA.search(pe))
    if encontrados:
        # multi -> cola parte×recurso; reportamos set + dominante (primero de la cascada)
        return encontrados[0], len(set(encontrados)), remand, "objeto"
    if RE_RECHAZA_REC.search(pe):
        return "confirma", 1, remand, "rechaza_recurso"
    sueltos = [lab for lab,pat in DISP_SUELTO if pat.search(pe)]
    if sueltos:
        return sueltos[0], len(set(sueltos)), remand, "suelto_baja_conf"
    return "sin_disposicion_legible", 0, remand, "none"

df = pd.read_csv("/mnt/user-data/uploads/csjn_casos.csv", dtype=str, keep_default_na=False)
t  = pd.read_csv("/mnt/user-data/uploads/csjn_casos_textos.csv", dtype=str, keep_default_na=False)[["caso_id_canonico","por_ello_text"]]
f = df[(df.tipo_entrada=="fallo") & (df.is_merit_decision=="1")].merge(t, on="caso_id_canonico", how="left")
print("Universo fondo (is_merit=1):", len(f))

res = f.por_ello_text.map(disposicion)
f["disp"]   = res.map(lambda x: x[0])
f["n_disp"] = res.map(lambda x: x[1])
f["remand"] = res.map(lambda x: x[2])
f["via"]    = res.map(lambda x: x[3])

print("\n=== disposición nueva (paso-3) ===")
for k,v in f.disp.value_counts().items(): print(f"  {k:<26} {v:>5}  ({100*v/len(f):.1f}%)")
print(f"\n  con reenvío (remand):        {f.remand.sum()}")
print(f"  multi-disposición (cola ×parte): {(f.n_disp>=2).sum()}")
print("\n  fuente del match:")
for k,v in f.via.value_counts().items(): print(f"    {k:<18} {v:>5}")

print("\n=== REDISTRIBUCIÓN  outcome(viejo) -> disposicion(nueva) ===")
print(pd.crosstab(f.outcome, f.disp).to_string())

# tasa de rotura
rotos = (f.disp=="sin_disposicion_legible")
print(f"\n>>> ROTURA: sin_disposicion_legible = {rotos.sum()} / {len(f)}  ({100*rotos.mean():.1f}%)")
f.to_csv("/home/claude/H118_poc/disp_poc.csv", index=False)
