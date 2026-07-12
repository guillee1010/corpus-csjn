r"""
CSJN Fallos Parser — etapa central del pipeline corpus-csjn
===========================================================
Consume fallos_localizados.csv + mapa_paginas.csv + corpus/*.md y emite los
5 CSV canonicos del parser: csjn_casos, csjn_casos_textos, csjn_casos_votos,
csjn_casos_zonas, csjn_casos_editorial (ver MAPA.md para el DAG completo).

Version vigente: __version__ (abajo); el changelog por version vive en el
comentario de __version__ y en CHANGELOG.md — este header no lo duplica para
no quedar stale (M53b, H197: estuvo clavado en "v17 beta" 15 versiones).

Uso canonico (desde la raiz del repo; o via scripts/pipeline/correr_pipeline.py):
  python scripts\pipeline\parser.py --localizados output\localizacion\fallos_localizados.csv \
      --mapa output\mapa\mapa_paginas.csv --corpus corpus \
      --output output\parser\csjn_casos.csv
"""

__version__ = "33.0"  # H200: B147/M45 sub-frente D1 (MAJOR) — guards de forma en los tiers exact/prefix de refinar_inicio_por_titulo (los dos tiers guardless, L~2472/2486 pre-fix). Causa raiz H199 (leida sobre 7 .md): falso-match-temprano del token del titulo sobre material del caso PREVIO en la cabeza (cola/dispositivo/disidencia/epilogo). Guards: (i) _es_caratula_v2 = _parece_caratula ∨ conector « c/ »/« s/ » (re.I, fin-de-linea ok) / « V. » (case-sensitive); (ii) rechazo de firma (linea_es_firma_de_juez, calcado H190); (iii) primer-match-CON-forma implicito en el orden del scan. Lo rechazado cae a 5b/Tier4/vistos/catalogo SIN cambio (fall-through medido: re-ancla title-case y Boggiano juez-parte identicos). Espec = poc_b147_d1_v03.py VERBATIM (scripts/diagnostico/H200/): E0/E0'' 5894/5894, FLIP-SET SELLADO 93 casos (base->base 84 / ->t4a 4 / ->catalogo 4 / ->vistos 1), adjudicado H200: clase epilogo-del-previo + clase a (firmas versales) + clase c (caratulas mixtas via conector) + TP v0.1; caidas a catalogo = recuperacion de cabeza propia (2733/583/1789 leidos en dump, ARGUELLO/CAJAL/carat-wrapeada restauradas) con costo de bleed conocido (enfermedad D, sucesor D2); 330_p224 = familia B161 nota-al-pie, no-peor (explica la fecha imposible de B153/H191). RESIDUALES: D1b = ancla en linea 2 de caratula wrapeada, 6 casos (1263/1767/1898/6072/1580/2584), unidad propia; 333_p1401 token-acronimo (D3/B018); los 37 CAT_FORMA_SIN_TOKEN (Melchiori) NO entran (riesgo FP H190). CONTRATO del ciclo: linea_inicio/status_localizacion SOLO en el flip-set {93} (baseline poc_b147_d1_v03.csv); bloque cambia solo ahi (84+5 achican, 4 catalogo CRECEN) -> zonas/wc_* ⊆ flip-set; textos.csv puede cambiar en ⊆{93} (considerando descontaminado) -> CANDADO BLIND obligatorio (build_m20 + git status, FRENAR si la clave n300 aparece modificada); ACOPLE B074: linea_inicio alimenta _li_for_dfr -> linea_fin_real/status_fin de los MISMOS 93 puede moverse (declarado, adjudicar) + vecinos-por-solape (fin_extendido_pag_compartida, patron 330_p2122/H197) adjudicables; votos.csv puede sumar/mover filas ⊆{93} (votos destapados al recuperar cabeza); 0 flips outcome/is_merit/gate/is_originaria fuera de {93}, y dentro solo adjudicables — cualquier flip de decision no adjudicado = FRENAR. Regresion propia: poc_b147_d1_v03 --esperar-version 33.0 post-regolden -> E0 5894/5894 / E0'' mismatch = {93} EXACTOS (la replica unguarded ES v32.1, esperado, no FRENO) / flip-set VACIO sobre los E0''-ok. // H198: M52 perf (MINOR) — prefiltro de literales obligatorios para JUECES_CONOCIDOS (hot spot perfil H196: linea_es_firma_de_juez ~55% del runtime; el perfil midio "~74" patrones, la tabla real tiene 87 — correccion de constancia). Diseño original DEUDA (union de alternacion unica) MUERTO con dato en sandbox: 1.0x en el caso NEGATIVO dominante (re stdlib no optimiza alternaciones grandes — mismo O(87·n) que el loop; el ahorro de overhead solo aparece en positivos, 3.1x, que son minoria). Diseño enmendado: de cada patron del CSV se deriva MECANICAMENTE (arbol re._parser, fallback sre_parse, del MISMO patron — fuente unica, cero drift con la tabla) un LITERAL OBLIGATORIO: secuencia que cualquier match debe contener (garantia por construccion: solo aportan runs LITERAL no-opcionales; BRANCH exige que TODAS las ramas aporten). Helper hay_juez_conocido(texto) = etapa 1 `lit in texto.lower()` (substring en C) -> etapa 2 loop existente INTACTO solo si dispara; patron futuro sin literal >=4 cae a chequeo incondicional (hoy: 0/87). Reemplaza los 6 sitios de EXISTENCIA pura (collect_firma_lines x2, _firma_nucleo, linea_es_firma_de_juez x2, frontera de firma pre-collect); los 3 sitios de EXTRACCION de nombre (parse_firma finditer, detectar_juez_en_voto_header, _firma_residuo_es_prosa sub) NO se tocan (corren por caso o post-match, no por linea). Literal generico unico documentado: «ctor» (Mendez, ningun run limpio en h[ee]ctor/m[ee]ndez) dispara etapa 2 en «Doctor/doctora» — costo de velocidad en esas lineas, no de correccion. Sandbox: equivalencia 0 mismatches (bateria + 4600 fuzz), 3.8-4.1x en negativos. CONTRATO del ciclo (REEL de refactor): sha byte-identico de los 5 CSV — assert golden==produccion del orquestador — o FRENAR; medicion de tiempo pre/post con la metodologia del perfil H196, en disco (no se promete cifra). Regresion propia: poc_m52_literales.py (scripts/diagnostico/H198/) — equivalencia hay_juez_conocido vs loop sobre TODAS las lineas del corpus real + tabla de literales + timing. // H197: B162 fix (MAJOR) — {en_consecuencia, atento_a} salen de RE_DISPOSITIVO_VARIANTES (T1 incondicional) a RE_DISPOSITIVO_VARIANTES_ZONIF_PERF: perf-gated (RE_PERF en cola+wrap) SOLO en el zonificador (detectar_apertura_dispositivo +1 kwarg zonif=False, unico call-site zonif=True = Pasada 1 L~3160); en el RESOLUTOR siguen INCONDICIONALES. Evidencia H197: superficie corpus-wide (poc_b162_superficie v0.2, 4607 matches T1 / 16 variantes): en_consecuencia 1411 matches / 471 anclas de zona / 10 picks de outcome + atento_a 74/30/5 — perfil B067 (huella de zona enorme, rinde de outcome minimo); 497 anclas espurias / 431 casos, hasta 1428 lineas de dispositivo espurio (329_p3235); testigos leidos: 344_p1952 b923 (atento_a wrap, micro-item B162 adjudicado: la clase NO era solo en_consecuencia) y b1586, 344_p2123 b1237/b1596. Constancia madre H041 (BITACORA L4028): el trio {de_conformidad, en_consecuencia, atento_a} ya excluido del Tier 2 mid-line; de_conformidad y demas variantes pesadas QUEDAN incondicionales (342/212 picks legitimos sinPerfL — gate de resolutor MUERTO con dato: 341_p774 revoca correcto con perf wrapeado perfW=1/perfL=0, 330_p2520 «lo que asi se ⏎ resuelve», 329_p2985 «hagase saber» enclitico — 5 extractos leidos). Los dispositivos genuinos PICKEADOS que pierden el ancla de Pasada 1 recuperan la zona via relabel A1 (H194) — red medida: 4 casos a1_fired + 9 ancla==pick sin flip. Flip-set SELLADO (poc_b162_flipset v0.1, replica fiel v31 con relabel A1, candado E0 5703/5703 0 mismatch): 423 casos, 0 flips outcome/por_ello_idx/por_ello_text, transiciones dispositivo->cuerpo/sumario/firma/residuo; 1 flip vecino-por-solape (330_p2122, fin_extendido_pag_compartida: el ancla caida del vecino 330_p2115 vive en las 16 lineas compartidas) adjudicado TP — contrato real: flips en zonas SOLO en {423} ∪ vecinos-por-solape. CONTRATO del ciclo: zonas.csv cambia SOLO en ese set (baseline poc_b162_flipset.csv); wc_* de casos.csv en el set; textos.csv byte-identico ESPERADO -> CANDADO BLIND obligatorio (build_m20 + git status; FRENAR si la clave n300 aparece modificada); votos.csv sin cambio esperado (cuerpo y dispositivo ambos en _ZONAS_FALLO -> lineas_excluir invariante); 0 flips outcome/is_merit/gate/is_originaria — cualquier flip de decision = FRENAR. Re-derivar epilogo (consume zonas) -> partes; recursos/materia sin cambio de fondo esperado. Regresion propia: poc_b162_flipset v0.2 --esperar-version 32.0 -> detecta layout post-fix, E0 5703/5703, flip-set VACIO. Absorbe M53(b): header del modulo reescrito (estaba clavado en «v17 beta», 15 versiones stale); M53(a) RUIDO_FIRMA NO se toca (Gate 2 pendiente). // H196: B159 fix clase B (MAJOR) — RE_DICT_HDR pasa de prefijo-abierto a FORMA-TITULO LAXA (la linea es SOLO el titulo: prefijo verbatim + slot de 1 token para «General» [tolera OCR Geberal 336.1 / Genera 338.1] + cola opcional «de la Nacion» + remate puntuacion/(*)). Causa raiz LEIDA sobre los 7 testigos .md extraidos: 6/7 = FP NARRATIVO — el wrap del OCR deja «dictamen de la/del Procura…» a inicio de linea y re.I lo matcheaba → dictamen_inicio espurio → guarda H052 engulle dispositivo/firma/votos (el «dictamen sin cierre» de la constancia H194 era el sintoma, no la causa). re.I SE CONSERVA: el titulo genuino existe en minuscula (versalitas-OCR 336.1 ×8, tomo hoy excluido pero futuro) → capitalizacion a la H139 DESCARTADA con dato; prev_abierta DESCARTADA (565 titulos genuinos con prev abierta). Calibracion corpus-wide (poc_b159_superficie v0.1): 3804 matches → quedan 3789 / caen 15 (todas narrativas min=1) / 0 perdidas, incl. versalitas y OCR-dañados. Flip-set SELLADO (poc_b159_flipset v0.2, replica fiel v30.0 CON relabel A1, candado E0 5703/5703 0 mismatch): 7 casos = 334_p109, 337_p166, 337_p1006, 339_p662, 340_p691, 344_p1952, 344_p2123; 0 flips outcome / 0 flips por_ello_idx (7/7 medidos). Los otros 8 FP del dump (329_p1638, 338_p1009, 340_p1542, 342_p1735, 344_p2307, 344_p3249, 347_p1944, 348_p763) = NO-OP adjudicado con dato (linea FP cae DENTRO de dictamen genuino; dictamen_inicio exento en Pasada 2) — mina latente desactivada gratis. CONTRATO del ciclo: zonas SOLO en {7} (baseline poc_b159_flipset.csv + layout leido de 344_p1952/344_p2123); considerando_text/textos.csv cambian en ⊆{7} (las lineas destapadas salen de lineas_dictamen) → CANDADO BLIND obligatorio (build_m20 + git status; FRENAR si la clave n300 aparece modificada); votos.csv +filas esperadas ⊆{7} (votos Highton/Maqueda/Lorenzetti recuperados en 344_p1952/2123); is_merit/gate re-derivan de textos → flips ⊆{7} adjudicables, fuera = FRENAR. RADIO fuera del PoC (declarado): linea_fin_real/status_fin pueden moverse en VECINOS de las 15 lineas FP (Pistas 3/4 de fin_real anclaban en el FP como «dictamen del siguiente») → adjudicar por vecindad; cualquier otro flip = FRENAR. RESIDUAL DESTAPADO con constancia: dispositivo sobre-extendido en votos por en_consecuencia T1 argumental SIN guard performativo (344_p1952 L1586 ~360 lineas · 344_p2123 L1237 [wrap en minuscula] y L1596; candidato = perf-gate espejo B067/H194, unidad propia; 344_p1952 L923 ancla sin identificar → leer). CLASE A ENCOLADA (B159-A): dictamen genuino como NOTA AL PIE «(*) Dicho dictamen dice asi» intercalado a pie de pagina, nunca cierra — 6 corpus-wide: 329_p879, 329_p3089, 329_p4032, 332_p1963, 332_p2418 [7mo testigo B159], 334_p419. Regresion propia: poc_b159_flipset --esperar-version 31.0 post-regolden → flip-set VACIO / E0 0 mismatch; poc_b159_superficie post-fix → caen 0. Ciclo: --consciente → adjudicar diff por clases (baseline PoC) → --regolden → re-derivar epilogo→partes → re-sello. // H194: B149 fix A (MAJOR) — el dispositivo se ZONIFICA con la misma evidencia que el outcome. Causa raiz leida: resolver_dispositivo usa la cascada T1→4 (T2 mid-linea, T4 «Asi/el Tribunal resuelve») pero el zonificador (Pasada 1 L3109) anclaba SOLO con detectar_apertura_dispositivo (T1) → outcome resuelto con zona dispositivo ausente. Espec = poc_b149_anclas v0.1 VERBATIM (scripts/diagnostico/H194/, replica de procesar_archivo L3729→3849 con candado E0 5703/5703, 0 mismatch). DOS piezas: (A1) HERENCIA DEL ANCLA en procesar_archivo, post-resolver/pre-extraer_segmentos: si por_ello_idx≠None ∧ zona[idx]==cuerpo, re-etiqueta cuerpo→dispositivo desde idx hasta la primera zona de cierre (firma/voto_separado/epilogo); flip-set SELLADO 25 casos 25/25 TP (poc_b149_a1_flipset.csv; cierre en firma 25/25, rangos 1-11 lineas; incluye testigo historico 329_p2596 y 5 testigos leidos H194); GUARD de alcance excluye los 7 zona=dictamen (dictamen-sin-cierre engulle el fallo, rangos 111-1213 lineas → B159 ENCOLADO: 332_p2418, 334_p109, 337_p1006, 337_p166, 339_p662, 344_p1952, 344_p2123); consumidores previos de _zonas_linea inmunes POR CONSTRUCCION (lineas_dictamen/residuo no tocan cuerpo; _ZONAS_FALLO contiene cuerpo Y dispositivo); textos.csv byte-identico bajo A1 SOLO (fin_cons ya corta en por_ello_idx L1141) — pero los RE-PICKS de A2 mueven por_ello_text/fin_cons → textos.csv cambia en ⊆{17 A2} → CANDADO BLIND obligatorio (build_m20 + git status; FRENAR si la clave n300 aparece modificada). (A2) RE_DISPOSITIVO_VARIANTES_PERF: 2 variantes T1 condicionales-a-performativo (guard RE_PERF fuente unica H130, sobre cola de linea + wrap): en_virtud_perf = B067 (BITACORA:4450, pospuesto sobre 5 hits/1 tomo 60%FP) RESUCITADA con el discriminador que faltaba — 268 matches corpus-wide / 204 en dictamen / perf-gated 16 = 16/16 TP adjudicados (testigo original 348_p443 incluido; 8 son dispositivos de VOTO que A1 no alcanza) + que_de_conf_perf (analogo que_por_ello) — 29 matches / perf-gated 1 = 344_p776 TP. «Por lo tanto» DESCARTADA con constancia (patron RE_ART_117_CN: 640 superficie / H039 70% argumental / rinde 2-3 / borde 341_p250 indecidible; residuales documentados 343_p720, 346_p1068). detectar_apertura_dispositivo +1 arg opcional cola_wrap (precedente H181/H190), peek SOLO en el zonificador (espejo del PoC: linea siguiente stripeada); _cand_estructural/_cand_t3b SIN cambio de firma → en el resolutor las perf-variantes exigen performativo en la MISMA linea (los wrapeados recuperan ZONA, no outcome — residual documentado). Guarda-dictamen H052 intacta = red extra sobre los 204. CONTRATO del ciclo: zonas cambia SOLO en {25 A1} ∪ {17 A2 perf de poc_b149_a2_anclas.csv}; flips de outcome/por_ello_text/is_merit ESPERADOS y adjudicables ⊆ {17 casos A2}: recuperaciones (sin_dispositivo→X) o RE-PICK (T1 ahora ancla la perf-variante antes que T2/T4 — adjudicar contra el CSV); cualquier flip FUERA de {25 A1}∪{17 A2} = FRENAR. Regresion propia: re-correr poc_b149_anclas v0.1 --esperar-version 30.0 → e0_mismatch = 25 EXACTOS (== flip-set A1: la replica del PoC corta en L3849, ANTES del relabel — esperado, no FRENO) + A1 flip-set = 7 (solo dictamen/B159, sobre los E0-ok) + los 17 matches A2-perf con zona_actual=dispositivo. Residual MEDIO-multivoto (~13, dispositivo per-voto con formula no cubierta) documentado en DEUDA. // H193: B148 fix A (MAJOR) — linea_es_firma_de_juez deja de disparar sobre atribuciones editoriales de sumario y cuerpo denso en nombres. Tres guards de consumo LOCAL (RE_HEADER_VOTO_DISIDENCIA y RE_CALIFICADOR INTACTAS: segundo consumidor en frontera L2488 / parse_firma): (i) RE_ATRIBUCION_SUMARIO — prefijo «[-–—(] Disidencia(s)/Voto(s)» + cola «(Disidencia(s)|Voto(s)) [parcial/conjunta] de» (el ^ de RE_HEADER_VOTO_DISIDENCIA no tolera guion/parentesis, causa raiz 1 de H192); (ii) nucleo de firma (_firma_nucleo): strip de parentesis balanceados SIN juez (calificadores fuera de catalogo medidos H193: «según mi voto», «(con) ampliación de fundamentos», «en disiden-cia» con soft-hyphen — sin tocar RE_CALIFICADOR) + corte de fragmentos parenteticos WRAPEADOS (prefijo hasta el «)» colgante / sufijo desde el «(» colgante) — y el match de JUECES_CONOCIDOS debe SOBREVIVIR en el nucleo: si el juez vivia solo dentro del fragmento, la linea es continuacion de atribucion «(Voto del Dr. / Nombre).» y NO firma; (iii) predicado residuo-prosa sobre el nucleo: quitados jueces+calificadores+conectores(don/doña/y/e)+particulas de nombre, prosa en minuscula = NO firma; residuo vacio o forma-de-nombre = SIGUE firma (preserva conjueces desconocidos, clase B153/v27.1; la enumeracion tipo 329_p5317 sobrevive POR DISEÑO -> residuo medido). Espec = poc_b148_flipset v0.3 VERBATIM (scripts/diagnostico/H193/); flip-set SELLADO 3799 lineas / 1303 casos (g1_atribucion 1671 / gU_juez_solo_en_fragmento 1401 / g2_residuo_prosa 727), adjudicado: testigos clase-1 15/15 caen, clase-2 8/9 (5317 por diseño), NO-B148 17/17 TP (atribuciones en bleed/cabeza), hdr_sumario flips 0 (call-site L2029 sin efecto medido), 579+5 firmas reales PRESERVADAS por los cortes de nucleo (clase FRENO v27.0: calificador partido por wrap, continuaciones «cia)—…», «mi voto»/«fundamentos»/soft-hyphen). RADIO (mismo predicado en A001 L1990/2005, header_sumario_guardado L2029, frontera L2488, fin_real/extender/retroceder L2595/2705/2776, zonificar L3019/3329/3412) -> MAJOR: esperada descontaminacion masiva de zonas (clases 1-2, pool 217 + multi-voto), wc_*, considerando_text (textos.csv VA a cambiar -> candado blind: build_m20 + git status, FRENAR si la clave n300 aparece modificada), firma_raw de 346_p965 reparacion TP esperada; flips de votos/n_jueces se adjudican contra dump_b148_tramos + flipset; 0 flips outcome/is_merit/gate/is_originaria — cualquier flip de decision = FRENAR. Regresion propia: poc_b148_flipset --esperar-version 29.0 debe dar flip-set VACIO; re-correr poc_b148_cardinalidad -> el residuo del pool 217 decide la unidad siguiente. // H191: B153 — conjueces en la firma (paneles subcontados). (i) JUECES_CONOCIDOS externalizado a DATO: _meta/jueces/jueces_csjn.csv (patron M46; 56 migradas VERBATIM + 18 nuevas [Moline O'Connor y Bossert titulares historicos en fallos publicados tardiamente 1998-2003; 16 conjueces: Planes, Prack, Enderle, Corchuelo de Huberman, Fernandez Vecino, Rueda, Munne, Recondo, Arribillaga, Uslenghi, Madueno, Niremperger, Fernandez E.L., Fernandez M.B., Tazza, Lugones] + 2 ensanches [Otero (?:luis)? — firma sin LUIS en 329_p1303/1305; Leal de Ibarra (?:mar[ii]al?)? — OCR MARIAL 329_p5261]), loader _cargar_jueces_conocidos fail-fast, compila re.I. PoC poc_b153_conjueces v0.1 (read-only, scripts/diagnostico/H191/): E0 replica==columnas publicadas 0 diffs/5703; flip-set EXACTO 35 casos / +48 jueces / 0 perdidas / 0 flips fuera del pool adjudicado; E1 set-CSV == flip-set medido. is_full_bench flips = 2 ADJUDICADOS: 329_p4178 1->0 (corrige FP: 5 titulares viejos eran 7 con Moline+Bossert) + 330_p224 0->1 (semantica ==5 sobre banco viejo — caso con fecha imposible 2007/panel 1998-2003, flageado). Descartes con constancia: RICARDO LUIS colgado 329_p158/576 = truncamiento upstream de firma_raw (clase v27.0, NO set); HIGTHON 330_p5010 ya contada (patron matchea ELENA I.); ASOCIART/DARIMAR = bleed de epilogo. (ii) columna jueces_desconocidos RE-CONECTADA: era vacia por construccion (conocido=True hardcodeado en extraer_jueces_de_firma + filtro not-conocido en el writer = conjunto vacio; la lista real solo iba al print de consola). Ahora persiste el colector real — instrumento de deteccion de conjueces en tomos futuros; ruido de bleed documentado. RADIO: el set alimenta parse_firma + detectar_juez_en_voto_header + linea_es_firma_de_juez (frontera H190/fin_real/retroceder/extender + firma inversa A001 + B141 peek + votos) -> MAJOR: esperados n_jueces/jueces/conocidos/desconocidos/posiciones/n_titulares/is_full_bench(2)/voting_pattern en ~35 casos + votos.csv +filas + POSIBLE corrimiento de linea_fin_real/zonas donde una firma pura-conjuez ahora es sustantiva para los guards. 0 flips esperados en outcome/is_merit/gate — cualquier flip = FRENAR y adjudicar. Ciclo: --consciente -> adjudicar diff por clases (baseline flipset_b153.csv) -> --regolden -> re-derivar -> re-sello. // H190-b: FRENO del ciclo consciente v27.0 adjudicado y corregido — el retroceso comía el FRAGMENTO FINAL de líneas sustantivas wrapeadas: (a) cierre de firma («…RICARDO LUIS» ⏎ «LORENZETTI.» / «…CARMEN» ⏎ «M. ARGIBAY.»): el apellido solo NO matchea JUECES_CONOCIDOS (patrones nombre+apellido, verificado empírico: linea_es_firma_de_juez("LORENZETTI.")=False) → rotulo_caps → A lo trimeaba → votos -42 filas, 329_p83 n_jueces 6→5 + is_full_bench flip, firma_raw truncada ~34 casos = VIOLACIÓN del contrato detectada en el diff consciente (golden/manifest intactos, fix-forward); (b) wrap de lista de partes del epílogo (331_p2099 «S.A. – AGROPERFO S.A.»). Clase medida en el baseline PoC v0.3: 34 casos (27 «M. ARGIBAY.» + 3 «LORENZETTI.» + conjueces/varios). GUARD v27.1 (_es_continuacion_wrap): rotulo_caps corto que CIERRA en «.» inmediatamente después (sin vacías) de una línea sustantiva ABIERTA (sin «.») = continuación del wrap → sustantivo, no se recorta. General: cubre firma-fragmento Y epílogo-wrap; arregla GRATIS el residual 329_p4506 («LORENZETTI — EMILIO L. FERNÁNDEZ.» cae en la clase, sin conocer al conjuez — B153 sigue abierto para firmas conjuez completas). Los recortes buenos NO se tocan: rótulos ajenos siguen a líneas CERRADAS (control 333_p380 «…Misiones.» → «DEFENSA DE LA COMPETENCIA.» se sigue recortando) y los banners nunca cierran en «.» (capa 1197 intacta). Refactor: _clase_linea_frontera pasa a (lines, idx) con _clase_linea_frontera_base line-only. PoC actualizado en paridad (v0.4). Anclas 8/8 + T4/T5/T6 sintéticos re-verificados. Re-correr ciclo consciente COMPLETO desde cero. // H190: B147-1A CERRADO — retroceso de frontera fina (retroceder_frontera) sobre los fines de Pistas 1/3/4 de detectar_fin_real (Pista 2 editorial / firma_actual / fallback_catalogo INTACTOS: mecanismos distintos, 1C/B019/B012). Mecanismo adjudicado sobre 8 testigos .md que CORRIGE el modelo H188: Pista 1 corta en carátula-1 pero deja colgando el material PRE-carátula del siguiente (rótulos temáticos, banners, apertura de dictamen, strays «NOVIEMBRE»/«Considerando:»); Pistas 3/4 anclan en el DICTAMEN del siguiente y absorben carátula+rótulo+SUMARIO ENTERO — el perfil 3/4 existe porque Pista 1 falla por token corto («Lumi» len 4 < umbral 5 L2538) o divergencia OCR índice/cuerpo («Hurting»/«HURTIG» 334_p405) → el retroceso es INDEPENDIENTE del token. Etapa A: recorte hacia atrás de líneas no-sustantivas (vacía · banner RE_PAGE_HEADER · rótulo caps _parece_caratula · apertura-dictamen · «Suprema Corte:» · atribución «–Del…–» con nota (*) · «Considerando:» suelto); etapa B: búsqueda acotada (W=25) de carátula POR FORMA con prosa intermedia → corta en carátula-1 y re-aplica A. GUARDS (adjudicación del flip-set poc v0.2→v0.3 en disco): linea_es_firma_de_juez + RE_HEADER_VOTO_DISIDENCIA (REUSO) = sustantivo en A / stop y no-candidato en B — la firma en VERSALES de los tomos viejos matchea _parece_caratula y sin guard B amputaba firma+disidencias+epílogo (958 FP de B + 420 de A eliminados, testigos 329_p2547/330_p2964/330_p5032); el scan de B FRENA en la primera firma; candidato con token del nombre PROPIO = apéndice 1C → no corta (3 candidatos flageados: 339_p1648/340_p1993/345_p1138). Desborde _RETRO_MAX_TRIM=60 → no-op conservador (0 observados; difiere del PoC que recortaba igual — clase vacía). Flip-set medido y adjudicado (poc_b147_1a_retroceso v0.3, scripts/diagnostico/H190/): 1866 recortes / 5542 en alcance = 1197 solo-banner + 669 con contenido ajeno sustantivo; B=91, 91/91 TP (79 auto-match nombre del vecino + 12 leídos: rótulos duplicados y solapes con vecinos sumario_con_link); diag-1A de H188: 47/47 con bleed real cubiertos + 3 FP del diag verificados en .md (345_p683/330_p2892/330_p3126: frontera perfecta, carátula del siguiente en lfr+1) + 1 editorial fuera de alcance; anclas 5/5 (339_p399→15054 · 332_p2425→15918 · 333_p380→14697 · 338_p176→7410 [B, Lumi] · 334_p398→15797 [B, Hurtig]); 0 fantasmas nuevos. Corrección de cardinalidad: 1A real = 1866, no 51 (bandera-1 de H188 solo veía el bleed que caía en zona epilogo). RESIDUALES documentados: firma-conjuez no reconocida 329_p4506 «EMILIO L. FERNÁNDEZ» (→ B153, mismo mecanismo Lozano/Rodríguez Basavilbaso) · under-trim carátula mixta wrapeada 345_p1219 «N.N. s/ …» deja ≤1 línea (B ancla en la 2ª línea caps). Regresión propia del fix: re-correr el PoC POST-fix sobre el casos.csv nuevo debe dar recorte 0 en los 1866 y 0 filas nuevas (baseline diffeable scripts/diagnostico/H190/poc_b147_1a_out.csv, orden caso_id). Contrato del ciclo: cambios confinados a linea_fin_real/status_fin + zonas.csv (bordes/cardinalidad) + wc_* de casos.csv + sidecars epilogo/partes (descontaminación esperada: p.ej. 338_p176 epilogo wc 307→~130 al soltar el sumario de Lumi; 332/333 pierden segmentos dictamen/sumario espurios del siguiente); 0 flips en outcome/is_merit/gate/is_originaria — cualquier flip = FRENAR y revertir. MAJOR (mueve linea_fin_real en ~1866 casos → firma de detectar_fin_real +1 arg opcional tokens_nombre_propio, 1 call-site). Ciclo: --consciente → adjudicar diff por clases (baseline PoC) → --regolden → re-derivar epilogo→partes → re-sello. // H184-b: B117 F2 corrección post-dump — la rama «Causa» de RE_EPILOGO_MARKER vuelve a ':' PEGADO ((?i:^Causa\s*:), verbatim RE_DATOS_PARTES vieja) y sale de la lista de rótulos-[^:\n]*:. Causa raíz: la forma relajada Causa[^:\n]*: re.I matcheaba narrativa «causa “Casal” (Fallos: …» — el ':' lo regalaba la cita de Fallos. Clase FUERA del universo F1 (la regex vieja exigía ':' adyacente, esas líneas nunca fueron markers): 103 de los 104 markers nuevos del dump H184 (87 líneas únicas, 92 casos), TODAS narrativa adjudicada por lectura. 0 pérdidas del universo F1 por construcción (todo marker «Causa» viejo tenía ':' pegado) — verificado en sandbox: 87/87 mueren, 21 controles (34 testigos-clase + Causa: genuino x3) sin diff. FP RESIDUAL ACEPTADO Y DOCUMENTADO: 340_p437 «Queja contra el Gobierno de Argentina presentada por el Sindicato» (cita de queja OIT caso 2240/informe 332 en el cuerpo, leída en .md; entra por gram_v2 presentad+por; discriminador candidato «contra» pre-verbo = sub-clase M44, PoC propio, NO parche ad-hoc). Regresión: poc superficie post-26.1 debe dar markers = 9882 + 1 (el FP Queja). // H184: B117 F2 — RE_EPILOGO_MARKER nueva = escalera v2 de poc_b117_superficie v0.2 CONSOLIDADA (unión verbatim de los 6 cuerpos: v1-recurso case-sensitive + v1-rótulos-':' re.I escopeado + case_scope + gram_v2 [verbos inte\w*rpu\w+/deducid/presentad/articulad/fundad · \bpor\b libre · sin-por artículo/Nombre] + recurso_dp ^Recurso[^:\n]{0,60}: + rotulo_relaj). Reemplaza a RE_DATOS_PARTES SOLO en el sitio del epilogo_marker (Pasada 1 de zonificar_bloque); RE_DATOS_PARTES INTACTA para A001 (búsqueda inversa de firma, PoC H045). Guard del marker sin cambio. Evidencia F1 adjudicada en H183 (11.201 markers / 5697 fallos, A0 5697/5697, regresión out300 299/299): cae 1319 / queda 9882, recupera EXACTAMENTE los 34 pies adjudicados, 0 readmisiones espurias, FN corpus-wide = 3 (clase verbo-partido → M44); 920 casos recuperan cuerpo (86 zona entera espuria + 834 parcial); 67 voces caps de sumario dejan de flipear a epilogo. Regresión del fix: poc v0.2 POST-fix debe dar queda 9882 exactos y los 34 testigos con marker. Contrato del ciclo: cambios confinados a zonas.csv (bordes) + wc_considerando/wc_cuerpo/wc_epilogo/wc_residuo de casos.csv + epilogo.csv + partes.csv; 0 flips en is_merit/gate/is_originaria (M43 no se contamina) — cualquier flip de decisión/outcome/mérito = FRENAR y revertir. MAJOR (mueve bordes de zona en ~920 casos → wc_* y sidecars epilogo/partes). Ciclo: --consciente → dump-adjudicación (patrón dump_diff_h181c) → --regolden → re-derivar epilogo→partes → re-sello. // H181 (unidad C): M21 FASE 3 — skip de RE_PAGE_HEADER (línea-sola: frase pelada o número 2-6 dígitos) dentro del chunk de _barrer SIN contar presupuesto, simétrico al skip de vacías de Fase 1. Cierra la clase banner-partido-en-N-líneas que la terna-substring de Fase 2 no cubre (encolados: 333_p1951, 343_p2080, 329_p59 [H171/H174] + los 4 truncados del costo del paso 3: 329_p4634, 330_p4129, 347_p474, 348_p355). Detector RE_PAGE_HEADER reusado (0 regex nueva); el componente de banner NO entra al chunk (higiene del pe persistido, además de liberar presupuesto). FUERA DE ALCANCE declarado: 330_p563 (dispositivo >6 líneas sin banner; el presupuesto de 6 NO se toca). MAJOR (cambia _barrer → por_ello_text/outcome y derivados denormalizados; precedente Fase 1 = v19.0). Medición = ciclo --consciente corpus-wide con adjudicación del diff por clases ANTES de --regolden (un cambio de _barrer no admite PoC read-only; camino H126). // H181: B135(c) CERRADO — señal 6 COMPUESTA en es_originaria: case_name demanda-contra-Estado/Provincia (RE_CN_DEMANDA_ESTADO ensanchada con la forma invertida «c/ <Nombre>, Provincia de», deja de ser huérfana) ∧ _orig_pelada_con_guards (reusada intacta, 4 guards H172) sobre la ventana RESULTA (_ventana_resulta: apertura RE_VISTOS → primer RE_CONSIDERANDO, verbatim de poc_b135c v0.1). NUNCA case_name solo (≈11% H156). Flip-set medido en disco y adjudicado por lectura caso a caso: 6 = 6 TP, 0 FP (329_p3168 López Casanegra, 329_p3403 Ferrari, 340_p1025 Fotógrafos Iguazú, 342_p917 Barrick, 344_p3476 Coihue, 348_p1686 Equística — los 6 con declaración de competencia en el propio expediente). Pool case_name-compuesto 326 → corroboración deja 6 (precisión de la compuesta demostrada). Ripple: is_originaria 589→595 · is_merit 2935→2941 (+6 vía rama originaria del gate, punto único; incluye Equística, recuperada por clasificador_disposicion v1.16 — ensanche «condenar al?», MISMO CICLO, ver su changelog; poc_condenar_al v0.1: flip-set del ensanche = 1 = el testigo, 0 pérdidas, 0 FP-costas. ACOPLE: el sello de este ciclo asume clasificador >= 1.16) · tribunal_origen_status→originaria en las 6 (Coihue corrige apelado_detectado falso). Ruta D (dispositivo) evaluada y DESCARTADA: testigo único 348_p473 = fila FANTASMA (rango [18027,18040] ⊂ 348_p461 La Rioja [17575,18046], ya orig=1/merit=1; nombre de catálogo de Hotesur; gap 18047-18076 = candidato al Hotesur real — familia B012/B045, constancia propia). Corrección de constancia H178: los «3 costos autorreparables B135c» eran 2 reales + 1 espurio. MINOR (recall acotado y medido; sin cambio de semántica ni schema; firma de es_originaria +1 arg opcional bloque). Re-golden consciente + re-derivar + re-sellar vía correr_pipeline. // H178: PASO 3 M39 — is_merit DERIVADO del gate del clasificador como FUENTE ÚNICA (patrón B136 extendido corpus-wide): import disposicion+es_revision_fondo (llamada idéntica a derivar_recursos v0.6), retiro del branch originaria y de MERIT_OUTCOMES; GATEKEEP_OUTCOMES removido (código muerto preexistente, 0 usos — hallazgo H178). Flip-set exacto verificado por PoC bimodal (poc_paso3_m39 v0.2 [CLEAN] sandbox+disco): 227 = 151 (1→0) + 76 (0→1) == divergencia M39 publicada, ids exactos; identidad de insumos demostrada (A1: gate recomputado 0 diffs vs columna publicada → el round-trip CSV es neutro). Absorbe por construcción M2A/M3/M4 + 9 expuestos B140b + 13 expuestos B143 + 9 aciertos-del-gate H172/H176. COSTOS ACEPTADOS documentados (~22 flips con valor conocido-equivocado o transitorio, todos con unidad sucesora): 9 FN-B139a 1→0 (332_p731, 340_p411, 341_p1924, 341_p1075, 343_p28, 338_p234, 331_p2628, 337_p1042, 332_p2797) · 4 residuales B138 0→1 (330_p1205, 330_p4891, 331_p2621, 348_p747 — tomos completados H178) · 3 originarias B135(c) 1→0 (329_p3403 Ferrari, 344_p3476, 348_p473 — fondo real, flip por miss de is_originaria; AUTORREPARABLES al cerrar B135c vía la rama originaria del gate) · 1 B139b (331_p100, ídem al cerrar B139b) · 4 truncados M21 (329_p4634, 330_p4129, 347_p474, 348_p355 — el pe truncado esconde el verbo al gate; se recuperan con M21 F3) · 1 ADC/329_p5261 0→1 (FP conocido B140a). Ancla no-flip: 330_p399 queda is_merit=1. Métricas: is_merit 3010→2935 (== gate=si) · divergencia M39 = 0 POR CONSTRUCCIÓN → RETIRO del instrumento D1 (límite documentado: las clases coincide-en-error —B142, B143 pre-fix— son lo que la divergencia nunca vio; sucesor: M43 re-κ del eje unificado). Ripple: votos 1078 filas is_merit_decision denormalizado + tipo_voto acotado (cota superior 15 pierden D-por-fallback / 2 ganan; exacto en check_regresion) · recursos.csv byte-idéntico ESPERADO (el gate no consume is_merit — verificar P1b del PoC POST) · clave n300 NO byte-idéntica (8 filas: 330_p1907, 330_p4592, 331_p2621, 332_p2625, 332_p2797, 338_p40, 344_p3394, 348_p92) → el candado byte-idéntico se retira CON D1; blind 0,930 midió el eje viejo, la re-validación del eje unificado es M43. La copia local de nulidad_concesion (pre-cascada B119, regex angosta pre-B140b) QUEDA: moldea outcome (eje legacy), ya no contamina is_merit; dedup → D3/M40. + Corrección de constancia: el schema real de csjn_casos.csv es 39 columnas (las menciones «40 columnas» en las entradas H148/H169 de abajo eran erróneas; se dejan intactas como registro histórico). MAJOR (semántica del eje de mérito corpus-wide). Re-golden consciente + re-derivar + re-sellar + M43 calzada como próxima unidad. // H174: B141 — falso terminador del chunk de _barrer: inicial anonimizada («...sus hijos E.») o numeral romano («se resuelve: I.») a fin de línea partía el dispositivo y escondía el verbo de fondo. RE_FALSO_TERMINADOR + peek _proxima_linea_es_firma (reusa linea_es_firma_de_juez, fuente única): si la línea del chunk termina en falso terminador y lo próximo con contenido NO es firma, el chunk sigue (dentro del presupuesto de 6); si es firma, el fin era genuino y corta igual (332_p238 «M. E. A. V.», 340_p397 «Sala B.»). Familia de 16 adjudicada contra texto real (14 truncados reales + 2 FP de firma): 12 recuperan la cola del dispositivo, 2 genuinos byte-idénticos, 2 residuales clase M21-banner-partido-en-3-líneas NO tocados acá (333_p1951, 343_p2080 — encolados con 329_p4634/330_p4129/329_p59 de H171). Mérito recuperado: is_merit 0→1 en 329_p3894 y 341_p1148 (vía es_de_fondo, ambas capas por construcción). ACOPLE: requiere clasificador_disposicion >= v1.11 (guard in limine, integrado H174) para no fabricar FP en 330_p3777 al destapar «Rechazar in limine la demanda». Nota: 343_p2080 gana cola de banner que norm() enmascara downstream (terna v1.05), efecto 0 en clasificadores. MAJOR (por_ello_text en ≤13 casos + outcome/is_merit derivados + denormalización en votos). Re-golden consciente + re-derivar recursos + re-sellar + re-medir divergencia M39. + Fix infra (H174): stdout/stderr con errors="replace" — el progreso imprime Unicode (→) que a consola Windows sale UTF-8 (PEP 528) pero bajo redirección (> log, | tee) caía a cp1252 y el charmap abortaba la corrida; reproducido sobre v23.1 intacta (defecto latente en todas las versiones, solo dispara con stdout redirigido). Ahora el glifo degrada a '?' y la corrida nunca muere por un print, en cualquier entorno, sin PYTHONUTF8. Misma clase que el fix LF de H111 (salida independiente del entorno). // H172: B135 (a)+(b) PARCIAL — es_originaria: (b) mask de RE_RUNNING_HEAD ANTES de _unhyphenate (el banner intercalado partía la señal y el des-guionado la unía al número de página; miss corpus-wide medido = 1, 337_p234 Credicoop); (a) 5ª señal «competencia originaria» PELADA con guards por-match (local/apelada/precedente/provincial W=120), calibrada por PoC en disco (poc_b135_flips v0.1→v0.3, anclas A1-A6 [OK]): flip-set 43 = 39 TP + 4 FP-F5 aceptados y documentados (349_p163, 347_p2146, 347_p2286, 334_p1842 — historia procesal narrada, 0,07%). M1 corregido a 14 (337_p901=Duarte, FP por cita CIDH «competencia originaria local»; gemelo 342_p2389). Ensanche de RE_ART_117_CN medido y RECHAZADO (marginal 0 TP / 1 FP: 348_p841). Las 4 señales existentes y el criterio-amplio SIN cambio; sub-causa (c) señal compuesta PENDIENTE. Ripple esperado: is_originaria 546→589 → is_merit vía es_de_fondo (B136) en el subset de fondo + denormalización en votos — MEDIR con verificar_b135_post. MINOR (recall acotado y medido; sin cambio de semántica ni schema). Re-golden consciente + re-derivar recursos + re-sellar. // H169: B136 — is_merit de la ORIGINARIA ya NO es hard-0 (B119 #1 revertido en parte): la originaria resuelve la demanda directamente y su mérito lo detecta es_de_fondo (clasificador_disposicion v1.10, importado en cabecera), el MISMO detector que es_revision_fondo del deriver → is_merit_decision y es_revision_fondo coinciden en la originaria (133 de fondo). Verbo apelativo (outcome ∈ MERIT_OUTCOMES) sigue rigiendo la no-originaria SIN cambio. Medido en disco: is_merit 2870→3003 (+133 originarias 0→1), 0 no-originarias tocadas; ripple a la denormalización de is_merit en csjn_casos_votos + señal de clasificar_tipo_voto. MAJOR (semántica del eje de mérito para toda la clase originaria + nueva dependencia de módulo). Re-golden consciente + re-derivar recursos + re-sellar. NO cambia el schema (40 columnas). // H148: M26 paso 3 — REMOVIDA la columna causa_inadmisibilidad (re-cableada al deriver: clasificador_causa.py, gate=admisibilidad). Borrados OUTCOME_A_CAUSA/OUTCOMES_GATE_GENERICO/RE_CAUSA_*/clasificar_causa_inadmisibilidad. RE_280_*/RE_ACORDADA_4_*/_unhyphenate QUEDAN (los usa classify_outcome). El voto NO denormaliza causa → csjn_casos_votos.csv intacto. MAJOR (cambia el schema de csjn_casos.csv: 40 columnas, sin causa). Re-golden consciente + re-sello. // H139: RE_RUNNING_HEAD case-sensitive (saca re.I) — el banner es MAYÚSCULAS; "Corte Suprema" en mixta del cuerpo NO es header. Verificado: por_ello 467/467 mayúsculas → no-op sobre el output (check_regresion [CLEAN] esperado). Base para limpiar el banner del considerando (materia, frente aparte). MINOR. // H137: M21 Fase 2 — RE_RUNNING_HEAD enmascarado en _barrer (saca el banner editorial del por_ello + libera presupuesto del chunk → recupera el dispositivo truncado). MAJOR (afecta outcome/por_ello_text/considerando indirecto/votos denormalizados). 463 banners / 0 FP verificado sobre el texto del sidecar; el efecto de recuperación-por-presupuesto y la regresión se validan en disco re-corriendo el parser (regression→golden→re-sello). PROPUESTA, NO cerrado. // H131: B019 CERRADO — fallback firma_actual de detectar_fin_real ahora extiende la firma wrapeada (extender_firma): cuando la firma de la Corte parte en >1 línea del OCR ("…— Carlos\nS. Fayt — …"), el pick bidireccional anclaba en la 1ª línea-firma y dejaba la continuación afuera del bloque → firma/votos truncados (23 casos, todos pista_fin=firma_actual). extender_firma avanza desde la línea elegida por linea_es_firma_de_juez, frena en la 1ª no-firma (epílogo "Recurso … interpuesto por …"), tolera 1 vacía (espejo collect_firma_lines), respeta limite_adelante (no invade el fallo siguiente). PoC en disco (poc_b019_extender_firma_actual): +56 votos / 23 casos / 0 sobre-extensión / 92 firma-completa intactos. Corolario: la zona firma de csjn_casos_zonas crece 1-2 líneas en esos 23 (la zonificación es downstream de linea_fin_real, así que heredaba el truncado). MINOR: solo extiende la salida del fallback firma_actual; NO altera el pick bidireccional B045/H069. Residual: 338_p1060 (línea "Maqueda (según su voto)." de 1 juez no la agarra el predicado angosto = deuda menor); consolidación vía divisor de zonas = camino elegante futuro (mover zonificación upstream del borde). // H130: B124 CERRADO — regla P en _barrer: entre candidatos-con-firma de la ventana del dispositivo devuelve el PRIMER performativo (RE_PERF v2); fallback al primer-con-firma (= comportamiento v19) si ninguno lo es. RE_PERF v2 = "se <verbo>" (clítico opc., H129) | "(el Tribunal|esta Corte|la Corte) resuelve" | "resuelve:" — extiende v1 a performativos de mayoría SIN "se", auditados en disco (audit_resuelve_sin_se, 5890 casos: "el Tribunal resuelve" 300 + "resuelve:" 23; OTRO_RESUELVE/ESTA_CORTE/LA_CORTE/RESUELVE_UP = 0 → sin over-match de instancia inferior). Recupera el dispositivo de fondo cuando el primer-con-firma es argumental (cierra B123/B124). Validación en disco: outcome +121 recuperaciones (otro→real) / 29 real→real (dom. inadmisible_280→merit) / 0 regresiones a otro; scan_concurrencia 0 sospechosos (mis-pick de concurrencia 331_p1028 cerrado = causa del rollback v20→v19 en H129); es_queja +8 recup / 2 correcciones de FP / 1 FN conocido (340_p114); votos net +1 (342_p1170 1→5 recupera panel, 348_p1435 dedup Alcalá; 332_p663 6→4 = exposición de B126, frente aparte). MAJOR: cambia el pick del dispositivo (afecta outcome/por_ello_text y derivados denormalizados en votos —outcome/is_merit/is_originaria/tipo_voto_sep—; considerando/firma/zonas/editorial sin cambio de lógica). // M21/H126: B122/B118 — skip de líneas vacías en el presupuesto del chunk de _barrer (resolver_dispositivo). El running-head intercalado dejaba vacías OCR que agotaban el chunk antes del '.' real y truncaban el verbo de disposición → outcome caía a otro. Skip-only +50 flips corpus-wide (otro→competencia 37), 0 regresiones (PoC H125). MAJOR: cambia el comportamiento de _barrer (afecta outcome/por_ello_text y sus derivados denormalizados en csjn_casos_votos —outcome/is_merit/is_originaria/tipo_voto_sep por voto—; considerando/firma/zonas/editorial intactos; identidad del voto juez/posicion/texto_voto/wc_voto intacta). Masking del banner = Fase 2 (gated). // B119: capa disposicion M20 (PASO 2) — detectores competencia/cautelar/nulidad_concesion/inoficioso pre-cascada + #1 originaria-no-merit + #2 des-hifenado es_originaria. Gate 0,907→0,953 (FP 19→5, 0 FN nuevos). // H113: split csjn_casos_textos — considerando_text/por_ello_text/firma_raw salen de csjn_casos.csv a output/parser/csjn_casos_textos.csv (5º CSV del parser, keyed por caso_id_canonico, espejo 1:1 5890 filas, SIN truncado; antes considerando[:2000] 47,6% cortado / por_ello[:300]); habilita materia capa 2 (lee el considerando completo). Escritura por proyección de fieldnames (patrón zonas), texto full ya estaba en memoria → relocaliza al escribir, sin cambio de lógica de parseo. Re-golden consciente + 7º output al manifest (generar_manifiesto v1.3). // H111: B114 find_tribunal_origen v12 — corta el nombre del tribunal por el fin de línea del OCR (guión/soft-hyphen intra-palabra + corte inter-palabra en preposición); v12 une hasta la línea que cierra en '.', break por carátula (_parece_caratula, proporción ≥60% MAYÚS) + _unhyphenate al persistir; ~1141 celdas tribunal_origen recuperadas, 0 violaciones de invariante; habilita capa 1 del Frente B (tribunal→fuero→materia). + Fix infra: lineterminator="\n" en los 4 DictWriter — csv.DictWriter default escribe CRLF, pero golden/prod estaban en LF (normalizados por git) → check_regresion daba FAIL espurio en los 4 CSV (byte-diff, 0 diffs de celda); ahora escritura LF determinística e independiente del entorno/git. // H108: capa-fuente es_queja — ancla fuerte de caratula ("recurso de hecho deducido/interpuesto por"), ~225 flips, guard cita; tail debil + capa considerando diferidos a DEUDA. // H107: B110 (parte) es_queja plural — \\bqueja\\b→\\bquejas?\\b en RE_ES_QUEJA y _SYN_Q (quejas multi-recurrente); ~60 es_queja 0→1, ~57 recuperan queja_resultado; aditivo (0 flips 1→0)

import re
import csv
import json
import argparse
import unicodedata
from pathlib import Path
from collections import Counter
from itertools import combinations
from parser_editorial import clasificar_editorial
from clasificador_disposicion import disposicion, es_revision_fondo   # PASO 3 M39 (H178): is_merit derivado del gate (fuente única; misma llamada que derivar_recursos). Reemplaza el import de es_de_fondo (B136/H169), que el gate usa internamente.

# ── Fix infra (H174): salida robusta a consolas/pipes no-UTF-8 ────────────────
# El parser imprime Unicode en el progreso (→, ×103). A consola directa de
# Windows sale en UTF-8 siempre (PEP 528), pero con stdout REDIRIGIDO
# (> log, | Tee-Object) Python cae al encoding de locale (cp1252) y el
# charmap aborta la corrida entera por un print cosmético. errors="replace"
# degrada el glifo no representable ('?') en vez de crashear: la corrida
# nunca muere por la salida, en ningún entorno, sin variables de entorno.
# Defecto reproducido sobre v23.1 intacta (latente en todas las versiones;
# solo dispara bajo redirección). Misma clase que el fix LF de H111:
# escritura independiente del entorno.
import sys
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except Exception:
        pass
del _stream

# ── Marcadores estructurales ──────────────────────────────────────────────────

RE_APERTURA = re.compile(r"^(FALLO|SENTENCIA)\s+DE\s+LA\s+CORTE\s+SUPREMA\s*$", re.I)
RE_FECHA_LINEA   = re.compile(r"^Buenos Aires[,]?\s+\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4}", re.I)
RE_FECHA_EXTRACT = re.compile(r"Buenos Aires[,]?\s+(\d{1,2}\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4})", re.I)

# Por ello — dispositivo institucional. v8/v9 distingue entre usos como dispositivo
# vs como cláusula subordinada (argumental).
RE_POR_ELLO          = re.compile(r"^Por ello[,.]?\s*", re.I)
POR_ELLO_ARGUMENTAL  = {"concluyó", "concluyo", "estimo", "estimó", "considera",
                       "considero", "consideró", "entiende", "entendió",
                       "afirma", "afirmó", "sostiene", "sostuvo",
                       "opino", "opinó"}

# v11: detector AMPLIADO del dispositivo. En tomos viejos (329-340) un ~25% de
# los fallos no usan "Por ello" sino una de estas aperturas alternativas.
# Empíricamente verificadas en LibroVol329_3.md sobre 79 fallos sin "Por ello":
#   - "Por los fundamentos [y conclusiones del dictamen del señor Procurador]"  41/79
#   - "De conformidad con [lo dictaminado por el señor Procurador]"             27/79
#   - Residuales: "Por todo lo expuesto", "Por lo expuesto", "Atento a",
#     "En consecuencia"
# El typo "concusiones" (por "conclusiones") aparece en OCR de tomos 329-336.
# Cada regex es .match() sobre línea ya stripeada (sin anchor de fin).
RE_DISPOSITIVO_VARIANTES = [
    # nombre              # regex
    ("por_los_fund",      re.compile(r"^Por los fundamentos\s+y\s+conc[lu]+siones", re.I)),
    ("por_los_fund_simple", re.compile(r"^Por los fundamentos\b", re.I)),
    ("de_conformidad",    re.compile(r"^De conformidad con\b", re.I)),
    ("por_todo_lo_exp",   re.compile(r"^Por todo lo expuesto\b", re.I)),
    ("por_todo_ello",     re.compile(r"^Por todo ello\b", re.I)),
    ("por_lo_expuesto",   re.compile(r"^Por lo expuesto\b", re.I)),
    ("por_estas_razones", re.compile(r"^Por estas razones\b", re.I)),
    ("en_merito",         re.compile(r"^En m[ée]rito\s+a\s+lo\b", re.I)),
    ("en_su_merito",      re.compile(r"^En su m[ée]rito\b", re.I)),
    # H197 (B162): en_consecuencia y atento_a MOVIDAS a
    # RE_DISPOSITIVO_VARIANTES_ZONIF_PERF (perf-gated solo en el zonificador).
    # ── H039: variantes confirmadas empíricamente (24 mejoras, 0 regresiones) ──
    ("por_lo_expresado",        re.compile(r"^Por lo expresado\b", re.I)),
    ("por_las_razones",         re.compile(r"^Por las razones\b", re.I)),
    ("por_las_consideraciones", re.compile(r"^Por las consideraciones\b", re.I)),
    ("oido_el",                 re.compile(r"^O[íi]dos?\s+(el|la|los|las)\b", re.I)),
    ("que_por_ello",            re.compile(r"^Que[,]?\s+por\s+ello\b", re.I)),
]

# ── H194 (B149 fix A2): variantes condicionales-a-performativo ──────────────
# Anclas de dispositivo que SOLO cuentan si la cola de la linea (mas cola_wrap,
# cuando el call-site puede peekear la linea siguiente) contiene un performativo
# (RE_PERF, fuente unica H130 — definida mas abajo, resuelta en call-time).
# Calibradas corpus-wide por poc_b149_anclas v0.1 (H194, candado E0 5703/5703):
#   en_virtud_perf   — B067 (BITACORA:4450, «pospuesto» sobre 5 hits de UN tomo,
#                      60% FP) resucitada con el discriminador que faltaba:
#                      268 matches / 204 en dictamen / perf-gated 16 = 16/16 TP
#                      (testigo original 348_p443; 8 son dispositivos de VOTO).
#   que_de_conf_perf — analogo de que_por_ello: 29 matches / perf-gated 1
#                      (344_p776, competencia embebida en considerando).
# «Por lo tanto» DESCARTADA con constancia (640 superficie, H039 70% argumental,
# rinde 2-3, borde 341_p250 indecidible; residuales 343_p720, 346_p1068).
RE_DISPOSITIVO_VARIANTES_PERF = [
    ("en_virtud_perf",   re.compile(r"^En virtud de lo expuesto\b", re.I)),
    ("que_de_conf_perf", re.compile(r"^Que,?\s+de conformidad con\b", re.I)),
]

# ── H197 (B162): variantes condicionales-a-performativo SOLO en el ZONIFICADOR ──
# {en_consecuencia, atento_a} salen de la lista T1: como anclas de zona son FP
# masivos (497 anclas espurias / 431 casos, hasta 1428 lineas de dispositivo
# espurio; testigos leidos 344_p1952 b923/b1586, 344_p2123 b1237/b1596 — wrap
# del OCR + conector argumental de parrafo; constancia madre H041: trio
# peligroso ya excluido del Tier 2 mid-line). En el RESOLUTOR siguen
# INCONDICIONALES (zonif=False): el gate misma-linea perderia dispositivos
# genuinos con performativo wrapeado (341_p774, revoca correcto) y aperturas
# procesales sin performativo alcanzable (330_p2520, 329_p2985 «hagase saber»
# enclitico). Los genuinos PICKEADOS que pierden el ancla de Pasada 1 recuperan
# la zona via el relabel A1 (H194). Flip-set: poc_b162_flipset v0.1, H197.
RE_DISPOSITIVO_VARIANTES_ZONIF_PERF = [
    ("en_consecuencia",   re.compile(r"^En consecuencia\s*,?\s*\b", re.I)),
    ("atento_a",          re.compile(r"^Atento\s+(a\s+)?(que|lo|el)\b", re.I)),
]

def detectar_apertura_dispositivo(stripped_line, cola_wrap="", zonif=False):
    """
    v11: devuelve (es_dispositivo: bool, tipo: str | None).

    H194 (B149 A2): cola_wrap opcional = linea siguiente stripeada, para que
    las variantes performativas (RE_DISPOSITIVO_VARIANTES_PERF) toleren el
    wrap del OCR («…oida la señora ⏎ Procuradora Fiscal, se declara…»).
    Con cola_wrap="" (call-sites del resolutor, sin cambio de firma) el
    performativo debe estar en la MISMA linea.

    es_dispositivo=True si la línea inicia el dispositivo del fallo. tipo
    identifica qué variante (para diagnóstico).

    Regla 'Por ello': solo cuenta como dispositivo si la palabra siguiente NO
    está en POR_ELLO_ARGUMENTAL (caso 'Por ello concluyó que...' es argumental,
    no dispositivo).

    v11 bugfix: el re.sub usa [,.]? (opcional) en vez de [,.] obligatorio,
    para que "Por ello concluyó..." (sin coma) sí entre por la rama
    argumental. v10 tenía esto roto: el regex de detección aceptaba "Por ello"
    sin coma pero el re.sub posterior no la limpiaba, dejando first_w='por' y
    saltándose la regla argumental.
    """
    if RE_POR_ELLO.match(stripped_line):
        rest = re.sub(r"^Por ello[,.]?\s*", "", stripped_line, flags=re.I)
        first_w = rest.split()[0].lower().rstrip(",;") if rest.split() else ""
        if first_w in POR_ELLO_ARGUMENTAL:
            return (False, None)
        return (True, "por_ello")
    for nombre, pat in RE_DISPOSITIVO_VARIANTES:
        if pat.match(stripped_line):
            return (True, nombre)
    # H194 (B149 A2): variantes que SOLO anclan con performativo en la cola.
    for nombre, pat in RE_DISPOSITIVO_VARIANTES_PERF:
        m = pat.match(stripped_line)
        if m:
            cola = stripped_line[m.end():] + " " + cola_wrap
            if RE_PERF.search(cola):
                return (True, nombre)
    # H197 (B162): variantes gated SOLO cuando llama el zonificador
    # (zonif=True, unico call-site con peek de wrap). En el resolutor
    # (zonif=False, default) son incondicionales — semantica pre-v32.
    for nombre, pat in RE_DISPOSITIVO_VARIANTES_ZONIF_PERF:
        m = pat.match(stripped_line)
        if m:
            if not zonif:
                return (True, nombre)
            cola = stripped_line[m.end():] + " " + cola_wrap
            if RE_PERF.search(cola):
                return (True, nombre)
    return (False, None)

# Considerando — apertura del cuerpo argumental
# B010: sin anchor ^ para detectar "Vistos los autos; Considerando:".
# Colon/punto obligatorio (no opcional) evita FP en body text.
# Usar .search() en todas las call sites (no .match()).
RE_CONSIDERANDO  = re.compile(r"Considerando\s*[:.]\s*$", re.I)

# Dictamen del Procurador (a excluir del wc principal)
# B159 (H196): forma-titulo LAXA — la linea debe ser SOLO el titulo del
# dictamen. Prefijo verbatim de la regex vieja + slot de UN token para
# "General" (tolera OCR "Geberal" 336.1 / "Genera" 338.1) + cola opcional
# "de la Nacion" + remate de puntuacion/asterisco. Mata el FP narrativo:
# el wrap del OCR deja "dictamen de la/del Procura..." a inicio de linea y
# re.I lo matcheaba (15 corpus-wide, 6 con el fallo entero engullido por la
# guarda H052). re.I SE CONSERVA: el titulo genuino existe en minuscula
# (versalitas-OCR 336.1 x8, tomo futuro) — capitalizacion a la H139
# DESCARTADA con dato. Calibrado sobre el dump completo (poc_b159_superficie
# v0.1, scripts/diagnostico/H196/): 3804 matches -> quedan 3789 / caen 15 /
# 0 perdidas. Fuente unica: cubre los 3 call-sites (zonificar L3122,
# frontera L2164, fin_real L2868) sin tocar logica; todos .match() booleano,
# 0 consumidores de grupos.
RE_DICT_HDR      = re.compile(
    r"^Dictamen\s+de(?:l)?\s+(?:la\s+)?Procura\S*"
    r"(?:\s+\w+)?"                       # slot "General" (tolera OCR)
    r"(?:\s+de\s+la\s+Naci[oó]n)?"
    r"\s*[.:\)\(\*\u2013\u2014-]*\s*$",
    re.I,
)

# v17: sumario editorial con link al fallo online (no contiene fallo parseable).
# Variantes detectadas:
#   - Tomos 345-346: "(*) Sentencia del [fecha]. Ver en https://sj.csjn.gov.ar/..."
#   - Tomos 347-349: "(*) Sentencia del [fecha]. Ver fallo."
# La regex matchea ambas variantes en una sola línea stripeada.
RE_SUMARIO_LINK  = re.compile(
    r"^\(\*\)\s+Sentencia del .+? Ver (en https://sj\.csjn\.gov\.ar|fallo)",
    re.I
)

# H052: anclas adicionales para el zonificador.
# "Vistos los autos" — apertura alternativa del cuerpo del fallo.
RE_VISTOS = re.compile(r"^\s*Vistos? los autos", re.I)
# Remisión a precedente/dictamen — señal fuerte de sumario editorial.
RE_REMISION = re.compile(
    r"^[–—-]\s*Del\s+(dictamen|precedente|voto|fallo)",
    re.I
)

# Votos y disidencias — regex mejorado cubre todas las variantes:
# v10: agregar 'Vicepresidente', 'Presidente', tolerar OCR con
# capitalización mezclada (ej: 'caRLos FERnando RosEnkRantz' por OCR de
# tipografía decorativa). El regex original solo buscaba 'Señor[es]/Señora[s]'.
RE_VOTO_HDR  = re.compile(
    r"^Voto\s+(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)
RE_DISID_HDR = re.compile(
    r"^Disidencia\s+(Parcial\s+)?(del?|de\s+l[ao]s?)\s+"
    r"(Se[nñ]or(?:es|as|a)?|Vicepresidente|Presidente|Ministr[ao]s?)",
    re.I
)

# B077: marcador editorial para señal de corte en detectar_fin_real (Pista 2).
# La clasificación detallada por subtipos vive en parser_editorial.py (H061).
# Validado H058: 0 falsos positivos en zona de fallos contra tomos 330, 342.

RE_EDITORIAL_ANY = re.compile(
    r"^(?:"
    r"A\s+C\s+O\s+R\s+D\s+A\s+D\s+A\s+S"
    r"|ACORDADAS\s+Y\s+RESOLUCIONES\s*$"
    r"|DISCURSOS\b"
    r"|INDICE\s+POR\s+LOS\s+NOMBRES"
    r"|NOMBRES\s+DE\s+LAS\s+PARTES\s*$"
    r"|INDICE\s+GENERAL\s*$"
    r"|INDICE\s+ALFAB[EÉ]TICO\s+POR\s+MATERIAS"
    r"|INDICE\s+DE\s+LEGISLACI[OÓ]N"
    r"|INDICE\s+SUMARIO\s*$"
    r"|LEGISLACI[OÓ]N\s+NACIONAL\s*$"
    r"|POR\s+MATERIAS\s*$"
    r")", re.I
)


def _es_marcador_editorial(linea):
    """B077: ¿la línea inicia una sección editorial (acordadas/índice/discurso)?"""
    s = linea.strip()
    return bool(s and RE_EDITORIAL_ANY.match(s))

# Page headers a ignorar en búsqueda de case_name
RE_PAGE_HEADER   = re.compile(
    r"^(FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACIÓN|"
    r"DE JUSTICIA DE LA NACION|\d{2,6})\s*$", re.I)

# M21 Fase 2 (B122/B118): running-head editorial intercalado en el cuerpo. A
# diferencia de RE_PAGE_HEADER (línea-sola, ^...$), este matchea la TERNA como
# SUBSTRING — 'número FALLOS DE LA CORTE SUPREMA número' / 'número DE JUSTICIA…' /
# '…NACIÓN número' (todas las orientaciones del OCR). El número OBLIGATORIO a un
# lado distingue el banner de la frase legítima "Corte Suprema de Justicia de la
# Nación" (que nunca lleva número adyacente): verificado 463 banners / 0 FP sobre
# el corpus. Se usa para enmascarar en _barrer (saca el banner del por_ello y, si
# la línea era solo banner, libera presupuesto del chunk → recupera el truncado).
RE_RUNNING_HEAD  = re.compile(
    r"\d{1,6}\s+(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s+\d{1,6}"
    r"|\d{1,6}\s+(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\b"
    r"|\b(?:FALLOS DE LA CORTE SUPREMA|DE JUSTICIA DE LA NACI[OÓ]N)\s+\d{1,6}")  # H139: sin re.I → case-sensitive

# v18: Fix 1 — V1 como fuente primaria de case_name_cuerpo.
# Auditoría B (sesión XV) midió 3.859 hits = 67.3% del corpus con captura
# limpia. Reemplaza a find_case_name como fuente primaria. La búsqueda
# arranca desde apertura_rel hacia adelante para evitar el dictamen previo
# (donde están las citas doctrinales que rompían find_case_name viejo).

RE_VISTOS_LOS_AUTOS = re.compile(
    r'^\s*Vistos los autos:\s*([\u201C\u201D"\u2018\u2019\'])',
    re.IGNORECASE
)
COMILLAS_CIERRE = '\u201C\u201D"\u2018\u2019\''

def extraer_caratula_v1(bloque, apertura_rel, max_lineas=8):
    """
    v18: extrae la carátula desde el patrón V1 (`Vistos los autos: "X"`).
    Itera el bloque desde apertura_rel hacia adelante. En cuanto encuentra
    el marcador, reconstruye la carátula concatenando líneas hasta cerrar
    la comilla, manejando wrap por silabación. Devuelve la carátula sin
    las comillas, o "" si no hay V1.
    """
    inicio = apertura_rel if apertura_rel is not None else 0
    for i in range(inicio, len(bloque)):
        linea = bloque[i]
        m = RE_VISTOS_LOS_AUTOS.match(linea)
        if not m:
            continue
        comilla_apert = m.group(1)
        pos_apertura = linea.index(comilla_apert)
        acumulado = linea[pos_apertura + 1:].rstrip()
        m_cierre = re.search(f'[{COMILLAS_CIERRE}]', acumulado)
        if m_cierre:
            return acumulado[:m_cierre.start()]
        for j in range(i + 1, min(i + max_lineas, len(bloque))):
            sig = bloque[j].rstrip()
            if acumulado.endswith('\u00AD') or acumulado.endswith('-'):
                acumulado = acumulado.rstrip('\u00AD-') + sig.lstrip()
            else:
                acumulado = acumulado + ' ' + sig.lstrip()
            if re.search(f'[{COMILLAS_CIERRE}]', sig):
                pos_cierre = max(acumulado.rfind(c) for c in COMILLAS_CIERRE)
                return acumulado[:pos_cierre]
        return acumulado
    return ""

# Tomo desde nombre de archivo
RE_TOMO          = re.compile(r"LibroVol(\d+)")

# ── Outcomes ──────────────────────────────────────────────────────────────────

# v10: dos detectores, uno para considerando (1) y otro para dispositivo (2).
# La gran diferencia con v9: art. 280 y "acordada 4/2007" se detectan
# ANTES de mirar el dispositivo, porque ese es el patrón institucional real.

# Versión flexibilizada: tolera más variaciones del texto histórico
# (variantes "es inadmisible", "resulta inadmisible", "se declara inadmisible")
# y mayor distancia entre la palabra "inadmisible" y la mención al art. 280.
RE_280_CONSIDERANDO = re.compile(
    r"recurso\s+extraordinario.{0,150}?"
    r"(es|resulta|se\s+declara)\s+inadmisible"
    r".{0,150}?(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal",
    re.I | re.DOTALL
)

# Variante alternativa: busca "art. 280 del Código Procesal Civil y Comercial"
# en el considerando, con o sin paréntesis de apertura. H065: fix regex
# art[íi]?culo? → (?:art\.?|art[íi]culo) para matchear "art." abreviado.
RE_280_LIBRE = re.compile(
    r"\(?\s*(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal\s+Civil\s+y\s+Comercial",
    re.I
)

# H066: tres variantes complementarias para detectar acordada 4/2007.
# Fixes H066:
#   - "arts." plural (arts.\xa04º → arts con s opcional)
#   - año corto: "4/07" además de "4/2007" → (?:20)?07
#   - (?!\d) después de 4 para no matchear "acordada 47/91" etc.
#   - (c) nueva: "art. N de la acordada 4/2007" (referencia directa,
#     sin pasar por "del reglamento"). Captura FN 333_p1235.
#
# Variantes:
#   (a) art. N del reglamento ... acordada 4/2007
#   (b) reglamento ... acordada 4/2007 (sin artículo explícito)
#   (c) art. N de la acordada 4/2007 (referencia directa al articulado)
RE_ACORDADA_4_CONSIDERANDO = re.compile(
    r"(?:art[s]?\.?\s*|art[íi]culo\s*)\d+\s*[°º]?\s*"
    r"(?:,\s*inc[s.]?.{0,30}?)?\s*del\s+reglamento"
    r".{0,80}?acordada\s*(?:n[°º]?\s*)?4(?!\d)\s*/?\s*(?:(?:del?\s+)?(?:20)?07)?",
    re.I | re.DOTALL
)
RE_ACORDADA_4_REGLAMENTO = re.compile(
    r"reglamento.{0,60}?acordada\s*(?:n[°º]?\s*)?4(?!\d)\s*/?\s*(?:(?:del?\s+)?(?:20)?07)?",
    re.I | re.DOTALL
)
RE_ACORDADA_4_DIRECTA = re.compile(
    r"(?:art[s]?\.?\s*|art[íi]culo\s*)\d+\s*[°º]?\s*"
    r"(?:,\s*inc[s.]?.{0,30}?)?\s*de\s+la\s+"
    r"acordada\s*(?:n[°º]?\s*)?4(?!\d)\s*/?\s*(?:(?:del?\s+)?(?:20)?07)?",
    re.I | re.DOTALL
)

OUTCOME_PATTERNS_DISPOSITIVO = [
    # Ordenados por frecuencia empírica para short-circuit
    ("hace_lugar",      re.compile(r"\bse hace lugar\b", re.I)),
    ("desestima",       re.compile(r"\bse (lo |los )?desestiman?\b", re.I)),
    ("procedente",      re.compile(r"\bse declara procedente\b", re.I)),
    ("revoca",          re.compile(r"\bse revoca\b", re.I)),
    ("confirma",        re.compile(r"\bse confirma\b", re.I)),
    ("competencia",     re.compile(
        r"\bse declara (que (debe|resulta|deberá)|la competencia|incompetente)\b|"
        r"\bdeberá entender\b|\bresulta competente\b|\bdeclara su (in)?competencia\b",
        re.I)),
    # H104: outcome=originaria DEPRECADO — era category error (tipo de proceso,
    # NO disposición). El estructural enumeración-"I." robaba disposiciones de
    # mérito: "Por ello, se resuelve: I. Desestimar/Rechazar/Hacer lugar" caía acá
    # ANTES de los patterns en infinitivo (líneas ~335-346). La dimensión proceso
    # vive completa en is_originaria / tribunal_origen_status (no se pierde nada).
    # En su lugar: aceptación de competencia originaria → competencia (simétrico
    # con la declinación de B108). Lookbehind 'no ' para no comerse "no corresponde".
    ("competencia",     re.compile(
        r"(?<!no )\bcorresponde\s+a\s+(?:la\s+|su\s+)?competencia\s+originaria\b|"
        r"(?<!no )\bes\s+de\s+la\s+competencia\s+originaria\b|"
        r"\bdeclarar\s+la\s+competencia\s+originaria\b", re.I)),  # H104: forma "declarar la comp. orig. de la Corte"
    ("abstracto",       re.compile(
        r"\binoficioso\b|\babstracto\b|\bse declara abstracta?\b", re.I)),
    ("nulidad",         re.compile(r"\bse declara la nulidad\b", re.I)),
    ("desistimiento",   re.compile(r"\bse tiene por desistid[ao]\b", re.I)),
    ("mal_concedido",   re.compile(r"\bse (lo )?declara mal concedid[ao]\b", re.I)),
    # B091 (H073): fallback infinitivo — captura "el Tribunal resuelve: Revocar",
    # "corresponde revocar", "se impone revocar", etc. Posición final (antes de
    # catch-all) para que originaria, abstracto y otros merit outcomes tengan
    # prioridad sobre la mención de revocar en dispositivos mixtos.
    ("revoca",          re.compile(r"\brevocar\b", re.I)),
    # ── H077: zona fallback — solo rescatan de "otro" ────────────────────────
    # Rechaza: formas directas + infinitivo (outcome NUEVO).
    # "se rechaza la demanda", "se rechazan las recusaciones", "Rechazar in
    # limine", etc.  No existía pattern previo.
    ("rechaza",         re.compile(r"\bse (lo |los |la |las )?rechazan?\b", re.I)),
    ("rechaza",         re.compile(r"\brechazar\b", re.I)),
    # Capa 2: plurales y pronombres que los patterns de zona alta no cubren.
    # "se la desestima", "se declaran procedentes", "se confirman".
    ("desestima",       re.compile(r"\bse (la |las )?desestiman?\b", re.I)),
    ("procedente",      re.compile(r"\bse declaran procedentes?\b", re.I)),
    ("confirma",        re.compile(r"\bse confirman\b", re.I)),
    # Capa 1: infinitivos — "el Tribunal resuelve: Confirmar / Desestimar /
    # Hacer lugar / Declarar procedente".  Misma lógica que B091 (revocar).
    ("confirma",        re.compile(r"\bconfirmar\b", re.I)),
    ("desestima",       re.compile(r"\bdesestimar\b", re.I)),
    ("hace_lugar",      re.compile(r"\bhacer lugar\b", re.I)),
    ("procedente",      re.compile(r"\bdeclarar procedentes?\b", re.I)),
    # Competencia: formas faltantes en zona alta.
    ("competencia",     re.compile(
        r"\bse declara competente\b|\bdeclarar(?:se)? (?:la )?(?:in)?competente\b|"
        r"\bdeclarar que .{0,20}(?:debe|deberá|resulta)\b", re.I)),
    # B108 (H103): competencia originaria que la cascada dejaba en "otro".
    # Origen M19. La Corte DECLINA su competencia originaria. Formas que los
    # patterns previos no cubren (el adjetivo "incompetente" ya estaba; faltaba
    # el sustantivo "incompetencia" y las formas "ajena a"/"no corresponde a la
    # competencia originaria"). Zona fallback: solo rescata de "otro".
    ("competencia",     re.compile(
        r"\bdeclara(?:r|se)?\s+(?:la\s+)?incompetencia\b|"
        r"\b(?:es\s+)?ajena\s+a\s+(?:su\s+|la\s+)?competencia\s+originaria\b|"
        r"\bno\s+corresponde\s+a\s+(?:su\s+|la\s+)?competencia\s+originaria\b|"
        r"\bno\s+es\s+de\s+(?:la\s+)?competencia\s+originaria\b", re.I)),   # B108 frontera H104
    # ── fin zona fallback H077 ───────────────────────────────────────────────
    # ── H079: procedente expandido + aposición + deja_sin_efecto ──────────────
    # Fix A1: "se declara formalmente/parcialmente procedente". Posición en
    # zona fallback para no pisar revoca/confirma que vienen antes en la cascada.
    # Así "se declara formalmente procedente el REF y se revoca" sigue siendo
    # revoca (outcome más informativo), y solo casos sin otro merit outcome
    # se rescatan de "otro".
    ("procedente",      re.compile(
        r"\bse\s+declara\s+(?:formalmente|parcialmente)\s+procedente\b", re.I)),
    # Fix A2: "procedente" en aposición: "se declara admisible la queja,
    # procedente el recurso extraordinario y se deja sin efecto".
    ("procedente",      re.compile(
        r"\bprocedentes?\s+(?:el\s+recurso|los\s+recursos)", re.I)),
    # Fix B: "se deja sin efecto la sentencia/resolución/pronunciamiento".
    # Posición final (antes de catch-all): solo rescata de "otro".
    # 1302 fallos mencionan "deja sin efecto" pero la mayoría ya está
    # clasificada por patterns anteriores (hace_lugar, procedente, etc.).
    ("deja_sin_efecto", re.compile(
        r"(?:se\s+)?deja(?:r|n)?\s+sin\s+efecto|"
        r"corresponde\s+dejar\s+sin\s+efecto", re.I)),
    # ── H079 2E: categorías menores — solo rescatan de "otro" ───────────────
    # Posición final (antes de catch-all): la cascada primero-que-matchea
    # garantiza que estos solo se aplican a casos sin outcome previo.
    # Ninguno es MERIT_OUTCOME: 280/ac4 del considerando puede sobreescribir.
    ("desierto",        re.compile(r"\bdesiert[oa]\b", re.I)),
    ("inadmisible",     re.compile(r"\binadmisible\b", re.I)),
    ("improcedente",    re.compile(r"\bimprocedente\b", re.I)),
    ("caducidad",       re.compile(r"\bcaducidad\b|\bcaduc[oó]\b", re.I)),
    # ── fin H079 ──────────────────────────────────────────────────────────────
    # B113 (H105): forma infinitiva "Declarar abstracta/o la cuestión/pretensión".
    # Origen: deprecación de outcome=originaria (B112, H104) — estos casos estaban
    # enmascarados como originaria por el estructural enumeración-"I." y al caerse
    # ese pattern quedaron en "otro". El pattern alto de abstracto (~329) solo cubre
    # "abstracto" (masc. suelto) y "se declara abstracta?"; NO la forma en infinitivo
    # del dispositivo ("Por ello se resuelve: Declarar abstracta la cuestión").
    # POSICIÓN FALLBACK (no se extiende el pattern alto) a propósito: "declarar
    # abstracta" aparece en dispositivos MIXTOS donde no domina — 329_p753 (I.
    # declarar abstracta una cuestión incidental, II. rechazar la impugnación de
    # liquidación -> rechaza) y 344_p3070 (I. competencia originaria, II. declarar
    # abstracta -> competencia). Subirlo a zona alta los robaria; aca solo rescata
    # de "otro" (cascada primero-que-matchea). abstracto in OUTCOMES_NO_FALLBACK_280
    # -> no lo pisa el 280/ac4 del considerando; is_merit no se mueve (histórico:
    # abstracto ∉ MERIT_OUTCOMES; desde H178 is_merit se deriva del gate del
    # clasificador — mismo efecto por otra vía). Adjetivo ANTES del sustantivo
    # (forma real de los 12 testigo).
    ("abstracto",       re.compile(r"\bdeclarar\s+abstract[oa]\b", re.I)),
    # catch-all
    ("otro",            re.compile(r".*")),
]

def _unhyphenate(text: str) -> str:
    """B056 (H066): une quiebres de línea con guión en texto digitalizado.
    'se deses- tima' → 'se desestima', 'mal con- cedido' → 'mal concedido'.
    Solo une cuando hay \\w-\\s+\\w (guión de corte tipográfico).
    No toca guiones legítimos (Buenos Aires-La Plata) porque esos no
    tienen whitespace después del guión."""
    return re.sub(r"(\w)[­\u00ad-]\s+(\w)", r"\1\2", text)


# ── B107 (H103): guards de la cascada de outcome ─────────────────────────────
# Origen: M19 (codificacion ciega del Marco A). La cascada matcheaba "hacer lugar"
# por substring dentro de "no hacer lugar" (negacion: la semantica es rechaza/
# desestima/etc.) y dentro de "hacer lugar a la excepcion de incompetencia"
# (la semantica es competencia). Ambas regex operan sobre texto YA pasado por
# _unhyphenate (Paso 0 de classify_outcome), por eso no necesitan tolerar el
# guion de corte del OCR ("in- competencia" ya viene unido a "incompetencia").
RE_B107_LUGAR_EXCEP_INCOMP = re.compile(
    r"\b(?:se\s+hace|hacer)\s+lugar\s+a\s+la\s+excepci[oó]n\s+de\s+incompetencia\b",
    re.I)
RE_B107_NEG_HACER_LUGAR = re.compile(
    r"\bno\s+(?:se\s+)?(?:corresponde\s+)?(?:hacer?|ha|hace|hacen)\s+lugar\b", re.I)


# ── B119 (PASO 2 M20): detectores de disposición ─────────────────────────────
# Capa de DISPOSICIÓN, NO exclusión de familia (la queja no es familia excluible:
# 69/114 quejas en n=300 son merit gold=sí). Pre-cascada: corren ANTES de
# OUTCOME_PATTERNS_DISPOSITIVO porque el verbo de merit (hace_lugar/revoca/
# deja_sin_efecto) aparece primero en el por_ello y ganaría la cascada por
# posición, enmascarando que la disposición REAL es procesal (competencia /
# cautelar / nulidad del auto de concesión / inoficioso). Operan sobre por_ello YA
# _unhyphenate'd + whitespace-normalizado (Paso 0/0b de classify_outcome).
# Recall-safety n300: 0 disparos sobre gold=sí (no crean FN). Recupera 11 FP:
# competencia(5) 339_p490·347_p360·329_p2645·331_p989·340_p431, cautelar(1)
# 342_p2399, nulidad_concesion(4) 329_p1626·348_p1717·329_p472·346_p439,
# inoficioso→abstracto(1) 348_p1499.

# Nulidad/dejar sin efecto del auto de concesión o de la denegatoria del REX: la
# disposición ataca la VÍA (concesión/denegación del recurso), no el fondo. El
# label "nulidad" sería merit; "nulidad_concesion" es disposición procesal.
RE_DISP_NULIDAD_CONCESION = re.compile(
    r"auto\s+de\s+concesi[oó]n\s+del\s+recurso\s+extraordinario|"
    r"nulidad\s+de\s+(?:la\s+resoluci[oó]n|las\s+resoluciones)\b"
    r".{0,90}?conced\w+\b.{0,30}?recursos?\s+extraordinarios?|"
    r"(?:resoluci[oó]n|auto)\s+\w*\s*que\s+conced\w+\s+(?:el|los)\s+recursos?\s+extraordinarios?|"
    r"resoluci[oó]n\s+denegatoria\s+del\s+remedio\s+federal|"
    r"denegatoria\s+del\s+remedio\s+federal", re.I)

# Disposición que revoca/deja sin efecto/confirma/modifica una MEDIDA CAUTELAR:
# el dispositivo no resuelve el fondo del litigio.
RE_DISP_CAUTELAR = re.compile(
    r"\b(?:revoca|deja\s+sin\s+efecto|confirma|modifica|hace\s+lugar\s+a)\b"
    r"[^.]{0,40}?\bmedida\s+cautelar\b|"
    r"\bmedida\s+cautelar\s+(?:decretada|dispuesta|ordenada)\b", re.I)

# Competencia resuelta como disposición aun cuando un verbo de merit la precede
# ("se hace lugar... se revoca... resulta competente para conocer"). Anclas fuertes
# de competencia DISPOSITIVA, no la mera mención de incompetencia en el cuerpo.
RE_DISP_COMPETENCIA = re.compile(
    r"resulta\s+competente\s+para\s+conocer|"
    r"tomar\s+intervenci[oó]n\s+en\s+el\s+conflicto|"
    r"conflicto\s+(?:positivo|negativo)\s+de\s+competencia", re.I)

# Inoficioso/abstracto: la Corte declina pronunciarse por falta de utilidad.
# Anclado a "inoficioso ... pronunciamiento" / "abstracta la cuestión"; NO basta la
# mera mención de "abstracto". DEUDA: mixto inoficioso+merit en puntos separados
# (332_p2208 tipo) sería FN si el inoficioso cayera en el por_ello — 0 en n300.
RE_DISP_INOFICIOSO = re.compile(
    r"inoficioso\s+(?:emitir|expedirse|(?:un\s+)?pronunciamiento|pronunciarse)|"
    r"(?:deviene|torna\w*|result\w+)\s+(?:inoficioso|abstract\w+)|"
    r"declara\w*\s+abstract\w+\s+la\s+cuesti[oó]n", re.I)


def classify_outcome(por_ello_text: str, considerando_text: str = "") -> str:
    """
    v14 (H077): zona fallback con outcome "rechaza" + infinitivos (confirmar,
    desestimar, hacer lugar, declarar procedente) + plurales/pronombres.
    Normalización de whitespace pre-matching (double spaces de OCR).
    610 "otro" reclasificados, 0 regresiones.

      0. Normalizar textos: _unhyphenate + whitespace.
      1. Determinar outcome del dispositivo (por_ello_text). Si por_ello_text
         está vacío → base "sin_dispositivo" (R2 H090: sede única del fallback
         280/ac4, antes duplicada en un bloque inline de procesar_archivo).
      2. Si el dispositivo da merit outcome (hace_lugar, procedente, revoca,
         confirma, rechaza, nulidad, competencia, abstracto, originaria,
         desistimiento), NO sobreescribir con 280/ac4 del considerando.
         Motivo: en fallos mixtos la Corte rechaza un agravio por 280 pero
         concede otro — el outcome relevante es la concesión.
      3. Si el dispositivo NO da merit outcome, buscar 280/ac4 en considerando.
    """
    # H092: renombrado desde MERIT_OUTCOMES. Su rol NO es "merit" sino "el
    # dispositivo ya resolvio algo, no sobreescribir con el 280 del considerando"
    # (incluye abstracto/desistimiento, que son gate). El set de merito real
    # (is_merit) ERA el MERIT_OUTCOMES de procesar_archivo (retirado H178:
    # is_merit se deriva del gate es_revision_fondo del clasificador, fuente única).
    # B109 (H106): "desestima" suma al set. Cuando el dispositivo desestima la via
    # (la queja / presentacion directa / recurso), el verbo dispositivo manda: el
    # 280/ac4 del considerando es la CAUSAL del rechazo, no el outcome. La causal
    # se deriva ahora en clasificador_causa (capa-deriver, M26 paso 3), gateada por
    # admisibilidad=="inadmite" (antes vivia en clasificar_causa_inadmisibilidad del
    # parser). Antes "desestima"
    # caia al Paso 3 y el 280/ac4 lo pisaba con inadmisible_280/ac4 (229 casos).
    # Los mixtos de resultados opuestos (342_p1017: desestima queja + procedente
    # otro REX) quedan en "desestima" como mejor aproximacion disponible hasta el
    # refactor etapa/disposicion+parte (M20); logueados en DEUDA.
    OUTCOMES_NO_FALLBACK_280 = {"hace_lugar", "procedente", "revoca", "confirma", "rechaza",
                      "nulidad", "competencia", "abstracto", "originaria",
                      "desistimiento", "deja_sin_efecto", "desestima",
                      "cautelar", "nulidad_concesion"}  # B119 (PASO 2 M20)

    # Paso 0 (H066): normalizar quiebres tipográficos
    por_ello_text = _unhyphenate(por_ello_text)
    considerando_text = _unhyphenate(considerando_text)
    # Paso 0b (H077): normalizar whitespace (double spaces de OCR)
    por_ello_text = re.sub(r"\s+", " ", por_ello_text).strip()
    considerando_text = re.sub(r"\s+", " ", considerando_text).strip()

    # Paso 1: outcome del dispositivo (centinela si no hay por_ello)
    if not por_ello_text:
        base = "sin_dispositivo"
    else:
        # B107.1: "hacer/se hace lugar a la excepcion de incompetencia" es una
        # decision de competencia, no un hace_lugar. Escopado a la frase exacta
        # (no a cualquier mencion de "incompetencia") para no pisar rechaza/
        # originaria de casos que solo la nombran.
        if RE_B107_LUGAR_EXCEP_INCOMP.search(por_ello_text):
            return "competencia"
        # B119 (PASO 2 M20): disposición procesal pre-cascada. El verbo de merit
        # aparece antes en el por_ello y ganaría la cascada por posición; estos
        # guards capturan la disposición REAL (procesal, no de fondo) y devuelven
        # un label no-merit. Orden: del ancla más específica a la más general.
        if RE_DISP_NULIDAD_CONCESION.search(por_ello_text):
            return "nulidad_concesion"
        if RE_DISP_CAUTELAR.search(por_ello_text):
            return "cautelar"
        if RE_DISP_COMPETENCIA.search(por_ello_text):
            return "competencia"
        if RE_DISP_INOFICIOSO.search(por_ello_text):
            return "abstracto"
        # B107.2: enmascarar "no (se) hace(r) lugar" para que la negacion no
        # dispare hace_lugar; el dispositivo real lo resuelve la cascada sobre el
        # texto enmascarado (un "hacer lugar a X" NO negado, como en dispositivos
        # mixtos, sobrevive y sigue clasificando bien).
        hubo_negacion = bool(RE_B107_NEG_HACER_LUGAR.search(por_ello_text))
        texto_disp = (RE_B107_NEG_HACER_LUGAR.sub(" ", por_ello_text)
                      if hubo_negacion else por_ello_text)
        outcome_disp = "otro"
        for label, pat in OUTCOME_PATTERNS_DISPOSITIVO:
            if pat.search(texto_disp):
                outcome_disp = label
                break
        # B107.3: negacion pura (sin otro verbo dispositivo) -> rechaza, pero como
        # base DEBIL: cae al Paso 3 para que el 280/ac4 del considerando aun pueda
        # ganar (evita pisar inadmisible_acordada_4 en quejas "no ha lugar").
        if hubo_negacion and outcome_disp == "otro":
            base = "rechaza"
        # Paso 2: si es merit, no sobreescribir
        elif outcome_disp in OUTCOMES_NO_FALLBACK_280:
            return outcome_disp
        else:
            base = outcome_disp

    # Paso 3: buscar 280 / acordada 4 en considerando (sede única, R2 H090)
    if considerando_text:
        if RE_280_CONSIDERANDO.search(considerando_text):
            return "inadmisible_280"
        if RE_280_LIBRE.search(considerando_text):
            return "inadmisible_280"
        if (RE_ACORDADA_4_CONSIDERANDO.search(considerando_text)
                or RE_ACORDADA_4_REGLAMENTO.search(considerando_text)
                or RE_ACORDADA_4_DIRECTA.search(considerando_text)):
            return "inadmisible_acordada_4"

    return base


# ── H078: es_queja + queja_resultado ─────────────────────────────────────────
# "Queja" = recurso de hecho = presentación directa. Tres sinónimos para la
# misma vía de acceso: el recurso que se interpone ante la CSJN cuando la
# Cámara deniega el REF.

RE_ES_QUEJA = re.compile(
    r"\bquejas?\b|\brecursos?\s+de\s+hecho\b|\bpresentaci[oó]n(?:es)?\s+directas?\b", re.I)

_SYN_Q = r"(?:quejas?|presentaci[oó]n(?:es)?\s+directas?|recursos?\s+de\s+hecho)"

QUEJA_RESULTADO_PATTERNS = [
    ("hace_lugar", re.compile(
        rf"(?:se\s+)?(?:re)?hace[n]?\s+lugar\s+(?:\w+\s+)?(?:a\s+)?la[s]?\s+{_SYN_Q}|"
        rf"(?:se\s+resuelve|resuelve)\s*:?\s*(?:I\.\s*)?[Hh]acer\s+lugar\s+"
        rf"(?:\w+\s+)?a\s+la[s]?\s+{_SYN_Q}|"
        rf"hacer\s+lugar\s+(?:a\s+)?la[s]?\s+{_SYN_Q}", re.I)),
    ("admisible", re.compile(
        rf"se\s+declara[n]?\s+(?:formalmente\s+)?admisibles?\s+"
        rf"(?:la[s]?\s+|el\s+)?{_SYN_Q}|"
        rf"se\s+admite[n]?\s+(?:la[s]?\s+|el\s+)?{_SYN_Q}|"
        rf"[Dd]eclarar\s+admisibles?\s+(?:la[s]?\s+|el\s+)?{_SYN_Q}|"
        rf"admitir\s+(?:la[s]?\s+|el\s+)?{_SYN_Q}|"
        rf"se\s+decide\s+admitir\s+(?:la[s]?\s+)?{_SYN_Q}", re.I)),
    ("procedente", re.compile(
        rf"se\s+declara[n]?\s+(?:formalmente\s+)?procedentes?\s+"
        rf"(?:la[s]?\s+|el\s+)?{_SYN_Q}|"
        rf"procedentes?\s+(?:la[s]?\s+|el\s+){_SYN_Q}|"
        rf"procedentes?\s+(?:el\s+recurso|los\s+recursos).*{_SYN_Q}", re.I)),
    ("desestima", re.compile(
        rf"se\s+desestima[n]?\s+.*?\b{_SYN_Q}\b|"
        rf"[Dd]esestimar\s+(?:la[s]?\s+|el\s+|esta?s?\s+)?{_SYN_Q}", re.I)),
    ("rechaza", re.compile(
        rf"se\s+rechaza[n]?\s+.*?\b{_SYN_Q}\b|"
        rf"rechaz[áa]ndose\s+.*?\b{_SYN_Q}\b|"
        rf"rechaza\s+(?:la[s]?\s+|el\s+){_SYN_Q}|"
        rf"rechazar\s+la[s]?\s+{_SYN_Q}", re.I)),
    ("inadmisible", re.compile(
        rf"se\s+declara[n]?\s+inadmisibles?\s+(?:la[s]?\s+|el\s+)?{_SYN_Q}", re.I)),
    ("agreguese", re.compile(rf"agr[ée]guese[n]?\s+la[s]?\s+{_SYN_Q}", re.I)),
    ("desistida", re.compile(
        rf"se\s+tiene\s+por\s+desistid[ao]\s+.*?\b{_SYN_Q}\b", re.I)),
    ("abstracta", re.compile(
        rf"abstracta?\s+.*?\b{_SYN_Q}\b|"
        rf"inoficioso\s+.*?\b{_SYN_Q}\b", re.I)),
    ("improcedente", re.compile(
        rf"improcedente\s+.*?\b{_SYN_Q}\b", re.I)),
    ("nula", re.compile(
        rf"(?:se\s+)?decl[áa]ra(?:se)?\s+nul[oa]\s+.*?\b{_SYN_Q}\b", re.I)),
    ("suspendida", re.compile(
        rf"(?:suspender|suspende|difi[ée]rese)\s+.*?\b{_SYN_Q}\b|"
        rf"resérvese\s+.*?\b{_SYN_Q}\b", re.I)),
]


# ── H108: capa-fuente de es_queja — detección por carátula ───────────────────
# classify_queja miraba SOLO el por_ello (dispositivo): perdía las quejas cuya
# vía se nombra en la carátula y no se repite en el dispositivo. La carátula usa
# la fórmula ritual "recurso de hecho deducido/interpuesto por <PARTE>", que
# además nombra la parte recurrente (gancho M20: cod_parte a nivel parte×recurso).
# Capa 1 (esta): ancla FUERTE de carátula -> ~225 flips, alta precisión.
# Guard RE_CARAT_CITA: la carátula a veces arrastra una CITA de otro fallo
# ("(Fallos: 328:4059)", "...publicado...") -> no es la vía del caso propio.
# DIFERIDO a DEUDA (requieren lectura sobre .md antes de habilitarse):
#   - capa débil de carátula ("s/ queja" suelto, presentación directa): ~11
#     casos ambiguos, TP limpios mezclados con fragmentos/residuo;
#   - capa considerando (ancla fuerte sobre el considerando completo).
RE_CARAT_QUEJA = re.compile(
    r"recursos?\s+de\s+hecho\s+(?:deducidos?|interpuestos?)\s+por", re.I)
RE_CARAT_CITA = re.compile(r"\(Fallos?:|publi[­\-]?cad", re.I)


def _es_queja_por_caratula(caratula: str) -> bool:
    """Capa 1: ancla fuerte de carátula. Guard de cita primero (la carátula puede
    arrastrar un fallo citado, no la vía propia)."""
    if not caratula:
        return False
    if RE_CARAT_CITA.search(caratula):
        return False
    return bool(RE_CARAT_QUEJA.search(caratula))


def classify_queja(por_ello_text: str, caratula_text: str = ""):
    """H078 + H108: detecta si el fallo es una queja y clasifica su resultado.
    es_queja: capa carátula (ancla fuerte, alta precisión) OR por_ello (RE_ES_QUEJA).
    queja_resultado: SIEMPRE del por_ello (el resultado vive en el dispositivo).
    Retorna (es_queja: bool, queja_resultado: str).
    queja_resultado es "" si es_queja=False o si no se pudo clasificar."""
    text = _unhyphenate(por_ello_text)
    text = re.sub(r"\s+", " ", text).strip()
    es_queja = _es_queja_por_caratula(caratula_text) or bool(RE_ES_QUEJA.search(text))
    if not es_queja:
        return False, ""
    for label, pat in QUEJA_RESULTADO_PATTERNS:
        if pat.search(text):
            return True, label
    return True, ""


# ── H078: tipo_cuestion_federal ──────────────────────────────────────────────
# Dos puertas de entrada al REF:
#   - Art. 14 ley 48: cuestión federal propiamente dicha.
#   - Doctrina de la arbitrariedad: creación pretoriana.
#
# Fuente primaria: sumario editorial (texto pre-apertura en el bloque).
#   La Secretaría de Jurisprudencia clasifica explícitamente:
#   - Tomo 330 (viejo): "RECURSO EXTRAORDINARIO: ... Sentencias arbitrarias."
#                        "RECURSO EXTRAORDINARIO: ... Cuestión federal."
#   - Tomo 348 (nuevo): "SENTENCIA ARBITRARIA" como header standalone.
# Fuente secundaria (fallback): considerando_text de la Corte.

# Patterns para sumario editorial (más confiable)
RE_SUMARIO_ARBITRARIEDAD = re.compile(
    r"SENTENCIA\s+ARBITRARIA|"
    r"[Ss]entencias?\s+arbitrarias?|"
    r"[Dd]octrina\s+de\s+la\s+arbitrariedad|"
    r"[Dd]escalific\w+\s+como\s+acto\s+jurisdiccional",
    re.I)

RE_SUMARIO_CUESTION_FEDERAL = re.compile(
    r"[Cc]uesti[oó]n\s+federal|"
    r"[Cc]uestiones\s+federales",
    re.I)

# Patterns para considerando_text (fallback, menos confiable)
RE_TIPO_CF_ARBITRARIEDAD = re.compile(
    r"sentencia\s+arbitraria|"
    r"doctrina\s+de\s+la\s+arbitrariedad|"
    r"arbitrariedad\s+de\s+(?:la\s+)?sentencia|"
    r"tacha\s+de\s+arbitrariedad|"
    r"descalific\w+\s+como\s+acto\s+jurisdiccional|"
    r"\barbitrariedad\b",
    re.I)

RE_TIPO_CF_CUESTION_FEDERAL = re.compile(
    r"art[íi]culo\s+14\s+de\s+la\s+ley\s+48|"
    r"art\.?\s*14\s+(?:de\s+)?(?:la\s+)?ley\s+48|"
    r"cuesti[oó]n\s+federal|"
    r"ley\s+48",
    re.I)


def classify_cuestion_federal(sumario_text: str, considerando_text: str) -> str:
    """H078: clasifica tipo de cuestión federal.
    Busca primero en sumario editorial (clasificación de la Secretaría de
    Jurisprudencia), fallback al considerando_text de la Corte.
    Retorna: 'arbitrariedad', 'cuestion_federal', 'mixto', o ''."""

    # ── Fuente primaria: sumario editorial ──
    if sumario_text:
        st = _unhyphenate(sumario_text)
        st = re.sub(r"\s+", " ", st).strip()
        has_arb = bool(RE_SUMARIO_ARBITRARIEDAD.search(st))
        has_cf  = bool(RE_SUMARIO_CUESTION_FEDERAL.search(st))
        if has_arb and has_cf:
            return "mixto"
        if has_arb:
            return "arbitrariedad"
        if has_cf:
            return "cuestion_federal"

    # ── Fuente secundaria: considerando_text ──
    if considerando_text:
        ct = _unhyphenate(considerando_text)
        ct = re.sub(r"\s+", " ", ct).strip()
        has_arb = bool(RE_TIPO_CF_ARBITRARIEDAD.search(ct))
        has_cf  = bool(RE_TIPO_CF_CUESTION_FEDERAL.search(ct))
        if has_arb and has_cf:
            return "mixto"
        if has_arb:
            return "arbitrariedad"
        if has_cf:
            return "cuestion_federal"

    return ""

# ── Jueces conocidos ──────────────────────────────────────────────────────────
# (idéntico a v9, copiado tal cual)

# ── B153 (H191): JUECES_CONOCIDOS pasa a ser DATO (patrón M46) ────────────────
# La tabla vive en _meta/jueces/jueces_csjn.csv (nombre_canonico, tipo, patron,
# periodo_desde/hasta, fuente, nota, testigos); el set se compila al importar.
# Migración VERBATIM de las 56 entradas hardcodeadas (<=v27.1) + 18 nuevas
# (2 titulares históricos —Moliné O'Connor, Bossert— en fallos publicados
# tardíamente + 16 conjueces) + 2 ensanches de variante (Otero sin «LUIS»,
# Leal de Ibarra OCR «MARIAL»). tipo=conjuez recompone el sufijo « (conjuez)»
# → contrato de n_titulares intacto. Todos los patrones compilan con re.I
# (invariante del set viejo, 56/56). Fail-fast si falta la tabla (estilo
# derivers). periodo_desde/hasta: columnas reservadas para el validador
# «n_jueces < mínimo del período» y full_bench period-aware (M pendiente).
_META_JUECES = Path(__file__).resolve().parents[2] / "_meta" / "jueces" / "jueces_csjn.csv"

def _cargar_jueces_conocidos(path=_META_JUECES):
    if not path.exists():
        sys.exit(f"[FATAL] no existe la tabla de jueces: {path}\n"
                 f"        (B153/H191: JUECES_CONOCIDOS es dato, patron M46)")
    out = []
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            tag = " (conjuez)" if r["tipo"] == "conjuez" else ""
            out.append((re.compile(r["patron"], re.I), r["nombre_canonico"] + tag))
    return out

JUECES_CONOCIDOS = _cargar_jueces_conocidos()

# ── M52 (H198): prefiltro de literales obligatorios para JUECES_CONOCIDOS ────
# El caso dominante del hot spot (perfil H196: linea_es_firma_de_juez ~55% del
# runtime) es el NEGATIVO: cada línea sin juez pagaba los 87 re.search de la
# tabla. La unión de alternación única (diseño original DEUDA M52) NO rinde:
# re de stdlib no optimiza alternaciones grandes (mismo O(n·87), medido 1.0x).
# En su lugar, de cada patrón del CSV se deriva mecánicamente (árbol de parseo
# del MISMO patrón → fuente única, cero drift con la tabla) un LITERAL
# OBLIGATORIO: una secuencia que cualquier match debe contener. Etapa 1:
# `literal in linea.lower()` (substring en C); etapa 2: el loop existente,
# intacto, solo si la etapa 1 dispara. Un patrón que no aporte literal
# ≥ _MIN_LIT queda en chequeo incondicional (robusto; hoy: 0 de 87).
# Garantía (match ⟹ literal presente) por construcción del árbol: solo
# aportan los runs de LITERAL obligatorios (no los opcionales, min=0); un
# BRANCH aporta solo si TODAS sus ramas aportan (la unión de sus literales).
# Los patrones del CSV son minúscula pura y compilan re.I; la línea se
# compara en .lower() (equivalente en el alfabeto en juego: ASCII + áéíóúñü).
try:
    from re import _parser as _re_parser          # Python >= 3.11, sin warning
except ImportError:                                # pragma: no cover
    import sre_parse as _re_parser                 # fallback legacy

_MIN_LIT = 4

def _literales_obligatorios(patron):
    """Set de literales tal que match(patron) ⟹ algún literal es substring
    de texto.lower(); None si el patrón no garantiza ninguno (≥ _MIN_LIT)."""
    def walk(seq):
        candidatos = []   # cada candidato: set de alternativas obligatorias
        run = ""
        def flush():
            nonlocal run
            if len(run) >= _MIN_LIT:
                candidatos.append({run})
            run = ""
        for op, av in seq:
            nombre_op = str(op)
            if nombre_op == "LITERAL":
                run += chr(av).lower()
            elif nombre_op == "BRANCH":
                flush()
                ramas = []
                for r in av[1]:
                    s = walk(r)
                    if s is None:
                        ramas = None
                        break
                    ramas.append(s)
                if ramas is not None:
                    union = set()
                    for s in ramas:
                        union |= s
                    candidatos.append(union)
            elif nombre_op == "SUBPATTERN":
                flush()
                s = walk(av[3])
                if s is not None:
                    candidatos.append(s)
            elif nombre_op in ("MAX_REPEAT", "MIN_REPEAT"):
                flush()
                if av[0] >= 1:          # repetición obligatoria (min >= 1)
                    s = walk(av[2])
                    if s is not None:
                        candidatos.append(s)
                # min == 0 → subpatrón opcional: no garantiza nada
            else:
                flush()                 # IN/ANY/AT/... rompen el run literal
        flush()
        if not candidatos:
            return None
        # el más selectivo: maximiza el largo del literal más corto del set,
        # a igualdad el de mayor largo promedio
        return max(candidatos,
                   key=lambda s: (min(len(x) for x in s),
                                  sum(len(x) for x in s) / len(s)))
    return walk(_re_parser.parse(patron, re.I))

def _construir_prefiltro_jueces(jueces):
    literales, sin_literal = set(), []
    for pat, _nombre in jueces:
        lits = _literales_obligatorios(pat.pattern)
        if lits is None:
            sin_literal.append(pat)
        else:
            literales |= lits
    return tuple(sorted(literales)), tuple(sin_literal)

_LITS_JUECES, _JUECES_SIN_LITERAL = _construir_prefiltro_jueces(JUECES_CONOCIDOS)

def hay_juez_conocido(texto):
    """Equivale a any(p.search(texto) for p, _ in JUECES_CONOCIDOS), con el
    prefiltro M52 adelante. Fuente única de la pregunta «¿hay algún juez
    acá?» — los sitios que EXTRAEN el nombre siguen iterando la tabla."""
    t = texto.lower()
    if not any(lit in t for lit in _LITS_JUECES):
        # sin literal presente, solo pueden matchear los patrones sin garantía
        return any(p.search(texto) for p in _JUECES_SIN_LITERAL)
    return any(p.search(texto) for p, _ in JUECES_CONOCIDOS)

# Ruido OCR (segmentos que no son nombres). Incluimos apellidos de jueces
# para que no se cuenten como "desconocidos" cuando aparecen en otros contextos.
RUIDO_FIRMA = {
    "buenos aires", "vistos", "considerando", "por ello", "notifíquese",
    "archívese", "fdo", "ante mí", "ante mi", "rosenkrantz —",
    "lorenzetti", "rosatti", "maqueda", "highton",
    "petracchi", "zaffaroni", "argibay", "fayt", "boggiano",
    "belluscio", "lópez", "vázquez", "nazareno",
}

# ── Calificadores ─────────────────────────────────────────────────────────────

RE_CALIFICADOR = re.compile(
    r"\(\s*(en\s+disidencia|seg[úu]n\s+su\s+voto|por\s+su\s+voto)"
    r"(\s+parcial)?\s*\)",
    re.I
)

# ── Búsqueda de case_name ─────────────────────────────────────────────────────

def find_case_name(lines, apertura_idx, max_back=15, max_back_fallback=60):
    for d in range(1, max_back + 1):
        idx = apertura_idx - d
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if not candidate or RE_PAGE_HEADER.match(candidate):
            continue
        if "c/" in candidate:
            return candidate
    for d in range(1, max_back_fallback + 1):
        idx = apertura_idx - d
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if not candidate or RE_PAGE_HEADER.match(candidate):
            continue
        if "c/" in candidate or "s/" in candidate:
            return candidate
    return ""

# ── Tribunal de origen ────────────────────────────────────────────────────────

# v11: ampliar marcadores. "Tribunal de origen" es el único frecuente en el
# corpus auditado (tomo 329 = 156 ocurrencias), pero los otros tres se agregan
# preventivamente para tomos donde el formato pueda variar.
# "Tribunales que intervinieron con anterioridad" NO se incluye como marcador
# de tribunal de origen porque introduce instancias INFERIORES intermedias,
# no la instancia recurrida; pero su presencia se usa en la detección
# positiva de is_originaria como señal de NO-originario.
RE_TRIB_ORIG = re.compile(
    r"^(?:Tribunal|Juzgado|C[áa]mara)\s+de\s+origen\s*:\s*(.*)$",
    re.I,
)
RE_TRIB_INTERVINIENTE = re.compile(
    r"^Tribunales?\s+que\s+intervin",
    re.I,
)

def _parece_caratula(s):
    """B114 (H111): True si la línea parece carátula/sumario y NO continuación
    del nombre de un tribunal. Heurística por proporción: ≥60% de los tokens
    alfabéticos largos (>2 chars) en MAYÚSCULAS. Atrapa carátulas con conectores
    en minúscula ('MARIA EUGENIA CIRILO y Otro' → 3/4) que un test all-caps puro
    (s == s.upper()) dejaba pasar; no toca continuaciones reales del nombre
    ('Administrativo Federal', 'Mendoza', 'Provincia de Buenos Aires' → 0)."""
    toks = [t for t in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", s) if len(t) > 2]
    if not toks:
        return False
    return sum(1 for t in toks if t == t.upper()) / len(toks) >= 0.6


def find_tribunal_origen(lines, idx_inicio, idx_fin):
    """
    v12 (B114, H111): el nombre del tribunal de origen viene partido por el corte
    de línea del OCR. Dos sub-patrones: (a) intra-palabra, el valor termina en
    guión/soft-hyphen ('…Contencioso Admi-' / '…Administra\xad') y la continuación
    arranca en minúscula ('nistrativo Federal, Sala IV.'); (b) inter-palabra, el
    valor corta en una preposición sin guión ('…en lo Contencioso ') y la
    continuación arranca en mayúscula ('Administrativo Federal.'). La regla v11
    ('unir si la siguiente empieza en minúscula y NO termina en ".") fallaba en
    los dos: la continuación legítima del NOMBRE casi siempre cierra en '.', y la
    inter-palabra arranca en mayúscula. v12: unir líneas siguientes hasta la que
    cierra en '.', parando antes en breaks estructurales (vacío, running-head,
    'Tribunal(es) que…', 'Intervino…', 'Ministerio…', 'Recurso…', carátula);
    _unhyphenate al final colapsa el corte intra-palabra ('Admi- nistrativo' →
    'Administrativo'). Seguro contra separadores legítimos ('La Plata - Sala II':
    espacio antes del guión, no matchea \\w-). Invariante: los nombres que ya
    cierran en '.' en su primera línea no entran al bloque → quedan idénticos.

    v11 (preservado): si el marcador está vacío ('Tribunal de origen:' sin
    contenido en la misma línea), el contenido está en la línea siguiente.
    """
    tope = min(idx_fin, len(lines))
    for k in range(idx_inicio, tope):
        m = RE_TRIB_ORIG.match(lines[k].strip())
        if not m:
            continue
        tribunal = m.group(1).strip()
        base = k
        # v11: marcador suelto → el nombre arranca en la línea siguiente.
        if not tribunal and k + 1 < tope:
            next_line = lines[k + 1].strip()
            if next_line and not RE_PAGE_HEADER.match(next_line):
                tribunal = next_line
                base = k + 1
        # v12: traer la continuación del nombre partido por OCR.
        if not tribunal.endswith("."):
            k2 = base + 1
            unidas = 0
            while k2 < tope and unidas < 2:
                next_line = lines[k2].strip()
                if (not next_line
                        or RE_PAGE_HEADER.match(next_line)
                        or RE_TRIB_INTERVINIENTE.match(next_line)
                        or next_line.startswith(("Tribunal", "Juzgado", "Intervino",
                                                 "Ministerio", "Recurso"))
                        or _parece_caratula(next_line)):
                    break
                tribunal += " " + next_line
                unidas += 1
                if next_line.endswith("."):
                    break
                k2 += 1
        return _unhyphenate(tribunal).rstrip(".").strip()
    return "SIN_TRIBUNAL_ORIGEN"

def hay_tribunal_interviniente(lines, idx_inicio, idx_fin):
    """v11: señal auxiliar — el caso vino de instancias inferiores."""
    for k in range(idx_inicio, min(idx_fin, len(lines))):
        if RE_TRIB_INTERVINIENTE.match(lines[k].strip()):
            return True
    return False

# ── Firma: collect_firma_lines + parse_firma ──────────────────────────────────

_RE_FIRMA_COMPLETA = re.compile(
    r"(?:rosatti|rosenkrantz|lorenzetti|maqueda|highton(?:\s+de\s+nolasco)?|nolasco|garc.a.mansilla|mansilla|zaffaroni|petracchi|argibay|fayt|boggiano|belluscio|l.pez|v.zquez|nazareno|rodr.guez\s+basavilbaso|basavilbaso|otero|cavallo|borinsky|catania|gemignani|petrone|ledesma|barroetave.a|hornos|leal\s+de\s+ibarra|catucci|cattucci|riggi|yacobucci|figueroa|mahiques|najurieta|alcal.a?|mor[áa]n|tyden(?:\s+de\s+skanata)?|skanata|poclava\s+lafuente|lafuente|pereyra\s+gonz.lez|ferro|pacilio|arga.araz|mill\s+de\s+pereyra|garc.a\s+lema|rabbi.baldi\s+cabanillas|m[ée]ndez|montesi|cossio|p[ée]rez\s+petit|romano|petra\s+fern.ndez|chausovsky|schiffrin|aguilar|p[ée]rez\s+tognola|corcuera|andalaf(?:\s+casiello)?|fern.ndez\s+g[óo]mez)"
    r"(?:\s*\((?:en\s+disidencia|seg[uú]n\s+su\s+voto)(?:\s+parcial)?\))?\s*\.\s*$",
    re.I
)

def collect_firma_lines(bloque, idx_start, max_lines=None):
    """Junta lineas de firma. H042 fix B055 v3.

    - Techo = len(bloque) (bloque acotado por catalogo/mapa).
    - Guarda: cuando texto acumulado termina en apellido conocido
      + calificador opcional + punto -> firma podria estar completa
      -> aplicar guarda estricta. Si no -> seguir con breaks.
    - Tolera 1 linea vacia intercalada si la siguiente parece firma.
    """
    techo = len(bloque) if max_lines is None else min(idx_start + max_lines, len(bloque))
    firma_lines = []
    started = False

    def es_continuacion_firma(s):
        if hay_juez_conocido(s):
            return True
        if "—" in s or " - " in s or "–" in s:
            return True
        if RE_CALIFICADOR.search(s):
            return True
        return False

    for k in range(idx_start, techo):
        line = bloque[k].strip()
        if not line:
            if started:
                next_firma = False
                for j in range(k + 1, min(k + 3, techo)):
                    nxt = bloque[j].strip()
                    if not nxt:
                        continue
                    if es_continuacion_firma(nxt):
                        next_firma = True
                    break
                if next_firma:
                    continue
                break
            continue
        if not started:
            if hay_juez_conocido(line):
                started = True
                firma_lines.append(line)
            continue
        # Breaks estructurales
        if RE_PAGE_HEADER.match(line) or line.startswith("Recurso de"):
            break
        if RE_VOTO_HDR.match(line) or RE_DISID_HDR.match(line):
            break
        if line.startswith("Tribunal de origen") or line.startswith("Tribunal que"):
            break
        # Guarda: texto acumulado termina en apellido conocido + punto?
        firma_so_far = " ".join(firma_lines)
        if _RE_FIRMA_COMPLETA.search(firma_so_far):
            if not es_continuacion_firma(line):
                break
        firma_lines.append(line)
    return " ".join(firma_lines)

def parse_firma(firma_raw):
    """Parsea firma multi-línea: detecta jueces conocidos y calificadores.

    v10 fix: la asignación de calificador busca el calificador entre
    el nombre del juez y el siguiente nombre/separador, no en una ventana
    fija de 80 caracteres. Esto evita asignar mal el calificador cuando
    aparece junto a un juez intermedio en una firma como
    'Rosatti — Rosenkrantz (según su voto) — Lorenzetti'.
    """
    jueces_out = []
    desconocidos = []
    voting_pattern = "unanime"
    has_voto    = False
    has_disid   = False

    # 1. Encontrar todas las ocurrencias de jueces y sus posiciones
    matches = []
    for pat, nombre in JUECES_CONOCIDOS:
        for m in pat.finditer(firma_raw):
            matches.append((m.start(), m.end(), nombre))
    # Ordenar por posición y eliminar overlaps (preferir el primer match)
    matches.sort()
    matches_dedup = []
    last_end = -1
    for ini, fin, nombre in matches:
        if ini < last_end:
            continue
        matches_dedup.append((ini, fin, nombre))
        last_end = fin

    # 2. Para cada juez, buscar calificador SOLO entre su fin y el siguiente inicio
    for i, (ini, fin, nombre) in enumerate(matches_dedup):
        if i + 1 < len(matches_dedup):
            limite_busqueda = matches_dedup[i + 1][0]
        else:
            limite_busqueda = len(firma_raw)
        ventana = firma_raw[fin:limite_busqueda]
        cm = RE_CALIFICADOR.search(ventana)
        calificador = None
        if cm:
            cal_text = cm.group(1).lower()
            if "disidencia" in cal_text:
                calificador = "en disidencia"
                has_disid   = True
            elif "seg" in cal_text:
                calificador = "según su voto"
                has_voto    = True
            elif "por" in cal_text:
                calificador = "por su voto"
                has_voto    = True
        jueces_out.append({
            "nombre":      nombre,
            "calificador": calificador,
            "conocido":    True,
        })

    # 3. Ruido / desconocidos: segmentos que parecen nombres pero no matchearon
    nombres_jueces = {j["nombre"].split(" (")[0].lower() for j in jueces_out}
    for token in re.findall(r"[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\.\-]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\.\-]+){1,3}", firma_raw):
        token_l = token.lower()
        if any(r in token_l for r in RUIDO_FIRMA):
            continue
        if any(j in token_l for j in nombres_jueces):
            continue
        if len(token) < 6:
            continue
        desconocidos.append(token)

    if has_voto and has_disid:
        voting_pattern = "mixed"
    elif has_voto:
        voting_pattern = "segun_su_voto"
    elif has_disid:
        voting_pattern = "disidencia"
    elif jueces_out:
        voting_pattern = "unanime"
    else:
        voting_pattern = "sin_firma"

    return {
        "jueces":         jueces_out,
        "voting_pattern": voting_pattern,
        "desconocidos":   desconocidos,
    }

# ── NUEVO v10: extraer texto del considerando + texto de cada voto individual ─

def extraer_considerando(bloque, por_ello_idx, lineas_dictamen):
    """
    Extrae el texto del considerando: desde 'Considerando' hasta 'Por ello'.
    Excluye líneas que forman parte del dictamen embebido.
    Returns: string con texto unificado.
    """
    inicio_cons = None
    for k, ln in enumerate(bloque):
        if k in lineas_dictamen:
            continue
        # B010 guard: match después del dispositivo no es el considerando
        # del fallo — es de un voto individual o del caso siguiente.
        if por_ello_idx is not None and k >= por_ello_idx:
            break
        if RE_CONSIDERANDO.search(ln.strip()):
            inicio_cons = k
            break
    if inicio_cons is None:
        # Fallback: a veces no hay marcador "Considerando:" explícito,
        # pero el considerando empieza igual. Tomamos desde apertura hasta
        # por_ello_idx como aproximación.
        inicio_cons = 0
    fin_cons = por_ello_idx if por_ello_idx is not None else len(bloque)
    lineas = [bloque[k].strip() for k in range(inicio_cons, fin_cons)
              if k not in lineas_dictamen]
    return " ".join([ln for ln in lineas if ln])

def extraer_textos_votos(bloque, posiciones_marcadores):
    """
    Para cada voto/disidencia individual, extrae el texto del bloque.
    posiciones_marcadores: lista de (k_inicio, juez_nombre, tipo)
        donde tipo ∈ {'voto', 'disidencia'}
    Returns: dict {juez_nombre: texto_voto}
    """
    resultado = {}
    if not posiciones_marcadores:
        return resultado
    # Ordenar por línea de inicio
    marcadores = sorted(posiciones_marcadores, key=lambda x: x[0])
    for i, (k_ini, juez, tipo) in enumerate(marcadores):
        # Fin: línea de inicio del próximo marcador, o fin del bloque
        if i + 1 < len(marcadores):
            k_fin = marcadores[i + 1][0]
        else:
            k_fin = len(bloque)
        # Extraer texto entre k_ini+1 y k_fin (el k_ini es el header del voto)
        texto = " ".join([bloque[k].strip() for k in range(k_ini, k_fin)
                          if bloque[k].strip()])
        resultado[juez] = texto
    return resultado

def detectar_juez_en_voto_header(linea):
    """
    Dado un header como 'Voto del Señor Ministro Doctor Don Ricardo Luis
    Lorenzetti', detecta cuál juez es. Devuelve None si no matchea.
    """
    for pat, nombre in JUECES_CONOCIDOS:
        if pat.search(linea):
            return nombre
    return None

def detectar_votos_disidencias(bloque, lineas_excluir):
    """
    Recorre el bloque buscando headers de votos y disidencias individuales.

    Devuelve (n_votos_svoto, n_disidencias, inicio_votos_indiv, marcadores_votos):
      n_votos_svoto      cantidad de headers "Voto del ..."
      n_disidencias      cantidad de headers "Disidencia (parcial) del ..."
      inicio_votos_indiv índice (en el bloque) del primer header individual, o None
      marcadores_votos   lista [(k, juez, tipo), ...] con el juez detectado por header

    lineas_excluir: índices del bloque fuera de zona de fallo (máscara M09:
    dictamen, residuo_caso_anterior, sumario, epílogo, header_pagina) que se
    saltan para no contar headers espurios. El juez se busca en el propio header
    y, si no aparece, en hasta 3 líneas siguientes (saltando vacías, cortando en
    "Considerando:").
    """
    n_votos_svoto      = 0
    n_disidencias      = 0
    inicio_votos_indiv = None
    marcadores_votos   = []

    for k, bl in enumerate(bloque):
        stripped = bl.strip()
        if not stripped:
            continue

        # M09: saltar líneas fuera de zona de fallo (dictamen,
        # residuo_caso_anterior, sumario, epilogo, header_pagina).
        if k in lineas_excluir:
            continue

        if RE_VOTO_HDR.match(stripped) or RE_DISID_HDR.match(stripped):
            tipo = "voto" if RE_VOTO_HDR.match(stripped) else "disidencia"
            if tipo == "voto":
                n_votos_svoto += 1
            else:
                n_disidencias += 1
            if inicio_votos_indiv is None:
                inicio_votos_indiv = k
            header_completo = stripped
            for offset in range(1, 4):
                juez = detectar_juez_en_voto_header(header_completo)
                if juez:
                    marcadores_votos.append((k, juez, tipo))
                    break
                if k + offset < len(bloque):
                    sig = bloque[k + offset].strip()
                    if not sig:
                        continue
                    if RE_CONSIDERANDO.search(sig):
                        break
                    header_completo += " " + sig
            continue

    return n_votos_svoto, n_disidencias, inicio_votos_indiv, marcadores_votos

# ── NUEVO v11: detección positiva de competencia originaria ──────────────────

# Señales internas en el cuerpo del fallo
RE_COMPETENCIA_ORIGINARIA = re.compile(
    r"competencia\s+originaria\s+(de\s+(esta\s+)?Corte|del\s+Tribunal|de\s+la\s+Corte\s+Suprema)",
    re.I,
)
RE_ART_117_CN = re.compile(
    r"(?:art\.?|art[íi]culos?)\s*117\s+(de\s+la\s+)?Constituci[óo]n\s+Nacional",
    re.I,
)
# "en forma originaria", "instancia originaria", "originariamente"
RE_FORMA_ORIGINARIA = re.compile(
    r"\b(en\s+forma\s+originaria|instancia\s+originaria|originariamente\s+ante)\b",
    re.I,
)

# Señales en case_name
# - "Originario" con O mayúscula (encabezados tipo "M. 466. XXIV. Originario")
RE_CN_ORIGINARIO = re.compile(r"\bOriginario\b")
# - patrón de demanda contra provincia o Estado Nacional (heurística amplia)
# B135(c) (H181): + forma INVERTIDA canónica de Fallos «X c/ Entre Ríos,
# Provincia de y otros» / «Coihue S.R.L. c/ Santa Cruz, Provincia de s/ ...»
# (verificada en 329_p3403 L191 y 344_p3476 L499 — 0/2 con la regex previa).
# Con esto la regex DEJA de ser huérfana: la consume la señal 6 de
# es_originaria (señal compuesta, nunca case_name solo — precisión ≈11% H156).
RE_CN_DEMANDA_ESTADO = re.compile(
    r"c/\s+(?:la\s+)?Provincia\s+de\s+|"
    r"c/\s+Estado\s+Nacional|"
    r",\s*Provincia\s+de\s+\w+,?\s+c/|"  # "Buenos Aires, Provincia de, c/"
    r"Provincia\s+de\s+\w+\s+c/|"
    r"c/\s*[^,/]{1,80},\s*Provincia\s+de\b",  # invertida (B135c/H181)
    re.I,
)

# ── B135 (H172): 5ª señal — «competencia originaria» pelada, con guards ──────
# La cola de RE_COMPETENCIA_ORIGINARIA («de esta Corte/del Tribunal/de la Corte
# Suprema») pierde los holdings sin cola («mantener su / asume su competencia
# originaria para dictar sentencia definitiva», «este juicio corresponde a la
# competencia originaria prevista en los artículos 116 y 117…»). Señal pelada
# medida corpus-wide (poc_b135_flips v0.1→v0.3, anclas A1-A6 [OK]): flip-set
# 43 = 39 TP + 4 FP-F5 aceptados (historia procesal narrada / doctrina:
# 349_p163, 347_p2146, 347_p2286 Ferrari-Levinas, 334_p1842 — 0,07%).
# Guards POR-MATCH, calibrados contra FP leídos; NO tocan las 4 señales previas:
#   local      — cita CIDH «competencia originaria local» (Barreto Leiva:
#                337_p901=Duarte, 342_p2389)
#   apelada    — aside doctrinal «originaria o apelada» (339_p1254)
#   precedente — precedente citado «…originaria en la causa “X”» (345_p220)
#   provincial — tribunal/constitución provincial en ventana previa W=120
#                (329_p6072 TSJ Neuquén, 330_p76 Constitución del Chaco)
# Ensanche de RE_ART_117_CN a «116 y 117»: medido y RECHAZADO (0 TP / 1 FP
# marginal, 348_p841).
RE_ORIG_PELADA = re.compile(r"competencia\s+originaria", re.I)
RE_ORIG_G_LOCAL      = re.compile(r"^\s*local\b", re.I)
RE_ORIG_G_APELADA    = re.compile(r"^\s+o\s+apelada\b", re.I)
RE_ORIG_G_PRECEDENTE = re.compile(r"^\s+en\s+la\s+causa\b", re.I)
RE_ORIG_G_PROVINCIAL = re.compile(
    r"Superior\s+de\s+Justicia|Superior\s+Tribunal|Tribunal\s+Superior|"
    r"Suprema\s+Corte\s+de|Constituci[óo]n\s+de\s+la\s+Provincia|"
    r"Constituci[óo]n\s+provincial", re.I)
_ORIG_W_PROV = 120


def _orig_pelada_con_guards(cuerpo):
    """B135 (H172): True si algún match de la señal pelada sobrevive a los
    guards por-match (calibración en el comentario de arriba)."""
    for m in RE_ORIG_PELADA.finditer(cuerpo):
        post = cuerpo[m.end():]
        pre = cuerpo[max(0, m.start() - _ORIG_W_PROV):m.start()]
        if RE_ORIG_G_LOCAL.search(post):
            continue
        if RE_ORIG_G_APELADA.search(post):
            continue
        if RE_ORIG_G_PRECEDENTE.search(post):
            continue
        if RE_ORIG_G_PROVINCIAL.search(pre):
            continue
        return True
    return False


def _ventana_resulta(bloque):
    """B135(c) (H181): ventana RESULTA = bloque[apertura(RE_VISTOS) → primer
    RE_CONSIDERANDO). None si falta cualquiera de las dos anclas (conservador:
    sin ventana no hay señal). VERBATIM de poc_b135c v0.1 — mismo código =
    misma ventana = el flip-set medido en disco (6 = 6 TP adjudicados) vale."""
    ap = None
    for i, ln in enumerate(bloque):
        if RE_VISTOS.match(ln):
            ap = i
            break
    if ap is None:
        return None
    for j in range(ap + 1, len(bloque)):
        if RE_CONSIDERANDO.search(bloque[j].strip()):
            return bloque[ap:j]
    return None


def es_originaria(case_name, considerando_text, por_ello_text, bloque=None):
    """
    v11: detección positiva de competencia originaria. B135 (H172): +señal 5
    y mask del banner antes del des-guionado. B135(c) (H181): +señal 6
    compuesta (case_name demanda-contra-Estado/Provincia ∧ pelada-con-guards
    sobre la ventana Resulta).

    Criterio AMPLIO: incluye fallos donde la Corte declina la competencia
    originaria (porque el caso fue presentado como originario, aunque la Corte
    rechace). Decisión metodológica del usuario.

    Retorna True si CUALQUIERA de estas señales aparece:
      1. "competencia originaria de esta Corte" en el texto del fallo
      2. Referencia al art. 117 CN en el texto
      3. "Originario" como marcador en el case_name
      4. Forma originaria mencionada
      5. "competencia originaria" pelada con guards por-match (B135, H172)

    El case_name tipo demanda-contra-Estado sigue sin usarse solo (precisión
    ≈11%, H156) — señal compuesta = B135(c), pendiente.
    """
    # B135(b) (H172): enmascarar el running-head ANTES del des-guionado — el
    # banner intercalado parte la señal («competencia origi- [5117 DE JUSTICIA
    # DE LA NACIÓN 329] naria», 337_p234 Credicoop) y _unhyphenate une el guión
    # con el NÚMERO de página (\w matchea dígitos), no con «naria». Patrón H137
    # (_barrer) aplicado localmente. Miss por guionado corpus-wide medido = 1.
    cuerpo = (considerando_text or "") + " " + (por_ello_text or "")
    cuerpo = RE_RUNNING_HEAD.sub(" ", cuerpo)
    cuerpo = _unhyphenate(cuerpo)

    # Señal fuerte 1: competencia originaria mencionada explícitamente
    if RE_COMPETENCIA_ORIGINARIA.search(cuerpo):
        return True
    # Señal fuerte 2: art. 117 CN
    if RE_ART_117_CN.search(cuerpo):
        return True
    # Señal fuerte 3: "Originario" en case_name (encabezado oficial del expediente)
    if case_name and RE_CN_ORIGINARIO.search(case_name):
        return True
    # Señal fuerte 4: forma originaria mencionada
    if RE_FORMA_ORIGINARIA.search(cuerpo):
        return True
    # Señal 5 (B135/H172): pelada con guards por-match
    if _orig_pelada_con_guards(cuerpo):
        return True
    # Señal 6 (B135(c), H181): COMPUESTA — case_name demanda-contra-Estado/
    # Provincia (RE_CN_DEMANDA_ESTADO ensanchada, incl. forma invertida) ∧
    # pelada-con-guards (reusada intacta) sobre la ventana RESULTA, donde vive
    # la declaración de competencia que considerando+por_ello no traen
    # («A fs. 380 esta Corte asume su competencia originaria», 329_p3403 L335;
    # «a fs. 90/91, esta Corte declara su competencia originaria», 344_p3476
    # L607). NUNCA case_name solo (≈11% precisión, H156): de un pool de 326
    # case_name-candidatos, la corroboración deja pasar 6 — todos TP
    # adjudicados por lectura (poc_b135c v0.1, H181). Ruta D (dispositivo)
    # evaluada y DESCARTADA: su único testigo (348_p473) era fila fantasma
    # (slice de 348_p461, ya orig=1/merit=1 — familia B012/B045).
    if bloque is not None and case_name and RE_CN_DEMANDA_ESTADO.search(case_name):
        ventana = _ventana_resulta(bloque)
        if ventana is not None:
            w = RE_RUNNING_HEAD.sub(" ", " ".join(ventana))
            w = _unhyphenate(w)
            if _orig_pelada_con_guards(w):
                return True
    return False

# ── NUEVO v12: clasificación de votos individuales ────────────────────────
# ── Tipo B: art. 280 CPCCN ────────────────────────────────────────────────────
# Señal definitoria: mención al art. 280 como base del rechazo. La regex
# original del parser (RE_280_LIBRE) requiere la apertura de paréntesis,
# pero en algunos votos individuales falta; ampliamos para tolerar las dos
# formas. El umbral de wc_voto se calibra desde los ejemplos 1 y 2 (89 y 55
# palabras): empíricamente los rechazos formulaicos están por debajo de 200
# palabras. El requisito is_merit_decision=0 es informativo, no duro: en
# fallos donde la mayoría rechaza por 280 pero algún ministro firma por su
# voto sin más, is_merit del caso será 0.

RE_TIPO_B_280 = re.compile(
    r"(?:art\.?|art[íi]culo)\s*280\s+del\s+C[óo]digo\s+Procesal",
    re.I,
)

# Variantes residuales: "art. 280", "art. 280 CPCCN" sin "del Código Procesal"
RE_TIPO_B_280_ABREV = re.compile(
    r"\b(?:art\.?|art[íi]culo)\s*280\b(?!\s+del\s+r[ée]gimen)",
    re.I,
)

# ── Tipo C: adhesión parcial con divergencia desde considerando N ────────────
# Señales arquetípicas extraídas del Ejemplo 5 (Lorenzetti, "coincide con el
# del voto de la mayoría con exclusión del considerando 4°") y del Ejemplo 6
# (Argibay, "coincide con los considerandos 1° y 2° del voto de la mayoría.
# 3°) Que..."). Dos patrones complementarios:
#
#   (a) "exclusión del considerando N"  / "excepción del considerando N"
#       Modelo: voto coincide con TODO menos un considerando explícito.
#       El considerando N se redacta a continuación de manera divergente.
#
#   (b) "coincide con los considerandos N1 y N2"  (sin "exclusión")
#       Modelo: voto adhiere hasta cierto punto y de ahí en más redacta
#       considerandos propios. El primer considerando NO citado es el
#       punto de divergencia. En el Ejemplo 6 cita "1° y 2°" y la
#       divergencia empieza en el 3°.

# Patrón (a) — exclusión / excepción explícita
RE_TIPO_C_EXCLUSION = re.compile(
    r"(coincide|comparte|adhiere|concuerda)\b"
    r".{0,80}?"
    r"(con\s+(?:la\s+)?(?:exclusi[óo]n|excepci[óo]n)\s+del?\s+"
    r"considerando\s+(\d+)\s*[°ºª]?)",
    re.I | re.DOTALL,
)

# Patrón (b) — adhesión hasta considerando N (inclusivo)
# Captura "coincide con los considerandos 1°, 2° y 3°" o "1° y 2°".
# El número capturado es el ÚLTIMO considerando adherido; la divergencia
# empieza en N+1. Construido para tolerar enumeraciones cortas.
RE_TIPO_C_HASTA = re.compile(
    r"(coincide|comparte|adhiere|concuerda)\b"
    r".{0,40}?"
    r"con\s+(?:los\s+)?considerandos?\s+"
    r"((?:\d+\s*[°ºª]?\s*[,y]?\s*)+)",
    re.I | re.DOTALL,
)

# Patrón (c) — variante "adhiere hasta el considerando N"
RE_TIPO_C_ADHIERE_HASTA = re.compile(
    r"(adhiere|coincide|comparte)\b"
    r".{0,40}?"
    r"hasta\s+el\s+considerando\s+(\d+)\s*[°ºª]?",
    re.I | re.DOTALL,
)

# ── Tipo A: remisión al dictamen del Procurador ──────────────────────────────
# Variantes empíricas, ordenadas por frecuencia esperada. Construidas para
# distinguir A puro (la remisión es el único o el principal fundamento) de
# A mixto (remisión al dictamen sobre algunos puntos + argumentos propios
# sobre otros). El Ejemplo 4 (Lorenzetti+Argibay) es A mixto: remite al
# dictamen para reseñar las cuestiones (acápites I, II y III) y luego
# argumenta sobre el fondo apoyándose en un precedente. Para nuestro
# clasificador AMBOS son tipo A — la subcategoría puro/mixto se puede
# inferir post-hoc desde wc_voto y desde la presencia de "Fallos:" pero no
# afecta la clasificación principal.

# Patrón principal: remisión explícita al dictamen como fundamento
RE_TIPO_A_REMISION_DICTAMEN = re.compile(
    r"(?:"
        # "por los fundamentos [y conclusiones] del dictamen"
        r"por\s+los\s+fundamentos\s+(?:y\s+conc[lu]+siones\s+)?"
            r"(?:expuestos\s+en\s+el\s+|del\s+)?dictamen"
        r"|"
        # "de conformidad con lo dictaminado"
        r"de\s+conformidad\s+con\s+lo\s+dictamin"
        r"|"
        # "se remite al dictamen" / "cabe remitirse al dictamen"
        r"(?:se\s+remite|cabe\s+remitirse|corresponde\s+remitir(?:se)?)\s+"
            r"(?:a\s+(?:los\s+)?(?:fundamentos\s+(?:y\s+conclusiones\s+)?"
            r"(?:expuestos\s+(?:en\s+el\s+)?|del\s+)?)?dictamen|al\s+dictamen)"
        r"|"
        # "comparte / comparten los fundamentos [y conclusiones] del dictamen"
        r"comparte[ns]?\s+(?:los\s+)?fundamentos\s+"
            r"(?:y\s+conc[lu]+siones\s+)?(?:expuestos\s+(?:en\s+el\s+)?|del\s+)?dictamen"
        r"|"
        # "concuerda / concuerdan con el dictamen"
        r"concuerd[ao]n?\s+(?:sustancialmente\s+)?con\s+(?:lo\s+expuesto\s+en\s+)?"
            r"(?:el\s+)?dictamen"
        r"|"
        # "al [que/cual] cabe remitir(se)" — referencia anafórica al dictamen
        # Sólo válida si "dictamen" aparece en una ventana corta previa,
        # condición que se chequea en el código.
        r"al\s+(?:que|cual)\s+cabe\s+remitir(?:se)?"
    r")",
    re.I | re.DOTALL,
)

# Para detectar A "anafórico" (Ejemplo 4: "...reseñados apropiadamente en
# el dictamen del señor Procurador Fiscal subrogante (acápites I, II y III),
# al que cabe remitirse..."), validamos que la palabra "dictamen" aparezca
# en una ventana de 200 caracteres previa al match anafórico.
RE_DICTAMEN_MENCION = re.compile(r"\bdictamen\b", re.I)

# ── Tipo E: remisión a voto propio anterior o a precedente ──────────────────
# Señales: cita de "Fallos: NNN:NNN" como fundamento principal, o frases
# del tipo "resulta aplicable lo resuelto en la causa", "remite a los
# fundamentos de su voto en", "criterio sostenido en". El Ejemplo 3 (Fayt)
# es el arquetipo: "Que al caso resulta aplicable, en lo pertinente, lo
# resuelto por el Tribunal en la causa 'Verbitsky' (Fallos: 328:1146,
# disidencia parcial del juez Fayt) a cuyos fundamentos y conclusiones
# corresponde remitir en razón de brevedad."
#
# Atención: la cita de "Fallos:" sola NO basta para Tipo E. Casi todos los
# fallos citan precedentes. Lo característico de E es que la cita es el
# fundamento PRINCIPAL del voto: aparece en los primeros considerandos,
# acompañada de fórmulas de remisión ("a cuyos fundamentos corresponde
# remitir", "resulta aplicable lo resuelto"). Distinguimos E "fuerte" (con
# fórmula de remisión + cita) de E "débil" (sólo cita), y sólo el primero
# califica como Tipo E. El segundo cae en otra categoría.

RE_TIPO_E_REMISION_PRECEDENTE = re.compile(
    r"(?:"
        # "resulta aplicable lo resuelto en"
        r"resulta(?:n)?\s+aplicables?\s+(?:al\s+caso\s+)?(?:en\s+lo\s+pertinente,?\s+)?"
            r"(?:lo\s+resuelto|los?\s+(?:argumentos|fundamentos|criterios?))"
        r"|"
        # "a cuyos fundamentos [y conclusiones] corresponde remitir(se)"
        r"a\s+cuyos\s+fundamentos\s+(?:y\s+conclusiones\s+)?"
            r"(?:corresponde|cabe)\s+remitir(?:se)?"
        r"|"
        # "remite a los fundamentos de su voto en"
        r"(?:se\s+)?remite\s+a\s+(?:los\s+fundamentos\s+(?:de\s+su\s+voto|"
            r"expuestos)\s+en|lo\s+resuelto\s+en)"
        r"|"
        # "criterio sostenido en" / "doctrina sentada en"
        r"(?:criterio\s+sostenido|doctrina\s+sentada|conforme\s+lo\s+resuelto)\s+en\s+(?:la\s+)?(?:causa|los\s+autos|Fallos)"
    r")",
    re.I | re.DOTALL,
)

# Cita de "Fallos: NNN:NNN" — se usa como señal corroborante para E
RE_FALLOS_CITA = re.compile(r"\bFallos\s*:\s*\d{2,3}\s*:\s*\d+", re.I)

# ── Tipo D: concurrencia sustantiva independiente ────────────────────────────
# Por descarte: NO matchea ninguna fórmula de adhesión / remisión y exhibe
# la estructura de un voto autónomo (considerandos numerados desde 1°,
# desarrollo extenso). El umbral de 1500 palabras se calibra desde los
# ejemplos 7 (6.026 palabras) y 8 (6.666 palabras) más la asimetría con C
# (los ejemplos 5 y 6 de C tienen 1.398 y 153 palabras). 1500 separa
# razonablemente C de D pero el discriminante real es la presencia/ausencia
# de fórmulas de adhesión, no el wc.

# Detección de "Considerando: 1°)" como inicio de redacción autónoma. Si el
# voto empieza así (o en esa ventana inicial aparece "1°)") es señal de
# estructura D. Tolerante al header del voto que precede.
RE_CONSIDERANDO_NUMERADO_1 = re.compile(
    r"Considerando\s*:\s*1\s*[°ºª]\s*\)",
    re.I,
)

# ── Función principal ─────────────────────────────────────────────────────────

def clasificar_tipo_voto(texto_voto, wc_voto, is_merit_decision):
    """
    Clasifica un voto individual ("según su voto" / "por su voto" /
    disidencia parcial) en uno de los cinco tipos definidos en el marco
    teórico de la tesis.

    Parámetros
    ----------
    texto_voto : str
        Texto del voto tal como lo extrae `extraer_textos_votos` en
        csjnv11.py: una sola línea con el header del voto seguido del
        cuerpo, sin saltos de línea internos.
    wc_voto : int
        Word count del voto (calculado en el loop principal con la regex
        \\b\\w+\\b).
    is_merit_decision : int | bool
        Flag del CASO (desde H178: derivado del gate es_revision_fondo del
        clasificador, fuente única; antes: outcome ∈ MERIT_OUTCOMES). Señal auxiliar.

    Returns
    -------
    dict con tres claves:
        tipo_voto_sep : str    "A" | "B" | "C" | "D" | "E" | "indeterminado"
        fragmenta_ratio : bool | str   True | False | "parcial"
        punto_divergencia : str | None  "considerando N" | "dispositivo" | None
    """
    if not texto_voto or not texto_voto.strip():
        return {
            "tipo_voto_sep":      "indeterminado",
            "fragmenta_ratio":    False,
            "punto_divergencia":  None,
        }

    # Trabajamos sobre los primeros 4000 caracteres para los matchers de
    # adhesión / remisión: las fórmulas características aparecen siempre al
    # inicio del considerando del voto separado. Para Tipo D (estructura
    # completa) sí necesitamos mirar más atrás, pero la decisión D se toma
    # por descarte y se basa en señales globales (wc, ausencia de fórmulas).
    cabeza = texto_voto[:4000]

    # ─ Tipo B — art. 280 ─────────────────────────────────────────────────────
    # Discriminante fuerte: mención al art. 280 como base del rechazo. El
    # umbral de wc <= 250 es generoso (el más largo de los ejemplos B es 89
    # palabras pero el corpus completo puede tener variantes con un párrafo
    # adicional). is_merit_decision=0 es corroborante pero no requerido:
    # ocasionalmente la mayoría decide el fondo y un ministro firma con voto
    # 280 en disidencia parcial.
    if RE_TIPO_B_280.search(cabeza):
        if wc_voto <= 250:
            return {
                "tipo_voto_sep":      "B",
                "fragmenta_ratio":    False,
                "punto_divergencia":  None,
            }
        # Si menciona 280 pero wc es alto, probablemente sea un voto de
        # fondo que cita 280 en otro contexto (raro pero posible). Cae a
        # los siguientes detectores.

    # ─ Tipo C — adhesión parcial con considerando explícito ────────────────
    # Patrón (a): "exclusión / excepción del considerando N"
    m_exc = RE_TIPO_C_EXCLUSION.search(cabeza)
    if m_exc:
        n = m_exc.group(3)
        return {
            "tipo_voto_sep":      "C",
            "fragmenta_ratio":    "parcial",
            "punto_divergencia":  f"considerando {n}",
        }

    # Patrón (c): "adhiere hasta el considerando N" — divergencia en N+1
    m_hasta = RE_TIPO_C_ADHIERE_HASTA.search(cabeza)
    if m_hasta:
        n = int(m_hasta.group(2))
        return {
            "tipo_voto_sep":      "C",
            "fragmenta_ratio":    "parcial",
            "punto_divergencia":  f"considerando {n + 1}",
        }

    # Patrón (b): "coincide con los considerandos N1 y N2..." — divergencia
    # en el primer considerando NO mencionado. Extraemos el último número
    # de la lista citada y la divergencia empieza en último+1.
    m_lista = RE_TIPO_C_HASTA.search(cabeza)
    if m_lista:
        lista_str = m_lista.group(2)
        nums = [int(x) for x in re.findall(r"\d+", lista_str)]
        if nums:
            ultimo = max(nums)
            return {
                "tipo_voto_sep":      "C",
                "fragmenta_ratio":    "parcial",
                "punto_divergencia":  f"considerando {ultimo + 1}",
            }

    # ─ Tipo A — remisión al dictamen ────────────────────────────────────────
    # Match principal: cualquier fórmula de remisión. La rama anafórica ("al
    # que cabe remitirse") se valida adicionalmente: requiere que la palabra
    # "dictamen" aparezca en una ventana de 250 caracteres previa al match,
    # para evitar falsos positivos donde "al que cabe remitirse" se refiere
    # a un precedente y no al dictamen.
    m_a = RE_TIPO_A_REMISION_DICTAMEN.search(cabeza)
    if m_a:
        es_anaforico = m_a.group(0).lower().startswith("al ")
        if es_anaforico:
            inicio = max(0, m_a.start() - 250)
            ventana_previa = cabeza[inicio:m_a.start()]
            if RE_DICTAMEN_MENCION.search(ventana_previa):
                return {
                    "tipo_voto_sep":      "A",
                    "fragmenta_ratio":    False,
                    "punto_divergencia":  None,
                }
            # Sin "dictamen" en la ventana previa: probablemente es remisión
            # a un precedente. Cae a Tipo E.
        else:
            return {
                "tipo_voto_sep":      "A",
                "fragmenta_ratio":    False,
                "punto_divergencia":  None,
            }

    # ─ Tipo E — remisión a voto propio anterior o a precedente ─────────────
    # Requiere una fórmula de remisión Y la presencia de una cita "Fallos:"
    # (o de la palabra "causa" en la ventana). La cita "Fallos:" sola es
    # demasiado común — todos los fallos citan precedentes —, y la fórmula
    # sola sin cita podría ser una remisión interna al propio considerando.
    # Pedir ambas condiciones reduce falsos positivos.
    m_e = RE_TIPO_E_REMISION_PRECEDENTE.search(cabeza)
    if m_e:
        # Verificamos que haya una cita de Fallos en una ventana razonable
        # alrededor del match (no necesariamente posterior: el patrón "a
        # cuyos fundamentos corresponde remitir" suele venir DESPUÉS de la
        # cita).
        ventana = cabeza[max(0, m_e.start() - 300):m_e.end() + 300]
        if RE_FALLOS_CITA.search(ventana):
            # Si la ratio del precedente es identificable (siempre lo es
            # cuando hay cita explícita de Fallos), fragmentación parcial.
            return {
                "tipo_voto_sep":      "E",
                "fragmenta_ratio":    "parcial",
                "punto_divergencia":  "dispositivo",
            }
        # Fórmula de remisión sin cita de Fallos: ambiguo. Cae a
        # indeterminado o a D según wc.

    # ─ Tipo D — concurrencia sustantiva independiente ──────────────────────
    # Por descarte: no matchea fórmulas de adhesión ni de remisión. Señales
    # de D:
    #   - wc_voto alto (>= 1500). Calibración: ejemplos 7 y 8 tienen 6026 y
    #     6666 palabras. Umbral conservador para no robarle votos a C y E
    #     que pueden ser largos (Ejemplo 5 de C: 1398 palabras).
    #   - is_merit_decision=1 sube la prior pero no es requisito (puede
    #     haber concurrencias sustantivas en casos no-de-fondo si el voto
    #     desarrolla una doctrina de admisibilidad alternativa).
    #   - "Considerando: 1°)" en la ventana inicial: estructura autónoma.
    es_estructura_autonoma = bool(RE_CONSIDERANDO_NUMERADO_1.search(cabeza))

    if wc_voto >= 1500 and es_estructura_autonoma:
        return {
            "tipo_voto_sep":      "D",
            "fragmenta_ratio":    True,
            "punto_divergencia":  "dispositivo",
        }

    # Caso límite: wc alto pero sin "1°)" detectable — puede ser OCR roto o
    # voto que arranca con un considerando no numerado. Si is_merit_decision=1
    # y wc >= 2500, lo consideramos D igual.
    if is_merit_decision and wc_voto >= 2500:
        return {
            "tipo_voto_sep":      "D",
            "fragmenta_ratio":    True,
            "punto_divergencia":  "dispositivo",
        }

    # ─ Fallback: indeterminado ──────────────────────────────────────────────
    return {
        "tipo_voto_sep":      "indeterminado",
        "fragmenta_ratio":    False,
        "punto_divergencia":  None,
    }

# ── Bloque de un caso ─────────────────────────────────────────────────────────

def construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin):
    """
    v14: dado el archivo (lines) y los límites del fallo (linea_inicio,
    linea_fin) tomados de fallos_localizados.csv, devuelve el bloque
    correspondiente.

    linea_inicio y linea_fin son 0-indexados (igual que en mapa_paginas.csv).
    El bloque incluye linea_fin.
    """
    if linea_fin is None or linea_fin == "":
        linea_fin = len(lines) - 1
    linea_inicio = max(0, int(linea_inicio))
    linea_fin = min(len(lines) - 1, int(linea_fin))
    if linea_inicio > linea_fin:
        return []
    return lines[linea_inicio : linea_fin + 1]


def detectar_apertura_en_bloque(bloque):
    """
    v14: busca el marcador clásico FALLO/SENTENCIA DE LA CORTE SUPREMA dentro
    del bloque. Devuelve (apertura_tipo, apertura_idx_relativo) donde
    apertura_idx_relativo es 0-indexado dentro del bloque, o (None, None) si
    no encuentra marcador.

    El marcador puede estar lejos del inicio del bloque cuando el fallo arranca
    con un dictamen largo del Procurador. Por eso buscamos en todo el bloque.
    RE_APERTURA es estricto (línea exacta = "FALLO DE LA CORTE SUPREMA"), por
    lo que no hay riesgo de matchear menciones del fallo en cuerpo de texto
    o en sumarios editoriales.
    """
    for k, ln in enumerate(bloque):
        m = RE_APERTURA.match(ln.strip())
        if m:
            return (m.group(1).lower(), k)
    return (None, None)


# ── NUEVO v15: detección de fin real del fallo ────────────────────────────────
# Lógica: buscar la frontera con el fallo siguiente usando pistas en cascada
# (carátula del siguiente, header de sumario nuevo, marcador de apertura, firma
# del actual) y búsqueda BIDIRECCIONAL alrededor del linea_fin del catálogo.
# Esto permite detectar correctamente el fin del contenido decisorio cuando:
#   (a) el catálogo extendió demás (bloque cubre múltiples fallos físicos)
#   (b) el catálogo cortó corto (la firma del fallo X cae en la página
#       compartida con el fallo siguiente)

# Header de sumario: línea en MAYÚSCULAS, corta, terminada en : o .
# Ejemplos: "RECURSO EXTRAORDINARIO: Principios generales.", "TRANSPORTE AEREO."
def linea_es_header_sumario(linea):
    s = linea.strip()
    if not s:
        return False
    if len(s) > 150:
        return False
    if not (s.endswith(".") or s.endswith(":") or ":" in s[:80]):
        return False
    primeros_chars = []
    for c in s:
        if c.isalpha():
            primeros_chars.append(c)
            if len(primeros_chars) >= 5:
                break
    if len(primeros_chars) < 5:
        return False
    if not all(c.isupper() for c in primeros_chars):
        return False
    primera_palabra_match = re.match(r"^[A-ZÁÉÍÓÚÑ]+", s)
    primera_palabra = primera_palabra_match.group(0) if primera_palabra_match else ""
    if len(primera_palabra) < 5:
        return False
    return True


# Headers de voto/disidencia que mencionan al juez como inicio (no como firma).
RE_HEADER_VOTO_DISIDENCIA = re.compile(
    r"^\s*(disidencia|voto)\b|"
    r"^\s*(don|do[ñn]a|del\s+(se[ñn]or|se[ñn]ora))\b|"
    r"^\s*(se[ñn]or(es)?|se[ñn]ora(s)?)\s+(ministr|president|vicepresidente|juez|jueza)|"
    r"^\s*la\s+se[ñn]ora\s+|"
    r"^\s*el\s+se[ñn]or\s+",
    re.I
)


# ── B148 (H193): guards del detector de firma — espec poc_b148_flipset v0.3 ──
# Guard nuevo de consumo LOCAL (NO se ensancha RE_HEADER_VOTO_DISIDENCIA: tiene
# segundo consumidor en la clasificacion de frontera). Cubre las atribuciones
# editoriales que el ^ de aquella no tolera: prefijo con guion/parentesis
# («-Disidencia del juez X-», «(Voto del Dr. X)») y cola parentetica
# («…gravedad extrema (Disidencia de la Dra. X).»), en singular/plural y con
# palabra intermedia («Disidencia parcial de», «Disidencias de los»).
RE_ATRIBUCION_SUMARIO = re.compile(
    r"^\s*[(\[\u2013\u2014-]\s*(disidencias?|votos?)\b"
    r"|\((disidencias?|votos?)(\s+\w+)?\s+de",
    re.I,
)

_RE_PAREN_BALANCEADO_FIRMA = re.compile(r"\([^()]*\)")
_CONECTORES_FIRMA = {"don", "dona", "doña", "y", "e"}
_PARTICULAS_NOMBRE_FIRMA = {"de", "del", "la", "los", "las", "di", "da",
                            "van", "von", "der", "den"}
_RE_TOKEN_FIRMA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+\.?")


def _firma_nucleo(s):
    """B148 (H193): normaliza la linea candidata a firma:
      1. quita parentesis BALANCEADOS que NO contienen juez (calificadores y
         apartes, incl. variantes fuera de RE_CALIFICADOR: «según mi voto»,
         «ampliación de fundamentos», soft-hyphen interno). Un parentesis CON
         juez se conserva («(Del voto del Dr. X).» sigue siendo atribucion).
      2. recorta los fragmentos parenteticos WRAPEADOS: prefijo hasta el
         ultimo «)» sin apertura («cia)», «su voto)», «Nombre).») y sufijo
         desde el primer «(» que nunca cierra («(en», «(según su»).
    La adjudicacion H193 midio 579+5 firmas reales que el predicado sin estos
    pasos mataba (clase FRENO v27.0)."""
    t = s
    while True:
        cambio = False
        for m in list(_RE_PAREN_BALANCEADO_FIRMA.finditer(t)):
            if not hay_juez_conocido(m.group(0)):
                t = t[:m.start()] + " " + t[m.end():]
                cambio = True
                break
        if not cambio:
            break
    t = RE_CALIFICADOR.sub(" ", t)
    depth, last_neg = 0, -1
    for i, c in enumerate(t):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth < 0:
                last_neg, depth = i, 0
    core = t[last_neg + 1:] if last_neg >= 0 else t
    depth, first_open = 0, None
    for i, c in enumerate(core):
        if c == "(":
            if depth == 0 and first_open is None:
                first_open = i
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                first_open = None
    if depth > 0 and first_open is not None:
        core = core[:first_open]
    return core


def _firma_residuo_es_prosa(core):
    """B148 (H193): quitados jueces conocidos + calificadores + conectores/
    particulas de nombre, True si el nucleo contiene prosa en minusculas
    (cuerpo denso en nombres: excusaciones/recusaciones/designaciones).
    Nucleo vacio o solo-forma-de-nombre -> False: sigue firma (preserva
    conjueces DESCONOCIDOS, clase B153/v27.1; la enumeracion de nombres
    propios no-jueces sobrevive por diseño -> residuo medido)."""
    r = core
    for pat, _nombre in JUECES_CONOCIDOS:
        r = pat.sub(" ", r)
    r = RE_CALIFICADOR.sub(" ", r)
    for tok in _RE_TOKEN_FIRMA.findall(r):
        base = tok.rstrip(".")
        low = base.lower()
        if low in _CONECTORES_FIRMA or low in _PARTICULAS_NOMBRE_FIRMA:
            continue
        if len(base) >= 2 and base[0].islower():
            return True
    return False


def linea_es_firma_de_juez(linea):
    """
    Una línea es firma de juez si contiene un apellido de JUECES_CONOCIDOS y
    tiene señales típicas de firma (raya, corta, termina en punto), descartando
    headers de voto/disidencia y menciones del juez en cuerpo de texto.
    """
    s = linea.strip()
    if not s or len(s) > 200:
        return False
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False
    if RE_ATRIBUCION_SUMARIO.search(s):
        return False  # B148 (H193): atribucion editorial de sumario
    primera_palabra = s.split()[0].lower() if s.split() else ""
    palabras_cuerpo = {
        "siguiendo", "como", "según", "segun", "que", "el", "la", "los", "las",
        "ya", "esta", "este", "ese", "esa", "ello", "por", "pero", "para",
        "tal", "incluso", "asimismo", "tambien", "también", "no", "si",
        "cuando", "mientras", "aunque", "luego", "después", "despues",
        "afirma", "sostiene", "entiende", "considera", "indicó", "indico",
        "destacó", "destaco", "señaló", "señalo", "concluyó", "concluyo",
    }
    if primera_palabra.rstrip(",;:") in palabras_cuerpo:
        return False
    if not hay_juez_conocido(s):
        return False
    # B148 (H193): el juez debe SOBREVIVIR en el nucleo (fragmentos
    # parenteticos wrapeados recortados) y el residuo no puede ser prosa.
    core = _firma_nucleo(s)
    if not hay_juez_conocido(core):
        return False  # el juez vivia solo en el fragmento -> atribucion wrapeada
    if _firma_residuo_es_prosa(core):
        return False  # cuerpo denso en nombres, no firma
    tiene_raya = "—" in s or " - " in s or "–" in s
    es_corta = len(s) <= 80
    termina_con_punto = s.rstrip().endswith(".")
    if tiene_raya or es_corta or (termina_con_punto and len(s) <= 120):
        return True
    return False


# ── A001: búsqueda inversa de firma (fallback post-dispositivo) ───────────────
#
# Cuando el parser no detecta dispositivo (por_ello_idx=None) o detecta
# dispositivo pero collect_firma_lines no encuentra firma, esta función
# busca desde el final del bloque hacia atrás. Guardas: zona de fallo
# obligatoria (post-apertura/considerando), span mínimo, filtro de zona
# post-firma, límite de retroceso.
# Validado: PoC H045 (poc_firma_independiente_v2.py), 34 recuperados,
# 0 falsos positivos sobre 148 sin_firma (corpus post-B069).

RE_DATOS_PARTES = re.compile(
    r"^(Recurso|Nombre del|Tribunal de origen|Tribunal que intervino|"
    r"Causa\s*:|Profesionales|Parte actora|Parte demandada)",
    re.I,
)

_SPAN_MINIMO_FIRMA_INVERSA = 20


def _encontrar_zona_fallo(bloque):
    """
    Encuentra el inicio de la zona del fallo propiamente dicho,
    excluyendo sumarios y dictamen del Procurador.

    Busca la PRIMERA ocurrencia de (en orden de prioridad):
    1. Apertura: "FALLO DE LA CORTE SUPREMA" — PRIMERA siempre
       (dictámenes no usan RE_APERTURA, así que la primera es del fallo).
    2. Fecha: "Buenos Aires, ..." — primera en la primera mitad
    3. Considerando: "Considerando:" — primera en la primera mitad
    4. Vistos: "Vistos los autos:" — primera en la primera mitad

    La restricción a primera mitad para fecha/considerando/vistos evita
    envenenamiento por marcadores del caso siguiente cuando el bloque
    arrastra residuo post-fin. Fallback sin restricción para bloques
    cortos donde el marcador cae en la segunda mitad.

    Retorna el índice relativo al bloque, o None.
    """
    n = len(bloque)
    mitad = n // 2

    # 1. Primera apertura (señal más fuerte, no ambigua)
    for k in range(n):
        s = bloque[k].strip()
        if RE_APERTURA.match(s):
            return k

    # 2. Primera fecha en primera mitad
    for k in range(mitad):
        s = bloque[k].strip()
        if RE_FECHA_LINEA.match(s):
            return k

    # 3. Primer considerando en primera mitad
    for k in range(mitad):
        s = bloque[k].strip()
        if RE_CONSIDERANDO.search(s):
            return k

    # 4. Primer vistos en primera mitad
    for k in range(mitad):
        s = bloque[k].strip()
        if s.lower().startswith("vistos los autos"):
            return k

    # 5. Fallback: sin restricción de mitad (bloques cortos)
    for k in range(n):
        s = bloque[k].strip()
        if RE_FECHA_LINEA.match(s):
            return k
    for k in range(n):
        s = bloque[k].strip()
        if RE_CONSIDERANDO.search(s):
            return k
    for k in range(n):
        s = bloque[k].strip()
        if s.lower().startswith("vistos los autos"):
            return k

    return None


def buscar_firma_inversa(bloque, max_retroceso=80):
    """
    Busca firma desde el final del bloque hacia atrás.

    Retorna (firma_idx, firma_raw, motivo) donde motivo es:
      'ok'                   — firma encontrada
      'span_corto'           — bloque menor a _SPAN_MINIMO_FIRMA_INVERSA
      'sin_zona_fallo'       — no se encontró apertura/fecha/considerando
      'sin_firma_post_fallo' — zona de fallo encontrada pero sin firma
    """
    n = len(bloque)
    if n < _SPAN_MINIMO_FIRMA_INVERSA:
        return None, "", "span_corto"

    zona_fallo = _encontrar_zona_fallo(bloque)
    if zona_fallo is None:
        return None, "", "sin_zona_fallo"

    limite = max(zona_fallo, n - max_retroceso)

    firma_encontrada = None
    for k in range(n - 1, limite - 1, -1):
        s = bloque[k].strip()
        if not s:
            continue
        if RE_PAGE_HEADER.match(s):
            continue
        if RE_DATOS_PARTES.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_encontrada = k
            break

    if firma_encontrada is None:
        return None, "", "sin_firma_post_fallo"

    # Subir para encontrar el inicio de la firma (puede ser multi-línea)
    firma_inicio = firma_encontrada
    for k in range(firma_encontrada - 1, max(limite, firma_encontrada - 5) - 1, -1):
        s = bloque[k].strip()
        if not s:
            break
        if RE_PAGE_HEADER.match(s):
            continue
        if linea_es_firma_de_juez(bloque[k]):
            firma_inicio = k
        else:
            if hay_juez_conocido(s) and len(s) < 80:
                firma_inicio = k
            else:
                break

    firma_raw = collect_firma_lines(bloque, firma_inicio)
    return firma_inicio, firma_raw, "ok"


# ── H040: wrapper con guardas para Pista 3 de detectar_fin_real ──────────────
#
# linea_es_header_sumario matchea falsos positivos en la zona de firma:
# líneas como "ARGIBAY (en disidencia)." pasan porque empiezan con ≥5
# mayúsculas y terminan en punto. Las guardas excluyen firmas, calificadores,
# headers de página y marcadores de apertura antes de aceptar el match.

def linea_es_header_sumario_guardado(linea):
    """linea_es_header_sumario + guardas de exclusión para Pista 3."""
    if not linea_es_header_sumario(linea):
        return False
    s = linea.strip()
    if linea_es_firma_de_juez(linea):
        return False
    if RE_CALIFICADOR.search(s):
        return False
    if RE_PAGE_HEADER.match(s):
        return False
    if RE_APERTURA.match(s):
        return False
    if RE_DICT_HDR.match(s):
        return False
    if s.upper().startswith("DICTAMEN"):
        return False
    if RE_HEADER_VOTO_DISIDENCIA.match(s):
        return False
    return True


def primer_token_de_caratula(nombres_indice):
    """Extrae el mejor token identificatorio de nombres_indice.

    B093 (H073): busca el primer token NO genérico recorriendo todos los
    tokens de todas las variantes (separadas por "|"). Ej:
      "D.G.I. c/ Provincia de Mendoza" → skip D,G,I (cortos),
        skip Provincia (genérico) → devuelve "Mendoza".
      "ANSeS (Benaben c/) | Benaben c/ ANSeS" → skip ANSeS (genérico)
        en var 1 → var 2 devuelve "Benaben".
    Solo si TODOS los tokens de TODAS las variantes son genéricos,
    devuelve el primer token usable como fallback.
    """
    if not nombres_indice:
        return ""

    _SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
             "empresa", "compania", "compañia", "compañía"}
    _GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
                  "afip", "buenos", "nacional", "administracion",
                  "federal", "direccion", "instituto"}

    variantes = nombres_indice.split("|")

    # Pasada 1: buscar primer token no-genérico en cualquier variante
    for v in variantes:
        tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", v.strip())
        for t in tokens:
            if (len(t) >= 4
                    and t.lower() not in _SKIP
                    and t.lower() not in _GENERICOS):
                return t

    # Pasada 2: todos genéricos — devolver el primer token usable
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", variantes[0].strip())
    for t in tokens:
        if len(t) >= 4 and t.lower() not in _SKIP:
            return t
    return tokens[0] if tokens else ""


def segundo_token_de_caratula(nombres_indice):
    """Extrae el segundo token significativo para confirmar genéricos.

    H076: cuando primer_token_de_caratula devuelve un token genérico
    (Buenos, Administración), el segundo token sirve como confirmación
    para evitar falsos positivos en ventana ampliada.
    """
    if not nombres_indice:
        return None
    _SKIP = {"otro", "otros", "sociedad", "sucesion", "sucesión",
             "empresa", "compania", "compañia", "compañía"}
    _GENERICOS = {"provincia", "anses", "nacion", "nación", "estado",
                  "afip", "buenos", "nacional", "administracion",
                  "federal", "direccion", "instituto"}
    first = nombres_indice.split("|")[0].strip()
    first = re.sub(r"^\(\d+\)\s*", "", first)
    tokens = re.findall(r"[A-ZÁÉÍÓÚÑa-záéíóúñ]+", first)
    found_first = False
    for t in tokens:
        if len(t) < 3:
            continue
        if not found_first:
            found_first = True
            continue
        if t.lower() not in _SKIP and t.lower() not in _GENERICOS:
            return t
    return None


# ── v18 Fase F: refinador de linea_inicio por título ─────────────────────────
#
# El localizador ancla linea_inicio en el header de página del .md, que
# frecuentemente cae en medio de la página anterior e incluye residuo del
# fallo previo (firma arrastrada, metadata editorial, representación letrada).
# Este refinador recorta ese residuo buscando el título del caso como ancla
# más precisa.
#
# Señal primaria : primer_token_de_caratula(nombres_indice) — token del título.
# Señal secundaria: "Vistos los autos" — emite warning en status_localizacion.
# Fallback final  : linea_inicio del catálogo sin cambios — emite warning.
#
# Tiers 1-3: búsqueda en ventana base (50 líneas).
# Tier 4 (H076): ventana ampliada (100 líneas) con guardas portadas de Pista 1
# de detectar_fin_real: _es_texto_corriente, stoplist + segundo token, trim≤50%.

MAX_LINEAS_BUSQUEDA_TITULO = 50
MAX_VENTANA_AMPLIADA = 100
MAX_TRIM_PCT = 50

# ── B147/M45 sub-frente D1 (H200): discriminador carátula v2 ─────────────────
#
# Los tiers exact/prefix de refinar_inicio_por_titulo tomaban el PRIMER match
# del token SIN guard de forma (causa raíz adjudicada H199 sobre 7 .md: el
# token matchea prosa/cola/dispositivo del caso PREVIO en la cabeza — «Banco»
# en la cola de Pontoriero 329_p2645, «Mendoza» en el dispositivo de Lavado
# 330_p1158). Guards D1, dictados por los FP de la muestra seed-199 y sellados
# con flip-set (poc_b147_d1_v03, E0/E0'' 5894/5894, 93 flips adjudicados H200):
#   (i)  el ancla debe parecer carátula: caps-ratio (_parece_caratula) ∨
#        conector de carátula « c/ » / « s/ » (re.I, toleran fin de línea
#        wrapeado: 339_p1048) / « V. » (case-sensitive: «v.» minúscula es
#        prosa legal — v. gr., véase). El conector recupera las carátulas
#        mixtas/anonimizadas («R. P., C. A. c/ M. O. ... s/ Restitución...»)
#        y evita avanzar desde la carátula real hacia un rubro caps posterior.
#   (ii) el ancla NO puede ser firma (linea_es_firma_de_juez, calcado H190):
#        «Santiago»/«Juan» matchean NOMBRES DE JUECES en firmas versales
#        (329_p1898, 330_p2478 — el FP que reventó el PoC v0.2 de H190).
# Lo que los guards rechazan cae a Pista 5b / Tier 4 / vistos / catalogo
# SIN cambios (el fall-through re-ancla las carátulas title-case tipo
# «MARINCCIONI...»/«TELECOM ITALIA SpA» y los Boggiano juez-parte — medido).
# Residuales documentados: D1b (ancla en línea 2 de carátula wrapeada, 6
# casos) · 333_p1401 (token «Unión» no matchea el acrónimo U.T.H.G.R.A. →
# D3/B018) · 330_p224 (nota-al-pie B161).

RE_CONECTOR_CARATULA_CS = re.compile(r"(?:^|\s)[cs]/(?:\s|$)", re.I)
RE_CONECTOR_CARATULA_V = re.compile(r"(?:^|\s)V\.\s")


def _es_caratula_v2(ln):
    """Guard (i) de D1: la línea parece carátula — por proporción de
    mayúsculas (_parece_caratula, B114) o por conector de carátula
    (mixtas/anonimizadas). Solo se evalúa sobre líneas donde el token del
    título ya matcheó (contención del FP de prosa)."""
    if _parece_caratula(ln):
        return True
    return bool(RE_CONECTOR_CARATULA_CS.search(ln)
                or RE_CONECTOR_CARATULA_V.search(ln))


# ── B095 Pista 5b: helpers para fullname matching (token corto) ──────────────
#
# Cuando primer_token_de_caratula devuelve <4 chars (iniciales anonimizadas,
# acrónimos cortos), el matching por token individual es inviable. Pista 5b
# busca el nombre COMPLETO del catálogo como frase, primero en formato
# directo ("P., S. D.") y luego invertido ("S. D. P."), porque el catálogo
# usa formato "apellido, nombre" pero el .md usa "nombre apellido".
# Validado H075: 15 fullname + ~23 inverted, 0 regresiones.

def _build_fullname_variants(nombres_indice):
    """Construye variantes del nombre para fullname matching.

    Devuelve lista de strings a buscar en orden: [forma_directa, forma_invertida].
    La forma invertida se genera swappeando "apellido, nombre" → "nombre apellido".
    Para carátulas con "c/", cada parte se invierte por separado.
    """
    if not nombres_indice:
        return []
    first = nombres_indice.split("|")[0].strip()
    # Limpiar prefijos editoriales: "(4) ", "(5) "
    first = re.sub(r"^\(\d+\)\s*", "", first)
    if len(first) < 2:
        return []

    variants = [first]  # forma directa primero

    # Forma invertida: "apellido, nombre" → "nombre apellido"
    if " c/ " in first:
        # "V., M. N. c/ S., W. F." → invertir cada parte
        parties = first.split(" c/ ", 1)
        inv_parts = []
        for p in parties:
            p = p.strip()
            cp = p.split(",", 1)
            if len(cp) == 2 and cp[1].strip():
                inv_parts.append(cp[1].strip() + " " + cp[0].strip())
            else:
                inv_parts.append(p)
        inverted = " c/ ".join(inv_parts)
        if inverted != first:
            variants.append(inverted)
    elif "," in first:
        # "P., S. D." → "S. D. P."
        cp = first.split(",", 1)
        if cp[1].strip():
            inverted = cp[1].strip() + " " + cp[0].strip()
            if inverted != first:
                variants.append(inverted)

    return variants


def _build_flexible_pattern(text):
    """Regex flexible para matching de nombre con espaciado variable.

    Puntos y comas aceptan espacio opcional después. Espacios aceptan
    variación. Devuelve regex compilado o None.
    """
    norm = _strip_accents(text)
    if len(norm) < 2:
        return None
    parts = []
    for c in norm:
        if c == '.':
            parts.append(r'\.\s*')
        elif c == ',':
            parts.append(r',\s*')
        elif c == ' ':
            parts.append(r'\s+')
        elif c.isalnum():
            parts.append(re.escape(c))
        else:
            parts.append(re.escape(c))
    try:
        return re.compile(''.join(parts), re.I)
    except re.error:
        return None


def refinar_inicio_por_titulo(bloque, nombres_indice):
    """
    Intenta refinar linea_inicio recortando residuo pre-título.

    Devuelve (offset_recorte, ancla_usada) donde:
      offset_recorte : int — líneas a recortar del inicio del bloque.
                       0 si no hay refinamiento o título está en línea 0.
      ancla_usada    : str — 'titulo' | 'vistos' | 'catalogo'

    El llamador aplica:
        linea_inicio += offset_recorte
        bloque = bloque[offset_recorte:]
    """
    # ── Señal primaria: token del título ──────────────────────────────────────
    # B089 (H074): normalizar tildes con _strip_accents (mismo fix que B071
    # en Pista 1). El catálogo tiene tildes ("Juárez") pero el .md es ALL
    # CAPS sin tildes ("JUAREZ"). Sin normalización, 318 casos caían a
    # ancla_catalogo con residuo del caso anterior no recortado.
    token = primer_token_de_caratula(nombres_indice)
    token_norm = _strip_accents(token) if token else ""
    if token and len(token) >= 4:
        pat = re.compile(r'\b' + re.escape(token_norm) + r'\b', re.I)
        for k, ln in enumerate(bloque[:MAX_LINEAS_BUSQUEDA_TITULO]):
            if pat.search(_strip_accents(ln)):
                # B089: si el match cae en las últimas 5 líneas del bloque,
                # es la carátula del caso siguiente, no del actual. Saltear.
                if k >= len(bloque) - 5:
                    continue
                if (linea_es_firma_de_juez(ln)
                        or not _es_caratula_v2(ln)):
                    continue  # ── GUARD D1 (exact), B147/H200 ──
                return (k, 'titulo')

        # B095 Pista 5 (H075): prefix match como fallback.
        # Cubre abreviaciones catálogo→.md: "Transp"→"TRANSPORTES",
        # "Camnasi"→"CAMNASIO", "Schr"→"SCHRÖDER", "Bank"→"BANKBOSTON".
        # Solo corre si el word-boundary exacto (arriba) no matcheó.
        # \b inicial garantiza inicio de palabra; sin \b final permite
        # que el token sea prefijo. Validado H075: 6 casos, 0 regresiones.
        pat_prefix = re.compile(r'\b' + re.escape(token_norm), re.I)
        for k, ln in enumerate(bloque[:MAX_LINEAS_BUSQUEDA_TITULO]):
            if pat_prefix.search(_strip_accents(ln)):
                if k >= len(bloque) - 5:
                    continue
                if (linea_es_firma_de_juez(ln)
                        or not _es_caratula_v2(ln)):
                    continue  # ── GUARD D1 (prefix), B147/H200 ──
                return (k, 'titulo')

    # ── B095 Pista 5b (H075): fullname + inverted para token corto ────────────
    # Cuando el token es <4 chars (iniciales anonimizadas, acrónimos), se
    # busca el nombre completo del catálogo como frase. Primero en formato
    # directo ("N. N.", "M. D. H. c/ M. B. M. F."), luego en formato
    # invertido ("S. D. P." ← "P., S. D.") porque el catálogo usa
    # "apellido, nombre" pero el .md usa "nombre apellido".
    if not token or len(token) < 4:
        for variant in _build_fullname_variants(nombres_indice):
            pat = _build_flexible_pattern(variant)
            if pat is None:
                continue
            for k, ln in enumerate(bloque[:MAX_LINEAS_BUSQUEDA_TITULO]):
                if pat.search(_strip_accents(ln)):
                    if k >= len(bloque) - 5:
                        continue
                    return (k, 'titulo')

    # ── H076 Tier 4: ventana ampliada con guardas ─────────────────────────────
    # Solo corre si Tiers 1-3 con ventana base fallaron. Porta heurísticas
    # de Pista 1 de detectar_fin_real:
    #   - _es_texto_corriente: descarta matches en texto corrido (retry loop)
    #   - Stoplist: tokens genéricos requieren segundo token confirmatorio
    #   - Guarda trim ≤ MAX_TRIM_PCT del bloque
    #   - Fullname+inverted para TODOS los tokens (no solo <4)
    _STOPLIST_TITULO = {"provincia", "anses", "nacion", "estado",
                        "afip", "buenos", "nacional", "administracion",
                        "federal", "direccion", "instituto"}
    len_bloque = len(bloque)

    def _buscar_con_guardas(pat, ventana):
        """Busca pat con retry loop + guarda texto corriente."""
        desde = 0
        limite = min(ventana, len_bloque)
        while desde < limite:
            found_k = None
            for j in range(desde, limite):
                if pat.search(_strip_accents(bloque[j])):
                    found_k = j
                    break
            if found_k is None:
                return None
            if found_k >= len_bloque - 5:
                desde = found_k + 1
                continue
            if _es_texto_corriente(bloque, found_k):
                desde = found_k + 1
                continue
            return found_k
        return None

    def _trim_ok(k):
        return len_bloque > 0 and (100 * k / len_bloque) <= MAX_TRIM_PCT

    def _confirma_generico(k, nombres_indice):
        """Para tokens genéricos, verificar segundo token en ±3 líneas."""
        tok2 = segundo_token_de_caratula(nombres_indice)
        if not tok2 or len(tok2) < 3:
            return False
        tok2_norm = _strip_accents(tok2)
        pat2 = re.compile(r'\b' + re.escape(tok2_norm) + r'\b', re.I)
        ventana_conf = bloque[max(0, k - 2):k + 5]
        return any(pat2.search(_strip_accents(ln)) for ln in ventana_conf)

    es_generico = (token_norm.lower() in _STOPLIST_TITULO) if token_norm else False

    # 4a: exact word boundary, ventana ampliada
    if token and len(token) >= 4:
        pat = re.compile(r'\b' + re.escape(token_norm) + r'\b', re.I)
        k = _buscar_con_guardas(pat, MAX_VENTANA_AMPLIADA)
        if k is not None and _trim_ok(k):
            if not es_generico or _confirma_generico(k, nombres_indice):
                return (k, 'titulo')

    # 4b: prefix match, ventana ampliada
    if token and len(token) >= 4:
        pat_prefix = re.compile(r'\b' + re.escape(token_norm), re.I)
        k = _buscar_con_guardas(pat_prefix, MAX_VENTANA_AMPLIADA)
        if k is not None and _trim_ok(k):
            if not es_generico or _confirma_generico(k, nombres_indice):
                return (k, 'titulo')

    # 4c: fullname+inverted para TODOS los tokens, ventana ampliada
    for variant in _build_fullname_variants(nombres_indice):
        pat = _build_flexible_pattern(variant)
        if pat is None:
            continue
        k = _buscar_con_guardas(pat, MAX_VENTANA_AMPLIADA)
        if k is not None and _trim_ok(k):
            return (k, 'titulo')

    # ── Señal secundaria: "Vistos los autos" ─────────────────────────────────
    # H076: extender búsqueda a ventana ampliada (antes era ventana base)
    for k, ln in enumerate(bloque[:MAX_VENTANA_AMPLIADA]):
        if RE_VISTOS_LOS_AUTOS.match(ln):
            return (k, 'vistos')

    # ── Fallback: sin refinamiento ────────────────────────────────────────────
    return (0, 'catalogo')


# ── B070+B071: helpers para Pista 1 forward ──────────────────────────────────
#
# B070: cuando Pista 1 forward encuentra un match de primer_token_siguiente,
# validar que la línea NO sea texto corriente (continuación de oración).
# Motivación: tokens comunes ("Nación", "Provincia", "Estado") matchean en
# el cuerpo argumentativo del caso actual, truncando el bloque antes de la firma.
# Validado: PoC H048 (poc_b070_v6.py), 37 mejoras, 0 regresiones.
#
# B071: normalizar tildes para matching tilde-insensitive.
# Motivación: el catálogo tiene tildes ("Administración") pero las carátulas
# en el .md son ALL CAPS sin tildes ("ADMINISTRACION"). Sin normalización,
# Pista 1 no matchea la carátula real.
# Validado: PoC H048 (poc_b070_v6.py), recupera 8 casos adicionales.

def _strip_accents(s):
    """á→a, é→e, ñ→n, etc. Para matching tilde-insensitive en Pista 1."""
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if unicodedata.category(c) != 'Mn')


def _es_texto_corriente(lines, k):
    """
    True si lines[k] parece continuación de texto corriente,
    no una carátula/sumario editorial. Usado como guarda en Pista 1 forward.

    Condiciones (OR):
      (a) Empieza con minúscula (continuación de oración),
          EXCEPTO si empieza con "c/" o "s/" (conector de carátula).
      (b) La línea anterior significativa termina con word-split genuino
          (letra + guión), no guión editorial (puntuación + guión).
    """
    s = lines[k].strip()
    if not s:
        return False

    # (a) Empieza con minúscula → continuación de oración
    #     Excepto "c/" y "s/" que son conectores de carátula
    first_alpha = None
    for c in s:
        if c.isalpha():
            first_alpha = c
            break
    if first_alpha and first_alpha.islower():
        s_stripped = s.lstrip()
        if not (s_stripped.startswith("c/") or s_stripped.startswith("s/")):
            return True

    # Buscar línea anterior significativa (no vacía, no page header)
    prev_line = None
    for j in range(k - 1, max(k - 5, -1), -1):
        if j < 0:
            break
        ps = lines[j].strip()
        if not ps:
            continue
        if RE_PAGE_HEADER.match(ps):
            continue
        if re.match(r'^\d{1,4}$', ps):
            continue
        if ps in ("FALLOS DE LA CORTE SUPREMA", "DE JUSTICIA DE LA NACION",
                   "DE JUSTICIA DE LA NACIÓN"):
            continue
        prev_line = ps
        break

    if prev_line is None:
        return False

    # (b) Word-split genuino: letra + guión (no puntuación + guión)
    if prev_line.endswith('-') and len(prev_line) >= 2:
        char_antes = prev_line[-2]
        if char_antes.isalpha():
            return True

    return False


# ── B147-1A (H190): retroceso de frontera fina sobre el fin de Pistas 1/3/4 ──
# Mecanismo adjudicado sobre 8 testigos .md (corrige el modelo H188): Pista 1
# corta en carátula-1 pero deja colgando el material PRE-carátula del caso
# siguiente (rótulos temáticos, banners, apertura de su dictamen, strays);
# Pistas 3/4 anclan en el DICTAMEN del siguiente y absorben carátula + rótulo
# + sumario ENTERO. El perfil 3/4 existe porque Pista 1 falla por token corto
# ("Lumi" < 5) o divergencia OCR índice/cuerpo ("Hurting"/"HURTIG") → el
# retroceso es INDEPENDIENTE del token: A recorta líneas no-sustantivas hacia
# atrás; B busca acotado una carátula POR FORMA con prosa intermedia (el
# sumario absorbido) y corta en carátula-1, re-aplicando A.
# GUARDS (adjudicación del flip-set poc v0.2→v0.3 en disco): firma de juez
# (linea_es_firma_de_juez — la firma en VERSALES de los tomos viejos matchea
# _parece_caratula: 958 FP de B + 420 de A eliminados) y header de voto
# (RE_HEADER_VOTO_DISIDENCIA, 2 líneas caps) = sustantivos en A y stop /
# no-candidato en B; el scan de B FRENA en la primera firma; candidato con
# token del nombre PROPIO = apéndice del mismo caso (1C) → no corta.
# Espec medida: poc_b147_1a_retroceso.py v0.3 (scripts/diagnostico/H190/),
# flip-set 1866/5542, anclas 5/5 — este bloque replica ese predicado VERBATIM
# (los umbrales y el orden de clases NO se tocan sin re-medir).

RE_FRONTERA_APERTURA_DICT = re.compile(r"^Dictamen de la Procuraci[oó]n\b", re.I)
RE_FRONTERA_SUPREMA_CORTE = re.compile(r"^Suprema Corte:\s*$", re.I)
RE_FRONTERA_ATRIBUCION    = re.compile(r"^[–—-]\s*De[l\s].{0,150}[–—-]\s*(\(\*+\))?\s*\.?\s*$")
RE_FRONTERA_CONSID_SUELTO = re.compile(r"^Considerando:\s*$")
RE_FRONTERA_CS_BARRA      = re.compile(r"\b[cs]/")   # ' c/ ' / ' s/ ' de carátula

_RETRO_MAX_TRIM  = 60   # tope de profundidad (guard patológico; 0 observados)
_RETRO_VENTANA_B = 25   # ventana de búsqueda de carátula (etapa B)
_RETRO_PISO_REL  = 5    # nunca recortar por debajo de li + 5

# Tokens que no identifican un caso (guard nombre-propio; lista del PoC v0.3
# = la espec medida; paralela a _GENERICOS de primer_token_de_caratula, que
# es function-local y con otro propósito — no se unifican sin re-medir).
_GENERICOS_FRONTERA = {
    "provincia", "nacion", "nacional", "estado", "buenos", "aires", "otros",
    "otro", "otra", "otras", "recurso", "hecho", "deducido", "interpuesto",
    "causa", "administracion", "federal", "direccion", "general", "instituto",
    "sociedad", "anonima", "argentina", "banco", "gobierno", "ciudad",
    "municipalidad", "ministerio", "empresa", "compania",
}


def _tokens_nombre_significativos(nombre):
    """Tokens identificatorios (>=5 chars, no genéricos, sin tildes, lower)
    del case_name/nombres_indice, para el guard nombre-propio de la etapa B."""
    toks = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñÜü]+", nombre or "")
    return {_strip_accents(t).lower() for t in toks
            if len(t) >= 5 and _strip_accents(t).lower() not in _GENERICOS_FRONTERA}


def _linea_es_firma_o_voto_hdr(linea, s):
    """Firma de juez o header de voto/disidencia = contenido PROPIO del caso.
    Sustantivo en la etapa A (frena el recorte); stop/no-candidato en B."""
    return bool(RE_HEADER_VOTO_DISIDENCIA.match(s)) or linea_es_firma_de_juez(linea)


def _clase_linea_frontera_base(linea):
    """Etiqueta de clase si la línea es no-sustantiva (basura de frontera),
    o None si es sustantiva. Orden de clases = espec del PoC v0.3.
    NO ve contexto: el guard de continuación-de-wrap vive en el wrapper."""
    s = linea.strip()
    if not s:
        return "vacia"
    if RE_PAGE_HEADER.match(s):
        return "banner"
    if RE_FRONTERA_APERTURA_DICT.match(s):
        return "apertura_dictamen"
    if RE_FRONTERA_SUPREMA_CORTE.match(s):
        return "suprema_corte"
    if RE_FRONTERA_ATRIBUCION.match(s):
        return "atribucion"
    if RE_FRONTERA_CONSID_SUELTO.match(s):
        return "considerando_suelto"
    if _linea_es_firma_o_voto_hdr(linea, s):
        return None                     # guard: firma/voto = sustantivo
    if _parece_caratula(linea):
        return "rotulo_caps"            # rótulo temático O carátula (all-caps)
    return None


def _es_continuacion_wrap(lines, idx):
    """v27.1: fragmento final de una línea SUSTANTIVA wrapeada — p.ej. el
    cierre de la firma («…RICARDO LUIS» ⏎ «LORENZETTI.»: el apellido solo no
    matchea JUECES_CONOCIDOS, cuyos patrones son nombre+apellido) o de la
    lista de partes del epílogo («…COSMOMAR S.A., PERFOMAR» ⏎ «S.A. –
    AGROPERFO S.A.»). Señal de wrap: fragmento corto caps que CIERRA en '.'
    inmediatamente después (sin vacías) de una línea sustantiva ABIERTA (que
    no cierra en '.'). Los rótulos ajenos genuinos siguen a líneas cerradas
    → no los protege; los banners nunca cierran en '.' → capa banner intacta."""
    s = lines[idx].strip()
    if len(s) > 80 or not s.endswith("."):
        return False
    if idx - 1 < 0:
        return False
    prev = lines[idx - 1].strip()
    if not prev or prev.endswith("."):
        return False                    # anterior vacía o CERRADA → no es wrap
    return _clase_linea_frontera_base(lines[idx - 1]) is None


def _clase_linea_frontera(lines, idx):
    """Clase de frontera CON contexto: la base, salvo que un rotulo_caps sea
    la continuación del wrap de la línea sustantiva anterior (v27.1)."""
    c = _clase_linea_frontera_base(lines[idx])
    if c == "rotulo_caps" and _es_continuacion_wrap(lines, idx):
        return None
    return c


def _es_caratula_forma_frontera(lines, idx, tope_sup):
    """Carátula POR FORMA (independiente del token): all-caps y además
    (tiene c// s/) o (la siguiente no-vacía es rótulo all-caps). Ni el
    candidato ni la línea-confirmante pueden ser firma/header-de-voto."""
    linea = lines[idx]
    s = linea.strip()
    if not s or not _parece_caratula(linea):
        return False
    if RE_PAGE_HEADER.match(s) or _linea_es_firma_o_voto_hdr(linea, s):
        return False
    if RE_FRONTERA_CS_BARRA.search(linea):
        return True
    j = idx + 1
    while j <= tope_sup and not lines[j].strip():
        j += 1
    if j > tope_sup:
        return False
    sj = lines[j].strip()
    return (_parece_caratula(lines[j])
            and not RE_PAGE_HEADER.match(sj)
            and not _linea_es_firma_o_voto_hdr(lines[j], sj))


def retroceder_frontera(lines, li, k, tokens_nombre_propio=frozenset()):
    """B147-1A: dado el fin k propuesto por Pistas 1/3/4 de detectar_fin_real,
    retrocede el borde para no absorber la cabeza del caso siguiente.
    Etapa A (recorte de no-sustantivas) → etapa B (carátula por forma, con
    prosa intermedia, scan frenado en la primera firma, guard nombre-propio)
    → re-A desde carátula-1. Devuelve el fin corregido (<= k). Desborde de
    _RETRO_MAX_TRIM = no-op conservador (0 casos observados en el PoC)."""
    piso = li + _RETRO_PISO_REL
    if k <= piso:
        return k

    def _recorte_a(fin):
        n, kk = 0, fin
        while kk > piso and n < _RETRO_MAX_TRIM:
            if _clase_linea_frontera(lines, kk) is None:
                break
            n += 1
            kk -= 1
        return kk, n >= _RETRO_MAX_TRIM

    fin_a, desbordado = _recorte_a(k)
    if desbordado:
        return k                        # no-op conservador
    # Etapa B: carátula ajena por forma dentro de la ventana.
    limite = max(piso, fin_a - _RETRO_VENTANA_B)
    candidatos = []
    for c in range(fin_a, limite - 1, -1):
        s = lines[c].strip()
        if s and linea_es_firma_de_juez(lines[c]):
            break                       # techo estructural: la firma propia
        if _es_caratula_forma_frontera(lines, c, fin_a):
            if tokens_nombre_propio and (
                    _tokens_nombre_significativos(lines[c]) & tokens_nombre_propio):
                continue                # apéndice del propio caso (1C)
            candidatos.append(c)
    if candidatos:
        c = min(candidatos)             # la cabeza ajena ARRANCA en su carátula
        hay_prosa = any(lines[j].strip() and _clase_linea_frontera(lines, j) is None
                        for j in range(c + 1, fin_a + 1))
        if hay_prosa:
            fin_b, desbordado = _recorte_a(c - 1)
            if not desbordado:
                return fin_b
    return fin_a


def detectar_fin_real(lines, linea_inicio, linea_fin_catalogo,
                      proximo_header_pagina, primer_token_siguiente,
                      tokens_nombre_propio=frozenset()):
    """
    v15: detecta dónde realmente termina el contenido decisorio del fallo.
    Devuelve (linea_fin_real, status_fin, pista).

    status_fin: 'fin_dentro_bloque' / 'fin_extendido_pag_compartida' /
                'fin_por_firma_actual' / 'fin_por_editorial' / 'fin_no_detectado'
    pista: 'caratula_siguiente' / 'sumario_siguiente' /
           'marcador_apertura_siguiente' / 'editorial_siguiente' /
           'firma_actual' / 'fallback_catalogo'

    H069: fallback firma_actual cambia de backward-first a bidireccional
    closest-to-lfc (B045). Busca en ambas direcciones y elige la firma más
    cercana a linea_fin_catalogo. Corrige 16 falsos unanime (firma arrastrada
    del caso anterior) y recupera 19 votos truncados.

    v27 (B147-1A, H190): los fines de Pistas 1/3/4 pasan por
    retroceder_frontera (ver bloque arriba) para no absorber la cabeza del
    caso siguiente. Pista 2 (editorial), fallback firma_actual y
    fallback_catalogo NO se tocan (mecanismos distintos: 1C, B019, B012).
    tokens_nombre_propio: tokens del nombre del PROPIO caso (guard apéndice).
    """
    n = len(lines)
    li = max(0, int(linea_inicio))
    lfc = min(n - 1, int(linea_fin_catalogo))

    # Determinar límite hacia adelante. proximo_header_pagina es la línea de
    # inicio del bloque del fallo siguiente; la firma del fallo X puede caer
    # en las primeras líneas de ese bloque (página compartida), por eso
    # extendemos ~50 líneas más allá.
    if proximo_header_pagina is not None and proximo_header_pagina > lfc:
        limite_adelante = min(proximo_header_pagina + 50, n - 1)
    else:
        limite_adelante = min(lfc + 200, n - 1)

    def buscar_atras(check, desde, hasta):
        for k in range(desde, hasta - 1, -1):
            if check(lines[k]):
                return k
        return None

    def buscar_adelante(check, desde, hasta):
        for k in range(desde, hasta + 1):
            if check(lines[k]):
                return k
        return None

    # Pista 1: carátula del fallo siguiente
    # B070: loop con validación de texto corriente.
    # B071: matching tilde-insensitive con _strip_accents.
    # B093 (H073): stoplist de tokens genéricos. "Provincia", "ANSeS",
    # "Nación" aparecen en el cuerpo de casi todos los fallos (citas
    # jurisprudenciales, menciones de partes). Cuando el siguiente caso
    # tiene uno de estos como primer token, Pista 1 genera falsos cortes
    # que truncan el bloque antes de la firma (31→21 sin_firma pero con
    # regresiones si se usa guarda de mayúsculas). Solución: skip Pista 1
    # y dejar que Pista 2/3/4/fallback-firma encuentre el fin real.
    # B093 (H073): stoplist de tokens genéricos — red de seguridad para
    # los casos donde primer_token_de_caratula no encuentra ningún token
    # específico (ambas partes son entidades genéricas). Sincronizada con
    # _GENERICOS de primer_token_de_caratula. Post _strip_accents.
    _STOPLIST_PISTA1 = {"provincia", "anses", "nacion", "estado",
                        "afip", "buenos", "nacional", "administracion",
                        "federal", "direccion", "instituto"}
    token_bloqueado = (primer_token_siguiente
                       and _strip_accents(primer_token_siguiente).lower() in _STOPLIST_PISTA1)
    if (primer_token_siguiente and len(primer_token_siguiente) >= 5
            and not token_bloqueado):
        token_norm = _strip_accents(primer_token_siguiente)
        pat = re.compile(r"\b" + re.escape(token_norm) + r"\b", re.I)
        # B069: búsqueda atrás de Pista 1 ELIMINADA.
        # B070: búsqueda adelante con guarda: si el match cae en texto
        # corriente (empieza con minúscula o word-split), saltar y seguir.
        desde = lfc + 1
        while desde <= limite_adelante:
            k = None
            for j in range(desde, limite_adelante + 1):
                linea_norm = _strip_accents(lines[j])
                if pat.search(linea_norm):
                    k = j
                    break
            if k is None:
                break
            if _es_texto_corriente(lines, k):
                desde = k + 1
                continue
            # B094: skip firma de juez — token del caso siguiente puede
            # coincidir con nombre de juez (ej: "Santiago" en "ENRIQUE
            # SANTIAGO PETRACCHI —"). Guarda: raya obligatoria para no
            # filtrar carátulas de jueces-parte (Boggiano, Moliné).
            if (linea_es_firma_de_juez(lines[k])
                    and ("—" in lines[k] or "–" in lines[k])):
                desde = k + 1
                continue
            return (retroceder_frontera(lines, li, k - 1, tokens_nombre_propio),
                    "fin_extendido_pag_compartida", "caratula_siguiente")

    # Pista 2: marcador editorial (B077, B088)
    # Acordadas, índices, discursos al final del tomo. Prioridad sobre
    # sumario/apertura porque Pista 3/4 pueden encontrar headers dentro
    # del índice editorial que parecen sumarios (B088: 330_p2849 110k wc).
    # Busca desde li hacia adelante — los marcadores son suficientemente
    # específicos para no generar FP en texto de fallos (validado H058).
    k = buscar_adelante(_es_marcador_editorial, li, lfc)
    if k is not None:
        return (k - 1, "fin_por_editorial", "editorial_siguiente")

    # Pista 3: header de sumario nuevo. Búsqueda atrás solo en mitad inferior
    # del bloque para no confundir con sumarios del propio fallo X.
    # H040: usa wrapper con guardas para excluir firmas, calificadores,
    # headers de página y marcadores de apertura.
    mitad_bloque = li + (lfc - li) // 2
    k = buscar_atras(linea_es_header_sumario_guardado, lfc, mitad_bloque)
    if k is not None:
        return (retroceder_frontera(lines, li, k - 1, tokens_nombre_propio),
                "fin_dentro_bloque", "sumario_siguiente")
    k = buscar_adelante(linea_es_header_sumario_guardado, lfc + 1, limite_adelante)
    if k is not None:
        return (retroceder_frontera(lines, li, k - 1, tokens_nombre_propio),
                "fin_extendido_pag_compartida", "sumario_siguiente")

    # Pista 4: DICTAMEN o FALLO DE LA CORTE del fallo siguiente. Solo adelante
    # (atrás siempre hay marcadores del propio fallo).
    def es_marcador_apertura(linea):
        s = linea.strip()
        return (RE_APERTURA.match(s) is not None
                or RE_DICT_HDR.match(s) is not None
                or s.upper().startswith("DICTAMEN"))
    k = buscar_adelante(es_marcador_apertura, lfc + 1, limite_adelante)
    if k is not None:
        return (retroceder_frontera(lines, li, k - 1, tokens_nombre_propio),
                "fin_extendido_pag_compartida", "marcador_apertura_siguiente")

    # Fallback: firma del fallo actual — bidireccional closest-to-lfc (B045 H069)
    # Busca en ambas direcciones y elige la firma más cercana a lfc.
    # Motivación: cuando hay arrastre del caso anterior (B045), backward
    # encontraba la firma arrastrada (lejos de lfc) e ignoraba la firma real
    # del caso actual en la zona de extensión (cerca de lfc). Bidireccional
    # elige la correcta por proximidad. Strict less-than: empate → backward.
    # POC validado: 35 mejoras (16 unanime + 19 votos truncados), 0 regresiones.
    #
    # B019 (H131): la firma puede wrapear en >1 línea del OCR ("…— Carlos\n
    # S. Fayt — …"). El pick anclaba en la PRIMERA línea-firma y dejaba la
    # continuación afuera del bloque → firma/votos truncados (23 casos, todos
    # pista_fin=firma_actual). extender_firma() avanza desde la línea elegida
    # por las líneas de continuación de firma y devuelve la última. Frena en la
    # primera no-firma (epílogo "Recurso … interpuesto por …"), tolera 1 vacía
    # (espejo de collect_firma_lines) y respeta limite_adelante (no invade el
    # fallo siguiente). PoC en disco: +56 votos / 0 sobre-extensión / firma-
    # completa intactos. NO altera el pick bidireccional, solo extiende su salida.
    def extender_firma(k):
        ult = k
        blancos = 0
        j = k + 1
        while j <= limite_adelante and j < n:
            if not lines[j].strip():
                blancos += 1
                if blancos > 1:
                    break
                j += 1
                continue
            if linea_es_firma_de_juez(lines[j]):
                ult = j
                blancos = 0
                j += 1
                continue
            break
        return ult

    k_back = buscar_atras(linea_es_firma_de_juez, lfc, li)
    k_fwd = buscar_adelante(linea_es_firma_de_juez, lfc + 1, limite_adelante)
    if k_back is not None and k_fwd is not None:
        if (k_fwd - lfc) < (lfc - k_back):
            return (extender_firma(k_fwd), "fin_por_firma_actual", "firma_actual")
        else:
            return (extender_firma(k_back), "fin_por_firma_actual", "firma_actual")
    elif k_back is not None:
        return (extender_firma(k_back), "fin_por_firma_actual", "firma_actual")
    elif k_fwd is not None:
        return (extender_firma(k_fwd), "fin_por_firma_actual", "firma_actual")

    # Sin detectar: usar el catálogo como está
    return (lfc, "fin_no_detectado", "fallback_catalogo")


def cargar_proximos_headers(ruta_mapa):
    """Devuelve dict {(tomo, archivo): [(linea_header, pagina), ...]} ordenado."""
    por_archivo = {}
    with open(ruta_mapa, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["tomo"]), row["archivo"])
            por_archivo.setdefault(key, []).append(
                (int(row["linea_header"]), int(row["pagina"]))
            )
    for k in por_archivo:
        por_archivo[k].sort()
    return por_archivo


def proximo_header_despues_de(headers_archivo, linea):
    """Devuelve la próxima línea-header > linea, o None."""
    for ln, _pg in headers_archivo:
        if ln > linea:
            return ln
    return None


# ── v17: helper para casos identificados como sumario-con-link ────────────────

def construir_caso_sumario_link(caso_id_canonico, tomo, nombres_indice,
                                 source_file, linea_inicio, linea_fin,
                                 linea_fin_real, status_loc_final,
                                 status_fin, pista_fin):
    """
    v17: construye el dict de un caso identificado como sumario-con-link.

    El bloque no contiene un fallo parseable (es una nota editorial con link
    al fallo online), por lo que todos los campos analíticos (firma, outcome,
    voting_pattern, considerando, jueces, wc_*, etc.) quedan vacíos o en cero.

    La metadata estructural (linea_inicio, linea_fin, source_file, nombres,
    status) se conserva intacta para permitir auditoría posterior y
    cruzamiento con otras fuentes (sentencias online, índice editorial).

    El schema es idéntico al de un caso normal — solo cambian los valores —
    para mantener consistencia del CSV y permitir filtrado simple por
    tipo_entrada.
    """
    return {
        "caso_id_canonico":       caso_id_canonico,
        "tomo":                   tomo,
        "case_name_indice":       nombres_indice,
        "case_name_cuerpo":       "",
        "case_name_cuerpo_legacy": "",
        "date":                   "",
        "apertura_tipo":          "",
        "outcome":                "",
        "voting_pattern":         "",
        "n_jueces":               0,
        "n_titulares":            0,
        "n_votos_svoto":          0,
        "n_disidencias":          0,
        "dictamen_presente":      0,
        "is_originaria":          0,
        "is_full_bench":          0,
        "is_merit_decision":      0,
        "es_queja":               0,
        "queja_resultado":        "",
        "tipo_cuestion_federal":  "",
        "word_count":             0,
        "wc_mayoria":             0,
        "wc_votos":               0,
        "wc_considerando":        0,
        "wc_dictamen":            0,
        "firma_raw":              "",
        "jueces":                 "",
        "jueces_conocidos":       "",
        "jueces_desconocidos":    "",
        "posiciones":             "{}",
        "tribunal_origen":        "",
        "tribunal_origen_status": "",
        "por_ello_text":          "",
        "considerando_text":      "",
        "source_file":            source_file,
        "linea_inicio":           int(linea_inicio),
        "linea_fin":              int(linea_fin) if linea_fin not in ("", None) else "",
        "linea_fin_real":         linea_fin_real,
        "status_localizacion":    status_loc_final,
        "status_fin":             status_fin,
        "pista_fin":              pista_fin,
        "tipo_entrada":           "sumario_con_link",
    }



# ── H051 Refacción C: zonificador de bloques ──────────────────────────────────
#
# Asigna una zona a cada línea de un bloque de fallo. Usa 3 pasadas:
#   Pasada 0: marcar headers de página (ruido transversal)
#   Pasada 1: detectar anclas (marcadores estructurales)
#   Pasada 2: propagar zonas entre anclas
#
# Uso actual: clasificar bloques como sumario_editorial (sin cuerpo/disp/firma).
# Uso futuro: reemplazar detección de dictamen, firma, dispositivo por zonas.

# ── B117 F2 (H184): marcador de epílogo — escalera v2 consolidada ─────────────
#
# Reemplaza a RE_DATOS_PARTES SOLO en el sitio del epilogo_marker (Pasada 1 de
# zonificar_bloque). RE_DATOS_PARTES queda INTACTA para su otro consumidor
# (A001, búsqueda inversa de firma, PoC H045).
#
# Fuente: poc_b117_superficie.py v0.2 (scripts/diagnostico/H183) — unión con
# '|' de los SEIS cuerpos verbatim de la candidata v2 (RE_V1_RECURSO +
# RE_V1_ROTULO + escalera _LADDER[1:]). Único cambio sintáctico: el re.I
# global de RE_V1_ROTULO pasa a (?i:...) escopeado. Equivalencia consolidada
# == escalera verificada (0 diffs, sandbox H184); la regresión que CIERRA es
# re-correr el poc post-fix: queda 9882 exactos + 34 testigos con marker.
#
# Evidencia F1 (H183, adjudicada): 11.201 markers (5697 fallos, A0 5697/5697),
# cae 1319 / queda 9882, 0 readmisiones espurias, FN corpus-wide = 3 (clase
# verbo-partido → M44). Constancia completa en B117 (DEUDA_TECNICA).
RE_EPILOGO_MARKER = re.compile(
    # v1 recurso: Recurso/Queja + interpuesto/deducido (y fundado) + por[:\s]
    # (case-sensitive entera)
    r"^(?:Recursos?|Queja)\b[^\n]*?(?:interpuest\w+|deducid\w+)"
    r"(?:\s+y\s+fundad\w+)?\s+por[:\s]"
    # v1 rótulos anclados a ':' (re.I escopeado). H184-b: «Causa» FUERA de esta
    # lista — con [^:\n]*: cualquier «causa …(Fallos: …» narrativa matcheaba
    # (103 FP del dump H184, clase fuera del universo F1); ancla aparte abajo.
    r"|(?i:^(?:Nombre del|Tribunal de origen|Tribunal que intervino|"
    r"Profesionales|Parte actora|Parte demandada)[^:\n]*:)"
    # Causa con ':' PEGADO (verbatim de RE_DATOS_PARTES vieja): todo marker
    # «Causa» del universo F1 tenía el ':' adyacente por definición — 0 pérdidas.
    r"|(?i:^Causa\s*:)"
    # case_scope: gramática v1 con case solo en el arranque (Title Case, t347)
    r"|^(?:Recursos?|Queja)\b(?i:[^\n]*?(?:interpuest\w+|deducid\w+)"
    r"(?:\s+y\s+fundad\w+)?\s+por[:\s])"
    # gram_v2: verbos ensanchados + «por» libre + sin-por (artículo / Nombre)
    r"|^(?:Recursos?|Queja)\b(?i:[^\n]*?"
    r"(?:inte\w*rpu\w+|deducid\w+|presentad\w+|articulad\w+|fundad\w+)"
    r"(?:[^\n]*?\bpor\b"
    r"|\s+(?:el|la|los|las)\b"
    r"|\s+(?-i:[A-ZÁÉÍÓÚÑ])"
    r"))"
    # recurso_dp: pie estilo rótulo sin verbo («Recurso ordinario de apelación: AFIP»)
    r"|^(?:Recursos?|Queja)\b[^:\n]{0,60}:"
    # rotulo_relaj: rótulos case-sensitive, separador [,.] u omitido + contenido de pie
    r"|^(?:Parte\s+(?:actora|demandada)|Tribunal\s+de\s+origen|"
    r"Profesionales(?:\s+intervinientes)?)"
    r"\s*(?:[,.]\s*)?"
    r"(?:Dres?\.|Dra\.|Cámara|Corte|Juzgado|Sala|Superior|Tribunal|\(|"
    r"[A-ZÁÉÍÓÚÑ])")


def zonificar_bloque(bloque):
    """
    H052/H055: asigna una zona a cada línea del bloque.

    Retorna:
      zonas:  list[str]    — etiqueta de zona para cada línea (len == len(bloque))
      anclas: list[tuple]  — (linea, tipo_marcador) detectadas en pasada 1

    Zonas posibles: header_pagina, sumario, dictamen, apertura, cuerpo,
    dispositivo, firma, voto_separado, epilogo, intersticio,
    residuo_caso_anterior.

    Guarda dictamen (H052): dentro de zona dictamen, solo apertura y
    fecha (sin apertura futura) cierran la zona. Los demás marcadores
    (dispositivo, firma, etc.) se suprimen — son falsos positivos del
    vocabulario compartido entre el dictamen del Procurador y el fallo.

    Residuo caso anterior (H055): el intersticio inicial (antes de la
    primera zona semántica) se reclasifica como residuo_caso_anterior.
    Es material del fallo previo incluido por solapamiento de páginas
    (B045 manifestación B). Se excluye del word_count en procesar_archivo.
    """
    n = len(bloque)
    zonas = ["intersticio"] * n

    # ── Pasada 0: headers de página ──────────────────────────────────
    for k in range(n):
        s = bloque[k].strip()
        if s and RE_PAGE_HEADER.match(s):
            zonas[k] = "header_pagina"

    # ── Pasada 1: detectar anclas ────────────────────────────────────
    anclas = []
    # B076: dentro de zona sumario, firma_linea es siempre espuria
    # (líneas de atribución como "Carlos S. Fayt." en sumarios editoriales).
    # Un flag _en_sumario se activa con sumario_header/RE_REMISION y se
    # desactiva con cualquier ancla semántica fuerte.
    _en_sumario = False
    for k in range(n):
        if zonas[k] == "header_pagina":
            continue
        s = bloque[k].strip()
        if not s:
            continue

        if RE_DICT_HDR.match(s):
            _en_sumario = False
            anclas.append((k, "dictamen_inicio")); continue
        if RE_APERTURA.match(s):
            _en_sumario = False
            anclas.append((k, "apertura")); continue
        if RE_FECHA_LINEA.match(s):
            anclas.append((k, "fecha")); continue
        if RE_CONSIDERANDO.search(s):
            _en_sumario = False
            anclas.append((k, "considerando")); continue
        if RE_VISTOS.match(s):
            _en_sumario = False
            anclas.append((k, "vistos")); continue
        if RE_VOTO_HDR.match(s) or RE_DISID_HDR.match(s):
            _en_sumario = False
            anclas.append((k, "voto_header")); continue

        # H194 (B149 A2): peek de wrap para las variantes performativas —
        # espejo del PoC (cola = linea siguiente stripeada).
        _cola_wrap = bloque[k + 1].strip() if k + 1 < n else ""
        es_disp, _ = detectar_apertura_dispositivo(s, _cola_wrap, zonif=True)
        if es_disp:
            _en_sumario = False
            anclas.append((k, "dispositivo")); continue

        # B076: suprimir firma dentro de sumario
        if linea_es_firma_de_juez(bloque[k]):
            if not _en_sumario:
                anclas.append((k, "firma_linea")); continue
            else:
                continue  # firma espuria en sumario — saltar

        # Sumario antes de epilogo (prioridad)
        if linea_es_header_sumario(bloque[k]):
            _en_sumario = True
            anclas.append((k, "sumario_header")); continue

        # Remisión a precedente/dictamen — señal de sumario editorial
        if RE_REMISION.match(s):
            _en_sumario = True
            anclas.append((k, "sumario_header")); continue

        # Epilogo solo después de firma/voto/dispositivo
        # B117 F2 (H184): la ancla usa RE_EPILOGO_MARKER (escalera v2), no
        # RE_DATOS_PARTES (que sigue viva en A001). Guard sin cambio.
        if RE_EPILOGO_MARKER.match(s):
            if any(t in ("firma_linea", "voto_header", "dispositivo")
                   for _, t in anclas):
                anclas.append((k, "epilogo_marker")); continue

    # ── Pasada 2: propagar zonas ─────────────────────────────────────
    zona_activa = "intersticio"
    ancla_en = {pos: tipo for pos, tipo in anclas}

    for k in range(n):
        if zonas[k] == "header_pagina":
            continue
        if k in ancla_en:
            tipo = ancla_en[k]

            # Guarda dictamen: dentro de dictamen, solo apertura y fecha
            # (sin apertura futura) cierran la zona.
            if zona_activa == "dictamen" and tipo not in (
                "apertura", "fecha", "dictamen_inicio"
            ):
                pass  # mantener zona_activa = "dictamen"
            elif tipo == "sumario_header":
                zona_activa = "sumario"
            elif tipo == "dictamen_inicio":
                zona_activa = "dictamen"
            elif tipo == "apertura":
                zona_activa = "apertura"
            elif tipo == "fecha":
                if zona_activa in ("apertura", "intersticio", "sumario"):
                    zona_activa = "cuerpo"
                elif zona_activa == "dictamen":
                    if not any(t == "apertura" for _, t in anclas if _ > k):
                        zona_activa = "cuerpo"
            elif tipo == "considerando":
                zona_activa = "cuerpo"
            elif tipo == "vistos":
                if zona_activa not in ("dictamen",):
                    zona_activa = "cuerpo"
            elif tipo == "dispositivo":
                zona_activa = "dispositivo"
            elif tipo == "firma_linea":
                zona_activa = "firma"
            elif tipo == "voto_header":
                zona_activa = "voto_separado"
            elif tipo == "epilogo_marker":
                zona_activa = "epilogo"
        zonas[k] = zona_activa if zonas[k] != "header_pagina" else "header_pagina"

    # ── Pasada 3: reclasificar intersticio inicial como residuo_caso_anterior ──
    # El bloque de intersticio antes de la primera zona semántica es
    # material del caso anterior incluido por solapamiento de páginas
    # (B045 manifestación B). Se reclasifica para excluirlo del word_count.
    # Lógica equivalente al catch_all_inicio del visor (líneas 313-325).
    _ZONAS_SEM = {"sumario", "dictamen", "apertura", "cuerpo",
                  "dispositivo", "firma", "voto_separado"}
    _primer_sem_k = None
    for k in range(n):
        if zonas[k] in _ZONAS_SEM:
            _primer_sem_k = k
            break
    if _primer_sem_k is not None:
        for k in range(n):
            if k >= _primer_sem_k:
                break
            if zonas[k] == "intersticio":
                zonas[k] = "residuo_caso_anterior"

    # ── Pasada 3b: revertir residuo falso positivo ──────────────────
    # Si el bloque no tiene ninguna zona de contenido sustantivo
    # (apertura/cuerpo/dictamen/sumario), el "residuo" es en realidad
    # el cuerpo del fallo — típicamente per curiam sin apertura formal.
    # 37 casos afectados, 24582 wc recuperados (H056-L0).
    _ZONAS_CUERPO = {"apertura", "cuerpo", "dictamen", "sumario"}
    if not any(zonas[k] in _ZONAS_CUERPO for k in range(n)):
        for k in range(n):
            if zonas[k] == "residuo_caso_anterior":
                zonas[k] = "cuerpo"

    return zonas, anclas


def clasificar_tipo_entrada(bloque, zonas_linea):
    """
    M13 (H089): clasifica el tipo de entrada de un bloque a partir de su
    contenido y su zonificación. Extraído del detector inline de
    procesar_archivo (v17/H051-H052) sin cambio de comportamiento.

    Devuelve:
      "sumario_con_link"   — el bloque contiene el patrón editorial
                             "(*) Sentencia del ... Ver ..." (RE_SUMARIO_LINK).
                             Señal suficiente: las firmas que arrastre por
                             solapamiento de páginas son del fallo previo.
      "sumario_editorial"  — el bloque no tiene zonas de cuerpo, dispositivo
                             ni firma → contenido editorial puro (H051/H052).
      None                 — es un fallo parseable (sigue el flujo normal).

    Prioridad: sumario_con_link se evalúa primero (no depende de zonas).
    """
    if any(RE_SUMARIO_LINK.match(ln.strip()) for ln in bloque):
        return "sumario_con_link"
    _zonas_set = set(zonas_linea)
    if (
        "cuerpo" not in _zonas_set
        and "dispositivo" not in _zonas_set
        and "firma" not in _zonas_set
    ):
        return "sumario_editorial"
    return None


def extraer_segmentos(zonas, bloque):
    """
    Extrae segmentos contiguos de zonas con sus fronteras y word count.

    Retorna lista de dicts:
      zona, segmento (1-indexed por zona), linea_ini, linea_fin, n_lineas, wc
    """
    if not zonas:
        return []

    segmentos = []
    conteo_zona = Counter()  # para numerar segmentos por zona

    zona_actual = zonas[0]
    ini_actual = 0

    for k in range(1, len(zonas)):
        if zonas[k] != zona_actual:
            # Cerrar segmento anterior
            conteo_zona[zona_actual] += 1
            wc = sum(
                len(re.findall(r'\b\w+\b', bloque[j]))
                for j in range(ini_actual, k)
            )
            segmentos.append({
                "zona": zona_actual,
                "segmento": conteo_zona[zona_actual],
                "linea_ini": ini_actual,
                "linea_fin": k - 1,
                "n_lineas": k - ini_actual,
                "wc": wc,
            })
            zona_actual = zonas[k]
            ini_actual = k

    # Último segmento
    conteo_zona[zona_actual] += 1
    wc = sum(
        len(re.findall(r'\b\w+\b', bloque[j]))
        for j in range(ini_actual, len(zonas))
    )
    segmentos.append({
        "zona": zona_actual,
        "segmento": conteo_zona[zona_actual],
        "linea_ini": ini_actual,
        "linea_fin": len(zonas) - 1,
        "n_lineas": len(zonas) - ini_actual,
        "wc": wc,
    })

    return segmentos


# ── Procesamiento de un archivo ───────────────────────────────────────────────

# ── H086 R5: detección del dispositivo — motor parametrizado ──────────────────
# Las 5 capas (Tier 1→2→3→3b→4) eran el mismo bucle copiado, difiriendo solo en
# 4 perillas: rango, exclusión de dictamen, detector (es_candidato) y fallback.
# Colapsadas a un motor _barrer() único + 5 llamadas configuradas en cascada.
# Patrones que antes se compilaban en cada llamada, ahora a nivel de módulo.

# Tier 2: patrones .search() mid-line (la fórmula viene pegada al final de la
# oración anterior, no arranca línea). Restringidos a fórmulas seguras + guardas.
_T2_PATS = [
    re.compile(r"Por ello[,.]?\s", re.I),
    re.compile(r"Por lo expuesto\b", re.I),
    re.compile(r"Por las razones\b", re.I),
    re.compile(r"Por lo expresado\b", re.I),
    re.compile(r"Por las consideraciones\b", re.I),
    re.compile(r"Que[,]?\s+por\s+ello\b", re.I),
    re.compile(r"O[íi]dos?\s+(el|la|los|las)\b", re.I),
]

# Tier 3b: recorta el prefijo "Por ello/..." para mirar la palabra siguiente y
# distinguir dispositivo del Tribunal ("se confirma") de conclusión del
# Procurador ("opino") dentro de la zona del dictamen.
_T3B_ARG_RE = re.compile(
    r"^(?:Por\s+(?:ello|lo\s+expuesto|todo\s+lo\s+expuesto|"
    r"todo\s+ello|lo\s+expresado|las\s+razones|las\s+consideraciones|"
    r"estos?\s+razones|los\s+fundamentos)[,.]?\s*)",
    re.I,
)

# Tier 4: fórmulas de cierre alternativas (fallos que no abren con "Por ello").
_RE_ASI = re.compile(
    r"[Aa]sí se resuelve"
    r"|[Ee]l\s+[Tt]ribunal\s+resuelve",
    re.I,
)

# ── B124 · regla P (H130) · RE_PERF v2 ────────────────────────────────────────
# Performatividad del dispositivo para la regla P de _barrer: entre los
# candidatos-CON-firma de la ventana, preferir el PRIMER performativo (y solo si
# ninguno lo es, caer al primer-con-firma = comportamiento v19). El dispositivo
# de fondo abre con marca performativa; el argumental que se cuela antes ("En
# consecuencia, no discutida…", "Por ello, si bien…") es no-performativo y se
# saltea.
#
# v2 (H130) extiende v1 (`se <verbo>`, H129) a los performativos de MAYORIA sin
# `se`, AUDITADOS en disco (audit_resuelve_sin_se.py, 5890 casos, ventana del
# dispositivo): únicas formas sin-`se` entre candidatos-con-firma → "el Tribunal
# resuelve" (300) y "resuelve:" (23 = "Tribunal" hifenado por el wrap del OCR /
# palabras interpuestas / "esta Corte Suprema" / "la mayoría del Tribunal" /
# "…y resuelve:"). El audit probó OTRO_RESUELVE=0 y ESTA/LA_CORTE/RESUELVE_UP=0
# en la ventana → NO hay "el a quo/la cámara resuelve": el over-match de
# instancia inferior no se materializa. Sin v2, P saltea la mayoría sin-`se` y
# ancla en una concurrencia según-su-voto con `se` (mis-pick 331_p1028 = causa
# del rollback v20→v19 en H129).
RE_PERF = re.compile(
    r"\bse\s+(?:(?:lo|la|los|las|le|les)\s+)?"
    r"(?:resuelve|decide|declara[n]?|revoca[n]?|confirma[n]?|"
    r"hace[n]?\s+lugar|deja[n]?\s+sin\s+efecto|rechaza[n]?|desestima[n]?|"
    r"tiene[n]?\s+por|admite[n]?|anula[n]?|hace\s+saber|intima)\b"
    r"|\b(?:el\s+[Tt]ribunal|esta\s+[Cc]orte|la\s+[Cc]orte)\s+resuelve\b"
    r"|\bresuelve\s*:",
    re.IGNORECASE)


def _cand_estructural(stripped):
    """Tiers 1 y 3: apertura estructural (detectar_apertura_dispositivo)."""
    es_disp, _ = detectar_apertura_dispositivo(stripped)
    return es_disp


def _cand_t2(stripped):
    """Tier 2: .search() mid-line + start>0 + fin de oración/'Que' + argumental.
    Replica la semántica per-patrón con `continue` del bucle original."""
    for pat in _T2_PATS:
        m = pat.search(stripped)
        if m and m.start() > 0:
            pre = stripped[:m.start()].rstrip()
            if not (pre.endswith(".") or pre.endswith(")")
                    or stripped.lstrip().startswith("Que")):
                continue
            rest = stripped[m.end():].strip()
            fw = rest.split()[0].lower().rstrip(",;") if rest.split() else ""
            if fw in POR_ELLO_ARGUMENTAL:
                continue
            return True
    return False


def _cand_t3b(stripped):
    """Tier 3b: apertura estructural + guarda argumental propia (_T3B_ARG_RE)."""
    es_disp, _ = detectar_apertura_dispositivo(stripped)
    if not es_disp:
        return False
    rest = _T3B_ARG_RE.sub("", stripped).strip()
    fw = rest.split()[0].lower().rstrip(",;") if rest.split() else ""
    if fw in POR_ELLO_ARGUMENTAL:
        return False
    return True


def _cand_t4(stripped):
    """Tier 4: fórmulas de cierre alternativas (_RE_ASI)."""
    return bool(_RE_ASI.search(stripped))


# ── B141 (H174): falso terminador de oración en el chunk del dispositivo ─────
# El chunk corta en la primera línea terminada en '.', pero una inicial
# anonimizada («...sus hijos E.») o un enumerador romano («se resuelve: I.»)
# a fin de línea NO es fin de oración: partía el dispositivo y escondía el
# verbo de fondo (testigos 329_p3894 y 341_p1148, mérito perdido; familia de
# 16 adjudicada en H174 contra texto real). Freno anti-contaminación: si lo
# próximo con contenido es la firma, el fin era genuino y se corta igual
# (332_p238 «M. E. A. V.», 340_p397 «Sala B.»). Reusa linea_es_firma_de_juez
# (fuente única — no regex paralela). El residual de banner partido en 3
# líneas físicas (333_p1951, 343_p2080) es clase M21 Fase 3, NO se toca acá.
# ACOPLE: requiere clasificador_disposicion >= 1.11 (guard in limine) para no
# fabricar FP de mérito en 330_p3777 al destapar «Rechazar in limine la demanda».
RE_FALSO_TERMINADOR = re.compile(
    r"(?:^|\s)(?:[A-ZÁÉÍÓÚÑ]|II|III|IV|VI|VII|VIII|IX)\.$")


def _proxima_linea_es_firma(bloque, m2):
    """Peek B141: ¿la próxima línea con contenido (post-banner) es firma?"""
    for j in range(m2, min(m2 + 8, len(bloque))):
        s = re.sub(r"\s+", " ", RE_RUNNING_HEAD.sub(" ", bloque[j])).strip()
        if not s:
            continue
        return linea_es_firma_de_juez(s)
    return False


def _barrer(bloque, rango, lineas_dictamen, *,
            excluye_dictamen, es_candidato, permite_fallback):
    """
    Motor único de las 5 capas. Barre rango=(inicio, fin) sobre bloque. En cada
    línea no vacía (y no excluida, si excluye_dictamen) evalúa es_candidato. Si
    es candidata: arma el chunk (hasta 6 líneas o hasta el primer '.') y valida
    firma de juez en k+1..k+41.

    REGLA P (B124 · H130): entre los candidatos-CON-firma, devuelve el PRIMER
    PERFORMATIVO (RE_PERF v2). Si ninguno es performativo, cae al PRIMER
    candidato-con-firma (= comportamiento v19, sin regresión). El argumental que
    se cuela antes del dispositivo de fondo ("En consecuencia, no discutida…",
    "Por ello, si bien…") es no-performativo y se saltea; recupera el dispositivo
    real cuando el primer-con-firma es argumental (B123/B124). Si permite_fallback
    y no hubo NINGÚN candidato-con-firma, devuelve el primer candidato sin firma
    (= fallback B059).
    """
    inicio, fin = rango
    _fb_idx, _fb_text = None, None        # primer candidato (con o sin firma) — B059
    _firma_idx, _firma_text = None, None  # primer candidato CON firma — fallback de P (= v19)
    for k in range(inicio, fin):
        if excluye_dictamen and k in lineas_dictamen:
            continue
        stripped = bloque[k].strip()
        if not stripped:
            continue
        if not es_candidato(stripped):
            continue
        # B122/B118 (M21 · H126): el running-head editorial intercalado deja
        # líneas EN BLANCO del OCR que, contadas, agotaban el presupuesto de 6
        # del chunk antes del '.' real → el verbo de disposición caía pasado el
        # corte (outcome=otro). Saltearlas SIN contarlas libera el presupuesto y
        # el chunk llega a la disposición. No mueve k (=por_ello_idx) ni la
        # ventana de firma k+1..k+41 (loop aparte). Lever validado corpus-wide
        # en PoC H125 (+50 flips, 0 regresiones); el banner como ruido residual
        # lo deshifena/colapsa classify_outcome (el masking de Fase 2 lo limpia).
        chunk, n_lineas, m2 = [], 0, k
        while n_lineas < 6 and m2 < len(bloque):
            ln = bloque[m2]
            m2 += 1
            s = ln.strip()
            if not s:                       # vacía OCR → no cuenta presupuesto
                continue
            # M21 Fase 3 (H181): banner PARTIDO en líneas físicas — «1959» /
            # «DE JUSTICIA DE LA NACION» / «333» — que la terna-substring de
            # RE_RUNNING_HEAD no agarra (cada componente va en línea propia) y
            # que contaba hasta 3 unidades del presupuesto de 6, truncando el
            # verbo de fondo (encolados H171/H174: 333_p1951, 343_p2080,
            # 329_p59 + los 4 del costo del paso 3). Cada componente ES
            # RE_PAGE_HEADER (línea-sola: frase pelada o \d{2,6}) → skipearlo
            # SIN contar, mismo patrón que las vacías de Fase 1. Detector
            # existente reusado; no entra al chunk (higiene del pe persistido).
            # FUERA DE ALCANCE declarado: 330_p563 (dispositivo genuinamente
            # >6 líneas sin banner — el presupuesto NO se toca).
            if RE_PAGE_HEADER.match(s):     # componente de banner → no cuenta
                continue
            # M21 Fase 2 (B122/B118): enmascarar el running-head editorial. La
            # terna 'número FALLOS… número' que RE_PAGE_HEADER (línea-sola) no
            # agarra queda incrustada mid-chunk (testigo 330_p1907). Se saca como
            # substring; si la línea era SOLO banner queda vacía → no cuenta
            # presupuesto (libera el chunk hacia el verbo de fondo, igual que las
            # vacías → recupera el dispositivo truncado). Si tenía contenido, el
            # contenido se conserva sin el banner. 463 banners / 0 FP (verificado).
            ln = RE_RUNNING_HEAD.sub(" ", ln)
            s = re.sub(r"\s+", " ", ln).strip()
            if not s:                       # era solo banner → no cuenta
                continue
            chunk.append(ln)
            n_lineas += 1
            if s.endswith("."):
                # B141 (H174): inicial suelta / numeral romano = falso
                # terminador, salvo que lo próximo sea la firma (fin genuino).
                if (RE_FALSO_TERMINADOR.search(s)
                        and not _proxima_linea_es_firma(bloque, m2)):
                    continue
                break
        candidate_text = " ".join(chunk).strip()
        if permite_fallback and _fb_idx is None:
            _fb_idx, _fb_text = k, candidate_text
        if any(linea_es_firma_de_juez(bloque[j])
               for j in range(k + 1, min(k + 41, len(bloque)))):
            # Regla P: el primer performativo-con-firma gana de una.
            if RE_PERF.search(candidate_text):
                return k, candidate_text
            # No-performativo con firma: recordarlo como fallback (primer-con-firma = v19).
            if _firma_idx is None:
                _firma_idx, _firma_text = k, candidate_text
    # Ningún performativo-con-firma → primer-con-firma (idéntico a v19).
    if _firma_idx is not None:
        return _firma_idx, _firma_text
    if permite_fallback and _fb_idx is not None:
        return _fb_idx, _fb_text
    return None, ""


def resolver_dispositivo(bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv):
    """
    Cascada Tier 1→2→3→3b→4 de detección del dispositivo. Devuelve
    (por_ello_idx, por_ello_text).

    H085 (R1): extraída de procesar_archivo sin cambios de comportamiento.
    H086 (R5): los 5 tiers (el mismo bucle copiado) colapsados a 5 llamadas a
    _barrer() configuradas por 4 perillas. Equivalencia exacta verificada; ver
    _barrer y los detectores _cand_* arriba.
    """
    # Cascada de inicio: apertura_rel → dictamen_end+1 → 0.
    # Techo: inicio_votos_indiv (no buscar dentro de votos separados) solo si
    # los votos están después de la apertura (B013, 302 casos).
    dictamen_end = max(lineas_dictamen) if lineas_dictamen else None
    if apertura_rel is not None:
        inicio_busqueda = apertura_rel
    elif dictamen_end is not None:
        inicio_busqueda = dictamen_end + 1
    else:
        inicio_busqueda = 0
    if (inicio_votos_indiv is not None
            and (apertura_rel is None or inicio_votos_indiv > apertura_rel)):
        fin_busqueda = inicio_votos_indiv
    else:
        fin_busqueda = len(bloque)

    # Tier 1: estructural, rango base, excluye dictamen, con fallback (B059).
    por_ello_idx, por_ello_text = _barrer(
        bloque, (inicio_busqueda, fin_busqueda), lineas_dictamen,
        excluye_dictamen=True, es_candidato=_cand_estructural,
        permite_fallback=True)

    # Tier 2 (H041): .search() mid-line, rango base, excluye dictamen, sin fallback.
    if por_ello_idx is None:
        por_ello_idx, por_ello_text = _barrer(
            bloque, (inicio_busqueda, fin_busqueda), lineas_dictamen,
            excluye_dictamen=True, es_candidato=_cand_t2,
            permite_fallback=False)

    # Tier 3 (B067): estructural, rango sin techo, excluye dictamen, con fallback.
    if por_ello_idx is None:
        por_ello_idx, por_ello_text = _barrer(
            bloque, (inicio_busqueda, len(bloque)), lineas_dictamen,
            excluye_dictamen=True, es_candidato=_cand_estructural,
            permite_fallback=True)

    # Tier 3b (B085): estructural+arg, rango 0→len, NO excluye dictamen, sin fallback.
    if por_ello_idx is None:
        por_ello_idx, por_ello_text = _barrer(
            bloque, (0, len(bloque)), lineas_dictamen,
            excluye_dictamen=False, es_candidato=_cand_t3b,
            permite_fallback=False)

    # Tier 4 (B084+B086): fórmulas alternativas, rango sin techo, excluye dictamen.
    if por_ello_idx is None:
        por_ello_idx, por_ello_text = _barrer(
            bloque, (inicio_busqueda, len(bloque)), lineas_dictamen,
            excluye_dictamen=True, es_candidato=_cand_t4,
            permite_fallback=False)

    return por_ello_idx, por_ello_text


def refinar_status_localizacion(status_loc, apertura_rel, ancla_inicio):
    """
    Refina el status de localización del catálogo con dos sufijos de auditoría:

      - falta de marcador clásico de apertura (apertura_rel is None):
        "ok" → "ok_sin_marcador_apertura"; otro → "<status>_sin_marcador".
      - ancla de inicio (v18 Fase F), registrada para auditoría posterior:
        'titulo'   → sin cambio (caso limpio, ancló por token del título)
        'vistos'   → sufijo "_ancla_vistos" (ancló por "Vistos los autos")
        'catalogo' → sufijo "_ancla_catalogo" (sin refinamiento, linea del catálogo)
    """
    s = status_loc
    if apertura_rel is None:
        s = "ok_sin_marcador_apertura" if status_loc == "ok" else status_loc + "_sin_marcador"
    if ancla_inicio == 'vistos':
        s += "_ancla_vistos"
    elif ancla_inicio == 'catalogo':
        s += "_ancla_catalogo"
    return s


def procesar_archivo(filepath, fallos_del_archivo, headers_archivo, primer_token_por_caso, siguiente_caso):
    """
    v15: procesa un archivo .md y devuelve (casos, votos, zonas, editorial, descon).

    fallos_del_archivo: lista de dicts con las filas de fallos_localizados.csv
    correspondientes a este archivo. Cada fila tiene al menos:
      caso_id_canonico, tomo, pagina_inicio, pagina_fin (puede ser ''),
      linea_inicio, linea_fin (puede ser ''), nombres_indice, status.

    headers_archivo: lista [(linea_header, pagina), ...] ordenada, del mapa.
    primer_token_por_caso: dict {caso_id_canonico: primer_token}.
    siguiente_caso: dict {caso_id_canonico: caso_id_canonico_siguiente}.

    Cada fallo se procesa con su bloque del catálogo, y dentro del bloque se
    detecta la frontera real con el fallo siguiente (linea_fin_real). Los
    conteos de palabras y el texto de los votos se calculan hasta linea_fin_real,
    no hasta el final del bloque.
    """
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Tomo (lo seguimos sacando del filename para tener un fallback, aunque
    # también está en cada fila del catálogo)
    tomo_match = RE_TOMO.search(filepath.name)
    tomo_filename = int(tomo_match.group(1)) if tomo_match else 0

    casos_out  = []
    votos_out  = []
    zonas_out  = []
    desconocidos_global = Counter()

    for fallo_meta in fallos_del_archivo:
        linea_inicio = fallo_meta["linea_inicio"]
        linea_fin    = fallo_meta["linea_fin"]
        caso_id_canonico = fallo_meta["caso_id_canonico"]
        tomo = int(fallo_meta["tomo"]) if fallo_meta["tomo"] else tomo_filename
        nombres_indice = fallo_meta.get("nombres_indice", "")
        status_loc = fallo_meta.get("status", "")

        # Extraer el bloque del fallo
        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin)
        if not bloque:
            continue  # bloque vacío (linea_inicio inválida); saltear

        # ── B074: pre-computar posición del título como lower-bound ─────────
        # Si el título del caso actual aparece en las primeras 15 líneas del
        # bloque, usarlo como li para detectar_fin_real. Así buscar_atras no
        # captura firma del caso anterior incluida en el residuo del bloque.
        # Si no se encuentra en 15 líneas → li original → baseline idéntico.
        # B089 (H074): normalizar tildes (consistencia con refinar_inicio_por_titulo).
        _li_for_dfr = int(linea_inicio)
        _token_titulo = primer_token_de_caratula(nombres_indice)
        if _token_titulo and len(_token_titulo) >= 4:
            _tok_norm = _strip_accents(_token_titulo)
            _pat_titulo = re.compile(r'\b' + re.escape(_tok_norm) + r'\b', re.I)
            for _k, _ln in enumerate(bloque[:15]):
                if _pat_titulo.search(_strip_accents(_ln)):
                    _li_for_dfr = int(linea_inicio) + _k
                    break

        # ── NUEVO v15: detectar fin real del fallo ──────────────────────────
        # Buscar la frontera con el fallo siguiente (carátula/sumario/marcador)
        # para detectar dónde termina realmente el contenido decisorio.
        siguiente = siguiente_caso.get(caso_id_canonico)
        primer_token_siguiente = primer_token_por_caso.get(siguiente, "") if siguiente else ""
        prox_header = proximo_header_despues_de(headers_archivo, int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1)
        # B147-1A (H190): tokens del nombre PROPIO para el guard apéndice-1C
        # del retroceso de frontera (retroceder_frontera).
        _tokens_nombre_propio = _tokens_nombre_significativos(nombres_indice)
        linea_fin_real, status_fin, pista_fin = detectar_fin_real(
            lines,
            _li_for_dfr,
            int(linea_fin) if linea_fin not in ("", None) else len(lines) - 1,
            prox_header,
            primer_token_siguiente,
            _tokens_nombre_propio
        )

        # Reconstruir el bloque hasta linea_fin_real (puede extender el bloque
        # original si la firma cae más allá del linea_fin del catálogo).
        bloque = construir_bloque_desde_localizacion(lines, linea_inicio, linea_fin_real)
        if not bloque:
            continue

        # ── v18 Fase F: refinar linea_inicio por título ──────────────────────
        # Recorta residuo del fallo anterior incluido por el localizador
        # (arranca desde header de página compartida). Señal primaria: token
        # del título en nombres_indice. Secundaria: "Vistos los autos".
        # Fallback: linea_inicio del catálogo sin cambios.
        # ancla_inicio se propaga a status_localizacion para auditoría.
        offset_titulo, ancla_inicio = refinar_inicio_por_titulo(
            bloque, nombres_indice
        )
        if offset_titulo > 0:
            linea_inicio = int(linea_inicio) + offset_titulo
            bloque = bloque[offset_titulo:]
            if not bloque:
                continue

        # Detectar apertura clásica dentro del bloque (para apertura_tipo y
        # como referencia para find_case_name del cuerpo)
        apertura_tipo, apertura_rel = detectar_apertura_en_bloque(bloque)
        # apertura_idx absoluto (en `lines`) cuando hay marcador, para
        # compatibilidad con find_case_name y find_tribunal_origen que
        # esperan índice global
        if apertura_rel is not None:
            apertura_idx = int(linea_inicio) + apertura_rel
        else:
            apertura_idx = int(linea_inicio)
            apertura_tipo = ""

        # ── status_localizacion: refinamiento (→ refinar_status_localizacion) ─
        status_loc_final = refinar_status_localizacion(
            status_loc, apertura_rel, ancla_inicio)

        # ── M13 (H089): zonificar primero ────────────────────────────────────
        # zonificar_bloque es pura y su resultado se reutiliza río abajo
        # (lineas_dictamen, residuo, M09, extraer_segmentos), así que
        # adelantarla respecto del detector sumario_con_link no cambia
        # comportamiento. H052: devuelve (zonas_por_linea, anclas); _anclas
        # no se usa.
        _zonas_linea, _anclas = zonificar_bloque(bloque)

        # ── v17/H051/H052: detector de sumarios (→ clasificar_tipo_entrada) ───
        # sumario_con_link: patrón "(*) Sentencia del ... Ver ..." → nota
        # editorial con link, campos analíticos vacíos. La detección no depende
        # de si el parser hallaría firma: en solapamiento de páginas el bloque
        # arrastra firma del fallo previo, pero el patrón es señal suficiente.
        # sumario_editorial: bloque sin zonas de cuerpo/dispositivo/firma.
        # En ambos casos se carga el caso y se salta el resto del procesamiento.
        _tipo_entrada = clasificar_tipo_entrada(bloque, _zonas_linea)
        if _tipo_entrada is not None:
            casos_out.append(construir_caso_sumario_link(
                caso_id_canonico=caso_id_canonico,
                tomo=tomo,
                nombres_indice=nombres_indice,
                source_file=filepath.name,
                linea_inicio=linea_inicio,
                linea_fin=linea_fin,
                linea_fin_real=linea_fin_real,
                status_loc_final=status_loc_final,
                status_fin=status_fin,
                pista_fin=pista_fin,
            ))
            # construir_caso_sumario_link deja tipo_entrada="sumario_con_link"
            # por default; reclasificar si el zonificador lo marcó editorial.
            if _tipo_entrada == "sumario_editorial":
                casos_out[-1]["tipo_entrada"] = "sumario_editorial"
            continue

        # Fecha del fallo. v16: cambio respecto a v15.
        # v15 buscaba en las primeras 8 líneas del bloque, pero el bloque
        # arranca con sumarios y dictamen, no con el fallo. La fecha del
        # fallo está cerca del marcador FALLO DE LA CORTE SUPREMA o, si no
        # hay marcador detectado, es la última fecha "Buenos Aires" del
        # bloque (la del dictamen suele estar antes).
        # NOTA: lineas_dictamen se calcula más abajo, pero _zonas_linea
        # ya está disponible. Mejora futura: excluir líneas con zona
        # "dictamen" de la búsqueda de fecha del fallo.
        fecha_str = ""
        if apertura_rel is not None:
            # Caso (a): hay marcador clásico. Buscar fecha en las 10 líneas
            # siguientes al marcador.
            for k in range(apertura_rel + 1, min(apertura_rel + 11, len(bloque))):
                m = RE_FECHA_EXTRACT.search(bloque[k])
                if m:
                    fecha_str = m.group(1)
                    break
        else:
            # Caso (b): sin marcador. Buscar la ÚLTIMA fecha del bloque.
            # La última fecha "Buenos Aires" suele ser la del fallo, ya que
            # la del dictamen del Procurador viene antes en el texto.
            for k in range(len(bloque) - 1, -1, -1):
                m = RE_FECHA_EXTRACT.search(bloque[k])
                if m:
                    fecha_str = m.group(1)
                    break

        # Fallback: si no encontró nada con la lógica nueva, usar la primera
        # fecha del bloque (comportamiento v15).
        if not fecha_str:
            for k, ln in enumerate(bloque[:30]):
                m = RE_FECHA_EXTRACT.search(ln)
                if m:
                    fecha_str = m.group(1)
                    break

        # case_name del cuerpo. v18: Fix 1 — V1 como fuente primaria.
        #
        # Estrategia primaria: extraer_caratula_v1 busca 'Vistos los autos:
        # "X"' desde apertura_rel hacia adelante. Cobertura medida: 67%
        # del corpus (Auditoría B, sesión XV). Captura limpia, sin las
        # citas doctrinales del dictamen que rompían find_case_name viejo.
        #
        # Fallback: find_case_name (heurística v12) cuando V1 no encuentra.
        # Si tampoco hay apertura_rel, queda vacío.
        #
        # Columna shadow case_name_cuerpo_legacy guarda lo que hubiera
        # devuelto find_case_name siempre, para auditar el diff post-fix.
        # Eliminable en una corrida posterior cuando el fix esté validado.
        if apertura_rel is not None:
            case_name_cuerpo_legacy = find_case_name(lines, apertura_idx)
            case_name_cuerpo_v1 = extraer_caratula_v1(bloque, apertura_rel)
            case_name_cuerpo = case_name_cuerpo_v1 or case_name_cuerpo_legacy
        else:
            case_name_cuerpo_legacy = ""
            case_name_cuerpo = ""

        # Tribunal de origen
        tribunal_str = find_tribunal_origen(lines, apertura_idx, apertura_idx + len(bloque))

        # ── H052: derivar lineas_dictamen del zonificador ─────────────
        # Reemplaza el loop en_dictamen (v12-v17) que tenía un bug: el
        # `continue` dentro de en_dictamen saltaba la detección de votos
        # y dispositivo, haciendo que si el dictamen no cerraba bien,
        # todo el bloque quedara como dictamen. El zonificador usa anclas
        # y no tiene este problema.
        lineas_dictamen = {k for k, z in enumerate(_zonas_linea)
                          if z == "dictamen"}
        dictamen_presente = bool(lineas_dictamen)

        # H055: líneas de residuo del caso anterior (excluir del word_count)
        lineas_residuo = {k for k, z in enumerate(_zonas_linea)
                         if z == "residuo_caso_anterior"}

        # M09: constraint de zona — excluir líneas fuera de zona de fallo
        # para detección de votos/disidencias. Protege contra FP en sumarios,
        # residuo del caso anterior, epílogo y headers de página.
        # Validado: 0 regresiones sobre 5667 fallos (poc_m09.py).
        _ZONAS_FALLO = {"apertura", "cuerpo", "dispositivo", "firma", "voto_separado"}
        lineas_excluir = {k for k, z in enumerate(_zonas_linea)
                         if z not in _ZONAS_FALLO}

        por_ello_idx       = None
        por_ello_text      = ""

        (n_votos_svoto, n_disidencias,
         inicio_votos_indiv, marcadores_votos) = detectar_votos_disidencias(
            bloque, lineas_excluir)

        # ── Dispositivo: cascada Tier 1→4 (extraída H085 R1) ───────────────
        por_ello_idx, por_ello_text = resolver_dispositivo(
            bloque, apertura_rel, lineas_dictamen, inicio_votos_indiv)

        # ── B149 fix A1 (H194): herencia del ancla del resolutor ────────────
        # El zonificador (Pasada 1) ancla dispositivo con T1; el resolutor lo
        # adjudica con la cascada completa T1→4 (regla P, guards, ventana). Si
        # el indice ya adjudicado cae en zona 'cuerpo', la zona HEREDA el
        # ancla: cuerpo→dispositivo desde por_ello_idx hasta la primera zona
        # de cierre. GUARD de alcance: SOLO zona 'cuerpo' — los 7 casos
        # zona 'dictamen' del flip-set son dictamen-sin-cierre (el fallo entero
        # engullido, rangos 111-1213 lineas → B159, NO se tocan). Consumidores
        # previos de _zonas_linea inmunes por construccion (lineas_dictamen/
        # residuo no tocan cuerpo; _ZONAS_FALLO contiene cuerpo y dispositivo);
        # extraer_segmentos corre despues y ve las etiquetas nuevas. Flip-set
        # sellado 25/25 TP: scripts/diagnostico/H194/poc_b149_a1_flipset.csv.
        if por_ello_idx is not None and _zonas_linea[por_ello_idx] == "cuerpo":
            _fin_disp = next(
                (j for j in range(por_ello_idx + 1, len(_zonas_linea))
                 if _zonas_linea[j] in ("firma", "voto_separado", "epilogo")),
                len(_zonas_linea))
            for _j in range(por_ello_idx, _fin_disp):
                if _zonas_linea[_j] == "cuerpo":
                    _zonas_linea[_j] = "dispositivo"

        # B082: excluir líneas de votos individuales del considerando
        # B083: excluir también residuo_caso_anterior (consistencia con wc_mayoria)
        _lineas_no_cons = set(lineas_dictamen) | lineas_residuo
        if inicio_votos_indiv is not None:
            _lineas_no_cons |= set(range(inicio_votos_indiv, len(bloque)))
        considerando_text = extraer_considerando(bloque, por_ello_idx, _lineas_no_cons)

        # R2 (H090): classify_outcome es la sede única del fallback 280/ac4,
        # incluido el caso sin dispositivo (por_ello_text vacío → "sin_dispositivo").
        outcome = classify_outcome(por_ello_text, considerando_text)

        # H078: queja + cuestion federal (sobre textos completos, pre-truncamiento)
        es_queja, queja_resultado = classify_queja(por_ello_text, case_name_cuerpo)
        # Sumario editorial = texto del bloque antes de la apertura.
        # Contiene los headers de la Secretaría de Jurisprudencia
        # ("SENTENCIA ARBITRARIA", "Cuestión federal", etc.).
        _sumario_lines = []
        if apertura_rel is not None:
            _sumario_lines = [bloque[k] for k in range(apertura_rel)
                              if k < len(bloque)]
        sumario_text = " ".join(_sumario_lines)
        tipo_cuestion_federal = classify_cuestion_federal(sumario_text, considerando_text)

        firma_raw    = ""
        firma_parsed = {"jueces": [], "voting_pattern": "sin_firma", "desconocidos": []}

        if por_ello_idx is not None:
            firma_raw = collect_firma_lines(bloque, por_ello_idx + 1)
            if firma_raw:
                firma_parsed = parse_firma(firma_raw)
                for d in firma_parsed["desconocidos"]:
                    desconocidos_global[d] += 1

        # ── A001: fallback firma inversa ──────────────────────────────
        # Si el flujo normal no encontró firma (por_ello_idx=None o
        # collect_firma_lines vacío), buscar desde el final del bloque
        # hacia atrás con guardas de zona de fallo y span mínimo.
        if firma_parsed["voting_pattern"] == "sin_firma":
            _fi_idx, _fi_raw, _fi_motivo = buscar_firma_inversa(bloque)
            if _fi_raw:
                _fi_parsed = parse_firma(_fi_raw)
                if _fi_parsed["jueces"]:
                    firma_raw = _fi_raw
                    firma_parsed = _fi_parsed
                    for d in firma_parsed["desconocidos"]:
                        desconocidos_global[d] += 1

        if inicio_votos_indiv is not None:
            lineas_mayoria = [bloque[k] for k in range(len(bloque))
                              if k not in lineas_dictamen
                              and k not in lineas_residuo
                              and k < inicio_votos_indiv]
            lineas_votos   = [bloque[k] for k in range(inicio_votos_indiv, len(bloque))]
        else:
            lineas_mayoria = [bloque[k] for k in range(len(bloque))
                              if k not in lineas_dictamen
                              and k not in lineas_residuo]
            lineas_votos   = []

        wc_mayoria = len(re.findall(r'\b\w+\b', " ".join(lineas_mayoria)))
        wc_votos   = len(re.findall(r'\b\w+\b', " ".join(lineas_votos)))
        word_count = wc_mayoria + wc_votos

        is_originaria = int(es_originaria(case_name_cuerpo, considerando_text, por_ello_text, bloque))

        if is_originaria:
            tribunal_origen_status = "originaria"
        elif tribunal_str != "SIN_TRIBUNAL_ORIGEN":
            tribunal_origen_status = "apelado_detectado"
        elif hay_tribunal_interviniente(lines, apertura_idx, apertura_idx + len(bloque)):
            tribunal_origen_status = "apelado_detectado"
        else:
            tribunal_origen_status = "sin_marcador"

        n_titulares = sum(1 for j in firma_parsed["jueces"] if j["conocido"]
                          and "(conjuez)" not in j["nombre"])
        is_full_bench = int(n_titulares == 5)

        # PASO 3 M39 (H178): is_merit DERIVADO del gate del clasificador (fuente
        # única) — extiende el patrón B136 (H169) de la originaria a TODO el corpus.
        # Llamada IDÉNTICA a derivar_recursos v0.6: disposicion() sobre el pe +
        # es_revision_fondo(disp, pe, is_originaria, considerando). El branch
        # originaria desaparece (el gate maneja la originaria adentro, vía
        # es_de_fondo) y MERIT_OUTCOMES se retira: outcome deja de definir el eje
        # de mérito (queda como eje legacy de dispositivo). GATEKEEP_OUTCOMES se
        # remueve por código muerto preexistente (0 usos, hallazgo H178).
        # Identidad de insumos parser↔deriver demostrada en disco (PoC
        # poc_paso3_m39 v0.2 A1: gate recomputado 0 diffs vs columna publicada).
        disp_gate, _reenvia_gate = disposicion(por_ello_text)
        is_merit = int(es_revision_fondo(disp_gate, por_ello_text,
                                         bool(is_originaria), considerando_text) == "si")

        jueces_nombres     = [j["nombre"] for j in firma_parsed["jueces"]]
        jueces_conocidos_l = [j["nombre"] for j in firma_parsed["jueces"] if j["conocido"]]
        # B153-ii (H191): cable re-conectado — la lista REAL del colector de
        # extraer_jueces_de_firma (paso 3) en vez del filtro not-conocido, muerto
        # por construcción (todo j entra con conocido=True) → la columna era
        # siempre vacía. NOTA: el colector es laxo (TitleCase 2-4 tokens) y en
        # ~157 casos con bleed de epílogo en firma_raw traerá partes/letrados —
        # ruido DOCUMENTADO: la columna es instrumento de auditoría, no dato
        # analítico; sirve de detector de conjueces nuevos en tomos futuros.
        jueces_descon_l    = firma_parsed["desconocidos"]

        posiciones = {}
        for j in firma_parsed["jueces"]:
            posiciones[j["nombre"]] = j["calificador"] or "mayoria"

        textos_votos = extraer_textos_votos(bloque, marcadores_votos)

        # H052: word count del dictamen, derivado del zonificador.
        # lineas_dictamen viene de las zonas (más preciso que el loop
        # en_dictamen de v12-v17: no incluye headers de página, y la
        # guarda de dictamen evita falsos positivos del dispositivo del
        # Procurador).
        wc_dictamen = sum(
            len(re.findall(r'\b\w+\b', bloque[k]))
            for k in lineas_dictamen
            if 0 <= k < len(bloque)
        )

        # ── B087: guard unanime con wcM≤4 → segun_su_voto ───────────
        # Si la firma dice "unanime" pero wc_mayoria ≤ 4 y todo el
        # contenido está en votos individuales, los jueces votaron
        # "según su voto" aunque la firma no lo marque.
        if (firma_parsed["voting_pattern"] == "unanime"
                and wc_mayoria <= 4 and wc_votos > wc_mayoria):
            firma_parsed["voting_pattern"] = "segun_su_voto"

        caso = {
            "caso_id_canonico":       caso_id_canonico,
            "tomo":                   tomo,
            "case_name_indice":       nombres_indice,
            "case_name_cuerpo":       case_name_cuerpo,
            "case_name_cuerpo_legacy": case_name_cuerpo_legacy,
            "date":                   fecha_str,
            "apertura_tipo":          apertura_tipo,
            "outcome":                outcome,
            "voting_pattern":         firma_parsed["voting_pattern"],
            "n_jueces":               len(firma_parsed["jueces"]),
            "n_titulares":            n_titulares,
            "n_votos_svoto":          n_votos_svoto,
            "n_disidencias":          n_disidencias,
            "dictamen_presente":      dictamen_presente,
            "is_originaria":          is_originaria,
            "is_full_bench":          is_full_bench,
            "is_merit_decision":      is_merit,
            "es_queja":               int(es_queja),
            "queja_resultado":        queja_resultado,
            "tipo_cuestion_federal":  tipo_cuestion_federal,
            "word_count":             word_count,
            "wc_mayoria":             wc_mayoria,
            "wc_votos":               wc_votos,
            "wc_considerando":       len(re.findall(r'\b\w+\b', considerando_text)),
            "wc_dictamen":            wc_dictamen,
            "firma_raw":              firma_raw,
            "jueces":                 " | ".join(jueces_nombres),
            "jueces_conocidos":       " | ".join(jueces_conocidos_l),
            "jueces_desconocidos":    " | ".join(jueces_descon_l),
            "posiciones":             json.dumps(posiciones, ensure_ascii=False),
            "tribunal_origen":        tribunal_str,
            "tribunal_origen_status": tribunal_origen_status,
            "por_ello_text":          por_ello_text,
            "considerando_text":      considerando_text,
            "source_file":            filepath.name,
            "linea_inicio":           int(linea_inicio),
            "linea_fin":              int(linea_fin) if linea_fin not in ("", None) else "",
            "linea_fin_real":         linea_fin_real,
            "status_localizacion":    status_loc_final,
            "status_fin":             status_fin,
            "pista_fin":              pista_fin,
            "tipo_entrada":           "fallo",
        }
        casos_out.append(caso)

        # ── H053: extraer segmentos de zonas para CSV zona-centered ───────
        segmentos = extraer_segmentos(_zonas_linea, bloque)
        for seg in segmentos:
            seg["caso_id_canonico"] = caso_id_canonico
            seg["tomo"] = tomo
            zonas_out.append(seg)

        for j in firma_parsed["jueces"]:
            if not j["conocido"]:
                continue
            juez_nombre = j["nombre"]
            posicion    = j["calificador"] or "mayoria"
            texto_voto = textos_votos.get(juez_nombre, "")
            wc_voto    = len(re.findall(r'\b\w+\b', texto_voto))
            if texto_voto:
                clasif = clasificar_tipo_voto(
                    texto_voto, wc_voto, caso["is_merit_decision"]
                )
                tipo_voto_sep     = clasif["tipo_voto_sep"]
                fragmenta_ratio   = clasif["fragmenta_ratio"]
                punto_divergencia = clasif["punto_divergencia"] or ""
            else:
                tipo_voto_sep     = ""
                fragmenta_ratio   = ""
                punto_divergencia = ""
            voto = {
                "caso_id_canonico":   caso_id_canonico,
                "tomo":               tomo,
                "date":               fecha_str,
                "juez":               juez_nombre,
                "posicion":           posicion,
                "es_conocido":        1,
                "outcome":            caso["outcome"],
                "voting_pattern":     caso["voting_pattern"],
                "is_originaria":      caso["is_originaria"],
                "is_full_bench":      caso["is_full_bench"],
                "is_merit_decision":  caso["is_merit_decision"],
                "wc_mayoria":         caso["wc_mayoria"],
                "wc_votos":           caso["wc_votos"],
                "dictamen_presente":  caso["dictamen_presente"],
                "texto_voto":         texto_voto[:5000],
                "wc_voto":            wc_voto,
                "tipo_voto_sep":      tipo_voto_sep,
                "fragmenta_ratio":    fragmenta_ratio,
                "punto_divergencia":  punto_divergencia,
            }
            votos_out.append(voto)

    # H061: clasificación editorial con subtipos (parser_editorial.py)
    editorial_out = []
    if casos_out:
        ultimo_lfr = max(int(c["linea_fin_real"]) for c in casos_out
                         if c["linea_fin_real"] not in ("", None))
        editorial_out = clasificar_editorial(
            lines, tomo, filepath.name, ultimo_lfr + 1
        )

    return casos_out, votos_out, zonas_out, editorial_out, desconocidos_global

# ── Orquestación ──────────────────────────────────────────────────────────────

def cargar_localizados(ruta):
    """
    Carga fallos_localizados.csv. Devuelve lista de dicts.

    v18 Fase F: los fallos con status='pagina_no_en_mapa' ya no se descartan
    automáticamente. Se intenta inferir su archivo .md y una linea_inicio
    estimada desde los vecinos del mismo tomo. El refinador de título en
    procesar_archivo corrige la linea_inicio en runtime buscando el título
    del caso en el bloque estimado.

    Si no hay ningún vecino con archivo conocido en el mismo tomo, el fallo
    se descarta igual (sin archivo no hay bloque posible).
    """
    filas = []
    descartadas_sin_localizacion = 0
    todas = []
    with open(ruta, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            todas.append(row)

    # Índice de vecinos con archivo y linea_inicio conocidos, por tomo.
    # Cada entrada: (pagina_inicio_int, archivo, linea_inicio_int)
    vecinos_por_tomo = {}
    for row in todas:
        if row.get("archivo") and row.get("linea_inicio"):
            t = row["tomo"]
            try:
                p  = int(row["pagina_inicio"])
                li = int(row["linea_inicio"])
            except (ValueError, TypeError):
                continue
            vecinos_por_tomo.setdefault(t, []).append((p, row["archivo"], li))
    for t in vecinos_por_tomo:
        vecinos_por_tomo[t].sort()

    for row in todas:
        if row["status"] == "pagina_no_en_mapa":
            # Inferir archivo y linea_inicio estimada desde vecinos del tomo
            t = row["tomo"]
            try:
                p = int(row["pagina_inicio"])
            except (ValueError, TypeError):
                descartadas_sin_localizacion += 1
                continue
            vecinos = vecinos_por_tomo.get(t, [])
            # Vecino siguiente: primer vecino con pagina > p
            sig_arch = None
            sig_li   = None
            for vp, va, vli in vecinos:
                if vp > p:
                    sig_arch = va
                    sig_li   = vli
                    break
            # Si no hay siguiente, usar el anterior más cercano
            if sig_arch is None:
                for vp, va, vli in reversed(vecinos):
                    if vp < p:
                        sig_arch = va
                        sig_li   = vli
                        break
            if sig_arch is None:
                # Sin vecinos: imposible inferir archivo
                descartadas_sin_localizacion += 1
                continue
            row = dict(row)  # no mutar el original
            row["archivo"]      = sig_arch
            # linea_inicio estimada: ventana de 200 líneas antes del vecino
            # siguiente. El refinador de título la corrige en runtime.
            row["linea_inicio"] = str(max(0, sig_li - 200))
            row["linea_fin"]    = str(sig_li - 1)
            filas.append(row)
            continue

        # Casos normales: validar que tengan linea_inicio
        if not row.get("linea_inicio"):
            descartadas_sin_localizacion += 1
            continue
        filas.append(row)

    return filas, descartadas_sin_localizacion


def agrupar_por_archivo(filas, carpeta_corpus):
    """
    Devuelve dict {Path(.md): [filas]} ordenado de manera estable.
    Las filas dentro de cada archivo se ordenan por linea_inicio.
    """
    carpeta = Path(carpeta_corpus)
    grupos = {}
    for row in filas:
        archivo_nombre = row["archivo"]
        if not archivo_nombre:
            continue
        clave = carpeta / archivo_nombre
        grupos.setdefault(clave, []).append(row)
    for clave in grupos:
        grupos[clave].sort(key=lambda r: int(r["linea_inicio"]))
    return grupos


def main():
    ap = argparse.ArgumentParser(description="CSJN Fallos Parser v16 (con mapa + fin real + fix fechas)")
    ap.add_argument("--localizados", required=True,
                    help="CSV con fallos localizados (output del cruce catalogo+mapa)")
    ap.add_argument("--mapa", required=True,
                    help="CSV con mapa de páginas (mapa_paginas.csv)")
    ap.add_argument("--corpus", required=True,
                    help="Directorio con los archivos LibroVol*.md")
    ap.add_argument("--output", default="../../output/parser/csjn_casos.csv",
                    help="CSV de salida (case-centered)")
    ap.add_argument("--output-votos", default=None,
                    help="CSV de salida (vote-centered). Default: <output>_votos.csv")
    ap.add_argument("--output-zonas", default=None,
                    help="CSV de salida (zone-centered). Default: <output>_zonas.csv")
    args = ap.parse_args()

    # Cargar fallos del catálogo + cruce
    filas_loc, n_sin_loc = cargar_localizados(args.localizados)
    print(f"Fallos cargados desde {args.localizados}: {len(filas_loc)}")
    if n_sin_loc:
        print(f"  ({n_sin_loc} fallos descartados por status='pagina_no_en_mapa')")

    # Cargar mapa de páginas
    headers_por_archivo = cargar_proximos_headers(args.mapa)
    print(f"Archivos con headers en mapa: {len(headers_por_archivo)}")

    # Calcular primer_token_por_caso (para detección de carátula del siguiente)
    primer_token_por_caso = {
        row["caso_id_canonico"]: primer_token_de_caratula(row.get("nombres_indice", ""))
        for row in filas_loc
    }

    # Calcular siguiente_caso (cuál fallo del catálogo viene después en el
    # mismo tomo, ordenado por pagina_inicio)
    cat_por_tomo = {}
    for row in filas_loc:
        cat_por_tomo.setdefault(int(row["tomo"]), []).append({
            "caso_id_canonico": row["caso_id_canonico"],
            "pagina_inicio": int(row["pagina_inicio"]) if row["pagina_inicio"] else 0,
        })
    for t in cat_por_tomo:
        cat_por_tomo[t].sort(key=lambda r: r["pagina_inicio"])
    siguiente_caso = {}
    for t, lst in cat_por_tomo.items():
        for i, c in enumerate(lst[:-1]):
            siguiente_caso[c["caso_id_canonico"]] = lst[i + 1]["caso_id_canonico"]

    # Agrupar por archivo
    grupos = agrupar_por_archivo(filas_loc, args.corpus)
    print(f"Archivos a procesar: {len(grupos)}")
    print()

    all_casos = []
    all_votos = []
    all_zonas = []
    all_editorial = []  # B077: secciones editoriales por archivo
    desconocidos_global = Counter()

    for filepath in sorted(grupos.keys(), key=lambda p: p.name):
        if not filepath.exists():
            print(f"  {filepath.name}... ARCHIVO NO ENCONTRADO en corpus, salteado")
            continue
        try:
            tamaño = filepath.stat().st_size
        except Exception:
            tamaño = 0
        if tamaño < 200:
            print(f"  {filepath.name}... [VACÍO/incompleto, salteado: {tamaño} bytes]")
            continue

        fallos_arch = grupos[filepath]
        # Headers del archivo (los del mismo tomo que las filas que vamos a procesar)
        # Si hay múltiples tomos en un archivo (raro), tomamos los headers de todos
        tomos_archivo = set(int(r["tomo"]) for r in fallos_arch)
        headers_archivo = []
        for t in tomos_archivo:
            headers_archivo.extend(headers_por_archivo.get((t, filepath.name), []))
        headers_archivo.sort()

        print(f"  {filepath.name}... {len(fallos_arch)} fallos →", end=" ", flush=True)
        try:
            casos, votos, zonas, editorial, descon = procesar_archivo(
                filepath, fallos_arch, headers_archivo,
                primer_token_por_caso, siguiente_caso
            )
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            continue
        all_casos.extend(casos)
        all_votos.extend(votos)
        all_zonas.extend(zonas)
        all_editorial.extend(editorial)
        desconocidos_global.update(descon)
        n_ed = len(editorial)
        ed_info = f", {n_ed} ed" if n_ed else ""
        print(f"{len(casos)} procesados, {len(votos)} votos{ed_info}")

    # ── Output: caso-centered ─────────────────────────────────────────────────
    output_path = Path(args.output)
    if all_casos:
        fieldnames = [
            "caso_id_canonico", "tomo",
            "case_name_indice", "case_name_cuerpo", "case_name_cuerpo_legacy",
            "date", "apertura_tipo",
            "outcome", "voting_pattern",
            "n_jueces", "n_titulares", "n_votos_svoto", "n_disidencias",
            "dictamen_presente", "is_originaria", "is_full_bench",
            "is_merit_decision",
            "es_queja", "queja_resultado", "tipo_cuestion_federal",
            "word_count", "wc_mayoria", "wc_votos", "wc_considerando",
            "wc_dictamen",
            "jueces", "jueces_conocidos", "jueces_desconocidos",
            "posiciones", "tribunal_origen", "tribunal_origen_status",
            "source_file", "linea_inicio", "linea_fin", "linea_fin_real",
            "status_localizacion", "status_fin", "pista_fin",
            "tipo_entrada",
        ]
        with output_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            for c in all_casos:
                writer.writerow({k: c[k] for k in fieldnames})
        print(f"\n[OK] {output_path}: {len(all_casos)} casos")

    # ── Output: textos (H113: blobs crudos fuera del analítico) ───────────────
    # considerando_text / por_ello_text / firma_raw: texto pesado SIN truncar,
    # keyed por caso_id_canonico, espejo 1:1 de csjn_casos.csv (sumarios con
    # texto vacío). Saca el blob del analítico y da el considerando completo que
    # necesita materia capa 2. Misma proyección por fieldnames que zonas.
    output_textos_path = (output_path.parent /
                          (output_path.stem + "_textos" + output_path.suffix))
    if all_casos:
        fieldnames_t = ["caso_id_canonico",
                        "considerando_text", "por_ello_text", "firma_raw"]
        with output_textos_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_t, lineterminator="\n")
            writer.writeheader()
            for c in all_casos:
                writer.writerow({k: c[k] for k in fieldnames_t})
        print(f"[OK] {output_textos_path}: {len(all_casos)} filas (textos)")

    # ── Output: vote-centered ─────────────────────────────────────────────────
    output_votos_path = (Path(args.output_votos) if args.output_votos
                         else output_path.parent /
                              (output_path.stem + "_votos" + output_path.suffix))
    if all_votos:
        fieldnames_v = [
            "caso_id_canonico", "tomo", "date",
            "juez", "posicion", "es_conocido",
            "outcome", "voting_pattern", "is_originaria", "is_full_bench",
            "is_merit_decision", "wc_mayoria", "wc_votos",
            "dictamen_presente",
            "texto_voto", "wc_voto",
            "tipo_voto_sep", "fragmenta_ratio", "punto_divergencia",
        ]
        with output_votos_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_v, lineterminator="\n")
            writer.writeheader()
            for v in all_votos:
                writer.writerow(v)
        print(f"[OK] {output_votos_path}: {len(all_votos)} filas (votos)")

    # ── Output: zone-centered (H053) ──────────────────────────────────────────
    output_zonas_path = (Path(args.output_zonas) if args.output_zonas
                         else output_path.parent /
                              (output_path.stem + "_zonas" + output_path.suffix))
    if all_zonas:
        fieldnames_z = [
            "caso_id_canonico", "tomo", "zona", "segmento",
            "linea_ini", "linea_fin", "n_lineas", "wc",
        ]
        with output_zonas_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_z, lineterminator="\n")
            writer.writeheader()
            for z in all_zonas:
                writer.writerow({k: z[k] for k in fieldnames_z})
        print(f"[OK] {output_zonas_path}: {len(all_zonas)} segmentos (zonas)")

    # ── Output: editorial (H061: subtipos via parser_editorial.py) ───────────
    output_editorial_path = (output_path.parent /
                             (output_path.stem + "_editorial" + output_path.suffix))
    if all_editorial:
        fieldnames_e = [
            "tomo", "source_file", "subtipo",
            "linea_ini", "linea_fin", "n_lineas", "wc",
        ]
        with output_editorial_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames_e, lineterminator="\n")
            writer.writeheader()
            for e in all_editorial:
                writer.writerow(e)
        print(f"[OK] {output_editorial_path}: {len(all_editorial)} secciones editoriales")

    # ── Diagnóstico ───────────────────────────────────────────────────────────
    print(f"\n  CSJN Fallos Parser v{__version__}")
    print(f"  {'='*40}")
    if all_casos:
        outcomes  = Counter(c["outcome"]        for c in all_casos)
        patterns  = Counter(c["voting_pattern"] for c in all_casos)
        statuses  = Counter(c["status_localizacion"] for c in all_casos)
        print("\n── Status de localización ──")
        for k, v in statuses.most_common():
            print(f"  {k:<35} {v:>5}")
        print("\n── Outcomes ──")
        for k, v in outcomes.most_common():
            print(f"  {k:<30} {v:>5}")
        print("\n── Voting patterns ──")
        for k, v in patterns.most_common():
            print(f"  {k:<30} {v:>5}")
        n_280 = outcomes.get("inadmisible_280", 0)
        n_a4  = outcomes.get("inadmisible_acordada_4", 0)
        n_des = outcomes.get("desestima", 0)
        print(f"\n── Gatekeeping ──")
        print(f"  inadmisible_280:           {n_280}")
        print(f"  inadmisible_acordada_4:    {n_a4}")
        print(f"  desestima (residual):      {n_des}")
        if n_280 + n_a4 > 0:
            total_gatekeep = n_280 + n_a4 + n_des
            print(f"  Tasa de gatekeeping ident: {100*(n_280+n_a4)/total_gatekeep:.1f}%")
        trib_status = Counter(c["tribunal_origen_status"] for c in all_casos)
        n_orig = sum(1 for c in all_casos if c["is_originaria"])
        n_sin_disp = outcomes.get("sin_dispositivo", 0)
        print(f"\n── Originaria + dispositivo ──")
        print(f"  is_originaria=1:           {n_orig}")
        print(f"  sin_dispositivo (residual):{n_sin_disp}")
        print(f"  tribunal_origen_status:")
        for k, v in trib_status.most_common():
            print(f"    {k:<22}      {v:>5}")

        # H078: queja
        fallos_only = [c for c in all_casos if c["tipo_entrada"] == "fallo"]
        n_queja = sum(1 for c in fallos_only if c["es_queja"])
        queja_res = Counter(c["queja_resultado"] for c in fallos_only if c["es_queja"])
        print(f"\n── Queja (H078) ──")
        print(f"  es_queja=1:                {n_queja}/{len(fallos_only)}"
              f" ({100*n_queja/len(fallos_only):.1f}%)")
        for k, v in queja_res.most_common():
            print(f"    {k or '(sin_clasificar)':<22}  {v:>5}")

        # H078: cuestion federal
        tipo_cf = Counter(c["tipo_cuestion_federal"] for c in fallos_only)
        print(f"\n── Cuestión federal (H078) ──")
        for k, v in tipo_cf.most_common():
            print(f"    {k or '(sin_dato)':<22}  {v:>5}")

    if desconocidos_global:
        print("\n── Top desconocidos en firma (auditar) ──")
        for k, v in desconocidos_global.most_common(20):
            print(f"  {k!r:<60} {v:>3}")


if __name__ == "__main__":
    main()
