"""secretarias_votacion.py — votación por secretaría con control de mérito y de tamaño del tribunal (M66/M67, H221)

Lee casos_sjconsulta.csv (salida de unir_sjconsulta.py, cache local) y output/parser/csjn_casos.csv
(solo lectura). No hace pedidos al sitio.

Para cada caso clasifica la votación desde `posiciones` del corpus (M67):
  unanime · cabeza_con_mayoria_abs (el voto que encabeza tiene la mayoría absoluta del tribunal)
  · cabeza_sin_mayoria_abs (mayoría circunstancial) · sin_cabeza (todos con voto propio o disidencia)
Tribunal = jueces con posición en el fallo (titulares y conjueces); mayoría absoluta = n//2 + 1.

Imprime, solo decisiones de MÉRITO (is_merit_decision), por secretaría:
  A. total · B. por tamaño del tribunal (el umbral de mayoría cambia con el tamaño) · C. por año
  · D. posición de cada juez dentro de cada secretaría · E. chi² (con corrección de Yates) de cada
  secretaría contra el resto, por tamaño de tribunal, para "≥1 disidencia" y "sin mayoría absoluta".
Escribe secretarias_votacion.csv en el cache (una fila por caso con la clasificación).

Uso:
  python scripts/analisis/secretarias_votacion.py [--cache DIR] [--min 15]
"""
__version__ = "0.3"  # H221: excluye MIGRACION (marca de migración del sistema de SJ, no es secretaría; cubre casi todo 2006-2015) y unifica "Sec. Judicial Nº 2 - Previsional/Civil…" con "Sec. Judicial Nº 2" // 0.2 H221: + D. posiciones por juez dentro de cada secretaría · E. prueba chi² (cada secretaría vs resto) // 0.1 H221
import argparse, csv, json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)

RAIZ = Path(__file__).resolve().parents[2]
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"

def clasificar(posiciones):
    """(clase, n_tribunal, n_cabeza, n_disid). Clase según M67."""
    try: pos = json.loads(posiciones or "{}")
    except json.JSONDecodeError: return "sin_posiciones", 0, 0, 0
    if not pos: return "sin_posiciones", 0, 0, 0
    v = [str(x).lower() for x in pos.values()]
    n = len(v)
    cab = sum(1 for x in v if x == "mayoria")
    dis = sum(1 for x in v if "disidencia" in x)
    if dis == 0 and cab == n: return "unanime", n, cab, dis
    if cab == 0: return "sin_cabeza", n, cab, dis
    if cab >= n // 2 + 1: return "cabeza_con_mayoria_abs", n, cab, dis
    return "cabeza_sin_mayoria_abs", n, cab, dis

def juez_cat(p):
    p = str(p).lower()
    if "disidencia" in p: return "disidencia"
    if p == "mayoria": return "mayoria"
    return "voto"

def chi2_yates(a, b, c, d):
    """2x2 [[a,b],[c,d]]: (chi², p). p con 1 g.l. = erfc(sqrt(chi²/2))."""
    n = a + b + c + d
    r1, r2, c1, c2 = a + b, c + d, a + c, b + d
    if 0 in (r1, r2, c1, c2): return None, None
    x = n * max(0, abs(a * d - b * c) - n / 2) ** 2 / (r1 * r2 * c1 * c2)
    return x, math.erfc(math.sqrt(x / 2))

def secretaria_norm(s):
    """None para valores que no son secretaría; unifica nombres anteriores de la misma secretaría."""
    s = (s or "").strip()
    if not s or s.upper() == "MIGRACION": return None
    if s.startswith("Sec. Judicial Nº 2 -"): return "Sec. Judicial Nº 2"
    return s

def anio(fecha_sj, date_corpus):
    m = re.search(r"/(\d{4})$", fecha_sj or "") or re.search(r"de\s+(\d{4})", date_corpus or "")
    return int(m.group(1)) if m else None

def main():
    ap = argparse.ArgumentParser(description="votación por secretaría (M66/M67)")
    ap.add_argument("--cache", default=str(RAIZ / "scripts" / "diagnostico" / "sjconsulta"))
    ap.add_argument("--min", type=int, default=15, help="mínimo de casos para mostrar una celda")
    a = ap.parse_args()
    cache = Path(a.cache)
    src = cache / "casos_sjconsulta.csv"
    if not src.exists(): sys.exit(f"ERROR: falta {src}; correr antes scripts/analisis/unir_sjconsulta.py")

    casos = {r["caso_id_canonico"]: r for r in csv.DictReader(CASOS.open(encoding="utf-8", newline=""))}
    filas, excl = [], Counter()
    for s in csv.DictReader(src.open(encoding="utf-8", newline="")):
        c = casos.get(s["caso_id_canonico"])
        if not c or c.get("tipo_entrada") != "fallo": continue
        sec = secretaria_norm(s.get("secretaria"))
        if sec is None:
            excl[(s.get("secretaria") or "(vacío)").strip()] += 1; continue
        clase, n, cab, dis = clasificar(c.get("posiciones"))
        filas.append({
            "caso_id_canonico": s["caso_id_canonico"], "anio": anio(s.get("fecha_sj"), c.get("date")),
            "secretaria": sec,
            "merito": c.get("is_merit_decision") in ("1", "True", "true"),
            "clase": clase, "n_tribunal": n, "n_cabeza": cab, "n_disidencias": dis,
            "voting_pattern": c.get("voting_pattern"),
            "posiciones": c.get("posiciones") or "{}",
        })
    with (cache / "secretarias_votacion.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)

    mer = [f for f in filas if f["merito"]]
    print(f"secretarias_votacion v{__version__} · casos con secretaría {len(filas)} · de mérito {len(mer)}"
          f" · excluidos sin secretaría real {dict(excl)}")
    if filas:
        ys = sorted(f["anio"] for f in filas if f["anio"])
        print(f"  años con secretaría: {ys[0]}-{ys[-1]} · casos por año: "
              + " ".join(f"{y}:{n}" for y, n in sorted(Counter(f['anio'] for f in filas if f['anio']).items())))
    print(f"  clases (mérito): {dict(Counter(f['clase'] for f in mer))}\n")

    def linea(etq, grupo):
        n = len(grupo)
        if n < a.min: return None
        cnt = Counter(f["clase"] for f in grupo)
        con_dis = sum(1 for f in grupo if f["n_disidencias"] > 0)
        pct = lambda x: f"{x * 100 / n:5.1f}"
        return (f"  {etq:46s} {n:4d} · unán {pct(cnt['unanime'])} · ≥1 disid {pct(con_dis)}"
                f" · cabeza c/may.abs {pct(cnt['cabeza_con_mayoria_abs'])} · SIN may.abs {pct(cnt['cabeza_sin_mayoria_abs'] + cnt['sin_cabeza'])}")

    print(f"A. Solo decisiones de mérito, por secretaría (celdas con ≥{a.min} casos)")
    por_sec = defaultdict(list)
    for f in mer: por_sec[f["secretaria"]].append(f)
    for sec, g in sorted(por_sec.items(), key=lambda kv: -len(kv[1])):
        l = linea(sec[:46], g)
        if l: print(l)
    l = linea("TODAS", mer)
    if l: print(l)

    print(f"\nB. Mérito, por tamaño del tribunal y secretaría (el umbral de mayoría absoluta cambia con el tamaño)")
    for n in sorted({f["n_tribunal"] for f in mer}):
        g_n = [f for f in mer if f["n_tribunal"] == n]
        if len(g_n) < a.min: continue
        print(f" tribunal de {n} (mayoría absoluta = {n // 2 + 1}), {len(g_n)} casos")
        por = defaultdict(list)
        for f in g_n: por[f["secretaria"]].append(f)
        for sec, g in sorted(por.items(), key=lambda kv: -len(kv[1])):
            l = linea("   " + sec[:43], g)
            if l: print(l)

    print(f"\nC. Mérito, por año (todas las secretarías): n · % con disidencia · % sin mayoría absoluta · tamaño de tribunal más frecuente")
    por_a = defaultdict(list)
    for f in mer:
        if f["anio"]: por_a[f["anio"]].append(f)
    for y in sorted(por_a):
        g = por_a[y]; n = len(g)
        if n < a.min: continue
        sin = sum(1 for f in g if f["clase"] in ("cabeza_sin_mayoria_abs", "sin_cabeza"))
        dis = sum(1 for f in g if f["n_disidencias"] > 0)
        tam = Counter(f["n_tribunal"] for f in g).most_common(1)[0][0]
        print(f"  {y}: {n:4d} · {dis * 100 / n:5.1f} · {sin * 100 / n:5.1f} · {tam}")
    print(f"\nD. Mérito: posición de cada juez dentro de cada secretaría (jueces con ≥{a.min} participaciones)")
    print("   participaciones · % mayoría (voto de cabeza) · % voto propio/concurrente · % disidencia")
    for sec, g in sorted(por_sec.items(), key=lambda kv: -len(kv[1])):
        if len(g) < a.min: continue
        pj = defaultdict(Counter)
        for f in g:
            try: pos = json.loads(f["posiciones"])
            except json.JSONDecodeError: continue
            for j, v in pos.items(): pj[j][juez_cat(v)] += 1
        filas_j = [(j, c) for j, c in pj.items() if sum(c.values()) >= a.min]
        if not filas_j: continue
        print(f" {sec}")
        for j, c in sorted(filas_j, key=lambda x: -x[1]["disidencia"] / sum(x[1].values())):
            n = sum(c.values())
            print(f"   {j[:28]:28s} {n:4d} · {c['mayoria'] * 100 / n:5.1f} · {c['voto'] * 100 / n:5.1f} · {c['disidencia'] * 100 / n:5.1f}")

    print(f"\nE. Chi² con corrección de Yates, cada secretaría contra el resto (mérito, mismo tamaño de tribunal; celdas con ≥{a.min})")
    print("   p < 0,05 sugiere que la diferencia no es azar; con muchas comparaciones, mirar las de p muy chico")
    for n_t in sorted({f["n_tribunal"] for f in mer}):
        g_n = [f for f in mer if f["n_tribunal"] == n_t]
        if len(g_n) < 2 * a.min: continue
        print(f" tribunal de {n_t}")
        for etq, cond in (("≥1 disidencia", lambda f: f["n_disidencias"] > 0),
                          ("sin mayoría absoluta", lambda f: f["clase"] in ("cabeza_sin_mayoria_abs", "sin_cabeza"))):
            for sec in sorted({f["secretaria"] for f in g_n}):
                dentro = [f for f in g_n if f["secretaria"] == sec]
                fuera = [f for f in g_n if f["secretaria"] != sec]
                if len(dentro) < a.min: continue
                si_d = sum(1 for f in dentro if cond(f)); si_f = sum(1 for f in fuera if cond(f))
                x, pv = chi2_yates(si_d, len(dentro) - si_d, si_f, len(fuera) - si_f)
                if x is None: continue
                marca = " *" if pv < 0.05 else ""
                print(f"   {etq:20s} {sec[:34]:34s} {si_d * 100 / len(dentro):5.1f}% vs {si_f * 100 / len(fuera):5.1f}% · chi² {x:6.2f} · p {pv:.4f}{marca}")

    print(f"\nArchivo: {cache / 'secretarias_votacion.csv'}")
    print("Cautelas: la secretaría de SJ no está validada contra el trabajo de campo; las posiciones vienen del parser (B019 puede bajar el tamaño del tribunal; B177 cuenta la disidencia parcial como disidencia).")

if __name__ == "__main__":
    main()
