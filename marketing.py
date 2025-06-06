#!/usr/bin/env python3
"""
Dashboard de Marketing - HotBoat
Ejecuta el dashboard de análisis de marketing y utilidad operativa
"""

from dashboard_utilidad import crear_app_utilidad, cargar_datos

if __name__ == '__main__':
    print("\n📊 INICIANDO DASHBOARD DE MARKETING HOTBOAT...")
    print("=" * 60)
    print("📈 Cargando datos de marketing...")
    
    # Cargar datos
    datos = cargar_datos()
    
    # Verificar datos cargados
    print(f"✅ Gastos marketing cargados: {len(datos['gastos_marketing'])} filas")
    print(f"✅ Ingresos cargados: {len(datos['ingresos'])} filas")
    print(f"✅ Costos operativos cargados: {len(datos['costos_operativos'])} filas")
    print(f"✅ Costos fijos cargados: {len(datos['costos_fijos'])} filas")
    
    # Crear y ejecutar app
    app = crear_app_utilidad(datos)
    
    print("✅ Dashboard de marketing creado exitosamente")
    print("🌐 URL: http://localhost:8056")
    print("🔄 Para detener: Ctrl+C")
    print("=" * 60)
    
    # Ejecutar dashboard
    app.run(debug=False, host='0.0.0.0', port=8056) 