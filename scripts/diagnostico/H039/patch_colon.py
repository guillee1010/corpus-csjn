"""Parcha poc_b055_sumario.py: exigir ':' en linea_es_header_sumario."""
from pathlib import Path

poc = Path("scripts/diagnostico/H039/poc_b055_sumario.py")
src = poc.read_text(encoding="utf-8")

# Reemplazar la condición que acepta "." OR ":" por solo ":"
OLD = '''    if not (s.endswith(".") or s.endswith(":") or ":" in s[:80]):
        return False'''

NEW = '''    # H039: exigir ":" — sumarios reales siempre tienen dos puntos.
    # Sin ":", matchean firmas ("LORENZETTI.") y carátulas ("YPF S.A.").
    if ":" not in s:
        return False'''

if OLD in src:
    src = src.replace(OLD, NEW)
    poc.write_text(src, encoding="utf-8")
    print("[OK] linea_es_header_sumario ahora exige ':'")
else:
    print("[ERROR] No encontré la condición original — ¿ya fue parcheada?")
