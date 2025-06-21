import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime
import numpy as np
import glob
import re

# Configuración de colores
COLORS = {
    'background': '#111111',
    'text': '#FFFFFF',
    'grid': '#333333',
    'primary': '#4285F4',  # Azul de Google
    'secondary': '#34A853',  # Verde de Google
    'accent': '#FBBC04',    # Amarillo de Google
    'expense': '#EA4335',   # Rojo de Google
    'card_bg': '#222222'
}

def parse_google_ads_date(date_str):
    """Parsea fechas en formato español de Google Ads."""
    try:
        # Formato: "Semana de 10 mar 2025"
        if 'Semana de' in str(date_str):
            # Extraer la fecha después de "Semana de"
            date_part = str(date_str).replace('Semana de ', '').strip()
            
            # Mapeo de meses en español
            meses = {
                'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
                'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
                'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
            }
            
            # Parsear usando regex
            match = re.match(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', date_part)
            if match:
                dia, mes, año = match.groups()
                mes_num = meses.get(mes.lower(), '01')
                return pd.to_datetime(f"{año}-{mes_num}-{dia.zfill(2)}")
        
        # Intentar parseo normal
        return pd.to_datetime(date_str)
        
    except Exception as e:
        print(f"Error parseando fecha '{date_str}': {e}")
        return pd.NaT

def limpiar_valor_monetario(valor):
    """Limpia y convierte valores monetarios (ej: 'CLP1,234') a float."""
    if pd.isna(valor):
        return 0.0
    s_valor = str(valor).replace('CLP', '').replace(',', '').strip()
    if s_valor == '' or s_valor == '""':
        return 0.0
    try:
        return float(s_valor)
    except (ValueError, TypeError):
        return 0.0

def convertir_a_numero(valor):
    """Convierte un valor a número, limpiando comas."""
    if pd.isna(valor):
        return 0
    s_valor = str(valor).replace(',', '').strip()
    if s_valor == '':
        return 0
    try:
        return int(s_valor)
    except (ValueError, TypeError):
        return 0
        
def cargar_y_limpiar_csv(ruta_archivo, columnas_monetarias, columnas_numericas):
    """Carga un CSV y limpia las columnas especificadas."""
    if not os.path.exists(ruta_archivo):
        print(f"   ⚠️ Archivo no encontrado: {os.path.basename(ruta_archivo)}")
        return None
    
    df = pd.read_csv(ruta_archivo)
    
    for col in columnas_monetarias:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_valor_monetario)
            
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = df[col].apply(convertir_a_numero)
            
    print(f"   ✅ Cargado y limpiado: {os.path.basename(ruta_archivo)} ({df.shape[0]} filas)")
    return df

def cargar_datos_google_ads():
    """Carga y procesa todos los datos de Google Ads."""
    try:
        print("🔍 Cargando y procesando datos de Google Ads...")
        ruta_base = 'archivos_input/archivos input marketing/google ads'
        datos = {}

        # 1. Series temporales
        archivo_series = os.path.join(ruta_base, 'Series_temporales(2025.03.10-2025.06.20).csv')
        if os.path.exists(archivo_series):
            df_series = pd.read_csv(archivo_series)
            df_series['Semana'] = df_series['Semana'].apply(parse_google_ads_date)
            df_series['Costo'] = df_series['Costo'].apply(limpiar_valor_monetario)
            df_series['CPC prom.'] = df_series['CPC prom.'].apply(limpiar_valor_monetario)
            df_series['Clics'] = df_series['Clics'].apply(convertir_a_numero)
            df_series['Impresiones'] = df_series['Impresiones'].apply(convertir_a_numero)
            df_series = df_series.dropna(subset=['Semana'])
            datos['series_temporales'] = df_series
            print(f"   ✅ Procesado: Series temporales ({df_series.shape[0]} filas)")
        
        # Cargar otros archivos
        archivos_a_cargar = {
            'campañas': ('Campañas(2025.03.10-2025.06.20).csv', ['Costo', 'CPC prom.'], ['Clics', 'Impresiones']),
            'grupos_anuncios': ('Grupos_de_anuncios(2025.03.10-2025.06.20).csv', ['Costo', 'CPC prom.'], ['Clics', 'Impresiones']),
            'palabras_clave': ('Palabras_clave_de_la_Búsqueda(2025.03.10-2025.06.20).csv', ['Costo', 'CPC prom.'], ['Clics', 'Impresiones']),
            'dispositivos': ('Dispositivos(2025.03.10-2025.06.20).csv', ['Costo', 'CPC prom.'], ['Clics', 'Impresiones']),
            'demograficos': ('Datos_demográficos(Género_Edad_2025.03.10-2025.06.20).csv', [], ['Impresiones']),
        }
        
        for clave, (nombre_archivo, cols_mon, cols_num) in archivos_a_cargar.items():
            ruta = os.path.join(ruta_base, nombre_archivo)
            datos[clave] = cargar_y_limpiar_csv(ruta, cols_mon, cols_num)
        
        # Día y hora
        archivo_dia_hora = os.path.join(ruta_base, 'Día_y_hora(Día_Hora_2025.03.10-2025.06.20).csv')
        df_dia_hora = cargar_y_limpiar_csv(archivo_dia_hora, [], ['Impresiones']) # No hay costo, solo impresiones
        if df_dia_hora is not None:
            # Las columnas son 'Día' y 'Hora de inicio', no se necesita parseo de fecha aquí
            datos['dia_hora'] = df_dia_hora
            
        print(f"\n🎉 Carga completada: {len(datos)} datasets procesados.")
        return datos
        
    except Exception as e:
        print(f"❌ Error crítico cargando datos: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

# ==============================================================================
# Funciones para Gráficos (con verificaciones de datos)
# ==============================================================================

def crear_grafico_vacio(titulo="No hay datos disponibles"):
    """Genera una figura de Plotly vacía con un mensaje."""
    fig = go.Figure()
    fig.update_layout(
        title=titulo,
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        xaxis={'visible': False},
        yaxis={'visible': False},
        annotations=[{
            "text": "No hay datos para mostrar.",
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16}
        }]
    )
    return fig

def crear_grafico_series_temporales(datos):
    """Crea un gráfico de series temporales con las métricas principales."""
    if 'series_temporales' not in datos or datos['series_temporales'].empty:
        return crear_grafico_vacio('Series Temporales')
    
    df = datos['series_temporales']
    
    if df['Semana'].isna().all():
        return crear_grafico_vacio('Error en Fechas de Series Temporales')
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Clics', 'Impresiones', 'CPC Promedio', 'Costo'),
        vertical_spacing=0.2,
        horizontal_spacing=0.1
    )
    
    fig.add_trace(go.Scatter(x=df['Semana'], y=df['Clics'], name='Clics', mode='lines+markers', line_color=COLORS['primary']), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Semana'], y=df['Impresiones'], name='Impresiones', mode='lines+markers', line_color=COLORS['secondary']), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['Semana'], y=df['CPC prom.'], name='CPC Promedio', mode='lines+markers', line_color=COLORS['accent']), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Semana'], y=df['Costo'], name='Costo', mode='lines+markers', line_color=COLORS['expense']), row=2, col=2)
    
    fig.update_layout(
        title_text='Evolución Semanal de Métricas de Google Ads',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        showlegend=False,
        height=600,
        margin=dict(l=40, r=40, t=80, b=40)
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    return fig

def crear_grafico_campañas(datos):
    """Crea un gráfico de rendimiento por campañas."""
    if 'campañas' not in datos or datos['campañas'].empty:
        return crear_grafico_vacio('Rendimiento por Campañas')
    
    df = datos['campañas'].nlargest(10, 'Costo')
    
    fig = go.Figure(go.Bar(
        x=df['Costo'],
        y=df['Nombre de la campaña'],
        orientation='h',
        marker_color=COLORS['primary'],
        text=df['Costo'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Top 10 Campañas por Costo',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        xaxis_title='Costo (CLP)',
        yaxis_title='Campaña',
        yaxis=dict(autorange="reversed"),
        height=400,
        margin=dict(l=150, t=50, b=40, r=40)
    )
    return fig

def crear_grafico_palabras_clave(datos):
    """Crea un gráfico de rendimiento por palabras clave."""
    if 'palabras_clave' not in datos or datos['palabras_clave'].empty:
        return crear_grafico_vacio('Rendimiento por Palabras Clave')
        
    df = datos['palabras_clave'].nlargest(10, 'Costo')

    fig = go.Figure(go.Bar(
        x=df['Costo'],
        y=df['Palabra clave de la Búsqueda'],
        orientation='h',
        marker_color=COLORS['secondary'],
        text=df['Costo'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto'
    ))

    fig.update_layout(
        title='Top 10 Palabras Clave por Costo',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        xaxis_title='Costo (CLP)',
        yaxis_title='Palabra Clave',
        yaxis=dict(autorange="reversed"),
        height=400,
        margin=dict(l=150, t=50, b=40, r=40)
    )
    return fig

def crear_grafico_dispositivos(datos):
    """Crea un gráfico de dona para la distribución por dispositivos."""
    if 'dispositivos' not in datos or datos['dispositivos'].empty:
        return crear_grafico_vacio('Distribución por Dispositivos')
        
    df = datos['dispositivos']
    
    fig = go.Figure(go.Pie(
        labels=df['Dispositivo'],
        values=df['Costo'],
        hole=.5,
        marker_colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['expense']],
        textinfo='percent+label',
        pull=[0.05, 0, 0, 0]
    ))
    
    fig.update_layout(
        title='Distribución de Gasto por Dispositivo',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        showlegend=False,
        height=400,
        margin=dict(t=50, b=40)
    )
    return fig

def crear_grafico_demograficos(datos):
    """Crea un gráfico de barras agrupadas para datos demográficos."""
    if 'demograficos' not in datos or datos['demograficos'].empty:
        return crear_grafico_vacio('Datos Demográficos')
        
    df = datos['demograficos']
    
    # Agrupar por Edad y Género para asegurar datos únicos
    df_grouped = df.groupby(['Rango de edades', 'Género'])['Impresiones'].sum().reset_index()
    
    fig = px.bar(
        df_grouped,
        x='Rango de edades',
        y='Impresiones',
        color='Género',
        barmode='group',
        text_auto='.2s',
        color_discrete_map={'Masculino': COLORS['primary'], 'Femenino': COLORS['accent'], 'Desconocido': COLORS['grid']}
    )
    
    fig.update_layout(
        title='Impresiones por Edad y Género',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        xaxis_title='Rango de Edad',
        yaxis_title='Impresiones',
        height=400,
        legend_title_text='Género',
        margin=dict(t=50, b=40)
    )
    return fig

def crear_grafico_dia_hora(datos):
    """Crea un mapa de calor para impresiones por día y hora."""
    if 'dia_hora' not in datos or datos['dia_hora'].empty:
        return crear_grafico_vacio('Impresiones por Día y Hora')
        
    df = datos['dia_hora']
    
    # Extraer y normalizar hora
    df['hora'] = df['Hora de inicio'].str.extract(r'(\d+)').astype(int)
    
    # Crear tabla pivote
    pivot_table = df.pivot_table(index='Día', columns='hora', values='Impresiones', aggfunc='sum').fillna(0)
    
    # Ordenar días de la semana y horas
    dias_ordenados = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    pivot_table = pivot_table.reindex(dias_ordenados).fillna(0)
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='Viridis',
        hovertemplate='Día: %{y}<br>Hora: %{x}<br>Impresiones: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Heatmap de Impresiones por Día y Hora',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font_color=COLORS['text'],
        xaxis_title='Hora del Día',
        yaxis_title='Día de la Semana',
        height=400,
        margin=dict(t=50, b=40)
    )
    return fig

# ==============================================================================
# Generación de Insights
# ==============================================================================

def generar_insights_google_ads(datos):
    """Genera un resumen de insights y recomendaciones."""
    if not datos:
        return html.P("No se pudieron generar insights por falta de datos.")
    
    insights = []
    
    # Insight de Campañas
    if 'campañas' in datos and not datos['campañas'].empty:
        df_campañas = datos['campañas']
        top_campaña = df_campañas.loc[df_campañas['Costo'].idxmax()]
        insights.append(html.Li(f"La campaña con mayor inversión es '{top_campaña['Nombre de la campaña']}' con un costo de ${top_campaña['Costo']:,.0f} CLP."))
    
    # Insight de Palabras Clave
    if 'palabras_clave' in datos and not datos['palabras_clave'].empty:
        df_palabras = datos['palabras_clave']
        top_palabra = df_palabras.loc[df_palabras['Costo'].idxmax()]
        insights.append(html.Li(f"La palabra clave de mayor costo es '{top_palabra['Palabra clave de la Búsqueda']}' (${top_palabra['Costo']:,.0f} CLP)."))

    # Insight de Dispositivos
    if 'dispositivos' in datos and not datos['dispositivos'].empty:
        df_dispositivos = datos['dispositivos']
        top_dispositivo = df_dispositivos.loc[df_dispositivos['Costo'].idxmax()]
        insights.append(html.Li(f"El dispositivo con más gasto es '{top_dispositivo['Dispositivo']}', concentrando la mayor parte de la inversión."))

    # Insight Demográfico
    if 'demograficos' in datos and not datos['demograficos'].empty:
        df_demograficos = datos['demograficos']
        top_segmento = df_demograficos.loc[df_demograficos['Impresiones'].idxmax()]
        insights.append(html.Li(f"El segmento demográfico con más impresiones es '{top_segmento['Rango de edades']}' de género '{top_segmento['Género']}'."))

    return html.Ul(insights, style={'color': COLORS['text']})

# ==============================================================================
# Creación de la Aplicación Dash
# ==============================================================================

app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='assets')
server = app.server

# Cargar datos una sola vez al iniciar
datos_google_ads = cargar_datos_google_ads()

# Definir layout
if datos_google_ads is not None:
    app.layout = html.Div(id='main-container', children=[
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-load-trigger', style={'display': 'none'}),
        
        # Header
        html.Div([
            html.H1('📊 Dashboard de Google Ads', style={'color': COLORS['primary'], 'textAlign': 'center'}),
            html.P('Análisis completo del rendimiento de campañas en Google Ads', style={'color': COLORS['text'], 'textAlign': 'center'})
        ]),
        
        # Contenedores de Gráficos
        html.Div([
            # Columna Izquierda
            html.Div([
                html.Div(dcc.Graph(id='grafico-series'), className='card'),
                html.Div(dcc.Graph(id='grafico-palabras'), className='card'),
                html.Div(dcc.Graph(id='grafico-dia-hora'), className='card'),
            ], className='column'),
            # Columna Derecha
            html.Div([
                html.Div(dcc.Graph(id='grafico-campañas'), className='card'),
                html.Div(dcc.Graph(id='grafico-dispositivos'), className='card'),
                html.Div(dcc.Graph(id='grafico-demograficos'), className='card'),
            ], className='column'),
        ], className='row'),

        # Insights
        html.Div([
            html.H3('💡 Insights y Recomendaciones', style={'color': COLORS['text']}),
            html.Div(id='insights-contenido', className='insights-box')
        ], className='card'),
    ])
else:
    app.layout = html.Div([
        html.H1('⚠️ Error al Cargar Datos', style={'color': 'red', 'textAlign': 'center'}),
        html.P('No se pudieron cargar o procesar los archivos de Google Ads. Verifica la consola para más detalles.')
    ])

@callback(
    [Output('grafico-series', 'figure'),
     Output('grafico-campañas', 'figure'),
     Output('grafico-palabras', 'figure'),
     Output('grafico-dispositivos', 'figure'),
     Output('grafico-demograficos', 'figure'),
     Output('grafico-dia-hora', 'figure'),
     Output('insights-contenido', 'children')],
    [Input('page-load-trigger', 'children')]
)
def actualizar_dashboard(_):
    if datos_google_ads is None:
        # Si los datos no se cargaron, devolver gráficos vacíos
        return [crear_grafico_vacio("Error en Carga de Datos")] * 6 + [html.P("Error en la carga de datos.")]

    try:
        # Crear todos los gráficos
        fig_series = crear_grafico_series_temporales(datos_google_ads)
        fig_campañas = crear_grafico_campañas(datos_google_ads)
        fig_palabras = crear_grafico_palabras_clave(datos_google_ads)
        fig_dispositivos = crear_grafico_dispositivos(datos_google_ads)
        fig_demograficos = crear_grafico_demograficos(datos_google_ads)
        fig_dia_hora = crear_grafico_dia_hora(datos_google_ads)
        
        # Generar insights
        insights = generar_insights_google_ads(datos_google_ads)
        
        return fig_series, fig_campañas, fig_palabras, fig_dispositivos, fig_demograficos, fig_dia_hora, insights
        
    except Exception as e:
        print(f"❌ Error en el callback: {e}")
        import traceback
        print(traceback.format_exc())
        return [crear_grafico_vacio(f"Error en Callback: {e}")] * 6 + [html.P(f"Error en callback: {e}")]

if __name__ == '__main__':
    print("=== Iniciando Dashboard de Google Ads ===")
    app.run(debug=True, port=8058) 