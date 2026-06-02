import csv, re, sys
from pathlib import Path
csv.field_size_limit(10**7)
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT/"scripts"/"pipeline"))
try:
    from parser import _unhyphenate
except Exception:
    def _unhyphenate(t): return (t or "").replace("\xad","")
def norm(t): return re.sub(r"\s+"," ",_unhyphenate(t or "")).lower()
FUERTES=("autos y vistos","por ello se resuelve","por ello, se resuelve","por ello se desestima","por ello, se desestima")
DEBILES=("se resuelve","se desestima la queja","se declara mal concedido","se confirma la sentencia","se revoca la sentencia","se hace lugar")
rows=[r for r in csv.DictReader(open(ROOT/"output"/"parser"/"csjn_casos.csv",encoding="utf-8")) if r.get("tipo_entrada")=="sumario_con_link"]
print("sumario_con_link total:", len(rows))
fuerte=[]; debil=[]; sinloc=0
for r in rows:
    sf=(r.get("source_file") or "").strip(); li=(r.get("linea_inicio") or "").strip(); lf=(r.get("linea_fin_real") or r.get("linea_fin") or "").strip()
    md=ROOT/"corpus"/sf
    if not (sf and li and lf and md.exists()): sinloc+=1; continue
    blk=norm(" ".join(md.read_text(encoding="utf-8").splitlines()[int(li):int(lf)+1]))
    hf=[m for m in FUERTES if m in blk]; hd=[m for m in DEBILES if m in blk]
    cid=r.get("caso_id_canonico"); n=int(lf)-int(li)+1
    if hf: fuerte.append((cid,n,";".join(hf+hd)))
    elif hd: debil.append((cid,n,";".join(hd)))
print("FUERTE (casi seguro fallo):", len(fuerte))
print("solo DEBIL (revisar):", len(debil))
print("sospechosos:", len(fuerte)+len(debil), "/", len(rows))
print("sin loc/.md:", sinloc)
out=ROOT/"scripts"/"diagnostico"/"H099"/"sumario_con_link_con_fallo.csv"
out.parent.mkdir(parents=True,exist_ok=True)
with open(out,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["caso_id","lineas","fuerza","marcadores"])
    [w.writerow([cid,n,"FUERTE",h]) for cid,n,h in sorted(fuerte)]
    [w.writerow([cid,n,"DEBIL",h]) for cid,n,h in sorted(debil)]
print("escrito:", out)
[print("  ",cid,n,"ln  [",h,"]") for cid,n,h in sorted(fuerte)[:20]]
