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
        # Datos para análisis de utilidad operativa
        if os.path.exists("archivos_output/ingresos_totales.csv"):
            df_ingresos = pd.read_csv("archivos_output/ingresos_totales.csv")
            df_ingresos["fecha"] = pd.to_datetime(df_ingresos["fecha"])
            datos['ingresos'] = df_ingresos
            print(f"✅ Ingresos cargados: {len(df_ingresos)} filas")
        else:
            datos['ingresos'] = pd.DataFrame()
        
        if os.path.exists("archivos_output/costos_operativos.csv"):
            df_costos_operativos = pd.read_csv("archivos_output/costos_operativos.csv")
            df_costos_operativos["fecha"] = pd.to_datetime(df_costos_operativos["fecha"])
            datos['costos_operativos'] = df_costos_operativos
            print(f"✅ Costos operativos cargados: {len(df_costos_operativos)} filas")
        else:
            datos['costos_operativos'] = pd.DataFrame()
        
        if os.path.exists("archivos_output/gastos_marketing.csv"):
            df_gastos_marketing = pd.read_csv("archivos_output/gastos_marketing.csv")
            df_gastos_marketing["fecha"] = pd.to_datetime(df_gastos_marketing["fecha"])
            datos['gastos_marketing'] = df_gastos_marketing
            print(f"✅ Gastos marketing cargados: {len(df_gastos_marketing)} filas")
        else:
            datos['gastos_marketing'] = pd.DataFrame()
        
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        for key in ['ingresos', 'costos_operativos', 'gastos_marketing']:
            if key not in datos:
                datos[key] = pd.DataFrame()
    
    return datos

# ======== FUNCIONES PARA GRÁFICOS ========
def crear_grafico_simple(df_ingresos, df_costos, df_marketing):
    """Crea un gráfico simple de barras."""
    
    # Calcular totales
    total_ingresos = df_ingresos['monto'].sum() if not df_ingresos.empty else 0
    total_costos = df_costos['monto'].sum() if not df_costos.empty else 0
    total_marketing = df_marketing['monto'].sum() if not df_marketing.empty else 0
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_bar(
        x=['Ingresos', 'Costos Operativos', 'Gastos Marketing'],
        y=[total_ingresos, total_costos, total_marketing],
        marker_color=['green', 'orange', 'blue']
    )
    
    fig.update_layout(
        title="Resumen Financiero",
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

# Variable global para datos
datos = {}

# Layout simple
app.layout = html.Div([
    html.Div([
        html.H1("🚤 Dashboard de Utilidad Operativa HotBoat", 
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
        html.A("📊 Reservas (8050)", href="http://localhost:8050", 
               style={'color': 'white', 'textDecoration': 'none', 'margin': '10px', 'padding': '10px', 'border': '1px solid white', 'borderRadius': '5px'}),
        html.Span("💰 Utilidad (8055)", 
                  style={'color': 'white', 'margin': '10px', 'padding': '10px', 'backgroundColor': 'rgba(255,255,255,0.3)', 'borderRadius': '5px'}),
        html.A("📈 Marketing (8056)", href="http://localhost:8056",
               style={'color': 'white', 'textDecoration': 'none', 'margin': '10px', 'padding': '10px', 'border': '1px solid white', 'borderRadius': '5px'})
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # Métricas
    html.Div([
        html.Div([
            html.H4("Total Ingresos", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="total-ingresos", style={'color': 'green', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Costos Operativos", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="total-costos", style={'color': 'orange', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Gastos Marketing", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="total-marketing", style={'color': 'blue', 'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
        
        html.Div([
            html.H4("Utilidad Operativa", style={'color': 'white', 'textAlign': 'center'}),
            html.H2(id="utilidad", style={'textAlign': 'center'})
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'})
    ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
    
    # Gráfico
    html.Div([
        dcc.Graph(id="grafico-principal")
    ], style={'backgroundColor': '#1a1a1a', 'padding': '20px', 'margin': '20px', 'borderRadius': '5px'})
    
], style={'backgroundColor': 'black', 'minHeight': '100vh', 'padding': '0'})

# Los callbacks se definen dentro del bloque main

if __name__ == '__main__':
    print("=== CARGANDO DASHBOARD DE UTILIDAD OPERATIVA ===")
    # Cargar datos
    datos = cargar_datos()
    
    # Función para obtener datos desde el callback
    def get_datos():
        return datos
    
    # Reemplazar la función actualizar_dashboard para usar datos locales
    @app.callback(
        [Output('total-ingresos', 'children'),
         Output('total-costos', 'children'),
         Output('total-marketing', 'children'),
         Output('utilidad', 'children'),
         Output('utilidad', 'style'),
         Output('grafico-principal', 'figure')],
        [Input('total-ingresos', 'id')]  # Dummy input para trigger inicial
    )
    def actualizar_dashboard_local(dummy):
        # Calcular métricas
        datos_local = get_datos()
        df_ingresos = datos_local.get('ingresos', pd.DataFrame())
        df_costos = datos_local.get('costos_operativos', pd.DataFrame())
        df_marketing = datos_local.get('gastos_marketing', pd.DataFrame())
        
        total_ingresos = df_ingresos['monto'].sum() if not df_ingresos.empty else 0
        total_costos = df_costos['monto'].sum() if not df_costos.empty else 0
        total_marketing = df_marketing['monto'].sum() if not df_marketing.empty else 0
        utilidad = total_ingresos - total_costos - total_marketing
        
        # Formato
        total_ingresos_fmt = f"${total_ingresos:,.0f}"
        total_costos_fmt = f"${total_costos:,.0f}"
        total_marketing_fmt = f"${total_marketing:,.0f}"
        utilidad_fmt = f"${utilidad:,.0f}"
        
        # Estilo para utilidad
        utilidad_style = {'color': 'green', 'textAlign': 'center'} if utilidad > 0 else {'color': 'red', 'textAlign': 'center'}
        
        # Crear gráfico
        fig = crear_grafico_simple(df_ingresos, df_costos, df_marketing)
        
        return total_ingresos_fmt, total_costos_fmt, total_marketing_fmt, utilidad_fmt, utilidad_style, fig
    
    print("Dashboard de utilidad iniciado exitosamente")
    print("Accede en: http://localhost:8055")
    app.run(debug=True, host='localhost', port=8055) 