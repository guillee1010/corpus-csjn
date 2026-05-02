"""
Auditoría de votos clasificados como 'indeterminado'.
=====================================================

Toma una muestra aleatoria del CSV de votos y la guarda en un archivo de
texto legible. Permite identificar a mano qué patrones está perdiendo la
función `clasificar_tipo_voto`.

Uso:
    python auditar_indeterminados.py csjn_casos_v12_votos.csv

Genera un archivo `auditoria_indeterminados.txt` con 30 votos seleccionados
de forma estratificada por word count (10 cortos, 10 medios, 10 largos),
para cubrir todo el rango de casos posibles.
"""

import csv
import random
import sys
from pathlib import Path


def main(csv_path):
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["tipo_voto_sep"] == "indeterminado":
                rows.append(r)

    print(f"Total indeterminados: {len(rows)}")

    # Estratificar por wc_voto: 10 cortos (<200), 10 medios (200-1000),
    # 10 largos (>1000). Esto nos da visibilidad sobre qué tipo de voto se
    # está perdiendo el clasificador.
    cortos = [r for r in rows if int(r["wc_voto"]) < 200]
    medios = [r for r in rows if 200 <= int(r["wc_voto"]) < 1000]
    largos = [r for r in rows if int(r["wc_voto"]) >= 1000]

    print(f"  Cortos (<200 palabras):    {len(cortos)}")
    print(f"  Medios (200-1000):         {len(medios)}")
    print(f"  Largos (>=1000):           {len(largos)}")

    random.seed(42)  # determinístico
    muestra_cortos = random.sample(cortos, min(10, len(cortos)))
    muestra_medios = random.sample(medios, min(10, len(medios)))
    muestra_largos = random.sample(largos, min(10, len(largos)))

    out_path = Path("auditoria_indeterminados.txt")
    with out_path.open("w", encoding="utf-8") as out:
        for etiqueta, muestra in [
            ("CORTOS (< 200 palabras)", muestra_cortos),
            ("MEDIOS (200 - 1000 palabras)", muestra_medios),
            ("LARGOS (>= 1000 palabras)", muestra_largos),
        ]:
            out.write("=" * 78 + "\n")
            out.write(f"{etiqueta}\n")
            out.write("=" * 78 + "\n\n")
            for i, r in enumerate(muestra, 1):
                out.write(f"--- {i}/{len(muestra)} ---\n")
                out.write(f"caso_id:           {r['caso_id']}\n")
                out.write(f"juez:              {r['juez']}\n")
                out.write(f"posicion:          {r['posicion']}\n")
                out.write(f"wc_voto:           {r['wc_voto']}\n")
                out.write(f"is_merit_decision: {r['is_merit_decision']}\n")
                out.write(f"outcome:           {r['outcome']}\n")
                out.write(f"\nTEXTO:\n{r['texto_voto']}\n\n")

    print(f"\nMuestra escrita en: {out_path.resolve()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python auditar_indeterminados.py <csv_de_votos>")
        sys.exit(1)
    main(sys.argv[1])
