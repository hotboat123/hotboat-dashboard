#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏦 ANÁLISIS DE FECHAS - BANCO CHILE MOVIMIENTOS NO FACTURADOS
============================================================

Este script analiza todos los archivos de Saldo_y_Mov_No_Facturado del Banco Chile
para identificar:
- Rango de fechas de cada archivo
- Gaps en la cobertura temporal
- Estadísticas por archivo

Uso:
    python analizar_fechas_no_facturados.py
"""

import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import glob

# Configurar UTF-8 para que los emojis funcionen siempre
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Para versiones de Python < 3.7
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Importar funciones necesarias
from funciones.funciones import (
    ver_si_es_nacional_no_facturado, 
    leer_excel_mov_no_facturados_nacional, 
    leer_excel_mov_no_facturados_internacional
)

def analizar_archivo_mov_no_facturado(ruta_archivo, valor_aproximado_dolar=950):
    """
    Analiza un archivo de movimientos no facturados y extrae información de fechas.
    """
    try:
        nombre_archivo = os.path.basename(ruta_archivo)
        print(f"\n📄 Analizando: {nombre_archivo}")
        
        # Determinar si es nacional o internacional
        es_nacional = ver_si_es_nacional_no_facturado(ruta_archivo)
        tipo = "Nacional" if es_nacional else "Internacional"
        print(f"   Tipo: {tipo}")
        
        # Leer el archivo según su tipo
        if es_nacional:
            df = leer_excel_mov_no_facturados_nacional(ruta_archivo)
        else:
            df = leer_excel_mov_no_facturados_internacional(ruta_archivo, valor_aproximado_dolar)
        
        if df is None or df.empty:
            print("   ❌ Archivo vacío o error en lectura")
            return None
        
        # Convertir fechas
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df_fechas = df.dropna(subset=['Fecha'])
        
        if df_fechas.empty:
            print("   ❌ No se encontraron fechas válidas")
            return None
        
        # Estadísticas de fechas
        fecha_min = df_fechas['Fecha'].min()
        fecha_max = df_fechas['Fecha'].max()
        total_registros = len(df_fechas)
        dias_unicos = df_fechas['Fecha'].dt.date.nunique()
        
        print(f"   📅 Fecha mínima: {fecha_min.strftime('%Y-%m-%d')}")
        print(f"   📅 Fecha máxima: {fecha_max.strftime('%Y-%m-%d')}")
        print(f"   📊 Total registros: {total_registros}")
        print(f"   📊 Días únicos: {dias_unicos}")
        
        # Calcular duración en días
        duracion = (fecha_max - fecha_min).days + 1
        print(f"   ⏱️  Duración: {duracion} días")
        
        return {
            'archivo': nombre_archivo,
            'tipo': tipo,
            'fecha_min': fecha_min,
            'fecha_max': fecha_max,
            'total_registros': total_registros,
            'dias_unicos': dias_unicos,
            'duracion_dias': duracion
        }
        
    except Exception as e:
        print(f"   ❌ Error procesando {nombre_archivo}: {str(e)}")
        return None

def identificar_gaps_no_facturados(archivos_info):
    """
    Identifica gaps en la cobertura temporal entre archivos.
    """
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DE GAPS EN COBERTURA TEMPORAL - NO FACTURADOS")
    print("="*60)
    
    if not archivos_info:
        print("❌ No hay información de archivos para analizar")
        return
    
    # Ordenar por fecha mínima
    archivos_ordenados = sorted(archivos_info, key=lambda x: x['fecha_min'])
    
    print("\n📋 ARCHIVOS ORDENADOS POR FECHA:")
    for i, info in enumerate(archivos_ordenados, 1):
        print(f"{i:2d}. {info['archivo']:<40} | {info['fecha_min'].strftime('%Y-%m-%d')} → {info['fecha_max'].strftime('%Y-%m-%d')} | {info['tipo']}")
    
    # Buscar gaps
    print("\n🔍 ANÁLISIS DE GAPS:")
    gaps_encontrados = []
    
    for i in range(len(archivos_ordenados) - 1):
        archivo_actual = archivos_ordenados[i]
        archivo_siguiente = archivos_ordenados[i + 1]
        
        fecha_fin_actual = archivo_actual['fecha_max']
        fecha_inicio_siguiente = archivo_siguiente['fecha_min']
        
        # Calcular diferencia (considerando que el día siguiente debería ser continuo)
        diferencia = (fecha_inicio_siguiente - fecha_fin_actual).days
        
        if diferencia > 1:  # Hay un gap
            gap_dias = diferencia - 1
            fecha_gap_inicio = fecha_fin_actual + timedelta(days=1)
            fecha_gap_fin = fecha_inicio_siguiente - timedelta(days=1)
            
            gap_info = {
                'archivo_anterior': archivo_actual['archivo'],
                'archivo_siguiente': archivo_siguiente['archivo'],
                'fecha_gap_inicio': fecha_gap_inicio,
                'fecha_gap_fin': fecha_gap_fin,
                'dias_faltantes': gap_dias
            }
            gaps_encontrados.append(gap_info)
            
            print(f"❗ GAP ENCONTRADO:")
            print(f"   Entre: {archivo_actual['archivo']} → {archivo_siguiente['archivo']}")
            print(f"   Período faltante: {fecha_gap_inicio.strftime('%Y-%m-%d')} → {fecha_gap_fin.strftime('%Y-%m-%d')}")
            print(f"   Días faltantes: {gap_dias}")
            print()
        elif diferencia == 1:
            print(f"✅ Continuidad perfecta entre {archivo_actual['archivo']} y {archivo_siguiente['archivo']}")
        elif diferencia <= 0:
            solapamiento = abs(diferencia) + 1
            print(f"🔄 Solapamiento de {solapamiento} días entre {archivo_actual['archivo']} y {archivo_siguiente['archivo']}")
    
    return gaps_encontrados

def mostrar_resumen_no_facturados(archivos_info):
    """
    Muestra un resumen general de la cobertura temporal.
    """
    print("\n" + "="*60)
    print("📊 RESUMEN GENERAL - MOVIMIENTOS NO FACTURADOS")
    print("="*60)
    
    if not archivos_info:
        print("❌ No hay información para mostrar")
        return
    
    fecha_global_min = min(info['fecha_min'] for info in archivos_info)
    fecha_global_max = max(info['fecha_max'] for info in archivos_info)
    total_archivos = len(archivos_info)
    total_registros = sum(info['total_registros'] for info in archivos_info)
    
    nacionales = [info for info in archivos_info if info['tipo'] == 'Nacional']
    internacionales = [info for info in archivos_info if info['tipo'] == 'Internacional']
    
    print(f"📅 Período total cubierto: {fecha_global_min.strftime('%Y-%m-%d')} → {fecha_global_max.strftime('%Y-%m-%d')}")
    print(f"📊 Total archivos analizados: {total_archivos}")
    print(f"📊 Total registros: {total_registros}")
    print(f"🇨🇱 Archivos nacionales: {len(nacionales)}")
    print(f"🌍 Archivos internacionales: {len(internacionales)}")
    
    duracion_total = (fecha_global_max - fecha_global_min).days + 1
    print(f"⏱️  Duración total: {duracion_total} días")
    
    # Mostrar última fecha más claramente
    archivo_mas_reciente = max(archivos_info, key=lambda x: x['fecha_max'])
    print(f"\n🎯 ÚLTIMA FECHA REGISTRADA: {fecha_global_max.strftime('%Y-%m-%d')}")
    print(f"   Archivo: {archivo_mas_reciente['archivo']}")

def main():
    """
    Función principal que ejecuta el análisis completo.
    """
    print("🏦 ANÁLISIS DE FECHAS - BANCO CHILE MOVIMIENTOS NO FACTURADOS")
    print("=" * 70)
    
    directorio_input = 'archivos_input/archivos_input_costos'
    
    # Buscar todos los archivos de Saldo_y_Mov_No_Facturado
    patron = os.path.join(directorio_input, 'Saldo_y_Mov_No_Facturado*.xls')
    archivos_no_facturados = glob.glob(patron)
    
    if not archivos_no_facturados:
        print(f"❌ No se encontraron archivos Saldo_y_Mov_No_Facturado en {directorio_input}")
        return
    
    print(f"📁 Directorio: {directorio_input}")
    print(f"📄 Archivos encontrados: {len(archivos_no_facturados)}")
    
    # Analizar cada archivo
    archivos_info = []
    for archivo in sorted(archivos_no_facturados):
        info = analizar_archivo_mov_no_facturado(archivo)
        if info:
            archivos_info.append(info)
    
    # Mostrar resumen general
    mostrar_resumen_no_facturados(archivos_info)
    
    # Identificar gaps
    gaps = identificar_gaps_no_facturados(archivos_info)
    
    if gaps:
        print(f"\n⚠️  TOTAL GAPS ENCONTRADOS: {len(gaps)}")
        total_dias_faltantes = sum(gap['dias_faltantes'] for gap in gaps)
        print(f"⚠️  TOTAL DÍAS FALTANTES: {total_dias_faltantes}")
    else:
        print("\n✅ No se encontraron gaps en la cobertura temporal")
    
    print("\n🎉 Análisis completado")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Análisis interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        sys.exit(1) 