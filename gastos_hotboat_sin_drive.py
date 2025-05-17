import pandas as pd
import os
from funciones.funciones import leer_excel_banco_estado, ver_si_es_nacional_facturado, ver_si_es_nacional_no_facturado, leer_excel_mov_facturados_nacional, leer_excel_mov_no_facturados_nacional, leer_excel_mov_facturados_internacional, leer_excel_mov_no_facturados_internacional, leer_pdf, leer_excel_mercado_pago, limpiar_y_ordenar_dataframe, exportar_archivos

valor_aproximado_dolar = 950
año_para_fecha_banco_estado = '2025'
año_para_fecha_mercado_pago = '2025'


df_banco_estado_abonos = []
df_banco_estado_cargos = []
df_mercado_pago_abonos = []
df_mercado_pago_reembolsos = []
df_banco_chile_facturado_nacional = []
df_banco_chile_facturado_internacional = []
df_banco_chile_no_facturado_nacional = []
df_banco_chile_no_facturado_internacional = []

for archivo in os.listdir('archivos_input'):
    ruta_archivo = os.path.join('archivos_input', archivo)
    
    # Determinar el tipo de archivo
    if archivo.endswith(".xlsx") or archivo.endswith(".xls"):
        df = pd.read_excel(ruta_archivo)
        if "Chequera" in archivo:
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
        elif "No_Facturado" in archivo: # es movimiento no facturado
            if ver_si_es_nacional_no_facturado(ruta_archivo):
                df = leer_excel_mov_no_facturados_nacional(ruta_archivo)
                df_banco_chile_no_facturado_nacional.append(df)
            else: #es internacional
                df = leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar)
                df_banco_chile_no_facturado_internacional.append(df)
#        elif "MercadoPago" in archivo:
#            df_abonos, df_reembolsos = leer_excel_mercado_pago(ruta_archivo, año_para_fecha_mercado_pago)
#            df_mercado_pago_reembolsos.append(df_reembolsos)
#            df_mercado_pago_abonos.append(df_abonos)
        else:
            print('archivo no procesado:', archivo) 


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


# Limpiar y ordenar los DataFrames de banco estado
df_banco_estado_abonos = limpiar_y_ordenar_dataframe(df_banco_estado_abonos)
df_banco_estado_cargos = limpiar_y_ordenar_dataframe(df_banco_estado_cargos)
#df_mercado_pago_reembolsos = limpiar_y_ordenar_dataframe(df_mercado_pago_reembolsos)
#df_mercado_pago_abonos = limpiar_y_ordenar_dataframe(df_mercado_pago_abonos)
df_mercado_pago_reembolsos = pd.DataFrame()
df_mercado_pago_abonos = pd.DataFrame()

df_banco_chile_facturado_internacional = pd.concat(df_banco_chile_facturado_internacional, ignore_index=True) 
df_banco_chile_facturado_nacional = pd.concat(df_banco_chile_facturado_nacional, ignore_index=True) 
df_banco_chile_no_facturado_nacional = pd.concat(df_banco_chile_no_facturado_nacional, ignore_index=True)  
df_banco_chile_no_facturado_internacional = pd.concat(df_banco_chile_no_facturado_internacional, ignore_index=True) 

df_final = pd.concat([df_banco_estado_cargos, df_mercado_pago_abonos, df_banco_chile_facturado_internacional, df_banco_chile_facturado_nacional, df_banco_chile_no_facturado_nacional, df_banco_chile_no_facturado_internacional], ignore_index=True, sort=False)
df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], format='%d/%m/%Y', errors='coerce')
df_final = df_final[df_final['Monto'] >= 0]

# Remove duplicates based on Date, Description and Amount
df_final = df_final.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')

# Crear el directorio si no existe
os.makedirs('archivos_output', exist_ok=True)

df_banco_estado_abonos['Fecha'] = pd.to_datetime(df_banco_estado_abonos['Fecha'], format='%d/%m/%Y', errors='coerce')
df_abonos = pd.concat([df_banco_estado_abonos, df_mercado_pago_abonos], axis=0)

# Exportar los archivos usando la nueva función
exportar_archivos(df_final, df_abonos)

