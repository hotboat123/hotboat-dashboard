#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importaciones
print("🚤 INICIANDO DASHBOARD DE RESERVAS HOTBOAT...")
print("=" * 60)

# Importar funciones desde dashboards.py
from dashboards import crear_app_reservas, cargar_datos

if __name__ == '__main__':
    print("📊 Cargando datos...")
    
    # Cargar todos los datos necesarios
    datos = cargar_datos()
    
    # Mostrar resumen de datos cargados
    print(f"✅ Reservas cargadas: {len(datos['reservas'])} filas")
    print(f"✅ Pagos cargados: {len(datos['pagos'])} filas")
    print(f"✅ Gastos cargados: {len(datos['gastos'])} filas")
    
    # Crear y ejecutar app
    app = crear_app_reservas(datos)
    
    print("✅ Dashboard de reservas creado exitosamente")
    print("🌐 URL: http://localhost:8050")
    print("🔄 Para detener: Ctrl+C")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=8050) 