"""
Extractor de contexto del corpus para los 22 casos afectados por B074.
Uso: python extractor_b074.py --corpus <ruta_corpus> --casos <csjn_casos.csv> --diff <poc_b074_diff.csv> --output <salida.md>

Para cada caso extrae:
  - 30 líneas desde linea_inicio (inicio del bloque)
  - 10 líneas alrededor de lfr_base (donde el baseline cortó)
  - 10 líneas alrededor de lf (fin del catálogo)
"""
import csv
import argparse
from pathlib import Path
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus', required=True, help='Ruta al directorio corpus/')
    parser.add_argument('--casos', required=True, help='csjn_casos.csv')
    parser.add_argument('--diff', required=True, help='poc_b074_diff.csv')
    parser.add_argument('--output', required=True, help='Archivo .md de salida')
    args = parser.parse_args()

    # Leer casos afectados del diff
    afectados = set()
    diff_data = defaultdict(dict)
    with open(args.diff, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            afectados.add(row['caso_id'])
            if 'linea_fin_real' in (row.get('campo') or ''):
                diff_data[row['caso_id']]['lfr_new'] = int(row['nuevo'])

    # Leer metadata de los casos
    meta = {}
    with open(args.casos, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['caso_id_canonico'] in afectados:
                meta[row['caso_id_canonico']] = row

    # Agrupar por source_file
    por_archivo = defaultdict(list)
    for cid, m in meta.items():
        por_archivo[m['source_file']].append(cid)

    # Procesar cada archivo
    output_lines = ['# Extracción B074 — contexto de los 22 casos afectados\n\n']

    corpus_path = Path(args.corpus)
    for source_file, caso_ids in sorted(por_archivo.items()):
        filepath = corpus_path / source_file
        if not filepath.exists():
            # Buscar en subdirectorios
            found = list(corpus_path.rglob(source_file))
            if found:
                filepath = found[0]
            else:
                output_lines.append(f'## ARCHIVO NO ENCONTRADO: {source_file}\n\n')
                continue

        lines = filepath.read_text(encoding='utf-8').split('\n')

        for cid in sorted(caso_ids):
            m = meta[cid]
            li = int(m['linea_inicio'])
            lf = int(m['linea_fin'])
            lfr = int(m['linea_fin_real'])
            lfr_new = diff_data.get(cid, {}).get('lfr_new', None)

            output_lines.append(f'## {cid}\n\n')
            output_lines.append(f'- **source:** {source_file}\n')
            output_lines.append(f'- **li={li}, lf={lf}, lfr_base={lfr}** (span={lfr-li})\n')
            if lfr_new:
                output_lines.append(f'- **lfr_new={lfr_new}** (span_new={lfr_new-li})\n')
            output_lines.append(f'- vp={m["voting_pattern"]}, n_jueces={m["n_jueces"]}\n')
            output_lines.append(f'- pista={m["pista_fin"]}, apertura={m["apertura_tipo"]}\n')
            output_lines.append(f'- firma_raw: {m["firma_raw"][:80]}\n\n')

            # Bloque A: primeras 30 líneas desde li
            end_a = min(li + 30, len(lines))
            output_lines.append(f'### Bloque inicio (li={li} a {end_a-1})\n\n```\n')
            for k in range(li, end_a):
                marker = ''
                if k == lfr:
                    marker = '  ◄◄◄ lfr_base'
                if lfr_new and k == lfr_new:
                    marker += '  ◄◄◄ lfr_new'
                output_lines.append(f'{k:6d} | {lines[k]}{marker}\n')
            output_lines.append('```\n\n')

            # Bloque B: alrededor de lfr_base (±5)
            if lfr > li + 30:  # solo si no está ya cubierto
                start_b = max(li, lfr - 5)
                end_b = min(len(lines), lfr + 6)
                output_lines.append(f'### Zona lfr_base (±5 de {lfr})\n\n```\n')
                for k in range(start_b, end_b):
                    marker = '  ◄◄◄ lfr_base' if k == lfr else ''
                    output_lines.append(f'{k:6d} | {lines[k]}{marker}\n')
                output_lines.append('```\n\n')

            # Bloque C: alrededor de lf (±5), solo si lf > lfr + 10
            if lf > lfr + 10:
                start_c = max(li, lf - 5)
                end_c = min(len(lines), lf + 6)
                output_lines.append(f'### Zona lf catálogo (±5 de {lf})\n\n```\n')
                for k in range(start_c, end_c):
                    marker = '  ◄◄◄ lf' if k == lf else ''
                    output_lines.append(f'{k:6d} | {lines[k]}{marker}\n')
                output_lines.append('```\n\n')

            # Bloque D: zona de lfr_new si existe y no está cubierta
            if lfr_new and lfr_new > end_a and lfr_new != lfr:
                start_d = max(li, lfr_new - 5)
                end_d = min(len(lines), lfr_new + 6)
                output_lines.append(f'### Zona lfr_new (±5 de {lfr_new})\n\n```\n')
                for k in range(start_d, end_d):
                    marker = '  ◄◄◄ lfr_new' if k == lfr_new else ''
                    output_lines.append(f'{k:6d} | {lines[k]}{marker}\n')
                output_lines.append('```\n\n')

            output_lines.append('---\n\n')

    with open(args.output, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

    print(f'Extraído: {len(meta)} casos → {args.output}')
    print(f'Archivos procesados: {len(por_archivo)}')

if __name__ == '__main__':
    main()
