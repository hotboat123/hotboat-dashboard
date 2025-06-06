#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOTBOAT - Dashboard de Marketing Optimizado
===========================================

Archivo de entrada principal para el dashboard de marketing.
Utiliza el sistema consolidado de módulos core/.

Uso: python marketing_optimizado.py

Autores: Sistema HotBoat
Fecha: Junio 2025
"""

import sys
import os

# Agregar core al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from dashboards_main import inicializar_dashboard

if __name__ == "__main__":
    print("📱 INICIANDO DASHBOARD DE MARKETING HOTBOAT OPTIMIZADO...")
    print("=" * 60)
    print("🔧 Versión: Optimizada y consolidada")
    print("📂 Usando: Sistema de módulos core/")
    print("=" * 60)
    
    try:
        app, puerto = inicializar_dashboard('marketing')
        
        print(f"🌐 Dashboard disponible en: http://localhost:{puerto}")
        print("💡 Para detener: Ctrl+C")
        print("=" * 60)
        
        app.run(debug=False, host='0.0.0.0', port=puerto)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando dashboard: {e}")
        sys.exit(1) 