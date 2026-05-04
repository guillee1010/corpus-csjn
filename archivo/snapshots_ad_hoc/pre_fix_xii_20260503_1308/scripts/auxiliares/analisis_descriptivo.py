#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_descriptivo.py

Analisis estadistico descriptivo del corpus CSJN parseado por csjnv16.py.
Produce 10 tablas tematicas en CSV + un Excel con todo en sheets separadas.

Uso (PowerShell):
    cd "C:\\Users\\guill\\My Drive\\Posgrados\\Maestria UBA\\Tesis UBA\\AC\\paginas"
    python analisis_descriptivo.py

Asume:
  - csjn_casos_v16.csv y csjn_casos_v16_votos.csv en el directorio actual.
  - Output va a la subcarpeta analisis/ (la crea si no existe).

Filtrado del corpus para el analisis principal:
  - Se excluyen casos con anomalias graves:
    * bloques > 10000 lineas (fallos multiples concatenados)
    * anios inconsistentes con el tomo (delta_anios fuera de [-2, +1])
    * status_localizacion in {pagina_fin_no_en_mapa, fallo_cruza_archivos, ultimo_del_tomo}
  - El criterio queda registrado en el log y en la tabla 02 de diagnostico.
"""

import sys
from pathlib import Path
from collections import Counter

import pandas as pd


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

ANIOS_TOMO = {
    329: 2006, 330: 2007, 331: 2008, 332: 2009, 333: 2010, 334: 2011,
    337: 2014, 338: 2015, 339: 2016, 340: 2017, 341: 2018, 342: 2019,
    343: 2020, 344: 2021, 345: 2022, 346: 2023, 347: 2024, 348: 2025,
    349: 2026,
}

# Composicion oficial del banco por anio
COMPOSICION_CORTE = {
    2006: ['Petracchi', 'Belluscio', 'Boggiano', 'Maqueda', 'Highton de Nolasco',
           'Fayt', 'Zaffaroni', 'Lorenzetti', 'Argibay'],
    2007: ['Petracchi', 'Highton de Nolasco', 'Fayt', 'Zaffaroni', 'Lorenzetti',
           'Argibay', 'Maqueda'],
    2008: ['Petracchi', 'Highton de Nolasco', 'Fayt', 'Zaffaroni', 'Lorenzetti',
           'Argibay', 'Maqueda'],
    2009: ['Petracchi', 'Highton de Nolasco', 'Fayt', 'Zaffaroni', 'Lorenzetti',
           'Argibay', 'Maqueda'],
    2010: ['Petracchi', 'Highton de Nolasco', 'Fayt', 'Zaffaroni', 'Lorenzetti',
           'Argibay', 'Maqueda'],
    2011: ['Petracchi', 'Highton de Nolasco', 'Fayt', 'Zaffaroni', 'Lorenzetti',
           'Argibay', 'Maqueda'],
    2014: ['Petracchi', 'Highton de Nolasco', 'Fayt', 'Zaffaroni', 'Lorenzetti',
           'Argibay', 'Maqueda'],
    2015: ['Highton de Nolasco', 'Fayt', 'Lorenzetti', 'Maqueda'],
    2016: ['Highton de Nolasco', 'Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2017: ['Highton de Nolasco', 'Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2018: ['Highton de Nolasco', 'Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2019: ['Highton de Nolasco', 'Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2020: ['Highton de Nolasco', 'Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2021: ['Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2022: ['Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2023: ['Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2024: ['Lorenzetti', 'Maqueda', 'Rosatti', 'Rosenkrantz'],
    2025: ['Lorenzetti', 'Rosatti', 'Rosenkrantz'],
    2026: ['Lorenzetti', 'Rosatti', 'Rosenkrantz'],
}


# ---------------------------------------------------------------------------
# Logging dual: consola + archivo
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
# Carga y filtrado
# ---------------------------------------------------------------------------

def cargar_datos(ruta_casos, ruta_votos, log):
    casos = pd.read_csv(ruta_casos)
    votos = pd.read_csv(ruta_votos)

    casos['anio'] = casos['date'].str.extract(r'(\d{4})$').astype('Int64')
    casos['anio_esperado'] = casos['tomo'].map(ANIOS_TOMO).astype('Int64')
    casos['delta_anios'] = casos['anio'] - casos['anio_esperado']
    casos['tam_bloque'] = casos['linea_fin_real'] - casos['linea_inicio']

    log(f"Casos cargados: {len(casos)}")
    log(f"Votos cargados: {len(votos)}")
    log()

    return casos, votos


def aplicar_filtros(casos, log):
    n = len(casos)
    casos['excl_bloque_gigante'] = casos['tam_bloque'] > 10000
    casos['excl_anio_inconsistente'] = (
        casos['anio'].notna() &
        ((casos['delta_anios'] < -2) | (casos['delta_anios'] > 1))
    )
    status_excluidos = {'pagina_fin_no_en_mapa', 'fallo_cruza_archivos', 'ultimo_del_tomo'}
    casos['excl_status_raro'] = casos['status_localizacion'].isin(status_excluidos)

    casos['en_subset_limpio'] = ~(
        casos['excl_bloque_gigante'] |
        casos['excl_anio_inconsistente'] |
        casos['excl_status_raro']
    )

    log("=" * 70)
    log("FILTRADO DEL CORPUS")
    log("=" * 70)
    log(f"  Total casos:                     {n}")
    log(f"  Excluidos por bloque gigante:    {int(casos['excl_bloque_gigante'].sum())}")
    log(f"  Excluidos por anio inconsistente:{int(casos['excl_anio_inconsistente'].sum())}")
    log(f"  Excluidos por status raro:       {int(casos['excl_status_raro'].sum())}")
    log(f"  --- los criterios pueden solaparse ---")
    log(f"  Total excluidos (union):         {int((~casos['en_subset_limpio']).sum())}")
    log(f"  Subset limpio:                   {int(casos['en_subset_limpio'].sum())}  ({100*casos['en_subset_limpio'].sum()/n:.1f}%)")
    log()

    return casos


# ---------------------------------------------------------------------------
# Tabla 01: Volumetria
# ---------------------------------------------------------------------------

def tabla_volumetria(casos, log):
    log("Generando 01_volumetria...")
    sub = casos[casos['en_subset_limpio']].copy()

    por_anio = sub.groupby('anio', dropna=True).agg(
        n_fallos=('caso_id_canonico', 'count'),
        wc_mediana=('word_count', 'median'),
        wc_promedio=('word_count', 'mean'),
        n_unanime=('voting_pattern', lambda x: int((x == 'unanime').sum())),
        n_disidencia=('voting_pattern', lambda x: int((x == 'disidencia').sum())),
        n_segun_su_voto=('voting_pattern', lambda x: int((x == 'segun_su_voto').sum())),
        n_mixed=('voting_pattern', lambda x: int((x == 'mixed').sum())),
    ).reset_index()
    por_anio['anio'] = por_anio['anio'].astype('Int64')
    por_anio['wc_mediana'] = por_anio['wc_mediana'].round(0).astype('Int64')
    por_anio['wc_promedio'] = por_anio['wc_promedio'].round(0).astype('Int64')

    por_tomo = sub.groupby('tomo').agg(
        n_fallos=('caso_id_canonico', 'count'),
        anio_esperado=('anio_esperado', 'first'),
        wc_mediana=('word_count', 'median'),
    ).reset_index()
    por_tomo['wc_mediana'] = por_tomo['wc_mediana'].round(0).astype('Int64')
    por_tomo['anio_esperado'] = por_tomo['anio_esperado'].astype('Int64')

    return {'por_anio': por_anio, 'por_tomo': por_tomo}


# ---------------------------------------------------------------------------
# Tabla 02: Diagnostico del corpus
# ---------------------------------------------------------------------------

def tabla_diagnostico(casos, log):
    log("Generando 02_diagnostico_corpus...")
    n = len(casos)

    por_status_loc = casos['status_localizacion'].value_counts(dropna=False).reset_index()
    por_status_loc.columns = ['status_localizacion', 'n']
    por_status_loc['pct'] = (100 * por_status_loc['n'] / n).round(2)

    por_status_fin = casos['status_fin'].value_counts(dropna=False).reset_index()
    por_status_fin.columns = ['status_fin', 'n']
    por_status_fin['pct'] = (100 * por_status_fin['n'] / n).round(2)

    por_pista_fin = casos['pista_fin'].value_counts(dropna=False).reset_index()
    por_pista_fin.columns = ['pista_fin', 'n']
    por_pista_fin['pct'] = (100 * por_pista_fin['n'] / n).round(2)

    sin_fecha = int(casos['date'].isna().sum())

    resumen = pd.DataFrame([
        {'metrica': 'total_casos', 'valor': n, 'pct': 100.0},
        {'metrica': 'subset_limpio', 'valor': int(casos['en_subset_limpio'].sum()),
         'pct': round(100 * casos['en_subset_limpio'].sum() / n, 2)},
        {'metrica': 'sin_fecha_extraida', 'valor': sin_fecha,
         'pct': round(100 * sin_fecha / n, 2)},
        {'metrica': 'bloque_gigante_>10k_lineas', 'valor': int(casos['excl_bloque_gigante'].sum()),
         'pct': round(100 * casos['excl_bloque_gigante'].sum() / n, 2)},
        {'metrica': 'anio_inconsistente_con_tomo', 'valor': int(casos['excl_anio_inconsistente'].sum()),
         'pct': round(100 * casos['excl_anio_inconsistente'].sum() / n, 2)},
        {'metrica': 'status_localizacion_raro', 'valor': int(casos['excl_status_raro'].sum()),
         'pct': round(100 * casos['excl_status_raro'].sum() / n, 2)},
    ])

    return {
        'resumen': resumen,
        'por_status_localizacion': por_status_loc,
        'por_status_fin': por_status_fin,
        'por_pista_fin': por_pista_fin,
    }


# ---------------------------------------------------------------------------
# Tabla 03: Outcomes
# ---------------------------------------------------------------------------

def tabla_outcomes(casos, log):
    log("Generando 03_outcomes...")
    sub = casos[casos['en_subset_limpio']].copy()

    g = sub['outcome'].value_counts(dropna=False).reset_index()
    g.columns = ['outcome', 'n']
    g['pct'] = (100 * g['n'] / len(sub)).round(2)

    por_anio = sub.groupby(['anio', 'outcome']).size().unstack(fill_value=0).reset_index()
    por_anio['anio'] = por_anio['anio'].astype('Int64')
    cols_outcome = [c for c in por_anio.columns if c != 'anio']
    por_anio['total'] = por_anio[cols_outcome].sum(axis=1)

    por_anio_pct = por_anio[['anio', 'total']].copy()
    for c in cols_outcome:
        por_anio_pct[c + '_pct'] = (100 * por_anio[c] / por_anio['total']).round(2)

    return {'global': g, 'por_anio_n': por_anio, 'por_anio_pct': por_anio_pct}


# ---------------------------------------------------------------------------
# Tabla 04: Voting patterns (CENTRAL para H3)
# ---------------------------------------------------------------------------

def tabla_voting_patterns(casos, log):
    log("Generando 04_voting_patterns...")
    sub = casos[casos['en_subset_limpio']].copy()

    g = sub['voting_pattern'].value_counts(dropna=False).reset_index()
    g.columns = ['voting_pattern', 'n']
    g['pct'] = (100 * g['n'] / len(sub)).round(2)

    por_anio = sub.groupby(['anio', 'voting_pattern']).size().unstack(fill_value=0).reset_index()
    por_anio['anio'] = por_anio['anio'].astype('Int64')
    cols_pattern = [c for c in por_anio.columns if c != 'anio']
    por_anio['total'] = por_anio[cols_pattern].sum(axis=1)

    por_anio_pct = por_anio[['anio', 'total']].copy()
    for c in cols_pattern:
        por_anio_pct[c + '_pct'] = (100 * por_anio[c] / por_anio['total']).round(2)

    if 'segun_su_voto_pct' in por_anio_pct.columns and 'mixed_pct' in por_anio_pct.columns:
        por_anio_pct['concurrencias_pct'] = (
            por_anio_pct['segun_su_voto_pct'] + por_anio_pct['mixed_pct']
        ).round(2)
    elif 'segun_su_voto_pct' in por_anio_pct.columns:
        por_anio_pct['concurrencias_pct'] = por_anio_pct['segun_su_voto_pct']

    return {'global': g, 'por_anio_n': por_anio, 'por_anio_pct': por_anio_pct}


# ---------------------------------------------------------------------------
# Tabla 05: Composicion de la Corte (H4)
# ---------------------------------------------------------------------------

def tabla_composicion_corte(casos, log):
    log("Generando 05_composicion_corte...")
    sub = casos[casos['en_subset_limpio']].copy()

    by_anio = sub.groupby('anio', dropna=True).agg(
        n_fallos=('caso_id_canonico', 'count'),
        n_jueces_mediana=('n_jueces', 'median'),
        n_jueces_moda=('n_jueces', lambda x: x.mode().iloc[0] if len(x) > 0 else None),
        pct_unanime=('voting_pattern', lambda x: round(100 * (x == 'unanime').mean(), 2)),
        pct_disidencia=('voting_pattern', lambda x: round(100 * (x == 'disidencia').mean(), 2)),
        pct_concurrencia=('voting_pattern', lambda x: round(100 * x.isin(['segun_su_voto', 'mixed']).mean(), 2)),
    ).reset_index()
    by_anio['anio'] = by_anio['anio'].astype('Int64')

    comp = []
    for anio, jueces in COMPOSICION_CORTE.items():
        comp.append({
            'anio': anio,
            'n_jueces_oficial': len(jueces),
            'jueces_oficial': '|'.join(jueces),
        })
    df_comp = pd.DataFrame(comp)
    by_anio = by_anio.merge(df_comp, on='anio', how='left')

    return {'por_anio': by_anio}


# ---------------------------------------------------------------------------
# Tabla 06: Productividad por juez (H5)
# ---------------------------------------------------------------------------

def tabla_jueces_productividad(casos, votos, log):
    log("Generando 06_jueces_productividad...")
    sub_casos = casos[casos['en_subset_limpio']].copy()
    sub_votos = votos[votos['caso_id_canonico'].isin(sub_casos['caso_id_canonico'])]

    # OJO: el parser usa 'segun su voto' con tilde; tambien existe variante
    # 'por su voto' (raro). Ambas se cuentan como concurrencia.
    posiciones_concurrencia = ['segun su voto', 'según su voto', 'por su voto']
    por_juez = sub_votos.groupby('juez').agg(
        n_total=('caso_id_canonico', 'count'),
        n_mayoria=('posicion', lambda x: int((x == 'mayoria').sum())),
        n_concurrencia=('posicion', lambda x: int(x.isin(posiciones_concurrencia).sum())),
        n_disidencia=('posicion', lambda x: int((x == 'en disidencia').sum())),
        # wc_voto = 0 para mayorias sin voto separado; mediana de los > 0
        wc_voto_mediana_cuando_separado=('wc_voto', lambda x: x[x > 0].median() if (x > 0).any() else 0),
    ).reset_index()
    por_juez['wc_voto_mediana_cuando_separado'] = por_juez['wc_voto_mediana_cuando_separado'].round(0).astype('Int64')
    por_juez['pct_concurrencia'] = (100 * por_juez['n_concurrencia'] / por_juez['n_total']).round(2)
    por_juez['pct_disidencia'] = (100 * por_juez['n_disidencia'] / por_juez['n_total']).round(2)
    por_juez = por_juez.sort_values('n_total', ascending=False)

    return {'por_juez': por_juez}


# ---------------------------------------------------------------------------
# Tabla 07: Diadicas entre jueces (H1/H2)
# ---------------------------------------------------------------------------

def tabla_jueces_diadicas(casos, votos, log):
    log("Generando 07_jueces_diadicas...")
    sub_casos = casos[casos['en_subset_limpio']].copy()
    sub_votos = votos[votos['caso_id_canonico'].isin(sub_casos['caso_id_canonico'])]

    pares = Counter()
    pares_misma_posicion = Counter()
    pares_distinta_posicion = Counter()

    for caso_id, grupo in sub_votos.groupby('caso_id_canonico'):
        registros = list(grupo[['juez', 'posicion']].itertuples(index=False, name=None))
        for i, (j1, p1) in enumerate(registros):
            for j2, p2 in registros[i+1:]:
                par = tuple(sorted([str(j1), str(j2)]))
                pares[par] += 1
                if p1 == p2:
                    pares_misma_posicion[par] += 1
                else:
                    pares_distinta_posicion[par] += 1

    rows = []
    for par, total in pares.most_common():
        misma = pares_misma_posicion[par]
        distinta = pares_distinta_posicion[par]
        rows.append({
            'juez_a': par[0],
            'juez_b': par[1],
            'n_casos_compartidos': total,
            'n_misma_posicion': misma,
            'n_distinta_posicion': distinta,
            'pct_misma_posicion': round(100 * misma / total, 2) if total > 0 else 0.0,
        })

    df = pd.DataFrame(rows)
    if len(df):
        df = df.sort_values('n_casos_compartidos', ascending=False)
    return {'pares': df}


# ---------------------------------------------------------------------------
# Tabla 08: Word counts (H3 boilerplate vs razonado)
# ---------------------------------------------------------------------------

def tabla_word_counts(casos, votos, log):
    log("Generando 08_word_counts...")
    sub_casos = casos[casos['en_subset_limpio']].copy()
    sub_votos = votos[votos['caso_id_canonico'].isin(sub_casos['caso_id_canonico'])]

    by_pattern = sub_casos.groupby('voting_pattern').agg(
        n=('caso_id_canonico', 'count'),
        wc_mediana=('word_count', 'median'),
        wc_p25=('word_count', lambda x: x.quantile(0.25)),
        wc_p75=('word_count', lambda x: x.quantile(0.75)),
        wc_promedio=('word_count', 'mean'),
        wc_max=('word_count', 'max'),
    ).reset_index()
    for c in ['wc_mediana', 'wc_p25', 'wc_p75', 'wc_promedio', 'wc_max']:
        by_pattern[c] = by_pattern[c].round(0).astype('Int64')

    by_outcome = sub_casos.groupby('outcome').agg(
        n=('caso_id_canonico', 'count'),
        wc_mediana=('word_count', 'median'),
        wc_p25=('word_count', lambda x: x.quantile(0.25)),
        wc_p75=('word_count', lambda x: x.quantile(0.75)),
    ).reset_index()
    for c in ['wc_mediana', 'wc_p25', 'wc_p75']:
        by_outcome[c] = by_outcome[c].round(0).astype('Int64')

    # NOTA: muchos votos tienen wc_voto = 0 porque solo se computa el texto
    # separado (no para mayorias sin voto independiente). Filtramos > 0
    # para calcular percentiles significativos.
    sub_votos_con_wc = sub_votos[sub_votos['wc_voto'] > 0].copy()
    by_posicion = sub_votos_con_wc.groupby('posicion').agg(
        n=('caso_id_canonico', 'count'),
        wc_mediana=('wc_voto', 'median'),
        wc_p25=('wc_voto', lambda x: x.quantile(0.25)),
        wc_p75=('wc_voto', lambda x: x.quantile(0.75)),
        wc_promedio=('wc_voto', 'mean'),
    ).reset_index()
    for c in ['wc_mediana', 'wc_p25', 'wc_p75', 'wc_promedio']:
        by_posicion[c] = by_posicion[c].round(0).astype('Int64')

    return {'por_voting_pattern': by_pattern, 'por_outcome': by_outcome, 'por_posicion_voto': by_posicion}


# ---------------------------------------------------------------------------
# Tabla 09: Originaria vs apelada (H4 bifurcacion)
# ---------------------------------------------------------------------------

def tabla_originaria_apelada(casos, log):
    log("Generando 09_originaria_vs_apelada...")
    sub = casos[casos['en_subset_limpio']].copy()
    sub['categoria'] = sub['is_originaria'].apply(lambda x: 'originaria' if x else 'apelada')

    df = sub.groupby('categoria').agg(
        n_fallos=('caso_id_canonico', 'count'),
        wc_mediana=('word_count', 'median'),
        pct_unanime=('voting_pattern', lambda x: round(100 * (x == 'unanime').mean(), 2)),
        pct_disidencia=('voting_pattern', lambda x: round(100 * (x == 'disidencia').mean(), 2)),
        pct_concurrencia=('voting_pattern', lambda x: round(100 * x.isin(['segun_su_voto', 'mixed']).mean(), 2)),
    ).reset_index()
    df['wc_mediana'] = df['wc_mediana'].round(0).astype('Int64')

    cruz = sub.groupby(['anio', 'categoria']).agg(
        n=('caso_id_canonico', 'count'),
        pct_unanime=('voting_pattern', lambda x: round(100 * (x == 'unanime').mean(), 2)),
    ).reset_index()
    cruz['anio'] = cruz['anio'].astype('Int64')

    return {'global': df, 'por_anio_y_categoria': cruz}


# ---------------------------------------------------------------------------
# Tabla 10: Presencia de dictamen
# ---------------------------------------------------------------------------

def tabla_dictamen(casos, log):
    log("Generando 10_dictamen_presence...")
    sub = casos[casos['en_subset_limpio']].copy()

    df = sub.groupby('anio').agg(
        n_fallos=('caso_id_canonico', 'count'),
        n_con_dictamen=('dictamen_presente', 'sum'),
    ).reset_index()
    df['anio'] = df['anio'].astype('Int64')
    df['pct_con_dictamen'] = (100 * df['n_con_dictamen'] / df['n_fallos']).round(2)

    return {'por_anio': df}


# ---------------------------------------------------------------------------
# Output: CSVs sueltos + Excel resumen
# ---------------------------------------------------------------------------

def guardar_outputs(tablas, dir_salida, log):
    dir_salida = Path(dir_salida)
    dir_salida.mkdir(parents=True, exist_ok=True)

    config = [
        ('01_volumetria.csv', tablas['volumetria']),
        ('02_diagnostico_corpus.csv', tablas['diagnostico']),
        ('03_outcomes.csv', tablas['outcomes']),
        ('04_voting_patterns.csv', tablas['voting_patterns']),
        ('05_composicion_corte.csv', tablas['composicion']),
        ('06_jueces_productividad.csv', tablas['productividad']),
        ('07_jueces_diadicas.csv', tablas['diadicas']),
        ('08_word_counts.csv', tablas['word_counts']),
        ('09_originaria_vs_apelada.csv', tablas['originaria']),
        ('10_dictamen_presence.csv', tablas['dictamen']),
    ]

    # CSVs sueltos
    for filename, dfs_dict in config:
        if isinstance(dfs_dict, dict):
            partes = []
            for nombre_sub, df in dfs_dict.items():
                df_copy = df.copy()
                df_copy.insert(0, 'subtabla', nombre_sub)
                partes.append(df_copy)
            df_concat = pd.concat(partes, ignore_index=True, sort=False)
        else:
            df_concat = dfs_dict.copy()
        ruta = dir_salida / filename
        df_concat.to_csv(ruta, index=False, encoding='utf-8')
        log(f"  Escrito: {ruta.name}  ({len(df_concat)} filas)")

    # Excel resumen
    excel_path = dir_salida / 'analisis_descriptivo.xlsx'
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for filename, dfs_dict in config:
                tabla_n = filename.split('_')[0]
                if isinstance(dfs_dict, dict):
                    for nombre_sub, df in dfs_dict.items():
                        sheet = f"{tabla_n}_{nombre_sub}"[:31]
                        df.to_excel(writer, sheet_name=sheet, index=False)
                else:
                    sheet = filename.replace('.csv', '')[:31]
                    dfs_dict.to_excel(writer, sheet_name=sheet, index=False)
        log(f"  Excel resumen: {excel_path.name}")
    except ImportError:
        log("  ! openpyxl no instalado - no se genero el .xlsx")
        log("    instalar con: pip install openpyxl")
    log()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    here = Path(__file__).parent if '__file__' in globals() else Path.cwd()

    ruta_casos = here / 'csjn_casos_v16.csv'
    ruta_votos = here / 'csjn_casos_v16_votos.csv'
    dir_salida = here / 'analisis'

    if not ruta_casos.exists():
        print(f"ERROR: no existe {ruta_casos}")
        sys.exit(1)
    if not ruta_votos.exists():
        print(f"ERROR: no existe {ruta_votos}")
        sys.exit(1)

    dir_salida.mkdir(exist_ok=True)
    log = Log(dir_salida / 'analisis_log.txt')

    log("=" * 70)
    log("ANALISIS DESCRIPTIVO DEL CORPUS CSJN (v16)")
    log("=" * 70)
    log()

    casos, votos = cargar_datos(ruta_casos, ruta_votos, log)
    casos = aplicar_filtros(casos, log)

    tablas = {
        'volumetria':       tabla_volumetria(casos, log),
        'diagnostico':      tabla_diagnostico(casos, log),
        'outcomes':         tabla_outcomes(casos, log),
        'voting_patterns':  tabla_voting_patterns(casos, log),
        'composicion':      tabla_composicion_corte(casos, log),
        'productividad':    tabla_jueces_productividad(casos, votos, log),
        'diadicas':         tabla_jueces_diadicas(casos, votos, log),
        'word_counts':      tabla_word_counts(casos, votos, log),
        'originaria':       tabla_originaria_apelada(casos, log),
        'dictamen':         tabla_dictamen(casos, log),
    }

    log()
    log("=" * 70)
    log("OUTPUTS")
    log("=" * 70)
    guardar_outputs(tablas, dir_salida, log)

    log("=" * 70)
    log("RESUMEN")
    log("=" * 70)
    sub = casos[casos['en_subset_limpio']]
    log(f"  Subset analizado: {len(sub)} fallos limpios de {len(casos)} totales")
    if len(sub) > 0:
        anio_min = sub['anio'].dropna().min()
        anio_max = sub['anio'].dropna().max()
        log(f"  Cobertura temporal: {anio_min} - {anio_max}")
        unanime = (sub['voting_pattern'] == 'unanime').mean()
        disidencia = (sub['voting_pattern'] == 'disidencia').mean()
        concurrencia = sub['voting_pattern'].isin(['segun_su_voto', 'mixed']).mean()
        log(f"  Unanimidad global:    {100*unanime:.1f}%")
        log(f"  Disidencia global:    {100*disidencia:.1f}%")
        log(f"  Concurrencia global:  {100*concurrencia:.1f}%")
    log()
    log("Listo. Mira analisis/analisis_descriptivo.xlsx para ver todo.")

    log.save()


if __name__ == '__main__':
    main()
