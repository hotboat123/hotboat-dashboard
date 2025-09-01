import pandas as pd
from funciones.funciones import leer_cartola_cuenta_corriente

print("🔍 DEBUG: Procesamiento de fechas de cuenta corriente")
print("=" * 60)

# Procesar un archivo de cuenta corriente
archivo_cc = "archivos_input/archivos_input_costos/cartola (4).xls"

print(f"📄 Procesando archivo: {archivo_cc}")

# Leer datos de cuenta corriente
cargos, abonos, consolidado = leer_cartola_cuenta_corriente(archivo_cc)

print(f"\n📊 Cargos encontrados: {len(cargos)}")
print(f"📊 Abonos encontrados: {len(abonos)}")

if not cargos.empty:
    print("\n🔍 Primeros 3 cargos:")
    print(cargos[['Fecha', 'Descripción', 'Monto']].head(3))
    
    print(f"\n📅 Tipo de columna Fecha: {type(cargos['Fecha'].iloc[0])}")
    print(f"📅 Valores únicos de Fecha: {cargos['Fecha'].unique()[:5]}")

# Simular el procesamiento de procesar_df_final
print("\n🔄 Simulando procesamiento de procesar_df_final...")

# Convertir a string y luego a datetime
cargos_test = cargos.copy()
cargos_test['Fecha'] = cargos_test['Fecha'].astype(str)
print(f"📅 Después de .astype(str): {cargos_test['Fecha'].iloc[0]} (tipo: {type(cargos_test['Fecha'].iloc[0])})")

# Intentar convertir con formato dd/mm/YYYY
cargos_test['Fecha'] = pd.to_datetime(cargos_test['Fecha'], format='%d/%m/%Y', errors='coerce')
print(f"📅 Después de pd.to_datetime: {cargos_test['Fecha'].iloc[0]} (tipo: {type(cargos_test['Fecha'].iloc[0])})")

# Verificar fechas nulas
fechas_nulas = cargos_test['Fecha'].isnull()
print(f"📅 Fechas nulas: {fechas_nulas.sum()} de {len(cargos_test)}")

if fechas_nulas.any():
    print("\n❌ Fechas que se convirtieron en NaN:")
    fechas_originales = cargos['Fecha'][fechas_nulas.index]
    print(fechas_originales.head()) 