"""
poc_b080.py — POC para RE_280_ABREVIADO

Simula el impacto de agregar una tercera regex de art. 280 que captura
formas abreviadas: CPCCN, C.P.C.C.N., CPCC.

Usa el CSV actual (considerando_text truncado a 2000 chars).
El parser ve el texto completo, así que el impacto real puede ser mayor.

Uso:
  cd corpus-csjn
  python poc_b080.py
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter

CASOS_CSV = Path("output/parser/csjn_casos.csv")

# ── Regexes actuales (B079) ──────────────────────────────────────────────

RE_280_CONSIDERANDO = re.compile(
    r"recurso\s+extraordinario.{0,150}?"
    r"(es|resulta|se\s+declara)\s+inadmisible"
    r".{0,150}?(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal",
    re.I | re.DOTALL
)

RE_280_LIBRE = re.compile(
    r"\(?\s*(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal\s+Civil\s+y\s+Comercial",
    re.I
)

# ── Regex nueva (B080) ──────────────────────────────────────────────────

RE_280_ABREVIADO = re.compile(
    r"\(?\s*(?:art\.?|art[íi]culo)\s*280\s+"
    r"(?:del\s+)?(?:CPCCN|C\.?\s*P\.?\s*C\.?\s*C\.?\s*N\.?|CPCC)\b",
    re.I
)

# ── Merit guard (B079) ──────────────────────────────────────────────────

MERIT_OUTCOMES = {
    "hace_lugar", "procedente", "revoca", "confirma", "nulidad",
    "competencia", "abstracto", "originaria", "desistimiento"
}

def _unhyphenate(text: str) -> str:
    return re.sub(r"(\w)[-\u00ad]\s+(\w)", r"\1\2", text)


def main():
    df = pd.read_csv(CASOS_CSV, low_memory=False)
    fallos = df[df["tipo_entrada"] == "fallo"].copy()
    print(f"Fallos: {len(fallos)}")
    print(f"280 actuales: {(fallos['outcome'] == 'inadmisible_280').sum()}")
    print()

    # ── Simular classify_outcome con y sin RE_280_ABREVIADO ─────────────

    changes = []
    already_280_also_abrev = 0

    for _, r in fallos.iterrows():
        ct = _unhyphenate(str(r["considerando_text"]))
        outcome = r["outcome"]

        old_280 = bool(RE_280_CONSIDERANDO.search(ct) or RE_280_LIBRE.search(ct))
        new_280 = bool(RE_280_ABREVIADO.search(ct))

        if new_280 and not old_280:
            # Nueva captura que la regex vieja no tenía
            protected = outcome in MERIT_OUTCOMES or outcome == "inadmisible_280"
            m = RE_280_ABREVIADO.search(ct)
            ctx = ct[max(0, m.start()-60):m.end()+30].replace("\n", " ")

            changes.append({
                "caso": r["caso_id_canonico"],
                "tomo": r["tomo"],
                "outcome_actual": outcome,
                "protected": protected,
                "context": ctx,
                "ct_len": len(ct),
            })

        if new_280 and old_280 and outcome == "inadmisible_280":
            already_280_also_abrev += 1

    # ── Reporte ─────────────────────────────────────────────────────────

    would_change = [c for c in changes if not c["protected"]]
    protected = [c for c in changes if c["protected"]]

    print("=" * 70)
    print(f"RE_280_ABREVIADO — nuevas capturas (sin regex vieja): {len(changes)}")
    print(f"  Cambiarían outcome → 280: {len(would_change)}")
    print(f"  Protegidos (merit/ya 280):  {len(protected)}")
    print(f"  Ya 280 + también abreviado: {already_280_also_abrev}")
    print("=" * 70)

    if would_change:
        print("\n── Cambios de outcome ──\n")
        for c in would_change:
            print(f"  {c['caso']:15s}  {c['outcome_actual']:20s} → inadmisible_280")
            print(f"    ...{c['context']}...")
            print(f"    ct_len={c['ct_len']}")
            print()

    if protected:
        print("\n── Protegidos (no cambian) ──\n")
        for c in protected:
            print(f"  {c['caso']:15s}  {c['outcome_actual']:20s}  (protegido)")
            print(f"    ...{c['context']}...")
            print()

    # ── Distribución por tomo de los cambios ────────────────────────────
    if would_change:
        print("\n── Cambios por tomo ──\n")
        tomo_dist = Counter(c["tomo"] for c in would_change)
        for t in sorted(tomo_dist):
            print(f"  tomo {t}: {tomo_dist[t]}")

    # ── Conteos proyectados ─────────────────────────────────────────────
    current_280 = (fallos["outcome"] == "inadmisible_280").sum()
    projected = current_280 + len(would_change)
    print(f"\n── Proyección ──")
    print(f"  280 actual:    {current_280}")
    print(f"  280 proyectado: {projected}  (+{len(would_change)})")
    print(f"\n  NOTA: esto es sobre considerando_text truncado a 2000 chars.")
    print(f"  El parser ve el texto completo — el impacto real puede ser mayor.")


if __name__ == "__main__":
    main()
