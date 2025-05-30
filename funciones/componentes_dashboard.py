from dash import html, dcc

# Definir estilos para componentes de UI
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

CARD_STYLE = {
    'backgroundColor': COLORS['card_bg'],
    'padding': '20px',
    'margin': '10px',
    'borderRadius': '5px',
    'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)',
    'textAlign': 'center',
    'color': COLORS['text']
}

def crear_header():
    """Crea el encabezado del dashboard."""
    return html.Div([
        html.H1('Dashboard de Reservas HotBoat', 
                style={
                    'textAlign': 'center',
                    'color': COLORS['text'],
                    'marginBottom': 30,
                    'marginTop': 20,
                    'fontWeight': 'bold',
                    'fontSize': '2.5em'
                })
    ], style={'backgroundColor': COLORS['accent'], 'padding': '20px', 'marginBottom': '30px'})

def crear_filtros(fecha_min, fecha_max):
    """Crea la sección de filtros del dashboard."""
    return html.Div([
        html.Label('Filtrar por rango de fechas:', style={'color': COLORS['text'], 'marginRight': '10px'}),
        dcc.DatePickerRange(
            id='date-range-picker',
            min_date_allowed=fecha_min,
            max_date_allowed=fecha_max,
            start_date=fecha_min,
            end_date=fecha_max,
            display_format='YYYY-MM-DD',
            style={'color': COLORS['text'], 'marginBottom': '20px'}
        )
    ], style={'marginBottom': '20px', 'textAlign': 'center'})

def crear_selector_periodo():
    """Crea el selector de período (día, semana, mes)."""
    return html.Div([
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
    ], style={'marginBottom': '20px', 'textAlign': 'center'})

def crear_tarjetas_metricas():
    """Crea las tarjetas de métricas del dashboard."""
    return html.Div([
        html.Div([
            html.H3('Total de Reservas', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(id='total-reservas', style={'color': COLORS['primary'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
        html.Div([
            html.H3('Total Ingresos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(id='total-ingresos', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
        html.Div([
            html.H3('Total Gastos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(id='total-gastos', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
        html.Div([
            html.H3('Balance', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            html.H2(id='balance', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
        ], style=CARD_STYLE),
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'})

def crear_contenedor_grafico(id_grafico, titulo=None, figura=None):
    """Crea un contenedor para gráficos con estilo consistente."""
    contenido = []
    
    if titulo:
        contenido.append(html.H2(titulo, style={'color': COLORS['text'], 'textAlign': 'center', 'marginBottom': '20px'}))
    
    if figura:
        contenido.append(dcc.Graph(id=id_grafico, figure=figura))
    else:
        contenido.append(dcc.Graph(id=id_grafico))
    
    return html.Div(contenido, style={
        'width': '100%', 
        'marginBottom': '30px', 
        'backgroundColor': COLORS['card_bg'], 
        'padding': '20px', 
        'boxShadow': '0px 0px 10px rgba(255,255,255,0.1)'
    })

def crear_contenedor_insights(id_contenedor, titulo="Conclusiones"):
    """Crea un contenedor para mostrar insights y conclusiones."""
    return html.Div([
        html.H3(titulo, style={
            'color': COLORS['text'],
            'fontSize': '18px',
            'fontWeight': 'bold',
            'marginBottom': '10px'
        }),
        html.Div(id=id_contenedor, style={
            'color': COLORS['text'],
            'fontSize': '14px',
            'lineHeight': '1.5',
            'padding': '10px'
        })
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'borderRadius': '5px',
        'padding': '15px',
        'marginBottom': '25px',
        'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
    }) 