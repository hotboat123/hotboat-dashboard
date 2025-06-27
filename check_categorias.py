import pandas as pd

df = pd.read_csv('archivos_output/Utilidad operativa.csv')
print('Categorías en CSV:')
print(sorted(df['categoria'].unique()))

print('\nPrimeras filas:')
print(df.head())

print('\nVerificar fechas:')
print(df['fecha'].head())
print(f"Fechas nulas: {df['fecha'].isnull().sum()}") 