#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
explorar_residual.py — diagnostico del residual de materia (capa 2).

Para los casos que la cascada de capa 2 NO resolvio (materia_capa ==
pendiente_capa2), extrae las senales mineable y mide cuales discriminan,
usando capa 1 (materia ground-truth via tribunal) como referencia:
  - leyes citadas en el considerando (csjn_casos_textos.csv)
  - el "s/ objeto" de la caratula (csjn_casos.csv)

Salidas: reporte por consola (motivo del residual, objetos 's/' discriminantes
de capa1, top objetos del residual, top leyes del residual NO en el indice) +
CSV por-caso (capa2 + pendiente_capa2) para auditar: output/diagnostico/.

NO canonico: herramienta de diagnostico, NO entra al manifest ni al golden.

Uso:
    python scripts/diagnostico/explorar_residual.py
    python scripts/diagnostico/explorar_residual.py --top 30
"""
from __future__ import annotations
import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

__version__ = "1.0"  # H113: diagnostico del residual de materia (leyes + s/objeto).

csv.field_size_limit(10 ** 7)

SCRIPT_DIR = Path(__file__).resolve().parent           # .../scripts/diagnostico
REPO_ROOT  = SCRIPT_DIR.parent.parent
D_CASOS   = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
D_TEXTOS  = REPO_ROOT / "output" / "parser" / "csjn_casos_textos.csv"
D_MATERIA = REPO_ROOT / "output" / "parser" / "csjn_casos_materia.csv"
D_INDICE  = REPO_ROOT / "_meta" / "vocab_materia" / "indice_normas.csv"
D_OUT     = REPO_ROOT / "output" / "diagnostico" / "residual_diagnostico.csv"

RE_SOBRE = re.compile(r"\bs/\s*")
RE_LEY   = re.compile(r"ley(?:es)?\s+(?:n[ºo]?\.?\s*)?(\d{1,3}(?:\.\d{3})+|\d{4,6})")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).lower().strip()


def objeto(cuerpo: str, indice: str) -> str:
    for fld in (cuerpo, indice):
        partes = RE_SOBRE.split(norm(fld))
        if len(partes) > 1:
            o = partes[-1].strip(" .,-")
            o = re.sub(r"\s+(recurso de hecho|recurso extraordinario).*$", "", o)
            return o[:60]
    return ""


def leyes(considerando: str) -> set:
    return {m.replace(".", "") for m in RE_LEY.findall(norm(considerando))}


def fmt_ley(n: str) -> str:
    n = str(int(n))
    return f"{n[:-3]}.{n[-3:]}" if len(n) > 3 else n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Diagnostico del residual de materia.")
    ap.add_argument("--casos",   type=Path, default=D_CASOS)
    ap.add_argument("--textos",  type=Path, default=D_TEXTOS)
    ap.add_argument("--materia", type=Path, default=D_MATERIA)
    ap.add_argument("--indice",  type=Path, default=D_INDICE)
    ap.add_argument("--out",     type=Path, default=D_OUT)
    ap.add_argument("--top",     type=int,  default=20)
    args = ap.parse_args(argv)

    for p in (args.casos, args.textos, args.materia, args.indice):
        if not p.exists():
            raise SystemExit(f"[FATAL] no existe: {p}")

    casos   = pd.read_csv(args.casos, dtype=str, keep_default_na=False)
    textos  = pd.read_csv(args.textos, dtype=str, keep_default_na=False)
    materia = pd.read_csv(args.materia, dtype=str, keep_default_na=False)
    ind     = pd.read_csv(args.indice, dtype=str, keep_default_na=False)
    conocidas = set(ind[ind["tier"] == "ancla"]["numero"].str.strip())

    df = (materia
          .merge(casos[["caso_id_canonico", "case_name_cuerpo", "case_name_indice"]],
                 on="caso_id_canonico", how="left")
          .merge(textos[["caso_id_canonico", "considerando_text"]],
                 on="caso_id_canonico", how="left"))
    df["objeto"] = [objeto(c, i) for c, i in
                    zip(df["case_name_cuerpo"], df["case_name_indice"])]
    df["leyes"]  = df["considerando_text"].map(leyes)

    c1  = df[df["materia_capa"] == "capa1"]
    res = df[df["materia_capa"] == "pendiente_capa2"]
    print(f"capa1={len(c1)}  residual(pendiente_capa2)={len(res)}")
    print(f"residual con objeto 's/': {(res['objeto']!='').sum()} "
          f"({100*(res['objeto']!='').sum()/max(len(res),1):.0f}%)")
    print("\n=== residual por motivo ===")
    print(res["materia_fuente"].map(lambda f: f.split(":")[0]).value_counts().to_string())

    print("\n=== objetos 's/' discriminantes (capa1, soporte>=10, pureza>=0.80) ===")
    o2m = defaultdict(Counter)
    for o, m in zip(c1["objeto"], c1["materia"]):
        if o:
            o2m[o][m] += 1
    filas = []
    for o, c in o2m.items():
        tot = sum(c.values())
        if tot < 10:
            continue
        dom, dn = c.most_common(1)[0]
        filas.append((o, tot, dom, dn / tot))
    for o, tot, dom, pur in sorted(filas, key=lambda x: (-x[3], -x[1])):
        if pur >= 0.80:
            print(f"  {o[:38]:38s} n={tot:4d} {pur:4.0%} -> {dom}")

    print("\n=== top objetos 's/' en el residual (candidatos) ===")
    for o, n in Counter(res[res["objeto"] != ""]["objeto"]).most_common(args.top):
        print(f"  {o[:50]:50s} {n:4d}")

    print("\n=== top leyes en el residual NO en el indice (candidatas) ===")
    cnt = Counter()
    for s in res["leyes"]:
        for n in s:
            if n not in conocidas:
                cnt[n] += 1
    for n, c in cnt.most_common(args.top):
        print(f"  {fmt_ley(n):>9} {c:4d}")

    dump = df[df["materia_capa"].isin(["capa2", "pendiente_capa2"])][
        ["caso_id_canonico", "materia", "materia_capa", "materia_fuente", "objeto"]].copy()
    dump["leyes"] = df["leyes"].map(lambda s: " ".join(sorted(s)))
    dump["caratula"] = df["case_name_cuerpo"].str[:80]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    dump.to_csv(args.out, index=False, lineterminator="\n")
    print(f"\n[dump] {args.out}  ({len(dump)} filas: capa2 + pendiente_capa2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
