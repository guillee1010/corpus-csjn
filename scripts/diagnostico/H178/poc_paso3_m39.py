#!/usr/bin/env python3
"""
poc_paso3_m39.py — PoC read-only del PASO 3 de M39 (corpus-csjn, H178).
========================================================================
Verificador BIMODAL con candado de versión (patrón poc_b143_guard, H177).

PASO 3: is_merit derivado del clasificador como fuente única (parser importa
disposicion() + es_revision_fondo(); el branch B136 y MERIT_OUTCOMES se retiran).

MODO PRE (antes de cablear):
  A1  Identidad de insumos: el gate RECOMPUTADO desde casos+textos (misma
      llamada que derivar_recursos v0.6) reproduce la columna publicada
      es_revision_fondo con 0 diffs. Cierra round-trip CSV + sync de versión.
  A2  Flip-set exacto: casos donde is_merit_decision != gate == divergencia
      M39 publicada == 227 (151 si→no·1→0 + 76 no→si·0→1), ids exactos.
  A3  Anclas 1→0 OBLIGATORIAS dentro del flip-set:
        - 9 expuestos B140b (H175)
        - 13 expuestos B143 (H177; los 15 FP menos 347_p327/348_p1152 que ya
          estaban divergentes con is_merit=0)
        - 9 aciertos-del-gate/outcome-equivocado adjudicados (H172+H176)
  A4  Ancla de NO-flip: 330_p399 (López) is_merit=1 ∧ gate=si (fuera del set).
  A5  n300 ∩ flip-set == los 8 medidos en apertura H178 (candado byte-idéntico
      NO alcanzable — retiro documentado junto con D1; re-κ = M43).
  R   Reporte por clase (dirección × outcome × disposicion × originaria),
      localización de los costos aceptados (FN-B139a enumerados, residuales
      B138) y cota superior del ripple en votos (si se pasa --votos).

MODO POST (después de cablear parser v24.0 + re-derivar):
  P1  is_merit == gate en las 5890 filas (divergencia M39 = 0 por construcción).
  P2  is_merit=1 == 2935 · is_originaria == 589.
  P3  Anclas: todas las 1→0 en 0; 330_p399 en 1.
  P4  Candado: parser >= 24.0 en disco.

Costos aceptados (documentados, NO son fallas del PoC):
  - FN-B139a enumerados (gate equivocado, adjudicados-sin-guard H176): el paso 3
    los flipea 1→0 si el parser acertaba de rebote. Se REPORTAN, no se assertan.
  - Residuales B138 (4 FP del gate): si el parser estaba en 0, flipean 0→1.

Uso:
  python poc_paso3_m39.py --mode pre  [--root RAIZ | overrides]
  python poc_paso3_m39.py --mode post [--root RAIZ | overrides]
Overrides: --casos --textos --recursos --votos --clave --pipeline-dir --parser-file
Ubicación canónica: scripts/diagnostico/H178/  (ROOT = parents[2])
"""
import argparse, csv, re, sys
from pathlib import Path
import pandas as pd
csv.field_size_limit(10**7)

__version__ = "0.2"

# ── candado de versión ────────────────────────────────────────────────────────
CLF_VER_ESPERADA     = "1.15"
DERIVAR_VER_ESPERADA = "0.6"
PARSER_VER_PRE       = "23.2"
PARSER_VER_POST_MIN  = (24, 0)

# ── métricas selladas H177 (estado PRE) ───────────────────────────────────────
N_FILAS        = 5890
IS_MERIT_PRE   = 3010
GATE_SI        = 2935
ORIGINARIA     = 589
DIV_TOTAL      = 227
DIV_1A0        = 151   # parser-si / gate-no
DIV_0A1        = 76    # parser-no / gate-si

# ── anclas adjudicadas (ids verbatim de DEUDA_TECNICA, entradas citadas) ─────
B140B_9 = ["329_p120", "329_p4279", "329_p5579", "331_p1906", "331_p2583",
           "332_p2813", "334_p1139", "339_p299", "344_p1435"]          # H175, B140(b)
B143_13 = ["329_p1794", "330_p487", "330_p4925", "330_p5052", "333_p1671",
           "339_p656", "330_p1169", "334_p1458", "337_p97", "345_p191",
           "332_p1823", "344_p163", "344_p1259"]                        # H177, B143
ACIERTOS_GATE_9 = ["330_p251", "333_p1152",                             # H172
                   "330_p1950", "330_p4396", "337_p1024", "339_p852",
                   "344_p2513", "348_p83", "333_p1857"]                 # H176
ANCLA_NOFLIP = "330_p399"                                               # López, gate=si
# costos aceptados — se reportan, no se assertan:
FN_B139A_9 = ["332_p731", "340_p411", "341_p1924", "341_p1075", "343_p28",
              "338_p234", "331_p2628", "337_p1042", "332_p2797"]        # H176 (el 10º,
              # 330_p1927, convergió vía v1.14 «impugnación»)
RESID_B138 = ["331_p2621", "330_p4891"]                                 # H175; +sufijos
RESID_B138_SUFIJOS = ["_p1205", "_p747"]                                # tomo sin registrar
N300_8 = ["330_p1907", "330_p4592", "331_p2621", "332_p2625", "332_p2797",
          "338_p40", "344_p3394", "348_p92"]                            # medidos H178

FALLAS = []
def check(nombre, cond, detalle=""):
    tag = "[OK]  " if cond else "[FAIL]"
    print(f"{tag} {nombre}" + (f" — {detalle}" if detalle else ""))
    if not cond:
        FALLAS.append(nombre)

def leer_version_archivo(path: Path, etiqueta: str) -> str:
    txt = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', txt, re.M)
    if not m:
        sys.exit(f"[ABORT] no encuentro __version__ en {etiqueta} ({path})")
    return m.group(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pre", "post"], required=True)
    ap.add_argument("--root")
    ap.add_argument("--casos"); ap.add_argument("--textos"); ap.add_argument("--recursos")
    ap.add_argument("--votos"); ap.add_argument("--clave")
    ap.add_argument("--pipeline-dir"); ap.add_argument("--parser-file")
    a = ap.parse_args()

    here = Path(__file__).resolve().parent
    if a.root:
        root = Path(a.root)
    elif len(here.parents) >= 3:
        root = here.parents[2]                              # scripts/diagnostico/H178/
    else:
        root = here                                         # sandbox: todo por override
    outp = root / "output" / "parser"
    pipe = Path(a.pipeline_dir) if a.pipeline_dir else root / "scripts" / "pipeline"
    casos_p   = Path(a.casos)   if a.casos   else outp / "csjn_casos.csv"
    textos_p  = Path(a.textos)  if a.textos  else outp / "csjn_casos_textos.csv"
    rec_p     = Path(a.recursos) if a.recursos else outp / "csjn_casos_recursos.csv"
    parser_p  = Path(a.parser_file) if a.parser_file else pipe / "parser.py"
    clave_p   = Path(a.clave) if a.clave else root / "scripts" / "validacion" / "M20_clave_parser_n300.csv"
    votos_p   = Path(a.votos) if a.votos else outp / "csjn_casos_votos.csv"

    # ── candado de versión ───────────────────────────────────────────────────
    sys.path.insert(0, str(pipe))
    from clasificador_disposicion import disposicion, es_revision_fondo, __version__ as CLF_VER
    check("candado clasificador_disposicion", CLF_VER == CLF_VER_ESPERADA,
          f"en disco {CLF_VER}, esperada {CLF_VER_ESPERADA}")
    dv = leer_version_archivo(pipe / "derivar_recursos.py", "derivar_recursos")
    check("candado derivar_recursos", dv == DERIVAR_VER_ESPERADA,
          f"en disco {dv}, esperada {DERIVAR_VER_ESPERADA}")
    pv = leer_version_archivo(parser_p, "parser")
    if a.mode == "pre":
        check("candado parser (PRE)", pv == PARSER_VER_PRE,
              f"en disco {pv}, esperada {PARSER_VER_PRE}")
    else:
        try:
            pt = tuple(int(x) for x in pv.split("."))
        except ValueError:
            pt = (0,)
        check("candado parser (POST)", pt >= PARSER_VER_POST_MIN,
              f"en disco {pv}, esperada >= {'.'.join(map(str, PARSER_VER_POST_MIN))}")
    if FALLAS:
        sys.exit(f"[ABORT] candado de versión no cumplido: {FALLAS}")

    # ── datos ────────────────────────────────────────────────────────────────
    casos  = pd.read_csv(casos_p,  dtype=str, keep_default_na=False)
    textos = pd.read_csv(textos_p, dtype=str, keep_default_na=False)[
                 ["caso_id_canonico", "por_ello_text", "considerando_text"]]
    rec    = pd.read_csv(rec_p,    dtype=str, keep_default_na=False)
    df = casos.merge(textos, on="caso_id_canonico", how="left")
    df["por_ello_text"] = df["por_ello_text"].fillna("")
    df["considerando_text"] = df["considerando_text"].fillna("")
    df = df.merge(rec[["caso_id_canonico", "es_revision_fondo", "disposicion"]],
                  on="caso_id_canonico", how="left")
    check("filas", len(df) == N_FILAS, f"{len(df)}")

    # gate RECOMPUTADO — llamada idéntica a derivar_recursos v0.6
    disp_re = df["por_ello_text"].map(disposicion)
    df["disp_recalc"] = disp_re.map(lambda r: r[0])
    df["gate_recalc"] = [es_revision_fondo(d, pe, o == "1", co)
                         for d, pe, o, co in zip(df["disp_recalc"], df["por_ello_text"],
                                                 df["is_originaria"], df["considerando_text"])]

    if a.mode == "pre":
        # A1 — identidad de insumos (round-trip CSV + sync de versión)
        diffs_gate = (df["gate_recalc"] != df["es_revision_fondo"]).sum()
        diffs_disp = (df["disp_recalc"] != df["disposicion"]).sum()
        check("A1 gate recomputado == columna publicada", diffs_gate == 0, f"{diffs_gate} diffs")
        check("A1b disposicion recomputada == publicada", diffs_disp == 0, f"{diffs_disp} diffs")

        # A2 — flip-set exacto == divergencia publicada
        f10 = df[(df["is_merit_decision"] == "1") & (df["gate_recalc"] == "no")]
        f01 = df[(df["is_merit_decision"] == "0") & (df["gate_recalc"] == "si")]
        flips = set(f10["caso_id_canonico"]) | set(f01["caso_id_canonico"])
        check("A2 flip-set 1→0", len(f10) == DIV_1A0, f"{len(f10)} (esperado {DIV_1A0})")
        check("A2 flip-set 0→1", len(f01) == DIV_0A1, f"{len(f01)} (esperado {DIV_0A1})")
        pub10 = df[(df["is_merit_decision"] == "1") & (df["es_revision_fondo"] == "no")]
        pub01 = df[(df["is_merit_decision"] == "0") & (df["es_revision_fondo"] == "si")]
        pub = set(pub10["caso_id_canonico"]) | set(pub01["caso_id_canonico"])
        check("A2 ids == divergencia publicada", flips == pub,
              f"solo-recalc {sorted(flips - pub)} · solo-pub {sorted(pub - flips)}" if flips != pub else "ids exactos")
        check("A2 métricas base", (df["is_merit_decision"] == "1").sum() == IS_MERIT_PRE
              and (df["gate_recalc"] == "si").sum() == GATE_SI
              and (df["is_originaria"] == "1").sum() == ORIGINARIA,
              f"is_merit {(df['is_merit_decision']=='1').sum()} · gate=si {(df['gate_recalc']=='si').sum()} · orig {(df['is_originaria']=='1').sum()}")

        # A3 — anclas 1→0 obligatorias
        s10 = set(f10["caso_id_canonico"])
        for nombre, ids in [("A3 9 expuestos B140b", B140B_9),
                            ("A3 13 expuestos B143", B143_13),
                            ("A3 9 aciertos-del-gate H172/H176", ACIERTOS_GATE_9)]:
            faltan = [i for i in ids if i not in s10]
            check(f"{nombre} ⊂ flips 1→0", not faltan, f"faltan {faltan}" if faltan else f"{len(ids)}/{len(ids)}")

        # A4 — ancla de no-flip
        r399 = df[df["caso_id_canonico"] == ANCLA_NOFLIP]
        ok399 = (len(r399) == 1 and r399.iloc[0]["is_merit_decision"] == "1"
                 and r399.iloc[0]["gate_recalc"] == "si" and ANCLA_NOFLIP not in flips)
        check("A4 330_p399 queda is_merit=1 (fuera del flip-set)", ok399)

        # A5 — n300
        if clave_p.exists():
            clave = pd.read_csv(clave_p, dtype=str, keep_default_na=False)
            inter = sorted(flips & set(clave["caso_id_canonico"]))
            check("A5 n300 ∩ flip-set == 8 medidos", inter == sorted(N300_8), f"{inter}")
        else:
            print(f"[WARN] clave n300 no encontrada en {clave_p} — A5 no corrido")

        # R — reporte por clase (adjudicación contra taxonomía M1-M5)
        print("\n── R: flip-set por clase ─────────────────────────────────────")
        for tag, sub in [("1→0 (151)", f10), ("0→1 (76)", f01)]:
            print(f"\n[{tag}] outcome × disposicion × originaria:")
            tab = (sub.groupby(["outcome", "disp_recalc", "is_originaria"])
                      .size().sort_values(ascending=False))
            print(tab.to_string())
        conocidos_10 = set(B140B_9) | set(B143_13) | set(ACIERTOS_GATE_9)
        resto10 = sorted(s10 - conocidos_10)
        print(f"\n1→0 no-adjudicados-por-id (clases M2A/M3/M4 del gate-ok): {len(resto10)}")
        print("   " + " ".join(resto10))
        print("\nCostos aceptados localizados:")
        fn_in = [i for i in FN_B139A_9 if i in s10]
        print(f"  FN-B139a en 1→0 (adoptan el error del gate): {fn_in}")
        fn_out = [i for i in FN_B139A_9 if i not in flips]
        print(f"  FN-B139a fuera del flip-set (coincide-en-error, sin cambio): {fn_out}")
        s01 = set(f01["caso_id_canonico"])
        rb = [i for i in RESID_B138 if i in s01] + \
             [i for i in s01 for suf in RESID_B138_SUFIJOS if i.endswith(suf)]
        print(f"  Residuales B138 en 0→1 (adoptan FP del gate): {sorted(set(rb))}")

        # cota de ripple en votos
        if votos_p.exists():
            votos = pd.read_csv(votos_p, dtype=str, keep_default_na=False)
            vf = votos[votos["caso_id_canonico"].isin(flips)]
            print(f"\nVotos en casos del flip-set (is_merit_decision denormalizado cambia): {len(vf)}")
            v10 = votos[votos["caso_id_canonico"].isin(s10)]
            v01 = votos[votos["caso_id_canonico"].isin(s01)]
            wc = pd.to_numeric(v10.get("wc_voto", pd.Series(dtype=str)), errors="coerce").fillna(0)
            cand_pierde = ((wc >= 2500) & (v10.get("tipo_voto_sep", "") == "D")).sum()
            wc2 = pd.to_numeric(v01.get("wc_voto", pd.Series(dtype=str)), errors="coerce").fillna(0)
            cand_gana = ((wc2 >= 2500) & (v01.get("tipo_voto_sep", "") == "indeterminado")).sum()
            print(f"COTA SUPERIOR tipo_voto (regla L1738): candidatos a perder D-por-fallback "
                  f"(1→0, wc≥2500, D): {cand_pierde} · a ganar D (0→1, wc≥2500, indeterminado): {cand_gana}")
            print("(cota, no flip exacto: D puede venir de ramas anteriores del cascade — "
                  "el diff exacto lo da check_regresion tras el cableado)")
        else:
            print("\n[WARN] --votos no provisto — cota de ripple en votos no corrida (Gate 7: pedirla antes de cablear)")

    else:  # POST
        div10 = ((df["is_merit_decision"] == "1") & (df["gate_recalc"] == "no")).sum()
        div01 = ((df["is_merit_decision"] == "0") & (df["gate_recalc"] == "si")).sum()
        check("P1 divergencia M39 == 0", div10 + div01 == 0, f"{div10}+{div01}")
        dpub = (df["gate_recalc"] != df["es_revision_fondo"]).sum()
        check("P1b gate recomputado == recursos re-derivado", dpub == 0, f"{dpub} diffs")
        check("P2 is_merit=1 == 2935", (df["is_merit_decision"] == "1").sum() == GATE_SI,
              f"{(df['is_merit_decision']=='1').sum()}")
        check("P2b is_originaria == 589", (df["is_originaria"] == "1").sum() == ORIGINARIA)
        idx = df.set_index("caso_id_canonico")["is_merit_decision"]
        mal = [i for i in (B140B_9 + B143_13 + ACIERTOS_GATE_9) if idx.get(i) != "0"]
        check("P3 anclas 1→0 en 0", not mal, f"mal: {mal}" if mal else "31/31")
        check("P3b 330_p399 en 1", idx.get(ANCLA_NOFLIP) == "1")

    print()
    if FALLAS:
        print(f"[FAIL] PoC v{__version__} modo {a.mode.upper()} — fallas: {FALLAS}")
        sys.exit(1)
    print(f"[CLEAN] PoC v{__version__} modo {a.mode.upper()} — todas las aserciones verdes")

if __name__ == "__main__":
    main()
