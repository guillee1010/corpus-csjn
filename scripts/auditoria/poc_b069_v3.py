# PoC B069 v3 - pasada completa del parser sin Pista 1 atras
#
# 1. Copia parser.py -> parser_poc_b069.py (con patch)
# 2. Corre el parser modificado
# 3. Diffea csjn_casos.csv viejo vs nuevo
#
# Uso: python scripts/auditoria/poc_b069_v3.py
# Desde: raiz del proyecto

import csv
import shutil
import subprocess
import sys
from pathlib import Path
from collections import Counter


def aplicar_patch():
    """Copia parser.py y comenta la busqueda atras de Pista 1."""
    src = Path("scripts/pipeline/parser.py")
    dst = Path("scripts/pipeline/parser_poc_b069.py")
    shutil.copy2(src, dst)

    with open(dst, encoding="utf-8") as f:
        contenido = f.read()

    # Reemplazar las 3 lineas de buscar_atras en Pista 1
    viejo = (
        '        # Atrás dentro del bloque (excluir las primeras 5 líneas para no\n'
        '        # matchear la propia carátula del fallo X)\n'
        '        k = buscar_atras(es_caratula, lfc, li + 5)\n'
        '        if k is not None:\n'
        '            return (k - 1, "fin_dentro_bloque", "caratula_siguiente")\n'
    )
    nuevo = (
        '        # [PoC B069] buscar_atras acotada a 20 lineas\n'
        '        k = buscar_atras(es_caratula, lfc, max(lfc - 20, li + 5))\n'
        '        if k is not None:\n'
        '            return (k - 1, "fin_dentro_bloque", "caratula_siguiente")\n'
    )

    if viejo not in contenido:
        print("ERROR: no encontre el bloque a patchear en parser.py")
        print("Verificar que las lineas 1326-1330 no cambiaron.")
        sys.exit(1)

    contenido = contenido.replace(viejo, nuevo)

    with open(dst, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"Patch aplicado: {dst}")
    return dst


def correr_parser(parser_script):
    """Corre el parser y guarda salida en output/auditoria/."""
    out_casos = "output/auditoria/poc_b069_casos.csv"
    out_votos = "output/auditoria/poc_b069_votos.csv"
    cmd = [
        sys.executable, str(parser_script),
        "--localizados", "output/localizacion/fallos_localizados.csv",
        "--mapa", "output/mapa/mapa_paginas.csv",
        "--corpus", "corpus",
        "--output", out_casos,
        "--output-votos", out_votos,
    ]
    print(f"\nCorriendo parser modificado...")
    print(f"  {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"ERROR: parser termino con codigo {result.returncode}")
        sys.exit(1)
    return out_casos


def diffear(csv_viejo, csv_nuevo):
    """Compara firma_raw y linea_fin_real entre ambos CSVs."""
    with open(csv_viejo, encoding="utf-8") as f:
        viejos = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}
    with open(csv_nuevo, encoding="utf-8") as f:
        nuevos = {r["caso_id_canonico"]: r for r in csv.DictReader(f)}

    mejoras = []
    regresiones = []
    sin_cambio = 0
    solo_lfr = 0

    for caso_id, v in viejos.items():
        if caso_id not in nuevos:
            continue
        n = nuevos[caso_id]

        firma_v = bool(v["firma_raw"].strip())
        firma_n = bool(n["firma_raw"].strip())
        lfr_v = int(v["linea_fin_real"])
        lfr_n = int(n["linea_fin_real"])

        if not firma_v and firma_n:
            mejoras.append({
                "caso": caso_id,
                "tomo": v["tomo"],
                "firma_nueva": n["firma_raw"][:80],
                "lfr_viejo": lfr_v,
                "lfr_nuevo": lfr_n,
                "pista_nueva": n["pista_fin"],
            })
        elif firma_v and not firma_n:
            regresiones.append({
                "caso": caso_id,
                "tomo": v["tomo"],
                "firma_vieja": v["firma_raw"][:80],
                "lfr_viejo": lfr_v,
                "lfr_nuevo": lfr_n,
                "pista_nueva": n["pista_fin"],
            })
        elif lfr_v != lfr_n:
            solo_lfr += 1
        else:
            sin_cambio += 1

    print(f"\n{'='*60}")
    print(f"=== DIFF: {csv_viejo} vs {csv_nuevo} ===")
    print(f"{'='*60}")
    print(f"  Casos comparados: {len(viejos)}")
    print(f"  Sin cambio:       {sin_cambio}")
    print(f"  Solo cambio lfr:  {solo_lfr}")
    print(f"  MEJORAS (gano firma):    {len(mejoras)}")
    print(f"  REGRESIONES (perdio firma): {len(regresiones)}")

    if mejoras:
        print(f"\n=== MEJORAS (primeras 20) ===")
        pistas_mejora = Counter(m["pista_nueva"] for m in mejoras)
        for m in mejoras[:20]:
            print(f"  {m['caso']:<15} firma={m['firma_nueva'][:60]}")
        print(f"\n  Pista que tomo el control:")
        for k, v in pistas_mejora.most_common():
            print(f"    {k:<35} {v:>4}")

    if regresiones:
        print(f"\n=== REGRESIONES ===")
        for r in regresiones[:20]:
            print(f"  {r['caso']:<15} firma_perdida={r['firma_vieja'][:60]}")
        if len(regresiones) > 20:
            print(f"  ... y {len(regresiones) - 20} mas")

    print(f"\n=== VEREDICTO ===")
    if len(regresiones) == 0:
        print(f"  SAFE: {len(mejoras)} mejoras, 0 regresiones")
        print(f"  -> Patchear parser.py")
    else:
        print(f"  {len(regresiones)} REGRESIONES - investigar antes de patchear")

    # Guardar diff detallado
    diff_path = Path("output/auditoria/poc_b069_v3_diff.csv")
    all_changes = [dict(m, tipo="MEJORA") for m in mejoras] + \
                  [dict(r, tipo="REGRESION") for r in regresiones]
    if all_changes:
        with open(diff_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=all_changes[0].keys())
            w.writeheader()
            for row in all_changes:
                w.writerow(row)
        print(f"\n  Diff detallado: {diff_path}")


def main():
    # 1. Patch
    parser_mod = aplicar_patch()

    # 2. Correr
    csv_nuevo = correr_parser(parser_mod)

    # 3. Diff
    csv_viejo = "output/parser/csjn_casos.csv"
    diffear(csv_viejo, csv_nuevo)

    # Cleanup
    parser_mod.unlink()
    print(f"\nLimpieza: {parser_mod} eliminado")


if __name__ == "__main__":
    main()
