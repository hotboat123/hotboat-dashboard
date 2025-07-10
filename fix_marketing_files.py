#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

print("🔧 VERIFICANDO ARCHIVOS DE MARKETING...")
print("=" * 50)

# Directorio de archivos de marketing
dir_marketing = "archivos_input/archivos input marketing/"

# Archivos que necesitamos
archivos_necesarios = [
    "Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_con_region.csv",
    "Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv"
]

# Verificar archivos existentes
archivos_existentes = os.listdir(dir_marketing)
print("📁 Archivos encontrados en el directorio:")
for archivo in archivos_existentes:
    if archivo.startswith("Comp-1"):
        print(f"   - {archivo}")

print("\n🔍 Buscando archivos necesarios...")

# Buscar archivos con espacios al final
for archivo_original in archivos_existentes:
    if archivo_original.startswith("Comp-1"):
        # Limpiar espacios al final
        archivo_limpio = archivo_original.strip()
        
        if archivo_limpio != archivo_original:
            print(f"🔄 Renombrando: '{archivo_original}' -> '{archivo_limpio}'")
            
            # Renombrar archivo
            ruta_original = os.path.join(dir_marketing, archivo_original)
            ruta_nueva = os.path.join(dir_marketing, archivo_limpio)
            
            try:
                shutil.move(ruta_original, ruta_nueva)
                print(f"✅ Renombrado exitosamente")
            except Exception as e:
                print(f"❌ Error renombrando: {e}")

print("\n📋 Verificando archivos necesarios...")
for archivo in archivos_necesarios:
    ruta_completa = os.path.join(dir_marketing, archivo)
    if os.path.exists(ruta_completa):
        print(f"✅ {archivo} - ENCONTRADO")
    else:
        print(f"❌ {archivo} - NO ENCONTRADO")

print("\n🎉 Proceso completado!") 