"""preparar_bundle_dataverse.py — arma el paquete a subir a Dataverse en una copia descartable del repo (H224)

Corre en el runner de GitHub Actions sobre la copia que hace `actions/checkout` (NUNCA en el disco del
operador: BORRA archivos). Deja en la copia SOLO lo que lista `_meta/dataverse/archivos_publicacion.txt`:

  1. crea `dataverse/` con `README.md` (desde `_meta/dataverse/README.md`) y `CODEBOOK.md` (copia de la raíz);
  2. dentro de las carpetas que se suben (`output/parser`, `scripts/pipeline`, `dataverse`) borra todo
     archivo que no esté en la lista;
  3. verifica que lo que queda sea EXACTAMENTE la lista (ni uno más, ni uno menos) y que el manifest
     declare los 10 CSV que se suben; si no, sale con error y el workflow no sube nada.

Uso:  python scripts/auxiliares/preparar_bundle_dataverse.py RAIZ_DE_LA_COPIA [--yo-se-que-borra]
Imprime la lista final con tamaños. Sin `--yo-se-que-borra` solo verifica, no borra ni copia.
"""
__version__ = "0.1"  # H224
import json, shutil, sys
from pathlib import Path

CARPETAS = ("output/parser", "scripts/pipeline", "dataverse")


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: preparar_bundle_dataverse.py RAIZ [--yo-se-que-borra]")
    raiz = Path(sys.argv[1]).resolve()
    borra = "--yo-se-que-borra" in sys.argv
    lista_p = raiz / "_meta/dataverse/archivos_publicacion.txt"
    lista = [l.strip() for l in lista_p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    if len(set(lista)) != len(lista):
        sys.exit("ERROR: la lista tiene duplicados")
    errores = []
    for x in lista:
        if not x.startswith(tuple(c + "/" for c in CARPETAS)):
            errores.append(f"en la lista pero fuera de las carpetas que se suben: {x}")

    readme_src = raiz / "_meta/dataverse/README.md"
    if not readme_src.is_file():
        errores.append("falta _meta/dataverse/README.md (el README del dataset)")
    if borra and not errores:
        (raiz / "dataverse").mkdir(exist_ok=True)
        shutil.copyfile(readme_src, raiz / "dataverse/README.md")
        shutil.copyfile(raiz / "CODEBOOK.md", raiz / "dataverse/CODEBOOK.md")
        for c in CARPETAS:
            for p in sorted((raiz / c).rglob("*")):
                if p.is_file() and p.relative_to(raiz).as_posix() not in lista:
                    p.unlink()

    presentes = sorted(p.relative_to(raiz).as_posix() for c in CARPETAS if (raiz / c).exists()
                       for p in (raiz / c).rglob("*") if p.is_file())
    sobran = sorted(set(presentes) - set(lista))
    faltan = sorted(set(lista) - set(presentes))
    if borra:
        errores += [f"sobra: {x}" for x in sobran] + [f"falta: {x}" for x in faltan]
    else:
        errores += [f"falta: {x}" for x in faltan if not x.startswith("dataverse/")]
        if sobran: print(f"(modo verificación: {len(sobran)} archivos se borrarían en la copia de CI)")

    man = json.loads((raiz / "output/parser/_manifest.json").read_text(encoding="utf-8"))
    csv_lista = {Path(x).name for x in lista if x.startswith("output/parser/") and x.endswith(".csv")}
    csv_man = {Path(k).name for k in man.get("outputs", {})}
    if csv_lista != csv_man:
        errores.append(f"los CSV de la lista no coinciden con los outputs del manifest: {sorted(csv_lista ^ csv_man)}")

    print(f"preparar_bundle_dataverse v{__version__} · {'BORRA (copia de CI)' if borra else 'solo verifica'} · {len(lista)} archivos en la lista")
    for x in lista:
        p = raiz / x
        print(f"  {x}  {p.stat().st_size if p.exists() else 'NO ESTÁ'}")
    if errores:
        print("\nERROR, no se sube nada:")
        for e in errores: print("  - " + e)
        sys.exit(1)
    print("\nOK: el paquete es exactamente la lista.")


if __name__ == "__main__":
    main()
