import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Configuración de archivos
ARCHIVO_REGIONES = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia (2).csv"
ARCHIVO_PRINCIPAL = "archivos_input/archivos input marketing/Comp-1-Conjunto-Anuncios-2Campañas-3-anuncios-por-dia.csv"

def cargar_datos_regiones():
    """Carga datos específicos para el gráfico de regiones."""
    try:
        print(f"Cargando archivo para regiones: {ARCHIVO_REGIONES}")
        df = pd.read_csv(ARCHIVO_REGIONES)
        print(f"Archivo de regiones cargado. Dimensiones: {df.shape}")
        
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
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('-', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Convertir fechas
        df['Día'] = pd.to_datetime(df['Día'])
        
        # Clasificar públicos también en datos de regiones
        df['Público'] = df['Nombre del conjunto de anuncios'].apply(
            lambda x: 'Advantage' if 'advantage' in str(x).lower() else 
                     'Pucón' if 'pucon' in str(x).lower() else 'Otro'
        )
        
        print("Datos de regiones procesados exitosamente")
        return df
    
    except Exception as e:
        print(f"Error cargando datos de regiones: {str(e)}")
        return None

def cargar_datos_principal():
    """Carga datos principales para todos los demás gráficos."""
    try:
        print(f"Cargando archivo principal: {ARCHIVO_PRINCIPAL}")
        df = pd.read_csv(ARCHIVO_PRINCIPAL)
        print(f"Archivo principal cargado. Dimensiones: {df.shape}")
        
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
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('-', '0')
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                print(f"Columna {col} convertida - Suma: {df[col].sum()}")
        
        # Convertir fechas si existe
        if 'Día' in df.columns:
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
        
        print("Datos principales procesados exitosamente")
        return df
    
    except Exception as e:
        print(f"Error cargando datos principales: {str(e)}")
        return None

# Crear aplicación
app = dash.Dash(__name__)

# Cargar ambos datasets
df_regiones = cargar_datos_regiones()
df_principal = cargar_datos_principal()

if df_regiones is not None and df_principal is not None:
    # Usar fechas del archivo principal si existe, sino del de regiones
    if 'Día' in df_principal.columns:
        fecha_min = df_principal['Día'].min()
        fecha_max = df_principal['Día'].max()
    else:
        fecha_min = df_regiones['Día'].min()
        fecha_max = df_regiones['Día'].max()
    
    app.layout = html.Div([
        html.H1('Dashboard de Marketing - Meta Ads (Dual)', style={
            'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'
        }),
        
        html.P('📊 Regiones: archivo (2) | 📈 Resto: archivo sin (2)', style={
            'textAlign': 'center', 'color': '#7f8c8d', 'fontStyle': 'italic'
        }),
        
        # Filtros generales
        html.Div([
            html.Div([
                html.Label('Rango de fechas:', style={'fontWeight': 'bold'}),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=fecha_min,
                    end_date=fecha_max,
                    display_format='DD/MM/YYYY'
                )
            ], style={'width': '45%', 'display': 'inline-block'}),
            
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
            ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'})
        ], style={'margin': '20px', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
        
        # Métricas principales
        html.Div(id='metricas-principales'),
        
        # Gráficos
        dcc.Graph(id='grafico-evolucion'),
        
        # Filtro específico para gráfico de regiones
        html.Div([
            html.H4('Gasto por Región', style={'marginBottom': '10px', 'color': '#2c3e50'}),
            html.Div([
                html.Label('Filtrar por Público:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Dropdown(
                    id='publico-regiones-filter',
                    options=[
                        {'label': 'Todos', 'value': 'Todos'},
                        {'label': 'Advantage', 'value': 'Advantage'},
                        {'label': 'Pucón', 'value': 'Pucón'},
                        {'label': 'Otro', 'value': 'Otro'}
                    ],
                    value='Todos',
                    clearable=False,
                    style={'width': '200px'}
                )
            ], style={'marginBottom': '15px'})
        ], style={'margin': '20px 20px 10px 20px'}),
        
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
         Input('periodo-selector', 'value'),
         Input('publico-regiones-filter', 'value')]
    )
    def actualizar_dashboard(start_date, end_date, periodo, publico_regiones_filter):
        # Filtrar datos principales por fecha
        if 'Día' in df_principal.columns:
            mask_principal = (df_principal['Día'] >= start_date) & (df_principal['Día'] <= end_date)
            df_filtrado_principal = df_principal[mask_principal]
        else:
            df_filtrado_principal = df_principal.copy()
        
        # Filtrar datos de regiones por fecha
        mask_regiones = (df_regiones['Día'] >= start_date) & (df_regiones['Día'] <= end_date)
        df_filtrado_regiones = df_regiones[mask_regiones]
        
        if df_filtrado_principal.empty:
            empty_fig = go.Figure()
            return (html.Div("No hay datos"), empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "No hay insights")
        
        # Calcular métricas principales usando datos principales
        total_gasto = df_filtrado_principal['Importe gastado (CLP)'].sum()
        total_impresiones = df_filtrado_principal['Impresiones'].sum()
        total_clics = df_filtrado_principal['Clics en el enlace'].sum()
        total_conversiones = df_filtrado_principal['Artículos agregados al carrito'].sum()
        
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
        
        # 2. Gráfico de evolución temporal (usando datos principales)
        if 'Día' in df_filtrado_principal.columns:
            if periodo == 'D':
                df_temporal = df_filtrado_principal.groupby('Día')['Importe gastado (CLP)'].sum().reset_index()
                titulo = 'Evolución Diaria del Gasto (archivo principal)'
            elif periodo == 'W':
                df_temporal = df_filtrado_principal.groupby(df_filtrado_principal['Día'].dt.to_period('W').dt.start_time)['Importe gastado (CLP)'].sum().reset_index()
                titulo = 'Evolución Semanal del Gasto (archivo principal)'
            else:
                df_temporal = df_filtrado_principal.groupby(df_filtrado_principal['Día'].dt.to_period('M').dt.start_time)['Importe gastado (CLP)'].sum().reset_index()
                titulo = 'Evolución Mensual del Gasto (archivo principal)'
            
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
        else:
            fig_evolucion = go.Figure()
            fig_evolucion.update_layout(title='Evolución del Gasto - Sin datos temporales', height=400)
        
        # 3. Gráfico por región (usando datos de regiones)
        if 'Región' in df_filtrado_regiones.columns:
            # Aplicar filtro por tipo de público si no es "Todos"
            if publico_regiones_filter != 'Todos':
                df_regiones_filtrado_publico = df_filtrado_regiones[df_filtrado_regiones['Público'] == publico_regiones_filter]
            else:
                df_regiones_filtrado_publico = df_filtrado_regiones
            
            df_regiones_agg = df_regiones_filtrado_publico.groupby('Región')['Importe gastado (CLP)'].sum().reset_index()
            df_regiones_agg = df_regiones_agg.sort_values('Importe gastado (CLP)', ascending=True).tail(10)
            
            fig_regiones = go.Figure(go.Bar(
                x=df_regiones_agg['Importe gastado (CLP)'],
                y=df_regiones_agg['Región'],
                orientation='h',
                marker_color='#3498db',
                text=[f'${x:,.0f}' for x in df_regiones_agg['Importe gastado (CLP)']],
                textposition='outside'
            ))
            
            titulo_regiones = f'Gasto por Región (Top 10) - archivo con (2)'
            if publico_regiones_filter != 'Todos':
                titulo_regiones += f' - Público: {publico_regiones_filter}'
            
            fig_regiones.update_layout(
                title=titulo_regiones,
                height=400,
                margin=dict(l=150)
            )
        else:
            fig_regiones = go.Figure()
            fig_regiones.update_layout(title='Gasto por Región - Sin datos regionales', height=400)
        
        # 4. Gráfico por públicos (usando datos principales)
        df_publicos = df_filtrado_principal.groupby('Público').agg({
            'Importe gastado (CLP)': 'sum',
            'CTR (todos)': 'mean',
            'CPC (todos)': 'mean',
            'Impresiones': 'sum',
            'Clics en el enlace': 'sum',
            'Artículos agregados al carrito': 'sum'
        }).reset_index()
        
        # Calcular tasa de conversión y costo por conversión
        df_publicos['Conversion_Rate'] = (df_publicos['Artículos agregados al carrito'] / df_publicos['Clics en el enlace'] * 100).fillna(0)
        df_publicos['Cost_Per_Conversion'] = (df_publicos['Importe gastado (CLP)'] / df_publicos['Artículos agregados al carrito']).replace([float('inf')], 0).fillna(0)
        
        fig_publicos = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Gasto Total', 'CTR Promedio', 'CPC Promedio', 
                          'Tasa de Conversión (%)', 'Costo por Conversión', 'Conversiones'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig_publicos.add_trace(
            go.Bar(x=df_publicos['Público'], y=df_publicos['Importe gastado (CLP)'], 
                  name='Gasto', marker_color='#1f77b4'),
            row=1, col=1
        )
        
        fig_publicos.add_trace(
            go.Bar(x=df_publicos['Público'], y=df_publicos['CTR (todos)'], 
                  name='CTR', marker_color='#ff7f0e'),
            row=1, col=2
        )
        
        fig_publicos.add_trace(
            go.Bar(x=df_publicos['Público'], y=df_publicos['CPC (todos)'], 
                  name='CPC', marker_color='#2ca02c'),
            row=1, col=3
        )
        
        fig_publicos.add_trace(
            go.Bar(x=df_publicos['Público'], y=df_publicos['Conversion_Rate'], 
                  name='Conv Rate', marker_color='#d62728'),
            row=2, col=1
        )
        
        fig_publicos.add_trace(
            go.Bar(x=df_publicos['Público'], y=df_publicos['Cost_Per_Conversion'], 
                  name='Cost/Conv', marker_color='#9467bd'),
            row=2, col=2
        )
        
        fig_publicos.add_trace(
            go.Bar(x=df_publicos['Público'], y=df_publicos['Artículos agregados al carrito'], 
                  name='Conversiones', marker_color='#8c564b'),
            row=2, col=3
        )
        
        fig_publicos.update_layout(height=600, title_text="Análisis por Público (archivo principal)", showlegend=False)
        
        # 5. Gráfico por tipos de anuncios (usando datos principales)
        df_tipos = df_filtrado_principal.groupby('Tipo_Anuncio').agg({
            'Importe gastado (CLP)': 'sum',
            'CTR (todos)': 'mean',
            'CPC (todos)': 'mean',
            'Impresiones': 'sum',
            'Clics en el enlace': 'sum',
            'Artículos agregados al carrito': 'sum'
        }).reset_index()
        
        # Calcular tasa de conversión y costo por conversión
        df_tipos['Conversion_Rate'] = (df_tipos['Artículos agregados al carrito'] / df_tipos['Clics en el enlace'] * 100).fillna(0)
        df_tipos['Cost_Per_Conversion'] = (df_tipos['Importe gastado (CLP)'] / df_tipos['Artículos agregados al carrito']).replace([float('inf')], 0).fillna(0)
        
        fig_tipos = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Gasto Total', 'CTR Promedio', 'CPC Promedio',
                          'Tasa de Conversión (%)', 'Costo por Conversión', 'Conversiones'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig_tipos.add_trace(
            go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Importe gastado (CLP)'], 
                  name='Gasto', marker_color='#1f77b4'),
            row=1, col=1
        )
        
        fig_tipos.add_trace(
            go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CTR (todos)'], 
                  name='CTR', marker_color='#ff7f0e'),
            row=1, col=2
        )
        
        fig_tipos.add_trace(
            go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['CPC (todos)'], 
                  name='CPC', marker_color='#2ca02c'),
            row=1, col=3
        )
        
        fig_tipos.add_trace(
            go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Conversion_Rate'], 
                  name='Conv Rate', marker_color='#d62728'),
            row=2, col=1
        )
        
        fig_tipos.add_trace(
            go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Cost_Per_Conversion'], 
                  name='Cost/Conv', marker_color='#9467bd'),
            row=2, col=2
        )
        
        fig_tipos.add_trace(
            go.Bar(x=df_tipos['Tipo_Anuncio'], y=df_tipos['Artículos agregados al carrito'], 
                  name='Conversiones', marker_color='#8c564b'),
            row=2, col=3
        )
        
        fig_tipos.update_layout(height=600, title_text="Análisis por Tipo de Anuncio (archivo principal)", showlegend=False)
        
        # 6. Gráfico de Hook Rates (usando datos principales)
        df_hook = df_filtrado_principal.groupby('Tipo_Anuncio').agg({
            'Impresiones': 'sum',
            'Reproducciones de video de 3 segundos': 'sum',
            'Reproducciones de video hasta el 25%': 'sum',
            'Reproducciones de video hasta el 50%': 'sum',
            'Reproducciones de video hasta el 75%': 'sum',
            'Reproducciones de video hasta el 100%': 'sum'
        }).reset_index()
        
        # Calcular hook rates
        df_hook['Hook_Rate_3s'] = (df_hook['Reproducciones de video de 3 segundos'] / df_hook['Impresiones']) * 100
        df_hook['Hook_Rate_25'] = (df_hook['Reproducciones de video hasta el 25%'] / df_hook['Impresiones']) * 100
        df_hook['Hook_Rate_50'] = (df_hook['Reproducciones de video hasta el 50%'] / df_hook['Impresiones']) * 100
        df_hook['Hook_Rate_75'] = (df_hook['Reproducciones de video hasta el 75%'] / df_hook['Impresiones']) * 100
        df_hook['Hook_Rate_100'] = (df_hook['Reproducciones de video hasta el 100%'] / df_hook['Impresiones']) * 100
        
        # Debug hook rates
        print("=== Hook Rates Debug (archivo principal) ===")
        print(f"Total impresiones: {df_hook['Impresiones'].sum():,}")
        print(f"Total reproducciones 3s: {df_hook['Reproducciones de video de 3 segundos'].sum():,}")
        print("Hook rates por tipo:")
        for _, row in df_hook.iterrows():
            print(f"  {row['Tipo_Anuncio']}: {row['Hook_Rate_3s']:.1f}%")
        print("========================")
        
        # Ordenar por Hook Rate 3s
        df_hook = df_hook.sort_values('Hook_Rate_3s', ascending=True)
        
        fig_hook = go.Figure()
        
        # Colores para cada hook rate
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC']
        hook_columns = ['Hook_Rate_3s', 'Hook_Rate_25', 'Hook_Rate_50', 'Hook_Rate_75', 'Hook_Rate_100']
        hook_names = ['3 segundos', '25%', '50%', '75%', '100%']
        
        for i, (col, name, color) in enumerate(zip(hook_columns, hook_names, colors)):
            fig_hook.add_trace(go.Bar(
                name=f'Hook Rate {name}',
                x=df_hook[col],
                y=df_hook['Tipo_Anuncio'],
                orientation='h',
                marker_color=color,
                text=[f'{val:.1f}%' for val in df_hook[col]],
                textposition='outside'
            ))
        
        fig_hook.update_layout(
            title='Hook Rates por Tipo de Anuncio (archivo principal)',
            xaxis_title='Hook Rate (%)',
            yaxis_title='Tipo de Anuncio',
            barmode='group',
            height=400,
            margin=dict(l=150, r=50, t=50, b=50)
        )
        
        # 7. Insights
        mejor_publico = df_publicos.loc[df_publicos['Importe gastado (CLP)'].idxmax(), 'Público'] if not df_publicos.empty else "N/A"
        mejor_tipo = df_tipos.loc[df_tipos['CTR (todos)'].idxmax(), 'Tipo_Anuncio'] if not df_tipos.empty else "N/A"
        mejor_hook = df_hook.loc[df_hook['Hook_Rate_3s'].idxmax(), 'Tipo_Anuncio'] if not df_hook.empty else "N/A"
        
        insights = html.Ul([
            html.Li(f"Público con mayor gasto: {mejor_publico} (archivo principal)"),
            html.Li(f"Tipo de anuncio con mejor CTR: {mejor_tipo} (archivo principal)"),
            html.Li(f"Mejor Hook Rate de 3s: {mejor_hook} (archivo principal)"),
            html.Li(f"Datos de regiones desde: archivo con (2) - Filtro: {publico_regiones_filter}"),
            html.Li(f"Total de conversiones: {total_conversiones}")
        ])
        
        return (
            metricas,
            fig_evolucion,
            fig_regiones,
            fig_publicos,
            fig_tipos,
            fig_hook,
            insights
        )

    print("=== DASHBOARD DE MARKETING DUAL (DOS ARCHIVOS) ===")
    print("📊 Regiones: archivo con (2)")
    print("📈 Resto: archivo sin (2)")
    print("Iniciando servidor en http://localhost:8054")

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8054) 