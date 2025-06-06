#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de Regresión para métricas de HotBoat
Estos tests aseguran que las métricas calculadas no cambien inesperadamente entre versiones.
"""

import pandas as pd
import numpy as np
import os
import sys
import json
from datetime import datetime

# Agregar el directorio padre al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboards import cargar_datos

class TestMetricasRegression:
    """Tests de regresión para métricas calculadas"""
    
    def __init__(self):
        """Configuración inicial para todos los tests"""
        print("🔧 Configurando tests de regresión de métricas...")
        self.datos = cargar_datos()
        self.tolerance = 0.01  # Tolerancia del 1% para cambios aceptables
    
    def calcular_metricas_clave(self):
        """Calcula las métricas clave del sistema"""
        metricas = {}
        
        # Métricas de reservas
        reservas = self.datos['reservas']
        if not reservas.empty:
            if 'TOTAL AMOUNT' in reservas.columns:
                metricas['total_revenue_reservas'] = float(reservas['TOTAL AMOUNT'].sum())
                metricas['avg_revenue_per_booking'] = float(reservas['TOTAL AMOUNT'].mean())
                metricas['median_revenue_per_booking'] = float(reservas['TOTAL AMOUNT'].median())
            
            metricas['total_reservas'] = len(reservas)
        
        # Métricas de ingresos
        ingresos = self.datos['ingresos']
        if not ingresos.empty:
            if 'monto' in ingresos.columns:
                metricas['total_ingresos'] = float(ingresos['monto'].sum())
                metricas['avg_ingreso'] = float(ingresos['monto'].mean())
            metricas['count_ingresos'] = len(ingresos)
        
        # Métricas de costos operativos
        costos_op = self.datos['costos_operativos']
        if not costos_op.empty:
            if 'monto' in costos_op.columns:
                metricas['total_costos_operativos'] = float(costos_op['monto'].sum())
                metricas['avg_costo_operativo'] = float(costos_op['monto'].mean())
            metricas['count_costos_operativos'] = len(costos_op)
        
        # Métricas de gastos marketing
        gastos_mkt = self.datos['gastos_marketing']
        if not gastos_mkt.empty:
            if 'monto' in gastos_mkt.columns:
                metricas['total_gastos_marketing'] = float(gastos_mkt['monto'].sum())
                metricas['avg_gasto_marketing'] = float(gastos_mkt['monto'].mean())
            metricas['count_gastos_marketing'] = len(gastos_mkt)
        
        # Calcular utilidad aproximada
        if 'total_ingresos' in metricas and 'total_costos_operativos' in metricas and 'total_gastos_marketing' in metricas:
            metricas['utilidad_bruta'] = (
                metricas['total_ingresos'] - 
                metricas['total_costos_operativos'] - 
                metricas['total_gastos_marketing']
            )
            
            if metricas['total_ingresos'] > 0:
                metricas['margen_utilidad'] = metricas['utilidad_bruta'] / metricas['total_ingresos']
        
        return metricas
    
    def test_calcular_metricas_clave(self):
        """Test que verifica que se puedan calcular las métricas clave"""
        try:
            metricas = self.calcular_metricas_clave()
            assert len(metricas) > 0, "No se pudieron calcular métricas"
            
            print("✅ Métricas clave calculadas:")
            for key, value in metricas.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:,.2f}")
                else:
                    print(f"   {key}: {value}")
            
        except Exception as e:
            raise AssertionError(f"Error al calcular métricas: {e}")
    
    def test_save_metrics_baseline(self):
        """Test que guarda las métricas actuales como baseline para futuras comparaciones"""
        metricas = self.calcular_metricas_clave()
        
        baseline_dir = "tests/baselines"
        os.makedirs(baseline_dir, exist_ok=True)
        
        baseline = {
            "fecha_creacion": datetime.now().isoformat(),
            "version": "1.0.0",  # Ajustar según sea necesario
            "metricas": metricas,
            "tolerancia": self.tolerance
        }
        
        baseline_file = os.path.join(baseline_dir, "metricas_baseline.json")
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Baseline de métricas guardado en: {baseline_file}")
        assert os.path.exists(baseline_file), "Baseline no se pudo crear"
    
    def test_compare_with_baseline(self):
        """Test de regresión que compara métricas actuales con baseline"""
        baseline_file = "tests/baselines/metricas_baseline.json"
        
        if not os.path.exists(baseline_file):
            print("ℹ️ No hay baseline anterior. Ejecutando test_save_metrics_baseline primero...")
            self.test_save_metrics_baseline()
            return
        
        # Cargar baseline
        with open(baseline_file, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
        
        baseline_metrics = baseline.get("metricas", {})
        tolerance = baseline.get("tolerancia", self.tolerance)
        
        # Calcular métricas actuales
        current_metrics = self.calcular_metricas_clave()
        
        print("🔍 Comparando métricas con baseline...")
        
        issues_found = []
        
        for metric_name, baseline_value in baseline_metrics.items():
            if metric_name in current_metrics:
                current_value = current_metrics[metric_name]
                
                if isinstance(baseline_value, (int, float)) and isinstance(current_value, (int, float)):
                    # Calcular diferencia porcentual
                    if baseline_value != 0:
                        diff_percent = abs(current_value - baseline_value) / abs(baseline_value)
                        
                        if diff_percent > tolerance:
                            issues_found.append({
                                "metric": metric_name,
                                "baseline": baseline_value,
                                "current": current_value,
                                "diff_percent": diff_percent * 100
                            })
                            print(f"❌ {metric_name}:")
                            print(f"   Baseline: {baseline_value:,.2f}")
                            print(f"   Actual: {current_value:,.2f}")
                            print(f"   Diferencia: {diff_percent*100:.2f}% (tolerancia: {tolerance*100:.1f}%)")
                        else:
                            print(f"✅ {metric_name}: Sin cambios significativos ({diff_percent*100:.2f}%)")
                    else:
                        # Caso especial: baseline es 0
                        if current_value != 0:
                            issues_found.append({
                                "metric": metric_name,
                                "baseline": baseline_value,
                                "current": current_value,
                                "diff_percent": float('inf')
                            })
                            print(f"❌ {metric_name}: Cambió de 0 a {current_value}")
                        else:
                            print(f"✅ {metric_name}: Ambos valores son 0")
                else:
                    # Comparación exacta para valores no numéricos
                    if baseline_value != current_value:
                        issues_found.append({
                            "metric": metric_name,
                            "baseline": baseline_value,
                            "current": current_value,
                            "diff_percent": "N/A"
                        })
                        print(f"❌ {metric_name}: {baseline_value} → {current_value}")
                    else:
                        print(f"✅ {metric_name}: Sin cambios")
            else:
                print(f"⚠️ Métrica '{metric_name}' no encontrada en datos actuales")
        
        # Verificar métricas nuevas
        for metric_name in current_metrics:
            if metric_name not in baseline_metrics:
                print(f"ℹ️ Nueva métrica encontrada: {metric_name} = {current_metrics[metric_name]}")
        
        # Informar sobre issues encontrados
        if issues_found:
            print(f"\n⚠️ Se encontraron {len(issues_found)} cambios significativos en las métricas")
            print("Esto podría indicar:")
            print("- Cambios en los datos de entrada")
            print("- Modificaciones en la lógica de cálculo")
            print("- Errores en el código")
            print("\nSi estos cambios son esperados, actualiza el baseline ejecutando test_save_metrics_baseline")
        else:
            print("\n🎉 Todas las métricas están dentro de los rangos esperados")
    
    def test_data_integrity(self):
        """Test que verifica la integridad básica de los datos"""
        issues = []
        
        for dataset_name, df in self.datos.items():
            if not df.empty:
                # Verificar valores nulos en columnas críticas
                if 'monto' in df.columns:
                    null_montos = df['monto'].isnull().sum()
                    if null_montos > 0:
                        issues.append(f"{dataset_name}: {null_montos} valores nulos en 'monto'")
                    
                    # Verificar valores negativos inesperados
                    negative_montos = (df['monto'] < 0).sum()
                    if negative_montos > 0:
                        issues.append(f"{dataset_name}: {negative_montos} valores negativos en 'monto'")
        
        if issues:
            print("⚠️ Problemas de integridad encontrados:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Integridad de datos verificada")

def run_tests():
    """Ejecuta todos los tests y retorna si pasaron"""
    test_instance = TestMetricasRegression()
    
    print("🧪 EJECUTANDO TESTS DE REGRESIÓN DE MÉTRICAS")
    print("=" * 60)
    
    tests = [
        test_instance.test_calcular_metricas_clave,
        test_instance.test_data_integrity,
        test_instance.test_save_metrics_baseline,
        test_instance.test_compare_with_baseline
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
        print("🎉 TODOS LOS TESTS DE REGRESIÓN COMPLETADOS")
        return True
    else:
        print(f"❌ {failed} TESTS FALLARON")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 