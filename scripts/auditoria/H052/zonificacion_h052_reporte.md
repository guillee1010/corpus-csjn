# Zonificación H052 — Reporte (fix concordancia dictamen)

Casos procesados: 5671


## Concordancia zonificador vs parser


### firma: 5656/5671 (99.7%)

Discrepancias (15):

- `329_p1568` (t329, span=710): parser=sin_firma zonif=True
- `329_p1928` (t329, span=51): parser=sin_firma zonif=True
- `329_p3564` (t329, span=157): parser=sin_firma zonif=True
- `329_p4135` (t329, span=175): parser=sin_firma zonif=True
- `329_p4170` (t329, span=62): parser=sin_firma zonif=True
- `329_p4176` (t329, span=78): parser=sin_firma zonif=True
- `329_p5151` (t329, span=236): parser=sin_firma zonif=True
- `330_p1643` (t330, span=22): parser=sin_firma zonif=True
- `330_p4071` (t330, span=206): parser=sin_firma zonif=True
- `334_p1920` (t334, span=212): parser=sin_firma zonif=True
- `344_p1102` (t344, span=1391): parser=sin_firma zonif=True
- `345_p378` (t345, span=7): parser=sin_firma zonif=True
- `345_p715` (t345, span=39): parser=sin_firma zonif=True
- `346_p1068` (t346, span=12): parser=sin_firma zonif=True
- `347_p1084` (t347, span=1730): parser=sin_firma zonif=True


### disp: 5649/5671 (99.6%)

Discrepancias (22):

- `329_p2121` (t329, span=143): parser=sin_dispositivo zonif=True
- `329_p3872` (t329, span=243): parser=sin_dispositivo zonif=True
- `329_p4135` (t329, span=175): parser=sin_dispositivo zonif=True
- `329_p5151` (t329, span=236): parser=sin_dispositivo zonif=True
- `330_p1971` (t330, span=173): parser=sin_dispositivo zonif=True
- `330_p4064` (t330, span=247): parser=sin_dispositivo zonif=True
- `330_p4687` (t330, span=132): parser=otro zonif=False
- `331_p1013` (t331, span=207): parser=sin_dispositivo zonif=True
- `332_p2418` (t332, span=266): parser=sin_dispositivo zonif=True
- `334_p109` (t334, span=429): parser=sin_dispositivo zonif=True
- `334_p829` (t334, span=333): parser=hace_lugar zonif=False
- `337_p166` (t337, span=534): parser=sin_dispositivo zonif=True
- `337_p1006` (t337, span=284): parser=sin_dispositivo zonif=True
- `339_p662` (t339, span=549): parser=sin_dispositivo zonif=True
- `340_p232` (t340, span=139): parser=sin_dispositivo zonif=True
- `340_p538` (t340, span=78): parser=sin_dispositivo zonif=True
- `340_p812` (t340, span=106): parser=sin_dispositivo zonif=True
- `343_p473` (t343, span=126): parser=sin_dispositivo zonif=True
- `344_p325` (t344, span=150): parser=sin_dispositivo zonif=True
- `344_p776` (t344, span=220): parser=sin_dispositivo zonif=True
- `344_p1952` (t344, span=1962): parser=sin_dispositivo zonif=True
- `344_p2123` (t344, span=1884): parser=sin_dispositivo zonif=True


### dictamen: 5671/5671 (100.0%)


## Dictamen: 4 cuadrantes

| Cuadrante | N | % |
|---|---|---|
| ambos_sí (parser=True, zonif=True) | 3330 | 58.7% |
| ambos_no (parser=False, zonif=False) | 2341 | 41.3% |
| zonif_only (parser=False, zonif=True) | 0 | 0.0% |
| parser_only (parser=True, zonif=False) | 0 | 0.0% |


## Clasificación por zonificador

| Clasificación | Total | sin_firma del parser |
|---|---|---|
| fallo_completo | 5613 | 6 |
| fallo_sin_dispositivo | 37 | 12 |
| fallo_sin_firma | 15 | 15 |
| sumario_editorial | 6 | 5 |


## Candidatos a reclasificar como sumario_editorial (5)

Estos casos tienen `voting_pattern=sin_firma` en el parser pero el zonificador no detecta ni cuerpo ni dispositivo.

- `329_p3564` (t329, span=157)
- `330_p1643` (t330, span=22)
- `345_p378` (t345, span=7)
- `345_p715` (t345, span=39)
- `346_p1068` (t346, span=12)


## Fallos sin_firma donde el zonificador SÍ ve firma (15)

Posible firma del caso anterior en el bloque, o firma que el parser no alcanzó.

- `329_p1568` (t329, span=710, clasif=fallo_completo)
- `329_p1928` (t329, span=51, clasif=fallo_sin_dispositivo)
- `329_p3564` (t329, span=157, clasif=sumario_editorial)
- `329_p4135` (t329, span=175, clasif=fallo_completo)
- `329_p4170` (t329, span=62, clasif=fallo_sin_dispositivo)
- `329_p4176` (t329, span=78, clasif=fallo_sin_dispositivo)
- `329_p5151` (t329, span=236, clasif=fallo_completo)
- `330_p1643` (t330, span=22, clasif=sumario_editorial)
- `330_p4071` (t330, span=206, clasif=fallo_completo)
- `334_p1920` (t334, span=212, clasif=fallo_sin_dispositivo)
- `344_p1102` (t344, span=1391, clasif=fallo_completo)
- `345_p378` (t345, span=7, clasif=sumario_editorial)
- `345_p715` (t345, span=39, clasif=sumario_editorial)
- `346_p1068` (t346, span=12, clasif=sumario_editorial)
- `347_p1084` (t347, span=1730, clasif=fallo_completo)


## Distribución promedio de zonas (sobre 5671 casos)

| Zona | Total líneas | Promedio | Casos con zona |
|---|---|---|---|
| sumario | 167479 | 29.5 | 3800 |
| dictamen | 385226 | 67.9 | 3330 |
| cuerpo | 498737 | 87.9 | 5598 |
| dispositivo | 211059 | 37.2 | 5628 |
| firma | 65499 | 11.5 | 5648 |
| voto | 16648 | 2.9 | 2153 |
| epilogo | 234813 | 41.4 | 4526 |
| header | 137614 | 24.3 | 5668 |
| intersticio | 110027 | 19.4 | 5156 |
