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

# ======== FUNCIONES PARA INSIGHTS ========
def generar_insights_reservas(df_reservas, periodo):
    """Genera insights automáticos para reservas."""
    
    insights = []
    
    # Verificar si hay datos
    if df_reservas.empty:
        insights.append("ℹ️ No hay datos de reservas en el período seleccionado")
        return insights
    
    # Insight 1: Total de reservas
    total_reservas = len(df_reservas)
    insights.append(f"📊 Total de reservas en el período: {total_reservas}")
    
    # Insight 2: Tendencia por período
    if periodo == 'D':
        df_reservas['periodo'] = df_reservas['fecha_trip'].dt.date
        nombre_periodo = 'día'
    elif periodo == 'W':
        df_reservas['periodo'] = df_reservas['fecha_trip'] - pd.to_timedelta(df_reservas['fecha_trip'].dt.dayofweek, unit='D')
        nombre_periodo = 'semana'
    else:  # 'M'
        df_reservas['periodo'] = df_reservas['fecha_trip'].dt.to_period('M').dt.to_timestamp()
        nombre_periodo = 'mes'
    
    reservas_por_periodo = df_reservas.groupby('periodo').size()
    
    if len(reservas_por_periodo) >= 2:
        ultimo_periodo = reservas_por_periodo.iloc[-1]
        penultimo_periodo = reservas_por_periodo.iloc[-2]
        
        if ultimo_periodo > penultimo_periodo:
            crecimiento = ((ultimo_periodo - penultimo_periodo) / penultimo_periodo) * 100
            insights.append(f"📈 Las reservas crecieron {crecimiento:.1f}% en el último {nombre_periodo}")
        elif ultimo_periodo < penultimo_periodo:
            decrecimiento = ((penultimo_periodo - ultimo_periodo) / penultimo_periodo) * 100
            insights.append(f"📉 Las reservas bajaron {decrecimiento:.1f}% en el último {nombre_periodo}")
        else:
            insights.append(f"📊 Las reservas se mantienen estables")
    
    # Insight 3: Promedio de reservas por período
    promedio_reservas = reservas_por_periodo.mean()
    insights.append(f"📊 Promedio de reservas por {nombre_periodo}: {promedio_reservas:.1f}")
    
    # Insight 4: Mejor y peor período
    if len(reservas_por_periodo) > 1:
        mejor_periodo = reservas_por_periodo.idxmax()
        peor_periodo = reservas_por_periodo.idxmin()
        insights.append(f"🎯 Mejor {nombre_periodo}: {mejor_periodo.strftime('%d/%m/%Y') if hasattr(mejor_periodo, 'strftime') else mejor_periodo} ({reservas_por_periodo.max()} reservas)")
        insights.append(f"⚠️ Peor {nombre_periodo}: {peor_periodo.strftime('%d/%m/%Y') if hasattr(peor_periodo, 'strftime') else peor_periodo} ({reservas_por_periodo.min()} reservas)")
    
    return insights

def generar_insights_ingresos_gastos(df_payments, df_expenses, periodo):
    """Genera insights automáticos para ingresos y gastos."""
    
    insights = []
    
    # Calcular totales
    total_ingresos = df_payments['Monto'].sum() if not df_payments.empty else 0
    total_gastos = df_expenses['Monto'].sum() if not df_expenses.empty else 0
    balance = total_ingresos - total_gastos
    
    # Insight 1: Balance general
    if balance > 0:
        insights.append(f"✅ Balance positivo de ${balance:,.0f} CLP")
    elif balance < 0:
        insights.append(f"⚠️ Balance negativo de ${abs(balance):,.0f} CLP")
    else:
        insights.append("📊 Balance equilibrado (ingresos = gastos)")
    
    # Insight 2: Distribución ingresos vs gastos
    if total_ingresos > 0 and total_gastos > 0:
        ratio_gastos = (total_gastos / total_ingresos) * 100
        insights.append(f"📊 Los gastos representan el {ratio_gastos:.1f}% de los ingresos")
        
        if ratio_gastos < 60:
            insights.append("✅ Excelente control de gastos")
        elif ratio_gastos < 80:
            insights.append("👍 Buen control de gastos")
        else:
            insights.append("⚠️ Los gastos son muy altos. Revisar optimizaciones.")
    
    # Insight 3: Análisis por categorías de gastos (si existen)
    if not df_expenses.empty and 'Categoría 1' in df_expenses.columns:
        gastos_por_categoria = df_expenses.groupby('Categoría 1')['Monto'].sum()
        categoria_mayor = gastos_por_categoria.idxmax()
        monto_mayor = gastos_por_categoria.max()
        porcentaje_mayor = (monto_mayor / total_gastos) * 100
        
        insights.append(f"💰 Mayor categoría de gasto: {categoria_mayor} (${monto_mayor:,.0f} - {porcentaje_mayor:.1f}%)")
    
    # Insight 4: Tendencia de ingresos (si hay datos suficientes)
    if not df_payments.empty:
        if periodo == 'D':
            df_payments['periodo'] = df_payments['Fecha'].dt.date
        elif periodo == 'W':
            df_payments['periodo'] = df_payments['Fecha'] - pd.to_timedelta(df_payments['Fecha'].dt.dayofweek, unit='D')
        else:  # 'M'
            df_payments['periodo'] = df_payments['Fecha'].dt.to_period('M').dt.to_timestamp()
        
        ingresos_por_periodo = df_payments.groupby('periodo')['Monto'].sum()
        
        if len(ingresos_por_periodo) >= 2:
            ultimo_ingreso = ingresos_por_periodo.iloc[-1]
            penultimo_ingreso = ingresos_por_periodo.iloc[-2]
            
            if ultimo_ingreso > penultimo_ingreso:
                crecimiento = ((ultimo_ingreso - penultimo_ingreso) / penultimo_ingreso) * 100
                insights.append(f"📈 Los ingresos crecieron {crecimiento:.1f}% en el último período")
            elif ultimo_ingreso < penultimo_ingreso:
                decrecimiento = ((penultimo_ingreso - ultimo_ingreso) / penultimo_ingreso) * 100
                insights.append(f"📉 Los ingresos bajaron {decrecimiento:.1f}% en el último período")
    
    return insights

def generar_insights_horas_populares(df):
    """Genera insights automáticos para horas populares."""
    
    insights = []
    
    if df.empty:
        insights.append("ℹ️ No hay datos suficientes para analizar horas populares")
        return insights
    
    # Extraer hora de la fecha de trip
    if 'fecha_trip' in df.columns:
        df['hora'] = df['fecha_trip'].dt.hour
        horas_populares = df['hora'].value_counts().sort_index()
        
        if not horas_populares.empty:
            hora_mas_popular = horas_populares.idxmax()
            reservas_hora_popular = horas_populares.max()
            
            insights.append(f"🕒 Hora más popular: {hora_mas_popular}:00 hrs ({reservas_hora_popular} reservas)")
            
            # Analizar distribución por franjas horarias
            df['franja'] = pd.cut(df['hora'], bins=[0, 6, 12, 18, 24], labels=['Madrugada (0-6)', 'Mañana (6-12)', 'Tarde (12-18)', 'Noche (18-24)'])
            franjas_populares = df['franja'].value_counts()
            
            if not franjas_populares.empty:
                franja_mas_popular = franjas_populares.idxmax()
                reservas_franja_popular = franjas_populares.max()
                insights.append(f"🌅 Franja más popular: {franja_mas_popular} ({reservas_franja_popular} reservas)")
    
    return insights

# ======== APLICACIÓN PRINCIPAL ========
def crear_app_reservas(datos=None):
    """Crea la aplicación Dash para análisis de reservas y finanzas."""
    
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
        crear_header("Dashboard de Reservas y Finanzas HotBoat"),
        
        # Controles principales
        html.Div([
            html.Div([
                crear_selector_periodo()
            ], className="col-md-6"),
            
            html.Div([
                html.Label("Rango de fechas:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.DatePickerRange(
                    id='date-range-picker',
                    display_format='DD/MM/YYYY',
                    style={'width': '100%'}
                )
            ], className="col-md-6")
        ], className="row mb-4"),
        
        # Tarjetas de métricas principales
        html.Div([
            html.Div([
                html.Div([
                    html.H4("Total Reservas", className="card-title"),
                    html.H2(id="total-reservas", className="card-value text-primary")
                ], className="card-body text-center")
            ], className="card col-md-3", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Total Ingresos", className="card-title"),
                    html.H2(id="total-ingresos", className="card-value text-success")
                ], className="card-body text-center")
            ], className="card col-md-3", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Total Gastos", className="card-title"),
                    html.H2(id="total-gastos", className="card-value text-warning")
                ], className="card-body text-center")
            ], className="card col-md-3", style=CARD_STYLE),
            
            html.Div([
                html.Div([
                    html.H4("Balance", className="card-title"),
                    html.H2(id="balance", className="card-value")
                ], className="card-body text-center")
            ], className="card col-md-3", style=CARD_STYLE)
        ], className="row mb-4"),
        
        # Gráficos principales
        html.Div([
            # Gráfico de reservas por tiempo
            html.Div([
                crear_contenedor_grafico("Reservas por Período", "reservas-tiempo"),
                crear_contenedor_insights("insights-reservas")
            ], className="col-md-6"),
            
            # Gráfico de ingresos por tiempo
            html.Div([
                crear_contenedor_grafico("Análisis Financiero", "ingresos-tiempo"),
                crear_contenedor_insights("insights-financieros")
            ], className="col-md-6")
        ], className="row mb-4"),
        
        # Gráfico de horas populares
        html.Div([
            html.Div([
                crear_contenedor_grafico("Horas Populares para Reservas", "horas-populares"),
                crear_contenedor_insights("insights-horas")
            ], className="col-md-12")
        ], className="row")
    ], className="container-fluid")
    
    # Callback principal
    @app.callback(
        [Output('reservas-tiempo', 'figure'),
         Output('ingresos-tiempo', 'figure'),
         Output('horas-populares', 'figure'),
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
        df_reservas_filtrado = datos.get('reservas')
        df_payments_filtrado = datos.get('pagos')
        df_expenses_filtrado = datos.get('gastos')
        
        # Aplicar filtros de fecha
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            
            if df_reservas_filtrado is not None:
                df_reservas_filtrado = df_reservas_filtrado[
                    (df_reservas_filtrado['fecha_trip'] >= start_date) & 
                    (df_reservas_filtrado['fecha_trip'] <= end_date)
                ].copy()
            
            if df_payments_filtrado is not None:
                df_payments_filtrado = df_payments_filtrado[
                    (df_payments_filtrado['Fecha'] >= start_date) & 
                    (df_payments_filtrado['Fecha'] <= end_date)
                ].copy()
            
            if df_expenses_filtrado is not None:
                df_expenses_filtrado = df_expenses_filtrado[
                    (df_expenses_filtrado['Fecha'] >= start_date) & 
                    (df_expenses_filtrado['Fecha'] <= end_date)
                ].copy()
        
        # Crear gráficos
        fig_reservas = crear_grafico_reservas(df_reservas_filtrado, periodo)
        fig_ingresos = crear_grafico_ingresos_gastos(df_payments_filtrado, df_expenses_filtrado, periodo)
        fig_horas = crear_grafico_horas_populares(df_reservas_filtrado)
        
        # Calcular métricas
        total_reservas = len(df_reservas_filtrado) if df_reservas_filtrado is not None else 0
        total_ingresos = df_payments_filtrado['Monto'].sum() if df_payments_filtrado is not None and not df_payments_filtrado.empty else 0
        total_gastos = df_expenses_filtrado['Monto'].sum() if df_expenses_filtrado is not None and not df_expenses_filtrado.empty else 0
        balance = total_ingresos - total_gastos
        
        # Formato de números
        total_ingresos_fmt = f"${total_ingresos:,.0f}"
        total_gastos_fmt = f"${total_gastos:,.0f}"
        balance_fmt = f"${balance:,.0f}"
        
        # Estilo para balance
        balance_style = {'color': 'green'} if balance > 0 else {'color': 'red'} if balance < 0 else {'color': 'gray'}
        
        # Generar insights
        insights_reservas = generar_insights_reservas(df_reservas_filtrado, periodo)
        insights_financieros = generar_insights_ingresos_gastos(df_payments_filtrado, df_expenses_filtrado, periodo)
        insights_horas = generar_insights_horas_populares(df_reservas_filtrado)
        
        return (
            fig_reservas, fig_ingresos, fig_horas,
            str(total_reservas), total_ingresos_fmt, total_gastos_fmt, balance_fmt, balance_style,
            [html.Li(insight) for insight in insights_reservas],
            [html.Li(insight) for insight in insights_financieros],
            [html.Li(insight) for insight in insights_horas]
        )
    
    return app

# ======== EJECUTAR APLICACIÓN ========
if __name__ == '__main__':
    print("=== CARGANDO DASHBOARD DE RESERVAS Y FINANZAS ===")
    try:
        # Cargar datos primero
        datos = cargar_datos()
        
        # Crear app con los datos
        app = crear_app_reservas(datos)
        print("Dashboard de reservas iniciado exitosamente")
        print("Accede en: http://localhost:8056")
        app.run(debug=True, host='localhost', port=8056)
    except Exception as e:
        print(f"Error al iniciar dashboard de reservas: {e}") 