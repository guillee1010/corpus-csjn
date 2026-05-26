"""
Agrega __version__ a los scripts canónicos del proyecto corpus-csjn.
Busca el cierre del primer docstring (segundo '\"\"\"') e inserta la línea después.
Idempotente: si __version__ ya existe, no hace nada.

Correr desde la raíz del repo:
    python scripts/auditoria/H076/agregar_version.py
"""

from pathlib import Path

SCRIPTS = {
    "scripts/pipeline/parser.py":                 "18.0",
    "scripts/pipeline/parser_editorial.py":       "1.0",
    "scripts/pipeline/construir_catalogo.py":     "1.0",
    "scripts/pipeline/cruzar_catalogo_y_mapa.py": "1.0",
    "scripts/pipeline/detectar_paginas.py":       "1.0",
    "scripts/auditoria/auditar_fallo.py":         "1.0",
}

TAG = "# H076"

def patch(path_str, version):
    path = Path(path_str)
    if not path.exists():
        print(f"  [SKIP] {path} no encontrado")
        return

    text = path.read_text(encoding="utf-8")

    if "__version__" in text:
        print(f"  [SKIP] {path} ya tiene __version__")
        return

    # Buscar el segundo '"""' (cierre del docstring)
    first = text.find('"""')
    if first == -1:
        print(f"  [SKIP] {path} sin docstring")
        return
    second = text.find('"""', first + 3)
    if second == -1:
        print(f"  [SKIP] {path} docstring no cerrado")
        return

    insert_pos = second + 3  # justo después del cierre """
    line = f'\n\n__version__ = "{version}"  {TAG}\n'

    new_text = text[:insert_pos] + line + text[insert_pos:]
    path.write_text(new_text, encoding="utf-8")
    print(f"  [OK]   {path} -> v{version}")


if __name__ == "__main__":
    print("Agregando __version__ a scripts canónicos...\n")
    for script, ver in SCRIPTS.items():
        patch(script, ver)
    print("\nListo. Verificar con: git diff --stat")
