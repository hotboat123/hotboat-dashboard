#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOTBOAT - Componentes de Dashboard Consolidados
===============================================

Este módulo contiene todos los componentes de interfaz de usuario para los dashboards,
organizados y reutilizables.

Autores: Sistema HotBoat
Fecha: Junio 2025
"""

import dash
from dash import dcc, html
import plotly.graph_objects as go

# ============================================================================
# CONFIGURACIÓN DE ESTILOS
# ============================================================================

COLORS = {
    'background': '#0f1419',
    'surface': '#1e2328',
    'primary': '#00d4ff',
    'secondary': '#ff6b35',
    'success': '#00ff88',
    'warning': '#ffaa00',
    'error': '#ff4444',
    'text': '#e6e6e6',
    'text_secondary': '#a0a0a0'
}

STYLES = {
    'dashboard_container': {
        'backgroundColor': COLORS['background'],
        'color': COLORS['text'],
        'fontFamily': 'Arial, sans-serif',
        'minHeight': '100vh',
        'display': 'flex'
    },
    'sidebar': {
        'width': '250px',
        'backgroundColor': COLORS['surface'],
        'padding': '20px',
        'borderRight': f'1px solid {COLORS["primary"]}',
        'height': '100vh',
        'position': 'fixed',
        'overflowY': 'auto'
    },
    'main_content': {
        'marginLeft': '250px',
        'padding': '20px',
        'width': 'calc(100% - 250px)'
    },
    'header_section': {
        'marginBottom': '30px',
        'textAlign': 'center',
        'borderBottom': f'2px solid {COLORS["primary"]}',
        'paddingBottom': '20px'
    },
    'controls_section': {
        'backgroundColor': COLORS['surface'],
        'padding': '20px',
        'borderRadius': '10px',
        'marginBottom': '30px',
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '20px'
    },
    'control_group': {
        'flex': '1',
        'minWidth': '200px'
    },
    'control_label': {
        'color': COLORS['text'],
        'marginBottom': '5px',
        'fontWeight': 'bold'
    },
    'metrics_section': {
        'marginBottom': '30px'
    },
    'metrics_grid': {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
        'gap': '20px',
        'marginBottom': '30px'
    },
    'metric_card': {
        'backgroundColor': COLORS['surface'],
        'padding': '20px',
        'borderRadius': '10px',
        'border': f'1px solid {COLORS["primary"]}',
        'textAlign': 'center',
        'transition': 'transform 0.2s ease',
        'cursor': 'pointer'
    },
    'charts_row': {
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(500px, 1fr))',
        'gap': '20px',
        'marginBottom': '30px'
    },
    'chart_container': {
        'backgroundColor': COLORS['surface'],
        'borderRadius': '10px',
        'padding': '10px',
        'border': f'1px solid {COLORS["primary"]}'
    }
}

# ============================================================================
# COMPONENTES PRINCIPALES
# ============================================================================

def crear_sidebar():
    """
    Crea la barra lateral de navegación
    
    Returns:
        html.Div: Componente de sidebar
    """
    
    return html.Div([
        # Logo y título
        html.Div([
            html.H2("🚤 HotBoat", style={
                'color': COLORS['primary'],
                'textAlign': 'center',
                'marginBottom': '10px',
                'fontSize': '24px'
            }),
            html.P("Dashboard Analytics", style={
                'color': COLORS['text_secondary'],
                'textAlign': 'center',
                'marginBottom': '30px',
                'fontSize': '14px'
            })
        ]),
        
        # Navegación
        html.Div([
            html.H4("Navegación", style={
                'color': COLORS['text'],
                'marginBottom': '15px',
                'fontSize': '16px'
            }),
            
            html.Div([
                crear_nav_link("📈 Utilidad", "http://localhost:8055", True),
                crear_nav_link("🚤 Reservas", "http://localhost:8050", False),
                crear_nav_link("📱 Marketing", "http://localhost:8056", False),
            ])
        ]),
        
        # Información del sistema
        html.Div([
            html.Hr(style={'borderColor': COLORS['primary'], 'margin': '30px 0'}),
            
            html.H4("Estado del Sistema", style={
                'color': COLORS['text'],
                'marginBottom': '15px',
                'fontSize': '16px'
            }),
            
            html.Div([
                crear_status_indicator("🟢", "Sistema operativo", "success"),
                crear_status_indicator("🔄", "Datos actualizados", "warning"),
                crear_status_indicator("📊", "Tests pasando", "success"),
            ])
        ], style={'position': 'absolute', 'bottom': '20px', 'width': '210px'})
        
    ], style=STYLES['sidebar'])

def crear_nav_link(texto, url, activo=False):
    """
    Crea un enlace de navegación
    
    Args:
        texto (str): Texto del enlace
        url (str): URL de destino
        activo (bool): Si está activo o no
        
    Returns:
        html.A: Enlace de navegación
    """
    
    style = {
        'display': 'block',
        'padding': '10px 15px',
        'color': COLORS['primary'] if activo else COLORS['text'],
        'textDecoration': 'none',
        'borderRadius': '5px',
        'marginBottom': '5px',
        'backgroundColor': COLORS['primary'] + '20' if activo else 'transparent',
        'border': f'1px solid {COLORS["primary"]}' if activo else 'none',
        'transition': 'all 0.2s ease'
    }
    
    return html.A(
        texto,
        href=url,
        target="_blank",
        style=style
    )

def crear_status_indicator(icono, texto, tipo):
    """
    Crea un indicador de estado
    
    Args:
        icono (str): Emoji del icono
        texto (str): Texto del indicador
        tipo (str): Tipo de estado ('success', 'warning', 'error')
        
    Returns:
        html.Div: Indicador de estado
    """
    
    color_map = {
        'success': COLORS['success'],
        'warning': COLORS['warning'],
        'error': COLORS['error']
    }
    
    return html.Div([
        html.Span(icono, style={'marginRight': '8px'}),
        html.Span(texto, style={'fontSize': '12px'})
    ], style={
        'color': color_map.get(tipo, COLORS['text']),
        'marginBottom': '5px',
        'display': 'flex',
        'alignItems': 'center'
    })

def crear_layout_principal(contenido):
    """
    Crea el layout principal del dashboard
    
    Args:
        contenido: Contenido principal del dashboard
        
    Returns:
        html.Div: Layout completo
    """
    
    return html.Div([
        crear_sidebar(),
        html.Div(contenido, style=STYLES['main_content'])
    ], style=STYLES['dashboard_container'])

# ============================================================================
# COMPONENTES DE MÉTRICAS
# ============================================================================

def crear_tarjeta_metrica(titulo, valor, icono, color="primary", formato="number"):
    """
    Crea una tarjeta de métrica individual
    
    Args:
        titulo (str): Título de la métrica
        valor: Valor a mostrar
        icono (str): Emoji del icono
        color (str): Color de la tarjeta
        formato (str): Formato del valor
        
    Returns:
        html.Div: Tarjeta de métrica
    """
    
    # Formatear valor
    if formato == "currency":
        valor_formateado = f"${valor:,.0f}"
    elif formato == "percentage":
        valor_formateado = f"{valor:.1f}%"
    elif formato == "number":
        valor_formateado = f"{valor:,.0f}"
    else:
        valor_formateado = str(valor)
    
    # Determinar color
    color_value = COLORS.get(color, COLORS['primary'])
    
    return html.Div([
        html.Div([
            html.Div([
                html.Span(icono, style={
                    'fontSize': '32px',
                    'marginBottom': '10px',
                    'display': 'block'
                }),
                html.H3(valor_formateado, style={
                    'color': color_value,
                    'margin': '0',
                    'fontSize': '28px',
                    'fontWeight': 'bold'
                }),
                html.P(titulo, style={
                    'color': COLORS['text_secondary'],
                    'margin': '5px 0 0 0',
                    'fontSize': '14px'
                })
            ], style={'textAlign': 'center'})
        ])
    ], style={
        **STYLES['metric_card'],
        'borderColor': color_value
    })

def crear_grid_metricas(metricas_config):
    """
    Crea un grid de múltiples métricas
    
    Args:
        metricas_config (list): Lista de configuraciones de métricas
        
    Returns:
        html.Div: Grid de métricas
    """
    
    tarjetas = []
    
    for config in metricas_config:
        tarjeta = crear_tarjeta_metrica(
            titulo=config.get('titulo', ''),
            valor=config.get('valor', 0),
            icono=config.get('icono', '📊'),
            color=config.get('color', 'primary'),
            formato=config.get('formato', 'number')
        )
        tarjetas.append(tarjeta)
    
    return html.Div(tarjetas, style=STYLES['metrics_grid'])

# ============================================================================
# COMPONENTES DE CONTROL
# ============================================================================

def crear_selector_periodo():
    """
    Crea un selector de período estándar
    
    Returns:
        html.Div: Selector de período
    """
    
    return html.Div([
        html.Label("Período de Análisis:", style=STYLES['control_label']),
        dcc.Dropdown(
            id='periodo-dropdown',
            options=[
                {'label': 'Diario', 'value': 'D'},
                {'label': 'Semanal', 'value': 'W'},
                {'label': 'Mensual', 'value': 'M'},
                {'label': 'Trimestral', 'value': 'Q'}
            ],
            value='M',
            style={
                'backgroundColor': COLORS['surface'],
                'color': COLORS['text']
            }
        )
    ], style=STYLES['control_group'])

def crear_selector_fechas():
    """
    Crea un selector de rango de fechas estándar
    
    Returns:
        html.Div: Selector de fechas
    """
    
    from datetime import datetime
    
    return html.Div([
        html.Label("Rango de Fechas:", style=STYLES['control_label']),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=datetime(2024, 8, 1),
            end_date=datetime(2025, 12, 31),
            display_format='DD/MM/YYYY',
            style={
                'backgroundColor': COLORS['surface'],
                'color': COLORS['text']
            }
        )
    ], style=STYLES['control_group'])

def crear_panel_controles(controles_adicionales=None):
    """
    Crea un panel de controles estándar
    
    Args:
        controles_adicionales (list): Lista de controles adicionales
        
    Returns:
        html.Div: Panel de controles
    """
    
    controles = [
        crear_selector_periodo(),
        crear_selector_fechas()
    ]
    
    if controles_adicionales:
        controles.extend(controles_adicionales)
    
    return html.Div(controles, style=STYLES['controls_section'])

# ============================================================================
# COMPONENTES DE CONTENIDO
# ============================================================================

def crear_header_dashboard(titulo, subtitulo):
    """
    Crea el header de un dashboard
    
    Args:
        titulo (str): Título principal
        subtitulo (str): Subtítulo descriptivo
        
    Returns:
        html.Div: Header del dashboard
    """
    
    return html.Div([
        html.H1(titulo, style={
            'color': COLORS['text'],
            'marginBottom': '10px',
            'fontSize': '32px',
            'fontWeight': 'bold'
        }),
        html.P(subtitulo, style={
            'color': COLORS['text_secondary'],
            'fontSize': '16px',
            'margin': '0'
        })
    ], style=STYLES['header_section'])

def crear_contenedor_grafico(grafico_id, titulo=None):
    """
    Crea un contenedor para un gráfico
    
    Args:
        grafico_id (str): ID del gráfico
        titulo (str): Título opcional del gráfico
        
    Returns:
        html.Div: Contenedor del gráfico
    """
    
    contenido = []
    
    if titulo:
        contenido.append(
            html.H4(titulo, style={
                'color': COLORS['text'],
                'marginBottom': '15px',
                'fontSize': '18px'
            })
        )
    
    contenido.append(dcc.Graph(id=grafico_id))
    
    return html.Div(contenido, style=STYLES['chart_container'])

def crear_fila_graficos(graficos_config):
    """
    Crea una fila de gráficos
    
    Args:
        graficos_config (list): Lista de configuraciones de gráficos
        
    Returns:
        html.Div: Fila de gráficos
    """
    
    graficos = []
    
    for config in graficos_config:
        grafico = crear_contenedor_grafico(
            grafico_id=config.get('id', ''),
            titulo=config.get('titulo')
        )
        graficos.append(grafico)
    
    return html.Div(graficos, style=STYLES['charts_row'])

# ============================================================================
# COMPONENTES ESPECÍFICOS
# ============================================================================

def crear_tabla_resumen(datos_df, titulo="Resumen de Datos"):
    """
    Crea una tabla de resumen
    
    Args:
        datos_df (pd.DataFrame): DataFrame con los datos
        titulo (str): Título de la tabla
        
    Returns:
        html.Div: Componente de tabla
    """
    
    if datos_df.empty:
        return html.Div([
            html.H4(titulo, style={'color': COLORS['text']}),
            html.P("No hay datos disponibles", style={'color': COLORS['text_secondary']})
        ])
    
    # Convertir DataFrame a tabla HTML
    tabla = html.Table([
        html.Thead([
            html.Tr([
                html.Th(col, style={
                    'color': COLORS['text'],
                    'backgroundColor': COLORS['surface'],
                    'padding': '10px',
                    'border': f'1px solid {COLORS["primary"]}'
                }) for col in datos_df.columns
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(datos_df.iloc[i][col], style={
                    'color': COLORS['text'],
                    'backgroundColor': COLORS['background'],
                    'padding': '8px',
                    'border': f'1px solid {COLORS["primary"]}'
                }) for col in datos_df.columns
            ]) for i in range(min(len(datos_df), 10))  # Mostrar máximo 10 filas
        ])
    ], style={
        'width': '100%',
        'borderCollapse': 'collapse',
        'marginTop': '15px'
    })
    
    return html.Div([
        html.H4(titulo, style={'color': COLORS['text'], 'marginBottom': '15px'}),
        tabla
    ], style=STYLES['chart_container'])

def crear_alerta(mensaje, tipo="info"):
    """
    Crea una alerta informativa
    
    Args:
        mensaje (str): Mensaje de la alerta
        tipo (str): Tipo de alerta ('info', 'success', 'warning', 'error')
        
    Returns:
        html.Div: Componente de alerta
    """
    
    color_map = {
        'info': COLORS['primary'],
        'success': COLORS['success'],
        'warning': COLORS['warning'],
        'error': COLORS['error']
    }
    
    icon_map = {
        'info': '💡',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    
    color = color_map.get(tipo, COLORS['primary'])
    icono = icon_map.get(tipo, '💡')
    
    return html.Div([
        html.Span(icono, style={'marginRight': '10px', 'fontSize': '18px'}),
        html.Span(mensaje)
    ], style={
        'backgroundColor': color + '20',
        'border': f'1px solid {color}',
        'borderRadius': '5px',
        'padding': '15px',
        'color': COLORS['text'],
        'marginBottom': '20px',
        'display': 'flex',
        'alignItems': 'center'
    })

if __name__ == "__main__":
    # Test de componentes
    print("🎨 Módulo de componentes de dashboard cargado exitosamente") 