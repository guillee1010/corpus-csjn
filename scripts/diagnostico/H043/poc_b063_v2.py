"""
PoC B063 v2 -- Conjueces + fix cosmético desconocidos.

Tres parches sobre parser.py original:
  1. JUECES_CONOCIDOS: 10 conjueces (9 de v1 + Rita Mill de Pereyra,
     con fix pereyra→pereyra y variante Carlos Martín).
  2. _RE_FIRMA_COMPLETA: apellidos sincronizados.
  3. Línea 550: fix cosmético — strip "(conjuez)" del nombre canónico
     para que el filtro de desconocidos no los deje pasar.

Uso (desde raíz del repo):
  python scripts/diagnostico/H043/poc_b063_v2.py
"""

import re
import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from collections import Counter

# ── Rutas ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSER_ORIG = ROOT / "scripts" / "pipeline" / "parser.py"
PARSER_POC  = ROOT / "scripts" / "pipeline" / "parser_b063v2.py"

BASELINE_CASOS = ROOT / "output" / "parser" / "csjn_casos.csv"
BASELINE_VOTOS = ROOT / "output" / "parser" / "csjn_casos_votos.csv"

OUTPUT_DIR   = ROOT / "output" / "parser" / "b063v2"
OUTPUT_CASOS = OUTPUT_DIR / "csjn_casos.csv"
OUTPUT_VOTOS = OUTPUT_DIR / "csjn_casos_votos.csv"

LOCALIZADOS = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA        = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS      = ROOT / "corpus"

# SHA-256 del parser.py pre-H043 (LF en disco)
HASH_ESPERADO = "a3466bb17ee6a9e4faa4d461a7919d39e9edeb3574307fbacddffbf10b8e7d83"

# ── Patch 1: JUECES_CONOCIDOS (10 conjueces) ────────────────────────────────
NUEVOS_CONJUECES = """    # ── Conjueces B063 (H043) ───────────────────────────────────────────────
    (re.compile(r"mar[íi]a\\s+susana\\s+najurieta", re.I),                    "Najurieta (conjuez)"),
    (re.compile(r"roc[íi]o\\s+alcal[áa]", re.I),                            "Alcalá (conjuez)"),
    (re.compile(r"jorge\\s+eduardo\\s+mor[áa]n\\.?", re.I),                   "Morán (conjuez)"),
    (re.compile(r"mirta\\s+(d\\.?|delia)\\s+tyden(?:\\s+de\\s+skanata)?", re.I), "Tyden de Skanata (conjuez)"),
    (re.compile(r"juan\\s+carlos\\s+poclava\\s+lafuente", re.I),              "Poclava Lafuente (conjuez)"),
    (re.compile(r"carlos\\s+(m\\.?|mart[íi]n)\\s+pereyra\\s+gonz[áa]lez", re.I), "Pereyra González (conjuez)"),
    (re.compile(r"jorge\\s+ferro", re.I),                                    "Ferro (conjuez)"),
    (re.compile(r"antonio\\s+pacilio", re.I),                                "Pacilio (conjuez)"),
    (re.compile(r"[áa]ngel\\s+a\\.?\\s*arga[ñn]araz", re.I),                  "Argañaraz (conjuez)"),
    (re.compile(r"rita\\s+(mill|m\\.?)\\s+de\\s+pereyra", re.I),               "Mill de Pereyra (conjuez)"),"""

# ── Patch 2: _RE_FIRMA_COMPLETA (apellidos sincronizados) ───────────────────
APELLIDOS_NUEVOS = (
    "|najurieta"
    "|alcal.a?"
    "|mor[áa]n"
    "|tyden(?:\\s+de\\s+skanata)?|skanata"
    "|poclava\\s+lafuente|lafuente"
    "|pereyra\\s+gonz.lez"
    "|ferro"
    "|pacilio"
    "|arga.araz"
    "|mill\\s+de\\s+pereyra"
)

# ── Patch 3: fix cosmético línea 550 ────────────────────────────────────────
LINEA_550_ORIG = '    nombres_jueces = {j["nombre"].lower() for j in jueces_out}'
LINEA_550_FIX  = '    nombres_jueces = {j["nombre"].split(" (")[0].lower() for j in jueces_out}'


def verificar_integridad():
    data = PARSER_ORIG.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != HASH_ESPERADO:
        print(f"FAIL: parser.py no coincide con pre-H043.")
        print(f"  Esperado: {HASH_ESPERADO[:16]}...")
        print(f"  Actual:   {sha[:16]}...")
        print(f"  Restaurá con: git checkout -- scripts/pipeline/parser.py")
        return False
    print(f"OK: parser.py SHA-256 coincide ({sha[:16]}...).")
    return True


def patchear_copia():
    shutil.copy2(PARSER_ORIG, PARSER_POC)
    texto = PARSER_POC.read_text(encoding="utf-8")

    # ── Patch 1: JUECES_CONOCIDOS ────────────────────────────────────────
    m_jc = re.search(r'(^.*mahiques.*conjuez.*$)', texto, re.MULTILINE)
    if not m_jc:
        print("FAIL: no encuentro anchor Mahiques"); return False
    texto = texto.replace(m_jc.group(1), m_jc.group(1) + "\n" + NUEVOS_CONJUECES, 1)
    print("  Patch 1 OK: JUECES_CONOCIDOS (+10 conjueces)")

    # ── Patch 2: _RE_FIRMA_COMPLETA ──────────────────────────────────────
    m_firma = re.search(r'(\|mahiques\s*\))', texto)
    if not m_firma:
        print("FAIL: no encuentro anchor |mahiques)"); return False
    texto = texto.replace(m_firma.group(1), f"|mahiques{APELLIDOS_NUEVOS})", 1)
    print("  Patch 2 OK: _RE_FIRMA_COMPLETA (apellidos)")

    # ── Patch 3: fix cosmético línea 550 ─────────────────────────────────
    if LINEA_550_ORIG not in texto:
        print("FAIL: no encuentro línea 550 original"); return False
    texto = texto.replace(LINEA_550_ORIG, LINEA_550_FIX, 1)
    print("  Patch 3 OK: fix cosmético desconocidos")

    PARSER_POC.write_text(texto, encoding="utf-8")

    # Verificación rápida
    check = PARSER_POC.read_text(encoding="utf-8")
    for nombre in ["Najurieta", "Pereyra González", "Mill de Pereyra",
                    "Ferro", "Argañaraz", ".split"]:
        if nombre not in check:
            print(f"  FAIL: falta {nombre}"); return False
    # Verificar que NO tiene "pereira" (typo viejo)
    if re.search(r'pereira\\s+gonz', check):
        print("  FAIL: todavía tiene 'pereira' (typo)"); return False

    print("OK: parser_b063v2.py patcheado (10 conjueces + fix cosmético).")
    return True


def correr_pipeline():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(PARSER_POC),
        "--localizados", str(LOCALIZADOS),
        "--mapa", str(MAPA),
        "--corpus", str(CORPUS),
        "--output", str(OUTPUT_CASOS),
        "--output-votos", str(OUTPUT_VOTOS),
    ]
    for path, label in [(LOCALIZADOS, "localizados"), (MAPA, "mapa"), (CORPUS, "corpus")]:
        if not path.exists():
            print(f"FAIL: no existe {label}: {path}"); return False

    print(f"\nCorriendo pipeline B063v2...")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"FAIL: pipeline terminó con código {result.returncode}"); return False
    if not OUTPUT_CASOS.exists():
        print("FAIL: no se generó CSV de casos."); return False
    print("OK: pipeline B063v2 completado.")
    return True


def comparar_csvs():
    print("\n" + "=" * 70)
    print("COMPARACIÓN BASELINE vs B063v2")
    print("=" * 70)

    def cargar(path):
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    base = cargar(BASELINE_CASOS)
    b063 = cargar(OUTPUT_CASOS)
    base_idx = {r["caso_id_canonico"]: r for r in base}
    b063_idx = {r["caso_id_canonico"]: r for r in b063}

    print(f"\nFilas: baseline={len(base)}, B063v2={len(b063)}")

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
            regresiones.append(f"FALTA en B063v2: {caso_id}"); continue
        for campo in campos_clave:
            v_base = r_base.get(campo, "")
            v_b063 = r_b063.get(campo, "")
            if v_base != v_b063:
                cambios.append({
                    "caso_id": caso_id, "campo": campo,
                    "antes": v_base, "despues": v_b063,
                })

    casos_cambiados = set(c["caso_id"] for c in cambios)
    print(f"\nCasos con cambios: {len(casos_cambiados)}")
    print(f"Campos modificados: {len(cambios)}")

    if regresiones:
        print(f"\n⚠ REGRESIONES ({len(regresiones)}):")
        for r in regresiones[:10]:
            print(f"  {r}")

    por_campo = Counter(c["campo"] for c in cambios)
    print("\nCambios por campo:")
    for campo, n in por_campo.most_common():
        print(f"  {campo:<25} {n:>4}")

    # ── n_jueces ────────────────────────────────────────────────────────
    njueces_cambios = [c for c in cambios if c["campo"] == "n_jueces"]
    if njueces_cambios:
        subio = sum(1 for c in njueces_cambios
                    if int(c["despues"] or 0) > int(c["antes"] or 0))
        bajo = sum(1 for c in njueces_cambios
                   if int(c["despues"] or 0) < int(c["antes"] or 0))
        print(f"\n── n_jueces: subió {subio}, bajó {bajo} ──")
        if bajo > 0:
            print("  ⚠ REGRESIÓN:")
            for c in njueces_cambios:
                if int(c["despues"] or 0) < int(c["antes"] or 0):
                    print(f"    {c['caso_id']}: {c['antes']} -> {c['despues']}")

    # ── Conjueces nuevos: cuántos matcheó cada uno ──────────────────────
    conjueces_nombres = [
        "Najurieta", "Alcalá", "Morán", "Tyden de Skanata",
        "Poclava Lafuente", "Pereyra González", "Ferro",
        "Pacilio", "Argañaraz", "Mill de Pereyra",
    ]
    print("\n── Conjueces B063v2: casos matcheados ──")
    for conj in conjueces_nombres:
        n = sum(1 for r in b063 if conj in r.get("jueces_conocidos", ""))
        print(f"  {conj:<25} {n:>3} casos")

    # ── Desconocidos: comparar top 20 pipeline ──────────────────────────
    # Usar firma_raw + parse_firma simulado para contar desconocidos reales
    # (no el campo CSV que siempre está vacío para conocidos)
    print("\n── Verificación fix cosmético (top desconocidos del pipeline output) ──")
    print("  → Revisar la salida del pipeline arriba.")
    print("  → Si el fix cosmético funcionó, OTERO/FERRO/etc. ya no aparecen.")

    # ── Votos ───────────────────────────────────────────────────────────
    if BASELINE_VOTOS.exists() and OUTPUT_VOTOS.exists():
        base_v = cargar(BASELINE_VOTOS)
        b063_v = cargar(OUTPUT_VOTOS)
        delta = len(b063_v) - len(base_v)
        print(f"\nVotos: baseline={len(base_v)}, B063v2={len(b063_v)}, Δ={delta:+d}")

    print("\n" + "=" * 70)
    hay_regresion = bool(regresiones) or any(
        int(c["despues"] or 0) < int(c["antes"] or 0) for c in njueces_cambios
    )
    if not hay_regresion:
        print("RESULTADO: Sin regresiones. Patch B063v2 listo para producción.")
    else:
        print("RESULTADO: HAY REGRESIONES. Revisar antes de aplicar.")
    print("=" * 70)


def limpiar():
    if PARSER_POC.exists():
        PARSER_POC.unlink()
        print(f"\nLimpieza: eliminado {PARSER_POC.name}")


def main():
    print("PoC B063 v2 — Conjueces + Pereyra + fix cosmético")
    print(f"Root: {ROOT}\n")

    if not verificar_integridad():
        return
    if not patchear_copia():
        limpiar(); return
    if not correr_pipeline():
        limpiar(); return
    try:
        comparar_csvs()
    except Exception as e:
        print(f"ERROR en comparación: {e}")
        import traceback; traceback.print_exc()

    limpiar()
    print(f"\nCSVs B063v2 en: {OUTPUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
