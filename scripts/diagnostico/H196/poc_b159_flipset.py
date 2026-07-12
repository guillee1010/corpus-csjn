#!/usr/bin/env python3
"""
poc_b159_flipset.py — PoC read-only de B159 (FP de RE_DICT_HDR). H195/H196.
============================================================================
Ubicacion canonica: scripts/diagnostico/H195/  (junto a poc_b159_superficie)

Causa raiz LEIDA (7/7 testigos .md + dump corpus-wide poc_b159_superficie
v0.1, 3804 matches): 6/7 casos B159 + 9 casos nuevos = FP NARRATIVO de
RE_DICT_HDR — prosa del cuerpo cuyo wrap del OCR deja "dictamen de la/del
Procura..." a inicio de linea; re.I la matchea -> dictamen_inicio espurio ->
guarda H052 suprime dispositivo/firma/votos. El 7mo testigo (332_p2418) es
clase aparte (dictamen genuino como nota al pie "(*)", 6 corpus-wide).

DISCRIMINADOR CALIBRADO sobre el dump completo (0 perdidas / 0 FP):
forma-titulo LAXA — la linea es SOLO el titulo, con slot de UN token para
"General" (tolera OCR "Geberal" 336.1 / "Genera" 338.1) y cola opcional
"de la Nacion". Sobrevive el titulo en versalitas-OCR de 336.1
("diCtameN de la proCuraCióN GeNeral" x8, tomo hoy fuera del universo pero
futuro) — la capitalizacion a la H139 quedo DESCARTADA por eso mismo.
Resultado sobre las 3804: quedan 3789 / caen 15 (todas narrativas min=1).

Este PoC mide el FLIP-SET EXACTO del reemplazo de RE_DICT_HDR por la
gramatica nueva, con replica FIEL de procesar_archivo v30.0 (zonificar ->
lineas_dictamen/excluir -> apertura -> votos -> resolver_dispositivo ->
RELABEL A1 de H194 verbatim -> extraer_segmentos + considerando + outcome).
A diferencia de poc_b149_anclas (que cortaba ANTES del relabel, e0_mismatch
esperado 25), aca el relabel A1 esta replicado -> CANDADO E0 esperado:
0 mismatch sobre los fallos en alcance.

CONTRATO ESPERADO: flips SOLO en los 15 casos del dump —
  329_p1638 334_p109 337_p166 337_p1006 338_p1009 339_p662 340_p691
  340_p1542 342_p1735 344_p1952 344_p2123 344_p2307 344_p3249 347_p1944
  348_p763
Cualquier flip FUERA de ese set = FRENAR y adjudicar.

LIMITES DECLARADOS del alcance:
  - linea_fin_real se toma del CSV publicado: el radio de RE_DICT_HDR en
    detectar_fin_real (L2868) y en la clase de linea de frontera (L2164)
    NO se mide aca — se adjudica en el ciclo --consciente.
  - Solo tipo_entrada == fallo (espejo poc_b149_anclas).

NO toca el pipeline. Salidas:
  poc_b159_flipset.csv — un registro por caso flipeado (transiciones de
    zona compactas + ripple por_ello/outcome)
  resumen por consola

Uso (desde la raiz del repo):
  python scripts\\diagnostico\\H195\\poc_b159_flipset.py
  python scripts\\diagnostico\\H195\\poc_b159_flipset.py --solo-tomo 344
  python scripts\\diagnostico\\H195\\poc_b159_flipset.py --esperar-version 30.0
"""
import argparse, csv, re, sys
from collections import Counter, defaultdict
from pathlib import Path

__version__ = "0.2"

HERE = Path(__file__).resolve().parent


def _find_root(start: Path) -> Path:
    """Sube hasta hallar la raiz del repo (marcador: scripts/pipeline/parser.py).
    Patron extraer_caso.py / poc_b148_flipset / poc_b149_anclas."""
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start.parents[2] if len(start.parents) >= 3 else start


ROOT = _find_root(HERE)
PARSER_PY = ROOT / "scripts" / "pipeline" / "parser.py"

DEF_CASOS  = ROOT / "output" / "parser" / "csjn_casos.csv"
DEF_ZONAS  = ROOT / "output" / "parser" / "csjn_casos_zonas.csv"
DEF_CORPUS = ROOT / "corpus"
DEF_OUT    = HERE / "poc_b159_flipset.csv"

# ── RE_DICT_HDR candidata (EL FIX): forma-titulo laxa ────────────────────────
# Calibrada en poc_b159_superficie v0.1 sobre el universo completo:
# 3789 titulos quedan (incl. versalitas 336.1 y OCR Geberal/Genera) /
# 15 narrativas caen / 0 perdidas. Reemplazaria a RE_DICT_HDR en L188
# (fuente unica: cubre los 3 call-sites sin tocar logica).
RE_DICT_HDR_NUEVA = re.compile(
    r"^Dictamen\s+de(?:l)?\s+(?:la\s+)?Procura\S*"
    r"(?:\s+\w+)?"                       # slot "General" (1 token, tolera OCR)
    r"(?:\s+de\s+la\s+Naci[oó]n)?"
    r"\s*[.:\)\(\*\u2013\u2014-]*\s*$",
    re.I,
)

FLIPS_ESPERADOS = {
    "329_p1638", "334_p109", "337_p166", "337_p1006", "338_p1009",
    "339_p662", "340_p691", "340_p1542", "342_p1735", "344_p1952",
    "344_p2123", "344_p2307", "344_p3249", "347_p1944", "348_p763",
}


def cargar_parser(esperar_version):
    """Importa el parser real (verbatim poc_b149_anclas.cargar_parser)."""
    if not PARSER_PY.exists():
        sys.exit(f"[FATAL] no existe {PARSER_PY}")
    pipeline_dir = str(PARSER_PY.parent)
    if pipeline_dir not in sys.path:
        sys.path.insert(0, pipeline_dir)
    import parser as P  # noqa
    ver = getattr(P, "__version__", "?")
    if esperar_version and not str(ver).startswith(esperar_version):
        sys.exit(f"[FATAL] parser v{ver} != esperado {esperar_version} "
                 f"(gate de instalacion; --esperar-version para override)")
    print(f"[poc_b159_flipset v{__version__}] parser v{ver} importado de {PARSER_PY}")
    return P


def replica_v30(P, bloque):
    """Replica de procesar_archivo v30.0: L3763 (zonificar) -> L3905 (fin del
    relabel A1) + considerando/outcome (L3912/3916). Retorna
    (zonas_linea, segs, por_ello_idx, por_ello_text, outcome)."""
    zl, _anclas = P.zonificar_bloque(bloque)
    lineas_dictamen = {k for k, z in enumerate(zl) if z == "dictamen"}
    lineas_residuo = {k for k, z in enumerate(zl)
                      if z == "residuo_caso_anterior"}
    _ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma",
                    "voto_separado"}
    lineas_excluir = {k for k, z in enumerate(zl) if z not in _ZONAS_FALLO}
    _t, apertura_rel = P.detectar_apertura_en_bloque(bloque)
    (_nv, _nd, inicio_votos_indiv, _mk) = P.detectar_votos_disidencias(
        bloque, lineas_excluir)
    por_ello_idx, por_ello_text = P.resolver_dispositivo(
        bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv)

    # B149 fix A1 (H194) VERBATIM (parser.py L3898-3905)
    if por_ello_idx is not None and zl[por_ello_idx] == "cuerpo":
        _fin_disp = next(
            (j for j in range(por_ello_idx + 1, len(zl))
             if zl[j] in ("firma", "voto_separado", "epilogo")),
            len(zl))
        for _j in range(por_ello_idx, _fin_disp):
            if zl[_j] == "cuerpo":
                zl[_j] = "dispositivo"

    segs = [(s["zona"], int(s["linea_ini"]), int(s["linea_fin"]))
            for s in P.extraer_segmentos(zl, bloque)]

    # ripple de decision (parser.py L3909-3916): considerando -> outcome
    _lineas_no_cons = set(lineas_dictamen) | lineas_residuo
    if inicio_votos_indiv is not None:
        _lineas_no_cons |= set(range(inicio_votos_indiv, len(bloque)))
    considerando_text = P.extraer_considerando(bloque, por_ello_idx,
                                               _lineas_no_cons)
    outcome = P.classify_outcome(por_ello_text, considerando_text)

    return zl, segs, por_ello_idx, por_ello_text, outcome


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--casos", type=Path, default=DEF_CASOS)
    ap.add_argument("--zonas", type=Path, default=DEF_ZONAS)
    ap.add_argument("--corpus-dir", type=Path, default=DEF_CORPUS)
    ap.add_argument("--out", type=Path, default=DEF_OUT)
    ap.add_argument("--solo-tomo", default="", help="filtrar un tomo (piloto)")
    ap.add_argument("--esperar-version", default="30.0")
    a = ap.parse_args()

    for p in (a.casos, a.zonas, a.corpus_dir):
        if not p.exists():
            sys.exit(f"[FATAL] no existe: {p}")

    P = cargar_parser(a.esperar_version)
    RE_VIEJA = P.RE_DICT_HDR  # referencia publicada, para restaurar

    zonas_pub = defaultdict(list)
    with a.zonas.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            zonas_pub[r["caso_id_canonico"]].append(
                (r["zona"], int(r["linea_ini"]), int(r["linea_fin"])))

    filas_casos = []
    with a.casos.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r.get("tipo_entrada") != "fallo":
                continue
            if a.solo_tomo and r.get("tomo") != a.solo_tomo:
                continue
            if not (r.get("source_file") and r.get("linea_inicio")
                    and r.get("linea_fin_real")):
                continue
            filas_casos.append(r)
    print(f"  fallos en alcance: {len(filas_casos)}"
          + (f" (tomo {a.solo_tomo})" if a.solo_tomo else ""))

    cache_md = {}
    def lineas_de(source_file):
        if source_file not in cache_md:
            fp = a.corpus_dir / source_file
            if not fp.exists():
                return None
            # lectura estilo parser: split('\n'), NO splitlines (parser L3530)
            cache_md[source_file] = fp.read_text(encoding="utf-8").split("\n")
        return cache_md[source_file]

    flips, stats = [], Counter()
    fuera_de_contrato = []

    for r in filas_casos:
        cid = r["caso_id_canonico"]
        lines = lineas_de(r["source_file"])
        if lines is None:
            stats["sin_md"] += 1
            continue
        bloque = P.construir_bloque_desde_localizacion(
            lines, int(r["linea_inicio"]), int(r["linea_fin_real"]))
        if not bloque:
            stats["bloque_vacio"] += 1
            continue

        # ── pasada VIEJA (regex publicada) + candado E0 ──────────────────
        P.RE_DICT_HDR = RE_VIEJA
        zl_o, segs_o, pei_o, pet_o, out_o = replica_v30(P, bloque)
        if segs_o != zonas_pub.get(cid, []):
            stats["e0_mismatch"] += 1
            continue
        stats["e0_ok"] += 1

        # ── pasada NUEVA (gramatica forma-titulo laxa) ───────────────────
        P.RE_DICT_HDR = RE_DICT_HDR_NUEVA
        zl_n, segs_n, pei_n, pet_n, out_n = replica_v30(P, bloque)
        P.RE_DICT_HDR = RE_VIEJA

        if segs_n == segs_o and pei_n == pei_o and pet_n == pet_o \
                and out_n == out_o:
            continue  # sin flip

        trans = Counter()
        for zo, zn in zip(zl_o, zl_n):
            if zo != zn:
                trans[f"{zo}->{zn}"] += 1
        fila = {
            "caso_id_canonico": cid, "tomo": r.get("tomo", ""),
            "en_contrato": int(cid in FLIPS_ESPERADOS),
            "n_lineas_zona_flip": sum(trans.values()),
            "transiciones": "; ".join(f"{k}:{v}"
                                      for k, v in trans.most_common()),
            "por_ello_idx_old": pei_o, "por_ello_idx_new": pei_n,
            "outcome_old": out_o, "outcome_new": out_n,
            "por_ello_cambia": int(pet_o != pet_n),
            "pe_old": (pet_o or "")[:90], "pe_new": (pet_n or "")[:90],
        }
        flips.append(fila)
        if cid not in FLIPS_ESPERADOS:
            fuera_de_contrato.append(cid)

    if flips:
        with a.out.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(flips[0].keys()),
                               lineterminator="\n")
            w.writeheader(); w.writerows(flips)

    # ── resumen ──────────────────────────────────────────────────────────
    print(f"\n  candado E0: ok {stats['e0_ok']} / mismatch "
          f"{stats['e0_mismatch']} / sin_md {stats['sin_md']} / "
          f"bloque_vacio {stats['bloque_vacio']}")
    if stats["e0_mismatch"]:
        print("  [FRENAR] e0_mismatch > 0: con el relabel A1 replicado el "
              "candado esperado es 0 — la replica no es fiel, adjudicar "
              "ANTES de usar el flip-set.")

    print(f"\nflip-set del reemplazo de RE_DICT_HDR: {len(flips)} casos "
          f"(esperados: {len(FLIPS_ESPERADOS)})")
    esperados_vistos = {f['caso_id_canonico'] for f in flips} & FLIPS_ESPERADOS
    print(f"  en contrato     : {len(esperados_vistos)}/{len(FLIPS_ESPERADOS)}")
    faltan = FLIPS_ESPERADOS - esperados_vistos
    if faltan:
        print(f"  esperados SIN flip (adjudicar: puede ser flip solo-de-zona "
              f"ya identico u otra causa): {sorted(faltan)}")
    if fuera_de_contrato:
        print(f"  [FRENAR] flips FUERA de contrato: {sorted(fuera_de_contrato)}")
    outs = Counter((f["outcome_old"], f["outcome_new"]) for f in flips
                   if f["outcome_old"] != f["outcome_new"])
    print(f"  flips de outcome: {sum(outs.values())}")
    for (o, n), c in outs.most_common():
        print(f"    {o or '(vacio)'} -> {n or '(vacio)'}: {c}")
    for f in flips:
        print(f"  {f['caso_id_canonico']:<11} zonas {f['n_lineas_zona_flip']:5d} | "
              f"pe {f['por_ello_idx_old']}→{f['por_ello_idx_new']} | "
              f"out {f['outcome_old'] or '∅'}→{f['outcome_new'] or '∅'} | "
              f"{f['transiciones'][:70]}")
    if flips:
        print(f"\n  -> {a.out}")
    print("\n  (la adjudicacion de cada flip es por lectura del CSV; el radio "
          "en detectar_fin_real/frontera se mide en el ciclo consciente)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
