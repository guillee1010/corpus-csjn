# Bloque C — Diseño del refactor del parser
# Pseudocódigo + simulación sobre casos representativos

## Estado actual del parser (lo que reemplazamos)

El parser actual usa una state machine con flag `en_dictamen` que recorre el bloque línea por línea. Cuando detecta `por_ello_idx` (la primera ocurrencia de "Por ello") ancla ahí el dispositivo. Después llama:
- `find_case_name(bloque, apertura_idx)` retrocede desde `apertura_idx` buscando la carátula.
- `collect_firma_lines(bloque, por_ello_idx, max_lines=40)` busca firma en las 40 líneas siguientes.

Problemas conocidos:
- **Bug XII**: dictámenes terminan con "Por ello" propio; el parser ancla ahí y no llega al "Por ello" real del fallo.
- **Bug `case_name_cuerpo`**: ~3.000 casos con NaN porque `find_case_name` retrocede en territorio del caso anterior (Tipo 1) o de marcadores editoriales (Tipo 1 ampliado).
- **Bug Tipo 1 con bug XII enmascarado**: Brizuela y Colegio de Escribanos. Doble cascada.

## Estado objetivo

Reemplazar la state machine por **división explícita en sub-bloques**:

```
bloque crudo
    │
    ├──── pre_fallo ────► [pre-FALLO DE LA CORTE SUPREMA]
    │                      contiene: carátula, sumarios, dictamen
    │
    └──── fallo    ────► [post-FALLO DE LA CORTE SUPREMA]
                           contiene: vistos, considerandos,
                                     dispositivo, firma,
                                     (a veces) votos disidentes
```

Cada función trabaja sobre el sub-bloque correcto:
- `detectar_caratula` consulta pre_fallo (estrategias 1 y 2) y fallo (estrategia 3 = V1).
- `detectar_dispositivo` consulta solo fallo, desde abajo hacia arriba.
- `collect_firma_lines` se acota a fallo, sin riesgo de cascada por dictamen anterior.

---

## Función 1 — `dividir_bloque_en_sub_bloques`

### Invariantes

- Todo bloque tiene exactamente un `FALLO DE LA CORTE SUPREMA` real (el del caso bajo análisis).
- Pueden existir `FALLO DE LA CORTE SUPREMA` espurios:
  - En notas al pie con jurisprudencia citada (caso 329_p4804).
  - En el caso anterior si la página está compartida (Tipo 1 estricto: el FALLO espurio queda *antes* de `pagina_inicio`).
- El cierre del bloque es `Tribunal de origen:` (o equivalente final).

### Estrategia

```python
def dividir_bloque_en_sub_bloques(bloque_lineas, pagina_inicio, nombres_indice):
    """
    bloque_lineas: lista de strings (el bloque del caso)
    pagina_inicio: int — primera línea del bloque en el .md original
    nombres_indice: lista de carátulas del catálogo

    Devuelve: (pre_fallo, fallo, flags)
        pre_fallo  = lista de líneas antes del FALLO real
        fallo      = lista de líneas desde el FALLO real
        flags      = dict con metadatos de la división
    """
    flags = {
        "n_fallos_detectados": 0,
        "fallo_idx_elegido": None,
        "estrategia_usada": None,
        "tiene_nota_al_pie": False,
        "pagina_compartida": False,
    }

    # Paso 1: encontrar TODOS los "FALLO DE LA CORTE SUPREMA" del bloque
    indices_fallo = []
    for i, linea in enumerate(bloque_lineas):
        if re.match(r'^\s*FALLO DE LA CORTE SUPREMA\s*$', linea):
            indices_fallo.append(i)
    flags["n_fallos_detectados"] = len(indices_fallo)

    # Paso 2: elegir el FALLO real según cantidad
    if len(indices_fallo) == 0:
        # No hay marcador estructural. Fallback: buscar V4/V5 (Autos y Vistos)
        # como proxy del inicio del fallo
        return _fallback_sin_fallo(bloque_lineas, pagina_inicio, flags)

    elif len(indices_fallo) == 1:
        # Caso típico
        flags["fallo_idx_elegido"] = indices_fallo[0]
        flags["estrategia_usada"] = "fallo_unico"

    else:
        # Múltiples FALLO detectados. Decidir cuál es el real:
        # Regla A: si hay un FALLO seguido de "(*)" o precedido de
        #          "Dicha sentencia dice así:" → es nota al pie, descartarlo
        # Regla B: el FALLO real es el PRIMERO que está después
        #          de un "Buenos Aires, [fecha]" en formato fallo
        #          (no en formato dictamen)
        # Regla C: si Regla B no resuelve, tomar el primero que esté
        #          después de la mitad estructural del bloque
        idx_real = _elegir_fallo_real(bloque_lineas, indices_fallo, flags)
        flags["fallo_idx_elegido"] = idx_real
        flags["estrategia_usada"] = "fallo_multiple_resuelto"

    # Paso 3: dividir
    idx = flags["fallo_idx_elegido"]
    pre_fallo = bloque_lineas[:idx]
    fallo = bloque_lineas[idx:]

    # Paso 4: detectar página compartida (Tipo 1)
    # Heurística: si pre_fallo contiene "Tribunal de origen:" o un FALLO
    # espurio, hubo cierre de caso anterior dentro del pre_fallo
    if any("Tribunal de origen:" in l for l in pre_fallo):
        flags["pagina_compartida"] = True

    return pre_fallo, fallo, flags


def _elegir_fallo_real(bloque, indices_fallo, flags):
    """
    Recorre los índices candidatos y descarta espurios.
    Reglas en orden de aplicación:
    """
    # Regla A: descartar FALLOs en notas al pie
    candidatos = []
    for idx in indices_fallo:
        # Mirar 5 líneas arriba: si aparece "Dicha sentencia dice así"
        # o "(*)" como referencia a nota, es espurio
        ventana_arriba = "\n".join(bloque[max(0, idx-5):idx])
        if "Dicha sentencia dice así" in ventana_arriba:
            flags["tiene_nota_al_pie"] = True
            continue
        # Mirar si la línea anterior tiene "(*)" suelto (asterisco de nota)
        if idx > 0 and re.search(r'\(\*\)', bloque[idx-1]):
            flags["tiene_nota_al_pie"] = True
            continue
        candidatos.append(idx)

    if not candidatos:
        # Todos eran espurios? Esto no debería pasar pero por las dudas
        return indices_fallo[-1]  # tomar el último (más cerca de la firma final)

    # Regla B: si hay 1 candidato → ese
    if len(candidatos) == 1:
        return candidatos[0]

    # Regla C: si hay varios, el primer FALLO después del primer
    # "Buenos Aires, [fecha]" en formato canónico
    # (Esta regla cubre el caso de Tipo 1 con FALLO espurio del caso
    #  anterior + FALLO real más abajo)
    for idx in candidatos:
        # ¿El FALLO está seguido inmediatamente por "Buenos Aires, ..."?
        if idx + 1 < len(bloque) and re.match(
            r'^\s*Buenos Aires,\s+', bloque[idx + 1]
        ):
            return idx

    # Fallback: tomar el último
    return candidatos[-1]


def _fallback_sin_fallo(bloque, pagina_inicio, flags):
    """
    No hay FALLO DE LA CORTE SUPREMA detectable. Buscar V4/V5
    (Autos y Vistos) como proxy del inicio del fallo.
    """
    for i, linea in enumerate(bloque):
        if re.match(r'^\s*Autos y Vistos\s*[;:]', linea):
            flags["fallo_idx_elegido"] = i
            flags["estrategia_usada"] = "fallback_autos_y_vistos"
            return bloque[:i], bloque[i:], flags

    # No hay nada → caso patológico, devolver bloque vacío
    flags["estrategia_usada"] = "fallback_sin_apertura"
    return bloque, [], flags
```

### Casos de borde cubiertos

| Caso | Comportamiento |
|---|---|
| 1 FALLO único | Regla trivial. División clean. |
| 2+ FALLOs (Tipo 1: caso anterior + caso actual) | Regla C: primer FALLO seguido de "Buenos Aires," real |
| FALLO espurio en nota al pie (329_p4804) | Regla A descarta y queda el real |
| 0 FALLOs detectados | Fallback a "Autos y Vistos;" o "Autos y Vistos:" |
| Bloque sin nada parseable | Devuelve bloque entero como pre_fallo, fallo vacío + flag |

---

## Función 2 — `detectar_caratula`

### Tres estrategias jerarquizadas

```python
def detectar_caratula(pre_fallo, fallo, nombres_indice, flags_division):
    """
    Aplica tres estrategias en orden:
    1. Matching contra nombres_indice (catálogo del tomo)
    2. Detección estructural en pre_fallo (MAYÚSCULAS:)
    3. V1 — extracción desde "Vistos los autos:" en fallo

    Cada estrategia devuelve un candidato. Si dos o más coinciden,
    confianza alta. Si solo una devuelve, se usa esa.
    """
    candidatos = {}

    # Estrategia 1: matching contra nombres_indice
    cand_1 = _matching_contra_indice(pre_fallo, nombres_indice)
    if cand_1:
        candidatos["matching_indice"] = cand_1

    # Estrategia 2: detección estructural en pre_fallo
    cand_2 = _detectar_caratula_estructural(pre_fallo)
    if cand_2:
        candidatos["estructural"] = cand_2

    # Estrategia 3: V1 desde Vistos los autos
    cand_3 = extraer_caratula_de_vistos(fallo)  # Función 4
    if cand_3:
        candidatos["vistos_los_autos"] = cand_3

    # Decisión
    return _decidir_caratula(candidatos, flags_division)


def _matching_contra_indice(pre_fallo, nombres_indice):
    """
    Busca en pre_fallo una línea (o concatenación de líneas) que matchee
    alguna entrada de nombres_indice. Tolerancia de fuzzy match (~85%).
    """
    pre_fallo_texto = " ".join(pre_fallo)
    mejor_match = None
    mejor_score = 0
    for nombre in nombres_indice:
        score = ratio_similitud(nombre, pre_fallo_texto)
        if score > mejor_score and score >= 0.85:
            mejor_score = score
            mejor_match = nombre
    return mejor_match


def _detectar_caratula_estructural(pre_fallo):
    """
    Busca línea con patrón A (MAYÚSCULAS: resto) o patrón B
    (MAYÚSCULAS solo, frase corta).
    Aplica lista negra de XIV: encabezados, meses, atribuciones.
    """
    LISTA_NEGRA = {
        "FALLOS DE LA CORTE SUPREMA",
        "DE JUSTICIA DE LA NACION",
        "DE JUSTICIA DE LA NACIÓN",
        "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE",
        "NOVIEMBRE", "DICIEMBRE", "ENERO",
        # Atribuciones
        "FALLO DE LA CORTE SUPREMA",
        "DICTAMEN DE LA PROCURACION GENERAL",
        # ... lista completa
    }

    for linea in reversed(pre_fallo):  # buscar de abajo hacia arriba
        # Patrón A: MAYÚSCULAS:
        m = re.match(r'^([A-ZÁÉÍÓÚÑ\s,\.]+)\s+c/\s+(.+?)\s+s/\s+(.+)$', linea)
        if m and linea.strip() not in LISTA_NEGRA:
            return linea.strip()
        # Patrón B: MAYÚSCULAS solo, frase corta
        if (linea.isupper() and 10 < len(linea) < 200
                and linea.strip() not in LISTA_NEGRA):
            return linea.strip()
    return None


def _decidir_caratula(candidatos, flags_division):
    """
    Lógica de decisión:
    - Si las 3 coinciden → matching_indice (preferida) + flag triple_match
    - Si 2 coinciden → la coincidente, prefiriendo en orden:
      matching_indice > estructural > vistos_los_autos
    - Si solo 1 → esa, con flag confianza_baja
    - Si 0 → None, flag caso_patologico
    """
    if not candidatos:
        return None, {"confianza": "patologico"}

    if len(candidatos) == 3:
        # Verificar coincidencia de las 3
        valores = list(candidatos.values())
        if all(_son_equivalentes(v, valores[0]) for v in valores):
            return candidatos["matching_indice"], {"confianza": "alta_triple"}
        # Sino: hay desacuerdo, elegir la mejor disponible y flagear
        return candidatos["matching_indice"], {
            "confianza": "media_desacuerdo",
            "discrepancias": candidatos
        }

    if len(candidatos) == 2:
        # Devolver según prioridad
        for clave in ("matching_indice", "estructural", "vistos_los_autos"):
            if clave in candidatos:
                return candidatos[clave], {"confianza": "media_dos_estrategias"}

    if len(candidatos) == 1:
        clave = list(candidatos.keys())[0]
        return candidatos[clave], {"confianza": "baja_una_estrategia"}

    return None, {"confianza": "patologico"}
```

---

## Función 3 — `detectar_dispositivo`

```python
def detectar_dispositivo(fallo):
    """
    Encuentra la línea del dispositivo del fallo.
    Estrategia: última 'Por ello' del sub-bloque fallo, escaneando
    de abajo hacia arriba.

    Resuelve bug XII: como trabajamos sobre el sub-bloque fallo
    (no sobre el bloque completo), el 'Por ello' del dictamen
    en pre_fallo no es accesible — ya queda excluido por construcción.

    Pero dentro del fallo puede haber MÚLTIPLES 'Por ello' válidos:
    - El de la mayoría
    - Los de votos concurrentes
    - Los de disidencias
    
    El que nos interesa para anclar es el PRIMERO de arriba hacia abajo
    (el de la mayoría o voto principal), que coincide con
    el final del considerando del voto que produce el dispositivo.
    
    Cuando hay disidencias, los Por ello posteriores anclan los votos
    disidentes — esos NO son "el dispositivo del fallo" sino sub-dispositivos
    de cada voto.

    Para la firma final del fallo (la que cierra el documento),
    sí queremos la ÚLTIMA línea de firma del último voto.
    """
    indices_por_ello = []
    for i, linea in enumerate(fallo):
        if re.match(r'^\s*Por\s+ello[,\s]', linea):
            indices_por_ello.append(i)

    if not indices_por_ello:
        return None, {"strategy": "ninguno"}

    return {
        "primer_por_ello": indices_por_ello[0],     # mayoría
        "todos_por_ello": indices_por_ello,         # mayoría + votos
        "ultimo_por_ello": indices_por_ello[-1],    # último voto
    }, {"strategy": "por_ello_multiple" if len(indices_por_ello) > 1
                    else "por_ello_simple"}
```

### Notas sobre el bug XII

El bug XII original era: el dictamen termina con "Por ello, opino..." y el parser ancla ahí. Como ahora `detectar_dispositivo` solo opera sobre el sub-bloque `fallo` (que empieza después de `FALLO DE LA CORTE SUPREMA`), el "Por ello" del dictamen queda en `pre_fallo` y no es accesible. **El bug XII queda resuelto por construcción**, sin necesidad de reglas adicionales.

### Notas sobre votos múltiples

Casos como Colegio de Escribanos tienen `Por ello` en mayoría + voto Maqueda + disidencia Lorenzetti + disidencia Rosenkrantz. La función devuelve los índices de todos. El loop de `collect_firma_lines` los usa para detectar voces individuales (cada `Por ello` cierra un voto independiente y la firma siguiente identifica al juez de ese voto).

---

## Función 4 — `extraer_caratula_de_vistos`

```python
def extraer_caratula_de_vistos(fallo, max_lineas=8):
    """
    Busca 'Vistos los autos:' seguido de comilla de apertura,
    reconstruye la carátula concatenando líneas hasta encontrar
    la comilla de cierre.

    Maneja:
    - Comillas tipográficas (U+201C / U+201D) y rectas
    - Wrap por silabación (guion suave U+00AD o guion normal)
    - Multi-línea hasta max_lineas

    Devuelve la carátula limpia o None si no encuentra.
    """
    PAT_INICIO = re.compile(
        r'^\s*Vistos los autos:\s*([\u201C\u201D"\u2018\u2019\'])',
        re.IGNORECASE
    )
    COMILLAS = '\u201C\u201D"\u2018\u2019\''

    for i, linea in enumerate(fallo):
        m = PAT_INICIO.match(linea)
        if not m:
            continue

        # Empezar a acumular desde la comilla de apertura
        comilla_apert = m.group(1)
        pos_apertura = linea.index(comilla_apert)
        acumulado = linea[pos_apertura + 1:].rstrip()

        # ¿Cierra en la misma línea?
        m_cierre = re.search(f'[{COMILLAS}]', acumulado)
        if m_cierre:
            return acumulado[:m_cierre.start()]

        # Sino, juntar líneas siguientes
        for j in range(i + 1, min(i + max_lineas, len(fallo))):
            sig = fallo[j].rstrip()
            # Manejar wrap por silabación
            if acumulado.endswith('\u00AD') or acumulado.endswith('-'):
                acumulado = acumulado.rstrip('\u00AD-') + sig.lstrip()
            else:
                acumulado = acumulado + ' ' + sig.lstrip()
            m_cierre = re.search(f'[{COMILLAS}]', sig)
            if m_cierre:
                # Cortar en la comilla de cierre
                idx_cierre = acumulado.rindex(sig.lstrip()) + m_cierre.start() - len(sig.lstrip()) + len(sig.lstrip())
                # Más simple: cortar acumulado en la última comilla
                pos_cierre_acum = max(
                    acumulado.rfind(c) for c in COMILLAS
                )
                return acumulado[:pos_cierre_acum]

        # No encontró cierre en max_lineas → carátula sin cierre
        return acumulado

    return None
```

---

## Simulación sobre 7 casos representativos

Para cada caso simulo el flujo: división → carátula → dispositivo → resultado esperado.

### Caso 1 — Brizuela (338_p1431) — Tipo 1 + bug XII enmascarado

Bloque crudo:
```
[línea N]   AUTO DE CONCESION                     ← caso anterior
[línea N+1] Suprema Corte:                         ← cierre dictamen anterior
[línea N+2] BRIZUELA, SANDRA ANALIA c/ TELEFONICA  ← carátula real
[línea N+3] ... (sumario doctrinal)
[línea N+x] Dictamen de la Procuración General
[línea N+y] -I-, -II-, -III- ... contenido dictamen
[línea N+z] Por ello, entiendo que ...              ← Por ello del dictamen
[línea N+z+1] FALLO DE LA CORTE SUPREMA            ← FALLO real
[línea N+z+2] Buenos Aires, 1° de diciembre de 2015.
[línea N+z+3] Vistos los autos: "Brizuela, Sandra...
[línea N+z+4]                                       Análía c/ Telefónica..."
[línea N+z+5] Considerando: ...
[línea N+z+6] Por ello y oída la señora Procuradora ← Por ello real
[línea N+z+7] Ricardo Luis Lorenzetti — ...        ← firma
[línea N+z+8] Tribunal de origen: ...
```

Flujo:
1. `dividir_bloque_en_sub_bloques`:
   - 1 FALLO detectado → estrategia `fallo_unico`
   - `pre_fallo` = todo hasta antes del FALLO real (incluye AUTO DE CONCESION + carátula Brizuela + dictamen completo)
   - `fallo` = desde FALLO hasta el final
   - `pagina_compartida = True` (porque `pre_fallo` contiene "Tribunal de origen:" del caso anterior — espera, NO, el AUTO DE CONCESION puede no tener Tribunal de origen. Verificar)

2. `detectar_caratula`:
   - Estrategia 1 (matching contra `nombres_indice`): Brizuela aparece en el catálogo → ✓
   - Estrategia 2 (estructural): la carátula MAYÚSCULAS Brizuela está en `pre_fallo` → ✓
   - Estrategia 3 (V1): `Vistos los autos: "Brizuela..."` en `fallo` → ✓
   - Triple coincidencia → confianza alta.

3. `detectar_dispositivo`:
   - 1 `Por ello` en `fallo` (el del dictamen quedó en `pre_fallo`) → `por_ello_idx` apunta al real.
   - Bug XII resuelto por construcción.

4. Firma: `collect_firma_lines` desde `por_ello_idx` en `fallo` → captura Lorenzetti, Highton, Maqueda → unanimidad.

**Resultado esperado**: caso pasa de `voting_pattern=sin_firma` a `voting_pattern=unanime`. ✓

### Caso 2 — Colegio de Escribanos (342_p1017) — Tipo 1 + bug XII enmascarado + cuatro voces

Estructura del bloque:
- pre_fallo: caso anterior (Estado Nacional/Min. Economía) con su firma + carátula Colegio + sumarios masivos + dictamen Gils Carbó.
- fallo: FALLO + Vistos los autos + considerandos mayoría + Por ello + firma con (en disidencia)... + voto Maqueda con su Por ello y firma + disidencia Lorenzetti con su Por ello y firma + disidencia Rosenkrantz con su Por ello y firma.

Flujo:
1. División: 1 FALLO real (los votos disidentes no tienen `FALLO DE LA CORTE SUPREMA`, solo "Voto del Señor..." o "Disidencia del Señor...").
2. Carátula: triple match → "Colegio de Escribanos de la Provincia de Bs. As. c/ PEN s/ sumarísimo".
3. Dispositivo: 4 `Por ello` detectados en `fallo` (mayoría + Maqueda + Lorenzetti + Rosenkrantz). El primero ancla el cuerpo de la mayoría.
4. Detector de voces (función separada, ya validado en XIV): captura las 4 voces. `voting_pattern` calculado: mayoría + voto + dos disidencias = `mayoria_concurrencia_disidencia`.

**Resultado esperado**: caso pasa de `sin_firma` a `mayoria_concurrencia_disidencia`. ✓

### Caso 3 — 344_p1 Araujo — preámbulo de tomo

Bloque crudo:
```
[línea 21] En el sitio de Internet www.csjn.gov.ar, se puede consultar...
[línea 35] R E P U B L I C A   A R G E N T I N A
[línea 36] FALLOS
[línea 43] TOMO 344
[línea 44] ENERO-MAYO
[línea 45] 2021
[línea 48] RECURSO EXTRAORDINARIO   (sumarios sueltos)
[línea 50] >> 1                      (header de página)
[línea 53] FALLOS DE LA CORTE SUPREMA
[línea 54] FEBRERO
[línea 55] ARAUJO, RAMONA c/ EN ...
[...]
[línea 76] FALLOS DE LA CORTE SUPREMA
[línea 77] FALLO DE LA CORTE SUPREMA
[línea 78] Buenos Aires, 4 de febrero de 2021.
```

Flujo:
1. División: 1 FALLO en línea 77. `pre_fallo` incluye el preámbulo del tomo + sumarios + carátula Araujo + cabezal de página.
2. Carátula:
   - Matching contra índice: Araujo aparece → ✓
   - Estructural: la carátula `ARAUJO, RAMONA c/ EN - M JUSTICIA y DDHH s/ Indemnizaciones – Ley 24043 - art 3` está en pre_fallo en MAYÚSCULAS → ✓
   - V1: el `Vistos los autos:` viene después del FALLO, en `fallo` → ✓
   - Triple coincidencia → confianza alta.
3. Dispositivo y firma: trabajan sobre `fallo`, sin contaminación del preámbulo.

**Resultado esperado**: caso pasa de `intermedio_a_revisar` a clasificado correctamente. ✓

### Caso 4 — 329_p4804 American Jet — nota al pie con FALLO espurio

Bloque crudo (resumido):
```
[línea X]   ... considerando 21 ... (causa "Serenar S.A.", sentencia del 19 de agosto de 2004) (*)
[línea X+1] Dicha sentencia dice así:
[línea X+2] SERENAR S.A. V. PROVINCIA DE BUENOS AIRES
[línea X+3] FALLO DE LA CORTE SUPREMA          ← FALLO espurio (nota al pie)
[línea X+4] Buenos Aires, 19 de agosto de 2004.
[línea X+5] Autos y Vistos; Considerando:
[...]       (todo el fallo Serenar)
[línea X+30] ENRIQUE SANTIAGO PETRACCHI ...
[línea X+31] Nombre de los actores: Serenar S.A....
[línea X+32] (vuelve al cuerpo American Jet)
[línea Y]   ENRIQUE SANTIAGO PETRACCHI (en disidencia PARCIAL) — ELENA I. HIGHTON
            ... (firma real American Jet)
```

Flujo:
1. División: detecta 2 FALLOs.
   - Aplicar Regla A: el FALLO espurio (línea X+3) está precedido por "Dicha sentencia dice así:" en línea X+1. **Lo descarta**.
   - Queda 1 candidato si hay otro FALLO real más arriba o más abajo. Pero en este caso American Jet **no tiene** un FALLO DE LA CORTE SUPREMA propio en el .md (porque su carátula y considerandos están directamente, sin marcador FALLO).
   - Reformulación: si después de descartar espurios queda 0 candidatos, fallback a buscar "Autos y Vistos;" o tomar la última firma como ancla.
   - Esto requiere un sub-flujo extra.

**Diagnóstico crítico**: el caso 329_p4804 NO tiene un `FALLO DE LA CORTE SUPREMA` propio del fallo American Jet. El único FALLO en el bloque es el de la nota al pie (Serenar). Esto rompe la asunción "todo bloque tiene exactamente un FALLO real".

**Decisión de diseño**: el caso 329_p4804 queda como **caso patológico no recuperable por el refactor**. Es coherente con la reclasificación a Tipo 2 que hicimos en la sesión XV. Fallback: capturar carátula desde `nombres_indice` y aceptar que `voting_pattern` quede sin firma o con la firma de Serenar (incorrecto pero detectable por el flag `tiene_nota_al_pie`).

### Caso 5 — 341_p1397 Arjona — atípico

Bloque (resumido):
```
[línea Z-50] (cuerpo del caso anterior TBA)
[línea Z]   1397                                ← header de página
[línea Z+1] DE JUSTICIA DE LA NACIÓN
[línea Z+2] 341
[línea Z+3] (sigue cuerpo TBA)
[línea Z+8] Por ello, el Tribunal resuelve... ← dispositivo TBA
[línea Z+15] Carlos Fernando Rosenkrantz —... ← firma TBA
[línea Z+20] Tribunal de origen: ...           ← cierre TBA
[línea Z+21] ARJONA, ROBERTO y Otros c/...     ← carátula Arjona
[línea Z+30] FALLO DE LA CORTE SUPREMA         ← FALLO Arjona
```

El problema: `pagina_inicio = Z` (donde aparece el header `1397`), pero el bloque del caso Arjona en el `.md` empieza realmente en línea Z. El parser actual asume que la carátula está cerca de `pagina_inicio` y retrocede, pero en este caso la carátula está adelante (línea Z+21).

Flujo del refactor:
1. División: detecta 1 FALLO real (línea Z+30).
   - `pre_fallo` = líneas [pagina_inicio, Z+30) = incluye cuerpo TBA + cierre TBA + carátula Arjona.
   - `fallo` = desde Z+30.
   - Flag `pagina_compartida = True` (porque hay "Tribunal de origen:" en pre_fallo).

2. Carátula:
   - Matching contra índice: Arjona aparece en `nombres_indice` → ✓
   - Estructural: busca de abajo hacia arriba en `pre_fallo`. La carátula Arjona (MAYÚSCULAS) está más abajo que la firma del caso anterior, en línea Z+21. Match → ✓
   - V1: `Vistos los autos: "Arjona..."` en `fallo` → ✓
   - Triple coincidencia.

3. Dispositivo y firma: en `fallo`, sin contaminación.

**Resultado esperado**: caso recuperado correctamente. ✓

### Caso 6 — Tipo 1 puro (Mellicovsky 331_p2283)

Caso pequeño con caso anterior corto:
```
[línea N-15]   ... cuerpo caso anterior (Ruiz)
[línea N-5]    Ricardo Luis Lorenzetti — Elena I. Highton...   ← firma caso anterior
[línea N-3]    Tribunal de origen: ...                          ← cierre caso anterior
[línea N]      MELLICOVSKY, LIDIA BEATRIZ c/ ESTADO NACIONAL    ← carátula real
[línea N+5]    FALLO DE LA CORTE SUPREMA
[línea N+6]    Buenos Aires, 21 de octubre de 2008.
[...]
[línea N+30]   Por ello, se desestima ...
[línea N+33]   Ricardo Luis Lorenzetti — ... — Carmen M. Argibay.
```

Flujo: división estándar, triple match en carátula, dispositivo y firma claros. Sin sorpresas. ✓

### Caso 7 — Caso sin V1 (uno de los 1.872 con V4/V5 únicamente)

Estructura:
```
[FALLO DE LA CORTE SUPREMA]
Buenos Aires, [fecha].
Autos y Vistos; Considerando:
1°) Que ...
2°) Que ...
Por ello, ...
[firma]
Tribunal de origen: ...
```

Flujo:
1. División: 1 FALLO único → `fallo` empieza en FALLO.
2. Carátula:
   - Matching: ✓ (asumiendo que el caso está en el catálogo)
   - Estructural: ✓ (la carátula está en pre_fallo)
   - V1: ✗ (no hay `Vistos los autos:`)
   - Doble coincidencia (matching + estructural) → confianza media.
3. Dispositivo: el `Por ello` está en `fallo`, captura limpia.

**Resultado esperado**: caso bien resuelto sin necesitar V1. La estrategia 3 sirve solo cuando 1 y 2 fallan, no es obligatoria. ✓

---

## Problemas no resueltos por el diseño

Después de la simulación quedan dos problemas identificados:

### Problema 1 — Caso 329_p4804 sin FALLO real propio

La asunción "todo bloque tiene exactamente un FALLO DE LA CORTE SUPREMA real" no se cumple en este caso. El refactor lo flageará como `tiene_nota_al_pie=True` y el fallback a `nombres_indice` aplicará para la carátula, pero el dispositivo y la firma no se podrán capturar correctamente.

**Mitigación**: aceptar que estos casos quedan como Tipo 2 (artefacto del conversor). La cantidad esperada es muy baja (1 caso confirmado en los 16 intermedios; auditoría a corpus completo daría una cota superior).

### Problema 2 — Equivalencia entre carátulas (`_son_equivalentes`)

La lógica de "triple coincidencia" requiere comparar tres strings que vienen de fuentes distintas (catálogo, MAYÚSCULAS estructural, V1 entrecomillado). Pueden diferir en:
- Mayúsculas/minúsculas
- Acentos
- Abreviaciones (`Bs. As.` vs `Buenos Aires`)
- Separadores (`c/` vs `contra` vs `vs`)
- Signos de puntuación

Necesitamos una función `_son_equivalentes(a, b)` que tolere estas variaciones. Propongo:

```python
def _son_equivalentes(a, b):
    return ratio_similitud(_normalizar(a), _normalizar(b)) >= 0.80

def _normalizar(s):
    s = s.lower()
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()  # sin acentos
    s = re.sub(r'\b(bs\.?\s*as\.?|prov\.?\s*de\s*bs\.?\s*as\.?)\b',
               'buenos aires', s)
    s = re.sub(r'\bc/\b', 'contra', s)
    s = re.sub(r'[^\w\s]', '', s)  # sin puntuación
    s = re.sub(r'\s+', ' ', s).strip()
    return s
```

---

## Próximos pasos antes de Bloque D

1. **Validar este diseño con vos**: si hay objeciones o sub-casos no cubiertos, ajustar antes de codificar.
2. **Listar las funciones del `parser.py` actual que se eliminan o se modifican**:
   - Eliminar: `RE_DISPOSITIVO_VARIANTES`, `detectar_apertura_dispositivo`, state machine `en_dictamen`.
   - Modificar: `find_case_name`, `collect_firma_lines`, loop principal.
   - Agregar: `dividir_bloque_en_sub_bloques`, `detectar_caratula`, `detectar_dispositivo`, `extraer_caratula_de_vistos`, helpers (`_son_equivalentes`, `_normalizar`, `_elegir_fallo_real`, `_fallback_sin_fallo`).
3. **Snapshot del `csjn_casos.csv` actual** antes de tocar `parser.py`.
4. **Acordar criterio de validación post-refactor** (Bloque E):
   - ¿Cuántos casos pasan de NaN a valor en `case_name_cuerpo`? Esperado: ~3.000.
   - ¿Cuántos casos pasan de `sin_firma` a clasificación válida? Esperado: ~234 + ~50 (los Tipo 1 con bug XII enmascarado).
   - ¿Cuántos casos del `voting_pattern` cambian respecto al snapshot? Auditoría manual sobre subsamples.
   - Detectar regresiones: casos que estaban bien y empeoran.

## Resumen ejecutivo

El diseño cubre las 4 categorías principales (Tipo 1 estricto + Tipo 1 ampliado + casos sanos + casos con V1) sin reglas ad hoc. La triple estrategia para carátula da redundancia natural. La división en sub-bloques resuelve el bug XII por construcción. Los casos atípicos (nota al pie 329_p4804, bug catalográfico 344_p344) quedan flageados pero no recuperados — son problemas aguas arriba.

El refactor está listo para codificarse en Bloque D una vez validado el diseño contigo.
