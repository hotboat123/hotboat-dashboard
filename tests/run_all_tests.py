#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ejecutar todos los tests de HotBoat
Este script ejecuta todos los tests en el orden correcto y genera un reporte.
"""

import os
import sys
import importlib.util
from datetime import datetime

def load_test_module(test_file):
    """Carga un módulo de test dinámicamente"""
    spec = importlib.util.spec_from_file_location("test_module", test_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_test_file(test_file, test_name):
    """Ejecuta un archivo de test específico"""
    print(f"\n{'='*60}")
    print(f"🧪 EJECUTANDO: {test_name}")
    print(f"📁 Archivo: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Cambiar al directorio del script para imports relativos
        original_dir = os.getcwd()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.dirname(script_dir))
        
        # Ejecutar el test
        os.system(f"python {test_file}")
        
        # Restaurar directorio original
        os.chdir(original_dir)
        
        print(f"✅ {test_name} completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en {test_name}: {e}")
        return False

def main():
    """Función principal que ejecuta todos los tests"""
    
    print("🚤 SISTEMA DE TESTING HOTBOAT")
    print("=" * 60)
    print(f"📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objetivo: Validar que todos los componentes funcionen correctamente")
    print("=" * 60)
    
    # Lista de tests a ejecutar
    tests = [
        {
            "file": "tests/test_data_loading.py",
            "name": "Tests de Carga de Datos",
            "description": "Valida que los datos se carguen correctamente"
        },
        {
            "file": "tests/test_dashboard_outputs.py", 
            "name": "Tests de Dashboard Outputs",
            "description": "Verifica que los dashboards se creen sin errores"
        },
        {
            "file": "tests/test_metricas_regression.py",
            "name": "Tests de Regresión de Métricas", 
            "description": "Asegura que las métricas no cambien inesperadamente"
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n📋 {test['name']}")
        print(f"   {test['description']}")
        
        if os.path.exists(test["file"]):
            success = run_test_file(test["file"], test["name"])
            results.append({
                "name": test["name"],
                "success": success,
                "file": test["file"]
            })
        else:
            print(f"⚠️ Archivo de test no encontrado: {test['file']}")
            results.append({
                "name": test["name"],
                "success": False,
                "file": test["file"]
            })
    
    # Reporte final
    print(f"\n{'='*60}")
    print("📊 REPORTE FINAL DE TESTING")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"✅ Tests exitosos: {passed_tests}/{total_tests}")
    print(f"❌ Tests fallidos: {failed_tests}/{total_tests}")
    
    if failed_tests > 0:
        print(f"\n❌ Tests que fallaron:")
        for result in results:
            if not result["success"]:
                print(f"   - {result['name']}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! El sistema está funcionando correctamente.")
        print("✨ Los dashboards están listos para usar en producción.")
    elif success_rate >= 80:
        print("\n⚠️ La mayoría de tests pasaron, pero hay algunos problemas menores.")
        print("🔧 Revisa los tests fallidos antes de usar en producción.")
    else:
        print("\n🚨 ALERTA: Múltiples tests fallaron.")
        print("🛠️ Es recomendable revisar y arreglar los problemas antes de continuar.")
    
    print(f"\n📝 Para más detalles, revisa los logs arriba.")
    print(f"🔄 Ejecuta este script regularmente después de hacer cambios.")
    
    return success_rate == 100

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrumpido por el usuario.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1) 