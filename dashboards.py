import dash
from dash import html, dcc, Input, Output
import pandas as pd
from datetime import datetime
import os
import plotly.graph_objects as go
from funciones.funciones import *
from funciones.funciones_reservas import *

# Importar módulos personalizados
from funciones.graficos_dashboard import (
    crear_grafico_ingresos_gastos,
    crear_grafico_horas_populares,
    crear_grafico_reservas,
    crear_grafico_utilidad_operativa,
    COLORS
)

from funciones.componentes_dashboard import (
    crear_header,
    crear_filtros,
    crear_selector_periodo,
    crear_tarjetas_metricas,
    crear_contenedor_grafico,
    CARD_STYLE
)

# ======== CARGA DE DATOS ========
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

# ======== FUNCIONES PARA GRÁFICOS INTERACTIVOS ========
def crear_grafico_interactivo(df_ingresos, df_costos_operativos, df_gastos_marketing, df_costos_fijos, periodo, variables_seleccionadas):
    """Crea un gráfico interactivo que muestra solo las variables seleccionadas."""
    
    # Preparar datos según el periodo seleccionado
    if periodo == 'D':
        # Preparación para ingresos
        if df_ingresos is not None:
            df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.date
        # Preparación para costos operativos  
        if df_costos_operativos is not None:
            df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.date
        # Preparación para gastos marketing
        if df_gastos_marketing is not None:
            df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.date
        # Preparación para costos fijos
        if df_costos_fijos is not None:
            df_costos_fijos['fecha_grupo'] = df_costos_fijos["Fecha"].dt.date
        
        titulo = 'Análisis Financiero por Día'
    elif periodo == 'W':
        # Preparación para ingresos
        if df_ingresos is not None:
            df_ingresos['fecha_grupo'] = df_ingresos["fecha"] - pd.to_timedelta(df_ingresos["fecha"].dt.dayofweek, unit='D')
            df_ingresos['fecha_label'] = df_ingresos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        # Preparación para costos operativos
        if df_costos_operativos is not None:
            df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"] - pd.to_timedelta(df_costos_operativos["fecha"].dt.dayofweek, unit='D')
            df_costos_operativos['fecha_label'] = df_costos_operativos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        # Preparación para gastos marketing
        if df_gastos_marketing is not None:
            df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"] - pd.to_timedelta(df_gastos_marketing["fecha"].dt.dayofweek, unit='D')
            df_gastos_marketing['fecha_label'] = df_gastos_marketing['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        # Preparación para costos fijos
        if df_costos_fijos is not None:
            df_costos_fijos['fecha_grupo'] = df_costos_fijos["Fecha"] - pd.to_timedelta(df_costos_fijos["Fecha"].dt.dayofweek, unit='D')
            df_costos_fijos['fecha_label'] = df_costos_fijos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        
        titulo = 'Análisis Financiero por Semana'
    else:  # 'M'
        # Preparación para ingresos
        if df_ingresos is not None:
            df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.to_period('M').dt.to_timestamp()
            df_ingresos['fecha_label'] = df_ingresos["fecha"].dt.strftime('%B %Y')
        # Preparación para costos operativos
        if df_costos_operativos is not None:
            df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.to_period('M').dt.to_timestamp()
            df_costos_operativos['fecha_label'] = df_costos_operativos["fecha"].dt.strftime('%B %Y')
        # Preparación para gastos marketing
        if df_gastos_marketing is not None:
            df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.to_period('M').dt.to_timestamp()
            df_gastos_marketing['fecha_label'] = df_gastos_marketing["fecha"].dt.strftime('%B %Y')
        # Preparación para costos fijos
        if df_costos_fijos is not None:
            df_costos_fijos['fecha_grupo'] = df_costos_fijos["Fecha"].dt.to_period('M').dt.to_timestamp()
            df_costos_fijos['fecha_label'] = df_costos_fijos["Fecha"].dt.strftime('%B %Y')
        
        titulo = 'Análisis Financiero por Mes'

    # Agrupar datos para cada categoría
    datos_agrupados = {}
    fechas_todas = set()
    etiquetas_fecha = {}
    
    # Procesar ingresos
    if 'ingresos' in variables_seleccionadas and df_ingresos is not None:
        ingresos_totales = df_ingresos.groupby('fecha_grupo')['monto'].sum().reset_index()
        datos_agrupados['ingresos'] = ingresos_totales
        fechas_todas.update(ingresos_totales['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_ingresos.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']
    
    # Procesar costos operativos
    if 'costos_operativos' in variables_seleccionadas and df_costos_operativos is not None:
        costos_operativos = df_costos_operativos.groupby('fecha_grupo')['monto'].sum().reset_index()
        datos_agrupados['costos_operativos'] = costos_operativos
        fechas_todas.update(costos_operativos['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_costos_operativos.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']

    # Procesar gastos marketing
    if 'gastos_marketing' in variables_seleccionadas and df_gastos_marketing is not None:
        gastos_marketing = df_gastos_marketing.groupby('fecha_grupo')['monto'].sum().reset_index()
        datos_agrupados['gastos_marketing'] = gastos_marketing
        fechas_todas.update(gastos_marketing['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_gastos_marketing.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']
    
    # Procesar costos fijos
    if 'costos_fijos' in variables_seleccionadas and df_costos_fijos is not None:
        costos_fijos = df_costos_fijos.groupby('fecha_grupo')['Monto'].sum().reset_index()
        datos_agrupados['costos_fijos'] = costos_fijos
        fechas_todas.update(costos_fijos['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_costos_fijos.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']

    # Crear figura
    fig = go.Figure()
    
    # Colores para cada categoría
    colores_categoria = {
        'ingresos': COLORS['income'],
        'costos_operativos': COLORS['expense'],
        'gastos_marketing': '#ff6b6b',
        'costos_fijos': '#9370db'  # Púrpura medio para costos fijos
    }
    
    # Nombres amigables para mostrar en la leyenda
    nombres_amigables = {
        'ingresos': 'Ingresos Totales',
        'costos_operativos': 'Costos Operativos',
        'gastos_marketing': 'Gastos Marketing',
        'costos_fijos': 'Costos Fijos'
    }
    
    # Añadir barras para cada categoría seleccionada
    for categoria, datos in datos_agrupados.items():
        fig.add_trace(go.Bar(
            x=datos['fecha_grupo'],
            y=datos['monto'] if categoria != 'costos_fijos' else datos['Monto'],
            name=nombres_amigables[categoria],
            marker_color=colores_categoria[categoria],
            hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
            type='bar'
        ))
    
    # Configurar diseño
    fig.update_layout(
        title=titulo,
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        yaxis=dict(
            title='Monto (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='x unified'
    )
    
    # Ajustar etiquetas si es semanal o mensual
    if periodo in ['W', 'M'] and etiquetas_fecha:
        fechas_ordenadas = sorted(list(fechas_todas))
        etiquetas = [etiquetas_fecha.get(fecha, '') for fecha in fechas_ordenadas]
        fig.update_xaxes(
            ticktext=etiquetas,
            tickvals=fechas_ordenadas
        )
    
    return fig

# ======== FUNCIÓN PARA GRÁFICO DE VALOR PROMEDIO DE VENTAS ========
def crear_grafico_avg_sale_value(df_reservas, periodo):
    """Crea un gráfico que muestra la evolución del valor promedio de las ventas a lo largo del tiempo."""
    
    # Asegurarse de que tengamos los datos necesarios
    if df_reservas is None or len(df_reservas) == 0:
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para mostrar',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500,
        )
        return fig
    
    # Convertir TOTAL AMOUNT a tipo numérico si no lo es
    df_reservas['TOTAL AMOUNT'] = pd.to_numeric(df_reservas['TOTAL AMOUNT'], errors='coerce')
    
    # Crear una copia para no modificar el original
    df = df_reservas.copy()
    
    # Agrupar por periodo
    if periodo == 'D':
        df['fecha_grupo'] = df['fecha_trip'].dt.date
        titulo = 'Valor Promedio de Venta por Día'
    elif periodo == 'W':
        df['fecha_grupo'] = df['fecha_trip'] - pd.to_timedelta(df['fecha_trip'].dt.dayofweek, unit='D')
        df['fecha_label'] = df['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        titulo = 'Valor Promedio de Venta por Semana'
    else:  # 'M'
        df['fecha_grupo'] = df['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        df['fecha_label'] = df['fecha_trip'].dt.strftime('%B %Y')
        titulo = 'Valor Promedio de Venta por Mes'
    
    # Calcular el promedio por grupo de fecha
    avg_values = df.groupby('fecha_grupo')['TOTAL AMOUNT'].mean().reset_index()
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir línea para el valor promedio
    fig.add_trace(go.Scatter(
        x=avg_values['fecha_grupo'],
        y=avg_values['TOTAL AMOUNT'],
        mode='lines+markers',
        name='Valor Promedio de Venta',
        line=dict(color='#6AB187', width=3),
        marker=dict(size=8, color='#6AB187', line=dict(width=1, color='#3B7080')),
        hovertemplate='Fecha: %{x}<br>Valor Promedio: $%{y:,.0f}<br>'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title=titulo,
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        yaxis=dict(
            title='Valor Promedio (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickformat='$,.0f'
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='x unified'
    )
    
    # Ajustar etiquetas si es semanal o mensual
    if periodo in ['W', 'M']:
        etiquetas_fecha = {}
        for idx, row in df.iterrows():
            etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']
            
        fechas_ordenadas = sorted(list(set(avg_values['fecha_grupo'])))
        etiquetas = [etiquetas_fecha.get(fecha, '') for fecha in fechas_ordenadas]
        
        if etiquetas and fechas_ordenadas:
            fig.update_xaxes(
                ticktext=etiquetas,
                tickvals=fechas_ordenadas
            )
    
    return fig

# ======== APLICACIONES SEPARADAS ========
def crear_app_reservas(datos=None):
    """Crea la aplicación Dash para la página de reservas."""
    
    if datos is None:
        datos = cargar_datos()
        
    df = datos['reservas']
    df_payments = datos['pagos']
    df_expenses = datos['gastos']
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        crear_header(),
        html.Div([
            html.Div("DASHBOARD DE RESERVAS", style={
                'color': COLORS['primary'], 
                'fontSize': '24px', 
                'fontWeight': 'bold',
                'padding': '10px',
                'marginBottom': '20px',
                'textAlign': 'center',
                'backgroundColor': COLORS['card_bg'],
                'borderRadius': '5px'
            }),
            html.Div([
                html.A("Ver Dashboard de Utilidad Operativa", 
                      href="http://localhost:8051", 
                      style={'color': '#00a3ff', 'textDecoration': 'none', 'fontSize': '16px'},
                      target="_blank")
            ], style={'textAlign': 'center', 'marginBottom': '20px'})
        ]),
        crear_filtros(df['fecha_trip'].min(), df['fecha_trip'].max()),
        crear_tarjetas_metricas(),
        crear_selector_periodo(),
        crear_contenedor_grafico('reservas-tiempo'),
        crear_contenedor_grafico('ingresos-tiempo'),
        crear_contenedor_grafico('horas-populares', figura=crear_grafico_horas_populares(df)),
    ], style={
        'padding': 20,
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })
    
    @app.callback(
        [Output('reservas-tiempo', 'figure'),
         Output('ingresos-tiempo', 'figure'),
         Output('total-reservas', 'children'),
         Output('total-ingresos', 'children'),
         Output('total-gastos', 'children'),
         Output('balance', 'children'),
         Output('balance', 'style')],
        [Input('periodo-selector', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date')]
    )
    def actualizar_graficos_reservas(periodo, start_date, end_date):
        # Filtrar DataFrames
        df_filtrado = df[(df['fecha_trip'] >= pd.to_datetime(start_date)) & (df['fecha_trip'] <= pd.to_datetime(end_date))]
        df_payments_filtrado = df_payments[(df_payments['Fecha'] >= pd.to_datetime(start_date)) & (df_payments['Fecha'] <= pd.to_datetime(end_date))]
        df_expenses_filtrado = df_expenses[(df_expenses['Fecha'] >= pd.to_datetime(start_date)) & (df_expenses['Fecha'] <= pd.to_datetime(end_date))]

        # Calcular métricas
        total_reservas_filtrado = len(df_filtrado)
        total_ingresos_filtrado = df_payments_filtrado['Monto'].sum()
        total_gastos_filtrado = df_expenses_filtrado['Monto'].sum()
        balance_filtrado = total_ingresos_filtrado - total_gastos_filtrado

        # Crear gráficos
        fig_reservas = crear_grafico_reservas(df_filtrado, periodo)
        fig_ingresos = crear_grafico_ingresos_gastos(df_payments_filtrado, df_expenses_filtrado, periodo)

        # Estilo del balance
        balance_style = {
            'color': COLORS['income'] if balance_filtrado >= 0 else COLORS['expense'],
            'fontSize': '2.5em',
            'margin': '0'
        }

        return (
            fig_reservas,
            fig_ingresos,
            f'{total_reservas_filtrado:,}',
            f'${total_ingresos_filtrado:,.0f}',
            f'${total_gastos_filtrado:,.0f}',
            f'${balance_filtrado:,.0f}',
            balance_style
        )
    
    return app

def crear_app_utilidad(datos=None):
    """Crea la aplicación Dash para la página de utilidad operativa."""
    
    if datos is None:
        datos = cargar_datos()
        
    df = datos['reservas']
    df_ingresos = datos['ingresos']
    df_costos_operativos = datos['costos_operativos']
    df_gastos_marketing = datos['gastos_marketing']
    df_costos_fijos = datos['costos_fijos']
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        crear_header(),
        html.Div([
            html.Div("DASHBOARD DE UTILIDAD OPERATIVA", style={
                'color': COLORS['income'], 
                'fontSize': '24px', 
                'fontWeight': 'bold',
                'padding': '10px',
                'marginBottom': '20px',
                'textAlign': 'center',
                'backgroundColor': COLORS['card_bg'],
                'borderRadius': '5px'
            }),
            html.Div([
                html.A("Ver Dashboard de Reservas", 
                      href="http://localhost:8050", 
                      style={'color': '#00a3ff', 'textDecoration': 'none', 'fontSize': '16px'},
                      target="_blank")
            ], style={'textAlign': 'center', 'marginBottom': '20px'})
        ]),
        crear_filtros(df['fecha_trip'].min(), df['fecha_trip'].max()),
        html.Div([
            html.Div([
                html.H3('Ingresos Totales', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-ingresos-op', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Costos Operativos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-costos-op', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Gastos Marketing', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-marketing', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Costos Fijos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-costos-fijos', style={'color': '#9370db', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Utilidad Operativa', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='utilidad-operativa-valor', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Valor Promedio de Venta', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='avg-sale-value', style={'color': '#6AB187', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
        crear_selector_periodo(),
        
        # Añadir controles de selección para el gráfico interactivo
        html.Div([
            html.H3("Seleccionar variables para el gráfico:", style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Checklist(
                id='seleccion-variables',
                options=[
                    {'label': ' Ingresos Totales', 'value': 'ingresos'},
                    {'label': ' Costos Operativos', 'value': 'costos_operativos'},
                    {'label': ' Gastos Marketing', 'value': 'gastos_marketing'},
                    {'label': ' Costos Fijos', 'value': 'costos_fijos'}
                ],
                value=['ingresos', 'costos_operativos', 'gastos_marketing', 'costos_fijos'],  # Todos seleccionados por defecto
                inline=True,
                style={
                    'color': COLORS['text'],
                    'fontSize': '16px'
                },
                labelStyle={
                    'marginRight': '20px',
                    'display': 'inline-block',
                    'padding': '5px 10px',
                    'borderRadius': '5px',
                    'backgroundColor': COLORS['card_bg'],
                    'marginBottom': '10px'
                }
            )
        ], style={
            'backgroundColor': COLORS['accent'],
            'padding': '15px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'textAlign': 'center'
        }),
        
        # Gráfico interactivo
        crear_contenedor_grafico('grafico-interactivo', 'Análisis Financiero Interactivo'),
        
        # Gráfico original de utilidad operativa
        crear_contenedor_grafico('utilidad-operativa-chart', 'Análisis de Utilidad Operativa'),
        
        # Nuevo gráfico de valor promedio de venta
        crear_contenedor_grafico('avg-sale-value-chart', 'Evolución del Valor Promedio de Venta'),
    ], style={
        'padding': 20,
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })
    
    @app.callback(
        [Output('utilidad-operativa-chart', 'figure'),
         Output('grafico-interactivo', 'figure'),
         Output('avg-sale-value-chart', 'figure'),
         Output('total-ingresos-op', 'children'),
         Output('total-costos-op', 'children'),
         Output('total-marketing', 'children'),
         Output('total-costos-fijos', 'children'),
         Output('utilidad-operativa-valor', 'children'),
         Output('utilidad-operativa-valor', 'style'),
         Output('avg-sale-value', 'children')],
        [Input('periodo-selector', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date'),
         Input('seleccion-variables', 'value')]
    )
    def actualizar_graficos_utilidad(periodo, start_date, end_date, variables_seleccionadas):
        # Filtrar DataFrames
        df_ingresos_filtrado = df_ingresos[(df_ingresos['fecha'] >= pd.to_datetime(start_date)) & (df_ingresos['fecha'] <= pd.to_datetime(end_date))]
        df_costos_operativos_filtrado = df_costos_operativos[(df_costos_operativos['fecha'] >= pd.to_datetime(start_date)) & (df_costos_operativos['fecha'] <= pd.to_datetime(end_date))]
        df_gastos_marketing_filtrado = df_gastos_marketing[(df_gastos_marketing['fecha'] >= pd.to_datetime(start_date)) & (df_gastos_marketing['fecha'] <= pd.to_datetime(end_date))]
        df_costos_fijos_filtrado = df_costos_fijos[(df_costos_fijos['Fecha'] >= pd.to_datetime(start_date)) & (df_costos_fijos['Fecha'] <= pd.to_datetime(end_date))]
        df_filtrado = df[(df['fecha_trip'] >= pd.to_datetime(start_date)) & (df['fecha_trip'] <= pd.to_datetime(end_date))]

        # Calcular métricas
        total_ingresos = df_ingresos_filtrado['monto'].sum()
        total_costos_op = df_costos_operativos_filtrado['monto'].sum()
        total_marketing = df_gastos_marketing_filtrado['monto'].sum()
        total_costos_fijos = df_costos_fijos_filtrado['Monto'].sum()
        utilidad_operativa = total_ingresos - total_costos_op - total_marketing - total_costos_fijos
        
        # Calcular promedio de ventas
        df_filtrado['TOTAL AMOUNT'] = pd.to_numeric(df_filtrado['TOTAL AMOUNT'], errors='coerce')
        avg_sale = df_filtrado['TOTAL AMOUNT'].mean() if not df_filtrado.empty else 0

        # Crear gráfico tradicional de utilidad operativa
        fig_utilidad = crear_grafico_utilidad_operativa(
            df_ingresos_filtrado, 
            df_costos_operativos_filtrado, 
            df_gastos_marketing_filtrado, 
            periodo
        )
        
        # Crear gráfico interactivo con las variables seleccionadas
        fig_interactivo = crear_grafico_interactivo(
            df_ingresos_filtrado if 'ingresos' in variables_seleccionadas else None,
            df_costos_operativos_filtrado if 'costos_operativos' in variables_seleccionadas else None,
            df_gastos_marketing_filtrado if 'gastos_marketing' in variables_seleccionadas else None,
            df_costos_fijos_filtrado if 'costos_fijos' in variables_seleccionadas else None,
            periodo,
            variables_seleccionadas
        )
        
        # Crear gráfico de valor promedio de ventas
        fig_avg_sale = crear_grafico_avg_sale_value(
            df_filtrado,
            periodo
        )

        # Estilo de utilidad operativa
        utilidad_style = {
            'color': COLORS['income'] if utilidad_operativa >= 0 else COLORS['expense'],
            'fontSize': '2.5em',
            'margin': '0'
        }

        return (
            fig_utilidad,
            fig_interactivo,
            fig_avg_sale,
            f'${total_ingresos:,.0f}',
            f'${total_costos_op:,.0f}',
            f'${total_marketing:,.0f}',
            f'${total_costos_fijos:,.0f}',
            f'${utilidad_operativa:,.0f}',
            utilidad_style,
            f'${avg_sale:,.0f}'
        )
    
    return app

# ======== EJECUCIÓN DE LA APLICACIÓN ========
if __name__ == '__main__':
    # Por defecto, ejecutar la aplicación de reservas
    app = crear_app_reservas()
    print("\n=== DASHBOARD DE RESERVAS ===")
    print("Dashboard disponible en: http://localhost:8050")
    print("O alternativamente en: http://127.0.0.1:8050")
    print("\nPara ver el Dashboard de Utilidad Operativa, ejecute el archivo: python utilidad.py")
    app.run(debug=True, host='localhost', port=8050)