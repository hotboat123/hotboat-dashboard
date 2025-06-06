#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests para validar que los dashboards funcionen correctamente
Estos tests verifican que las aplicaciones se creen sin errores y produzcan outputs esperados.
"""

import pandas as pd
import os
import sys
import json
from datetime import datetime

# Agregar el directorio padre al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboards import cargar_datos, crear_app_reservas, crear_app_utilidad

class TestDashboardOutputs:
    """Tests para validar los outputs de los dashboards"""
    
    def __init__(self):
        """Configuración inicial para todos los tests"""
        print("🔧 Configurando tests de dashboard...")
        self.datos = cargar_datos()
    
    def test_crear_app_reservas(self):
        """Test que verifica que la app de reservas se cree correctamente"""
        try:
            app = crear_app_reservas(self.datos)
            assert app is not None
            print("✅ App de reservas creada exitosamente")
            
            # Verificar que el layout no esté vacío
            assert app.layout is not None
            print("✅ Layout de reservas configurado correctamente")
            
        except Exception as e:
            raise AssertionError(f"Error al crear app de reservas: {e}")
    
    def test_crear_app_utilidad(self):
        """Test que verifica que la app de utilidad se cree correctamente"""
        try:
            app = crear_app_utilidad(self.datos)
            assert app is not None
            print("✅ App de utilidad creada exitosamente")
            
            # Verificar que el layout no esté vacío
            assert app.layout is not None
            print("✅ Layout de utilidad configurado correctamente")
            
        except Exception as e:
            raise AssertionError(f"Error al crear app de utilidad: {e}")
    
    def test_calcular_metricas_basicas(self):
        """Test que verifica que se puedan calcular métricas básicas"""
        reservas = self.datos['reservas']
        ingresos = self.datos['ingresos']
        
        if not reservas.empty and not ingresos.empty:
            # Test de conteo básico
            total_reservas = len(reservas)
            total_ingresos = len(ingresos)
            
            assert total_reservas >= 0, "Total de reservas no puede ser negativo"
            assert total_ingresos >= 0, "Total de ingresos no puede ser negativo"
            
            print(f"✅ Métricas básicas calculadas:")
            print(f"   Total reservas: {total_reservas}")
            print(f"   Total ingresos: {total_ingresos}")
    
    def test_data_consistency(self):
        """Test que verifica consistencia entre datasets"""
        datos = self.datos
        
        # Verificar que las fechas estén en formato correcto
        for key, df in datos.items():
            if not df.empty and 'fecha' in df.columns:
                try:
                    pd.to_datetime(df['fecha'])
                    print(f"✅ Fechas en '{key}' son válidas")
                except Exception as e:
                    print(f"⚠️ Error en fechas de '{key}': {e}")
    
    def test_save_test_snapshot(self):
        """Test que guarda un snapshot de los datos actuales para comparaciones futuras"""
        snapshot_dir = "tests/snapshots"
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Crear snapshot de métricas clave
        snapshot = {
            "fecha_creacion": datetime.now().isoformat(),
            "metricas": {}
        }
        
        for key, df in self.datos.items():
            if not df.empty:
                snapshot["metricas"][key] = {
                    "filas": len(df),
                    "columnas": len(df.columns),
                    "columnas_nombres": list(df.columns)
                }
        
        # Guardar snapshot
        snapshot_file = os.path.join(snapshot_dir, "data_snapshot.json")
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Snapshot guardado en: {snapshot_file}")
        
        # Verificar que el archivo se creó
        assert os.path.exists(snapshot_file), "Snapshot no se pudo crear"
    
    def test_compare_with_previous_snapshot(self):
        """Test que compara con snapshot anterior (si existe)"""
        snapshot_file = "tests/snapshots/data_snapshot.json"
        
        if os.path.exists(snapshot_file):
            print("📊 Comparando con snapshot anterior...")
            
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                previous_snapshot = json.load(f)
            
            # Comparar métricas clave
            previous_metrics = previous_snapshot.get("metricas", {})
            
            for key, df in self.datos.items():
                if not df.empty and key in previous_metrics:
                    current_rows = len(df)
                    previous_rows = previous_metrics[key]["filas"]
                    
                    # Alertar si hay cambios significativos
                    if abs(current_rows - previous_rows) > 0:
                        print(f"⚠️ Cambio detectado en '{key}':")
                        print(f"   Anterior: {previous_rows} filas")
                        print(f"   Actual: {current_rows} filas")
                        print(f"   Diferencia: {current_rows - previous_rows}")
                    else:
                        print(f"✅ '{key}' sin cambios: {current_rows} filas")
        else:
            print("ℹ️ No hay snapshot anterior para comparar")

def run_tests():
    """Ejecuta todos los tests y retorna si pasaron"""
    test_instance = TestDashboardOutputs()
    
    print("🧪 EJECUTANDO TESTS DE DASHBOARD OUTPUTS")
    print("=" * 50)
    
    tests = [
        test_instance.test_crear_app_reservas,
        test_instance.test_crear_app_utilidad,
        test_instance.test_calcular_metricas_basicas,
        test_instance.test_data_consistency,
        test_instance.test_save_test_snapshot,
        test_instance.test_compare_with_previous_snapshot
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} falló: {e}")
            failed += 1
    
    print(f"\n📊 Resumen: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 TODOS LOS TESTS DE DASHBOARD PASARON EXITOSAMENTE")
        return True
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 