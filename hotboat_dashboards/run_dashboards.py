#!/usr/bin/env python3
"""
🚤 HOTBOAT - LAUNCHER DE DASHBOARDS OPTIMIZADO
==============================================

Sistema principal optimizado para ejecutar dashboards HotBoat.
Mantiene la funcionalidad exacta de la versión original.

Uso:
    python run_dashboards.py [reservas|utilidad|marketing|todos]

Autor: Sistema HotBoat Optimizado
Versión: 2.0
"""

import sys
import os
import subprocess
import threading
import time
from pathlib import Path

def mostrar_banner():
    """Muestra el banner de inicio"""
    print("\n" + "="*60)
    print("🚤 HOTBOAT - DASHBOARD LAUNCHER OPTIMIZADO")
    print("="*60)
    print("🔧 Versión: 2.0 - Optimizada y funcional")
    print("📂 Estructura: Modular y ordenada")
    print("🎨 Interfaz: Original (negra con selector arriba)")
    print("="*60)

def verificar_dependencias():
    """Verifica que los archivos necesarios existan"""
    archivos_necesarios = [
        'dashboards.py',
        'utilidad.py', 
        'marketing.py',
        'funciones/funciones.py',
        'funciones/funciones_reservas.py'
    ]
    
    faltantes = []
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            faltantes.append(archivo)
    
    if faltantes:
        print("⚠️ Archivos faltantes:")
        for archivo in faltantes:
            print(f"   - {archivo}")
        return False
    
    return True

def ejecutar_dashboard(tipo):
    """Ejecuta un dashboard específico"""
    comandos = {
        'reservas': 'python dashboards.py',
        'utilidad': 'python utilidad.py', 
        'marketing': 'python marketing.py'
    }
    
    puertos = {
        'reservas': 8050,
        'utilidad': 8055,
        'marketing': 8056
    }
    
    if tipo not in comandos:
        print(f"❌ Dashboard '{tipo}' no válido")
        return False
    
    try:
        print(f"\n🚀 Iniciando Dashboard de {tipo.title()}...")
        print(f"🌐 Puerto: {puertos[tipo]}")
        print(f"📋 Comando: {comandos[tipo]}")
        print("-" * 40)
        
        # Ejecutar el comando en segundo plano si es parte de 'todos'
        if len(sys.argv) > 1 and sys.argv[1] == 'todos':
            subprocess.Popen([sys.executable] + comandos[tipo].split()[1:], 
                           cwd=os.getcwd())
            time.sleep(2)  # Dar tiempo para que se inicie
            print(f"✅ Dashboard de {tipo} iniciado en puerto {puertos[tipo]}")
            return True
        else:
            # Ejecutar directamente si es individual
            subprocess.run([sys.executable] + comandos[tipo].split()[1:])
            return True
            
    except Exception as e:
        print(f"❌ Error ejecutando dashboard de {tipo}: {e}")
        return False

def ejecutar_todos():
    """Ejecuta todos los dashboards simultáneamente"""
    print("\n🌐 Iniciando TODOS los dashboards...")
    print("⏳ Los dashboards se ejecutarán simultáneamente")
    print("🔗 Cada dashboard en su puerto específico")
    print("=" * 50)
    
    dashboards = ['reservas', 'utilidad', 'marketing']
    resultados = []
    
    # Ejecutar todos en paralelo
    for dashboard in dashboards:
        exito = ejecutar_dashboard(dashboard)
        resultados.append((dashboard, exito))
    
    # Esperar un momento para que se inicien
    print("\n⏳ Esperando que se inicien todos los dashboards...")
    time.sleep(5)
    
    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE DASHBOARDS ACTIVOS")
    print("="*60)
    
    exitosos = 0
    for dashboard, exito in resultados:
        if exito:
            puerto = {'reservas': 8050, 'utilidad': 8055, 'marketing': 8056}[dashboard]
            print(f"✅ {dashboard.title():12} → http://localhost:{puerto}")
            exitosos += 1
        else:
            print(f"❌ {dashboard.title():12} → FALLÓ")
    
    print("-" * 60)
    print(f"📈 Total activos: {exitosos}/{len(dashboards)} dashboards")
    
    if exitosos == len(dashboards):
        print("\n🎉 ¡Todos los dashboards están funcionando!")
        print("🔗 URLs de acceso:")
        print("   • Reservas:  http://localhost:8050")
        print("   • Utilidad:  http://localhost:8055")
        print("   • Marketing: http://localhost:8056")
        print("\n💡 Para detener: Ctrl+C en cada terminal")
    else:
        print("⚠️ Algunos dashboards fallaron. Verifica los errores arriba.")

def mostrar_ayuda():
    """Muestra la ayuda de uso"""
    print("\n📖 USO DEL LAUNCHER DE DASHBOARDS")
    print("="*50)
    print("Comandos disponibles:")
    print("  python run_dashboards.py reservas   → Dashboard de Reservas (puerto 8050)")
    print("  python run_dashboards.py utilidad   → Dashboard de Utilidad (puerto 8055)")
    print("  python run_dashboards.py marketing  → Dashboard de Marketing (puerto 8056)")
    print("  python run_dashboards.py todos      → Todos los dashboards")
    print("  python run_dashboards.py help       → Mostrar esta ayuda")
    print("\n🌐 Características:")
    print("  • Interfaz original (negra con selector arriba)")
    print("  • Código optimizado y modular")
    print("  • Funcionalidad exacta de la versión original")
    print("  • Dashboards independientes en puertos específicos")

def main():
    """Función principal"""
    mostrar_banner()
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("\n❌ No se pueden ejecutar los dashboards debido a archivos faltantes")
        return
    
    # Obtener comando
    if len(sys.argv) < 2:
        print("\n⚠️ No se especificó qué dashboard ejecutar")
        mostrar_ayuda()
        return
    
    comando = sys.argv[1].lower()
    
    if comando in ['help', 'ayuda', '-h', '--help']:
        mostrar_ayuda()
    elif comando in ['reservas', 'utilidad', 'marketing']:
        ejecutar_dashboard(comando)
    elif comando in ['todos', 'all']:
        ejecutar_todos()
    else:
        print(f"❌ Comando no válido: {comando}")
        mostrar_ayuda()

if __name__ == "__main__":
    main() 