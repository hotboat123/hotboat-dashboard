#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚤 ACTUALIZAR TODO - HOTBOAT
============================

Este script ejecuta todos los procesos de HotBoat en el orden correcto:
1. Procesar gastos y costos
2. Procesar reservas
3. Calcular utilidad
4. Ejecutar dashboards

Uso:
    python actualizar_todo.py
"""

import subprocess
import sys
import os
import time

# Configurar UTF-8 para que los emojis funcionen siempre
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Para versiones de Python < 3.7
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

def ejecutar_comando(comando, descripcion):
    """
    Ejecuta un comando y maneja errores
    
    Args:
        comando (str): Comando a ejecutar
        descripcion (str): Descripción del proceso
        
    Returns:
        bool: True si se ejecutó correctamente, False en caso contrario
    """
    print("=" * 60)
    print(f"🔄 {descripcion}")
    print("=" * 60)
    print(f"📋 Ejecutando: {comando}")
    print()
    
    try:
        # Ejecutar el comando
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        
        # Mostrar output
        if resultado.stdout:
            print("✅ Output:")
            print(resultado.stdout)
        
        print(f"✅ {descripcion} completado exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {descripcion}:")
        print(f"   Comando: {comando}")
        print(f"   Código de error: {e.returncode}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en {descripcion}: {str(e)}")
        return False

def main():
    """
    Función principal que ejecuta todos los procesos en orden
    """
    print("🚤" * 20)
    print("🚤 ACTUALIZAR TODO - HOTBOAT")
    print("🚤" * 20)
    print()
    print("📋 Este script ejecutará todos los procesos en el siguiente orden:")
    print("   1. 🏦 Procesar gastos y costos (gastos_hotboat_sin_drive.py)")
    print("   2. 📅 Procesar reservas (Informacion_reservas.py)")
    print("   3. 💰 Calcular utilidad (estimacion_utilidad_hotboat.py)")
    print("   4. 📊 Ejecutar dashboards (ejecutar_todos_dashboards.py)")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('gastos_hotboat_sin_drive.py'):
        print("❌ ERROR: No se encontró gastos_hotboat_sin_drive.py")
        print("💡 Asegúrate de estar en el directorio correcto del proyecto")
        return False
    
    # Lista de comandos a ejecutar en orden
    comandos = [
        ("python gastos_hotboat_sin_drive.py", "PROCESAR GASTOS Y COSTOS"),
        ("python Informacion_reservas.py", "PROCESAR RESERVAS"),
        ("python estimacion_utilidad_hotboat.py", "CALCULAR UTILIDAD"),
        ("python ejecutar_todos_dashboards.py", "EJECUTAR DASHBOARDS")
    ]
    
    # Contador de procesos exitosos
    procesos_exitosos = 0
    procesos_fallidos = 0
    
    # Ejecutar cada comando en orden
    for i, (comando, descripcion) in enumerate(comandos, 1):
        print(f"\n📋 Paso {i}/4: {descripcion}")
        
        if ejecutar_comando(comando, descripcion):
            procesos_exitosos += 1
            print(f"✅ Paso {i} completado exitosamente")
        else:
            procesos_fallidos += 1
            print(f"❌ Paso {i} falló")
            
            # Preguntar si continuar con los siguientes pasos
            if i < len(comandos):
                respuesta = input(f"\n❓ ¿Deseas continuar con los siguientes pasos? (s/n): ").lower().strip()
                if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
                    print("🛑 Proceso interrumpido por el usuario")
                    break
        
        # Pausa entre procesos (excepto el último)
        if i < len(comandos):
            print("\n⏳ Esperando 2 segundos antes del siguiente proceso...")
            time.sleep(2)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Procesos exitosos: {procesos_exitosos}")
    print(f"❌ Procesos fallidos: {procesos_fallidos}")
    print(f"📈 Total de procesos: {len(comandos)}")
    
    if procesos_fallidos == 0:
        print("\n🎉 ¡Todos los procesos se completaron exitosamente!")
        print("🌐 Los dashboards deberían estar ejecutándose en:")
        print("   - Dashboard Reservas: http://localhost:8050")
        print("   - Dashboard Utilidad: http://localhost:8055")
        print("   - Dashboard Marketing: http://localhost:8056")
    else:
        print(f"\n⚠️  {procesos_fallidos} proceso(s) falló/failaron")
        print("💡 Revisa los errores anteriores y ejecuta manualmente los procesos fallidos")
    
    print("\n" + "=" * 60)
    return procesos_fallidos == 0

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1) 