import pandas as pd

# Verificar archivo de ingresos totales
print("=== VERIFICACIÓN DE INGRESOS TOTALES ===")
df_ingresos = pd.read_csv('archivos_output/ingresos_totales.csv')
print(f"Total registros: {len(df_ingresos)}")
print(f"Total monto: ${df_ingresos['monto'].sum():,.0f}")
print(f"Registros con monto 0: {len(df_ingresos[df_ingresos['monto'] == 0])}")
print(f"Total monto sin ceros: ${df_ingresos[df_ingresos['monto'] > 0]['monto'].sum():,.0f}")

print("\n=== VERIFICACIÓN DE RESERVAS ===")
df_reservas = pd.read_csv('archivos_output/reservas_HotBoat.csv')
print(f"Total reservas: {len(df_reservas)}")
print(f"Total PAID AMOUNT: ${df_reservas['PAID AMOUNT'].sum():,.0f}")
print(f"Reservas con PAID AMOUNT 0: {len(df_reservas[df_reservas['PAID AMOUNT'] == 0])}")

print("\n=== RESERVAS CON PAID AMOUNT 0 ===")
reservas_cero = df_reservas[df_reservas['PAID AMOUNT'] == 0]
print(reservas_cero[['ID', 'fecha_trip', 'Customer Email', 'PAID AMOUNT']].head(10))

print("\n=== VERIFICACIÓN DE ABONOS ===")
df_abonos = pd.read_csv('archivos_output/abonos hotboat.csv')
print(f"Total abonos: {len(df_abonos)}")
print(f"Total monto abonos: ${df_abonos['Monto'].sum():,.0f}")

print("\n=== COMPARACIÓN ===")
print(f"Diferencia entre abonos e ingresos: ${df_abonos['Monto'].sum() - df_ingresos['monto'].sum():,.0f}")
print(f"Diferencia entre abonos y PAID AMOUNT: ${df_abonos['Monto'].sum() - df_reservas['PAID AMOUNT'].sum():,.0f}") 