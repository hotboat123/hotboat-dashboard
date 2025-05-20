import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os
from funciones.funciones import *
from funciones.funciones_reservas import *

# Definir colores y estilos
COLORS = {
    'background': '#000000',
    'card_bg': '#1a1a1a',
    'text': '#ffffff',
    'primary': '#007bff',
    'secondary': '#00a3ff',
    'accent': '#004085',
    'grid': '#333333',
    'income': '#28a745',
    'expense': '#dc3545'
}

# Estilo común para los gráficos
GRAPH_STYLE = {
    'paper_bgcolor': COLORS['card_bg'],
    'plot_bgcolor': COLORS['card_bg'],
    'font': {'color': COLORS['text']},
    'height': 500,
}

# Estilos para las tarjetas de métricas
CARD_STYLE = {
    'backgroundColor': COLORS['card_bg'],
    'padding': '20px',
    'margin': '10px',
    'borderRadius': '5px',
    'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)',
    'textAlign': 'center',
    'color': COLORS['text']
}

# Inicializar la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Cargar datos
df = pd.read_csv("archivos_output/reservas_HotBoat.csv")
df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])

# Cargar datos de pagos y procesar montos correctamente
df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"])

# Cargar nuevos datos para el análisis de utilidad
df_ingresos = pd.read_csv("archivos_output/ingresos_totales.csv")
df_ingresos["fecha"] = pd.to_datetime(df_ingresos["fecha"])

df_costos_operativos = pd.read_csv("archivos_output/costos_operativos.csv")
df_costos_operativos["fecha"] = pd.to_datetime(df_costos_operativos["fecha"])

df_gastos_marketing = pd.read_csv("archivos_output/gastos_marketing.csv")
df_gastos_marketing["fecha"] = pd.to_datetime(df_gastos_marketing["fecha"])

# Función para limpiar y convertir montos
def clean_amount(amount):
    if isinstance(amount, str):
        return float(amount.replace('$', '').replace(',', ''))
    return float(amount)

# Limpiar y convertir montos
df_payments["Monto"] = df_payments["Monto"].astype(float)

# Cargar datos de gastos
df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")
df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"])
df_expenses["Monto"] = df_expenses["Monto"].astype(float)

# Asegurar que existe el directorio de salida
if not os.path.exists("archivos_output/graficos"):
    os.makedirs("archivos_output/graficos")

def crear_grafico_ingresos_gastos(df_payments, df_expenses, periodo):
    # Crear columna de fecha según el período
    if periodo == 'D':
        df_payments['fecha_grupo'] = df_payments["Fecha"].dt.date
        df_expenses['fecha_grupo'] = df_expenses["Fecha"].dt.date
        titulo = 'Ingresos y Gastos por Día'
        fecha_format = '%Y-%m-%d'
    elif periodo == 'W':
        df_payments['fecha_grupo'] = df_payments["Fecha"] - pd.to_timedelta(df_payments["Fecha"].dt.dayofweek, unit='D')
        df_payments['fecha_label'] = df_payments['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df_expenses['fecha_grupo'] = df_expenses["Fecha"] - pd.to_timedelta(df_expenses["Fecha"].dt.dayofweek, unit='D')
        df_expenses['fecha_label'] = df_expenses['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        titulo = 'Ingresos y Gastos por Semana'
        fecha_format = '%Y-%m-%d'
    else:  # Mensual
        df_payments['fecha_grupo'] = df_payments["Fecha"].dt.to_period('M').dt.to_timestamp()
        df_payments['fecha_label'] = df_payments["Fecha"].dt.strftime('%B %Y')
        df_expenses['fecha_grupo'] = df_expenses["Fecha"].dt.to_period('M').dt.to_timestamp()
        df_expenses['fecha_label'] = df_expenses["Fecha"].dt.strftime('%B %Y')
        titulo = 'Ingresos y Gastos por Mes'
        fecha_format = '%B %Y'

    # Agrupar datos
    ingresos_totales = df_payments.groupby('fecha_grupo')['Monto'].sum().reset_index()
    gastos = df_expenses.groupby('fecha_grupo')['Monto'].sum().reset_index()
    
    # Crear gráfico
    fig = go.Figure()
    
    # Agregar barras de ingresos
    fig.add_trace(go.Bar(
        x=ingresos_totales['fecha_grupo'],
        y=ingresos_totales['Monto'],
        name='Ingresos',
        marker_color=COLORS['income'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Agregar barras de gastos
    fig.add_trace(go.Bar(
        x=gastos['fecha_grupo'],
        y=gastos['Monto'],
        name='Gastos',
        marker_color=COLORS['expense'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Actualizar layout
    fig.update_layout(
        title=titulo,
        **GRAPH_STYLE,
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
        legend=dict(
            font=dict(color=COLORS['text'])
        ),
        hovermode='x unified'
    )
    
    # Si es semanal o mensual, personalizar etiquetas del eje X
    if periodo in ['W', 'M']:
        fig.update_xaxes(
            ticktext=df_payments.groupby('fecha_grupo')['fecha_label'].first(),
            tickvals=ingresos_totales['fecha_grupo']
        )
    
    return fig

def crear_grafico_utilidad_operativa(df_ingresos, df_costos_operativos, df_gastos_marketing, periodo):
    # Crear columna de fecha según el período
    if periodo == 'D':
        df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.date
        df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.date
        df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.date
        titulo = 'Utilidad Operativa por Día'
        fecha_format = '%Y-%m-%d'
    elif periodo == 'W':
        df_ingresos['fecha_grupo'] = df_ingresos["fecha"] - pd.to_timedelta(df_ingresos["fecha"].dt.dayofweek, unit='D')
        df_ingresos['fecha_label'] = df_ingresos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"] - pd.to_timedelta(df_costos_operativos["fecha"].dt.dayofweek, unit='D')
        df_costos_operativos['fecha_label'] = df_costos_operativos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"] - pd.to_timedelta(df_gastos_marketing["fecha"].dt.dayofweek, unit='D')
        df_gastos_marketing['fecha_label'] = df_gastos_marketing['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        titulo = 'Utilidad Operativa por Semana'
        fecha_format = '%Y-%m-%d'
    else:  # Mensual
        df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.to_period('M').dt.to_timestamp()
        df_ingresos['fecha_label'] = df_ingresos["fecha"].dt.strftime('%B %Y')
        df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.to_period('M').dt.to_timestamp()
        df_costos_operativos['fecha_label'] = df_costos_operativos["fecha"].dt.strftime('%B %Y')
        df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.to_period('M').dt.to_timestamp()
        df_gastos_marketing['fecha_label'] = df_gastos_marketing["fecha"].dt.strftime('%B %Y')
        titulo = 'Utilidad Operativa por Mes'
        fecha_format = '%B %Y'

    # Agrupar datos
    ingresos_totales = df_ingresos.groupby('fecha_grupo')['monto'].sum().reset_index()
    costos_operativos = df_costos_operativos.groupby('fecha_grupo')['monto'].sum().reset_index()
    gastos_marketing = df_gastos_marketing.groupby('fecha_grupo')['monto'].sum().reset_index()
    
    # Crear gráfico
    fig = go.Figure()
    
    # Agregar barras de ingresos
    fig.add_trace(go.Bar(
        x=ingresos_totales['fecha_grupo'],
        y=ingresos_totales['monto'],
        name='Ingresos Totales',
        marker_color=COLORS['income'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Agregar barras de costos operativos
    fig.add_trace(go.Bar(
        x=costos_operativos['fecha_grupo'],
        y=costos_operativos['monto'],
        name='Costos Operativos',
        marker_color=COLORS['expense'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Agregar barras de gastos marketing
    fig.add_trace(go.Bar(
        x=gastos_marketing['fecha_grupo'],
        y=gastos_marketing['monto'],
        name='Gastos Marketing',
        marker_color='#ff6b6b',
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Actualizar layout
    fig.update_layout(
        title=titulo,
        **GRAPH_STYLE,
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
        legend=dict(
            font=dict(color=COLORS['text'])
        ),
        hovermode='x unified'
    )
    
    # Si es semanal o mensual, personalizar etiquetas del eje X
    if periodo in ['W', 'M']:
        fig.update_xaxes(
            ticktext=df_ingresos.groupby('fecha_grupo')['fecha_label'].first(),
            tickvals=ingresos_totales['fecha_grupo']
        )
    
    return fig

def crear_grafico_horas_populares(df):
    # Asegurarnos de que tenemos la columna hora_trip
    if 'hora_trip' not in df.columns:
        print("Columnas disponibles:", df.columns.tolist())
        return go.Figure()  # Retornar un gráfico vacío si no existe la columna

    horas_count = df['hora_trip'].value_counts().sort_index()
    print("Horas disponibles:", horas_count.index.tolist())
    
    fig = px.bar(
        x=horas_count.index,
        y=horas_count.values,
        title='Horarios Más Populares',
        labels={'x': 'Hora del Día', 'y': 'Número de Reservas'},
        text=horas_count.values
    )

    fig.update_layout(
        **GRAPH_STYLE,
        showlegend=False,
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

    fig.update_traces(
        marker_color=COLORS['primary'],
        textposition='auto',
    )

    return fig

# Calcular métricas
total_reservas = len(df)
total_ingresos = df_payments['Monto'].sum()
total_gastos = df_expenses['Monto'].sum()
balance = total_ingresos - total_gastos

print(f"Debug - Métricas:")
print(f"Total Ingresos: ${total_ingresos:,.0f}")
print(f"Total Gastos: ${total_gastos:,.0f}")
print(f"Balance: ${balance:,.0f}")

# Definir el layout del dashboard
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('Dashboard de Reservas HotBoat', 
                style={
                    'textAlign': 'center',
                    'color': COLORS['text'],
                    'marginBottom': 30,
                    'marginTop': 20,
                    'fontWeight': 'bold',
                    'fontSize': '2.5em'
                })
    ], style={'backgroundColor': COLORS['accent'], 'padding': '20px', 'marginBottom': '30px'}),
    
    # Tarjetas de métricas
    html.Div([
        html.Div([
            html.H3('Total de Reservas', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(f'{total_reservas:,}', style={'color': COLORS['primary'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
        html.Div([
            html.H3('Total Ingresos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(f'${total_ingresos:,.0f}', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
        html.Div([
            html.H3('Total Gastos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(f'${total_gastos:,.0f}', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
        html.Div([
            html.H3('Balance', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(f'${balance:,.0f}', 
                   style={'color': COLORS['income'] if balance >= 0 else COLORS['expense'], 
                         'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
    
    # Selector de período y gráficos
    html.Div([
        html.Div([
            html.Label('Seleccionar Período:', style={'color': COLORS['text'], 'marginRight': '10px'}),
            dcc.RadioItems(
                id='periodo-selector',
                options=[
                    {'label': ' Por Día ', 'value': 'D'},
                    {'label': ' Por Semana ', 'value': 'W'},
                    {'label': ' Por Mes ', 'value': 'M'}
                ],
                value='D',
                inline=True,
                style={'color': COLORS['text'], 'marginBottom': '20px'},
                labelStyle={'marginRight': '20px'}
            )
        ], style={'marginBottom': '20px', 'textAlign': 'center'}),
        
        # Gráfico de reservas
        html.Div([
            dcc.Graph(id='reservas-tiempo')
        ], style={'width': '100%', 'marginBottom': '30px', 'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'}),
        
        # Gráfico de ingresos
        html.Div([
            dcc.Graph(id='ingresos-tiempo')
        ], style={'width': '100%', 'marginBottom': '30px', 'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'}),
        
        # Nuevo gráfico de utilidad operativa
        html.Div([
            html.H2('Estimación Utilidad Operativa HotBoat', 
                   style={'color': COLORS['text'], 'textAlign': 'center', 'marginBottom': '20px'}),
            dcc.Graph(id='utilidad-operativa')
        ], style={'width': '100%', 'marginBottom': '30px', 'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'}),
        
        # Gráfico de horas populares
        html.Div([
            dcc.Graph(id='horas-populares', figure=crear_grafico_horas_populares(df))
        ], style={'width': '100%', 'backgroundColor': COLORS['card_bg'], 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'}),
    ]),
], style={
    'padding': 20,
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh'
})

@app.callback(
    [Output('reservas-tiempo', 'figure'),
     Output('ingresos-tiempo', 'figure'),
     Output('utilidad-operativa', 'figure')],
    [Input('periodo-selector', 'value')]
)
def actualizar_graficos(periodo):
    print(f"Callback ejecutado con período: {periodo}")
    
    # Gráfico de reservas
    if periodo == 'D':
        # Agrupación diaria
        df_agrupado = df.groupby('fecha_trip').size().reset_index(name='cantidad')
        fig_reservas = px.bar(df_agrupado, x='fecha_trip', y='cantidad',
                    title='Reservas por Día')
        
    elif periodo == 'W':
        # Agrupación semanal
        df['inicio_semana'] = df['fecha_trip'] - pd.to_timedelta(df['fecha_trip'].dt.dayofweek, unit='D')
        df['semana_label'] = df['inicio_semana'].dt.strftime('Semana del %d/%m/%Y')
        
        df_agrupado = df.groupby(['inicio_semana', 'semana_label']).size().reset_index(name='cantidad')
        df_agrupado = df_agrupado.sort_values('inicio_semana')
        
        fig_reservas = px.bar(df_agrupado, x='inicio_semana', y='cantidad',
                    title='Reservas por Semana')
        
        fig_reservas.update_xaxes(
            ticktext=df_agrupado['semana_label'],
            tickvals=df_agrupado['inicio_semana']
        )
        
    else:  # Mensual
        df['inicio_mes'] = df['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        df['mes_label'] = df['fecha_trip'].dt.strftime('%B %Y')
        
        df_agrupado = df.groupby(['inicio_mes', 'mes_label']).size().reset_index(name='cantidad')
        df_agrupado = df_agrupado.sort_values('inicio_mes')
        
        fig_reservas = px.bar(df_agrupado, x='inicio_mes', y='cantidad',
                    title='Reservas por Mes')
        
        fig_reservas.update_xaxes(
            ticktext=df_agrupado['mes_label'],
            tickvals=df_agrupado['inicio_mes']
        )
    
    # Aplicar estilo común al gráfico de reservas
    fig_reservas.update_layout(
        **GRAPH_STYLE,
        showlegend=False,
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
    
    fig_reservas.update_traces(marker_color=COLORS['primary'])
    
    # Crear gráfico de ingresos y gastos
    fig_ingresos = crear_grafico_ingresos_gastos(df_payments, df_expenses, periodo)
    
    # Crear gráfico de utilidad operativa
    fig_utilidad = crear_grafico_utilidad_operativa(df_ingresos, df_costos_operativos, df_gastos_marketing, periodo)
    
    return fig_reservas, fig_ingresos, fig_utilidad

if __name__ == '__main__':
    print("Dashboard disponible en: http://localhost:8050")
    print("O alternativamente en: http://127.0.0.1:8050")
    app.run(debug=True, host='localhost', port=8050)