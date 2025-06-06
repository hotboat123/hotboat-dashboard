#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cargador de datos específico para tests
Este módulo carga datos estáticos desde tests/test_data/ 
para asegurar consistencia en los tests.
"""

import pandas as pd
import os
import sys
from datetime import datetime

def cargar_datos_test():
    """
    Carga datos estáticos para testing desde tests/test_data/
    Estos datos NO cambian y son específicos para validar funcionalidad.
    
    Returns:
        dict: Diccionario con DataFrames de datos de test
    """
    
    # Directorio base para datos de test
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    
    datos = {}
    
    try:
        print("🧪 === CARGANDO DATOS DE TEST ESTÁTICOS ===")
        
        # ====== RESERVAS ======
        reservas_dir = os.path.join(test_data_dir, 'reservas')
        
        # Reservas principales
        reservas_file = os.path.join(reservas_dir, 'reservas_HotBoat.csv')
        if os.path.exists(reservas_file):
            datos['reservas'] = pd.read_csv(reservas_file)
            print(f"✅ Reservas de test: {len(datos['reservas'])} filas")
        else:
            datos['reservas'] = pd.DataFrame()
            print("⚠️ Archivo de reservas de test no encontrado")
        
        # Pagos
        pagos_file = os.path.join(reservas_dir, 'payments_2025May12.csv')
        if os.path.exists(pagos_file):
            datos['pagos'] = pd.read_csv(pagos_file)
            print(f"✅ Pagos de test: {len(datos['pagos'])} filas")
        else:
            datos['pagos'] = pd.DataFrame()
        
        # Gastos extras
        gastos_file = os.path.join(reservas_dir, 'HotBoat - Pedidos Extras.csv')
        if os.path.exists(gastos_file):
            gastos_extras = pd.read_csv(gastos_file)
            # Simular estructura de gastos completa
            datos['gastos'] = gastos_extras
            print(f"✅ Gastos de test: {len(datos['gastos'])} filas")
        else:
            datos['gastos'] = pd.DataFrame()
        
        # ====== COSTOS FIJOS ======
        # Crear datos simulados de costos fijos
        costos_fijos_data = {
            'concepto': ['Combustible', 'Mantenimiento', 'Seguro', 'Personal', 'Puerto', 'Otros'],
            'monto_mensual': [500000, 200000, 150000, 800000, 100000, 150000],
            'fecha': [datetime(2024, 1, 1)] * 6
        }
        datos['costos_fijos'] = pd.DataFrame(costos_fijos_data)
        print(f"✅ Costos fijos de test: {len(datos['costos_fijos'])} filas")
        
        # ====== INGRESOS ======
        # Calcular ingresos desde reservas si existen
        if not datos['reservas'].empty:
            # Simular estructura de ingresos
            if 'TOTAL AMOUNT' in datos['reservas'].columns and 'fecha_trip' in datos['reservas'].columns:
                ingresos_data = {
                    'fecha': datos['reservas']['fecha_trip'].copy(),
                    'monto': datos['reservas']['TOTAL AMOUNT'].copy(),
                    'tipo': ['reserva'] * len(datos['reservas'])
                }
                datos['ingresos'] = pd.DataFrame(ingresos_data)
                datos['ingresos']['fecha'] = pd.to_datetime(datos['ingresos']['fecha'])
                print(f"✅ Ingresos de test: {len(datos['ingresos'])} filas")
            else:
                # Crear datos de prueba básicos
                ingresos_test = {
                    'fecha': pd.date_range('2024-01-01', periods=100, freq='D'),
                    'monto': [150000] * 100,
                    'tipo': ['test'] * 100
                }
                datos['ingresos'] = pd.DataFrame(ingresos_test)
                print(f"✅ Ingresos de test simulados: {len(datos['ingresos'])} filas")
        else:
            datos['ingresos'] = pd.DataFrame()
        
        # ====== COSTOS OPERATIVOS ======
        # Simular costos operativos
        if not datos['ingresos'].empty:
            costos_op_data = {
                'fecha': datos['ingresos']['fecha'].copy(),
                'monto': [35000] * len(datos['ingresos']),  # ~23% de ingresos
                'concepto': ['operacion'] * len(datos['ingresos'])
            }
            datos['costos_operativos'] = pd.DataFrame(costos_op_data)
            print(f"✅ Costos operativos de test: {len(datos['costos_operativos'])} filas")
        else:
            datos['costos_operativos'] = pd.DataFrame()
        
        # ====== MARKETING ======
        marketing_dir = os.path.join(test_data_dir, 'marketing')
        
        # Archivo principal de marketing
        marketing_file1 = os.path.join(marketing_dir, 'Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv')
        marketing_file2 = os.path.join(marketing_dir, 'Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia.csv')
        
        marketing_data = []
        
        if os.path.exists(marketing_file1):
            df1 = pd.read_csv(marketing_file1)
            marketing_data.append(df1)
            print(f"✅ Marketing file 1: {len(df1)} filas")
        
        if os.path.exists(marketing_file2):
            df2 = pd.read_csv(marketing_file2)
            marketing_data.append(df2)
            print(f"✅ Marketing file 2: {len(df2)} filas")
        
        if marketing_data:
            # Combinar y simular gastos de marketing
            combined_marketing = pd.concat(marketing_data, ignore_index=True)
            
            # Crear datos de gastos marketing
            if not datos['ingresos'].empty:
                gastos_marketing_data = {
                    'fecha': datos['ingresos']['fecha'].iloc[:90].copy(),  # Primeros 90 días
                    'monto': [7500] * 90,  # ~5% de ingresos
                    'plataforma': ['meta'] * 45 + ['google'] * 45
                }
                datos['gastos_marketing'] = pd.DataFrame(gastos_marketing_data)
                print(f"✅ Gastos marketing de test: {len(datos['gastos_marketing'])} filas")
            else:
                datos['gastos_marketing'] = pd.DataFrame()
        else:
            datos['gastos_marketing'] = pd.DataFrame()
        
        print("🧪 === DATOS DE TEST CARGADOS EXITOSAMENTE ===")
        print(f"📊 Resumen:")
        for key, df in datos.items():
            print(f"   {key}: {len(df)} filas")
        
        return datos
        
    except Exception as e:
        print(f"❌ Error al cargar datos de test: {e}")
        # Retornar estructura vacía pero válida
        return {
            'reservas': pd.DataFrame(),
            'pagos': pd.DataFrame(),
            'gastos': pd.DataFrame(),
            'costos_fijos': pd.DataFrame(),
            'ingresos': pd.DataFrame(),
            'costos_operativos': pd.DataFrame(),
            'gastos_marketing': pd.DataFrame()
        }

if __name__ == "__main__":
    # Test de la función
    datos_test = cargar_datos_test()
    print("\n🔍 Estructura de datos de test:")
    for key, df in datos_test.items():
        if not df.empty:
            print(f"{key}: {df.shape} - Columnas: {list(df.columns)[:3]}...")
        else:
            print(f"{key}: DataFrame vacío") 