#!/usr/bin/env python3
"""
🚤 HOTBOAT - ESTILOS DE DASHBOARD ORIGINALES
============================================

Mantiene los estilos exactos de la versión original que funciona.
Interfaz negra con selector arriba.

Autor: Sistema HotBoat Optimizado
Versión: 2.0
"""

# Estilos CSS originales que funcionan
ESTILOS_ORIGINALES = {
    'backgroundColor': '#1e1e1e',
    'color': 'white',
    'fontFamily': 'Arial, sans-serif'
}

ESTILO_CONTENEDOR_PRINCIPAL = {
    'backgroundColor': '#1e1e1e',
    'padding': '20px',
    'minHeight': '100vh'
}

ESTILO_TITULO_PRINCIPAL = {
    'textAlign': 'center',
    'color': 'white',
    'fontSize': '28px',
    'marginBottom': '30px',
    'backgroundColor': '#2d2d2d',
    'padding': '15px',
    'borderRadius': '10px'
}

ESTILO_SELECTOR_DASHBOARD = {
    'backgroundColor': '#2d2d2d',
    'color': 'white',
    'border': '1px solid #555',
    'marginBottom': '20px'
}

ESTILO_TARJETA = {
    'backgroundColor': '#2d2d2d',
    'border': '1px solid #555',
    'borderRadius': '10px',
    'padding': '15px',
    'margin': '10px 0',
    'color': 'white'
}

ESTILO_GRAFICO = {
    'backgroundColor': '#1e1e1e',
    'paper_bgcolor': '#1e1e1e',
    'plot_bgcolor': '#1e1e1e',
    'font': {'color': 'white'},
    'title': {'font': {'color': 'white'}},
    'xaxis': {
        'gridcolor': '#555',
        'tickfont': {'color': 'white'},
        'titlefont': {'color': 'white'}
    },
    'yaxis': {
        'gridcolor': '#555',
        'tickfont': {'color': 'white'},
        'titlefont': {'color': 'white'}
    }
}

def get_layout_config():
    """Configuración de layout original que funciona"""
    return ESTILO_GRAFICO

def get_container_style():
    """Estilo del contenedor principal"""
    return ESTILO_CONTENEDOR_PRINCIPAL

def get_title_style():
    """Estilo del título principal"""
    return ESTILO_TITULO_PRINCIPAL

def get_card_style():
    """Estilo de las tarjetas"""
    return ESTILO_TARJETA

def get_dropdown_style():
    """Estilo del selector/dropdown"""
    return ESTILO_SELECTOR_DASHBOARD 