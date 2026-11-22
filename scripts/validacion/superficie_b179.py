"""superficie_b179.py (H224) — superficie de B179 sobre considerando_text y por_ello_text.

Solo lectura. Fórmulas de la constancia H222 de B179 (DEUDA). Texto des-guionado (U+00AD y guion de
corte) y con espacios colapsados antes de buscar (lección B171/H220). Para cada match: juez(es) de
`posiciones` nombrados en una ventana de 120 caracteres antes del match, su posición publicada y si
tienen texto_voto en votos.csv (mitigación del FP 'remisión dentro de voto separado no detectado').
Salida: output/validacion/superficie_b179.csv (un renglón por match). Adjudicación leída: output/validacion/adjudicacion_b179_h224.csv.
Es un PISO: hay fórmulas sin cubrir (p. ej. "al que se remiten", 343_p1923). Uso: python scripts/validacion/superficie_b179.py
"""
__version__ = "0.6"  # H224: v0.1 fórmulas H222 · 0.2 +F7-F9 · 0.3 +F10 · 0.4 F3 anclada en por_ello · 0.5 respectiva(s) · 0.6 corte de renglón aplanado
import csv, json, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path
csv.field_size_limit(2**31 - 1)
RAIZ = Path(__file__).resolve().parents[2]
P = RAIZ / "output" / "parser"
OUT = RAIZ / "output" / "validacion" / "superficie_b179.csv"

def norm(t):
    t = t or ""
    t = re.sub(r"\xad\s*", "", t)
    t = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", t)
    t = re.sub(r"([a-záéíóúñ])- ([a-záéíóúñ])", r"\1\2", t)  # v0.6: corte de renglón ya aplanado ("disiden- cias")
    return re.sub(r"\s+", " ", t)

V = r"(?:votos?|disidencias?)"
PAT = {
    "F1_se_remite": re.compile(r"\bse\s+remite\s+a\s+su\s+(?:respectiv[oa]\s+)?(?:voto|disidencia)", re.I),
    "F2_se_remiten": re.compile(r"\bse\s+remiten\s+a\s+sus\s+(?:respectiv[oa]s?\s+)?" + V, re.I),
    "F3_por_mayoria": re.compile(r"\bpor\s+mayor[ií]a\b|\bla\s+mayor[ií]a\s+del\s+Tribunal\b", re.I),
    "F5_jueces_consideran": re.compile(r"\b[Ll]os\s+(?:[Ss]e[ñn]ores\s+)?(?:[Jj]ueces|[Mm]inistros|[Jj]uezas)\s+[A-ZÁÉÍÓÚ][^.;:]{2,120}?\s+(?:consideran|entienden|estiman)\b"),
    "F7_remiten_sin_se": re.compile(r"(?<!se )\b(?:remite|remiten)\s+a\s+(?:su|sus)\s+(?:respectiv[oa]s?\s+)?(?:votos?|disidencias?)", re.I),
    "F8_a_juicio_de": re.compile(r"\ba\s+juicio\s+de\s+(?:los|las|la|el)\s+(?:se[ñn]ores\s+)?(?:jueces|juezas|jueza|juez|ministros?)\s+[A-ZÁÉÍÓÚ]"),
    "F9_por_su_parte": re.compile(r"\b(?:El|La)\s+(?:se[ñn]ora?\s+)?(?:juez|jueza|conjuez|conjueza)\s+[^.;]{2,60}?,?\s+por\s+su\s+parte,?\s+(?:estima|considera|entiende|remite|sostiene)", re.I),
    "F10_mayoria_absoluta": re.compile(r"\bmayor[ií]a\s+absoluta\s+de\s+(?:los\s+)?(?:votos|opiniones|miembros)|\bescindir\s+(?:el\s+conjunto\s+decisorio|las\s+cuestiones)|\bvotos?\s+concordantes", re.I),
    "F6_deja_a_salvo": re.compile(r"\bdeja[n]?\s+a\s+salvo\s+su[s]?\s+(?:opini[oó]n|criterio|posici[oó]n)", re.I),
}

def sinac(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

def main():
    casos = {}
    for c in csv.DictReader((P / "csjn_casos.csv").open(encoding="utf-8", newline="")):
        if c["tipo_entrada"] == "fallo":
            casos[c["caso_id_canonico"]] = c
    tv = defaultdict(dict)
    for v in csv.DictReader((P / "csjn_casos_votos.csv").open(encoding="utf-8", newline="")):
        tv[v["caso_id_canonico"]][v["juez"]] = int(v["wc_voto"] or 0)
    filas = []; n_txt = 0
    for t in csv.DictReader((P / "csjn_casos_textos.csv").open(encoding="utf-8", newline="")):
        cid = t["caso_id_canonico"]
        if cid not in casos: continue
        n_txt += 1
        pos = json.loads(casos[cid]["posiciones"] or "{}")
        for campo in ("considerando_text", "por_ello_text"):
            x = norm(t[campo])
            for nom, rx in PAT.items():
                if nom == "F3_por_mayoria" and campo != "por_ello_text": continue  # v0.6: F3 anclada en por_ello (mitigación H222)
                for m in rx.finditer(x):
                    ven = sinac(x[max(0, m.start() - 120): m.end()])
                    nombrados = [j for j in pos if sinac(j.split()[-1]) in ven]
                    filas.append({
                        "caso_id_canonico": cid, "campo": campo, "formula": nom,
                        "match": m.group(0), "voting_pattern": casos[cid]["voting_pattern"],
                        "jueces_nombrados": " | ".join(nombrados),
                        "posicion_publicada": " | ".join(pos[j] for j in nombrados),
                        "wc_voto_nombrados": " | ".join(str(tv[cid].get(j, "")) for j in nombrados),
                        "contexto": x[max(0, m.start() - 220): m.end() + 120],
                    })
    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    print(f"superficie_b179 v{__version__} · fallos con textos {n_txt}/{len(casos)} · matches {len(filas)}")
    por = defaultdict(set)
    for f in filas: por[f["formula"]].add(f["caso_id_canonico"])
    for k in PAT: print(f"  {k:22s} fallos {len(por[k]):4d} · matches {sum(1 for f in filas if f['formula']==k)}")
    u = set().union(*por.values()); print(f"  unión fallos {len(u)}")
    for tst in ("341_p961", "341_p1063", "343_p536", "343_p1923", "342_p287"):
        print(f"  testigo {tst}: {sorted({f['formula'] for f in filas if f['caso_id_canonico']==tst})}")
    print(f"Archivo: {OUT.relative_to(RAIZ)}")

if __name__ == "__main__":
    main()
