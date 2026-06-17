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

v1.01 — norm() ahora des-hifena el soft-hyphen (\u00ad) de fin de línea del OCR
        ('re­ curso' -> 'recurso'), que antes quedaba como 're curso' y rompía el
        match del verbo dispositivo. Cambio GENERAL (no a medida del gold). Validado
        en disco vs gold: disposición 0,887 -> 0,930, 0 regresiones, 6 mejoras.
        REQUIERE regenerar la clave (build_m20) y re-sellar antes de cerrar.
"""
import re
__version__ = "1.06"

# v1.06 (H139): RE_RUNNING_HEAD case-sensitive (saca re.I), sync con parser L218.
# El banner es MAYÚSCULAS; "Corte Suprema de Justicia de la Nación" en mixta es CUERPO,
# no header. Verificado en disco: por_ello 467/467 mayúsculas → disposición byte-idéntica
# (no-op sobre el output). Habilita limpiar el banner del considerando para materia (frente aparte).
# v1.05 (M21 Fase 2 en el submódulo): banner editorial (terna 'número FALLOS… número' /
# '…NACIÓN número') enmascarado en norm(). RE_RUNNING_HEAD VERBATIM del parser (L215) —
# fuente única, no un regex paralelo (el RE_BANNER del validador es el drift que evitamos;
# dedup futuro a módulo compartido). Recupera los INTERPOLADOS (banner mid-text que parte el
# OBJ → al sacarlo se re-pega el verbo de fondo): 330_p380/330_p960 → deja_sin_efecto,
# 333_p1951 → revoca, 344_p1444 → deja_sin_efecto. Los TRUNCADOS (verbo físicamente cortado)
# NO se recuperan acá: viven en el parser (por_ello_cortado los marca legítimamente).
RE_RUNNING_HEAD = re.compile(
    r"\d{1,6}\s+(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s+\d{1,6}"
    r"|\d{1,6}\s+(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\b"
    r"|\b(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s+\d{1,6}")  # H139: sin re.I → case-sensitive

def norm(s):
    s = s or ""
    s = re.sub(r"(\w)\u00ad\s*(\w)", r"\1\2", s)   # des-hifena el soft-hyphen de fin de linea ('re­ curso' -> 'recurso')
    s = re.sub(r"\u00ad", "", s)                    # limpia soft-hyphens sueltos restantes
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)         # des-hifena el guion normal
    s = RE_RUNNING_HEAD.sub(" ", s)                 # v1.05: enmascara el banner editorial (terna) -> recupera interpolados
    return re.sub(r"\s+", " ", s).strip()

OBJ  = r"(?:la|las|el|los)\s+(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto)s?\b"
# v1.03 (B127): OBJ con plural -es ('resoluciones'/'decisiones', que 's?' no cubria).
# Aplicado SOLO en revoca/deja_sin_efecto (verbos de revocacion limpia). NO en
# nulidad/invalidez/confirma: ahi el -es arrastra FP (nulidad-de-concesion, originarias,
# 'confirmar ... en cuanto a la nulidad de las resoluciones'). Verificado en disco (5890):
# 6 flips, 0 regresiones, gold 0/300 tocado. El frente del banner (por_ello truncado) es M21, no esto.
OBJ_es = r"(?:la|las|el|los)\s+(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto)(?:es|s)?\b"
OBJX = r"(?:sentencia|pronunciamiento|resoluci[oó]n|fallo|decisorio|decisi[oó]n|auto|sanci[oó]n|pena|condena|multa)s?\b"
W = r"[^.;]{0,55}"
DISP = [
    ("revoca",  re.compile(rf"\b(?:se\s+)?revoca(?:n)?\b{W}{OBJ_es}|\brevocar\b{W}{OBJ_es}|revoc[áa]ndose{W}{OBJ_es}", re.I)),
    ("deja_sin_efecto", re.compile(
        rf"\bdeja(?:r|se|n)?\s+sin\s+efecto\b{W}{OBJ_es}|\bdej[áa]ndose\s+sin\s+efecto\b{W}?{OBJ_es}|"
        rf"\bdejando\s+sin\s+efecto\b{W}?{OBJ_es}|\bd[ée]jase\s+sin\s+efecto\b{W}?{OBJ_es}|\bdeje\s+sin\s+efecto\b{W}?{OBJ_es}", re.I)),
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
    return "no_fondo", remand   # v1.02: ex 'sin_disposicion_legible'. El por_ello es legible; no hay disposicion de FONDO (competencia/liquidacion/desercion/queja/honorarios). El gold concuerda: 88/89 vacio.

def parte_ganadora_regla(disp):
    if disp in ("revoca", "deja_sin_efecto", "nulidad", "grant_remand_implicito"): return "recurrente_gana"
    if disp == "confirma": return "recurrente_pierde"
    if disp == "modifica": return "parcial"
    return "no_aplica"
