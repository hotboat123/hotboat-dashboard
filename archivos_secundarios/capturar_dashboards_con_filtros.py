#!/usr/bin/env python3
"""
Script para capturar screenshots de dashboards con filtros de fecha
Organiza las capturas por carpetas de fecha (YYYY-MM-DD)
"""

import os
import time
import subprocess
import threading
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import json

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

# Configuración de filtros de fecha
FILTROS_FECHA = {
    'mes': {
        'name': 'Último Mes',
        'days': 30
    },
    'semana': {
        'name': 'Última Semana', 
        'days': 7
    },
    'dia': {
        'name': 'Hoy',
        'days': 1
    }
}

def iniciar_dashboards():
    """Inicia todos los dashboards en segundo plano"""
    print("🚀 Iniciando dashboards...")
    
    procesos = {}
    for nombre, config in DASHBOARDS.items():
        try:
            # Extraer puerto de la URL
            puerto = config['url'].split(':')[-1]
            
            # Determinar archivo del dashboard
            if nombre == 'reservas':
                archivo = 'dashboard_reservas_simple.py'
            elif nombre == 'utilidad':
                archivo = 'dashboard_utilidad_simple.py'
            elif nombre == 'marketing':
                archivo = 'dashboard_marketing_simple.py'
            else:
                continue
                
            print(f"  📊 Iniciando {config['name']} en puerto {puerto}...")
            
            # Iniciar proceso
            proceso = subprocess.Popen(
                ['python', archivo],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            procesos[nombre] = proceso
            
            # Esperar un poco entre cada dashboard
            time.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Error iniciando {config['name']}: {e}")
    
    return procesos

def esperar_dashboards_listos():
    """Espera a que todos los dashboards estén listos"""
    print("⏳ Esperando que los dashboards estén listos...")
    time.sleep(15)  # Tiempo base para que se inicien

def aplicar_filtro_fecha(page, filtro):
    """Aplica filtro de fecha al dashboard"""
    try:
        # Buscar y hacer clic en el selector de fecha
        selector_fecha = 'input[placeholder*="fecha"], input[placeholder*="date"], .DatePickerInput'
        page.wait_for_selector(selector_fecha, timeout=5000)
        
        # Calcular fechas
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=filtro['days'])
        
        # Formatear fechas
        fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
        fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
        
        # Aplicar filtro
        page.fill(selector_fecha, f"{fecha_inicio_str} - {fecha_fin_str}")
        page.press(selector_fecha, 'Enter')
        
        # Esperar a que se actualice
        time.sleep(3)
        
        print(f"    ✅ Filtro aplicado: {filtro['name']}")
        
    except Exception as e:
        print(f"    ⚠️ No se pudo aplicar filtro de fecha: {e}")

def capturar_dashboard(playwright, nombre, config, filtro, carpeta_fecha):
    """Captura screenshot de un dashboard específico"""
    try:
        print(f"  📸 Capturando {config['name']} con filtro {filtro['name']}...")
        
        # Crear carpeta si no existe
        carpeta_dashboard = os.path.join(carpeta_fecha, nombre)
        os.makedirs(carpeta_dashboard, exist_ok=True)
        
        # Nombre del archivo
        nombre_archivo = f"{nombre}_{filtro['name'].lower().replace(' ', '_')}.png"
        ruta_completa = os.path.join(carpeta_dashboard, nombre_archivo)
        
        # Iniciar navegador
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navegar al dashboard
        page.goto(config['url'], wait_until='networkidle')
        
        # Esperar a que cargue
        time.sleep(5)
        
        # Aplicar filtro de fecha si está disponible
        aplicar_filtro_fecha(page, filtro)
        
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
    print("🎯 INICIANDO CAPTURA DE DASHBOARDS CON FILTROS")
    print("=" * 60)
    
    # Crear carpeta principal con fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    carpeta_principal = f"screenshots_{fecha_actual}"
    os.makedirs(carpeta_principal, exist_ok=True)
    
    print(f"📁 Carpeta de capturas: {carpeta_principal}")
    
    # Iniciar dashboards
    procesos = iniciar_dashboards()
    
    if not procesos:
        print("❌ No se pudieron iniciar los dashboards")
        return
    
    # Esperar a que estén listos
    esperar_dashboards_listos()
    
    # Capturar con Playwright
    with sync_playwright() as playwright:
        for nombre, config in DASHBOARDS.items():
            if nombre not in procesos:
                continue
                
            print(f"\n📊 Procesando {config['name']}...")
            
            for filtro_nombre, filtro in FILTROS_FECHA.items():
                # Crear carpeta para el filtro
                carpeta_filtro = os.path.join(carpeta_principal, filtro_nombre)
                os.makedirs(carpeta_filtro, exist_ok=True)
                
                # Capturar dashboard
                capturar_dashboard(playwright, nombre, config, filtro, carpeta_filtro)
                
                # Pausa entre capturas
                time.sleep(2)
    
    # Terminar procesos
    print("\n🛑 Terminando procesos de dashboards...")
    for nombre, proceso in procesos.items():
        try:
            proceso.terminate()
            print(f"  ✅ {DASHBOARDS[nombre]['name']} terminado")
        except:
            pass
    
    print(f"\n🎉 CAPTURA COMPLETADA!")
    print(f"📁 Revisa las capturas en: {carpeta_principal}")
    
    # Mostrar estructura de archivos creados
    print("\n📋 Estructura de archivos creados:")
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