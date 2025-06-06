#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOTBOAT - Sistema de Dashboards Consolidado
===========================================

Este módulo contiene todos los dashboards principales de HotBoat en un solo lugar,
optimizado y organizado para mejor mantenimiento.

Autores: Sistema HotBoat
Fecha: Junio 2025
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback_context
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Agregar paths para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports consolidados
from core.data_loader import cargar_datos
from core.dashboard_components import crear_layout_principal, crear_sidebar
from core.chart_generators import (
    crear_grafico_utilidad_tiempo,
    crear_grafico_ingresos_vs_costos,
    crear_grafico_reservas_mes,
    crear_grafico_marketing_roi
)

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

THEME_CONFIG = {
    'background_color': '#0f1419',
    'paper_color': '#1e2328', 
    'text_color': '#e6e6e6',
    'primary_color': '#00d4ff',
    'secondary_color': '#ff6b35',
    'grid_color': '#2d3748'
}

# ============================================================================
# DASHBOARD PRINCIPAL DE UTILIDAD
# ============================================================================

def crear_app_utilidad(datos):
    """
    Crea la aplicación principal de dashboard de utilidad operativa
    
    Args:
        datos (dict): Diccionario con todos los DataFrames cargados
        
    Returns:
        dash.Dash: Aplicación de dashboard configurada
    """
    
    app = dash.Dash(__name__, title="HotBoat - Utilidad Operativa")
    
    # Layout principal
    app.layout = html.Div([
        crear_sidebar(),
        
        # Contenido principal
        html.Div([
            # Header
            html.Div([
                html.H1("🚤 HotBoat - Dashboard de Utilidad Operativa", 
                       className="dashboard-title"),
                html.P("Análisis completo de rentabilidad y métricas financieras",
                       className="dashboard-subtitle")
            ], className="header-section"),
            
            # Controles
            html.Div([
                html.Div([
                    html.Label("Período de Análisis:", className="control-label"),
                    dcc.Dropdown(
                        id='periodo-dropdown',
                        options=[
                            {'label': 'Diario', 'value': 'D'},
                            {'label': 'Semanal', 'value': 'W'},
                            {'label': 'Mensual', 'value': 'M'},
                            {'label': 'Trimestral', 'value': 'Q'}
                        ],
                        value='M',
                        className="control-dropdown"
                    )
                ], className="control-group"),
                
                html.Div([
                    html.Label("Rango de Fechas:", className="control-label"),
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        start_date=datetime(2024, 8, 1),
                        end_date=datetime(2025, 12, 31),
                        display_format='DD/MM/YYYY',
                        className="control-datepicker"
                    )
                ], className="control-group")
            ], className="controls-section"),
            
            # Métricas principales
            html.Div(id="metricas-principales", className="metrics-section"),
            
            # Gráficos principales
            html.Div([
                html.Div([
                    dcc.Graph(id="grafico-utilidad-tiempo")
                ], className="chart-container"),
                
                html.Div([
                    dcc.Graph(id="grafico-ingresos-costos")
                ], className="chart-container")
            ], className="charts-row"),
            
            # Gráficos secundarios
            html.Div([
                html.Div([
                    dcc.Graph(id="grafico-margenes")
                ], className="chart-container"),
                
                html.Div([
                    dcc.Graph(id="grafico-breakdown-costos")
                ], className="chart-container")
            ], className="charts-row")
            
        ], className="main-content")
    ], className="dashboard-container")
    
    # Callbacks
    @app.callback(
        [Output('metricas-principales', 'children'),
         Output('grafico-utilidad-tiempo', 'figure'),
         Output('grafico-ingresos-costos', 'figure'),
         Output('grafico-margenes', 'figure'),
         Output('grafico-breakdown-costos', 'figure')],
        [Input('periodo-dropdown', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date')]
    )
    def actualizar_dashboard_utilidad(periodo, start_date, end_date):
        """Actualiza todos los componentes del dashboard de utilidad"""
        
        # Procesar datos según período y fechas
        datos_filtrados = filtrar_datos_por_periodo(datos, periodo, start_date, end_date)
        
        # Calcular métricas
        metricas = calcular_metricas_principales(datos_filtrados)
        
        # Crear componentes de métricas
        metricas_html = crear_tarjetas_metricas(metricas)
        
        # Crear gráficos
        fig_utilidad = crear_grafico_utilidad_tiempo(datos_filtrados, periodo)
        fig_ingresos_costos = crear_grafico_ingresos_vs_costos(datos_filtrados, periodo)
        fig_margenes = crear_grafico_margenes_tiempo(datos_filtrados, periodo)
        fig_breakdown = crear_grafico_breakdown_costos(datos_filtrados)
        
        return metricas_html, fig_utilidad, fig_ingresos_costos, fig_margenes, fig_breakdown
    
    return app

# ============================================================================
# DASHBOARD DE RESERVAS
# ============================================================================

def crear_app_reservas(datos):
    """
    Crea la aplicación de dashboard de reservas
    
    Args:
        datos (dict): Diccionario con todos los DataFrames cargados
        
    Returns:
        dash.Dash: Aplicación de dashboard configurada
    """
    
    app = dash.Dash(__name__, title="HotBoat - Análisis de Reservas")
    
    app.layout = html.Div([
        crear_sidebar(),
        
        html.Div([
            # Header
            html.Div([
                html.H1("🚤 HotBoat - Dashboard de Reservas", 
                       className="dashboard-title"),
                html.P("Análisis detallado de reservas, pagos y tendencias",
                       className="dashboard-subtitle")
            ], className="header-section"),
            
            # Controles específicos para reservas
            html.Div([
                html.Div([
                    html.Label("Tipo de Análisis:", className="control-label"),
                    dcc.Dropdown(
                        id='tipo-analisis-reservas',
                        options=[
                            {'label': 'Vista General', 'value': 'general'},
                            {'label': 'Por Embarcación', 'value': 'embarcacion'},
                            {'label': 'Por Cliente', 'value': 'cliente'},
                            {'label': 'Por Estado de Pago', 'value': 'pago'}
                        ],
                        value='general',
                        className="control-dropdown"
                    )
                ], className="control-group")
            ], className="controls-section"),
            
            # Dashboard de reservas
            html.Div(id="dashboard-reservas-content")
            
        ], className="main-content")
    ], className="dashboard-container")
    
    @app.callback(
        Output('dashboard-reservas-content', 'children'),
        [Input('tipo-analisis-reservas', 'value')]
    )
    def actualizar_dashboard_reservas(tipo_analisis):
        """Actualiza el contenido del dashboard de reservas"""
        
        if tipo_analisis == 'general':
            return crear_vista_general_reservas(datos)
        elif tipo_analisis == 'embarcacion':
            return crear_vista_por_embarcacion(datos)
        elif tipo_analisis == 'cliente':
            return crear_vista_por_cliente(datos)
        elif tipo_analisis == 'pago':
            return crear_vista_por_estado_pago(datos)
    
    return app

# ============================================================================
# DASHBOARD DE MARKETING
# ============================================================================

def crear_app_marketing(datos):
    """
    Crea la aplicación de dashboard de marketing
    
    Args:
        datos (dict): Diccionario con todos los DataFrames cargados
        
    Returns:
        dash.Dash: Aplicación de dashboard configurada
    """
    
    app = dash.Dash(__name__, title="HotBoat - Marketing Analytics")
    
    app.layout = html.Div([
        crear_sidebar(),
        
        html.Div([
            # Header
            html.Div([
                html.H1("📊 HotBoat - Dashboard de Marketing", 
                       className="dashboard-title"),
                html.P("Análisis de campañas, ROI y métricas de marketing digital",
                       className="dashboard-subtitle")
            ], className="header-section"),
            
            # Métricas de marketing
            html.Div(id="metricas-marketing"),
            
            # Gráficos de marketing
            html.Div([
                html.Div([
                    dcc.Graph(id="grafico-roi-campañas")
                ], className="chart-container"),
                
                html.Div([
                    dcc.Graph(id="grafico-cpc-ctr")
                ], className="chart-container")
            ], className="charts-row")
            
        ], className="main-content")
    ], className="dashboard-container")
    
    return app

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def filtrar_datos_por_periodo(datos, periodo, start_date, end_date):
    """
    Filtra los datos según el período y rango de fechas especificado
    
    Args:
        datos (dict): Datos originales
        periodo (str): Período de agrupación
        start_date (str): Fecha de inicio
        end_date (str): Fecha de fin
        
    Returns:
        dict: Datos filtrados
    """
    datos_filtrados = datos.copy()
    
    # Aplicar filtro de fechas a cada DataFrame que tenga columnas de fecha
    for key, df in datos_filtrados.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            # Buscar columnas de fecha
            date_columns = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
            
            if date_columns:
                date_col = date_columns[0]
                try:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
                    datos_filtrados[key] = df[mask].copy()
                except:
                    pass  # Si hay error en el filtrado, mantener datos originales
    
    return datos_filtrados

def calcular_metricas_principales(datos):
    """
    Calcula las métricas principales del negocio
    
    Args:
        datos (dict): Datos filtrados
        
    Returns:
        dict: Métricas calculadas
    """
    metricas = {}
    
    try:
        # Ingresos totales
        if 'ingresos' in datos and not datos['ingresos'].empty:
            metricas['ingresos_totales'] = datos['ingresos']['monto'].sum()
        
        # Costos totales
        if 'costos_operativos' in datos and not datos['costos_operativos'].empty:
            metricas['costos_totales'] = datos['costos_operativos']['monto'].sum()
        
        # Gastos marketing
        if 'gastos_marketing' in datos and not datos['gastos_marketing'].empty:
            metricas['gastos_marketing'] = datos['gastos_marketing']['monto'].sum()
        
        # Utilidad bruta
        ingresos = metricas.get('ingresos_totales', 0)
        costos = metricas.get('costos_totales', 0)
        marketing = metricas.get('gastos_marketing', 0)
        
        metricas['utilidad_bruta'] = ingresos - costos - marketing
        metricas['margen_utilidad'] = (metricas['utilidad_bruta'] / ingresos * 100) if ingresos > 0 else 0
        
        # Número de reservas
        if 'reservas' in datos and not datos['reservas'].empty:
            metricas['num_reservas'] = len(datos['reservas'])
            metricas['ticket_promedio'] = ingresos / metricas['num_reservas'] if metricas['num_reservas'] > 0 else 0
        
    except Exception as e:
        print(f"Error calculando métricas: {e}")
        metricas = {
            'ingresos_totales': 0,
            'costos_totales': 0,
            'gastos_marketing': 0,
            'utilidad_bruta': 0,
            'margen_utilidad': 0,
            'num_reservas': 0,
            'ticket_promedio': 0
        }
    
    return metricas

def crear_tarjetas_metricas(metricas):
    """
    Crea las tarjetas de métricas principales
    
    Args:
        metricas (dict): Métricas calculadas
        
    Returns:
        html.Div: Componente HTML con las tarjetas
    """
    
    tarjetas = []
    
    # Configuración de tarjetas
    config_tarjetas = [
        {
            'titulo': 'Ingresos Totales',
            'valor': metricas.get('ingresos_totales', 0),
            'formato': 'currency',
            'icono': '💰',
            'color': 'green'
        },
        {
            'titulo': 'Utilidad Bruta',
            'valor': metricas.get('utilidad_bruta', 0),
            'formato': 'currency',
            'icono': '📈',
            'color': 'blue'
        },
        {
            'titulo': 'Margen de Utilidad',
            'valor': metricas.get('margen_utilidad', 0),
            'formato': 'percentage',
            'icono': '📊',
            'color': 'orange'
        },
        {
            'titulo': 'Reservas Totales',
            'valor': metricas.get('num_reservas', 0),
            'formato': 'number',
            'icono': '🚤',
            'color': 'purple'
        }
    ]
    
    for config in config_tarjetas:
        if config['formato'] == 'currency':
            valor_formateado = f"${config['valor']:,.0f}"
        elif config['formato'] == 'percentage':
            valor_formateado = f"{config['valor']:.1f}%"
        else:
            valor_formateado = f"{config['valor']:,.0f}"
        
        tarjeta = html.Div([
            html.Div([
                html.Span(config['icono'], className="metric-icon"),
                html.Div([
                    html.H3(valor_formateado, className="metric-value"),
                    html.P(config['titulo'], className="metric-title")
                ], className="metric-text")
            ], className="metric-content")
        ], className=f"metric-card metric-{config['color']}")
        
        tarjetas.append(tarjeta)
    
    return html.Div(tarjetas, className="metrics-grid")

# ============================================================================
# FUNCIONES DE GRÁFICOS ADICIONALES
# ============================================================================

def crear_grafico_margenes_tiempo(datos, periodo='M'):
    """
    Crea un gráfico de márgenes de utilidad a lo largo del tiempo
    
    Args:
        datos (dict): Datos filtrados
        periodo (str): Período de agrupación
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de márgenes
    """
    try:
        # Calcular utilidad por período
        utilidad_data = calcular_utilidad_por_periodo(datos, periodo)
        
        if utilidad_data.empty:
            return crear_grafico_vacio("Sin datos para mostrar márgenes")
        
        # Calcular margen de utilidad
        utilidad_data['margen_utilidad'] = (
            utilidad_data['utilidad_neta'] / utilidad_data['ingresos'] * 100
        ).fillna(0)
        
        # Crear gráfico
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=utilidad_data['periodo'],
            y=utilidad_data['margen_utilidad'],
            mode='lines+markers',
            name='Margen de Utilidad (%)',
            line=dict(color=THEME_CONFIG['primary_color'], width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Margen: %{y:.1f}%<extra></extra>'
        ))
        
        # Configurar layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '📊 Evolución del Margen de Utilidad',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']}
            },
            'xaxis': {
                'title': 'Período',
                'color': THEME_CONFIG['text_color']
            },
            'yaxis': {
                'title': 'Margen de Utilidad (%)',
                'color': THEME_CONFIG['text_color']
            }
        })
        
        fig.update_layout(layout)
        return fig
        
    except Exception as e:
        print(f"Error creando gráfico de márgenes: {e}")
        return crear_grafico_vacio("Error generando gráfico de márgenes")

def crear_grafico_breakdown_costos(datos):
    """
    Crea un gráfico de desglose de costos
    
    Args:
        datos (dict): Datos filtrados
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de breakdown de costos
    """
    try:
        costos_data = []
        
        # Costos operativos
        if 'costos_operativos' in datos and not datos['costos_operativos'].empty:
            costos_operativos = datos['costos_operativos']['monto'].sum()
            costos_data.append({'categoria': 'Costos Operativos', 'monto': costos_operativos})
        
        # Gastos marketing
        if 'gastos_marketing' in datos and not datos['gastos_marketing'].empty:
            gastos_marketing = datos['gastos_marketing']['monto'].sum()
            costos_data.append({'categoria': 'Marketing', 'monto': gastos_marketing})
        
        # Costos fijos
        if 'costos_fijos' in datos and not datos['costos_fijos'].empty:
            costos_fijos = datos['costos_fijos']['monto'].sum()
            costos_data.append({'categoria': 'Costos Fijos', 'monto': costos_fijos})
        
        if not costos_data:
            return crear_grafico_vacio("Sin datos de costos disponibles")
        
        df_costos = pd.DataFrame(costos_data)
        
        # Crear gráfico de dona
        fig = go.Figure(data=[go.Pie(
            labels=df_costos['categoria'],
            values=df_costos['monto'],
            hole=0.4,
            marker_colors=[THEME_CONFIG['secondary_color'], 
                          THEME_CONFIG['primary_color'], 
                          '#ff9500'],
            textinfo='label+percent',
            textfont=dict(color=THEME_CONFIG['text_color']),
            hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        # Configurar layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '💰 Desglose de Costos',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']}
            },
            'showlegend': True,
            'legend': {
                'font': {'color': THEME_CONFIG['text_color']},
                'orientation': 'v',
                'x': 1.02,
                'y': 0.5
            }
        })
        
        fig.update_layout(layout)
        return fig
        
    except Exception as e:
        print(f"Error creando breakdown de costos: {e}")
        return crear_grafico_vacio("Error generando breakdown de costos")

# ============================================================================
# FUNCIÓN PRINCIPAL DE CARGA
# ============================================================================

def inicializar_dashboard(tipo='utilidad'):
    """
    Función principal para inicializar cualquier dashboard
    
    Args:
        tipo (str): Tipo de dashboard ('utilidad', 'reservas', 'marketing')
        
    Returns:
        dash.Dash: Aplicación configurada y lista para ejecutar
    """
    
    print(f"🚤 INICIANDO DASHBOARD DE {tipo.upper()} HOTBOAT...")
    print("=" * 60)
    
    # Cargar datos
    print("📊 Cargando datos...")
    datos = cargar_datos()
    
    # Crear aplicación según el tipo
    if tipo == 'utilidad':
        app = crear_app_utilidad(datos)
        puerto = 8055
    elif tipo == 'reservas':
        app = crear_app_reservas(datos)
        puerto = 8050
    elif tipo == 'marketing':
        app = crear_app_marketing(datos)
        puerto = 8056
    else:
        raise ValueError(f"Tipo de dashboard no reconocido: {tipo}")
    
    print(f"✅ Dashboard de {tipo} creado exitosamente")
    print(f"🌐 URL: http://localhost:{puerto}")
    print(f"🔄 Para detener: Ctrl+C")
    print("=" * 60)
    
    return app, puerto

def crear_vista_general_reservas(datos):
    """
    Crea la vista general de reservas
    
    Args:
        datos (dict): Datos consolidados
        
    Returns:
        html.Div: Vista general
    """
    
    from dashboard_components import crear_grid_metricas, crear_fila_graficos
    
    if 'reservas' not in datos or datos['reservas'].empty:
        return html.Div([
            html.H3("Sin datos de reservas disponibles", 
                   style={'color': THEME_CONFIG['text_color'], 'textAlign': 'center'})
        ])
    
    df_reservas = datos['reservas']
    
    # Métricas de reservas
    metricas_config = [
        {
            'titulo': 'Total Reservas',
            'valor': len(df_reservas),
            'icono': '🚤',
            'color': 'primary',
            'formato': 'number'
        },
        {
            'titulo': 'Reservas Este Mes',
            'valor': len(df_reservas),  # Simplificado
            'icono': '📅',
            'color': 'success',
            'formato': 'number'
        }
    ]
    
    metricas_html = crear_grid_metricas(metricas_config)
    
    # Gráficos
    graficos_config = [
        {'id': 'grafico-reservas-mes', 'titulo': 'Reservas por Mes'}
    ]
    
    graficos_html = crear_fila_graficos(graficos_config)
    
    return html.Div([
        metricas_html,
        graficos_html
    ])

def crear_vista_por_embarcacion(datos):
    """Vista por embarcación"""
    return html.Div([
        html.H3("Vista por Embarcación", style={'color': THEME_CONFIG['text_color']})
    ])

def crear_vista_por_cliente(datos):
    """Vista por cliente"""
    return html.Div([
        html.H3("Vista por Cliente", style={'color': THEME_CONFIG['text_color']})
    ])

def crear_vista_por_estado_pago(datos):
    """Vista por estado de pago"""
    return html.Div([
        html.H3("Vista por Estado de Pago", style={'color': THEME_CONFIG['text_color']})
    ])

if __name__ == "__main__":
    # Ejemplo de uso
    app, puerto = inicializar_dashboard('utilidad')
    app.run(debug=False, host='0.0.0.0', port=puerto) 