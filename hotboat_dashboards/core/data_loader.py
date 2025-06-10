#!/usr/bin/env python3
"""
🚤 HOTBOAT - CARGADOR DE DATOS OPTIMIZADO
=========================================

Módulo centralizado para carga de datos de todos los dashboards.
Mantiene la funcionalidad exacta de la versión original.

Autor: Sistema HotBoat Optimizado
Versión: 2.0
"""

import pandas as pd
import os
from pathlib import Path

def cargar_datos_reservas():
    """Carga datos de reservas y pagos"""
    print("🚤 Cargando datos de reservas...")
    
    try:
        # Cargar reservas
        reservas_df = pd.read_csv('archivos_output/reservas_procesadas.csv')
        print(f"   ✅ Reservas cargadas: {len(reservas_df)} filas")
        
        # Cargar pagos/ingresos
        try:
            ingresos_df = pd.read_csv('archivos_output/ingresos_procesados.csv')
            print(f"   ✅ Ingresos cargados: {len(ingresos_df)} filas")
        except:
            # Intentar cargar desde pagos
            ingresos_df = pd.read_csv('archivos_output/pagos_procesados.csv')
            print(f"   ✅ Pagos cargados: {len(ingresos_df)} filas")
        
        # Cargar gastos operacionales
        try:
            gastos_df = pd.read_csv('archivos_output/gastos_procesados.csv')
            print(f"   ✅ Gastos cargados: {len(gastos_df)} filas")
        except:
            gastos_df = pd.DataFrame()
            print("   ⚠️ No se encontraron gastos procesados")
        
        return {
            'reservas': reservas_df,
            'ingresos': ingresos_df,
            'gastos': gastos_df
        }
        
    except Exception as e:
        print(f"   ❌ Error cargando datos de reservas: {e}")
        return None

def cargar_datos_utilidad():
    """Carga datos específicos para el dashboard de utilidad"""
    print("💰 Cargando datos de utilidad...")
    
    try:
        # Cargar ingresos
        ingresos_df = pd.read_csv('archivos_output/ingresos_procesados.csv')
        print(f"   ✅ Ingresos cargados: {len(ingresos_df)} filas")
        
        # Cargar costos operativos
        costos_df = pd.read_csv('archivos_output/costos_operativos_procesados.csv')
        print(f"   ✅ Costos operativos cargados: {len(costos_df)} filas")
        
        # Cargar gastos marketing
        marketing_df = pd.read_csv('archivos_output/gastos_marketing_procesados.csv')
        print(f"   ✅ Gastos marketing cargados: {len(marketing_df)} filas")
        
        # Cargar costos fijos
        try:
            costos_fijos_df = pd.read_csv('archivos_output/costos_fijos_procesados.csv')
            print(f"   ✅ Costos fijos cargados: {len(costos_fijos_df)} filas")
        except:
            costos_fijos_df = pd.DataFrame()
            print("   ⚠️ No se encontraron costos fijos")
        
        return {
            'ingresos': ingresos_df,
            'costos_operativos': costos_df,
            'gastos_marketing': marketing_df,
            'costos_fijos': costos_fijos_df
        }
        
    except Exception as e:
        print(f"   ❌ Error cargando datos de utilidad: {e}")
        return None

def cargar_datos_marketing():
    """Carga datos específicos para el dashboard de marketing"""
    print("📱 Cargando datos de marketing...")
    
    try:
        # Cargar archivo CON región
        archivo_con_region = 'archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv'
        print(f"Cargando archivo CON región: {archivo_con_region}")
        df_con_region = pd.read_csv(archivo_con_region)
        print(f"Archivo CON región cargado. Dimensiones: {df_con_region.shape}")
        
        # Cargar archivo SIN región
        archivo_sin_region = 'archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia.csv'
        print(f"Cargando archivo SIN región: {archivo_sin_region}")
        df_sin_region = pd.read_csv(archivo_sin_region)
        print(f"Archivo SIN región cargado. Dimensiones: {df_sin_region.shape}")
        
        print("Ambos archivos procesados exitosamente")
        print(f"✅ Datos CON región: {len(df_con_region)} filas")
        print(f"✅ Datos SIN región: {len(df_sin_region)} filas")
        
        return {
            'con_region': df_con_region,
            'sin_region': df_sin_region
        }
        
    except Exception as e:
        print(f"   ❌ Error cargando datos de marketing: {e}")
        return None

def verificar_archivos_datos():
    """Verifica que existan los archivos de datos necesarios"""
    archivos_necesarios = [
        'archivos_output/reservas_procesadas.csv',
        'archivos_output/ingresos_procesados.csv',
        'archivos_output/costos_operativos_procesados.csv',
        'archivos_output/gastos_marketing_procesados.csv'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print("⚠️ Archivos faltantes:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        return False
    
    return True 