import pandas as pd
import os
from funciones.funciones import leer_cartola_cuenta_corriente

# Probar con un archivo específico
archivo_test = 'archivos_input/archivos_input_costos/cartola (4).xls'

print(f"🔍 Probando archivo: {archivo_test}")
print("=" * 60)

try:
    cargos, abonos, consolidado = leer_cartola_cuenta_corriente(archivo_test)
    
    print(f"✅ Archivo procesado exitosamente")
    print(f"📊 Cargos: {len(cargos)} | Abonos: {len(abonos)} | Consolidado: {len(consolidado)}")
    if not consolidado.empty:
        print(f"\n📋 CONSOLIDADO - Primeras 5 filas:")
        print(consolidado.head())
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc() 