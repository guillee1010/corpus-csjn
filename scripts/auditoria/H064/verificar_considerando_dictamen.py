"""Verificar si 'Considerando:' post-separador aparece dentro de dictámenes.

Busca líneas que matchearían el fix propuesto para B010:
  (?:^|[;,])\s*Considerando\s*[:.]?\s*$
y clasifica cada hit como DICTAMEN o FALLO según contexto.

Uso: python scripts/auditoria/verificar_considerando_dictamen.py
"""
import re, glob, os

RE_FIX_PROPUESTO = re.compile(r"(?:^|[;,])\s*Considerando\s*[:.]?\s*$", re.I)
RE_CONSIDERANDO_VIEJO = re.compile(r"^Considerando\s*[:.]?\s*$", re.I)
RE_DICTAMEN_INICIO = re.compile(
    r"^(?:Dictamen de la Procuración|Suprema Corte)", re.I
)
RE_FALLO_APERTURA = re.compile(r"^FALLO DE LA CORTE SUPREMA", re.I)

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")


def analizar(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()

    fname = os.path.basename(filepath)
    en_dictamen = False
    hits_fallo = []
    hits_dictamen = []
    hits_nuevos_dictamen = []  # los que el fix AGREGARÍA y están en dictamen

    for i, raw in enumerate(lines):
        line = raw.strip()

        if RE_DICTAMEN_INICIO.match(line):
            en_dictamen = True
        if RE_FALLO_APERTURA.match(line):
            en_dictamen = False

        if RE_FIX_PROPUESTO.search(line):
            es_nuevo = not RE_CONSIDERANDO_VIEJO.match(line)
            if en_dictamen:
                hits_dictamen.append((i + 1, line[:120], es_nuevo))
                if es_nuevo:
                    hits_nuevos_dictamen.append((i + 1, line[:120]))
            else:
                hits_fallo.append((i + 1, line[:120], es_nuevo))

    return {
        "fname": fname,
        "fallo": hits_fallo,
        "dictamen": hits_dictamen,
        "nuevos_dictamen": hits_nuevos_dictamen,
    }


if __name__ == "__main__":
    archivos = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.md")))
    if not archivos:
        print(f"No se encontraron .md en {CORPUS_DIR}")
        raise SystemExit(1)

    print(f"Corpus: {len(archivos)} archivos\n")
    total_fallo = 0
    total_dictamen = 0
    total_nuevos_dict = 0
    total_nuevos_fallo = 0

    for fp in archivos:
        r = analizar(fp)
        nuevos_fallo = sum(1 for _, _, es_nuevo in r["fallo"] if es_nuevo)
        total_fallo += len(r["fallo"])
        total_dictamen += len(r["dictamen"])
        total_nuevos_dict += len(r["nuevos_dictamen"])
        total_nuevos_fallo += nuevos_fallo

        if r["nuevos_dictamen"]:
            print(f"⚠️  {r['fname']}: {len(r['nuevos_dictamen'])} NUEVOS en DICTAMEN")
            for lineno, text in r["nuevos_dictamen"]:
                print(f"    L{lineno}: {text}")

        if nuevos_fallo:
            print(f"✓  {r['fname']}: +{nuevos_fallo} nuevos en fallo")

    print(f"\n--- RESUMEN ---")
    print(f"Considerando: en fallo (total):     {total_fallo}")
    print(f"Considerando: en dictamen (total):   {total_dictamen}")
    print(f"NUEVOS en fallo (delta del fix):     +{total_nuevos_fallo}")
    print(f"NUEVOS en dictamen (FALSOS POS):     {total_nuevos_dict}")

    if total_nuevos_dict == 0:
        print("\n✅ Fix seguro: 0 falsos positivos en dictamen.")
    else:
        print(f"\n❌ {total_nuevos_dict} falsos positivos en dictamen — revisar antes de aplicar.")
