#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 Actualizar Reservas y Utilidad Operativa - HotBoat
=====================================================

Este script ejecuta, en orden:
1) Informacion_reservas.py
2) estimacion_utilidad_hotboat.py
3) utilidad_operativa.py

Uso:
    python actualizar_reservas_utilidad.py
"""

import os
import sys
import time
import subprocess


def _python_interpreter() -> str:
    """Devuelve el intérprete de Python del venv si existe; si no, 'python'."""
    # Windows
    win_path = os.path.join('venv', 'Scripts', 'python.exe')
    # Unix-like
    nix_path = os.path.join('venv', 'bin', 'python')

    if os.path.exists(win_path):
        return win_path
    if os.path.exists(nix_path):
        return nix_path
    return 'python'


def ejecutar_comando(comando: str, descripcion: str) -> bool:
    """Ejecuta un comando y muestra outputs/errores detallados."""
    print("=" * 60)
    print(f"🔄 {descripcion}")
    print("=" * 60)
    print(f"📋 Ejecutando: {comando}")
    print()
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
        )
        if resultado.stdout:
            print("✅ Output:")
            print(resultado.stdout)
        if resultado.stderr:
            # Mostrar stderr como info adicional para debugging
            print("ℹ️  Stderr (informativo):")
            print(resultado.stderr)
        print(f"✅ {descripcion} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {descripcion}")
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


def main() -> bool:
    print("🚤" * 20)
    print("🚤 ACTUALIZAR RESERVAS Y UTILIDAD OPERATIVA - HOTBOAT")
    print("🚤" * 20)
    print()
    print("📋 Orden de ejecución:")
    print("   1. 📅 Informacion_reservas.py")
    print("   2. 💰 estimacion_utilidad_hotboat.py")
    print("   3. 📈 utilidad_operativa.py")
    print()

    # Verificaciones básicas de archivos
    required_files = [
        'Informacion_reservas.py',
        'estimacion_utilidad_hotboat.py',
        'utilidad_operativa.py',
    ]
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print("❌ ERROR: No se encontraron los siguientes archivos requeridos:")
        for f in missing:
            print(f"   - {f}")
        print("💡 Asegúrate de ejecutar este script en el directorio raíz del proyecto.")
        return False

    py = _python_interpreter()

    comandos = [
        (f"{py} Informacion_reservas.py", "PROCESAR RESERVAS"),
        (f"{py} estimacion_utilidad_hotboat.py", "CALCULAR UTILIDAD HOTBOAT"),
        (f"{py} utilidad_operativa.py", "GENERAR UTILIDAD OPERATIVA"),
    ]

    exitos = 0
    fallos = 0

    for i, (cmd, desc) in enumerate(comandos, 1):
        print(f"\n📋 Paso {i}/{len(comandos)}: {desc}")
        ok = ejecutar_comando(cmd, desc)
        if ok:
            exitos += 1
            print(f"✅ Paso {i} completado")
        else:
            fallos += 1
            print(f"❌ Paso {i} falló")
        if i < len(comandos):
            print("\n⏳ Esperando 2 segundos antes del siguiente proceso...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Procesos exitosos: {exitos}")
    print(f"❌ Procesos fallidos: {fallos}")
    print(f"📈 Total de procesos: {len(comandos)}")

    if fallos == 0:
        print("\n🎉 ¡Actualización completada exitosamente!")
    else:
        print("\n⚠️  Hubo fallos. Revisa el detalle arriba y ejecuta manualmente lo necesario.")

    return fallos == 0


if __name__ == "__main__":
    # Configurar UTF-8 para que los emojis funcionen siempre
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

    try:
        ok = main()
        sys.exit(0 if ok else 1)
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)

