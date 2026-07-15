#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
derivar_materia.py — Frente B: deriva la variable `materia` del corpus CSJN.

Arquitectura (REE): NO muta csjn_casos.csv. Lee tablas primarias read-only y
escribe un sidecar keyed por `caso_id_canonico`, igual patron que
csjn_casos_votos / _zonas / _editorial. El analisis hace left-join 1:1.
Se re-corre y se refina por capa sin reparsear ni ensuciar el golden.

Capas de extraccion (orden = limpieza de senal):
  - Capa 1: tribunal_origen -> fuero -> materia (deterministica). SIN cambios.
    Solo fuero nacional/federal ESPECIALIZADO (tribunal == materia).
  - Capa 2 (H113-H114): para los casos que capa 1 deja en `pendiente_capa2`
    (provincial + SIN_TRIBUNAL, donde el tribunal NO desambigua), aplica
    VOCABULARIOS CONTROLADOS leidos de _meta/vocab_materia/. Cascada por
    limpieza de senal:
        norma citada -> keyword-ancla -> parte-ancla -> objeto-ancla
        -> (TIER 1 H114) Estado litigante en caratula => contencioso_administrativo
        -> sin_ancla.
    Vocab COMO DATO: se itera sin tocar este codigo.
    M59 (H209): el canal `norma citada` ya NO extrae del texto — CONSUME el
    sidecar csjn_casos_normas.csv (etapa previa extraer_normas.py), filtrado
    ambito=considerando AND tipo=ley: exactamente lo que RE_LEY extraia del
    considerando normalizado. Refactor byte-identico (candado sha de este
    sidecar, patron M52/H198). Los ambitos caratula/dispositivo/voto quedan
    EXTRAIDOS PERO INERTES para la cascada; habilitarlos = unidad propia con
    flip-set (M59 paso 2). RE_LEY vive ahora en extraer_normas.py.
  - Capa 3: originaria (art. 117). La determina el PARSER por texto
    (is_originaria via art.117 CN / "competencia originaria"); 1:1 con
    tribunal_origen_status=='originaria'. Por construccion ningun
    pendiente_capa2 es originaria, por eso el router Tier 1 NO intenta
    reclasificar a capa3 (seria contradecir una senal autoritativa upstream).

Vocabularios (autorados, versionados en git; NO se regeneran -> viven en _meta,
no en output/):
  _meta/vocab_materia/indice_normas.csv   (numero -> materia)
  _meta/vocab_materia/vocab_keywords.csv  (patron considerando -> materia, tier)
  _meta/vocab_materia/vocab_partes.csv    (patron caratula -> materia, tier)
Patrones en forma NORMALIZADA (sin acentos): el texto pasa por _norm antes de
matchear. Solo se usan filas tier=ancla (materia != EXCLUIDA). Los
desambiguadores y triggers se cargan pero los desambiguadores NO se aplican aun
(reglas de co-ocurrencia pendientes, ver DEUDA).

NOTA: capa 2 es ADITIVA — solo toca casos pendiente_capa2. NO refina capa 1.
Reclasificar capa 1 (p.ej. CA->tributario cuando la norma/parte lo indica:
~165 casos AFIP, ~77 por norma) es una decision DELIBERADA aparte, porque
cambia resultados de capa 1 y exige re-validacion. Ver DEUDA "refinamiento capa1".

Hallazgos que el diseno fija (H112-H113):
  - tributario / consumo / lesa_humanidad / cambiario NO son derivables de
    tribunal_origen (suben por CNACAF / van a fueros generales): son materias
    finas de capa 2, ancladas por norma/parte.
  - sui generis (Jurado de Enjuiciamiento, Consejo de la Magistratura) -> ruteo
    propio, taxonomia pendiente.
"""
from __future__ import annotations
import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

__version__ = "3.3"  # H209 (M59 paso 1): REFACTOR BYTE-IDENTICO — el canal norma de clasificar_capa2 deja de correr RE_LEY sobre el considerando y consume el sidecar csjn_casos_normas.csv (etapa previa extraer_normas.py; filtro ambito=considerando AND tipo=ley, doble filtro explicito para que ampliaciones futuras del sidecar no entren en silencio). RE_LEY movida a extraer_normas.py (unico consumidor historico). Candado: csjn_casos_materia.csv byte-identico (sha sellado H207), patron M52/H198. CLI nueva --normas. // 3.2 H115 TIER 3 motor de co-ocurrencia: vocab_coocurrencia.csv (reglas dato (A,B)->materia con excluye y ambito por senal); desambiguar_co_ocurrencia desempata conflicto_capa2 y rescata sin_ancla ANTES del trigger CA. Reglas: tributario_disfrazado, corralito_emergencia(->CA, gt14/14), accion_civil_accidente, indemniz_despido, danos_transito, salud_amparo. Relabel originaria (pendiente_capa3 -> 'originaria', categoria terminal; cobertura sobre universo clasificable=fallos-originaria). Familia->civil_comercial via objeto-anclas. // 3.1 H114 REFINAMIENTO CAPA1: override CA->tributario por autoridad fiscal. // 3.0 H114: TIER 1 router de partes -> CA + anclas. // 2.1 H113: capa objeto. // 2.0: capa 2 vocabularios ADITIVA. // H112: capa 1.

# csjn_casos_textos.csv tiene considerando_text completo (post-split #1). Subir
# el limite de campo csv a un valor amplio pero seguro en Windows.
csv.field_size_limit(10 ** 7)

# --- Rutas (resueltas respecto del script, robusto al cwd; overridables CLI) ---
SCRIPT_DIR = Path(__file__).resolve().parent           # .../scripts/pipeline
REPO_ROOT  = SCRIPT_DIR.parent.parent                  # raiz del repo
VOCAB_DIR_DEFAULT = REPO_ROOT / "_meta" / "vocab_materia"
DEFAULT_INPUT  = REPO_ROOT / "output" / "parser" / "csjn_casos.csv"
DEFAULT_TEXTOS = REPO_ROOT / "output" / "parser" / "csjn_casos_textos.csv"
DEFAULT_NORMAS = REPO_ROOT / "output" / "parser" / "csjn_casos_normas.csv"
DEFAULT_OUTPUT = REPO_ROOT / "output" / "parser" / "csjn_casos_materia.csv"

# Columnas requeridas (falla ruidoso si falta alguna).
REQUIRED_COLS    = ("caso_id_canonico", "tribunal_origen", "tribunal_origen_status",
                    "tipo_entrada", "case_name_cuerpo", "case_name_indice")
REQUIRED_TEXTOS  = ("caso_id_canonico", "considerando_text")
REQUIRED_NORMAS  = ("caso_id_canonico", "tipo", "norma", "ambito")

SENTINEL_SIN_TRIBUNAL = "SIN_TRIBUNAL_ORIGEN"


def _norm(s: str) -> str:
    """Deshace acentos + minusculas + colapsa espacios. Contrato de los patrones."""
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", s).lower().strip()


_RE_SOBRE = re.compile(r"\bs/\s*")

# Tier 1 (H114): "banco (de la) provincia" es una entidad bancaria, NO la
# provincia como litigante. Se enmascara antes de testear el trigger estatal
# para no rutear a CA falsos positivos (p.ej. "Banco de la Provincia de Bs As").
_RE_BANCO_PROV = re.compile(r"banco (?:de )?(?:la )?provincia")


def _objeto(caratula_norm: str) -> str:
    """Extrae el 's/ objeto' de la caratula NORMALIZADA (lo que sigue al ultimo s/)."""
    partes = _RE_SOBRE.split(caratula_norm)
    if len(partes) > 1:
        o = partes[-1].strip(" .,-")
        o = re.sub(r"\s+(recurso de hecho|recurso extraordinario).*$", "", o)
        return o[:60]
    return ""


# ============================================================================
# CAPA 1 — tribunal_origen -> fuero (SIN cambios respecto de v1.0)
# ============================================================================
REGLAS_CAPA1: list[tuple[str, list[str]]] = [
    ("laboral",                    [r"\bdel trabajo\b"]),
    ("previsional",                [r"seguridad social"]),
    ("contencioso_administrativo", [r"contencioso administrativo"]),
    ("penal",                      [r"casacion penal", r"criminal y correccional",
                                    r"penal economico", r"\ben lo penal\b",
                                    r"casacion en lo penal", r"oral en lo criminal",
                                    r"oral federal"]),
    ("tributario",                 [r"tribunal fiscal", r"fiscal de la nacion"]),
    ("civil_comercial",            [r"civil y comercial federal", r"\ben lo comercial\b",
                                    r"\ben lo civil\b", r"relaciones de consumo"]),
    ("electoral",                  [r"electoral"]),
]
_REGLAS = [(m, [re.compile(p) for p in pats]) for m, pats in REGLAS_CAPA1]

_RE_SUIGENERIS = re.compile(r"jurado de enjuiciamiento|consejo de la magistratura|"
                            r"tribunal de etica|tribunal de enjuiciamiento")
_RE_GENERAL = re.compile(
    r"suprema corte|corte suprema|superior tribunal|tribunal superior|"
    r"corte de justicia|tribunal de justicia|"
    r"camara federal|camara nacional de apelaciones|camara de apelaciones|"
    r"camara (en lo )?civil|camara del crimen|camara penal|camara contencioso|"
    r"juzgado|tribunal oral|jueza con funciones|juez ")


def clasificar_capa1(tribunal_origen: str, status: str, tipo_entrada: str
                     ) -> tuple[str, str, str]:
    """(materia, materia_capa, materia_fuente). Identica a v1.0."""
    if tipo_entrada != "fallo":
        return ("", "no_aplica", f"tipo_entrada={tipo_entrada}")
    if status == "originaria":
        # Categoria TERMINAL (no "pendiente"): competencia originaria art. 117 CN,
        # con secretaria propia; NO es universo de derivacion de materia. Se
        # reporta fuera del denominador de cobertura (universo clasificable).
        return ("", "originaria", "originaria")
    to = (tribunal_origen or "").strip()
    n = _norm(to)
    if to == SENTINEL_SIN_TRIBUNAL or n == "":
        return ("", "pendiente_capa2", "sin_tribunal")
    for materia, pats in _REGLAS:
        for p in pats:
            if p.search(n):
                return (materia, "capa1", f"regla:{p.pattern}")
    if _RE_SUIGENERIS.search(n):
        return ("", "sui_generis", to[:80])
    if _RE_GENERAL.search(n):
        return ("", "pendiente_capa2", "jurisdiccion_general")
    return ("", "residual", to[:80])


# ============================================================================
# REFINAMIENTO CAPA 1 (H114) — override CA -> tributario por autoridad fiscal
# ============================================================================
# DECISION DELIBERADA del usuario (anula la nota "fuera de alcance" del prompt):
# los casos capa1=contencioso_administrativo cuya caratula nombra una autoridad
# fiscal (AFIP/DGI/DGA nacional, ARBA/AGIP/DGR provincial — las parte-anclas que
# mapean a tributario) son tributario disfrazado de CA: AFIP/DGI suben por CNACAF
# y el tribunal los etiqueta CA, enmascarando la sustancia (hallazgo de tesis).
# Scope acotado y auditable:
#   - SOLO materia==contencioso_administrativo (las previsional/laboral/civil con
#     AFIP estan en su fuero por sustancia: aportes, concurso con AFIP acreedor;
#     NO se tocan).
#   - EXCLUYE co-ocurrencia penal (contrabando / ley penal tributaria 24.769):
#     esos son penal/penal_tributario, no tributario.
#   - Marca materia_capa='capa1_refinado' (NO 'capa1'): el override es visible y
#     contable, no muta silenciosamente capa1.
_RE_PENAL_FISCAL = re.compile(
    r"contrabando|ley penal tributaria|24\.?769|evasi[o]n (agravada|simple)|"
    r"asociaci[o]n il[i]cita")


def refinar_capa1(materia: str, capa: str, caratula: str, considerando: str,
                  partes_trib: list) -> tuple[str, str, str]:
    """Si capa1=CA y hay autoridad fiscal en caratula sin co-ocurrencia penal,
    override -> tributario (capa1_refinado). Si no, devuelve la entrada igual."""
    if capa != "capa1" or materia != "contencioso_administrativo":
        return (materia, capa, "")
    c = _norm(caratula)
    for rx in partes_trib:
        if rx.search(c):
            if _RE_PENAL_FISCAL.search(_norm(considerando)):
                return (materia, capa, "")  # contrabando/penal: no flip
            return ("tributario", "capa1_refinado", f"refinamiento:fiscal({rx.pattern[:18]})")
    return (materia, capa, "")


# ============================================================================
# CAPA 2 — vocabularios controlados (H113)
# ============================================================================
# M59 (H209): RE_LEY vivio aca (v2.0-v3.2) con un unico consumidor, el canal
# norma de clasificar_capa2. Movida VERBATIM a extraer_normas.py, que la corre
# como etapa previa del pipeline; esta capa consume su sidecar (ver derivar()).


def _leer_csv(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"[FATAL] falta vocabulario: {path}\n"
                 f"        (esperado en {VOCAB_DIR_DEFAULT} o --vocab-dir)")
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def cargar_vocabularios(vocab_dir: Path) -> dict:
    """Carga los tres vocabularios. Solo anclas (materia != EXCLUIDA) para
    clasificar; desambiguadores/triggers se separan."""
    indice = {r["numero"].strip(): r["materia"]
              for r in _leer_csv(vocab_dir / "indice_normas.csv")
              if r["tier"] == "ancla" and r["materia"] not in ("", "EXCLUIDA")}

    def _anclas(fname):
        return [(re.compile(r["patron"]), r["materia"])
                for r in _leer_csv(vocab_dir / fname)
                if r["tier"] == "ancla" and r["materia"] not in ("", "EXCLUIDA")]

    kw      = _anclas("vocab_keywords.csv")
    partes  = _anclas("vocab_partes.csv")
    objeto  = _anclas("vocab_objeto.csv")
    # provincia/Estado: NO ancla fina, dispara la pendiente CA/originaria.
    triggers = [re.compile(r["patron"])
                for r in _leer_csv(vocab_dir / "vocab_partes.csv")
                if r["tier"] == "trigger_ca_originaria"]
    # desambiguadores: cargados pero NO aplicados aun (co-ocurrencia pendiente).
    desambig = [(re.compile(r["patron"]), r["materia"])
                for r in _leer_csv(vocab_dir / "vocab_keywords.csv")
                if r["tier"] == "desambiguador"]
    # H115 TIER 3: reglas de co-ocurrencia como DATO. Cada regla es
    # (signal_a, signal_b, excluye?) -> materia, ordenadas por prioridad.
    # Una senal debil se vuelve ancla cuando co-ocurre con otra corroborante.
    coocur = []
    for r in _leer_csv(vocab_dir / "vocab_coocurrencia.csv"):
        if not r.get("materia") or r["materia"] in ("", "EXCLUIDA"):
            continue
        coocur.append({
            "nombre": r["nombre"],
            "a": re.compile(r["signal_a"]),
            "b": re.compile(r["signal_b"]),
            "excluye": re.compile(r["excluye"]) if r.get("excluye", "").strip() else None,
            "materia": r["materia"],
            "prioridad": int(r.get("prioridad") or 999),
            "ambito_a": (r.get("ambito_a") or "texto").strip(),
            "ambito_b": (r.get("ambito_b") or "texto").strip(),
        })
    coocur.sort(key=lambda d: d["prioridad"])
    return {"indice": indice, "kw": kw, "partes": partes, "objeto": objeto,
            "triggers": triggers, "desambig": desambig, "coocur": coocur,
            # subconjunto de parte-anclas que mapean a tributario: insumo del
            # refinamiento capa1 (autoridades fiscales AFIP/DGI/DGA/ARBA/AGIP/DGR).
            "partes_trib": [rx for rx, mat in partes if mat == "tributario"]}


def desambiguar_co_ocurrencia(caratula: str, considerando: str, vocab: dict
                              ) -> tuple[str, str]:
    """H115 TIER 3. Evalua las reglas de co-ocurrencia (vocab['coocur']) en orden
    de prioridad. Una regla dispara si signal_a Y signal_b co-ocurren en su
    `ambito` y NO matchea `excluye`. Devuelve (materia, nombre_regla) o ('', '').

    `ambito_a` / `ambito_b` por regla controlan DONDE se busca cada senal:
      - 'caratula'     -> solo en la caratula. Usado para senales que deben ser
                          litigante/objeto del caso, no menciones al pasar ni
                          CITAS DE PRECEDENTES en el considerando. P.ej.: la accion
                          declarativa de tributario_disfrazado debe ser la del caso
                          (caratula), no una caratula citada dentro del considerando
                          ('X c/ provincia s/ accion declarativa de inconst.'); y la
                          entidad de salud debe ser parte demandada.
      - 'considerando' -> solo en el considerando.
      - 'texto' (def.) -> caratula + considerando (el tributo de tributario_disfra-
                          zado puede estar en el considerando, por eso ambito_b=texto).

    Resuelve dos frentes que las anclas duras dejan abiertos:
      - empates de capa 2 (conflicto_capa2): se llama ANTES de devolver conflicto.
      - sin_ancla con objeto/considerando polisemico: ANTES del trigger CA.
    Reglas validadas (REE): precision contra GT capa1 donde aplica; spot-check
    donde el GT esta mudo (tributario via acc. declarativa, salud).
    """
    espacios = {"caratula": caratula, "considerando": considerando,
                "texto": f"{caratula} {considerando}"}
    for regla in vocab["coocur"]:
        scope_a = espacios.get(regla["ambito_a"], espacios["texto"])
        scope_b = espacios.get(regla["ambito_b"], espacios["texto"])
        if regla["a"].search(scope_a) and regla["b"].search(scope_b):
            if regla["excluye"] is not None and regla["excluye"].search(
                    espacios["texto"]):
                continue
            return (regla["materia"], regla["nombre"])
    return ("", "")


def clasificar_capa2(considerando: str, caratula: str, vocab: dict,
                     normas: set[str]) -> tuple[str, str, str]:
    """(materia, materia_capa, materia_fuente) para un caso pendiente_capa2.
    Cascada: norma -> keyword-ancla -> parte-ancla -> provincia -> sin_ancla.
    Regla de empate: voto dominante; empate real -> conflicto (queda pendiente).

    `normas` (M59): normas citadas en el CONSIDERANDO del caso, leidas del
    sidecar csjn_casos_normas.csv (ambito=considerando, tipo=ley) — el mismo
    conjunto que RE_LEY extraia del considerando normalizado hasta v3.2.
    sorted() = higiene deterministica; el output es orden-independiente por
    construccion (fuentes y empates se serializan con sorted, ganador sin
    empate unico)."""
    t = _norm(considerando)
    c = _norm(caratula)
    votos: Counter = Counter()
    fuente_de: dict[str, list[str]] = {}

    for num in sorted(normas):
        mat = vocab["indice"].get(num)
        if mat:
            votos[mat] += 1
            fuente_de.setdefault(mat, []).append(f"norma:{num}")
    for rx, mat in vocab["kw"]:
        if rx.search(t):
            votos[mat] += 1
            fuente_de.setdefault(mat, []).append("kw")
    for rx, mat in vocab["partes"]:
        if rx.search(c):
            votos[mat] += 1
            fuente_de.setdefault(mat, []).append("parte")
    obj = _objeto(c)
    if obj:
        for rx, mat in vocab["objeto"]:
            if rx.search(obj):
                votos[mat] += 1
                fuente_de.setdefault(mat, []).append("objeto")

    if votos:
        top = votos.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            # EMPATE: antes de declararlo conflicto, intentar desempate por
            # co-ocurrencia (TIER 3 H115). Resuelve p.ej. CA/tributario y
            # constitucional/tributario (tributario disfrazado), civil/laboral.
            mat_co, regla_co = desambiguar_co_ocurrencia(c, t, vocab)
            if mat_co:
                return (mat_co, "capa2", f"coocur:{regla_co}(desempate)")
            empate = "/".join(sorted(m for m, n in top if n == top[0][1]))
            return ("", "pendiente_capa2", f"conflicto_capa2:{empate}")
        mat = top[0][0]
        fuentes = "+".join(sorted(set(fuente_de[mat])))
        return (mat, "capa2", f"{fuentes}({top[0][1]})")

    # SIN anclas duras: TIER 3 H115 — co-ocurrencia ANTES del trigger CA, para
    # que amparo+salud o acc.declarativa+tributo ganen al generico Estado->CA.
    mat_co, regla_co = desambiguar_co_ocurrencia(c, t, vocab)
    if mat_co:
        return (mat_co, "capa2", f"coocur:{regla_co}")

    # TIER 1 (H114): relacion de partes -> contencioso_administrativo.
    # El parser ya separo competencia originaria por TEXTO (is_originaria via
    # art. 117 CN / "competencia originaria"): is_originaria==1 <=> capa3, 477/477.
    # Por construccion NINGUN pendiente_capa2 es originaria, asi que la rama
    # "estado c/ estado -> originaria" del diseno contradeciria una senal
    # autoritativa del parser. Resolucion: si hay un Estado como litigante en la
    # caratula (y no es "banco (de la) provincia"), el caso es CA. Las anclas
    # finas (norma/kw/parte/objeto) ya corrieron antes, de modo que el tributario
    # provincial (ingresos brutos, sellos, codigo fiscal, ejecucion fiscal) se
    # extrae ANTES de este barrido. REE: robusto (no parsea el fragil "X c/ Y"),
    # se apoya en la deteccion de originaria del parser.
    c_estado = _RE_BANCO_PROV.sub(" ", c)
    for rx in vocab["triggers"]:
        if rx.search(c_estado):
            return ("contencioso_administrativo", "capa2", "provincia:ca")
    return ("", "pendiente_capa2", "sin_ancla")


# ============================================================================
# Orquestacion
# ============================================================================
def derivar(input_path: Path, textos_path: Path, normas_path: Path,
            output_path: Path, vocab_dir: Path) -> dict:
    if not input_path.exists():
        sys.exit(f"[FATAL] no existe el input: {input_path}")
    with input_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {input_path}: {faltan}")
        filas = list(reader)

    # considerando completo desde el sidecar de textos (post-split #1).
    if not textos_path.exists():
        sys.exit(f"[FATAL] no existe el sidecar de textos: {textos_path}")
    with textos_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_TEXTOS if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {textos_path}: {faltan}")
        considerandos = {r["caso_id_canonico"]: r["considerando_text"] for r in rd}

    # M59: normas citadas desde el sidecar de la etapa previa extraer_normas.
    # DOBLE FILTRO explicito (ambito AND tipo): cuando el sidecar sume filas
    # nuevas (decretos, ambito dictamen...), NO entran a la cascada en silencio
    # — habilitarlas es una unidad propia con flip-set.
    if not normas_path.exists():
        sys.exit(f"[FATAL] no existe el sidecar de normas: {normas_path}\n"
                 f"        (correr antes scripts/pipeline/extraer_normas.py — "
                 f"etapa M59, ver MAPA.md)")
    normas_cons: dict[str, set[str]] = {}
    with normas_path.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        faltan = [c for c in REQUIRED_NORMAS if c not in (rd.fieldnames or [])]
        if faltan:
            sys.exit(f"[FATAL] faltan columnas en {normas_path}: {faltan}")
        for r in rd:
            if r["ambito"] == "considerando" and r["tipo"] == "ley":
                normas_cons.setdefault(r["caso_id_canonico"], set()).add(r["norma"])

    vocab = cargar_vocabularios(vocab_dir)

    salida = []
    cobertura: Counter = Counter()
    materias1: Counter = Counter()
    materias2: Counter = Counter()
    pend2_motivo: Counter = Counter()
    _vacio: set[str] = set()
    for r in filas:
        cid = r["caso_id_canonico"]
        caratula = f'{r.get("case_name_cuerpo","")} {r.get("case_name_indice","")}'
        materia, capa, fuente = clasificar_capa1(
            r["tribunal_origen"], r["tribunal_origen_status"], r["tipo_entrada"])

        if capa == "capa1":
            # Refinamiento H114: CA -> tributario por autoridad fiscal.
            materia, capa, fref = refinar_capa1(
                materia, capa, caratula, considerandos.get(cid, ""),
                vocab["partes_trib"])
            if fref:
                fuente = fref
        elif capa == "pendiente_capa2":
            materia, capa, fuente = clasificar_capa2(
                considerandos.get(cid, ""), caratula, vocab,
                normas_cons.get(cid, _vacio))

        salida.append({
            "caso_id_canonico": cid,
            "materia": materia,
            "materia_capa": capa,
            "materia_fuente": fuente,
        })
        cobertura[capa] += 1
        if capa == "capa1":
            materias1[materia] += 1
        elif capa == "capa1_refinado":
            materias1[materia] += 1
        elif capa == "capa2":
            materias2[materia] += 1
        elif capa == "pendiente_capa2":
            pend2_motivo[fuente.split(":")[0]] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["caso_id_canonico", "materia", "materia_capa",
                            "materia_fuente"],
            lineterminator="\n")
        writer.writeheader()
        writer.writerows(salida)

    return {"n": len(salida), "cobertura": cobertura,
            "materias1": materias1, "materias2": materias2,
            "pend2_motivo": pend2_motivo}


def _reporte(stats: dict, fallos: int) -> None:
    cov = stats["cobertura"]
    originaria = cov.get("originaria", 0)
    clasificable = fallos - originaria
    print(f"\n  derivar_materia v{__version__}")
    print(f"  filas escritas: {stats['n']}  (fallos: {fallos})")
    print(f"  originaria (terminal, fuera del denominador): {originaria}")
    print(f"  universo clasificable (fallos - originaria): {clasificable}")
    clasificadas = (cov.get("capa1", 0) + cov.get("capa1_refinado", 0)
                    + cov.get("capa2", 0))
    if clasificable:
        print(f"  COBERTURA: {clasificadas}/{clasificable} = "
              f"{100*clasificadas/clasificable:.1f}%")
    print("\n  === cobertura (capas) ===")
    orden = ["capa1", "capa1_refinado", "capa2", "pendiente_capa2",
             "originaria", "sui_generis", "residual", "no_aplica"]
    for k in orden:
        v = cov.get(k, 0)
        base = clasificable if k in ("capa1", "capa1_refinado", "capa2",
                                     "pendiente_capa2") else fallos
        if k == "no_aplica":
            base = stats["n"]
        pct = f"({100*v/base:5.1f}%)" if base else ""
        print(f"    {k:18s} {v:5d}  {pct}")
    print("\n  === materia capa 1 (tribunal) ===")
    for m, v in sorted(stats["materias1"].items(), key=lambda kv: -kv[1]):
        print(f"    {m:30s} {v:5d}")
    print("\n  === materia capa 2 (vocabularios) ===")
    for m, v in sorted(stats["materias2"].items(), key=lambda kv: -kv[1]):
        print(f"    {m:30s} {v:5d}")
    print("\n  === pendiente_capa2 por motivo ===")
    for m, v in sorted(stats["pend2_motivo"].items(), key=lambda kv: -kv[1]):
        print(f"    {m:30s} {v:5d}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deriva materia capas 1-2 (sidecar).")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                    help=f"tabla primaria (default: {DEFAULT_INPUT})")
    ap.add_argument("--textos", type=Path, default=DEFAULT_TEXTOS,
                    help=f"sidecar de textos, considerando (default: {DEFAULT_TEXTOS})")
    ap.add_argument("--normas", type=Path, default=DEFAULT_NORMAS,
                    help=f"sidecar de normas citadas, M59 (default: {DEFAULT_NORMAS})")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                    help=f"sidecar de salida (default: {DEFAULT_OUTPUT})")
    ap.add_argument("--vocab-dir", type=Path, default=VOCAB_DIR_DEFAULT,
                    help=f"vocabularios controlados (default: {VOCAB_DIR_DEFAULT})")
    args = ap.parse_args(argv)

    stats = derivar(args.input, args.textos, args.normas, args.output,
                    args.vocab_dir)
    fallos = stats["n"] - stats["cobertura"].get("no_aplica", 0)
    _reporte(stats, fallos)
    print(f"\n  -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
