"""
PoC B074 v4 — Invertir orden: refinar_inicio ANTES de detectar_fin_real.

Diagnóstico H050:
  El bloque catálogo arranca en un header de página compartida e incluye
  residuo del caso anterior (dispositivo + firma + metadata). buscar_atras
  en detectar_fin_real pesca esa firma y corta el bloque prematuramente.

  refinar_inicio_por_titulo sabe recortar ese residuo (busca el título del
  caso actual), pero corre DESPUÉS de detectar_fin_real — cuando el bloque
  ya fue cortado a 8 líneas y el título no está.

Fix:
  Mover refinar_inicio_por_titulo ANTES de detectar_fin_real. Así:
  1. Bloque inicial [li, lf] — grande, título visible.
  2. refinar_inicio recorta residuo → li_refinado.
  3. detectar_fin_real(li_refinado, lf) → buscar_atras no ve el residuo.
  4. Bloque final [li_refinado, lfr].

  Sin heurísticas, sin límites arbitrarios. Usa lógica ya validada.

Uso:
  python poc_b074v4.py --parser <parser.py>
                       --localizados <fallos_localizados.csv>
                       --mapa <mapa_paginas.csv>
                       --corpus <corpus/>
                       --baseline <csjn_casos.csv>
                       --output <poc_b074v4_diff.csv>
"""
import sys
import os
import csv
import subprocess
from pathlib import Path
import argparse


def patch_parser(parser_src: Path, parser_dst: Path):
    """Aplica el parche B074v4 a parser.py."""
    code = parser_src.read_text(encoding='utf-8')

    # ── Patch 1: insertar refinar_inicio ANTES de detectar_fin_real ──────
    old_1 = """        # Extraer el bloque del fallo
        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin)
        if not bloque:
            continue  # bloque vacío (linea_inicio inválida); saltear

        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────"""

    new_1 = """        # Extraer el bloque del fallo
        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin)
        if not bloque:
            continue  # bloque vacío (linea_inicio inválida); saltear

        # ── B074: refinar linea_inicio ANTES de detectar_fin_real ────────────
        # Recorta residuo del caso anterior (firma arrastrada, metadata) para
        # que buscar_atras en detectar_fin_real no lo confunda con firma del
        # caso actual. Sobre el bloque [li, lf] (grande), refinar_inicio tiene
        # más contexto que sobre [li, lfr] (que puede ser cortísimo).
        offset_titulo, ancla_inicio = refinar_inicio_por_titulo(
            bloque, nombres_indice
        )
        if offset_titulo > 0:
            linea_inicio = int(linea_inicio) + offset_titulo
            bloque = bloque[offset_titulo:]
            if not bloque:
                continue

        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────"""

    if old_1 not in code:
        print("ERROR: no se encontró Patch 1 (bloque pre-detectar_fin_real).")
        sys.exit(1)
    code = code.replace(old_1, new_1)

    # ── Patch 2: eliminar el refinar_inicio duplicado post-detectar_fin_real ─
    old_2 = """        # ── v18 Fase F: refinar linea_inicio por título ──────────────────────
        # Recorta residuo del fallo anterior incluido por el localizador
        # (arranca desde header de página compartida). Señal primaria: token
        # del título en nombres_indice. Secundaria: "Vistos los autos".
        # Fallback: linea_inicio del catálogo sin cambios.
        # ancla_inicio se propaga a status_localizacion para auditoría.
        offset_titulo, ancla_inicio = refinar_inicio_por_titulo(
            bloque, nombres_indice
        )
        if offset_titulo > 0:
            linea_inicio = int(linea_inicio) + offset_titulo
            bloque = bloque[offset_titulo:]
            if not bloque:
                continue"""

    new_2 = """        # ── v18 Fase F: refinar linea_inicio por título ──────────────────────
        # B074: ya ejecutado antes de detectar_fin_real (ver arriba).
        # offset_titulo y ancla_inicio ya están seteados."""

    if old_2 not in code:
        print("ERROR: no se encontró Patch 2 (refinar_inicio post-detectar_fin_real).")
        sys.exit(1)
    code = code.replace(old_2, new_2)

    parser_dst.write_text(code, encoding='utf-8')
    print(f"Parser parcheado: {parser_dst}")


def run_parser(parser_path, localizados, mapa, corpus, output):
    """Corre el parser y devuelve el CSV como dict."""
    cmd = [
        sys.executable, str(parser_path),
        '--localizados', str(localizados),
        '--mapa', str(mapa),
        '--corpus', str(corpus),
        '--output', str(output),
    ]
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print("ERROR corriendo parser:")
        print(result.stderr[-2000:])
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
                if campo == 'voting_pattern':
                    if bv == 'sin_firma' and nv != 'sin_firma':
                        tipo = 'MEJORA'
                    elif bv != 'sin_firma' and nv == 'sin_firma':
                        tipo = 'REGRESION'
                    else:
                        tipo = 'CAMBIO'
                elif campo == 'n_jueces':
                    bi, ni = int(bv or 0), int(nv or 0)
                    if bi == 0 and ni > 0:
                        tipo = 'MEJORA'
                    elif ni > bi and bi > 0:
                        tipo = 'MEJORA_JUECES'
                    elif ni < bi:
                        tipo = 'REGRESION'
                    else:
                        tipo = 'CAMBIO'
                elif campo == 'linea_fin_real':
                    tipo = 'LFR_CAMBIO'
                elif campo == 'pista_fin':
                    tipo = 'PISTA_CAMBIO'
                else:
                    tipo = 'CAMBIO'
                diffs.append({
                    'caso_id': cid, 'tipo': tipo,
                    'campo': campo, 'base': bv, 'nuevo': nv,
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
                if d['tipo'] in ('LFR_CAMBIO', 'PISTA_CAMBIO', 'CAMBIO')
                } - mejoras - regresiones - mejora_j

    # Sin firma
    sf_base = sum(1 for r in baseline_rows.values()
                  if r.get('voting_pattern') == 'sin_firma'
                  and r.get('tipo_entrada', 'fallo') == 'fallo')
    sf_new = sum(1 for r in new_rows.values()
                 if r.get('voting_pattern') == 'sin_firma'
                 and r.get('tipo_entrada', 'fallo') == 'fallo')

    print(f"\n=== RESUMEN B074v4 ===")
    print(f"sin_firma: {sf_base} -> {sf_new} (delta {sf_new - sf_base:+d})")
    print(f"Total casos con cambios: {len(set(d['caso_id'] for d in diffs))}")
    print(f"\n  MEJORA (sf->firma): {len(mejoras)}")
    for c in sorted(mejoras):
        n = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'n_jueces'), None)
        print(f"    {c}: n_jueces {n['base']}->{n['nuevo']}" if n else f"    {c}")
    print(f"\n  REGRESION: {len(regresiones)}")
    for c in sorted(regresiones):
        n = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'n_jueces'), None)
        f = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'firma_raw'), None)
        print(f"    {c}: n_jueces {n['base']}->{n['nuevo']}" if n else f"    {c}")
        if f:
            print(f"      firma_base: {f['base'][:70]}")
            print(f"      firma_new:  {f['nuevo'][:70]}")
    print(f"\n  MEJORA_JUECES: {len(mejora_j)}")
    for c in sorted(mejora_j):
        n = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'n_jueces'), None)
        f = next((d for d in diffs if d['caso_id'] == c and d['campo'] == 'firma_raw'), None)
        print(f"    {c}: n_jueces {n['base']}->{n['nuevo']}" if n else f"    {c}")
        if f:
            print(f"      firma_base: {f['base'][:70]}")
            print(f"      firma_new:  {f['nuevo'][:70]}")
    print(f"\n  Solo LFR/pista/cambio: {len(lfr_only)}")
    print(f"\nDiff escrito en: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parser', required=True)
    parser.add_argument('--localizados', required=True)
    parser.add_argument('--mapa', required=True)
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    print("Leyendo baseline...")
    baseline_rows = {}
    with open(args.baseline, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            baseline_rows[row['caso_id_canonico']] = row
    print(f"  {len(baseline_rows)} casos en baseline.")

    parser_src = Path(args.parser)
    parser_patched = parser_src.parent / 'parser_b074v4.py'
    patch_parser(parser_src, parser_patched)

    output_new = Path(args.output).parent / 'csjn_casos_b074v4.csv'
    print(f"\nCorriendo parser parcheado...")
    new_rows = run_parser(
        parser_patched, args.localizados, args.mapa, args.corpus, output_new,
    )
    print(f"  {len(new_rows)} casos en output parcheado.")

    print("\nGenerando diff...")
    diff_results(baseline_rows, new_rows, args.output)


if __name__ == '__main__':
    main()
