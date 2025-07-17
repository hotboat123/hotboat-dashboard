#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Utilidad Operativa HotBoat
Muestra la evolución de costos operativos, ingresos operativos y marketing
con filtros por categoría y tiempo (día, semana, mes)
"""

import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import numpy as np
import sys

# Forzar UTF-8 para evitar problemas con emojis en Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Importar componentes comunes de navegación
from funciones.componentes_dashboard import crear_header, crear_filtros, crear_selector_periodo, COLORS, CARD_STYLE

# Colores específicos para las categorías de utilidad operativa
UTILIDAD_COLORS = {
    'ingreso operativo': '#00ff88',  # Verde brillante
    'costo operativo': '#ff6b6b',    # Rojo
    'Costos de Marketing': '#4ecdc4'  # Turquesa
}

def cargar_datos():
    """Carga los datos de utilidad operativa desde el archivo CSV."""
    try:
        print("📊 Cargando datos de utilidad operativa...")
        
        archivo_utilidad = "archivos_output/Utilidad operativa.csv"
        
        if not os.path.exists(archivo_utilidad):
            print(f"❌ ERROR: No se encuentra el archivo: {archivo_utilidad}")
            print("💡 Ejecuta primero: python utilidad_operativa.py")
            return None
        
        df = pd.read_csv(archivo_utilidad)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        print(f"✅ Datos de utilidad operativa cargados: {len(df)} registros")
        print(f"📅 Período: {df['fecha'].min().strftime('%Y-%m-%d')} a {df['fecha'].max().strftime('%Y-%m-%d')}")
        print(f"📋 Categorías: {', '.join(df['categoria'].unique())}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error cargando datos: {str(e)}")
        return None

def aplicar_filtro_tiempo(df, periodo):
    """Aplica filtro de tiempo según el período seleccionado."""
    if df is None or df.empty:
        return df
    
    # Si no hay período seleccionado, devolver todos los datos
    if not periodo:
        return df
    
    # Obtener la fecha máxima de los datos FILTRADOS (no de todos los datos)
    fecha_maxima = df['fecha'].max()
    
    # Calcular fecha de inicio según el período
    if periodo == 'D':  # Día
        fecha_inicio = fecha_maxima
    elif periodo == 'W':  # Semana
        fecha_inicio = fecha_maxima - timedelta(days=7)
    elif periodo == 'M':  # Mes
        fecha_inicio = fecha_maxima - timedelta(days=30)
    else:
        return df  # Período no válido, devolver todos los datos
    
    # Filtrar datos
    df_filtrado = df[df['fecha'] >= fecha_inicio]
    
    print(f"🔍 Filtro '{periodo}': {len(df)} → {len(df_filtrado)} registros")
    print(f"📅 Desde {fecha_inicio} hasta {fecha_maxima}")
    
    return df_filtrado

def crear_grafico_evolucion(df, categorias_filtradas):
    """Crea el gráfico de evolución temporal."""
    if df is None or df.empty:
        return go.Figure().add_annotation(
            text="No hay datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=COLORS['text'])
        )
    
    # Filtrar por categorías seleccionadas
    if categorias_filtradas and 'todos' not in categorias_filtradas:
        df_filtrado = df[df['categoria'].isin(categorias_filtradas)]
    else:
        df_filtrado = df
    
    if df_filtrado.empty:
        return go.Figure().add_annotation(
            text="No hay datos para las categorías seleccionadas",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color=COLORS['text'])
        )
    
    # Agrupar por fecha y categoría
    df_agrupado = df_filtrado.groupby(['fecha', 'categoria'])['monto'].sum().reset_index()
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar línea para cada categoría
    for categoria in df_agrupado['categoria'].unique():
        df_cat = df_agrupado[df_agrupado['categoria'] == categoria]
        color = UTILIDAD_COLORS.get(categoria, '#ffffff')
        
        fig.add_trace(go.Scatter(
            x=df_cat['fecha'],
            y=df_cat['monto'],
            mode='lines+markers',
            name=categoria.title(),
            line=dict(color=color, width=3),
            marker=dict(size=6, color=color),
            hovertemplate='<b>%{x}</b><br>' +
                         f'{categoria.title()}: $%{{y:,.0f}}<br>' +
                         '<extra></extra>'
        ))
    
    # Configurar layout
    fig.update_layout(
        title={
            'text': 'Evolución Temporal de Utilidad Operativa',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': COLORS['text']}
        },
        xaxis_title='Fecha',
        yaxis_title='Monto ($)',
        template='plotly_dark',
        plot_bgcolor=COLORS['card_bg'],
        paper_bgcolor=COLORS['card_bg'],
        font=dict(color=COLORS['text']),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def crear_tarjetas_promedio(df, categorias_filtradas):
    """Crea las tarjetas con valores promedio por categoría."""
    if df is None or df.empty:
        return []
    
    # Filtrar por categorías seleccionadas
    if categorias_filtradas and 'todos' not in categorias_filtradas:
        df_filtrado = df[df['categoria'].isin(categorias_filtradas)]
    else:
        df_filtrado = df
    
    tarjetas = []
    
    for categoria in df_filtrado['categoria'].unique():
        df_cat = df_filtrado[df_filtrado['categoria'] == categoria]
        
        # Calcular métricas
        total = df_cat['monto'].sum()
        promedio = df_cat['monto'].mean()
        count = len(df_cat)
        
        # Color específico para cada categoría
        color = UTILIDAD_COLORS.get(categoria, '#ffffff')
        
        tarjeta = html.Div([
            html.H4(categoria.title(), style={
                'color': COLORS['text'],
                'textAlign': 'center',
                'marginBottom': '10px',
                'fontSize': '16px'
            }),
            html.Div([
                html.Div([
                    html.H3(f"${total:,.0f}", style={
                        'color': color,
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.P("Total", style={
                        'color': COLORS['text'],
                        'textAlign': 'center',
                        'margin': '5px 0 0 0',
                        'fontSize': '12px'
                    })
                ], style={'flex': '1'}),
                html.Div([
                    html.H3(f"${promedio:,.0f}", style={
                        'color': color,
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.P("Promedio", style={
                        'color': COLORS['text'],
                        'textAlign': 'center',
                        'margin': '5px 0 0 0',
                        'fontSize': '12px'
                    })
                ], style={'flex': '1'}),
                html.Div([
                    html.H3(f"{count:,}", style={
                        'color': color,
                        'textAlign': 'center',
                        'margin': '0',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.P("Registros", style={
                        'color': COLORS['text'],
                        'textAlign': 'center',
                        'margin': '5px 0 0 0',
                        'fontSize': '12px'
                    })
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '10px',
            'margin': '10px',
            'flex': '1',
            'minWidth': '250px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)',
            'border': f'2px solid {color}'
        })
        
        tarjetas.append(tarjeta)
    
    return tarjetas

# Crear aplicación
app = dash.Dash(__name__)

# Cargar datos
df_utilidad = cargar_datos()

if df_utilidad is not None:
    fecha_min = df_utilidad['fecha'].min()
    fecha_max = df_utilidad['fecha'].max()
    categorias_disponibles = sorted(df_utilidad['categoria'].unique())
    
    # Layout con tema oscuro consistente
    app.layout = html.Div([
        # Header con navegación
        crear_header("Dashboard de Utilidad Operativa HotBoat", 8057),
        
        # Título del dashboard
        html.Div([
            html.Div("DASHBOARD DE UTILIDAD OPERATIVA", style={
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
        
        # Filtro de categorías
        html.Div([
            html.H3('Filtrar por Categoría:', style={
                'color': COLORS['text'],
                'marginBottom': '15px',
                'fontSize': '18px'
            }),
            dcc.Dropdown(
                id='filtro-categoria',
                options=[
                    {'label': 'Todas las categorías', 'value': 'todos'}
                ] + [
                    {'label': cat.title(), 'value': cat} 
                    for cat in categorias_disponibles
                ],
                value='todos',
                style={
                    'backgroundColor': COLORS['card_bg'],
                    'color': COLORS['text'],
                    'border': '1px solid #444'
                }
            )
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        # Selector de período
        crear_selector_periodo(),
        
        # Tarjetas de métricas promedio
        html.Div([
            html.H3('Métricas por Categoría', style={
                'color': COLORS['text'],
                'marginBottom': '15px',
                'fontSize': '18px'
            }),
            html.Div(id='tarjetas-promedio', style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'center'
            })
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
        }),
        
        # Gráfico de evolución
        html.Div([
            html.H3('Evolución Temporal', style={
                'color': COLORS['text'],
                'marginBottom': '15px',
                'fontSize': '18px'
            }),
            dcc.Graph(id='grafico-evolucion')
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
    
    @callback(
        [Output('tarjetas-promedio', 'children'),
         Output('grafico-evolucion', 'figure')],
        [Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date'),
         Input('periodo-selector', 'value'),
         Input('filtro-categoria', 'value')]
    )
    def actualizar_dashboard(start_date, end_date, periodo, categoria_filtro):
        """Callback principal para actualizar el dashboard."""
        
        # Empezar con todos los datos
        df_filtrado = df_utilidad.copy()
        
        # 1. Aplicar filtro de rango de fechas
        if start_date and end_date:
            # Si hay fechas seleccionadas, usar ese rango
            df_filtrado = df_filtrado[
                (df_filtrado['fecha'] >= start_date) & 
                (df_filtrado['fecha'] <= end_date)
            ]
            print(f"📅 Filtro fecha: {start_date} a {end_date}")
        else:
            # Si no hay fechas seleccionadas, usar fechas por defecto
            start_date = df_utilidad['fecha'].min()
            end_date = df_utilidad['fecha'].max()
            print(f"📅 Usando fechas por defecto: {start_date} a {end_date}")
        
        # 2. Aplicar filtro de período sobre el rango de fechas
        if periodo:
            # Obtener la fecha máxima del rango filtrado
            fecha_max_rango = df_filtrado['fecha'].max()
            
            # Calcular fecha de inicio según el período
            if periodo == 'D':  # Día
                fecha_inicio = fecha_max_rango
            elif periodo == 'W':  # Semana
                fecha_inicio = fecha_max_rango - timedelta(days=7)
            elif periodo == 'M':  # Mes
                fecha_inicio = fecha_max_rango - timedelta(days=30)
            else:
                fecha_inicio = start_date  # Usar fecha de inicio del rango
            
            # Aplicar filtro de período
            df_filtrado = df_filtrado[df_filtrado['fecha'] >= fecha_inicio]
            
            print(f"🔍 Filtro '{periodo}': {len(df_utilidad)} → {len(df_filtrado)} registros")
            print(f"📅 Desde {fecha_inicio} hasta {fecha_max_rango}")
        
        # 3. Preparar categorías para filtro
        categorias_seleccionadas = [categoria_filtro] if categoria_filtro != 'todos' else []
        
        print(f"📊 Datos finales: {len(df_filtrado)} registros")
        
        # 4. Crear tarjetas y gráfico
        tarjetas = crear_tarjetas_promedio(df_filtrado, categorias_seleccionadas)
        grafico = crear_grafico_evolucion(df_filtrado, categorias_seleccionadas)
        
        return tarjetas, grafico

else:
    # Layout de error si no se pueden cargar los datos
    app.layout = html.Div([
        crear_header("Dashboard de Utilidad Operativa HotBoat", 8057),
        html.Div([
            html.H1("❌ Error al cargar datos", style={
                'color': 'red',
                'textAlign': 'center',
                'marginTop': '100px'
            }),
            html.P("No se pudieron cargar los datos de utilidad operativa.", style={
                'color': COLORS['text'],
                'textAlign': 'center',
                'fontSize': '18px'
            }),
            html.P("Ejecuta primero: python utilidad_operativa.py", style={
                'color': COLORS['text'],
                'textAlign': 'center',
                'fontSize': '16px'
            })
        ])
    ], style={
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'padding': '20px'
    })

if __name__ == '__main__':
    print("=== INICIANDO DASHBOARD DE UTILIDAD OPERATIVA ===")
    print("🚀 Dashboard de utilidad operativa iniciado")
    print("🌐 Accede en: http://localhost:8057")
    print("=" * 60)
    
    app.run(debug=True, host='localhost', port=8057) 