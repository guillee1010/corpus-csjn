#!/usr/bin/env python3
# scripts/diagnostico/H120/extraer_lote_M20.py   (DIAGNOSTICO, solo lee)
# -----------------------------------------------------------------------------
# Corre extraer_caso.py --blind sobre los 300 caso_id del frame M19 (embebidos
# abajo) y los concatena en UN solo .md, para codificar cod_parte_ganadora
# leyendo el FALLO COMPLETO desde el .md (el por_ello no nombra al recurrente;
# el bloque/considerandos si). REE: reusa extraer_caso.py tal cual (subproceso).
#
# Uso (desde cualquier subdir del repo; los 300 ids ya estan adentro):
#   python scripts/diagnostico/H120/extraer_lote_M20.py
#   python ... extraer_lote_M20.py --out output/diagnostico/extraidos_M20.md
#   python ... extraer_lote_M20.py OTRO_FRAME.csv|.xlsx   # opcional: otra lista de ids
#   python ... extraer_lote_M20.py --no-blind             # incluye respuestas del parser (NO para ciego)
# -----------------------------------------------------------------------------
import argparse, csv, subprocess, sys, time
from pathlib import Path
csv.field_size_limit(10 ** 7)

IDS_M20 = [
    '329_p53', '329_p167', '329_p171', '329_p239', '329_p381', '329_p472', '329_p473', '329_p1336',
    '329_p1447', '329_p1473', '329_p1487', '329_p1541', '329_p1626', '329_p1693', '329_p1862',
    '329_p1908', '329_p1917', '329_p1936', '329_p1963', '329_p2111', '329_p2265', '329_p2569',
    '329_p2588', '329_p2645', '329_p2856', '329_p2911', '329_p3129', '329_p3203', '329_p3213',
    '329_p3388', '329_p3757', '329_p3834', '329_p3846', '329_p3931', '329_p3956', '329_p4007',
    '329_p4094', '329_p4161', '329_p4178', '329_p4337', '329_p4342', '329_p4352', '329_p4355',
    '329_p4447', '329_p4481', '329_p4524', '329_p4535', '329_p4717', '329_p4741', '329_p4762',
    '329_p4822', '329_p4845', '329_p4902', '329_p4990', '329_p5007', '329_p5064', '329_p5115',
    '329_p5198', '329_p5227', '329_p5234', '329_p5310', '329_p5336', '329_p5368', '329_p5670',
    '329_p5728', '329_p5789', '329_p5848', '329_p5871', '329_p5994', '329_p6050', '329_p6068',
    '330_p24', '330_p50', '330_p182', '330_p238', '330_p246', '330_p304', '330_p610', '330_p619',
    '330_p1043', '330_p1179', '330_p1303', '330_p1465', '330_p1907', '330_p2014', '330_p2081',
    '330_p2345', '330_p2445', '330_p2470', '330_p2520', '330_p2900', '330_p2915', '330_p3519',
    '330_p3565', '330_p3609', '330_p3764', '330_p3777', '330_p4211', '330_p4252', '330_p4592',
    '330_p4632', '330_p4690', '330_p4797', '330_p5010', '330_p5064', '330_p5131', '330_p5197',
    '330_p5435', '331_p68', '331_p116', '331_p123', '331_p194', '331_p355', '331_p499', '331_p536',
    '331_p846', '331_p989', '331_p1651', '331_p2166', '331_p2257', '331_p2266', '331_p2283',
    '331_p2608', '331_p2621', '331_p2839', '331_p2910', '331_p2913', '332_p105', '332_p324',
    '332_p548', '332_p582', '332_p595', '332_p810', '332_p850', '332_p962', '332_p979', '332_p1029',
    '332_p1035', '332_p1280', '332_p1338', '332_p1382', '332_p1629', '332_p1704', '332_p1741',
    '332_p2043', '332_p2502', '332_p2604', '332_p2625', '332_p2797', '333_p9', '333_p60',
    '333_p215', '333_p241', '333_p290', '333_p300', '333_p447', '333_p508', '333_p1235',
    '333_p1639', '333_p2010', '334_p44', '334_p376', '334_p490', '334_p941', '334_p1070',
    '334_p1074', '334_p1081', '334_p1204', '334_p1276', '337_p329', '337_p373', '337_p481',
    '337_p505', '337_p735', '337_p771', '337_p1095', '337_p1142', '337_p1234', '337_p1581',
    '338_p40', '338_p102', '338_p148', '338_p155', '338_p249', '338_p280', '338_p419', '338_p1252',
    '339_p155', '339_p183', '339_p274', '339_p434', '339_p490', '339_p506', '339_p597', '339_p824',
    '339_p1048', '339_p1171', '339_p1530', '339_p1567', '339_p1621', '339_p1834', '340_p95',
    '340_p397', '340_p431', '340_p708', '340_p732', '340_p786', '340_p822', '340_p900', '340_p1395',
    '340_p1398', '340_p1441', '340_p1450', '340_p1551', '340_p1554', '341_p127', '341_p324',
    '341_p335', '341_p500', '341_p566', '341_p600', '341_p1338', '341_p1649', '342_p507',
    '342_p824', '342_p969', '342_p1358', '342_p1393', '342_p1456', '342_p1483', '342_p2083',
    '342_p2399', '343_p412', '343_p580', '343_p646', '343_p1233', '343_p1319', '343_p1620',
    '343_p1688', '343_p1944', '344_p344', '344_p701', '344_p1283', '344_p1438', '344_p1835',
    '344_p2172', '344_p2393', '344_p2669', '344_p2868', '344_p2955', '344_p3394', '344_p3469',
    '345_p12', '345_p154', '345_p241', '345_p523', '345_p583', '345_p670', '345_p1238', '345_p1421',
    '346_p44', '346_p439', '346_p646', '346_p675', '346_p1241', '346_p1339', '347_p360', '347_p412',
    '347_p606', '347_p833', '347_p1031', '347_p1046', '347_p1137', '347_p1191', '347_p1215',
    '347_p2001', '347_p2025', '348_p61', '348_p92', '348_p113', '348_p169', '348_p296', '348_p405',
    '348_p708', '348_p1347', '348_p1378', '348_p1499', '348_p1576', '348_p1717', '349_p95',
    '349_p148', '349_p280', '329_p4150', '329_p4356', '329_p4503', '331_p978', '332_p2208',
    '341_p560', '343_p595', '346_p658'
]

import re as _re
_ORD = _re.compile(r"\s+(\d{1,2}\s*[º°]\s*\))")
_SEC = _re.compile(r"\s+(Considerando:|Autos\s+y\s+Vistos|Y\s+Vistos|Por\s+ello|Buenos\s+Aires,|"
                   r"FALLO\s+DE\s+LA\s+CORTE|DICTAMEN|—?Del\s+dictamen)")
def reflow(t: str) -> str:
    """Re-inserta puntos y aparte en el bloque aplanado por extraer_caso (norm).
    Quiebra antes de cada considerando numerado y de las secciones tipicas del fallo."""
    t = _ORD.sub(r"\n\n\1", t)
    t = _SEC.sub(r"\n\n\1", t)
    return _re.sub(r"\n{3,}", "\n\n", t)

def find_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start

ROOT = find_root(Path(__file__).resolve().parent)
EXTRAER = ROOT / "scripts" / "diagnostico" / "extraer_caso.py"

def leer_ids(path: Path, col: str):
    """Lee la columna de caso_id desde .xlsx/.xlsm o .csv (csv tolera BOM de Excel)."""
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import pandas as pd
        except ImportError:
            sys.exit("Falta pandas para leer .xlsx. Pasa un .csv, o: pip install pandas openpyxl")
        df = pd.read_excel(path, dtype=str)
        if col not in df.columns:
            sys.exit(f"[FATAL] no hay columna '{col}' en {path.name}. Columnas: {list(df.columns)}")
        return [str(x).strip() for x in df[col].tolist() if str(x).strip() and str(x).strip().lower() != "nan"]
    with open(path, encoding="utf-8-sig") as f:
        return [r[col].strip() for r in csv.DictReader(f) if r.get(col, "").strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frame", nargs="?", default="",
                    help="opcional: .xlsx/.csv con otra lista de caso_id. Sin esto usa los 300 embebidos.")
    ap.add_argument("--col", default="caso_id_canonico")
    ap.add_argument("--out", default=str(ROOT / "output" / "diagnostico" / "extraidos_M20_n300.md"))
    ap.add_argument("--carpeta", default=str(ROOT / "output" / "diagnostico" / "extraidos_M20"))
    ap.add_argument("--no-blind", action="store_true",
                    help="incluye outcome/causa/dictamen del parser (NO recomendado para ciego)")
    ap.add_argument("--no-reflow", action="store_true",
                    help="no re-insertar puntos y aparte (deja el bloque tal cual lo aplana extraer_caso)")
    args = ap.parse_args()

    if not EXTRAER.exists():
        sys.exit(f"[FATAL] no encuentro {EXTRAER}\n  (ROOT detectada: {ROOT})")

    if args.frame:
        fp = Path(args.frame)
        if not fp.exists():
            sys.exit(f"[FATAL] no encuentro el frame {fp}")
        ids = leer_ids(fp, args.col)
        fuente = fp.name
    else:
        ids = list(IDS_M20)
        fuente = "lista embebida (300)"
    if not ids:
        sys.exit("[FATAL] sin ids para procesar")

    blind = not args.no_blind
    carpeta = Path(args.carpeta); carpeta.mkdir(parents=True, exist_ok=True)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    print(f"{len(ids)} casos · {'BLIND' if blind else 'CON respuestas del parser'} · fuente ids: {fuente}")
    print(f"ROOT={ROOT}")

    partes = [f"# Extraccion lote M20 — {len(ids)} casos (bloque completo desde .md)",
              "_Para codificar `cod_parte_ganadora`. El recurrente suele nombrarse en el considerando 1._",
              f"_Modo: {'ciego (sin respuestas del parser)' if blind else 'CON respuestas'}._\n", "---\n"]
    fallos = []; t0 = time.time()
    for k, cid in enumerate(ids, 1):
        f_ind = carpeta / f"{cid}.md"
        cmd = [sys.executable, str(EXTRAER), cid, "--out", str(f_ind)] + (["--blind"] if blind else [])
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not f_ind.exists():
            msg = (r.stderr or r.stdout or "sin salida").strip().replace("\n", " ")[:180]
            fallos.append((cid, msg))
            partes.append(f"## {cid}\n\n> [FALLO EXTRACCION] {msg}\n\n---\n")
        else:
            txt = f_ind.read_text(encoding="utf-8").rstrip()
            partes.append((txt if args.no_reflow else reflow(txt)) + "\n\n---\n")
        if k % 25 == 0 or k == len(ids):
            print(f"  {k}/{len(ids)}  ({time.time()-t0:.0f}s)")

    out.write_text("\n".join(partes), encoding="utf-8", newline="\n")
    print(f"\n[escrito consolidado] {out}  ({out.stat().st_size//1024} KB)")
    print(f"[escritos por caso  ] {carpeta}/  ({len(ids)-len(fallos)} archivos)")
    if fallos:
        print(f"\n[AVISO] {len(fallos)} extracciones fallaron (revisar a mano):")
        for cid, msg in fallos[:25]:
            print(f"   {cid}: {msg}")
    else:
        print("todas las extracciones OK")

if __name__ == "__main__":
    main()
