#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_resuelve_sin_se.py - H130 / B124 paso 1 (auditar ANTES de tocar la regex).

Audita el UNIVERSO de openers performativos de MAYORIA SIN `se` entre los
candidatos-con-firma de la ventana del dispositivo, usando la MISMA ventana y la
MISMA deteccion de candidato que `_barrer` / `resolver_dispositivo` v19 (no una
heuristica paralela). Objetivo: cuantificar frecuencia y FORMAS REALES para
disenar `RE_PERF v2` desde el dato, y medir el impacto del flip -- cuando un
performativo-sin-`se` PRECEDE al primer performativo-con-`se` entre los
candidatos-con-firma, P v2 cambiaria el pick (= el caso 331_p1028).

NO toca nada. Read-only. Mismo scaffolding que scan_disidencia_recup.py (H129):
reconstruye el bloque desde la localizacion e importa el parser como fuente unica.

Ubicacion esperada: scripts/diagnostico/H130/audit_resuelve_sin_se.py
(parents[2]=scripts -> pipeline ; parents[3]=raiz del repo).

Buckets de openers SIN `se` (EXPLORATORIOS, NO son la regex final; sirven para
ver la distribucion real y disenar RE_PERF v2 con los anclajes/guardas correctos):
  TRIB_RESUELVE   'el Tribunal resuelve'        (sujeto-Corte explicito)
  ESTA_CORTE      'esta Corte resuelve'         (sujeto-Corte explicito)
  LA_CORTE        'la Corte resuelve'           (sujeto-Corte explicito)
  RESUELVE_UP     'RESUELVE:' mayuscula + ':'   (tomos viejos)
  RESUELVE_COLON  'resuelve:' cualquier caja    (AMPLIO; riesgo de over-match)
  OTRO_RESUELVE   'resuelve' sin ninguno de los anteriores
                  (= riesgo over-match: 'el a quo resuelve', 'la camara resuelve')

clase_perf devuelve el PRIMER bucket que matchea (orden de BUCKETS), asi cada
chunk cae en exactamente una clase. Los sujeto-Corte se chequean antes que los
amplios, y los amplios antes que OTRO, para que OTRO/COLON-sin-sujeto aislen el
universo de over-match a revisar.

Uso:
  python audit_resuelve_sin_se.py
  python audit_resuelve_sin_se.py --max-muestras 20 --max-flips 40
"""
import sys
import re
import csv
import argparse
import pathlib
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
REPO = HERE.parents[3]
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402

csv.field_size_limit(2**31 - 1)  # Windows: C long 32-bit, sys.maxsize desborda

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}

# Performativo CON `se` = RE_PERF v1 (H129, clitico opcional). Para clasificar la
# clase de cada candidato-con-firma. Identico al de scan_disidencia_recup.py.
RE_PERF_V1 = re.compile(
    r"\bse\s+(?:(?:lo|la|los|las|le|les)\s+)?"
    r"(resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
    r"hace[n]?\s+lugar|deja[n]?\s+sin\s+efecto|rechaza[n]?|desestima[n]?|"
    r"tiene[n]?\s+por|admite[n]?|anula[n]?|hace\s+saber|intima)\b",
    re.IGNORECASE)

# Buckets SIN `se` (exploratorios). RESUELVE_UP es case-sensitive a proposito.
BUCKETS = [
    ("TRIB_RESUELVE",  re.compile(r"\bel\s+tribunal\s+resuelve\b", re.I)),
    ("ESTA_CORTE",     re.compile(r"\besta\s+corte\s+resuelve\b", re.I)),
    ("LA_CORTE",       re.compile(r"\bla\s+corte\s+resuelve\b", re.I)),
    ("RESUELVE_UP",    re.compile(r"\bRESUELVE\s*:")),            # mayuscula + ':'
    ("RESUELVE_COLON", re.compile(r"\bresuelve\s*:", re.I)),      # amplio
    ("OTRO_RESUELVE",  re.compile(r"\bresuelve[n]?\b", re.I)),    # residuo
]

# Sujeto-Corte explicito (para separar over-match de instancia inferior).
RE_SUJETO_CORTE = re.compile(
    r"\b(?:el\s+tribunal|esta\s+corte|la\s+corte)\s+resuelve\b", re.I)


def chunk_de(bloque, k):
    """Chunk del candidato: hasta 6 lineas no vacias o hasta el primer '.'.
    Identico a chunk_de de scan_disidencia_recup.py (replica el chunk de _barrer
    pero SIN el skip-de-vacias-del-presupuesto de B122; suficiente para clasificar
    el opener, que esta en la(s) primera(s) linea(s))."""
    chunk, n, m = [], 0, k
    while n < 6 and m < len(bloque):
        ln = bloque[m]
        m += 1
        s = ln.strip()
        if not s:
            continue
        chunk.append(ln)
        n += 1
        if s.endswith("."):
            break
    return " ".join(chunk).strip()


def tiene_firma(bloque, k):
    return any(P.linea_es_firma_de_juez(bloque[j])
               for j in range(k + 1, min(k + 41, len(bloque))))


def es_cand(s):
    return (P._cand_estructural(s) or P._cand_t2(s)
            or P._cand_t3b(s) or P._cand_t4(s))


def reproducir_full(bloque):
    """ld (dictamen), ar (apertura_rel), ivi (inicio_votos_indiv) -- igual que
    scan_disidencia_recup.py."""
    zonas, _ = P.zonificar_bloque(bloque)
    ld = {k for k, z in enumerate(zonas) if z == "dictamen"}
    lex = {k for k, z in enumerate(zonas) if z not in ZONAS_FALLO}
    _, ar = P.detectar_apertura_en_bloque(bloque)
    _, _, ivi, _ = P.detectar_votos_disidencias(bloque, lex)
    return ld, ar, ivi


def ventana(bloque, ar, ld, ivi):
    """Misma ventana base que resolver_dispositivo (Tier 1): inicio por cascada
    apertura -> dictamen_end+1 -> 0 ; techo en ivi si esta despues de apertura."""
    de = max(ld) if ld else None
    inicio = ar if ar is not None else (de + 1 if de is not None else 0)
    fin = ivi if (ivi is not None and (ar is None or ivi > ar)) else len(bloque)
    return inicio, fin


def clase_perf(txt):
    """('se', None) | ('sin_se', bucket) | ('no_perf', None)."""
    if RE_PERF_V1.search(txt):
        return "se", None
    for nombre, rx in BUCKETS:
        if rx.search(txt):
            return "sin_se", nombre
    return "no_perf", None


def _norm(s, n=120):
    return " ".join(str(s or "").split())[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos",  default=str(REPO / "output" / "parser" / "csjn_casos.csv"))
    ap.add_argument("--corpus", default=str(REPO / "corpus"))
    ap.add_argument("--max-muestras", type=int, default=12)
    ap.add_argument("--max-flips",    type=int, default=30)
    args = ap.parse_args()

    corpus = pathlib.Path(args.corpus)
    cache = {}

    def lines_de(sf):
        if sf not in cache:
            p = pathlib.Path(sf)
            if not p.is_absolute():
                p = corpus / sf
            cache[sf] = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
        return cache[sf]

    with open(args.casos, encoding="utf-8") as f:
        casos = list(csv.DictReader(f))

    n_ok = 0
    clase_count   = Counter()             # 'se' / 'sin_se' / 'no_perf'
    bucket_count  = Counter()             # forma sin_se
    bucket_muestras = defaultdict(list)
    flip_set = []                         # (cid, bucket, sin_txt, se_txt)
    flip_bucket = Counter()
    watch_overmatch = []                  # (cid, bucket, txt) COLON/OTRO sin sujeto-Corte

    for c in casos:
        cid = c.get("caso_id_canonico", "")
        sf  = c.get("source_file", "")
        li  = c.get("linea_inicio", "")
        lfr = c.get("linea_fin_real", "")
        lines = lines_de(sf) if sf else None
        if lines is None:
            continue
        try:
            li_i = int(li)
            lfr_i = int(lfr) if str(lfr) != "" else None
        except (ValueError, TypeError):
            continue
        bloque = P.construir_bloque_desde_localizacion(lines, li_i, lfr_i)
        if not bloque:
            continue
        n_ok += 1

        ld, ar, ivi = reproducir_full(bloque)
        inicio, fin = ventana(bloque, ar, ld, ivi)

        # Secuencia ordenada de candidatos-con-firma en la ventana (lo que compite
        # en el pick de _barrer). Excluye dictamen como los tiers base.
        seq = []  # (k, clase, bucket, txt)
        for k in range(inicio, fin):
            if k in ld:
                continue
            s = bloque[k].strip()
            if not s or not es_cand(s):
                continue
            if not tiene_firma(bloque, k):
                continue
            txt = chunk_de(bloque, k)
            cl, bk = clase_perf(txt)
            seq.append((k, cl, bk, txt))
            clase_count[cl] += 1
            if cl == "sin_se":
                bucket_count[bk] += 1
                if len(bucket_muestras[bk]) < args.max_muestras:
                    bucket_muestras[bk].append((cid, _norm(txt)))
                if (bk in ("RESUELVE_COLON", "OTRO_RESUELVE")
                        and not RE_SUJETO_CORTE.search(txt)
                        and len(watch_overmatch) < args.max_muestras):
                    watch_overmatch.append((cid, bk, _norm(txt)))

        # Flip: primer sin_se ANTES del primer se entre los candidatos-con-firma.
        idx_se  = next((i for i, t in enumerate(seq) if t[1] == "se"), None)
        idx_sin = next((i for i, t in enumerate(seq) if t[1] == "sin_se"), None)
        if idx_sin is not None and (idx_se is None or idx_sin < idx_se):
            bk = seq[idx_sin][2]
            flip_bucket[bk] += 1
            se_txt = seq[idx_se][3] if idx_se is not None else "(sin se-perf posterior)"
            if len(flip_set) < 10000:
                flip_set.append((cid, bk, _norm(seq[idx_sin][3]), _norm(se_txt)))

    # ────────────────────────── reporte ──────────────────────────
    print("=" * 98)
    print(f"AUDIT 'resuelve sin se' . H130/B124 paso 1 . parser v{P.__version__}")
    print("=" * 98)
    print(f"casos reconstruidos: {n_ok}")
    tot = sum(clase_count.values()) or 1
    print(f"\ncandidatos-con-firma en la ventana del dispositivo: {tot}")
    for cl in ("se", "sin_se", "no_perf"):
        print(f"    {cl:<8} {clase_count[cl]:>6}  ({100*clase_count[cl]/tot:.1f}%)")

    print(f"\nFORMAS performativas SIN `se` (frecuencia entre candidatos-con-firma):")
    for nombre, _ in BUCKETS:
        if bucket_count[nombre]:
            print(f"    {nombre:<16} {bucket_count[nombre]:>6}")

    print(f"\n{'='*98}")
    print(f"FLIP SET: un sin-`se` PRECEDE al primer `se`-perf => P v2 cambiaria el pick")
    print(f"  total flips: {sum(flip_bucket.values())}")
    for nombre, _ in BUCKETS:
        if flip_bucket[nombre]:
            print(f"    por {nombre:<16} {flip_bucket[nombre]:>6}")
    print(f"\n  muestras (would-be pick [WB] vs pick actual P-v1 [SE]):")
    for cid, bk, sin_txt, se_txt in flip_set[:args.max_flips]:
        print(f"  -- {cid}  [{bk}]")
        print(f"     WB: {sin_txt}")
        print(f"     SE: {se_txt}")

    print(f"\n{'='*98}")
    print(f"WATCH over-match (COLON/OTRO sin sujeto-Corte = posibles instancias inferiores):")
    if not watch_overmatch:
        print("   (ninguno) -- los `resuelve` sin sujeto-Corte no aparecen en la ventana")
    for cid, bk, txt in watch_overmatch:
        print(f"   {cid}  [{bk}]  {txt}")

    print(f"\n{'='*98}")
    print("MUESTRAS por bucket (para disenar RE_PERF v2 desde el texto real):")
    for nombre, _ in BUCKETS:
        if bucket_muestras[nombre]:
            print(f"\n  [{nombre}] (n={bucket_count[nombre]})")
            for cid, txt in bucket_muestras[nombre]:
                print(f"     {cid}  {txt}")


if __name__ == "__main__":
    main()
