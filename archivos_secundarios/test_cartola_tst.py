import pandas as pd
import os
from funciones.funciones import leer_cartola_cuenta_corriente

# Configurar directorios de prueba
DIRECTORIO_INPUT_TST = 'archivos_input_tst'
DIRECTORIO_OUTPUT_TST = 'archivos_output_tst'

# Crear directorio de output si no existe
if not os.path.exists(DIRECTORIO_OUTPUT_TST):
    os.makedirs(DIRECTORIO_OUTPUT_TST)

print("🧪 TEST CON CARPETA archivos_input_tst")
print("=" * 60)

# Procesar archivos de cuenta corriente en la carpeta de test
cuenta_corriente_cargos = []
cuenta_corriente_abonos = []

for archivo in os.listdir(DIRECTORIO_INPUT_TST):
    # Buscar archivos que contengan "cartola" en el nombre (case insensitive)
    if 'cartola' in archivo.lower() and archivo.lower().endswith(('.xls', '.xlsx')):
        ruta = os.path.join(DIRECTORIO_INPUT_TST, archivo)
        print(f"📄 Procesando: {archivo}")
        try:
            cargos, abonos = leer_cartola_cuenta_corriente(ruta)
            if not cargos.empty:
                cuenta_corriente_cargos.append(cargos)
                print(f"   ✅ Cargos: {len(cargos)} filas")
            if not abonos.empty:
                cuenta_corriente_abonos.append(abonos)
                print(f"   ✅ Abonos: {len(abonos)} filas")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

# Consolidar resultados
df_cargos_cc = pd.DataFrame()
df_abonos_cc = pd.DataFrame()

if cuenta_corriente_cargos:
    df_cargos_cc = pd.concat(cuenta_corriente_cargos, ignore_index=True)
    df_cargos_cc = df_cargos_cc.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
    print(f"\n📊 Cargos consolidados: {len(df_cargos_cc)} filas")
    
if cuenta_corriente_abonos:
    df_abonos_cc = pd.concat(cuenta_corriente_abonos, ignore_index=True)
    df_abonos_cc = df_abonos_cc.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
    print(f"📊 Abonos consolidados: {len(df_abonos_cc)} filas")

# Exportar archivos de prueba
if not df_cargos_cc.empty:
    df_cargos_cc.to_csv(os.path.join(DIRECTORIO_OUTPUT_TST, 'test_cuenta_corriente_cargos.csv'), index=False)
    print(f"💾 Exportado: test_cuenta_corriente_cargos.csv")
    
if not df_abonos_cc.empty:
    df_abonos_cc.to_csv(os.path.join(DIRECTORIO_OUTPUT_TST, 'test_cuenta_corriente_abonos.csv'), index=False)
    print(f"💾 Exportado: test_cuenta_corriente_abonos.csv")

# Mostrar resumen
print("\n" + "=" * 60)
print("📋 RESUMEN DEL TEST:")
print(f"   📁 Archivos procesados: {len(cuenta_corriente_cargos) + len(cuenta_corriente_abonos)}")
print(f"   💰 Total cargos: {len(df_cargos_cc)} filas")
print(f"   💰 Total abonos: {len(df_abonos_cc)} filas")

if not df_cargos_cc.empty:
    print(f"\n📋 MUESTRA CARGOS:")
    print(df_cargos_cc.head(3))

if not df_abonos_cc.empty:
    print(f"\n📋 MUESTRA ABONOS:")
    print(df_abonos_cc.head(3))

print("\n✅ Test completado exitosamente!") 