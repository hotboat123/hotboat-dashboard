import pandas as pd
import os
from funciones.funciones import ProcesadorArchivos, leer_cartola_cuenta_corriente

print("🔍 DEBUG: Procesamiento de Cuenta Corriente")
print("=" * 50)

# 1. Verificar archivos de cuenta corriente
archivos_cc = []
for archivo in os.listdir('archivos_input/archivos_input_costos'):
    if "cartola" in archivo.lower() and any(num in archivo for num in ["(4)", "(5)", "(6)", "(7)", "(8)"]):
        archivos_cc.append(archivo)

print(f"📁 Archivos de cuenta corriente encontrados: {len(archivos_cc)}")
for archivo in archivos_cc:
    print(f"   - {archivo}")

# 2. Procesar un archivo de ejemplo
if archivos_cc:
    archivo_ejemplo = os.path.join('archivos_input/archivos_input_costos', archivos_cc[0])
    print(f"\n🔍 Procesando archivo de ejemplo: {archivos_cc[0]}")
    
    cargos, abonos = leer_cartola_cuenta_corriente(archivo_ejemplo)
    
    print(f"   Cargos: {len(cargos)} registros")
    if not cargos.empty:
        print(f"   Columnas de cargos: {list(cargos.columns)}")
        print(f"   Tipo de Fecha: {type(cargos['Fecha'].iloc[0])}")
        print(f"   Primera fecha: {cargos['Fecha'].iloc[0]}")
        print(f"   Fechas nulas: {cargos['Fecha'].isnull().sum()}")
        print(f"   Primeras filas:")
        print(cargos[['Fecha', 'Descripción', 'Monto']].head())
    
    print(f"   Abonos: {len(abonos)} registros")
    if not abonos.empty:
        print(f"   Columnas de abonos: {list(abonos.columns)}")
        print(f"   Tipo de Fecha: {type(abonos['Fecha'].iloc[0])}")
        print(f"   Primera fecha: {abonos['Fecha'].iloc[0]}")
        print(f"   Fechas nulas: {abonos['Fecha'].isnull().sum()}")

# 3. Verificar procesamiento completo
print(f"\n🔍 Procesamiento completo con ProcesadorArchivos")
procesador = ProcesadorArchivos()

for archivo in archivos_cc:
    ruta_archivo = os.path.join('archivos_input/archivos_input_costos', archivo)
    procesador.procesar_archivo(ruta_archivo, archivo, 950, '2025')

datos_consolidados = procesador.consolidar_datos()

if not datos_consolidados['cuenta_corriente_cargos'].empty:
    print(f"   Cargos consolidados: {len(datos_consolidados['cuenta_corriente_cargos'])} registros")
    print(f"   Columnas: {list(datos_consolidados['cuenta_corriente_cargos'].columns)}")
    print(f"   Tipo de Fecha: {type(datos_consolidados['cuenta_corriente_cargos']['Fecha'].iloc[0])}")
    print(f"   Fechas nulas: {datos_consolidados['cuenta_corriente_cargos']['Fecha'].isnull().sum()}")
    print(f"   Primeras filas:")
    print(datos_consolidados['cuenta_corriente_cargos'][['Fecha', 'Descripción', 'Monto']].head())
else:
    print("   ❌ No hay cargos de cuenta corriente consolidados") 