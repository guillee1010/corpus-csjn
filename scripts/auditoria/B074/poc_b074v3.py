"""
PoC B074 v3 — Guarda posicional en fallback firma_actual de detectar_fin_real.

Diagnóstico H050:
  Los 22 casos afectados comparten la misma estructura: el bloque empieza
  con residuo del caso anterior (dispositivo + firma + metadata), seguido
  del caso actual. buscar_atras(lfc→li) encuentra la firma del caso
  ANTERIOR y corta prematuramente.

Fix:
  Buscar primera RE_APERTURA ("FALLO/SENTENCIA DE LA CORTE SUPREMA")
  dentro de [li, lfc]. Si buscar_atras encuentra firma ANTES de esa
  apertura, rechazarla (es del caso anterior) y reintentar con rango
  restringido [primera_apertura, lfc]. Si no hay firma en ese rango,
  caer al buscar_adelante existente.

  Si primera_apertura=None (sin apertura en el bloque), no hacer nada
  (preservar baseline).

Resultado esperado:
  3+ mejoras (casos con apertura donde firma_prev < apertura).
  0 regresiones (casos sin apertura quedan idénticos al baseline).

Uso:
  python poc_b074v3.py --parser <parser.py>
                       --localizados <fallos_localizados.csv>
                       --mapa <mapa_paginas.csv>
                       --corpus <corpus/>
                       --baseline <csjn_casos.csv>
                       --output <poc_b074v3_diff.csv>
"""
import sys
import csv
import subprocess
import tempfile
import shutil
import time
import re
from pathlib import Path
import argparse


def patch_parser(parser_src: Path, parser_dst: Path):
    """Aplica el parche B074v3 a parser.py."""
    code = parser_src.read_text(encoding='utf-8')

    # ── Localizar el bloque a parchear ──────────────────────────────────────
    # Buscamos el fallback firma_actual en detectar_fin_real.
    # Código baseline (líneas ~1600-1606):
    #
    #     # Fallback: firma del fallo actual
    #     k = buscar_atras(linea_es_firma_de_juez, lfc, li)
    #     if k is not None:
    #         return (k, "fin_por_firma_actual", "firma_actual")
    #     k = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    #     if k is not None:
    #         return (k, "fin_por_firma_actual", "firma_actual")

    old_block = '''    # Fallback: firma del fallo actual
    k = buscar_atras(linea_es_firma_de_juez, lfc, li)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")
    k = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")'''

    new_block = '''    # ── B074v3: guarda posicional en fallback firma_actual ─────────────
    # Buscar primera RE_APERTURA dentro de las primeras 40 líneas del
    # bloque como lower-bound. El límite de 40 evita capturar apertura
    # del caso SIGUIENTE en bloques grandes (el residuo del caso anterior
    # nunca supera ~15 líneas, y la apertura del caso actual cae en las
    # primeras ~25).
    _primera_apertura = None
    _limite_busqueda_apertura = min(li + 40, lfc + 1)
    for _j in range(li, _limite_busqueda_apertura):
        if RE_APERTURA.match(lines[_j].strip()):
            _primera_apertura = _j
            break

    # Fallback: firma del fallo actual (con guarda B074v3)
    k = buscar_atras(linea_es_firma_de_juez, lfc, li)
    if k is not None:
        if _primera_apertura is None or k >= _primera_apertura:
            # Firma después de la apertura (o sin apertura): aceptar
            return (k, "fin_por_firma_actual", "firma_actual")
        # Firma rechazada: antes de la apertura, del caso anterior.
        # Reintentar con rango restringido [primera_apertura, lfc]
        k2 = buscar_atras(linea_es_firma_de_juez, lfc, _primera_apertura)
        if k2 is not None:
            return (k2, "fin_por_firma_actual", "firma_actual")
    k = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k is not None:
        return (k, "fin_por_firma_actual", "firma_actual")'''

    if old_block not in code:
        print("ERROR: no se encontró el bloque a parchear en parser.py.")
        print("Verificar que el parser sea la versión post-H049.")
        sys.exit(1)

    patched = code.replace(old_block, new_block)
    parser_dst.write_text(patched, encoding='utf-8')
    print(f"Parser parcheado: {parser_dst}")


def run_parser(parser_path, localizados, mapa, corpus, output):
    """Corre el parser y devuelve el CSV como lista de dicts."""
    cmd = [
        sys.executable, str(parser_path),
        '--localizados', str(localizados),
        '--mapa', str(mapa),
        '--corpus', str(corpus),
        '--output', str(output),
    ]
    import os
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print("ERROR corriendo parser:")
        print(result.stderr)
        sys.exit(1)
    rows = {}
    with open(output, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            rows[row['caso_id_canonico']] = row
    return rows


def diff_results(baseline_rows, new_rows, output_path):
    """Genera diff entre baseline y nuevo."""
    diffs = []
    campos_check = [
        'voting_pattern', 'n_jueces', 'jueces', 'jueces_conocidos',
        'linea_fin_real', 'pista_fin', 'firma_raw',
    ]
    for cid, base in baseline_rows.items():
        nuevo = new_rows.get(cid)
        if not nuevo:
            continue
        for campo in campos_check:
            bv = base.get(campo, '')
            nv = nuevo.get(campo, '')
            if bv != nv:
                # Clasificar
                if campo == 'voting_pattern':
                    if bv == 'sin_firma' and nv != 'sin_firma':
                        tipo = 'MEJORA'
                    elif bv != 'sin_firma' and nv == 'sin_firma':
                        tipo = 'REGRESION'
                    else:
                        tipo = 'CAMBIO'
                elif campo == 'n_jueces':
                    bi, ni = int(bv or 0), int(nv or 0)
                    if ni > bi and bi > 0:
                        tipo = 'MEJORA_JUECES'
                    elif ni < bi:
                        tipo = 'REGRESION'
                    elif bi == 0 and ni > 0:
                        tipo = 'MEJORA'
                    else:
                        tipo = 'CAMBIO'
                elif campo == 'linea_fin_real':
                    tipo = 'LFR_CAMBIO'
                elif campo == 'pista_fin':
                    tipo = 'PISTA_CAMBIO'
                else:
                    tipo = 'CAMBIO'
                diffs.append({
                    'caso_id': cid,
                    'tipo': tipo,
                    'campo': campo,
                    'base': bv,
                    'nuevo': nv,
                })

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['caso_id', 'tipo', 'campo', 'base', 'nuevo'])
        writer.writeheader()
        writer.writerows(sorted(diffs, key=lambda d: (d['caso_id'], d['campo'])))

    # Resumen
    mejoras = {d['caso_id'] for d in diffs if d['tipo'] == 'MEJORA'}
    regresiones = {d['caso_id'] for d in diffs if d['tipo'] == 'REGRESION'}
    mejora_j = {d['caso_id'] for d in diffs if d['tipo'] == 'MEJORA_JUECES'} - mejoras - regresiones
    lfr_only = {d['caso_id'] for d in diffs
                if d['tipo'] in ('LFR_CAMBIO', 'PISTA_CAMBIO', 'CAMBIO')} - mejoras - regresiones - mejora_j

    print(f"\n=== RESUMEN B074v3 ===")
    print(f"Total casos con cambios: {len(set(d['caso_id'] for d in diffs))}")
    print(f"  MEJORA (sf→firma): {len(mejoras)}")
    for c in sorted(mejoras):
        n = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'n_jueces'), None)
        print(f"    {c}: n_jueces {n['base']}→{n['nuevo']}" if n else f"    {c}")
    print(f"  REGRESION: {len(regresiones)}")
    for c in sorted(regresiones):
        n = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'n_jueces'), None)
        print(f"    {c}: n_jueces {n['base']}→{n['nuevo']}" if n else f"    {c}")
    print(f"  MEJORA_JUECES: {len(mejora_j)}")
    for c in sorted(mejora_j):
        n = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'n_jueces'), None)
        print(f"    {c}: n_jueces {n['base']}→{n['nuevo']}" if n else f"    {c}")
    print(f"  Solo LFR/pista/cambio: {len(lfr_only)}")
    print(f"\nDiff escrito en: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parser', required=True, help='parser.py original')
    parser.add_argument('--localizados', required=True)
    parser.add_argument('--mapa', required=True)
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--baseline', required=True, help='csjn_casos.csv baseline')
    parser.add_argument('--output', required=True, help='Archivo diff de salida')
    args = parser.parse_args()

    # Leer baseline
    print("Leyendo baseline...")
    baseline_rows = {}
    with open(args.baseline, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            baseline_rows[row['caso_id_canonico']] = row
    print(f"  {len(baseline_rows)} casos en baseline.")

    # Parchear parser
    parser_src = Path(args.parser)
    parser_patched = parser_src.parent / 'parser_b074v3.py'
    patch_parser(parser_src, parser_patched)

    # Correr parser parcheado
    output_new = Path(args.output).parent / 'csjn_casos_b074v3.csv'
    print(f"\nCorriendo parser parcheado...")
    new_rows = run_parser(
        parser_patched,
        args.localizados, args.mapa, args.corpus,
        output_new,
    )
    print(f"  {len(new_rows)} casos en output parcheado.")

    # Diff
    print("\nGenerando diff...")
    diff_results(baseline_rows, new_rows, args.output)


if __name__ == '__main__':
    main()
