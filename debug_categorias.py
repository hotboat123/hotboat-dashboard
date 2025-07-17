import pandas as pd
from funciones.funciones import obtener_categoria
from inputs_modelo import diccionario_categorias, diccionario_categoria_1

print("🔍 DEBUG: Proceso de Categorización")
print("=" * 50)

# Cargar datos de gastos
df = pd.read_csv('archivos_output/gastos hotboat.csv')

# Filtrar datos de cuenta corriente (que deberían ser costos variables)
cuenta_corriente = df[df['Descripción'].str.contains('Javiera Rodriguez', na=False)]

print(f"📊 Datos de cuenta corriente encontrados: {len(cuenta_corriente)}")

if not cuenta_corriente.empty:
    print("\n🔍 Analizando categorización:")
    for idx, row in cuenta_corriente.iterrows():
        descripcion = row['Descripción']
        categoria_2 = row['Categoría_2']
        categoria_1 = row['Categoría 1']
        
        print(f"\n📝 Descripción: {descripcion}")
        print(f"   Categoría_2: {categoria_2}")
        print(f"   Categoría 1: {categoria_1}")
        
        # Probar categorización manual
        cat_manual = obtener_categoria(descripcion, diccionario_categorias)
        print(f"   Categoría manual (diccionario_categorias): {cat_manual}")
        
        # Probar categorización de Categoría 1
        if categoria_2 != 'Sin categoría':
            cat1_manual = obtener_categoria(categoria_2, diccionario_categoria_1)
            print(f"   Categoría 1 manual (diccionario_categoria_1): {cat1_manual}")

print("\n📋 Diccionario de categorías:")
print("diccionario_categorias['Gas']:", diccionario_categorias['Gas'])

print("\n📋 Diccionario de categoría 1:")
print("diccionario_categoria_1['Costos Variables']:", diccionario_categoria_1['Costos Variables']) 