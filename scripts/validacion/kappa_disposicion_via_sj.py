"""kappa_disposicion_via_sj.py — κ de disposición y vía: corpus vs sjconsulta (M66, H224)

Segundo codificador externo para los ejes de recursos (`csjn_casos_recursos.csv`): el `sentido` y el
`tipo_recurso` que carga la Secretaría de Jurisprudencia. Lee `casos_sjconsulta.csv` (salida de
`scripts/analisis/unir_sjconsulta.py`, cache local; SIN datos de funcionarios) y los canónicos (solo
lectura). Las tablas de equivalencia de abajo son DECISIÓN DEL OPERADOR (propuesta H224): una etiqueta
de SJ que no figura en la tabla deja el par fuera del cálculo y se informa.

Uso:
  python scripts/validacion/kappa_disposicion_via_sj.py [--sj RUTA] [--boot 2000]
Escribe output/validacion/kappa_disposicion_via_sj.csv (κ, IC 95% bootstrap, n) y
output/validacion/kappa_disposicion_via_sj_matriz.csv (matriz de confusión por eje).
"""
__version__ = "0.1"  # H224
import argparse, csv, random
from collections import Counter
from pathlib import Path
csv.field_size_limit(2**31 - 1)
RAIZ = Path(__file__).resolve().parents[2]

# --- equivalencias (propuesta H224; cambiar acá y re-correr) ---
DISP_CORPUS = {
    "deja_sin_efecto": "deja_sin_efecto", "grant_remand_implicito": "deja_sin_efecto",
    "revoca": "revoca", "modifica": "revoca",
    "confirma": "confirma",
    "no_revision_competencia": "competencia",
    "nulidad": "nulidad", "nulidad_concesion": "nulidad",
    "no_fondo": "sin_revision", "no_revision_procesal": "sin_revision",
    "no_revision_demanda": "demanda",
}
DISP_SJ = {
    "DEJA SIN EFECTO": "deja_sin_efecto",
    "REVOCA": "revoca", "REVOCA PARCIALMENTE": "revoca", "MODIFICA": "revoca",
    "CONFIRMA": "confirma", "CONFIRMA PARCIALMENTE": "confirma",
    "DECLARA COMPETENCIA": "competencia", "DECLARA INCOMPETENCIA": "competencia",
    "DECLARA NULIDAD": "nulidad",
    "DESESTIMA": "sin_revision", "RECHAZA": "sin_revision", "DECLARA INADMISIBLE": "sin_revision",
    "DECLARA MAL CONCEDIDO": "sin_revision", "DECLARA INOFICIOSO": "sin_revision",
    "DECLARA ABSTRACTA LA CUESTION": "sin_revision", "DECLARA CADUCIDAD": "sin_revision",
    "DECLARA DESIERTO": "sin_revision", "RECHAZA MEDIDA CAUTELAR": "sin_revision",
    "DECLARA IMPROCEDENTE": "sin_revision",
    "HACE LUGAR A  LA DEMANDA": "demanda", "HACE LUGAR A LA DEMANDA": "demanda",
    "HACE LUGAR PARCIALMENTE A LA DEMANDA": "demanda", "RECHAZA LA DEMANDA": "demanda",
}
VIA_CORPUS = {"recurso_extraordinario": "extraordinario", "recurso_ordinario": "ordinario", "": "otra_o_ninguna"}
VIA_SJ = {
    "RECURSO EXTRAORDINARIO FEDERAL": "extraordinario", "RECURSO DE QUEJA": "extraordinario",
    "RECURSO EXTRAORDINARIO POR SALTO DE INSTANCIA": "extraordinario",
    "RECURSO ORDINARIO DE APELACION": "ordinario",
    "RECURSO DE REVOCATORIA": "otra_o_ninguna", "RECURSO DE ACLARATORIA": "otra_o_ninguna",
    "RECURSO DE NULIDAD": "otra_o_ninguna",
}

def kappa(pares):
    n = len(pares)
    if not n: return None, 0
    po = sum(a == b for a, b in pares) / n
    ca, cb = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return ((po - pe) / (1 - pe) if pe < 1 else 1.0), po

def ic(pares, boot, seed=224):
    rnd = random.Random(seed); ks = []
    for _ in range(boot):
        k, _ = kappa([pares[rnd.randrange(len(pares))] for _ in pares]); ks.append(k)
    ks.sort(); return ks[int(0.025 * boot)], ks[int(0.975 * boot) - 1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sj", default=str(RAIZ / "scripts/diagnostico/sjconsulta/casos_sjconsulta.csv"))
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    SJ = {r["caso_id_canonico"]: r for r in csv.DictReader(open(a.sj, encoding="utf-8"))}
    fallo = {c["caso_id_canonico"] for c in csv.DictReader((RAIZ / "output/parser/csjn_casos.csv").open(encoding="utf-8", newline="")) if c["tipo_entrada"] == "fallo"}
    rec = {r["caso_id_canonico"]: r for r in csv.DictReader((RAIZ / "output/parser/csjn_casos_recursos.csv").open(encoding="utf-8", newline=""))}
    ks = sorted(k for k in SJ if k in fallo and SJ[k].get("fallos_sj_misma_pagina", "1") == "1")
    ejes = {}
    # disposición
    P, fuera = [], Counter()
    for k in ks:
        s = SJ[k]["sentido"].strip()
        if not s: continue
        if s not in DISP_SJ: fuera[s] += 1; continue
        P.append((DISP_CORPUS[rec[k]["disposicion"]], DISP_SJ[s]))
    ejes["disposicion"] = (P, fuera)
    # vía (3 clases) y queja (binario)
    P, Q, fuera = [], [], Counter()
    for k in ks:
        t = SJ[k]["tipo_recurso"].strip()
        if not t: continue
        if t not in VIA_SJ: fuera[t] += 1; continue
        P.append((VIA_CORPUS[rec[k]["via_recurso"]], VIA_SJ[t]))
        Q.append((rec[k]["es_queja"] == "1", t == "RECURSO DE QUEJA"))
    ejes["via_recurso"] = (P, fuera); ejes["es_queja"] = (Q, Counter())
    filas, mat = [], []
    print(f"kappa_disposicion_via_sj v{__version__} · pares corpus×SJ (fallo, una sola entrada SJ por página) {len(ks)}")
    for eje, (P, fuera) in ejes.items():
        k, po = kappa(P); lo, hi = ic(P, a.boot)
        print(f"  {eje:12s} n {len(P):5d} · acuerdo {po*100:5.1f}% · κ {k:.3f} [{lo:.3f}; {hi:.3f}]" + (f" · fuera de tabla {sum(fuera.values())}: {dict(fuera.most_common(5))}" if fuera else ""))
        filas.append({"eje": eje, "n": len(P), "acuerdo": round(po, 4), "kappa": round(k, 4), "ic95_inf": round(lo, 4), "ic95_sup": round(hi, 4), "fuera_de_tabla": sum(fuera.values())})
        for (x, y), v in Counter(P).items(): mat.append({"eje": eje, "corpus": x, "sj": y, "n": v})
    out = RAIZ / "output/validacion"
    with (out / "kappa_disposicion_via_sj.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]), lineterminator="\n"); w.writeheader(); w.writerows(filas)
    with (out / "kappa_disposicion_via_sj_matriz.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["eje", "corpus", "sj", "n"], lineterminator="\n"); w.writeheader()
        w.writerows(sorted(mat, key=lambda r: (r["eje"], -r["n"])))

if __name__ == "__main__":
    main()
