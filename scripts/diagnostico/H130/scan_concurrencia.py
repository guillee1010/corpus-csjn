#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_concurrencia.py - H130 / B124 paso 4 · check de PICK-DE-CONCURRENCIA.

El blind spot que causó el rollback v20->v19 (H129): el scan de validación
buscaba *votos perdedores* (disidencias), no *concurrencias* ("según su voto").
En 331_p1028 Argibay CONCURRE (mismo resultado) tras la mayoría, asi que el pick
de P en su dispositivo NO se flageó y el A/B contó el otro->confirma como
correccion. Este check generaliza scan_disidencia_recup.py:

  - RE_VOTO_HEAD v2 agrega los encabezados "Voto la señora/el señor ministro…"
    (forma según-su-voto / concurrencia) que el regex H129 NO matcheaba.
  - chequea TODOS los picks (no solo las recuperaciones otro->real).
  - usa el parser PARCHEADO como fuente única: el pick es P.resolver_dispositivo
    (regla P + RE_PERF v2) y la performatividad es P.RE_PERF (mismo criterio que
    el fix).

REGLA del flag (mis-pick de concurrencia): el pick de P cae DESPUES de un
encabezado de voto/disidencia separado, y EXISTE un candidato-con-firma
PERFORMATIVO (= dispositivo de mayoría) ANTES de ese encabezado. Si regla P
funciona, debería devolver esa mayoría primero -> 0 sospechosos. Cualquier hit
es un mis-pick residual a leer.

Sobre 331_p1028 (con v2): el pick ahora ES la mayoría (antes de todo encabezado)
-> NO flagea. El check confirma el fix y caza cualquier caso que quede.

NO toca nada. Read-only. Correr DESPUES de aplicar el patch v20 y re-correr el
parser. Ubicación esperada: scripts/diagnostico/H130/scan_concurrencia.py

Uso:
  python scan_concurrencia.py
"""
import sys
import re
import csv
import argparse
import pathlib

HERE = pathlib.Path(__file__).resolve()
PIPELINE = HERE.parents[2] / "pipeline"
REPO = HERE.parents[3]
sys.path.insert(0, str(PIPELINE))
import parser as P  # noqa: E402  (parser PARCHEADO: regla P + RE_PERF v2)

csv.field_size_limit(2**31 - 1)

ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}

# Encabezado de voto/disidencia SEPARADO (a principio de línea). v2 (H130) agrega
# "Voto la señora/el señor ministro…" (según-su-voto). NO matchea la anotación de
# firma inline "(en disidencia)"/"(según su voto)" (esas van inline, no abren línea).
RE_VOTO_HEAD = re.compile(
    r"^\s*("
    r"disidencia\b"
    r"|voto\s+(?:del?\b|de\s+l[ao]s?\b|conjunto\b|concurrente\b|en\s+disidencia\b)"
    r"|voto\s+(?:el|la|los|las)\s+se[ñn]or"
    r")", re.I)


def chunk_de(bloque, k):
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
    zonas, _ = P.zonificar_bloque(bloque)
    ld = {k for k, z in enumerate(zonas) if z == "dictamen"}
    lex = {k for k, z in enumerate(zonas) if z not in ZONAS_FALLO}
    _, ar = P.detectar_apertura_en_bloque(bloque)
    _, _, ivi, _ = P.detectar_votos_disidencias(bloque, lex)
    return ld, ar, ivi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos",  default=str(REPO / "output" / "parser" / "csjn_casos.csv"))
    ap.add_argument("--corpus", default=str(REPO / "corpus"))
    ap.add_argument("--max-muestras", type=int, default=40)
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
    sospechosos = []  # (cid, pick_idx, head_idx, pick_txt, head_txt, cands_antes)

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
        # pick del parser PARCHEADO (regla P + RE_PERF v2)
        ip, tp = P.resolver_dispositivo(bloque, ar, ld, ivi)
        if ip is None:
            continue

        de = max(ld) if ld else None
        inicio = ar if ar is not None else (de + 1 if de is not None else 0)

        # encabezados de voto/disidencia ANTES del pick
        heads = [k for k in range(inicio, ip)
                 if RE_VOTO_HEAD.search(bloque[k].strip())]
        if not heads:
            continue
        h0 = heads[0]

        # candidatos-con-firma PERFORMATIVOS antes del encabezado = mayoría que el
        # pick salteó. Si existe alguno, regla P falló en devolverlo -> mis-pick.
        cands_antes = []
        for k in range(inicio, h0):
            if k in ld:
                continue
            s = bloque[k].strip()
            if not s or not es_cand(s) or not tiene_firma(bloque, k):
                continue
            txt = chunk_de(bloque, k)
            if P.RE_PERF.search(txt):
                cands_antes.append((k, txt[:100]))
        if cands_antes:
            sospechosos.append((cid, ip, h0,
                                " ".join(str(tp or "").split())[:100],
                                " ".join(bloque[h0].split())[:80],
                                cands_antes))

    print("=" * 98)
    print(f"SCAN CONCURRENCIA · pick-de-concurrencia · parser v{P.__version__}")
    print("=" * 98)
    print(f"casos reconstruidos: {n_ok}")
    print(f"SOSPECHOSOS (pick despues de encabezado de voto CON mayoría performativa "
          f"antes): {len(sospechosos)}")
    if not sospechosos:
        print("\n>> 0 sospechosos: ningun pick salta una mayoría performativa para")
        print("   caer en una concurrencia/disidencia. El mis-pick 331_p1028 esta")
        print("   cerrado y no aparecio ninguno nuevo. Regla P + RE_PERF v2 airtight")
        print("   en el frente concurrencia.")
    for cid, ip, h0, pick_txt, head_txt, cands in sospechosos[:args.max_muestras]:
        print("\n" + "-" * 90)
        print(f"### {cid}   pick=idx {ip}   encabezado_voto=idx {h0}")
        print(f"    encabezado: {head_txt}")
        print(f"    pick      : {pick_txt}")
        print(f"    mayoría performativa ANTES del encabezado (que el pick salteo):")
        for k, t in cands:
            print(f"       idx {k:>5}  {t}")


if __name__ == "__main__":
    main()
