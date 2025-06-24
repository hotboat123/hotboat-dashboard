#!/usr/bin/env python3
"""
Script básico para capturar screenshots de dashboards manualmente
Requiere que los dashboards ya estén ejecutándose
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configuración de dashboards
DASHBOARDS = {
    'reservas': {
        'url': 'http://localhost:8050',
        'name': 'Dashboard Reservas'
    },
    'utilidad': {
        'url': 'http://localhost:8055', 
        'name': 'Dashboard Utilidad'
    },
    'marketing': {
        'url': 'http://localhost:8056',
        'name': 'Dashboard Marketing'
    }
}

def capturar_dashboard(playwright, nombre, config, carpeta_fecha):
    """Captura screenshot de un dashboard específico"""
    try:
        print(f"  📸 Capturando {config['name']}...")
        
        # Crear carpeta si no existe
        carpeta_dashboard = os.path.join(carpeta_fecha, nombre)
        os.makedirs(carpeta_dashboard, exist_ok=True)
        
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"{nombre}_{timestamp}.png"
        ruta_completa = os.path.join(carpeta_dashboard, nombre_archivo)
        
        # Iniciar navegador
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navegar al dashboard
        page.goto(config['url'], wait_until='networkidle')
        
        # Esperar a que cargue
        time.sleep(5)
        
        # Capturar screenshot
        page.screenshot(path=ruta_completa, full_page=True)
        
        # Cerrar navegador
        browser.close()
        
        print(f"    ✅ Captura guardada: {ruta_completa}")
        return True
        
    except Exception as e:
        print(f"    ❌ Error capturando {config['name']}: {e}")
        return False

def capturar_todos_dashboards():
    """Función principal para capturar todos los dashboards"""
    print("🎯 CAPTURA MANUAL DE DASHBOARDS")
    print("=" * 40)
    print("⚠️  Asegúrate de que los dashboards estén ejecutándose")
    print("   - Reservas: http://localhost:8050")
    print("   - Utilidad: http://localhost:8055")
    print("   - Marketing: http://localhost:8056")
    print()
    
    # Crear carpeta principal con fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    carpeta_principal = f"screenshots_manual_{fecha_actual}"
    os.makedirs(carpeta_principal, exist_ok=True)
    
    print(f"📁 Carpeta de capturas: {carpeta_principal}")
    
    # Capturar con Playwright
    with sync_playwright() as playwright:
        for nombre, config in DASHBOARDS.items():
            print(f"\n📊 Procesando {config['name']}...")
            
            # Capturar dashboard
            capturar_dashboard(playwright, nombre, config, carpeta_principal)
            
            # Pausa entre capturas
            time.sleep(2)
    
    print(f"\n🎉 CAPTURA COMPLETADA!")
    print(f"📁 Revisa las capturas en: {carpeta_principal}")
    
    # Mostrar estructura de archivos creados
    print("\n📋 Archivos creados:")
    for root, dirs, files in os.walk(carpeta_principal):
        level = root.replace(carpeta_principal, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

if __name__ == "__main__":
    try:
        capturar_todos_dashboards()
    except KeyboardInterrupt:
        print("\n⚠️ Captura interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}") 