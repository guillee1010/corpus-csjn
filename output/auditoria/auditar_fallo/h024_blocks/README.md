# H024 — Bloques `.txt` de diagnóstico

Aparato probatorio de la sesión H024 (15/5/2026). Cada `.txt` es el
bloque exacto que el localizador (`output/localizacion/fallos_localizados.csv`)
asigna al caso testigo. Extraídos vía `Get-Content` con
`-TotalCount` / `-Skip` calculados a partir de `linea_inicio` y
`linea_fin` del localizador.

Ver `BITACORA.md` entrada H024 para análisis completo.

## Mapeo caso → archivos → bugs

| Archivo | Caso | Bordes | Bug(s) testimoniados |
|---|---|---|---|
| `bloque_332_p244.txt` | 332_p244 (Fernández c/ Fed. Asoc. Católicas) | LibroVol332.1.md, 9536-9713 (178 líneas, bloque entero) | **B044** (testigo principal), B022 V2b |
| `bloque_330_p829.txt` | 330_p829 (Brandsen c/ AFIP-DGI) | LibroVol330.1.md, 31412-31591 (180 líneas, bloque entero) | **B022 V1b** (testigo principal) |
| `bloque_346_p1205.txt` | 346_p1205 (Álvarez c/ Cancillería) | LibroVol346-2.md, 16883-16988 (106 líneas, bloque entero) | **B022 V2** + **B045** (cara N) |
| `bloque_346_p1205_extension.txt` | 346_p1205 + contexto post-bloque | LibroVol346-2.md, 16989-17048 (60 líneas adicionales) | Evidencia de **B045**: muestra que el fallo Álvarez continúa fuera del bloque del catálogo |
| `bloque_343_p2243_inicio.txt` | 343_p2243 (Salvatierra) — primeras 30 líneas | LibroVol343-3.md, 30534-30563 | **B025** + B022 V1b. Líneas 30541-30542 contienen firma del Gente Grossa que el parser captura espuriamente |
| `bloque_343_p2243_fin.txt` | 343_p2243 — últimas 41 líneas del bloque | LibroVol343-3.md, 30987-31027 | **B045** (cara N): bloque truncado al medio del considerando 4°, sin dispositiva ni firma |

## Auditoría regex aplicada

A cada `.txt` se le aplicaron las regex reales de
`scripts/pipeline/parser.py` líneas 57-167 (RE_APERTURA,
RE_FECHA_LINEA, RE_DICT_HDR, RE_VOTO_HDR, RE_DISID_HDR). Resultados
en BITACORA H024.

## Origen de la muestra

Los cuatro casos testigo son parte de la muestra de 80 con seed
`15052026` generada en H021 (`tabla_senales_80_15052026.csv`,
`auditoria_80_15052026.md`, no versionados). H022 los identificó
en el spot-check de 7 casos extremos. H023 verificó M2/M3; H024
verificó M1/M4/M5 + el huérfano `346_p1205`.

## Pendientes asociados (ver BITACORA H024 §Pendientes inmediatos)

1. Diagnóstico al nivel código de B045 en
   `scripts/pipeline/construir_catalogo.py` (sesión dedicada).
2. Re-medición de cardinalidad de B025 post §3.6.a contra CSV vivo.
3. Decisión de fix de B044: vía A (vía B045) o vía B (guardia
   espacial en parser.py 1513-1552).
