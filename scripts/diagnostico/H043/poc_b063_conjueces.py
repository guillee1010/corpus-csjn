"""
PoC B063 -- Conjueces faltantes en JUECES_CONOCIDOS.

Flujo:
  1. Verifica que parser.py sea el original (sin marcadores B063).
  2. Copia parser.py -> parser_b063.py en el mismo directorio.
  3. Patchea la copia con 9 conjueces nuevos.
  4. Corre pipeline con la copia, output a output/parser/b063/.
  5. Compara CSVs campo por campo.
  6. Limpia la copia.

Uso (desde raíz del repo):
  python scripts/diagnostico/H043/poc_b063_conjueces.py

Requiere que existan los CSVs de la corrida anterior (baseline).
"""

import re
import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from collections import Counter

# ── Rutas (relativas a raíz del repo) ───────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent.parent  # H043 -> diagnostico -> scripts -> ROOT
PARSER_ORIG = ROOT / "scripts" / "pipeline" / "parser.py"
PARSER_B063 = ROOT / "scripts" / "pipeline" / "parser_b063.py"

BASELINE_CASOS = ROOT / "output" / "parser" / "csjn_casos.csv"
BASELINE_VOTOS = ROOT / "output" / "parser" / "csjn_casos_votos.csv"

OUTPUT_DIR = ROOT / "output" / "parser" / "b063"
OUTPUT_CASOS = OUTPUT_DIR / "csjn_casos.csv"
OUTPUT_VOTOS = OUTPUT_DIR / "csjn_casos_votos.csv"

LOCALIZADOS = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS = ROOT / "corpus"

# ── Marcador de integridad ──────────────────────────────────────────────────
MARCADOR_B063 = "Conjueces B063"
# SHA-256 del parser.py pre-H043 (commit e258f66, post-H042)
# Nota: hash sobre bytes crudos del disco (LF, según git autocrlf).
HASH_ESPERADO = "a3466bb17ee6a9e4faa4d461a7919d39e9edeb3574307fbacddffbf10b8e7d83"

# ── Patch data ──────────────────────────────────────────────────────────────
NUEVOS_CONJUECES = """    # ── Conjueces B063 (H043) ───────────────────────────────────────────────
    (re.compile(r"mar[íi]a\\s+susana\\s+najurieta", re.I),                    "Najurieta (conjuez)"),
    (re.compile(r"roc[íi]o\\s+alcal[áa]", re.I),                            "Alcalá (conjuez)"),
    (re.compile(r"jorge\\s+eduardo\\s+mor[áa]n\\.?", re.I),                   "Morán (conjuez)"),
    (re.compile(r"mirta\\s+(d\\.?|delia)\\s+tyden(?:\\s+de\\s+skanata)?", re.I), "Tyden de Skanata (conjuez)"),
    (re.compile(r"juan\\s+carlos\\s+poclava\\s+lafuente", re.I),              "Poclava Lafuente (conjuez)"),
    (re.compile(r"carlos\\s+m\\.?\\s*pereira\\s+gonz[áa]lez", re.I),           "Pereira González (conjuez)"),
    (re.compile(r"jorge\\s+ferro", re.I),                                    "Ferro (conjuez)"),
    (re.compile(r"antonio\\s+pacilio", re.I),                                "Pacilio (conjuez)"),
    (re.compile(r"[áa]ngel\\s+a\\.?\\s*arga[ñn]araz", re.I),                  "Argañaraz (conjuez)"),"""

APELLIDOS_NUEVOS = (
    "|najurieta"
    "|alcal.a?"
    "|mor[áa]n"
    "|tyden(?:\\s+de\\s+skanata)?|skanata"
    "|poclava\\s+lafuente|lafuente"
    "|pereira\\s+gonz.lez"
    "|ferro"
    "|pacilio"
    "|arga.araz"
)


def verificar_integridad():
    """Chequea que parser.py sea exactamente el de pre-H043."""
    data = PARSER_ORIG.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != HASH_ESPERADO:
        print(f"FAIL: parser.py no coincide con el original pre-H043.")
        print(f"  Esperado: {HASH_ESPERADO[:16]}...")
        print(f"  Actual:   {sha[:16]}...")
        print(f"  Restaurá con: git checkout -- scripts/pipeline/parser.py")
        return False
    print(f"OK: parser.py SHA-256 coincide con pre-H043 ({sha[:16]}...).")
    return True


def patchear_copia():
    """Copia parser.py y aplica patch B063."""
    shutil.copy2(PARSER_ORIG, PARSER_B063)
    texto = PARSER_B063.read_text(encoding="utf-8")

    # 1. JUECES_CONOCIDOS
    m_jc = re.search(r'(^.*mahiques.*conjuez.*$)', texto, re.MULTILINE)
    anchor_jc = m_jc.group(1)
    texto = texto.replace(anchor_jc, anchor_jc + "\n" + NUEVOS_CONJUECES, 1)

    # 2. _RE_FIRMA_COMPLETA
    m_firma = re.search(r'(\|mahiques\s*\))', texto)
    anchor_firma = m_firma.group(1)
    texto = texto.replace(anchor_firma, f"|mahiques{APELLIDOS_NUEVOS})", 1)

    PARSER_B063.write_text(texto, encoding="utf-8")

    # Verificación rápida
    check = PARSER_B063.read_text(encoding="utf-8")
    nombres = ["Najurieta", "Alcalá", "Morán", "Tyden de Skanata",
               "Poclava Lafuente", "Pereira González", "Ferro",
               "Pacilio", "Argañaraz"]
    for n in nombres:
        if n not in check:
            print(f"  FAIL en patch: falta {n}")
            return False
    print(f"OK: parser_b063.py patcheado ({len(nombres)} conjueces).")
    return True


def correr_pipeline():
    """Corre parser_b063.py con output a directorio b063/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(PARSER_B063),
        "--localizados", str(LOCALIZADOS),
        "--mapa", str(MAPA),
        "--corpus", str(CORPUS),
        "--output", str(OUTPUT_CASOS),
        "--output-votos", str(OUTPUT_VOTOS),
    ]

    # Verificar que existan los inputs
    for path, label in [(LOCALIZADOS, "localizados"), (MAPA, "mapa"), (CORPUS, "corpus")]:
        if not path.exists():
            print(f"FAIL: no existe {label}: {path}")
            return False

    print(f"\nCorriendo pipeline B063...")
    print(f"  Comando: python parser_b063.py --output {OUTPUT_CASOS.relative_to(ROOT)}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"FAIL: pipeline terminó con código {result.returncode}")
        return False
    if not OUTPUT_CASOS.exists():
        print("FAIL: no se generó CSV de casos.")
        return False
    print("OK: pipeline B063 completado.")
    return True


def comparar_csvs():
    """Compara baseline vs B063 campo por campo."""
    print("\n" + "=" * 70)
    print("COMPARACIÓN BASELINE vs B063")
    print("=" * 70)

    # Cargar ambos
    def cargar(path):
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    base = cargar(BASELINE_CASOS)
    b063 = cargar(OUTPUT_CASOS)

    base_idx = {r["caso_id_canonico"]: r for r in base}
    b063_idx = {r["caso_id_canonico"]: r for r in b063}

    print(f"\nFilas: baseline={len(base)}, B063={len(b063)}")
    if len(base) != len(b063):
        print("  ⚠ DIFERENCIA EN CANTIDAD DE FILAS")

    # Campos a comparar
    campos_clave = [
        "n_jueces", "n_titulares", "firma_raw", "jueces",
        "jueces_conocidos", "jueces_desconocidos", "posiciones",
        "voting_pattern", "n_votos_svoto", "n_disidencias",
    ]

    cambios = []
    regresiones = []

    for caso_id, r_base in base_idx.items():
        r_b063 = b063_idx.get(caso_id)
        if not r_b063:
            regresiones.append(f"FALTA en B063: {caso_id}")
            continue
        for campo in campos_clave:
            v_base = r_base.get(campo, "")
            v_b063 = r_b063.get(campo, "")
            if v_base != v_b063:
                cambios.append({
                    "caso_id": caso_id,
                    "campo": campo,
                    "antes": v_base,
                    "despues": v_b063,
                })

    # ── Resumen de cambios ──────────────────────────────────────────────
    print(f"\nCasos con cambios: {len(set(c['caso_id'] for c in cambios))}")
    print(f"Campos modificados: {len(cambios)}")

    if regresiones:
        print(f"\n⚠ REGRESIONES ({len(regresiones)}):")
        for r in regresiones[:10]:
            print(f"  {r}")

    # Agrupar por campo
    por_campo = Counter(c["campo"] for c in cambios)
    print("\nCambios por campo:")
    for campo, n in por_campo.most_common():
        print(f"  {campo:<25} {n:>4}")

    # ── Detalle: desconocidos que bajaron ────────────────────────────────
    descon_cambios = [c for c in cambios if c["campo"] == "jueces_desconocidos"]
    if descon_cambios:
        print(f"\n── Detalle: jueces_desconocidos ({len(descon_cambios)} casos) ──")
        for c in descon_cambios[:30]:
            print(f"  {c['caso_id']}")
            print(f"    antes:   {c['antes'][:80]}")
            print(f"    después: {c['despues'][:80]}")

    # ── Detalle: n_jueces que subió ─────────────────────────────────────
    njueces_cambios = [c for c in cambios if c["campo"] == "n_jueces"]
    if njueces_cambios:
        print(f"\n── Detalle: n_jueces ({len(njueces_cambios)} casos) ──")
        subio = sum(1 for c in njueces_cambios
                    if int(c["despues"] or 0) > int(c["antes"] or 0))
        bajo = sum(1 for c in njueces_cambios
                   if int(c["despues"] or 0) < int(c["antes"] or 0))
        print(f"  Subió: {subio}  Bajó: {bajo}")
        if bajo > 0:
            print("  ⚠ REGRESIÓN: n_jueces bajó en algunos casos:")
            for c in njueces_cambios:
                if int(c["despues"] or 0) < int(c["antes"] or 0):
                    print(f"    {c['caso_id']}: {c['antes']} -> {c['despues']}")

    # ── Top desconocidos comparado ──────────────────────────────────────
    def contar_desconocidos(rows):
        ctr = Counter()
        for r in rows:
            desc = r.get("jueces_desconocidos", "").strip()
            if desc:
                for nombre in desc.split("; "):
                    nombre = nombre.strip()
                    if nombre:
                        ctr[nombre] += 1
        return ctr

    desc_base = contar_desconocidos(base)
    desc_b063 = contar_desconocidos(b063)

    print("\n── Top 20 desconocidos: BASELINE vs B063 ──")
    todos = set(desc_base.keys()) | set(desc_b063.keys())
    ranking = sorted(todos, key=lambda k: desc_base.get(k, 0), reverse=True)
    print(f"  {'Nombre':<45} {'Base':>5} {'B063':>5} {'Δ':>5}")
    print(f"  {'-'*45} {'-'*5} {'-'*5} {'-'*5}")
    for nombre in ranking[:25]:
        n_base = desc_base.get(nombre, 0)
        n_b063 = desc_b063.get(nombre, 0)
        delta = n_b063 - n_base
        marker = " ✓" if delta < 0 else (" ⚠" if delta > 0 else "")
        print(f"  {nombre:<45} {n_base:>5} {n_b063:>5} {delta:>+5}{marker}")

    # ── Votos ───────────────────────────────────────────────────────────
    if BASELINE_VOTOS.exists() and OUTPUT_VOTOS.exists():
        base_v = cargar(BASELINE_VOTOS)
        b063_v = cargar(OUTPUT_VOTOS)
        print(f"\nVotos: baseline={len(base_v)}, B063={len(b063_v)}, Δ={len(b063_v)-len(base_v)}")

    print("\n" + "=" * 70)
    if not regresiones and not any(
        int(c["despues"] or 0) < int(c["antes"] or 0)
        for c in njueces_cambios
    ):
        print("RESULTADO: Sin regresiones. Patch B063 listo para producción.")
    else:
        print("RESULTADO: HAY REGRESIONES. Revisar antes de aplicar.")
    print("=" * 70)


def limpiar():
    """Elimina la copia patcheada."""
    if PARSER_B063.exists():
        PARSER_B063.unlink()
        print(f"\nLimpieza: eliminado {PARSER_B063.name}")


def main():
    print("PoC B063 — Conjueces faltantes")
    print(f"Root: {ROOT}\n")

    # Paso 0: verificar integridad
    if not verificar_integridad():
        return

    # Paso 1: patchear copia
    if not patchear_copia():
        limpiar()
        return

    # Paso 2: correr pipeline
    if not correr_pipeline():
        limpiar()
        return

    # Paso 3: comparar
    try:
        comparar_csvs()
    except Exception as e:
        print(f"ERROR en comparación: {e}")
        import traceback
        traceback.print_exc()

    # Paso 4: limpiar copia (dejar CSVs para inspección)
    limpiar()
    print(f"\nCSVs B063 en: {OUTPUT_DIR.relative_to(ROOT)}/")
    print("Para aplicar en producción, usar patch definitivo post-validación.")


if __name__ == "__main__":
    main()
