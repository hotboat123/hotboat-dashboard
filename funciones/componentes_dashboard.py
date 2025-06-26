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

def crear_header(titulo_dashboard="Dashboard HotBoat", puerto_actual=None):
    """Crea el encabezado del dashboard con navegación."""
    
    # Enlaces de navegación
    enlaces_nav = []
    
    # Definir los dashboards disponibles
    dashboards = [
        {"nombre": "Reservas", "puerto": 8050, "url": "http://localhost:8050"},
        {"nombre": "Utilidad Operativa", "puerto": 8055, "url": "http://localhost:8055"},
        {"nombre": "Marketing", "puerto": 8056, "url": "http://localhost:8056"},
        {"nombre": "Utilidad Operativa (Nuevo)", "puerto": 8057, "url": "http://localhost:8057"}
    ]
    
    # Crear enlaces para cada dashboard
    for dashboard in dashboards:
        if puerto_actual == dashboard["puerto"]:
            # Dashboard actual - mostrar como activo
            enlaces_nav.append(
                html.Span(dashboard["nombre"], 
                         style={
                             'color': '#ffffff', 
                             'fontWeight': 'bold', 
                             'marginRight': '20px',
                             'padding': '10px 15px', 
                             'backgroundColor': 'rgba(255,255,255,0.3)',
                             'borderRadius': '8px',
                             'border': '2px solid rgba(255,255,255,0.5)',
                             'textShadow': '0 1px 2px rgba(0,0,0,0.3)'
                         })
            )
        else:
            # Otros dashboards - mostrar como enlaces
            enlaces_nav.append(
                html.A(dashboard["nombre"], 
                      href=dashboard["url"],
                      target="_self",
                      style={
                          'color': '#ffffff', 
                          'textDecoration': 'none', 
                          'marginRight': '20px',
                          'padding': '10px 15px', 
                          'border': '2px solid rgba(255,255,255,0.4)',
                          'borderRadius': '8px', 
                          'transition': 'all 0.3s ease',
                          'backgroundColor': 'rgba(255,255,255,0.1)',
                          'cursor': 'pointer'
                      },
                      className="dashboard-nav-link")
            )
    
    return html.Div([
        # Título principal
        html.Div([
            html.H1(titulo_dashboard, 
                    style={
                        'textAlign': 'center',
                        'color': COLORS['text'],
                        'marginBottom': 20,
                        'marginTop': 0,
                        'fontWeight': 'bold',
                        'fontSize': '2.5em',
                        'textShadow': '0 2px 4px rgba(0,0,0,0.3)'
                    })
        ]),
        
        # Barra de navegación
        html.Div([
            html.Div("🚤 HotBoat Dashboards:", style={
                'color': 'rgba(255,255,255,0.8)', 
                'fontSize': '14px', 
                'marginBottom': '10px',
                'textAlign': 'center'
            }),
            html.Div(enlaces_nav, style={
                'textAlign': 'center', 
                'display': 'flex',
                'justifyContent': 'center',
                'flexWrap': 'wrap',
                'gap': '10px'
            })
        ], style={
            'backgroundColor': 'rgba(0,0,0,0.2)', 
            'padding': '15px', 
            'borderRadius': '10px',
            'marginTop': '10px'
        })
    ], style={
        'backgroundColor': COLORS['accent'], 
        'padding': '25px', 
        'marginBottom': '30px',
        'background': f'linear-gradient(135deg, {COLORS["accent"]} 0%, {COLORS["primary"]} 100%)',
        'borderBottom': '3px solid rgba(255,255,255,0.2)'
    })

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

def crear_contenedor_insights(id_insights, titulo="💡 Insights"):
    """Crea un contenedor para mostrar insights."""
    return html.Div([
        html.H4(titulo, style={'color': COLORS['text'], 'marginBottom': '15px'}),
        html.Ul(id=id_insights, style={
            'color': COLORS['text'],
            'fontSize': '14px',
            'lineHeight': '1.6',
            'padding': '0',
            'margin': '0'
        })
    ], style=CARD_STYLE) 