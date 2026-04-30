#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cruce_anuarios.py

Cruza el corpus CSJN (csjn_casos_v16.csv) con datos extraidos manualmente de los
Anuarios Estadisticos 2024 y 2025 publicados por la Oficina de Estadisticas de
la CSJN.

Permite caracterizar la diferencia entre dos universos:
  - UNIVERSO ANUARIO: todos los casos resueltos (incluye 82-85% rechazados por
    art. 280 y otras formulas, masivamente previsional)
  - UNIVERSO FALLOS (corpus): solo lo publicado en la Coleccion de Fallos
    (donde se concentra la actividad jurisprudencial sustantiva)

La Secretaria de Jurisprudencia opera el filtro entre ambos universos.

Uso (PowerShell):
    cd "C:\\Users\\guill\\My Drive\\Posgrados\\Maestria UBA\\Tesis UBA\\AC\\paginas"
    python cruce_anuarios.py

Asume:
  - csjn_casos_v16.csv en el directorio actual
  - Output: analisis/11_cruce_anuario.csv y analisis/cruce_anuarios_log.txt
"""

import sys
from pathlib import Path
import pandas as pd


# ---------------------------------------------------------------------------
# Datos extraidos manualmente de los Anuarios Estadisticos
# Fuente: Oficina de Estadisticas CSJN, informes 2024 y 2025
# ---------------------------------------------------------------------------

ANUARIO = {
    2024: {
        # Volumetria
        'casos_ingresados': 45678,
        'casos_resueltos': 19056,
        'casos_pendientes': 26622,
        'fallos_dictados': 12521,
        'acuerdos': 47,
        'casos_tratados': 5370,    # 2999 recursos + 2371 ddas/comp/otros
        'casos_inadmisibles_formula': 13686,  # 82% rechazados sin tratamiento
        # Composicion por via de acceso (resueltos)
        'recursos_resueltos': 16685,
        'ddas_comp_otros_resueltos': 2371,
        # Composicion por materia (sobre recursos resueltos, %)
        'pct_previsional': 40.4,
        'pct_penal': 18.9,
        'pct_laboral': 15.8,
        'pct_trib_aduan_banc': 8.6,
        'pct_contencioso_adm': 8.4,
        'pct_civil_comercial': 5.9,
        'pct_consumo': 1.3,
        'pct_salud': 0.4,
        'pct_ddhh_inst': 0.2,
        'pct_ambiental': 0.1,
        # Tipos de voto (sobre votos emitidos, %)
        'pct_unanimidad': 42.35,
        'pct_voto_conjunto': 27.17,
        'pct_voto_propio': 23.13,
        'pct_disidencia_propia': 7.07,
        'pct_disidencia_parcial': 0.18,
        'pct_disidencia_conjunta': 0.10,
        'pct_disidencia_parcial_conjunta': 0.01,
        # Conjueces
        'casos_con_conjueces': 29,
        'pct_casos_con_conjueces': 0.15,
        # Remisiones (sobre casos tratados)
        'pct_con_remision': 88.0,
        'pct_sin_remision': 12.0,
        'pct_remision_precedentes': 69.4,
        'pct_remision_total_pgn': 29.0,
        'pct_remision_parcial_pgn': 1.6,
        # Duracion
        'duracion_promedio_dias': 599,
        'duracion_mediana_dias': 385,
        'duracion_admitidos_promedio': 730,
        'duracion_admitidos_mediana': 511,
        'duracion_inadmisibles_promedio': 548,
        'duracion_inadmisibles_mediana': 324,
        # Cuestion federal en admitidos
        'pct_sentencia_arbitraria': 65.1,
        'pct_art_14_ley_48': 34.8,
        'pct_gravedad_institucional': 0.08,
        # Top oficinas en arbitrariedad
        'top_arbitrariedad_cnat': 28.39,           # Camara Nacional Apel del Trabajo
        'top_arbitrariedad_cfss': 15.01,           # Camara Federal Seguridad Social
        'top_arbitrariedad_civil': 8.14,           # Camara Civil
        'top_arbitrariedad_casacion_penal': 5.42,
        'top_arbitrariedad_cadm_federal': 4.88,
        # Inconstitucionalidades
        'inconstitucionalidades_declaradas': 68,
        'pct_inconst_originarios': 72.0,
        'pct_inconst_previsionales': 13.25,
    },
    2025: {
        # Volumetria
        'casos_ingresados': 58424,
        'casos_resueltos': 26524,
        'casos_pendientes': 31900,
        'fallos_dictados': 15652,
        'acuerdos': 46,
        'casos_tratados': 5701,    # 3722 recursos + 1979 ddas/comp/otros
        'casos_inadmisibles_formula': 20823,  # 84.84%
        # Composicion por via de acceso
        'recursos_resueltos': 24545,
        'ddas_comp_otros_resueltos': 1979,
        # Composicion por materia (sobre recursos resueltos, %)
        'pct_previsional': 58.28,
        'pct_penal': 13.62,
        'pct_laboral': 12.04,
        'pct_trib_aduan_banc': 3.59,
        'pct_contencioso_adm': 5.05,
        'pct_civil_comercial': 4.88,
        'pct_consumo': 2.09,
        'pct_salud': 0.14,
        'pct_ddhh_inst': 0.02,
        'pct_ambiental': 0.27,
        # Tipos de voto (sobre votos emitidos, %)
        'pct_unanimidad': 48.97,
        'pct_voto_conjunto': 33.97,
        'pct_voto_propio': 16.92,
        'pct_disidencia_propia': 0.11,
        'pct_disidencia_parcial': 0.0,
        'pct_disidencia_conjunta': 0.03,
        'pct_disidencia_parcial_conjunta': 0.001,
        # Conjueces
        'casos_con_conjueces': 131,
        'pct_casos_con_conjueces': 0.49,
        # Remisiones
        'pct_con_remision': 93.21,
        'pct_sin_remision': 6.79,
        'pct_remision_precedentes': 72.6,
        'pct_remision_total_pgn': 25.65,
        'pct_remision_parcial_pgn': 1.75,
        # Duracion
        'duracion_promedio_dias': 609,
        'duracion_mediana_dias': 364,
        'duracion_admitidos_promedio': 844,
        'duracion_admitidos_mediana': 571,
        'duracion_inadmisibles_promedio': 545,
        'duracion_inadmisibles_mediana': 295,
        # Cuestion federal
        'pct_sentencia_arbitraria': 32.71,
        'pct_art_14_ley_48': 67.29,
        'pct_gravedad_institucional': 0.0,
        # Top oficinas en arbitrariedad
        'top_arbitrariedad_cnat': 74.92,
        'top_arbitrariedad_civil': 9.42,
        'top_arbitrariedad_cfss': 3.90,
        'top_arbitrariedad_cadm_federal': 2.19,
        'top_arbitrariedad_casacion_penal': 1.95,
        # Inconstitucionalidades
        'inconstitucionalidades_declaradas': 24,
        'pct_inconst_originarios': 79.17,  # 19/24
        'pct_inconst_previsionales': None,  # no desagregado igual
    },
}

ANIOS_TOMO = {
    329: 2006, 330: 2007, 331: 2008, 332: 2009, 333: 2010, 334: 2011,
    337: 2014, 338: 2015, 339: 2016, 340: 2017, 341: 2018, 342: 2019,
    343: 2020, 344: 2021, 345: 2022, 346: 2023, 347: 2024, 348: 2025,
    349: 2026,
}


# ---------------------------------------------------------------------------
# Heuristica de materia (replicada del analisis previo)
# ---------------------------------------------------------------------------

def inferir_materia(t):
    if pd.isna(t) or t in ('SIN_TRIBUNAL_ORIGEN', ''):
        return 'no_inferible'
    t = str(t).lower()
    if 'originaria' in t: return 'originaria'
    if 'casación penal' in t or 'casacion penal' in t or 'criminal' in t or 'oral en lo penal' in t: return 'penal'
    if 'del trabajo' in t or 'laboral' in t: return 'laboral'
    if 'seguridad social' in t: return 'seguridad_social'  # = "previsional" en lenguaje del anuario
    if 'contencioso' in t: return 'contencioso_administrativo'
    if 'civil y comercial' in t: return 'civil_comercial'
    if 'suprema corte' in t or 'superior tribunal' in t or 'supremo tribunal' in t: return 'tribunal_provincial'
    if 'cámara federal' in t or 'camara federal' in t: return 'federal_otro'
    if 'cámara nacional' in t or 'camara nacional' in t: return 'nacional_otro'
    return 'otro'


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class Log:
    def __init__(self, path):
        self.lines = []
        self.path = path
    def __call__(self, s=""):
        print(s)
        self.lines.append(str(s))
    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.lines))


# ---------------------------------------------------------------------------
# Carga del corpus
# ---------------------------------------------------------------------------

def cargar_corpus(ruta_casos, log):
    casos = pd.read_csv(ruta_casos)
    casos['anio'] = casos['date'].str.extract(r'(\d{4})$').astype('Int64')
    casos['anio_esperado'] = casos['tomo'].map(ANIOS_TOMO).astype('Int64')
    casos['delta_anios'] = casos['anio'] - casos['anio_esperado']
    casos['tam_bloque'] = casos['linea_fin_real'] - casos['linea_inicio']
    casos['en_subset_limpio'] = ~(
        (casos['tam_bloque'] > 10000) |
        (casos['anio'].notna() & ((casos['delta_anios'] < -2) | (casos['delta_anios'] > 1))) |
        (casos['status_localizacion'].isin({'pagina_fin_no_en_mapa', 'fallo_cruza_archivos', 'ultimo_del_tomo'}))
    )
    casos['materia'] = casos['tribunal_origen'].apply(inferir_materia)
    sub = casos[casos['en_subset_limpio']].copy()
    log(f"Corpus cargado: {len(casos)} totales, {len(sub)} en subset limpio")
    return sub


# ---------------------------------------------------------------------------
# Calculo de metricas del corpus por anio
# ---------------------------------------------------------------------------

def metricas_corpus(sub, anio):
    s = sub[sub['anio'] == anio]
    if len(s) == 0:
        return None

    # Composicion por materia (% sobre el total del anio)
    materia_pct = (s['materia'].value_counts(normalize=True) * 100).round(2)

    # Voting patterns
    n = len(s)
    pct_unanime = round((s['voting_pattern'] == 'unanime').mean() * 100, 2)
    pct_disidencia = round((s['voting_pattern'] == 'disidencia').mean() * 100, 2)
    pct_segun_voto = round((s['voting_pattern'] == 'segun_su_voto').mean() * 100, 2)
    pct_mixed = round((s['voting_pattern'] == 'mixed').mean() * 100, 2)
    pct_concurrencia = pct_segun_voto + pct_mixed
    pct_sin_firma = round((s['voting_pattern'] == 'sin_firma').mean() * 100, 2)

    # Originaria vs apelada
    pct_originaria = round(s['is_originaria'].mean() * 100, 2)

    # Word count
    wc_mediana = int(s['word_count'].median())
    wc_promedio = int(s['word_count'].mean())

    return {
        'n_corpus': n,
        # Composicion materia
        'mat_seguridad_social_pct': materia_pct.get('seguridad_social', 0),  # ~ "previsional" anuario
        'mat_penal_pct': materia_pct.get('penal', 0),
        'mat_laboral_pct': materia_pct.get('laboral', 0),
        'mat_contencioso_adm_pct': materia_pct.get('contencioso_administrativo', 0),
        'mat_civil_comercial_pct': materia_pct.get('civil_comercial', 0),
        'mat_tribunal_provincial_pct': materia_pct.get('tribunal_provincial', 0),
        'mat_federal_otro_pct': materia_pct.get('federal_otro', 0),
        'mat_nacional_otro_pct': materia_pct.get('nacional_otro', 0),
        'mat_originaria_pct': materia_pct.get('originaria', 0),
        'mat_no_inferible_pct': materia_pct.get('no_inferible', 0),
        # Voting patterns
        'pct_unanime': pct_unanime,
        'pct_disidencia': pct_disidencia,
        'pct_segun_su_voto': pct_segun_voto,
        'pct_mixed': pct_mixed,
        'pct_concurrencia_total': round(pct_concurrencia, 2),
        'pct_sin_firma': pct_sin_firma,
        # Otras
        'pct_originaria_corpus': pct_originaria,
        'wc_mediana': wc_mediana,
        'wc_promedio': wc_promedio,
    }


# ---------------------------------------------------------------------------
# Construccion de la tabla comparativa
# ---------------------------------------------------------------------------

def construir_tabla_comparativa(corpus_2024, corpus_2025, log):
    """Construye una tabla larga con metrica, anio, fuente, valor, comentario."""
    rows = []

    # ---- VOLUMETRIA ----
    for anio in [2024, 2025]:
        a = ANUARIO[anio]
        c = corpus_2024 if anio == 2024 else corpus_2025
        rows.append({
            'categoria': 'volumetria', 'metrica': 'total_casos', 'anio': anio,
            'anuario': a['casos_resueltos'],
            'corpus': c['n_corpus'],
            'cobertura_pct': round(100 * c['n_corpus'] / a['casos_resueltos'], 2),
            'comentario': 'casos resueltos del anuario vs publicados en Fallos'
        })
        rows.append({
            'categoria': 'volumetria', 'metrica': 'casos_tratados_anuario_vs_corpus', 'anio': anio,
            'anuario': a['casos_tratados'],
            'corpus': c['n_corpus'],
            'cobertura_pct': round(100 * c['n_corpus'] / a['casos_tratados'], 2),
            'comentario': 'casos tratados (excluye art. 280 y formulas) vs publicados'
        })
        rows.append({
            'categoria': 'volumetria', 'metrica': 'casos_inadmisibles_formula', 'anio': anio,
            'anuario': a['casos_inadmisibles_formula'],
            'corpus': None,
            'cobertura_pct': None,
            'comentario': 'rechazados por art. 280 u otras formulas (no tratados)'
        })

    # ---- COMPOSICION POR MATERIA ----
    materias = [
        ('previsional', 'pct_previsional', 'mat_seguridad_social_pct'),
        ('penal', 'pct_penal', 'mat_penal_pct'),
        ('laboral', 'pct_laboral', 'mat_laboral_pct'),
        ('contencioso_adm', 'pct_contencioso_adm', 'mat_contencioso_adm_pct'),
        ('civil_comercial', 'pct_civil_comercial', 'mat_civil_comercial_pct'),
        ('trib_aduan_banc', 'pct_trib_aduan_banc', None),  # no separado en corpus
    ]
    for anio in [2024, 2025]:
        a = ANUARIO[anio]
        c = corpus_2024 if anio == 2024 else corpus_2025
        for nombre, key_a, key_c in materias:
            rows.append({
                'categoria': 'materia',
                'metrica': f'pct_{nombre}',
                'anio': anio,
                'anuario': a[key_a],
                'corpus': c[key_c] if key_c else None,
                'cobertura_pct': None,
                'comentario': '% de los recursos (anuario) / % del corpus'
            })

    # ---- VOTING PATTERNS (con advertencia conceptual) ----
    # OJO: las categorias del anuario no son identicas a las del corpus.
    # Anuario: "voto conjunto" + "voto propio" mezcla concurrencias formales y
    # sustantivas. Corpus: "segun_su_voto" exige texto separado.
    for anio in [2024, 2025]:
        a = ANUARIO[anio]
        c = corpus_2024 if anio == 2024 else corpus_2025
        rows.append({
            'categoria': 'votacion',
            'metrica': 'pct_unanimidad',
            'anio': anio,
            'anuario': a['pct_unanimidad'],
            'corpus': c['pct_unanime'],
            'cobertura_pct': None,
            'comentario': 'OJO: anuario cuenta "unanimidad" estricta (sin votos separados); corpus puede incluir casos con voto conjunto formal'
        })
        rows.append({
            'categoria': 'votacion',
            'metrica': 'pct_disidencia',
            'anio': anio,
            'anuario': a['pct_disidencia_propia'],
            'corpus': c['pct_disidencia'],
            'cobertura_pct': None,
            'comentario': 'COINCIDE BIEN entre ambas fuentes — disidencia formal'
        })
        # Concurrencia: anuario suma voto conjunto + voto propio
        anuario_concur = round(a['pct_voto_conjunto'] + a['pct_voto_propio'], 2)
        rows.append({
            'categoria': 'votacion',
            'metrica': 'pct_concurrencia_o_voto_separado',
            'anio': anio,
            'anuario': anuario_concur,
            'corpus': c['pct_concurrencia_total'],
            'cobertura_pct': None,
            'comentario': 'anuario = voto_conjunto+voto_propio (incluye formales); corpus = solo con texto separado'
        })

    # ---- OTROS ----
    for anio in [2024, 2025]:
        a = ANUARIO[anio]
        c = corpus_2024 if anio == 2024 else corpus_2025
        rows.append({
            'categoria': 'duracion',
            'metrica': 'mediana_dias_resueltos',
            'anio': anio,
            'anuario': a['duracion_mediana_dias'],
            'corpus': None,
            'cobertura_pct': None,
            'comentario': 'corpus no tiene fecha de presentacion del recurso'
        })
        rows.append({
            'categoria': 'remisiones',
            'metrica': 'pct_con_remision',
            'anio': anio,
            'anuario': a['pct_con_remision'],
            'corpus': None,
            'cobertura_pct': None,
            'comentario': 'parser v16 no detecta remisiones automaticamente'
        })
        rows.append({
            'categoria': 'conjueces',
            'metrica': 'pct_casos_con_conjueces',
            'anio': anio,
            'anuario': a['pct_casos_con_conjueces'],
            'corpus': None,
            'cobertura_pct': None,
            'comentario': 'parser detecta jueces; cruzar manualmente'
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    here = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    ruta_casos = here / 'csjn_casos_v16.csv'
    dir_salida = here / 'analisis'

    if not ruta_casos.exists():
        print(f"ERROR: no existe {ruta_casos}")
        sys.exit(1)

    dir_salida.mkdir(exist_ok=True)
    log = Log(dir_salida / 'cruce_anuarios_log.txt')

    log("=" * 70)
    log("CRUCE CORPUS CSJN vs ANUARIOS ESTADISTICOS 2024-2025")
    log("=" * 70)
    log()

    sub = cargar_corpus(ruta_casos, log)

    log()
    c24 = metricas_corpus(sub, 2024)
    c25 = metricas_corpus(sub, 2025)

    if c24 is None:
        log("ADVERTENCIA: no hay casos del corpus en 2024")
        return
    if c25 is None:
        log("ADVERTENCIA: no hay casos del corpus en 2025")
        return

    log(f"Casos en corpus 2024: {c24['n_corpus']}")
    log(f"Casos en corpus 2025: {c25['n_corpus']}")
    log()

    # Resumen de cobertura
    log("=" * 70)
    log("COBERTURA DEL CORPUS RESPECTO DEL ANUARIO")
    log("=" * 70)
    for anio, c in [(2024, c24), (2025, c25)]:
        a = ANUARIO[anio]
        log(f"\n{anio}:")
        log(f"  Casos resueltos (anuario):                {a['casos_resueltos']:>6}")
        log(f"  Casos tratados (anuario, sin formulas):   {a['casos_tratados']:>6}  ({100*a['casos_tratados']/a['casos_resueltos']:.1f}% de los resueltos)")
        log(f"  Casos en corpus (Fallos publicados):      {c['n_corpus']:>6}")
        log(f"    -> {100*c['n_corpus']/a['casos_resueltos']:.1f}% del universo resueltos")
        log(f"    -> {100*c['n_corpus']/a['casos_tratados']:.1f}% del universo tratados")
    log()

    # Tabla comparativa
    df = construir_tabla_comparativa(c24, c25, log)
    ruta_csv = dir_salida / '11_cruce_anuario.csv'
    df.to_csv(ruta_csv, index=False, encoding='utf-8')
    log(f"Tabla comparativa: {ruta_csv.name} ({len(df)} filas)")
    log()

    # Mostrar tabla pivoteada para lectura
    log("=" * 70)
    log("VISTA RAPIDA — METRICAS CLAVE")
    log("=" * 70)
    log()
    log("MATERIA: % en anuario vs % en corpus")
    log("(diferencia revela el sesgo editorial de la Coleccion de Fallos)")
    log()
    mat_view = df[df['categoria'] == 'materia'].copy()
    for _, r in mat_view.iterrows():
        a_val = f"{r['anuario']:.2f}" if pd.notna(r['anuario']) else 'n/a'
        c_val = f"{r['corpus']:.2f}" if pd.notna(r['corpus']) else 'n/a'
        log(f"  {r['anio']} {r['metrica']:<30} anuario={a_val:>6}%  corpus={c_val:>6}%")

    log()
    log("VOTACION:")
    vot_view = df[df['categoria'] == 'votacion'].copy()
    for _, r in vot_view.iterrows():
        a_val = f"{r['anuario']:.2f}" if pd.notna(r['anuario']) else 'n/a'
        c_val = f"{r['corpus']:.2f}" if pd.notna(r['corpus']) else 'n/a'
        log(f"  {r['anio']} {r['metrica']:<35} anuario={a_val:>6}%  corpus={c_val:>6}%")

    log()
    log("=" * 70)
    log("LECTURA INTERPRETATIVA")
    log("=" * 70)
    log("""
Los anuarios y la Coleccion de Fallos describen DOS UNIVERSOS COMPLEMENTARIOS:

  1. UNIVERSO ANUARIO (~26.000 casos/ano)
     - La Corte como administradora de litigiosidad masiva.
     - 82-85% se rechaza por art. 280 sin tratamiento sustantivo.
     - 88-93% remite a precedente o dictamen PGN.
     - Previsional concentra 40-58% (ANSES presentante en 91-93%).
     - Aqui la coordinacion es por economia procesal: las secretarias
       producen los proyectos, el voto conjunto formal del 27-34% no
       indica deliberacion sino firma agregada.

  2. UNIVERSO FALLOS (corpus, ~200 casos/ano publicados)
     - La Corte como productora de doctrina.
     - Lo que la Secretaria de Jurisprudencia decidio publicar.
     - Aqui se concentran los casos con disidencias razonadas,
       contencioso administrativo, casos federales relevantes.
     - Aqui la coordinacion es deliberativa, aunque buena parte arranca
       igualmente con un proyecto de secretaria que se discute, modifica
       o sobre el que se construyen votos propios.

La distincion no es binaria: hay un continuo entre "punto focal puro de
secretaria" y "deliberacion entre ministros y sus secretarios". Pero la
Coleccion de Fallos selecciona sistematicamente casos del segundo tipo,
y por eso es el universo apropiado para estudiar coordinacion deliberativa.

LA SECRETARIA DE JURISPRUDENCIA opera como filtro institucional entre
ambos regimenes — un poder que no figura en el organigrama formal pero es
decisivo para definir que cuenta como "jurisprudencia de la Corte".

VALIDACION CRUZADA DE HIPOTESIS:

  H2 (proyectos de secretaria como punto focal): respaldado fuertemente.
    En 2025 tres jueces resolvieron 26.524 casos (+39% vs 2024 con 5
    jueces). Materialmente imposible sin las secretarias.

  H3 (proliferacion de votos): visible en el corpus (concurrencias
    13-15% en 2024-2025). El anuario las cuenta como 50% (voto
    conjunto + voto propio) pero mezcla formal y sustantivo.

  H4 (bifurcacion regimen ordinario / regimen de doctrina): se ilumina.
    NO es originaria vs apelada (casi sin diferencia). Es masivo
    formulaico vs publicado deliberativo.

  H5 (autonomia burocracia letrada): consistente con la division del
    trabajo formal (jueces firman, secretarias proyectan) y con que en
    casos de imposibilidad de firma se recurre a conjueces (no a
    secretarias) — los limites se respetan formalmente, pero la
    autonomia material es enorme.
""")

    log.save()


if __name__ == '__main__':
    main()
