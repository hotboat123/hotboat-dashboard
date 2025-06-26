import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# ======== CARGA DE DATOS ========
def cargar_datos():
    """Carga todos los archivos CSV necesarios para el dashboard."""
    datos = {}
    
    try:
        # Carga de datos de reservas
        if os.path.exists("archivos_output/reservas_HotBoat.csv"):
            df = pd.read_csv("archivos_output/reservas_HotBoat.csv")
            df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])
            datos['reservas'] = df
            print(f"✅ Reservas cargadas: {len(df)} filas")
        else:
            datos['reservas'] = pd.DataFrame()
        
        # Carga de datos financieros
        if os.path.exists("archivos_output/abonos hotboat.csv"):
            df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
            df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"])
            df_payments["Monto"] = df_payments["Monto"].astype(float)
            datos['pagos'] = df_payments
            print(f"✅ Pagos cargados: {len(df_payments)} filas")
        else:
            datos['pagos'] = pd.DataFrame()
        
        if os.path.exists("archivos_output/gastos hotboat.csv"):
            df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")
            df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"])
            df_expenses["Monto"] = df_expenses["Monto"].astype(float)
            datos['gastos'] = df_expenses
            print(f"✅ Gastos cargados: {len(df_expenses)} filas")
        else:
            datos['gastos'] = pd.DataFrame()
        
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        for key in ['reservas', 'pagos', 'gastos']:
            if key not in datos:
                datos[key] = pd.DataFrame()
    
    return datos

# ======== FUNCIONES PARA GRÁFICOS ========
def crear_grafico_reservas_simple(df_reservas):
    """Crea un gráfico simple de reservas por día."""
    
    if df_reservas.empty:
        fig = go.Figure()
        fig.add_annotation(text="No hay datos de reservas", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(template="plotly_dark", plot_bgcolor='black', paper_bgcolor='black', font_color='white')
        return fig
    
    # Agrupar por día
    reservas_por_dia = df_reservas.groupby(df_reservas['fecha_trip'].dt.date).size().reset_index()
    reservas_por_dia.columns = ['fecha', 'cantidad']
    
    fig = go.Figure()
    fig.add_scatter(
        x=reservas_por_dia['fecha'],
        y=reservas_por_dia['cantidad'],
        mode='lines+markers',
        name='Reservas',
        line_color='#007bff',
        marker_color='#007bff'
    )
    
    fig.update_layout(
        title="Reservas por Día",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Reservas",
        template="plotly_dark",
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    
    return fig

def crear_grafico_ingresos_simple(df_pagos, df_gastos):
    """Crea un gráfico simple de ingresos vs gastos."""
    
    total_ingresos = df_pagos['Monto'].sum() if not df_pagos.empty else 0
    total_gastos = df_gastos['Monto'].sum() if not df_gastos.empty else 0
    
    fig = go.Figure()
    fig.add_bar(
        x=['Ingresos', 'Gastos'],
        y=[total_ingresos, total_gastos],
        marker_color=['green', 'red']
    )
    
    fig.update_layout(
        title="Ingresos vs Gastos",
        xaxis_title="Categoría",
        yaxis_title="Monto ($)",
        template="plotly_dark",
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    
    return fig

# ======== APLICACIÓN PRINCIPAL ========
app = dash.Dash(__name__)

# Cargar datos
datos = cargar_datos()

# Layout simple
app.layout = html.Div([
    html.Div([
        html.H1("🚤 Dashboard de Reservas y Finanzas HotBoat", 
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
    
    # Métricas
    html.Div([
        html.Div([
            html.H4("Total Reservas", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="total-reservas", style={'color': '#007bff', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Total Ingresos", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="total-ingresos", style={'color': 'green', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Total Gastos", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="total-gastos", style={'color': 'red', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Balance", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="balance", style={'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'})
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
    
    # Gráficos
    html.Div([
        html.Div([
            dcc.Graph(id="grafico-reservas")
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'borderRadius': '5px', 'width': '48%', 'display': 'inline-block', 'margin': '1%'}),
        
        html.Div([
            dcc.Graph(id="grafico-ingresos")
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'borderRadius': '5px', 'width': '48%', 'display': 'inline-block', 'margin': '1%'})
    ])
    
], style={'backgroundColor': 'black', 'minHeight': '100vh', 'padding': '0'})

# Callback
@app.callback(
    [Output('total-reservas', 'children'),
     Output('total-ingresos', 'children'),
     Output('total-gastos', 'children'),
     Output('balance', 'children'),
     Output('balance', 'style'),
     Output('grafico-reservas', 'figure'),
     Output('grafico-ingresos', 'figure')],
    [Input('total-reservas', 'id')]  # Dummy input para trigger inicial
)
def actualizar_dashboard(dummy):
    # Obtener datos
    df_reservas = datos.get('reservas', pd.DataFrame())
    df_pagos = datos.get('pagos', pd.DataFrame())
    df_gastos = datos.get('gastos', pd.DataFrame())
    
    # Calcular métricas
    total_reservas = len(df_reservas) if not df_reservas.empty else 0
    total_ingresos = df_pagos['Monto'].sum() if not df_pagos.empty else 0
    total_gastos = df_gastos['Monto'].sum() if not df_gastos.empty else 0
    balance = total_ingresos - total_gastos
    
    # Formato
    total_ingresos_fmt = f"${total_ingresos:,.0f}"
    total_gastos_fmt = f"${total_gastos:,.0f}"
    balance_fmt = f"${balance:,.0f}"
    
    # Estilo para balance
    balance_style = {'color': 'green', 'textAlign': 'center'} if balance > 0 else {'color': 'red', 'textAlign': 'center'}
    
    # Crear gráficos
    fig_reservas = crear_grafico_reservas_simple(df_reservas)
    fig_ingresos = crear_grafico_ingresos_simple(df_pagos, df_gastos)
    
    return str(total_reservas), total_ingresos_fmt, total_gastos_fmt, balance_fmt, balance_style, fig_reservas, fig_ingresos

if __name__ == '__main__':
    print("=== CARGANDO DASHBOARD DE RESERVAS Y FINANZAS ===")
    print("Dashboard de reservas iniciado exitosamente")
    print("Accede en: http://localhost:8050")
    app.run(debug=True, host='localhost', port=8050) 