# buscar_firmas_corpus.py
# Escanea TODOS los .md del corpus buscando lineas que parezcan firma de Procurador.
# Estrategia: una linea de firma tipica termina con "Buenos Aires, [fecha]. [Nombre]." o
# solo "[Nombre]." o "[Nombre Apellido]." en linea corta. Filtramos las lineas que ya
# matcheamos (Casal/Monti/Abramovich/Cosarin/Righi) y mostramos las que tienen ese formato
# pero con OTROS apellidos al final.

import re
from pathlib import Path
from collections import Counter

CORPUS_DIR = Path("markdowns_v2")
OUTPUT = Path("firmas_posibles_corpus.txt")

# Apellidos ya conocidos (no nos interesan, ya los detectamos)
APELLIDOS_CONOCIDOS = {"casal", "monti", "abramovich", "cosarin", "righi"}

# Una linea tipo firma de procurador tiene estas caracteristicas:
# - corta (menos de 100 chars)
# - termina con palabra capitalizada seguida de punto o nada
# - opcionalmente precedida por "Buenos Aires, [fecha]." o por mayoria de minusculas
# Patron: ultima palabra es un apellido capitalizado, posiblemente precedido por nombres
RE_FIRMA_GENERICA = re.compile(
    r"^.{0,80}\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)\s*\.?\s*$"
)

# Indicadores fuertes de que es firma (no parrafo cualquiera):
# - contiene "Buenos Aires" + fecha
# - linea muy corta (menos de 50 chars) con solo nombre propio
RE_FECHA_BUENOS_AIRES = re.compile(
    r"Buenos Aires[,]?\s+\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4}",
    re.I
)

apellidos_candidatos = Counter()  # apellido -> cuantas veces aparece como ultima palabra
ejemplos_por_apellido = {}        # apellido -> lista de (archivo, linea, texto)

archivos = sorted(CORPUS_DIR.glob("LibroVol*.md"))
print(f"Procesando {len(archivos)} archivos...")

for path in archivos:
    lines = path.read_text(encoding="utf-8").split("\n")
    for i, ln in enumerate(lines, start=1):
        stripped = ln.strip()
        if not stripped or len(stripped) > 100:
            continue

        m = RE_FIRMA_GENERICA.match(stripped)
        if not m:
            continue

        # La ultima palabra capitalizada es probable apellido
        nombre_completo = m.group(1)
        ultima_palabra = nombre_completo.split()[-1]
        apellido_lower = ultima_palabra.lower()

        # Filtrar conocidos
        if apellido_lower in APELLIDOS_CONOCIDOS:
            continue

        # Indicador fuerte: si la linea contiene "Buenos Aires + fecha", muy probable firma
        tiene_fecha = bool(RE_FECHA_BUENOS_AIRES.search(stripped))
        # O linea muy corta (solo nombre)
        es_corta_nombre = len(stripped) < 50

        if tiene_fecha or es_corta_nombre:
            apellidos_candidatos[ultima_palabra] += 1
            if ultima_palabra not in ejemplos_por_apellido:
                ejemplos_por_apellido[ultima_palabra] = []
            if len(ejemplos_por_apellido[ultima_palabra]) < 3:
                ejemplos_por_apellido[ultima_palabra].append(
                    (path.name, i, stripped)
                )

# Output
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("FIRMAS POSIBLES DE PROCURADOR (apellidos no conocidos)\n")
    f.write("=" * 70 + "\n\n")
    f.write("Apellidos ya detectados (filtrados): Casal, Monti, Abramovich, Cosarin, Righi\n\n")
    f.write(f"Apellidos candidatos encontrados (con >=5 ocurrencias):\n")
    f.write("-" * 70 + "\n")

    candidatos_significativos = [(ap, n) for ap, n in apellidos_candidatos.most_common()
                                  if n >= 5]
    f.write(f"Total: {len(candidatos_significativos)}\n\n")

    for apellido, count in candidatos_significativos:
        f.write(f"\n{apellido}: {count} ocurrencias\n")
        f.write("  Ejemplos:\n")
        for archivo, linea, texto in ejemplos_por_apellido[apellido]:
            f.write(f"    {archivo} L{linea}: {texto}\n")

print(f"Output: {OUTPUT}")
print(f"Apellidos candidatos con >=5 ocurrencias: {len(candidatos_significativos)}")
