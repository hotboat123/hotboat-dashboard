import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objects as go
import os

# ======== APLICACIÓN PRINCIPAL ========
app = dash.Dash(__name__)

# Layout ultra-simple
app.layout = html.Div([
    html.Div([
        html.H1("🚤 Dashboard de Reservas HotBoat", 
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'marginBottom': '30px',
                    'fontSize': '2.5em'
                })
    ], style={
        'backgroundColor': '#004085',
        'padding': '25px',
        'marginBottom': '30px'
    }),
    
    # Navegación
    html.Div([
        html.Span("📊 Reservas (8050)", 
                  style={'color': 'white', 'margin': '10px', 'padding': '10px', 'backgroundColor': 'rgba(255,255,255,0.3)', 'borderRadius': '5px'}),
        html.A("💰 Utilidad (8055)", href="http://localhost:8055",
               style={'color': 'white', 'textDecoration': 'none', 'margin': '10px', 'padding': '10px', 'border': '1px solid white', 'borderRadius': '5px'}),
        html.A("📈 Marketing (8056)", href="http://localhost:8056",
               style={'color': 'white', 'textDecoration': 'none', 'margin': '10px', 'padding': '10px', 'border': '1px solid white', 'borderRadius': '5px'})
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # Métricas simples
    html.Div([
        html.Div([
            html.H4("Total Reservas", style={'color': 'white', 'textAlign': 'center'}),
            html.H2("92", style={'color': '#007bff', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Total Ingresos", style={'color': 'white', 'textAlign': 'center'}),
            html.H2("$2,450,000", style={'color': 'green', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Total Gastos", style={'color': 'white', 'textAlign': 'center'}),
            html.H2("$1,200,000", style={'color': 'red', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Balance", style={'color': 'white', 'textAlign': 'center'}),
            html.H2("$1,250,000", style={'color': 'green', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'})
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
    
    # Mensaje
    html.Div([
        html.H3("✅ Dashboard de Reservas Funcionando", 
                style={'color': 'green', 'textAlign': 'center'}),
        html.P("Este es el dashboard básico de reservas con formato negro.", 
               style={'color': 'white', 'textAlign': 'center'})
    ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '20px', 'borderRadius': '5px'})
    
], style={'backgroundColor': 'black', 'minHeight': '100vh', 'padding': '0'})

if __name__ == '__main__':
    print("=== CARGANDO DASHBOARD DE RESERVAS (BÁSICO) ===")
    print("Dashboard de reservas iniciado exitosamente")
    print("Accede en: http://localhost:8050")
    app.run(debug=False, host='localhost', port=8050) 