#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📦 EXTRACTOR DE ARCHIVOS GOOGLE ADS
===================================

Este script extrae automáticamente los archivos CSV del ZIP de Google Ads
y los prepara para su uso en el dashboard.

Uso:
    python extraer_google_ads.py
"""

import zipfile
import os
import glob
import pandas as pd
from datetime import datetime

def extraer_archivos_google_ads():
    """Extrae los archivos CSV del ZIP de Google Ads."""
    try:
        print("📦 Iniciando extracción de archivos Google Ads...")
        
        # Ruta del archivo ZIP
        ruta_zip = 'archivos_input/archivos input marketing/google ads/Tarjetas_de_descripción_general_csv(2025-06-20_23_08_15).zip'
        ruta_destino = 'archivos_input/archivos input marketing/google ads'
        
        # Verificar que el ZIP existe
        if not os.path.exists(ruta_zip):
            print(f"❌ No se encuentra el archivo ZIP: {ruta_zip}")
            return False
        
        print(f"📁 Archivo ZIP encontrado: {os.path.basename(ruta_zip)}")
        
        # Crear directorio de destino si no existe
        if not os.path.exists(ruta_destino):
            os.makedirs(ruta_destino)
            print(f"📂 Directorio creado: {ruta_destino}")
        
        # Extraer archivos
        with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
            # Listar contenido del ZIP
            archivos_zip = zip_ref.namelist()
            print(f"📋 Archivos en el ZIP: {len(archivos_zip)}")
            
            for archivo in archivos_zip:
                print(f"   - {archivo}")
            
            # Extraer solo archivos CSV
            archivos_csv = [f for f in archivos_zip if f.lower().endswith('.csv')]
            
            if not archivos_csv:
                print("⚠️ No se encontraron archivos CSV en el ZIP")
                return False
            
            print(f"\n📊 Extrayendo {len(archivos_csv)} archivos CSV...")
            
            for archivo_csv in archivos_csv:
                # Extraer el archivo
                zip_ref.extract(archivo_csv, ruta_destino)
                
                # Renombrar si es necesario (eliminar rutas internas del ZIP)
                nombre_archivo = os.path.basename(archivo_csv)
                ruta_original = os.path.join(ruta_destino, archivo_csv)
                ruta_final = os.path.join(ruta_destino, nombre_archivo)
                
                if ruta_original != ruta_final:
                    os.rename(ruta_original, ruta_final)
                
                print(f"   ✅ Extraído: {nombre_archivo}")
        
        print("\n🎉 Extracción completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la extracción: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def verificar_archivos_extraidos():
    """Verifica que los archivos se hayan extraído correctamente."""
    try:
        print("\n🔍 Verificando archivos extraídos...")
        
        ruta_destino = 'archivos_input/archivos input marketing/google ads'
        archivos_csv = glob.glob(os.path.join(ruta_destino, '*.csv'))
        
        if not archivos_csv:
            print("❌ No se encontraron archivos CSV extraídos")
            return False
        
        print(f"📊 Archivos CSV encontrados: {len(archivos_csv)}")
        
        for archivo in archivos_csv:
            nombre = os.path.basename(archivo)
            tamaño = os.path.getsize(archivo)
            print(f"   📄 {nombre} ({tamaño:,} bytes)")
            
            # Intentar leer el archivo para verificar que es válido
            try:
                df = pd.read_csv(archivo, nrows=5)  # Leer solo las primeras 5 filas
                print(f"      ✅ Válido - {df.shape[1]} columnas")
                
                # Mostrar las columnas
                print(f"      📋 Columnas: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
                
            except Exception as e:
                print(f"      ❌ Error leyendo archivo: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos: {str(e)}")
        return False

def crear_archivo_resumen():
    """Crea un archivo de resumen con información sobre los datos extraídos."""
    try:
        print("\n📝 Creando archivo de resumen...")
        
        ruta_destino = 'archivos_input/archivos input marketing/google ads'
        archivos_csv = glob.glob(os.path.join(ruta_destino, '*.csv'))
        
        if not archivos_csv:
            return False
        
        resumen = []
        resumen.append("📊 RESUMEN DE ARCHIVOS GOOGLE ADS")
        resumen.append("=" * 50)
        resumen.append(f"Fecha de extracción: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        resumen.append(f"Total de archivos: {len(archivos_csv)}")
        resumen.append("")
        
        for archivo in archivos_csv:
            nombre = os.path.basename(archivo)
            tamaño = os.path.getsize(archivo)
            
            resumen.append(f"📄 {nombre}")
            resumen.append(f"   Tamaño: {tamaño:,} bytes")
            
            try:
                df = pd.read_csv(archivo)
                resumen.append(f"   Filas: {df.shape[0]:,}")
                resumen.append(f"   Columnas: {df.shape[1]}")
                resumen.append(f"   Columnas: {', '.join(df.columns)}")
            except Exception as e:
                resumen.append(f"   ❌ Error: {str(e)}")
            
            resumen.append("")
        
        # Guardar resumen
        archivo_resumen = os.path.join(ruta_destino, 'RESUMEN_GOOGLE_ADS.txt')
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            f.write('\n'.join(resumen))
        
        print(f"✅ Resumen guardado en: {archivo_resumen}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando resumen: {str(e)}")
        return False

def main():
    """Función principal."""
    print("🚀 EXTRACTOR DE ARCHIVOS GOOGLE ADS")
    print("=" * 50)
    
    # Paso 1: Extraer archivos
    if not extraer_archivos_google_ads():
        print("❌ Falló la extracción de archivos")
        return
    
    # Paso 2: Verificar archivos
    if not verificar_archivos_extraidos():
        print("❌ Falló la verificación de archivos")
        return
    
    # Paso 3: Crear resumen
    crear_archivo_resumen()
    
    print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE!")
    print("=" * 50)
    print("📊 Ahora puedes ejecutar el dashboard de Google Ads:")
    print("   python dashboard_google_ads.py")
    print("   o")
    print("   python ejecutar_todos_dashboards.py")
    print("\n🌐 Dashboard disponible en: http://localhost:8058")

if __name__ == '__main__':
    main() 