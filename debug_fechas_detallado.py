import pandas as pd
from funciones.funciones import leer_cartola_cuenta_corriente, procesar_df_final, eliminar_filas_por_descripcion
from inputs_modelo import diccionario_categorias, diccionario_categoria_1

print("🔍 DEBUG DETALLADO: Rastreo de fechas de cuenta corriente")
print("=" * 70)

# Paso 1: Leer archivo de cuenta corriente
print("📄 PASO 1: Leyendo archivo de cuenta corriente...")
cargos_cc, abonos_cc, consolidado_cc = leer_cartola_cuenta_corriente('archivos_input/archivos_input_costos/cartola (4).xls')

print(f"   Cargos encontrados: {len(cargos_cc)}")
if not cargos_cc.empty:
    print(f"   Tipo de columna Fecha: {type(cargos_cc['Fecha'].iloc[0])}")
    print(f"   Primera fecha: {cargos_cc['Fecha'].iloc[0]}")
    print(f"   Fechas nulas: {cargos_cc['Fecha'].isnull().sum()}")

# Paso 2: Simular procesar_df_final completo
print("\n📄 PASO 2: Simulando procesar_df_final completo...")

# Crear DataFrames vacíos para simular
df_banco_estado = pd.DataFrame()
df_banco_chile_int = pd.DataFrame()
df_banco_chile_nac = pd.DataFrame()

# Concatenar
df_final = pd.concat([
    df_banco_estado,
    df_banco_chile_int,
    df_banco_chile_nac,
    cargos_cc
], ignore_index=True, sort=False)

print(f"   Después de concatenar: {len(df_final)} registros")
print(f"   Fechas nulas: {df_final['Fecha'].isnull().sum()}")

# Paso 3: eliminar_filas_por_descripcion
print("\n📄 PASO 3: eliminar_filas_por_descripcion...")
df_final = eliminar_filas_por_descripcion(df_final, None)
print(f"   Después de eliminar_filas_por_descripcion: {len(df_final)} registros")
print(f"   Fechas nulas: {df_final['Fecha'].isnull().sum()}")

# Paso 4: Procesar fechas
print("\n📄 PASO 4: Procesando fechas...")

# Verificar si es datetime
if pd.api.types.is_datetime64_any_dtype(df_final['Fecha']):
    print("   ✅ Es tipo datetime, formateando a string...")
    df_final['Fecha'] = df_final['Fecha'].dt.strftime('%d/%m/%Y')
    print(f"   Después de formatear: {df_final['Fecha'].iloc[0]} (tipo: {type(df_final['Fecha'].iloc[0])})")

# Convertir a string
df_final['Fecha'] = df_final['Fecha'].astype(str)
print(f"   Después de .astype(str): {df_final['Fecha'].iloc[0]} (tipo: {type(df_final['Fecha'].iloc[0])})")

# Convertir a datetime
df_final['Fecha'] = pd.to_datetime(df_final['Fecha'], format='%d/%m/%Y', errors='coerce')
print(f"   Después de pd.to_datetime: {df_final['Fecha'].iloc[0]} (tipo: {type(df_final['Fecha'].iloc[0])})")
print(f"   Fechas nulas: {df_final['Fecha'].isnull().sum()}")

# Paso 5: Filtros adicionales
print("\n📄 PASO 5: Filtros adicionales...")
df_final = df_final[df_final['Monto'] >= 0]
print(f"   Después de filtro Monto >= 0: {len(df_final)} registros")
print(f"   Fechas nulas: {df_final['Fecha'].isnull().sum()}")

df_final = df_final.drop_duplicates(subset=['Fecha', 'Descripción', 'Monto'], keep='first')
print(f"   Después de drop_duplicates: {len(df_final)} registros")
print(f"   Fechas nulas: {df_final['Fecha'].isnull().sum()}")

# Paso 6: Categorización
print("\n📄 PASO 6: Categorización...")
from funciones.funciones import categorizar_por_descripcion
df_final = categorizar_por_descripcion(df_final, diccionario_categorias)
print(f"   Después de categorización: {len(df_final)} registros")
print(f"   Fechas nulas: {df_final['Fecha'].isnull().sum()}")

# Verificar fechas nulas finales
fechas_nulas = df_final['Fecha'].isnull()
if fechas_nulas.any():
    print("\n❌ Fechas que se convirtieron en NaN:")
    print(df_final[fechas_nulas][['Fecha', 'Descripción', 'Monto']].head())
else:
    print("\n✅ Todas las fechas se mantuvieron correctamente") 