import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import os
import numpy as np

# Importar componentes comunes de navegación
from funciones.componentes_dashboard import crear_header, crear_filtros, crear_selector_periodo, COLORS, CARD_STYLE

# Paleta de colores diversa para combinaciones público-tipo de anuncio
PALETA_COLORES = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#a6cee3', '#fb9a99', '#fdbf6f', '#cab2d6', '#ff9896',
    '#f0027f', '#386cb0', '#fdc086', '#beaed4', '#7fc97f',
    '#bf5b17', '#666666', '#fb8072', '#80b1d3', '#fdb462',
    '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5'
]

def obtener_color_combinacion(indice):
    return PALETA_COLORES[indice % len(PALETA_COLORES)]

def cargar_datos():
    try:
        archivo_con_region = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_con_region.csv"
        print(f"🔄 Cargando archivo CON región (lluvia): {archivo_con_region}")
        if not os.path.exists(archivo_con_region):
            print(f"❌ ERROR: No se encuentra el archivo en: {archivo_con_region}")
            return None, None
        df_con_region = pd.read_csv(archivo_con_region)
        print(f"✅ Archivo CON región (lluvia) cargado. Dimensiones: {df_con_region.shape}")
        archivo_sin_region = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv"
        print(f"🔄 Cargando archivo SIN región (lluvia): {archivo_sin_region}")
        if not os.path.exists(archivo_sin_region):
            print(f"❌ ERROR: No se encuentra el archivo en: {archivo_sin_region}")
            return None, None
        df_sin_region = pd.read_csv(archivo_sin_region)
        print(f"✅ Archivo SIN región (lluvia) cargado. Dimensiones: {df_sin_region.shape}")
        print("📊 USANDO INPUTS DE LLUVIA:")
        print(f"   📈 Dataset SIN región: {len(df_sin_region)} filas")
        print(f"   🗺️ Dataset CON región: {len(df_con_region)} filas")
        numeric_columns = [
            "Importe gastado (CLP)", "Impresiones", "Clics en el enlace", 
            "Artículos agregados al carrito", "CTR (todos)", "CPC (todos)",
            "Reproducciones de video de 3 segundos", "Reproducciones de video hasta el 25%",
            "Reproducciones de video hasta el 50%", "Reproducciones de video hasta el 75%",
            "Reproducciones de video hasta el 100%"
        ]
        for df in [df_con_region, df_sin_region]:
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df['Día'] = pd.to_datetime(df['Día'])
            df['CTR_calc'] = (df['Clics en el enlace'] / df['Impresiones'] * 100).fillna(0)
            df['CPC_calc'] = (df['Importe gastado (CLP)'] / df['Clics en el enlace']).fillna(0)
            df['Hook_Rate_3s'] = (df['Reproducciones de video de 3 segundos'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_25'] = (df['Reproducciones de video hasta el 25%'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_50'] = (df['Reproducciones de video hasta el 50%'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_75'] = (df['Reproducciones de video hasta el 75%'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_100'] = (df['Reproducciones de video hasta el 100%'] / df['Impresiones'] * 100).fillna(0)
            df['Conversion_Rate'] = (df['Artículos agregados al carrito'] / df['Clics en el enlace'] * 100).fillna(0)
            df['Cost_Per_Conversion'] = (df['Importe gastado (CLP)'] / df['Artículos agregados al carrito']).fillna(0)
            def clasificar_publico(x):
                nombre = str(x).lower()
                if 'advantage' in nombre:
                    return 'Publico Advantage'
                elif 'pucon' in nombre:
                    return 'Publico Pucón'
                elif 'concepcion' in nombre:
                    return 'Publico Concepción'
                elif 'valdivia' in nombre:
                    return 'Publico Valdivia'
                elif 'temuco' in nombre:
                    return 'Test Públicos Temuco'
                else:
                    return str(x)
            df['Público'] = df['Nombre del conjunto de anuncios'].apply(clasificar_publico)
            df['Tipo_Anuncio'] = df['Nombre del anuncio'].apply(
                lambda x: 'Video explicativo' if 'explicando servicio' in str(x).lower() else
                         'Video parejas amor' if 'parejas amor' in str(x).lower() else
                         'Video parejas dcto' if 'parejas dcto' in str(x).lower() or 'pareja dcto' in str(x).lower() else
                         'Video Lluvia' if 'lluvia' in str(x).lower() else
                         'Video Viral TikTok' if 'viral tiktok' in str(x).lower() else
                         'Otro'
            )
        print("🎉 Ambos archivos de lluvia procesados exitosamente")
        print(f"✅ Dataset CON región: {len(df_con_region)} filas")
        print(f"✅ Dataset SIN región: {len(df_sin_region)} filas")
        print("=" * 60)
        return df_con_region, df_sin_region
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None, None

app = dash.Dash(__name__)
df_con_region, df_sin_region = cargar_datos()
if df_con_region is not None and df_sin_region is not None:
    fecha_min = df_con_region['Día'].min()
    fecha_max = df_con_region['Día'].max()
    app.layout = html.Div([
        crear_header("Dashboard de Marketing Lluvia", 8057),
        html.Div([
            html.Div("DASHBOARD DE MARKETING LLUVIA", style={
                'color': COLORS['primary'],
                'fontSize': '24px',
                'fontWeight': 'bold',
                'padding': '10px',
                'marginBottom': '20px',
                'textAlign': 'center',
                'backgroundColor': COLORS['card_bg'],
                'borderRadius': '5px'
            })
        ]),
        crear_filtros(fecha_min, fecha_max),
        html.Div(id='metricas-principales', style={'margin': '20px'}),
        html.Div(id='seccion-performance', style={'margin': '20px'}),
        crear_selector_periodo(),
        # ... (el resto del layout y callbacks es idéntico al dashboard simple)
    ])
    # Copiar el resto del layout y callbacks del dashboard simple aquí
else:
    app.layout = html.Div([
        html.H1("Error: No se pudieron cargar los datos de lluvia", style={
            'textAlign': 'center',
            'color': COLORS['expense'],
            'backgroundColor': COLORS['background'],
            'minHeight': '100vh',
            'padding': '20px'
        })
    ], style={'backgroundColor': COLORS['background']})

if __name__ == '__main__':
    print("\n=== DASHBOARD DE MARKETING LLUVIA ===")
    print("Datos de lluvia cargados exitosamente")
    print("Iniciando servidor en http://localhost:8057")
    app.run(debug=False, port=8057) 