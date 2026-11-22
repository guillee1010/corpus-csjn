"""subir_dataverse.py — sube el paquete preparado a Harvard Dataverse como BORRADOR (H224)

Reemplaza a `dataverse.py` de IQSS/dataverse-uploader v1.7, que se cae en Harvard: consulta los locks con
autenticación básica, recibe una respuesta que no es JSON y aborta después del primer archivo (corrida
44993368912). Acá todo va por la API nativa con el encabezado `X-Dataverse-key`.

Pasos:
  1. Lee el dataset (DOI) y la última versión (borrador si existe, si no la publicada).
  2. Con --borrar-antes: borra uno por uno los archivos de esa versión (DELETE /api/files/{id}). Sobre una
     versión publicada, Dataverse crea un borrador y borra ahí; la versión publicada no se toca.
  3. Sube cada archivo de la lista cerrada (`_meta/dataverse/archivos_publicacion.txt`) con su carpeta
     (`directoryLabel`) y `tabIngest: false`, para que Dataverse NO convierta los CSV a .tab (así el sha256
     del archivo publicado coincide con el del manifest).
  4. Entre archivo y archivo espera a que el dataset no tenga locks.
  5. NUNCA publica. El operador revisa el borrador y publica desde la web.

Uso:
  python subir_dataverse.py RAIZ --doi doi:10.7910/DVN/TJTVKW [--server https://dataverse.harvard.edu]
                            [--borrar-antes] [--dry-run]
El token se lee de la variable de entorno DATAVERSE_TOKEN (nunca por argumento ni en el log).
"""
__version__ = "0.1"  # H224
import argparse, json, os, sys, time
from pathlib import Path
import requests


def _lista(raiz):
    p = raiz / "_lista_subida.txt"  # la escribe preparar_bundle_dataverse.py v0.5+ (la original se borra con _meta/)
    if not p.is_file():
        sys.exit("ERROR: falta _lista_subida.txt; correr antes preparar_bundle_dataverse.py --yo-se-que-borra")
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]


class DV:
    def __init__(self, server, token, doi):
        self.s = server.rstrip("/"); self.doi = doi
        self.h = {"X-Dataverse-key": token}

    def _ok(self, r, que):
        try:
            j = r.json()
        except ValueError:
            sys.exit(f"ERROR en {que}: HTTP {r.status_code}, respuesta no JSON: {r.text[:300]!r}")
        if r.status_code >= 300 or j.get("status") != "OK":
            sys.exit(f"ERROR en {que}: HTTP {r.status_code}: {json.dumps(j)[:500]}")
        return j["data"]

    def dataset(self):
        r = requests.get(f"{self.s}/api/datasets/:persistentId/", params={"persistentId": self.doi}, headers=self.h, timeout=60)
        return self._ok(r, "leer el dataset")

    def esperar_locks(self, ds_id, max_s=600):
        t0 = time.time()
        while True:
            r = requests.get(f"{self.s}/api/datasets/{ds_id}/locks", headers=self.h, timeout=60)
            try:
                locks = r.json().get("data") or []
            except ValueError:
                locks = None  # respuesta rara: esperar un poco y seguir, no abortar
            if not locks:
                return
            if time.time() - t0 > max_s:
                sys.exit(f"ERROR: el dataset sigue con locks después de {max_s}s: {locks}")
            time.sleep(3)

    def borrar(self, file_id):
        r = requests.delete(f"{self.s}/api/files/{file_id}", headers=self.h, timeout=120)
        self._ok(r, f"borrar el archivo {file_id}")

    def subir(self, ruta, directory_label, nombre):
        meta = {"directoryLabel": directory_label, "tabIngest": "false",
                "description": "Uploaded from github.com/guillee1010/corpus-csjn (subir_dataverse.py)."}
        for intento in range(5):
            with open(ruta, "rb") as fh:
                r = requests.post(f"{self.s}/api/datasets/:persistentId/add", params={"persistentId": self.doi},
                                  headers=self.h, files={"file": (nombre, fh)},
                                  data={"jsonData": json.dumps(meta)}, timeout=1800)
            if r.status_code == 400 and "lock" in r.text.lower():
                time.sleep(5 * (intento + 1)); continue
            return self._ok(r, f"subir {directory_label}/{nombre}")
        sys.exit(f"ERROR: {directory_label}/{nombre} siguió bloqueado tras 5 intentos")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raiz")
    ap.add_argument("--doi", required=True)
    ap.add_argument("--server", default="https://dataverse.harvard.edu")
    ap.add_argument("--borrar-antes", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    raiz = Path(a.raiz).resolve()
    lista = _lista(raiz)
    faltan = [x for x in lista if not (raiz / x).is_file()]
    if faltan:
        sys.exit(f"ERROR: faltan en la copia {faltan} (¿corrió preparar_bundle_dataverse.py?)")
    print(f"subir_dataverse v{__version__} · {len(lista)} archivos · {a.doi} · {'DRY-RUN' if a.dry_run else 'sube como borrador'}")
    if a.dry_run:
        for x in lista: print("  ", x)
        return
    token = os.environ.get("DATAVERSE_TOKEN", "")
    if not token:
        sys.exit("ERROR: falta la variable de entorno DATAVERSE_TOKEN")
    dv = DV(a.server, token, a.doi)
    ds = dv.dataset(); ds_id = ds["id"]; v = ds["latestVersion"]
    print(f"dataset id {ds_id} · última versión {v.get('versionNumber')}.{v.get('versionMinorNumber')} estado {v.get('versionState')} · {len(v.get('files', []))} archivos")
    if a.borrar_antes:
        for f in v.get("files", []):
            df = f["dataFile"]
            dv.esperar_locks(ds_id)
            dv.borrar(df["id"])
            print(f"  borrado: {f.get('directoryLabel', '')}/{f['label']}")
    for i, x in enumerate(lista, 1):
        p = Path(x)
        dv.esperar_locks(ds_id)
        d = dv.subir(raiz / x, p.parent.as_posix(), p.name)
        fid = d["files"][0]["dataFile"]["id"] if d.get("files") else "?"
        print(f"  [{i}/{len(lista)}] subido: {x} (id {fid})")
    dv.esperar_locks(ds_id)
    ds = dv.dataset(); v = ds["latestVersion"]
    print(f"\nOK · borrador con {len(v.get('files', []))} archivos (estado {v.get('versionState')}). No se publicó nada.")


if __name__ == "__main__":
    main()
