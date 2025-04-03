import pandas as pd
import os
from funciones import leer_excel_banco_estado, ver_si_es_nacional_facturado, ver_si_es_nacional_no_facturado, leer_excel_mov_facturados_nacional, leer_excel_mov_no_facturados_nacional, leer_excel_mov_facturados_internacional, leer_excel_mov_no_facturados_internacional, leer_pdf

valor_aproximado_dolar = 950
año_para_fecha_banco_estado = '2025'


df_banco_estado_abonos = []
df_banco_estado_cargos = []
df_banco_chile_facturado_nacional = []
df_banco_chile_facturado_internacional = []
df_banco_chile_no_facturado_nacional = []
df_banco_chile_no_facturado_internacional = []

for archivo in os.listdir('archivos'):
    ruta_archivo = os.path.join('archivos', archivo)
    
    # Determinar el tipo de archivo
    if archivo.endswith(".xlsx") or archivo.endswith(".xls"):
        df = pd.read_excel(ruta_archivo)
        if "Excel" in archivo:
            df_cargos, df_abonos = leer_excel_banco_estado(ruta_archivo, año_para_fecha_banco_estado)
            df_banco_estado_abonos.append(df_abonos)
            df_banco_estado_cargos.append(df_cargos)
        elif "Mov_Facturado" in archivo:
            if ver_si_es_nacional_facturado(ruta_archivo):
                df = leer_excel_mov_facturados_nacional(ruta_archivo)
                df_banco_chile_facturado_nacional.append(df)
            else: #es internacional
                df = leer_excel_mov_facturados_internacional(ruta_archivo, valor_aproximado_dolar)
                df_banco_chile_facturado_internacional.append(df)
        else: # es movimiento no facturado
            if ver_si_es_nacional_no_facturado(ruta_archivo):
                df = leer_excel_mov_no_facturados_nacional(ruta_archivo)
                df_banco_chile_no_facturado_nacional.append(df)
            else: #es internacional
                df = leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar)
                df_banco_chile_no_facturado_internacional.append(df)
    
#    elif archivo.endswith(".pdf"):
#        print(f"Procesando archivo PDF: {archivo}")
#        df = leer_pdf(ruta_archivo)
#        if df is not None:
#            # Aquí deberías implementar la lógica específica para procesar el PDF
#            # basado en su contenido y estructura
#            print(f"Contenido del PDF {archivo}:")
#            print(df.head())
            # Por ahora solo mostramos el contenido, pero deberías agregar la lógica
            # para clasificar y procesar el contenido según tus necesidades

df_banco_estado_abonos = pd.concat(df_banco_estado_abonos, ignore_index=True) 
df_banco_estado_cargos = pd.concat(df_banco_estado_cargos, ignore_index=True) 
df_banco_chile_facturado_internacional = pd.concat(df_banco_chile_facturado_internacional, ignore_index=True) 
df_banco_chile_facturado_nacional = pd.concat(df_banco_chile_facturado_nacional, ignore_index=True) 
df_banco_chile_no_facturado_nacional = pd.concat(df_banco_chile_no_facturado_nacional, ignore_index=True)  
df_banco_chile_no_facturado_internacional = pd.concat(df_banco_chile_no_facturado_internacional, ignore_index=True) 

df_final = pd.concat([df_banco_estado_cargos, df_banco_chile_facturado_internacional, df_banco_chile_facturado_nacional, df_banco_chile_no_facturado_nacional, df_banco_chile_no_facturado_internacional], ignore_index=True, sort=False)
df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], format='%d/%m/%Y', errors='coerce')
df_final = df_final.rename(columns={'Monto ($)': 'Monto'})
df_final = df_final[df_final['Monto'] >= 0]
df_final.to_csv("gastos hotboat.csv", index=False)  # Guarda sin índices

df_banco_estado_abonos['Fecha'] = pd.to_datetime(df_banco_estado_abonos['Fecha'], format='%d/%m/%Y', errors='coerce')
df_banco_estado_abonos = df_banco_estado_abonos.rename(columns={'Monto ($)': 'Monto'})
df_banco_estado_abonos.to_csv("abonos hotboat.csv", index=False) 
