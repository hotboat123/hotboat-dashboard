#!/usr/bin/env python3
"""
🚤 HOTBOAT - SISTEMA DE DASHBOARDS PRINCIPAL
============================================

Este es el archivo principal para ejecutar todos los dashboards de HotBoat.
Proporciona una interfaz unificada para acceder a los diferentes análisis.

Dashboards disponibles:
- Utilidad Operativa (Puerto 8055)
- Reservas (Puerto 8050) 
- Marketing (Puerto 8056)

Uso:
    python hotboat_dashboards.py [utilidad|reservas|marketing|todos]

Autor: Sistema HotBoat
Versión: 1.0
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Configuración de puertos
PUERTOS = {
    'utilidad': 8055,
    'reservas': 8050,
    'marketing': 8056
}

def mostrar_menu():
    """Muestra el menú principal de dashboards"""
    print("\n" + "="*60)
    print("🚤 HOTBOAT - SISTEMA DE DASHBOARDS")
    print("="*60)
    print("1. 📊 Dashboard de Utilidad Operativa (Puerto 8055)")
    print("2. 🛥️  Dashboard de Reservas (Puerto 8050)")
    print("3. 📱 Dashboard de Marketing (Puerto 8056)")
    print("4. 🌐 Ejecutar Todos los Dashboards")
    print("5. ❌ Salir")
    print("="*60)

def ejecutar_dashboard(tipo):
    """Ejecuta un dashboard específico"""
    dashboards_dir = Path("dashboards")
    
    # Mapeo de archivos
    archivos = {
        'utilidad': 'utilidad_optimizado.py',
        'reservas': 'reservas_optimizado.py', 
        'marketing': 'marketing_optimizado.py'
    }
    
    if tipo not in archivos:
        print(f"❌ Error: Dashboard '{tipo}' no válido")
        return False
    
    archivo = dashboards_dir / archivos[tipo]
    
    if not archivo.exists():
        print(f"❌ Error: No se encontró {archivo}")
        return False
    
    try:
        print(f"\n🚀 Iniciando dashboard de {tipo.title()}...")
        print(f"📍 URL: http://localhost:{PUERTOS[tipo]}")
        print(f"🔄 Para detener: Ctrl+C")
        print("-" * 50)
        
        # Ejecutar el dashboard
        subprocess.run([sys.executable, str(archivo)], check=True)
        
    except KeyboardInterrupt:
        print(f"\n✅ Dashboard de {tipo.title()} detenido por el usuario")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando dashboard de {tipo.title()}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def ejecutar_todos():
    """Ejecuta todos los dashboards en paralelo"""
    print("\n🌐 Iniciando todos los dashboards...")
    print("📍 URLs disponibles:")
    for tipo, puerto in PUERTOS.items():
        print(f"   - {tipo.title()}: http://localhost:{puerto}")
    
    print("\n🔄 Para detener todos: Ctrl+C")
    print("=" * 50)
    
    procesos = []
    dashboards_dir = Path("dashboards")
    
    try:
        # Iniciar cada dashboard en paralelo
        for tipo in ['utilidad', 'reservas', 'marketing']:
            archivo = dashboards_dir / f"{tipo}_optimizado.py"
            if archivo.exists():
                proceso = subprocess.Popen([sys.executable, str(archivo)])
                procesos.append((proceso, tipo))
                print(f"✅ {tipo.title()} iniciado (PID: {proceso.pid})")
                time.sleep(2)  # Pequeña pausa entre inicios
        
        print("\n🎉 Todos los dashboards están ejecutándose!")
        print("👆 Presiona Ctrl+C para detener todos")
        
        # Esperar a que el usuario presione Ctrl+C
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo todos los dashboards...")
        
        # Terminar todos los procesos
        for proceso, tipo in procesos:
            try:
                proceso.terminate()
                proceso.wait(timeout=5)
                print(f"✅ {tipo.title()} detenido")
            except subprocess.TimeoutExpired:
                proceso.kill()
                print(f"🔪 {tipo.title()} forzado a detenerse")
            except Exception as e:
                print(f"⚠️ Error deteniendo {tipo.title()}: {e}")
        
        print("\n✅ Todos los dashboards han sido detenidos")

def main():
    """Función principal"""
    # Verificar que estamos en el directorio correcto
    if not Path("dashboards").exists():
        print("❌ Error: No se encontró la carpeta 'dashboards'")
        print("💡 Asegúrate de ejecutar este script desde la raíz del proyecto HotBoat")
        return
    
    # Si se pasa un argumento de línea de comandos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando in ['utilidad', 'reservas', 'marketing']:
            ejecutar_dashboard(comando)
        elif comando in ['todos', 'all']:
            ejecutar_todos()
        else:
            print(f"❌ Comando no válido: {comando}")
            print("💡 Uso: python hotboat_dashboards.py [utilidad|reservas|marketing|todos]")
        return
    
    # Interfaz interactiva
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🎯 Selecciona una opción (1-5): ").strip()
            
            if opcion == '1':
                ejecutar_dashboard('utilidad')
            elif opcion == '2':
                ejecutar_dashboard('reservas')
            elif opcion == '3':
                ejecutar_dashboard('marketing')
            elif opcion == '4':
                ejecutar_todos()
            elif opcion == '5':
                print("\n👋 ¡Hasta luego! Navegación segura con HotBoat 🚤")
                break
            else:
                print("❌ Opción no válida. Por favor selecciona 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego! Navegación segura con HotBoat 🚤")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 