#!/usr/bin/env python3
"""
PoC — harness de medición de normalizar_bloque + _barrer-skip (M21 · H125)
==========================================================================

Mide el IMPACTO de las DOS mitades de M21 sobre la EXTRACCIÓN, por separado:
  - normalizar_bloque  → enmascara el banner a "" (vista limpia).
  - _barrer-skip        → _barrer NO cuenta las líneas vacías en el presupuesto
                          de 6 → el chunk pasa de largo el banner enmascarado y
                          suma el texto hasta el "." real. (monkeypatch en el PoC;
                          NO toca parser.py canónico).

4 configs:
  baseline      headers=F guion=F skip=F   (control)
  +masking      headers=T guion=F skip=F   (solo enmascara — inerte, control)
  +skip         headers=F guion=F skip=T   (solo saltea vacías — REGRESIONES de
                                             saltar blancos legítimos; banner NO
                                             enmascarado, sigue comiendo presupuesto)
  +masking+skip headers=T guion=F skip=T   (EL FIX: banner vacío + salteado)

  El masking preserva longitud/índices (vacíos in-place); _barrer-skip cambia el
  CONTEO del chunk, no los datos → NO mueve linea_inicio/linea_fin_real ni la
  ventana de firma k+1..k+41 (que es un loop aparte sobre bloque, intacto).

NO compara contra gold (circular). Ganancia vs regresión se lee por la MATRIZ DE
TRANSICIÓN y el delta de distribución. `+skip` aísla la regresión del salteo;
`+masking+skip` la recuperación.

⚠️  Corre LOCAL.

Uso:
    python scripts\\diagnostico\\h125\\poc_normalizar.py --corpus corpus \\
      --casos output\\parser\\csjn_casos.csv --mapa output\\mapa\\mapa_paginas.csv \\
      --pipeline scripts\\pipeline --corpus-full \\
      --n42 scripts\\diagnostico\\h124\\B122_banco_truncado_jurisdiccional_n42.csv
"""
import sys, csv, argparse, random
from pathlib import Path
from collections import Counter, defaultdict

csv.field_size_limit(1 << 24)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import normalizar_bloque as N

PIPELINE = HERE.parents[1] / "scripts" / "pipeline" if (HERE.parents[1] / "scripts").exists() else None

# espacio de configs (incluye la perilla skip de _barrer)
CONFIGS = {
    "baseline":      dict(headers=False, guion=False, skip=False),
    "+masking":      dict(headers=True,  guion=False, skip=False),
    "+skip":         dict(headers=False, guion=False, skip=True),
    "+masking+skip": dict(headers=True,  guion=False, skip=True),
}
FOCO = "+masking+skip"


def _import_parser(pipeline_dir):
    if pipeline_dir is None or not (Path(pipeline_dir) / "parser.py").exists():
        sys.exit("[ABORT] no encuentro scripts/pipeline/parser.py — pasá --pipeline")
    sys.path.insert(0, str(pipeline_dir))
    import parser as P
    return P


def make_barrer_skip(P):
    """Copia EXACTA de parser._barrer salvo el chunk: saltea las líneas vacías
    (banner enmascarado o blanco) SIN gastar presupuesto. Resto idéntico,
    incluida la ventana de firma k+1..k+41."""
    def _barrer_skip(bloque, rango, lineas_dictamen, *,
                     excluye_dictamen, es_candidato, permite_fallback):
        inicio, fin = rango
        _fb_idx, _fb_text = None, None
        for k in range(inicio, fin):
            if excluye_dictamen and k in lineas_dictamen:
                continue
            stripped = bloque[k].strip()
            if not stripped:
                continue
            if not es_candidato(stripped):
                continue
            # CHUNK con salteo de vacías en el presupuesto de 6
            chunk, count, m2 = [], 0, k
            while count < 6 and m2 < len(bloque):
                ln = bloque[m2]; m2 += 1
                s = ln.strip()
                if not s:                       # vacía → saltear, no cuenta
                    continue
                chunk.append(ln); count += 1
                if s.endswith("."):
                    break
            candidate_text = " ".join(chunk).strip()
            if permite_fallback and _fb_idx is None:
                _fb_idx, _fb_text = k, candidate_text
            if any(P.linea_es_firma_de_juez(bloque[j])
                   for j in range(k + 1, min(k + 41, len(bloque)))):
                return k, candidate_text
        if permite_fallback and _fb_idx is not None:
            return _fb_idx, _fb_text
        return None, ""
    return _barrer_skip


# ── insumos ──────────────────────────────────────────────────────────────────
def cargar_casos_index(casos_csv):
    idx = {}
    with open(casos_csv, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            idx[r["caso_id_canonico"]] = dict(
                source_file=r["source_file"], linea_inicio=r["linea_inicio"],
                linea_fin_real=r.get("linea_fin_real") or r.get("linea_fin"),
                tipo_entrada=r.get("tipo_entrada", ""))
    return idx


def cargar_mapa(mapa_csv):
    m = defaultdict(list)
    with open(mapa_csv, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try:
                m[r["archivo"]].append(int(r["linea_header"]))
            except (KeyError, ValueError):
                continue
    for k in m:
        m[k].sort()
    return m


def _lines_de(corpus_dir, source_file, cache):
    if source_file in cache:
        return cache[source_file]
    p = Path(corpus_dir) / source_file
    lines = p.read_text(encoding="utf-8").split("\n") if p.exists() else None
    cache[source_file] = lines
    return lines


def reconstruir_bloque(P, corpus_dir, source_file, li, lf, cache):
    lines = _lines_de(corpus_dir, source_file, cache)
    if lines is None:
        return None
    li = int(li) if str(li).strip() not in ("", "None") else 0
    lf = int(lf) if str(lf).strip() not in ("", "None") else len(lines) - 1
    return P.construir_bloque_desde_localizacion(lines, li, lf)


# ── extracción bajo una config (con perilla skip vía monkeypatch) ────────────
def extraer_bajo_config(P, bloque_crudo, header_offsets, cfg, diag, barrer_skip_fn):
    bloque = N.normalizar_bloque(bloque_crudo, header_offsets, _diag=diag,
                                 headers=cfg["headers"], guion=cfg["guion"])
    _zonas, _ = P.zonificar_bloque(bloque)
    lineas_dictamen = {k for k, z in enumerate(_zonas) if z == "dictamen"}
    lineas_residuo  = {k for k, z in enumerate(_zonas) if z == "residuo_caso_anterior"}
    _ZF = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
    lineas_excluir  = {k for k, z in enumerate(_zonas) if z not in _ZF}

    _at, apertura_rel = P.detectar_apertura_en_bloque(bloque)
    (_a, _b, inicio_votos_indiv, _c) = P.detectar_votos_disidencias(bloque, lineas_excluir)

    if cfg["skip"]:
        _orig = P._barrer
        P._barrer = barrer_skip_fn
        try:
            por_ello_idx, por_ello_text = P.resolver_dispositivo(
                bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv)
        finally:
            P._barrer = _orig
    else:
        por_ello_idx, por_ello_text = P.resolver_dispositivo(
            bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv)

    _no_cons = set(lineas_dictamen) | lineas_residuo
    if inicio_votos_indiv is not None:
        _no_cons |= set(range(inicio_votos_indiv, len(bloque)))
    considerando_text = P.extraer_considerando(bloque, por_ello_idx, _no_cons)
    outcome = P.classify_outcome(por_ello_text, considerando_text)
    return dict(por_ello_text=por_ello_text, considerando_text=considerando_text,
                outcome=outcome, dictamen_presente=bool(lineas_dictamen))


def _case_name_crudo(P, bloque_crudo):
    try:
        _, ap = P.detectar_apertura_en_bloque(bloque_crudo)
        return P.extraer_caratula_v1(bloque_crudo, ap) or ""
    except Exception:
        return ""


def correr_muestra(P, corpus_dir, casos_idx, mapa, ids, cache, barrer_skip_fn):
    res = {cfg: [] for cfg in CONFIGS}
    faltan = 0
    for cid in ids:
        meta = casos_idx.get(cid)
        if not meta or (meta["tipo_entrada"] or "").startswith("sumario"):
            continue
        bloque = reconstruir_bloque(P, corpus_dir, meta["source_file"],
                                    meta["linea_inicio"], meta["linea_fin_real"], cache)
        if not bloque:
            faltan += 1
            continue
        offsets = N.offsets_relativos(mapa.get(meta["source_file"], []),
                                      meta["linea_inicio"], meta["linea_fin_real"])
        case_name = _case_name_crudo(P, bloque)
        for cfg, kw in CONFIGS.items():
            diag = {}
            r = extraer_bajo_config(P, bloque, offsets, kw, diag, barrer_skip_fn)
            r["caso_id"] = cid
            r["es_originaria"] = bool(
                P.es_originaria(case_name, r["considerando_text"], r["por_ello_text"]))
            r["ternas"] = diag.get("ternas", 0)
            res[cfg].append(r)
    if faltan:
        print(f"[warn] {faltan} casos sin bloque reconstruible")
    return res


# ── reporte de impacto ───────────────────────────────────────────────────────
def reporte_impacto(by_id, ids_ok):
    n = len(ids_ok)
    print(f"\n{'config':14} {'flips':>7} {'flip%':>7} {'es_orig_flips':>14}")
    for cfg in CONFIGS:
        if cfg == "baseline":
            continue
        flips = sum(1 for cid in ids_ok
                    if by_id["baseline"][cid]["outcome"] != by_id[cfg][cid]["outcome"])
        esf = sum(1 for cid in ids_ok
                  if by_id["baseline"][cid]["es_originaria"] != by_id[cfg][cid]["es_originaria"])
        print(f"{cfg:14} {flips:>7} {100*flips/max(n,1):>6.2f}% {esf:>14}")

    # detalle del FIX (+masking+skip): transición + recuperación + regresión
    trans = Counter()
    gana_comp = []   # otro/… → competencia (recuperación jurisdiccional)
    for cid in ids_ok:
        b, c = by_id["baseline"][cid], by_id[FOCO][cid]
        if b["outcome"] != c["outcome"]:
            trans[(b["outcome"], c["outcome"])] += 1
            if c["outcome"] == "competencia":
                gana_comp.append((cid, b["outcome"]))
    print(f"\n  ── {FOCO}: matriz de transición (baseline → fix) ──")
    for (a, bb), k in trans.most_common(30):
        marca = "  ← recup. jurisd." if bb == "competencia" else ""
        print(f"    {a:18} → {bb:18} {k:>5}{marca}")
    print(f"\n  recuperación a competencia: {len(gana_comp)} casos")
    for cid, a in gana_comp[:40]:
        print(f"    {cid:16} {a:14} → competencia")
    if len(gana_comp) > 40:
        print(f"    (... +{len(gana_comp)-40} más)")

    # +skip solo: flips por blancos legítimos (lo que el skip quirúrgico eliminaría)
    skip_flips = [(cid, by_id["baseline"][cid]["outcome"], by_id["+skip"][cid]["outcome"])
                  for cid in ids_ok
                  if by_id["baseline"][cid]["outcome"] != by_id["+skip"][cid]["outcome"]]
    print(f"\n  ── +skip solo: {len(skip_flips)} flips (blancos legítimos; el quirúrgico los sacaría) ──")
    for cid, a, b in skip_flips:
        print(f"    {cid:16} {a:14} → {b}")

    # fix: flips NO-otro (disposición ya clasificada que cambia → riesgo de regresión)
    nootro = [(cid, by_id["baseline"][cid]["outcome"], by_id[FOCO][cid]["outcome"])
              for cid in ids_ok
              if (by_id["baseline"][cid]["outcome"] != by_id[FOCO][cid]["outcome"]
                  and by_id["baseline"][cid]["outcome"] != "otro")]
    print(f"\n  ── {FOCO}: {len(nootro)} flips NO-otro (riesgo de regresión — ojear con diag_textos) ──")
    for cid, a, b in nootro:
        print(f"    {cid:16} {a:14} → {b}")

    # delta de distribución del fix
    bd = Counter(by_id["baseline"][cid]["outcome"] for cid in ids_ok)
    fd = Counter(by_id[FOCO][cid]["outcome"] for cid in ids_ok)
    print(f"\n  ── delta de distribución outcome (baseline → {FOCO}) ──")
    for k in sorted(set(bd) | set(fd), key=lambda k: -abs(fd[k] - bd[k])):
        d = fd[k] - bd[k]
        if d:
            print(f"    {k:18} {bd[k]:>5} → {fd[k]:>5}  ({d:+d})")


def main():
    ap = argparse.ArgumentParser(description="PoC normalizar_bloque + _barrer-skip (M21/H125)")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--casos", required=True)
    ap.add_argument("--mapa", required=True)
    ap.add_argument("--n42")
    ap.add_argument("--corpus-sample", type=int, default=0)
    ap.add_argument("--corpus-full", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--pipeline", default=str(PIPELINE) if PIPELINE else None)
    args = ap.parse_args()

    P = _import_parser(args.pipeline)
    barrer_skip_fn = make_barrer_skip(P)
    casos_idx = cargar_casos_index(args.casos)
    mapa = cargar_mapa(args.mapa)
    cache = {}
    print(f"[ok] parser v{getattr(P,'__version__','?').split()[0]} · "
          f"{len(casos_idx)} casos · {len(mapa)} archivos en mapa")

    def correr_y_reportar(titulo, ids):
        print(f"\n══════ {titulo} (n_objetivo={len(ids)}) ══════")
        res = correr_muestra(P, args.corpus, casos_idx, mapa, ids, cache, barrer_skip_fn)
        by_id = {cfg: {r["caso_id"]: r for r in res[cfg]} for cfg in CONFIGS}
        ids_ok = [cid for cid in ids if cid in by_id["baseline"]]
        print(f"  reconstruidos: {len(ids_ok)}/{len(ids)}")
        reporte_impacto(by_id, ids_ok)

    if args.corpus_full or args.corpus_sample:
        reales = [cid for cid, m in casos_idx.items()
                  if not (m["tipo_entrada"] or "").startswith("sumario")]
        if args.corpus_full:
            ids = reales
        else:
            random.seed(args.seed)
            ids = random.sample(reales, min(args.corpus_sample, len(reales)))
        correr_y_reportar("IMPACTO CORPUS-WIDE", ids)

    if args.n42:
        with open(args.n42, encoding="utf-8") as f:
            ids42 = [r["caso_id_canonico"] for r in csv.DictReader(f)]
        correr_y_reportar("ANCLA banco n42", ids42)

    print("\n[fin] PoC — NO sella nada. Compuerta: BLUEPRINT §3.")


if __name__ == "__main__":
    main()
