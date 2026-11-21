"""cruce_sjconsulta.py — cruce de posiciones juez×fallo: corpus vs sjconsulta (M66, H221)

Segundo codificador externo: la base de sumarios de la Secretaría de Jurisprudencia
(sjconsulta.csjn.gov.ar). Read-only respecto del pipeline: lee output/parser/csjn_casos.csv
y escribe solo en el directorio de cache (por defecto scripts/diagnostico/sjconsulta/,
gitignoreado: los JSON de sjconsulta son datos locales, no se versionan).

Uso:
  python scripts/validacion/cruce_sjconsulta.py AAAA [--cache DIR]

Por cada mes del año: baja los sumarios (reusa sj_AAAAMM_limpio.json si existe; si el mes
entero falla, reintenta en dos quincenas), cruza por tomo+página y compara la posición de
cada juez titular. Escribe posiciones_AAAA.csv en el cache e imprime matriz y discrepancias.

Equivalencia (medida en H221): el primer bloque UNANIMIDAD o VOTO CONJUNTO = mayoría (sin
ninguno de los dos, nadie es mayoría); otros bloques no disidentes = según su voto;
DISIDENCIA* = en disidencia. Diferencia de DEFINICIÓN conocida: el corpus llama "mayoria" al
voto que encabeza aunque tenga una sola firma (342_p761/1061/1665); SJ lo codifica VOTO
PROPIO (ver M67). Excluye fallos con CONJUECES en SJ (bloque genérico, 342_p1847).

Capa funcionarial (v0.3, decisión del operador H221): se guardan, por sumario, por análisis y por
cada elemento cargado (voces, cuestiones federales, normas, votos…), el código de usuario, el
nombre, el cargo y las fechas de carga/modificación de los funcionarios que intervinieron. NO se
guardan CUIL (nombreUsuario) ni mail. Uso: análisis de la tesis; anonimizar en toda exposición.
Endpoint no documentado: puede cambiar sin aviso.
Historia: H221 sj_mes/sj_anio v0.1-v0.2 en scripts/diagnostico/H221/ (scratch).
"""
__version__ = "0.3"  # H221 (cierre): capa funcionarial (código/nombre/cargo/fechas de carga, sin CUIL ni mail) + cache _v03 + reintento por semanas y por página // 0.2 H221: promovido desde diagnostico/H221/sj_anio_v02.py (regla 340_p257 + reintento por quincenas)
import argparse
import csv, http.cookiejar, json, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
csv.field_size_limit(2**31 - 1)
RAIZ = Path(__file__).resolve().parents[2]
_ap = argparse.ArgumentParser(description="cruce corpus × sjconsulta (M66)")
_ap.add_argument("anio", type=int)
_ap.add_argument("--cache", default=str(RAIZ / "scripts" / "diagnostico" / "sjconsulta"))
_args = _ap.parse_args()
ANIO = _args.anio
AQUI = Path(_args.cache); AQUI.mkdir(parents=True, exist_ok=True)
CASOS = RAIZ / "output" / "parser" / "csjn_casos.csv"
B = "https://sjconsulta.csjn.gov.ar/sjconsulta"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) corpus-csjn/sondeo (investigacion academica)"
PAUSA = 1.5
MESES = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,"julio":7,"agosto":8,
         "septiembre":9,"setiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
RF = re.compile(r"(\d{1,2})\s*[°º]?\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})", re.I)

def fecha(s):
    m = RF.search(s or "")
    if m and m.group(2).lower() in MESES:
        return datetime(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1)))

def norm(n):
    n = unicodedata.normalize("NFKD", n or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", n).strip()

def val(o): return o.get("valor") if isinstance(o, dict) else None

CAMPOS_USR = ("usuarioCreacion", "usuarioModificacion", "usuarioCreacionOld",
              "usuarioModificacionOld", "usuarioControl", "usuarioControlOld", "usuarioMod")
CAMPOS_FECHA = ("fechaCreacion", "fechaModificacion", "fechaControl")
LISTAS_AN = ("voces", "cuestionesFederales", "referenciasNormativas", "formulas", "recusExcus",
             "enlaces", "materias", "votosAnalisisDocumental", "votosSumario")

def usr(u):
    """Funcionario sin CUIL ni mail: código si viene como string; código/apellido/nombre/cargo si dict."""
    if isinstance(u, dict):
        return {k: u.get(k) for k in ("codigo", "apellido", "nombre", "cargo", "estado")}
    return u

def huella(o):
    """Usuarios y fechas de carga de un objeto (solo los campos presentes y no nulos)."""
    if not isinstance(o, dict): return {}
    h = {k: usr(o[k]) for k in CAMPOS_USR if o.get(k)}
    h.update({k: o[k] for k in CAMPOS_FECHA if o.get(k)})
    return h

def funcionarial(r):
    a = r.get("analisisDocumental") or {}
    rec = a.get("reciboEntrada") or {}
    out = {"sumario": huella(r), "analisis": huella(a),
           "recibo": {"codigoUsuario": rec.get("codigoUsuario"), "fecha": rec.get("fechaString")}}
    for lista in LISTAS_AN:
        items = [huella(x) for x in a.get(lista) or []]
        items = [x for x in items if x]
        if items: out[lista] = items
    return out

def limpiar(r):
    a = r.get("analisisDocumental") or {}
    rec = a.get("reciboEntrada") or {}
    return {"id_sumario": r.get("id"), "id_fallo": r.get("idFallo"), "tomo": r.get("tomo"),
            "pagina": r.get("pagina"), "fecha": r.get("fechaString"),
            "autos": r.get("autos") or r.get("caratulaWeb"), "expediente": r.get("numeroExpediente"),
            "sentencia_arbitraria": r.get("sentenciaArbitraria"), "inconstitucional": r.get("inconstitucional"),
            "voces": r.get("voces"), "texto": r.get("texto"),
            "citado_por": [c.get("aliasWeb") for c in r.get("citasRex") or []],
            "an_presente": bool(a), "an_destacado": bool(a.get("falloDestacado")),
            "an_secretaria": (rec.get("secretaria") or {}).get("descripcion"),
            "an_fecha_entrada": rec.get("fechaString"), "an_sentido": val(a.get("sentidoPronunciamiento")),
            "an_tipo_recurso": val(a.get("tipoRecurso")), "an_materia": val(a.get("materiaSecretaria")),
            "an_votos": [{"tipo": (v.get("tipoVoto") or {}).get("descripcion"),
                          "ministros": [x.get("descripcion") for x in v.get("ministros") or []]}
                         for v in a.get("votosAnalisisDocumental") or []],
            "funcionarial": funcionarial(r)}

def descargar(anio, mes, d1=1, d2=None):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    op.open(f"{B}/consultaSumarios/consulta.html", timeout=20).read(); time.sleep(PAUSA)
    d = urllib.parse.urlencode({"filter.fullText": "", "filter.autos": "", "filter.fechaExacta": "",
        "filter.fechaDesde": f"{d1:02d}/{mes:02d}/{anio}",
        "filter.fechaHasta": f"{(d2 or monthrange(anio, mes)[1]):02d}/{mes:02d}/{anio}"}).encode()
    html = op.open(urllib.request.Request(f"{B}/consultaSumarios/buscar.html", data=d, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{B}/consultaSumarios/consulta.html"}), timeout=60).read().decode("utf-8", "replace")
    m = re.search(r'totalResultados\s*=\s*"(\d+)"', html)
    if not m: raise RuntimeError(f"{mes:02d}/{anio}: sin totalResultados")
    total, regs = int(m.group(1)), []
    while len(regs) < total:
        p = None
        for intento in range(3):   # v0.3: reintento por página (respuestas truncadas, 05/2023)
            time.sleep(PAUSA * (1 + 2 * intento))
            try:
                p = json.loads(op.open(urllib.request.Request(
                    f"{B}/consultaSumarios/paginarSumarios.html?startIndex={len(regs)}",
                    headers={"X-Requested-With": "XMLHttpRequest"}), timeout=60).read().decode("utf-8"))
                break
            except (json.JSONDecodeError, TimeoutError, urllib.error.URLError):
                if intento == 2: raise
        if not p: break
        regs += [limpiar(x) for x in p]
    print(f"  {mes:02d}/{anio} [{d1}-{d2 or 'fin'}]: total declarado {total} · descargados {len(regs)}")
    return regs

def cargar_mes(anio, mes):
    cache = AQUI / f"sj_{anio}{mes:02d}_v03.json"
    if cache.exists():
        regs = json.loads(cache.read_text(encoding="utf-8"))
        print(f"  {mes:02d}/{anio}: cache {cache.name} · {len(regs)}")
        return regs
    fin = monthrange(anio, mes)[1]
    niveles = [("mes", [(1, fin)]), ("quincenas", [(1, 15), (16, fin)]),
               ("semanas", [(1, 7), (8, 14), (15, 21), (22, fin)])]
    regs, ultimo = None, None
    for nombre, tramos in niveles:   # v0.3: mes → quincenas → semanas
        try:
            acum, vistos = [], set()
            for d1, d2 in tramos:
                for r in descargar(anio, mes, d1, d2):
                    if r["id_sumario"] not in vistos:
                        vistos.add(r["id_sumario"]); acum.append(r)
            regs = acum; break
        except Exception as e:
            ultimo = e
            print(f"  {mes:02d}/{anio}: falló por {nombre} ({e!r})")
    if regs is None: raise ultimo
    cache.write_text(json.dumps(regs, ensure_ascii=False, indent=1), encoding="utf-8")
    return regs

def pos_sj(votos):
    """dict juez_norm -> categoria, segun la equivalencia medida."""
    out, cabeza = {}, None
    for i, v in enumerate(votos):
        t = norm(v["tipo"])
        # v0.2: solo un bloque UNANIMIDAD o VOTO CONJUNTO puede ser mayoria (340_p257)
        if ("UNANIMIDAD" in t or "CONJUNTO" in t) and "DISIDENCIA" not in t and cabeza is None:
            cabeza = i
    for i, v in enumerate(votos):
        t = norm(v["tipo"])
        if "PARCIAL" in t and "DISIDENCIA" in t: cat = "disid_parcial"
        elif "DISIDENCIA" in t: cat = "disidencia"
        elif "ABSTENCION" in t: cat = "abstencion"
        elif i == cabeza: cat = "mayoria"
        else: cat = "voto"
        for mnz in v["ministros"]: out[norm(mnz)] = cat
    return out

def cat_corpus(p):
    p = norm(p).lower()
    if "disidencia parcial" in p: return "disid_parcial"
    if "disidencia" in p: return "disidencia"
    if "segun su voto" in p: return "voto"
    if "mayoria" in p: return "mayoria"
    return "otro:" + p

def main():
    print(f"cruce_sjconsulta v{__version__} · año {ANIO} · cache {AQUI}\n")
    regs = []
    for mes in range(1, 13):
        try: regs += cargar_mes(ANIO, mes)
        except Exception as e: print(f"  {mes:02d}/{ANIO}: ERROR {e!r}")
    pf = defaultdict(list)
    for r in regs: pf[r["id_fallo"]].append(r)
    casos = list(csv.DictReader(CASOS.open(encoding="utf-8", newline="")))
    idx = {tuple(map(int, c["caso_id_canonico"].split("_p"))): c for c in casos}

    tipos, sin_par, con_conj, sin_votos = Counter(), [], [], []
    jueces_mal, pos_mal, celdas, filas = [], [], Counter(), []
    n_cruce = 0
    for idf, ss in pf.items():
        s = ss[0]
        for v in s["an_votos"]: tipos[v["tipo"]] += 1
        c = idx.get((s["tomo"], s["pagina"])) if s["tomo"] else None
        if not c: sin_par.append(s); continue
        n_cruce += 1
        if any("CONJUE" in norm(m) for v in s["an_votos"] for m in v["ministros"]):
            con_conj.append(c["caso_id_canonico"]); continue
        if not s["an_votos"]:
            sin_votos.append(c["caso_id_canonico"]); continue
        sj = pos_sj(s["an_votos"])
        try: co_raw = json.loads(c["posiciones"] or "{}")
        except json.JSONDecodeError: co_raw = {}
        co = {norm(k): cat_corpus(v) for k, v in co_raw.items()}
        if set(sj) != set(co):
            jueces_mal.append((c["caso_id_canonico"], sorted(set(sj) - set(co)), sorted(set(co) - set(sj))))
        difs = []
        for j in sorted(set(sj) & set(co)):
            celdas[(sj[j], co[j])] += 1
            if sj[j] != co[j]: difs.append(f"{j}: SJ={sj[j]} CO={co[j]}")
        if difs: pos_mal.append((c, s, difs))
        filas.append({"caso_id_canonico": c["caso_id_canonico"], "sj_votos":
                      " ; ".join(f"{v['tipo']}: {', '.join(v['ministros'])}" for v in s["an_votos"]),
                      "posiciones_corpus": c["posiciones"], "voting_pattern": c["voting_pattern"],
                      "jueces_coinciden": set(sj) == set(co), "difs": " | ".join(difs)})

    print(f"\nSumarios {len(regs)} · fallos SJ {len(pf)} · con par en corpus {n_cruce} · sin par {len(sin_par)}"
          f" (de esos, sin tomo: {sum(1 for s in sin_par if not s['tomo'])})")
    for s in [s for s in sin_par if s["tomo"]][:20]:
        print(f"  SIN PAR CON TOMO {s['tomo']}:{s['pagina']} · {s['fecha']} · {(s['autos'] or '')[:55]}")
    print(f"Excluidos: conjueces {len(con_conj)} {con_conj[:10]} · sin bloque de votos {len(sin_votos)} {sin_votos[:10]}")
    print(f"Tipos de voto SJ: {dict(tipos)}")
    comparados = len(filas)
    print(f"\nFallos comparados: {comparados}")
    print(f"  conjunto de jueces distinto: {len(jueces_mal)}")
    for cid, a, b in jueces_mal[:25]: print(f"    {cid} · solo SJ {a} · solo corpus {b}")
    print(f"  fallos con alguna posición distinta: {len(pos_mal)}")
    tot = sum(celdas.values()); ok = sum(n for (a, b), n in celdas.items() if a == b)
    print(f"\nPosiciones juez×fallo comparadas: {tot} · coinciden {ok} ({(ok / tot * 100 if tot else 0):.1f}%)")
    print("  Matriz SJ × corpus:")
    for (a, b), n in sorted(celdas.items(), key=lambda kv: -kv[1]):
        print(f"    {n:5d} · SJ={a:13s} CO={b}")
    print("\nDiscrepancias de posición (detalle, hasta 40):")
    for c, s, difs in pos_mal[:40]:
        print(f"  {c['caso_id_canonico']} · {c['voting_pattern']}\n     SJ: "
              + " ; ".join(f"{v['tipo']}: {', '.join(v['ministros'])}" for v in s["an_votos"])
              + f"\n     DIF: {' | '.join(difs)}")

    del_anio = [c for c in casos if (d := fecha(c["date"])) and d.year == ANIO]
    claves = {(v[0]["tomo"], v[0]["pagina"]) for v in pf.values() if v[0]["tomo"]}
    sin = [c for c in del_anio if tuple(map(int, c["caso_id_canonico"].split("_p"))) not in claves]
    print(f"\nCobertura: corpus {ANIO} (fecha parseable) = {len(del_anio)} · con sumario {len(del_anio) - len(sin)} · sin {len(sin)}")
    print(f"  tipo_entrada sin sumario: {dict(Counter(c['tipo_entrada'] for c in sin))}")
    for c in sin[:30]:
        print(f"  {c['caso_id_canonico']} · {c['date']} · merit={c['is_merit_decision']} · {c['outcome']} · {c['case_name_indice'][:50]}")

    out = AQUI / f"posiciones_{ANIO}.csv"
    if filas:
        with out.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0])); w.writeheader(); w.writerows(filas)
    print(f"\nArchivo: {out.name}")

if __name__ == "__main__":
    main()
