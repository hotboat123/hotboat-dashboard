import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import os
import numpy as np

# Función para cargar datos con más procesamiento
def cargar_datos():
    """Carga los archivos CSV de marketing."""
    try:
        archivo_path = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv"
        print(f"Cargando archivo: {archivo_path}")
        
        if not os.path.exists(archivo_path):
            print(f"ERROR: No se encuentra el archivo en: {archivo_path}")
            return None
        
        df = pd.read_csv(archivo_path)
        print(f"Archivo cargado. Dimensiones: {df.shape}")
        
        # Convertir columnas numéricas
        numeric_columns = [
            "Importe gastado (CLP)", "Impresiones", "Clics en el enlace", 
            "Artículos agregados al carrito", "CTR (todos)", "CPC (todos)",
            "Reproducciones de video de 3 segundos", "Reproducciones de video hasta el 25%",
            "Reproducciones de video hasta el 50%", "Reproducciones de video hasta el 75%",
            "Reproducciones de video hasta el 100%"
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Convertir fechas
        df['Día'] = pd.to_datetime(df['Día'])
        
        # Agregar columnas calculadas
        df['CTR_calc'] = (df['Clics en el enlace'] / df['Impresiones'] * 100).fillna(0)
        df['CPC_calc'] = (df['Importe gastado (CLP)'] / df['Clics en el enlace']).fillna(0)
        df['Hook_Rate_3s'] = (df['Reproducciones de video de 3 segundos'] / df['Impresiones'] * 100).fillna(0)
        df['Hook_Rate_25'] = (df['Reproducciones de video hasta el 25%'] / df['Impresiones'] * 100).fillna(0)
        df['Hook_Rate_50'] = (df['Reproducciones de video hasta el 50%'] / df['Impresiones'] * 100).fillna(0)
        df['Hook_Rate_75'] = (df['Reproducciones de video hasta el 75%'] / df['Impresiones'] * 100).fillna(0)
        df['Hook_Rate_100'] = (df['Reproducciones de video hasta el 100%'] / df['Impresiones'] * 100).fillna(0)
        df['Conversion_Rate'] = (df['Artículos agregados al carrito'] / df['Clics en el enlace'] * 100).fillna(0)
        df['Cost_Per_Conversion'] = (df['Importe gastado (CLP)'] / df['Artículos agregados al carrito']).fillna(0)
        
        # Clasificar públicos
        df['Público'] = df['Nombre del conjunto de anuncios'].apply(
            lambda x: 'Advantage' if 'advantage' in str(x).lower() else 
                     'Pucón' if 'pucon' in str(x).lower() else 'Otro'
        )
        
        # Clasificar tipos de anuncios
        df['Tipo_Anuncio'] = df['Nombre del anuncio'].apply(
            lambda x: 'Video explicativo' if 'explicando servicio' in str(x).lower() else
                     'Video parejas amor' if 'parejas amor' in str(x).lower() else
                     'Video parejas dcto' if 'parejas dcto' in str(x).lower() else
                     'Otro'
        )
        
        print("Datos procesados exitosamente")
        return df
    
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return None

# Crear aplicación
app = dash.Dash(__name__)

# Cargar datos
df_data = cargar_datos()

if df_data is not None:
    fecha_min = df_data['Día'].min()
    fecha_max = df_data['Día'].max()
    
    # Layout expandido
    app.layout = html.Div([
        html.H1('Dashboard de Marketing - Meta Ads', style={
            'textAlign': 'center',
            'color': '#2c3e50',
            'marginBottom': '30px',
            'fontFamily': 'Arial, sans-serif'
        }),
        
        # Filtros
        html.Div([
            html.Div([
                html.Label('Seleccionar rango de fechas:', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=fecha_min,
                    end_date=fecha_max,
                    display_format='DD/MM/YYYY',
                    style={'width': '100%'}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label('Periodo de agrupación:', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                dcc.RadioItems(
                    id='periodo-selector',
                    options=[
                        {'label': 'Diario', 'value': 'D'},
                        {'label': 'Semanal', 'value': 'W'},
                        {'label': 'Mensual', 'value': 'M'}
                    ],
                    value='D',
                    style={'marginTop': '10px'}
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
        
        # Métricas principales
        html.Div(id='metricas-principales', style={'margin': '20px'}),
        
        # Gráficos en filas
        html.Div([
            dcc.Graph(id='grafico-evolucion')
        ], style={'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='grafico-regiones')
        ], style={'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='grafico-publicos')
        ], style={'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='grafico-tipos-anuncios')
        ], style={'margin': '20px'}),
        
        html.Div([
            dcc.Graph(id='grafico-hook-rates')
        ], style={'margin': '20px'}),
        
        # Insights
        html.Div([
            html.H3('Conclusiones e Insights', style={'color': '#2c3e50', 'marginBottom': '15px'}),
            html.Div(id='insights-contenido')
        ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
    ])
    
    # Callback principal
    @callback(
        [Output('metricas-principales', 'children'),
         Output('grafico-evolucion', 'figure'),
         Output('grafico-regiones', 'figure'),
         Output('grafico-publicos', 'figure'),
         Output('grafico-tipos-anuncios', 'figure'),
         Output('grafico-hook-rates', 'figure'),
         Output('insights-contenido', 'children')],
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('periodo-selector', 'value')]
    )
    def actualizar_dashboard(start_date, end_date, periodo):
        try:
            # Filtrar datos por fecha
            mask = (df_data['Día'] >= start_date) & (df_data['Día'] <= end_date)
            df_filtrado = df_data[mask]
            
            if df_filtrado.empty:
                empty_fig = go.Figure()
                empty_fig.update_layout(title="No hay datos para el período seleccionado")
                return (html.Div("No hay datos"), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "No hay insights disponibles")
            
            # Calcular métricas principales
            total_gasto = df_filtrado['Importe gastado (CLP)'].sum()
            total_impresiones = df_filtrado['Impresiones'].sum()
            total_clics = df_filtrado['Clics en el enlace'].sum()
            total_conversiones = df_filtrado['Artículos agregados al carrito'].sum()
            
            ctr = (total_clics / total_impresiones * 100) if total_impresiones > 0 else 0
            cpc = (total_gasto / total_clics) if total_clics > 0 else 0
            
            # 1. Tarjetas de métricas
            metricas = html.Div([
                html.Div([
                    html.H3(f'${total_gasto:,.0f}', style={'color': '#e74c3c', 'margin': '0', 'fontSize': '2em'}),
                    html.P('Gasto Total', style={'margin': '5px 0', 'fontWeight': 'bold'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '0 10px'}),
                
                html.Div([
                    html.H3(f'{total_impresiones:,.0f}', style={'color': '#3498db', 'margin': '0', 'fontSize': '2em'}),
                    html.P('Impresiones', style={'margin': '5px 0', 'fontWeight': 'bold'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '0 10px'}),
                
                html.Div([
                    html.H3(f'{total_clics:,.0f}', style={'color': '#27ae60', 'margin': '0', 'fontSize': '2em'}),
                    html.P('Clics', style={'margin': '5px 0', 'fontWeight': 'bold'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '0 10px'}),
                
                html.Div([
                    html.H3(f'{ctr:.2f}%', style={'color': '#f39c12', 'margin': '0', 'fontSize': '2em'}),
                    html.P('CTR Promedio', style={'margin': '5px 0', 'fontWeight': 'bold'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '0 10px'}),
                
                html.Div([
                    html.H3(f'{total_conversiones:,.0f}', style={'color': '#9b59b6', 'margin': '0', 'fontSize': '2em'}),
                    html.P('Conversiones', style={'margin': '5px 0', 'fontWeight': 'bold'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '8px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'flex': '1', 'margin': '0 10px'})
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap', 'gap': '10px'})
            
            # 2. Gráfico de evolución temporal (línea + área)
            if periodo == 'D':
                df_temporal = df_filtrado.groupby('Día')['Importe gastado (CLP)'].sum().reset_index()
                titulo_evolucion = 'Evolución Diaria del Gasto'
            elif periodo == 'W':
                df_temporal = df_filtrado.groupby(df_filtrado['Día'].dt.to_period('W').dt.start_time)['Importe gastado (CLP)'].sum().reset_index()
                titulo_evolucion = 'Evolución Semanal del Gasto'
            else:
                df_temporal = df_filtrado.groupby(df_filtrado['Día'].dt.to_period('M').dt.start_time)['Importe gastado (CLP)'].sum().reset_index()
                titulo_evolucion = 'Evolución Mensual del Gasto'
            
            fig_evolucion = go.Figure()
            fig_evolucion.add_trace(go.Scatter(
                x=df_temporal['Día'],
                y=df_temporal['Importe gastado (CLP)'],
                mode='lines+markers',
                name='Gasto',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8),
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.1)'
            ))
            
            fig_evolucion.update_layout(
                title=titulo_evolucion,
                xaxis_title='Período',
                yaxis_title='Gasto (CLP)',
                height=400,
                template='plotly_white',
                hovermode='x unified'
            )
            
            # 3. Gráfico por región (barras horizontales)
            df_regiones = df_filtrado.groupby('Región').agg({
                'Importe gastado (CLP)': 'sum',
                'Impresiones': 'sum',
                'Clics en el enlace': 'sum'
            }).reset_index()
            df_regiones = df_regiones.sort_values('Importe gastado (CLP)', ascending=True).tail(10)
            
            fig_regiones = go.Figure(go.Bar(
                x=df_regiones['Importe gastado (CLP)'],
                y=df_regiones['Región'],
                orientation='h',
                marker_color='#3498db',
                text=df_regiones['Importe gastado (CLP)'].apply(lambda x: f'${x:,.0f}'),
                textposition='auto'
            ))
            
            fig_regiones.update_layout(
                title='Gasto por Región (Top 10)',
                xaxis_title='Gasto (CLP)',
                yaxis_title='',
                height=500,
                template='plotly_white'
            )
            
            # 4. Gráfico por públicos (6 métricas en subplots)
            df_publicos = df_filtrado.groupby('Público').agg({
                'Importe gastado (CLP)': 'sum',
                'Impresiones': 'sum',
                'Clics en el enlace': 'sum',
                'Artículos agregados al carrito': 'sum'
            }).reset_index()
            
            df_publicos['CTR (%)'] = (df_publicos['Clics en el enlace'] / df_publicos['Impresiones'] * 100).fillna(0)
            df_publicos['CPC (CLP)'] = (df_publicos['Importe gastado (CLP)'] / df_publicos['Clics en el enlace']).fillna(0)
            df_publicos['Conversión (%)'] = (df_publicos['Artículos agregados al carrito'] / df_publicos['Clics en el enlace'] * 100).fillna(0)
            df_publicos['Costo por Conversión (CLP)'] = (df_publicos['Importe gastado (CLP)'] / df_publicos['Artículos agregados al carrito']).fillna(0)
            
            fig_publicos = make_subplots(
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
            
            # Colores para cada métrica
            colors = ['#e74c3c', '#f39c12', '#9b59b6', '#27ae60', '#e67e22', '#3498db']
            
            # Añadir barras para cada métrica
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Importe gastado (CLP)'], marker_color=colors[0], showlegend=False), row=1, col=1)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['CTR (%)'], marker_color=colors[1], showlegend=False), row=1, col=2)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['CPC (CLP)'], marker_color=colors[2], showlegend=False), row=2, col=1)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Conversión (%)'], marker_color=colors[3], showlegend=False), row=2, col=2)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Costo por Conversión (CLP)'], marker_color=colors[4], showlegend=False), row=3, col=1)
            fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Artículos agregados al carrito'], marker_color=colors[5], showlegend=False), row=3, col=2)
            
            fig_publicos.update_layout(
                title='Comparación entre Públicos',
                height=800,
                template='plotly_white'
            )
            
            # 5. Gráfico por tipos de anuncios (6 métricas en subplots)
            df_tipos = df_filtrado.groupby('Tipo_Anuncio').agg({
                'Importe gastado (CLP)': 'sum',
                'Impresiones': 'sum',
                'Clics en el enlace': 'sum',
                'Artículos agregados al carrito': 'sum'
            }).reset_index()
            
            df_tipos['CTR (%)'] = (df_tipos['Clics en el enlace'] / df_tipos['Impresiones'] * 100).fillna(0)
            df_tipos['CPC (CLP)'] = (df_tipos['Importe gastado (CLP)'] / df_tipos['Clics en el enlace']).fillna(0)
            df_tipos['Conversión (%)'] = (df_tipos['Artículos agregados al carrito'] / df_tipos['Clics en el enlace'] * 100).fillna(0)
            df_tipos['Costo por Conversión (CLP)'] = (df_tipos['Importe gastado (CLP)'] / df_tipos['Artículos agregados al carrito']).fillna(0)
            
            fig_tipos = make_subplots(
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
            
            # Añadir barras para cada métrica
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Importe gastado (CLP)'], marker_color=colors[0], showlegend=False), row=1, col=1)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CTR (%)'], marker_color=colors[1], showlegend=False), row=1, col=2)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CPC (CLP)'], marker_color=colors[2], showlegend=False), row=2, col=1)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Conversión (%)'], marker_color=colors[3], showlegend=False), row=2, col=2)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Costo por Conversión (CLP)'], marker_color=colors[4], showlegend=False), row=3, col=1)
            fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Artículos agregados al carrito'], marker_color=colors[5], showlegend=False), row=3, col=2)
            
            fig_tipos.update_layout(
                title='Comparación de Métricas por Tipo de Anuncio',
                height=800,
                template='plotly_white'
            )
            
            # Rotar etiquetas del eje x para tipos de anuncios
            fig_tipos.update_xaxes(tickangle=45)
            
            # 6. Gráfico de Hook Rates (barras horizontales como el original)
            df_hooks = df_filtrado.groupby('Tipo_Anuncio').agg({
                'Hook_Rate_3s': 'mean',
                'Hook_Rate_25': 'mean',
                'Hook_Rate_50': 'mean',
                'Hook_Rate_75': 'mean',
                'Hook_Rate_100': 'mean'
            }).reset_index()
            
            # Ordenar por Hook Rate 3s como en el original
            df_hooks = df_hooks.sort_values('Hook_Rate_3s', ascending=True)
            
            # Colores específicos para cada hook rate como en el original
            colors_hooks = {
                '3s': '#FF9999',
                '25%': '#66B2FF', 
                '50%': '#99FF99',
                '75%': '#FFCC99',
                '100%': '#FF99CC'
            }
            
            fig_hooks = go.Figure()
            
            # Añadir cada hook rate como una barra horizontal separada
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_3s'],
                name='3 segundos',
                orientation='h',
                marker_color=colors_hooks['3s'],
                hovertemplate='Hook Rate 3s: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_25'],
                name='25%',
                orientation='h',
                marker_color=colors_hooks['25%'],
                hovertemplate='Hook Rate 25%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_50'],
                name='50%',
                orientation='h',
                marker_color=colors_hooks['50%'],
                hovertemplate='Hook Rate 50%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_75'],
                name='75%',
                orientation='h',
                marker_color=colors_hooks['75%'],
                hovertemplate='Hook Rate 75%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.add_trace(go.Bar(
                y=df_hooks['Tipo_Anuncio'],
                x=df_hooks['Hook_Rate_100'],
                name='100%',
                orientation='h',
                marker_color=colors_hooks['100%'],
                hovertemplate='Hook Rate 100%: %{x:.2f}%<br><extra></extra>'
            ))
            
            fig_hooks.update_layout(
                title='Hook Rates por Tipo de Anuncio',
                xaxis=dict(
                    title='Hook Rate (%)',
                    showgrid=True,
                    gridcolor='#e0e0e0',
                    tickformat='.2f'
                ),
                yaxis=dict(
                    title='Tipo de Anuncio',
                    showgrid=False
                ),
                height=500,
                template='plotly_white',
                barmode='group',
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                margin=dict(l=200)  # Margen izquierdo para nombres largos
            )
            
            # 7. Generar insights
            dias_analizados = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
            gasto_promedio_diario = total_gasto / dias_analizados if dias_analizados > 0 else 0
            
            mejor_region = df_regiones.iloc[-1] if not df_regiones.empty else None
            mejor_publico = df_publicos.loc[df_publicos['Importe gastado (CLP)'].idxmax()] if not df_publicos.empty else None
            
            insights = [
                html.P(f"📊 Análisis del período: {dias_analizados} días", style={'fontWeight': 'bold', 'fontSize': '16px'}),
                html.P(f"💰 Gasto promedio diario: ${gasto_promedio_diario:,.0f}"),
                html.P(f"📈 CTR promedio: {ctr:.2f}%"),
                html.P(f"💸 CPC promedio: ${cpc:,.0f}"),
            ]
            
            if mejor_region is not None:
                insights.append(html.P(f"🎯 Región con mayor gasto: {mejor_region['Región']} (${mejor_region['Importe gastado (CLP)']:,.0f})"))
            
            if mejor_publico is not None:
                insights.append(html.P(f"👥 Público con mejor rendimiento: {mejor_publico['Público']} (${mejor_publico['Importe gastado (CLP)']:,.0f})"))
            
            insights_contenido = html.Div(insights)
            
            return metricas, fig_evolucion, fig_regiones, fig_publicos, fig_tipos, fig_hooks, insights_contenido
            
        except Exception as e:
            print(f"Error en callback: {str(e)}")
            import traceback
            traceback.print_exc()
            empty_fig = go.Figure()
            return (html.Div("Error al cargar datos"), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "Error en insights")

else:
    app.layout = html.Div([
        html.H1("Error: No se pudieron cargar los datos", style={'textAlign': 'center', 'color': 'red'})
    ])

if __name__ == '__main__':
    print("\n=== DASHBOARD DE MARKETING COMPLETO ===")
    print("Datos cargados exitosamente")
    print("Iniciando servidor en http://localhost:8052")
    app.run(debug=True, port=8052) 