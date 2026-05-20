"""
Patch B063 producción — validado por poc_b063_v2.py.
40 mejoras n_jueces, 0 regresiones, +55 votos.

Uso (desde raíz del repo):
  python scripts/diagnostico/H043/patch_b063_produccion.py
"""

import re
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARSER = ROOT / "scripts" / "pipeline" / "parser.py"
HASH_ESPERADO = "a3466bb17ee6a9e4faa4d461a7919d39e9edeb3574307fbacddffbf10b8e7d83"

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

LINEA_550_ORIG = '    nombres_jueces = {j["nombre"].lower() for j in jueces_out}'
LINEA_550_FIX  = '    nombres_jueces = {j["nombre"].split(" (")[0].lower() for j in jueces_out}'


def main():
    # ── Hash check ──────────────────────────────────────────────────────
    sha = hashlib.sha256(PARSER.read_bytes()).hexdigest()
    if sha != HASH_ESPERADO:
        print(f"FAIL: parser.py no coincide con pre-H043 ({sha[:16]}...).")
        print("  Restaurá con: git checkout -- scripts/pipeline/parser.py")
        return

    # ── Backup ──────────────────────────────────────────────────────────
    bak = PARSER.with_suffix(".py.bak_b063v2")
    shutil.copy2(PARSER, bak)

    texto = PARSER.read_text(encoding="utf-8")

    # ── Patch 1: JUECES_CONOCIDOS ────────────────────────────────────────
    m_jc = re.search(r'(^.*mahiques.*conjuez.*$)', texto, re.MULTILINE)
    texto = texto.replace(m_jc.group(1), m_jc.group(1) + "\n" + NUEVOS_CONJUECES, 1)

    # ── Patch 2: _RE_FIRMA_COMPLETA ──────────────────────────────────────
    m_firma = re.search(r'(\|mahiques\s*\))', texto)
    texto = texto.replace(m_firma.group(1), f"|mahiques{APELLIDOS_NUEVOS})", 1)

    # ── Patch 3: fix cosmético línea 550 ─────────────────────────────────
    texto = texto.replace(LINEA_550_ORIG, LINEA_550_FIX, 1)

    # ── Escribir ─────────────────────────────────────────────────────────
    PARSER.write_text(texto, encoding="utf-8")

    # ── Verificar ────────────────────────────────────────────────────────
    check = PARSER.read_text(encoding="utf-8")
    ok = True
    for marca in ["Conjueces B063", "Pereyra González", "Mill de Pereyra",
                   "najurieta", "pereyra", "mill", '.split(" (")[0]']:
        if marca not in check:
            print(f"  FALTA: {marca}")
            ok = False

    if ok:
        print(f"OK: parser.py patcheado. Backup en {bak.name}")
        print(f"\nCommit sugerido:")
        print(f'  git add scripts/pipeline/parser.py')
        print(f'  git commit -m "B063: 10 conjueces + fix cosmético desconocidos (40 mejoras, 0 regresiones)"')
    else:
        print("FAIL: restaurar desde backup.")
        shutil.copy2(bak, PARSER)


if __name__ == "__main__":
    main()
