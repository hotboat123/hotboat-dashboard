import pandas as pd

# Cargar datos
df = pd.read_csv('archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv')

print("=== ANÁLISIS DE COLUMNAS PROBLEMÁTICAS ===")

# Buscar todas las columnas que contienen "video" o "carrito"
problematic_cols = []
for col in df.columns:
    if any(word in col.lower() for word in ['video', 'carrito', 'agregados']):
        problematic_cols.append(col)

print(f"Columnas encontradas: {problematic_cols}")

# Examinar cada columna problemática
for col in problematic_cols:
    print(f"\n--- Columna: {col} ---")
    print(f"Tipo: {df[col].dtype}")
    print(f"Valores únicos: {df[col].nunique()}")
    print(f"Primeros 10 valores únicos:")
    unique_vals = df[col].unique()[:10]
    for val in unique_vals:
        print(f"  '{val}' (tipo: {type(val)})")
    
    # Intentar convertir y ver qué pasa
    try:
        original_sum = df[col].sum() if df[col].dtype in ['int64', 'float64'] else "No numérico"
        print(f"Suma original: {original_sum}")
        
        # Limpiar y convertir
        cleaned = df[col].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('-', '0')
        converted = pd.to_numeric(cleaned, errors='coerce').fillna(0)
        print(f"Suma después de limpieza: {converted.sum()}")
        print(f"Valores no nulos después de conversión: {converted[converted > 0].count()}")
        
    except Exception as e:
        print(f"Error en conversión: {e}")

print("\n=== VERIFICACIÓN MANUAL ===")
# Verificar manualmente algunas filas
print("Primeras 5 filas de todas las columnas problemáticas:")
if problematic_cols:
    print(df[problematic_cols].head()) 