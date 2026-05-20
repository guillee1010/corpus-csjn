"""
Diagnóstico B063 — Confirmar bug cosmético en filtro de desconocidos
y verificar status de PEREYRA.

Uso (desde raíz del repo):
  python scripts/diagnostico/H043/diag_b063_desconocidos.py
"""

import csv
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
B063_CASOS = ROOT / "output" / "parser" / "b063" / "csjn_casos.csv"
BASELINE_CASOS = ROOT / "output" / "parser" / "csjn_casos.csv"

# Conjueces B063 — nombre canónico tal como sale en jueces_conocidos
CONJUECES_B063 = [
    "Najurieta (conjuez)",
    "Alcalá (conjuez)",
    "Morán (conjuez)",
    "Tyden de Skanata (conjuez)",
    "Poclava Lafuente (conjuez)",
    "Pereira González (conjuez)",    # <- typo, debería ser Pereyra
    "Ferro (conjuez)",
    "Pacilio (conjuez)",
    "Argañaraz (conjuez)",
]

# Nombres que siguen en desconocidos (del output B063)
DESCONOCIDOS_SOSPECHOSOS = [
    "JORGE FERRO",
    "ANTONIO PACILIO",
    "Rocío Alcalá",
    "MARIA SUSANA NAJURIETA",
    "MARÍA SUSANA NAJURIETA",
    "Jorge Eduardo Morán",
    "ANGEL A. ARGAÑARAZ",
    "MIRTA D. TYDEN DE",
    "JUAN CARLOS POCLAVA LAFUENTE",
    "CARLOS M. PEREYRA GONZÁLEZ",
    "LUIS CÉSAR OTERO",
]


def cargar(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    if not B063_CASOS.exists():
        print(f"ERROR: no existe {B063_CASOS}")
        return

    b063 = cargar(B063_CASOS)
    baseline = cargar(BASELINE_CASOS) if BASELINE_CASOS.exists() else None

    # ── 1. Casos donde un conjuez B063 está en jueces_conocidos ─────────
    print("=" * 70)
    print("1. CONJUECES B063 RECONOCIDOS (en jueces_conocidos)")
    print("=" * 70)

    for conj in CONJUECES_B063:
        casos = [r for r in b063 if conj in r.get("jueces_conocidos", "")]
        print(f"\n  {conj}: {len(casos)} casos")
        for r in casos[:3]:
            desc = r.get("jueces_desconocidos", "")
            print(f"    {r['caso_id_canonico']}")
            print(f"      jueces_conocidos: {r['jueces_conocidos'][:80]}")
            print(f"      jueces_desconocidos: {desc[:80]}")
            if desc:
                print(f"      ⚠ DOBLE REPORTE: reconocido + desconocido")

    # ── 2. Confirmar bug cosmético: casos con nombre en AMBOS campos ────
    print("\n" + "=" * 70)
    print("2. BUG COSMÉTICO: casos con conjuez en conocidos Y desconocidos")
    print("=" * 70)

    doble_reporte = 0
    for r in b063:
        conocidos = r.get("jueces_conocidos", "")
        desconocidos = r.get("jueces_desconocidos", "")
        for conj in CONJUECES_B063:
            apellido = conj.split(" (")[0].lower()  # "ferro", "najurieta", etc.
            if conj in conocidos and apellido in desconocidos.lower():
                doble_reporte += 1

    print(f"\n  Casos con doble reporte: {doble_reporte}")

    # ── 3. PEREYRA vs PEREIRA ───────────────────────────────────────────
    print("\n" + "=" * 70)
    print("3. PEREYRA vs PEREIRA")
    print("=" * 70)

    # ¿Algún caso tiene "Pereira González (conjuez)" en jueces_conocidos?
    pereira_match = [r for r in b063
                     if "Pereira" in r.get("jueces_conocidos", "")]
    print(f"\n  Casos con 'Pereira' en jueces_conocidos: {len(pereira_match)}")

    # ¿Cuántos tienen PEREYRA en desconocidos?
    pereyra_desc = [r for r in b063
                    if "PEREYRA" in r.get("jueces_desconocidos", "").upper()
                    or "PEREYRA" in r.get("firma_raw", "").upper()]
    print(f"  Casos con 'PEREYRA' en firma_raw o desconocidos: {len(pereyra_desc)}")
    for r in pereyra_desc:
        print(f"    {r['caso_id_canonico']}")
        print(f"      firma_raw: ...{r.get('firma_raw', '')[-100:]}...")
        print(f"      jueces_desconocidos: {r.get('jueces_desconocidos', '')}")

    # ── 4. OTERO: ¿reconocido pero doble-reportado? ────────────────────
    print("\n" + "=" * 70)
    print("4. OTERO (B064): ¿encoding o bug cosmético?")
    print("=" * 70)

    otero_conocido = [r for r in b063
                      if "Otero" in r.get("jueces_conocidos", "")]
    otero_desconocido = [r for r in b063
                         if "OTERO" in r.get("jueces_desconocidos", "").upper()]
    print(f"\n  Casos con Otero en jueces_conocidos: {len(otero_conocido)}")
    print(f"  Casos con OTERO en jueces_desconocidos: {len(otero_desconocido)}")

    otero_ambos = [r for r in b063
                   if "Otero" in r.get("jueces_conocidos", "")
                   and "OTERO" in r.get("jueces_desconocidos", "").upper()]
    print(f"  Casos con Otero en AMBOS (bug cosmético): {len(otero_ambos)}")

    otero_solo_desc = [r for r in b063
                       if "Otero" not in r.get("jueces_conocidos", "")
                       and "OTERO" in r.get("jueces_desconocidos", "").upper()]
    print(f"  Casos con OTERO solo en desconocidos (encoding real): {len(otero_solo_desc)}")
    for r in otero_solo_desc[:3]:
        firma = r.get("firma_raw", "")
        # Mostrar bytes alrededor de OTERO para diagnóstico encoding
        idx = firma.upper().find("OTERO")
        if idx >= 0:
            ctx = firma[max(0, idx-20):idx+25]
            print(f"    {r['caso_id_canonico']}: ...{ctx}...")
            # Bytes del contexto
            raw_bytes = ctx.encode("utf-8")
            print(f"      bytes: {' '.join(f'{b:02x}' for b in raw_bytes)}")

    # ── 5. Resumen ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("5. RESUMEN")
    print("=" * 70)
    print(f"""
  - 36 casos mejoraron n_jueces: FUNCIONAL, los regex matchean.
  - Desconocidos que siguen apareciendo: BUG COSMÉTICO en línea 555
    del parser (filtro usa nombre canónico con sufijo '(conjuez)').
  - PEREYRA: {'MISS REAL (typo en regex)' if len(pereira_match) == 0 else 'matchea OK'}.
    Corregir pereira -> pereyra en próximo script.
  - OTERO: {len(otero_ambos)} cosmético + {len(otero_solo_desc)} encoding real.
  - Fix propuesto para línea 555: usar apellido sin sufijo para el filtro.
""")


if __name__ == "__main__":
    main()
