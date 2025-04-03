import pandas as pd
import os
from funciones import leer_excel_banco_estado, ver_si_es_nacional_facturado, ver_si_es_nacional_no_facturado, leer_excel_mov_facturados_nacional, leer_excel_mov_no_facturados_nacional, leer_excel_mov_facturados_internacional, leer_excel_mov_no_facturados_internacional, leer_pdf
from funciones_reservas import procesar_fechas_reservas, procesar_appointments, procesar_reservas
from analisis_graficos import graficar_reservas_por_dia_mes
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
    if archivo.endswith(".csv"):
        df = pd.read_csv(ruta_archivo)
        if "payments" in archivo:
            payments = df
        elif "appointments" in archivo:
            appointments = df
        elif "reservas" in archivo:
            df_reservas_original = procesar_fechas_reservas(df)

df_reservas_nuevas = procesar_appointments(payments, appointments)
df_reservas = procesar_reservas(df_reservas_original, df_reservas_nuevas)

# Guardar el DataFrame en un archivo CSV
df_reservas.to_csv("archivos/reservas_HotBoat.csv", index=False)

# Generar gráfico de reservas por día y mes
graficar_reservas_por_dia_mes(df_reservas)
