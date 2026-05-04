"""
Aplicador de Tanda 1 al parser.py.

Aplica dos ediciones quirúrgicas:
  1. Agrega `import unicodedata` después de `import re`.
  2. Inserta el bloque de funciones nuevas (Refactor sub-bloques v18) después
     del cierre de RUIDO_FIRMA y antes de `# ── Calificadores ──`.

Diseño defensivo:
  - Verifica que parser.py esté en el estado esperado antes de cualquier cambio.
  - Si ya estaba parchado (bloque presente), no hace nada y avisa.
  - Crea backup automático parser.py.bak_pre_tanda1 si no existe.
  - Si algo falla en medio, no deja el archivo en estado intermedio.

Uso (desde scripts/pipeline/, mismo directorio que parser.py):
    python aplicar_tanda1.py                # aplicar
    python aplicar_tanda1.py --check        # solo verificar estado, sin tocar
    python aplicar_tanda1.py --revert       # revertir desde backup
"""
import sys
import shutil
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────

PARSER_PATH = Path(__file__).parent / "parser.py"
BLOQUE_PATH = Path(__file__).parent / "bloque_funciones_nuevas.py"
BACKUP_PATH = Path(__file__).parent / "parser.py.bak_pre_tanda1"

# Marcadores únicos del archivo original que usamos para localizar las ediciones.
# Son strings exactos; si parser.py fue modificado de manera que estos no
# matcheen, el script aborta y no toca nada.

# Edición 1: agregar import unicodedata
IMPORT_ANCLA_VIEJO = "import re\nimport csv\nimport json\n"
IMPORT_ANCLA_NUEVO = "import re\nimport unicodedata\nimport csv\nimport json\n"

# Edición 2: insertar bloque después de RUIDO_FIRMA y antes de Calificadores
# Usamos un ancla larga y única para no confundir.
INSERCION_ANCLA = (
    '    "petracchi", "zaffaroni", "argibay", "fayt", "boggiano",\n'
    '    "belluscio", "lópez", "vázquez", "nazareno",\n'
    "}\n"
    "\n"
    "# ── Calificadores ─────────────────────────────────────────────────────────────"
)

# Marcador del bloque insertado (para detectar si ya está parchado)
MARCADOR_BLOQUE_PRESENTE = "# ── Refactor sub-bloques (v18) ──"


# ── Lógica ────────────────────────────────────────────────────────────────────

class EstadoArchivo:
    """Diagnostica el estado actual de parser.py."""

    def __init__(self, contenido):
        self.contenido = contenido
        self.tiene_import_unicodedata = "import unicodedata\n" in contenido
        self.tiene_bloque_v18 = MARCADOR_BLOQUE_PRESENTE in contenido
        self.tiene_ancla_import_vieja = IMPORT_ANCLA_VIEJO in contenido
        self.tiene_ancla_import_nueva = IMPORT_ANCLA_NUEVO in contenido
        self.tiene_ancla_insercion = INSERCION_ANCLA in contenido

    def estado(self):
        """Devuelve string identificando el estado:
        - 'limpio': listo para parchar
        - 'ya_parchado': el bloque ya está presente
        - 'parcial': solo una de las dos ediciones se aplicó (raro)
        - 'inconsistente': el archivo no matchea ninguna ancla esperada
        """
        if self.tiene_bloque_v18 and self.tiene_import_unicodedata:
            return "ya_parchado"
        if self.tiene_bloque_v18 or (
            self.tiene_import_unicodedata and not self.tiene_ancla_import_vieja
        ):
            return "parcial"
        if self.tiene_ancla_import_vieja and self.tiene_ancla_insercion:
            return "limpio"
        return "inconsistente"

    def reporte(self):
        return (
            f"  import unicodedata presente: {self.tiene_import_unicodedata}\n"
            f"  bloque v18 presente:         {self.tiene_bloque_v18}\n"
            f"  ancla import vieja:          {self.tiene_ancla_import_vieja}\n"
            f"  ancla import nueva:          {self.tiene_ancla_import_nueva}\n"
            f"  ancla inserción:             {self.tiene_ancla_insercion}\n"
            f"  → estado: {self.estado()}"
        )


def cargar_archivo(path, descripcion):
    if not path.exists():
        print(f"ERROR: no encuentro {descripcion} en {path}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def escribir_archivo(path, contenido):
    path.write_text(contenido, encoding="utf-8", newline="\n")


def crear_backup_si_no_existe():
    if BACKUP_PATH.exists():
        print(f"[OK]  Backup ya existe: {BACKUP_PATH.name}")
        return
    shutil.copy2(PARSER_PATH, BACKUP_PATH)
    print(f"[OK]  Backup creado: {BACKUP_PATH.name}")


def revertir():
    if not BACKUP_PATH.exists():
        print(f"ERROR: no hay backup en {BACKUP_PATH}")
        sys.exit(1)
    shutil.copy2(BACKUP_PATH, PARSER_PATH)
    print(f"[OK]  parser.py revertido desde {BACKUP_PATH.name}")


def verificar_solo():
    contenido = cargar_archivo(PARSER_PATH, "parser.py")
    estado = EstadoArchivo(contenido)
    print(f"Diagnóstico de {PARSER_PATH.name}:")
    print(estado.reporte())
    return estado


def aplicar():
    print(f"Aplicando Tanda 1 a {PARSER_PATH.name}...")
    print()

    # 1. Cargar archivos
    contenido = cargar_archivo(PARSER_PATH, "parser.py")
    bloque_nuevo = cargar_archivo(BLOQUE_PATH, "bloque_funciones_nuevas.py")

    # 2. Diagnosticar estado
    estado = EstadoArchivo(contenido)
    print(f"Estado actual de parser.py:")
    print(estado.reporte())
    print()

    estado_str = estado.estado()

    if estado_str == "ya_parchado":
        print("[INFO] El parser ya tiene Tanda 1 aplicada. No hago nada.")
        return 0

    if estado_str == "parcial":
        print("[ABORT] El parser está en estado parcial (solo una de las dos")
        print("        ediciones se aplicó). Revisar manualmente o revertir")
        print("        con: python aplicar_tanda1.py --revert")
        return 1

    if estado_str == "inconsistente":
        print("[ABORT] El parser no matchea las anclas esperadas. Esto significa")
        print("        que el archivo fue modificado de manera incompatible con")
        print("        el script. Detalles arriba. No toco nada.")
        return 1

    assert estado_str == "limpio"
    print("[OK]  Estado: limpio, listo para aplicar.")
    print()

    # 3. Backup
    crear_backup_si_no_existe()
    print()

    # 4. Edición 1: import unicodedata
    print("Aplicando edición 1: import unicodedata...")
    if contenido.count(IMPORT_ANCLA_VIEJO) != 1:
        print(f"[ABORT] Ancla de import aparece "
              f"{contenido.count(IMPORT_ANCLA_VIEJO)} veces (esperado: 1)")
        return 1
    contenido_nuevo = contenido.replace(IMPORT_ANCLA_VIEJO, IMPORT_ANCLA_NUEVO, 1)
    if "import unicodedata\n" not in contenido_nuevo:
        print("[ABORT] La edición 1 no se aplicó correctamente")
        return 1
    print("[OK]  Edición 1 aplicada en memoria.")
    print()

    # 5. Edición 2: insertar bloque
    print("Aplicando edición 2: insertar bloque sub-bloques v18...")
    if contenido_nuevo.count(INSERCION_ANCLA) != 1:
        print(f"[ABORT] Ancla de inserción aparece "
              f"{contenido_nuevo.count(INSERCION_ANCLA)} veces (esperado: 1)")
        return 1
    # El bloque va entre el cierre de RUIDO_FIRMA y "# ── Calificadores ──"
    # La ancla incluye ambas zonas. Reemplazamos por: zona1 + bloque + zona2
    cierre_ruido_firma = (
        '    "petracchi", "zaffaroni", "argibay", "fayt", "boggiano",\n'
        '    "belluscio", "lópez", "vázquez", "nazareno",\n'
        "}\n"
    )
    inicio_calificadores = (
        "# ── Calificadores ─────────────────────────────────────────────────────────────"
    )
    bloque_a_insertar = (
        cierre_ruido_firma + "\n" + bloque_nuevo.rstrip() + "\n\n" + inicio_calificadores
    )
    contenido_final = contenido_nuevo.replace(INSERCION_ANCLA, bloque_a_insertar, 1)
    if MARCADOR_BLOQUE_PRESENTE not in contenido_final:
        print("[ABORT] La edición 2 no se aplicó correctamente")
        return 1
    print("[OK]  Edición 2 aplicada en memoria.")
    print()

    # 6. Verificar que el resultado tenga sentido (compila)
    print("Verificando que el archivo resultante compila...")
    try:
        compile(contenido_final, str(PARSER_PATH), "exec")
        print("[OK]  Compila sin errores de sintaxis.")
    except SyntaxError as e:
        print(f"[ABORT] El archivo resultante tiene error de sintaxis: {e}")
        print("        No escribo nada al disco. parser.py queda intacto.")
        return 1
    print()

    # 7. Escribir
    escribir_archivo(PARSER_PATH, contenido_final)
    print(f"[OK]  parser.py actualizado.")
    print()

    # 8. Verificación post-escritura
    print("Verificación post-escritura:")
    estado_final = EstadoArchivo(cargar_archivo(PARSER_PATH, "parser.py"))
    print(estado_final.reporte())
    print()

    if estado_final.estado() == "ya_parchado":
        print("=" * 60)
        print("TANDA 1 APLICADA CORRECTAMENTE")
        print("=" * 60)
        print()
        print("Próximo paso: validar con")
        print("    python test_tanda1.py")
        return 0
    else:
        print("[ABORT] Estado post-escritura inesperado. Revertí con:")
        print("        python aplicar_tanda1.py --revert")
        return 1


def main():
    args = sys.argv[1:]
    if "--check" in args:
        verificar_solo()
        return 0
    if "--revert" in args:
        revertir()
        return 0
    return aplicar()


if __name__ == "__main__":
    sys.exit(main())
