import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def cargar_datos():
    """Carga los archivos CSV de marketing."""
    try:
        archivo_path = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv"
        print(f"Cargando archivo: {archivo_path}")
        
        df = pd.read_csv(archivo_path)
        print(f"Archivo cargado. Dimensiones: {df.shape}")
        
        # Convertir columnas numéricas con manejo especial de formato
        numeric_columns = [
            "Importe gastado (CLP)", "Impresiones", "Clics en el enlace", 
            "Artículos agregados al carrito", "CTR (todos)", "CPC (todos)",
            "Reproducciones de video de 3 segundos", "Reproducciones de video hasta el 25%",
            "Reproducciones de video hasta el 50%", "Reproducciones de video hasta el 75%",
            "Reproducciones de video hasta el 100%"
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                # Manejo especial para datos de Facebook/Meta que pueden tener comas
                if df[col].dtype == 'object':
                    # Limpiar formato: quitar espacios, comas, convertir "-" a 0
                    df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('-', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                print(f"Columna {col} convertida - Suma: {df[col].sum()}")
        
        # Convertir fechas
        df['Día'] = pd.to_datetime(df['Día'])
        
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
df_data = cargar_datos()

if df_data is not None:
    fecha_min = df_data['Día'].min()
    fecha_max = df_data['Día'].max()
    
    app.layout = html.Div([
        html.H1('Dashboard de Marketing - Meta Ads', style={
            'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'
        }),
        
        # Filtros
        html.Div([
            html.Div([
                html.Label('Rango de fechas:', style={'fontWeight': 'bold'}),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=fecha_min,
                    end_date=fecha_max,
                    display_format='DD/MM/YYYY'
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label('Período:', style={'fontWeight': 'bold'}),
                dcc.RadioItems(
                    id='periodo-selector',
                    options=[
                        {'label': 'Diario', 'value': 'D'},
                        {'label': 'Semanal', 'value': 'W'},
                        {'label': 'Mensual', 'value': 'M'}
                    ],
                    value='D'
                )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
        ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
        
        # Métricas principales
        html.Div(id='metricas-principales'),
        
        # Gráficos
        dcc.Graph(id='grafico-evolucion'),
        dcc.Graph(id='grafico-regiones'),
        dcc.Graph(id='grafico-publicos'),
        dcc.Graph(id='grafico-tipos-anuncios'),
        dcc.Graph(id='grafico-hook-rates'),
        
        # Insights
        html.Div([
            html.H3('Insights'),
            html.Div(id='insights-contenido')
        ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa'})
    ])
    
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
        # Filtrar datos por fecha
        mask = (df_data['Día'] >= start_date) & (df_data['Día'] <= end_date)
        df_filtrado = df_data[mask]
        
        if df_filtrado.empty:
            empty_fig = go.Figure()
            return (html.Div("No hay datos"), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "No hay insights")
        
        # Calcular métricas principales
        total_gasto = df_filtrado['Importe gastado (CLP)'].sum()
        total_impresiones = df_filtrado['Impresiones'].sum()
        total_clics = df_filtrado['Clics en el enlace'].sum()
        total_conversiones = df_filtrado['Artículos agregados al carrito'].sum()
        
        ctr = (total_clics / total_impresiones * 100) if total_impresiones > 0 else 0
        
        # 1. Tarjetas de métricas
        metricas = html.Div([
            html.Div([
                html.H3(f'${total_gasto:,.0f}', style={'color': '#e74c3c', 'fontSize': '2em'}),
                html.P('Gasto Total')
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f'{total_impresiones:,.0f}', style={'color': '#3498db', 'fontSize': '2em'}),
                html.P('Impresiones')
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f'{total_clics:,.0f}', style={'color': '#27ae60', 'fontSize': '2em'}),
                html.P('Clics')
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f'{ctr:.2f}%', style={'color': '#f39c12', 'fontSize': '2em'}),
                html.P('CTR')
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f'{total_conversiones:,.0f}', style={'color': '#9b59b6', 'fontSize': '2em'}),
                html.P('Conversiones')
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': 'white', 'margin': '10px', 'borderRadius': '5px', 'flex': '1'})
        ], style={'display': 'flex', 'flexWrap': 'wrap'})
        
        # 2. Gráfico de evolución temporal
        if periodo == 'D':
            df_temporal = df_filtrado.groupby('Día')['Importe gastado (CLP)'].sum().reset_index()
            titulo = 'Evolución Diaria del Gasto'
        elif periodo == 'W':
            df_temporal = df_filtrado.groupby(df_filtrado['Día'].dt.to_period('W').dt.start_time)['Importe gastado (CLP)'].sum().reset_index()
            titulo = 'Evolución Semanal del Gasto'
        else:
            df_temporal = df_filtrado.groupby(df_filtrado['Día'].dt.to_period('M').dt.start_time)['Importe gastado (CLP)'].sum().reset_index()
            titulo = 'Evolución Mensual del Gasto'
        
        fig_evolucion = go.Figure()
        fig_evolucion.add_trace(go.Scatter(
            x=df_temporal['Día'],
            y=df_temporal['Importe gastado (CLP)'],
            mode='lines+markers',
            fill='tonexty',
            fillcolor='rgba(231, 76, 60, 0.1)',
            line=dict(color='#e74c3c', width=3)
        ))
        fig_evolucion.update_layout(title=titulo, height=400)
        
        # 3. Gráfico por región
        df_regiones = df_filtrado.groupby('Región')['Importe gastado (CLP)'].sum().reset_index()
        df_regiones = df_regiones.sort_values('Importe gastado (CLP)', ascending=True).tail(10)
        
        fig_regiones = go.Figure(go.Bar(
            x=df_regiones['Importe gastado (CLP)'],
            y=df_regiones['Región'],
            orientation='h',
            marker_color='#3498db'
        ))
        fig_regiones.update_layout(title='Gasto por Región (Top 10)', height=500)
        
        # 4. Gráfico por públicos (6 métricas)
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
            subplot_titles=['Gasto Total (CLP)', 'CTR (%)', 'CPC (CLP)', 'Conversión (%)', 'Costo por Conversión (CLP)', 'Artículos al carrito']
        )
        
        colors = ['#e74c3c', '#f39c12', '#9b59b6', '#27ae60', '#e67e22', '#3498db']
        
        fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Importe gastado (CLP)'], marker_color=colors[0], showlegend=False), row=1, col=1)
        fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['CTR (%)'], marker_color=colors[1], showlegend=False), row=1, col=2)
        fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['CPC (CLP)'], marker_color=colors[2], showlegend=False), row=2, col=1)
        fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Conversión (%)'], marker_color=colors[3], showlegend=False), row=2, col=2)
        fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Costo por Conversión (CLP)'], marker_color=colors[4], showlegend=False), row=3, col=1)
        fig_publicos.add_trace(go.Bar(x=df_publicos['Público'], y=df_publicos['Artículos agregados al carrito'], marker_color=colors[5], showlegend=False), row=3, col=2)
        
        fig_publicos.update_layout(title='Comparación entre Públicos', height=800)
        
        # 5. Gráfico por tipos de anuncios (6 métricas)
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
            subplot_titles=['Gasto Total (CLP)', 'CTR (%)', 'CPC (CLP)', 'Conversión (%)', 'Costo por Conversión (CLP)', 'Artículos al carrito']
        )
        
        fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Importe gastado (CLP)'], marker_color=colors[0], showlegend=False), row=1, col=1)
        fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CTR (%)'], marker_color=colors[1], showlegend=False), row=1, col=2)
        fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CPC (CLP)'], marker_color=colors[2], showlegend=False), row=2, col=1)
        fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Conversión (%)'], marker_color=colors[3], showlegend=False), row=2, col=2)
        fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Costo por Conversión (CLP)'], marker_color=colors[4], showlegend=False), row=3, col=1)
        fig_tipos.add_trace(go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Artículos agregados al carrito'], marker_color=colors[5], showlegend=False), row=3, col=2)
        
        fig_tipos.update_layout(title='Comparación de Métricas por Tipo de Anuncio', height=800)
        fig_tipos.update_xaxes(tickangle=45)
        
        # 6. Gráfico de Hook Rates
        # Calcular hook rates
        df_hooks = df_filtrado.groupby('Tipo_Anuncio').agg({
            'Reproducciones de video de 3 segundos': 'sum',
            'Reproducciones de video hasta el 25%': 'sum',
            'Reproducciones de video hasta el 50%': 'sum',
            'Reproducciones de video hasta el 75%': 'sum',
            'Reproducciones de video hasta el 100%': 'sum',
            'Impresiones': 'sum'
        }).reset_index()
        
        # DIAGNÓSTICO: Imprimir los datos para debug
        print("\n=== Hook Rates Debug ===")
        total_impresiones = df_hooks['Impresiones'].sum()
        total_reproducciones = df_hooks['Reproducciones de video de 3 segundos'].sum()
        print(f"Total impresiones: {total_impresiones:,.0f}")
        print(f"Total reproducciones 3s: {total_reproducciones:,.0f}")
        
        # Calcular porcentajes
        df_hooks['Hook_Rate_3s'] = (df_hooks['Reproducciones de video de 3 segundos'] / df_hooks['Impresiones'] * 100).fillna(0)
        df_hooks['Hook_Rate_25'] = (df_hooks['Reproducciones de video hasta el 25%'] / df_hooks['Impresiones'] * 100).fillna(0)
        df_hooks['Hook_Rate_50'] = (df_hooks['Reproducciones de video hasta el 50%'] / df_hooks['Impresiones'] * 100).fillna(0)
        df_hooks['Hook_Rate_75'] = (df_hooks['Reproducciones de video hasta el 75%'] / df_hooks['Impresiones'] * 100).fillna(0)
        df_hooks['Hook_Rate_100'] = (df_hooks['Reproducciones de video hasta el 100%'] / df_hooks['Impresiones'] * 100).fillna(0)
        
        print("Hook rates por tipo:")
        for _, row in df_hooks.iterrows():
            print(f"  {row['Tipo_Anuncio']}: {row['Hook_Rate_3s']:.1f}%")
        print("========================")
        
        # Ordenar por Hook Rate 3s
        df_hooks = df_hooks.sort_values('Hook_Rate_3s', ascending=True)
        
        # Crear el gráfico de hook rates como barras VERTICALES agrupadas
        fig_hooks = go.Figure()
        
        # Colores para cada hook rate
        hook_colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC']
        hook_names = ['3 segundos', '25%', '50%', '75%', '100%']
        hook_columns = ['Hook_Rate_3s', 'Hook_Rate_25', 'Hook_Rate_50', 'Hook_Rate_75', 'Hook_Rate_100']
        
        # Agregar cada serie de hook rates como barras VERTICALES
        for col, color, name in zip(hook_columns, hook_colors, hook_names):
            fig_hooks.add_trace(go.Bar(
                x=df_hooks['Tipo_Anuncio'],
                y=df_hooks[col],
                name=name,
                marker_color=color,
                text=df_hooks[col].round(1),
                textposition='outside',
                hovertemplate=f'{name}: %{{y:.2f}}%<br>%{{x}}<extra></extra>'
            ))
        
        fig_hooks.update_layout(
            title='Hook Rates por Tipo de Anuncio',
            xaxis_title='Tipo de Anuncio',
            yaxis_title='Hook Rate (%)',
            height=600,
            template='plotly_white',
            barmode='group',  # Barras agrupadas verticalmente
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(tickangle=45),  # Rotar etiquetas para mejor legibilidad
            yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
        )
        
        # 7. Insights
        insights = [
            html.P(f"💰 Gasto total: ${total_gasto:,.0f}"),
            html.P(f"📈 CTR promedio: {ctr:.2f}%"),
            html.P(f"🔄 Total conversiones: {total_conversiones:,.0f}")
        ]
        
        return metricas, fig_evolucion, fig_regiones, fig_publicos, fig_tipos, fig_hooks, html.Div(insights)

else:
    app.layout = html.Div([
        html.H1("Error: No se pudieron cargar los datos", style={'textAlign': 'center', 'color': 'red'})
    ])

if __name__ == '__main__':
    print("\n=== DASHBOARD DE MARKETING FINAL ===")
    print("Iniciando servidor en http://localhost:8053")
    app.run(debug=True, port=8053) 