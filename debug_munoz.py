import pandas as pd
from funciones.funciones import obtener_categoria
from inputs_modelo import diccionario_categorias, diccionario_categoria_1

print("🔍 DEBUG: Por qué 'munoz cucha basti' no se categoriza")
print("=" * 60)

# Cargar datos de gastos
df = pd.read_csv('archivos_output/gastos hotboat.csv')

# Buscar todas las descripciones que contengan "munoz"
munoz_data = df[df['Descripción'].str.contains('munoz', case=False, na=False)]

print(f"📊 Registros con 'munoz': {len(munoz_data)}")

if not munoz_data.empty:
    print("\n🔍 Analizando cada registro:")
    for idx, row in munoz_data.iterrows():
        descripcion = row['Descripción']
        categoria_2 = row['Categoría_2']
        categoria_1 = row['Categoría 1']
        
        print(f"\n📝 Descripción: '{descripcion}'")
        print(f"   Categoría_2: {categoria_2}")
        print(f"   Categoría 1: {categoria_1}")
        
        # Probar categorización manual
        cat_manual = obtener_categoria(descripcion, diccionario_categorias)
        print(f"   Categoría manual: {cat_manual}")
        
        # Debug: mostrar normalización
        desc_normalizada = str(descripcion).strip().lower()
        print(f"   Descripción normalizada: '{desc_normalizada}'")
        
        # Verificar si contiene las palabras clave
        palabras_clave = diccionario_categorias['Gas']
        print(f"   Palabras clave para 'Gas': {palabras_clave}")
        
        for palabra in palabras_clave:
            palabra_normalizada = str(palabra).strip().lower()
            contiene = palabra_normalizada in desc_normalizada
            print(f"     '{palabra_normalizada}' en '{desc_normalizada}': {contiene}")

print("\n📋 Diccionario completo de 'Gas':")
print(diccionario_categorias['Gas']) 