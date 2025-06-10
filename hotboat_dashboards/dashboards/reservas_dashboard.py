#!/usr/bin/env python3
"""
🚤 HOTBOAT - DASHBOARD DE RESERVAS OPTIMIZADO
=============================================

Dashboard de reservas manteniendo la funcionalidad exacta de la versión original.
Interfaz negra con selector arriba.

Autor: Sistema HotBoat Optimizado  
Versión: 2.0
"""

import dash
from dash import html, dcc, Input, Output
import pandas as pd
from datetime import datetime
import os
import plotly.graph_objects as go
import sys
sys.path.append('../..')

# Importar funciones originales
from funciones.funciones import *
from funciones.funciones_reservas import *
from funciones.graficos_dashboard import (
    crear_grafico_ingresos_gastos,
    crear_grafico_horas_populares,
    crear_grafico_reservas,
    COLORS
)
from funciones.componentes_dashboard import (
    crear_header,
    crear_filtros,
    crear_selector_periodo,
    crear_tarjetas_metricas,
    crear_contenedor_grafico,
    crear_contenedor_insights,
    CARD_STYLE
)

# Importar módulos optimizados
from hotboat_dashboards.core import (
    cargar_datos_reservas,
    get_container_style,
    get_title_style,
    get_card_style,
    ESTILOS_ORIGINALES
)

def cargar_datos():
    """Carga todos los archivos CSV necesarios para el dashboard."""
    
    # Crear directorio para gráficos si no existe
    if not os.path.exists("archivos_output/graficos"):
        os.makedirs("archivos_output/graficos")
    
    # Carga de datos de reservas
    df = pd.read_csv("archivos_output/reservas_HotBoat.csv")
    df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])
    
    # Carga de datos financieros
    df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
    df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"])
    df_payments["Monto"] = df_payments["Monto"].astype(float)
    
    df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")
    df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"])
    df_expenses["Monto"] = df_expenses["Monto"].astype(float)
    
    # Extraer costos fijos desde gastos
    df_costos_fijos = df_expenses[df_expenses["Categoría 1"] == "Costos Fijos"].copy()
    
    # Datos para análisis de utilidad operativa
    df_ingresos = pd.read_csv("archivos_output/ingresos_totales.csv")
    df_ingresos["fecha"] = pd.to_datetime(df_ingresos["fecha"])
    
    df_costos_operativos = pd.read_csv("archivos_output/costos_operativos.csv")
    df_costos_operativos["fecha"] = pd.to_datetime(df_costos_operativos["fecha"])
    
    df_gastos_marketing = pd.read_csv("archivos_output/gastos_marketing.csv")
    df_gastos_marketing["fecha"] = pd.to_datetime(df_gastos_marketing["fecha"])
    
    return {
        'reservas': df,
        'pagos': df_payments,
        'gastos': df_expenses,
        'costos_fijos': df_costos_fijos,
        'ingresos': df_ingresos,
        'costos_operativos': df_costos_operativos,
        'gastos_marketing': df_gastos_marketing
    }

def generar_insights_reservas(df_reservas, periodo):
    """Genera insights específicos para reservas."""
    insights = []
    
    if df_reservas.empty:
        return "No hay datos de reservas disponibles para el periodo seleccionado."
    
    total_reservas = len(df_reservas)
    insights.append(f"📊 Total de reservas: {total_reservas}")
    
    # Análisis por tipo de barco
    if 'Boat_Type' in df_reservas.columns:
        tipo_mas_popular = df_reservas['Boat_Type'].value_counts().index[0]
        insights.append(f"🚤 Tipo de barco más popular: {tipo_mas_popular}")
    
    # Análisis temporal
    if periodo == 'D':
        reservas_por_dia = df_reservas.groupby(df_reservas['fecha_trip'].dt.date).size()
        dia_mas_ocupado = reservas_por_dia.idxmax()
        insights.append(f"📅 Día con más reservas: {dia_mas_ocupado}")
    
    return " | ".join(insights)

def generar_insights_ingresos_gastos(df_payments, df_expenses, periodo):
    """Genera insights para ingresos y gastos."""
    insights = []
    
    total_ingresos = df_payments['Monto'].sum() if not df_payments.empty else 0
    total_gastos = df_expenses['Monto'].sum() if not df_expenses.empty else 0
    
    insights.append(f"💰 Ingresos totales: ${total_ingresos:,.0f}")
    insights.append(f"💸 Gastos totales: ${total_gastos:,.0f}")
    
    balance = total_ingresos - total_gastos
    if balance > 0:
        insights.append(f"📈 Balance positivo: ${balance:,.0f}")
    else:
        insights.append(f"📉 Balance negativo: ${abs(balance):,.0f}")
    
    return " | ".join(insights)

def generar_insights_horas_populares(df):
    """Genera insights sobre horas populares."""
    if df.empty or 'hora_trip' not in df.columns:
        return "No hay datos de horarios disponibles."
    
    hora_mas_popular = df['hora_trip'].value_counts().index[0]
    return f"🕐 Hora más popular: {hora_mas_popular}"

def crear_app_reservas(datos=None):
    """Crea la aplicación Dash para el dashboard de reservas."""
    
    if datos is None:
        datos = cargar_datos()
    
    app = dash.Dash(__name__)
    
    # Layout principal con estilos originales
    app.layout = html.Div([
        # Título principal
        html.H1("🚤 DASHBOARD DE RESERVAS HOTBOAT", 
                style=get_title_style()),
        
        # Controles principales
        html.Div([
            html.Div([
                html.Label("Periodo de Análisis:", style={'color': 'white', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='periodo-selector',
                    options=[
                        {'label': 'Diario', 'value': 'D'},
                        {'label': 'Semanal', 'value': 'W'},
                        {'label': 'Mensual', 'value': 'M'}
                    ],
                    value='M',
                    style={'backgroundColor': '#2d2d2d', 'color': 'white'}
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
            
            html.Div([
                html.Label("Rango de Fechas:", style={'color': 'white', 'marginBottom': '5px'}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    start_date=datos['reservas']['fecha_trip'].min(),
                    end_date=datos['reservas']['fecha_trip'].max(),
                    display_format='DD/MM/YYYY',
                    style={'backgroundColor': '#2d2d2d'}
                )
            ], style={'width': '60%', 'display': 'inline-block'})
        ], style={'marginBottom': '30px'}),
        
        # Métricas principales
        html.Div([
            html.Div([
                html.H3("Total Reservas", style={'color': 'white', 'textAlign': 'center'}),
                html.H2(id='total-reservas', style={'color': '#4CAF50', 'textAlign': 'center'})
            ], style=get_card_style(), className='metric-card'),
            
            html.Div([
                html.H3("Total Ingresos", style={'color': 'white', 'textAlign': 'center'}),
                html.H2(id='total-ingresos', style={'color': '#4CAF50', 'textAlign': 'center'})
            ], style=get_card_style(), className='metric-card'),
            
            html.Div([
                html.H3("Total Gastos", style={'color': 'white', 'textAlign': 'center'}),
                html.H2(id='total-gastos', style={'color': '#FF5722', 'textAlign': 'center'})
            ], style=get_card_style(), className='metric-card'),
            
            html.Div([
                html.H3("Balance", style={'color': 'white', 'textAlign': 'center'}),
                html.H2(id='balance', style={'textAlign': 'center'})
            ], style=get_card_style(), className='metric-card')
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),
        
        # Gráficos principales
        html.Div([
            html.Div([
                html.H3("📊 Reservas por Periodo", style={'color': 'white', 'textAlign': 'center'}),
                dcc.Graph(id='reservas-tiempo')
            ], style=get_card_style()),
            
            html.Div([
                html.H3("💰 Ingresos vs Gastos", style={'color': 'white', 'textAlign': 'center'}),
                dcc.Graph(id='ingresos-tiempo')
            ], style=get_card_style())
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}),
        
        # Insights
        html.Div([
            html.H3("📈 Insights Automáticos", style={'color': 'white', 'marginBottom': '20px'}),
            html.Div(id='insights-reservas', style={'color': 'white', 'marginBottom': '10px'}),
            html.Div(id='insights-financieros', style={'color': 'white', 'marginBottom': '10px'}),
            html.Div(id='insights-horas', style={'color': 'white'})
        ], style=get_card_style())
        
    ], style=get_container_style())
    
    # Callback principal
    @app.callback(
        [Output('reservas-tiempo', 'figure'),
         Output('ingresos-tiempo', 'figure'),
         Output('total-reservas', 'children'),
         Output('total-ingresos', 'children'),
         Output('total-gastos', 'children'),
         Output('balance', 'children'),
         Output('balance', 'style'),
         Output('insights-reservas', 'children'),
         Output('insights-financieros', 'children'),
         Output('insights-horas', 'children')],
        [Input('periodo-selector', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date')]
    )
    def actualizar_graficos_reservas(periodo, start_date, end_date):
        # Filtrar DataFrames
        mask_reservas = (datos['reservas']['fecha_trip'] >= start_date) & (datos['reservas']['fecha_trip'] <= end_date)
        df_reservas_filtrado = datos['reservas'][mask_reservas]
        
        mask_pagos = (datos['pagos']['Fecha'] >= start_date) & (datos['pagos']['Fecha'] <= end_date)
        df_pagos_filtrado = datos['pagos'][mask_pagos]
        
        mask_gastos = (datos['gastos']['Fecha'] >= start_date) & (datos['gastos']['Fecha'] <= end_date)
        df_gastos_filtrado = datos['gastos'][mask_gastos]
        
        # Crear gráficos
        fig_reservas = crear_grafico_reservas(df_reservas_filtrado, periodo)
        fig_ingresos = crear_grafico_ingresos_gastos(df_pagos_filtrado, df_gastos_filtrado, periodo)
        
        # Calcular métricas
        total_reservas = len(df_reservas_filtrado)
        total_ingresos = df_pagos_filtrado['Monto'].sum()
        total_gastos = df_gastos_filtrado['Monto'].sum()
        balance = total_ingresos - total_gastos
        
        # Estilo del balance
        balance_style = {'textAlign': 'center', 'color': '#4CAF50' if balance >= 0 else '#FF5722'}
        
        # Generar insights
        insights_reservas = generar_insights_reservas(df_reservas_filtrado, periodo)
        insights_financieros = generar_insights_ingresos_gastos(df_pagos_filtrado, df_gastos_filtrado, periodo)
        insights_horas = generar_insights_horas_populares(df_reservas_filtrado)
        
        return (
            fig_reservas, fig_ingresos,
            f"{total_reservas:,}",
            f"${total_ingresos:,.0f}",
            f"${total_gastos:,.0f}",
            f"${balance:,.0f}",
            balance_style,
            insights_reservas,
            insights_financieros,
            insights_horas
        )
    
    return app

def main():
    """Función principal para ejecutar el dashboard de reservas."""
    print("=== DASHBOARD DE RESERVAS ===")
    
    try:
        datos = cargar_datos()
        app = crear_app_reservas(datos)
        
        print("Dashboard de reservas iniciado exitosamente")
        print("Accede en: http://localhost:8050")
        
        app.run_server(debug=True, host='0.0.0.0', port=8050)
        
    except Exception as e:
        print(f"Error iniciando dashboard de reservas: {e}")

if __name__ == "__main__":
    main() 