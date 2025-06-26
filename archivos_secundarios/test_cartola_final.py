import pandas as pd
import os
from funciones.funciones import leer_cartola_cuenta_corriente

# Probar con un archivo específico
archivo_test = 'archivos_input/archivos_input_costos/cartola (4).xls'

print(f"🔍 Probando archivo: {archivo_test}")
print("=" * 60)

try:
    cargos, abonos = leer_cartola_cuenta_corriente(archivo_test)
    
    print(f"📊 RESULTADOS:")
    print(f"   Cargos: {len(cargos)} filas")
    print(f"   Abonos: {len(abonos)} filas")
    
    if not cargos.empty:
        print(f"\n📋 CARGOS - Primeras 3 filas:")
        print(cargos.head(3))
        print(f"\n📋 CARGOS - Columnas: {list(cargos.columns)}")
    
    if not abonos.empty:
        print(f"\n📋 ABONOS - Primeras 3 filas:")
        print(abonos.head(3))
        print(f"\n📋 ABONOS - Columnas: {list(abonos.columns)}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc() 