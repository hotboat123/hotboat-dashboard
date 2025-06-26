import pandas as pd
from datetime import datetime

print("=== VERIFICACIÓN DE LÓGICA DEL DASHBOARD DE RESERVAS ===")

# Cargar datos como lo hace el dashboard
df_reservas = pd.read_csv("archivos_output/reservas_HotBoat.csv")
df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")

# Convertir fechas como lo hace el dashboard
df_reservas["fecha_trip"] = pd.to_datetime(df_reservas["fecha_trip"])
df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"], dayfirst=True, errors='coerce')
df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"], dayfirst=True, errors='coerce')

print(f"📊 RESERVAS:")
print(f"   Total reservas: {len(df_reservas)}")
print(f"   Total PAID AMOUNT: ${df_reservas['PAID AMOUNT'].sum():,.0f}")
print(f"   Reservas con PAID AMOUNT 0: {len(df_reservas[df_reservas['PAID AMOUNT'] == 0])}")

print(f"\n💰 PAGOS (ABONOS):")
print(f"   Total abonos: {len(df_payments)}")
print(f"   Total monto abonos: ${df_payments['Monto'].sum():,.0f}")

print(f"\n💸 GASTOS:")
print(f"   Total gastos: {len(df_expenses)}")
print(f"   Total monto gastos: ${df_expenses['Monto'].sum():,.0f}")

# Simular el filtrado del dashboard (sin filtros de fecha)
print(f"\n🎯 LÓGICA DEL DASHBOARD:")
print(f"   El dashboard usa df_payments['Monto'].sum() para ingresos")
print(f"   Esto debería ser: ${df_payments['Monto'].sum():,.0f}")

# Verificar si hay algún problema con los datos
print(f"\n🔍 VERIFICACIÓN DE DATOS:")
print(f"   ¿Hay valores NaN en Monto?: {df_payments['Monto'].isna().sum()}")
print(f"   ¿Hay valores negativos?: {len(df_payments[df_payments['Monto'] < 0])}")
print(f"   Rango de fechas abonos: {df_payments['Fecha'].min()} a {df_payments['Fecha'].max()}")
print(f"   Rango de fechas reservas: {df_reservas['fecha_trip'].min()} a {df_reservas['fecha_trip'].max()}")

# Verificar si el dashboard está usando un filtro de fecha por defecto
fecha_min = df_reservas['fecha_trip'].min()
fecha_max = df_reservas['fecha_trip'].max()

print(f"\n📅 FILTRADO POR FECHAS DE RESERVAS:")
df_payments_filtrado = df_payments[(df_payments['Fecha'] >= fecha_min) & (df_payments['Fecha'] <= fecha_max)]
print(f"   Abonos en rango de fechas de reservas: {len(df_payments_filtrado)}")
print(f"   Monto abonos filtrado: ${df_payments_filtrado['Monto'].sum():,.0f}")

print(f"\n❓ POSIBLE PROBLEMA:")
print(f"   Si el dashboard muestra ~$860K, podría estar usando un filtro de fecha")
print(f"   o podría estar usando solo los pagos de reservas en lugar de todos los abonos") 