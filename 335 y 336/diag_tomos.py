import fitz

archivos = [
    r"C:\Users\guill\Downloads\LibroVol335.1.pdf",
    r"C:\Users\guill\Downloads\LibroVol335.2.pdf",
    r"C:\Users\guill\Downloads\LibroVol336.1.pdf",
    r"C:\Users\guill\Downloads\LibroVol336.2.pdf"
]

for ruta in archivos:
    try:
        doc = fitz.open(ruta)
    except Exception as e:
        print(f"{ruta}: no se pudo abrir - {e}")
        continue

    nombre = ruta.split("\\")[-1]
    print(f"\n{'='*60}")
    print(f"{nombre}: {doc.page_count} pags")

    for p in [0, doc.page_count//4, doc.page_count//2,
              3*doc.page_count//4, doc.page_count-1]:
        page = doc[p]
        texto = page.get_text()
        imgs = page.get_images(full=True)
        print(f"  Pag {p+1}: {len(texto)} chars, {len(imgs)} imgs")
        print(f"    inicio: {repr(texto[:150])}")

    doc.close()
