"""
ocr_tomos_335_336.py
====================
Extrae texto de los tomos 335 y 336 de la CSJN.
- Páginas con texto embebido: usa PyMuPDF (extracción directa).
- Páginas sin texto (imagen): rasteriza y aplica Tesseract OCR.

Requisitos:
    pip install PyMuPDF pytesseract Pillow
    Tesseract instalado: https://github.com/UB-Mannheim/tesseract/wiki
    Datos de idioma español: al instalar Tesseract, tildar "Spanish" en Additional language data.

Uso:
    python ocr_tomos_335_336.py --test          # procesa 5 páginas de prueba
    python ocr_tomos_335_336.py                 # procesa todos los tomos
    python ocr_tomos_335_336.py --umbral 200    # chars mínimos para considerar página con texto
"""

import argparse
import os
import sys
import io
import time

# ── Verificar dependencias ──────────────────────────────────────
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Falta PyMuPDF: pip install PyMuPDF")
    sys.exit(1)

try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("Falta pytesseract o Pillow: pip install pytesseract Pillow")
    sys.exit(1)

# ── Ruta de Tesseract en Windows (ajustar si es necesario) ──────
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\guill\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

def encontrar_tesseract():
    """Busca el ejecutable de Tesseract."""
    # Primero probar si ya está en PATH
    try:
        version = pytesseract.get_tesseract_version()
        print(f"  Tesseract encontrado en PATH: v{version}")
        return True
    except Exception:
        pass

    # Buscar en rutas conocidas
    for ruta in TESSERACT_PATHS:
        if os.path.isfile(ruta):
            pytesseract.pytesseract.tesseract_cmd = ruta
            try:
                version = pytesseract.get_tesseract_version()
                print(f"  Tesseract encontrado: {ruta} (v{version})")
                return True
            except Exception:
                continue

    return False


def verificar_idioma_español():
    """Verifica si Tesseract tiene datos de español instalados."""
    try:
        langs = pytesseract.get_languages()
        if "spa" in langs:
            print("  Idioma español (spa): disponible")
            return True
        else:
            print(f"  Idioma español NO disponible. Idiomas: {langs}")
            print("  Reinstalar Tesseract tildando 'Spanish' en language data.")
            return False
    except Exception as e:
        print(f"  No se pudo verificar idiomas: {e}")
        return False


UMBRAL_CHARS = 100  # Páginas con menos chars que esto → OCR
DPI_OCR = 300       # Resolución para rasterizar


def extraer_pagina(page, usar_ocr=False):
    """Extrae texto de una página. Si usar_ocr=True, rasteriza y aplica Tesseract."""
    if not usar_ocr:
        return page.get_text()

    # Rasterizar a imagen
    mat = fitz.Matrix(DPI_OCR / 72, DPI_OCR / 72)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_bytes))

    # OCR con Tesseract (español + inglés para nombres propios y citas en inglés)
    texto = pytesseract.image_to_string(img, lang="spa", config="--psm 6")
    return texto


def procesar_tomo(ruta_pdf, destino, umbral, limite_paginas=None):
    """Procesa un tomo completo. Retorna estadísticas."""
    nombre = os.path.basename(ruta_pdf)

    try:
        doc = fitz.open(ruta_pdf)
    except Exception as e:
        print(f"  ERROR abriendo {nombre}: {e}")
        return None

    total = doc.page_count
    if limite_paginas:
        total = min(total, limite_paginas)

    print(f"\n  {nombre}: {doc.page_count} páginas"
          f"{f' (procesando {total})' if limite_paginas else ''}")

    textos = []
    stats = {"texto_directo": 0, "ocr": 0, "vacias": 0}

    for i in range(total):
        page = doc[i]
        texto_directo = page.get_text()

        if len(texto_directo.strip()) >= umbral:
            # Página con texto embebido suficiente
            textos.append(texto_directo)
            stats["texto_directo"] += 1
        else:
            # Página sin texto → OCR
            texto_ocr = extraer_pagina(page, usar_ocr=True)
            if len(texto_ocr.strip()) > 10:
                textos.append(texto_ocr)
                stats["ocr"] += 1
            else:
                textos.append(texto_directo)  # Conservar lo que haya
                stats["vacias"] += 1

        # Progreso cada 50 páginas
        if (i + 1) % 50 == 0 or i == total - 1:
            pct = (i + 1) / total * 100
            print(f"    [{pct:5.1f}%] pág {i+1}/{total} "
                  f"(texto: {stats['texto_directo']}, "
                  f"ocr: {stats['ocr']}, "
                  f"vacías: {stats['vacias']})", flush=True)

    doc.close()

    # Guardar
    nombre_txt = nombre.replace(".pdf", ".txt")
    ruta_salida = os.path.join(destino, nombre_txt)
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(textos))

    size_kb = os.path.getsize(ruta_salida) / 1024
    print(f"  → {ruta_salida} ({size_kb:.0f} KB)")
    print(f"    Texto directo: {stats['texto_directo']}, "
          f"OCR: {stats['ocr']}, Vacías: {stats['vacias']}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="OCR para tomos CSJN 335-336 (páginas sin texto embebido)"
    )
    parser.add_argument("--test", action="store_true",
                        help="Procesar solo 5 páginas por tomo (prueba)")
    parser.add_argument("--umbral", type=int, default=UMBRAL_CHARS,
                        help=f"Chars mínimos para considerar página con texto (default: {UMBRAL_CHARS})")
    parser.add_argument("--destino", type=str, default=".",
                        help="Carpeta de salida (default: directorio actual)")
    parser.add_argument("--archivos", nargs="+",
                        help="PDFs a procesar (default: los 4 tomos 335-336)")

    args = parser.parse_args()

    print("=" * 60)
    print("OCR Tomos CSJN 335-336")
    print("=" * 60)

    # Verificar Tesseract
    print("\nVerificando Tesseract...")
    if not encontrar_tesseract():
        print("\n  Tesseract NO encontrado.")
        print("  Instalalo desde: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Al instalar, tildá 'Spanish' en Additional language data.")
        sys.exit(1)

    if not verificar_idioma_español():
        print("  Continuando sin español (resultados pueden ser peores)")

    # Archivos
    if args.archivos:
        archivos = args.archivos
    else:
        archivos = [
            r"C:\Users\guill\Downloads\LibroVol335.1.pdf",
            r"C:\Users\guill\Downloads\LibroVol335.2.pdf",
            r"C:\Users\guill\Downloads\LibroVol336.1.pdf",
            r"C:\Users\guill\Downloads\LibroVol336.2.pdf",
        ]

    # Verificar que existen
    existentes = [a for a in archivos if os.path.isfile(a)]
    faltantes = [a for a in archivos if not os.path.isfile(a)]
    if faltantes:
        print(f"\nArchivos no encontrados:")
        for f in faltantes:
            print(f"  {f}")
    if not existentes:
        print("No hay archivos para procesar.")
        sys.exit(1)

    # Crear destino
    os.makedirs(args.destino, exist_ok=True)

    limite = 5 if args.test else None
    if args.test:
        print(f"\n*** MODO TEST: solo 5 páginas por tomo ***")

    print(f"\nUmbral texto/OCR: {args.umbral} chars")
    print(f"Destino: {os.path.abspath(args.destino)}")

    t0 = time.time()
    for ruta in existentes:
        procesar_tomo(ruta, args.destino, args.umbral, limite_paginas=limite)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"Completado en {elapsed/60:.1f} minutos")


if __name__ == "__main__":
    main()
