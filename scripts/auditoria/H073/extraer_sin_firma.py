"""
extraer_sin_firma.py — H073
Extrae los bloques de todos los casos sin_firma a un solo .md diagnóstico.
Para cada caso muestra:
  - Metadata (caso_id, wc, pista_fin, span)
  - El bloque completo (linea_inicio → linea_fin_real)
  - 50 líneas DESPUÉS de linea_fin_real (zona cortada, donde debería estar la firma)

Uso:
    python extraer_sin_firma.py
    (ejecutar desde la raíz del repo corpus-csjn)
"""

import csv
import os

CSV_PATH = "output/parser/csjn_casos.csv"
CORPUS_DIR = "corpus"
OUTPUT_PATH = "output/diagnostico/sin_firma_bloques.md"
LINEAS_POST = 50  # líneas a mostrar después del corte


def main():
    # Leer CSV
    with open(CSV_PATH, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    sin_firma = [r for r in rows if r["voting_pattern"] == "sin_firma"]
    sin_firma.sort(key=lambda r: (r["source_file"], int(r["linea_inicio"])))

    print(f"sin_firma: {len(sin_firma)} casos")

    # Cache de archivos fuente
    cache = {}

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        out.write(f"# Diagnóstico sin_firma — {len(sin_firma)} casos\n\n")
        out.write("Extraído por `extraer_sin_firma.py` (H073).\n")
        out.write("Para cada caso: bloque completo + 50 líneas post-corte.\n")
        out.write("La línea `>>> CORTE AQUÍ <<<` marca linea_fin_real.\n\n---\n\n")

        for r in sin_firma:
            cid = r["caso_id_canonico"]
            sf = r["source_file"]
            li = int(r["linea_inicio"])
            lfr = int(r["linea_fin_real"])
            lf = int(r["linea_fin"])
            wc = r["word_count"]
            pista = r["pista_fin"]
            status = r["status_fin"]
            outcome = r["outcome"]
            name = r["case_name_indice"]

            # Cargar archivo fuente
            if sf not in cache:
                path = os.path.join(CORPUS_DIR, sf)
                if not os.path.exists(path):
                    print(f"  WARN: {path} no existe, saltando {cid}")
                    continue
                with open(path, encoding="utf-8") as fmd:
                    cache[sf] = fmd.readlines()

            lines = cache[sf]
            n = len(lines)

            # Bloque: linea_inicio → linea_fin_real
            bloque = lines[li:lfr + 1]
            # Post-corte: linea_fin_real+1 → +LINEAS_POST
            post_start = lfr + 1
            post_end = min(post_start + LINEAS_POST, n)
            post = lines[post_start:post_end]

            out.write(f"## {cid} — {name}\n\n")
            out.write(f"- **wc:** {wc} | **span:** {lfr - li} líneas\n")
            out.write(f"- **outcome:** {outcome} | **pista_fin:** {pista}\n")
            out.write(f"- **status_fin:** {status}\n")
            out.write(f"- **source:** `{sf}` L{li}–L{lfr} (lf_cat={lf})\n\n")

            # Últimas 30 líneas del bloque (no todo, para no inflar el archivo)
            if len(bloque) > 30:
                out.write(f"*(bloque: {len(bloque)} líneas, mostrando últimas 30)*\n\n")
                out.write("```\n")
                for i, ln in enumerate(bloque[-30:]):
                    lineno = lfr - 29 + i
                    out.write(f"L{lineno:>6}  {ln.rstrip()}\n")
            else:
                out.write(f"*(bloque completo: {len(bloque)} líneas)*\n\n")
                out.write("```\n")
                for i, ln in enumerate(bloque):
                    lineno = li + i
                    out.write(f"L{lineno:>6}  {ln.rstrip()}\n")

            out.write(f"\n{'='*60}\n")
            out.write(f">>> CORTE AQUÍ (linea_fin_real = {lfr}) <<<\n")
            out.write(f"{'='*60}\n\n")

            # Post-corte
            for i, ln in enumerate(post):
                lineno = post_start + i
                out.write(f"L{lineno:>6}  {ln.rstrip()}\n")

            out.write("```\n\n---\n\n")

    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
