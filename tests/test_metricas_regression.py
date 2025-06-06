#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de regresión para métricas críticas de HotBoat
Estos tests calculan métricas financieras clave y las comparan con un baseline.
USAN DATOS ESTÁTICOS desde tests/test_data/ para garantizar consistencia.
"""

import pandas as pd
import os
import sys
import json
from datetime import datetime

# Agregar el directorio padre al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el cargador de datos de test
from test_data_loader import cargar_datos_test

class TestMetricasRegression:
    """Tests de regresión para métricas críticas del negocio"""
    
    def __init__(self):
        """Configuración inicial"""
        self.baseline_file = os.path.join(os.path.dirname(__file__), 'baselines', 'metricas_baseline_test.json')
        self.tolerance = 0.01  # 1% de tolerancia
        
        # Crear directorio de baselines si no existe
        baseline_dir = os.path.dirname(self.baseline_file)
        if not os.path.exists(baseline_dir):
            os.makedirs(baseline_dir)
    
    def calcular_metricas_test(self):
        """Calcula métricas usando datos estáticos de test"""
        print("📊 Calculando métricas con datos de test...")
        
        datos = cargar_datos_test()
        metricas = {}
        
        try:
            # === INGRESOS ===
            if not datos['ingresos'].empty and 'monto' in datos['ingresos'].columns:
                metricas['total_ingresos_test'] = float(datos['ingresos']['monto'].sum())
                metricas['promedio_ingreso_test'] = float(datos['ingresos']['monto'].mean())
                metricas['num_transacciones_ingresos'] = len(datos['ingresos'])
            else:
                metricas['total_ingresos_test'] = 0.0
                metricas['promedio_ingreso_test'] = 0.0
                metricas['num_transacciones_ingresos'] = 0
            
            # === COSTOS OPERATIVOS ===
            if not datos['costos_operativos'].empty and 'monto' in datos['costos_operativos'].columns:
                metricas['total_costos_operativos_test'] = float(datos['costos_operativos']['monto'].sum())
                metricas['promedio_costo_operativo'] = float(datos['costos_operativos']['monto'].mean())
            else:
                metricas['total_costos_operativos_test'] = 0.0
                metricas['promedio_costo_operativo'] = 0.0
            
            # === GASTOS MARKETING ===
            if not datos['gastos_marketing'].empty and 'monto' in datos['gastos_marketing'].columns:
                metricas['total_gastos_marketing_test'] = float(datos['gastos_marketing']['monto'].sum())
                metricas['promedio_gasto_marketing'] = float(datos['gastos_marketing']['monto'].mean())
            else:
                metricas['total_gastos_marketing_test'] = 0.0
                metricas['promedio_gasto_marketing'] = 0.0
            
            # === COSTOS FIJOS ===
            if not datos['costos_fijos'].empty and 'monto_mensual' in datos['costos_fijos'].columns:
                metricas['total_costos_fijos_mensual'] = float(datos['costos_fijos']['monto_mensual'].sum())
                metricas['num_conceptos_costos_fijos'] = len(datos['costos_fijos'])
            else:
                metricas['total_costos_fijos_mensual'] = 0.0
                metricas['num_conceptos_costos_fijos'] = 0
            
            # === MÉTRICAS CALCULADAS ===
            if metricas['total_ingresos_test'] > 0:
                # Utilidad bruta
                metricas['utilidad_bruta_test'] = metricas['total_ingresos_test'] - metricas['total_costos_operativos_test']
                
                # Margen bruto
                metricas['margen_bruto_test'] = (metricas['utilidad_bruta_test'] / metricas['total_ingresos_test']) * 100
                
                # ROI Marketing (si hay gastos de marketing)
                if metricas['total_gastos_marketing_test'] > 0:
                    metricas['roi_marketing_test'] = (metricas['total_ingresos_test'] / metricas['total_gastos_marketing_test']) * 100
                else:
                    metricas['roi_marketing_test'] = 0.0
                
                # Costo por transacción
                if metricas['num_transacciones_ingresos'] > 0:
                    metricas['costo_por_transaccion'] = metricas['total_costos_operativos_test'] / metricas['num_transacciones_ingresos']
                else:
                    metricas['costo_por_transaccion'] = 0.0
            else:
                metricas['utilidad_bruta_test'] = 0.0
                metricas['margen_bruto_test'] = 0.0
                metricas['roi_marketing_test'] = 0.0
                metricas['costo_por_transaccion'] = 0.0
            
            # Timestamp del cálculo
            metricas['fecha_calculo'] = datetime.now().isoformat()
            metricas['tipo_datos'] = 'test_estaticos'
            
            print(f"✅ Métricas calculadas: {len(metricas)} métricas")
            return metricas
            
        except Exception as e:
            print(f"❌ Error al calcular métricas: {e}")
            raise
    
    def guardar_baseline(self, metricas):
        """Guarda las métricas como baseline"""
        try:
            with open(self.baseline_file, 'w', encoding='utf-8') as f:
                json.dump(metricas, f, indent=2, ensure_ascii=False)
            print(f"✅ Baseline guardado en: {self.baseline_file}")
        except Exception as e:
            print(f"❌ Error al guardar baseline: {e}")
            raise
    
    def cargar_baseline(self):
        """Carga el baseline guardado"""
        try:
            if os.path.exists(self.baseline_file):
                with open(self.baseline_file, 'r', encoding='utf-8') as f:
                    baseline = json.load(f)
                print(f"✅ Baseline cargado desde: {self.baseline_file}")
                return baseline
            else:
                print("ℹ️ No existe baseline previo")
                return None
        except Exception as e:
            print(f"❌ Error al cargar baseline: {e}")
            return None
    
    def comparar_con_baseline(self, metricas_actuales, baseline):
        """Compara métricas actuales con baseline"""
        cambios_significativos = []
        
        print("🔍 Comparando con baseline...")
        
        for key, valor_actual in metricas_actuales.items():
            if key in ['fecha_calculo', 'tipo_datos']:
                continue
                
            if key in baseline and isinstance(valor_actual, (int, float)):
                valor_baseline = baseline[key]
                
                if valor_baseline != 0:
                    cambio_porcentual = ((valor_actual - valor_baseline) / valor_baseline) * 100
                    
                    if abs(cambio_porcentual) > (self.tolerance * 100):
                        cambios_significativos.append({
                            'metrica': key,
                            'baseline': valor_baseline,
                            'actual': valor_actual,
                            'cambio_porcentual': cambio_porcentual
                        })
                        print(f"⚠️ Cambio significativo en {key}: {cambio_porcentual:.2f}%")
                    else:
                        print(f"✅ {key}: cambio {cambio_porcentual:.2f}% (dentro de tolerancia)")
                elif valor_actual != 0:
                    # Valor baseline era 0 pero ahora no
                    cambios_significativos.append({
                        'metrica': key,
                        'baseline': valor_baseline,
                        'actual': valor_actual,
                        'cambio_porcentual': float('inf')
                    })
                    print(f"⚠️ Nueva métrica con valor: {key}")
        
        return cambios_significativos
    
    def test_calculo_metricas(self):
        """Test que verifica que se puedan calcular métricas"""
        metricas = self.calcular_metricas_test()
        
        # Verificar que se calcularon métricas mínimas
        assert len(metricas) > 5, f"Se esperaban al menos 6 métricas, se calcularon {len(metricas)}"
        
        # Verificar métricas críticas
        metricas_criticas = ['total_ingresos_test', 'total_costos_operativos_test', 'utilidad_bruta_test']
        for metrica in metricas_criticas:
            assert metrica in metricas, f"Métrica crítica faltante: {metrica}"
        
        print("✅ Test de cálculo de métricas pasó")
        return metricas
    
    def test_regression_vs_baseline(self):
        """Test de regresión principal"""
        # Calcular métricas actuales
        metricas_actuales = self.calcular_metricas_test()
        
        # Cargar baseline
        baseline = self.cargar_baseline()
        
        if baseline is None:
            # Crear baseline inicial
            print("🔧 Creando baseline inicial...")
            self.guardar_baseline(metricas_actuales)
            print("✅ Baseline inicial creado exitosamente")
            return metricas_actuales
        
        # Comparar con baseline
        cambios = self.comparar_con_baseline(metricas_actuales, baseline)
        
        if cambios:
            print(f"\n⚠️ DETECTADOS {len(cambios)} CAMBIOS SIGNIFICATIVOS:")
            for cambio in cambios:
                print(f"   {cambio['metrica']}: {cambio['baseline']} → {cambio['actual']} ({cambio['cambio_porcentual']:.2f}%)")
            
            # Decidir si fallar el test o actualizar baseline
            respuesta = input("\n¿Actualizar baseline con nuevos valores? (y/N): ").lower()
            if respuesta == 'y':
                self.guardar_baseline(metricas_actuales)
                print("✅ Baseline actualizado")
            else:
                raise AssertionError(f"Test de regresión falló: {len(cambios)} cambios significativos")
        else:
            print("✅ No hay cambios significativos detectados")
        
        return metricas_actuales
    
    def test_metricas_sanity_check(self):
        """Test de sanidad para verificar que las métricas tienen sentido"""
        metricas = self.calcular_metricas_test()
        
        # Verificar que los valores son razonables
        if metricas['total_ingresos_test'] > 0:
            assert metricas['utilidad_bruta_test'] <= metricas['total_ingresos_test'], "Utilidad bruta no puede ser mayor que ingresos"
            assert metricas['margen_bruto_test'] <= 100, "Margen bruto no puede ser mayor que 100%"
        
        if metricas['total_costos_fijos_mensual'] > 0:
            assert metricas['num_conceptos_costos_fijos'] == 6, f"Se esperaban 6 conceptos de costos fijos, se encontraron {metricas['num_conceptos_costos_fijos']}"
        
        print("✅ Test de sanidad de métricas pasó")
        return metricas

def run_tests():
    """Ejecuta todos los tests de regresión"""
    test_instance = TestMetricasRegression()
    
    print("🧪 EJECUTANDO TESTS DE REGRESIÓN CON DATOS DE TEST")
    print("=" * 65)
    
    tests = [
        test_instance.test_calculo_metricas,
        test_instance.test_regression_vs_baseline,
        test_instance.test_metricas_sanity_check
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n🔍 Ejecutando: {test.__name__}")
            result = test()
            passed += 1
            print(f"✅ {test.__name__} - PASÓ")
        except Exception as e:
            print(f"❌ {test.__name__} falló: {e}")
            failed += 1
    
    print(f"\n📊 Resumen: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 TODOS LOS TESTS DE REGRESIÓN PASARON")
        return True
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 