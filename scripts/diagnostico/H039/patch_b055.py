"""Parcha poc_b055_sumario.py: agrega check de apellidos de jueces a linea_es_header_sumario."""
from pathlib import Path

poc = Path("scripts/diagnostico/H039/poc_b055_sumario.py")
src = poc.read_text(encoding="utf-8")

# 1. Agregar set de apellidos antes de linea_es_header_sumario
APELLIDOS_BLOCK = '''
# H039 fix B055: apellidos de jueces no son sumarios.
_APELLIDOS_JUECES_SUMARIO = {
    "rosatti", "rosenkrantz", "lorenzetti", "maqueda",
    "highton", "nolasco", "mansilla",
    "zaffaroni", "petracchi", "argibay", "fayt",
    "boggiano", "belluscio", "lopez", "lopez",
    "vazquez", "vazquez", "nazareno",
}

'''

ANCHOR = "def linea_es_header_sumario(linea):"
if "_APELLIDOS_JUECES_SUMARIO" not in src:
    src = src.replace(ANCHOR, APELLIDOS_BLOCK + ANCHOR)
    print("[OK] Set _APELLIDOS_JUECES_SUMARIO agregado")
else:
    print("[SKIP] Ya tiene _APELLIDOS_JUECES_SUMARIO")

# 2. Agregar check antes del return True final
OLD_RETURN = "    if len(primera_palabra) < 5:\n        return False\n    return True"
NEW_RETURN = """    if len(primera_palabra) < 5:
        return False
    # H039: descartar si primera palabra es apellido de juez conocido
    if primera_palabra.lower() in _APELLIDOS_JUECES_SUMARIO:
        return False
    return True"""

if "primera_palabra.lower() in _APELLIDOS_JUECES_SUMARIO" not in src:
    src = src.replace(OLD_RETURN, NEW_RETURN)
    print("[OK] Check de apellidos agregado en linea_es_header_sumario")
else:
    print("[SKIP] Ya tiene check de apellidos")

poc.write_text(src, encoding="utf-8")
print(f"[OK] {poc} parcheado")
