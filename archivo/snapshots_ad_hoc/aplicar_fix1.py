"""
aplicar_fix1.py — aplica Fix 1 (V1 como fuente primaria de case_name_cuerpo)
a parser.py productivo.

Sesión XIX, post-XVIII.

Qué hace:
  1. Verifica que parser.py existe y es la versión esperada.
  2. Hace backup automático: parser.py.bak_pre_fix1.
  3. Aplica 4 cambios mínimos al parser:
     A. Inserta función extraer_caratula_v1 + regex + comilla constants.
     B. Modifica el bloque case_name_cuerpo en procesar_archivo (línea ~1437).
     C. Agrega case_name_cuerpo_legacy al dict del caso normal.
     D. Agrega case_name_cuerpo_legacy al dict de sumario_con_link.
     E. Agrega case_name_cuerpo_legacy a fieldnames del CSV.
  4. Compila el resultado para verificar sintaxis. Si falla, restaura backup.
  5. Ejecuta py_compile y reporta tamaños antes/después.

Qué NO hace:
  - No corre el parser. Eso lo hacés vos manualmente después.
  - No toca ningún CSV. Solo modifica parser.py.
  - No toca firma, dispositivo, voces, sub-bloques, ni nada que no sea
    case_name_cuerpo. Fix 2 y Fix 3 son sesiones aparte.

Uso (en Windows, desde la carpeta scripts/pipeline/):
    python aplicar_fix1.py

Si algo sale mal:
    copy parser.py.bak_pre_fix1 parser.py

Auditorías A, B, C son ground truth; no se cuestionan en este script.
Auditoría B es la que valida V1: 3.859 hits = 67% del corpus, distribución
estable en los tres regímenes editoriales. Reconstrucción multi-línea
hasta 8 líneas cubre 96.9% de los casos.
"""

import sys
import shutil
import py_compile
from pathlib import Path


# ── Configuración ────────────────────────────────────────────────────────────

PARSER_PATH = Path("parser.py")
BACKUP_PATH = Path("parser.py.bak_pre_fix1")


# ── Bloques de código a insertar / cambios a hacer ───────────────────────────

# A. Función nueva + regex + constantes. Se inserta después del bloque
#    RE_PAGE_HEADER y antes de RE_TOMO. El ancla es la línea del comentario
#    "# Tomo desde nombre de archivo" (línea 158 del parser actual).

ANCLA_INSERTAR_FUNCION = "# Tomo desde nombre de archivo\nRE_TOMO          = re.compile(r\"LibroVol(\\d+)\")"

BLOQUE_FUNCION_NUEVA = '''# v18: Fix 1 — V1 como fuente primaria de case_name_cuerpo.
# Auditoría B (sesión XV) midió 3.859 hits = 67.3% del corpus con captura
# limpia. Reemplaza a find_case_name como fuente primaria. La búsqueda
# arranca desde apertura_rel hacia adelante para evitar el dictamen previo
# (donde están las citas doctrinales que rompían find_case_name viejo).

RE_VISTOS_LOS_AUTOS = re.compile(
    r'^\\s*Vistos los autos:\\s*([\\u201C\\u201D"\\u2018\\u2019\\'])',
    re.IGNORECASE
)
COMILLAS_CIERRE = '\\u201C\\u201D"\\u2018\\u2019\\''

def extraer_caratula_v1(bloque, apertura_rel, max_lineas=8):
    """
    v18: extrae la carátula desde el patrón V1 (`Vistos los autos: "X"`).
    Itera el bloque desde apertura_rel hacia adelante. En cuanto encuentra
    el marcador, reconstruye la carátula concatenando líneas hasta cerrar
    la comilla, manejando wrap por silabación. Devuelve la carátula sin
    las comillas, o "" si no hay V1.
    """
    inicio = apertura_rel if apertura_rel is not None else 0
    for i in range(inicio, len(bloque)):
        linea = bloque[i]
        m = RE_VISTOS_LOS_AUTOS.match(linea)
        if not m:
            continue
        comilla_apert = m.group(1)
        pos_apertura = linea.index(comilla_apert)
        acumulado = linea[pos_apertura + 1:].rstrip()
        m_cierre = re.search(f'[{COMILLAS_CIERRE}]', acumulado)
        if m_cierre:
            return acumulado[:m_cierre.start()]
        for j in range(i + 1, min(i + max_lineas, len(bloque))):
            sig = bloque[j].rstrip()
            if acumulado.endswith('\\u00AD') or acumulado.endswith('-'):
                acumulado = acumulado.rstrip('\\u00AD-') + sig.lstrip()
            else:
                acumulado = acumulado + ' ' + sig.lstrip()
            if re.search(f'[{COMILLAS_CIERRE}]', sig):
                pos_cierre = max(acumulado.rfind(c) for c in COMILLAS_CIERRE)
                return acumulado[:pos_cierre]
        return acumulado
    return ""

# Tomo desde nombre de archivo
RE_TOMO          = re.compile(r"LibroVol(\\d+)")'''


# B. Cambio en procesar_archivo (línea 1437 del parser actual). Reemplaza
#    el bloque que asigna case_name_cuerpo por uno que prioriza V1 con
#    fallback a find_case_name.

CASE_NAME_VIEJO = '''        # case_name del cuerpo (heurística v12). Si no hay marcador clásico
        # de apertura, no tiene sentido retroceder buscando carátula desde
        # apertura_idx (estaríamos retrocediendo desde el inicio del bloque,
        # agarrando basura del fallo anterior). En ese caso lo dejamos vacío.
        if apertura_rel is not None:
            case_name_cuerpo = find_case_name(lines, apertura_idx)
        else:
            case_name_cuerpo = ""'''

CASE_NAME_NUEVO = '''        # case_name del cuerpo. v18: Fix 1 — V1 como fuente primaria.
        #
        # Estrategia primaria: extraer_caratula_v1 busca \'Vistos los autos:
        # "X"\' desde apertura_rel hacia adelante. Cobertura medida: 67%
        # del corpus (Auditoría B, sesión XV). Captura limpia, sin las
        # citas doctrinales del dictamen que rompían find_case_name viejo.
        #
        # Fallback: find_case_name (heurística v12) cuando V1 no encuentra.
        # Si tampoco hay apertura_rel, queda vacío.
        #
        # Columna shadow case_name_cuerpo_legacy guarda lo que hubiera
        # devuelto find_case_name siempre, para auditar el diff post-fix.
        # Eliminable en una corrida posterior cuando el fix esté validado.
        if apertura_rel is not None:
            case_name_cuerpo_legacy = find_case_name(lines, apertura_idx)
            case_name_cuerpo_v1 = extraer_caratula_v1(bloque, apertura_rel)
            case_name_cuerpo = case_name_cuerpo_v1 or case_name_cuerpo_legacy
        else:
            case_name_cuerpo_legacy = ""
            case_name_cuerpo = ""'''


# C. Cambio en el dict del caso normal (línea 1583-1584 del parser actual).
#    Agrega case_name_cuerpo_legacy después de case_name_cuerpo.

DICT_CASO_VIEJO = '''            "case_name_indice":       nombres_indice,
            "case_name_cuerpo":       case_name_cuerpo,
            "date":                   fecha_str,'''

DICT_CASO_NUEVO = '''            "case_name_indice":       nombres_indice,
            "case_name_cuerpo":       case_name_cuerpo,
            "case_name_cuerpo_legacy": case_name_cuerpo_legacy,
            "date":                   fecha_str,'''


# D. Cambio en construir_caso_sumario_link (línea 1240-1242 del parser actual).
#    Agrega case_name_cuerpo_legacy como "" para que el DictWriter no falle.

DICT_SUMARIO_VIEJO = '''        "case_name_indice":       nombres_indice,
        "case_name_cuerpo":       "",
        "date":                   "",'''

DICT_SUMARIO_NUEVO = '''        "case_name_indice":       nombres_indice,
        "case_name_cuerpo":       "",
        "case_name_cuerpo_legacy": "",
        "date":                   "",'''


# E. Cambio en fieldnames del CSV (línea 1801-1802 del parser actual).
#    Agrega case_name_cuerpo_legacy a la lista de columnas.

FIELDNAMES_VIEJO = '''            "caso_id_canonico", "tomo",
            "case_name_indice", "case_name_cuerpo",
            "date", "apertura_tipo",'''

FIELDNAMES_NUEVO = '''            "caso_id_canonico", "tomo",
            "case_name_indice", "case_name_cuerpo", "case_name_cuerpo_legacy",
            "date", "apertura_tipo",'''


# ── Aplicación con verificaciones ────────────────────────────────────────────

def main():
    # 1. Verificar que parser.py existe
    if not PARSER_PATH.exists():
        print(f"[ERROR] No se encontró {PARSER_PATH} en el directorio actual.")
        print(f"        Corré este script desde scripts/pipeline/.")
        sys.exit(1)

    # 2. Leer parser.py actual
    contenido = PARSER_PATH.read_text(encoding="utf-8")
    tamaño_original = len(contenido)
    print(f"[INFO] parser.py leído: {tamaño_original:,} bytes, "
          f"{contenido.count(chr(10)):,} líneas.")

    # 3. Verificar que es una versión compatible (busca anclas conocidas)
    anclas_requeridas = [
        ("RE_VISTOS_LOS_AUTOS", "RE_VISTOS_LOS_AUTOS no debe existir todavía",
         False),  # NO debe estar
        ("def extraer_caratula_v1", "extraer_caratula_v1 no debe existir",
         False),  # NO debe estar
        (ANCLA_INSERTAR_FUNCION, "ancla para insertar función nueva", True),
        (CASE_NAME_VIEJO, "bloque case_name_cuerpo a reemplazar", True),
        (DICT_CASO_VIEJO, "dict del caso normal a modificar", True),
        (DICT_SUMARIO_VIEJO, "dict de sumario_con_link a modificar", True),
        (FIELDNAMES_VIEJO, "fieldnames del CSV a modificar", True),
    ]

    print("\n[INFO] Verificando estado del parser.py productivo...")
    for ancla, descripcion, debe_estar in anclas_requeridas:
        presente = ancla in contenido
        if presente != debe_estar:
            estado = "PRESENTE" if presente else "AUSENTE"
            esperado = "ausente" if not debe_estar else "presente"
            print(f"  [ERROR] {descripcion}: {estado} (esperado: {esperado})")
            print(f"          parser.py no es la versión esperada. Abortando.")
            sys.exit(1)
    print("  [OK] Todas las anclas verificadas.")

    # 4. Backup
    print(f"\n[INFO] Creando backup en {BACKUP_PATH}...")
    if BACKUP_PATH.exists():
        print(f"  [WARN] {BACKUP_PATH} ya existe. Sobreescribiéndolo.")
    shutil.copy2(PARSER_PATH, BACKUP_PATH)
    print(f"  [OK] Backup creado.")

    # 5. Aplicar cambios
    print("\n[INFO] Aplicando cambios...")

    # Cambio A: insertar función nueva
    nuevo = contenido.replace(
        ANCLA_INSERTAR_FUNCION,
        BLOQUE_FUNCION_NUEVA,
        1  # solo una vez
    )
    if nuevo == contenido:
        print("  [ERROR] Cambio A (insertar función) no se aplicó. Abortando.")
        sys.exit(1)
    contenido = nuevo
    print("  [OK] A. Función extraer_caratula_v1 insertada.")

    # Cambio B: case_name_cuerpo
    nuevo = contenido.replace(CASE_NAME_VIEJO, CASE_NAME_NUEVO, 1)
    if nuevo == contenido:
        print("  [ERROR] Cambio B (case_name_cuerpo) no se aplicó. Abortando.")
        sys.exit(1)
    contenido = nuevo
    print("  [OK] B. Bloque case_name_cuerpo reemplazado.")

    # Cambio C: dict del caso normal
    nuevo = contenido.replace(DICT_CASO_VIEJO, DICT_CASO_NUEVO, 1)
    if nuevo == contenido:
        print("  [ERROR] Cambio C (dict caso normal) no se aplicó. Abortando.")
        sys.exit(1)
    contenido = nuevo
    print("  [OK] C. Columna case_name_cuerpo_legacy agregada al dict del caso.")

    # Cambio D: dict de sumario_con_link
    nuevo = contenido.replace(DICT_SUMARIO_VIEJO, DICT_SUMARIO_NUEVO, 1)
    if nuevo == contenido:
        print("  [ERROR] Cambio D (dict sumario_con_link) no se aplicó. Abortando.")
        sys.exit(1)
    contenido = nuevo
    print("  [OK] D. Columna case_name_cuerpo_legacy agregada a sumario_con_link.")

    # Cambio E: fieldnames
    nuevo = contenido.replace(FIELDNAMES_VIEJO, FIELDNAMES_NUEVO, 1)
    if nuevo == contenido:
        print("  [ERROR] Cambio E (fieldnames) no se aplicó. Abortando.")
        sys.exit(1)
    contenido = nuevo
    print("  [OK] E. Columna case_name_cuerpo_legacy agregada a fieldnames.")

    # 6. Escribir archivo modificado
    PARSER_PATH.write_text(contenido, encoding="utf-8")
    tamaño_nuevo = len(contenido)
    delta = tamaño_nuevo - tamaño_original
    print(f"\n[INFO] parser.py escrito: {tamaño_nuevo:,} bytes (delta: +{delta:,}).")

    # 7. Verificar que compila
    print("\n[INFO] Verificando que el parser.py modificado compila...")
    try:
        py_compile.compile(str(PARSER_PATH), doraise=True)
        print("  [OK] parser.py compila sin errores.")
    except py_compile.PyCompileError as e:
        print(f"  [ERROR] parser.py NO compila: {e}")
        print(f"          Restaurando backup desde {BACKUP_PATH}...")
        shutil.copy2(BACKUP_PATH, PARSER_PATH)
        print(f"          Restaurado. parser.py vuelve al estado pre-fix.")
        sys.exit(1)

    print("\n" + "="*72)
    print("[OK] Fix 1 aplicado correctamente.")
    print("="*72)
    print()
    print("Próximos pasos sugeridos (en este orden):")
    print()
    print("  1. Ejecutar el parser sobre el corpus completo:")
    print("     python parser.py --localizados <ruta_localizados.csv> \\")
    print("                       --mapa <ruta_mapa.csv> \\")
    print("                       --corpus <ruta_corpus> \\")
    print("                       --output <output_test>.csv")
    print()
    print("  2. Comparar el nuevo csjn_casos.csv contra el snapshot")
    print("     csjn_casos_pre_refactor_subloques.csv. Métricas a chequear:")
    print()
    print("     - Casos donde V1 encuentra y legacy no (mejora limpia).")
    print("       Esperado: ~2.844 (los 50.3% que estaban vacíos).")
    print()
    print("     - Casos donde ambos coinciden (confirmación).")
    print()
    print("     - Casos donde V1 y legacy difieren (auditar a ojo unos pocos).")
    print()
    print("     - Casos donde V1 falla y legacy encontró algo.")
    print("       Esperado: bajo. Si es alto, hay regresión.")
    print()
    print("  3. Si los números cuadran con la Auditoría B (~67% del corpus")
    print("     tiene case_name_cuerpo capturado por V1), el fix está OK.")
    print()
    print("Para revertir:")
    print(f"     copy {BACKUP_PATH} {PARSER_PATH}")
    print()


if __name__ == "__main__":
    main()
