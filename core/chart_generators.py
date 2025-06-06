#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOTBOAT - Generadores de Gráficos Consolidados
==============================================

Este módulo contiene todas las funciones de generación de gráficos de HotBoat,
organizadas y optimizadas para mejor rendimiento y mantenibilidad.

Autores: Sistema HotBoat
Fecha: Junio 2025
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================================================
# CONFIGURACIÓN DE TEMA
# ============================================================================

THEME_CONFIG = {
    'background_color': '#0f1419',
    'paper_color': '#1e2328', 
    'text_color': '#e6e6e6',
    'primary_color': '#00d4ff',
    'secondary_color': '#ff6b35',
    'success_color': '#00ff88',
    'warning_color': '#ffaa00',
    'error_color': '#ff4444',
    'grid_color': '#2d3748',
    'font_family': 'Arial, sans-serif'
}

def get_base_layout():
    """
    Retorna el layout base para todos los gráficos
    
    Returns:
        dict: Configuración de layout base
    """
    return {
        'plot_bgcolor': THEME_CONFIG['background_color'],
        'paper_bgcolor': THEME_CONFIG['paper_color'],
        'font': {
            'color': THEME_CONFIG['text_color'],
            'family': THEME_CONFIG['font_family']
        },
        'xaxis': {
            'gridcolor': THEME_CONFIG['grid_color'],
            'color': THEME_CONFIG['text_color']
        },
        'yaxis': {
            'gridcolor': THEME_CONFIG['grid_color'],
            'color': THEME_CONFIG['text_color']
        },
        'legend': {
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': THEME_CONFIG['grid_color'],
            'font': {'color': THEME_CONFIG['text_color']}
        }
    }

# ============================================================================
# GRÁFICOS DE UTILIDAD
# ============================================================================

def crear_grafico_utilidad_tiempo(datos, periodo='M'):
    """
    Crea gráfico de utilidad operativa en el tiempo
    
    Args:
        datos (dict): Datos consolidados
        periodo (str): Período de agrupación ('D', 'W', 'M', 'Q')
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de utilidad
    """
    
    try:
        # Preparar datos
        df_utilidad = calcular_utilidad_por_periodo(datos, periodo)
        
        if df_utilidad.empty:
            return crear_grafico_vacio("Sin datos de utilidad disponibles")
        
        # Crear gráfico
        fig = go.Figure()
        
        # Línea de utilidad
        fig.add_trace(go.Scatter(
            x=df_utilidad['fecha'],
            y=df_utilidad['utilidad'],
            mode='lines+markers',
            name='Utilidad Operativa',
            line=dict(
                color=THEME_CONFIG['primary_color'],
                width=3
            ),
            marker=dict(
                size=8,
                color=THEME_CONFIG['primary_color']
            ),
            hovertemplate='<b>%{y:$,.0f}</b><br>%{x}<extra></extra>'
        ))
        
        # Línea de tendencia
        if len(df_utilidad) > 2:
            z = np.polyfit(range(len(df_utilidad)), df_utilidad['utilidad'], 1)
            p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=df_utilidad['fecha'],
                y=p(range(len(df_utilidad))),
                mode='lines',
                name='Tendencia',
                line=dict(
                    color=THEME_CONFIG['warning_color'],
                    width=2,
                    dash='dash'
                ),
                hovertemplate='Tendencia: <b>%{y:$,.0f}</b><extra></extra>'
            ))
        
        # Layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '📈 Utilidad Operativa en el Tiempo',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']},
                'x': 0.5
            },
            'xaxis': {
                **layout['xaxis'],
                'title': 'Período'
            },
            'yaxis': {
                **layout['yaxis'],
                'title': 'Utilidad (CLP)',
                'tickformat': '$,.0f'
            },
            'hovermode': 'x unified'
        })
        
        fig.update_layout(layout)
        
        return fig
        
    except Exception as e:
        print(f"Error creando gráfico de utilidad: {e}")
        return crear_grafico_vacio("Error generando gráfico de utilidad")

def crear_grafico_ingresos_vs_costos(datos, periodo='M'):
    """
    Crea gráfico comparativo de ingresos vs costos
    
    Args:
        datos (dict): Datos consolidados
        periodo (str): Período de agrupación
        
    Returns:
        plotly.graph_objects.Figure: Gráfico comparativo
    """
    
    try:
        # Preparar datos
        df_resumen = calcular_resumen_financiero_por_periodo(datos, periodo)
        
        if df_resumen.empty:
            return crear_grafico_vacio("Sin datos financieros disponibles")
        
        # Crear gráfico de barras agrupadas
        fig = go.Figure()
        
        # Ingresos
        fig.add_trace(go.Bar(
            x=df_resumen['fecha'],
            y=df_resumen['ingresos'],
            name='Ingresos',
            marker_color=THEME_CONFIG['success_color'],
            hovertemplate='Ingresos: <b>%{y:$,.0f}</b><extra></extra>'
        ))
        
        # Costos Operativos
        fig.add_trace(go.Bar(
            x=df_resumen['fecha'],
            y=df_resumen['costos_operativos'],
            name='Costos Operativos',
            marker_color=THEME_CONFIG['error_color'],
            hovertemplate='Costos: <b>%{y:$,.0f}</b><extra></extra>'
        ))
        
        # Gastos Marketing
        fig.add_trace(go.Bar(
            x=df_resumen['fecha'],
            y=df_resumen['gastos_marketing'],
            name='Marketing',
            marker_color=THEME_CONFIG['warning_color'],
            hovertemplate='Marketing: <b>%{y:$,.0f}</b><extra></extra>'
        ))
        
        # Layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '💰 Ingresos vs Costos por Período',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']},
                'x': 0.5
            },
            'xaxis': {
                **layout['xaxis'],
                'title': 'Período'
            },
            'yaxis': {
                **layout['yaxis'],
                'title': 'Monto (CLP)',
                'tickformat': '$,.0f'
            },
            'barmode': 'group',
            'hovermode': 'x unified'
        })
        
        fig.update_layout(layout)
        
        return fig
        
    except Exception as e:
        print(f"Error creando gráfico ingresos vs costos: {e}")
        return crear_grafico_vacio("Error generando gráfico comparativo")

def crear_grafico_margenes_tiempo(datos, periodo='M'):
    """
    Crea gráfico de márgenes de utilidad en el tiempo
    
    Args:
        datos (dict): Datos consolidados
        periodo (str): Período de agrupación
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de márgenes
    """
    
    try:
        df_utilidad = calcular_utilidad_por_periodo(datos, periodo)
        
        if df_utilidad.empty:
            return crear_grafico_vacio("Sin datos para calcular márgenes")
        
        fig = go.Figure()
        
        # Línea de margen
        fig.add_trace(go.Scatter(
            x=df_utilidad['fecha'],
            y=df_utilidad['margen_porcentaje'],
            mode='lines+markers',
            name='Margen de Utilidad',
            line=dict(
                color=THEME_CONFIG['secondary_color'],
                width=3
            ),
            marker=dict(
                size=8,
                color=df_utilidad['margen_porcentaje'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Margen %")
            ),
            hovertemplate='Margen: <b>%{y:.1f}%</b><br>%{x}<extra></extra>'
        ))
        
        # Línea de referencia (0%)
        fig.add_hline(
            y=0, 
            line_dash="dash", 
            line_color=THEME_CONFIG['text_color'],
            annotation_text="Punto de equilibrio"
        )
        
        # Layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '📊 Margen de Utilidad en el Tiempo',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']},
                'x': 0.5
            },
            'xaxis': {
                **layout['xaxis'],
                'title': 'Período'
            },
            'yaxis': {
                **layout['yaxis'],
                'title': 'Margen (%)',
                'tickformat': '.1f',
                'ticksuffix': '%'
            }
        })
        
        fig.update_layout(layout)
        
        return fig
        
    except Exception as e:
        print(f"Error creando gráfico de márgenes: {e}")
        return crear_grafico_vacio("Error generando gráfico de márgenes")

def crear_grafico_breakdown_costos(datos):
    """
    Crea gráfico de desglose de costos (pie chart)
    
    Args:
        datos (dict): Datos consolidados
        
    Returns:
        plotly.graph_objects.Figure: Gráfico pie de costos
    """
    
    try:
        # Calcular totales por categoría
        categorias = []
        valores = []
        
        if 'costos_operativos' in datos and not datos['costos_operativos'].empty:
            total_operativos = datos['costos_operativos']['monto'].sum()
            categorias.append('Costos Operativos')
            valores.append(total_operativos)
        
        if 'gastos_marketing' in datos and not datos['gastos_marketing'].empty:
            total_marketing = datos['gastos_marketing']['monto'].sum()
            categorias.append('Marketing')
            valores.append(total_marketing)
        
        if 'costos_fijos' in datos and not datos['costos_fijos'].empty:
            total_fijos = datos['costos_fijos']['monto'].sum()
            categorias.append('Costos Fijos')
            valores.append(total_fijos)
        
        if not categorias:
            return crear_grafico_vacio("Sin datos de costos disponibles")
        
        # Crear gráfico pie
        fig = go.Figure(data=[go.Pie(
            labels=categorias,
            values=valores,
            hole=0.4,
            marker=dict(
                colors=[THEME_CONFIG['error_color'], THEME_CONFIG['warning_color'], THEME_CONFIG['secondary_color']],
                line=dict(color=THEME_CONFIG['background_color'], width=2)
            ),
            textinfo='label+percent+value',
            texttemplate='<b>%{label}</b><br>%{percent}<br>$%{value:,.0f}',
            hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
        )])
        
        # Layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '🥧 Desglose de Costos',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']},
                'x': 0.5
            },
            'annotations': [dict(text='Total<br>Costos', x=0.5, y=0.5, font_size=16, showarrow=False)]
        })
        
        fig.update_layout(layout)
        
        return fig
        
    except Exception as e:
        print(f"Error creando gráfico de breakdown: {e}")
        return crear_grafico_vacio("Error generando desglose de costos")

# ============================================================================
# GRÁFICOS DE RESERVAS
# ============================================================================

def crear_grafico_reservas_mes(datos):
    """
    Crea gráfico de reservas por mes
    
    Args:
        datos (dict): Datos consolidados
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de reservas
    """
    
    try:
        if 'reservas' not in datos or datos['reservas'].empty:
            return crear_grafico_vacio("Sin datos de reservas disponibles")
        
        df_reservas = datos['reservas'].copy()
        
        # Buscar columna de fecha
        fecha_cols = [col for col in df_reservas.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        if not fecha_cols:
            return crear_grafico_vacio("No se encontró columna de fecha en reservas")
        
        fecha_col = fecha_cols[0]
        df_reservas[fecha_col] = pd.to_datetime(df_reservas[fecha_col], errors='coerce')
        df_reservas = df_reservas.dropna(subset=[fecha_col])
        
        # Agrupar por mes
        df_reservas['mes'] = df_reservas[fecha_col].dt.to_period('M')
        reservas_por_mes = df_reservas.groupby('mes').size().reset_index(name='cantidad')
        reservas_por_mes['mes_str'] = reservas_por_mes['mes'].astype(str)
        
        # Crear gráfico
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=reservas_por_mes['mes_str'],
            y=reservas_por_mes['cantidad'],
            name='Reservas',
            marker_color=THEME_CONFIG['primary_color'],
            hovertemplate='Mes: %{x}<br>Reservas: <b>%{y}</b><extra></extra>'
        ))
        
        # Layout
        layout = get_base_layout()
        layout.update({
            'title': {
                'text': '🚤 Reservas por Mes',
                'font': {'size': 20, 'color': THEME_CONFIG['text_color']},
                'x': 0.5
            },
            'xaxis': {
                **layout['xaxis'],
                'title': 'Mes'
            },
            'yaxis': {
                **layout['yaxis'],
                'title': 'Número de Reservas'
            }
        })
        
        fig.update_layout(layout)
        
        return fig
        
    except Exception as e:
        print(f"Error creando gráfico de reservas: {e}")
        return crear_grafico_vacio("Error generando gráfico de reservas")

# ============================================================================
# GRÁFICOS DE MARKETING
# ============================================================================

def crear_grafico_marketing_roi(datos):
    """
    Crea gráfico de ROI de marketing
    
    Args:
        datos (dict): Datos consolidados
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de ROI
    """
    
    try:
        if 'gastos_marketing' not in datos or datos['gastos_marketing'].empty:
            return crear_grafico_vacio("Sin datos de marketing disponibles")
        
        df_marketing = datos['gastos_marketing'].copy()
        
        # Calcular ROI por campaña si existe información
        if 'campana' in df_marketing.columns:
            roi_por_campana = df_marketing.groupby('campana')['monto'].sum().reset_index()
            roi_por_campana = roi_por_campana.head(10)  # Top 10 campañas
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=roi_por_campana['campana'],
                y=roi_por_campana['monto'],
                name='Gasto por Campaña',
                marker_color=THEME_CONFIG['warning_color'],
                hovertemplate='Campaña: %{x}<br>Gasto: <b>$%{y:,.0f}</b><extra></extra>'
            ))
            
            # Layout
            layout = get_base_layout()
            layout.update({
                'title': {
                    'text': '📱 Gasto por Campaña de Marketing',
                    'font': {'size': 20, 'color': THEME_CONFIG['text_color']},
                    'x': 0.5
                },
                'xaxis': {
                    **layout['xaxis'],
                    'title': 'Campaña',
                    'tickangle': -45
                },
                'yaxis': {
                    **layout['yaxis'],
                    'title': 'Gasto (CLP)',
                    'tickformat': '$,.0f'
                }
            })
            
            fig.update_layout(layout)
            
            return fig
        else:
            return crear_grafico_vacio("Sin información de campañas para ROI")
        
    except Exception as e:
        print(f"Error creando gráfico de marketing ROI: {e}")
        return crear_grafico_vacio("Error generando gráfico de marketing")

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def crear_grafico_vacio(mensaje):
    """
    Crea un gráfico vacío con un mensaje
    
    Args:
        mensaje (str): Mensaje a mostrar
        
    Returns:
        plotly.graph_objects.Figure: Gráfico vacío
    """
    
    fig = go.Figure()
    
    fig.add_annotation(
        text=mensaje,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color=THEME_CONFIG['text_color'])
    )
    
    layout = get_base_layout()
    layout.update({
        'title': {
            'text': 'Sin Datos',
            'font': {'size': 18, 'color': THEME_CONFIG['text_color']},
            'x': 0.5
        },
        'xaxis': {'visible': False},
        'yaxis': {'visible': False}
    })
    
    fig.update_layout(layout)
    
    return fig

def calcular_utilidad_por_periodo(datos, periodo='M'):
    """
    Calcula la utilidad operativa agrupada por período
    
    Args:
        datos (dict): Datos consolidados
        periodo (str): Período de agrupación
        
    Returns:
        pd.DataFrame: DataFrame con utilidad por período
    """
    
    try:
        # Obtener datasets necesarios
        ingresos_df = datos.get('ingresos', pd.DataFrame())
        costos_df = datos.get('costos_operativos', pd.DataFrame())
        marketing_df = datos.get('gastos_marketing', pd.DataFrame())
        
        # Lista para almacenar datos por período
        periodos_data = []
        
        # Combinar todas las fechas para determinar el rango
        all_dates = []
        
        for df, tipo in [(ingresos_df, 'ingreso'), (costos_df, 'costo'), (marketing_df, 'marketing')]:
            if not df.empty and 'fecha' in df.columns:
                fechas_validas = pd.to_datetime(df['fecha'], errors='coerce').dropna()
                if not fechas_validas.empty:
                    all_dates.extend(fechas_validas.tolist())
        
        if not all_dates:
            return pd.DataFrame()
        
        # Crear rango de períodos
        fecha_min = min(all_dates)
        fecha_max = max(all_dates)
        
        if periodo == 'M':
            periodos = pd.period_range(fecha_min, fecha_max, freq='M')
        elif periodo == 'W':
            periodos = pd.period_range(fecha_min, fecha_max, freq='W')
        elif periodo == 'Q':
            periodos = pd.period_range(fecha_min, fecha_max, freq='Q')
        else:  # 'D'
            periodos = pd.period_range(fecha_min, fecha_max, freq='D')
        
        # Calcular para cada período
        for per in periodos:
            periodo_start = per.start_time
            periodo_end = per.end_time
            
            # Ingresos del período
            ingresos_periodo = 0
            if not ingresos_df.empty and 'fecha' in ingresos_df.columns and 'monto' in ingresos_df.columns:
                mask = (pd.to_datetime(ingresos_df['fecha'], errors='coerce') >= periodo_start) & \
                       (pd.to_datetime(ingresos_df['fecha'], errors='coerce') <= periodo_end)
                ingresos_periodo = ingresos_df[mask]['monto'].sum()
            
            # Costos del período
            costos_periodo = 0
            if not costos_df.empty and 'fecha' in costos_df.columns and 'monto' in costos_df.columns:
                mask = (pd.to_datetime(costos_df['fecha'], errors='coerce') >= periodo_start) & \
                       (pd.to_datetime(costos_df['fecha'], errors='coerce') <= periodo_end)
                costos_periodo = costos_df[mask]['monto'].sum()
            
            # Marketing del período
            marketing_periodo = 0
            if not marketing_df.empty and 'fecha' in marketing_df.columns and 'monto' in marketing_df.columns:
                mask = (pd.to_datetime(marketing_df['fecha'], errors='coerce') >= periodo_start) & \
                       (pd.to_datetime(marketing_df['fecha'], errors='coerce') <= periodo_end)
                marketing_periodo = marketing_df[mask]['monto'].sum()
            
            # Calcular utilidad
            utilidad = ingresos_periodo - costos_periodo - marketing_periodo
            margen = (utilidad / ingresos_periodo * 100) if ingresos_periodo > 0 else 0
            
            periodos_data.append({
                'fecha': periodo_start,
                'periodo': str(per),
                'ingresos': ingresos_periodo,
                'costos': costos_periodo,
                'marketing': marketing_periodo,
                'utilidad': utilidad,
                'margen_porcentaje': margen
            })
        
        return pd.DataFrame(periodos_data)
        
    except Exception as e:
        print(f"Error calculando utilidad por período: {e}")
        return pd.DataFrame()

def calcular_resumen_financiero_por_periodo(datos, periodo='M'):
    """
    Calcula resumen financiero agrupado por período
    
    Args:
        datos (dict): Datos consolidados
        periodo (str): Período de agrupación
        
    Returns:
        pd.DataFrame: DataFrame con resumen financiero
    """
    
    return calcular_utilidad_por_periodo(datos, periodo)

if __name__ == "__main__":
    # Test de funciones
    print("🎨 Módulo de generadores de gráficos cargado exitosamente") 