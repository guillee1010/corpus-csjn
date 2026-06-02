#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
poc_b108.py -- A/B de B108 (competencia originaria rescatada de "otro").
Corré contra el parser PRE-B108 (v18.16) para ver los 157 flips.
Ajustá la ruta de csjn_casos.csv. Origen: M19.
"""
import csv
import parser as P  # importá el parser que querés medir

rows = list(csv.DictReader(open("output/parser/csjn_casos.csv", encoding="utf-8")))
otros = [r for r in rows if r["outcome"] == "otro"]
nuevos = [r for r in otros
          if P.classify_outcome(r["por_ello_text"], r["considerando_text"]) == "competencia"]
print("otro -> competencia con el parser importado: %d / %d otro" % (len(nuevos), len(otros)))
for r in nuevos[:20]:
    import re
    t = re.sub(r"\s+", " ", P._unhyphenate(r["por_ello_text"])).strip()
    print("  %-12s %s" % (r["caso_id_canonico"], t[:90]))
