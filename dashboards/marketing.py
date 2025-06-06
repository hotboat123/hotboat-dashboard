#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importaciones
print("📊 INICIANDO DASHBOARD DE MARKETING HOTBOAT...")
print("=" * 60)

# Ejecutar dashboard de marketing específico
from dashboard_marketing_simple import app

if __name__ == '__main__':
    print("📈 Cargando datos de marketing...")
    print("📊 Dashboard de marketing con métricas CPC, CTR, región")
    print("🎯 Análisis de audiencias y tipos de anuncios")
    print("💹 Hook rates y conversiones")
    print("✅ Dashboard de marketing creado exitosamente")
    print("🌐 URL: http://localhost:8056")
    print("🔄 Para detener: Ctrl+C")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=8056) 