"""
PoC Fase 2 — Agregar Juez/Jueza a RE_VOTO_HDR y RE_DISID_HDR.

Impacto esperado: ~85 headers nuevos matcheados (55 voto + 19 disidencia
+ 6 jueza + 2 juez-femenino + 2 disid parcial + 1 disid jueza).

Uso (desde raíz del repo):
  python scripts/diagnostico/H043/poc_juez_header.py
"""

import re
import csv
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSER_ORIG = ROOT / "scripts" / "pipeline" / "parser.py"
PARSER_POC  = ROOT / "scripts" / "pipeline" / "parser_poc_juez.py"

BASELINE_CASOS = ROOT / "output" / "parser" / "csjn_casos.csv"
BASELINE_VOTOS = ROOT / "output" / "parser" / "csjn_casos_votos.csv"

OUTPUT_DIR   = ROOT / "output" / "parser" / "poc_juez"
OUTPUT_CASOS = OUTPUT_DIR / "csjn_casos.csv"
OUTPUT_VOTOS = OUTPUT_DIR / "csjn_casos_votos.csv"

LOCALIZADOS = ROOT / "output" / "localizacion" / "fallos_localizados.csv"
MAPA        = ROOT / "output" / "mapa" / "mapa_paginas.csv"
CORPUS      = ROOT / "corpus"

# SHA-256 post-B063 (commit 8a2558e)
HASH_ESPERADO = "7ce956a86dcf57559d12b0ed9663393ca177744167ce7cfaeb388071ea931489"

# Anchor: cierre del grupo de títulos (aparece 2 veces: RE_VOTO_HDR y RE_DISID_HDR)
ANCHOR = r'Ministr[ao]s?)'
REEMPLAZO = r'Ministr[ao]s?|Juez(?:as?|es)?)'


def verificar_integridad():
    sha = hashlib.sha256(PARSER_ORIG.read_bytes()).hexdigest()
    if sha != HASH_ESPERADO:
        print(f"FAIL: parser.py no coincide con post-B063.")
        print(f"  Esperado: {HASH_ESPERADO[:16]}...")
        print(f"  Actual:   {sha[:16]}...")
        return False
    print(f"OK: parser.py SHA-256 coincide con post-B063.")
    return True


def patchear_copia():
    shutil.copy2(PARSER_ORIG, PARSER_POC)
    texto = PARSER_POC.read_text(encoding="utf-8")

    n = texto.count(ANCHOR)
    if n != 2:
        print(f"FAIL: anchor '{ANCHOR}' aparece {n} veces (esperaba 2)")
        return False

    texto = texto.replace(ANCHOR, REEMPLAZO)

    if texto.count(REEMPLAZO) != 2:
        print("FAIL: reemplazo no quedó correcto")
        return False

    PARSER_POC.write_text(texto, encoding="utf-8")
    print(f"OK: parser_poc_juez.py patcheado (Juez/Jueza en ambos regex).")
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

    print(f"\nCorriendo pipeline poc_juez...")
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print(f"FAIL: código {result.returncode}"); return False
    if not OUTPUT_CASOS.exists():
        print("FAIL: no se generó CSV."); return False
    print("OK: pipeline poc_juez completado.")
    return True


def comparar_csvs():
    print("\n" + "=" * 70)
    print("COMPARACIÓN BASELINE vs POC_JUEZ")
    print("=" * 70)

    def cargar(path):
        with open(path, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    base = cargar(BASELINE_CASOS)
    poc = cargar(OUTPUT_CASOS)
    base_idx = {r["caso_id_canonico"]: r for r in base}
    poc_idx = {r["caso_id_canonico"]: r for r in poc}

    print(f"\nFilas: baseline={len(base)}, poc_juez={len(poc)}")

    campos_clave = [
        "n_jueces", "firma_raw", "jueces", "jueces_conocidos",
        "posiciones", "voting_pattern", "n_votos_svoto", "n_disidencias",
        "wc_votos", "wc_mayoria",
    ]

    cambios = []
    for caso_id, r_base in base_idx.items():
        r_poc = poc_idx.get(caso_id)
        if not r_poc:
            cambios.append({"caso_id": caso_id, "campo": "FALTA", "antes": "", "despues": ""})
            continue
        for campo in campos_clave:
            v_base = r_base.get(campo, "")
            v_poc = r_poc.get(campo, "")
            if v_base != v_poc:
                cambios.append({
                    "caso_id": caso_id, "campo": campo,
                    "antes": v_base, "despues": v_poc,
                })

    casos_cambiados = set(c["caso_id"] for c in cambios)
    print(f"\nCasos con cambios: {len(casos_cambiados)}")

    por_campo = Counter(c["campo"] for c in cambios)
    print("\nCambios por campo:")
    for campo, n in por_campo.most_common():
        print(f"  {campo:<25} {n:>4}")

    # n_votos_svoto y n_disidencias son los que más importan
    # (si RE_VOTO_HDR/RE_DISID_HDR matchean más, estos suben)
    for campo_interes in ["n_votos_svoto", "n_disidencias"]:
        cambios_ci = [c for c in cambios if c["campo"] == campo_interes]
        if cambios_ci:
            subio = sum(1 for c in cambios_ci
                        if int(c["despues"] or 0) > int(c["antes"] or 0))
            bajo = sum(1 for c in cambios_ci
                       if int(c["despues"] or 0) < int(c["antes"] or 0))
            print(f"\n── {campo_interes}: subió {subio}, bajó {bajo} ──")
            if bajo > 0:
                print("  ⚠ REGRESIÓN:")
                for c in cambios_ci:
                    if int(c["despues"] or 0) < int(c["antes"] or 0):
                        print(f"    {c['caso_id']}: {c['antes']} -> {c['despues']}")

    # wc_votos / wc_mayoria: si un voto se detecta como separado,
    # wc_votos sube y wc_mayoria baja (el texto pasa de mayoría a voto)
    wc_votos_cambios = [c for c in cambios if c["campo"] == "wc_votos"]
    wc_may_cambios = [c for c in cambios if c["campo"] == "wc_mayoria"]
    if wc_votos_cambios:
        print(f"\n── wc_votos cambió en {len(wc_votos_cambios)} casos ──")
        print(f"── wc_mayoria cambió en {len(wc_may_cambios)} casos ──")

    # Detalle de algunos casos cambiados
    if casos_cambiados:
        print(f"\n── Muestra de casos cambiados (primeros 10) ──")
        for caso_id in sorted(casos_cambiados)[:10]:
            cambios_caso = [c for c in cambios if c["caso_id"] == caso_id]
            print(f"\n  {caso_id}:")
            for c in cambios_caso:
                print(f"    {c['campo']}: {c['antes'][:60]} → {c['despues'][:60]}")

    # Votos
    if BASELINE_VOTOS.exists() and OUTPUT_VOTOS.exists():
        base_v = cargar(BASELINE_VOTOS)
        poc_v = cargar(OUTPUT_VOTOS)
        delta = len(poc_v) - len(base_v)
        print(f"\nVotos: baseline={len(base_v)}, poc_juez={len(poc_v)}, Δ={delta:+d}")

    print("\n" + "=" * 70)
    hay_regresion = any(c["campo"] == "FALTA" for c in cambios)
    for campo_interes in ["n_votos_svoto", "n_disidencias"]:
        cambios_ci = [c for c in cambios if c["campo"] == campo_interes]
        if any(int(c["despues"] or 0) < int(c["antes"] or 0) for c in cambios_ci):
            hay_regresion = True
    if not hay_regresion:
        print("RESULTADO: Sin regresiones.")
    else:
        print("RESULTADO: HAY REGRESIONES. Revisar.")
    print("=" * 70)


def limpiar():
    if PARSER_POC.exists():
        PARSER_POC.unlink()
        print(f"\nLimpieza: eliminado {PARSER_POC.name}")


def main():
    print("PoC Fase 2 — Juez/Jueza en RE_VOTO_HDR + RE_DISID_HDR")
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
        print(f"ERROR: {e}")
        import traceback; traceback.print_exc()

    limpiar()
    print(f"\nCSVs en: {OUTPUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
