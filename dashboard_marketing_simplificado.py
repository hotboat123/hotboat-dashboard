import dash
from dash import dcc, html, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import dash_bootstrap_components as dbc

# Agregar el directorio de funciones al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'funciones'))

from funciones.componentes_dashboard import crear_header, crear_filtros, crear_selector_periodo, COLORS, CARD_STYLE

# Configuración del tema oscuro
COLORS = {
    'background': '#1a1a1a',
    'card_bg': '#2d2d2d',
    'text': '#ffffff',
    'primary': '#00d4aa',
    'secondary': '#ff6b6b',
    'expense': '#ff4757',
    'income': '#2ed573',
    'grid': '#404040'
}

CARD_STYLE = {
    'backgroundColor': COLORS['card_bg'],
    'padding': '20px',
    'borderRadius': '10px',
    'margin': '10px',
    'textAlign': 'center',
    'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)',
    'minWidth': '150px'
}

def cargar_datos():
    """Cargar y procesar los datos de marketing"""
    try:
        # Cargar archivos con nombres específicos
        print("🔄 Cargando archivo CON región (5): archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_con_region.csv")
        df_con_region = pd.read_csv('archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_con_region.csv')
        print(f"✅ Archivo CON región (5) cargado. Dimensiones: {df_con_region.shape}")
        
        print("🔄 Cargando archivo SIN región (6): archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv")
        df_sin_region = pd.read_csv('archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia_sin_region.csv')
        print(f"✅ Archivo SIN región (6) cargado. Dimensiones: {df_sin_region.shape}")
        
        print("📊 USANDO NUEVOS INPUTS ESPECÍFICOS:")
        print(f"   📈 Dataset (6): {len(df_sin_region)} filas - Sin región")
        print(f"   🗺️ Dataset (5): {len(df_con_region)} filas - Con región")
        print("🎉 Ambos archivos procesados exitosamente con nuevos inputs")
        
        # Convertir columna de fecha
        df_sin_region['Día'] = pd.to_datetime(df_sin_region['Día'], dayfirst=False)
        df_con_region['Día'] = pd.to_datetime(df_con_region['Día'], dayfirst=False)
        
        # Clasificar tipos de anuncios
        def clasificar_tipo_anuncio(x):
            if 'Video pareja dcto' in str(x) or 'Video parejas dcto' in str(x):
                return 'Video pareja dcto'
            elif 'Video Lluvia' in str(x):
                return 'Video Lluvia'
            elif 'Video pareja' in str(x):
                return 'Video pareja'
            elif 'Video parejas' in str(x):
                return 'Video parejas'
            else:
                return 'Otro'
        
        df_sin_region['Tipo_Anuncio'] = df_sin_region['Nombre del anuncio'].apply(clasificar_tipo_anuncio)
        df_con_region['Tipo_Anuncio'] = df_con_region['Nombre del anuncio'].apply(clasificar_tipo_anuncio)
        
        # Clasificar públicos - verificar si la columna existe
        if 'Público' in df_sin_region.columns:
            def clasificar_publico(x):
                if 'Advantage' in str(x):
                    return 'Advantage'
                elif 'Pucón' in str(x):
                    return 'Pucón'
                elif 'Concepción' in str(x):
                    return 'Concepción'
                elif 'Valdivia' in str(x):
                    return 'Valdivia'
                elif 'Temuco' in str(x):
                    return 'Temuco'
                else:
                    return 'Otro'
            
            df_sin_region['Público'] = df_sin_region['Público'].apply(clasificar_publico)
            df_con_region['Público'] = df_con_region['Público'].apply(clasificar_publico)
        else:
            # Si no existe la columna Público, crear una columna por defecto
            df_sin_region['Público'] = 'General'
            df_con_region['Público'] = 'General'
            print("⚠️ No se encontró columna 'Público', usando 'General' por defecto")
        
        print(f"✅ Dataset (5) CON región: {len(df_con_region)} filas")
        print(f"✅ Dataset (6) SIN región: {len(df_sin_region)} filas")
        
        return df_sin_region, df_con_region
        
    except Exception as e:
        print(f"❌ Error al cargar datos: {str(e)}")
        return None, None

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Cargar datos
df_sin_region, df_con_region = cargar_datos()

if df_sin_region is not None and df_con_region is not None:
    # Layout del dashboard
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("📊 Dashboard Marketing Simplificado", style={
                'textAlign': 'center', 
                'color': COLORS['primary'],
                'marginBottom': '20px',
                'fontWeight': 'bold'
            }),
            html.P("Análisis rápido y fácil de interpretar", style={
                'textAlign': 'center', 
                'color': COLORS['text'],
                'marginBottom': '30px'
            })
        ], style={'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '10px', 'marginBottom': '20px'}),
        
        # Controles
        html.Div([
            html.Div([
                html.Label("Rango de fechas:", style={'color': COLORS['text'], 'fontWeight': 'bold'}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    start_date=df_sin_region['Día'].min(),
                    end_date=df_sin_region['Día'].max(),
                    display_format='DD/MM/YYYY',
                    style={'backgroundColor': COLORS['card_bg']}
                )
            ], style={'marginRight': '20px'}),
            html.Div([
                html.Label("Período:", style={'color': COLORS['text'], 'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='periodo-selector',
                    options=[
                        {'label': 'Todo el período', 'value': 'todo'},
                        {'label': 'Últimos 7 días', 'value': '7dias'},
                        {'label': 'Últimos 30 días', 'value': '30dias'}
                    ],
                    value='todo',
                    style={'backgroundColor': COLORS['card_bg']}
                )
            ])
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
        
        # Métricas principales
        html.Div(id='metricas-principales', style={'marginBottom': '30px'}),
        
        # Sección Winners & Losers
        html.Div([
            html.H2("🏆 Winners & Losers", style={
                'textAlign': 'center', 
                'color': COLORS['primary'],
                'marginBottom': '20px'
            }),
            html.Div([
                html.Div([
                    html.H3("🥇 Top Performers", style={'color': COLORS['income'], 'textAlign': 'center'}),
                    html.Div(id='top-performers', style={'padding': '15px'})
                ], style={'flex': '1', 'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '10px', 'marginRight': '10px'}),
                html.Div([
                    html.H3("⚠️ Necesita Atención", style={'color': COLORS['expense'], 'textAlign': 'center'}),
                    html.Div(id='necesita-atencion', style={'padding': '15px'})
                ], style={'flex': '1', 'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '10px', 'marginLeft': '10px'})
            ], style={'display': 'flex', 'marginBottom': '30px', 'flexWrap': 'wrap'})
        ]),
        
        # Gráficos simplificados
        html.Div([
            html.H2("📈 Análisis Visual", style={
                'textAlign': 'center', 
                'color': COLORS['primary'],
                'marginBottom': '20px'
            }),
            html.Div([
                html.Div([
                    dcc.Graph(id='grafico-conversiones-simple')
                ], style={'flex': '1', 'marginRight': '10px'}),
                html.Div([
                    dcc.Graph(id='grafico-gasto-simple')
                ], style={'flex': '1', 'marginLeft': '10px'})
            ], style={'display': 'flex', 'marginBottom': '20px', 'flexWrap': 'wrap'}),
            html.Div([
                html.Div([
                    dcc.Graph(id='grafico-cpc-simple')
                ], style={'flex': '1', 'marginRight': '10px'}),
                html.Div([
                    dcc.Graph(id='grafico-costo-conversion-simple')
                ], style={'flex': '1', 'marginLeft': '10px'})
            ], style={'display': 'flex', 'flexWrap': 'wrap'})
        ]),
        
        # Tabla resumen
        html.Div([
            html.H2("📋 Resumen Detallado", style={
                'textAlign': 'center', 
                'color': COLORS['primary'],
                'marginBottom': '20px'
            }),
            html.Div(id='tabla-resumen', style={'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '10px'})
        ], style={'marginBottom': '30px'}),
        
        # Insights automáticos
        html.Div([
            html.H2("💡 Insights Automáticos", style={
                'textAlign': 'center', 
                'color': COLORS['primary'],
                'marginBottom': '20px'
            }),
            html.Div(id='insights-simplificado', style={'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'borderRadius': '10px'})
        ])
    ], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'padding': '20px'})
    
    # Callback para actualizar el dashboard
    @app.callback(
        [Output('metricas-principales', 'children'),
         Output('top-performers', 'children'),
         Output('necesita-atencion', 'children'),
         Output('grafico-conversiones-simple', 'figure'),
         Output('grafico-gasto-simple', 'figure'),
         Output('grafico-cpc-simple', 'figure'),
         Output('grafico-costo-conversion-simple', 'figure'),
         Output('tabla-resumen', 'children'),
         Output('insights-simplificado', 'children')],
        [Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date'),
         Input('periodo-selector', 'value')]
    )
    def actualizar_dashboard_simplificado(start_date, end_date, periodo):
        try:
            # Filtrar datos por fecha
            df_filtrado = df_sin_region.copy()
            
            if start_date and end_date:
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                df_filtrado = df_filtrado[(df_filtrado['Día'] >= start_date) & (df_filtrado['Día'] <= end_date)]
            
            if periodo == '7dias':
                ultima_fecha = df_filtrado['Día'].max()
                df_filtrado = df_filtrado[df_filtrado['Día'] >= (ultima_fecha - pd.Timedelta(days=7))]
            elif periodo == '30dias':
                ultima_fecha = df_filtrado['Día'].max()
                df_filtrado = df_filtrado[df_filtrado['Día'] >= (ultima_fecha - pd.Timedelta(days=30))]
            
            if df_filtrado.empty:
                empty_fig = go.Figure()
                empty_fig.update_layout(
                    paper_bgcolor=COLORS['card_bg'],
                    plot_bgcolor=COLORS['card_bg'],
                    font={'color': COLORS['text']}
                )
                return (html.Div("No hay datos para el período seleccionado", style={'color': COLORS['text']}), 
                       "No hay datos", "No hay datos", empty_fig, empty_fig, empty_fig, empty_fig, "No hay datos", "No hay insights")
            
            # Calcular métricas principales
            total_gasto = df_filtrado['Importe gastado (CLP)'].sum()
            total_conversiones = df_filtrado['Artículos agregados al carrito'].sum()
            total_clics = df_filtrado['Clics en el enlace'].sum()
            ctr = (total_clics / df_filtrado['Impresiones'].sum() * 100) if df_filtrado['Impresiones'].sum() > 0 else 0
            cpc = (total_gasto / total_clics) if total_clics > 0 else 0
            
            # 1. Métricas principales
            metricas = html.Div([
                html.Div([
                    html.H3(f'${total_gasto:,.0f}', style={'color': COLORS['expense'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('Gasto Total', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                html.Div([
                    html.H3(f'{total_conversiones:,.0f}', style={'color': COLORS['income'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('Conversiones', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                html.Div([
                    html.H3(f'{ctr:.2f}%', style={'color': COLORS['secondary'], 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('CTR Promedio', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE),
                html.Div([
                    html.H3(f'${cpc:,.0f}', style={'color': '#9b59b6', 'margin': '0', 'fontSize': '2.5em'}),
                    html.P('CPC Promedio', style={'margin': '5px 0', 'fontWeight': 'bold', 'color': COLORS['text']})
                ], style=CARD_STYLE)
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'})
            
            # 2. Análisis por combinación público-tipo
            df_combinaciones = df_filtrado.groupby(['Público', 'Tipo_Anuncio']).agg({
                'Importe gastado (CLP)': 'sum',
                'Artículos agregados al carrito': 'sum',
                'Clics en el enlace': 'sum',
                'Impresiones': 'sum'
            }).reset_index()
            
            df_combinaciones['CPC'] = (df_combinaciones['Importe gastado (CLP)'] / df_combinaciones['Clics en el enlace']).fillna(0)
            df_combinaciones['Costo por Conversión'] = (df_combinaciones['Importe gastado (CLP)'] / df_combinaciones['Artículos agregados al carrito']).fillna(0)
            df_combinaciones['CTR'] = (df_combinaciones['Clics en el enlace'] / df_combinaciones['Impresiones'] * 100).fillna(0)
            df_combinaciones['ROI'] = (df_combinaciones['Artículos agregados al carrito'] / df_combinaciones['Importe gastado (CLP)'] * 1000).fillna(0)  # Conversiones por $1000
            
            # Top performers (por ROI)
            top_performers = df_combinaciones.nlargest(3, 'ROI')
            top_performers_html = []
            for _, row in top_performers.iterrows():
                top_performers_html.append(html.Div([
                    html.Strong(f"{row['Público']} - {row['Tipo_Anuncio']}", style={'color': COLORS['income']}),
                    html.Br(),
                    html.Span(f"ROI: {row['ROI']:.1f} conv/$1000", style={'color': COLORS['text']}),
                    html.Br(),
                    html.Span(f"Conversiones: {row['Artículos agregados al carrito']:.0f}", style={'color': COLORS['text']})
                ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': COLORS['background'], 'borderRadius': '5px'}))
            
            # Necesita atención (por costo por conversión alto)
            necesita_atencion = df_combinaciones.nlargest(3, 'Costo por Conversión')
            necesita_atencion_html = []
            for _, row in necesita_atencion.iterrows():
                necesita_atencion_html.append(html.Div([
                    html.Strong(f"{row['Público']} - {row['Tipo_Anuncio']}", style={'color': COLORS['expense']}),
                    html.Br(),
                    html.Span(f"Costo/Conv: ${row['Costo por Conversión']:,.0f}", style={'color': COLORS['text']}),
                    html.Br(),
                    html.Span(f"Conversiones: {row['Artículos agregados al carrito']:.0f}", style={'color': COLORS['text']})
                ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': COLORS['background'], 'borderRadius': '5px'}))
            
            # 3. Gráficos simplificados
            # Gráfico de conversiones (top 5)
            top_conv = df_combinaciones.nlargest(5, 'Artículos agregados al carrito')
            fig_conv = go.Figure(go.Bar(
                x=[f"{row['Público']} - {row['Tipo_Anuncio']}" for _, row in top_conv.iterrows()],
                y=top_conv['Artículos agregados al carrito'],
                marker_color=COLORS['income']
            ))
            fig_conv.update_layout(
                title='Top 5 por Conversiones',
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(tickangle=45),
                height=300
            )
            
            # Gráfico de gasto (top 5)
            top_gasto = df_combinaciones.nlargest(5, 'Importe gastado (CLP)')
            fig_gasto = go.Figure(go.Bar(
                x=[f"{row['Público']} - {row['Tipo_Anuncio']}" for _, row in top_gasto.iterrows()],
                y=top_gasto['Importe gastado (CLP)'],
                marker_color=COLORS['expense']
            ))
            fig_gasto.update_layout(
                title='Top 5 por Gasto',
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(tickangle=45),
                height=300
            )
            
            # Gráfico de CPC (top 5)
            top_cpc = df_combinaciones.nlargest(5, 'CPC')
            fig_cpc = go.Figure(go.Bar(
                x=[f"{row['Público']} - {row['Tipo_Anuncio']}" for _, row in top_cpc.iterrows()],
                y=top_cpc['CPC'],
                marker_color='#9b59b6'
            ))
            fig_cpc.update_layout(
                title='Top 5 por CPC',
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(tickangle=45),
                height=300
            )
            
            # Gráfico de costo por conversión (top 5)
            top_costo_conv = df_combinaciones.nlargest(5, 'Costo por Conversión')
            fig_costo_conv = go.Figure(go.Bar(
                x=[f"{row['Público']} - {row['Tipo_Anuncio']}" for _, row in top_costo_conv.iterrows()],
                y=top_costo_conv['Costo por Conversión'],
                marker_color='#e67e22'
            ))
            fig_costo_conv.update_layout(
                title='Top 5 por Costo por Conversión',
                paper_bgcolor=COLORS['card_bg'],
                plot_bgcolor=COLORS['card_bg'],
                font={'color': COLORS['text']},
                xaxis=dict(tickangle=45),
                height=300
            )
            
            # 4. Tabla resumen
            tabla_data = []
            for _, row in df_combinaciones.iterrows():
                tabla_data.append({
                    'Combinación': f"{row['Público']} - {row['Tipo_Anuncio']}",
                    'Conversiones': f"{row['Artículos agregados al carrito']:.0f}",
                    'Gasto': f"${row['Importe gastado (CLP)']:,.0f}",
                    'CPC': f"${row['CPC']:,.0f}",
                    'Costo/Conv': f"${row['Costo por Conversión']:,.0f}",
                    'CTR': f"{row['CTR']:.2f}%",
                    'ROI': f"{row['ROI']:.1f}"
                })
            
            tabla_html = html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([html.Th(col, style={'color': COLORS['text'], 'padding': '10px'}) for col in tabla_data[0].keys()])
                    ]),
                    html.Tbody([
                        html.Tr([html.Td(tabla_data[i][col], style={'color': COLORS['text'], 'padding': '8px'}) for col in tabla_data[i].keys()])
                        for i in range(len(tabla_data))
                    ])
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
            ])
            
            # 5. Insights automáticos
            mejor_roi = df_combinaciones.loc[df_combinaciones['ROI'].idxmax()]
            peor_costo = df_combinaciones.loc[df_combinaciones['Costo por Conversión'].idxmax()]
            mas_conversiones = df_combinaciones.loc[df_combinaciones['Artículos agregados al carrito'].idxmax()]
            
            insights = [
                html.P(f"🎯 **Mejor ROI**: {mejor_roi['Público']} - {mejor_roi['Tipo_Anuncio']} ({mejor_roi['ROI']:.1f} conv/$1000)", style={'color': COLORS['income']}),
                html.P(f"⚠️ **Costo más alto**: {peor_costo['Público']} - {peor_costo['Tipo_Anuncio']} (${peor_costo['Costo por Conversión']:,.0f} por conversión)", style={'color': COLORS['expense']}),
                html.P(f"📈 **Más conversiones**: {mas_conversiones['Público']} - {mas_conversiones['Tipo_Anuncio']} ({mas_conversiones['Artículos agregados al carrito']:.0f} conversiones)", style={'color': COLORS['primary']}),
                html.P(f"💰 **Recomendación**: Enfócate en {mejor_roi['Público']} - {mejor_roi['Tipo_Anuncio']} y optimiza {peor_costo['Público']} - {peor_costo['Tipo_Anuncio']}", style={'color': COLORS['text']})
            ]
            
            return (metricas, top_performers_html, necesita_atencion_html, 
                   fig_conv, fig_gasto, fig_cpc, fig_costo_conv, tabla_html, insights)
            
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
            return (html.Div("Error al cargar datos", style={'color': COLORS['text']}), 
                   "Error", "Error", empty_fig, empty_fig, empty_fig, empty_fig, "Error", "Error en insights")

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
    print("\n=== DASHBOARD DE MARKETING SIMPLIFICADO ===")
    print("Datos cargados exitosamente")
    print("Iniciando servidor en http://localhost:8057")
    app.run(debug=False, port=8057) 