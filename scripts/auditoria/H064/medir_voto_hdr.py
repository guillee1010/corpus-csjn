"""Medir impacto de fix B032 en RE_VOTO_HDR y RE_DISID_HDR."""
import re, sys, os

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
    
    print(f"=== {fname} ({len(lines)} líneas) ===")
    print(f"RE_VOTO_HDR:  vieja={len(voto_old)}  nueva={len(voto_new)}  delta=+{len(voto_new)-len(voto_old)}")
    print(f"RE_DISID_HDR: vieja={len(disid_old)}  nueva={len(disid_new)}  delta=+{len(disid_new)-len(disid_old)}")
    
    # Mostrar los nuevos hits (delta)
    old_set = {x[0] for x in voto_old}
    nuevos_voto = [x for x in voto_new if x[0] not in old_set]
    if nuevos_voto:
        print(f"\nVotos NUEVOS detectados ({len(nuevos_voto)}):")
        for lineno, text in nuevos_voto:
            print(f"  L{lineno}: {text[:120]}")
    
    old_set_d = {x[0] for x in disid_old}
    nuevos_disid = [x for x in disid_new if x[0] not in old_set_d]
    if nuevos_disid:
        print(f"\nDisidencias NUEVAS detectadas ({len(nuevos_disid)}):")
        for lineno, text in nuevos_disid:
            print(f"  L{lineno}: {text[:120]}")
    
    if not nuevos_voto and not nuevos_disid:
        print("\nSin hits nuevos en este archivo.")
    
    return len(nuevos_voto), len(nuevos_disid)

if __name__ == "__main__":
    for fp in sys.argv[1:]:
        medir(fp)
