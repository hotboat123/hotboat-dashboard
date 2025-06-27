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
    'marketing': '#ffc107',
    'costos_fijos': '#6f42c1',
    'costos_variables': '#fd7e14'
}

def cargar_datos():
    """Carga los datos de utilidad operativa."""
    try:
        df = pd.read_csv('archivos_output/Utilidad operativa.csv')
        df['fecha'] = pd.to_datetime(df['fecha'])
        # Normalizar categorías a formato título
        df['categoria'] = df['categoria'].astype(str).str.strip().str.title()
        print(f"✅ Datos cargados: {len(df)} registros")
        print(f"Categorías detectadas: {sorted(df['categoria'].unique())}")
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
                html.Label("Año:", style={'color': COLORS['text']}),
                dcc.Dropdown(
                    id='filtro_ano',
                    options=[{'label': 'Todos los años', 'value': 'todos'}] + 
                            [{'label': str(ano), 'value': ano} for ano in sorted(df['fecha'].dt.year.unique(), reverse=True)],
                    value='todos',
                    style={
                        'backgroundColor': COLORS['card_bg'],
                        'color': COLORS['text'],
                        'border': '1px solid #444',
                        'width': '200px'
                    },
                    className='dropdown-dark'
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
                        'border': '1px solid #444',
                        'width': '300px'
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
            # Tarjeta especial de Utilidad Operativa
            html.Div(id='tarjeta_utilidad', style={
                'width': '100%',
                'marginBottom': '30px'
            }),
            
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
        [Output('tarjeta_utilidad', 'children'),
         Output('tarjetas', 'children'),
         Output('grafico', 'figure')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('periodo', 'value'),
         Input('categoria', 'value'),
         Input('filtro_ano', 'value')]
    )
    def actualizar_dashboard(start_date, end_date, periodo, categoria, filtro_ano):
        # Filtrar por fecha
        df_filtrado = df.copy()
        
        if start_date and end_date:
            df_filtrado = df_filtrado[
                (df_filtrado['fecha'] >= start_date) & 
                (df_filtrado['fecha'] <= end_date)
            ]
        
        # Filtrar por año
        if filtro_ano != 'todos':
            df_filtrado = df_filtrado[df_filtrado['fecha'].dt.year == filtro_ano]
        
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
        
        # Calcular utilidad operativa
        ingresos = df_agrupado[df_agrupado['categoria'] == 'Ingreso Operativo']['monto'].sum()
        costos = df_agrupado[df_agrupado['categoria'].isin(['Costo Operativo', 'Costos De Marketing', 'Costos Fijos', 'Costos Variables'])]['monto'].sum()
        utilidad_operativa = ingresos - costos
        
        # Crear tarjeta especial de utilidad operativa
        color_utilidad = COLORS['income'] if utilidad_operativa >= 0 else COLORS['expense']
        icono_utilidad = "📈" if utilidad_operativa >= 0 else "📉"
        
        tarjeta_utilidad = html.Div([
            html.Div([
                html.H2("💰 Utilidad Operativa", style={
                    'color': COLORS['text'], 
                    'marginBottom': '10px',
                    'textAlign': 'center',
                    'fontSize': '24px'
                }),
                html.H1(f"{icono_utilidad} ${utilidad_operativa:,.0f}", style={
                    'color': color_utilidad, 
                    'margin': '0', 
                    'fontSize': '48px',
                    'textAlign': 'center',
                    'fontWeight': 'bold'
                }),
                html.P("Ingresos - Costos", style={
                    'color': COLORS['text'], 
                    'margin': '10px 0', 
                    'fontSize': '16px',
                    'textAlign': 'center'
                }),
                html.Div([
                    html.Span(f"Ingresos: ${ingresos:,.0f}", style={
                        'color': COLORS['income'], 
                        'fontSize': '14px',
                        'marginRight': '20px'
                    }),
                    html.Span(f"Costos: ${costos:,.0f}", style={
                        'color': COLORS['expense'], 
                        'fontSize': '14px'
                    })
                ], style={'textAlign': 'center', 'marginTop': '15px'})
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '30px',
                'borderRadius': '15px',
                'textAlign': 'center',
                'border': f'3px solid {color_utilidad}',
                'boxShadow': f'0 4px 8px rgba(0,0,0,0.3)'
            })
        ])
        
        # Crear tarjetas normales
        tarjetas = []
        
        # Colores específicos para cada categoría
        colores_categoria = {
            'Ingreso Operativo': COLORS['income'],      # Verde
            'Costo Operativo': COLORS['expense'],       # Rojo
            'Costos De Marketing': COLORS['marketing'],  # Amarillo
            'Costos Fijos': COLORS['costos_fijos'],      # Morado
            'Costos Variables': COLORS['costos_variables'] # Naranjo
        }
        
        for cat in df_agrupado['categoria'].unique():
            df_cat = df_agrupado[df_agrupado['categoria'] == cat]
            total = df_cat['monto'].sum()
            promedio = df_cat['monto'].mean()
            cantidad = len(df_cat)
            
            color = colores_categoria.get(cat, COLORS['primary'])
            
            tarjeta = html.Div([
                html.H3(cat, style={'color': COLORS['text'], 'marginBottom': '10px'}),
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
        
        # Crear gráfico de evolución
        fig = go.Figure()
        
        # Colores específicos para cada categoría
        colores_categoria = {
            'Ingreso Operativo': COLORS['income'],      # Verde
            'Costo Operativo': COLORS['expense'],       # Rojo
            'Costos De Marketing': COLORS['marketing'],  # Amarillo
            'Costos Fijos': COLORS['costos_fijos'],      # Morado
            'Costos Variables': COLORS['costos_variables'] # Naranjo
        }
        
        # Agregar líneas para cada categoría individual
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
        
        # Agregar línea de todos los costos juntos
        categorias_costos = ['Costo Operativo', 'Costos De Marketing', 'Costos Fijos', 'Costos Variables']
        df_costos = df_agrupado[df_agrupado['categoria'].isin(categorias_costos)]
        if not df_costos.empty:
            df_costos_totales = df_costos.groupby('fecha')['monto'].sum().reset_index()
            fig.add_trace(go.Scatter(
                x=df_costos_totales['fecha'],
                y=df_costos_totales['monto'],
                mode='lines+markers',
                name='Total Costos',
                line=dict(color='#ff6b6b', width=4, dash='dash'),
                marker=dict(size=8, color='#ff6b6b', symbol='diamond')
            ))
        # Agregar línea de utilidad operativa (ingresos - costos)
        df_ingresos = df_agrupado[df_agrupado['categoria'] == 'Ingreso Operativo'][['fecha', 'monto']].rename(columns={'monto': 'ingresos'})
        if not df_ingresos.empty and not df_costos.empty:
            df_costos_totales = df_costos.groupby('fecha')['monto'].sum().reset_index().rename(columns={'monto': 'costos'})
            # Unir ingresos y costos por fecha (outer para no perder fechas)
            df_utilidad = pd.merge(df_ingresos, df_costos_totales, on='fecha', how='outer').fillna(0)
            df_utilidad = df_utilidad.sort_values('fecha')
            df_utilidad['utilidad'] = df_utilidad['ingresos'] - df_utilidad['costos']
            fig.add_trace(go.Scatter(
                x=df_utilidad['fecha'],
                y=df_utilidad['utilidad'],
                mode='lines+markers',
                name='Utilidad Operativa',
                line=dict(color='#00ff88', width=4, dash='dot'),
                marker=dict(size=8, color='#00ff88', symbol='circle-open')
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
        
        return tarjeta_utilidad, tarjetas, fig

else:
    app.layout = html.Div([
        html.H1("Error al cargar datos", style={'color': 'red', 'textAlign': 'center'})
    ])

if __name__ == '__main__':
    print("🚀 Dashboard iniciado en http://localhost:8057")
    app.run(debug=True, host='localhost', port=8057) 