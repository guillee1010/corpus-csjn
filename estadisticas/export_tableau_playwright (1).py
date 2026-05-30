#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae el tablero Resueltos 2025 de la CSJN (Tableau Public) recorriendo los
story points por INTERACCIÓN real (Playwright clickea cada tab) y capturando
las respuestas que dispara el navegador (sesión viva, status 200). El parseo
lo hace TableauScraper sobre esas respuestas capturadas.

Por qué así: la sesión de Tableau Public solo vive dentro del navegador. Lanzar
los comandos desde Python da 410 (sesión consumida). Clickear el tab en el
navegador y capturar su respuesta sí funciona.

    pip install playwright TableauScraper pandas
    playwright install chromium
    python export_tableau_playwright.py
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from playwright.sync_api import sync_playwright
from tableauscraper import TableauScraper as TS, dashboard, utils

# ----------------------- config -----------------------
HEADLESS = False
WAIT_RENDER_MS = 9000
PER_TAB_MS = 2500           # espera tras clickear cada tab
BASE_DIR = Path(__file__).resolve().parent          # .../corpus-csjn/estadisticas
OUT_ROOT = BASE_DIR / "output_tableau"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
TAB_SELECTOR = ".tabStoryPointContent"

# Tableros a extraer: subcarpeta -> URL /views/. Comentá los que no quieras correr.
VIZZES = {
    "resueltos_2025": "https://public.tableau.com/views/CasosResueltos2025final/Resueltos",
    "ingresos_2025":  "https://public.tableau.com/views/Ingresos2025/INGRESOS",
    "resueltos_2024": "https://public.tableau.com/views/Resueltos2024/Resueltos",
    "ingresos_2024":  "https://public.tableau.com/views/CasosIngresadosCSJN2024/INGRESOS",
}
# -------------------------------------------------------


def slug(s):
    s = re.sub(r"[^\w\-]+", "_", str(s).strip())
    return s.strip("_")[:80] or "sin_nombre"


def parse_bootstrap(ts, txt):
    """Carga ts.info/ts.data/ts.dataSegments desde el texto del bootstrap."""
    m = re.search(r"\d+;({.*})\d+;({.*})", txt, re.MULTILINE)
    if not m:
        raise RuntimeError("bootstrap_no_parseable")
    ts.info = json.loads(m.group(1))
    ts.data = json.loads(m.group(2))
    if "presModelMap" in ts.data["secondaryInfo"]:
        pmm = ts.data["secondaryInfo"]["presModelMap"]
        ts.dataSegments = pmm["dataDictionary"]["presModelHolder"][
            "genDataDictionaryPresModel"]["dataSegments"]
        ts.parameters = utils.getParameterControlInput(ts.info)
    ts.dashboard = ts.info["sheetName"]


def volcar_cmd(ts, cmd_json, story_label, manifiesto, out_dir):
    """
    Extrae las hojas REALES del story point activo de una respuesta de
    set-active-story-point. Las hojas viven en:
      applicationPresModel.workbookPresModel.dashboardPresModel.zones
        -> zona con flipboard -> storyPoints[activeId].dashboardPresModel.zones
    y los dataSegments vienen en applicationPresModel.dataDictionary (no en el boot).
    """
    apm = cmd_json["vqlCmdResponse"]["layoutStatus"].get("applicationPresModel")
    if not apm:
        return 0
    seg = apm.get("dataDictionary", {}).get("dataSegments")
    if not seg:
        return 0
    df_full = utils.getDataFullCmdResponse(apm, seg)

    # localizar el flipboard y el story point activo
    root_zones = apm["workbookPresModel"]["dashboardPresModel"]["zones"]
    flip = None
    for z in root_zones.values():
        if isinstance(z, dict) and "flipboard" in z.get("presModelHolder", {}):
            flip = z["presModelHolder"]["flipboard"]
            break
    if not flip:
        return 0
    active = str(flip.get("activeStoryPointId"))
    sp = flip.get("storyPoints", {}).get(active)
    if not sp:
        return 0
    print(f"      (storyPointId activo={active})")
    subz = sp.get("dashboardPresModel", {}).get("zones", {})

    escritas = 0
    for zz in subz.values():
        if not isinstance(zz, dict):
            continue
        pmh = zz.get("presModelHolder", {})
        if "visual" not in pmh or "vizData" not in pmh.get("visual", {}):
            continue
        wsname = zz.get("worksheet", "?")
        try:
            frame = utils.getWorksheetCmdResponse(zz, df_full)
        except Exception as e:
            print(f"      {wsname}: parseo hoja {type(e).__name__}")
            continue
        if not frame:
            continue
        df = pd.DataFrame.from_dict(frame, orient="index").fillna(0).T
        n = len(df)
        # nombre de archivo: story point + hoja
        (out_dir / f"{slug(story_label)}__{slug(wsname)}.csv").write_bytes(
            df.to_csv(index=False).encode("utf-8-sig"))
        escritas += 1
        manifiesto.append({
            "historia": story_label, "hoja": wsname,
            "filas": n, "columnas": " | ".join(map(str, df.columns)),
        })
        print(f"      {wsname}: {n} filas, {len(df.columns)} cols")
    return escritas


def procesar_viz(ctx, viz_url, out_dir):
    """Extrae un tablero completo a out_dir. Devuelve (n_hojas, n_con_datos)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    manifiesto = []
    page = ctx.new_page()
    boot = {"text": None}
    last_cmd = {"text": None}

    def on_resp(r):
        url = r.url
        if "bootstrapSession" in url and boot["text"] is None:
            try: boot["text"] = r.text()
            except Exception: pass
        elif "set-active-story-point" in url:
            try: last_cmd["text"] = r.text()
            except Exception: pass

    page.on("response", on_resp)

    print(f"  [1] abriendo {viz_url.split('/views/')[-1]}")
    page.goto(f"{viz_url}?:embed=y&:showVizHome=no", wait_until="load", timeout=60000)
    for _ in range(int(WAIT_RENDER_MS / 500)):
        if boot["text"]:
            break
        page.wait_for_timeout(500)
    page.wait_for_timeout(2000)

    print(f"  [2] tsConfig={'tsConfigContainer' in page.content()}  "
          f"bootstrap={'OK' if boot['text'] else 'NO'}  title={page.title()!r}")
    if not boot["text"]:
        print("      Sin bootstrap. Subí WAIT_RENDER_MS. Salteando este viz.")
        page.close()
        return (0, 0)

    ts = TS()
    cfg = page.eval_on_selector("#tsConfigContainer", "el => el.value || el.textContent")
    ts.tableauData = json.loads(cfg)
    uri = urlparse(viz_url)
    ts.host = f"{uri.scheme}://{uri.netloc}"
    parse_bootstrap(ts, boot["text"])
    print(f"      dashboard={ts.dashboard!r}")

    tabs = page.locator(TAB_SELECTOR)
    total = tabs.count()
    seen = set()
    idxs = []
    for i in range(total):
        t = (tabs.nth(i).inner_text() or "").strip()
        if t and t not in seen:
            seen.add(t)
            idxs.append((i, t))
    print(f"  [3] tabs únicos: {len(idxs)} de {total}")

    print("  [4] recorriendo story points:")
    for i, txt in idxs:
        last_cmd["text"] = None
        try:
            tabs.nth(i).scroll_into_view_if_needed(timeout=4000)
            tabs.nth(i).click(timeout=6000)
        except Exception as e:
            print(f"      [{txt[:40]}] no pude clickear: {type(e).__name__}")
            continue
        for _ in range(int(PER_TAB_MS / 250)):
            if last_cmd["text"]:
                break
            page.wait_for_timeout(250)
        if not last_cmd["text"]:
            continue  # tab ya activo (portada) — sin comando
        try:
            cmd_json = json.loads(last_cmd["text"])
            volcar_cmd(ts, cmd_json, txt, manifiesto, out_dir)
        except Exception as e:
            print(f"      [{txt[:40]}] parseo: {type(e).__name__} {str(e)[:80]}")

    page.close()

    if manifiesto:
        man = pd.DataFrame(manifiesto)
        man.to_csv(out_dir / "_manifiesto.csv", index=False, encoding="utf-8-sig")
        con = man[man["filas"] > 0]
        print(f"  [5] {len(man)} hojas ({len(con)} con datos) -> {out_dir.name}\\")
        return (len(man), len(con))
    print("  [5] sin hojas.")
    return (0, 0)


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    resumen = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        ctx = browser.new_context(user_agent=UA, locale="es-AR",
                                  viewport={"width": 1920, "height": 1080})
        for sub, url in VIZZES.items():
            print(f"\n=== {sub} ===")
            try:
                resumen[sub] = procesar_viz(ctx, url, OUT_ROOT / sub)
            except Exception as e:
                print(f"  FALLO viz {sub}: {type(e).__name__} {str(e)[:120]}")
                resumen[sub] = ("error", str(e)[:60])
        browser.close()

    print("\n===== RESUMEN =====")
    for sub, r in resumen.items():
        print(f"  {sub:18} {r}")


if __name__ == "__main__":
    main()
