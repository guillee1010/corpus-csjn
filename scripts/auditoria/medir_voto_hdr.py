"""Medir impacto de fix B032 en RE_VOTO_HDR y RE_DISID_HDR.
Uso: python scripts/auditoria/medir_voto_hdr.py
"""
import re, glob, os

# --- Regex vieja (producción) ---
RE_VOTO_OLD = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)
RE_DISID_OLD = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)

# --- Regex nueva (fix B032: +l[ao]s?) ---
RE_VOTO_NEW = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?|l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)
RE_DISID_NEW = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?|l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")

def medir(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    fname = os.path.basename(filepath)
    voto_old, voto_new = [], []
    disid_old, disid_new = [], []

    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if RE_VOTO_OLD.match(line):
            voto_old.append((i, line))
        if RE_VOTO_NEW.match(line):
            voto_new.append((i, line))
        if RE_DISID_OLD.match(line):
            disid_old.append((i, line))
        if RE_DISID_NEW.match(line):
            disid_new.append((i, line))

    delta_v = len(voto_new) - len(voto_old)
    delta_d = len(disid_new) - len(disid_old)

    if delta_v or delta_d:
        print(f"\n=== {fname} ({len(lines)} líneas) ===")
        print(f"  VOTO:  {len(voto_old)} → {len(voto_new)}  (delta +{delta_v})")
        print(f"  DISID: {len(disid_old)} → {len(disid_new)}  (delta +{delta_d})")
        old_set = {x[0] for x in voto_old}
        for lineno, text in voto_new:
            if lineno not in old_set:
                print(f"    NUEVO voto   L{lineno}: {text[:120]}")
        old_set_d = {x[0] for x in disid_old}
        for lineno, text in disid_new:
            if lineno not in old_set_d:
                print(f"    NUEVA disid  L{lineno}: {text[:120]}")

    return delta_v, delta_d

if __name__ == "__main__":
    archivos = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.md")))
    if not archivos:
        print(f"No se encontraron .md en {CORPUS_DIR}")
        raise SystemExit(1)

    print(f"Corpus: {len(archivos)} archivos en {CORPUS_DIR}")
    total_v, total_d = 0, 0
    for fp in archivos:
        dv, dd = medir(fp)
        total_v += dv
        total_d += dd

    print(f"\n--- TOTAL ---")
    print(f"Votos nuevos:       +{total_v}")
    print(f"Disidencias nuevas: +{total_d}")
