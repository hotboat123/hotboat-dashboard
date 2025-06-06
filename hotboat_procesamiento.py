#!/usr/bin/env python3
"""
🚤 HOTBOAT - SISTEMA DE PROCESAMIENTO DE DATOS
=============================================

Este archivo centraliza todos los procesos de transformación de datos de HotBoat.
Convierte archivos de input en archivos de output procesados y listos para análisis.

Procesos disponibles:
- Procesamiento de Reservas (archivos_input → archivos_output)
- Procesamiento de Gastos (sin dependencia de Google Drive)
- Estimaciones de Utilidad
- Validación y limpieza de datos

Uso:
    python hotboat_procesamiento.py [reservas|gastos|utilidad|validar|todos]

Autor: Sistema HotBoat
Versión: 1.0
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def mostrar_menu():
    """Muestra el menú principal de procesamiento"""
    print("\n" + "="*60)
    print("🚤 HOTBOAT - SISTEMA DE PROCESAMIENTO DE DATOS")
    print("="*60)
    print("1. 🛥️  Procesar Información de Reservas")
    print("2. 💰 Procesar Gastos (sin Google Drive)")
    print("3. 📊 Generar Estimaciones de Utilidad")
    print("4. 🔍 Validar y Depurar Datos")
    print("5. 📈 Procesar Datos de Marketing")
    print("6. 🌐 Ejecutar Todos los Procesos")
    print("7. ❌ Salir")
    print("="*60)

def ejecutar_proceso(tipo):
    """Ejecuta un proceso específico de datos"""
    procesamiento_dir = Path("procesamiento")
    
    # Mapeo de archivos y descripciones
    procesos = {
        'reservas': {
            'archivo': 'Informacion_reservas.py',
            'descripcion': 'Procesamiento de Información de Reservas',
            'input': 'archivos_input/reservas/',
            'output': 'archivos_output/'
        },
        'gastos': {
            'archivo': 'gastos_hotboat_sin_drive.py',
            'descripcion': 'Procesamiento de Gastos (sin Google Drive)',
            'input': 'archivos_input/gastos/',
            'output': 'archivos_output/'
        },
        'utilidad': {
            'archivo': 'estimacion_utilidad_hotboat.py',
            'descripcion': 'Estimaciones de Utilidad Operativa',
            'input': 'archivos_output/',
            'output': 'reportes/'
        },
        'validar': {
            'archivo': 'check_data.py',
            'descripcion': 'Validación y Depuración de Datos',
            'input': 'archivos_input/',
            'output': 'logs/'
        },
        'marketing': {
            'archivo': 'gastos_marketing.py',
            'descripcion': 'Procesamiento de Datos de Marketing',
            'input': 'archivos_input/marketing/',
            'output': 'archivos_output/'
        }
    }
    
    if tipo not in procesos:
        print(f"❌ Error: Proceso '{tipo}' no válido")
        return False
    
    proceso = procesos[tipo]
    archivo = procesamiento_dir / proceso['archivo']
    
    if not archivo.exists():
        print(f"❌ Error: No se encontró {archivo}")
        return False
    
    try:
        print(f"\n🚀 Iniciando {proceso['descripcion']}...")
        print(f"📥 Input: {proceso['input']}")
        print(f"📤 Output: {proceso['output']}")
        print(f"🔄 Procesando...")
        print("-" * 50)
        
        # Ejecutar el proceso
        resultado = subprocess.run([sys.executable, str(archivo)], 
                                 capture_output=True, text=True, check=True)
        
        print("✅ Proceso completado exitosamente!")
        if resultado.stdout:
            print("📋 Salida del proceso:")
            print(resultado.stdout)
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {proceso['descripcion']}")
        print(f"💬 Código de error: {e.returncode}")
        if e.stderr:
            print(f"📋 Error detallado:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def ejecutar_todos():
    """Ejecuta todos los procesos en secuencia"""
    print("\n🌐 Iniciando todos los procesos de datos...")
    print("⏳ Los procesos se ejecutarán en secuencia para evitar conflictos")
    print("=" * 50)
    
    # Orden recomendado de ejecución
    orden_procesos = [
        ('validar', 'Validación inicial de datos'),
        ('reservas', 'Procesamiento de reservas'),
        ('gastos', 'Procesamiento de gastos'),
        ('marketing', 'Procesamiento de marketing'),
        ('utilidad', 'Estimaciones de utilidad')
    ]
    
    resultados = []
    
    for proceso, descripcion in orden_procesos:
        print(f"\n📋 Paso {len(resultados)+1}/5: {descripcion}")
        print("-" * 30)
        
        exito = ejecutar_proceso(proceso)
        resultados.append((proceso, descripcion, exito))
        
        if exito:
            print(f"✅ {descripcion} - COMPLETADO")
        else:
            print(f"❌ {descripcion} - FALLÓ")
            
        time.sleep(1)  # Pausa breve entre procesos
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE PROCESAMIENTO")
    print("="*60)
    
    exitosos = 0
    for proceso, descripcion, exito in resultados:
        estado = "✅ EXITOSO" if exito else "❌ FALLÓ"
        print(f"{estado:12} | {descripcion}")
        if exito:
            exitosos += 1
    
    print("-" * 60)
    print(f"📈 Total: {exitosos}/{len(resultados)} procesos completados exitosamente")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todos los procesos se completaron correctamente!")
    else:
        print("⚠️ Algunos procesos fallaron. Revisa los errores arriba.")

def verificar_estructura():
    """Verifica que existe la estructura de directorios necesaria"""
    directorios_necesarios = [
        'archivos_input',
        'archivos_output', 
        'procesamiento'
    ]
    
    faltantes = []
    for directorio in directorios_necesarios:
        if not Path(directorio).exists():
            faltantes.append(directorio)
    
    if faltantes:
        print("⚠️ Advertencia: Faltan algunos directorios:")
        for directorio in faltantes:
            print(f"   - {directorio}/")
        print("\n💡 Creando directorios faltantes...")
        
        for directorio in faltantes:
            Path(directorio).mkdir(exist_ok=True)
            print(f"✅ Creado: {directorio}/")

def mostrar_estado_archivos():
    """Muestra el estado actual de archivos de input y output"""
    print("\n📁 ESTADO ACTUAL DE ARCHIVOS")
    print("="*50)
    
    # Verificar archivos de input
    input_dir = Path("archivos_input")
    if input_dir.exists():
        archivos_input = list(input_dir.rglob("*.csv")) + list(input_dir.rglob("*.xlsx"))
        print(f"📥 Archivos de input: {len(archivos_input)} encontrados")
        if archivos_input:
            for archivo in archivos_input[:5]:  # Mostrar solo los primeros 5
                size_kb = archivo.stat().st_size / 1024
                print(f"   - {archivo.name} ({size_kb:.1f} KB)")
            if len(archivos_input) > 5:
                print(f"   ... y {len(archivos_input) - 5} más")
    else:
        print("📥 Archivos de input: Directorio no encontrado")
    
    # Verificar archivos de output
    output_dir = Path("archivos_output")
    if output_dir.exists():
        archivos_output = list(output_dir.rglob("*.csv")) + list(output_dir.rglob("*.xlsx"))
        print(f"📤 Archivos de output: {len(archivos_output)} encontrados")
        if archivos_output:
            for archivo in archivos_output[:5]:  # Mostrar solo los primeros 5
                size_kb = archivo.stat().st_size / 1024
                print(f"   - {archivo.name} ({size_kb:.1f} KB)")
            if len(archivos_output) > 5:
                print(f"   ... y {len(archivos_output) - 5} más")
    else:
        print("📤 Archivos de output: Directorio no encontrado")

def main():
    """Función principal"""
    # Verificar estructura de directorios
    verificar_estructura()
    
    # Si se pasa un argumento de línea de comandos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando in ['reservas', 'gastos', 'utilidad', 'validar', 'marketing']:
            ejecutar_proceso(comando)
        elif comando in ['todos', 'all']:
            ejecutar_todos()
        elif comando in ['estado', 'status']:
            mostrar_estado_archivos()
        else:
            print(f"❌ Comando no válido: {comando}")
            print("💡 Uso: python hotboat_procesamiento.py [reservas|gastos|utilidad|validar|marketing|todos|estado]")
        return
    
    # Interfaz interactiva
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\n🎯 Selecciona una opción (1-7): ").strip()
            
            if opcion == '1':
                ejecutar_proceso('reservas')
            elif opcion == '2':
                ejecutar_proceso('gastos')
            elif opcion == '3':
                ejecutar_proceso('utilidad')
            elif opcion == '4':
                ejecutar_proceso('validar')
            elif opcion == '5':
                ejecutar_proceso('marketing')
            elif opcion == '6':
                ejecutar_todos()
            elif opcion == '7':
                print("\n👋 ¡Procesamiento completado! Datos listos para HotBoat 🚤")
                break
            else:
                print("❌ Opción no válida. Por favor selecciona 1-7.")
                
            # Opción para mostrar estado después de cada proceso
            if opcion in ['1', '2', '3', '4', '5', '6']:
                mostrar_estado = input("\n📊 ¿Mostrar estado de archivos? (s/N): ").strip().lower()
                if mostrar_estado in ['s', 'sí', 'si', 'y', 'yes']:
                    mostrar_estado_archivos()
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Procesamiento interrumpido! Datos seguros en HotBoat 🚤")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 