import pandas as pd
import os

def clasificar_tipo_anuncio(x):
    """Función de clasificación idéntica a la del dashboard"""
    return ('Video explicativo' if 'explicando servicio' in str(x).lower() else
            'Video parejas amor' if 'parejas amor' in str(x).lower() else
            'Video parejas dcto' if 'parejas dcto' in str(x).lower() or 'pareja dcto' in str(x).lower() else
            'Video Lluvia' if 'lluvia' in str(x).lower() else
            'Otro')

def analizar_tipos_anuncios():
    """Analizar qué anuncios se clasifican como 'Otro'"""
    
    # Cargar archivos
    archivo_sin_region = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv"
    
    if not os.path.exists(archivo_sin_region):
        print(f"❌ No se encuentra el archivo: {archivo_sin_region}")
        return
    
    print("🔄 Cargando datos...")
    df = pd.read_csv(archivo_sin_region)
    print(f"✅ Datos cargados: {len(df)} filas")
    
    # Aplicar clasificación
    df['Tipo_Anuncio'] = df['Nombre del anuncio'].apply(clasificar_tipo_anuncio)
    
    # Mostrar todos los nombres únicos de anuncios
    print("\n📋 TODOS LOS NOMBRES DE ANUNCIOS ÚNICOS:")
    nombres_unicos = sorted(df['Nombre del anuncio'].unique())
    for i, nombre in enumerate(nombres_unicos, 1):
        tipo = clasificar_tipo_anuncio(nombre)
        print(f"{i:2d}. {nombre} → {tipo}")
    
    # Mostrar distribución por tipo
    print("\n📊 DISTRIBUCIÓN POR TIPO DE ANUNCIO:")
    distribucion = df['Tipo_Anuncio'].value_counts()
    for tipo, cantidad in distribucion.items():
        print(f"   {tipo}: {cantidad} registros")
    
    # Mostrar específicamente los que se clasifican como "Otro"
    print("\n❓ ANUNCIOS CLASIFICADOS COMO 'OTRO':")
    otros = df[df['Tipo_Anuncio'] == 'Otro']['Nombre del anuncio'].unique()
    if len(otros) > 0:
        for i, nombre in enumerate(sorted(otros), 1):
            print(f"   {i}. {nombre}")
    else:
        print("   ✅ No hay anuncios clasificados como 'Otro'")
    
    # Mostrar estadísticas de gasto por tipo
    print("\n💰 GASTO POR TIPO DE ANUNCIO:")
    gasto_por_tipo = df.groupby('Tipo_Anuncio')['Importe gastado (CLP)'].sum().sort_values(ascending=False)
    for tipo, gasto in gasto_por_tipo.items():
        print(f"   {tipo}: ${gasto:,.0f}")

if __name__ == "__main__":
    analizar_tipos_anuncios() 