import dash
from dash import html, dcc, Input, Output
import pandas as pd
from datetime import datetime
import os
import plotly.graph_objects as go
from funciones.funciones import *
from funciones.funciones_reservas import *

# Importar módulos personalizados
from funciones.graficos_dashboard import (
    crear_grafico_ingresos_gastos,
    crear_grafico_horas_populares,
    crear_grafico_reservas,
    crear_grafico_utilidad_operativa,
    COLORS
)

from funciones.componentes_dashboard import (
    crear_header,
    crear_filtros,
    crear_selector_periodo,
    crear_tarjetas_metricas,
    crear_contenedor_grafico,
    crear_contenedor_insights,
    CARD_STYLE
)

# ======== CARGA DE DATOS ========
def cargar_datos():
    """Carga todos los archivos CSV necesarios para el dashboard."""
    
    # Crear directorio para gráficos si no existe
    if not os.path.exists("archivos_output/graficos"):
        os.makedirs("archivos_output/graficos")
    
    # Carga de datos de reservas
    df = pd.read_csv("archivos_output/reservas_HotBoat.csv")
    df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])
    
    # Carga de datos financieros
    df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
    df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"])
    df_payments["Monto"] = df_payments["Monto"].astype(float)
    
    df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")
    df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"])
    df_expenses["Monto"] = df_expenses["Monto"].astype(float)
    
    # Extraer costos fijos desde gastos
    df_costos_fijos = df_expenses[df_expenses["Categoría 1"] == "Costos Fijos"].copy()
    
    # Datos para análisis de utilidad operativa
    df_ingresos = pd.read_csv("archivos_output/ingresos_totales.csv")
    df_ingresos["fecha"] = pd.to_datetime(df_ingresos["fecha"])
    
    df_costos_operativos = pd.read_csv("archivos_output/costos_operativos.csv")
    df_costos_operativos["fecha"] = pd.to_datetime(df_costos_operativos["fecha"])
    
    df_gastos_marketing = pd.read_csv("archivos_output/gastos_marketing.csv")
    df_gastos_marketing["fecha"] = pd.to_datetime(df_gastos_marketing["fecha"])
    
    return {
        'reservas': df,
        'pagos': df_payments,
        'gastos': df_expenses,
        'costos_fijos': df_costos_fijos,
        'ingresos': df_ingresos,
        'costos_operativos': df_costos_operativos,
        'gastos_marketing': df_gastos_marketing
    }

# ======== FUNCIONES PARA GRÁFICOS INTERACTIVOS ========
def crear_grafico_interactivo(df_ingresos, df_costos_operativos, df_gastos_marketing, df_costos_fijos, periodo, variables_seleccionadas):
    """Crea un gráfico interactivo que muestra solo las variables seleccionadas."""
    
    # Preparar datos según el periodo seleccionado
    if periodo == 'D':
        # Preparación para ingresos
        if df_ingresos is not None:
            df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.date
        # Preparación para costos operativos  
        if df_costos_operativos is not None:
            df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.date
        # Preparación para gastos marketing
        if df_gastos_marketing is not None:
            df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.date
        # Preparación para costos fijos
        if df_costos_fijos is not None:
            df_costos_fijos['fecha_grupo'] = df_costos_fijos["Fecha"].dt.date
        
        titulo = 'Análisis Financiero por Día'
    elif periodo == 'W':
        # Preparación para ingresos
        if df_ingresos is not None:
            df_ingresos['fecha_grupo'] = df_ingresos["fecha"] - pd.to_timedelta(df_ingresos["fecha"].dt.dayofweek, unit='D')
            df_ingresos['fecha_label'] = df_ingresos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        # Preparación para costos operativos
        if df_costos_operativos is not None:
            df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"] - pd.to_timedelta(df_costos_operativos["fecha"].dt.dayofweek, unit='D')
            df_costos_operativos['fecha_label'] = df_costos_operativos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        # Preparación para gastos marketing
        if df_gastos_marketing is not None:
            df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"] - pd.to_timedelta(df_gastos_marketing["fecha"].dt.dayofweek, unit='D')
            df_gastos_marketing['fecha_label'] = df_gastos_marketing['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        # Preparación para costos fijos
        if df_costos_fijos is not None:
            df_costos_fijos['fecha_grupo'] = df_costos_fijos["Fecha"] - pd.to_timedelta(df_costos_fijos["Fecha"].dt.dayofweek, unit='D')
            df_costos_fijos['fecha_label'] = df_costos_fijos['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        
        titulo = 'Análisis Financiero por Semana'
    else:  # 'M'
        # Preparación para ingresos
        if df_ingresos is not None:
            df_ingresos['fecha_grupo'] = df_ingresos["fecha"].dt.to_period('M').dt.to_timestamp()
            df_ingresos['fecha_label'] = df_ingresos["fecha"].dt.strftime('%B %Y')
        # Preparación para costos operativos
        if df_costos_operativos is not None:
            df_costos_operativos['fecha_grupo'] = df_costos_operativos["fecha"].dt.to_period('M').dt.to_timestamp()
            df_costos_operativos['fecha_label'] = df_costos_operativos["fecha"].dt.strftime('%B %Y')
        # Preparación para gastos marketing
        if df_gastos_marketing is not None:
            df_gastos_marketing['fecha_grupo'] = df_gastos_marketing["fecha"].dt.to_period('M').dt.to_timestamp()
            df_gastos_marketing['fecha_label'] = df_gastos_marketing["fecha"].dt.strftime('%B %Y')
        # Preparación para costos fijos
        if df_costos_fijos is not None:
            df_costos_fijos['fecha_grupo'] = df_costos_fijos["Fecha"].dt.to_period('M').dt.to_timestamp()
            df_costos_fijos['fecha_label'] = df_costos_fijos["Fecha"].dt.strftime('%B %Y')
        
        titulo = 'Análisis Financiero por Mes'

    # Agrupar datos para cada categoría
    datos_agrupados = {}
    fechas_todas = set()
    etiquetas_fecha = {}
    
    # Procesar ingresos
    if 'ingresos' in variables_seleccionadas and df_ingresos is not None:
        ingresos_totales = df_ingresos.groupby('fecha_grupo')['monto'].sum().reset_index()
        datos_agrupados['ingresos'] = ingresos_totales
        fechas_todas.update(ingresos_totales['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_ingresos.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']
    
    # Procesar costos operativos
    if 'costos_operativos' in variables_seleccionadas and df_costos_operativos is not None:
        costos_operativos = df_costos_operativos.groupby('fecha_grupo')['monto'].sum().reset_index()
        datos_agrupados['costos_operativos'] = costos_operativos
        fechas_todas.update(costos_operativos['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_costos_operativos.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']

    # Procesar gastos marketing
    if 'gastos_marketing' in variables_seleccionadas and df_gastos_marketing is not None:
        gastos_marketing = df_gastos_marketing.groupby('fecha_grupo')['monto'].sum().reset_index()
        datos_agrupados['gastos_marketing'] = gastos_marketing
        fechas_todas.update(gastos_marketing['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_gastos_marketing.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']
    
    # Procesar costos fijos
    if 'costos_fijos' in variables_seleccionadas and df_costos_fijos is not None:
        costos_fijos = df_costos_fijos.groupby('fecha_grupo')['Monto'].sum().reset_index()
        datos_agrupados['costos_fijos'] = costos_fijos
        fechas_todas.update(costos_fijos['fecha_grupo'])
        
        if periodo in ['W', 'M']:
            for idx, row in df_costos_fijos.iterrows():
                etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']

    # Crear figura
    fig = go.Figure()
    
    # Colores para cada categoría
    colores_categoria = {
        'ingresos': COLORS['income'],
        'costos_operativos': COLORS['expense'],
        'gastos_marketing': '#ff6b6b',
        'costos_fijos': '#9370db'  # Púrpura medio para costos fijos
    }
    
    # Nombres amigables para mostrar en la leyenda
    nombres_amigables = {
        'ingresos': 'Ingresos Totales',
        'costos_operativos': 'Costos Operativos',
        'gastos_marketing': 'Gastos Marketing',
        'costos_fijos': 'Costos Fijos'
    }
    
    # Añadir barras para cada categoría seleccionada
    for categoria, datos in datos_agrupados.items():
        fig.add_trace(go.Bar(
            x=datos['fecha_grupo'],
            y=datos['monto'] if categoria != 'costos_fijos' else datos['Monto'],
            name=nombres_amigables[categoria],
            marker_color=colores_categoria[categoria],
            hovertemplate='Fecha: %{x}<br>Monto: $%{y:,.0f}<br>',
            type='bar'
        ))
    
    # Configurar diseño
    fig.update_layout(
        title=titulo,
        paper_bgcolor=COLORS['card_bg'],
        plot_bgcolor=COLORS['card_bg'],
        font={'color': COLORS['text']},
        height=500,
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
    if periodo in ['W', 'M'] and etiquetas_fecha:
        fechas_ordenadas = sorted(list(fechas_todas))
        etiquetas = [etiquetas_fecha.get(fecha, '') for fecha in fechas_ordenadas]
        fig.update_xaxes(
            ticktext=etiquetas,
            tickvals=fechas_ordenadas
        )
    
    return fig

# ======== FUNCIÓN PARA GRÁFICO DE VALOR PROMEDIO DE VENTAS ========
def crear_grafico_avg_sale_value(df_reservas, periodo):
    """Crea un gráfico que muestra la evolución del valor promedio de las ventas a lo largo del tiempo."""
    
    # Asegurarse de que tengamos los datos necesarios
    if df_reservas is None or len(df_reservas) == 0:
        fig = go.Figure()
        fig.update_layout(
            title='No hay datos disponibles para mostrar',
            paper_bgcolor=COLORS['card_bg'],
            plot_bgcolor=COLORS['card_bg'],
            font={'color': COLORS['text']},
            height=500,
        )
        return fig
    
    # Convertir TOTAL AMOUNT a tipo numérico si no lo es
    df_reservas['TOTAL AMOUNT'] = pd.to_numeric(df_reservas['TOTAL AMOUNT'], errors='coerce')
    
    # Crear una copia para no modificar el original
    df = df_reservas.copy()
    
    # Agrupar por periodo
    if periodo == 'D':
        df['fecha_grupo'] = df['fecha_trip'].dt.date
        titulo = 'Valor Promedio de Venta por Día'
    elif periodo == 'W':
        df['fecha_grupo'] = df['fecha_trip'] - pd.to_timedelta(df['fecha_trip'].dt.dayofweek, unit='D')
        df['fecha_label'] = df['fecha_grupo'].dt.strftime('Semana del %d/%m/%Y')
        titulo = 'Valor Promedio de Venta por Semana'
    else:  # 'M'
        df['fecha_grupo'] = df['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        df['fecha_label'] = df['fecha_trip'].dt.strftime('%B %Y')
        titulo = 'Valor Promedio de Venta por Mes'
    
    # Calcular el promedio por grupo de fecha
    avg_values = df.groupby('fecha_grupo')['TOTAL AMOUNT'].mean().reset_index()
    
    # Crear figura
    fig = go.Figure()
    
    # Añadir línea para el valor promedio
    fig.add_trace(go.Scatter(
        x=avg_values['fecha_grupo'],
        y=avg_values['TOTAL AMOUNT'],
        mode='lines+markers',
        name='Valor Promedio de Venta',
        line=dict(color='#6AB187', width=3),
        marker=dict(size=8, color='#6AB187', line=dict(width=1, color='#3B7080')),
        hovertemplate='Fecha: %{x}<br>Valor Promedio: $%{y:,.0f}<br>'
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
            title='Valor Promedio (CLP)',
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
        etiquetas_fecha = {}
        for idx, row in df.iterrows():
            etiquetas_fecha[row['fecha_grupo']] = row['fecha_label']
            
        fechas_ordenadas = sorted(list(set(avg_values['fecha_grupo'])))
        etiquetas = [etiquetas_fecha.get(fecha, '') for fecha in fechas_ordenadas]
        
        if etiquetas and fechas_ordenadas:
            fig.update_xaxes(
                ticktext=etiquetas,
                tickvals=fechas_ordenadas
            )
    
    return fig

# ======== FUNCIONES PARA GENERAR INSIGHTS ========
def generar_insights_reservas(df_reservas, periodo):
    """Genera insights sobre las reservas."""
    try:
        # Calcular tendencias y días con mayor/menor reservas
        total_reservas = len(df_reservas)
        
        if total_reservas == 0:
            return html.Div([html.P("No hay datos de reservas para el período seleccionado.")])
        
        # Agrupar por fecha según período
        if periodo == 'D':
            df_reservas['fecha_grupo'] = df_reservas['fecha_trip'].dt.date
            agrupacion = 'diario'
        elif periodo == 'W':
            df_reservas['fecha_grupo'] = df_reservas['fecha_trip'] - pd.to_timedelta(df_reservas['fecha_trip'].dt.dayofweek, unit='D')
            agrupacion = 'semanal'
        else:  # 'M'
            df_reservas['fecha_grupo'] = df_reservas['fecha_trip'].dt.to_period('M').dt.to_timestamp()
            agrupacion = 'mensual'
        
        # Contar reservas por fecha
        reservas_por_fecha = df_reservas.groupby('fecha_grupo').size().reset_index(name='count')
        
        # Encontrar período con más reservas
        max_reservas = reservas_por_fecha.loc[reservas_por_fecha['count'].idxmax()]
        
        # Calcular promedio y tendencia
        promedio_reservas = reservas_por_fecha['count'].mean()
        
        # Si hay suficientes datos, analizar tendencia
        if len(reservas_por_fecha) > 1:
            primera_mitad = reservas_por_fecha.iloc[:len(reservas_por_fecha)//2]['count'].mean()
            segunda_mitad = reservas_por_fecha.iloc[len(reservas_por_fecha)//2:]['count'].mean()
            tendencia = "creciente" if segunda_mitad > primera_mitad else "decreciente" if segunda_mitad < primera_mitad else "estable"
            cambio_porcentual = abs((segunda_mitad - primera_mitad) / primera_mitad * 100) if primera_mitad > 0 else 0
        else:
            tendencia = "no determinada"
            cambio_porcentual = 0
        
        # Analizar tipo de embarcación y tiempo de viaje
        tipos_embarcacion = df_reservas['type boat'].value_counts()
        embarcacion_popular = tipos_embarcacion.index[0] if not tipos_embarcacion.empty else "No disponible"
        
        # Generar insights
        if periodo == 'D':
            fecha_max = max_reservas['fecha_grupo'].strftime('%d/%m/%Y')
        elif periodo == 'W':
            fecha_max = f"semana del {max_reservas['fecha_grupo'].strftime('%d/%m/%Y')}"
        else:
            fecha_max = max_reservas['fecha_grupo'].strftime('%B %Y')
        
        insights = [
            f"Se registraron un total de {total_reservas} reservas en el período seleccionado, con un promedio {agrupacion} de {promedio_reservas:.1f} reservas.",
            f"El período con mayor número de reservas fue {fecha_max} con {max_reservas['count']} reservas.",
            f"La tendencia de reservas es {tendencia}, con una variación del {cambio_porcentual:.1f}% entre la primera y segunda mitad del período."
        ]
        
        if embarcacion_popular != "No disponible":
            insights.append(f"La embarcación más popular fue '{embarcacion_popular}', representando el {tipos_embarcacion[embarcacion_popular]/total_reservas*100:.1f}% de las reservas.")
        
        # Análisis adicional de ingreso promedio si hay datos de monto
        if 'TOTAL AMOUNT' in df_reservas.columns:
            df_reservas['TOTAL AMOUNT'] = pd.to_numeric(df_reservas['TOTAL AMOUNT'], errors='coerce')
            monto_promedio = df_reservas['TOTAL AMOUNT'].mean()
            insights.append(f"El monto promedio por reserva fue de ${monto_promedio:,.0f} CLP.")
        
        return html.Div([html.P(insight) for insight in insights])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: {str(e)}")])

def generar_insights_ingresos_gastos(df_payments, df_expenses, periodo):
    """Genera insights sobre ingresos y gastos."""
    try:
        # Calcular totales
        total_ingresos = df_payments['Monto'].sum()
        total_gastos = df_expenses['Monto'].sum()
        balance = total_ingresos - total_gastos
        
        if total_ingresos == 0 and total_gastos == 0:
            return html.Div([html.P("No hay datos financieros para el período seleccionado.")])
        
        # Agrupar por fecha según período
        if periodo == 'D':
            df_payments['fecha_grupo'] = df_payments['Fecha'].dt.date
            df_expenses['fecha_grupo'] = df_expenses['Fecha'].dt.date
            agrupacion = 'diario'
        elif periodo == 'W':
            df_payments['fecha_grupo'] = df_payments['Fecha'] - pd.to_timedelta(df_payments['Fecha'].dt.dayofweek, unit='D')
            df_expenses['fecha_grupo'] = df_expenses['Fecha'] - pd.to_timedelta(df_expenses['Fecha'].dt.dayofweek, unit='D')
            agrupacion = 'semanal'
        else:  # 'M'
            df_payments['fecha_grupo'] = df_payments['Fecha'].dt.to_period('M').dt.to_timestamp()
            df_expenses['fecha_grupo'] = df_expenses['Fecha'].dt.to_period('M').dt.to_timestamp()
            agrupacion = 'mensual'
        
        # Sumar por fecha
        ingresos_por_fecha = df_payments.groupby('fecha_grupo')['Monto'].sum().reset_index()
        gastos_por_fecha = df_expenses.groupby('fecha_grupo')['Monto'].sum().reset_index()
        
        # Análisis de gastos por categoría
        categorias_gastos = df_expenses.groupby('Categoría 1')['Monto'].sum().sort_values(ascending=False)
        
        # Generar insights
        insights = [
            f"El ingreso total fue de ${total_ingresos:,.0f} CLP y el gasto total fue de ${total_gastos:,.0f} CLP.",
            f"El balance financiero para el período es ${balance:,.0f} CLP, lo que representa un {'superávit' if balance >= 0 else 'déficit'} del {abs(balance/total_ingresos*100 if total_ingresos > 0 else 0):.1f}% respecto a los ingresos."
        ]
        
        # Añadir insight sobre categorías de gastos
        if not categorias_gastos.empty:
            principal_categoria = categorias_gastos.index[0]
            porcentaje_principal = categorias_gastos.iloc[0] / total_gastos * 100
            insights.append(f"La principal categoría de gastos fue '{principal_categoria}' con ${categorias_gastos.iloc[0]:,.0f} CLP ({porcentaje_principal:.1f}% del total).")
        
        # Análisis de tendencia si hay suficientes datos
        if len(ingresos_por_fecha) > 1:
            primera_mitad_ingresos = ingresos_por_fecha.iloc[:len(ingresos_por_fecha)//2]['Monto'].sum()
            segunda_mitad_ingresos = ingresos_por_fecha.iloc[len(ingresos_por_fecha)//2:]['Monto'].sum()
            
            tendencia_ingresos = "creciente" if segunda_mitad_ingresos > primera_mitad_ingresos else "decreciente" if segunda_mitad_ingresos < primera_mitad_ingresos else "estable"
            insights.append(f"La tendencia de ingresos es {tendencia_ingresos} a lo largo del período analizado.")
        
        return html.Div([html.P(insight) for insight in insights])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: {str(e)}")])

def generar_insights_horas_populares(df):
    """Genera insights sobre las horas más populares para reservas."""
    try:
        if 'hora_trip' not in df.columns or df.empty:
            return html.Div([html.P("No hay datos suficientes para analizar las horas populares.")])
        
        # Contar reservas por hora
        reservas_por_hora = df['hora_trip'].value_counts().sort_index()
        
        # Encontrar horas pico
        hora_max = reservas_por_hora.idxmax()
        
        # Dividir el día en franjas
        manana = reservas_por_hora.loc[6:11].sum() if any(h in reservas_por_hora.index for h in range(6, 12)) else 0
        tarde = reservas_por_hora.loc[12:17].sum() if any(h in reservas_por_hora.index for h in range(12, 18)) else 0
        noche = reservas_por_hora.loc[18:23].sum() if any(h in reservas_por_hora.index for h in range(18, 24)) else 0
        
        # Determinar franja más popular
        franjas = {'Mañana (6-11h)': manana, 'Tarde (12-17h)': tarde, 'Noche (18-23h)': noche}
        franja_popular = max(franjas.items(), key=lambda x: x[1])[0]
        
        # Calcular porcentaje de la franja más popular
        total_reservas = sum(franjas.values())
        porcentaje_franja = franjas[franja_popular] / total_reservas * 100 if total_reservas > 0 else 0
        
        # Generar insights
        insights = [
            f"La hora más popular para reservas es a las {hora_max}:00h.",
            f"La franja horaria más concurrida es {franja_popular}, con el {porcentaje_franja:.1f}% de las reservas."
        ]
        
        # Recomendación operativa
        if hora_max in range(10, 16):
            insights.append("Recomendación: Asegurar personal adicional durante las horas del mediodía y primeras horas de la tarde para gestionar el mayor volumen de clientes.")
        elif hora_max in range(6, 10):
            insights.append("Recomendación: Preparar la operación temprano, ya que hay una significativa demanda en las primeras horas de la mañana.")
        else:
            insights.append("Recomendación: Considerar extender los horarios de operación hacia la tarde-noche para maximizar las reservas en esa franja.")
        
        return html.Div([html.P(insight) for insight in insights])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: {str(e)}")])

# Añadir después de las funciones para generar insights del dashboard de reservas
def generar_insights_utilidad_operativa(df_ingresos, df_costos_operativos, df_gastos_marketing, df_costos_fijos, periodo):
    """Genera insights sobre la utilidad operativa."""
    try:
        # Calcular totales
        total_ingresos = df_ingresos['monto'].sum()
        total_costos_op = df_costos_operativos['monto'].sum() if df_costos_operativos is not None else 0
        total_marketing = df_gastos_marketing['monto'].sum() if df_gastos_marketing is not None else 0
        total_costos_fijos = df_costos_fijos['Monto'].sum() if df_costos_fijos is not None else 0
        
        utilidad_operativa = total_ingresos - total_costos_op - total_marketing - total_costos_fijos
        
        if total_ingresos == 0:
            return html.Div([html.P("No hay datos de ingresos para el período seleccionado.")])
        
        # Calcular porcentajes
        margen_op = (utilidad_operativa / total_ingresos) * 100 if total_ingresos > 0 else 0
        pct_costos_op = (total_costos_op / total_ingresos) * 100 if total_ingresos > 0 else 0
        pct_marketing = (total_marketing / total_ingresos) * 100 if total_ingresos > 0 else 0
        pct_costos_fijos = (total_costos_fijos / total_ingresos) * 100 if total_ingresos > 0 else 0
        
        # Agrupar por fecha según período para analizar tendencias
        if periodo == 'D':
            df_ingresos['fecha_grupo'] = df_ingresos['fecha'].dt.date
            agrupacion = 'diaria'
        elif periodo == 'W':
            df_ingresos['fecha_grupo'] = df_ingresos['fecha'] - pd.to_timedelta(df_ingresos['fecha'].dt.dayofweek, unit='D')
            agrupacion = 'semanal'
        else:  # 'M'
            df_ingresos['fecha_grupo'] = df_ingresos['fecha'].dt.to_period('M').dt.to_timestamp()
            agrupacion = 'mensual'
        
        # Calcular utilidad por período
        ingresos_por_periodo = df_ingresos.groupby('fecha_grupo')['monto'].sum()
        
        # Generar insights
        insights = [
            f"La utilidad operativa del período fue de ${utilidad_operativa:,.0f} CLP, representando un margen del {margen_op:.1f}% sobre los ingresos.",
            f"Los costos operativos representan el {pct_costos_op:.1f}%, los gastos de marketing el {pct_marketing:.1f}% y los costos fijos el {pct_costos_fijos:.1f}% de los ingresos totales."
        ]
        
        # Análisis de rentabilidad
        if margen_op >= 20:
            insights.append("La operación muestra una rentabilidad excelente, con un margen operativo superior al 20%.")
        elif margen_op >= 10:
            insights.append("La operación muestra una rentabilidad buena, con un margen operativo entre el 10% y 20%.")
        elif margen_op >= 0:
            insights.append("La operación muestra una rentabilidad ajustada, con un margen operativo positivo pero inferior al 10%.")
        else:
            insights.append("La operación muestra pérdidas en el período analizado. Se recomienda revisar la estructura de costos y estrategias de precio.")
        
        # Recomendaciones basadas en los datos
        mayor_costo = max(pct_costos_op, pct_marketing, pct_costos_fijos)
        if mayor_costo == pct_costos_op:
            insights.append("Recomendación: Enfocarse en optimizar los costos operativos, que representan la mayor proporción de los gastos.")
        elif mayor_costo == pct_marketing:
            insights.append("Recomendación: Evaluar el retorno de la inversión en marketing para optimizar el gasto en este rubro.")
        elif mayor_costo == pct_costos_fijos:
            insights.append("Recomendación: Analizar la estructura de costos fijos y buscar oportunidades de reducción o mayor eficiencia.")
        
        return html.Div([html.P(insight) for insight in insights])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: {str(e)}")])

def generar_insights_valor_promedio_venta(df_reservas, periodo):
    """Genera insights sobre el valor promedio de venta."""
    try:
        if df_reservas.empty or 'TOTAL AMOUNT' not in df_reservas.columns:
            return html.Div([html.P("No hay datos suficientes para analizar el valor promedio de venta.")])
        
        # Convertir a numérico
        df_reservas['TOTAL AMOUNT'] = pd.to_numeric(df_reservas['TOTAL AMOUNT'], errors='coerce')
        
        # Calcular promedios
        valor_promedio = df_reservas['TOTAL AMOUNT'].mean()
        valor_mediano = df_reservas['TOTAL AMOUNT'].median()
        
        # Agrupar por fecha según período
        if periodo == 'D':
            df_reservas['fecha_grupo'] = df_reservas['fecha_trip'].dt.date
            agrupacion = 'diario'
        elif periodo == 'W':
            df_reservas['fecha_grupo'] = df_reservas['fecha_trip'] - pd.to_timedelta(df_reservas['fecha_trip'].dt.dayofweek, unit='D')
            agrupacion = 'semanal'
        else:  # 'M'
            df_reservas['fecha_grupo'] = df_reservas['fecha_trip'].dt.to_period('M').dt.to_timestamp()
            agrupacion = 'mensual'
        
        # Calcular valor promedio por período
        promedios_por_periodo = df_reservas.groupby('fecha_grupo')['TOTAL AMOUNT'].mean()
        
        # Analizar tendencia si hay suficientes datos
        if len(promedios_por_periodo) > 1:
            primera_mitad = promedios_por_periodo.iloc[:len(promedios_por_periodo)//2].mean()
            segunda_mitad = promedios_por_periodo.iloc[len(promedios_por_periodo)//2:].mean()
            
            tendencia = "creciente" if segunda_mitad > primera_mitad else "decreciente" if segunda_mitad < primera_mitad else "estable"
            cambio_porcentual = abs((segunda_mitad - primera_mitad) / primera_mitad * 100) if primera_mitad > 0 else 0
        else:
            tendencia = "no determinada"
            cambio_porcentual = 0
        
        # Generar insights
        insights = [
            f"El valor promedio de venta es ${valor_promedio:,.0f} CLP, con un valor mediano de ${valor_mediano:,.0f} CLP.",
            f"La tendencia del valor promedio es {tendencia}, con una variación del {cambio_porcentual:.1f}% entre la primera y segunda mitad del período."
        ]
        
        # Análisis por tipo de embarcación si está disponible
        if 'type boat' in df_reservas.columns:
            promedio_por_tipo = df_reservas.groupby('type boat')['TOTAL AMOUNT'].mean().sort_values(ascending=False)
            if not promedio_por_tipo.empty:
                tipo_max = promedio_por_tipo.index[0]
                tipo_min = promedio_por_tipo.index[-1]
                insights.append(f"La embarcación '{tipo_max}' genera el mayor valor promedio (${promedio_por_tipo.iloc[0]:,.0f} CLP), mientras que '{tipo_min}' genera el menor (${promedio_por_tipo.iloc[-1]:,.0f} CLP).")
        
        # Recomendación
        if tendencia == "decreciente" and cambio_porcentual > 5:
            insights.append("Recomendación: Evaluar la estrategia de precios o el mix de servicios, ya que el valor promedio de venta muestra una tendencia decreciente significativa.")
        elif tendencia == "creciente" and cambio_porcentual > 5:
            insights.append("Recomendación: Continuar con la estrategia actual que está logrando incrementar el valor promedio de venta.")
        else:
            insights.append("Recomendación: Considerar implementar estrategias de up-selling o cross-selling para incrementar el valor promedio de venta.")
        
        return html.Div([html.P(insight) for insight in insights])
    
    except Exception as e:
        return html.Div([html.P(f"No se pudieron generar insights: {str(e)}")])

# ======== APLICACIONES SEPARADAS ========
def crear_app_reservas(datos=None):
    """Crea la aplicación Dash para la página de reservas."""
    
    if datos is None:
        datos = cargar_datos()
        
    df = datos['reservas']
    df_payments = datos['pagos']
    df_expenses = datos['gastos']
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        crear_header(),
        html.Div([
            html.Div("DASHBOARD DE RESERVAS", style={
                'color': COLORS['primary'], 
                'fontSize': '24px', 
                'fontWeight': 'bold',
                'padding': '10px',
                'marginBottom': '20px',
                'textAlign': 'center',
                'backgroundColor': COLORS['card_bg'],
                'borderRadius': '5px'
            }),
            html.Div([
                html.A("Ver Dashboard de Utilidad Operativa", 
                      href="http://localhost:8051", 
                      style={'color': '#00a3ff', 'textDecoration': 'none', 'fontSize': '16px'},
                      target="_blank")
            ], style={'textAlign': 'center', 'marginBottom': '20px'})
        ]),
        crear_filtros(df['fecha_trip'].min(), df['fecha_trip'].max()),
        crear_tarjetas_metricas(),
        crear_selector_periodo(),
        crear_contenedor_grafico('reservas-tiempo'),
        crear_contenedor_insights('insights-reservas', 'Conclusiones: Tendencia de Reservas'),
        crear_contenedor_grafico('ingresos-tiempo'),
        crear_contenedor_insights('insights-financieros', 'Conclusiones: Análisis Financiero'),
        crear_contenedor_grafico('horas-populares', figura=crear_grafico_horas_populares(df)),
        crear_contenedor_insights('insights-horas', 'Conclusiones: Horas Populares'),
    ], style={
        'padding': 20,
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })
    
    @app.callback(
        [Output('reservas-tiempo', 'figure'),
         Output('ingresos-tiempo', 'figure'),
         Output('total-reservas', 'children'),
         Output('total-ingresos', 'children'),
         Output('total-gastos', 'children'),
         Output('balance', 'children'),
         Output('balance', 'style'),
         # Nuevos outputs para los insights
         Output('insights-reservas', 'children'),
         Output('insights-financieros', 'children'),
         Output('insights-horas', 'children')],
        [Input('periodo-selector', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date')]
    )
    def actualizar_graficos_reservas(periodo, start_date, end_date):
        # Filtrar DataFrames
        df_filtrado = df[(df['fecha_trip'] >= pd.to_datetime(start_date)) & (df['fecha_trip'] <= pd.to_datetime(end_date))]
        df_payments_filtrado = df_payments[(df_payments['Fecha'] >= pd.to_datetime(start_date)) & (df_payments['Fecha'] <= pd.to_datetime(end_date))]
        df_expenses_filtrado = df_expenses[(df_expenses['Fecha'] >= pd.to_datetime(start_date)) & (df_expenses['Fecha'] <= pd.to_datetime(end_date))]

        # Calcular métricas
        total_reservas_filtrado = len(df_filtrado)
        total_ingresos_filtrado = df_payments_filtrado['Monto'].sum()
        total_gastos_filtrado = df_expenses_filtrado['Monto'].sum()
        balance_filtrado = total_ingresos_filtrado - total_gastos_filtrado

        # Crear gráficos
        fig_reservas = crear_grafico_reservas(df_filtrado, periodo)
        fig_ingresos = crear_grafico_ingresos_gastos(df_payments_filtrado, df_expenses_filtrado, periodo)

        # Estilo del balance
        balance_style = {
            'color': COLORS['income'] if balance_filtrado >= 0 else COLORS['expense'],
            'fontSize': '2.5em',
            'margin': '0'
        }
        
        # Generar insights
        insights_reservas = generar_insights_reservas(df_filtrado, periodo)
        insights_financieros = generar_insights_ingresos_gastos(df_payments_filtrado, df_expenses_filtrado, periodo)
        insights_horas = generar_insights_horas_populares(df_filtrado)

        return (
            fig_reservas,
            fig_ingresos,
            f'{total_reservas_filtrado:,}',
            f'${total_ingresos_filtrado:,.0f}',
            f'${total_gastos_filtrado:,.0f}',
            f'${balance_filtrado:,.0f}',
            balance_style,
            insights_reservas,
            insights_financieros,
            insights_horas
        )
    
    return app

def crear_app_utilidad(datos=None):
    """Crea la aplicación Dash para la página de utilidad operativa."""
    
    if datos is None:
        datos = cargar_datos()
        
    df = datos['reservas']
    df_ingresos = datos['ingresos']
    df_costos_operativos = datos['costos_operativos']
    df_gastos_marketing = datos['gastos_marketing']
    df_costos_fijos = datos['costos_fijos']
    
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        crear_header(),
        html.Div([
            html.Div("DASHBOARD DE UTILIDAD OPERATIVA", style={
                'color': COLORS['income'], 
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
                      style={'color': '#00a3ff', 'textDecoration': 'none', 'fontSize': '16px'},
                      target="_blank")
            ], style={'textAlign': 'center', 'marginBottom': '20px'})
        ]),
        crear_filtros(df['fecha_trip'].min(), df['fecha_trip'].max()),
        html.Div([
            html.Div([
                html.H3('Ingresos Totales', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-ingresos-op', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Costos Operativos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-costos-op', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Gastos Marketing', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-marketing', style={'color': COLORS['expense'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Costos Fijos', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='total-costos-fijos', style={'color': '#9370db', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Utilidad Operativa', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='utilidad-operativa-valor', style={'color': COLORS['income'], 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
            html.Div([
                html.H3('Valor Promedio de Venta', style={'color': COLORS['text'], 'marginBottom': '10px'}),
                html.H2(id='avg-sale-value', style={'color': '#6AB187', 'fontSize': '2.5em', 'margin': '0'}),
            ], style=CARD_STYLE),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'}),
        crear_selector_periodo(),
        
        # Añadir controles de selección para el gráfico interactivo
        html.Div([
            html.H3("Seleccionar variables para el gráfico:", style={'color': COLORS['text'], 'marginBottom': '15px'}),
            dcc.Checklist(
                id='seleccion-variables',
                options=[
                    {'label': ' Ingresos Totales', 'value': 'ingresos'},
                    {'label': ' Costos Operativos', 'value': 'costos_operativos'},
                    {'label': ' Gastos Marketing', 'value': 'gastos_marketing'},
                    {'label': ' Costos Fijos', 'value': 'costos_fijos'}
                ],
                value=['ingresos', 'costos_operativos', 'gastos_marketing', 'costos_fijos'],  # Todos seleccionados por defecto
                inline=True,
                style={
                    'color': COLORS['text'],
                    'fontSize': '16px'
                },
                labelStyle={
                    'marginRight': '20px',
                    'display': 'inline-block',
                    'padding': '5px 10px',
                    'borderRadius': '5px',
                    'backgroundColor': COLORS['card_bg'],
                    'marginBottom': '10px'
                }
            )
        ], style={
            'backgroundColor': COLORS['accent'],
            'padding': '15px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'textAlign': 'center'
        }),
        
        # Gráfico interactivo
        crear_contenedor_grafico('grafico-interactivo', 'Análisis Financiero Interactivo'),
        crear_contenedor_insights('insights-interactivo', 'Conclusiones: Análisis Financiero'),
        
        # Gráfico original de utilidad operativa
        crear_contenedor_grafico('utilidad-operativa-chart', 'Análisis de Utilidad Operativa'),
        crear_contenedor_insights('insights-utilidad', 'Conclusiones: Utilidad Operativa'),
        
        # Nuevo gráfico de valor promedio de venta
        crear_contenedor_grafico('avg-sale-value-chart', 'Evolución del Valor Promedio de Venta'),
        crear_contenedor_insights('insights-avg-sale', 'Conclusiones: Valor Promedio de Venta'),
    ], style={
        'padding': 20,
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh'
    })
    
    @app.callback(
        [Output('utilidad-operativa-chart', 'figure'),
         Output('grafico-interactivo', 'figure'),
         Output('avg-sale-value-chart', 'figure'),
         Output('total-ingresos-op', 'children'),
         Output('total-costos-op', 'children'),
         Output('total-marketing', 'children'),
         Output('total-costos-fijos', 'children'),
         Output('utilidad-operativa-valor', 'children'),
         Output('utilidad-operativa-valor', 'style'),
         Output('avg-sale-value', 'children'),
         # Nuevos outputs para los insights
         Output('insights-interactivo', 'children'),
         Output('insights-utilidad', 'children'),
         Output('insights-avg-sale', 'children')],
        [Input('periodo-selector', 'value'),
         Input('date-range-picker', 'start_date'),
         Input('date-range-picker', 'end_date'),
         Input('seleccion-variables', 'value')]
    )
    def actualizar_graficos_utilidad(periodo, start_date, end_date, variables_seleccionadas):
        # Filtrar DataFrames
        df_ingresos_filtrado = df_ingresos[(df_ingresos['fecha'] >= pd.to_datetime(start_date)) & (df_ingresos['fecha'] <= pd.to_datetime(end_date))]
        df_costos_operativos_filtrado = df_costos_operativos[(df_costos_operativos['fecha'] >= pd.to_datetime(start_date)) & (df_costos_operativos['fecha'] <= pd.to_datetime(end_date))]
        df_gastos_marketing_filtrado = df_gastos_marketing[(df_gastos_marketing['fecha'] >= pd.to_datetime(start_date)) & (df_gastos_marketing['fecha'] <= pd.to_datetime(end_date))]
        df_costos_fijos_filtrado = df_costos_fijos[(df_costos_fijos['Fecha'] >= pd.to_datetime(start_date)) & (df_costos_fijos['Fecha'] <= pd.to_datetime(end_date))]
        df_filtrado = df[(df['fecha_trip'] >= pd.to_datetime(start_date)) & (df['fecha_trip'] <= pd.to_datetime(end_date))]

        # Calcular métricas
        total_ingresos = df_ingresos_filtrado['monto'].sum()
        total_costos_op = df_costos_operativos_filtrado['monto'].sum()
        total_marketing = df_gastos_marketing_filtrado['monto'].sum()
        total_costos_fijos = df_costos_fijos_filtrado['Monto'].sum()
        utilidad_operativa = total_ingresos - total_costos_op - total_marketing - total_costos_fijos
        
        # Calcular promedio de ventas
        df_filtrado['TOTAL AMOUNT'] = pd.to_numeric(df_filtrado['TOTAL AMOUNT'], errors='coerce')
        avg_sale = df_filtrado['TOTAL AMOUNT'].mean() if not df_filtrado.empty else 0

        # Crear gráfico tradicional de utilidad operativa
        fig_utilidad = crear_grafico_utilidad_operativa(
            df_ingresos_filtrado, 
            df_costos_operativos_filtrado, 
            df_gastos_marketing_filtrado, 
            periodo
        )
        
        # Crear gráfico interactivo con las variables seleccionadas
        fig_interactivo = crear_grafico_interactivo(
            df_ingresos_filtrado if 'ingresos' in variables_seleccionadas else None,
            df_costos_operativos_filtrado if 'costos_operativos' in variables_seleccionadas else None,
            df_gastos_marketing_filtrado if 'gastos_marketing' in variables_seleccionadas else None,
            df_costos_fijos_filtrado if 'costos_fijos' in variables_seleccionadas else None,
            periodo,
            variables_seleccionadas
        )
        
        # Crear gráfico de valor promedio de ventas
        fig_avg_sale = crear_grafico_avg_sale_value(
            df_filtrado,
            periodo
        )

        # Estilo de utilidad operativa
        utilidad_style = {
            'color': COLORS['income'] if utilidad_operativa >= 0 else COLORS['expense'],
            'fontSize': '2.5em',
            'margin': '0'
        }
        
        # Generar insights
        insights_utilidad = generar_insights_utilidad_operativa(
            df_ingresos_filtrado,
            df_costos_operativos_filtrado,
            df_gastos_marketing_filtrado,
            df_costos_fijos_filtrado,
            periodo
        )
        
        # Los insights interactivos son los mismos que los de utilidad operativa
        insights_interactivo = insights_utilidad
        
        # Insights para valor promedio de venta
        insights_avg_sale = generar_insights_valor_promedio_venta(df_filtrado, periodo)

        return (
            fig_utilidad,
            fig_interactivo,
            fig_avg_sale,
            f'${total_ingresos:,.0f}',
            f'${total_costos_op:,.0f}',
            f'${total_marketing:,.0f}',
            f'${total_costos_fijos:,.0f}',
            f'${utilidad_operativa:,.0f}',
            utilidad_style,
            f'${avg_sale:,.0f}',
            insights_interactivo,
            insights_utilidad,
            insights_avg_sale
        )
    
    return app

# ======== EJECUCIÓN DE LA APLICACIÓN ========
if __name__ == '__main__':
    # Por defecto, ejecutar la aplicación de reservas
    app = crear_app_reservas()
    print("\n=== DASHBOARD DE RESERVAS ===")
    print("Dashboard disponible en: http://localhost:8050")
    print("O alternativamente en: http://127.0.0.1:8050")
    print("\nPara ver el Dashboard de Utilidad Operativa, ejecute el archivo: python utilidad.py")
    app.run(debug=True, host='localhost', port=8050)