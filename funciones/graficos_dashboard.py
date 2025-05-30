import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Definir colores y estilos para todos los gráficos
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

GRAPH_STYLE = {
    'paper_bgcolor': COLORS['card_bg'],
    'plot_bgcolor': COLORS['card_bg'],
    'font': {'color': COLORS['text']},
    'height': 500,
}

def crear_grafico_ingresos_gastos(df_payments, df_expenses, periodo):
    """Crea un gráfico comparativo de ingresos y gastos por periodo."""
    
    # Preparar datos según el periodo seleccionado
    if periodo == 'D':
        df_payments['fecha_grupo'] = df_payments["Fecha"].dt.date
        df_expenses['fecha_grupo'] = df_expenses["Fecha"].dt.date
        titulo = 'Ingresos y Gastos por Día'
    elif periodo == 'W':
        df_payments['fecha_grupo'] = df_payments["Fecha"] - pd.to_timedelta(df_payments["Fecha"].dt.dayofweek, unit='D')
        df_payments['fecha_label'] = df_payments['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df_expenses['fecha_grupo'] = df_expenses["Fecha"] - pd.to_timedelta(df_expenses["Fecha"].dt.dayofweek, unit='D')
        df_expenses['fecha_label'] = df_expenses['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        titulo = 'Ingresos y Gastos por Semana'
    else:
        df_payments['fecha_grupo'] = df_payments["Fecha"].dt.to_period('M').dt.to_timestamp()
        df_payments['fecha_label'] = df_payments["Fecha"].dt.strftime('%B %Y')
        df_expenses['fecha_grupo'] = df_expenses["Fecha"].dt.to_period('M').dt.to_timestamp()
        df_expenses['fecha_label'] = df_expenses["Fecha"].dt.strftime('%B %Y')
        titulo = 'Ingresos y Gastos por Mes'

    # Agrupar datos
    ingresos_totales = df_payments.groupby('fecha_grupo')['Monto'].sum().reset_index()
    gastos = df_expenses.groupby('fecha_grupo')['Monto'].sum().reset_index()

    # Crear figura
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ingresos_totales['fecha_grupo'],
        y=ingresos_totales['Monto'],
        name='Ingresos',
        marker_color=COLORS['income'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    fig.add_trace(go.Bar(
        x=gastos['fecha_grupo'],
        y=gastos['Monto'],
        name='Gastos',
        marker_color=COLORS['expense'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title=titulo,
        **GRAPH_STYLE,
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        yaxis=dict(
            title='Monto (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='x unified'
    )
    
    # Ajustar etiquetas si es semanal o mensual
    if periodo in ['W', 'M']:
        fig.update_xaxes(
            ticktext=df_payments.groupby('fecha_grupo')['fecha_label'].first(),
            tickvals=ingresos_totales['fecha_grupo']
        )
    return fig

def crear_grafico_utilidad_operativa(df_ingresos, df_costos_operativos, df_gastos_marketing, periodo):
    """Crea un gráfico de utilidad operativa por periodo."""
    
    # Preparar datos según el periodo seleccionado
    if periodo == 'D':
        df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.date
        df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.date
        df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.date
        titulo = 'Utilidad Operativa por Día'
    elif periodo == 'W':
        df_ingresos['fecha_grupo'] = df_ingresos["fecha"] - pd.to_timedelta(df_ingresos["fecha"].dt.dayofweek, unit='D')
        df_ingresos['fecha_label'] = df_ingresos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"] - pd.to_timedelta(df_costos_operativos["fecha"].dt.dayofweek, unit='D')
        df_costos_operativos['fecha_label'] = df_costos_operativos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"] - pd.to_timedelta(df_gastos_marketing["fecha"].dt.dayofweek, unit='D')
        df_gastos_marketing['fecha_label'] = df_gastos_marketing['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        titulo = 'Utilidad Operativa por Semana'
    else:
        df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.to_period('M').dt.to_timestamp()
        df_ingresos['fecha_label'] = df_ingresos["fecha"].dt.strftime('%B %Y')
        df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.to_period('M').dt.to_timestamp()
        df_costos_operativos['fecha_label'] = df_costos_operativos["fecha"].dt.strftime('%B %Y')
        df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.to_period('M').dt.to_timestamp()
        df_gastos_marketing['fecha_label'] = df_gastos_marketing["fecha"].dt.strftime('%B %Y')
        titulo = 'Utilidad Operativa por Mes'

    # Agrupar datos
    ingresos_totales = df_ingresos.groupby('fecha_grupo')['monto'].sum().reset_index()
    costos_operativos = df_costos_operativos.groupby('fecha_grupo')['monto'].sum().reset_index()
    gastos_marketing = df_gastos_marketing.groupby('fecha_grupo')['monto'].sum().reset_index()

    # Crear figura
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ingresos_totales['fecha_grupo'],
        y=ingresos_totales['monto'],
        name='Ingresos Totales',
        marker_color=COLORS['income'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    fig.add_trace(go.Bar(
        x=costos_operativos['fecha_grupo'],
        y=costos_operativos['monto'],
        name='Costos Operativos',
        marker_color=COLORS['expense'],
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    fig.add_trace(go.Bar(
        x=gastos_marketing['fecha_grupo'],
        y=gastos_marketing['monto'],
        name='Gastos Marketing',
        marker_color='#ff6b6b',
        hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
        type='bar'
    ))
    
    # Configurar diseño
    fig.update_layout(
        title=titulo,
        **GRAPH_STYLE,
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        xaxis=dict(
            title='Fecha',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        yaxis=dict(
            title='Monto (CLP)',
            showgrid=True,
            gridcolor=COLORS['grid'],
            tickfont={'color': COLORS['text']},
            title_font={'color': COLORS['text']}
        ),
        legend=dict(font=dict(color=COLORS['text'])),
        hovermode='x unified'
    )
    
    # Ajustar etiquetas si es semanal o mensual
    if periodo in ['W', 'M']:
        fig.update_xaxes(
            ticktext=df_ingresos.groupby('fecha_grupo')['fecha_label'].first(),
            tickvals=ingresos_totales['fecha_grupo']
        )
    return fig

def crear_grafico_horas_populares(df):
    """Crea un gráfico de barras que muestra las horas más populares para reservas."""
    
    if 'hora_trip' not in df.columns:
        return go.Figure()
    
    horas_count = df['hora_trip'].value_counts().sort_index()
    
    fig = px.bar(
        x=horas_count.index,
        y=horas_count.values,
        title='Horarios Más Populares',
        labels={'x': 'Hora del Día', 'y': 'Número de Reservas'},
        text=horas_count.values
    )
    
    fig.update_layout(
        **GRAPH_STYLE,
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor=COLORS['grid'], tickfont={'color': COLORS['text']}, title_font={'color': COLORS['text']}),
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid'], tickfont={'color': COLORS['text']}, title_font={'color': COLORS['text']})
    )
    
    fig.update_traces(marker_color=COLORS['primary'], textposition='auto')
    
    return fig

def crear_grafico_reservas(df_filtrado, periodo):
    """Crea un gráfico de reservas por periodo (día, semana, mes)."""
    
    if periodo == 'D':
        df_agrupado = df_filtrado.groupby('fecha_trip').size().reset_index(name='cantidad')
        fig = px.bar(df_agrupado, x='fecha_trip', y='cantidad', title='Reservas por Día')
    elif periodo == 'W':
        df_filtrado = df_filtrado.copy()
        df_filtrado['inicio_semana'] = df_filtrado['fecha_trip'] - pd.to_timedelta(df_filtrado['fecha_trip'].dt.dayofweek, unit='D')
        df_filtrado['semana_label'] = df_filtrado['inicio_semana'].dt.strftime('Semana del %d/%m/%Y')
        df_agrupado = df_filtrado.groupby(['inicio_semana', 'semana_label']).size().reset_index(name='cantidad')
        df_agrupado = df_agrupado.sort_values('inicio_semana')
        fig = px.bar(df_agrupado, x='inicio_semana', y='cantidad', title='Reservas por Semana')
        fig.update_xaxes(ticktext=df_agrupado['semana_label'], tickvals=df_agrupado['inicio_semana'])
    else:
        df_filtrado = df_filtrado.copy()
        df_filtrado['inicio_mes'] = df_filtrado['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        df_filtrado['mes_label'] = df_filtrado['fecha_trip'].dt.strftime('%B %Y')
        df_agrupado = df_filtrado.groupby(['inicio_mes', 'mes_label']).size().reset_index(name='cantidad')
        df_agrupado = df_agrupado.sort_values('inicio_mes')
        fig = px.bar(df_agrupado, x='inicio_mes', y='cantidad', title='Reservas por Mes')
        fig.update_xaxes(ticktext=df_agrupado['mes_label'], tickvals=df_agrupado['inicio_mes'])
    
    fig.update_layout(
        **GRAPH_STYLE,
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor=COLORS['grid'], tickfont={'color': COLORS['text']}, title_font={'color': COLORS['text']}),
        yaxis=dict(showgrid=True, gridcolor=COLORS['grid'], tickfont={'color': COLORS['text']}, title_font={'color': COLORS['text']})
    )
    
    fig.update_traces(marker_color=COLORS['primary'])
    
    return fig 