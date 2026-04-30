import pandas as pd

casos = pd.read_csv('csjn_casos_v10.csv', low_memory=False)
orig = casos[casos['is_originaria']==1]

print(f'N total corpus: {len(casos)}')
print(f'N marcados originaria: {len(orig)}')
print(f'Porcentaje: {round(100*len(orig)/len(casos), 1)}%')

# Resumen 1: tribunal_origen
t1 = orig['tribunal_origen'].value_counts().reset_index()
t1.columns = ['tribunal_origen', 'n_casos']
t1.to_csv('diag_originaria_tribunal.csv', index=False)
print(f'\nGuardado: diag_originaria_tribunal.csv ({len(t1)} valores distintos)')

# Resumen 2: outcome
t2 = orig['outcome'].value_counts().reset_index()
t2.columns = ['outcome', 'n_casos']
t2.to_csv('diag_originaria_outcome.csv', index=False)
print(f'Guardado: diag_originaria_outcome.csv')

# Resumen 3: por tomo
t3 = orig.groupby('tomo')['caso_id'].count().reset_index()
t3.columns = ['tomo', 'n_casos']
t3.to_csv('diag_originaria_por_tomo.csv', index=False)
print(f'Guardado: diag_originaria_por_tomo.csv')

# Muestra de 50 casos para inspección manual
muestra = orig[['caso_id','tomo','date','case_name','outcome',
                'voting_pattern','tribunal_origen','por_ello_text']].head(50)
muestra.to_csv('diag_originaria_muestra50.csv', index=False)
print(f'Guardado: diag_originaria_muestra50.csv (50 casos para inspección)')
