import pandas as pd
import os
from funciones.funciones import leer_excel_banco_estado, ver_si_es_nacional_facturado, ver_si_es_nacional_no_facturado, leer_excel_mov_facturados_nacional, leer_excel_mov_no_facturados_nacional, leer_excel_mov_facturados_internacional, leer_excel_mov_no_facturados_internacional, leer_pdf
from funciones.funciones_reservas import procesar_fechas_reservas, procesar_appointments, procesar_reservas
# from analisis_graficos import graficar_reservas_por_dia_mes

# Inicializar variables
payments = None
appointments = None
df_reservas_original = None

# Leer archivos de input
for archivo in os.listdir('archivos_input/Archivos input reservas/'):
    ruta_archivo = os.path.join('archivos_input/Archivos input reservas/', archivo)
    if archivo.endswith(".csv"):
        df = pd.read_csv(ruta_archivo)
        if "payments" in archivo:
            payments = df
        elif "appointments" in archivo:
            appointments = df
        elif "reservas" in archivo:
            df_reservas_original = procesar_fechas_reservas(df)

# Procesar las nuevas reservas
df_reservas_nuevas = procesar_appointments(payments, appointments)

# Procesar todas las reservas
df_reservas = procesar_reservas(df_reservas_original, df_reservas_nuevas)

# Guardar el DataFrame en un archivo CSV
df_reservas.to_csv("archivos_input/Archivos input reservas/reservas_HotBoat.csv", index=False)
df_reservas.to_csv("archivos_output/reservas_HotBoat.csv", index=False)

# Generar gráfico de reservas por día y mes
# graficar_reservas_por_dia_mes(df_reservas)