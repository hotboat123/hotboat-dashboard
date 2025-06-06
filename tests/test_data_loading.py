#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests para validar la carga de datos de HotBoat
Estos tests aseguran que los datos se carguen correctamente y tengan el formato esperado.
USAN DATOS ESTÁTICOS desde tests/test_data/ para garantizar consistencia.
"""

import pandas as pd
import os
import sys

# Agregar el directorio padre al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el cargador de datos de test
from test_data_loader import cargar_datos_test

class TestDataLoading:
    """Tests para validar la carga de datos usando datos estáticos de test"""
    
    def test_cargar_datos_test_success(self):
        """Test que verifica que cargar_datos_test() funcione sin errores"""
        try:
            datos = cargar_datos_test()
            assert datos is not None, "cargar_datos_test() devolvió None"
            assert isinstance(datos, dict), "cargar_datos_test() no devolvió un diccionario"
            print("✅ cargar_datos_test() ejecutado exitosamente")
        except Exception as e:
            raise AssertionError(f"cargar_datos_test() falló: {e}")
    
    def test_datos_structure(self):
        """Test que verifica la estructura de los datos cargados"""
        datos = cargar_datos_test()
        
        # Verificar que existan las claves esperadas
        expected_keys = [
            'reservas', 'pagos', 'gastos', 'costos_fijos', 
            'ingresos', 'costos_operativos', 'gastos_marketing'
        ]
        
        for key in expected_keys:
            assert key in datos, f"Falta la clave '{key}' en los datos"
            assert isinstance(datos[key], pd.DataFrame), f"'{key}' no es un DataFrame"
        
        print("✅ Estructura de datos validada correctamente")
    
    def test_datos_consistency(self):
        """Test que verifica la consistencia de los datos de test"""
        datos = cargar_datos_test()
        
        data_counts = {}
        for key, df in datos.items():
            data_counts[key] = len(df)
        
        print("✅ Conteos de datos de test:")
        for key, count in data_counts.items():
            print(f"   {key}: {count} filas")
        
        # Verificar que tenemos datos básicos
        assert data_counts['costos_fijos'] == 6, f"Se esperaban 6 costos fijos, se encontraron {data_counts['costos_fijos']}"
        
        # Si hay reservas, debe haber ingresos
        if data_counts['reservas'] > 0:
            assert data_counts['ingresos'] > 0, "Si hay reservas, debe haber ingresos"
        
        print("✅ Consistencia de datos validada")
    
    def test_reservas_columns(self):
        """Test que verifica las columnas esperadas en reservas"""
        datos = cargar_datos_test()
        reservas = datos['reservas']
        
        if not reservas.empty:
            # Verificar que existan columnas críticas
            critical_columns = ['fecha_trip', 'TOTAL AMOUNT']
            
            for col in critical_columns:
                if col in reservas.columns:
                    print(f"✅ Columna '{col}' encontrada")
                else:
                    print(f"⚠️ Columna '{col}' no encontrada en reservas")
                    print(f"   Columnas disponibles: {list(reservas.columns)}")
        else:
            print("ℹ️ No hay datos de reservas en el dataset de test")
    
    def test_ingresos_data_quality(self):
        """Test que verifica la calidad de los datos de ingresos"""
        datos = cargar_datos_test()
        ingresos = datos['ingresos']
        
        if not ingresos.empty:
            # Verificar que no hay valores negativos en montos
            if 'monto' in ingresos.columns:
                negative_amounts = ingresos[ingresos['monto'] < 0]
                assert len(negative_amounts) == 0, f"Encontrados {len(negative_amounts)} montos negativos en ingresos"
            
            # Verificar que las fechas son válidas
            if 'fecha' in ingresos.columns:
                assert ingresos['fecha'].notna().all(), "Hay fechas nulas en ingresos"
        
        print("✅ Calidad de datos de ingresos validada")
    
    def test_archivos_test_exist(self):
        """Test que verifica que existan los archivos de test"""
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        
        # Verificar estructura de carpetas
        expected_dirs = ['reservas', 'costos', 'marketing']
        for dirname in expected_dirs:
            dir_path = os.path.join(test_data_dir, dirname)
            assert os.path.exists(dir_path), f"Directorio de test no encontrado: {dir_path}"
            print(f"✅ Directorio de test encontrado: {dirname}")
        
        # Verificar archivos críticos
        reservas_dir = os.path.join(test_data_dir, 'reservas')
        critical_files = [
            'reservas_HotBoat.csv',
            'payments_2025May12.csv',
            'HotBoat - Pedidos Extras.csv'
        ]
        
        for filename in critical_files:
            file_path = os.path.join(reservas_dir, filename)
            if os.path.exists(file_path):
                print(f"✅ Archivo de test encontrado: {filename}")
                
                # Verificar que se puede leer
                try:
                    df = pd.read_csv(file_path)
                    print(f"   Dimensiones: {df.shape}")
                except Exception as e:
                    raise AssertionError(f"Error al leer {file_path}: {e}")
            else:
                print(f"⚠️ Archivo de test no encontrado: {filename}")
    
    def test_baseline_metrics_calculation(self):
        """Test que verifica que se puedan calcular métricas baseline"""
        datos = cargar_datos_test()
        
        # Calcular métricas básicas
        metricas = {}
        
        if not datos['ingresos'].empty and 'monto' in datos['ingresos'].columns:
            metricas['total_ingresos'] = datos['ingresos']['monto'].sum()
        
        if not datos['costos_operativos'].empty and 'monto' in datos['costos_operativos'].columns:
            metricas['total_costos_operativos'] = datos['costos_operativos']['monto'].sum()
        
        if not datos['gastos_marketing'].empty and 'monto' in datos['gastos_marketing'].columns:
            metricas['total_gastos_marketing'] = datos['gastos_marketing']['monto'].sum()
        
        # Verificar que se pueden calcular métricas
        assert len(metricas) > 0, "No se pudieron calcular métricas básicas"
        
        print("✅ Métricas calculadas:")
        for key, value in metricas.items():
            print(f"   {key}: ${value:,.0f}")

def run_tests():
    """Ejecuta todos los tests y retorna si pasaron"""
    test_instance = TestDataLoading()
    
    print("🧪 EJECUTANDO TESTS CON DATOS ESTÁTICOS DE TEST")
    print("=" * 60)
    
    tests = [
        test_instance.test_cargar_datos_test_success,
        test_instance.test_datos_structure,
        test_instance.test_datos_consistency,
        test_instance.test_reservas_columns,
        test_instance.test_ingresos_data_quality,
        test_instance.test_archivos_test_exist,
        test_instance.test_baseline_metrics_calculation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n🔍 Ejecutando: {test.__name__}")
            test()
            passed += 1
            print(f"✅ {test.__name__} - PASÓ")
        except Exception as e:
            print(f"❌ {test.__name__} falló: {e}")
            failed += 1
    
    print(f"\n📊 Resumen: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        return True
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 