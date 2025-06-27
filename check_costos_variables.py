import pandas as pd

# Cargar datos
df = pd.read_csv('archivos_output/gastos hotboat.csv')

# Filtrar costos variables
costos_vars = df[df['Categoría 1'] == 'Costos Variables']

print('Costos Variables:')
print(f'Total registros: {len(costos_vars)}')
print(f'Fechas nulas: {costos_vars["Fecha"].isnull().sum()}')

print('\nPrimeras filas:')
print(costos_vars[['Fecha', 'Descripción', 'Monto']].head())

print('\nTipo de columna Fecha:')
print(type(costos_vars['Fecha'].iloc[0]))

print('\nValores únicos de Fecha:')
print(costos_vars['Fecha'].unique())

print('\nColumnas disponibles:')
print(costos_vars.columns.tolist()) 