# PoC M09 - Deteccion con constraint de zona
# Correr desde la raiz del repo: python poc_m09.py

import sys
import csv
from pathlib import Path

sys.path.insert(0, str(Path("scripts/pipeline")))
from parser import (
    zonificar_bloque,
    construir_bloque_desde_localizacion,
    detectar_apertura_en_bloque,
    refinar_inicio_por_titulo,
    RE_VOTO_HDR,
    RE_DISID_HDR,
    RE_CONSIDERANDO,
    detectar_juez_en_voto_header,
)

CASOS_CSV = Path("output/parser/csjn_casos.csv")
CORPUS_DIR = Path("corpus")

_ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}


def replay_loop(bloque, skip_set):
    n_votos = 0
    n_disid = 0
    inicio_vi = None
    marcadores = []

    for k, bl in enumerate(bloque):
        stripped = bl.strip()
        if not stripped:
            continue
        if k in skip_set:
            continue

        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            tipo = "voto" if RE_VOTO_HDR.match(stripped) else "disidencia"
            if tipo == "voto":
                n_votos += 1
            else:
                n_disid += 1
            if inicio_vi is None:
                inicio_vi = k
            header_completo = stripped
            for offset in range(1, 4):
                juez = detectar_juez_en_voto_header(header_completo)
                if juez:
                    marcadores.append((k, juez, tipo))
                    break
                if k + offset < len(bloque):
                    sig = bloque[k + offset].strip()
                    if not sig:
                        continue
                    if RE_CONSIDERANDO.match(sig):
                        break
                    header_completo += " " + sig

    return n_votos, n_disid, inicio_vi, marcadores


def main():
    with open(CASOS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        casos = [r for r in reader if r["tipo_entrada"] == "fallo"]

    print(f"Casos fallo: {len(casos)}")
    print()

    cache_lines = {}
    diffs = []
    errores = []
    stats_zonas_excluidas = {}

    for i, caso in enumerate(casos):
        caso_id = caso["caso_id_canonico"]
        source = caso["source_file"]
        li = caso["linea_inicio"]
        lfr = caso["linea_fin_real"]

        if not li or not lfr:
            continue

        filepath = CORPUS_DIR / source
        if source not in cache_lines:
            try:
                cache_lines[source] = filepath.read_text(encoding="utf-8").splitlines()
            except FileNotFoundError:
                errores.append((caso_id, f"archivo no encontrado: {source}"))
                continue
        lines = cache_lines[source]

        bloque = construir_bloque_desde_localizacion(lines, li, lfr)
        if not bloque:
            continue

        zonas_linea, _anclas = zonificar_bloque(bloque)

        lineas_dictamen = {k for k, z in enumerate(zonas_linea) if z == "dictamen"}
        lineas_excluir = {k for k, z in enumerate(zonas_linea) if z not in _ZONAS_FALLO}

        old = replay_loop(bloque, lineas_dictamen)
        new = replay_loop(bloque, lineas_excluir)

        nuevas_excluidas = lineas_excluir - lineas_dictamen
        for k in nuevas_excluidas:
            z = zonas_linea[k]
            stats_zonas_excluidas[z] = stats_zonas_excluidas.get(z, 0) + 1

        if old != new:
            old_nv, old_nd, old_iv, old_m = old
            new_nv, new_nd, new_iv, new_m = new

            zonas_afectadas = set()
            lineas_perdidas = []
            for k, bl in enumerate(bloque):
                stripped = bl.strip()
                if not stripped:
                    continue
                if k in lineas_dictamen:
                    continue
                if k not in lineas_excluir:
                    continue
                if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
                    zonas_afectadas.add(zonas_linea[k])
                    lineas_perdidas.append({
                        "linea_rel": k,
                        "linea_abs": int(li) + k,
                        "zona": zonas_linea[k],
                        "texto": stripped[:120],
                    })

            diffs.append({
                "caso_id": caso_id,
                "source": source,
                "old_nv": old_nv,
                "old_nd": old_nd,
                "new_nv": new_nv,
                "new_nd": new_nd,
                "old_marcadores": len(old_m),
                "new_marcadores": len(new_m),
                "zonas_afectadas": zonas_afectadas,
                "lineas_perdidas": lineas_perdidas,
            })

        if (i + 1) % 500 == 0:
            print(f"  procesados {i+1}/{len(casos)}...")

    print(f"\n{'='*70}")
    print(f"RESULTADOS PoC M09 -- constraint de zona")
    print(f"{'='*70}")
    print(f"Casos procesados: {len(casos)}")
    print(f"Casos con diff:   {len(diffs)}")
    print(f"Errores:          {len(errores)}")
    print()

    if diffs:
        solo_menos_votos = [d for d in diffs if d["new_nv"] < d["old_nv"]]
        solo_menos_disid = [d for d in diffs if d["new_nd"] < d["old_nd"]]
        mas_votos = [d for d in diffs if d["new_nv"] > d["old_nv"]]
        mas_disid = [d for d in diffs if d["new_nd"] > d["old_nd"]]

        print(f"  Menos votos:       {len(solo_menos_votos)}")
        print(f"  Menos disidencias: {len(solo_menos_disid)}")
        print(f"  Mas votos:         {len(mas_votos)}  (inesperado)")
        print(f"  Mas disidencias:   {len(mas_disid)}  (inesperado)")
        print()

        all_zonas = {}
        for d in diffs:
            for z in d["zonas_afectadas"]:
                all_zonas[z] = all_zonas.get(z, 0) + 1
        print("Zonas que causaron cambios:")
        for z, c in sorted(all_zonas.items(), key=lambda x: -x[1]):
            print(f"  {z:30s} {c} casos")
        print()

        print(f"\n{'~'*70}")
        print("DETALLE POR CASO")
        print(f"{'~'*70}")
        for d in diffs:
            print(f"\n  {d['caso_id']}  ({d['source']})")
            print(f"    votos:       {d['old_nv']} -> {d['new_nv']}")
            print(f"    disidencias: {d['old_nd']} -> {d['new_nd']}")
            print(f"    marcadores:  {d['old_marcadores']} -> {d['new_marcadores']}")
            print(f"    zonas:       {d['zonas_afectadas']}")
            for lp in d["lineas_perdidas"]:
                print(f"    x L{lp['linea_abs']} [{lp['zona']}]: {lp['texto']}")
    else:
        print("  Sin diferencias -- el constraint de zona no cambia ningun resultado.")
        print("  (Las zonas excluidas no contenian matches de RE_VOTO_HDR/RE_DISID_HDR)")

    print(f"\n{'~'*70}")
    print("VOLUMEN DE LINEAS EXCLUIDAS POR ZONA (nuevas, no dictamen)")
    print(f"{'~'*70}")
    for z, c in sorted(stats_zonas_excluidas.items(), key=lambda x: -x[1]):
        print(f"  {z:30s} {c:>8,} lineas")

    if errores:
        print(f"\n{'~'*70}")
        print(f"ERRORES ({len(errores)})")
        for cid, msg in errores[:10]:
            print(f"  {cid}: {msg}")


if __name__ == "__main__":
    main()
