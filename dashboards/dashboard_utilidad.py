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
    
    datos = {}
    
    try:
        # Carga de datos de reservas
        if os.path.exists("archivos_output/reservas_HotBoat.csv"):
            df = pd.read_csv("archivos_output/reservas_HotBoat.csv")
            df["fecha_trip"] = pd.to_datetime(df["fecha_trip"])
            datos['reservas'] = df
        else:
            print("Archivo de reservas no encontrado, creando DataFrame vacío")
            datos['reservas'] = pd.DataFrame()
        
        # Carga de datos financieros
        if os.path.exists("archivos_output/abonos hotboat.csv"):
            df_payments = pd.read_csv("archivos_output/abonos hotboat.csv")
            df_payments["Fecha"] = pd.to_datetime(df_payments["Fecha"])
            df_payments["Monto"] = df_payments["Monto"].astype(float)
            datos['pagos'] = df_payments
        else:
            print("Archivo de abonos no encontrado, creando DataFrame vacío")
            datos['pagos'] = pd.DataFrame()
        
        if os.path.exists("archivos_output/gastos hotboat.csv"):
            df_expenses = pd.read_csv("archivos_output/gastos hotboat.csv")
            df_expenses["Fecha"] = pd.to_datetime(df_expenses["Fecha"])
            df_expenses["Monto"] = df_expenses["Monto"].astype(float)
            datos['gastos'] = df_expenses
            
            # Extraer costos fijos desde gastos
            if "Categoría 1" in df_expenses.columns:
                df_costos_fijos = df_expenses[df_expenses["Categoría 1"] == "Costos Fijos"].copy()
            else:
                df_costos_fijos = pd.DataFrame()
            datos['costos_fijos'] = df_costos_fijos
        else:
            print("Archivo de gastos no encontrado, creando DataFrame vacío")
            datos['gastos'] = pd.DataFrame()
            datos['costos_fijos'] = pd.DataFrame()
        
        # Datos para análisis de utilidad operativa
        if os.path.exists("archivos_output/ingresos_totales.csv"):
            df_ingresos = pd.read_csv("archivos_output/ingresos_totales.csv")
            df_ingresos["fecha"] = pd.to_datetime(df_ingresos["fecha"])
            datos['ingresos'] = df_ingresos
            print(f"✅ Ingresos cargados: {len(df_ingresos)} filas")
        else:
            print("❌ Archivo de ingresos totales no encontrado, creando DataFrame vacío")
            datos['ingresos'] = pd.DataFrame()
        
        if os.path.exists("archivos_output/costos_operativos.csv"):
            df_costos_operativos = pd.read_csv("archivos_output/costos_operativos.csv")
            df_costos_operativos["fecha"] = pd.to_datetime(df_costos_operativos["fecha"])
            datos['costos_operativos'] = df_costos_operativos
            print(f"✅ Costos operativos cargados: {len(df_costos_operativos)} filas")
        else:
            print("❌ Archivo de costos operativos no encontrado, creando DataFrame vacío")
            datos['costos_operativos'] = pd.DataFrame()
        
        if os.path.exists("archivos_output/gastos_marketing.csv"):
            df_gastos_marketing = pd.read_csv("archivos_output/gastos_marketing.csv")
            df_gastos_marketing["fecha"] = pd.to_datetime(df_gastos_marketing["fecha"])
            datos['gastos_marketing'] = df_gastos_marketing
            print(f"✅ Gastos marketing cargados: {len(df_gastos_marketing)} filas")
        else:
            print("❌ Archivo de gastos marketing no encontrado, creando DataFrame vacío")
            datos['gastos_marketing'] = pd.DataFrame()
        
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        # Crear DataFrames vacíos como fallback
        for key in ['reservas', 'pagos', 'gastos', 'costos_fijos', 'ingresos', 'costos_operativos', 'gastos_marketing']:
            if key not in datos:
                datos[key] = pd.DataFrame()
    
    return datos

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
            marker_color=colores_categoria[categoria]
        ))
    
    # Configurar layout
    fig.update_layout(
        title=titulo,
        xaxis_title='Período',
        yaxis_title='Monto (CLP)',
        barmode='group',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def crear_grafico_avg_sale_value(df_reservas, periodo):
    """Crea un gráfico de valor promedio de venta agrupado por período."""
    
    # Filtrar datos válidos
    df_filtered = df_reservas.dropna(subset=['precio_total', 'fecha_trip'])
    
    if df_filtered.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos suficientes para mostrar el gráfico",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="Valor Promedio de Venta por Período",
            template='plotly_white',
            height=400
        )
        return fig
    
    # Agrupar según el periodo
    if periodo == 'D':
        df_filtered['periodo'] = df_filtered['fecha_trip'].dt.date
        titulo = 'Valor Promedio de Venta por Día'
    elif periodo == 'W':
        df_filtered['periodo'] = df_filtered['fecha_trip'] - pd.to_timedelta(df_filtered['fecha_trip'].dt.dayofweek, unit='D')
        titulo = 'Valor Promedio de Venta por Semana'
    else:  # 'M'
        df_filtered['periodo'] = df_filtered['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        titulo = 'Valor Promedio de Venta por Mes'
    
    # Calcular valor promedio por período
    avg_sale_by_period = df_filtered.groupby('periodo')['precio_total'].mean().reset_index()
    
    # Crear gráfico de línea
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=avg_sale_by_period['periodo'],
        y=avg_sale_by_period['precio_total'],
        mode='lines+markers',
        name='Valor Promedio',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=6)
    ))
    
    # Configurar layout
    fig.update_layout(
        title=titulo,
        xaxis_title='Período',
        yaxis_title='Valor Promedio (CLP)',
        template='plotly_white',
        hovermode='x unified',
        height=400
    )
    
    return fig

def generar_insights_utilidad_operativa(df_ingresos, df_costos_operativos, df_gastos_marketing, df_costos_fijos, periodo):
    """Genera insights automáticos para la utilidad operativa."""
    
    insights = []
    
    # Calcular totales
    total_ingresos = df_ingresos['monto'].sum() if df_ingresos is not None else 0
    total_costos_op = df_costos_operativos['monto'].sum() if df_costos_operativos is not None else 0
    total_marketing = df_gastos_marketing['monto'].sum() if df_gastos_marketing is not None else 0
    total_costos_fijos = df_costos_fijos['Monto'].sum() if df_costos_fijos is not None else 0
    
    utilidad_operativa = total_ingresos - total_costos_op - total_marketing - total_costos_fijos
    margen_operativo = (utilidad_operativa / total_ingresos * 100) if total_ingresos > 0 else 0
    
    # Insight 1: Estado general de la utilidad
    if utilidad_operativa > 0:
        insights.append(f"✅ La empresa genera una utilidad operativa positiva de ${utilidad_operativa:,.0f} CLP")
        if margen_operativo > 20:
            insights.append(f"🎯 Excelente margen operativo del {margen_operativo:.1f}%")
        elif margen_operativo > 10:
            insights.append(f"✔️ Buen margen operativo del {margen_operativo:.1f}%")
        else:
            insights.append(f"⚠️ Margen operativo bajo del {margen_operativo:.1f}%")
    else:
        insights.append(f"⚠️ La empresa tiene pérdidas operativas de ${abs(utilidad_operativa):,.0f} CLP")
    
    # Insight 2: Análisis de costos
    total_costos = total_costos_op + total_marketing + total_costos_fijos
    if total_costos > 0:
        porcentaje_costos_op = (total_costos_op / total_costos) * 100
        porcentaje_marketing = (total_marketing / total_costos) * 100
        porcentaje_costos_fijos = (total_costos_fijos / total_costos) * 100
        
        insights.append(f"📊 Distribución de costos: Operativos {porcentaje_costos_op:.1f}%, Marketing {porcentaje_marketing:.1f}%, Fijos {porcentaje_costos_fijos:.1f}%")
        
        # Identificar el mayor componente de costos
        if porcentaje_costos_op > porcentaje_marketing and porcentaje_costos_op > porcentaje_costos_fijos:
            insights.append("⚡ Los costos operativos son el mayor componente. Revisa la eficiencia operacional.")
        elif porcentaje_marketing > porcentaje_costos_fijos:
            insights.append("📢 Los gastos de marketing son significativos. Evalúa el ROI de las campañas.")
        else:
            insights.append("🏢 Los costos fijos representan una parte importante. Considera optimizaciones estructurales.")
    
    # Insight 3: Tendencia por período
    if periodo != 'D' and df_ingresos is not None and len(df_ingresos) > 1:
        # Agrupar por período
        if periodo == 'W':
            df_ingresos['periodo'] = df_ingresos['fecha'] - pd.to_timedelta(df_ingresos['fecha'].dt.dayofweek, unit='D')
        else:  # 'M'
            df_ingresos['periodo'] = df_ingresos['fecha'].dt.to_period('M').dt.to_timestamp()
        
        ingresos_por_periodo = df_ingresos.groupby('periodo')['monto'].sum()
        
        if len(ingresos_por_periodo) >= 2:
            ultimo_periodo = ingresos_por_periodo.iloc[-1]
            penultimo_periodo = ingresos_por_periodo.iloc[-2]
            
            if ultimo_periodo > penultimo_periodo:
                crecimiento = ((ultimo_periodo - penultimo_periodo) / penultimo_periodo) * 100
                insights.append(f"📈 Los ingresos crecieron {crecimiento:.1f}% en el último período")
            else:
                decrecimiento = ((penultimo_periodo - ultimo_periodo) / penultimo_periodo) * 100
                insights.append(f"📉 Los ingresos bajaron {decrecimiento:.1f}% en el último período")
    
    return insights

def generar_insights_valor_promedio_venta(df_reservas, periodo):
    """Genera insights automáticos para el valor promedio de venta."""
    
    insights = []
    
    # Filtrar datos válidos
    df_filtered = df_reservas.dropna(subset=['precio_total', 'fecha_trip'])
    
    if df_filtered.empty:
        insights.append("ℹ️ No hay datos suficientes para generar insights")
        return insights
    
    # Calcular valor promedio general
    valor_promedio_general = df_filtered['precio_total'].mean()
    insights.append(f"💰 Valor promedio de venta general: ${valor_promedio_general:,.0f} CLP")
    
    # Agrupar por período
    if periodo == 'D':
        df_filtered['periodo'] = df_filtered['fecha_trip'].dt.date
        nombre_periodo = 'día'
    elif periodo == 'W':
        df_filtered['periodo'] = df_filtered['fecha_trip'] - pd.to_timedelta(df_filtered['fecha_trip'].dt.dayofweek, unit='D')
        nombre_periodo = 'semana'
    else:  # 'M'
        df_filtered['periodo'] = df_filtered['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        nombre_periodo = 'mes'
    
    # Analizar tendencia
    avg_by_period = df_filtered.groupby('periodo')['precio_total'].mean()
    
    if len(avg_by_period) >= 2:
        ultimo_valor = avg_by_period.iloc[-1]
        penultimo_valor = avg_by_period.iloc[-2]
        
        if ultimo_valor > penultimo_valor:
            crecimiento = ((ultimo_valor - penultimo_valor) / penultimo_valor) * 100
            insights.append(f"📈 El valor promedio aumentó {crecimiento:.1f}% en el último {nombre_periodo}")
        elif ultimo_valor < penultimo_valor:
            decrecimiento = ((penultimo_valor - ultimo_valor) / penultimo_valor) * 100
            insights.append(f"📉 El valor promedio bajó {decrecimiento:.1f}% en el último {nombre_periodo}")
        else:
            insights.append(f"📊 El valor promedio se mantiene estable")
    
    # Analizar variabilidad
    desviacion_estandar = df_filtered['precio_total'].std()
    coeficiente_variacion = (desviacion_estandar / valor_promedio_general) * 100
    
    if coeficiente_variacion < 20:
        insights.append("✅ Los precios son muy consistentes")
    elif coeficiente_variacion < 40:
        insights.append("📊 Los precios tienen variabilidad moderada")
    else:
        insights.append("⚠️ Los precios tienen alta variabilidad. Considera estrategias de pricing")
    
    # Identificar el rango de precios más común
    q1 = df_filtered['precio_total'].quantile(0.25)
    q3 = df_filtered['precio_total'].quantile(0.75)
    insights.append(f"📊 El 50% de las ventas están entre ${q1:,.0f} y ${q3:,.0f} CLP")
    
    return insights

# ======== APLICACIÓN PRINCIPAL ========
def crear_app_utilidad(datos=None):
    """Crea la aplicación Dash para análisis de utilidad operativa."""
    
    # Inicializar la aplicación
    app = dash.Dash(__name__)
    
    # Cargar datos si no se proporcionan
    if datos is None:
        try:
            datos = cargar_datos()
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            datos = {}
    
    # Definir layout
    app.layout = html.Div([
        crear_header("Dashboard de Marketing HotBoat", 8056),
        
        # Controles principales
        html.Div([
            html.Div([
                crear_selector_periodo()
            ], className="col-md-6"),
            
            html.Div([
                html.Label("Rango de fechas:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    start_date='2024-08-01',  # Fecha inicio por defecto
                    end_date='2025-12-31',   # Fecha fin por defecto
                    display_format='DD/MM/YYYY',
                    style={'width': '100%'}
                )
            ], className="col-md-6")
        ], className="row mb-4"),
        
        # Selector de variables para gráfico interactivo
        html.Div([
            html.Label("Selecciona las variables a mostrar:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Checklist(
                id='seleccion-variables',
                options=[
                    {'label': ' Ingresos Totales', 'value': 'ingresos'},
                    {'label': ' Costos Operativos', 'value': 'costos_operativos'},
                    {'label': ' Gastos Marketing', 'value': 'gastos_marketing'},
                    {'label': ' Costos Fijos', 'value': 'costos_fijos'}
                ],
                value=['ingresos', 'costos_operativos'],
                inline=True,
                style={'marginBottom': '20px'}
            )
        ], className="mb-4"),
        
        # Tarjetas de métricas
        html.Div([
            html.Div([
                html.Div([
                    html.H4("Total Ingresos", className="card-title", style={'fontSize': '14px', 'marginBottom': '5px'}),
                    html.H2(id="total-ingresos-op", className="card-value text-success", style={'fontSize': '20px', 'margin': '0'})
                ], className="card-body text-center")
            ], className="card", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Costos Operativos", className="card-title", style={'fontSize': '14px', 'marginBottom': '5px'}),
                    html.H2(id="total-costos-op", className="card-value text-warning", style={'fontSize': '20px', 'margin': '0'})
                ], className="card-body text-center")
            ], className="card", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Gastos Marketing", className="card-title", style={'fontSize': '14px', 'marginBottom': '5px'}),
                    html.H2(id="total-marketing", className="card-value text-info", style={'fontSize': '20px', 'margin': '0'})
                ], className="card-body text-center")
            ], className="card", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Costos Fijos", className="card-title", style={'fontSize': '14px', 'marginBottom': '5px'}),
                    html.H2(id="total-costos-fijos", className="card-value text-secondary", style={'fontSize': '20px', 'margin': '0'})
                ], className="card-body text-center")
            ], className="card", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Utilidad Operativa", className="card-title", style={'fontSize': '14px', 'marginBottom': '5px'}),
                    html.H2(id="utilidad-operativa-valor", className="card-value", style={'fontSize': '20px', 'margin': '0'})
                ], className="card-body text-center")
            ], className="card", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Valor Promedio Venta", className="card-title", style={'fontSize': '14px', 'marginBottom': '5px'}),
                    html.H2(id="avg-sale-value", className="card-value text-primary", style={'fontSize': '20px', 'margin': '0'})
                ], className="card-body text-center")
            ], className="card", style=CARD_STYLE)
        ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'gap': '10px', 'marginBottom': '30px'}),
        
        # Gráficos
        html.Div([
            # Gráfico de utilidad operativa
            html.Div([
                crear_contenedor_grafico("Utilidad Operativa por Período", "utilidad-operativa-chart"),
                crear_contenedor_insights("insights-utilidad")
            ], className="col-md-6"),
            
            # Gráfico interactivo
            html.Div([
                crear_contenedor_grafico("Análisis Financiero Interactivo", "grafico-interactivo"),
                crear_contenedor_insights("insights-interactivo")
            ], className="col-md-6")
        ], className="row mb-4"),
        
        # Gráfico de valor promedio de venta
        html.Div([
            html.Div([
                crear_contenedor_grafico("Valor Promedio de Venta", "avg-sale-value-chart"),
                crear_contenedor_insights("insights-avg-sale")
            ], className="col-md-12")
        ], className="row")
    ], className="container-fluid")
    
    # Callback principal
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
        print(f"=== DEBUG CALLBACK ===")
        print(f"Período: {periodo}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")
        print(f"Datos disponibles: {list(datos.keys()) if datos else 'No hay datos'}")
        
        # Verificar datos al inicio
        if datos.get('ingresos') is not None:
            print(f"Ingresos disponibles: {len(datos['ingresos'])} filas")
        else:
            print("❌ No hay datos de ingresos")
            
        if datos.get('costos_operativos') is not None:
            print(f"Costos operativos disponibles: {len(datos['costos_operativos'])} filas")
        else:
            print("❌ No hay datos de costos operativos")
            
        if datos.get('gastos_marketing') is not None:
            print(f"Gastos marketing disponibles: {len(datos['gastos_marketing'])} filas")
        else:
            print("❌ No hay datos de gastos marketing")
        
        # Filtrar DataFrames
        df_ingresos_filtrado = datos.get('ingresos')
        df_costos_operativos_filtrado = datos.get('costos_operativos')
        df_gastos_marketing_filtrado = datos.get('gastos_marketing')
        df_costos_fijos_filtrado = datos.get('costos_fijos')
        df_reservas_filtrado = datos.get('reservas')
        
        # Aplicar filtros de fecha
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
            if df_ingresos_filtrado is not None:
                df_ingresos_filtrado = df_ingresos_filtrado[
                    (df_ingresos_filtrado['fecha'] >= start_date) & 
                    (df_ingresos_filtrado['fecha'] <= end_date)
                ].copy()
            
            if df_costos_operativos_filtrado is not None:
                df_costos_operativos_filtrado = df_costos_operativos_filtrado[
                    (df_costos_operativos_filtrado['fecha'] >= start_date) & 
                    (df_costos_operativos_filtrado['fecha'] <= end_date)
                ].copy()
            
            if df_gastos_marketing_filtrado is not None:
                df_gastos_marketing_filtrado = df_gastos_marketing_filtrado[
                    (df_gastos_marketing_filtrado['fecha'] >= start_date) & 
                    (df_gastos_marketing_filtrado['fecha'] <= end_date)
                ].copy()
            
            if df_costos_fijos_filtrado is not None:
                df_costos_fijos_filtrado = df_costos_fijos_filtrado[
                    (df_costos_fijos_filtrado['Fecha'] >= start_date) & 
                    (df_costos_fijos_filtrado['Fecha'] <= end_date)
                ].copy()
            
            if df_reservas_filtrado is not None:
                df_reservas_filtrado = df_reservas_filtrado[
                    (df_reservas_filtrado['fecha_trip'] >= start_date) & 
                    (df_reservas_filtrado['fecha_trip'] <= end_date)
                ].copy()
        
        # Crear gráficos
        fig_utilidad = crear_grafico_utilidad_operativa(
            df_ingresos_filtrado, df_costos_operativos_filtrado, 
            df_gastos_marketing_filtrado, df_costos_fijos_filtrado, periodo
        )
        
        fig_interactivo = crear_grafico_interactivo(
            df_ingresos_filtrado, df_costos_operativos_filtrado,
            df_gastos_marketing_filtrado, df_costos_fijos_filtrado, 
            periodo, variables_seleccionadas
        )
        
        fig_avg_sale = crear_grafico_avg_sale_value(df_reservas_filtrado, periodo)
        
        # Calcular métricas
        total_ingresos = 0
        total_costos_op = 0
        total_marketing = 0
        total_costos_fijos = 0
        
        print(f"=== DEBUG MÉTRICAS ===")
        
        if df_ingresos_filtrado is not None and not df_ingresos_filtrado.empty:
            total_ingresos = df_ingresos_filtrado['monto'].sum()
            print(f"Total ingresos calculado: {total_ingresos}")
        else:
            print("❌ No hay datos de ingresos para calcular")
        
        if df_costos_operativos_filtrado is not None and not df_costos_operativos_filtrado.empty:
            total_costos_op = df_costos_operativos_filtrado['monto'].sum()
            print(f"Total costos operativos calculado: {total_costos_op}")
        else:
            print("❌ No hay datos de costos operativos para calcular")
        
        if df_gastos_marketing_filtrado is not None and not df_gastos_marketing_filtrado.empty:
            total_marketing = df_gastos_marketing_filtrado['monto'].sum()
            print(f"Total gastos marketing calculado: {total_marketing}")
        else:
            print("❌ No hay datos de gastos marketing para calcular")
        
        if df_costos_fijos_filtrado is not None and not df_costos_fijos_filtrado.empty:
            total_costos_fijos = df_costos_fijos_filtrado['Monto'].sum()
            print(f"Total costos fijos calculado: {total_costos_fijos}")
        else:
            print("❌ No hay datos de costos fijos para calcular")
        
        utilidad_operativa = total_ingresos - total_costos_op - total_marketing - total_costos_fijos
        print(f"Utilidad operativa calculada: {utilidad_operativa}")
        
        # Valor promedio de venta
        avg_sale_value = 0
        if df_reservas_filtrado is not None and not df_reservas_filtrado.empty and 'precio_total' in df_reservas_filtrado.columns:
            avg_sale_value = df_reservas_filtrado['precio_total'].mean()
            print(f"Valor promedio de venta calculado: {avg_sale_value}")
        else:
            print("❌ No hay datos de reservas para calcular valor promedio")
        
        # Formato de números
        total_ingresos_fmt = f"${total_ingresos:,.0f}"
        total_costos_op_fmt = f"${total_costos_op:,.0f}"
        total_marketing_fmt = f"${total_marketing:,.0f}"
        total_costos_fijos_fmt = f"${total_costos_fijos:,.0f}"
        utilidad_operativa_fmt = f"${utilidad_operativa:,.0f}"
        avg_sale_value_fmt = f"${avg_sale_value:,.0f}"
        
        print(f"Valores formateados:")
        print(f"- Ingresos: {total_ingresos_fmt}")
        print(f"- Costos Op: {total_costos_op_fmt}")
        print(f"- Marketing: {total_marketing_fmt}")
        print(f"- Costos Fijos: {total_costos_fijos_fmt}")
        print(f"- Utilidad: {utilidad_operativa_fmt}")
        print(f"- Avg Sale: {avg_sale_value_fmt}")
        print("=== FIN DEBUG MÉTRICAS ===")
        
        # Estilo para utilidad operativa
        utilidad_style = {'color': 'green'} if utilidad_operativa > 0 else {'color': 'red'}
        
        # Generar insights
        insights_interactivo = ["📊 Selecciona diferentes variables para comparar tendencias"] if variables_seleccionadas else ["ℹ️ Selecciona al menos una variable para mostrar insights"]
        insights_utilidad = generar_insights_utilidad_operativa(df_ingresos_filtrado, df_costos_operativos_filtrado, df_gastos_marketing_filtrado, df_costos_fijos_filtrado, periodo)
        insights_avg_sale = generar_insights_valor_promedio_venta(df_reservas_filtrado, periodo)
        
        return (
            fig_utilidad, fig_interactivo, fig_avg_sale,
            total_ingresos_fmt, total_costos_op_fmt, total_marketing_fmt, total_costos_fijos_fmt,
            utilidad_operativa_fmt, utilidad_style, avg_sale_value_fmt,
            [html.Li(insight) for insight in insights_interactivo],
            [html.Li(insight) for insight in insights_utilidad],
            [html.Li(insight) for insight in insights_avg_sale]
        )
    
    return app

# ======== EJECUTAR APLICACIÓN ========
if __name__ == '__main__':
    print("=== CARGANDO DASHBOARD DE UTILIDAD OPERATIVA ===")
    try:
        # Cargar datos primero
        datos = cargar_datos()
        
        # Crear app con los datos
        app = crear_app_utilidad(datos)
        print("Dashboard de utilidad iniciado exitosamente")
        print("Accede en: http://localhost:8055")
        app.run(debug=True, host='localhost', port=8055)
    except Exception as e:
        print(f"Error al iniciar dashboard de utilidad: {e}") 