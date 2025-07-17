#!/usr/bin/env python3
"""
Script principal para capturar screenshots de dashboards
Permite elegir entre diferentes tipos de captura
"""

import os
import sys
import subprocess

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("📸 CAPTURADOR DE DASHBOARDS")
    print("=" * 40)
    print("Elige el tipo de captura:")
    print()
    print("1. 📋 Captura Simple")
    print("   - Inicia dashboards automáticamente")
    print("   - Captura una imagen de cada dashboard")
    print("   - Sin filtros de fecha")
    print()
    print("2. 📅 Captura con Filtros")
    print("   - Inicia dashboards automáticamente")
    print("   - Captura con filtros: Día, Semana, Mes")
    print("   - Organiza por carpetas de filtro")
    print()
    print("3. 🤖 Captura Automática")
    print("   - Usa ejecutar_todos_dashboards.py")
    print("   - Captura una imagen de cada dashboard")
    print("   - Proceso más robusto")
    print()
    print("4. ✋ Captura Manual")
    print("   - Requiere que los dashboards estén ejecutándose")
    print("   - Captura una imagen de cada dashboard")
    print("   - Para uso manual")
    print()
    print("5. ❌ Salir")
    print()

def ejecutar_captura(opcion):
    """Ejecuta la captura según la opción elegida"""
    scripts = {
        '1': 'capturar_dashboards_simple.py',
        '2': 'capturar_dashboards_con_filtros.py',
        '3': 'capturar_dashboards_automatico.py',
        '4': 'capturar_dashboards_basico.py'
    }
    
    if opcion in scripts:
        script = scripts[opcion]
        print(f"🚀 Ejecutando: {script}")
        print("=" * 50)
        
        try:
            # Ejecutar el script
            resultado = subprocess.run(['python', script], capture_output=False)
            
            if resultado.returncode == 0:
                print("\n✅ Captura completada exitosamente")
            else:
                print("\n❌ Error en la captura")
                
        except Exception as e:
            print(f"\n❌ Error ejecutando {script}: {e}")
    else:
        print("❌ Opción no válida")

def verificar_playwright():
    """Verifica si Playwright está instalado"""
    try:
        import playwright
        return True
    except ImportError:
        print("❌ Playwright no está instalado")
        print("💡 Instala con: pip install playwright")
        print("💡 Y luego: python -m playwright install chromium")
        return False

def main():
    """Función principal"""
    print("🎯 BIENVENIDO AL CAPTURADOR DE DASHBOARDS")
    print("=" * 50)
    
    # Verificar Playwright
    if not verificar_playwright():
        return
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("Elige una opción (1-5): ").strip()
            
            if opcion == '5':
                print("👋 ¡Hasta luego!")
                break
            elif opcion in ['1', '2', '3', '4']:
                ejecutar_captura(opcion)
                
                # Preguntar si quiere continuar
                continuar = input("\n¿Quieres hacer otra captura? (s/n): ").strip().lower()
                if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
                    print("👋 ¡Hasta luego!")
                    break
            else:
                print("❌ Opción no válida. Intenta de nuevo.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 