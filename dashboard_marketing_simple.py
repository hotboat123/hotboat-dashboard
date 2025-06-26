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
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',  # Azul, Naranja, Verde, Rojo, Púrpura
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',  # Marrón, Rosa, Gris, Verde lima, Cian
    '#a6cee3', '#fb9a99', '#fdbf6f', '#cab2d6', '#ff9896',  # Azul claro, Rosa claro, Naranja claro, Púrpura claro, Rosa claro 2
    '#f0027f', '#386cb0', '#fdc086', '#beaed4', '#7fc97f',  # Magenta, Azul oscuro, Naranja oscuro, Púrpura oscuro, Verde oscuro
    '#bf5b17', '#666666', '#fb8072', '#80b1d3', '#fdb462',  # Marrón oscuro, Gris oscuro, Rojo claro, Azul medio, Naranja medio
    '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5'   # Verde lima claro, Rosa muy claro, Gris claro, Púrpura medio, Verde muy claro
]

def obtener_color_combinacion(indice):
    """Asigna un color único a cada combinación público-tipo de anuncio"""
    return PALETA_COLORES[indice % len(PALETA_COLORES)]

# Función para cargar datos con más procesamiento
def cargar_datos():
    """Carga los archivos CSV de marketing específicos: (5) CON región y (6) SIN región."""
    try:
        # Archivo CON región (5) - para gráfico de regiones
        archivo_con_region = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_con_region.csv"
        print(f"🔄 Cargando archivo CON región (5): {archivo_con_region}")
        
        if not os.path.exists(archivo_con_region):
            print(f"❌ ERROR: No se encuentra el archivo en: {archivo_con_region}")
            return None, None
        
        df_con_region = pd.read_csv(archivo_con_region)
        print(f"✅ Archivo CON región (5) cargado. Dimensiones: {df_con_region.shape}")
        
        # Archivo SIN región (6) - para demás gráficos  
        archivo_sin_region = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv"
        print(f"🔄 Cargando archivo SIN región (6): {archivo_sin_region}")
        
        if not os.path.exists(archivo_sin_region):
            print(f"❌ ERROR: No se encuentra el archivo en: {archivo_sin_region}")
            return None, None
            
        df_sin_region = pd.read_csv(archivo_sin_region)
        print(f"✅ Archivo SIN región (6) cargado. Dimensiones: {df_sin_region.shape}")
        
        print("📊 USANDO NUEVOS INPUTS ESPECÍFICOS:")
        print(f"   📈 Dataset (6): {len(df_sin_region)} filas - Sin región")
        print(f"   🗺️ Dataset (5): {len(df_con_region)} filas - Con región")
        
        # Procesar archivos con datos actualizados
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
            
            # Convertir fechas
            df['Día'] = pd.to_datetime(df['Día'])
            
            # Agregar columnas calculadas
            df['CTR_calc'] = (df['Clics en el enlace'] / df['Impresiones'] * 100).fillna(0)
            df['CPC_calc'] = (df['Importe gastado (CLP)'] / df['Clics en el enlace']).fillna(0)
            df['Hook_Rate_3s'] = (df['Reproducciones de video de 3 segundos'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_25'] = (df['Reproducciones de video hasta el 25%'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_50'] = (df['Reproducciones de video hasta el 50%'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_75'] = (df['Reproducciones de video hasta el 75%'] / df['Impresiones'] * 100).fillna(0)
            df['Hook_Rate_100'] = (df['Reproducciones de video hasta el 100%'] / df['Impresiones'] * 100).fillna(0)
            df['Conversion_Rate'] = (df['Artículos agregados al carrito'] / df['Clics en el enlace'] * 100).fillna(0)
            df['Cost_Per_Conversion'] = (df['Importe gastado (CLP)'] / df['Artículos agregados al carrito']).fillna(0)
            
            # Clasificar públicos - mantener todas las regiones/públicos separados
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
                    # Mantener el nombre original para otros casos
                    return str(x)
            
            df['Público'] = df['Nombre del conjunto de anuncios'].apply(clasificar_publico)
            
            # Clasificar tipos de anuncios
            df['Tipo_Anuncio'] = df['Nombre del anuncio'].apply(
                lambda x: 'Video explicativo' if 'explicando servicio' in str(x).lower() else
                         'Video parejas amor' if 'parejas amor' in str(x).lower() else
                         'Video parejas dcto' if 'parejas dcto' in str(x).lower() or 'pareja dcto' in str(x).lower() else
                         'Video Lluvia' if 'lluvia' in str(x).lower() else
                         'Otro'
            )
        
        print("🎉 Ambos archivos procesados exitosamente con nuevos inputs")
        print(f"✅ Dataset (5) CON región: {len(df_con_region)} filas")
        print(f"✅ Dataset (6) SIN región: {len(df_sin_region)} filas")
        print("=" * 60)
        return df_con_region, df_sin_region
    
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None, None

# Crear aplicación
app = dash.Dash(__name__)

# Cargar datos
df_con_region, df_sin_region = cargar_datos()

if df_con_region is not None and df_sin_region is not None:
    fecha_min = df_con_region['Día'].min()
    fecha_max = df_con_region['Día'].max()
    
    # Layout con tema oscuro idéntico a otros dashboards
    app.layout = html.Div([
        # Header con navegación
        crear_header("Dashboard de Marketing HotBoat", 8056),
        
        # Título del dashboard
        html.Div([
            html.Div("DASHBOARD DE MARKETING", style={
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
        
        # Filtros con el mismo estilo que otros dashboards
        crear_filtros(fecha_min, fecha_max),
        
        # Métricas principales
        html.Div(id='metricas-principales', style={'margin': '20px'}),
        
        # Sección Top Performers y Necesita Atención
        html.Div(id='seccion-performance', style={'margin': '20px'}),
        
        # Selector de período con el mismo estilo
        crear_selector_periodo(),
        
        # Gráficos con contenedores oscuros
        html.Div([
            html.H3('Evolución Temporal del Gasto', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-evolucion')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        html.Div([
            html.H3('Evolución de Conversiones por Público y Tipo de Anuncio', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-evolucion-conversiones')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        # Gráfico de evolución con filtros de métricas
        html.Div([
            html.H3('Evolución de Conversiones y Gasto por Combinación Público-Tipo de Anuncio', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Label('Filtrar por Público:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-publico-conversiones',
                        options=[{'label': 'Todos', 'value': 'todos'}] + [{'label': p, 'value': p} for p in sorted(df_sin_region['Público'].unique())],
                        value='todos',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'}),
                html.Div([
                    html.Label('Filtrar por Tipo de Anuncio:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-tipo-conversiones',
                        options=[{'label': 'Todos', 'value': 'todos'}] + [{'label': t, 'value': t} for t in sorted(df_sin_region['Tipo_Anuncio'].unique())],
                        value='todos',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'}),
                html.Div([
                    html.Label('Métrica Eje Y Izquierdo:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-metrica-eje-izq-conv',
                        options=[
                            {'label': 'Ninguno', 'value': 'ninguno'},
                            {'label': 'Conversiones', 'value': 'conversiones'},
                            {'label': 'Gasto', 'value': 'gasto'}
                        ],
                        value='conversiones',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'}),
                html.Div([
                    html.Label('Métrica Eje Y Derecho:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-metrica-eje-der-conv',
                        options=[
                            {'label': 'Ninguno', 'value': 'ninguno'},
                            {'label': 'Conversiones', 'value': 'conversiones'},
                            {'label': 'Gasto', 'value': 'gasto'}
                        ],
                        value='gasto',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'})
            ], style={'marginBottom': '20px'}),
            dcc.Graph(id='grafico-evolucion-conversiones-filtrado')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        # Gráfico de evolución de costos con filtros
        html.Div([
            html.H3('Evolución de CPC y Costo por Conversión por Combinación Público-Tipo de Anuncio', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            html.Div([
                html.Div([
                    html.Label('Filtrar por Público:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-publico-costos',
                        options=[{'label': 'Todos', 'value': 'todos'}] + [{'label': p, 'value': p} for p in sorted(df_sin_region['Público'].unique())],
                        value='todos',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'}),
                html.Div([
                    html.Label('Filtrar por Tipo de Anuncio:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-tipo-costos',
                        options=[{'label': 'Todos', 'value': 'todos'}] + [{'label': t, 'value': t} for t in sorted(df_sin_region['Tipo_Anuncio'].unique())],
                        value='todos',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'}),
                html.Div([
                    html.Label('Métrica Eje Y Izquierdo:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-metrica-eje-izq-costos',
                        options=[
                            {'label': 'Ninguno', 'value': 'ninguno'},
                            {'label': 'CPC', 'value': 'cpc'},
                            {'label': 'Costo por Conversión', 'value': 'costo_conversion'}
                        ],
                        value='cpc',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'}),
                html.Div([
                    html.Label('Métrica Eje Y Derecho:', style={'color': COLORS['text'], 'marginRight': '10px'}),
                    dcc.Dropdown(
                        id='filtro-metrica-eje-der-costos',
                        options=[
                            {'label': 'Ninguno', 'value': 'ninguno'},
                            {'label': 'CPC', 'value': 'cpc'},
                            {'label': 'Costo por Conversión', 'value': 'costo_conversion'}
                        ],
                        value='costo_conversion',
                        style={'backgroundColor': COLORS['card_bg'], 'color': 'black'}
                    )
                ], style={'display': 'inline-block', 'marginRight': '20px', 'width': '200px'})
            ], style={'marginBottom': '20px'}),
            dcc.Graph(id='grafico-evolucion-costos')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        html.Div([
            html.H3('Gasto por Región', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-regiones')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        html.Div([
            html.H3('Análisis por Públicos', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-publicos')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        html.Div([
            html.H3('Análisis por Tipos de Anuncios', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-tipos-anuncios')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        html.Div([
            html.H3('Hook Rates por Tipo de Anuncio', style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-hook-rates')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        # Insights con estilo oscuro
        html.Div([
            html.H3('💡 Conclusiones e Insights', style={
                'color': COLORS['text'], 
                'marginBottom': '15px'
            }),
            html.Div(id='insights-contenido')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        })
    ], style={
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'padding': '20px'
    })
    
    # Callback principal
    @callback(
        [Output('metricas-principales', 'children'),
         Output('seccion-performance', 'children'),
         Output('grafico-evolucion', 'figure'),
         Output('grafico-evolucion-conversiones', 'figure'),
         Output('grafico-evolucion-conversiones-filtrado', 'figure'),
         Output('grafico-evolucion-costos', 'figure'),
         Output('grafico-regiones', 'figure'),
         Output('grafico-publicos', 'figure'),
         Output('grafico-tipos-anuncios', 'figure'),
         Output('grafico-hook-rates', 'figure'),
         Output('insights-contenido', 'children')],
        [Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date'),
         Input('periodo-selector', 'value'),
         Input('filtro-publico-conversiones', 'value'),
         Input('filtro-tipo-conversiones', 'value'),
         Input('filtro-metrica-eje-izq-conv', 'value'),
         Input('filtro-metrica-eje-der-conv', 'value'),
         Input('filtro-publico-costos', 'value'),
         Input('filtro-tipo-costos', 'value'),
         Input('filtro-metrica-eje-izq-costos', 'value'),
         Input('filtro-metrica-eje-der-costos', 'value')]
    )
    def actualizar_dashboard(start_date, end_date, periodo, filtro_publico_conv, filtro_tipo_conv, 
                           filtro_metric_izq_conv, filtro_metric_der_conv,
                           filtro_publico_costos, filtro_tipo_costos, 
                           filtro_metric_izq_costos, filtro_metric_der_costos):
        try:
            # Filtrar datos por fecha - USAR ARCHIVO SIN REGIÓN para métricas generales
            mask_sin_region = (df_sin_region['Día'] >= start_date) & (df_sin_region['Día'] <= end_date)
            df_filtrado_sin_region = df_sin_region[mask_sin_region]
            
            # Filtrar datos por fecha - USAR ARCHIVO CON REGIÓN solo para gráfico regional
            mask_con_region = (df_con_region['Día'] >= start_date) & (df_con_region['Día'] <= end_date)
            df_filtrado_con_region = df_con_region[mask_con_region]
            
            if df_filtrado_sin_region.empty:
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    title="No hay datos para el período seleccionado",
                    paper_bgcolor=COLORS['card_bg'],
                    plot_bgcolor=COLORS['card_bg'],
                    font={'color': COLORS['text']}
                )
                return (html.Div("No hay datos"), html.Div("No hay datos"), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "No hay insights disponibles")
            
            # Calcular métricas principales (usar archivo SIN región)
            total_gasto = df_filtrado_sin_region['Importe gastado (CLP)'].sum()
            total_impresiones = df_filtrado_sin_region['Impresiones'].sum()
            total_clics = df_filtrado_sin_region['Clics en el enlace'].sum()
            total_conversiones = df_filtrado_sin_region['Artículos agregados al carrito'].sum()
            
            ctr = (total_clics / total_impresiones * 100) if total_impresiones > 0 else 0
            cpc = (total_gasto / total_clics) if total_clics > 0 else 0
            
            # 1. Tarjetas de métricas con estilo oscuro
            metricas = html.Div([
                html.Div([
                    html.H3(f'${total_gasto:,.0f}', style={'color': COLORS['expense'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('Gasto Total', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                
                html.Div([
                    html.H3(f'{total_impresiones:,.0f}', style={'color': COLORS['primary'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('Impresiones', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                
                html.Div([
                    html.H3(f'{total_clics:,.0f}', style={'color': COLORS['income'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('Clics', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                
                html.Div([
                    html.H3(f'{ctr:.2f}%', style={'color': COLORS['secondary'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('CTR Promedio', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                
                html.Div([
                    html.H3(f'{total_conversiones:,.0f}', style={'color': '#9b59b6', 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('Conversiones', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE)
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'})
            
            # Sección Top Performers y Needs Attention
            df_combinaciones = df_filtrado_sin_region.groupby(['Público', 'Tipo_Anuncio']).agg({
                'Importe gastado (CLP)': 'sum',
                'Artículos agregados al carrito': 'sum',
                'Clics en el enlace': 'sum'
            }).reset_index()
            
            # Calcular métricas adicionales
            df_combinaciones['CPC'] = (df_combinaciones['Importe gastado (CLP)'] / df_combinaciones['Clics en el enlace']).fillna(0)
            df_combinaciones['Costo_Por_Conversion'] = (df_combinaciones['Importe gastado (CLP)'] / df_combinaciones['Artículos agregados al carrito']).fillna(0)
            df_combinaciones['Conversion_Rate'] = (df_combinaciones['Artículos agregados al carrito'] / df_combinaciones['Clics en el enlace'] * 100).fillna(0)
            
            # Top Performers (mejor costo por conversión)
            top_performers = df_combinaciones[df_combinaciones['Artículos agregados al carrito'] > 0].nlargest(5, 'Conversion_Rate')
            
            # Needs Attention (gasto sin conversiones)
            needs_attention = df_combinaciones[df_combinaciones['Artículos agregados al carrito'] == 0].nlargest(5, 'Importe gastado (CLP)')
            
            seccion_performance = html.Div([
                html.Div([
                    html.H3('🏆 Top Performers (Mejor Tasa de Conversión)', style={'color': COLORS['income'], 'marginBottom': '15px'}),
                    html.Div([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th('Público', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Tipo Anuncio', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Conversiones', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Gasto', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Tasa Conv.', style={'color': COLORS['text'], 'padding': '8px'})
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(row['Público'], style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(row['Tipo_Anuncio'], style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(f"{row['Artículos agregados al carrito']:.0f}", style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(f"${row['Importe gastado (CLP)']:,.0f}", style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(f"{row['Conversion_Rate']:.2f}%", style={'color': COLORS['income'], 'padding': '8px', 'fontWeight': 'bold'})
                                ]) for _, row in top_performers.iterrows()
                            ])
                        ], style={'width': '100%', 'borderCollapse': 'collapse'})
                    ])
                ], style={'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '5px', 'marginBottom': '20px'}),
                
                html.Div([
                    html.H3('⚠️ Needs Attention (Sin Conversiones)', style={'color': COLORS['expense'], 'marginBottom': '15px'}),
                    html.Div([
                        html.Table([
                            html.Thead([
                                html.Tr([
                                    html.Th('Público', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Tipo Anuncio', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Gasto', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Clics', style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Th('Conversiones', style={'color': COLORS['text'], 'padding': '8px'})
                                ])
                            ]),
                            html.Tbody([
                                html.Tr([
                                    html.Td(row['Público'], style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(row['Tipo_Anuncio'], style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(f"${row['Importe gastado (CLP)']:,.0f}", style={'color': COLORS['expense'], 'padding': '8px', 'fontWeight': 'bold'}),
                                    html.Td(f"{row['Clics en el enlace']:.0f}", style={'color': COLORS['text'], 'padding': '8px'}),
                                    html.Td(f"{row['Artículos agregados al carrito']:.0f}", style={'color': COLORS['text'], 'padding': '8px'})
                                ]) for _, row in needs_attention.iterrows()
                            ])
                        ], style={'width': '100%', 'borderCollapse': 'collapse'})
                    ])
                ], style={'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '5px'})
            ])
            
            # 2. Gráfico de evolución temporal con tema oscuro
            if periodo == 'D':
                df_temporal = df_filtrado_sin_region.groupby('Día').agg({
                    'Importe gastado (CLP)': 'sum',
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                titulo_evolucion = 'Evolución Diaria del Gasto y Conversiones'
            elif periodo == 'W':
                df_temporal = df_filtrado_sin_region.groupby(df_filtrado_sin_region['Día'].dt.to_period('W').dt.start_time).agg({
                    'Importe gastado (CLP)': 'sum',
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                titulo_evolucion = 'Evolución Semanal del Gasto y Conversiones'
            else:
                df_temporal = df_filtrado_sin_region.groupby(df_filtrado_sin_region['Día'].dt.to_period('M').dt.start_time).agg({
                    'Importe gastado (CLP)': 'sum',
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                titulo_evolucion = 'Evolución Mensual del Gasto y Conversiones'
            
            fig_evolucion = go.Figure()
            
            # Agregar línea de gasto (eje Y izquierdo)
            fig_evolucion.add_trace(go.Scatter(
                x=df_temporal['Día'],
                y=df_temporal['Importe gastado (CLP)'],
                mode='lines+markers',
                name='Gasto (CLP)',
                line=dict(color=COLORS['expense'], width=3),
                marker=dict(size=8),
                yaxis='y'
            ))
            
            # Agregar línea de conversiones (eje Y derecho)
            fig_evolucion.add_trace(go.Scatter(
                x=df_temporal['Día'],
                y=df_temporal['Artículos agregados al carrito'],
                mode='lines+markers',
                name='Conversiones',
                line=dict(color=COLORS['income'], width=3),
                marker=dict(size=8, symbol='diamond'),
                yaxis='y2'
            ))
            
            fig_evolucion.update_layout(
                title=titulo_evolucion,
                xaxis_title='Período',
                height=400,
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    tickfont={'color': COLORS['text']},
                    title_font={'color': COLORS['text']}
                ),
                yaxis=dict(
                    title='Gasto (CLP)',
                    titlefont=dict(color=COLORS['expense']),
                    tickfont=dict(color=COLORS['expense']),
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    side='left'
                ),
                yaxis2=dict(
                    title='Conversiones',
                    titlefont=dict(color=COLORS['income']),
                    tickfont=dict(color=COLORS['income']),
                    showgrid=False,
                    side='right',
                    overlaying='y'
                ),
                legend=dict(
                    font=dict(color=COLORS['text']),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified'
            )
            
            # 3. Gráfico de evolución de conversiones por público y tipo de anuncio
            if periodo == 'D':
                df_conv_publico = df_filtrado_sin_region.groupby(['Día', 'Público']).agg({
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_conv_tipo = df_filtrado_sin_region.groupby(['Día', 'Tipo_Anuncio']).agg({
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                titulo_conv = 'Evolución Diaria de Conversiones'
            elif periodo == 'W':
                df_conv_publico = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('W').dt.start_time, 'Público']).agg({
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_conv_publico.rename(columns={'Día': 'Día'}, inplace=True)
                df_conv_tipo = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('W').dt.start_time, 'Tipo_Anuncio']).agg({
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_conv_tipo.rename(columns={'Día': 'Día'}, inplace=True)
                titulo_conv = 'Evolución Semanal de Conversiones'
            else:
                df_conv_publico = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('M').dt.start_time, 'Público']).agg({
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_conv_publico.rename(columns={'Día': 'Día'}, inplace=True)
                df_conv_tipo = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('M').dt.start_time, 'Tipo_Anuncio']).agg({
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_conv_tipo.rename(columns={'Día': 'Día'}, inplace=True)
                titulo_conv = 'Evolución Mensual de Conversiones'
            
            fig_evolucion_conv = go.Figure()
            
            # Agregar líneas por público
            for publico in df_conv_publico['Público'].unique():
                df_publico = df_conv_publico[df_conv_publico['Público'] == publico]
                fig_evolucion_conv.add_trace(go.Scatter(
                    x=df_publico['Día'],
                    y=df_publico['Artículos agregados al carrito'],
                    mode='lines+markers',
                    name=f'Público: {publico}',
                    line=dict(width=2),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{publico}</b><br>Fecha: %{{x}}<br>Conversiones: %{{y}}<extra></extra>'
                ))
            
            # Agregar líneas por tipo de anuncio
            for tipo in df_conv_tipo['Tipo_Anuncio'].unique():
                df_tipo = df_conv_tipo[df_conv_tipo['Tipo_Anuncio'] == tipo]
                fig_evolucion_conv.add_trace(go.Scatter(
                    x=df_tipo['Día'],
                    y=df_tipo['Artículos agregados al carrito'],
                    mode='lines+markers',
                    name=f'Tipo: {tipo}',
                    line=dict(width=2, dash='dash'),
                    marker=dict(size=6, symbol='diamond'),
                    hovertemplate=f'<b>{tipo}</b><br>Fecha: %{{x}}<br>Conversiones: %{{y}}<extra></extra>'
                ))
            
            fig_evolucion_conv.update_layout(
                title=titulo_conv,
                xaxis_title='Período',
                height=500,
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    tickfont={'color': COLORS['text']},
                    title_font={'color': COLORS['text']}
                ),
                yaxis=dict(
                    title='Conversiones',
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    tickfont={'color': COLORS['text']},
                    title_font={'color': COLORS['text']}
                ),
                legend=dict(
                    font=dict(color=COLORS['text']),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified'
            )
            
            # 4. Gráfico de evolución de conversiones y gasto con filtros
            if periodo == 'D':
                df_conv_combinado = df_filtrado_sin_region.groupby(['Día', 'Público', 'Tipo_Anuncio']).agg({
                    'Artículos agregados al carrito': 'sum',
                    'Importe gastado (CLP)': 'sum'
                }).reset_index()
                titulo_conv_filtrado = 'Evolución Diaria de Conversiones y Gasto por Combinación'
            elif periodo == 'W':
                df_conv_combinado = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('W').dt.start_time, 'Público', 'Tipo_Anuncio']).agg({
                    'Artículos agregados al carrito': 'sum',
                    'Importe gastado (CLP)': 'sum'
                }).reset_index()
                df_conv_combinado.rename(columns={'Día': 'Día'}, inplace=True)
                titulo_conv_filtrado = 'Evolución Semanal de Conversiones y Gasto por Combinación'
            else:
                df_conv_combinado = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('M').dt.start_time, 'Público', 'Tipo_Anuncio']).agg({
                    'Artículos agregados al carrito': 'sum',
                    'Importe gastado (CLP)': 'sum'
                }).reset_index()
                df_conv_combinado.rename(columns={'Día': 'Día'}, inplace=True)
                titulo_conv_filtrado = 'Evolución Mensual de Conversiones y Gasto por Combinación'
            
            # Aplicar filtros
            if filtro_publico_conv != 'todos':
                df_conv_combinado = df_conv_combinado[df_conv_combinado['Público'] == filtro_publico_conv]
            if filtro_tipo_conv != 'todos':
                df_conv_combinado = df_conv_combinado[df_conv_combinado['Tipo_Anuncio'] == filtro_tipo_conv]
            
            fig_evolucion_conv_filtrado = go.Figure()
            
            # Crear combinación única
            df_conv_combinado['Combinacion'] = df_conv_combinado['Público'] + ' - ' + df_conv_combinado['Tipo_Anuncio']
            
            # Agregar líneas según métricas seleccionadas
            combinaciones = df_conv_combinado['Combinacion'].unique()
            
            for i, combinacion in enumerate(combinaciones):
                df_combinacion = df_conv_combinado[df_conv_combinado['Combinacion'] == combinacion]
                color = obtener_color_combinacion(i)
                
                # Métrica eje izquierdo
                if filtro_metric_izq_conv != 'ninguno':
                    if filtro_metric_izq_conv == 'conversiones':
                        y_data = df_combinacion['Artículos agregados al carrito']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>Conversiones: %{{y}}<extra></extra>'
                    else:  # gasto
                        y_data = df_combinacion['Importe gastado (CLP)']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>Gasto: $%{{y:,.0f}}<extra></extra>'
                    
                    fig_evolucion_conv_filtrado.add_trace(go.Scatter(
                        x=df_combinacion['Día'],
                        y=y_data,
                        mode='lines+markers',
                        name=f'{filtro_metric_izq_conv.title()}: {combinacion}',
                        line=dict(color=color, width=2),
                        marker=dict(size=6),
                        yaxis='y',
                        hovertemplate=hover_template
                    ))
                
                # Métrica eje derecho
                if filtro_metric_der_conv != 'ninguno':
                    if filtro_metric_der_conv == 'conversiones':
                        y_data = df_combinacion['Artículos agregados al carrito']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>Conversiones: %{{y}}<extra></extra>'
                    else:  # gasto
                        y_data = df_combinacion['Importe gastado (CLP)']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>Gasto: $%{{y:,.0f}}<extra></extra>'
                    
                    fig_evolucion_conv_filtrado.add_trace(go.Scatter(
                        x=df_combinacion['Día'],
                        y=y_data,
                        mode='lines+markers',
                        name=f'{filtro_metric_der_conv.title()}: {combinacion}',
                        line=dict(color=color, width=2, dash='dash'),
                        marker=dict(size=6, symbol='diamond'),
                        yaxis='y2',
                        hovertemplate=hover_template
                    ))
            
            # Configurar layout
            layout_yaxis = {}
            layout_yaxis2 = {}
            
            if filtro_metric_izq_conv != 'ninguno':
                titulo_eje_izq = 'Conversiones' if filtro_metric_izq_conv == 'conversiones' else 'Gasto (CLP)'
                layout_yaxis = dict(
                    title=titulo_eje_izq,
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    side='left'
                )
            
            if filtro_metric_der_conv != 'ninguno':
                titulo_eje_der = 'Conversiones' if filtro_metric_der_conv == 'conversiones' else 'Gasto (CLP)'
                layout_yaxis2 = dict(
                    title=titulo_eje_der,
                    showgrid=False,
                    side='right',
                    overlaying='y'
                )
            
            fig_evolucion_conv_filtrado.update_layout(
                title=titulo_conv_filtrado,
                xaxis_title='Período',
                height=500,
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    tickfont={'color': COLORS['text']},
                    title_font={'color': COLORS['text']}
                ),
                yaxis=layout_yaxis,
                yaxis2=layout_yaxis2,
                legend=dict(
                    font=dict(color=COLORS['text']),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified'
            )
            
            # 5. Gráfico de evolución de costos con filtros
            if periodo == 'D':
                df_costos_combinado = df_filtrado_sin_region.groupby(['Día', 'Público', 'Tipo_Anuncio']).agg({
                    'Importe gastado (CLP)': 'sum',
                    'Clics en el enlace': 'sum',
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                titulo_costos = 'Evolución Diaria de Costos por Combinación'
            elif periodo == 'W':
                df_costos_combinado = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('W').dt.start_time, 'Público', 'Tipo_Anuncio']).agg({
                    'Importe gastado (CLP)': 'sum',
                    'Clics en el enlace': 'sum',
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_costos_combinado.rename(columns={'Día': 'Día'}, inplace=True)
                titulo_costos = 'Evolución Semanal de Costos por Combinación'
            else:
                df_costos_combinado = df_filtrado_sin_region.groupby([df_filtrado_sin_region['Día'].dt.to_period('M').dt.start_time, 'Público', 'Tipo_Anuncio']).agg({
                    'Importe gastado (CLP)': 'sum',
                    'Clics en el enlace': 'sum',
                    'Artículos agregados al carrito': 'sum'
                }).reset_index()
                df_costos_combinado.rename(columns={'Día': 'Día'}, inplace=True)
                titulo_costos = 'Evolución Mensual de Costos por Combinación'
            
            # Calcular CPC y costo por conversión
            df_costos_combinado['CPC'] = (df_costos_combinado['Importe gastado (CLP)'] / df_costos_combinado['Clics en el enlace']).fillna(0)
            df_costos_combinado['Costo_Por_Conversion'] = (df_costos_combinado['Importe gastado (CLP)'] / df_costos_combinado['Artículos agregados al carrito']).fillna(0)
            
            # Aplicar filtros
            if filtro_publico_costos != 'todos':
                df_costos_combinado = df_costos_combinado[df_costos_combinado['Público'] == filtro_publico_costos]
            if filtro_tipo_costos != 'todos':
                df_costos_combinado = df_costos_combinado[df_costos_combinado['Tipo_Anuncio'] == filtro_tipo_costos]
            
            fig_evolucion_costos = go.Figure()
            
            # Crear combinación única
            df_costos_combinado['Combinacion'] = df_costos_combinado['Público'] + ' - ' + df_costos_combinado['Tipo_Anuncio']
            
            # Agregar líneas según métricas seleccionadas
            combinaciones_costos = df_costos_combinado['Combinacion'].unique()
            
            for i, combinacion in enumerate(combinaciones_costos):
                df_combinacion = df_costos_combinado[df_costos_combinado['Combinacion'] == combinacion]
                color = obtener_color_combinacion(i)
                
                # Métrica eje izquierdo
                if filtro_metric_izq_costos != 'ninguno':
                    if filtro_metric_izq_costos == 'cpc':
                        y_data = df_combinacion['CPC']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>CPC: $%{{y:,.0f}}<extra></extra>'
                    else:  # costo_conversion
                        y_data = df_combinacion['Costo_Por_Conversion']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>Costo por Conversión: $%{{y:,.0f}}<extra></extra>'
                    
                    fig_evolucion_costos.add_trace(go.Scatter(
                        x=df_combinacion['Día'],
                        y=y_data,
                        mode='lines+markers',
                        name=f'{filtro_metric_izq_costos.upper()}: {combinacion}',
                        line=dict(color=color, width=2),
                        marker=dict(size=6),
                        yaxis='y',
                        hovertemplate=hover_template
                    ))
                
                # Métrica eje derecho
                if filtro_metric_der_costos != 'ninguno':
                    if filtro_metric_der_costos == 'cpc':
                        y_data = df_combinacion['CPC']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>CPC: $%{{y:,.0f}}<extra></extra>'
                    else:  # costo_conversion
                        y_data = df_combinacion['Costo_Por_Conversion']
                        hover_template = f'<b>{combinacion}</b><br>Fecha: %{{x}}<br>Costo por Conversión: $%{{y:,.0f}}<extra></extra>'
                    
                    fig_evolucion_costos.add_trace(go.Scatter(
                        x=df_combinacion['Día'],
                        y=y_data,
                        mode='lines+markers',
                        name=f'{filtro_metric_der_costos.upper()}: {combinacion}',
                        line=dict(color=color, width=2, dash='dash'),
                        marker=dict(size=6, symbol='diamond'),
                        yaxis='y2',
                        hovertemplate=hover_template
                    ))
            
            # Configurar layout para costos
            layout_yaxis_costos = {}
            layout_yaxis2_costos = {}
            
            if filtro_metric_izq_costos != 'ninguno':
                titulo_eje_izq_costos = 'CPC (CLP)' if filtro_metric_izq_costos == 'cpc' else 'Costo por Conversión (CLP)'
                layout_yaxis_costos = dict(
                    title=titulo_eje_izq_costos,
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    side='left'
                )
            
            if filtro_metric_der_costos != 'ninguno':
                titulo_eje_der_costos = 'CPC (CLP)' if filtro_metric_der_costos == 'cpc' else 'Costo por Conversión (CLP)'
                layout_yaxis2_costos = dict(
                    title=titulo_eje_der_costos,
                    showgrid=False,
                    side='right',
                    overlaying='y'
                )
            
            fig_evolucion_costos.update_layout(
                title=titulo_costos,
                xaxis_title='Período',
                height=500,
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(
                    showgrid=True,
                    gridcolor=COLORS['grid'],
                    tickfont={'color': COLORS['text']},
                    title_font={'color': COLORS['text']}
                ),
                yaxis=layout_yaxis_costos,
                yaxis2=layout_yaxis2_costos,
                legend=dict(
                    font=dict(color=COLORS['text']),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                hovermode='x unified'
            )
            
            # 6. Gráfico por región con tema oscuro
            if df_filtrado_con_region.empty:
                fig_regiones = go.Figure()
                fig_regiones.update_layout(
                    title="No hay datos regionales para el período seleccionado",
                    paper_bgcolor=COLORS['card_bg'],
                    plot_bgcolor=COLORS['card_bg'],
                    font={'color': COLORS['text']}
                )
            else:
                df_regiones = df_filtrado_con_region.groupby('Región').agg({
                    'Importe gastado (CLP)': 'sum',
                    'Impresiones': 'sum',
                    'Clics en el enlace': 'sum'
                }).reset_index()
                df_regiones = df_regiones.sort_values('Importe gastado (CLP)', ascending=True).tail(10)
                
                fig_regiones = go.Figure(go.Bar(
                    x=df_regiones['Importe gastado (CLP)'],
                    y=df_regiones['Región'],
                    orientation='h',
                    marker_color=COLORS['primary'],
                    text=df_regiones['Importe gastado (CLP)'].apply(lambda x: f'${x:,.0f}'),
                    textposition='auto'
                ))
                
                fig_regiones.update_layout(
                    title='Gasto por Región',
                    xaxis_title='Gasto (CLP)',
                    height=400,
                    paper_bgcolor=COLORS['card_bg'],
                    plot_bgcolor=COLORS['card_bg'],
                    font={'color': COLORS['text']},
                    xaxis=dict(
                        showgrid=True,
                        gridcolor=COLORS['grid'],
                        tickfont={'color': COLORS['text']},
                        title_font={'color': COLORS['text']}
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor=COLORS['grid'],
                        tickfont={'color': COLORS['text']},
                        title_font={'color': COLORS['text']}
                    )
                )
            
            # 7. Gráfico por públicos con tema oscuro
            df_publicos = df_filtrado_sin_region.groupby('Público').agg({
                'Importe gastado (CLP)': 'sum',
                'Impresiones': 'sum',
                'Clics en el enlace': 'sum',
                'Artículos agregados al carrito': 'sum'
            }).reset_index()
            
            df_publicos['CTR (%)'] = (df_publicos['Clics en el enlace'] / df_publicos['Impresiones'] * 100).fillna(0)
            df_publicos['CPC (CLP)'] = (df_publicos['Importe gastado (CLP)'] / df_publicos['Clics en el enlace']).fillna(0)
            df_publicos['Conversión (%)'] = (df_publicos['Artículos agregados al carrito'] / df_publicos['Clics en el enlace'] * 100).fillna(0)
            df_publicos['Costo por Conversión (CLP)'] = (df_publicos['Importe gastado (CLP)'] / df_publicos['Artículos agregados al carrito']).fillna(0)
            
            fig_publicos = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Gasto Total (CLP)',
                    'CTR (%)',
                    'CPC (CLP)',
                    'Conversión (%)',
                    'Costo por Conversión (CLP)',
                    'Artículos agregados al carrito'
                ),
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            # Colores para cada métrica
            colors = [COLORS['expense'], COLORS['secondary'], '#9b59b6', COLORS['income'], '#e67e22', COLORS['primary']]
            
            # Añadir barras para cada métrica
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Importe gastado (CLP)'], marker_color=colors[0], showlegend=False), row=1, col=1)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['CTR (%)'], marker_color=colors[1], showlegend=False), row=1, col=2)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['CPC (CLP)'], marker_color=colors[2], showlegend=False), row=2, col=1)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Conversión (%)'], marker_color=colors[3], showlegend=False), row=2, col=2)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Costo por Conversión (CLP)'], marker_color=colors[4], showlegend=False), row=3, col=1)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Artículos agregados al carrito'], marker_color=colors[5], showlegend=False), row=3, col=2)
            
            # Rotar etiquetas del eje x para públicos
            fig_publicos.update_xaxes(tickangle=45)
            
            # 8. Gráfico por tipos de anuncios con tema oscuro
            df_tipos = df_filtrado_sin_region.groupby('Tipo_Anuncio').agg({
                'Importe gastado (CLP)': 'sum',
                'Impresiones': 'sum',
                'Clics en el enlace': 'sum',
                'Artículos agregados al carrito': 'sum'
            }).reset_index()
            
            df_tipos['CTR (%)'] = (df_tipos['Clics en el enlace'] / df_tipos['Impresiones'] * 100).fillna(0)
            df_tipos['CPC (CLP)'] = (df_tipos['Importe gastado (CLP)'] / df_tipos['Clics en el enlace']).fillna(0)
            df_tipos['Conversión (%)'] = (df_tipos['Artículos agregados al carrito'] / df_tipos['Clics en el enlace'] * 100).fillna(0)
            df_tipos['Costo por Conversión (CLP)'] = (df_tipos['Importe gastado (CLP)'] / df_tipos['Artículos agregados al carrito']).fillna(0)
            
            fig_tipos = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Gasto Total (CLP)',
                    'CTR (%)',
                    'CPC (CLP)',
                    'Conversión (%)',
                    'Costo por Conversión (CLP)',
                    'Artículos agregados al carrito'
                ),
                vertical_spacing=0.15,
                horizontal_spacing=0.1
            )
            
            # Añadir barras para cada métrica
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Importe gastado (CLP)'], marker_color=colors[0], showlegend=False), row=1, col=1)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CTR (%)'], marker_color=colors[1], showlegend=False), row=1, col=2)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CPC (CLP)'], marker_color=colors[2], showlegend=False), row=2, col=1)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Conversión (%)'], marker_color=colors[3], showlegend=False), row=2, col=2)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Costo por Conversión (CLP)'], marker_color=colors[4], showlegend=False), row=3, col=1)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Artículos agregados al carrito'], marker_color=colors[5], showlegend=False), row=3, col=2)
            
            # Rotar etiquetas del eje x para tipos de anuncios
            fig_tipos.update_xaxes(tickangle=45)
            
            # 9. Gráfico de Hook Rates con tema oscuro
            df_hooks = df_filtrado_sin_region.groupby('Tipo_Anuncio').agg({
                'Hook_Rate_3s': 'mean',
                'Hook_Rate_25': 'mean',
                'Hook_Rate_50': 'mean',
                'Hook_Rate_75': 'mean',
                'Hook_Rate_100': 'mean'
            }).reset_index()
            
            # Ordenar por Hook Rate 3s
            df_hooks = df_hooks.sort_values('Hook_Rate_3s', ascending=True)
            
            # Colores específicos para cada hook rate
            colors_hooks = {
                '3s': '#FF9999',
                '25%': '#66B2FF', 
                '50%': '#99FF99',
                '75%': '#FFCC99',
                '100%': '#FF99CC'
            }
            
            fig_hooks = go.Figure()
            
            # Añadir cada hook rate como una barra horizontal separada
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_3s'],
                name='3 segundos',
                orientation='h',
                marker_color=colors_hooks['3s'],
                hovertemplate='Hook Rate 3s: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_25'],
                name='25%',
                orientation='h',
                marker_color=colors_hooks['25%'],
                hovertemplate='Hook Rate 25%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_50'],
                name='50%',
                orientation='h',
                marker_color=colors_hooks['50%'],
                hovertemplate='Hook Rate 50%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_75'],
                name='75%',
                orientation='h',
                marker_color=colors_hooks['75%'],
                hovertemplate='Hook Rate 75%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_100'],
                name='100%',
                orientation='h',
                marker_color=colors_hooks['100%'],
                hovertemplate='Hook Rate 100%: %{x:.2f}%<br><extra></extra>'
            ))
            
            # Configurar todos los gráficos con tema oscuro
            for fig in [fig_evolucion_conv_filtrado, fig_evolucion_costos, fig_hooks]:
                fig.update_layout(
                    paper_bgcolor=COLORS['card_bg'],
                    plot_bgcolor=COLORS['card_bg'],
                    font={'color': COLORS['text']},
                    xaxis=dict(
                        showgrid=True,
                        gridcolor=COLORS['grid'],
                        tickfont={'color': COLORS['text']},
                        title_font={'color': COLORS['text']}
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor=COLORS['grid'],
                        tickfont={'color': COLORS['text']},
                        title_font={'color': COLORS['text']}
                    ),
                    legend=dict(font=dict(color=COLORS['text']))
                )
            
            # Configuraciones específicas
            fig_evolucion_conv_filtrado.update_layout(
                title='Evolución de Conversiones y Gasto por Combinación',
                height=800
            )
            
            fig_evolucion_costos.update_layout(
                title='Evolución de Costos por Combinación',
                height=800
            )
            
            fig_hooks.update_layout(
                title='Hook Rates por Tipo de Anuncio',
                height=500,
                barmode='group',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                margin=dict(l=200)
            )
            
            # 8. Generar insights con estilo oscuro
            dias_analizados = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
            gasto_promedio_diario = total_gasto / dias_analizados if dias_analizados > 0 else 0
            
            # Mejor región (de los datos con región)
            mejor_region = None
            if not df_filtrado_con_region.empty:
                df_regiones_insight = df_filtrado_con_region.groupby('Región')['Importe gastado (CLP)'].sum().reset_index()
                if not df_regiones_insight.empty:
                    mejor_region = df_regiones_insight.loc[df_regiones_insight['Importe gastado (CLP)'].idxmax()]
            
            # Mejor público (de los datos sin región)
            mejor_publico = df_publicos.loc[df_publicos['Importe gastado (CLP)'].idxmax()] if not df_publicos.empty else None
            
            insights = [
                html.P(f"📊 Análisis del período: {dias_analizados} días", style={
                    'fontWeight': 'bold', 
                    'fontSize': '16px',
                    'color': COLORS['text']
                }),
                html.P(f"💰 Gasto promedio diario: ${gasto_promedio_diario:,.0f}", style={'color': COLORS['text']}),
                html.P(f"📈 CTR promedio: {ctr:.2f}%", style={'color': COLORS['text']}),
                html.P(f"💸 CPC promedio: ${cpc:,.0f}", style={'color': COLORS['text']}),
                html.P(f"📋 Datos procesados: {len(df_filtrado_sin_region)} registros principales, {len(df_filtrado_con_region)} registros regionales", style={'color': COLORS['text']}),
            ]
            
            if mejor_region is not None:
                insights.append(html.P(f"🎯 Región con mayor gasto: {mejor_region['Región']} (${mejor_region['Importe gastado (CLP)']:,.0f})", style={'color': COLORS['text']}))
            
            if mejor_publico is not None:
                insights.append(html.P(f"👥 Público con mejor rendimiento: {mejor_publico['Público']} (${mejor_publico['Importe gastado (CLP)']:,.0f})", style={'color': COLORS['text']}))
            
            insights_contenido = html.Div(insights)
            
            return metricas, seccion_performance, fig_evolucion, fig_evolucion_conv, fig_evolucion_conv_filtrado, fig_evolucion_costos, fig_regiones, fig_publicos, fig_tipos, fig_hooks, insights_contenido
            
        except Exception as e:
            print(f"Error en callback: {str(e)}")
            import traceback
            traceback.print_exc()
            empty_fig = go.Figure()
            empty_fig.update_layout(
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']}
            )
            return (html.Div("Error al cargar datos", style={'color': COLORS['text']}), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Error en insights")

else:
    app.layout = html.Div([
        html.H1("Error: No se pudieron cargar los datos", style={
            'textAlign': 'center', 
            'color': COLORS['expense'],
            'backgroundColor': COLORS['background'],
            'minHeight': '100vh',
            'padding': '20px'
        })
    ], style={'backgroundColor': COLORS['background']})

if __name__ == '__main__':
    print("\n=== DASHBOARD DE MARKETING COMPLETO ===")
    print("Datos cargados exitosamente")
    print("Iniciando servidor en http://localhost:8056")
    app.run(debug=False, port=8056) 