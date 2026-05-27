# Auditoría de fallos
Generado: 2026-05-17 23:37
Versión: 1.0.0
Comando: `diag_h036 --categoria A3_otro_con_verbo --n 10 --seed 42`
Casos auditados: 10
Seed: 42
Borde inferior: solapado_con_proximo=10 | alertas totales: 10

---

## 342_p122 — Iñigo, David Gustavo y Otros s/ Privación ilegítima de la libertad

**Localización**
- Archivo: `LibroVol342-1.md`
- Páginas catálogo: 122–126 | Página consultada: 126
- Líneas catálogo: 4922–5067 | Línea fin real: 5089 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 4922–4922 | 1 |
| 2 | header_pagina | 4923–4923 | 1 |
| 3 | header_pagina | 4924–4924 | 1 |
| 4 | catch_all | 4925–4950 | 26 |
| 5 | caratula | 4951–4951 | 1 |
| 6 | sumario [1] | 4952–4959 | 8 |
| 7 | header_pagina | 4957–4957 | 1 |
| 8 | header_pagina | 4958–4958 | 1 |
| 9 | header_pagina | 4959–4959 | 1 |
| 10 | sumario [2] | 4960–4964 | 5 |
| 11 | sumario [3] | 4965–4969 | 5 |
| 12 | sumario [4] | 4970–4983 | 14 |
| 13 | cuerpo_mayoria | 4984–5080 | 97 |
| 14 | header_pagina | 4990–4990 | 1 |
| 15 | header_pagina | 4991–4991 | 1 |
| 16 | header_pagina | 4992–4992 | 1 |
| 17 | header_pagina | 5030–5030 | 1 |
| 18 | header_pagina | 5031–5031 | 1 |
| 19 | header_pagina | 5032–5032 | 1 |
| 20 | header_pagina | 5068–5068 | 1 |
| 21 | header_pagina | 5069–5069 | 1 |
| 22 | header_pagina | 5070–5070 | 1 |
| 23 | firma | 5081–5082 | 2 |
| 24 | catch_all | 5083–5089 | 7 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=33 (19.64% del bloque, n=168)

---

### [span 1] header_pagina (4922–4922)
```
342
```

### [span 2] header_pagina (4923–4923)
```
122
```

### [span 3] header_pagina (4924–4924)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 4] catch_all (4925–4950)
```
quo concluyó que la actora no gozaba de una exención en el impuesto 
al valor agregado, consideró inaplicable la previsión contenida en el 
art. 18 de la ley del impuesto a las ganancias y, en consecuencia, coin­
cidió con el fisco en que los importes facturados por sus proveedores 
debían ser computados como créditos fiscales frente al IVA y no como 
gastos deducibles en los términos del citado art. 18 de aquel impuesto 
(fs. 958 vta.), argumentos estos que han quedado sin contestación algu­
na por parte de la actora. Más infundada aun, resulta la queja expuesta 
a fs. 980 vta., pues la apelante no desarrolló ningún argumento aten­
dible para ser eximida del pago de los intereses resarcitorios, cuya 
exigibilidad dispuso el tribunal a quo con sustento en la jurisprudencia 
de esta Corte.
Por ello, oída la señora Procuradora Fiscal, se declara inadmisible 
el recurso de queja, se rechaza el recurso extraordinario y se confirma 
la sentencia. Con costas. Declárase perdido el depósito agregado a fs. 
63 del recurso de hecho y archívese la queja. Notifíquese y, oportuna­
mente, devuélvase.
Elena I. Highton de Nolasco — Horacio Rosatti.
Recurso extraordinario y recurso de hecho interpuestos por: la actora con la represen­
tación y el patrocinio letrado del Dr. Eduardo Marcelo Gil Roca.
Traslado contestado por el Fisco Nacional, representado por la Dra. María Alejandra 
Repila, con el patrocinio letrado de la Dra. Agostina Carla García.
Tribunal de origen: Cámara Nacional de Apelaciones en lo Contencioso Administra­
tivo Federal, Sala I.
Tribunal que intervino con anterioridad: Tribunal Fiscal de la Nación, Sala A.
IÑIGO, DAVID GUSTAVO y Otros s/ Privación ilegítima de la
```

### [span 5] caratula (4951–4951)
```
IÑIGO, DAVID GUSTAVO y Otros s/ Privación ilegítima de la libertad

```

### [span 6] sumario [1] (4952–4959)
**Header**: JUICIO CRIMINAL
**Atribución**: (sin atribución detectada)
```
JUICIO CRIMINAL
En materia criminal, en la que se encuentran en juego los derechos 
esenciales de la libertad y el honor, deben extremarse los recaudos que 
garanticen plenamente el ejercicio del derecho de defensa.

123
DE JUSTICIA DE LA NACIÓN
342
```

### [span 7] header_pagina (4957–4957)
```
123
```

### [span 8] header_pagina (4958–4958)
```
DE JUSTICIA DE LA NACIÓN
```

### [span 9] header_pagina (4959–4959)
```
342
```

### [span 10] sumario [2] (4960–4964)
**Header**: DEFENSA EN JUICIO
**Atribución**: (sin atribución detectada)
```
DEFENSA EN JUICIO
El ejercicio de la defensa debe ser cierto, de modo tal que quien sufre un 
proceso penal ha de ser provisto de un adecuado asesoramiento legal, al 
extremo de suplir su negligencia en la provisión de defensor aseguran­
do, de este modo, la realidad sustancial de la defensa en juicio.
```

### [span 11] sumario [3] (4965–4969)
**Header**: DEBIDO PROCESO
**Atribución**: (sin atribución detectada)
```
DEBIDO PROCESO
No basta para cumplir con las exigencias básicas del debido proceso 
que el acusado haya tenido patrocinio letrado de manera formal, sino 
que es menester además que aquel haya recibido una efectiva y sustan­
cial asistencia de parte de su defensor.
```

### [span 12] sumario [4] (4970–4983)
**Header**: DEFENSA EN JUICIO
**Atribución**: (sin atribución detectada)
```
DEFENSA EN JUICIO
Si el defensor oficial se ha limitado a acompañar un escrito que, por 
vía de principio, estaría destinado a ser descalificado ante la instancia 
extraordinaria no solo por incumplimientos extrínsecos, vinculados con 
la desatención de los requisitos establecidos por el art. 7° de la acordada 
4/2007, sino, además, con la ausencia casi completa de referencias a la 
concreta situación procesal de su pupila y a los motivos alegados para 
la habilitación de la instancia federal en su favor, el tribunal superior 
debió haber asumido con mayor prudencia la misión que le compete, 
en orden a tomar a su cargo el aseguramiento de la efectiva tutela de 
la inviolabilidad de la defensa pues, de otro modo, quedaría completa­
mente desvirtuado el sentido de la doctrina del Tribunal según la cual 
los recursos procesales constituyen una facultad del imputado y no una 
potestad técnica del defensor.
```

### [span 13] cuerpo_mayoria (4984–5080)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 26 de febrero de 2019.
Vistos los autos: “Recurso de hecho deducido por María Azucena 
Márquez en la causa Iñigo, David Gustavo y otros s/ privación ilegíti­
ma de la libertad”, para decidir sobre su procedencia.

342
124
FALLOS DE LA CORTE SUPREMA
1°) Que estas actuaciones se inician con la presentación de Ma­
ría Azucena Márquez, quien manifestó ante el Tribunal su voluntad 
de impugnar la decisión de la Suprema Corte de Tucumán por la que 
se habría rechazado su recurso extraordinario –también incoado in 
pauperis forma– contra la condena recaída a su respecto en la causa 
“Iñigo, David Gustavo y otros s/ privación ilegítima de la libertad”.
Según alegó, la peticionaria se encontraría bajo arresto domicilia­
rio en la Provincia de La Rioja y sin posibilidad material de acceder a 
las oficinas de la Defensoría Oficial de Tucumán. En cuanto al rechazo 
del remedio federal que había intentado, no habría sido notificada en 
forma personal, sino que luego de enterarse por los medios de dicha 
desestimación, se habría comunicado con la defensa pública oficial 
que le habría remitido copia de la cédula de notificación respectiva.
2°) Que con la finalidad de garantizar debidamente el derecho de 
defensa en juicio de Márquez, el legajo fue remitido a la corte tucu­
mana a fin de que arbitrara los medios necesarios para que en dicha 
jurisdicción se fundamentara técnicamente la voluntad recursiva ex­
presada, de conformidad con el criterio del Tribunal en el caso CSJ 
746/2011 (47-G)/CS1 “Godoy, Matías Rafael s/ homicidio simple –causa 
n° 4364-”, del 25 de febrero de 2014.
3°) Que a pesar de lo ordenado por esta Corte, la presentación en 
cuestión fue devuelta a esta instancia luego de que en sede provincial 
se hubiera notificado a un letrado que, según el sistema “Lex doctor”, 
aparecería como el defensor técnico de la nombrada, pero sin que se 
hubiera satisfecho la fundamentación reclamada, ni aportado ninguna 
aclaración o justificación para adoptar este temperamento.
4°) Que ante el incumplimiento de lo ordenado, se volvió a disponer 
la remisión de las actuaciones al tribunal superior provincial. Esta vez, 
el legajo volvió a esta Corte con el escrito suscripto por el Defensor 
Oficial Penal de Va. Nominación del Centro Judicial Capital de la Pro­
vincia de Tucumán que obra a fs. 12/15, pero sin que se hubiera dado 
cumplimiento, siquiera mínimamente, a los recaudos de procedencia 
para la fundamentación del recurso de queja por denegación de la vía 
del art. 14 de la ley 48 (cf. acordadas 4/2007 y 38/2011).
5°) Que esta Corte tiene dicho que en materia criminal, en la que se 
encuentran en juego los derechos esenciales de la libertad y el honor,

125
DE JUSTICIA DE LA NACIÓN
342
deben extremarse los recaudos que garanticen plenamente el ejerci­
cio del derecho de defensa (Fallos: 311:2502; 320:854; 321:1424; 325:157; 
327:3087, 5095; 329:1794).
La tutela de dicha garantía ha sido preocupación del Tribunal des­
de sus orígenes, en los que señaló que el ejercicio de la defensa debe 
ser cierto, de modo tal que quien sufre un proceso penal ha de ser pro­
visto de un adecuado asesoramiento legal, al extremo de suplir su ne­
gligencia en la provisión de defensor asegurando, de este modo, la rea­
lidad sustancial de la defensa en juicio (Fallos: 5:459; 192:152; 237:158; 
255:91; 311:2502).
6°) Que, asimismo, corresponde recordar la seriedad con que ha de 
atenderse a los reclamos de quienes se encuentran privados de su li­
bertad, los cuales “más allá de los reparos formales que pudieran me­
recer, deben ser considerados como una manifestación de voluntad de 
interponer los recursos de ley” (Fallos: 314:1909, entre muchos otros).
Al respecto, no basta para cumplir con las exigencias básicas del 
debido proceso que el acusado haya tenido patrocinio letrado de ma­
nera formal, sino que es menester además que aquel haya recibido 
una efectiva y sustancial asistencia de parte de su defensor (Fallos: 
310:1934; 327:103; 331:2520).
7°) Que tal como se señaló en Fallos: 310:1797 en una materia tan 
delicada como es la que concierne a la defensa en sede penal los juzga­
dores están legalmente obligados a proveer lo necesario para que no 
se produzcan situaciones de indefensión.
8°) Que en el sub lite el defensor oficial se ha limitado a acom­
pañar un escrito que, por vía de principio, estaría destinado a ser 
descalificado ante esta instancia extraordinaria no solo por incumpli­
mientos extrínsecos, vinculados con la desatención de los requisitos 
establecidos por el art. 7° de la acordada 4/2007, sino, además, con la 
ausencia casi completa de referencias a la concreta situación pro­
cesal de su pupila y a los motivos alegados para la habilitación de la 
instancia federal en su favor.
En esas condiciones, el tribunal superior debió haber asumido con 
mayor prudencia la misión que le compete, en orden a tomar a su cargo

342
126
FALLOS DE LA CORTE SUPREMA
el aseguramiento de la efectiva tutela de la inviolabilidad de la defensa. 
Pues, de otro modo, quedaría completamente desvirtuado el sentido 
de la doctrina de este Tribunal según la cual los recursos procesales 
constituyen una facultad del imputado y no una potestad técnica del 
defensor (cf. doctrina de Fallos: 327:3802 y sus citas; 329:149; 330:4920).
Por ello, se resuelve devolver las actuaciones a la Corte Suprema 
de Justicia de Tucumán a fin de que a la mayor brevedad posible, dé 
debido cumplimiento a lo ordenado a fs. 4. Remítase copia del legajo 
al Ministerio Público de la Defensa de la Provincia de Tucumán, a 
sus efectos.
```

### [span 14] header_pagina (4990–4990)
```
342
```

### [span 15] header_pagina (4991–4991)
```
124
```

### [span 16] header_pagina (4992–4992)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 17] header_pagina (5030–5030)
```
125
```

### [span 18] header_pagina (5031–5031)
```
DE JUSTICIA DE LA NACIÓN
```

### [span 19] header_pagina (5032–5032)
```
342
```

### [span 20] header_pagina (5068–5068)
```
342
```

### [span 21] header_pagina (5069–5069)
```
126
```

### [span 22] header_pagina (5070–5070)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 23] firma (5081–5082)
```
Elena I. Highton de Nolasco — Juan Carlos Maqueda — Ricardo 
Luis Lorenzetti — Horacio Rosatti.
```

### [span 24] catch_all (5083–5089)
```
Recurso de queja deducido por María Azucena Márquez, asistida por el Dr. Hernán E. 
Molina, Defensor Oficial Penal de 5ª Nominación del Centro Judicial Capital de la 
Provincia de Tucumán.
Tribunal de origen: Corte Suprema de Justicia de la Provincia de Tucumán.
Tribunales que intervinieron con anterioridad: Juzgado de Instrucción Penal de IVa. 
Nominación; Cámara de Apelaciones en lo Penal de Instrucción; Sala II de la Cá­
mara Penal, Centro Judicial Capital.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=5089 | linea_inicio_proximo_caso=5068 | delta=-22
**Alertas**: `solapado_con_proximo`


---

## 329_p2347 — ANSeS (Lizarraga, Moisés Ciriaco c/) | Lizarraga, Moisés Ciriaco c/ ANSeS

**Localización**
- Archivo: `LibroVol329.2.md`
- Páginas catálogo: 2347–2351 | Página consultada: 2351
- Líneas catálogo: 36809–36947 | Línea fin real: 36974 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 36809–36809 | 1 |
| 2 | catch_all | 36810–36811 | 2 |
| 3 | caratula | 36812–36812 | 1 |
| 4 | cuerpo_mayoria | 36813–36821 | 9 |
| 5 | firma | 36822–36823 | 2 |
| 6 | catch_all | 36824–36835 | 12 |
| 7 | header_pagina | 36836–36836 | 1 |
| 8 | header_pagina | 36837–36837 | 1 |
| 9 | header_pagina | 36838–36838 | 1 |
| 10 | catch_all | 36839–36871 | 33 |
| 11 | header_pagina | 36872–36872 | 1 |
| 12 | header_pagina | 36873–36873 | 1 |
| 13 | header_pagina | 36874–36874 | 1 |
| 14 | catch_all | 36875–36910 | 36 |
| 15 | header_pagina | 36911–36911 | 1 |
| 16 | header_pagina | 36912–36912 | 1 |
| 17 | header_pagina | 36913–36913 | 1 |
| 18 | disidencia | 36914–36974 | 61 |
| 19 | header_pagina | 36946–36946 | 1 |
| 20 | header_pagina | 36947–36947 | 1 |
| 21 | header_pagina | 36948–36948 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=83 (50.0% del bloque, n=166)

---

### [span 1] header_pagina (36809–36809)
```
329
```

### [span 2] catch_all (36810–36811)
```
tes (Fallos: 327:90 y 1835), opino que corresponde declarar la compe-
tencia del juzgado provincial para conocer en estas actuaciones. Bue-
```

### [span 3] caratula (36812–36812)
```
nos Aires, 22 de noviembre de 2005. Luis Santiago González Warcalde.
```

### [span 4] cuerpo_mayoria (36813–36821)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 20 de junio de 2006.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que corresponde remitirse en razón de brevedad, se
declara que deberá entender en la causa en la que se originó el presen-
te incidente el Juzgado de Instrucción Formal de la Primera Nomina-
ción de la ciudad de Salta, al que se le remitirá. Hágase saber al Juz-
gado Federal Nº 1 con asiento en la mencionada ciudad.
```

### [span 5] firma (36822–36823)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — RICARDO LUIS LORENZETTI — CARMEN M. ARGIBAY.
```

### [span 6] catch_all (36824–36835)
```
MOISES CIRIACO LIZARRAGA V. ANSES
JUBILACION Y PENSION.
Corresponde revocar la sentencia que estableció la movilidad en los términos de
la ley 22.929 y ordenar el reajuste de acuerdo a las disposiciones de la ley 22.955,
con la movilidad correspondiente a dicho régimen hasta la entrada en vigencia
del sistema de la ley 24.463, pues lo resuelto prescindió de la aclaración efectua-
da por el jubilado y la constancia emitida por el INTA, que certificaba que las
labores desarrolladas eran de carácter administrativo y no de investigación.
JUBILACION Y PENSION.
Corresponde confirmar la sentencia que estableció la movilidad en los términos
de la ley 22.929 si el único agravio de la ANSeS se refiere a que la derogación de

```

### [span 7] header_pagina (36836–36836)
```
2348
```

### [span 8] header_pagina (36837–36837)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] header_pagina (36838–36838)
```
329
```

### [span 10] catch_all (36839–36871)
```
dicha norma impedía que la pretensión se efectuase de acuerdo con sus disposi-
ciones, pues el régimen jubilatorio de los investigadores científicos ha quedado
sustraído de las disposiciones que integran el sistema general de las leyes 24.241
y 24.463, con el que coexiste, manteniéndose vigente con todas sus característi-
cas, entre las que se encuentra su pauta de movilidad (Disidencia de la Dra.
Carmen M. Argibay).
FALLO DE LA CORTE SUPREMA
Buenos Aires, 20 de junio de 2006.
Vistos los autos: “Lizarraga, Moisés Ciríaco c/ ANSeS s/ reajustes
varios”.
Considerando:
1º) Que el actor solicitó y obtuvo jubilación ordinaria por los servi-
cios prestados como personal administrativo durante más de treinta
años en el Instituto Nacional de Tecnología Agropecuaria hasta el 1º
de julio de 1990. Posteriormente, en virtud de lo dispuesto por la ley
23.682 respecto de las personas que hubieran trabajado en los orga-
nismos que taxativamente enumeraba dicha norma –entre los que se
encontraba el I.N.T.A.–, reclamó que se le reajustara su prestación
según las pautas de movilidad de la ley 22.955. La ANSeS rechazó el
pedido, lo que dio lugar a que el jubilado interpusiera demanda de
conocimiento pleno.
2º) Que si bien es cierto que el titular fundó originariamente su
reclamo en las disposiciones de la ley 22.929 –régimen jubilatorio
para investigadores científicos y tecnológicos–, durante el trámite
del juicio presentó un escrito en el que manifestó que había confun-
dido su encuadramiento previsional y que la norma que correspon-
día aplicar a los fines de la recomposición de su haber era la ley 23.682.
Expresó también que su error no afectaba los términos de la deman-
da pues ambos estatutos eran especiales y contenían cláusulas de
movilidad que remitían a la retribución de la categoría en actividad
con la cual se había obtenido la jubilación (confr. fs. 49 del expedien-
te principal).

```

### [span 11] header_pagina (36872–36872)
```
2349
```

### [span 12] header_pagina (36873–36873)
```
DE JUSTICIA DE LA NACION
```

### [span 13] header_pagina (36874–36874)
```
329
```

### [span 14] catch_all (36875–36910)
```
3º) Que no obstante la aclaración efectuada por el jubilado y la
constancia de fs. 38/39 emitida por el Instituto Nacional de Tecnología
Agropecuaria –que certificaba que las labores desarrolladas eran de
carácter administrativo y no de investigación–, el juez de grado orde-
nó el reajuste de los haberes jubilatorios por aplicación de la ley 22.929.
Apelada la decisión por el organismo previsional, la cámara también
prescindió de las constancias del expediente y la confirmó, lo que dio
lugar a que la ANSeS interpusiera recurso ordinario de apelación, que
fue concedido.
4º) Que lo expresado pone en evidencia el error en que han incu-
rrido los jueces al fijar el alcance de la movilidad reclamada, pues a
contrario de lo que sucede con la ley 22.929, que se encuentra vigen-
te (conf. doctrina de este Tribunal dictada en la causa M.821.XXXIX
“Massani de Sese” (Fallos: 328:4044), la ley 22.955 ha sido dero-
gada.
5º) Que en virtud de las consideraciones que anteceden, corres-
ponde revocar las sentencias apeladas y ordenar el reajuste del ha-
ber previsional del actor de acuerdo a las disposiciones de la ley
22.955, con la movilidad correspondiente a dicho régimen hasta la
entrada en vigencia del sistema previsto en la ley 24.463, de confor-
midad con lo establecido por esta Corte en la causa “Brochetta” (Fa-
llos: 328:3975).
6º) Que el planteo acerca de la tasa de interés aplicada no guarda
relación con lo decidido por la alzada, aparte de que la tasa que pre-
tende fue la ordenada por el juez de grado, que quedó firme al no ha-
ber habido agravio sobre el punto.
Por ello, el Tribunal resuelve: Declarar procedente el recurso
ordinario interpuesto por la ANSeS, revocar las sentencias apela-
das y reajustar el haber previsional de la parte actora de acuerdo a
lo establecido en el antecedente “Brochetta” citado. Notifíquese y
devuélvase, con copias de las sentencias citadas en los considerandos
4º y 5º.
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS
S. FAYT — JUAN CARLOS MAQUEDA — RICARDO LUIS LORENZETTI — CARMEN
M. ARGIBAY (en disidencia).

```

### [span 15] header_pagina (36911–36911)
```
2350
```

### [span 16] header_pagina (36912–36912)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 17] header_pagina (36913–36913)
```
329
```

### [span 18] disidencia (36914–36974)
**Header**: DISIDENCIA DE LA SEÑORA
```
DISIDENCIA DE LA SEÑORA
MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY
Considerando:
Que la infrascripta coincide con los considerandos 1º al 2º del pro-
yecto de Secretaría.
3º) A fs. 49 el jubilado presentó un escrito con el fin de hacer saber
que “en la demanda medió un error material..., consignándose el Nº de
la ley 22.929 en vez de la ley 23.682 que le corresponde a su beneficio”.
Seguidamente expresó que “ello fue rectificado al librar el oficio de
prueba al INTA, organismo que contestó correctamente”.
Cabe apuntar, que en dicha pieza procesal se certificó que las labo-
res desarrolladas por el señor Lizarraga fueron de carácter adminis-
trativo y no de investigación (fojas 38/39).
4º) Si bien el juez de primera instancia proveyó la aclaración del
actor en los siguientes términos “Téngase presente lo manifestado”
(fojas 50), al dictar sentencia ordenó el reajuste de sus haberes
jubilatorios de conformidad con la ley 22.929 (fojas 53/55).
El organismo previsional apeló ese fallo (fojas 71/73) y su único
agravio respecto de dicha norma fue que estaba derogada.
5º) La alzada se atuvo estrictamente al planteo de la ANSeS y sin
reparar en lo obrado en el expediente, incurrió en el error de afirmar
que el beneficio del actor fue otorgado de acuerdo con el régimen de los
investigadores y científicos (ley 22.929). A continuación, rechazó que
el reajuste no pudiese efectuarse según sus términos.
6º) Contra esta decisión, el ente administrativo interpone un re-
curso ordinario de apelación, que fue concedido (fojas 85, 87, 96/98).
Reprocha a la alzada haberse apartado de las normas aplicables
en la especie, pero al igual que hizo al apelar el fallo de primera ins-
tancia, no funda esa afirmación en que la ley 22.929 resultaba ajena
al accionante sino en que estaba derogada (artículo 168 de la ley 24.241)
y por lo tanto no podía regir el caso.

2351
DE JUSTICIA DE LA NACION
329
Ninguna alusión hace al yerro en que incurrió la cámara al afir-
mar que el actor goza de un beneficio otorgado al amparo de las pres-
cripciones destinadas a los investigadores científicos y tecnológicos, ni
tampoco a que el propio jubilado reconoció que las tareas desarrolla-
das no correspondían a las comprendidas en ese ámbito, lo que ha
bloqueado la posibilidad de su revisión en esta instancia.
7º) Respecto del único agravio relativo a la ley 22.929 sometido a
consideración por esta Corte, que como ya se dijo, es que su derogación
impedía que la pretensión del accionante se efectuase de acuerdo con
sus disposiciones, cabe responder negativamente con sustento en la
doctrina dictada en la causa “Massani de Sese” (Fallos: 328:4044).
8º) Que el planteo acerca de la tasa de interés aplicada no guarda
relación con lo decidido por la alzada, aparte de que la tasa que pre-
tende fue la ordenada por el juez de grado, que quedó firme al no ha-
ber habido agravio sobre el punto.
Por ello, el Tribunal resuelve: Declarar procedente el recurso ordi-
nario interpuesto por la ANSeS y confirmar la sentencia apelada.
Notifíquese y devuélvase.
CARMEN M. ARGIBAY.
Recurso ordinario interpuesto por la Administración Nacional de la Seguridad
Social, representada por la Dra. Carolina Giudice.
Traslado contestado por Moisés Ciríaco Lizarraga, representado por el Dr. Gustavo
Francisco Sigal Escalada.
Tribunal de origen: Sala II de la Cámara Federal de la Seguridad Social.
Tribunales que intervinieron con anterioridad: Juzgado Federal de Primera Ins-
tancia de la Seguridad Social Nº 7.
```

### [span 19] header_pagina (36946–36946)
```
2351
```

### [span 20] header_pagina (36947–36947)
```
DE JUSTICIA DE LA NACION
```

### [span 21] header_pagina (36948–36948)
```
329
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=36974 | linea_inicio_proximo_caso=36948 | delta=-27
**Alertas**: `solapado_con_proximo`


---

## 329_p88 — ANSeS (Sisterna, Ramón Silvano c/) | Sisterna, Ramón Silvano c/ ANSeS

**Localización**
- Archivo: `LibroVol329.1.md`
- Páginas catálogo: 88–94 | Página consultada: 94
- Líneas catálogo: 3172–3390 | Línea fin real: 3394 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 3172–3172 | 1 |
| 2 | catch_all | 3173–3191 | 19 |
| 3 | caratula | 3192–3192 | 1 |
| 4 | sumario [1] | 3193–3202 | 10 |
| 5 | header_pagina | 3200–3200 | 1 |
| 6 | header_pagina | 3201–3201 | 1 |
| 7 | header_pagina | 3202–3202 | 1 |
| 8 | sumario [2] | 3203–3211 | 9 |
| 9 | sumario [3] | 3212–3219 | 8 |
| 10 | sumario [4] | 3220–3224 | 5 |
| 11 | dictamen | 3225–3301 | 77 |
| 12 | header_pagina | 3237–3237 | 1 |
| 13 | header_pagina | 3238–3238 | 1 |
| 14 | header_pagina | 3239–3239 | 1 |
| 15 | header_pagina | 3279–3279 | 1 |
| 16 | header_pagina | 3280–3280 | 1 |
| 17 | header_pagina | 3281–3281 | 1 |
| 18 | cuerpo_mayoria | 3302–3372 | 71 |
| 19 | header_pagina | 3314–3314 | 1 |
| 20 | header_pagina | 3315–3315 | 1 |
| 21 | header_pagina | 3316–3316 | 1 |
| 22 | header_pagina | 3355–3355 | 1 |
| 23 | header_pagina | 3356–3356 | 1 |
| 24 | header_pagina | 3357–3357 | 1 |
| 25 | firma | 3373–3374 | 2 |
| 26 | catch_all | 3375–3375 | 1 |
| 27 | disidencia | 3376–3394 | 19 |
| 28 | header_pagina | 3389–3389 | 1 |
| 29 | header_pagina | 3390–3390 | 1 |
| 30 | header_pagina | 3391–3391 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=20 (8.97% del bloque, n=223)

---

### [span 1] header_pagina (3172–3172)
```
329
```

### [span 2] catch_all (3173–3191)
```
las particulares circunstancias en que se habrían producido, formen
parte de un único propósito delictivo que deba ser analizado por un
mismo magistrado (Competencia Nº 364, L. XLI, in re “Ayala, Pedro
Gabriel s/ falsificación de documentos públicos”, resuelta el 23 de agosto
de este año), opino que corresponde atribuir competencia a la justicia
federal, sin perjuicio de lo que surja de la pesquisa. Buenos Aires, 30
de noviembre del año 2005. Luis Santiago González Warcalde.
FALLO DE LA CORTE SUPREMA
Buenos Aires, 7 de febrero de 2006.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que corresponde remitirse en razón de brevedad, se
declara que deberá entender en la causa en la que se originó el presen-
te incidente el Juzgado Nacional en lo Criminal y Correccional Fede-
ral Nº 12, al que se le remitirá. Hágase saber al Juzgado en lo
Contravencional y de Faltas Nº 7 de la Ciudad Autónoma de Buenos
Aires, provincia homónima.
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — E. RAÚL ZAFFARONI — CARMEN M. ARGIBAY.
```

### [span 3] caratula (3192–3192)
```
RAMON SILVANO SISTERNA V. ANSES
```

### [span 4] sumario [1] (3193–3202)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestión federal. Cuestiones fede-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestión federal. Cuestiones fede-
rales simples. Interpretación de las leyes federales. Leyes federales de carácter procesal.
Existe cuestión federal si se encuentra en juego la interpretación de normas pro-
cesales con incidencia directa sobre derechos adquiridos bajo la órbita de una
regulación anterior y media lesión a las garantías constitucionales invocadas
(art. 14, inc. 2º, de la ley 48).

89
DE JUSTICIA DE LA NACION
329
```

### [span 5] header_pagina (3200–3200)
```
89
```

### [span 6] header_pagina (3201–3201)
```
DE JUSTICIA DE LA NACION
```

### [span 7] header_pagina (3202–3202)
```
329
```

### [span 8] sumario [2] (3203–3211)
**Header**: PROCEDIMIENTO ADMINISTRATIVO.
**Atribución**: (sin atribución detectada)
```
PROCEDIMIENTO ADMINISTRATIVO.
Aun cuando la nueva redacción del art. 31 de la ley de procedimientos adminis-
trativos, introducida por el art. 12 de la ley 25.344, prescribe un plazo perentorio
de 90 días para deducir demanda en contra del Estado o de sus entes autárquicos,
contados a partir de la notificación al interesado del acto expreso que agote la
instancia administrativa o cuando hubiesen transcurrido 45 días del pedido de
pronto despacho (art. 25), tal exigencia no puede recaer sobre aquellos supuestos
en que el cumplimiento de los requisitos de procedencia de la acción se hubiese
configurado antes de la sanción de la nueva ley.
```

### [span 9] sumario [3] (3212–3219)
**Header**: LEYES PROCESALES.
**Atribución**: (sin atribución detectada)
```
LEYES PROCESALES.
Si bien es cierto que las leyes sobre procedimiento son de orden público y se
aplican a las causas pendientes, también lo es que su aplicación se encuentra
limitada a los supuestos en que no se prive de validez a los actos procesales
cumplidos, ni se deje sin efecto lo actuado de conformidad con las leyes anterio-
res, máxime cuando ello desbarataría una situación consolidada a favor del recu-
rrente con privación de justicia respecto de derechos de naturaleza alimentaria
que gozan de protección constitucional.
```

### [span 10] sumario [4] (3220–3224)
**Header**: RECURSO EXTRAORDINARIO: Principios generales.
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Principios generales.
El recurso extraordinario contra la sentencia que confirmó el pronunciamiento
que declaró de oficio no habilitada la instancia judicial es inadmisible (art. 280
del Código Procesal Civil y Comercial de la Nación) (Disidencia de la Dra. Car-
men M. Argibay).
```

### [span 11] dictamen (3225–3301)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
Los integrantes de la Sala III de la Cámara Federal de la Seguri-
dad Social en remisión al dictamen del Ministerio Público del fuero
confirmaron la resolución de la juez de grado que declaró de oficio no
habilitada la instancia judicial (v. fs. 25, 35/vta. y 37 del principal,
foliatura a citar, salvo indicación, en adelante).
Para así decidir, entendieron que el actor no había dado cumpli-
miento con los plazos establecidos para la plena operatividad del insti-
tuto del silencio en sede administrativa, ello en virtud de que transcu-
rrieron casi diez años entre su solicitud de reajuste y la interposición

90
FALLOS DE LA CORTE SUPREMA
329
de la demanda judicial. Asimismo, consideraron de aplicación al sub
lite las disposiciones contenidas en la ley 25.344 en cuanto modificó el
artículo 32 de la ley 19.549 y dejó sin efecto la posibilidad de obviar el
reclamo administrativo previo en aquellas situaciones donde mediara
una clara conducta del Estado que hiciera presumir la ineficacia cier-
ta del procedimiento.
Contra dicho pronunciamiento y con fundamento en la doctrina de
la arbitrariedad de fallos judiciales la actora interpuso recurso extraor-
dinario, cuya denegatoria, previo traslado de ley, motiva la presente
queja.
En relación con él, creo necesario recordar que, si bien V.E. tiene
reiteradamente dicho que a los fines del recurso extraordinario pre-
visto en el artículo 14 de la ley 48, revisten carácter de definitivas, no
sólo aquellas sentencias que ponen fin al pleito e impiden su prosecu-
ción, sino también las que causan un agravio de imposible o insufi-
ciente reparación ulterior (Fallos: 310:1045; 312:2348; 323:1084;
325:2623 entre muchos otros), considero que en el caso la resolución
que declaró no habilitada la instancia judicial es asimilable a una sen-
tencia definitiva, en cuanto clausura totalmente el acceso del actor a
la jurisdicción (Fallos: 312:1724).
Ello sentado, vale poner de resalto que la ley nacional de procedi-
mientos administrativos prevé dos vías mediante las cuales se habili-
ta la instancia judicial a efectos de accionar contra el Estado Nacional:
la denominada impugnatoria o recursiva y la llamada reparatoria o
reclamatoria. La primera de estas vías tiene por objeto la impugna-
ción de actos administrativos mediante la necesaria deducción de los
recursos administrativos que resulten procedentes, y la posterior in-
terposición de acción judicial de impugnación de conformidad con los
artículos 23 a 27 de la ley 19.549. La restante, por el contrario, exige
la promoción de reclamo administrativo previo con el objeto de cues-
tionar el accionar de la Administración que como tal no constituye un
acto administrativo, o efectuar dicho reclamo como medio de impug-
nación directa de actos de alcance general.
En el sub lite, y tal como lo reconoce el quejoso, la presentación de
fecha 17 de junio de 1992 tuvo el carácter de un reclamo administrati-
vo en los términos del artículo 30 de la ley de procedimientos adminis-
trativos, reclamo que fue iniciado a efectos de solicitar un reajuste de
su haber previsional (v. fs. 5/7). En consecuencia, y contrariamente a

91
DE JUSTICIA DE LA NACION
329
lo argumentado por el apelante, no son de aplicación a estas actuacio-
nes las disposiciones contenidas en el artículo 26 de la ley 19.549 que
presuponen el ejercicio previo de la vía impugnatoria o recursiva.
Por otra parte, estimo que no resultan arbitrarias las conclusiones
de los sentenciantes cuando afirman que la demanda judicial promo-
vida por el recurrente se encuentra comprendida dentro de lo estable-
cido por el artículo 31 de la ley 19.549, texto según ley 25.344. Ello, en
razón de que toda reforma de las leyes de procedimientos es de aplica-
ción plena e inmediata, aun cuando la situación jurídica que constitu-
ye el objeto del litigio se haya configurado y desarrollado bajo la ley
anterior. Las normas procedimentales tienen carácter de orden públi-
co por lo que no existe derecho adquirido a ser juzgado de conformidad
con un determinado procedimiento (Fallos: 211:725; 215:467; 321:1865,
entre otros). De allí que, los presupuestos de admisibilidad de la ac-
ción contencioso administrativa no puedan sino ser verificados de acuer-
do con la ley de procedimientos vigente a la fecha de promoción de la
demanda.
Por lo expuesto, soy de opinión que corresponde desestimar la pre-
sente queja. Buenos Aires, 23 de febrero de 2005. Marta A. Beiró de
Gonçalvez.
```

### [span 12] header_pagina (3237–3237)
```
90
```

### [span 13] header_pagina (3238–3238)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 14] header_pagina (3239–3239)
```
329
```

### [span 15] header_pagina (3279–3279)
```
91
```

### [span 16] header_pagina (3280–3280)
```
DE JUSTICIA DE LA NACION
```

### [span 17] header_pagina (3281–3281)
```
329
```

### [span 18] cuerpo_mayoria (3302–3372)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 7 de febrero de 2006.
Vistos los autos: “Recurso de hecho deducido por la actora en la
causa Sisterna, Ramón Silvano c/ ANSeS”, para decidir sobre su pro-
cedencia.
Considerando:
1º) Que contra el pronunciamiento de la Sala III de la Cámara
Federal de la Seguridad Social que confirmó el del juez de grado en
cuanto había declarado de oficio no habilitada la instancia judicial, el
actor dedujo recurso extraordinario cuya denegación origina la pre-
sente queja.

92
FALLOS DE LA CORTE SUPREMA
329
2º) Que el a quo sostuvo, haciendo suyos los fundamentos del se-
ñor Fiscal General, que el beneficiario de una jubilación había solici-
tado el reajuste de su haber ante la ANSeS y que solo después de casi
diez años había deducido la demanda judicial sin acreditar que hubie-
se requerido pronto despacho en sede administrativa, por lo que no se
habían cumplido los plazos legales para que tuviese plena operatividad
el instituto del silencio.
3º) Que sobre esa base resolvió que resultaban de aplicación al
caso las disposiciones del art. 12 de la ley 25.344, que eliminó la excep-
ción contemplada por el art. 32, inc. e, de la ley 19.549 y consagró al
reclamo administrativo previo como requisito sine qua non para la
procedencia de la vía judicial en razón de que dicha ley había entrado
en vigencia el día 30 de noviembre de 2000 y la demanda había sido
deducida con posterioridad a esa fecha.
4º) Que los agravios del apelante suscitan el examen de cuestiones
de naturaleza federal que autorizan la apertura de la instancia ex-
traordinaria, pues la decisión tiene el alcance de una sentencia defini-
tiva (Fallos: 324:1405), se encuentra en juego la interpretación de nor-
mas procesales con incidencia directa sobre derechos adquiridos bajo
la órbita de una regulación anterior y media lesión a las garantías
constitucionales invocadas (art. 14, inc. 2º, de la ley 48).
5º) Que aun cuando la nueva redacción del art. 31 de la ley de
procedimientos administrativos, introducida por el art. 12 de la ley
25.344, prescribe un plazo perentorio de 90 días para deducir deman-
da en contra del Estado o de sus entes autárquicos, contados a partir
de la notificación al interesado del acto expreso que agote la instancia
administrativa o cuando hubiesen transcurrido 45 días del pedido de
pronto despacho (art. 25), tal exigencia no puede recaer sobre aquellos
supuestos en que el cumplimiento de los requisitos de procedencia de
la acción se hubiese configurado antes de la sanción de la nueva ley.
6º) Que el pedido de reajuste de haberes y pago de diferencias en
sede administrativa, deducido con fecha 17 de junio de 1992 (fs. 5/7 de
la causa principal), y la posterior solicitud de pronto despacho presen-
tada el 30 de noviembre de 1994 (fs. 4), cuya existencia no fue adverti-
da en las instancias anteriores, ponen en evidencia que se encontra-
ban dadas las exigencias formales para la promoción de la demanda
judicial establecidas en los arts. 23 y 26 de la ley 19.549.

93
DE JUSTICIA DE LA NACION
329
7º) Que esta Corte ha dicho que si bien es cierto que las leyes sobre
procedimiento son de orden público y se aplican a las causas pendien-
tes, también lo es que su aplicación se encuentra limitada a los su-
puestos en que no se prive de validez a los actos procesales cumplidos,
ni se deje sin efecto lo actuado de conformidad con las leyes anteriores;
máxime cuando ello desbarataría una situación consolidada a favor
del recurrente con privación de justicia respecto de derechos de natu-
raleza alimentaria que gozan de protección constitucional (Fallos:
319:2151 y 2215).
Por ello, oída la señora Procuradora Fiscal subrogante, el Tribu-
nal resuelve: Hacer lugar a la queja, declarar procedente el recurso
extraordinario y dejar sin efecto la sentencia apelada. Devuélvanse
los autos al tribunal de origen para que, por medio de quien corres-
ponda, dicte un nuevo fallo con arreglo a lo expresado. Notifíquese,
agréguese la queja al principal y devuélvase.
```

### [span 19] header_pagina (3314–3314)
```
92
```

### [span 20] header_pagina (3315–3315)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 21] header_pagina (3316–3316)
```
329
```

### [span 22] header_pagina (3355–3355)
```
93
```

### [span 23] header_pagina (3356–3356)
```
DE JUSTICIA DE LA NACION
```

### [span 24] header_pagina (3357–3357)
```
329
```

### [span 25] firma (3373–3374)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS
S. FAYT — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI — CARMEN M.
```

### [span 26] catch_all (3375–3375)
```
ARGIBAY (en disidencia).
```

### [span 27] disidencia (3376–3394)
**Header**: DISIDENCIA DE LA SEÑORA
```
DISIDENCIA DE LA SEÑORA
MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY
Considerando:
Que el recurso extraordinario, cuya denegación origina esta queja,
es inadmisible (art. 280 del Código Procesal Civil y Comercial de la
Nación).
Por ello, y oída la señora Procuradora Fiscal subrogante, se deses-
tima la queja. Notifíquese y, previa devolución de los autos principa-
les, archívese.
CARMEN M. ARGIBAY.
Recurso de hecho interpuesto por Ramón Silvano Sisterna, representado y patroci-
nado por la Dra. Laura Ester Alalachvily.

94
FALLOS DE LA CORTE SUPREMA
329
Tribunal de origen: Sala III de la Cámara Federal de la Seguridad Social.
Tribunales que intervinieron con anterioridad: Juzgado Federal de Primera Ins-
tancia de la Seguridad Social Nº 4.
```

### [span 28] header_pagina (3389–3389)
```
94
```

### [span 29] header_pagina (3390–3390)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 30] header_pagina (3391–3391)
```
329
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=3394 | linea_inicio_proximo_caso=3391 | delta=-4
**Alertas**: `solapado_con_proximo`


---

## 343_p139 — Andino, María Cristina c/ Prevención A.R.T. S.A. s/ Procedimiento abreviado - ley 7434

**Localización**
- Archivo: `LibroVol343-1.md`
- Páginas catálogo: 139–140 | Página consultada: 140
- Líneas catálogo: 5211–5236 | Línea fin real: 5250 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 5211–5211 | 1 |
| 2 | sumario [1] | 5212–5212 | 1 |
| 3 | sumario [2] | 5213–5214 | 2 |
| 4 | sumario [3] | 5215–5220 | 6 |
| 5 | cuerpo_mayoria | 5221–5241 | 21 |
| 6 | header_pagina | 5237–5237 | 1 |
| 7 | header_pagina | 5238–5238 | 1 |
| 8 | header_pagina | 5239–5239 | 1 |
| 9 | firma | 5242–5243 | 2 |
| 10 | catch_all | 5244–5250 | 7 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=7 (17.5% del bloque, n=40)

---

### [span 1] header_pagina (5211–5211)
```
343
```

### [span 2] sumario [1] (5212–5212)
**Header**: MARZO
**Atribución**: (sin atribución detectada)
```
MARZO
```

### [span 3] sumario [2] (5213–5214)
**Header**: ANDINO, MARÍA CRISTINA c/ PREVENCIÓN A.R.T. S.A.
**Atribución**: (sin atribución detectada)
```
ANDINO, MARÍA CRISTINA c/ PREVENCIÓN A.R.T. S.A.
s/ Procedimiento abreviado - ley 7434
```

### [span 4] sumario [3] (5215–5220)
**Header**: RECURSO DE QUEJA
**Atribución**: (sin atribución detectada)
```
RECURSO DE QUEJA
La queja reglada por los arts. 285 y siguientes del Código Procesal Civil 
y Comercial de la Nación tiene por finalidad que la Corte revise la dene­
gación por los jueces de la causa de un recurso de apelación extraordi­
nario deducido por ante ellos, por lo tanto, carece de sentido cuando tal 
recurso no ha sido interpuesto.
```

### [span 5] cuerpo_mayoria (5221–5241)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 3 de marzo de 2020.
Autos y Vistos; Considerando:
Que contra el pronunciamiento del Superior Tribunal de Justicia 
de la Provincia del Chaco que desestimó el recurso extraordinario lo­
cal de inaplicabilidad de ley o doctrina legal, la demandada dedujo ante 
esta Corte el recurso de hecho que es objeto de examen.
Tal presentación resulta inadmisible pues, como ha sido señala­
do repetidamente, la queja reglada por los arts. 285 y siguientes del 
Código Procesal Civil y Comercial de la Nación tiene por finalidad 
que la Corte revise la denegación por los jueces de la causa de un 
recurso de apelación extraordinario deducido por ante ellos (doctri­
na de Fallos: 269:405; 327:3136 y 328:24, entre muchos otros), por lo 
tanto, carece de sentido cuando, como ocurre en el caso, tal recurso 
no ha sido interpuesto.

343
140
FALLOS DE LA CORTE SUPREMA
Por ello, se desestima la presentación directa. Declárase perdido 
el depósito de fs. 79. Notifíquese y, oportunamente, archívese.
```

### [span 6] header_pagina (5237–5237)
```
343
```

### [span 7] header_pagina (5238–5238)
```
140
```

### [span 8] header_pagina (5239–5239)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] firma (5242–5243)
```
Carlos Fernando Rosenkrantz — Elena I. Highton de Nolasco — 
Ricardo Luis Lorenzetti — Horacio Rosatti.
```

### [span 10] catch_all (5244–5250)
```
Recurso de queja interpuesto por Prevención ART SA, parte demandada, representa­
da por el Dr. Federico Carlos Tallone.
Tribunal de origen: Sala Primera Civil, Comercial y Laboral del Superior Tribunal 
de Justicia de la Provincia del Chaco.
Tribunales que intervinieron con anterioridad: Juzgado Laboral n° 2 Segunda Cir­
cunscripción Judicial y Sala Tercera de la Cámara de Apelaciones Civil, Comercial 
y del Trabajo de Roque Sáenz Peña, Provincia del Chaco.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=5250 | linea_inicio_proximo_caso=5237 | delta=-14
**Alertas**: `solapado_con_proximo`


---

## 330_p2265 — Kang, Yong Soo

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 2265–2268 | Página consultada: 2268
- Líneas catálogo: 35833–35937 | Línea fin real: 35949 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 35833–35833 | 1 |
| 2 | voto | 35834–35924 | 91 |
| 3 | caratula | 35854–35854 | 1 |
| 4 | sumario [1] | 35855–35858 | 4 |
| 5 | sumario [2] | 35859–35872 | 14 |
| 6 | header_pagina | 35864–35864 | 1 |
| 7 | header_pagina | 35865–35865 | 1 |
| 8 | header_pagina | 35866–35866 | 1 |
| 9 | sumario [3] | 35873–35876 | 4 |
| 10 | sumario [4] | 35877–35882 | 6 |
| 11 | header_pagina | 35899–35899 | 1 |
| 12 | header_pagina | 35900–35900 | 1 |
| 13 | header_pagina | 35901–35901 | 1 |
| 14 | disidencia | 35925–35949 | 25 |
| 15 | header_pagina | 35936–35936 | 1 |
| 16 | header_pagina | 35937–35937 | 1 |
| 17 | header_pagina | 35938–35938 | 1 |

**Invariantes**: cobertura=OK, disjunción=FALLA, líneas_residuo=0 (0.0% del bloque, n=117)

---

### [span 1] header_pagina (35833–35833)
```
330
```

### [span 2] voto (35834–35924)
**Header**: VOTO DE LA SEÑORA
```
VOTO DE LA SEÑORA
MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY
Considerando:
Que comparto, con exclusión de los párrafos 8 y 10 del acápite V,
las consideraciones expuestas por el señor Procurador Fiscal
subrogante en el dictamen de fs. 78/80 vta., a las que cabe remitir por
razones de brevedad.
Por ello, se hace lugar a la queja, se declara procedente el recurso
extraordinario y se revoca el pronunciamiento de fs. 296/299 vta. de
los autos principales. Con costas. Exímese a la recurrente de efectuar
el depósito previsto en el art. 286 del Código Procesal Civil y Comer-
cial de la Nación, cuyo pago se encuentra diferido de conformidad con
lo prescripto en la acordada 47/91. Agréguese la queja al principal.
Notifíquese y, oportunamente, devuélvase.
CARMEN M. ARGIBAY.
Recurso de hecho deducido por el Fisco Nacional, Administración Federal de In-
gresos Públicos, demandada en autos, representada por el Dr. Cristian Mario
Morasso en calidad de apoderado.
Tribunal de origen: Cámara Nacional de Apelaciones en lo Contencioso Admi-
nistrativo Federal Sala II.
YONG SOO KANG
CONSTITUCION NACIONAL: Derechos y garantías. Non bis in idem.
La regla constitucional del non bis in idem no sólo veda la aplicación de una
segunda pena por un mismo hecho sino también la exposición al riesgo de que
ello ocurra.
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y
generalidades.
El pronunciamiento que anuló la sentencia absolutoria y dispuso el reenvío de la
causa a otro tribunal oral para la realización de un nuevo juicio sin tratar el

2266
FALLOS DE LA CORTE SUPREMA
330
agravio vinculado con la violación del non bis in idem, resulta equiparable a
sentencia definitiva, pues en ese aspecto la garantía en cuestión está destinada a
gobernar decisiones previas al fallo final, ya que, llegado el momento de la sen-
tencia definitiva, aun siendo absolutoria, resultaría inoficioso examinar el agra-
vio invocado por la defensa, pues para aquel entonces “el riesgo” de ser sometido
a un nuevo juicio ya se habrá concretado.
RECURSO EXTRAORDINARIO: Requisitos propios. Tribunal superior.
La omisión del tribunal de última instancia designado por las leyes 48 o 4055 de
pronunciarse sobre la cuestión federal involucrada, constituye un obstáculo para
que la Corte Suprema pueda ejercer su competencia apelada.
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
nes anteriores a la sentencia definitiva. Varias.
El pronunciamiento que anuló la sentencia absolutoria y dispuso el reenvío de la
causa a otro tribunal oral para la realización de un nuevo juicio, no constituye
una sentencia definitiva o equiparable a tal (art. 14 de la ley 48) (Disidencia de
los Dres. Ricardo Luis Lorenzetti, Elena I. Highton de Nolasco y Carlos S. Fayt).
FALLO DE LA CORTE SUPREMA
Buenos Aires, 15 de mayo de 2007.
Vistos los autos: “Recurso de hecho deducido por la defensa de Yong
Soo Kang en la causa Kang, Yong Soo s/ causa Nº 5742”, para decidir
sobre su procedencia.
Considerando:
1º) La Sala III de la Cámara Nacional de Casación Penal, al resol-
ver de conformidad con lo solicitado por el Ministerio Público Fiscal en
su recurso, anulando la sentencia absolutoria y disponiendo el reenvío
de la causa a otro tribunal oral para la realización de un nuevo juicio,
omitió pronunciarse sobre el agravio planteado en tiempo y forma por
la defensa vinculado con la violación del non bis in idem que causaría
a esa parte una decisión como la arribada.
2º) Esta regla constitucional, no sólo veda la aplicación de una se-
gunda pena por un mismo hecho sino también “la exposición al riesgo

2267
DE JUSTICIA DE LA NACION
330
de que ello ocurra” (Fallos: 314:377; 319:43; 320:374; 321:1173, disi-
dencia de los jueces Petracchi y Bossert, 321:2826, entre otros) por lo
que la decisión recurrida resulta equiparable a definitiva, pues en ese
aspecto la garantía en cuestión está destinada a gobernar decisiones
previas al fallo final. En efecto, llegado el momento de la sentencia
definitiva, aún siendo absolutoria, resultaría inoficioso examinar el
agravio invocado por la defensa, pues para aquel entonces “el riesgo”
de ser sometido a un nuevo juicio ya se habrá concretado.
3º) Sentado ello, correspondería hacer lugar a la queja y reenviar
la causa para que el a quo trate el punto federal cuya afectación se
invoca, la omisión del tribunal de última instancia designado por las
leyes 48 o 4055 de pronunciarse sobre la cuestión federal involucrada,
constituye un obstáculo para que esta Corte Suprema pueda ejercer
su competencia apelada.
Por ello, se hace lugar a la queja, se declara procedente el recurso
extraordinario y se deja sin efecto el pronunciamiento recurrido con el
alcance indicado. Acumúlese al principal. Vuelva al tribunal de origen
para quien corresponda se dicte un nuevo fallo. Notifíquese y remí-
tase.
RICARDO LUIS LORENZETTI (en disidencia) — ELENA I. HIGHTON DE NOLASCO
(en disidencia) — CARLOS S. FAYT (en disidencia) — ENRIQUE SANTIAGO
PETRACCHI — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI — CARMEN M.
ARGIBAY.
```

### [span 3] caratula (35854–35854)
```
YONG SOO KANG
```

### [span 4] sumario [1] (35855–35858)
**Header**: CONSTITUCION NACIONAL: Derechos y garantías. Non bis in idem.
**Atribución**: (sin atribución detectada)
```
CONSTITUCION NACIONAL: Derechos y garantías. Non bis in idem.
La regla constitucional del non bis in idem no sólo veda la aplicación de una
segunda pena por un mismo hecho sino también la exposición al riesgo de que
ello ocurra.
```

### [span 5] sumario [2] (35859–35872)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y
generalidades.
El pronunciamiento que anuló la sentencia absolutoria y dispuso el reenvío de la
causa a otro tribunal oral para la realización de un nuevo juicio sin tratar el

2266
FALLOS DE LA CORTE SUPREMA
330
agravio vinculado con la violación del non bis in idem, resulta equiparable a
sentencia definitiva, pues en ese aspecto la garantía en cuestión está destinada a
gobernar decisiones previas al fallo final, ya que, llegado el momento de la sen-
tencia definitiva, aun siendo absolutoria, resultaría inoficioso examinar el agra-
vio invocado por la defensa, pues para aquel entonces “el riesgo” de ser sometido
a un nuevo juicio ya se habrá concretado.
```

### [span 6] header_pagina (35864–35864)
```
2266
```

### [span 7] header_pagina (35865–35865)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 8] header_pagina (35866–35866)
```
330
```

### [span 9] sumario [3] (35873–35876)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Tribunal superior.
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Tribunal superior.
La omisión del tribunal de última instancia designado por las leyes 48 o 4055 de
pronunciarse sobre la cuestión federal involucrada, constituye un obstáculo para
que la Corte Suprema pueda ejercer su competencia apelada.
```

### [span 10] sumario [4] (35877–35882)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
nes anteriores a la sentencia definitiva. Varias.
El pronunciamiento que anuló la sentencia absolutoria y dispuso el reenvío de la
causa a otro tribunal oral para la realización de un nuevo juicio, no constituye
una sentencia definitiva o equiparable a tal (art. 14 de la ley 48) (Disidencia de
los Dres. Ricardo Luis Lorenzetti, Elena I. Highton de Nolasco y Carlos S. Fayt).
```

### [span 11] header_pagina (35899–35899)
```
2267
```

### [span 12] header_pagina (35900–35900)
```
DE JUSTICIA DE LA NACION
```

### [span 13] header_pagina (35901–35901)
```
330
```

### [span 14] disidencia (35925–35949)
**Header**: DISIDENCIA DEL SEÑOR PRESIDENTE DOCTOR
```
DISIDENCIA DEL SEÑOR PRESIDENTE DOCTOR
DON RICARDO LUIS LORENZETTI, DE LA SEÑORA VICEPRESIDENTA
DOCTORA DOÑA ELENA I. HIGHTON DE NOLASCO Y DEL
SEÑOR MINISTRO DOCTOR DON CARLOS S. FAYT
Considerando:
Que el recurso extraordinario, cuya denegación dio origen a esta
queja, no se dirige contra una sentencia definitiva o equiparable a tal
(art. 14 de la ley 48).
Por ello, se desestima la queja. Intímese al recurrente a que, den-
tro del quinto día, efectúe el depósito que dispone el art. 286 del Códi-

2268
FALLOS DE LA CORTE SUPREMA
330
go Procesal Civil y Comercial de la Nación, en el Banco de la Ciudad
de Buenos Aires, a la orden de esta Corte y bajo apercibimiento de
ejecución. Hágase saber y, previa devolución de los autos principales,
archívese.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT.
Recurso de hecho interpuesto por Yong Soo Kang, representado por el Dr. Miguel A.
Sarrabayrouse Bargallo.
Tribunal de origen: Cámara Nacional de Casación Penal, Sala III.
Tribunales que intervinieron con anterioridad: Tribunal Oral en lo Criminal Fede-
ral de San Luis.
```

### [span 15] header_pagina (35936–35936)
```
2268
```

### [span 16] header_pagina (35937–35937)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 17] header_pagina (35938–35938)
```
330
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=35949 | linea_inicio_proximo_caso=35938 | delta=-12
**Alertas**: `solapado_con_proximo`


---

## 330_p1820 — Del Val, Rodolfo A.

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 1820–1823 | Página consultada: 1823
- Líneas catálogo: 18899–19011 | Línea fin real: 19025 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 18899–18899 | 1 |
| 2 | catch_all | 18900–18916 | 17 |
| 3 | caratula | 18917–18917 | 1 |
| 4 | sumario [1] | 18918–18926 | 9 |
| 5 | sumario [2] | 18927–18937 | 11 |
| 6 | header_pagina | 18932–18932 | 1 |
| 7 | header_pagina | 18933–18933 | 1 |
| 8 | header_pagina | 18934–18934 | 1 |
| 9 | sumario [3] | 18938–18944 | 7 |
| 10 | dictamen | 18945–19014 | 70 |
| 11 | header_pagina | 18969–18969 | 1 |
| 12 | header_pagina | 18970–18970 | 1 |
| 13 | header_pagina | 18971–18971 | 1 |
| 14 | header_pagina | 19010–19010 | 1 |
| 15 | header_pagina | 19011–19011 | 1 |
| 16 | header_pagina | 19012–19012 | 1 |
| 17 | cuerpo_mayoria | 19015–19023 | 9 |
| 18 | firma | 19024–19025 | 2 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=17 (13.39% del bloque, n=127)

---

### [span 1] header_pagina (18899–18899)
```
330
```

### [span 2] catch_all (18900–18916)
```
correspondiente control de legalidad que le permitiría afrontar la deu-
da en el marco de la normativa invocada.
8º) Que las deficiencias y falencias apuntadas, impiden concluir
que se esté frente a una forma de pago a la que se le puedan reconocer
los efectos que, con relación a las obligaciones de los estados y en de-
terminadas condiciones, le ha atribuido el excepcional régimen esta-
blecido por la ley 23.982 (Fallos: 322:1050; 323:1187 y 327:1827, ya
citado).
Por ello, se resuelve: Rechazar el planteo formulado a fs. 174/175
por la Provincia de Santiago del Estero, con costas (arts. 68 y 69, Códi-
go Procesal Civil y Comercial de la Nación). Notifíquese.
ELENA I. HIGHTON DE NOLASCO — CARLOS S. FAYT — ENRIQUE SANTIAGO
PETRACCHI — JUAN CARLOS MAQUEDA.
Partes en la cuestión a resolver: 1) Doctor Ricardo Tomás Druetta, letrado en
causa propia.
2) Provincia de Santiago del Estero, representada por la doctora Sara Delia del
Valle Fauze.
```

### [span 3] caratula (18917–18917)
```
RODOLFO A. DEL VAL
```

### [span 4] sumario [1] (18918–18926)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Inhibitoria: plantea-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Inhibitoria: plantea-
miento y trámite.
La ausencia de constancias relativas a la necesaria investigación que debe prece-
der a toda cuestión de competencia, obsta a la posibilidad de encuadrar los he-
chos prima facie en alguna figura determinada con el grado de certeza que esta
etapa procesal requiere y de llegar a un criterio cierto acerca del lugar donde
fueron cometidos, para finalmente discernir el tribunal al que corresponde in-
vestigarlos.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] sumario [2] (18927–18937)
**Header**: JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
nes penales. Delitos en particular. Falsificación de documentos.
La validez extrínseca del testamento declarada en sede civil no constituye un
elemento, de por sí, que permita establecer su legitimidad, no habiéndose efec-

1821
DE JUSTICIA DE LA NACION
330
tuado ninguna diligencia de investigación que permita corroborar mínimamente
su procedencia y validez.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 6] header_pagina (18932–18932)
```
1821
```

### [span 7] header_pagina (18933–18933)
```
DE JUSTICIA DE LA NACION
```

### [span 8] header_pagina (18934–18934)
```
330
```

### [span 9] sumario [3] (18938–18944)
**Header**: JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
nes penales. Delitos en particular. Falsificación de documentos.
Si no puede descartarse aún que el hecho materia de investigación hubiere afec-
tado a la administración de justicia de la Nación, en los supuestos en que se
desconoce el lugar de creación del documento falso debe estarse al lugar donde
fue utilizado.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 10] dictamen (18945–19014)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
La presente contienda negativa de competencia suscitada entre
los titulares del Juzgado Nacional en lo Criminal de Instrucción Nº 39
y del Juzgado de Instrucción Nº 3 de Corrientes, provincia homónima,
se refiere a la causa en la que se investiga la denuncia formulada por
Rodolfo del Val, en representación de Remigio Alvarez.
Refirió que su poderdante adquirió una vivienda, ubicada en esta
capital, a Fernando Esteban Paolinelli, para lo cual suscribieron un
boleto de compra-venta y en el mismo acto el vendedor le otorgó poder
especial irrevocable para la escrituración. Años después, y en momen-
tos en que se aprestaba a efectuar dicha formalidad, tomó conocimien-
to que ante los tribunales de esta ciudad tramitaba un proceso suceso-
rio respecto de los bienes del nombrado y que el testamento que dio
origen a esas actuaciones sería falso.
El juez nacional, de conformidad con lo dictaminado por el repre-
sentante de este Ministerio Público, declinó su competencia en favor
de los tribunales con jurisdicción sobre el lugar donde se efectuó el
acto de última voluntad. Más allá de considerar que en los hechos
materia de investigación no se habría configurado una defraudación
en tanto la suscripción de un boleto de compra-venta constituye, en
materia de inmuebles, una promesa y no venta, que debe estimarse
consumada sólo con la suscripción de la correspondiente escritura pú-

1822
FALLOS DE LA CORTE SUPREMA
330
blica, ponderó que el testamento debe presumirse otorgado en el lugar
de celebración de la escritura pública (fs. 19/20).
El magistrado local, por su parte, no aceptó el planteo por prema-
turo al considerar que las severas anomalías que presenta el docu-
mento cuestionado, referidas por el denunciante, no permiten afirmar
que hubiere sido creado en su jurisdicción, ni descartar que los hechos
denunciados tuvieran como fin estafar procesalmente al juez de esta
ciudad. En este sentido valoró la realización del testamento a más de
mil kilómetros de distancia del lugar donde se domicilian el testador y
el testado (fs. 21).
Con la insistencia del tribunal de origen y la elevación del inciden-
te a la Corte, quedó trabada la contienda (fs. 22/23).
A mi modo de ver, la ausencia de constancias relativas a la necesa-
ria investigación que debe preceder a toda cuestión de competencia,
obsta a la posibilidad de encuadrar los hechos prima facie en alguna
figura determinada con el grado de certeza que esta etapa procesal
requiere y de llegar a un criterio cierto acerca del lugar donde fueron
cometidos, para finalmente discernir el tribunal al que corresponde
investigarlos (Fallos: 308:275; 318:1001 y 324:2331).
En efecto y en mi opinión, la validez extrínseca del testamento
declarada en sede civil no constituye un elemento, de por sí, que per-
mita establecer su legitimidad, no habiéndose efectuado ninguna dili-
gencia de investigación que permita corroborar mínimamente su pro-
cedencia y validez (Fallos: 323:2345).
Por lo expuesto, en atención a que no podría descartarse aún que
el hecho materia de investigación hubiere afectado a la administra-
ción de justicia de la Nación (Fallos: 249:579; 306:1712; 322:2669 y
Competencia Nº 115, L. XLII, in re “Díaz, Nora Cristina s/ estafa”
–Fallos: 329:5683–, resuelta el 12 de diciembre del año pasado) y que
V.E. tiene decidido que en los supuestos como el de autos en que se
desconoce el lugar de creación del documento falso debe estarse al lu-
gar donde fue utilizado (Fallos: 313:942 y 315:1698), opino que corres-
ponde al magistrado nacional que previno asumir su jurisdicción e
incorporar al proceso los elementos de juicio necesarios a fin de confe-
rir precisión a la notitia criminis y resolver, luego, con arreglo a lo que
resulte de ese trámite (Fallos: 323:1808; 325:265, y Competencia
Nº 464, L. XXXIX in re “Fernández, Susana s/ defraudación por reten-

1823
DE JUSTICIA DE LA NACION
330
ción indebida” resuelta el 8 de septiembre de 2003). Buenos Aires, 28
de febrero del año 2007. Luis Santiago González Warcalde.
```

### [span 11] header_pagina (18969–18969)
```
1822
```

### [span 12] header_pagina (18970–18970)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 13] header_pagina (18971–18971)
```
330
```

### [span 14] header_pagina (19010–19010)
```
1823
```

### [span 15] header_pagina (19011–19011)
```
DE JUSTICIA DE LA NACION
```

### [span 16] header_pagina (19012–19012)
```
330
```

### [span 17] cuerpo_mayoria (19015–19023)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 17 de abril de 2007.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que corresponde remitirse en razón de brevedad, se
declara que deberá entender en la causa en la que se originó el presen-
te incidente el Juzgado Nacional en lo Criminal de Instrucción Nº 39,
al que se le remitirá. Hágase saber al Juzgado de Instrucción Nº 3 de
la ciudad de Corrientes, provincia homónima.
```

### [span 18] firma (19024–19025)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — ENRIQUE
SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=19025 | linea_inicio_proximo_caso=19012 | delta=-14
**Alertas**: `solapado_con_proximo`


---

## 330_p1807 — Banco de la Nación Argentina c/ Provincia de Córdoba | Provincia de Córdoba (Banco de la Nación Argentina c/)

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 1807–1814 | Página consultada: 1814
- Líneas catálogo: 18416–18675 | Línea fin real: 18701 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 18416–18416 | 1 |
| 2 | catch_all | 18417–18427 | 11 |
| 3 | caratula | 18428–18428 | 1 |
| 4 | sumario [1] | 18429–18436 | 8 |
| 5 | sumario [2] | 18437–18448 | 12 |
| 6 | header_pagina | 18446–18446 | 1 |
| 7 | header_pagina | 18447–18447 | 1 |
| 8 | header_pagina | 18448–18448 | 1 |
| 9 | sumario [3] | 18449–18456 | 8 |
| 10 | sumario [4] | 18457–18465 | 9 |
| 11 | sumario [5] | 18466–18472 | 7 |
| 12 | dictamen | 18473–18539 | 67 |
| 13 | header_pagina | 18481–18481 | 1 |
| 14 | header_pagina | 18482–18482 | 1 |
| 15 | header_pagina | 18483–18483 | 1 |
| 16 | header_pagina | 18519–18519 | 1 |
| 17 | header_pagina | 18520–18520 | 1 |
| 18 | header_pagina | 18521–18521 | 1 |
| 19 | cuerpo_mayoria | 18540–18696 | 157 |
| 20 | header_pagina | 18554–18554 | 1 |
| 21 | header_pagina | 18555–18555 | 1 |
| 22 | header_pagina | 18556–18556 | 1 |
| 23 | header_pagina | 18594–18594 | 1 |
| 24 | header_pagina | 18595–18595 | 1 |
| 25 | header_pagina | 18596–18596 | 1 |
| 26 | header_pagina | 18634–18634 | 1 |
| 27 | header_pagina | 18635–18635 | 1 |
| 28 | header_pagina | 18636–18636 | 1 |
| 29 | header_pagina | 18674–18674 | 1 |
| 30 | header_pagina | 18675–18675 | 1 |
| 31 | header_pagina | 18676–18676 | 1 |
| 32 | firma | 18697–18698 | 2 |
| 33 | catch_all | 18699–18701 | 3 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=14 (4.9% del bloque, n=286)

---

### [span 1] header_pagina (18416–18416)
```
330
```

### [span 2] catch_all (18417–18427)
```
Considerando:
Que, esta Corte comparte y hace suyos los fundamentos y conclu-
siones del señor Procurador General a fs. 44, párrafos primero, segun-
do y tercero, a cuyos términos se remite en razón de brevedad.
Por ello, se resuelve desestimar la denuncia realizada por Edgar
Omar Clementi y Edgar Gustavo Clementi contra las autoridades de
la Embajada de la Federación de Rusia –art. 195 Código Procesal Pe-
nal de la Nación–. Hágase saber, cúmplase y archívese.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA — E.
RAÚL ZAFFARONI — CARMEN M. ARGIBAY.
```

### [span 3] caratula (18428–18428)
```
BANCO DE LA NACION ARGENTINA V. PROVINCIA DE CORDOBA
```

### [span 4] sumario [1] (18429–18436)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Competencia originaria de
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Competencia federal. Competencia originaria de
la Corte Suprema. Causas en que es parte una provincia. Generalidades.
Cuando es parte el Estado Nacional, o una entidad autárquica o descentralizada
del Estado Nacional, y una provincia, la única forma de conciliar lo preceptuado
por el art. 117 de la Constitución Nacional respecto de los Estados provinciales,
con la prerrogativa jurisdiccional que le asiste a la Nación y a sus entes al fuero
federal, sobre la base de lo dispuesto por el art. 116 de la Ley Fundamental, es
sustanciando la acción en la instancia originaria de la Corte Suprema.
```

### [span 5] sumario [2] (18437–18448)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Entidades
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Entidades
autárquicas nacionales.
De acuerdo con lo dispuesto por el art. 27 de la ley 21.799, la entidad bancaria,
en su calidad de parte actora, tiene la posibilidad de optar entre la jurisdicción
local o la federal para promover sus acciones, pero ello no excluye a la jurisdic-
ción federal, ya que ese derecho no ha sido establecido según el beneficiario sea
actor o demandado en un juicio, sino en virtud del reconocimiento que la ley le
otorga sobre la base de determinada cualidad personal.

1808
FALLOS DE LA CORTE SUPREMA
330
```

### [span 6] header_pagina (18446–18446)
```
1808
```

### [span 7] header_pagina (18447–18447)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 8] header_pagina (18448–18448)
```
330
```

### [span 9] sumario [3] (18449–18456)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Generali-
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Generali-
dades.
La competencia federal en razón de la persona es un derecho implícito dentro
del contenido del derecho a la jurisdicción, y otorga la posibilidad de ejercerlo
ante los tribunales federales en función de ciertas calidades personales o
institucionales, en las que no cabe hacer distinciones ni en cuanto a la materia
del pleito, ni a la posición procesal que asume la parte con derecho al fuero fede-
ral.
```

### [span 10] sumario [4] (18457–18465)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Generali-
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Generali-
dades.
Las personas en cuyo beneficio y garantía ha sido establecida la competencia
federal pueden renunciar a ese derecho, y será en estas situaciones de prorro-
gabilidad cuando surge la jurisdicción concurrente. En el supuesto en que la per-
sona que tiene derecho a la justicia federal sea demandada ante jueces locales,
podrá consentir dicha jurisdicción y contestar demanda sin oponer excepciones,
pero, por el contrario, no podrá en ningún caso renunciar la jurisdicción federal
cuando ha sido demandado ante los tribunales federales.
```

### [span 11] sumario [5] (18466–18472)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Entidades
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Entidades
autárquicas nacionales.
Debe prevalecer la actuación ante la justicia federal pues, en principio, corres-
ponde a ésta y no a la justicia provincial entender en las causas en que la Nación
o uno de sus organismos autárquicos sea parte, máxime en las que pudiera deri-
var un perjuicio al patrimonio del Banco de la Nación Argentina, de acuerdo al
art. 116 de la Constitución Nacional y a lo dispuesto por el art. 27 de la ley 21.799.
```

### [span 12] dictamen (18473–18539)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
V.E. corre nuevamente vista a este Ministerio Público, a fs. 90,
con motivo de la excepción de incompetencia articulada por la Provin-
cia demandada (v. fs. 70/81), de la cual el actor solicita su rechazo (v.
fs. 87/89).

1809
DE JUSTICIA DE LA NACION
330
– II –
Quien opone la excepción sostiene que la Corte es incompetente
para entender en este proceso en el que el Banco de la Nación Argen-
tina demanda a la Provincia de Córdoba a fin de obtener que se revo-
quen resoluciones de la Dirección de Policía Fiscal, que le ordenan el
pago de una suma de dinero en concepto de diferencias por “Impuestos
de Sellos”, puesto que no se presentan los requisitos exigidos por los
arts. 116 y 117 de la Constitución Nacional para que el Tribunal inter-
venga en instancia originaria.
Apoya su defensa en que la materia debatida en el pleito se rige
por normas de derecho público local, de lo que se deduce que la cues-
tión debe ventilarse ante los tribunales provinciales.
Además, agrega que conforme a lo estipulado por el art. 27 de la
ley nacional 21.799 (Carta Orgánica del Banco de la Nación Argenti-
na), “El Banco como entidad del Estado Nacional está sometido exclu-
sivamente a la jurisdicción federal. Cuando sea actor en juicio, la com-
petencia federal será concurrente con la justicia ordinaria de las pro-
vincias y la competencia nacional federal en lo civil y comercial de la
Capital Federal con la de la justicia nacional común”. En consecuen-
cia, concluye en que en el sub lite no resulta aplicable el primer párra-
fo de dicho artículo, correspondiendo la intervención de la justicia lo-
cal.
A fs. 87/89, el actor contesta la excepción e insiste en sostener que
el litigio corresponde a la competencia originaria del Tribunal en ra-
zón de que una entidad nacional demanda a una Provincia y funda su
postura en precedentes de la Corte.
Afirma asimismo que el pago cuya repetición pretende que fue efec-
tuado bajo protesto y con reserva de acudir ante la Corte en cumpli-
miento de la intimación contenida en la resolución cuestionada, no se
encuentra pendiente de recurso alguno en el orden local.
– III –
A mi modo de ver, los fundamentos expuestos por la Provincia de
Córdoba contra la tramitación del proceso en esta instancia no logran
variar lo expuesto por este Ministerio Público en su dictamen de fs. 39,

1810
FALLOS DE LA CORTE SUPREMA
330
en el que sostiene que por la naturaleza de las partes que intervienen
la causa corresponde a la instancia originaria de la Corte ratione
personae (v. doctrina de Fallos: 325:413 y 2363; 326:973 y 2448).
En efecto, ello es así, puesto que el Banco de la Nación Argentina
ejerció, como actor, la opción de litigar ante la justicia federal –en el
caso la Corte Suprema– al interponer la demanda ante V.E.
Al respecto, cabe recordar que la competencia originaria de la Cor-
te por provenir de la Constitución Nacional no es susceptible de ser
ampliada ni restringida por normas legales o reglamentarias (v. doc-
trina de Fallos: 315:1892; 318:1361), por lo cual no resulta aplicable
en autos el art. 27 de la Carta Orgánica del Banco Nación ut supra
citado como pretende la demandada, ya que se trata de un pleito in-
terpuesto contra una Provincia, resultando sólo aplicable el art. 117
de la C. N.
En tales condiciones, opino que corresponde rechazar la defensa
opuesta por la Provincia y declarar que los autos deben continuar su
trámite ante los estrados del Tribunal. Buenos Aires, 7 de septiembre
de 2006. Laura M. Monti.
```

### [span 13] header_pagina (18481–18481)
```
1809
```

### [span 14] header_pagina (18482–18482)
```
DE JUSTICIA DE LA NACION
```

### [span 15] header_pagina (18483–18483)
```
330
```

### [span 16] header_pagina (18519–18519)
```
1810
```

### [span 17] header_pagina (18520–18520)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 18] header_pagina (18521–18521)
```
330
```

### [span 19] cuerpo_mayoria (18540–18696)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 17 de abril de 2007.
Autos y Vistos; Considerando:
1º) Que a fs. 16/26 se presenta el Banco de la Nación Argentina y
promueve demanda contra la Provincia de Córdoba a fin de que se
revoque la resolución administrativa F 009/2004 dictada por la Direc-
ción de Rentas provincial –confirmada por la resolución PFD 039/2005–,
por la que se dispuso aprobar la determinación impositiva practicada
a la referida entidad bancaria, declarándola obligada al pago de la
deuda allí determinada, como así también al pago de recargos re-
sarcitorios, multas y sellado de actuación postal.
2º) Que a fs. 27, párrafo segundo, se ordenó correr vista de las pre-
sentes actuaciones a la Procuración General de la Nación, a fin de que

1811
DE JUSTICIA DE LA NACION
330
dictamine acerca de la competencia de esta Corte para entender en la
presente causa.
3º) Que el señor Procurador Fiscal subrogante, en su dictamen de
fs. 39/39 vta., consideró que la causa debía tramitar en la instancia
originaria del Tribunal, razón por la cual se ordenó correr traslado de
la demanda interpuesta a la Provincia de Córdoba, por el término de
sesenta días.
4º) Que a fs. 70/81 la demandada opuso excepción de incompeten-
cia, y contestó la demanda en subsidio solicitando el rechazo de la
acción iniciada, con expresa imposición de costas.
5º) Que para fundar la excepción referida, la provincia sostuvo que
la competencia originaria de la Corte establecida en el art. 117 de la
Constitución Nacional sólo procede en virtud de la persona, si a la
distinta vecindad de la otra parte se une el carácter civil de la materia
en debate, de conformidad con lo dispuesto en el art. 24, inc. 1º, del
decreto-ley 1285/58. En ese sentido, citando jurisprudencia del Tribu-
nal, afirmó la excepcionante que la causa debería radicarse en sede
provincial, por no existir cuestión constitucional alguna, ni verificarse
el requisito supra indicado de “causa civil”. Ello –así lo sostuvo– dado
que la cuestión en estudio se refiere a temas de derecho público pro-
vincial, que, a su entender, serían ajenos a esta instancia judicial.
6º) Que asimismo expuso –a fin de fundar la excepción referida–
que la presente causa no puede ser analizada en esta instancia, toda
vez que la parte actora recurre a normas locales en su escrito inicial,
extremo que determina que deba ser la justicia ordinaria provincial la
que entienda en el caso. En ese sentido argumentó que los actos lleva-
dos a cabo por las provincias como entidades de derecho público, no
pueden ser revisados por vía de la jurisdicción originaria de esta Cor-
te, aun cuando se invoquen disposiciones de la Constitución Nacional,
si simultáneamente se aducen normas locales.
7º) Que, finalmente, la demandada arguyó que, tal como se des-
prendería del art. 27 de la ley 21.799, el Banco de la Nación Argentina
estaría sometido en forma exclusiva a la jurisdicción federal siempre y
cuando actúe en juicio como demandado, ya que para el caso de que
asuma la posición de actor en el proceso, la competencia federal será
concurrente con la justicia ordinaria de las provincias, y la competen-

1812
FALLOS DE LA CORTE SUPREMA
330
cia nacional federal en lo civil y comercial de la Capital Federal con la
de la justicia nacional común.
En tales condiciones, entendió que al revestir la entidad bancaria
el carácter de parte actora en las presentes actuaciones, debe some-
terse a la justicia local de la provincia demandada.
8º) Que a fs. 87/89, en oportunidad de contestar el traslado oportu-
namente conferido, la parte actora solicitó el rechazo de la excepción
de incompetencia con fundamento en el dictamen del señor Procura-
dor Fiscal obrante a fs. 39/39 vta. Argumentó al efecto que al tratarse
de una demanda deducida por un ente autárquico del Estado Nacio-
nal dirigida contra una provincia, y con fundamento directo en dispo-
siciones de la Ley Fundamental, la competencia originaria del Tribu-
nal establecida en los arts. 116 y 117 de la Carta Magna no sería sus-
ceptible de restringirse o modificarse por normas legales o reglamen-
tarias.
9º) Que finalmente afirmó que en casos como el presente, el argu-
mento de la demandada respecto a la materia sobre la que versa la
cuestión de fondo no resultaría determinante, toda vez que las presen-
tes actuaciones corresponderían a la competencia originaria de esta
Corte ratione personae. Ello, dado que esta instancia sería la única
forma de conciliar lo preceptuado por el art. 117 de la Constitución
Nacional respecto a las provincias, con la prerrogativa jurisdiccional
que le asiste a la Nación al fuero federal, sobre la base de lo dispuesto
en el art. 116 de la Ley Fundamental.
10) Que corrida una nueva vista a la Procuración General de la
Nación, a fs. 91/92 la señora Procuradora Fiscal opina que correspon-
de rechazar la defensa opuesta por la provincia y declarar que los au-
tos deben continuar tramitando ante los estrados del Tribunal.
11) Que corresponde señalar que esta causa es de la competencia
originaria prevista en el art. 117 de la Constitución Nacional. En efec-
to, como lo ha sostenido este Tribunal en reiteradas oportunidades,
cuando es parte el Estado Nacional, o una entidad autárquica o des-
centralizada del Estado Nacional, y una provincia, la única forma de
conciliar lo preceptuado por el art. 117 de la Constitución Nacional
respecto de los Estados provinciales, con la prerrogativa jurisdiccional
que le asiste a la Nación y a sus entes al fuero federal, sobre la base de

1813
DE JUSTICIA DE LA NACION
330
lo dispuesto por el art. 116 de la Ley Fundamental, es sustanciando la
acción en la instancia originaria de la Corte Suprema (Fallos: 308:2054;
311:489 y 2725; 314:830; 315:1232; 317:746; 322:190; 323:702, entre
muchos otros).
12) Que sin perjuicio de ello, resulta necesario examinar el alcance
del art. 27 de la ley 21.799, en el que la provincia demandada sustenta
la excepción de incompetencia interpuesta.
13) Que la norma citada establece que el Banco, como entidad del
Estado Nacional, está sometido exclusivamente a la jurisdicción fede-
ral, y que cuando sea actor en juicio la competencia federal será concu-
rrente con la justicia ordinaria de las provincias, y la competencia
nacional federal en lo civil y comercial de la Capital Federal con la de
la justicia nacional común.
14) Que ello implica que la entidad bancaria, en su calidad de par-
te actora, tiene la posibilidad de optar entre la jurisdicción local o la
federal para promover sus acciones (Fallos: 327:1329), pero ello no
excluye a la jurisdicción federal como lo entiende la demandada, ya
que ese derecho no ha sido establecido según el beneficiario sea actor o
demandado en un juicio, sino en virtud del reconocimiento que la ley
le otorga sobre la base de determinada cualidad personal. Ninguna
razón existe para atribuirle a la disposición en examen el carácter
limitativo que pretende la provincia.
La competencia federal en razón de la persona es un derecho im-
plícito dentro del contenido del derecho a la jurisdicción, y otorga la
posibilidad de ejercerlo ante los tribunales federales en función de cier-
tas calidades personales o institucionales (arg. Fallos: 323:2893), en
las que no cabe hacer distinciones ni en cuanto a la materia del pleito,
ni a la posición procesal que asume la parte con derecho al fuero fede-
ral.
15) Que de este modo, aquellas personas en cuyo beneficio y ga-
rantía ha sido establecida la competencia federal –el Banco en el caso–
pueden renunciar a ese derecho, y será en estas situaciones de pro-
rrogabilidad cuando surge la jurisdicción concurrente.
En el supuesto en que la persona que tiene derecho a la justicia
federal sea demandada ante jueces locales, podrá consentir dicha ju-
risdicción y contestar demanda sin oponer excepciones, pero, por el

1814
FALLOS DE LA CORTE SUPREMA
330
contrario, no podrá en ningún caso renunciar la jurisdicción federal
cuando ha sido demandado ante los tribunales federales.
16) Que en las presentes actuaciones el Banco de la Nación Argen-
tina ha hecho uso del derecho de opción que le otorga el art. 27 de la
ley 21.799, y se presentó ante el fuero federal –esta Corte– para intro-
ducir la pretensión por ella esgrimida, renunciando de esa manera al
derecho de interponer la demanda ante los jueces locales.
17) Que, finalmente, cabe concluir también que debe prevalecer la
actuación ante la justicia federal –en el caso esta Corte Suprema–,
pues, en principio, corresponde a ésta y no a la justicia provincial en-
tender en las causas en que la Nación o uno de sus organismos
autárquicos sea parte, máxime en las que, como la presente, pudiera
derivar un perjuicio al patrimonio del Banco de la Nación Argentina
(Fallos:307:1831; 319:923; entre otros), de acuerdo al art. 116 de la
Constitución Nacional y a lo dispuesto por el art. 27 de la ley 21.799.
Por ello, y de conformidad con lo dictaminado por la señora Procu-
radora Fiscal, se resuelve: Rechazar la excepción de incompetencia
planteada. Con costas (arts. 68 y 69, Código Procesal Civil y Comer-
cial de la Nación). Notifíquese y comuníquese al señor Procurador
General.
```

### [span 20] header_pagina (18554–18554)
```
1811
```

### [span 21] header_pagina (18555–18555)
```
DE JUSTICIA DE LA NACION
```

### [span 22] header_pagina (18556–18556)
```
330
```

### [span 23] header_pagina (18594–18594)
```
1812
```

### [span 24] header_pagina (18595–18595)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 25] header_pagina (18596–18596)
```
330
```

### [span 26] header_pagina (18634–18634)
```
1813
```

### [span 27] header_pagina (18635–18635)
```
DE JUSTICIA DE LA NACION
```

### [span 28] header_pagina (18636–18636)
```
330
```

### [span 29] header_pagina (18674–18674)
```
1814
```

### [span 30] header_pagina (18675–18675)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 31] header_pagina (18676–18676)
```
330
```

### [span 32] firma (18697–18698)
```
ELENA I. HIGHTON DE NOLASCO — CARLOS S. FAYT — ENRIQUE SANTIAGO
PETRACCHI — JUAN CARLOS MAQUEDA.
```

### [span 33] catch_all (18699–18701)
```
Demanda interpuesta por: Carla Silvina Rodríguez y Juan Carlos Paladino (Ban-
co de la Nación Argentina), Claudio Martín Viale y Elea Peliche (Provincia de
Córdoba).
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=18701 | linea_inicio_proximo_caso=18676 | delta=-26
**Alertas**: `solapado_con_proximo`


---

## 329_p2684 — Antonio Barillari S.A. c/ Provincia de Buenos Aires | Provincia de Buenos Aires (Antonio Barillari S.A. c/)

**Localización**
- Archivo: `LibroVol329.2.md`
- Páginas catálogo: 2684–2688 | Página consultada: 2688
- Líneas catálogo: 49573–49724 | Línea fin real: 49748 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 49573–49573 | 1 |
| 2 | caratula | 49574–49574 | 1 |
| 3 | sumario [1] | 49575–49585 | 11 |
| 4 | sumario [2] | 49586–49590 | 5 |
| 5 | sumario [3] | 49591–49597 | 7 |
| 6 | dictamen | 49598–49675 | 78 |
| 7 | header_pagina | 49608–49608 | 1 |
| 8 | header_pagina | 49609–49609 | 1 |
| 9 | header_pagina | 49610–49610 | 1 |
| 10 | header_pagina | 49646–49646 | 1 |
| 11 | header_pagina | 49647–49647 | 1 |
| 12 | header_pagina | 49648–49648 | 1 |
| 13 | cuerpo_mayoria | 49676–49745 | 70 |
| 14 | header_pagina | 49682–49682 | 1 |
| 15 | header_pagina | 49683–49683 | 1 |
| 16 | header_pagina | 49684–49684 | 1 |
| 17 | header_pagina | 49723–49723 | 1 |
| 18 | header_pagina | 49724–49724 | 1 |
| 19 | header_pagina | 49725–49725 | 1 |
| 20 | firma | 49746–49747 | 2 |
| 21 | catch_all | 49748–49748 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=1 (0.57% del bloque, n=176)

---

### [span 1] header_pagina (49573–49573)
```
329
```

### [span 2] caratula (49574–49574)
```
ANTONIO BARILLARI S.A. V. PROVINCIA DE BUENOS AIRES
```

### [span 3] sumario [1] (49575–49585)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Competencia originaria de
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia federal. Competencia originaria de
la Corte Suprema. Causas en que es parte una provincia. Causas que versan sobre cues-
tiones federales.
Si el planteo exige dilucidar si el accionar proveniente de las autoridades locales
interfiere el ámbito que le es propio a la Nación en materia de pesca, la causa se
encuentra entre las especialmente regidas por la Constitución Nacional, a las
que alude el art. 2º, inc. 1º, de la ley 48, pues versa sobre la preservación de las
órbitas de competencia entre los poderes del Gobierno federal y los de un estado
provincial, lo que hace competente a la justicia nacional y, al ser parte una pro-
vincia, el proceso corresponde a la competencia originaria de la Corte Suprema.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 4] sumario [2] (49586–49590)
**Header**: MEDIDAS CAUTELARES.
**Atribución**: (sin atribución detectada)
```
MEDIDAS CAUTELARES.
Si bien, por vía de principio, las medidas cautelares no proceden respecto de
actos administrativos o legislativos habida cuenta de la presunción de validez
que ostentan, tal doctrina debe ceder cuando se los impugna sobre bases prima
facie verosímiles.
```

### [span 5] sumario [3] (49591–49597)
**Header**: MEDIDA CAUTELAR INNOVATIVA.
**Atribución**: (sin atribución detectada)
```
MEDIDA CAUTELAR INNOVATIVA.
Corresponde decretar la medida cautelar innovativa y hacer saber a la Provincia
de Buenos Aires que deberá abstenerse de exigir, con fundamento en la resolu-
ción 524/04 de la Subsecretaría de Pesca del Ministerio de Asuntos Agrarios, que
la captura que realice la actora fuera de su jurisdicción marítima y para cuyo
desembarco a tierra utilice puertos bonaerenses deba ser procesada en dicho
territorio provincial.
```

### [span 6] dictamen (49598–49675)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
Antonio Barillari S.A., en su carácter de titular de un permiso na-
cional de pesca, promueve acción declarativa, en los términos del
art. 322 del Código Procesal Civil y Comercial de la Nación, contra la
Provincia de Buenos Aires, a fin de obtener que se declare la inconsti-
tucionalidad de la resolución 524/04 de la Subsecretaría de Activida-
des Pesqueras dependiente del Ministerio de Asuntos Agrarios.

2685
DE JUSTICIA DE LA NACION
329
Cuestiona dicha resolución en cuanto le impide transportar los
pescados y mariscos frescos que obtiene en mar argentino (más allá de
las 12 millas) y desembarca en puertos de la Provincia de Buenos Ai-
res, destinados a otras jurisdicciones –esto es, a Comodoro Rivadavia
y a Caleta Olivia, donde también se encuentran sus plantas industria-
les–, disponiendo que su procesamiento debe hacerse previamente en
los establecimientos habilitados en el territorio del Estado local.
Asimismo, señala que, con fundamento en esa determinación, la
Dirección de Fiscalización de Pesca de aquel Ministerio, le negó la “Guía
de Tránsito”, documento que necesita para transportar productos
pesqueros desde la Provincia hacia otras jurisdicciones.
Por lo tanto, indica que el accionar de la Provincia afecta su dere-
cho a la libre circulación interprovincial de mercaderías y su libertad
de trabajar y comerciar, conculcando los arts. 9, 10, 11, 12, 14, 17, 75,
incs. 13 y 18, y 126 de la Constitución Nacional y los arts. 3 y 4 de la
ley nacional 24.922 que establece el Régimen Federal de Pesca.
Solicita como medida cautelar innovativa que se ordene a la de-
mandada a abstenerse de aplicar la resolución 524/04 y a emitir las
guías de tránsito que posibiliten el transporte de los productos
pesqueros desde la Provincia de Buenos Aires hacia otras provincias.
A fs. 69, se corre vista a este Ministerio Público, por la competen-
cia.
– II –
Ante todo, corresponde señalar que uno de los supuestos en que
procede la competencia originaria de la Corte si es parte una Provin-
cia, según el art. 117 de la Constitución Nacional, es cuando la de-
manda que se entabla se funda directa y exclusivamente en prescrip-
ciones constitucionales de carácter nacional, en leyes del Congreso o
en tratados con las naciones extranjeras, de tal suerte que la cuestión
federal sea la predominante en la causa (Fallos: 311:1812 y 2154; 313:98
y 548; 315:448; 318:992 y 2457; 322:1470; 323:2380 y 3279).
En el sub lite, según se desprende de los términos de la demanda
–a cuya exposición de los hechos se debe atender de modo principal
para determinar la competencia, según los arts. 4º y 5º del Código Pro-

2686
FALLOS DE LA CORTE SUPREMA
329
cesal Civil y Comercial de la Nación y doctrina de Fallos: 306:1056;
308:1239 y 2230–, la actora, quien invoca ser permisionaria para el
ejercicio de la actividad pesquera en jurisdicción nacional, cuestiona
una disposición local por ser contraria a la Constitución Nacional y a
la ley que establece el Régimen Federal de Pesca.
A mi modo de ver, en razón de lo expuesto y toda vez que el asunto
en examen se vincula con el comercio interjurisdiccional, la cuestión
reviste naturaleza federal (art. 75, inc. 13 de la Ley Fundamental y
Fallos: 188:27; 199:326; 271:211; 277:237; 312:1495; 321:2501;
323:1534).
Asimismo, dado que el planteamiento que efectúa la actora exige
dilucidar si el accionar proveniente de las autoridades locales interfie-
re el ámbito que le es propio a la Nación en materia de pesca, conside-
ro que la causa se encuentra entre las especialmente regidas por la
Constitución Nacional, a las que alude el art. 2º, inc. 1º, de la ley 48,
pues versa sobre la preservación de las órbitas de competencia entre
los poderes del Gobierno federal y los de un Estado provincial, lo que
hace competente a la justicia nacional para entender en ella (conf.
sentencia in re S.841, XXXVII, Originario, “Servicios Portuarios Inte-
grados S.A. c/ Chubut, Provincia del s/ amparo”, del 18 de julio de
2002, y Fallos: 317:397; 325:3209 y 326:676).
En atención a lo expuesto, al ser parte una Provincia en una causa
de manifiesto contenido federal, considero que –cualquiera que sea la
vecindad o nacionalidad de la actora (Fallos: 317:473; 318:30 y sus
citas y 323:1716, entre otros)– el proceso corresponde a la competen-
cia originaria de la Corte. Buenos Aires, 9 de noviembre de 2005. Ri-
cardo O. Bausset.
```

### [span 7] header_pagina (49608–49608)
```
2685
```

### [span 8] header_pagina (49609–49609)
```
DE JUSTICIA DE LA NACION
```

### [span 9] header_pagina (49610–49610)
```
329
```

### [span 10] header_pagina (49646–49646)
```
2686
```

### [span 11] header_pagina (49647–49647)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 12] header_pagina (49648–49648)
```
329
```

### [span 13] cuerpo_mayoria (49676–49745)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 11 de julio de 2006.
Autos y Vistos; Considerando:
1º) Que a fs. 59/67 Antonio Barillari S.A. promueve la acción pre-
vista en el art. 322 del Código Procesal Civil y Comercial de la Nación

2687
DE JUSTICIA DE LA NACION
329
contra la Provincia de Buenos Aires con el objeto de que se declare la
inconstitucionalidad de la resolución 524/04 de la Subsecretaría de
Actividades Pesqueras dependiente del Ministerio de Asuntos Agra-
rios, por medio de la cual con relación a los pescados y mariscos que se
descarguen en puertos bonaerenses se dispuso que el transporte fuera
del territorio provincial estaba condicionado a que se los procesara en
establecimientos industriales habilitados al efecto y radicados en la
provincia.
Manifiesta que realiza una importante actividad pesquera de mer-
luza y otras especies sólo en aguas nacionales, que las capturas son
procesadas en establecimientos de su propiedad en Mar del Plata,
Comodoro Rivadavia y Caleta Olivia; y que la decisión provincial que
impugna afecta seriamente el giro normal de su actividad comercial,
al restringir ilegítimamente el traslado de la mercadería hacia otros
estados provinciales, provocando el peligro de un desabastecimiento
de materia prima en sus plantas procesadoras ubicadas en jurisdiccio-
nes vecinas. Expone que la Dirección de Fiscalización de Pesca provin-
cial le ha denegado –como lo acredita con el acta obrante a fs. 11/12–
las guías de tránsito necesarias para el transporte de los productos
pesqueros fuera del territorio de la demandada.
De este modo –según expone– la norma en cuestión conculca sus
derechos a la libre circulación de mercadería y su libertad de trabajar
y comerciar previstos en los arts. 9, 10, 11, 12, 14, 17, 75, inc. 13 y 18,
y 126 de la Constitución Nacional; a su vez, viola los arts. 3 y 4 de la
ley federal de pesca 24.922 al prohibir que la captura realizada en
jurisdicción federal, más allá de las 12 millas marinas, y descargada
en puertos bonaerenses pueda circular libremente dentro del país.
2º) Que la presente demanda es de la competencia originaria de
esta Corte, de acuerdo con los fundamentos y la conclusión dados en el
dictamen del señor Procurador Fiscal subrogante que antecede, a los
que cabe remitir brevitatis causa.
3º) Que la actora solicita una medida cautelar innovativa consis-
tente en que se ordene la suspensión de la aplicación de la norma im-
pugnada hasta tanto se dicte sentencia definitiva en los autos.
4º) Que este Tribunal ha establecido que si bien, por vía de princi-
pio, medidas como las requeridas no proceden respecto de actos admi-
nistrativos o legislativos habida cuenta de la presunción de validez

2688
FALLOS DE LA CORTE SUPREMA
329
que ostentan, tal doctrina debe ceder cuando se los impugna sobre
bases prima facie verosímiles (Fallos: 250:154; 251:336; 307:1702;
314:695).
En el presente caso resultan suficientemente acreditadas la vero-
similitud en el derecho y el peligro en la demora previstos en los incs. 1º
y 2º del art. 230 del Código Procesal Civil y Comercial de la Nación
para acceder a la medida pedida.
Por ello, se resuelve: I. Correr traslado de la demanda interpuesta
a la Provincia de Buenos Aires, la que se sustanciará por la vía del
proceso ordinario, por el plazo de sesenta días (arts. 338 y concs., Có-
digo Procesal Civil y Comercial de la Nación). Para su comunicación al
señor gobernador y al señor fiscal de Estado líbrese oficio al señor juez
federal en turno de la ciudad de La Plata. II. Decretar la medida cau-
telar innovativa y en consecuencia hacer saber a la Provincia de Bue-
nos Aires que deberá abstenerse de exigir, con fundamento en la reso-
lución 524/04 de la Subsecretaría de Pesca del Ministerio de Asuntos
Agrarios, que la captura que realice la actora fuera de su jurisdicción
marítima y para cuyo desembarco a tierra utilice puertos bonaerenses
deba ser procesada en dicho territorio provincial. Notifíquese la medi-
da directamente al señor gobernador, por oficio.
```

### [span 14] header_pagina (49682–49682)
```
2687
```

### [span 15] header_pagina (49683–49683)
```
DE JUSTICIA DE LA NACION
```

### [span 16] header_pagina (49684–49684)
```
329
```

### [span 17] header_pagina (49723–49723)
```
2688
```

### [span 18] header_pagina (49724–49724)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 19] header_pagina (49725–49725)
```
329
```

### [span 20] firma (49746–49747)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS
S. FAYT — JUAN CARLOS MAQUEDA — RICARDO LUIS LORENZETTI.
```

### [span 21] catch_all (49748–49748)
```
Por la actora: doctores Carlos Choco, Roberto A. Muguillo y María Teresa Muguillo.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=49748 | linea_inicio_proximo_caso=49725 | delta=-24
**Alertas**: `solapado_con_proximo`


---

## 347_p105 — L., M. E. c/ PAMI (INSSJYP) s/ Amparo ley 16.986

**Localización**
- Archivo: `LibroVol347-1.md`
- Páginas catálogo: 105–109 | Página consultada: 109
- Líneas catálogo: 4025–4162 | Línea fin real: 4163 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 4025–4025 | 1 |
| 2 | catch_all | 4026–4030 | 5 |
| 3 | caratula | 4031–4031 | 1 |
| 4 | sumario [1] | 4032–4042 | 11 |
| 5 | sumario [2] | 4043–4058 | 16 |
| 6 | header_pagina | 4056–4056 | 1 |
| 7 | header_pagina | 4057–4057 | 1 |
| 8 | header_pagina | 4058–4058 | 1 |
| 9 | sumario [3] | 4059–4068 | 10 |
| 10 | cuerpo_mayoria | 4069–4153 | 85 |
| 11 | header_pagina | 4092–4092 | 1 |
| 12 | header_pagina | 4093–4093 | 1 |
| 13 | header_pagina | 4094–4094 | 1 |
| 14 | header_pagina | 4133–4133 | 1 |
| 15 | header_pagina | 4134–4134 | 1 |
| 16 | header_pagina | 4135–4135 | 1 |
| 17 | firma | 4154–4155 | 2 |
| 18 | catch_all | 4156–4160 | 5 |
| 19 | header_pagina | 4161–4161 | 1 |
| 20 | header_pagina | 4162–4162 | 1 |
| 21 | header_pagina | 4163–4163 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=10 (7.19% del bloque, n=139)

---

### [span 1] header_pagina (4025–4025)
```
347
```

### [span 2] catch_all (4026–4030)
```
Recurso de queja interpuesto por COMA S.A., representada por la Dra. Graciela Pa­
ganini.
Tribunal de origen: Sala IX de la Cámara Nacional de Apelaciones del Trabajo.
Tribunal que intervino con anterioridad: Juzgado Nacional de Primera Instancia del 
Trabajo n° 62.
```

### [span 3] caratula (4031–4031)
```
L., M. E. c/ PAMI (INSSJYP) s/ Amparo ley 16.986
```

### [span 4] sumario [1] (4032–4042)
**Header**: COSTAS
**Atribución**: (sin atribución detectada)
```
COSTAS
Es arbitraria la sentencia que, al hacer lugar a una acción de amparo 
contra una obra social por la provisión de prestaciones médicas, distri­
buyó las costas por su orden, pues no consideró que el art. 68 del Código 
Procesal Civil y Comercial de la Nación que citó resultaba inaplicable al 
caso, en tanto tratándose de un proceso de amparo las costas debían ser 
impuestas según lo normado en el art. 14 de la ley 16.986 que establece 
la imposición a la parte vencida con la sola excepción de que, con ante­
rioridad a la contestación del informe previsto en el art. 8° de esa ley, se 
produzca el cese del acto u omisión en que se fundó el amparo, supuesto 
que no ocurrió en las actuaciones.
```

### [span 5] sumario [2] (4043–4058)
**Header**: COSTAS
**Atribución**: (sin atribución detectada)
```
COSTAS
Es arbitraria la sentencia que, al hacer lugar a una acción de amparo 
contra una obra social por la provisión de prestaciones médicas, distri­
buyó las costas por su orden, pues la cámara no proporcionó una razón 
válida para justificar el apartamiento de la ley 16.986, así como que -pese 
a haber confirmado in totum el fallo de la instancia anterior que había 
hecho lugar a la pretensión- modificó la imposición de las costas de am­
bas instancias, sin que esa decisión atendiera al resultado del pleito y 
utilizando como argumento decisivo el hecho de que la actora fue repre­
sentada por la defensoría oficial, circunstancia que, además de no estar 
contemplada en la normativa aplicable al caso, carece de relevancia a 
los fines de la distribución de los gastos causídicos.

347
106
FALLOS DE LA CORTE SUPREMA
```

### [span 6] header_pagina (4056–4056)
```
347
```

### [span 7] header_pagina (4057–4057)
```
106
```

### [span 8] header_pagina (4058–4058)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] sumario [3] (4059–4068)
**Header**: RECURSO EXTRAORDINARIO
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO
Si bien las cuestiones atinentes a la imposición de las costas del proce­
so, por ser de derecho común y procesal, resultan propias de los jueces 
de la causa y ajenas -como regla a la vía del art. 14 de la ley 48, a la par 
que la aplicación de la doctrina de la arbitrariedad es especialmente 
restringida en esta materia; tales principios admiten excepción cuando 
se denuncia que el fallo apelado afecta la garantía de defensa en juicio 
por otorgar un tratamiento inadecuado a la controversia suscitada, al 
utilizar una fundamentación dogmática y apartarse sin fundamentos de 
las normas concretamente aplicables al caso.
```

### [span 10] cuerpo_mayoria (4069–4153)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 29 de febrero de 2024.
Vistos los autos: “Recurso de hecho deducido por la actora en la 
causa L., M. E. c/ PAMI (INSSJYP) s/ amparo ley 16.986”, para decidir 
sobre su procedencia.
Considerando:
1º) Que la Sala I de la Cámara Federal de Apelaciones de Salta, 
ante el recurso de apelación deducido por la demandada, confirmó el 
pronunciamiento de la instancia anterior mediante el cual se había he­
cho lugar a la acción de amparo iniciada por la actora, representada 
por el Defensor Oficial, para que el Instituto Nacional de Servicios So­
ciales para Jubilados y Pensionados (INSSJP) le provea las prestacio­
nes médicas que requiere con motivo de su enfermedad. No obstante, 
modificó la decisión solo en lo atinente a la imposición de las costas, 
las que distribuyó por su orden en ambas instancias.
2º) Que para así decidir, el tribunal a quo, tras concluir que las 
manifestaciones esgrimidas por la enjuiciada resultaban insuficientes 
para modificar la solución dada por el juez de primera instancia, ex­
presó -sin más- que “por las particularidades del caso y porque es cri­
terio sostenido por esta Sala que en cuestiones como la aquí planteada 
en las que concurre la intervención del Defensor Oficial en represen­
tación de la actora, las costas se distribuyen por el orden causado (art.

107
DE JUSTICIA DE LA NACIÓN
347
68, segundo párrafo, del CPCCN), corresponde modificar las de la ins­
tancia anterior, e imponerlas por su orden en todo el proceso”.
3°) Que contra esa decisión la demandante interpuso el recurso ex­
traordinario cuya denegación motiva esta queja, en el que invoca como 
cuestión federal la doctrina de esta Corte en materia de sentencias 
arbitrarias. Sostiene que el tribunal de alzada dictó un fallo dogmáti­
co y se apartó manifiestamente de las circunstancias de la causa, así 
como de lo dispuesto en el art. 14 de la ley 16.986, aplicable al caso, con 
afectación de sus derechos de propiedad y debido proceso.
4º) Que los agravios planteados por la apelante suscitan cuestión 
federal suficiente para su tratamiento por la vía elegida, en tanto si 
bien de conformidad con reiterada doctrina de esta Corte las cues­
tiones atinentes a la imposición de las costas del proceso, por ser de 
derecho común y procesal, resultan propias de los jueces de la causa 
y ajenas -como regla- a la vía del art. 14 de la ley 48 (Fallos: 278:48; 
308:1076; 317:1139 y 339:1691), a la par que la aplicación de la doctrina 
de la arbitrariedad es especialmente restringida en esta materia (Fa­
llos: 311:1950); tales principios admiten excepción cuando se denuncia 
que el fallo apelado afecta la garantía de defensa en juicio por otor­
gar un tratamiento inadecuado a la controversia suscitada, al utilizar 
una fundamentación dogmática y apartarse sin fundamentos de las 
normas concretamente aplicables al caso (Fallos: 311:1189; 321:654; 
322:464 y 329:2856).
5º) Que, en efecto, ello acontece en el sub examine en tanto el 
tribunal a quo impuso las costas por su orden, sin considerar que el 
art. 68 del código de rito que citó resultaba inaplicable a este asun­
to, pues tratándose de un proceso de amparo las costas debían ser 
impuestas según lo normado en el art. 14 de la ley 16.986 -precepto 
vinculado directamente a la concreta situación suscitada en la cau­
sa- que establece la imposición de las costas a la parte vencida con la 
sola excepción de que, con anterioridad a la contestación del informe 
previsto en el art. 8° de esa ley, se produzca el cese del acto u omisión 
en que se fundó el amparo, supuesto que no ocurrió en estas actua­
ciones (Fallos: 329:2856).
Más aún, de las constancias de autos se advierte que la cámara 
no proporcionó una razón válida para justificar su apartamiento de la 
norma referida, así como que -pese a haber confirmado in totum el

347
108
FALLOS DE LA CORTE SUPREMA
fallo de la instancia anterior que había hecho lugar a la pretensión- 
modificó la imposición de las costas de ambas instancias, sin que esa 
decisión atendiera al resultado del pleito y utilizando como argumento 
decisivo el hecho de que la actora fue representada por la defensoría 
oficial, circunstancia que, además de no estar contemplada en la nor­
mativa aplicable al caso, carece de relevancia a los fines de la distribu­
ción de los gastos causídicos.
6°) Que, en las condiciones expresadas, los graves defectos en que 
incurrió el tribunal de alzada afectan de modo directo e inmediato la 
garantía constitucional de defensa en juicio que asiste a la recurrente 
(ley 48, art. 15) y justifican la invalidación del pronunciamiento a fin de 
que la cuestión sea nuevamente decidida mediante un fallo constitu­
cionalmente sostenible.
Por ello, se hace lugar a la queja, se declara procedente el recurso 
extraordinario y se deja sin efecto la sentencia apelada. Con costas 
a la demandada. Vuelvan los autos al tribunal de origen a fin de que, 
por quien corresponda, se dicte un nuevo fallo con arreglo al presente. 
Notifíquese y devuélvase.
```

### [span 11] header_pagina (4092–4092)
```
107
```

### [span 12] header_pagina (4093–4093)
```
DE JUSTICIA DE LA NACIÓN
```

### [span 13] header_pagina (4094–4094)
```
347
```

### [span 14] header_pagina (4133–4133)
```
347
```

### [span 15] header_pagina (4134–4134)
```
108
```

### [span 16] header_pagina (4135–4135)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 17] firma (4154–4155)
```
Horacio Rosatti — Carlos Fernando Rosenkrantz — Juan Carlos 
Maqueda — Ricardo Luis Lorenzetti.
```

### [span 18] catch_all (4156–4160)
```
Recurso de queja interpuesto por la actora, M. E. L., representada por el Dr. Martín 
Bomba Royo, Defensor Público Oficial.
Tribunal de origen: Cámara Federal de Apelaciones de Salta, Sala I.
Tribunal que intervino con anterioridad: Juzgado Federal n° 2 de Jujuy.

```

### [span 19] header_pagina (4161–4161)
```
109
```

### [span 20] header_pagina (4162–4162)
```
DE JUSTICIA DE LA NACIÓN
```

### [span 21] header_pagina (4163–4163)
```
347
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=4163 | linea_inicio_proximo_caso=4163 | delta=-1
**Alertas**: `solapado_con_proximo`


---

## 329_p2314 — Ferrocarriles Argentinos (E.L.) c/ Provincia de Río Negro | Provincia de Río Negro (Ferrocarriles Argentinos (E.L.) c/) 

**Localización**
- Archivo: `LibroVol329.2.md`
- Páginas catálogo: 2314–2316 | Página consultada: 2316
- Líneas catálogo: 35526–35597 | Línea fin real: 35621 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 35526–35526 | 1 |
| 2 | catch_all | 35527–35537 | 11 |
| 3 | caratula | 35538–35538 | 1 |
| 4 | sumario [1] | 35539–35542 | 4 |
| 5 | sumario [2] | 35543–35543 | 1 |
| 6 | sumario [3] | 35544–35549 | 6 |
| 7 | sumario [4] | 35550–35559 | 10 |
| 8 | header_pagina | 35557–35557 | 1 |
| 9 | header_pagina | 35558–35558 | 1 |
| 10 | header_pagina | 35559–35559 | 1 |
| 11 | cuerpo_mayoria | 35560–35614 | 55 |
| 12 | header_pagina | 35596–35596 | 1 |
| 13 | header_pagina | 35597–35597 | 1 |
| 14 | header_pagina | 35598–35598 | 1 |
| 15 | firma | 35615–35616 | 2 |
| 16 | catch_all | 35617–35621 | 5 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=16 (16.67% del bloque, n=96)

---

### [span 1] header_pagina (35526–35526)
```
329
```

### [span 2] catch_all (35527–35537)
```
carlo fuera del orden jurídico (arg. Fallos: 322:1201 y 324:933 y cau-
sas: C.276.XXXIX. “Caja Complementaria de Previsión para la Activi-
dad Docente c/ Jujuy, Provincia de s/ ejecución fiscal” y C.903.XXXVII.
“Caja Complementaria de Previsión para la Actividad Docente c/ Jujuy,
Provincia de s/ ejecución fiscal”, resoluciones del 8 de noviembre de
2005), debe desestimarse el pedido de levantamiento de embargo for-
mulado y, atento que no se han opuesto excepciones, mandar llevar
adelante la ejecución.
Por ello, se resuelve: Desestimar los planteos deducidos a fs. 578 y
593/595 y ordenar que se lleve adelante la ejecución hasta hacerse a
los acreedores íntegro pago del capital reclamado, intereses y costas
```

### [span 3] caratula (35538–35538)
```
(art. 508 del código citado) (Fallos: 311:1795; 318:2660). Notifíquese.
```

### [span 4] sumario [1] (35539–35542)
**Header**: ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS
**Atribución**: (sin atribución detectada)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS
S. FAYT — JUAN CARLOS MAQUEDA — CARMEN M. ARGIBAY.
Profesionales intervinientes: Dres: José Samper, Pablo Miguel Jcoby, R.A. Patri-
cio Carballés, Andrés B. Alvarez y Pablo R. Vélez.
```

### [span 5] sumario [2] (35543–35543)
**Header**: FERROCARRILES ARGENTINOS (E. L.) V. PROVINCIA DE RIO NEGRO
**Atribución**: (sin atribución detectada)
```
FERROCARRILES ARGENTINOS (E. L.) V. PROVINCIA DE RIO NEGRO
```

### [span 6] sumario [3] (35544–35549)
**Header**: TRANSACCION.
**Atribución**: (sin atribución detectada)
```
TRANSACCION.
La interpretación del contenido de toda transacción está presidida por un crite-
rio estricto que expresamente contempla el art. 835 del Código Civil y este prin-
cipio hermenéutico lleva a que, aun de verificarse un estado de duda, deba en-
tenderse que los derechos no incluidos en el acto jurídico quedan fuera de los
efectos extintivos de esa convención liberatoria.
```

### [span 7] sumario [4] (35550–35559)
**Header**: SECRETARIO DE LA CORTE SUPREMA.
**Atribución**: (sin atribución detectada)
```
SECRETARIO DE LA CORTE SUPREMA.
Corresponde rechazar los recursos interpuestos contra la providencia suscripta
por el Secretario de la Corte a cargo de la Secretaría de Juicios Originarios, pues
no es ni más ni menos que la consecuencia ineludible de una decisión adoptada
en el expediente que se encuentra firme, por haber consentido la demandada la
resolución desestimatoria de su primer planteo.

2315
DE JUSTICIA DE LA NACION
329
```

### [span 8] header_pagina (35557–35557)
```
2315
```

### [span 9] header_pagina (35558–35558)
```
DE JUSTICIA DE LA NACION
```

### [span 10] header_pagina (35559–35559)
```
329
```

### [span 11] cuerpo_mayoria (35560–35614)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 20 de junio de 2006.
Autos y Vistos; Considerando:
1º) Que a fs. 302/303 la demandada interpone recurso de reposi-
ción y nulidad contra la providencia recaída a fs. 301, por medio de la
cual se rechazó el pedido que aquella parte había formulado para que
se extiendan a estos autos los efectos extintivos del convenio celebrado
en la causa E.59.XXXVII “E.N.A.B.I.E.F. c/ Río Negro, Provincia de y
otro s/ demanda ordinaria”, acumulada a estas actuaciones, que fue
homologado por el Tribunal mediante sentencia del cinco de abril de
2005.
2º) Que los argumentos sostenidos por la recurrente no desvirtúan
el fundamento esencial que dio lugar a la providencia en cuestión,
consistente en que el planteo efectuado por dicha parte a fs. 298/300
remitía a una petición de igual naturaleza que había sido tratada y
rechazada por la cámara federal en la resolución de fs. 216/218
(considerandos 3º a 9º), cuyas consideraciones y conclusión eran de
entera aplicación en cuanto habían definido que los reclamos efectua-
dos en ambas causas eran de diverso objeto y esta circunstancia impe-
día la extensión requerida.
Por lo demás, cabe señalar que, contrariamente a lo sostenido por
la demandada, el acuerdo que se intenta hacer valer sólo comprendió
el crédito por los alquileres de distintas máquinas que se individua-
lizaron con toda precisión (locomotoras Nros. 9041 y 6411 y locotractor
Nº 10.013 –ver fs. 151, anexo II, punto 3–), en la medida en que ningu-
na referencia –aun tácita– efectuó con respecto a las obligaciones
atinentes a peajes de trenes, déficit de corridas, ajuste de intereses e
I.V.A., que han sido el definido objeto de la pretensión introducida en
estas actuaciones.
3º) Que de tal manera, frente a los términos claros e inequívocos
del objeto comprendido en el acuerdo de voluntades mencionado, la
extensión que se postula es inadmisible, máxime cuando, por su natu-
raleza, la interpretación del contenido de toda transacción está presi-
dida por un criterio estricto que expresamente contempla el art. 835
del Código Civil y este principio hermenéutico lleva a que, aun de ve-

2316
FALLOS DE LA CORTE SUPREMA
329
rificarse un estado de duda que no concurre en el caso, deba entender-
se que los derechos no incluidos en el acto jurídico quedan fuera de los
efectos extintivos de esa convención liberatoria.
4º) Que, por otra parte, tampoco puede ser atendida la argumenta-
ción que se introduce en los puntos 2.1 y siguientes ya que la providen-
cia recurrida, suscripta por el señor Secretario de esta Corte a cargo
de la Secretaría de Juicios Originarios, no es ni más ni menos que la
consecuencia ineludible de una decisión adoptada en este expediente
que se encuentra firme, por haber consentido la demandada la resolu-
ción desestimatoria de su primer planteo, que vanamente intenta ree-
ditar en la presentación de fs. 298/300 que mereció la providencia que
por la presente se confirma (ver fs. 216/218 y causa: P.417.XXIII “Pérez,
María Elisa y otra c/ San Luis, Provincia de y otro s/ daños y perjui-
cios”, sentencia del 16 de mayo de 2000).
Por ello, se resuelve: Rechazar el recurso interpuesto a fs. 302/303.
Notifíquese.
```

### [span 12] header_pagina (35596–35596)
```
2316
```

### [span 13] header_pagina (35597–35597)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 14] header_pagina (35598–35598)
```
329
```

### [span 15] firma (35615–35616)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — RICARDO LUIS LORENZETTI — CARMEN M. ARGIBAY.
```

### [span 16] catch_all (35617–35621)
```
Demanda interpuesta por Ferrocarriles Argentinos (E.L.), representado por el Dr.
Bernardo Cazenave, patrocinado por los Dres. Alfredo R. Elsegood y Jorge F.
Estruch.
Nombre de los demandados: Provincia de Río Negro, representada por el Dr. Daniel
Palenque Bullrich.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=35621 | linea_inicio_proximo_caso=35598 | delta=-24
**Alertas**: `solapado_con_proximo`


---
