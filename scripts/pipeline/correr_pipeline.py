#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
correr_pipeline.py — orquestador de la cadena canónica (corpus-csjn, M42).
==========================================================================

Corre la cadena parser → derivers → gate de regresión → manifest en el ORDEN
del DAG de MAPA.md (la spec; este script es su implementación), con las
invocaciones cableadas VERBATIM desde la CLI real de cada etapa (leídas H179,
no reconstruidas). Mata la clase de errores de H174/H178: invocación de
memoria, secuencia que sigue tras un fallo, golden congelado sin refrescar
producción, manifest fuera de orden.

Alcance v1.1 (H179 + M59/H209): parser → extraer_epilogos → derivar_partes →
extraer_normas → derivar_materia → derivar_recursos → check_regresion →
manifest. Las etapas UPSTREAM (construir_catalogo / detectar_paginas /
cruzar_catalogo_y_mapa) quedan FUERA del ejecutable v1 (sus CLIs no se
leyeron; zonas ⚠ en MAPA.md): se corren a mano según MAPA.md §orden 1-3, en
sesión propia. El pre-flight detecta corpus-drift (.md en corpus/ ausentes
del universo source_file de csjn_casos.csv — misma derivación que
fuentes_corpus() de generar_manifiesto) y ABORTA: la cadena v1 nunca corre
"limpia" sobre un catálogo que no vio esos archivos.

Invariantes cableados (lecciones H178):
  (a) FAIL-FAST total: returncode != 0 en cualquier etapa → abort inmediato
      con el estado documentado. Nada sigue tras un fallo.
  (b) Versiones: pre-flight lee __version__ de los 11 módulos de la cadena
      (el Select-String que salvó H178, cableado) + pin opcional --esperar.
      Post-etapa: frescura de outputs (existe + mtime >= arranque de etapa).
  (c) golden == producción: assert final por sha256 de los 5 CSV del parser
      (scripts/tests/golden/ vs output/parser/) en TODA corrida. El freno
      del PoC POST de H178, permanente.
  (d) Cero paths adivinados: constantes desde REPO_ROOT (patrón __file__ de
      generar_manifiesto), existencia verificada en pre-flight.

Modos:
  --plan            imprime la secuencia exacta (comandos verbatim, paths
                    verificados, tabla de versiones) SIN ejecutar nada.
  (default)         reproducción/verificación: cadena completa a producción;
                    check_regresion debe dar [CLEAN] o aborta ANTES del
                    manifest; assert (c); manifest --verify (re-sella solo
                    si --verify falla: la decisión sello-vs-verify deja de
                    ser de memoria).
  --solo-derivers   saltea el parser (epilogos → partes → normas → materia →
                    recursos → gate → manifest).
  --consciente      post-fix deliberado: tolera [FAIL] del check, imprime
                    el diff y FRENA (exit 3) SIN tocar golden ni manifest.
                    La adjudicación es humana y previa a congelar nada.
  --regolden        tras adjudicar: check_regresion --make-golden + assert
                    (c) (si producción quedó stale vs el golden recién
                    congelado, los hashes difieren → aborta: el incidente
                    H178-2 es imposible por construcción) + re-sello +
                    --verify.
  --esperar         pin de versiones "parser=24.0,clasificador_disposicion=1.15"
                    → mismatch aborta (hojas de ruta sin placeholders).
  --ignorar-corpus-drift  permite correr con .md no incorporados (caso
                    legítimo: tomo aún no procesado a propósito).

Contrato con las herramientas existentes (Gate 3 — invoca, no duplica):
check_regresion.py corre el parser a TEMP y adjudica vs golden (exit 0/1/2);
generar_manifiesto.py sella (sin flag) y verifica (--verify). El orquestador
solo ordena, frena y verifica.

Infra de salida: PYTHONUTF8=1 en el env de cada subprocess (mata la clase
charmap de H174 para TODA la cadena sin tocar los hijos) + errors="replace"
en el stdout propio (patrón parser v23.2).

Exit codes: 0 OK · 1 etapa/gate falló · 2 abort de pre-flight ·
3 frenado para adjudicación (--consciente con [FAIL] esperado).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

__version__ = "1.1"  # H209 (M59 paso 1): etapa extraer_normas cableada entre derivar_partes y derivar_materia (que gana --normas); NORMAS constante; VERSION_FILES 10->11 modulos. // 1.0 H179 (M42): orquestador inicial. Alcance parser→derivers→gate→manifest; upstream fuera (v2 cuando haya tomos nuevos reales). Invariantes (a)-(d) del docstring. Validado reproduciendo el sello H178 en 0 cambios.

# El orquestador imprime → sujeto a la misma clase charmap que el parser
# (H174): degradar a '?' antes que morir por un print, en cualquier entorno.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass

csv.field_size_limit(10 ** 7)  # source_file se lee de casos.csv (campos grandes)

# ── Rutas: constantes desde REPO_ROOT (patrón generar_manifiesto, robusto al
#    cwd). Espejan MAPA.md; NINGUNA se adivina en runtime. ──────────────────
SCRIPT_DIR = Path(__file__).resolve().parent          # scripts/pipeline/
REPO_ROOT  = SCRIPT_DIR.parent.parent                 # raíz del repo
PIPELINE   = SCRIPT_DIR
TESTS      = REPO_ROOT / "scripts" / "tests"
GOLDEN_DIR = TESTS / "golden"
OUT_DIR    = REPO_ROOT / "output" / "parser"
CORPUS     = REPO_ROOT / "corpus"
LOCALIZADOS = REPO_ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA_PAG    = REPO_ROOT / "output" / "mapa" / "mapa_paginas.csv"
VOCAB_DIR   = REPO_ROOT / "_meta" / "vocab_materia"

CHECK_REGRESION   = TESTS / "check_regresion.py"
GENERAR_MANIFIESTO = PIPELINE / "generar_manifiesto.py"

CASOS    = OUT_DIR / "csjn_casos.csv"
TEXTOS   = OUT_DIR / "csjn_casos_textos.csv"
VOTOS    = OUT_DIR / "csjn_casos_votos.csv"
ZONAS    = OUT_DIR / "csjn_casos_zonas.csv"
EDITORIAL = OUT_DIR / "csjn_casos_editorial.csv"
EPILOGO  = OUT_DIR / "csjn_casos_epilogo.csv"
PARTES   = OUT_DIR / "csjn_casos_partes.csv"
NORMAS   = OUT_DIR / "csjn_casos_normas.csv"   # M59 (H209)
MATERIA  = OUT_DIR / "csjn_casos_materia.csv"
RECURSOS = OUT_DIR / "csjn_casos_recursos.csv"

# Los 5 CSV del harness (espejo de check_regresion.OUTPUTS): el invariante (c)
# se afirma sobre ESTOS, golden vs producción.
PARSER_CSVS = [CASOS, TEXTOS, VOTOS, ZONAS, EDITORIAL]

PY = sys.executable

# ── Etapas: (nombre, comando verbatim, outputs esperados) ────────────────────
# Comandos cableados desde la CLI REAL de cada script (leída H179; etapa
# extraer_normas leída H209). Nota: las flags NO son uniformes (--out en
# recursos, --input en materia) a propósito: verbatim, no normalizado.
# cwd=PIPELINE en todas (el parser lo requiere para
# `from parser_editorial import ...`; extraer_normas importa derivar_materia
# con sys.path propio; a los derivers, que resuelven por __file__, no los
# afecta).
ETAPA_PARSER = ("parser", [
    PY, str(PIPELINE / "parser.py"),
    "--localizados", str(LOCALIZADOS),
    "--mapa", str(MAPA_PAG),
    "--corpus", str(CORPUS),
    "--output", str(CASOS),
], PARSER_CSVS)

ETAPAS_DERIVERS = [
    ("extraer_epilogos", [
        PY, str(PIPELINE / "extraer_epilogos.py"),
        "--zonas", str(ZONAS),
        "--casos", str(CASOS),
        "--corpus-dir", str(CORPUS),
        "--output", str(EPILOGO),
    ], [EPILOGO]),
    ("derivar_partes", [
        PY, str(PIPELINE / "derivar_partes.py"),
        "--casos", str(CASOS),
        "--epilogo", str(EPILOGO),
        "--output", str(PARTES),
    ], [PARTES]),
    # M59 (H209): extractor canónico de normas citadas — ANTES de materia,
    # que consume su sidecar (ambito=considerando).
    ("extraer_normas", [
        PY, str(PIPELINE / "extraer_normas.py"),
        "--casos", str(CASOS),
        "--textos", str(TEXTOS),
        "--votos", str(VOTOS),
        "--output", str(NORMAS),
    ], [NORMAS]),
    ("derivar_materia", [
        PY, str(PIPELINE / "derivar_materia.py"),
        "--input", str(CASOS),
        "--textos", str(TEXTOS),
        "--normas", str(NORMAS),
        "--output", str(MATERIA),
        "--vocab-dir", str(VOCAB_DIR),
    ], [MATERIA]),
    ("derivar_recursos", [
        PY, str(PIPELINE / "derivar_recursos.py"),
        "--casos", str(CASOS),
        "--textos", str(TEXTOS),
        "--out", str(RECURSOS),          # sic: --out, no --output
    ], [RECURSOS]),
]

CMD_CHECK       = [PY, str(CHECK_REGRESION)]
CMD_MAKE_GOLDEN = [PY, str(CHECK_REGRESION), "--make-golden"]
CMD_SELLO       = [PY, str(GENERAR_MANIFIESTO)]
CMD_VERIFY      = [PY, str(GENERAR_MANIFIESTO), "--verify"]

# ── Versiones: los módulos cuyo __version__ describe el estado de la cadena.
#    check_regresion.py no declara __version__ (verificado H179) → "—". ──────
VERSION_FILES = {
    "parser":                   PIPELINE / "parser.py",
    "extraer_epilogos":         PIPELINE / "extraer_epilogos.py",
    "derivar_partes":           PIPELINE / "derivar_partes.py",
    "extraer_normas":           PIPELINE / "extraer_normas.py",   # M59 (H209)
    "derivar_materia":          PIPELINE / "derivar_materia.py",
    "derivar_recursos":         PIPELINE / "derivar_recursos.py",
    "clasificador_disposicion": PIPELINE / "clasificador_disposicion.py",
    "clasificador_via":         PIPELINE / "clasificador_via.py",
    "clasificador_admision":    PIPELINE / "clasificador_admision.py",
    "clasificador_causa":       PIPELINE / "clasificador_causa.py",
    "generar_manifiesto":       GENERAR_MANIFIESTO,
}

RE_VERSION = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']', re.M)


def leer_version(path: Path) -> str | None:
    try:
        m = RE_VERSION.search(path.read_text(encoding="utf-8"))
        return m.group(1) if m else None
    except OSError:
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def abort(msg: str, code: int = 2):
    print(f"\n[ABORT] {msg}")
    sys.exit(code)


# ── Pre-flight ───────────────────────────────────────────────────────────────

def preflight(args) -> dict[str, str | None]:
    """Verifica paths, lee versiones, aplica pins y detecta corpus-drift.
    Devuelve la tabla de versiones. Aborta (exit 2) ante cualquier desvío."""
    print(f"correr_pipeline v{__version__} — repo: {REPO_ROOT}")

    # (d) existencia de TODO lo que la corrida toca, antes de invocar nada.
    requeridos = [CHECK_REGRESION, GENERAR_MANIFIESTO, CORPUS, VOCAB_DIR,
                  LOCALIZADOS, MAPA_PAG] + list(VERSION_FILES.values())
    if args.solo_derivers or args.regolden:
        # los derivers consumen la salida del parser; --regolden asume
        # producción ya refrescada por la corrida --consciente previa.
        requeridos += [CASOS, TEXTOS, VOTOS, ZONAS]
    faltan = [p for p in requeridos if not p.exists()]
    if faltan:
        print("[pre-flight] paths faltantes:")
        for p in faltan:
            print(f"   {p}")
        abort("no se invoca nada con paths faltantes (invariante d).")

    # (b) tabla de versiones en disco.
    versiones: dict[str, str | None] = {n: leer_version(p)
                                        for n, p in VERSION_FILES.items()}
    print("\n[pre-flight] versiones en disco:")
    for n, v in versiones.items():
        print(f"   {n:26s} {v or '—'}")
    print(f"   {'check_regresion':26s} — (sin __version__, verificado H179)")

    # pin opcional --esperar.
    if args.esperar:
        pines = {}
        for par in args.esperar.split(","):
            if "=" not in par:
                abort(f"--esperar malformado: {par!r} (formato nombre=version)")
            k, v = (t.strip() for t in par.split("=", 1))
            if k not in VERSION_FILES:
                abort(f"--esperar: {k!r} no es un módulo de la cadena "
                      f"(válidos: {', '.join(VERSION_FILES)})")
            pines[k] = v
        malos = [(k, v, versiones.get(k)) for k, v in pines.items()
                 if versiones.get(k) != v]
        if malos:
            for k, esp, real in malos:
                print(f"[pin] {k}: esperado {esp}, en disco {real}")
            abort("pin de versión no coincide (invariante b).")
        print(f"[pre-flight] pins OK: {pines}")

    # corpus-drift: .md en disco no presentes en el universo source_file del
    # casos.csv vigente (misma derivación que fuentes_corpus() del manifiesto).
    en_disco = {p.name for p in CORPUS.glob("*.md")}
    if not CASOS.exists():
        if not args.ignorar_corpus_drift:
            abort("no hay csjn_casos.csv previo: drift de corpus no "
                  "verificable. Si es intencional, --ignorar-corpus-drift.")
        print("[pre-flight] WARN: sin casos.csv previo, drift no verificable "
              "(--ignorar-corpus-drift activo).")
    else:
        sellados: set[str] = set()
        with CASOS.open(encoding="utf-8", newline="") as f:
            for fila in csv.DictReader(f):
                sf = (fila.get("source_file") or "").strip()
                if sf:
                    sellados.add(sf)
        drift = sorted(en_disco - sellados)
        if drift:
            print(f"\n[CORPUS-DRIFT] {len(drift)} .md en corpus/ fuera del "
                  f"universo source_file vigente:")
            for n in drift[:20]:
                print(f"   {n}")
            if len(drift) > 20:
                print(f"   ... (+{len(drift) - 20})")
            if not args.ignorar_corpus_drift:
                abort("la cadena v1 NO regenera catálogo/mapa/cruce. Correr "
                      "upstream a mano (MAPA.md §orden 1-3) en sesión propia, "
                      "o --ignorar-corpus-drift si la exclusión es deliberada.")
            print("   (--ignorar-corpus-drift activo: se continúa.)")
    return versiones


# ── Ejecución de etapas ──────────────────────────────────────────────────────

def correr(cmd: list[str], nombre: str) -> int:
    """Corre un comando con cwd=PIPELINE y PYTHONUTF8=1, streaming directo."""
    print(f"\n[run:{nombre}] {' '.join(cmd)}")
    env = dict(os.environ, PYTHONUTF8="1")
    r = subprocess.run(cmd, cwd=str(PIPELINE), env=env)
    return r.returncode


def etapa(nombre: str, cmd: list[str], outputs: list[Path]):
    """(a) fail-fast + (b) frescura post-etapa. Aborta con estado documentado."""
    t0 = time.time()
    rc = correr(cmd, nombre)
    if rc != 0:
        abort(f"etapa '{nombre}' salió con código {rc}. La secuencia NO "
              f"continúa. Estado: etapas previas ya escribieron a producción; "
              f"golden y manifest NO tocados.", 1)
    frios = [p for p in outputs
             if not p.exists() or p.stat().st_mtime < t0 - 1]
    if frios:
        for p in frios:
            print(f"   [frescura] {p.name}: "
                  f"{'NO existe' if not p.exists() else 'mtime anterior a la etapa'}")
        abort(f"etapa '{nombre}' terminó 0 pero no refrescó su output "
              f"(clase H178-1: 'corrió pero no era / no escribió').", 1)
    print(f"[ok:{nombre}] {len(outputs)} output(s) frescos "
          f"({time.time() - t0:.1f}s)")


def assert_golden_eq_prod():
    """(c) golden == producción, sha256 sobre los 5 CSV del parser."""
    print("\n[invariante c] golden == producción (sha256, 5 CSV del parser):")
    malos = []
    for p in PARSER_CSVS:
        g = GOLDEN_DIR / p.name
        if not g.exists() or not p.exists():
            malos.append((p.name, "falta " + ("golden" if not g.exists() else "producción")))
            continue
        hg, hp = sha256(g), sha256(p)
        estado = "OK" if hg == hp else "DIFIERE"
        print(f"   {p.name:28s} golden {hg[:12]}  prod {hp[:12]}  [{estado}]")
        if hg != hp:
            malos.append((p.name, "hash distinto"))
    if malos:
        abort("golden != producción — ciclo incompleto (clase H178-2). "
              "NO se sella. Adjudicar: ¿--make-golden corrido fuera del "
              "orquestador, o producción stale?", 1)
    print("   [CLEAN] invariante golden==producción sostenido.")


def gate_manifest():
    """Sello condicional: --verify primero (read-only); si falla, re-sella y
    re-verifica. La decisión sello-vs-verify deja de ser de memoria."""
    rc = correr(CMD_VERIFY, "manifest --verify")
    if rc == 0:
        print("[manifest] [CLEAN] sin cambios → no se re-sella.")
        return
    print("[manifest] verify falló (esperado si la corrida cambió canónicos) "
          "→ re-sellando…")
    if correr(CMD_SELLO, "manifest sello") != 0:
        abort("generar_manifiesto (sello) falló.", 1)
    if correr(CMD_VERIFY, "manifest --verify (post-sello)") != 0:
        abort("manifest --verify falló INMEDIATAMENTE después del sello: "
              "algo mutó los canónicos entre sello y verify.", 1)
    print("[manifest] re-sellado y verificado [CLEAN].")


# ── Plan (dry-run) ───────────────────────────────────────────────────────────

def plan(args):
    secuencia = []
    if args.regolden:
        secuencia = [("check_regresion --make-golden", CMD_MAKE_GOLDEN),
                     ("assert golden==producción", None),
                     ("manifest (verify → sello condicional)", CMD_VERIFY)]
    else:
        if not args.solo_derivers:
            secuencia.append((ETAPA_PARSER[0], ETAPA_PARSER[1]))
        secuencia += [(n, c) for n, c, _ in ETAPAS_DERIVERS]
        secuencia += [("check_regresion (gate)", CMD_CHECK),
                      ("assert golden==producción", None),
                      ("manifest (verify → sello condicional)", CMD_VERIFY)]
    print("\n[PLAN] secuencia exacta (nada se ejecuta):")
    for i, (n, c) in enumerate(secuencia, 1):
        print(f"\n  {i}. {n}")
        if c:
            print(f"     {' '.join(c)}")
    print("\n[PLAN] upstream FUERA del alcance v1 (correr a mano, MAPA.md "
          "§orden 1-3): construir_catalogo → detectar_paginas → "
          "cruzar_catalogo_y_mapa.")
    print("[PLAN] fin del dry-run: 0 comandos ejecutados.")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="M42 — orquestador de la cadena canónica (MAPA.md como spec).")
    ap.add_argument("--plan", action="store_true",
                    help="imprime la secuencia exacta sin ejecutar nada")
    ap.add_argument("--solo-derivers", action="store_true",
                    help="saltea el parser (epilogos→partes→normas→materia→recursos)")
    ap.add_argument("--consciente", action="store_true",
                    help="tolera [FAIL] del check: imprime el diff y frena "
                         "(exit 3) sin tocar golden ni manifest")
    ap.add_argument("--regolden", action="store_true",
                    help="tras adjudicar un --consciente: make-golden + "
                         "assert hashes + re-sello")
    ap.add_argument("--esperar", metavar="PINS",
                    help='pin de versiones, ej. "parser=24.0,clasificador_disposicion=1.15"')
    ap.add_argument("--ignorar-corpus-drift", action="store_true",
                    help="continuar aunque haya .md fuera del universo sellado")
    args = ap.parse_args()

    if args.regolden and (args.solo_derivers or args.consciente):
        abort("--regolden es un modo propio: no se combina con "
              "--solo-derivers ni --consciente.")

    preflight(args)

    if args.plan:
        plan(args)
        return 0

    if args.regolden:
        t0 = time.time()
        rc = correr(CMD_MAKE_GOLDEN, "check_regresion --make-golden")
        if rc != 0:
            abort(f"--make-golden salió con código {rc}.", 1)
        frios = [p.name for p in PARSER_CSVS
                 if not (GOLDEN_DIR / p.name).exists()
                 or (GOLDEN_DIR / p.name).stat().st_mtime < t0 - 1]
        if frios:
            abort(f"--make-golden no refrescó: {', '.join(frios)}", 1)
        assert_golden_eq_prod()          # el candado anti-H178-2
        gate_manifest()
        print("\n[FIN] ciclo re-golden completo: golden congelado, "
              "invariante (c) sostenido, manifest verificado.")
        return 0

    # ── corrida normal / --solo-derivers ──
    if not args.solo_derivers:
        etapa(*ETAPA_PARSER)
    for e in ETAPAS_DERIVERS:
        etapa(*e)

    rc = correr(CMD_CHECK, "check_regresion (gate)")
    if rc == 2:
        abort("check_regresion abortó por infra (código 2): revisar paths/golden.", 1)
    if rc == 1:
        if not args.consciente:
            abort("check_regresion [REGRESION] y la corrida NO es --consciente. "
                  "Estado: producción refrescada, golden viejo, manifest NO "
                  "resellado. Si el cambio es deliberado: adjudicar el diff de "
                  "arriba y correr --consciente / --regolden; si no, revertir "
                  "el fix y re-correr.", 1)
        print("\n[CONSCIENTE] check [FAIL] tolerado como esperado. El diff quedó "
              "impreso arriba. FRENO acá: golden y manifest NO tocados.")
        print("  Siguiente paso tras adjudicar el diff:  correr_pipeline.py --regolden")
        return 3
    print("[gate] check_regresion [CLEAN].")

    assert_golden_eq_prod()
    gate_manifest()
    print("\n[FIN] cadena completa: etapas OK, gate [CLEAN], invariante (c) "
          "sostenido, manifest verificado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
