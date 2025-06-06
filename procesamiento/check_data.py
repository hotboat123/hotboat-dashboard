import pandas as pd

# Cargar datos
df = pd.read_csv('archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv')

print("=== VERIFICACIÓN DE DATOS ===")
print(f"Total filas: {len(df)}")
print(f"Total columnas: {len(df.columns)}")

# Buscar columnas relacionadas con video
video_cols = [col for col in df.columns if 'video' in col.lower() or 'reproduc' in col.lower()]
print(f"\nColumnas de video encontradas: {video_cols}")

# Verificar datos específicos
print("\n=== DATOS DE REPRODUCCIONES ===")
if 'Reproducciones de video de 3 segundos' in df.columns:
    col = 'Reproducciones de video de 3 segundos'
    print(f"Columna '{col}':")
    print(f"  - Tipo de datos: {df[col].dtype}")
    print(f"  - Valores únicos: {df[col].nunique()}")
    print(f"  - Suma total: {df[col].sum()}")
    print(f"  - Valores no nulos: {df[col].notna().sum()}")
    print(f"  - Primeros 10 valores: {df[col].head(10).tolist()}")
    
    # Convertir a numérico
    df[col] = pd.to_numeric(df[col], errors='coerce')
    print(f"  - Después de conversión numérica - Suma: {df[col].sum()}")

print("\n=== DATOS DE IMPRESIONES ===")
if 'Impresiones' in df.columns:
    col = 'Impresiones'
    print(f"Columna '{col}':")
    print(f"  - Tipo de datos: {df[col].dtype}")
    print(f"  - Suma total: {df[col].sum()}")
    print(f"  - Primeros 10 valores: {df[col].head(10).tolist()}")

print("\n=== CÁLCULO DE HOOK RATE ===")
if 'Reproducciones de video de 3 segundos' in df.columns and 'Impresiones' in df.columns:
    # Convertir ambas columnas
    df['Reproducciones de video de 3 segundos'] = pd.to_numeric(df['Reproducciones de video de 3 segundos'], errors='coerce').fillna(0)
    df['Impresiones'] = pd.to_numeric(df['Impresiones'], errors='coerce').fillna(0)
    
    # Calcular hook rate
    hook_rate = (df['Reproducciones de video de 3 segundos'] / df['Impresiones'] * 100).fillna(0)
    print(f"Hook rate promedio: {hook_rate.mean():.2f}%")
    print(f"Hook rate por fila (primeras 10): {hook_rate.head(10).tolist()}")
    
    # Por tipo de anuncio
    df['Tipo_Anuncio'] = df['Nombre del anuncio'].apply(
        lambda x: 'Video explicativo' if 'explicando servicio' in str(x).lower() else
                 'Video parejas amor' if 'parejas amor' in str(x).lower() else
                 'Video parejas dcto' if 'parejas dcto' in str(x).lower() else
                 'Otro'
    )
    
    agrupado = df.groupby('Tipo_Anuncio').agg({
        'Reproducciones de video de 3 segundos': 'sum',
        'Impresiones': 'sum'
    })
    agrupado['Hook_Rate'] = (agrupado['Reproducciones de video de 3 segundos'] / agrupado['Impresiones'] * 100).fillna(0)
    print("\nHook rates por tipo de anuncio:")
    print(agrupado) 