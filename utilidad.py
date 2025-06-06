#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importaciones
print("🚤 INICIANDO DASHBOARD DE UTILIDAD OPERATIVA HOTBOAT...")
print("=" * 60)

# Importar funciones desde dashboards.py
from dashboards import crear_app_utilidad, cargar_datos

if __name__ == '__main__':
    print("📊 Cargando datos...")
    
    # Cargar todos los datos necesarios
    datos = cargar_datos()
    
    # Mostrar resumen de datos cargados
    print(f"✅ Reservas cargadas: {len(datos['reservas'])} filas")
    print(f"✅ Ingresos cargados: {len(datos['ingresos'])} filas")
    print(f"✅ Costos operativos cargados: {len(datos['costos_operativos'])} filas")
    print(f"✅ Gastos marketing cargados: {len(datos['gastos_marketing'])} filas")
    print(f"✅ Costos fijos cargados: {len(datos['costos_fijos'])} filas")
    
    # Crear y ejecutar app
    app = crear_app_utilidad(datos)
    
    print("✅ Dashboard de utilidad operativa creado exitosamente")
    print("🌐 URL: http://localhost:8055")
    print("🔄 Para detener: Ctrl+C")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=8055) 