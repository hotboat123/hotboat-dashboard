#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests para validar la carga de datos de HotBoat
Estos tests aseguran que los datos se carguen correctamente y tengan el formato esperado.
"""

import pandas as pd
import os
import sys

# Agregar el directorio padre al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboards import cargar_datos

class TestDataLoading:
    """Tests para validar la carga de datos"""
    
    def test_cargar_datos_success(self):
        """Test que verifica que cargar_datos() funcione sin errores"""
        try:
            datos = cargar_datos()
            assert datos is not None, "cargar_datos() devolvió None"
            assert isinstance(datos, dict), "cargar_datos() no devolvió un diccionario"
            print("✅ cargar_datos() ejecutado exitosamente")
        except Exception as e:
            raise AssertionError(f"cargar_datos() falló: {e}")
    
    def test_datos_structure(self):
        """Test que verifica la estructura de los datos cargados"""
        datos = cargar_datos()
        
        # Verificar que existan las claves esperadas
        expected_keys = [
            'reservas', 'pagos', 'gastos', 'costos_fijos', 
            'ingresos', 'costos_operativos', 'gastos_marketing'
        ]
        
        for key in expected_keys:
            assert key in datos, f"Falta la clave '{key}' en los datos"
            assert isinstance(datos[key], pd.DataFrame), f"'{key}' no es un DataFrame"
        
        print("✅ Estructura de datos validada correctamente")
    
    def test_datos_not_empty(self):
        """Test que verifica que los datos no estén vacíos"""
        datos = cargar_datos()
        
        data_counts = {}
        for key, df in datos.items():
            if not df.empty:
                data_counts[key] = len(df)
                assert len(df) > 0, f"DataFrame '{key}' está vacío"
        
        print("✅ Conteos de datos:")
        for key, count in data_counts.items():
            print(f"   {key}: {count} filas")
    
    def test_reservas_columns(self):
        """Test que verifica las columnas esperadas en reservas"""
        datos = cargar_datos()
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
    
    def test_ingresos_data_quality(self):
        """Test que verifica la calidad de los datos de ingresos"""
        datos = cargar_datos()
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
    
    def test_archivos_marketing_exist(self):
        """Test que verifica que existan los archivos de marketing"""
        marketing_files = [
            "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv",
            "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia.csv"
        ]
        
        for file_path in marketing_files:
            if os.path.exists(file_path):
                print(f"✅ Archivo encontrado: {file_path}")
                
                # Verificar que se puede leer
                try:
                    df = pd.read_csv(file_path)
                    print(f"   Dimensiones: {df.shape}")
                except Exception as e:
                    raise AssertionError(f"Error al leer {file_path}: {e}")
            else:
                print(f"⚠️ Archivo no encontrado: {file_path}")

def run_tests():
    """Ejecuta todos los tests y retorna si pasaron"""
    test_instance = TestDataLoading()
    
    print("🧪 EJECUTANDO TESTS DE CARGA DE DATOS")
    print("=" * 50)
    
    tests = [
        test_instance.test_cargar_datos_success,
        test_instance.test_datos_structure,
        test_instance.test_datos_not_empty,
        test_instance.test_reservas_columns,
        test_instance.test_ingresos_data_quality,
        test_instance.test_archivos_marketing_exist
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
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        return True
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 