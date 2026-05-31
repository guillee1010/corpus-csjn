#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PoC B103 -- guard EXCL en el bloque DEPOSITO de clasificar_causa_inadmisibilidad.

Problema (DEUDA_TECNICA B103, ABIERTO): 330_p1025 y 343_p166 quedan etiquetados
DEPOSITO_PREVIO siendo FP. En ambos la frase del deposito describe una resolucion
ANTERIOR de la Corte ("la resolucion de fs. X que desestimo la queja en razon de
no haberse efectuado el deposito"); lo que el fallo decide es una revocatoria/
planteo CONTRA esa resolucion, no un gate de deposito sobre el recurso presente.
Mismo discriminador holding-vs-antecedente que B100/B101, pero el bloque DEPOSITO
no tiene guard. TP control: 340_p225, 348_p805.

Fix propuesto: guard RE_CAUSA_DEPOSITO_EXCL anclado al considerando (co),
sumado como '... and not EXCL' a la condicion del bloque DEPOSITO.

Metodologia (M15): A/B OLD vs NEW sobre TEXTO IDENTICO (no OLD-truncado vs
NEW-completo). Este PoC corre dos capas:
  (1) A/B broad sobre las 5862 filas usando considerando_text/por_ello_text del
      CSV. Mismo texto en ambos lados -> aisla el patch. Confirma que el unico
      efecto del guard son las 2 celdas esperadas (sin cascada).
  (2) Anti-M15: verifica que los considerandos afectados NO estan truncados a
      2000 (len < 2000) -> el texto del CSV == texto completo de produccion, no
      hay riesgo de veredicto-dado-vuelta. Si alguno estuviera truncado, aborta
      y remite a extraer_caso.py para validar sobre el .md completo.

Ademas reusa las regex de PRODUCCION (import desde parser.py): el unico literal
local es RE_CAUSA_DEPOSITO_EXCL. La capa (1) prueba de paso que clasif_NEW es una
copia fiel de produccion + guard, porque sobre las 5860 filas no-flip debe
coincidir EXACTO con la clasificar_causa_inadmisibilidad real.

No toca produccion. No escribe nada. Solo lee CSV + importa parser.
Esperado: DEPOSITO_PREVIO 4->2; SIN_CAUSAL 413->415; gate total 1036 sin cambio.
"""
import csv
import re
import sys
from pathlib import Path

# --- localizar raiz del repo por marcador (estilo extraer_caso.py) -----------
def _hallar_raiz(inicio: Path) -> Path:
    for d in (inicio, *inicio.parents):
        if (d / ".git").exists() or (d / "README.md").exists():
            return d
    return inicio

RAIZ = _hallar_raiz(Path(__file__).resolve())
CSV_PATH = RAIZ / "output" / "parser" / "csjn_casos.csv"
PARSER_DIR = RAIZ / "scripts" / "pipeline"

# permite correr el PoC desde la copia subida (CSV junto al script) como fallback
if not CSV_PATH.exists():
    aqui = Path(__file__).resolve().parent
    if (aqui / "csjn_casos.csv").exists():
        CSV_PATH = aqui / "csjn_casos.csv"
    if (aqui / "parser.py").exists():
        PARSER_DIR = aqui

sys.path.insert(0, str(PARSER_DIR))
import parser as P  # noqa: E402

# --- import de las regex/constantes de PRODUCCION (cero drift de literales) ---
clasif_OLD = P.clasificar_causa_inadmisibilidad
_unhyph = P._unhyphenate
OUTCOME_A_CAUSA = P.OUTCOME_A_CAUSA
OUTCOMES_GATE_GENERICO = P.OUTCOMES_GATE_GENERICO
RE_SD = P.RE_CAUSA_SENTENCIA_DEFINITIVA
RE_FUND = P.RE_CAUSA_FUNDAMENTACION
RE_DEP = P.RE_CAUSA_DEPOSITO
RE_FUERA = P.RE_CAUSA_FUERA_TERMINO
RE_FUERA_EXCL = P.RE_CAUSA_FUERA_TERMINO_EXCL
RE_FUERA_EXCL_DISP = P.RE_CAUSA_FUERA_TERMINO_EXCL_DISP
RE_NORE = P.RE_CAUSA_NO_RECURRIBLE
RE_NORE_EXCL = P.RE_CAUSA_NO_RECURRIBLE_EXCL
RE_REMITE = P.RE_CAUSA_REMITE_DICTAMEN

# --- UNICO literal nuevo: el guard candidato B103 ----------------------------
RE_CAUSA_DEPOSITO_EXCL = re.compile(
    r"la\s+resoluci[oó]n\s+de\s+fs\.?\s*\d+[\s,]+que\s+desestim[oó]\b"
    r".{0,80}?no\s+haberse\s+(?:efectuad|integrad|abonad|acreditad|cumplid)\w*"
    r"\s+(?:con\s+)?el\s+dep[oó]sito", re.I)


def clasif_NEW(outcome, considerando_text, por_ello_text, dictamen_presente):
    """Copia fiel de produccion + guard B103 en el bloque DEPOSITO."""
    if outcome in OUTCOME_A_CAUSA:
        return OUTCOME_A_CAUSA[outcome]
    if outcome not in OUTCOMES_GATE_GENERICO and outcome != "otro":
        return ""
    co = re.sub(r"\s+", " ", _unhyph(considerando_text)).strip()
    pe = re.sub(r"\s+", " ", _unhyph(por_ello_text)).strip()
    txt = co + " || " + pe
    if outcome in OUTCOMES_GATE_GENERICO:
        if RE_SD.search(txt):
            return "FALTA_SENTENCIA_DEFINITIVA"
        if RE_FUND.search(txt):
            return "FALTA_FUNDAMENTACION_AUTONOMA"
        if RE_DEP.search(txt) and not RE_CAUSA_DEPOSITO_EXCL.search(co):  # B103
            return "DEPOSITO_PREVIO"
        if (RE_FUERA.search(txt)
                and not RE_FUERA_EXCL.search(txt)
                and not RE_FUERA_EXCL_DISP.search(pe)):
            return "FUERA_DE_TERMINO"
        if RE_NORE.search(co) and not RE_NORE_EXCL.search(pe):
            return "RESOLUCION_NO_RECURRIBLE"
    if outcome == "otro":
        return ""
    if (RE_REMITE.search(co)
            and str(dictamen_presente).strip().lower() in ("true", "1", "presente")):
        return "INADMISIBLE_REMITE_DICTAMEN"
    return "INADMISIBLE_SIN_CAUSAL_EXPLICITA"


FLIPS_ESPERADOS = {"330_p1025", "343_p166"}
TPS_CONTROL = {"340_p225", "348_p805"}      # deben quedar DEPOSITO_PREVIO
TRUNC = 2000                                # corte que aplica el parser al CSV
CORPUS_DIR = RAIZ / "corpus"


def _texto_completo_md(row):
    """Reconstruye el bloque completo del .md (sin truncar), un-hyphenated y
    colapsado, como superset del considerando. Mismo metodo que extraer_caso.py
    v2.0: source_file + rango [linea_inicio, linea_fin_real], reusando
    construir_bloque_desde_localizacion del parser. None si no hay corpus."""
    md = CORPUS_DIR / row["source_file"]
    if not md.exists():
        return None
    lines = md.read_text(encoding="utf-8").splitlines()
    fin = row.get("linea_fin_real") or row.get("linea_fin")
    bloque = P.construir_bloque_desde_localizacion(
        lines, int(row["linea_inicio"]), int(fin))
    return re.sub(r"\s+", " ", _unhyph(" ".join(bloque))).strip()


def main():
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    if not CSV_PATH.exists():
        sys.exit(f"[ABORT] no encuentro el CSV en {CSV_PATH}")
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"PoC B103  |  parser v{P.__version__}  |  {CSV_PATH}")
    print(f"filas: {len(rows)}")

    # --- (2) anti-M15: fidelidad sobre TEXTO COMPLETO del .md -----------------
    # El A/B broad corre sobre considerando_text del CSV (truncado a 2000). Para
    # cualquier caso DEPOSITO con considerando >=2000 no podemos descartar desde
    # el CSV que la formula EXCL aparezca pasado el corte. Reconstruimos el
    # bloque completo del .md y exigimos: EXCL presente en los 2 FP, AUSENTE en
    # los TP. (block superset del considerando: 'no en block' => 'no en co'.)
    afectados = {r["caso_id_canonico"]: r for r in rows
                 if r["caso_id_canonico"] in (FLIPS_ESPERADOS | TPS_CONTROL)
                 or r["causa_inadmisibilidad"] == "DEPOSITO_PREVIO"}
    print("\n[anti-M15] EXCL sobre texto COMPLETO del .md (universo DEPOSITO):")
    sin_corpus, fidelidad_ok = [], True
    for cid in sorted(afectados):
        r = afectados[cid]
        n = len(r["considerando_text"])
        full = _texto_completo_md(r)
        if full is None:
            sin_corpus.append(cid)
            print(f"   {cid:14} CSV_len={n}  (sin corpus: no verificable aca)")
            continue
        excl = bool(RE_CAUSA_DEPOSITO_EXCL.search(full))
        esperado = cid in FLIPS_ESPERADOS
        ok = (excl == esperado)
        fidelidad_ok = fidelidad_ok and ok
        print(f"   {cid:14} CSV_len={n} EXCL_full={excl} esperado={esperado} "
              f"[{'ok' if ok else 'FAIL'}]")
    if sin_corpus:
        print(f"   AVISO: sin corpus/ no se verifico texto completo de {sin_corpus}; "
              f"correr en el repo o validar con extraer_caso.py.")

    # --- (1) A/B OLD vs NEW sobre TEXTO IDENTICO (CSV) ------------------------
    # OJO M15: clasif sobre considerando_text del CSV (truncado a 2000) NO
    # reproduce el golden para causales cuyo ancla cae pasado el corte (p.ej.
    # REMITE_DICTAMEN). Por eso NO comparamos contra la columna golden aca; el
    # A/B es OLD(texto) vs NEW(texto): el truncado afecta IGUAL a ambos lados,
    # asi que la comparacion aisla limpio el efecto del guard. El guard solo
    # vive dentro del bloque DEPOSITO y solo SACA -> su universo de efecto esta
    # contenido en los casos DEPOSITO_PREVIO del golden (no puede agregar).
    golden_dep = {r["caso_id_canonico"] for r in rows
                  if r["causa_inadmisibilidad"] == "DEPOSITO_PREVIO"}
    diffs = []
    for r in rows:
        a = clasif_OLD(r["outcome"], r["considerando_text"],
                       r["por_ello_text"], r["dictamen_presente"])
        b = clasif_NEW(r["outcome"], r["considerando_text"],
                       r["por_ello_text"], r["dictamen_presente"])
        if a != b:
            diffs.append((r["caso_id_canonico"], a, b))

    print(f"\n[A/B] celdas que cambian OLD->NEW (texto identico): {len(diffs)}")
    for cid, a, b in sorted(diffs):
        print(f"   {cid:14} {a} -> {b}")

    cambiados = {c for c, _, _ in diffs}
    ok_set = cambiados == FLIPS_ESPERADOS
    ok_origen = all(a == "DEPOSITO_PREVIO" for _, a, _ in diffs)
    ok_destino = all(b == "INADMISIBLE_SIN_CAUSAL_EXPLICITA" for _, _, b in diffs)
    ok_universo = cambiados <= golden_dep
    print(f"   universo de cambios ⊆ DEPOSITO_PREVIO del golden: {ok_universo}")

    # --- (1b) destino fiel: los 2 FP NO estan truncados -> CSV == texto real --
    # Para que el destino (->SIN_CAUSAL) sea fiel a produccion, el texto del CSV
    # de los flips debe ser el completo (no truncado). 330/343 miden 1117/1412.
    flips_truncados = [c for c in FLIPS_ESPERADOS
                       if len({r["caso_id_canonico"]: r for r in rows}[c]
                              ["considerando_text"]) >= TRUNC]
    ok_flip_fiel = not flips_truncados
    if not ok_flip_fiel:
        print(f"   AVISO: flip(s) con considerando truncado {flips_truncados}: "
              f"validar destino sobre .md completo.")

    # --- conteos: delta derivado del GOLDEN + los flips verificados ----------
    # (no de re-correr clasif sobre CSV truncado, que falsea REMITE & co.)
    from collections import Counter
    g = Counter(r["causa_inadmisibilidad"] or "(vacio)" for r in rows)
    print("\n[conteos] golden -> esperado (aplicando los flips verificados):")
    print(f"   DEPOSITO_PREVIO                  "
          f"{g['DEPOSITO_PREVIO']} -> {g['DEPOSITO_PREVIO'] - len(diffs)}")
    print(f"   INADMISIBLE_SIN_CAUSAL_EXPLICITA "
          f"{g['INADMISIBLE_SIN_CAUSAL_EXPLICITA']} -> "
          f"{g['INADMISIBLE_SIN_CAUSAL_EXPLICITA'] + len(diffs)}")
    gate_golden = sum(v for k, v in g.items() if k != "(vacio)")
    print(f"   gate total: {gate_golden} -> {gate_golden} (sin cambio; flip dentro del gate)")

    print("\n--- VEREDICTO ---")
    print(f"  flips == esperados (330_p1025, 343_p166): {ok_set}")
    print(f"  origen DEPOSITO_PREVIO / destino SIN_CAUSAL: {ok_origen and ok_destino}")
    print(f"  universo de cambios ⊆ DEPOSITO del golden: {ok_universo}")
    print(f"  destino fiel (flips no truncados): {ok_flip_fiel}")
    print(f"  EXCL fiel sobre texto completo del .md: "
          f"{'(no verificado: faltaba corpus)' if sin_corpus else fidelidad_ok}")
    core = ok_set and ok_origen and ok_destino and ok_universo and ok_flip_fiel
    if sin_corpus:
        print(f"  [INCOMPLETO] PoC B103 -- core {'ok' if core else 'FAIL'}; "
              f"correr en el repo (con corpus/) para cerrar el chequeo de texto completo")
        sys.exit(2)
    limpio = core and fidelidad_ok
    print(f"  [{'CLEAN' if limpio else 'FAIL'}] PoC B103")
    sys.exit(0 if limpio else 1)


if __name__ == "__main__":
    main()
