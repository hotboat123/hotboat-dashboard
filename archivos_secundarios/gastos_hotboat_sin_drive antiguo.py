import pandas as pd
import os
from funciones.funciones import leer_excel_banco_estado, ver_si_es_nacional_facturado, ver_si_es_nacional_no_facturado, leer_excel_mov_facturados_nacional, leer_excel_mov_no_facturados_nacional, leer_excel_mov_facturados_internacional, leer_excel_mov_no_facturados_internacional, leer_pdf, leer_excel_mercado_pago, limpiar_y_ordenar_dataframe, exportar_archivos, procesar_df_final, categorizar_por_descripcion
from inputs_modelo import diccionario_categorias, descripciones_a_eliminar, diccionario_categoria_1

valor_aproximado_dolar = 950
año_para_fecha_banco_estado = '2025'

# Diccionario de categorías para gastos
# Puedes modificar las palabras clave y categorías según tus necesidades

df_banco_estado_abonos = []
df_banco_estado_cargos = []
df_banco_chile_facturado_nacional = []
df_banco_chile_facturado_internacional = []


for archivo in os.listdir('archivos_input/archivos_input_costos'):
    ruta_archivo = os.path.join('archivos_input/archivos_input_costos', archivo)
    
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


df_banco_chile_facturado_internacional = pd.concat(df_banco_chile_facturado_internacional, ignore_index=True) 
df_banco_chile_facturado_nacional = pd.concat(df_banco_chile_facturado_nacional, ignore_index=True) 


# Procesar los DataFrames finales

df_final = procesar_df_final(
    df_banco_estado_cargos,
    df_banco_chile_facturado_internacional,
    df_banco_chile_facturado_nacional,
    diccionario_categorias,
    descripciones_a_eliminar,
    diccionario_categoria_1
)



df_banco_estado_abonos['Fecha'] = pd.to_datetime(df_banco_estado_abonos['Fecha'], format='%d/%m/%Y', errors='coerce')
df_abonos = pd.concat([df_banco_estado_abonos], axis=0)

# Exportar los archivos usando la nueva función
exportar_archivos(df_final, df_abonos)

