#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANALIZADOR DE TIPOS DE ANUNCIOS
==================================

Este script analiza los datos de marketing para identificar qué anuncios
están siendo clasificados como "Otro" y por qué.
"""

import pandas as pd
import os

def analizar_tipos_anuncios():
    """Analiza los tipos de anuncios en los datos de marketing"""
    
    # Cargar archivo SIN región (6)
    archivo_sin_region = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv"
    
    if not os.path.exists(archivo_sin_region):
        print(f"❌ No se encuentra el archivo: {archivo_sin_region}")
        return
    
    print("📊 Analizando tipos de anuncios...")
    print("=" * 60)
    
    # Cargar datos
    df = pd.read_csv(archivo_sin_region)
    print(f"✅ Datos cargados: {len(df)} filas")
    
    # Mostrar columnas disponibles
    print(f"\n📋 Columnas disponibles:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    # Verificar si existe la columna de nombre del anuncio
    if 'Nombre del anuncio' not in df.columns:
        print("\n❌ No se encuentra la columna 'Nombre del anuncio'")
        print("Columnas disponibles:")
        for col in df.columns:
            print(f"   - {col}")
        return
    
    # Obtener nombres únicos de anuncios
    nombres_anuncios = df['Nombre del anuncio'].unique()
    print(f"\n📢 Nombres únicos de anuncios ({len(nombres_anuncios)}):")
    for i, nombre in enumerate(nombres_anuncios, 1):
        print(f"   {i}. {nombre}")
    
    # Aplicar la clasificación actual
    def clasificar_anuncio(x):
        nombre = str(x).lower()
        if 'explicando servicio' in nombre:
            return 'Video explicativo'
        elif 'parejas amor' in nombre:
            return 'Video parejas amor'
        elif 'parejas dcto' in nombre or 'pareja dcto' in nombre:
            return 'Video parejas dcto'
        elif 'Lluvia' in nombre or 'lluvia' in nombre:
            return 'Video Lluvia'
        else:
            return 'Otro'
    
    df['Tipo_Anuncio'] = df['Nombre del anuncio'].apply(clasificar_anuncio)
    
    # Analizar clasificación
    print(f"\n📊 CLASIFICACIÓN ACTUAL:")
    clasificacion = df['Tipo_Anuncio'].value_counts()
    for tipo, cantidad in clasificacion.items():
        print(f"   {tipo}: {cantidad} anuncios")
    
    # Mostrar anuncios clasificados como "Otro"
    otros_anuncios = df[df['Tipo_Anuncio'] == 'Otro']['Nombre del anuncio'].unique()
    if len(otros_anuncios) > 0:
        print(f"\n❓ ANUNCIOS CLASIFICADOS COMO 'OTRO' ({len(otros_anuncios)}):")
        for i, nombre in enumerate(otros_anuncios, 1):
            print(f"   {i}. {nombre}")
        
        print(f"\n💡 SUGERENCIAS PARA MEJORAR LA CLASIFICACIÓN:")
        print("   - Revisar los nombres de anuncios que aparecen como 'Otro'")
        print("   - Agregar más condiciones en la función clasificar_anuncio()")
        print("   - Considerar usar expresiones regulares para mayor flexibilidad")
    else:
        print(f"\n✅ ¡Excelente! No hay anuncios clasificados como 'Otro'")
    
    # Mostrar estadísticas por tipo
    print(f"\n📈 ESTADÍSTICAS POR TIPO DE ANUNCIO:")
    for tipo in df['Tipo_Anuncio'].unique():
        df_tipo = df[df['Tipo_Anuncio'] == tipo]
        gasto_total = df_tipo['Importe gastado (CLP)'].sum()
        impresiones_total = df_tipo['Impresiones'].sum()
        clics_total = df_tipo['Clics en el enlace'].sum()
        
        print(f"\n   {tipo}:")
        print(f"     - Cantidad de registros: {len(df_tipo)}")
        print(f"     - Gasto total: ${gasto_total:,.0f}")
        print(f"     - Impresiones totales: {impresiones_total:,.0f}")
        print(f"     - Clics totales: {clics_total:,.0f}")

if __name__ == '__main__':
    analizar_tipos_anuncios() 