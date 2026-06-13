#!/usr/bin/env python3
"""
clasificador_disposicion.py — fuente ÚNICA de la lógica de disposición (corpus-csjn).
=====================================================================================
Regex VERBATIM del PoC v3 (H118), congeladas. Importado por:
  - scripts/diagnostico/H120/build_m20.py   (validación: genera la clave)
  - scripts/pipeline/derivar_recursos.py     (producción: csjn_casos_recursos.csv)
Una sola copia => el 0,857 blind describe exactamente lo que se shippea. Sin drift.

Garantía: corrido sobre los mismos textos, reproduce la clave blind 300/300
(disposición, reenvía, parte_ganadora). NO modificar sin re-validar contra held-out.
"""
import re
__version__ = "1.0"

def norm(s):
    s = re.sub(r"\u00ad", "", s or "")
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)
    return re.sub(r"\s+", " ", s).strip()

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
    """(label, reenvia_bool) a partir del por_ello_text."""
    pe = norm(pe)
    enc = [lab for lab, pat in DISP if pat.search(pe)]
    remand = bool(RE_REMAND.search(pe))
    if enc: return enc[0], remand
    if RE_RECHAZA_REC.search(pe): return "confirma", remand
    if RE_COMPET.search(pe):  return "no_revision_competencia", remand
    if RE_DEMANDA.search(pe): return "no_revision_demanda", remand
    if RE_PROCESAL.search(pe): return "no_revision_procesal", remand
    if RE_HEADER.search(pe):  return "por_ello_cortado", remand
    if RE_GRANT.search(pe) and remand: return "grant_remand_implicito", remand
    return "sin_disposicion_legible", remand

def parte_ganadora_regla(disp):
    if disp in ("revoca", "deja_sin_efecto", "nulidad", "grant_remand_implicito"): return "recurrente_gana"
    if disp == "confirma": return "recurrente_pierde"
    if disp == "modifica": return "parcial"
    return "no_aplica"
