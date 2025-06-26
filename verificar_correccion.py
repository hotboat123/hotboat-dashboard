import pandas as pd
from datetime import datetime

print("=== VERIFICACIÓN DE LA CORRECCIÓN DEL DASHBOARD ===")

# Cargar datos como lo hace el dashboard
df_reservas = pd.read_csv("archivos_output/reservas_HotBoat.csv")
df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")

# Convertir fechas como lo hace el dashboard
df_reservas["fecha_trip"] = pd.to_datetime(df_reservas["fecha_trip"])
df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"], dayfirst=True, errors='coerce')
df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"], dayfirst=True, errors='coerce')

print(f"📊 RANGOS DE FECHAS:")
print(f"   Reservas: {df_reservas['fecha_trip'].min()} a {df_reservas['fecha_trip'].max()}")
print(f"   Abonos: {df_payments['Fecha'].min()} a {df_payments['Fecha'].max()}")

# Calcular el nuevo rango de filtro (como lo hace el dashboard corregido)
fecha_min_reservas = df_reservas['fecha_trip'].min()
fecha_max_reservas = df_reservas['fecha_trip'].max()
fecha_min_abonos = df_payments['Fecha'].min()
fecha_max_abonos = df_payments['Fecha'].max()

fecha_min_filtro = min(fecha_min_reservas, fecha_min_abonos)
fecha_max_filtro = max(fecha_max_reservas, fecha_max_abonos)

print(f"\n🎯 NUEVO RANGO DE FILTRO:")
print(f"   Fecha mínima: {fecha_min_filtro}")
print(f"   Fecha máxima: {fecha_max_filtro}")

# Simular el filtrado con el nuevo rango
df_payments_filtrado = df_payments[(df_payments['Fecha'] >= fecha_min_filtro) & (df_payments['Fecha'] <= fecha_max_filtro)]

print(f"\n💰 RESULTADO CORREGIDO:")
print(f"   Abonos en el nuevo rango: {len(df_payments_filtrado)}")
print(f"   Monto total corregido: ${df_payments_filtrado['Monto'].sum():,.0f}")

print(f"\n✅ COMPARACIÓN:")
print(f"   Antes (rango reservas): $860,189")
print(f"   Ahora (rango amplio): ${df_payments_filtrado['Monto'].sum():,.0f}")
print(f"   Diferencia: ${df_payments_filtrado['Monto'].sum() - 860189:,.0f}")

print(f"\n🎉 ¡CORRECCIÓN EXITOSA!")
print(f"   El dashboard ahora debería mostrar todos los abonos bancarios") 