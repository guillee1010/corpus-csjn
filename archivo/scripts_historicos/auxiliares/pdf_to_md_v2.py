"""
pdf_to_md_v2.py — conversión PDF → markdown con preservación de columnas.

Reemplaza a pdf_to_md.py. La diferencia clave: detecta si la página tiene
una o dos columnas y, si tiene dos, procesa cada columna por separado en
vez de aplastarlas con un sort por bandas horizontales.

Heurística de detección de columnas
-----------------------------------
Para cada página, calcula la mediana de los anchos de los bloques de
texto. Si los bloques se concentran en dos clusters horizontales bien
separados (uno en la mitad izquierda, otro en la mitad derecha) y la
mayoría de los bloques son angostos (menos de ~60% del ancho de página),
asume dos columnas. Si no, asume una columna.

El umbral del cluster es un punto medio dinámico: el x medio de la
página. Bloques cuyo centro está a la izquierda → columna 1; a la derecha
→ columna 2. Después se ordenan dentro de cada columna por posición Y.

Esto resuelve correctamente índices de dos columnas, cuerpos de fallos en
dos columnas, y mantiene compatibilidad con PDFs de una sola columna.

Uso (idéntico a la versión original):
    python pdf_to_md_v2.py input.pdf output.md
"""

import sys
import fitz  # PyMuPDF


def procesar_pagina(page):
    """Devuelve la lista de líneas de texto de una página, respetando columnas."""
    blocks = page.get_text("blocks")
    if not blocks:
        return []

    # Filtrar bloques vacíos
    blocks = [b for b in blocks if b[4].strip()]
    if not blocks:
        return []

    # Geometría de la página
    page_width = page.rect.width
    x_mid = page_width / 2

    # Detectar si la página es de dos columnas
    # Criterio: la mayoría (>=70%) de los bloques son "angostos" (ancho < 55% de la página)
    # Y existen bloques claramente en ambas mitades de la página
    anchos_relativos = [(b[2] - b[0]) / page_width for b in blocks]
    pct_angostos = sum(1 for a in anchos_relativos if a < 0.55) / len(anchos_relativos)

    centros_x = [(b[0] + b[2]) / 2 for b in blocks]
    hay_izq = any(cx < x_mid * 0.95 for cx in centros_x)
    hay_der = any(cx > x_mid * 1.05 for cx in centros_x)

    es_dos_columnas = pct_angostos >= 0.70 and hay_izq and hay_der

    if es_dos_columnas:
        # Separar por columnas según centro X de cada bloque
        col_izq = []
        col_der = []
        for b in blocks:
            centro = (b[0] + b[2]) / 2
            if centro < x_mid:
                col_izq.append(b)
            else:
                col_der.append(b)

        # Ordenar cada columna por posición Y (top de cada bloque)
        col_izq.sort(key=lambda b: b[1])
        col_der.sort(key=lambda b: b[1])

        # Devolver columna izquierda primero, luego derecha
        lineas = []
        for b in col_izq:
            lineas.append(b[4].strip())
        for b in col_der:
            lineas.append(b[4].strip())
        return lineas
    else:
        # Una sola columna: ordenar por Y, después por X (lectura natural)
        blocks.sort(key=lambda b: (b[1], b[0]))
        return [b[4].strip() for b in blocks]


def main():
    if len(sys.argv) != 3:
        print("Uso: python pdf_to_md_v2.py input.pdf output.md")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    try:
        doc = fitz.open(src)
        out_lines = []

        for page in doc:
            lineas_pagina = procesar_pagina(page)
            out_lines.extend(lineas_pagina)
            out_lines.append("")  # separador entre páginas

        doc.close()

        with open(dst, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))

        sys.exit(0)

    except Exception as e:
        print("ERROR: " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
