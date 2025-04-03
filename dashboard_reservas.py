import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import os

# Definir colores y estilos
COLORS = {
    'background': '#000000',
    'card_bg': '#1a1a1a',
    'text': '#ffffff',
    'primary': '#007bff',
    'secondary': '#00a3ff',
    'accent': '#004085',
    'grid': '#333333'
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
df = pd.read_csv("archivos/reservas_HotBoat.csv")
df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])

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
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
    
    # Selector de período y gráfico de reservas
    html.Div([
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
            dcc.Graph(id='reservas-tiempo')
        ], style={'width': '100%', 'display': 'inline-block', 'padding': '20px', 'backgroundColor': COLORS['card_bg'], 'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'}),
    ], style={'marginBottom': '30px'}),
    
    # Gráfico de horas populares
    html.Div([
        html.Div([
            dcc.Graph(id='horas-populares', figure=crear_grafico_horas_populares(df))
        ], style={'width': '100%', 'display': 'inline-block', 'padding': '20px', 'backgroundColor': COLORS['card_bg'], 'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'}),
    ]),
], style={
    'padding': 20,
    'backgroundColor': COLORS['background'],
    'minHeight': '100vh'
})

@app.callback(
    Output('reservas-tiempo', 'figure'),
    [Input('periodo-selector', 'value')]
)
def actualizar_grafico(periodo):
    print(f"Callback ejecutado con período: {periodo}")  # Debug print
    
    if periodo == 'D':
        # Agrupación diaria
        df_agrupado = df.groupby('fecha_trip').size().reset_index(name='cantidad')
        fig = px.bar(df_agrupado, x='fecha_trip', y='cantidad',
                    title='Reservas por Día')
        
    elif periodo == 'W':
        # Agrupación semanal
        # Crear una columna con el inicio de cada semana
        df['inicio_semana'] = df['fecha_trip'] - pd.to_timedelta(df['fecha_trip'].dt.dayofweek, unit='D')
        # Crear etiqueta personalizada para cada semana
        df['semana_label'] = df['inicio_semana'].dt.strftime('Semana del %d/%m/%Y')
        
        # Agrupar por el inicio de la semana y la etiqueta
        df_agrupado = df.groupby(['inicio_semana', 'semana_label']).size().reset_index(name='cantidad')
        df_agrupado = df_agrupado.sort_values('inicio_semana')
        
        fig = px.bar(df_agrupado, x='inicio_semana', y='cantidad',
                    title='Reservas por Semana')
        
        # Personalizar las etiquetas del eje X
        fig.update_xaxes(
            ticktext=df_agrupado['semana_label'],
            tickvals=df_agrupado['inicio_semana']
        )
        
    else:  # Mensual
        # Crear una columna con el primer día de cada mes
        df['inicio_mes'] = df['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        # Crear etiqueta personalizada para cada mes
        df['mes_label'] = df['fecha_trip'].dt.strftime('%B %Y')
        
        # Agrupar por el inicio del mes y la etiqueta
        df_agrupado = df.groupby(['inicio_mes', 'mes_label']).size().reset_index(name='cantidad')
        df_agrupado = df_agrupado.sort_values('inicio_mes')
        
        fig = px.bar(df_agrupado, x='inicio_mes', y='cantidad',
                    title='Reservas por Mes')
        
        # Personalizar las etiquetas del eje X
        fig.update_xaxes(
            ticktext=df_agrupado['mes_label'],
            tickvals=df_agrupado['inicio_mes']
        )
    
    # Aplicar estilo común
    fig.update_layout(
        **GRAPH_STYLE,
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickangle=45
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

if __name__ == '__main__':
    print("\n=== Dashboard HotBoat ===")
    print("El dashboard estará disponible en: http://localhost:8050")
    print("Si esa URL no funciona, intenta con: http://127.0.0.1:8050")
    print("Presiona Ctrl+C para detener el servidor\n")
    app.run(debug=True, host='localhost', port=8050) 