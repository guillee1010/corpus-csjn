# Auditoría de fallos
Generado: 2026-05-17 23:37
Versión: 1.0.0
Comando: `diag_h036 --categoria A2_disp_real --n 10 --seed 42`
Casos auditados: 10
Seed: 42
Borde inferior: solapado_con_proximo=7, gap_con_residuo=3 | alertas totales: 11

---

## 330_p803 — Banco Río de la Plata S.A. c/ Industrias J. Matas S.C.A. y otro | Industrias J. Matas S.C.A. y otro (Banco Río de la Pla

**Localización**
- Archivo: `LibroVol330.1.md`
- Páginas catálogo: 803–807 | Página consultada: 807
- Líneas catálogo: 30485–30627 | Línea fin real: 30623 (status_fin=`fin_dentro_bloque`, pista=`sumario_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 30485–30485 | 1 |
| 2 | catch_all | 30486–30509 | 24 |
| 3 | caratula | 30510–30510 | 1 |
| 4 | sumario [1] | 30511–30518 | 8 |
| 5 | header_pagina | 30516–30516 | 1 |
| 6 | header_pagina | 30517–30517 | 1 |
| 7 | header_pagina | 30518–30518 | 1 |
| 8 | sumario [2] | 30519–30524 | 6 |
| 9 | sumario [3] | 30525–30533 | 9 |
| 10 | dictamen | 30534–30613 | 80 |
| 11 | header_pagina | 30554–30554 | 1 |
| 12 | header_pagina | 30555–30555 | 1 |
| 13 | header_pagina | 30556–30556 | 1 |
| 14 | header_pagina | 30593–30593 | 1 |
| 15 | header_pagina | 30594–30594 | 1 |
| 16 | header_pagina | 30595–30595 | 1 |
| 17 | cuerpo_mayoria | 30614–30622 | 9 |
| 18 | firma | 30623–30623 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=24 (17.27% del bloque, n=139)

---

### [span 1] header_pagina (30485–30485)
```
330
```

### [span 2] catch_all (30486–30509)
```
las particularidades procesales reseñadas en el párrafo precedente, el
reenvió de la causa al fuero federal, importaría someter cuestiones ya
consideradas y decididas en el ámbito de otro tribunal, situación que
importa generar un evidente retardo injustificado en el trámite de las
actuaciones que va en desmedro del principio de seguridad jurídica y
economía procesal.
Por todo lo expuesto, dentro del limitado marco cognoscitivo en el
que se tienen que resolver las cuestiones de competencia y dado el
carácter nacional que revisten los tribunales aquí en conflicto, estimo
que corresponde dirimir la contienda y disponer que compete a la Jus-
ticia Nacional en lo Civil, seguir conociendo en las presentes actuacio-
nes. Buenos Aires, 27 de septiembre de 2006. Marta A. Beiró de
Gonçalvez.
FALLO DE LA CORTE SUPREMA
Buenos Aires, 13 de marzo de 2007.
Autos y Vistos:
De conformidad con lo dictaminado por la señora Procuradora Fis-
cal subrogante, se declara que resulta competente para conocer en las
actuaciones el Juzgado Nacional de Primera Instancia en lo Civil
Nº 105, al que se le remitirán por intermedio de la Sala D de la cáma-
ra de apelaciones de dicho fuero. Hágase saber al Juzgado Nacional de
Primera Instancia en lo Civil y Comercial Federal Nº 4.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA.
```

### [span 3] caratula (30510–30510)
```
BANCO RIO DE LA PLATA S.A. V. INDUSTRIAS J. MATAS S.C.A. Y OTRO
```

### [span 4] sumario [1] (30511–30518)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Generalidades.
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Generalidades.
Las cuestiones de competencia entre tribunales de distinta jurisdicción deben
ser resueltas por aplicación de las normas nacionales de procedimientos.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.

804
FALLOS DE LA CORTE SUPREMA
330
```

### [span 5] header_pagina (30516–30516)
```
804
```

### [span 6] header_pagina (30517–30517)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 7] header_pagina (30518–30518)
```
330
```

### [span 8] sumario [2] (30519–30524)
**Header**: JURISDICCION Y COMPETENCIA: Prórroga. Convenio de partes.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Prórroga. Convenio de partes.
El art. 2º, primera parte, del Código Procesal Civil y Comercial de la Nación,
establece que la jurisdicción territorial es esencialmente prorrogable por confor-
midad de los interesados cuando se trata de asuntos exclusivamente patrimo-
niales.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 9] sumario [3] (30525–30533)
**Header**: JURISDICCION Y COMPETENCIA: Prórroga. Convenio de partes.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Prórroga. Convenio de partes.
Corresponde rechazar la impugnación de invalidez de la cláusula de prórroga de
jurisdicción –fundada en su carácter abusivo con sustento en la ley de Defensa
del Consumidor– pues la ejecución se sustenta en un contrato de mutuo con ga-
rantía hipotecaria y no en un contrato que revista características propias de aque-
llos denominados como de “adhesión”, máxime si el demandado no requirió su
nulidad ni demostró que importe una efectiva afectación a la defensa en juicio o
que le genere una virtual denegación de justicia.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 10] dictamen (30534–30613)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
El señor juez a cargo del Juzgado en lo Civil, Comercial y Minas de
la Primera Circunscripción Judicial de la Provincia de Mendoza, hizo
lugar a la inhibitoria interpuesta por la demandada y declaró su com-
petencia para entender en los autos: “Banco Río de la Plata S.A. c/
Industrias J. Matas y otro s/ ejecución especial ley 24.441. Ejecutivo”,
Expediente Nº 75.538/2005, en trámite ante el Juzgado Nacional de
Primera Instancia en lo Civil Nº 89.
Señaló, que resultaba competente para conocer en la causa la jus-
ticia ordinaria del referido estado provincial en virtud que, el domici-
lio de la empresa demandada se halla en la Provincia de Mendoza y
porque el artículo 4º del código de rito local dispone que la competen-
cia de los Tribunales Provinciales es improrrogable en las relaciones
jurídicas nacidas de contratos con garantías hipotecarias, siempre y
cuando se hubieran celebrado en el ámbito de la provincia, el bien se
encuentre en su ámbito territorial y/o estén comprometidos derechos
del consumidor resguardados por la ley 24.240 (Ver fs. 244/245 y 249).

805
DE JUSTICIA DE LA NACION
330
Por su parte, el magistrado nacional, rechazó la inhibitoria del
magistrado provincial y declaró su competencia, con sustento en la
prórroga de jurisdicción acordada por las partes en el contrato de mutuo
con garantía real obrante a fojas 57/81 de las presentes actuaciones
(Ver fs. 265/266).
En tales condiciones se planteó un conflicto de competencia que
corresponde dirimir a esta Corte en los términos del artículo 24 inciso
7º del decreto-ley 1285/58.
– II –
Debo señalar, en primer lugar, que V.E. tiene reiteradamente di-
cho que las cuestiones de competencia entre tribunales de distinta
jurisdicción deben ser resueltas por aplicación de las normas naciona-
les de procedimientos (Ver Doctrina de Fallos: 302:1380, entre otros).
En tales condiciones, cabe resaltar que el artículo 2º, primera par-
te, del Código Procesal Civil y Comercial de la Nación, establece que la
jurisdicción territorial es esencialmente prorrogable por conformidad
de los interesados cuando se trata, como ocurre en autos, de asuntos
exclusivamente patrimoniales (Ver Doctrina de Fallos: 306:542 y
313:717, entre muchos otros).
En tal orden de ideas, en oportunidad de concluirse la relación
jurídica que los vinculó, los contratantes admitieron someterse expre-
samente a la jurisdicción y competencia de los tribunales ordinarios
de la Ciudad de Buenos Aires (Ver fojas 76 y vta., punto VI, del contra-
to en que se funda la demanda).
Cabe señalar, a mayor abundamiento, que no resulta óbice a la
adopción del criterio expuesto precedentemente, las alegaciones invo-
cadas por la accionada en cuanto peticiona, en forma genérica, la in-
validez de la referida cláusula de prórroga de jurisdicción por su ca-
rácter abusivo con sustento, centralmente, en la ley de Defensa del
Consumidor y en la Resolución Nº 53/2003 de la Secretaría de la Com-
petencia, la Desregulación y la Defensa del consumidor. Así lo pienso
toda vez que la presente ejecución se sustenta en un contrato de mu-
tuo con garantía hipotecaria y no en un contrato que revista caracte-
rísticas propias de aquellos denominados como de “adhesión” –en los
que su contenido se estructura a partir de cláusulas predispuestas

806
FALLOS DE LA CORTE SUPREMA
330
que impliquen un perjuicio o una inequidad para la parte adherente
de la relación contractual–, máxime cuando surge de las constancias
de autos, que el demandado no ha requerido su nulidad, ni ha demos-
trado en forma concreta que la misma importe una efectiva afectación
a la debida defensa en juicio o que le genere una virtual denegación de
justicia.
Considero, que las circunstancias apuntadas precedentemente,
sumadas a que de una lectura pormenorizada de las actuaciones sur-
ge que el referido acuerdo de prórroga jurisdiccional no importa des-
virtuar, prima facie, el objeto fin de la relación contractual base de la
presente acción, antecedente que a estos fines permite atender a lo
convenido en la cláusula mencionada.
En tal sentido, entiendo que la inhibitoria planteada ante el ma-
gistrado en lo civil, comercial y de minas de la Provincia de Mendoza,
debe ser rechazada y disponer que ha de seguir entendiendo en las
presentes actuaciones el Juzgado de Primera Instancia en lo Civil
Nº 89. Buenos Aires, 19 de diciembre de 2006. Marta A. Beiró de
Gonçalvez.
```

### [span 11] header_pagina (30554–30554)
```
805
```

### [span 12] header_pagina (30555–30555)
```
DE JUSTICIA DE LA NACION
```

### [span 13] header_pagina (30556–30556)
```
330
```

### [span 14] header_pagina (30593–30593)
```
806
```

### [span 15] header_pagina (30594–30594)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 16] header_pagina (30595–30595)
```
330
```

### [span 17] cuerpo_mayoria (30614–30622)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 13 de marzo de 2007.
Autos y Vistos:
De conformidad con lo dictaminado por la señora Procuradora Fis-
cal subrogante, se declara que resulta competente para conocer en las
actuaciones el Juzgado Nacional de Primera Instancia en lo Civil Nº 89,
al que se le remitirán. Hágase saber al Sexto Juzgado en lo Civil, Co-
mercial y Minas de la Primera Circunscripción Judicial de la Provin-
cia de Mendoza.
```

### [span 18] firma (30623–30623)
```
ELENA I. HIGHTON DE NOLASCO — CARLOS S. FAYT — ENRIQUE SANTIAGO
```

### Borde inferior (transición al próximo caso)
**Estado**: `gap_con_residuo` | linea_fin_real=30623 | linea_inicio_proximo_caso=30628 | delta=4
**Alertas**: `firma_multilinea_partida_por_fin_real`

| Línea | Clasificación | Texto |
|------:|---------------|-------|
| 30624 | `firma_arrastrada` | PETRACCHI — JUAN CARLOS MAQUEDA. |
| 30625 | `vacia` |  |
| 30626 | `header_pagina` | 807 |
| 30627 | `header_pagina` | DE JUSTICIA DE LA NACION |


---

## 329_p2532 — Cámara de Comercio, Industria y Agropecuaria de San Rafael c/ Poder Ejecutivo Nacional | Poder Ejecutivo Nacional (Cámar

**Localización**
- Archivo: `LibroVol329.2.md`
- Páginas catálogo: 2532–2539 | Página consultada: 2539
- Líneas catálogo: 43936–44185 | Línea fin real: 44186 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 43936–43936 | 1 |
| 2 | catch_all | 43937–43962 | 26 |
| 3 | caratula | 43963–43963 | 1 |
| 4 | sumario [1] | 43964–43976 | 13 |
| 5 | header_pagina | 43969–43969 | 1 |
| 6 | header_pagina | 43970–43970 | 1 |
| 7 | header_pagina | 43971–43971 | 1 |
| 8 | sumario [2] | 43977–43983 | 7 |
| 9 | sumario [3] | 43984–43992 | 9 |
| 10 | sumario [4] | 43993–43998 | 6 |
| 11 | sumario [5] | 43999–44007 | 9 |
| 12 | header_pagina | 44005–44005 | 1 |
| 13 | header_pagina | 44006–44006 | 1 |
| 14 | header_pagina | 44007–44007 | 1 |
| 15 | dictamen | 44008–44146 | 139 |
| 16 | header_pagina | 44043–44043 | 1 |
| 17 | header_pagina | 44044–44044 | 1 |
| 18 | header_pagina | 44045–44045 | 1 |
| 19 | header_pagina | 44080–44080 | 1 |
| 20 | header_pagina | 44081–44081 | 1 |
| 21 | header_pagina | 44082–44082 | 1 |
| 22 | header_pagina | 44118–44118 | 1 |
| 23 | header_pagina | 44119–44119 | 1 |
| 24 | header_pagina | 44120–44120 | 1 |
| 25 | cuerpo_mayoria | 44147–44165 | 19 |
| 26 | header_pagina | 44152–44152 | 1 |
| 27 | header_pagina | 44153–44153 | 1 |
| 28 | header_pagina | 44154–44154 | 1 |
| 29 | firma | 44166–44168 | 3 |
| 30 | disidencia | 44169–44186 | 18 |
| 31 | header_pagina | 44184–44184 | 1 |
| 32 | header_pagina | 44185–44185 | 1 |
| 33 | header_pagina | 44186–44186 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=26 (10.36% del bloque, n=251)

---

### [span 1] header_pagina (43936–43936)
```
329
```

### [span 2] catch_all (43937–43962)
```
nes por las que se descartó la prescripción según la ley del país recla-
mante y la aplicación de la pena de muerte, y de que se concedió la
extradición sin juicio previo), en modo alguno puede soslayarse el tra-
tamiento de este tema toda vez que puede originar responsabilidad
internacional del Estado Argentino la omisión de aplicar las normas
internacionales que prohíben conceder la extradición cuando haya
motivos serios para creer que la persona requerida será sometida a
tortura o tratos crueles (arts. 3.1 de la Convención contra la Tortura y
Otros Tratos o Penas Crueles Inhumanos o Degradantes –art. 75,
inc. 22, de la Constitución Nacional y ley 23.338– y 13 de la Conven-
ción Interamericana para Prevenir y Sancionar la Tortura –ley
23.652–).
4º) Que en tales condiciones, la cuestión planteada en la presente
causa resulta sustancialmente análoga a la tratada en el fallo “Bore-
lina” (Fallos: 328:3233, disidencia del suscripto), a cuyos argumentos
y conclusiones corresponde remitirse en razón de brevedad; de modo
tal que resulta inoficioso que la Corte se pronuncie con respecto a los
agravios expresados en el recurso de apelación.
Por ello y oído el señor Procurador Fiscal, se revoca la resolución
de fs. 141/147 y se rechaza el pedido de extradición de Carmen Pozo
Gamarra. Notifíquese y remítanse.
E. RAÚL ZAFFARONI.
Recurso ordinario interpuesto por Carmen María Pozo Gamarra, representada por
el Dr. Roberto H. Polito.
Tribunal de origen: Juzgado Federal de Lomas de Zamora Nº 1.
CAMARA DE COMERCIO, INDUSTRIA Y AGROPECUARIA DE SAN RAFAEL
```

### [span 3] caratula (43963–43963)
```
CAMARA DE COMERCIO, INDUSTRIA Y AGROPECUARIA DE SAN RAFAEL V. PODER EJECUTIVO NACIONAL

```

### [span 4] sumario [1] (43964–43976)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
nes anteriores a la sentencia definitiva. Medidas precautorias.
Si bien las resoluciones sobre medidas precautorias, ya sea que las ordenen,
modifiquen o extingan, no autorizan el otorgamiento del recurso extraordinario,

2533
DE JUSTICIA DE LA NACION
329
ya que no revisten, en principio, el carácter de sentencias definitivas, tal princi-
pio cede cuando los agravios que se invocan revisten gravedad institucional, la
que debe admitirse si la ejecución corresponde a medidas de alcance general que
inciden en actividades ligadas al bienestar común.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] header_pagina (43969–43969)
```
2533
```

### [span 6] header_pagina (43970–43970)
```
DE JUSTICIA DE LA NACION
```

### [span 7] header_pagina (43971–43971)
```
329
```

### [span 8] sumario [2] (43977–43983)
**Header**: MEDIDA CAUTELAR INNOVATIVA.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
MEDIDA CAUTELAR INNOVATIVA.
La medida innovativa es una decisión excepcional dentro de las medidas
precautorias porque altera el estado de hecho o de derecho existente al tiempo de
su dictado, ya que se configura un anticipo de jurisdicción favorable respecto del
fallo final de la causa, lo que justifica una mayor prudencia al apreciar los recaudos
que hacen a su admisibilidad.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 9] sumario [3] (43984–43992)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Sen-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Sen-
tencias arbitrarias. Procedencia del recurso. Valoración de circunstancias de hecho y
prueba.
Corresponde dejar sin efecto la sentencia que mantuvo la orden dirigida al Poder
Ejecutivo Nacional para que se suspenda la ejecución del decreto 1295/03 si la
actora no ofreció prueba alguna tendiente a demostrar el perjuicio que le ocasio-
na a sus miembros el acto estatal atacado ni tampoco el peligro que encierra su
mantenimiento.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 10] sumario [4] (43993–43998)
**Header**: SENTENCIA.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
SENTENCIA.
Los fallos judiciales deben tener fundamentos serios, lo que exige un correcto
análisis de las constancias del expediente, que acrediten los hechos y una razo-
nable conclusión sobre la valoración que le corresponde a la luz del derecho vi-
gente.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 11] sumario [5] (43999–44007)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y
generalidades.
Es improcedente el recurso extraordinario que no se dirige contra una sentencia
definitiva o equiparable a tal (art. 14 de la ley 48) (Disidencia de los Dres. E.
Raúl Zaffaroni y Carmen M. Argibay).

2534
FALLOS DE LA CORTE SUPREMA
329
```

### [span 12] header_pagina (44005–44005)
```
2534
```

### [span 13] header_pagina (44006–44006)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 14] header_pagina (44007–44007)
```
329
```

### [span 15] dictamen (44008–44146)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
A fs. 121/127, la Cámara Federal de Apelaciones de Mendoza con-
firmó lo resuelto por la instancia anterior y, en consecuencia, mantu-
vo la orden dirigida al Poder Ejecutivo Nacional para que se suspenda
la ejecución del decreto 1295/03 hasta tanto se resuelva, en definitiva,
el amparo promovido.
Para así pronunciarse, ratificó la legitimación para obrar de la
Cámara de Comercio, Industria y Agropecuaria de San Rafael en re-
presentación de sus asociados, con sustento en lo dispuesto por el
art. 43, segunda parte, de la Constitución Nacional. En tal sentido,
afirmó que la indebida regulación de la promoción industrial median-
te un decreto de necesidad y urgencia (Nº 1295/03) origina, al menos,
un interés legítimo en el reestablecimiento de los derechos de los co-
merciantes e industriales de las provincias vecinas discriminadas que,
si bien no puede evaluarse en un daño inmediato, directo e indemni-
zable, constituye, en los términos constitucionales, “derecho de inci-
dencia colectiva”.
Negó que la causa sea de la competencia originaria de la Corte
Suprema de Justicia de la Nación pues, por el momento, no se encuen-
tra como actora, demandada o litisconsorte ninguna provincia, según
lo requerido por el art. 117 de la Constitución Nacional.
Estimó, en carácter provisorio para determinar la verosimilitud
del derecho, que el decreto de necesidad y urgencia 1295/03 contravie-
ne el art. 99, inc. 3), de la Constitución Nacional pues no existirían
aquellas razones de excepción y se regularía materia tributaria, obje-
to expresamente prohibido por la norma constitucional.
Por último, respecto del peligro en la demora, aseveró que, de no
accederse a la cautelar, ello producirá efectos irreparables en los
accionantes, ya que la autorización amplia para cambiar de objeto en
el marco de beneficios promocionales otorgados –conforme lo autoriza
el decreto 1295/03– generará un inmediato desequilibrio en la actual
distribución de las actividades y alterará las previsiones industriales

2535
DE JUSTICIA DE LA NACION
329
y comerciales en la zona, en orden a la satisfacción de la competencia
según la composición y relación económica existente.
– II –
A fs. 139/150, la AFIP interpuso el recurso extraordinario que fue
concedido a fs. 157/159.
En primer término, señaló que la decisión ocasiona al Estado Na-
cional un perjuicio irreparable, que incide directa y decisivamente so-
bre el interés de la comunidad al tiempo que resuelve sobre el fondo de
la cuestión en debate pues, al hacer lugar a la cautelar solicitada, an-
ticipa su opinión desfavorable a la validez constitucional de las nor-
mas impugnadas.
Negó que el amparista haya iniciado esta acción en defensa de los
derechos de incidencia colectiva de sus representados, sino que lo hizo
para tutelar derechos subjetivos individuales, de estricta índole patri-
monial y titularidad exclusiva de cada uno de ellos. Esgrimió que a
éstos les corresponde, en todo caso, transitar las vías judiciales que
estimen pertinentes, en tanto acrediten, o al menos invoquen, un per-
juicio efectivo derivado de la aplicación de la norma impugnada.
Cuestionó la existencia de verosimilitud del derecho, pues el de-
creto no produce incrementos en los beneficios otorgados ni permite la
aprobación de nuevos proyectos, sino que únicamente posibilita modi-
ficar el objeto por otro cuyo código comparta los tres primeros dígitos
con el original. Puntualizó que la medida así adoptada resuelve cues-
tiones de orden operativo, para solucionar los conflictos generados por
la instrumentación de las cuentas corrientes computarizadas, pero de
ninguna manera incide en la fecha de puesta en marcha del proyecto
ni en la extensión del período de beneficios.
En lo atinente al peligro en la demora, subrayó que el actor no ha
especificado, en concreto y subjetivamente, las consecuencias irrepa-
rables e irreversibles de la medida cuestionada y ni siquiera ha ofreci-
do prueba tendiente a demostrar sus perjuicios.
En tales condiciones, consideró que la cuestión federal planteada
es trascendente y de gravedad institucional, pues afecta de manera

2536
FALLOS DE LA CORTE SUPREMA
329
directa la percepción de las rentas públicas y compromete institucio-
nes básicas del Estado.
– III –
Tiene dicho la Corte que las resoluciones sobre medidas precau-
torias, ya sea que las ordenen, modifiquen o extingan, no autorizan el
otorgamiento del recurso extraordinario, ya que no revisten, en prin-
cipio, el carácter de sentencias definitivas a que se refiere el art. 14 de
la ley 48 (Fallos: 300:1036; 308:2006, entre otros).
Sin embargo, tal principio cede –entre otros supuestos– cuando los
agravios que se invocan como fundamento de dicho recurso, a más de
cumplir con los recaudos exigibles de acuerdo con la norma citada,
revisten gravedad institucional, tal como sucede en el sub lite. Y esta
última debe admitirse si la ejecución corresponde a medidas de alcan-
ce general que inciden en actividades ligadas al bienestar común, cir-
cunstancia que, por darse en el caso, confiere trascendencia al planteo
constitucional formulado (Fallos: 247:601; 298:732, entre otros).
– IV –
La viabilidad de las medidas precautorias, es sabido, se halla su-
peditada a que se demuestre tanto la verosimilitud del derecho invo-
cado como el peligro en la demora (art. 230 del Código Procesal Civil y
Comercial de la Nación), y que dentro de aquéllas, la innovativa es
una decisión excepcional porque altera el estado de hecho o de derecho
existente al tiempo de su dictado, habida cuenta de que configura un
anticipo de jurisdicción favorable respecto del fallo final de la causa, lo
que justifica una mayor prudencia al apreciar los recaudos que hacen
a su admisibilidad (Fallos: 316:1833; 320:1633; 325:2347, entre mu-
chos otros).
En lo que atañe al sub examine, a mi modo de ver, la medida pre-
cautoria en crisis fue otorgada con el solo respaldo de las afirmaciones
de la actora, las cuales, a su vez, carecen de todo apoyo probatorio.
En tal sentido, respecto del peligro en la demora, el a quo aseveró
que, de no accederse a la cautelar, se producirán efectos irreparables
en los accionantes, por un inmediato desequilibrio en la actual distri-
bución de las actividades y alteración de las previsiones industriales y

2537
DE JUSTICIA DE LA NACION
329
comerciales en la zona, en orden a la satisfacción de la competencia
según la composición y relación económica existente.
Observo que tales afirmaciones omiten toda referencia concreta a
las circunstancias de la causa, sin revelar los motivos ni indicar por
medio de cuales constancias arribó a dicha conclusión. En tales condi-
ciones, es necesario recordar la reiterada exigencia de que los fallos
judiciales tengan fundamentos serios, lo que exige un correcto análi-
sis de las constancias del expediente, que acrediten los hechos y una
razonable conclusión sobre la valoración que le corresponde a la luz
del derecho vigente (Fallos: 303:290; 303:1295).
Desde esta perspectiva, es importante poner de relieve que la actora
no ha ofrecido prueba alguna tendiente a demostrar el perjuicio que le
ocasiona a sus miembros el acto estatal atacado ni tampoco el peligro
que encierra su mantenimiento (cfr. pto. XII, fs. 50).
En tales condiciones, es mi opinión que la decisión apelada resulta
descalificable como acto judicial válido, a la luz de la conocida doctrina
de la Corte elaborada en torno a las sentencias arbitrarias (Fallos:
312:1150; 314:740; 318:643; 324:2009, entre otros).
A ello cabe agregar, por último, que de concederse la medida se
obtendría, por anticipado, el propósito que sólo se podría lograr con la
admisión de la demanda, extremo, de por sí, inaceptable (Fallos:
307:1804 y su cita).
– V –
En virtud de lo aquí dicho, opino que corresponde dejar sin efecto
la sentencia apelada en cuanto fue materia de recurso extraordinario.
Buenos Aires, 17 de noviembre de 2005. Ricardo O. Bausset.
```

### [span 16] header_pagina (44043–44043)
```
2535
```

### [span 17] header_pagina (44044–44044)
```
DE JUSTICIA DE LA NACION
```

### [span 18] header_pagina (44045–44045)
```
329
```

### [span 19] header_pagina (44080–44080)
```
2536
```

### [span 20] header_pagina (44081–44081)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 21] header_pagina (44082–44082)
```
329
```

### [span 22] header_pagina (44118–44118)
```
2537
```

### [span 23] header_pagina (44119–44119)
```
DE JUSTICIA DE LA NACION
```

### [span 24] header_pagina (44120–44120)
```
329
```

### [span 25] cuerpo_mayoria (44147–44165)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 11 de julio de 2006.
Vistos los autos: “Cámara de Comercio Ind. y Agrop. de San Rafael
c/ PEN s/ acción de amparo”.

2538
FALLOS DE LA CORTE SUPREMA
329
Considerando:
Que las cuestiones planteadas han sido adecuadamente tratadas
en el dictamen del señor Procurador Fiscal subrogante, cuyos funda-
mentos son compartidos por el Tribunal, y a los que corresponde remi-
tirse por motivos de brevedad. Ello sin perjuicio de que corresponde
precisar que el recurso extraordinario no ha sido interpuesto por la
AFIP sino por el Estado Nacional.
Por ello, de conformidad con lo dictaminado por el señor Procura-
dor Fiscal subrogante, se declara formalmente admisible el recurso
extraordinario y se deja sin efecto la resolución apelada. Con costas.
Notifíquese y devuélvase.
```

### [span 26] header_pagina (44152–44152)
```
2538
```

### [span 27] header_pagina (44153–44153)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 28] header_pagina (44154–44154)
```
329
```

### [span 29] firma (44166–44168)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS
S. FAYT — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI (en disidencia) —
RICARDO LUIS LORENZETTI — CARMEN M. ARGIBAY (en disidencia).
```

### [span 30] disidencia (44169–44186)
**Header**: DISIDENCIA DE LOS SEÑORES MINISTROS
```
DISIDENCIA DE LOS SEÑORES MINISTROS
DOCTORES DON E. RAÚL ZAFFARONI Y DOÑA CARMEN M. ARGIBAY
Considerando:
Que el recurso extraordinario no se dirige contra una sentencia
definitiva o equiparable a tal (art. 14 de la ley 48).
Por ello, y habiendo dictaminado el señor Procurador Fiscal
subrogante, se declara improcedente el recurso extraordinario inter-
puesto. Notifíquese y devuélvase.
E. RAÚL ZAFFARONI — CARMEN M. ARGIBAY.
Recurso extraordinario interpuesto por el Estado Nacional, representado por el Dr.
José Miguel Abdala, con el patrocinio del Dr. José Blas Made.
Tribunal de origen: Cámara Federal de Apelaciones de Mendoza.
Tribunales que intervinieron con anterioridad: Juzgado Federal de San Rafael,
Mendoza.

2539
DE JUSTICIA DE LA NACION
329
```

### [span 31] header_pagina (44184–44184)
```
2539
```

### [span 32] header_pagina (44185–44185)
```
DE JUSTICIA DE LA NACION
```

### [span 33] header_pagina (44186–44186)
```
329
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=44186 | linea_inicio_proximo_caso=44186 | delta=-1
**Alertas**: `solapado_con_proximo`


---

## 330_p1427 — Marchal, Juan

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 1427–1436 | Página consultada: 1436
- Líneas catálogo: 3908–4245 | Línea fin real: 4251 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 3908–3908 | 1 |
| 2 | catch_all | 3909–3931 | 23 |
| 3 | caratula | 3932–3932 | 1 |
| 4 | sumario [1] | 3933–3946 | 14 |
| 5 | header_pagina | 3939–3939 | 1 |
| 6 | header_pagina | 3940–3940 | 1 |
| 7 | header_pagina | 3941–3941 | 1 |
| 8 | sumario [2] | 3947–3950 | 4 |
| 9 | sumario [3] | 3951–3956 | 6 |
| 10 | dictamen | 3957–4060 | 104 |
| 11 | header_pagina | 3972–3972 | 1 |
| 12 | header_pagina | 3973–3973 | 1 |
| 13 | header_pagina | 3974–3974 | 1 |
| 14 | header_pagina | 4011–4011 | 1 |
| 15 | header_pagina | 4012–4012 | 1 |
| 16 | header_pagina | 4013–4013 | 1 |
| 17 | header_pagina | 4052–4052 | 1 |
| 18 | header_pagina | 4053–4053 | 1 |
| 19 | header_pagina | 4054–4054 | 1 |
| 20 | cuerpo_mayoria | 4061–4136 | 76 |
| 21 | header_pagina | 4085–4085 | 1 |
| 22 | header_pagina | 4086–4086 | 1 |
| 23 | header_pagina | 4087–4087 | 1 |
| 24 | header_pagina | 4127–4127 | 1 |
| 25 | header_pagina | 4128–4128 | 1 |
| 26 | header_pagina | 4129–4129 | 1 |
| 27 | firma | 4137–4139 | 3 |
| 28 | catch_all | 4140–4140 | 1 |
| 29 | voto | 4141–4235 | 95 |
| 30 | header_pagina | 4164–4164 | 1 |
| 31 | header_pagina | 4165–4165 | 1 |
| 32 | header_pagina | 4166–4166 | 1 |
| 33 | header_pagina | 4208–4208 | 1 |
| 34 | header_pagina | 4209–4209 | 1 |
| 35 | header_pagina | 4210–4210 | 1 |
| 36 | disidencia | 4236–4251 | 16 |
| 37 | header_pagina | 4244–4244 | 1 |
| 38 | header_pagina | 4245–4245 | 1 |
| 39 | header_pagina | 4246–4246 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=24 (6.98% del bloque, n=344)

---

### [span 1] header_pagina (3908–3908)
```
330
```

### [span 2] catch_all (3909–3931)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 10 de abril de 2007.
Vistos los autos: “Inspección General de Justicia c/ Empresa Na-
viera Petrolera Atlántica S.A.”.
Considerando:
Que las cuestiones planteadas han sido adecuadamente tratadas
en el dictamen del señor Procurador General de la Nación que el Tri-
bunal comparte y a cuyos fundamentos corresponde remitirse a fin de
evitar reiteraciones innecesarias.
Por ello, de conformidad con lo dictaminado por el señor Procura-
dor General, se declara procedente el recurso extraordinario y se deja
sin efecto la sentencia apelada. Con costas. Notifíquese y devuélvase
al tribunal de origen a fin de que, por quien corresponda, se dicte un
nuevo fallo de acuerdo con lo expresado.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI.
Recurso extraordinario interpuesto por la Inspección General de Justicia, repre-
sentada por la Dra. Susana G. Junqueira, con el patrocinio de la Dra. Adriana E.
Vicente.
Traslado contestado por la Empresa Naviera Petrolera Atlántida S.A., representa-
da por la Dra. Alicia J. Stratta.
Tribunal de origen: Cámara Nacional de Apelaciones en lo Comercial, Sala D.
Tribunales que intervinieron con anterioridad: Juzgado Nacional en lo Comercial.
```

### [span 3] caratula (3932–3932)
```
JUAN MARCHAL
```

### [span 4] sumario [1] (3933–3946)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Procedencia del recurso. Exceso ritual manifiesto.
Corresponde dejar sin efecto la sentencia que incurrió en un excesivo rigor for-
mal pues, con estricto apego a las limitaciones establecidas por el ordenamiento
adjetivo local, omitió examinar y resolver la cuestión constitucional planteada

1428
FALLOS DE LA CORTE SUPREMA
330
oportunamente en la instancia casatoria y que estaba claramente involucrada,
como lo era la de determinar si el art. 8.2.h de la Convención Americana sobre
Derechos Humanos resultaba o no aplicable a la sanción de clausura impuesta
por la infracción prevista en el art. 63, inc. 3º, del Código Fiscal de la Provincia
de Buenos Aires (t.o. 1996).
```

### [span 5] header_pagina (3939–3939)
```
1428
```

### [span 6] header_pagina (3940–3940)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 7] header_pagina (3941–3941)
```
330
```

### [span 8] sumario [2] (3947–3950)
**Header**: CORTE INTERAMERICANA DE DERECHOS HUMANOS.
**Atribución**: (sin atribución detectada)
```
CORTE INTERAMERICANA DE DERECHOS HUMANOS.
La jurisprudencia de la Corte Interamericana de Derechos Humanos debe servir
de guía para la interpretación de los preceptos convencionales (Voto de los Dres.
Carlos S. Fayt y E. Raúl Zaffaroni).
```

### [span 9] sumario [3] (3951–3956)
**Header**: RECURSO EXTRAORDINARIO: Principios generales.
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Principios generales.
Es inadmisible (art. 280 del Código Procesal Civil y Comercial de la Nación) el
recurso extraordinario interpuesto contra el pronunciamiento que denegó los
recursos contra el fallo que confirmó la sanción de clausura impuesta por la in-
fracción prevista en el art. 63, inc. 3º, del Código Fiscal de la Provincia de Bue-
nos Aires (t.o. 1996) (Disidencia de la Dra. Carmen M. Argibay).
```

### [span 10] dictamen (3957–4060)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
La Suprema Corte de Justicia de la Provincia de Buenos Aires
desestimó el recurso extraordinario de inaplicabilidad de ley que Juan
Héctor Marchal interpuso contra el auto mediante el cual, la Sala II
del Tribunal de Casación, rechazó el recurso de casación planteado
contra el fallo del Juzgado en lo Criminal y Correccional de Transición
Nº 2 de la ciudad de Mar del Plata que confirmó la sanción de clausura
por tres días impuesta por la Dirección Provincial de Rentas sobre su
establecimiento comercial, en el marco del sumario instruido por in-
fracción al artículo 63, inciso 3º, del código fiscal de esa provincia.
Contra ese pronunciamiento, Marchal interpuso recurso extraor-
dinario federal, que fue concedido a fs. 59.

1429
DE JUSTICIA DE LA NACION
330
– II –
El apelante tacha de arbitrario el fallo, al considerar que en él se
omitió el tratamiento de argumentos conducentes a la solución del
caso, entre los que se encuentra el relativo a la afectación del derecho
de raigambre constitucional de recurrir ante un tribunal superior (ar-
tículo 8, apartado 2, inciso “h”, de la Convención Americana sobre
Derechos Humanos, y artículo 14, apartado 5, del Pacto Internacional
de Derechos Civiles y Políticos) con motivo de la denegación del acceso
a la instancia casatoria local.
Asimismo, sostiene que igual vicio afecta al pronunciamiento en
cuanto la Corte local habría examinado con excesivo rigor formal los
requisitos de procedencia del recurso de inaplicabilidad de ley. En ese
sentido, expresa que el precepto legal que regula esa vía impugnativa
(artículo 494 del Código Procesal Penal de la Provincia de Buenos Ai-
res) es irrazonable, en tanto circunscribe la competencia apelada del
superior tribunal provincial al examen de la aplicación de ley
sustantiva; y alega que, como consecuencia de la interpretación literal
de esa norma, el a quo soslayó el tratamiento de las cuestiones federa-
les planteadas.
Por último, aduce que la decisión vulnera el citado derecho de re-
currir ante un tribunal superior, cuya aplicación postula con base en
la naturaleza penal de la sanción de clausura impuesta.
– III –
Tiene dicho V. E. que las resoluciones de los superiores tribunales
de provincia por las cuales deciden acerca de los recursos extraordina-
rios de carácter local que se interponen ante ellos no son, por princi-
pio, revisables en esta instancia extraordinaria (Fallos: 302:1134;
308:1253; 311:519 y 926) y la tacha de arbitrariedad a su respecto es
de aplicación particularmente restringida (Fallos: 302:418; 305:515;
306:501; 307:1100; 313:493; y sentencia del 11 de junio de 1998 dicta-
da en los autos V. 250, L. XXXIII, “Valdez, Oscar Eugenio s/ homici-
dio”, considerando 7º).
En mi opinión, esa doctrina resulta aplicable al sub lite en tanto
las cuestiones que se pretende someter a decisión de la Corte se vincu-
lan a la interpretación y aplicación de normas procesales, y el fallo

1430
FALLOS DE LA CORTE SUPREMA
330
impugnado posee fundamentos suficientes que lo ponen a salvo de la
tacha de arbitrariedad.
Pienso que ello es así por cuanto el a quo denegó el recurso de la
especialidad fundado en que el caso no constituye alguno de los su-
puestos que autorizan su procedencia –de acuerdo con la regulación
pertinente, cuya constitucionalidad no fue oportunamente cuestiona-
da– y en que no se advierte la afectación constitucional alegada por el
recurrente, cuyos agravios estarían dirigidos a criticar el tratamiento
dado a cuestiones de índole estrictamente formal.
Por otra parte –aunque con evidente vinculación a la materia an-
tes analizada– aprecio que el agravio referente al derecho a recurrir
ante un tribunal superior carece de la fundamentación autónoma que
exige el artículo 15 de la ley 48, pues en el recurso extraordinario no se
demuestra la razón por la cual aquel derecho sería aplicable en el sub
examine, a la vez que se reiteran asertos vertidos en instancias ante-
riores que, como se dijo, fueron desechados con base en argumentos
vinculados a cuestiones de orden ritual.
En ese sentido, observo que el apelante asienta su pretensión ex-
clusivamente en la supuesta naturaleza “penal” de la sanción de clau-
sura prevista en el código fiscal provincial, a cuyo efecto invoca el pre-
cedente de la Corte publicado en Fallos: 321:1043, pero omite explicar
por qué la atribución de carácter represivo a esa sanción implicaría
simultáneamente el reconocimiento de naturaleza delictiva a la in-
fracción que le da origen, al tiempo que tampoco se hace cargo de los
términos en que los instrumentos internacionales que invoca regulan
la aplicación de aquel derecho, ni del alcance que V. E. le reconoció en
el pronunciamiento publicado en Fallos: 323:1787 –reiterado en Fa-
llos: 325:2711, y en la sentencia del 7 de septiembre de 2004 dictada
en los autos A. 421, L. XL, “Auchán Argentina S. A. s/ infr. art. 9º ley
22.802”– en cuanto se sostuvo que el derecho de recurrir la resolución
ante un tribunal superior se halla supeditado a la existencia de un
fallo final dictado contra persona “inculpada de delito”, por lo que re-
sultan ajenas a su ámbito las resoluciones judiciales que condenen o
absuelvan con motivo de la imputación de faltas, contravenciones o
infracciones administrativas.
De ese modo, al no haberse demostrado la existencia de una cues-
tión federal, ni de un supuesto de arbitrariedad de sentencia, no con-

1431
DE JUSTICIA DE LA NACION
330
curren en el sub judice los extremos que condicionan la procedencia de
la doctrina de Fallos: 308:490 y 311:2478.
– IV –
Por todo lo expuesto, opino que V. E. debe declarar improcedente
el recurso extraordinario interpuesto a fs. 37/51. Buenos Aires, 29 de
noviembre de 2005. Eduardo Ezequiel Casal.
```

### [span 11] header_pagina (3972–3972)
```
1429
```

### [span 12] header_pagina (3973–3973)
```
DE JUSTICIA DE LA NACION
```

### [span 13] header_pagina (3974–3974)
```
330
```

### [span 14] header_pagina (4011–4011)
```
1430
```

### [span 15] header_pagina (4012–4012)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 16] header_pagina (4013–4013)
```
330
```

### [span 17] header_pagina (4052–4052)
```
1431
```

### [span 18] header_pagina (4053–4053)
```
DE JUSTICIA DE LA NACION
```

### [span 19] header_pagina (4054–4054)
```
330
```

### [span 20] cuerpo_mayoria (4061–4136)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 10 de abril de 2007.
Vistos los autos: “Marchal, Juan s/ apelación”.
Considerando:
1º) Que el recurso extraordinario concedido a fs. 59/60, se interpu-
so contra la sentencia de la Suprema Corte de Justicia de la Provincia
de Buenos Aires que desestimó el recurso de inaplicabilidad de ley
interpuesto contra la resolución del Tribunal de Casación Penal (Sala
II) que declaró inadmisible el recurso de casación deducido contra la
sentencia del Juzgado en lo Criminal y Correccional de Transición Nº 2
de la ciudad de Mar del Plata que había confirmado la sanción de tres
días de clausura impuesta por la Dirección Provincial de Rentas al
establecimiento comercial de Juan H. Marchal por la infracción pre-
vista en el art. 63, inc. 3º, del Código Fiscal de esa provincia (T.O. 1996).
2º) Que en el recurso de casación el interesado alegó la inexisten-
cia de la infracción y, en lo que al caso interesa, arguyó en favor de la
procedencia de esa vía recursiva por considerar que el art. 66 del Có-
digo Fiscal –donde se establece que es inapelable la decisión del juez
que resuelve la apelación deducida contra la sanción de clausura– re-
sulta violatorio de la Convención Americana sobre Derechos Huma-
nos en cuanto consagra el derecho a la doble instancia en materia
penal, toda vez que la Corte Suprema le había reconocido naturaleza
criminal a la sanción de clausura por cuestiones fiscales.

1432
FALLOS DE LA CORTE SUPREMA
330
3º) Que el tribunal de casación no hizo lugar al pedido de revisión
de la sanción por considerar que “...el ámbito de aplicación del recurso
de casación se encuentra legalmente delimitado por la normativa pre-
vista por la ley 11.922, y sólo aparece viable respecto de sentencias
definitivas cuando resulten dictadas por órganos jurisdiccionales en el
marco de esa ley y en razón de la comisión de conductas ilícitas que
configuren delitos (art. 421 del C.P.P.). La ley 10.397/96 y su decreto
reglamentario 9.394/86, (Código Fiscal), establece un sistema propio
para el juzgamiento de las infracciones fiscales cometidas en la Juris-
dicción de la Provincia de Buenos Aires, en el que la resolución dictada
por el Director de la Dirección Técnica Tributaria de la Dirección Pro-
vincial de Rentas, resulta apelable ante el Juez de Primera Instancia
en lo Criminal y Correccional, rigiendo lo dispuesto en el artículo 66 y
ccdtes. del Código Fiscal citado. El hecho de que la ley 10.397/96
–ordenamiento aplicable al sub lite– prevea un control judicial sufi-
ciente para los actos administrativos (art. 63, inc. 3º C.F.), no puede
significar que las faltas cuenten con el mismo marco impugnativo que
los propios delitos, situación ésta que provocaría que las faltas posean
más instancias revisoras que estos últimos”.
4º) Que esta decisión fue llevada a conocimiento del superior tri-
bunal provincial, que desestimó el recurso de inaplicabilidad de ley
por considerar que no se daban en el caso las hipótesis en las que
procedía la impugnación deducida (inobservancia o errónea aplicación
de la ley sustantiva o doctrina legal, según el art. 494 del código proce-
sal penal provincial), y que si bien se había alegado violación de ga-
rantías contempladas en la Constitución Nacional, en realidad los agra-
vios se dirigían a cuestionar el tratamiento dado a cuestiones de orden
procesal (fs. 28/33).
5º) Que de esta manera, al resolver con estricto apego a las limita-
ciones establecidas por el ordenamiento adjetivo local, el a quo omitió
examinar y resolver la cuestión constitucional que había sido plantea-
da oportunamente en la instancia casatoria y que estaba claramente
involucrada en el caso, como lo era la de determinar si el art. 8.2.h de
la Convención Americana sobre Derechos Humanos resultaba o no
aplicable al caso de autos.
6º) Que, en tales condiciones, el pronunciamiento apelado incurrió
en un excesivo rigor formal que frustró el debido control jurisdiccional
del efectivo cumplimiento de los derechos reconocidos por la Conven-

1433
DE JUSTICIA DE LA NACION
330
ción, por lo que corresponde su descalificación como acto judicial váli-
do, sin que esto implique emitir juicio sobre el fondo del asunto.
Por ello y oído el señor Procurador Fiscal, se declara procedente el
recurso extraordinario y se deja sin efecto la sentencia apelada. Hága-
se saber y devuélvanse las actuaciones a la Suprema Corte de Justicia
de la Provincia de Buenos Aires para que se dicte un nuevo pronuncia-
miento con arreglo a lo expuesto.
```

### [span 21] header_pagina (4085–4085)
```
1432
```

### [span 22] header_pagina (4086–4086)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 23] header_pagina (4087–4087)
```
330
```

### [span 24] header_pagina (4127–4127)
```
1433
```

### [span 25] header_pagina (4128–4128)
```
DE JUSTICIA DE LA NACION
```

### [span 26] header_pagina (4129–4129)
```
330
```

### [span 27] firma (4137–4139)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT (según su voto) — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS
MAQUEDA — E. RAÚL ZAFFARONI (según su voto) — CARMEN M. ARGIBAY
```

### [span 28] catch_all (4140–4140)
```
(en disidencia).
```

### [span 29] voto (4141–4235)
**Header**: VOTO DE LOS SEÑORES MINISTROS
```
VOTO DE LOS SEÑORES MINISTROS
DOCTORES DON CARLOS S. FAYT Y DON E. RAÚL ZAFFARONI
Considerando:
1º) Que el recurso extraordinario concedido a fs. 59/60, se interpu-
so contra la sentencia de la Suprema Corte de Justicia de la Provincia
de Buenos Aires que desestimó el recurso de inaplicabilidad de ley
interpuesto contra la resolución del Tribunal de Casación Penal (Sala
II) que declaró inadmisible el recurso de casación deducido contra la
sentencia del Juzgado en lo Criminal y Correccional de Transición Nº 2
de la ciudad de Mar del Plata que había confirmado la sanción de tres
días de clausura impuesta por la Dirección Provincial de Rentas al
establecimiento comercial de Juan H. Marchal por la infracción pre-
vista en el art. 63, inc. 3º, del Código Fiscal de esa provincia (T.O. 1996).
2º) Que en el recurso de casación el interesado alegó la inexisten-
cia de la infracción y, en lo que al caso interesa, arguyó en favor de la
procedencia de esa vía recursiva por considerar que el art. 66 del Có-
digo Fiscal –donde se establece que es inapelable la decisión del juez
que resuelve la apelación deducida contra la sanción de clausura– re-
sulta violatorio de la Convención Americana sobre Derechos Huma-
nos en cuanto consagra el derecho a la doble instancia en materia
penal, toda vez que la Corte Suprema le había reconocido naturaleza
criminal a la sanción de clausura por cuestiones fiscales.

1434
FALLOS DE LA CORTE SUPREMA
330
3º) Que el tribunal de casación no hizo lugar al pedido de revisión
de la sanción por considerar que “...el ámbito de aplicación del recurso
de casación se encuentra legalmente delimitado por la normativa pre-
vista por la ley 11.922, y sólo aparece viable respecto de sentencias
definitivas cuando resulten dictadas por órganos jurisdiccionales en el
marco de esa ley y en razón de la comisión de conductas ilícitas que
configuren delitos (art. 421 del C.P.P.). La ley 10.397/96 y su decreto
reglamentario 9.394/86, (Código Fiscal), establece un sistema propio
para el juzgamiento de las infracciones fiscales cometidas en la Juris-
dicción de la Provincia de Buenos Aires, en el que la resolución dictada
por el Director de la Dirección Técnica Tributaria de la Dirección Pro-
vincial de Rentas, resulta apelable ante el Juez de Primera Instancia
en lo Criminal y Correccional, rigiendo lo dispuesto en el artículo 66 y
ccdtes. del Código Fiscal citado. El hecho de que la ley 10.397/96
–ordenamiento aplicable al sub lite– prevea un control judicial sufi-
ciente para los actos administrativos (art. 63, inc. 3º C.F.), no puede
significar que las faltas cuenten con el mismo marco impugnativo que
los propios delitos, situación ésta que provocaría que las faltas posean
más instancias revisoras que estos últimos”.
4º) Que esta decisión fue llevada a conocimiento del superior tri-
bunal provincial, que desestimó el recurso de inaplicabilidad de ley
por considerar que no se daban en el caso las hipótesis en las que
procedía la impugnación deducida (inobservancia o errónea aplicación
de la ley sustantiva o doctrina legal, según el art. 494 del código proce-
sal penal provincial), y que si bien se había alegado violación de ga-
rantías contempladas en la Constitución Nacional, en realidad los agra-
vios se dirigían a cuestionar el tratamiento dado a cuestiones de orden
procesal (fs. 28/33).
5º) Que de esta manera, al resolver con estricto apego a las limita-
ciones establecidas en el ordenamiento adjetivo local, el a quo omitió
examinar y resolver la cuestión constitucional que había sido plantea-
da oportunamente en la instancia casatoria y que estaba claramente
involucrada en el caso, como lo era la de determinar si el art. 8.2.h de
la Convención Americana sobre Derechos Humanos resultaba o no
aplicable al caso de autos. Más aún, la pertinencia de esta cuestión
debió haber sido analizada a la luz de la jurisprudencia de la Corte
Interamericana de Derechos Humanos pues, siendo que ella debe ser-
vir de guía para la interpretación de esos preceptos convencionales, en
la sentencia dictada el 31 de enero de 2001 en el “Caso del Tribunal
Constitucional” se sostuvo lo siguiente:

1435
DE JUSTICIA DE LA NACION
330
69. Si bien el artículo 8 de la Convención Americana se titula “Ga-
rantías Judiciales”, su aplicación no se limita a los recursos judiciales
en sentido estricto, “sino el conjunto de requisitos que deben observar-
se en las instancias procesales” a efectos de que las personas puedan
defenderse adecuadamente ante cualquier tipo de acto emanado del
Estado que pueda afectar sus derechos.
70. Ya la Corte ha dejado establecido que a pesar de que el citado
artículo no especifica garantías mínimas en materias que conciernen a
la determinación de los derechos y obligaciones de orden civil, laboral,
fiscal o de cualquier otro carácter, el elenco de garantías mínimas es-
tablecido en el numeral 2 del mismo precepto se aplica también a esos
órdenes y, por ende, en ese tipo de materias el individuo tiene también
el derecho, en general, al debido proceso que se aplica en materia pe-
nal.
6º) Que, en tales condiciones, el pronunciamiento apelado incurrió
en un excesivo rigor formal que frustró el debido control jurisdiccional
del efectivo cumplimiento de los derechos reconocidos por la Conven-
ción, por lo que corresponde su descalificación como acto judicial váli-
do, sin que esto implique emitir juicio sobre el fondo del asunto.
Por ello y oído el señor Procurador Fiscal, se declara procedente el
recurso extraordinario y se deja sin efecto la sentencia apelada. Hága-
se saber y devuélvanse las actuaciones a la Suprema Corte de Justicia
de la Provincia de Buenos Aires para que se dicte un nuevo pronuncia-
miento con arreglo a lo expuesto.
CARLOS S. FAYT — E. RAÚL ZAFFARONI.
```

### [span 30] header_pagina (4164–4164)
```
1434
```

### [span 31] header_pagina (4165–4165)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 32] header_pagina (4166–4166)
```
330
```

### [span 33] header_pagina (4208–4208)
```
1435
```

### [span 34] header_pagina (4209–4209)
```
DE JUSTICIA DE LA NACION
```

### [span 35] header_pagina (4210–4210)
```
330
```

### [span 36] disidencia (4236–4251)
**Header**: DISIDENCIA DE LA SEÑORA
```
DISIDENCIA DE LA SEÑORA
MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY
Considerando:
Que el recurso extraordinario es inadmisible (art. 280 del Código
Procesal Civil y Comercial de la Nación).
Por ello, se lo declara mal concedido. Hágase saber y devuélvase.
CARMEN M. ARGIBAY.

1436
FALLOS DE LA CORTE SUPREMA
330
Recurso extraordinario interpuesto por Juan H. Marchal, con el patrocinio del Dr.
Marcos Jaureguiberry.
Traslado contestado por la Fiscalía de Estado de la Provincia de Buenos Aires,
representada por el Dr. Martín Jorge Lasarte.
Tribunal de origen: Suprema Corte de Justicia de la Provincia de Buenos Aires.
```

### [span 37] header_pagina (4244–4244)
```
1436
```

### [span 38] header_pagina (4245–4245)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 39] header_pagina (4246–4246)
```
330
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=4251 | linea_inicio_proximo_caso=4246 | delta=-6
**Alertas**: `solapado_con_proximo`


---

## 330_p1383 — Banco Patagónico –en liquidación– c/ Maripez S.A. | Maripez S.A. (Banco Patagónico –en liquidación– c/) | (3) Banco Pata

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 1383–1389 | Página consultada: 1389
- Líneas catálogo: 2270–2495 | Línea fin real: 2496 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 2270–2270 | 1 |
| 2 | catch_all | 2271–2280 | 10 |
| 3 | caratula | 2281–2281 | 1 |
| 4 | sumario [1] | 2282–2290 | 9 |
| 5 | sumario [2] | 2291–2300 | 10 |
| 6 | sumario [3] | 2301–2311 | 11 |
| 7 | header_pagina | 2306–2306 | 1 |
| 8 | header_pagina | 2307–2307 | 1 |
| 9 | header_pagina | 2308–2308 | 1 |
| 10 | dictamen | 2312–2402 | 91 |
| 11 | header_pagina | 2341–2341 | 1 |
| 12 | header_pagina | 2342–2342 | 1 |
| 13 | header_pagina | 2343–2343 | 1 |
| 14 | header_pagina | 2382–2382 | 1 |
| 15 | header_pagina | 2383–2383 | 1 |
| 16 | header_pagina | 2384–2384 | 1 |
| 17 | cuerpo_mayoria | 2403–2484 | 82 |
| 18 | header_pagina | 2415–2415 | 1 |
| 19 | header_pagina | 2416–2416 | 1 |
| 20 | header_pagina | 2417–2417 | 1 |
| 21 | header_pagina | 2457–2457 | 1 |
| 22 | header_pagina | 2458–2458 | 1 |
| 23 | header_pagina | 2459–2459 | 1 |
| 24 | firma | 2485–2486 | 2 |
| 25 | catch_all | 2487–2493 | 7 |
| 26 | header_pagina | 2494–2494 | 1 |
| 27 | header_pagina | 2495–2495 | 1 |
| 28 | header_pagina | 2496–2496 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=17 (7.49% del bloque, n=227)

---

### [span 1] header_pagina (2270–2270)
```
330
```

### [span 2] catch_all (2271–2280)
```
Recursos extraordinarios interpuestos por la Dra. Alejandra M. Gils Carbo fiscal
general ante la Cámara Nacional de Apelaciones en lo Comercial y Farina
Ingrid Pilewski, Ivón Denise Pilewski, Fabrizio Gastón Pilewski y Jonathan
Pilewski, con el patrocinio del Dr. Fernando Zito.
Traslado contestado por Alberto José Pérez –síndico– patrocinado por el Dr. Javier
Héctor Conde.
Tribunal de origen: Sala D de la Cámara Nacional de Apelaciones en lo Comer-
cial.
Tribunales que intervinieron con anterioridad: Juzgado Nacional de Primera Ins-
tancia en lo Comercial Nº 13 secretaría Nº 26.
```

### [span 3] caratula (2281–2281)
```
BANCO PATAGONICO –EN LIQUIDACIÓN– V. MARIPEZ S.A.
```

### [span 4] sumario [1] (2282–2290)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Interpre-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Interpre-
tación de normas locales de procedimientos. Doble instancia y recursos.
Los agravios suscitan cuestión federal, pues aunque remiten al análisis de as-
pectos vinculados con la improcedencia de los recursos extraordinarios en el or-
den provincial, cuestión ajena como regla y por su naturaleza, al remedio federal
del art. 14 de la ley 48, tal circunstancia no constituye óbice decisivo para invali-
dar lo resuelto cuando el tribunal local no ha dado sustento suficiente a su deci-
sión y cuando ha omitido tratar planteos oportunamente propuestos y conducen-
tes para la correcta solución del caso.
```

### [span 5] sumario [2] (2291–2300)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Procedencia del recurso. Falta de fundamentación suficiente.
Corresponde descalificar la sentencia por la que se deniegan los extraordinarios
locales con el único fundamento de que los pronunciamientos recaídos en la eta-
pa de ejecución no son susceptibles de ser recurridos por la vía intentada, toda
vez que omitió considerar y pronunciarse acerca de cuestiones relevantes para
resolver la cuestión debatida –una causa en trámite en la cual se discute la exis-
tencia de un convenio de renuncia al cobro de honorarios– y que eventualmente
constituirían supuestos de excepción a la regla enunciada para rechazar aqué-
llos.
```

### [span 6] sumario [3] (2301–2311)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
nes posteriores a la sentencia.
Corresponde hacer excepción al principio según el cual las decisiones adoptadas
en la etapa de ejecución de sentencia no configuran la sentencia definitiva reque-

1384
FALLOS DE LA CORTE SUPREMA
330
rida por el art. 14 de la ley 48 cuando lo decidido provoca un agravio de imposible
o insuficiente reparación ulterior, tal como la afectación del derecho de defensa
ligado a la existencia misma de la causa de la obligación.
```

### [span 7] header_pagina (2306–2306)
```
1384
```

### [span 8] header_pagina (2307–2307)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] header_pagina (2308–2308)
```
330
```

### [span 10] dictamen (2312–2402)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
A fs. 826, la Suprema Corte de Justicia de la Provincia de Buenos
Aires desestimó el recurso de queja interpuesto por el Banco Central
de la República Argentina (BCRA, en adelante), con fundamento en
que los pronunciamientos recaídos en la etapa de ejecución no son
susceptibles de ser recurridos por la vía de los arts. 278 y 296 del Có-
digo Procesal Civil y Comercial, pues, por ser posteriores a la senten-
cia definitiva, no reúnen la calidad requerida por dichas normas. Aña-
dió que tales cuestiones, en cuanto corresponden al cumplimiento de
lo ya decidido y firme, deben quedar concluidas en la instancia ordina-
ria.
– II –
Disconforme, el BCRA interpuso el recurso extraordinario de
fs. 833/845, con fundamento en que la sentencia es arbitraria porque
se sustenta en afirmaciones dogmáticas, es contradictoria, omite el
tratamiento de cuestiones esenciales planteadas, se aparta de las nor-
mas procesales aplicables y de las constancias de la causa. Añade que
es asimilable a sentencia definitiva, en tanto no dispone de otra vía
para plantear sus agravios.
Sostiene que el tribunal, al denegar los recursos extraordinarios
de nulidad e inaplicabilidad de ley, confirmó lo resuelto a fs. 75/76,
que mandó llevar adelante la ejecución sin considerar el pronuncia-
miento de la Corte Suprema de Justicia de la Nación del 7 de septiem-
bre de 1999 en los autos principales “Banco Patagónico S.A. (su quie-
bra) c/ Marypez S.A. s/ ejecución” – Expte. Nº 65.273 y, por ello, lo
priva definitivamente de ejercer la defensa de la renuncia al cobro de

1385
DE JUSTICIA DE LA NACION
330
honorarios realizada por el doctor Monterisi, cuestión que se encuen-
tra pendiente de resolución en los autos “Monterisi, Ricardo Domingo
c/ Banco Central de la República Argentina s/ incidente de ejecución
de honorarios” – Expte. Nº 68.910. En este sentido, reitera que el juz-
gador incurre en arbitrariedad, pues se aparta de lo resuelto en las
mismas sentencias que dice ejecutar, así como también de las normas
procesales aplicables al caso y quiebra el verdadero alcance de la cosa
juzgada que emana del fallo dictado por V.E. a fs. 445 del Expte.
Nº 65.273. Expresa que dichos pronunciamientos (fs. 12 y 15/16) lo
único que resolvieron fue el carácter de legitimado pasivo del BCRA
frente a los honorarios regulados al letrado en los términos del art. 50,
inc. c) de la ley 22.529, pero de ellos no se puede derivar la pérdida de
las defensas que pudiera oponer respecto a la pretensión de cobro,
pues no existió debate alguno con relación a este punto.
Asimismo, destaca que la ejecución que aquí se pretende llevar
adelante importa un palmario apartamiento de lo resuelto con autori-
dad de cosa juzgada, porque con posterioridad a la sentencia dictada a
fs. 281 en el Expte. Nº 65.273 ya citado, el Alto Tribunal dictó otra a
fs. 445, donde expresamente se manifestó respecto al derecho al cobro
de los honorarios y sostuvo que no existía sentencia definitiva pues
ello debía resolverse en el trámite abierto de ejecución en el cual esta
cuestión había sido introducida (fs. 113/116 del Expte. Nº 68.910).
– III –
Ante todo, cabe señalar que, con arreglo a lo previsto en el art. 14
de la ley 48, siempre que esté en tela de juicio la inteligencia de un
pronunciamiento del Tribunal dictado en la misma causa, en que el
recurrente funda el derecho que estima asistirle, se configura una hi-
pótesis que hace formalmente viable el recurso extraordinario (doctri-
na de Fallos: 306:1195; 312:396, entre muchos otros), aunque la proce-
dencia sustancial de dicho recurso está supeditada a que la resolución
impugnada consagre un inequívoco apartamiento de lo dispuesto por
la Corte (Fallos: 323:3068 y sus citas).
En esta tarea, son los integrantes del Tribunal los que se encuen-
tran en mejores condiciones para desentrañar el alcance de sus pro-
pios fallos. Máxime, en situaciones como la de autos, donde este Mi-
nisterio Público no intervino en forma previa a la sentencia del 8 de
junio de 1993, que obraría a fs. 281 del Expte. 44.450 del registro de la

1386
FALLOS DE LA CORTE SUPREMA
330
Suprema Corte local, caratulado “Banco Patagónico S.A. (hoy su quie-
bra) c/ Cía. Marypez s/ ejecución”, así como tampoco al dictarse el fallo
del 7 de septiembre de 1999 en la causa B. 29, L. XXXV, cuya copia
simple se encuentra agrega a fs. 18/20 de este proceso (conf. dictamen
del señor Procurador General publicado en Fallos: 325:2835 y dicta-
men del 15 de septiembre de 2004, in re S. 2703, L. XXXVIII,
“Serralunga, Fernan Constante c/ Provincia de Santa Fe s/ recurso
contencioso administrativo de plena jurisdicción”).
No obsta a lo expuesto el distinto temperamento adoptado al dic-
taminar en las causas B. 3808, L.XXXVIII; B. 3809, L.XXXVIII, B.
4233, L. XXXVIII; B. 4225, L. XXXVIII y B. 4241, L. XXXVIII, puesto
que en ellas no debía interpretarse el alcance de sentencias dictadas
por el Alto Tribunal con anterioridad, sino que se trataba de la prime-
ra intervención que tenía en los autos que llegaron a su conocimiento.
– IV –
Por tanto, solicito a V.E. que tenga por evacuada la vista en los
términos indicados. Buenos Aires, 12 de mayo de 2005. Ricardo O.
Bausset.
```

### [span 11] header_pagina (2341–2341)
```
1385
```

### [span 12] header_pagina (2342–2342)
```
DE JUSTICIA DE LA NACION
```

### [span 13] header_pagina (2343–2343)
```
330
```

### [span 14] header_pagina (2382–2382)
```
1386
```

### [span 15] header_pagina (2383–2383)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 16] header_pagina (2384–2384)
```
330
```

### [span 17] cuerpo_mayoria (2403–2484)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 10 de abril de 2007.
Vistos los autos: “Banco Patagónico en liquidación c/ Maripez S.A.
s/ ejecución s/ ejecución de sentencia”.
Considerando:
1º) Que la Suprema Corte de la Provincia de Buenos Aires desesti-
mó el recurso de queja interpuesto por el Banco Central de la Repúbli-
ca Argentina contra la resolución que denegó los recursos extraordi-
narios locales, oportunamente planteados contra el pronunciamiento
de fs. 75/76 que mandó llevar adelante la ejecución en las presentes
actuaciones.

1387
DE JUSTICIA DE LA NACION
330
Para desestimar la queja el a quo fundó su decisión en que los
pronunciamientos recaídos en la etapa de ejecución no son suscepti-
bles de ser recurridos por la vía intentada.
2º) Que contra tal resolución el Banco Central de la República Ar-
gentina interpuso el remedio federal de fs. 833/845, con fundamento,
entre otros, y en lo que aquí importa, en la omisión en la que habría
incurrido el máximo tribunal local al no considerar el pronunciamien-
to de este Tribunal de fecha 7 de septiembre de 1999 en los autos
B.29.XXXV “Banco Patagónico S.A. (s/ quiebra) c/ Maripez S.A. s/ eje-
cución”, privándolo definitivamente de oponer la defensa fundada en
la renuncia al cobro de honorarios efectuada por el doctor Monterisi.
3º) Que, en la sentencia dictada por este Tribunal con fecha 7 de
septiembre de 1999 se manifestó que “En cuanto a la existencia de un
convenio que impediría el cobro de los honorarios regulados al doctor
Monterisi, el agravio que como de naturaleza federal se invoca, no es
de carácter definitivo en la medida que dicha cuestión ha sido introdu-
cida ante los tribunales ordinarios en la causa ‘Monterisi, Ricardo
Domingo c/ Banco Central de la República Argentina s/ incidente de
ejecución de honorarios en autos: Banco Patagónico S.A. c/ Marypez
S.A. s/ ejecución’” (conf. fs. 113/116)”. En referencia con la antedicha
cuestión la Corte Suprema había sostenido en la causa B.383.XXXIV
“Banco Patagónico S.A. s/ quiebra c/ Denegri, Enrique José s/ ejecu-
ción hipotecaria” (Fallos: 322:113) que “en cuanto a la existencia de un
convenio que impediría el cobro de honorarios regulados al doctor
Monterisi, el agravio que, como de naturaleza federal, se invoca, no es
de carácter definitivo en la medida en que dicha defensa –por su natu-
raleza– es susceptible de ser eficazmente introducida ante los tribu-
nales ordinarios en el correspondiente trámite de ejecución” (en igual
sentido, confr. causa B.644.XXIV “Banco Patagónico S.A. –hoy su quie-
bra– c/ Sotavento S.R.L s/ ejecución”, fallada el 6 de mayo de 1997,
considerando 6º).
4º) Que los agravios del apelante suscitan cuestión federal para su
examen en la vía elegida, pues aunque remiten al análisis de aspectos
vinculados con la improcedencia de los recursos extraordinarios en el
orden provincial, cuestión ajena como regla y por su naturaleza, al
remedio federal del art. 14 de la ley 48, tal circunstancia no constituye
óbice decisivo para invalidar lo resuelto cuando el tribunal local no ha
dado sustento suficiente a su decisión y cuando ha omitido tratar

1388
FALLOS DE LA CORTE SUPREMA
330
planteos oportunamente propuestos y conducentes para la correcta
solución del caso (Fallos: 311:1655, entre otros).
5º) Que corresponde descalificar la sentencia del Superior Tribu-
nal de la Provincia de Buenos Aires por la que se deniegan los ex-
traordinarios locales con el único fundamento de que los pronuncia-
mientos recaídos en la etapa de ejecución no son susceptibles de ser
recurridos por la vía intentada, toda vez que omitió considerar y pro-
nunciarse acerca de cuestiones relevantes para resolver la cuestión
debatida –una causa en trámite en la cual se discute la existencia de
un convenio de renuncia al cobro de honorarios– y que eventualmen-
te constituirían supuestos de excepción a la regla enunciada para
rechazar aquéllos.
6º) Que, en orden a lo indicado, es doctrina de este Tribunal que
corresponde hacer excepción al principio según el cual las decisiones
adoptadas en la etapa de ejecución de sentencia no configuran la sen-
tencia definitiva requerida por el art. 14 de la ley 48 cuando lo decidi-
do provoca un agravio de imposible o insuficiente reparación ulterior,
tal como la afectación del derecho de defensa ligado a la existencia
misma de la causa de la obligación (conf. Fallos: 312:1467; 315:305 y
2757; 317:1397, entre otros).
Por ello, oído el señor Procurador Fiscal subrogante, se declara
procedente el recurso extraordinario interpuesto, se deja sin efecto la
sentencia apelada. Vuelvan los autos al tribunal de origen para que,
por quien corresponda, se dicte un nuevo fallo de acuerdo a lo expresa-
do. Con costas. Notifíquese y remítase.
```

### [span 18] header_pagina (2415–2415)
```
1387
```

### [span 19] header_pagina (2416–2416)
```
DE JUSTICIA DE LA NACION
```

### [span 20] header_pagina (2417–2417)
```
330
```

### [span 21] header_pagina (2457–2457)
```
1388
```

### [span 22] header_pagina (2458–2458)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 23] header_pagina (2459–2459)
```
330
```

### [span 24] firma (2485–2486)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA — E.
```

### [span 25] catch_all (2487–2493)
```
RAÚL ZAFFARONI.
Recurso extraordinario interpuesto por el Banco Central, representado por la Dra.
Francisca M. Jeanneret.
Traslado contestado por el Dr. Ricardo D. Monterisi, patrocinado por el Dr. Héctor
O. Méndez.
Tribunal de origen: Suprema Corte de Justicia de la provincia Buenos Aires.

```

### [span 26] header_pagina (2494–2494)
```
1389
```

### [span 27] header_pagina (2495–2495)
```
DE JUSTICIA DE LA NACION
```

### [span 28] header_pagina (2496–2496)
```
330
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=2496 | linea_inicio_proximo_caso=2496 | delta=-1
**Alertas**: `solapado_con_proximo`


---

## 330_p1336 — Cencosud S.A. c/ D.G.I. | D.G.I. (Cencosud S.A. c/)

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 1336–1350 | Página consultada: 1350
- Líneas catálogo: 481–1024 | Línea fin real: 936 (status_fin=`fin_dentro_bloque`, pista=`sumario_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 481–481 | 1 |
| 2 | catch_all | 482–504 | 23 |
| 3 | caratula | 505–505 | 1 |
| 4 | sumario [1] | 506–517 | 12 |
| 5 | header_pagina | 513–513 | 1 |
| 6 | header_pagina | 514–514 | 1 |
| 7 | header_pagina | 515–515 | 1 |
| 8 | sumario [2] | 518–524 | 7 |
| 9 | sumario [3] | 525–530 | 6 |
| 10 | sumario [4] | 531–539 | 9 |
| 11 | sumario [5] | 540–542 | 3 |
| 12 | sumario [6] | 543–554 | 12 |
| 13 | header_pagina | 552–552 | 1 |
| 14 | header_pagina | 553–553 | 1 |
| 15 | header_pagina | 554–554 | 1 |
| 16 | sumario [7] | 555–561 | 7 |
| 17 | sumario [8] | 562–567 | 6 |
| 18 | sumario [9] | 568–576 | 9 |
| 19 | sumario [10] | 577–583 | 7 |
| 20 | sumario [11] | 584–596 | 13 |
| 21 | header_pagina | 592–592 | 1 |
| 22 | header_pagina | 593–593 | 1 |
| 23 | header_pagina | 594–594 | 1 |
| 24 | sumario [12] | 597–606 | 10 |
| 25 | sumario [13] | 607–616 | 10 |
| 26 | sumario [14] | 617–626 | 10 |
| 27 | sumario [15] | 627–639 | 13 |
| 28 | header_pagina | 634–634 | 1 |
| 29 | header_pagina | 635–635 | 1 |
| 30 | header_pagina | 636–636 | 1 |
| 31 | sumario [16] | 640–648 | 9 |
| 32 | sumario [17] | 649–652 | 4 |
| 33 | sumario [18] | 653–658 | 6 |
| 34 | sumario [19] | 659–663 | 5 |
| 35 | sumario [20] | 664–674 | 11 |
| 36 | header_pagina | 672–672 | 1 |
| 37 | header_pagina | 673–673 | 1 |
| 38 | header_pagina | 674–674 | 1 |
| 39 | cuerpo_mayoria | 675–767 | 93 |
| 40 | header_pagina | 711–711 | 1 |
| 41 | header_pagina | 712–712 | 1 |
| 42 | header_pagina | 713–713 | 1 |
| 43 | header_pagina | 752–752 | 1 |
| 44 | header_pagina | 753–753 | 1 |
| 45 | header_pagina | 754–754 | 1 |
| 46 | firma | 768–770 | 3 |
| 47 | catch_all | 771–771 | 1 |
| 48 | disidencia | 772–936 | 165 |
| 49 | header_pagina | 786–786 | 1 |
| 50 | header_pagina | 787–787 | 1 |
| 51 | header_pagina | 788–788 | 1 |
| 52 | header_pagina | 826–826 | 1 |
| 53 | header_pagina | 827–827 | 1 |
| 54 | header_pagina | 828–828 | 1 |
| 55 | header_pagina | 868–868 | 1 |
| 56 | header_pagina | 869–869 | 1 |
| 57 | header_pagina | 870–870 | 1 |
| 58 | header_pagina | 911–911 | 1 |
| 59 | header_pagina | 912–912 | 1 |
| 60 | header_pagina | 913–913 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=24 (5.26% del bloque, n=456)

---

### [span 1] header_pagina (481–481)
```
330
```

### [span 2] catch_all (482–504)
```
a una liquidación ulterior, el recurso ordinario resulta formalmente
improcedente, sin que obste a tal conclusión el hecho de que el monto
global aproximado pueda hipotéticamente superarlo (Fallos: 289:72,
entre otros).
En su caso, para acreditar el valor disputado, debió el recurrente
realizar una estimación de los honorarios que correspondería regular
en calidad de costas (Fallos: 314:129, considerando 3º), lo cual fue
omitido.
5º) Que según lo ha destacado esta Corte, la demostración referen-
te al valor en discusión resulta una carga del recurrente de cumpli-
miento imprescindible (Fallos: 312:238).
En tales condiciones, en ejercicio de las facultades que posee esta
Corte como juez del recurso, corresponde declarar improcedente la
apelación ordinaria articulada por el ejecutante.
Por ello, se resuelve: Declarar mal concedido el recurso ordinario
de apelación de fs. 2002. Con costas (art. 68 del Código Procesal Civil
y Comercial de la Nación). Notifíquese y devuélvase.
RICARDO LUIS LORENZETTI.
Recurso ordinario interpuesto por el Banco de Inversión y Comercio Exterior S.A.,
representado por el Dr. Matías Di Iorio, con el patrocinio del Dr. Patricio Harte
Traslado contestado por CitiBank NA, representado por el Dr. Eduardo J. Güemes,
patrocinado por el Dr. Ignacio Flores.
Tribunal de origen: Cámara Nacional de Apelaciones en lo Comercial, Sala B.
```

### [span 3] caratula (505–505)
```
CENCOSUD S.A. V. DIRECCION GENERAL IMPOSITIVA
```

### [span 4] sumario [1] (506–517)
**Header**: RECURSO ORDINARIO DE APELACION: Tercera instancia. Juicios en que la Nación
**Atribución**: (sin atribución detectada)
```
RECURSO ORDINARIO DE APELACION: Tercera instancia. Juicios en que la Nación
es parte.
Son formalmente admisibles los recursos ordinarios interpuestos contra una sen-
tencia definitiva en un pleito en que el Estado Nacional es parte y el valor dispu-
tado en último término, consistente en la diferencia entre el monto de los honora-
rios regulados y los que a juicio de las recurrentes corresponden, supera el míni-

1337
DE JUSTICIA DE LA NACION
330
mo establecido por el art. 24, inc. 6º, ap. a, del decreto ley 1285/58, modificado
por la ley 21.708 y reajustado por la resolución 1360/91.
```

### [span 5] header_pagina (513–513)
```
1337
```

### [span 6] header_pagina (514–514)
```
DE JUSTICIA DE LA NACION
```

### [span 7] header_pagina (515–515)
```
330
```

### [span 8] sumario [2] (518–524)
**Header**: RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
**Atribución**: (sin atribución detectada)
```
RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
Corresponde desestimar los recursos ordinarios pues los apelantes no formulan
–como es imprescindible– una crítica concreta y razonada de los fundamentos
desarrollados por el a quo, circunstancia que conduce a declarar la deserción de
los recursos, desde que las razones expuestas en los memoriales respectivos de-
ben ser suficientes para refutar los argumentos de hecho y de derecho dados
para arribar a la decisión impugnada.
```

### [span 9] sumario [3] (525–530)
**Header**: RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
**Atribución**: (sin atribución detectada)
```
RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
Corresponde declarar desiertos los recursos ordinarios si los argumentos
recursivos sólo constituyen una mera reedición de las objeciones ya formuladas
en las instancias anteriores o, en el mejor de los casos, simples discrepancias con
el criterio del a quo, pero distan de contener una crítica puntual de los funda-
mentos que informan la sentencia.
```

### [span 10] sumario [4] (531–539)
**Header**: RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
**Atribución**: (sin atribución detectada)
```
RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
Los argumentos que apuntan a demostrar que la retribución fijada es elevada
respecto a las remuneraciones que perciben otros miembros de la comunidad por
diversas tareas no son suficientes para desvirtuar las conclusiones de la cámara
en cuanto a que no existe una evidente e injustificada desproporción en los tér-
minos del art. 13 de la ley 24.432 pues, para justificar que un caso encuadra
dentro de la excepción legal es necesario explicar cuál fue concretamente el tra-
bajo realizado por los profesionales y demostrar que su calidad, extensión y efi-
cacia es desproporcionada con la retribución fijada.
```

### [span 11] sumario [5] (540–542)
**Header**: RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
**Atribución**: (sin atribución detectada)
```
RECURSO ORDINARIO DE APELACION: Tercera instancia. Generalidades.
Son tardíos los agravios introducidos por primera vez en la instancia ordinaria
ante la Corte Suprema.
```

### [span 12] sumario [6] (543–554)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
La regulación de honorarios profesionales no depende exclusivamente del monto
del juicio y de las escalas dispuestas en la ley de aranceles sino de un conjunto de
pautas previstas en los regímenes respectivos que deben ser evaluados por los
jueces y entre los que se encuentran la naturaleza y complejidad del asunto, la
índole, extensión, calidad y eficacia de los trabajos realizados, de manera de arri-
bar a una solución justa y mesurada acorde con las circunstancias particulares
de cada caso (Disidencia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).

1338
FALLOS DE LA CORTE SUPREMA
330
```

### [span 13] header_pagina (552–552)
```
1338
```

### [span 14] header_pagina (553–553)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 15] header_pagina (554–554)
```
330
```

### [span 16] sumario [7] (555–561)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
Establecer los honorarios profesionales mediante la aplicación automática de los
porcentuales fijados en la ley arancelaria, aún del mínimo establecido, puede dar
por resultado sumas exorbitantes y desproporcionadas en relación con las cons-
tancias de la causa, no compatibles con los fines perseguidos por el legislador al
sancionar la ley arancelaria ni con los intereses involucrados en el caso (Disiden-
cia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).
```

### [span 17] sumario [8] (562–567)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
Las normas contenidas en la ley arancelaria deben ser interpretadas
armónicamente, para evitar hacer prevalecer una sobre otra, con el propósito de
resguardar el sentido que el legislador ha entendido asignarles y, al mismo tiem-
po, el resultado valioso o disvalioso que se obtiene a partir de su aplicación a los
casos concretos (Disidencia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).
```

### [span 18] sumario [9] (568–576)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
Los arts. 6º, 7º y 13 de las leyes 21.839 y 24.432, configuran un bloque normativo
con determinación de pautas para fijar los honorarios que debe ser analizado y
ponderado en conjunto al momento de efectuar las pertinentes regulaciones. La
escala dispuesta en el art. 7º configura una pauta general, una directriz, que
permite verificar en cada caso concreto el grado de razonabilidad del resultado
de la regulación en orden a las pautas y principios receptados en el art. 6º, estos
últimos de ponderación exclusiva en cada caso concreto (Disidencia de los Dres.
Carlos S. Fayt y Juan Carlos Maqueda).
```

### [span 19] sumario [10] (577–583)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
El art. 13 de la ley 24.432 –modificatoria de la 21.839– dispone el deber de los
jueces de apartarse de los montos o porcentuales mínimos para privilegiar la
consideración de las pautas del art. 6º de la ley 21.839, cuando la aplicación es-
tricta, lisa y llana, de las escalas arancelarias ocasionaran una evidente e injus-
tificada desproporción, con la obligación de justificar fundadamente la resolu-
ción adoptada (Disidencia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).
```

### [span 20] sumario [11] (584–596)
**Header**: HONORARIOS: Regulación.
**Atribución**: (Disidencia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).
```
HONORARIOS: Regulación.
Con respecto a la regulación de honorarios es aplicable también el principio se-
gún el cual la misión judicial no se agota con la remisión a la letra de los textos
legales, sino que requiere del intérprete la búsqueda de la significación jurídica o
de los preceptos aplicables que consagre la versión técnicamente elaborada y
adecuada a su espíritu, debiendo desecharse las soluciones notoriamente injus-
tas que no se avienen con el fin propio de la investigación judicial de determinar

1339
DE JUSTICIA DE LA NACION
330
los principios acertados para el reconocimiento de los derechos de los litigantes
(Disidencia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).
```

### [span 21] header_pagina (592–592)
```
1339
```

### [span 22] header_pagina (593–593)
```
DE JUSTICIA DE LA NACION
```

### [span 23] header_pagina (594–594)
```
330
```

### [span 24] sumario [12] (597–606)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Procedencia del recurso. Falta de fundamentación suficiente.
Por aplicación de la doctrina de la arbitrariedad, según la cual es condición de
validez de un fallo judicial que sea la conclusión razonada del derecho vigente
con particular referencia a las circunstancias comprobadas de la causa, merece-
ría la tacha de desproporcionada aquella regulación que bajo la apariencia de
responder a los principios establecidos en las normas vigentes, diera por resulta-
do una suma irrisoria, incompatible con un análisis serio y mesurado de las va-
riables del caso y de las normas aplicables (Disidencia de los Dres. Carlos S. Fayt
y Juan Carlos Maqueda).
```

### [span 25] sumario [13] (607–616)
**Header**: SENTENCIA: Principios generales.
**Atribución**: (sin atribución detectada)
```
SENTENCIA: Principios generales.
A la condición de órganos de aplicación del derecho vigente va entrañablemente
unida la obligación que incumbe a los jueces de fundar sus decisiones, no sólo
porque los ciudadanos pueden sentirse mejor juzgados sino también porque ello
persigue la exclusión de decisiones irregulares para documentar que el fallo es la
derivación razonada del derecho vigente y no producto de la individual voluntad
del juez. La exigencia de fundamentos serios reconoce raíz constitucional y tiene,
como contenido concreto, el imperativo de que la decisión se conforme a la ley y a
los principios propios de la doctrina y jurisprudencia vinculados con la especie a
decidir (Disidencia de los Dres. Carlos S. Fayt y Juan Carlos Maqueda).
```

### [span 26] sumario [14] (617–626)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
Corresponde reducir la regulación que luce desproporcionada en relación a la
magnitud y extensión de la tarea profesional desarrollada y a las etapas procesa-
les efectivamente cumplidas, ya que la única pauta ponderada por el a quo ha
sido el monto del litigio y la aplicación automática de los porcentajes arancela-
rios sin tener en cuenta las constancias de la causa, lo cual conduce a un resulta-
do no compatible con los fines perseguidos por el legislador al sancionar la ley
arancelaria, ni con los intereses involucrados, ni con los parámetros del mercado
de trabajo en general (Disidencia de los Dres. Carlos S. Fayt y Juan Carlos
Maqueda).
```

### [span 27] sumario [15] (627–639)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
La materia atinente a la regulación de honorarios no resulta ajena al principio
según el cual la misión judicial no se agota con la remisión a la letra de los textos
legales, sino que requiere del intérprete la búsqueda de la significación jurídica o
de los preceptos aplicables que consagre la versión técnicamente elaborada y
adecuada a su espíritu, debiendo desecharse las soluciones notoriamente injus-

1340
FALLOS DE LA CORTE SUPREMA
330
tas que no se avienen con el fin propio de la investigación judicial de determinar
los principios acertados para el reconocimiento de los derechos (Disidencia del
Dr. E. Raúl Zaffaroni).
```

### [span 28] header_pagina (634–634)
```
1340
```

### [span 29] header_pagina (635–635)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 30] header_pagina (636–636)
```
330
```

### [span 31] sumario [16] (640–648)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
En materia de regulación de honorarios se impone una interpretación armónica
que integre, con el adecuado equilibrio, los distintos parámetros que determina
la ley, a efectos de evitar la disociación de la pauta económica, atinente al monto
del litigio, de las restantes que informa la normativa arancelaria, entre las cua-
les se destacan la extensión, calidad, complejidad de la labor profesional, y la
trascendencia jurídica, moral y económica que tiene el asunto o proceso para
casos futuros, y para la situación económica de las partes (Disidencia del Dr. E.
Raúl Zaffaroni).
```

### [span 32] sumario [17] (649–652)
**Header**: CONSTITUCION NACIONAL: Derechos y garantías. Derecho a la justa retribución.
**Atribución**: (sin atribución detectada)
```
CONSTITUCION NACIONAL: Derechos y garantías. Derecho a la justa retribución.
El establecimiento de una regulación justa, debe conciliar la letra y el espíritu de
la ley de arancel con el respeto al derecho que en tal sentido prevé nuestra Carta
Magna en su art. 14 bis (Disidencia del Dr. E. Raúl Zaffaroni).
```

### [span 33] sumario [18] (653–658)
**Header**: CONSTITUCION NACIONAL: Derechos y garantías. Derecho a la justa retribución.
**Atribución**: (sin atribución detectada)
```
CONSTITUCION NACIONAL: Derechos y garantías. Derecho a la justa retribución.
La garantía a una justa retribución debe plasmarse mediante la decisión judicial
correspondiente que, como tal, importe una derivación razonada del derecho vi-
gente de conformidad con las constancias de la causa, de modo que sustan-
cialmente no traduzca un menoscabo a las previsiones constitucionales estable-
cidas en los arts. 14 bis y 17 (Disidencia del Dr. E. Raúl Zaffaroni).
```

### [span 34] sumario [19] (659–663)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
De acuerdo al principio sentado en el art. 28 de la Constitución Nacional las
garantías contenidas, al respecto, en los arts. 14 bis y 17, resultan vulneradas
cuando la regulación exorbita la adecuada composición que debe establecerse al
conceder una retribución desproporcionada (Disidencia del Dr. E. Raúl Zaffaroni).
```

### [span 35] sumario [20] (664–674)
**Header**: HONORARIOS: Regulación.
**Atribución**: (sin atribución detectada)
```
HONORARIOS: Regulación.
La afectación de las garantías contenidas en los arts. 14 bis y 17 de la Constitu-
ción Nacional, en la medida que ocasione una evidente e injustificada despropor-
ción entre la importancia del trabajo efectivamente cumplido y la retribución,
posibilita regular los honorarios por debajo de la escala mínima prevista en el
art. 7 de la ley 21.839, de acuerdo a la modificación establecida por el art. 13 de
la ley 24.432 (Disidencia del Dr. E. Raúl Zaffaroni).

1341
DE JUSTICIA DE LA NACION
330
```

### [span 36] header_pagina (672–672)
```
1341
```

### [span 37] header_pagina (673–673)
```
DE JUSTICIA DE LA NACION
```

### [span 38] header_pagina (674–674)
```
330
```

### [span 39] cuerpo_mayoria (675–767)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 10 de abril de 2007.
Vistos los autos: “Cencosud S.A. (TF 14.438-I) y acum. 14.439-I y
14.441-I c/ DGI”.
Considerando:
1º) Que contra la sentencia de la Sala I de la Cámara Nacional de
Apelaciones en lo Contencioso Administrativo Federal, que elevó los
honorarios regulados por el Tribunal Fiscal a los doctores Delfín J.
Carballo y José L. Patrignani –letrado patrocinante y representante
de la parte actora, respectivamente– y al perito contador Armando M.
Casal, ambas partes interpusieron recursos ordinarios de apelación,
que fueron concedidos mediante el auto de fs. 1333. La parte actora
presentó su memorial a fs. 1340/1356 y el Fisco expresó sus agravios a
fs. 1357/1363 vta., escritos que fueron contestados por los profesiona-
les a fs. 1369/1386.
2º) Que, al señalar que los recurrentes no habían demostrado la
existencia de un caso excepcional que justificara la regulación por de-
bajo de los mínimos arancelarios legales en los términos del art. 13 de
la ley 24.432, la cámara fijó los honorarios profesionales en las sumas
de $ 3.300.000 a favor del doctor Delfín J. Carballo, $ 1.350.000 a fa-
vor del doctor José L. Patrignani, y de $ 1.200.000 a favor del perito
contador Armando M. Casal.
3º) Que ambas partes alegan que la regulación practicada resulta
sumamente elevada con relación a la importancia y trascendencia de
las tareas cumplidas por los profesionales en el expediente. De ahí que
solicitan que se aplique el art. 13 de la ley 24.432, según el cual los
jueces deben regular honorarios por debajo de los mínimos legales cuan-
do “la aplicación de esos aranceles ocasionaría una evidente e injusti-
ficada desproporción entre la importancia del trabajo efectivamente
cumplido y la retribución que en virtud de aquellas normas arancela-
rias habría de corresponder”. Se agravian porque el a quo desechó la
aplicación de la norma citada sobre la base de que el monto del juicio
no era excepcionalmente significativo pero no evaluó si existía despro-
porción entre la retribución fijada y la calidad, extensión y eficacia de
la labor profesional.

1342
FALLOS DE LA CORTE SUPREMA
330
En su memorial, la parte actora también se queja por el modo en
que la cámara calculó la base regulatoria.
4º) Que los recursos ordinarios articulados resultan, en principio,
formalmente admisibles toda vez que se trata de una sentencia defini-
tiva en un pleito en que el Estado Nacional es parte y el valor disputa-
do en último término, consistente en la diferencia entre el monto de
los honorarios regulados y los que a juicio de las recurrentes corres-
ponden, supera el mínimo establecido por el art. 24, inc. 6º, ap. a, del
decreto-ley 1285/58, modificado por la ley 21.708 y reajustado por la
resolución 1360/91.
5º) Que no obstante la admisibilidad formal antes señalada, los
recursos deben desestimarse por otro motivo, pues los apelantes no
formulan –como es imprescindible– una crítica concreta y razonada
de los fundamentos desarrollados por el a quo, circunstancia que con-
duce a declarar la deserción de los recursos (Fallos: 310:2914; 311:1989;
312:1819; 313:396), desde que las razones expuestas en los memoria-
les respectivos deben ser suficientes para refutar los argumentos de
hecho y de derecho dados para arribar a la decisión impugnada (Fa-
llos: 310:2929).
6º) Que tales defectos de fundamentación se advierten en tanto los
argumentos recursivos sólo constituyen una mera reedición de las ob-
jeciones ya formuladas en las instancias anteriores o, en el mejor de
los casos, simples discrepancias con el criterio del a quo, pero distan
de contener una crítica puntual de los fundamentos que informan la
sentencia.
Las apelantes insisten en argumentos que apuntan a demostrar
que la retribución fijada es elevada respecto a las remuneraciones que
perciben otros miembros de la comunidad por diversas tareas, pero
que no son suficientes para desvirtuar las conclusiones de la cámara
en cuanto a que no existe una evidente e injustificada desproporción
en los términos del art. 13 de la ley 24.432. Cabe señalar que para
justificar que un caso encuadra dentro de la excepción legal es necesa-
rio explicar cuál fue concretamente el trabajo realizado por los profe-
sionales y demostrar que su calidad, extensión y eficacia es
desproporcionada con la retribución fijada.
Por lo demás, no asiste razón a las recurrentes en cuanto sostie-
nen que la cámara no evaluó la existencia de desproporción entre las

1343
DE JUSTICIA DE LA NACION
330
tareas cumplidas y la retribución fijada ya que, por el contrario, el a
quo examinó los agravios de los apelantes y concluyó, fundadamente,
que no habían logrado acreditar tal circunstancia.
7º) Que, finalmente, en cuanto al cálculo de la base regulatoria, los
agravios de la parte actora resultan tardíos ya que fueron introduci-
dos por primera vez en esta instancia. Al respecto, cabe señalar que en
el memorial de apelación de fs. 1249/1250 la actora se limitó a solici-
tar la aplicación del art. 13 de la ley 24.432, por considerar que la
regulación de honorarios era desproporcionada con respecto a las ta-
reas efectivamente cumplidas por los profesionales.
Por ello, se declaran desiertos los recursos ordinarios concedidos
(art. 280, ap. 2º, del Código Procesal Civil y Comercial de la Nación).
Con costas. Notifíquese y devuélvanse los autos.
```

### [span 40] header_pagina (711–711)
```
1342
```

### [span 41] header_pagina (712–712)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 42] header_pagina (713–713)
```
330
```

### [span 43] header_pagina (752–752)
```
1343
```

### [span 44] header_pagina (753–753)
```
DE JUSTICIA DE LA NACION
```

### [span 45] header_pagina (754–754)
```
330
```

### [span 46] firma (768–770)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT (en disidencia) — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS
MAQUEDA (en disidencia) — E. RAÚL ZAFFARONI (en disidencia) — CARMEN
```

### [span 47] catch_all (771–771)
```
M. ARGIBAY.
```

### [span 48] disidencia (772–936)
**Header**: DISIDENCIA DE LOS SEÑORES MINISTROS
```
DISIDENCIA DE LOS SEÑORES MINISTROS
 DOCTORES DON CARLOS S. FAYT Y DON JUAN CARLOS MAQUEDA
Considerando:
Que los infrascriptos coinciden con el considerando 1º al 4º del voto
de la mayoría.
5º) Que los agravios relativos a los montos de honorarios regula-
dos en la instancia de grado, que aumentaron significativamente los
fijados por el Tribunal Fiscal de la Nación, exigen en primer término
efectuar una serie de consideraciones de alcance general en la mate-
ria.
6º) Que cabe recordar que la Corte Suprema de Justicia de la Na-
ción a partir de 1879 sostuvo el criterio de evaluar la extensión y com-
plejidad de los trabajos de los profesionales intervinientes en las cau-

1344
FALLOS DE LA CORTE SUPREMA
330
sas, de manera de determinar una regulación con arreglo al trabajo
efectivamente realizado y a su extensión (Fallos: 21:521).
El Tribunal según lo resuelto en Fallos: 306:1265 modificó tal doc-
trina estableciendo un criterio según el cual la ponderación de los di-
versos factores tales como mérito, naturaleza e importancia de los tra-
bajos no podía derivar en la aplicación de un porcentaje que se aparte
de los extremos de la ley. Razón por la cual no se advertía que en los
juicios susceptibles de apreciación pecuniaria los honorarios pudieran
ser inferiores a los que resultan de aplicar el mínimo de la escala pre-
vista en la norma (considerando 4º del fallo citado). A partir de tal
doctrina sólo excepcionalmente se ha entendido que corresponde re-
gular por debajo de la escala arancelaria (Fallos: 320:495; 322:1535).
7º) Que corresponde dejar de lado tal doctrina y retomar la postu-
ra tradicional en la materia por considerar que es la más adecuada en
los términos de la legislación arancelaria vigente y de acuerdo al rol
institucional que le cabe a esta Corte.
En tal sentido, la regulación de honorarios profesionales no depen-
de exclusivamente del monto del juicio y de las escalas dispuestas en
la ley de aranceles sino de un conjunto de pautas previstas en los regí-
menes respectivos que deben ser evaluados por los jueces y entre los
que se encuentran la naturaleza y complejidad del asunto, la índole,
extensión, calidad y eficacia de los trabajos realizados, de manera de
arribar a una solución justa y mesurada acorde con las circunstancias
particulares de cada caso.
Establecer los honorarios profesionales mediante la aplicación
automática de los porcentuales fijados en la ley arancelaria, aún del
mínimo establecido, puede dar por resultado sumas exorbitantes y
desproporcionadas en relación con las constancias de la causa, no com-
patibles con los fines perseguidos por el legislador al sancionar la ley
arancelaria ni con los intereses involucrados en el caso.
8º) Que en el sentido expuesto es necesario recordar que las nor-
mas contenidas en la ley arancelaria deben ser interpretadas
armónicamente, para evitar hacer prevalecer una sobre otra, con el
propósito de resguardar el sentido que el legislador ha entendido asig-
narles y, al mismo tiempo, el resultado valioso o disvalioso que se ob-
tiene a partir de su aplicación a los casos concretos.

1345
DE JUSTICIA DE LA NACION
330
9º) Que como principio general cabe sostener que los arts. 6º, 7º y
13 de las leyes 21.839 y 24.432, configuran un bloque normativo con
determinación de pautas para fijar los honorarios que debe ser anali-
zado y ponderado en conjunto al momento de efectuar las pertinentes
regulaciones. La escala dispuesta en el art. 7º configura una pauta
general, una directriz, que permite verificar en cada caso concreto el
grado de razonabilidad del resultado de la regulación en orden a las
pautas y principios receptados en el art. 6º, estos últimos de pondera-
ción exclusiva en cada caso concreto.
El art. 13 de la ley 24.432 –modificatoria de la 21.839– consagra
en forma explícita la interpretación propuesta, ya que dispone el de-
ber de los jueces de apartarse de los montos o porcentuales mínimos
para privilegiar la consideración de las pautas del art. 6º de la ley
21.839, cuando la aplicación estricta, lisa y llana, de las escalas aran-
celarias ocasionaran una evidente e injustificada desproporción, con
la obligación de justificar fundadamente la resolución adoptada.
Al mismo tiempo el art. 63 de la ley 21.839 –no derogado por la ley
24.432– dispone que la ley se aplicará a todos los asuntos o procesos
pendientes, con la única limitación de no haber resolución firme de
regulación de honorarios al tiempo de su entrada en vigencia. Norma
que no debe soslayarse al interpretar la aplicación del art. 13 de la ley
24.432, ya que su invocación en los casos concretos estaría condiciona-
da a la existencia y fundamentación del irrazonable resultado que se
obtendría de aplicar exclusivamente las escalas porcentuales y pres-
cindir de las pautas enunciadas en el art. 6º y ratificadas en el art. 13
citado.
10) Que en la cuestión de regulación de honorarios es de aplicación
también el principio elaborado por el Tribunal según el cual la misión
judicial no se agota con la remisión a la letra de los textos legales, sino
que requiere del intérprete la búsqueda de la significación jurídica o
de los preceptos aplicables que consagre la versión técnicamente ela-
borada y adecuada a su espíritu, debiendo desecharse las soluciones
notoriamente injustas que no se avienen con el fin propio de la inves-
tigación judicial de determinar los principios acertados para el reco-
nocimiento de los derechos de los litigantes (Fallos: 253:267 entre otros).
11) Que en la materia sub examine, y por aplicación de la doctrina
de la arbitrariedad, según la cual es condición de validez de un fallo
judicial que sea la conclusión razonada del derecho vigente con parti-

1346
FALLOS DE LA CORTE SUPREMA
330
cular referencia a las circunstancias comprobadas de la causa (Fallos:
238:550 entre otros), de igual manera merecería la tacha de despro-
porcionada aquella regulación que bajo la apariencia de responder a
los principios enunciados en los considerandos precedentes diera por
resultado una suma irrisoria, incompatible con un análisis serio y
mesurado de las variables del caso y de las normas aplicables.
12) Que, por último, es necesario reiterar que la correcta aplica-
ción de las normas y principios enunciados requiere, indefectiblemen-
te, de una adecuada fundamentación de la decisión que permita com-
probar que se han considerado la totalidad de las variables que inte-
gran el régimen de regulación. A tales efectos es oportuno recordar
que a la condición de órganos de aplicación del derecho vigente va
entrañablemente unida la obligación que incumbe a los jueces de fun-
dar sus decisiones, no sólo porque los ciudadanos pueden sentirse mejor
juzgados sino también porque ello persigue la exclusión de decisiones
irregulares para documentar que el fallo es la derivación razonada del
derecho vigente y no producto de la individual voluntad del juez. La
exigencia de fundamentos serios reconoce raíz constitucional y tiene,
como contenido concreto, el imperativo de que la decisión se conforme
a la ley y a los principios propios de la doctrina y jurisprudencia vincu-
lados con la especie a decidir. (Fallos: 236:27).
13) Que en apoyo del sentido de interpretación expuesto en la
materia es oportuno recordar que la Corte Interamericana de Dere-
chos Humanos en el Caso Cantos (sentencia contra el Estado Argenti-
no de fecha 28 de noviembre de 2000 Serie C. Nº 97) manifestó que
“...existen normas internas en la Argentina que ordenan liquidar y
pagar en concepto... de honorarios de abogados y peritos sumas exor-
bitantes, que van mucho más allá de los límites que corresponderían a
la equitativa remuneración de un trabajo profesional calificado. Tam-
bién existen disposiciones que facultan a los jueces para reducir el
cálculo de la tasa y de los honorarios aludidos a límites que los hagan
razonables y equitativos... (ap. 62)”. Con expresa mención de las leyes
24.432 y 21.839 la Corte Interamericana observa que “...la aplicación
a los honorarios de los parámetros permitidos por la ley condujeron a
que se regularan sumas exorbitantes... Ante esta situación las autori-
dades judiciales han debido tomar todas las medidas pertinentes para
impedir que se produjeran y para lograr que se hicieran efectivos el
acceso a la justicia y el derecho a las garantías judiciales y a la protec-
ción judicial...”.

1347
DE JUSTICIA DE LA NACION
330
14) Que por aplicación de la doctrina expuesta corresponde redu-
cir la regulación apelada, teniendo en cuenta que la misma luce
desproporcionada en relación a la magnitud y extensión de la tarea
profesional desarrollada y a las etapas procesales efectivamente cum-
plidas. Surge con claridad que la única pauta ponderada por el a quo
ha sido el monto del litigio y la aplicación automática de los porcen-
tajes arancelarios sin tener en cuenta las constancias de la causa.
Ello conduce a un resultado no compatible con los fines perseguidos
por el legislador al sancionar la ley arancelaria, ni con los intereses
involucrados en el caso, ni con los parámetros del mercado de trabajo
en general (conforme considerandos 9 a 16 del voto del juez Maqueda
en la causa D.163. XXXVII D.N.R.P. c/ Vidal de Docampo, Clara Au-
rora s/ ejecución fiscal – inc. de ejecución de honorarios –Fallos:
329:94–).
15) Que, en razón de las pautas enunciadas, corresponde regular
los honorarios en las sumas de $ 320.000 (pesos trescientos veinte mil)
al doctor José L. Pratignani; de $ 960.000 (pesos novecientos sesenta
mil) al doctor Delfín J. Carballo y de $ 300.000 (pesos trescientos mil)
al perito contador Armando M. Casal.
Por ello, el Tribunal resuelve declarar procedente el recurso ordi-
nario interpuesto y revocar la sentencia apelada y fijar los honorarios
de los profesionales en las sumas indicadas en el considerando 15 de
la presente. Con costas. Notifíquese y, oportunamente, remítase.
```

### [span 49] header_pagina (786–786)
```
1344
```

### [span 50] header_pagina (787–787)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 51] header_pagina (788–788)
```
330
```

### [span 52] header_pagina (826–826)
```
1345
```

### [span 53] header_pagina (827–827)
```
DE JUSTICIA DE LA NACION
```

### [span 54] header_pagina (828–828)
```
330
```

### [span 55] header_pagina (868–868)
```
1346
```

### [span 56] header_pagina (869–869)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 57] header_pagina (870–870)
```
330
```

### [span 58] header_pagina (911–911)
```
1347
```

### [span 59] header_pagina (912–912)
```
DE JUSTICIA DE LA NACION
```

### [span 60] header_pagina (913–913)
```
330
```

### Borde inferior (transición al próximo caso)
**Estado**: `gap_con_residuo` | linea_fin_real=936 | linea_inicio_proximo_caso=1025 | delta=88
**Alertas**: `firma_multilinea_partida_por_fin_real`, `voto_disidencia_individual_en_gap`

| Línea | Clasificación | Texto |
|------:|---------------|-------|
| 937 | `firma_arrastrada` | CARLOS S. FAYT — JUAN CARLOS MAQUEDA. |
| 938 | `voto_disidencia_individual` | DISIDENCIA DEL SEÑOR |
| 939 | `firma_arrastrada` | MINISTRO DOCTOR DON E. RAÚL ZAFFARONI |
| 940 | `no_clasificable` | Considerando: |
| 941 | `no_clasificable` | Que el infrascripto coincide con el considerando 1º al 4º del voto de |
| 942 | `firma_arrastrada` | los jueces Fayt y Maqueda. |
| 943 | `no_clasificable` | 5º) Que la materia atinente a la regulación de honorarios no re- |
| 944 | `no_clasificable` | sulta ajena al principio, elaborado por el Tribunal, según el cual la |
| 945 | `vacia` |  |
| 946 | `header_pagina` | 1348 |
| 947 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 948 | `header_pagina` | 330 |
| 949 | `no_clasificable` | misión judicial no se agota con la remisión a la letra de los textos |
| 950 | `no_clasificable` | legales, sino que requiere del intérprete la búsqueda de la significa- |
| 951 | `no_clasificable` | ción jurídica o de los preceptos aplicables que consagre la versión |
| 952 | `no_clasificable` | técnicamente elaborada y adecuada a su espíritu, debiendo desecharse |
| 953 | `no_clasificable` | las soluciones notoriamente injustas que no se avienen con el fin pro- |
| 954 | `no_clasificable` | pio de la investigación judicial de determinar los principios acerta- |
| 955 | `no_clasificable` | dos para el reconocimiento de los derechos (Fallos: 253:267 entre |
| 956 | `no_clasificable` | otros). |
| 957 | `no_clasificable` | 6º) Que, en cuanto al fondo de la cuestión, cabe precisar que la ley |
| 958 | `no_clasificable` | arancelaria no debe ser aplicada en forma mecánica prescindiendo de |
| 959 | `no_clasificable` | una adecuada relación con las restantes pautas que establece el art. 6º, |
| 960 | `no_clasificable` | inc. b y sgtes. de la ley 21.839. |
| 961 | `no_clasificable` | 7º) Que, en la materia, se impone una interpretación armónica |
| 962 | `no_clasificable` | que integre, con el adecuado equilibrio, los distintos parámetros que |
| 963 | `no_clasificable` | determina la ley, a efectos de evitar la disociación de la pauta econó- |
| 964 | `no_clasificable` | mica, atinente al monto del litigio, de las restantes que informa la |
| 965 | `no_clasificable` | normativa arancelaria, entre las cuales se destacan la extensión, cali- |
| 966 | `no_clasificable` | dad, complejidad de la labor profesional, y la trascendencia jurídica, |
| 967 | `no_clasificable` | moral y económica que tiene el asunto o proceso para casos futuros, y |
| 968 | `no_clasificable` | para la situación económica de las partes. |
| 969 | `no_clasificable` | 8º) Que tal valoración propende, como fin último, al establecimien- |
| 970 | `no_clasificable` | to de una regulación justa, de manera que concilie la letra y el espíritu |
| 971 | `no_clasificable` | de la ley de arancel con el respeto al derecho que en tal sentido prevé |
| 972 | `no_clasificable` | nuestra Carta Magna en su art. 14 bis. |
| 973 | `no_clasificable` | 9º) Que la garantía a una justa retribución debe plasmarse me- |
| 974 | `no_clasificable` | diante la decisión judicial correspondiente que, como tal, importe una |
| 975 | `no_clasificable` | derivación razonada del derecho vigente de conformidad con las cons- |
| 976 | `no_clasificable` | tancias de la causa, de modo que sustancialmente no traduzca un |
| 977 | `no_clasificable` | menoscabo a las previsiones constitucionales establecidas en los arts. 14 |
| 978 | `no_clasificable` | bis y 17. |
| 979 | `no_clasificable` | 10) Que de acuerdo al principio sentado en el art. 28 de la Consti- |
| 980 | `no_clasificable` | tución Nacional las garantías contenidas, al respecto, en los artículos |
| 981 | `no_clasificable` | citados en el considerando anterior, resultan vulneradas cuando la |
| 982 | `no_clasificable` | regulación exorbita la adecuada composición, que debe establecerse, |
| 983 | `no_clasificable` | entre las pautas indicadas (considerando 7º) al conceder una retribu- |
| 984 | `no_clasificable` | ción desproporcionada. |
| 985 | `vacia` |  |
| 986 | `header_pagina` | 1349 |
| 987 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 988 | `header_pagina` | 330 |
| 989 | `no_clasificable` | 11) Que ello es así, cuando se desconoce esa composición, mediante |
| 990 | `no_clasificable` | la fijación de una retribución en exceso –como en el caso–, o se la dis- |
| 991 | `no_clasificable` | minuye de forma que resulta inconciliable con la tutela establecida en |
| 992 | `no_clasificable` | las garantías de raigambre constitucional mencionadas. |
| 993 | `no_clasificable` | 12) Que la afectación de tales derechos, en la medida que ocasione |
| 994 | `no_clasificable` | una evidente e injustificada desproporción entre la importancia del |
| 995 | `no_clasificable` | trabajo efectivamente cumplido y la retribución, posibilita regular los |
| 996 | `no_clasificable` | honorarios por debajo de la escala mínima prevista en el art. 7 de la |
| 997 | `no_clasificable` | ley 21.839, de acuerdo a la modificación establecida por el art. 13 de la |
| 998 | `no_clasificable` | ley 24.432. |
| 999 | `no_clasificable` | 13) Que, en el presente caso, se exterioriza el apartamiento de los |
| 1000 | `no_clasificable` | principios enunciados, ya que la decisión recurrida resulta descali- |
| 1001 | `no_clasificable` | ficable, al fijar honorarios que no guardan la debida relación con la |
| 1002 | `no_clasificable` | extensión, calidad y complejidad de la tarea realizada, a tiempo en |
| 1003 | `no_clasificable` | que se ha sustentado en argumentos sólo aparentes. |
| 1004 | `no_clasificable` | 14) Que, en razón de las pautas enunciadas, corresponde regular |
| 1005 | `no_clasificable` | los honorarios en las sumas de $ 320.000 (pesos trescientos veinte mil) |
| 1006 | `no_clasificable` | al doctor José L. Pratignani; de $ 960.000 (pesos novecientos sesenta |
| 1007 | `no_clasificable` | mil) al doctor Delfín J. Carballo y de $ 300.000 (pesos trescientos mil) |
| 1008 | `no_clasificable` | al perito contador Armando M. Casal. |
| 1009 | `no_clasificable` | Por ello, el Tribunal resuelve declarar procedente el recurso ordi- |
| 1010 | `no_clasificable` | nario interpuesto y revocar la sentencia apelada y fijar los honorarios |
| 1011 | `no_clasificable` | de los profesionales en las sumas indicadas en el considerando 15 de |
| 1012 | `no_clasificable` | la presente. Con costas. Notifíquese y, oportunamente, remítase. |
| 1013 | `firma_arrastrada` | E. RAÚL ZAFFARONI. |
| 1014 | `no_clasificable` | Recurso ordinario interpuesto por Cencosud S.A., representada por el Dr. Guillermo |
| 1015 | `no_clasificable` | E. Quiñoa y el Fisco Nacional, representado por la Dra. Marta N. Arzone. |
| 1016 | `no_clasificable` | Traslados contestados por Cencosud S.A., representada por los Dres. Guillermo E. |
| 1017 | `no_clasificable` | Quiñoa, Delfín Jorge Carvallo y Armando Miguel Casal, patrocinado por los Dres. |
| 1018 | `no_clasificable` | José L. Patrignani y Matías E. Carballo, respectivamente y Fisco Nacional, |
| 1019 | `no_clasificable` | representados por la Dra. Marta N. Arzone. |
| 1020 | `no_clasificable` | Tribunal de origen: Cámara Nacional de Apelaciones en lo Contencioso Admi- |
| 1021 | `no_clasificable` | nistrativo Federal, Sala I. |
| 1022 | `vacia` |  |
| 1023 | `header_pagina` | 1350 |
| 1024 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |


---

## 330_p807 — Obra Social Bancaria Argentina c/ Superintendencia de Servicios de Salud | Superintendencia de Servicios de Salud (Obra 

**Localización**
- Archivo: `LibroVol330.1.md`
- Páginas catálogo: 807–810 | Página consultada: 810
- Líneas catálogo: 30628–30724 | Línea fin real: 30719 (status_fin=`fin_dentro_bloque`, pista=`sumario_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 30628–30628 | 1 |
| 2 | catch_all | 30629–30629 | 1 |
| 3 | caratula | 30630–30630 | 1 |
| 4 | sumario [1] | 30631–30639 | 9 |
| 5 | dictamen | 30640–30710 | 71 |
| 6 | header_pagina | 30660–30660 | 1 |
| 7 | header_pagina | 30661–30661 | 1 |
| 8 | header_pagina | 30662–30662 | 1 |
| 9 | header_pagina | 30695–30695 | 1 |
| 10 | header_pagina | 30696–30696 | 1 |
| 11 | header_pagina | 30697–30697 | 1 |
| 12 | cuerpo_mayoria | 30711–30719 | 9 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=1 (1.09% del bloque, n=92)

---

### [span 1] header_pagina (30628–30628)
```
330
```

### [span 2] catch_all (30629–30629)
```
OBRA SOCIAL BANCARIA ARGENTINA
```

### [span 3] caratula (30630–30630)
```
OBRA SOCIAL BANCARIA ARGENTINA V. SUPERINTENDENCIA DE SERVICIOS DE SALUD

```

### [span 4] sumario [1] (30631–30639)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Nación.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia federal. Por las personas. Nación.
Si la pretensión de la obra social actora consiste en obtener que se deje sin efecto
un acto administrativo, dictado por la Superintendencia de Servicios de Salud en
virtud de la cual le aplicó una multa por incumplir con lo previsto en el art. 42
incs. a) y c) de la ley 23.661, corresponde que la Justicia Nacional en lo Conten-
cioso Administrativo Federal entienda en la causa en donde se cuestiona la san-
ción de carácter administrativo, impuesta por un órgano estatal en ejercicio de la
función administrativa.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] dictamen (30640–30710)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
A fs. 1/5, la Obra Social Bancaria Argentina (OSBA) interpuso re-
curso de apelación, en los términos del art. 45 de la ley 23.661, a fin de
obtener que se deje sin efecto la resolución 666/05, dictada por la
Superintendencia de Servicios de Salud (expte. Nº 1-26304), por me-
dio de la cual se le impuso una sanción, con sustento en lo dispuesto en
el art. 42, incs. a) y c), de la ley citada.
– II –
A fs. 33, la Cámara Nacional de Apelaciones en lo Contencioso
Administrativo Federal (Sala I) se declaró incompetente para enten-
der en la causa, al considerar que corresponde aplicar con criterio ex-
tensivo la doctrina sentada por V.E. en el precedente de Fallos:
315:2292 y remitió los autos a la Cámara Nacional de Apelaciones en
lo Civil y Comercial Federal.
Por su parte, la Sala III de dicho tribunal rechazó la competencia
asignada, con fundamento en que su par en lo Contencioso Adminis-
trativo Federal es el órgano judicial competente para conocer en los

808
FALLOS DE LA CORTE SUPREMA
330
recursos que se interpongan contra las resoluciones de los organismos
administrativos, en virtud de lo dispuesto en el art. 4º de la ley 21.628.
En consecuencia, devolvió la causa al remitente, quien mantuvo su
criterio y la elevó a V.E. (v. fs. 48).
– III –
En tales condiciones, ha quedado trabado un conflicto negativo de
competencia que corresponde dirimir a V.E., en los términos del art. 24,
inc. 7º), del decreto-ley 1285/58.
– IV –
Ante todo, cabe recordar que el art. 45 de la ley 23.661 establece
que será competente para conocer en el recurso de apelación la Cáma-
ra Federal de Apelaciones que corresponda de acuerdo con el domicilio
del recurrente.
Sentado lo anterior, cabe concluir que la presente causa debe tra-
mitar ante la justicia federal, aunque todavía resta por examinar a
qué fuero –civil y comercial federal o contencioso administrativo fede-
ral– le corresponde hacerlo cuando el proceso se sustancia en el ámbi-
to de la Capital Federal.
A mi modo de ver, según se desprende de los términos de la de-
manda, a cuya exposición de los hechos se debe atender de modo prin-
cipal para determinar la competencia (art. 4º del Código Procesal Ci-
vil y Comercial de la Nación), la pretensión de la obra social actora
consiste en obtener que se deje sin efecto un acto administrativo (reso-
lución 666/05), dictado por la Superintendecia de Servicios de Salud
en virtud de la cual le aplicó una multa por incumplir con lo previsto
en el art. 42 incs. a) y c) de la ley 23.661.
En tales condiciones, es mi parecer que corresponde que la Justi-
cia Nacional en lo Contencioso Administrativo Federal entienda en
esta causa en donde se cuestiona la sanción de carácter administrati-
vo, impuesta por un órgano estatal en ejercicio de la función adminis-
trativa (doctrina de Fallos: 316:2768 y 317:308).

809
DE JUSTICIA DE LA NACION
330
Ello es así, puesto que para resolver la cuestión en debate se debe-
rán aplicar normas y principios propios del derecho público, donde
resulta clara la prioritaria relevancia que los aspectos propios del de-
recho administrativo asumen para su solución (Fallos: 327:471). En
tales condiciones, la materia en debate, su contenido jurídico y el dere-
cho que se intenta hacer valer, permite considerar al sub lite como una
causa contencioso administrativa, en los términos del art. 45, inc. a),
de la ley 13.998.
– V –
En tales condiciones, opino que este proceso debe continuar su trá-
mite ante la Cámara Nacional de Apelaciones en lo Contencioso Ad-
ministrativo Federal, por intermedio de su Sala I. Buenos Aires, 31 de
octubre de 2006. Laura M. Monti.
```

### [span 6] header_pagina (30660–30660)
```
808
```

### [span 7] header_pagina (30661–30661)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 8] header_pagina (30662–30662)
```
330
```

### [span 9] header_pagina (30695–30695)
```
809
```

### [span 10] header_pagina (30696–30696)
```
DE JUSTICIA DE LA NACION
```

### [span 11] header_pagina (30697–30697)
```
330
```

### [span 12] cuerpo_mayoria (30711–30719)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 13 de marzo de 2007.
Autos y Vistos:
De conformidad con lo dictaminado por la señora Procuradora Fis-
cal, se declara que resulta competente para conocer en las actuaciones
la Sala I de la Cámara Nacional de Apelaciones en lo Contencioso
Administrativo Federal, a la que se le remitirán. Hágase saber a la
Sala III de la Cámara Nacional de Apelaciones en lo Civil y Comercial
Federal.
```

### Borde inferior (transición al próximo caso)
**Estado**: `gap_con_residuo` | linea_fin_real=30719 | linea_inicio_proximo_caso=30725 | delta=5
**Alertas**: `firma_multilinea_partida_por_fin_real`

| Línea | Clasificación | Texto |
|------:|---------------|-------|
| 30720 | `firma_arrastrada` | RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S. |
| 30721 | `firma_arrastrada` | FAYT — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA. |
| 30722 | `vacia` |  |
| 30723 | `header_pagina` | 810 |
| 30724 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |


---

## 330_p625 — Federico, Irma Iris

**Localización**
- Archivo: `LibroVol330.1.md`
- Páginas catálogo: 625–628 | Página consultada: 628
- Líneas catálogo: 23557–23661 | Línea fin real: 23662 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 23557–23557 | 1 |
| 2 | catch_all | 23558–23563 | 6 |
| 3 | caratula | 23564–23564 | 1 |
| 4 | sumario [1] | 23565–23571 | 7 |
| 5 | sumario [2] | 23572–23580 | 9 |
| 6 | dictamen | 23581–23648 | 68 |
| 7 | header_pagina | 23587–23587 | 1 |
| 8 | header_pagina | 23588–23588 | 1 |
| 9 | header_pagina | 23589–23589 | 1 |
| 10 | header_pagina | 23626–23626 | 1 |
| 11 | header_pagina | 23627–23627 | 1 |
| 12 | header_pagina | 23628–23628 | 1 |
| 13 | cuerpo_mayoria | 23649–23656 | 8 |
| 14 | firma | 23657–23658 | 2 |
| 15 | catch_all | 23659–23659 | 1 |
| 16 | header_pagina | 23660–23660 | 1 |
| 17 | header_pagina | 23661–23661 | 1 |
| 18 | header_pagina | 23662–23662 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=7 (6.6% del bloque, n=106)

---

### [span 1] header_pagina (23557–23557)
```
330
```

### [span 2] catch_all (23558–23563)
```
actuaciones el Juzgado de Primera Instancia en lo Civil y Comercial
Nº 1 de Colón, Provincia de Entre Ríos, al que se le remitirán. Hágase
saber al Juzgado Federal de Primera Instancia de Concepción del Uru-
guay.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA.
```

### [span 3] caratula (23564–23564)
```
IRMA IRIS FEDERICO V. UNION PERSONAL
```

### [span 4] sumario [1] (23565–23571)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Generalidades.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Generalidades.
De acuerdo con las pautas previstas en los artículos 4º, 10 y 352 del Código Pro-
cesal Civil y Comercial de la Nación, resulta extemporánea la declaración de
incompetencia adoptada luego de haber recaído sentencia de primera instancia
que pone fin al proceso y sin que el tema de competencia haya sido objeto de
agravios por el recurrente.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] sumario [2] (23572–23580)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Generalidades.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Generalidades.
Si bien la demanda dirigida contra una obra social corresponde al fuero federal,
debe declararse la competencia de la justicia local para entender en el recurso
contra la sentencia de primera instancia, pues el reenvío a la justicia de excep-
ción importaría someter cuestiones ya consideradas y decididas en el ámbito de
otro tribunal, generando un evidente retardo injustificado en el trámite de las
actuaciones, que por su naturaleza deben resolverse rápidamente atendiendo a
los derechos que se intenta proteger.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 6] dictamen (23581–23648)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
Los magistrados integrantes de la Sala I de la Cámara de Apela-
ción y Garantías en lo Penal y de la Cámara Federal de Apelaciones,

626
FALLOS DE LA CORTE SUPREMA
330
del Departamento Judicial de Mar del Plata, Provincia de Buenos Ai-
res, discrepan en torno a la competencia para entender en la presente
causa.
El tribunal de alzada provincial, al conocer en virtud del recurso
de apelación incoado por la demandada contra la sentencia del juez de
grado, declaró de oficio su incompetencia para conocer en la causa con
fundamento en que la demanda se dirige contra una obra social –Conf.
leyes 23.660 y 23.661–, y entender en ella, exige precisar el sentido y
alcance de normas federales e invoca la doctrina sentada por V.E. en
el precedente “Wraage”, publicada en Fallos: 326:3535 (Ver fojas
179/186 vta.).
Recibida la causa por la Cámara Nacional, sus titulares, no admi-
tieron la radicación aduciendo que, la sustanciación de la causa ante
su jurisdicción importaría generar una situación que va en desmedro
del principio de celeridad procesal y buen servicio de justicia, pudien-
do configurarse en el caso una privación de justicia (Ver fs. 202).
En tales condiciones, se suscitó una contienda que corresponde
resolver a V.E., de conformidad con lo dispuesto por el artículo 24,
inciso 7º, del decreto-ley 1285/58, texto según ley 21.708.
– II –
Advierto que, de una interpretación armónica de las pautas pre-
vistas en los artículos 4º, 10 y 352 del Código Procesal Civil y Comer-
cial de la Nación, la resolución del tribunal de alzada local –Ver
fs. 179/186 vta.– en cuanto se declara de oficio incompetente, devino
extemporánea, toda vez que, según se desprende de las constancias de
autos, dicha decisión fue adoptada luego de haber recaído sentencia
de primera instancia que pone fin a este proceso y sin que el tema de
competencia haya sido objeto de agravios por el recurrente (Ver
fs. 142/149 vta.). En tal sentido, V.E. tiene reiteradamente dicho que
las contiendas de competencia no pueden prosperar después de dicta-
do tal acto procesal (Ver doctrina de Fallos: 302:101 y jurisprudencia
emanada en el precedente “Rezk”, publicada en Fallos: 324:2493).
Por otro lado, y a mayor abundamiento, cabe destacar que si bien
es cierto que las cuestiones discutidas en la presente causa guardan
sustancial analogía con las debatidas en el precedente “Kogan”, con

627
DE JUSTICIA DE LA NACION
330
sentencia de V.E. del 25 de noviembre de 2005 (Fallos: 328:4095), –por
tratarse de una materia propia de la justicia federal–, no es menos
cierto que, sumado a las particularidades procesales reseñadas en el
párrafo precedente, el reenvió de la causa al fuero federal, importaría
someter cuestiones ya consideradas y decididas en el ámbito de otro
tribunal (ver doctrina de Fallos: 301:514, entre otros). Tal situación
generaría, además, un evidente retardo injustificado en el trámite de
las actuaciones, lo que por su naturaleza deben tener un trámite abre-
viado atendiendo a los derechos que se intentan proteger, y afectan el
principio de seguridad jurídica y economía procesal (ver autos: “Pechini
Dante Pio c/ FEMEDICA –Federación Médica Gremial de la Cap. Fed.
s/ amparo”. S.C. Comp. 902, L. XLII, dictamen del 27 de septiembre de
2006).
Por todo lo expuesto, dentro del limitado marco cognoscitivo en el
que se tienen que resolver las cuestiones de competencia, estimo que
corresponde dirimir la contienda y disponer que compete a la Sala I de
la Cámara de Apelación y Garantías en lo Penal, del Departamento
Judicial de Mar del Plata, Provincia de Buenos Aires, entender en el
recurso pendiente de resolución. Buenos Aires, 10 de noviembre de
2006. Marta A. Beiró de Gonçalvez.
```

### [span 7] header_pagina (23587–23587)
```
626
```

### [span 8] header_pagina (23588–23588)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] header_pagina (23589–23589)
```
330
```

### [span 10] header_pagina (23626–23626)
```
627
```

### [span 11] header_pagina (23627–23627)
```
DE JUSTICIA DE LA NACION
```

### [span 12] header_pagina (23628–23628)
```
330
```

### [span 13] cuerpo_mayoria (23649–23656)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 6 de marzo de 2007.
Autos y Vistos:
De conformidad con lo dictaminado por la señora Procuradora Fis-
cal subrogante, remítanse las actuaciones a la Sala I de la Cámara de
Apelación y Garantías en lo Penal del Departamento Judicial de Mar
del Plata, Provincia de Buenos Aires. Hágase saber a la Cámara Fede-
ral de Apelaciones de Mar del Plata.
```

### [span 14] firma (23657–23658)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — JUAN CARLOS MAQUEDA.
```

### [span 15] catch_all (23659–23659)
```

```

### [span 16] header_pagina (23660–23660)
```
628
```

### [span 17] header_pagina (23661–23661)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 18] header_pagina (23662–23662)
```
330
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=23662 | linea_inicio_proximo_caso=23662 | delta=-1
**Alertas**: `solapado_con_proximo`


---

## 330_p119 — Martínez, Rita Mabel c/ Provincia de Corrientes | Provincia de Corrientes (Martínez, Rita Mabel c/)

**Localización**
- Archivo: `LibroVol330.1.md`
- Páginas catálogo: 119–120 | Página consultada: 120
- Líneas catálogo: 4281–4312 | Línea fin real: 4338 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 4281–4281 | 1 |
| 2 | catch_all | 4282–4285 | 4 |
| 3 | caratula | 4286–4286 | 1 |
| 4 | sumario [1] | 4287–4293 | 7 |
| 5 | sumario [2] | 4294–4300 | 7 |
| 6 | cuerpo_mayoria | 4301–4333 | 33 |
| 7 | header_pagina | 4311–4311 | 1 |
| 8 | header_pagina | 4312–4312 | 1 |
| 9 | header_pagina | 4313–4313 | 1 |
| 10 | firma | 4334–4335 | 2 |
| 11 | catch_all | 4336–4338 | 3 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=7 (12.07% del bloque, n=58)

---

### [span 1] header_pagina (4281–4281)
```
330
```

### [span 2] catch_all (4282–4285)
```
oficio a la Suprema Corte de la Provincia a fin de que tome conoci-
miento de la decisión del día de la fecha.
Libradas las cédulas correspondientes, vuelva para que el Tribu-
nal se pronuncie con relación al dictamen de la señora Procuradora
```

### [span 3] caratula (4286–4286)
```
Fiscal obrante a fs. 146/148.
```

### [span 4] sumario [1] (4287–4293)
**Header**: CARLOS S. FAYT.
**Atribución**: (sin atribución detectada)
```
CARLOS S. FAYT.
Demanda interpuesta por los Dres. Diego Jorge Lavado, Carlos Varela Alvarez,
Pablo Gabriel Salinas y Alfredo Guevara Escayola.
Contestan ministro de Justicia y Derechos Humanos de la Nación: Dr. Alberto
J. Iribarne y el subsecretario de Justicia de la Provincia de Mendoza: Dr. Gus-
tavo E. Castiñeira de Dios.
RITA MABEL MARTINEZ V. PROVINCIA DE CORRIENTES
```

### [span 5] sumario [2] (4294–4300)
**Header**: CADUCIDAD DE LA INSTANCIA.
**Atribución**: (sin atribución detectada)
```
CADUCIDAD DE LA INSTANCIA.
La circunstancia de tratarse de un juicio voluntario susceptible de ser iniciado
nuevamente no obsta a la declaración de caducidad de la instancia pues ello no
invalida la obligación, propia de la parte interesada, de adoptar las medidas
necesarias tendientes a activar el procedimiento para evitar las consecuencias
de su inactividad, pues ellas resultan un medio idóneo para determinar la pre-
sunción de interés en la acción que se promueve.
```

### [span 6] cuerpo_mayoria (4301–4333)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 13 de febrero de 2007.
Autos y Vistos; Considerando:
1º) Que a fs. 10 se presenta la Provincia de Corrientes y solicita
que se declare la caducidad de la instancia en las presentes actuacio-
nes por haber transcurrido el plazo previsto por el art. 310, inc. 2º del
Código Procesal Civil y Comercial de la Nación. Corrido el pertinente
traslado, a fs. 13 lo contesta la parte actora y se opone por las razones
que aduce.

120
FALLOS DE LA CORTE SUPREMA
330
2º) Que le asiste razón a la incidentista. En efecto desde la resolu-
ción dictada el 11 de mayo de 2006 (ver fs. 6) hasta el 24 de octubre de
2006 –fecha en que se solicitó la perención– ha transcurrido con exce-
so el plazo previsto por la citada norma legal sin que la parte actora
haya realizado actividad alguna a fin de impulsar el procedimiento y
sin que se verifique ninguna de las circunstancias eximentes que pre-
vé el art. 313, inc. 3º del código del rito.
3º) Que carece de relevancia el argumento esgrimido por la de-
mandante en cuanto a que se trataría de un juicio voluntario suscepti-
ble de ser iniciado nuevamente, toda vez que ello no invalida la obliga-
ción, propia de la parte interesada, de adoptar las medidas necesarias
tendientes a activar el procedimiento para evitar las consecuencias de
su inactividad, pues ellas resultan un medio idóneo para determinar
la presunción de interés en la acción que se promueve (Fallos: 320:2762;
y causa E.111.XXVIII. “El Inca de Hughes S.C.A. c/ Buenos Aires, Pro-
vincia de s/ daños y perjuicios”, pronunciamiento del 19 de noviembre
de 1996, entre otros).
Por ello, se resuelve: Hacer lugar a la caducidad de instancia opues-
ta por la Provincia de Corrientes a fs. 10. Con costas (arts. 68, 69 y 73
del Código Procesal Civil y Comercial de la Nación). Notifíquese.
```

### [span 7] header_pagina (4311–4311)
```
120
```

### [span 8] header_pagina (4312–4312)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] header_pagina (4313–4313)
```
330
```

### [span 10] firma (4334–4335)
```
RICARDO LUIS LORENZETTI — CARLOS S. FAYT — ENRIQUE SANTIAGO
PETRACCHI — JUAN CARLOS MAQUEDA.
```

### [span 11] catch_all (4336–4338)
```
Nombre de la actora: Rita Mabel Martínez. Dr. Jorge A. Cannata.
Nombre de la demandada: Provincia de Corrientes. Dr. Eleazar Christian
Meléndez.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=4338 | linea_inicio_proximo_caso=4313 | delta=-26
**Alertas**: `solapado_con_proximo`


---

## 330_p1618 — López, Miguel Angel

**Localización**
- Archivo: `LibroVol330.2.md`
- Páginas catálogo: 1618–1620 | Página consultada: 1620
- Líneas catálogo: 11093–11163 | Línea fin real: 11180 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 11093–11093 | 1 |
| 2 | catch_all | 11094–11103 | 10 |
| 3 | caratula | 11104–11104 | 1 |
| 4 | sumario [1] | 11105–11113 | 9 |
| 5 | sumario [2] | 11114–11128 | 15 |
| 6 | header_pagina | 11126–11126 | 1 |
| 7 | header_pagina | 11127–11127 | 1 |
| 8 | header_pagina | 11128–11128 | 1 |
| 9 | dictamen | 11129–11168 | 40 |
| 10 | header_pagina | 11162–11162 | 1 |
| 11 | header_pagina | 11163–11163 | 1 |
| 12 | header_pagina | 11164–11164 | 1 |
| 13 | cuerpo_mayoria | 11169–11178 | 10 |
| 14 | firma | 11179–11180 | 2 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=10 (11.36% del bloque, n=88)

---

### [span 1] header_pagina (11093–11093)
```
330
```

### [span 2] catch_all (11094–11103)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 10 de abril de 2007.
Autos y Vistos:
De conformidad con lo dictaminado por el señor Procurador Gene-
ral, se declara que resulta competente para conocer en las actuaciones
la Sala A de la Cámara Federal de Apelaciones de Rosario, a la que se
le remitirán. Hágase saber a la Sala B de la Cámara Nacional de Ape-
laciones en lo Penal Económico.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — ENRIQUE
SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI.
```

### [span 3] caratula (11104–11104)
```
MIGUEL ANGEL LOPEZ
```

### [span 4] sumario [1] (11105–11113)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Causas penales. Violación
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia federal. Causas penales. Violación
de normas federales.
Si bien la ley 26.052 modificó sustancialmente la competencia material para al-
gunas de las conductas típicas contenidas en la ley de estupefacientes, al asignar
su conocimiento a la justicia local, siempre que las provincias adhieran a ese
régimen legal, ello no importa desconocer el carácter prioritario de la jurisdic-
ción federal en la materia, tal como se ve reflejado en la regla del art. 4º para el
caso de duda.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] sumario [2] (11114–11128)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Causas penales. Violación
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Competencia federal. Causas penales. Violación
de normas federales.
Corresponde declarar la competencia de la justicia federal respecto de la causa
seguida ante la justicia local por infracción al art. 14 de la ley 23.737 si el impu-
tado tiene otro proceso en trámite ante el fuero de excepción por infracción a
dicha ley, pues si bien la acumulación por conexidad sólo puede invocarse en
conflictos en que participen jueces nacionales, esta regla no resulta aplicable
cuando rige la norma establecida en el art. 3º de la ley 26.052, ya que las reglas
de conexidad están inspiradas en asegurar una más expedita y uniforme admi-
nistración de justicia.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.

1619
DE JUSTICIA DE LA NACION
330
```

### [span 6] header_pagina (11126–11126)
```
1619
```

### [span 7] header_pagina (11127–11127)
```
DE JUSTICIA DE LA NACION
```

### [span 8] header_pagina (11128–11128)
```
330
```

### [span 9] dictamen (11129–11168)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
La presente contienda negativa de competencia suscitada entre el
Juzgado de Garantías Nº 1, y el Juzgado Federal Nº 2, ambos de Morón,
Provincia de Buenos Aires, se refiere a la causa seguida contra Miguel
Angel López por infracción al artículo 14 de la ley 23.737.
Al certificar que el imputado tenía una causa en trámite, por ante
el fuero de excepción también por infracción a la mencionada ley, la
juez local se declaró incompetente con sustento en el artículo 3 de la
ley 26.052 (fs. 24/vta.).
Por su parte, el magistrado federal no aceptó esa atribución, al
considerar con sustento en doctrina de V.E. que las reglas de acumu-
lación por conexidad sólo pueden invocarse en conflictos en que parti-
cipen jueces nacionales (fs. 32/3).
Con la insistencia de la juez que previno y la elevación del inciden-
te a la Corte quedó formalmente planteada esta contienda.
A mi modo de ver la jurisprudencia invocada por el magistrado
nacional no resulta aplicable al caso en que rige la norma establecida
en el artículo 3º de la ley 26.052.
Al respecto creo conveniente señalar, que esa norma modificó
sustancialmente la competencia material para algunas de las conduc-
tas típicas contenidas en la ley de estupefacientes, al asignar su cono-
cimiento a la justicia local, siempre que las provincias adhieran a ese
régimen legal, lo que de ningún modo importa desconocer el carácter
prioritario de la jurisdicción federal en la materia, tal como incluso se
ve reflejado en la regla del artículo 4º.
Aprecio entonces que lo dispuesto en el artículo 3º responde a ese
mismo principio, en tanto la aplicación de las reglas de conexidad es-
tán inspiradas en asegurar una más expedita y uniforme administra-
ción de justicia (Fallos: 311:695; 311:1514 y 1515; 312:645 entre mu-
chos otros), sin que por lo tanto tampoco resulte aplicable en estos
supuestos la limitación establecida por el artículo 7º de la ley 26.052.

1620
FALLOS DE LA CORTE SUPREMA
330
En ese sentido, toda vez que contra el imputado tramita una causa
por ante el Juzgado Federal Nº 2 de Morón (ver fs. 15/17 y 19/21) opi-
no que corresponde a ese tribunal seguir conociendo en la presente.
Buenos Aires, 11 de septiembre de 2006. Eduardo Ezequiel Casal.
```

### [span 10] header_pagina (11162–11162)
```
1620
```

### [span 11] header_pagina (11163–11163)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 12] header_pagina (11164–11164)
```
330
```

### [span 13] cuerpo_mayoria (11169–11178)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 10 de abril de 2007.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que corresponde remitirse en razón de brevedad, se
declara que deberá entender en la causa en la que se originó el presen-
te incidente el Juzgado Federal en lo Criminal y Correccional Nº 2 de
Morón, Provincia de Buenos Aires, al que se le remitirá. Hágase saber
al Juzgado de Garantías Nº 1 del Departamento Judicial de la locali-
dad mencionada.
```

### [span 14] firma (11179–11180)
```
ELENA I. HIGHTON DE NOLASCO — ENRIQUE SANTIAGO PETRACCHI — JUAN
CARLOS MAQUEDA — E. RAÚL ZAFFARONI — CARMEN M. ARGIBAY.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=11180 | linea_inicio_proximo_caso=11164 | delta=-17
**Alertas**: `solapado_con_proximo`


---

## 330_p1303 — Compañía de Seguros La Mercantil Andina S.A. c/ Corporación del Mercado Central de Buenos Aires y otro | Corporación del

**Localización**
- Archivo: `LibroVol330.1.md`
- Páginas catálogo: 1303–1305 | Página consultada: 1305
- Líneas catálogo: 49686–49751 | Línea fin real: 49765 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 49686–49686 | 1 |
| 2 | catch_all | 49687–49700 | 14 |
| 3 | caratula | 49701–49701 | 1 |
| 4 | sumario [1] | 49702–49705 | 4 |
| 5 | dictamen | 49706–49752 | 47 |
| 6 | header_pagina | 49712–49712 | 1 |
| 7 | header_pagina | 49713–49713 | 1 |
| 8 | header_pagina | 49714–49714 | 1 |
| 9 | header_pagina | 49750–49750 | 1 |
| 10 | header_pagina | 49751–49751 | 1 |
| 11 | header_pagina | 49752–49752 | 1 |
| 12 | cuerpo_mayoria | 49753–49763 | 11 |
| 13 | firma | 49764–49765 | 2 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=14 (17.5% del bloque, n=80)

---

### [span 1] header_pagina (49686–49686)
```
330
```

### [span 2] catch_all (49687–49700)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 27 de marzo de 2007.
Autos y Vistos: “Competencia Nº 1101.XLII. ‘Banco Central de la
República Argentina c/ Carranza, Alfredo s/ ejecutivo’; y otros”.
De conformidad con lo dictaminado por la señora Procuradora Fis-
cal subrogante, se declara que resulta competente para conocer en las
actuaciones, el Juzgado Federal de Primera Instancia Nº 2 de Rosa-
rio, al que se le remitirán por intermedio de la Sala B de la cámara
federal de apelaciones de dicha localidad. Hágase saber al Juzgado en
lo Civil y Comercial de Segunda Nominación del Departamento Judi-
cial de Venado Tuerto, Provincia de Santa Fe.
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — CARLOS S.
FAYT — ENRIQUE SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA.
COMPAÑIA DE SEGUROS LA MERCANTIL ANDINA S.A.
```

### [span 3] caratula (49701–49701)
```
V. CORPORACION DEL MERCADO CENTRAL DE BUENOS AIRES Y OTRO
```

### [span 4] sumario [1] (49702–49705)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Por la materia. Varias.
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia federal. Por la materia. Varias.
Corresponde a la justicia federal conocer en las causas en que la Corporación del
Mercado Central de Buenos Aires sea parte.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] dictamen (49706–49752)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
El titular del Juzgado Nacional de Primera Instancia en lo Civil y
Comercial Federal Nº 5 (ver fs. 60) y los Jueces integrantes de la Sala

1304
FALLOS DE LA CORTE SUPREMA
330
D de la Cámara Nacional de Apelaciones en lo Comercial (Ver
fs. 385/386), discrepan en torno a la competencia para entender en la
presente causa.
El magistrado federal, haciendo suyos los argumentos esgrimi-
dos por el Sr. Representante del Ministerio Público Fiscal, se declaró
incompetente para entender en la causa con fundamento en que la
pretensión objeto de la demanda se ha vertebrado en las previsiones
contenidas en el artículo 80 de la Ley de Seguros, circunstancia ésta,
que, adujo, excluye la intervención del fuero de excepción tanto en
razón de la materia como de la persona, para seguir conociendo en la
causa.
A fojas 385/386, la Cámara Nacional de Apelaciones en lo Comer-
cial, confirmó el decisorio del juez de primera instancia, en cuanto
hizo lugar a la excepción de incompetencia incoado por la demandada
–Corporación del Mercado Central de Buenos Aires (ver fs. 365/366)–
con sustento en que la presente acción se dirige contra una entidad de
carácter pública interestadual, cuya actividad ha sido declarada como
de interés nacional (Conf. leyes Nº 17.422 y 19.227).
En tales condiciones, se suscitó un conflicto negativo de competen-
cia que corresponde dirimir a V.E., en los términos del artículo 24,
inciso 7º, del decreto-ley 1285/58, texto según ley 21.708.
– II –
Cabe recordar, que V.E. ha señalado que corresponde a la justicia
federal conocer en las causas en que la Corporación del Mercado Cen-
tral de Buenos Aires sea parte (Fallos: 310:1420, entre muchos otros),
supuesto que se verifica en la causa, desde que la actora ha demanda-
do nominal y sustancialmente a la entidad indicada (Ver fojas 53/57).
Por lo expuesto, dentro del estrecho marco de conocimiento en el
que se tiene que resolver las cuestiones de competencia y toda vez que
la institución aquí demandada tiene su domicilio legal en el ámbito
territorial de la Provincia de Buenos Aires –Ver fs. 53; 164; 166 vta. y
168–, opino, que compete a la justicia federal con asiento en esta últi-
ma jurisdicción, entender en las presentes actuaciones en debate. Bue-
nos Aires, 19 de diciembre de 2006. Marta A. Beiró de Gonçalvez.

1305
DE JUSTICIA DE LA NACION
330
```

### [span 6] header_pagina (49712–49712)
```
1304
```

### [span 7] header_pagina (49713–49713)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 8] header_pagina (49714–49714)
```
330
```

### [span 9] header_pagina (49750–49750)
```
1305
```

### [span 10] header_pagina (49751–49751)
```
DE JUSTICIA DE LA NACION
```

### [span 11] header_pagina (49752–49752)
```
330
```

### [span 12] cuerpo_mayoria (49753–49763)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 27 de marzo de 2007.
Autos y Vistos:
De conformidad con lo dictaminado por la señora Procuradora Fis-
cal subrogante, se declara la competencia de la justicia federal con
asiento en la localidad de San Martín. A los fines correspondientes,
remítanse las actuaciones a la cámara federal de apelaciones de dicha
localidad y hágase saber al Juzgado Nacional de Primera Instancia en
lo Comercial Nº 24, por intermedio de la Sala D de la cámara de apela-
ciones de ese fuero y al Juzgado Nacional de Primera Instancia en lo
Civil y Comercial Federal Nº 5.
```

### [span 13] firma (49764–49765)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — ENRIQUE
SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=49765 | linea_inicio_proximo_caso=49752 | delta=-14
**Alertas**: `solapado_con_proximo`


---
