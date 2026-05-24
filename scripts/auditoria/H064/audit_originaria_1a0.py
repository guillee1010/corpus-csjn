# audit_originaria_1a0.py — Verificar si los 1->0 perdieron la keyword o no
import csv, sys, re
sys.path.insert(0, "scripts/pipeline")
from parser import RE_COMPETENCIA_ORIGINARIA, RE_ART_117_CN, RE_FORMA_ORIGINARIA, RE_CN_ORIGINARIO

PRE = "output/parser/csjn_casos_pre_b010.csv"
POST = "output/parser/csjn_casos.csv"

pre_rows = {r["caso_id_canonico"]: r for r in csv.DictReader(open(PRE, encoding="utf-8"))}
post_rows = {r["caso_id_canonico"]: r for r in csv.DictReader(open(POST, encoding="utf-8"))}

# Encontrar casos 1->0
casos_1a0 = []
for k in post_rows:
    pre_orig = pre_rows.get(k, {}).get("is_originaria", "")
    post_orig = post_rows[k].get("is_originaria", "")
    if pre_orig == "1" and post_orig == "0":
        casos_1a0.append(k)

print(f"Casos is_originaria 1->0: {len(casos_1a0)}")
print()

# Para cada caso, buscar si la keyword sigue en el POST considerando+por_ello
bug_potencial = []
mejora_legit = []

for k in sorted(casos_1a0):
    pre_r = pre_rows[k]
    post_r = post_rows[k]

    pre_cons = pre_r.get("considerando_text", "") or ""
    post_cons = post_r.get("considerando_text", "") or ""
    por_ello = post_r.get("por_ello_text", "") or ""

    pre_cuerpo = pre_cons + " " + (pre_r.get("por_ello_text", "") or "")
    post_cuerpo = post_cons + " " + por_ello

    # Verificar cuál regex matcheaba en PRE
    pre_match = None
    if RE_COMPETENCIA_ORIGINARIA.search(pre_cuerpo):
        pre_match = "competencia_originaria"
    elif RE_ART_117_CN.search(pre_cuerpo):
        pre_match = "art_117"
    elif RE_FORMA_ORIGINARIA.search(pre_cuerpo):
        pre_match = "forma_originaria"
    elif RE_CN_ORIGINARIO.search(pre_r.get("case_name_cuerpo", "")):
        pre_match = "case_name_originario"

    # Verificar si POST todavia tiene la keyword
    post_tiene = False
    post_match = None
    if RE_COMPETENCIA_ORIGINARIA.search(post_cuerpo):
        post_tiene = True
        post_match = "competencia_originaria"
    elif RE_ART_117_CN.search(post_cuerpo):
        post_tiene = True
        post_match = "art_117"
    elif RE_FORMA_ORIGINARIA.search(post_cuerpo):
        post_tiene = True
        post_match = "forma_originaria"
    elif RE_CN_ORIGINARIO.search(post_r.get("case_name_cuerpo", "")):
        post_tiene = True
        post_match = "case_name_originario"

    # Buscar la keyword en el texto perdido (PRE - POST)
    texto_perdido = pre_cons[:len(pre_cons) - len(post_cons)] if len(pre_cons) > len(post_cons) else ""

    if post_tiene:
        # BUG: la keyword sigue en POST pero is_originaria=0
        bug_potencial.append((k, pre_match, post_match))
    else:
        # Mejora: la keyword estaba en texto editorial/preamble que B010 excluyo
        mejora_legit.append((k, pre_match))

print(f"{'='*70}")
print(f"RESULTADO")
print(f"{'='*70}")
print(f"Mejoras legitimas (keyword en texto editorial excluido): {len(mejora_legit)}")
print(f"Bugs potenciales (keyword sigue en POST pero is_orig=0): {len(bug_potencial)}")
print()

if mejora_legit:
    print("MEJORAS LEGITIMAS:")
    for k, pm in mejora_legit:
        print(f"  {k}: keyword PRE era '{pm}'")

if bug_potencial:
    print(f"\nBUGS POTENCIALES (investigar):")
    for k, pm, postm in bug_potencial:
        print(f"  {k}: PRE match='{pm}', POST match='{postm}'")
        # Mostrar contexto
        post_r = post_rows[k]
        cuerpo = (post_r.get("considerando_text", "") or "") + " " + (post_r.get("por_ello_text", "") or "")
        # Buscar la keyword en el texto
        for pat, nombre in [(RE_COMPETENCIA_ORIGINARIA, "comp_orig"),
                            (RE_ART_117_CN, "art_117"),
                            (RE_FORMA_ORIGINARIA, "forma_orig")]:
            m = pat.search(cuerpo)
            if m:
                start = max(0, m.start() - 40)
                end = min(len(cuerpo), m.end() + 40)
                print(f"    match '{nombre}': ...{cuerpo[start:end]}...")
