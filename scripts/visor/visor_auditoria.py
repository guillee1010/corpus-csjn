#!/usr/bin/env python3
"""
visor_auditoria.py
------------------
Convierte el output markdown de auditar_fallo.py en una vista compacta,
con opciones de filtrado, estadísticas y múltiples formatos.

Por default guarda en output/visor/<nombre>_vista.md (crea el dir si no existe).
Usar --stdout para imprimir a consola.

Filtros de spans:
    --solo firma
    --solo caratula,firma
    --excluir catch_all
    --excluir catch_all,cuerpo_mayoria
    --incluir header_pagina          # header_pagina está oculto por default
    --sin-cuerpo                     # excluye cuerpo_mayoria,voto,dictamen,concurrencia,disidencia

Filtros de casos:
    --tomo 347
    --pagina 344
    --pagina 344,1081
    --con-alertas

Formato:
    --formato md                     # default
    --formato txt
    --formato csv
    --preview 10                     # truncar spans a N líneas

Navegación:
    --resumen                        # solo tabla de spans, sin contenido
    --stats                          # estadísticas

Output:
    (sin flags)                      # guarda en output/visor/<nombre>_vista.md
    --output ruta/archivo.md         # ruta explícita
    --stdout                         # imprime a consola

Ubicación en el repo: scripts/pipeline/visor_auditoria.py
"""

import re
import sys
import csv
import argparse
from io import StringIO
from pathlib import Path

EXCLUIDOS_DEFAULT = {"header_pagina", "catch_all_inicio"}
TIPOS_CUERPO = {"cuerpo_mayoria", "voto", "concurrencia", "disidencia", "dictamen"}
ORDEN_TIPOS = [
    "caratula", "sumario", "dictamen", "cuerpo_mayoria",
    "voto", "concurrencia", "disidencia", "firma", "catch_all", "catch_all_fin", "catch_all_inicio", "header_pagina",
]


# ---------------------------------------------------------------------------
# PARSEO
# ---------------------------------------------------------------------------

def parse_md(text: str) -> tuple[str, list[dict]]:
    caso_pattern = re.compile(r'^## ([\w_]+) — (.+?)$', re.MULTILINE)
    caso_matches = list(caso_pattern.finditer(text))
    encabezado = text[:caso_matches[0].start()].strip() if caso_matches else ""

    casos = []
    for i, m in enumerate(caso_matches):
        inicio = m.start()
        fin = caso_matches[i + 1].start() if i + 1 < len(caso_matches) else len(text)
        bloque = text[inicio:fin]
        casos.append({
            "id": m.group(1),
            "titulo": m.group(2).strip(),
            "localizacion": _extraer_localizacion(bloque),
            "resumen_tabla": _extraer_tabla(bloque),
            "invariantes": _extraer_invariantes(bloque),
            "borde_inferior": _extraer_borde(bloque),
            "alertas": _extraer_alertas(bloque),
            "spans": _extraer_spans(bloque),
        })
    return encabezado, casos


def _extraer_localizacion(bloque):
    lines = bloque.splitlines()
    resultado = []
    capturando = False
    for line in lines:
        if "**Localización**" in line:
            capturando = True
            continue
        if capturando:
            if line.startswith("**") or line.startswith("---"):
                break
            if line.strip():
                resultado.append(line.strip())
    return resultado


def _extraer_tabla(bloque):
    lines = bloque.splitlines()
    resultado = []
    en_tabla = False
    for line in lines:
        if "**Resumen de spans**" in line:
            en_tabla = True
            continue
        if en_tabla:
            if line.startswith("|"):
                resultado.append(line)
            elif resultado:
                break
    return "\n".join(resultado).strip()


def _extraer_invariantes(bloque):
    for line in bloque.splitlines():
        if "**Invariantes**" in line:
            return re.sub(r'\*\*Invariantes\*\*:?\s*', '', line).strip()
    return ""


def _extraer_borde(bloque):
    lines = bloque.splitlines()
    resultado = []
    capturando = False
    for line in lines:
        if "### Borde inferior" in line:
            capturando = True
            continue
        if capturando and line.strip() and not line.startswith("---"):
            resultado.append(line.strip())
    return " | ".join(resultado)


def _extraer_alertas(bloque):
    for line in bloque.splitlines():
        if "**Alertas**" in line:
            m = re.search(r'\*\*Alertas\*\*:?\s*`?([^`\n]+)`?', line)
            if m:
                return [a.strip() for a in m.group(1).split(",")]
    return []


def _extraer_spans(bloque):
    span_pattern = re.compile(
        r'^### \[span (\d+)\] ([\w_]+(?:\s+\[\d+\])?)\s+\((\d+)–(\d+)\)',
        re.MULTILINE
    )
    spans = []
    matches = list(span_pattern.finditer(bloque))
    for j, sm in enumerate(matches):
        numero = int(sm.group(1))
        tipo_raw = sm.group(2).strip()
        linea_inicio = int(sm.group(3))
        linea_fin = int(sm.group(4))
        span_inicio = sm.end()
        span_fin = matches[j + 1].start() if j + 1 < len(matches) else len(bloque)
        span_texto = bloque[span_inicio:span_fin]
        contenido = _extraer_codigo(span_texto)
        extra = {}
        for campo in ["Header", "Atribución"]:
            m2 = re.search(rf'\*\*{campo}\*\*: (.+)', span_texto)
            if m2:
                extra[campo.lower()] = m2.group(1).strip()
        tipo_base = re.sub(r'\s*\[\d+\]', '', tipo_raw).strip()
        sub_match = re.search(r'\[(\d+)\]', tipo_raw)
        sub = int(sub_match.group(1)) if sub_match else None
        spans.append({
            "numero": numero,
            "tipo": tipo_base,
            "sub": sub,
            "rango": (linea_inicio, linea_fin),
            "lineas": linea_fin - linea_inicio + 1,
            "contenido": contenido,
            "extra": extra,
        })
    return spans


def _extraer_codigo(texto):
    m = re.search(r'```\n(.*?)```', texto, re.DOTALL)
    return m.group(1).strip() if m else texto.strip()


# ---------------------------------------------------------------------------
# FILTROS
# ---------------------------------------------------------------------------

def filtrar_casos(casos, args):
    resultado = casos
    if args.tomo:
        resultado = [c for c in resultado if c["id"].startswith(f"{args.tomo}_")]
    if args.pagina:
        paginas = {p.strip() for p in args.pagina.split(",")}
        resultado = [c for c in resultado if
                     (m := re.search(r'_p(\d+)$', c["id"])) and m.group(1) in paginas]
    if args.con_alertas:
        resultado = [c for c in resultado if c["alertas"]]
    return resultado


def calcular_tipos_visibles(args):
    excluidos = set(EXCLUIDOS_DEFAULT)
    if args.incluir:
        for t in args.incluir.split(","):
            excluidos.discard(t.strip())
    if args.sin_cuerpo:
        excluidos.update(TIPOS_CUERPO)
    if args.excluir:
        for t in args.excluir.split(","):
            excluidos.add(t.strip())
    if args.solo:
        return {t.strip() for t in args.solo.split(",")}, set()
    return None, excluidos


def span_visible(span, whitelist, blacklist):
    tipo = span["tipo"]
    if whitelist is not None:
        return tipo in whitelist
    return tipo not in blacklist


# ---------------------------------------------------------------------------
# ESTADÍSTICAS
# ---------------------------------------------------------------------------

def generar_stats(casos, whitelist, blacklist):
    lines = ["# Estadísticas de auditoría", "", f"Casos analizados: {len(casos)}", ""]
    total_spans = total_lineas = 0
    tipo_counts: dict[str, int] = {}
    tipo_lineas: dict[str, int] = {}
    casos_con_alertas = 0
    alertas_counts: dict[str, int] = {}

    for caso in casos:
        if caso["alertas"]:
            casos_con_alertas += 1
            for a in caso["alertas"]:
                alertas_counts[a] = alertas_counts.get(a, 0) + 1
        for span in caso["spans"]:
            if not span_visible(span, whitelist, blacklist):
                continue
            total_spans += 1
            total_lineas += span["lineas"]
            t = span["tipo"]
            tipo_counts[t] = tipo_counts.get(t, 0) + 1
            tipo_lineas[t] = tipo_lineas.get(t, 0) + span["lineas"]

    lines += [f"Total spans visibles: {total_spans}", f"Total líneas visibles: {total_lineas}", ""]
    lines.append(f"{'Tipo':<25} {'Spans':>6} {'Líneas':>8} {'Prom':>8} {'% líneas':>9}")
    lines.append("-" * 60)
    for tipo in sorted(tipo_counts, key=lambda t: -tipo_lineas[t]):
        cnt = tipo_counts[tipo]
        lns = tipo_lineas[tipo]
        prom = lns / cnt if cnt else 0
        pct = (lns / total_lineas * 100) if total_lineas else 0
        lines.append(f"{tipo:<25} {cnt:>6} {lns:>8} {prom:>8.1f} {pct:>8.1f}%")
    lines += ["", f"Alertas: {casos_con_alertas} caso/s afectado/s", ""]
    if alertas_counts:
        for alerta, cnt in sorted(alertas_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {alerta}: {cnt}")
    else:
        lines.append("  Sin alertas.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# RENDERIZADO MD / TXT
# ---------------------------------------------------------------------------

_RE_HEADER_EMBEBIDO = re.compile(
    r'^\s*(\d{1,4}|FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s*$'
)

def _limpiar_headers_embebidos(contenido):
    """Elimina líneas de header_pagina embebidas dentro del contenido de un span."""
    lineas = contenido.splitlines()
    return "\n".join(l for l in lineas if not _RE_HEADER_EMBEBIDO.match(l))


def _aplicar_preview(contenido, preview):
    contenido = _limpiar_headers_embebidos(contenido)
    if not preview:
        return contenido
    lineas = contenido.splitlines()
    if len(lineas) <= preview:
        return contenido
    return "\n".join(lineas[:preview]) + f"\n… [{len(lineas) - preview} líneas omitidas]"


def renderizar_caso_md(caso, whitelist, blacklist, args):
    lines = [f"## {caso['id']} — {caso['titulo']}", ""]
    for l in caso["localizacion"]:
        lines.append(l)
    lines.append("")
    if caso["invariantes"]:
        lines.append(f"**Invariantes**: {caso['invariantes']}")
    if caso["borde_inferior"]:
        lines.append(f"**Borde**: {caso['borde_inferior']}")
    if caso["alertas"]:
        lines.append(f"**⚠ Alertas**: {', '.join(caso['alertas'])}")
    lines.append("")

    if args.resumen:
        if caso["resumen_tabla"]:
            lines += ["**Resumen de spans**", "", caso["resumen_tabla"]]
        lines += ["", "---", ""]
        return "\n".join(lines)

    # Identificar el catch_all inicial: el de linea_ini más baja que termina
    # antes del primer span semántico (residuo del caso anterior).
    # Se silencia por default salvo --incluir catch_all_inicio.
    TIPOS_SEMANTICOS = {"caratula", "sumario", "dictamen", "cuerpo_mayoria",
                        "voto", "concurrencia", "disidencia", "firma"}
    catch_alls = [s for s in caso["spans"] if s["tipo"] == "catch_all"]
    spans_semanticos = [s for s in caso["spans"] if s["tipo"] in TIPOS_SEMANTICOS]
    primer_semantico = min((s["rango"][0] for s in spans_semanticos), default=None)
    catch_all_inicio_ids = set()
    if catch_alls and primer_semantico is not None:
        candidato = min(catch_alls, key=lambda s: s["rango"][0])
        if candidato["rango"][1] < primer_semantico:
            catch_all_inicio_ids.add(id(candidato))

    grupos: dict[str, list] = {}
    for span in caso["spans"]:
        if id(span) in catch_all_inicio_ids:
            if whitelist is not None and "catch_all" not in whitelist and "catch_all_inicio" not in whitelist:
                continue
            if whitelist is None and "catch_all_inicio" not in (args.incluir or "").split(","):
                continue
        if span_visible(span, whitelist, blacklist):
            grupos.setdefault(span["tipo"], []).append(span)

    if not grupos:
        lines += ["*(sin spans visibles con los filtros actuales)*", "", "---", ""]
        return "\n".join(lines)

    conocidos = [t for t in ORDEN_TIPOS if t in grupos]
    desconocidos = [t for t in grupos if t not in ORDEN_TIPOS]

    for tipo in conocidos + desconocidos:
        spans_tipo = grupos[tipo]

        if tipo == "header_pagina":
            valores = list(dict.fromkeys(
                s["contenido"].replace("\n", " ").strip()
                for s in spans_tipo if s["contenido"].strip()
            ))
            resumen = ", ".join(valores[:6])
            if len(valores) > 6:
                resumen += f", … ({len(valores)} únicos)"
            lines += [f"**header_pagina** ×{len(spans_tipo)} → `{resumen}`", ""]
            continue

        if tipo == "sumario":
            lines += [f"### SUMARIO ({len(spans_tipo)} entradas)", ""]
            for s in spans_tipo:
                idx = s["sub"] if s["sub"] else s["numero"]
                lines += [f"**[{idx}]** {_aplicar_preview(s['contenido'], args.preview)}", ""]
            continue

        if tipo in TIPOS_CUERPO:
            for s in spans_tipo:
                rng = f"{s['rango'][0]}–{s['rango'][1]}"
                lines += [
                    f"### {tipo.upper().replace('_', ' ')} ({rng}, {s['lineas']} líneas)",
                    "",
                    _aplicar_preview(s["contenido"], args.preview),
                    ""
                ]
            continue

        # Cualquier otro tipo: firma, catch_all, caratula, epilogo, etc.
        label = tipo.upper().replace("_", " ")
        lines += [f"### {label} ({len(spans_tipo)} span/s)", ""]
        for s in spans_tipo:
            rng = f"{s['rango'][0]}–{s['rango'][1]}"
            lines += [f"*Líneas {rng}*", "", _aplicar_preview(s["contenido"], args.preview), ""]

    lines += ["---", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# RENDERIZADO CSV
# ---------------------------------------------------------------------------

def renderizar_csv(casos, whitelist, blacklist):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["caso_id", "caratula", "tipo_span", "sub",
                     "linea_inicio", "linea_fin", "n_lineas", "contenido"])
    for caso in casos:
        for span in caso["spans"]:
            if span_visible(span, whitelist, blacklist):
                writer.writerow([
                    caso["id"], caso["titulo"], span["tipo"],
                    span["sub"] if span["sub"] else "",
                    span["rango"][0], span["rango"][1], span["lineas"],
                    span["contenido"].replace("\n", " "),
                ])
    return output.getvalue()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Visor compacto de auditorías de auditar_fallo.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Default: guarda en output/visor/<nombre>_vista.md
Usar --stdout para imprimir a consola.

Ejemplos:
  python visor_auditoria.py output/auditoria/auditar_fallo/archivo.md
  python visor_auditoria.py archivo.md --stdout
  python visor_auditoria.py archivo.md --output ruta/custom.md
  python visor_auditoria.py archivo.md --solo firma
  python visor_auditoria.py archivo.md --solo caratula,firma --formato csv
  python visor_auditoria.py archivo.md --excluir catch_all --preview 20
  python visor_auditoria.py archivo.md --tomo 347 --pagina 344
  python visor_auditoria.py archivo.md --con-alertas --resumen
  python visor_auditoria.py archivo.md --stats
  python visor_auditoria.py archivo.md --incluir header_pagina
        """
    )

    parser.add_argument("entrada", help="Archivo .md de auditoría")

    # Output
    out_grp = parser.add_mutually_exclusive_group()
    out_grp.add_argument("--output", "-o", default=None,
        help="Ruta explícita de salida")
    out_grp.add_argument("--stdout", action="store_true",
        help="Imprimir a consola en lugar de guardar archivo")

    # Filtros de spans
    grp = parser.add_argument_group("Filtros de spans")
    excl = grp.add_mutually_exclusive_group()
    excl.add_argument("--solo", metavar="TIPOS",
        help="Mostrar solo estos tipos. Ej: firma  o  caratula,firma")
    excl.add_argument("--excluir", metavar="TIPOS",
        help="Excluir estos tipos. Ej: catch_all,cuerpo_mayoria")
    grp.add_argument("--incluir", metavar="TIPOS",
        help="Incluir tipos ocultos por default. Ej: header_pagina")
    grp.add_argument("--sin-cuerpo", action="store_true",
        help="Excluir cuerpo_mayoria, voto, dictamen, concurrencia, disidencia")

    # Filtros de casos
    grp2 = parser.add_argument_group("Filtros de casos")
    grp2.add_argument("--tomo", metavar="N",
        help="Mostrar solo casos del tomo N")
    grp2.add_argument("--pagina", metavar="N[,N]",
        help="Mostrar solo casos de estas páginas")
    grp2.add_argument("--con-alertas", action="store_true",
        help="Mostrar solo casos con alertas")

    # Formato
    grp3 = parser.add_argument_group("Formato")
    grp3.add_argument("--formato", choices=["md", "txt", "csv"], default="md",
        help="Formato de salida (default: md)")
    grp3.add_argument("--preview", metavar="N", type=int, default=None,
        help="Truncar contenido de spans a N líneas")

    # Navegación
    grp4 = parser.add_argument_group("Navegación")
    nav = grp4.add_mutually_exclusive_group()
    nav.add_argument("--resumen", action="store_true",
        help="Solo tabla de spans por caso, sin contenido")
    nav.add_argument("--stats", action="store_true",
        help="Estadísticas de spans, líneas y alertas")

    args = parser.parse_args()

    # Validar entrada
    ruta = Path(args.entrada)
    if not ruta.exists():
        print(f"Error: no existe '{ruta}'", file=sys.stderr)
        sys.exit(1)

    texto = ruta.read_text(encoding="utf-8")
    encabezado, casos = parse_md(texto)

    if not casos:
        print("No se encontraron casos.", file=sys.stderr)
        sys.exit(1)

    casos = filtrar_casos(casos, args)
    if not casos:
        print("Ningún caso coincide con los filtros.", file=sys.stderr)
        sys.exit(0)

    whitelist, blacklist = calcular_tipos_visibles(args)

    # Generar contenido
    if args.stats:
        salida = generar_stats(casos, whitelist, blacklist)

    elif args.formato == "csv":
        salida = renderizar_csv(casos, whitelist, blacklist)

    else:
        lines = ["# Vista compacta de auditoría", ""]
        for l in encabezado.splitlines():
            if any(k in l for k in ["Generado", "Versión", "Comando", "Casos", "alertas", "Seed"]):
                lines.append(l)

        filtros = []
        for flag, val in [
            ("--solo", args.solo), ("--excluir", args.excluir),
            ("--incluir", args.incluir), ("--tomo", args.tomo),
            ("--pagina", args.pagina), ("--preview", args.preview),
        ]:
            if val:
                filtros.append(f"{flag} {val}")
        for flag, cond in [
            ("--sin-cuerpo", args.sin_cuerpo),
            ("--con-alertas", args.con_alertas),
            ("--resumen", args.resumen),
        ]:
            if cond:
                filtros.append(flag)
        if filtros:
            lines.append(f"Filtros: {' '.join(filtros)}")
        lines += [f"Casos: {len(casos)}", "", "---", ""]

        for caso in casos:
            lines.append(renderizar_caso_md(caso, whitelist, blacklist, args))

        salida = "\n".join(lines)

        if args.formato == "txt":
            salida = re.sub(r'\*\*(.+?)\*\*', r'\1', salida)
            salida = re.sub(r'\*(.+?)\*', r'\1', salida)
            salida = re.sub(r'^#+\s+', '', salida, flags=re.MULTILINE)
            salida = re.sub(r'`([^`]+)`', r'\1', salida)

    # Determinar destino
    if args.stdout:
        print(salida)
        return

    if args.output:
        ruta_out = Path(args.output)
    else:
        # Default: output/visor/ relativo a donde se corre el script
        sufijo = "_stats" if args.stats else "_resumen" if args.resumen else "_vista"
        ext = ".csv" if args.formato == "csv" else ".txt" if args.formato == "txt" else ".md"
        # Buscar raíz del repo (directorio que contiene scripts/)
        repo_root = Path.cwd()
        dir_visor = repo_root / "output" / "visor"
        dir_visor.mkdir(parents=True, exist_ok=True)
        ruta_out = dir_visor / (ruta.stem + sufijo + ext)

    ruta_out.parent.mkdir(parents=True, exist_ok=True)
    ruta_out.write_text(salida, encoding="utf-8")
    print(f"Guardado en: {ruta_out}")


if __name__ == "__main__":
    main()
