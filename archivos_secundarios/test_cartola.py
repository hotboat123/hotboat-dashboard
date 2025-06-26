import pandas as pd
import os
from funciones.funciones import leer_cartola_cuenta_corriente

# Probar con un archivo específico
archivo_test = 'archivos_input/archivos_input_costos/cartola (4).xls'

print(f"🔍 Probando archivo: {archivo_test}")
print("=" * 60)

try:
    df_resultado = leer_cartola_cuenta_corriente(archivo_test)
    
    if not df_resultado.empty:
        print(f"✅ Archivo procesado exitosamente")
        print(f"📊 Filas: {len(df_resultado)}")
        print(f"📋 Columnas: {list(df_resultado.columns)}")
        print(f"\n📋 Primeras 5 filas:")
        print(df_resultado.head())
    else:
        print("❌ No se encontraron datos válidos")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc() 