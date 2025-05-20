import pandas as pd
import os

ruta_base = 'archivos_input/archivos input marketing'
archivo_google = os.path.join(ruta_base, 'gasto diario en google ads.csv')
archivo_meta = os.path.join(ruta_base, 'gasto diario en meta.csv')

try:
    df_google = pd.read_csv(archivo_google, skiprows=2)
    df_google = df_google[['Día', 'Costo']]
    df_google = df_google.rename(columns={'Día': 'fecha', 'Costo': 'monto'})
    df_google['plataforma'] = 'Google Ads'

    df_meta = pd.read_csv(archivo_meta)
    df_meta = df_meta[['Día', 'Importe gastado (CLP)']]
    df_meta = df_meta.rename(columns={'Día': 'fecha', 'Importe gastado (CLP)': 'monto'})
    df_meta['plataforma'] = 'Meta'

    df_combinado = pd.concat([df_google, df_meta], ignore_index=True)
    df_combinado = df_combinado.sort_values('fecha')
    df_combinado = df_combinado[['fecha', 'plataforma', 'monto']]
    
    df_combinado.to_csv('archivos_output/gastos_marketing.csv', index=False)
    print("Archivo gastos_marketing.csv creado exitosamente.")
    print("\nPrimeras 5 filas:")
    print(df_combinado.head())
    
except Exception as e:
    print(f"Error: {e}")