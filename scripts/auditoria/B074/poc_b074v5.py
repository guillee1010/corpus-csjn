"""
PoC B074 v5 — Pre-computar posición del título como lower-bound para buscar_atras.

NO mueve refinar_inicio de lugar. Solo pre-computa la posición del título
del caso actual en las primeras 15 líneas del bloque [li, lf], y pasa ese
valor como li ajustado SOLO para detectar_fin_real. Todo el resto del
pipeline usa el li original.

15 líneas es el máximo razonable para residuo: ~3 page headers + ~5 líneas
de dispositivo/firma del caso anterior + ~5 de metadata + carátula.
Si el título no se encuentra en 15 líneas, no hay residuo detectable →
baseline preservado.
"""
import sys, os, csv, subprocess, re
from pathlib import Path
import argparse


def patch_parser(parser_src: Path, parser_dst: Path):
    code = parser_src.read_text(encoding='utf-8')

    # Patch: insertar pre-cómputo de título antes de detectar_fin_real,
    # y usar _li_for_dfr como linea_inicio en la llamada.

    old = """        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────
        # Buscar la frontera con el fallo siguiente (carátula/sumario/marcador)
        # para detectar dónde termina realmente el contenido decisorio.
        siguiente = siguiente_caso.get(caso_id_canonico)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""
        prox_header = proximo_header_despues_de(headers_archivo, int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1)
        linea_fin_real, status_fin, pista_fin = detectar_fin_real(
            lines,
            int(linea_inicio),
            int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1,
            prox_header,
            primer_token_siguiente
        )"""

    new = """        # ── B074v5: pre-computar posición del título como lower-bound ─────
        # Si el título del caso actual aparece en las primeras 15 líneas del
        # bloque, usarlo como li para detectar_fin_real. Así buscar_atras no
        # pesca firma del caso anterior (que está antes del título).
        # Si no se encuentra, usar el li original (= baseline idéntico).
        _li_for_dfr = int(linea_inicio)
        _token_titulo = primer_token_de_caratula(nombres_indice)
        if _token_titulo and len(_token_titulo) >= 4:
            _pat_titulo = re.compile(r'\\b' + re.escape(_token_titulo) + r'\\b', re.I)
            for _k, _ln in enumerate(bloque[:15]):
                if _pat_titulo.search(_ln):
                    _li_for_dfr = int(linea_inicio) + _k
                    break

        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────
        # Buscar la frontera con el fallo siguiente (carátula/sumario/marcador)
        # para detectar dónde termina realmente el contenido decisorio.
        siguiente = siguiente_caso.get(caso_id_canonico)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""
        prox_header = proximo_header_despues_de(headers_archivo, int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1)
        linea_fin_real, status_fin, pista_fin = detectar_fin_real(
            lines,
            _li_for_dfr,
            int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1,
            prox_header,
            primer_token_siguiente
        )"""

    if old not in code:
        print("ERROR: no se encontró el bloque a parchear.")
        sys.exit(1)
    code = code.replace(old, new)
    parser_dst.write_text(code, encoding='utf-8')
    print(f"Parser parcheado: {parser_dst}")


def run_parser(parser_path, localizados, mapa, corpus, output):
    cmd = [sys.executable, str(parser_path),
           '--localizados', str(localizados), '--mapa', str(mapa),
           '--corpus', str(corpus), '--output', str(output)]
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
    diffs = []
    for cid, base in baseline_rows.items():
        nuevo = new_rows.get(cid)
        if not nuevo: continue
        for campo in ['voting_pattern','n_jueces','jueces','jueces_conocidos',
                      'linea_fin_real','pista_fin','firma_raw']:
            bv, nv = base.get(campo,''), nuevo.get(campo,'')
            if bv != nv:
                if campo == 'voting_pattern':
                    tipo = 'MEJORA' if (bv=='sin_firma' and nv!='sin_firma') else \
                           'REGRESION' if (bv!='sin_firma' and nv=='sin_firma') else 'CAMBIO'
                elif campo == 'n_jueces':
                    bi,ni = int(bv or 0), int(nv or 0)
                    tipo = 'MEJORA' if (bi==0 and ni>0) else \
                           'MEJORA_JUECES' if (ni>bi and bi>0) else \
                           'REGRESION' if ni<bi else 'CAMBIO'
                elif campo == 'linea_fin_real': tipo = 'LFR_CAMBIO'
                elif campo == 'pista_fin': tipo = 'PISTA_CAMBIO'
                else: tipo = 'CAMBIO'
                diffs.append({'caso_id':cid,'tipo':tipo,'campo':campo,'base':bv,'nuevo':nv})

    with open(output_path,'w',encoding='utf-8',newline='') as f:
        w = csv.DictWriter(f, fieldnames=['caso_id','tipo','campo','base','nuevo'])
        w.writeheader(); w.writerows(sorted(diffs, key=lambda d:(d['caso_id'],d['campo'])))

    mejoras = {d['caso_id'] for d in diffs if d['tipo']=='MEJORA'}
    regresiones = {d['caso_id'] for d in diffs if d['tipo']=='REGRESION'}
    mejora_j = {d['caso_id'] for d in diffs if d['tipo']=='MEJORA_JUECES'} - mejoras - regresiones
    lfr_only = {d['caso_id'] for d in diffs if d['tipo'] in ('LFR_CAMBIO','PISTA_CAMBIO','CAMBIO')} - mejoras - regresiones - mejora_j

    sf_b = sum(1 for r in baseline_rows.values() if r.get('voting_pattern')=='sin_firma' and r.get('tipo_entrada','fallo')=='fallo')
    sf_n = sum(1 for r in new_rows.values() if r.get('voting_pattern')=='sin_firma' and r.get('tipo_entrada','fallo')=='fallo')

    print(f"\n=== RESUMEN B074v5 ===")
    print(f"sin_firma: {sf_b} -> {sf_n} (delta {sf_n-sf_b:+d})")
    print(f"Total casos con cambios: {len(set(d['caso_id'] for d in diffs))}")
    for cat, label, s in [(mejoras,'MEJORA (sf->firma)',True),(regresiones,'REGRESION',True),
                           (mejora_j,'MEJORA_JUECES',True),(lfr_only,'Solo LFR/pista',False)]:
        print(f"\n  {label}: {len(cat)}")
        if s:
            for c in sorted(cat):
                n = next((d for d in diffs if d['caso_id']==c and d['campo']=='n_jueces'),None)
                f = next((d for d in diffs if d['caso_id']==c and d['campo']=='firma_raw'),None)
                print(f"    {c}: n_jueces {n['base']}->{n['nuevo']}" if n else f"    {c}")
                if f and cat in (regresiones,mejora_j):
                    print(f"      base: {f['base'][:70]}")
                    print(f"      new:  {f['nuevo'][:70]}")
    print(f"\nDiff: {output_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parser',required=True); p.add_argument('--localizados',required=True)
    p.add_argument('--mapa',required=True); p.add_argument('--corpus',required=True)
    p.add_argument('--baseline',required=True); p.add_argument('--output',required=True)
    a = p.parse_args()

    print("Leyendo baseline...")
    bl = {}
    with open(a.baseline,encoding='utf-8') as f:
        for r in csv.DictReader(f): bl[r['caso_id_canonico']]=r
    print(f"  {len(bl)} casos.")

    ps = Path(a.parser); pd = ps.parent/'parser_b074v5.py'
    patch_parser(ps, pd)

    out_csv = Path(a.output).parent/'csjn_casos_b074v5.csv'
    print(f"\nCorriendo parser parcheado...")
    nr = run_parser(pd, a.localizados, a.mapa, a.corpus, out_csv)
    print(f"  {len(nr)} casos.")

    print("\nGenerando diff...")
    diff_results(bl, nr, a.output)

if __name__=='__main__': main()
