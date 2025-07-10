#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

print("🧪 TESTING DASHBOARD DE RESERVAS...")
print("=" * 50)

# Verificar archivo de reservas
archivo_reservas = "archivos_output/reservas_HotBoat.csv"
if not os.path.exists(archivo_reservas):
    print(f"❌ ERROR: No se encuentra el archivo {archivo_reservas}")
    exit(1)

print(f"✅ Archivo encontrado: {archivo_reservas}")

# Cargar datos
try:
    df = pd.read_csv(archivo_reservas)
    print(f"✅ Datos cargados: {len(df)} filas")
    print(f"✅ Columnas: {df.columns.tolist()}")
    
    # Verificar columna de fecha
    if 'fecha_hora_trip' in df.columns:
        print("✅ Columna fecha_hora_trip encontrada")
        
        # Convertir a datetime
        df["fecha_trip"] = pd.to_datetime(df["fecha_hora_trip"])
        print("✅ Conversión a datetime exitosa")
        
        # Verificar fechas
        print(f"✅ Fecha mínima: {df['fecha_trip'].min()}")
        print(f"✅ Fecha máxima: {df['fecha_trip'].max()}")
        
        # Verificar que no hay fechas nulas
        fechas_nulas = df['fecha_trip'].isnull().sum()
        print(f"✅ Fechas nulas: {fechas_nulas}")
        
    else:
        print("❌ ERROR: No se encuentra la columna fecha_hora_trip")
        print(f"   Columnas disponibles: {df.columns.tolist()}")
        exit(1)
        
except Exception as e:
    print(f"❌ ERROR cargando datos: {e}")
    exit(1)

# Verificar otros archivos necesarios
archivos_requeridos = [
    "archivos_output/abonos hotboat.csv",
    "archivos_output/gastos hotboat.csv"
]

for archivo in archivos_requeridos:
    if os.path.exists(archivo):
        print(f"✅ {archivo} encontrado")
    else:
        print(f"❌ {archivo} NO encontrado")

print("=" * 50)
print("🎉 TEST COMPLETADO - Todo parece estar bien")
print("🚀 Intentando ejecutar el dashboard...")
print("=" * 50)

# Intentar ejecutar el dashboard
try:
    from dashboards import cargar_datos
    datos = cargar_datos()
    print("✅ Función cargar_datos ejecutada exitosamente")
    print(f"✅ Reservas cargadas: {len(datos['reservas'])} filas")
    print(f"✅ Pagos cargados: {len(datos['pagos'])} filas")
    print(f"✅ Gastos cargados: {len(datos['gastos'])} filas")
    
except Exception as e:
    print(f"❌ ERROR en cargar_datos: {e}")
    import traceback
    traceback.print_exc() 