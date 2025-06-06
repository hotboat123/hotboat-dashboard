#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOTBOAT - Cargador de Datos Consolidado
=======================================

Este módulo maneja toda la carga y procesamiento de datos de HotBoat.
Consolida la funcionalidad de cargar_datos() en un solo lugar optimizado.

Autores: Sistema HotBoat
Fecha: Junio 2025
"""

import pandas as pd
import os
import sys
from datetime import datetime
import numpy as np

def cargar_datos():
    """
    Función principal consolidada para cargar todos los datos de HotBoat
    
    Returns:
        dict: Diccionario con todos los DataFrames cargados y procesados
    """
    
    print("📊 === INICIANDO CARGA DE DATOS HOTBOAT ===")
    
    datos = {}
    
    try:
        # ============================================================================
        # CARGAR DATOS DE RESERVAS
        # ============================================================================
        print("🚤 Cargando datos de reservas...")
        
        # Reservas principales
        reservas_path = "archivos_input/Archivos input reservas/reservas_HotBoat.csv"
        if os.path.exists(reservas_path):
            datos['reservas'] = pd.read_csv(reservas_path)
            print(f"   ✅ Reservas cargadas: {len(datos['reservas'])} filas")
        
        # Pagos
        pagos_path = "archivos_input/Archivos input reservas/payments_2025May12.csv"
        if os.path.exists(pagos_path):
            datos['pagos'] = pd.read_csv(pagos_path)
            print(f"   ✅ Pagos cargados: {len(datos['pagos'])} filas")
        
        # Gastos extras
        gastos_path = "archivos_input/Archivos input reservas/HotBoat - Pedidos Extras.csv"
        if os.path.exists(gastos_path):
            datos['gastos'] = pd.read_csv(gastos_path)
            print(f"   ✅ Gastos cargados: {len(datos['gastos'])} filas")
        
        # ============================================================================
        # CARGAR DATOS FINANCIEROS
        # ============================================================================
        print("💰 Cargando datos financieros...")
        
        # Cargar múltiples archivos de costos operativos
        costos_dir = "archivos_input/archivos_input_costos"
        costos_operativos = []
        
        if os.path.exists(costos_dir):
            for filename in os.listdir(costos_dir):
                if filename.endswith(('.xlsx', '.xls', '.csv')):
                    file_path = os.path.join(costos_dir, filename)
                    try:
                        if filename.endswith('.csv'):
                            df = pd.read_csv(file_path)
                        else:
                            df = pd.read_excel(file_path)
                        
                        # Estandarizar columnas
                        df = estandarizar_columnas_financieras(df, filename)
                        if not df.empty:
                            costos_operativos.append(df)
                            
                    except Exception as e:
                        print(f"   ⚠️ Error cargando {filename}: {e}")
        
        if costos_operativos:
            datos['costos_operativos'] = pd.concat(costos_operativos, ignore_index=True)
            print(f"   ✅ Costos operativos cargados: {len(datos['costos_operativos'])} filas")
        
        # ============================================================================
        # CARGAR DATOS DE MARKETING
        # ============================================================================
        print("📱 Cargando datos de marketing...")
        
        marketing_dir = "archivos_input/archivos input marketing"
        marketing_data = []
        
        if os.path.exists(marketing_dir):
            for filename in os.listdir(marketing_dir):
                if filename.endswith('.csv'):
                    file_path = os.path.join(marketing_dir, filename)
                    try:
                        df = pd.read_csv(file_path)
                        df = procesar_datos_marketing(df, filename)
                        if not df.empty:
                            marketing_data.append(df)
                    except Exception as e:
                        print(f"   ⚠️ Error cargando {filename}: {e}")
        
        if marketing_data:
            datos['gastos_marketing'] = pd.concat(marketing_data, ignore_index=True)
            print(f"   ✅ Gastos marketing cargados: {len(datos['gastos_marketing'])} filas")
        
        # ============================================================================
        # PROCESAR Y CREAR DATASETS DERIVADOS
        # ============================================================================
        print("🔄 Procesando datos derivados...")
        
        # Crear dataset de ingresos desde reservas y pagos
        datos['ingresos'] = crear_dataset_ingresos(datos)
        if 'ingresos' in datos:
            print(f"   ✅ Ingresos procesados: {len(datos['ingresos'])} filas")
        
        # Crear dataset de costos fijos
        datos['costos_fijos'] = crear_dataset_costos_fijos()
        if 'costos_fijos' in datos:
            print(f"   ✅ Costos fijos cargados: {len(datos['costos_fijos'])} filas")
        
        # ============================================================================
        # VALIDAR Y LIMPIAR DATOS
        # ============================================================================
        print("🧹 Validando y limpiando datos...")
        
        for key, df in datos.items():
            if isinstance(df, pd.DataFrame):
                datos[key] = limpiar_dataframe(df, key)
        
        print("✅ === CARGA DE DATOS COMPLETADA EXITOSAMENTE ===")
        
        return datos
        
    except Exception as e:
        print(f"❌ Error en la carga de datos: {e}")
        return {}

def estandarizar_columnas_financieras(df, filename):
    """
    Estandariza las columnas de archivos financieros
    
    Args:
        df (pd.DataFrame): DataFrame original
        filename (str): Nombre del archivo para contexto
        
    Returns:
        pd.DataFrame: DataFrame con columnas estandarizadas
    """
    
    if df.empty:
        return df
    
    # Mapeo de columnas comunes
    column_mapping = {
        'amount': 'monto',
        'fecha': 'fecha',
        'date': 'fecha',
        'description': 'descripcion',
        'concepto': 'descripcion',
        'tipo': 'categoria',
        'type': 'categoria'
    }
    
    # Renombrar columnas
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    # Asegurar columnas mínimas requeridas
    required_columns = ['monto', 'fecha', 'descripcion']
    for col in required_columns:
        if col not in df.columns:
            if col == 'monto':
                # Buscar columnas numéricas que podrían ser montos
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df['monto'] = df[numeric_cols[0]]
                else:
                    df['monto'] = 0
            elif col == 'fecha':
                df['fecha'] = datetime.now()
            elif col == 'descripcion':
                df['descripcion'] = filename
    
    # Agregar metadatos
    df['fuente'] = filename
    df['categoria'] = determinar_categoria_financiera(filename)
    
    return df

def procesar_datos_marketing(df, filename):
    """
    Procesa datos específicos de marketing
    
    Args:
        df (pd.DataFrame): DataFrame de marketing
        filename (str): Nombre del archivo
        
    Returns:
        pd.DataFrame: DataFrame procesado
    """
    
    if df.empty:
        return df
    
    # Mapeo específico para marketing
    marketing_mapping = {
        'Cost per result': 'costo_por_resultado',
        'Amount spent (CLP)': 'monto',
        'Fecha de inicio': 'fecha',
        'Campaign name': 'campana',
        'Ad set name': 'conjunto_anuncios',
        'Clicks (all)': 'clicks',
        'Impressions': 'impresiones',
        'CTR (all)': 'ctr'
    }
    
    # Renombrar columnas de marketing
    for old_col, new_col in marketing_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})
    
    # Procesar datos específicos
    if 'monto' in df.columns:
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce').fillna(0)
    
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Agregar metadatos
    df['fuente'] = filename
    df['tipo'] = 'marketing'
    
    return df

def crear_dataset_ingresos(datos):
    """
    Crea el dataset de ingresos consolidado desde reservas y pagos
    
    Args:
        datos (dict): Datos cargados
        
    Returns:
        pd.DataFrame: Dataset de ingresos
    """
    
    ingresos_list = []
    
    # Ingresos desde reservas
    if 'reservas' in datos and not datos['reservas'].empty:
        reservas_df = datos['reservas'].copy()
        
        # Buscar columna de monto
        monto_cols = [col for col in reservas_df.columns if 'precio' in col.lower() or 'monto' in col.lower() or 'total' in col.lower()]
        fecha_cols = [col for col in reservas_df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        
        if monto_cols and fecha_cols:
            ingresos_reservas = pd.DataFrame({
                'monto': pd.to_numeric(reservas_df[monto_cols[0]], errors='coerce'),
                'fecha': pd.to_datetime(reservas_df[fecha_cols[0]], errors='coerce'),
                'descripcion': 'Ingreso por reserva',
                'tipo': 'reserva',
                'fuente': 'reservas'
            })
            ingresos_list.append(ingresos_reservas)
    
    # Ingresos desde pagos
    if 'pagos' in datos and not datos['pagos'].empty:
        pagos_df = datos['pagos'].copy()
        
        # Buscar columnas relevantes
        monto_cols = [col for col in pagos_df.columns if 'amount' in col.lower() or 'monto' in col.lower()]
        fecha_cols = [col for col in pagos_df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        
        if monto_cols and fecha_cols:
            ingresos_pagos = pd.DataFrame({
                'monto': pd.to_numeric(pagos_df[monto_cols[0]], errors='coerce'),
                'fecha': pd.to_datetime(pagos_df[fecha_cols[0]], errors='coerce'),
                'descripcion': 'Pago recibido',
                'tipo': 'pago',
                'fuente': 'pagos'
            })
            ingresos_list.append(ingresos_pagos)
    
    # Consolidar ingresos
    if ingresos_list:
        ingresos = pd.concat(ingresos_list, ignore_index=True)
        ingresos = ingresos.dropna(subset=['monto', 'fecha'])
        ingresos = ingresos[ingresos['monto'] > 0]
        return ingresos
    
    return pd.DataFrame()

def crear_dataset_costos_fijos():
    """
    Crea dataset de costos fijos predeterminados
    
    Returns:
        pd.DataFrame: Dataset de costos fijos
    """
    
    costos_fijos = [
        {'descripcion': 'Seguros embarcaciones', 'monto': 500000, 'frecuencia': 'mensual'},
        {'descripcion': 'Mantención general', 'monto': 300000, 'frecuencia': 'mensual'},
        {'descripcion': 'Licencias y permisos', 'monto': 150000, 'frecuencia': 'mensual'},
        {'descripcion': 'Personal fijo', 'monto': 800000, 'frecuencia': 'mensual'},
        {'descripcion': 'Combustible base', 'monto': 400000, 'frecuencia': 'mensual'},
        {'descripcion': 'Comunicaciones y software', 'monto': 100000, 'frecuencia': 'mensual'}
    ]
    
    df_costos_fijos = pd.DataFrame(costos_fijos)
    df_costos_fijos['fecha'] = datetime.now()
    df_costos_fijos['tipo'] = 'costo_fijo'
    df_costos_fijos['fuente'] = 'sistema'
    
    return df_costos_fijos

def limpiar_dataframe(df, nombre):
    """
    Limpia y valida un DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame a limpiar
        nombre (str): Nombre del dataset para logging
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    
    if df.empty:
        return df
    
    original_rows = len(df)
    
    # Eliminar filas completamente vacías
    df = df.dropna(how='all')
    
    # Convertir fechas si existen
    date_columns = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Convertir montos si existen
    monto_columns = [col for col in df.columns if 'monto' in col.lower() or 'amount' in col.lower()]
    for col in monto_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Eliminar duplicados
    df = df.drop_duplicates()
    
    cleaned_rows = len(df)
    if original_rows != cleaned_rows:
        print(f"   🧹 {nombre}: {original_rows} → {cleaned_rows} filas después de limpieza")
    
    return df

def determinar_categoria_financiera(filename):
    """
    Determina la categoría financiera basada en el nombre del archivo
    
    Args:
        filename (str): Nombre del archivo
        
    Returns:
        str: Categoría determinada
    """
    
    filename_lower = filename.lower()
    
    if any(word in filename_lower for word in ['marketing', 'publicidad', 'ads']):
        return 'marketing'
    elif any(word in filename_lower for word in ['banco', 'cuenta', 'cartola']):
        return 'bancario'
    elif any(word in filename_lower for word in ['mercadopago', 'pago']):
        return 'pagos'
    elif any(word in filename_lower for word in ['gasto', 'expense']):
        return 'gastos'
    elif any(word in filename_lower for word in ['ingreso', 'income', 'venta']):
        return 'ingresos'
    else:
        return 'otros'

if __name__ == "__main__":
    # Test de carga de datos
    datos = cargar_datos()
    print(f"\n📊 Resumen de datos cargados:")
    for key, df in datos.items():
        if isinstance(df, pd.DataFrame):
            print(f"   {key}: {len(df)} registros") 