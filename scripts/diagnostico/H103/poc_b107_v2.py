import csv, re
import parser as P

# B107.1 ESCOPADO: solo "hacer/se hace lugar a la excepcion de incompetencia"
RE_LUGAR_EXCEP_INCOMP = re.compile(
    r"\b(?:se\s+hace|hacer)\s+lugar\s+a\s+la\s+excepci[oó]n\s+de\s+incompetencia\b", re.I)
RE_NEG_HACER_LUGAR = re.compile(
    r"\bno\s+(?:se\s+)?(?:corresponde\s+)?(?:hacer?|ha|hace|hacen)\s+lugar\b", re.I)
NO_FB = {"hace_lugar","procedente","revoca","confirma","rechaza","nulidad",
         "competencia","abstracto","originaria","desistimiento","deja_sin_efecto"}

def norm(t): return re.sub(r"\s+", " ", P._unhyphenate(t)).strip()

def classify_new(por_ello_text, considerando_text=""):
    por = norm(por_ello_text); cons = norm(considerando_text)
    if not por:
        base = "sin_dispositivo"
    else:
        if RE_LUGAR_EXCEP_INCOMP.search(por):
            return "competencia"
        hubo_neg = bool(RE_NEG_HACER_LUGAR.search(por))
        texto = RE_NEG_HACER_LUGAR.sub(" ", por) if hubo_neg else por
        outcome_disp = "otro"
        for label, pat in P.OUTCOME_PATTERNS_DISPOSITIVO:
            if pat.search(texto): outcome_disp = label; break
        if hubo_neg and outcome_disp == "otro":
            base = "rechaza"            # base DEBIL: el considerando 280/ac4 aun puede ganar
        elif outcome_disp in NO_FB:
            return outcome_disp
        else:
            base = outcome_disp
    if cons:
        if P.RE_280_CONSIDERANDO.search(cons) or P.RE_280_LIBRE.search(cons):
            return "inadmisible_280"
        if (P.RE_ACORDADA_4_CONSIDERANDO.search(cons) or
            P.RE_ACORDADA_4_REGLAMENTO.search(cons) or P.RE_ACORDADA_4_DIRECTA.search(cons)):
            return "inadmisible_acordada_4"
    return base

rows = list(csv.DictReader(open("/mnt/user-data/uploads/csjn_casos.csv", encoding="utf-8")))
diffs = [(r["caso_id_canonico"], P.classify_outcome(r["por_ello_text"], r["considerando_text"]),
          classify_new(r["por_ello_text"], r["considerando_text"]))
         for r in rows]
diffs = [(c,o,n) for c,o,n in diffs if o != n]
from collections import Counter
print("A/B v2: %d celdas cambian" % len(diffs))
print("transiciones:", dict(Counter((o,n) for _,o,n in diffs)))
no_hl = [(c,o,n) for c,o,n in diffs if o != "hace_lugar"]
print("\nCAMBIOS QUE NO SALEN DE hace_lugar (colateral a vetar): %d" % len(no_hl))
for c,o,n in sorted(no_hl):
    r = next(x for x in rows if x["caso_id_canonico"]==c)
    print("  %-12s %s->%s :: %s" % (c,o,n, r["por_ello_text"][:110].replace("\n"," ")))

# fidelidad real: solo fallos, solo donde classify reproduce/no
fallos = [r for r in rows if r["tipo_entrada"]=="fallo"]
mism = [r for r in fallos if P.classify_outcome(r["por_ello_text"], r["considerando_text"]) != r["outcome"]]
print("\nFIDELIDAD sobre fallos: %d/%d mismatch classify_outcome vs columna" % (len(mism), len(fallos)))
print("  (clave: el outcome guardado pasa por procesar_archivo, NO solo classify_outcome)")

print("\n\n===== VERIFICACION DIRIGIDA =====")
TARGETS_NEG = ["329_p838","329_p1035","329_p1399","329_p1834","329_p2316","329_p2860",
"329_p2874","329_p2944","329_p3109","329_p5175","329_p5578","329_p5745","330_p778",
"330_p2064","330_p4389","330_p4824","330_p4960","331_p1500","339_p633","341_p726",
"341_p2010","343_p748","344_p21","344_p48","348_p61"]
TARGETS_INC = ["329_p53","329_p783","329_p1875","330_p3899"]
byid = {r["caso_id_canonico"]: r for r in rows}
def cn(c): return classify_new(byid[c]["por_ello_text"], byid[c]["considerando_text"])
def co(c): return P.classify_outcome(byid[c]["por_ello_text"], byid[c]["considerando_text"])
sin_flip = [c for c in TARGETS_NEG if co(c)==cn(c)]
print("negacion: %d/%d flipean. SIN flipear: %s" % (len(TARGETS_NEG)-len(sin_flip), len(TARGETS_NEG), sin_flip))
for c in sin_flip:
    print("   %s sigue en %s :: %s" % (c, cn(c), byid[c]["por_ello_text"][:120].replace("\n"," ")))
print("incompetencia: todas -> competencia?", all(cn(c)=="competencia" for c in TARGETS_INC),
      "->", {c: cn(c) for c in TARGETS_INC})
print("\n329_p1399 (el otorgamiento) por_ello completo:")
print("  ", byid["329_p1399"]["por_ello_text"][:320].replace("\n"," "))
