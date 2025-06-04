import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import numpy as np
from plotly.subplots import make_subplots

# Importar colores y estilos comunes
COLORS = {
    'background': '#111111',
    'text': '#FFFFFF',
    'grid': '#333333',
    'primary': '#00A6FB',
    'secondary': '#0582CA',
    'expense': '#FF6B6B',
    'income': '#4CAF50',
    'card_bg': '#222222'
}

CARD_STYLE = {
    'backgroundColor': COLORS['card_bg'],
    'padding': '15px',
    'margin': '10px',
    'borderRadius': '5px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'flex': '1',
    'minWidth': '200px',
    'maxWidth': '300px'
}

def crear_header():
    """Crea el encabezado del dashboard."""
    return html.Div([
        html.H1('Dashboard de Marketing', style={
            'color': COLORS['primary'],
            'textAlign': 'center',
            'marginBottom': '20px'
        })
    ])

def crear_filtros(fecha_min, fecha_max):
    """Crea los filtros de fecha."""
    return html.Div([
        dcc.DatePickerRange(
            id='date-range-picker',
            min_date_allowed=fecha_min,
            max_date_allowed=fecha_max,
            start_date=fecha_min,
            end_date=fecha_max,
            style={'backgroundColor': COLORS['card_bg']},
        )
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'padding': '15px',
        'marginBottom': '20px',
        'borderRadius': '5px'
    })

def crear_selector_periodo():
    """Crea el selector de período para la evolución temporal."""
    return html.Div([
        dcc.RadioItems(
            id='periodo-selector',
            options=[
                {'label': 'Diario', 'value': 'D'},
                {'label': 'Semanal', 'value': 'W'},
                {'label': 'Mensual', 'value': 'M'}
            ],
            value='D',
            style={'color': COLORS['text']},
            labelStyle={'display': 'inline-block', 'marginRight': '20px'}
        )
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'padding': '15px',
        'marginBottom': '20px',
        'borderRadius': '5px'
    })

def crear_contenedor_grafico(id_grafico, titulo=""):
    """Crea un contenedor para un gráfico."""
    return html.Div([
        html.H3(titulo, style={'color': COLORS['text'], 'marginBottom': '10px'}),
        dcc.Graph(id=id_grafico)
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'padding': '15px',
        'marginBottom': '25px',
        'borderRadius': '5px'
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

# Definir las métricas disponibles para comparación
METRICAS_COMPARACION = {
    'cpc': {'nombre': 'CPC (todos)', 'formato': '${:,.0f}', 'color': '#1f77b4'},
    'ctr': {'nombre': 'CTR (todos)', 'formato': '{:.2%}', 'color': '#ff7f0e'},
    'gasto': {'nombre': 'Importe gastado (CLP)', 'formato': '${:,.0f}', 'color': '#2ca02c'},
    'conversion': {'nombre': 'Artículos agregados al carrito', 'formato': '{:,.0f}', 'color': '#d62728'},
    'costo_conversion': {'nombre': 'Costo por artículo agregado al carrito', 'formato': '${:,.0f}', 'color': '#9467bd'}
}

# Función para cargar datos de marketing
def cargar_datos_marketing():
    """Carga los archivos CSV de marketing para el análisis."""
    print("\nIniciando carga de datos...")
    
    try:
    # Crear directorio para gráficos si no existe
    if not os.path.exists("archivos_output/graficos"):
        os.makedirs("archivos_output/graficos")
            print("Directorio de gráficos creado")
        
        # Verificar la existencia del archivo
        archivo_path = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv"
        if not os.path.exists(archivo_path):
            print(f"ERROR: No se encuentra el archivo en la ruta: {archivo_path}")
            return None
        
        print(f"Cargando archivo: {archivo_path}")
    # Cargar datos de campaña de Meta
        df_campana = pd.read_csv(archivo_path)
        print(f"Archivo cargado exitosamente. Dimensiones: {df_campana.shape}")
        
        # Mostrar las columnas disponibles
        print("\nColumnas en el archivo:")
        print(df_campana.columns.tolist())
    
    # Convertir columnas numéricas en df_campana (limpiando formato de moneda)
    columnas_numericas = [
        "Alcance", "Impresiones", "Frecuencia", "Importe gastado (CLP)", 
        "Clics en el enlace", "CTR (todos)", "CPC (todos)", 
        "CPM (costo por mil impresiones)", "Artículos agregados al carrito",
            "Costo por artículo agregado al carrito", "Reproducciones de video de 3 segundos",
            "Reproducciones de video hasta el 25%", "Reproducciones de video hasta el 50%",
            "Reproducciones de video hasta el 75%", "Reproducciones de video hasta el 100%"
    ]
    
        print("\nConvirtiendo columnas numéricas...")
    # Convertir columnas numéricas
    for col in columnas_numericas:
        if col in df_campana.columns:
            df_campana.loc[:, col] = pd.to_numeric(df_campana[col].astype(str).str.replace(',', '.'), errors='coerce')
                print(f"Columna {col} convertida")
    
        print("\nAñadiendo columnas calculadas...")
    # Añadir columnas útiles para análisis
    df_campana.loc[:, 'CTR (%)'] = df_campana['CTR (todos)'] * 100  # Convertir a porcentaje
        
        # Calcular métricas de hook rate
        df_campana.loc[:, 'Hook Rate 3s (%)'] = (df_campana['Reproducciones de video de 3 segundos'] / df_campana['Impresiones'] * 100).fillna(0)
        df_campana.loc[:, 'Hook Rate 25% (%)'] = (df_campana['Reproducciones de video hasta el 25%'] / df_campana['Impresiones'] * 100).fillna(0)
        df_campana.loc[:, 'Hook Rate 50% (%)'] = (df_campana['Reproducciones de video hasta el 50%'] / df_campana['Impresiones'] * 100).fillna(0)
        df_campana.loc[:, 'Hook Rate 75% (%)'] = (df_campana['Reproducciones de video hasta el 75%'] / df_campana['Impresiones'] * 100).fillna(0)
        df_campana.loc[:, 'Hook Rate 100% (%)'] = (df_campana['Reproducciones de video hasta el 100%'] / df_campana['Impresiones'] * 100).fillna(0)
    
    # Identificar categoría de público (advantage vs pucon)
    df_campana.loc[:, 'Público'] = df_campana['Nombre del conjunto de anuncios'].apply(
        lambda x: 'Advantage' if 'advantage' in str(x).lower() else 
                  'Pucón' if 'pucon' in str(x).lower() else 'Otro'
    )
    
    # Clasificar tipo de anuncio
    df_campana.loc[:, 'Tipo de Anuncio'] = df_campana['Nombre del anuncio'].apply(
        lambda x: 'Video explicativo' if 'explicando servicio' in str(x).lower() else
                  'Video inicial' if 'inicial' in str(x).lower() else
                  'Video publicitario' if 'publicitario' in str(x).lower() else
                  'Video Flo' if 'flo' in str(x).lower() else
                  'Día de la madre' if 'madre' in str(x).lower() or 'dia madre' in str(x).lower() else
                  'Parejas Amor' if 'parejas amor' in str(x).lower() else
                  'Parejas Descuento' if 'parejas dcto' in str(x).lower() or 'parejas descuento' in str(x).lower() else
                  'Video Karin' if 'karin' in str(x).lower() else
                  'Video Lluvia' if 'lluvia' in str(x).lower() else
                  'Otro'
    )
    
        print("\nConvirtiendo fechas...")
    # Convertir fechas
    df_campana.loc[:, 'Día'] = pd.to_datetime(df_campana['Día'])
    
    # Llenar valores nulos en nombres de campaña
    df_campana.loc[:, 'Nombre de la campaña'] = df_campana['Nombre de la campaña'].fillna('Sin nombre')
    
        print("\nCreando DataFrame de gasto diario...")
    # Crear una copia del DataFrame de campaña para usarlo como gasto diario
    df_gasto_diario = df_campana.groupby('Día')['Importe gastado (CLP)'].sum().reset_index()
    
        print("Carga de datos completada exitosamente")
    return {
        'campana_meta': df_campana,
        'gasto_diario_meta': df_gasto_diario
    }
    
    except Exception as e:
        print(f"\nError al cargar los datos: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

# ======== FUNCIONES PARA GRÁFICOS ========
def crear_grafico_rendimiento_adsets(df_campana):
    """Crea un gráfico que compara el rendimiento de los diferentes conjuntos de anuncios."""
    
    if df_campana.empty:
        # Devolver un gráfico vacío si no hay datos
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Agrupar por conjunto de anuncios
    metrics_by_adset = df_campana.groupby('Nombre del conjunto de anuncios').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_adset['CTR (%)'] = (metrics_by_adset['Clics en el enlace'] / metrics_by_adset['Impresiones'] * 100).fillna(0)
    metrics_by_adset['CPC (CLP)'] = (metrics_by_adset['Importe gastado (CLP)'] / metrics_by_adset['Clics en el enlace']).fillna(0)
    
    # Ordenar por gasto total y tomar los top 10
    metrics_by_adset = metrics_by_adset.sort_values('Importe gastado (CLP)', ascending=False).head(10)
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el gasto
    fig.add_trace(go.Bar(
        x=metrics_by_adset['Nombre del conjunto de anuncios'],
        y=metrics_by_adset['Importe gastado (CLP)'],
        name='Gasto Total (CLP)',
        marker_color=COLORS['expense'],
        hovertemplate='Conjunto: %{x}<br>Gasto: $%{y:,.0f}<br>'
    ))
    
    # Añadir línea para CTR
    fig.add_trace(go.Scatter(
        x=metrics_by_adset['Nombre del conjunto de anuncios'],
        y=metrics_by_adset['CTR (%)'],
        name='CTR (%)',
        mode='lines+markers',
        marker=dict(size=8, color='#FFD700'),
        line=dict(color='#FFD700', width=2),
        yaxis='y2',
        hovertemplate='Conjunto: %{x}<br>CTR: %{y:.2f}%<br>'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title='Rendimiento de Conjuntos de Anuncios',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        xaxis=dict(
            title='Conjunto de Anuncios',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text'], 'size': 10},
            title_font={'color': COLORS['text']},
            tickangle=45
        ),
        yaxis=dict(
            title='Gasto Total (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickformat='$,.0f'
        ),
        yaxis2=dict(
            title='CTR (%)',
            overlaying='y',
            side='right',
            showgrid=False,
            tickfont={'color': '#FFD700'},
            title_font={'color': '#FFD700'}
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='closest'
    )
    
    return fig

def crear_grafico_comparacion_publicos(df_campana):
    """Crea un gráfico que compara el rendimiento entre los diferentes públicos."""
    
    if df_campana.empty:
        # Devolver un gráfico vacío si no hay datos
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Agrupar por público
    metrics_by_audience = df_campana.groupby('Público').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_audience['CTR (%)'] = (metrics_by_audience['Clics en el enlace'] / metrics_by_audience['Impresiones'] * 100).fillna(0)
    metrics_by_audience['CPC (CLP)'] = (metrics_by_audience['Importe gastado (CLP)'] / metrics_by_audience['Clics en el enlace']).fillna(0)
    metrics_by_audience['Conversión (%)'] = (metrics_by_audience['Artículos agregados al carrito'] / metrics_by_audience['Clics en el enlace'] * 100).fillna(0)
    metrics_by_audience['Costo por Conversión (CLP)'] = (metrics_by_audience['Importe gastado (CLP)'] / metrics_by_audience['Artículos agregados al carrito']).fillna(0)
    
    # Crear figura con subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Gasto Total (CLP)',
            'CTR (%)',
            'CPC (CLP)',
            'Conversión (%)',
            'Costo por Conversión (CLP)',
            'Artículos agregados al carrito'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Definir colores para cada métrica
    colors = {
        'gasto': COLORS['expense'],
        'ctr': '#FFD700',
        'cpc': '#9370db',
        'conversion': '#6AB187',
        'costo_conversion': '#FF6B6B',
        'articulos': '#4CAF50'
    }
    
    # Añadir cada métrica como un subplot
    # 1. Gasto Total
    fig.add_trace(
        go.Bar(
            x=metrics_by_audience['Público'],
            y=metrics_by_audience['Importe gastado (CLP)'],
            marker_color=colors['gasto'],
            hovertemplate='Gasto: $%{y:,.0f}<br>'
        ),
        row=1, col=1
    )
    
    # 2. CTR
    fig.add_trace(
        go.Bar(
            x=metrics_by_audience['Público'],
            y=metrics_by_audience['CTR (%)'],
            marker_color=colors['ctr'],
            hovertemplate='CTR: %{y:.2f}%<br>'
        ),
        row=1, col=2
    )
    
    # 3. CPC
    fig.add_trace(
        go.Bar(
            x=metrics_by_audience['Público'],
            y=metrics_by_audience['CPC (CLP)'],
            marker_color=colors['cpc'],
            hovertemplate='CPC: $%{y:,.0f}<br>'
        ),
        row=2, col=1
    )
    
    # 4. Conversión
    fig.add_trace(
        go.Bar(
            x=metrics_by_audience['Público'],
            y=metrics_by_audience['Conversión (%)'],
            marker_color=colors['conversion'],
            hovertemplate='Conversión: %{y:.2f}%<br>'
        ),
        row=2, col=2
    )
    
    # 5. Costo por Conversión
    fig.add_trace(
        go.Bar(
            x=metrics_by_audience['Público'],
            y=metrics_by_audience['Costo por Conversión (CLP)'],
            marker_color=colors['costo_conversion'],
            hovertemplate='Costo por Conversión: $%{y:,.0f}<br>'
        ),
        row=3, col=1
    )
    
    # 6. Artículos agregados al carrito
    fig.add_trace(
        go.Bar(
            x=metrics_by_audience['Público'],
            y=metrics_by_audience['Artículos agregados al carrito'],
            marker_color=colors['articulos'],
            hovertemplate='Artículos: %{y:,.0f}<br>'
        ),
        row=3, col=2
    )
    
    # Actualizar diseño
    fig.update_layout(
        title='Comparación entre Públicos',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=1000,  # Aumentar altura para acomodar todos los subplots
        showlegend=False,
        margin=dict(t=100)
    )
    
    # Actualizar ejes
    fig.update_xaxes(
        showgrid=True,
        gridcolor=COLORS['grid'],
        tickfont={'color': COLORS['text'], 'size': 10}
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS['grid'],
        tickfont={'color': COLORS['text']},
        title_font={'color': COLORS['text']}
    )
    
    # Actualizar formato específico para cada tipo de métrica
    for i in range(1, 7):
        row = (i-1) // 2 + 1
        col = (i-1) % 2 + 1
        
        if i in [1, 3, 5]:  # Métricas monetarias
            fig.update_yaxes(tickformat='$,.0f', row=row, col=col)
        elif i in [2, 4]:  # Porcentajes
            fig.update_yaxes(tickformat='.2f', row=row, col=col)
        else:  # Valores enteros
            fig.update_yaxes(tickformat=',.0f', row=row, col=col)
    
    return fig

def crear_grafico_hook_rates(df_campana):
    """Crea un gráfico que compara los diferentes hook rates por tipo de anuncio."""
    
    if df_campana.empty:
        # Devolver un gráfico vacío si no hay datos
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Agrupar por tipo de anuncio y calcular promedios de hook rates
    metrics_by_ad = df_campana.groupby('Tipo de Anuncio').agg({
        'Hook Rate 3s (%)': 'mean',
        'Hook Rate 25% (%)': 'mean',
        'Hook Rate 50% (%)': 'mean',
        'Hook Rate 75% (%)': 'mean',
        'Hook Rate 100% (%)': 'mean',
        'Impresiones': 'sum'  # Para referencia
    }).reset_index()
    
    # Ordenar por Hook Rate 3s
    metrics_by_ad = metrics_by_ad.sort_values('Hook Rate 3s (%)', ascending=True)
    
    # Crear figura
    fig = go.Figure()
    
    # Colores para cada hook rate
    colors = {
        '3s': '#FF9999',
        '25%': '#66B2FF',
        '50%': '#99FF99',
        '75%': '#FFCC99',
        '100%': '#FF99CC'
    }
    
    # Añadir barras para cada hook rate
    fig.add_trace(go.Bar(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Hook Rate 3s (%)'],
        name='3 segundos',
        orientation='h',
        marker_color=colors['3s'],
        hovertemplate='Hook Rate 3s: %{x:.2f}%<br>'
    ))
    
    fig.add_trace(go.Bar(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Hook Rate 25% (%)'],
        name='25%',
        orientation='h',
        marker_color=colors['25%'],
        hovertemplate='Hook Rate 25%: %{x:.2f}%<br>'
    ))
    
    fig.add_trace(go.Bar(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Hook Rate 50% (%)'],
        name='50%',
        orientation='h',
        marker_color=colors['50%'],
        hovertemplate='Hook Rate 50%: %{x:.2f}%<br>'
    ))
    
    fig.add_trace(go.Bar(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Hook Rate 75% (%)'],
        name='75%',
        orientation='h',
        marker_color=colors['75%'],
        hovertemplate='Hook Rate 75%: %{x:.2f}%<br>'
    ))
    
    fig.add_trace(go.Bar(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Hook Rate 100% (%)'],
        name='100%',
        orientation='h',
        marker_color=colors['100%'],
        hovertemplate='Hook Rate 100%: %{x:.2f}%<br>'
    ))
    
    # Actualizar diseño
    fig.update_layout(
        title='Hook Rates por Tipo de Anuncio',
        barmode='group',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        xaxis=dict(
            title='Hook Rate (%)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickformat='.2f'
        ),
        yaxis=dict(
            title='Tipo de Anuncio',
            showgrid=False,
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color=COLORS['text'])
        ),
        margin=dict(l=200)  # Margen izquierdo para nombres largos
    )
    
    return fig

def crear_grafico_evolucion_diaria(df_gasto_diario, periodo):
    """Crea un gráfico que muestra la evolución diaria del gasto en Meta Ads."""
    
    if df_gasto_diario.empty:
        # Devolver un gráfico vacío si no hay datos
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Agrupar datos según el período seleccionado
    if periodo == 'D':
        df_agrupado = df_gasto_diario.copy()
        formato_fecha = '%d/%m/%Y'
        titulo = 'Evolución Diaria del Gasto en Meta Ads'
    elif periodo == 'W':
        df_agrupado = df_gasto_diario.groupby(
            df_gasto_diario['Día'].dt.to_period('W').dt.start_time
        )['Importe gastado (CLP)'].sum().reset_index()
        df_agrupado['fecha_label'] = df_agrupado['Día'].dt.strftime('Semana del %d/%m/%Y')
        formato_fecha = 'Semana del %d/%m/%Y'
        titulo = 'Evolución Semanal del Gasto en Meta Ads'
    else:  # 'M'
        df_agrupado = df_gasto_diario.groupby(
            df_gasto_diario['Día'].dt.to_period('M').dt.start_time
        )['Importe gastado (CLP)'].sum().reset_index()
        df_agrupado['fecha_label'] = df_agrupado['Día'].dt.strftime('%B %Y')
        formato_fecha = '%B %Y'
        titulo = 'Evolución Mensual del Gasto en Meta Ads'
    
    # Calcular la tendencia
    x_num = np.arange(len(df_agrupado))
    y = df_agrupado['Importe gastado (CLP)'].values
    z = np.polyfit(x_num, y, 1)
    p = np.poly1d(z)
    tendencia = p(x_num)
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el gasto
    fig.add_trace(go.Bar(
        x=df_agrupado['Día'],
        y=df_agrupado['Importe gastado (CLP)'],
        name='Gasto',
        marker_color=COLORS['expense'],
        hovertemplate='Fecha: %{x}<br>Gasto: $%{y:,.0f}<br>'
    ))
    
    # Añadir línea de tendencia
    fig.add_trace(go.Scatter(
        x=df_agrupado['Día'],
        y=tendencia,
        name='Tendencia',
        mode='lines',
        line=dict(color='#FFD700', width=2, dash='dash'),
        hovertemplate='Tendencia: $%{y:,.0f}<br>'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title=titulo,
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickangle=45 if periodo == 'D' else 0
        ),
        yaxis=dict(
            title='Gasto (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickformat='$,.0f'
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='x unified'
    )
    
    # Ajustar etiquetas si es semanal o mensual
    if periodo in ['W', 'M']:
        fig.update_xaxes(
            ticktext=df_agrupado['fecha_label'],
            tickvals=df_agrupado['Día']
        )
    
    return fig

def crear_grafico_anuncios_rendimiento(df_campana):
    """Crea un gráfico que muestra el rendimiento de los diferentes anuncios."""
    
    if df_campana.empty:
        # Devolver un gráfico vacío si no hay datos
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Agrupar por tipo de anuncio
    metrics_by_ad = df_campana.groupby('Tipo de Anuncio').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_ad['CTR (%)'] = (metrics_by_ad['Clics en el enlace'] / metrics_by_ad['Impresiones'] * 100).fillna(0)
    metrics_by_ad['CPC (CLP)'] = (metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Clics en el enlace']).fillna(0)
    metrics_by_ad['Conversión (%)'] = (metrics_by_ad['Artículos agregados al carrito'] / metrics_by_ad['Clics en el enlace'] * 100).fillna(0)
    
    # Ordenar por gasto total
    metrics_by_ad = metrics_by_ad.sort_values('Importe gastado (CLP)', ascending=False)
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras horizontales para el gasto
    fig.add_trace(go.Bar(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Importe gastado (CLP)'],
        name='Gasto',
        orientation='h',
        marker_color=COLORS['expense'],
        hovertemplate='Tipo: %{y}<br>Gasto: $%{x:,.0f}<br>'
    ))
    
    # Añadir puntos para CTR
    fig.add_trace(go.Scatter(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['CTR (%)'],
        name='CTR (%)',
        mode='markers',
        marker=dict(
            size=12,
            symbol='diamond',
            color='#FFD700'
        ),
        xaxis='x2',
        hovertemplate='Tipo: %{y}<br>CTR: %{x:.2f}%<br>'
    ))
    
    # Añadir puntos para Conversión
    fig.add_trace(go.Scatter(
        y=metrics_by_ad['Tipo de Anuncio'],
        x=metrics_by_ad['Conversión (%)'],
        name='Conversión (%)',
        mode='markers',
        marker=dict(
            size=12,
            symbol='circle',
            color='#6AB187'
        ),
        xaxis='x3',
        hovertemplate='Tipo: %{y}<br>Conversión: %{x:.2f}%<br>'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title='Rendimiento por Tipo de Anuncio',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=max(500, len(metrics_by_ad) * 60),  # Altura dinámica según cantidad de tipos
        showlegend=True,
        xaxis=dict(
            title='Gasto Total (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickformat='$,.0f',
            domain=[0, 0.5]
        ),
        xaxis2=dict(
            title='CTR (%)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': '#FFD700'},
            title_font={'color': '#FFD700'},
            overlaying='x',
            side='top',
            position=0.5,
            domain=[0.5, 0.75]
        ),
        xaxis3=dict(
            title='Conversión (%)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': '#6AB187'},
            title_font={'color': '#6AB187'},
            overlaying='x',
            side='top',
            position=0.75,
            domain=[0.75, 1]
        ),
        yaxis=dict(
            showgrid=False,
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        legend=dict(
            font=dict(color=COLORS['text']),
            x=0.5,
            y=-0.2,
            orientation='h',
            xanchor='center'
        ),
        margin=dict(t=100)  # Margen superior para los títulos de los ejes x2 y x3
    )
    
    return fig

def crear_grafico_comparacion_metricas(df_campana, metrica_seleccionada=None):
    """Crea un gráfico que compara todas las métricas principales entre los diferentes anuncios."""
    
    if df_campana.empty:
        # Devolver un gráfico vacío si no hay datos
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Agrupar por tipo de anuncio y calcular todas las métricas
    metrics_by_ad = df_campana.groupby('Tipo de Anuncio').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_ad['CTR (%)'] = (metrics_by_ad['Clics en el enlace'] / metrics_by_ad['Impresiones'] * 100).fillna(0)
    metrics_by_ad['CPC (CLP)'] = (metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Clics en el enlace']).fillna(0)
    metrics_by_ad['Conversión (%)'] = (metrics_by_ad['Artículos agregados al carrito'] / metrics_by_ad['Clics en el enlace'] * 100).fillna(0)
    metrics_by_ad['Costo por Conversión (CLP)'] = (metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Artículos agregados al carrito']).fillna(0)
    
    # Crear figura con subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Gasto Total (CLP)',
            'CTR (%)',
            'CPC (CLP)',
            'Conversión (%)',
            'Costo por Conversión (CLP)',
            'Artículos agregados al carrito'
        ),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Definir colores para cada métrica
    colors = {
        'gasto': COLORS['expense'],
        'ctr': '#FFD700',
        'cpc': '#9370db',
        'conversion': '#6AB187',
        'costo_conversion': '#FF6B6B',
        'articulos': '#4CAF50'
    }
    
    # Añadir cada métrica como un subplot
    # 1. Gasto Total
    fig.add_trace(
        go.Bar(
            x=metrics_by_ad['Tipo de Anuncio'],
            y=metrics_by_ad['Importe gastado (CLP)'],
            marker_color=colors['gasto'],
            hovertemplate='Gasto: $%{y:,.0f}<br>'
        ),
        row=1, col=1
    )
    
    # 2. CTR
    fig.add_trace(
        go.Bar(
            x=metrics_by_ad['Tipo de Anuncio'],
            y=metrics_by_ad['CTR (%)'],
            marker_color=colors['ctr'],
            hovertemplate='CTR: %{y:.2f}%<br>'
        ),
        row=1, col=2
    )
    
    # 3. CPC
    fig.add_trace(
        go.Bar(
            x=metrics_by_ad['Tipo de Anuncio'],
            y=metrics_by_ad['CPC (CLP)'],
            marker_color=colors['cpc'],
            hovertemplate='CPC: $%{y:,.0f}<br>'
        ),
        row=2, col=1
    )
    
    # 4. Conversión
    fig.add_trace(
        go.Bar(
            x=metrics_by_ad['Tipo de Anuncio'],
            y=metrics_by_ad['Conversión (%)'],
            marker_color=colors['conversion'],
            hovertemplate='Conversión: %{y:.2f}%<br>'
        ),
        row=2, col=2
    )
    
    # 5. Costo por Conversión
    fig.add_trace(
        go.Bar(
            x=metrics_by_ad['Tipo de Anuncio'],
            y=metrics_by_ad['Costo por Conversión (CLP)'],
            marker_color=colors['costo_conversion'],
            hovertemplate='Costo por Conversión: $%{y:,.0f}<br>'
        ),
        row=3, col=1
    )
    
    # 6. Artículos agregados al carrito
    fig.add_trace(
        go.Bar(
            x=metrics_by_ad['Tipo de Anuncio'],
            y=metrics_by_ad['Artículos agregados al carrito'],
            marker_color=colors['articulos'],
            hovertemplate='Artículos: %{y:,.0f}<br>'
        ),
        row=3, col=2
    )
    
    # Actualizar diseño
    fig.update_layout(
        title='Comparación de Métricas por Tipo de Anuncio',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=1000,  # Aumentar altura para acomodar todos los subplots
        showlegend=False,
        margin=dict(t=100)
    )
    
    # Actualizar ejes
    fig.update_xaxes(
        showgrid=True,
        gridcolor=COLORS['grid'],
        tickfont={'color': COLORS['text'], 'size': 10},
        tickangle=45
    )
    
    fig.update_yaxes(
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
    )
    
    # Actualizar formato específico para cada tipo de métrica
    for i in range(1, 7):
        row = (i-1) // 2 + 1
        col = (i-1) % 2 + 1
        
        if i in [1, 3, 5]:  # Métricas monetarias
            fig.update_yaxes(tickformat='$,.0f', row=row, col=col)
        elif i in [2, 4]:  # Porcentajes
            fig.update_yaxes(tickformat='.2f', row=row, col=col)
        else:  # Valores enteros
            fig.update_yaxes(tickformat=',.0f', row=row, col=col)
    
    return fig

# ======== FUNCIONES PARA GENERAR INSIGHTS ========
def generar_insights_evolucion_gasto(df_gasto_diario):
    """Genera insights sobre la evolución del gasto."""
    
    if df_gasto_diario.empty:
        return "No hay datos disponibles para el período seleccionado."
    
    # Calcular métricas clave
    gasto_total = df_gasto_diario['Importe gastado (CLP)'].sum()
    gasto_promedio = df_gasto_diario['Importe gastado (CLP)'].mean()
    dias_totales = len(df_gasto_diario)
    
    # Calcular tendencia
    x = np.arange(len(df_gasto_diario))
    y = df_gasto_diario['Importe gastado (CLP)'].values
    z = np.polyfit(x, y, 1)
    tendencia = z[0]  # Pendiente de la línea de tendencia
    
    # Identificar días con mayor y menor gasto
    dia_max_gasto = df_gasto_diario.loc[df_gasto_diario['Importe gastado (CLP)'].idxmax()]
    dia_min_gasto = df_gasto_diario.loc[df_gasto_diario['Importe gastado (CLP)'].idxmin()]
    
    # Generar insights
    insights = []
    
    # Insight sobre gasto total y promedio
    insights.append(f"• El gasto total en el período fue de ${gasto_total:,.0f} CLP, con un promedio diario de ${gasto_promedio:,.0f} CLP.")
    
    # Insight sobre tendencia
    if tendencia > 0:
        insights.append("• La tendencia del gasto es creciente, lo que indica un aumento progresivo en la inversión publicitaria.")
    elif tendencia < 0:
        insights.append("• La tendencia del gasto es decreciente, lo que sugiere una reducción progresiva en la inversión publicitaria.")
    else:
        insights.append("• El gasto se ha mantenido relativamente estable durante el período.")
    
    # Insight sobre días destacados
    insights.append(f"• El día con mayor gasto fue el {dia_max_gasto['Día'].strftime('%d/%m/%Y')}, con ${dia_max_gasto['Importe gastado (CLP)']:,.0f} CLP.")
    insights.append(f"• El día con menor gasto fue el {dia_min_gasto['Día'].strftime('%d/%m/%Y')}, con ${dia_min_gasto['Importe gastado (CLP)']:,.0f} CLP.")
    
    return html.Div([html.P(insight) for insight in insights])

def generar_insights_adsets(df_campana):
    """Genera insights sobre el rendimiento de los conjuntos de anuncios."""
    
    if df_campana.empty:
        return "No hay datos disponibles para el período seleccionado."
    
    # Agrupar por conjunto de anuncios
    metrics_by_adset = df_campana.groupby('Nombre del conjunto de anuncios').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_adset['CTR (%)'] = (metrics_by_adset['Clics en el enlace'] / metrics_by_adset['Impresiones'] * 100).fillna(0)
    metrics_by_adset['CPC (CLP)'] = (metrics_by_adset['Importe gastado (CLP)'] / metrics_by_adset['Clics en el enlace']).fillna(0)
    metrics_by_adset['Conversión (%)'] = (metrics_by_adset['Artículos agregados al carrito'] / metrics_by_adset['Clics en el enlace'] * 100).fillna(0)
    
    # Identificar mejores y peores conjuntos
    mejor_ctr = metrics_by_adset.nlargest(1, 'CTR (%)').iloc[0]
    mejor_conversion = metrics_by_adset.nlargest(1, 'Conversión (%)').iloc[0]
    menor_cpc = metrics_by_adset.nsmallest(1, 'CPC (CLP)').iloc[0]
    mayor_gasto = metrics_by_adset.nlargest(1, 'Importe gastado (CLP)').iloc[0]
    
    # Generar insights
    insights = []
    
    # Insight sobre conjunto con mayor gasto
    insights.append(f"• El conjunto '{mayor_gasto['Nombre del conjunto de anuncios']}' tuvo el mayor gasto (${mayor_gasto['Importe gastado (CLP)']:,.0f} CLP) con un CTR de {mayor_gasto['CTR (%)']:.2f}% y una tasa de conversión de {mayor_gasto['Conversión (%)']:.2f}%.")
    
    # Insight sobre mejor CTR
    insights.append(f"• El mejor CTR fue de {mejor_ctr['CTR (%)']:.2f}% logrado por '{mejor_ctr['Nombre del conjunto de anuncios']}'.")
    
    # Insight sobre mejor conversión
    insights.append(f"• La mejor tasa de conversión fue de {mejor_conversion['Conversión (%)']:.2f}% alcanzada por '{mejor_conversion['Nombre del conjunto de anuncios']}'.")
    
    # Insight sobre CPC más eficiente
    insights.append(f"• El CPC más eficiente fue de ${menor_cpc['CPC (CLP)']:,.0f} CLP logrado por '{menor_cpc['Nombre del conjunto de anuncios']}'.")
    
    return html.Div([html.P(insight) for insight in insights])

def generar_insights_publicos(df_campana):
    """Genera insights sobre el rendimiento de los diferentes públicos."""
    
    if df_campana.empty:
        return "No hay datos disponibles para el período seleccionado."
    
    # Agrupar por público
    metrics_by_audience = df_campana.groupby('Público').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_audience['CTR (%)'] = (metrics_by_audience['Clics en el enlace'] / metrics_by_audience['Impresiones'] * 100).fillna(0)
    metrics_by_audience['CPC (CLP)'] = (metrics_by_audience['Importe gastado (CLP)'] / metrics_by_audience['Clics en el enlace']).fillna(0)
    metrics_by_audience['Conversión (%)'] = (metrics_by_audience['Artículos agregados al carrito'] / metrics_by_audience['Clics en el enlace'] * 100).fillna(0)
    
    # Generar insights
    insights = []
    
    for _, publico in metrics_by_audience.iterrows():
        nombre_publico = publico['Público']
        gasto = publico['Importe gastado (CLP)']
        ctr = publico['CTR (%)']
        conversion = publico['Conversión (%)']
        cpc = publico['CPC (CLP)']
        
        insights.append(f"• Público {nombre_publico}:")
        insights.append(f"  - Gasto total: ${gasto:,.0f} CLP")
        insights.append(f"  - CTR: {ctr:.2f}%")
        insights.append(f"  - Tasa de conversión: {conversion:.2f}%")
        insights.append(f"  - CPC: ${cpc:,.0f} CLP")
        insights.append("")
    
    # Identificar el público más efectivo
    mejor_ctr = metrics_by_audience.loc[metrics_by_audience['CTR (%)'].idxmax()]
    mejor_conversion = metrics_by_audience.loc[metrics_by_audience['Conversión (%)'].idxmax()]
    
    insights.append(f"• El público con mejor CTR fue {mejor_ctr['Público']} ({mejor_ctr['CTR (%)']:.2f}%).")
    insights.append(f"• El público con mejor tasa de conversión fue {mejor_conversion['Público']} ({mejor_conversion['Conversión (%)']:.2f}%).")
    
    return html.Div([html.P(insight) for insight in insights])

def generar_insights_anuncios(df_campana):
    """Genera insights sobre el rendimiento de los diferentes tipos de anuncios."""
    
    if df_campana.empty:
        return "No hay datos disponibles para el período seleccionado."
    
    # Agrupar por tipo de anuncio
    metrics_by_ad = df_campana.groupby('Tipo de Anuncio').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_ad['CTR (%)'] = (metrics_by_ad['Clics en el enlace'] / metrics_by_ad['Impresiones'] * 100).fillna(0)
    metrics_by_ad['CPC (CLP)'] = (metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Clics en el enlace']).fillna(0)
    metrics_by_ad['Conversión (%)'] = (metrics_by_ad['Artículos agregados al carrito'] / metrics_by_ad['Clics en el enlace'] * 100).fillna(0)
    
    # Ordenar por gasto total
    metrics_by_ad = metrics_by_ad.sort_values('Importe gastado (CLP)', ascending=False)
    
    # Generar insights
    insights = []
    
    # Insight sobre el tipo de anuncio más efectivo
    mejor_ctr = metrics_by_ad.loc[metrics_by_ad['CTR (%)'].idxmax()]
    mejor_conversion = metrics_by_ad.loc[metrics_by_ad['Conversión (%)'].idxmax()]
    menor_cpc = metrics_by_ad.loc[metrics_by_ad['CPC (CLP)'].idxmin()]
    
    insights.append("Rendimiento por tipo de anuncio:")
    
    for _, tipo in metrics_by_ad.iterrows():
        insights.append(f"\n• {tipo['Tipo de Anuncio']}:")
        insights.append(f"  - Gasto: ${tipo['Importe gastado (CLP)']:,.0f} CLP")
        insights.append(f"  - CTR: {tipo['CTR (%)']:.2f}%")
        insights.append(f"  - Conversión: {tipo['Conversión (%)']:.2f}%")
        insights.append(f"  - CPC: ${tipo['CPC (CLP)']:,.0f} CLP")
    
    insights.append("\nDestacados:")
    insights.append(f"• El tipo de anuncio con mejor CTR fue '{mejor_ctr['Tipo de Anuncio']}' con {mejor_ctr['CTR (%)']:.2f}%")
    insights.append(f"• El tipo de anuncio con mejor conversión fue '{mejor_conversion['Tipo de Anuncio']}' con {mejor_conversion['Conversión (%)']:.2f}%")
    insights.append(f"• El tipo de anuncio con menor CPC fue '{menor_cpc['Tipo de Anuncio']}' con ${menor_cpc['CPC (CLP)']:,.0f} CLP")
    
    return html.Div([html.P(insight) for insight in insights])

def generar_insights_hook_rates(df_campana):
    """Genera insights sobre los hook rates de los diferentes tipos de anuncios."""
    
    if df_campana.empty:
        return "No hay datos disponibles para el período seleccionado."
    
    # Agrupar por tipo de anuncio
    metrics_by_ad = df_campana.groupby('Tipo de Anuncio').agg({
        'Hook Rate 3s (%)': 'mean',
        'Hook Rate 25% (%)': 'mean',
        'Hook Rate 50% (%)': 'mean',
        'Hook Rate 75% (%)': 'mean',
        'Hook Rate 100% (%)': 'mean',
        'Impresiones': 'sum'
    }).reset_index()
    
    # Generar insights
    insights = []
    
    # Encontrar el mejor anuncio para cada hook rate
    for rate in ['3s', '25%', '50%', '75%', '100%']:
        col = f'Hook Rate {rate} (%)'
        mejor = metrics_by_ad.loc[metrics_by_ad[col].idxmax()]
        insights.append(f"• El mejor Hook Rate {rate} fue de {mejor[col]:.2f}% logrado por '{mejor['Tipo de Anuncio']}'")
    
    # Análisis de retención
    for _, anuncio in metrics_by_ad.iterrows():
        tipo = anuncio['Tipo de Anuncio']
        retencion_25 = (anuncio['Hook Rate 25% (%)'] / anuncio['Hook Rate 3s (%)'] * 100) if anuncio['Hook Rate 3s (%)'] > 0 else 0
        retencion_100 = (anuncio['Hook Rate 100% (%)'] / anuncio['Hook Rate 3s (%)'] * 100) if anuncio['Hook Rate 3s (%)'] > 0 else 0
        
        insights.append(f"\n• {tipo}:")
        insights.append(f"  - Retención al 25%: {retencion_25:.1f}% de los espectadores que vieron 3s")
        insights.append(f"  - Retención al 100%: {retencion_100:.1f}% de los espectadores que vieron 3s")
    
    return html.Div([html.P(insight) for insight in insights])

def crear_grafico_distribucion_regional(df_campana, metrica_seleccionada):
    """Crea un mapa de calor que muestra la distribución de la métrica seleccionada por región."""
    
    if df_campana.empty:
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para el período seleccionado',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500
        )
        return fig
    
    # Definir las métricas disponibles y sus formatos
    metricas = {
        'gasto': {'nombre': 'Importe gastado (CLP)', 'formato': '${:,.0f}', 'titulo': 'Gasto por Región'},
        'impresiones': {'nombre': 'Impresiones', 'formato': '{:,.0f}', 'titulo': 'Impresiones por Región'},
        'clics': {'nombre': 'Clics en el enlace', 'formato': '{:,.0f}', 'titulo': 'Clics por Región'},
        'ctr': {'nombre': 'CTR (%)', 'formato': '{:.2f}%', 'titulo': 'CTR por Región'},
        'cpc': {'nombre': 'CPC (todos)', 'formato': '${:,.0f}', 'titulo': 'CPC por Región'},
        'conversiones': {'nombre': 'Artículos agregados al carrito', 'formato': '{:,.0f}', 'titulo': 'Conversiones por Región'},
        'hook_rate_3s': {'nombre': 'Hook Rate 3s (%)', 'formato': '{:.2f}%', 'titulo': 'Hook Rate 3s por Región'}
    }
    
    # Obtener la métrica seleccionada
    metrica = metricas[metrica_seleccionada]
    
    # Agrupar por región
    if metrica_seleccionada == 'ctr':
        # Para CTR, necesitamos calcular clics/impresiones
        df_region = df_campana.groupby('Región').agg({
            'Clics en el enlace': 'sum',
            'Impresiones': 'sum'
        }).reset_index()
        df_region['CTR (%)'] = (df_region['Clics en el enlace'] / df_region['Impresiones'] * 100).fillna(0)
        valores = df_region['CTR (%)']
    elif metrica_seleccionada == 'cpc':
        # Para CPC, necesitamos calcular gasto/clics
        df_region = df_campana.groupby('Región').agg({
            'Importe gastado (CLP)': 'sum',
            'Clics en el enlace': 'sum'
        }).reset_index()
        df_region['CPC (todos)'] = (df_region['Importe gastado (CLP)'] / df_region['Clics en el enlace']).fillna(0)
        valores = df_region['CPC (todos)']
    elif metrica_seleccionada == 'hook_rate_3s':
        # Para Hook Rate, necesitamos calcular reproducciones/impresiones
        df_region = df_campana.groupby('Región').agg({
            'Reproducciones de video de 3 segundos': 'sum',
            'Impresiones': 'sum'
        }).reset_index()
        df_region['Hook Rate 3s (%)'] = (df_region['Reproducciones de video de 3 segundos'] / df_region['Impresiones'] * 100).fillna(0)
        valores = df_region['Hook Rate 3s (%)']
    else:
        # Para métricas simples, solo sumamos
        df_region = df_campana.groupby('Región')[metrica['nombre']].sum().reset_index()
        valores = df_region[metrica['nombre']]
    
    # Crear figura
    fig = go.Figure(data=go.Bar(
        x=df_region['Región'],
        y=valores,
        marker_color=valores,
        marker=dict(
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title=metrica['titulo'],
                tickfont=dict(color=COLORS['text']),
                title_font=dict(color=COLORS['text'])  # Cambiado de titlefont a title_font
            )
        ),
        text=[metrica['formato'].format(val) for val in valores],
        textposition='auto',
    ))
    
    # Actualizar diseño
    fig.update_layout(
        title=metrica['titulo'],
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        xaxis=dict(
            title='Región',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickangle=45
        ),
        yaxis=dict(
            title=metrica['titulo'],
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']},
            tickformat=metrica['formato'].replace('{:,', '').replace('{:.2', '').replace('f}', '').replace('%}', '%')
        )
    )
    
    return fig

def generar_insights_regionales(df_campana, metrica_seleccionada):
    """Genera insights sobre la distribución regional de la métrica seleccionada."""
    
    if df_campana.empty:
        return "No hay datos disponibles para el período seleccionado."
    
    # Definir las métricas y sus descripciones
    metricas = {
        'gasto': {'nombre': 'Importe gastado (CLP)', 'formato': '${:,.0f}', 'desc': 'gasto'},
        'impresiones': {'nombre': 'Impresiones', 'formato': '{:,.0f}', 'desc': 'impresiones'},
        'clics': {'nombre': 'Clics en el enlace', 'formato': '{:,.0f}', 'desc': 'clics'},
        'ctr': {'nombre': 'CTR (%)', 'formato': '{:.2f}%', 'desc': 'CTR'},
        'cpc': {'nombre': 'CPC (todos)', 'formato': '${:,.0f}', 'desc': 'CPC'},
        'conversiones': {'nombre': 'Artículos agregados al carrito', 'formato': '{:,.0f}', 'desc': 'conversiones'},
        'hook_rate_3s': {'nombre': 'Hook Rate 3s (%)', 'formato': '{:.2f}%', 'desc': 'Hook Rate 3s'}
    }
    
    metrica = metricas[metrica_seleccionada]
    insights = []
    
    # Calcular métricas por región
    if metrica_seleccionada == 'ctr':
        df_region = df_campana.groupby('Región').agg({
            'Clics en el enlace': 'sum',
            'Impresiones': 'sum'
        }).reset_index()
        df_region['valor'] = (df_region['Clics en el enlace'] / df_region['Impresiones'] * 100).fillna(0)
    elif metrica_seleccionada == 'cpc':
        df_region = df_campana.groupby('Región').agg({
            'Importe gastado (CLP)': 'sum',
            'Clics en el enlace': 'sum'
        }).reset_index()
        df_region['valor'] = (df_region['Importe gastado (CLP)'] / df_region['Clics en el enlace']).fillna(0)
    elif metrica_seleccionada == 'hook_rate_3s':
        df_region = df_campana.groupby('Región').agg({
            'Reproducciones de video de 3 segundos': 'sum',
            'Impresiones': 'sum'
        }).reset_index()
        df_region['valor'] = (df_region['Reproducciones de video de 3 segundos'] / df_region['Impresiones'] * 100).fillna(0)
    else:
        df_region = df_campana.groupby('Región')[metrica['nombre']].sum().reset_index()
        df_region['valor'] = df_region[metrica['nombre']]
    
    # Encontrar región con mayor y menor valor
    mejor_region = df_region.loc[df_region['valor'].idxmax()]
    peor_region = df_region.loc[df_region['valor'].idxmin()]
    
    # Calcular promedio y total
    promedio = df_region['valor'].mean()
    total = df_region['valor'].sum()
    
    # Generar insights
    insights.append(f"• La región con mayor {metrica['desc']} es {mejor_region['Región']} con {metrica['formato'].format(mejor_region['valor'])}")
    insights.append(f"• La región con menor {metrica['desc']} es {peor_region['Región']} con {metrica['formato'].format(peor_region['valor'])}")
    
    if metrica_seleccionada in ['gasto', 'impresiones', 'clics', 'conversiones']:
        insights.append(f"• El total de {metrica['desc']} es {metrica['formato'].format(total)}")
    
    insights.append(f"• El promedio por región es {metrica['formato'].format(promedio)}")
    
    # Análisis de distribución
    df_region['porcentaje'] = (df_region['valor'] / total * 100) if total > 0 else 0
    regiones_principales = df_region.nlargest(3, 'valor')
    
    insights.append("\nDistribución en las principales regiones:")
    for _, region in regiones_principales.iterrows():
        insights.append(f"• {region['Región']}: {metrica['formato'].format(region['valor'])} ({region['porcentaje']:.1f}% del total)")
    
    return html.Div([html.P(insight) for insight in insights])

# ======== CREACIÓN DE LA APLICACIÓN ========
def crear_app_marketing():
    """Crea la aplicación Dash para la página de marketing."""
    try:
        print("\nCreando aplicación Dash...")
    datos = cargar_datos_marketing()
        if datos is None:
            print("Error: No se pudieron cargar los datos")
            return None
        
    df_campana = datos['campana_meta']
    df_gasto_diario = datos['gasto_diario_meta']
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    # Obtener fechas mínima y máxima
    fecha_min = df_campana['Día'].min()
    fecha_max = df_campana['Día'].max()
    
        # Definir las métricas disponibles para el análisis regional
        METRICAS_REGIONALES = [
            {'label': 'Gasto', 'value': 'gasto'},
            {'label': 'Impresiones', 'value': 'impresiones'},
            {'label': 'Clics', 'value': 'clics'},
            {'label': 'CTR', 'value': 'ctr'},
            {'label': 'CPC', 'value': 'cpc'},
            {'label': 'Conversiones', 'value': 'conversiones'}
        ]
    
    app.layout = html.Div([
        crear_header(),
        html.Div([
            html.Div("DASHBOARD DE MARKETING - META ADS", style={
                'color': COLORS['primary'], 
                'fontSize': '24px', 
                'fontWeight': 'bold',
                'padding': '10px',
                'marginBottom': '20px',
                'textAlign': 'center',
                'backgroundColor': COLORS['card_bg'],
                'borderRadius': '5px'
            })
        ]),
        crear_filtros(fecha_min, fecha_max),
        html.Div([
            html.Div([
                html.H3('Gasto Total Meta', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-gasto-meta', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Impresiones', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-impresiones', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Clics', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-clics', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('CTR Promedio', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='ctr-promedio', style={'color': '#FFD700', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('CPC Promedio', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='cpc-promedio', style={'color': '#FFD700', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Artículos al Carrito', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='articulos-carrito', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
        crear_selector_periodo(),
        crear_contenedor_grafico('evolucion-gasto-meta', 'Evolución del Gasto en Meta Ads'),
        crear_contenedor_insights('insights-evolucion', 'Conclusiones: Evolución del Gasto'),
            crear_contenedor_grafico('comparacion-metricas', 'Comparación de Métricas por Tipo de Anuncio'),
            crear_contenedor_insights('insights-metricas', 'Conclusiones: Comparación de Métricas'),
            crear_contenedor_grafico('comparacion-publicos', 'Comparación entre Públicos'),
            crear_contenedor_insights('insights-publicos', 'Conclusiones: Análisis de Públicos'),
            crear_contenedor_grafico('hook-rates', 'Hook Rates por Tipo de Anuncio'),
            crear_contenedor_insights('insights-hook-rates', 'Conclusiones: Hook Rates'),
        html.Div([
                html.H3('Análisis Regional', style={'color': COLORS['text'], 'marginBottom': '10px'}),
            dcc.Dropdown(
                    id='selector-metrica-regional',
                    options=METRICAS_REGIONALES,
                    value='gasto',
                style={
                    'backgroundColor': COLORS['card_bg'],
                        'color': '#000000',
                        'border': f'1px solid {COLORS["grid"]}',
                        'width': '300px'
                }
            )
        ], style={
                'backgroundColor': COLORS['card_bg'],
            'padding': '15px',
                'marginBottom': '20px',
                'borderRadius': '5px'
            }),
            crear_contenedor_grafico('distribucion-regional', 'Distribución Regional'),
            crear_contenedor_insights('insights-regional', 'Conclusiones: Análisis Regional')
    ], style={
        'padding': 20,
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })
    
        def actualizar_graficos_marketing(periodo, start_date, end_date, metrica_regional):
            try:
                print(f"Actualizando gráficos con periodo={periodo}, start_date={start_date}, end_date={end_date}, metrica={metrica_regional}")
                
                # Convertir fechas una sola vez
                start_date = pd.to_datetime(start_date)
                end_date = pd.to_datetime(end_date)
                
                print("Aplicando filtros de fecha...")
                # Usar máscaras booleanas para filtrado eficiente
                mask_campana = (df_campana['Día'] >= start_date) & (df_campana['Día'] <= end_date)
                mask_gasto = (df_gasto_diario['Día'] >= start_date) & (df_gasto_diario['Día'] <= end_date)
                
                df_filtrado = df_campana[mask_campana]
                df_gasto_filtrado = df_gasto_diario[mask_gasto]
                
                print("Calculando métricas totales...")
                # Calcular métricas totales de una vez
                metricas = df_filtrado.agg({
                    'Importe gastado (CLP)': 'sum',
                    'Impresiones': 'sum',
                    'Clics en el enlace': 'sum',
                    'Artículos agregados al carrito': 'sum'
                })
                
                total_gasto = metricas['Importe gastado (CLP)']
                total_impresiones = metricas['Impresiones']
                total_clics = metricas['Clics en el enlace']
                total_carrito = metricas['Artículos agregados al carrito']
                
        ctr_promedio = (total_clics / total_impresiones * 100) if total_impresiones > 0 else 0
        cpc_promedio = (total_gasto / total_clics) if total_clics > 0 else 0
        
                print("Creando gráficos...")
        # Crear gráficos
                try:
        fig_evolucion = crear_grafico_evolucion_diaria(df_gasto_filtrado, periodo)
                    print("Gráfico evolución creado")
                except Exception as e:
                    print(f"Error en gráfico evolución: {str(e)}")
                    fig_evolucion = go.Figure()
                    
                try:
                    fig_metricas = crear_grafico_comparacion_metricas(df_filtrado)
                    print("Gráfico métricas creado")
                except Exception as e:
                    print(f"Error en gráfico métricas: {str(e)}")
                    fig_metricas = go.Figure()
                    
                try:
        fig_publicos = crear_grafico_comparacion_publicos(df_filtrado)
                    print("Gráfico públicos creado")
                except Exception as e:
                    print(f"Error en gráfico públicos: {str(e)}")
                    fig_publicos = go.Figure()
                    
                try:
                    fig_hook_rates = crear_grafico_hook_rates(df_filtrado)
                    print("Gráfico hook rates creado")
                except Exception as e:
                    print(f"Error en gráfico hook rates: {str(e)}")
                    fig_hook_rates = go.Figure()
                    
                try:
                    fig_regional = crear_grafico_distribucion_regional(df_filtrado, metrica_regional)
                    print("Gráfico regional creado")
                except Exception as e:
                    print(f"Error en gráfico regional: {str(e)}")
                    fig_regional = go.Figure()
                
                print("Generando insights...")
        # Generar insights
                try:
        insights_evolucion = generar_insights_evolucion_gasto(df_gasto_filtrado)
                except Exception as e:
                    print(f"Error en insights evolución: {str(e)}")
                    insights_evolucion = "Error al generar insights de evolución"
                    
                try:
                    insights_metricas = generar_insights_anuncios(df_filtrado)
                except Exception as e:
                    print(f"Error en insights métricas: {str(e)}")
                    insights_metricas = "Error al generar insights de métricas"
                    
                try:
        insights_publicos = generar_insights_publicos(df_filtrado)
                except Exception as e:
                    print(f"Error en insights públicos: {str(e)}")
                    insights_publicos = "Error al generar insights de públicos"
                    
                try:
                    insights_hook_rates = generar_insights_hook_rates(df_filtrado)
                except Exception as e:
                    print(f"Error en insights hook rates: {str(e)}")
                    insights_hook_rates = "Error al generar insights de hook rates"
                    
                try:
                    insights_regional = generar_insights_regionales(df_filtrado, metrica_regional)
                except Exception as e:
                    print(f"Error en insights regionales: {str(e)}")
                    insights_regional = "Error al generar insights regionales"
                
                print("Retornando resultados...")
        return (
            fig_evolucion,
            fig_metricas,
            fig_publicos,
                    fig_hook_rates,
                    fig_regional,
            f'${total_gasto:,.0f}',
            f'{total_impresiones:,.0f}',
            f'{total_clics:,.0f}',
            f'{ctr_promedio:.2f}%',
            f'${cpc_promedio:,.0f}',
            f'{total_carrito:,.0f}',
            insights_evolucion,
            insights_metricas,
            insights_publicos,
                    insights_hook_rates,
                    insights_regional
                )
            except Exception as e:
                print(f"Error en el callback principal: {str(e)}")
                import traceback
                print(traceback.format_exc())
                # Retornar valores por defecto en caso de error
                empty_fig = go.Figure()
                return [empty_fig] * 5 + ['Error'] * 11
        
        app.callback(
            [Output('evolucion-gasto-meta', 'figure'),
             Output('comparacion-metricas', 'figure'),
             Output('comparacion-publicos', 'figure'),
             Output('hook-rates', 'figure'),
             Output('distribucion-regional', 'figure'),
             Output('total-gasto-meta', 'children'),
             Output('total-impresiones', 'children'),
             Output('total-clics', 'children'),
             Output('ctr-promedio', 'children'),
             Output('cpc-promedio', 'children'),
             Output('articulos-carrito', 'children'),
             Output('insights-evolucion', 'children'),
             Output('insights-metricas', 'children'),
             Output('insights-publicos', 'children'),
             Output('insights-hook-rates', 'children'),
             Output('insights-regional', 'children')],
            [Input('periodo-selector', 'value'),
             Input('date-range-picker', 'start_date'),
             Input('date-range-picker', 'end_date'),
             Input('selector-metrica-regional', 'value')]
        )(actualizar_graficos_marketing)
    
    return app
        
    except Exception as e:
        print(f"Error al crear la aplicación: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

# ======== EJECUCIÓN DE LA APLICACIÓN ========
if __name__ == '__main__':
    try:
    print("\n=== DASHBOARD DE MARKETING - META ADS ===")
        print("Iniciando la aplicación...")
        
        # Verificar directorios necesarios
        required_dirs = [
            "archivos_input/archivos input marketing",
            "archivos_output/graficos"
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Creado directorio: {directory}")
            else:
                print(f"Directorio existente: {directory}")

        # Verificar archivo de datos
        data_file = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv"
        if not os.path.exists(data_file):
            print(f"ERROR: No se encuentra el archivo de datos en: {data_file}")
            exit(1)
        else:
            print(f"Archivo de datos encontrado: {data_file}")

        print("\nCreando la aplicación Dash...")
        app = crear_app_marketing()
        
        if app is not None:
            print("\nAplicación creada exitosamente")
            print("Dashboard disponible en:")
            print("- http://localhost:8052")
            print("- http://127.0.0.1:8052")
            print("\nIniciando el servidor...")
            app.run(debug=False, port=8052)
        else:
            print("ERROR: No se pudo crear la aplicación.")
            exit(1)
            
    except Exception as e:
        print(f"\nError fatal al ejecutar la aplicación: {str(e)}")
        import traceback
        print("\nDetalles del error:")
        print(traceback.format_exc())
        exit(1)