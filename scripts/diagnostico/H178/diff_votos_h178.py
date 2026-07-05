#!/usr/bin/env python3
"""
diff_votos_h178.py — dato fino H178: diff EXACTO por columna del golden de votos.
Compara git HEAD:scripts/tests/golden/csjn_casos_votos.csv (pre-paso-3) contra el
golden nuevo en disco, fila a fila (alineación posicional verificada por id).
Read-only. Correr desde la raíz del repo.
Esperado: is_merit_decision == 1078 · tipo_voto_sep (+acopladas) <= 17 · resto 0.
"""
import csv, io, subprocess, sys
import pandas as pd
csv.field_size_limit(10**7)

__version__ = "0.1"
PATH = "scripts/tests/golden/csjn_casos_votos.csv"

old_raw = subprocess.run(["git", "show", f"HEAD:{PATH}"],
                         capture_output=True, check=True).stdout
old = pd.read_csv(io.BytesIO(old_raw), dtype=str, keep_default_na=False)
new = pd.read_csv(PATH, dtype=str, keep_default_na=False)

if len(old) != len(new) or list(old.columns) != list(new.columns):
    sys.exit(f"[ABORT] estructura distinta: {len(old)}x{len(old.columns)} vs {len(new)}x{len(new.columns)}")

id_col = old.columns[0]  # caso_id_canonico (primera columna del schema de votos)
if (old[id_col] != new[id_col]).any():
    sys.exit("[ABORT] filas desalineadas por id — la comparación posicional no vale")
print(f"[OK] {len(old)} filas alineadas por {id_col}\n")

print("── diff exacto por columna ──")
cols_diff = {}
for col in old.columns:
    n = int((old[col] != new[col]).sum())
    if n:
        cols_diff[col] = n
        print(f"  {col}: {n}")
if not cols_diff:
    print("  (ninguna)")

if "tipo_voto_sep" in cols_diff:
    m = old["tipo_voto_sep"] != new["tipo_voto_sep"]
    det = [c for c in old.columns
           if c == id_col or "juez" in c.lower() or "posicion" in c.lower()]
    tabla = pd.DataFrame({c: new.loc[m, c] for c in det})
    tabla["tipo_voto_viejo"] = old.loc[m, "tipo_voto_sep"].values
    tabla["tipo_voto_nuevo"] = new.loc[m, "tipo_voto_sep"].values
    print("\n── flips de tipo_voto_sep (detalle) ──")
    print(tabla.to_string(index=False))
    trans = (old.loc[m, "tipo_voto_sep"] + " → " + new.loc[m, "tipo_voto_sep"]).value_counts()
    print("\n  transiciones:")
    print(trans.to_string())
else:
    print("\n(tipo_voto_sep sin flips — la cota 15/2 no se materializó: todos los D venían de ramas anteriores del cascade)")

filas_tocadas = int((old != new).any(axis=1).sum())
print(f"\nfilas con algún cambio: {filas_tocadas} (esperado 1078)")
