"""
B063 -- Agregar conjueces faltantes a JUECES_CONOCIDOS y _RE_FIRMA_COMPLETA.

9 conjueces:
  Najurieta(8), Alcalá(6), Morán(4), Tyden de Skanata(3),
  Poclava Lafuente(3), Pereira González(3), Ferro(3),
  Pacilio(3), Argañaraz(3).
  Moliné O'Connor(3) excluido: destituido 12/2003, no puede ser
  conjuez y corpus empieza 2006.

Uso:
  python patch_b063_conjueces.py
  (modifica parser.py in-place con backup .bak)
"""

import re
import shutil
from pathlib import Path

PARSER = Path(r"C:\Users\guill\Proyectos\corpus-csjn\scripts\pipeline\parser.py")

# ── Nuevas entradas JUECES_CONOCIDOS ─────────────────────────────────────────
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

# ── Apellidos nuevos para _RE_FIRMA_COMPLETA ─────────────────────────────────
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


def aplicar_patch():
    if not PARSER.exists():
        print(f"ERROR: no existe {PARSER}")
        return False

    texto = PARSER.read_text(encoding="utf-8")

    # ── 1. Buscar anchor JUECES_CONOCIDOS (línea de Mahiques) ────────────
    m_jc = re.search(r'(^.*mahiques.*conjuez.*$)', texto, re.MULTILINE)
    if not m_jc:
        print("ERROR: no encuentro línea de Mahiques en JUECES_CONOCIDOS")
        return False
    anchor_jc = m_jc.group(1)
    print(f"  Anchor JC encontrado OK")

    # ── 2. Buscar anchor _RE_FIRMA_COMPLETA (|mahiques + cierre grupo) ──
    m_firma = re.search(r'(\|mahiques\s*\))', texto)
    if not m_firma:
        print("ERROR: no encuentro |mahiques) en _RE_FIRMA_COMPLETA")
        print("  Diagnóstico — todas las ocurrencias de 'mahiques':")
        for i, m in enumerate(re.finditer(r'mahiques', texto)):
            start = max(0, m.start() - 20)
            end = min(len(texto), m.end() + 20)
            ctx = texto[start:end].replace('\n', '\\n').replace('\r', '\\r')
            after = texto[m.end():m.end()+5]
            print(f"    #{i+1} pos {m.start()}: ...{ctx}...")
            print(f"       bytes después: {[hex(ord(c)) for c in after]}")
        return False
    anchor_firma = m_firma.group(1)
    print(f"  Anchor FIRMA encontrado: {repr(anchor_firma)}")

    # ── 3. Aplicar parche JUECES_CONOCIDOS ───────────────────────────────
    reemplazo_jc = anchor_jc + "\n" + NUEVOS_CONJUECES
    texto_nuevo = texto.replace(anchor_jc, reemplazo_jc, 1)
    if texto_nuevo == texto:
        print("ERROR: reemplazo JUECES_CONOCIDOS no cambió nada")
        return False
    print("  JUECES_CONOCIDOS patcheado OK")

    # ── 4. Aplicar parche _RE_FIRMA_COMPLETA ─────────────────────────────
    reemplazo_firma = f"|mahiques{APELLIDOS_NUEVOS})"
    texto_nuevo = texto_nuevo.replace(anchor_firma, reemplazo_firma, 1)
    print("  _RE_FIRMA_COMPLETA patcheado OK")

    # ── 5. Backup y escritura ────────────────────────────────────────────
    bak = PARSER.with_suffix(".py.bak_b063")
    shutil.copy2(PARSER, bak)
    PARSER.write_text(texto_nuevo, encoding="utf-8")

    # ── 6. Verificación ─────────────────────────────────────────────────
    check = PARSER.read_text(encoding="utf-8")
    ok = True
    for nombre in ["Najurieta", "Alcalá", "Morán", "Tyden de Skanata",
                    "Poclava Lafuente", "Pereira González", "Ferro",
                    "Pacilio", "Argañaraz"]:
        found = nombre in check
        print(f"  {'OK' if found else 'FALTA'}: {nombre}")
        if not found:
            ok = False

    for ap in ["najurieta", "ferro", "pacilio", "skanata"]:
        found = ap in check
        print(f"  _RE_FIRMA {'OK' if found else 'FALTA'}: {ap}")
        if not found:
            ok = False

    if ok:
        print(f"\nPatch B063 aplicado. Backup en {bak}")
    else:
        print(f"\nPatch con errores. Backup en {bak}, revisar manualmente.")
    return ok


if __name__ == "__main__":
    aplicar_patch()
