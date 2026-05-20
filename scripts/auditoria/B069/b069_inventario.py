# B069 inventario - extrae tokens del caso siguiente para los 309 sin_firma
# cortados por Pista 1 (caratula_siguiente + fin_dentro_bloque).
#
# Uso:  python scripts/auditoria/b069_inventario.py
# Salida:  output/auditoria/b069_tokens.csv

import csv
import re
from pathlib import Path


def primer_token_de_caratula(nombres_indice):
    if not nombres_indice:
        return ""
    primera = nombres_indice.split("|")[0].strip()
    tokens = re.findall(r"[A-ZA-Za-z\u00c0-\u017f]+", primera)
    skip = {
        "otro", "otros", "sociedad", "sucesion", "sucesion",
        "empresa", "compania", "compania", "compania",
    }
    for t in tokens:
        if len(t) >= 4 and t.lower() not in skip:
            return t
    return tokens[0] if tokens else ""


def main():
    with open("output/parser/csjn_casos.csv", encoding="utf-8") as f:
        todos = list(csv.DictReader(f))
    print(f"Casos totales: {len(todos)}")

    por_tomo = {}
    for r in todos:
        por_tomo.setdefault(r["tomo"], []).append(r)
    for t in por_tomo:
        por_tomo[t].sort(key=lambda r: int(r["linea_inicio"]))

    siguiente = {}
    for t, lst in por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente[c["caso_id_canonico"]] = lst[i + 1]

    with open("output/auditoria/sin_firma_406.csv", encoding="utf-8") as f:
        sf = [
            r for r in csv.DictReader(f)
            if r["pista_fin"] == "caratula_siguiente"
            and r["status_fin"] == "fin_dentro_bloque"
        ]
    print(f"Sin firma por Pista 1 (fin_dentro_bloque): {len(sf)}")

    cols = [
        "caso_id_canonico", "tomo", "case_name_indice",
        "linea_inicio", "linea_fin", "linea_fin_real",
        "source_file",
        "sig_caso_id", "sig_caratula", "token_siguiente",
    ]
    out_path = Path("output/auditoria/b069_tokens.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sf:
            sig = siguiente.get(r["caso_id_canonico"])
            token = primer_token_de_caratula(sig["case_name_indice"]) if sig else ""
            w.writerow({
                "caso_id_canonico": r["caso_id_canonico"],
                "tomo": r["tomo"],
                "case_name_indice": r["case_name_indice"],
                "linea_inicio": r["linea_inicio"],
                "linea_fin": r["linea_fin"],
                "linea_fin_real": r["linea_fin_real"],
                "source_file": r["source_file"],
                "sig_caso_id": sig["caso_id_canonico"] if sig else "",
                "sig_caratula": sig["case_name_indice"] if sig else "",
                "token_siguiente": token,
            })

    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main()
