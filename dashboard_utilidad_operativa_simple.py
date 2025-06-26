import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Configuración de colores
COLORS = {
    'background': '#1a1a1a',
    'card_bg': '#2d2d2d',
    'text': '#ffffff',
    'primary': '#007bff',
    'income': '#28a745',
    'expense': '#dc3545',
    'marketing': '#ffc107'
}

def cargar_datos():
    """Carga los datos de utilidad operativa."""
    try:
        df = pd.read_csv('archivos_output/Utilidad operativa.csv')
        df['fecha'] = pd.to_datetime(df['fecha'])
        print(f"✅ Datos cargados: {len(df)} registros")
        return df
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return None

# Crear aplicación
app = dash.Dash(__name__)

# Agregar estilos CSS personalizados
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dashboard Utilidad Operativa</title>
        {%favicon%}
        {%css%}
        <style>
            .Select-control {
                background-color: #2d2d2d !important;
                border-color: #444 !important;
            }
            .Select-menu-outer {
                background-color: #2d2d2d !important;
                border-color: #444 !important;
            }
            .Select-option {
                background-color: #2d2d2d !important;
                color: #ffffff !important;
            }
            .Select-option:hover {
                background-color: #444 !important;
            }
            .Select-value-label {
                color: #ffffff !important;
            }
            .Select-placeholder {
                color: #cccccc !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Cargar datos
df = cargar_datos()

if df is not None:
    fecha_min = df['fecha'].min()
    fecha_max = df['fecha'].max()
    categorias = sorted(df['categoria'].unique())
    
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("Dashboard Utilidad Operativa", style={
                'color': COLORS['text'],
                'textAlign': 'center',
                'marginBottom': '30px'
            })
        ]),
        
        # Filtros
        html.Div([
            html.Div([
                html.Label("Rango de Fechas:", style={'color': COLORS['text']}),
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=fecha_min,
                    max_date_allowed=fecha_max,
                    start_date=fecha_min,
                    end_date=fecha_max,
                    display_format='YYYY-MM-DD'
                )
            ], style={'marginBottom': '20px', 'textAlign': 'center'}),
            
            html.Div([
                html.Label("Período:", style={'color': COLORS['text']}),
                dcc.RadioItems(
                    id='periodo',
                    options=[
                        {'label': 'Agrupar por día', 'value': 'dia'},
                        {'label': 'Agrupar por semana', 'value': 'semana'},
                        {'label': 'Agrupar por mes', 'value': 'mes'}
                    ],
                    value='dia',
                    inline=True,
                    style={'color': COLORS['text'], 'marginBottom': '20px'}
                )
            ], style={'marginBottom': '20px', 'textAlign': 'center'}),
            
            html.Div([
                html.Label("Categoría:", style={'color': COLORS['text']}),
                dcc.Dropdown(
                    id='categoria',
                    options=[{'label': 'Todas', 'value': 'todas'}] + 
                            [{'label': cat.title(), 'value': cat} for cat in categorias],
                    value='todas',
                    style={
                        'backgroundColor': COLORS['card_bg'],
                        'color': COLORS['text'],
                        'border': '1px solid #444'
                    },
                    className='dropdown-dark'
                )
            ], style={'textAlign': 'center'})
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '10px',
            'marginBottom': '20px',
            'textAlign': 'center',
            'maxWidth': '500px',
            'margin': '0 auto 20px auto',
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center'
        }),
        
        # Tarjetas
        html.Div([
            html.Div(id='tarjetas', style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'center',
                'gap': '20px'
            })
        ]),
        
        # Gráfico
        html.Div([
            dcc.Graph(id='grafico')
        ], style={
            'backgroundColor': COLORS['card_bg'],
            'padding': '20px',
            'borderRadius': '10px',
            'marginTop': '20px'
        })
        
    ], style={
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'padding': '20px'
    })
    
    @callback(
        [Output('tarjetas', 'children'),
         Output('grafico', 'figure')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('periodo', 'value'),
         Input('categoria', 'value')]
    )
    def actualizar_dashboard(start_date, end_date, periodo, categoria):
        # Filtrar por fecha
        df_filtrado = df.copy()
        
        if start_date and end_date:
            df_filtrado = df_filtrado[
                (df_filtrado['fecha'] >= start_date) & 
                (df_filtrado['fecha'] <= end_date)
            ]
        
        # Filtrar por categoría
        if categoria != 'todas':
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]
        
        # Agrupar por período
        if periodo == 'dia':
            # Agrupar por día
            df_agrupado = df_filtrado.groupby([df_filtrado['fecha'].dt.date, 'categoria'])['monto'].sum().reset_index()
            df_agrupado['fecha'] = pd.to_datetime(df_agrupado['fecha'])
        elif periodo == 'semana':
            # Agrupar por semana
            df_agrupado = df_filtrado.groupby([df_filtrado['fecha'].dt.to_period('W').dt.start_time, 'categoria'])['monto'].sum().reset_index()
            df_agrupado['fecha'] = pd.to_datetime(df_agrupado['fecha'])
        elif periodo == 'mes':
            # Agrupar por mes
            df_agrupado = df_filtrado.groupby([df_filtrado['fecha'].dt.to_period('M').dt.start_time, 'categoria'])['monto'].sum().reset_index()
            df_agrupado['fecha'] = pd.to_datetime(df_agrupado['fecha'])
        
        # Crear tarjetas
        tarjetas = []
        
        # Colores específicos para cada categoría
        colores_categoria = {
            'ingreso operativo': COLORS['income'],      # Verde
            'costo operativo': COLORS['expense'],       # Rojo
            'Costos de Marketing': COLORS['marketing']  # Amarillo
        }
        
        for cat in df_agrupado['categoria'].unique():
            df_cat = df_agrupado[df_agrupado['categoria'] == cat]
            total = df_cat['monto'].sum()
            promedio = df_cat['monto'].mean()
            cantidad = len(df_cat)
            
            color = colores_categoria.get(cat, COLORS['primary'])
            
            tarjeta = html.Div([
                html.H3(cat.title(), style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(f"${total:,.0f}", style={'color': color, 'margin': '0', 'fontSize': '28px'}),
                html.P("Total", style={'color': COLORS['text'], 'margin': '5px 0', 'fontSize': '12px'}),
                html.Div([
                    html.Span(f"Promedio: ${promedio:,.0f}", style={'color': COLORS['text'], 'fontSize': '14px'}),
                    html.Br(),
                    html.Span(f"Registros: {cantidad:,}", style={'color': COLORS['text'], 'fontSize': '14px'})
                ], style={'marginTop': '10px'})
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '20px',
                'borderRadius': '10px',
                'textAlign': 'center',
                'minWidth': '250px'
            })
            tarjetas.append(tarjeta)
        
        # Crear gráfico
        fig = go.Figure()
        
        # Colores específicos para cada categoría
        colores_categoria = {
            'ingreso operativo': COLORS['income'],      # Verde
            'costo operativo': COLORS['expense'],       # Rojo
            'Costos de Marketing': COLORS['marketing']  # Amarillo
        }
        
        for cat in df_agrupado['categoria'].unique():
            df_cat = df_agrupado[df_agrupado['categoria'] == cat]
            color = colores_categoria.get(cat, COLORS['primary'])
            
            fig.add_trace(go.Scatter(
                x=df_cat['fecha'],
                y=df_cat['monto'],
                mode='lines+markers',
                name=cat.title(),
                line=dict(color=color, width=3),
                marker=dict(size=6, color=color)
            ))
        
        # Título del gráfico según el período
        titulo_periodo = {
            'dia': 'Evolución por Día',
            'semana': 'Evolución por Semana',
            'mes': 'Evolución por Mes'
        }.get(periodo, 'Evolución Temporal')
        
        fig.update_layout(
            title=titulo_periodo,
            xaxis_title='Fecha',
            yaxis_title='Monto ($)',
            template='plotly_dark',
            plot_bgcolor=COLORS['card_bg'],
            paper_bgcolor=COLORS['card_bg'],
            font=dict(color=COLORS['text'])
        )
        
        return tarjetas, fig

else:
    app.layout = html.Div([
        html.H1("Error al cargar datos", style={'color': 'red', 'textAlign': 'center'})
    ])

if __name__ == '__main__':
    print("🚀 Dashboard iniciado en http://localhost:8057")
    app.run(debug=True, host='localhost', port=8057) 