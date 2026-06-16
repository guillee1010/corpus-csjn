#!/usr/bin/env python3
"""
clasificador_via.py — fuente ÚNICA de la vía recursiva (corpus-csjn).
=====================================================================
Paralelo a clasificador_disposicion.py. Reusa su norm() (normalizador compartido,
\xad-aware desde v1.01) para no divergir. Importado por:
  - scripts/diagnostico/H120/build_m20.py   (validación: clave cod_via_recurso)
  - scripts/pipeline/derivar_recursos.py     (producción: csjn_casos_recursos.csv)
Una sola copia de la lógica => el número validado describe lo que se shippea. Sin drift.

Diseño (validado en disco vs gold n=136):
  - Vocabulario, no umbral: la vía está en el texto, no requiere tuneo de threshold.
  - Lee dispositivo (por_ello) y, si no aparece, considerando: la vía a veces vive
    en los fundamentos, no en el dispositivo (sobre todo el ordinario).
  - Plural + des-hifenado (vía norm v1.01): 'recurso ex­ traordinario', 'recursos
    ordinarios' se capturan igual que el singular limpio.
  - PRIMACÍA DEL ORDINARIO (doctrina, Klein): cuando coexisten 'recurso ordinario de
    apelación' y 'extraordinario', gana el ordinario. Regla con fundamento, no ad-hoc.
  - multi_recurso: flag (plural o ambos tipos presentes). Marca los candidatos a
    desagregación parte×recurso (cola SCDB ~2%); NO la resuelve.

Métrica en disco (n=136 del gold, sobre por_ello+considerando): vía 0,956.
NO modificar sin re-validar contra el gold como held-out.
"""
import re
from clasificador_disposicion import norm   # normalizador compartido (\xad-aware v1.01)

__version__ = "0.1"

RE_ORD_AP = re.compile(r"recursos?\s+ordinarios?\s+de\s+apelaci[oó]n", re.I)  # frase canónica
RE_EXT    = re.compile(r"recursos?\s+extraordinarios?", re.I)
RE_ORD    = re.compile(r"recursos?\s+ordinarios?", re.I)
RE_PLURAL = re.compile(r"recursos\s+(?:extra)?ordinarios", re.I)


def via_recurso(por_ello, considerando=""):
    """(via, multi) a partir del dispositivo y, en su defecto, del considerando.

    via   ∈ {'recurso_extraordinario', 'recurso_ordinario', ''}  ('' = no detectada)
    multi : bool — hay más de un recurso (plural) o ambos tipos presentes.
    """
    pe, co = norm(por_ello), norm(considerando)
    tipo = ""
    for z in (pe, co):
        if RE_ORD_AP.search(z):
            tipo = "recurso_ordinario"; break        # primacía del ordinario
        if RE_EXT.search(z):
            tipo = "recurso_extraordinario"; break
        if RE_ORD.search(z):
            tipo = "recurso_ordinario"; break
    blob = pe + " || " + co
    multi = bool(RE_PLURAL.search(blob)) or (bool(RE_EXT.search(blob)) and bool(RE_ORD.search(blob)))
    return tipo, multi
