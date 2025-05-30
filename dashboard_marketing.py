import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import numpy as np

# Importar colores y estilos comunes
from funciones.graficos_dashboard import COLORS
from funciones.componentes_dashboard import (
    crear_header,
    crear_filtros,
    crear_selector_periodo,
    crear_tarjetas_metricas,
    crear_contenedor_grafico,
    CARD_STYLE
)

# Función para crear un contenedor de texto con insights
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

# Función para cargar datos de marketing
def cargar_datos_marketing():
    """Carga los archivos CSV de marketing para el análisis."""
    
    # Crear directorio para gráficos si no existe
    if not os.path.exists("archivos_output/graficos"):
        os.makedirs("archivos_output/graficos")
    
    # Cargar datos de campaña de Meta
    df_campana = pd.read_csv("archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios.csv")
    
    # Cargar datos de gasto diario en Meta
    df_gasto_diario = pd.read_csv("archivos_input/archivos input marketing/gasto diario en meta.csv")
    df_gasto_diario["Día"] = pd.to_datetime(df_gasto_diario["Día"])
    
    # Convertir columnas numéricas en df_campana (limpiando formato de moneda)
    columnas_numericas = [
        "Alcance", "Impresiones", "Frecuencia", "Importe gastado (CLP)", 
        "Clics en el enlace", "CTR (todos)", "CPC (todos)", 
        "CPM (costo por mil impresiones)", "Artículos agregados al carrito",
        "Costo por artículo agregado al carrito"
    ]
    for col in columnas_numericas:
        if col in df_campana.columns:
            # Convertir a string primero para manejar posibles NaN
            df_campana[col] = df_campana[col].astype(str).str.replace(',', '.')
            # Convertir a float
            df_campana[col] = pd.to_numeric(df_campana[col], errors='coerce')
    
    # Añadir columnas útiles para análisis
    df_campana['CTR (%)'] = df_campana['CTR (todos)'] * 100  # Convertir a porcentaje
    
    # Identificar categoría de público (advantage vs pucon)
    df_campana['Público'] = df_campana['Nombre del conjunto de anuncios'].apply(
        lambda x: 'Advantage' if 'advantage' in x.lower() else 
                  'Pucón' if 'pucon' in x.lower() else 'Otro'
    )
    
    # Clasificar tipo de anuncio
    df_campana['Tipo de Anuncio'] = df_campana['Nombre del anuncio'].apply(
        lambda x: 'Video explicativo' if 'explicando servicio' in x.lower() else
                  'Video inicial' if 'inicial' in x.lower() else
                  'Video publicitario' if 'publicitario' in x.lower() else
                  'Video Flo' if 'flo' in x.lower() else
                  'Día de la madre' if 'madre' in x.lower() or 'dia madre' in x.lower() else
                  'Parejas' if 'parejas' in x.lower() else
                  'Video Karin' if 'karin' in x.lower() else
                  'Video Lluvia' if 'lluvia' in x.lower() else
                  'Otro'
    )
    
    # Convertir fechas de inicio y fin
    df_campana['Inicio del informe'] = pd.to_datetime(df_campana['Inicio del informe'])
    df_campana['Fin del informe'] = pd.to_datetime(df_campana['Fin del informe'])
    
    return {
        'campana_meta': df_campana,
        'gasto_diario_meta': df_gasto_diario
    }

# ======== FUNCIONES PARA GRÁFICOS ========
def crear_grafico_rendimiento_adsets(df_campana):
    """Crea un gráfico que compara el rendimiento de los diferentes conjuntos de anuncios."""
    
    # Agrupar por conjunto de anuncios
    metrics_by_adset = df_campana.groupby('Nombre del conjunto de anuncios').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Alcance': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionales
    metrics_by_adset['CTR (%)'] = (metrics_by_adset['Clics en el enlace'] / metrics_by_adset['Impresiones']) * 100
    metrics_by_adset['CPC (CLP)'] = metrics_by_adset['Importe gastado (CLP)'] / metrics_by_adset['Clics en el enlace']
    metrics_by_adset['CPM (CLP)'] = (metrics_by_adset['Importe gastado (CLP)'] / metrics_by_adset['Impresiones']) * 1000
    metrics_by_adset['Frecuencia'] = metrics_by_adset['Impresiones'] / metrics_by_adset['Alcance']
    
    # Ordenar por gasto total
    metrics_by_adset = metrics_by_adset.sort_values('Importe gastado (CLP)', ascending=False)
    
    # Tomar los 10 conjuntos de anuncios con mayor gasto
    top_adsets = metrics_by_adset.head(10)
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para el gasto
    fig.add_trace(go.Bar(
        x=top_adsets['Nombre del conjunto de anuncios'],
        y=top_adsets['Importe gastado (CLP)'],
        name='Gasto Total (CLP)',
        marker_color=COLORS['expense'],
        hovertemplate='Conjunto: %{x}<br>Gasto: $%{y:,.0f}<br>'
    ))
    
    # Añadir línea para CTR
    fig.add_trace(go.Scatter(
        x=top_adsets['Nombre del conjunto de anuncios'],
        y=top_adsets['CTR (%)'],
        name='CTR (%)',
        mode='lines+markers',
        marker=dict(size=8, color='#FFD700'),
        line=dict(color='#FFD700', width=2),
        yaxis='y2',
        hovertemplate='Conjunto: %{x}<br>CTR: %{y:.2f}%<br>'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title='Rendimiento de Conjuntos de Anuncios por Gasto y CTR',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        barmode='group',
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
            title_font={'color': COLORS['text']}
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
    """Crea un gráfico que compara el rendimiento entre los públicos Advantage y Pucón."""
    
    # Agrupar por tipo de público
    metrics_by_audience = df_campana.groupby('Público').agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum',
        'Alcance': 'sum'
    }).reset_index()
    
    # Calcular métricas
    metrics_by_audience['CTR (%)'] = (metrics_by_audience['Clics en el enlace'] / metrics_by_audience['Impresiones']) * 100
    metrics_by_audience['CPC (CLP)'] = metrics_by_audience['Importe gastado (CLP)'] / metrics_by_audience['Clics en el enlace']
    metrics_by_audience['CPM (CLP)'] = (metrics_by_audience['Importe gastado (CLP)'] / metrics_by_audience['Impresiones']) * 1000
    metrics_by_audience['Conversión (%)'] = (metrics_by_audience['Artículos agregados al carrito'] / metrics_by_audience['Clics en el enlace']) * 100
    metrics_by_audience['Frecuencia'] = metrics_by_audience['Impresiones'] / metrics_by_audience['Alcance']
    
    # Crear figura con subplots
    fig = go.Figure()
    
    # Definir colores para cada público
    colors = {
        'Advantage': '#6AB187',
        'Pucón': '#F6AE2D',
        'Otro': '#6A8EAE'
    }
    
    # Métricas para comparar
    metrics = [
        {'name': 'CTR (%)', 'col': 'CTR (%)', 'format': '.2f%'},
        {'name': 'CPC (CLP)', 'col': 'CPC (CLP)', 'format': ',.0f'},
        {'name': 'CPM (CLP)', 'col': 'CPM (CLP)', 'format': ',.0f'},
        {'name': 'Frecuencia', 'col': 'Frecuencia', 'format': '.2f'}
    ]
    
    # Añadir barras para cada métrica por público
    for i, metric in enumerate(metrics):
        for j, (audience, row) in enumerate(metrics_by_audience.iterrows()):
            fig.add_trace(go.Bar(
                x=[metric['name']],
                y=[row[metric['col']]],
                name=f"{row['Público']} - {metric['name']}",
                marker_color=colors.get(row['Público'], '#888888'),
                legendgroup=row['Público'],
                showlegend=i==0,  # Mostrar en leyenda solo para la primera métrica
                offsetgroup=row['Público'],
                hovertemplate=f"{row['Público']}<br>{metric['name']}: {row[metric['col']]:.2f}<br>Gasto: ${row['Importe gastado (CLP)']:,.0f}"
            ))
    
    # Configurar diseño
    fig.update_layout(
        title='Comparación de Rendimiento por Tipo de Público',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        barmode='group',
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        yaxis=dict(
            title='Valor',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        legend=dict(
            font=dict(color=COLORS['text']),
            orientation='h',
            y=1.1
        ),
        hovermode='closest'
    )
    
    return fig

def crear_grafico_evolucion_diaria(df_gasto_diario, periodo):
    """Crea un gráfico que muestra la evolución diaria del gasto y métricas en Meta."""
    
    # Copia para no modificar original
    df = df_gasto_diario.copy()
    
    # Agrupar por periodo seleccionado
    if periodo == 'D':
        df['fecha_grupo'] = df['Día']
        titulo = 'Evolución Diaria de Gasto en Meta'
    elif periodo == 'W':
        df['fecha_grupo'] = df['Día'] - pd.to_timedelta(df['Día'].dt.dayofweek, unit='D')
        df['fecha_label'] = df['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df = df.groupby('fecha_grupo').agg({
            'Alcance': 'sum',
            'Impresiones': 'sum',
            'Importe gastado (CLP)': 'sum',
            'CPC (todos)': 'mean',
            'fecha_label': 'first'
        }).reset_index()
        titulo = 'Evolución Semanal de Gasto en Meta'
    else:  # 'M'
        df['fecha_grupo'] = df['Día'].dt.to_period('M').dt.to_timestamp()
        df['fecha_label'] = df['Día'].dt.strftime('%B %Y')
        df = df.groupby('fecha_grupo').agg({
            'Alcance': 'sum',
            'Impresiones': 'sum',
            'Importe gastado (CLP)': 'sum',
            'CPC (todos)': 'mean',
            'fecha_label': 'first'
        }).reset_index()
        titulo = 'Evolución Mensual de Gasto en Meta'
    
    # Calcular CTR, aunque sea aproximado al no tener clics directamente
    df['CTR Aprox. (%)'] = (df['Importe gastado (CLP)'] / df['CPC (todos)']) / df['Impresiones'] * 100
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir barras para gasto
    fig.add_trace(go.Bar(
        x=df['fecha_grupo'],
        y=df['Importe gastado (CLP)'],
        name='Gasto (CLP)',
        marker_color=COLORS['expense'],
        hovertemplate='Fecha: %{x}<br>Gasto: $%{y:,.0f}<br>'
    ))
    
    # Añadir línea para impresiones
    fig.add_trace(go.Scatter(
        x=df['fecha_grupo'],
        y=df['Impresiones'],
        name='Impresiones',
        mode='lines',
        line=dict(color='#3498db', width=2),
        yaxis='y2',
        hovertemplate='Fecha: %{x}<br>Impresiones: %{y:,.0f}<br>'
    ))
    
    # Añadir línea para CTR aproximado
    fig.add_trace(go.Scatter(
        x=df['fecha_grupo'],
        y=df['CTR Aprox. (%)'],
        name='CTR Aprox. (%)',
        mode='lines',
        line=dict(color='#FFD700', width=2, dash='dot'),
        yaxis='y3',
        hovertemplate='Fecha: %{x}<br>CTR Aprox.: %{y:.2f}%<br>'
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
            title_font={'color': COLORS['text']}
        ),
        yaxis=dict(
            title='Gasto (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        yaxis2=dict(
            title='Impresiones',
            overlaying='y',
            side='right',
            showgrid=False,
            tickfont={'color': '#3498db'},
            title_font={'color': '#3498db'}
        ),
        yaxis3=dict(
            title='CTR (%)',
            overlaying='y',
            side='right',
            position=0.85,
            showgrid=False,
            tickfont={'color': '#FFD700'},
            title_font={'color': '#FFD700'}
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='x unified'
    )
    
    # Ajustar etiquetas si es semanal o mensual
    if periodo in ['W', 'M']:
        fechas_ordenadas = sorted(list(df['fecha_grupo'].unique()))
        etiquetas = [df[df['fecha_grupo'] == fecha]['fecha_label'].iloc[0] for fecha in fechas_ordenadas]
        
        fig.update_xaxes(
            ticktext=etiquetas,
            tickvals=fechas_ordenadas
        )
    
    return fig

def crear_grafico_anuncios_rendimiento(df_campana):
    """Crea un gráfico que compara el rendimiento de los diferentes anuncios."""
    
    # Agrupar por anuncio
    metrics_by_ad = df_campana.groupby(['Nombre del anuncio', 'Tipo de Anuncio']).agg({
        'Importe gastado (CLP)': 'sum',
        'Impresiones': 'sum',
        'Clics en el enlace': 'sum',
        'Artículos agregados al carrito': 'sum',
        'Alcance': 'sum'
    }).reset_index()
    
    # Calcular métricas
    metrics_by_ad['CTR (%)'] = (metrics_by_ad['Clics en el enlace'] / metrics_by_ad['Impresiones']) * 100
    metrics_by_ad['CPC (CLP)'] = metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Clics en el enlace']
    metrics_by_ad['CPM (CLP)'] = (metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Impresiones']) * 1000
    metrics_by_ad['Conversión (%)'] = metrics_by_ad['Artículos agregados al carrito'].fillna(0) / metrics_by_ad['Clics en el enlace'] * 100
    
    # Ordenar por gasto total
    metrics_by_ad = metrics_by_ad.sort_values('Importe gastado (CLP)', ascending=False)
    
    # Tomar los 8 anuncios con mayor gasto
    top_ads = metrics_by_ad.head(8)
    
    # Crear figura
    fig = go.Figure()
    
    # Definir colores por tipo de anuncio
    colors = {
        'Video explicativo': '#6AB187',
        'Video inicial': '#F6AE2D',
        'Video publicitario': '#3498db',
        'Video Flo': '#e74c3c',
        'Día de la madre': '#9b59b6',
        'Parejas': '#1abc9c',
        'Video Karin': '#f39c12',
        'Video Lluvia': '#34495e',
        'Otro': '#95a5a6'
    }
    
    # Añadir barras para el gasto
    for i, row in top_ads.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Nombre del anuncio']],
            y=[row['Importe gastado (CLP)']],
            name=row['Tipo de Anuncio'],
            marker_color=colors.get(row['Tipo de Anuncio'], '#888888'),
            hovertemplate=(
                f"Anuncio: {row['Nombre del anuncio']}<br>"
                f"Tipo: {row['Tipo de Anuncio']}<br>"
                f"Gasto: ${row['Importe gastado (CLP)']:,.0f}<br>"
                f"CTR: {row['CTR (%)']:.2f}%<br>"
                f"CPC: ${row['CPC (CLP)']:,.0f}<br>"
                f"Impresiones: {row['Impresiones']:,.0f}<br>"
                f"Clics: {row['Clics en el enlace']:,.0f}"
            )
        ))
    
    # Añadir marcadores para CTR
    for i, row in top_ads.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['Nombre del anuncio']],
            y=[row['CTR (%)']],
            mode='markers',
            marker=dict(
                size=12,
                symbol='diamond',
                color='#FFD700',
                line=dict(color='#000000', width=1)
            ),
            name='CTR (%)' if i == 0 else None,
            showlegend=i == 0,
            yaxis='y2',
            hoverinfo='skip'
        ))
    
    # Configurar diseño
    fig.update_layout(
        title='Rendimiento por Anuncio - Gasto vs CTR',
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
        xaxis=dict(
            title='Anuncio',
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
            title_font={'color': COLORS['text']}
        ),
        yaxis2=dict(
            title='CTR (%)',
            overlaying='y',
            side='right',
            showgrid=False,
            range=[0, max(top_ads['CTR (%)']) * 1.2],  # Ajustar rango para CTR
            tickfont={'color': '#FFD700'},
            title_font={'color': '#FFD700'}
        ),
        legend=dict(
            font=dict(color=COLORS['text']),
            title='Tipo de Anuncio'
        ),
        hovermode='closest'
    )
    
    return fig

# ======== FUNCIONES PARA GENERAR INSIGHTS ========
def generar_insights_evolucion_gasto(df_gasto_diario):
    """Genera insights sobre la evolución del gasto en Meta."""
    try:
        # Calcular tendencias y días con mayor/menor gasto
        total_gasto = df_gasto_diario['Importe gastado (CLP)'].sum()
        promedio_diario = df_gasto_diario['Importe gastado (CLP)'].mean()
        
        # Encontrar día con mayor gasto
        dia_max_gasto = df_gasto_diario.loc[df_gasto_diario['Importe gastado (CLP)'].idxmax()]
        
        # Calcular tendencia (comparar primera mitad vs segunda mitad)
        mitad = len(df_gasto_diario) // 2
        if mitad > 0:
            primera_mitad = df_gasto_diario.iloc[:mitad]['Importe gastado (CLP)'].mean()
            segunda_mitad = df_gasto_diario.iloc[mitad:]['Importe gastado (CLP)'].mean()
            tendencia = "creciente" if segunda_mitad > primera_mitad else "decreciente"
            cambio_porcentual = abs((segunda_mitad - primera_mitad) / primera_mitad * 100) if primera_mitad > 0 else 0
        else:
            tendencia = "estable"
            cambio_porcentual = 0
        
        # Generar texto de insights
        insights = [
            f"El gasto total en el período analizado fue de ${total_gasto:,.0f} CLP, con un promedio diario de ${promedio_diario:,.0f} CLP.",
            f"El día con mayor inversión fue el {dia_max_gasto['Día'].strftime('%d/%m/%Y')} con ${dia_max_gasto['Importe gastado (CLP)']:,.0f} CLP.",
            f"La tendencia del gasto es {tendencia}, con una variación del {cambio_porcentual:.1f}% entre la primera y segunda mitad del período."
        ]
        
        # Añadir insights sobre impresiones y CTR si hay suficientes datos
        if 'Impresiones' in df_gasto_diario.columns and len(df_gasto_diario) > 1:
            total_impresiones = df_gasto_diario['Impresiones'].sum()
            costo_mil_impresiones = (total_gasto / total_impresiones) * 1000 if total_impresiones > 0 else 0
            insights.append(f"Se generaron {total_impresiones:,.0f} impresiones con un CPM promedio de ${costo_mil_impresiones:.2f} CLP.")
        
        return html.Div([html.P(insight) for insight in insights])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: datos insuficientes o error en el análisis. {str(e)}")])

def generar_insights_adsets(df_campana):
    """Genera insights sobre el rendimiento de los conjuntos de anuncios."""
    try:
        # Agrupar por conjunto de anuncios
        metrics_by_adset = df_campana.groupby('Nombre del conjunto de anuncios').agg({
            'Importe gastado (CLP)': 'sum',
            'Impresiones': 'sum',
            'Clics en el enlace': 'sum',
            'Artículos agregados al carrito': 'sum'
        }).reset_index()
        
        # Calcular CTR y CPC
        metrics_by_adset['CTR'] = metrics_by_adset['Clics en el enlace'] / metrics_by_adset['Impresiones'] * 100
        metrics_by_adset['CPC'] = metrics_by_adset['Importe gastado (CLP)'] / metrics_by_adset['Clics en el enlace']
        
        # Ordenar por gasto
        metrics_by_adset = metrics_by_adset.sort_values('Importe gastado (CLP)', ascending=False)
        
        # Obtener mejor y peor conjunto por CTR (entre los que tienen gasto significativo)
        adsets_significativos = metrics_by_adset[metrics_by_adset['Importe gastado (CLP)'] > metrics_by_adset['Importe gastado (CLP)'].mean() * 0.2]
        
        if not adsets_significativos.empty:
            mejor_ctr = adsets_significativos.loc[adsets_significativos['CTR'].idxmax()]
            peor_ctr = adsets_significativos.loc[adsets_significativos['CTR'].idxmin()]
            
            # Generar insights
            insights = [
                f"El conjunto de anuncios con mayor inversión fue '{metrics_by_adset.iloc[0]['Nombre del conjunto de anuncios']}' con ${metrics_by_adset.iloc[0]['Importe gastado (CLP)']:,.0f} CLP.",
                f"El conjunto con mejor CTR fue '{mejor_ctr['Nombre del conjunto de anuncios']}' con {mejor_ctr['CTR']:.2f}% y un CPC de ${mejor_ctr['CPC']:,.0f} CLP.",
                f"El conjunto con menor rendimiento (CTR) fue '{peor_ctr['Nombre del conjunto de anuncios']}' con {peor_ctr['CTR']:.2f}% y un CPC de ${peor_ctr['CPC']:,.0f} CLP."
            ]
            
            # Añadir insight sobre conversiones si hay datos
            if 'Artículos agregados al carrito' in metrics_by_adset.columns:
                metrics_by_adset['Tasa de conversión'] = metrics_by_adset['Artículos agregados al carrito'] / metrics_by_adset['Clics en el enlace'] * 100
                
                if not metrics_by_adset[metrics_by_adset['Artículos agregados al carrito'] > 0].empty:
                    mejor_conversion = metrics_by_adset.loc[metrics_by_adset['Tasa de conversión'].idxmax()]
                    insights.append(f"El conjunto con mejor tasa de conversión fue '{mejor_conversion['Nombre del conjunto de anuncios']}' con {mejor_conversion['Tasa de conversión']:.2f}% de clics que resultaron en artículos agregados al carrito.")
            
            return html.Div([html.P(insight) for insight in insights])
        else:
            return html.Div([html.P("No hay suficientes datos para generar insights sobre los conjuntos de anuncios.")])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: datos insuficientes o error en el análisis. {str(e)}")])

def generar_insights_publicos(df_campana):
    """Genera insights sobre la comparación de públicos."""
    try:
        # Agrupar por tipo de público
        metrics_by_audience = df_campana.groupby('Público').agg({
            'Importe gastado (CLP)': 'sum',
            'Impresiones': 'sum',
            'Clics en el enlace': 'sum',
            'Artículos agregados al carrito': 'sum'
        }).reset_index()
        
        # Calcular métricas
        metrics_by_audience['CTR'] = metrics_by_audience['Clics en el enlace'] / metrics_by_audience['Impresiones'] * 100
        metrics_by_audience['CPC'] = metrics_by_audience['Importe gastado (CLP)'] / metrics_by_audience['Clics en el enlace']
        
        # Filtrar solo públicos principales (Advantage y Pucón)
        main_audiences = metrics_by_audience[metrics_by_audience['Público'].isin(['Advantage', 'Pucón'])]
        
        if len(main_audiences) >= 2:
            # Comparar rendimiento
            advantage = main_audiences[main_audiences['Público'] == 'Advantage'].iloc[0]
            pucon = main_audiences[main_audiences['Público'] == 'Pucón'].iloc[0]
            
            # Calcular diferencias porcentuales
            ctr_diff = (advantage['CTR'] / pucon['CTR'] - 1) * 100 if pucon['CTR'] > 0 else 0
            cpc_diff = (pucon['CPC'] / advantage['CPC'] - 1) * 100 if advantage['CPC'] > 0 else 0
            
            # Determinar cuál es mejor
            mejor_publico = "Advantage" if advantage['CTR'] > pucon['CTR'] else "Pucón"
            peor_cpc = "Advantage" if advantage['CPC'] > pucon['CPC'] else "Pucón"
            
            # Generar insights
            insights = [
                f"El público de {mejor_publico} muestra un mejor CTR con {abs(ctr_diff):.1f}% {'más' if ctr_diff > 0 else 'menos'} que el otro segmento.",
                f"El costo por clic (CPC) es {'más alto' if cpc_diff > 0 else 'más bajo'} en {peor_cpc} por un {abs(cpc_diff):.1f}%.",
                f"Advantage tuvo un gasto total de ${advantage['Importe gastado (CLP)']:,.0f} CLP vs ${pucon['Importe gastado (CLP)']:,.0f} CLP para Pucón."
            ]
            
            # Añadir insight sobre conversiones si hay datos
            if 'Artículos agregados al carrito' in metrics_by_audience.columns:
                advantage_conv = advantage['Artículos agregados al carrito'] / advantage['Clics en el enlace'] * 100 if advantage['Clics en el enlace'] > 0 else 0
                pucon_conv = pucon['Artículos agregados al carrito'] / pucon['Clics en el enlace'] * 100 if pucon['Clics en el enlace'] > 0 else 0
                
                mejor_conv = "Advantage" if advantage_conv > pucon_conv else "Pucón"
                conv_diff = (max(advantage_conv, pucon_conv) / max(0.1, min(advantage_conv, pucon_conv)) - 1) * 100
                
                insights.append(f"En términos de conversión, el público de {mejor_conv} muestra un rendimiento {conv_diff:.1f}% superior.")
            
            return html.Div([html.P(insight) for insight in insights])
        else:
            return html.Div([html.P("No hay suficientes datos para comparar los públicos de Advantage y Pucón.")])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: datos insuficientes o error en el análisis. {str(e)}")])

def generar_insights_anuncios(df_campana):
    """Genera insights sobre el rendimiento de los anuncios."""
    try:
        # Agrupar por anuncio y tipo
        metrics_by_ad = df_campana.groupby(['Nombre del anuncio', 'Tipo de Anuncio']).agg({
            'Importe gastado (CLP)': 'sum',
            'Impresiones': 'sum',
            'Clics en el enlace': 'sum',
            'Artículos agregados al carrito': 'sum'
        }).reset_index()
        
        # Calcular métricas
        metrics_by_ad['CTR'] = metrics_by_ad['Clics en el enlace'] / metrics_by_ad['Impresiones'] * 100
        metrics_by_ad['CPC'] = metrics_by_ad['Importe gastado (CLP)'] / metrics_by_ad['Clics en el enlace']
        
        # Ordenar por gasto
        metrics_by_ad = metrics_by_ad.sort_values('Importe gastado (CLP)', ascending=False)
        
        # Filtrar anuncios con gasto significativo
        significant_ads = metrics_by_ad[metrics_by_ad['Importe gastado (CLP)'] > metrics_by_ad['Importe gastado (CLP)'].mean() * 0.2]
        
        if not significant_ads.empty:
            # Encontrar mejor y peor anuncio por CTR
            mejor_ctr = significant_ads.loc[significant_ads['CTR'].idxmax()]
            peor_ctr = significant_ads.loc[significant_ads['CTR'].idxmin()]
            
            # Analizar por tipo de anuncio
            metrics_by_type = df_campana.groupby('Tipo de Anuncio').agg({
                'Importe gastado (CLP)': 'sum',
                'Impresiones': 'sum',
                'Clics en el enlace': 'sum'
            }).reset_index()
            
            metrics_by_type['CTR'] = metrics_by_type['Clics en el enlace'] / metrics_by_type['Impresiones'] * 100
            metrics_by_type = metrics_by_type.sort_values('CTR', ascending=False)
            
            # Generar insights
            insights = [
                f"El anuncio con mayor inversión fue '{metrics_by_ad.iloc[0]['Nombre del anuncio']}' ({metrics_by_ad.iloc[0]['Tipo de Anuncio']}) con ${metrics_by_ad.iloc[0]['Importe gastado (CLP)']:,.0f} CLP.",
                f"El anuncio con mejor CTR fue '{mejor_ctr['Nombre del anuncio']}' ({mejor_ctr['Tipo de Anuncio']}) con {mejor_ctr['CTR']:.2f}% y un CPC de ${mejor_ctr['CPC']:,.0f} CLP.",
                f"El tipo de anuncio con mejor rendimiento es '{metrics_by_type.iloc[0]['Tipo de Anuncio']}' con un CTR promedio de {metrics_by_type.iloc[0]['CTR']:.2f}%."
            ]
            
            # Añadir insight sobre conversiones si hay datos
            if 'Artículos agregados al carrito' in metrics_by_ad.columns:
                metrics_by_ad['Conversión'] = metrics_by_ad['Artículos agregados al carrito'] / metrics_by_ad['Clics en el enlace'] * 100
                converting_ads = metrics_by_ad[metrics_by_ad['Artículos agregados al carrito'] > 0]
                
                if not converting_ads.empty:
                    mejor_conversion = converting_ads.loc[converting_ads['Conversión'].idxmax()]
                    insights.append(f"El anuncio con mejor tasa de conversión fue '{mejor_conversion['Nombre del anuncio']}' con {mejor_conversion['Conversión']:.2f}% de clics que resultaron en artículos agregados al carrito.")
            
            return html.Div([html.P(insight) for insight in insights])
        else:
            return html.Div([html.P("No hay suficientes datos para generar insights sobre los anuncios.")])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: datos insuficientes o error en el análisis. {str(e)}")])

# ======== CREACIÓN DE LA APLICACIÓN ========
def crear_app_marketing(datos=None):
    """Crea la aplicación Dash para el análisis de marketing."""
    
    if datos is None:
        datos = cargar_datos_marketing()
        
    df_campana = datos['campana_meta']
    df_gasto_diario = datos['gasto_diario_meta']
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        crear_header(),
        html.Div([
            html.Div("DASHBOARD DE MARKETING - META ADS", style={
                'color': '#4267B2',  # Color de Facebook/Meta
                'fontSize': '24px', 
                'fontWeight': 'bold',
                'padding': '10px',
                'marginBottom': '20px',
                'textAlign': 'center',
                'backgroundColor': COLORS['card_bg'],
                'borderRadius': '5px'
            }),
            html.Div([
                html.A("Ver Dashboard de Reservas", 
                      href="http://localhost:8050", 
                      style={'color': '#00a3ff', 'textDecoration': 'none', 'fontSize': '16px', 'marginRight': '20px'},
                      target="_blank"),
                html.A("Ver Dashboard de Utilidad Operativa", 
                      href="http://localhost:8051", 
                      style={'color': '#00a3ff', 'textDecoration': 'none', 'fontSize': '16px'},
                      target="_blank")
            ], style={'textAlign': 'center', 'marginBottom': '20px'})
        ]),
        
        # Filtros de fecha
        crear_filtros(df_gasto_diario['Día'].min(), df_gasto_diario['Día'].max()),
        
        # Tarjetas de métricas
        html.Div([
            html.Div([
                html.H3('Gasto Total', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-gasto-meta', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Impresiones', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-impresiones', style={'color': '#3498db', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Clics Totales', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-clics', style={'color': '#2ecc71', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('CTR Promedio', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='ctr-promedio', style={'color': '#FFD700', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('CPC Promedio', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='cpc-promedio', style={'color': '#e74c3c', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Artículos al Carrito', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='articulos-carrito', style={'color': '#9b59b6', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
        
        # Selector de período para gráficos temporales
        crear_selector_periodo(),
        
        # Gráficos principales con sus insights
        crear_contenedor_grafico('evolucion-gasto-meta', 'Evolución del Gasto en Meta Ads'),
        crear_contenedor_insights('insights-evolucion', 'Insights: Evolución del Gasto'),
        
        crear_contenedor_grafico('rendimiento-adsets', 'Rendimiento de Conjuntos de Anuncios'),
        crear_contenedor_insights('insights-adsets', 'Insights: Conjuntos de Anuncios'),
        
        crear_contenedor_grafico('comparacion-publicos', 'Comparación de Públicos: Advantage vs Pucón'),
        crear_contenedor_insights('insights-publicos', 'Insights: Comparación de Públicos'),
        
        crear_contenedor_grafico('rendimiento-anuncios', 'Rendimiento por Anuncio'),
        crear_contenedor_insights('insights-anuncios', 'Insights: Rendimiento de Anuncios'),
        
    ], style={
        'padding': 20,
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })
    
    # Callback para actualizar los gráficos y métricas
    @app.callback(
        [Output('evolucion-gasto-meta', 'figure'),
         Output('rendimiento-adsets', 'figure'),
         Output('comparacion-publicos', 'figure'),
         Output('rendimiento-anuncios', 'figure'),
         Output('total-gasto-meta', 'children'),
         Output('total-impresiones', 'children'),
         Output('total-clics', 'children'),
         Output('ctr-promedio', 'children'),
         Output('cpc-promedio', 'children'),
         Output('articulos-carrito', 'children'),
         # Nuevos outputs para los insights
         Output('insights-evolucion', 'children'),
         Output('insights-adsets', 'children'),
         Output('insights-publicos', 'children'),
         Output('insights-anuncios', 'children')],
        [Input('periodo-selector', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date')]
    )
    def actualizar_graficos_marketing(periodo, start_date, end_date):
        # Filtrar datos de campaña
        df_campana_filtrado = df_campana[
            (df_campana['Inicio del informe'] <= pd.to_datetime(end_date)) & 
            (df_campana['Fin del informe'] >= pd.to_datetime(start_date))
        ]
        
        # Filtrar datos de gasto diario
        df_gasto_diario_filtrado = df_gasto_diario[
            (df_gasto_diario['Día'] >= pd.to_datetime(start_date)) & 
            (df_gasto_diario['Día'] <= pd.to_datetime(end_date))
        ]
        
        # Calcular métricas
        total_gasto = df_gasto_diario_filtrado['Importe gastado (CLP)'].sum()
        total_impresiones = df_gasto_diario_filtrado['Impresiones'].sum()
        
        # Para clics, CTR, CPC y carrito, usamos df_campana ya que df_gasto_diario no tiene estos datos directamente
        total_clics = df_campana_filtrado['Clics en el enlace'].sum()
        
        # Calcular CTR y CPC promedios (ponderados por impresiones)
        pesos = df_campana_filtrado['Impresiones'] / df_campana_filtrado['Impresiones'].sum()
        ctr_promedio = (df_campana_filtrado['CTR (todos)'] * pesos).sum() * 100  # Convertir a porcentaje
        
        # CPC promedio ponderado por clics
        pesos_clics = df_campana_filtrado['Clics en el enlace'] / df_campana_filtrado['Clics en el enlace'].sum()
        cpc_promedio = (df_campana_filtrado['CPC (todos)'] * pesos_clics).sum()
        
        # Artículos agregados al carrito
        articulos_carrito = df_campana_filtrado['Artículos agregados al carrito'].sum()
        
        # Crear gráficos
        fig_evolucion = crear_grafico_evolucion_diaria(df_gasto_diario_filtrado, periodo)
        fig_adsets = crear_grafico_rendimiento_adsets(df_campana_filtrado)
        fig_publicos = crear_grafico_comparacion_publicos(df_campana_filtrado)
        fig_anuncios = crear_grafico_anuncios_rendimiento(df_campana_filtrado)
        
        # Generar insights
        insights_evolucion = generar_insights_evolucion_gasto(df_gasto_diario_filtrado)
        insights_adsets = generar_insights_adsets(df_campana_filtrado)
        insights_publicos = generar_insights_publicos(df_campana_filtrado)
        insights_anuncios = generar_insights_anuncios(df_campana_filtrado)
        
        return (
            fig_evolucion,
            fig_adsets,
            fig_publicos,
            fig_anuncios,
            f'${total_gasto:,.0f}',
            f'{total_impresiones:,.0f}',
            f'{total_clics:,.0f}',
            f'{ctr_promedio:.2f}%',
            f'${cpc_promedio:.0f}',
            f'{articulos_carrito:.0f}',
            insights_evolucion,
            insights_adsets,
            insights_publicos,
            insights_anuncios
        )
    
    return app

# ======== EJECUCIÓN DE LA APLICACIÓN ========
if __name__ == '__main__':
    app = crear_app_marketing()
    print("\n=== DASHBOARD DE MARKETING - META ADS ===")
    print("Dashboard disponible en: http://localhost:8052")
    print("O alternativamente en: http://127.0.0.1:8052")
    app.run(debug=True, host='localhost', port=8052) 