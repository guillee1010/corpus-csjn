import sys, csv
from pathlib import Path
sys.path.insert(0, 'scripts/pipeline')
import parser as P

loc = {}
with open('output/localizacion/fallos_localizados.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        loc[row['caso_id_canonico']] = row

cid = '329_p94'
row = loc.get(cid)
print(f'Caso en localizados: {row is not None}')
if row:
    archivo = row.get("archivo", "")
    print(f'  li={row.get("linea_inicio")}, lf={row.get("linea_fin")}')
    print(f'  archivo={archivo}')
    ruta = Path('corpus') / archivo
    print(f'  existe: {ruta.exists()}')
    if ruta.exists():
        lines = ruta.read_text(encoding='utf-8').split('\n')
        print(f'  Total lines: {len(lines)}')
        bloque = P.construir_bloque_desde_localizacion(lines, row['linea_inicio'], row['linea_fin'])
        print(f'  Bloque len: {len(bloque) if bloque else 0}')
        if bloque:
            zonas, anclas = P.zonificar_bloque(bloque)
            segs = P.extraer_segmentos(zonas, bloque)
            print(f'  Segmentos: {len(segs)}')
            firmas = [s for s in segs if s["zona"] == "firma"]
            sumarios = [s for s in segs if s["zona"] == "sumario"]
            print(f'  Firma segs: {len(firmas)}, Sumario segs: {len(sumarios)}')
            for s in segs[:40]:
                print(f'    seg {s["segmento"]:>2} | {s["zona"]:<25} | L{s["linea_ini"]:>4}-L{s["linea_fin"]:>4} | {s["wc"]:>4} wc')
