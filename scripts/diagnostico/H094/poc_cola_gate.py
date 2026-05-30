#!/usr/bin/env python3
# scripts/auditoria/H094/poc_cola_gate.py
# -----------------------------------------------------------------------------
# PoC H094 — mide la DIRECCION del fix antes de tocar produccion.
#
# Fix propuesto: las 3 causales de cola (FALTA_SENTENCIA_DEFINITIVA,
# FALTA_FUNDAMENTACION_AUTONOMA, DEPOSITO_PREVIO) deben emitirse SOLO cuando
# outcome esta en OUTCOMES_GATE_GENERICO (igual que ya hace FUERA_DE_TERMINO),
# no para outcome 'otro'. Motivo: con 'otro' el parser no determino dispositivo
# de gate, y la frase causal puede venir de un antecedente citado o de un
# dictamen embebido, no del holding (FP 334_p419, H094).
#
# Como el cambio solo RESTRINGE (gatea), el unico efecto posible es quitar la
# etiqueta de cola a filas cuyo outcome no esta en gate-generico. Y la unica via
# de llegar a los chequeos de cola con outcome fuera de gate-generico es 'otro'
# (los outcomes de OUTCOME_A_CAUSA retornan antes; el resto retorna "" antes).
# Por eso la direccion se mide exactamente leyendo el CSV canonico: filas con
# causal de cola + outcome no-gate -> pasaran a "".
#
# El A/B old<->new sobre texto identico (M15) se hace despues con el parser real
# via check_regresion (NEW vs golden=OLD); este PoC solo predice la dimension.
#
# Uso (desde la raiz del repo):  python scripts/auditoria/H094/poc_cola_gate.py
# -----------------------------------------------------------------------------

import csv
import sys
from pathlib import Path

csv.field_size_limit(10 ** 7)

# espejo de los conjuntos de parser.py (solo lectura, no se importa el modulo)
COLA = {"FALTA_SENTENCIA_DEFINITIVA", "FALTA_FUNDAMENTACION_AUTONOMA", "DEPOSITO_PREVIO"}
GATE = {"desestima", "mal_concedido", "desierto", "inadmisible", "improcedente"}
NATIVAS = {"inadmisible_280", "inadmisible_acordada_4", "abstracto",
           "desistimiento", "caducidad"}


def _find_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "scripts" / "pipeline" / "parser.py").exists():
            return p
    return start.parents[1] if len(start.parents) >= 2 else start


def main():
    root = _find_root(Path(__file__).resolve().parent)
    csv_path = root / "output" / "parser" / "csjn_casos.csv"
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        sys.exit(f"[FATAL] no encuentro {csv_path}")

    total_cola = 0
    cambian = []        # (caso, causal, outcome) -> pasan a ""
    raros = []          # cola con outcome nativo (no deberia existir)
    with open(csv_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("tipo_entrada") != "fallo":
                continue
            ci, oc = r.get("causa_inadmisibilidad", ""), r.get("outcome", "")
            if ci in COLA:
                total_cola += 1
                if oc not in GATE:
                    cambian.append((r["caso_id_canonico"], ci, oc))
                if oc in NATIVAS:
                    raros.append((r["caso_id_canonico"], ci, oc))

    print(f"CSV               : {csv_path}")
    print(f"filas causal cola : {total_cola}")
    print(f"filas que CAMBIAN : {len(cambian)}  (cola + outcome fuera de gate-generico -> \"\")")
    for cid, ci, oc in cambian:
        print(f"  {cid}: {ci} (outcome={oc}) -> \"\"")
    print(f"sanity nativos    : {len(raros)}  (cola con outcome nativo; esperado 0)")
    if raros:
        for cid, ci, oc in raros:
            print(f"  [!] {cid}: {ci} (outcome={oc})")

    # criterio de aceptacion del PoC: el patch no debe mover ninguna fila de
    # gate-generico ni nativa; solo quita cola a los 'otro'.
    ok = (len(raros) == 0) and all(oc == "otro" for _, _, oc in cambian)
    print(f"\nPoC {'OK' if ok else 'REVISAR'}: el patch solo afecta filas cola+otro "
          f"({len(cambian)} fila/s), sin tocar gate-generico ni nativas.")


if __name__ == "__main__":
    main()
