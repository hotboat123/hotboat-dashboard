#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚤 EJECUTOR MÚLTIPLE DE DASHBOARDS HOTBOAT
==========================================

Este script ejecuta simultáneamente los 5 dashboards de HotBoat:
- Dashboard de Reservas (Puerto 8050)
- Dashboard de Utilidad Operativa (Puerto 8055)  
- Dashboard de Marketing (Puerto 8056)
- Dashboard de Gastos de Marketing (Puerto 8057)
- Dashboard de Google Ads (Puerto 8058)

Uso:
    python ejecutar_todos_dashboards.py

Para detener:
    Ctrl+C (detendrá todos los procesos)
"""

import multiprocessing
import subprocess
import time
import sys
import os
from typing import List

def print_banner():
    """Imprime el banner de inicio"""
    print("🚤" * 20)
    print("🚤 HOTBOAT DASHBOARDS - EJECUTOR MÚLTIPLE")
    print("🚤" * 20)
    print()
    print("📊 Iniciando todos los dashboards simultáneamente...")
    print("=" * 60)

def ejecutar_dashboard(script_name: str, puerto: int, nombre: str):
    """
    Ejecuta un dashboard individual en un proceso separado
    
    Args:
        script_name: Nombre del archivo Python a ejecutar
        puerto: Puerto en el que se ejecutará
        nombre: Nombre descriptivo del dashboard
    """
    try:
        print(f"🚀 Iniciando {nombre} en puerto {puerto}...")
        # Ejecutar el script Python
        subprocess.run([sys.executable, script_name], check=True)
    except KeyboardInterrupt:
        print(f"🛑 Deteniendo {nombre}...")
    except Exception as e:
        print(f"❌ Error en {nombre}: {e}")

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_requeridos = ['reservas.py', 'utilidad.py', 'marketing.py', 'dashboard_gastos_marketing.py', 'dashboard_google_ads.py']
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print("❌ ERROR: Los siguientes archivos no existen:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        print("\n💡 Asegúrate de estar en el directorio correcto del proyecto")
        return False
    
    return True

def main():
    """Función principal que ejecuta todos los dashboards"""
    print_banner()
    
    # Verificar archivos
    if not verificar_archivos():
        sys.exit(1)
    
    # Configuración de dashboards
    dashboards = [
        {
            'script': 'reservas.py',
            'puerto': 8050,
            'nombre': 'Dashboard de Reservas',
            'url': 'http://localhost:8050'
        },
        {
            'script': 'utilidad.py', 
            'puerto': 8055,
            'nombre': 'Dashboard de Utilidad Operativa',
            'url': 'http://localhost:8055'
        },
        {
            'script': 'marketing.py',
            'puerto': 8056,
            'nombre': 'Dashboard de Marketing',
            'url': 'http://localhost:8056'
        },
        {
            'script': 'dashboard_gastos_marketing.py',
            'puerto': 8057,
            'nombre': 'Dashboard de Gastos de Marketing',
            'url': 'http://localhost:8057'
        },
        {
            'script': 'dashboard_google_ads.py',
            'puerto': 8058,
            'nombre': 'Dashboard de Google Ads',
            'url': 'http://localhost:8058'
        }
    ]
    
    # Crear procesos
    procesos = []
    
    try:
        # Iniciar cada dashboard en un proceso separado
        for dashboard in dashboards:
            proceso = multiprocessing.Process(
                target=ejecutar_dashboard,
                args=(dashboard['script'], dashboard['puerto'], dashboard['nombre'])
            )
            proceso.start()
            procesos.append(proceso)
            print(f"✅ {dashboard['nombre']} iniciado")
        
        print("=" * 60)
        print("🎉 TODOS LOS DASHBOARDS INICIADOS EXITOSAMENTE")
        print("=" * 60)
        print()
        print("📱 URLs de acceso:")
        for dashboard in dashboards:
            print(f"   🔗 {dashboard['nombre']}: {dashboard['url']}")
        print()
        print("🔄 Para detener todos los dashboards: Ctrl+C")
        print("⚡ Para navegar entre dashboards, usa los enlaces en la interfaz web")
        print("=" * 60)
        
        # Esperar a que terminen todos los procesos
        for proceso in procesos:
            proceso.join()
            
    except KeyboardInterrupt:
        print("\n🛑 DETENIENDO TODOS LOS DASHBOARDS...")
        print("=" * 60)
        
        # Terminar todos los procesos
        for i, proceso in enumerate(procesos):
            if proceso.is_alive():
                print(f"🔄 Deteniendo {dashboards[i]['nombre']}...")
                proceso.terminate()
                proceso.join(timeout=5)
                
                # Si no se detuvo amablemente, forzar
                if proceso.is_alive():
                    print(f"⚡ Forzando detención de {dashboards[i]['nombre']}...")
                    proceso.kill()
        
        print("✅ Todos los dashboards han sido detenidos")
        print("👋 ¡Hasta luego!")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        # Limpiar procesos en caso de error
        for proceso in procesos:
            if proceso.is_alive():
                proceso.terminate()

if __name__ == '__main__':
    # Configurar multiprocessing en Windows
    if sys.platform.startswith('win'):
        multiprocessing.set_start_method('spawn', force=True)
    
    main() 