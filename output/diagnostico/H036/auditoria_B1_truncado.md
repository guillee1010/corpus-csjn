# Auditoría de fallos
Generado: 2026-05-17 23:37
Versión: 1.0.0
Comando: `diag_h036 --categoria B1_truncado --n 10 --seed 42`
Casos auditados: 10
Seed: 42
Borde inferior: solapado_con_proximo=8, gap_con_residuo=2 | alertas totales: 13

---

## 329_p6060 — Ornstein Mendoza, Bernardo Cristóbal

**Localización**
- Archivo: `LibroVol329.4.md`
- Páginas catálogo: 6060–6064 | Página consultada: 6064
- Líneas catálogo: 44083–44231 | Línea fin real: 44246 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 44083–44083 | 1 |
| 2 | catch_all | 44084–44101 | 18 |
| 3 | caratula | 44102–44102 | 1 |
| 4 | sumario [1] | 44103–44111 | 9 |
| 5 | header_pagina | 44109–44109 | 1 |
| 6 | header_pagina | 44110–44110 | 1 |
| 7 | header_pagina | 44111–44111 | 1 |
| 8 | sumario [2] | 44112–44118 | 7 |
| 9 | sumario [3] | 44119–44127 | 9 |
| 10 | dictamen | 44128–44232 | 105 |
| 11 | header_pagina | 44148–44148 | 1 |
| 12 | header_pagina | 44149–44149 | 1 |
| 13 | header_pagina | 44150–44150 | 1 |
| 14 | header_pagina | 44188–44188 | 1 |
| 15 | header_pagina | 44189–44189 | 1 |
| 16 | header_pagina | 44190–44190 | 1 |
| 17 | header_pagina | 44230–44230 | 1 |
| 18 | header_pagina | 44231–44231 | 1 |
| 19 | header_pagina | 44232–44232 | 1 |
| 20 | cuerpo_mayoria | 44233–44243 | 11 |
| 21 | firma | 44244–44246 | 3 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=18 (10.98% del bloque, n=164)

---

### [span 1] header_pagina (44083–44083)
```
329
```

### [span 2] catch_all (44084–44101)
```
prochados a los funcionarios de la casa matriz y las demás sucursales,
en las operaciones realizadas en el marco del programa de apoyo a la
construcción (ver informe de fs. 407/445), opino que, corresponde a la
justicia local continuar con el trámite de la causa que originó este inci-
dente. Buenos Aires, 6 de noviembre de 2006. Luis Santiago González
Warcalde.
FALLO DE LA CORTE SUPREMA
Buenos Aires, 27 de diciembre de 2006.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que cabe remitirse en razón de brevedad, se declara
que deberá entender en la causa en la que se originó el presente inci-
dente, el Juzgado de Garantías Nº 3 del Departamento Judicial de La
Plata, Provincia de Buenos Aires, al que se le remitirá. Hágase saber
al Juzgado Nacional en lo Criminal de Instrucción Nº 49.
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — E. RAÚL ZAFFARONI — RICARDO LUIS LORENZETTI —
CARMEN M. ARGIBAY.
```

### [span 3] caratula (44102–44102)
```
BERNARDO CRISTOBAL ORNSTEIN MENDOZA
```

### [span 4] sumario [1] (44103–44111)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Inhibitoria: plantea-
**Atribución**: (sin atribución detectada)
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Inhibitoria: plantea-
miento y trámite.
Es presupuesto necesario para una concreta contienda negativa de competencia
que los jueces entre quienes se suscita se la atribuyan recíprocamente.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.

6061
DE JUSTICIA DE LA NACION
329
```

### [span 5] header_pagina (44109–44109)
```
6061
```

### [span 6] header_pagina (44110–44110)
```
DE JUSTICIA DE LA NACION
```

### [span 7] header_pagina (44111–44111)
```
329
```

### [span 8] sumario [2] (44112–44118)
**Header**: JURISDICCION Y COMPETENCIA: Competencia federal. Causas penales. Delitos que
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia federal. Causas penales. Delitos que
obstruyen el normal funcionamiento de las instituciones nacionales.
El encubrimiento de un delito cometido en la Capital de la República afecta a la
administración de justicia nacional, siempre y cuando surja, con absoluta niti-
dez, que el imputado por ese delito no ha tenido participación alguna en la sus-
tracción.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 9] sumario [3] (44119–44127)
**Header**: JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
nes penales. Pluralidad de delitos.
Aunque no consta en el expediente el estado de la investigación realizada en
Capital Federal, en razón de la relación de alternatividad entre la sustracción
del vehículo y el encubrimiento, corresponde a la justicia nacional en lo criminal
de instrucción profundizar la investigación respecto de dicha sustracción, a par-
tir de los elementos recabados con motivo de su secuestro en la Provincia de
Mendoza, aunque no haya sido parte en la contienda.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 10] dictamen (44128–44232)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
Entre la Sala Segunda de la Suprema Corte de Justicia de la Pro-
vincia de Mendoza, y el Juzgado de Garantías Nº 3 del departamento
judicial de La Matanza, Provincia de Buenos Aires, se suscitó la pre-
sente contienda negativa de competencia en la causa instruida con
motivo del secuestro en Mendoza, de un vehículo sustraído unos días
antes en la Capital Federal, que se hallaba en poder de Bernardo Cris-
tóbal Ornstein, y presentaba su numeración individualizadora adul-
terada.
Frente a la sentencia dictada por el Cuarto Juzgado Correccional
de la Primera Circunscripción Judicial de aquella ciudad que lo absol-
vió por infracción al artículo 289, inciso 3º, del Código Penal, y lo con-
denó por el delito de encubrimiento, su defensa interpuso recurso de
casación ante la Corte provincial, que anuló lo actuado a partir de la
citación a juicio, y declaró la incompetencia a favor de los tribunales
de La Matanza, Provincia de Buenos Aires, con fundamento en que
ese último delito se había consumado en ese ámbito territorial
(fs. 139/142).

6062
FALLOS DE LA CORTE SUPREMA
329
El magistrado bonaerense, por su parte, rechazó tal atribución al
considerar que la sustracción había sido cometida en la Capital Fede-
ral y que, por ende, al tratarse de un delito que afectaba a la adminis-
tración de justicia nacional debía entender el fuero de excepción, siem-
pre y cuando surgiera con nitidez que el imputado no había tenido
vinculación con la sustracción (fs. 151/152).
Con la insistencia del juzgado mendocino, quedó trabada la pre-
sente contienda (fs. 164).
Es doctrina de V.E. que es presupuesto necesario para una concre-
ta contienda negativa de competencia que los jueces entre quienes se
suscita se la atribuyan recíprocamente (Fallos: 305:2204; 306:591;
311:1965; 314:239; 318:1834; 319:144 y 323:772), lo que no sucede en
el sub lite, en tanto que el juez de la Matanza no consideró que debían
intervenir los tribunales de Mendoza, sino que se limitó a sostener
que correspondía conocer a la justicia nacional.
No obstante, para el supuesto de que el Tribunal decidiera dejar
de lado ese óbice formal por razones de economía procesal y la necesi-
dad de dar pronto fin a esta contienda, me pronunciaré sobre el fondo
(Fallos: 312:1624; 313:655 y 824).
En tal sentido, y en la inteligencia de que la nulidad dispuesta por
el tribunal declinante no alcanza en sus efectos a la absolución respec-
to de la infracción al artículo 289, inciso 3º, del Código Penal, por la
que no medió acusación ni recurso, pienso que en cuanto al hallazgo
del automotor en poder de Bernardo Cristóbal Orstein, los escasos ele-
mentos reunidos hasta el presente no alcanzan, en el caso, para califi-
car con el grado de certeza que esta etapa procesal requiere, el delito
que se habría cometido.
Por ello, entiendo que resulta indispensable contar con una ade-
cuada investigación y un auto de mérito que defina su situación jurídi-
ca respecto de la sustracción (Fallos: 317:499; 325:950 y 326:918), es-
pecialmente si se repara en que no surge que se haya realizado ningu-
na medida tendiente a dilucidar ese aspecto (Comp. 2004 L.XXXIX,
“Zolloco, Ruben s/ averiguación ilícito”, resuelta el 16 de marzo de 2004).
Por otra parte, creo oportuno recordar que V.E. tiene establecido,
a través de numerosos precedentes, que el encubrimiento de un delito
cometido en la Capital de la República afecta a la administración de

6063
DE JUSTICIA DE LA NACION
329
justicia nacional (Fallos: 308:2522 y 322:1216, entre otros), siempre y
cuando surja, con absoluta nitidez, que el imputado por ese delito no
ha tenido participación alguna en la sustracción (Fallos: 325:898 y
950; y Competencia Nº 228; L.XLII, “Agquín, Miguel Raúl s/ encubri-
miento”, resuelta el 29 de agosto de 2006).
A ello cabe agregar las contradicciones que surgen de las constan-
cias de fs. 9, 10 y 11, y de la declaración indagatoria de fs. 32/34 acerca
de la supuesta adquisición del rodado lo que, en su caso, debería esta-
blecerse con mayor precisión dada su relevancia para discernir el tri-
bunal competente por razón del territorio.
Por lo tanto –aunque no consta en el expediente el estado de la
investigación realizada en Capital (vid. fs. 41)– estimo que, en razón
de la relación de alternatividad existente entre ambas infracciones
(Fallos: 312:1624; 315:1617; 320:2016) corresponde a la justicia nacio-
nal en lo criminal de instrucción profundizar la investigación respecto
de la sustracción del vehículo (fs. 5 y vta. y 41), a partir de los elemen-
tos recabados con motivo de su secuestro en la Provincia de Mendoza
(Competencias Nº 1634, L. XXXVI in re “Viano, Norma Beatriz s/ en-
cubrimiento”, Nº 2094, L. XXXVII in re “Saira, Roberto Juan s/ encu-
brimiento calificado, etc.” y Nº 1709; L. XLI, “Aloise, Daniel Roberto s/
falsificación de marcas y contraseñas, resueltas el 10 de abril de 2001,
19 de marzo de 2002 y 23 de mayo de 2006, respectivamente) aunque
no haya sido parte en la contienda (Fallos: 317:929; 318:182 y 323:2032,
entre otros) y sin perjuicio de lo que ulteriormente resulte.
Asimismo, también advierto que según el acta de fs. 8, se incautó
un formulario (fs. 15/16) donde surge que el automóvil habría sido ve-
rificado “sin novedad” el 29 de septiembre de 2004, y una constancia
de retención de documentación (fs. 11/14) que habría sido confecciona-
da en la localidad bonaerense de San Justo, a nombre del imputado
Orstein.
No obstante esas circunstancias, pienso que ante las conclusiones
a que se arribó en el informe pericial de fs. 23/24 respecto de las nume-
raciones individualizadoras del vehículo, se torna necesario investi-
gar acerca de la autenticidad o falsedad de esa documentación, máxi-
me cuando la presunta verificación del rodado se habría realizado sin
tenerse a la vista aquélla que lo identifique, atento la fecha de la refe-
rida constancia de retención de fs. 11/14. Buenos Aires, 14 de noviem-
bre de 2006. Eduardo Ezequiel Casal.

6064
FALLOS DE LA CORTE SUPREMA
329
```

### [span 11] header_pagina (44148–44148)
```
6062
```

### [span 12] header_pagina (44149–44149)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 13] header_pagina (44150–44150)
```
329
```

### [span 14] header_pagina (44188–44188)
```
6063
```

### [span 15] header_pagina (44189–44189)
```
DE JUSTICIA DE LA NACION
```

### [span 16] header_pagina (44190–44190)
```
329
```

### [span 17] header_pagina (44230–44230)
```
6064
```

### [span 18] header_pagina (44231–44231)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 19] header_pagina (44232–44232)
```
329
```

### [span 20] cuerpo_mayoria (44233–44243)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 27 de diciembre de 2006.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que cabe remitirse en razón de brevedad, se declara
que deberá entender en la presente causa el Juzgado Nacional en lo
Criminal de Instrucción Nº 25, al que se le remitirá. Hágase saber al
Juzgado de Garantías Nº 3 del Departamento Judicial de La Matan-
za, Provincia de Buenos Aires, a la Sala Segunda de la Suprema Corte
de Justicia de la Provincia de Mendoza y al Cuarto Juzgado Correccio-
nal de la Primera Circunscripción Judicial de esta última provincia.
```

### [span 21] firma (44244–44246)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — E. RAÚL ZAFFARONI — RICARDO LUIS LORENZETTI —
CARMEN M. ARGIBAY.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=44246 | linea_inicio_proximo_caso=44232 | delta=-15
**Alertas**: `solapado_con_proximo`


---

## 329_p1541 — Torres, Justo Santiago

**Localización**
- Archivo: `LibroVol329.2.md`
- Páginas catálogo: 1541–1554 | Página consultada: 1554
- Líneas catálogo: 6397–6892 | Línea fin real: 6408 (status_fin=`fin_dentro_bloque`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 6397–6397 | 1 |
| 2 | caratula | 6398–6398 | 1 |
| 3 | sumario [1] | 6399–6404 | 6 |
| 4 | sumario [2] | 6405–6408 | 4 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=0 (0.0% del bloque, n=12)

---

### [span 1] header_pagina (6397–6397)
```
329
```

### [span 2] caratula (6398–6398)
```
JUSTO SANTIAGO TORRES
```

### [span 3] sumario [1] (6399–6404)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Principios generales.
La doctrina de la arbitrariedad tiende a resguardar la defensa en juicio y el debi-
do proceso, al exigir que las sentencias sean fundadas y constituyan una deriva-
ción razonada del derecho vigente con aplicación a las circunstancias comproba-
das de la causa.
```

### [span 4] sumario [2] (6405–6408)
**Header**: RECURSO DE CASACION.
**Atribución**: (sin atribución detectada)
```
RECURSO DE CASACION.
La decisión que, sin atender a la sustancia real del planteo, desestimó la vía
casatoria por considerar que el rechazo de una excepción de falta de acción no
encuadraba en los supuestos de resoluciones recurribles que contiene el art. 457
```

### Borde inferior (transición al próximo caso)
**Estado**: `gap_con_residuo` | linea_fin_real=6408 | linea_inicio_proximo_caso=6893 | delta=484
**Alertas**: `voto_disidencia_individual_en_gap`, `caratula_siguiente_en_gap`

| Línea | Clasificación | Texto |
|------:|---------------|-------|
| 6409 | `apertura_proximo_caso` | del Código Procesal Penal de la Nación vulnera los principios de defensa en juicio |
| 6410 | `no_clasificable` | y debido proceso ya que se basa en una interpretación irrazonable del citado |
| 6411 | `no_clasificable` | artículo que no armoniza con las restantes normas del ordenamiento jurídico. |
| 6412 | `no_clasificable` | RECURSO DE CASACION. |
| 6413 | `no_clasificable` | Si el art. 457 del Código Procesal Penal hace referencia al concepto de sentencia |
| 6414 | `no_clasificable` | definitiva al igual que el art. 14 de la ley 48 y el art. 6 de la ley 4055 y la Corte |
| 6415 | `no_clasificable` | desarrolló el criterio de sentencia equiparable a definitiva para aquellos pronun- |
| 6416 | `no_clasificable` | ciamientos que, si bien no ponen fin al pleito, generan un perjuicio de imposible |
| 6417 | `no_clasificable` | o tardía reparación ulterior que requiere una tutela inmediata, cabe concluir que |
| 6418 | `no_clasificable` | el concepto de sentencia definitiva para el recurso extraordinario no difiere del |
| 6419 | `no_clasificable` | establecido para el recurso de casación, habida cuenta el carácter de tribunal |
| 6420 | `no_clasificable` | intermedio de la cámara homónima. |
| 6421 | `no_clasificable` | RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio- |
| 6422 | `no_clasificable` | nes anteriores a la sentencia definitiva. Varias. |
| 6423 | `no_clasificable` | Corresponde hacer excepción a la doctrina según la cual no revisten la calidad de |
| 6424 | `no_clasificable` | sentencia definitiva, las resoluciones cuya consecuencia sea la obligación de se- |
| 6425 | `no_clasificable` | guir sometido a proceso penal, en los supuestos en los que el recurso se dirige a |
| 6426 | `no_clasificable` | lograr la plena efectividad de la prohibición de la doble persecución penal. |
| 6427 | `no_clasificable` | RECURSO EXTRAORDINARIO: Requisitos propios. Tribunal superior. |
| 6428 | `no_clasificable` | La restricción del recurso extraordinario a la impugnación de aquellas senten- |
| 6429 | `no_clasificable` | cias que provengan de un determinado tribunal o clase de ellos sólo es válida si |
| 6430 | `no_clasificable` | se encuentra prevista en una cláusula legal, como la del art. 14, primer párrafo |
| 6431 | `no_clasificable` | de la ley 48 que se refiere a los “superiores tribunales de provincia” o la del |
| 6432 | `vacia` |  |
| 6433 | `header_pagina` | 1542 |
| 6434 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 6435 | `header_pagina` | 329 |
| 6436 | `no_clasificable` | art. 6º de la ley 4055 que lo hacía respecto de las cámaras de apelaciones en lo |
| 6437 | `firma_arrastrada` | federal y de la Capital (Disidencia de la Dra. Carmen M. Argibay). |
| 6438 | `no_clasificable` | RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y |
| 6439 | `no_clasificable` | generalidades. |
| 6440 | `no_clasificable` | Desde que se encuentra en vigencia el nuevo sistema procesal penal (leyes 23.984 |
| 6441 | `no_clasificable` | y 24.050), el art. 6º de la ley 4055 debe entenderse parcialmente derogado, pues |
| 6442 | `no_clasificable` | las cámaras de apelación en lo penal ya no dictan las sentencias definitivas en |
| 6443 | `no_clasificable` | sentido propio, es decir, el pronunciamiento final de absolución o condena (Disi- |
| 6444 | `firma_arrastrada` | dencia de la Dra. Carmen M. Argibay). |
| 6445 | `no_clasificable` | RECURSO EXTRAORDINARIO: Requisitos propios. Tribunal superior. |
| 6446 | `no_clasificable` | Hasta tanto el Congreso dicte una ley correctiva, corresponde examinar los re- |
| 6447 | `no_clasificable` | cursos extraordinarios planteados contra resoluciones de tribunales nacionales |
| 6448 | `no_clasificable` | según las condiciones de admisibilidad que han persistido en el derecho positivo, |
| 6449 | `no_clasificable` | la concurrencia de una sentencia que se pronuncie de manera final en contra del |
| 6450 | `no_clasificable` | derecho federal invocado en alguna de las formas descriptas en el art. 14 de la |
| 6451 | `firma_arrastrada` | ley 48 (Disidencia de la Dra. Carmen M. Argibay). |
| 6452 | `no_clasificable` | RECURSO EXTRAORDINARIO: Requisitos propios. Tribunal superior. |
| 6453 | `no_clasificable` | En ausencia de una regla dictada por el Congreso que restrinja el alcance del |
| 6454 | `no_clasificable` | recurso extraordinario a las sentencias dictadas por la Cámara de Casación, no |
| 6455 | `no_clasificable` | corresponde denegar el recurso extraordinario por no haberse deducido contra |
| 6456 | `firma_arrastrada` | un fallo de ese tribunal (Disidencia de la Dra. Carmen M. Argibay). |
| 6457 | `no_clasificable` | RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Concepto y |
| 6458 | `no_clasificable` | generalidades. |
| 6459 | `no_clasificable` | El cumplimiento de ambos requisitos –superior tribunal y sentencia definitiva– |
| 6460 | `no_clasificable` | no puede ser examinado de manera desvinculada al establecer los casos en que |
| 6461 | `no_clasificable` | una resolución previa a la sentencia final deba ser “equiparada” a definitiva; a |
| 6462 | `no_clasificable` | los efectos del recurso extraordinario, son “equiparables” aquellos pronuncia- |
| 6463 | `no_clasificable` | mientos que resuelven en contra de un interés que se aduce protegido por una |
| 6464 | `no_clasificable` | norma contenida en la Constitución Nacional o en las leyes federales que no |
| 6465 | `no_clasificable` | subsistirá una vez dictado el pronunciamiento final (Disidencia de la Dra. Car- |
| 6466 | `firma_arrastrada` | men M. Argibay). |
| 6467 | `no_clasificable` | CORTE SUPREMA. |
| 6468 | `no_clasificable` | Si ya se ha formado una mayoría de opiniones en el sentido de otorgar a la Cáma- |
| 6469 | `no_clasificable` | ra Nacional de Casación Penal el carácter de un tribunal intermedio que debe |
| 6470 | `no_clasificable` | intervenir en todos aquellos casos en que se haya planteado una cuestión apta |
| 6471 | `vacia` |  |
| 6472 | `header_pagina` | 1543 |
| 6473 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 6474 | `header_pagina` | 329 |
| 6475 | `no_clasificable` | para ser tratada por la Corte a través del recurso extraordinario, no tendrá lugar |
| 6476 | `no_clasificable` | una deliberación entre los jueces del Tribunal acerca de la presunta afectación |
| 6477 | `no_clasificable` | constitucional alegada, lo que hace improcedente que, pese a su disidencia, la |
| 6478 | `no_clasificable` | ministra se pronuncie aisladamente sobre el tema de fondo (Disidencia de la |
| 6479 | `firma_arrastrada` | Dra. Carmen M. Argibay). |
| 6480 | `no_clasificable` | DICTAMEN DE LA PROCURACIÓN GENERAL |
| 6481 | `no_clasificable` | Suprema Corte: |
| 6482 | `no_clasificable` | – I – |
| 6483 | `no_clasificable` | La Sala A de la Cámara Federal de Apelaciones de Mendoza, re- |
| 6484 | `no_clasificable` | solvió confirmar la resolución de primera instancia que no hizo lugar a |
| 6485 | `no_clasificable` | la excepción de falta de acción presentada por la defensa oficial de |
| 6486 | `no_clasificable` | Justo Santiago Torres (fojas 1/3 vuelta). Contra ese pronunciamiento |
| 6487 | `no_clasificable` | se interpuso recurso de casación, que fue declarado inadmisible por el |
| 6488 | `no_clasificable` | tribunal (fojas 15/16). Presentada la queja ante la Cámara Nacional |
| 6489 | `no_clasificable` | de Casación Penal, su Sala II decidió desestimarla (fojas 22/vuelta). |
| 6490 | `no_clasificable` | Contra esta resolución se dedujo recurso extraordinario federal |
| 6491 | `no_clasificable` | (fojas 23/29), cuyo rechazo (fojas 30/vuelta), dio lugar a la formulación |
| 6492 | `no_clasificable` | del presente remedio directo (32/38 vuelta). |
| 6493 | `no_clasificable` | – II – |
| 6494 | `no_clasificable` | 1. La defensa oficial introdujo la excepción de falta de acción por |
| 6495 | `no_clasificable` | entender que el sobreseimiento dictado por el Juzgado Nacional en lo |
| 6496 | `no_clasificable` | Penal Económico Nº 3 de esta ciudad, y confirmado por la cámara de |
| 6497 | `no_clasificable` | apelaciones del fuero, había extinguido la acción penal emergente de |
| 6498 | `no_clasificable` | la conducta imputada en esa sede, y una nueva atribución de los mis- |
| 6499 | `no_clasificable` | mos hechos en la jurisdicción federal mendocina implicaba desconocer |
| 6500 | `no_clasificable` | las proyecciones de la cosa juzgada y una doble persecución penal. |
| 6501 | `no_clasificable` | Al convalidar el rechazo del planteo, la Cámara Federal de |
| 6502 | `no_clasificable` | Mendoza, de consuno con el criterio esbozado por el magistrado de |
| 6503 | `no_clasificable` | primera instancia y el representante de este Ministerio Público, consi- |
| 6504 | `no_clasificable` | deró que los hechos imputados a Torres en ambas jurisdicciones resul- |
| 6505 | `vacia` |  |
| 6506 | `header_pagina` | 1544 |
| 6507 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 6508 | `header_pagina` | 329 |
| 6509 | `no_clasificable` | taban material y temporalmente escindibles, por lo que concluyó que |
| 6510 | `no_clasificable` | la garantía del non bis in idem no se encontraba afectada en el sub |
| 6511 | `no_clasificable` | judice. |
| 6512 | `no_clasificable` | 2. Interpuesto el recurso de casación, éste fue declarado inadmisi- |
| 6513 | `no_clasificable` | ble por ese tribunal, al entender que obstaba a su procedencia formal |
| 6514 | `no_clasificable` | la falta de sentencia definitiva, toda vez que la decisión recurrida ha- |
| 6515 | `no_clasificable` | cía posible la prosecución del proceso. |
| 6516 | `no_clasificable` | Disconforme con esta solución, la defensa formuló queja por dene- |
| 6517 | `no_clasificable` | gación de la vía casatoria, sosteniendo, con cita de la jurisprudencia |
| 6518 | `no_clasificable` | de Fallos: 299:221; 300:1273 y 314:377, que la resolución por la que se |
| 6519 | `no_clasificable` | somete al imputado a un proceso por un hecho en virtud del cual ya |
| 6520 | `no_clasificable` | fue juzgado con anterioridad, es equiparable a un pronunciamiento |
| 6521 | `no_clasificable` | definitivo, en tanto podría ocasionar al agraviado un perjuicio no sus- |
| 6522 | `no_clasificable` | ceptible de reparación ulterior. Este argumento no convenció al a quo, |
| 6523 | `no_clasificable` | quien, compartiendo la tesis de la Cámara Federal mendocina, recha- |
| 6524 | `no_clasificable` | zó el remedio directo. |
| 6525 | `no_clasificable` | Ello motivó que la parte interpusiera recurso extraordinario, invo- |
| 6526 | `no_clasificable` | cando las garantías de doble instancia y non bis in idem, por conside- |
| 6527 | `no_clasificable` | rar que la denegatoria a revisar el rechazo de la excepción, expone a |
| 6528 | `no_clasificable` | su pupilo al riesgo de ser condenado por un hecho en el cual ya recayó |
| 6529 | `no_clasificable` | sobreseimiento firme en otro juicio; argumentos estos que fueron re- |
| 6530 | `no_clasificable` | novados al introducirse la queja en examen. |
| 6531 | `no_clasificable` | – III – |
| 6532 | `no_clasificable` | De antemano he de adelantar mi opinión en el sentido de que co- |
| 6533 | `no_clasificable` | rresponde el rechazo del presente remedio directo, pues la mera invo- |
| 6534 | `no_clasificable` | cación del agravio relativo a la violación de la garantía que prohíbe la |
| 6535 | `no_clasificable` | doble persecución penal, no exhibe, en el caso, entidad bastante para |
| 6536 | `no_clasificable` | acceder a esta instancia extraordinaria, toda vez que no concurre el |
| 6537 | `no_clasificable` | requisito de fundamentación suficiente. |
| 6538 | `no_clasificable` | Veamos. |
| 6539 | `no_clasificable` | 1. Tal como quedó reseñado en el apartado anterior, la Cámara |
| 6540 | `no_clasificable` | Federal de Mendoza, en coincidencia con el criterio del juez instructor |
| 6541 | `no_clasificable` | y el fiscal, descartó en el caso la configuración de una lesión al princi- |
| 6542 | `no_clasificable` | pio del non bis in idem, luego de determinar que las conductas atribui- |
| 6543 | `vacia` |  |
| 6544 | `header_pagina` | 1545 |
| 6545 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 6546 | `header_pagina` | 329 |
| 6547 | `no_clasificable` | das a Justo Santiago Torres en una y otra causa se refieren a distintos |
| 6548 | `no_clasificable` | sucesos delictivos. |
| 6549 | `no_clasificable` | En efecto, con tal objetivo la cámara comenzó su relato recordando |
| 6550 | `no_clasificable` | que los hechos que originaron el proceso de su jurisdicción, se relacio- |
| 6551 | `no_clasificable` | nan con la primigenia investigación de una amplia y compleja estruc- |
| 6552 | `no_clasificable` | tura delictiva que se dedicaría al comercio internacional de estupefa- |
| 6553 | `no_clasificable` | cientes, y operaría en la ciudad de Mendoza a través de dos líneas de |
| 6554 | `no_clasificable` | tráfico perfectamente diferenciadas. |
| 6555 | `no_clasificable` | Sobre esta base, precisó que Torres fue imputado y procesado con |
| 6556 | `no_clasificable` | prisión preventiva por su participación activa en una de esas líneas, |
| 6557 | `no_clasificable` | colaborando en el traslado de heroína desde Ecuador a la Argentina, |
| 6558 | `no_clasificable` | guardándola momentáneamente en aquella ciudad andina, e intervi- |
| 6559 | `no_clasificable` | niendo en los trámites y financiamiento del o los viajes de Luis Eduar- |
| 6560 | `no_clasificable` | do Morán, quien sería la persona elegida para introducir subrepticia- |
| 6561 | `no_clasificable` | mente la droga en los Estados Unidos de Norteamérica. |
| 6562 | `no_clasificable` | De esta manera concluyó que estos hechos se consumaron con pre- |
| 6563 | `no_clasificable` | cedencia e independencia a los que posteriormente fueron objeto de |
| 6564 | `no_clasificable` | imputación en el fuero penal económico, donde el sindicado Torres fue |
| 6565 | `no_clasificable` | sobreseído en orden al delito de tentativa de contrabando de estupefa- |
| 6566 | `no_clasificable` | cientes, por intentar extraer heroína del territorio argentino con des- |
| 6567 | `no_clasificable` | tino a la ciudad de Nueva York, oculta en el respaldar y partes latera- |
| 6568 | `no_clasificable` | les de una mochila color negra que llevaba Morán cuando es detenido |
| 6569 | `no_clasificable` | por la policía, el once de diciembre de 2000, al intentar subir a un |
| 6570 | `no_clasificable` | avión en el aeropuerto internacional de Ezeiza. |
| 6571 | `no_clasificable` | 2. Ahora bien, aún cuando la parte insistió que en la causa trami- |
| 6572 | `no_clasificable` | tada en esa jurisdicción se investiga la misma realidad histórica que |
| 6573 | `no_clasificable` | la que fuera sobreseída en esta Capital, lo cierto es que no se hizo |
| 6574 | `no_clasificable` | cargo de refutar adecuadamente los fundamentos conclusivos de la |
| 6575 | `no_clasificable` | cámara de apelaciones. |
| 6576 | `no_clasificable` | En este sentido, puede advertirse que durante toda su actividad |
| 6577 | `no_clasificable` | recursiva, más exactamente desde la interposición del remedio |
| 6578 | `no_clasificable` | casatorio hasta el planteo del recurso extraordinario federal, la defen- |
| 6579 | `no_clasificable` | sa omitió poner en evidencia, con razones valederas y de forma clara e |
| 6580 | `no_clasificable` | inequívoca, la identidad absoluta de objeto procesal, condición necesa- |
| 6581 | `no_clasificable` | ria para aplicar la regla del non bis in idem (conf. doctrina de Fallos: |
| 6582 | `no_clasificable` | 299:221; 308:1678; 314:377; 315:2680 y 321:1848, entre otros). Muy |
| 6583 | `no_clasificable` | por el contrario, sólo circunscribió su crítica a que aquel tribunal ha- |
| 6584 | `vacia` |  |
| 6585 | `header_pagina` | 1546 |
| 6586 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 6587 | `header_pagina` | 329 |
| 6588 | `no_clasificable` | bría confundido el eadem res con la distinta calificación legal que el |
| 6589 | `no_clasificable` | juez de grado, al momento de la intimación, le otorgó a los hechos, |
| 6590 | `no_clasificable` | pero sin demostrar que esa variación de encuadre no tuviera como |
| 6591 | `no_clasificable` | base, precisamente, la diversidad fáctica. |
| 6592 | `no_clasificable` | 3. Las deficiencias apuntadas me permiten advertir, por otro lado, |
| 6593 | `no_clasificable` | que el recurrente, además de no haber introducido nuevos argumen- |
| 6594 | `no_clasificable` | tos que hicieran viable su reclamo federal, efectuando un análisis com- |
| 6595 | `no_clasificable` | parativo riguroso para concluir con un juicio de identidad, tampoco |
| 6596 | `no_clasificable` | alegó que el razonamiento empleado por la cámara de apelaciones, al |
| 6597 | `no_clasificable` | valorar la disímil materialidad de los hechos involucrados, se encuen- |
| 6598 | `no_clasificable` | tre viciado de arbitrariedad o resulte adverso a los principios de la |
| 6599 | `no_clasificable` | lógica o el sentido común, circunstancia ésta que impide avanzar en |
| 6600 | `no_clasificable` | un análisis crítico respecto a la validez del fallo. |
| 6601 | `no_clasificable` | Por ello, y más allá de los avatares territoriales, que señala la re- |
| 6602 | `no_clasificable` | currente, seguramente para ver qué reglas de competencia o conexión |
| 6603 | `no_clasificable` | correspondía aplicar, estimo necesario concluir, que no se ha demos- |
| 6604 | `no_clasificable` | trado que las acciones desplegadas por Justo Santiago Torres en terri- |
| 6605 | `no_clasificable` | torio mendocino, al introducir y acopiar momentáneamente la heroí- |
| 6606 | `no_clasificable` | na traída desde Ecuador, constituyan conductas que no sean perfecta- |
| 6607 | `no_clasificable` | mente escindibles de las maniobras realizadas en el ámbito capitali- |
| 6608 | `no_clasificable` | no, para intentar –por medio de otra persona– el envío de esa droga a |
| 6609 | `no_clasificable` | los Estados Unidos de Norteamérica. |
| 6610 | `no_clasificable` | Esta posibilidad de separar el enjuiciamiento según los distintos |
| 6611 | `no_clasificable` | tramos delictivos de determinada operación compleja de tráfico |
| 6612 | `no_clasificable` | interjurisdiccional de estupefacientes, guarda correlación –mutatis |
| 6613 | `no_clasificable` | mutandi– con la regla de derecho internacional del artículo 36, párra- |
| 6614 | `no_clasificable` | fo segundo, apartado “a”, inciso “i” de la Convención Unica de Estupe- |
| 6615 | `no_clasificable` | facientes, celebrada en Nueva York en 1961 y enmendada por el Pro- |
| 6616 | `no_clasificable` | tocolo de Modificación suscripto en Ginebra el 25 de marzo de 1972 |
| 6617 | `no_clasificable` | –incorporados a nuestra legislación por el decreto-ley 7672/63 y por la |
| 6618 | `no_clasificable` | ley 20.449, respectivamente–, que prescribe que las acciones de expor- |
| 6619 | `no_clasificable` | tar e introducir deben considerarse como infracciones distintas si son |
| 6620 | `no_clasificable` | cometidas en diferentes países, ya que lesionan ambos ordenamientos |
| 6621 | `no_clasificable` | y tienen distintos momentos de consumación, aún cuando puedan re- |
| 6622 | `no_clasificable` | sultar de un único designio (conf. doctrina de Fallos: 324:1146, con su |
| 6623 | `no_clasificable` | cita de Fallos: 311:2518; y dictamen de esta Procuración General en la |
| 6624 | `no_clasificable` | causa A. 234. XXXVII “Arla Pita, Tamara y otros s/ extradición”, pu- |
| 6625 | `no_clasificable` | blicada en Fallos: 325:2777). |
| 6626 | `vacia` |  |
| 6627 | `header_pagina` | 1547 |
| 6628 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 6629 | `header_pagina` | 329 |
| 6630 | `no_clasificable` | En consecuencia, y si bien el principio contenido en aquella nor- |
| 6631 | `no_clasificable` | mativa convencional corresponde a los procesos de extradición entre |
| 6632 | `no_clasificable` | los Estados partes, entiendo que puede utilizarse como guía interpre- |
| 6633 | `no_clasificable` | tativa en el derecho interno, cuando los hechos ocurrieron en diferen- |
| 6634 | `no_clasificable` | tes provincias y las operaciones tuvieron un origen y un destino final |
| 6635 | `no_clasificable` | foráneo. Ello permitiría sostener el criterio según el cual las conductas |
| 6636 | `no_clasificable` | de tráfico incriminadas –introducción y exportación de heroína del te- |
| 6637 | `no_clasificable` | rritorio argentino–, pueden investigarse y juzgarse en forma separa- |
| 6638 | `no_clasificable` | da una de la otra, por haber afectado con su comisión distintas juris- |
| 6639 | `no_clasificable` | dicciones federales (Fallos: 305:1499; 310:2842; 314:374; 315:2542, |
| 6640 | `no_clasificable` | entre otros). |
| 6641 | `no_clasificable` | – IV – |
| 6642 | `no_clasificable` | En mérito a lo expuesto, y al no haberse demostrado con acabada |
| 6643 | `no_clasificable` | suficiencia que lo decidido trasunte en el caso una efectiva violación a |
| 6644 | `no_clasificable` | la garantía constitucional del non bis in idem que permita su estudio a |
| 6645 | `no_clasificable` | la luz de la doctrina diseñada por el Tribunal, es mi opinión, tal como |
| 6646 | `no_clasificable` | lo he anticipado, que corresponde sin más el rechazo del presente re- |
| 6647 | `no_clasificable` | curso de hecho. Buenos Aires, 30 de agosto de 2004. Luis Santiago |
| 6648 | `no_clasificable` | González Warcalde. |
| 6649 | `no_clasificable` | FALLO DE LA CORTE SUPREMA |
| 6650 | `no_clasificable` | Buenos Aires, 9 de mayo de 2006. |
| 6651 | `apertura_proximo_caso` | Vistos los autos: “Recurso de hecho deducido por la defensa de Jus- |
| 6652 | `no_clasificable` | to Santiago Torres en la causa Torres, Justo Santiago s/ excepción”, |
| 6653 | `no_clasificable` | para decidir sobre su procedencia. |
| 6654 | `no_clasificable` | Considerando: |
| 6655 | `no_clasificable` | 1º) Que el recurso extraordinario federal –cuya denegación dio ori- |
| 6656 | `no_clasificable` | gen a esta queja– fue interpuesto contra la resolución de la Sala II de |
| 6657 | `no_clasificable` | la Cámara Nacional de Casación Penal que desestimó la queja por |
| 6658 | `no_clasificable` | rechazo del remedio casatorio deducido contra el fallo de la Cámara |
| 6659 | `no_clasificable` | Federal de Apelaciones de Mendoza (Sala A) que confirmó la decisión |
| 6660 | `no_clasificable` | de primera instancia que no había hecho lugar a la excepción de falta |
| 6661 | `vacia` |  |
| 6662 | `header_pagina` | 1548 |
| 6663 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 6664 | `header_pagina` | 329 |
| 6665 | `no_clasificable` | de acción (art. 339, inc. 2º, del Código Procesal Penal) interpuesta por |
| 6666 | `no_clasificable` | la defensa de Justo Santiago Torres. |
| 6667 | `no_clasificable` | En dicho planteo se alegaba que en la causa 8998-D, “Fiscal c/ |
| 6668 | `no_clasificable` | Rodríguez, Andino s/ ley 23.737”, del Juzgado Federal de Mendoza |
| 6669 | `no_clasificable` | Nº 3 se estaba llevando a cabo una doble persecución penal, puesto |
| 6670 | `no_clasificable` | que se le atribuían a Torres los mismos hechos –aunque con diferente |
| 6671 | `no_clasificable` | calificación legal (art. 7 en función del art. 5 –inc. c– de la ley 23.737, |
| 6672 | `no_clasificable` | en la modalidad de transporte de estupefacientes)– por los que había |
| 6673 | `no_clasificable` | sido juzgado y sobreseído en la causa 11.183/01, “Torres, Justo San- |
| 6674 | `no_clasificable` | tiago s/ contrabando de estupefacientes”, del Juzgado Nacional en lo |
| 6675 | `no_clasificable` | Penal Económico Nº 3 de la Capital Federal. |
| 6676 | `no_clasificable` | 2º) Que el a quo, sin atender a la sustancia real del planteo efec- |
| 6677 | `no_clasificable` | tuado, desestimó la vía casatoria por considerar que el rechazo de una |
| 6678 | `no_clasificable` | excepción de falta de acción no encuadraba en los supuestos de resolu- |
| 6679 | `no_clasificable` | ciones recurribles que contiene el art. 457 del ordenamiento adjetivo. |
| 6680 | `no_clasificable` | 3º) Que el recurrente considera que el a quo incurrió en arbitrarie- |
| 6681 | `no_clasificable` | dad puesto que encontrándose afectado un derecho federal que es sus- |
| 6682 | `no_clasificable` | ceptible de tutela inmediata, no le atribuyó carácter de definitiva a la |
| 6683 | `no_clasificable` | sentencia impidiendo así el examen de la impugnación. |
| 6684 | `no_clasificable` | 4º) Que, como es sabido, la doctrina invocada por el apelante tien- |
| 6685 | `no_clasificable` | de a resguardar la defensa en juicio y el debido proceso, al exigir que |
| 6686 | `no_clasificable` | las sentencias sean fundadas y constituyan una derivación razonada |
| 6687 | `no_clasificable` | del derecho vigente con aplicación a las circunstancias comprobadas |
| 6688 | `no_clasificable` | de la causa (Fallos: 311:948, 2314, 2547; 312:2507, entre otros). |
| 6689 | `no_clasificable` | 5º) Que en el sub lite se han vulnerado esos principios dado que la |
| 6690 | `no_clasificable` | exclusión de la competencia del a quo se basa en una interpretación |
| 6691 | `no_clasificable` | irrazonable del art. 457 del Código Procesal Penal que no armoniza |
| 6692 | `no_clasificable` | con las restantes normas del ordenamiento jurídico. |
| 6693 | `no_clasificable` | En efecto, la regulación establecida por el ordenamiento procesal |
| 6694 | `no_clasificable` | vigente no impide la revisión de sentencias como la recurrida en las |
| 6695 | `no_clasificable` | presentes actuaciones, si se tiene en cuenta que el art. 457 del Código |
| 6696 | `no_clasificable` | Procesal Penal hace referencia al concepto de sentencia definitiva al |
| 6697 | `no_clasificable` | igual que el art. 14 de la ley 48 y el art. 6 de la ley 4055, y que desde |
| 6698 | `no_clasificable` | antaño esta Corte ha desarrollado el criterio de sentencia equiparable |
| 6699 | `no_clasificable` | a definitiva para aquellos pronunciamientos que, si bien no ponen fin |
| 6700 | `no_clasificable` | al pleito, generan un perjuicio de imposible o tardía reparación ulte- |
| 6701 | `vacia` |  |
| 6702 | `header_pagina` | 1549 |
| 6703 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 6704 | `header_pagina` | 329 |
| 6705 | `no_clasificable` | rior que requiere una tutela inmediata. Es por ello que cabe concluir |
| 6706 | `no_clasificable` | que el concepto de sentencia definitiva para el recurso extraordinario |
| 6707 | `no_clasificable` | no difiere del establecido para el recurso de casación, habida cuenta el |
| 6708 | `no_clasificable` | carácter de tribunal intermedio de la cámara homónima (conf. causa |
| 6709 | `no_clasificable` | “Di Nunzio”, Fallos: 328:1108, considerando 12). |
| 6710 | `no_clasificable` | 6º) Que, sentado lo expuesto, cabe entonces señalar que el criterio |
| 6711 | `no_clasificable` | del a quo no se ajusta a la conocida jurisprudencia de esta Corte según |
| 6712 | `no_clasificable` | la cual corresponde hacer excepción a la doctrina según la cual no |
| 6713 | `no_clasificable` | revisten la calidad de sentencia definitiva, las resoluciones cuya con- |
| 6714 | `no_clasificable` | secuencia sea la obligación de seguir sometido a proceso penal, en los |
| 6715 | `no_clasificable` | supuestos en los que el recurso se dirige a lograr la plena efectividad |
| 6716 | `no_clasificable` | de la prohibición de la doble persecución penal (Fallos: 314:377, consi- |
| 6717 | `no_clasificable` | derandos 3º y 4º, entre otros). |
| 6718 | `no_clasificable` | 7º) Que, en consecuencia, la resolución impugnada guarda nexo |
| 6719 | `no_clasificable` | directo e inmediato con las garantías constitucionales de la defensa en |
| 6720 | `no_clasificable` | juicio y el debido proceso, por lo que resulta descalificable como acto |
| 6721 | `no_clasificable` | jurisdiccional válido, sin que esto implique abrir juicio sobre la proce- |
| 6722 | `no_clasificable` | dencia o improcedencia de la excepción articulada. |
| 6723 | `no_clasificable` | Por ello y oído el señor Procurador Fiscal, se hace lugar a la queja, |
| 6724 | `no_clasificable` | se declara procedente el recurso extraordinario y se deja sin efecto la |
| 6725 | `no_clasificable` | sentencia apelada. Hágase saber y remítase la queja la que oportuna- |
| 6726 | `no_clasificable` | mente se le agregará a la causa principal. |
| 6727 | `firma_arrastrada` | ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — CARLOS |
| 6728 | `firma_arrastrada` | S. FAYT (según su voto) — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI — |
| 6729 | `firma_arrastrada` | RICARDO LUIS LORENZETTI — CARMEN M. ARGIBAY (en disidencia). |
| 6730 | `voto_disidencia_individual` | VOTO DEL SEÑOR MINISTRO DOCTOR DON CARLOS S. FAYT |
| 6731 | `no_clasificable` | Considerando: |
| 6732 | `no_clasificable` | 1º) Que el recurso extraordinario federal –cuya denegación dio ori- |
| 6733 | `no_clasificable` | gen a esta queja– fue interpuesto contra la resolución de la Sala II de |
| 6734 | `no_clasificable` | la Cámara Nacional de Casación Penal que desestimó la queja por |
| 6735 | `vacia` |  |
| 6736 | `header_pagina` | 1550 |
| 6737 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 6738 | `header_pagina` | 329 |
| 6739 | `no_clasificable` | rechazo del remedio casatorio deducido contra el fallo de la Cámara |
| 6740 | `no_clasificable` | Federal de Apelaciones de Mendoza (Sala A) que confirmó la decisión |
| 6741 | `no_clasificable` | de primera instancia que no había hecho lugar a la excepción de falta |
| 6742 | `no_clasificable` | de acción (art. 339, inc. 2º, del Código Procesal Penal) interpuesta por |
| 6743 | `no_clasificable` | la defensa de Justo Santiago Torres. |
| 6744 | `no_clasificable` | En dicho planteo se alegaba que en la causa 8998-D, “Fiscal c/ |
| 6745 | `no_clasificable` | Rodríguez, Andino s/ ley 23.737”, del Juzgado Federal de Mendoza |
| 6746 | `no_clasificable` | Nº 3 se estaba llevando a cabo una doble persecución penal, puesto |
| 6747 | `no_clasificable` | que se le atribuían a Torres los mismos hechos –aunque con diferente |
| 6748 | `no_clasificable` | calificación legal (art. 7 en función del art. 5 –inc. c– de la ley 23.737, |
| 6749 | `no_clasificable` | en la modalidad de transporte de estupefacientes)– por los que había |
| 6750 | `no_clasificable` | sido juzgado y sobreseído en la causa 11.183/01, “Torres, Justo San- |
| 6751 | `no_clasificable` | tiago s/ contrabando de estupefacientes”, del Juzgado Nacional en lo |
| 6752 | `no_clasificable` | Penal Económico Nº 3 de la Capital Federal. |
| 6753 | `no_clasificable` | 2º) Que el a quo, sin atender a la sustancia real del planteo efec- |
| 6754 | `no_clasificable` | tuado, desestimó la vía casatoria por considerar que el rechazo de una |
| 6755 | `no_clasificable` | excepción de falta de acción no encuadraba en los supuestos de resolu- |
| 6756 | `no_clasificable` | ciones recurribles que contiene el art. 457 del ordenamiento adjetivo. |
| 6757 | `no_clasificable` | 3º) Que el recurrente considera que el a quo incurrió en arbitrarie- |
| 6758 | `no_clasificable` | dad puesto que encontrándose afectado un derecho federal que es sus- |
| 6759 | `no_clasificable` | ceptible de tutela inmediata, no le atribuyó carácter de definitiva a la |
| 6760 | `no_clasificable` | sentencia impidiendo así el examen de la impugnación. |
| 6761 | `no_clasificable` | 4º) Que, como es sabido, la doctrina invocada por el apelante tien- |
| 6762 | `no_clasificable` | de a resguardar la defensa en juicio y el debido proceso, al exigir que |
| 6763 | `no_clasificable` | las sentencias sean fundadas y constituyan una derivación razonada |
| 6764 | `no_clasificable` | del derecho vigente con aplicación a las circunstancias comprobadas |
| 6765 | `no_clasificable` | de la causa (Fallos: 311:948, 2314, 2547; 312:2507, entre otros). |
| 6766 | `no_clasificable` | 5º) Que en el sub lite se han vulnerado esos principios dado que la |
| 6767 | `no_clasificable` | exclusión de la competencia del a quo se basa en una interpretación |
| 6768 | `no_clasificable` | irrazonable del art. 457 del Código Procesal Penal que no armoniza |
| 6769 | `no_clasificable` | con las restantes normas del ordenamiento jurídico. |
| 6770 | `no_clasificable` | En efecto, la regulación establecida por el ordenamiento procesal |
| 6771 | `no_clasificable` | vigente no impide la revisión de sentencias como la recurrida en las |
| 6772 | `no_clasificable` | presentes actuaciones, si se tiene en cuenta que el art. 457 del Código |
| 6773 | `no_clasificable` | Procesal Penal hace referencia al concepto de sentencia definitiva al |
| 6774 | `no_clasificable` | igual que el art. 14 de la ley 48 y el art. 6 de la ley 4055, y que desde |
| 6775 | `vacia` |  |
| 6776 | `header_pagina` | 1551 |
| 6777 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 6778 | `header_pagina` | 329 |
| 6779 | `no_clasificable` | antaño esta Corte ha desarrollado el criterio de sentencia equiparable |
| 6780 | `no_clasificable` | a definitiva para aquellos pronunciamientos que, si bien no ponen fin |
| 6781 | `no_clasificable` | al pleito, generan un perjuicio de imposible o tardía reparación ulte- |
| 6782 | `no_clasificable` | rior que requiere una tutela inmediata. Es por ello que cabe concluir |
| 6783 | `no_clasificable` | que el concepto de sentencia definitiva para el recurso extraordinario |
| 6784 | `no_clasificable` | no difiere del establecido para el recurso de casación, habida cuenta el |
| 6785 | `no_clasificable` | carácter de tribunal intermedio de la cámara homónima. |
| 6786 | `no_clasificable` | 6º) Que, sentado lo expuesto, cabe entonces señalar que el criterio |
| 6787 | `no_clasificable` | del a quo no se ajusta a la conocida jurisprudencia de esta Corte según |
| 6788 | `no_clasificable` | la cual corresponde hacer excepción a la doctrina según la cual no |
| 6789 | `no_clasificable` | revisten la calidad de sentencia definitiva, las resoluciones cuya con- |
| 6790 | `no_clasificable` | secuencia sea la obligación de seguir sometido a proceso penal, en los |
| 6791 | `no_clasificable` | supuestos en los que el recurso se dirige a lograr la plena efectividad |
| 6792 | `no_clasificable` | de la prohibición de la doble persecución penal (Fallos: 314:377, |
| 6793 | `no_clasificable` | considerandos 3º y 4º, entre otros). |
| 6794 | `no_clasificable` | 7º) Que, en consecuencia, la resolución impugnada guarda nexo |
| 6795 | `no_clasificable` | directo e inmediato con las garantías constitucionales de la defensa en |
| 6796 | `no_clasificable` | juicio y el debido proceso, por lo que resulta descalificable como acto |
| 6797 | `no_clasificable` | jurisdiccional válido, sin que esto implique abrir juicio sobre la proce- |
| 6798 | `no_clasificable` | dencia o improcedencia de la excepción articulada. |
| 6799 | `no_clasificable` | Por ello y oído el señor Procurador Fiscal, se hace lugar a la queja, |
| 6800 | `no_clasificable` | se declara procedente el recurso extraordinario y se deja sin efecto la |
| 6801 | `no_clasificable` | sentencia apelada. Agréguese oportunamente la queja al principal. |
| 6802 | `no_clasificable` | Hágase saber y remítase. |
| 6803 | `firma_arrastrada` | CARLOS S. FAYT. |
| 6804 | `voto_disidencia_individual` | DISIDENCIA DE LA SEÑORA |
| 6805 | `firma_arrastrada` | MINISTRA DOCTORA DOÑA CARMEN M. ARGIBAY |
| 6806 | `no_clasificable` | Autos y Vistos: |
| 6807 | `no_clasificable` | 1º) La competencia apelada de esta Corte está sujeta a las “reglas |
| 6808 | `no_clasificable` | y excepciones que prescriba el Congreso.” (Artículo 117 de la Constitu- |
| 6809 | `no_clasificable` | ción Nacional). En materia penal, estas reglas y excepciones surgen |
| 6810 | `vacia` |  |
| 6811 | `header_pagina` | 1552 |
| 6812 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 6813 | `header_pagina` | 329 |
| 6814 | `no_clasificable` | de la confluencia de los artículos 6º de la ley 24.050, 24.2 del decreto- |
| 6815 | `no_clasificable` | ley 1285/58, ratificado por ley 14.467, 6º de la ley 4055 y 14 de la |
| 6816 | `no_clasificable` | ley 48. |
| 6817 | `no_clasificable` | La restricción del recurso extraordinario a la impugnación de aque- |
| 6818 | `no_clasificable` | llas sentencias que provengan de un determinado tribunal o clase de |
| 6819 | `no_clasificable` | ellos sólo es válida si se encuentra prevista en una cláusula legal, como |
| 6820 | `no_clasificable` | la del artículo 14, primer párrafo de la ley 48 que se refiere a los “supe- |
| 6821 | `no_clasificable` | riores tribunales de provincia” o la del artículo 6º de la ley 4.055 que lo |
| 6822 | `no_clasificable` | hacía respecto de las cámaras de apelaciones en lo federal y de la Ca- |
| 6823 | `no_clasificable` | pital. |
| 6824 | `no_clasificable` | 2º) Sin embargo, desde que se encuentra en vigencia el nuevo sis- |
| 6825 | `no_clasificable` | tema procesal penal (leyes 23.984 y 24.050), el artículo 6º de la ley |
| 6826 | `no_clasificable` | 4055 debe entenderse parcialmente derogado, pues las cámaras de |
| 6827 | `no_clasificable` | apelación en lo penal ya no dictan las sentencias definitivas en sentido |
| 6828 | `no_clasificable` | propio, es decir, el pronunciamiento final de absolución o condena. |
| 6829 | `no_clasificable` | Por consiguiente, hasta tanto el Congreso dicte una ley correctiva, |
| 6830 | `no_clasificable` | corresponde examinar los recursos extraordinarios planteados contra |
| 6831 | `no_clasificable` | resoluciones de tribunales nacionales según las condiciones de |
| 6832 | `no_clasificable` | admisibilidad que han persistido en el derecho positivo, a saber, la |
| 6833 | `no_clasificable` | concurrencia de una sentencia que se pronuncie de manera final en |
| 6834 | `no_clasificable` | contra del derecho federal invocado en alguna de las formas descriptas |
| 6835 | `no_clasificable` | en el artículo 14 de la ley 48. |
| 6836 | `no_clasificable` | Lo anterior determina que, en ausencia de una regla dictada por el |
| 6837 | `no_clasificable` | Congreso que restrinja el alcance del recurso extraordinario a las sen- |
| 6838 | `no_clasificable` | tencias dictadas por la Cámara de Casación, no corresponde denegar |
| 6839 | `no_clasificable` | el recurso extraordinario por no haberse deducido contra un fallo de |
| 6840 | `no_clasificable` | ese tribunal. |
| 6841 | `no_clasificable` | 3º) El cumplimiento de ambos requisitos (superior tribunal y sen- |
| 6842 | `no_clasificable` | tencia definitiva) no puede ser examinado de manera desvinculada |
| 6843 | `no_clasificable` | al establecer los casos en que una resolución previa a la sentencia |
| 6844 | `no_clasificable` | final deba ser “equiparada” a definitiva. A los efectos del recurso ex- |
| 6845 | `no_clasificable` | traordinario, son “equiparables” a la sentencia definitiva aquellos |
| 6846 | `no_clasificable` | pronunciamientos que resuelven en contra de un interés que se adu- |
| 6847 | `no_clasificable` | ce protegido por una norma contenida en la Constitución Nacional o |
| 6848 | `no_clasificable` | en las leyes federales que no subsistirá una vez dictado el pronuncia- |
| 6849 | `no_clasificable` | miento final. |
| 6850 | `vacia` |  |
| 6851 | `header_pagina` | 1553 |
| 6852 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 6853 | `header_pagina` | 329 |
| 6854 | `no_clasificable` | En el caso, según alega la defensa, la decisión que motivó el recur- |
| 6855 | `no_clasificable` | so resuelve en contra de la garantía que veda la doble persecución por |
| 6856 | `no_clasificable` | el mismo hecho consagrada por el artículo 18 de la Constitución Na- |
| 6857 | `no_clasificable` | cional y los artículos 8.4 de la Convención Americana sobre Derechos |
| 6858 | `no_clasificable` | Humanos y 14.7 del Pacto Internacional de Derechos Civiles y Políti- |
| 6859 | `no_clasificable` | cos, en función del artículo 75, inciso 22, principio constitucional que |
| 6860 | `no_clasificable` | no puede ser revisado en la sentencia definitiva, pues el derecho a no |
| 6861 | `no_clasificable` | ser sometido a proceso se extinguiría precisamente, con el dictado de |
| 6862 | `no_clasificable` | dicha sentencia que convertiría al procesado en condenado o absuelto. |
| 6863 | `no_clasificable` | Considero que ésta es la recta interpretación de la doctrina sentada |
| 6864 | `no_clasificable` | en Fallos: 290:393 y 300:642. En tales precedentes, la equiparación a |
| 6865 | `no_clasificable` | sentencia definitiva se apoyó en que la garantía constitucional invoca- |
| 6866 | `no_clasificable` | da era de carácter procesal y por lo tanto no podría la decisión judicial |
| 6867 | `no_clasificable` | sobre el punto ser revisada de manera eficaz en la sentencia definitiva |
| 6868 | `no_clasificable` | que, precisamente, es la conclusión o cierre del proceso. |
| 6869 | `no_clasificable` | 4º) No obstante lo expuesto, en esta causa ya se ha formado una |
| 6870 | `no_clasificable` | mayoría de opiniones en el sentido de otorgar a la Cámara Nacional |
| 6871 | `no_clasificable` | de Casación Penal el carácter de un tribunal intermedio que debe in- |
| 6872 | `no_clasificable` | tervenir en todos aquellos casos en que se haya planteado una cues- |
| 6873 | `no_clasificable` | tión federal apta para ser tratada por esta Corte a través del recurso |
| 6874 | `no_clasificable` | extraordinario. |
| 6875 | `no_clasificable` | Por tal razón, no tendrá lugar en esta oportunidad una delibera- |
| 6876 | `no_clasificable` | ción entre los jueces del Tribunal acerca de la presunta afectación cons- |
| 6877 | `no_clasificable` | titucional que la defensa alega, lo que hace improcedente que, pese a |
| 6878 | `no_clasificable` | la disidencia antes expuesta, me pronuncie aisladamente sobre el tema |
| 6879 | `no_clasificable` | de fondo. |
| 6880 | `no_clasificable` | Por ello, opino que esta Corte debe declarar admisible la queja, |
| 6881 | `no_clasificable` | declarar procedente el recurso extraordinario y expedirse sobre el punto |
| 6882 | `no_clasificable` | federal en cuestión. Notifíquese. |
| 6883 | `firma_arrastrada` | CARMEN M. ARGIBAY. |
| 6884 | `no_clasificable` | Recurso de hecho interpuesto por el Dr. Daniel Eduardo Pirrello, defensor público |
| 6885 | `no_clasificable` | oficial a cargo de la defensa de Justo Santiago Torres. |
| 6886 | `no_clasificable` | Tribunal de origen: Sala II de la Cámara Nacional de Casación Penal. |
| 6887 | `no_clasificable` | Tribunales que intervinieron con anterioridad: Sala A de la Cámara Federal de |
| 6888 | `no_clasificable` | Apelaciones de la Provincia de Mendoza; Juzgado Federal en lo Penal Nº 3 de |
| 6889 | `no_clasificable` | la Ciudad de Mendoza –provincia homónima–. |
| 6890 | `vacia` |  |
| 6891 | `header_pagina` | 1554 |
| 6892 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |


---

## 334_p229 — Organismo Regulador del Sistema Nacional de Aeropuertos | Delfino, Laura Virginia

**Localización**
- Archivo: `LibroVol334.1.md`
- Páginas catálogo: 229–236 | Página consultada: 236
- Líneas catálogo: 8930–9206 | Línea fin real: 9213 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 8930–8930 | 1 |
| 2 | catch_all | 8931–8942 | 12 |
| 3 | caratula | 8943–8943 | 1 |
| 4 | sumario [1] | 8944–8945 | 2 |
| 5 | sumario [2] | 8946–8956 | 11 |
| 6 | dictamen | 8957–9168 | 212 |
| 7 | header_pagina | 8963–8963 | 1 |
| 8 | header_pagina | 8964–8964 | 1 |
| 9 | header_pagina | 8965–8965 | 1 |
| 10 | header_pagina | 9002–9002 | 1 |
| 11 | header_pagina | 9003–9003 | 1 |
| 12 | header_pagina | 9004–9004 | 1 |
| 13 | header_pagina | 9044–9044 | 1 |
| 14 | header_pagina | 9045–9045 | 1 |
| 15 | header_pagina | 9046–9046 | 1 |
| 16 | header_pagina | 9085–9085 | 1 |
| 17 | header_pagina | 9086–9086 | 1 |
| 18 | header_pagina | 9087–9087 | 1 |
| 19 | header_pagina | 9126–9126 | 1 |
| 20 | header_pagina | 9127–9127 | 1 |
| 21 | header_pagina | 9128–9128 | 1 |
| 22 | header_pagina | 9166–9166 | 1 |
| 23 | header_pagina | 9167–9167 | 1 |
| 24 | header_pagina | 9168–9168 | 1 |
| 25 | cuerpo_mayoria | 9169–9201 | 33 |
| 26 | firma | 9202–9203 | 2 |
| 27 | catch_all | 9204–9204 | 1 |
| 28 | header_pagina | 9205–9205 | 1 |
| 29 | header_pagina | 9206–9206 | 1 |
| 30 | header_pagina | 9207–9207 | 1 |
| 31 | catch_all | 9208–9213 | 6 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=19 (6.69% del bloque, n=284)

---

### [span 1] header_pagina (8930–8930)
```
334
```

### [span 2] catch_all (8931–8942)
```
indicado, con costas (art. 68 del Código Procesal Civil y Comercial de 
Comercial de la Nación). Hágase saber, agréguese la queja al principal 
y, oportunamente, devuélvase a fin de que se dicte un nuevo pronun-
ciamiento con arreglo al presente.
Ricardo Luis Lorenzetti — Elena I. Highton de Nolasco — Carlos 
S. Fayt — Enrique Santiago Petracchi — Juan Carlos Maqueda — E. 
Raúl Zaffaroni.
Recurso de hecho deducido por Norma Isabel Calderón de Loiza, actora en autos, re-
presentada por el doctor Rubén Alberto Suárez, en calidad de patrocinante.
Tribunal de origen: Suprema Corte de Justicia de la Provincia de Buenos Ai-
res.
Tribunal que intervino con anterioridad: Tribunal del Trabajo Nº 2 de La Ma-
```

### [span 3] caratula (8943–8943)
```
tanza.
```

### [span 4] sumario [1] (8944–8945)
**Header**: LAURA VIRGINIA DELFINO c/ ORGANISMO REGULADOR
**Atribución**: (sin atribución detectada)
```
LAURA VIRGINIA DELFINO c/ ORGANISMO REGULADOR
del SISTEMA NACIONAL de AEROPUERTOS
```

### [span 5] sumario [2] (8946–8956)
**Header**: ESTABILIDAD DEL EMPLEADO PUBLICO.
**Atribución**: –Del precedente “Madorrán” (Fallos: 330:1989), al que remitió la Corte Supre-
```
ESTABILIDAD DEL EMPLEADO PUBLICO.
Corresponde confirmar la sentencia que declaró la inconstitucionalidad del art. 24 
del decreto 375/97 –que, al disponer que las relaciones entre el Organismo Regu-
lador del Sistema Nacional de Aeropuertos y su personal dependiente se regirán 
por la Ley de Contrato de Trabajo privó a la demandante de su la estabilidad del 
empleado público– y ordenó la reinstalación de la actora, ya que dicha estabilidad 
en sentido propio, excluye por principio, la cesantía sin causa justificada y debido 
proceso y su violación trae la nulidad de la medida y la consiguiente reincorpora-
ción, en tanto el derecho a la carrera integra el concepto de estabilidad.
–Del precedente “Madorrán” (Fallos: 330:1989), al que remitió la Corte Supre-
ma–.
```

### [span 6] dictamen (8957–9168)
```
Dictamen de la Procuración General
Suprema Corte:
– I –
Los jueces de la Cámara Nacional de Apelaciones del Trabajo, Sala 
VII, confirmaron la declaración de inconstitucionalidad del artículo 24

230
FALLOS DE LA CORTE SUPREMA
334
del Decreto 375/97, en cuanto dispone que el personal dependiente del 
Organismo Regulador de Aeropuertos (ORSNA) se rige por la Ley de 
Contrato de Trabajo y no es de aplicación el Régimen Jurídico Básico 
de la Función Pública, vulnerando, así, la estabilidad del empleado 
público reconocida por el art. 14 bis, de la Constitución Nacional. Or-
denaron que en un plazo máximo de cinco días, desde que quede firme 
el pronunciamiento, se reincorpore a la actora al empleo, bajo aperci-
bimiento de astreintes, con igual nivel salarial, más los aumentos que 
le hubieran correspondido en razón de su trayectoria y antigüedad e 
idéntica categoría a la desempeñada hasta su egreso (v. fs. 279/283; 
fs. 200/205; fs. 420).
Contra dicho pronunciamiento dedujeron el recurso extraordina-
rio federal la demandada, ORSNA, y la reclamante (v. fs. 305/361 y 
fs. 390/402, respectivamente), cuya denegación (v. fs. 427 y fs. 430/431) 
dio origen a los recursos de hecho: D. 1312, L. XLII y D. 1380, L. XLII, 
deducidos por las mencionadas en el mismo orden.
Si bien la vista a esta Procuración General se dio en la presentación 
directa mencionada en primer término, de su encabezado se desprende 
que se mencionan los expedientes D. 1312 y 1380 (v. fs. 80), por ello 
entiendo que corresponde dictaminar en ambas quejas.
– II –
A) RHE D. Nº 1312, L. XLII.
La demandada (ORSNA) plantea –en síntesis– que la sentencia de 
la Cámara es arbitraria al considerar abstracto el tratamiento de la 
injuria que dio motivo al despido y, directamente, abordar la inconsti-
tucionalidad del art. 24 del decreto 375/97 disponiendo la estabilidad 
absoluta de la trabajadora sin sustento legal. Entiende que al descar-
tarse la aplicación al caso del derecho común se desplazó la materia 
que sirve de base para la atribución de la competencia de la justicia 
laboral especializada en la materia (art. 20 de la ley 18.345).
Sostiene que arbitrariamente se dispone la reincorporación de la 
trabajadora sin tener en cuenta la cláusula constitucional que man-
da a proteger contra el despido arbitrario y que el legislador asegura 
mediante la previsión de una indemnización tarifada (art. 245 de la 
LCT). Señala que de esa manera el juzgador se erigió como un poder

231
DE JUSTICIA DE LA NACION
334
constituyente al atribuirle carácter absoluto a la estabilidad que prevé 
el art. 14 bis de la C.N. e infiere la necesidad de un sumario previo para 
disponer un despido por justa causa. Afirma que los jueces desprecian 
la disposición legal del Régimen Jurídico Básico de la Función Pública 
que faculta al Poder Ejecutivo Nacional a exceptuar de su régimen al 
personal que requiera un tratamiento particular por las especiales ca-
racterísticas de sus actividades (art. 2, inciso h de la ley 22.140). Luego, 
reprocha que ni siquiera se valora la razonabilidad del “acto expreso” 
que habilita la inclusión del empleo público en la Ley de Contrato de 
Trabajo (art. 2, inciso a de la ley 20.744). Afirma que desde el inicio de 
la relación laboral con el ORSNA, la trabajadora estuvo incluida en 
la Ley de Contrato de Trabajo y excluida del Régimen Jurídico Básico 
de la Función Pública, por lo tanto, nunca integró los cuadros de la 
Administración Pública Nacional debido a que no ingresó al ente au-
tárquico con arreglo a las disposiciones legales específicas que regulan 
el acceso al régimen de estabilidad.
Asevera que se viola el principio de legalidad, de supremacía cons-
titucional, de división de poderes y se incurre en gravedad institucional 
al generar “un peligroso precedente” para todo ente público, nacional o 
local, cuyas relaciones con sus dependientes se rijan por la Ley de Con-
trato de Trabajo, porque en definitiva el organismo demandado pierde 
el régimen sustantivo aplicable a los despidos de sus dependientes.
B) RHE D. Nº 1380, L. XLII.
La actora se agravia porque en ambas instancias, a pesar de co-
incidir en aceptar el reclamo y en que se la reincorpore al empleo, los 
jueces rechazaron el pedido de pago de los salarios caídos desde que fue 
despedida y hasta su efectiva reincorporación o, en subsidio, desde la 
interposición de la demanda. Afirma que es arbitrario el razonamiento 
por el cual se desestima la pretensión con fundamento en que gozó de 
una beca de estudios en el exterior, ya que se solicitó expresamente la 
deducción de ese período e inclusive, en subsidio, por todo el tiempo en 
que no inició la acción. Señala que no se tuvo en cuenta lo dispuesto 
por el art. 103 de la LCT en cuanto establece que el empleador debe 
al trabajador la remuneración aunque este no preste servicios, por la 
mera circunstancia de haber puesto su fuerza de trabajo a disposición 
de aquél. Explica que la beca de estudios bien pudo realizarse aun 
manteniendo el vínculo de trabajo, pues dicho programa de estudios 
no es una relación laboral y el derecho a los salarios caídos hasta la

232
FALLOS DE LA CORTE SUPREMA
334
reincorporación se encuentra implícito en este reconocimiento, tal como 
lo reconoce la jurisprudencia que cita.
También se agravia porque no se hizo lugar al reclamo de certifica-
ción de servicios, en atención que existió un período en que el vínculo 
se mantuvo mediante la figura fraudulenta de la locación de servicios, 
sin ingresar aportes a los organismos de la seguridad social. En vir-
tud de ello es que solicitó la indemnización prevista en el art. 45 de 
la ley 25.345 frente a la falta de entrega del certificado que exige el 
art. 80 de la LCT. Entiende que no inhibe tal pretensión el hecho que 
se haya ordenado la reincorporación dada la situación irregular por el 
período mencionado y del cual se requiere la subsanación ordenando a 
la demandada efectuar los aportes y contribuciones correspondientes y 
consignar la fecha real de ingreso bajo apercibimiento de lo dispuesto 
en el art. 80, último párrafo, de la LCT.
– III –
En primer lugar, procede señalar que el recurso extraordinario de-
ducido es admisible, toda vez que en autos se discute la interpretación 
y validez de normas federales y la decisión del superior tribunal de la 
causa fue contraria al derecho que el apelante fundó en ellas (art. 14, 
inc. 1º y 3º, de la ley 48). En lo que concierne a las causales de arbi-
trariedad invocadas por la recurrente relativas a la fundamentación 
de la declaración de inconstitucionalidad, estimo que se vinculan de 
modo inescindible con los temas federales en discusión y, por ello, deben 
ser examinados en forma conjunta (conf. doctrina de Fallos: 308:1076; 
322:3154; 323:1625, entre muchos otros).
En cuanto a la competencia de los jueces en el dictado del pronun-
ciamiento apelado, cabe señalar el doble aspecto de la sinrazón del 
recurrente –demandada–. Pues, por un lado, la radicación del trámite 
que ahora la quejosa cuestiona, no fue objeto de la excepción de in-
competencia, como bien lo señaló el Fiscal General ante la Cámara (v. 
fs. 275 vta., párrafo 3º) a pesar que los términos de la decisión apelada 
que motivó el planteo resultaba un evento previsible en el marco de los 
fundamentos de la demanda y su ampliación (v. fs. 22/24, fs. 27/28; fs. 71, 
punto 2.3.5 y ss). Por el otro, ya que según lo tiene decidido la Corte, 
todos los magistrados que integran la judicatura de la Capital de la 
República revisten el mismo carácter nacional (Fallos: 236:8; 246:285; 
321:2659). Desde esa perspectiva, el planteo de pérdida de competencia

233
DE JUSTICIA DE LA NACION
334
sobreviviente, cuando en la causa se haya dictado “actos típicamente 
jurisdiccionales”, no es posible en la medida que ello importa privar 
de validez a los actos procesales ya cumplidos, pues en el caso se ha 
decidido un conflicto mediante la adecuación de las normas aplicables, 
como resulta característico de la función jurisdiccional encomendada 
a los jueces (v. Fallos: 324:2334 y sus citas). En tales condiciones, las 
causas en las que ha recaído un acto jurisdiccional de ese tipo –ya sea 
que se encuentre firme o no, o que las dé por terminadas por alguna de 
las formas de extinción previstas en la ley– deben continuar su trámite 
hasta finiquitar ante el fuero que lo dictó.
En lo que respecta al fondo de la cuestión debatida, sin perjuicio de 
que la calificación de la injuria resultaría un tema ajeno a la instancia 
de excepción, se encuentra firme la sentencia en cuanto confirma la 
calificación de arbitrario al despido decidido por la demandada, pues 
no se ha puesto en tela de juicio en esta etapa, las circunstancias que 
motivaron la decisión de romper el vínculo en tal sentido. Cabe señalar 
sobre el particular que los agravios traídos a esta instancia se limitan 
a la declaración de inconstitucionalidad formulada por los jueces y a 
la reincorporación de la actora a su puesto de trabajo.
Centrada entonces la cuestión en la impugnación del art. 24 del 
decreto 375/97 en cuanto dispone que el personal dependiente del 
Organismo Regulador de Aeropuertos (ORSNA) se rige por la Ley de 
Contrato de Trabajo y no es de aplicación el Régimen Jurídico Básico 
de la Función Pública, entiendo que le asiste razón a la recurrente –de-
mandada– en cuanto reprocha al fallo la carencia de fundamento.
En efecto, el a quo afirma que en un organismo descentralizado y 
autárquico como es el ORSNA, debe prevalecer el pedido de la trabaja-
dora de hacer valer su estabilidad absoluta que recoge el art. 14 bis de 
la CN (v. fs. 281, punto V, párrafo 5º). Sin hacerse cargo adecuadamente 
de que la demandada había alegado que el decreto en cuestión fue dic-
tado con la vigencia de la ley 22.140, que facultaba al Poder Ejecutivo 
Nacional para exceptuar del citado régimen al personal que requiriera 
un tratamiento normativo particular, por las especiales características 
de sus actividades (v. art. 2º, inc. h).
En tal sentido, cobra relevancia, para el caso, que la Ley de Con-
trato de Trabajo en su art. 2º, inc. a, dispone que a los dependientes 
de la administración pública nacional, provincial o municipal, no les

234
FALLOS DE LA CORTE SUPREMA
334
será aplicable dicho cuerpo legal, excepto que por acto expreso se los 
incluya. Razón por la cual, no pudo el a quo decidir válidamente, sin 
extender la impugnación a estas otras normas legales que se mantie-
nen firmes ante la falta de cuestionamiento constitucional por parte 
de la actora (v. fs. 22/24 y fs. 27/28) y que los jueces tampoco advirtie-
ron, ni evaluaron su validez. Esta falencia también se manifiesta en 
el fallo de primera instancia (v. fs. 204), sin que supla tal insuficiencia 
la cita del precedente “Madorran”, en cuanto –como bien lo señaló el 
Procurador Fiscal ante la Cámara– “no guarda estricta analogía con 
el caso de autos, ya que están involucradas otras preceptivas legales” 
(v. fs. 276 vta.).
Cabe recordar en este aspecto la reiterada jurisprudencia de V.E. 
en cuanto ha establecido que es condición para la validez de los pro-
nunciamientos judiciales que ellos sean fundados y constituyan deriva-
ción razonada del derecho vigente con aplicación de las circunstancias 
comprobadas de la causa, y consideración de las alegaciones decisivas 
formuladas por las partes (Fallos: 323:2468, 324:556, 325:2817, entre 
otros). Asimismo, la declaración de inconstitucionalidad de una norma 
es un acto de suma gravedad institucional que debe ser considerado 
como ultima ratio del orden jurídico, por lo que procede en aquellos 
supuestos donde se advierta una clara, concreta y manifiesta afecta-
ción de las garantías consagradas en la Constitución Nacional (Fallos: 
327:831; 330:855, entre muchos otros).
En tales condiciones, entiendo que la decisión carece de fundamento 
jurídico válido, sin que ello implique anticipar opinión sobre el fondo 
del problema, por lo que, se deberá decidir en definitiva sobre las cues-
tiones en debate atendiendo a los aspectos señalados, lo cual me exime 
de emitir opinión sobre los demás temas traídos por la recurrente e 
inclusive los que introdujo la actora en la queja D. Nº 1380, L. XLII.
– IV –
Por lo expresado, estimo que corresponde hacer lugar a la queja, 
declarar procedente el recurso de la demandada, dejar sin efecto la 
sentencia impugnada y restituir las actuaciones al tribunal de origen 
para que, por quien competa, se dicte nuevo pronunciamiento con 
arreglo a lo expuesto. Buenos Aires, 15 de septiembre de 2008. Marta 
A. Beiró de Gonçalvez.

235
DE JUSTICIA DE LA NACION
334
```

### [span 7] header_pagina (8963–8963)
```
230
```

### [span 8] header_pagina (8964–8964)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] header_pagina (8965–8965)
```
334
```

### [span 10] header_pagina (9002–9002)
```
231
```

### [span 11] header_pagina (9003–9003)
```
DE JUSTICIA DE LA NACION
```

### [span 12] header_pagina (9004–9004)
```
334
```

### [span 13] header_pagina (9044–9044)
```
232
```

### [span 14] header_pagina (9045–9045)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 15] header_pagina (9046–9046)
```
334
```

### [span 16] header_pagina (9085–9085)
```
233
```

### [span 17] header_pagina (9086–9086)
```
DE JUSTICIA DE LA NACION
```

### [span 18] header_pagina (9087–9087)
```
334
```

### [span 19] header_pagina (9126–9126)
```
234
```

### [span 20] header_pagina (9127–9127)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 21] header_pagina (9128–9128)
```
334
```

### [span 22] header_pagina (9166–9166)
```
235
```

### [span 23] header_pagina (9167–9167)
```
DE JUSTICIA DE LA NACION
```

### [span 24] header_pagina (9168–9168)
```
334
```

### [span 25] cuerpo_mayoria (9169–9201)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 9 de marzo de 2011.
Vistos los autos: “Recurso de queja deducido por la demandada en 
la causa Delfino, Laura Virginia c/ Organismo Regulador del Sistema 
Nacional de Aeropuertos”, para decidir sobre su procedencia.
Considerando:
1º) Que la Sala VII de la Cámara Nacional de Apelaciones del Tra-
bajo declaró la inconstitucionalidad del art. 24 del decreto 375/97 en 
la medida en que, al disponer que “las relaciones entre el Organismo 
Regulador del Sistema Nacional de Aeropuertos y su personal depen-
diente, se regirán por la Ley de Contrato de Trabajo [...]”, privó a la 
demandante de la “estabilidad del empleado público” prevista en el 
art. 14 bis de la Constitución Nacional. En consecuencia, ordenó la 
reinstalación de la actora en dicho Organismo, el cual había despedi-
do a aquélla con arreglo al art. 242 de la Ley de Contrato de Trabajo 
(LCT). Contra ello, el vencido dedujo el recurso extraordinario, cuya 
denegación dio origen a la queja en examen.
2º) Que los agravios del demandado mediante los cuales, con arreglo 
al citado art. 24 y al art. 2, inc. a, de la LCT, se pretende la validez cons-
titucional del sometimiento de la reclamante al régimen de estabilidad 
impropia previsto en el cuerpo legal últimamente recordado, encuen-
tran respuesta en las consideraciones y conclusiones expresadas por 
este Tribunal en la causa “Madorrán, Marta Cristina c/ Administración 
Nacional de Aduanas” (Fallos: 330:1989 –2007), a las que corresponde 
remitir, en lo pertinente, en razón de brevedad.
3º) Que los restantes planteos del recurso extraordinario son 
inadmisibles (art. 280 del Código Procesal Civil y Comercial de la 
Nación).
Por ello, oída la señora Procuradora Fiscal, se hace lugar parcial-
mente a la queja y al recurso extraordinario, y se confirma la sentencia 
apelada con los alcances indicados, con costas (art. 68 del código citado). 
Devuélvase el depósito de fs. 73, hágase saber, acumúlese la queja al 
principal y, oportunamente, remítase.
```

### [span 26] firma (9202–9203)
```
Ricardo Luis Lorenzetti — Enrique Santiago Petracchi — Juan Carlos 
Maqueda — E. Raúl Zaffaroni.
```

### [span 27] catch_all (9204–9204)
```

```

### [span 28] header_pagina (9205–9205)
```
236
```

### [span 29] header_pagina (9206–9206)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 30] header_pagina (9207–9207)
```
334
```

### [span 31] catch_all (9208–9213)
```
Recurso de hecho interpuesto por el Organismo Regulador del Sistema Nacional 
de Aeropuertos, demandado en autos, representado por el doctor Jorge G. Mo-
ras Mom, en calidad de apoderado.
Tribunal de origen: Cámara Nacional de Apelaciones del Trabajo, Sala VII.
Tribunales que intervinieron con anterioridad: Juzgado Nacional de Primera Ins-
tancia del Trabajo Nº 33.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=9213 | linea_inicio_proximo_caso=9207 | delta=-7
**Alertas**: `solapado_con_proximo`


---

## 333_p721 — Sociedad Anónima Expreso Sudoeste | Buenos Aires, Provincia de

**Localización**
- Archivo: `LibroVol333.1.md`
- Páginas catálogo: 721–724 | Página consultada: 724
- Líneas catálogo: 27833–27938 | Línea fin real: 27954 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 27833–27833 | 1 |
| 2 | catch_all | 27834–27846 | 13 |
| 3 | caratula | 27847–27847 | 1 |
| 4 | sumario [1] | 27848–27849 | 2 |
| 5 | sumario [2] | 27850–27860 | 11 |
| 6 | sumario [3] | 27861–27874 | 14 |
| 7 | header_pagina | 27866–27866 | 1 |
| 8 | header_pagina | 27867–27867 | 1 |
| 9 | header_pagina | 27868–27868 | 1 |
| 10 | cuerpo_mayoria | 27875–27918 | 44 |
| 11 | header_pagina | 27902–27902 | 1 |
| 12 | header_pagina | 27903–27903 | 1 |
| 13 | header_pagina | 27904–27904 | 1 |
| 14 | firma | 27919–27921 | 3 |
| 15 | disidencia | 27922–27954 | 33 |
| 16 | header_pagina | 27937–27937 | 1 |
| 17 | header_pagina | 27938–27938 | 1 |
| 18 | header_pagina | 27939–27939 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=13 (10.66% del bloque, n=122)

---

### [span 1] header_pagina (27833–27833)
```
333
```

### [span 2] catch_all (27834–27846)
```
público provincial de carácter constitucional, extremo que evidencia 
que la exégesis de ese precepto y de las instituciones de derecho público 
local puede ser determinante en la causa. Ello, desde ya, sin perjuicio 
de que el Tribunal, en su momento y como ya quedó expuesto, pueda 
entender en los temas federales comprometidos por la vía extraordi-
naria (Fallos: 328:3555; 329:5814 y 331:1302).
Por ello, oída la señora Procuradora Fiscal, se resuelve: Declarar 
que esta causa no corresponde a la instancia originaria de esta Corte. 
Notifíquese y, oportunamente, archívese.
Juan Carlos Maqueda.
Parte actora: Federación Argentina de la Magistratura, representada por su pre-
sidente, Dr. Abel Fleming, con el patrocinio letrado de los Dres. Enrique Máximo 
Pita y Martín Ovejero Cornejo.
```

### [span 3] caratula (27847–27847)
```
Parte demandada: Provincia de Salta.
```

### [span 4] sumario [1] (27848–27849)
**Header**: SOCIEDAD ANONIMA EXPRESO SUDOESTE
**Atribución**: (sin atribución detectada)
```
SOCIEDAD ANONIMA EXPRESO SUDOESTE
c/ PROVINCIA de BUENOS AIRES
```

### [span 5] sumario [2] (27850–27860)
**Header**: RECURSO DE REVOCATORIA.
**Atribución**: (sin atribución detectada)
```
RECURSO DE REVOCATORIA.
Si bien en principio las sentencias de la Corte no son susceptibles de los recursos 
de reconsideración, revocatoria o nulidad, cabe hacer excepción a dicho principio 
cuando se trata de situaciones serias e inequívocas que demuestren con nitidez 
manifiesta el error que se pretende subsanar, lo que se configura cuando la deci-
sión prescindió de la doctrina establecida por el Tribunal en varios precedentes, 
según la cual cuando el régimen tarifario que corresponde al servicio común de 
transporte interjurisdiccional ha sido fijado unilateralmente por la autoridad 
nacional, sin considerar entre los elementos de costo el impuesto a los ingresos 
brutos provincial, su determinación conduce inexorablemente a que sea sopor-
tado por el contribuyente.
```

### [span 6] sumario [3] (27861–27874)
**Header**: RECURSO DE REVOCATORIA.
**Atribución**: (sin atribución detectada)
```
RECURSO DE REVOCATORIA.
Corresponde rechazar el recurso de reposición intentado contra un anterior pro-
nunciamiento de la Corte si el mismo se sustentó en un informe del expediente 
administrativo en el que se señaló que en el caso de las tarifas del servicio el cál-

722
FALLOS DE LA CORTE SUPREMA
333
culo de costos que brindaba soporte a la adopción de las escalas tarifarias tenían 
incorporado el impuesto a los ingresos brutos, afirmación que era determinante 
para la suerte del pleito pero que no fue suficientemente rebatida por la accio-
nante en la oportunidad procesal pertinente y tampoco aparece desvirtuada por 
las restantes constancias obrantes en la causa (Disidencia del Dr. Juan Carlos 
Maqueda).
```

### [span 7] header_pagina (27866–27866)
```
722
```

### [span 8] header_pagina (27867–27867)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 9] header_pagina (27868–27868)
```
333
```

### [span 10] cuerpo_mayoria (27875–27918)
```
FALLO DE LA CORTE SUPREMA
Año del Bicentenario
Buenos Aires, 19 de mayo de 2010.
Autos y Vistos; Considerando:
1º) Que a fs. 179/187 la parte actora solicitó revocatoria del fallo 
dictado a fs. 172/174 por el que el Tribunal rechazó la demanda, con 
sustento en la ponderación de un informe obrante a fs. 252 del expe-
diente administrativo 2306-400.241/98, en el que un funcionario de la 
Comisión Nacional de Regulación del Transporte consignó que el cálculo 
de costos que brinda soporte a la adopción de las escalas tarifarias, 
tiene incorporado el impuesto a los ingresos brutos.
2º) Que este Tribunal ha resuelto en reiteradas oportunidades que 
sus sentencias no son susceptibles de los recursos de reconsideración, 
revocatoria o nulidad, pero ese principio reconoce excepciones cuando 
se trata de situaciones serias e inequívocas que demuestren con ni-
tidez manifiesta el error que se pretende subsanar (Fallos: 315:1431; 
318:2329; 325:3380; 327:3208; 329:6030).
3º) Que este último supuesto se configura en el presente, pues en 
la decisión referida se ha prescindido de la doctrina establecida por 
el Tribunal en varios precedentes, según la cual cuando el régimen 
tarifario que corresponde al servicio común de transporte interjuris-
diccional ha sido fijado unilateralmente por la autoridad nacional, 
sin considerar entre los elementos de costo el impuesto a los ingresos 
brutos provincial, su determinación conduce inexorablemente a que 
sea soportado por el contribuyente (Fallos: 328:4198; 330:2049, entre 
otros). Tal criterio, que resulta de aplicación al sub lite, no se ve des-

723
DE JUSTICIA DE LA NACION
333
virtuado por la prueba aludida supra, que constituye una declaración 
carente de adecuado sustento técnico y que no resulta corroborada por 
otras probanzas de la causa, en especial por las normas que regulan 
las tarifas aplicadas por la actora, individualizadas por la Comisión 
Nacional de Regulación del Transporte y la respuesta que dio ese or-
ganismo ante el requerimiento informativo (fs. 109/110).
Por ello, demás circunstancias de la causa ponderadas en el fallo 
de fs. 172/174 y la doctrina del Tribunal que surge de los precedentes 
mencionados, se resuelve: Revocar el pronunciamiento de fs. 172/174 
y, en consecuencia, hacer lugar a la demanda seguida por Sociedad 
Anónima Expreso Sudoeste contra la Provincia de Buenos Aires y de-
clarar la improcedencia de la pretensión fiscal de la demandada, con 
costas (art. 68, primera parte, del Código Procesal Civil y Comercial 
de la Nación). Notifíquese.
```

### [span 11] header_pagina (27902–27902)
```
723
```

### [span 12] header_pagina (27903–27903)
```
DE JUSTICIA DE LA NACION
```

### [span 13] header_pagina (27904–27904)
```
333
```

### [span 14] firma (27919–27921)
```
Ricardo Luis Lorenzetti — Elena I. Highton de Nolasco — Carlos 
S. Fayt — Enrique Santiago Petracchi — Juan Carlos Maqueda (en 
disidencia) — Carmen M. Argibay.
```

### [span 15] disidencia (27922–27954)
**Header**: Disidencia del señor ministro
```
Disidencia del señor ministro
doctor don Juan Carlos Maqueda
Considerando:
1º) Que a fs.  179/187 la Sociedad Anónima Expreso Sudoeste 
interpone recurso de reposición contra la sentencia definitiva dicta-
da a fs. 172/174. Corrido traslado a la Provincia de Buenos Aires, a 
fs. 190/190 vta. se opone por las razones que aduce.
2º) Que como lo ha decidido el Tribunal en reiterados anteceden-
tes, las sentencias definitivas e interlocutorias no son susceptibles de 
ser modificadas por la vía intentada (artículos 238 y 160 del Código 
Procesal Civil y Comercial de la Nación; Fallos: 310:1377; 325:1603; 
326:4351; causa P.1524.XXXIX “Paz, Carlos Alberto y otros c/ Santiago 
del Estero, Provincia de s/ acción declarativa de certeza”, pronuncia-
miento del 27 de febrero de 2007, entre muchos otros), principio que

724
FALLOS DE LA CORTE SUPREMA
333
reconoce una excepción cuando se manifiestan con nitidez errores que 
son necesarios subsanar, circunstancia que no se da en autos.
3º) Que, sin perjuicio de ello, y a fin de dar una acabada respuesta 
a la pretensión de la recurrente, cabe señalar que el pronunciamiento 
de este Tribunal se sustentó en el informe obrante a fs. 252 del expe-
diente administrativo 2306–400.241/98, en el que se señaló que en el 
caso de las tarifas del servicio a cargo del actor “el cálculo de costos que 
brinda soporte a la adopción de las escalas tarifarias, tiene incorporado 
el impuesto a los ingresos brutos”. Esta afirmación, determinante para 
la suerte del pleito, no fue suficientemente rebatida por la accionante 
en la oportunidad procesal pertinente y tampoco aparece desvirtuada 
por las restantes constancias obrantes en la causa.
Por ello, se resuelve: Rechazar el recurso de reposición interpuesto 
por la actora a fs. 179/187.
Juan Carlos Maqueda.
```

### [span 16] header_pagina (27937–27937)
```
724
```

### [span 17] header_pagina (27938–27938)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 18] header_pagina (27939–27939)
```
333
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=27954 | linea_inicio_proximo_caso=27939 | delta=-16
**Alertas**: `solapado_con_proximo`


---

## 332_p2033 — Fiscal | Ferreyra, José; Almeida, Alberto y Díaz, Jorge.

**Localización**
- Archivo: `LibroVol332.3.md`
- Páginas catálogo: 2033–2043 | Página consultada: 2043
- Líneas catálogo: 245–444 | Línea fin real: 465 (status_fin=`fin_extendido_pag_compartida`, pista=`sumario_siguiente`)
- Status localización: `pagina_no_en_mapa`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | catch_all | 245–247 | 3 |
| 2 | header_pagina | 248–248 | 1 |
| 3 | header_pagina | 249–249 | 1 |
| 4 | header_pagina | 250–250 | 1 |
| 5 | catch_all | 251–281 | 31 |
| 6 | header_pagina | 282–282 | 1 |
| 7 | header_pagina | 283–283 | 1 |
| 8 | header_pagina | 284–284 | 1 |
| 9 | catch_all | 285–319 | 35 |
| 10 | header_pagina | 320–320 | 1 |
| 11 | header_pagina | 321–321 | 1 |
| 12 | header_pagina | 322–322 | 1 |
| 13 | catch_all | 323–361 | 39 |
| 14 | header_pagina | 362–362 | 1 |
| 15 | header_pagina | 363–363 | 1 |
| 16 | header_pagina | 364–364 | 1 |
| 17 | catch_all | 365–402 | 38 |
| 18 | header_pagina | 403–403 | 1 |
| 19 | header_pagina | 404–404 | 1 |
| 20 | header_pagina | 405–405 | 1 |
| 21 | catch_all | 406–442 | 37 |
| 22 | header_pagina | 443–443 | 1 |
| 23 | header_pagina | 444–444 | 1 |
| 24 | header_pagina | 445–445 | 1 |
| 25 | catch_all | 446–446 | 1 |
| 26 | caratula | 447–447 | 1 |
| 27 | cuerpo_mayoria | 448–459 | 12 |
| 28 | firma | 460–461 | 2 |
| 29 | catch_all | 462–465 | 4 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=188 (85.07% del bloque, n=221)

---

### [span 1] catch_all (245–247)
```
Además de ello, si bien no consta en autos que esa providencia haya 
sido modificada, la compulsa de las actuaciones muestra numerosas

```

### [span 2] header_pagina (248–248)
```
2038
```

### [span 3] header_pagina (249–249)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 4] header_pagina (250–250)
```
332
```

### [span 5] catch_all (251–281)
```
constancias que, por el contrario, permiten afirmar que las muertes 
de Chacón Araujo y Naranjo Nievas constituyen expreso objeto de in-
vestigación. Así se desprende de las siguientes:
1º) Acta inicial que describe el hecho íntegramente (fs. 1/3).
2º) Acta de constatación que, entre otros aspectos, hace referencia 
a la ubicación, posición, etc., del cadáver de Chacón Araujo (fs. 4/6).
3º) Croquis ilustrativo del lugar de los hechos, que “indica donde 
se encontraba el occiso” (fs. 7).
4º) Nota librada en el sumario por averiguación de homicidio, diri-
gida por la dependencia policial a la autoridad hospitalaria, donde se 
solicita la entrega del cadáver de Naranjo Nievas (fs. 10).
5º) Solicitudes de sendas necropsias al Instituto de Criminología y 
Medicina Legal (fs. 11 y 12).
6º) Pedido de la autoridad de prevención a la Policía Científica, 
librado en el sumario por averiguación evasión seguida de muerte 
Nº 3168/04 (fs. 15).
7º) Informe del Subjefe de la División Sanidad al Director del esta-
blecimiento penitenciario, donde se alude al deceso de Chacón Araujo 
y a la derivación de Naranjo Nievas al hospital (fs. 43).
8º) Resumen del sumario de prevención policial Nº 3168/04 elevado 
al juez de la causa, donde si bien se indica como carátula “av. evasión y 
lesiones a la autoridad”, en la descripción de los hechos incluye ambas 
muertes (fs. 56).
9º) Informe del hecho elevado por el Director de la Penitenciaría 
Provincial al magistrado interviniente, donde también se hace mención 
a los fallecimientos (fs. 58).
10) Informe del Jefe de Turno al Jefe de División Seguridad In-
terna de esa penitenciaría, que al referirse a los occisos señala que al 
intentar darse a la fuga, “mediante un enfrentamiento armado ambos 
fueron abatidos por personal de seguridad” (fs. 66).

```

### [span 6] header_pagina (282–282)
```
2039
```

### [span 7] header_pagina (283–283)
```
DE JUSTICIA DE LA NACION
```

### [span 8] header_pagina (284–284)
```
332
```

### [span 9] catch_all (285–319)
```
11) Sendas comunicaciones de la autoridad penitenciaria al Juz-
gado de Ejecución Nº 1, informando las muertes de Naranjo Nievas y 
Chacón Araujo (fs. 69/70).
12) “Poder Apud Acta” por el cual Alejandra Herrera Nievas com-
parece ante el juzgado de instrucción interviniente, a fin de otorgar 
poder a un letrado para que en su nombre y representación “inicie y/o 
prosiga hasta su terminación las acciones legales que correspondieran 
al querellante particular y actor civil en los autos Nº P 46454/04, ca-
ratulados ‘F. c/ NN. o personal penitenciario p/ av. muerte de Naranjo 
Nievas, Federico’...”. Dicha diligencia fue realizada con intervención 
del secretario del tribunal (fs. 73).
13) Informe químico producido en el sumario policial Nº 3168/04 
por “av. evasión seguida de muerte” (fs. 115/6).
14) Informes de autopsias de Chacón Araujo y Naranjo Nievas 
(fs. 118 y 120/1).
15) Declaración testimonial del agente penitenciario Luis A. Dri 
Amo, donde, entre otros aspectos, el tribunal le preguntó “si vio que 
el disparo que se produjo de su arma cuando forcejeaba con Ferrando 
impactara en Naranjo” (fs. 132/3).
16) Declaración testimonial del agente penitenciario Oscar I. Gor-
dillo, a quien se le preguntó “si... vio quién disparó sobre Chacón y 
Naranjo” (fs. 135).
17) Declaración testimonial del agente penitenciario Sergio R. Juá-
rez Montaña, que fue interrogado para que diga “si el interno Naranjo 
Nievas se encontraba herido al momento en que manifiesta quedarse 
con él hasta que llegó grupo especial de seguridad”, “si... puede aclarar 
lo visto con relación al interno Chacón”, “si... vio alguna persona que 
efectuara disparos en dirección de Chacón” y “si... puede afirmar con 
seguridad la posición que refiere de los internos Chacón, Naranjo y 
Ferrando...” (fs. 137/8).
18) Pericia balística realizada por la Policía Científica de la pro-
vincia en el sumario de prevención Nº 3168/04 en “av. evasión segui-
da de muerte”, que comprende el proyectil recuperado del cuerpo de 
Federico Naranjo Nievas (fs. 144/9). Cabe destacar que este informe

```

### [span 10] header_pagina (320–320)
```
2040
```

### [span 11] header_pagina (321–321)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 12] header_pagina (322–322)
```
332
```

### [span 13] catch_all (323–361)
```
técnico también incluyó el armamento del personal penitenciario (ver 
fs. 27 y 270/1).
19) Presentación del letrado apoderado de Alejandra Herrera 
Nievas, “hermana de la víctima” Federico Naranjo Nievas, solicitando 
fotocopias de las actuaciones (fs. 207).
20) Oficio mediante el cual el Director Presidente de la Inspec-
ción General de Seguridad del Ministerio de Justicia y Seguridad de 
la Provincia de Mendoza, solicita al juez interviniente que se sirva 
informar si como consecuencia de la remisión del sumario de preven-
ción Nº 3168/04 (Nº 46454/04 del tribunal) “en el que se investiga la 
tentativa de evasión y fallecimiento de internos del Penal... ha sido 
imputado algún personal penitenciario...” (fs. 222).
21) Declaración testimonial del 5 de mayo de 2005 del interno Cris-
tian G. Naranjo Nievas, durante la cual ratificó –en parte– la prestada 
en sede administrativa obrante a fojas 223. Al ser preguntado en el 
tribunal “por las generales de la ley con respecto a las partes que en 
este acto se le mencionan, responde: que es hermano del interno Na-
ranjo Nievas Federico Daniel, que resultara muerto en el hecho que 
se investiga. Era asimismo amigo de Chacón, quien también resultó 
muerto...”. También fue interrogado para que diga “si puede relatar 
como dice en su declaración cuando dice vio mataron a su hermano”. 
Tanto en la respuesta a esa pregunta como en la aludida declaración 
anterior, hizo referencia a ambas muertes (se deja constancia que la 
foliatura de la audiencia en sede judicial es ilegible).
22) Declaración testimonial de Cristian R. Manrique Bugueño, 
también del 5 de mayo de 2005, durante la cual ratificó parcialmente 
la similar de fojas 225 que se le recibió en sede administrativa. Al ser 
“preguntado por las generales de la ley con respecto a las partes que 
en este acto se le mencionan, responde: era compañero de celda de las 
personas intervinientes en la fuga, en aquel momento se trataba de 
la celda 8 del pabellón 11, siendo los intervinientes Chacón, Ferreyra, 
Ferrando, Díaz Rodríguez y Almeyda; también intervino Naranjo, del 
pabellón 12 pero no sé de cuál celda”. Tras contestar positivamente 
sobre si luego de los hechos tuvo trato con los internos intervinientes 
en la fuga, al ser preguntado para que diga “si le contaron algo con 
relación a este hecho, responde: que se había armado una balacera 
infernal y que a Chacón y a Naranjo los habían matado mal, porque 
no había necesidad porque no llevaban armas. Que los habían matado

```

### [span 14] header_pagina (362–362)
```
2041
```

### [span 15] header_pagina (363–363)
```
DE JUSTICIA DE LA NACION
```

### [span 16] header_pagina (364–364)
```
332
```

### [span 17] catch_all (365–402)
```
los penitenciarios, no sé sus nombres o apellidos...” (la foliatura de esta 
pieza procesal también es ilegible).
– IV –
La elocuencia de la enumeración efectuada, desvirtúa per se el 
fundamento invocado tanto por el a quo como por las instancias an-
teriores de la justicia de la Provincia de Mendoza y permite, sin más, 
descalificar lo resuelto con sustento en la doctrina de la arbitrariedad, 
pues es claro que en la resolución impugnada no sólo se han dejado de 
lado aquellos elementos relevantes de la causa, sino también se inter-
pretó con excesivo rigor formal el decreto de fojas 75 (Fallos: 319:366; 
320:1519 y 2219; 321:1019; 323:1455 y 2461, entre muchos otros).
Así lo considero porque además de aquellas actas, informes, peri-
cias y testimonios agregados al expediente, las preguntas específicas 
formuladas por el tribunal en esas audiencias no dejan duda en cuanto 
a que la muerte de ambos internos también constituye su objeto proce-
sal. De otro modo no se explica que, no figurando como imputados en 
el “decreto de avoque”, se los haya incluido como “partes” al interrogar 
a los testigos por las “generales de la ley”, tal como surge expresamen-
te de lo respondido al respecto en las declaraciones reseñadas en los 
Nº 21 y 22 del apartado anterior. Es útil mencionar en este sentido, 
que el artículo 240 del Código Procesal Penal de Mendoza contempla 
que el testigo deberá ser requerido sobre el “vínculo de parentesco y 
de interés por las partes, y cualquier otra circunstancia que sirva para 
apreciar su veracidad” (énfasis agregado).
Esta conclusión se refuerza si se tiene en cuenta que –con criterio 
diverso al aquí recurrido– no consta que el tribunal se haya expedido 
respecto de las constancias de fojas 73 y 207 (detalladas en los Nº 12 
y 19 del apartado anterior), por las cuales Alejandra Herrera Nievas 
pretendería querellar por el homicidio de su hermano, ni tampoco que 
hayan sido rechazadas o devueltas a la interesada o su letrado.
En consecuencia, habida cuenta que en la propia instancia local 
se ha interpretado que, de investigarse en autos aquellas muertes, no 
existiría impedimento para reconocer –de conformidad con el artículo 
10 del Código Procesal Penal provincial– la calidad de parte al fun-
cionario nacional y que, como se ha visto, el temperamento adverso 
ha desconocido aquellas constancias de la causa que acreditan ese 
supuesto, sólo resta proponer a V.E. que en aplicación de la doctrina

```

### [span 18] header_pagina (403–403)
```
2042
```

### [span 19] header_pagina (404–404)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 20] header_pagina (405–405)
```
332
```

### [span 21] catch_all (406–442)
```
de la arbitrariedad deje sin efecto la sentencia para que se dicte una 
nueva con arreglo a derecho.
– V –
Por último y sin perjuicio de lo hasta aquí desarrollado, correspon-
de mencionar que la solicitud del Secretario de Derechos Humanos 
de la Nación para asumir en autos el rol de querellante particular se 
relaciona –tal como lo ha invocado– con las cuestiones tratadas por la 
Corte Interamericana de Derechos Humanos en sus resoluciones del 
22 de noviembre de 2004, del 18 de junio de 2005, del 30 de marzo de 
2006 y del 27 de noviembre de 2007 (ésta última ratificatoria de la de 
su presidente del 22 de agosto anterior), dictadas en el caso presentado 
contra la República Argentina caratulado “Asunto de las Penitenciarías 
de Mendoza”; y con las sentencias de V.E. publicadas Fallos: 329:3863; 
330:111 y 1135, dictadas en la acción declarativa de certeza planteada 
contra el Estado Nacional y la Provincia de Mendoza en razón de lo 
resuelto en la instancia supranacional.
Habida cuenta que las muertes de Javier Chacón Araujo y de Fede-
rico Naranjo Nievas se encuentran, efectivamente, entre los hechos que 
fueron presentados ante el tribunal internacional (ver párrafo 2.c.i.d. de 
la resolución del 22 de noviembre de 2004, obrante en copia a fs. 170/88 
–en especial fs. 171– de los autos principales) y en cuya virtud se han 
adoptado en ese ámbito diversas medidas provisionales, más allá de 
que sea el Estado Nacional –a través del Poder Ejecutivo– el obligado 
frente a esos pronunciamientos de la Corte Interamericana de Dere-
chos Humanos (Fallos: 330:1135, considerandos 13 al 18), toda vez que 
por imperio de los artículos 31 de la Constitución Nacional y 28 de la 
Convención Americana sobre Derechos Humanos los Estados provin-
ciales también deben cumplir con esta última (conf. Fallos: 330:2836 
y citas del punto IV del dictamen de esta Procuración General al que 
hizo remisión la sentencia), entiendo que el criterio anticipado no sólo 
permite la mejor consecución de esa finalidad sino también resulta 
respetuoso del régimen federal y la jurisdicción local (arts. 1º, 5º, 75 
inc. 12, y 121 y siguientes de la Constitución Nacional).
– VI –
Por ello, opino que V.E. debe hacer lugar a la queja de fojas 75/80, 
declarar procedente el recurso extraordinario y dejar sin efecto la

```

### [span 22] header_pagina (443–443)
```
2043
```

### [span 23] header_pagina (444–444)
```
DE JUSTICIA DE LA NACION
```

### [span 24] header_pagina (445–445)
```
332
```

### [span 25] catch_all (446–446)
```
sentencia apelada. Buenos Aires, 16 de septiembre de 2008. Eduardo 
```

### [span 26] caratula (447–447)
```
Ezequiel Casal.
```

### [span 27] cuerpo_mayoria (448–459)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 1º de septiembre de 2009.
Vistos los autos: “Recurso de hecho deducido por Eduardo Luis 
Duhalde (Secretario de Derechos Humanos) en la causa Fiscal c/ Fe-
rreyra, José; Almeida, Alberto y Díaz, Jorge”, para decidir sobre su 
procedencia.
Considerando:
Que esta Corte comparte el dictamen del señor Procurador Fiscal a 
cuyos argumentos y conclusiones cabe remitir en razón de brevedad.
Por ello, se declara admisible la queja, procedente el recurso ex-
traordinario y se deja sin efecto la sentencia apelada. Notifíquese. 
Agréguese la queja al principal y, oportunamente, remítase.
```

### [span 28] firma (460–461)
```
Ricardo Luis Lorenzetti — Elena I. Highton de Nolasco — Carlos 
S. Fayt — Enrique Santiago Petracchi — Juan Carlos Maqueda — E. 
```

### [span 29] catch_all (462–465)
```
Raúl Zaffaroni.
Recurso de hecho interpuesto por Eduardo Luis Duhalde en su carácter de Se-
cretario de Derechos Humanos, con el patrocinio del Dr. Ciro V. Annicchirico.
Tribunal de origen: Suprema Corte de Justicia de la Provincia de Mendoza.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=465 | linea_inicio_proximo_caso=445 | delta=-21
**Alertas**: `solapado_con_proximo`


---

## 330_p2902 — Grillo, Vicente c/ Sparano, Claudio Rafael | Sparano, Claudio Rafael (Grillo, Vicente c/)

**Localización**
- Archivo: `LibroVol330.3.md`
- Páginas catálogo: 2902–2915 | Página consultada: 2915
- Líneas catálogo: 1028–1544 | Línea fin real: 1550 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 1028–1028 | 1 |
| 2 | caratula | 1029–1029 | 1 |
| 3 | sumario [1] | 1030–1036 | 7 |
| 4 | sumario [2] | 1037–1040 | 4 |
| 5 | sumario [3] | 1041–1049 | 9 |
| 6 | sumario [4] | 1050–1053 | 4 |
| 7 | sumario [5] | 1054–1063 | 10 |
| 8 | header_pagina | 1061–1061 | 1 |
| 9 | header_pagina | 1062–1062 | 1 |
| 10 | header_pagina | 1063–1063 | 1 |
| 11 | sumario [6] | 1064–1070 | 7 |
| 12 | sumario [7] | 1071–1081 | 11 |
| 13 | sumario [8] | 1082–1090 | 9 |
| 14 | dictamen | 1091–1123 | 33 |
| 15 | header_pagina | 1099–1099 | 1 |
| 16 | header_pagina | 1100–1100 | 1 |
| 17 | header_pagina | 1101–1101 | 1 |
| 18 | cuerpo_mayoria | 1124–1407 | 284 |
| 19 | header_pagina | 1135–1135 | 1 |
| 20 | header_pagina | 1136–1136 | 1 |
| 21 | header_pagina | 1137–1137 | 1 |
| 22 | header_pagina | 1177–1177 | 1 |
| 23 | header_pagina | 1178–1178 | 1 |
| 24 | header_pagina | 1179–1179 | 1 |
| 25 | header_pagina | 1220–1220 | 1 |
| 26 | header_pagina | 1221–1221 | 1 |
| 27 | header_pagina | 1222–1222 | 1 |
| 28 | header_pagina | 1261–1261 | 1 |
| 29 | header_pagina | 1262–1262 | 1 |
| 30 | header_pagina | 1263–1263 | 1 |
| 31 | header_pagina | 1303–1303 | 1 |
| 32 | header_pagina | 1304–1304 | 1 |
| 33 | header_pagina | 1305–1305 | 1 |
| 34 | header_pagina | 1346–1346 | 1 |
| 35 | header_pagina | 1347–1347 | 1 |
| 36 | header_pagina | 1348–1348 | 1 |
| 37 | header_pagina | 1387–1387 | 1 |
| 38 | header_pagina | 1388–1388 | 1 |
| 39 | header_pagina | 1389–1389 | 1 |
| 40 | firma | 1408–1409 | 2 |
| 41 | catch_all | 1410–1410 | 1 |
| 42 | disidencia | 1411–1550 | 140 |
| 43 | header_pagina | 1424–1424 | 1 |
| 44 | header_pagina | 1425–1425 | 1 |
| 45 | header_pagina | 1426–1426 | 1 |
| 46 | header_pagina | 1463–1463 | 1 |
| 47 | header_pagina | 1464–1464 | 1 |
| 48 | header_pagina | 1465–1465 | 1 |
| 49 | header_pagina | 1504–1504 | 1 |
| 50 | header_pagina | 1505–1505 | 1 |
| 51 | header_pagina | 1506–1506 | 1 |
| 52 | header_pagina | 1543–1543 | 1 |
| 53 | header_pagina | 1544–1544 | 1 |
| 54 | header_pagina | 1545–1545 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=1 (0.19% del bloque, n=523)

---

### [span 1] header_pagina (1028–1028)
```
330
```

### [span 2] caratula (1029–1029)
```
VICENTE GRILLO V. CLAUDIO RAFAEL SPARANO
```

### [span 3] sumario [1] (1030–1036)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestión federal. Cuestiones fede-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestión federal. Cuestiones fede-
rales simples. Interpretación de las leyes federales. Leyes federales en general.
Es formalmente admisible el recurso extraordinario si se ha objetado la validez e
inteligencia de normas federales –leyes 25.798, 25.908 y 26.167 y decreto regla-
mentario 1284/2003– y la sentencia definitiva del superior tribunal de la causa
ha sido contraria al derecho que el apelante fundó en ellas (art. 14, inc. 3, de la
ley 48).
```

### [span 4] sumario [2] (1037–1040)
**Header**: CONSTITUCION NACIONAL: Derechos y garantías. Derecho de propiedad.
**Atribución**: (sin atribución detectada)
```
CONSTITUCION NACIONAL: Derechos y garantías. Derecho de propiedad.
Los derechos reconocidos en una sentencia pasada en autoridad de cosa juzgada
han quedado incorporados al patrimonio y se encuentran protegidos por el art. 17
de la Constitución Nacional.
```

### [span 5] sumario [3] (1041–1049)
**Header**: EMERGENCIA ECONOMICA.
**Atribución**: (sin atribución detectada)
```
EMERGENCIA ECONOMICA.
Aun cuando las normas sobre refinanciación hipotecaria han sido dictadas con el
fin de dar una solución definitiva, justa y equitativa a los conflictos suscitados
por la crisis económica respecto de los deudores hipotecarios que tuviesen com-
prometida su vivienda única y familiar, ello no constituye un argumento eficaz
para desconocer la estabilidad de las decisiones jurisdiccionales que, por consti-
tuir un presupuesto ineludible de la seguridad jurídica, es uno de los presupues-
tos del ordenamiento social cuya ausencia o debilitamiento pondría en crisis a la
íntegra juridicidad del sistema.
```

### [span 6] sumario [4] (1050–1053)
**Header**: EMERGENCIA ECONOMICA.
**Atribución**: (sin atribución detectada)
```
EMERGENCIA ECONOMICA.
El carácter de orden público de las leyes de emergencia no alcanza para modifi-
car los efectos de la cosa juzgada que también reviste dicho carácter y goza de
plena protección constitucional.
```

### [span 7] sumario [5] (1054–1063)
**Header**: EMERGENCIA ECONOMICA.
**Atribución**: (sin atribución detectada)
```
EMERGENCIA ECONOMICA.
La alteración de los derechos adquiridos que las leyes pueden llegar a disponer
circunstancialmente para asegurar el bien común comprometido en la emergen-
cia por desequilibrios económicos o sociales u otros motivos de análogo carácter
extraordinario, no pueden alcanzar la inmutabilidad de la cosa juzgada, porque
no hay bienestar posible fuera del orden.

2903
DE JUSTICIA DE LA NACION
330
```

### [span 8] header_pagina (1061–1061)
```
2903
```

### [span 9] header_pagina (1062–1062)
```
DE JUSTICIA DE LA NACION
```

### [span 10] header_pagina (1063–1063)
```
330
```

### [span 11] sumario [6] (1064–1070)
**Header**: REFINANCIACION HIPOTECARIA.
**Atribución**: (sin atribución detectada)
```
REFINANCIACION HIPOTECARIA.
El art. 7 de la ley 26.167 prevé la hipótesis de que el pago, a pedido del deudor,
sea realizado, en forma parcial o total, con aportes del Fondo Fiduciario previsto
en la ley 25.798. Ello pone en evidencia que el legislador consideró también la
posibilidad de que, en ciertas hipótesis, el deudor pudiera cancelar una parte del
crédito del ejecutante con fondos propios y pagar la parte restante mediante la
utilización del fondo fiduciario.
```

### [span 12] sumario [7] (1071–1081)
**Header**: EMERGENCIA ECONOMICA.
**Atribución**: (sin atribución detectada)
```
EMERGENCIA ECONOMICA.
Corresponde revocar la sentencia que declaró inaplicable el régimen de
refinanciación hipotecaria y, a pesar de que las partes no se manifestaron en ese
sentido, fijar un plazo para que el deudor manifieste si optará por cancelar el
crédito en la forma prevista en el art. 7 de la ley 26.167, pues el sistema legal
admite que el deudor lo haga y pague con fondos propios la parte de la deuda que
no resulta cubierta por el sistema de refinanciación hipotecaria, sin que ello im-
plique vulnerar derechos del acreedor alcanzados por la protección de la Ley
Fundamental, lo que permite compatibilizar la validez constitucional de las nor-
mas cuya aplicación se pretende, con el principio de la cosa juzgada que también
cuenta con protección constitucional.
```

### [span 13] sumario [8] (1082–1090)
**Header**: EMERGENCIA ECONOMICA.
**Atribución**: (sin atribución detectada)
```
EMERGENCIA ECONOMICA.
La aplicación del régimen de refinanciación hipotecaria con posterioridad al dic-
tado de la sentencia que declaró la inconstitucionalidad de las normas de emer-
gencia, implicaría reeditar el debate sobre temas que ya han sido objeto de trata-
miento y resolución en etapas del proceso que el ejecutado ha dejado precluir y,
además, hacer caso omiso a los derechos reconocidos al actor en el pronuncia-
miento firme, que han quedado así incorporados a su patrimonio y se encuentran
protegidos por el art. 17 de la Constitución Nacional (Disidencia de la Dra. Car-
men M. Argibay).
```

### [span 14] dictamen (1091–1123)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
Toda vez que las cuestiones materia de recurso en los presentes
actuados, guardan sustancial analogía con las examinadas en la cau-
sa: S.C. H. 82, L. XLI, caratulada “Hodari, Estela c/ Villa, Antonio s/
Ejecución Hipotecaria”, dictaminada por esta Procuración General el
día 29 de noviembre de 2005, corresponde remitir, en lo pertinente, a

2904
FALLOS DE LA CORTE SUPREMA
330
los términos y consideraciones allí vertidos, por razones de brevedad.
Ello es así, en virtud de que aquí también, el a quo, de un lado, omitió
considerar que, conforme al artículo 16, inciso “d”, de la ley 25.798
(texto según ley 25.908), la existencia de sentencia firme de remate,
no resulta impedimento para que el deudor (o el acreedor), puedan
optar por ingresar al Sistema de Refinanciación Hipotecaria; y de otro,
tampoco se pronunció acerca de la constitucionalidad de dicho siste-
ma, a pesar de que la cuestión viene debatida en autos.
Debo señalar, asimismo, que esta Procuración General se ha pro-
nunciado sobre el fondo de la cuestión en la causa: S.C. G. Nº 1360, L.
XLI, caratulada “Guijun S.A. y otros c/ Wrubel Marta Angela y otros s/
Ejecución hipotecaria”, dictamen, del día 13 de junio de 2006. A todo
evento, también remito, en lo pertinente, a los argumentos allí verti-
dos, en especial en el ítem IV, por razones de brevedad.
Por lo expuesto, opino que corresponde hacer lugar a la queja, de-
clarar procedente el recurso extraordinario y disponer que vuelvan los
actuados al tribunal de origen para que, por quien corresponda, se
dicte nuevo pronunciamiento con arreglo a lo expresado en el primero
de los dictámenes referidos; o bien, si V.E. lo estima pertinente por
razones de economía procesal, atento a la opinión vertida en el segun-
do de dichos dictámenes, revoque la sentencia en lo que ha sido mate-
ria de apelación. Buenos Aires, 14 de agosto de 2006. Esteban Righi.
```

### [span 15] header_pagina (1099–1099)
```
2904
```

### [span 16] header_pagina (1100–1100)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 17] header_pagina (1101–1101)
```
330
```

### [span 18] cuerpo_mayoria (1124–1407)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 3 de julio de 2007.
Vistos los autos: “Recurso de hecho deducido por la demandada en
la causa Grillo, Vicente c/ Sparano, Claudio Rafael”, para decidir so-
bre su procedencia.
Considerando:
1º) Que el ejecutado, que adquirió un inmueble el 3 de abril de
1998, se obligó a pagar el saldo del precio –U$S 60.000– en 166 cuotas
mensuales, iguales y consecutivas de U$S 1.500, que incluían el inte-
rés pactado, con vencimiento la primera el 7 de enero de 1999, y gravó

2905
DE JUSTICIA DE LA NACION
330
el bien a favor de sus acreedores con derecho real de hipoteca. En
razón de que el deudor incurrió en mora en el mes de abril de 2001,
uno de los coacreedores inició la presente ejecución hipotecaria por el
cobro del capital adeudado, con más sus intereses y costas.
2º) Que el juez de primera instancia declaró la inconstitucionalidad
del decreto 214/2002 y de las normas ampliatorias y complementa-
rias, y mandó llevar adelante la ejecución hasta hacerse al acreedor
íntegro pago del capital adeudado, transformado por aplicación del
principio del esfuerzo compartido a razón de un dólar igual a un peso,
más el 50% del valor de la divisa que, según cotización del tipo vende-
dor en el mercado libre de cambios a la fecha del efectivo pago, exce-
diese de la paridad indicada (fs. 48/56 del expediente principal).
3º) Que dicha sentencia fue notificada y no fue objeto de recurso de
apelación por el ejecutado. Con posterioridad éste último denunció que
había hecho uso de la opción prevista por el art. 6 de la ley 25.798 para
ingresar en el sistema de refinanciación hipotecaria, trámite que cul-
minó con la declaración de elegible del mutuo y la firma del correspon-
diente contrato con el Banco de la Nación Argentina (ver fs. 63/64, 121
y 137/145 de las actuaciones principales).
Por su lado, el ejecutante sostuvo que las leyes 25.798 y 25.908
resultaban inaplicables al caso pues se encontraba firme la sentencia
que había resuelto acerca de la inconstitucionalidad de las normas de
emergencia económica, motivo por el cual su parte había adquirido
irrevocablemente los derechos que emanaban de ella y que en caso
contrario, añadió, se vulneraría el principio de la cosa juzgada que es
el sostén del sistema legal; y en forma subsidiaria planteó la incons-
titucionalidad del mencionado régimen de refinanciación hipotecaria.
4º) Que la Sala L de la Cámara Nacional de Apelaciones en lo Civil
confirmó la sentencia de primera instancia que había declarado ina-
plicables al caso las leyes 25.798 y 25.908. Después de efectuar consi-
deraciones respecto de los principios de preclusión y de eventualidad
procesal, señaló que al haber pasado en autoridad de cosa juzgada el
pronunciamiento que mandaba llevar adelante la ejecución por el ca-
pital reclamado, calculado según el principio del esfuerzo compartido,
no se podía pretender habilitar nuevamente el debate de lo actuado
hasta ese momento, so pena de vulnerar los principios de cosa juzgada
y de preclusión. Añadió que el art. 3 de la ley 25.820 –que modificó el
art. 11 de la ley 25.561– era claro al prescribir que la norma no modi-

2906
FALLOS DE LA CORTE SUPREMA
330
ficaba las situaciones ya resueltas mediante acuerdos privados o sen-
tencias judiciales.
5º) Que contra dicho fallo el ejecutado interpuso el recurso extraor-
dinario que, denegado, dio origen a esta presentación directa. Afirma
que se ha incurrido en un error en la consideración legal del caso, pues
se han desconocido normas de orden público que contemplan los al-
cances y efectos de la cosa juzgada para este tipo de causas (art. 16,
incs. c y d, de la ley 25.798, texto según ley 25.908); que la decisión
vulnera el derecho de igualdad ante la ley porque establece un privile-
gio a favor del actor y le otorga la posibilidad de cobrar su crédito
evadiendo la aplicación del régimen legal que arbitró los medios para
soportar los estragos de la crisis, aparte de que resulta injusta porque
le niega la solución dada por el legislador a quien adquirió su vivienda
única destinada al uso familiar con el fruto de su trabajo y lo somete a
la pérdida del bien.
6º) Que el señor Procurador General consideró que las cuestiones
planteadas guardaban sustancial analogía con las examinadas en su
dictamen del 29 de noviembre de 2005 en la causa H.82.XLI “Hodari,
Estela c/ Villa, Antonio s/ ejecución hipotecaria”, en la cual estimó que
correspondía devolver el expediente a la instancia de grado para que
se dictase un nuevo pronunciamiento, pues la sentencia impugnada
era arbitraria por apartarse de las normas aplicables (art. 16, inc. d,
de la ley 25.798, texto según ley 25.908) y no haberse pronunciado
acerca de la constitucionalidad del sistema de refinanciación hipote-
caria debatida por las partes. Como alternativa sugirió que si por ra-
zones de economía procesal el Tribunal lo consideraba pertinente, co-
rrespondía revocar el fallo de cámara según lo dictaminado respecto
del fondo del asunto en la causa G.1360.XLI “Guijun S.A. y otros c/
Wrubel, Marta Angela y otros s/ ejecución hipotecaria” con fecha 13 de
junio de 2006.
7º) Que por haberse dictado durante el trámite del juicio nuevas
normas en materia de refinanciación hipotecaria, esta Corte dispuso
oír a las partes al respecto (conf. fs. 71 del recurso de queja), criterio
acorde con la doctrina que impone atender a las modificaciones intro-
ducidas por esos preceptos en tanto configuran circunstancias
sobrevinientes de las que no es posible prescindir (Fallos: 308:1489;
312:555; 315:123; 325:28; 327:4495 –“Bustos”– y causa R.320.XLII
“Rinaldi, Francisco Augusto y otro c/ Guzmán Toledo, Ronal Constan-
te y otra” del 15 de marzo de 2007, entre muchos otros). Al expedirse

2907
DE JUSTICIA DE LA NACION
330
sobre el tema, el acreedor planteó la inaplicabilidad de la ley 26.167,
mientras que el deudor solicitó su aplicación al caso (fs. 74/75, 76 y
79/80, respectivamente).
8º) Que el recurso extraordinario es formalmente admisible por-
que en autos se ha objetado la validez e inteligencia de normas federa-
les y la sentencia definitiva del superior tribunal de la causa ha sido
contraria al derecho que el apelante fundó en ellas (art. 14, inc. 3º, de
la ley 48). También se han invocado causales de arbitrariedad que son
inescindibles de los temas federales en discusión y deben ser examina-
das conjuntamente (Fallos: 323:1625, entre muchos otros).
9º) Que en la presente causa se encuentra en juego la pretensión
del deudor de que se apliquen las normas que previeron el régimen de
refinanciación hipotecaria (leyes 25.798, 25.908 y 26.167 y decreto re-
glamentario 1284/2003), efectuada con posterioridad al dictado de una
sentencia que declaró la inconstitucionalidad del decreto 214/2002 y
dispuso la transformación del capital adeudado por aplicación del prin-
cipio del esfuerzo compartido, decisión a la que los magistrados
intervinientes atribuyeron el carácter de firme y pasada en autoridad
de cosa juzgada por no haber sido impugnada.
10) Que con particular referencia a la cuestión que se plantea en
autos, la ley 25.798, modificada por la 25.908, dispone que en caso de
encontrarse pendiente un proceso de ejecución hipotecaria contra el
deudor, la acreditación en el expediente del ejercicio de la opción por el
régimen de refinanciación hipotecaria limitará los efectos de la sen-
tencia de remate a la determinación de la procedencia o no del juicio
ejecutivo y a la liquidación final de la deuda exigible, y que sólo podrá
continuarse con el cumplimiento de la resolución firme si el agente
fiduciario no considerase admisible el mutuo (art. 16, inc. c).
Asimismo, contempla que en el supuesto de que el mencionado
ejercicio de la opción fuese posterior a la fecha en que hubiese quedado
firme la sentencia de remate y anterior a la subasta, su cumplimiento
se suspende hasta que el fiduciario notifique la no admisibilidad
(art. 16, inc. d).
11) Que, a su vez, el art. 17 de la ley 26.167, después de señalar
que las disposiciones de dicha ley son de orden público, establece que
se aplicará retroactivamente a todos los supuestos contemplados en
ella, salvo que se hubiere perfeccionado la venta “y siempre que no se

2908
FALLOS DE LA CORTE SUPREMA
330
afecten derechos amparados por garantías constitucionales, por cons-
tituir directa derivación del artículo 14 bis de la Constitución Nacio-
nal, en cuanto ordena al Congreso Nacional la protección integral de
la familia y el establecimiento del acceso a una vivienda digna”.
12) Que habida cuenta de que en el trámite del proceso ejecutivo
las partes consintieron que se debatiese de manera irrestricta acerca
de la validez constitucional de las normas de emergencia y de que
dicha cuestión ha sido resuelta en términos que no admiten recurso
alguno, el tema no podrá ser replanteado en otro juicio ulterior que
permita alcanzar un resultado distinto, motivo por el cual puede afir-
marse que en el caso la sentencia de fs. 48/56 del expediente principal
ha pasado en autoridad de cosa juzgada formal y material.
13) Que aceptado dicho carácter respecto del referido pronuncia-
miento, que no fue objeto de recursos ordinarios ni extraordinarios a
pesar de que la índole de la cuestión debatida le permitía al deudor
llegar hasta esta instancia, ha precluido a su respecto la posibilidad
de hacerlo en el futuro, por lo que al examinar la cuestión planteada
no debe perderse de vista que la Corte Suprema ha resuelto que los
derechos reconocidos en una sentencia pasada en autoridad de cosa
juzgada han quedado incorporados al patrimonio y se encuentran pro-
tegidos por el art. 17 de la Constitución Nacional (conf. Fallos: 209:303;
237:563; 307:1709; 308:916 y 319:3241).
14) Que la tutela del derecho referido resultaría desconocida de
hacerse lugar a la pretensión del ejecutado, lo que lleva a concluir que
es acertada la decisión de ambas instancias que consideraron ina-
plicables las disposiciones sobre refinanciación hipotecaria frente a lo
que se había resuelto respecto de las normas de emergencia relaciona-
das con la pesificación de las obligaciones de dar sumas de dinero pac-
tadas originariamente en dólares estadounidenses u otra moneda ex-
tranjera.
15) Que no puede dejar de advertirse que la aplicación lisa y llana
del régimen de refinanciación hipotecaria al caso implicaría reeditar
el debate sobre temas que ya han sido objeto de tratamiento y resolu-
ción en etapas del proceso que el ejecutado ha dejado precluir, aparte
de que llevaría a que la deuda se abonase de acuerdo al régimen esta-
blecido por la ley 26.167, que contempla pautas para su determina-
ción y liquidación que difieren de las ya fijadas en la presente ejecu-
ción hipotecaria.

2909
DE JUSTICIA DE LA NACION
330
16) Que aun cuando el Tribunal ha admitido que las normas cuya
aplicación pretende el recurrente han sido dictadas con el fin de dar
una solución definitiva, justa y equitativa a los conflictos suscitados
por la crisis económica respecto de los deudores hipotecarios que tu-
viesen comprometida su vivienda única y familiar, ello no constituye
un argumento eficaz para desconocer la estabilidad de las decisiones
jurisdiccionales que, por constituir un presupuesto ineludible de la
seguridad jurídica, es uno de los presupuestos del ordenamiento social
cuya ausencia o debilitamiento pondría en crisis a la íntegra juridicidad
del sistema (conf. Fallos: 315:2406 y arg. Fallos: 291:423; 299:373;
301:762; 307:1289; 308:117 y 139; 311:651 y 2058; 313:904; 319:1885;
323:2648 y 328:3299).
17) Que no obsta a lo expresado el carácter de orden público asig-
nado por el legislador a la ley 26.167 ni lo reglado respecto de su apli-
cación retroactiva (art. 17), como tampoco la sanción de la nulidad
prevista con relación a las resoluciones que resulten contrarias a la
suspensión contemplada en su art. 9, pues el carácter de orden públi-
co de las leyes de emergencia no alcanza para modificar los efectos de
la cosa juzgada que también reviste dicho carácter y goza de plena
protección constitucional (ver Fallos: 235:171 y 512; 250:751; 259:88 y
289; 296:584; 307:1289; 311:495; 317:161 y 992; 319:3241; 321:172 y
328:4801; arg. art. 3 del Código Civil, texto según ley 17.711).
18) Que el hecho de que este Tribunal haya considerado razona-
bles las medidas adoptadas para paliar las consecuencias de la grave
crisis económica –causa R.320.XLII “Rinaldi, Francisco Augusto y otro
c/ Guzmán Toledo, Ronal Constante y otra” del 15 de marzo de 2007–
no resulta óbice para resolver la cuestión en el sentido indicado, ya
que la alteración de los derechos adquiridos que las leyes pueden lle-
gar a disponer circunstancialmente para asegurar el bien común com-
prometido en la emergencia por desequilibrios económicos o sociales u
otros motivos de análogo carácter extraordinario, no pueden alcanzar
la inmutabilidad de la cosa juzgada, porque no hay bienestar posible
fuera del orden (Fallos: 307:1289 y su cita; 319:3241 y 326:2546).
19) Que, a mayor abundamiento, cabe señalar que las considera-
ciones precedentes y la falta de impugnación concreta respecto del
argumento corroborante utilizado por la cámara vinculado con el
art. 11, in fine, de la ley 25.561, según texto de la 25.820, hacen inne-
cesario ahondar en la interpretación del alcance de esta norma que,
por lo demás, excluye expresamente la posibilidad de aplicar las solu-

2910
FALLOS DE LA CORTE SUPREMA
330
ciones previstas en las normas de emergencia en materia de pesificación
cuando las situaciones hubiesen sido resueltas mediante acuerdos pri-
vados o sentencias judiciales.
20) Que, sin perjuicio de lo expresado, se advierte que el art. 7 de
la ley 26.167, al referirse al pago de la deuda fijada en los términos del
art. 6, prevé la hipótesis de que “...el pago, a pedido del deudor, sea
realizado, en forma parcial o total, con aportes del Fondo Fiduciario
previsto en la ley 25.798...”. Ello pone en evidencia que el legislador
consideró también la posibilidad de que, en ciertas hipótesis, el deu-
dor pudiera cancelar una parte del crédito del ejecutante con fondos
propios y pagar la parte restante mediante la utilización del fondo
fiduciario, supuestos entre los que no puede excluirse al presente caso.
21) Que la exégesis propuesta encuentra sustento en una compren-
sión armónica del referido art. 7 y los principios que llevan a preser-
var los derechos patrimoniales reconocidos al acreedor en sede judi-
cial, los cuales no se verían menoscabados por la alternativa que con-
fiere al deudor de acudir a la ayuda del agente fiduciario –entidad que
ha considerado elegible el mutuo– para satisfacer parcialmente el cré-
dito, pues de ese modo se daría cumplimiento al art. 15 de la ley 26.167,
que contribuye a sustentar la solución al disponer que “en caso de
duda sobre la aplicación, interpretación o alcance de la presente ley,
los jueces se decidirán en el sentido más favorable a la subsistencia y
conservación de la vivienda digna y la protección integral de la fami-
lia, en los términos del art. 14 bis de la Constitución Nacional”.
22) Que, en consecuencia, a pesar de que las partes no se han ma-
nifestado en el sentido de lograr que la obligación se cumpla en la
forma señalada, el sistema legal admite que el deudor lo haga y pague
con fondos propios la parte de la deuda que no resulta aquí cubierta
por el sistema de refinanciación hipotecaria, sin que ello implique vul-
nerar derechos del acreedor alcanzados por la protección de la Ley
Fundamental, lo que permite compatibilizar lo resuelto por el Tribu-
nal en el precedente “Rinaldi”, en cuanto a la validez constitucional de
las normas cuya aplicación se pretende, con el principio de la cosa
juzgada que también cuenta con protección constitucional.
Por ello, y habiendo dictaminado el señor Procurador General, se
declara procedente la queja, formalmente admisible el recurso extraor-
dinario interpuesto por el ejecutado, se revoca la sentencia apelada en

2911
DE JUSTICIA DE LA NACION
330
cuanto declaró inaplicable al caso el régimen de refinanciación hipote-
caria y se dispone que el juez de primera instancia fijará un plazo –no
mayor de 30 días– para que el deudor manifieste si optará por cance-
lar el crédito en la forma indicada en el presente fallo, a los efectos de
que se cumplan los demás actos previstos en la ley 26.167 para hacer
efectiva la sentencia y el pago al acreedor. En caso de no hacerlo, la
ejecución continuará en la forma prevista por las normas procesales
correspondientes.
Las costas de la ejecución serán soportadas en los términos del
art. 558 del Código Procesal Civil y Comercial de la Nación, salvo las
correspondientes a los incidentes generados con motivo de los planteos
atinentes a la aplicación del régimen de refinanciación hipotecaria,
como las de esta instancia que se imponen en el orden causado atento
a la forma en que se decide y a la naturaleza de las cuestiones pro-
puestas.
Notifíquese, agréguese la queja al principal, reintégrese el depósi-
to y vuelvan los autos al tribunal de origen para que se cumpla, según
el alcance indicado, con el trámite previsto por la ley 26.167.
```

### [span 19] header_pagina (1135–1135)
```
2905
```

### [span 20] header_pagina (1136–1136)
```
DE JUSTICIA DE LA NACION
```

### [span 21] header_pagina (1137–1137)
```
330
```

### [span 22] header_pagina (1177–1177)
```
2906
```

### [span 23] header_pagina (1178–1178)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 24] header_pagina (1179–1179)
```
330
```

### [span 25] header_pagina (1220–1220)
```
2907
```

### [span 26] header_pagina (1221–1221)
```
DE JUSTICIA DE LA NACION
```

### [span 27] header_pagina (1222–1222)
```
330
```

### [span 28] header_pagina (1261–1261)
```
2908
```

### [span 29] header_pagina (1262–1262)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 30] header_pagina (1263–1263)
```
330
```

### [span 31] header_pagina (1303–1303)
```
2909
```

### [span 32] header_pagina (1304–1304)
```
DE JUSTICIA DE LA NACION
```

### [span 33] header_pagina (1305–1305)
```
330
```

### [span 34] header_pagina (1346–1346)
```
2910
```

### [span 35] header_pagina (1347–1347)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 36] header_pagina (1348–1348)
```
330
```

### [span 37] header_pagina (1387–1387)
```
2911
```

### [span 38] header_pagina (1388–1388)
```
DE JUSTICIA DE LA NACION
```

### [span 39] header_pagina (1389–1389)
```
330
```

### [span 40] firma (1408–1409)
```
RICARDO LUIS LORENZETTI — ELENA I. HIGHTON DE NOLASCO — ENRIQUE
SANTIAGO PETRACCHI — JUAN CARLOS MAQUEDA — CARMEN M. ARGIBAY
```

### [span 41] catch_all (1410–1410)
```
(en disidencia).
```

### [span 42] disidencia (1411–1550)
**Header**: DISIDENCIA DE LA SEÑORA
```
DISIDENCIA DE LA SEÑORA
MINISTRA DOCTOR A DOÑA CARMEN M. ARGIBAY
Considerando:
1º) El 3 de abril de 1998 el demandado en la presente causa, Claudio
Rafael Sparano, compró un inmueble en la localidad de Villa Insupe-
rable, Partido de La Matanza, Provincia de Buenos Aires, sito en la
Av. Crovara Nº 1724 y, según dice la escritura pública que instrumentó
la venta, ésta se pactó por el precio total de dólares estadounidenses
noventa mil (U$S 90.000). En ese mismo acto, el comprador pagó la
suma de dólares estadounidenses treinta mil (U$S 30.000) y se obligó
a pagar el saldo del precio –U$S 60.000– en 166 cuotas mensuales,
iguales y consecutivas de U$S 1.500, que incluían el interés convenido

2912
FALLOS DE LA CORTE SUPREMA
330
entre las partes, venciendo la primera el 7 de enero de 1999. En ga-
rantía del cumplimiento de lo pactado, el deudor constituyó derecho
real de hipoteca sobre el inmueble adquirido en favor de los acreedo-
res (ver fs. 1/5 del expediente principal).
El 30 de junio de 2003, ante la mora en que incurrió el comprador
desde el 1 de abril de 2001, uno de los coacreedores inició la presente
ejecución hipotecaria por la suma de U$S 25.120,42, con más sus inte-
reses, gastos y costas del proceso. Para ello el actor planteó la
inconstitucionalidad de toda la normativa de emergencia, en la medi-
da que le impedía ejercer plenamente su derecho personal, protegido
por el artículo 17 de la Constitución Nacional.
Contra dicha pretensión, el deudor se presentó y solicitó que la
deuda se “pesifique”, es decir, se reconvierta en pesos a la par, o sea,
un peso por cada dólar adeudado. Asimismo, defendió la validez cons-
titucional de la ley 25.561 y del decreto 214/2002.
2º) El juez de primera instancia declaró la inconstitucionalidad
del decreto 214/2002 y de las normas ampliatorias y complementa-
rias, y mandó llevar adelante la ejecución por el capital adeudado que
–por aplicación de la doctrina del esfuerzo compartido– debía calcu-
larse a razón de un peso por cada dólar, con más el 50% de la brecha
entre $ 1 y el valor de la divisa norteamericana según la cotización
vigente al momento del pago, con más sus intereses.
3º) Dicha sentencia fue notificada según constancia obrante a fs. 58
del expediente principal y no fue objeto de recurso de apelación por el
ejecutado.
Con posterioridad este último denunció que había hecho uso de la
opción prevista en el art. 6º de la ley 25.798 para ingresar en el siste-
ma de refinanciación hipotecaria, trámite administrativo que culminó
con la firma del correspondiente contrato con el Banco de la Nación
Argentina (ver fs. 63/64, fs. 121 y fs. 137/145 de las actuaciones prin-
cipales).
Acto seguido, el ejecutante sostuvo que las leyes 25.798 y 25.908
resultaban inaplicables al caso pues se encontraba firme la sentencia
que había resuelto acerca de la inconstitucionalidad de las normas de
emergencia económica, motivo por el cual su parte había adquirido

2913
DE JUSTICIA DE LA NACION
330
irrevocablemente los derechos que emanaban de ella. En forma subsi-
diaria planteó la inconstitucionalidad del mencionado régimen de
refinanciación hipotecaria.
4º) El juez de primera instancia señaló que al haber pasado en
autoridad de cosa juzgada el pronunciamiento que mandaba llevar
adelante la ejecución por el capital reclamado, calculado según el prin-
cipio del esfuerzo compartido, no se podía pretender habilitar nueva-
mente el debate de lo actuado hasta ese momento, so pena de vulnerar
los principios de la cosa juzgada y de preclusión y el derecho de propie-
dad del actor. En base a ello, y en tanto el régimen previsto por la ley
25.798 prevé que el capital se liquide de una forma distinta de la que
se estableció en la sentencia que se encuentra firme, el a quo resolvió
declararlo inaplicable al caso. Apelada la resolución por el ejecutado,
la Sala L de la Cámara Nacional de Apelaciones en lo Civil la confir-
mó.
Contra dicho fallo el demandado interpuso el recurso extraordina-
rio que, denegado, dio origen a esta presentación directa. Afirma que
se ha incurrido en un error en la consideración legal del caso, pues se
han desconocido normas de orden público que contemplan los alcances
y efectos de la cosa juzgada para este tipo de causas (art. 16, incs. c y
d, de la ley 25.798, texto según ley 25.908); que la decisión vulnera el
derecho de igualdad ante la ley porque establece un privilegio a favor
del actor y le otorga la posibilidad de cobrar su crédito evadiendo la
aplicación del régimen legal que arbitró los medios para soportar los
estragos de la crisis, aparte de que resulta injusta porque le niega la
solución dada por el legislador a quien adquirió su vivienda única des-
tinada al uso familiar con el fruto de su trabajo y lo somete a la pérdi-
da del bien.
Cuando la causa se encontraba ya en esta Corte, se dictó la ley
26.167, por lo que se dispuso oír a las partes respecto a dicha norma
(conf. fs. 71 del recurso de queja). Al expedirse sobre el tema, el acree-
dor planteó la inaplicabilidad de la ley, mientras que el deudor solicitó
su aplicación al caso.
5º) Sin perjuicio de señalar que, como surge de la anterior reseña
del caso y sus constancias –especialmente de la escritura obrante a
fojas 1 a 5 del expediente principal–, en autos no se trata de un mutuo
sino de una hipoteca sobre el saldo de precio por la compra de un in-

2914
FALLOS DE LA CORTE SUPREMA
330
mueble, por lo que resultaría al menos dudosa la aplicación del régi-
men de refinanciación hipotecaria y de la ley 26.167, lo cierto es que el
deudor pretende que se aplique dicha normativa al supuesto de autos.
Ahora bien, tal pretensión fue efectuada con posterioridad al dic-
tado de la sentencia que declaró la inconstitucionalidad del decreto
214/2002 y dispuso la transformación del capital adeudado por aplica-
ción del principio del esfuerzo compartido, decisión que, tal como co-
rrectamente lo resolvieron los tribunales de grado, ha quedado firme y
pasada en autoridad de cosa juzgada al no haber sido objeto de recur-
so alguno por parte del ejecutado.
En efecto, la aplicación de dicho régimen al caso implicaría reedi-
tar el debate sobre temas que ya han sido objeto de tratamiento y
resolución en etapas del proceso que el ejecutado ha dejado precluir y,
además, hacer caso omiso a los derechos reconocidos al actor en el
pronunciamiento firme, que han quedado así incorporados a su patri-
monio y se encuentran protegidos por el artículo 17 de la Constitución
Nacional (Fallos: 209:303; 237:563; 307:1709; 308:916, entre otros).
6º) No obsta a lo expresado el carácter de orden público asignado
por el legislador a la ley 26.167 ni lo reglado respecto de su aplicación
retroactiva (art. 17), como tampoco la sanción de nulidad prevista con
relación a las resoluciones que resulten contrarias a la suspensión con-
templada en su art. 9º, pues el carácter de orden público de las leyes
de emergencia no alcanza para modificar los efectos de la cosa juzgada
que también reviste dicho carácter y goza de plena protección consti-
tucional (Fallos: 235:171 y 512; 250:751; 296:584, entre otros).
7º) En tales condiciones, el recurso extraordinario, cuya denega-
ción origina esta queja, es inadmisible, pues el derecho que el recu-
rrente ha fundado en las leyes federales de emergencia no guarda re-
lación directa e inmediata con la sentencia apelada que se encuentra
suficientemente fundada en la cosa juzgada.
Por ello, se desestima la queja. Declárase perdido el depósito de
fs. 1.
Notifíquese y, oportunamente, archívese, previa devolución de los
autos principales.
CARMEN M. ARGIBAY.

2915
DE JUSTICIA DE LA NACION
330
Recurso de hecho interpuesto por Claudio Rafael Sparano, con el patrocinio del Dr.
Carlos E. Spini Slocker.
Tribunal de origen: Sala L de la Cámara Nacional de Apelaciones en lo Civil.
Tribunales que intervinieron con anterioridad: Juzgado Nacional de Primera Ins-
tancia en lo Civil Nº 59.
```

### [span 43] header_pagina (1424–1424)
```
2912
```

### [span 44] header_pagina (1425–1425)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 45] header_pagina (1426–1426)
```
330
```

### [span 46] header_pagina (1463–1463)
```
2913
```

### [span 47] header_pagina (1464–1464)
```
DE JUSTICIA DE LA NACION
```

### [span 48] header_pagina (1465–1465)
```
330
```

### [span 49] header_pagina (1504–1504)
```
2914
```

### [span 50] header_pagina (1505–1505)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 51] header_pagina (1506–1506)
```
330
```

### [span 52] header_pagina (1543–1543)
```
2915
```

### [span 53] header_pagina (1544–1544)
```
DE JUSTICIA DE LA NACION
```

### [span 54] header_pagina (1545–1545)
```
330
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=1550 | linea_inicio_proximo_caso=1545 | delta=-6
**Alertas**: `solapado_con_proximo`


---

## 329_p5085 — Agroindustrias Inca S.A. (Violino, Osvaldo C. c/) | Violino, Osvaldo C. c/ Agroindustrias Inca S.A.

**Localización**
- Archivo: `LibroVol329.4.md`
- Páginas catálogo: 5085–5089 | Página consultada: 5089
- Líneas catálogo: 7474–7612 | Línea fin real: 7613 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 7474–7474 | 1 |
| 2 | caratula | 7475–7475 | 1 |
| 3 | sumario [1] | 7476–7482 | 7 |
| 4 | sumario [2] | 7483–7486 | 4 |
| 5 | dictamen | 7487–7576 | 90 |
| 6 | header_pagina | 7506–7506 | 1 |
| 7 | header_pagina | 7507–7507 | 1 |
| 8 | header_pagina | 7508–7508 | 1 |
| 9 | header_pagina | 7544–7544 | 1 |
| 10 | header_pagina | 7545–7545 | 1 |
| 11 | header_pagina | 7546–7546 | 1 |
| 12 | cuerpo_mayoria | 7577–7591 | 15 |
| 13 | header_pagina | 7582–7582 | 1 |
| 14 | header_pagina | 7583–7583 | 1 |
| 15 | header_pagina | 7584–7584 | 1 |
| 16 | firma | 7592–7594 | 3 |
| 17 | voto | 7595–7613 | 19 |
| 18 | header_pagina | 7611–7611 | 1 |
| 19 | header_pagina | 7612–7612 | 1 |
| 20 | header_pagina | 7613–7613 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=0 (0.0% del bloque, n=140)

---

### [span 1] header_pagina (7474–7474)
```
329
```

### [span 2] caratula (7475–7475)
```
OSVALDO C. VIOLINO V. AGROINDUSTRIAS INCA S.A.
```

### [span 3] sumario [1] (7476–7482)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
RECURSO EXTRAORDINARIO: Requisitos propios. Sentencia definitiva. Resolucio-
nes anteriores a la sentencia definitiva. Varias.
No constituye sentencia definitiva el pronunciamiento que decretó la nulidad de
la subasta en virtud de la cual el apelante ejecutó su crédito contra la fallida
cuando ya existía trámite concursal, si el recurrente puede hacer efectivo su cré-
dito mediante las vías previstas en la ley de concursos.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 4] sumario [2] (7483–7486)
**Header**: RECURSO EXTRAORDINARIO: Principios generales.
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Principios generales.
Es inadmisible (art. 280 del Código Procesal Civil y Comercial de la Nación) el
recurso extraordinario interpuesto contra el pronunciamiento que declaró la
nulidad de una subasta (Voto de la Dra. Elena I. Highton de Nolasco).
```

### [span 5] dictamen (7487–7576)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
La Cámara Nacional de Apelaciones en lo Comercial resolvió a
fs. 251/52, confirmar las decisiones del tribunal de primera instancia
que decretó la nulidad de la subasta y desestimó la pretensión de dar
por perdido el derecho a la sindicatura a contestar el traslado del me-
morial de apelación de la actora (ver fs. 213/15 y 242).
Para así decidir, el tribunal a quo destacó, que la subasta de autos
fue realizada con posterioridad al decreto de quiebra y bajo la jurisdic-
ción de juez incompetente, razón que habilitaba la nulidad del acto
por cuanto se verificaba en el caso una modificación de la situación
patrimonial de la fallida susceptible de ocasionar gravamen a los acree-
dores.
Agregó, que el accionante adquirió el inmueble por compensación
de su crédito, instituto que no es aplicable en el marco de la ley 24.522,
si no media autorización del juez de la quiebra, y que ella no se efectuó
en la proporción del crédito que presumiblemente podría tener el acree-

5086
FALLOS DE LA CORTE SUPREMA
329
dor para serle oponible a la masa de acreedores, ya que no se ha demos-
trado que haya habido petición de verificación en el juicio universal.
– II –
Contra dicha decisión la actora interpuso recurso extraordinario a
fs. 260/270, el que fue concedido a fs. 279/280.
Manifiesta el recurrente, que la sentencia es arbitraria por cuanto
no constituye derivación razonada del derecho vigente y de los hechos
de la causa, y genera la afectación a su derecho de propiedad, a la
igualdad y a los principios de defensa en juicio y seguridad jurídica al
decidir extra-petita, violentar la cosa juzgada, y no atender sus planteos
sobre el carácter privilegiado del crédito.
En lo que aquí interesa, el apelante sostiene que la nulidad decre-
tada nunca se solicitó, que este juicio tramitó en extraña jurisdicción,
y se hizo, cumpliendo con todos los requisitos procesales, mientras que
ni el proceso de quiebra ni el accionar de la sindicatura, se ajustan a
los mandatos del artículo 89 de la ley 24.522, y tampoco a lo ordenado
en el auto de falencia, pues no inscribieron las inhibiciones, ni se pu-
blicaron los edictos obligados por la ley, dejándose vencer todos los
plazos de caducidad.
Pone de relieve además que la existencia de quiebra, recién se hizo
conocer cuando todos los actos habían pasado en autoridad de cosa
juzgada y vencidos los plazos de caducidad para objetar los producidos
en sede provincial.
Respecto de las garantías constitucionales afectadas, señala que
se ha violentado el principio de igualdad ante la ley permitiendo a la
sindicatura contestar un traslado fuera de plazo, y resolviendo sobre
cuestiones no planteadas, alterando el derecho de propiedad consoli-
dado del adquirente en subasta, máxime cuando la comunicación del
juzgado haciendo conocer el estado de quiebra sólo ordenaba abste-
nerse de realizar nuevas subastas, entrega de posesión o pagos libra-
dos.
– III –
Cabe señalar de inicio, que no se verifica en el caso la existencia de
una decisión definitiva que importe la pérdida del derecho del recu-

5087
DE JUSTICIA DE LA NACION
329
rrente respecto del crédito contra la hoy fallida, el que se puede hacer
efectivo mediante las vías previstas en la ley de concursos.
En efecto, se desprende de las constancias de autos que el apelan-
te ejecutó un crédito contra la fallida por medio de una acción indivi-
dual y obtuvo su satisfacción por vía de compensación, mediante la
adquisición en subasta judicial de un bien que constituye parte del
activo falencial cuando ya existía un trámite concursal, que la había
desapoderado de sus bienes, generado la suspensión de las acciones
judiciales en curso y obligado a todos los acreedores a hacer valer sus
pretensiones en tal procedimiento universal (artículos 107, 125,126,
130,211 y concordantes de la ley 24.522).
Sin perjuicio de ello corresponde poner de resalto que más allá de
las contingencias procesales que parecieran favorecer al recurrente,
como consecuencia de la inadecuada publicidad realizada en el trámi-
te del proceso de quiebra, lo indudablemente cierto es que un acreedor
de la fallida pretende cobrar sus acreencias, con apoyo en tales cir-
cunstancias formales afectando los principios sustanciales y de orden
público del proceso universal destinados a resguardar la igualdad de
trato de todos los acreedores y el principio de que tales bienes consti-
tuyen la prenda común de todos ellos.
Por último cabe poner de relieve en orden a la invocación de agra-
vios irreparables por afectación al derecho de propiedad que alega el
recurrente, con apoyo en la existencia de un privilegio especial que le
permitiría cobrar de modo preferente su crédito, que conforme lo seña-
la el a quo no ha mediado reconocimiento de tal privilegio, ni ha recaído
decisión que permita considerar que se ha agotado la vía procesal de
verificación para su reconocimiento y debida satisfacción.
Por todo ello, opino que corresponde que V. E. debe desestimar el
recurso extraordinario interpuesto. Buenos Aires, 20 de abril de 2005.
Marta A. Beiró de Gonçalvez.
```

### [span 6] header_pagina (7506–7506)
```
5086
```

### [span 7] header_pagina (7507–7507)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 8] header_pagina (7508–7508)
```
329
```

### [span 9] header_pagina (7544–7544)
```
5087
```

### [span 10] header_pagina (7545–7545)
```
DE JUSTICIA DE LA NACION
```

### [span 11] header_pagina (7546–7546)
```
329
```

### [span 12] cuerpo_mayoria (7577–7591)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 14 de noviembre de 2006.
Vistos los autos: “Violino, Osvaldo C. c/ Agroindustrias Inca S.A. s/
ordinario”.

5088
FALLOS DE LA CORTE SUPREMA
329
Considerando:
Que las cuestiones propuestas por el apelante han sido objeto de
adecuado tratamiento en el dictamen de la señora Procuradora Fiscal
subrogante, a cuyos fundamentos y conclusiones corresponde remitir
por razones de brevedad.
Por ello, se desestima el recurso extraordinario interpuesto. Con
costas. Notifíquese y, oportunamente, remítase.
```

### [span 13] header_pagina (7582–7582)
```
5088
```

### [span 14] header_pagina (7583–7583)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 15] header_pagina (7584–7584)
```
329
```

### [span 16] firma (7592–7594)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO (según su
voto) — CARLOS S. FAYT — JUAN CARLOS MAQUEDA — E. RAÚL ZAFFARONI —
RICARDO LUIS LORENZETTI.
```

### [span 17] voto (7595–7613)
**Header**: VOTO DE LA SEÑORA VICEPRESIDENTA
```
VOTO DE LA SEÑORA VICEPRESIDENTA
DOCTORA DOÑA ELENA I. HIGHTON DE NOLASCO
Considerando:
Que el recurso extraordinario es inadmisible (art. 280 del Código
Procesal Civil y Comercial de la Nación).
Por ello, oída la señora Procuradora Fiscal subrogante, se declara
improcedente el recurso extraordinario, con costas. Notifíquese y de-
vuélvase.
ELENA I. HIGHTON DE NOLASCO.
Recurso extraordinario interpuesto por la actora, representada por el Dr. Alvaro G.
Casalins, con el patrocinio de los Dres. Jorge E. Anzorreguy y Alberto Daniel
Cardiello.
Traslado contestado por el síndico (Ricardo M. Lostao), representado por el Dr.
Luis A. Promesti.
Tribunal de origen: Cámara Nacional de Apelaciones en lo Comercial, Sala B.

5089
DE JUSTICIA DE LA NACION
329
```

### [span 18] header_pagina (7611–7611)
```
5089
```

### [span 19] header_pagina (7612–7612)
```
DE JUSTICIA DE LA NACION
```

### [span 20] header_pagina (7613–7613)
```
329
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=7613 | linea_inicio_proximo_caso=7613 | delta=-1
**Alertas**: `solapado_con_proximo`


---

## 329_p4755 — Empresa Nacional de Telecomunicaciones y Estado Nacional (Municipalidad de la Capital de Catamarca c/) | Municipalidad d

**Localización**
- Archivo: `LibroVol329.3.md`
- Páginas catálogo: 4755–4762 | Página consultada: 4762
- Líneas catálogo: 68831–69090 | Línea fin real: 68996 (status_fin=`fin_dentro_bloque`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 68831–68831 | 1 |
| 2 | catch_all | 68832–68859 | 28 |
| 3 | caratula | 68860–68860 | 1 |
| 4 | sumario [1] | 68861–68868 | 8 |
| 5 | header_pagina | 68866–68866 | 1 |
| 6 | header_pagina | 68867–68867 | 1 |
| 7 | header_pagina | 68868–68868 | 1 |
| 8 | sumario [2] | 68869–68877 | 9 |
| 9 | sumario [3] | 68878–68884 | 7 |
| 10 | sumario [4] | 68885–68889 | 5 |
| 11 | sumario [5] | 68890–68894 | 5 |
| 12 | dictamen | 68895–68993 | 99 |
| 13 | header_pagina | 68901–68901 | 1 |
| 14 | header_pagina | 68902–68902 | 1 |
| 15 | header_pagina | 68903–68903 | 1 |
| 16 | header_pagina | 68940–68940 | 1 |
| 17 | header_pagina | 68941–68941 | 1 |
| 18 | header_pagina | 68942–68942 | 1 |
| 19 | header_pagina | 68984–68984 | 1 |
| 20 | header_pagina | 68985–68985 | 1 |
| 21 | header_pagina | 68986–68986 | 1 |
| 22 | cuerpo_mayoria | 68994–68996 | 3 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=28 (16.87% del bloque, n=166)

---

### [span 1] header_pagina (68831–68831)
```
329
```

### [span 2] catch_all (68832–68859)
```
dad como grupo y a nadie en particular. Por otra parte, es un bien al
cual tienen acceso todas las personas por su sola condición de habitan-
tes que se financia con fondos públicos. De tal modo, la lesión tiene
incidencia colectiva, pues implica un perjuicio potencial para todos los
posibles usuarios y para la comunidad contribuyente. Además, al no
tratarse de un bien sujeto a titularidad individual, nadie puede invo-
car un derecho o interés propio que le otorgue legitimación procesal
para promover la actuación del poder judicial en su defensa.
7º) Una vez hechas las consideraciones precedentes, corresponde-
rá determinar si los actores pueden ser clasificados en alguna de las
categorías de sujetos legitimados que menciona el artículo 43, segun-
do párrafo de la Constitución Nacional. En particular, deberá tomarse
en cuenta que las asociaciones demandantes tienen por fin estatutario
el de velar por las condiciones del ambiente hospitalario. Por otra par-
te, también se han presentado actores que se dicen afectados directos
por los riesgos derivados de las condiciones en que se encuentra el
hospital público en que trabajan por el incumplimiento del gobierno
provincial.
En tales condiciones, se hace lugar a la queja, se declara proceden-
te el recurso extraordinario y se revoca la sentencia. Con costas. Vuel-
van los autos al tribunal de origen para que, por quien corresponda, se
dicte un nuevo fallo con arreglo al presente. Agréguese la queja al
principal. Notifíquese y remítase.
CARMEN M. ARGIBAY.
Recurso de hecho interpuesto por los actores, representados por el Dr. Juan P.
Recchiuto – Dra. Verónica V. Pose y José W. Tobías.
Tribunal de origen: Corte de Justicia de Salta.
MUNICIPALIDAD DE LA CAPITAL DE CATAMARCA
```

### [span 3] caratula (68860–68860)
```
MUNICIPALIDAD DE LA CAPITAL DE CATAMARCA V. EMPRESA NACIONAL DE TELECOMUNICACIONES Y ESTADO NACIONAL

```

### [span 4] sumario [1] (68861–68868)
**Header**: RECURSO EXTRAORDINARIO: Principios generales.
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Principios generales.
El recurso extraordinario es inadmisible en lo que respecta a la inclusión de los
intereses en la base regulatoria (art. 280 del Código Procesal Civil y Comercial
de la Nación).

4756
FALLOS DE LA CORTE SUPREMA
329
```

### [span 5] header_pagina (68866–68866)
```
4756
```

### [span 6] header_pagina (68867–68867)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 7] header_pagina (68868–68868)
```
329
```

### [span 8] sumario [2] (68869–68877)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Procedencia del recurso. Excesos u omisiones en el pronunciamiento.
Corresponde dejar sin efecto la sentencia que, sobre la base de afirmar
dogmáticamente que estimaba justa la regulación fijada por el juez federal, la
confirmó sin hacerse cargo de los concretos agravios referentes a la necesidad de
apartarse de la escala mínima arancelaria, sin que salve esa omisión el desarro-
llo efectuado para justificar que cabía aplicar la ley 21.839 sin las modificaciones
introducidas por la ley 24.432, ya que la posibilidad de regular por debajo del
mínimo arancelario preexistía a la sanción de esta última norma.
```

### [span 9] sumario [3] (68878–68884)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Procedencia del recurso. Excesos u omisiones en el pronunciamiento.
Corresponde dejar sin efecto la sentencia en tanto no se hizo cargo de ninguno de
los argumentos sobre la base de los cuales se solicitó la aplicación de la doctrina
de la Corte y prescindió de las disposiciones de la ley 24.432, que son de neto
carácter procesal y, por tanto, de aplicación inmediata (Voto de los Dres. Enrique
Santiago Petracchi y Carlos S. Fayt).
```

### [span 10] sumario [4] (68885–68889)
**Header**: RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Requisitos propios. Cuestiones no federales. Senten-
cias arbitrarias. Procedencia del recurso. Excesos u omisiones en el pronunciamiento.
Corresponde hacer lugar a los agravios atinentes a las escalas arancelarias si la
cámara prescindió de las disposiciones de la ley 24.432, que son de neto carácter
procesal y, por tanto, de aplicación inmediata (Voto del Dr. Juan Carlos Maqueda).
```

### [span 11] sumario [5] (68890–68894)
**Header**: RECURSO EXTRAORDINARIO: Principios generales.
**Atribución**: (sin atribución detectada)
```
RECURSO EXTRAORDINARIO: Principios generales.
El recurso extraordinario contra el pronunciamiento que confirmó la regulación
de honorarios es inadmisible (art. 280 del Código Procesal Civil y Comercial de
la Nación) (Disidencia de las Dras. Elena I. Highton de Nolasco y Carmen M.
Argibay).
```

### [span 12] dictamen (68895–68993)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
– I –
Contra la sentencia de la Cámara Federal de Apelaciones de
Tucumán (fs. 415/417 de los autos principales, a los que me referiré en

4757
DE JUSTICIA DE LA NACION
329
adelante) que confirmó la regulación de los honorarios de los profesio-
nales que asistieron al Estado Nacional y a la Municipalidad de la
Capital de Catamarca, la Empresa Nacional de Telecomunicaciones
(en liquidación) interpuso el recurso extraordinario de fs. 426/454, que,
denegado (fs. 534), motivó la presente queja.
Los principales agravios del recurrente se centran en tratar de
demostrar la arbitrariedad del veredicto en cuanto a la integración de
los intereses en la base regulatoria empleada para la determinación
de los honorarios y en obtener la modificación conceptual de éstos so-
bre la base de aplicar, no sólo la ley de aranceles 24.432 a toda la
actuación profesional desarrollada en autos, sino también el prece-
dente de la Corte registrado en Fallos: 320:495.
Sintetiza su postura en que el fallo de la alzada revela un desacier-
to en cuanto a las normas aplicables, arbitrariedad manifiesta y gra-
vedad institucional.
– II –
Como ha expresado en forma reiterada la Corte Suprema, las cues-
tiones referentes a los honorarios regulados en las instancias ordina-
rias, a la determinación del interés comprometido en el juicio y a las
bases consideradas a tal fin, así como la interpretación y aplicación de
las normas arancelarias, son –en virtud de su carácter fáctico y proce-
sal– materia extraña a la vía del art. 14 de la ley 48 y, en consecuen-
cia, ajenas al recurso extraordinario (Fallos: 308:881, entre muchos
otros). Sin embargo, V.E. tiene dicho, por otra parte, que se justifica la
excepción a esta doctrina cuando se omita la indispensable funda-
mentación conforme a las circunstancias de la causa, pues el pronun-
ciamiento se torna descalificable como acto judicial (Fallos: 308:1079,
entre otros), o cuando la resolución respectiva utiliza pautas de exce-
siva latitud y omite pronunciarse sobre articulaciones serias y condu-
centes para la decisión (Fallos: 313:248, entre otros).
A mi modo de ver, concurren circunstancias excepcionales en el
sub lite que tornan aplicable al caso la doctrina de la arbitrariedad,
toda vez que el fallo carece del debido rigor de fundamentación, en
tanto el a quo se limita a decidir –sin mayor argumento– que las retri-
buciones se exhiben como justas.

4758
FALLOS DE LA CORTE SUPREMA
329
En efecto, ningún argumento exhibe el a quo para desestimar la
solicitada aplicación al sub examine del precedente de Fallos: 320:495,
donde el Tribunal precisó, en un caso de excepción y ante la magnitud
y desproporción de los montos a abonar, que los jueces debían evaluar,
con un razonable margen de discrecionalidad, que una solución justa
y mesurada no depende exclusivamente del monto del juicio ni de las
escalas arancelarias, sino de un conjunto de pautas previstas en los
regímenes específicos. Ello, con el fin de que la aplicación de fórmulas
matemáticas previstas en las leyes arancelarias sobre la significación
patrimonial de excepción involucrada en determinado juicio no conlle-
ve a establecer honorarios que arrojen valores exagerados.
Asimismo, el tribunal, al confirmar como cuantificación económi-
ca al monto liquidado y consentido de la ejecución, omite considerar
importantes fundamentos plasmados por el aquí quejoso, tales como
que en el importe respectivo se incluyen actualizaciones e intereses.
En mi concepto, las pautas que la Alzada manifestó ponderar, como
la invocación de sus propios pronunciamientos y jurisprudencia de
tribunales inferiores, resultan insuficientes como sustento de su re-
solución y no son bastantes como para rechazar el planteo de la recu-
rrente acerca de la irrazonabilidad de los emolumentos fijados. Máxi-
me, cuando con ello se aparta injustificadamente de los precedentes
de la Corte Suprema respecto de la no integración, a los fines regu-
latorios, de intereses al monto del juicio, dada su naturaleza acceso-
ria respecto del capital, así como su carácter esencialmente indem-
nizatorio de la privación temporaria de éste (Fallos: 308:2257, entre
otros).
Por último, en cuanto al agravio según el cual debió aplicarse in
totum la ley 24.432, dado que los trabajos profesionales se regularon
durante su vigencia, estimo que sólo traduce la discrepancia del ape-
lante sobre lo decidido por los jueces de la causa con fundamentos de
derecho común y de hecho y prueba que, más allá de su acierto o
error, bastan para descartar la existencia de arbitrariedad. Con mayor
razón si lo resuelto se ajusta a lo dicho por la Corte en el precedente
registrado en Fallos: 319:1915, donde expresó que “En el caso de los
trabajos profesionales el derecho se constituye en la oportunidad en
que se los realiza, más allá de la época en que se practique la regula-
ción” por lo cual si fueron llevados a cabo con anterioridad a la entra-
da en vigencia de la nueva disposición legal, mal pueden ser ésta
aplicada sin afectar derechos amparados por garantías constitucio-
nales.

4759
DE JUSTICIA DE LA NACION
329
– III –
Opino, por tanto, que debe hacerse lugar a la queja, declarar pro-
cedente el recurso extraordinario, dejar sin efecto la sentencia apela-
da en cuanto fue materia de éste y disponer que vuelvan los actuados
al tribunal de origen para que dicte un nuevo pronunciamiento con
arreglo a lo expuesto. Buenos Aires, 17 de septiembre de 2003. Nicolás
Eduardo Becerra.
```

### [span 13] header_pagina (68901–68901)
```
4757
```

### [span 14] header_pagina (68902–68902)
```
DE JUSTICIA DE LA NACION
```

### [span 15] header_pagina (68903–68903)
```
329
```

### [span 16] header_pagina (68940–68940)
```
4758
```

### [span 17] header_pagina (68941–68941)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 18] header_pagina (68942–68942)
```
329
```

### [span 19] header_pagina (68984–68984)
```
4759
```

### [span 20] header_pagina (68985–68985)
```
DE JUSTICIA DE LA NACION
```

### [span 21] header_pagina (68986–68986)
```
329
```

### [span 22] cuerpo_mayoria (68994–68996)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 31 de octubre de 2006.
Vistos los autos: “Recurso de hecho deducido por el Estado Nacio-
```

### Borde inferior (transición al próximo caso)
**Estado**: `gap_con_residuo` | linea_fin_real=68996 | linea_inicio_proximo_caso=69091 | delta=94
**Alertas**: `apellido_repetido_en_firma_arrastrada`, `voto_disidencia_individual_en_gap`, `caratula_siguiente_en_gap`

| Línea | Clasificación | Texto |
|------:|---------------|-------|
| 68997 | `apertura_proximo_caso` | nal – Ministerio de Economía en la causa Municipalidad de la Capital |
| 68998 | `no_clasificable` | de Catamarca c/ Empresa Nacional de Telecomunicaciones y Estado |
| 68999 | `no_clasificable` | Nacional”, para decidir sobre su procedencia. |
| 69000 | `no_clasificable` | Considerando: |
| 69001 | `no_clasificable` | 1º) Que respecto de la inclusión de los intereses en la base |
| 69002 | `no_clasificable` | regulatoria, el recurso extraordinario es inadmisible (art. 280 del Có- |
| 69003 | `no_clasificable` | digo Procesal Civil y Comercial de la Nación). |
| 69004 | `no_clasificable` | 2º) Que, en cambio, la sentencia recurrida debe ser descalificada |
| 69005 | `no_clasificable` | con arreglo a la doctrina de la arbitrariedad en cuanto, sobre la base |
| 69006 | `no_clasificable` | de afirmar dogmáticamente que estimaba justa la regulación fijada |
| 69007 | `no_clasificable` | por el juez federal, la confirmó sin hacerse cargo de los concretos agra- |
| 69008 | `no_clasificable` | vios planteados por la actora referentes a la necesidad de apartarse de |
| 69009 | `no_clasificable` | la escala mínima arancelaria, conforme lo autoriza conocida jurispru- |
| 69010 | `no_clasificable` | dencia de esta Corte. |
| 69011 | `no_clasificable` | 3º) Que, por cierto, no salva esa omisión el desarrollo efectuado |
| 69012 | `no_clasificable` | por el a quo para justificar que en el sub lite cabía aplicar la ley 21.839 |
| 69013 | `no_clasificable` | sin las modificaciones introducidas por la ley 24.432, toda vez que la |
| 69014 | `no_clasificable` | posibilidad de regular por debajo del mínimo arancelario preexistía a |
| 69015 | `no_clasificable` | la sanción de esta última norma (Fallos: 322:1537, voto del juez |
| 69016 | `firma_arrastrada` | Vázquez). |
| 69017 | `vacia` |  |
| 69018 | `header_pagina` | 4760 |
| 69019 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |
| 69020 | `header_pagina` | 329 |
| 69021 | `no_clasificable` | Por ello, habiendo dictaminado el señor Procurador General se |
| 69022 | `no_clasificable` | declara procedente la queja y el recurso extraordinario interpuestos y |
| 69023 | `no_clasificable` | se deja sin efecto la sentencia apelada con el alcance indicado. Con |
| 69024 | `no_clasificable` | costas. Vuelvan los autos al tribunal de origen a fin de que, por quien |
| 69025 | `no_clasificable` | corresponda, se dicte nuevo fallo con arreglo al presente. Agréguese la |
| 69026 | `no_clasificable` | queja al principal. Notifíquese y remítase. |
| 69027 | `firma_arrastrada` | ENRIQUE SANTIAGO PETRACCHI (según su voto) — ELENA I. HIGHTON DE |
| 69028 | `firma_arrastrada` | NOLASCO (en disidencia) — CARLOS S. FAYT (según su voto) — JUAN CARLOS |
| 69029 | `firma_arrastrada` | MAQUEDA (según su voto) — E. RAÚL ZAFFARONI — RICARDO LUIS |
| 69030 | `firma_arrastrada` | LORENZETTI — CARMEN M. ARGIBAY (en disidencia) — MARÍA SUSANA |
| 69031 | `no_clasificable` | NAJURIETA — HEBE L. CORCHUELO DE HUBERMAN. |
| 69032 | `voto_disidencia_individual` | VOTO DEL SEÑOR PRESIDENTE DOCTOR DON ENRIQUE SANTIAGO PETRACCHI |
| 69033 | `firma_arrastrada` | Y DEL SEÑOR MINISTRO DOCTOR DON CARLOS S. FAYT |
| 69034 | `no_clasificable` | Considerando: |
| 69035 | `no_clasificable` | 1º) Que los antecedentes de la causa, los fundamentos de la sen- |
| 69036 | `no_clasificable` | tencia apelada y los planteos de las partes han sido objeto de adecua- |
| 69037 | `no_clasificable` | da reseña en el dictamen del señor Procurador General, cuyos térmi- |
| 69038 | `no_clasificable` | nos se dan por reproducidos en razón de brevedad. |
| 69039 | `no_clasificable` | 2º) Que respecto de la inclusión de los intereses en la base regu- |
| 69040 | `no_clasificable` | latoria el recurso extraordinario es inadmisible (art. 280 del Código |
| 69041 | `no_clasificable` | Procesal Civil y Comercial de la Nación). |
| 69042 | `no_clasificable` | 3º) Que, en cambio, los agravios atinentes a las escalas arancela- |
| 69043 | `no_clasificable` | rias suscitan cuestión federal para su consideración por la vía intenta- |
| 69044 | `no_clasificable` | da, pues la cámara –tal como se indica en el dictamen del señor Procu- |
| 69045 | `no_clasificable` | rador General– no se hizo cargo de ninguno de los argumentos sobre |
| 69046 | `no_clasificable` | la base de los cuales se solicitó en el caso la aplicación de la doctrina de |
| 69047 | `no_clasificable` | Fallos: 320:495. Igualmente, prescindió de las disposiciones de la ley |
| 69048 | `no_clasificable` | 24.432, que son de neto carácter procesal y, por tanto, de aplicación |
| 69049 | `no_clasificable` | inmediata conforme a la doctrina de esta Corte (Fallos: 319:2791, disi- |
| 69050 | `firma_arrastrada` | dencia del juez Fayt). |
| 69051 | `no_clasificable` | Por ello, y de conformidad en lo pertinente con lo dictaminado por |
| 69052 | `no_clasificable` | el señor Procurador General se declara procedente la queja y el recur- |
| 69053 | `vacia` |  |
| 69054 | `header_pagina` | 4761 |
| 69055 | `header_pagina` | DE JUSTICIA DE LA NACION |
| 69056 | `header_pagina` | 329 |
| 69057 | `no_clasificable` | so extraordinario interpuestos y se deja sin efecto la sentencia apela- |
| 69058 | `no_clasificable` | da con el alcance indicado. Con costas. Vuelvan los autos al tribunal |
| 69059 | `no_clasificable` | de origen a fin de que, por quien corresponda, se dicte un nuevo fallo |
| 69060 | `no_clasificable` | con arreglo al presente. Agréguese la queja al principal. Notifíquese y |
| 69061 | `no_clasificable` | remítase. |
| 69062 | `firma_arrastrada` | ENRIQUE SANTIAGO PETRACCHI — CARLOS S. FAYT. |
| 69063 | `voto_disidencia_individual` | VOTO DEL SEÑOR MINISTRO |
| 69064 | `firma_arrastrada` | DOCTOR DON JUAN CARLOS MAQUEDA |
| 69065 | `no_clasificable` | Considerando: |
| 69066 | `no_clasificable` | 1º) Que los antecedentes de la causa, los fundamentos de la sen- |
| 69067 | `no_clasificable` | tencia apelada y los planteos de las partes han sido objeto de adecua- |
| 69068 | `no_clasificable` | da reseña en el dictamen del señor Procurador General, cuyos térmi- |
| 69069 | `no_clasificable` | nos se dan por reproducidos en razón de brevedad. |
| 69070 | `no_clasificable` | 2º) Que respecto de la inclusión de los intereses en la base |
| 69071 | `no_clasificable` | regulatoria el recurso extraordinario es inadmisible (art. 280 del Có- |
| 69072 | `no_clasificable` | digo Procesal Civil y Comercial de la Nación). |
| 69073 | `no_clasificable` | 3º) Que, en cambio, los agravios atinentes a las escalas arancela- |
| 69074 | `no_clasificable` | rias suscitan cuestión federal para su consideración por la vía inten- |
| 69075 | `no_clasificable` | tada, pues la cámara prescindió de las disposiciones de la ley 24.432, |
| 69076 | `no_clasificable` | que son de neto carácter procesal y, por tanto, de aplicación inmedia- |
| 69077 | `no_clasificable` | ta conforme a la doctrina de esta Corte (Fallos: 319:1915, disidencia |
| 69078 | `firma_arrastrada` | de los jueces Fayt, Boggiano y Vázquez; 323:1128 –voto del juez |
| 69079 | `firma_arrastrada` | Boggiano–). Ello torna insustancial el tratamiento de los demás |
| 69080 | `no_clasificable` | planteos de la apelante sobre el particular. |
| 69081 | `no_clasificable` | Por ello, habiendo dictaminado el señor Procurador General se |
| 69082 | `no_clasificable` | declara procedente la queja y el recurso extraordinario interpuestos y |
| 69083 | `no_clasificable` | se deja sin efecto la sentencia apelada con el alcance indicado. Con |
| 69084 | `no_clasificable` | costas. Vuelvan los autos al tribunal de origen a fin de que, por quien |
| 69085 | `no_clasificable` | corresponda, se dicte un nuevo fallo con arreglo al presente. Agréguese |
| 69086 | `no_clasificable` | la queja al principal. Notifíquese y remítase. |
| 69087 | `firma_arrastrada` | JUAN CARLOS MAQUEDA. |
| 69088 | `vacia` |  |
| 69089 | `header_pagina` | 4762 |
| 69090 | `header_pagina` | FALLOS DE LA CORTE SUPREMA |


---

## 343_p1679 — Fano, Osvaldo Jorge y Otros s/ Imposición de tortura (art. 144 ter, inc. 1)

**Localización**
- Archivo: `LibroVol343-3.md`
- Páginas catálogo: 1679–1684 | Página consultada: 1684
- Líneas catálogo: 8751–8928 | Línea fin real: 8933 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 8751–8751 | 1 |
| 2 | catch_all | 8752–8752 | 1 |
| 3 | caratula | 8753–8753 | 1 |
| 4 | sumario [1] | 8754–8765 | 12 |
| 5 | sumario [2] | 8766–8779 | 14 |
| 6 | sumario [3] | 8780–8794 | 15 |
| 7 | header_pagina | 8786–8786 | 1 |
| 8 | header_pagina | 8787–8787 | 1 |
| 9 | header_pagina | 8788–8788 | 1 |
| 10 | dictamen | 8795–8877 | 83 |
| 11 | header_pagina | 8824–8824 | 1 |
| 12 | header_pagina | 8825–8825 | 1 |
| 13 | header_pagina | 8826–8826 | 1 |
| 14 | header_pagina | 8868–8868 | 1 |
| 15 | header_pagina | 8869–8869 | 1 |
| 16 | header_pagina | 8870–8870 | 1 |
| 17 | cuerpo_mayoria | 8878–8892 | 15 |
| 18 | firma | 8893–8895 | 3 |
| 19 | catch_all | 8896–8896 | 1 |
| 20 | header_pagina | 8897–8897 | 1 |
| 21 | header_pagina | 8898–8898 | 1 |
| 22 | header_pagina | 8899–8899 | 1 |
| 23 | voto | 8900–8914 | 15 |
| 24 | disidencia | 8915–8933 | 19 |
| 25 | header_pagina | 8929–8929 | 1 |
| 26 | header_pagina | 8930–8930 | 1 |
| 27 | header_pagina | 8931–8931 | 1 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=2 (1.09% del bloque, n=183)

---

### [span 1] header_pagina (8751–8751)
```
343
```

### [span 2] catch_all (8752–8752)
```
FANO, OSVALDO JORGE y Otros s/ Imposición de tortura
```

### [span 3] caratula (8753–8753)
```
FANO, OSVALDO JORGE y Otros s/ Imposición de tortura (art. 144 ter, inc. 1)

```

### [span 4] sumario [1] (8754–8765)
**Header**: RECURSO EXTRAORDINARIO
**Atribución**: -Del dictamen de la Procuración General al que la Corte remite-
```
RECURSO EXTRAORDINARIO
Si bien las cuestiones relativas a la admisibilidad de los recursos or­
dinarios no son, por regla, revisables en esta instancia extraordinaria, 
tal criterio admite excepción cuando la resolución apelada conduce, sin 
fundamentos adecuados, a una restricción sustancial de la vía utilizada 
que afecta el debido proceso, máxime cuando lo decidido por la casa­
ción, al confirmar la libertad provisional de un imputado por un delito de 
lesa humanidad, pone inmediatamente en riesgo los compromisos de 
la Nación y, por lo mismo, configura un caso de gravedad institucional.
-Del dictamen de la Procuración General al que la Corte remite-
-El juez Rosenkrantz, en disidencia, consideró inadmisible el recurso 
(art. 280 CPCCN)-
```

### [span 5] sumario [2] (8766–8779)
**Header**: RECURSO DE CASACION
**Atribución**: -Del dictamen de la Procuración General al que la Corte remite-
```
RECURSO DE CASACION
La sentencia que declaró mal concedido el recurso de casación inter­
puesto por el Ministerio Público contra la confirmación de la libertad 
provisional de un procesado por delitos de lesa humanidad con el ar­
gumento de que la existencia de los presupuestos procesales exigidos 
para la procedencia de la prisión preventiva, debería ser una cuestión 
acreditada y debatida en la instancia en la que se encuentran las actua­
ciones, debe ser revocada, pues el Ministerio Público ya había brindado 
las razones por cuales consideraba que debía detenerse preventivamen­
te al procesado y se venía agraviando precisamente de que esas razones 
no habían sido refutadas, ni ponderadas en las instancias anteriores.
-Del dictamen de la Procuración General al que la Corte remite-
-El juez Rosenkrantz, en disidencia, consideró inadmisible el recurso 
(art. 280 CPCCN)-
```

### [span 6] sumario [3] (8780–8794)
**Header**: RECURSO DE CASACION
**Atribución**: -Del dictamen de la Procuración General al que la Corte remite-
```
RECURSO DE CASACION
El cercenamiento de la vía recursiva es equiparable a sentencia definiti­
va, en tanto si quedara confirmada la libertad provisional del imputado, 
un pedido posterior de detención cautelar, de conformidad con el artícu­
lo 333 del código ritual, debería fundarse en nuevas circunstancias que

343
1680
FALLOS DE LA CORTE SUPREMA
exijan su detención, cuando las ya invocadas, empero, serían suficientes 
para la adopción de esa medida, a pesar de que su consideración, fue 
deliberadamente omitida por los tribunales del caso.
-Del dictamen de la Procuración General al que la Corte remite-
-El juez Rosenkrantz, en disidencia, consideró inadmisible el recurso 
(art. 280 CPCCN)-
```

### [span 7] header_pagina (8786–8786)
```
343
```

### [span 8] header_pagina (8787–8787)
```
1680
```

### [span 9] header_pagina (8788–8788)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 10] dictamen (8795–8877)
```
Dictamen de la Procuración General
Suprema Corte:
-I-
La Sala III de la Cámara Federal de Casación Penal declaró mal 
concedido el recurso de su especialidad interpuesto por este Ministe­
rio Público contra la confirmación de la libertad provisional de Jorge 
Osvaldo S procesado como partícipe necesario de torturas agravadas 
por el carácter de perseguido político del damnificado (fs. 2 y vta.).
Contra esa decisión, el señor Fiscal General dedujo recurso ex­
traordinario (fs. 6/21), cuyo rechazo (fs. 25) motivó la presente queja 
(fs. 26/30 vta.).
-II-
Si bien es cierto que V.E. tiene establecido que las cuestiones re­
lativas a la admisibilidad de los recursos ordinarios no son, por regla, 
revisables en esta instancia extraordinaria (Fallos: 297:52; 302:1134; 
311:926; 313:1045, entre otros), también lo es que tal criterio admite ex­
cepción cuando la resolución apelada conduce, sin fundamentos ade­
cuados, a una restricción sustancial de la vía utilizada que afecta el de­
bido proceso (Fallos: 301:1149; 312:426; 323:1449 y 324:3612). Y creo que 
éste es uno de esos casos de excepción, máxime cuando lo decidido 
por la casación, al confirmar la libertad provisional de un imputado por 
un delito de lesa humanidad, pone inmediatamente en riesgo los com­
promisos de la Nación y, por lo mismo, configura un caso de gravedad 
institucional (Cf. G. 1162, XLIV, “Guevara, Aníbal Alberto s/causa 8222” 
del 8 de febrero de 2011; M. 871, XLVII. “Méndez, Mario Carlos Antonio 
s/causa Nº 13958”, del 16 de octubre de 2012, y sus citas, entre otros).
En efecto, el a quo negó al representante de este Ministerio Públi­
co el acceso a la vía recursiva con el argumento de que “la existencia

1681
DE JUSTICIA DE LA NACIÓN
343
de los presupuestos procesales exigidos para la procedencia de una 
medida cautelar máxima como la prisión preventiva, debería ser una 
cuestión acreditada y debatida en la instancia en la que se encuentran 
las actuaciones” (fs. 2 vta.), por lo que dio a entender que el recurrente 
no había “acreditado” ni “debatido’” esa cuestión oportunamente.
Sin embargo, el agravio planteado en el recurso federal se apoya 
en la premisa opuesta. En efecto, según se afirma en ese recurso, el 
fiscal de instrucción impugnó la decisión de primera instancia con fun­
damento en la gravedad del delito por el que se procesó a S y el ries­
go procesal que, en su opinión, existe en este caso, y posteriormente 
impugnó también la resolución confirmatoria de la cámara federal al 
considerar que ese tribunal había omitido por completo el análisis de 
la cuestión. En particular, se señaló que, en lo referido al riesgo proce­
sal, esas impugnaciones se basaron en el rol que desempeñó S dentro 
de la estructura de represión formada al amparo del último gobierno 
de facto, y las características singulares de la modalidad de comisión 
de los hechos, que permiten sostener, razonablemente, no sólo su vo­
luntad, sino también su capacidad para eludir la acción de la justicia. 
Además, también se recordó que, si bien el procesamiento del impu­
tado fue confirmado, el proceso se encuentra todavía en la etapa de 
instrucción (fs. 8 vta./10 y 14/19 vta.).
Pues bien, de los precedentes citados surge que V.E. consideró 
relevantes esas circunstancias a los fines del juicio prospectivo pre­
visto en el artículo 319 del código ritual, por lo que el a quo, según 
lo advierto, ha expuesto un fundamento aparente que descalifica su 
decisión como acto jurisdiccional válido (Fallos: 303:386; 306: 1395; 
307:1875; 311:512 y 326:3734, entre otros), en tanto este Ministerio Pú­
blico ya había brindado las razones por cuales consideraba que debía 
detenerse preventivamente a Steding y se venía agraviando precisa­
mente de que esas razones no habían sido refutadas, ni ponderadas 
en las instancias anteriores.
Por último, no puedo dejar de añadir que ese cercenamiento de la 
vía recursiva es equiparable a sentencia definitiva para este Ministe­
rio Público, en tanto si quedara confirmada la libertad provisional del 
imputado, un pedido posterior de detención cautelar, de conformidad 
con el artículo 333 del código ritual, debería fundarse en nuevas cir­
cunstancias que exijan su detención, cuando las ya invocadas, empero, 
serían suficientes para la adopción de esa medida, a pesar de que su 
consideración, como se ha dicho, ha sido deliberadamente omitida por 
los tribunales del caso.

343
1682
FALLOS DE LA CORTE SUPREMA
-III-
Por todo lo expuesto, y los demás argumentos desarrollados por 
el señor Fiscal General, mantengo la presente queja y opino que V.E. 
debe declarar procedente el recurso extraordinario y revocar la deci­
sión apelada, a fin de que el a quo, en su carácter de “tribunal inter­
medio”, se pronuncie sobre la cuestión planteada (Fallos: 328:1108). 
Buenos Aires, 10 de julio de 2017. Eduardo Ezequiel Casal.
```

### [span 11] header_pagina (8824–8824)
```
1681
```

### [span 12] header_pagina (8825–8825)
```
DE JUSTICIA DE LA NACIÓN
```

### [span 13] header_pagina (8826–8826)
```
343
```

### [span 14] header_pagina (8868–8868)
```
343
```

### [span 15] header_pagina (8869–8869)
```
1682
```

### [span 16] header_pagina (8870–8870)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 17] cuerpo_mayoria (8878–8892)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 12 de noviembre de 2020.
Vistos los autos: “Recurso de hecho deducido por el Fiscal General 
en la causa Fano, Osvaldo Jorge y otros s/ imposición de tortura (art. 
144 ter, inc. 1)”, para decidir sobre su procedencia.
Considerando:
Que esta Corte comparte y hace suyos los fundamentos y conclu­
siones del señor Procurador Fiscal, a cuyos términos se remite en ra­
zón de brevedad.
Por ello, y lo concordemente dictaminado por el señor Procurador 
Fiscal, el Tribunal resuelve: Hacer lugar a la queja, declarar proceden­
te el recurso extraordinario y dejar sin efecto el fallo apelado. Agré­
guese la queja al principal y vuelvan los autos al Tribunal de origen a 
fin de que, por quien corresponda, se dicte uno nuevo con arreglo a lo 
expresado. Notifíquese y, oportunamente, remítase.
```

### [span 18] firma (8893–8895)
```
Carlos Fernando Rosenkrantz (en disidencia) — Elena I. Highton
de Nolasco — Juan Carlos Maqueda — Ricardo Luis Lorenzetti — 
Horacio Rosatti (según su voto).
```

### [span 19] catch_all (8896–8896)
```

```

### [span 20] header_pagina (8897–8897)
```
1683
```

### [span 21] header_pagina (8898–8898)
```
DE JUSTICIA DE LA NACIÓN
```

### [span 22] header_pagina (8899–8899)
```
343
```

### [span 23] voto (8900–8914)
**Header**: Voto del Señor Ministro Doctor Don Horacio Rosatti
```
Voto del Señor Ministro Doctor Don Horacio Rosatti
Considerando:
Que resulta aplicable al caso mutatis mutandis y en lo pertinente 
lo resuelto por el Tribunal en “Uzcátegui Matheus” (Fallos: 339:408); 
“Moringo Troche, Vicente” (Fallos: 339:1441) y FSM 2378/2010/TO1/1/
RH1 “Olivera, Guillermo Adolfo s/ infracción ley 22.362 (art. 31, inc. d)”, 
sentencia del 8 de noviembre de 2016, a cuyos fundamentos y conclu­
siones corresponde remitir por razones de brevedad.
Por ello, y lo concordemente dictaminado por el señor Procura­
dor Fiscal, se hace lugar a la queja, se declara procedente el recurso 
extraordinario y se deja sin efecto la sentencia apelada. Agréguese la 
queja al principal. Notifíquese y vuelvan los autos al Tribunal de ori­
gen con el fin de que se dicte un nuevo pronunciamiento con arreglo 
a lo expresado.
Horacio Rosatti.
```

### [span 24] disidencia (8915–8933)
**Header**: Disidencia del Señor Presidente Doctor Don Carlos Fernando
```
Disidencia del Señor Presidente Doctor Don Carlos Fernando
Rosenkrantz
Considerando:
Que el recurso extraordinario, cuya denegación origina esta que­
ja, es inadmisible (art. 280 del Código Procesal Civil y Comercial de 
la Nación).
Por ello, se lo desestima. Notifíquese y, previa devolución de los 
autos principales, archívese.
Carlos Fernando Rosenkrantz.
Recurso de queja interpuesto por el Dr. Ricardo Gustavo Wechsler, Fiscal General 
ante la Cámara Federal de Casación Penal, mantenido por el señor Procurador Fis­
cal, Dr. Eduardo Casal.
Tribunal de origen: Sala III, Cámara Federal de Casación Penal.

343
1684
FALLOS DE LA CORTE SUPREMA
Tribunal que intervino con anterioridad: Cámara Federal de Apelaciones de Comodo­
ro Rivadavia, Provincia del Chubut.
```

### [span 25] header_pagina (8929–8929)
```
343
```

### [span 26] header_pagina (8930–8930)
```
1684
```

### [span 27] header_pagina (8931–8931)
```
FALLOS DE LA CORTE SUPREMA
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=8933 | linea_inicio_proximo_caso=8929 | delta=-5
**Alertas**: `solapado_con_proximo`


---

## 329_p1924 — Girón, Julio

**Localización**
- Archivo: `LibroVol329.2.md`
- Páginas catálogo: 1924–1928 | Página consultada: 1928
- Líneas catálogo: 21038–21183 | Línea fin real: 21208 (status_fin=`fin_extendido_pag_compartida`, pista=`caratula_siguiente`)
- Status localización: `ok`

**Resumen de spans**

| # | Tipo | Líneas (abs) | Líneas |
|---|------|--------------|-------:|
| 1 | header_pagina | 21038–21038 | 1 |
| 2 | catch_all | 21039–21051 | 13 |
| 3 | caratula | 21052–21052 | 1 |
| 4 | sumario [1] | 21053–21058 | 6 |
| 5 | sumario [2] | 21059–21073 | 15 |
| 6 | header_pagina | 21065–21065 | 1 |
| 7 | header_pagina | 21066–21066 | 1 |
| 8 | header_pagina | 21067–21067 | 1 |
| 9 | sumario [3] | 21074–21082 | 9 |
| 10 | dictamen | 21083–21196 | 114 |
| 11 | header_pagina | 21103–21103 | 1 |
| 12 | header_pagina | 21104–21104 | 1 |
| 13 | header_pagina | 21105–21105 | 1 |
| 14 | header_pagina | 21143–21143 | 1 |
| 15 | header_pagina | 21144–21144 | 1 |
| 16 | header_pagina | 21145–21145 | 1 |
| 17 | header_pagina | 21182–21182 | 1 |
| 18 | header_pagina | 21183–21183 | 1 |
| 19 | header_pagina | 21184–21184 | 1 |
| 20 | cuerpo_mayoria | 21197–21205 | 9 |
| 21 | firma | 21206–21208 | 3 |

**Invariantes**: cobertura=OK, disjunción=OK, líneas_residuo=13 (7.6% del bloque, n=171)

---

### [span 1] header_pagina (21038–21038)
```
329
```

### [span 2] catch_all (21039–21051)
```
ción por administración fraudulenta”, resuelta el 6 de febrero de 2003).
Buenos Aires, 06 de marzo de 2006. Eduardo Ezequiel Casal.
FALLO DE LA CORTE SUPREMA
Buenos Aires, 23 de mayo de 2006.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que corresponde remitirse en razón de brevedad, se
declara que deberá entender en la causa en la que se originó el presen-
te incidente el Juzgado de Control y Faltas de Río Cuarto, Provincia
de Córdoba, al que se le remitirá. Hágase saber al Juzgado Nacional
en lo Criminal de Instrucción Nº 26.
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — E. RAÚL ZAFFARONI — CARMEN M. ARGIBAY.
```

### [span 3] caratula (21052–21052)
```
JULIO GIRON
```

### [span 4] sumario [1] (21053–21058)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Inhibitoria: plantea-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Inhibitoria: plantea-
miento y trámite.
Si la cámara de apelaciones confirmó la resolución del juez que declinó la com-
petencia, rechazada la atribución es dicha alzada y no el juez quien debe man-
tenerla.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 5] sumario [2] (21059–21073)
**Header**: JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Intervención de la Corte
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Cuestiones de competencia. Intervención de la Corte
Suprema.
No es posible para la Corte Suprema ejercer las atribuciones que le acuerda el
art. 24, inc. 7º, del decreto ley 1285/58, si los escasos elementos incorporados al
incidente no resultan suficientes para conocer con la certeza necesaria los hechos

1925
DE JUSTICIA DE LA NACION
329
que motivaron la causa y, consecuentemente, encuadrarlos en la forma escogida
por el juez declinante, y formar fundado criterio acerca del lugar de su comisión,
para finalmente discernir el tribunal al que corresponde investigarlos, máxime
cuando ante la multiplicidad de circunstancias que comprenden, podría existir
más de una calificación posible.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 6] header_pagina (21065–21065)
```
1925
```

### [span 7] header_pagina (21066–21066)
```
DE JUSTICIA DE LA NACION
```

### [span 8] header_pagina (21067–21067)
```
329
```

### [span 9] sumario [3] (21074–21082)
**Header**: JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
**Atribución**: –Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```
JURISDICCION Y COMPETENCIA: Competencia ordinaria. Por la materia. Cuestio-
nes penales. Prevención en la causa.
Corresponde al juez nacional, que previno y a cuyos estrados acudió la denun-
ciante a hacer valer sus derechos, incorporar los elementos necesarios para darle
precisión a los sucesos y las calificaciones que le pueden ser atribuidas, pues sólo
en relación con un delito concreto es que cabe pronunciarse acerca del lugar de
su comisión y respecto del juez a quien compete investigarlo y juzgarlo, sin per-
juicio de lo que resulte ulteriormente.
–Del dictamen de la Procuración General, al que remitió la Corte Suprema–.
```

### [span 10] dictamen (21083–21196)
```
DICTAMEN DE LA PROCURACIÓN GENERAL
Suprema Corte:
Entre el Juzgado Nacional en lo Criminal de Instrucción Nº 21, y
el Juzgado de Garantías Nº 1 del departamento judicial de Quilmes,
Provincia de Buenos Aires, se suscitó la presente contienda negativa
de competencia, con motivo de la querella promovida por Silvina Dolo-
res Portela.
En ella refiere que en el mes de diciembre de 2003 inició un juicio
de divorcio contra su cónyuge Julio Girón –en trámite ante el Tribu-
nal de Familia Nº 2 del departamento judicial de Quilmes, Provincia
de Buenos Aires– donde también se encuentran radicados los autos
“Portela, Silvina Dolores c/ Girón, Julio s/ separación de bienes –medi-
das cautelares”– en los que la contadora Gabriela Noemí Fernández
fue designada judicialmente como veedora, recaudadora y adminis-
tradora de los bienes de la sociedad conyugal.
Dice que con fecha 21 de febrero de 2005, esa profesional le entre-
gó una fotocopia de un instrumento titulado “Cede, vende y transfie-
re”, de donde se desprendería su consentimiento expreso para la ena-
jenación de las acciones que su cónyuge posee en “Austral Médica S.A.”

1926
FALLOS DE LA CORTE SUPREMA
329
y “J. Girón y Cía. S.A.”, que habría sido suscripto el 15 de diciembre de
2003, y sus rúbricas certificadas por el escribano Eduardo O. Bromberg.
Manifiesta a su vez, que ese documento sería falso pues no estuvo
presente el día de su otorgamiento, ni le pertenecen las firmas que lo
suscriben. Además, se trataría de una maniobra pergeñada por Girón,
algunos familiares y otras personas, con el objeto de desapoderarla de
su parte en esas razones sociales.
Señala también que tomó conocimiento que el notario habría falle-
cido antes de la instrumentación de la cesión, y que los números del
libro y acta donde se anotara la certificación de la firma que le habrían
falsificado, no se correspondían con su fecha.
El juez nacional declinó su competencia a favor de la justicia local,
al entender que los delitos se habrían consumado al presentarse el
documento falsificado en Quilmes, donde tramita el divorcio (fs. 53/56
y 97/100).
El magistrado local, por su parte, rechazó tal atribución con fun-
damento en que no se hallaba debidamente acreditada la falsedad del
documento, ni tampoco se habían individualizado fehacientemente los
hechos y sus calificaciones legales (fs. 152/155).
Advierto que la cuestión no ha sido correctamente trabada pues
tiene establecido la Corte que si, tal como ocurrió en el caso, la cámara
de apelaciones confirmó la resolución del juez que declinó la compe-
tencia (fs. 130), rechazada la atribución es dicha alzada y no el juez
quien debe mantenerla (Fallos: 311:1388 y 312:1624).
Más allá de ese defecto formal, considero que no es posible para el
Tribunal ejercer las atribuciones que le acuerda el artículo 24, inciso
7º, del decreto ley 1285/58, y aplicar al caso la doctrina de Fallos:
317:1332 y 319:916, y Competencia 864 L. XXXVI “López Guillermo y
Otros s/ estafa Procesal”, resuelta el 10 de octubre de 2000, pues los
escasos elementos incorporados al incidente no resultan suficientes
para conocer con la certeza necesaria los hechos que motivaron esta
causa (Competencia Nº 452, L. XXXVIII in re “Alcaraz, Martín Bernabé
s/ amenazas, encubrimiento”, resuelta el 13 de mayo de 2003) y, con-
secuentemente, encuadrarlos en la forma escogida por el juez decli-
nante, y formar fundado criterio acerca del lugar de su comisión, para
finalmente discernir el tribunal al que corresponde investigarlos (Fa-

1927
DE JUSTICIA DE LA NACION
329
llos: 303:634; 304:949 y 308:275) máxime cuando ante la multiplici-
dad de circunstancias que comprenden, podría existir más de una ca-
lificación posible (Fallos: 328:3969).
En tal sentido, creo conveniente señalar que si bien en Quilmes
tramitarían los juicios que atañen al divorcio y separación de bienes
de la querellante, debe repararse en que, a la luz de lo manifestado a
fs. 17 vta., no podría afirmarse con certeza que el original de la su-
puesta cesión fraudulenta haya sido incorporado en ese proceso pues,
según los dichos de la denunciante se encontraría en poder de la
contadora de Girón –Cecilia Prieto– en tanto que la administradora
judicial Gabriela Noemí Fernández, sólo habría aportado al juicio una
copia certificada, sin que ninguna de ellas haya sido aún interrogada
al respecto.
Por otra parte, tampoco se han incorporado las copias de ninguno
de los expedientes radicados ante el Juzgado de Familia Nº 2 de
Quilmes.
Además, tal como lo manifiesta la parte querellante en su escrito
de apelación obrante a fs. 72/73, el magistrado declinante todavía no
ha orientado la pesquisa con el objeto de precisar, con el grado de cer-
teza que esta etapa procesal requiere, la naturaleza de la falsedad del
instrumento de cesión cuestionado.
En tal sentido cabe destacar que si bien –como acertadamente lo
asevera la juez provincial a fs. 152– el escribano Bromberg habría es-
tado con vida en la época de la certificación de firmas del documento
incriminado, pues falleció un año después (vid. fs. 23 y 36), habría sido
víctima de la sustracción de diverso material de empleo notarial, se-
gún la versión de la denunciante (fs. 7).
A ello se agrega que tampoco se ha llevado a cabo medida alguna
tendiente a corroborar los extremos indicados por Silvina Dolores
Portela a fs. 5 de su escrito inicial, relativos a la ausencia de congruencia
entre los números del libro de actas donde –presuntamente– se docu-
mentaran esas certificaciones, y la fecha en que realmente se habrían
efectuado.
En esas condiciones, opino que corresponde al Juzgado Nacional
en lo Criminal de Instrucción Nº 21, que previno (Fallos: 311:67;

1928
FALLOS DE LA CORTE SUPREMA
329
317:486 y 319:753, entre otros) y a cuyos estrados concurrió la denun-
ciante a hacer valer sus derechos (Fallos: 291:272; 293:405; 311:487 y
Competencia Nº 1818 L. XXXVII in re “Gómez, Lucrecia Ileana s/ de-
nuncia”, resuelta el 13 de noviembre de 2001) incorporar los elemen-
tos necesarios para darle precisión a los sucesos y las calificaciones
que le pueden ser atribuidas, pues sólo en relación con un delito con-
creto es que cabe pronunciarse acerca del lugar de su comisión y res-
pecto del juez a quien compete investigarlo y juzgarlo (Fallos: 308:275,
315:312, 323:171 y Competencia Nº 457, L. XXXVIII, in re “Clerc,
Cayetano Pedro s/ supresión de estado civil y falsedad ideológica”, re-
suelta el 18 de febrero de 2003), sin perjuicio de lo que resulte ulterior-
mente. Buenos Aires, 16 de marzo de 2006. Eduardo Ezequiel Casal.
```

### [span 11] header_pagina (21103–21103)
```
1926
```

### [span 12] header_pagina (21104–21104)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 13] header_pagina (21105–21105)
```
329
```

### [span 14] header_pagina (21143–21143)
```
1927
```

### [span 15] header_pagina (21144–21144)
```
DE JUSTICIA DE LA NACION
```

### [span 16] header_pagina (21145–21145)
```
329
```

### [span 17] header_pagina (21182–21182)
```
1928
```

### [span 18] header_pagina (21183–21183)
```
FALLOS DE LA CORTE SUPREMA
```

### [span 19] header_pagina (21184–21184)
```
329
```

### [span 20] cuerpo_mayoria (21197–21205)
```
FALLO DE LA CORTE SUPREMA
Buenos Aires, 23 de mayo de 2006.
Autos y Vistos:
Por los fundamentos y conclusiones del dictamen del señor Procu-
rador Fiscal a los que cabe remitirse en razón de brevedad, se declara
que deberá entender en la causa en la que se originó el presente inci-
dente, el Juzgado Nacional en lo Criminal de Instrucción Nº 21, al que
se le remitirá. Hágase saber al Juzgado de Garantías Nº 1 del Depar-
tamento Judicial de Quilmes, Provincia de Buenos Aires.
```

### [span 21] firma (21206–21208)
```
ENRIQUE SANTIAGO PETRACCHI — ELENA I. HIGHTON DE NOLASCO — JUAN
CARLOS MAQUEDA — E. RAÚL ZAFFARONI — RICARDO LUIS LORENZETTI —
CARMEN M. ARGIBAY.
```

### Borde inferior (transición al próximo caso)
**Estado**: `solapado_con_proximo` | linea_fin_real=21208 | linea_inicio_proximo_caso=21184 | delta=-25
**Alertas**: `solapado_con_proximo`


---
